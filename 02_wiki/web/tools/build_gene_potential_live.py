#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 PE 活树重建「种族潜能总表」（gene_potential_catalog）。

## 数据来源（全部在 PE 活树内，不碰 PC 客户端 / APK）

   01_索引与产物/41_还原树/pe/配置/com/cdata/
     gene_node_data.nxs            ← 经典服/内测侧节点表（141 行，行级解码）
     gene_node_data_chs.py         ← 同表字符串池（266 串：字段名 + 取值）
     oversea/gene_node_data_auto_oversea_data_kj1.py  ← 简单生存服节点表（63 行）
     oversea/gene_node_data_auto_oversea_data_kj1_chs.py

## 为什么旧板只有 104 条、且 56 条没有字段

旧板用的是 Documents 快照，`gene_node_data` 表体当时解不开（0x73 容器 / 76-idx
都没命中载荷），所以 56 条只能从 `_chs` 池里拿到「名字 + 档位」，race/分值/效果
全部为 null。PE 活树这份 `gene_node_data.nxs` 的 bindict 表体是**完整可解**的：

    264 偏移处 `7b <u32 8996>`：payload 头 = count 266 / reserved 0
    blob = payload[8+4*266:] → 0x76 索引尾 141 个 key → 141 行全部解出

所以本板改为**行级来源**：`node_name / race / level / node_score / effect_desc`
全部来自表体，不再有「名册级」条目。

## 两个必须知道的坑

1. `xbody()`（rebuild_lottery_periods）在这张表上会**偏 1 字节**：
   它找 `b"x{"`，而表体前一个字节 0x78（NONE）紧跟 0x7b（STRING）时命中在 0x7b
   之前 ⇒ 读到假 count。这里自带 `_find_payload()` 自校验扫描（扫 7b/fb + u32 长
   + payload 头 (count, 0) + 8+4*count < len），不依赖 xbody。
2. **同一 key 在两服不是同一个节点**：base 1003 = 初级潜能:护甲强化，
   kj1 1003 = 初级潜能:暴击强化（63 个 key 里 41 个名字不同）。
   ⇒ 跨服合并**只能按 (race, node_name)**，不能按 key 对齐；
   简单生存独有的节点 id 前缀加 `gene_kj1_`，避免和经典服 id 撞名。

## 口径（沿用旧板，不改）

- race 1 = 通用（不属任何种族）→ **不入板**，只记 `dropped_common_rows`。
- race 2=人类 / 3=半感染者（旧称再生者）/ 4=械骨人。

输出：`02_wiki/web/data/boards/gene_potential_catalog.json` (+ .js)
幂等：同一份 PE 树连续跑两次，输出字节完全相同。
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from la_paths import TREE_ROOT, WEB, TOOLKIT_CORE  # noqa: E402

sys.path.insert(0, str(TOOLKIT_CORE))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data" / "boards" / "gene_potential_catalog.json"

PE_CDATA = Path(TREE_ROOT) / "pe" / "配置" / "com" / "cdata"
BASE_TABLE = "gene_node_data.nxs"
BASE_POOL = "gene_node_data_chs.py"
KJ1_TABLE = "oversea/gene_node_data_auto_oversea_data_kj1.py"
KJ1_POOL = "oversea/gene_node_data_auto_oversea_data_kj1_chs.py"

SOURCE_ID = "pe-merged-config"
SOURCE_LABEL = "PE 活树 41_还原树/pe/配置 · gene_node_data(base, 行级) + oversea kj1(行级)"

RACE_NAMES = {1: "通用", 2: "人类", 3: "半感染者", 4: "械骨人"}
# 口径开关：race=1 是「全种族共享」节点，按旧板既有口径不入板面（旧板 meta.dropped_common_*）。
# 要恢复这 30 条只改这里 —— 其余逻辑按 race 自洽，不需要动别处。
KEEP_COMMON = False
TIERS = ("初级", "中级", "高级", "特级", "超级", "究级")
POTENTIAL_TIER_ORDER = {t: i for i, t in enumerate(TIERS)}

# 旧板保留的 meta 字段原样沿用（前端按它渲染卡片/筛选）
META_KEEP = ("name", "category", "id_label", "hide_media", "evidence",
             "card_mode", "card_summary", "field_labels", "filters", "race_rule")


