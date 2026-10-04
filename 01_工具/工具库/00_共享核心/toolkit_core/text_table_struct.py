# -*- coding: utf-8 -*-
r"""text_table_struct —— 把【表结构解析】产物接进交付物 `02_文字表`。

背景（为什么要这个模块）
------------------------------------------------------------
`hotfix bundle` 原先交付的文字表只有**裸句子**：

    `变更文案_去重.txt` / `变更文案_分表.txt`
      —— 从 overlay 块解出来的 6,067 条中文串，**没有字段名、没有行 ID**
      —— 读的人无法回答「这句话属于哪个任务 / 哪个道具 / 哪一行」

而 `03_执行/30_分析/表结构解析_*/` 这套产物已经做到了**文案 → 字段 → 行 ID**：

    <root>/结构/<表>.rows.csv        每行一条记录；列 = 字段名；首列 row_key = 行 ID
    <root>/结构/<表>.structure.json  字段清单（名 / 类型 / 文本槽行数）
    <root>/结构2/<表>.rows.csv       同一查器的后续一轮（部分表字段解析更完整）
    <root>/产物/表文案归属.jsonl       {表, 行键, 字段, 文案, 位置} 逐条归属（含嵌套子行）

本模块把上面这些"搬运 + 归属"成一句一句带结构的文案：

    表名 \t 字段名 \t 行ID \t 文案

★ 铁律
  · 只做搬运：文案**原样**取出，不改写、不拼接、不编造。
  · 一张表只认一个来源（按优先级取第一个**有产出**的来源），避免同一句被重复登记。
  · 嵌套子行的字段名形如 `args.xxx`（沿用上游查器的命名），归属仍是**父行的行 ID**，
    `位置` 记为「嵌套子行」。
  · 任何一步失败都只降级、不抛：拿不到结构就返回空，调用方回退裸串版交付。
"""

from __future__ import annotations

import csv
import json
import os
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

# 行 ID 列名（首列）。`结构/` 与 `结构2/` 都用 row_key。
_ID_COLS = ("row_key", "行键", "rowid")
# CSV 里的非字段元数据列（不当文案扫）——row_key 之外的 start/marker/schema 是整数/十六进制，
# 天然不含中文，不必单独排除（万一某表真有同名字段是文案，排除反而丢内容）。
_SKIP_COLS = set(_ID_COLS) | {"start", "marker"}

# 结构解析产物所在的分析根（相对项目根）
_ANALYSIS_REL = ("03_执行", "30_分析")
_ROOT_GLOB = "表结构解析_*"
_CSV_SUBDIRS = ("结构", "结构2")          # 优先级：结构 → 结构2
_JSONL_REL = ("产物", "表文案归属.jsonl")


def has_cjk(s) -> bool:
    """是否含中日韩统一表意文字（= 本项目的「文案」判据，与 `_cn_strings` 同口径）。"""
    return isinstance(s, str) and any("\u4e00" <= c <= "\u9fff" for c in s)


def short_name(table: str) -> str:
    r"""`com\cdata\box_data_chs.py` → `box_data_chs.py`。"""
    return str(table).replace("\\", "/").rstrip("/").split("/")[-1]


# ══════════════════════════════════════════════════════════════════
# 来源发现
# ══════════════════════════════════════════════════════════════════
def _project_root() -> Path:
    try:
        from toolkit_core.paths import PROJECT_ROOT          # noqa: PLC0415
        return Path(PROJECT_ROOT)
    except Exception:                                        # noqa: BLE001
        return Path(__file__).resolve().parents[3]


def discover_roots(analysis_root=None, struct_src=None) -> List[Path]:
    r"""找出所有「表结构解析」产物根，**按可用表数排序**（好的在前）。

    struct_src 给了就用它（目录或 `表文案归属.jsonl` 文件；可给多个，逗号分隔）。
    """
    out: List[Path] = []
    for s in ([struct_src] if isinstance(struct_src, (str, Path)) else list(struct_src or [])):
        p = Path(str(s))
        if p.is_file() and p.name.endswith(".jsonl"):
            p = p.parent.parent
        if p.is_dir():
            out.append(p)
    if not out:
        base = Path(analysis_root) if analysis_root else (_project_root().joinpath(*_ANALYSIS_REL))
        if base.is_dir():
            cands = [d for d in sorted(base.glob(_ROOT_GLOB)) if d.is_dir()]
            # 按「csv/ 目录里的行数文件数」倒序 —— 覆盖表多的优先
            def score(d: Path) -> Tuple[int, float]:
                n = 0
                for sub in _CSV_SUBDIRS:
                    n = max(n, len(list((d / sub).glob("*.rows.csv"))))
                return (n, (d / _JSONL_REL[0]).stat().st_mtime if (d / _JSONL_REL[0]).exists() else 0)
            out = sorted(cands, key=score, reverse=True)
    return out


def _csv_dir(root: Path) -> Optional[Path]:
    for sub in _CSV_SUBDIRS:
        d = root / sub
        if d.is_dir():
            return d
    return None


