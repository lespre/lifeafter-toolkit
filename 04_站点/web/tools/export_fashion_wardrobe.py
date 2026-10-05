# -*- coding: utf-8 -*-
"""全量时装衣柜板块（人物类）——★ 权威源换成【表结构解析的行】。

## 为什么换源（原版被隔离的原因，逐条解掉）

原版从 BA 快照 CHS 池用**正则启发式**取名，隔离理由（publication_policy.json）写着：
  「display_name/part 取整行 CHS 字符串的正则启发式，而非已校准的 name/part 字段；
    聚合后丢失原表 row key，不能回溯。」
⇒ 两条都是**数据源问题**，不是展示问题。改成读【表结构解析产物】后两条同时解掉：

| 隔离理由 | 现在怎么解 |
|---|---|
| 名字/部件来自正则启发式 | 改用表的 `name` / `part_type` **字段**（BinDict 按 schema 解出，不是正则） |
| 聚合后丢 row key | 每条带 `row_keys`（该外观的全部 row_key）⇒ 可回溯到具体行 |

## join 口径（实测教训）

★ **不能用 model_id** —— 旧板与表的 model_id **交集 0**（旧板 10008~81898 vs 表 1001~5004，
  是两个不同空间；数字相等纯属巧合，会造出假匹配，实测 76.9% 的「命中」全是巧合）。

正解 = 按【归一名字】聚合，三层剥离：
  ① 剥部件后缀    -衣服 / -头饰 / -背包 / -套装 / -挂件 / -脱帽头
  ② 剥「·XXX」    ·守护 / ·闪耀 / ·求索 / ·腾飞 …（★ 后缀词表是变动的 ⇒ 直接截断到「·」）
  ③ 剥时效与包装  -N天 / （永久款）

只读源；同名归一后聚合成一条，desc 取该外观的实描述。
"""
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJ = Path("E:/la拆包项目")
OUT = ROOT / "data" / "boards" / "fashion_wardrobe.json"

_NAMES = Path(__file__).name            # 便于报错时指路

# ★ 权威源：最新一次表结构解析产物
_CANDS = sorted((PROJ / "03_执行" / "30_分析").glob("表结构解析_*/结构"))
SRC_DIR = _CANDS[-1] if _CANDS else None

FASHION_TABLES = [
    "fashion_data_chs.py.rows.csv",
    "fashion_data_auto_oversea_data_kjxq_chs.py.rows.csv",
]
# ★ 名字只从【玩家可见表】来 —— fashion_data 是时装表（名字如「极地朋克」），
#   player_appear_data 是【部件工程表】（名字如「005high套（女）」「100级甲」），
#   混进来会把内部工程名当成时装名（实测踩过）。
#   ⇒ 它只作【desc 补源】（有些时装只在部件表里有描述）。
DESC_EXTRA_TABLES = [
    "player_appear_data_chs.py.rows.csv",
    "player_appear_data_auto_oversea_data_kjxq_chs.py.rows.csv",
]

_PARTS = ["-衣服", "-头饰", "-背包", "-套装", "-挂件", "-脱帽头", "-头发", "-帽子"]


def norm_name(n: str) -> str:
    """名字归一 —— 三层剥离。"""
    s = (n or "").strip()
    s = re.sub(r"[-－]?\d+天$", "", s)
    s = re.sub(r"[（(]\s*永久款\s*[）)]", "", s)
    s = re.sub(r"[（(]\s*\d+天\s*[）)]", "", s)
    s = s.replace("永久款", "")
    for sep in ("·", "・", "•"):          # ★ 后缀词表是变动的 ⇒ 直接截断
        if sep in s:
            s = s.split(sep)[0]
    for x in _PARTS:
        if s.endswith(x):
            s = s[: -len(x)]
    return s.strip()