# ────────────────────────────────────────────── 表体装载
def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_payload(raw: bytes) -> tuple[int, int]:
    """扫 0x7b/0xfb + u32 长 + payload 头 (count, 0)，返回 (payload 起点, 长度)。

    自校验三条：count 合理、reserved==0、8+4*count < 载荷长（否则行索引表压掉全部 blob）。
    """
    for j in range(len(raw) - 5):
        if raw[j] not in (0x7B, 0xFB):
            continue
        n = struct.unpack_from("<I", raw, j + 1)[0]
        if not (0 < n < len(raw) - j - 5):
            continue
        head = raw[j + 5:j + 13]
        if len(head) < 8:
            continue
        count, reserved = struct.unpack_from("<II", head, 0)
        if 0 < count < 200_000 and reserved == 0 and 8 + 4 * count < n:
            return j + 5, n
    raise ValueError("表体载荷未命中（0x7b/0xfb + count/reserved 自校验全失败）")


def load_table(table_rel: str, pool_rel: str) -> tuple[dict[int, dict], dict]:
    """解一张 gene_node_data 表 → ({key: {字段: 值}}, 证据字典)。"""
    tpath = PE_CDATA / table_rel
    ppath = PE_CDATA / pool_rel
    raw = tpath.read_bytes()
    start, length = _find_payload(raw)
    body = raw[start:start + length]
    pool = parse_legacy_chs_pool(ppath.read_bytes())
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)
    if unbound:
        raise ValueError(f"{table_rel}: {len(unbound)} 行解不动，拒绝写半张表")
    out: dict[int, dict] = {}
    for row in rows:
        out[row["key"]] = {k: (v[1] if isinstance(v, tuple) else v)
                           for k, v in row["values"].items()}
    evidence = {
        "file": table_rel,
        "payload_offset": start - 5,
        "payload_bytes": length,
        "header_count": struct.unpack_from("<I", body, 0)[0],
        "row_count": len(rows),
        "pool_strings": len(pool),
        "sha256": _sha256(tpath),
    }
    return out, evidence


# ────────────────────────────────────────────── 条目构造
def _tier_of(name: str) -> str:
    for t in TIERS:
        if name.startswith(t + "潜能"):
            return t
    return "特殊"


def _provenance(key: int, table: str, sha: str, *, role: str = "gene_node_data",
                stem: str = BASE_TABLE) -> dict:
    """行级溯源：source 文件 sha + 表名 + 行 key + 定位链。

    ★ 不写 row_offset：该表的行 key 就是节点 id，行号 = key，重复一份只会让
      `provenance_defaults` 的形态签名（STABLE_KEYS 里含 row_offset）多一个噪声键。"""
    return {
        "source_id": SOURCE_ID,
        "source_lock_sha256": sha,
        "table": table,
        "row_key": key,
        "name_source": f"{stem}.node_name（_chs.py 池槽回放）",
        "upstream": {"role": role, "package_sha256": sha},
        "field_refs": ["node_name", "race", "level", "node_score",
                       "effect_desc", "icon_path"],
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": SOURCE_ID,
                "table": table,
                "row_key": key,
                "field_refs": ["node_name", "race", "level", "node_score",
                               "effect_desc"],
            }],
        },
    }


