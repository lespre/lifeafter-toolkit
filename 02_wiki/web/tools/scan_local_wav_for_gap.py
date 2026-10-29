# -*- coding: utf-8 -*-
"""在已落盘的音频资产里，按真名找工作区里已有但未挂到卡上的 WAV。"""
from __future__ import annotations
import sys

import json
import pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
AUDIO_DIRS = [ROOT / "02_wiki/web/assets/audio", ROOT / "01_索引与产物/30_分析"]


def main() -> int:
    wavs = []
    for base in AUDIO_DIRS:
        if base.is_dir():
            wavs.extend(base.rglob("*.wav"))
    print("磁盘上 WAV 总数", len(wavs))
    stems = defaultdict(list)
    for p in wavs:
        stems[p.stem].append(p)

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    gap = [i for i in d["items"] if (i.get("sfx_real_names") and i.get("sfx_audio_state") != "已提取")]
    for it in gap:
        names = it.get("sfx_real_names") or []
        exact = [n for n in names if n in stems]
        partial = {}
        for n in names:
            hits = [s for s in stems if n in s or s.startswith(n.rsplit("_", 1)[0])]
            if hits:
                partial[n] = sorted(hits)[:4]
        print(" %-10s %-12s 真名%2d 精确%2d 近似%2d"
              % (it["id"], (it.get("name") or "")[:10], len(names), len(exact), len(partial)))
        if exact:
            print("     精确:", [(n, str(stems[n][0].relative_to(ROOT))) for n in exact[:4]])
        if partial:
            k = list(partial)[0]
            print("     近似示例:", k, "→", partial[k])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
