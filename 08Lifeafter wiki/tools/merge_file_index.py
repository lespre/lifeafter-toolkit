# -*- coding: utf-8 -*-
"""P1-8 Stage 4：统一 file_index 合并器（由各格式 summary 驱动）。

- file_index.json：目录/统计/来源引用/字段说明/未覆盖清单
- file_index_entries.jsonl：统一字段
  client_channel/source_id/package/package_sha/kind/entry_index/
  file_id(16hex, npk)|c1c2(gpk)|hash16(idx)|frame_offset(fpk)/
  offset/packed_size/decoded_size/flag|storage/name_known
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
PKG = ROOT / "data" / "audit" / "package_indexes"
OUT_INDEX = ROOT / "data" / "file_index.json"
OUT_ENTRIES = ROOT / "data" / "file_index_entries.jsonl"


def load_summary(name: str) -> dict:
    return json.loads((PKG / name).read_text(encoding="utf-8"))


def main() -> int:
    summaries = {
        # script 11 包已含在 npk summary（kind=容器(script)），不重复遍历
        "npk": load_summary("npk_index_summary.json"),
        "gpk": load_summary("gpk_index_summary.json"),
        "fpk": load_summary("fpk_index_summary.json"),
        "idx": load_summary("wpk_idx_index_summary.json"),
    }
    stats = {"sources": 0, "entries": 0, "by_kind": Counter(), "by_client": Counter()}
    covered = []  # (kind, client, path)
    failures = []
    with OUT_ENTRIES.open("w", encoding="utf-8", newline="\n") as out:
        for kind, summary in summaries.items():
            pkg_list = summary.get("packages") or summary.get("idx_packages") or []
            for p in pkg_list:
                if p.get("status") != "indexed":
                    failures.append({kind: p.get("status")})
                    continue
                client = p["client_channel"]
                path = p["path"]
                kind_field = p.get("kind", kind)  # npk summary 内 script 包标 容器(script)
                ef_rel = (p.get("entries_file") or p.get("frames_file")
                          or p.get("records_file"))
                if not ef_rel:
                    failures.append({kind: "no file field for " + path})
                    continue
                ef = ROOT / ef_rel
                stats["sources"] += 1
                stats["by_kind"][kind_field] += 1
                stats["by_client"][client] += 1
                covered.append((kind_field, client, path))
                # 单行条目统一化（kind 字段用包级 kind_field）
                for ln in ef.read_text(encoding="utf-8").splitlines():
                    if not ln.strip():
                        continue
                    e = json.loads(ln)
                    if kind in ("npk",):
                        row = {
                            "kind": kind_field, "client_channel": client,
                            "package": path, "entry_index": e["entry_index"],
                            "file_id": e["file_id"], "offset": e["offset"],
                            "packed_size": e["packed_size"],
                            "decoded_size": e["declared_size"],
                            "flag": e["flag"], "name_known": False,
                        }
                    elif kind == "gpk":
                        row = {
                            "kind": kind_field, "client_channel": client,
                            "package": path, "entry_index": e["entry_index"],
                            "c1": e["c1"], "c2": e["c2"],
                            "offset": e["offset"], "packed_size": e["packed_size"],
                            "decoded_size": e["decoded_size"],
                            "flag": e["flag"], "name_known": False,
                        }
                    elif kind == "fpk":
                        row = {
                            "kind": kind_field, "client_channel": client,
                            "package": path, "entry_index": e["frame_index"],
                            "frame_offset": e["offset"],
                            "packed_size": e["packed_size"],
                            "decoded_size": e["output_size"],
                            "output_magic": e["output_magic"],
                            "storage": e["storage"], "name_known": False,
                        }
                    elif kind == "idx":
                        row = {
                            "kind": kind_field, "client_channel": client,
                            "package": path, "entry_index": e["index"],
                            "hash16": e["hash"], "pkg": e["pkg"],
                            "offset": e["offset"], "packed_size": e["payload_size"],
                            "header_size": e["header_size"], "name_known": False,
                        }
                    else:
                        continue
                    out.write(json.dumps(row, ensure_ascii=False) + "\n")
                    stats["entries"] += 1

    by_kind_total = Counter()
    for kind, summary in summaries.items():
        pkg_list = summary.get("packages") or summary.get("idx_packages") or []
        for p in pkg_list:
            if p.get("status") == "indexed":
                by_kind_total[kind] += p.get("entry_count", p.get("record_count", p.get("frame_count", 0)))
    index = {
        "schema_version": 1,
        "name": "unified file_index（P1-8 Stage 4）",
        "scope": "条目级：双端 script/npk/gpk/fpk/idx 容器",
        "server_branch_policy": "unresolved",
        "note": "仅回答'哪个包有什么条目/offset/size/hash'；不含字段语义、业务关联、名称猜测",
        "stats": {
            "entry_sources": stats["sources"],
            "entries_written": stats["entries"],
            "declared_entries_by_kind": dict(by_kind_total),
            "by_client": dict(stats["by_client"]),
        },
        "field_notes": {
            "npk/script": "file_id=NPK 目录表 16 位 hex；flag 0=stored 2=LZ4 12=zstd",
            "gpk": "c1/c2=内容指纹（条目匿名，无路径信息）；flag 同 npk；offset 指向 o+36 数据体",
            "fpk": "frame_offset=zstd 帧起始；storage zstd|raw；output_magic=内容头判别",
            "idx": "hash16=解压内容 MD5（1DPW 已验证）；pkg=分卷号(255=旁侧散装)；实体在 wpk 内 offset+payload",
        },
        "files": {
            "entries": str(OUT_ENTRIES.relative_to(ROOT)),
            "sources": {
                "script": "data/audit/package_indexes/script_package_index_summary.json",
                "npk": "data/audit/package_indexes/npk_index_summary.json",
                "gpk": "data/audit/package_indexes/gpk_index_summary.json",
                "fpk": "data/audit/package_indexes/fpk_index_summary.json",
                "idx": "data/audit/package_indexes/wpk_idx_index_summary.json",
            },
        },
    }
    OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    print(json.dumps(index["stats"], ensure_ascii=False, indent=1))
    print("failures:", len(failures))
    print("file_index ->", OUT_INDEX)
    return 0


if __name__ == "__main__":
    sys.exit(main())
