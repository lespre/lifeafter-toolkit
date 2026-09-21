# -*- coding: utf-8 -*-
"""定位并提取**武器皮肤音频**：在 gpk/npk 里裸搜 FSB5 bank + 皮肤音效名。

原理（前人已验证）：
  · 游戏音频是 FSB5（FMOD）bank，样本名写在 bank 头里（未压缩）
  · 已提取成果：gres_0058 → 000049.fsb → 24 个武器音（wepon_hexin_* / ice_weapon_* …）
  · 管线：lifeafter_unpacker_full.extract_fsb(bank, outdir) → FSB5→WAV（名字取自 bank）

本工具做两件事：
  1) 扫 gpk/npk 原始字节：找 b"FSB5" 魔数 + 皮肤音效关键词（fx_skin_/wepon_/skin_）
     —— 只做字节级定位，不解压，快
  2) 对命中处，向前找最近的 FSB5 头，用 fsb5 解析尺寸并落盘成 <pack>_<offset>.fsb

产物：03拆包产物/skin_audio_banks/*.fsb + analysis/audit/skin_audio_banks.json
用法：python tools/find_skin_audio_banks.py [--packs N] [--extract]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = Path(r"E:\la拆包项目\03拆包产物\skin_audio_banks")
OUT = ROOT / "analysis" / "audit" / "skin_audio_banks.json"
MRZH = Path(r"E:\mrzh")
PACKS = [MRZH / "res.gpk", MRZH / "res.npk"] + sorted((MRZH / "Documents" / "gres").glob("*.gpk"))
FSB5 = b"FSB5"
PATTERNS = [b"fx_skin_", b"wepon_hexin_", b"wepon_", b"ice_weapon_", b"rifle_ice_", b"skin_100", b"skin_200", b"skin_101", b"skin_102"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", type=int, default=0)
    ap.add_argument("--extract", action="store_true")
    a = ap.parse_args()
    packs = PACKS[: a.packs] if a.packs else PACKS
    OUTDIR.mkdir(parents=True, exist_ok=True)
    doc = {"schema": "skin-audio-banks-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "packs": [], "banks": []}
    for pk in packs:
        if not pk.exists():
            continue
        data = pk.read_bytes()
        rec = {"pack": pk.name, "bytes": len(data), "fsb5_heads": data.count(FSB5), "name_hits": {}}
        hit_offsets: list[int] = []
        for pat in PATTERNS:
            n = data.count(pat)
            if n:
                rec["name_hits"][pat.decode()] = n
            pos = 0
            while len(hit_offsets) < 40:
                j = data.find(pat, pos)
                if j < 0:
                    break
                pos = j + 1
                # 向前找最近的 FSB5 头（bank 头在名字之前）
                k = data.rfind(FSB5, max(0, j - 4_000_000), j)
                if k >= 0:
                    hit_offsets.append(k)
        rec["bank_offsets"] = sorted(set(hit_offsets))
        if a.extract:
            for k in rec["bank_offsets"]:
                blob = data[k:k + 8 * 1024 * 1024]
                try:
                    import fsb5
                    fsb = fsb5.FSB5(blob)
                    names = [s.name for s in fsb.samples][:40]
                    size = getattr(fsb, "size", None)
                except Exception as e:  # noqa: BLE001
                    names, size = [], f"parse-fail:{type(e).__name__}"
                fn = OUTDIR / f"{pk.stem}_{k:012d}.fsb"
                fn.write_bytes(blob)
                doc["banks"].append({"pack": pk.name, "offset": k, "file": fn.name,
                                     "sample_count": len(names) if isinstance(names, list) else 0,
                                     "names": names, "size": size})
        doc["packs"].append(rec)
        print(f"  {pk.name}: FSB5头={rec['fsb5_heads']} 名字命中={rec['name_hits']} 候选bank={len(rec['bank_offsets'])}", flush=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
