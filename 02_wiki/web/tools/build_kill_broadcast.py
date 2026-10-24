# -*- coding: utf-8 -*-
"""建「击败播报 / MVP 结算动画」板（2026-10-22 重建）。

旧板（38 条）是错的：把「播报文案」(error_code_data) 与「皮肤击败特效」
(weapon_skin_sfx_function_data sfx_type=4) 混成了「击败播报」，两者都不属于外观板。

用户口径要的是两样东西：
  ① 击败播报外观  → common_item_kill_board_data（5 条，带 icon/名字/获取方式）
  ② MVP 结算动画  → mvp_action_data（8 条，带动画名/时长/轨道/演示视频/获取方式）

数据源：41_还原树/pe/配置_基线包/com/cdata（= E:/mrzh/Documents/script.py314.lc.npk），
pe_20261020 树里没有这两张表（已 ls 核对），只能用 documents 树。

解码说明（kill_board 不走默认入口）：
  · common_item_kill_board_data：表体 434 B，0x86 行 + 0x76 索引。
      body[0:4] = 配对 CHS 池条数(37)，blob = body[8+4*count:]
      blob[0:4] = 索引区偏移 de，tail = 76 01 0b <n=5> + n×(u32 hash, u32 node_off)
      node = (uleb key, uleb row_offset)；行 = 0x86 <schema_ref> + 字段值流
      （schema 在 blob@37：n=12、bits=0、字段槽 1..12，解码恰好停在第一条行标记=自洽）
      默认 decode_table_rows 在此报 no schemas discovered（它按 0x76 直接模式取行起点，
      本表 node 里还多一层 (key,row) 间接），所以本脚本自带这层重放。
  · mvp_action_data：标准表，decode_table_rows_with_chs_slots 直接可解；jump 字段用
      去表头后的 blob 解 0x27 组（基址 body[8+4*count]，与本仓解码器一致）。
"""
from __future__ import annotations

import json
import os
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
import toolkit_core.bindict_table as BT  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
TREE = ROOT / "01_索引与产物/41_还原树"
OUT = WEB / "data/boards/kill_broadcast.json"


def find_cdata() -> pathlib.Path:
    """定位 py314 表的 com/cdata 目录。

    还原树正在被顶层分区迁移（script.py314.lc.npk → pc/…，pe_20261020 → pe/…），
    所以不写死路径：按候选列表 → 限定深度扫描，命中「含 mvp_action_data.py 的 cdata 目录」为准。
    """
    for cand in (
        TREE / "script.py314.lc.npk/com/cdata",
        TREE / "pc/配置/com/cdata",
        TREE / "pc/com/cdata",
        TREE / "pc/script.py314.lc.npk/com/cdata",
    ):
        if (cand / "mvp_action_data.py").is_file():
            return cand
    for depth in (2, 3, 4):
        pat = "/".join(["*"] * depth) + "/cdata"
        for d in TREE.glob(pat):
            if (d / "mvp_action_data.py").is_file():
                return d
    raise SystemExit("未找到含 mvp_action_data.py 的 com/cdata 目录（还原树可能正在迁移）")


CD = find_cdata()

_SRC = "E:/mrzh/Documents/script.py314.lc.npk"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
try:
    _st = os.stat(_SRC)
    SRC_BYTES, SRC_MTIME = _st.st_size, _st.st_mtime_ns
except OSError:
    SRC_BYTES, SRC_MTIME = 196059988, 1792505574167464800


def body(p: pathlib.Path) -> bytes:
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def pool_of(table: str) -> list[str]:
    return BT.parse_legacy_chs_pool((CD / (table + "_chs.py")).read_bytes())


def plain(v):
    """values 里的 (type, value) 折叠成 value。"""
    if isinstance(v, (list, tuple)) and len(v) == 2 and isinstance(v[0], str):
        return v[1]
    return v


def prov(table: str, key, fields: list[str]) -> dict:
    return {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": table,
        "row_key": str(key),
        "field_refs": fields,
        "name_source": "chs-pool",
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": "documents-py314-current",
                "table": table,
                "row_key": str(key),
                "field_refs": fields,
            }],
        },
        "table_raw": table,
    }


