# -*- coding: utf-8 -*-
"""给时装板里「其他外观」类条目补图标（挂饰 / 戒指 / 半感染者花苞 / 面饰 / 发型…）。

这些条目来自 player_appear_data（part 1~7），表里**没有 icons 字段**，
所以之前的取图链路（fashion_data.icons）对它们完全无效，整桶 0 图。

图标资源靠「模型路径反推命名族」拿到：
  character/ring/ring_1008/ring_1008.gim        → ui/item_icon/icon_ring_1008
  character/monsters/cloth_3499_hua/...gim      → ui/item_icon/icon_hua_3499
  character/pendant/pendant_068/pendant_068.gim → ui/item_icon/icon_pendant_068（包内不存在）

命中就用 pe_fetch 实导到 assets/fashion_posters/<卡id>.png，写回 icons_all / _media。
命中不了的不造假图，原样保留缺图标记。

用法：
    python fill_appearance_icons.py --dry       # 只统计，不写盘
    python fill_appearance_icons.py             # 落盘
    python fill_appearance_icons.py --buckets 挂饰,戒指,半感染者花苞
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"
OUT = WEB / "assets/fashion_posters"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402

ICON_BASE = "ui/item_icon/"


def load_appear_rows() -> dict:
    """player_appear_data 全表：row_key → {models, name, part}"""
    raw = (CD / "player_appear_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / "player_appear_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]

    def gs(off: int) -> list:
        g = BT.read_27_group(blob, off)
        if not g:
            return []
        kind, els = g
        out = []
        if kind == 0x0B:
            for e in els:
                out.extend(gs(e))
        elif kind == 0x05:
            for e in els:
                if 0 <= e < len(pool):
                    out.append(pool[e])
        return out

    def iv(v):
        return v[1] if isinstance(v, tuple) else v

    out = {}
    for r in rows:
        val = r["values"]
        models: list = []
        for fld in ("socket_models", "high_model_name", "model_name"):
            vv = val.get(fld)
            if isinstance(vv, tuple) and "jump" in str(vv[1]):
                try:
                    models += gs(int(str(vv[1]).split(":")[1]))
                except Exception:
                    pass
            elif isinstance(vv, tuple) and str(vv[1]).endswith((".gim", ".mesh", ".gis")):
                models.append(str(vv[1]))
        out[str(r["key"])] = {"models": models, "name": iv(val.get("name")),
                              "part": iv(val.get("part"))}
    return out


# 模型字段填错 / 通用件：显式指定图标（按部位+名称精确匹配）
SPECIAL_ICON = {
    ("半感染者花苞", "花朵"): "icon_hua_moren",   # 默认花苞；表里 socket_models 误填成 ring_1001
    # 2026-10-29 补：这行 row_key 70892/170892 就是 player_appear_race_ctrl_data
    # key=1330000「默认」，该表自带 icon_path = ui/item_icon/icon_hua_moren_b.png
    ("半感染者花苞", "控制器"): "icon_hua_moren",
}


# 每个部位桶只认自己那一族图标前缀，避免「表里模型字段填错」导致张冠李戴
BUCKET_RULES = {
    "戒指": ("icon_ring_",),
    "半感染者花苞": ("icon_hua_",),
    "挂饰": ("icon_pendant_",),
    "面饰": ("icon_face_", "icon_"),
    "发饰": ("icon_hair_", "icon_h_"),
}


def icon_candidates(models: list, allow=None, row_keys=None) -> list:
    """模型路径 → 候选图标基名（有序，去重）。allow 不为空时只保留这些前缀。"""
    cands: list = []

    def add(x):
        if not x:
            return
        if allow and not any(x.startswith(p) for p in allow):
            return
        if x not in cands:
            cands.append(x)

    for m in models:
        s = str(m).replace("\\", "/")
        stem = s.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        # 戒指：character/ring/ring_1008/ring_1008
        mm = re.search(r"/ring/ring_(\d+)", s)
        if mm:
            add("icon_ring_" + mm.group(1))
        # 花苞：cloth_3499_hua
        mm = re.search(r"cloth_(\d+)_hua", s)
        if mm:
            add("icon_hua_" + mm.group(1))
        # 挂饰：pendant_068
        mm = re.search(r"/pendant/pendant_(\d+)", s)
        if mm:
            add("icon_pendant_" + mm.group(1))
        # 控制器等：controller_1001
        mm = re.search(r"^(controller)_(\d+)$", stem)
        if mm:
            add("icon_%s_%s" % (mm.group(1), mm.group(2)))
        # 兜底：目录名 + 数字
        mm = re.search(r"^([a-z_]+?)_(\d+)$", stem)
        if mm:
            add("icon_%s_%s" % (mm.group(1), mm.group(2)))
    # ⚠ 不要按「行键编号」猜图标（icon_{row_key}）：挂饰桶实测能命中 8 个，
    #   但导出的图是炸弹、时装宣传图 —— 那是别的道具占了同一编号，属张冠李戴。
    return cands


def probe(conn, base: str):
    """返回 (完整路径, 后缀, 行) 或 None。"""
    for suf in ("_b", "_s", ""):
        try:
            r = pe_fetch.resolve(ICON_BASE + base, suf, conn)
        except Exception:
            r = None
        if r:
            return r[0], suf, r[2]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--buckets", default="挂饰,戒指,半感染者花苞")
    a = ap.parse_args()
    want = {x.strip() for x in a.buckets.split(",") if x.strip()}

    appear = load_appear_rows()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    conn = pe_fetch.con()
    OUT.mkdir(parents=True, exist_ok=True)

    stat: dict = {}
    filled = []
    for it in board["items"]:
        bucket = (it.get("part_bucket") or [None])[0]
        if want and bucket not in want:
            continue
        st = stat.setdefault(bucket, {"卡": 0, "有图跳过": 0, "补上": 0, "无图标": 0})
        st["卡"] += 1
        if (it.get("_media") or {}).get("images"):
            st["有图跳过"] += 1
            continue
        models: list = []
        for rk in (it.get("row_keys") or []):
            models += (appear.get(str(rk)) or {}).get("models") or []
        if not models:
            st["无图标"] += 1
            continue
        hit = None
        allow = BUCKET_RULES.get(bucket)
        forced = SPECIAL_ICON.get((bucket, it.get("name")))
        cands = [forced] if forced else icon_candidates(models, allow, it.get("row_keys"))
        for base in cands:
            hit = probe(conn, base)
            if hit:
                hit = (base,) + hit
                break
        if not hit:
            st["无图标"] += 1
            continue
        base, full, suf, _row = hit
        dst = OUT / (str(it["id"]) + ".png")
        if not a.dry:
            if dst.exists():
                dst.unlink()
            try:
                ok = pe_fetch.export(ICON_BASE + base + suf, dst)
            except Exception:
                ok = False
            if not (ok and dst.is_file() and dst.stat().st_size > 512):
                st["无图标"] += 1
                continue
        rel = "assets/fashion_posters/" + dst.name
        st["补上"] += 1
        filled.append((it["name"], bucket, base, suf))
        if a.dry:
            continue
        imgs = (it.get("_media") or {}).get("images") or []
        imgs.append({
            "png": rel,
            "base": base + suf,
            "label": "图标",
            "source": "player_appear_data → socket_models → %s%s" % (ICON_BASE, base + suf),
            "fetch": "pe",
            "bytes": dst.stat().st_size,
        })
        it["_media"] = dict(it.get("_media") or {}, images=imgs, total=len(imgs))
        it["_media"].pop("missing", None)
        it["icons_all"] = [{"path": ICON_BASE + base, "gender": None, "png": rel}]
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        it["gender_icon_state"] = None
        it["icon_source"] = "appear_model_name"

    print("=== 补图结果 ===")
    for k, v in stat.items():
        print("  %-10s 卡 %-4d 补上 %-4d 无图标 %-4d 已有图 %d"
              % (k, v["卡"], v["补上"], v["无图标"], v["有图跳过"]))
    print("命中样例：")
    for f in filled[:12]:
        print("   %-18s %-8s %s%s" % f)

    if a.dry:
        print("（--dry：未写盘）")
        return 0
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s（卡数 %d）" % (BOARD.name, len(board["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
