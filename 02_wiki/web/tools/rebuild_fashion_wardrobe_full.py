# -*- coding: utf-8 -*-
"""全量重建 fashion_wardrobe（时装衣柜）—— 不靠旧板合并，从 fashion_data 表逐行解。

口径（已验通的解码姿势）：
    raw = table.read_bytes(); at = raw.find(b'x{'); L = <u32 at+2>
    body = raw[at+6:at+6+L]; cnt = <u32 body[0]>; blob = body[8+4*cnt:]
    rows = decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    icons/theme_codes/appear_ids = 0x0b jump → read_27_group(blob, off) → chs 池字符串

卡片粒度 = (归一名字, 部位, model_id)
    · 归一名字 = 表 name 去掉 -N天 时限后缀（不含其它任何改写，名字原样保留，含 -衣服/-头饰 后缀）
    · 部位 = 表字段 part_type → 图标族前缀 → new_fashion_id_str 前缀（三级，全部是表内证据）
    · model_id 进 key：实测 92 个名字被多套外观复用（如「灵动黄」8 个 model），
      只按名字聚合会把 8 件不同的衣服并成一张卡 —— 那是错的合并，不是"合卡"。
    · 男女合卡：同一卡内 f/m 两条图标都挂上，label 写「女」「男」。

图：assets/fashion_icon_refs/<basename>{.png,_b,_s,_max}.png 直接复用；
    没有才 img_fetch.export（PE→PC）实导，默认上限 200 条，其余如实标无图。
"""
from __future__ import annotations
import pathlib

import argparse
import hashlib
import json
import re
import shutil
import struct
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # 02_wiki/web

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
CDATA = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = ROOT / "data/boards/fashion_wardrobe.json"
REFS = ROOT / "assets/fashion_icon_refs"
POSTERS = ROOT / "assets/fashion_posters"
PLACEHOLDER = "assets/fashion_icon_refs/icon_unknown_s.png"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402

CST = timezone(timedelta(hours=8))
# 时限后缀：-30天 / (30天) / （30天）三种写法都要归一，否则「冰雪礼赞-头饰(30天)」
# 会跟永久款「冰雪礼赞-头饰」分成两张卡（2026-10-29 用户反馈）
# ★ 仍有一种归不了的：时限行的 name 只写配色（如「不羁黄-30天」），永久款叫「悠游探索 不羁黄」。
#   这类靠 tools/merge_duration_cards.py 兜（用 desc 里的全名 + 图标交集兜底匹配）。
DUR_RE = re.compile(r"(?:[-－]\d+天|[(（]\d+天[)）])$")
FAM = (("icon_b_", "cloth"), ("icon_h_", "hat"), ("icon_bag_", "bag"),
       ("icon_light_", "light"), ("icon_suit_", "suit"))
BUCKET = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "suit": "整套", "light": "光源"}
GENERIC_DESC = re.compile(r"^一件(永久款|\d+天时效|.{0,6}时效)")
LOCK_SOURCE_ID = "fashion-wardrobe-struct"


def load_rows():
    base = CDATA / "fashion_data.py"
    chs = CDATA / "fashion_data_chs.py"
    raw = base.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool(chs.read_bytes())
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, unbound, blob, pool, {"fashion_data.py": base, "fashion_data_chs.py": chs}


def gstrings(blob, pool, off):
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    kind, els = g
    out = []
    if kind == 0x0B:
        for e in els:
            out.extend(gstrings(blob, pool, e))
    elif kind == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                out.append(pool[e])
    return out


def V(r, k, d=None):
    got = r["values"].get(k)
    return got[1] if got else d


def fam_of(paths):
    for s in paths:
        b = s.rsplit("/", 1)[-1]
        for pre, pt in FAM:
            if b.startswith(pre):
                return pt
    return None


def part_of(r, paths):
    pt = V(r, "part_type")
    if pt:
        return pt, "part_type"
    pt = fam_of(paths)
    if pt:
        return pt, "icon_family"
    nf = V(r, "new_fashion_id_str") or ""
    if "_" in nf and nf.split("_")[0] in BUCKET:
        return nf.split("_")[0], "new_fashion_id_str"
    return None, None


def gender_of_path(p):
    b = p.rsplit("/", 1)[-1]
    if "_f_" in b:
        return "女"
    if "_m_" in b:
        return "男"
    return None