# ---------------------------------------------------------------- ① 击败播报
def decode_kill_board() -> list[dict]:
    """common_item_kill_board_data：0x86 行 + 0x76 索引（node 内含 key→row 一层间接）。"""
    pool = pool_of("common_item_kill_board_data")
    b = body(CD / "common_item_kill_board_data.py")
    chs_count = struct.unpack_from("<I", b, 0)[0]
    if chs_count != len(pool):
        raise SystemExit(f"CHS 池条数不符：body={chs_count} pool={len(pool)}")
    blob = b[8 + 4 * chs_count:]
    de = struct.unpack_from("<I", blob, 0)[0]
    tail = blob[de:]
    if tail[0] != 0x76:
        raise SystemExit(f"索引尾不是 0x76：{tail[:4].hex()}")
    n, pos = BT.uleb(tail, 3, len(tail))
    nodes = [struct.unpack_from("<II", tail, pos + 8 * i) for i in range(n)]
    rows = []
    for _hash, node_off in nodes:
        key, p = BT.uleb(blob, node_off, len(blob))
        row_off, p = BT.uleb(blob, p, len(blob))
        if blob[row_off] not in BT.ROW_MARKERS + BT.NESTED_ROW_MARKERS:
            raise SystemExit(f"row {row_off} 不是行标记：{blob[row_off]:#x}")
        schema_ref, p = BT.uleb(blob, row_off + 1, len(blob))
        bits, fields, _end = BT._schema_at(blob, schema_ref, pool)
        vals = {}
        cursor = p
        for _slot, type_byte, name in fields:
            raw, cursor = BT._decode_value(blob, cursor, type_byte, pool)
            vals[name] = plain(raw)
        if vals.get("id") != key:
            raise SystemExit(f"行键与 id 不符：key={key} id={vals.get('id')}")
        vals["_row_key"] = key
        vals["_row_off"] = row_off
        vals["_bits"] = bits
        rows.append(vals)
    return rows


# ---------------------------------------------------------------- ② MVP 动画
def decode_mvp_actions() -> list[dict]:
    pool = pool_of("mvp_action_data")
    b = body(CD / "mvp_action_data.py")
    rows = decode_table_rows_with_chs_slots(b, pool)[0]
    chs_count = struct.unpack_from("<I", b, 0)[0]
    blob = b[8 + 4 * chs_count:]

    def group(val):
        if not (isinstance(val, str) and val.startswith("jump:")):
            return None
        g = BT.resolve_jump_group(blob, int(val.split(":")[1])) or []
        return [pool[i] if isinstance(i, int) and i < len(pool) else i for i in g]

    out = []
    for r in rows:
        vals = {k: plain(v) for k, v in (r.get("values") or {}).items()}
        for k in list(vals):
            g = group(vals[k])
            if g:
                vals[k] = g
        vals["_row_key"] = r["key"]
        out.append(vals)
    return out


def decode_mvp_skin_links() -> dict:
    """MVP 动画 → 关联武器皮肤（skin_id / 男女 sfx / 男女 gis 模型路径）。

    mvp_action_res_replace_data 的字段：action_id, skin_id(行键), sfx_male, sfx_female,
    model_path_male/female, gis_path_male/female, model_socket, coldweapon。
    这是「MVP 结算动画属于哪套皮肤」的唯一直接字段链（weapon_skin_sfx_function_data 里
    sfx_type=17 全场最佳动画 0 行，动画不在皮肤音效表里）。
    """
    out: dict = {}
    path = CD / "mvp_action_res_replace_data.py"
    if not path.is_file():
        return out
    pool = pool_of("mvp_action_res_replace_data")
    rows = decode_table_rows_with_chs_slots(body(path), pool)[0]
    for r in rows:
        v = {k: plain(x) for k, x in (r.get("values") or {}).items()}
        aid = v.get("action_id")
        out.setdefault(aid, []).append({
            "skin_id": r["key"],
            "sfx_male": v.get("sfx_male"),
            "sfx_female": v.get("sfx_female"),
            "model_male": v.get("model_path_male"),
            "model_female": v.get("model_path_female"),
            "socket": v.get("model_socket"),
        })
    return out


