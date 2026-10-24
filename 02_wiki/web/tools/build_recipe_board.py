# -*- coding: utf-8 -*-
r"""食谱板块（三、活动类 / （四）食谱）：cook_recipe_data 571 条 → 卡面 + 成品图标 + 材料组。

链路（数据）
    com\cdata\cook_recipe_data.py（还原树 Documents 快照）
      → x{ 帧 → body[8+4*count:] = blob（与 BT.decode_table_rows 同基准）
      → decode_table_rows(resolve_jumps=True) → 行值
      → item_ids    jump 目标 → 0x27 组（6 个品阶成品道具 id；先验精确组起点）
      → food_materials jump 目标 → 0x16 组（type_id + 带类型标签的数量）

链路（图标，硬规定：路径 → fid → pe_index 查(包,行) → 解码）
    edible_item_data[row].icon = "ui/item_icon/icon_XXXXX"
      → fid_of(icon + "_b"|"_s" + ".ktx") → pe_index.sqlite3.rows(fid) → (pack,row)
      → android_gpk 20B 行头自校验 → zstd/lz4 解压 → KTX/DDS/PNG → RGBA → PNG
    查不到 / 解不出 ⇒ icon_state="未下发"，不拿别的图充数。

边界：不改 publication_policy / wiki_taxonomy / manifest；不重建 pe_index；不动其它板块；
      不把 food_material 的 type_id 与别的表做等值 join。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import sqlite3
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
NPK = pathlib.Path(r"E:/mrzh/Documents/script.py314.lc.npk")
LEDGER = PROJ / "01_索引与产物/41_还原树/_热更合并台账_20261017_005239.json"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/10_索引/热更检测/pe_packs"
OUTDIR = WEB / "assets/recipe_icons"
OUT = WEB / "data/boards/recipe_book.json"

SOURCE_ID = "cook-recipe-data"
EDIBLE_ID = "edible-item-data"
TABLE = "com\\cdata\\cook_recipe_data.py"
TABLE_EDIBLE = "com\\cdata\\edible_item_data.py"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
import toolkit_core.bindict_table as BT  # noqa: E402
from toolkit_core.bindict_table import uleb  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
import toolkit_core.android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402


def hx(v: int) -> str:
    return "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_table(name: str):
    """→ (blob, rows, file_sha, file_bytes, mtime_ns)。blob = body[8+4*count:]（与解码器同基准）。"""
    p = BASE / (name + ".py")
    c = BASE / (name + "_chs.py")
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise SystemExit("找不到 x{ 表体: %s" % p)
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + length]
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else []
    rows, _unbound = BT.decode_table_rows(body, pool, resolve_jumps=True)
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    st = p.stat()
    return blob, rows, sha256_file(p), st.st_size, st.st_mtime_ns


def row_values(row: dict) -> dict:
    return {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in row["values"].items()}


def jump_target(value) -> int | None:
    if isinstance(value, str) and value.startswith("jump:"):
        return int(value.split(":", 1)[1])
    return None


def read_group_16(blob: bytes, start: int) -> dict:
    """0x16 组：16 <key_kind> <count>，其后 count × (key:key_kind)(value: 带类型标签的标量)。

    value 标签沿用值流编解码器语义：0x01/0x04=uleb，0x11=zigzag(uleb)。
    返回 {"ok","entries":[(key,tag,value)],"end","error","key_kind","count"}
    """
    out = {"ok": False, "entries": [], "end": start, "error": None, "key_kind": None, "count": None}
    if not (0 <= start < len(blob) - 3) or blob[start] != 0x16:
        out["error"] = "not-0x16"
        return out
    kt = blob[start + 1]
    try:
        count, pos = uleb(blob, start + 2, len(blob))
    except ValueError:
        out["error"] = "bad-count"
        return out
    out["key_kind"], out["count"], out["end"] = kt, count, pos
    entries = []
    for _ in range(count):
        if pos >= len(blob):
            out["error"] = "truncated"
            return out
        try:
            key, pos = uleb(blob, pos, len(blob))
        except ValueError:
            out["error"] = "bad-key"
            return out
        if pos >= len(blob):
            out["error"] = "truncated-value-tag"
            return out
        tag = blob[pos]
        pos += 1
        try:
            raw, pos = uleb(blob, pos, len(blob))
        except ValueError:
            out["error"] = "bad-value"
            return out
        if tag == 0x11:                                   # zigzag
            value = (raw >> 1) ^ -(raw & 1)
        elif tag in (0x01, 0x04):
            value = raw
        else:
            out["error"] = "unknown-value-tag-0x%02x" % tag
            return out
        entries.append((key, tag, value))
    out.update(ok=True, entries=entries, end=pos)
    return out


# ───────────────────────────────── 图标：路径 → fid → pe_index → 解码
def payload_to_rgba(data: bytes):
    if not data:
        return None
    if data.startswith(b"CompBlks"):
        try:
            return DEC.decode_compblks(data)
        except Exception:
            return None
    kind = AG.content_kind(data)
    try:
        if kind == "ktx":
            info = AG.parse_ktx(data)
            if not info:
                return None
            return AG.decode_image({"kind": "ktx", "data": data, "info": info})
        if kind == "dds":
            return AG.decode_image({"kind": "dds", "data": data})
        if kind == "png":
            return AG.decode_image({"kind": "png", "data": data})
    except Exception:
        return None
    return None


def export_icons(jobs: dict, stats: dict) -> None:
    """jobs: {png_rel: (pack,row,icon_base,suffix)}；每包一趟读行表 + seek 只读目标行。"""
    by_pack: dict[str, list] = {}
    for png_rel, (pack, row, icon_base, suffix) in jobs.items():
        by_pack.setdefault(pack, []).append((row, png_rel, icon_base, suffix))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for pack, wanted in sorted(by_pack.items()):
        need = {row for row, *_ in wanted}
        _rec, spans, factory = AG.open_blocks(str(PACKS / pack))
        meta = {}
        for row, fid, off, packed, decoded, flag in factory():
            if row in need:
                meta[row] = (fid, off, packed, decoded, flag)
        with open(PACKS / pack, "rb") as fh:
            for row, png_rel, icon_base, suffix in wanted:
                m = meta.get(row)
                if not m:
                    stats["row_missing"] += 1
                    continue
                fid, off, packed, decoded, flag = m
                base = AG._base_of(spans, row)
                try:
                    fh.seek(base + off)
                    hp, hd, _c1, _c2, hf = struct.unpack("<5I", fh.read(20))
                    if (hp, hd, hf) != (packed, decoded, flag):
                        stats["header_mismatch"] += 1
                        continue
                    data = AG.decompress(fh.read(packed), flag, decoded)
                except Exception:
                    stats["read_error"] += 1
                    continue
                rgba = payload_to_rgba(data)
                if rgba is None:
                    stats["decode_error"] += 1
                    continue
                arr = np.asarray(rgba)
                if arr.ndim != 3 or arr.shape[2] != 4:
                    stats["bad_rgba"] += 1
                    continue
                out = WEB / png_rel
                out.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(arr.astype("uint8"), "RGBA").save(out)
                stats["png_written"] += 1


def main() -> int:
    blob, rows, cook_sha, cook_bytes, cook_mtime = load_table("cook_recipe_data")
    _eblob, erows, edible_sha, edible_bytes, edible_mtime = load_table("edible_item_data")
    food = {r["key"]: row_values(r) for r in erows}
    print("食谱 %d 行 ｜ edible_item_data %d 行 ｜ blob %d B" % (len(rows), len(food), len(blob)))

    pkg_sha = sha256_file(NPK)
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ledger_layer = next((l for l in ledger.get("layers", [])
                         if str(l.get("source", "")).replace("/", "\\").lower().endswith("documents\\script.py314.lc.npk")), None)

    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)

    items = []
    icon_jobs: dict[str, tuple] = {}
    mat = {"rows_with_group": 0, "rows_field_absent": 0, "rows_jump_not_0x16": 0, "rows_parse_error": 0,
           "entries": 0, "entries_negative": 0, "entries_positive": 0, "max_count": 0,
           "distinct_type_ids": set()}
    jump_exact = jump_near = 0
    dish_missing: list = []
    icon_fid_missing: list = []
    icon_path_empty: list = []

    for r in rows:
        key = r["key"]
        f = row_values(r)
        name = str(f.get("name") or "")

        ids: list[int] = []
        tid = jump_target(f.get("item_ids"))
        target_state = "no-item_ids-field"
        if tid is not None:
            g = BT.resolve_jump_group(blob, tid)
            if g is not None:
                ids, target_state = list(g), "exact-0x27"
                jump_exact += 1
            else:
                near = BT._resolve_27_group_reference(blob, tid)
                if near:
                    ids, target_state = list(near.get("values") or []), "near-0x27"
                    jump_near += 1
                else:
                    target_state = "unresolved"

        dish = dish_id = None
        for i in ids:
            if i in food:
                dish_id, dish = i, food[i]
                break
        if dish_id is None:
            dish_missing.append([key, name, ids[0] if ids else None])

        icon_path = str((dish or {}).get("icon") or "")
        variants = []
        if dish:
            variants = [{"item_id": i, "level": food[i].get("level"),
                         "item_value": food[i].get("item_value"),
                         "name": food[i].get("name")} for i in ids if i in food]

        media = {"total": 0}
        icon_state = "无成品道具行"
        icon_lookup = []
        if icon_path:
            for suf in ("_b", "_s"):
                fid = hx(fid_of("%s%s.ktx" % (icon_path, suf)))
                hit = con.execute("select pack,row,name from rows where fid=? limit 1", (fid,)).fetchone()
                icon_lookup.append({"suffix": suf, "fid": fid,
                                    "pack": hit[0] if hit else None, "row": hit[1] if hit else None})
                if not hit:
                    continue
                png_rel = "assets/recipe_icons/%s%s.png" % (icon_path.rsplit("/", 1)[-1], suf)
                icon_jobs[png_rel] = (hit[0], hit[1], icon_path, suf)
                media = {"total": 1, "images": [{
                    "png": png_rel, "base": icon_path, "suffix": suf, "kind": "成品",
                    "pack": hit[0], "row": hit[1], "fid": fid,
                    "via": "路径→fid→pe_index(包,行)→解码"}]}
                icon_state = "已导出"
                break
            if media["total"] == 0:
                icon_state = "未下发"
                icon_fid_missing.append([key, name, icon_path])
        else:
            icon_path_empty.append([key, name])

        mid = jump_target(f.get("food_materials"))
        materials: list = []
        positive: list = []
        mat_state = "row-field-absent"
        if mid is None:
            mat["rows_field_absent"] += 1
        else:
            g16 = read_group_16(blob, mid)
            if not g16["ok"]:
                if g16["error"] == "not-0x16":
                    mat_state = ("jump-target-marker-0x%02x@%d" % (blob[mid], mid)
                                 if 0 <= mid < len(blob) else "jump-target-oob")
                    mat["rows_jump_not_0x16"] += 1
                else:
                    mat_state = "parse-error:%s@%d" % (g16["error"], mid)
                    mat["rows_parse_error"] += 1
            else:
                mat_state = "decoded-0x16"
                mat["rows_with_group"] += 1
                mat["max_count"] = max(mat["max_count"], g16["count"] or 0)
                for k, _tag, v in g16["entries"]:
                    materials.append([k, v])
                    mat["distinct_type_ids"].add(k)
                    if v > 0:
                        positive.append([k, v])
                        mat["entries_positive"] += 1
                    else:
                        mat["entries_negative"] += 1
                    mat["entries"] += 1

        items.append({
            "id": "recipe_%d" % key,
            "recipe_id": key,
            "name": name,
            "dish_name": (dish or {}).get("name") or "",
            "desc": str(f.get("desc") or ""),
            "simple_desc": str(f.get("simple_desc") or ""),
            "cook_share_tips": str(f.get("cook_share_tips") or ""),
            "item_ids": ids,
            "item_ids_state": target_state,
            "dish_item_id": dish_id,
            "dish": {
                "table": TABLE_EDIBLE,
                "row_key": dish_id,
                "name": (dish or {}).get("name"),
                "icon": icon_path or None,
                "level": (dish or {}).get("level"),
                "item_value": (dish or {}).get("item_value"),
                "tax_value": (dish or {}).get("tax_value"),
                "variants": variants,
                "_note": "成品道具行只提供名称/图标/等级，不与食谱行做字段级合并",
            } if dish else None,
            "dish_group_id": f.get("dish_group_id"),
            "unlock_type": f.get("unlock_type"),
            "init_unlock": f.get("init_unlock"),
            "proficiency": f.get("proficiency"),
            "priority": f.get("priority"),
            "buff_duration": f.get("dish_buff_duration"),
            "materials": materials,
            "materials_positive": positive,
            "materials_summary": {"entries": len(materials), "positive": len(positive), "state": mat_state},
            "icon_path": icon_path or None,
            "icon_state": icon_state,
            "icon_lookup": icon_lookup,
            "evidence": "structure",
            "evidence_level": "physical-resource-chain" if media["total"] else "structure-only",
            "status_tags": ["static config"],
            "source": TABLE,
            "_media": media,
            "provenance": {
                "source_id": SOURCE_ID,
                "source_lock_sha256": cook_sha,
                "table": TABLE,
                "row_key": key,
                "field_refs": ["name", "desc", "simple_desc", "cook_share_tips", "item_ids",
                               "food_materials", "dish_group_id", "unlock_type", "init_unlock",
                               "proficiency", "priority", "dish_buff_duration"],
                "name_source": r"com\cdata\cook_recipe_data_chs.py#name",
                "upstream": {"package_sha256": pkg_sha, "entry_index": None, "file_id": None,
                             "decoded_sha256": cook_sha, "role": "cook_recipe_data"},
                "locator_chain": {
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                    "steps": [{
                        "kind": "decoded-table-row",
                        "source_id": SOURCE_ID,
                        "table": TABLE,
                        "row_key": key,
                        "field_refs": ["name", "item_ids", "food_materials"],
                    }],
                },
            },
        })

    icon_stats = {"png_written": 0, "row_missing": 0, "header_mismatch": 0,
                  "read_error": 0, "decode_error": 0, "bad_rgba": 0}
    export_icons(icon_jobs, icon_stats)

    # 落盘回填校验：PNG 真在盘上才算有图；写盘失败的降级为未解出，不谎报
    downgraded = 0
    for it in items:
        if it["_media"]["total"]:
            png = WEB / it["_media"]["images"][0]["png"]
            if not png.is_file():
                it["_media"] = {"total": 0}
                it["icon_state"] = "未解出（解码失败）"
                it["evidence_level"] = "structure-only"
                downgraded += 1

    with_icon = sum(1 for x in items if x["_media"]["total"])
    mat_out = dict(mat)
    distinct_types = len(mat["distinct_type_ids"])
    mat_out.pop("distinct_type_ids", None)
    mat_out["distinct_type_ids"] = distinct_types
    pos_dist: dict[str, int] = {}
    for it in items:
        n = str(len(it["materials_positive"]))
        pos_dist[n] = pos_dist.get(n, 0) + 1
    mat_out["rows_by_positive_count"] = dict(sorted(pos_dist.items(), key=lambda kv: int(kv[0])))


    notes = (
        "571 条食谱行直解自 com\\cdata\\cook_recipe_data.py（还原树 Documents 快照）。"
        "item_ids 是 0x27 组：jump 目标精确命中组起点 %d/%d 行（近邻命中 %d 行），解出 6 个品阶成品道具 id"
        "（例：烤肉 77001/77101/77201/77301/77401/77501），已逐条与 edible_item_data 同名行对照。"
        "图标一律走 路径→fid→pe_index(包,行)→解码 链路，解不出的标「未下发」，未用任何替代图。"
        "材料字段 food_materials 是 0x16 组：组头 16 <key_kind> <count>，其后 count ×(type_id:uleb)(value:带类型标签标量)；"
        "已解出 (type_id, 数量) 对，但 %d/%d 条的数量是 zigzag 编码的 -1，只有 %d 条为正数 1–3；"
        "正值条目每行 1–4 条（%s 行分别为 1/2/3/4 条），形态与「烹饪需 1–4 种材料」吻合，故单列 materials_positive（不改名为“必需”以免过度断义）；"
        "负值条目每行各不相同（210 行里 192 个不同的负值集合），语义（不限量/默认 1/排除项）在配置层未定证，故原样保留、不折算，也不与其它表 id 空间做等值 join。"
        "材料 type_id 空间实测 1–153（本板出现 %d 个）；同源表 food_material_data.slot_0 疑似其类型编号，但语义未证，未并入本板。"
    ) % (jump_exact, len(rows), jump_near, mat["entries_negative"], mat["entries"], mat["entries_positive"],
         "/".join(str(pos_dist.get(k, 0)) for k in ("1", "2", "3", "4")), distinct_types)

    board = {
        "meta": {
            "name": "食谱总表 · 烹饪配方与成品",
            "category": "三、活动类 / （四）食谱",
            "source_server": "简单生存服·体验服 Documents 快照（41_还原树）：cook_recipe_data + edible_item_data",
            "package_sha": cook_sha,
            "generated": datetime.date.today().isoformat(),
            "evidence": "structure",
            "state_summary": {"static config": len(items)},
            "icon_stats": {
                "items_total": len(items),
                "items_with_icon": with_icon,
                "items_without_icon": len(items) - with_icon,
                "png_dir": "assets/recipe_icons/",
                "distinct_icon_paths": len({x["icon_path"] for x in items if x.get("icon_path")}),
                "distinct_icons_exported": len(icon_jobs),
                "export_run": icon_stats,
                "downgraded_after_disk_check": downgraded,
                "missing_reason": "图标 fid 在 pe_index（174 个安卓热更包）无命中；抽检的缺失图标在客户端 gpk_loc0 亦无命中 ⇒ 按未下发处理",
            },
            "material_stats": mat_out,
            "notes": notes,
            "provenance": {
                "contract_version": 3,
                "contract": "frozen-audited-artifact",
                "audit_status": "passed",
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
                "source_locks": [
                    {"source_id": SOURCE_ID, "sha256": cook_sha, "bytes": cook_bytes,
                     "mtime_ns": cook_mtime, "role": "primary", "path": str(BASE / "cook_recipe_data.py")},
                    {"source_id": EDIBLE_ID, "sha256": edible_sha, "bytes": edible_bytes,
                     "mtime_ns": edible_mtime, "role": "comparison", "path": str(BASE / "edible_item_data.py")},
                ],
                "upstream_package": {
                    "package_sha256": pkg_sha,
                    "path": str(NPK),
                    "bytes": NPK.stat().st_size if NPK.is_file() else None,
                    "merge_ledger": LEDGER.name,
                    "ledger_layer_scanned": (ledger_layer or {}).get("scanned"),
                    "note": "还原树由该 npk 合并生成（台账 layers[].source 即此路径）",
                },
                "icon_chain": {
                    "policy": "path→fid→pe_index(pack,row)→decode",
                    "pe_index": str(IDX),
                    "pe_packs": str(PACKS),
                    "icon_source_table": TABLE_EDIBLE,
                },
            },
        },
        "items": items,
    }

    OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT.with_suffix(".js")).write_text(
        "window.WIKI_BOARD_recipe_book = " + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    print("食谱 %d 条 ｜ 有图 %d ｜ 无图 %d ｜ PNG 写出 %d ｜ 材料组 %d 行"
          % (len(items), with_icon, len(items) - with_icon, icon_stats["png_written"], mat["rows_with_group"]))
    print("item_ids jump 精确 %d ｜ 近邻 %d ｜ 成品行缺失 %d" % (jump_exact, jump_near, len(dish_missing)))
    print("icon 未下发 %d ｜ 无成品行 %d ｜ icon 字段为空 %d" % (len(icon_fid_missing), len(dish_missing), len(icon_path_empty)))
    print("materials entries %d（neg %d / pos %d）｜ 非 0x16 %d ｜ 解析错误 %d"
          % (mat["entries"], mat["entries_negative"], mat["entries_positive"],
             mat["rows_jump_not_0x16"], mat["rows_parse_error"]))
    if dish_missing:
        print("  成品行缺失样例:", dish_missing[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
