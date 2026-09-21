# -*- coding: utf-8 -*-
"""P1-8 Stage 3b-3：WPK/IDX 盘点与索引 —— 独立于 GPK/FPK/NPK 链。

- idx（SKPW）：头部 0x20 + 每条 0x24：hash(16=解压内容 MD5) + ?4 + pkg(低8位) +
  offset + payload_size + hf(header_size=低16位)。记录全量索引。
- wpk：实体容器（1DPW 头 + payload）；实体由 idx 记录定位，实体内嵌 16B hash
  与 idx hash 一致（1DPW 已验证）。wpk 层只做文件级元数据 + 关联表。
- 复用 wpk_1dpw_decryptor.parse_idx（SKPW）；非 SKPW idx 登记 unknown 格式。
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\03_WPK_1DPW")
sys.path[:0] = [str(Path(__file__).resolve().parent), str(TOOLKIT)]

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
OUT_DIR = ROOT / "data" / "audit" / "package_indexes"


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    wpk_srcs = [s for s in reg["sources"]
                if s["kind"] in ("容器(wpk)", "索引(idx)")]
    # wpk/idx 全部位于 Documents/res
    wpk_srcs.sort(key=lambda s: (s["client_channel"], s["path"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"idx_packages": [], "wpk_files": [], "failures": []}

    idx_by_client: dict[str, dict[str, list[dict]]] = {"test": {}, "live": {}}
    for s in wpk_srcs:
        client_root = Path(r"E:\mrzh" if s["client_channel"] == "test" else r"E:\LifeAfter")
        p = client_root / s["path"]
        slug = s["path"].replace("/", "_").replace(".", "_")
        if s["ext"] == ".idx":
            rec = {"client_channel": s["client_channel"], "path": s["path"],
                   "size": p.stat().st_size, "sha256": s["sha256"]}
            try:
                from wpk_1dpw_decryptor import parse_idx
                entries = parse_idx(str(p))
            except Exception as exc:
                # 非 SKPW 格式登记
                head = p.read_bytes()[:8].hex()
                rec["status"] = f"unknown-idx-format: {exc}"
                rec["head_hex"] = head
                summary["failures"].append(rec)
                summary["idx_packages"].append(rec)
                print("IDX-FAIL", s["path"], rec["status"], head)
                continue
            out = OUT_DIR / f"idx_{s['client_channel']}_{slug}.records.jsonl"
            with out.open("w", encoding="utf-8", newline="\n") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
            rec["status"] = "indexed"
            rec["record_count"] = len(entries)
            rec["records_file"] = str(out.relative_to(ROOT))
            pkg_counter = Counter(e["pkg"] for e in entries)
            rec["pkg_distribution"] = {str(k): v for k, v in sorted(pkg_counter.items())}
            summary["idx_packages"].append(rec)
            idx_by_client[s["client_channel"]][s["path"].split("/")[-1]] = entries
            print(f"IDX {s['client_channel']} {s['path']}: {len(entries)} records")
        else:  # wpk
            rec = {"client_channel": s["client_channel"], "path": s["path"],
                   "size": p.stat().st_size, "sha256": s["sha256"],
                   "status": "wpk-file-registered",
                   "note": "wpk 实体由同名族 idx 记录定位（1DPW 头+payload）；本层为文件级元数据"}
            summary["wpk_files"].append(rec)
            print(f"WPK {s['client_channel']} {s['path']}: {p.stat().st_size} bytes")

    # idx→wpk 覆盖关联：wpk 名族与 idx 的 pkg 号无法一一静态对应（building3.wpk 等），
    # 记录每 idx 引用的 pkg 集合供后续实体级校验使用
    for c, by_name in idx_by_client.items():
        pkg_refs = set()
        for entries in by_name.values():
            for e in entries:
                pkg_refs.add(e["pkg"])
        summary.setdefault("idx_pkg_refs", {})[c] = sorted(pkg_refs)

    (OUT_DIR / "wpk_idx_index_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    n_idx = len(summary["idx_packages"])
    n_wpk = len(summary["wpk_files"])
    ok = sum(1 for p in summary["idx_packages"] if p["status"] == "indexed")
    print(f"idx indexed {ok}/{n_idx}; wpk files registered {n_wpk}; "
          f"failures {len(summary['failures'])}")
    return 0 if ok == n_idx else 1


if __name__ == "__main__":
    sys.exit(main())
