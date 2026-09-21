# -*- coding: utf-8 -*-
"""P1-8 Stage 3b-1：GPK 条目索引（FPGH v2，与 NPK/WPK 解析链完全独立）。

结构（已定论，见 06_文件名还原/GPK文件名还原_最终结论）：
  头 64B AES-128-ECB 解密（KEY 606308D8A32C782013D26C2F226F686D）：
    [4:8]=FPGH [8:12]=版本2 [20:24]=条目数 B
  条目表 @64 起，每条 32B <IIIIII>：o(绝对偏移,数据体 o+36)/cmp/dec/c1(内容指纹高)/c2(低)/fl(0|2|12)
条目完全匿名（c1/c2=内容指纹非路径哈希）——索引保留指纹字段，不猜名称。
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent)]

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
OUT_DIR = ROOT / "data" / "audit" / "package_indexes"

KEY = bytes.fromhex("606308D8A32C782013D26C2F226F686D")
ENTRY = struct.Struct("<IIIIII")
ENTRY_SIZE = 32


def aes_ecb(data: bytes) -> bytes:
    usable = len(data) // 16 * 16
    if not usable:
        return data
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    d = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return d.update(data[:usable]) + d.finalize() + data[usable:]


def index_gpk(path: Path, sha_expected: str) -> dict:
    rec = {"path": str(path), "size": path.stat().st_size}
    fs = path.stat().st_size
    with path.open("rb") as f:
        head_raw = f.read(64)
        if len(head_raw) < 64:
            rec["status"] = "error: short header"
            return rec
        head = aes_ecb(head_raw)
        rec["magic_observed"] = head[4:8].decode("latin1", "replace")
        rec["version"] = struct.unpack_from("<I", head, 8)[0]
        count = struct.unpack_from("<I", head, 20)[0]
        # 不 gate magic（gres 变体头布局有差异）；magic 仅记录。
        # count 合理性由条目边界校验兜底；异常 count 直接失败防越界读
        if not (0 < count < 5_000_000) or 64 + count * 32 > fs:
            rec["status"] = f"error: implausible count={count}"
            return rec
        f.seek(64)
        table = f.read(count * ENTRY_SIZE)
    if len(table) != count * ENTRY_SIZE:
        rec["status"] = "error: truncated entry table"
        return rec
    table = aes_ecb(table)
    entries = []
    flags: Counter = Counter()
    unique_c12 = set()
    rejected = 0
    for i in range(count):
        o, cmp_, dec, c1, c2, fl = ENTRY.unpack_from(table, i * ENTRY_SIZE)
        # 参考实现同款边界校验（lifeafter_unpacker_full.parse_gpk_entries）
        if not (o >= 64 and o + 36 + cmp_ <= fs and fl in (0, 2, 12)):
            rejected += 1
            continue
        entries.append({"entry_index": i, "offset": o, "packed_size": cmp_,
                        "decoded_size": dec, "c1": c1, "c2": c2, "flag": fl})
        flags[fl] += 1
        unique_c12.add((c1, c2))
    rec["status"] = "indexed"
    rec["header_count"] = count
    rec["entry_count"] = len(entries)
    rec["rejected_rows"] = rejected
    rec["flag_distribution"] = dict(flags)
    rec["unique_c1c2_pairs"] = len(unique_c12)
    rec["entries"] = entries
    return rec


def main() -> int:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    gpks = [s for s in reg["sources"] if s["kind"] == "容器(gpk)"]
    gpks.sort(key=lambda s: (s["client_channel"], s["path"]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"packages": [], "failures": []}
    for s in gpks:
        client_root = Path(r"E:\mrzh" if s["client_channel"] == "test" else r"E:\LifeAfter")
        slug = s["path"].replace("/", "_").replace(".", "_")
        rec = index_gpk(client_root / s["path"], s["sha256"])
        rec["client_channel"] = s["client_channel"]
        rec["path"] = s["path"]
        entries = rec.pop("entries", [])
        rec["sha256"] = s["sha256"]
        if rec["status"] == "indexed":
            out = OUT_DIR / f"gpk_{s['client_channel']}_{slug}.entries.jsonl"
            with out.open("w", encoding="utf-8", newline="\n") as f:
                for e in entries:
                    f.write(json.dumps(e) + "\n")
            rec["entries_file"] = str(out.relative_to(ROOT))
            summary["packages"].append(rec)
            print(f"{s['client_channel']} {s['path']}: {rec['entry_count']} entries")
        else:
            summary["failures"].append(rec)
            summary["packages"].append(rec)
            print("FAIL", s["path"], rec["status"])
    (OUT_DIR / "gpk_index_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for p in summary["packages"] if p["status"] == "indexed")
    print(f"gpk indexed {ok}/{len(gpks)}; failures {len(summary['failures'])}")
    return 0 if ok == len(gpks) else 1


if __name__ == "__main__":
    sys.exit(main())
