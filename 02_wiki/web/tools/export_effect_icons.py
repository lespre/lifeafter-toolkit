# -*- coding: utf-8 -*-
"""导出武器皮肤战斗表现面板图标（12 个固定 UI 图标）并回填到板数据。

只走 PE 源（la.py img export），失败不回落 PC。
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
PY = ROOT / "00_规范与工具/环境/venv/Scripts/python.exe"
OUTDIR = ROOT / "02_wiki/web/assets/effect_icons"
REL = "assets/effect_icons"
TABLE = ROOT / "01_索引与产物/30_分析/weapon_skin_effect_show.json"
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(TABLE.read_text(encoding="utf-8"))
    icons = sorted({r[k] for v in data.values() for r in v for k in ("icon", "icon_melee") if r.get(k)})
    print("待导出", len(icons))

    ok, fail = {}, []
    for p in icons:
        name = p.rsplit("/", 1)[-1]
        dest = OUTDIR / name
        if dest.is_file() and dest.stat().st_size > 0:
            ok[p] = name
            continue
        r = subprocess.run([str(PY), str(ROOT / "la.py"), "img", "export", p, "-o", str(dest)],
                           capture_output=True, text=True, cwd=str(ROOT), timeout=120)
        if dest.is_file() and dest.stat().st_size > 0:
            ok[p] = name
            print("  ✓", name, dest.stat().st_size, "B")
        else:
            fail.append((p, (r.stdout or r.stderr)[-80:]))
            print("  ✗", name, (r.stdout or r.stderr)[-80:].replace("\n", " "))

    print("成功", len(ok), "失败", len(fail))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in board["items"]:
        rows = it.get("effect_show") or []
        for r in rows:
            for key, dst in (("icon", "icon_rel"), ("icon_melee", "icon_melee_rel")):
                src = r.get(key)
                if src and src in ok:
                    r[dst] = REL + "/" + ok[src]
                    n += 1
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("回填图标字段", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
