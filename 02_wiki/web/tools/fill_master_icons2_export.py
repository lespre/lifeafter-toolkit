#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量道具总表补图（第 2 轮）：把 item_master_full 里「源已定位未导出」的条目导出成 PNG。

取图三条路线（按优先级）：
  1. 还原树直解：41_还原树/pe/资源/<icon_path>{_b,_s,''}{.ktx,.dds}（扩展 .ktx 优先）
  2. 源包直读：pe_index.sqlite3 的 ui/% 行 → 解压 payload → 解码（还原树没铺到的）
  3. 站内既有 PNG 复用：assets/item_icons_full/<path 扁平名>[_b|_s].png（同一张图，不重解）

解码硬约束：RGBA8_ETC2_EAC 必须走 toolkit_core.android_gpk.parse_ktx + _ktx_rgba；
CompBlks 载荷走 pe_icon_bind.decoders.decode_compblks。**禁用 texture2ddecoder.decode_astc**
（对该格式会出噪声块）。

输出：02_wiki/web/assets/item_icons_full/<item_id>.png（已存在则跳过）
报告：01_索引与产物/30_分析/master_icon_export2_report.json

只读 PE 源；不改 41_还原树；不 commit。
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
OUT = WEB / "assets/item_icons_full"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
PE_INDEX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
BOARD = WEB / "data/boards/item_master_full.json"
REPORT = PROJ / "01_索引与产物/30_分析/master_icon_export2_report.json"

