# -*- coding: utf-8 -*-
"""站点清理 + 依赖归位。"""
from __future__ import annotations

import json
import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "04_站点/web"
PARK = ROOT / "03_执行/95_待清理/站点_20261022"
PARK.mkdir(parents=True, exist_ok=True)

moved, removed, patched = [], [], []


def mv(src: pathlib.Path, dst: pathlib.Path, tag: str) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst = dst.with_name(dst.name + "_1")
    shutil.move(str(src), str(dst))
    moved.append({"what": tag, "from": src.relative_to(ROOT).as_posix(),
                  "to": dst.relative_to(ROOT).as_posix()})


# 1) 归档与缓存
mv(WEB / "_备份归档", PARK / "_备份归档", "旧板块备份 295MB")
mv(WEB / "_cache_official_icons.json", PARK / "_cache_official_icons.json", "图标缓存 3.6MB")
mv(WEB / "_audio_probe_test.html", PARK / "_audio_probe_test.html", "探针页")
mv(WEB / "_perf_probe_test.html", PARK / "_perf_probe_test.html", "探针页")

# 2) 旧版预览页（v3 已取代 v1/v2）
for name in ("spine_view.html", "spine_view_v2.html"):
    mv(WEB / name, PARK / name, "旧版 spine 预览")

# 3) 播放器归位：统一到 assets/spine_runtime/3.8/
old_root = WEB / "assets/spine_runtime/spine-webgl-3.8.js"
if old_root.is_file():
    old_root.unlink()
    removed.append(old_root.relative_to(ROOT).as_posix())

# 4) 预览页指向 3.8 目录
v3 = WEB / "spine_view_v3.html"
s = v3.read_text(encoding="utf-8")
if 'assets/spine_runtime/spine-webgl-3.8.js' in s:
    s = s.replace('assets/spine_runtime/spine-webgl-3.8.js',
                  'assets/spine_runtime/3.8/spine-webgl-3.8.js')
    v3.write_text(s, encoding="utf-8")
    patched.append(v3.relative_to(ROOT).as_posix())

(PARK / "MANIFEST.json").write_text(
    json.dumps({"moved": moved, "removed": removed, "patched": patched}, ensure_ascii=False, indent=1),
    encoding="utf-8")
print(json.dumps({"moved": moved, "removed": removed, "patched": patched}, ensure_ascii=False, indent=1))
