"""all_equips_data attrs 抽取（帧族感知）— 2026-10-24 结案脚本。

用法：
  <venv python> all_equips_attrs_extract.py            # 打印抽样 + 统计
  <venv python> all_equips_attrs_extract.py --json OUT # 落盘全量 json
"""
import json
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core.bindict_table import (  # noqa: E402
    decode_table_rows, parse_legacy_chs_pool, resolve_jump_target, JUMP_BASE_BY_TABLE,
)

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata/oversea/"
P = BASE + "all_equips_data_auto_oversea_data_kj1.py"
C = BASE + "all_equips_data_auto_oversea_data_kj1_chs.py"


def load():
    raw = open(P, "rb").read()
    chs = open(C, "rb").read()
    # 容器：[... 头 ...][u32 body_len][body]，body 长 373271；body[0:4]=count=5248
    body_len_at = raw.find(struct.pack("<I", 373271), 0, 16384)
    body = raw[body_len_at + 4: body_len_at + 4 + 373271]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    pool = parse_legacy_chs_pool(chs)
    rows, unbound = decode_table_rows(body, pool)
    return body, blob, pool, rows, unbound


def extract():
    body, blob, pool, rows, unbound = load()
    out, stats = [], {"rows": len(rows), "unbound": len(unbound), "attrs_total": 0,
                      "attrs_ok": 0, "frames": {}}
    for r in rows:
        v = r.get("values") or {}
        attrs_field = v.get("attrs")
        rec = {"key": r["key"], "name": v.get("name", (None, None))[1],
               "equip_type": v.get("equip_type", (None, None))[1],
               "weapon_type": v.get("weapon_type", (None, None))[1],
               "attrs": None, "attrs_frame": None}
        if isinstance(attrs_field, tuple) and str(attrs_field[1]).startswith("jump:"):
            stats["attrs_total"] += 1
            j = int(attrs_field[1][5:]) + JUMP_BASE_BY_TABLE.get("all_equips_data", 0)
            res = resolve_jump_target(blob, j, pool)
            rec["attrs_frame"] = res["frame"]
            stats["frames"][res["frame"]] = stats["frames"].get(res["frame"], 0) + 1
            if res.get("error") is None and res.get("values"):
                stats["attrs_ok"] += 1
                rec["attrs"] = res["values"] if res["frame"] != "0x27" else {
                    "pairs": res.get("pairs"), "leaves": res.get("leaves")}
        out.append(rec)
    return out, stats


if __name__ == "__main__":
    data, stats = extract()
    print(json.dumps(stats, ensure_ascii=False))
    if "--json" in sys.argv:
        path = sys.argv[sys.argv.index("--json") + 1]
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print("wrote", path)
    else:
        for rec in [d for d in data if d["key"] in (10001, 10002, 10003, 30019, 30036, 30042, 270000)]:
            print(rec)
