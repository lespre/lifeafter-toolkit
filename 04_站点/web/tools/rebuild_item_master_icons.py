# -*- coding: utf-8 -*-
r"""道具总表 item_master_v01（1189 条）补齐图标 —— 同表 icon 字段 → PE .ktx / PC .bc7 双源定位 → PNG。

链路（数据，零跨源字段 join）
    com\cdata\common_item_data_base.py（PE 测试客户端快照 pe_test_script）
      → x{ 帧 → body[8+4*count:] = blob（与 BT.decode_table_rows 同基准）
      → decode_table_rows(resolve_jumps=True) → 行的 icon 字段（同一条记录，非跨表拼字段）

链路（图标，硬规定：路径 → fid → 落点 → 解码）
    1) PE 口径：icon + "_b"|"_s" + ".ktx" → fid_of → pe_index.sqlite3.rows(fid)
       → (pack,row) → android_gpk 20B 行头自校验 → zstd/lz4 解压 → KTX/DDS/PNG/CompBlks → RGBA
    2) PC 口径：icon + "_b"|"_s"|"" + ".bc7" → pc_fid_calib/hit_table.csv（路径级校准表）
       → (pkg,row) → E:/mrzh/res/<pkg> 块链 → zstd/DDS(BC7) → RGBA
    3) 两源都无 ⇒ icon_state="未下发"，_media.images=[]，绝不拿别的图凑。

输出
    04_站点/web/assets/item_icons/<icon_basename><suffix>.png
    04_站点/web/data/boards/item_master_v01.json（+ 同目录 .js 由 build_wiki.py 重新导出）
    04_站点/web/data/boards/_report_item_icons.md

边界：不改 publication_policy / wiki_taxonomy / manifest；不重建 pe_index；
      不改 src 表；不动其它板块；item 的 evidence/evidence_level/status_tags/provenance 原样保留
      （status_tags 取值域由 publication_policy 冻结，禁止新增自定义标签）。
"""
from __future__ import annotations

import collections
import csv
import datetime
import hashlib
import json
import pathlib
import re
import sqlite3
import struct
import sys

import numpy as np
from PIL import Image

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
BASE_TABLE = PROJ / "03_执行/41_还原树/pe_test_script/common_item_data_base.py"
BASE_CHS = PROJ / "03_执行/41_还原树/pe_test_script/common_item_data_base_chs.py"
IDX = PROJ / "03_执行/30_分析/热更检测/pe_index.sqlite3"
PACKS = PROJ / "03_执行/30_分析/热更检测/pe_packs"
PC_HIT = PROJ / "03_执行/30_分析/热更检测/pc_fid_calib/hit_table.csv"
PC_RES = pathlib.Path(r"E:/mrzh/res")
OUTDIR = WEB / "assets/item_icons"
BOARD = WEB / "data/boards/item_master_v01.json"
REPORT = WEB / "data/boards/_report_item_icons.md"

SOURCE_ID = "ITEM_MASTER_v01"
TABLE = r"com\cdata\common_item_data_base.py"

sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染"))
sys.path.insert(0, str(PROJ / "03_执行/30_分析/热更检测/pe_icon_bind"))
sys.path.insert(0, str(PROJ / "03_执行/30_分析/热更检测/pc_fid_calib"))
import toolkit_core.bindict_table as BT  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
import toolkit_core.android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
import gpk_npk_index as GI  # noqa: E402
import pcdecode  # noqa: E402
import pc_icons  # noqa: E402

MASK = 0xFFFFFFFFFFFFFFFF
EXT_HINT = re.compile(r"\.(png|ktx|dds|bc7)$", re.I)
PE_SUFFIXES = ("_b", "_s")


def hx(v: int) -> str:
    return "%016X" % (v & MASK)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_table():
    raw = BASE_TABLE.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise SystemExit("找不到 x{ 表体: %s" % BASE_TABLE)
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + length]
    pool = BT.parse_legacy_chs_pool(BASE_CHS.read_bytes()) if BASE_CHS.is_file() else []
    rows, _unbound = BT.decode_table_rows(body, pool, resolve_jumps=True)
    st = BASE_TABLE.stat()
    return rows, sha256_file(BASE_TABLE), st.st_size, st.st_mtime_ns


def row_values(row: dict) -> dict:
    return {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in row["values"].items()}


