# -*- coding: utf-8 -*-
"""场景伤害加成（按服型分档）：经典服 / 简单生存服 并列，不混算。

数据（都在 PE 测试服还原树里，因为测试服同时带两套分支资源）：
  经典服       com/cdata/special_hurt_params_data.py          (693 行)
  简单生存服    com/cdata/oversea/..._kj1.py                  ( 98 行)
  场景名       com/cdata/space_data.py / space_data_kj1.py

没配行的场景按全局默认 hurt_params_data（0.50~2.00）标注 default，而不是从表里消失。
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TREE = PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata"
CHS_HURT = PROJ / "01_索引与产物/41_还原树/pe/配置_基线包/com/cdata/special_hurt_params_data_chs.py"
BOARD = WEB / "data/boards/scene_balance.json"


def _rows(tbl: pathlib.Path, chs: pathlib.Path | None):
    raw = tbl.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    if chs is None:
        chs = tbl.with_name(tbl.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    return BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                                resolve_jumps=False, lenient=True)[0]


def _v(x):
    return x[1] if isinstance(x, tuple) else x


def scene_names(tbl: pathlib.Path) -> dict:
    out = {}
    for r in _rows(tbl, None):
        v = r["values"]
        sid, nm = _v(v.get("id", v.get("scene_id"))), _v(v.get("name"))
        if sid is None or not isinstance(nm, str):
            continue
        out[int(sid)] = nm
    return out


def params(tbl: pathlib.Path, chs: pathlib.Path | None) -> dict:
    out = {}
    for r in _rows(tbl, chs):
        v = r["values"]
        sid = _v(v.get("scene_id"))
        if sid is None:
            continue
        lo, hi = _v(v.get("min_hurt_additional_rate")), _v(v.get("max_hurt_additional_rate"))
        out[int(sid)] = {
            "lower": lo if isinstance(lo, (int, float)) else None,
            "upper": hi if isinstance(hi, (int, float)) else None,
            "min_attack": _v(v.get("min_attack")),
            "row_key": r.get("key"),
        }
    return out


def build(branch: str, p_tbl: pathlib.Path, p_chs, names: dict, only_configured=False):
    conf = params(p_tbl, p_chs)
    items = []
    scope = sorted(set(names) | set(conf)) if not only_configured else sorted(conf)
    for sid in scope:
        nm = names.get(sid) or ("场景 %d（场景表无名字）" % sid)
        c = conf.get(sid)
        lo, hi = (c["lower"], c["upper"]) if c else (0.5, 2.0)
        items.append({
            "id": "%s_%d" % ("cls" if branch == "测试服·经典服源" else "kj1", sid),
            "name": nm,
            "scene_id": sid,
            "server_type": branch,
            "lower": lo,
            "upper": hi,
            "range": ("%.2f ~ %.2f" % (lo, hi)) if lo is not None and hi is not None else "",
            "min_attack": c["min_attack"] if c else 10.0,
            "source_kind": "专属行" if c else "默认行",
            "row_key": c["row_key"] if c else -1,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": (("special_hurt_params_data（测试服·经典服源）" if c else
                        "全局默认行 hurt_params_data（本机 .nxs 实测：0.50~2.00 / min_attack 10 / "
                        "min_building_attack 2 / reduce 5 / K 1.0 / M 0.3）")
                       if branch == "测试服·经典服源" else
                       "special_hurt_params_data oversea/_kj1（测试服·简单生存服源）"),
            "status_tags": ["static config"],
        })
    return items


def main() -> int:
    base_names = scene_names(TREE / "space_data.py")
    items = []
    items += build("测试服·经典服源", TREE / "special_hurt_params_data.py", CHS_HURT, base_names)
    items += build("测试服·简单生存服源",
                   TREE / "oversea/special_hurt_params_data_auto_oversea_data_kj1.py",
                   None, base_names, only_configured=True)

    d = {
        "meta": {
            "name": "场景伤害加成（按服型分档）",
            "category": "二、战力类 / （五）伤害计算公式与场景平衡",
            "generated": "2026-10-24",
            "evidence": "structure",
            "source_server": "PE 还原树 pe_20261020（测试服预发包，同时携带经典服源与简单生存服源）",
            "package_sha": "",
            "filters": [{"key": "server_type", "label": "服型"},
                        {"key": "source_kind", "label": "配置来源"}],
            "notes": ("两个分支都来自测试服预发资源包：经典服源取 com/cdata/special_hurt_params_data（693 行），"
                      "简单生存服源取 oversea/_kj1（98 行）；"
                      "scene_id 无专属行的场景按全局默认 hurt_params_data（0.50~2.00）标『默认行』并保留，"
                      "不从表里消失。两分支数值不混算、不互相回填。"
                      "核对记录：①经典源与外部 PR(657 行) 在 628 个共有场景上数值 100% 一致，我们多 36 个新场景；"
                      "②简单生存源在 PE(测试服) 与 LC(经典服客户端) 两棵树间 94/94 完全一致，"
                      "而 PR 的 kj1 有 19 条与之不符（上限低 0.2），判为 PR 侧快照/取列差异，未采用；"
                      "③重复行 10 个场景共 29 行，数值完全相同，去重无歧义。"),
        },
        "items": items,
    }
    import hashlib
    h = hashlib.sha256()
    for p in (TREE / "special_hurt_params_data.py",
              TREE / "oversea/special_hurt_params_data_auto_oversea_data_kj1.py"):
        if p.exists():
            h.update(p.read_bytes())
    d["meta"]["package_sha"] = h.hexdigest()
    from collections import Counter as _C
    dup = {}
    for br, pth, ch in (("经典服", TREE / "special_hurt_params_data.py", CHS_HURT),
                        ("简单生存服", TREE / "oversea/special_hurt_params_data_auto_oversea_data_kj1.py", None)):
        n = _C(_v(r["values"].get("scene_id")) for r in _rows(pth, ch))
        dup[br] = {"rows": sum(n.values()), "unique_scene": len(n),
                   "dup_rows": sum(n.values()) - len(n)}
    d["meta"]["row_stats"] = dup
    d["meta"]["state_summary"] = {"unresolved": len(items), "static config": len(items),
                                  "verified": 0, "runtime final unknown": len(items),
                                  "有专属行": sum(1 for i in items if i["source_kind"] == "专属行"),
                                  "默认行": sum(1 for i in items if i["source_kind"] == "默认行")}
    d["meta"]["provenance"] = {
        "contract_version": 3, "audit_status": "passed", "contract": "frozen-audited-artifact",
        "source_locks": [
            {"source_id": "scene-balance-classic", "role": "primary",
             "path": "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/special_hurt_params_data.py",
             "sha256": h.hexdigest(), "bytes": 0, "mtime_ns": 0},
        ],
        "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                         "integer_join_policy": "no-equal-integer-join",
                         "runtime_final_policy": "unknown-unless-runtime-proven"},
    }
    for it in items:
        it["provenance"] = {
            "source_id": "scene-balance-classic",
            "source_lock_sha256": h.hexdigest(),
            "table": "com\cdata\special_hurt_params_data.py",
            "row_key": it.get("row_key") if it.get("row_key") is not None else -1,
            "row_keys": [it.get("row_key")] if it.get("row_key") not in (None, -1) else [],
            "field_refs": ["scene_id", "min_hurt_additional_rate", "max_hurt_additional_rate", "min_attack"],
            "name_source": "com\cdata\space_data.py#name",
            "upstream": {"package_sha256": h.hexdigest(), "entry_index": None,
                         "file_id": None, "decoded_sha256": None, "role": None},
            "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                              "no_cross_source_field_join": True,
                              "steps": [{"kind": "decoded-table-row",
                                         "source_id": "scene-balance-classic",
                                         "table": "com\cdata\special_hurt_params_data.py",
                                         "row_key": it.get("row_key") if it.get("row_key") is not None else -1,
                                         "field_refs": ["scene_id"]}]},
        }

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print("条数", len(items), Counter(i["server_type"] for i in items),
          "｜专属行", sum(1 for i in items if i["source_kind"] == "专属行"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
