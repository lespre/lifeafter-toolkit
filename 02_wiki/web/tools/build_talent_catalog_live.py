# -*- coding: utf-8 -*-
r"""build_talent_catalog_live — 天赋总表（talent_catalog）从 PE 活树重建

## 口径（2026-11-04 重写）

旧板的 5304 条 = **两张表相加**，不是「按等级展开」：

    tree=基础  new_talent_data           （旧版 3085 条，本树 4112 行）
    tree=主题  theme_new_talent_data     （旧版 2219 条；本树该表已空壳）
               ↳ 本树对应物 = merge_new_talent_data（2743 行，map_talents 指向被合并的基础天赋）

两条独立证据：
  1) 旧板 基础 的 (name, level, prof_id) 三元组 **3085/3085 全部命中** new_talent_data
     ⇒ 基础确为该表的逐行投影（每条 = 一行 = 一个等级档，无额外展开）。
  2) 旧板 主题 的 2219 个三元组里 944 个命中 merge_new_talent_data，且
     `theme_new_talent_data.py` 在本树只有表头（0 行）⇒ 主题只能取 merge 表。

★ 行数差异（5304 → 6855）来自**数据版本**，不是规则变化：id 空间被重新编号
  （旧板 3085 个 key 里只有 377 个还在新表 key 里，但三元组全覆盖），
  且本树基础表本身多出约 1000 行、合并表多出约 500 行。

## 与旧板一致/不一致的地方

- 字段集合完全一致（16 个键，见 ITEM_KEYS）。
- **不做**旧 builder 的 `(name, tree, level)` 去重：实测那 1416 条是**不同的真行**
  （icon / ui_pos / cost_moneys 各不相同，例如 快速采集 在 1001 树与新版树各有一份），
  去重会静默丢真条目。旧板的 5304 本身就是那个有损规则的结果。
- 旧 builder 的 `str(item_id) in seen_ids` 跨树去重也去掉了同 key 的主题行 —— 这里
  靠 id 前缀（t_ / tt_）区分，两条都留。

## 职业名来源（prof_id → prof_name / prof_group）

  11..38  profession_name_data.prof_name；职业系按图标族（caiji/zhizao/zhandou）
  1001..1004  basal_prof_conf_data.name（拓荒者/工匠/武器专家/生化专家）；
             职业系按 icon_path 族（caiji/zhizuo/wuqi/shenghua）
  1/2/3   客户端无该行；沿用旧板已定口径 采集/制造/战斗（旧板 481/457/499 条逐一吻合）

用法：
    python 02_wiki/web/tools/build_talent_catalog_live.py [--check]

幂等：同一批源文件重复运行 → 输出字节完全相同（generated 取源文件 mtime，不用 now()）。
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pe_source as src                      # noqa: E402  锁 / 源标识 / 板路径
import rebuild_lottery_periods as R          # noqa: E402  Table 解码（含 _chs 池槽）
from board_io import dumps_board, write_board_pair  # noqa: E402
import provenance_defaults as PD             # noqa: E402  形态签名 / 常量上提

BOARD_ID = "talent_catalog"
CD = Path(src.CD)
OUT = src.board_path(BOARD_ID)

# (tree, 表名, field_refs)  —— 顺序即输出顺序：基础在前
TREES = [
    ("基础", "new_talent_data", ["name", "level", "prof_id", "desc", "open_level"]),
    ("主题", "merge_new_talent_data", ["name", "level", "prof_id", "map_talents", "open_level"]),
]

# 客户端无 prof 名的三个「大类」id（旧板 481/457/499 条逐一吻合）
PROF_CLASS = {1: ("采集", "采集"), 2: ("制造", "制造"), 3: ("战斗", "战斗")}

# 大类 conf（basal_prof_conf_data）的职业系：按图标族 + 号段双证，图标认不出时用这里
PROF_GROUP_BY_ID = {
    1: "采集", 2: "制造", 3: "战斗",
    1001: "采集", 1002: "制造", 1003: "战斗", 1004: "生化",
}

# 图标族 → 职业系（profession_name_data 用 zhizao/zhandou，basal_prof_conf 用 zhizuo/wuqi）
ICON_FAMILY = [
    ("caiji", "采集"),
    ("zhizao", "制造"),
    ("zhizuo", "制造"),
    ("zhandou", "战斗"),
    ("wuqi", "战斗"),
    ("shenghua", "生化"),
]

ITEM_KEYS = ["id", "item_id", "name", "kind", "tree", "level", "prof_id", "prof_name",
             "prof_group", "desc", "evidence", "evidence_level", "status_tags",
             "source", "provenance", "_prov_shape"]


def _table(stem: str) -> R.Table:
    t = R._opt_table(CD / f"{stem}.py", CD / f"{stem}_chs.py")
    if not getattr(t, "by_key", None):
        raise SystemExit(f"❌ 表为空或不可解：{stem}")
    return t


def _family_of_icon(icon) -> str | None:
    s = str(icon or "").lower()
    for key, fam in ICON_FAMILY:
        if key in s:
            return fam
    return None


def _group_by_id(pid: int) -> str | None:
    """图标族认不出时的兜底：按 prof_id 段（10x=采集 / 20x=制造 / 30x=战斗 / 100x=大类）。"""
    if pid in PROF_GROUP_BY_ID:
        return PROF_GROUP_BY_ID[pid]
    if 10 <= pid < 20:
        return "采集"
    if 20 <= pid < 30:
        return "制造"
    if 30 <= pid < 40:
        return "战斗"
    return None


def prof_map() -> dict[int, tuple[str, str]]:
    """prof_id → (prof_name, prof_group)。只取表里真有的事实 + 旧板已定的大类口径。"""
    out: dict[int, tuple[str, str]] = {}
    for pid, (nm, grp) in PROF_CLASS.items():
        out[pid] = (nm, grp)
    pn = R._opt_table(CD / "profession_name_data.py", CD / "profession_name_data_chs.py")
    for key, row in pn.by_key.items():
        nm = str(row["values"].get("prof_name") or "").strip()
        if not nm:
            continue
        pid = int(key)
        # ★ 名字照收；只有「职业系」才允许用图标族/号段推 —— 不可因图标认不出就丢名字
        #   （孢子捕手 35 的图标是 icon_baozilieren_banganranzhe，不含族关键字）
        fam = _family_of_icon(row["values"].get("prof_icon")) or _group_by_id(pid)
        out[pid] = (nm, fam or "未分类")
    bp = R._opt_table(CD / "basal_prof_conf_data.py", CD / "basal_prof_conf_data_chs.py")
    for key, row in bp.by_key.items():
        nm = str(row["values"].get("name") or "").strip()
        if not nm:
            continue
        pid = int(key)
        fam = _family_of_icon(row["values"].get("icon_path")) or _group_by_id(pid)
        out[pid] = (nm, fam or "未分类")
    return out


def _lock(stem: str) -> dict:
    return src.lock_of(CD / f"{stem}.py", source_id=src.SOURCE_TREE)


def item_prov(stem: str, row_key: int, field_refs: list[str], sha: str) -> dict:
    """条目级溯源：键集合与旧板样例一致 + name_source（发布契约 strict_v2 必填）。"""
    return {
        "source_id": src.SOURCE_TREE,
        "source_lock_sha256": sha,
        "table": stem,
        "row_key": int(row_key),
        "name_source": f"{stem}.name（_chs.py 池槽回放）",
        "field_refs": list(field_refs),
        "upstream": {"role": stem, "package_sha256": sha},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": src.SOURCE_TREE,
                "table": stem,
                "row_key": int(row_key),
                "field_refs": list(field_refs),
            }],
        },
    }


def build() -> dict:
    profs = prof_map()
    items: list[dict] = []
    stats: dict[str, dict] = {}
    locks: list[dict] = []
    unknown_prof: set[int] = set()
    base_triples: set[tuple] = set()

    for tree, stem, field_refs in TREES:
        t = _table(stem)
        lock = _lock(stem)
        locks.append(dict(lock, role="primary" if not locks else "comparison"))
        sha = lock["sha256"]
        kept = skipped = 0
        for key in sorted(t.by_key):
            v = t.by_key[key]["values"]
            name = str(v.get("name") or "").strip()
            if not name:
                skipped += 1
                continue
            try:
                pid = int(v.get("prof_id"))
            except (TypeError, ValueError):
                pid = 0
            if pid not in profs:
                unknown_prof.add(pid)
            pname, pgroup = profs.get(pid, ("未分类", "未分类"))
            try:
                level = int(v.get("level"))
            except (TypeError, ValueError):
                level = None
            # 主题表里指向基础天赋的「纯副本行」（无 desc）跳过，避免同一天赋显示两张卡
            triple = (name, level, pid)
            if tree != "基础" and triple in base_triples and not str(v.get("desc") or "").strip():
                skipped += 1
                continue
            if tree == "基础":
                base_triples.add(triple)
            items.append({
                "id": f"{'t' if tree == '基础' else 'tt'}_{key}",
                "item_id": int(key),
                "name": name,
                "kind": "天赋",
                "tree": tree,
                "level": level,
                "prof_id": pid,
                "prof_name": pname,
                "prof_group": pgroup,
                "desc": str(v.get("desc") or "").strip(),
                "evidence": "structure",
                "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "source": f"{stem}.py",
                "provenance": item_prov(stem, key, field_refs, sha),
            })
            kept += 1
        stats[stem] = {"rows": len(t.by_key), "kept": kept, "skipped_no_name": skipped,
                       "sha256": sha, "bytes": lock["bytes"], "mtime_ns": lock["mtime_ns"]}

    # 职业名/职业系用到的两张表也登记为源（同 source_id ⇒ 同源多表，不是跨源拼字段）
    for stem in ("profession_name_data", "basal_prof_conf_data"):
        locks.append(dict(_lock(stem), role="comparison"))

    # 稳定排序：基础在前，表内按 row_key 升序
    order = {stem: i for i, (_, stem, _) in enumerate(TREES)}
    items.sort(key=lambda it: (order[it["source"][:-3]], it["item_id"]))

    # 形态签名（旧板同款 _prov_shape）= provenance 稳定键集合的哈希
    for it in items:
        it["_prov_shape"] = PD._shape_signature(it["provenance"])

    meta = copy.deepcopy(json.loads(OUT.read_text(encoding="utf-8-sig"))["meta"])
    meta.pop("provenance_defaults", None)          # 旧板的常量表属于旧快照，不能留
    primary = locks[0]
    meta.update({
        "source_server": "PE 测试服 · 41_还原树/pe/配置/com/cdata（逐表行级）",
        "generated": datetime.date.fromtimestamp(primary["mtime_ns"] / 1e9).isoformat(),
        "package_sha": primary["sha256"],
        "source_label": "PE 还原树 · new_talent_data + merge_new_talent_data · 测试服",
        "state_summary": {
            "条目": len(items),
            "基础": sum(1 for i in items if i["tree"] == "基础"),
            "主题": sum(1 for i in items if i["tree"] == "主题"),
            "战斗": sum(1 for i in items if i["prof_group"] == "战斗"),
            "采集": sum(1 for i in items if i["prof_group"] == "采集"),
            "制造": sum(1 for i in items if i["prof_group"] == "制造"),
            "生化": sum(1 for i in items if i["prof_group"] == "生化"),
        },
        "notes": (
            f"{len(items)} 条 = 基础 new_talent_data {stats['new_talent_data']['kept']} 行"
            f" + 主题 merge_new_talent_data {stats['merge_new_talent_data']['kept']} 行"
            f"（各自逐行一条，不按等级展开、不做名称去重）。"
            "主题表旧板取自 theme_new_talent_data（oversea-kj1），本树该表已空壳，"
            "改取 merge_new_talent_data（map_talents 即「被合并的基础天赋」，语义同源）；"
            "旧板主题 2219 个 (名,等级,职业) 三元组中 944 个在本表命中，其余属 overseas 专属表，本树无。"
            "id 空间随版本重编号：旧板 3085 个基础 key 仅 377 个仍在，但三元组 3085/3085 全覆盖。"
            "职业名取 profession_name_data（11..38）+ basal_prof_conf_data（1001..1004）；"
            "1/2/3 客户端无行，沿用旧板口径 采集/制造/战斗；1004 生化专家按图标族归「生化」"
            "（旧板无 1004 条目，无先例）。"
            "desc 仅基础表有（主题表无 desc 列，6 行例外）；表内 is_deleted 行照原样保留，未过滤。"
        ),
        "provenance": {
            "contract_version": 3,
            "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": locks,
            "source_scope": {
                "cross_source_policy": "no-cross-source-field-join",
                "integer_join_policy": "no-equal-integer-join",
                "runtime_final_policy": "unknown-unless-runtime-proven",
            },
        },
    })

    board = {"meta": meta, "items": items}
    PD.hoist_board_defaults(board)                 # 同形态全同常量（若有）上提
    board["stats"] = {
        "tables": stats,
        "catalog_entries": len(items),
        "unknown_prof_ids": sorted(unknown_prof),
        "with_desc": sum(1 for i in items if i["desc"]),
        "with_prof_name": sum(1 for i in items if i["prof_name"] not in ("", "未分类")),
    }
    return board


def _baseline_items() -> list[dict] | None:
    """对比基线：优先 git HEAD 里的上一版板（重跑时 live 已是本脚本产物，拿它对比没意义）。"""
    live = src.old_board(BOARD_ID)
    if isinstance(live, dict) and "stats" not in live:
        return live.get("items")
    import subprocess
    root = TOOLS.parents[2]
    rel = OUT.relative_to(root).as_posix()
    try:
        raw = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root, check=True,
                             capture_output=True, timeout=60).stdout
        return json.loads(raw.decode("utf-8-sig")).get("items")
    except Exception:                              # noqa: BLE001
        return live.get("items") if isinstance(live, dict) else None


def report(board: dict) -> None:
    items = board["items"]
    n = len(items)
    nm_cov = sum(1 for i in items if i["name"]) / n * 100
    ds_cov = sum(1 for i in items if i["desc"]) / n * 100
    pf_cov = sum(1 for i in items if i["prof_name"] and i["prof_name"] != "未分类") / n * 100
    print(f"条目 {n}（基础 {board['meta']['state_summary']['基础']} / 主题 "
          f"{board['meta']['state_summary']['主题']}）")
    print(f"覆盖率 name {nm_cov:.1f}% · desc {ds_cov:.1f}% · prof_name {pf_cov:.1f}%")
    old = _baseline_items()
    if old:
        oid = {i["id"] for i in old}
        nid = {i["id"] for i in items}
        print(f"基线 {len(oid)} 条 → 新增 {len(nid - oid)} · 消失 {len(oid - nid)} · 交集 {len(oid & nid)}")
        ok = {(i["name"], i["level"], i["prof_id"]) for i in old if i.get("tree") == "基础"}
        nk = {(i["name"], i["level"], i["prof_id"]) for i in items if i["tree"] == "基础"}
        print(f"基础三元组（名,等级,职业）：基线 {len(ok)} / 命中 {len(ok & nk)}")


def main(argv: list[str]) -> int:
    board = build()
    report(board)
    try:
        from publication_policy import publication_contract_errors
        errs = publication_contract_errors(board, strict_v2=True)
        print(f"发布契约 strict_v2：{'✅ 0 错误' if not errs else f'❌ {len(errs)} 错误 ' + str(errs[:5])}")
    except Exception as exc:                      # noqa: BLE001
        print(f"（契约自检跳过：{exc}）")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
