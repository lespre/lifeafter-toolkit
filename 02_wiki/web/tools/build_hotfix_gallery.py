# -*- coding: utf-8 -*-
"""把 20261030 热更内容做成一个图集包：图片 + index.html + zip。"""
from __future__ import annotations

import json
import pathlib
import shutil
import struct
import subprocess
import sys
import zipfile

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
OUT = ROOT / "_截图/hotfix_20261030"
CATA = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
import pe_fetch  # noqa: E402


def nucleus_icon() -> pathlib.Path | None:
    p = CATA / "nucleus_data.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    pool = parse_legacy_chs_pool((CATA / "nucleus_data_chs.py").read_bytes())
    rows, _ = decode_table_rows(raw[at + 6:at + 6 + n], pool, resolve_jumps=False, lenient=True)
    for r in rows:
        if r.get("key") == 350084:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
            icon = v.get("icon")
            print("核芯 350084 字段", {k: v[k] for k in list(v)[:6]})
            if isinstance(icon, str) and icon.startswith("ui/"):
                dst = OUT / "images" / "core_350084.png"
                dst.parent.mkdir(parents=True, exist_ok=True)
                if pe_fetch.export(icon + "_b", dst) or pe_fetch.export(icon, dst):
                    return dst
    return None


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    imgs = OUT / "images"
    imgs.mkdir(parents=True, exist_ok=True)

    name_of = {}
    mp = ROOT / "01_索引与产物/30_分析/pe_hotfix_fashion_imgs.json"
    if mp.is_file():
        for nm, paths in json.loads(mp.read_text(encoding="utf-8")).items():
            for rel in paths:
                name_of[pathlib.Path(rel).name] = nm

    entries = []
    for p in sorted((WEB / "assets/fashion_posters/pe_hotfix").glob("*.png")):
        shutil.copy2(p, imgs / p.name)
        entries.append(("时装", name_of.get(p.name, p.stem), "images/" + p.name))

    for sid, label in (("1110189", "浪漫过载 · 喷火器 典藏"),
                       ("1110194", "青瓷鉴心 · 狙击枪 直售"),
                       ("1110205", "瑞秋之狙 · 狙击枪 白送")):
        src = WEB / f"assets/skin_posters/{sid}.png"
        if src.is_file():
            shutil.copy2(src, imgs / src.name)
            entries.append(("武器皮肤", f"{sid} · {label}", "images/" + src.name))

    core = nucleus_icon()
    if core:
        entries.append(("核芯", "350084", "images/" + core.name))

    rows = "\n".join(
        f'<figure><img src="{src}" alt="{name}"><figcaption><b>{cat}</b> · {name}</figcaption></figure>'
        for cat, name, src in entries)
    html = f"""<!doctype html><meta charset="utf-8"><title>热更 20261030 图集</title>
<style>
body{{background:#0d1117;color:#e6edf3;font:14px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;margin:24px}}
h1{{font-size:20px;margin:0 0 4px}}p.sub{{color:#8b949e;margin:0 0 20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}}
figure{{margin:0;background:#161b22;border:1px solid #30363d;border-radius:8px;overflow:hidden}}
img{{width:100%;display:block;background:#0b0f14}}
figcaption{{padding:8px 10px;font-size:12px;color:#c9d1d9}}
b{{color:#f0b429;font-weight:600}}
</style>
<h1>热更 20261030 · 图集合集</h1>
<p class="sub">PE 测试服 {len([e for e in entries if e[0]=='时装'])} 张时装图 · 武器皮肤 3 张 · 核芯 1 张</p>
<div class="grid">{rows}</div>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")

    zp = ROOT / "_截图/hotfix_20261030_图集.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in OUT.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(OUT))
    print("条目", len(entries), "｜ 目录", OUT, "｜ zip", zp, "%.1f MB" % (zp.stat().st_size / 1e6))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
