# -*- coding: utf-8 -*-
"""按 model_id 查 player_appear_data 的 gender / force_gender，判断是否仅女款。"""
import collections
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

v = lambda x: x[1] if isinstance(x, tuple) else x
MODELS = [3331, 3483, 3719, 3720, 3721, 3658, 4024, 3546, 5004, 3010, 3006]


def main() -> int:
    raw = (CD / "player_appear_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    pool = BT.parse_legacy_chs_pool((CD / "player_appear_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]

    c = collections.Counter()
    for r in rows:
        val = r["values"]
        g = v(val.get("gender"))
        fg = v(val.get("force_gender"))
        c[(str(g), str(fg))] += 1
    print("全表 (gender, force_gender) 分布:", c.most_common(8))

    print("\n按 model 看：")
    for mid in MODELS:
        sub = [r for r in rows if str(v(r["values"].get("model_id"))) == str(mid)]
        if not sub:
            print("  model %-5s 无行" % mid)
            continue
        gs = collections.Counter((str(v(r["values"].get("gender"))), str(v(r["values"].get("force_gender"))))
                                 for r in sub)
        names = sorted({str(v(r["values"].get("name"))) for r in sub})[:3]
        print("  model %-5s 行 %-3d (gender,force)=%s  %s" % (mid, len(sub), dict(gs), names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
