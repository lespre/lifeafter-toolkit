# -*- coding: utf-8 -*-
"""给时装板「挂饰」桶补图标（唯一正确链路：挂饰 = 道具，图标 = ui/item_icon/icon_<道具id>）。

═══════════════════════════════════════════════════════════════════════════
★ 为什么以前的规则是错的（务必记住，别再犯）

  旧脚本 fill_appearance_icons.py 按「模型路径反推命名族」：
      character/pendant/pendant_068/pendant_068.gim → icon_pendant_068
  这个族**在包里只有一个编号**（icon_pendant_f/m_55001，那是"挂饰"部位页签图），
  所以 134 张挂饰卡永远 0 命中。当时还试过 icon_<row_key>，命中 8 个但全是炸弹/宣传图。

★ 真实机制（PE 客户端 + 藏宝阁配置双向对上）

  挂饰在客户端是**道具**，道具 id 段 270000~2701xx，
  图标路径就是 `ui/item_icon/icon_<item_id>`（带 _b/_s 两档）。
  UI 代码 PanelFashionArrangement.py 里的 `AppearPartItem.ensure_item_icon`
  也印证：外观部位条目取的是 **item icon**。

  证据链（都能复现）：
    1. daily_items_limit_alarm_data（PE 表）: item_id 270000 → desc「蓝白猫咪」
    2. gift_data（PE 表）: name「彩虹独角兽挂饰礼盒」icon=ui/item_icon/icon_270010，
       desc 明确写「打开礼盒后可获得彩虹独角兽挂饰」
    3. 藏宝阁 all_equips_data.json 的 270xxx 段 131 条名字，与 (1) 交叉 20/22 一致
       （差的 2 条是 json 未收录，PE 表有）

★ 数据源分层（全部只读）

  A. PE 表主链路   daily_items_limit_alarm_data / gift_data / super_fashion_gift_data
                   / random_item_reward_data_*
  B. 藏宝阁配置   00_规范与工具/治理/参考资料/藏宝阁_CBG/json/game_auto_config/all_equips_data.json
                   → 仅补「名字→道具id」，图**一律从 PE 包取**，provenance 标注 cbg_reference
  C. 图片          pe_fetch（pe_gres_android），三档 _b/_s/无后缀

★ 口径

  · 连锁路：名字精确匹配才用，匹配不上留缺图（不猜、不按编号顺序塞）
  · 图取不到就不写，不动 _media
  · 幂等：已带 icons_all 的卡默认跳过；--force 才重刷
  · --dry 只统计不写盘
═══════════════════════════════════════════════════════════════════════════

用法：
    python fill_pendant_icons.py --dry
    python fill_pendant_icons.py
    python fill_pendant_icons.py --force --only 中国结,一叶知秋
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
MAP_OUT = WEB / "data/boards/_refs/pendant_item_icon_map.json"
CBG = (PROJ / "00_规范与工具/治理/参考资料/藏宝阁_CBG/json/game_auto_config"
       / "all_equips_data.json")

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402

ICON_BASE = "ui/item_icon/"
SEG_LO, SEG_HI = 270000, 271999          # 挂饰道具 id 段
GIFT_ICON_RE = re.compile(r"^ui?/?item_icon/icon_(\d+)(?:_[bs])?(?:\.png)?$")


# ─────────────────────────────────────────────── PE 表读取
def read_pe_table(stem: str):
    """读 PE cdata 的 x{ 表，返回 (rows, blob, pool)；解不了返回 (None, None, None)。"""
    p = CD / (stem + ".py")
    if not p.is_file():
        return None, None, None
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0 or at > 4096:
        return None, None, None
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    if len(body) < 12:
        return None, None, None
    cnt = struct.unpack_from("<I", body, 0)[0]
    if cnt <= 0 or cnt > 900000:
        return None, None, None
    blob = body[8 + 4 * cnt:]
    cp = CD / (stem + "_chs.py")
    pool: list = []
    if cp.is_file():
        try:
            pool = BT.parse_legacy_chs_pool(cp.read_bytes())
        except Exception:
            pool = []
    try:
        rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    except Exception:
        return None, None, None
    return (rows or None), blob, pool


def group_strings(blob: bytes, pool: list, off: int, depth: int = 0) -> list:
    """展开 0x0B 组 / 0x05 字符串池引用。"""
    if depth > 6:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    kind, els = g
    out: list = []
    if kind == 0x0B:
        for e in els:
            out.extend(group_strings(blob, pool, e, depth + 1))
    elif kind == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                out.append(pool[e])
    return out


def fval(v, blob, pool) -> list:
    """字段值 → 值列表（自动展开 jump 组）。"""
    if isinstance(v, tuple) and len(v) == 2:
        if str(v[1]).startswith("jump:"):
            try:
                return group_strings(blob, pool, int(str(v[1]).split(":")[1]))
            except Exception:
                return []
        return [v[1]]
    return [v]


# ─────────────────────────────────────────────── 名字 → 道具 id
def collect_map(verbose: bool = True) -> dict:
    """返回 {挂饰名: {"ids": [...], "src": [...]}, }"""
    idx: dict = {}

    def add(name: str, iid: int, src: str):
        if not name or not isinstance(iid, int) or not (SEG_LO <= iid <= SEG_HI):
            return
        rec = idx.setdefault(name, {"ids": [], "src": []})
        if iid not in rec["ids"]:
            rec["ids"].append(iid)
        if src not in rec["src"]:
            rec["src"].append(src)

    # A1. daily_items_limit_alarm_data：item_id + desc(名字)
    rows, blob, pool = read_pe_table("daily_items_limit_alarm_data")
    n_a1 = 0
    if rows:
        for r in rows:
            f = r["values"]
            ids = [x for x in fval(f.get("item_id"), blob, pool) if isinstance(x, int)]
            nms = [x for x in fval(f.get("desc"), blob, pool) if isinstance(x, str)]
            for iid in ids:
                for nm in nms[:1]:
                    add(nm, iid, "pe:daily_items_limit_alarm_data")
                    n_a1 += 1

    # A2. gift_data / super_fashion_gift_data / random_item_reward_*：礼盒 icon → 挂饰名
    n_a2 = 0
    for stem, iconf, namef in (
        ("gift_data", "icon", "name"),
        ("super_fashion_gift_data", "gift_icon", "title"),
        ("random_item_reward_data_794", "icon", "name"),
        ("random_item_reward_data_921", "icon", "name"),
        ("random_item_reward_data_922", "icon", "name"),
        ("random_item_reward_data_923", "icon", "name"),
        ("random_item_reward_data_951", "icon", "name"),
        ("random_item_reward_data_5", "icon", "name"),
        ("random_item_reward_data_860", "icon", "name"),
    ):
        rows, blob, pool = read_pe_table(stem)
        if not rows:
            continue
        for r in rows:
            f = r["values"]
            icons = [x for x in fval(f.get(iconf), blob, pool) if isinstance(x, str)]
            nms = [x for x in fval(f.get(namef), blob, pool) if isinstance(x, str)]
            if not icons or not nms:
                continue
            m = GIFT_ICON_RE.match(icons[0].strip())
            if not m:
                continue
            iid = int(m.group(1))
            nm = nms[0].strip()
            cands = {nm}
            for tail in ("挂饰礼盒", "挂件礼盒", "礼盒"):
                if nm.endswith(tail):
                    cands.add(nm[: -len(tail)].strip())
                    break
            for c in cands:
                if c:
                    add(c, iid, "pe:%s" % stem)
                    n_a2 += 1

    # B. 藏宝阁配置（只补名字→id，图仍从 PE 取）
    n_b = 0
    if CBG.is_file():
        try:
            d = json.loads(CBG.read_text(encoding="utf-8"))
            for k, v in d.items():
                if not str(k).startswith("270"):
                    continue
                nm = (v or {}).get("name")
                if nm:
                    add(str(nm), int(k), "cbg_reference")
                    n_b += 1
        except Exception as exc:  # noqa: BLE001
            print("  ! 藏宝阁配置读取失败：%r" % (exc,))

    if verbose:
        print("映射源：daily_items %d 条 / 礼盒 %d 条 / 藏宝阁 %d 条 → 去重名字 %d 个"
              % (n_a1, n_a2, n_b, len(idx)))
    return idx


# ─────────────────────────────────────────────── 取图
def icon_candidates(name: str, rec: dict) -> list:
    """名字 → 候选图标基名（有序）。"""
    out = []
    for iid in sorted(rec["ids"]):
        base = "%sicon_%d" % (ICON_BASE, iid)
        if base not in out:
            out.append(base)
    # 名字本身可能带「挂件/挂饰」后缀差异，交给调用方做宽松匹配
    return out


def probe(conn, base: str):
    for suf in ("_b", "_s", ""):
        try:
            r = pe_fetch.resolve(base, suf, conn)
        except Exception:
            r = None
        if r:
            return suf, r
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true", help="已有 icons_all 的卡也重刷")
    ap.add_argument("--only", default="", help="只处理这些卡名（逗号分隔）")
    a = ap.parse_args()
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    idx = collect_map()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    conn = pe_fetch.con()
    OUT.mkdir(parents=True, exist_ok=True)

    cards = [it for it in board["items"] if (it.get("part_bucket") or [None])[0] == "挂饰"]
    st = {"卡": len(cards), "已有图跳过": 0, "补上": 0, "无映射": 0, "有映射但包里无图": 0}
    filled, no_map, no_file = [], [], []

    for it in cards:
        nm = (it.get("name") or "").strip()
        if only and nm not in only:
            continue
        if (it.get("icons_all") or (it.get("_media") or {}).get("images")) and not a.force:
            st["已有图跳过"] += 1
            continue
        rec = idx.get(nm)
        if not rec:
            # 宽松：去掉「挂件/挂饰」后缀再试
            for cut in ("挂件", "挂饰"):
                if nm.endswith(cut) and idx.get(nm[: -len(cut)].strip()):
                    rec = idx[nm[: -len(cut)].strip()]
                    break
        if not rec:
            st["无映射"] += 1
            no_map.append(nm)
            continue
        cands = icon_candidates(nm, rec)
        hit = None
        for base in cands:
            got = probe(conn, base)
            if got:
                hit = (base, got[0])
                break
        if not hit:
            st["有映射但包里无图"] += 1
            no_file.append((nm, rec["ids"]))
            continue

        base, suf = hit
        dst = OUT / (str(it["id"]) + ".png")
        if not a.dry:
            if dst.exists():
                dst.unlink()
            try:
                ok = pe_fetch.export(base + suf, dst)
            except Exception:
                ok = False
            if not (ok and dst.is_file() and dst.stat().st_size > 512):
                st["有映射但包里无图"] += 1
                no_file.append((nm, rec["ids"]))
                continue

        st["补上"] += 1
        filled.append((nm, base, suf, ",".join(rec["src"])))
        if a.dry:
            continue
        rel = "assets/fashion_posters/" + dst.name
        imgs = (it.get("_media") or {}).get("images") or []
        imgs = [x for x in imgs if x.get("png") != rel]
        imgs.append({
            "png": rel,
            "base": base + suf,
            "label": "图标",
            "source": "%s → %s%s" % ("/".join(rec["src"]), base, suf),
            "fetch": "pe",
            "bytes": dst.stat().st_size,
        })
        it["_media"] = dict(it.get("_media") or {}, images=imgs, total=len(imgs))
        it["_media"].pop("missing", None)
        it["icons_all"] = [{"path": base, "gender": None, "png": rel}]
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        it["gender_icon_state"] = None
        it["icon_source"] = "pendant_item_icon"
        prov = it.setdefault("provenance", {})
        prov["icon_source"] = "pendant_item_icon"
        prov["icon_item_ids"] = rec["ids"]
        prov["icon_refs"] = rec["src"]
        df = prov.setdefault("derived_fields", [])
        for f in ("icons_all", "icon_source", "icon_item_ids"):
            if f not in df:
                df.append(f)

    # 未补上的卡：写清缺图原因（不留空白，便于后续复查）
    if not a.dry:
        no_map_names = set(no_map)
        no_file_names = {x[0] for x in no_file}
        for it in cards:
            nm = (it.get("name") or "").strip()
            if (it.get("icons_all") or []):
                continue
            if nm in no_file_names:
                it["icon_state"] = "缺图"
                it["icon_missing_reason"] = "道具id已定位，但 PE 解包产物内无该编号的独立 PNG（清单有、包内无）"
            elif nm in no_map_names:
                it["icon_state"] = "缺图"
                it["icon_missing_reason"] = "未能把名字对上挂饰道具 id（270xxx 段）"

    print("=== 挂饰补图 ===")
    for k, v in st.items():
        print("  %-14s %d" % (k, v))
    print("命中样例：")
    for f in filled[:10]:
        print("   %-16s %-34s %-3s %s" % f)
    if no_file:
        print("有映射但包里无图 %d：%s" % (len(no_file), [x[0] for x in no_file]))
    if no_map:
        print("无映射 %d：%s" % (len(no_map), no_map))

    if a.dry:
        print("（--dry：未写盘）")
        return 0

    MAP_OUT.parent.mkdir(parents=True, exist_ok=True)
    MAP_OUT.write_text(json.dumps(
        {k: {"ids": v["ids"], "src": v["src"]} for k, v in sorted(idx.items())},
        ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s（卡数 %d）｜映射表 %s" % (BOARD.name, len(board["items"]), MAP_OUT.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