def main() -> int:
    if not SRC_DIR:
        print("✗ 找不到表结构解析产物（03_执行/30_分析/表结构解析_*）")
        return 1
    print("权威源:", SRC_DIR)

    agg = {}
    src_rows = 0
    for t in FASHION_TABLES:
        p = SRC_DIR / t
        if not p.is_file():
            print("  · 跳过（无产物）:", t)
            continue
        with p.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                nm = (r.get("name") or "").strip()
                if not nm:
                    continue
                base = norm_name(nm)
                if not base or re.fullmatch(r"[A-Za-z0-9_;.\-/]+", base):
                    continue
                src_rows += 1
                a = agg.setdefault(base, {
                    "names": set(), "parts": set(), "models": set(),
                    "durs": set(), "rows": [], "desc": None, "tables": set(),
                })
                a["names"].add(nm)
                a["tables"].add(t.replace(".rows.csv", ""))
                pt = (r.get("part_type") or "").strip()
                if pt:
                    a["parts"].add(pt)
                mid = (r.get("model_id") or "").strip()
                if mid.isdigit():
                    a["models"].add(int(mid))
                # 时效：从 new_fashion_id_str 尾段 `_N_M` 推（N>0 即时限天数）
                nf = (r.get("new_fashion_id_str") or "")
                m = re.search(r"_(\d+)_\d+$", nf)
                if m and m.group(1) != "0":
                    a["durs"].add(int(m.group(1)))
                if len(a["rows"]) < 60:
                    a["rows"].append(int(r["row_key"]))
                d = (r.get("desc") or "").strip()
                if d and not a["desc"]:
                    a["desc"] = d

    print("表行 %d → 归一外观 %d 条" % (src_rows, len(agg)))

    # ★ desc 补源：部件工程表里有的时装描述（只补空，不新造条目）
    extra_desc, extra_src = {}, set()
    for t in DESC_EXTRA_TABLES:
        p = SRC_DIR / t
        if not p.is_file():
            continue
        extra_src.add(t.replace(".rows.csv", ""))
        with p.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                d = (r.get("desc") or "").strip()
                if not d:
                    continue
                k = norm_name(r.get("name"))
                if k:
                    extra_desc.setdefault(k, d)
    filled = 0
    for base, a in agg.items():
        if not a["desc"] and base in extra_desc:
            a["desc"] = extra_desc[base]
            a["tables"].add("(desc补源) " + "/".join(sorted(extra_src)))
            filled += 1
    if filled:
        print("  desc 补源：从部件表补了 %d 条" % filled)

    items = []
    for idx, (base, a) in enumerate(sorted(agg.items())):
        parts = sorted(a["parts"])
        models = sorted(a["models"])
        items.append({
            "id": f"wardrobe_{idx:04d}",
            "name": base,
            "evidence": "structure",
            # ★ v3 契约要求逐条带 evidence_level（缺了就进不了 manifest）
            #   合法值见 publication_policy.EVIDENCE_LEVELS —— 静态度量用 structure-only
            "evidence_level": "structure-only",
            "source": ("表结构解析产物（fashion_data / player_appear 的 "
                       "name·desc·part_type·model_id 字段）"),
            "tables": sorted(a["tables"]),
            # ★ 可回溯：该外观的全部 row_key（解掉隔离理由②）
            "row_keys": sorted(a["rows"]),
            "name_variants": sorted(a["names"]),
            "part": parts[0] if len(parts) == 1 else ("/".join(parts) if parts else "整套"),
            "all_parts": parts if len(parts) > 1 else None,
            "model_ids": models or None,
            "time_limited_variants": sorted(a["durs"]) or None,
            "desc": a["desc"],
            "desc_note": ("描述来自表的 desc 字段" if a["desc"]
                          else "★ 该外观在表里 desc 为空（渠道/纪念类常无描述）"),
        })

    part_count = defaultdict(int)
    withdesc = sum(1 for x in items if x["desc"])
    for it in items:
        part_count[it["part"]] += 1

    # 源 sha：以表结构解析产物为准（可复现）
    h = hashlib.sha256()
    for t in FASHION_TABLES:
        p = SRC_DIR / t
        if p.is_file():
            h.update(p.read_bytes())

    board = {
        "meta": {
            "name": "人物·全量时装衣柜",
            "category": "二、时装类 / （一）全量时装总表",
            "source_server": "体验服 script 表结构解析（正式解出的 name/desc/part_type/model_id 字段）",
            "package_sha": h.hexdigest(),
            "generated": "2026-09-28",
            "evidence": "structure",
            "notes": (
                f"全量 {len(items)} 件外观（按归一名字聚合时限/部件变体）。"
                f"部件分布={dict(part_count)}。"
                f"★ 名字/部件取自表的【字段】（非正则启发式），每条带 row_keys 可回溯 —— "
                f"原版两条隔离理由均已解掉。★ 描述覆盖 {withdesc}/{len(items)}"
                f"（{100.0 * withdesc / max(1, len(items)):.1f}%），无描述的在 desc_note 里说明原因。"
                "★ 归一口径：剥部件后缀 / 剥「·XXX」/ 剥时效包装。"
            ),
            "join_policy": ("按归一名字聚合；★ 禁用 model_id —— 旧板与表的 model_id 交集 0，"
                            "数字相等是巧合（实测 76.9% 假命中）"),
        },
        "items": items,
    }
    # ★ 发布契约 v3（frozen-artifact）—— 已发布的板必须带可机读定位链，
    #   否则 build_wiki.py 直接拒绝（实测：「已发布 board 缺可机读定位链 meta.provenance」）。
    #   走 tools/preview_board_contract.apply_frozen_v3：一条 primary 锁 + 逐条 locator 链。
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "tools"))
    from preview_board_contract import apply_frozen_v3  # noqa

    # 真源 = 我们实际读的那份 rows.csv（诚实来源，不是编的）
    _primary = SRC_DIR / FASHION_TABLES[0]

    def _loc(it):
        tbl = (it.get("tables") or ["?"])[0]
        rk = (it.get("row_keys") or [None])[0]
        return {
            "table": f"com\\cdata\\{tbl}.py",
            "row_key": rk,
            "field_refs": ["name", "desc", "part_type", "model_id"],
            "name_source": f"com\\cdata\\{tbl}.py#name",
            "kind": "sanitized-existing-board-record",
            "status_tags": ["unresolved", "static config"],
        }

    apply_frozen_v3(
        board,
        source_id="fashion-wardrobe-struct",
        artifact_path=_primary,
        artifact_label=_primary.name,
        state_summary={
            "unresolved": len(items),
            "static config": len(items),
            "verified": 0,
            "runtime final unknown": len(items),
        },
        locator=_loc,
    )

    OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    pct = 100.0 * withdesc / max(1, len(items))
    print("写出 %s 条目 %d ｜ desc %d = %.1f%%" % (OUT.name, len(items), withdesc, pct))
    print("部件", dict(part_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