def payload_to_rgba(data: bytes):
    if not data:
        return None
    if data.startswith(b"CompBlks"):
        return DEC.decode_compblks(data)
    kind = AG.content_kind(data)
    try:
        if kind == "ktx":
            info = AG.parse_ktx(data)
            return AG.decode_image({"kind": "ktx", "data": data, "info": info}) if info else None
        if kind in ("dds", "png"):
            return AG.decode_image({"kind": kind, "data": data})
    except Exception:
        return None
    return None


# ─────────────────────────────── 落点查询
def pe_hits(conn: sqlite3.Connection, bases: set[str]) -> dict:
    """{base: (suffix, pack, row, fid, resolved_path, norm_from)}；按 _b 优先。"""
    out = {}
    for base in bases:
        cands = []
        if EXT_HINT.search(base):
            cands.append(("", base))
        cands += [(s, base + s + ".ktx") for s in PE_SUFFIXES]
        for suf, rel in cands:
            fid = hx(fid_of(rel))
            hit = conn.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
            if hit:
                out[base] = (suf, hit[0], hit[1], fid, rel, None)
                break
    return out


def load_pc_table() -> dict:
    idx = {}
    with PC_HIT.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            idx.setdefault(row["path"], row)
    return idx


def pc_hits(pc_idx: dict, bases: set[str]) -> dict:
    out = {}
    for base in bases:
        cands = []
        if EXT_HINT.search(base):
            cands.append(("", base))
        cands += [(s, base + s + ".bc7") for s in PE_SUFFIXES]
        cands += [("", base + ".bc7")]
        for suf, rel in cands:
            row = pc_idx.get(rel)
            if row:
                out[base] = (suf, row, rel, None)
                break
    return out


# ─────────────────────────────── 解码落盘
def _flat_white(arr) -> bool:
    """RGB 全白只有 alpha 形状 ⇒ 客户端染色用的白模图标（动作/舞蹈类）。"""
    try:
        rgb = arr[..., :3]
        a = arr[..., 3]
        return bool((rgb == 255).all()) and int(a.min()) < int(a.max())
    except Exception:
        return False


def export_pe(jobs: dict, stats: dict, written: dict) -> None:
    """jobs: {base: (suffix, pack, row, fid, rel)}"""
    by_pack: dict[str, list] = collections.defaultdict(list)
    for base, (suf, pack, row, fid, rel, _norm) in jobs.items():
        by_pack[pack].append((row, base, suf, fid))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for pack, wanted in sorted(by_pack.items()):
        need = {row for row, *_ in wanted}
        try:
            _rec, spans, factory = AG.open_blocks(str(PACKS / pack))
        except Exception:
            stats["pack_open_error"] += len(wanted)
            continue
        meta = {}
        for row, fid, off, packed, decoded, flag in factory():
            if row in need:
                meta[row] = (fid, off, packed, decoded, flag)
        with open(PACKS / pack, "rb") as fh:
            for row, base, suf, fid in wanted:
                m = meta.get(row)
                if not m:
                    stats["row_missing"] += 1
                    continue
                rfid, off, packed, decoded, flag = m
                try:
                    fh.seek(AG._base_of(spans, row) + off)
                    hp, hd, _c1, _c2, hf = struct.unpack("<5I", fh.read(20))
                    if (hp, hd, hf) != (packed, decoded, flag):
                        stats["header_mismatch"] += 1
                        continue
                    data = AG.decompress(fh.read(packed), flag, decoded)
                except Exception:
                    stats["read_error"] += 1
                    continue
                try:
                    rgba = payload_to_rgba(data)
                except Exception:
                    rgba = None
                if rgba is None:
                    stats["decode_error"] += 1
                    continue
                arr = np.asarray(rgba)
                if arr.ndim != 3 or arr.shape[2] != 4 or arr.size == 0:
                    stats["bad_rgba"] += 1
                    continue
                png = OUTDIR / png_name(base, suf)
                Image.fromarray(arr.astype("uint8"), "RGBA").save(png)
                stats["png_written"] += 1
                written[base] = {"png": png, "w": int(arr.shape[1]), "h": int(arr.shape[0]),
                                 "flat_white": _flat_white(arr)}


_pc_cache: dict[str, tuple] = {}