for _p in (PROJ / "00_规范与工具/工具/工具库/00_共享核心",
           PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

SUFFIXES = ("_b", "_s", "")
EXTS = (".ktx", ".dds")
TARGET_STATE = "源已定位未导出"


# ---------------- worker side ----------------
_AG = None
_DEC = None
_NP = None
_IMG = None
_PACK_CACHE: dict[str, tuple[bytes, list]] = {}


def _lazy():
    global _AG, _DEC, _NP, _IMG
    if _AG is None:
        from toolkit_core import android_gpk as AG
        import decoders as DEC
        import numpy as np
        from PIL import Image
        _AG, _DEC, _NP, _IMG = AG, DEC, np, Image
    return _AG, _DEC, _NP, _IMG


def _magenta_bad(arr, np) -> bool:
    al = arr[:, :, 3]
    op = al > 8
    n = int(op.sum())
    if n == 0:
        return True
    px = arr[op]
    mag = (px[:, 0] > 240) & (px[:, 1] < 16) & (px[:, 2] > 240)
    return mag.sum() / n > 0.30


def _decode(data: bytes):
    AG, DEC, np, _ = _lazy()
    if data.startswith(b"CompBlks"):
        arr = DEC.decode_compblks(data)
        if arr is None:
            raise ValueError("compblks_none")
        return np.ascontiguousarray(arr)
    info = AG.parse_ktx(data)
    if not info:
        raise ValueError("parse_ktx_empty")
    return np.ascontiguousarray(AG._ktx_rgba(data, info))


def _save(arr, tgt: Path) -> None:
    AG, DEC, np, Image = _lazy()
    if arr.ndim != 3 or arr.shape[2] != 4:
        raise ValueError(f"bad_shape{arr.shape}")
    if arr.dtype != np.uint8:
        raise ValueError(f"bad_dtype{arr.dtype}")
    h, w = arr.shape[0], arr.shape[1]
    if h < 8 or w < 8:
        raise ValueError("too_small")
    if int((arr[:, :, 3] > 8).sum()) < 64:
        raise ValueError("empty_alpha")
    if _magenta_bad(arr, np):
        raise ValueError("magenta_bg")
    Image.fromarray(arr).save(tgt, optimize=False, compress_level=6)


def _pack_payload(pack: str, row: int, off: int, packed: int, decoded: int, flag: int):
    AG, _, _, _ = _lazy()
    if pack not in _PACK_CACHE:
        if len(_PACK_CACHE) >= 2:
            _PACK_CACHE.clear()
        p = PACKS / pack
        rec, spans, _f = AG.open_blocks(str(p))
        _PACK_CACHE[pack] = (p.read_bytes(), spans)
    blob, spans = _PACK_CACHE[pack]
    h = AG._base_of(spans, row) + off
    if h + 20 > len(blob):
        return None
    return AG.decompress(blob[h + 20: h + 20 + packed], flag, decoded)


def work(task) -> tuple[str, str, str]:
    """task = (item_id, icon_path, route, payload) → (status, item_id, why)"""
    iid, icon_path, route, payload = task
    tgt = OUT / f"{iid}.png"
    if tgt.exists():
        return ("skip", iid, "")
    try:
        if route == "tree":
            data = (RES / payload).read_bytes()
            _save(_decode(data), tgt)
            return ("tree", iid, "")
        if route == "pack":
            data = _pack_payload(*payload)
            if not data:
                return ("fail", iid, "pack_payload_empty")
            _save(_decode(data), tgt)
            return ("pack", iid, "")
        if route == "flatpng":
            _, _, _, Image = _lazy()
            with Image.open(FLAT / payload) as im:
                arr = _NP.array(im.convert("RGBA"))
            _save(arr, tgt)
            return ("flatpng", iid, "")
        return ("fail", iid, "no_route")
    except Exception as exc:  # noqa: BLE001
        if tgt.exists():
            try:
                tgt.unlink()
            except OSError:
                pass
        return ("fail", iid, f"{route}:{type(exc).__name__}:{str(exc)[:60]}")


FLAT = OUT


# ---------------- parent side ----------------
def resolve_tree(icon_path: str):
    for suf in SUFFIXES:
        for ext in EXTS:
            q = RES / (icon_path + suf + ext)
            if q.is_file():
                return q.relative_to(RES).as_posix()
    return None


def load_pack_map():
    import sqlite3
    con = sqlite3.connect(f"file:{PE_INDEX.as_posix()}?mode=ro", uri=True, timeout=120)
    pm: dict[str, tuple] = {}
    for r in con.execute("select name,pack,row,off,packed,decoded,flag from rows where name like 'ui/%'"):
        pm.setdefault(r[0], tuple(r[1:]))
    con.close()
    return pm


def main() -> int:
    t0 = time.time()
    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    stat_before = Counter(i.get("icon_state") for i in items)
    todo = [i for i in items if i.get("icon_state") == TARGET_STATE]
    print(f"board items={len(items)} states={dict(stat_before)} target={len(todo)}", flush=True)

    tasks: list[tuple] = []
    plan = Counter()
    unresolved = []
    for it in todo:
        iid = str(it["item_id"])
        if (OUT / f"{iid}.png").exists():
            plan["skip_exists"] += 1
            continue
        ic = it.get("icon_path")
        if not ic:
            plan["no_icon_path"] += 1
            continue
        f = resolve_tree(ic)
        if f:
            tasks.append((iid, ic, "tree", f))
            plan["tree"] += 1
        else:
            unresolved.append((iid, ic))

    # 源包兜底
    if unresolved:
        pm = load_pack_map()
        pack_uniq = Counter()
        still = []
        for iid, ic in unresolved:
            hit = None
            for suf in ("_b", "_s", "", "_sq", "_l"):
                for ext in EXTS:
                    n = f"{ic}{suf}{ext}"
                    if n in pm:
                        hit = pm[n]
                        break
                if hit:
                    break
            if hit:
                tasks.append((iid, ic, "pack", hit))
                plan["pack"] += 1
                pack_uniq[hit[0]] += 1
            else:
                still.append((iid, ic))
        print(f"pack fallback: hit={plan['pack']} packs={len(pack_uniq)} unresolved_left={len(still)}", flush=True)
        unresolved = still

    # 站内既有 png 复用
    still2 = []
    for iid, ic in unresolved:
        base = ic.replace("/", "_")
        hit = None
        for suf in ("_b", "_s", ""):
            q = OUT / f"{base}{suf}.png"
            if q.is_file():
                hit = q.name
                break
        if hit:
            tasks.append((iid, ic, "flatpng", hit))
            plan["flatpng"] += 1
        else:
            still2.append((iid, ic))
    print(f"flat png reuse={plan['flatpng']} still_missing={len(still2)}", flush=True)
    missing = still2

    res = Counter()
    fails: dict[str, list[str]] = {}
    BATCH = 2000
    WORKERS = 12
    if limit:
        tasks = tasks[:limit]
        print(f"[dry-run] limited to {len(tasks)} tasks", flush=True)
    done = 0
    n_batches = (len(tasks) + BATCH - 1) // BATCH
    for bi in range(n_batches):
        batch = tasks[bi * BATCH: (bi + 1) * BATCH]
        if not batch:
            continue
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            futs = [ex.submit(work, t) for t in batch]
            for fu in as_completed(futs):
                status, iid, why = fu.result()
                res[status] += 1
                done += 1
                if status == "fail":
                    fails.setdefault(why.split(":")[0] + ":" + (why.split(":")[1] if ":" in why else ""), []).append(f"{iid}|{why}")
        print(f"  batch {bi + 1}/{n_batches}: {len(batch)} tasks, cum ok={res['tree'] + res['pack'] + res['flatpng']} "
              f"skip={res['skip']} fail={res['fail']}  ({time.time() - t0:.0f}s)", flush=True)

    ok = res["tree"] + res["pack"] + res["flatpng"]
    total_bytes = 0
    n_png = 0
    for p in OUT.glob("*.png"):
        n_png += 1
        total_bytes += p.stat().st_size

    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "board": str(BOARD.relative_to(PROJ)),
        "out_dir": "02_wiki/web/assets/item_icons_full",
        "target_state": TARGET_STATE,
        "board_states_before": dict(stat_before),
        "attempted": len(todo),
        "planned": dict(plan),
        "results": {"tree": res["tree"], "pack": res["pack"], "flatpng": res["flatpng"],
                    "skip_exists": res["skip"], "fail": res["fail"], "ok_total": ok},
        "fail_groups": {k: len(v) for k, v in sorted(fails.items(), key=lambda x: -len(x[1]))},
        "fail_samples": {k: v[:5] for k, v in sorted(fails.items(), key=lambda x: -len(x[1]))},
        "source_missing": {"count": len(missing),
                           "by_prefix": dict(Counter("/".join(ic.split("/")[:2]) for _, ic in missing).most_common(10)),
                           "samples": missing[:10]},
        "png_in_dir": n_png,
        "png_dir_mb": round(total_bytes / 1024 / 1024, 1),
        "elapsed_s": round(time.time() - t0, 1),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("attempted", "results", "fail_groups", "source_missing",
                                             "png_in_dir", "png_dir_mb", "elapsed_s")},
                     ensure_ascii=False, indent=1)[:3000], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
