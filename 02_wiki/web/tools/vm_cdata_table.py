# -*- coding: utf-8 -*-
"""mini-VM：执行 com\\cdata 变体表 .py 的模块字节码，直接拿到它构造的字典。

用法：python vm_cdata_table.py <file.py> [--dump out.json] [--rows N]
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")))
from toolkit_core import script_decode as SD  # noqa: E402


class TDict(dict):
    """TD(...) 构造出来的表行；只保留键值对语义。"""


def unwrap(v):
    if isinstance(v, SD.Value):
        v = v.v
    if isinstance(v, (list, tuple)):
        return type(v)(unwrap(x) for x in v)
    return v


def call_td(args):
    out = TDict()
    i = 0
    while i + 1 < len(args):
        k = args[i]
        v = args[i + 1]
        if isinstance(k, str):
            out[k] = v
        i += 2
    return out


def run(code, verbose: bool = False):
    ins = code.dis_resolved()
    consts = [unwrap(c) for c in code.consts]
    names = [unwrap(n) for n in code.names]
    st: list = []
    g: dict = {"TD": call_td}
    skipped: dict[str, int] = {}

    def pop(n=1):
        out = st[-n:]
        del st[-n:]
        return out if n > 1 else out[0]

    for item in ins:
        i = item[0]
        name, arg = i.name, i.arg
        if name in ("RESUME", "NOP", "NOT_TAKEN", "POP_TOP"):
            continue
        if name == "LOAD_CONST":
            st.append(consts[arg] if arg < len(consts) else None)
        elif name == "LOAD_SMALL_INT":
            st.append(arg)
        elif name == "LOAD_NAME" or name == "LOAD_GLOBAL":
            st.append(g.get(names[arg], names[arg]) if arg < len(names) else None)
        elif name == "PUSH_NULL":
            st.append(None)
        elif name == "BUILD_MAP":
            pairs = pop(2 * arg) if arg else []
            d = TDict()
            for j in range(0, len(pairs), 2):
                k, v = pairs[j], pairs[j + 1]
                if isinstance(k, str):
                    d[k] = v
            st.append(d)
        elif name == "BUILD_TUPLE" or name == "BUILD_LIST":
            vals = pop(arg) if arg else []
            st.append(tuple(vals) if name == "BUILD_TUPLE" else list(vals))
        elif name == "BUILD_SET":
            vals = pop(arg) if arg else []
            st.append(set(vals))
        elif name == "LIST_EXTEND" or name == "DICT_UPDATE" or name == "SET_ADD" or name == "LIST_APPEND":
            v = pop()
            if st and isinstance(st[-1], list):
                st[-1].extend(v if isinstance(v, (list, tuple)) else [v])
            elif st and isinstance(st[-1], dict) and isinstance(v, dict):
                st[-1].update(v)
        elif name == "BINARY_OP":
            b = pop()
            a = pop()
            if arg == 26:                      # NB_SUBSCR
                try:
                    st.append(a[b])
                except Exception as e:
                    print("  [subscr 失败] off=%d a=%r len=%s b=%r %s"
                          % (i.off, type(a).__name__, (len(a) if hasattr(a, "__len__") else "-"), b, e))
                    st.append(None)
            elif arg == 0:
                st.append(a + b)
            else:
                skipped["BINARY_OP%d" % arg] = skipped.get("BINARY_OP%d" % arg, 0) + 1
                st.append(None)
        elif name == "CALL" or name == "CALL_KW":
            a = pop(arg) if arg else []
            fn = pop()
            if st and st[-1] is None:          # 吃掉 PUSH_NULL 占位
                st.pop()
            if callable(fn):
                st.append(fn(list(a) if isinstance(a, list) else [a]))
            elif isinstance(fn, type):
                st.append(fn())
            else:
                st.append(TDict())
        elif name == "STORE_NAME":
            if arg < len(names):
                g[names[arg]] = pop()
        elif name == "STORE_SUBSCR":
            key, obj, val = pop(), pop(), pop()
            try:
                obj[key] = val
            except Exception:                  # noqa: BLE001
                pass
        elif name == "STORE_FAST" or name == "STORE_GLOBAL":
            pop()
        elif name in ("IMPORT_NAME", "IMPORT_FROM"):
            st.append(None)
        elif i.op == 0x57:                     # MAP_ADD(depth)：value,key → 第 depth 层字典
            val = pop()
            key = pop()
            depth = arg if arg else 1
            if not hasattr(run, "_dbg"):
                run._dbg = 0
            if run._dbg < 3:
                run._dbg += 1
                print("  [MAP_ADD] depth=%d key=%r target=%s stacktop=%s"
                      % (depth, key, type(st[len(st)-depth]).__name__ if st else "empty",
                         [type(x).__name__ for x in st[-3:]]))
            try:
                tgt = st[len(st) - depth]
                if isinstance(tgt, dict):
                    tgt[key] = val
                else:
                    st.append(None)
            except Exception:                  # noqa: BLE001
                st.append(None)
        elif name == "COPY":
            st.append(st[-arg])
        elif name == "SWAP":
            st[-1], st[-arg] = st[-arg], st[-1]
        elif name == "BUILD_STRING":
            vals = pop(arg) if arg else []
            st.append("".join(str(x) for x in vals))
        else:
            skipped[name] = skipped.get(name, 0) + 1
            if verbose:
                print("   未处理指令", name, arg, "@", i.off)
    return g, skipped


def main(argv: list[str]) -> int:
    p = argv[0]
    r, code, end = SD.load_module(p)
    if code is None:
        print("解析失败")
        return 1
    g, skipped = run(code)
    data = g.get("data")
    print("解析终点 %d ｜ 全局变量 %s" % (end, list(g)))
    print("未处理指令", dict(sorted(skipped.items(), key=lambda x: -x[1])[:6]))
    if isinstance(data, dict):
        print("data 条目 %d" % len(data))
        k0 = next(iter(data), None)
        print("首条 key=%r" % (k0,))
        print("首条内容", json.dumps(data[k0], ensure_ascii=False, default=str)[:400])
        out = pathlib.Path(argv[argv.index("--dump") + 1]) if "--dump" in argv else None
        if out:
            out.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
            print("写出", out)
    else:
        print("data 类型", type(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
