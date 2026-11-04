# -*- coding: utf-8 -*-
"""全量扫 PE 所有 gpk 包，捞出「称号动画 csb」（载荷含 chenghao/<家族>/ 贴图引用）。

判定：载荷前 16B == Cocos 场景签名，且载荷内出现 'chenghao/' 路径。
输出：01_索引与产物/30_分析/title_csb_pe/gpk_all/*.csb + index.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
SIG = bytes.fromhex("1400000010001c00040008000c001000")
STATE = OUT / "_progress.json"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    done = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    packs = sorted(PACKS.glob("*.gpk"))
    index_path = OUT / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else []
    t0 = time.time()
    for p in packs:
        if done.get(p.name):
            continue
        n_csb = n_title = 0
        try:
            for e in AG.iter_entries(str(p)):
                d = e.get("payload")
                if not d or len(d) < 200 or d[:16] != SIG:
                    continue
                n_csb += 1
                head = d[:80000]
                if b"chenghao/" not in head:
                    continue
                n_title += 1
                fn = OUT / f"{p.stem}_{e.get('row')}.csb"
                fn.write_bytes(d)
                index.append({"pack": p.name, "row": e.get("row"), "bytes": len(d), "file": fn.name})
        except Exception as exc:  # noqa: BLE001
            print("失败", p.name, type(exc).__name__, exc, flush=True)
        done[p.name] = {"csb": n_csb, "title_csb": n_title}
        STATE.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{p.name} csb={n_csb} 称号csb={n_title} 累计称号={len(index)} "
              f"用时{time.time()-t0:.0f}s", flush=True)
    print("完成：称号 csb", len(index), "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
