# -*- coding: utf-8 -*-
"""打包 wiki 数据包 v2：**按引用收集**，不再硬编码白名单。

规则：
  1) 页面里出现的 assets/ 与 data/ 引用（html/js）
  2) 所有 board 的 _media.images[].png
  3) data/boards 下的 json/js 全量（页面按 ?b= 动态加载）
  4) data/ 下的 *.js / *.json（小文件，页面直接引用的配置）
  5) 已知图标目录整目录带上
输出：zip + 缺口清单（引用了但磁盘上不存在），后者用于纠错。

用法：python tools/build_release_pack_v2.py [--out PATH] [--dry]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import zipfile

PROJ = pathlib.Path(__file__).resolve().parents[3]
WEB = PROJ / "02_wiki" / "web"
ICON_DIRS = ["core_icons", "chip_icons", "drone_icons", "nucleus_icons", "skin_posters",
             "fashion_icon_refs", "item_icons", "avatar_icons", "vehicle_icons",
             "recipe_icons", "lottery_icons", "show_reward_icons",
             "img_cache", "avatar_frames", "fashion_posters", "appearance_icons",
             "item_icons_full"]

REF = re.compile(r"""["'(](?:\.\./)?((?:assets|data)/[^"')\s]+\.(?:js|json|png|webp|svg|css))""")


def collect() -> tuple[set[pathlib.Path], set[str]]:
    files: set[pathlib.Path] = set()
    missing: set[str] = set()

    for f in list(WEB.glob("*.html")) + list((WEB / "tools").glob("*.py")):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in REF.finditer(text):
            if "%" in m.group(1):      # 代码里的模板串（%s.png），不是真引用
                continue
            p = WEB / m.group(1)
            (files.add(p) if p.exists() else missing.add(m.group(1)))

    for b in (WEB / "data/boards").glob("*.json"):
        try:
            d = json.loads(b.read_text(encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items") or []:
            for im in (it.get("_media") or {}).get("images") or []:
                png = im.get("png")
                if not png:
                    continue
                p = WEB / png
                (files.add(p) if p.exists() else missing.add(png))

    files |= {p for p in (WEB / "data/boards").glob("*") if p.is_file()}
    files |= {p for p in (WEB / "data").glob("*.js") if p.is_file()}
    files |= {p for p in (WEB / "data").glob("*.json") if p.is_file()}

    for d in ICON_DIRS:
        base = WEB / "assets" / d
        if base.is_dir():
            files |= {p for p in base.rglob("*") if p.is_file()}
    return files, missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/rel/la-wiki-data-v1.4.0.zip")))
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--split", action="store_true", help="只打 core（data+代码，不打 assets 大目录）")
    a = ap.parse_args()

    files, missing = collect()
    if a.split:
        files = {p for p in files
                 if "assets" not in p.relative_to(WEB).parts
                 or p.relative_to(WEB).parts[1] in ("skin_posters", "avatar_icons")}
    total = sum(p.stat().st_size for p in files)
    print("收集 %d 个文件，%.1f MB" % (len(files), total / 1048576))
    print("引用了但磁盘不存在：%d 条" % len(missing))
    for m in sorted(missing)[:10]:
        print("   缺", m)
    if a.dry:
        return 0

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for p in sorted(files):
            z.write(p, str(p.relative_to(PROJ)).replace("\\", "/"))
    print("写出", out, "%.1f MB" % (out.stat().st_size / 1048576))
    rep = PROJ / "01_索引与产物/30_分析/发布包缺口_20261024.json"
    rep.write_text(json.dumps(sorted(missing), ensure_ascii=False, indent=1), encoding="utf-8")
    print("缺口清单 →", rep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
