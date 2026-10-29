# -*- coding: utf-8 -*-
"""补全时装板的「捏脸」桶：把捏脸预设表里的成品脸做成卡，并配 PE 图。

═══════════════════════════════════════════════════════════════════════════
★ 现状

  板上「捏脸」只有 22 张，全部来自 `player_appear_data` part=2 的**基础脸型**
  （鹅蛋脸 / 婴儿脸 / 扑克脸…）。捏脸系统真正的**成品预设**有两套表，一张都没进板：

  1. `fashion_preset_do_face_config_data`（28 行）—— 品牌/联动捏脸
     有 name（敦煌飞天 / 幻紫晶芒 / 红莲业火…）+ face_icon_0/1（女/男图标）
     + brand_id + face_group + order
  2. `do_face_v4_preset_data`（21 行）—— v4 预设（游戏里"一键套用"的整脸）
     无 name，靠 `img_path` 的 `new4_icon_yushe_<NNN>_<f|m>` 编号配对，
     NNN 相同的女/男是同一套预设

★ 做法

  · brand 28 行 → 28 张卡（一卡男女两图）
  · v4 21 行 → 按 yushe 编号合并成 11 张卡（一卡男女两图）
  · 图标路径直接来自表字段，PE 三档取图（_b/_s/无），取不到就留缺图标记
  · 卡 id 用稳定可读写法：`fw_facepreset_brand_<key>` / `fw_facepreset_v4_<NNN>`
  · 幂等：同 id 的卡已存在就跳过（--force 才重刷）

★ 用法
    python add_face_preset_cards.py --dry
    python add_face_preset_cards.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"
OUT = WEB / "assets/fashion_posters"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402

YUSHE_RE = re.compile(r"yushe_(\d+)", re.I)


def group_strings(blob, pool, off, depth=0):
    if depth > 6:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    kind, els = g
    out = []
    if kind == 0x0B:
        for e in els:
            out.extend(group_strings(blob, pool, e, depth + 1))
    elif kind == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                out.append(pool[e])
    return out


def fval(v, blob, pool):
    if isinstance(v, tuple) and len(v) == 2:
        if str(v[1]).startswith("jump:"):
            try:
                return group_strings(blob, pool, int(str(v[1]).split(":")[1]))
            except Exception:
                return []
        return [v[1]]
    return [v]


def load(stem: str):
    p = CD / (stem + ".py")
    if not p.is_file():
        return []
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0 or at > 4096:
        return []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    if len(body) < 12:
        return []
    cnt = struct.unpack_from("<I", body, 0)[0]
    if cnt <= 0 or cnt > 900000:
        return []
    blob = body[8 + 4 * cnt:]
    cp = CD / (stem + "_chs.py")
    pool = []
    if cp.is_file():
        try:
            pool = BT.parse_legacy_chs_pool(cp.read_bytes())
        except Exception:
            pool = []
    try:
        rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    except Exception:
        return []
    out = []
    for r in rows:
        out.append({"key": r["key"],
                    **{k: fval(v, blob, pool) for k, v in r["values"].items()}})
    return out


def to_icon(path: str) -> str:
    return (path or "").strip().rsplit(".", 1)[0]


def fetch(conn, icon_base: str, dst_stem: str):
    """按图标基名取图，返回 (assets 相对路径 or None, 实际路径)。"""
    for suf in ("_b", "_s", ""):
        try:
            r = pe_fetch.resolve(icon_base, suf, conn)
        except Exception:
            r = None
        if r:
            dst = OUT / (dst_stem + ".png")
            if dst.exists():
                dst.unlink()
            try:
                ok = pe_fetch.export(r[0], dst)
            except Exception:
                ok = False
            if ok and dst.is_file() and dst.stat().st_size > 512:
                return "assets/fashion_posters/" + dst.name, r[0]
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    have = {it["id"] for it in board["items"]}
    conn = pe_fetch.con()
    OUT.mkdir(parents=True, exist_ok=True)

    specs = []   # (id, name, kind, src_table, row_keys, [(label, icon_path)])

    # ── 1) 品牌/联动捏脸
    for r in load("fashion_preset_do_face_config_data"):
        nm = (r.get("name") or [""])[0]
        if not nm:
            continue
        icons = []
        f0 = (r.get("face_icon_0") or [""])[0]
        f1 = (r.get("face_icon_1") or [""])[0]
        if f0:
            icons.append(("女", f0))
        if f1:
            icons.append(("男", f1))
        if not icons:
            continue
        specs.append(("fw_facepreset_brand_%s" % r["key"], nm, "品牌联动",
                      "fashion_preset_do_face_config_data", [r["key"]], icons))

    # ── 2) v4 预设（按 yushe 编号合并男女）
    v4: dict = {}
    for r in load("do_face_v4_preset_data"):
        img = (r.get("img_path") or [""])[0]
        m = YUSHE_RE.search(img)
        if not m:
            continue
        num = m.group(1)
        g = (r.get("gender") or [0])[0]
        rec = v4.setdefault(num, {"keys": [], "icons": {}, "hair": None, "fashion": None})
        rec["keys"].append(r["key"])
        rec["icons"]["男" if g == 1 else "女"] = img
        if r.get("hair_id"):
            rec["hair"] = (r.get("hair_id") or [None])[0]
        if r.get("fashion_id"):
            rec["fashion"] = (r.get("fashion_id") or [None])[0]
    for num in sorted(v4, key=int):
        rec = v4[num]
        icons = [(lb, rec["icons"][lb]) for lb in ("女", "男") if lb in rec["icons"]]
        specs.append(("fw_facepreset_v4_%s" % num, "预设%s" % num, "预设",
                      "do_face_v4_preset_data", sorted(rec["keys"]), icons))

    new_cards = []
    stat = {"拟建": len(specs), "已存在跳过": 0, "有图": 0, "缺图": 0}
    for cid, nm, kind, table, keys, icons in specs:
        if cid in have and not a.force:
            stat["已存在跳过"] += 1
            continue
        imgs, icon_all = [], []
        for i, (lb, ip) in enumerate(icons):
            base = to_icon(ip)
            rel = icon_p = None
            if not a.dry:
                rel, icon_p = fetch(conn, base, "%s_%s" % (cid, "f" if lb == "女" else "m"))
            else:
                rel = "(dry)"
            if rel:
                stat["有图"] += 1
                imgs.append({"png": rel, "base": base, "label": lb,
                             "source": "PE · %s（%s）" % (ip, table),
                             "fetch": "pe"})
                icon_all.append({"path": base, "gender": lb, "png": rel})
            else:
                stat["缺图"] += 1
        if a.dry:
            continue
        card = {
            "id": cid,
            "name": nm,
            "part": "捏脸",
            "part_label": "捏脸",
            "part_bucket": ["捏脸"],
            "face_kind": kind,
            "part_source": table,
            "gender": "/".join(lb for lb, _ in icons),
            "row_keys": keys,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "捏脸预设表 %s（逐行解码）" % table,
            "status_tags": ["static config"],
            "name_visible": True,
            "icon_state": "有图" if imgs else "缺图",
            "icon_count": len(imgs),
            "icons_all": icon_all,
            "_media": {"images": imgs, "total": len(imgs)},
            "provenance": {
                "source_id": "face-preset-%s" % table,
                "table": "com\\cdata\\%s.py" % table,
                "row_key": keys[0],
                "row_keys": keys,
                "field_refs": (["name", "face_icon_0", "face_icon_1"]
                               if table.startswith("fashion_preset") else
                               ["img_path", "gender", "hair_id", "fashion_id"]),
                "rebuild": "face-preset-import-20261029",
            },
        }
        new_cards.append(card)

    print("=== 捏脸预设 ===")
    for k, v in stat.items():
        print("  %-10s %d" % (k, v))
    for c in new_cards[:8]:
        print("   %-28s %-10s %-6s %s" % (c["id"], c["name"], c["face_kind"],
                                          [i["png"] for i in c["_media"]["images"]]))
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    if new_cards:
        board["items"].extend(new_cards)
    ts = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_face" % ts))
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_face" % ts))
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("新增 %d 张，板内共 %d 张" % (len(new_cards), len(board["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