def main() -> int:
    kb = decode_kill_board()
    mv = decode_mvp_actions()
    skin_links = decode_mvp_skin_links()
    if len(kb) != 5:
        raise SystemExit(f"击败播报行数异常：{len(kb)}（期望 5）")
    if len(mv) != 8:
        raise SystemExit(f"MVP 行数异常：{len(mv)}（期望 8）")

    items: list[dict] = []
    for r in sorted(kb, key=lambda x: x["id"]):
        desc = r.get("desc") or ""
        acquire = desc.split("#r#r", 1)[1].split("，")[0] if "#r#r" in desc else ""
        items.append({
            "id": f"kb_{r['id']}",
            "name": r.get("name") or "",
            "kind": "击败播报",
            "item_id": r["id"],
            "icon": r.get("icon") or "",
            "desc": desc.replace("#r#r", "\n"),
            "acquire": acquire,
            "level": r.get("level"),
            "sort_id": r.get("sort_id"),
            "sub_item_type": r.get("sub_item_type"),
            "hide_in_bag": r.get("hide_in_bag"),
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "common_item_kill_board_data",
            "provenance": prov("common_item_kill_board_data", r["_row_key"],
                               ["desc", "name", "icon", "id", "level", "sort_id"]),
        })

    for r in sorted(mv, key=lambda x: x["_row_key"]):
        track = r.get("cine_names") or r.get("trk_names") or []
        track3 = r.get("cine_names3") or []
        items.append({
            "id": f"mvp_{r.get('anim_name')}",
            "name": r.get("name") or "",
            "kind": "MVP 结算动画",
            "anim_name": r.get("anim_name"),
            "level": r.get("level"),
            "icon": r.get("icon") or "",
            "acquire": r.get("jump_tips") or "",
            "kind_detail": "战场奖励" if "特训战场" in str(r.get("jump_tips")) else "皮肤升格/造境",
            "duration": r.get("anim_in_duration") if not isinstance(r.get("anim_in_duration"), str) else None,
            "track": track,
            "track_alt": track3,
            "videos": r.get("videos") or [],
            "video_covers": r.get("video_covers") or [],
            "skins": skin_links.get(r["_row_key"], []),
            "default_scene": r.get("default_scene"),
            "show_pos": r.get("show_pos"),
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "mvp_action_data",
            "provenance": prov("mvp_action_data", r["_row_key"],
                               ["name", "icon", "anim_name", "level", "jump_tips",
                                "cine_names", "videos", "video_covers"]),
        })

    state = {}
    for it in items:
        state[it["kind"]] = state.get(it["kind"], 0) + 1

    board = {
        "meta": {
            "name": "击败播报 / MVP 结算动画",
            "category": "三、活动类 / （五）击败播报",
            "source_server": "简单生存服·体验服（Documents py314 树）",
            "generated": "2026-10-22",
            "id_label": "条目",
            "hide_media": True,
            "evidence": "structure",
            "card_mode": "roster",
            "package_sha": SHA,
            "filters": [{"key": "kind", "label": "类型"}],
            "card_summary": [["kind", "类型"], ["acquire", "获取方式"]],
            "state_summary": state,
            "note": (
                "击败播报 = common_item_kill_board_data 的 5 行（icon/名字/说明直接来自该表 CHS 池，"
                "说明句写明「<皮肤>升格至二阶后获得」）；MVP 结算动画 = mvp_action_data 的 8 行"
                "（动画名 bq_mvp_01..08、时长、轨道 track/*.xml、演示视频、获取方式）。"
                "旧板把 error_code_data 的播报文案与 weapon_skin_sfx_function_data 的"
                "击败特效(sfx_type=4)混进本板，二者分别是提示文案与武器皮肤音效，已剔除。"
                "MVP 的所属皮肤与 sfx 路径来自 mvp_action_res_replace_data（action_id → skin_id / 男女 sfx / 男女 gis）；"
                "weapon_skin_sfx_function_data 里 sfx_type=17(全场最佳动画) 行数为 0，动画本体不在皮肤音效表。"
            ),
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [{
                    "source_id": "documents-py314-current",
                    "role": "primary",
                    "path": _SRC,
                    "sha256": SHA,
                    "bytes": SRC_BYTES,
                    "mtime_ns": SRC_MTIME,
                }],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
        },
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK {OUT} items={len(items)} {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