def _pc_rows(pkg: str) -> tuple:
    """→ ({row: (fid,off,cm,de,fl)}, payload_delta)；每包只解一次块链（ui_01 有 1.3 GB）。"""
    if pkg not in _pc_cache:
        rec, rows, _ = GI._gpk_blockchain(str(PC_RES / pkg))
        table = {r: (fid, off, cm, de, fl) for r, fid, off, cm, de, fl in rows()}
        _pc_cache[pkg] = (table, rec["payload_delta_by_block"][0])
    return _pc_cache[pkg]


def export_pc(jobs: dict, stats: dict, written: dict) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for base, (suf, row, rel, _norm) in jobs.items():
        pkg = row["pkg"]
        try:
            table, delta = _pc_rows(pkg)
        except Exception:
            stats["pack_open_error"] += 1
            continue
        rec = table.get(int(row["row"]))
        if not rec:
            stats["row_missing"] += 1
            continue
        fid, off, cm, _de, _fl = rec
        try:
            with open(PC_RES / pkg, "rb") as fh:
                fh.seek(off + delta)
                raw = fh.read(cm)
            inner, _outer = pcdecode.unwrap(raw)
        except Exception:
            stats["read_error"] += 1
            continue
        try:
            rgba, info = pc_icons.decode_dds(inner)
        except Exception:
            rgba, info = None, {}
        if rgba is None:
            stats["decode_error"] += 1
            continue
        try:
            cx, cy = pc_icons.crop_for(info.get("w", 0), info.get("h", 0))
            img = pc_icons.icon_png(rgba, cx, cy)
        except Exception:
            stats["bad_rgba"] += 1
            continue
        if img.width == 0 or img.height == 0:
            stats["bad_rgba"] += 1
            continue
        png = OUTDIR / png_name(base, suf)
        img.save(png)
        stats["png_written"] += 1
        written[base] = {"png": png, "w": img.width, "h": img.height,
                         "flat_white": _flat_white(np.asarray(img))}


def png_name(base: str, suffix: str) -> str:
    stem = re.sub(r"\.(png|ktx|dds|bc7)$", "", base, flags=re.I).rsplit("/", 1)[-1]
    ext = re.search(r"\.(png|ktx|dds|bc7)$", base, flags=re.I)
    if ext and not suffix:                       # icon 值本身已带扩展名
        return stem + "." + ext.group(1).lower() if ext.group(1).lower() == "png" else stem + ".png"
    return "%s%s.png" % (stem, suffix)


# ─────────────────────────────── 主流程
FIELD_LABELS = {
    "name": "名称",
    "item_id": "道具ID",
    "max_stack_num": "堆叠上限",
    "hide_in_bag": "背包隐藏",
    "hide_in_bag_state": "隐藏状态",
    "icon": "图标路径",
    "icon_state": "图标",
    "icon_note": "图标说明",
    "icon_provenance": "图标溯源",
    "evidence": "证据",
    "evidence_level": "证据等级",
    "status_tags": "状态标签",
    "search_text": "检索文本",
}


