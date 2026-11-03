#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""板块重建能力 + 依赖表汇总（给人工逐条审阅）。

数据来源：
  · 02_wiki/web/data/boards/*.json        板块条目数
  · 02_wiki/web/data/board_builders.json  builder 注册（28 条，带 inputs）
  · 02_wiki/rules/boards/*.yml            每板规则（source_server / primary_builders）
  · builder 脚本正文                       扫描 cdata 表名

产物：01_索引与产物/30_分析/板块重建能力汇总.md
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
import functools


@functools.lru_cache(maxsize=None)
def find_script(name: str) -> str | None:
    """builder 可能不在 tools/ 下（如 02_图文音频渲染）。全项目按名找一次。"""
    for root in (PROJ / "02_wiki", PROJ / "00_规范与工具"):
        for p in root.rglob(name):
            return str(p.relative_to(PROJ)).replace("\\", "/")
    return None
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
TOOLS = WEB / "tools"
RULES = PROJ / "02_wiki/rules/boards"
OUT = PROJ / "01_索引与产物/30_分析/板块重建能力汇总.md"

TABLE_RE = re.compile(r"\b([a-z][a-z0-9_]{3,60}_(?:data|conf|db|list|pool|map|base|table))\b")


def parse_yml(path: Path) -> dict:
    out: dict = {}
    key = None
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("- "):
            if key:
                out.setdefault(key, []).append(line[2:].strip())
            continue
        if line.startswith("  - ") or line.startswith("    - "):
            if key:
                out.setdefault(key, []).append(line.split("- ", 1)[1].strip())
            continue
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                out[key] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                key = None
            else:
                out[key] = v if v else []
    return out


def main() -> int:
    reg = {}
    rp = WEB / "data/board_builders.json"
    if rp.exists():
        for b in json.loads(rp.read_text(encoding="utf-8")).get("boards") or []:
            reg[b.get("board_id")] = b

    rules = {}
    for p in RULES.glob("*.yml"):
        try:
            rules[p.stem] = parse_yml(p)
        except Exception:
            pass

    rows = []
    for p in sorted(BOARDS.glob("*.json")):
        bid = p.stem
        if bid.startswith("_"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = len(d.get("items") or [])
        meta = d.get("meta") or {}
        name = meta.get("name") or bid

        r = reg.get(bid) or {}
        builders = []
        if r.get("builder"):
            builders.append(Path(str(r["builder"])).name)
        for b in (rules.get(bid) or {}).get("primary_builders") or []:
            b = str(b).strip().strip("'\"")
            if b.endswith(".py") and b not in builders:
                builders.append(b)

        tables: set[str] = set()
        for inp in (r.get("inputs") or []):
            tables.update(TABLE_RE.findall(str(inp)))
        src = str((rules.get(bid) or {}).get("source_server") or "")
        tables.update(TABLE_RE.findall(src))
        for b in builders:
            if not b:
                continue
            bp = TOOLS / b
            if bp.is_file():
                txt = bp.read_text(encoding="utf-8", errors="ignore")
                tables.update(TABLE_RE.findall(txt))

        resolved = []
        for b in builders:
            if (TOOLS / b).is_file():
                resolved.append(f"tools/{b}")
            elif find_script(b):
                resolved.append(find_script(b))
        builders = resolved
        ok = bool(builders)
        rows.append({
            "board": bid, "name": name, "items": items,
            "rebuildable": ok, "builders": builders,
            "tables": sorted(tables), "verified": bool(r.get("verified")),
            "notes": (r.get("notes") or "")[:60],
        })

    rows.sort(key=lambda x: (not x["rebuildable"], -x["items"]))
    ok_n = sum(1 for r in rows if r["rebuildable"])

    lines = ["# 板块重建能力 · 依赖表汇总", "",
             f"- 板块总数 **{len(rows)}**，可重建 **{ok_n}**，缺 builder **{len(rows) - ok_n}**", "",
             "> 「可重建」= 能找到 builder 脚本且文件存在；表名是从 builder 正文 / 规则 yml / 注册表 inputs 里扫出来的，",
             "> 可能与真实读取略有出入，审阅时以脚本为准。", ""]

    for title, group in (("## 一、可重建", [r for r in rows if r["rebuildable"]]),
                         ("## 二、缺 builder（无法自动重建）", [r for r in rows if not r["rebuildable"]])):
        lines += [title, ""]
        lines += ["| 板块 | 名称 | 条目 | builder | 依赖表 | 已验证 |", "|---|---|---:|---|---|---|"]
        for r in group:
            tb = "<br>".join(f"`{t}`" for t in r["tables"][:6]) or "—"
            bs = "<br>".join(r["builders"][:2]) or "—"
            lines.append(f"| `{r['board']}` | {r['name']} | {r['items']:,} | {bs} | {tb} | "
                         f"{'✓' if r['verified'] else ''} |")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"板块 {len(rows)} | 可重建 {ok_n} | 缺 {len(rows)-ok_n}")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
