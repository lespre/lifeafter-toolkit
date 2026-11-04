# -*- coding: utf-8 -*-
"""字段级审计：已发布板块的「名字 / 图 / 描述」覆盖率，当前 vs 历史基准。

条目数没掉但字段掉了（例如真名变内部名、图没了）也会被这块抓出来。
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BASE = "88e0a1e"


def metrics(d: dict) -> dict:
    items = d.get("items") or []
    n = len(items) or 1
    name = sum(1 for i in items if str(i.get("name") or "").strip()
               and not str(i.get("name")).startswith(("皮肤 ", "道具 ", "未识别")))
    media = sum(1 for i in items if ((i.get("_media") or {}).get("images") or []))
    desc = sum(1 for i in items if str(i.get("desc") or i.get("official_desc") or "").strip())
    return {"n": len(items), "name%": round(name / n * 100), "img%": round(media / n * 100),
            "desc%": round(desc / n * 100)}


def load_cur(bid: str):
    p = WEB / f"data/boards/{bid}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_old(bid: str):
    out = subprocess.run(["git", "show", f"{BASE}:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))["boards"]
    pub = [b for b, m in pol.items() if (m or {}).get("publication_status") == "published"]
    print(f"{'板块':32s} {'条':>7} {'名%':>5} {'图%':>5} {'述%':>5}   (基准 → 当前)")
    for bid in sorted(pub):
        cur, old = load_cur(bid), load_old(bid)
        if not cur:
            continue
        c = metrics(cur)
        if not old:
            print(f"{bid:32s} {c['n']:>7} {c['name%']:>5} {c['img%']:>5} {c['desc%']:>5}   (新板)")
            continue
        o = metrics(old)
        drop = (c["name%"] < o["name%"] - 10 or c["img%"] < o["img%"] - 15
                or c["desc%"] < o["desc%"] - 15)
        tail = f"   ({o['n']}→{c['n']} | 名{o['name%']}→{c['name%']} 图{o['img%']}→{c['img%']} 述{o['desc%']}→{c['desc%']})"
        print(f"{bid:32s} {c['n']:>7} {c['name%']:>5} {c['img%']:>5} {c['desc%']:>5}{'  ←残' if drop else ''}{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
