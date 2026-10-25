# -*- coding: utf-8 -*-
"""用 FSB 样本索引，把武器皮肤「音效真名」落到 bank 并导出 WAV。

规则：
- 只认样本名「完全相同」；重名（同一名字出现在多个 bank）不自动绑定，列候选等人工裁决。
- 导出用 vgmstream 按 subsong 序号取，不按名字猜。
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/30_分析/fsb_sample_index_pe.json"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
BOARD = PROJ / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
AUDIO = PROJ / "02_wiki/web/assets/audio/weapon_skin"
VGM = pathlib.Path("C:/Users/Administrator/AppData/Local/Temp/vgm/ex/vgmstream-cli.exe")
REPORT = PROJ / "01_索引与产物/30_分析/weapon_skin_audio_match_report.json"


def carve(pack: str, off: int, ln: int, k: int, out: pathlib.Path) -> bool:
    src = PACKS / pack
    with open(src, "rb") as f:
        f.seek(off)
        blob = f.read(ln)
    with tempfile.NamedTemporaryFile(suffix=".fsb", delete=False) as tf:
        tf.write(blob)
        tmp = pathlib.Path(tf.name)
    try:
        r = subprocess.run([str(VGM), "-s", str(k), "-o", str(out), str(tmp)],
                           capture_output=True, timeout=120)
        return r.returncode == 0 and out.is_file() and out.stat().st_size > 1000
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    idx = json.loads(IDX.read_text(encoding="utf-8"))["index"]
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    gap = [i for i in d["items"] if (i.get("sfx_real_names") and i.get("sfx_audio_state") != "已提取")]
    rep = {}
    ok_total = 0
    for it in gap:
        groups = []
        for name in it["sfx_real_names"]:
            hits = idx.get(name) or []
            if len(hits) == 1:
                pack, off, ln, k = hits[0]
                d_ext = AUDIO / "auto_%s" % it["id"]
                d_ext.mkdir(parents=True, exist_ok=True)
                dst = d_ext / ("%s.wav" % name)
                if carve(pack, off, ln, k, dst):
                    groups.append({"label": name, "file": dst.name, "dir": d_ext.name,
                                   "source": "%s@%d sub%d" % (pack, off, k)})
                    ok_total += 1
            elif len(hits) > 1:
                groups.append({"label": name, "candidates": len(hits), "state": "重名待裁决"})
        if groups:
            rep[it["id"]] = {"name": it.get("name"), "groups": groups}
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("导出 WAV %d 个 ｜ 涉及卡 %d ｜ 报告 %s" % (ok_total, len(rep), REPORT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