def build() -> dict:
    base, base_ev = load_table(BASE_TABLE, BASE_POOL)
    kj1, kj1_ev = load_table(KJ1_TABLE, KJ1_POOL)

    if len(base) < 100:
        raise ValueError(f"base 只解出 {len(base)} 行，低于安全阈值，拒绝重建")

    # 字段完整性自检：缺一个就报错，不写半张表
    for k, v in base.items():
        for f in ("node_name", "race", "level", "node_score", "effect_desc"):
            if v.get(f) in (None, ""):
                raise ValueError(f"base 行 {k} 缺字段 {f}")

    base_pairs = {(v["race"], v["node_name"]) for v in base.values()}
    kj1_by_pair = {(v["race"], v["node_name"]): v for v in kj1.values()}
    kj1_pairs = set(kj1_by_pair)

    items: list[dict] = []
    dropped_common = 0

    for key in sorted(base):
        v = base[key]
        if v["race"] not in (2, 3, 4):
            if not KEEP_COMMON:
                dropped_common += 1
                continue
        pair = (v["race"], v["node_name"])
        branches = ["经典服"]
        branch_label = "经典服（PE gene_node_data base 行级）"
        score_by_branch = None
        note = "节点表行级解码：node_name/race/level/node_score/effect_desc 均取自表体"
        if pair in kj1_pairs:
            branches = ["简单生存", "经典服"]
            branch_label = "经典服 + 简单生存（同种族同名节点，两服同名册）"
            kj1_row = kj1_by_pair[pair]
            if kj1_row.get("node_score") != v["node_score"]:
                score_by_branch = {"经典服": v["node_score"],
                                   "简单生存": kj1_row["node_score"]}
                note = ("两服同名节点但分值不同：本行 node_score 取经典服，"
                        "简单生存侧见 node_score_branches")
        items.append({
            "id": f"gene_{key}",
            "item_id": key,
            "name": v["node_name"],
            "kind": "种族潜能",
            "race": v["race"],
            "race_name": RACE_NAMES[v["race"]],
            "level": v["level"],
            "node_score": v["node_score"],
            "effect_desc": v["effect_desc"],
            "tier": _tier_of(v["node_name"]),
            "icon_path": v.get("icon_path"),
            "server_branch": branch_label,
            "server_branches": branches,
            "fields_note": note,
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "gene_node_data(base, PE)",
            "provenance": _provenance(key, f"com/cdata/{BASE_TABLE}",
                                      base_ev["sha256"]),
            **({"node_score_branches": score_by_branch} if score_by_branch else {}),
        })

    # 简单生存独有的节点：不能按 key 合并（同 key 不同节点），id 加前缀
    kj1_only = 0
    for key in sorted(kj1):
        v = kj1[key]
        if v["race"] not in (2, 3, 4) and not KEEP_COMMON:
            continue
        if (v["race"], v["node_name"]) in base_pairs:
            continue
        kj1_only += 1
        items.append({
            "id": f"gene_kj1_{key}",
            "item_id": key,
            "name": v["node_name"],
            "kind": "种族潜能",
            "race": v["race"],
            "race_name": RACE_NAMES[v["race"]],
            "level": v["level"],
            "node_score": v["node_score"],
            "effect_desc": v["effect_desc"],
            "tier": _tier_of(v["node_name"]),
            "icon_path": v.get("icon_path"),
            "server_branch": "简单生存（PE oversea gene_node_data kj1 行级，经典服无此节点）",
            "server_branches": ["简单生存"],
            "fields_note": "简单生存独有节点；同 key 在经典服表里指向另一个节点，故 id 加 gene_kj1_ 前缀",
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "gene_node_data(kj1, PE)",
            "provenance": _provenance(key, f"com/cdata/{KJ1_TABLE}",
                                      kj1_ev["sha256"],
                                      role="gene_node_data_oversea_kj1",
                                      stem=KJ1_TABLE),
        })

    items.sort(key=lambda it: (it["race"], POTENTIAL_TIER_ORDER.get(it["tier"], 99),
                               it["level"], it["item_id"]))

    tier_counter = Counter(it["tier"] for it in items)
    race_counter = Counter(it["race_name"] for it in items)

    meta = {
        "name": "（内测版）种族潜能总表",
        "category": "二、战力类 / （七）各种族潜能",
        "source_server": "经典服（行级）+ 简单生存（行级）",
        "generated": "2026-11-04",
        "id_label": "节点ID",
        "hide_media": True,
        "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "潜能"], ["race_name", "种族"],
                         ["level", "潜能等级"], ["effect_desc", "效果"]],
        "field_labels": {"item_id": "节点ID", "race_name": "种族",
                         "level": "潜能等级", "node_score": "节点分值",
                         "effect_desc": "效果", "tier": "档位",
                         "server_branches": "服型", "fields_note": "字段说明"},
        "filters": [{"key": "race_name", "label": "种族"},
                    {"key": "tier", "label": "档位"}],
        "race_rule": ("种族按用户口径：现行为械骨人（race=4）与半感染者（race=3，旧称再生者）、"
                      "人类（race=2）；不存在「通用」种族。"),
        "state_summary": {"条目": len(items)},
        "notes": ("行级来源：PE 活树 gene_node_data.nxs（经典服，141 行全解）+ "
                  "oversea gene_node_data kj1（简单生存，63 行全解）。"
                  "两服同 key 不同节点（63 个 key 里 41 个名字不同），故只按 (race, name) 对齐，"
                  "简单生存独有节点 id 用 gene_kj1_ 前缀。"
                  "档位取自节点名前缀（初级/中级/高级/特级/超级/究级），无前缀的特殊节点记为「特殊」。"
                  "两服同名节点分值不完全一致：初级档 经典服 300 / 简单生存 400（16 条），"
                  "本板 node_score 统一取经典服，另一侧写在 node_score_branches。"),
        "dropped_common_rows": dropped_common,
        "dropped_common_note": (f"经典服表里 race=1「通用（无种族专属）」{dropped_common} 条，"
                                "沿用旧板口径不入板面（数据仍在 PE 表 gene_node_data.nxs 内）。"),
        "server_note": (f"经典服 {sum(1 for it in items if '经典服' in it['server_branches'])} 条 / "
                        f"简单生存 {sum(1 for it in items if '简单生存' in it['server_branches'])} 条 "
                        f"（其中简单生存独有 {kj1_only} 条）。"
                        "旧板 56 条「池名册级」条目本次全部升级为行级字段。"),
        "source_label": SOURCE_LABEL,
        "package_sha": base_ev["sha256"],
        "provenance": {
            "contract_version": 3,
            "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": [{
                "source_id": SOURCE_ID,
                "role": "primary",
                "path": str(PE_CDATA / BASE_TABLE).replace("\\", "/"),
                "sha256": base_ev["sha256"],
                "bytes": (PE_CDATA / BASE_TABLE).stat().st_size,
                "mtime_ns": (PE_CDATA / BASE_TABLE).stat().st_mtime_ns,
            }, {
                "source_id": SOURCE_ID,
                "role": "pool",
                "path": str(PE_CDATA / BASE_POOL).replace("\\", "/"),
                "sha256": _sha256(PE_CDATA / BASE_POOL),
                "bytes": (PE_CDATA / BASE_POOL).stat().st_size,
                "mtime_ns": (PE_CDATA / BASE_POOL).stat().st_mtime_ns,
            }, {
                "source_id": SOURCE_ID,
                "role": "server-branch(简单生存)",
                "path": str(PE_CDATA / KJ1_TABLE).replace("\\", "/"),
                "sha256": kj1_ev["sha256"],
                "bytes": (PE_CDATA / KJ1_TABLE).stat().st_size,
                "mtime_ns": (PE_CDATA / KJ1_TABLE).stat().st_mtime_ns,
            }],
            "source_scope": {
                "cross_source_policy": "no-cross-source-field-join",
                "integer_join_policy": "no-equal-integer-join",
                "runtime_final_policy": "unknown-unless-runtime-proven",
            },
            "decode": {
                "kind": "legacy-x-container + 0x76 index-tail",
                "evidence": {"base": base_ev, "kj1": kj1_ev},
                "cross_server_join": "race+node_name（不按 key）",
            },
        },
        "evidence_chain": {
            "base": base_ev,
            "kj1": kj1_ev,
            "tier_counts": dict(sorted(tier_counter.items())),
            "race_counts": dict(sorted(race_counter.items())),
        },
    }

    # ★ 不做 provenance 常量上提：`provenance_defaults._shape_signature()` 用的是
    #   「STABLE_KEYS 键集合」的哈希，本板两种来源（经典服 / 简单生存）键集合完全相同
    #   ⇒ 会塌成同一形态，而两形态的 table / sha256 取值不同 ⇒ 一个字段都上提不了，
    #   只会留下一个空的 provenance_defaults。逐条写全更简单也更诚实（133 条，代价可忽略）。
    return {"meta": meta, "periods": [], "items": items}


def main() -> int:
    before = 0
    if BOARD.exists():
        try:
            before = len(json.loads(BOARD.read_text(encoding="utf-8")).get("items") or [])
        except Exception:
            before = 0
    board = build()
    after = len(board["items"])
    if after < max(before, 104):
        raise SystemExit(f"条目数回退：{before} → {after}，拒绝写板")
    write_board_pair(BOARD, board)
    m = board["meta"]
    print(f"written {BOARD} items={after} (before {before})")
    print(f"  base={m['evidence_chain']['base']['row_count']} 行 / "
          f"kj1={m['evidence_chain']['kj1']['row_count']} 行")
    print(f"  tier={m['evidence_chain']['tier_counts']}")
    print(f"  race={m['evidence_chain']['race_counts']}")
    print(f"  dropped_common={m['dropped_common_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
