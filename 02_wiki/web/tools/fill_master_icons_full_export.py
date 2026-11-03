#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「全量道具总表」里 icon_state=源已定位未导出 的条目批量导出为
02_wiki/web/assets/item_icons_full/<item_id>.png。

三条取图路线（按优先级）：
  1. 站内扁平名复用：assets/item_icons_full/<icon 路径扁平化>.png（同路径同图，不重解码）
  2. 还原树 ktx/dds 解码：41_还原树/pe/资源/<icon><suffix><ext>，suffix 顺序 _b/_s/空/_sq/_l，.ktx 优先
  3. 都不可得 → 记「源缺失」（PE 本次构建包内无此路径，非未还原）

解码硬口径：RGBA8_ETC2_EAC 必须走 toolkit_core.android_gpk 的 parse_ktx/_ktx_rgba；
CompBlks 载荷走 pe_icon_bind.decoders.decode_compblks。禁止 texture2ddecoder.decode_astc（出彩色噪声）。

只读 PE 源；不改 41_还原树；不读 E:/mrzh；不碰 APK。
报告：01_索引与产物/30_分析/fill_master_icons_report.json
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
OUT = WEB / "assets/item_icons_full"
REG = PROJ / "01_索引与产物/30_分析/icon_registry.json"
BOARD = WEB / "data/boards/item_master_full.json"
REPORT = PROJ / "01_索引与产物/30_分析/fill_master_icons_report.json"

SUFFIXES = ("_b", "_s", "", "_sq", "_l")
_SUF_STRIP = tuple(sorted((s for s in SUFFIXES if s), key=len, reverse=True))
EXTS = (".ktx", ".dds")
BATCH = 2000          # 单批任务上限
WORKERS = 12          # 进程数
STATE_PENDING = "源已定位未导出"
REJECTED: list[dict] = []   # 跨族兜底里因归属冲突被拒的项（审计用）


# ---------------------------------------------------------------- 质量守卫
def magenta_ratio(arr: np.ndarray) -> float:
    """不透明像素里接近 (255,0,255) 的比例——紫底/噪声守卫。"""
    op = arr[:, :, 3] > 8
    n = int(op.sum())
    if n == 0:
        return 1.0
    px = arr[op]
    mag = (px[:, 0] > 240) & (px[:, 1] < 16) & (px[:, 2] > 240)
    return float(mag.sum()) / n


def png_ok(path: Path) -> tuple[bool, str]:
    try:
        with Image.open(path) as im:
            im.load()
            if im.width < 8 or im.height < 8:
                return False, "too_small"
            arr = np.array(im.convert("RGBA"))
    except Exception as exc:  # noqa: BLE001
        return False, f"open_fail:{exc.__class__.__name__}"
    if int((arr[:, :, 3] > 8).sum()) < 16:
        return False, "empty_alpha"
    if magenta_ratio(arr) > 0.30:
        return False, "magenta_bg"
    return True, ""


# ---------------------------------------------------------------- worker
_W = {}


def _init_worker() -> None:
    if _W:
        return
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
    from toolkit_core import android_gpk as AG
    import decoders as DEC
    _W["AG"] = AG
    _W["DEC"] = DEC


def _decode_bytes(data: bytes) -> np.ndarray:
    if data.startswith(b"CompBlks"):
        arr = _W["DEC"].decode_compblks(data)
        if arr is None:
            raise ValueError("decode_compblks returned None")
        return np.ascontiguousarray(arr)
    info = _W["AG"].parse_ktx(data)
    if not info:
        raise ValueError("parse_ktx empty")
    arr = _W["AG"]._ktx_rgba(data, info)
    if arr is None:
        raise ValueError("_ktx_rgba returned None")
    return np.ascontiguousarray(arr)


