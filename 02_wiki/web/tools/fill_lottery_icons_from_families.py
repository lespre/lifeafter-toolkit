#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B 层补图：奖池板上「不在 common_item 图标索引里」的 id，去各自家族表取 icon 字段。

输入：01_索引与产物/30_分析/lottery_icon_field_sweep.json
      （fill_lottery_icons_field_sweep.py 扫全表产出：id → [(表, 字段, 值)]，值只收 ui/ 与 jump:）
做法：按家族优先级挑第一个可用的 icon 字段 → 解 jump 组（R.jump_values 等价：
      bindict_table.resolve_jump_group + 表内 chs 池）→ 定位 41_还原树/pe/资源 下的 .ktx
      → CompBlks / KTX 解码 → 写 02_wiki/web/assets/lottery_icons/<id>.png

家族优先级（先专表后泛表）：
  涂装 equip_coating_data.coating_icon     时装 fashion_data.icons / simple_fashion_data.icons
  礼包 gift_data.icon / gift_data.icons     配方 recipe.icon
  代币 token_icon_data.icon_path           外观模块 player_module_appear_data.icon
  奖池展示 nt_lottery_item_show_conf_data  img_path/small_img_path
只读 PE 源；不改 41_还原树；不改板；已存在 png 跳过。
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = WEB / "assets/lottery_icons"
SWEEP = PROJ / "01_索引与产物/30_分析/lottery_icon_field_sweep.json"
REPORT = PROJ / "01_索引与产物/30_分析/lottery_icons_fill_families_report.json"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core import android_gpk as AG  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa: E402
import decoders as DEC  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

# (表, 字段) 优先级：越靠前越权威
PRIORITY = [
    ("equip_coating_data", "coating_icon"),
    ("gift_data", "icon"),
    ("gift_data", "icons"),
    ("fashion_data", "icons"),
    ("simple_fashion_data", "icons"),
    ("simple_fashion_data", "name"),
    ("recipe", "icon"),
    ("token_icon_data", "icon_path"),
    ("player_module_appear_data", "icon"),
    ("player_module_appear_data_for_export", "icon"),
    ("nt_lottery_item_show_conf_data", "img_path"),
    ("nt_lottery_item_show_conf_data", "small_img_path"),
    ("common_hd_reward_preview_data", "prop_icon"),
    ("monster_transform_data", "head_icon_path"),
    ("fashion_diy_lottery_pool_map_data", "style_icon"),
    ("infrastruct_building_data", "icon"),
    ("record_label_suit_data", "img"),
    ("gift_data", "present_path"),
]
SUFFIXES = ("", "_b", "_s", "_max", "_mid", "_l", "_sq")

_tbl_cache: dict[str, tuple[bytes, list[str]]] = {}


def _xbody(p: Path) -> bytes | None:
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def _table(name: str):
    if name in _tbl_cache:
        return _tbl_cache[name]
    body = _xbody(CD / f"{name}.py")
    if body is None:
        _tbl_cache[name] = (b"", [])
        return _tbl_cache[name]
    cp = CD / f"{name}_chs.py"
    pool = parse_legacy_chs_pool(cp.read_bytes()) if cp.exists() else []
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    _tbl_cache[name] = (blob, pool)
    return _tbl_cache[name]


def jump_group(table: str, value: str) -> list[str]:
    blob, pool = _table(table)
    if not blob or not value.startswith("jump:"):
        return []
    t = int(value.split(":")[1])
    if not (0 <= t < len(blob) - 2):
        return []
    kind = blob[t + 1]
    vals = resolve_jump_group(blob, t) or []
    if kind == 0x05:
        return [pool[x] if x < len(pool) else "" for x in vals]
    return [str(v) for v in vals]


def icon_paths(table: str, value: str) -> list[str]:
    """字段值 → 候选 ui/ 路径列表（jump 组可能给多条，取第一条 ui/ 的）。"""
    if not isinstance(value, str):
        return []
    vals = jump_group(table, value) if value.startswith("jump:") else [value]
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        for s in (v,) if isinstance(v, str) else ():
            if s.lower().endswith((".png", ".ktx", ".csb", ".jpg")):
                s = s.rsplit(".", 1)[0]
            if s.startswith("ui/"):
                out.append(s)
    return out


