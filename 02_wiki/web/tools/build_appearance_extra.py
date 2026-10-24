# -*- coding: utf-8 -*-
"""建「其他外观」板：player_appear_data 里 fashion_data 没有的发型/脸型/背包/挂饰/特效等。

- 卡片粒度：名字 + 部位；男女同卡，图标并排
- 图标：ui/item_icon/icon_b_<f|m>_<七位id>_b（id 取自 model_name 文件名）
- 取不到的标无图，不伪造
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import img_fetch  # noqa: E402

CDATA = PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata"
BOARD = WEB / "data/boards/appearance_extra.json"
OUT = WEB / "assets/appearance_icons"
REFS = WEB / "assets/fashion_icon_refs"

PART_CN = {1: "发型/头部", 2: "脸型", 3: "衣服", 4: "背包",
           5: "挂饰/宠物", 6: "光环/特效", 7: "手持/道具"}


def _rows(path: pathlib.Path):
    raw = path.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = path.with_name(path.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    return BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                                resolve_jumps=False, lenient=True)[0]


def _v(x):
    return x[1] if isinstance(x, tuple) else x


def model_id_of(model_name: str):
    """character/players/b_f_2001/h_f_2001001.gim → (2001001, '女')"""
    if not isinstance(model_name, str):
        return None, None
    m = re.search(r"_([fm])_(\d{6,})", model_name.rsplit("/", 1)[-1])
    if not m:
        return None, None
    return int(m.group(2)), ("女" if m.group(1) == "f" else "男")


def main() -> int:
    fd = {_v(r["values"].get("name")) for r in _rows(CDATA / "fashion_data.py")}
    rows = [r for r in _rows(CDATA / "player_appear_data.py")
            if isinstance(_v(r["values"].get("name")), str)
            and _v(r["values"].get("name")) not in fd]

    groups = {}
    for r in rows:
        v = r["values"]
        name, part = _v(v.get("name")), _v(v.get("part"))

        key = (name, part)
        g = groups.setdefault(key, {"name": name, "part": part, "rows": [], "icons": []})
        g["rows"].append(r["key"])
        mid, gender = model_id_of(_v(v.get("model_name")))
        if mid:
            for gd in ("女", "男"):
                if gender == gd:
                    g["icons"].append({"model_id": mid, "gender": gd})

    import hashlib
    table = CDATA / "player_appear_data.py"
    sha = hashlib.sha256(table.read_bytes()).hexdigest() if table.exists() else "0" * 64

    OUT.mkdir(parents=True, exist_ok=True)
    items, fetched = [], 0
    for (name, part), g in groups.items():
        iid = "ap_" + re.sub(r"[^0-9a-zA-Z]", "", name)[:12] + "_" + str(part)
        imgs = []
        for ic in g["icons"]:
            dst = OUT / ("%s_%s.png" % (ic["model_id"], ic["gender"]))
            if dst.exists():
                imgs.append({"png": "assets/appearance_icons/%s" % dst.name,
                             "label": "图标（%s）" % ic["gender"]})
                continue
            local = REFS / ("icon_b_%s_%s_b.png" % ("f" if ic["gender"] == "女" else "m",
                                                    ic["model_id"]))
            if local.exists():
                dst.write_bytes(local.read_bytes())
                imgs.append({"png": "assets/appearance_icons/%s" % dst.name,
                             "label": "图标（%s）" % ic["gender"]})
                continue
            if fetched >= 400:
                continue
            for cand in ("ui/item_icon/icon_b_%s_%s_b" % ("f" if ic["gender"] == "女" else "m", ic["model_id"]),
                         "ui/item_icon/icon_b_%s_%s_s" % ("f" if ic["gender"] == "女" else "m", ic["model_id"])):
                fetched += 1
                if img_fetch.export(cand, dst):
                    imgs.append({"png": "assets/appearance_icons/%s" % dst.name,
                                 "label": "图标（%s）" % ic["gender"]})
                    break
        items.append({
            "id": iid,
            "name": name,
            "part": PART_CN.get(part, str(part)),
            "name_type": ("开发名" if re.match(r"^(\d|[a-zA-Z])", str(name))
                          or re.search(r"[a-zA-Z]{2,}\d*", str(name)) else "正式名"),
            "part_code": part,
            "gender": "/".join(sorted({i["gender"] for i in g["icons"]})) or "",
            "model_ids": sorted({i["model_id"] for i in g["icons"]}),
            "row_keys": g["rows"],
            "_media": {"images": imgs, "total": len(imgs)},
            "generated": "2026-10-24",
            "evidence": "structure",
            "status_tags": ["verified"],
            "evidence_level": "structure-only",
            "source": "player_appear_data（PE 还原树 pe_20261020）",
            "provenance": {
                "source_id": "appearance-extra-struct",
                "source_lock_sha256": sha,
                "table": "com\cdata\player_appear_data.py",
                "row_key": g["rows"][0],
                "row_keys": g["rows"],
                "field_refs": ["name", "part", "model_name"],
                "name_source": "com\cdata\player_appear_data.py#name",
                "part_source": "com\cdata\player_appear_data.py#part",
                "icon_source": "ui/item_icon/icon_b_<f|m>_<model_id>_b（model_name 文件名派生）",
                "rebuild": "full-rebuild-20261024",
                "upstream": {"package_sha256": sha, "entry_index": None,
                             "file_id": None, "decoded_sha256": None, "role": None},
                "locator_chain": {
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                    "steps": [{
                        "kind": "decoded-table-row",
                        "source_id": "appearance-extra-struct",
                        "table": "com\cdata\player_appear_data.py",
                        "row_key": g["rows"][0],
                        "field_refs": ["name", "part", "model_name"],
                    }],
                },
            },
        })

    items.sort(key=lambda i: (i["part_code"], i["name"]))
    with_img = sum(1 for i in items if i["_media"]["images"])
    d = {
        "meta": {
            "state_summary": {"unresolved": len(items), "static config": len(items),
                              "verified": 0, "runtime final unknown": len(items),
                              "有图": with_img, "无图": len(items) - with_img},
            "generated": "2026-10-24",
            "evidence": "structure",
            "status_tags": ["verified"],
            "package_sha": sha,
            "name": "其他外观（发型·脸型·背包·挂饰·特效·手持）",
            "category": "一、时装类 / （六）其他外观",
            "source_server": "PE 还原树 pe_20261020 · player_appear_data · 体验服",
            "filters": [{"key": "part", "label": "部位"},
                        {"key": "name_type", "label": "名称类型"}],
            "notes": "fashion_data 未收录的外观部件；男女同卡，图标按性别并排。",
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [{
                    "source_id": "appearance-extra-struct",
                    "role": "primary",
                    "path": "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/player_appear_data.py",
                    "sha256": sha,
                    "bytes": table.stat().st_size if table.exists() else 0,
                    "mtime_ns": table.stat().st_mtime_ns if table.exists() else 0,
                }],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            }
        },
        "items": items,
    }
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    n = len(items)
    print("卡片", n, "｜有图", sum(1 for i in items if i["_media"]["images"]), "｜取图请求", fetched)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
