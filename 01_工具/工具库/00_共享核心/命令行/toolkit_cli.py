# -*- coding: utf-8 -*-
"""明日之后拆包器统一命令行：索引优先、定点查询、定点提取。"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

from toolkit_core import hotfix_bundle as HB
from toolkit_core.paths import (ANALYSIS_ROOT, DEFAULT_NAMES_DICT, DEFAULT_OUTPUT_ROOT,
                                INDEX_ROOT, PROJECT_ROOT)
from toolkit_core.unified_index import (
    AmbiguousMatch, IndexNotReady, UnifiedFileIndex, build_database, path_fid)

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ★ 原先写 Path(__file__).resolve().parents[3] —— 手算层级，项目明文禁止；
#   且 2026-09-26 把散文件分进中文文件夹后（本文件在 00_共享核心/命令行/），
#   层数又变了。改为从 toolkit_core.paths 取（那里已实现四优先级定位）。
PROJECT_ROOT = PROJECT_ROOT
DEFAULT_DB = INDEX_ROOT / "indexes" / "lifeafter_files.sqlite3"
DEFAULT_RESTORE = Path(str(INDEX_ROOT).replace("10_索引", "41_还原树"))
DEFAULT_FPK_INDEX = INDEX_ROOT / "fpk_fid_index.json"
DEFAULT_RES_ROOT = Path(r"E:\mrzh")

# ── 带 H · H-2：本地容器快照 ──
#   ★ 治理边界：只允许扫 E:\mrzh（体验服）；正式服 E:\LifeAfter 与其它路径一律拒绝。
SNAPSHOT_ALLOWED_ROOTS = (r"e:\mrzh",)
DEFAULT_SNAPSHOT_ROOT = Path(r"E:\mrzh")
SNAPSHOT_OUT_ROOT = PROJECT_ROOT / "03_执行" / "10_索引" / "patch_snapshots"

# ═══════════════════════════════════════════════════════════════════════════
# 命令 → 段位 登记（唯一入口：所有子命令都经由 _sp() 创建）
#   ★ 为什么这么做：`map` 要打印「段位 → 命令」，而命令定义只能有一份
#     （见 规范/CLI与EXE统一方案.md：两套定义会让「改一处、另一处静默坏掉」）。
#     段位取自 help 开头的 [①-1] 前缀 —— 那是页面的跳转锚点，不能删；
#     带子子命令的组（index/names/delta/resolver/texscan/snapshot）用 _inherit 继承。
# ═══════════════════════════════════════════════════════════════════════════

COMMANDS: list[dict[str, str]] = []          # [{seg, name, full, help}]
_SEG_CONTEXT: dict[int, tuple[str, str]] = {}   # id(subparsers_action) -> (段位, 父命令)


def _seg_of_help(help_text: str | None) -> str:
    m = re.match(r"^\s*\[([^\]]+)\]", help_text or "")
    return m.group(1) if m else ""


def _sp(sub, name: str, help: str | None = None, seg: str | None = None, **kw):
    """创建子命令并登记段位（`help` 仍原样传给 argparse ⇒ --help 输出不变）。"""
    if help is not None:
        kw["help"] = help
    _add = getattr(sub, "add_parser")
    parser = _add(name, **kw)
    inherited, parent = _SEG_CONTEXT.get(id(sub), ("", ""))
    seg = seg or _seg_of_help(help) or inherited
    if seg:
        COMMANDS.append({"seg": seg, "name": name,
                         "full": ("%s %s" % (parent, name)) if parent else name,
                         "help": help or ""})
    return parser


def _inherit(sub_action, seg: str, parent: str = "") -> None:
    """让某个子命令组下的子子命令（它们没有 [段位] 前缀）继承段位。"""
    _SEG_CONTEXT[id(sub_action)] = (seg, parent)


def commands_by_seg() -> dict[str, list[str]]:
    """段位 → 命令名（按登记顺序）。多次调用 build_parser() 也不会重复。

    有子子命令的组只列子命令（`delta fetch` 而不是 `delta` + `delta fetch`）。
    """
    out: dict[str, list[str]] = {}
    seen: set[tuple[str, str]] = set()
    for c in COMMANDS:
        k = (c["seg"], c["full"])
        if k in seen:
            continue
        seen.add(k)
        out.setdefault(c["seg"], []).append(c["full"])
    for seg, names in out.items():
        if len(names) < 2:
            continue
        out[seg] = [n for n in names
                    if not any(o != n and o.startswith(n + " ") for o in names)]
    return out



def _sidecar_path(kind: str, database) -> Path:
    """sidecar 落在与索引库同目录，命名沿用既有约定。"""
    return Path(database).resolve().parent / f"lifeafter_files_{kind}.json"


def _dump(value: object, destination: str | None = None, *,
          sidecar: Path | None = None, quiet: bool = False) -> None:
    """输出报告。

    · 显式 --json：写到指定位置（原行为不变）
    · 否则：默认同步到 sidecar，让状态文件随索引自动更新
            （不这样做，索引重建后 sidecar 会停在旧值上误导下游）
    · sidecar 写失败只告警，绝不影响命令本身的结果与退出码
    """
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    # ★ 2026-09-28 修：所有命令的 --json 都写的是「裸用打 stdout（const="-"）」，
    #   但这里一直把 "-" 当文件名 ⇒ 写出一个名为 `-` 的杂文件、stdout 反而空。
    #   调用方（脚本 / 主页采集器 / 管道）拿不到 JSON。
    if destination == "-":
        print(text, end="")
        return
    if destination:
        path = Path(destination).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"已写入：{path}")
        return
    if sidecar is not None:
        try:
            path = Path(sidecar).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            if not quiet:
                # ★ 必须同时把 JSON 打到 stdout —— 保持 stdout 契约不变。
                #   曾有版本在此 return 只打印「已同步」，导致解析 stdout 的
                #   调用方（脚本 / 主页采集器 / 管道）静默拿到空值。
                print(text, end="")
                print(f"已同步：{path}", file=sys.stderr)
            return
        except OSError as exc:
            print(f"⚠ sidecar 同步失败（不影响本次结果）：{exc}", file=sys.stderr)
    print(text, end="")


def _sync(args, kind: str) -> Path | None:
    """取该命令的 sidecar 目标；--no-sidecar 时返回 None。"""
    if getattr(args, "no_sidecar", False):
        return None
    return _sidecar_path(kind, args.db)


def _open(args) -> UnifiedFileIndex:
    return UnifiedFileIndex(args.db, res_root=getattr(args, "res_root", None))


def cmd_index_build(args) -> int:
    report = build_database(args.db, res_root=args.res_root, fpk_index=args.fpk_index,
                            include=args.include, progress=None if args.quiet else print)
    _dump(report, args.json, sidecar=_sync(args, "build"), quiet=args.quiet)
    return 0 if not report["failures"] else 4


def cmd_export(args) -> int:
    """解析结果 → 表格文件（通用导出器）。

    ★ 为什么要有这条命令：历史上每要一张表都现写一个一次性脚本（qj_*.py 写了 40+ 个），
      每次都要重推「去哪拿 body、池子怎么解、是哪一族、行怎么落文件」。
      现在固定成一条命令。

    输入可以是：
      · 一个 .bin 文件（条目解码后的载荷）
      · 一个逻辑路径 / fid（先经索引定点提取，再导出）
    """
    import importlib
    te = importlib.import_module("toolkit_core.table_export")

    src = args.source
    p = Path(src)

    if p.is_file():
        # ① 存在的文件：直接读载荷
        payload = p.read_bytes()
        origin = str(p)
        if not payload:
            print(f"[export] 输入文件是空的：{p}", file=sys.stderr)
            print("[export] 空文件里没有任何表体可解。请检查是不是传错了路径。", file=sys.stderr)
            return 6
    else:
        # ② 不是文件 ⇒ 当成逻辑路径 / fid，走索引定点提取
        #    ★ 整段包裹：extract_path 对未命中会抛 KeyError，之前没接住 ⇒ 裸 Traceback
        import tempfile
        try:
            tmp = Path(tempfile.gettempdir()) / "_export_entry.bin"
            if tmp.exists():
                tmp.unlink()
            with _open(args) as index:
                index.extract_path(src, tmp, overwrite=True)
            payload = tmp.read_bytes()
        except KeyError as exc:
            print(f"[export] 既不是存在的文件，索引里也查不到：{src}", file=sys.stderr)
            print(f"[export]   （{exc}）", file=sys.stderr)
            print("[export] 提示：输入可以是 .bin 条目载荷的路径，或索引里存在的逻辑路径 / fid。",
                  file=sys.stderr)
            return 6
        except IndexNotReady as exc:
            print(f"[export] 索引不可用：{exc}", file=sys.stderr)
            return 3
        except Exception as exc:  # noqa: BLE001 - 如实报错，不丢栈
            print(f"[export] 提取失败（{type(exc).__name__}）：{exc}", file=sys.stderr)
            return 6
        origin = f"{src}（经索引提取）"

    rep = te.export_entry_bytes(payload, family=args.family,
                                resolve_jumps=not args.no_jump)
    print(f"[export] {origin}")
    print(f"[export] {rep.get('body')}")
    print(f"[export] {te.human_summary(rep)}")
    if not rep.get("family"):
        for x in rep.get("tried", []):
            print(f"[export]   试过 {x.get('family')}：{x.get('error') or '无行'}")
        print("[export] 说明：这张表当前解不出行。上面逐族列了失败原因，没有静默跳过。",
              file=sys.stderr)
        return 6
    out = te.write_table(rep["rows"], args.out, args.format)
    n = len(rep["rows"])
    if args.json:
        _dump({"origin": origin, "out": str(out), "family": rep["family"],
               "rows": n, "unbound": len(rep.get("unbound") or []),
               "tried": rep.get("tried")}, args.json)
    print(f"[export] 已写 {out}（{n} 行，格式 {args.format}）")
    return 0


def cmd_index_status(args) -> int:
    try:
        with _open(args) as index:
            report = index.status(check_sources=not args.no_source_check,
                                  deep=getattr(args, "deep", False))
    except IndexNotReady as exc:
        print(str(exc), file=sys.stderr); return 3
    _dump(report, args.json, sidecar=_sync(args, "status"))
    if report["quick_check"] != "ok": return 4
    return 5 if report["stale"] is True else 0


def cmd_find(args) -> int:
    try:
        with _open(args) as index:
            result = index.find(args.path, variants=args.variants, deep=args.deep_variants)
    except (IndexNotReady, ValueError) as exc:
        print(str(exc), file=sys.stderr); return 3
    _dump(result.as_dict(), args.json)
    return 0 if result.hits else 5


def cmd_extract(args) -> int:
    try:
        with _open(args) as index:
            report = index.extract_path(
                args.path, args.output, container=args.container, row=args.row,
                variants=args.variants, deep=args.deep_variants,
                decode=not args.raw, overwrite=args.force)
    except AmbiguousMatch as exc:
        print(str(exc), file=sys.stderr); return 6
    except (IndexNotReady, KeyError, FileNotFoundError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr); return 5
    _dump(report, args.json)
    return 0


def cmd_verify(args) -> int:
    # ★ 只断言「语义」：fid 命中 + 路径匹配。
    #   不断言行号 —— 行号是解析实现的副产品，随容器集变化；
    #   旧版把 res.npk 的行号当 ground truth 写死，索引从 313 容器重建为
    #   60 容器后必然位移（而 fid 仍全中），于是每次 verify 都误报 pass=False。
    #   行号保留在 observed_rows 里作记录，供人核对。
    expected = [
        r"common\env_map\qiangpi.cube",
        r"common\env_map\car_studio01.cube",
        r"common\env_map\fashion_qiangpi.cube",
    ]
    checks = []
    try:
        with _open(args) as index:
            status = index.status(check_sources=not args.no_source_check)
            for path in expected:
                fid = f"{path_fid(path):016X}"
                result = index.find(path)
                good = [h for h in result.hits
                        if h.fid_hex == fid and (h.matched_path or "") == path]
                checks.append({"path": path, "expected_fid": fid,
                               "pass": bool(good),
                               "observed_rows": [h.row for h in good],
                               "hits": [h.as_dict() for h in result.hits]})
    except IndexNotReady as exc:
        print(str(exc), file=sys.stderr); return 3
    report = {"pass": status["quick_check"] == "ok" and all(x["pass"] for x in checks),
              "status": status, "checks": checks,
              "note": "三条 ground truth 只验证路径键/索引链；不替代资产语义验收。"}
    _dump(report, args.json, sidecar=_sync(args, "verify"))
    return 0 if report["pass"] else 4


def cmd_glb(args) -> int:
    """一个或多个 .mesh → 单个 GLB（世界坐标拼接 + 自检报告）。

    实现全部在 toolkit_core.la_glb（本函数只做参数转交，避免"CLI 里再抄一套逻辑"）。
    局部导入：numpy/PIL 由 la_glb 内部惰性加载，index/find/extract/verify 的依赖面不变。
    """
    try:
        from toolkit_core import la_glb
    except ImportError as exc:                      # 模块缺失/坏掉时明确报错，不静默
        print("glb 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    code, _report = la_glb.run(args.meshes, mat=args.mat, tex=args.tex, out=args.out,
                               force=args.force, json_path=args.json)
    return int(code)


# ═══════════════════════════════════════════════════════════════════════════
# ② 图文音频渲染线：把散在 02_图文音频渲染/ 的能力接进统一 CLI
#   · CLI 只做参数转交，实现留在原模块（避免"CLI 里再抄一套逻辑"）
#   · 惰性导入：不碰 numpy/PIL 的命令不受影响
# ═══════════════════════════════════════════════════════════════════════════

def _line2_dir() -> Path:
    """②线脚本目录（皮肤链与渲染）。"""
    return PROJECT_ROOT / "01_工具" / "工具库" / "02_图文音频渲染" / "皮肤链与渲染"


def _load_line2(module_name: str):
    """惰性导入 ②线模块（它们是散脚本、非包，只能按路径进 sys.path）。"""
    d = str(_line2_dir())
    if d not in sys.path:
        sys.path.insert(0, d)
    import importlib
    return importlib.import_module(module_name)


def _collect_inputs(targets) -> list:
    """把「文件 / 目录 / glob」统一收成文件列表。"""
    import glob as _glob
    out = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            out += sorted(q for q in p.rglob("*") if q.is_file())
        elif any(ch in str(t) for ch in "*?["):
            out += sorted(Path(q) for q in _glob.glob(str(t), recursive=True) if Path(q).is_file())
        elif p.is_file():
            out.append(p)
    return out


def cmd_tex(args) -> int:
    """[②-2] 贴图 → PNG。只走 dds_rgba_canonical 规范入口（R↔B 唯一修正点）。"""
    exts = {("." + e.lower().lstrip(".")) for e in args.ext}
    files = [p for p in _collect_inputs(args.target) if p.suffix.lower() in exts]
    if not files:
        print("tex：没找到输入（%s）。给文件、目录或 glob。" % "/".join(sorted(exts)),
              file=sys.stderr)
        return 2
    try:
        CAN = _load_line2("dds_rgba_canonical")
        import numpy as np
        from PIL import Image
    except Exception as exc:
        print("tex 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5

    outdir = Path(args.out) if args.out else (PROJECT_ROOT / "03_执行" / "90_临时" / "tex_out")
    outdir.mkdir(parents=True, exist_ok=True)
    rows, ok, fail = [], 0, 0
    for src in files:
        dst = outdir / (src.stem + ".png")
        if dst.exists() and not args.force:
            rows.append({"src": str(src), "png": str(dst), "skipped": "已存在（--force 覆盖）"})
            continue
        try:
            if src.suffix.lower() == ".ktx":
                ktx = _load_line2("ktx_to_png")
                fn = getattr(ktx, "ktx_to_png", None) or getattr(ktx, "convert", None)
                if fn is None:
                    raise RuntimeError("ktx_to_png 模块没有可用的转换函数")
                fn(str(src), str(dst))
                rows.append({"src": str(src), "png": str(dst), "fmt": "KTX"})
            else:
                u8, prov = CAN.decode_dds_rgba_u8(str(src), verify_oiio=not args.no_verify)
                Image.fromarray(u8, "RGBA").save(dst)
                rows.append({"src": str(src), "png": str(dst), "fmt": prov.get("fmt"),
                             "size": [prov.get("width"), prov.get("height")],
                             "swizzle": prov.get("applied_swizzle"),
                             "pixel_sha256": prov.get("canonical_pixel_sha256")})
            ok += 1
        except Exception as exc:
            fail += 1
            rows.append({"src": str(src), "error": "%s: %s" % (type(exc).__name__, exc)})

    report = {"kind": "tex", "segment": "②-2", "out": str(outdir),
              "total": len(files), "ok": ok, "fail": fail, "items": rows}
    _dump(report, args.json)
    if not args.quiet:
        print("tex：%d 张 → %s（成功 %d / 失败 %d）" % (len(files), outdir, ok, fail))
    return 1 if fail and args.strict else 0


def cmd_sheet(args) -> int:
    """[②-1] 装配帧 .c159 → 材质/部件表（配对规则见 C159_PARAM_PAIRING.md）。"""
    try:
        v4 = _load_line2("c159_pair_v4")
    except Exception as exc:
        print("sheet 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    files = [p for p in _collect_inputs(args.mtl) if p.suffix.lower() == ".c159"]
    if not files:
        print("sheet：没找到 .c159 输入", file=sys.stderr)
        return 2
    outdir = Path(args.out) if args.out else (PROJECT_ROOT / "03_执行" / "90_临时" / "sheet_out")
    outdir.mkdir(parents=True, exist_ok=True)
    bind = str(args.bind) if args.bind else None
    rows, ok, fail = [], 0, 0
    for src in files:
        try:
            res = v4.analyze_v4(str(src), bind)
            dst = outdir / (src.stem + ".sheet.json")
            dst.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str),
                           encoding="utf-8")
            rows.append({"src": str(src), "out": str(dst),
                         "keys": sorted(res.keys()) if isinstance(res, dict) else type(res).__name__})
            ok += 1
        except Exception as exc:
            fail += 1
            rows.append({"src": str(src), "error": "%s: %s" % (type(exc).__name__, exc)})
    report = {"kind": "sheet", "segment": "②-1", "out": str(outdir),
              "total": len(files), "ok": ok, "fail": fail, "items": rows}
    _dump(report, args.json)
    if not args.quiet:
        print("sheet：%d 个装配帧 → %s（成功 %d / 失败 %d）" % (len(files), outdir, ok, fail))
    return 1 if fail and args.strict else 0


def cmd_audio(args) -> int:
    """[②-2] 音效轨道 .sfx → 帧表 JSON（节点树 / 色帧 / 缩放帧 / 绑定贴图）。"""
    try:
        st = _load_line2("parse_sfx_tracks")
    except Exception as exc:
        print("audio 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    files = [p for p in _collect_inputs(args.src)
             if p.suffix.lower() in {("." + e.lower().lstrip(".")) for e in args.ext}]
    if not files:
        print("audio：没找到 .sfx 输入", file=sys.stderr)
        return 2
    outdir = Path(args.out) if args.out else (PROJECT_ROOT / "03_执行" / "90_临时" / "audio_out")
    outdir.mkdir(parents=True, exist_ok=True)
    rows, ok, fail = [], 0, 0
    for src in files:
        try:
            dst = outdir / (src.stem + ".tracks.json")
            st.main(str(src), str(dst))
            rows.append({"src": str(src), "out": str(dst)})
            ok += 1
        except Exception as exc:
            fail += 1
            rows.append({"src": str(src), "error": "%s: %s" % (type(exc).__name__, exc)})
    report = {"kind": "audio", "segment": "②-2", "out": str(outdir),
              "total": len(files), "ok": ok, "fail": fail, "items": rows}
    _dump(report, args.json)
    if not args.quiet:
        print("audio：%d 个轨道文件 → %s（成功 %d / 失败 %d）" % (len(files), outdir, ok, fail))
    return 1 if fail and args.strict else 0


def cmd_render(args) -> int:
    """[②-3] 材质分层出图（非交付面 PNG + layers_trace.json）。

    render_material_layers 是位置参数式 main()（mesh tex_dir out_dir + 若干开关），
    这里只做参数转交，不改它的逻辑。
    """
    try:
        mod = _load_line2("render_material_layers")
    except Exception as exc:
        print("render 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    out_dir = Path(args.out) if args.out else (PROJECT_ROOT / "03_执行" / "90_临时" / "render_out")
    argv = [str(args.mesh), str(args.tex_dir), str(out_dir)]
    if args.materials:
        argv += ["--materials", str(args.materials)]
    if args.polarity:
        argv += ["--polarity", args.polarity]
    if args.dual:
        argv += ["--dual"]
    if args.dual_sep is not None:
        argv += ["--dual-sep", str(args.dual_sep)]
    # ★ 2026-09-28 加：把 tex（②-2）的行号命名产物接进 render（②-3）。
    for _spec in (args.tex_map or []):
        argv += ["--tex-map", _spec]
    if args.input_manifest:
        argv += ["--input-manifest", str(args.input_manifest)]

    saved = sys.argv
    sys.argv = ["render_material_layers.py"] + argv
    # ★ 2026-09-28：渲染器自己会往 stdout 打进度（LAYERS DONE / 8 个层名）。
    #   只要调用方要了 JSON（--json -），stdout 就必须【只有 JSON】能被 json.loads，
    #   否则「报告 JSON 打 stdout」这条契约是假的（实测 json.loads 直接炸在 char 0）。
    #   有 JSON 出口时把被包装模块的 stdout 转到 stderr。
    _sink = sys.stderr if args.json else None
    try:
        if _sink is not None:
            with contextlib.redirect_stdout(_sink):
                mod.main()
        else:
            mod.main()
    except SystemExit as exc:              # 渲染器的 fail-closed（缺槽位/极性非法）⇒ 用法错
        if exc.code not in (0, None):
            print("render 参数/输入不满足：%s" % (exc.code,), file=sys.stderr)
            return 2
    except Exception as exc:
        print("render 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    finally:
        sys.argv = saved

    trace = out_dir / "layers_trace.json"
    # ★ 报告里带上【产物清单】：下游（看板/验收/再处理）原来只能自己去 glob 输出目录。
    outputs = sorted(str(p) for p in out_dir.glob("*.png")) if out_dir.is_dir() else []
    report = {"kind": "render", "segment": "②-3", "out": str(out_dir),
              "mesh": str(args.mesh), "tex_dir": str(args.tex_dir),
              "materials": str(args.materials) if args.materials else None,
              "polarity": args.polarity, "dual": bool(args.dual),
              "tex_map": list(args.tex_map or []),
              "input_manifest": str(args.input_manifest) if args.input_manifest else None,
              "outputs": outputs, "output_count": len(outputs),
              "trace": str(trace) if trace.exists() else None}
    _dump(report, args.json)
    if not args.quiet:
        print("render：%s → %s（%d 张 PNG）" % (args.mesh, out_dir, len(outputs)))
    return 0 if outputs else 1


def cmd_resolver(args) -> int:
    """[①-1] 资源物理桥定位器（原 resource_resolver._main 的独立入口，收编进来）。

    原实现自带一份 argparse（locate/tree/dump/bridge-gpk），违反「命令定义只有一份」，
    且不在统一 CLI 里 ⇒ 能力够不着。这里只做参数转交。
    """
    try:
        from toolkit_core.resource_resolver import ResourceResolver
    except Exception as exc:
        print("resolver 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    r = ResourceResolver(args.res).build_index()
    if not args.quiet:
        print("[索引] %s" % r.stats())
    if args.resolver_command == "locate":
        e = r.locate(args.path)
        _dump(e.__dict__ if e else None, args.json)
    elif args.resolver_command == "tree":
        _dump(r.resolve_tree(args.path, args.depth), args.json)
    elif args.resolver_command == "dump":
        data = r.read_path(args.path)
        if data is None:
            print("路径未定位到：%s" % args.path, file=sys.stderr)
            return 1
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        if not args.quiet:
            print("已保存 %d B -> %s" % (len(data), out))
        _dump({"path": args.path, "out": str(out), "bytes": len(data)}, args.json)
    elif args.resolver_command == "bridge-gpk":
        rep = r.bridge_gpk(args.gpk)
        _dump(rep, args.json)
        if not args.quiet:
            print("%s: %s/%s 覆盖 %.1f%%" % (rep["gpk"], rep["bridged"], rep["entries"],
                                             rep["coverage"] * 100))
    return 0


def cmd_declared(args) -> int:
    """[②-2] 声明文件（.c159/.mtg/.sfx…）里的资产路径 → 容器 HIT/MISS 矩阵。

    ★ 为什么收编它：渲染线的第一环是「这块材质声明了哪几张图」，而 .mtg 里写的是
      `weapon\\skin\\skin_1003_010\\textures\\skin_1003_010_1001a.tga` 这类【逻辑路径】，
      容器里只有哈希。判断「声明了却没落地」必须走「候选名 → fid → 容器表查行」，
      不能靠字符串搜索。这个能力（resolve_declared_paths.py）早就写好了，但自带一份
      argparse、没进统一 CLI —— 实测要判断皮肤贴图是否在产物里时，只能手写脚本重造。
      这里只做参数转交，实现留在原模块（与 resolver / texscan 同一收编方式）。

    退出码沿用原模块：0 跑完（MISS 是数据结论不是故障）· 1 用法 · 2 输入读不到 · 4 索引不可用
    """
    try:
        mod = _load_line2("resolve_declared_paths")
    except Exception as exc:
        print("declared 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    argv = []
    for t in (args.inputs or []):
        argv.append(str(t))
    argv += ["--res-root", str(args.res_root)]
    if args.fpk_index:
        argv += ["--fpk-index", str(args.fpk_index)]
    if args.index:
        argv += ["--index", str(args.index)]
    for e in (args.ext or []):
        argv += ["--ext", e]
    for flag, on in (("--variants", args.variants), ("--deep-variants", args.deep_variants),
                     ("--dump-strings", args.dump_strings), ("--no-detail", args.no_detail),
                     ("--quiet", args.quiet)):
        if on:
            argv.append(flag)
    if args.json:
        argv += ["--json", str(args.json)]
    try:
        return int(mod.main(argv) or 0)
    except SystemExit as exc:              # 原模块 argparse 的用法错
        return 2 if exc.code not in (0, None) else 0
    except Exception as exc:
        print("declared 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1


def cmd_texscan(args) -> int:
    """[②-2] 匿名 GPK 纹理颜色筛选 / 未上线候选（原 texture_extractor._main 收编）。"""
    try:
        from toolkit_core.texture_extractor import scan_dir
    except Exception as exc:
        print("texscan 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    scan_dir(args.unpacked_dir, args.out, args.res, args.color,
             only_unique=not args.all, min_side=args.min_side, top=args.top)
    return 0


def cmd_delta(args) -> int:
    """[H-1] 热更增量取证：只比服务端版本清单，不碰任何本地客户端文件。

    默认只比 release(正式服) vs playertest(测试服) —— 这个差就是「测试服提前拿到的内容」。
    """
    try:
        from toolkit_core import patch_delta as PD
    except Exception as exc:
        print("delta 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5

    _cache_arg = getattr(args, "cache", None)
    cache = Path(_cache_arg) if _cache_arg else (PROJECT_ROOT / "03_执行" / "10_索引" / "patch_manifests")
    sub = args.delta_command

    # ── 官方 CDN 包清单 pkg_N.pi（H-1 扩展；≈18 MB/版本，替代下 42 GB 大包）──
    if sub == "pkg":
        try:
            from toolkit_core import patch_pkg as PP
        except Exception as exc:
            print("patch_pkg 不可用：%r" % (exc,), file=sys.stderr)
            return 5
        psub = args.pkg_command

        if psub == "fetch":
            try:
                rep = PP.fetch(args.entry, args.out, timeout=args.timeout,
                               only=([int(x) for x in args.only.split(",")] if args.only else None),
                               quiet=args.quiet)
            except Exception as exc:
                print("delta pkg fetch 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
                return 1
            rep = {"kind": "delta", "action": "pkg_fetch", **rep}
            _dump(rep, args.json)
            if not args.quiet:
                print("  CDN 目录 %s" % rep["cdn_dir"])
                print("  下到本地 %s" % rep["out_dir"])
            return 0

        if psub == "info":
            try:
                doc = PD.fetch(args.entry, timeout=args.timeout)
                cdn = PP.cdn_dir_of(doc)
                lst = PP.fetch_pkg_lst(cdn, timeout=args.timeout)
            except Exception as exc:
                print("delta pkg info 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
                return 1
            rep = {"kind": "delta", "action": "pkg_info", "entry": args.entry,
                   "version": doc.get("version"), "cdn_dir": cdn,
                   "cloud_dir_name": doc.get("cloud_dir_name"),
                   "bc7_only": doc.get("bc7_only"), "use_overlay": doc.get("use_overlay"),
                   "zstd_dict": doc.get("zstd_dict"), "pkg_lst": lst}
            _dump(rep, args.json)
            if not args.quiet:
                print("  入口      %s" % args.entry)
                print("  version   %s" % rep["version"])
                print("  CDN 目录  %s" % cdn)
                print("  bc7_only  %s    use_overlay %s" % (rep["bc7_only"], rep["use_overlay"]))
                print("  包顺序    %s" % lst)
            return 0

        if psub == "owner":
            # ★ H-3 新版：用官方 pkg_N.pi 直接回答「fid 属于哪个官方包」
            try:
                cdn = Path(args.pkg_dir)
                fids = list(args.fid or [])
                if not args.fid:
                    print("delta pkg owner 需要至少一个 fid", file=sys.stderr)
                    return 2
                own = PP.build_fid_owner(cdn)
                got = PP.owner_of(cdn, fids, cache=own)
            except Exception as exc:
                print("delta pkg owner 失败：%s: %s" % (type(exc).__name__, exc),
                      file=sys.stderr)
                return 1
            rep = {"kind": "delta", "action": "pkg_owner", "dir": str(cdn),
                   "result": got}
            _dump(rep, args.json)
            if not args.quiet:
                for f, o in got.items():
                    print("  %s  →  %s" % (f, ("%s 包内第 %d 条" % (o["pkg"], o["index"]))
                                           if o else "★ 不属于任何官方包"))
            return 0

        if psub == "diff":
            try:
                rep = PP.diff(args.a, args.b)
            except Exception as exc:
                print("delta pkg diff 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
                return 1
            out = {"kind": "delta", "action": "pkg_diff",
                   "a_dir": rep["a_dir"], "b_dir": rep["b_dir"],
                   "a_total": rep["a_total"], "b_total": rep["b_total"],
                   "added_n": len(rep["added"]), "removed_n": len(rep["removed"]),
                   "common_n": len(rep["common"]),
                   "added": ["%016X" % v for v in sorted(rep["added"])],
                   "removed": ["%016X" % v for v in sorted(rep["removed"])]}
            _dump(out, args.json)
            if not args.quiet:
                print(PP.render(rep, limit=args.limit))
            if args.out:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
                if not args.quiet:
                    print("  完整报告 → %s" % args.out)
            return 0

        print("未知 pkg 子命令 %r" % psub, file=sys.stderr)
        return 2

    if sub == "fetch":
        want = args.entry or list(PD.ENTRIES)
        got = PD.fetch_all(want, cache_dir=cache)
        rows = []
        for e, doc in got.items():
            if "_error" in doc:
                rows.append({"entry": e, "error": doc["_error"]})
                continue
            keys = PD._pick_file_keys(doc)
            rows.append({"entry": e, "version": doc.get("version"),
                         "svn_branch": doc.get("svn_branch"),
                         "revision": doc.get("revision"),
                         "files_main": keys["main"][0] if keys["main"] else None,
                         "files_main_n": len(keys["main"][1]) if keys["main"] else 0,
                         "files_ext": keys["ext"][0] if keys["ext"] else None,
                         "files_ext_n": len(keys["ext"][1]) if keys["ext"] else 0})
        rep = {"kind": "delta", "action": "fetch", "cache": str(cache), "entries": rows}
        _dump(rep, args.json)
        if not args.quiet:
            for r in rows:
                if "error" in r:
                    print("  ✗ %-20s %s" % (r["entry"], r["error"][:60]))
                else:
                    print("  ✓ %-20s %-34s %s(%d) · %s(%d)" % (
                        r["entry"], r["version"], r["files_main"], r["files_main_n"],
                        r["files_ext"], r["files_ext_n"]))
        return 0

    # ── 热更 overlay 全量定位（H-2+）：客户端状态 → 下载 → 解包 → 定位 ──
    if sub == "overlay":
        try:
            from toolkit_core import patch_overlay as PO
        except Exception as exc:
            print("patch_overlay 不可用：%r" % (exc,), file=sys.stderr)
            return 5
        osub = args.overlay_command

        if osub == "list":
            try:
                rep = PO.selfcheck(args.client_root, quiet=args.quiet)
            except Exception as exc:
                print("delta overlay list 失败：%s: %s" % (type(exc).__name__, exc),
                      file=sys.stderr)
                return 1
            _dump({"kind": "delta", "action": "overlay_list", **rep}, args.json)
            return 0

        if osub == "fetch":
            try:
                st = PO.read_client_state(args.client_root)
                ol = PO.overlay_list(st)
                cd = PO.cdn_dir(st)
                rep = PO.fetch(cd, [p["name"] for p in ol["packages"]],
                               args.out, timeout=args.timeout, quiet=args.quiet)
            except Exception as exc:
                print("delta overlay fetch 失败：%s: %s" % (type(exc).__name__, exc),
                      file=sys.stderr)
                return 1
            _dump({"kind": "delta", "action": "overlay_fetch", **rep}, args.json)
            return 0

        if osub == "locate":
            import hashlib
            try:
                from toolkit_core import content_index as CI
            except Exception as exc:
                print("content_index 不可用：%r" % (exc,), file=sys.stderr)
                return 5
            d = Path(args.dir)
            if not d.is_dir():
                print("delta overlay locate：目录不存在 %s" % d, file=sys.stderr)
                return 6
            rows = []
            total_blk = total_hit = 0
            for p in sorted(d.glob("*.npk")):
                u = PO.unpack_frames(p.read_bytes())
                if not u["n_decoded"]:
                    rows.append({"pkg": p.name, "frames": u["n_frames"],
                                 "decoded": 0, "blocks": 0, "hits": 0})
                    continue
                md5s = [hashlib.md5(b).hexdigest() for b in u["pieces"]]
                hit = CI.lookup_many(str(PROJECT_ROOT / "03_执行" / "10_索引" / "indexes"
                                         / "lifeafter_files.sqlite3"), md5s)
                n = sum(1 for m in md5s if m in hit)
                total_blk += len(md5s)
                total_hit += n
                conts = {}
                for m, lst in hit.items():
                    for c, ri, sz in lst:
                        conts.setdefault(Path(c.replace("\\", "/")).stem, 0)
                        conts[Path(c.replace("\\", "/")).stem] += 1
                rows.append({"pkg": p.name, "frames": u["n_frames"],
                             "decoded": u["n_decoded"], "blocks": len(md5s),
                             "hits": n, "containers": conts})
            rep = {"kind": "delta", "action": "overlay_locate", "dir": str(d),
                   "total_blocks": total_blk, "total_hits": total_hit,
                   "by_pkg": rows}
            _dump(rep, args.json)
            if not args.quiet:
                print("  ★ 共 %d 块，命中 %d（%.1f%%）"
                      % (total_blk, total_hit,
                         100.0 * total_hit / max(1, total_blk)))
                for r in rows:
                    c = r.get("containers") or {}
                    print("    %-50s 块%-4d 命中%-4d %s"
                          % (r["pkg"][:50], r["blocks"], r["hits"], c or ""))
            if args.out:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
            return 0

        print("未知 overlay 子命令 %r" % osub, file=sys.stderr)
        return 2

    # diff / families 都要两份清单
    a_name, b_name = (args.pair or list(PD.DEFAULT_PAIR))[:2]
    docs = {}
    for name in (a_name, b_name):
        d = PD.load_cached(cache, name)
        if d is None:
            try:
                print("  本地无缓存，拉取 %s …" % name, file=sys.stderr)
                d = PD.fetch(name)
                cache.mkdir(parents=True, exist_ok=True)
                (cache / ("%s.json" % name)).write_text(
                    json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            except Exception as exc:
                print("delta：拉取 %s 失败：%s: %s" % (name, type(exc).__name__, exc),
                      file=sys.stderr)
                return 5
        docs[name] = d

    try:
        rep = PD.diff(docs[a_name], docs[b_name], keys=args.keys)
    except ValueError as exc:
        print("delta diff 失败：%s" % exc, file=sys.stderr)
        return 1

    if sub == "families":
        rep = {"kind": "delta", "action": "families",
               "a": rep["a"], "b": rep["b"],
               "added_by_family": rep["added_by_family"],
               "changed_by_family": rep["changed_by_family"],
               "totals": rep["totals"]}
        _dump(rep, args.json)
        if not args.quiet:
            print(PD.render({"a": rep["a"], "b": rep["b"], "added": [], "removed": [],
                             "changed": [], "same": rep["totals"]["same"],
                             "added_by_family": rep["added_by_family"],
                             "changed_by_family": rep["changed_by_family"],
                             "totals": rep["totals"]}))
        return 0

    _dump(rep, args.json)
    if not args.quiet:
        print(PD.render(rep, limit=args.limit))
    out = args.out
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        if not args.quiet:
            print("  完整报告 → %s" % out)
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# 带 H · 散文件层（客户端单独下载的文件 = Documents/res/*.idx + *<pkg>.wpk）
#   机制依据：NeoX 的文件系统「优先读散文件，没找到才读资源包」
#     ⇒ 散文件层里就是【客户端额外取下来的那些文件】。
#   scan  = 解密（1DPW 容器 → 明文 DDS 等；★ 已通用化，扫全部家族）
#   match = 内容 MD5 撞本地索引 ⇒ 不靠名字就能定位「哪个容器哪一行」
# ═══════════════════════════════════════════════════════════════════════════

LOOSE_ALLOWED_ROOTS = (r"e:\mrzh",)
DEFAULT_LOOSE_ROOT = Path(r"E:\mrzh\Documents\res")


def _under(root: Path, allowed) -> bool:
    """路径是否落在允许的根下（不依赖 os：统一分隔符后按前缀比）。"""
    s = str(root).replace("/", "\\").lower().rstrip("\\")
    for a in allowed:
        a = a.lower().rstrip("\\")
        if s == a or s.startswith(a + "\\"):
            return True
    return False


def _load_container_fmt(module_name: str):
    """惰性导入 ①线容器格式模块（散脚本，按路径进 sys.path）。"""
    d = str(PROJECT_ROOT / "01_工具" / "工具库" / "01_解码定位复原" / "容器格式")
    if d not in sys.path:
        sys.path.insert(0, d)
    import importlib
    return importlib.import_module(module_name)


def _pkg_fids(d: Path):
    """读一个目录下所有 pkg_*.pi → fid 集合（★ 统一转成 16 位大写十六进制字符串，
    与索引表 `entries.fid_hex` 的口径一致；直接拿 int 去比对会全不中）。"""
    import struct
    s = set()
    for p in sorted(Path(d).glob("pkg_*.pi")):
        b = p.read_bytes()
        if len(b) < 8:
            continue
        n = int.from_bytes(b[:4], "little")
        if n <= 0 or 8 + n * 8 > len(b):
            continue
        s.update("%016X" % v for v in struct.unpack("<%dQ" % n, b[8:8 + n * 8]))
    return s


_CN_COMMON = set("的一是不了在人有我他这个上们来到时大地为子中你说生国年着就那和要"
                 "她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没")


def _cn_strings(blob: bytes) -> list:
    """从 marshal 明文里抽中文串。

    ★ 判据：UTF-8 三字节序列 + 常用字占比 ≥ 0.5。
      只用 `[\\xe4-\\xe9]{3}` 会命中一堆字节错位假中文（实测「歳汥瑥湯」那种）。
    """
    out = []
    for m in re.finditer(rb"[\xe4-\xe9][\x80-\xbf]{2}(?:[\xe4-\xe9][\x80-\xbf]{2}|[\x20-\x7e])*",
                         blob):
        try:
            s = m.group().decode("utf-8")
        except UnicodeDecodeError:
            continue
        if len(s) < 2:
            continue
        c = sum(1 for ch in s if ch in _CN_COMMON)
        if c and c / len(s) >= 0.5:
            out.append(s)
    return out


def _fill_text_tables(b, out: Path, added_f: set, dict_path, args) -> None:
    """把文字表落进 02_文字表 —— ★ 必须给实质内容，不能只写「未涉及」。

    两块：
      ① 本次热更涉及的文字表：从新增行里筛 `com\\cdata\\` 且 `_chs.py` 的 —— 真实回答「本次动没动表」
      ② 全量文字表汇总：复用已有的抽取产物（`tables chs` / 配置表攻关的导出）
    """
    import shutil as _sh
    td = out / HB.D_TEXT
    td.mkdir(parents=True, exist_ok=True)

    # ① 本次热更涉及的文字表
    #   ★★★ 判据必须【两条合起来】：
    #     (a) pkg_N.pi 物理布局 diff 里新增的 —— 覆盖普通容器（ui/gres/…）
    #     (b) ★ script overlay 清单里的 —— script 容器按【模块名】索引，
    #         它的表变更【只出现在 overlay 里】，用 pkg_N.pi 判会得出「0 个」的错结论
    #   （实测 2026-09-28：只用 (a) → 0 个；加上 (b) → 102 个 _chs.py 真的变了）
    hot_meta = {}
    if added_f:
        db = sqlite3.connect("file:%s?mode=ro" % str(DEFAULT_DB).replace("\\", "/"), uri=True)
        for f, c, rw in db.execute(
                "SELECT fid_hex, container, row_index FROM entries"):
            if f in added_f:
                nm = b.names.get(f, "")
                if nm and "_chs." in nm.lower():
                    hot_meta[nm] = {"来源": "pkg_N.pi 新增", "fid": f,
                                    "容器": c, "行": rw}
    # (b) script overlay —— ★ 必须用 npk_decode_entry 解块，raw 是加密的
    try:
        pkg_dir = out / "pkgs"
        for pk in sorted(pkg_dir.glob("script*.npk")):
            rr = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "ovl", "entries",
                 str(pk), "--limit", "5000"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1])))
            by_fid = {}
            for m in re.finditer(
                    r"fid=([0-9A-F]+)\s+off=(\d+)\s+packed=(\d+)\s+decoded=(\d+)\s+flag=(\d+)",
                    rr.stdout):
                nm = b.names.get(m.group(1), "")
                if nm and "_chs." in nm.lower():
                    by_fid[m.group(1)] = {
                        "off": int(m.group(2)), "packed": int(m.group(3)),
                        "decoded": int(m.group(4)), "flag": int(m.group(5)), "name": nm}
            if not by_fid:
                continue
            # ★ 解块：flag=0 → AES-ECB 解密 + (i64@0==1 ? 偏移18起 zlib)；flag=2 → LZ4
            #   la_unpack_core 在 01_解码定位复原/解包与扫描/ 下（不在 00_共享核心）
            try:
                _root = Path(__file__).resolve().parents[2]
                _p = _root / "01_解码定位复原" / "解包与扫描"
                if str(_p) not in sys.path:
                    sys.path.insert(0, str(_p))
                from la_unpack_core import npk_decode_entry
            except Exception as exc:
                if not getattr(_fill_text_tables, "_warned", False):
                    _fill_text_tables._warned = True
                    print("  ⚠ 解块器不可用（文字表只能给表名）：%s" % exc)
                npk_decode_entry = None
            data = pk.read_bytes()
            for fid, e in by_fid.items():
                if fid in hot_meta:
                    continue
                raw = data[e["off"]: e["off"] + e["packed"]]
                txt = []
                if npk_decode_entry is not None:
                    try:
                        dec = npk_decode_entry(raw, e["decoded"], e["flag"])
                        txt = _cn_strings(dec)
                    except Exception:
                        pass
                hot_meta[e["name"]] = {
                    "来源": "script overlay", "fid": fid,
                    "热更版明文长度": e["decoded"], "flag": e["flag"],
                    "变更文案": txt}
    except Exception as exc:
        print("  ⚠ 文字表（overlay 路）扫描失败：%s" % exc)
    hot = sorted(hot_meta)
    _hotinfo = hot_meta

    lines = ["# 本次热更涉及的文字表", "",
             "结论：**%d 个** `_chs.py` 文字表有变化" % len(hot), "",
             "> ★ 判据 = `pkg_N.pi` 物理布局 diff ∪ `script overlay` 清单。",
             "> 只用前者会漏光（script 容器按模块名索引，变更只在 overlay 里）。",
             ""]
    if hot:
        lines += ["| 表 | 来源 |", "|---|---|"]
        for x in hot:
            lines.append("| `%s` | %s |" % (x, _hotinfo.get(x, {}).get("来源", "")))
    else:
        lines += ["本次热更确实未涉及 `_chs.py`。"]
    (td / "本次热更涉及.md").write_text("\n".join(lines), encoding="utf-8")
    (td / "本次变更文字表_表名清单.txt").write_text("\n".join(hot), encoding="utf-8")

    # ★ 变更文案（从 overlay 块解出来的真明文里抽）
    allcn = []
    detail = []
    for x in hot:
        cn = (hot_meta.get(x) or {}).get("变更文案") or []
        if cn:
            allcn += cn
            detail.append("## %s\n\n" % x)
            detail += ["- %s" % s for s in sorted(set(cn))]   # ★ 不截断（用户要求完整）
            detail.append("")
    u = sorted(set(allcn))
    (td / "变更文案_去重.txt").write_text("\n".join(u), encoding="utf-8")
    (td / "变更文案_分表.txt").write_text("\n".join(detail), encoding="utf-8")

    # ★★★ 结构化版（2026-09-28 新增）：把「表结构解析」产物的【文案 → 表名 + 字段名 + 行ID】
    #   接进来，让交付的每句文案都带归属，不再是裸句子。
    #   来源：`03_执行/30_分析/表结构解析_*/`（结构/<表>.rows.csv → 结构2/ → 产物/表文案归属.jsonl）
    #   ★ 拿不到结构时【只降级】，裸串版（上面两个文件）照旧交付，不抛异常。
    struct_note = ""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from toolkit_core import text_table_struct as TTS
        src = getattr(args, "struct_src", None) or os.environ.get("LA_STRUCT_SRC")
        ent, smeta = TTS.load(hot, struct_src=src)
        if ent:
            w = TTS.write(td, ent, smeta, bare_strings=u)
            struct_note = ("结构化 %d 条 ｜ 表 %d ｜ 去重 %d ｜ 裸串命中 %d/%d ｜ 来源 %s"
                           % (w["n"], w["n_tables"], w["n_unique"], w["hit"],
                              w["hit"] + w["miss"],
                              "、".join("%s=%d" % kv for kv in
                                        (smeta.get("来源分布") or {}).items())))
            if smeta.get("无结构产物表"):
                struct_note += " ｜ 无结构表 %d 个（该表保持裸串版）" % len(smeta["无结构产物表"])
            print("  02_文字表：" + struct_note)
        else:
            (td / TTS.IDX_NAME).write_text(json.dumps({
                "schema": "lifeafter-text-struct-v1",
                "状态": "未取到结构化产物，已回退裸串版",
                "来源根": smeta.get("来源根"),
                "无结构产物表": smeta.get("无结构产物表"),
                "说明": "本文件存在即表示结构化整合【尝试过】但无产出；"
                        "文案请看 变更文案_去重.txt / 变更文案_分表.txt（裸串版）。",
            }, ensure_ascii=False, indent=1), encoding="utf-8")
            print("  ⚠ 02_文字表：结构化产物不可用，已回退裸串版（来源根 %s）"
                  % (smeta.get("来源根") or "无"))
    except Exception as exc:                     # noqa: BLE001
        print("  ⚠ 02_文字表：结构化整合失败（%s: %s），继续交付裸串版"
              % (type(exc).__name__, str(exc)[:100]))
    txt_extra = ("\n## 结构化文案\n\n%s\n\n> `变更文案_结构化.tsv`：每句带【表名 + 字段名 + 行ID】；"
                 "`变更文案_结构化_索引.json` 记来源 / 每表条数 / 与裸串版交集。\n"
                 % (struct_note or "（未取到结构化产物，仅裸串版）"))
    lines.append(txt_extra)
    (td / "本次热更涉及.md").write_text("\n".join(lines), encoding="utf-8")

    print("  02_文字表：变更 %d 个表 ｜ 有文案 %d 个 ｜ 中文 %d 条 / 去重 %d"
          % (len(hot), sum(1 for x in hot if (hot_meta.get(x) or {}).get("变更文案")),
             len(allcn), len(u)))

    # ② 全量文字表汇总（复用已有产物）
    srcs = []
    explicit = getattr(args, "text_src", None)
    if explicit:
        srcs.append(Path(explicit))
    else:
        base = ANALYSIS_ROOT
        for name in ("配置表中文_20260928", "配置表加密攻关_20260928"):
            p = base / name
            if p.is_dir():
                srcs.append(p)
    copied, total = [], 0
    for s in srcs:
        for pat in ("配置表中文_全量.txt", "中文文案_全表_去重.txt",
                    "中文文案_优先_活动时装抽奖.txt", "配置表中文_分类.md",
                    "中文文案_全量.tsv", "抽取统计.json"):
            f = s / pat
            if f.is_file():
                dst = td / f.name
                if not dst.exists():
                    _sh.copy2(f, dst)
                copied.append(f.name)
                if pat.endswith(".txt") and "全量" in pat or "去重" in pat:
                    try:
                        total = max(total, sum(1 for _ in f.open(encoding="utf-8")))
                    except OSError:
                        pass
    (td / "索引.json").write_text(json.dumps({
        "schema": "lifeafter-text-tables-v1",
        "本次热更涉及表数": len(hot),
        "全量汇总来源": [str(s) for s in srcs],
        "已收录文件": copied,
        "全量文案条数(参考)": total,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  02_文字表：本次涉及 %d 个表 ｜ 全量汇总收录 %d 个文件" % (len(hot), len(copied)))

    # ③ ★ 时装热更表（用户口径：文字表产物固定带一份）
    #    走行级 diff —— 两个 script 包逐行比，只比真值字段。
    #    pre/post 包：优先用 --pre-pkg/--post-pkg，否则自动在 02_资料/源包/ 下找。
    _write_fashion_hotfix(td, out, hot, args)


# ★ 时装族表名（用户口径：文字表产物固定要一份时装热更表）
FASHION_TABLES = ["fashion_data_chs.py", "player_appear_data_chs.py",
                  "fashion_data.py", "player_appear_data.py"]


def _find_pkg_pair(args) -> tuple:
    """找热更前后的 script 包。命令行给了就用，否则自动找。"""
    pre = getattr(args, "pre_pkg", None)
    post = getattr(args, "post_pkg", None)
    if pre and post:
        return Path(pre), Path(post)
    root = Path(r"E:/la拆包项目/02_资料/源包")
    if not root.is_dir():
        return None, None
    pres = sorted(root.glob("pre_update_*/raw/script*.npk"))
    posts = sorted(root.glob("post_update_*/raw/script*.npk"))
    if pres and posts:
        return pres[-1], posts[-1]
    return None, None


def _write_fashion_hotfix(td: Path, out: Path, hot: list, args) -> None:
    """在 02_文字表 里落一份【时装热更表】。

    ★ 口径：文字表产物固定带这份。找得到 pre/post 包就真出表，
      找不到就写「未采集」并说明怎么补（**不拿旧产物冒充**）。
    """
    try:
        from toolkit_core import hotfix_rows as HR
    except Exception as exc:                                       # noqa: BLE001
        print("  ⚠ 行级 diff 模块不可用，跳过时装热更表：%s" % exc)
        return

    pre, post = _find_pkg_pair(args)
    if not pre or not post:
        (td / "时装热更表.md").write_text(
            "# 时装 · 本次热更表\n\n"
            "⚠ **未采集**：找不到热更前后的 script 包。\n\n"
            "给出 `--pre-pkg` / `--post-pkg`，或把它们放进 `02_资料/源包/`\n"
            "（`pre_update_*/raw/script*.npk` 与 `post_update_*/raw/script*.npk`）。\n",
            encoding="utf-8")
        print("  ⚠ 时装热更表：未采集（缺 pre/post script 包）")
        return

    names = _load_names_map(getattr(args, "dict_path", None))
    rep = HR.diff_npk(Path(pre), Path(post), FASHION_TABLES, names,
                      workdir=out / "_rows_bits", quiet=True)
    md = HR.render_md(rep, "时装 · 本次热更表（行级）")
    (td / "时装热更表.md").write_text(md, encoding="utf-8")
    _dump(rep, str(td / "时装热更表.json"))
    print("  ✓ 时装热更表：%s" % " ｜ ".join(
        "%s 新增%d/移除%d/变更%d" % (k, v.get("计数", {}).get("新增", 0),
                                   v.get("计数", {}).get("移除", 0),
                                   v.get("计数", {}).get("变更", 0))
        for k, v in rep.items() if "计数" in v))


def cmd_hotfix_bundle(args) -> int:
    """★ 把一次热更的全量产物铺成【标准交付结构】。

    对标（都在模块 docstring 里写了出处）：
      · 一个根目录按类型分子目录 + 顶层 manifest.json（Intelli-verse-X asset-pipeline-standard）
      · inventory 按类型统计（evrFileTools）
      · 名字不明的单独放 99_未归类（ree-pak-rs --skip-unknown）
      · 幂等 + 硬链接（免拷贝、可重复跑）

    定位判据：overlay 帧的【内容 SHA-256】对本地产物的 SHA-256。
    ★ 不用尺寸 —— 尺寸会撞（实测多个帧尺寸相同会落到同一行）。
    """
    import hashlib
    import sqlite3
    from collections import defaultdict
    from concurrent.futures import ThreadPoolExecutor

    product_root = Path(args.product_root) if getattr(args, "product_root", None) else \
        _default_product_root()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # ① 报告
    rep_path = Path(args.report) if args.report else (out / "hotfix_report.json")
    rep = {}
    if rep_path.is_file():
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        print("报告 %s" % rep_path)
    else:
        print("⚠ 未找到报告 %s（继续，但元数据会缺）" % rep_path)
    ts = (rep.get("steps", {}).get("1_list", {}) or {}).get("timestamp", "") or ""
    pkg_names = [p.get("name", "") for p in
                 ((rep.get("steps", {}).get("1_list", {}) or {}).get("packages") or [])]

    # ② 字典
    dict_path = Path(args.dict_path) if getattr(args, "dict_path", None) else DEFAULT_NAMES_DICT
    print("字典 %s" % dict_path.name)

    b = HB.Bundle(out, names_dict=dict_path)
    b.ensure_dirs()

    # ③ 解 overlay 包 → 帧
    pkgs_dir = Path(args.pkgs) if args.pkgs else (out / "pkgs")
    pkgs = sorted(pkgs_dir.glob("*.npk")) if pkgs_dir.is_dir() else []
    print("包 %d 个（%s）" % (len(pkgs), pkgs_dir))

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from toolkit_core import patch_overlay as PO
    from toolkit_core import artifact_locator as AL

    frames = []          # [(pkg_name, idx, bytes)]
    for pk in pkgs:
        raw = pk.read_bytes()
        if len(raw) <= 32:
            continue
        u = PO.unpack_frames(raw)
        if u.get("n_decoded", 0) == 0:
            # 非 zstd 封装（如 video 的纯 MP4 / script 明文壳）：整段当一个块
            frames.append((pk.name, 0, raw[32:]))
            continue
        for i, blk in enumerate(u["pieces"]):
            frames.append((pk.name, i, blk))
    print("解出块 %d 个" % len(frames))

    # ③b ★★ 新增/移除行 —— 这才是「本次热更该有的内容」的大头
    #    ★ 教训：只吃 overlay 帧会严重漏内容（实测：overlay 374 帧 vs 新增行 23,322，
    #      而立绘/图集本体/大部分贴图都在新增行里）。
    added_f, removed_f = set(), set()
    pc = getattr(args, "pkg_cache", None)
    if pc:
        pc = Path(pc)
        rel = _pkg_fids(pc / "rel")
        pt = _pkg_fids(pc / "pt")
        if rel and pt:
            added_f, removed_f = pt - rel, rel - pt
            print("★ pkg_N.pi diff：新增 %d ｜ 移除 %d ｜ 共有 %d"
                  % (len(added_f), len(removed_f), len(pt & rel)))
        else:
            print("⚠ --pkg-cache 下没读到 pkg_*.pi（应有 rel/ 与 pt/ 两个子目录）")
    else:
        # ★★ 拒绝静默给残缺结果 —— 只吃 overlay 帧会漏掉大头
        #    （实测：overlay 374 帧 vs 新增行 23,322；立绘/图集本体都在新增行里）。
        #    要只做 overlay 那部分，请显式加 --overlay-only。
        if not getattr(args, "overlay_only", False):
            print("✗ 未给 --pkg-cache ⇒ 拿不到「新增/移除行」，本次热更的大头会缺失。", file=sys.stderr)
            print("  实测：只吃 overlay 帧得到 372 条，接上 pkg_N.pi diff 后是 23,694 条。", file=sys.stderr)
            print("  请给 --pkg-cache <含 rel/ 与 pt/ 两版本 pkg_N.pi 的目录>；", file=sys.stderr)
            print("  确实只要 overlay 那部分，请显式加 --overlay-only。", file=sys.stderr)
            return 2
        print("⚠ --overlay-only：本次只做 overlay 帧，产物【不完整】，manifest 会标注")

    # 新增行 → 按 fid 定位到本地容器行（内容已落地，直接可取）
    n_add_rows = 0
    if added_f:
        db0 = sqlite3.connect("file:%s?mode=ro" % str(DEFAULT_DB).replace("\\", "/"), uri=True)
        fmap2 = {}
        for f, c, r in db0.execute("SELECT fid_hex,container,row_index FROM entries"):
            if f in added_f:
                fmap2[f] = (c, r)
        for h, (c, r) in fmap2.items():
            nm = b.names.get(h, "")
            b.add(container=c, row=r, name=nm or None, source="pkg_N.pi diff",
                  note="新增行")
            n_add_rows += 1
        print("  新增行定位到本地 %d / %d" % (n_add_rows, len(added_f)))
        # 变更清单落盘
        ch = out / HB.D_DELTA / HB.V_CHANGES
        ch.mkdir(parents=True, exist_ok=True)
        (ch / "新增_fid.txt").write_text("\n".join(sorted(added_f)), encoding="utf-8")
        (ch / "移除_fid.txt").write_text("\n".join(sorted(removed_f)), encoding="utf-8")
        # 有名字的新增（字典里查得到的）
        nm_add = sorted(b.names[h] for h in added_f if h in b.names)
        (ch / "新增_有名字.txt").write_text("\n".join(nm_add), encoding="utf-8")
        print("  其中字典里有名字的 %d 条" % len(nm_add))
        print("  → %s（新增_fid.txt / 移除_fid.txt / 新增_有名字.txt）" % ch)

    # ④ 内容哈希定位（want_sizes 预过滤）
    sizes = {len(x[2]) for x in frames}
    loc = AL.Locator()
    db = sqlite3.connect("file:%s?mode=ro" % str(DEFAULT_DB).replace("\\", "/"), uri=True)
    # ★ 没有 overlay 帧就直接跳过内容索引（建它是分钟级的白活）
    if not frames:
        print("  （无 overlay 帧，跳过内容索引）")
        hits = {}
    else:
        # ★ content_index 把 content_hashes 表写回【主索引库】（它也从那里读 entries），
        #   所以 index_db 必须传 DEFAULT_DB，不能传临时库（否则 OperationalError: no such table）
        try:
            from toolkit_core import content_index as CI
            st = CI.build(DEFAULT_DB, product_root, want_sizes=sizes,
                          workers=args.workers, quiet=not args.verbose)
            print("  内容索引: %s" % st)
            md5s = {hashlib.md5(x[2]).hexdigest(): x for x in frames}
            hits = CI.lookup_many(DEFAULT_DB, list(md5s))
        except Exception as exc:
            print("  ⚠ 内容索引不可用（%s: %s），回退到逐块 SHA-256 比对"
                  % (type(exc).__name__, str(exc)[:80]))
            hits = {}

    # 未命中索引的块：退回直接哈希比对
    def sha(b):
        return hashlib.sha256(b).hexdigest()

    unresolved = list(frames)
    by_sha_ok = 0
    if hits:
        # CI.lookup_many 返回 {md5: [(container,row),...]} 之类 —— 兼容多种形状
        def first_loc(v):
            if isinstance(v, (list, tuple)) and v:
                x = v[0]
                if isinstance(x, (list, tuple)) and len(x) >= 2:
                    return str(x[0]), int(x[1])
                if isinstance(x, dict):
                    return str(x.get("container", "")), int(x.get("row_index", -1))
            return None, None
        for md5, fr in list(md5s.items()):
            v = hits.get(md5)
            c, r = first_loc(v)
            if c:
                b.add(container=c, row=r, name=None,
                      source=fr[0], size=len(fr[2]), sha256=sha(fr[2]),
                      note="块%d" % fr[1])
                unresolved = [x for x in unresolved if x is not fr]
                by_sha_ok += 1

    if unresolved:
        print("  回退哈希比对的块 %d 个（会慢）" % len(unresolved))
        # 按尺寸分桶，只读候选尺寸的行
        want = {len(x[2]) for x in unresolved}
        rows = db.execute("SELECT container,row_index,decoded FROM entries").fetchall()
        cand = defaultdict(list)
        for c, r, sz in rows:
            if sz in want:
                cand[sz].append((c, r))
        print("  候选行 %d" % sum(len(v) for v in cand.values()))

        def probe(item):
            c, r = item
            fp = loc.path(c, r)
            if fp is None:
                return None
            try:
                return (c, r, sha(fp.read_bytes()))
            except OSError:
                return None

        pool = [x for v in cand.values() for x in v]
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            table = {}
            for t in ex.map(probe, pool):
                if t:
                    table.setdefault(t[2], (t[0], t[1]))
        print("  候选哈希 %d 个" % len(table))
        for fr in unresolved:
            sh = sha(fr[2])
            t = table.get(sh)
            if t:
                b.add(container=t[0], row=t[1], name=None,
                      source=fr[0], size=len(fr[2]), sha256=sh, note="块%d" % fr[1])
            else:
                # ★ 未在本地命中 —— 但【内容的字节还在手上】，不能只记一行 CSV 就完事。
                #   按魔数推扩展名，落到 99_未归类/，manifest 里如实标 note。
                mc = HB.magic_class(fr[2][:16])
                ext = {"video": ".mp4", "audio": ".fsb", "image": ".bin",
                       "fx": ".txt", "text": ".txt", "script": ".bin"}.get(mc, ".bin")
                stem = Path(fr[0]).stem[:40]
                name = "%s_块%d%s" % (stem, fr[1], ext)
                dst = out / HB.D_OTHER / HB.O_UNSOLVED / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists():
                    dst.write_bytes(fr[2])
                b.unknown.append({"container": "", "row": -1, "name": "",
                                  "ext": ext.lstrip("."), "size": len(fr[2]),
                                  "sha256": sh, "saved_as": name,
                                  "note": "块%d 本地未命中；内容已存为 %s（%s）"
                                          % (fr[1], name, mc or "魔数不认")})

    # 把名字补上（fid → 路径）
    db2 = sqlite3.connect("file:%s?mode=ro" % str(DEFAULT_DB).replace("\\", "/"), uri=True)
    fmap = {}
    for c, r in {(x["container"], x["row"]) for x in b.rows}:
        row = db2.execute("SELECT fid_hex FROM entries WHERE container=? AND row_index=?",
                          (c, r)).fetchone()
        if row:
            fmap[(c, r)] = row[0]
    for x in b.rows:
        h = fmap.get((x["container"], x["row"]))
        if h and not x["name"]:
            x["name"] = b.names.get(h, "")
            x["named"] = bool(x["name"])
            x["ext"] = HB._ext_of(x["name"] or "")

    print("登记 %d 条（有名 %d）｜ 未定位 %d 条"
          % (len(b.rows), sum(1 for x in b.rows if x["named"]), len(b.unknown)))

    # ⑤ 物化 + 汇总
    st = b.materialize(do_sha=False, workers=args.workers,
                       png=bool(getattr(args, "png", False)))
    print("物化: %s" % st)
    # ★ 清理历史版本可能残留的临时库（它不该出现在交付目录里）
    for junk in out.glob("_content_index.sqlite3*"):
        try:
            junk.unlink()
        except OSError:
            pass
    b.write_manifest(meta={"hotfix_ts": ts, "source_report": str(rep_path),
                           "packages": pkg_names})
    b.write_inventory()
    b.write_unknown_list()
    loc3 = (rep.get("steps", {}).get("3_locate", {}) or {})
    l1 = l2 = ""
    if loc3 and loc3.get("total_blocks"):
        l1 = "overlay 帧：%s / %s 块命中（%.1f%%）" % (
            loc3.get("total_hits"), loc3.get("total_blocks"),
            loc3.get("total_hits", 0) / loc3["total_blocks"] * 100)
    if n_add_rows:
        l2 = "新增行：%d / %d 定位到本地容器行（%.1f%%）" % (
            n_add_rows, len(added_f), n_add_rows / len(added_f) * 100 if added_f else 0)
    locate_str = "；".join(x for x in (l1, l2) if x) or "—（未提供 hotfix 报告）"
    b.write_readme(hotfix_ts=ts, packages=pkg_names,
                   locate=locate_str,
                   extra="## 定位判据\n\n"
                         "- **overlay 帧** → 内容 SHA-256 对本地产物 SHA-256\n"
                         "- **新增行** → `pkg_N.pi`（playertest vs release）差集，fid → 索引 `entries`\n"
                         "- ★ 两者缺一不可：只吃 overlay 会漏掉大头（实测 372 vs 23,694）\n"
                         "- ★ 判据不用尺寸 —— 尺寸会撞（多个帧尺寸相同会落到同一行）")
    # ★ 报告类文件收进 05_变更清单与报告总结（README 与 manifest 在根做入口）
    try:
        rep_dir = out / HB.D_DELTA
        rep_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out / "README.md", rep_dir / "README.md")
        if Path(rep_path).is_file():
            shutil.copy2(rep_path, rep_dir / "hotfix_report.json")
    except (OSError, NameError) as exc:
        print("  ⚠ 报告归类失败：%s" % exc)
    if args.text_tables:
        tt = json.loads(Path(args.text_tables).read_text(encoding="utf-8"))
        b.write_text_tables(tables=tt)
    else:
        # ★★ 02_文字表 必须给【实质内容】，不能只写「本次未涉及」。
        #   做法：① 本次热更涉及的文字表（从新增行筛 _chs.py / cdata 表）——本次为 0
        #        ② 全量文字表汇总（复用已有的抽取产物，见 --text-src）
        _fill_text_tables(b, out, added_f, dict_path, args)

    print()
    print("★ 标准交付结构 → %s" % out)
    for p in sorted(out.iterdir()):
        if p.is_dir():
            n = len([x for x in p.rglob("*") if x.is_file()])
            print("   %-24s [%d 文件]" % (p.name + "/", n))
        else:
            print("   %-24s %d B" % (p.name, p.stat().st_size))
    if args.json is not None:
        _dump({"out": str(out), "entries": len(b.rows),
               "named": sum(1 for x in b.rows if x["named"]),
               "unknown": len(b.unknown), "materialize": st}, args.json)
    return 0


def cmd_hotfix_rows(args) -> int:
    """★ [带 H] 行级热更 diff：两个 script 包逐行比。

    补的缺口：`delta pkg diff` 只到【包级/fid 级】，答不了「哪一行变了」。
    script 容器按【模块名】索引、表按【行】组织 ⇒ 真内容变化是行级的。

    ★ 口径（见 toolkit_core/hotfix_rows 的三条实测教训）：
      只比【真值字段】—— 凡值是 `jump:行号` 的一律排除（行号漂移不是内容变更），
      也不比 `start`/`schema`/`bitmap` 这些解码偏移元数据。
    """
    import re as _re

    from toolkit_core import hotfix_rows as HR

    # 表清单：--tables / --table-file / --filter，默认时装族
    tables = list(args.tables or [])
    if args.table_file:
        for line in Path(args.table_file).read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line:
                tables.append(line.replace("\\", "/").split("/")[-1])
    if not tables:
        # ★ 默认 = 时装族（用户口径：文字表产物固定要一份时装热更表）
        tables = ["fashion_data_chs.py", "player_appear_data_chs.py",
                  "fashion_data.py", "player_appear_data.py"]
    if args.kw:
        rx = _re.compile(args.kw, _re.I)
        before = len(tables)
        tables = [t for t in tables if rx.search(t)]
        # ★ 静默 0 结果防护：--filter 把表筛空时必须报错退出，不能静默跑出「0 张表」的假成功
        if not tables:
            print("hotfix rows：--filter %r 把候选表筛空了（筛前 %d 张，全是默认时装族）。"
                  % (args.kw, before), file=sys.stderr)
            print("  ⇒ --filter 是【在 --tables 之上再筛】，不是【全库搜表名】。"
                  "要按关键词找表请显式给 --tables，例如：", file=sys.stderr)
            print("     --tables fashion_data_chs.py player_appear_data_chs.py "
                  "nucleus_build_data_chs.py lottery_big_reward_conf_chs.py", file=sys.stderr)
            return 2
    # 去重保序
    seen, uniq = set(), []
    for t in tables:
        if t.lower() not in seen:
            seen.add(t.lower())
            uniq.append(t)
    tables = uniq

    names = _load_names_map(args.dict_path)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print("★ 行级热更 diff")
    print("  pre : %s" % args.pre)
    print("  post: %s" % args.post)
    print("  表 %d 张：%s" % (len(tables), tables))
    print()

    rep = HR.diff_npk(Path(args.pre), Path(args.post), tables, names,
                      workdir=out / "_bits", quiet=args.quiet)

    md = HR.render_md(rep, "行级热更表")
    (out / "行级热更表.md").write_text(md, encoding="utf-8")
    _dump(rep, str(out / "行级热更表.json"))

    print()
    print("★ 产物 → %s" % out)
    for p in sorted(out.iterdir()):
        if p.is_file():
            print("   %-24s %d B" % (p.name, p.stat().st_size))
    if args.json is not None:
        _dump(rep, args.json)
    return 0


def cmd_hotfix_patchlog(args) -> int:
    """★ [带 H] 读客户端补丁日志（`Documents/plcoht_ag`，单字节 XOR 0xAA）。

    补的缺口：官方 CDN 清单只到**包级**，`plcoht_ag` 是**客户端落盘级** ——
    它给出「客户端手里应该有的每个文件 + 逐文件版本串 `fver` + 各种哈希 + 期望大小」。

    ★ 最有用的一点：`fver` 形如 `20260929_172554_playertest_newpc`，
    即**该次的版本推送时间** ⇒ 看一眼就知道「最近几次热更分别发生在什么时候」，
    不用逐个容器算哈希。

    ★ 另有本地对照：清单期望大小 vs 本地实测（缺哪些、大小不符哪些）。
    """
    from toolkit_core import patch_log as PL

    root = Path(args.client_root)
    logs = [Path(p) for p in (args.log or [])] if getattr(args, "log", None) else PL.find_logs(root)
    if not logs:
        print("hotfix patchlog：在 %s\\Documents 下找不到 plcoht_ag —— 客户端还没跑过补丁？"
              % root, file=sys.stderr)
        return 2

    out = Path(args.out) if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    print("★ 客户端补丁日志")
    print("  客户端根：%s" % root)
    print("  日志 %d 份：%s" % (len(logs), [p.name for p in logs]))
    if args.find:
        print("  关键词过滤：%s" % args.find)
    print()

    all_rep = {"kind": "patch_log_batch", "client_root": str(root), "logs": []}
    for p in logs:
        text = PL.read_log(p)
        rep = PL.summarize(text, client_root=(None if args.no_local_check else root),
                           limit=args.limit, find=args.find)
        rep["log"] = str(p)
        all_rep["logs"].append(rep)

        print("═" * 74)
        print("★ %s" % p.name)
        print("   会话（%d 次）：%s" % (rep["session_count"],
                                   " · ".join(rep["sessions"]) or "—"))
        print("   记录 %d 条 · 期望清单 %d 条%s" % (
            rep["records"], rep["manifest_entries"],
            ("（过滤后 %d）" % rep["match_count"]) if args.find else ""))
        if rep["fvers"]:
            print("   ★ 版本串 fver：")
            for k, v in rep["fvers"].items():
                print("       %-46s × %d" % (k, v))
        if rep["families"]:
            print("   家族分布（前 12）：")
            for k, v in list(rep["families"].items())[:12]:
                print("       %-24s %d" % (k, v))
        lc = rep.get("local_check")
        if lc:
            print("   本地对照：查 %d · 缺失 %d · 大小不符 %d" % (
                lc["checked"], lc["missing"], lc["size_mismatch"]))
            for x in lc["missing_sample"][:5]:
                print("       ✗ 缺 %s" % x)
            for x in lc["mismatch_sample"][:5]:
                print("       ≠ %s 期望 %s / 实测 %s" % (x["path"], x["expect"], x["actual"]))
        if rep["sample"]:
            print("   样例：")
            for s in rep["sample"][:args.limit]:
                print("       %-56s fver=%s doc=%s" % (
                    s["path"][:56], s.get("fver") or "—",
                    s.get("doc") or s.get("size") or "—"))

        if out:
            stem = p.name.replace(".", "_")
            (out / ("补丁日志_%s.md" % stem)).write_text(
                PL.render_md(rep, "客户端补丁日志 · %s" % p.name), encoding="utf-8")
    if out:
        json.dump(all_rep, (out / "补丁日志.json").open("w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print()
        print("★ 产物 → %s" % out)
        for q in sorted(out.iterdir()):
            if q.is_file():
                print("   %-28s %d B" % (q.name, q.stat().st_size))
    if args.json is not None:
        PL.json_dump(all_rep, args.json)
    return 0


def cmd_sched(args) -> int:
    """[横切] ★ 智能调度：显示硬件、并行预算、GPU 可用性 —— 以及【哪些任务真能上 GPU】。

    ★ 诚实原则：不能上 GPU 的任务明确说不能，并给理由；不假装限了 GPU。
    """
    import json as _json
    from toolkit_core import throttle as TH

    snap = TH.global_snapshot()
    hw = snap["hardware"]

    print("★ 智能调度 · 本机能力")
    print("   CPU      %s 逻辑核 / %s 物理核   当前占用 %s%%"
          % (hw.get("cpu_logical"), hw.get("cpu_physical"),
             snap.get("cpu_percent")))
    mem = ("%.1f GB（可用 %.1f）" % (hw["mem_total_gb"], hw["mem_avail_gb"])
           if hw.get("mem_total_gb") else "未知")
    print("   内存     %s" % mem)
    if hw.get("gpu_name"):
        print("   GPU      %s  %s  %.1f GB  %d SM   当前占用 %s%%"
              % (hw["gpu_name"], hw.get("gpu_cc") or "", hw.get("gpu_mem_gb") or 0,
                 hw.get("gpu_sm") or 0, snap.get("gpu_percent")))
    else:
        print("   GPU      未探测到")
    print("   CUDA     %s   torch %s" % ("可用" if hw.get("cuda") else "不可用",
                                        hw.get("torch_version") or "未装"))
    print()

    pol = snap["policy"]
    print("★ 当前策略")
    print("   CPU 上限 %s%%   GPU 上限 %s%%   限流 %s   GPU 模式 %s"
          % (pol["cpu_limit"], pol["gpu_limit"],
             "开" if snap["throttle"] else "★ 关（跑满）", snap["gpu_mode"]))
    print("   并行数覆盖：%s" % (snap["jobs_override"] or "auto（按任务类型自动）"))
    print()
    print("★ 并行预算（来源：%s）" % snap.get("jobs_source", "auto"))
    names = {"io": "文件遍历/读盘/解包", "cpu": "哈希/解码/统计（CPU 密集）",
             "mixed": "读+算（批量解码，最常用）", "light": "查索引（极轻）",
             "gpu": "GPU 高负载（CPU 只喂数据）",
             "mem": "★ 内存吃重（大张量/百万级对象）"}
    for k in ("io", "cpu", "mixed", "light", "gpu", "mem"):
        print("   %-6s %3d  workers   %s" % (k, snap["jobs"][k], names[k]))
    ram = snap.get("ram") or {}
    bud = snap.get("ram_budget_gb") or {}
    print("★ 内存预算（实时读，不缓存）")
    print("   可用 %.1f GB / 共 %.1f GB（已用 %s%% ｜ swap %.2f GB）"
          % (ram.get("mem_avail_gb") or 0, ram.get("mem_total_gb") or 0,
             ram.get("mem_used_pct"), ram.get("swap_used_gb") or 0))
    print("   任务预算：常规(0.5)=%.1f GB ｜ 重活(0.7)=%.1f GB ｜ 并行(0.3)=%.1f GB"
          % (bud.get("常规(0.5)", 0), bud.get("重活(0.7)", 0), bud.get("并行(0.3)", 0)))
    print("   （单行 N 字节时，分块行数 = 预算/行宽 —— 见 TH.recommend_chunk_rows）")
    print()

    print("★ 哪些任务真能上 GPU（禁止假承诺）")
    for kind in ("image_stats", "image_resize", "bc_decode", "render", "hash_batch",
                 "decompress", "decrypt", "hash", "walk"):
        ok, why = TH.gpu_capable(kind)
        print("   %s %-13s %s" % ("✅" if ok else "❌", kind, why))
    print()
    print("★ 用法")
    print("   toolkit_cli --jobs 16 <命令>        指定并行数")
    print("   toolkit_cli --cpu-limit 60 <命令>   最多占 60% CPU")
    print("   toolkit_cli --no-throttle <命令>    跑满（没人用电脑时）")
    print("   toolkit_cli --gpu off <命令>        禁用 GPU")

    if getattr(args, "json", None) is not None:
        PL.json_dump(snap, args.json)
    return 0


def _names_common_item(ids, idx_p, args) -> int:
    """`ns=common_item`：走工作副本专用链（★ 只认 quality=ok 且不重名）。

    ★ 为什么单开：common_item 不在 41_还原树、也不在包内，
      数据在 `config_work/<snapshot>/entries/`（base∪inc−del × chs）。
      且它的名字有 **48% 处于重名群组**（含 icon 路径），必须逐条标可信度。
    """
    from toolkit_core import common_item_names as CI

    st = CI.stats()
    if not st.get("exists"):
        print("[names items] ✗ common_item 索引还没建 —— 先跑：names items ci-build",
              file=sys.stderr)
        return 4
    meta = CI.lookup_meta(ids, Path(args.index) if idx_p else None)
    print("★ item_id → 名字（ns=common_item · ★ 工作副本专用链）")
    print("   快照 %s（entries %s）· base=%s chs=%s"
          % (st.get("snapshot"), st.get("entries"), st.get("base"), st.get("chs")))
    print("   索引 %d 条，其中 **可用 %d 条**（quality=ok 且不重名）· "
          "重名名字 %d 个" % (st["count"], st["usable"], st["dup_names"]))
    hit = usable = 0
    for i in ids:
        rec = meta.get(i)
        if not rec:
            print("   %-12d ★ 未收录（该 id 不在此 ns 的 base∪inc−del 里）" % i)
            continue
        hit += 1
        q, dup = rec.get("quality"), bool(rec.get("dup"))
        ok = (q == "ok" and not dup)
        usable += 1 if ok else 0
        print("   %-12d %-30s [%s%s]%s"
              % (i, str(rec.get("name"))[:30], q, "·重名" if dup else "",
                 "" if ok else "   ⚠ 非可用（只是候选，别当结论）"))
    print()
    print("   命中 %d / 未收录 %d ｜ 其中可用 %d" % (hit, len(ids) - hit, usable))
    print("★ 纪律：只有 quality=ok 且不重名的才算名字；其余是候选，禁当结论。")
    if args.json is not None:
        PL.json_dump({"ns": "common_item", "stats": st,
                      "hits": {str(k): v for k, v in meta.items()}}, args.json)
    return 0 if hit else 5


def cmd_script(args) -> int:
    """★ 脚本模块方言读取（NeoX 魔改 marshal）：抽字符串 / 整数。

    ★ 能力边界（如实）：能抽**名字与文案**和**整数**；**还原不了字节码**
      （opcode 被换表）⇒ 拿不到「常量值 ↔ 字段名」的绑定。
    实测 tag：0xd3/0xf3 ASCII 串(1B 长, 0xff→u32) · 0xda/0xfa Unicode 串 · 0x5a 整数(u32)。
    """
    import json as _json
    from toolkit_core import paths as P
    from toolkit_core import script_dialect as SD
    target = args.target
    p = Path(target)
    if not p.is_file():
        # 按模块名在还原树里找（Documents 层优先 = 当前态）
        rel = target.replace(".", "/").replace("\\", "/")
        cands = [P.TREE_ROOT / "Documents/script.py314.lc.npk" / (rel + ".py"),
                 P.TREE_ROOT / "script.py314.lc.npk" / (rel + ".py"),
                 P.TREE_ROOT / "Documents/script.py314.lc.npk" / rel,
                 P.TREE_ROOT / "script.py314.lc.npk" / rel]
        p = next((c for c in cands if c.is_file()), None)
    if p is None or not p.is_file():
        print("✗ 找不到脚本模块：%s（给路径，或给 com.const 这种模块名）" % target, file=sys.stderr)
        return 6
    strs, ints = SD.scan_file(p)
    print("★ 脚本模块方言扫描：%s（%d B）" % (p, p.stat().st_size))
    print("   字符串 %d ｜ 整数 %d" % (len(strs), len(ints)))
    what = args.what or "strings"
    if what in ("strings", "all"):
        rows = [x for x in strs if (not args.grep or args.grep.lower() in x["s"].lower())]
        print("   ── 字符串（%d 条，显示前 %d）──" % (len(rows), args.limit))
        for x in rows[:args.limit]:
            print("   @%-9d %s len=%-4d %s" % (x["off"], x["tag"], x["len"], x["s"][:80]))
    if what in ("ints", "all"):
        iv = ints[:args.limit]
        print("   ── 整数（%d 个，显示前 %d）──" % (len(ints), args.limit))
        print("   %s" % [x["v"] for x in iv])
    if args.json is not None:
        rep = {"module": str(p), "strings": strs, "ints": ints}
        if args.json == "-":
            print(_json.dumps(rep, ensure_ascii=False)[:4000])
        else:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).open("w", encoding="utf-8").write(
                _json.dumps(rep, ensure_ascii=False))
            print("   明细 → %s" % args.json)
    return 0


def cmd_names_candidates(args) -> int:
    """★ 名字【候选】名册：atlas 认领等**无哈希可校验**的推断，只登记不入权威表。

    候选 ≠ 名字：不写 row_path_map / 字典 / 还原树；物化链只读权威表，天然不会被污染。
    晋级条件（见台账）：a) 能按包内路径正算 fid == 行 fid（本轮 0 满足）
      b) 第二独立来源指向同一 (容器,行)  c) 内容指纹（尺寸+结构）一致且唯一
    """
    import json as _json
    REG = Path(r"E:\la拆包项目\00_治理\台账\名字候选_20261001.jsonl")
    CON = Path(r"E:\la拆包项目\00_治理\台账\名字候选_冲突_20261001.jsonl")
    LED = Path(r"E:\la拆包项目\00_治理\台账\名字候选_台账_20261001.json")
    src = CON if args.conflicts else REG
    if not src.is_file():
        print("✗ 候选名册不存在：%s（先跑建册脚本）" % src, file=sys.stderr)
        return 6
    rows = [_json.loads(x) for x in src.read_text(encoding="utf-8").splitlines() if x.strip()]
    if args.tier:
        rows = [r for r in rows if r.get("tier") == args.tier]
    if getattr(args, "verdict", None):
        rows = [r for r in rows if r.get("verdict") == args.verdict]
    if args.grep:
        rows = [r for r in rows if args.grep.lower() in str(r.get("name", "")).lower()]
    print("★ 名字候选名册（%s）｜ 共 %d 条 ｜ 可按哈希校验 %d 条"
          % ("冲突批" if args.conflicts else "净增候选", len(rows),
             sum(1 for r in rows if r.get("hash_verifiable"))))
    if LED.is_file():
        led = _json.loads(LED.read_text(encoding="utf-8"))
        print("   台账：净增 %s ｜ 分档 %s ｜ 冲突 %s ｜ 判词 %s"
              % (led.get("candidates_net_new"), led.get("by_tier"),
                 led.get("conflicts_vs_existing_name"),
                 (led.get("verdicts_20261001") or {}).get("可升级")))
    for r in rows[:args.limit]:
        print("   [%-3s%s] %s r%-6s %s"
              % (r.get("tier"), ("·" + r["verdict"]) if r.get("verdict") else "",
                 (r.get("container") or "")[:26], r.get("row"), (r.get("name") or "")[:58]))
        if r.get("existing_name"):
            print("          现有=%s" % str(r["existing_name"])[:70])
    if args.json is not None:
        rep = {"source": str(src), "count": len(rows), "rows": rows}
        if args.json == "-":
            print(_json.dumps(rep, ensure_ascii=False, indent=1))
        else:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).open("w", encoding="utf-8").write(
                _json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


def cmd_servers(args) -> int:
    """★ 服型（服务器类型后缀）总表 —— 中文名 / 依据 / 本客户端是否真有表族。

    唯一来源：`toolkit_core/server_types.py`（此前散在 lottery_locate 与注释里）。
    术语：`_auto_oversea_data_<后缀>` = 服务器类型变体，不是"渠道"。
    """
    import json as _json
    from toolkit_core import server_types as ST
    rows = sorted(ST.VARIANT_NAMES.items(), key=lambda kv: kv[0])
    cache = Path(ST.__file__).resolve().parents[2].parent / "03_执行" / "30_分析" / "服型总表_cache.json"
    per = {}
    if args.scan or not cache.is_file():
        per = (ST.scan_tree().get("per_suffix") or {})
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.open("w", encoding="utf-8").write(
                _json.dumps({"per_suffix": per}, ensure_ascii=False, indent=1))
        except OSError:
            pass
    else:
        try:
            per = (_json.loads(cache.read_text(encoding="utf-8")).get("per_suffix") or {})
        except Exception:                                                 # noqa: BLE001
            per = {}
    print("★ 服型后缀总表（来源：toolkit_core/server_types.py）")
    print("   术语：`_auto_oversea_data_<后缀>` = 【服务器类型变体】，不是渠道")
    print("   %-10s %-24s %9s  %s" % ("后缀", "中文名", "本端表数", "依据"))
    for suf, (nm, ev) in rows:
        cnt = per.get(suf, {}).get("files")
        print("   %-10s %-24s %9s  %s" % (suf, nm, cnt if cnt is not None else "-", ev[:44]))
    extra = sorted(k for k in per if k not in ST.VARIANT_NAMES)
    for suf in extra:
        d = per[suf]
        print("   %-10s %-24s %9d  %s" % (suf, d.get("name"), d.get("files"), d.get("evidence", "")[:44]))
    if args.scan:
        unknown = sorted(k for k in per if "未定" in (per[k].get("name") or ""))
        have_no_table = sorted(k for k in ST.VARIANT_NAMES if k not in per)
        if extra:
            print("\n   （以上 %d 个是复合后缀/新后缀，已按 label() 解析）" % len(extra))
        if unknown:
            print("   ★ 仍未定名的后缀：%s" % unknown)
        if have_no_table:
            print("   本端没有表族的后缀（如 yh 硬核无奖池 → 符合预期）：%s" % have_no_table)
    print("\n   base（无后缀）= 通用/经典服（用户口径：经典服可能不走后缀）")
    if args.json is not None:
        rep = {"variants": {k: {"name": v[0], "evidence": v[1]} for k, v in rows},
               "scan": per}
        if args.json == "-":
            print(_json.dumps(rep, ensure_ascii=False, indent=1))
        else:
            Path(args.json).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json).open("w", encoding="utf-8").write(
                _json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


def cmd_npk_header(args) -> int:
    """NPK 头/条目表：本地路径或 http(s) URL（★ 远端只取头+条目表，不下整包）。

    ★ 2026-10-01 头格式实测破解：
      48 B 头 → AES-ECB 解密 → [8:12]='NXPK' · [12:16]=ver · [16:20]=table_offset · [20:24]=count
      slack = size - (table_offset + count*48)：==0 表示【没有 NXFN】；>0 表示尾部有额外数据。
    """
    from toolkit_core import npk_remote as NR
    info = NR.read_header(args.target)
    print("★ NPK 头：%s" % args.target)
    if info.get("error"):
        print("  ✗ %s" % info["error"], file=sys.stderr)
        return 6
    print("  远端(Range)：%s ｜ 文件大小：%s B" % (info.get("remote"), info.get("size")))
    if not info.get("magic_ok"):
        print("  ✗ 解密后不是 NXPK（头 24 字节：%s）—— 可能不是 NPK 家族（如 .gpk）"
              % info.get("head_hex"), file=sys.stderr)
        return 7
    print("  version=%s ｜ 条目数=%s ｜ 条目表@%s ｜ 表末=%s"
          % (info.get("version"), info.get("entry_count"), info.get("table_offset"),
             info.get("table_end")))
    print("  头部其余 u32[24:48] = %s" % info.get("tail_u32"))
    print("  ★ slack=%s ⇒ %s" % (info.get("slack"),
                                "★有尾随数据（疑似 NXFN，值得看）"
                                if info.get("nxfn_suspected") else "无 NXFN（表尾即文件尾）"))
    if args.limit:
        ents = NR.read_entries(args.target, args.limit)
        print("  前 %d 条：" % len(ents))
        for e in ents:
            print("    #%-3d fid=%s off=%-9d packed=%-7d dec=%-7d zip=%d ff=%d reserved=%s"
                  % (e["index"], e["fid"], e["offset"], e["packed"], e["decoded"],
                     e["zip_flag"], e["file_flag"], e["reserved"]))
    if args.json is not None:
        _j = __import__("json")
        rep = {"header": info, "entries": NR.read_entries(args.target, args.limit)}
        if args.json == "-":
            print(_j.dumps(rep, ensure_ascii=False, indent=1))
        else:
            _o = Path(args.json)
            _o.parent.mkdir(parents=True, exist_ok=True)
            _o.open("w", encoding="utf-8").write(_j.dumps(rep, ensure_ascii=False, indent=1))
    return 0


def cmd_names_item_ci(args) -> int:
    """建 common_item 专用索引 + 报体检数字（可用率只有 ~28%，必须报清楚）。"""
    from toolkit_core import common_item_names as CI

    rep = CI.build(Path(args.out) if getattr(args, "out", None) else None)
    st = CI.stats()
    print("★ common_item 索引体检")
    print("   快照 %s（entries %s）· base=%s inc=%s del=%s chs=%s"
          % (st.get("snapshot"), st.get("entries"), st.get("base"),
             rep.get("inc"), rep.get("del"), st.get("chs")))
    print("   收录 %d 条 ｜ quality %s" % (st["count"], st.get("quality")))
    print("   ★ 可用（ok 且不重名）%d 条 = %.1f%% ｜ 重名名字 %d 个"
          % (st["usable"], 100.0 * st["usable"] / max(st["count"], 1), st["dup_names"]))
    print("   门禁口径：只有【可用】能进交付名字；其余是候选，禁当结论。")
    if args.json is not None:
        PL.json_dump({"build": rep, "stats": st}, args.json)
    return 0 if rep.get("ok") else 4


def cmd_names_item_show(args) -> int:
    """`names items show-build / show-lookup` —— 展示大奖名字表（直解树）。"""
    from toolkit_core import show_item_names as SN

    sub = getattr(args, "items_command", None) or "show-lookup"
    if sub == "show-build":
        rep = SN.build(Path(args.out) if getattr(args, "out", None) else None)
        st = SN.stats()
        print("   ★ 覆盖的表：%s" % " · ".join("%s=%d" % kv
                                          for kv in (st.get("tables") or {}).items()))
        if args.json is not None:
            PL.json_dump({"build": rep, "stats": st}, args.json)
        return 0 if rep.get("count") else 4

    ids = []
    for x in (getattr(args, "ids", None) or []):
        for part in str(x).replace(",", " ").split():
            try:
                ids.append(int(part))
            except ValueError:
                pass
    if not ids:
        print("names items show-lookup：要给至少一个 id", file=sys.stderr)
        return 2
    st = SN.stats()
    print("★ 展示大奖 id → 名字（源：直解树里的名字表）")
    print("   索引 %s（%d 条 · %s）" % ("在" if st.get("exists") else "★ 还没建",
                                     st.get("count", 0), st.get("generated", "—")))
    hits = SN.lookup(ids)
    for i in ids:
        rec = hits.get(i)
        if not rec:
            print("   %-12d ★ 未收录（不在这几张名字表的行里 —— 它多半是"
                  "武器皮肤/核芯这类**表内无 name 字段**的 id）" % i)
            continue
        for nm, tabs in rec:
            print("   %-12d %-26s ← %s" % (i, nm, ", ".join(tabs)))
    print()
    print("★ 口径：行 key == id 且有 name 字段才算；多表命中全列，不猜。")
    if args.json is not None:
        PL.json_dump({str(k): v for k, v in hits.items()}, args.json)
    return 0 if hits else 5


def cmd_names_items(args) -> int:
    """[①-1] ★ item_id → 名字 回填链（奖池/表输出里的 id 回填成人能看的名）。

    ★ 为什么固化进 CLI：奖池/表产物里全是 item_id（133218 / 570124…）人没法核对；
      名字的数据源是表结构产物的 `row_key + name` 列，必须有一条固定的链去取。

    sub：
      build   扫结构产物建索引（`10_索引/items/item_names.json`）
      lookup  查 id → 名字（查不到如实说「未收录」，不猜）
      stats   索引规模 + 覆盖的表排行 + 缺口说明
    """
    import json as _json
    from toolkit_core import item_names as IN

    sub = getattr(args, "items_command", None) or "lookup"

    if sub == "build":
        rep = IN.build(Path(args.out) if getattr(args, "out", None) else None)
        if args.json is not None:
            PL.json_dump(rep, args.json)
        return 0 if rep.get("ok") else 4

    if sub == "stats":
        st = IN.stats(Path(args.index) if getattr(args, "index", None) else None)
        print("★ item_id → 名字 索引（★ 命名空间感知 v2）")
        print("   文件：%s（%s）" % (st["path"], "在" if st["exists"] else "★ 还没建"))
        print("   收录：%d 个 (ns, id)" % st["count"])
        if st.get("legacy_exists"):
            print("   ⚠ 还留着 v1 的错版索引：%s" % st["legacy_path"])
            print("      ★ v1 把 row_key 当全局 id ⇒ 跨表撞车、回填全错。别再读它。")
        if st["namespaces"]:
            print("   各命名空间：")
            for ns, n in sorted(st["namespaces"].items(), key=lambda kv: -kv[1]):
                tbls = (st["ns_tables"] or {}).get(ns) or []
                print("      %-16s %6d 条   表：%s" % (ns, n, ", ".join(tbls[:2])))
        if st["struct_roots"]:
            print("   结构产物源：%s" % " · ".join(st["struct_roots"]))
        print()
        print("★ 缺口说明：结构产物只覆盖 cdata 全量的一小部分")
        print("  （那条总装链当初只跑了「本次变更表清单」）⇒ 查不到名 ≠ id 不存在。")
        print("★ 纪律：ns 未知一律不回填 —— 绝不拿别的表的同号行顶替。")
        if args.json is not None:
            PL.json_dump(st, args.json)
        return 0

    ids = []
    for x in (getattr(args, "ids", None) or []):
        for part in str(x).replace(",", " ").split():
            try:
                ids.append(int(part))
            except ValueError:
                pass
    if not ids:
        print("names items lookup：要给至少一个 id（可空格/逗号分隔）", file=sys.stderr)
        return 2
    idx_p = Path(args.index) if getattr(args, "index", None) else None
    ns = getattr(args, "ns", None)
    if ns:
        # ★ common_item 走专用链（见 _names_common_item）
        if ns == "common_item":
            return _names_common_item(ids, idx_p, args)
        meta = IN.lookup_ns(ns, ids, idx_p)
        print("★ item_id → 名字（ns=%s · %d 个）" % (ns, len(ids)))
        hit = 0
        for i in ids:
            rec = meta.get(i)
            if rec:
                hit += 1
                print("   %-12d %-30s  ← %s/%s"
                      % (i, rec.get("name"), rec.get("table", "?")[:36], rec.get("field", "?")))
            else:
                print("   %-12d ★ 未收录（该 ns 的结构产物没覆盖到）" % i)
        print()
        print("   命中 %d / 未收录 %d" % (hit, len(ids) - hit))
        if args.json is not None:
            PL.json_dump({"ns": ns, "hits": {str(k): v for k, v in meta.items() if v}},
                         args.json)
        return 0 if hit else 5

    # 不带 ns：★ 只做人工排查，明确标出撞车
    anyr = IN.lookup_any(ids, idx_p)
    print("★ item_id → 名字（★ 未指定 ns，跨表排查模式）")
    print("   ⚠ 不同表的 row_key 会撞车 —— 要准确回填请给 --ns（如 --ns gift_data）")
    print()
    for i in ids:
        rec = anyr.get(i)
        if not rec:
            print("   %-12d ★ 未收录" % i)
            continue
        amb = "  ⚠ 多 ns 名字不同" if rec.get("ambiguous") else ""
        print("   %-12d %s%s" % (i, rec.get("name"), amb))
        for c in (rec.get("candidates") or [])[:6]:
            print("        ns=%-14s %-26s ← %s"
                  % (c.get("ns"), c.get("name"), (c.get("table") or "")[:34]))
    if args.json is not None:
        PL.json_dump({str(k): v for k, v in anyr.items()}, args.json)
    return 0


def cmd_lottery_chain(args) -> int:
    """[H-1] ★ 全量奖池链：活动 → lottery_id → 展示大奖 → 名字（全通道一遍跑完）。

    ★ 边界（实测）：客户端无 `reward_pool_data_base` ⇒ 池【成员】静态不可得。
      本命令给的是客户端能确定的全量：
        L1 活动行 → lottery_id / lottery_group_id / rule_id
        L0 展示项  panel_show_item_ids（0x27 组，通常 4 件大奖）+ 名字回填
    """
    from toolkit_core import lottery_chain as LC

    print("★ 全量奖池链（源：41_还原树）")
    print()
    rep = LC.build(out=Path(args.out) if getattr(args, "out", None) else None)
    print()
    rep = LC.apply_names(rep)
    print()
    # ★ 活动桥接（2026-09-30）：抽奖配置 key → 活动号 → 静态展示道具
    rep = LC.attach_hd(rep)
    print()
    cs = LC.channel_summary(rep)
    if cs:
        print("★ 服型覆盖：同一 key 在不同【服务器类型变体】里 lottery_id 不同（%d 组）——★ 不是矛盾"
              % len(cs))
        for g in cs[:8]:
            pairs = " ｜ ".join("%s→%s" % ("/".join(chs), lid)
                                for lid, chs in sorted(g["ids"].items()))
            print("   key=%-7s group=%-6s %s" % (g["key"], g["group"], pairs))
        if len(cs) > 8:
            print("   …还有 %d 组（见 JSON 的 channel_summary）" % (len(cs) - 8))
        print("   ⇒ 客户端按服型覆盖：服型表（kj1＝简单生存 / kjxq / kj* 各地区 / yk＝月卡服 …）"
              "优先于 base 表（base＝通用/经典服）。★ 这是【服务器类型变体】，不是渠道。")
    rep["channel_summary"] = cs
    hrows = [r for r in (rep.get("rows") or []) if r.get("hd")]
    hrows.sort(key=lambda r: -(r["hd"].get("n_static") or 0))   # ★ 有静态道具的排前面
    if hrows:
        n_with = sum(1 for r in hrows if (r["hd"].get("n_static") or 0) > 0)
        print()
        print("★ 活动静态展示道具：%d 行对上了活动（其中 %d 行拿到静态列表）"
              "（桥 = 活动行 extra_param ←→ 抽奖配置 key）" % (len(hrows), n_with))
        for n, r in enumerate(hrows[:4]):
            hd = r["hd"]
            print("   super key=%-7s → 活动 %-7s %-16s · 静态 %d 件（面板 %d 件）"
                  % (r.get("key"), hd["hd_key"], hd["hd_name"] or "?",
                     hd["n_static"], hd["n_panel"]))
            if n < 2:
                for it in (hd.get("static_show_names") or []):
                    print("        %-12s %-26s %s"
                          % (it["id"],
                             it.get("name") or ("★未命名（%s）" % it["kind"]
                                                if it.get("kind") else "★无名字"),
                             it.get("via") or ""))
        if len(hrows) > 4:
            print("   …还有 %d 行（见 JSON 的 rows[].hd / hd_bridge）" % (len(hrows) - 4))
    # ★ 2026-09-30 修：**带名字版必须落盘**。
    #   上一版加「服型覆盖」时误删了这段 ⇒ `全量奖池链_*_带名字.json` 停在旧数据上
    #   （实测：文件里还是 66.5%、channel=None、星穹环冕显示「缺」，
    #    而命令实际已回填 67.3%）—— 产物比命令旧，是最容易误导人的那种错。
    out = Path(rep["out"])
    with_names = out.with_name(out.stem + "_带名字.json")
    with_names.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 带名字版 → %s" % with_names)
    if args.json is not None:
        PL.json_dump(rep, args.json)
    print()
    print("★ 命令内注：池成员（L2/L3）在客户端不可得 —— 唯一静态源是官方概率公示，"
          "用 `lottery prob` 看。")
    return 0


def cmd_lottery_hd(args) -> int:
    """★★ 活动展示道具（静态表 `common_hd_show_reward_data`）。

    ★★ 为什么必须单开（2026-09-30 用户当场纠正）：
      我一直按【池号 391831】找池成员，得出「客户端没有静态表、靠服务端下发」的结论 —— **错**。
      正确的键是【活动号】：`common_hd_show_reward_data` 行 key = 活动号（幻夜 = **3610**，
      与 `huodong_conf_data` 的行 key 同源），值 `show_item_ids` 是 jump 组 =
      该活动的**展示道具列表**。实测幻夜 = 9 件，含全部 4 件 `panel_show_item_ids`。
      ⇒ 教训：找成员表时，键可能是【活动号】而不是【池号】；按池号搜一轮 0 命中
        不等于「客户端没有」，要换键再搜。
    """
    from toolkit_core import lottery_chain as LC
    from toolkit_core import show_item_names as SN
    import struct as _struct

    key = str(args.key).strip()
    # ★ 2026-09-30：按层序取（不许硬拼某个 cdata 目录）—— overlay 优先，找不到才兜底
    from toolkit_core import table_locator as _TL
    p = _TL.best_table_path("common_hd_show_reward_data.py") or (
        LC.tree_cdata() / "common_hd_show_reward_data.py")
    if not p.is_file():
        print("[lottery hd-show] ✗ 找不到 %s" % p, file=sys.stderr)
        return 6
    M = LC._mods()
    fr, b = LC._frame(p)
    if not fr:
        print("[lottery hd-show] ✗ 表里没有合法 x{ 帧", file=sys.stderr)
        return 7
    body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
    cnt, _ = _struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    chs = p.with_name("common_hd_show_reward_data_chs.py")
    pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
    rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)

    target = None
    if key not in ("", "None", "-", "all", "list"):
        for r in rows:
            if str(r.get("key")) == key:
                target = r
                break
    if target is None:
        # ★ 不给活动号（或没匹配上）→ 列出全部：这张表就 36 行，是「活动 → 展示道具」的总表
        print("★ 活动展示道具表（common_hd_show_reward_data）全部 %d 行" % len(rows))
        print("   活动号        道具数   bg_id")
        for r in rows:
            v0 = r.get("values") or {}
            g = v0.get("show_item_ids")
            g = g[1] if isinstance(g, (list, tuple)) and len(g) > 1 else g
            n = 0
            if isinstance(g, str) and g.startswith("jump:"):
                try:
                    n = len(M["BT"].resolve_jump_group(blob, int(g.split(":")[1])) or [])
                except Exception:                                   # noqa: BLE001
                    n = 0
            bg = v0.get("bg_id")
            bg = bg[1] if isinstance(bg, (list, tuple)) and len(bg) > 1 else bg
            print("   %-13s %4d   %s" % (r.get("key"), n, bg))
        print()
        print("★ 用 `lottery hd-show <活动号>` 看某个活动的道具 + 名字。")
        if key not in ("", "None", "-", "all", "list"):
            print("（没有活动号 %s —— 上面选一个）" % key, file=sys.stderr)
            return 8
        return 0

    v = {k: (x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else x)
         for k, x in (target.get("values") or {}).items()}
    ids = []
    for f, x in v.items():
        if isinstance(x, str) and x.startswith("jump:"):
            try:
                ids += M["BT"].resolve_jump_group(blob, int(x.split(":")[1])) or []
            except Exception:                                       # noqa: BLE001
                pass

    csvn = LC._csv_names()
    if not SN.stats().get("exists"):
        SN.build(verbose=False)
    snmeta = SN.lookup(ids)
    print("★ 活动展示道具（源：41_还原树\\com\\cdata\\common_hd_show_reward_data.py）")
    print("   活动号 %s · bg_id=%s · 展示道具 %d 件" % (key, v.get("bg_id"), len(ids)))
    print()
    named = 0
    for i in ids:
        rec = LC.name_ids([i])[0]
        nm = rec.get("name")
        via = rec.get("via")
        if nm:
            named += 1
        label = nm or ("★未命名（%s）" % rec["kind"] if rec.get("kind") else "★无名字")
        print("   %-12d %-28s %s" % (i, label, via or ""))
    print()
    print("   命名 %d/%d" % (named, len(ids)))
    print("★ 口径：本表键是【活动号】（与 huodong_conf_data 同行号），不是 pool id —"
          " 按池号搜客户端是 0 命中，别据此说「没有静态表」。")
    if args.json is not None:
        PL.json_dump({"hd_key": key, "bg_id": v.get("bg_id"),
                      "items": [{"id": i,
                                 "name": (snmeta.get(i)[0][0] if snmeta.get(i)
                                          else (csvn[i][0] if i in csvn else None))}
                                for i in ids]}, args.json)
    return 0


def cmd_hotfix_apply(args) -> int:
    """[带 H] ★ 把一次热更【就地增补】到 41_还原树（架构改造 S3）。

    ★ 口径（2026-09-29 用户定）：
       热更拆包【不再产出自己的还原树】，而是按补丁清单在**全量还原树**上
       「增 / 删 / 补」，只出一份【补丁台账】。还原树始终只有一份（唯一权威）。

    两层来源：
      ① 资源层 `--from-tree <dir>`：某次热更已铺好的还原树（如交付里的 01_还原树）
      ② 脚本层 `--script-pack <npk>`：script.py314.lc.npk（需配索引定位行→路径）

    ★ 默认 `--dry-run` —— 想真写必须显式给 `--real`（防止误改唯一权威产物）。
    """
    from toolkit_core import restore_merge as RM
    from toolkit_core import paths as P

    tree = Path(args.tree) if getattr(args, "tree", None) else P.TREE_ROOT
    real = bool(getattr(args, "real", False))
    dry = not real
    out = Path(args.out) if getattr(args, "out", None) else (
        P.ANALYSIS_ROOT / ("热更就地增补_%s" % time.strftime("%Y%m%d_%H%M")))
    out.mkdir(parents=True, exist_ok=True)

    print("★ hotfix apply —— 热更就地增补到还原树")
    print("   还原树（唯一权威）：%s" % tree)
    print("   模式：%s" % ("★ DRY-RUN（不写）" if dry else "★ REAL（真写！）"))
    print()

    if not tree.is_dir():
        print("✗ 还原树不存在：%s" % tree, file=sys.stderr)
        return 2

    stats = []

    # ① 资源层
    src_tree = getattr(args, "from_tree", None)
    if src_tree:
        src_tree = Path(src_tree)
        if not src_tree.is_dir():
            print("✗ 资源层来源不存在：%s" % src_tree, file=sys.stderr)
            return 2
        print("── ① 资源层：%s" % src_tree)
        s = RM.merge_tree_dir(src_tree, tree, dry_run=dry, layer="资源层")
        stats.append(s)
        print("   扫 %d · 新增 %d · 覆盖 %d · 相同 %d · 失败 %d"
              % (s.scanned, s.added, s.updated, s.same, s.failed))
        for x in s.samples.get("added", [])[:8]:
            print("      + %s" % x)
        for x in s.samples.get("updated", [])[:8]:
            print("      ~ %s" % x)
        if s.errors:
            print("   ⚠ 错误 %d 条，前 3：%s" % (len(s.errors), s.errors[:3]))
        print()

    # ② 脚本层
    sp = getattr(args, "script_pack", None)
    if sp:
        sp = Path(sp)
        # ★ 2026-09-30 修：默认索引必须是【存在的】主索引。
        #   原默认 `30_分析/relic_index/relic_index.db` 不存在 ⇒ 直接崩栈。
        idx = Path(args.index_db) if getattr(args, "index_db", None) else (
            P.PROJECT_ROOT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3")
        cdir = getattr(args, "container_dir", None)
        print("── ② 脚本层：%s" % sp)
        print("   索引：%s（%s）" % (idx, "有" if idx.is_file() else "★ 缺"))
        if not idx.is_file():
            print("   ✗ 索引库不存在，无法定位行→路径。请用 --index-db 指定，"
                  "或先跑 `index build`。", file=sys.stderr)
            return 2
        names = {}
        nd = Path(args.dict_path) if getattr(args, "dict_path", None) else P.DEFAULT_NAMES_DICT
        if nd.is_file():
            import json as _json
            names = _json.loads(nd.read_text(encoding="utf-8"))
            print("   字典：%d 条" % len(names))
        _force = bool(getattr(args, "force", False))
        s2 = RM.merge_script_pack(sp, tree, idx, names, dry_run=dry,
                                  container_dir=cdir,
                                  container=getattr(args, "container", None),
                                  allow_suspicious=_force)
        # ★★ 2026-09-30 守卫：拒绝「几乎全在覆盖」的写入。
        #   实测（拿 Documents 热更包的差量块去比已合并的树）：
        #     扫 27,072 · 覆盖 25,511（94%）· 相同 19 · 失败 1,542
        #   根因：overlay 包里的条目很多是【差量块】（连 `x{` 表体都没有），
        #   而树里是【合并后的完整表】⇒ 整条替换＝把合并结果换成差量块 = 毁数据。
        #   判据用比例、不用绝对值：覆盖+失败占扫描数 >60% 就拒写。
        if not dry and not getattr(args, "force", False):
            pre = RM.merge_script_pack(sp, tree, idx, names, dry_run=True,
                                       container_dir=cdir,
                                       container=getattr(args, "container", None),
                                       allow_suspicious=_force)
            bad = (pre.same == 0 and (pre.added + pre.updated) > 0)
            ratio = (pre.updated + pre.failed) / max(pre.scanned, 1)
            if bad or ratio > 0.60:
                print("   ✗ 拒绝写入：预检 扫 %d · 新增 %d · 覆盖 %d · 相同 %d · 失败 %d"
                      "（覆盖+失败占 %.0f%%）" % (pre.scanned, pre.added, pre.updated,
                                                pre.same, pre.failed, 100 * ratio),
                      file=sys.stderr)
                print("     这通常意味着【把差量块当完整内容写】或容器选错 —— 会覆盖掉"
                      "合并好的正确内容。先看不加 --real 的 dry-run；确实要强写加 --force。",
                      file=sys.stderr)
                return 5
        stats.append(s2)
        print("   容器：%s" % (getattr(s2, "container", "") or "—"))
        print("   扫 %d · 有名 %d · 无名 %d" % (s2.scanned, s2.named, s2.unnamed))
        print("   新增 %d · 覆盖 %d · 相同 %d · 失败 %d · ★拒写(内容不像话) %d"
              % (s2.added, s2.updated, s2.same, s2.failed,
                 getattr(s2, "suspicious", 0)))
        if s2.errors:
            print("   ⚠ 错误 %d 条，前 3：%s" % (len(s2.errors), s2.errors[:3]))
        print()

    if not stats:
        print("✗ 两层来源都没给（--from-tree / --script-pack 至少给一个）", file=sys.stderr)
        return 2

    # ③ 台账
    led = RM.write_ledger(tree, stats, dry_run=dry, out_dir=out)
    print("★ 台账 → %s" % led)
    tot = {k: sum(getattr(s, k) for s in stats)
           for k in ("scanned", "added", "updated", "same", "failed")}
    print("★ 合计：扫 %d · 新增 %d · 覆盖 %d · 相同 %d · 失败 %d"
          % (tot["scanned"], tot["added"], tot["updated"], tot["same"], tot["failed"]))
    if dry:
        print()
        print("★ 这是 DRY-RUN，什么都没写。要真写请加 --real。")

    rep = {"kind": "hotfix", "action": "apply", "dry_run": dry,
           "tree": str(tree), "out": str(out), "ledger": str(led),
           "layers": [{"layer": s.layer, "source": s.source, "scanned": s.scanned,
                       "added": s.added, "updated": s.updated, "same": s.same,
                       "failed": s.failed, "named": s.named, "unnamed": s.unnamed,
                       "errors": s.errors[:5]} for s in stats],
           "total": tot}
    (out / "hotfix_apply.json").write_text(
        __import__("json").dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 报告 → %s" % (out / "hotfix_apply.json"))
    return 0


def cmd_hotfix(args) -> int:
    """[带 H] 热更线总入口：一条命令跑完全流程。

    六步：
      1 读客户端状态 → overlay 清单（本次热更改了哪些包）
      2 官方 CDN 下载（幂等）
      3 解包 + 用内容指纹索引定位到本地「容器+行号」
      4 官方版本清单元数据（version / CDN 目录 / 开关）
      5 官方 fid 级 diff（release vs playertest）
      6 综合报告落盘 + 人读摘要
    """
    import hashlib
    import time

    from toolkit_core import patch_overlay as PO

    t0 = time.time()
    sub = args.hotfix_command
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = {"kind": "hotfix", "action": sub, "out": str(out), "steps": {}}

    def _log(msg):
        if not args.quiet:
            print(msg, flush=True)

    # ── 1 清单
    _log("══ 【1/6】读客户端状态 → overlay 清单 ══")
    try:
        st = PO.read_client_state(args.client_root)
        ol = PO.overlay_list(st)
        cdn_dir = PO.cdn_dir(st)
    except Exception as exc:
        print("hotfix：读客户端状态失败 %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1
    rep["steps"]["1_list"] = {"client_root": str(args.client_root), "cdn_dir": cdn_dir,
                              "timestamp": ol["timestamp"], "n": ol["n"],
                              "bytes": sum(p["size"] or 0 for p in ol["packages"]),
                              "packages": ol["packages"]}
    _log("  时间戳 %s ｜ %d 个包 ｜ %.1f MB"
         % (ol["timestamp"], ol["n"], rep["steps"]["1_list"]["bytes"] / 1048576))

    names = [p["name"] for p in ol["packages"]]
    pkg_dir = out / "pkgs"

    # ── 2 下载（report 模式跳过）
    if sub == "all":
        _log("══ 【2/6】官方 CDN 下载（幂等）══")
        try:
            fr = PO.fetch(cdn_dir, names, pkg_dir, timeout=args.timeout, quiet=args.quiet)
        except Exception as exc:
            print("hotfix：下载失败 %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
            return 1
        rep["steps"]["2_fetch"] = {"n": fr["n"], "bytes": fr["bytes"],
                                   "failed": fr["failed"], "out_dir": fr["out_dir"]}
        _log("  ✓ %d 个 / %.1f MB ｜ 失败 %d"
             % (fr["n"], fr["bytes"] / 1048576, len(fr["failed"])))
    else:
        rep["steps"]["2_fetch"] = {"skipped": True}

    # ── 3 解包 + 定位
    _log("══ 【3/6】解包 + 定位到本地「容器+行号」══")
    try:
        from toolkit_core import content_index as CI
        idx_db = PROJECT_ROOT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3"
        rows = []
        tot_blk = tot_hit = 0
        for p in sorted(pkg_dir.glob("*.npk")) if pkg_dir.is_dir() else []:
            u = PO.unpack_frames(p.read_bytes())
            if not u["n_decoded"]:
                rows.append({"pkg": p.name, "frames": u["n_frames"], "blocks": 0, "hits": 0})
                continue
            md5s = [hashlib.md5(b).hexdigest() for b in u["pieces"]]
            hit = CI.lookup_many(str(idx_db), md5s)
            n = sum(1 for m in md5s if m in hit)
            conts = {}
            for m, lst in hit.items():
                for c, ri, sz in lst:
                    k = Path(c.replace("\\", "/")).stem
                    conts[k] = conts.get(k, 0) + 1
            tot_blk += len(md5s)
            tot_hit += n
            rows.append({"pkg": p.name, "frames": u["n_frames"], "decoded": u["n_decoded"],
                         "blocks": len(md5s), "hits": n,
                         "bad_frames": len(u.get("bad_frames") or []),
                         "containers": conts})
        rep["steps"]["3_locate"] = {"total_blocks": tot_blk, "total_hits": tot_hit,
                                    "by_pkg": rows}
        _log("  ★ %d 块 / 命中 %d（%.1f%%）"
             % (tot_blk, tot_hit, 100.0 * tot_hit / max(1, tot_blk)))
    except Exception as exc:
        print("hotfix：定位失败 %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        return 1

    # ── 4 官方元数据
    _log("══ 【4/6】官方版本清单元数据 ══")
    try:
        from toolkit_core import patch_delta as PD
        from toolkit_core import patch_pkg as PP
        doc = PD.load_cached(Path(args.cache) if args.cache else
                             (PROJECT_ROOT / "03_执行" / "10_索引" / "patch_manifests"),
                             args.entry) if getattr(args, "entry", None) else None
        if doc is None:
            doc = PD.fetch(args.entry or "release", timeout=30.0)
        cd = PP.cdn_dir_of(doc)
        rep["steps"]["4_meta"] = {"entry": args.entry or "release", "version": doc.get("version"),
                                  "cdn_dir": cd, "bc7_only": doc.get("bc7_only"),
                                  "use_overlay": doc.get("use_overlay"),
                                  "pkg_lst": PP.fetch_pkg_lst(cd, timeout=30.0) if cd else None}
        _log("  version=%s ｜ CDN=%s ｜ bc7_only=%s"
             % (doc.get("version"), cd, doc.get("bc7_only")))
    except Exception as exc:
        rep["steps"]["4_meta"] = {"error": "%s: %s" % (type(exc).__name__, exc)}
        _log("  ⚠ 官方元数据取不到：%s" % str(exc)[:70])

    # ── 5 fid 级 diff
    _log("══ 【5/6】官方 fid 级 diff ══")
    cache = Path(args.cache) if args.cache else \
        (PROJECT_ROOT / "03_执行" / "10_索引" / "patch_manifests")
    pdir = Path(args.pkg_cache) if getattr(args, "pkg_cache", None) else None
    if pdir and (pdir / "rel").is_dir() and (pdir / "pt").is_dir():
        try:
            d = PP.diff(pdir / "rel", pdir / "pt")
            rep["steps"]["5_diff"] = {"a_dir": d["a_dir"], "b_dir": d["b_dir"],
                                      "a_total": d["a_total"], "b_total": d["b_total"],
                                      "added_n": len(d["added"]), "removed_n": len(d["removed"]),
                                      "common_n": len(d["common"])}
            _log("  ★ 新增 %d ｜ 移除 %d ｜ 共有 %d"
                 % (len(d["added"]), len(d["removed"]), len(d["common"])))
        except Exception as exc:
            rep["steps"]["5_diff"] = {"error": str(exc)[:100]}
            _log("  ⚠ diff 失败：%s" % str(exc)[:70])
    else:
        rep["steps"]["5_diff"] = {"skipped": "未提供 --pkg-cache（含 rel/ pt/ 两版本 pkg_N.pi）"}
        _log("  ○ 跳过（未给 --pkg-cache）")

    # ── 6 报告
    rep["seconds"] = round(time.time() - t0, 1)
    rp = out / "hotfix_report.json"
    rp.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    _log("══ 【6/6】报告 → %s（%.1f 秒）══" % (rp, rep["seconds"]))
    _dump(rep, args.json)
    return 0


def cmd_content(args) -> int:
    """[横切] 内容指纹索引。"""
    from toolkit_core import content_index as CI

    sub = args.content_command
    db = Path(args.db) if getattr(args, "db", None) else \
        (PROJECT_ROOT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3")

    if sub == "build":
        root = Path(args.product_root) if args.product_root else \
            _default_product_root()
        sizes = None
        if args.sizes:
            sizes = {int(x) for x in args.sizes.split(",") if x.strip()}
        rep = CI.build(db, root, args.container, workers=args.workers,
                       want_sizes=sizes, quiet=args.quiet)
        rep.update({"kind": "content", "action": "build", "db": str(db)})
        _dump(rep, args.json)
        return 0

    if sub == "lookup":
        got = CI.lookup_many(db, args.md5)
        rep = {"kind": "content", "action": "lookup", "db": str(db),
               "queried": len(args.md5), "found": len(got),
               "result": {k: [{"container": c, "row": r, "size": s} for c, r, s in v]
                          for k, v in got.items()}}
        _dump(rep, args.json)
        if not args.quiet:
            for m in args.md5:
                v = got.get(m)
                print("  %s  →  %s" % (m, v if v else "未命中"))
        return 0 if got else 5

    if sub == "stats":
        rep = CI.stats(db)
        rep.update({"kind": "content", "action": "stats", "db": str(db)})
        _dump(rep, args.json)
        if not args.quiet:
            print("  索引 %d 行" % rep["rows"])
            for c, n in rep["by_container"]:
                print("    %-46s %d" % (c, n))
        return 0

    print("未知 content 子命令 %r" % sub, file=sys.stderr)
    return 2


def cmd_loose(args) -> int:
    """[H-2] 散文件层：解密 + 内容寻址。"""
    sub = args.loose_command

    if sub == "scan":
        root = Path(args.source_root).resolve()
        if not _under(root, LOOSE_ALLOWED_ROOTS):
            print("loose scan 拒绝执行：只允许读 E:\\mrzh（体验服）下的路径；"
                  "正式服安装目录与其它路径由治理边界禁读。", file=sys.stderr)
            return 2
        try:
            mod = _load_container_fmt("wpk_1dpw_decryptor")
            pf = None
            if getattr(args, "pkg_filter", None):
                pf = [int(x) for x in str(args.pkg_filter).replace(",", " ").split() if x]
            ok, fail = mod.batch_decrypt_wpk(str(root), str(args.out),
                                             pkg_filter=pf, max_count=0)
        except Exception as exc:
            print("loose scan 失败：%s: %s" % (type(exc).__name__, exc), file=sys.stderr)
            return 1
        rep = {"kind": "loose", "action": "scan", "segment": "H-2",
               "source_root": str(root), "out": str(args.out),
               "success": ok, "failed": fail}
        _dump(rep, args.json)
        return 0

    if sub == "match":
        import hashlib
        import sqlite3

        d = Path(args.dir)
        if not d.is_dir():
            print("loose match：目录不存在 %s" % d, file=sys.stderr)
            return 6
        db_path = Path(args.db) if args.db else DEFAULT_DB
        if not db_path.is_file():
            print("loose match：索引不可用 %s" % db_path, file=sys.stderr)
            return 3
        con = sqlite3.connect("file:%s?mode=ro" % db_path.as_posix(), uri=True)

        targets = {}
        for p in sorted(d.iterdir()):
            if p.is_file() and p.suffix.lower() != ".json":
                b = p.read_bytes()
                targets[hashlib.md5(b).hexdigest()] = {"file": p.name, "size": len(b)}
        if not targets:
            print("loose match：%s 下没有解密产物（先跑 loose scan）" % d, file=sys.stderr)
            return 5

        sizes = sorted({v["size"] for v in targets.values()})
        qm = ",".join("?" * len(sizes))
        rows = con.execute(
            "SELECT container,row_index,decoded,fid_hex FROM entries WHERE decoded IN (%s)"
            % qm, sizes).fetchall()

        out_root = Path(args.product_root) if args.product_root else \
            _default_product_root()
        # ★★ 2026-09-30 修（真 bug，会静默 0 命中）：
        #   原实现按【初拆载荷铺法】找文件 —— `out_root/<容器stem>/<8位行号>.bin`。
        #   而 S5 已把载荷删掉、`out_root` 现在是**还原树**（路径树，不是行号铺法）
        #   ⇒ `_dir_cache[stem]` 恒为空 ⇒ tasks 空 ⇒ `实算 MD5 0 · 命中 0`，
        #   而且**不报错**（本次实测就是这么得到 0 的）。
        #   改走 `TreeResolver`（查 S1 的 row_path_map sidecar，容器+行号 → 树路径），
        #   与 `artifact_locator` / `container_probe` 同一条链。
        from toolkit_core import artifact_locator as _AL
        _tres = _AL.TreeResolver()
        if not _tres.available:
            print("loose match：TreeResolver 不可用（缺 row_path_map 或还原树）—— "
                  "先跑 `build_row_path_map.py`；本命令不再按载荷铺法找文件。",
                  file=sys.stderr)

        def _product_of(cont: str, ri: int):
            return _tres.path(cont, ri)

        # ★ 接资源调度：算 2.4 万个文件的 MD5 是典型 CPU 密集活，单线程太慢。
        #   走与 bulk / decode-audit 同一套（toolkit_core.throttle），
        #   并行预算 = 核数 × --cpu-limit%，跑动中按实测负载反馈让路。
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from toolkit_core.throttle import LoadGate, LoadPolicy, cpu_count

        pol = LoadPolicy(cpu_limit=args.cpu_limit, gpu_limit=args.gpu_limit,
                         kinds=("decode",))
        n_workers = args.workers or pol.workers()
        gate = LoadGate(pol, every=max(1, len(rows) // 12))
        if not args.quiet:
            print("  [调度] 核数 %d · CPU 上限 %.0f%% ⇒ 并行 %d%s"
                  % (cpu_count(), pol.cpu_limit, n_workers,
                     "" if pol.gpu_applicable() else " · GPU 不适用（解码线不碰 GPU）"),
                  file=sys.stderr)

        tasks = []
        for cont, ri, de, fid in rows:
            fp = _product_of(cont, ri)
            if fp is not None:
                tasks.append((cont, ri, de, fid, fp))

        def _one(item):
            cont, ri, de, fid, fp = item
            try:
                return (hashlib.md5(fp.read_bytes()).hexdigest(), cont, ri, de, fid)
            except OSError:
                return (None, cont, ri, de, fid)

        hits, checked = [], 0
        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            futs = [ex.submit(_one, t) for t in tasks]
            for fut in as_completed(futs):
                checked += 1
                gate.tick(checked)
                h, cont, ri, de, fid = fut.result()
                if h and h in targets:
                    hits.append({"md5": h, "target": targets[h], "container": cont,
                                 "row": ri, "decoded": de, "fid": fid})

        rep = {"kind": "loose", "action": "match", "segment": "H-2",
               "dir": str(d), "targets": len(targets),
               "size_candidates": len(rows), "md5_checked": checked,
               "hits_n": len(hits), "hits": hits,
               "policy": pol.snapshot(), "workers": n_workers,
               "throttle": gate.summary()}
        if args.json:
            _dump(rep, args.json)
        if not args.quiet:
            print("  目标 %d · 尺寸候选 %d 行 · 实算 MD5 %d · ★ 命中 %d"
                  % (len(targets), len(rows), checked, len(hits)))
            for h in hits[:args.limit]:
                print("    %-12s %8d B → %s r%s" % (
                    h["target"]["file"][:12], h["target"]["size"],
                    h["container"], h["row"]))
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(json.dumps(rep, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
            if not args.quiet:
                print("  完整报告 → %s" % args.out)
        return 0

    print("未知 loose 子命令 %r" % sub, file=sys.stderr)
    return 2


# ═══════════════════════════════════════════════════════════════════════════
# 批量能力（半全量跑出来的 9 条需求的落点）
# ═══════════════════════════════════════════════════════════════════════════

def _mk_filter(a) -> "object":
    from toolkit_core.bulk import Filter
    rr = None
    if getattr(a, "row", None):
        lo, _, hi = str(a.row).partition(":")
        rr = (int(lo), int(hi) if hi else int(lo))
    return Filter(
        containers=tuple(a.container or ()),
        flags=tuple(a.flag or ()),
        kinds=tuple(a.kind or ()),
        min_size=a.min_size, max_size=a.max_size,
        row_range=rr,
        fids=tuple(a.fid or ()),
        sample_per_container=a.per_container,
        percent=a.percent, limit=a.limit,
    )


def _add_filter_args(sp) -> None:
    sp.add_argument("--container", action="append", help="容器名子串（可多次，任一命中）")
    sp.add_argument("--flag", action="append", type=int, help="按 flag 筛（0原始/2lz4/12zstd）")
    sp.add_argument("--kind", action="append", choices=["gpk", "fpk", "npk"])
    sp.add_argument("--min-size", type=int, help="解压后大小下限（字节）")
    sp.add_argument("--max-size", type=int, help="解压后大小上限（字节）")
    sp.add_argument("--row", help="条目号范围，如 1000:2000（单值也可）")
    sp.add_argument("--fid", action="append", help="指定 16 位 hex fid（可多次）")
    sp.add_argument("--per-container", type=int, help="每容器最多取 N 条")
    sp.add_argument("--percent", type=float, help="按百分比均匀取（0-100，可复现）")
    sp.add_argument("--limit", type=int, help="总条数上限")


def cmd_query(args) -> int:
    """只筛不落盘 —— 先看清样本形状，再决定抽多少（避免「跑一半发现磁盘不够」）。"""
    from toolkit_core import bulk
    f = _mk_filter(args)
    with _open(args) as index:
        rows = bulk.select(index.conn, f)
        out = {"filter": f.describe(), "count": len(rows),
               "bytes_packed": sum(r[4] or 0 for r in rows),
               "bytes_decoded": sum(r[5] or 0 for r in rows)}
        if args.by:
            out["summary"] = bulk.summarize(rows, by=args.by)
        if args.show:
            out["head"] = [dict(zip(bulk.COLS, r)) for r in rows[: args.show]]
    if args.json:
        _dump(out, args.json)
    else:
        print("[query] %s" % out["filter"])
        print("  条目 %d · packed %.2f GB · decoded %.2f GB"
              % (out["count"], out["bytes_packed"] / 2**30, out["bytes_decoded"] / 2**30))
        s = out.get("summary")
        if s:
            print("  按 %s 分组：" % s["by"])
            for k, v in sorted(s["groups"].items(), key=lambda x: -x[1]["count"])[:20]:
                print("    %-42s %8d 条  %8.1f MB" % (k[-42:], v["count"], v["decoded"] / 2**20))
        for r in out.get("head", [])[:8]:
            print("    %-32s row %-8d %10.1f KB flag %s" %
                  (r["container"][-32:], r["row_index"], (r["decoded"] or 0) / 1024, r["flag"]))
    return 0


def cmd_bulk(args) -> int:
    """批量提取：断点续跑 + 清单 + 类型识别 + 错误聚合 + 慢条目。"""
    from toolkit_core import bulk
    from toolkit_core.unified_index import load_verified_index_module
    f = _mk_filter(args)
    UM = load_verified_index_module()
    out_root = Path(args.out).resolve()
    from toolkit_core.throttle import LoadPolicy, cpu_count, gpu_percent
    _pol = LoadPolicy(cpu_limit=args.cpu_limit, gpu_limit=args.gpu_limit, kinds=("decode",))
    print("[bulk] 资源策略：核数 %d · CPU 上限 %.0f%% ⇒ 并行 %d · GPU 上限 %.0f%%（本任务%s用 GPU）"
          % (cpu_count(), _pol.cpu_limit, _pol.workers(), _pol.gpu_limit,
             "会" if _pol.gpu_applicable() else "不"))

    def prog(d):
        if args.progress == "json":
            print(json.dumps({"progress": d}, ensure_ascii=False), flush=True)
        else:
            print("  %6d/%d  已出 %d 个  %.1f MB  %.0f 条/s  %.1f MB/s"
                  % (d["done"], d["total"], d["extracted"], d["bytes"] / 2**20,
                     d["rate_rows_s"], d["rate_MB_s"]), flush=True)

    with _open(args) as index:
        rep = bulk.bulk_extract(
            index.conn, Path(args.res_root or DEFAULT_RES_ROOT), f, out_root,
            unpack=UM.unpack_entry, name_by=args.name_by,
            resume=args.resume, manifest=Path(args.manifest) if args.manifest else None,
            progress=(prog if not args.quiet else None),
            decode=not args.raw, policy=_pol, workers=args.workers)

    d = rep.as_dict()
    if args.json:
        _dump(d, args.json)
    print("[bulk] %s" % f.describe())
    print("  选中 %d · 提取 %d%s · 输出 %.2f GB"
          % (rep.selected, rep.extracted,
             ("（续跑跳过 %d）" % rep.skipped_resume) if rep.skipped_resume else "",
             rep.bytes_out / 2**30))
    print("  耗时：选择 %.2fs · 读 %.2fs · 解码 %.2fs · 写 %.2fs · 合计 %.2fs"
          % (rep.seconds_select, rep.seconds_read, rep.seconds_decode,
             rep.seconds_write, rep.seconds_total))
    if rep.signatures:
        print("  产物类型：")
        for k, v in sorted(rep.signatures.items(), key=lambda x: -x[1]):
            print("    %-12s %6d" % (k, v))
    if rep.errors:
        print("  ★ 错误（按类别聚合）：")
        for k, v in sorted(rep.errors.items(), key=lambda x: -x[1]):
            print("    %-22s %6d" % (k, v))
            for s in rep.error_samples.get(k, [])[:2]:
                print("        %s" % s)
    if rep.slow:
        print("  ★ 最慢条目：")
        for s in rep.slow[:5]:
            print("    %6.3fs  %-34s row %-8d decoded %7.1f MB flag %s"
                  % (s["seconds"], s["container"][-34:], s["row"],
                     s["decoded"] / 2**20, s["flag"]))
    if args.manifest:
        print("  清单 → %s（%d 条）" % (args.manifest, len(rep.files)))
    return 0 if not rep.errors else 1


def cmd_identify(args) -> int:
    """产物类型识别：一堆 bytes 里认出纹理/配置/网格/音频。"""
    from toolkit_core import bulk
    paths: list[Path] = []
    for pat in args.target:
        p = Path(pat)
        if p.is_dir():
            paths += sorted(x for x in p.rglob("*") if x.is_file())
        elif p.is_file():
            paths.append(p)
        else:
            paths += sorted(Path().glob(pat))
    if args.from_manifest:
        for ln in Path(args.from_manifest).read_text(encoding="utf-8").splitlines():
            if ln.strip():
                paths.append(Path(json.loads(ln)["file"]))

    agg: dict[str, dict] = {}
    rows = []
    for p in paths[: args.limit or 10 ** 9]:
        try:
            head = p.read_bytes()[:4096]
        except OSError:
            continue
        short, desc = bulk.identify(head)
        a = agg.setdefault(short, {"n": 0, "bytes": 0, "desc": desc, "eg": []})
        a["n"] += 1
        a["bytes"] += p.stat().st_size
        if len(a["eg"]) < 2:
            a["eg"].append(p.name)
        rows.append({"file": str(p), "type": short, "desc": desc})
    out = {"scanned": len(rows), "types": agg}
    if args.json:
        _dump(out, args.json)
    print("[identify] 扫了 %d 个文件" % len(rows))
    for k, v in sorted(agg.items(), key=lambda x: -x[1]["n"]):
        print("  %-10s %6d 个 %10.2f MB   %s" % (k, v["n"], v["bytes"] / 2**20, v["desc"]))
        for e in v["eg"]:
            print("        eg. %s" % e)
    return 0


# ═══════════════════════════════════════════════════════════════════════════
# 从 run_all.py 收编的兼容命令（命令定义单点化，见 规范/CLI与EXE统一方案.md）
# ═══════════════════════════════════════════════════════════════════════════

def _toolkit_root() -> Path:
    """工具库根：向上搜索（判据：含 00_共享核心/工具库 结构），不手算 parents[N]。"""
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_共享核心").is_dir() and (up / "01_解码定位复原").is_dir():
            return up
    raise RuntimeError("找不到工具库根（向上没有同时含 00_共享核心 与 01_解码定位复原 的目录）")


def _load_by_path(name: str, rel: str):
    import importlib.util
    p = _toolkit_root() / rel
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def cmd_overview(args) -> int:
    import struct
    print("== NPK 条目数 ==")
    R = _toolkit_root()
    mr = _load_by_path("npkr_ov", "01_解码定位复原/解包与扫描/npk_reader.py")
    docs, res = Path(r"E:/mrzh/Documents"), Path(r"E:/mrzh/res")
    missing = []
    for name in ("script.npk", "script.py3.npk", "script.py314.lc.npk"):
        p = docs / name
        if p.exists():
            with p.open("rb") as f:
                h = mr.aes_ecb(f.read(32))
                _r, magic, ver, _to, n = struct.unpack_from("<QIIII", h)
                print("  %s: %d entries (v%d)" % (name, n, ver) if magic == 0x4B50584E else "  %s: 不可读" % name)
        else:
            missing.append(name)
    for name in ("res.npk", "ui.npk"):
        p = res / name
        if not p.exists():
            p = Path(r"E:/mrzh") / name
        if p.exists():
            with p.open("rb") as f:
                h = mr.aes_ecb(f.read(32))
                _r, magic, ver, _to, n = struct.unpack_from("<QIIII", h)
                print("  %s: %d entries (v%d)" % (name, n, ver) if magic == 0x4B50584E else "  %s: 不可读" % name)
        else:
            missing.append(name)
    newp = sorted(res.glob("ui_*.gpk"))
    if (res / "res.gpk").is_file():
        newp.append(res / "res.gpk")
    if newp:
        print("  新版多包容器（GPK，非 NPK 条目表）：%d 个" % len(newp))
        for p in newp[:6]:
            print("    %s  %s B" % (p.name, format(p.stat().st_size, ",")))
        if len(newp) > 6:
            print("    … 另 %d 个" % (len(newp) - 6))
    if missing:
        print("  ★ 以下旧包名已不存在（新版客户端已改名/拆包），非错误：")
        print("     " + " / ".join(missing))
    print("\n== FPK 包分类（前 8MB 扫描）==")
    _load_by_path("fpk_ov", "01_解码定位复原/容器格式/fpk_toolkit.py").cmd_overview()
    return 0


def cmd_restore(args) -> int:
    print("== 文件名还原（配置表 → path_id → ui.npk）==")
    _load_by_path("fr_rs", "01_解码定位复原/名字还原/filename_restore.py").main()
    return 0


def cmd_thfb(args) -> int:
    print("== THFB 哈希提取 ==")
    _load_by_path("th_tf", "01_解码定位复原/哈希提取/thfb_toolkit.py").main()
    return 0


def cmd_bridge_audit(args) -> int:
    print("== 皮肤逻辑路径 → IDX/WPK 物理桥审计 ==")
    _load_by_path("bridge", "00_共享核心/独立工具/physical_bridge_audit.py").main([])
    return 0


def cmd_bindict_check(args) -> int:
    print("== BinDict 自检 ==")
    import runpy
    base = _toolkit_root() / "01_解码定位复原" / "表解码"
    for script in ("bindict_attrs_decoder.py", "bindict_kj1_transfer_decoder.py"):
        p = base / script
        if p.exists():
            print("-- %s --" % script)
            try:
                runpy.run_path(str(p), run_name="__check__")
            except Exception as e:
                print("  ERR %r" % e)
    return 0


def cmd_decode_audit(args) -> int:
    """解码线体检：每个【容器 × flag】分层抽样，判据不带盲区。

    ★ 关键判据「解码毁内容」：原始载荷认出格式、解码后认不出 ⇒ 致命。
       这正是 A38（flag 0 把 GPK 明文 AES 毁掉，274,295 条）逃过上一轮测试的原因 ——
       上一轮只按容器抽样、且长度判据对 flag 0（decoded==packed）完全失效。
    """
    from toolkit_core import decode_audit
    from toolkit_core.throttle import LoadPolicy, cpu_count, gpu_percent
    from toolkit_core.unified_index import load_verified_index_module
    UM = load_verified_index_module()
    pol = LoadPolicy(cpu_limit=args.cpu_limit, gpu_limit=args.gpu_limit, kinds=("decode",))
    print("[decode-audit] 资源策略：核数 %d · CPU 上限 %.0f%% ⇒ 并行 %d · GPU 上限 %.0f%%（本任务%s用 GPU，%s）"
          % (cpu_count(), pol.cpu_limit, pol.workers(), pol.gpu_limit,
             "会" if pol.gpu_applicable() else "不",
             ("实测 GPU %.0f%%" % gpu_percent()) if gpu_percent() is not None else "GPU 计数不可用"))
    with _open(args) as index:
        rep = decode_audit.audit(
            index.conn, Path(args.res_root or DEFAULT_RES_ROOT), UM.unpack_entry,
            per_group=args.per_group, full=args.full, policy=pol,
            progress=(lambda d: print("  …%s" % json.dumps(d, ensure_ascii=False), flush=True)
                      if args.progress else None))
    out = rep.as_dict()
    if args.json:
        _dump(out, args.json)
    print("[decode-audit] 抽样 %d 条 · 用时 %.1fs · 覆盖 %d 个(容器×flag)组合"
          % (rep.sampled, rep.seconds, len(rep.per_container_flag)))
    print()
    print("  判据分布：")
    order = ["无变换直通", "解码有效", "两边都是内容", "中立（无魔数数据块）",
             "★解码毁内容", "★长度不符", "解码异常", "读取短读"]
    for k in order:
        if k in rep.verdicts:
            print("    %-22s %6d" % (k, rep.verdicts[k]))
    for k, v in rep.verdicts.items():
        if k not in order:
            print("    %-22s %6d" % (k, v))
    fatal = [b for b in rep.bad if b["verdict"].startswith("★")]
    print()
    if fatal:
        print("  ★★ 致命 %d 例（这就是「有纰漏」的定义）：" % len(fatal))
        seen = set()
        for b in fatal[:20]:
            k = (b.get("container"), b.get("flag"), b["verdict"])
            if k in seen:
                continue
            seen.add(k)
            print("    %-34s flag %-4s row %-8s %s" % (str(b.get("container"))[-34:],
                                                       b.get("flag"), b.get("row"), b.get("note", "")[:70]))
        uniq = len({(b.get("container"), b.get("flag"), b["verdict"]) for b in fatal})
        print("    … 去重后 %d 个(容器,flag,判据)组合" % uniq)
    else:
        print("  ✓ 无致命项（没有「解码毁内容」「长度不符」「异常」）")
    return 1 if fatal else 0


# ═══════════════════════════════════════════════════════════════════════════
# ①-4 名字还原（2026-09-27：双 seed murmur3 机制实测成立后落的命令）
#   旧结论「名字永久不可还原」只算了一条 seed；这里按验证过的三条规矩实现：
#     ① 包内相对路径原样拼（不剥前缀、不补容器名）
#     ② 算哈希前 / → \
#     ③ 先查索引 fid_hex 快路径；索引不在就明确报错，不静默降级
# ═══════════════════════════════════════════════════════════════════════════

def _names_json(payload: dict, dest) -> None:
    """--json：裸用打 stdout（机器读）；给了路径则同时落盘（D 契约带）。"""
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if dest and dest != "-":
        p = Path(dest).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        print("已写入：%s" % p, file=sys.stderr)
    print(text, end="")


def cmd_names_build(args) -> int:
    """从文本产物挖路径 → 建/扩字典（默认不覆盖已有输出）。"""
    from toolkit_core import names as N
    from toolkit_core.paths import DEFAULT_NAME_SOURCES
    srcs = [Path(s) for s in (args.source or DEFAULT_NAME_SOURCES)]
    try:
        rep = N.build(srcs, args.out, db=args.db, limit=args.limit,
                      workers=args.workers, force=args.force)
    except FileExistsError as exc:
        print("[names build] %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("[names build] 写不出字典：%s" % exc, file=sys.stderr)
        return 6

    if args.json:
        _names_json(rep, args.json)
    else:
        print("[names build] 开采 %d 个源 → 读成 %d 个文件 · 候选 %d 条 · 入库 %d 条"
              % (len(rep["sources"]), rep["files_read"], rep["candidates"], rep["kept"]))
        print("  字典 → %s（%s 字节）" % (rep["out"], format(rep.get("out_bytes", 0), ",")))
        h = rep.get("hits")
        if h:
            print("  索引命中 %d/%d（%.1f%%）· 覆盖 %d 个容器"
                  % (h["hit"], h["total"], 100 * (h["rate"] or 0), len(h["containers"])))
            for k, v in list(h["containers"].items())[:8]:
                print("    %-38s %6d 条" % (k[-38:], v))
        if rep["index_error"]:
            print("  ★ 索引不可用，未统计命中：%s" % rep["index_error"], file=sys.stderr)
        for s in rep["missing_sources"]:
            print("  ★ 开采源不存在：%s" % s, file=sys.stderr)
        if rep["file_errors"]:
            print("  ★ %d 个文件读不动：" % len(rep["file_errors"]), file=sys.stderr)
            for k, v in list(rep["file_errors"].items())[:5]:
                print("    %s：%s" % (k, v), file=sys.stderr)
        if not rep["kept"]:
            print("  ★ 一条路径都没挖到 —— 这个开采源里没有路径文本。", file=sys.stderr)
    if not rep["kept"] or rep["index_error"]:
        return 6 if not rep["kept"] else 1
    return 1 if (rep["missing_sources"] or rep["file_errors"]) else 0


def cmd_names_lookup(args) -> int:
    """★ 核心能力：一个游戏内路径 → 它在哪个包、哪一行。"""
    from toolkit_core import names as N
    try:
        rep = N.lookup(args.path, args.db, limit=args.limit)
    except N.IndexUnavailable as exc:
        print("[names lookup] 索引不可用：%s" % exc, file=sys.stderr)
        return 3
    except ValueError as exc:
        print("[names lookup] 用法错：%s" % exc, file=sys.stderr)
        return 2
    if args.json:
        _names_json(rep, args.json)
        return 0 if rep["found"] else 5
    print("[names lookup] %s" % rep["input"])
    print("  fid %s（%s）" % (rep["fid"], "按 16 位 fid 直查" if rep["mode"] == "fid"
                              else "路径 → murmur3 双 seed"))
    if rep["found"]:
        for h in rep["hits"]:
            print("  → %-34s row %-8d %s flag %s decoded %s"
                  % (h["container"], h["row_index"], h["kind"], h["flag"],
                     format(h["decoded"] or 0, ",")))
        print("  命中 %d 处" % len(rep["hits"]))
        return 0
    print("  未命中：索引 %s 条里没有 fid_hex = %s。"
          % (format(rep["index_rows"], ","), rep["fid"]))
    print("  如实说：这条路径当前【查不到】—— 要么它不在这个客户端，要么路径写法与包内不一致。")
    return 5


def cmd_names_stats(args) -> int:
    """字典规模 / 已命中多少条 / 各容器覆盖率排行（命中数现场查索引）。"""
    from toolkit_core import names as N
    try:
        rep = N.stats(args.dict_path, args.db)
    except N.IndexUnavailable as exc:
        print("[names stats] 索引不可用：%s" % exc, file=sys.stderr)
        return 3
    except (FileNotFoundError, ValueError) as exc:
        print("[names stats] %s" % exc, file=sys.stderr)
        return 6
    if args.json:
        _names_json(rep, args.json)
        return 0
    print("[names stats] 字典 %s" % rep["dict"])
    fmt = rep.get("dict_format", "flat")
    print("  规模 %s 条（fid 行口径）· 唯一路径 %s 条 · 格式 %s"
          % (format(rep["count"], ","),
             format(rep.get("unique_paths", rep["count"]), ","),
             "裸映射 {fid: 路径}" if fmt == "flat" else "带包装 {entries: {路径: fid}}"))
    print("  建于 %s · 源 %d 个"
          % (rep["built"] or "（裸映射格式无元信息）", len(rep["sources"])))
    print("  命中 %s 条 / 未命中 %s 条（%.1f%%）· 覆盖 %d 个容器 · 索引 %s 行"
          % (format(rep["hit"], ","), format(rep["miss"], ","),
             100 * (rep["rate"] or 0), rep["containers_covered"],
             format(rep["index_rows"], ",")))
    if rep["containers"]:
        print("  各容器覆盖率排行（字典里有多少条落在该容器）：")
        for k, v in list(rep["containers"].items())[:12]:
            print("    %-44s %6d 条" % (k[-44:], v))
    st = rep["selftest"]
    print("  哈希自检：%s（%d 项取样）" % ("通过" if st["ok"] else "不通过", st["checked"]))
    return 0 if st["ok"] else 1


# ═══════════════════════════════════════════════════════════════════════════
# 带 H · H-2：本地容器快照与终态判定（snapshot）
#   ★ 治理边界：只允许扫 E:\mrzh（体验服）；正式服 E:\LifeAfter 与其它路径一律拒绝。
#   ★ 默认【不读正式服】：默认根就是 E:\mrzh，且 _snapshot_guard() 会拒绝一切别处路径。
# ═══════════════════════════════════════════════════════════════════════════

def _snapshot_guard(root: Path) -> str | None:
    """只允许 E:\\mrzh 及其子目录；其它路径（含正式服 E:\\LifeAfter）一律拒绝。"""
    s = str(Path(root).resolve()).replace("/", "\\").rstrip("\\").lower()
    for base in SNAPSHOT_ALLOWED_ROOTS:
        if s == base or s.startswith(base + "\\"):
            return None
    return ("只允许扫 E:\\mrzh（体验服）。正式服安装目录 E:\\LifeAfter 与其它路径由治理边界禁读；"
            "要换路径先在 00_治理 侧登记。")


def _snapshot_root_of(path: Path) -> str:
    """只读前 2 KB 取快照的 root（避免为挑基线而整份读 1 MB 的 files 列表）。"""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2048]
    except OSError:
        return ""
    m = re.search(r'"root"\s*:\s*"((?:[^"\\]|\\.)*)"', head)
    if not m:
        try:
            return str(json.loads(path.read_text(encoding="utf-8")).get("root") or "")
        except (OSError, ValueError):
            return ""
    return m.group(1).replace("\\\\", "\\")


def _snapshot_runs(out_root: Path, *, root: str | None = None) -> list[Path]:
    """历史快照（out_root/*/source_lock.json），按 mtime 升序。

    ★ root 给定时只保留【同一源根】的快照 —— 否则会把「只扫了某个子目录」的快照
      当成基线，算出「全部新增」的假结论（--only 与全量扫描的相对路径基准不同）。
    """
    base = Path(out_root)
    if not base.is_dir():
        return []
    rows = []
    for p in base.glob("*/source_lock.json"):
        try:
            rows.append((p.stat().st_mtime, str(p), p))
        except OSError:
            continue
    rows.sort()
    out = [p for _m, _s, p in rows]
    if root:
        out = [p for p in out if _snapshot_root_of(p) == root]
    return out


def cmd_snapshot(args) -> int:
    """[H-2] 本地容器快照：两段式快扫 + 写入窗口守卫 + 与基线比内容。

    分两个动作：
      scan  廉价 stat 扫 → 只对候选算 sha256（算完回读 stat，一致才算终态）→ 落盘
      diff  两次快照按内容比，mtime-only 变化单列（永不作为更新证据）
    """
    try:
        from toolkit_core import patch_snapshot as PS
        from toolkit_core import source_lock as SL
    except Exception as exc:
        print("snapshot 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5

    out_root = Path(args.out) if getattr(args, "out", None) else SNAPSHOT_OUT_ROOT
    sub = args.snapshot_command
    # 裸用 --json（打 stdout）时自动静音进度，否则 stdout 会混进进度行
    quiet = bool(getattr(args, "quiet", False) or args.json == "-")

    if sub == "scan":
        root = Path(getattr(args, "source_root", None) or DEFAULT_SNAPSHOT_ROOT)
        if args.only:
            root = root / args.only
        bad = _snapshot_guard(root)
        if bad:
            print("snapshot scan 拒绝执行：%s" % bad, file=sys.stderr)
            return 2
        if not root.is_dir():
            print("snapshot scan：目录不存在：%s" % root, file=sys.stderr)
            return 6
        runs = _snapshot_runs(out_root, root=str(root.resolve()))   # 只认同源根的基线

        suffixes = None
        if args.suffix:
            suffixes = [s if s.startswith(".") else "." + s for s in args.suffix]

        baseline: Path | None = None
        if args.baseline and args.baseline != "auto":
            baseline = Path(args.baseline)
            if not baseline.is_file():
                print("snapshot scan：基线不存在：%s" % baseline, file=sys.stderr)
                return 6
        elif args.only:
            # --only 的相对路径以子目录为基准 ⇒ 与全量基线不可比，故意不自动取基线
            print("snapshot scan：--only 模式不自动取基线（相对路径基准不同）；"
                  "要与某次基线比请显式 --baseline。", file=sys.stderr)
        elif runs and not args.no_baseline:
            baseline = runs[-1]
            if not quiet:
                print("snapshot scan：基线 = 最近一次快照 %s" % baseline)

        res = PS.lock(root, baseline_path=baseline, suffixes=suffixes,
                      include_all=args.all_files, quiet=quiet,
                      progress=(None if quiet else
                                (lambda i, n: print("      …%d/%d" % (i, n), flush=True))))
        snap, delta = res["snapshot"], res.get("delta") or {}
        out_dir = out_root / _stamp()
        paths = PS.write_run(res, out_dir)
        report = {
            "kind": "snapshot", "action": "scan", "segment": "H-2",
            "root": snap["root"], "out": str(out_dir),
            "files": len(snap["files"]), "unstable": len(snap["unstable"]),
            "seconds": res["seconds"],
            "baseline": str(baseline) if baseline else None,
            "candidates": res.get("candidates"),
            "suffixes": sorted(suffixes) if suffixes else "默认容器后缀",
            "delta_totals": {k: len(v) for k, v in delta.items() if isinstance(v, list)},
            "written": {k: str(v) for k, v in paths.items()},
            "conclusion_boundary": ("mtime 变化不是内容变化；unstable（写入窗口内 stat 变化）"
                                    "的文件被排除出内容结论。"),
        }
        if args.json:
            _dump(report, args.json)
            return 1 if snap["unstable"] else 0
        print("[snapshot scan] %s → %s" % (snap["root"], out_dir))
        print("  文件 %d 个 %s · 不稳定 %d 个 · 用时 %.1fs"
              % (len(snap["files"]),
                 "（后缀 %s）" % "/".join(sorted(suffixes)) if suffixes else "（默认容器后缀）",
                 len(snap["unstable"]), res["seconds"]))
        if delta:
            t = report["delta_totals"]
            print("  与基线比（按内容）：新增 %d · 消失 %d · 内容变更 %d · 未变 %d ｜ mtime-only %d"
                  % (t.get("content_added", 0), t.get("content_removed", 0),
                     t.get("content_changed", 0), t.get("content_unchanged", 0),
                     t.get("mtime_only_changed", 0)))
        else:
            print("  无基线 ⇒ 本次是全量基线（下次 scan 会自动与它比）")
        for u in snap["unstable"][:3]:
            print("  ★ 不稳定：%s（%s）" % (u["relative_path"], u["note"]))
        print("  落盘：%s" % " · ".join(sorted(p.name for p in paths.values())))
        return 1 if snap["unstable"] else 0

    # ── diff ──
    allruns = _snapshot_runs(out_root)
    c = Path(args.current) if args.current else None
    if c is None:
        # auto：挑「最近一次且它有同源根的上一次」的那一份（避免选中孤零零的 --only 快照）
        for cand in reversed(allruns):
            w = _snapshot_root_of(cand)
            if any(_snapshot_root_of(p) == w and p.resolve() != cand.resolve() for p in allruns):
                c = cand
                break
        if c is None and allruns:
            c = allruns[-1]
    b = None
    if args.baseline and args.baseline != "auto":
        b = Path(args.baseline)
    elif c is not None:                       # auto：同一源根的上一次
        want = _snapshot_root_of(c)
        same = [p for p in allruns
                if _snapshot_root_of(p) == want and p.resolve() != c.resolve()]
        b = same[-1] if same else None
    if b is None or c is None or not Path(b).is_file() or not Path(c).is_file():
        print("snapshot diff：需要两次【同一源根】的快照（或显式 --baseline/--current）。"
              "快照根：%s" % out_root, file=sys.stderr)
        print("  先跑：run_all.py snapshot scan --only <小目录>，再跑一次即有两份。",
              file=sys.stderr)
        return 6
    base, cur = SL.read_snapshot(b), SL.read_snapshot(c)
    if base.get("root") != cur.get("root"):
        print("snapshot diff 拒绝比较：两次快照的 root 不同（相对路径基准不同）\n"
              "  基线 %s ← %s\n  当前 %s ← %s"
              % (b, base.get("root"), c, cur.get("root")), file=sys.stderr)
        return 2
    delta = SL.compare_snapshots(base, cur)
    lim = max(0, int(args.limit))
    report = {
        "kind": "snapshot", "action": "diff", "segment": "H-2",
        "baseline": str(b), "current": str(c), "root": cur.get("root"),
        "totals": {k: len(v) for k, v in delta.items()},
        "content_added": delta["content_added"][:lim],
        "content_removed": delta["content_removed"][:lim],
        "content_changed": delta["content_changed"][:lim],
        "mtime_only_changed": delta["mtime_only_changed"][:lim],
        "conclusion_boundary": "只有 content_* 是更新证据；mtime_only_changed 只作诊断。",
    }
    if args.json:
        _dump(report, args.json)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(
            {"baseline": str(b), "current": str(c), "root": cur.get("root"),
             "totals": report["totals"], "delta": delta},
            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if not quiet:
        print("[snapshot diff] %s → %s" % (b.parent.name, c.parent.name))
        print("  内容：新增 %d · 消失 %d · 变更 %d · 未变 %d"
              % (len(delta["content_added"]), len(delta["content_removed"]),
                 len(delta["content_changed"]), len(delta["content_unchanged"])))
        print("  mtime-only（诊断，不算更新）：%d" % len(delta["mtime_only_changed"]))
        for label, key in (("新增", "content_added"), ("消失", "content_removed"),
                           ("变更", "content_changed")):
            for p in delta[key][:lim]:
                print("    %s %s" % (label, p))
        if args.out:
            print("  完整报告 → %s" % args.out)
    return 0


def _artifact_locator():
    """产物定位器（统一「容器+行号 → 产物路径」，禁再各写 glob）。"""
    from toolkit_core import artifact_locator as AL
    return AL.Locator()


def _default_product_root():
    """★ 产物根的智能默认值：载荷在就用载荷，已清则回退还原树。

    统一在这里，避免各命令自己拼 `20_提取/.../files` —— 载荷被清后那种拼法
    会指向不存在的目录，命令静默返回 0 结果（比报错危险）。
    """
    try:
        from toolkit_core import artifact_locator as AL
        return AL.default_product_root()
    except Exception:
        from toolkit_core.paths import TREE_ROOT
        return TREE_ROOT


# ══════════════════════════════════════════════════════════════════
# tables —— 配置表层（com\cdata\ 下的表）
#   ★ 关键事实：表里字符串是 UTF-16LE，不是 UTF-8（UTF-8 扫会 0 命中）
#   ★ 关键事实：npk 容器的 fid ≠ murmur3(路径)，必须用名字字典自带的 fid
# ══════════════════════════════════════════════════════════════════

_TABLE_CATS = {
    "奖池抽奖": r"lottery|gacha|choujiang|zhuanpan|dajiang",
    "活动": r"huodong|activity|jixun|xunbao|tiaozhan|shengcunfu",
    "时装": r"shizhuang|fashion|diancang|gexing|makeup",
    "商店付费": r"shop|mall|shangcheng|paid|pay|gift|box",
    "文字提示": r"text|tips|notice|msg|desc|title|name",
}


def _table_cat(path: str) -> str:
    import re as _re
    for k, rx in _TABLE_CATS.items():
        if _re.search(rx, path, _re.I):
            return k
    return "其它"


def _names_dict(path=None):
    import json as _json
    p = Path(path) if path else DEFAULT_NAMES_DICT
    if not p.is_file():
        raise SystemExit("[tables] 名字字典不存在：%s" % p)
    with p.open(encoding="utf-8") as fh:
        return _json.load(fh)


def _load_names_map(dict_path=None):
    """返回 {fid_hex: 路径}（npk 的文件只能用这个查，不能重算 fid）。

    ★ 走 names.fid_map：兼容「裸映射 {fid: 路径}」与「build 输出 {entries:{路径:fid}}」
      两种落盘格式。原先直接 json.load 返回裸 payload —— 喂进 build 出来的字典时，
      调用方拿到的是包装层（{version/built/...}），fid 一个都对不上。
    """
    from toolkit_core import names as _N
    return _N.fid_map(_names_dict(dict_path))


def _table_index(names_map, db_path, subdir="com\\cdata\\"):
    """{fid_hex: (container,row)}。
    ★ 按容器整拉，禁用 `IN (几千个占位符)` —— 会超 SQLite 变量上限而【静默 0 命中】。
    ★ 只扫「可能含目标表的容器」：先按容器名粗筛，再逐行比对 fid。
    """
    import sqlite3
    db = sqlite3.connect("file:%s?mode=ro" % str(db_path).replace("\\", "/"), uri=True)
    want = {h for h, p in names_map.items()
            if isinstance(p, str) and p.replace("/", "\\").lower().startswith(subdir.lower())}
    out = {}
    for (c,) in db.execute("SELECT DISTINCT container FROM entries"):
        low = c.lower()
        # 表都在 script / cdata 类容器里；其余容器跳过（省大量扫描）
        if not any(k in low for k in ("script", "cdata", "py314", "core")):
            continue
        for f, r in db.execute("SELECT fid_hex,row_index FROM entries WHERE container=?", (c,)):
            if f in want:
                out[f] = (c, r)
    db.close()
    return out


_U16_CN = None


def _cn_re():
    """★ 中文串正则。

    实测结论（drinks_parameter_data_chs.py 等）：
      · 表里字符串是【UTF-8】普通编码 —— 不是 UTF-16
      · 之所以早期「UTF-8 扫 0 命中」，是因为用 path_fid 定位 npk 里的文件（定位全错）
      · .pyc 由 Python 3.13 编译（marshal 有 string_pool / TYPE_INTERNED 0xd3）
    """
    global _U16_CN
    if _U16_CN is None:
        import re as _re
        _U16_CN = _re.compile(rb"(?:[\xe4-\xe9][\x80-\xbf]{2}){2,}")
    return _U16_CN


def cmd_shader(args) -> int:
    """[④] 着色器层：`cc aa 55 66` = NeoX .pipe 编译着色器变体（内层标准 DXBC）。

    ★ 实证 2026-09-28：全库 122,459 个；本次热更无名块 10,733 里占 ~81%。
      外层 0x20 字节头 + N 个 blob（{u64 阶段, u64 长度} + DXBC）。
      ★ blob 个数无显式字段，靠链走到 EOF（300/300 精确自洽）。
    """
    from toolkit_core import shader_pipe as SP
    sub = getattr(args, "shader_command", None)

    if sub == "list":
        # ★ 路径不在 entries 表里（列只有 fid_hex/container/row_index/…），
        #   名字要查字典。索引库只用来数「有多少行落了名字」。
        names = _load_names_map(args.dict_path)
        by_top, exts = {}, {}
        named = 0
        for fid, nm in names.items():
            if not nm:
                continue
            low = nm.lower().replace("/", "\\")
            if not low.endswith(".ccaa5566"):
                continue
            named += 1
            top = low.split("\\")[0]
            by_top[top] = by_top.get(top, 0) + 1
        import sqlite3 as _sq
        db = _sq.connect("file:%s?mode=ro" % str(DEFAULT_DB).replace("\\", "/"), uri=True)
        total_rows = db.execute(
            "SELECT COUNT(*) FROM entries WHERE container LIKE '%effect_cache%' "
            "OR container LIKE '%gres\\\\0000%'").fetchone()[0]
        print("[shader] .ccaa5566 = NeoX .pipe 编译着色器变体（内层标准 DXBC）")
        print("  字典里有名字的: %d 个" % named)
        print("  effect_cache / gres\\0000 两个容器的总行数: %d" % total_rows)
        print("  按容器顶层分布 Top 12：")
        for k, v in sorted(by_top.items(), key=lambda x: -x[1])[:12]:
            print("    %-28s %7d" % (k, v))
        if args.json:
            _dump({"named": named, "by_top": by_top,
                   "effect_cache_rows": total_rows}, args.json)
        return 0

    if sub == "info":
        r = SP.parse_file(args.path)
        if not r.get("ok") and "header" not in r:
            print("[shader] %s" % r.get("error"))
            return 1
        h = r["header"]
        print("[shader] %s" % Path(args.path).name)
        print("  文件 %d B ｜ 版本 %d ｜ [0x04]=%d [0x08]=%d [0x0C]=%d ｜ 零填充 %s"
              % (h["size"], h["version"], h["f04"], h["f08"], h["f0c"],
                 "✓" if h["zeros_ok"] else "✗"))
        print("  blob %d 个：" % len(r["blobs"]))
        for m in r["blobs"]:
            ch = " ".join(c["tag"] for c in m.get("chunks", []))
            print("    #%d  %-8s %8d B  DXBC=%s  chunks=[%s]"
                  % (m["index"], m["stage_name"], m["size"],
                     "✓" if m["is_dxbc"] else "✗", ch))
        if args.json:
            _dump(r["blobs"], args.json)
        return 0

    if sub == "export":
        src = Path(args.path)
        files = []
        if src.is_dir():
            for f in sorted(src.rglob("*.ccaa5566"))[: args.limit]:
                files += SP.export(f, args.out, asm=args.asm, fxc=args.fxc)
        else:
            files = SP.export(src, args.out, asm=args.asm, fxc=args.fxc)
        print("[shader] 拆出 %d 个文件 → %s" % (len(files), args.out))
        for f in files[:12]:
            print("    %-52s %9d B" % (f.name, f.stat().st_size))
        if len(files) > 12:
            print("    … 另有 %d 个" % (len(files) - 12))
        return 0

    raise SystemExit("[shader] 未知子命令 %r（用 list / info / export）" % sub)


# ══════════════════════════════════════════════════════════════════
# lottery —— 奖池层（list 家底 / find 找池 / show 单池 / delta 本次热更）
#   数据源全部是既有产物，不重算任何表；池名只从已发布看板取，取不到写「未解」
# ══════════════════════════════════════════════════════════════════

_LOT_POOL_FIDS = {"D558884A36C972C5": "reward_pool_data（base 表体）",
                  "69E58821939CB515": "reward_pool_data（chs 文字池）"}
_LOT_TAB_RE = r"lottery|gacha|choujiang|zhuanpan|dajiang|reward_pool"


def _lot_paths() -> dict:
    """奖池层的四个数据源（全是既有产物；本命令不重算表）。"""
    from toolkit_core import paths as P
    site = P.INDEX_ROOT / "site_data"
    return {"pool": site / "LOTTERY_POOL_RESOLVED_v01.jsonl",
            "target": site / "LOTTERY_REWARD_TARGETS_v0.1.jsonl",
            "boards": P.PROJECT_ROOT / "04_站点" / "web" / "data" / "boards",
            "analysis": P.PROJECT_ROOT / "03_执行" / "30_分析"}


def _lot_lines(path: Path):
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                yield json.loads(s)


def _lot_pool_rows(path: Path, manifest_note: list | None = None):
    """LOTTERY_POOL_RESOLVED → 精简行（只留判据字段）。"""
    for d in _lot_lines(path):
        if d.get("record_type") == "dataset_manifest":
            if manifest_note is not None:
                manifest_note.append(d)
            continue
        lk = d.get("lookup_key") or {}
        st = d.get("static_projection") or {}
        rt = d.get("runtime_dispatch") or {}
        src = d.get("source") or {}
        yield {"pool": (lk.get("pool_key") or {}).get("value"),
               "slot": (lk.get("item_no") or {}).get("value"),
               "raw": list((d.get("static_config", {}).get("reward_raw") or {}).get("value") or []),
               "head": st.get("reward_head_raw"), "count": st.get("reward_second_raw"),
               "dispatch": st.get("static_dispatch_candidate"),
               "child": (rt.get("child_pool_key") or {}).get("value"),
               "component": src.get("component"), "channel": src.get("channel"),
               "reliability": src.get("reliability_state"),
               "partition": d.get("dataset_partition"),
               "tier": d.get("publication_tier"), "record_id": d.get("record_id")}


def _lot_target_rows(path: Path):
    for d in _lot_lines(path):
        if d.get("pool_key") is None:
            continue
        yield {"pool": d.get("pool_key"), "slot": d.get("item_no"),
               "item_id": d.get("item_id"), "count": d.get("item_count"),
               "type": d.get("reward_target_type"), "ns": d.get("item_namespace"),
               "child": d.get("child_pool_key"),
               "state": d.get("target_identity_status"),
               "runtime": d.get("runtime_final_status")}


def _lot_attr(boards: Path) -> dict:
    """池归属/池内条目名 —— 只从【已发布看板】取；取不到就是「未解」。

    认得三种板型（都不重算）：
      · flat  条目自带 pool_id/name（如 lottery_dihuang.json）
      · pools 条目带 pools:[{pool_id, rows:[{slot,name,...}]}]（如 *_panel_static.json）
      · ids   条目带 pools:[391580, ...] + note_samples（如 future_lottery_preview.json）
    """
    out: dict = {}
    if not boards.is_dir():
        return out

    def slot_of(pk, board, act, ev, **kw):
        rec = out.setdefault(pk, {"boards": [], "activity": [], "items": [], "notes": []})
        if board not in rec["boards"]:
            rec["boards"].append(board)
        if act and act not in rec["activity"]:
            rec["activity"].append(act)
        rec["items"].append(dict({"board": board, "evidence": ev}, **kw))

    for fp in sorted(boards.glob("*.json")):
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:                                   # noqa: BLE001
            continue
        if not isinstance(d, dict):
            continue
        items = d.get("items")
        if not isinstance(items, list):
            continue
        # ★ 排除派生看板：lottery_pool_resolved_v01.json 就是本数据的投影，
        #   拿它当「归属」= 自己证明自己（实测会把 1761/1762 池全「认领」掉）。
        if items and isinstance(items[0], dict) and {"pool_key", "search_text"} <= set(items[0]):
            continue
        bname = (d.get("meta") or {}).get("name") or fp.stem
        for it in items:
            if not isinstance(it, dict):
                continue
            act = it.get("activity") or bname
            ev = it.get("evidence") or (d.get("meta") or {}).get("evidence") or "?"
            pk = it.get("pool_id") or it.get("pool_key")
            if pk is not None:
                slot_of(pk, bname, act, ev, slot=it.get("slot"), name=it.get("name"),
                        item_id=it.get("item_id"), prob=it.get("prob"))
            pools = it.get("pools")
            if isinstance(pools, list):
                for p in pools:
                    if isinstance(p, dict):
                        pid = p.get("pool_id")
                        if pid is None:
                            continue
                        if p.get("name"):
                            slot_of(pid, bname, act, ev, note=p.get("name"))
                        for r in (p.get("rows") or []):
                            if isinstance(r, dict):
                                slot_of(pid, bname, act, r.get("evidence") or ev,
                                        slot=r.get("slot"), name=r.get("name"),
                                        item_id=r.get("item_id"), prob=r.get("prob_note"))
                    elif isinstance(p, int):
                        slot_of(p, bname, act, ev)
                        rec = out[p]
                        for s in (it.get("note_samples") or [])[:12]:
                            if s not in rec["notes"]:
                                rec["notes"].append(s)
                        if it.get("instance_exp_date"):
                            rec["exp"] = it["instance_exp_date"]
    return out


def _lot_load(pool_jsonl: Path, targets_jsonl: Path, *, with_manifest=False):
    man: list = []
    pools = list(_lot_pool_rows(pool_jsonl, man))
    tg = {}
    if targets_jsonl.is_file():
        for t in _lot_target_rows(targets_jsonl):
            tg[(t["pool"], t["slot"])] = t
    return (man, pools, tg) if with_manifest else (pools, tg)


def _lot_lottery_tables(names_map: dict) -> list:
    import re as _re
    rx = _re.compile(_LOT_TAB_RE, _re.I)
    return sorted(p for p in names_map.values()
                  if isinstance(p, str) and p.replace("/", "\\").lower().startswith("com\\cdata\\")
                  and rx.search(p))


def _lot_pair(pool_jsonl: Path, targets_jsonl: Path):
    """一次扫描同时拿 pool 行与 target 行（按 pool 分组）。"""
    pools: dict = {}
    for r in _lot_pool_rows(pool_jsonl):
        pools.setdefault(r["pool"], []).append(r)
    tg: dict = {}
    if targets_jsonl.is_file():
        for t in _lot_target_rows(targets_jsonl):
            tg[(t["pool"], t["slot"])] = t
    return pools, tg


def cmd_lottery_locate(args) -> int:
    """★★ 按【内容】定位奖池 —— 取代「按看板归属认池」。

    ★ 为什么另起：旧 `find/show` 用【已发布看板】的归属认池，而看板是
      presentation projection、不是业务身份 ⇒ 实测把一批家具池归到「幻夜神谕」
      名下，每次问都被误导。

    ★ 本命令的做法（三环，每环可核）：
      ① 关键词 → 候选 id（ITEM_MASTER + gift/fashion/player_appear 的已解析行）
      ② 候选 id → 池：`reward_pool_data` 体系走 LOTTERY_REWARD_TARGETS 反查
      ③ 候选 id / 关键词 → 其它抽奖体系：扫 com\\cdata 下所有 lottery 系表
         （★ 三条线索：id 文本 / id 的 4 字节 LE-BE / 关键词本身）

    ★ 覆盖范围比旧命令大：旧命令只认 `reward_pool_data`，所以「幻夜神谕」
      （走超级时装抽奖）永远答不对；本命令会把命中体系一并给出。
    """
    from toolkit_core import lottery_locate as LL

    P = _lot_paths()
    site = P["pool"].parent
    # ★ P["analysis"] = <ROOT>/03_执行/30_分析 ⇒ 其 .parent 才是 03_执行
    #   （多写一层 .parent 会退到 ROOT，拼出不存在路径 ⇒ cdata 检查静默失败、第③节恒 0）
    # ★ 2026-10-01 修：**别再硬编码老扁平目录** —— 对标 E:\mrzh 之后 cdata 表每容器一份，
    #   老扁平 `41_还原树/com/cdata` 只是"赢家副本"，不是当前态；而且文件数最多、扫得最慢。
    #   改走 `table_locator.cdata_dirs()[0]`（= overlay/Documents 层 = 客户端当前态）。
    cdata = Path(args.cdata) if args.cdata else None
    if cdata is None:
        try:
            from toolkit_core import table_locator as _TL
            dirs = _TL.cdata_dirs()
            if dirs:
                cdata = dirs[0]
        except Exception:                                            # noqa: BLE001
            cdata = None
    if cdata is None:
        cdata = P.cdata_dir()
    if not cdata.is_dir():
        for alt in (P.cdata_dir(), P.PROJECT_ROOT / "03_执行" / "41_还原树" / "com" / "cdata"):
            if alt.is_dir():
                cdata = alt
                break
    struct_dir = Path(args.struct_dir) if args.struct_dir else None
    if struct_dir is None:
        cands = sorted(P["analysis"].glob("表结构解析_*"), reverse=True)
        for c in cands:
            if (c / "结构").is_dir():
                struct_dir = c / "结构"
                break

    print("★ 奖池定位（按内容认池 · 覆盖所有抽奖体系）")
    print("  关键词：%s" % args.keyword)
    print("  名字源：%s" % site)
    if struct_dir:
        print("  行数据：%s" % struct_dir)
    if cdata.is_dir():
        print("  表目录：%s" % cdata)
    else:
        print("  ⚠ 表目录不存在：%s ⇒ 第③节（其它抽奖体系）将恒为 0，"
              "请用 --cdata 指定 com\\cdata 还原树目录" % cdata, file=sys.stderr)
    print()

    rep = LL.locate(args.keyword, site_data=site, targets=P["target"],
                    cdata_dir=cdata, struct_dir=struct_dir, limit=args.limit)

    print("★ ① 关键词命中的 id：%d 条" % rep.get("name_hit_count", 0))
    for h in rep.get("name_hits", [])[:args.limit]:
        print("   %-10s %-26s %-20s %s" % (h["item_id"], (h["name"] or "")[:26],
                                           h.get("ns") or "—", h.get("strength") or "—"))
    print()
    print("★ ② `reward_pool_data` 体系命中的池：%d 个" % rep.get("pool_count", 0))
    for p in rep.get("pools", []):
        print("   池 %s（命中 %d 格）" % (p["pool"], len(p["hits"])))
        for h in p["hits"][:6]:
            print("      slot %-4s %-10s %-22s ns=%s" % (h["slot"], h["item_id"],
                                                         (h["name"] or "")[:22], h.get("ns")))
    if not rep.get("pools"):
        print("   （无 —— 说明它不走普通奖池，看第③节）")
    print()
    print("★ ③ 其它抽奖体系命中：%d 张表（`_auto_oversea_data_<后缀>` = 服务器类型变体，"
          "不是渠道）" % len(rep.get("systems") or []))
    for s in (rep.get("systems") or [])[:args.limit]:
        ch = s.get("channel")
        print("   %s %s%s" % ("[服型=%s]" % LL.variant_label(ch) if ch else "[通用]",
                              s.get("rel") or s["table"],
                              "（名字出自同名 _chs 池）" if s.get("via_chs") else ""))
        print("        %s ｜ 名字命中=%s ｜ id命中=%d（%s）%s"
              % (s["system"], s.get("name_hit"), s["hit_count"],
                 s.get("id_via") or "字节搜",
                 (", ".join(str(x) for x in (s.get("hit_ids") or [])[:6])) or "—"))
    if not rep.get("systems"):
        print("   （无）")
    print()
    print("★ ④ 官方概率公示命中：%d 块（★ 池成员的唯一静态源）"
          % len(rep.get("probs") or []))
    if rep.get("prob_alias"):
        print("   别名：%r → %s（活动名 ≠ 公示块名）"
              % (args.keyword, " / ".join("【%s】" % a for a in rep["prob_alias"])))
    for b in (rep.get("probs") or []):
        print("   ── 【%s】（%d 格）──" % (b["name"], len(b["entries"])))
        for idx, item, pct in b["entries"]:
            print("      %2s. %-38s %s" % (idx, item[:38], pct))
    if not rep.get("probs"):
        print("   （该关键词不在公示块名里；公示是池成员唯一静态源，不在就不给内容）")
    print()

    # ★★ ⑤ 活动展示道具（静态表 common_hd_show_reward_data，2026-09-30 加）
    #   ★ 键是【活动号】不是池号：按池号搜全树 0 命中（那条链客户端不存在），
    #     按活动号能直接取到该活动的展示道具列表（幻夜 3610 = 9 件）。
    #   链路：关键词 → huodong_conf_data 行(name) → 行 key(活动号) → 展示道具 + 名字
    try:
        hd = _hd_show_items_for_keyword(args.keyword, cdata)
    except Exception as exc:                                        # noqa: BLE001
        hd = []
        print("  ★ ⑤ 活动展示道具：查询失败 %s: %s" % (type(exc).__name__, exc))
    if hd:
        print("★ ⑤ 活动展示道具（静态表 common_hd_show_reward_data，按【活动号】取）")
        for blk in hd:
            print("   活动号 %s · %s · %d 件"
                  % (blk["key"], blk.get("hd_name") or "", len(blk["items"])))
            for it in blk["items"]:
                print("      %-12d %-26s %s" % (it["id"],
                      it.get("name") or ("★未命名（%s）" % it["kind"] if it.get("kind")
                                         else "★无名字"),
                      it.get("via") or ""))
        print()
    else:
        print("  ★ ⑤ 活动展示道具：关键词没对上活动表里的活动名"
              "（试 `lottery hd-show` 看全部 36 个活动）")
        print()
    print("  ⚠ %s" % rep.get("caveat", ""))

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        safe = "".join(c for c in args.keyword if c.isalnum() or c in "_-")[:40] or "kw"
        (out / ("奖池定位_%s.md" % safe)).write_text(LL.render_md(rep), encoding="utf-8")
        json.dump(rep, (out / ("奖池定位_%s.json" % safe)).open("w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print()
        print("★ 产物 → %s" % out)
    if args.json is not None:
        s = json.dumps(rep, ensure_ascii=False, indent=1)
        if args.json == "-":
            print(s)
        else:
            Path(args.json).write_text(s, encoding="utf-8")
    return 0


def _hd_show_items_for_keyword(keyword, cdata: Path) -> list:
    """关键词 → 活动号 → 该活动的【展示道具】列表 + 名字。

    ★ 为什么单独一条（2026-09-30 用户纠正后的正解）：
      池成员别按 pool id 找（客户端 0 命中）；按**活动号**在
      `common_hd_show_reward_data` 里能直接取到展示道具列表。
      活动号来自 `huodong_conf_data` 行的 key（与活动表同一套编号）。
    """
    import struct as _struct
    from toolkit_core import lottery_chain as LC
    from toolkit_core import show_item_names as SN

    key = str(keyword).strip()
    if not key:
        return []
    M = LC._mods()
    # ① 活动号 ← 活动名：★ 不能只看 base！
    #   实测 base `huodong_conf_data.py` 在树里【没有合法 x{ 帧】（3 个候选全越界），
    #   而幻夜神谕行（key=3610）住在 `oversea/huodong_conf_data_auto_oversea_data_kj1.py`
    #   ⇒ 必须按【服型表优先】多表搜。
    hp_cands = [
        Path(cdata) / "oversea" / "huodong_conf_data_auto_oversea_data_kj1.py",
        Path(cdata) / "oversea" / "huodong_conf_data_auto_oversea_data_kjxq.py",
        Path(cdata) / "huodong_conf_data.py",
    ]
    keys, src_used = [], None
    for hp in hp_cands:
        if not hp.is_file():
            continue
        fr, b = LC._frame(hp)
        if not fr:
            continue
        body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
        chs = hp.with_name(hp.stem + "_chs.py")
        pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
        rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
        for r in rows:
            v = {k: (x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else x)
                 for k, x in (r.get("values") or {}).items()}
            nm = str(v.get("name") or "")
            if nm and key in nm:
                keys.append((r.get("key"), nm, v.get("hd_class")))
        if keys:
            src_used = hp.name
            break
    if not keys:
        return []

    # ② common_hd_show_reward_data：活动号 → 展示道具
    sp = Path(cdata) / "common_hd_show_reward_data.py"
    if not sp.is_file():
        return []
    fr2, b2 = LC._frame(sp)
    if not fr2:
        return []
    body2 = b2[fr2[0] + 6: fr2[0] + 6 + fr2[1]]
    cnt, _ = _struct.unpack_from("<II", body2, 0)
    blob2 = body2[8 + 4 * cnt:]
    chs2 = sp.with_name(sp.stem + "_chs.py")
    pool2 = M["MP"].pool_of_file(str(chs2)) if chs2.is_file() else []
    rows2, _u2 = M["BP"].decode_table_rows_with_chs_slots(body2, pool2)
    by_key = {}
    for r in rows2:
        by_key[str(r.get("key"))] = r

    csvn = LC._csv_names()
    if not SN.stats().get("exists"):
        SN.build(verbose=False)

    out = []
    for k, nm, hd_class in keys[:4]:
        r = by_key.get(str(k))
        ids = []
        if r:
            v = {kk: (x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else x)
                 for kk, x in (r.get("values") or {}).items()}
            for _f, x in v.items():
                if isinstance(x, str) and x.startswith("jump:"):
                    try:
                        ids += M["BT"].resolve_jump_group(blob2, int(x.split(":")[1])) or []
                    except Exception:                               # noqa: BLE001
                        pass
        items = LC.name_ids(ids)
        out.append({"key": k, "hd_name": nm, "hd_class": hd_class, "items": items})
    return out


def cmd_lottery(args) -> int:
    """奖池层：list 家底 · find 找池 · show 单池详情 · delta 本次热更涉及哪些池。

    ★ 口径（不许含糊）：
      · 「池」= `reward_pool_data` 的复合键 `pool_key`（390000–391793）；
      · 池的**名字**在客户端静态表里不存在 —— 本命令只在【已发布看板】里找归属，
        找不到就写「未解」，绝不用别的东西凑；
      · runtime_final = 未解（child replacement / OptionalVersionMgr 覆盖），
        所以没有「当前在发的池」，也没有「最终奖励表」。
    """
    import hashlib
    import re as _re
    sub = getattr(args, "lottery_command", None) or "list"
    P = _lot_paths()
    pool_jsonl = Path(args.data) if getattr(args, "data", None) else P["pool"]
    targets_jsonl = P["target"]
    if not pool_jsonl.is_file():
        print("[lottery] ✗ 静态池结构不存在：%s" % pool_jsonl, file=sys.stderr)
        return 6
    boards = Path(args.boards) if getattr(args, "boards", None) else P["boards"]

    if sub == "list":
        man, pools, tg = _lot_load(pool_jsonl, targets_jsonl, with_manifest=True)
        m = (man[0] if man else {})
        stats = (m.get("stats") or {})
        by_pool: dict = {}
        for r in pools:
            by_pool.setdefault(r["pool"], []).append(r)
        pub = [r for r in pools if r["partition"] == "records"]
        q = [r for r in pools if r["partition"] != "records"]
        comp: dict = {}
        disp: dict = {}
        ttype: dict = {}
        ns: dict = {}
        for r in pools:
            comp[r["component"]] = comp.get(r["component"], 0) + 1
            disp[r["dispatch"]] = disp.get(r["dispatch"], 0) + 1
        for t in tg.values():
            ttype[t["type"]] = ttype.get(t["type"], 0) + 1
            ns[str(t["ns"])] = ns.get(str(t["ns"]), 0) + 1
        attr = _lot_attr(boards)
        covered = [p for p in by_pool if p in attr and (
            attr[p]["activity"] or any(i.get("name") for i in attr[p]["items"]))]
        named_items = sum(1 for v in attr.values() for i in v["items"] if i.get("name"))
        names_map = _load_names_map(getattr(args, "dict_path", None))
        tabs = _lot_lottery_tables(names_map)
        bs = sorted(p.name for p in boards.glob("*.json")
                    if _re.search(r"lottery|pool|chip|nucleus|chenshi", p.name, _re.I)
                    and p.name != "lottery_pool_resolved_v01.json")
        print("[lottery list] 奖池家底（源：%s，只读）" % pool_jsonl)
        print("  发布层：%s ｜ runtime_final=%s" % (m.get("publication_tier"), m.get("runtime_final_state")))
        print("  行：总 %d ｜ 已发布 %d ｜ 隔离 %d（隔离=通道变体未过校验，默认不参与结论）"
              % (len(pools), len(pub), len(q)))
        print("  ★ 池 %d 个（pool_key %d–%d）｜平均 %.1f 格/池｜最大 %d 格"
              % (len(by_pool), min(by_pool), max(by_pool),
                 len(pools) / len(by_pool), max(len(v) for v in by_pool.values())))
        print("  组件：%s" % dict(sorted(comp.items(), key=lambda x: -x[1])))
        print("  静态分派：%s（child_pool = 该格指向子池，要递归）"
              % dict(sorted(disp.items(), key=lambda x: -x[1])))
        print("  reward target 分类：%s" % dict(sorted(ttype.items(), key=lambda x: -x[1])))
        print("  item 命名空间：%s" % dict(sorted(ns.items(), key=lambda x: -x[1])))
        print("  相关配置表（com\\cdata\\ 匹配 %s）：%d 个" % (_LOT_TAB_RE, len(tabs)))
        print("  已发布看板 %d 个（不含派生看板）｜ 有名字/活动归属的池 %d / %d = %.1f%% ｜ 归属条目名 %d 条"
              % (len(bs), len(covered), len(by_pool), len(covered) / len(by_pool) * 100, named_items))
        print("  ★ 已排除的假设：静态表里【没有】池名字段 —— 池名只能来自看板归属；"
              "未认领的池 = 未解（不是「无名随机池」）")
        if args.limit and bs:
            print("  看板：")
            for b in bs[:args.limit]:
                print("    · %s" % b)
        if args.json is not None:
            _dump({"source": str(pool_jsonl), "manifest": m,
                   "rows_total": len(pools), "rows_published": len(pub),
                   "rows_quarantined": len(q), "pools": len(by_pool),
                   "pool_key_min": min(by_pool), "pool_key_max": max(by_pool),
                   "components": comp, "static_dispatch": disp,
                   "reward_target_type": ttype, "item_namespace": ns,
                   "table_count": len(tabs), "boards": len(bs),
                   "pools_attributed": len(covered)}, args.json)
        return 0

    if sub == "find":
        kw = args.keyword.strip()
        by_pool, tg = _lot_pair(pool_jsonl, targets_jsonl)
        attr = _lot_attr(boards)
        hit = {}
        if kw.isdigit():
            n = int(kw)
            for p in by_pool:
                if p == n or str(p).startswith(kw):
                    hit[p] = "pool_key 命中"
        else:
            low = kw.lower()
            for p, rec in attr.items():
                if p not in by_pool:
                    continue
                blob = " ".join(rec["activity"]) + " " + " ".join(
                    str(i.get("name") or "") for i in rec["items"]) + " " + " ".join(rec["notes"])
                if low in blob.lower():
                    hit[p] = "看板归属命中"
        print("[lottery find] 关键词 %r" % kw)
        if kw.isdigit():
            print("  口径：按 pool_key 精确/前缀匹配（%d 位）" % len(kw))
        else:
            print("  口径：只在【已发布看板】的活动名/条目名里找（池名在静态表里不存在）")
        print("  ★ 命中池 %d 个" % len(hit))
        for p, why in sorted(hit.items())[:args.limit]:
            rows = by_pool[p]
            t = [tg.get((p, r["slot"])) for r in rows]
            types = {}
            for x in t:
                if x:
                    types[x["type"]] = types.get(x["type"], 0) + 1
            act = "／".join(attr.get(p, {}).get("activity", [])) or "未解"
            tshow = dict(sorted(types.items(), key=lambda x: -x[1]))
            if not tshow:
                tshow = "target 侧无行（非 base 组件）"
            print("    %d  %-3d 格  %-24s %s  ← %s"
                  % (p, len(rows), act[:24], tshow, why))
        # 表侧：关键词也用于找相关配置表
        names_map = _load_names_map(getattr(args, "dict_path", None))
        tabs = _lot_lottery_tables(names_map)
        thit = [t for t in tabs if kw.lower() in t.lower()] if not kw.isdigit() else []
        if not kw.isdigit():
            print("  ★ 相关配置表命中 %d 个（com\\cdata\\ 奖池族）" % len(thit))
            for t in thit[:args.limit]:
                print("    · %s" % t)
        if args.json is not None:
            _dump({"keyword": kw, "pools": sorted(hit),
                   "tables": thit, "why": hit}, args.json)
        return 0 if (hit or thit) else 5

    if sub == "show":
        key = args.key.strip()
        by_pool, tg = _lot_pair(pool_jsonl, targets_jsonl)
        attr = _lot_attr(boards)
        target_pool = None
        if key.isdigit():
            if int(key) in by_pool:
                target_pool = int(key)
        if target_pool is None:
            low = key.lower()
            cand = [p for p, rec in attr.items() if p in by_pool and (
                low in " ".join(rec["activity"]).lower()
                or any(low in str(i.get("name") or "").lower() for i in rec["items"])
                or any(low in n.lower() for n in rec["notes"]))]
            if len(cand) == 1:
                target_pool = cand[0]
                print("[lottery show] %r → 池 %d（由看板归属认领）" % (key, target_pool))
            elif len(cand) > 1:
                print("[lottery show] %r 命中多个池，请用池号：%s" % (key, sorted(cand)[:args.limit]))
                return 5
        if target_pool is None:
            print("[lottery show] ✗ 找不到池 %r（池号 390000–391793；名字要先被看板认领）" % key,
                  file=sys.stderr)
            return 5
        rows = sorted(by_pool[target_pool], key=lambda r: (r["slot"] is None, r["slot"]))
        rec = attr.get(target_pool) or {}
        print("[lottery show] 池 %d" % target_pool)
        print("  格数 %d ｜ slot %s" % (len(rows), [r["slot"] for r in rows][:40]))
        acts = "／".join(rec.get("activity", [])) or "未解（无看板认领）"
        print("  归属（来自看板）：%s" % acts)
        if rec.get("boards"):
            print("  看板：%s" % "／".join(rec["boards"][:3]))
        if rec.get("exp"):
            print("  看板内 expiration：%s" % rec["exp"])
        print("  组件：%s" % dict(sorted({r["component"]: 1 for r in rows}.items())))
        print("  隔离行：%d / %d" % (sum(1 for r in rows if r["partition"] != "records"), len(rows)))
        print("  ── 每格有什么 ──")
        # ★ 2026-09-30 修正：回填必须【按命名空间】查。
        #   v1 拿 item_id 去全局 row_key 索引查 ⇒ 跨表撞车、名字全错
        #   （实测 row_key 133218 在 common_entity → 「废墟堆」、在 gift_data → 「海语童话头饰盒」，
        #     池里 ns=gift_data ⇒ 后者才对）。
        #   查不到就如实写「未收录」，绝不用别的表的同号行顶替。
        try:
            from toolkit_core import item_names as _IN
        except Exception:
            _IN = None
        # (ns, id) → 名字
        _nm: dict = {}
        if _IN:
            _by_ns: dict = {}
            for _r in rows[:args.limit]:
                _t = tg.get((target_pool, _r["slot"])) or {}
                _iid = _t.get("item_id")
                if not isinstance(_iid, int):
                    _iid = (_r["raw"] or [None])[0]
                _ns = _t.get("ns")
                if isinstance(_iid, int):
                    _by_ns.setdefault(_ns, []).append(_iid)
            for _ns, _ids in _by_ns.items():
                # ★ ns=common_item 占奖池目标 74%，但它不在 41_还原树（树里只是 815B 合并壳）
                #   ⇒ 走专用解析器（工作副本 base∪inc−del × chs 池）
                if _ns == "common_item":
                    try:
                        from toolkit_core import common_item_names as _CI
                        _meta = _CI.lookup_meta(_ids) if hasattr(_CI, "lookup_meta") else {}
                        for _k, _v in _CI.lookup(_ids).items():
                            if _v:
                                _q = ((_meta.get(_k) or {}).get("quality")) if _meta else None
                                _nm[(_ns, _k)] = _v if not _q else "%s｜%s" % (_v, _q)
                        continue
                    except Exception:
                        pass
                for _k, _v in _IN.lookup_ns(_ns, _ids).items():
                    _nm[(_ns, _k)] = (_v or {}).get("name")
        for r in rows[:args.limit]:
            t = tg.get((target_pool, r["slot"])) or {}
            mark = "○" if r["partition"] == "records" else "△隔离"
            if t.get("type") == "child_pool":
                print("    slot %-3s %s → 子池 %s（数量 %s）｜%s"
                      % (r["slot"], mark, t.get("child"), t.get("count"), t.get("state")))
            else:
                _iid = t.get("item_id")
                if not isinstance(_iid, int):
                    _iid = (r["raw"] or [None])[0]
                _ns = t.get("ns")
                _label = ""
                if isinstance(_iid, int):
                    _n = _nm.get((_ns, _iid))
                    _label = ("名字=%s" % _n) if _n else (
                        "名字=★未收录" if _ns else "名字=★ns未知不回填")
                print("    slot %-3s %s item_id=%-9s ×%-4s ns=%-10s 类型=%-10s %s 原始=%s"
                      % (r["slot"], mark, t.get("item_id"), t.get("count"),
                         t.get("ns"), t.get("type"), _label, r["raw"]))
        seen = set()
        for r in rows:
            t = tg.get((target_pool, r["slot"])) or {}
            c = t.get("child")
            if c is not None and c not in seen:
                seen.add(c)
                sub_rows = by_pool.get(c) or []
                print("    ↳ 子池 %d：%d 格 %s" % (c, len(sub_rows),
                                               sorted(x["slot"] for x in sub_rows)[:20]))
        print("  ★ 名字来源：%s" % ("看板条目名（下，按 item_id 与静态行对齐）"
                                 if rec.get("items") else
                                 "未解 —— 静态表无池名，本池未被任何看板认领"))
        by_item = {}
        for r in rows:
            t = tg.get((target_pool, r["slot"])) or {}
            for k in {t.get("item_id"), (r["raw"] or [None])[0]}:
                if isinstance(k, int):
                    by_item.setdefault(k, []).append(r["slot"])
        for it in (rec.get("items") or [])[:args.limit]:
            if not it.get("name") and it.get("item_id") is None:
                continue
            try:
                iid = int(it.get("item_id")) if it.get("item_id") is not None else None
            except (TypeError, ValueError):
                iid = None
            slots = by_item.get(iid) if iid is not None else None
            loc = ("静态 slot " + "/".join(str(s) for s in slots)) if slots else "静态表无此 item"
            warn = ""
            bs = it.get("slot")
            if slots and isinstance(bs, int) and bs not in slots:
                warn = "  ⚠看板 slot=%s ≠ 静态 slot（对账以 item_id 为准）" % bs
            print("    %-30s item_id=%-9s prob=%-9s [%s] %s%s"
                  % ((it.get("name") or "?")[:30], it.get("item_id"), it.get("prob"),
                     it.get("evidence"), loc, warn))
        for n in (rec.get("notes") or [])[:8]:
            print("    · 看板样例名：%s" % n)
        print("  ★ runtime_final=未解：child replacement / OptionalVersionMgr 覆盖未解析，"
              "本输出是静态结构，不是当前发奖结果")
        if args.json is not None:
            _dump({"pool_key": target_pool, "slots": [r["slot"] for r in rows],
                   "attribution": rec, "rows": [
                       dict(r, target=tg.get((target_pool, r["slot"]))) for r in rows]}, args.json)
        return 0

    if sub == "delta":
        return _lot_delta(args, pool_jsonl, targets_jsonl, boards)

    if sub == "prob":
        return _lot_prob(args)

    print("[lottery] 未知子命令 %r（用 list / find / show / delta / prob）" % sub, file=sys.stderr)
    return 2


def _find_desc_info() -> Path | None:
    """定位 desc_info_data_chs.py —— 奖池概率公示的原文表。

    ★ 顺序（2026-09-29 改）：**先把 `41_还原树` 当唯一权威**，
      老的 `30_分析/*/07_restore_tree/tree_v*` 只作**回退**。

    为什么改：原实现只认 `*/07_restore_tree/tree_v*`，而那是**复核副本**、
    正被清理（68 GB 重复树）。架构改造的口径是「产物根单一来源 = 还原树」，
    这里就是第一个断点 —— 只认副本的话，副本一删功能就哑。
    """
    import re as _re
    from toolkit_core import paths as P

    # ① 权威源：41_还原树（★ 新层级：<树>/<容器>/com/cdata/…，走表定位链）
    tree = P.cdata_table("desc_info_data_chs.py")
    if tree.is_file():
        return tree

    # ② 回退：老的复核副本（取 tree_v 版本最大的）
    analysis = P.PROJECT_ROOT / "03_执行" / "30_分析"
    if not analysis.is_dir():
        return None
    cands = list(analysis.glob("*/07_restore_tree/tree_v*/com/cdata/desc_info_data_chs.py"))
    if not cands:
        return None

    def ver(p):
        m = _re.search(r"tree_v(\d+)", str(p))
        return int(m.group(1)) if m else 0
    return sorted(cands, key=ver, reverse=True)[0]


def _prob_blocks(path: Path) -> list:
    """★ 单一来源：`toolkit_core.lottery_locate.prob_blocks`。

    为什么收回模块：原来的判据（只认名字含「奖池/抽奖/转盘」）在 CLI 里，
    而 `lottery locate` 也要用公示 —— 两边各写一份必然分叉。现在口径只有一份。
    """
    from toolkit_core import lottery_locate as LL
    return LL.prob_blocks(path)


def _prob_alias(kw: str) -> list:
    """★ 单一来源：`toolkit_core.lottery_locate.prob_alias`。"""
    from toolkit_core import lottery_locate as LL
    return LL.prob_alias(kw)


def _lot_prob(args) -> int:
    """奖池概率公示：从 desc_info_data_chs.py 抽【XX奖池】块（配置表原文）。"""
    path = Path(args.desc_info) if getattr(args, "desc_info", None) else _find_desc_info()
    if not path or not path.is_file():
        print("[lottery prob] ✗ 找不到 desc_info_data_chs.py（用 --desc-info 指明）",
              file=sys.stderr)
        return 6
    blocks = _prob_blocks(path)
    if not blocks:
        print("[lottery prob] ✗ 没抽到概率公示块（表结构可能变了）", file=sys.stderr)
        return 7
    kw = getattr(args, "keyword", None)
    if kw:
        cand = _prob_alias(kw)
        blocks = [b for b in blocks if any(k in b["name"] for k in cand)]
        if not blocks:
            print("[lottery prob] ✗ 没有匹配 %r 的奖池" % kw, file=sys.stderr)
            print("   公示块共 %d 个，用 `lottery prob`（不带关键词）看全名 —— "
                  "活动名常与公示块名不同（如「幻夜神谕」→【神谕童话概率公示】）"
                  % len(_prob_blocks(path)), file=sys.stderr)
            return 8
        extra = [k for k in cand if k != kw]
        if extra:
            print("[lottery prob] 别名：%r → %s（活动名与官方公示块名不同）"
                  % (kw, " / ".join("【%s】" % e for e in extra)))
    print("[lottery prob] 奖池概率公示（源：%s）" % path)
    print("  口径：配置表原文的概率公示字段；游戏声明「大样本统计值，"
          "与单个玩家少量测试数据可能有差异」")
    for b in blocks:
        print()
        print("── 【%s】（%d 格）──" % (b["name"], len(b["entries"])))
        for idx, item, pct in b["entries"]:
            print("   %2s. %-40s %s" % (idx, item[:40], pct))
    if args.json is not None:
        _dump({"source": str(path), "pools": blocks}, args.json)
    return 0


def _lot_delta(args, pool_jsonl: Path, targets_jsonl: Path, boards: Path) -> int:
    """本次热更涉及哪些池：三条判据各自独立，命中就写「已确认」，不命中就写「未命中」。

    判据①  overlay 包 fid 条目 ⊇ 奖池相关模块？去重后逐条与基线产物比字节 ⇒ 哪些真变了
    判据②  pkg_N.pi 新增/移除 fid 里有奖池相关 fid？⇒ 静态结构是否被动过
    判据③  变更文字表清单里的奖池表（模块名级）—— 只作旁证，不等于内容变了
    """
    import hashlib
    analysis = args.analysis or _lot_paths()["analysis"]
    delivery = Path(args.delivery) if args.delivery else None
    if delivery is None:
        cands = [p for p in analysis.glob("热更交付_5目录_*") if p.is_dir()]
        if not cands:
            print("[lottery delta] ✗ 没找到 热更交付_5目录_* 目录（用 --delivery 指明）", file=sys.stderr)
            return 6
        delivery = max(cands, key=lambda p: p.stat().st_mtime)
    print("[lottery delta] 热更交付目录：%s" % delivery)

    names_map = _load_names_map(getattr(args, "dict_path", None))
    name_of = names_map
    rep = {"delivery": str(delivery), "changed_modules": [], "unchanged_modules": [],
           "tables_overlay_list": [], "struct_fids_in_delta": [], "fid_delta_lottery": 0,
           "overlay_entries": 0, "overlay_present": False}

    # ── 判据③（旁证）：变更文字表清单里的奖池表 ──
    chg = delivery / "02_文字表" / "本次变更文字表_表名清单.txt"
    tabs = []
    if chg.is_file():
        tabs = [x.strip() for x in chg.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
    import re as _re
    rx = _re.compile(_LOT_TAB_RE, _re.I)
    tab_hits = [t for t in tabs if rx.search(t)]
    rep["tables_overlay_list"] = tab_hits
    print("  判据③（旁证·模块名级）变更文字表 %d 个，其中奖池族 %d 个"
          % (len(tabs), len(tab_hits)))
    for t in tab_hits:
        print("    · %s" % t)

    # ── 判据②：pkg_N.pi 新增/移除 fid ──
    cl = delivery / "05_变更清单与报告总结" / "变更清单"
    added_p = cl / "新增_fid.txt"
    removed_p = cl / "移除_fid.txt"
    core = {}
    if added_p.is_file():
        added = {x.strip().upper() for x in added_p.read_text(encoding="utf-8-sig").splitlines() if x.strip()}
        removed = ({x.strip().upper() for x in removed_p.read_text(encoding="utf-8-sig").splitlines() if x.strip()}
                   if removed_p.is_file() else set())
        def _is_tab(nm: str) -> bool:
            return str(nm).replace("/", "\\").lower().startswith("com\\cdata\\")

        lot_add = sorted(f for f in added if f in name_of and rx.search(str(name_of[f])))
        lot_rem = sorted(f for f in removed if f in name_of and rx.search(str(name_of[f])))
        t_add = [f for f in lot_add if _is_tab(name_of[f])]
        t_rem = [f for f in lot_rem if _is_tab(name_of[f])]
        a_add = [f for f in lot_add if not _is_tab(name_of[f])]
        core = {f: {"name": name_of.get(f, "（字典无此 fid）"), "in_added": f in added,
                    "in_removed": f in removed} for f in _LOT_POOL_FIDS}
        rep.update({"added_total": len(added), "removed_total": len(removed),
                    "fid_delta_lottery": len(lot_add) + len(lot_rem),
                    "fid_delta_tables": [name_of[f] for f in t_add + t_rem],
                    "fid_delta_assets": [name_of[f] for f in a_add + [f for f in lot_rem if not _is_tab(name_of[f])]],
                    "struct_fids_in_delta": [f for f, v in core.items()
                                             if v["in_added"] or v["in_removed"]]})
        print("  判据②（pkg_N.pi 物理 diff）新增 %d ｜ 移除 %d 条 fid"
              % (len(added), len(removed)))
        print("    · 奖池族**配置表**（com\\cdata\\）命中：%d 条%s"
              % (len(t_add) + len(t_rem),
                 ("：" + "、".join(name_of[f] for f in t_add + t_rem)) if (t_add or t_rem) else ""))
        print("    · 抽奖**界面资源**（ui/ 图标·图集·spine）命中：%d 条（不是池配置，仅供 UI 复原用）"
              % len(rep["fid_delta_assets"]))
        for f in (a_add + [f for f in lot_rem if not _is_tab(name_of[f])])[:args.limit]:
            print("      %s %s" % (f, name_of[f]))
        print("    静态奖池结构表（LOTTERY_POOL_RESOLVED 的源）：")
        for f, v in core.items():
            print("      %s %-34s 新增=%s 移除=%s"
                  % (f, v["name"], v["in_added"], v["in_removed"]))

    # ── 判据①：overlay 包逐条比内容 ──
    pkgs = sorted((delivery / "pkgs").glob("*script*overlay*.npk"))
    print("  判据①（script overlay 逐条 fid 比字节）：")
    if not pkgs:
        print("    ○ overlay 包不在交付目录（%s/pkgs）—— 未解，未做内容级判定" % delivery)
    else:
        from toolkit_core import container_probe as CP
        overlay = pkgs[-1]
        rep["overlay_present"] = True
        rep["overlay"] = str(overlay)
        meta = CP.overlay_entries(overlay)
        fids = [e["fid"] for e in meta["entries"]]
        rep["overlay_entries"] = len(fids)
        lot_fids = [(f, name_of[f]) for f in fids if f in name_of and rx.search(str(name_of[f]))]
        print("    overlay %s（%s B）条目 %d 条，其中奖池族模块 %d 个"
              % (overlay.name, format(overlay.stat().st_size, ","), len(fids), len(lot_fids)))
        # 基线产物：索引拿 (容器,行) → 产物路径（取存在的、尺寸优先相同的）
        from toolkit_core import artifact_locator as AL
        db = Path(args.db) if args.db else DEFAULT_DB
        import sqlite3
        con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
        cand: dict = {}
        for c, f, r in con.execute(
                "SELECT container,fid_hex,row_index FROM entries WHERE lower(container) LIKE '%script%'"):
            cand.setdefault(f, []).append((c, r))
        con.close()
        if args.unpack_out:
            unp = CP.overlay_unpack(overlay, args.unpack_out)
            sha = {e["fid"]: (e.get("sha256"), e.get("bytes")) for e in unp["entries"]}
            print("    解包 → %s（%d 条）" % (unp["out"], unp["n_entries"]))
        else:
            import tempfile
            tmp = Path(tempfile.mkdtemp(prefix="lot_lot_"))
            unp = CP.overlay_unpack(overlay, tmp, write=False)
            sha = {e["fid"]: (e.get("sha256"), e.get("bytes")) for e in unp["entries"]}
        loc = AL.Locator(args.product_root if args.product_root else AL.DEFAULT_ROOT)
        changed, same, nolocal = [], 0, 0
        for f, nm in lot_fids:
            h, n = sha.get(f, (None, None))
            if h is None:
                nolocal += 1
                continue
            # ★ 同一 fid 在本地可能有多个副本（base 包 / Documents 包），且彼此内容不同。
            #   规则：全部副本逐个比，**只要有任意一个副本与 overlay 逐字节相同 ⇒ 判「未变」（重下发）**；
            #   并在输出里把「有副本却不同」的事实一并列出（不裁决容器优先级）。
            copies = []
            for c, r in cand.get(f, []):
                p = loc.path(c, r)
                if p is not None and p.is_file():
                    pb = p.read_bytes()
                    copies.append({"container": c, "row": r, "bytes": len(pb),
                                   "match": hashlib.sha256(pb).hexdigest() == h,
                                   "path": str(p)})
            if not copies:
                nolocal += 1
                continue
            rec = {"fid": f, "name": nm, "overlay_bytes": n, "copies": copies,
                   "same": any(x["match"] for x in copies)}
            if rec["same"]:
                same += 1
                rep["unchanged_modules"].append(rec)
            else:
                changed.append(rec)
        rep["changed_modules"] = changed
        print("    奖池族 %d 个模块：内容变化 %d ｜ 与本地副本逐字节一致 %d ｜ 本地无对应 %d"
              % (len(lot_fids), len(changed), same, nolocal))
        for c in changed:
            print("    ★ 变了 %s %s  overlay=%s B ｜ 本地 %d 个副本均不同：%s"
                  % (c["fid"], c["name"], c["overlay_bytes"], len(c["copies"]),
                     "、".join("%s r%s %dB" % (x["container"], x["row"], x["bytes"])
                               for x in c["copies"])))
        for c in rep["unchanged_modules"]:
            hit = [x for x in c["copies"] if x["match"]][0]
            other = [x for x in c["copies"] if not x["match"]]
            print("    ○ 未变 %s %s（%s B）← 本地 %s r%s 与 overlay 逐字节相同"
                  % (c["fid"], c["name"], c["overlay_bytes"], hit["container"], hit["row"]))
            for o in other:
                print("        · 另一副本不同（本就是两份、都早于本次热更）：%s r%s %s B —— 本命令不裁决容器优先级"
                      % (o["container"], o["row"], o["bytes"]))
        rep["overlay_to_scan"] = str(overlay)

    # ── 结论 ──
    print()
    print("  ── 结论（证据分级）──")
    struct = rep.get("struct_fids_in_delta") or []
    if struct:
        print("   ⚠ 静态奖池结构表出现在 fid delta 里：%s ⇒ 需重跑 LOTTERY_POOL_RESOLVED" % struct)
    else:
        print("   已确认：静态奖池结构（reward_pool_data base/chs，fid %s）本次"
              "【未】出现在新增/移除 fid 里 ⇒ 池成员结构未被这次热更改动"
              % "／".join(_LOT_POOL_FIDS))
    if rep["changed_modules"]:
        print("   已确认：overlay 内奖池族模块内容真变了 %d 个：" % len(rep["changed_modules"]))
        for c in rep["changed_modules"]:
            print("      %s（%s）" % (c["name"], c["fid"]))
        print("   未解：这些表改的是哪几行/哪几个 pool_key —— 表体是 Py3.13 marshal 的 legacy 池格式，"
              "本命令只做字节级比对，不解析内容")
    if tab_hits:
        n_chs_same = len([u for u in rep.get("unchanged_modules", [])
                          if "_chs" in (u.get("name") or "")])
        print("   注意：变更文字表清单（%d 个奖池族表）是【模块名级】判据 —— "
              "上面逐字节比对显示这 %d 个 _chs 表内容全与本地一致 ⇒ 该清单会高估「真变化」"
              % (len(tab_hits), n_chs_same))
    if not rep["overlay_present"]:
        print("   未解：交付目录里没有 script overlay 包，判据①无法执行；"
              "已排除：判据②③均已跑过")
    n_changed = len(rep["changed_modules"])
    n_same = len(rep["unchanged_modules"])
    if rep["overlay_present"]:
        if n_changed == 0 and n_same:
            print("   ★ 总判定（已确认）：本次热更【没有】引入任何奖池族配置表的内容变化 —— "
                  "overlay 里 %d 个奖池族模块全部与本地副本逐字节相同（重下发）；"
                  "静态池结构表更是根本没进本次 diff。" % n_same)
        elif n_changed:
            print("   ★ 总判定（已确认）：本次热更【改动了】%d 个奖池族配置表：%s；"
                  "静态池结构表%s。" % (n_changed,
                                    "、".join(c["name"].split("\\")[-1] for c in rep["changed_modules"]),
                                    "未动" if not struct else "也在 diff 里（见上⚠）"))
    print("   口径提醒：本命令的「涉及」= 配置表变了；不等于「某池的奖励内容变了」"
          "（池成员结构未动已由判据②证明）")
    if args.json is not None:
        _dump(rep, args.json)
    return 0


def cmd_tables_copies(args) -> int:
    """★★ 表副本定位/审计 —— 回答「这张表该读哪一份」。

    ★ 背景（2026-09-30 用户抓到并要求杜绝）：
      同一逻辑表在客户端里有**多份副本**（安装目录底座包 vs `Documents` 可写/overlay 包），
      **fid 相同、内容不同**；热更新增的行只在 `Documents` 那份里。
      引擎侧证据：`patch\\PatchUtils.py` 的包名规则含 `.layers.<层号>` / `.overlay<类型>.<ts>`，
      配套 `layer_order` / `get_enabled_res_layer_order` / `max_overlay`
      ⇒ 客户端按层序挂载、**后挂的盖先挂的**，所以「读哪份」由层序定，不是比内容。
    ⇒ 规则：**按 fid 定位 + overlay/Documents 优先**（实现见 `toolkit_core.table_locator`）。
    """
    from toolkit_core import table_locator as TL

    if args.audit:
        print("★ 全库自检：树里「有名字的表」到底存的是哪一份副本 …")
        rep = TL.audit_named_tables_in_tree(limit=args.limit)
        if rep.get("error"):
            print("   ✗ %s" % rep["error"], file=sys.stderr)
            return 4
        print("   多副本且内容不同的 fid：%d" % rep["multi_copy_fids"])
        print("   树里有名字且属于这些 fid 的路径：%d" % rep["named_rows_checked"])
        h = rep["tree_holds"]
        print("   ★ 判据=通用解析器解出的行集合： 树已合并(最新) %d ｜ ★树旧了 %d ｜ 树解不出/某层能解 %d ｜ 都解不出 %d"
              % (h.get("tree_merged_ok", 0), h.get("tree_stale", 0),
                 h.get("tree_unparsed", 0), h.get("unknown", 0)))
        if rep["hazards"]:
            print()
            print("   ⚠ 隐患清单（前 %d 条）：" % len(rep["hazards"]))
            for x in rep["hazards"]:
                print("     [%s] %s  fid=%s  树行数=%s"
                      % (x["verdict"], x["path"][:52], x["fid"], x["tree_rows"]))
                for c in x["copies"]:
                    print("         %-40s 行数=%s" % (c["container"][:40], c["rows"]))
        print()
        print("   ★ %s" % rep["note"])
        if args.json is not None:
            _j = __import__("json")
            if args.json == "-":
                print(_j.dumps(rep, ensure_ascii=False, indent=1))
            else:
                _out = Path(args.json)
                _out.parent.mkdir(parents=True, exist_ok=True)
                _out.open("w", encoding="utf-8").write(
                    _j.dumps(rep, ensure_ascii=False, indent=1))
        return 0

    if not args.table:
        print("[tables copies] 给一个表名/路径/fid，或用 --audit 全库自检", file=sys.stderr)
        return 2
    key = str(args.table).strip()
    print("★ 表副本定位（规则：按 fid + overlay/Documents 优先）")
    if re.fullmatch(r"[0-9A-Fa-f]{16}", key):
        fid = key.upper()
        cs = TL.copies_of_fid(fid)
        print("   fid %s → 副本 %d 份" % (fid, len(cs)))
    else:
        fid = TL.fid_of_path(key) or TL.fid_of_path("com\\cdata\\" + key)
        if not fid:
            print("   ✗ 在 row_path_map 里找不到这个表名/路径：%s" % key, file=sys.stderr)
            return 5
        cs = TL.copies_of_fid(fid)
        print("   %s → fid=%s · 副本 %d 份" % (key, fid, len(cs)))
    if not cs:
        print("   ✗ 索引里没有这个 fid 的条目", file=sys.stderr)
        return 5
    for c in cs:
        mark = "★ overlay(可写/热更层)" if any(
            m in c["container"] for m in TL.OVERLAY_MARKERS) else "base(底座)"
        print("   %-14s %-40s r%-7s decoded=%-9s flag=%s"
              % (mark, c["container"][:40], c["row"], c["decoded"], c["flag"]))
        if c.get("tree_path"):
            print("        树路径：%s（in_tree=%s）" % (c["tree_path"], c["in_tree"]))
    best = TL.best_copy(fid)
    got = TL.best_path_for_fid(fid)
    print()
    print("   ⇒ 该用的那份：%s（%s · r%s）"
          % (best["container"], "overlay/Documents" if any(
              m in best["container"] for m in TL.OVERLAY_MARKERS) else "base",
             best["row"]))
    if got:
        p, info = got
        print("   ⇒ 实际该读：%s" % p)
        print("   ⇒ 判定：%s ｜ 树里 %s 行%s"
              % (info.get("verdict", "?"), info.get("tree_rows") or info.get("copy_rows") or "?",
                 ("（副本有 %s 行，比树多 ⇒ 树旧了）" % info["copy_rows"])
                 if info.get("verdict") == "tree_stale" else ""))
        if info.get("verdict") == "unparsed":
            print("      ⚠ 树里那份解不出行、副本也解不出 ⇒ 需人工看（不猜）")
    else:
        print("   ⇒ ★ 树里没有可用文件（请用 fid 从容器取）")
    if args.json is not None:
        _j = __import__("json")
        _rep = {"fid": fid, "copies": cs, "best": best,
                "path": str(got[0]) if got else None,
                "verdict": (got[1].get("verdict") if got else None)}
        if args.json == "-":
            print(_j.dumps(_rep, ensure_ascii=False, indent=1))
        else:
            _out = Path(args.json)
            _out.parent.mkdir(parents=True, exist_ok=True)
            _out.open("w", encoding="utf-8").write(
                _j.dumps(_rep, ensure_ascii=False, indent=1))
    return 0


def cmd_tables(args) -> int:
    """配置表层：list / find / chs（抽中文）/ refimg（表引用的图片路径）。"""
    import json as _json
    import re as _re
    sub = getattr(args, "tables_command", None)
    names_map = _load_names_map(getattr(args, "dict_path", None))
    alltab = [p for p in names_map.values()
              if isinstance(p, str) and p.replace("/", "\\").lower().startswith("com\\cdata\\")]
    print("[tables] com\\cdata\\ 表 %d 个" % len(alltab))

    if sub in (None, "list"):
        from collections import Counter
        c = Counter(_table_cat(p) for p in alltab)
        print()
        for k in list(_TABLE_CATS) + ["其它"]:
            if c.get(k):
                print("  %-10s %6d" % (k, c[k]))
        print("  %-10s %6d" % ("（合计）", len(alltab)))
        if args.json is not None:
            _dump({"total": len(alltab), "by_cat": dict(c)}, args.json)
        return 0

    if sub == "find":
        kw = args.keyword.lower()
        hit = sorted(p for p in alltab if kw in p.lower())
        print("  匹配 %d 个：" % len(hit))
        for p in hit[:args.limit]:
            print("    %s" % p)
        if len(hit) > args.limit:
            print("    …还有 %d 个（--limit 调大）" % (len(hit) - args.limit))
        if args.json is not None:
            _dump({"count": len(hit), "paths": hit}, args.json)
        return 0

    if sub in ("chs", "cn"):
        # ★ 只查 _chs.py（或用户给的关键词）
        kw = (args.keyword or "_chs.").lower()
        cand = [(p, h) for h, p in names_map.items()
                if isinstance(p, str) and kw in p.lower()]
        print("  目标表 %d 个 ｜ 关键词 %r" % (len(cand), kw))
        loc = _artifact_locator()
        rx = _cn_re()
        db = args.db or DEFAULT_DB
        idx = _table_index(names_map, db)
        print("  fid→容器行 定位 %d 个" % len(idx))
        rows, tot = [], 0
        from concurrent.futures import ThreadPoolExecutor
        import os as _os

        def grab(item):
            p, h = item
            lc = idx.get(h)
            if not lc:
                return None
            fp = loc.path(lc[0], lc[1])
            if fp is None or fp.stat().st_size > args.max_size:
                return None
            try:
                b = fp.read_bytes()
            except OSError:
                return None
            cn = []
            for m in rx.finditer(b):
                try:
                    s = m.group().decode("utf-8", "replace").strip()
                except Exception:
                    continue
                if len(s) >= 2:
                    cn.append(s)
            if not cn:
                return None
            return {"path": p, "container": lc[0], "row": lc[1],
                    "bytes": len(b), "cn": list(dict.fromkeys(cn))}

        nw = min(args.workers, (_os.cpu_count() or 4))
        with ThreadPoolExecutor(max_workers=nw) as ex:
            for r in ex.map(grab, cand):
                if r:
                    rows.append(r)
                    tot += len(r["cn"])
        uniq = list(dict.fromkeys([s for r in rows for s in r["cn"]]))
        print()
        print("  ★ 解出中文的表 %d / %d = %.1f%%"
              % (len(rows), len(cand), len(rows) / len(cand) * 100 if cand else 0))
        print("  ★ 中文串 %d 条（唯一 %d）" % (tot, len(uniq)))
        print()
        for r in rows[:5]:
            print("  ── %s  (%s r%d)" % (r["path"], r["container"], r["row"]))
            for s in r["cn"][:15]:
                print("       %s" % s)
        if args.out:
            o = Path(args.out)
            o.mkdir(parents=True, exist_ok=True)
            (o / "配置表中文_全量.txt").write_text("\n".join(uniq), encoding="utf-8")
            by = {}
            for r in rows:
                by.setdefault(_table_cat(r["path"]), []).extend(r["cn"])
            L = ["# 配置表中文（UTF-16LE 解出）\n",
                 "来源 com\\cdata\\ ，解出 %d 表 / %d 条\n" % (len(rows), tot)]
            for k, v in by.items():
                vv = list(dict.fromkeys(v))
                L.append("\n## %s（%d）\n" % (k, len(vv)))
                L += ["- %s" % s for s in vv]
            (o / "配置表中文_分类.md").write_text("\n".join(L), encoding="utf-8")
            _dump(rows, str(o / "配置表中文.json"))
            print("  → %s" % o)
        if args.json is not None:
            _dump({"tables": len(rows), "strings": tot, "unique": uniq[:5000]}, args.json)
        return 0

    if sub == "refimg":
        # 表里抽【明文图片路径】（表内容虽是 UTF-16，但路径是 ASCII 明文）
        from collections import Counter, defaultdict
        HEADS = ("ui", "res", "video", "weather", "scene_bw", "effect", "character",
                 "model", "model_high_2024", "weapon", "building", "sound", "script",
                 "other_icon", "instance", "shader", "text")
        PAT = _re.compile(r"(?i)(?:" + "|".join(HEADS) + r")[\\/][A-Za-z0-9_\-\\/\.]{2,180}?"
                          r"\.(?:png|jpg|jpeg|dds|tga|mp4|webm|xml|webp)")
        SCAN = _re.compile(rb"[\x20-\x7e]{6,2000}")
        kw = (args.keyword or "").lower()
        cand = [(p, h) for h, p in names_map.items()
                if isinstance(p, str) and p.replace("/", "\\").lower().startswith("com\\cdata\\")
                and (not kw or kw in p.lower())]
        print("  扫 %d 个表" % len(cand))
        loc = _artifact_locator()
        idx = _table_index(names_map, args.db or DEFAULT_DB)
        allp, src = Counter(), defaultdict(set)
        from concurrent.futures import ThreadPoolExecutor
        import os as _os

        def one(item):
            p, h = item
            lc = idx.get(h)
            if not lc:
                return None
            fp = loc.path(lc[0], lc[1])
            if fp is None or fp.stat().st_size > 2_000_000:
                return None
            try:
                b = fp.read_bytes()
            except OSError:
                return None
            got = set()
            for m in SCAN.finditer(b):
                for q in PAT.findall(m.group().decode("latin1")):
                    q = q.replace("/", "\\").strip("\\")
                    if 6 <= len(q) <= 160 and ".." not in q:
                        got.add(q)
            return (p, sorted(got)) if got else None

        with ThreadPoolExecutor(max_workers=min(args.workers, _os.cpu_count() or 4)) as ex:
            for r in ex.map(one, cand):
                if r:
                    for q in r[1]:
                        allp[q] += 1
                        src[q].add(r[0].split("\\")[-1])
        print("  ★ 唯一图片路径 %d 条" % len(allp))
        if args.out:
            o = Path(args.out)
            o.mkdir(parents=True, exist_ok=True)
            (o / "表引用图片路径_全量.txt").write_text("\n".join(sorted(allp)), encoding="utf-8")
            L = ["# 配置表引用的图片路径（%d）\n" % len(allp)]
            for q in sorted(allp):
                L.append("- `%s`   ← %s" % (q, ", ".join(sorted(src[q])[:2])))
            (o / "表引用图片路径_分类.md").write_text("\n".join(L), encoding="utf-8")
            print("  → %s" % o)
        if args.json is not None:
            _dump({"unique": dict(allp)}, args.json)
        return 0

    raise SystemExit("[tables] 未知子命令 %r" % sub)


# ══════════════════════════════════════════════════════════════════
# atlas —— spine 图集层
#   ★ 铁律：容器内顺序 = [atlas][本体DDS][json]，但偏移不固定（+1 主流，也有 +3/-1）
#     所以必须【在 atlas 行附近按尺寸找 DDS】，不能写死 +1
# ══════════════════════════════════════════════════════════════════

def _parse_atlas(fp: Path):
    """解析一个 atlas：返回 [{"png","w","h","fmt","sprites":[{name,x,y,sw,sh,rot}]}]"""
    import re as _re
    try:
        txt = fp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    pages, cur, lines, i = [], None, txt.splitlines(), 0
    while i < len(lines):
        s = lines[i].strip()
        if s.lower().endswith(".png") and " " not in s:
            cur = {"png": s, "w": 0, "h": 0, "fmt": "", "sprites": []}
            pages.append(cur)
            i += 1
            continue
        if cur is None:
            i += 1
            continue
        if s.startswith("size:"):
            a, b = s[5:].split(",")
            cur["w"], cur["h"] = int(a), int(b)
            i += 1
            continue
        if s.startswith("format:"):
            cur["fmt"] = s.split(":", 1)[1].strip()
            i += 1
            continue
        if s and ":" not in s and not s.startswith(("  ", "\t")):
            d = {"name": s}
            j = i + 1
            while j < len(lines) and lines[j].startswith(("  ", "\t")):
                t = lines[j].strip()
                if t.startswith("xy:"):
                    a, b = t[3:].split(",")
                    d["x"], d["y"] = int(a), int(b)
                elif t.startswith("size:"):
                    a, b = t[5:].split(",")
                    d["sw"], d["sh"] = int(a), int(b)
                elif t.startswith("rotate:"):
                    d["rot"] = t.split(":", 1)[1].strip() == "true"
                j += 1
            if "sw" in d:
                cur["sprites"].append(d)
            i = j
            continue
        i += 1
    return pages


def cmd_atlas(args) -> int:
    """图集层：list / discover（按清单+尺寸认本体）/ export / sprites / cut。"""
    import json as _json
    import struct as _struct
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor
    import os as _os

    sub = args.atlas_command
    root = Path(args.restore_root) if args.restore_root else DEFAULT_RESTORE
    loc = _artifact_locator()
    names_map = _load_names_map(getattr(args, "dict_path", None))

    if sub == "list":
        atl = sorted(list((root / "ui/spine").rglob("*.atlas"))
                     + list((root / "ui/spine_new").rglob("*.atlas")))
        print("[atlas] %d 个" % len(atl))
        c = Counter("/".join(p.relative_to(root).as_posix().split("/")[:3]) for p in atl)
        for k, v in c.most_common(30):
            print("   %-46s %5d" % (k, v))
        if args.json is not None:
            _dump({"count": len(atl), "by_dir": dict(c)}, args.json)
        return 0

    # discover：atlas → 本体真名 + 容器行（按尺寸认领）
    atl = sorted(list((root / "ui/spine").rglob("*.atlas"))
                 + list((root / "ui/spine_new").rglob("*.atlas")))
    print("[atlas] atlas %d 个 ｜ 窗口 ±%d" % (len(atl), args.window))
    pages = []
    for p in atl:
        for pg in _parse_atlas(p):
            if pg["w"]:
                pg["atlas"] = p.relative_to(root).as_posix()
                pages.append(pg)
    print("  图集页 %d" % len(pages))

    # atlas 自身定位到行（★ 用字典自带 fid；ui 在 gpk 里，fid=murmur3(path) 可用）
    import sqlite3
    db = sqlite3.connect("file:%s?mode=ro"
                         % str(args.db or DEFAULT_DB).replace("\\", "/"), uri=True)
    from toolkit_core import unified_index as _UI
    W = args.window
    need, acache = {}, {}
    for pg in pages:
        h = "%016X" % _UI.path_fid(pg["atlas"].replace("/", "\\"))
        r = acache.get(pg["atlas"])
        if r is None:
            r = db.execute("SELECT container,row_index FROM entries WHERE fid_hex=? LIMIT 1",
                           (h,)).fetchone()
            acache[pg["atlas"]] = r
        if not r:
            pg["ok"] = False
            continue
        pg["ac"], pg["ar"] = r[0], r[1]
        # ★ 多页图集要往后多留几行（去重时可能重指到 +12）
        for d in range(-1, W + 13):
            need.setdefault(r[0], set()).add(r[1] + d)

    look = {}
    for c, rs in need.items():
        rs = set(rs)
        for rr, f in db.execute("SELECT row_index,fid_hex FROM entries WHERE container=?", (c,)):
            if rr in rs:
                look[(c, rr)] = f
    print("  窗口行 %d" % len(look))

    def dims(key):
        c, rr = key
        fp = loc.path(c, rr)
        if fp is None:
            return key, None
        try:
            with fp.open("rb") as fh:
                h = fh.read(148)
        except OSError:
            return key, None
        if len(h) < 128 or h[:4] != b"DDS ":
            return key, None
        hh, ww = _struct.unpack_from("<II", h, 12)
        return key, (ww, hh)

    with ThreadPoolExecutor(max_workers=min(args.workers, _os.cpu_count() or 4)) as ex:
        res = dict(ex.map(dims, list(look.keys())))

    ok = 0
    # ★ 全局去重：一个 (容器, 行号) 只能被【一个】atlas 页认领。
    #   否则同一尺寸的多个 DDS 会让多个 atlas 页撞到同一个 —— 产生互相矛盾的映射
    #   （实测：曾出现同一 fid 对应 3 个不同路径）。
    #   窗口内有多个同尺寸候选时，按「偏移最小」排序取，保证优先取紧邻的。
    claimed = set()
    order = sorted(pages, key=lambda v: (v.get("ar") is None, v.get("ar") or 0))
    for pg in order:
        if pg.get("ar") is None:
            continue
        best = None
        for d in range(-1, W + 13):
            rr = pg["ar"] + d
            k = (pg["ac"], rr)
            if k not in look or res.get(k) != (pg["w"], pg["h"]) or k in claimed:
                continue
            best = (d, rr, k)
            break
        if best is None:
            continue
        d, rr, k = best
        dd = pg["atlas"].rsplit("/", 1)
        pg["body_name"] = (dd[0] + "/" + pg["png"]) if len(dd) > 1 else pg["png"]
        pg["bc"], pg["br"], pg["bfid"], pg["off"] = pg["ac"], rr, look[k], d
        pg["ok"] = True
        pg["_row"] = rr
        claimed.add(k)
        ok += 1
    print("  ★ 认到本体 %d / %d = %.1f%%（全局去重后）"
          % (ok, len(pages), ok / len(pages) * 100 if pages else 0))
    print("  偏移分布: %s" % dict(Counter(v["off"] for v in pages if v.get("ok")).most_common()))
    if args.out:
        o = Path(args.out)
        o.mkdir(parents=True, exist_ok=True)
        (o / "图集页_命名表.csv").write_text(
            "本体真名,宽,高,容器,行号,fid,偏移,来源atlas\n" + "\n".join(
                "%s,%d,%d,%s,%d,%s,%d,%s" % (v["body_name"].replace("/", "\\"), v["w"], v["h"],
                                             v["bc"], v["br"], v["bfid"], v["off"], v["atlas"])
                for v in pages if v.get("ok")), encoding="utf-8")
        _dump([{k: v for k, v in x.items()
                if k not in ("sprites", "used", "_row")} for x in pages],
              str(o / "图集页_全量.json"))
        print("  → %s" % (o / "图集页_命名表.csv"))
    if args.json is not None:
        _dump({"pages": len(pages), "claimed": ok}, args.json)
    return 0


def cmd_atlas_export(args) -> int:
    """★ 把图集本体按 sprite 切出来（Spine atlas 的 xy/size/rotate）。

    Spine atlas 记法：
      xy    = sprite 在图集里的左上角坐标（像素）
      size  = sprite 尺寸
      rotate= true 时 sprite 在图集里【逆时针转 90°】摆放 ⇒ 切完要转回来
    """
    import json as _json
    import struct as _struct
    import csv as _csv
    from concurrent.futures import ThreadPoolExecutor
    import os as _os

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                           / "02_图文音频渲染" / "皮肤链与渲染"))
    import numpy as _np
    from PIL import Image as _Image
    from dds_rgba_canonical import decode_dds_rgba_u8 as _dec

    root = Path(args.restore_root) if args.restore_root else DEFAULT_RESTORE
    out = Path(args.out) if args.out else (DEFAULT_OUTPUT_ROOT / "sprite")
    out.mkdir(parents=True, exist_ok=True)
    work = Path(args.work) if args.work else (out / "_tmp")
    work.mkdir(parents=True, exist_ok=True)
    loc = _artifact_locator()
    dict_path = getattr(args, "dict_path", None) or DEFAULT_NAMES_DICT

    # 命名表（atlas 页 → 本体容器行）
    nm = Path(args.names) if args.names else None
    if nm is None:
        base = ANALYSIS_ROOT
        for cand in (base / "spine图集本体_20260928" / "图集页_命名表.csv",):
            if cand.is_file():
                nm = cand
                break
    if nm is None or not nm.is_file():
        raise SystemExit("[atlas export] 找不到命名表，请先跑 atlas discover --out <dir>，"
                         "再用 --names <dir>/图集页_命名表.csv")

    rows = []
    with nm.open(encoding="utf-8", newline="") as fh:
        for d in _csv.DictReader(fh):
            rows.append(d)
    print("[atlas export] 命名表 %d 条 ｜ 源 %s" % (len(rows), nm))

    # 按 atlas 归组，定位 atlas 文件
    by_atlas = {}
    for d in rows:
        by_atlas.setdefault(d["来源atlas"], []).append(d)
    print("  涉及 atlas %d 个" % len(by_atlas))

    kw = (args.filter or "").lower()
    if kw:
        by_atlas = {k: v for k, v in by_atlas.items() if kw in k.lower()}
        print("  过滤 %r → 剩 atlas %d 个" % (args.filter, len(by_atlas)))

    MAXSP = args.max_sprites
    made = 0
    skip = 0
    sheets = 0

    for a, decls in sorted(by_atlas.items()):
        fp = root / a.replace("/", "\\")
        if not fp.is_file():
            fp = root / a
        if not fp.is_file():
            skip += 1
            continue
        pages = _parse_atlas(fp)
        if not pages:
            skip += 1
            continue
        # 页 → 本体行（按声明的 png 名匹配命名表）
        pgbody = {}
        for d in decls:
            nm_png = d["本体真名"].replace("\\", "/").rsplit("/", 1)[-1]
            pgbody[nm_png] = d
        for pg in pages:
            d = pgbody.get(pg["png"])
            if d is None or not pg["sprites"]:
                continue
            src = loc.path(d["容器"], int(d["行号"]))
            if src is None:
                skip += 1
                continue
            t = work / ("%s_%d.dds" % (Path(a).stem[:24], int(d["行号"])))
            try:
                t.write_bytes(src.read_bytes())
                u8, prov = _dec(str(t), verify_oiio=False)
                sheet = _Image.fromarray(
                    _np.asarray(u8).reshape(prov["height"], prov["width"], 4), "RGBA")
            except Exception:
                skip += 1
                continue
            finally:
                t.unlink(missing_ok=True)

            sheets += 1
            sub = out / Path(a).parent.name if args.group else out
            sub.mkdir(parents=True, exist_ok=True)
            for sp in pg["sprites"]:
                if MAXSP and made >= MAXSP:
                    break
                name = sp["name"].replace("/", "__").replace("\\", "__")
                safe = "".join(c for c in name if c.isalnum() or c in "_-.")[:110] or "s"
                x, y = sp["x"], sp["y"]
                w, h = sp["sw"], sp["sh"]
                rot = sp.get("rot", False)
                if x < 0 or y < 0 or x + (h if rot else w) > sheet.width \
                        or y + (w if rot else h) > sheet.height:
                    continue
                box = (x, y, x + h, y + w) if rot else (x, y, x + w, y + h)
                try:
                    im = sheet.crop(box)
                    if rot:
                        im = im.transpose(_Image.ROTATE_90)
                    im.save(sub / (safe + ".png"))
                    made += 1
                except Exception:
                    pass
        if MAXSP and made >= MAXSP:
            break

    print()
    print("  ★ 切出 sprite %d 张 ｜ 跳过图集 %d 个 ｜ 用了 %d 张图集本体"
          % (made, skip, sheets))
    print("  → %s" % out)
    if args.json is not None:
        _dump({"sprites": made, "sheets": sheets, "skipped": skip}, args.json)
    return 0


def _stamp() -> str:
    import time
    return time.strftime("%Y%m%d_%H%M%S")


# ═══════════════════════════════════════════════════════════════════════════
# 横切：物理探针 locate / fiddiff / ovl
#   ★ 这三条不是「设计出来的」，是 2026-09-28 全量拆包复核时【逼出来的】：
#     当时每一步都只能现写一次性脚本，而且每次都要重推同一批细节
#     （pkg_N.pi 的二进制布局 / overlay 到底是不是 NPK / 哪个容器目录名配哪个 stem）。
#     实现在 toolkit_core.container_probe（唯一实现，别再往 CLI 里抄一份）。
# ═══════════════════════════════════════════════════════════════════════════

def cmd_locate(args) -> int:
    """[①-1] 容器 + 行号 → 产物文件（或 --fid 反查「这个 fid 落在哪一行」）。

    ★ 目录名规则用 container_probe.container_dir_name（与 restore_tree 同一套）。
      实测：`Documents\\script.py314.lc.npk` 与 `script.py314.lc.npk` 会被
      artifact_locator.Locator 用 Path.stem 折成同一个 `script.py314.lc`
      ⇒ 查前者会拿到后者的文件（实测 r100 两文件 953 B vs 751 B，确实不同）。
    """
    from toolkit_core import container_probe as CP

    # ★ 2026-09-29（S5）：默认走【树优先、载荷回退】。
    #   老写法 `CP.Locator(args.product_root or CP.PRODUCT_ROOT)` 把默认值也当显式根传，
    #   于是永远只查载荷 —— 载荷被清后就成了「树里有、locate 说没有」的假阴性。
    loc = CP.Locator(args.product_root) if args.product_root else CP.Locator()
    out: dict = {"product_root": str(loc.root), "hits": [], "miss": []}

    if args.fid:
        for fid in args.fid:
            rows = loc.locate_fid(fid, args.db)
            out["hits"].append({"fid": fid.upper(), "rows": rows})
    else:
        if not args.row:
            print("locate：给了容器就要给行号（或改用 --fid）", file=sys.stderr)
            return 2
        for row in args.row:
            p = loc.path(args.container, row)
            rec = {"container": args.container, "row": row,
                   "artifact": str(p) if p else None,
                   "exists": bool(p and p.is_file())}
            if p and p.is_file():
                rec["bytes"] = p.stat().st_size
                if args.head:
                    rec["head_hex"] = p.open("rb").read(args.head).hex(" ")
            (out["hits"] if p else out["miss"]).append(rec)

    out["stats"] = loc.stats()
    if args.json:
        _dump(out, args.json)
    for h in out["hits"]:
        if "rows" in h:
            print("  %s → %s" % (h["fid"], "未命中" if not h["rows"] else ""))
            for r in h["rows"]:
                print("      %-34s r%-8d %s" % (r["container"], r["row"],
                                                r["artifact"] or "（产物缺失）"))
        else:
            print("  %-34s r%-8d → %s" % (h["container"], h["row"],
                                          h["artifact"] or "（未命中）"))
            if h.get("head_hex"):
                print("      头 %d B：%s" % (args.head, h["head_hex"]))
    for m in out["miss"]:
        print("  ✗ %s r%s 没有产物" % (m["container"], m["row"]))
    if args.fid:
        return 0 if any(h["rows"] for h in out["hits"]) else 5
    return 0 if out["hits"] else 5


def cmd_fiddiff(args) -> int:
    """[①-1] 两个 pkg_N.pi 目录的 fid 增删（可解名字 / 按关键词筛）。

    布局实测：`[u64 count][count × u64 fid]`，长度必须 == 8 + 8*count（container_probe.parse_pi 自检）。
    """
    from toolkit_core import container_probe as CP

    rep = CP.pi_diff(args.a, args.b)
    nm = {}
    if args.dict_path and Path(args.dict_path).is_file():
        nm = json.loads(Path(args.dict_path).read_text(encoding="utf-8"))

    def rows(fids):
        out = []
        for f in fids:
            h = "%016X" % f
            p = nm.get(h)
            if args.named and not p:
                continue
            if args.grep and args.grep.lower() not in (p or "").lower():
                continue
            out.append({"fid": h, "name": p})
        return out

    added, removed = rows(rep["added"]), rows(rep["removed"])
    # ★ 「字典里能给出名字」必须【不带 --named/--grep 过滤】地数，
    #   否则那行会把自己刚加的过滤器算进去，读起来像「字典一条也不认识」。
    named_added = sum(1 for f in rep["added"] if ("%016X" % f) in nm)
    named_removed = sum(1 for f in rep["removed"] if ("%016X" % f) in nm)
    out = {"kind": "fiddiff", "a_dir": rep["a_dir"], "b_dir": rep["b_dir"],
           "a_total": rep["a_total"], "b_total": rep["b_total"], "common": rep["common"],
           "added_n": len(rep["added"]), "removed_n": len(rep["removed"]),
           "named_added": named_added, "named_removed": named_removed,
           "added_shown": len(added), "removed_shown": len(removed),
           "named_dict": str(args.dict_path) if nm else None,
           "added": added[:args.limit], "removed": removed[:args.limit]}
    if args.json:
        _dump(out, args.json)
    print("[fiddiff] %s → %s" % (rep["a_dir"], rep["b_dir"]))
    print("  fid：A %s ｜ B %s ｜ 共有 %s" % (format(rep["a_total"], ","),
                                             format(rep["b_total"], ","),
                                             format(rep["common"], ",")))
    print("  ★ 新增 %s ｜ 移除 %s（字典能给出名字：新增 %d / 移除 %d）"
          % (format(len(rep["added"]), ","), format(len(rep["removed"]), ","),
             named_added, named_removed))
    for tag, lst in (("＋", added), ("－", removed)):
        for r in lst[:args.limit]:
            print("    %s %s  %s" % (tag, r["fid"], r["name"] or "（无名）"))
        if len(lst) > args.limit:
            print("    … 还有 %d 条（--limit 调大）" % (len(lst) - args.limit))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(
            {"a_dir": rep["a_dir"], "b_dir": rep["b_dir"],
             "added": ["%016X" % f for f in rep["added"]],
             "removed": ["%016X" % f for f in rep["removed"]]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("  完整清单 → %s" % args.out)
    return 0


def cmd_ovl(args) -> int:
    """[H-1] overlay 包：entries 看条目表 · unpack 条目级全量解包 + 分类落盘。

    ★ 实测（推翻了「[32B 头] + zstd 帧流」的旧说法）：
      overlay 包**就是普通 NPK 容器** —— 头 32 B 经 AES-ECB 解密后
      offset 8 起是 `NXPK` 魔数 + version=3，条目表可完整读出。
      旧口径「扫 zstd 魔数切块」只覆盖 1741 条里的 371 条：
        instance.layers.1.1.1 声明 390 条，魔数只找到 192 个；
        flag=0 的原始条目（video 包的两个 MP4 段）一条都拿不到。
      所以这里走 la_unpack_core.NpkArchive，不扫魔数。
    """
    from toolkit_core import container_probe as CP

    sub = args.ovl_command
    if sub == "entries":
        rep = CP.overlay_entries(args.path)
        out = {"kind": "ovl", "action": "entries", **rep}
        if args.json:
            _dump(out, args.json)
        print("[ovl entries] %s（%s B）" % (rep["path"], format(rep["bytes"], ",")))
        if rep.get("empty"):
            print("  ★ 空容器（count=0）：只有 32 B 头，没有条目。%s" % (rep["error"] or ""))
            return 0
        if rep["error"]:
            print("  ✗ %s" % rep["error"], file=sys.stderr)
            return 5
        print("  ★ 条目 %d 条 ｜ flag 分布 %s" % (rep["n"], rep["flags"]))
        for e in rep["entries"][:args.limit]:
            print("    #%-5d fid=%s off=%-9d packed=%-9d decoded=%-10d flag=%s"
                  % (e["index"], e["fid"], e["offset"], e["packed"], e["decoded"], e["flag"]))
        if rep["n"] > args.limit:
            print("    … 另有 %d 条（--limit 调大 / --json 全量）" % (rep["n"] - args.limit))
        return 0

    if sub == "unpack":
        rep = CP.overlay_unpack(args.path, args.out, write=not args.dry_run)
        rec = {"kind": "ovl", "action": "unpack", "path": str(args.path),
               "out": rep["out"], "n_pkgs": rep["n_pkgs"], "n_entries": rep["n_entries"],
               "ok": rep["ok"], "failed": rep["failed"], "types": rep["types"],
               "empty_pkgs": rep["empty_pkgs"]}
        if args.json:
            _dump({"entries": rep["entries"], **rec}, args.json)
        print("[ovl unpack] %s → %s" % (args.path, rep["out"]))
        print("  可解析包 %d ｜ ★ 条目 %d 条 → 解出 %d ｜ 失败 %d ｜ 空包 %d"
              % (rep["n_pkgs"], rep["n_entries"], rep["ok"], rep["failed"],
                 len(rep["empty_pkgs"])))
        print("  类型分布：%s" % dict(sorted(rep["types"].items(), key=lambda x: -x[1])))
        for e in rep["empty_pkgs"]:
            print("    ○ 空包 %s（%s）" % (e["pkg"], e["error"]))
        return 0 if not rep["failed"] else 1

    print("未知 ovl 子命令 %r" % sub, file=sys.stderr)
    return 2


def cmd_materialize(args) -> int:
    """[①-1] 把产物按源路径物化成还原树（硬链接，不复制）。

    ★ 这条命令早该有：``toolkit_core/restore_tree.py`` 的模块 docstring 第 30 行
      写着「CLI 对应：``toolkit_cli.py materialize``」—— 但 CLI 里从来没有注册过它。
      2026-09-28 做还原树复核时，想「按最新字典重建一份」只能自己写脚本直接调模块。

    ★ 另一处坑：``restore_tree.materialize(names_dict=None)`` 的**默认字典是写死的
      v6 → v5 → v3**（不是 paths 里那个「取版本号最大」的 DEFAULT_NAMES_DICT）。
      实测：v6 能命名 992,121 行（43.12%），v13 能命名 1,030,452 行（44.79%），
      差 38,331 行 —— 直接调模块会静默少 3.8 万条名字。所以这里**永远显式传最新字典**。
    """
    try:
        from toolkit_core import restore_tree as RT
        from toolkit_core.paths import DEFAULT_NAMES_DICT as _LATEST
    except Exception as exc:                       # noqa: BLE001
        print("materialize 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5

    out_root = Path(args.out) if args.out else DEFAULT_RESTORE
    src_root = Path(args.src_root) if args.src_root else None
    nd = Path(args.dict_path) if args.dict_path else _LATEST
    if not nd.is_file():
        print("materialize：名字字典不存在：%s" % nd, file=sys.stderr)
        return 6

    # ★ 硬链接不能跨卷。实测：把 --out 指到 C: 而产物在 E: 时，os.link 每条都抛
    #   OSError，materialize() 把它计进 errors（实测 54,292 条全失败、linked=0），
    #   而命令本身"跑完了" —— 看起来像成功，其实一个文件都没出来。
    #   所以在动手之前先判卷，拒绝执行并说清怎么改。
    import os as _os                                     # CLI 模块级没导 os，就地取
    from toolkit_core import paths as _P
    eff_src = src_root or (_P.DEFAULT_OUTPUT_ROOT / "全量实测_20260926" / "files")
    if not args.copy:
        d_out = _os.path.splitdrive(str(Path(out_root).resolve()))[0].lower()
        d_src = _os.path.splitdrive(str(Path(eff_src).resolve()))[0].lower()
        if d_out != d_src:
            print("materialize 拒绝执行：硬链接不能跨卷（--out 在 %s: ，产物在 %s:）。"
                  % (d_out or "?", d_src or "?"), file=sys.stderr)
            print("  两个选择：① --out 换成与产物同卷的目录；"
                  "② 确实要落到别的卷就显式 --copy（会把 %d 条全部真复制，占空间）。"
                  % 0, file=sys.stderr)
            return 2

    if not args.quiet:
        print("[materialize] 字典 %s" % nd)
        print("  产物根 %s" % (src_root or "（模块默认）"))
        print("  输出   %s ｜ %s" % (out_root, "复制" if args.copy else "硬链接"))
    try:
        st = RT.materialize(out_root=out_root, db_path=args.db, names_dict=nd,
                            src_root=src_root,
                            containers=(args.container or None),
                            link=not args.copy, include_unnamed=not args.no_unnamed)
    except OSError as exc:
        print("materialize：写失败：%s" % exc, file=sys.stderr)
        return 6
    rep = {"kind": "materialize", "out": str(out_root), "dict": str(nd),
           "src_root": str(src_root) if src_root else None,
           "link": not args.copy, "containers": st.containers, "rows": st.rows,
           "named": st.named, "unnamed": st.unnamed, "missing": st.missing,
           "linked": st.linked, "errors": st.errors,
           "coverage_pct": round(100.0 * st.named / max(1, st.rows), 3)}
    if args.json:
        _dump(rep, args.json)
    if not args.quiet:
        print(str(st))
        print("  覆盖率 %.2f%%" % rep["coverage_pct"])
    return 0 if not st.errors else 1


# ═══════════════════════════════════════════════════════════════════════════
# 横切：工具 × 段位 映射（map）
# ═══════════════════════════════════════════════════════════════════════════

def cmd_map(args) -> int:
    """[横切] 打印「工具 × 段位」映射表（判据与归属在 toolkit_core.tool_seg_map）。"""
    try:
        from toolkit_core import tool_seg_map as M
    except Exception as exc:
        print("map 子命令不可用：%r" % (exc,), file=sys.stderr)
        return 5
    try:
        root = M.default_toolkit_root()
    except RuntimeError as exc:
        print("map：%s" % exc, file=sys.stderr)
        return 3

    rows = M.collect(root, include_archive=True)
    by_seg = commands_by_seg()
    want: list[str] = []
    for q in (args.seg or ()):
        hits = M.match_seg(q)
        if not hits:
            print("map：--seg %s 不匹配任何段位；可用：%s" % (q, " · ".join(M.SEGMENTS)),
                  file=sys.stderr)
            return 2
        want += [h for h in hits if h not in want]
    sel = [r for r in rows if r["seg"] in want] if want else rows

    if args.json:
        _dump({"kind": "map", "segment": "横切", "criterion": M.CRITERION,
               "totals": M.totals(sel),
               "segments": [{k: v for k, v in b.items() if k != "items"}
                            for b in M.summarize(sel) if not want or b["seg"] in want],
               "cli_by_seg": by_seg,
               "items": sel}, args.json)
        return 0

    print(M.render_text(rows, seg_filter=(want or None), show_files=bool(args.files),
                        by_seg=by_seg, limit=(None if args.limit == 0 else args.limit)))
    if args.write:
        paths = M.write_artifacts(rows, root / "docs", by_seg=by_seg)
        print("已落盘：%s ｜ %s" % (paths["md"], paths["json"]))
    unknown = [r for r in rows if r["seg"] == "未分类"]
    if unknown:
        print("⚠ 有 %d 个文件没有命中任何判据（段位=未分类），需人工定段。" % len(unknown),
              file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    COMMANDS.clear()          # 每次构建都重建登记表（可重复调用）
    parser = argparse.ArgumentParser(
        prog="lifeafter-toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="明日之后拆包器统一入口（文件索引优先；源包只读）",
        epilog="""\
命令按【三线三带】分组（子命令 help 开头的方括号就是段位，可直接 grep）：

  ── 带H 热更定位带（三条线的入口：先知道「哪里变了」）────────────
    H-1 版本清单对比    delta fetch · delta diff · delta families
    H-2 本地冻结与终态   snapshot scan · snapshot diff
    H-3 包级归因        （当前由 delta families 承担；家族词表待补）

  ── ① 解码定位复原线（源包 → 事实）──────────────────────────
    ①-0 索引地基        index build · index status · verify · overview
    ①-1 定位与复原       find · extract · export · restore · thfb · bindict-check
                        bridge-audit · resolver locate/tree/dump/bridge-gpk
                        names build/lookup/stats
    ①-2 批量质检        query · bulk · identify · decode-audit

  ── ② 图文音频渲染线（事实 → 能看能听）─────────────────────
    ②-1 三维装配        glb · sheet
    ②-2 媒体定位        tex · audio · texscan scan
    ②-3 三维出图校准     render

  ── ③ 前端展示交互线（东西 → 人能点的页面）──────────────────
    ③-1 页面与看板 / ③-2 服务与契约 / ③-3 资产落地与投影
        ⇒ 工具层暂无命令：前端工具在 04_站点/web/tools/，
          段位归属见 run_all.py map --json

  ── 带D 数据契约带（横切：接口）───────────────────────────
      --json 出口与返回码：0 通过 / 1 有错但跑完 / 2 用法错 /
      3 索引不可用 / 4 自检未过 / 5 未命中 / 6 输入不可用

  ── 带Q 质量·交付·治理带（横切：闸门）─────────────────────
      00_共享核心/测试（pytest -q ⇒ 105 passed）· 站点 tools/checks.py 判据

  ◆ 横切段的工具不产出业务产物：run_all / exe_cli（入口壳）· 图形界面/app（GUI）
    · 调度与限流（scheduler / throttle）· 项目根定位（paths）· 测试
  ◆ 完整「工具 × 段位」映射：run_all.py map
    （--seg ②-2 只看一段 · --files 连文件清单 · --json 机器读 · --write 落盘 docs/）

路径定位（不再硬编码）：① --root  ② 环境变量 LA_ROOT  ③ exe 同级向上
                          ④ 源码树向上；找不到就明确报错，不猜。
""")
    parser.add_argument("--root", help="项目根（覆盖环境变量与自动探测）")
    # ── ★ 智能调度（全局开关：所有子命令都吃得到）──────────────────
    parser.add_argument("--jobs", default=None,
                        help="★ 并行数：auto（默认，按硬件+任务类型自动）或具体数字（如 8）")
    parser.add_argument("--cpu-limit", dest="cpu_limit", type=float, default=None,
                        help="★ 整机 CPU 占用上限 %%（默认 80，超了自动让路）")
    parser.add_argument("--gpu-limit", dest="gpu_limit", type=float, default=None,
                        help="★ GPU 占用上限 %%（默认 80）")
    parser.add_argument("--gpu", choices=["auto", "on", "off"], default="auto",
                        help="★ GPU 加速：auto（默认，能上才上）/ on（强制试）/ off（禁用）")
    parser.add_argument("--no-throttle", dest="no_throttle", action="store_true",
                        help="★ 关掉反馈限流（跑满机器，适合没人用电脑时）")
    sub = parser.add_subparsers(dest="command", required=True)
    ex = _sp(sub, "export", help="[①-1] 解析结果 → 表格文件（通用导出器）")
    ex.add_argument("source", help=".bin 条目载荷，或逻辑路径 / fid（经索引提取）")
    ex.add_argument("--out", required=True, help="输出文件（扩展名决定格式：csv/json/md）")
    ex.add_argument("--format", default="csv", choices=["csv", "json", "md"],
                    help="输出格式（默认 csv）")
    ex.add_argument("--family", default="auto", choices=["auto", "d6", "kj1", "hd86"],
                    help="指定表族；默认 auto 逐族试并如实报告各自结果")
    ex.add_argument("--no-jump", action="store_true", help="不解析 0x27 跳转组（更快）")
    ex.add_argument("--db", type=Path, default=DEFAULT_DB)
    ex.add_argument("--res-root", type=Path)
    ex.add_argument("--json", help="把导出摘要写到该文件")
    ex.set_defaults(func=cmd_export)

    index = _sp(sub, "index", help="[①-0] 统一文件索引")
    index_sub = index.add_subparsers(dest="index_command", required=True)
    _inherit(index_sub, "①-0", "index")     # 子子命令继承段位（它们没有 [段位] 前缀）

    build = _sp(index_sub, "build", help="构建/原子更新 SQLite 索引")
    build.add_argument("--res-root", type=Path, default=DEFAULT_RES_ROOT)
    build.add_argument("--fpk-index", type=Path, default=DEFAULT_FPK_INDEX)
    build.add_argument("--db", type=Path, default=DEFAULT_DB)
    build.add_argument("--include", nargs="+", choices=("gpk", "fpk", "npk"), default=("gpk", "fpk", "npk"))
    build.add_argument("--quiet", action="store_true"); build.add_argument("--json")
    build.add_argument("--no-sidecar", action="store_true",
                       help="不同步 lifeafter_files_build.json")
    build.set_defaults(func=cmd_index_build)
    status = _sp(index_sub, "status", help="检查索引完整性与源包是否变化")
    status.add_argument("--db", type=Path, default=DEFAULT_DB); status.add_argument("--res-root", type=Path)
    status.add_argument("--no-source-check", action="store_true"); status.add_argument("--json")
    status.add_argument("--deep", action="store_true",
                        help="深层校验：逐容器重算 sha256 与库内比对（要读全部字节，几十秒级）。"
                             "不加则只比「名字+大小+mtime」指纹，检不出「大小与 mtime 未变但内容变了」")
    status.add_argument("--no-sidecar", action="store_true",
                        help="不同步 lifeafter_files_status.json")
    status.set_defaults(func=cmd_index_status)
    find = _sp(sub, "find", help="[①-1] 逻辑路径查全部物理候选")
    find.add_argument("path"); find.add_argument("--db", type=Path, default=DEFAULT_DB)
    find.add_argument("--res-root", type=Path); find.add_argument("--variants", action="store_true")
    find.add_argument("--deep-variants", action="store_true"); find.add_argument("--json")
    find.set_defaults(func=cmd_find)
    extract = _sp(sub, "extract", help="[①-1] 按索引定点提取一个条目")
    extract.add_argument("path"); extract.add_argument("output")
    extract.add_argument("--db", type=Path, default=DEFAULT_DB); extract.add_argument("--res-root", type=Path)
    extract.add_argument("--container", help="多命中时按容器路径子串筛选")
    extract.add_argument("--row", type=int, help="多命中时按原始条目号筛选")
    extract.add_argument("--variants", action="store_true"); extract.add_argument("--deep-variants", action="store_true")
    extract.add_argument("--raw", action="store_true", help="输出压缩载荷，不解码")
    extract.add_argument("--force", action="store_true", help="允许覆盖既有输出"); extract.add_argument("--json")
    extract.set_defaults(func=cmd_extract)
    verify = _sp(sub, "verify", help="[①-0] SQLite + 三条已知路径端到端自检")
    verify.add_argument("--db", type=Path, default=DEFAULT_DB); verify.add_argument("--res-root", type=Path)
    verify.add_argument("--no-source-check", action="store_true"); verify.add_argument("--json")
    verify.add_argument("--no-sidecar", action="store_true",
                        help="不同步 lifeafter_files_verify.json")
    verify.set_defaults(func=cmd_verify)
    glb = _sp(sub, "glb", help="[②-1] 一个或多个 .mesh → 单 GLB（世界坐标拼接 + 自检报告）")
    glb.add_argument("meshes", nargs="+", help="输入 .mesh 路径（可多个；顶点已是世界坐标，直接拼接）")
    glb.add_argument("--mat", type=Path, help=".c159 材质文件（可选，记进 GLB extras/报告）")
    glb.add_argument("--tex", type=Path, help="贴图目录（可选，按槽位后缀选 a/n/m）")
    glb.add_argument("--out", type=Path, help="输出 .glb（默认 03_执行\\90_临时\\glb_out\\<首件名>.glb）")
    glb.add_argument("--force", action="store_true", help="允许覆盖已存在的输出")
    glb.add_argument("--json", help="自检报告 JSON 输出路径")
    glb.set_defaults(func=cmd_glb)

    # ── ②线其余段位（原先 57 个脚本只有 glb 一个进了 CLI） ──
    sh = _sp(sub, "sheet", help="[②-1] 装配帧 .c159 → 材质/部件表（配对规则 C159_PARAM_PAIRING）")
    sh.add_argument("mtl", nargs="+", help=".c159 文件 / 目录 / glob")
    sh.add_argument("--bind", type=Path, help="绑定文件（可选）")
    sh.add_argument("--out", type=Path, help="输出目录（默认 03_执行\\90_临时\\sheet_out）")
    sh.add_argument("--strict", action="store_true", help="有失败则退出码 1（默认 0）")
    sh.add_argument("--quiet", action="store_true")
    sh.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    sh.set_defaults(func=cmd_sheet)

    tx = _sp(sub, "tex", help="[②-2] 贴图 → PNG（只走 dds_rgba_canonical 规范入口）")
    tx.add_argument("target", nargs="+", help=".dds/.ktx 文件 / 目录 / glob")
    tx.add_argument("--ext", action="append", default=None,
                    help="扩展名（可多次；默认 dds,ktx）")
    tx.add_argument("--out", type=Path, help="输出目录（默认 03_执行\\90_临时\\tex_out）")
    tx.add_argument("--force", action="store_true", help="允许覆盖已存在的 PNG")
    tx.add_argument("--no-verify", action="store_true", help="跳过 OIIO 交叉校验（默认校验）")
    tx.add_argument("--strict", action="store_true", help="有失败则退出码 1（默认 0）")
    tx.add_argument("--quiet", action="store_true")
    tx.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    tx.set_defaults(func=cmd_tex)
    if tx.get_default("ext") is None:      # argparse 的 append 默认 None ⇒ 补默认值
        tx.set_defaults(ext=["dds", "ktx"])

    au = _sp(sub, "audio", help="[②-2] 音效轨道 .sfx → 帧表 JSON（节点树/色帧/绑定贴图）")
    au.add_argument("src", nargs="+", help=".sfx 文件 / 目录 / glob")
    au.add_argument("--ext", action="append", default=None,
                    help="扩展名（可多次；默认 sfx,xml）。★ 本项目的产物按【检测类型】命名，"
                         ".sfx 常落成 .text ⇒ 可用 --ext text")
    au.add_argument("--out", type=Path, help="输出目录（默认 03_执行\\90_临时\\audio_out）")
    au.add_argument("--strict", action="store_true", help="有失败则退出码 1（默认 0）")
    au.add_argument("--quiet", action="store_true")
    au.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    au.set_defaults(func=cmd_audio)
    if au.get_default("ext") is None:
        au.set_defaults(ext=["sfx", "xml"])

    rd = _sp(sub, "render", help="[②-3] 材质分层出图（非交付面 PNG + layers_trace.json）")
    rd.add_argument("mesh", help="输入 .mesh")
    rd.add_argument("tex_dir", help="贴图目录（可配合 --tex-map 指向任意命名的文件）")
    rd.add_argument("--out", type=Path, help="输出目录（默认 03_执行\\90_临时\\render_out）")
    rd.add_argument("--materials", type=Path, help=".c159 材质文件（可选）")
    # ★ 2026-09-28 修：这里原来写 choices=["smooth","steep"] ——
    #   render_material_layers 的实际分支是 smooth/rough/const，'steep' 不存在
    #   ⇒ CLI 放行了不存在的值（静默等于 smooth），却挡住了真实的 --polarity rough。
    rd.add_argument("--polarity", choices=["smooth", "rough", "const"],
                    help="4013 遮罩极性（默认 smooth=直接用 R；rough=1-R；const=0.5 对照）")
    rd.add_argument("--dual", action="store_true", help="双部件并排出图")
    rd.add_argument("--dual-sep", type=float, help="双部件间距（默认 0.62）")
    # ★ 2026-09-28 加：tex（②-2）产物按行号命名，render（②-3）只认 tex_<槽位>.png，
    #   两个命令原本接不上（实测 FileNotFoundError）。--tex-map 把它们接起来。
    rd.add_argument("--tex-map", action="append", default=[], metavar="槽位=文件",
                    help="直接指定槽位贴图（可重复），如 --tex-map 4011=00001240.png；"
                         "相对路径按 tex_dir 解析")
    rd.add_argument("--input-manifest", type=Path,
                    help="输入清单 JSON（默认 tex_dir/_input_manifest.json）")
    rd.add_argument("--quiet", action="store_true")
    rd.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    rd.set_defaults(func=cmd_render)

    # ── 收编两个「自带 argparse 的孤立入口」（命令定义单点化）──
    # ★ 公共选项挂到每个子命令上（用 parents=），否则只能写成 `resolver --quiet locate P`，
    #   而 `resolver locate P --quiet` 会报 unrecognized arguments。
    _rv_common = argparse.ArgumentParser(add_help=False)
    _rv_common.add_argument("--res", default=r"E:\mrzh\res", help="资源根（默认 E:\\mrzh\\res）")
    _rv_common.add_argument("--quiet", action="store_true")
    _rv_common.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")

    rv = _sp(sub, "resolver", help="[①-1] 资源物理桥定位器（原 resource_resolver 独立入口）")
    rv_sub = rv.add_subparsers(dest="resolver_command", required=True)
    _inherit(rv_sub, "①-1", "resolver")

    _rvp = _sp(rv_sub, "locate", parents=[_rv_common], help="定位逻辑路径所在包/条目")
    _rvp.add_argument("path")
    _rvt = _sp(rv_sub, "tree", parents=[_rv_common], help="递归解析一套资源")
    _rvt.add_argument("path"); _rvt.add_argument("--depth", type=int, default=3)
    _rvd = _sp(rv_sub, "dump", parents=[_rv_common], help="解出并保存单个资源")
    _rvd.add_argument("path"); _rvd.add_argument("out")
    _rvb = _sp(rv_sub, "bridge-gpk", parents=[_rv_common], help="用 c1c2 给 GPK 匿名条目对接 fid")
    _rvb.add_argument("gpk")
    rv.set_defaults(func=cmd_resolver)

    ts = _sp(sub, "texscan", help="[②-2] 匿名 GPK 纹理颜色筛选 / 未上线候选")
    ts_sub = ts.add_subparsers(dest="texscan_command", required=True)
    _inherit(ts_sub, "②-2", "texscan")

    _tss = _sp(ts_sub, "scan")
    _tss.add_argument("unpacked_dir")
    _tss.add_argument("--out", required=True)
    _tss.add_argument("--res", default=r"E:\mrzh\res")
    _tss.add_argument("--color", default="gold")
    _tss.add_argument("--all", action="store_true", help="不只看独有（默认只看独有）")
    _tss.add_argument("--min-side", type=int, default=0)
    _tss.add_argument("--top", type=int, default=60)
    ts.set_defaults(func=cmd_texscan)

    # ── ②-2 声明路径解析（resolve_declared_paths 的孤立入口收编）──
    dc = _sp(sub, "declared",
             help="[②-2] 声明文件(.c159/.mtg/.sfx)里的资产路径 → 容器 HIT/MISS 矩阵")
    dc.add_argument("inputs", nargs="*", help="声明文件（支持 *.c159 / *.sfx 通配）")
    dc.add_argument("--res-root", default=r"E:\mrzh\res", help="游戏资源根（默认 E:\\mrzh\\res）")
    dc.add_argument("--fpk-index", type=Path, help="既有 fpk 索引 JSON")
    dc.add_argument("--index", type=Path, help="复用 gpk_npk_index 产出的紧凑 TSV 索引")
    dc.add_argument("--ext", action="append", help="扩展名白名单（可重复）")
    dc.add_argument("--variants", action="store_true", help="展开候选名（分隔符/大小写/换扩展名）")
    dc.add_argument("--deep-variants", action="store_true", help="再补 _lod01/_1/_high 等后缀变体")
    dc.add_argument("--dump-strings", action="store_true", help="只抽路径并打印，不解析")
    dc.add_argument("--no-detail", action="store_true", help="只输出汇总矩阵")
    dc.add_argument("--quiet", action="store_true")
    dc.add_argument("--json", type=Path, help="结果 JSON 落盘路径")
    dc.set_defaults(func=cmd_declared)

    # ── ①-5 热更增量取证（只比服务端清单，不碰本地客户端目录）──
    dl = _sp(sub, "delta", help="[H-1] 热更增量取证：release(正式服) vs playertest(测试服) 差在哪")
    dl_sub = dl.add_subparsers(dest="delta_command", required=True)
    _inherit(dl_sub, "H-1", "delta")

    _dlf = _sp(dl_sub, "fetch", help="拉取各入口版本清单到本地缓存")
    _dlf.add_argument("--entry", action="append",
                      help="只拉指定入口（可多次；默认全部）")
    _dlf.add_argument("--cache", type=Path, help="缓存目录（默认 03_执行\\10_索引\\patch_manifests）")
    _dlf.add_argument("--quiet", action="store_true")
    _dlf.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _dlf.set_defaults(func=cmd_delta)

    for _name, _help in (("diff", "diff 两份清单：新增/删除/变更的包"),
                         ("families", "只按家族聚合（哪个族有新东西）")):
        _p = _sp(dl_sub, _name, help=_help)
        _p.add_argument("--pair", nargs=2, metavar=("A", "B"),
                        help="对比哪两份清单（默认 release playertest）")
        _p.add_argument("--keys", choices=["ext", "main"], default="ext",
                        help="比哪张表：ext=filesNN_2（以 .npk 包为主，默认）· main=filesNN")
        _p.add_argument("--limit", type=int, default=30, help="明细最多列几条（默认 30）")
        _p.add_argument("--cache", type=Path, help="缓存目录（默认 03_执行\\10_索引\\patch_manifests）")
        _p.add_argument("--out", type=Path, help="完整报告落盘路径")
        _p.add_argument("--quiet", action="store_true")
        _p.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
        _p.set_defaults(func=cmd_delta)

    # ── 带 H · H-2 本地容器快照与终态判定（只读 E:\mrzh）──
    # ── 带 H · H-1 扩展：官方 CDN 包清单 pkg_N.pi（fid 级）──
    _dlp = _sp(dl_sub, "pkg",
               help="[H-1] 官方 CDN 包清单 pkg_N.pi：下载 / 查看 / fid 级 diff")
    _dlp_sub = _dlp.add_subparsers(dest="pkg_command", required=True)
    _inherit(_dlp_sub, "H-1", "delta pkg")

    _pf = _sp(_dlp_sub, "fetch", help="下载某入口的 pkg_1..17.pi（约 18 MB/版本）")
    _pf.add_argument("--entry", default="release", help="入口（默认 release；见 delta fetch）")
    _pf.add_argument("--out", type=Path, help="落盘目录（不给则只报不落）")
    _pf.add_argument("--only", help="只下这几个包，逗号分隔，如 1,2,3")
    _pf.add_argument("--timeout", type=float, default=120.0)
    _pf.add_argument("--quiet", action="store_true")
    _pf.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _pf.set_defaults(func=cmd_delta)

    _pn = _sp(_dlp_sub, "info", help="看某入口的 CDN 目录名 / 版本 / 包顺序 / 关键开关")
    _pn.add_argument("--entry", default="release")
    _pn.add_argument("--timeout", type=float, default=30.0)
    _pn.add_argument("--quiet", action="store_true")
    _pn.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _pn.set_defaults(func=cmd_delta)

    _pdd = _sp(_dlp_sub, "diff", help="两个已下载版本目录做 fid 级 diff（新增/移除）")
    _pdd.add_argument("--a", type=Path, required=True, help="A 版本目录（里面是 pkg_N.pi）")
    _pdd.add_argument("--b", type=Path, required=True, help="B 版本目录")
    _pdd.add_argument("--limit", type=int, default=12, help="明细最多列几条（默认 12）")
    _pdd.add_argument("--out", type=Path, help="完整报告落盘路径")
    _pdd.add_argument("--quiet", action="store_true")
    _pdd.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _pdd.set_defaults(func=cmd_delta)

    _pow = _sp(_dlp_sub, "owner",
               help="查 fid 属于哪个官方包（H-3 新版；用官方 pkg_N.pi 替代前缀猜包）")
    _pow.add_argument("fid", nargs="+", help="一个或多个 16 位 hex fid")
    _pow.add_argument("--pkg-dir", type=Path, required=True,
                      help="已下载的版本目录（含 pkg_N.pi）")
    _pow.add_argument("--quiet", action="store_true")
    _pow.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _pow.set_defaults(func=cmd_delta)

    # ── 带 H · 热更 overlay 全量定位（客户端状态 → 下载 → 解包 → 定位）──
    _ov = _sp(dl_sub, "overlay",
              help="[H-2] 热更 overlay 全量定位：读客户端状态 → 下载/解包/定位到本地行")
    _ov_sub = _ov.add_subparsers(dest="overlay_command", required=True)
    _inherit(_ov_sub, "H-2", "delta overlay")

    _ol = _sp(_ov_sub, "list", help="读客户端状态，列出本次热更的 overlay 包清单")
    _ol.add_argument("--client-root", type=Path, default=Path(r"E:\mrzh"),
                     help="客户端根（默认 E:\\\\mrzh，只读）")
    _ol.add_argument("--quiet", action="store_true")
    _ol.add_argument("--json", nargs="?", const="-")
    _ol.set_defaults(func=cmd_delta)

    _of = _sp(_ov_sub, "fetch", help="按清单从官方 CDN 下载 overlay 包（幂等）")
    _of.add_argument("--client-root", type=Path, default=Path(r"E:\mrzh"))
    _of.add_argument("--out", type=Path, required=True, help="落盘目录")
    _of.add_argument("--timeout", type=float, default=300.0)
    _of.add_argument("--quiet", action="store_true")
    _of.add_argument("--json", nargs="?", const="-")
    _of.set_defaults(func=cmd_delta)

    _oc = _sp(_ov_sub, "locate",
              help="解包 + 用内容指纹索引定位每个块到「容器+行号」（需先 content build）")
    _oc.add_argument("--dir", type=Path, required=True, help="overlay 包目录")
    _oc.add_argument("--out", type=Path, help="完整报告落盘路径")
    _oc.add_argument("--quiet", action="store_true")
    _oc.add_argument("--json", nargs="?", const="-")
    _oc.set_defaults(func=cmd_delta)

    # ── 带 H · 热更线总入口（一条命令跑完全流程）──
    hf = _sp(sub, "hotfix",
             help="[带 H] 热更线总入口：清单 → 下载 → 解包定位 → 官方元数据 → fid 级 diff")
    hf_sub = hf.add_subparsers(dest="hotfix_command", required=True)
    _inherit(hf_sub, "H-1", "hotfix")
    for _name, _h in (("all", "全流程：下载 + 解包定位 + 官方对比 + 报告"),
                      ("report", "只出报告（不下载，用已有产物）")):
        _p = _sp(hf_sub, _name, help=_h)
        _p.add_argument("--out", type=Path, required=True, help="产物与报告目录")
        _p.add_argument("--client-root", type=Path, default=Path(r"E:\mrzh"),
                        help="客户端根（默认 E:\\mrzh，只读）")
        _p.add_argument("--entry", default="release", help="官方清单入口（默认 release）")
        _p.add_argument("--cache", type=Path, help="清单缓存目录")
        _p.add_argument("--pkg-cache", type=Path,
                        help="含 rel/ 与 pt/ 两版本 pkg_N.pi 的目录（启用第 5 步 fid diff）")
        _p.add_argument("--timeout", type=float, default=300.0)
        _p.add_argument("--quiet", action="store_true")
        _p.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
        _p.set_defaults(func=cmd_hotfix)

    # ★ 标准交付结构：把热更产物铺成规范目录（对标 Intelli-verse-X / evrFileTools / ree-pak-rs）
    hb = _sp(hf_sub, "bundle",
             help="★ 生成【标准交付结构】：还原树 / 文字表 / 影音图文表 / 图集 / 变更清单 / 未归类")
    hb.add_argument("--out", type=Path, required=True,
                    help="交付目录（同时作为报告与 pkgs 的读取处）")
    hb.add_argument("--report", type=Path, help="hotfix_report.json（默认 <out>/hotfix_report.json）")
    hb.add_argument("--pkgs", type=Path, help="原始包目录（默认 <out>/pkgs）")
    hb.add_argument("--pkg-cache", dest="pkg_cache", type=Path,
                    help="★ 含 rel/ 与 pt/ 两版本 pkg_N.pi 的目录 —— 给了才能拿到「新增/移除行」")
    hb.add_argument("--overlay-only", dest="overlay_only", action="store_true",
                    help="★ 明确只做 overlay 帧（产物不完整，默认【不允许】不给 --pkg-cache）")
    hb.add_argument("--png", action="store_true",
                    help="★ 把 DDS 额外转成 PNG 放进 03_影音图文表/图片（默认只放原始 DDS）")
    hb.add_argument("--product-root", dest="product_root", type=Path,
                    help="本地产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    hb.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT,
                    help="名字字典（默认取最新版）")
    hb.add_argument("--text-tables", dest="text_tables", type=Path,
                    help="文字表汇总 JSON（{表: [文案...]}）；不给则按「本次未涉及」写说明")
    hb.add_argument("--text-src", dest="text_src", type=Path,
                    help="全量文字表汇总的来源目录（默认自动找 30_分析/配置表中文_* 与 配置表加密攻关_*）")
    hb.add_argument("--text-note", dest="text_note", help="文字表说明文字")
    hb.add_argument("--struct-src", dest="struct_src", type=Path,
                    help="★ 表结构解析产物根（默认自动找 30_分析/表结构解析_*）—— 用于把文案"
                         "带成【表名+字段名+行ID】的结构化版；拿不到就回退裸串版")
    hb.add_argument("--pre-pkg", dest="pre_pkg", type=Path,
                    help="★ 热更【前】的整包 script.npk —— 给行级 diff 用"
                         "（默认自动找 02_资料/源包/pre_update_*/raw/）")
    hb.add_argument("--post-pkg", dest="post_pkg", type=Path,
                    help="★ 热更【后】的整包 script.npk（默认自动找 post_update_*/raw/）")
    hb.add_argument("--workers", type=int, default=24)
    hb.add_argument("--verbose", action="store_true")
    hb.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    hb.set_defaults(func=cmd_hotfix_bundle)

    # ★ 行级热更 diff：两个 script 包 → 哪一【行】新增/移除/改了（补包级/fid 级的缺口）
    hr = _sp(hf_sub, "rows",
             help="★ 行级热更 diff：两个 script 包逐行比，出【新增/移除/真内容变更】")
    hr.add_argument("--pre", type=Path, required=True,
                    help="热更【前】的整包 script.npk（如 02_资料/源包/pre_update_*/raw/script.py314.lc.npk）")
    hr.add_argument("--post", type=Path, required=True,
                    help="热更【后】的整包 script.npk")
    hr.add_argument("--tables", nargs="*",
                    help="要比的表（短名，如 fashion_data_chs.py）；默认 = 时装族")
    hr.add_argument("--table-file", dest="table_file", type=Path,
                    help="从文件读表名清单（每行一个，如 02_文字表/本次变更文字表_表名清单.txt）")
    hr.add_argument("--filter", dest="kw",
                    help="按关键词筛表名（正则，如 'fashion|appear'）")
    hr.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT,
                    help="名字字典（默认取最新版）")
    hr.add_argument("--out", type=Path, required=True, help="产物目录")
    hr.add_argument("--html", action="store_true", help="额外出一份 md（默认出 md + json）")
    hr.add_argument("--quiet", action="store_true")
    hr.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    hr.set_defaults(func=cmd_hotfix_rows)

    # ★ 客户端补丁日志（plcoht_ag，XOR 0xAA）：会话时间 / 逐文件版本串 fver / 期望清单 / 本地对照
    hp = _sp(hf_sub, "patchlog",
             help="★ 读客户端补丁日志 plcoht_ag（XOR 0xAA）：会话时间 / 逐文件版本串 fver "
                  "/ 期望清单 / 本地对照")
    hp.add_argument("--client-root", type=Path, default=Path(r"E:\mrzh"),
                    help="客户端根（默认 E:\\mrzh，只读）")
    hp.add_argument("--log", type=Path, action="append",
                    help="指定日志文件（可多次；默认自动找 Documents/plcoht_ag[.1]）")
    hp.add_argument("--find", help="按关键词过滤清单路径（正则，如 'script|gres|character'）")
    hp.add_argument("--limit", type=int, default=12, help="每条日志样例最多列几条（默认 12）")
    hp.add_argument("--no-local-check", dest="no_local_check", action="store_true",
                    help="跳过「期望大小 vs 本地实测」对照")
    hp.add_argument("--out", type=Path, help="产物目录（出 md + json）")
    hp.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    hp.set_defaults(func=cmd_hotfix_patchlog)

    # ★ S3：热更【就地增补】到 41_还原树（不再单独产还原树）
    ha = _sp(hf_sub, "apply",
             help="★ 把一次热更就地增补到 41_还原树（增/删/补 + 台账）；默认 dry-run")
    ha.add_argument("--from-tree", dest="from_tree", type=Path,
                    help="资源层来源：某次热更已铺好的还原树目录（如交付里的 01_还原树）")
    ha.add_argument("--script-pack", dest="script_pack", type=Path,
                    help="脚本层来源：script.py314.lc.npk")
    ha.add_argument("--tree", type=Path,
                    help="目标还原树（默认 03_执行\\41_还原树 = 唯一权威）")
    ha.add_argument("--container", help="★ 脚本层容器名（默认从 --container-dir 反推；"
                                       "容器名要带前缀，如 Documents\\script.py314.lc.npk）")
    ha.add_argument("--index-db", dest="index_db", type=Path,
                    help="脚本层定位索引（默认 10_索引/indexes/lifeafter_files.sqlite3）")
    ha.add_argument("--container-dir", dest="container_dir",
                    help="脚本层容器目录名（默认 Documents__script.py314.lc）")
    ha.add_argument("--dict", dest="dict_path", type=Path,
                    help="名字字典（默认取最新版）")
    ha.add_argument("--real", action="store_true",
                    help="★ 真写（不加此参数只做 dry-run —— 保护唯一权威产物）")
    ha.add_argument("--force", action="store_true",
                    help="★ 跳过「相同 0 但有新增/覆盖」的安全守卫（默认拒绝写入）")
    ha.add_argument("--out", type=Path, help="报告目录（默认 30_分析\\热更就地增补_<时间>）")
    ha.set_defaults(func=cmd_hotfix_apply)

    # ★★ 2026-10-01：脚本模块方言读取（NeoX 魔改 marshal → 字符串/整数）
    sc = _sp(sub, "script",
             help="[①-x] ★ 脚本模块方言读取：抽字符串/整数（NeoX 魔改 marshal；还原不了字节码）")
    sc.add_argument("target", help="模块路径，或模块名（如 com.const / ui.trade.PanelTradeBuy）")
    sc.add_argument("--what", choices=("strings", "ints", "all"), default="strings",
                    help="看什么（默认 strings）")
    sc.add_argument("--grep", help="按子串过滤字符串")
    sc.add_argument("--limit", type=int, default=25, help="显示条数")
    sc.add_argument("--json", nargs="?", const="-", help="全量明细落盘（文件较大）")
    sc.set_defaults(func=cmd_script)

    # ★★ 2026-10-01：服型（服务器类型后缀）总表 —— 单一来源 server_types.py
    sv = _sp(sub, "servers",
             help="[横切] ★ 服型后缀总表：中文名 / 依据 / 本客户端是否真有表族")
    sv.add_argument("--scan", action="store_true", help="同时扫还原树统计各服型表数（较慢）")
    sv.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    sv.set_defaults(func=cmd_servers)

    # ★★ 2026-10-01：NPK 头/条目表（本地 或 CDN URL，Range 只取几十 KB）
    npx = _sp(sub, "npk",
              help="[①-x] NPK 头与条目表：解 48 B 头（AES-ECB）+ 读条目，★支持 CDN URL 只取头+表")
    nps = npx.add_subparsers(dest="npk_command")
    nh = _sp(nps, "header",
             help="读 NPK 头 + 前 N 条条目（本地路径 或 http(s) URL，★远端不下整包）")
    nh.add_argument("target", help="本地路径 或 http(s) URL")
    nh.add_argument("--limit", type=int, default=5, help="显示前 N 条条目（0 = 不显示）")
    nh.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    nh.set_defaults(func=cmd_npk_header)

    ct = _sp(sub, "sched",
             help="[横切] ★ 智能调度：看硬件 / 并行预算 / 哪些任务真能上 GPU")
    ct.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    ct.set_defaults(func=cmd_sched)

    # ── 内容指纹索引（跨线基建：H 的定位 / ②线的素材匹配都用它）──
    ct = _sp(sub, "content",
             help="[横切] 内容指纹索引：容器+行 → 内容 MD5，建一次以后秒查")
    ct_sub = ct.add_subparsers(dest="content_command", required=True)
    _inherit(ct_sub, "H-2", "content")

    _cb = _sp(ct_sub, "build", help="建/补索引（增量 + 尺寸预过滤 + 多线程）")
    _cb.add_argument("--container", action="append", help="只建这些容器（可多次；默认全部）")
    _cb.add_argument("--product-root", type=Path,
                     help="本地产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    _cb.add_argument("--db", type=Path, help="索引库（默认 03_执行\\10_索引\\indexes\\lifeafter_files.sqlite3）")
    _cb.add_argument("--workers", type=int, default=24)
    _cb.add_argument("--sizes", help="只算这些尺寸，逗号分隔（预过滤）")
    _cb.add_argument("--quiet", action="store_true")
    _cb.add_argument("--json", nargs="?", const="-")
    _cb.set_defaults(func=cmd_content)

    _cl = _sp(ct_sub, "lookup", help="按 MD5 查「容器+行号」")
    _cl.add_argument("md5", nargs="+", help="一个或多个 32 位 hex MD5")
    _cl.add_argument("--db", type=Path)
    _cl.add_argument("--quiet", action="store_true")
    _cl.add_argument("--json", nargs="?", const="-")
    _cl.set_defaults(func=cmd_content)

    _cs = _sp(ct_sub, "stats", help="索引统计")
    _cs.add_argument("--db", type=Path)
    _cs.add_argument("--quiet", action="store_true")
    _cs.add_argument("--json", nargs="?", const="-")
    _cs.set_defaults(func=cmd_content)

    # ── 带 H · H-2 散文件层（客户端单独下载的文件）──
    lo = _sp(sub, "loose",
             help="[H-2] 散文件层：客户端单独下载的文件（.idx + *.wpk）解密与内容寻址")
    lo_sub = lo.add_subparsers(dest="loose_command", required=True)
    _inherit(lo_sub, "H-2", "loose")

    _los = _sp(lo_sub, "scan", help="解密一个 res 目录下【全部家族】的 *.idx/*.wpk → 明文文件")
    _los.add_argument("--source-root", "--root", dest="source_root",
                      type=Path, default=DEFAULT_LOOSE_ROOT,
                      help="【源】目录（默认 E:\\mrzh\\Documents\\res；只允许 E:\\mrzh 下）")
    _los.add_argument("--out", type=Path, required=True, help="产物目录")
    _los.add_argument("--pkg-filter", dest="pkg_filter",
                      help="只解指定 pkg（如 255 = 内容寻址散文件那一批；逗号分隔）")
    _los.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _los.set_defaults(func=cmd_loose)

    _lom = _sp(lo_sub, "match",
               help="用解密产物的内容 MD5 撞本地索引 ⇒ 定位到容器+行号（不靠名字）")
    _lom.add_argument("--dir", type=Path, required=True, help="loose scan 的产物目录")
    _lom.add_argument("--product-root", type=Path,
                      help="本地产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    _lom.add_argument("--db", type=Path, help="索引库（默认 03_执行\\10_索引\\indexes\\lifeafter_files.sqlite3）")
    _lom.add_argument("--workers", type=int, help="显式并行数（不给则按 --cpu-limit 算）")
    _lom.add_argument("--cpu-limit", type=float, default=80.0,
                      help="最多用整机 CPU 的百分之几（默认 80；跑动中按实测负载反馈让路）")
    _lom.add_argument("--gpu-limit", type=float, default=80.0,
                      help="GPU 上限（默认 80；★ 解码线全程不碰 GPU，对本命令不适用）")
    _lom.add_argument("--limit", type=int, default=20, help="明细最多列几条（默认 20）")
    _lom.add_argument("--out", type=Path, help="完整报告落盘路径")
    _lom.add_argument("--quiet", action="store_true")
    _lom.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _lom.set_defaults(func=cmd_loose)

    sn = _sp(sub, "snapshot",
             help="[H-2] 本地容器快照与终态判定（写入窗口守卫；只读 E:\\mrzh）")
    sn_sub = sn.add_subparsers(dest="snapshot_command", required=True)
    _inherit(sn_sub, "H-2", "snapshot")
    _sns = _sp(sn_sub, "scan",
               help="扫一次并落盘（source_lock.json + CURRENT_STATE.json；有基线再出 patch_delta.json）")
    _sns.add_argument("--source-root", "--root", dest="source_root",
                      help="【源】根（默认 E:\\mrzh；只允许 E:\\mrzh 下的路径，正式服一律拒绝）。"
                           "★ 这是源根，不是项目根 —— 项目根是全局 --root，要写在子命令之前")
    _sns.add_argument("--only", help="只扫该子目录（小规模实测用；相对路径以它为准，不自动取基线）")
    _sns.add_argument("--suffix", action="append",
                      help="只算这些后缀（可多次，如 --suffix .npk；默认 "
                           ".gpk/.npk/.fpk/.wpk/.idx/.pi/.bin/.nxs）")
    _sns.add_argument("--all-files", action="store_true",
                      help="不按后缀过滤、扫全部文件（很慢，慎用）")
    _sns.add_argument("--baseline",
                      help="基线 source_lock.json 路径；auto=最近一次（默认 auto；--only 时不自动取）")
    _sns.add_argument("--no-baseline", action="store_true", help="不比差分，只落快照")
    _sns.add_argument("--out", type=Path,
                      help="快照根目录（默认 03_执行\\10_索引\\patch_snapshots\\<时间戳>）")
    _sns.add_argument("--quiet", action="store_true")
    _sns.add_argument("--json", nargs="?", const="-",
                      help="报告 JSON：裸用打 stdout（自动静音进度，保证 stdout 只有 JSON），给路径则落盘")
    _sns.set_defaults(func=cmd_snapshot)

    _snd = _sp(sn_sub, "diff", help="两次快照按内容比（新增/消失/变更/mtime-only 分开）")
    _snd.add_argument("--baseline", help="基线快照（默认 auto=倒数第二次）")
    _snd.add_argument("--current", help="当前快照（默认 auto=最近一次）")
    _snd.add_argument("--limit", type=int, default=20, help="明细最多列几条（默认 20）")
    _snd.add_argument("--out", type=Path, help="完整报告落盘路径")
    _snd.add_argument("--quiet", action="store_true")
    _snd.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _snd.set_defaults(func=cmd_snapshot)

    # ── 从 run_all.py 收编的兼容命令（命令定义单点化） ──
    sp = _sp(sub, "overview", help="[①-0] 全格式概览：NPK 条目数 + FPK 包分类")
    sp.set_defaults(func=cmd_overview)
    sp = _sp(sub, "restore", help="[①-1] 文件名还原（配置表 → path_id → ui.npk）")
    sp.set_defaults(func=cmd_restore)
    sp = _sp(sub, "thfb", help="[①-1] THFB 哈希提取")
    sp.set_defaults(func=cmd_thfb)
    sp = _sp(sub, "bindict-check", help="[①-1] BinDict 自检（AUG attrs + KJ1 转印）")
    sp.set_defaults(func=cmd_bindict_check)
    sp = _sp(sub, "bridge-audit", help="[①-1] 皮肤逻辑路径→IDX/WPK 物理桥审计（只读）")
    sp.set_defaults(func=cmd_bridge_audit)

    # ── 批量能力（2026-09-26 跑 1% 半全量后加的；原先每件事都得手写脚本） ──
    q = _sp(sub, "query", help="[①-2] 按条件筛条目，只看规模和形状，不落盘")
    _add_filter_args(q)
    q.add_argument("--by", choices=["container", "flag", "kind"], help="分组统计")
    q.add_argument("--show", type=int, default=0, help="额外打印前 N 条明细")
    q.add_argument("--db", type=Path, default=DEFAULT_DB)
    q.add_argument("--res-root", type=Path)
    q.add_argument("--json")
    q.set_defaults(func=cmd_query)

    b = _sp(sub, "bulk", help="[①-2] 批量提取：断点续跑 + 清单 + 类型识别 + 错误聚合")
    _add_filter_args(b)
    b.add_argument("--out", required=True, help="产出根目录")
    b.add_argument("--name-by", default="row", choices=["row", "fid", "row_fid"],
                   help="命名策略。★ 游戏内逻辑路径当前拿不到，只能按 条目号/fid")
    b.add_argument("--resume", action="store_true",
                   help="断点续跑（状态文件 <out>/.bulk_state.json）")
    b.add_argument("--manifest", help="清单文件（JSONL：条 → 文件 + 类型 + sha256）")
    b.add_argument("--progress", nargs="?", const="text", default="text",
                   choices=["text", "json"],
                   help="进度输出格式（默认 text；json = 每行一个 JSON，供机器读）。"
                        "可裸用 --progress")
    b.add_argument("--quiet", action="store_true")
    b.add_argument("--workers", type=int, help="显式并行数（不给则按 --cpu-limit 算）")
    b.add_argument("--cpu-limit", type=float, default=80.0,
                   help="最多用整机 CPU 的百分之几（默认 80）；本命令为 I/O 受限，主要作用是限流不抢占")
    b.add_argument("--gpu-limit", type=float, default=80.0,
                   help="GPU 上限（默认 80）。★ 解码线不碰 GPU ⇒ 本命令下不适用")
    b.add_argument("--raw", action="store_true", help="落压缩载荷，不解码")
    b.add_argument("--db", type=Path, default=DEFAULT_DB)
    b.add_argument("--res-root", type=Path)
    b.add_argument("--json")
    b.set_defaults(func=cmd_bulk)

    idf = _sp(sub, "identify", help="[①-2] 产物类型识别（魔数 → 纹理/配置/网格/音频）")
    idf.add_argument("target", nargs="*", help="文件 / 目录 / glob")
    idf.add_argument("--from-manifest", help="改从 bulk 的清单里读文件列表")
    idf.add_argument("--limit", type=int)
    idf.add_argument("--json")
    idf.set_defaults(func=cmd_identify)

    da = _sp(sub, "decode-audit",
                        help="[①-2] 解码线体检：按【容器×flag】分层抽样，判据不带盲区")
    da.add_argument("--per-group", type=int, default=12,
                    help="每个(容器,flag)组合抽多少条（--full 时忽略）")
    da.add_argument("--full", action="store_true",
                    help="不抽样，逐条全过（2,300,843 条，约十几分钟）——"
                         "「确保不出纰漏」的唯一硬保证；抽样只能证伪、不能证明")
    da.add_argument("--res-root", type=Path)
    da.add_argument("--db", type=Path, default=DEFAULT_DB)
    da.add_argument("--cpu-limit", type=float, default=80.0,
                    help="最多用整机 CPU 的百分之几（默认 80）⇒ 并行 worker = 核数×这个比例")
    da.add_argument("--gpu-limit", type=float, default=80.0,
                    help="GPU 上限（默认 80）。★ 解码线不碰 GPU ⇒ 本命令下不适用，如实提示")
    da.add_argument("--progress", action="store_true")
    da.add_argument("--json")
    da.set_defaults(func=cmd_decode_audit)

    # ── ①-4 名字还原 ──
    nm = _sp(sub, "names", help="[①-1] 名字还原：路径 → 容器 + 行号（双 seed murmur3 → 索引 fid_hex）")
    nm_sub = nm.add_subparsers(dest="names_command", required=True)
    _inherit(nm_sub, "①-1", "names")

    nb = _sp(nm_sub, "build", help="从文本产物挖路径，建/扩字典（默认不覆盖已有输出）")
    nb.add_argument("--source", action="append", type=Path,
                    help="开采源：文本产物文件或目录（可多次；不给则用仓库里现存的路径产物）")
    nb.add_argument("--out", type=Path, default=DEFAULT_NAMES_DICT,
                    help="字典输出（默认 03_执行/10_索引/names/names_dict.json）")
    nb.add_argument("--limit", type=int, help="最多入库多少条路径")
    nb.add_argument("--workers", type=int, default=4, help="并行读文件数（默认 4）")
    nb.add_argument("--force", action="store_true", help="允许覆盖既有字典")
    nb.add_argument("--db", type=Path, default=DEFAULT_DB)
    nb.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    nb.set_defaults(func=cmd_names_build)

    nl = _sp(nm_sub, "lookup", help="★ 一个游戏内路径 → 它在哪个包、哪一行")
    nl.add_argument("path", help="包内相对路径（UI 类带 ui/ 前缀，如 ui/all/img.png）；也可给 16 位 fid")
    nl.add_argument("--db", type=Path, default=DEFAULT_DB)
    nl.add_argument("--res-root", type=Path)
    nl.add_argument("--limit", type=int, default=20, help="最多列几处命中（默认 20）")
    nl.add_argument("--json", nargs="?", const="-", help="JSON：裸用打 stdout，给路径则落盘")
    nl.set_defaults(func=cmd_names_lookup)

    ns = _sp(nm_sub, "stats", help="字典规模 / 已命中多少条 / 各容器覆盖率排行")
    ns.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    ns.add_argument("--db", type=Path, default=DEFAULT_DB)
    ns.add_argument("--json", nargs="?", const="-", help="JSON：裸用打 stdout，给路径则落盘")
    ns.set_defaults(func=cmd_names_stats)

    # ★ 2026-10-01：名字候选名册（atlas 认领等【无哈希可校验】的推断，只登记不入权威表）
    nc = _sp(nm_sub, "candidates",
             help="★ 候选名册：查 atlas 认领等未验证候选（候选 ≠ 名字，不进 row_path_map/字典）")
    nc.add_argument("--tier", help="只看某档（硬/较硬/存疑）")
    nc.add_argument("--verdict", help="只看复核判词（可升级/应废弃/仍存疑）")
    nc.add_argument("--conflicts", action="store_true",
                    help="看【与现有名字冲突】的那批（同一行两个推断）")
    nc.add_argument("--grep", help="按名字子串过滤")
    nc.add_argument("--limit", type=int, default=20)
    nc.add_argument("--json", nargs="?", const="-", help="JSON：裸用打 stdout，给路径则落盘")
    nc.set_defaults(func=cmd_names_candidates)

    # ★ 回填链（2026-09-29）：item_id → 名字 —— 奖池/表输出里的 id 回填成人能看的名
    ni = _sp(nm_sub, "items",
             help="★ item_id → 名字 回填链：建/查从表结构产物来的 id→名 索引")
    ni_sub = ni.add_subparsers(dest="items_command", required=False)
    _ib = _sp(ni_sub, "build", help="扫结构产物（表结构解析_*/结构*）建索引")
    _ib.add_argument("--out", type=Path, help="索引输出（默认 10_索引/items/item_names.json）")
    _ib.add_argument("--json", nargs="?", const="-")
    _ib.set_defaults(func=cmd_names_items)
    _il = _sp(ni_sub, "lookup", help="查 id → 名字（★ 给 --ns 才准确；不给只做跨表排查）")
    _il.add_argument("ids", nargs="*", help="item_id（如 133218 570124）")
    _il.add_argument("--ns", help="★ 命名空间（如 gift_data / common_item / box_data）—— "
                                 "不同表的 row_key 会撞车，不给 ns 只能跨表排查")
    _il.add_argument("--index", type=Path, help="索引文件（默认 10_索引/items/item_names_ns.json）")
    _il.add_argument("--json", nargs="?", const="-")
    _il.set_defaults(func=cmd_names_items)
    _is = _sp(ni_sub, "stats", help="索引规模 / 覆盖表排行 / 缺口说明")
    _is.add_argument("--index", type=Path)
    _is.add_argument("--json", nargs="?", const="-")
    _is.set_defaults(func=cmd_names_items)
    # ★ common_item 专用链（它不在 41_还原树、也不在包内 —— 见模块 docstring）
    _ic = _sp(ni_sub, "ci-build",
              help="★ 建 common_item 索引（工作副本 base∪inc−del × chs，约 20s）")
    _ic.add_argument("--out", type=Path)
    _ic.add_argument("--json", nargs="?", const="-")
    _ic.set_defaults(func=cmd_names_item_ci)
    # ★ 展示大奖名字表直解（补 CSV 只覆盖 180 张的缺口）
    _shb = _sp(ni_sub, "show-build",
               help="★ 直解树里的名字表（player_module_appear_data/fashion/gift/vehicle/box）")
    _shb.add_argument("--out", type=Path)
    _shb.add_argument("--json", nargs="?", const="-")
    _shb.set_defaults(func=cmd_names_item_show)
    _shl = _sp(ni_sub, "show-lookup", help="查 id（展示大奖）→ 名字 + 来源表")
    _shl.add_argument("ids", nargs="*")
    _shl.add_argument("--json", nargs="?", const="-")
    _shl.set_defaults(func=cmd_names_item_show)

    # ── 横切：工具 × 段位 映射表（三线三带的导航表）──
    mp = _sp(sub, "map",
             help="[横切] 工具 × 段位 映射表（--seg ②-2 过滤 · --files 看文件 · --json 机器读）")
    mp.add_argument("--seg", action="append",
                    help="只看某些段位（可多次）：②-2 精确 · ② 该线全部 · H 或 带H · "
                         "带D · 带Q · 横切 · 归档")
    mp.add_argument("--files", action="store_true", help="连文件清单一起打（默认只打段位汇总）")
    mp.add_argument("--limit", type=int, default=20,
                    help="--seg 时每段最多列几个文件（0=全部；默认 20）")
    mp.add_argument("--write", action="store_true",
                    help="落盘 工具库/docs/工具段位映射.md 与 工具段位映射.json")
    mp.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    mp.set_defaults(func=cmd_map)

    # ── 横切：着色器层（`.ccaa5566` = NeoX .pipe 编译着色器变体）──
    sh = _sp(sub, "shader",
             help="[横切] 着色器层：list 家底 · info 看 blob · export 拆成 .dxbc(可选 .asm)")
    sh_sub = sh.add_subparsers(dest="shader_command", required=True)
    _inherit(sh_sub, "横切", "shader")

    sl = _sp(sh_sub, "list", help=".ccaa5566 家底：全库计数 + 按容器顶层分布")
    sl.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    sl.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    sl.set_defaults(func=cmd_shader)

    si = _sp(sh_sub, "info", help="看一个 .pipe 的头字段与 blob 列表（阶段/DXBC/chunk）")
    si.add_argument("path", type=Path, help="一个 .ccaa5566 文件")
    si.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    si.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    si.set_defaults(func=cmd_shader)

    se = _sp(sh_sub, "export", help="★ 拆成真正的 .dxbc（可选 fxc 反汇编出 .asm）")
    se.add_argument("path", type=Path, help="一个 .ccaa5566 文件或一个目录")
    se.add_argument("--out", type=Path, required=True, help="落盘目录")
    se.add_argument("--limit", type=int, default=500, help="目录模式下最多处理几个（默认 500）")
    se.add_argument("--asm", action="store_true", help="额外出 .asm（需 --fxc 指向 fxc.exe）")
    se.add_argument("--fxc", help="fxc.exe 路径（微软 D3D 编译器）")
    se.set_defaults(func=cmd_shader)

    # ── 横切：配置表层（com\cdata\）──
    tb = _sp(sub, "tables",
             help="[横切] 配置表层：list 分类家底 · find 找表 · chs 抽中文名(UTF-8) · refimg 表引用的图")
    tb_sub = tb.add_subparsers(dest="tables_command")
    _inherit(tb_sub, "横切", "tables")

    tl = _sp(tb_sub, "list", help="表家底：按奖池/活动/时装/商店/文字 分类计数")
    tl.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    tl.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    tl.set_defaults(func=cmd_tables)

    tf = _sp(tb_sub, "find", help="按关键词找表（如 lottery / shizhuang / huodong）")
    tf.add_argument("keyword", help="关键词")
    tf.add_argument("--limit", type=int, default=60)
    tf.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    tf.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    tf.set_defaults(func=cmd_tables)

    # ★ 2026-09-28 实测更正：help 原写作「_chs.py，UTF-16LE」—— 那是错的。
    #   实测 116 张表：非 ASCII 串 85,039 条，逐串严格 utf-8 解码 100% 成功；
    #   相反证据：45.72% 的非 ASCII 串是奇数长度（UTF-16 数学上不可能）、
    #   池体 0x00 字节数为 0、交错 NUL 签名命中 0 次。
    #   详见 03_执行/30_分析/全量拆包复核_20260928/06_text_tables/文字表汇总_20260928.md
    tc = _sp(tb_sub, "chs", help="★ 抽中文名表内容（_chs.py，UTF-8；--out 落盘）")
    tc.add_argument("--keyword", help="只处理路径含此关键词的表（默认 _chs.）")
    tc.add_argument("--out", type=Path, help="落盘目录（配置表中文_全量.txt / _分类.md / .json）")
    tc.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    tc.add_argument("--db", type=Path, default=DEFAULT_DB)
    tc.add_argument("--workers", type=int, default=24)
    tc.add_argument("--max-size", dest="max_size", type=int, default=3_000_000,
                    help="跳过超过此字节的表（默认 3e6）")
    tc.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    tc.set_defaults(func=cmd_tables)

    tr = _sp(tb_sub, "refimg", help="抽表里【明文】的图片路径（这是顺着表找图的入口）")
    tr.add_argument("--keyword", help="只处理路径含此关键词的表")
    tr.add_argument("--out", type=Path, help="落盘目录")
    tr.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    tr.add_argument("--db", type=Path, default=DEFAULT_DB)
    tr.add_argument("--workers", type=int, default=24)
    tr.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    tr.set_defaults(func=cmd_tables)

    # ★★ 表副本审计（2026-09-30 用户要求「杜绝以后再犯」）
    tcp = _sp(tb_sub, "copies",
              help="★★ 表副本：一张表有几份副本、该用哪份（overlay/Documents 优先）；"
                   "--audit 全库自检「树里存的是底座」的隐患表")
    tcp.add_argument("table", nargs="?", help="表名或树内路径（如 weapon_skin_data.py）或 16 位 fid")
    tcp.add_argument("--audit", action="store_true", help="全库自检（较慢，约 1~2 分钟）")
    tcp.add_argument("--limit", type=int, default=30, help="--audit 时最多列几条隐患（默认 30）")
    tcp.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    tcp.set_defaults(func=cmd_tables_copies)

    # ── 横切：spine 图集层（②-2 贴图复原的入口）──
    at = _sp(sub, "atlas",
             help="[②-2] spine 图集层：list 家底 · discover 按尺寸认本体(复原真名) · export 导出")
    at_sub = at.add_subparsers(dest="atlas_command", required=True)
    _inherit(at_sub, "②-2", "atlas")

    al = _sp(at_sub, "list", help="图集家底：atlas 个数按目录")
    al.add_argument("--restore-root", dest="restore_root", type=Path, default=DEFAULT_RESTORE)
    al.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    al.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    al.set_defaults(func=cmd_atlas)

    ad = _sp(at_sub, "discover",
             help="★ atlas → 图集本体：按尺寸在附近行认领，复原本体真名（--out 落盘命名表）")
    ad.add_argument("--window", type=int, default=5, help="在 atlas 行前后各看几行（默认 5）")
    ad.add_argument("--out", type=Path, help="落盘目录（图集页_命名表.csv / 图集页_全量.json）")
    ad.add_argument("--restore-root", dest="restore_root", type=Path, default=DEFAULT_RESTORE)
    ad.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    ad.add_argument("--db", type=Path, default=DEFAULT_DB)
    ad.add_argument("--workers", type=int, default=24)
    ad.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    ad.set_defaults(func=cmd_atlas)

    ae = _sp(at_sub, "export",
             help="★ 按 sprite 切图集（Spine xy/size/rotate），--filter 限定目录 · --group 按目录分")
    ae.add_argument("--names", type=Path,
                    help="命名表 CSV（默认找 30_分析/spine图集本体_20260928/图集页_命名表.csv）")
    ae.add_argument("--out", type=Path, help="输出目录（默认 90_临时/sprite）")
    ae.add_argument("--filter", help="只处理路径含此关键词的 atlas（如 diancangshizhuang）")
    ae.add_argument("--group", action="store_true", help="按 atlas 所在目录分子目录")
    ae.add_argument("--max-sprites", dest="max_sprites", type=int, default=0,
                    help="最多切多少张（0=不限）")
    ae.add_argument("--work", type=Path, help="临时目录")
    ae.add_argument("--restore-root", dest="restore_root", type=Path, default=DEFAULT_RESTORE)
    ae.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    ae.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    ae.set_defaults(func=cmd_atlas_export)

    # ── 横切：物理探针（locate / fiddiff / ovl）—— 2026-09-28 拆包复核逼出来的 ──
    lc = _sp(sub, "locate",
             help="[①-1] 容器+行号 → 产物文件（或 --fid 反查它落在哪个容器哪一行）")
    lc.add_argument("container", nargs="?", help="容器名，如 res\\\\scene_03.gpk")
    lc.add_argument("row", nargs="*", type=int, help="行号（可给多个）")
    lc.add_argument("--fid", action="append", help="16 位 hex fid（可多次）→ 反查容器/行")
    lc.add_argument("--product-root", dest="product_root", type=Path,
                    help="产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    lc.add_argument("--db", type=Path, default=DEFAULT_DB)
    lc.add_argument("--head", type=int, default=0, help="额外打印前 N 字节的 hex")
    lc.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    lc.set_defaults(func=cmd_locate)

    fd = _sp(sub, "fiddiff",
             help="[①-1] 两个 pkg_N.pi 目录的 fid 增删（--named 只看有名 / --grep 按名字筛）")
    fd.add_argument("a", type=Path, help="A 版本目录（含 pkg_1..17.pi）")
    fd.add_argument("b", type=Path, help="B 版本目录")
    fd.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT,
                    help="名字字典（用来把 fid 解成路径）")
    fd.add_argument("--named", action="store_true", help="只列字典里有名字的")
    fd.add_argument("--grep", help="只列路径含此关键词的（不区分大小写）")
    fd.add_argument("--limit", type=int, default=25, help="每条最多打印多少（默认 25）")
    fd.add_argument("--out", type=Path, help="完整增删清单落盘（JSON）")
    fd.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    fd.set_defaults(func=cmd_fiddiff)

    ov = _sp(sub, "ovl",
             help="[H-1] overlay 包（=普通 NPK 容器）：entries 看条目表 · unpack 全量解包分类落盘")
    ov_sub = ov.add_subparsers(dest="ovl_command", required=True)
    _inherit(ov_sub, "H-1", "ovl")

    ove = _sp(ov_sub, "entries", help="读一个 overlay .npk 的条目表（fid/偏移/packed/decoded/flag）")
    ove.add_argument("path", type=Path, help="overlay 包文件，或含 *.npk 的目录")
    ove.add_argument("--limit", type=int, default=20)
    ove.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    ove.set_defaults(func=cmd_ovl)

    ovu = _sp(ov_sub, "unpack",
              help="★ 条目级全量解包 + 按类型落盘（<包名>_ov/<fid>.<类型>）")
    ovu.add_argument("path", type=Path, help="overlay 包文件，或含 *.npk 的目录")
    ovu.add_argument("--out", type=Path, required=True, help="输出目录")
    ovu.add_argument("--dry-run", dest="dry_run", action="store_true", help="只统计不落盘")
    ovu.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    ovu.set_defaults(func=cmd_ovl)

    # ★ restore_tree.py 的 docstring 早就承诺了 `toolkit_cli.py materialize`，但一直没注册。
    mt = _sp(sub, "materialize",
             help="[①-1] 产物 → 还原树（按源路径物化，硬链接；★ 用最新字典，不是模块的 v6 默认）")
    mt.add_argument("--out", type=Path, default=DEFAULT_RESTORE, help="输出根（默认 41_还原树）")
    mt.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT,
                    help="名字字典（默认取版本号最大的 names_dict_vN.json）")
    mt.add_argument("--db", type=Path, default=DEFAULT_DB)
    mt.add_argument("--src-root", dest="src_root", type=Path,
                    help="产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    mt.add_argument("--container", action="append", help="只做这些容器（可多次；默认全部）")
    mt.add_argument("--copy", action="store_true", help="复制而不是硬链接（占空间）")
    mt.add_argument("--no-unnamed", dest="no_unnamed", action="store_true",
                    help="不落 _未命名/ 那一半")
    mt.add_argument("--quiet", action="store_true")
    mt.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    mt.set_defaults(func=cmd_materialize)

    # ── 横切：奖池层（静态池结构 / 池目录 / 本次热更）──
    lt = _sp(sub, "lottery",
             help="[横切] 奖池层：list 家底 · find 找池 · show 单池详情 · delta 本次热更涉及哪些池")
    lt_sub = lt.add_subparsers(dest="lottery_command")
    _inherit(lt_sub, "横切", "lottery")

    _ltl = _sp(lt_sub, "list", help="奖池家底：池数/格数/组件/target 分类/相关表/看板覆盖")
    _ltl.add_argument("--data", type=Path, help="静态池结构 JSONL（默认 LOTTERY_POOL_RESOLVED_v01.jsonl）")
    _ltl.add_argument("--boards", type=Path, help="看板目录（池归属的唯一来源）")
    _ltl.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    _ltl.add_argument("--limit", type=int, default=12)
    _ltl.add_argument("--json", nargs="?", const="-", help="报告 JSON：裸用打 stdout，给路径则落盘")
    _ltl.set_defaults(func=cmd_lottery)

    _ltf = _sp(lt_sub, "find", help="找池：数字=按 pool_key；文本=在看板归属/条目名里找（+列奖池族表）")
    _ltf.add_argument("keyword", help="池号（如 391762 / 3917）或关键词（如 帝皇 / 铠甲 / 樱灵狐梦）")
    _ltf.add_argument("--data", type=Path)
    _ltf.add_argument("--boards", type=Path)
    _ltf.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    _ltf.add_argument("--limit", type=int, default=40)
    _ltf.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    _ltf.set_defaults(func=cmd_lottery)

    _lts = _sp(lt_sub, "show", help="单池详情：逐格 item_id/数量/类型/命名空间 + 子池 + 看板归属")
    _lts.add_argument("key", help="池号（390000–391793）或已被看板认领的名字")
    _lts.add_argument("--data", type=Path)
    _lts.add_argument("--boards", type=Path)
    _lts.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    _lts.add_argument("--limit", type=int, default=60)
    _lts.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    _lts.set_defaults(func=cmd_lottery)

    _ltt = _sp(lt_sub, "delta",
               help="★ 本次热更涉及哪些池：①overlay 逐条比字节 ②新增/移除 fid ③变更文字表清单")
    _ltt.add_argument("--delivery", type=Path, help="热更交付目录（默认取最新的 热更交付_5目录_*）")
    _ltt.add_argument("--analysis", type=Path, help="30_分析 目录（用于找交付目录）")
    _ltt.add_argument("--product-root", dest="product_root", type=Path,
                      help="基线产物根（默认自动：载荷在就用载荷，已清则用 41_还原树）")
    _ltt.add_argument("--unpack-out", dest="unpack_out", type=Path,
                      help="overlay 解包落盘目录（不给则解到临时目录、不落盘）")
    _ltt.add_argument("--db", type=Path, default=DEFAULT_DB)
    _ltt.add_argument("--limit", type=int, default=10, help="明细最多列几条（默认 10）")
    _ltt.add_argument("--dict", dest="dict_path", type=Path, default=DEFAULT_NAMES_DICT)
    _ltt.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    _ltt.set_defaults(func=cmd_lottery)

    _ltp = _sp(lt_sub, "prob",
               help="★ 奖池概率公示：从 desc_info_data_chs.py 抽【XX奖池】块（配置表原文）")
    _ltp.add_argument("keyword", nargs="?", help="只列名字含此关键词的池（如 红尘 / 墨隐 / 狐梦）")
    _ltp.add_argument("--desc-info", dest="desc_info", type=Path,
                      help="desc_info_data_chs.py（★ 默认先找 41_还原树/com/cdata/，"
                           "回退 30_分析/*/07_restore_tree/tree_v*）")
    _ltp.add_argument("--json", nargs="?",
                      const="-", help="报告 JSON（裸用打 stdout，给路径则落盘）")
    _ltp.set_defaults(func=cmd_lottery)

    # ★★ locate —— 按【内容】认池（覆盖所有抽奖体系），取代「按看板归属认池」
    _ltz = _sp(lt_sub, "locate",
               help="★★ 按内容定位奖池：关键词 → item_id → 池/体系（不看板；覆盖 "
                    "reward_pool_data + 超级时装抽奖等所有抽奖表）")
    _ltz.add_argument("keyword", help="外观/道具/礼盒名（如 幻夜神谕 / 红焰剑仙）")
    _ltz.add_argument("--struct-dir", dest="struct_dir", type=Path,
                      help="表结构解析产物目录（默认自动找 30_分析/表结构解析_*/结构）")
    _ltz.add_argument("--cdata", type=Path, help="com\\cdata 还原树目录（默认 41_还原树/com/cdata）")
    _ltz.add_argument("--limit", type=int, default=40, help="每条最多列几个（默认 40）")
    _ltz.add_argument("--out", type=Path, help="产物目录（出 md + json）")
    _ltz.add_argument("--json", nargs="?", const="-", help="报告 JSON（裸用打 stdout，给路径则落盘）")
    _ltz.set_defaults(func=cmd_lottery_locate)

    # ★★ chain —— 全量奖池链（活动 → lottery_id → 展示大奖 → 名字，全通道一遍跑完）
    _ltc = _sp(lt_sub, "chain",
               help="★★ 全量奖池链：所有活动 → lottery_id → 展示大奖 + 名字（源：41_还原树）")
    _ltc.add_argument("--out", type=Path, help="产物 JSON（默认 30_分析/全量奖池链_<日期>.json）")
    _ltc.add_argument("--limit", type=int, help="跑完顺手预览前 N 行")
    _ltc.add_argument("--json", nargs="?", const="-", help="报告 JSON（裸用打 stdout，给路径则落盘）")
    _ltc.set_defaults(func=cmd_lottery_chain)

    # ★★ hd-show —— 活动展示道具（★ 静态表，别再按池号找：池号那条链在客户端是空的）
    _lth = _sp(lt_sub, "hd-show",
               help="★★ 活动展示道具：活动号 → 道具 id 列表 + 名字"
                    "（源：common_hd_show_reward_data，按【活动号】取，不是池号）")
    _lth.add_argument("key", nargs="?", default=None,
                      help="活动号（如 3610 = 幻夜神谕；取自 huodong_conf_data 的行 key）；"
                           "★ 不给则列出表里全部活动号")
    _lth.add_argument("--json", nargs="?", const="-", help="报告 JSON")
    _lth.set_defaults(func=cmd_lottery_hd)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # ★ --root 是全局选项：显式给了就改根（无效时 paths 会直接报错，不回退，见 paths.find_project_root）
    root = getattr(args, "root", None)
    if root:
        from toolkit_core.paths import set_root
        set_root(root)
    # ★★ 智能调度：把全局开关一次性设好，各命令用 throttle.global_jobs(kind) 取并行数。
    #    这样「写死 24 workers」全部退役 —— 换台机器自动适配。
    try:
        from toolkit_core import throttle as _TH
        _TH.set_global(jobs=getattr(args, "jobs", None),
                       cpu_limit=getattr(args, "cpu_limit", None),
                       gpu_limit=getattr(args, "gpu_limit", None),
                       gpu_mode=getattr(args, "gpu", "auto"),
                       throttle=not getattr(args, "no_throttle", False))
    except Exception as _e:                     # 调度是增强项，坏了不能拖垮主流程
        import sys as _s
        print("[sched] ⚠ 智能调度初始化失败（按默认继续）：%s" % _e, file=_s.stderr)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
