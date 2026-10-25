# -*- coding: utf-8 -*-
"""找 special_hurt_params(经典服 693 行) 的 key 被谁引用。"""
from __future__ import annotations

import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata")


def rows_of(p, chs=None):
    b = pathlib.Path(p).read_bytes()
    at = b.find(b"x{")
    if at < 0:
        return None
    L = struct.unpack_from("<I", b, at + 2)[0]
    pool = {}
    if chs and pathlib.Path(chs).is_file():
        try:
            pool = BT.parse_legacy_chs_pool(pathlib.Path(chs).read_bytes())
        except Exception:
            pool = {}
    try:
        return BT.decode_table_rows(b[at + 6: at + 6 + L], pool, resolve_jumps=False)[0]
    except Exception:
        return None


def main() -> int:
    base = rows_of(CD / "special_hurt_params_data.py")
    keys = {int(r["key"]) for r in base}
    print("经典服参数组", len(keys), "样例", sorted(keys)[:5])

    targets = [
        ("buff_data", CD / "buff_data.py", CD / "buff_data_chs.py"),
        ("skill_data", CD / "skill_data.py", CD / "skill_data_chs.py"),
        ("skill_bullet_data", CD / "skill_bullet_data.py", CD / "skill_bullet_data_chs.py"),
        ("oversea/rangeland_hurt_test_data",
         CD / "oversea/rangeland_hurt_test_data_auto_oversea_data_kj1.py",
         CD / "oversea/rangeland_hurt_test_data_auto_oversea_data_kj1_chs.py"),
    ]
    for label, p, chs in targets:
        if not pathlib.Path(p).is_file():
            print(label, "缺")
            continue
        rows = rows_of(p, chs)
        if not rows:
            print(label, "解不出/空")
            continue
        fields = set()
        for r in rows[:200]:
            fields.update(r["values"].keys())
        hurt = sorted(f for f in fields if "hurt" in f.lower() or "param" in f.lower())
        print("%-34s 行%-6d hurt相关字段 %s" % (label, len(rows), hurt[:8]))
        # 看这些字段的取值是否命中 keys
        hit = 0
        sample = []
        for r in rows:
            for f in hurt:
                v = r["values"].get(f)
                if not v:
                    continue
                x = v[1] if isinstance(v, tuple) else v
                try:
                    xi = int(x)
                except Exception:
                    continue
                if xi in keys:
                    hit += 1
                    if len(sample) < 5:
                        sample.append((r["key"], f, xi))
        print("    命中参数组 id", hit, sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
