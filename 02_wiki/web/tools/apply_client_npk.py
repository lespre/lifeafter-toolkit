#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把客户端当前 script npk 合并进还原树（按 fid→路径，不依赖 sqlite 索引）。

为什么不用 hotfix apply：apply 走 10_索引/indexes/lifeafter_files.sqlite3 的行偏移，
那是为旧包建的；换了 11-03 的新包后偏移全错，解码会大面积失败/出垃圾。
npk_reader 能直接解析这个包的条目表，用它的 file_id 去名字字典反查路径最稳。

用法：
  python apply_client_npk.py --dry      # 只统计
  python apply_client_npk.py --apply    # 真写
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
import npk_reader as NR  # noqa: E402

NPK = PROJ / "90_临时/pe_client/Documents/script.py314.lc.npk"
TREE = PROJ / "01_索引与产物/41_还原树/pe"
PREFIX = "配置"
NAMES = PROJ / "01_索引与产物/10_索引/names/names_dict_v18_apk_selfboot.json"
OUT = PROJ / "01_索引与产物/30_分析/客户端npk合并"


def find_names() -> dict:
    # ★ 必须用 v18（1.65M 条，覆盖客户端脚本包），v2 只有 426k 条、只能对上 336 个
    for p in (NAMES, *sorted((PROJ / "01_索引与产物/10_索引/names").glob("names_dict*.json"), reverse=True)):
        if p.is_file():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(d, dict) and len(d) > 1000:
                    print("名字字典：", p.name, len(d))
                    return d
            except Exception:
                continue
    raise SystemExit("找不到名字字典")


def main() -> int:
    apply = "--apply" in sys.argv
    names = find_names()
    stats = {"scanned": 0, "named": 0, "added": 0, "updated": 0, "same": 0,
             "failed": 0, "skipped_nostruct": 0, "no_name": 0}
    samples: dict[str, list] = {"added": [], "updated": [], "failed": []}

    for e in NR.iter_entries(str(NPK)):
        stats["scanned"] += 1
        fid = (e.file_id_hex or "").upper()
        path = names.get(fid) or names.get(fid.lower())
        if not path:
            stats["no_name"] += 1
            continue
        stats["named"] += 1
        rel = Path(PREFIX) / path.replace("/", "\\")
        dst = TREE / rel
        try:
            data = NR.read_entry(str(NPK), entry_index=e.entry_index)
        except Exception as exc:
            stats["failed"] += 1
            if len(samples["failed"]) < 20:
                samples["failed"].append(f"{rel} :: {type(exc).__name__}")
            continue
        if not data:
            stats["failed"] += 1
            continue
        # 守卫：脚本表（.py）解出来应该带 x{ 或 0x73 头；不带说明是差量块/解错
        if str(path).endswith(".py") and not (b"x{" in data[:4096] or data[:4] == b"s\x00\x00\x00" or b"SplitTableData" in data):
            low = data[:4].hex()
            if not (low.startswith("73") or b"x{" in data):
                stats["skipped_nostruct"] += 1
                continue
        if dst.is_file():
            old = dst.read_bytes()
            if old == data:
                stats["same"] += 1
                continue
            stats["updated"] += 1
            if len(samples["updated"]) < 20:
                samples["updated"].append(str(rel))
            if apply:
                bak = PROJ / "90_临时" / "tree_backup_20261104" / rel
                if not bak.is_file():
                    bak.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dst, bak)
                dst.write_bytes(data)
        else:
            stats["added"] += 1
            if len(samples["added"]) < 20:
                samples["added"].append(str(rel))
            if apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)

    ts = time.strftime("%Y%m%d_%H%M%S")
    OUT.mkdir(parents=True, exist_ok=True)
    rep = OUT / f"merge_{ts}{'' if apply else '_dryrun'}.json"
    rep.write_text(json.dumps({"apply": apply, "stats": stats, "samples": samples},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    for k, v in samples.items():
        if v:
            print(f"  {k} 例：", v[:3])
    print("报告 →", rep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
