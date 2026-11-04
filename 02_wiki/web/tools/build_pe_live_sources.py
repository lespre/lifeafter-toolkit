#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 PE 源的 live_sources 注册表（替代指向 PC E:\\mrzh 的那份）。

只登记 PE 客户端脚本包（从雷电拉下来的那份），SHA/字节数/mtime 现场算，
供 gift_data_text_sources / weapon_skin_sfx_text_sources 这类「按 fid 读包」的 builder 用。
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
NPK = PROJ / "90_临时/pe_client/Documents/script.py314.lc.npk"
OUT = PROJ / "02_wiki/web/data/live_sources_pe.json"


def main() -> int:
    data = NPK.read_bytes()
    st = NPK.stat()
    entry = {
        "source_id": "documents-py314-current",
        "path": str(NPK),
        "server_branch": "playertest",
        "expected_sha256": hashlib.sha256(data).hexdigest(),
        "expected_bytes": len(data),
        "expected_mtime_ns": st.st_mtime_ns,
        "note": "PE 体验服客户端脚本包（雷电 /sdcard/Android/data/com.netease.mrzh/files/netease/g66/Documents）",
    }
    doc = {
        "schema_version": 2,
        "generated": time.strftime("%Y-%m-%d"),
        "scope": "PE 体验服（只用 PE 源；不再引用 E:/mrzh）",
        "sources": [entry],
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT.name, "| sha", entry["expected_sha256"][:12], "| bytes", entry["expected_bytes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
