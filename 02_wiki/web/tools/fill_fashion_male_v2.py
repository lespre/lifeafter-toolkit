# -*- coding: utf-8 -*-
"""用 fashion_data 的 icons 组反推男图：model_id → 该套注册的全部图标名。"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402
from PIL import Image  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"
v = lambda x: x[1] if isinstance(x, tuple) else x


def load_fashion():
    raw = (CD / "fashion_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, blob, pool


def main() -> int:
    rows, blob, pool = load_fashion()
    by_model: dict[str, set[str]] = {}
    for r in rows:
        val = r["values"]
        mid = v(val.get("model_id"))
        ic = val.get("icons")
        if mid is None or not isinstance(ic, tuple):
            continue
        try:
            grp = BT.read_27_group(blob, int(str(ic[1]).split(":")[1]))
        except Exception:  # noqa: BLE001
            continue
        if not grp:
            continue
        names = by_model.setdefault(str(mid), set())
        for i in grp[1]:
            if i < len(pool):
                nm = str(pool[i])
                if nm.startswith("ui/item_icon/"):
                    names.add(nm.split("/")[-1])
    print("model → 图标组 %d 个 model" % len(by_model), flush=True)

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    todo = []
    for it in board["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        if not imgs or any("男" in str(x.get("label", "")) for x in imgs):
            continue
        todo.append(it)
    print("仍缺男图卡 %d" % len(todo), flush=True)

    ok = fail = nomodel = 0
    t0 = time.time()
    for i, it in enumerate(todo, 1):
        mid = str(it.get("model_id"))
        names = by_model.get(mid) or set()
        males = [n for n in names if re.search(r"_m_|_1($|_)", n)] or sorted(names)
        cands = []
        for n in males:
            for suf in ("_b", "_s", ""):
                cands.append("ui/item_icon/%s%s" % (n, suf))
        if not names:
            nomodel += 1
        hit = ""
        dst = OUT / ("%s_m.png" % it["id"])
        for c in dict.fromkeys(cands):
            try:
                if pe_fetch.export(c, dst) and dst.is_file() and dst.stat().st_size > 512:
                    w, h = Image.open(dst).size
                    if w >= 64 and h >= 64:
                        hit = c
                        break
            except Exception:  # noqa: BLE001
                continue
        if hit:
            imgs = [x for x in it["_media"]["images"] if isinstance(x, dict)]
            imgs.append({"png": "assets/fashion_posters/%s_m.png" % it["id"],
                         "base": hit.split("/")[-1], "label": "男装",
                         "source": "PE · %s（按 model %s 图标组反推）" % (hit, mid)})
            it["_media"] = {"images": imgs, "total": len(imgs)}
            ok += 1
        else:
            fail += 1
            if dst.exists():
                dst.unlink()
        if i % 100 == 0:
            BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
            print("  [%d/%d] 命中 %d 失败 %d ｜ %.0fs" % (i, len(todo), ok, fail, time.time() - t0), flush=True)

    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("完成 命中 %d ｜ 失败 %d ｜ 其中无 model 图标组 %d ｜ %.0fs" % (ok, fail, nomodel, time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
