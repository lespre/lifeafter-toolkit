# -*- coding: utf-8 -*-
"""时装图标双重校对（只读资源，产出校验图/CSV/JSON）。

任务口径（2026-10-18）：
  ① gpk_loc0 命中率：每张 images[].png 对应的真实资源路径 base+suffix+.ktx
     → toolkit_core.path_fid.fid_of → %016X，查客户端自己的全局文件索引
     `03_执行/30_分析/热更检测/pe_file_index/gpk_loc0`（16 字节/条：[u64 fid][u32][u32]）
  ② 部位自洽：hat→icon_h_ / bag→icon_bag_ / cloth→icon_b_|icon_cloth_ / suit→icon_suit_|icon_
     多部位件按「任一部位允许的前缀」判定
  ③ 30 条抽样联系表（PNG），每行标 名字 + 部位 + 图标基名

产出：
  04_站点/web/assets/fashion_icon_refs/_校对_30条.png
  04_站点/web/assets/fashion_icon_refs/_suspects.csv
  04_站点/web/data/media/fashion_icon_audit.json
"""
from __future__ import annotations

import csv
import json
import struct
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # 04_站点/web
PROJ = Path("E:/la拆包项目")
LOC0 = PROJ / "03_执行/30_分析/热更检测/pe_file_index/gpk_loc0"
REFS = ROOT / "data/media/fashion_icon_refs.json"
BOARD = ROOT / "data/boards/fashion_wardrobe.json"
PNG_DIR = ROOT / "assets/fashion_icon_refs"
OUT_PNG = PNG_DIR / "_校对_30条.png"
OUT_CSV = PNG_DIR / "_suspects.csv"
OUT_JSON = ROOT / "data/media/fashion_icon_audit.json"
CST = timezone(timedelta(hours=8))

sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

# ── 部位 → 允许的图标前缀（任务口径；多部位取并集）──
RULE = {
    "hat": ("icon_h_",),
    "bag": ("icon_bag_",),
    "cloth": ("icon_b_", "icon_cloth_"),
    "suit": ("icon_suit_", "icon_"),
}
CN = {"hat": "头饰", "bag": "背包", "cloth": "衣服", "suit": "整套", "light": "光源"}


def load_fids() -> set[int]:
    raw = LOC0.read_bytes()
    return {struct.unpack_from("<Q", raw, i)[0] for i in range(0, len(raw) - 15, 16)}


def stem_of(base: str) -> str:
    return base.rsplit("/", 1)[-1]


def prefixes_of(part: str) -> tuple[str, ...] | None:
    """返回该件允许的前缀集合；无法判定（整套/光源/空）返回 None = 不校验。"""
    parts = [p for p in str(part or "").split("/") if p]
    if not parts:
        return None
    if set(parts) <= {"整套", "light"}:
        return None          # 整套/光源没有图标命名约定 → 不做规则判定
    allowed: list[str] = []
    for p in parts:
        allowed.extend(RULE.get(p, ()))
    return tuple(dict.fromkeys(allowed)) if allowed else None


