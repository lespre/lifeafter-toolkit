# -*- coding: utf-8 -*-
"""按正确 subsong 重新切 1110189 浪漫过载的 3 条音效，并挂到音效附件。"""
from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path("E:/la拆包项目")
PACKS = ROOT / "01_索引与产物/源包/pe_gres_android"
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"
JS = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.js"
AUDIO = ROOT / "02_wiki/web/assets/audio/weapon_skin"
VGM = pathlib.Path("C:/Users/Administrator/AppData/Local/Temp/vgm/ex/vgmstream-cli.exe")

SKIN = "1110189"
DIR = "penhuoqi_smzg_1110189"
BANK = ("0358.gpk", 56352420, 97536)
# (subsong 1-based, 样本名, 中文标签)
SAMPLES = [
    (2, "weapon_smzg_fire_start", "开火（单发）"),
    (1, "weapon_smzg_fire_loop", "持续开火（循环）"),
    (3, "weapon_smzg_reload", "换弹"),
]


def carve(k: int, out: pathlib.Path) -> bool:
    pack, off, ln = BANK
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
    outdir = AUDIO / DIR
    outdir.mkdir(parents=True, exist_ok=True)
    items = []
    for k, name, label in SAMPLES:
        dst = outdir / f"{name}.wav"
        ok = carve(k, dst)
        print(("  ok  " if ok else "  失败 ") + f"{name} sub={k} {dst.stat().st_size if ok else 0} B → {label}")
        if ok:
            items.append({"label": label, "file": dst.name, "sample": name})
    if not items:
        return 1

    att = json.loads(ATT.read_text(encoding="utf-8"))
    att.setdefault("skins", {})[SKIN] = {
        "name": "浪漫过载",
        "dir": DIR,
        "groups": [{"label": "皮肤专属音（202610_penhuoqi_smzg）", "items": items}],
        "evidence": "FMOD 事件 g66_weapon.fev:/penhuoqi_smzg_202610/ + FSB 样本名精确匹配",
        "source": "0358.gpk sound bank offset 56352420",
    }
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    JS.write_text("window.WEAPON_SKIN_AUDIO_ATTACHMENTS=window.WEAPON_SKIN_AUDIO_ATTACHMENTS = "
                  + json.dumps(att, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"已挂 {SKIN}：{len(items)} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
