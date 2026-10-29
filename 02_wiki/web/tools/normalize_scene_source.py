import sys
# -*- coding: utf-8 -*-
"""统一场景平衡板块的来源口径（去掉旧路径 pe_20261020）。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import BOARDS_DIR  # noqa: E402

p = pathlib.Path(BOARDS_DIR / "scene_balance.json")
d = json.loads(p.read_text(encoding="utf-8"))
m = d["meta"]
src = ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata（special_hurt_params_data、space_data）"
       " · 资源 41_还原树/pe/资源")
m["source_server"] = src
if "source_label" in m:
    m["source_label"] = src
p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("场景平衡来源口径已统一：", src)
