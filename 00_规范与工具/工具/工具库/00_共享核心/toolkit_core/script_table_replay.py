# -*- coding: utf-8 -*-
r"""script_table_replay.py — 重放 NeoX 模块字节码，还原 cdata 表。

═══════════════════════════════════════════════════════════════════════════
★ 为什么需要它

   2026-10-30 热更后，`com/cdata/*.py` 改了一种打包方式：

     旧：文件 = [0x73 头][bindict 二进制表体]      → bindict_table / bindict_73 直接解
     新：文件 = [0x73 头][ NeoX 字节码 co_code ][ 常量池 ]
          表不再以二进制表体存放，而是**由模块字节码逐行构造**：
              data = { 3637: TD(name=…, hd_class=…, start_ts=…), … }
          即 `TD(...)` 构造行、dict 字面量收行、最后 STORE_NAME。

   所以「解表」变成「重放字节码」。本模块就是一个迷你栈机。

═══════════════════════════════════════════════════════════════════════════
★ 前置：0x75 大常量表

   新格式的 co_consts 常有 9000+ 项，超过 0x2e（u8 计数）上限，
   改用 `75 + u32 count`。script_decode.NeoXReader 已支持（2026-10-30 补），
   缺它则 2 万张变体表一律卡在「未知 marshal 标签 0x75」。

═══════════════════════════════════════════════════════════════════════════
★ 实测布局（huodong_conf_data.py，1,120,063 B，逐字节对上）

   0x00  73 + 5×u32                        code 头（argcount…flags）
   0x15  fb + u32(373976) + co_code        字节码
        75 + u32(9768) + consts            大常量表（本模块依赖）
        后续 names / filename / name / linetable …
   常量池：str(字段名/类名/中文活动名) 3957 + tag3e 4343 + float 983 + tuple 350 + uint 132

   行构造（每行同一模式，实测 3,055 行）：
        LOAD_SMALL_INT <key>       ← 行主键
        LOAD_NAME <构造函数 TD>
        PUSH_NULL
        LOAD_CONST <字段名> / <值> × 2n
        BUILD_MAP n                ← 折叠成 kwargs
        CALL 1                     ← 构造行对象（本模块按「kwargs 即行内容」处理）
        0x57 MAP_ADD               ← 收进当前 dict 字面量

   ★ 一个模块里有多段 dict 字面量（实测 888 段），段间用 DICT_UPDATE 合并。
     本模块不去猜合并链，而是**收集所有被写过的容器再合并** —— 段内 key 不冲突时
     等价，且不依赖 0x57/DICT_UPDATE 的精确栈语义（那两个语义仍有争议，见下）。

═══════════════════════════════════════════════════════════════════════════
★ 不敢说死的地方（如实列出）

   1) 0x57 的精确语义未定论：按 MAP_ADD（dict 留栈）与按 STORE_SUBSCR（全弹）
      会导致栈深度不同。本模块两者都能跑（容器用「栈上第三个」定位），
      合并结果一致，所以不阻塞；但 DICT_UPDATE 时栈不足会记 warning。
   2) BINARY_OP 只实现了「下标 / 数值加 / 字符串拼」三种（arg=26 实测是下标
      `t2[135]` 这类取值）。未覆盖的运算会退化成 ('<binop>', lhs, rhs) 占位，
      **不伪造值**。
   3) CALL 的结果按「kwargs dict」近似 —— 若构造函数真的做类型转换/校验，
      这里拿到的是入参而非最终对象。本表够用，别的表要另行验证。

用法：
    from toolkit_core.script_table_replay import replay_module
    rows, meta = replay_module("…/huodong_conf_data.py")

    CLI: python script_table_replay.py <表.py> [-o out.json] [--all-keys]
"""
from __future__ import annotations

import json
import struct
from collections import Counter
from pathlib import Path

from toolkit_core import script_decode as SD

__all__ = ["replay_module", "ReplayError"]

