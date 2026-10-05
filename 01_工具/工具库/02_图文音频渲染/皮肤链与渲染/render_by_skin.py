# -*- coding: utf-8 -*-
"""render_by_skin.py —— 给一个皮肤 ID 就跑材质分层出图。

把原来的「手工凑 mesh + tex_dir + c159」三步自动化成单命令：

    python render_by_skin.py 1110171                 # 皮肤 ID（皮肤表内）
    python render_by_skin.py --mesh A.mesh --materials B.c159 --out DIR
    python render_by_skin.py --list                  # 表内皮肤 + 模型路径
    python render_by_skin.py 1110171 --dry-run       # 只解析定位，不出图

## 定位链（每一环都是实测出来的，不是猜的）

皮肤表 `weapon_skin_sfx_text_sources.json` 的 `model_path` 给的是
    weapon/skin/<stem>/<stem>.gim
`.gim` 是**模型描述文件**（不是网格）：实测本机 res\\weapon.gpk 的 row 1223 内容里
是 Socket/SubMesh/BoundingCenter/MtlIdx + `skin_1003_010_0/1/2` 子网格名 +
`_lod01/_lod02/_lod03.gim` 引用。真正的网格在**隔壁行**：

    实测（names lookup rows + 逐行落盘核对）：
      row 1223 = weapon\\skin\\skin_1003_010\\skin_1003_010.gim   ← 表里的 model_path 命中
      row 1224 = <stem>.mesh                                      ← 网格
      row 1225 = .c159                                            ← 材质
      row 1226 = <stem>_lod01.gim                                 ← 下一级 LOD，回到第 1 步

    row 1265/1266/1267 = skin_1003_012 的同一套结构（gim/mesh/c159）
    row 1278/1279      = 已知能出图的 001264.mesh/001265.c159
                         （旧目录 20_提取/weapon 的 6 位名 = 本目录 8 位名 - 14 的平移视图）

⇒ mesh 候选行 = gim_row + 1, +2, -1, +3；材质候选行 = mesh_row + 1, +2, +3。
   按「该行在本目录里存在的真实文件」落地，绝不凭空造路径。

## mesh 精确性判据（render 严格，glb 宽容 —— 必须用严格判据）

    meta["sizes_ok"] and meta["extra_streams_state"] == "exact"

## 诚实边界

- 贴图目录默认复用 `render_1003_010/input_tex`（光影咏叹调那一套）。
  换皮肤时不换贴图 ⇒ 颜色仍是那套贴图。这是**共用贴图**，不是人工配色。
- 任何一环失败都返回明确状态码（mesh_not_found / mesh_not_exact /
  c159_not_found / render_failed），不静默跳过、不用近似产物冒充成功。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

# ── 路径 ─────────────────────────────────────────────────────────
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
while not os.path.isdir(os.path.join(PROJ, "01_工具")):
    _up = os.path.dirname(PROJ)
    if _up == PROJ:
        raise RuntimeError("找不到项目根（向上没有含 01_工具 的目录）")
    PROJ = _up

PY = os.path.join(PROJ, ".venv", "Scripts", "python.exe")
if not os.path.exists(PY):
    PY = sys.executable
RUN_ALL = os.path.join(PROJ, "01_工具", "run_all.py")
CORE = os.path.join(PROJ, "01_工具", "工具库", "00_共享核心")

SKIN_TABLE = os.path.join(PROJ, "04_站点", "web", "data", "boards",
                          "weapon_skin_sfx_text_sources.json")
#: 已解包产物目录（row → 8 位数字文件名）。行号与 res\weapon.gpk 一致（实测核对过）。
EXTRACT_DIR = os.path.join(PROJ, "03_执行", "20_提取", "全量实测_20260926",
                           "files", "weapon")
#: 默认贴图目录（通用：跑别的皮肤也能出图，只是颜色是这一套）
DEFAULT_TEX_DIR = os.path.join(PROJ, "03_执行", "30_分析", "render_1003_010", "input_tex")
OUT_ROOT = os.path.join(PROJ, "03_执行", "90_临时", "render_by_skin")

#: mesh 相对 gim 行的候选偏移（先试实测命中的 +1）
MESH_OFFSETS = (1, 2, -1, 3, 4, -2)
#: 材质相对 mesh 行的候选偏移
MTL_OFFSETS = (1, 2, 3, 4, -1)
#: 一个皮肤最终产出的分层 PNG 期望数量（render_material_layers 的 8 层）
EXPECTED_PNGS = 8

sys.path.insert(0, CORE)


# ── 皮肤表 ────────────────────────────────────────────────────────
def load_skin_table() -> dict:
    d = json.load(open(SKIN_TABLE, encoding="utf-8"))
    out = {}
    for it in d["items"]:
        sid = it.get("skin_id")
        mp = (it.get("model_path") or "").strip()
        rec = {
            "skin_id": sid,
            "name": it.get("name_display") or it.get("name"),
            "catalog_layer": it.get("catalog_layer"),
            "model_path": mp,
        }
        if mp:
            m = re.search(r"weapon[/\\]skin[/\\]([^/\\]+)[/\\][^/\\]+$", mp)
            rec["stem"] = m.group(1) if m else None
        out[sid] = rec
        # 时限变体也挂上（id 形如 11100041）
        for v in it.get("variant_items") or []:
            vid = v.get("skin_id")
            if vid is not None:
                rec2 = dict(rec)
                rec2.update(skin_id=vid, name=v.get("name_display") or v.get("name"),
                            catalog_layer="time_limit_variant", main_skin_id=sid)
                out[vid] = rec2
    return out


# ── 名字还原：路径 → 容器 + 行 ─────────────────────────────────────
def names_lookup(path: str) -> dict:
    """调①-4 官方入口（不自己重写 murmur3）。返回 {found, row, container, fid, raw}。"""
    r = subprocess.run([PY, RUN_ALL, "names", "lookup", path],
                       cwd=PROJ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    out = (r.stdout or "") + (r.stderr or "")
    rec = {"found": False, "row": None, "container": None, "fid": None, "raw": out.strip()}
    mf = re.search(r"fid\s+([0-9A-F]{16})", out)
    if mf:
        rec["fid"] = mf.group(1)
    m = re.search(r"→\s*(\S+)\s+row\s+(\d+)", out)
    if m:
        rec["found"] = True
        rec["container"] = m.group(1)
        rec["row"] = int(m.group(2))
    return rec


def file_at_row(row: int, ext: str) -> str | None:
    """本目录里该行的真实文件（8 位补零命名）。不存在就 None。"""
    p = os.path.join(EXTRACT_DIR, "%08d.%s" % (row, ext))
    return p if os.path.exists(p) else None


def any_file_at_row(row: int) -> str | None:
    pref = "%08d." % row
    try:
        for n in os.listdir(EXTRACT_DIR):
            if n.startswith(pref):
                return os.path.join(EXTRACT_DIR, n)
    except OSError:
        pass
    return None


# ── mesh 精确性 ───────────────────────────────────────────────────
def mesh_integrity(mesh_path: str) -> dict:
    """★ 严格判据：sizes_ok 且 extra_streams_state == 'exact'。glb 能出图不代表 render 能。"""
    rec = {"checked": False, "ok": False, "sizes_ok": None,
           "extra_streams_state": None, "trailing_bytes": None, "error": None}
    try:
        from toolkit_core import la_glb
        P, uv, idx, meta = la_glb.parse_part(mesh_path)
        rec.update(checked=True,
                   sizes_ok=bool(meta.get("sizes_ok")),
                   extra_streams_state=meta.get("extra_streams_state"),
                   trailing_bytes=meta.get("trailing_bytes"),
                   vertices=int(meta.get("tv", 0)), faces=int(meta.get("tf", 0)))
        rec["ok"] = bool(meta.get("sizes_ok")) and meta.get("extra_streams_state") == "exact"
    except Exception as e:  # noqa: BLE001
        rec["error"] = "%s: %s" % (type(e).__name__, e)
    return rec


# ── c159 材质校验（两套解析器，用前 try/except） ──────────────────────
def c159_parse(path: str) -> dict:
    rec = {"old": None, "v4": None, "note": None}
    sys.path.insert(0, os.path.join(PROJ, "01_工具", "工具库", "02_图文音频渲染", "皮肤链与渲染"))
    try:
        import c159_pair
        mats = c159_pair.load_asset_materials(path)
        rec["old"] = {"ok": True, "materials": len(mats) if hasattr(mats, "__len__") else None}
    except Exception as e:  # noqa: BLE001
        rec["old"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    try:
        import c159_pair_v4
        a = c159_pair_v4.analyze_v4(path)
        conf = None
        if isinstance(a, dict):
            conf = a.get("confidence")
        rec["v4"] = {"ok": True, "confidence": conf}
    except Exception as e:  # noqa: BLE001
        rec["v4"] = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
    rec["note"] = "两套解析器结果都失败时仍可试渲染（render 自带解析），这里只做记录"
    return rec


# ── 定位 ─────────────────────────────────────────────────────────
def resolve(skin_id: int | None, mesh_arg: str | None, mtl_arg: str | None,
            table: dict, trace: dict) -> dict:
    """返回 {status, mesh, materials, how}。status != 'ok' 时后续不渲染。"""
    res = {"status": None, "mesh": None, "materials": None, "gim_row": None,
           "mesh_row": None, "mtl_row": None, "how": {}}

    if mesh_arg:
        res["mesh"] = os.path.abspath(mesh_arg)
        res["materials"] = os.path.abspath(mtl_arg) if mtl_arg else None
        res["how"] = {"mode": "manual", "mesh": "命令行 --mesh", "materials": "命令行 --materials"}
        return res

    rec = table.get(skin_id)
    if rec is None:
        res["status"] = "skin_not_in_table"
        res["how"] = {"reason": "皮肤表 118 条 main + 时限变体里没有 skin_id=%s" % skin_id}
        return res
    mp = rec.get("model_path")
    if not mp:
        res["status"] = "skin_no_model_path"
        res["how"] = {"reason": "该皮肤行没有 model_path"}
        return res
    stem = rec.get("stem") or ""

    # ① 表里的 model_path（.gim）→ 行
    lk = names_lookup(mp)
    trace["gim_lookup"] = lk
    res["how"]["model_path"] = mp
    if not lk["found"]:
        # 退路：同 skin 表里其它同类路径也不试了，直接如实报
        res["status"] = "mesh_not_found"
        res["how"]["reason"] = "names lookup 未命中 model_path：%s" % mp
        return res
    gim_row = lk["row"]
    res["gim_row"] = gim_row
    res["how"]["gim_row"] = {"row": gim_row, "container": lk["container"], "fid": lk["fid"]}

    # ② 网格 = 隔壁行里真实存在的 .mesh
    tried = []
    mesh_path = None
    for off in MESH_OFFSETS:
        row = gim_row + off
        p = file_at_row(row, "mesh")
        tried.append({"row": row, "offset": off, "found": bool(p),
                      "other": os.path.basename(any_file_at_row(row) or "") or None})
        if p:
            mesh_path = p
            res["mesh_row"] = row
            res["how"]["mesh_row"] = {"row": row, "offset_from_gim": off,
                                      "file": os.path.basename(p)}
            break
    res["how"]["mesh_tried"] = tried
    if not mesh_path:
        res["status"] = "mesh_not_found"
        res["how"]["reason"] = ("gim row %d 的邻行（%s）在本目录 %s 里都没有 .mesh 文件"
                                % (gim_row, list(MESH_OFFSETS), EXTRACT_DIR))
        return res
    res["mesh"] = mesh_path

    # ③ 材质 = 网格后面的真实 .c159
    mt = []
    mtl_path = None
    for off in MTL_OFFSETS:
        row = res["mesh_row"] + off
        p = file_at_row(row, "c159")
        mt.append({"row": row, "offset": off, "found": bool(p),
                   "other": os.path.basename(any_file_at_row(row) or "") or None})
        if p:
            mtl_path = p
            res["mtl_row"] = row
            res["how"]["mtl_row"] = {"row": row, "offset_from_mesh": off,
                                     "file": os.path.basename(p)}
            break
    res["how"]["mtl_tried"] = mt
    res["materials"] = mtl_path
    if not mtl_path:
        res["status"] = "c159_not_found"
        res["how"]["reason"] = ("mesh row %d 的邻行（%s）在本目录里都没有 .c159"
                                % (res["mesh_row"], list(MTL_OFFSETS)))
        return res

    res["how"]["mesh_pick_rule"] = ("实测：gim row 1223 → mesh row 1224（skin_1003_010）；"
                                    "gim row 1265 → mesh row 1266（skin_1003_012）")
    return res


# ── 出图 ─────────────────────────────────────────────────────────
def run_render(mesh: str, tex_dir: str, materials: str | None, out_dir: str,
               timeout_s: int = 280) -> dict:
    cmd = [PY, RUN_ALL, "render", mesh, tex_dir, "--out", out_dir]
    if materials:
        cmd += ["--materials", materials]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=PROJ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout_s)
        rc, out, err = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc, out, err = -99, (e.stdout or "") if isinstance(e.stdout, str) else "", "TIMEOUT %ss" % timeout_s
    return {"cmd": cmd, "returncode": rc, "seconds": round(time.time() - t0, 1),
            "stdout_tail": out[-2500:], "stderr_tail": err[-1500:]}


def collect_outputs(out_dir: str) -> dict:
    pngs, others = [], []
    if os.path.isdir(out_dir):
        for n in sorted(os.listdir(out_dir)):
            p = os.path.join(out_dir, n)
            if not os.path.isfile(p):
                continue
            item = {"name": n, "bytes": os.path.getsize(p)}
            (pngs if n.lower().endswith(".png") else others).append(item)
    return {"pngs": pngs, "others": others, "png_count": len(pngs)}


# ── 主流程 ───────────────────────────────────────────────────────
def do_one(skin_id, args, table) -> dict:
    t0 = time.time()
    trace = {}
    item = {"skin_id": skin_id, "status": None, "how": {}, "outputs": {},
            "seconds": None, "error": None}
    if skin_id is not None:
        rec = table.get(skin_id) or {}
        item["name"] = rec.get("name")
        item["model_path"] = rec.get("model_path")
        item["catalog_layer"] = rec.get("catalog_layer")
    tag = str(skin_id) if skin_id is not None else "manual"
    out_dir = args.out or os.path.join(args.out_dir_root, tag)

    res = resolve(skin_id, args.mesh, args.materials, table, trace)
    item["how"] = res["how"]
    item["trace"] = trace
    item["mesh"] = res["mesh"]
    item["materials"] = res["materials"]
    item["gim_row"], item["mesh_row"], item["mtl_row"] = \
        res["gim_row"], res["mesh_row"], res["mtl_row"]

    if res["status"]:
        item["status"] = res["status"]
        item["seconds"] = round(time.time() - t0, 1)
        return item

    # mesh 严格自检
    integ = mesh_integrity(res["mesh"])
    item["mesh_integrity"] = integ
    if not integ["ok"]:
        item["status"] = "mesh_not_exact"
        item["how"]["reason"] = ("sizes_ok=%r extra_streams_state=%r trailing_bytes=%r "
                                 "—— render 严格判据不通过（glb 宽容，能出图也不算）"
                                 % (integ["sizes_ok"], integ["extra_streams_state"],
                                    integ["trailing_bytes"]))
        item["seconds"] = round(time.time() - t0, 1)
        return item

    if res["materials"]:
        item["c159_check"] = c159_parse(res["materials"])
    item["tex_dir"] = args.tex_dir or DEFAULT_TEX_DIR
    item["tex_dir_note"] = ("复用光影咏叹调那套贴图（非本皮肤自有）—— 只影响颜色，不影响出图"
                            if not args.tex_dir else "调用方指定")

    if args.dry_run:
        item["status"] = "dry_run_ok"
        item["out"] = out_dir
        item["seconds"] = round(time.time() - t0, 1)
        return item

    os.makedirs(out_dir, exist_ok=True)
    rr = run_render(res["mesh"], item["tex_dir"], res["materials"], out_dir,
                    timeout_s=args.timeout)
    item["render"] = {"cmd": " ".join('"%s"' % c if " " in c else c for c in rr["cmd"]),
                      "returncode": rr["returncode"], "seconds": rr["seconds"],
                      "stdout_tail": rr["stdout_tail"], "stderr_tail": rr["stderr_tail"]}
    item["out"] = out_dir
    outs = collect_outputs(out_dir)
    item["outputs"] = outs
    has_trace = any(o["name"] == "layers_trace.json" for o in outs["others"])
    if rr["returncode"] == 0 and outs["png_count"] >= EXPECTED_PNGS and has_trace:
        item["status"] = "ok"
    else:
        item["status"] = "render_failed"
        item["how"]["reason"] = ("returncode=%s, png=%d(期望>=%d), layers_trace.json=%s"
                                 % (rr["returncode"], outs["png_count"], EXPECTED_PNGS, has_trace))
    item["seconds"] = round(time.time() - t0, 1)
    return item


def main(argv=None) -> int:
    ap = argparse.ArgumentParser("render_by_skin", description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skin_id", nargs="?", help="皮肤 ID（皮肤表内，如 1110171）")
    ap.add_argument("--mesh", help="直接指定 .mesh（跳过定位）")
    ap.add_argument("--materials", help="直接指定 .c159 材质")
    ap.add_argument("--out", help="输出目录")
    ap.add_argument("--out-dir-root", default=OUT_ROOT, help="输出根（默认 %s）" % OUT_ROOT)
    ap.add_argument("--tex-dir", help="贴图目录（默认 %s）" % DEFAULT_TEX_DIR)
    ap.add_argument("--dry-run", action="store_true", help="只解析定位，不出图")
    ap.add_argument("--timeout", type=int, default=280, help="单次 render 超时秒（默认 280）")
    ap.add_argument("--list", action="store_true", help="列出皮肤表可用的 skin_id")
    ap.add_argument("--json", dest="json_out", help="把本次结果 JSON 落盘")
    args = ap.parse_args(argv)

    table = load_skin_table()
    if args.list:
        for sid, rec in sorted(table.items()):
            if rec.get("model_path"):
                print("%-10s %-14s %s" % (sid, rec.get("name"), rec["model_path"]))
        print("共 %d 条（含时限变体）" % len(table))
        return 0

    if args.skin_id is None and not args.mesh:
        ap.error("要么给 skin_id，要么给 --mesh")
    sid = int(args.skin_id) if args.skin_id is not None else None

    item = do_one(sid, args, table)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    if args.json_out:
        json.dump(item, open(args.json_out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    return 0 if item["status"] in ("ok", "dry_run_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
