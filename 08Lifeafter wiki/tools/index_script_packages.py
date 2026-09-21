# -*- coding: utf-8 -*-
"""P1-8a：script 家族 11 包条目级索引（目录表级，不解 payload）。

- 输入：data/source_registry.json kind=容器(script) 的 11 项
- 每包：LiveNpkReader 只读解析目录表 → entries.jsonl（entry_index/file_id/offset/
  packed_size/declared_size/c1/c2/flag）
- 校验：包 SHA 与 registry 一致；entry_count 与已知锚对照（BA8=25,373）
- 输出：data/audit/package_indexes/<client>_<pkg>.entries.jsonl + package_index_summary.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]

from live_npk_reader import LiveNpkReader, NpkFormatError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
OUT_DIR = ROOT / "data" / "audit" / "package_indexes"

# 已知锚：BA8 manifest header.entry_count（目录级，2026-09-07 实测 25,485；
# 日志 27.14 的"25,373"为旧口径，以 manifest 为准）
KNOWN_ENTRY_ANCHORS = {
    "test|Documents/script.py314.lc.npk": 25485,
}


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    scripts = [s for s in reg["sources"] if s["kind"] == "容器(script)"]
    scripts.sort(key=lambda s: (s["client_channel"], s["path"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {"packages": []}
    for s in scripts:
        client_root = Path(r"E:\mrzh" if s["client_channel"] == "test" else r"E:\LifeAfter")
        pkg_path = client_root / s["path"]
        slug = s["path"].replace("/", "_").replace(".", "_")
        rec = {
            "client_channel": s["client_channel"],
            "path": s["path"],
            "registry_sha256": s["sha256"],
            "size": s["size"],
        }
        try:
            reader = LiveNpkReader(pkg_path, "unresolved")
            meta = reader.source_metadata()
        except (NpkFormatError, OSError, ValueError) as exc:
            rec["status"] = f"error: {exc}"
            summary["packages"].append(rec)
            print(rec["status"], s["path"])
            continue
        rec["status"] = "indexed"
        rec["sha256_ok"] = meta["package_sha256"] == s["sha256"]
        rec["bytes_ok"] = meta["bytes"] == s["size"]
        rec["entry_count"] = meta["entry_count"]
        rec["mtime_ns"] = meta.get("mtime_ns")

        # 锚校验
        anchor = KNOWN_ENTRY_ANCHORS.get(f"{s['client_channel']}|{s['path']}")
        if anchor is not None:
            rec["anchor_ok"] = meta["entry_count"] == anchor

        # 写 entries jsonl
        out = OUT_DIR / f"{s['client_channel']}_{slug}.entries.jsonl"
        flag_counter: Counter = Counter()
        dup_fid = 0
        seen_fid = set()
        with out.open("w", encoding="utf-8", newline="\n") as f:
            for e in reader._entries:
                d = e.as_public_dict()
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
                flag_counter[e.flag] += 1
                if e.file_id in seen_fid:
                    dup_fid += 1
                seen_fid.add(e.file_id)
        rec["entries_file"] = str(out.relative_to(ROOT))
        rec["flag_distribution"] = dict(flag_counter)
        rec["unique_file_ids"] = len(seen_fid)
        rec["duplicate_file_id_rows"] = dup_fid
        summary["packages"].append(rec)
        print(f"{s['client_channel']} {s['path']}: {meta['entry_count']} entries, "
              f"flags={dict(flag_counter)}, sha_ok={rec['sha256_ok']}")

    (OUT_DIR / "script_package_index_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for p in summary["packages"] if p["status"] == "indexed"
             and p["sha256_ok"] and p.get("anchor_ok", True))
    print(f"indexed {ok}/{len(scripts)} packages fully verified")
    return 0 if ok == len(scripts) else 1


if __name__ == "__main__":
    sys.exit(main())