MAP_ADD = 0x57


class ReplayError(ValueError):
    """无法重放（不是 NeoX 模块 / 解析失败）。"""


def _consts_of(code) -> list:
    out = []
    for v in code.consts:
        out.append(v.v)
    return out


def _names_of(code) -> list:
    return [v.v for v in (code.names or [])]


def replay_module(src, *, int_keys_only: bool = True):
    """重放模块字节码 → (rows, meta)。

    rows : {key: {字段: 值}}（int_keys_only=True 时只保留整数主键）
    meta : 自检信息（容器数 / 写入次数 / 过滤 / 未知 op / warning）
    """
    if isinstance(src, (bytes, bytearray)):
        buf = bytes(src)
        path = None
    else:
        path = Path(src)
        buf = path.read_bytes()

    reader, top, end = SD.load_module(path) if path else (None, None, 0)
    if top is None:
        # bytes 输入：直接用 NeoXReader
        r = SD.NeoXReader(buf)
        r.z7a = "marker"
        try:
            top, end = r.read_top()
        except SD.NeoxDecodeError as exc:
            raise ReplayError("解析失败：%s" % exc) from exc
        reader = r

    consts = _consts_of(top)
    names = _names_of(top)
    ins = SD.dis_code(top.co_code)

    stack: list = []
    env: dict = {}
    unknown: Counter = Counter()
    warn: list = []
    containers: dict[int, dict] = {}
    order: list[int] = []
    n_write = 0

    def flat(v):
        return v.v if isinstance(v, SD.Value) else v

    for x in ins:
        op, a, nm = x.op, x.arg, x.name
        if nm == "LOAD_CONST":
            stack.append(flat(consts[a]) if 0 <= a < len(consts) else "<const?%d>" % a)
        elif nm == "LOAD_SMALL_INT":
            stack.append(a)
        elif nm == "LOAD_NAME":
            stack.append(flat(names[a]) if 0 <= a < len(names) else "<name?%d>" % a)
        elif nm == "PUSH_NULL":
            stack.append(None)
        elif nm == "BUILD_MAP":
            items = stack[-2 * a:] if a else []
            del stack[-2 * a:]
            d = {}
            for k in range(a):
                if 2 * k + 1 >= len(items):
                    warn.append("BUILD_MAP 项数不足 @%d" % x.off)
                    break
                kk = flat(items[2 * k])
                vv = flat(items[2 * k + 1])
                d[kk if isinstance(kk, (str, int, float, bool)) else repr(kk)] = vv
            stack.append(d)
        elif nm == "BUILD_TUPLE":
            items = stack[-a:] if a else []
            del stack[-a:]
            stack.append(tuple(items))
        elif nm == "CALL":
            args = stack[-a:] if a else []
            del stack[-a:]
            fn = None
            while stack:
                t = stack.pop()
                if t is None:
                    continue
                fn = t
                break
            kw = args[-1] if args and isinstance(args[-1], dict) else {}
            stack.append(dict(kw) if isinstance(kw, dict) else {})
        elif op == MAP_ADD:
            if len(stack) < 3:
                warn.append("MAP_ADD 栈不足 @%d" % x.off)
                continue
            val, key, cont = stack[-1], stack[-2], stack[-3]
            if isinstance(cont, dict):
                cid = id(cont)
                if cid not in containers:
                    containers[cid] = cont
                    order.append(cid)
                cont[key] = val
                n_write += 1
                del stack[-2:]
            else:
                warn.append("MAP_ADD 容器非 dict @%d（%s）" % (x.off, type(cont).__name__))
                del stack[-2:]
        elif nm == "DICT_UPDATE":
            if len(stack) < 2:
                warn.append("DICT_UPDATE 栈不足 @%d" % x.off)
                continue
            upd = stack.pop()
            base = stack[-1]
            if isinstance(base, dict) and isinstance(upd, dict):
                base.update(upd)
            else:
                warn.append("DICT_UPDATE 类型不符 @%d" % x.off)
        elif nm == "BINARY_OP":
            if len(stack) < 2:
                warn.append("BINARY_OP 栈不足 @%d" % x.off)
                continue
            rhs, lhs = stack.pop(), stack.pop()
            if isinstance(rhs, int) and isinstance(lhs, (list, tuple, str)):
                try:
                    stack.append(lhs[rhs])
                except Exception:
                    stack.append(("<subscr>", lhs, rhs))
            elif isinstance(lhs, list) and isinstance(rhs, list):
                stack.append(lhs + rhs)
            elif isinstance(lhs, (int, float)) and isinstance(rhs, (int, float)):
                stack.append(lhs + rhs)
            elif isinstance(lhs, str) and isinstance(rhs, str):
                stack.append(lhs + rhs)
            else:
                stack.append(("<binop%d>" % a, lhs, rhs))
        elif nm == "STORE_NAME":
            env[flat(names[a]) if 0 <= a < len(names) else a] = stack.pop() if stack else None
        elif nm == "LOAD_ATTR":
            if stack:
                stack.append(("<attr>", stack.pop(), a))
        elif nm == "SWAP":
            if len(stack) >= 2 and a == 2:
                stack[-1], stack[-2] = stack[-2], stack[-1]
        elif nm == "POP_TOP":
            if stack:
                stack.pop()
        elif nm in ("IMPORT_NAME", "IMPORT_FROM"):
            stack.append(("IMPORT", a))
        elif nm in ("NOP", "RESUME", "RETURN_VALUE", "DELETE_NAME", "RERAISE",
                    "POP_EXCEPT", "PUSH_EXC_INFO", "CHECK_EXC_MATCH",
                    "POP_JUMP_IF_FALSE", "NOT_TAKEN", "COPY"):
            pass
        else:
            unknown[(op, nm)] += 1

    rows: dict = {}
    for cid in order:
        rows.update(containers[cid])
    n_all = len(rows)
    if int_keys_only:
        rows = {k: v for k, v in rows.items() if isinstance(k, int)}
        rows = dict(sorted(rows.items()))

    meta = {
        "table": (SD.CodeObj._lit(top.filename) or (path.name if path else "")),
        "file_len": len(buf),
        "parse_end": end,
        "parse_complete": end == len(buf),
        "consts": len(consts),
        "names": len(names),
        "instructions": len(ins),
        "containers": len(order),
        "map_add_writes": n_write,
        "rows_all": n_all,
        "rows": len(rows),
        "dropped_non_int_keys": n_all - len(rows),
        "unknown_ops": {"%s(0x%02x)" % (n, o): c for (o, n), c in unknown.most_common(10)},
        "warnings": len(warn),
        "warning_samples": warn[:5],
        "module_vars": sorted(str(k) for k in env),
    }
    return rows, meta


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="重放 NeoX 模块字节码还原 cdata 表")
    ap.add_argument("table")
    ap.add_argument("-o", "--out")
    ap.add_argument("--all-keys", action="store_true", help="不过滤非整数主键")
    a = ap.parse_args()

    rows, meta = replay_module(a.table, int_keys_only=not a.all_keys)
    print("表 %s ｜ 行 %d ｜ 解析 %s" % (
        meta["table"], meta["rows"], "完整" if meta["parse_complete"] else "不完整"))
    print("  常量 %d ｜ 指令 %d ｜ 字面量段 %d ｜ 写入 %d ｜ warning %d"
          % (meta["consts"], meta["instructions"], meta["containers"],
             meta["map_add_writes"], meta["warnings"]))
    if meta["unknown_ops"]:
        print("  未知 op:", meta["unknown_ops"])
    if a.out:
        Path(a.out).write_text(
            json.dumps({"meta": meta, "rows": {str(k): v for k, v in rows.items()}},
                       ensure_ascii=False, indent=1, default=str),
            encoding="utf-8")
        print("  → %s" % a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
