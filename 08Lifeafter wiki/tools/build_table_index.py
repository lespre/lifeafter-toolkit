# -*- coding: utf-8 -*-
"""P1-10：table_index 构建器 —— 从 BA8 全量条目找"配置表"（纯定位，无字段语义）。

来源（复用既有产物，不重扫原包）：
- BA8 工作副本 entries/（25,485 已解码条目文件，test Documents/script.py314.lc.npk 的快照）
- P1-9 id_locator（live 同 fid 传播命名）

每条目提取：
- co_filename：条目内嵌字面 `com\\cdata\\<X>.py`（后 16B 内邻接 <module>）=自身模块路径
- refs：其他 cdata 路径字面（引用关系，不解释含义）
- table_body：合法 x{ 容器（count+reserved=0）存在=数据体表候选
- merge_shell：MergedTableData/SplitTableData 字面（合并/拆分壳代码，1765 类先例）

角色（纯字符串后缀规则，非语义）：
  co_filename basename 尾 {_base,_chs,_inc,_del,_merged} → role 同名；否则 plain
  family = basename 去 role 后缀；x{ 与 role/后缀组合成表族视图。

输出：data/table_index_entries.jsonl（entry 级）+ data/table_index.json（表族聚合/统计）
  + data/table_families.json（族级：成员与 role 分布）。live 命名=fid 传播（evidence=fid-shared）。
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
DB = ROOT / "data" / "id_locator_index.db"
OUT_ENTRIES = ROOT / "data" / "table_index_entries.jsonl"
OUT_INDEX = ROOT / "data" / "table_index.json"
OUT_FAMILIES = ROOT / "data" / "table_families.json"

CDATA = b"com" + bytes([92]) + b"cdata" + bytes([92])
MODULE_TAG = b"<module>"
XOPEN = b"x{"
ROLE_SUFFIXES = ("_base", "_chs", "_inc", "_del", "_merged")

_PATH_RE = re.compile(
    rb"com\\cdata\\[A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)*\.py")
# 但 regex 反斜杠——用手写字节扫描避免转义问题：
def find_cdata_paths(data: bytes) -> list[str]:
    out = []
    start = 0
    while True:
        i = data.find(CDATA, start)
        if i < 0:
            break
        j = i
        while j < len(data) and (data[j:j + 1].isalnum()
                                 or data[j:j + 1] in (b"\\", b"_", b".")):
            j += 1
        # 只收以 .py 结尾的完整路径段
        chunk = data[i:j]
        if chunk.endswith(b".py") and len(chunk) < 200:
            try:
                out.append(chunk.decode("utf-8"))
            except UnicodeDecodeError:
                pass
        start = j if j > i else i + 1
    return out


def has_x_container(data: bytes) -> bool:
    pos = 0
    while True:
        at = data.find(XOPEN, pos)
        if at < 0:
            return False
        if at + 18 <= len(data):
            blen, cnt, res = (int.from_bytes(data[at + 2:at + 6], "little"),
                              int.from_bytes(data[at + 6:at + 10], "little"),
                              int.from_bytes(data[at + 10:at + 14], "little"))
            if res == 0 and 0 < cnt < 2_000_000 and blen <= len(data):
                return True
        pos = at + 2


def role_of(basename: str) -> tuple[str, str]:
    """(family, role) 纯后缀规则；_base_chs/_data_chs 等多后缀循环剥离。"""
    stem = basename[:-3] if basename.endswith(".py") else basename
    roles = []
    changed = True
    while changed:
        changed = False
        for suf in ROLE_SUFFIXES:
            if stem.endswith(suf):
                roles.append(suf[1:])
                stem = stem[: -len(suf)]
                changed = True
                break
    if not roles:
        return stem, "plain"
    # chs 属配套层不算独立角色：主 role=最末剥离项
    return stem, roles[0]


def _process_entry(fn: str) -> dict:
    d = (ENTRIES_DIR / fn).read_bytes()
    paths = find_cdata_paths(d)
    co_name = None
    for p in paths:
        i = d.find(p.encode("utf-8"))
        j = i + len(p.encode("utf-8")) if i >= 0 else i
        if i >= 0 and MODULE_TAG in d[j:j + 40]:
            co_name = p
            break
    rec = {
        "entry": int(fn[:6]),
        "size": len(d),
        "co_filename": co_name,
        "path_refs": [p for p in paths if p != co_name],
        "table_body": has_x_container(d),
        "merge_shell": (b"MergedTableData" in d or b"SplitTableData" in d),
    }
    return rec


def main() -> int:
    started = time.time()
    files = sorted(f.name for f in ENTRIES_DIR.iterdir() if f.suffix == ".bin")
    assert len(files) == 25485, f"expected 25485, got {len(files)}"
    workers = min(12, (os.cpu_count() or 4))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(_process_entry, files, chunksize=64))
    recs.sort(key=lambda r: r["entry"])

    # 命名与族聚合（test=BA8）
    named = 0
    xbodies = 0
    families: dict[str, dict] = {}
    rows = []
    for r in recs:
        row = {
            "client_channel": "test",
            "package": "Documents/script.py314.lc.npk",
            "entry": r["entry"],
            "table_name": None,
            "family": None,
            "role": None,
            "evidence": "none",
            "table_body": r["table_body"],
            "merge_shell": r["merge_shell"],
            "size": r["size"],
        }
        if r["table_body"]:
            xbodies += 1
        if r["co_filename"]:
            row["table_name"] = r["co_filename"]
            fam, role = role_of(r["co_filename"].split("\\")[-1])
            row["family"] = fam
            row["role"] = role
            row["evidence"] = "co_filename"
            named += 1
            families.setdefault(fam, {"roles": Counter(), "members": []})
            families[fam]["roles"][role] += 1
            families[fam]["members"].append(r["entry"])
        elif r["merge_shell"]:
            # 合并/拆分壳：family=co 引用中的表族（含 _data 主名）——仅登记壳标志
            row["evidence"] = "merge_shell"
            for ref in r["path_refs"]:
                if ref.endswith("_data.py") or ref.endswith(".py"):
                    fam, _ = role_of(ref.split("\\")[-1])
                    row["family"] = fam
                    row["role"] = "merge_shell"
                    row["evidence"] = "merge_shell_ref"
                    families.setdefault(fam, {"roles": Counter(), "members": []})
                    families[fam]["roles"]["merge_shell"] += 1
                    families[fam]["members"].append(r["entry"])
                    break
        rows.append(row)

    # live 传播：同 fid 的 live 条目继承命名（evidence=fid-shared）
    con = sqlite3.connect(DB)
    ba8_fid = {}
    for r in con.execute(
            "SELECT entry_index, identifier FROM locations WHERE "
            "client_channel='test' AND identifier_type='fid' AND "
            "package='Documents/script.py314.lc.npk'"):
        ba8_fid[r[0]] = r[1]
    live_pkgs = ("Documents/script.py314.lc.npk", "Documents/script.py3.npk",
                 "Documents/script.npk", "script.py314.lc.npk", "script.npk")
    live_rows = con.execute(
        "SELECT entry_index, identifier, package FROM locations WHERE "
        "client_channel='live' AND identifier_type='fid' AND package IN "
        "('" + "','".join(live_pkgs) + "')").fetchall()
    fid2entry_test = {}
    for row in rows:
        e = row["entry"]
        if e in ba8_fid:
            fid2entry_test[ba8_fid[e]] = row
    live_named = 0
    for (eidx, fid, pkg) in live_rows:
        src = fid2entry_test.get(fid)
        if src and src.get("table_name"):
            rows.append({
                "client_channel": "live",
                "package": pkg,
                "entry": eidx,
                "table_name": src["table_name"],
                "family": src["family"],
                "role": src["role"],
                "evidence": "fid-shared",
                "table_body": src["table_body"],
                "merge_shell": src["merge_shell"],
                "size": None,
            })
            live_named += 1

    # 写 jsonl
    with OUT_ENTRIES.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    named_total = sum(1 for r in rows if r["table_name"])
    fam_summary = []
    for fam, info in families.items():
        fam_summary.append({
            "family": fam,
            "roles": dict(info["roles"]),
            "member_count": len(info["members"]),
            "member_entries": info["members"][:50],
        })
    fam_summary.sort(key=lambda x: -x["member_count"])
    index = {
        "schema_version": 1,
        "client_snapshot": {
            "test": "Documents/script.py314.lc.npk sha 328b8446891d6230106bf53541d8ea63"
                    "c0aeca8f3800398bf2d0763dbbcc55ad (workcopy config_work/"
                    "script_py314_docs_BA8A239A)",
            "live": "5 script 包 fid 传播（版本不同 sha79c0…等，无工作副本）",
        },
        "source": "BA8 工作副本 25485 entries + id_locator 传播",
        "total_entries": len(rows),
        "test_entries": 25485,
        "live_propagated_entries": live_named,
        "named_entries": named_total,
        "unnamed_entries": len(rows) - named_total,
        "table_body_entries": xbodies,
        "merge_shell_entries": sum(1 for r in recs if r["merge_shell"]),
        "named_by_kind": {
            "co_filename": sum(1 for r in rows if r["evidence"] == "co_filename"),
            "fid-shared": live_named,
            "merge_shell_ref": sum(1 for r in rows
                                   if r["evidence"] == "merge_shell_ref"),
        },
        "family_count": len(families),
        "families": fam_summary[:200],
        "note": "纯定位：表名=条目内嵌 co_filename 字面；table_body=x{ 容器结构；"
                "role=文件名后缀字符串规则；不解释字段语义，不猜测",
        "build_seconds": round(time.time() - started, 1),
    }
    # stats_v2：P1-10 双端/表体统计（从 rows 重算，含覆盖范围口径注）
    t_all = [r for r in rows if r["client_channel"] == "test"]
    l_all = [r for r in rows if r["client_channel"] == "live"]
    bodies = [r for r in t_all if r["table_body"]]
    b_named = [r for r in bodies if r["table_name"]]
    b_unnamed = [r for r in bodies if not r["table_name"]]
    t_fams = {r["family"] for r in t_all if r["family"]}
    l_fams = {r["family"] for r in l_all if r["family"]}
    stats_v2 = {
        "test_entries": len(t_all),
        "test_named": sum(1 for r in t_all if r["table_name"]),
        "config_table_bodies": len(bodies),
        "config_table_bodies_named": len(b_named),
        "config_table_bodies_unnamed": len(b_unnamed),
        "config_table_families": len({r["family"] for r in b_named if r["family"]}),
        "live_propagated": len(l_all),
        "family_shared": len(t_fams & l_fams),
        "family_test_only": len(t_fams - l_fams),
        "family_live_only": len(l_fams - t_fams),
        "scope_note": "family 级口径（table_index 覆盖范围内）：test=BA8 工作副本 25,485 条独立命名；"
                      "live=50,658 条 100% fid-shared 传播（live BA8 sha79c0…≠test，无独立命名源，未重扫原包）。"
                      "live-only=0 为结构性结果（live family 集恒为 test 子集），不代表 live 无独有表："
                      "live Documents/script 系共 170,177 个 fid 位置，其中 119,519 条不在 test BA8 fid 集="
                      "未命名未覆盖（unknown）。record 级口径：live 50,658 每条均有 test 同 fid 源。",
    }
    index["stats_v2"] = stats_v2
    OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    fams_out = {"families": fam_summary, "count": len(fam_summary)}
    OUT_FAMILIES.write_text(json.dumps(fams_out, ensure_ascii=False, indent=1),
                            encoding="utf-8")
    print(f"test 25,485 | named(co_filename) {sum(1 for r in rows if r['evidence']=='co_filename')} "
          f"| table_body {xbodies} | merge_shell {sum(1 for r in recs if r['merge_shell'])} "
          f"| families {len(families)}")
    print(f"live propagated named: {live_named}")
    print(f"total rows {len(rows)} named_total {named_total}")
    print(f"-> {OUT_INDEX.name} in {index['build_seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
