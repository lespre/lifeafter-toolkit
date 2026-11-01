# -*- coding: utf-8 -*-
r"""回填（一）人物时装·头饰 / 面饰 / 挂饰（并入自 fashion_face 的 face_* 条目）的
**2D 图标** 与 **描述**。

溯源结论（唯一口径，可复算）：
  这批条目的行源表是 com/cdata/player_module_appear_data.py（legacy 0x73 表，
  文本走同目录 _chs.py 池）。该表**自带**两个字段，当初并入主板时没带过来：
    icon  → 2D 图标资源路径（如 item_icon/icon_260030、ui/item_icon/icon_h_m_3395001）
    desc  → 描述原文（含 #r 换行 / #f(N) 颜色标记，前端 board_core.js 已能渲染）
  所以描述 100% 可直接取；2D 图按 icon 路径去 PE 包取，取不到的如实标缺图。

取图规则（有序，不猜名）：
  1. 归一化路径：不以 "ui/" 开头的一律补 "ui/" 前缀（表里两种写法混用）；
  2. 档位依次试 `_b` → `_s` → 无后缀（同 pe_fetch 的 join 约定）；
  3. 表内声明的目录取不到时，再用同名文件在 `ui/item_big_icon/`、`ui/item_icon/` 下试一次；
  4. 面饰/头饰的 icon 常是 `icon_h_m_XXXXXXX`（男版）。若男版取不到，
     再试同模块号的 `icon_h_f_XXXXXXX`（女版）—— 这是**同名同模块的另一性别渲染**，
     不是另一个道具。实测两者有时字节完全相同（抽样 30 对：20 对一致 / 10 对不同），
     所以女版只能作为**替代图**并如实标注，不能冒充男版。
  5. 全部未命中 → icon_state="缺图"，icon_missing_reason 写明「表内声明路径 + PE 包内无该资源」，
     绝不导出占位图、绝不按行号猜图。
  ★ 不做「模型路径反推图标名」那套（fill_appearance_icons.py 的做法）：
    本表自带 icon 字段，按名字反推反而可能张冠李戴。

写盘字段：
  卡片级  desc / desc_note / icon_state / icon_missing_reason / icon_source / icon_note /
          icon_count / icons_all / _media
  溯源    provenance.field_refs 校正为**真实字段名**（原来写的是 show_name / part_type /
          model_id / female_icon，这 4 个字段在本表并不存在），
          并追加 desc_source / icon_source 两块（同源同表同行，故不新增 locator_chain step，
          遵守 no-cross-source-field-join）。
  女版替代   icons_all[0].gender="女"、_media.images[0].label="图标（女版）"、
          icon_note 写明「表内声明的是男版路径 …，包内只有女版资源，男女表现可能不同」。

幂等：同输入重跑结果不变；已存在且体积正常的 PNG 不重复导出；
      meta.notes 用 notes_util.append_note() 幂等追加。

用法：
    python fill_face_media_desc.py --dry      # 只统计，不写盘、不导图
    python fill_face_media_desc.py            # 落盘 + 导图
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if SHARED.exists():
    sys.path.insert(0, str(SHARED))
FETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"
if FETCH.exists():
    sys.path.insert(0, str(FETCH))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"

TBL = "player_module_appear_data"
TBL_PATH = CD / f"{TBL}.py"
TBL_CHSE = CD / f"{TBL}_chs.py"
SRC_ID = "fashion-face-player_module_appear_data-media"

SUFFIXES = ("_b", "_s", "")
ALT_DIRS = ("ui/item_big_icon/", "ui/item_icon/")
MIN_PNG_BYTES = 512


def load_table() -> dict:
    raw = TBL_PATH.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(TBL_CHSE.read_bytes()) if TBL_CHSE.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            out[int(r.get("key"))] = v
        except (TypeError, ValueError):
            continue
    return out


def normalize(icon: str) -> str:
    p = str(icon or "").replace("\\", "/").strip()
    if not p:
        return ""
    if not p.startswith("ui/"):
        p = "ui/" + p
    return p


def candidates(icon: str) -> list:
    """同一张声明的图标，在本目录与备用目录里各试一次（**只换目录，不换性别**）。

    ★ 修正：以前这里在男版取不到时会自动换成女版同名资源当成本卡的「图标」。
      但 player_module_appear_data 是 **icon(男) + female_icon(女) 两列**，
      女版本来就该单独展示，拿去顶男版会变成「一卡只有一张图、性别还标错」。
    """
    declared = normalize(icon)
    if not declared:
        return []
    stem = declared.rsplit("/", 1)[-1]
    out = []
    for base in [declared] + [d + stem for d in ALT_DIRS]:
        if base not in out:
            out.append(base)
    return out


def gender_of(declared: str, field: str):
    """图标性别：路径里有 _h_m_/_h_f_ 就照路径判；通用图（无性别段）返回 None。"""
    if "_h_m_" in declared:
        return "男"
    if "_h_f_" in declared:
        return "女"
    if field == "female_icon":
        return "女"
    return None


def probe(conn, base: str):
    """返回 (基路径, 后缀, 完整资源路径) 或 None。"""
    import pe_fetch
    for suf in SUFFIXES:
        try:
            r = pe_fetch.resolve(base, suf, conn)
        except Exception:
            r = None
        if r:
            return base, suf, r[0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    import pe_fetch

    src = load_table()
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    conn = pe_fetch.con()

    st = {"卡": 0, "描述": 0, "有图": 0, "双图": 0, "单图": 0, "单图缺": 0,
          "缺图": 0, "无源行": 0}
    miss: list[tuple[str, str, str]] = []

    for it in d["items"]:
        if not str(it.get("id", "")).startswith("face_"):
            continue
        st["卡"] += 1
        prov = it.setdefault("provenance", {})
        rk = prov.get("row_key")
        try:
            rk = int(rk)
        except (TypeError, ValueError):
            rk = None
        row = src.get(rk) if rk is not None else None
        if row is None:
            st["无源行"] += 1
            it["desc_note"] = f"该行不在 {TBL}（描述待补，不伪造）"
            continue

        # ── 描述 ───────────────────────────────────────────────
        desc = row.get("desc")
        if desc:
            it["desc"] = desc
            it["desc_note"] = f"{TBL}.desc（行 {rk}）"
            st["描述"] += 1
        else:
            it["desc"] = None
            it["desc_note"] = f"{TBL}.desc 为空（行 {rk}）"

        # ── 2D 图标（男 icon / 女 female_icon 两列都要）───────────
        # 同一张卡的所有变体行（row_variants）都看，取两列去重后的声明路径清单。
        decl: list[tuple[str, str]] = []      # [(声明路径, 字段名)]
        seen_p: set[str] = set()
        for rr in [row] + [src.get(int(k)) for k in (it.get("row_variants") or [])
                           if str(k).isdigit()] :
            if not rr:
                continue
            for field in ("icon", "female_icon"):
                p = normalize(rr.get(field))
                if p and p not in seen_p:
                    seen_p.add(p)
                    decl.append((p, field))
        if not decl:
            decl = [(normalize(row.get("icon")), "icon")]
        # 男在前、女在后，通用图放最后
        order = {"男": 0, "女": 1, None: 2}
        decl.sort(key=lambda x: order.get(gender_of(x[0], x[1]), 2))

        imgs: list[dict] = []
        icons_all: list[dict] = []
        no_gender: list[str] = []
        idx = 0
        for declared, field in decl:
            g = gender_of(declared, field)
            hit = None
            for base in candidates(declared):
                hit = probe(conn, base)
                if hit:
                    break
            if not hit:
                icons_all.append({"path": declared, "gender": g, "png": None})
                no_gender.append(g or declared)
                st["单图缺"] += 1
                miss.append((it["name"], declared, "PE 包内无该图标资源"))
                continue
            base, suf, full = hit
            rel = "assets/fashion_posters/%s%s.png" % (it["id"], "" if idx == 0 else f"_{idx}")
            dst = WEB / rel
            want_base = full.rsplit(".", 1)[0]
            # ★ 必须校验旧文件到底是不是这张图：命名规则从「单张 <id>.png」改成
            #   「男 <id>.png / 女 <id>_1.png」后，旧的女版图会正好躺在 <id>.png 上，
            #   只看「文件存在且够大」就会把女图当男图复用。用上一版 _media 记的 base 对账。
            prev_by_rel = {im.get("png"): im.get("base") for im in (it.get("_media") or {}).get("images") or []}
            ok = ((not a.dry) and dst.is_file() and dst.stat().st_size > MIN_PNG_BYTES
                  and prev_by_rel.get(rel) == want_base)
            if not ok and not a.dry:
                if dst.exists():
                    dst.unlink()
                try:
                    ok = bool(pe_fetch.export(full, dst))
                except Exception:
                    ok = False
                ok = ok and dst.is_file() and dst.stat().st_size > MIN_PNG_BYTES
            if not ok:
                icons_all.append({"path": declared, "gender": g, "png": None})
                st["单图缺"] += 1
                miss.append((it["name"], declared, "PE 包内声明路径解不出图"))
                continue
            icons_all.append({"path": base, "gender": g, "png": rel})
            imgs.append({
                "png": rel,
                "base": full.rsplit(".", 1)[0],
                "suffix": suf,
                "label": g or "图标",
                "source": f"{TBL}.{field} → {declared}",
                "fetch": "pe",
                "bytes": dst.stat().st_size if dst.is_file() else None,
            })
            idx += 1

        want = {g for _p, f in decl for g in [gender_of(_p, f)] if g}
        # 卡片性别口径：按**表里声明的列**判，不按「哪张图恰好取到了」判
        #（取不到图是打包问题，不能反推这件外观只有单性别）
        if want == {"男", "女"}:
            it["gender"] = "女/男"
        elif want == {"女"}:
            it["gender"] = "女"
        elif want == {"男"}:
            it["gender"] = "男"
        got = {i["gender"] for i in icons_all if i["png"]}
        if imgs:
            it["icon_state"] = "有图"
            it["icon_count"] = len(imgs)
            it["icon_source"] = f"{TBL}.icon（男）/ female_icon（女）"
            it["icons_all"] = icons_all
            it["_media"] = {"images": imgs, "icons_total": len(icons_all), "total": len(imgs)}
            it.pop("icon_missing_reason", None)
            lack = sorted(want - got)
            if lack:
                it["icon_note"] = ("表内 %s 版图标路径在 PE 包里取不到，卡面只展示%s；"
                                   "男女表现可能不同，缺的那一类不是没有、是这一版包里没打包。"
                                   % ("、".join(lack), "、".join(sorted(got))))
            else:
                it.pop("icon_note", None)
            st["有图"] += 1
            st["双图" if len(imgs) >= 2 else "单图"] += 1
        else:
            it["icon_state"] = "缺图"
            it["icon_missing_reason"] = "表里 icon / female_icon 声明的路径在 PE 包里都取不到图"
            it["icon_count"] = 0
            it["icon_source"] = f"{TBL}.icon（男）/ female_icon（女）"
            it["icons_all"] = icons_all
            it["_media"] = {"images": [], "total": 0}
            it.pop("icon_note", None)
            st["缺图"] += 1


        # 清掉多余的序号图（例如上一版出过 _1.png，这一版只有 1 张）
        if not a.dry:
            for n in range(len(imgs), len(imgs) + 4):
                p = OUT / ("%s_%d.png" % (it["id"], n))
                if p.is_file():
                    p.unlink()

        # ── 溯源字段校正 ───────────────────────────────────────
        # 卡面 source 原文写的是「面饰专池 BA entry…（0x73 legacy CHS 池，名+时限可靠）」，
        # 那时描述/图标还没解出来。现在四个字段都按 row_key 直取同一行，
        # 卡面说明必须跟着改，否则和 provenance 自相矛盾。
        it["source"] = (f"{TBL} 行解码（row_key {rk} 直取 name / part / icon / female_icon / desc / "
                        f"charm_value；时限变体为同组行 row_variants 合并；"
                        f"男图取 icon、女图取 female_icon，两列都单独出图）")
        refs = ["name", "part", "icon", "female_icon", "desc"]
        prov["field_refs"] = refs
        prov["name_source"] = f"{TBL}.name"
        prov["desc_source"] = {
            "source_id": SRC_ID,
            "source_lock_sha256": prov.get("source_lock_sha256"),
            "table": TBL,
            "row_key": rk,
            "field_refs": ["desc"],
        }
        prov["icon_source"] = {
            "source_id": SRC_ID,
            "source_lock_sha256": prov.get("source_lock_sha256"),
            "table": TBL,
            "row_key": rk,
            "field_refs": ["icon", "female_icon"],
        }
        ch = prov.get("locator_chain") or {}
        for step in ch.get("steps") or []:
            if step.get("table") == TBL:
                step["field_refs"] = refs

    note = ("头饰/面饰/挂饰（并入自 fashion_face 的 face_* 条目）2D 图与描述回填："
            f"来源 {TBL}（按 provenance.row_key 取行），描述字段 desc，"
            f"男图字段 icon、女图字段 female_icon —— **两列分别出图，不互相顶替**。"
            f"描述命中 {st['描述']} 条；出图成功 {st['有图']} 条"
            f"（男女各 1 张的 {st['双图']} 条，只有单边资源的 {st['单图']} 条，"
            f"单边缺失已在卡片 icon_note 注明是「包里没打包」而不是「没有这个东西」），"
            f"两列都取不到而如实标缺图 {st['缺图']} 条；不导占位图、不按行号猜图、不跨性别顶替。")
    # 旧版口径（只取 icon 单列、女版顶替男版）必须清掉，否则和新口径同时挂着一句话打脸
    _meta = d.setdefault("meta", {})
    _parts = [p for p in (_meta.get("notes") or "").split(notes_util.SEP)
              if p.strip() and not p.strip().startswith("头饰/面饰/挂饰（并入自 fashion_face 的 face_* 条目）2D 图与描述回填")]
    _meta["notes"] = notes_util.SEP.join(_parts)
    notes_util.append_note(d, note)

    print("=== face_* 2D图 / 描述 回填（男女双图）===")
    for k in ("卡", "描述", "有图", "双图", "单图", "单图缺", "缺图", "无源行"):
        print("  %-6s %d" % (k, st[k]))
    if miss:
        print("  缺图样例（前 8）：")
        for n, p, why in miss[:8]:
            print("    %-14s %-34s %s" % (n, p, why))

    if a.dry:
        print("（--dry：未写盘）")
        return 0
    write_board_pair(BOARD, d)
    print("已写回 %s（卡数 %d）" % (BOARD.name, len(d["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