def main() -> int:
    rows, table_sha, table_bytes, table_mtime = load_table()
    tab = {}
    dup = 0
    for r in rows:
        v = row_values(r)
        iid = v.get("id")
        if not isinstance(iid, int):
            continue
        if iid in tab:
            dup += 1
            continue
        tab[iid] = v

    board = json.loads(BOARD.read_text(encoding="utf-8-sig"))
    items = board["items"]
    meta_in = board["meta"]

    # 1) 每条 → icon 路径（同表同记录）
    plan = {}
    for it in items:
        v = tab.get(it["item_id"])
        ic = v.get("icon") if v else None
        if not isinstance(ic, str) or not ic.strip():
            plan[it["item_id"]] = None
            continue
        plan[it["item_id"]] = ic.strip()

    bases = {b for b in plan.values() if b}
    conn = sqlite3.connect(str(IDX))
    pe = pe_hits(conn, bases)
    pc_idx = load_pc_table()
    pc = pc_hits(pc_idx, bases - set(pe))

    # 末位兜底：源表路径里重复的 `ui/ui/` 前缀（同一 icon 名，仅段重复）。
    # 只在「归一后同路径确实存在」时启用，绝不改 icon 名、不换图。
    norm_pairs = {}
    for b in sorted(bases - set(pe) - set(pc)):
        nb = b[3:] if b.startswith("ui/ui/") else None
        if nb:
            norm_pairs[nb] = b
    if norm_pairs:
        pe_n = pe_hits(conn, set(norm_pairs))
        for nb, v in pe_n.items():
            pe[norm_pairs[nb]] = v[:5] + (nb,)
        pc_n = pc_hits(pc_idx, set(norm_pairs) - set(pe_n))
        for nb, v in pc_n.items():
            pc[norm_pairs[nb]] = v[:3] + (nb,)
    conn.close()

    pe_stats = collections.Counter()
    pc_stats = collections.Counter()
    pe_written: dict = {}
    pc_written: dict = {}
    export_pe(pe, pe_stats, pe_written)
    export_pc(pc, pc_stats, pc_written)

    # 2) 回填 item
    state_counter = collections.Counter()
    missing_reason = collections.Counter()
    norm_count = 0
    for it in items:
        base = plan.get(it["item_id"])
        it.pop("icon_note", None)
        it["icon"] = base
        if base is None:
            it["icon_state"] = "无图标字段"
            it["_media"] = {"total": 0, "images": []}
            it["icon_provenance"] = {
                "table": TABLE, "row_key": it["item_id"], "field": "icon",
                "state": "field-absent-or-empty",
            }
            state_counter["无图标字段"] += 1
            missing_reason["源表无该 item 行或 icon 字段为空"] += 1
            continue
        got = None
        src = None
        if base in pe and base in pe_written:
            suf, pack, row, fid, rel, norm_from = pe[base]
            w = pe_written[base]
            got = {"png": str(w["png"].relative_to(WEB)).replace("\\", "/"), "base": base,
                   "suffix": suf, "label": "图标", "pack": pack, "row": row, "fid": fid,
                   "resolved_path": rel, "width": w["w"], "height": w["h"],
                   "via": "PE .ktx：路径→fid→pe_index(包,行)→解码"}
            src = "PE"
        elif base in pc and base in pc_written:
            suf, prow, rel, norm_from = pc[base]
            w = pc_written[base]
            got = {"png": str(w["png"].relative_to(WEB)).replace("\\", "/"), "base": base,
                   "suffix": suf, "label": "图标", "pack": prow["pkg"], "row": int(prow["row"]),
                   "fid": prow["fid"], "resolved_path": rel, "width": w["w"], "height": w["h"],
                   "via": "PC .bc7：路径→hit_table(包,行)→E:/mrzh/res 解码"}
            src = "PC"
        else:
            norm_from = None
        if got and norm_from:
            got["path_normalized_from"] = base
            got["via"] += "；源表路径含重复 `ui/ui/` 段，归一后同名资源命中"
            norm_count += 1
        if got:
            it["icon_state"] = "已导出"
            if w.get("flat_white"):
                got["flat_white"] = True
                it["icon_note"] = "白模图标：包内 RGB 全白、只有 alpha 形状，运行时按色值染色（动作/舞蹈类常见）"
            it["_media"] = {"total": 1, "images": [got]}
            it["icon_provenance"] = {
                "table": TABLE, "row_key": it["item_id"], "field": "icon",
                "source_id": SOURCE_ID, "source_lock_sha256": table_sha,
                "locator": {k: got[k] for k in ("resolved_path", "pack", "row", "fid")},
                "media_source": src,
                "policy": "path→fid→(pack,row)→decode；无跨源字段 join，未用非本源图兜底",
            }
            state_counter["已导出"] += 1
        else:
            # 命中落点但没解出来 ⇒ 与「完全无落点」分开记
            if base in pe:
                it["icon_state"] = "未解出（解码失败）"
                state_counter["未解出（解码失败）"] += 1
                missing_reason["PE 落点命中但解码/自校验失败"] += 1
            elif base in pc:
                it["icon_state"] = "未解出（解码失败）"
                state_counter["未解出（解码失败）"] += 1
                missing_reason["PC 落点命中但解码失败"] += 1
            else:
                it["icon_state"] = "未下发"
                state_counter["未下发"] += 1
                missing_reason["PE(174 包) 与 PC(hit_table 133k) 均无该路径"] += 1
            it["_media"] = {"total": 0, "images": []}
            it["icon_provenance"] = {
                "table": TABLE, "row_key": it["item_id"], "field": "icon",
                "source_id": SOURCE_ID, "source_lock_sha256": table_sha,
                "locator": {"resolved_path": None, "pack": None, "row": None, "fid": None},
                "media_source": None,
                "policy": "路径在 PE/PC 两源均无落点，按未下发处理，不以其它图替代",
            }

    # 3) 磁盘回查：写盘失败/被删的降级
    downgraded = 0
    for it in items:
        imgs = it["_media"]["images"]
        if not imgs:
            continue
        if not (WEB / imgs[0]["png"]).is_file():
            it["_media"] = {"total": 0, "images": []}
            it["icon_state"] = "未解出（无 PNG）"
            state_counter["已导出"] -= 1
            state_counter["未解出（无 PNG）"] += 1
            downgraded += 1

    with_icon = sum(1 for it in items if it["_media"]["images"])
    flat_white_items = sum(1 for it in items if it.get("icon_note"))
    miss_bases = collections.Counter(it["icon"] for it in items
                                     if it["icon_state"] == "未下发" and it.get("icon"))
    miss_sample = [(it["item_id"], it["name"]) for it in items if it["icon_state"] == "未下发"]
    by_source = collections.Counter(it["_media"]["images"][0]["via"].split(" ")[0]
                                   for it in items if it["_media"]["images"])

    # 4) meta
    meta = meta_in
    meta["generated"] = datetime.date.today().isoformat()
    meta["card_mode"] = "roster"
    meta["card_summary"] = [["name", "名称"], ["item_id", "道具ID"], ["icon_state", "图标"]]
    meta["field_labels"] = FIELD_LABELS
    ic_stats = {
        "items_total": len(items),
        "items_with_icon": with_icon,
        "items_without_icon": len(items) - with_icon,
        "png_dir": "assets/item_icons/",
        "distinct_icon_paths": len(bases),
        "distinct_icon_paths_pe": len(pe),
        "distinct_icon_paths_pc_only": len(pc),
        "distinct_icons_exported": len(set(pe_written) | set(pc_written)),
        "by_source": dict(sorted(by_source.items())),
        "state_breakdown": dict(sorted(state_counter.items())),
        "missing_reasons": dict(sorted(missing_reason.items())),
        "pe_export_run": dict(sorted(pe_stats.items())),
        "pc_export_run": dict(sorted(pc_stats.items())),
        "downgraded_after_disk_check": downgraded,
        "flat_white_items": flat_white_items,
        "path_normalized_items": norm_count,
        "missing_reason": "icon 路径在 pe_index（174 个安卓热更包）与 PC 校准表（133,188 条路径）均无落点 ⇒ 按未下发处理；不以其它图替代",
    }
    meta["icon_stats"] = ic_stats
    meta.setdefault("state_summary", {})
    meta["icon_state_summary"] = dict(sorted(state_counter.items()))
    prov = meta.setdefault("provenance", {})
    prov["icon_binding"] = {
        "policy": "same-record icon field → path → fid → (pack,row) → decode",
        "cross_source_policy": "no-cross-source-field-join",
        "icon_field": "icon",
        "icon_table": TABLE,
        "icon_table_sha256": table_sha,
        "pe_index": "03_执行/30_分析/热更检测/pe_index.sqlite3（174 包 / 1,801,666 行）",
        "pc_table": "03_执行/30_分析/热更检测/pc_fid_calib/hit_table.csv（133,188 行路径）",
        "pc_pack_root": "E:/mrzh/res（只读）",
        "fallback_policy": "none（未使用 APK npk 图库或按名/按 id 借用，缺失即未下发）",
    }
    prov["source_locks"] = prov.get("source_locks") or []
    meta["notes"] = (
        "1,189 条 verified item self-ID；图标取自同表 icon 字段（同一条解码记录，非跨表字段 join）。"
        "PE .ktx 与 PC .bc7 双源定位，%d 条导出、%d 条未下发；未下发者 _media 留空，"
        "未以任何别名/近似图兜底。hide_in_bag 缺席仍保持 unresolved。"
    ) % (with_icon, len(items) - with_icon)

    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")

    # 5) 报告
    lines = [
        "# 道具总表图标补齐报告（item_master_v01）",
        "",
        "- 生成：%s" % meta["generated"],
        "- 板：`data/boards/item_master_v01.json`（%d 条）" % len(items),
        "- 图标目录：`assets/item_icons/`（%d 个 PNG）" % len(set(pe_written) | set(pc_written)),
        "",
        "## 总数 / 有图 / 未下发",
        "",
        "| 项 | 条数 |",
        "| --- | --- |",
        "| 总条数 | %d |" % len(items),
        "| 有图（已导出） | %d |" % with_icon,
        "| 未下发 | %d |" % state_counter.get("未下发", 0),
        "| 未解出（解码失败/无 PNG） | %d |" % (state_counter.get("未解出（解码失败）", 0) + state_counter.get("未解出（无 PNG）", 0)),
        "| 无图标字段 | %d |" % state_counter.get("无图标字段", 0),
        "",
        "## 双源命中",
        "",
        "| 来源 | 条数 | 说明 |",
        "| --- | --- | --- |",
        "| PE .ktx | %d | `icon`+`_b`/`_s`+`.ktx` → fid → pe_index(pack,row) → 解压/解码 |" % by_source.get("PE", 0),
        "| PC .bc7 | %d | PE 未命中者再查 hit_table(path→pkg,row) → E:/mrzh/res 解 BC7 |" % by_source.get("PC", 0),
        "| 未下发 | %d | 两源均无该路径 |" % state_counter.get("未下发", 0),
        "",
        "去重口径：不同 icon 路径 %d 条（PE 有落点 %d、PC 补 %d），实际写盘 PNG %d 个（多 item 共用同一图只写一次）。"
        % (len(bases), len(pe), len(pc), len(set(pe_written) | set(pc_written))),
        "",
        "## 失败原因分类",
        "",
        "| 原因 | 条数 |",
        "| --- | --- |",
    ]
    for k, v in sorted(missing_reason.items(), key=lambda kv: -kv[1]):
        lines.append("| %s | %d |" % (k, v))
    lines += [
        "",
        "### 未下发集中度（按 icon 路径聚合）",
        "",
        "| icon 路径 | 道具数 |",
        "| --- | --- |",
    ]
    for base, n in miss_bases.most_common(10):
        lines.append("| `%s` | %d |" % (base, n))
    lines += [
        "",
        "未下发样例：%s" % "、".join("%s(%d)" % (nm, iid) for iid, nm in miss_sample[:10]),
    ]
    lines += [
        "",
        "## 已知现象（非缺陷）",
        "",
        "- 白模图标 %d 条：包内 RGB 全白、只有 alpha 形状（动作/舞蹈类道具），运行时按色值染色；"
        "板上以 `icon_note` 标注，未做任何重上色。" % flat_white_items,
        "- 源表路径含重复 `ui/ui/` 段的 %d 条：仅去掉重复段后同名资源确实存在才采用，"
        "记录 `_media.images[0].path_normalized_from`；未改 icon 名。" % norm_count,
        "",
        "PE 导出运行计数：`%s`" % json.dumps(dict(sorted(pe_stats.items())), ensure_ascii=False),
        "",
        "PC 导出运行计数：`%s`" % json.dumps(dict(sorted(pc_stats.items())), ensure_ascii=False),
        "",
        "## 口径说明",
        "",
        "- 图标字段与 item_master 同表同记录：`com\\cdata\\common_item_data_base.py` 的 `icon`，不做跨表字段 join。",
        "- `_media.images[i]` 记录 `png/base/suffix/pack/row/fid/resolved_path/width/height/via`，可逐条回溯到包内行。",
        "- 未下发项 `_media.images=[]`、`icon_state=\"未下发\"`；未使用 APK npk 图库或同名/同 id 图标兜底（其 fid 口径与路径哈希不通，按图匹配无法建立 1:1 归属）。",
        "- `evidence / evidence_level / status_tags / provenance` 原样保留（status_tags 取值域由 publication_policy 冻结）。",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("items=%d with_icon=%d missing=%d png=%d PE=%d PC=%d" % (
        len(items), with_icon, len(items) - with_icon,
        len(set(pe_written) | set(pc_written)), by_source.get("PE", 0), by_source.get("PC", 0)))
    print("state:", dict(sorted(state_counter.items())))
    print("pe_run:", dict(sorted(pe_stats.items())))
    print("pc_run:", dict(sorted(pc_stats.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
