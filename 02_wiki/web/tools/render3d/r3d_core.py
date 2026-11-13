# -*- coding: utf-8 -*-
"""r3d_core.py — 3D 资产流水线公共层：路径 / 契约 / 幂等写盘 / 证据

★ 纪律（rules/render3d.yml）：
  · 路径一律经 la_paths 派生，本文件内不得出现设备绝对路径；
  · 契约是唯一口径来源，脚本只读不写；
  · 默认 dry-run，--apply 才落盘；先算差异，一致则不写（字节级幂等）；
  · 拿不到证据标 unresolved 并写报告，绝不伪造。

用法（作为库）：from r3d_core import paths, contract, write_json_idempotent
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from la_paths import (  # noqa: E402
    PROJ, WEB, TREE_ROOT, ANALYSIS_ROOT, STATE_DIR, RULES_DIR, TOOLKIT_LIB, ENV_DIR,
)

# ── 路径（全部由 la_paths 派生）───────────────────────────────────────────
RULES_FILE = RULES_DIR / "render3d.yml"
PE_RES = TREE_ROOT / "pe" / "资源"
PE_CHARACTER = PE_RES / "character"
F3D = ANALYSIS_ROOT / "_fashion3d"
FASHION_INDEX = F3D / "fashion_index.json"
ASSETS_3D = WEB / "assets" / "3d"
FASHION_3D = ASSETS_3D / "fashion_3d"
SKIN_CHAIN = TOOLKIT_LIB / "02_图文音频渲染" / "皮肤链与渲染"
EXPORTER = SKIN_CHAIN / "fashion_glb.py"
TEX_CACHE = F3D / "texcache"          # 既有缓存，只复用不新建体系
STATE = STATE_DIR / "render3d"
ROSTER = STATE / "roster.json"
STAGING = STATE / "staging"
VERIFY_REPORT = STATE / "verify_report.json"
PIPELINE_REPORT = STATE / "pipeline_report.json"

WEAPON_3D = ASSETS_3D / "weapon_skin"
WEAPON_INVENTORY = STATE / "weapon_inventory.json"
WEAPON_VERIFY_REPORT = STATE / "weapon_verify_report.json"
C159_SURVEY = F3D / "weapon_c159_material_survey.json"

SEP = " ｜ "

# ── mesh 有效性（选型后的再校验；桩/_shadow 文件魔数不对，必须剔除）──────
MESH_MAGIC = b"\x34\x80\xc8\xbb"   # .mesh 格式魔数（little-endian uint32 0xbbc88034）


def mesh_evidence(p: pathlib.Path, root: pathlib.Path | None = None) -> dict:
    """单个 .mesh 源文件的有效性证据。非法（桩/坏魔数）标 bad_magic，绝不补占位。"""
    if not p.exists():
        return {"rel": _rel(p, root), "status": "missing"}
    try:
        head = p.read_bytes()[:4]
    except Exception:
        return {"rel": _rel(p, root), "status": "unreadable"}
    if head != MESH_MAGIC:
        # 44 字节 _shadow 桩（全 0）或其他容器 → 非可解析 .mesh
        return {"rel": _rel(p, root), "status": "bad_magic",
                "bytes": p.stat().st_size, "sha256": sha256_file(p)}
    return {"rel": _rel(p, root), "status": "ready",
            "bytes": p.stat().st_size, "sha256": sha256_file(p)}


def resolve_mesh(mesh_rel: str) -> tuple[str, dict, str, str | None]:
    """给定选型候选 mesh 相对路径，返回 (final_rel, ev, status, reason)。

    status ∈ {ready, missing, bad_magic, gim_only}：
      · 候选合法                 → ready（原样返回）
      · 候选非法                 → 在同级目录找别的合法 .mesh；找到则用
      · 同级无合法 .mesh 但有 .gim → gim_only（几何体为 .gim，当前导出器不支持）
      · 否则                     → missing
    ★ 不臆造：找不到可用 mesh 就如实标 gim_only/missing，不拿别的部件顶替。
    """
    cand = PE_CHARACTER / mesh_rel
    ev = mesh_evidence(cand, PE_RES)
    if ev["status"] == "ready":
        return mesh_rel, ev, "ready", None
    d = cand.parent
    if d.exists():
        cands = []
        for m in sorted(d.glob("*.mesh")):
            e2 = mesh_evidence(m, PE_RES)
            if e2["status"] == "ready":
                nm = m.name
                # 优先非 _shadow / _lod 的件
                penalty = 1 if ("_shadow" in nm or "_lod" in nm) else 0
                cands.append((penalty, nm, e2))
        if cands:
            cands.sort(key=lambda x: (x[0], x[1]))
            nm = cands[0][1]
            final = (d / nm).relative_to(PE_RES).as_posix()
            return final, cands[0][2], "ready", "re-resolved from sibling (candidate was %s)" % ev["status"]
        # ★ 跨目录装配：同级 .gim 描述符可能引用外部 .mesh 几何体
        #   （如 suit_f_3007_eu → character\players\suit_f_3007\suit_f_3007.mesh）。
        #   解析 .gim 抽取其引用的合法 .mesh，定位成功即升级为 ready；绝不伪造。
        if list(d.glob("*.gim")):
            from r3d_gim import parse as _parse_gim, normalize_ref as _norm
            refs2 = []
            for gim in sorted(d.glob("*.gim")):
                gi = _parse_gim(gim)
                for ref in gi.get("references", []):
                    if not ref.lower().endswith(".mesh"):
                        continue
                    rel = _norm(ref)
                    cand2 = PE_CHARACTER / rel
                    ev2 = mesh_evidence(cand2, PE_RES)
                    if ev2["status"] == "ready":
                        nm2 = cand2.name
                        penalty = 1 if any(k in nm2 for k in ("_shadow", "_lod", "_preview")) else 0
                        refs2.append((penalty, rel, ev2, gim.name))
            if refs2:
                refs2.sort(key=lambda x: (x[0], x[1]))
                _, rel, ev2, gn = refs2[0]
                return rel, ev2, "ready", "resolved via .gim ref %s → %s" % (gn, rel)
            return mesh_rel, ev, "gim_only", "同级无合法 .mesh 且 .gim 引用未定位到可用几何体（导出器不支持 .gim 内嵌）"
    return mesh_rel, ev, "missing", "mesh 非法（%s）且同级无可用 .mesh" % ev["status"]



def paths() -> dict:
    return {
        "PROJ": str(PROJ), "RULES_FILE": str(RULES_FILE), "PE_RES": str(PE_RES),
        "FASHION_INDEX": str(FASHION_INDEX), "FASHION_3D": str(FASHION_3D),
        "EXPORTER": str(EXPORTER), "STATE": str(STATE),
    }


# ── 契约 ──────────────────────────────────────────────────────────────────
def _load_yaml(p: pathlib.Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except ImportError:
        pass
    # 回退仓库内 mini_yaml（与 build_pipeline.py 同口径）
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "build"))
    try:
        from build_pipeline import parse_yaml_text  # noqa
        return parse_yaml_text(p.read_text(encoding="utf-8"), "render3d 契约")
    except Exception as exc:
        raise SystemExit("❌ 无法解析契约 %s（缺 PyYAML 且 mini_yaml 回退失败）：%r" % (p, exc))


def contract() -> dict:
    if not RULES_FILE.exists():
        raise SystemExit("❌ 找不到契约：%s\n   口径只写在契约里，缺失时不臆造。" % RULES_FILE)
    c = _load_yaml(RULES_FILE)
    for key in ("version", "policy", "data_sources", "fidelity", "stages", "golden_set"):
        if key not in c:
            raise SystemExit("❌ 契约缺字段 %s：%s" % (key, RULES_FILE))
    return c


def golden(c: dict | None = None) -> list[dict]:
    return (c or contract())["golden_set"]


def fidelity_levels(c: dict | None = None) -> list[str]:
    return list((c or contract())["fidelity"]["levels"])


# ── 证据 ──────────────────────────────────────────────────────────────────
def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def evidence(p: pathlib.Path, root: pathlib.Path | None = None) -> dict:
    """单个源文件的证据块。不存在 ⇒ status=missing，绝不补占位值。"""
    if not p.exists():
        return {"rel": _rel(p, root), "status": "missing"}
    return {
        "rel": _rel(p, root), "status": "ready",
        "bytes": p.stat().st_size, "sha256": sha256_file(p),
    }


def _rel(p: pathlib.Path, root: pathlib.Path | None) -> str:
    try:
        return str(p.relative_to(root or PE_RES)).replace("\\", "/")
    except (ValueError, TypeError):
        return str(p).replace("\\", "/")


# ── 幂等写盘 ─────────────────────────────────────────────────────────────
def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n"


def write_json_idempotent(p: pathlib.Path, obj, apply: bool, label: str = "") -> str:
    """返回 same | diff | new | dry-<state>。apply=False 时绝不写盘。"""
    want = dumps(obj)
    cur = p.read_text(encoding="utf-8") if p.exists() else None
    state = "same" if cur == want else ("new" if cur is None else "diff")
    if not apply:
        print("  [DRY ] %-28s %s%s" % (label or p.name, state, "" if state == "same" else " → 需 --apply"))
        return "dry-" + state
    if state == "same":
        print("  [SAME] %-28s 幂等，未写盘" % (label or p.name))
        return "same"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(want, encoding="utf-8")
    print("  [WRITE] %-28s %s" % (label or p.name, state))
    return state


def read_json(p: pathlib.Path, default=None):
    if not p.exists():
        if default is not None:
            return default
        raise SystemExit("❌ 缺输入 %s；先跑前置阶段，不臆造数据。" % p)
    return json.loads(p.read_text(encoding="utf-8"))


def ensure_state() -> None:
    STATE.mkdir(parents=True, exist_ok=True)


def note_append(existing: str, note: str) -> str:
    """幂等追加口径说明（与 notes_util.append_note 同分隔符，但不碰板产物）。"""
    parts = [x for x in (existing or "").split(SEP) if x.strip()]
    if note not in parts:
        parts.append(note)
    return SEP.join(parts)


# ── GLB 结构解析（质检用；只读，不改写既有产物）─────────────────────────
_ABS_IN_JSON = re.compile(r'"[^"]*la拆包项目[^"]*"')


def canonicalize_paths(text: str) -> str:
    """把 JSON chunk 里所有含项目根的字符串值统一成占位符。

    ★ 既有 GLB 把本机绝对路径（e:/la拆包项目/...）写进了 extras.source_mesh /
      extras.texmap / materials[].extras.source_slots.*.path，换机即失效。
      本轮**不改写这些产物**（会动 45MB 且需用户批准），只在质检时剥离，
      以便区分「路径字面量差异」与「几何/材质语义差异」。
    """
    return _ABS_IN_JSON.sub('"<PROJ>"', text)


def abs_path_present(p: pathlib.Path) -> bool:
    """GLB 的 JSON chunk 是否内嵌本机绝对路径（可移植性缺口探测）。"""
    info = glb_chunks(p)
    if not info["valid"]:
        return False
    return canonicalize_paths(info["json"]) != info["json"]


def glb_chunks(p: pathlib.Path) -> dict:
    """解析 GLB 头与 chunk。不合法则 valid=False 并给原因，绝不抛异常。

    ★ 允许两种结构：
      (a) 标准 glTF2：JSON chunk + BIN chunk；
      (b) JSON-only glB（如骨骼绑定 rig，仅 JSON 无几何 buffer，BIN 缺失）。
    只对 magic/version/长度/首个 chunk 为可解析 JSON 做硬性校验；
    BIN 缺失只标 json_only，不判非法。
    """
    try:
        b = p.read_bytes()
        if len(b) < 20:
            return {"valid": False, "error": "文件过短"}
        magic, ver, total = struct.unpack_from("<4sII", b, 0)
        if magic != b"glTF" or ver != 2:
            return {"valid": False, "error": "magic/version 非 glTF 2.0"}
        if total != len(b):
            return {"valid": False, "error": "头长度 %d ≠ 实际 %d" % (total, len(b))}
        chunks, off = [], 12
        while off < len(b):
            if off + 8 > len(b):
                return {"valid": False, "error": "chunk 头越界"}
            clen, ctype = struct.unpack_from("<I4s", b, off)
            if off + 8 + clen > len(b):
                return {"valid": False, "error": "chunk 数据越界"}
            chunks.append((ctype, b[off + 8:off + 8 + clen]))
            off += 8 + clen
        if off != len(b) or len(chunks) < 1 or chunks[0][0] != b"JSON":
            return {"valid": False, "error": "chunk 结构异常（首 chunk 非 JSON 或越界）"}
        jtxt = chunks[0][1].decode("utf-8").rstrip(" \x00")
        json.loads(jtxt)  # 确认可解析
        bin_data = chunks[1][1] if len(chunks) >= 2 and chunks[1][0] == b"BIN\x00" else b""
        json_only = len(chunks) < 2 or chunks[1][0] != b"BIN\x00"
        return {"valid": True, "raw": b, "json": jtxt, "bin": bin_data,
                "json_bytes": len(chunks[0][1]), "bin_bytes": len(bin_data),
                "json_only": json_only}
    except Exception as exc:
        return {"valid": False, "error": repr(exc)}


def glb_equivalence(p1: pathlib.Path, p2: pathlib.Path) -> str:
    """identical | path_literal_only | semantic_diff | missing | invalid"""
    if not p1.exists() or not p2.exists():
        return "missing"
    a, b = glb_chunks(p1), glb_chunks(p2)
    if not a["valid"] or not b["valid"]:
        return "invalid"
    if a["raw"] == b["raw"]:
        return "identical"
    if canonicalize_paths(a["json"]) == canonicalize_paths(b["json"]) and a["bin"] == b["bin"]:
        return "path_literal_only"
    return "semantic_diff"


if __name__ == "__main__":
    print(json.dumps(paths(), ensure_ascii=False, indent=1))
    print("契约 golden_set =", len(golden()), "套")
