# -*- coding: utf-8 -*-
"""场景 × 伤害加成上下限 映射表（hurt params + space_data 名字）。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")


def rows_of(p: pathlib.Path, chs: pathlib.Path | None = None):
    b = p.read_bytes()
    at = b.find(b"x{")
    if at < 0:
        return None
    L = struct.unpack_from("<I", b, at + 2)[0]
    pool = {}
    if chs and chs.is_file():
        try:
            pool = BT.parse_legacy_chs_pool(chs.read_bytes())
        except Exception:
            pool = {}
    return BT.decode_table_rows(b[at + 6: at + 6 + L], pool, resolve_jumps=False)[0]


def main() -> int:
    params = json.loads((OUT / "hurt_additional_rate_params_kj1.json").read_text(encoding="utf-8"))
    spaces = rows_of(CD / "space_data.py", CD / "space_data_chs.py")
    name = {}
    if spaces:
        for r in spaces:
            v = r["values"].get("name")
            if v:
                try:
                    name[int(r["key"])] = str(v[1] if isinstance(v, tuple) else v)
                except Exception:
                    pass
    print("space_data 名字", len(name))

    out = []
    for p in params:
        sid = p.get("scene_id")
        out.append({
            "scene_id": sid,
            "name": name.get(int(sid)) if isinstance(sid, int) else None,
            "min": p.get("min_hurt_additional_rate"),
            "max": p.get("max_hurt_additional_rate"),
            "p2d_min": p.get("p2d_min_hurt_additional_rate"),
            "min_attack": p.get("min_attack"),
            "reduce_hurt_value": p.get("reduce_hurt_value"),
        })
    out.sort(key=lambda x: (x["name"] is None, x["name"] or "", x["scene_id"] or 0))
    (OUT / "scene_balance.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    named = [x for x in out if x["name"]]
    print("有名场景", len(named), "/", len(out))
    for x in named[:40]:
        print("  %-6s %-22s %.2f ~ %.2f" % (x["scene_id"], x["name"], x["min"], x["max"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
