# -*- coding: utf-8 -*-
"""用工具库的 npk_reader 读**大容器**（res.npk / res.gpk）的目录，回答两个问题：

  1. 武器皮肤有没有"静态展示图"（找 skin 相关的 png/dds，而不是 gim）
  2. 音频在不在里面（.wem/.bnk/.ogg/.wav + 容器格式）

为什么必须走这条路：res.npk / res.gpk 不是明文 zstd 流（裸扫 zstd frame = 0），
它们是被打包/加密的 NPK 容器，只有工具库的 scan_package/unpack_entry 认得。

用法：python tools/read_large_npk.py            # res.gpk + res.npk
      python tools/read_large_npk.py res.gpk    # 只跑一个
产物：analysis/audit/large_npk_read.json
"""
from __future__ import annotations

import collections
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")))
import npk_reader as NR  # noqa: E402

OUT = ROOT / "analysis" / "audit" / "large_npk_read.json"
MRZH = Path(r"E:\mrzh")
KEYS = ("skin", "wem", "bnk", "ogg", "wav", "mp3", ".png", ".dds", ".gim", ".py", ".txt", ".json")


def txt(e) -> str:
    return json.dumps(e, ensure_ascii=False, default=str).lower()


def main() -> int:
    want = sys.argv[1:] or ["res.gpk", "res.npk"]
    doc = {"schema": "large-npk-read-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "containers": []}
    for name in want:
        p = MRZH / name
        if not p.exists():
            doc["containers"].append({"name": name, "exists": False})
            continue
        rec = {"name": name, "bytes": p.stat().st_size}
        t0 = time.time()
        try:
            meta, entries, extra = NR.scan_package(p)
            rec["meta"] = meta
            rec["entry_count"] = len(entries)
            rec["scan_seconds"] = round(time.time() - t0, 1)
            blob = " ".join(txt(e) for e in entries)
            rec["keyword_counts"] = {k: blob.count(k) for k in KEYS}
            exts = collections.Counter(re.findall(r"\.([a-z0-9]{2,6})", blob))
            rec["ext_top"] = exts.most_common(25)
            rec["skin_samples"] = [e for e in entries if "skin" in txt(e)][:20]
            rec["audio_samples"] = [e for e in entries
                                    if any(k in txt(e) for k in (".wem", ".bnk", ".ogg", ".wav", ".mp3"))][:20]
            rec["entry_samples"] = entries[:5]
            if isinstance(extra, dict):
                rec["extra_keys"] = list(extra)[:20]
        except Exception as e:  # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["scan_seconds"] = round(time.time() - t0, 1)
        doc["containers"].append(rec)
        print(json.dumps({k: v for k, v in rec.items()
                          if k in ("name", "entry_count", "scan_seconds", "keyword_counts", "ext_top", "error")},
                         ensure_ascii=False, default=str)[:1500], flush=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
