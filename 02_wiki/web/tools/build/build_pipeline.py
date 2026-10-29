#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_pipeline.py — 板级重建编排器（执行图唯一来源 = rules/pipeline_graph.yml）

把「谁先谁后」从聊天记录与脚本命名里拿出来，落成可执行、可复算的流水线：

    快照 → 主产出 → 后处理 → 溯源契约修复 pass → 发布门禁 → 条目级 diff → 更新日志草稿

铁律：
  * **执行图只认 rules/pipeline_graph.yml**（手工维护层）。
    rules/boards/*.yml 里的 primary_builders / postprocess_scripts 只是「脚本角色分类
    （build/patch）」的副产品 —— 角色 ≠ 顺序，拿它当执行图会错（实测 vehicle_full 的 7 个
    脚本里，角色分类给出的顺序与真实顺序仅 1 处吻合）。
  * 每条 step 必须声明 order_basis（为何排在此位）+ source（依据出处）；
    缺任一 → 视为**顺序未声明**，编排器拒绝执行。
  * 顺序依据等级：
      documented 有书面依据（脚本 docstring / 用户决策 / 实测）→ 可自动执行
      inferred   由角色分类推定 → 默认**不执行**，需 --allow-inferred 显式放行
      unknown    无依据 → 一律不执行，只在 --check 里列为待补
  * 默认 dry-run；--apply 才真正落盘。--resume 从上次中断处续跑。
  * 依赖产物层（01_索引与产物）的板：产物层不在库，克隆者须自备；
    缺输入时明确报错并跳过该板，**不猜、不伪造**。

用法:
  python 02_wiki/web/tools/build/build_pipeline.py --check
  python 02_wiki/web/tools/build/build_pipeline.py --board vehicle_full            # dry-run
  python 02_wiki/web/tools/build/build_pipeline.py --board vehicle_full --apply
  python 02_wiki/web/tools/build/build_pipeline.py --all --apply
  python 02_wiki/web/tools/build/build_pipeline.py --all --apply --resume
  python 02_wiki/web/tools/build/build_pipeline.py --all --apply --allow-inferred

退出码: 0 成功 / 1 执行失败 / 2 参数或规则层错误
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from la_paths import PROJ, WEB, BOARDS_DIR, RULES_DIR, STATE_DIR, ARTIFACTS  # noqa: E402

try:
    import yaml
    YAML_BACKEND = "PyYAML"
except ImportError:
    yaml = None
    YAML_BACKEND = ""

GRAPH_FILE = RULES_DIR / "pipeline_graph.yml"
STATE_FILE = STATE_DIR / "pipeline_state.json"
REPORT_FILE = STATE_DIR / "pipeline_report.json"

# 脚本搜索根（按名解析真实路径；工具库里的脚本不在 web/tools 下）
SCRIPT_ROOTS = [
    WEB / "tools",
    PROJ / "00_规范与工具" / "工具" / "工具库",
]

# 判定「依赖产物层」的标志 —— 产物层不入库，克隆者可能没有
ARTIFACT_MARKERS = ("30_分析", "41_还原树", "10_索引", "20_提取")

try:
    import yaml
    YAML_BACKEND = "PyYAML"
except ImportError:
    yaml = None
    YAML_BACKEND = ""

# 无 PyYAML 时的兜底解析器（克隆者可能直接用系统 python）
if yaml is None:
    try:
        from mini_yaml import loads as _mini_loads
        from mini_yaml import MiniYamlError
    except ImportError:
        _mini_loads = None
        MiniYamlError = ValueError
else:
    _mini_loads = None

# ── 基础工具 ──────────────────────────────────────────────────────────
def now_stamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_yaml_text(text: str, what: str) -> dict:
    """解析 YAML 文本。缺 PyYAML 时用内置 mini_yaml 兜底。

    ★ 为什么要兜底：克隆者可能直接用系统 python（没装 PyYAML）。
      执行图是编排器的唯一执行来源 —— 读不到就等于编排器不可用。
      参照 checks/portability_audit.py 的既有做法：缺依赖时明确告警 + 内置兜底，
      而不是静默降级成「看起来正常、结果全错」。
    """
    if yaml is not None:
        try:
            return yaml.safe_load(text) or {}
        except Exception as e:
            raise SystemExit(f"❌ {what} 解析失败（PyYAML）：{e}")
    if _mini_loads is None:
        raise SystemExit("❌ 缺 PyYAML，且内置兜底解析器不可用。\n"
                         f"   用项目 venv：{PROJ / '00_规范与工具' / '环境' / 'venv' / 'Scripts' / 'python.exe'}\n"
                         f"   或 pip install pyyaml")
    try:
        return _mini_loads(text) or {}
    except Exception as e:
        raise SystemExit(f"❌ {what} 解析失败（内置兜底解析器 mini_yaml）：{e}\n"
                         f"   建议装 PyYAML：pip install pyyaml")


def load_graph() -> dict:
    if not GRAPH_FILE.exists():
        raise SystemExit(f"❌ 找不到执行图：{GRAPH_FILE}\n"
                         f"   这是编排器的唯一执行来源，缺失时不臆造顺序。")
    try:
        g = parse_yaml_text(GRAPH_FILE.read_text(encoding="utf-8"), "执行图")
    except SystemExit:
        raise
    if not isinstance(g, dict):
        raise SystemExit("❌ 执行图格式错误：顶层应为映射")
    return g


def resolve_script(name: str) -> tuple[pathlib.Path | None, list[pathlib.Path]]:
    """按文件名解析脚本真实路径。返回 (命中路径 or None, 全部候选)。

    规则层记的是文件名，脚本却分散在 web/tools 与工具库两处 ⇒ 必须按名解析。
    多处同名 → 返回全部候选，由调用方按「唯一命中」原则判定（不猜）。
    """
    cands: list[pathlib.Path] = []
    for root in SCRIPT_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob(name):
            if p.is_file() and "__pycache__" not in p.parts:
                cands.append(p)
    cands.sort()
    if not cands:
        return None, []
    return cands[0], cands


def script_needs_artifacts(path: pathlib.Path) -> bool:
    """脚本是否依赖产物层（01_索引与产物，不入库）。"""
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:6000]
    except OSError:
        return False
    return any(m in head for m in ARTIFACT_MARKERS)


def artifacts_present() -> bool:
    return ARTIFACTS.exists() and any(ARTIFACTS.iterdir())


def pick_python(pref: str) -> str:
    """选解释器：auto = 优先项目 venv（依赖齐全），否则当前解释器。"""
    if pref and pref != "auto":
        return pref
    venv = PROJ / "00_规范与工具" / "环境" / "venv" / "Scripts" / "python.exe"
    if venv.exists():
        return str(venv)
    return sys.executable


# ── 步骤解析 ──────────────────────────────────────────────────────────
def collect_steps(graph: dict, board: str | None) -> list[dict]:
    """把执行图展开成有序步骤列表。

    每个 step 统一为：
      {board, script, path, stage, order_basis, source, level}
    level = documented | inferred | unknown
    """
    boards = graph.get("boards") or {}
    out: list[dict] = []

    def add(step: dict, board_id: str, level: str, cands: list[pathlib.Path]):
        name = step.get("script") or ""
        path = cands[0] if len(cands) == 1 else None
        out.append({
            "board": board_id,
            "script": name,
            "path": str(path) if path else None,
            "candidates": [str(c) for c in cands],
            "stage": step.get("stage") or "rebuild",
            "args": list(step.get("args") or []),
            "requires": list(step.get("requires") or []),
            "order_basis": (step.get("order_basis") or "").strip(),
            "source": (step.get("source") or "").strip(),
            "level": level,
            "ambiguous": len(cands) > 1,
            "missing": len(cands) == 0,
        })

    # global 脚本：一次 run 内只跑一次，单独成组（不属于任何板的 rebuild/postprocess）
    for step in graph.get("global_scripts") or []:
        _, cands = resolve_script(step.get("script") or "")
        add(step, "(global)", "documented", cands)

    # 逐板步骤
    for bid, spec in boards.items():
        if board and bid != board:
            continue
        if spec.get("partial"):
            # 只声明了部分依赖的板：只跑声明过的步骤，其余不碰
            for step in spec.get("steps") or []:
                _, cands = resolve_script(step.get("script") or "")
                add(step, bid, "documented", cands)
        else:
            for step in spec.get("steps") or []:
                _, cands = resolve_script(step.get("script") or "")
                add(step, bid, "documented", cands)

    # inferred 层：未声明顺序的板，按规则层角色分类推定
    if board is None or board in (graph.get("unresolved_order") or [{}])[0].get("boards", []):
        inv_boards = ((graph.get("unresolved_order") or [{}])[0]).get("boards") or []
        for bid in inv_boards:
            byml = RULES_DIR / "boards" / f"{bid}.yml"
            if not byml.exists():
                continue
            try:
                d = parse_yaml_text(byml.read_text(encoding="utf-8"),
                                    f"规则层 {bid}") or {}
            except SystemExit:
                continue
            if not isinstance(d, dict):
                continue
            prim = d.get("primary_builders") or []
            post = d.get("postprocess_scripts") or []
            for nm in prim + post:
                _, cands = resolve_script(nm)
                add({"script": nm,
                     "stage": "rebuild" if nm in prim else "postprocess",
                     "order_basis": "由 rules/boards 角色分类推定（未人工判定）",
                     "source": "rules/boards/<board>.yml（自动生成，勿手改）"},
                    bid, "inferred", cands)
    return out


def check_requires(step: dict) -> list[str]:
    """校验 step 的前置条件（文件存在 / 文件含特定内容）。

    目的：把「跑到最后一步才 assert 失败」提前到执行前，
    让人一眼看出是**环境前置条件**没满足，而不是脚本坏了。
    """
    bad: list[str] = []
    for req in step.get("requires") or []:
        f = req.get("file")
        if not f:
            continue
        p = PROJ / f
        if not p.exists():
            bad.append(f"缺前置文件 {f}")
            continue
        needle = req.get("contains")
        if needle:
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError as e:
                bad.append(f"读不了前置文件 {f}（{e}）")
                continue
            if needle not in txt:
                bad.append(f"前置文件 {f} 不含 {needle}"
                           + (f"（{req.get('note')}）" if req.get("note") else ""))
    return bad


def validate_steps(steps: list[dict], allow_inferred: bool) -> list[str]:
    """返回阻断项列表（每条说明为什么这条不能跑）。"""
    problems: list[str] = []
    for s in steps:
        tag = f"{s['board']}/{s['script']}"
        if s["missing"]:
            problems.append(f"{tag}：脚本找不到（解析了 {len(SCRIPT_ROOTS)} 个搜索根）")
        elif s["ambiguous"]:
            problems.append(f"{tag}：多处同名 → {s['candidates']}")
        if not s["order_basis"]:
            problems.append(f"{tag}：缺 order_basis（顺序未声明）")
        if not s["source"]:
            problems.append(f"{tag}：缺 source（依据出处未标注）")
        if s["level"] == "unknown":
            problems.append(f"{tag}：顺序依据等级 unknown，不执行")
        if s["level"] == "inferred" and not allow_inferred:
            problems.append(f"{tag}：顺序为推定（inferred），默认不执行；"
                            f"确认无误加 --allow-inferred")
    return problems


# ── 执行 ──────────────────────────────────────────────────────────────
def run_tool(tool: str, args: list[str], cwd: pathlib.Path, timeout: int,
             python: str, dry: bool) -> dict:
    """跑一个工具脚本（tool 为项目相对路径）。"""
    cmd = [python, str(PROJ / tool)] + [str(a) for a in args]
    if dry:
        return {"cmd": " ".join(cmd), "cwd": str(cwd), "rc": 0, "dry": True,
                "stdout": "(dry-run 未执行)", "stderr": ""}
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {"cmd": " ".join(cmd), "cwd": str(cwd), "rc": r.returncode, "dry": False,
                "stdout": r.stdout[-4000:], "stderr": r.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(cmd), "cwd": str(cwd), "rc": -9, "dry": False,
                "stdout": "", "stderr": f"超时（>{timeout}s）"}
    except Exception as e:
        return {"cmd": " ".join(cmd), "cwd": str(cwd), "rc": -1, "dry": False,
                "stdout": "", "stderr": f"{type(e).__name__}: {e}"}


def run_step(step: dict, cwd: pathlib.Path, timeout: int, python: str, dry: bool) -> dict:
    """跑单个板级步骤脚本。"""
    path = pathlib.Path(step["path"]) if step["path"] else None
    if path is None:
        return {"script": step["script"], "board": step["board"], "rc": -2,
                "stdout": "", "stderr": "脚本路径未解析（缺失或同名冲突）", "skipped": True}
    cmd = [python, str(path)] + [str(a) for a in (step.get("args") or [])]
    if dry:
        return {"script": step["script"], "board": step["board"], "rc": 0, "dry": True,
                "cmd": " ".join(cmd), "stdout": "(dry-run 未执行)", "stderr": ""}
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {"script": step["script"], "board": step["board"], "rc": r.returncode,
                "cmd": " ".join(cmd), "stdout": r.stdout[-4000:], "stderr": r.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"script": step["script"], "board": step["board"], "rc": -9,
                "cmd": " ".join(cmd), "stdout": "", "stderr": f"超时（>{timeout}s）"}
    except Exception as e:
        return {"script": step["script"], "board": step["board"], "rc": -1,
                "cmd": " ".join(cmd), "stdout": "", "stderr": f"{type(e).__name__}: {e}"}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(st: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")


# ── 主流程 ────────────────────────────────────────────────────────────
def cmd_check(args, graph: dict) -> int:
    """体检：执行图完整性 + 顺序依据覆盖度。"""
    steps = collect_steps(graph, args.board)
    declared = sorted((graph.get("boards") or {}).keys())
    unresolved = ((graph.get("unresolved_order") or [{}])[0]).get("boards") or []

    print(f"📋 执行图：{GRAPH_FILE.relative_to(PROJ)}")
    print(f"   声明板 {len(declared)}：{declared}")
    print(f"   待补顺序板 {len(unresolved)}")
    print()
    print("── 已声明顺序的板 ──")
    for bid in declared:
        spec = (graph.get("boards") or {})[bid]
        steps_n = spec.get("steps") or []
        print(f"  {bid}（{spec.get('name', '?')}）"
              f"{'  ⚠️ partial（仅声明部分依赖）' if spec.get('partial') else ''}")
        for s in steps_n:
            path, cands = resolve_script(s.get("script") or "")
            mark = "✅" if len(cands) == 1 else ("⚠️" if cands else "❌")
            loc = ""
            if len(cands) == 1:
                loc = "  @ " + str(path.relative_to(PROJ)).replace("\\", "/")
            elif cands:
                loc = "  多处同名: " + ", ".join(str(c.relative_to(PROJ)).replace("\\", "/") for c in cands)
            print(f"      {mark} [{s.get('stage', '?')}] {s.get('script')}{loc}")
            if s.get("args"):
                print(f"         参数: {' '.join(str(a) for a in s['args'])}")
            if s.get("requires"):
                for req in s["requires"]:
                    rp = PROJ / (req.get("file") or "")
                    if not rp.exists():
                        st = "❌ 缺文件"
                    else:
                        try:
                            txt = rp.read_text(encoding="utf-8", errors="ignore")
                            st = "✅" if (not req.get("contains") or req["contains"] in txt) else "⚠️ 内容不符"
                        except OSError:
                            st = "❌ 读不了"
                    print(f"         前置 {st} {req.get('file')}"
                          + (f" 含 {req.get('contains')}" if req.get("contains") else ""))
            print(f"         依据: {(s.get('order_basis') or '（缺）')[:80]}")
    print()
    print("── 跨板脚本（global）──")
    for s in graph.get("global_scripts") or []:
        path, cands = resolve_script(s.get("script") or "")
        mark = "✅" if len(cands) == 1 else ("⚠️" if cands else "❌")
        print(f"  {mark} {s.get('script')}  影响板 {len(s.get('boards') or [])} 块")
        print(f"     依据: {(s.get('order_basis') or '（缺）')[:80]}")
    print()
    print("── 阶段主干 ──")
    for st in graph.get("stages") or []:
        kind = st.get("kind") or ("tool:" + str(st.get("tool")))
        print(f"  {st.get('id'):14s} {st.get('title', ''):16s} {kind}")
    print()

    problems = validate_steps(steps, args.allow_inferred)
    if problems:
        print(f"⚠️ 阻断项 {len(problems)} 条：")
        for p in problems[:40]:
            print(f"   - {p}")
        if len(problems) > 40:
            print(f"   … 另有 {len(problems) - 40} 条")
    else:
        print("✅ 无阻断项")

    # 覆盖度统计
    doc = sum(1 for s in steps if s["level"] == "documented")
    inf = sum(1 for s in steps if s["level"] == "inferred")
    unk = sum(1 for s in steps if s["level"] == "unknown")
    print()
    print(f"── 顺序依据覆盖 ──")
    print(f"   documented（有书面依据，可自动执行）: {doc}")
    print(f"   inferred  （角色分类推定，需显式放行）: {inf}")
    print(f"   unknown   （无依据，不执行）           : {unk}")
    if unresolved:
        print(f"   待人工判定顺序的板: {len(unresolved)} 块")
    return 0


def cmd_run(args, graph: dict) -> int:
    dry = not args.apply
    defaults = graph.get("defaults") or {}
    python = pick_python(defaults.get("python", "auto"))
    cwd = PROJ / (defaults.get("cwd") or "02_wiki/web")
    timeout = int(defaults.get("timeout_s", 3600))

    steps = collect_steps(graph, args.board)
    problems = validate_steps(steps, args.allow_inferred)

    # 阻断项：dry-run 时只报告；apply 时直接拦下（不半途执行）
    if problems and args.apply:
        print("❌ 存在阻断项，拒绝执行（修规则层或加 --allow-inferred）：")
        for p in problems[:40]:
            print(f"   - {p}")
        if len(problems) > 40:
            print(f"   … 另有 {len(problems) - 40} 条")
        return 2

    label = args.label or now_stamp()
    state = load_state()
    resumed = False
    if args.resume:
        prev = state.get("last_run")
        if prev and prev.get("label") == label:
            state = prev
            resumed = True
        elif prev:
            state = prev
            label = prev.get("label", label)
            resumed = True
            print(f"ℹ️ --resume 续跑上次：{label}")

    done = set(state.get("done_steps") or []) if resumed else set()
    if not resumed:
        state = {"label": label, "done_steps": [], "stages": {},
                 "started": datetime.datetime.now().isoformat(timespec="seconds")}

    stages = graph.get("stages") or []
    only = set(args.stage.split(",")) if args.stage else None
    report = {"label": label, "dry": dry, "started": state.get("started"),
              "python": python, "cwd": str(cwd), "steps": [], "stages": {}}

    print(f"{'🔍 DRY-RUN' if dry else '▶️  执行'}  label={label}"
          f"{'（续跑）' if resumed else ''}")
    print(f"   解释器 {python}")
    print(f"   工作目录 {cwd}")
    print(f"   产物层 {'✅ 在位' if artifacts_present() else '⚠️ 缺失（01_索引与产物 不入库，克隆者须自备）'}")
    print()

    if problems:
        print(f"⚠️ 阻断项 {len(problems)} 条（dry-run 下仅提示）：")
        for p in problems[:10]:
            print(f"   - {p}")
        if len(problems) > 10:
            print(f"   … 另有 {len(problems) - 10} 条")
        print()

    # ── 阶段推进 ──────────────────────────────────────────────────────
    for st in stages:
        sid = st.get("id")
        if only and sid not in only:
            continue
        title = st.get("title", sid)
        kind = st.get("kind")

        if kind == "steps":
            # 板级步骤：按 stage 分组执行
            want = "rebuild" if sid == "rebuild" else "postprocess"
            group = [s for s in steps if s["stage"] == want and s["board"] != "(global)"]
            gsteps = [s for s in steps if s["board"] == "(global)"] if sid == "rebuild" else []
            if not group and not gsteps:
                print(f"── {title} ── 无步骤")
                continue
            print(f"── {title}（{len(group) + len(gsteps)} 步）──")
            for s in (gsteps + group) if sid == "rebuild" else group:
                key = f"{s['board']}::{s['script']}"
                if key in done:
                    print(f"   ⏭  {key}（已完成，跳过）")
                    continue
                # 产物层缺失：依赖产物层的脚本跳过并说明，不猜
                if s["path"] and not artifacts_present() and script_needs_artifacts(pathlib.Path(s["path"])):
                    print(f"   ⏭  {key} —— 依赖产物层，当前不可用（跳过）")
                    report["steps"].append({"step": key, "skipped": True,
                                            "reason": "依赖产物层，当前不可用"})
                    continue
                # 前置条件不满足：跳过并说明（环境问题，不是顺序问题，不阻断流水线）
                unmet = check_requires(s)
                if unmet:
                    print(f"   ⏭  {key} —— 前置条件未满足（跳过）：{unmet[0]}")
                    for u in unmet[1:]:
                        print(f"      · {u}")
                    report["steps"].append({"step": key, "skipped": True,
                                            "reason": "前置条件未满足：" + "；".join(unmet)})
                    continue
                r = run_step(s, cwd, timeout, python, dry)
                flag = "✅" if r["rc"] == 0 else "❌"
                print(f"   {flag} {key} (rc={r['rc']})")
                if r.get("dry"):
                    print(f"      → {r.get('cmd', '')}")
                elif r["rc"] != 0:
                    tail = (r.get("stderr") or r.get("stdout") or "").strip().splitlines()
                    for t in tail[-6:]:
                        print(f"      | {t}")
                report["steps"].append({"step": key, **{k: v for k, v in r.items() if k != "dry"}})
                if r["rc"] != 0 and not dry:
                    print(f"   ⛔ {key} 失败，后续板级步骤中止")
                    done.add(key)
                    save_state(state)
                    report["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
                    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
                    return 1
                done.add(key)
                state["done_steps"] = sorted(done)
                save_state(state)
            continue

        # 工具型阶段
        tool = st.get("tool")
        if not tool:
            continue
        tpath = PROJ / tool
        if not tpath.exists():
            print(f"── {title} ── ⚠️ 工具缺失，跳过：{tool}")
            continue
        args_t = list(st.get("args") or [])
        # 占位符替换
        args_t = [str(a).replace("{label}", label) for a in args_t]
        if "{boards}" in args_t:
            idx = args_t.index("{boards}")
            args_t[idx] = args.board or "all"
        if "{diff_dir}" in args_t:
            idx = args_t.index("{diff_dir}")
            args_t[idx] = str(STATE_DIR / "diff" / f"{label}__current")
        # 门禁会重写全部 boards/*.js —— 先提示
        if sid == "gate":
            print(f"── {title} ── ⚠️ 该阶段会重写 data/boards/*.js（派生物）")
        print(f"── {title} ──")
        r = run_tool(tool, args_t, cwd, timeout, python, dry)
        flag = "✅" if r["rc"] == 0 else ("❌" if not dry else "·")
        print(f"   {flag} {tool} (rc={r['rc']})")
        if r.get("dry"):
            print(f"      → {r['cmd']}")
        else:
            for t in (r.get("stdout") or "").strip().splitlines()[-8:]:
                print(f"      | {t}")
            if r["rc"] != 0:
                for t in (r.get("stderr") or "").strip().splitlines()[-6:]:
                    print(f"      | {t}")
        report["stages"][sid] = {k: v for k, v in r.items() if k != "dry"}
        if r["rc"] != 0 and not dry:
            print(f"   ⛔ 阶段 {sid} 失败，流水线中止")
            report["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
            REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
            return 1

    state["done_steps"] = sorted(done)
    # ⚠️ 不能写 state["last_run"] = state —— 自引用会让 json 序列化抛
    #    "Circular reference detected"。存一份不带 last_run 的副本。
    state["last_run"] = {k: v for k, v in state.items() if k != "last_run"}
    save_state(state)
    report["finished"] = datetime.datetime.now().isoformat(timespec="seconds")
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print()
    print(f"{'✅ DRY-RUN 完成' if dry else '✅ 流水线完成'} · label={label}")
    print(f"   报告 {REPORT_FILE}")
    if dry:
        print("   （未落盘任何改动；加 --apply 真正执行）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="板级重建编排器")
    ap.add_argument("--board", help="只处理某板")
    ap.add_argument("--all", action="store_true", help="处理全部板")
    ap.add_argument("--check", action="store_true", help="体检执行图与顺序依据覆盖")
    ap.add_argument("--apply", action="store_true", help="真正执行（默认 dry-run）")
    ap.add_argument("--resume", action="store_true", help="从上次中断处续跑")
    ap.add_argument("--allow-inferred", action="store_true", help="放行「顺序为推定」的步骤")
    ap.add_argument("--stage", help="只跑指定阶段（逗号分隔）")
    ap.add_argument("--label", help="快照/run 标签（默认时间戳）")
    args = ap.parse_args()

    graph = load_graph()
    if args.check:
        return cmd_check(args, graph)
    if not (args.board or args.all):
        ap.print_help()
        print("\n提示：--check 体检 / --board X 处理单板 / --all 处理全部")
        return 0
    return cmd_run(args, graph)


if __name__ == "__main__":
    sys.exit(main())
