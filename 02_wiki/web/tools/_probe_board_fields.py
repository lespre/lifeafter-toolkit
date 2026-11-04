# -*- coding: utf-8 -*-
"""抽查 kill_broadcast / upcoming_auto 的图与描述字段，定位是哪个字段丢了。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")


def cur(bid):
    return json.loads((WEB / f"data/boards/{bid}.json").read_text(encoding="utf-8"))


def old(bid, ref="88e0a1e"):
    out = subprocess.run(["git", "show", f"{ref}:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out) if out else None


def main() -> int:
    for bid in ("kill_broadcast", "upcoming_auto"):
        c, o = cur(bid), old(bid)
        print("==", bid, "当前", len(c["items"]))
        if c["items"]:
            print("  当前 keys", [k for k in c["items"][0]][:18])
            print("  当前样例", {k: str(c["items"][0].get(k))[:40]
                              for k in ("id", "name", "icon", "_media", "desc")})
        if o:
            print("  基准 keys", [k for k in o["items"][0]][:18])
            print("  基准样例", {k: str(o["items"][0].get(k))[:40]
                              for k in ("id", "name", "icon", "_media", "desc")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