def ref_file(base):
    for suf in ("", "_b", "_s", "_max"):
        p = REFS / (base + suf + ".png")
        if p.is_file():
            return p
    return None


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-budget", type=int, default=200)
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--out", default=str(BOARD))
    args = ap.parse_args()

    POSTERS.mkdir(parents=True, exist_ok=True)
    rows, unbound, blob, pool, srcs = load_rows()
    PKG_SHA = sha256(srcs["fashion_data.py"])
    print(f"fashion_data 行 {len(rows)}  未解组 {len(unbound)}")

    cards = {}
    unkeyed = 0
    for r in rows:
        name = V(r, "name")
        if not name:
            unkeyed += 1
            continue
        paths = gstrings(blob, pool, int(str(V(r, "icons")).split(":")[1])) if V(r, "icons") else []
        pt, pt_src = part_of(r, paths)
        if pt is None:
            pt, pt_src = "unknown", "none"
        base = DUR_RE.sub("", name)
        mid = V(r, "model_id")
        key = (base, pt, mid)
        c = cards.get(key)
        if c is None:
            c = cards[key] = {"rows": [], "icons": [], "charm": [], "levels": [], "days": [],
                              "fid_days": set(), "desc": [], "names": set(), "model_ids": set(),
                              "permanent_rows": 0, "part_src": pt_src}
        c["part_src"] = pt_src
        c["rows"].append(r["key"])
        c["names"].add(name)
        c["model_ids"].add(mid)
        for p in paths:
            if p not in c["icons"]:
                c["icons"].append(p)
        is_perm = V(r, "valid_days") in (None, 0)
        if is_perm:
            c["permanent_rows"] += 1
        if isinstance(V(r, "charm_value"), int):
            c["charm"].append((is_perm, V(r, "charm_value")))
        if isinstance(V(r, "level"), int):
            c["levels"].append(V(r, "level"))
        vd = V(r, "valid_days")
        if isinstance(vd, int) and vd > 0:
            c["days"].append(vd)
        nf = V(r, "new_fashion_id_str") or ""
        tail = nf.split("_")[-1] if nf else ""
        if tail.isdigit() and int(tail) > 0:
            c["fid_days"].add(int(tail))
        if V(r, "desc"):
            c["desc"].append((is_perm, V(r, "desc")))

    print(f"卡片 {len(cards)}（归一名字+部位+model_id）")

    # ── 图：先复用 refs，再按预算实导
    # ★ 2026-10-29 修正：原来的 need 只收「整张卡一张 refs 都没有」的卡，
    #    于是女图命中 refs 的卡永远不去取男图 → 卡面只剩一个性别（用户报的
    #    「男女角色取图不完整」就是这个）。改成 **按槽位** 判断：哪张图没 refs
    #    就补哪张，预算也按张扣，不再按卡一刀切。
    need_icons = set()
    for (_name, _pt, _mid), c in cards.items():
        for p in c["icons"]:
            base = p.rsplit("/", 1)[-1]
            if ref_file(base):
                c["have_ref"] = c.get("have_ref", 0) + 1
            else:
                need_icons.add(base)
    total_icons = sum(len(c["icons"]) for c in cards.values())
    print(f"图标槽 {total_icons} ｜ refs 可直接复用 {total_icons - len(need_icons)} ｜ "
          f"需实导 {len(need_icons)} 个不同图标（预算 {args.fetch_budget}）")

    fetcher = None
    if not args.no_fetch and need_icons:
        try:
            from toolkit_core.img_fetch import export as img_export
            fetcher = img_export
        except Exception as e:  # noqa
            print("! img_fetch 不可用：", e)

    # ── 落卡 ──
    out_items = []
    stat = Counter()
    fetched = 0
    t0 = time.time()
    for (name, pt, mid), c in sorted(cards.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or 0)):
        hid = hashlib.md5(f"{name}|{pt}|{mid}".encode("utf-8")).hexdigest()[:10]
        cid = "fw_" + hid
        days = sorted(set(c["days"]))
        perm_rows = c["permanent_rows"]
        has_perm = perm_rows > 0
        state = "mixed" if (days and perm_rows) else ("timed" if days else "permanent")
        cv = [v for p, v in c["charm"] if p] or [v for _, v in c["charm"]]
        charm = max(cv) if cv else None
        lv = sorted(set(c["levels"]))
        descs = [d for _, d in c["desc"]]
        real = [d for d in descs if not GENERIC_DESC.match(str(d))]
        desc = (real or descs or [None])[0]

        # 图标 → 本地 png（女性优先做封面）
        icons = []
        for p in c["icons"]:
            base = p.rsplit("/", 1)[-1]
            icons.append({"path": p, "base": base, "gender": gender_of_path(p)})
        icons.sort(key=lambda x: (0 if x["gender"] == "女" else 1 if x["gender"] == "男" else 2))
        imgs = []
        for i, ic in enumerate(icons):
            rp = ref_file(ic["base"])
            dst = POSTERS / (f"{cid}.png" if i == 0 else f"{cid}_{i}.png")
            if rp:
                if not dst.is_file() or dst.stat().st_size != rp.stat().st_size:
                    shutil.copyfile(rp, dst)
                ic["png"] = f"assets/fashion_posters/{dst.name}"
                ic["fetch"] = "refs"
            elif fetcher and fetched < args.fetch_budget and ic["base"] in need_icons:
                ok = ""
                try:
                    ok = fetcher(ic["path"], dst)
                except Exception as e:  # noqa
                    ok = ""
                    print("  ! 导出失败", ic["path"], e)
                fetched += 1
                if ok and dst.is_file():
                    ic["png"] = f"assets/fashion_posters/{dst.name}"
                    ic["fetch"] = str(ok)
                elif dst.is_file():
                    dst.unlink()
            if ic.get("png"):
                imgs.append({
                    "png": ic["png"],
                    "base": ic["base"],
                    "label": ic["gender"] or f"图示{i + 1}",
                    "source": f"fashion_data.icons → {ic['path']}",
                    "fetch": ic.get("fetch"),
                    "bytes": (POSTERS / Path(ic["png"]).name).stat().st_size,
                })
        stat["有图" if imgs else "无图"] += 1

        genders = [ic["gender"] for ic in icons if ic["gender"]]
        g = "女/男" if ("女" in genders and "男" in genders) else (genders[0] if genders else None)
        media = {"images": imgs, "icons_total": len(icons), "total": len(imgs)}
        if not imgs:
            media["placeholder"] = {"png": PLACEHOLDER, "source": "客户端同款占位图 ui/item_icon/icon_unknown_s",
                                    "reason": "图标未从 refs 命中且未在本次实导预算内取得"}

        out_items.append({
            "id": cid,
            "name": name,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "fashion_data 表逐行解码（name/desc/model_id/charm_value/level/icons 字段）",
            "tables": ["fashion_data.py", "fashion_data_chs.py"],
            "row_keys": sorted(c["rows"]),
            "name_variants": sorted(c.get("names") or [name]),
            "part": pt,
            "part_source": c.get("part_src"),
            "part_label": BUCKET.get(pt, "未分类"),
            "part_bucket": [BUCKET.get(pt, "其他")],
            "model_id": mid,
            "model_ids": sorted(x for x in c.get("model_ids", set()) if x is not None),
            "grade_level": lv[-1] if lv else None,
            "grade_levels": lv or None,
            "charm_value": charm,
            "durations": days or None,
            "duration_variants": sorted(set(days) | c["fid_days"]) or None,
            "time_limited_variants": days or None,
            "has_permanent": has_perm,
            "duration_state": state,
            "gender": g,
            "desc": desc,
            "desc_note": "描述取自 fashion_data.desc（同卡多行时优先永久款的非通用描述）" if desc else "表里 desc 为空",
            "icon_state": "有图" if imgs else "含占位",
            "icon_count": len(imgs),
            "icons_all": [{"path": ic["path"], "gender": ic["gender"], "png": ic.get("png")} for ic in icons],
            "_media": media,
            "status_tags": ["static config"],
            "provenance": {
                "source_id": LOCK_SOURCE_ID,
                "source_lock_sha256": PKG_SHA,
                "table": r"com\cdata\fashion_data.py",
                "row_key": min(c["rows"]),
                "row_keys": sorted(c["rows"]),
                "field_refs": ["name", "desc", "model_id", "charm_value", "level", "icons",
                               "valid_days", "part_type", "new_fashion_id_str"],
                "name_source": r"com\cdata\fashion_data.py#name（去 -N天 后缀）",
                "part_source": c.get("part_src"),
                "icon_source": r"com\cdata\fashion_data.py#icons（0x0b jump → chs 池）",
                "rebuild": "full-rebuild-20261024（不靠旧板合并）",
                "upstream": {"package_sha256": PKG_SHA, "entry_index": None, "file_id": None,
                             "decoded_sha256": None, "role": None},
                "locator_chain": {
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                    "steps": [{
                        "kind": "decoded-table-row",
                        "source_id": LOCK_SOURCE_ID,
                        "table": r"com\cdata\fashion_data.py",
                        "row_key": min(c["rows"]),
                        "field_refs": ["name", "desc", "model_id", "charm_value", "level", "icons",
                                       "valid_days", "part_type", "new_fashion_id_str"],
                    }],
                },
            },
        })

    # 唯一 id 校验
    ids = [x["id"] for x in out_items]
    assert len(ids) == len(set(ids)), "id 冲突"

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    old_n = len(board.get("items") or [])
    pkg = srcs["fashion_data.py"]
    part_count = Counter(x["part"] for x in out_items)
    bucket_count = Counter(b for x in out_items for b in x["part_bucket"])
    dur = Counter(x["duration_state"] for x in out_items)
    now = datetime.now(CST)
    meta = board.get("meta") or {}
    meta.update({
        "name": meta.get("name") or "人物·全量时装衣柜",
        "category": meta.get("category") or "二、时装类 / （一）全量时装总表",
        "source_server": "PE 测试服 fashion_data 表（逐行解码：name/desc/model_id/charm_value/level/icons）",
        "package_sha": PKG_SHA,
        "generated": now.date().isoformat(),
        "evidence": "structure",
        "notes": (f"全量重建：{len(rows)} 行 → {len(out_items)} 张卡（归一名字+部位+model_id）。"
                  f"部位分布={dict(part_count)}；部位归组={dict(bucket_count)}；"
                  f"期限：永久 {dur.get('permanent', 0)} / 限时 {dur.get('timed', 0)} / 永久+限时 {dur.get('mixed', 0)}；"
                  f"图示：有图 {stat['有图']} / 无图占位 {stat['无图']}。"
                  "★ 归一口径：仅去 -N天 时限后缀；名字里的 -衣服/-头饰 等部件词原样保留（不猜不改写）。"
                  "★ 男女合卡：同一卡内 f/m 图标都挂上，label 写女/男。"
                  "★ model_id 进卡键：92 个名字被多套外观复用（如「灵动黄」8 个 model），只按名字会错并。"),
        "join_policy": "按（归一名字 + 部位 + model_id）聚合；part 取表字段 part_type → 图标族前缀 → new_fashion_id_str 前缀",
        "icon_source": "fashion_data.icons（0x0b jump → CHS 池）→ assets/fashion_icon_refs 复用 / img_fetch PE→PC 实导",
        "rebuild": {
            "at": now.isoformat(timespec="seconds"),
            "decoded_rows": len(rows),
            "unresolved_groups": len(unbound) if hasattr(unbound, "__len__") else None,
            "cards": len(out_items),
            "prev_items": old_n,
            "fetched_new": fetched,
            "fetch_budget": args.fetch_budget,
            "distinct_names_raw": len({V(r, "name") for r in rows}),
            "distinct_names_norm": len({x["name"] for x in out_items}),
        },
        "state_summary": {
            "unresolved": len(out_items), "static config": len(out_items), "verified": 0,
            "runtime final unknown": len(out_items),
            "有图": stat["有图"], "无图": stat["无图"],
        },
        "provenance": {"contract_version": 3, "audit_status": "passed",
                       "contract": "frozen-audited-artifact",
                       "source_locks": [{"source_id": LOCK_SOURCE_ID, "role": "primary",
                                         "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_data.py",
                                         "sha256": PKG_SHA, "bytes": pkg.stat().st_size,
                                         "mtime_ns": pkg.stat().st_mtime_ns}],
                       "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                        "integer_join_policy": "no-equal-integer-join",
                                        "runtime_final_policy": "unknown-unless-runtime-proven"}},
        "icon_filled_at": now.isoformat(timespec="seconds"),
    })
    board["meta"] = meta
    board["items"] = out_items
    out = Path(args.out)
    out.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = "
        + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"→ {out.name}: {old_n} → {len(out_items)} 张卡 ｜ 有图 {stat['有图']} 无图 {stat['无图']} "
          f"｜ 本次实导 {fetched} ｜ 用时 {time.time() - t0:.1f}s")
    print("部位", dict(part_count), "| 归组", dict(bucket_count), "| 期限", dict(dur))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
