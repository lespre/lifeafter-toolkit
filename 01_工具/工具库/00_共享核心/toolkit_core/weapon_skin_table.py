"""武器皮肤列表加载模块 —— 一键构建武器皮肤全量表（名字/模型/类型/品级/版本状态）。

用法：
    from toolkit_core.weapon_skin_table import build_weapon_skin_table, export_csv
    rows = build_weapon_skin_table(doc_entries, root_entries, item_rows_path)
    export_csv(rows, "weapon_skin_全量.csv")

数据源（2026-08-29 验证）：
    - weapon_skin_data（base+chs，py314 精拆 entries）
    - weapon_skin_sfx_function_data（特效名补充）
    - weapon_skin_behavior_res_data（深层预告）
    - common_item_data（道具表 item_id==skin_id = 名字正源）
"""
from __future__ import annotations

import csv
import json
import re
import struct
from pathlib import Path

from toolkit_core.bindict_table import parse_legacy_chs_pool, parse_chs_pool, decode_table_rows

# skin_XXXX 前缀 ↔ 武器类型（用户确认 + 名字自证）
TYPE_NAMES = {
    "1001": "突击步枪", "1002": "狙击枪", "1003": "手枪", "1006": "霰弹枪",
    "1007": "弓箭", "1008": "电磁机枪", "1012": "榴弹炮", "1013": "喷火器",
    "2003": "冷兵器", "2004": "冷兵器", "2005": "冷兵器", "2006": "护臂/盾",
}
# level 字段品级名（6=传世升格、5=典藏/联动）
GRADE_NAMES = {"2": "品级2", "3": "品级3", "4": "品级4", "5": "典藏/联动", "6": "传世(升格)"}
SFX_SUFFIXES = ("命中特效", "弹道特效", "音效", "特效")


def _parse_pool(data: bytes) -> list[str] | None:
    if data[:2] == b"tI" and len(data) > 6:
        plen = struct.unpack_from("<I", data, 2)[0]
        if 6 + plen <= len(data):
            data = data[6 + plen:]
    try:
        return parse_legacy_chs_pool(data)
    except Exception:
        pass
    x = data.find(b"x{")
    if x >= 0:
        ln = struct.unpack_from("<I", data, x + 2)[0]
        try:
            return parse_chs_pool(data[x + 6:x + 6 + ln])
        except Exception:
            pass
    return None


def _load_table(entries_dir: Path, base_entry: int, chs_entry: int):
    data = (entries_dir / f"{base_entry:06d}.bin").read_bytes()
    x = data.find(b"x{")
    if x < 0:
        return []
    ln = struct.unpack_from("<I", data, x + 2)[0]
    body = data[x + 6:x + 6 + ln]
    pool = _parse_pool((entries_dir / f"{chs_entry:06d}.bin").read_bytes())
    try:
        rows, _ = decode_table_rows(body, pool if pool else [])
        return rows
    except Exception:
        return []


def _get(v: dict, k: str):
    item = v.get(k)
    return item[1] if item else None


def _sfx_names(rows) -> dict[int, set[str]]:
    names = {}
    for r in rows:
        nm = _get(r["values"], "sfx_name")
        sid = _get(r["values"], "skin_id")
        if isinstance(nm, str) and sid:
            base = nm
            for suf in SFX_SUFFIXES:
                base = base.replace(suf, "")
            if base:
                names.setdefault(sid, set()).add(base)
    return names