def find_asset(rel: str):
    """rel = 无扩展名 ui/ 路径 → (真实文件, 是否靠变体模糊匹配)。

    精确档位优先（_b 横幅 > _s 小图 > 裸名 > _max/_mid）；
    找不到时按 <name>* 做变体模糊匹配（同一件东西的 _1/_2/_3 分帧，≤6 个候选才认）。
    """
    base = rel.replace("/", "\\")
    p = RES / base
    for suf in SUFFIXES:
        c = p.with_name(p.name + suf + ".ktx")
        if c.exists():
            return c, False
        c = p.with_name(p.name + suf + ".png")
        if c.exists():
            return c, False
    if not p.parent.exists():
        return None, True
    stem = p.name
    stems = [stem]
    if "_" in stem and stem.rsplit("_", 1)[1].isdigit():
        stems.append(stem.rsplit("_", 1)[0])  # icon_367196_3 → 再试 icon_367196
    cands = []
    for st in stems:
        try:
            cands = sorted(q for q in p.parent.glob(st + "_*")
                           if q.suffix.lower() in {".ktx", ".png"} and q.stem != stem)
        except OSError:
            cands = []
        if cands:
            stem = st
            break
    if not cands or len(cands) > 6:
        return None, True
    want_idx = None
    orig = p.name
    if "_" in orig and orig.rsplit("_", 1)[1].isdigit():
        want_idx = orig.rsplit("_", 1)[1]
    ranked = []

    def rank(q: Path):
        s = q.stem
        same = 1 if (want_idx and f"_{want_idx}" in s) else 0
        tier = 3 if s.endswith("_b") else (2 if s.endswith("_s") else 1)
        idx = 0
        tail = s[len(stem) + 1:] if s.startswith(stem + "_") else ""
        num = tail.split("_")[0]
        if num.isdigit():
            idx = int(num)
        return (-same, -tier, idx)

    ranked = sorted(cands, key=rank)
    return ranked[0], True


def decode_bytes(data: bytes) -> np.ndarray:
    if data.startswith(b"CompBlks"):
        arr = DEC.decode_compblks(data)
        if arr is None:
            raise ValueError("decode_compblks None")
        return np.asarray(arr)
    info = AG.parse_ktx(data)
    if not info:
        raise ValueError("parse_ktx empty")
    return np.asarray(AG._ktx_rgba(data, info))


def magenta_ratio(a: np.ndarray) -> float:
    if a.ndim != 3 or a.shape[2] < 3:
        return 1.0
    op = a[..., 3] > 8 if a.shape[2] == 4 else np.ones(a.shape[:2], bool)
    n = int(op.sum())
    if n == 0:
        return 1.0
    px = a[op]
    m = (px[:, 0] > 240) & (px[:, 1] < 16) & (px[:, 2] > 240)
    return float(m.mean())


def build_namejoin() -> dict[str, tuple[str, str]]:
    """gift_data：name → (key, icon)。板上自选箱/典藏盒常与礼包表同名但 key 不同。"""
    body = _xbody(CD / "gift_data.py")
    if body is None:
        return {}
    cp = CD / "gift_data_chs.py"
    pool = parse_legacy_chs_pool(cp.read_bytes()) if cp.exists() else []
    try:
        rows, _ = decode_table_rows_with_chs_slots(body, pool)
    except Exception:  # noqa: BLE001
        return {}
    out: dict[str, tuple[str, str]] = {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r["values"].items()}
        nm, ic = v.get("name"), v.get("icon")
        if isinstance(nm, str) and isinstance(ic, str) and ic.startswith("ui/"):
            out.setdefault(nm, (str(r["key"]), ic))
    return out


