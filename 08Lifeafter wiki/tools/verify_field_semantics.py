# -*- coding: utf-8 -*-
"""P2-2：字段语义可信度验证（逐 (table, schema_ref, slot) 统计判据）。

判据（无单条值语义猜测，统计级+结构级）：
A. 名↔型一致性：字段名尾模式期望类型 vs 槽实际类型字节（结构事实）
   文本期望尾：_name/name_/_desc/_title/_icon/_path/_url/_pic/_img/_model/_sfx/_tip
   整数期望尾：_id/id_/_num/_count/_level/_type/_index
   矛盾=unsafe（漂移池/名字错位信号）
B. 文本槽内容模式（CHS）：值=池文本；槽主导模式 vs 名字类别：
   name/desc/title→期望 zh_normal 主导；icon/path/model/sfx→期望 pathlike 主导
   模式混杂/主导反转=unsafe（跨记录文本错位信号，decode_probe 宽表警示同源）
C. 历史实证（2026-09-01 日志用户确认）：all_equips_data 的 name/desc/icon 文本槽
   跨记录错位（194190 实例）→ 文本语义槽直接 unsafe；结构字段（数值/跳转）verified
   fashion_data 文本槽=轻史 suspect（统计正常则 likely）
D. unresolved：池未配对表槽 / 槽 oob / 无样本
状态=verified/likely/unsafe/unresolved；表状态=最差槽状态（unsafe>unresolved>likely>verified）。
输出：data/FIELD_RULES.json + field_semantics_summary.json
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
FNAMES = ROOT / "data" / "field_names.json"
OUT = ROOT / "data" / "FIELD_RULES.json"
OUT_SUM = ROOT / "data" / "field_semantics_summary.json"
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"

TEXT_TAILS = ("_name", "_desc", "_title", "_text", "_talk", "_tip",
              "_content", "_icon", "_icons", "_icon2", "_path", "_url",
              "_pic", "_img")
TEXT_HEADS = ("name", "desc", "icon", "title")
INT_TAILS = ("_id", "_num", "_count", "_level", "_type", "_index", "_cnt",
             "_time", "_day", "_rate", "_weight", "_price", "_num2", "_num3")
INT_HEADS = ("id", "num", "count", "level", "type", "index")
CHS = 0x05
HIST_UNSAFE = {"all_equips_data"}
HIST_SUSPECT = {"fashion_data", "simple_fashion_data"}
HIST_UNSAFE_SUFFIX = ("name", "desc", "icon", "icons", "icon2", "title",
                     "short_name", "desc2", "desc3")


def name_category(name: str) -> str:
    """名尾模式→预期类别：text/int/neutral（写死可审查规则，非语义猜值）。"""
    n = name.lower()
    for t in TEXT_TAILS:
        if n.endswith(t):
            return "text"
    for h in TEXT_HEADS:
        if n == h or n.startswith(h + "_"):
            return "text"
    for t in INT_TAILS:
        if n.endswith(t):
            return "int"
    for h in INT_HEADS:
        if n == h or n.startswith(h + "_"):
            return "int"
    return "neutral"


def text_mode(txt: str) -> str:
    if not txt:
        return "empty"
    try:
        has_cjk = any("\u4e00" <= ch <= "\u9fff" for ch in txt)
    except Exception:
        has_cjk = False
    pathlike = ("\\" in txt or "/" in txt or txt.lower().endswith((
        ".png", ".jpg", ".atlas", ".py", ".txt", ".prefab", ".anim")))
    if has_cjk and len(txt) < 60 and not pathlike:
        return "zh_normal"
    if pathlike:
        return "pathlike"
    if len(txt) > 80:
        return "ascii_long"
    return "other_short"


def main() -> int:
    t0 = time.time()
    sys.path[:0] = [TOOLKIT]
    doc = json.loads(FNAMES.read_text(encoding="utf-8"))
    entries = doc["schema_entries"]
    print(f"schema entries: {len(entries)}", flush=True)
    out_tables = []
    c_fields = Counter()
    c_tables = Counter()
    hist_unsafe_names = set()

    for te in entries:
        entry = te["entry"]
        if te.get("pool_unresolved"):
            n_unres = 0
            for sch in te["schemas"]:
                n_unres += sch.get("n_fields", 0)
            c_tables["unresolved"] += 1
            c_fields["unresolved"] += n_unres
            out_tables.append({"entry": entry, "table": te["table"],
                               "state": "unresolved", "pool_note":
                               te.get("pool_note"), "schemas": []})
            continue
        # 读表体（一次）
        fn = f"{entry:06d}.bin"
        data = (ENTRIES_DIR / fn).read_bytes()
        at = data.find(b"x{")
        xl = int.from_bytes(data[at + 2:at + 6], "little")
        body = data[at + 6:at + 6 + xl]
        cnt = int.from_bytes(body[0:4], "little")
        blob = body[8 + 4 * cnt:]
        # 池（字段名解析用同池=field_names 的 pool_entry 对应文件）
        # 这里直接复用 field_names.json 的字段名（已绑）——文本值模式需池文本：
        # 池文本=池文件 parse_legacy_chs_pool
        from toolkit_core.bindict_table import parse_legacy_chs_pool
        pe = te.get("pool_entry")
        pool = []
        if pe:
            pd = (ENTRIES_DIR / f"{pe:06d}.bin").read_bytes()
            try:
                pool = parse_legacy_chs_pool(pd)
            except Exception:
                pool = []
        # 逐 schema 逐槽：收集样本（值型统计）
        # 行遍历同 P1-13 定位（简单复用：index rows 采样前 N）
        from toolkit_core import bindict_table as bt
        try:
            idx = bt.parse_index(blob)
            known = bt._collect_schemas(blob, idx)
        except ValueError:
            known = set()
        schemas_out = []
        for sch_def in te["schemas"]:
            ref = sch_def["schema_ref"]
            if "error" in sch_def:
                # error schema=定义解析失败，槽数未知：不计入槽统计（与 P2-1 一致）
                schemas_out.append({**sch_def, "state": "unresolved"})
                continue
            if not sch_def.get("fields"):
                # 池缺表 schema：n_fields 已知（P2-1 写入）→ 计 unresolved
                n_f = sch_def.get("n_fields", 0)
                c_fields["unresolved"] += n_f
                schemas_out.append({**sch_def, "state": "unresolved"})
                continue
            fields = sch_def["fields"]
            # 槽级样本收集
            per_slot = defaultdict(lambda: {"types": Counter(),
                                            "texts": Counter(), "n": 0})
            n_rows = 0
            for key, s0 in idx[:2000]:  # 采样上限 2000 行
                if not (0 <= s0 < len(blob)):
                    continue
                m = blob[s0]
                if m not in (0x96, 0xD6, 0xC6):
                    continue
                try:
                    sr, q = bt.uleb(blob, s0 + 1, len(blob))
                except ValueError:
                    continue
                if sr != ref:
                    continue
                try:
                    bits, flds, _ = bt._schema_at(blob, ref, [])
                except ValueError:
                    continue
                q2 = q
                bm_size = (bits + 7) // 8
                if m == 0x96:
                    if q2 + bm_size > len(blob):
                        continue
                    bm = blob[q2:q2 + bm_size]
                    q2 += bm_size
                else:
                    try:
                        bref, q2 = bt.uleb(blob, q2, len(blob))
                    except ValueError:
                        continue
                    if bref + bm_size > len(blob):
                        continue
                    bm = blob[bref:bref + bm_size]
                for i, (_s2, tbyte, _n2) in enumerate(flds):
                    if i >= bits or (bm[i // 8] >> (i % 8)) & 1:
                        try:
                            v, q2 = bt._decode_value(blob, q2, tbyte, pool)
                        except ValueError:
                            break
                        ps = per_slot[i]
                        ps["types"][f"0x{tbyte:02x}"] += 1
                        if tbyte == CHS and isinstance(v, str) and not v.startswith("<"):
                            ps["texts"][text_mode(v)] += 1
                        ps["n"] += 1
                n_rows += 1
            # 状态判定
            for i, f in enumerate(fields):
                st = per_slot[i]
                name = f["name"]
                if not f.get("bound") or name is None:
                    c_fields["unresolved"] += 1
                    f["state"] = "unresolved"
                    continue
                cat = name_category(name)
                tbyte = f["type"]
                is_chs = tbyte == "0x05"
                family = te.get("family") or ""
                # C. 历史实证
                nl = name.lower()
                if family in HIST_UNSAFE and any(
                        nl == s or nl.endswith("_" + s)
                        for s in HIST_UNSAFE_SUFFIX):
                    f["state"] = "unsafe"
                    f["evidence"] = "hist-all_equips-name-desc-icon-cross-record"
                    hist_unsafe_names.add(name)
                    c_fields["unsafe"] += 1
                    continue
                # A. 名↔型矛盾
                if cat == "text" and not is_chs:
                    f["state"] = "unsafe"
                    f["evidence"] = "name-text-but-type-not-chs"
                    c_fields["unsafe"] += 1
                    continue
                if cat == "int" and is_chs:
                    f["state"] = "unsafe"
                    f["evidence"] = "name-int-but-type-chs"
                    c_fields["unsafe"] += 1
                    continue
                # B. 文本槽模式
                is_text_cat = cat == "text"
                if is_chs and is_text_cat and st["n"] > 0:
                    tm = st["texts"]
                    tot = sum(tm.values())
                    zh = tm.get("zh_normal", 0)
                    pl = tm.get("pathlike", 0)
                    mixed = (zh + pl) / tot if tot else 0
                    dom = "zh_normal" if zh >= pl else "pathlike"
                    expect_path = ("icon" in name.lower() or "path" in name.lower()
                                   or "model" in name.lower()
                                   or "sfx" in name.lower() or "pic" in name.lower()
                                   or "img" in name.lower() or "url" in name.lower())
                    if expect_path:
                        ok = pl / tot >= 0.8 if tot else False
                    else:
                        # name/desc 类：可读文本样（中文/短文本）占多数即可
                        texty = (zh + tm.get("other_short", 0)) / tot if tot else 0
                        ok = texty >= 0.8 if tot else False
                    if not ok and tot >= 5:
                        f["state"] = "unsafe"
                        f["evidence"] = (f"text-mode-mismatch dom={dom} "
                                         f"zh={zh}/{tot} path={pl}/{tot}")
                        c_fields["unsafe"] += 1
                        continue
                    if tot < 5:
                        f["state"] = "likely"
                        f["evidence"] = "few-samples"
                    elif family in HIST_SUSPECT:
                        f["state"] = "likely"
                        f["evidence"] = "hist-suspect-text-ok-stats"
                    else:
                        f["state"] = "verified"
                        f["evidence"] = f"text-mode-{dom}"
                    c_fields[f["state"]] += 1
                    continue
                # neutral 文本槽（无名字类别预期）：类型自证即可
                if is_chs and st["n"] > 0:
                    if family in HIST_SUSPECT:
                        f["state"] = "likely"
                        f["evidence"] = "hist-suspect-text-ok-stats"
                    else:
                        f["state"] = "verified"
                        f["evidence"] = "text-consistent"
                    c_fields[f["state"]] += 1
                    continue
                # 整数/其他槽：类型自证
                if st["n"] == 0:
                    f["state"] = "unresolved"
                    f["evidence"] = "no-samples"
                    c_fields["unresolved"] += 1
                    continue
                if family in HIST_UNSAFE:
                    f["state"] = "verified"
                    f["evidence"] = "hist-struct-field-trusted"
                elif cat == "int" or cat == "neutral":
                    f["state"] = "verified"
                    f["evidence"] = "int-slot-consistent"
                else:
                    f["state"] = "likely"
                    f["evidence"] = "other-type"
                c_fields[f["state"]] += 1
            states = [f.get("state", "unresolved") for f in fields]
            worst = "verified"
            for s in ("unsafe", "unresolved", "likely"):
                if s in states:
                    worst = s
                    break
            schemas_out.append({"schema_ref": ref, "state": worst,
                                "n_fields": len(fields), "fields": fields})
        tstates = [s.get("state") or "unresolved" for s in schemas_out]
        tw = "verified"
        for s in ("unsafe", "unresolved", "likely"):
            if s in tstates:
                tw = s
                break
        c_tables[tw] += 1
        out_tables.append({"entry": entry, "table": te["table"],
                           "family": te.get("family"),
                           "state": tw, "schemas": schemas_out})
    summary = {
        "field_states": dict(c_fields),
        "table_states": dict(c_tables),
        "hist_unsafe_names_hit": sorted(hist_unsafe_names)[:40],
        "note": "判据 A 名↔型 / B 文本槽模式（统计级≥5 样本）/ C 历史实证 all_equips "
                "name/desc/icon 错位（2026-09-01 日志）；表状态=最差槽状态；"
                "未根据单条值判语义",
        "build_seconds": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps({"tables": out_tables}, ensure_ascii=False),
                   encoding="utf-8")
    OUT_SUM.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
