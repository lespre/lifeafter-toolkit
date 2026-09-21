# -*- coding: utf-8 -*-
"""把提取到的音频 bank 样本按**武器皮肤**归类，产出 Wiki 用的音频清单。

匹配三条路（按可靠性排序）：
  1) stem 直对：样本名含 skin_XXXX_YYY（图鉴板里每个皮肤的 model stem）
  2) 拼音对名：样本名前缀 = 皮肤中文名的拼音（水金玫瑰 → shuijinmeigui）
  3) 收进 unmatched：认不出的原样保留（**不硬凑**，交人工认）

产物：
  data/exports/skin_audio_manifest.json   （skin_id → 名字 → 音频文件清单）
  analysis/audit/skin_audio_match.json    （统计 + unmatched）

用法：python tools/aggregate_skin_audio.py [--audio-dir DIR]...
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pypinyin import lazy_pinyin

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
MANIFEST = ROOT / "data" / "exports" / "skin_audio_manifest.json"
AUDIT = ROOT / "analysis" / "audit" / "skin_audio_match.json"
DEFAULT_DIRS = [Path(r"E:\la拆包项目\03拆包产物\skin_audio_all"),
                Path(r"E:\la拆包项目\03拆包产物\gres_0058_可读版\WAV音频")]
STEM_RE = re.compile(r"skin_(\d{4})_(\d{3})")


def skins_from_board() -> list[dict]:
    if not BOARD.exists():
        return []
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    out, seen = [], set()
    for it in d.get("items", []):
        blob = json.dumps(it, ensure_ascii=False)
        stems = {"skin_%s_%s" % (a, b) for a, b in STEM_RE.findall(blob)}
        name = it.get("name") or it.get("display_name") or it.get("title") or ""
        ids = re.findall(r"1110\d{3}", blob)
        if not ids and not stems:
            continue
        key = (tuple(sorted(stems)), name, tuple(sorted(set(ids))[:1]))
        if key in seen:
            continue
        seen.add(key)
        out.append({"skin_id": (sorted(set(ids))[:1] or [""])[0], "name": name,
                    "stems": sorted(stems)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio-dir", action="append", default=[])
    a = ap.parse_args()
    dirs = [Path(x) for x in a.audio_dir] or DEFAULT_DIRS
    wavs: list[Path] = []
    for d in dirs:
        if d.exists():
            wavs += sorted(d.rglob("*.wav"))
    skins = skins_from_board()
    # 拼音表
    pys = []
    for s in skins:
        if not s["name"]:
            continue
        for variant in {''.join(lazy_pinyin(s["name"])), s["name"]}:
            if len(variant) >= 3:
                pys.append((variant.lower(), s))
    by_skin: dict[str, dict] = {}
    unmatched: list[str] = []
    for w in wavs:
        stem = w.stem
        hit = None
        low = stem.lower()
        m = STEM_RE.search(low)
        if m:
            key = f"skin_{m.group(1)}_{m.group(2)}"
            hit = next((s for s in skins if key in s["stems"]), None)
        if hit is None:
            for pv, s in sorted(pys, key=lambda t: -len(t[0])):
                if low.startswith(pv):
                    hit = s
                    break
        ukey = (hit or {}).get("skin_id") or ("?" + stem.split("_")[0].lower())
        bucket = by_skin.setdefault(ukey, {
            "skin_id": (hit or {}).get("skin_id", ""), "name": (hit or {}).get("name", ""),
            "stems": (hit or {}).get("stems", []), "files": []})
        bucket["files"].append({"sample": stem, "file": str(w), "pack": w.parent.parent.name})
        bucket.setdefault("matched", hit is not None)
        if hit is None:
            unmatched.append(stem)
    doc = {"schema": "skin-audio-manifest-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "audio_dirs": [str(d) for d in dirs], "wav_total": len(wavs),
           "skins_with_audio": sum(1 for v in by_skin.values() if v.get("matched")),
           "unmatched_samples": len(unmatched),
           "skins": sorted([v for k, v in by_skin.items() if v.get("matched")],
                           key=lambda x: -len(x["files"])),
           "unknown": sorted([v for v in by_skin.values() if not v.get("matched")],
                             key=lambda x: -len(x["files"]))}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    AUDIT.write_text(json.dumps({"wav_total": len(wavs), "matched_skins": doc["skins_with_audio"],
                                 "unmatched": unmatched[:400]}, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(json.dumps({"wav_total": len(wavs), "matched_skins": doc["skins_with_audio"],
                      "unmatched": len(unmatched)}, ensure_ascii=False))
    for s in doc["skins"][:12]:
        print(f'  {s["skin_id"]:>8} {s["name"]:<10} {len(s["files"]):>3} 个  例: {s["files"][0]["sample"]}')
    if doc["unknown"]:
        print("  未归属（前 10）:", [f["files"][0]["sample"] for f in doc["unknown"][:10]])
    print("→", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
