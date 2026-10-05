# -*- coding: utf-8 -*-
"""la_glb.py — toolkit `glb` 子命令核心：一个或多个 .mesh 部件 → 单个 GLB（世界坐标拼接）

用户 2026-09-26 指定约束：
 · **只新增**：不修改 mesh_parse2.py / export_glb.py / paths.py 等现有脚本；
 · 解析复用 `mesh_parse2.parse_mesh2`（**import 成功，无需在本文件重实现**——该模块只依赖
   stdlib + numpy，且带文件级导入路径回退，见 `_chain_module`）；
 · 写出复用 `export_glb.build_glb`：**每个部件调用一次**，再把 N 个部件 GLB 合并成一个
   （`_merge_glbs`）。不"自己拼顶点另写一个导出器"的原因：build_glb 内部持有交付标准的
   坐标/源法线(不重算)/UV/provenance 逻辑，且只有"单 mesh 文件 + texmap"入口；重实现会与
   该文件分叉（该文件禁止修改）。合并时不做整体中心化/缩放：**部件顶点已是世界坐标**，
   直接合成就自动归位（用户明确"不归零"）。

自检（写进 --json 报告）：
 · 每部件 顶点数 / 三角数 / 比值 tri_per_vert = tf/tv（**信息输出，不再单独触发告警**）、bbox、子网格数；
 · 解析器原生完整性：sizes_ok / extra_streams_state / trailing_bytes（mesh_parse2 的权威判据）；
   ★★ 修复（2026-09-26，A11）：**解析是否完整以 `sizes_ok and extra_streams_state == 'exact'` 为准**
   （`integrity_ok` / `alarm`）。旧的 `tf/tv < 1.5` 口径对本仓**无区分度**（实测 184/188 = 97.87% 触发），
   已降级为信息字段 `ratio_alarm`（`reason` 标 `info_only`），只统计、不计入 `alarm`、不进退出码。
 · 附加诊断（非用户硬性要求，便于定位）：唯一顶点数、重复顶点率、索引越界、退化三角；
 · 合并后：总顶点数/总三角数、并集 bbox 与 GLB 内 POSITION accessor min/max 的一致性、
   primitive 索引总量 = 3×总三角数、GLB 结构自检（buffer/bufferView/accessor 边界）。

退出码：0 成功 | 2 输出已存在且无 --force | 3 无任何部件导出成功 | 4 部分失败（有失败清单）
        | 5 运行环境缺依赖（numpy/PIL 等）
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
import re
import struct
import sys
import tempfile
import time
from pathlib import Path

from toolkit_core.paths import PROJECT_ROOT

# ---- 常量 ----
CHAIN_DIR = PROJECT_ROOT / "01_工具" / "工具库"  / "02_图文音频渲染" / "皮肤链与渲染"   # 06_皮肤定位链（被包装脚本所在）
DEFAULT_GLB_DIR = PROJECT_ROOT / "03_执行" / "90_临时" / "glb_out"  # 默认输出（禁硬编码项目根）
RATIO_ALARM = 1.5                  # 【已降级·信息专用】旧口径：tf/tv < 1.5。对本仓无区分度，见下。
INTEGRITY_JUDGE = "sizes_ok and extra_streams_state == 'exact'"   # ★ 权威判据（mesh_parse2 docstring 同源）
# ★★ 标定记录（2026-09-26，A11；样本 = 03_执行/20_提取/weapon/*.mesh 前 200 个，解析成功 188）：
#   tf/tv 分布  min=0.5000  p05=0.6067  p25=0.7101  median=0.8214  p75=0.9952  p95=1.1699  max=1.6656
#   旧判据 tf/tv<1.5        → 184/188 = 97.87% 触发 ⇒ 失去预警意义（"几乎全数报警"= 等于不报警）
#   新判据 integrity_ok     →  57/188 = 30.32% 触发，且失败态**全部**是 extra_streams_state='trailing_unaccounted'
#   若坚持保留比值告警，按本仓分布应取 p05≈0.60（触发率约 5%）；默认**不启用**该阈值。
RATIO_RECALIBRATED_HINT = 0.60     # 仅标定依据，默认不参与任何判定
RATIO_STATS_20260926 = {"sample_n": 200, "parsed_ok": 188,
                        "min": 0.5000, "p05": 0.6067, "p25": 0.7101, "median": 0.8214,
                        "p75": 0.9952, "p95": 1.1699, "max": 1.6656,
                        "old_alarm_count": 184, "new_alarm_count": 57}
FAILURE_LOG_NAME = "glb_failures.jsonl"
TOOLKIT_VERSION = "la_glb v1.0 (2026-09-26)"

# 贴图槽位后缀（实证：c159 内声明 weapon\\..\\*_c_d.tga/_c_n/_c_m，wiki texmap 用 a/n/m/b_m/s_m）
# 顺序 = 最长后缀优先匹配；slot 'a'=baseColor 'n'=normal 'm'=metalRough(ParamMap)，
# 's_m'/'b_m' 为源侧额外掩码，export_glb 无对应槽位 ⇒ 只在报告里登记，不写进材质。
SLOT_SUFFIXES = ("c_s_m", "b_m", "s_m", "c_m", "c_n", "c_d", "a", "n", "m", "d")
SLOT_MAP = {"c_s_m": "s_m", "b_m": "b_m", "s_m": "s_m", "c_m": "m", "c_n": "n",
            "c_d": "a", "a": "a", "n": "n", "m": "m", "d": "a"}
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".tga", ".dds", ".bmp")


# ============================================================================
# 0. 环境探针 / 失败清单
# ============================================================================
def _chain_module(name: str):
    """按文件所在目录导入 06_皮肤定位链 的脚本（不复制其代码）。"""
    if str(CHAIN_DIR) not in sys.path:
        sys.path.insert(0, str(CHAIN_DIR))
    return importlib.import_module(name)


def _env_probe() -> dict:
    info = dict(python=sys.version.split()[0], executable=sys.executable,
                numpy=None, pillow=None, chain_dir=str(CHAIN_DIR), chain_dir_exists=CHAIN_DIR.is_dir())
    try:
        info["numpy"] = importlib.import_module("numpy").__version__
    except Exception as exc:                                    # noqa: BLE001
        info["numpy_error"] = repr(exc)
    try:
        from PIL import __version__ as pilver                         # noqa: PLC0415
        info["pillow"] = pilver
    except Exception as exc:                                    # noqa: BLE001
        info["pillow_error"] = repr(exc)
    for script in ("mesh_parse2.py", "export_glb.py", "c159_pair.py", "export_tex_png.py"):
        p = CHAIN_DIR / script
        info[f"sha16_{script}"] = _sha16(p) if p.is_file() else None
    return info


def _sha16(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def _append_failure(log_path: Path, record: dict) -> None:
    """失败清单 JSONL —— 逐个失败追写，绝不静默跳过。"""
    record = dict(record)
    record.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ============================================================================
# 1. 解析（复用 mesh_parse2）
# ============================================================================
def parse_part(mesh_path: Path, load_vcol: bool = True):
    """→ (P, uv, idx, meta)，直接转调 mesh_parse2.parse_mesh2（本文件不重实现解析）。"""
    MP = _chain_module("mesh_parse2")
    P, uv, idx, meta = MP.parse_mesh2(str(mesh_path), load_vcol=load_vcol)
    return P, uv, idx, meta


def part_selfcheck(mesh_path: Path, P, idx, meta: dict) -> dict:
    """单部件自检（用户要求的 顶点/三角/比值/bbox + 解析器原生完整性 + 附加诊断）。"""
    import numpy as np

    tv, tf = int(meta["tv"]), int(meta["tf"])
    bmin, bmax = meta["bbox"]
    bmin = np.asarray(bmin, np.float64); bmax = np.asarray(bmax, np.float64)
    uniq = int(np.unique(np.asarray(P, np.float32), axis=0).shape[0]) if tv else 0
    max_idx = int(np.max(idx)) if getattr(idx, "size", 0) else -1
    degen = int((((idx[:, 0] == idx[:, 1]) | (idx[:, 1] == idx[:, 2]) | (idx[:, 0] == idx[:, 2]))
                 ).sum()) if getattr(idx, "size", 0) else 0
    # ★★ 修复（2026-09-26，A11）：权威判据 = 解析器原生完整性（sizes_ok 且 extra_streams_state=='exact'）。
    integrity_ok = bool(meta["sizes_ok"] and meta["extra_streams_state"] == "exact")
    alarm_reason = None if integrity_ok else (
        ("sizes_ok=False" if not meta["sizes_ok"] else "")
        + (";" if not meta["sizes_ok"] and meta["extra_streams_state"] != "exact" else "")
        + ("extra_streams_state=%s(trailing_bytes=%d,n_extra=%d)"
           % (meta["extra_streams_state"], int(meta["trailing_bytes"]), int(meta["n_extra"]))
           if meta["extra_streams_state"] != "exact" else ""))
    return dict(
        path=str(mesh_path), name=mesh_path.name, size_bytes=mesh_path.stat().st_size,
        sha256_16=_sha16(mesh_path),
        vertices=tv, faces=tf,
        tri_per_vert=round(tf / tv, 4) if tv else 0.0,
        # --- 权威完整性判定（参与告警/汇总，不进退出码） ---
        integrity_ok=integrity_ok, alarm=not integrity_ok, alarm_reason=alarm_reason,
        # --- tf/tv 比值：**信息输出**（ratio_reason 标 info_only，不计入 alarm） ---
        ratio_alarm=bool(tv and (tf / tv) < RATIO_ALARM),
        ratio_alarm_reason="info_only:legacy_tf_tv_lt_%s" % RATIO_ALARM,
        submeshes=len(meta["subs"]), sub_sizes=[int(s[0]) for s in meta["subs"]],
        sub_flags=[hex(u) for _, _, u in meta["subs"]],
        bbox_file_min=[round(float(x), 4) for x in bmin], bbox_file_max=[round(float(x), 4) for x in bmax],
        bbox_file_inverted=bool(any(bmin[i] > bmax[i] for i in range(3))),
        bbox_file_span=[round(float(abs(bmax[i] - bmin[i])), 4) for i in range(3)],
        bbox_world_min=[round(float(x), 4) for x in np.asarray(P, np.float32).min(0)] if tv else None,
        bbox_world_max=[round(float(x), 4) for x in np.asarray(P, np.float32).max(0)] if tv else None,
        # 解析器原生完整性（mesh_parse2 docstring: 判据用 sizes_ok=True 且 extra_streams_state=='exact'）
        sizes_ok=bool(meta["sizes_ok"]), extra_streams_state=meta["extra_streams_state"],
        n_extra=int(meta["n_extra"]), trailing_bytes=int(meta["trailing_bytes"]),
        vcol_read=(meta.get("vcol_read") or {}).get("state"),
        # 附加诊断（本工具补充，非用户硬性要求）
        unique_positions=uniq, dup_vertex_ratio=round(1 - uniq / tv, 4) if tv else None,
        max_index=max_idx, index_in_range=bool(max_idx < tv if tv else False),
        degenerate_tris=degen,
    )


# ============================================================================
# 2. 贴图目录（--tex）与材质文件（--mat）
# ============================================================================
def classify_slot(filename: str):
    """按文件名槽位后缀分组 → (前缀, 槽位, 命中后缀)。

    两种实证命名都支持：带下划线（c159 声明：`baishe_332_c_d.tga`、wiki：`<id>_<id>_a.png`）
    与紧随数字的无下划线形式（material_manifest：`skin_1001_014001a.tga`）。
    无下划线形式要求后缀前一字符是数字，避免把 `main.png` 之类误判成槽位 n。
    """
    stem = Path(filename).stem.lower()
    for suf in SLOT_SUFFIXES:
        if stem.endswith("_" + suf) and len(stem) > len(suf) + 1:
            return stem[:-(len(suf) + 1)], SLOT_MAP[suf], "_" + suf
        if stem.endswith(suf) and len(stem) > len(suf) and stem[-len(suf) - 1].isdigit():
            return stem[:-len(suf)], SLOT_MAP[suf], suf
    return None, None, None


def group_textures(tex_dir: Path) -> dict:
    """扫目录，按"首段 token"分组（实证命名：<matid>_<texid>_<slot>.png / *_c_d.tga）。

    → {group_key: {slot: path, ...}}，同槽位冲突保留文件名最短者（并登记 conflict）。
    """
    groups, conflicts = {}, {}
    for f in sorted(Path(tex_dir).iterdir()):
        if not f.is_file() or f.suffix.lower() not in IMAGE_EXTS:
            continue
        prefix, slot, _suf = classify_slot(f.name)
        if slot is None:
            continue
        key = prefix.split("_")[0]
        bucket = groups.setdefault(key, {})
        if slot in bucket:
            conflicts.setdefault(key, []).append(
                dict(slot=slot, kept=bucket[slot].name, dropped=f.name))
            if len(f.name) >= len(bucket[slot].name):
                continue
        bucket[slot] = f
    return dict(groups=groups, conflicts=conflicts)


def _as_png(path: Path, tmpdir: Path) -> Path:
    """DDS 必须走唯一解码入口 dds_rgba_canonical（export_tex_png 是其 CLI 封装）；
    其它格式（png/jpg/tga）由 export_glb 内部 PIL 直接读，保持与既有交付一致。

    dds_rgba_canonical 依赖第三方 `texture2ddecoder`；本机 2 个可用解释器均未安装
    （见报告 env）。此时**不绕过唯一入口**（不许用 PIL 直接解 DDS）：该槽位记失败、
    其余槽位照常导出。
    """
    if path.suffix.lower() != ".dds":
        return path
    try:
        ET = _chain_module("export_tex_png")
    except ImportError as exc:
        raise RuntimeError("DDS 解码链不可用（dds_rgba_canonical/export_tex_png）：%s；"
                           "请 pip install texture2ddecoder，或改用已解码 PNG 目录" % exc) from exc
    out = tmpdir / (path.stem + "_canon.png")
    ET.export_one(str(path), str(out), None, verify_oiio=False)
    return out


def resolve_textures(tex_dir: Path | None, mat_path: Path | None, tmpdir: Path) -> dict:
    """决定 export_glb 用的贴图集 {'a','n','m'}（可缺）。

    优先级 1：--mat 的 .c159 内**声明的贴图路径**，其 basename 在 --tex 内命中 ⇒ 最高置信度；
    优先级 2：--tex 目录内文件名槽位约定分组（选覆盖 a/n/m 最多的一组）；
    两者都不成立 ⇒ 几何-only 导出（在报告里说明，不是失败）。
    单槽位转换失败（如 DDS 解码链缺依赖）记入 failures，不中断其余槽位。
    """
    res = dict(tex_dir=str(tex_dir) if tex_dir else None, mat_file=str(mat_path) if mat_path else None,
               declared=[], declared_matched={}, groups={}, group_selected=None,
               group_candidates={}, conflicts={}, slots={}, unmapped_slots={}, failures=[],
               slot_matched_suffix={}, warnings=[])
    if tex_dir is None:
        return res
    tex_dir = Path(tex_dir)
    if not tex_dir.is_dir():
        res["warnings"].append("--tex 目录不存在：%s" % tex_dir)
        return res

    by_name = {}
    for f in tex_dir.iterdir():
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS:
            by_name.setdefault(f.stem.lower(), f)
            by_name.setdefault(f.name.lower(), f)

    # 优先级 1：c159 声明
    if mat_path is not None:
        try:
            CP = _chain_module("c159_pair")
            declared = [s for s in CP.read_names(mat_path.read_bytes())["full"]
                        if any(ext in s.lower() for ext in (".tga", ".dds", ".png"))]
            # c159_pair.read_names 的参数表在遇到含 `\` 或 `::` 的串时即 break，
            # 贴图路径**不在** full 里 ⇒ 再对全文可打印串扫一遍补全（实测 000007.c159
            # 四个 `weapon\26_chunjie\textures\baishe_332_c_{d,n,m,s_m}.tga` 只能这样拿到）。
            raw = mat_path.read_bytes()
            declared += [m.group().decode("latin1") for m in re.finditer(rb"[\x20-\x7e]{4,}", raw)
                         if any(ext in m.group().lower() for ext in (b".tga", b".dds", b".png"))]
            declared = list(dict.fromkeys(declared))
            res["declared"] = declared
            for d in declared:
                stem = Path(d.replace("\\", "/")).stem
                _, slot, _suf = classify_slot(stem)
                hit = by_name.get(stem.lower())
                if hit is None or slot is None:
                    continue
                if slot in ("a", "n", "m") and slot not in res["slots"]:
                    res["slots"][slot] = hit
                    res["declared_matched"][slot] = dict(declared=d, file=str(hit))
                elif slot not in ("a", "n", "m"):
                    res["unmapped_slots"].setdefault(slot, []).append(str(hit))
        except Exception as exc:                                     # noqa: BLE001
            res["warnings"].append("c159 声明贴图解析失败：%r" % (exc,))

    # 优先级 2：目录分组补缺
    g = group_textures(tex_dir)
    res["groups"] = {k: {s: str(p) for s, p in v.items()} for k, v in g["groups"].items()}
    res["conflicts"] = g["conflicts"]
    if res["groups"]:
        def score(item):
            slots = item[1]
            return (sum(1 for s in ("a", "n", "m") if s in slots), len(slots))
        cands = sorted(res["groups"].items(), key=lambda it: (-score(it)[0], -score(it)[1], it[0]))
        res["group_candidates"] = {k: sorted(v) for k, v in res["groups"].items()}
        key, slots = cands[0]
        res["group_selected"] = key
        for slot in ("a", "n", "m"):
            if slot not in res["slots"] and slot in slots:
                res["slots"][slot] = Path(slots[slot])
        for slot, p in slots.items():
            if slot not in ("a", "n", "m"):
                res["unmapped_slots"].setdefault(slot, []).append(p)
    if not res["slots"]:
        res["warnings"].append("--tex 内未找到可用的 a/n/m 组 ⇒ 几何-only 导出")
    elif "a" not in res["slots"]:
        res["warnings"].append("贴图组缺 baseColor(a) ⇒ 材质无 baseColorTexture")

    # 槽位源文件 → 导出用文件（DDS 走规范解码；单槽位失败不拖垮整次导出）
    converted = {}
    for s, p in sorted(res["slots"].items()):
        try:
            converted[s] = str(_as_png(Path(p), tmpdir))
        except Exception as exc:                                    # noqa: BLE001
            res["failures"].append(dict(kind="texture", slot=s, file=str(p),
                                        error="%s: %s" % (type(exc).__name__, exc)))
            res["warnings"].append("槽位 %s 贴图不可用（%s）⇒ 材质缺该槽" % (s, Path(p).name))
    res["slot_matched_suffix"] = {s: classify_slot(Path(p).name)[2] for s, p in res["slots"].items()}
    res["unmapped_slots"] = {k: list(dict.fromkeys(v)) for k, v in res["unmapped_slots"].items()}
    res["slots_source"] = {s: str(p) for s, p in res["slots"].items()}
    res["slots"] = converted
    return res


def analyze_material(mat_path: Path | None) -> dict:
    """复用 c159_pair.analyze 解析材质文件（材料名/shader/参数配对），失败登记为失败项。"""
    if mat_path is None:
        return dict(file=None, ok=None, note="未提供 --mat")
    if not Path(mat_path).is_file():
        return dict(file=str(mat_path), ok=False, error="文件不存在")
    try:
        CP = _chain_module("c159_pair")
        A = CP.analyze(str(mat_path))
        return dict(file=str(mat_path), ok=True, sha256_16=_sha16(Path(mat_path)),
                    materials=A["materials"], shaders=A["shaders"],
                    components=A["names"]["comp"], params=A["names"]["params"],
                    groups=len(A["groups"]), blocks=len(A["blocks"]), pairs=len(A["pairs"]))
    except Exception as exc:                                        # noqa: BLE001
        return dict(file=str(mat_path), ok=False, error=repr(exc))


# ============================================================================
# 3. GLB：单部件导出（export_glb）+ 多部件合并
# ============================================================================
def export_part_glb(mesh_path: Path, texmap_path: Path, set_name: str, out_glb: Path, label: str) -> dict:
    """转调 export_glb.build_glb（center=False：保留世界坐标，用户要求不归零）。"""
    EG = _chain_module("export_glb")
    return EG.build_glb(str(mesh_path), str(texmap_path), [set_name], str(out_glb),
                        label, center=False)


def _read_glb(path: Path):
    b = Path(path).read_bytes()
    magic, ver, total = struct.unpack_from("<III", b, 0)
    if magic != 0x46546C67:
        raise ValueError("GLB magic 不对：%s" % path)
    if total != len(b):
        raise ValueError("GLB 声明长度 %d != 实际 %d：%s" % (total, len(b), path))
    off, js, binb = 12, None, b""
    while off < len(b):
        ln, typ = struct.unpack_from("<II", b, off)
        off += 8
        chunk = b[off:off + ln]
        off += ln
        if typ == 0x4E4F534A:
            js = json.loads(chunk.decode("utf-8"))
        elif typ == 0x004E4942:
            binb = chunk
    if js is None:
        raise ValueError("GLB 缺 JSON chunk：%s" % path)
    return js, binb


def _write_glb(out_path: Path, js: dict, binb: bytes) -> int:
    payload = binb + b"\x00" * ((-len(binb)) % 4)
    jsb = json.dumps(js, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    jsb += b" " * ((-len(jsb)) % 4)
    total = 12 + 8 + len(jsb) + (8 + len(payload) if payload else 0)
    with out_path.open("wb") as fh:
        fh.write(struct.pack("<III", 0x46546C67, 2, total))
        fh.write(struct.pack("<II", len(jsb), 0x4E4F534A)); fh.write(jsb)
        if payload:
            fh.write(struct.pack("<II", len(payload), 0x004E4942)); fh.write(payload)
    return total


def _merge_glbs(part_glbs: list, out_path: Path, extras: dict) -> dict:
    """N 个部件 GLB → 1 个 GLB（部件顶点已是世界坐标 ⇒ 合并即归位，无节点变换）。"""
    out = dict(asset=dict(version="2.0",
                          generator="la-toolkit glb v1 (mesh_parse2 + export_glb per part, merged)"),
               scene=0, scenes=[dict(nodes=[])], nodes=[], meshes=[], materials=[],
               textures=[], images=[], samplers=[], accessors=[], bufferViews=[],
               buffers=[dict(byteLength=0)])
    bins, base = [], 0
    mat_keys, img_keys, tex_keys, samp_keys = {}, {}, {}, {}
    per_part = []
    for idx, (mesh_path, glb_path, label) in enumerate(part_glbs):
        js, binb = _read_glb(glb_path)
        blob = binb + b"\x00" * ((-len(binb)) % 4)
        bv_base, acc_base = len(out["bufferViews"]), len(out["accessors"])
        for bv in js.get("bufferViews", []):
            nb = dict(bv); nb["byteOffset"] = int(bv.get("byteOffset", 0)) + base
            out["bufferViews"].append(nb)
        for acc in js.get("accessors", []):
            na = dict(acc); na["bufferView"] = int(acc["bufferView"]) + bv_base
            out["accessors"].append(na)
        samp_map = [_dedupe(out["samplers"], samp_keys, dict(s), lambda d: d.get("magFilter"),
                            json.dumps(s, sort_keys=True)) for s in js.get("samplers", [])]
        img_map = [_dedupe(out["images"], img_keys,
                           dict(im, bufferView=int(im["bufferView"]) + bv_base), lambda d: d.get("name"),
                           im.get("name")) for im in js.get("images", [])]
        tex_map = [_dedupe(out["textures"], tex_keys,
                           dict(t, source=img_map[int(t["source"])],
                                sampler=samp_map[int(t["sampler"])] if "sampler" in t else None),
                           lambda d: (d.get("source"), d.get("sampler")),
                           (img_map[int(t["source"])], samp_map[int(t["sampler"])] if "sampler" in t else None))
                   for t in js.get("textures", [])]
        mat_map = []
        for m in js.get("materials", []):
            nm = copy.deepcopy(m)
            pbr = nm.get("pbrMetallicRoughness", {})
            for key in ("baseColorTexture", "metallicRoughnessTexture"):
                if key in pbr:
                    pbr[key] = dict(pbr[key]); pbr[key]["index"] = tex_map[int(pbr[key]["index"])]
            for key in ("normalTexture", "occlusionTexture", "emissiveTexture"):
                if key in nm:
                    nm[key] = dict(nm[key]); nm[key]["index"] = tex_map[int(nm[key]["index"])]
            nm["extras"] = dict(nm.get("extras") or {}, part=label)
            mat_map.append(_dedupe(out["materials"], mat_keys, nm, lambda d: d.get("name"), nm.get("name")))
        js_meshes = []
        for m in js.get("meshes", []):
            nm = dict(m); prims = []
            for pr in m.get("primitives", []):
                np_ = dict(pr)
                np_["attributes"] = {k: int(v) + acc_base for k, v in pr["attributes"].items()}
                if "indices" in pr:
                    np_["indices"] = int(pr["indices"]) + acc_base
                if "material" in pr and mat_map:
                    np_["material"] = mat_map[int(pr["material"])]
                prims.append(np_)
            nm["primitives"] = prims
            out["meshes"].append(nm)
            js_meshes.append(len(out["meshes"]) - 1)
        for m_i in js_meshes:
            out["nodes"].append(dict(mesh=m_i, name=label))
            out["scenes"][0]["nodes"].append(len(out["nodes"]) - 1)
        per_part.append(dict(index=idx, label=label, mesh=str(mesh_path), part_glb=str(glb_path),
                             part_bytes=len(blob), nodes=len(js_meshes),
                             accessors=len(js.get("accessors", [])),
                             bufferViews=len(js.get("bufferViews", [])),
                             materials=len(js.get("materials", [])),
                             images=len(js.get("images", []))))
        bins.append(blob); base += len(blob)
    binb = b"".join(bins)
    out["buffers"][0]["byteLength"] = len(binb)
    out["extras"] = dict(extras, parts=per_part)
    size = _write_glb(out_path, out, binb)
    return dict(out=str(out_path), size=size, bin_bytes=len(binb),
                nodes=len(out["nodes"]), meshes=len(out["meshes"]),
                accessors=len(out["accessors"]), bufferViews=len(out["bufferViews"]),
                materials=len(out["materials"]), images=len(out["images"]),
                parts=per_part)


def _dedupe(store: list, keys: dict, item: dict, key_fn, key) -> int:
    if key in keys:
        return keys[key]
    store.append(item)
    keys[key] = len(store) - 1
    return keys[key]


def verify_glb(path: Path, expected_bbox: list, expected_faces: int) -> dict:
    """结构自检 + 几何回读：buffer/bufferView/accessor 边界、POSITION bbox、索引总量。"""
    js, binb = _read_glb(path)
    problems = []
    if int(js["buffers"][0]["byteLength"]) != len(binb):
        problems.append("buffers[0].byteLength=%s 实际 bin=%d" % (js["buffers"][0]["byteLength"], len(binb)))
    for i, bv in enumerate(js.get("bufferViews", [])):
        if int(bv.get("byteOffset", 0)) + int(bv["byteLength"]) > len(binb):
            problems.append("bufferView[%d] 越界" % i)
    for i, acc in enumerate(js.get("accessors", [])):
        if "bufferView" in acc and int(acc["bufferView"]) >= len(js["bufferViews"]):
            problems.append("accessor[%d].bufferView 越界" % i)
    for i, pr in enumerate([p for m in js["meshes"] for p in m["primitives"]]):
        for k, v in pr["attributes"].items():
            if int(v) >= len(js["accessors"]):
                problems.append("primitive[%d].%s accessor 越界" % (i, k))
        if "indices" in pr and int(pr["indices"]) >= len(js["accessors"]):
            problems.append("primitive[%d].indices accessor 越界" % i)
        if "material" in pr and int(pr["material"]) >= len(js.get("materials", [])):
            problems.append("primitive[%d].material 越界" % i)

    prims = [p for m in js["meshes"] for p in m["primitives"]]
    idx_total = sum(int(js["accessors"][int(p["indices"])]["count"]) for p in prims if "indices" in p)
    pos_mm, seen = [], set()
    for p in prims:
        a = js["accessors"][int(p["attributes"]["POSITION"])]
        key = int(p["attributes"]["POSITION"])
        if key in seen:
            continue
        seen.add(key)
        pos_mm.append(dict(accessor=key, count=int(a["count"]), min=a.get("min"), max=a.get("max")))
    match = len(pos_mm) == len(expected_bbox)
    if match:
        for got, exp in zip(pos_mm, expected_bbox):
            for ax in range(3):
                if abs(float(got["min"][ax]) - exp["min"][ax]) > 1e-4 or abs(float(got["max"][ax]) - exp["max"][ax]) > 1e-4:
                    match = False
    if not match:
        problems.append("POSITION accessor min/max 与解析结果不一致（%d 组 vs 期望 %d 组）"
                        % (len(pos_mm), len(expected_bbox)))
    if idx_total != 3 * expected_faces:
        problems.append("索引总量 %d != 3 × 总三角数 %d" % (idx_total, 3 * expected_faces))
    return dict(path=str(path), size_bytes=path.stat().st_size, sha256_16=_sha16(path),
                nodes=len(js.get("nodes", [])), meshes=len(js["meshes"]), primitives=len(prims),
                materials=len(js.get("materials", [])), images=len(js.get("images", [])),
                accessors=len(js.get("accessors", [])), bufferViews=len(js.get("bufferViews", [])),
                bin_bytes=len(binb), index_count=idx_total, expected_index_count=3 * expected_faces,
                position_accessors=pos_mm, position_bbox_match=bool(match and not problems),
                problems=problems, pass_=not problems)


# ============================================================================
# 4. 主流程
# ============================================================================
def run(mesh_paths, mat=None, tex=None, out=None, force=False, json_path=None) -> tuple:
    """→ (exit_code, report)。cmd_glb 只是薄封装。"""
    t0 = time.time()
    meshes = [Path(m) for m in mesh_paths]
    mat_path = Path(mat) if mat else None
    tex_dir = Path(tex) if tex else None

    first = meshes[0].stem if meshes else "out"
    default_name = ("%s.glb" % first) if len(meshes) <= 1 else ("%s_merge%d.glb" % (first, len(meshes)))
    out_path = Path(out) if out else (DEFAULT_GLB_DIR / default_name)
    out_path = out_path.resolve()
    failures_log = out_path.parent / FAILURE_LOG_NAME
    failures = []

    report = dict(tool=TOOLKIT_VERSION, started=time.strftime("%Y-%m-%dT%H:%M:%S"),
                  inputs=[str(m) for m in meshes], mat=str(mat_path) if mat_path else None,
                  tex=str(tex_dir) if tex_dir else None, out=str(out_path),
                  out_exists=out_path.is_file(), force=bool(force),
                  env=_env_probe(), parts=[], failures=failures, failures_log=str(failures_log),
                  assumptions=[
                      "部件顶点已是世界坐标 ⇒ 直接合并即自动归位（不做中心化/缩放，用户明确「不归零」）",
                      "★★ 解析完整性判据（2026-09-26 A11 修正）：%s ⇒ 报告字段 integrity_ok/alarm。" % INTEGRITY_JUDGE,
                      "tf/tv 比值（tri_per_vert）仅作**信息输出**：本仓实测旧口径 tf/tv<1.5 触发 184/188=97.87%%，"
                      "无区分度 ⇒ 已降级 ratio_alarm(reason=info_only)，不计入 alarm、不参与退出码。"
                      "分发依据 RATIO_STATS_20260926；若坚持比值告警按分布取 p05≈%.2f。" % RATIO_RECALIBRATED_HINT,
                      "解析器直接抛异常的文件（如 ValueError: 无法定位 sub 表）**两条判据都覆盖不到**，"
                      "它们出现在 failures 清单里，不在 parts 里。",
                      "显示端需 THREE rotation.x=Math.PI（导出侧不加旋转）",
                  ])

    # --- 输出拒绝（无 --force） ---
    if out_path.is_file() and not force:
        report["status"] = "refused_exists"
        report["message"] = "输出已存在：%s（加 --force 覆盖）" % out_path
        _dump_report(report, json_path)
        print(report["message"], file=sys.stderr)
        return 2, report

    # --- 依赖探针 ---
    if report["env"].get("numpy") is None or report["env"].get("pillow") is None:
        rec = dict(kind="env", error="缺 numpy/PIL：numpy=%s PIL=%s"
                   % (report["env"].get("numpy_error"), report["env"].get("pillow_error")))
        failures.append(rec); _append_failure(failures_log, rec)
        report["status"] = "env_error"
        _dump_report(report, json_path); print("环境缺依赖：%s" % rec["error"], file=sys.stderr)
        return 5, report

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = Path(tempfile.mkdtemp(prefix="la_glb_"))
    try:
        # --- 材质 / 贴图 ---
        report["material"] = analyze_material(mat_path)
        if mat_path is not None and report["material"].get("ok") is False:
            rec = dict(kind="mat", file=str(mat_path), error=report["material"].get("error"))
            failures.append(rec); _append_failure(failures_log, rec)
        try:
            report["textures"] = resolve_textures(tex_dir, mat_path, tmpdir)
        except Exception as exc:                                    # noqa: BLE001
            rec = dict(kind="texture", tex=str(tex_dir), error="%s: %s" % (type(exc).__name__, exc))
            failures.append(rec); _append_failure(failures_log, rec)
            report["textures"] = dict(tex_dir=str(tex_dir) if tex_dir else None, slots={},
                                      warnings=["贴图阶段整体失败：%s" % rec["error"]],
                                      declared=[], groups={}, failures=[])
        for rec in report["textures"].get("failures", []):
            failures.append(rec); _append_failure(failures_log, rec)
        slots = report["textures"]["slots"]
        set_name = ("la_%s" % (tex_dir.name if tex_dir else (mat_path.stem if mat_path else first)))
        texmap_path = tmpdir / "texmap.json"
        texmap_path.write_text(json.dumps(dict(sets={set_name: dict(slots)},
                                              note="toolkit glb 自动生成（见报告 texture_resolution）"),
                                         ensure_ascii=False, indent=1), encoding="utf-8")
        report["set_name"] = set_name
        report["texmap"] = dict(path=str(texmap_path), slots=slots)

        # --- 逐部件解析（失败进清单，不静默跳过） ---
        ok_bbox, total_v, total_f = [], 0, 0
        for m in meshes:
            if not m.is_file():
                rec = dict(kind="mesh", mesh=str(m), error="文件不存在")
                failures.append(rec); _append_failure(failures_log, rec); continue
            try:
                P, uv, idx, meta = parse_part(m)
                info = part_selfcheck(m, P, idx, meta)
                part_glb = tmpdir / ("part_%03d.glb" % len(ok_bbox))
                info["part_glb"] = str(part_glb)
                info["export"] = export_part_glb(m, texmap_path, set_name, part_glb, m.stem)
                import numpy as np
                pf = np.asarray(P, np.float32)
                ok_bbox.append(dict(min=[float(x) for x in pf.min(0)], max=[float(x) for x in pf.max(0)]))
                total_v += info["vertices"]; total_f += info["faces"]
                report["parts"].append(info)
            except Exception as exc:                                # noqa: BLE001
                rec = dict(kind="mesh", mesh=str(m), error="%s: %s" % (type(exc).__name__, exc))
                failures.append(rec); _append_failure(failures_log, rec)

        report["totals"] = dict(
            parts_in=len(meshes), parts_ok=len(report["parts"]),
            parts_failed=sum(1 for f in failures if f.get("kind") == "mesh"),
            total_vertices=total_v, total_faces=total_f,
            tri_per_vert_overall=round(total_f / total_v, 4) if total_v else 0.0,
            ratio_alarm_parts=[p["name"] for p in report["parts"] if p["ratio_alarm"]])
        if not report["parts"]:
            report["status"] = "no_part_exported"
            report["message"] = "无任何部件解析/导出成功，见失败清单 %s" % failures_log
            _dump_report(report, json_path)
            print(report["message"], file=sys.stderr)
            return 3, report

        # --- 合并 ---
        merge = _merge_glbs([(p["path"], Path(p["part_glb"]), p["name"]) for p in report["parts"]],
                            out_path,
                            dict(tool=TOOLKIT_VERSION, source_meshes=[p["path"] for p in report["parts"]],
                                 set_name=set_name, texmap=dict(slots=slots),
                                 mat_file=str(mat_path) if mat_path else None,
                                 world_space_note="各部件顶点为源世界坐标；合并未做中心化/缩放/旋转",
                                 display_note="显示端挂 THREE 时统一 rotation.x = Math.PI"))
        report["merge"] = merge
        report["verify"] = verify_glb(out_path, ok_bbox, total_f)
        report["expected_bbox_union"] = dict(
            min=[min(b["min"][i] for b in ok_bbox) for i in range(3)],
            max=[max(b["max"][i] for b in ok_bbox) for i in range(3)])
        report["elapsed_s"] = round(time.time() - t0, 3)
        partial = bool(failures)
        report["status"] = "partial" if partial else "ok"
        _dump_report(report, json_path)
        _print_summary(report)
        return (4 if partial else 0), report
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def _dump_report(report: dict, json_path) -> None:
    if json_path:
        p = Path(json_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("报告已写入：%s" % p)


def _print_summary(report: dict) -> None:
    print("== la-toolkit glb ==")
    for p in report.get("parts", []):
        # ★ 修复（2026-09-26，A11）：告警以 integrity_ok 为准；tf/tv 仅作信息打印。
        flag = "  ⚠ 解析不完整" if p.get("alarm") else ""
        print("  %-34s v=%-6d f=%-6d tf/tv=%-6.3f subs=%d sizes_ok=%s/%s%s"
              % (p["name"], p["vertices"], p["faces"], p["tri_per_vert"], p["submeshes"],
                 p["sizes_ok"], p["extra_streams_state"], flag))
        if p.get("alarm") and p.get("alarm_reason"):
            print("     ↑ %s" % p["alarm_reason"])
        print("     文件 bbox min=%s max=%s%s" % (p["bbox_file_min"], p["bbox_file_max"],
                                              "（文件内 min/max 反序，已按实测世界坐标纠正）"
                                              if p["bbox_file_inverted"] else ""))
        print("     世界 bbox min=%s max=%s span=%s 唯一顶点=%d 重复率=%s"
              % (p["bbox_world_min"], p["bbox_world_max"], p["bbox_file_span"],
                 p["unique_positions"], p["dup_vertex_ratio"]))
    t = report.get("totals", {})
    print("  合计: 部件 %d/%d 成功, 顶点 %d, 三角 %d" % (t.get("parts_ok"), t.get("parts_in"),
                                                  t.get("total_vertices"), t.get("total_faces")))
    v = report.get("verify", {})
    if v:
        print("  GLB: %s (%d B) nodes=%d prims=%d materials=%d images=%d"
              % (report["out"], v.get("size_bytes", 0), v.get("nodes"), v.get("primitives"),
                 v.get("materials"), v.get("images")))
        print("  自检: POSITION bbox 一致=%s 索引总量=%d(=3×%d) 问题=%s"
              % (v.get("position_bbox_match"), v.get("index_count"), t.get("total_faces"),
                 v.get("problems") or "无"))
    if report.get("failures"):
        print("  失败 %d 项（清单：%s）" % (len(report["failures"]), report.get("failures_log")))
        for f in report["failures"]:
            print("    ✗ [%s] %s :: %s" % (f.get("kind"), f.get("mesh") or f.get("file"), f.get("error")))
    if report.get("textures", {}).get("warnings"):
        for w in report["textures"]["warnings"]:
            print("  ⚠ 贴图: %s" % w)
    print("  状态=%s" % report.get("status"))
