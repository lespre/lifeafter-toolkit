# -*- coding: utf-8 -*-
"""把 fashion_registry.json 生成成 wiki 板块 data/boards/fashion_registry.json。"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT, WEB  # noqa: E402

REG = WEB / "data/fashion_registry.json"
OUT = WEB / "data/boards/fashion_registry.json"

SRC = ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata"
       "（fashion_data.py、player_appear_data.py、simple_fashion_data.py）"
       " · 资源 41_还原树/pe/资源")


def _locks() -> list:
    import hashlib as _h
    base = pathlib.Path(TREE_ROOT / "pe/配置/com/cdata")
    out = []
    for name in ("fashion_data.py", "player_appear_data.py", "simple_fashion_data.py"):
        f = base / name
        if not f.is_file():
            continue
        b = f.read_bytes()
        st = f.stat()
        out.append({"source_id": "pe-cdata-" + name.replace(".py", ""), "role": "primary",
                    "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/" + name,
                    "sha256": _h.sha256(b).hexdigest(), "bytes": len(b), "mtime_ns": st.st_mtime_ns})
    return out


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    rows = reg["rows"]
    by_key = {}
    for r in rows:
        k = "%s|%s" % (r["base"], r["model_id"])
        by_key.setdefault(k, {"rows": [], "parts": set(), "tables": set()})
        d = by_key[k]
        d["rows"].append(r)
        if r["part"]:
            d["parts"].add(r["part"])
        d["tables"].add(r["table"])

    items = []
    for k, d in by_key.items():
        rs = d["rows"]
        base = k.split("|")[0]
        model = k.split("|")[1]
        lv = [r["level"] for r in rs if isinstance(r["level"], int)]
        ch = [r["charm"] for r in rs if isinstance(r["charm"], (int, float))]
        desc = next((r["desc"] for r in rs if r["desc"]), "")
        items.append({
            "id": "freg_" + hashlib.md5(k.encode()).hexdigest()[:10],
            "name": base,
            "model_id": model,
            "parts": sorted(d["parts"]),
            "parts_text": "、".join(sorted(d["parts"])) or "未标",
            "tables": sorted(d["tables"]),
            "row_count": len(rs),
            "row_keys": [r["key"] for r in rs][:12],
            "level": max(lv) if lv else None,
            "charm": max(ch) if ch else None,
            "desc": desc[:160],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": " / ".join(sorted(d["tables"])),
        })
    items.sort(key=lambda x: (x["name"], str(x["model_id"])))

    board = {
        "meta": {
            "name": "时装全量登记表",
            "category": "一、时装类 / （一）人物时装",
            "source_server": SRC,
            "source_label": SRC,
            "generated": "2026-10-25",
            "id_label": "套装行数",
            "evidence": "structure",
            "card_mode": "roster",
            "filters": [{"key": "parts_text", "label": "部位"},
                        {"key": "source", "label": "来源表"}],
            "card_summary": [["parts_text", "部位"], ["source", "来源表"],
                             ["level", "品级"], ["charm", "魅力值"], ["desc", "描述"]],
            "notes": ("三源合并的全量登记：fashion_data（%d 行）+ player_appear_data（%d 行）+ "
                      "simple_fashion_data（%d 行），按「基名 + model_id」归并成 %d 张套装卡。"
                      % (sum(1 for r in rows if r["table"] == "fashion_data"),
                         sum(1 for r in rows if r["table"] == "player_appear_data"),
                         sum(1 for r in rows if r["table"] == "simple_fashion_data"),
                         len(items))),
            "registry": "data/fashion_registry.json",
            "state_summary": {},
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": _locks(),
                "source_scope": {"cross_source_policy": "三表合并，按基名+model_id 归并", "integer_join_policy": "model_id 整型直连，不做取整/掩码", "runtime_final_policy": "静态配置为准，运行时外观未核"},
            },
        },
        "items": items,
    }
    payload = json.dumps(board, ensure_ascii=False)
    board["meta"]["package_sha"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    OUT.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("生成 %s ｜ %d 张卡 ｜ 部位分布 %s"
          % (OUT.name, len(items), Counter(i["parts_text"] for i in items).most_common(5)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
