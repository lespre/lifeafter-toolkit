#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""gen_rules_inventory.py — 规则层生成器（幂等）

扫描 web/tools/*.py 与 web/data/boards/*.json，产出：
  02_wiki/rules/boards/<board>.yml   每板声明：来源、产物、主产出脚本、后处理脚本、顺序风险
  02_wiki/rules/pipeline.yml          重建流水线：闸门 + 板清单 + 风险汇总
  02_wiki/rules/tools_inventory.yml   脚本分类：build / patch / check / probe / infra / archive 候选

用法：
  python 02_wiki/web/tools/build/gen_rules_inventory.py            # 生成
  python 02_wiki/web/tools/build/gen_rules_inventory.py --dry      # 只打印统计
（无需参数，默认以 __file__ 反推项目根；只读，不改动任何产物）
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

PROJ = pathlib.Path(__file__).resolve().parents[4]        # E:/la拆包项目
WEB = PROJ / "02_wiki" / "web"
TOOLS = WEB / "tools"
BOARDS = WEB / "data" / "boards"
RULES = PROJ / "02_wiki" / "rules"

WRITE_FUNCS = {"write_text", "dump", "writelines", "write_bytes"}
BOARD_HINT = re.compile(r"boards[\\/]|data/boards|BOARDS_DIR", re.I)

# ── 脚本角色判定（按前缀/语义）────────────────────────────────────────
ROLE_BUILD = {
    "build", "rebuild", "register", "stamp", "sync", "refresh", "ensure",
    "export", "generate",
}
ROLE_PATCH = {
    "add", "apply", "fill", "fix", "patch", "merge", "backfill", "import",
    "normalize", "attach", "align", "annotate", "split", "repair", "restore",
    "tidy", "supplement", "wire", "dedupe", "link", "mark", "note", "set",
    "purge", "polish", "reclassify", "regroup", "rewrite", "simplify",
    "decorate", "provenance",
}
ROLE_CHECK = {
    "audit", "check", "verify", "parity", "preview", "run", "list", "find",
    "report", "project", "trace", "show", "print", "estimate", "prune",
}
ROLE_PROBE = {"probe", "cdp", "spine", "decode", "scan", "query", "inspect", "dump", "calib"}
ROLE_INFRA = {
    "wiki", "publication", "provenance", "lib", "img", "source", "make",
    "clean", "push", "download", "index", "carve", "render", "map", "locate",
    "read", "parse", "compare", "convert", "segment", "decrypt", "extract",
    "find", "search", "slim", "refresh", "step", "record", "tune", "live",
    "reload", "apply",
}

ARCHIVE_PREFIX = ("_probe", "probe_", "cdp_probe", "spine_probe", "decode_probe")
ARCHIVE_HINT = re.compile(r"mockup|_tmp", re.I)
# 这些模块是共享库/入口，被现役脚本 import，禁止归档
KEEP_ALWAYS = {"__init__.py", "_src.py", "publication_policy.py", "provenance_standard.py",
                "wiki_server.py", "build_wiki.py"}


def classify_script(name: str) -> tuple[str, bool]:
    """返回 (role, archive_candidate)。仅对探针/一次性脚本给出归档候选。"""
    stem = name[:-3] if name.endswith(".py") else name
    if stem.startswith(ARCHIVE_PREFIX) or ARCHIVE_HINT.search(stem):
        return "probe", True
    head = stem.split("_", 1)[0]
    if head in ROLE_BUILD:
        return "build", False
    if head in ROLE_PATCH:
        return "patch", False
    if head in ROLE_CHECK:
        return "check", False
    if head in ROLE_PROBE:
        return "probe", False
    if head in ROLE_INFRA:
        return "infra", False
    return "other", False


def script_writes_boards(path: pathlib.Path) -> tuple[bool, set[str]]:
    """返回 (是否写板目录, 脚本内出现的字符串常量集合)。"""
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src)
    except Exception:
        return False, set()
    strs = {
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }
    has_write = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fname = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if fname in WRITE_FUNCS:
                has_write = True
            if fname == "open" and len(node.args) >= 2:
                mode = node.args[1]
                if isinstance(mode, ast.Constant) and "w" in str(mode.value):
                    has_write = True
    return has_write, strs


def board_refs(strs: set[str], stems: set[str]) -> set[str]:
    hit: set[str] = set()
    for s in strs:
        for m in re.finditer(r"([a-z0-9_]{3,})\.json", s):
            if m.group(1) in stems:
                hit.add(m.group(1))
        s2 = s.strip()
        if s2 in stems:
            hit.add(s2)
    return hit


def dump_yaml(path: pathlib.Path, obj) -> None:
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )


def validate_rules() -> list[str]:
    """校验手工维护的规则文件是否可解析（生成器自己写 YAML，也要保证人写的能读）。"""
    import yaml
    errs: list[str] = []
    for p in sorted(RULES.glob("*.yml")):
        try:
            yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append(f"{p.name}: {str(e).splitlines()[0]}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只统计不写文件")
    args = ap.parse_args()

    rule_errs = validate_rules()
    if rule_errs:
        print("❌ 规则层 YAML 解析失败，先修规则再生成：")
        for e in rule_errs:
            print("  -", e)
        return 1

    stems = {p.stem for p in BOARDS.glob("*.json")}
    if not stems:
        print("❌ 未找到 data/boards/*.json，终止")
        return 1

    board2prod: dict[str, list[str]] = defaultdict(list)
    inventory: dict[str, dict] = {}

    # 被任何脚本 import 的模块 → 禁止归档（共享库）
    imported: set[str] = set()
    for p in sorted(TOOLS.glob("*.py")):
        try:
            src = p.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    imported.add(a.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)

    for p in sorted(TOOLS.glob("*.py")):
        role, arch = classify_script(p.name)
        if p.name in KEEP_ALWAYS or p.stem in imported:
            arch = False
        writes, strs = script_writes_boards(p)
        touches_boards = any(BOARD_HINT.search(s) for s in strs)
        refs = board_refs(strs, stems) if touches_boards else set()
        if writes and touches_boards:
            for b in refs:
                board2prod[b].append(p.name)
        inventory[p.name] = {
            "role": role,
            "archive_candidate": arch,
            "archived": False,
            "writes_boards": bool(writes and touches_boards),
            "boards": sorted(refs),
        }

    # 已归档脚本（web/tools/_archive/）：保留登记，禁止执行
    archive_dir = TOOLS / "_archive"
    for p in sorted(archive_dir.glob("*.py")) if archive_dir.exists() else []:
        inventory[p.name] = {
            "role": "probe",
            "archive_candidate": False,
            "archived": True,
            "writes_boards": False,
            "boards": [],
        }

    # ── 每板声明 ──────────────────────────────────────────────────────
    board_docs = {}
    risk_rows = []
    for b in sorted(stems):
        jf = BOARDS / f"{b}.json"
        meta, items = {}, 0
        try:
            d = json.loads(jf.read_text(encoding="utf-8-sig"))
            meta = d.get("meta", {}) or {}
            items = len(d.get("items") or [])
        except Exception as e:
            meta = {"_error": str(e)[:120]}
        scripts = sorted(set(board2prod.get(b, [])))
        primary = [s for s in scripts if classify_script(s)[0] == "build"]
        post = [s for s in scripts if classify_script(s)[0] != "build"]
        doc = {
            "board": b,
            "name": meta.get("name"),
            "category": meta.get("category"),
            "source_server": meta.get("source_server"),
            "package_sha": meta.get("package_sha"),
            "generated": meta.get("generated"),
            "evidence": meta.get("evidence"),
            "items": items,
            "primary_builders": primary,
            "postprocess_scripts": post,
            "script_count": len(scripts),
            "rebuild_risk": "high" if len(scripts) >= 10 else ("mid" if len(scripts) >= 4 else "low"),
        }
        board_docs[b] = doc
        if len(scripts) >= 10:
            risk_rows.append((b, len(scripts), len(post)))

    if not args.dry:
        for b, doc in board_docs.items():
            dump_yaml(RULES / "boards" / f"{b}.yml", doc)

        dump_yaml(RULES / "pipeline.yml", {
            "version": 1,
            "generated_by": "web/tools/build/gen_rules_inventory.py",
            "raw_layer": "01_索引与产物/30_分析 冻结产物（每两周热更后替换）",
            "rule_layer": "02_wiki/rules（人工/agent 维护，禁止自动覆盖）",
            "artifact_layer": "02_wiki/web/data/boards（纯生成，产物零手改）",
            "publish_gate": {
                "command": "python 02_wiki/web/tools/build_wiki.py",
                "role": "校验 + 导出 manifest.js / 每板 .js / manifest.json / build_meta.js",
                "note": "它不是全量构建器：只校验既有 boards/*.json 并导出产物",
            },
            "inventory_generator": "python 02_wiki/web/tools/build/gen_rules_inventory.py",
            "board_count": len(board_docs),
            "high_risk_boards": [
                {"board": b, "script_count": n, "postprocess_count": p}
                for b, n, p in sorted(risk_rows, key=lambda x: -x[1])
            ],
            "boards": sorted(board_docs),
        })

        roles = Counter(v["role"] for v in inventory.values())
        dump_yaml(RULES / "tools_inventory.yml", {
            "version": 1,
            "generated_by": "web/tools/build/gen_rules_inventory.py",
            "total": len(inventory),
            "role_counts": dict(roles),
            "policy": {
                "build": "现役：主产出脚本，产出 boards/*.json 主体",
                "patch": "现役：后处理脚本，改写已产出板，顺序敏感",
                "check": "现役：只读校验，可随时跑",
                "probe": "探针/探查，多数为一次性，归档候选",
                "infra": "公共库/服务/工具",
                "other": "未归类，需人工判定",
                "archive_candidate": "建议迁入 web/tools/_archive/，禁止执行",
            },
            "scripts": {
                k: {"role": v["role"], "writes_boards": v["writes_boards"],
                    "archive_candidate": v["archive_candidate"],
                    "archived": v.get("archived", False),
                    "boards": v["boards"]}
                for k, v in sorted(inventory.items())
            },
        })

    print(f"板文件 {len(stems)} 个 → rules/boards/*.yml")
    print(f"高风险板（≥10 脚本经手）{len(risk_rows)} 个：")
    for b, n, p in sorted(risk_rows, key=lambda x: -x[1]):
        print(f"  {b}: {n} 脚本（后处理 {p}）")
    print("工具脚本角色分布：", dict(Counter(v["role"] for v in inventory.values())))
    print("归档候选：", sum(1 for v in inventory.values() if v["archive_candidate"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
