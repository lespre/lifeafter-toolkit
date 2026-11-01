# -*- coding: utf-8 -*-
r"""补「板块缺对侧部件、但池里有名字且包里有图」的时装子卡（v2）。

分组口径用【板块自己的 model_id】（板块已是当前配置的投影，含 10-30 热更），
不用 9 月那份 CSV 快照。

三条判据（缺一不可）：
  ① 名字：fashion_data_chs.py 池里逐字存在
  ② 图标：ui/item_icon/icon_{h|b}_{f|m}_<model>001_b.ktx 能在 pe_index 定位
  ③ 归属：同 model_id 的另一部件卡已在板块里

产出证据等级固定 resource-claimed：row_key / charm / desc 一律留空。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
POOL = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_data_chs.py"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT_IMG = PROJ / "02_wiki/web/assets/fashion_posters/pe_resource_claimed"


def core_name(n: str) -> str:
    n = (n or "").strip()
    for suf in ("-衣服", "-头饰", "-头发"):
        if n.endswith(suf):
            return n[: -len(suf)].strip()
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    pool = POOL.read_bytes()
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    from toolkit_core.path_fid import fid_of
    con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)

    by_model = {}
    for it in items:
        mids = it.get("model_ids") or ([it["model_id"]] if it.get("model_id") else [])
        for m in mids:
            by_model.setdefault(str(m), []).append(it)

    existing_names = {i["name"] for i in items}
    plans, reject_name, reject_icon = [], 0, 0
    for mid, cards in sorted(by_model.items()):
        parts = {c.get("part") for c in cards}
        pairs = []
        if "衣服" in parts and not ({"头发", "头饰"} & parts):
            pairs.append(("头饰", "h"))
        if ("头发" in parts or "头饰" in parts) and "衣服" not in parts:
            pairs.append(("衣服", "b"))
        for want, kind in pairs:
            src = next((c for c in cards if c.get("part") in ("衣服", "头发", "头饰")), None)
            if not src:
                continue
            name = f"{core_name(src['name'])}-{want}"
            if name in existing_names:
                continue
            if name.encode("utf-8") not in pool:
                reject_name += 1
                continue
            off = pool.find(name.encode("utf-8"))
            icons = []
            for sex in ("f", "m"):
                path = f"ui/item_icon/icon_{kind}_{sex}_{mid}001_b.ktx"
                fid = "%016X" % (fid_of(path) & 0xFFFFFFFFFFFFFFFF)
                row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
                if row:
                    icons.append((sex, path, fid, row[0], row[1]))
            if not icons:
                reject_icon += 1
                continue
            plans.append({"model": mid, "part": want, "name": name, "offset": off,
                          "icons": icons, "from_card": src["name"]})

    print(f"板块条目 {len(items)} ｜ model {len(by_model)}")
    print(f"可补卡 {len(plans)} ｜ 名字不在池里 {reject_name} ｜ 有名字无图 {reject_icon}")
    for p in plans[:12]:
        print(f"   {p['model']}  {p['name']}  ← {p['from_card']}  图 {[(i[0], i[3], i[4]) for i in p['icons']]}")

    if not a.apply:
        print("\n（dry-run：未写板、未导图）")
        return 0

    OUT_IMG.mkdir(parents=True, exist_ok=True)
    todo = plans[: a.limit] if a.limit else plans
    added = 0
    for p in todo:
        imgs = []
        for sex, path, fid, pack, row in p["icons"]:
            out = OUT_IMG / f"{path.rsplit('/', 1)[-1].replace('.ktx', '')}.png"
            if not out.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(out)],
                               capture_output=True, text=True)
            if out.is_file():
                imgs.append({"png": str(out.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "label": "图示1", "source": "PE 测试服 · ui/item_icon"})
        if not imgs:
            continue
        items.append({
            "id": f"fw_rc_{p['model']}_{'h' if p['part'] == '头饰' else 'c'}",
            "name": p["name"], "part": p["part"], "part_label": p["part"],
            "part_bucket": [p["part"]],
            "model_id": int(p["model"]) if p["model"].isdigit() else p["model"],
            "model_ids": [int(p["model"])] if p["model"].isdigit() else [p["model"]],
            "grade_level": None, "charm_value": None, "gender": "女/男", "desc": None,
            "row_keys": [], "icon_state": "有图", "icon_count": len(imgs),
            "_media": {"images": imgs, "total": len(imgs)},
            "status_tags": ["resource claimed"],
            "source": "PE 测试服 · 池串 + 图标（配置无行）",
            "evidence": "resource", "evidence_level": "resource-claimed",
            "provenance": {
                "source_id": "fashion-resource-claimed",
                "table": "com\\cdata\\fashion_data_chs.py",
                "row_key": None,
                "field_refs": ["name"],
                "name_source": f"fashion_data_chs.py 池偏移 {p['offset']}",
                "icon_source": "PE ui/item_icon（.ktx → png）",
                "paired_with": p["from_card"],
                "locator_chain": {
                    "chain_status": "resource-only", "scope": "resource",
                    "steps": [{"kind": "pool-string", "offset": p["offset"], "text": p["name"]}]
                    + [{"kind": "icon-fid", "sex": s, "path": pa, "fid": fi, "pack": pk, "row": rw}
                       for s, pa, fi, pk, rw in p["icons"]],
                },
            },
        })
        added += 1

    board["items"] = items
    board.setdefault("meta", {})["resource_claimed"] = {
        "count": sum(1 for i in items if i.get("evidence_level") == "resource-claimed"),
        "rule": "池串逐字存在 + 图标 fid 可定位 + 同 model 对侧部件已在板",
        "added_at": "2026-11-01",
    }
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print(f"写入：新增 {added} 卡 ｜ 板块总数 {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