def build_weapon_skin_table(doc_entries: Path | str, root_entries: Path | str,
                            item_rows_path: Path | str | None = None,
                            doc_entries_: tuple[int, int, int, int] = (11762, 21081, 18154, 9049),
                            root_entries_: tuple[int, int, int, int] = (49069, 87558, 75639, 38461),
                            behavior_entries: tuple[int, int] = (15858, 22893),
                            behavior_only: tuple[int, ...] = (1110184, 1110186, 1110190)) -> list[dict]:
    """构建武器皮肤全量表。

    doc/root = 新旧版本 entries 目录；返回行列表（dict），字段与 v4 导出一致。
    """
    doc, root = Path(doc_entries), Path(root_entries)

    # 1) 道具表名字（正源：item_id == skin_id）
    item_names: dict[int, dict] = {}
    if item_rows_path:
        for r in json.loads(Path(item_rows_path).read_text(encoding="utf-8"))["rows"]:
            iid, nm, desc = r.get("id"), r.get("name"), r.get("desc")
            if isinstance(iid, int) and str(iid).startswith("1110") and isinstance(nm, str) and nm:
                item_names[iid] = {"name": nm, "desc": desc}

    # 2) 皮肤表 + 特效表
    doc_skin = {r["key"]: r for r in _load_table(doc, *doc_entries_[:2])}
    root_skin = {r["key"]: r for r in _load_table(root, *root_entries_[:2])}
    doc_sfx = _load_table(doc, *doc_entries_[2:])
    sfx_names = _sfx_names(doc_sfx)

    # 3) 深层预告（behavior_res 仅资源）
    deep: dict[int, dict] = {}
    beh = _load_table(doc, *behavior_entries)
    for r in beh:
        if r["key"] not in behavior_only:
            continue
        v = r["values"]
        sfx = sorted({str(vv[1]).split("/")[-1] for vv in v.values()
                      if vv and isinstance(vv[1], str) and vv[1].endswith(".sfx")})
        mp = ""
        m = re.search(r"skin_(\d{4})_(\d{3})", " ".join(sfx))
        if m:
            mp = f"weapon/skin/skin_{m.group(1)}_{m.group(2)}/skin_{m.group(1)}_{m.group(2)}.gim"
        deep[r["key"]] = {"model": mp, "sfx": "、".join(sfx)}

    # 4) 合并
    rows = []
    for k in sorted(set(doc_skin) | set(root_skin) | set(deep)):
        if k in deep:
            m = re.search(r"skin_(\d{4})", deep[k]["model"])
            rows.append({"skin_id": k, "name": "", "name_src": "行为资源(深层预告)",
                         "model_path": deep[k]["model"], "status": "★8-29新增(仅行为资源)",
                         "level": "", "grade": "", "type": "",
                         "type_name": TYPE_NAMES.get(m.group(1), "") if m else "",
                         "detail": "特效: " + deep[k]["sfx"]})
            continue
        in_doc, in_root = k in doc_skin, k in root_skin
        status = "两个版本都有" if (in_doc and in_root) else ("★8-29新增" if in_doc else "8-27有/8-29删")
        r = doc_skin.get(k) or root_skin.get(k)
        v = r["values"]
        name, src = "", ""
        if k in item_names:
            name, src = item_names[k]["name"], "道具表"
        elif k in sfx_names:
            name, src = "、".join(sorted(sfx_names[k])), "特效表"
        mp = _get(v, "model_path") or ""
        m = re.search(r"skin_(\d{4})", mp)
        lv = _get(v, "level")
        rows.append({"skin_id": k, "name": name, "name_src": src, "model_path": mp,
                     "status": status, "level": lv,
                     "grade": GRADE_NAMES.get(str(lv), ""), "type": _get(v, "weapon_type"),
                     "type_name": TYPE_NAMES.get(m.group(1), "") if m else "",
                     "detail": (item_names.get(k, {}).get("desc", "") or "")[:80]})
    return rows


def export_csv(rows: list[dict], path: Path | str, header: list[str] | None = None) -> Path:
    """导出 CSV（utf-8-sig，Excel 友好）。注意：Excel 打开时写会 PermissionError，换新文件名。"""
    header = header or ["skin_id", "名字", "名字来源", "model_path", "版本状态", "品级", "品级名",
                        "武器类型(type)", "武器类型名", "特效/描述"]
    out = Path(path)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in ["skin_id", "name", "name_src", "model_path", "status",
                                               "level", "grade", "type", "type_name", "detail"]])
    return out