def _jsonl_path(root: Path) -> Optional[Path]:
    p = root.joinpath(_JSONL_REL[0], _JSONL_REL[1])
    return p if p.is_file() else None


# ══════════════════════════════════════════════════════════════════
# 单表读取
# ══════════════════════════════════════════════════════════════════
def _read_rows_csv(path: Path) -> Tuple[List[dict], int, List[str]]:
    """读一个 `<表>.rows.csv` → (文案条目, 行数, 字段名列表)。

    条目 = {"字段", "行ID", "文案", "位置"}；位置 = 行 / 嵌套子行。
    """
    items: List[dict] = []
    fields: List[str] = []
    nrow = 0
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        hdr = [c for c in (rd.fieldnames or []) if c]
        if not hdr:
            return [], 0, []
        id_col = next((c for c in hdr if c.lower() in _ID_COLS), hdr[0])
        fields = [c for c in hdr if c != id_col and c not in _SKIP_COLS]
        for rec in rd:
            nrow += 1
            rid = rec.get(id_col)
            rid = "" if rid is None else str(rid).strip()
            for k in fields:
                v = rec.get(k)
                if has_cjk(v):
                    items.append({"字段": k, "行ID": rid, "文案": v,
                                  "位置": "嵌套子行" if k.startswith("args.") else "行"})
    return items, nrow, fields


def _read_jsonl_tables(path: Path) -> Dict[str, List[dict]]:
    """读归属 jsonl 一次，按表分组（表 → 条目）。"""
    by: Dict[str, List[dict]] = {}
    for line in path.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        t = str(d.get("表") or "")
        if not t:
            continue
        by.setdefault(t, []).append({"字段": str(d.get("字段") or ""),
                                     "行ID": "" if d.get("行键") is None else str(d.get("行键")),
                                     "文案": d.get("文案") or "",
                                     "位置": d.get("位置") or "行"})
    return by


# ══════════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════════
def load(hot_tables: Sequence[str], *, analysis_root=None, struct_src=None,
         fallback_jsonl=True) -> Tuple[List[dict], dict]:
    r"""把本次热更涉及的表展开成结构化文案。

    参数
      hot_tables     `_chs.py` 表名列表（形如 `com\cdata\box_data_chs.py`，取自表名清单）
    返回
      (entries, meta)
        entries = [{"表": 完整表名, "表文件": 短名, "字段": …, "行ID": …, "文案": …, "位置": …,
                    "来源": 来源说明}, …]   —— 顺序 = 清单顺序 → 行顺序 → 字段顺序
        meta    = {来源根, 已覆盖表数, 无结构表, 每表来源/条数/行数, 字段分布, 位置分布}

    ★ 一张表只取一个来源：`结构/<表>.rows.csv` → `结构2/<表>.rows.csv` → `表文案归属.jsonl`。
      第一个**解出至少一条中文**的来源胜出（前面来源字段名没解出来时自动往下走）。
    """
    roots = discover_roots(analysis_root, struct_src)
    hot = [t for t in (hot_tables or []) if t]
    entries: List[dict] = []
    per_table: "OrderedDict[str, dict]" = OrderedDict()
    no_struct: List[str] = []
    jsonl_by: Dict[str, List[dict]] = {}
    jsonl_used_from: Optional[Path] = None
    seen: set = set()
    cand_cache: Dict[Path, Tuple[List[dict], int, List[str]]] = {}

    def _csv_cand(f: Path):
        if f not in cand_cache:
            try:
                cand_cache[f] = _read_rows_csv(f)
            except (OSError, UnicodeDecodeError, csv.Error):
                cand_cache[f] = ([], 0, [])
        return cand_cache[f]

    for full in hot:
        short = short_name(full)
        # 收集该表的所有候选来源（结构 → 结构2 → 归属jsonl），按顺序
        cands: List[dict] = []
        for root in roots:
            d = _csv_dir(root)
            if d is None:
                continue
            for sub in _CSV_SUBDIRS:
                f = root / sub / (short + ".rows.csv")
                if not f.is_file():
                    continue
                items, nrow, fields = _csv_cand(f)
                tag = "%s/%s" % (sub, short + ".rows.csv")
                cands.append({"来源": tag, "根": str(root), "items": items,
                              "行数": nrow, "字段数": len(fields), "文件": str(f)})
            break                     # 一个根只认它自己的 csv 目录层（结构 或 结构2）
        for root in roots:
            if not fallback_jsonl:
                break
            jp = _jsonl_path(root)
            if jp is None:
                continue
            if jsonl_used_from != jp:
                try:
                    jsonl_by = _read_jsonl_tables(jp)
                except (OSError, UnicodeDecodeError):
                    jsonl_by = {}
                jsonl_used_from = jp
            items = jsonl_by.get(short) or []
            if items:
                cands.append({"来源": "归属jsonl:" + jp.name, "根": str(root),
                              "items": items, "行数": None, "字段数": None, "文件": str(jp)})
        cand: dict = {}
        # ★ 取「解出中文最多」的来源：条数多的覆盖更全（新一版查器可能多解出字段）；
        #   条数相同按候选顺序（结构 → 结构2 → jsonl）取先到的，保证确定性。
        picked = None
        best = -1
        for i, c in enumerate(cands):
            cand[c["来源"].split(":")[0]] = len(c["items"])
            if len(c["items"]) > best:
                best, picked = len(c["items"]), c
        if picked is not None and not picked["items"]:
            picked = None
        if picked is None:
            no_struct.append(short)
            per_table[short] = {"表": full, "条数": 0, "行数": None, "来源": "",
                                "候选来源条数": cand,
                                "状态": "无结构产物（保持裸串版）"}
            continue
        n = 0
        for it in picked["items"]:
            txt = it.get("文案")
            if not has_cjk(txt):
                continue
            key = (full, it.get("字段", ""), it.get("行ID", ""), txt)
            if key in seen:
                continue
            seen.add(key)
            entries.append({"表": full, "表文件": short, "字段": it.get("字段", ""),
                            "行ID": it.get("行ID", ""), "文案": txt,
                            "位置": it.get("位置") or "行", "来源": picked["来源"]})
            n += 1
        per_table[short] = {"表": full, "条数": n, "行数": picked["行数"],
                            "字段数": picked["字段数"], "来源": picked["来源"],
                            "候选来源条数": cand,
                            "状态": "结构化" if n else "有产物但无中文（保持裸串版）"}

    meta = {
        "来源根": [str(r) for r in roots],
        "本次表数": len(hot),
        "已覆盖表数": sum(1 for v in per_table.values() if v["条数"]),
        "无结构产物表": no_struct,
        "每表": per_table,
        "字段分布": dict(Counter(e["字段"] for e in entries).most_common()),
        "位置分布": dict(Counter(e["位置"] for e in entries)),
        "来源分布": dict(Counter(v["来源"].split(":")[0] for v in per_table.values() if v["来源"])),
    }
    return entries, meta