def main() -> int:
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    hits: dict[str, list[dict]] = sweep["hits"]

    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ids = list(dict.fromkeys(str(i["item_id"]) for i in board["items"]
                             if isinstance(i, dict) and i.get("item_id")))
    names = {}
    for i in board["items"]:
        if isinstance(i, dict) and i.get("item_id"):
            names.setdefault(str(i["item_id"]), i.get("name") or "")

    OUT.mkdir(parents=True, exist_ok=True)
    namejoin = build_namejoin()
    rep = {"candidates": 0, "exported": 0, "fuzzy": 0, "by_source": {}, "fail_no_icon": [],
           "fail_no_asset": [], "fail_decode": [], "fail_bad": [], "detail": []}

    for iid in ids:
        tgt = OUT / f"{iid}.png"
        if tgt.exists():
            continue
        rows = hits.get(iid) or []
        if not rows:
            continue
        rep["candidates"] += 1
        chosen = None
        for tbl, field in PRIORITY:
            for h in rows:
                if h["table"] == tbl and h["field"] == field:
                    paths = icon_paths(tbl, h["value"])
                    if paths:
                        chosen = (tbl, field, paths[0], h["value"])
                        break
            if chosen:
                break
        if chosen:
            tbl, field, rel, rawval = chosen
        else:
            alt = namejoin.get(names.get(iid, ""))
            if alt and alt[0] != iid:
                tbl, field, rel, rawval = "gift_data", f"name-join:{alt[0]}", alt[1], alt[1]
            else:
                rep["fail_no_icon"].append(iid)
                continue
        src, fuzzy = find_asset(rel)
        if src is None:
            # 兜底：同一张礼包表里按「同名」找另一行（自选箱/典藏盒常是多 key 同图）
            alt = namejoin.get(names.get(iid, ""))
            if alt and alt[0] != iid and alt[1] != rel:
                src, fuzzy = find_asset(alt[1])
                if src is not None:
                    tbl, field, rel, rawval = "gift_data", f"name-join:{alt[0]}", alt[1], alt[1]
        if src is None:
            rep["fail_no_asset"].append({"id": iid, "table": tbl, "field": field, "path": rel})
            continue
        try:
            arr = decode_bytes(src.read_bytes())
        except Exception as exc:  # noqa: BLE001
            rep["fail_decode"].append({"id": iid, "path": rel, "err": type(exc).__name__})
            continue
        if arr.ndim != 3 or arr.shape[2] != 4 or int((arr[..., 3] > 8).sum()) < 16:
            rep["fail_bad"].append({"id": iid, "path": rel, "why": "bad_rgba"})
            continue
        if magenta_ratio(arr) > 0.30:
            rep["fail_bad"].append({"id": iid, "path": rel, "why": "magenta"})
            continue
        Image.fromarray(np.ascontiguousarray(arr.astype("uint8"))).save(tgt)
        rep["exported"] += 1
        if fuzzy:
            rep["fuzzy"] += 1
        key = f"{tbl}.{field}"
        rep["by_source"][key] = rep["by_source"].get(key, 0) + 1
        rep["detail"].append({"id": iid, "name": names.get(iid, ""), "from": key,
                              "value": rawval if len(str(rawval)) < 90 else str(rawval)[:90],
                              "asset": str(src).replace(str(RES) + "\\", ""),
                              "fuzzy": bool(fuzzy),
                              "size": f"{arr.shape[1]}x{arr.shape[0]}"})

    rep["fail_no_icon_n"] = len(rep["fail_no_icon"])
    rep["fail_no_asset_n"] = len(rep["fail_no_asset"])
    rep["fail_decode_n"] = len(rep["fail_decode"])
    rep["fail_bad_n"] = len(rep["fail_bad"])
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"B层: cand={rep['candidates']} exported={rep['exported']} "
          f"no_icon={rep['fail_no_icon_n']} no_asset={rep['fail_no_asset_n']} "
          f"decode={rep['fail_decode_n']} bad={rep['fail_bad_n']}")
    print("来源:", json.dumps(rep["by_source"], ensure_ascii=False))
    for k in ("fail_no_asset", "fail_decode", "fail_bad"):
        for s in rep[k][:8]:
            print("  ", k, s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
