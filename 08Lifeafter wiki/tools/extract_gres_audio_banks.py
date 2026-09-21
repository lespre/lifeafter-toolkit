# -*- coding: utf-8 -*-
"""扫全部 gres 包，抽出其中的 FSB5 音频 bank → WAV（样本名取自 bank）。

做法（复用已复现的路径，不再自己切条目）：
  1. lifeafter_unpacker_full.extract_gpk(pack, tmpdir)  —— 完整解包（先例：gres_0058 → 000046.fsb …）
  2. 只保留 *.fsb，其余（dds/bin/c159）立即删除（省盘）
  3. 对每个 bank：fsb5 解析样本名 + extract_fsb → WAV
  4. 汇总到 analysis/audit/gres_audio_banks.json，并单独标出**武器/皮肤相关**样本名

用法：python tools/extract_gres_audio_banks.py [--packs N]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")))
import lifeafter_unpacker_full as m  # noqa: E402

DEST = Path(r"E:\la拆包项目\03拆包产物\skin_audio_all")
OUT = ROOT / "analysis" / "audit" / "gres_audio_banks.json"
GRES = Path(r"E:\mrzh\Documents\gres")
KEYS = ("skin", "weapon", "wepon", "wuqi", "hexin", "gunshot", "qiang", "dao", "jiguan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=int, default=0)
    ap.add_argument("--only", default="", help="只跑这些包名，逗号分隔，如 0058,0059")
    a = ap.parse_args()
    packs = sorted(GRES.glob("*.gpk"))
    if a.packs:
        packs = packs[: a.packs]
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        packs = [p for p in packs if p.stem in want]
    doc = {"schema": "gres-audio-banks-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "packs": [], "weapon_related": []}
    for pk in packs:
        pd = DEST / pk.stem
        pd.mkdir(parents=True, exist_ok=True)
        rec = {"pack": pk.name, "fsb5": 0, "banks": [], }
        tmp = Path(tempfile.mkdtemp(prefix=f"gpk_{pk.stem}_"))
        try:
            m.extract_gpk(str(pk), str(tmp))
        except Exception as e:  # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"
        fsbs = sorted(tmp.glob("*.fsb"))
        for f in fsbs:
            tgt = pd / f.name
            try:
                shutil.move(str(f), str(tgt))
            except Exception:
                pass
            names = []
            try:
                import fsb5
                names = [s.name for s in fsb5.FSB5(tgt.read_bytes()).samples]
            except Exception as e2:  # noqa: BLE001
                names = [f"<parse-fail {type(e2).__name__}>"]
            rec["fsb5"] += 1
            rec["banks"].append({"file": tgt.name, "bytes": tgt.stat().st_size if tgt.exists() else 0,
                                 "samples": len(names), "names": names[:100]})
            if names and not names[0].startswith("<parse-fail"):
                try:
                    m.extract_fsb(str(tgt), str(pd / "WAV"))
                except Exception:
                    pass
            for n in names:
                if any(k in n.lower() for k in KEYS):
                    doc["weapon_related"].append({"pack": pk.name, "bank": tgt.name, "sample": n})
        shutil.rmtree(tmp, ignore_errors=True)
        doc["packs"].append(rec)
        print(f"  {pk.name}: bank {rec['fsb5']} | 武器相关样本 {sum(1 for x in doc['weapon_related'] if x['pack']==pk.name)}",
              flush=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("武器相关样本总数:", len(doc["weapon_related"]))
    for x in doc["weapon_related"][:25]:
        print("   ", x["pack"], x["sample"])
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
