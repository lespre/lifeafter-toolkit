# -*- coding: utf-8 -*-
"""P1-8 Stage 1：file_hash_pack.bin（FHPK v2）解析与评估。

已验证结构（skill lifeafter-patch-delta-forensics）：
  HEADER = '<4sIIII20s'  magic=FHPK version=2 entry_count toc_offset data_offset sha1
  TAIL   = '<QIQI16s16s' h_offset,h_size,x_offset,x_size,h_md5,x_md5
  TOC 每条: uint16 name_len + UTF-8 name + TAIL(64B)
只读解析 TOC；对少量 h_data/x_data 抽样做 MD5 验证。输出评估：能提供哪些全局文件索引信息。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

AUDIT = Path(r"E:\la拆包项目\08Lifeafter wiki\data\audit")
OUT_DIR = AUDIT / "file_hash_pack"
HEADER = struct.Struct("<4sIIII20s")
TAIL = struct.Struct("<QIQI16s16s")


def parse(path: Path, md5_samples: int = 4) -> dict:
    rec = {"path": path.as_posix(), "size": path.stat().st_size}
    with path.open("rb") as f:
        raw = f.read(HEADER.size)
        if len(raw) != HEADER.size:
            rec["error"] = "short header"
            return rec
        magic, version, entry_count, toc_offset, data_offset, sha1 = HEADER.unpack(raw)
        rec["magic"] = magic.decode("latin1", "replace")
        rec["version"] = version
        rec["entry_count"] = entry_count
        rec["toc_offset"] = toc_offset
        rec["data_offset"] = data_offset
        rec["header_sha1"] = sha1.hex()
        # 校验整体 sha1 = file[:20] + file[40:]
        f.seek(0)
        head = f.read(20)
        f.seek(40)
        rest = f.read()
        rec["sha1_ok"] = hashlib.sha1(head + rest).hexdigest() == sha1.hex()
        # 读 TOC
        f.seek(toc_offset)
        entries = []
        names = []
        for i in range(entry_count):
            nl = f.read(2)
            if len(nl) != 2:
                rec["error"] = f"toc truncated at {i}"
                break
            (name_len,) = struct.unpack("<H", nl)
            name = f.read(name_len).decode("utf-8", "replace")
            tail = f.read(TAIL.size)
            if len(tail) != TAIL.size:
                rec["error"] = f"tail truncated at {i}"
                break
            h_off, h_size, x_off, x_size, h_md5, x_md5 = TAIL.unpack(tail)
            entries.append({
                "name": name,
                "h_offset": h_off, "h_size": h_size, "h_md5": h_md5.hex(),
                "x_offset": x_off, "x_size": x_size, "x_md5": x_md5.hex(),
            })
            names.append(name)
        rec["toc_read"] = len(entries)
        rec["entries"] = entries
        rec["names"] = names
        # name 形态统计
        ext_c = Counter()
        for n in names:
            ext = n.rsplit(".", 1)[-1].lower() if "." in n else "(none)"
            ext_c[ext] += 1
        rec["name_ext_top"] = dict(ext_c.most_common(15))
        rec["name_len_min"] = min((len(n) for n in names), default=0)
        rec["name_len_max"] = max((len(n) for n in names), default=0)
        # x_data/h_data 大小合计
        rec["h_bytes_total"] = sum(e["h_size"] for e in entries)
        rec["x_bytes_total"] = sum(e["x_size"] for e in entries)
        # 抽样 MD5 验证（x_data）
        md5_ok = 0
        md5_fail = 0
        for e in entries[:md5_samples]:
            if e["x_size"] == 0:
                md5_ok += 1
                continue
            f.seek(data_offset + e["x_offset"])
            blob = f.read(e["x_size"])
            if len(blob) == e["x_size"] and hashlib.md5(blob).hexdigest() == e["x_md5"]:
                md5_ok += 1
            else:
                md5_fail += 1
        rec["x_md5_samples_ok"] = md5_ok
        rec["x_md5_samples_fail"] = md5_fail
        # 是否含路径型 name（res/xxx 或 .npk/.gpk 形态）
        rec["name_has_res_prefix"] = sum(1 for n in names if n.startswith("res/") or n.startswith("res\\"))
        rec["name_container_ext"] = sum(1 for n in names if n.rsplit(".", 1)[-1].lower() in
                                        ("npk", "gpk", "wpk", "fpk", "idx", "pi"))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md5-samples", type=int, default=4)
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for client, root in (("test", r"E:\mrzh"), ("live", r"E:\LifeAfter")):
        p = Path(root) / "Documents" / "file_hash_pack.bin"
        results[client] = parse(p, args.md5_samples)
        r = results[client]
        print(f"== {client}: magic={r.get('magic')} v={r.get('version')} "
              f"entries={r.get('entry_count')} toc_read={r.get('toc_read')} "
              f"sha1_ok={r.get('sha1_ok')}")
    # 双端对比
    t_names = set(results["test"]["names"])
    l_names = set(results["live"]["names"])
    results["compare"] = {
        "both": len(t_names & l_names),
        "test_only": len(t_names - l_names),
        "live_only": len(l_names - t_names),
        "same_x_md5_for_common": sum(
            1 for n in (t_names & l_names)
            if _by_name(results["test"], n)["x_md5"] == _by_name(results["live"], n)["x_md5"]
        ),
    }
    out = OUT_DIR / "file_hash_pack_assessment.json"
    # assessment 只保留统计与对比（entries/names 全量在 jsonl）
    slim = {}
    for c in ("test", "live"):
        r = results[c]
        slim[c] = {k: v for k, v in r.items() if k not in ("entries", "names")}
    slim["compare"] = results["compare"]
    # TOC 全量落 jsonl（官方文件清单，供 P1/后续交叉使用）
    for c in ("test", "live"):
        r = results[c]
        with (OUT_DIR / f"{c}_file_hash_pack_toc.jsonl").open(
                "w", encoding="utf-8", newline="\n") as f:
            for e in r["entries"]:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"{c} toc -> jsonl: {r['toc_read']} entries")
    # 官方清单 vs 磁盘文件地图交叉（路径归一：FHPK name 用 / 且无前导；文件地图为相对 posix）
    import collections as _c
    for c, inv_name in (("test", "mrzh_file_inventory.jsonl"),
                        ("live", "lifeafter_file_inventory.jsonl")):
        disk = set()
        for ln in (AUDIT / "client_file_maps" / inv_name).read_text(
                encoding="utf-8").splitlines():
            if ln.strip():
                disk.add(json.loads(ln)["path"].replace("\\", "/"))
        official = {n.replace("\\", "/") for n in results[c]["names"]}
        slim[c]["cross_with_disk"] = {
            "official_total": len(official),
            "on_disk": len(official & disk),
            "official_but_not_on_disk": sorted(official - disk)[:30],
            "official_but_not_on_disk_count": len(official - disk),
        }
    out.write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    print("assessment (slim) ->", out)
    return 0


def _by_name(rec: dict, name: str) -> dict:
    for e in rec["names"]:
        pass
    idx = rec["names"].index(name)
    # names 列表与 entries 同序（评估阶段已确保无截断）
    return {"x_md5": rec["entries"][idx]["x_md5"]}


if __name__ == "__main__":
    sys.exit(main())
