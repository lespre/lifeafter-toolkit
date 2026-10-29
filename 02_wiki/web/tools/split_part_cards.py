# -*- coding: utf-8 -*-
r"""把「同套多部位」合并卡拆回按部位的单卡（头饰一张、衣服一张）。

起因（2026-10-29 用户反馈）：
  「星月落羽幻彩典藏」在板上是一张卡，部位写「衣服/头饰」，4 张图、4 个行键 —— 但表里
  那是两件独立装备：
    行 367067  hat_3202_1_0   头饰  魅力 600   图标 icon_367067_*
    行 367068  cloth_3202_1_0 衣服  魅力 1400  图标 icon_367068_*
  合并来自历史脚本 merge_fashion_part_cards.py（同 name + 同 model 的 cloth/hat 并卡），
  把两件的行键、图、魅力值糊在一张卡上，看起来就"莫名其妙合并"了。

本脚本按表里的行重新拆：
  · 以 row_keys 反查 fashion_data 每一行的 part_type，按部位分组
  · 每组一张卡：part / row_keys / 图标 / 魅力 / 品级 / 期限 全部按该组自己的行算
  · 名字从该行 desc 里取「xxx-头饰(永久款)。…」的前半段（表里 name 本身不带部位后缀）
  · 图片按该组图标的 base 重新挂（refs → 原卡同 base → PE/PC 实导 → 记 missing）
  · 顺带修「假多部位」：part 是单部位、part_bucket 却被写成 [衣服,头饰] 的 516 张

用法：
  python split_part_cards.py --dry
  python split_part_cards.py --only 星月落羽幻彩典藏
  python split_part_cards.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import struct
import sys
from collections import Counter, defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"
CDATA = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
POSTERS = WEB / "assets/fashion_posters"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(WEB / "tools"))
import toolkit_core.bindict_table as BT          # noqa: E402
from repair_fashion_posters import PackExporter, gender_of, nb, refs_hit  # noqa: E402

FAM = (("icon_b_", "cloth"), ("icon_h_", "hat"), ("icon_bag_", "bag"),
       ("icon_light_", "light"), ("icon_suit_", "suit"), ("icon_face_", "face"))
BUCKET = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "suit": "整套",
          "light": "光源", "face": "面饰", "pendant": "挂饰", "proj": "投影"}
DUR_RE = re.compile(r"-(\d+)天$")
DESC_PART = re.compile(r"^(.+?)-(头饰|衣服|背包|挂饰|面饰|整套|光源)[（(]")
PART_ORDER = {"头饰": 0, "衣服": 1, "背包": 2, "整套": 3, "光源": 4}


def V(r, k, d=None):
    got = r["values"].get(k)
    return got[1] if got else d


def load_rows():
    raw = (CDATA / "fashion_data.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CDATA / "fashion_data_chs.py").read_bytes())
    rows, _unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, blob, pool


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
        return pt
    pt = fam_of(paths)
    if pt:
        return pt
    nf = V(r, "new_fashion_id_str") or ""
    if "_" in nf and nf.split("_")[0] in BUCKET:
        return nf.split("_")[0]
    return None


def row_index():
    rows, blob, pool = load_rows()
    idx = {}
    for r in rows:
        ic = V(r, "icons")
        paths = gstrings(blob, pool, int(str(ic).split(":")[1])) if ic else []
        pt = part_of(r, paths)
        idx[r["key"]] = {
            "part": BUCKET.get(pt, pt or "其他"),
            "icons": paths,
            "charm": V(r, "charm_value"),
            "level": V(r, "level"),
            "days": V(r, "valid_days"),
            "name": V(r, "name"),
            "desc": V(r, "desc"),
        }
    return idx


def new_id(name: str, part: str, mid) -> str:
    h = hashlib.sha1(("%s|%s|%s" % (name, part, mid)).encode("utf-8")).hexdigest()
    return "fw_" + h[:10]


def split_gender(path: str) -> str:
    g = gender_of(path)
    if g:
        return g
    b = path.rsplit("/", 1)[-1]
    if b.endswith("_1") or b.endswith("_1_b") or b.endswith("_1_s"):
        return "男"
    if b.endswith("_2") or b.endswith("_2_b") or b.endswith("_2_s"):
        return "女"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default="", help="只拆名字含该串的卡")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--no-bucket", action="store_true", help="不修假多部位标记")
    a = ap.parse_args()

    d = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = d["items"]
    ridx = row_index()
    print("fashion_data 行", len(ridx))

    exp = PackExporter()
    stat = Counter()
    out = []
    touched = 0

    for it in items:
        part_raw = str(it.get("part") or "")
        if "/" not in part_raw or (a.only and a.only not in it["name"]):
            if not a.no_bucket and "/" not in part_raw and len(it.get("part_bucket") or []) > 1:
                it["part_bucket"] = [part_raw]
                it["part_label"] = part_raw
                it["parts_raw"] = [part_raw]
                stat["假多部位已修"] += 1
                touched += 1
            out.append(it)
            continue

        # 按行分组
        groups = defaultdict(list)
        unknown = []
        for rk in (it.get("row_keys") or []):
            m = ridx.get(rk)
            if not m:
                unknown.append(rk)
                continue
            groups[m["part"]].append(rk)
        if unknown:
            groups[part_raw.split("/")[0] if groups else part_raw].extend(unknown)
            stat["行未解（沿用原部位）"] += len(unknown)
        if len(groups) < 2:
            stat["分组不足，跳过"] += 1
            out.append(it)
            continue

        mid = it.get("model_id")
        old_imgs = {nb(x.get("base")): x for x in ((it.get("_media") or {}).get("images") or [])}

        for part, rks in sorted(groups.items(), key=lambda kv: PART_ORDER.get(kv[0], 9)):
            rows = [ridx[k] for k in rks]
            paths = []
            for r in rows:
                for p in r["icons"]:
                    if p not in paths:
                        paths.append(p)
            # 名字：desc 前缀优先（表里 name 不带部位后缀）
            # 名字 = 表字段 name + 部位后缀（name 是权威字段；desc 前缀有时是简称，
            # 如「青鸾之誓」的 desc 写成「青鸾-衣服(永久款)」，用 desc 会把名字截断）
            nm = it["name"]
            if not nm.endswith("-" + part):
                nm = "%s-%s" % (nm, part)

            nid = new_id(nm, part, mid)
            card = {k: v for k, v in it.items() if k not in ("_media", "icons_all", "part_bucket", "parts_raw")}
            card["id"] = nid
            card["name"] = nm
            card["part"] = part
            card["part_bucket"] = [part]
            card["part_label"] = part
            card["parts_raw"] = [part]
            card["row_keys"] = sorted(rks)
            card["part_source"] = "fashion_data.part_type（拆卡按行重算）"

            charms = [r["charm"] for r in rows if isinstance(r["charm"], int)]
            levels = [r["level"] for r in rows if isinstance(r["level"], int)]
            days = sorted({r["days"] for r in rows if isinstance(r["days"], int) and r["days"] > 0})
            perm = any(r["days"] in (None, 0) for r in rows)
            card["charm_value"] = (max(charms) if charms else None)
            card["grade_level"] = (max(levels) if levels else None)
            card["grade_levels"] = sorted(set(levels))
            card["durations"] = days
            card["duration_variants"] = days
            card["time_limited_variants"] = days
            card["has_permanent"] = perm
            card["duration_state"] = ("mixed" if perm and days else
                                      ("permanent" if perm else ("timed" if days else "unknown")))
            body = ""
            for r in rows:
                t = str(r.get("desc") or "")
                t = re.sub(r"^[^。]*[（(](永久款|\d+天[^）)]*)[）)]。?", "", t).strip()
                t = re.sub(r"^#r", "", t).strip()
                if len(t) > len(body):
                    body = t
            if body:
                card["desc"] = body
            variants = sorted({r["name"] for r in rows if r.get("name")})
            if variants:
                card["name_variants"] = variants

            # 图片：按本组图标重挂（同一卡可能有多张同性别图，文件名要带序号，否则互相覆盖）
            imgs, missing = [], []
            seen = Counter()
            for p in paths:
                g = split_gender(p)
                code = "m" if g == "男" else ("f" if g == "女" else "x")
                seen[code] += 1
                fn = "%s_%s%s.png" % (nid, code, "" if seen[code] == 1 else str(seen[code]))
                key = nb(p)
                cand = None
                if key in old_imgs and (WEB / str(old_imgs[key].get("png") or "")).is_file():
                    cand = old_imgs[key]
                rp = refs_hit(p)
                if rp:
                    dst = POSTERS / fn
                    if not a.dry:
                        POSTERS.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(rp, dst)
                    if a.dry or dst.is_file():
                        imgs.append({"png": str(dst.relative_to(WEB)).replace("\\", "/"), "base": key,
                                     "label": g or "图示", "source": "拆卡：%s → refs %s" % (p, rp.name),
                                     "fetch": "refs", "bytes": rp.stat().st_size})
                        continue
                if cand:
                    imgs.append({"png": cand["png"], "base": key, "label": g or cand.get("label") or "图示",
                                 "source": "拆卡：沿用原卡同 base 图", "fetch": cand.get("fetch")})
                    continue
                if a.no_fetch:
                    missing.append({"base": key, "gender": g, "why": "拆卡未实导"})
                    continue
                dst = POSTERS / fn
                src = "" if a.dry else exp.export(p, dst)
                if src and dst.is_file():
                    imgs.append({"png": str(dst.relative_to(WEB)).replace("\\", "/"), "base": key,
                                 "label": g or "图示", "source": "拆卡实导：%s" % src, "fetch": src,
                                 "bytes": dst.stat().st_size})
                else:
                    if dst.exists():
                        dst.unlink()
                    missing.append({"base": key, "gender": g, "why": "PE/PC/refs 均无"})
            imgs.sort(key=lambda x: 0 if x.get("label") == "女" else (1 if x.get("label") == "男" else 2))
            card["_media"] = {"images": imgs, "total": len(imgs)}
            if missing:
                card["_media"]["missing"] = missing
                card["gender_icon_state"] = "缺%s图" % "/".join(sorted({m["gender"] for m in missing if m["gender"]}))
            card["icon_count"] = len(imgs)
            card["icon_state"] = "有图" if imgs else "无独立图标"
            card["icons_all"] = [{"path": p, "gender": split_gender(p),
                                  "png": next((x["png"] for x in imgs if x["base"] == nb(p)), None)}
                                 for p in paths]
            card["split_from"] = it["id"]
            if isinstance(it.get("appearance_merge"), dict):
                am = it["appearance_merge"]
                ids, parts = am.get("ids") or [], am.get("parts") or []
                if len(ids) == len(parts):
                    keep = [i for i, pp in enumerate(parts) if pp == part]
                    if keep:
                        card["appearance_merge"] = {**am, "ids": [ids[i] for i in keep],
                                                    "parts": [parts[i] for i in keep]}
                    else:
                        card.pop("appearance_merge", None)
                elif part != "衣服":
                    card.pop("appearance_merge", None)
            out.append(card)
            stat["拆出卡"] += 1
            print("  拆 %-22s → %-26s %s  行键 %s  图 %d  魅力 %s" % (
                it["name"], card["name"], part, rks, len(imgs), card.get("charm_value")))
        touched += 1

    if not a.dry:
        d["items"] = out
        if d.get("meta"):
            st = d["meta"].get("state_summary") or {}
            st["有图"] = sum(1 for x in d["items"] if x.get("icon_state") == "有图")
            st["无图"] = len(d["items"]) - st["有图"]
            d["meta"]["state_summary"] = st
            if isinstance(d["meta"].get("rebuild"), dict):
                d["meta"]["rebuild"]["cards"] = len(d["items"])
            d["meta"]["notes"] = (d["meta"].get("notes") or "") + (
                "\n\n【同套多部位拆卡（2026-10-29）】\n"
                "历史脚本 merge_fashion_part_cards.py 曾把「同 name + 同 model」的衣服/头饰并成一张卡，"
                "导致两件的行键、图、魅力值糊在一起。本次按 fashion_data 每行的 part_type 重新分组拆开："
                "%d 张合并卡 → 拆出 %d 张单部位卡，各行键/图标/魅力/品级独立；"
                "另修正 %d 张「part 单部位但 part_bucket 写成多部位」的筛选标记。\n" % (
                    touched, stat["拆出卡"], stat["假多部位已修"]))
        BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                            + json.dumps(d, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-18s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(out)))
    print("（dry-run，未写盘）" if a.dry else "已写回 json + js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
