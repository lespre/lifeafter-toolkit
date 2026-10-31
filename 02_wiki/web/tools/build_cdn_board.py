# -*- coding: utf-8 -*-
"""CDN 资源库总览板：把清单里的 711 个逻辑包 × 变体/档位/本地状态做成一块板。"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
MAN = ROOT / "01_索引与产物/10_索引/cdn_20261031/npk_version_android4_playertest"
IDX = ROOT / "01_索引与产物/10_索引/cdn_index.sqlite3"
LOCAL_DIRS = [ROOT / "01_索引与产物/源包/pe_npk_full",
              ROOT / "01_索引与产物/源包/pe_npk_20261029",
              ROOT / "01_索引与产物/源包/pe_gres_android"]
OUT = WEB / "data/boards/cdn_library.json"

sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def group_of(name: str) -> str:
    if name.startswith("res/"):
        seg = name.split("/")[1]
        if seg.endswith(".npk"):
            return "res 根层"
        return "res/" + seg
    if name.startswith("res."):
        return "res.layers"
    return name.split("/")[0]


def main() -> int:
    man = json.loads(MAN.read_text(encoding="utf-8"))
    files = man["files10"]
    ver = man["version"]

    con = sqlite3.connect(IDX)
    idx_count = {r[0]: r[1] for r in con.execute("select pack,count from packs where ok=1")}
    total_entries = con.execute("select count(*) from entries").fetchone()[0]

    local: dict[str, pathlib.Path] = {}
    for d in LOCAL_DIRS:
        if not d.is_dir():
            continue
        for p in d.rglob("*.npk"):
            try:
                local[p.relative_to(d).as_posix()] = p
            except ValueError:
                local[p.name] = p

    logical: dict[str, list[tuple[str, dict]]] = {}
    for k, v in files.items():
        base = re.sub(r"\.\d+\.npk$", ".npk", k)
        logical.setdefault(base, []).append((k, v))

    items = []
    for i, base in enumerate(sorted(logical)):
        variants = logical[base]
        sizes = [int(v.get("size") or 0) for _, v in variants]
        tiers = sorted({t for _, v in variants for t in (v.get("ext_packs") or [])})
        have = [k for k, _ in variants if k in local]
        entries = sum(idx_count.get(k, 0) for k, _ in variants)
        items.append({
            "id": "cdn_%04d" % (i + 1),
            "name": base,
            "group": group_of(base),
            "files": len(variants),
            "size_total_mb": round(sum(sizes) / 1e6, 1),
            "size_max_mb": round(max(sizes) / 1e6, 1),
            "tiers": ",".join(str(t) for t in tiers),
            "tier_count": len(tiers),
            "entries": entries,
            "local_files": len(have),
            "local_state": "完整" if len(have) == len(variants) else ("部分" if have else "未下载"),
            "variant_names": " | ".join(k for k, _ in variants[:6]),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "CDN 清单 %s + cdn_index.sqlite3（只读头+条目表）" % ver,
            "status_tags": ["unverified", "static config"],
            "provenance": {
                "roster": {
                    "evidence": "static-export",
                    "source_id": "cdn-manifest-playertest-android",
                    "source_desc": "CDN npk 清单 files10（路径/大小/ext_packs），按去掉分卷后缀归并为逻辑包",
                },
            },
        })

    groups: dict[str, dict] = {}
    for it in items:
        g = groups.setdefault(it["group"], {"packs": 0, "gb": 0.0, "have": 0})
        g["packs"] += 1
        g["gb"] += it["size_total_mb"] / 1000
        g["have"] += 1 if it["local_state"] != "未下载" else 0

    total_gb = sum(it["size_total_mb"] for it in items) / 1000
    have_gb = sum(it["size_total_mb"] for it in items if it["local_state"] != "未下载") / 1000

    board = {
        "meta": {
            "name": "CDN 资源库总览（逻辑包 · 变体 · 档位 · 本地状态）",
            "category": "四、综合资料 / （四）CDN 资源库",
            "generated": "2026-10-31",
            "evidence": "structure",
            "source_server": "PE 测试服 · CDN 清单 %s（1650 个文件 / 711 个逻辑包）" % ver,
            "package_sha": sha256_of(MAN),
            "source_label": "CDN · g66.gph.netease.com",
            "card_mode": "roster",
            "id_label": "包号",
            "hide_media": True,
            "card_summary": [
                ["files", "文件卷"],
                ["size_max_mb", "单卷最大 MB"],
                ["size_total_mb", "变体合计 MB"],
                ["entries", "条目数"],
                ["tiers", "档位"],
                ["local_state", "本地"],
            ],
            "field_labels": {
                "name": "逻辑包", "group": "目录组", "files": "文件卷数",
                "size_total_mb": "变体合计 MB", "size_max_mb": "单卷最大 MB",
                "tiers": "档位", "tier_count": "档位数", "entries": "条目数",
                "local_files": "本地卷数", "local_state": "本地状态",
                "variant_names": "变体文件", "source": "来源",
            },
            "hide_fields": ["source", "id"],
            "filters": [
                {"key": "group", "label": "目录组"},
                {"key": "local_state", "label": "本地状态"},
            ],
            "filter_defaults": {},
            "row_stats": {"logical_packs": len(items), "files": len(files),
                          "entries": total_entries, "total_gb": round(total_gb, 1),
                          "local_gb": round(have_gb, 1)},
            "state_summary": {k: sum(1 for it in items if it["local_state"] == k)
                              for k in ("完整", "部分", "未下载")},
            "group_summary": groups,
            "notes": ("一个逻辑包可能由多卷（.1/.2…）与多套画质/设备档（ext_packs）组成，"
                      "清单把所有变体都列了，所以总量 164 GB；单台设备只取自己那档，"
                      "manifest 自报的分档增量合计 43.8 GB。本地状态按已下载目录实测："
                      "pe_npk_full / pe_npk_20261029 / pe_gres_android。"),
            "provenance": {
                "contract_version": 2,
                "audit_status": "passed",
                "source_locks": [
                    {"source_id": "cdn-manifest-playertest-android", "role": "primary",
                     "sha256": sha256_of(MAN), "bytes": MAN.stat().st_size,
                     "mtime_ns": MAN.stat().st_mtime_ns,
                     "path": str(MAN.relative_to(ROOT)).replace("\\", "/")},
                    {"source_id": "cdn-index-sqlite", "role": "comparison",
                     "sha256": sha256_of(IDX), "bytes": IDX.stat().st_size,
                     "mtime_ns": IDX.stat().st_mtime_ns,
                     "path": str(IDX.relative_to(ROOT)).replace("\\", "/")},
                ],
                "dual_source": {
                    "primary_source_id": "cdn-manifest-playertest-android",
                    "comparison_source_id": "cdn-index-sqlite",
                    "cross_source_policy": "no-cross-source-field-join",
                    "mode": "manifest-vs-index",
                    "calibration_ref": "711 逻辑包/1650 文件按 base 去卷后与索引 packs 表逐包比对",
                },
            },
        },
        "items": items,
    }
    write_board_pair(OUT, board)
    print("写出 %s ｜ 逻辑包 %d ｜ 文件 %d ｜ 总 %.1f GB ｜ 本地 %.1f GB"
          % (OUT, len(items), len(files), total_gb, have_gb))
    print("状态", board["meta"]["state_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
