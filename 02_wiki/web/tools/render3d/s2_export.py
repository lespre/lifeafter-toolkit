# -*- coding: utf-8 -*-
"""s2_export.py — Stage 2 GLB 导出（staging → 差异比对 → 可选落盘）

★ 复用既有 fashion_glb.py 的 build_outfit()，但**不修改该脚本**：
  动态加载后覆写它写死的 RES_ROOT / OUT_ROOT / CACHE_ROOT 与
  _resolve_tex.__defaults__（默认参数在定义时求值，只改模块常量无效）。

★ 幂等：先出到 02_wiki/state/render3d/staging/<id>/，
  再与 assets/3d/fashion_3d/<id>/ 逐文件 sha256 比对；一致即跳过，
  仅 --apply 才复制替换。目标目录里多出的文件只报告、不删除。

★ dry-run 会写 state/staging 中间区，但**绝不触碰正式产物**。
用法：
  python s2_export.py                       # dry-run，全部 roster 套
  python s2_export.py --apply               # 有差异才替换正式产物
  python s2_export.py --only 3715_f         # 只跑一套
  python s2_export.py --reuse-cache         # 复用既有 texcache（省解码时间）
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys

from r3d_core import (
    EXPORTER, FASHION_3D, PE_RES, ROSTER, SKIN_CHAIN, STATE, STAGING, TEX_CACHE,
    contract, dumps, ensure_state, read_json, sha256_file, write_json_idempotent,
)
from r3d_core import PE_CHARACTER  # noqa: F401  （保持证据路径同源）

MANIFEST = STATE / "export_manifest.json"


def _make_white_aware(mod, white_mat):
    """返回 build_part 的覆写版（不改共享 fashion_glb.py）：
    · 基础 .mtg 缺失但几何在 → 白模 GLB（空 sets + 白色 mat_opts）。
    · 带 mtg 但解析失败（如 c159_pair 头部污染）→ 退化为白模，几何不丢。
    · 带 mtg 且解析成功 → 走原 build_part，行为不变。
    逐部件容错：任一部件导出异常只记录该部件错误，不中止整套。"""
    orig = mod.build_part

    def _white(part_id, label, mesh_rel, outfit_id, out_dir, warn):
        mesh_path = os.path.join(mod.RES_ROOT, "character", mesh_rel)
        cache_dir = os.path.join(mod.CACHE_ROOT, "%s_%d" % (outfit_id, getattr(mod, "MAX_TEX", 1024)))
        os.makedirs(cache_dir, exist_ok=True)
        texmap_path = os.path.join(cache_dir, part_id + ".whitemap.json")
        json.dump({"sets": {"WHITE": {}}}, open(texmap_path, "w", encoding="utf-8"), ensure_ascii=False)
        out_glb = os.path.join(out_dir, part_id + ".glb")
        mat_opts = {"WHITE": dict(white_mat)}
        r = mod.EG.build_glb(mesh_path, texmap_path, ["WHITE"], out_glb,
                             label="%s_%s" % (outfit_id, part_id), center=False,
                             mat_opts=mat_opts)
        warnings = ["白模：缺基础 .mtg，已用默认白色 PBR 材质（metallic=0,rough=0.75）"]
        if warn:
            warnings.append(warn)
        return {
            "id": part_id, "label": label, "source_mesh": mesh_rel, "file": part_id + ".glb",
            "missing": [], "materials": [{"i": 0, "name": "WHITE", "shader": "white_model",
                                          "slots": [], "alphaMode": "OPAQUE"}],
            "warnings": warnings,
            "vertices": r["vertices"], "faces": r["faces"], "submeshes": r["submeshes"],
            "materials_exported": r["materials"], "bytes": r["size"], "white_model": True,
        }

    def _wp(part_id, label, mesh_rel, outfit_id, out_dir):
        mesh_path = os.path.join(mod.RES_ROOT, "character", mesh_rel)
        mtg_path = os.path.splitext(mesh_path)[0] + ".mtg"
        if os.path.exists(mtg_path):
            try:
                return orig(part_id, label, mesh_rel, outfit_id, out_dir)
            except Exception as exc:
                # 材质解析失败（c159_pair 头部污染等）→ 退化白模，几何不丢
                return _white(part_id, label, mesh_rel, outfit_id, out_dir,
                              "基础 .mtg 解析失败(%r)，退化白模" % exc)
        return _white(part_id, label, mesh_rel, outfit_id, out_dir, None)

    return _wp


def load_exporter(res_root, out_root, cache_root):
    """动态加载 fashion_glb.py，把写死的路径常量改成 la_paths 派生值。"""
    if not EXPORTER.exists():
        raise SystemExit("❌ 找不到导出器 %s；不臆造替代实现。" % EXPORTER)
    sys.path.insert(0, str(SKIN_CHAIN))
    sys.path.insert(0, str(SKIN_CHAIN / "纹理转换"))
    spec = importlib.util.spec_from_file_location("r3d_fashion_glb", EXPORTER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.RES_ROOT = str(res_root)
    mod.OUT_ROOT = str(out_root)
    mod.CACHE_ROOT = str(cache_root)
    # `_resolve_tex(logical_path, res_root=RES_ROOT)` 的默认值在 def 时求值
    mod._resolve_tex.__defaults__ = (str(res_root),)
    return mod


def spec_from_unit(u: dict) -> dict:
    return {
        "id": u["id"], "series": u["series"], "gender": u["gender"],
        "label": u["label"], "note": u["note"],
        "parts": [(p["part_id"], p["label"], p["source_mesh"]) for p in u["parts"]],
    }


def compare_unit(uid: str) -> dict:
    src, dst = STAGING / uid, FASHION_3D / uid
    rows = []
    for f in sorted(src.iterdir()):
        if not f.is_file():
            continue
        t = dst / f.name
        if not t.exists():
            state, cur = "new", None
        else:
            cur = sha256_file(t)
            state = "same" if cur == sha256_file(f) else "diff"
        rows.append({"file": f.name, "state": state,
                     "staging_sha256": sha256_file(f), "target_sha256": cur,
                     "staging_bytes": f.stat().st_size})
    known = {r["file"] for r in rows}
    extra = sorted(p.name for p in dst.iterdir() if p.is_file() and p.name not in known) if dst.exists() else []
    return {
        "id": uid, "files": rows, "extra_in_target": extra,
        "state": ("diff" if any(r["state"] != "same" for r in rows) else "same"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 2 · GLB 导出与幂等比对")
    ap.add_argument("--apply", action="store_true", help="有差异才替换正式产物")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--reuse-cache", action="store_true", help="复用 30_分析/_fashion3d/texcache")
    ap.add_argument("--allow-bulk", action="store_true", help="允许 index 模式批量导出（默认拒绝）")
    args = ap.parse_args()

    ensure_state()
    STAGING.mkdir(parents=True, exist_ok=True)
    roster = read_json(ROSTER)
    # ★ 护栏：扩量清单动辄上千套，一次全量导出会产出数 GB。
    #   默认拒绝，必须显式 --only 指定范围或 --allow-bulk 才放行。
    if roster.get("mode") == "index" and not args.only and not args.allow_bulk:
        print("❌ roster 为 index 扩量模式（%d 套），默认拒绝全量导出。" % len(roster["units"]))
        print("   请加 --only <id...> 指定范围，或显式 --allow-bulk（确认磁盘空间后）。")
        return 2
    cache = TEX_CACHE if args.reuse_cache else (STATE / "texcache")
    cache.mkdir(parents=True, exist_ok=True)

    units = [u for u in roster["units"] if (not args.only or u["id"] in args.only)]
    todo = [u for u in units if u["status"] == "ready"]
    skipped = [u["id"] for u in units if u["status"] != "ready"]
    if skipped:
        print("⚠ 跳过缺源套（不顶替）：%s" % ", ".join(skipped))
    if not todo:
        print("❌ 无可导出单元；先跑 s1_roster.py --apply")
        return 2

    print("== Stage 2 export  套=%d  cache=%s ==" % (len(todo), cache.name))
    mod = load_exporter(PE_RES, STAGING, cache)
    # 白模政策：基础 .mtg 缺失但几何在 → 覆写 build_part 出白模 GLB（不改共享脚本）
    wm = (contract().get("white_model") or {})
    if wm.get("enabled"):
        mod.build_part = _make_white_aware(mod, wm.get("material", {}))
        print("  [white_model] 已启用：基础 .mtg 缺失的部件按白模渲染")
    results = []
    for u in todo:
        uid = u["id"]
        print("  -- %s (%d 部件)" % (uid, len(u["parts"])))
        try:
            vj = mod.build_outfit(spec_from_unit(u))
        except Exception as exc:
            print("     ❌ 导出异常：%r" % exc)
            results.append({"id": uid, "state": "error", "error": repr(exc)})
            continue
        cmp = compare_unit(uid)
        cmp["vertices"] = sum(p.get("vertices") or 0 for p in vj["parts"])
        cmp["missing"] = sum(len(p.get("missing") or []) for p in vj["parts"])
        cmp["warnings"] = sum(len(p.get("warnings") or []) for p in vj["parts"])
        results.append(cmp)
        print("     %-5s files=%d missing=%d vertices=%d" % (
            cmp["state"], len(cmp["files"]), cmp["missing"], cmp["vertices"]))
        for r in cmp["files"]:
            if r["state"] != "same":
                print("       %-14s %s" % (r["file"], r["state"]))

    changed = 0
    if args.apply:
        for r in results:
            if r.get("state") not in ("diff", "new"):
                continue
            dst = FASHION_3D / r["id"]
            dst.mkdir(parents=True, exist_ok=True)
            for f in r["files"]:
                shutil.copy2(STAGING / r["id"] / f["file"], dst / f["file"])
                changed += 1
            print("  [WRITE] %s → %s" % (r["id"], dst))
    else:
        print("  [DRY ] 未触碰正式产物；加 --apply 才替换（共 %d 套有差异）"
              % sum(1 for r in results if r.get("state") == "diff"))

    manifest = {
        "schema_version": 1, "apply": args.apply,
        "cache_root": str(cache),
        "units": results, "files_written": changed,
        "target_root": str(FASHION_3D), "staging_root": str(STAGING),
    }
    write_json_idempotent(MANIFEST, manifest, True, "export_manifest.json")
    return 1 if any(r.get("state") == "error" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
