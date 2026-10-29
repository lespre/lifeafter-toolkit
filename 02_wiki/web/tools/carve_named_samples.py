# -*- coding: utf-8 -*-
"""按样本名从 FSB 索引精确取 WAV，并挂到指定皮肤卡的音效区。

用法：python carve_named_samples.py <skin_id> <dir> <sample_name> [<sample_name> ...]
标签由样本名生成（走 translate_skin_sfx_names 的词表思路，简单直译）。
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

IDX = PROJ / "01_索引与产物/30_分析/fsb_sample_index_pe.json"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
ATT = PROJ / "02_wiki/web/data/weapon_skin_audio_attachments.json"
AUDIO = PROJ / "02_wiki/web/assets/audio/weapon_skin"
VGM = pathlib.Path("C:/Users/Administrator/AppData/Local/Temp/vgm/ex/vgmstream-cli.exe")


def carve(pack: str, off: int, ln: int, k: int, out: pathlib.Path) -> bool:
    with open(PACKS / pack, "rb") as f:
        f.seek(off)
        blob = f.read(ln)
    tf = tempfile.NamedTemporaryFile(suffix=".fsb", delete=False)
    tf.write(blob)
    tf.close()
    tmp = pathlib.Path(tf.name)
    try:
        r = subprocess.run([str(VGM), "-s", str(k), "-o", str(out), str(tmp)],
                           capture_output=True, timeout=180)
        return out.is_file() and out.stat().st_size > 1000
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    sid, dirname, *names = sys.argv[1:]
    idx = json.loads(IDX.read_text(encoding="utf-8"))["index"]
    outdir = AUDIO / dirname
    outdir.mkdir(parents=True, exist_ok=True)
    items = []
    for nm in names:
        hits = idx.get(nm) or []
        if not hits:
            print("  未命中", nm)
            continue
        pack, off, ln, k = hits[0]
        dst = outdir / (nm + ".wav")
        if carve(pack, off, ln, k, dst):
            items.append({"label": nm, "file": dst.name})
            print("  ok", nm, dst.stat().st_size, "B  <-", pack, off, "sub", k)
        else:
            print("  失败", nm, pack, off, k)
    if not items:
        print("没有产出")
        return 1
    att = json.loads(ATT.read_text(encoding="utf-8"))
    att.setdefault("skins", {})[sid] = {
        "name": None, "dir": dirname,
        "groups": [{"label": "", "items": items}],
        "evidence": "名字精确匹配（样本名=配置真名）",
    }
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    print("已挂到 %s：%d 条" % (sid, len(items)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
