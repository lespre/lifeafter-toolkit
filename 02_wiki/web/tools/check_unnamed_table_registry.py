# -*- coding: utf-8 -*-
"""只读校验：`rules/unnamed_table_registry.yml` 的登记项在还原树里是否找得到、解得开。

这是「无名大表 → 逻辑表名」契约的**验收关卡**，不写任何文件。

退出码：
  0  登记项全部命中且可解（未登记的大表只列告警）
  2  有登记项在树里找不到，或解不开 ⇒ 应阻断后续构建
  3  契约文件/索引缺失

用法：
  python 02_wiki/web/tools/check_unnamed_table_registry.py
  python 02_wiki/web/tools/check_unnamed_table_registry.py --json        # 机器可读
  python 02_wiki/web/tools/check_unnamed_table_registry.py --no-inventory  # 跳过反向盘点
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import unnamed_registry as UREG  # noqa: E402
from la_paths import RULES_DIR, rel  # noqa: E402
from pe_source import body_of  # noqa: E402

from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import lottery_chain as LC  # noqa: E402

REGISTRY = RULES_DIR / "unnamed_table_registry.yml"
MP = LC._mods()["MP"]
MIN_BLOB = 100_000  # 反向盘点只看大 blob，避免把几万个小资源算进来


def load_registry() -> dict:
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("缺 PyYAML，无法读契约文件") from e
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def check_entry(p: pathlib.Path, kind: str, expect: dict) -> dict:
    """解一个 blob，报实际值；与登记里的 observed_* 不一致只算版本变化，不算错误。"""
    out: dict = {"path": rel(p), "bytes": p.stat().st_size, "kind": kind, "ok": False}
    try:
        raw = p.read_bytes()
        if kind == "data":
            rows, _ = BT.decode_table_rows(body_of(raw), [], resolve_jumps=False)
            out["rows"] = len(rows)
            out["declared_rows"] = expect.get("observed_rows")
            out["ok"] = len(rows) > 0
        else:
            pool = MP.pool_of_file(p)
            out["strings"] = len(pool)
            out["declared_strings"] = expect.get("observed_strings")
            out["ok"] = len(pool) > 0
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
    return out


def inventory_unregistered(root: pathlib.Path, known: set[pathlib.Path]) -> list[dict]:
    """反向盘点：无名层里还有多少能解但没登记的大表/池。

    ★ 不做自动配对、不猜逻辑名 —— 只列出来交人工判定（符合「不猜数」铁律）。
    """
    found = []
    for p in sorted(root.rglob("*.bin")):
        try:
            if p.stat().st_size < MIN_BLOB or p in known:
                continue
        except OSError:
            continue
        raw = p.read_bytes()
        if b"x{" in raw:
            try:
                rows, _ = BT.decode_table_rows(body_of(raw), [], resolve_jumps=False)
                if rows:
                    found.append({"path": rel(p), "kind": "data", "rows": len(rows),
                                  "bytes": p.stat().st_size})
                    continue
            except Exception:
                pass
        try:
            pool = MP.pool_of_file(p)
            if pool:
                found.append({"path": rel(p), "kind": "pool", "strings": len(pool),
                              "bytes": p.stat().st_size})
        except Exception:
            pass
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非人读报告")
    ap.add_argument("--no-inventory", action="store_true", help="跳过未登记大表盘点（更快）")
    a = ap.parse_args()

    if not REGISTRY.is_file():
        print("契约文件不存在：%s" % rel(REGISTRY))
        return 3

    cfg = load_registry()
    root = UREG.tree_root()
    report: dict = {"registry": rel(REGISTRY), "key_policy": cfg.get("key_policy"),
                    "entries": [], "unregistered": [], "errors": []}
    known: set[pathlib.Path] = set()

    for t in cfg.get("tables") or []:
        name = t["logical_name"]
        comp = t.get("component") or "base"
        container = t.get("container") or ""
        for kind in ("data", "pool"):
            spec = t.get(kind)
            if not spec:
                continue
            p, state = UREG.resolve_entry(spec["file_id"], container,
                                          spec.get("observed_row_name"))
            if p is None:
                report["errors"].append("%s@%s.%s: 树里找不到（fid_names 无记录，"
                                        "占位名也不存在）" % (name, comp, kind))
                report["entries"].append({"table": name, "component": comp, "kind": kind,
                                          "file_id": spec["file_id"], "ok": False,
                                          "path": None, "resolve_state": state})
                continue
            known.add(p)
            rec = check_entry(p, kind, spec)
            rec.update({"table": name, "component": comp, "file_id": spec["file_id"],
                        "resolve_state": state})
            report["entries"].append(rec)
            if not rec["ok"]:
                report["errors"].append("%s@%s.%s: 解不开 %s" % (name, comp, kind, rel(p)))

    if not a.no_inventory and root.is_dir():
        report["unregistered"] = inventory_unregistered(root, known)

    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 2 if report["errors"] else 0

    print("契约: %s ｜ 主键: %s" % (report["registry"], report["key_policy"]))
    print("\n── 已登记项 ──")
    for e in report["entries"]:
        tag = "%s@%s" % (e["table"], e["component"])
        if not e.get("ok"):
            print("  [FAIL] %-26s %-5s %s  %s" %
                  (tag, e["kind"], e["file_id"], e.get("path") or e.get("error", "")))
            continue
        val = ("%s 行" % e["rows"]) if e["kind"] == "data" else ("%s 串" % e["strings"])
        declared = e.get("declared_rows") if e["kind"] == "data" else e.get("declared_strings")
        note = "" if declared is None or declared == (e.get("rows") or e.get("strings")) \
            else "  (登记时 %s，版本已变)" % declared
        deg = "" if e.get("resolve_state") == UREG.STATE_VERIFIED else "  [降级:按行号名]"
        print("  [ OK ] %-26s %-5s %s  %s  → %s%s%s" %
              (tag, e["kind"], e["file_id"], val, e["path"], note, deg))

    print("\n── 未登记的可解大表（只告警，交人工判定）──")
    if not report["unregistered"]:
        print("  (无)")
    else:
        c = Counter(x["kind"] for x in report["unregistered"])
        print("  共 %d 个：主表 %d / 池 %d" %
              (len(report["unregistered"]), c["data"], c["pool"]))
        for x in report["unregistered"][:12]:
            v = ("%s 行" % x["rows"]) if x["kind"] == "data" else ("%s 串" % x["strings"])
            print("    %-5s %10s  %s" % (x["kind"], v, x["path"]))
        if len(report["unregistered"]) > 12:
            print("    … 其余 %d 个见 --json" % (len(report["unregistered"]) - 12))

    print("\n── 结论 ──")
    if report["errors"]:
        for e in report["errors"]:
            print("  ✗ " + e)
        print("  ⇒ 退出码 2，应阻断后续构建")
        return 2
    print("  ✓ 全部登记项命中且可解；未登记项不阻断")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