def do_ktx(task: tuple[str, str]) -> tuple[str, str, str]:
    """(item_id, src_path) -> (item_id, status, detail)"""
    _init_worker()
    iid, src = task
    tgt = OUT / f"{iid}.png"
    if tgt.exists():
        return iid, "skipped", ""
    try:
        data = Path(src).read_bytes()
    except Exception as exc:  # noqa: BLE001
        return iid, "fail_read", exc.__class__.__name__
    try:
        arr = _decode_bytes(data)
    except Exception as exc:  # noqa: BLE001
        return iid, "fail_decode", f"{exc.__class__.__name__}:{exc}"[:120]
    if arr.ndim != 3 or arr.shape[2] != 4 or arr.shape[0] < 8 or arr.shape[1] < 8:
        return iid, "fail_decode", f"bad_shape:{arr.shape}"
    if magenta_ratio(arr) > 0.30:
        return iid, "fail_magenta", f"magenta>{0.30}"
    tmp = OUT / f".{iid}.tmp.png"
    try:
        Image.fromarray(arr, "RGBA").save(tmp, "PNG", optimize=True)
        os.replace(tmp, tgt)
    except Exception as exc:  # noqa: BLE001
        tmp.unlink(missing_ok=True)
        return iid, "fail_write", exc.__class__.__name__
    return iid, "ok", ""


# ---------------------------------------------------------------- 规划
def plan() -> tuple[list, list, list]:
    reg = json.loads(REG.read_text(encoding="utf-8"))["icons"]
    items = json.loads(BOARD.read_text(encoding="utf-8"))["items"]
    flat = {p.name: p for p in OUT.glob("*.png")}
    flat_names = set(flat)

    flat_tasks: list[tuple[str, str]] = []   # (item_id, 扁平 png 路径)
    ktx_tasks: list[tuple[str, str]] = []    # (item_id, 源文件路径)
    missing: list[tuple[str, str]] = []      # (item_id, icon 路径)
    skipped = 0

    for it in items:
        if it.get("icon_state") != STATE_PENDING:
            continue
        iid = str(it.get("item_id") or "")
        rec = reg.get(iid)
        if not rec:
            missing.append((iid, ""))
            continue
        ipath = rec["path"]
        if (OUT / f"{iid}.png").exists():
            skipped += 1
            continue
        fname = ipath.replace("/", "_") + ".png"
        if fname in flat_names:
            flat_tasks.append((iid, str(flat[fname])))
            continue
        src = None
        for suf in SUFFIXES:
            for ext in EXTS:
                cand = RES / (ipath + suf + ext)
                if cand.exists():
                    src = cand
                    break
            if src:
                break
        if src:
            ktx_tasks.append((iid, str(src)))
        else:
            missing.append((iid, ipath))
    return flat_tasks, ktx_tasks, missing, skipped


def run_flat(tasks: list[tuple[str, str]], demoted: list[tuple[str, str]]) -> Counter:
    """扁平名 PNG 直接复用；校验不过的降级到 ktx 队列。"""
    st = Counter()
    for i, (iid, src) in enumerate(tasks, 1):
        tgt = OUT / f"{iid}.png"
        if tgt.exists():
            st["skipped"] += 1
            continue
        tmp = OUT / f".{iid}.tmp.png"
        try:
            shutil.copyfile(src, tmp)
            ok, why = png_ok(tmp)
            if ok:
                os.replace(tmp, tgt)
                st["ok"] += 1
            else:
                tmp.unlink(missing_ok=True)
                st[f"flat_bad_{why.split(':')[0]}"] += 1
                demoted.append((iid, ""))
        except Exception as exc:  # noqa: BLE001
            tmp.unlink(missing_ok=True)
            st[f"flat_err_{exc.__class__.__name__}"] += 1
            demoted.append((iid, ""))
        if i % 2000 == 0:
            print(f"  [flat] {i}/{len(tasks)} ok={st['ok']}", flush=True)
    return st


