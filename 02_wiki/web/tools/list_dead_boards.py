# -*- coding: utf-8 -*-
"""列出已发布但没有 board 文件的死链。"""
import json
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))["boards"]
    dead = [b for b, m in pol.items()
            if (m or {}).get("publication_status") == "published"
            and not (WEB / f"data/boards/{b}.json").is_file()]
    print("已发布但无文件", len(dead), dead)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