def main() -> int:
    fids = load_fids()
    refs = json.loads(REFS.read_text(encoding="utf-8"))
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    bmap = {x["id"]: x for x in board["items"]}

    rows, suspects = [], []
    sus_map = {}      # (item_id, base) → 合并同基名的 _b/_s 两条，避免 CSV 里重复行
    n_img = n_hit = 0
    png_missing = 0
    per_item_hit = 0
    items_with_img = 0
    miss_refs_total = miss_refs_inpack = 0
    by_part = defaultdict(lambda: {"imgs": 0, "hit": 0})

    for it in refs["items"]:
        imgs = it.get("images") or []
        if imgs:
            items_with_img += 1
        ok_all = True
        bucket = (bmap.get(it["id"], {}).get("part_bucket") or [CN.get(it.get("part"), it.get("part"))])
        allowed = prefixes_of(it.get("part"))
        for im in imgs:
            n_img += 1
            path = str(im["base"]) + str(im.get("suffix") or "") + ".ktx"
            f = fid_of(path)
            hit = f in fids
            n_hit += hit
            by_part[it.get("part")][("imgs")] += 1
            by_part[it.get("part")][("hit")] += 1 if hit else 0
            ok_all = ok_all and hit
            png = ROOT / str(im.get("png") or "")
            png_ok = bool(im.get("png")) and png.is_file()
            if not png_ok:
                png_missing += 1
            st = stem_of(im["base"])
            reason = []
            if not hit:
                reason.append("gpk_loc0 未命中")
            if not png_ok:
                reason.append("PNG 缺失")
            if allowed and not st.startswith(allowed):
                reason.append("部位前缀不符（%s 应为 %s）" % (
                    it.get("part"), "/".join(x.rstrip("_") + "_*" for x in allowed)))
            if reason:
                key = (it.get("id"), str(im["base"]))
                if key in sus_map:
                    sus_map[key]["refs"] += 1
                else:
                    sus_map[key] = {
                        "item": it.get("name"), "id": it.get("id"), "part": it.get("part"),
                        "bucket": "/".join(bucket), "icon": st, "png": im.get("png") or "",
                        "fid": "%016X" % f, "reason": "；".join(reason), "refs": 1,
                    }
            rows.append({"item_id": it["id"], "name": it.get("name"), "part": it.get("part"),
                         "icon": st, "fid": "%016X" % f, "hit": hit, "png_ok": png_ok})
        per_item_hit += ok_all and bool(imgs)
        # 表里声明但客户端没下发的引用：反向核对，确认「缺席」不是索引读法错了
        for m in it.get("missing") or []:
            miss_refs_total += 1
            base = str(m.get("base") or "")
            for sfx in ("_b", "_s"):
                if fid_of(base + sfx + ".ktx") in fids:
                    miss_refs_inpack += 1
                    k2 = (it.get("id"), base + sfx)
                    if k2 not in sus_map:
                        sus_map[k2] = {
                            "item": it.get("name"), "id": it.get("id"), "part": it.get("part"),
                            "bucket": "/".join(bucket), "icon": stem_of(base) + sfx,
                            "png": "", "fid": "%016X" % fid_of(base + sfx + ".ktx"),
                            "reason": "标为未下发，但 gpk_loc0 有该 fid（索引/绑定可补）", "refs": 1,
                        }
                    break

    suspects = sorted(sus_map.values(), key=lambda s: (s["reason"].startswith("标为未下发"), s["item"] or ""))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "part", "bucket", "icon", "png", "fid", "reason", "refs", "id"])
        w.writeheader()
        for s in suspects:
            w.writerow({k: s.get(k, "") for k in w.fieldnames})

    stats = {
        "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
        "loc0": {"path": str(LOC0.relative_to(PROJ)).replace("\\", "/"),
                 "records": len(fids), "entry_bytes": 16},
        "items": len(refs["items"]),
        "items_with_img": items_with_img,
        "images": n_img,
        "gpk_loc0_hit": n_hit,
        "gpk_loc0_hit_rate": round(100.0 * n_hit / max(1, n_img), 2),
        "items_all_imgs_hit": per_item_hit,
        "png_missing": png_missing,
        "declared_missing_refs": miss_refs_total,
        "declared_missing_but_in_loc0": miss_refs_inpack,
        "suspects": len(suspects),
        "by_part": {k: dict(v) for k, v in by_part.items()},
        "rule": ("hat→icon_h_* / bag→icon_bag_* / cloth→icon_b_*|icon_cloth_* / "
                 "suit→icon_suit_*|icon_*；多部位按并集；整套/光源不设命名约定"),
    }
    OUT_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))

    # ── 30 条联系表：按部位分层抽样（每桶最多 6 条），不足用各桶轮转补 ──
    by_bucket = defaultdict(list)
    for it in refs["items"]:
        bk = (bmap.get(it["id"], {}).get("part_bucket") or ["其他"])[0]
        by_bucket[bk].append(it)
    order = ["头饰", "衣服", "背包", "整套", "光源", "其他"]
    sample = []
    for bk in order:
        lst = sorted(by_bucket.get(bk) or [], key=lambda x: x["id"])
        if not lst:
            continue
        step = max(1, len(lst) // 6)
        take = lst[::step][:6]
        sample.extend(take)
    # 补到 30：把 suspects 涉及的外观补进来（有图才算）
    if len(sample) < 30:
        seen = {x["id"] for x in sample}
        for s in suspects:
            it = next((x for x in refs["items"] if x["id"] == s["id"]), None)
            if it and it["id"] not in seen and it.get("images"):
                sample.append(it)
                seen.add(it["id"])
            if len(sample) >= 30:
                break
    sample = sample[:30]

    from PIL import Image, ImageDraw, ImageFont
    W, RH, TH = 1180, 118, 104
    H = RH * len(sample) + 10
    sheet = Image.new("RGB", (W, H), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    try:
        f_name = ImageFont.truetype(str(font_path), 17)
        f_small = ImageFont.truetype(str(font_path), 13)
    except Exception:
        f_name = f_small = ImageFont.load_default()
    y = 5
    for it in sample:
        im0 = (it.get("images") or [{}])[0]
        png = ROOT / str(im0.get("png") or "")
        d.rectangle([6, y, W - 6, y + RH - 8], fill=(255, 255, 255), outline=(226, 226, 232))
        if png.is_file():
            try:
                with Image.open(png) as im:
                    im = im.convert("RGBA")
                    im.thumbnail((TH, TH - 12))
                    bg = Image.new("RGBA", im.size, (246, 246, 250, 255))
                    bg.alpha_composite(im)
                    sheet.paste(bg.convert("RGB"), (14, y + (RH - 12 - im.height) // 2))
            except Exception:
                d.text((18, y + 40), "读图失败", fill=(190, 60, 60), font=f_small)
        else:
            d.text((18, y + 40), "无图/占位", fill=(150, 150, 160), font=f_small)
        bk = "/".join(bmap.get(it["id"], {}).get("part_bucket") or [])
        nm = it.get("name") or ""
        d.text((132, y + 16), nm, fill=(24, 24, 27), font=f_name)
        d.text((132, y + 44), f"部位：{it.get('part')}（{bk}）", fill=(82, 82, 91), font=f_small)
        d.text((132, y + 64), f"图标：{stem_of(im0.get('base', '')) or '（无）'}", fill=(82, 82, 91), font=f_small)
        d.text((132, y + 84), f"PNG：{im0.get('png') or '（无）'}", fill=(140, 140, 150), font=f_small)
        bad = next((s for s in suspects if s["id"] == it["id"]), None)
        if bad:
            d.text((W - 300, y + 16), "⚠ 校对疑点", fill=(180, 83, 9), font=f_small)
            d.text((W - 300, y + 36), bad["reason"][:26], fill=(180, 83, 9), font=f_small)
        y += RH
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_PNG)
    print("联系表 →", OUT_PNG, f"{W}x{H}", "| 行数", len(sample))
    print("疑点 →", OUT_CSV, "| 条数", len(suspects))
    for s in suspects[:10]:
        print("  ·", s["item"], "|", s["part"], "|", s["icon"], "|", s["reason"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
