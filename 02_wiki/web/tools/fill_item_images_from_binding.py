# -*- coding: utf-8 -*-
"""用 pe_icon_bind/binding_rows_v2.jsonl 给 item_master_full 灌图。

流程：item_id → icon 路径 → 绑定行(pkg,row) → android_gpk 解该行 → PNG → 回写 _media
只处理「绑定校验全过」的行；解不出的记原因，不伪造。
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

BIND = PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind/binding_rows_v2.jsonl"
MAP = PROJ / "01_索引与产物/30_分析/子代理产出_20261022/item_icon_map_resolved.json"
BOARD = PROJ / "02_wiki/web/data/boards/item_master_full.json"
OUT = PROJ / "02_wiki/web/assets/img_cache/item_master_full"
GPK_DIR = pathlib.Path("E:/mrzh/Documents/gres")
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bind = {}
    with BIND.open(encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if not r.get("path"):
                continue
            ok = r.get("in_pkg") and r.get("dims_exact", True) and r.get("hdr_ok", True)
            if ok:
                bind[r["path"].replace("\\", "/")] = r
    print("可用绑定", len(bind))

    m = json.loads(MAP.read_text(encoding="utf-8"))
    path2ids = defaultdict(list)
    for iid, p in m.items():
        path2ids[p.replace("\\", "/")].append(str(iid))

    need = defaultdict(dict)          # pkg -> {row: [items(path)]}
    for path, rec in bind.items():
        if path not in path2ids:
            continue
        need[rec["pkg"]].setdefault(int(rec["row"]), []).append(path)

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    by_item = {}
    for it in board["items"]:
        iid = str(it.get("item_id") or it.get("id", "")).replace("item_", "")
        by_item[iid] = it

    done = 0
    for pkg, rows in sorted(need.items()):
        p = GPK_DIR / pkg
        if not p.exists():
            print("缺包", p); continue
        todo = set(rows)
        print("扫 %s（需 %d 行）" % (pkg, len(todo)))
        got = 0
        for e in AG.iter_entries(str(p), include_empty=False):
            if e["row"] not in todo:
                continue
            data = e.get("payload")
            if not data:
                continue
            rec = {"kind": e.get("kind"), "data": data}
            if data.startswith(b"\xabKTX"):
                info = AG.parse_ktx(data)
                if not info:
                    continue
                rec.update(kind="ktx", info=info)
            elif data.startswith(b"DDS "):
                rec.update(kind="dds")
            elif data.startswith(b"\x89PNG"):
                rec.update(kind="png")
            else:
                continue
            for path in rows[e["row"]]:
                for iid in path2ids[path]:
                    it = by_item.get(iid)
                    if not it:
                        continue
                    dst = OUT / (iid + ".png")
                    try:
                        AG.save_png(rec, dst)
                    except Exception:
                        continue
                    it["_media"] = {"images": [{"png": "assets/img_cache/item_master_full/%s.png" % iid,
                                                "label": "图标"}], "total": 1}
                    done += 1
                    got += 1
            todo.discard(e["row"])
            if done >= LIMIT:
                break
            if done % 500 == 0:
                BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
        print("  %s 完成 %d 条（累计 %d）" % (pkg, got, done))

    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    n = sum(1 for i in board["items"] if (i.get("_media") or {}).get("images"))
    print("最终有图 %d / %d" % (n, len(board["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
