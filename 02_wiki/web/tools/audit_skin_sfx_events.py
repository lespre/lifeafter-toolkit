# -*- coding: utf-8 -*-
"""武器皮肤音效：统计「行为 .sfx 路径 → FxGroup 索引 → EventName」的覆盖情况。"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

ROOT = pathlib.Path("E:/la拆包项目")
ART = ROOT / "01_索引与产物/30_分析/site_artifacts/artifacts/active/weapon_skin_audio"
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"


def norm(p: str) -> str:
    return p.replace("\\", "/")


def main() -> int:
    idx = [json.loads(l) for l in open(ART / "AUDIO_FXGROUP_INDEX.jsonl", encoding="utf-8")]
    by_sfx: dict[str, list[dict]] = {}
    for r in idx:
        for s in r.get("SfxName") or []:
            by_sfx.setdefault(norm(s), []).append(r)
    ev_cnt = sum(1 for v in by_sfx.values() if any(x.get("EventName") for x in v))
    print("FxGroup 索引 sfx 路径 %d ｜ 其中带事件 %d" % (len(by_sfx), ev_cnt))

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    its = d["items"]
    print("样例 behavior_resources:", json.dumps(its[3].get("behavior_resources"), ensure_ascii=False)[:300])

    skins_with = 0
    paths = 0
    hit = 0
    with_event = 0
    per_grade = Counter()
    for i in its:
        ps = set()
        br = i.get("behavior_resources") or []
        for b in br:
            v = b.get("value") if isinstance(b, dict) else b
            if isinstance(v, str) and v.endswith(".sfx"):
                ps.add(norm(v))
        if ps:
            skins_with += 1
        grades = i.get("grade") or ""
        n_ev = 0
        for p in ps:
            paths += 1
            if p in by_sfx:
                hit += 1
                if any(x.get("EventName") for x in by_sfx[p]):
                    with_event += 1
                    n_ev += 1
        if n_ev:
            per_grade[grades] += 1
    print("有 sfx 路径的卡 %d / %d ｜ 路径 %d 命中索引 %d ｜ 有事件 %d"
          % (skins_with, len(its), paths, hit, with_event))
    print("有事件的卡按品级:", per_grade.most_common())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
