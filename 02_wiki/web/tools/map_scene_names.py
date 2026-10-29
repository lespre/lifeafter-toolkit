# -*- coding: utf-8 -*-
"""把伤害参数表的 scene_id 映射到地图名。"""
import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, TOOLKIT_CORE, TREE_ROOT  # noqa: E402
sys.path.insert(0, str(TOOLKIT_CORE))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(TREE_ROOT / "pe/配置/com/cdata")
OUT = pathlib.Path(ANALYSIS_ROOT / "伤害系统逆向")


def main() -> int:
    p = CD / "map_icon_data.py"
    c = CD / "map_icon_data_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    blob = b[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else {}
    rows, _ = BT.decode_table_rows(blob, pool, resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    params = json.loads((OUT / "hurt_additional_rate_params_kj1.json").read_text(encoding="utf-8"))
    scenes = {r["scene_id"] for r in params if r.get("scene_id")}
    print("待映射场景 id", len(scenes))

    mapping = {}
    for r in rows:
        ids = g(r, "show_scene_ids")
        if not (isinstance(ids, str) and ids.startswith("jump:")):
            continue
        grp = BT.resolve_jump_group(blob, int(ids.split(":")[1]))
        if not grp:
            continue
        hit = scenes.intersection(grp)
        if hit:
            name = str(g(r, "name") or "")
            for s in hit:
                mapping.setdefault(s, set()).add(name)

    print("映射到地图名的场景", len(mapping))
    for s in sorted(mapping)[:20]:
        print("  %-6s %s" % (s, "、".join(sorted(mapping[s]))[:40]))

    out = {str(k): sorted(v) for k, v in mapping.items()}
    (OUT / "scene_map_names.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT / "scene_map_names.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
