# -*- coding: utf-8 -*-
"""对「有 sfx 真名但没音频」的皮肤，在 FSB bank 里按样本名精确匹配，输出可提名单。"""
from __future__ import annotations

import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path("E:/la拆包项目")
ART = ROOT / "01_索引与产物/30_分析/site_artifacts/artifacts/active/weapon_skin_audio"
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
OUT = ROOT / "01_索引与产物/30_分析/weapon_skin_audio_gap_match.json"


def main() -> int:
    idx = [json.loads(l) for l in open(ART / "FSB_SAMPLE_INDEX.jsonl", encoding="utf-8")]
    name2bank: dict[str, list[str]] = defaultdict(list)
    for r in idx:
        for s in r.get("samples") or []:
            nm = (s or {}).get("name")
            if nm:
                name2bank[nm].append(r["bank"])

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    gap = [i for i in d["items"]
           if (i.get("sfx_real_names") and i.get("sfx_audio_state") != "已提取")]
    print("缺口卡 %d ｜ FSB 样本名 %d 个" % (len(gap), len(name2bank)))

    rep = {}
    for it in gap:
        names = it.get("sfx_real_names") or []
        exact = {n: name2bank[n] for n in names if n in name2bank}
        stem = {}
        for n in names:
            hits = [k for k in name2bank if n in k or k in n]
            if hits:
                stem[n] = hits[:3]
        rep[it["id"]] = {"name": it.get("name"), "grade": it.get("grade"),
                         "real_names": names, "exact": exact, "fuzzy": stem}
        print(" %-18s %-12s 真名%2d 精确命中%2d 近似%2d"
              % (it["id"], (it.get("name") or "")[:10], len(names), len(exact), len(stem)))

    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
