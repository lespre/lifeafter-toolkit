# -*- coding: utf-8 -*-
r"""补「配置无行、但资源与名字都在包里」的时装子卡。

来源三角（缺一不可）：
  ① 名字：`com/cdata/fashion_data_chs.py` 池里逐字存在（不做拼接臆造）
  ② 图标：`ui/item_icon/icon_{h|b}_{f|m}_<model>001_b.ktx` 能在 pe_index 按 fid 定位
  ③ 归属：与已存在的同 model 服装卡同 model 编号

产出卡的证据等级固定为 resource-claimed：
  卡面只写 名字 / 部件 / 图；row_key、charm、desc、获取途径 一律留空。
  技术详情里写清：池偏移、图标 fid、包:行。

用法：
  python tools/build_resource_claimed_cards.py --dry-run
  python tools/build_resource_claimed_cards.py --apply [--limit N]
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sqlite3
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
CDC = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
POOL = CDC / "fashion_data_chs.py"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT_IMG = PROJ / "02_wiki/web/assets/fashion_posters/pe_resource_claimed"

TIME_RE = re.compile(r"-(1|3|5|7|14|30)天$")


def base(n: str) -> str:
    n = (n or "").strip()
    prev = None
    while prev != n:
        prev = n
        n = TIME_RE.sub("", n).strip()
    return n


def load_cfg():
    src = sorted((PROJ / "01_索引与产物/30_分析").glob("表结构解析_*/结构"))[-1]
    rows = []
    for name in ("fashion_data_chs.py.rows.csv",
                 "fashion_data_auto_oversea_data_kjxq_chs.py.rows.csv"):
        p = src / name
        if not p.is_file():
            continue
        with p.open(encoding="utf-8", errors="ignore", newline="") as f:
            for r in csv.DictReader(f):
                rows.append({k.lstrip("\ufeff"): v for k, v in r.items()})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    apply = a.apply and not a.dry_run

    pool = POOL.read_bytes()
    rows = load_cfg()
    by_model = {}
    for r in rows:
        pt = (r.get("part_type") or "").strip()
        mid = (r.get("model_id") or "").strip()
        nm = base(r.get("name"))
        if pt not in ("cloth", "hat") or not mid or not nm:
            continue
        g = by_model.setdefault(mid, {"cloth": set(), "hat": set()})
        g[pt].add(nm)
    print("配置 model 数", len(by_model))

    cands = []
    for mid, g in by_model.items():
        if g["cloth"] and not g["hat"]:
            for nm in sorted(g["cloth"]):
                cands.append((mid, "头饰", nm, "h"))
        elif g["hat"] and not g["cloth"]:
            for nm in sorted(g["hat"]):
                cands.append((mid, "衣服", nm, "b"))
    print("候选（配置缺对侧部件）", len(cands))

    # 名字存在性 + 图标存在性
    con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    from toolkit_core.path_fid import fid_of

    named, resolvable, rejected_name, rejected_icon = [], [], 0, 0
    seen = set()
    for mid, want_part, have_name, kind in cands:
        core = have_name
        for suf in ("-衣服", "-头饰"):
            if core.endswith(suf):
                core = core[: -len(suf)]
        cand_name = f"{core}-{want_part}"
        if cand_name in seen:
            continue
        if cand_name.encode("utf-8") not in pool:
            rejected_name += 1
            continue
        off = pool.find(cand_name.encode("utf-8"))
        icons = []
        for sex in ("f", "m"):
            path = f"ui/item_icon/icon_{kind}_{sex}_{mid}001_b.ktx"
            fid = "%016X" % (fid_of(path) & 0xFFFFFFFFFFFFFFFF)
            row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
            if row:
                icons.append((sex, path, fid, row[0], row[1]))
        if not icons:
            rejected_icon += 1
            continue
        seen.add(cand_name)
        named.append((mid, want_part, cand_name, off, icons))

    print(f"名字在池里且在包里有图：{len(named)} ｜ 名字不在池里 {rejected_name} ｜ 有名字无图 {rejected_icon}")
    for it in named[:10]:
        print("   ", it[0], it[2], "池偏移", it[3], "图", [(x[0], x[3], x[4]) for x in it[4]])

    if not apply:
        print("\n（dry-run：未写板、未导图）")
        return 0

    OUT_IMG.mkdir(parents=True, exist_ok=True)
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    existing = {i["name"] for i in items}
    todo = [x for x in named if x[2] not in existing]
    if a.limit:
        todo = todo[: a.limit]
    print("待写入卡", len(todo))

    added = 0
    for mid, part, name, off, icons in todo:
        imgs = []
        for sex, path, fid, pack, row in icons:
            out = OUT_IMG / f"{path.rsplit('/', 1)[-1].replace('.ktx', '')}.png"
            if not out.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export",
                                path[:-4], str(out)],
                               capture_output=True, text=True)
            if out.is_file():
                imgs.append({
                    "png": str(out.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                    "label": "图示1",
                    "source": "PE 测试服 · ui/item_icon",
                })
        if not imgs:
            continue
        items.append({
            "id": f"fw_rc_{mid}_{'h' if part == '头饰' else 'c'}",
            "name": name,
            "part": part,
            "part_label": part,
            "part_bucket": [part],
            "model_id": int(mid) if mid.isdigit() else mid,
            "model_ids": [int(mid)] if mid.isdigit() else [mid],
            "grade_level": None,
            "charm_value": None,
            "gender": "女/男",
            "desc": None,
            "row_keys": [],
            "icon_state": "有图",
            "icon_count": len(imgs),
            "_media": {"images": imgs, "total": len(imgs)},
            "status_tags": ["resource claimed"],
            "source": "PE 测试服 · 池串 + 图标（配置无行）",
            "evidence": "resource",
            "evidence_level": "resource-claimed",
            "provenance": {
                "source_id": "fashion-resource-claimed",
                "table": "com\\cdata\\fashion_data_chs.py",
                "row_key": None,
                "field_refs": ["name"],
                "name_source": f"fashion_data_chs.py 池偏移 {off}",
                "icon_source": "PE ui/item_icon（.ktx → png）",
                "locator_chain": {
                    "chain_status": "resource-only",
                    "scope": "resource",
                    "steps": [{
                        "kind": "pool-string",
                        "offset": off,
                        "text": name,
                    }] + [{
                        "kind": "icon-fid",
                        "sex": sc,
                        "path": pa,
                        "fid": fi,
                        "pack": pk,
                        "row": rw,
                    } for sc, pa, fi, pk, rw in icons],
                },
            },
        })
        added += 1

    board["items"] = items
    meta = board.setdefault("meta", {})
    meta["resource_claimed"] = {
        "count": sum(1 for i in items if i.get("evidence_level") == "resource-claimed"),
        "rule": "池串逐字存在 + 图标 fid 可定位 + 与同 model 服装卡对齐；无 row_key/charm/desc",
        "added_at": "2026-11-01",
    }
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print(f"写入完成：新增 {added} 卡 ｜ 板块总数 {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
