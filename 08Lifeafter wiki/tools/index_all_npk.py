# -*- coding: utf-8 -*-
"""P1-8 Stage 3a：registry 全部 npk（script+资源）条目级索引。

复用 LiveNpkReader（NXPK 已验证覆盖 res-root 与 Documents 全部 npk）。
输出：data/audit/package_indexes/npk_<client>_<slug>.entries.jsonl
      + npk_index_summary.json（每包 entry_count/flag 分布/唯一 FID/SHA 校验）
gpk/wpk/fpk 因格式不同（1DPW/IDX/zstd 帧）不在本阶段。
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


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    npks = [s for s in reg["sources"] if s["kind"] in ("容器(npk)", "容器(script)")]
    npks.sort(key=lambda s: (s["client_channel"], s["path"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {"packages": [], "failures": []}
    for s in npks:
        client_root = Path(r"E:\mrzh" if s["client_channel"] == "test" else r"E:\LifeAfter")
        pkg_path = client_root / s["path"]
        slug = s["path"].replace("/", "_").replace(".", "_")
        rec = {"client_channel": s["client_channel"], "path": s["path"],
               "kind": s["kind"], "registry_sha256": s["sha256"], "size": s["size"]}
        try:
            reader = LiveNpkReader(pkg_path, "unresolved")
            meta = reader.source_metadata()
        except Exception as exc:
            rec["status"] = f"error: {exc}"
            summary["failures"].append(rec)
            summary["packages"].append(rec)
            print("FAIL", s["path"], str(exc)[:80])
            continue
        rec["status"] = "indexed"
        rec["sha256_ok"] = meta["package_sha256"] == s["sha256"]
        rec["entry_count"] = meta["entry_count"]
        out = OUT_DIR / f"npk_{s['client_channel']}_{slug}.entries.jsonl"
        flag_counter: Counter = Counter()
        seen = set()
        with out.open("w", encoding="utf-8", newline="\n") as f:
            for e in reader._entries:
                f.write(json.dumps(e.as_public_dict(), ensure_ascii=False) + "\n")
                flag_counter[e.flag] += 1
                seen.add(e.file_id)
        rec["entries_file"] = str(out.relative_to(ROOT))
        rec["flag_distribution"] = dict(flag_counter)
        rec["unique_file_ids"] = len(seen)
        summary["packages"].append(rec)
        print(f"{s['client_channel']} {s['path']}: {meta['entry_count']} "
              f"sha_ok={rec['sha256_ok']}")

    (OUT_DIR / "npk_index_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for p in summary["packages"] if p["status"] == "indexed" and p["sha256_ok"])
    print(f"indexed+sha_ok {ok}/{len(npks)}; failures {len(summary['failures'])}")
    print("summary ->", OUT_DIR / "npk_index_summary.json")
    return 0 if ok == len(npks) else 1


if __name__ == "__main__":
    sys.exit(main())
