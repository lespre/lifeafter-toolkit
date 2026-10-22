# -*- coding: utf-8 -*-
r"""客户端补丁日志读取器（`Documents/plcoht_ag`）。

## 这是什么

客户端每次启动/热更都会把**补丁过程写成日志**，文件名固定 `plcoht_ag`（备份 `plcoht_ag.1`），
**整文件单字节 XOR 0xAA**。日志里含两类高价值信息：

1. **过程记录**：`[时间] 消息`，分隔符是 XOR 后的不可打印字节。开头一条必是
   `[ts] Patch Log Start` ⇒ 该次会话的起始时间（用于「最近几次热更分别是几号」）。
2. **完整期望清单**：一处 Python dict repr，形如
   ```
   '<包路径>': {'hash': '...', 'size': N, 'doc': M, 'fver': '20260928_163420',
                'b_hash': '...', 'fhash': '...', 'hash64': '...',
                'root': bool, 'engine': bool, 'ext_packs': [2], 'mumu_skip': bool}
   ```
   ⇒ 客户端**手里应该有的每个文件 + 各自的版本串 `fver` + 各种哈希 + 期望大小**。

## 为什么值得读

- `fver` 是**逐文件版本戳**（形如 `20260928_163420`）⇒ 能直接看出「这次热更的版本时间」，
  比逐个容器算哈希快得多。
- `doc` / `size` 是**期望大小** ⇒ 与本地文件实测大小对照 = 「这个包到底落盘没有 / 大小对不对」。
- 官方 CDN 清单只到**包级**、`plcoht_ag` 是**客户端落盘级**，两者互补。

## 坑

- 单字节 XOR 0xAA（不是 0xFA、不是 0xFF）。判据：解后开头应是 `[20xx-xx-xx ...] Patch Log Start`。
- 记录分隔符不是 `\n`，是 XOR 后的不可打印字节；**用 `\x00`/`[\r\n\x00]` 切都不完整**，
  正解是按 `\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]` 锚点正则切。
- 清单是 **Python dict repr（单引号）**，不是合法 JSON ⇒ 用 `ast.literal_eval` 逐值解析，
  不要整体当 JSON/`json.loads`。
- 清单里的 key 有单引号和转义，**当字符串扫 `'<path>': {` 更稳**，别依赖整体括号配对。

## ★★ 目录名是【逻辑名】，本地落盘带渠道后缀

日志里写 `bin/x64` / `x64-2` / `x64-3` / `x64-win7`，本地实际是
`bin/x64-a50` / `x64-a50-2` / `x64-a50-win7`（`a50` = 产品代号）。
不做这层映射会得出「缺 1244 个文件」的假结论 —— 文件其实都在。
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

#: 整个文件按单字节 XOR 该键
XOR_KEY = 0xAA
#: 日志文件名（按新→旧备份顺序）
LOG_NAMES = ("plcoht_ag", "plcoht_ag.1")
#: 记录锚点：`[YYYY-MM-DD HH:MM:SS]`
TS_RE = re.compile(r"\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]")
#: 清单条目：`'<path>': {`  —— 路径里允许单引号转义
ENTRY_RE = re.compile(r"'((?:[^'\\]|\\.){3,300})'\s*:\s*\{")


def decode_bytes(raw: bytes) -> bytes:
    """单字节 XOR 0xAA。"""
    return bytes(b ^ XOR_KEY for b in raw)


def looks_like_log(raw: bytes) -> bool:
    """解出来的开头是不是补丁日志（判据：解后前 200 字节内含 Patch Log Start）。"""
    return b"Patch Log Start" in decode_bytes(raw[:512])


def read_log(path: Path) -> str:
    """读一个日志文件 → 解 XOR → 文本（非法字节替换，不抛）。"""
    return decode_bytes(Path(path).read_bytes()).decode("utf-8", "replace")


def find_logs(client_root: Path) -> List[Path]:
    """在 <client_root>/Documents 下找补丁日志（新→旧）。"""
    doc = Path(client_root) / "Documents"
    out = []
    for n in LOG_NAMES:
        p = doc / n
        if p.is_file():
            out.append(p)
    return out


def split_records(text: str) -> List[Tuple[str, str]]:
    """按 `[时间]` 锚点切记录 → [(ts, msg)]。

    ★ 不用 '\\n' 切：日志分隔符是 XOR 后的不可打印字节，切成一行会漏。
    """
    out: List[Tuple[str, str]] = []
    marks = list(TS_RE.finditer(text))
    for i, m in enumerate(marks):
        s = m.end()
        e = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        msg = text[s:e].strip().strip("\x00").strip()
        out.append((m.group(1), msg))
    return out


def _clean_path(raw: str) -> str:
    """清单里的路径 key → 干净路径（去转义、正斜杠保留）。"""
    try:
        return ast.literal_eval("'" + raw + "'")
    except Exception:
        return raw.replace("\\\\", "\\").replace("\\'", "'")


def parse_manifest(text: str) -> Dict[str, Dict[str, Any]]:
    """抽「期望清单」：{路径: {hash/size/doc/fver/...}}。

    逐条按 `'<path>': {` 扫，用括号配对取该条目的 dict 文本，再 `ast.literal_eval`。
    单条解析失败就跳过该条（不拖垮整体）。
    """
    out: Dict[str, Dict[str, Any]] = {}
    for m in ENTRY_RE.finditer(text):
        path = _clean_path(m.group(1))
        if not path or len(path) < 3 or " " in path[:3]:
            continue
        i = m.end() - 1              # 指向 '{'
        depth, j, n = 0, i, len(text)
        while j < n:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0 or j >= n:
            continue
        body = text[i:j + 1]
        if len(body) > 4000:          # 异常长度，跳过
            continue
        try:
            val = ast.literal_eval(body)
        except Exception:
            continue
        if not isinstance(val, dict):
            continue
        meta = {k: v for k, v in val.items()
                if k in ("hash", "size", "doc", "fver", "b_hash", "fhash", "hash64",
                         "root", "engine", "ext_packs", "mumu_skip")}
        if meta:
            out[path] = meta
    return out


def family_of(path: str) -> str:
    """包路径 → 家族（用于聚合）。"""
    p = path.replace("\\", "/")
    if p.startswith("bin/"):
        return "bin/" + (p.split("/")[1] if len(p.split("/")) > 1 else "")
    if p.startswith("res/"):
        parts = p.split("/")
        return "res/" + (parts[1] if len(parts) > 1 else "")
    if p.endswith(".npk") or p.endswith(".gpk"):
        return "根级包"
    return "其他"


#: 渠道后缀：日志写逻辑名，本地落盘带它（`bin/x64-2` ↔ `bin/x64-a50-2`）
CHANNEL_SUFFIX = "a50"
_BIN_RE = re.compile(r"^bin/x64(?P<tail>(?:-\d+|-win7)?)(?P<rest>/.*)$")


def rel_variants(path: str) -> List[str]:
    """清单路径 → 本地可能的相对路径变体（多给几个，宁多不误判「缺」）。"""
    rel = path.replace("/", "\\")
    out = [rel]
    m = _BIN_RE.match(path.replace("\\", "/"))
    if m:
        tail = m.group("tail") or ""
        rest = m.group("rest").lstrip("/").replace("/", "\\")
        out.append("bin\\x64-%s%s\\%s" % (CHANNEL_SUFFIX, tail, rest))
    return out


def summarize(text: str, client_root: Optional[Path] = None,
              limit: int = 30, find: Optional[str] = None) -> Dict[str, Any]:
    """把一份日志汇总成可交付的结构。

    client_root 给了就顺带对照本地文件：存在与否 / 实测大小 vs 期望大小。
    find 给了就按关键词过滤清单（匹配路径）。
    """
    recs = split_records(text)
    starts = [ts for ts, msg in recs if "Patch Log Start" in msg]
    man = parse_manifest(text)

    # 版本串（fver）分布 —— 直接回答「这次热更的版本是什么」
    fvers: Dict[str, int] = {}
    for meta in man.values():
        fv = meta.get("fver")
        if isinstance(fv, str) and fv:
            fvers[fv] = fvers.get(fv, 0) + 1

    # 家族聚合
    fams: Dict[str, int] = {}
    for p in man:
        fams[family_of(p)] = fams.get(family_of(p), 0) + 1

    # 关键词过滤
    picked: Dict[str, Dict[str, Any]] = man
    if find:
        rx = re.compile(find, re.I)
        picked = {p: v for p, v in man.items() if rx.search(p)}

    # 本地对照（多根试探：客户端根 / 根下的 Documents / 启动器 Data 目录）
    local: List[Dict[str, Any]] = []
    if client_root:
        root = Path(client_root)
        cand_roots = [root, root / "Documents"]
        # 启动器数据目录：<launcher>/<ver>/Data
        for pat in ("*/*/Data", "*/Data"):
            for d in root.parent.glob(pat):
                if d.is_dir():
                    cand_roots.append(d)
        for p, meta in list(picked.items())[:5000]:
            rels = rel_variants(p)
            fp = None
            for r0 in cand_roots:
                for rel in rels:
                    t = r0 / rel
                    if t.is_file():
                        fp = t
                        break
                if fp is not None:
                    break
            exp = meta.get("doc") or meta.get("size")
            if fp is not None:
                act = fp.stat().st_size
                local.append({"path": p, "exists": True, "expect": exp, "actual": act,
                              "match": (exp is None or exp == act)})
            else:
                local.append({"path": p, "exists": False, "expect": exp, "actual": None,
                              "match": False})

    # 动作计数
    acts: Dict[str, int] = {}
    for _, msg in recs:
        head = msg.split(":", 1)[0].split(" ", 1)[0]
        if head and len(head) < 40:
            acts[head] = acts.get(head, 0) + 1

    out: Dict[str, Any] = {
        "kind": "patch_log",
        "records": len(recs),
        "sessions": starts,
        "session_count": len(starts),
        "manifest_entries": len(man),
        "fvers": dict(sorted(fvers.items(), key=lambda x: -x[1])[:20]),
        "families": dict(sorted(fams.items(), key=lambda x: -x[1])[:40]),
        "match_count": len(picked),
        "sample": [{"path": p, **{k: v for k, v in m.items() if k in
                                  ("fver", "doc", "size", "hash")}}
                   for p, m in list(picked.items())[:limit]],
        "action_heads": dict(sorted(acts.items(), key=lambda x: -x[1])[:20]),
    }
    if local:
        miss = [x for x in local if not x["exists"]]
        mism = [x for x in local if x["exists"] and not x["match"]]
        out["local_check"] = {
            "checked": len(local), "missing": len(miss), "size_mismatch": len(mism),
            "missing_sample": [x["path"] for x in miss[:20]],
            "mismatch_sample": [{"path": x["path"], "expect": x["expect"],
                                 "actual": x["actual"]} for x in mism[:20]],
        }
    return out


def render_md(rep: Dict[str, Any], title: str = "客户端补丁日志") -> str:
    """汇总 → md。"""
    L: List[str] = ["# %s" % title, ""]
    L.append("## 会话")
    L.append("")
    L.append("- 记录条数：%d" % rep.get("records", 0))
    L.append("- 补丁会话（%d 次）：%s" % (rep.get("session_count", 0),
                                   " · ".join(rep.get("sessions", [])) or "—"))
    L.append("")
    fv = rep.get("fvers") or {}
    if fv:
        L.append("## 版本串（`fver`，逐文件版本戳）")
        L.append("")
        for k, v in fv.items():
            L.append("- `%s` × %d" % (k, v))
        L.append("")
    fam = rep.get("families") or {}
    if fam:
        L.append("## 期望清单家族分布（共 %d 条）" % rep.get("manifest_entries", 0))
        L.append("")
        for k, v in fam.items():
            L.append("- %s：%d" % (k, v))
        L.append("")
    lc = rep.get("local_check")
    if lc:
        L.append("## 本地对照")
        L.append("")
        L.append("- 检查 %d 条：缺失 **%d** · 大小不符 **%d**" % (
            lc["checked"], lc["missing"], lc["size_mismatch"]))
        if lc["missing_sample"]:
            L.append("- 缺失样例：%s" % ", ".join("`%s`" % x for x in lc["missing_sample"][:8]))
        if lc["mismatch_sample"]:
            L.append("- 大小不符样例：")
            for x in lc["mismatch_sample"][:8]:
                L.append("  - `%s` 期望 %s / 实测 %s" % (x["path"], x["expect"], x["actual"]))
        L.append("")
    smp = rep.get("sample") or []
    if smp:
        L.append("## 样例条目")
        L.append("")
        L.append("| 路径 | fver | doc/size |")
        L.append("|---|---|---|")
        for x in smp:
            L.append("| `%s` | %s | %s |" % (x["path"], x.get("fver") or "—",
                                             x.get("doc") or x.get("size") or "—"))
        L.append("")
    ah = rep.get("action_heads") or {}
    if ah:
        L.append("## 记录动作词频（前 20）")
        L.append("")
        for k, v in ah.items():
            L.append("- %s：%d" % (k, v))
        L.append("")
    return "\n".join(L)


def json_dump(rep: Dict[str, Any], path: Optional[str]) -> None:
    s = json.dumps(rep, ensure_ascii=False, indent=1)
    if not path or path == "-":
        print(s)
    else:
        Path(path).write_text(s, encoding="utf-8")