def cross_family_candidates(left: list[tuple[str, str]], reg: dict) -> list[tuple[str, str]]:
    """注册表路径所在的图标族目录里没有文件，但同名文件在别的族目录下（同 id 同一个资源，
    多为注册表路径前缀写错，如 ui/ui/item_icon/x）。只做「basename 完全相等」匹配，不做模糊。

    归属冲突守卫（必须有）：若该图标路径已被注册表里**别的道具**认领，说明这是别人的图，
    一律不借——例如 ui/item_icon/icon_93217 是道具 93603「塔奇克马摆件」的图，
    借给 93217「黄金等身灯台」就是错图。
    """
    claimed: dict[str, set[str]] = {}
    for iid, rec in reg.items():
        pth = rec.get("path") if isinstance(rec, dict) else None
        if pth:
            claimed.setdefault(pth, set()).add(iid)
    idx: dict[str, str] = {}
    ui_root = RES / "ui"
    if not ui_root.exists():
        return []
    for root, _dirs, files in os.walk(ui_root):
        for fn in files:
            if fn.endswith(EXTS):
                stem = fn.rsplit(".", 1)[0]
                idx.setdefault(stem, str(Path(root) / fn))
    out: list[tuple[str, str]] = []
    REJECTED.clear()
    for iid, ipath in left:
        if not ipath:
            continue
        base = ipath.split("/")[-1]
        for suf in SUFFIXES:
            hit = idx.get(base + suf)
            if not hit:
                continue
            # 还原出「逻辑图标路径」：去掉 _b/_s/_sq/_l 后缀（长后缀优先，必须显式排序，
            # 否则 "" 会先命中导致后缀没剥掉，归属检查形同虚设）
            p_rel = Path(hit).relative_to(ui_root)
            stem = p_rel.stem
            for s in _SUF_STRIP:
                if stem.endswith(s):
                    stem = stem[: -len(s)]
                    break
            rel = (p_rel.parent / stem).as_posix()
            owners = claimed.get("ui/" + rel, set()) - {iid}
            if owners:
                # 别人认领了 → 不借（宁可空着也不错图）
                REJECTED.append({"item_id": iid, "want": ipath, "found": "ui/" + rel,
                                 "owners": sorted(owners)})
                continue
            out.append((iid, hit))
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个（调试）")
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cross-family", action="store_true",
                    help="对源缺失项做 basename 跨族兜底（同 id 换目录）")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    flat_tasks, ktx_tasks, missing, skipped = plan()
    if args.limit:
        flat_tasks = flat_tasks[: args.limit]
        ktx_tasks = ktx_tasks[: args.limit]
    print(f"计划：扁平复用 {len(flat_tasks)} | ktx解码 {len(ktx_tasks)} | 源缺失 {len(missing)} "
          f"| 跳过已存在 {skipped} | 合计 {len(flat_tasks)+len(ktx_tasks)+len(missing)+skipped}", flush=True)
    if args.dry_run:
        print("dry-run，不落盘")
        return 0

    demoted: list[tuple[str, str]] = []
    st = run_flat(flat_tasks, demoted)
    print(f"扁平复用完成：{dict(st)}，降级 {len(demoted)}", flush=True)

    # 降级项：重新解析 ktx 源
    ktx_more: list[tuple[str, str]] = []
    reg = json.loads(REG.read_text(encoding="utf-8"))["icons"]
    for iid, _ in demoted:
        ipath = reg.get(iid, {}).get("path")
        if not ipath:
            continue
        for suf in SUFFIXES:
            hit = next((RES / (ipath + suf + e) for e in EXTS if (RES / (ipath + suf + e)).exists()), None)
            if hit:
                ktx_more.append((iid, str(hit)))
                break
    ktx_tasks = ktx_tasks + ktx_more

    dstat = Counter()
    if ktx_tasks:
        with ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker) as ex:
            for bi in range(0, len(ktx_tasks), BATCH):
                batch = ktx_tasks[bi: bi + BATCH]
                futs = [ex.submit(do_ktx, t) for t in batch]
                for f in as_completed(futs):
                    iid, status, detail = f.result()
                    dstat[status] += 1
                    if status.startswith("fail"):
                        dstat[f"why:{status}:{detail.split(':')[0]}"] += 1
                print(f"  [ktx] 批次 {bi//BATCH+1} 完成 {bi+len(batch)}/{len(ktx_tasks)} "
                      f"ok={dstat['ok']} fail={sum(v for k,v in dstat.items() if k.startswith('fail'))}",
                      flush=True)

    # 跨族兜底（可选）：同 basename 在别的图标族目录里
    xstat = Counter()
    xmap: list[dict] = []
    if args.cross_family:
        left = [(iid, ip) for iid, ip in missing if not (OUT / f"{iid}.png").exists()]
        canc = cross_family_candidates(left, reg)
        print(f"跨族候选 {len(canc)}", flush=True)
        if canc:
            with ProcessPoolExecutor(max_workers=args.workers, initializer=_init_worker) as ex:
                futs = [ex.submit(do_ktx, t) for t in canc]
                for f in as_completed(futs):
                    iid, status, _detail = f.result()
                    xstat[status] += 1
            xmap = [{"item_id": i, "src": s} for i, s in canc]

    # 统计
    failed_detail = Counter()
    for k, v in dstat.items():
        if k.startswith("why:"):
            failed_detail[k] += v
    fail_decode = dstat["fail_decode"] + dstat["fail_magenta"] + dstat["fail_read"] + dstat["fail_write"]
    # 源缺失里再区分：扁平图校验不过且无 ktx 源
    missing_ids = [i for i, _ in missing]
    demoted_ids = {i for i, _ in demoted}
    still_missing = len([i for i in missing_ids if i not in demoted_ids])
    demoted_unresolved = len([i for i in demoted_ids if not (OUT / f"{i}.png").exists()])

    total_size = sum(p.stat().st_size for p in OUT.glob("*.png"))
    report = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t0, 1),
        "out_dir": "02_wiki/web/assets/item_icons_full",
        "attempted": len(flat_tasks) + len(ktx_tasks) + len(xmap),
        "succeeded": st["ok"] + dstat["ok"] + xstat["ok"],
        "succeeded_flat_reuse": st["ok"],
        "succeeded_ktx_decode": dstat["ok"],
        "succeeded_cross_family": xstat["ok"],
        "skipped_exists": skipped + st["skipped"] + dstat["skipped"] + xstat["skipped"],
        "failed": fail_decode + sum(v for k, v in xstat.items() if k.startswith("fail")),
        "failed_reasons": {
            "decode_fail": dstat["fail_decode"] + xstat["fail_decode"],
            "magenta_guard": dstat["fail_magenta"] + xstat["fail_magenta"],
            "read_fail": dstat["fail_read"] + xstat["fail_read"],
            "write_fail": dstat["fail_write"] + xstat["fail_write"],
            "source_missing_no_ktx": still_missing - xstat["ok"],
            "demoted_flat_bad_unresolved": demoted_unresolved,
        },
        "cross_family_map": xmap if xmap else None,
        "cross_family_rejected": REJECTED or None,
        "cross_family_rejected_count": len(REJECTED),
        "flat_quality_rejects": {k: v for k, v in st.items() if k.startswith("flat_")},
        "dir_png_count": len(list(OUT.glob("*.png"))),
        "dir_size_mb": round(total_size / 1e6, 1),
        "workers": args.workers,
    }
    # 跨多次运行累计（补跑/续跑时 attempted 不会重复计数：已成功的下一轮记为 skipped）
    plan_total = len(flat_tasks) + len(ktx_tasks) + len(missing) + skipped
    runs: list[dict] = []
    if REPORT.exists():
        try:
            old = json.loads(REPORT.read_text(encoding="utf-8"))
            runs = old.get("runs") or [{
                "generated": old.get("generated"), "attempted": old.get("attempted", 0),
                "succeeded": old.get("succeeded", 0), "failed": old.get("failed", 0),
                "plan_total": old.get("job_totals", {}).get("plan_total", 0) or plan_total,
            }]
        except Exception:  # noqa: BLE001
            runs = []
    runs.append({"generated": report["generated"], "attempted": report["attempted"],
                 "succeeded": report["succeeded"], "failed": report["failed"],
                 "plan_total": plan_total})
    job_total = max([r.get("plan_total") or 0 for r in runs] + [plan_total])
    att = sum(r.get("attempted") or 0 for r in runs)
    succ = sum(r.get("succeeded") or 0 for r in runs)
    fail = sum(r.get("failed") or 0 for r in runs)
    report["job_totals"] = {
        "plan_total": job_total,
        "attempted": att,
        "succeeded": succ,
        "failed": fail,
        "source_missing": max(0, job_total - att - fail),
        "runs": len(runs),
    }
    report["runs"] = runs
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