# ══════════════════════════════════════════════════════════════════
# 落盘
# ══════════════════════════════════════════════════════════════════
TSV_NAME = "变更文案_结构化.tsv"
IDX_NAME = "变更文案_结构化_索引.json"
TSV_HEADER = ("表名", "字段名", "行ID", "文案")


def write(out_dir, entries: List[dict], meta: dict, *,
          bare_strings: Optional[Iterable[str]] = None, hot_tables=None) -> dict:
    r"""写 `变更文案_结构化.tsv` + `变更文案_结构化_索引.json`。

    bare_strings 给了就顺带算「与裸串版（变更文案_去重.txt）的交集」——回答
    「本次变更的那几千句里，有多少句拿到了结构」。返回写出的路径与统计。
    """
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    tsv = d / TSV_NAME
    with tsv.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(TSV_HEADER) + "\n")
        for e in entries:
            fh.write("%s\t%s\t%s\t%s\n" % (e["表"], e["字段"], e["行ID"],
                                           str(e["文案"]).replace("\t", " ")))
    uniq_txt = len({e["文案"] for e in entries})
    hit_n = miss_n = 0
    miss_samples: List[str] = []
    if bare_strings is not None:
        have = {e["文案"] for e in entries}
        for s in bare_strings:
            if not has_cjk(s):
                continue
            if s in have:
                hit_n += 1
            else:
                miss_n += 1
                if len(miss_samples) < 30:
                    miss_samples.append(s)
    idx = {
        "schema": "lifeafter-text-struct-v1",
        "生成时间": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "用途": "本次热更涉及文字表的【结构化文案】：每句都带 表名 + 字段名 + 行ID，"
                "不再是裸句子。裸串版（%s / 变更文案_分表.txt）同时保留。" % "变更文案_去重.txt",
        "文件": {
            TSV_NAME: {"列": list(TSV_HEADER), "首行表头": True, "分隔符": "\\t",
                       "编码": "utf-8", "数据行数": len(entries)},
            IDX_NAME: "本文件（索引）",
        },
        "统计": {
            "条数": len(entries),
            "去重文案": uniq_txt,
            "表数": len({e["表文件"] for e in entries}),
            "本次表数": meta.get("本次表数"),
            "已覆盖表数": meta.get("已覆盖表数"),
            "行级条数（含嵌套）": dict(meta.get("位置分布") or {}),
        },
        "与裸串版交集": {
            "裸串条数": (hit_n + miss_n) if bare_strings is not None else None,
            "命中结构化": hit_n,
            "未命中": miss_n,
            "未命中样例": miss_samples,
        },
        "来源": {
            "来源根": meta.get("来源根"),
            "来源分布（表数）": meta.get("来源分布"),
            "优先级": "结构/<表>.rows.csv → 结构2/<表>.rows.csv → 产物/表文案归属.jsonl",
        },
        "每表": meta.get("每表"),
        "字段分布Top50": dict(list((meta.get("字段分布") or {}).items())[:50]),
        "无结构产物表": meta.get("无结构产物表"),
    }
    ip = d / IDX_NAME
    ip.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"tsv": tsv, "index": ip, "n": len(entries), "n_unique": uniq_txt,
            "n_tables": idx["统计"]["表数"], "hit": hit_n, "miss": miss_n,
            "meta": meta}
