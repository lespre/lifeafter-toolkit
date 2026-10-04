# -*- coding: utf-8 -*-
"""Build a read-only provenance audit for the historical “55 FPK” claim.

Inputs are restricted to retained documents/JSON/CSV/source under the three
approved roots. No E:/mrzh archive body and no E:/lifeafter path is opened.
All generated files stay beside this script.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

OUT = Path(r"E:\提取成果\明日拆包\output\04_fpk_scope")
ALLOWED_ROOTS = [
    Path(r"E:\提取成果"),
    Path(r"E:\mrzh_audit"),
    Path(r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"),
]
OLD_REPORT = Path(r"E:\提取成果\报告文档\全面拆包最终报告.md")
OLD_TOOL = Path(r"E:\提取成果\明日之后拆包工具\lifeafter_unpacker_full.py")
OLD_DOCX = Path(r"E:\提取成果\lifeafter拆包思路与进展.docx")
RUN2_SUMMARY = Path(
    r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"
    r"\极光剑存在性核查_001\12_audit_summary.json"
)
RUN2_HEADS = Path(
    r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"
    r"\极光剑存在性核查_001\04_candidate_payloads.csv"
)
RUN2_META = Path(
    r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"
    r"\极光剑存在性核查_001\14_full_source_metadata_index.csv"
)
RUN2_PHYSICAL_README = Path(
    r"C:\Users\<user>\AppData\Local\hermes\mrzh_weapon_skin_audit\run_002"
    r"\物理实体链路_001\README_证据边界.md"
)
CURRENT_1DPW_REPORT = Path(
    r"E:\提取成果\明日拆包\output\03_1dpw\verification_report.md"
)
EXPECTED_OLD_LIST = Path(r"E:\提取成果\拆包产物\fpk\体验服独有fpk.txt")

TEXT_EXTS = {
    ".md", ".txt", ".json", ".csv", ".log", ".yaml", ".yml",
    ".ini", ".toml", ".xml", ".py",
}
MAX_TEXT_BYTES = 128 * 1024 * 1024
NUMERIC_FPK_RE = re.compile(r"(?i)(?<![A-Za-z0-9_.-])(\d{3}\.fpk)(?![A-Za-z0-9_.-])")
ANY_FPK_RE = re.compile(r"(?i)(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+\.fpk)(?![A-Za-z0-9_.-])")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def line(path: Path, n: int) -> str:
    with path.open("r", encoding="utf-8-sig") as f:
        for i, value in enumerate(f, 1):
            if i == n:
                return value.rstrip("\r\n")
    raise ValueError(f"line {n} missing: {path}")


def decode_text_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeError:
            pass
    return data.decode("utf-8", "replace")


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        raw = zf.read("word/document.xml")
    root = ElementTree.fromstring(raw)
    return "\n".join((node.text or "") for node in root.iter() if node.tag.endswith("}t"))


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def retained_scope_search() -> dict:
    """Search retained textual artifacts only; never follow reparse directories."""
    scanned_files = 0
    scanned_bytes = 0
    skipped_large = []
    parse_errors = []
    files_with_fpk = []
    claim_hits = []
    files_with_exactly_55_unique_fpk_tokens = []
    files_with_64_unique_numeric_fpk_tokens = []
    basename_hits = []

    for root in ALLOWED_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            # Exclude this output tree so reruns remain stable.
            dirnames[:] = [
                d for d in dirnames
                if not is_under(Path(dirpath) / d, OUT)
                and not (getattr(os.stat(Path(dirpath) / d, follow_symlinks=False), "st_file_attributes", 0) & 0x400)
            ]
            for name in filenames:
                path = Path(dirpath) / name
                if "体验服独有fpk" in name.lower():
                    basename_hits.append(str(path))
                ext = path.suffix.lower()
                if ext not in TEXT_EXTS and ext != ".docx":
                    continue
                try:
                    size = path.stat().st_size
                except OSError as exc:
                    parse_errors.append({"path": str(path), "error": repr(exc)})
                    continue
                if size > MAX_TEXT_BYTES:
                    skipped_large.append({"path": str(path), "size_bytes": size})
                    continue
                try:
                    if ext == ".docx":
                        text = docx_text(path)
                    else:
                        data = path.read_bytes()
                        low = data.lower()
                        chinese_gate = (
                            "体验服独有".encode("utf-8") in data
                            or "独有包清单".encode("utf-8") in data
                        )
                        if b"fpk" not in low and not chinese_gate:
                            scanned_files += 1
                            scanned_bytes += size
                            continue
                        text = decode_text_bytes(data)
                    scanned_files += 1
                    scanned_bytes += size
                except Exception as exc:
                    parse_errors.append({"path": str(path), "error": repr(exc)})
                    continue

                any_tokens = sorted(set(ANY_FPK_RE.findall(text.lower())))
                numeric_tokens = sorted(set(NUMERIC_FPK_RE.findall(text.lower())))
                if any_tokens or "体验服独有" in text or "独有包清单" in text:
                    files_with_fpk.append({
                        "path": str(path),
                        "unique_fpk_token_count": len(any_tokens),
                        "unique_numeric_fpk_token_count": len(numeric_tokens),
                    })
                if re.search(r"55\s*个[^\r\n]{0,100}(?:体验服独有|fpk)|(?:体验服独有|fpk)[^\r\n]{0,100}55\s*个", text, re.I):
                    claim_hits.append(str(path))
                if len(any_tokens) == 55:
                    files_with_exactly_55_unique_fpk_tokens.append({
                        "path": str(path), "tokens": any_tokens,
                    })
                if len(numeric_tokens) == 64:
                    files_with_64_unique_numeric_fpk_tokens.append(str(path))

    return {
        "roots": [str(x) for x in ALLOWED_ROOTS],
        "extensions": sorted(TEXT_EXTS | {".docx"}),
        "max_text_bytes": MAX_TEXT_BYTES,
        "files_scanned": scanned_files,
        "bytes_scanned": scanned_bytes,
        "skipped_large": skipped_large,
        "parse_errors": parse_errors,
        "files_with_relevant_tokens": files_with_fpk,
        "claim_phrase_files": sorted(set(claim_hits)),
        "basename_matches_for_expected_list": sorted(set(basename_hits)),
        "files_with_exactly_55_unique_fpk_tokens": files_with_exactly_55_unique_fpk_tokens,
        "files_with_64_unique_numeric_fpk_tokens": sorted(set(files_with_64_unique_numeric_fpk_tokens)),
        "expected_old_list_path": str(EXPECTED_OLD_LIST),
        "expected_old_list_exists": EXPECTED_OLD_LIST.exists(),
    }


def parse_current_64_heads() -> list[dict]:
    rows = []
    with RUN2_HEADS.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not re.fullmatch(r"res/\d{3}\.fpk", row["relative_path"], re.I):
                continue
            head = bytes.fromhex(row["first_64_hex"])
            if len(head) != 64:
                raise ValueError(f"not 64-byte retained head: {row['relative_path']}")
            at20 = head[0x20:0x24]
            if at20 == bytes.fromhex("28b52ffd"):
                kind = "zstd_magic_at_0x20"
            elif head[0x24:0x2C] == b"ftypisom":
                kind = "iso_bmff_box_header_at_0x20_ftypisom_at_0x24"
            elif at20 == b"FSB5":
                kind = "fsb5_magic_at_0x20"
            else:
                kind = "unclassified_non_zstd_at_0x20"
            rows.append({
                "file": row["name"],
                "relative_path": row["relative_path"],
                "size_bytes": int(row["size_bytes"]),
                "mtime_local": row["mtime_local"],
                "offset_0x20_hex": at20.hex(),
                "offset_0x20_class": kind,
                "zstd_magic_at_0x20": at20 == bytes.fromhex("28b52ffd"),
                "historical_55_membership": "unresolved_missing_official_baseline_and_deleted_list",
                "first_64_hex": row["first_64_hex"],
            })
    rows.sort(key=lambda x: x["file"])
    expected = [f"{i:03d}.fpk" for i in range(1, 65)]
    actual = [x["file"] for x in rows]
    if actual != expected:
        raise AssertionError({"expected": expected, "actual": actual})
    return rows


def parse_wpk_inventory() -> dict:
    rows = []
    with RUN2_META.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["relative_path"].lower().endswith(".wpk"):
                rows.append(row["relative_path"].replace("\\", "/"))
    groups = Counter()
    for path in rows:
        if path.startswith("Documents/res/"):
            groups["Documents/res"] += 1
        elif path.startswith("Documents/multi_cloud1/res/"):
            groups["Documents/multi_cloud1/res"] += 1
        else:
            groups["other"] += 1
    return {"total_wpk_files_in_run_002_root_inventory": len(rows), "group_counts": dict(groups), "files": rows}


def source_meta(path: Path) -> dict:
    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "file", "relative_path", "size_bytes", "mtime_local", "offset_0x20_hex",
        "offset_0x20_class", "zstd_magic_at_0x20", "historical_55_membership",
        "first_64_hex",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def build() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    retained_search = retained_scope_search()
    fpk_rows = parse_current_64_heads()
    wpk = parse_wpk_inventory()
    zstd = [x["file"] for x in fpk_rows if x["zstd_magic_at_0x20"]]
    non_zstd = [x["file"] for x in fpk_rows if not x["zstd_magic_at_0x20"]]
    total_bytes = sum(x["size_bytes"] for x in fpk_rows)

    old_report_claim = {
        "scope_lines": {"3": line(OLD_REPORT, 3), "4": line(OLD_REPORT, 4), "5": line(OLD_REPORT, 5)},
        "inventory_line_29": line(OLD_REPORT, 29),
        "claim_line_52": line(OLD_REPORT, 52),
        "wpk_line_53": line(OLD_REPORT, 53),
        "old_1dpw_line_62": line(OLD_REPORT, 62),
        "deletion_notice_line_155": line(OLD_REPORT, 155),
    }
    generator = {
        "test_root_constant_line_33": line(OLD_TOOL, 33),
        "output_root_constant_line_35": line(OLD_TOOL, 35),
        "exp_set_line_187": line(OLD_TOOL, 187),
        "selection_expression_line_188": line(OLD_TOOL, 188),
        "output_line_190": line(OLD_TOOL, 190),
        "write_line_191": line(OLD_TOOL, 191),
        "search_selector_line_324": line(OLD_TOOL, 324),
        "count_print_line_325": line(OLD_TOOL, 325),
        "official_root_call_line_953": line(OLD_TOOL, 953),
    }
    current_wpk_1dpw = {
        "verified_chain_line_11": line(CURRENT_1DPW_REPORT, 11),
        "fpk_boundary_line_13": line(CURRENT_1DPW_REPORT, 13),
        "idx_layout_line_25": line(CURRENT_1DPW_REPORT, 25),
        "physical_source_line_27": line(CURRENT_1DPW_REPORT, 27),
        "entry_boundary_line_30": line(CURRENT_1DPW_REPORT, 30),
        "run_002_physical_boundary_line_6": line(RUN2_PHYSICAL_README, 6),
    }

    report = {
        "audit_name": "55个体验服独有FPK来源与范围审计_001",
        "scope": {
            "allowed_read_roots": [str(x) for x in ALLOWED_ROOTS],
            "output_root": str(OUT),
            "not_read": [
                "E:\\mrzh\\res\\*.fpk raw bodies",
                "E:\\mrzh\\Documents\\res\\*.wpk raw bodies",
                "E:\\lifeafter (the historical official baseline root)",
            ],
            "method": "retained document/JSON/CSV/source review plus first-64-byte records already retained in run_002",
        },
        "verdict": {
            "classification": "historical_basename_selection_claim_with_missing_membership_artifact",
            "plain_zh": (
                "“55个”按保留源码的意图是体验服当前FPK文件名集合减去正式服当前FPK文件名集合；"
                "它不是版本/日期内容差分，也不是Zstd/非Zstd筛选，更不是WPK或1DPW计数。"
                "但原始55行清单、正式服文件名基线和运行日志均未保留，因此55的精确成员及当时计数不能在当前允许材料内复验。"
            ),
            "reported_count": 55,
            "current_fpk_count": len(fpk_rows),
            "conditional_implied_same_name_overlap_count": len(fpk_rows) - 55,
            "exact_55_membership": "unresolved",
            "do_not_promote_hypothesis": (
                "010.fpk..064.fpk happens to contain 55 names, but no retained source proves the official overlap was 001.fpk..009.fpk."
            ),
        },
        "provenance": {
            "old_report": old_report_claim,
            "generator_definition": generator,
            "expected_old_list_artifact": {
                "path": str(EXPECTED_OLD_LIST),
                "exists_now": EXPECTED_OLD_LIST.exists(),
                "status": "expected from code; absent now; old report explicitly says original fpk extraction was deleted",
            },
            "retained_scope_search": retained_search,
        },
        "current_64_retained_head_snapshot": {
            "source_csv": str(RUN2_HEADS),
            "count": len(fpk_rows),
            "filenames": [x["file"] for x in fpk_rows],
            "total_bytes": total_bytes,
            "decimal_gb": round(total_bytes / 1_000_000_000, 6),
            "zstd_magic_at_0x20_count": len(zstd),
            "zstd_magic_at_0x20_files": zstd,
            "non_zstd_at_0x20_count": len(non_zstd),
            "non_zstd_at_0x20_files": non_zstd,
            "non_zstd_classes": {x["file"]: x["offset_0x20_class"] for x in fpk_rows if not x["zstd_magic_at_0x20"]},
            "boundary": "magic classification only from retained first 64 bytes; no frame decompression or full-package scan in this audit",
        },
        "wpk_and_1dpw_relationship": {
            "run_002_wpk_inventory": wpk,
            "verified_current_chain": "IDX -> WPK -> 1DPW -> WPD1/AC -> DTSZ -> Zstandard -> DDS",
            "evidence": current_wpk_1dpw,
            "conclusion": (
                "1DPW is verified as per-entry framing inside IDX-addressed WPK/slot sources. FPK is a separate top-level layer. "
                "The old universal wording 'FPK data area = 1DPW encryption' is unsupported and must not be reused. "
                "This does not exclude an unscanned nested 1DPW occurrence somewhere in an FPK."
            ),
        },
        "three_independent_55_counts": {
            "gpk": "old report line 29/41: 55 top-level .gpk files",
            "claimed_exclusive_fpk": "old report line 52: 55, intended by generator as basename set difference",
            "wpk": "run_002 whole-root inventory: 55 .wpk paths = 48 under Documents/res + 7 under Documents/multi_cloud1/res",
            "warning": "identical numerals do not establish shared membership, container semantics, or derivation",
        },
        "evidence_boundaries": [
            "No official-baseline directory was accessed, so the historical basename difference cannot be rerun.",
            "No content hash comparison exists behind the old 55 claim; same basename never proves same content.",
            "No version/date lock was persisted for the historical official FPK set.",
            "The exact 55-line output is absent and the old report says original FPK extraction artifacts were deleted.",
            "59 Zstd magic hits and five non-Zstd first blocks classify the current retained head snapshot, not test-vs-official exclusivity.",
            "WPK/1DPW evidence proves a separate physical chain only; it does not map any FPK filename to WPK entries.",
        ],
        "source_artifacts": [
            source_meta(OLD_REPORT), source_meta(OLD_TOOL), source_meta(OLD_DOCX),
            source_meta(RUN2_SUMMARY), source_meta(RUN2_HEADS), source_meta(RUN2_META),
            source_meta(RUN2_PHYSICAL_README), source_meta(CURRENT_1DPW_REPORT),
        ],
    }

    csv_path = OUT / "current_64_fpk_header_scope.csv"
    json_path = OUT / "fpk_scope_trace.json"
    readme_path = OUT / "README_55FPK来源与范围.md"
    write_csv(fpk_rows, csv_path)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    readme = f"""# “55个体验服独有 FPK”来源与范围审计

## 结论

- **55 的原始口径**：保留源码执行 `exp_files - off_files`，即 `E:\\mrzh\\res` 与当时 `E:\\lifeafter\\res` 的 **`.fpk` 文件名集合差**。
- **应归类为**：历史快照上的**文件名选择集声明**；不是版本/日期内容差分，不是内容哈希差分，也不是容器格式筛选。
- **精确 55 清单已不可复验**：源码预期输出 `{EXPECTED_OLD_LIST}`，该文件现不存在；旧报告第 155 行明确说原始 `fpk提取` 已删除。正式服当时的文件名基线和运行日志也未保留。
- 当前保留快照有 **{len(fpk_rows)}** 个 `001.fpk..064.fpk`，合计 **{total_bytes:,} B（{total_bytes / 1_000_000_000:.6f} GB）**。其中 `0x20` 为 Zstd magic 的 **{len(zstd)}** 个；非 Zstd 的 **{len(non_zstd)}** 个为：`{', '.join(non_zstd)}`。这组 `59+5` 与“55 独有”无集合推导关系。
- `010.fpk..064.fpk` 虽恰好有 55 个名称，但没有保留证据证明正式服交集就是 `001.fpk..009.fpk`，**禁止把该连续区间冒充历史清单**。

## 与 WPK / 1DPW 的关系

- run_002 全根目录曾清点到 **{wpk['total_wpk_files_in_run_002_root_inventory']} 个 WPK 路径**：`Documents/res` {wpk['group_counts'].get('Documents/res', 0)} 个，`Documents/multi_cloud1/res` {wpk['group_counts'].get('Documents/multi_cloud1/res', 0)} 个。这是另一个独立的“55”。
- 当前哈希锁定复验已证明链路：`IDX → ui4.wpk → 1DPW → AC → DTSZ → Zstandard → DDS`。
- `1DPW` 是 IDX 指向的 WPK/slot 条目外层；**FPK 是另一容器层**。旧报告把 FPK 数据区统一写成“1DPW 加密”没有事实支撑，应撤回。这里不排除未全扫 FPK 内部某处将来出现嵌套 `1DPW`，但现有证据绝不能写成 `FPK = 1DPW`。

## 三个彼此独立的“55”

1. 旧报告的 **55 个 GPK**；
2. 旧报告声称的 **55 个体验服独有 FPK**（源码意图：basename 差集，但清单遗失）；
3. run_002 全根目录清点的 **55 个 WPK 路径**（48+7）。

数字相同不代表同一集合，也不能互相补证。

## 关键证据路径

- 旧聚合声明：`{OLD_REPORT}` 第 29、52、53、62、155 行。
- 差集生成逻辑：`{OLD_TOOL}` 第 165–191、318–325、953 行。
- 当前 64 包头保留记录：`{RUN2_HEADS}`。
- 当前 64 文件元数据：`{RUN2_META}`。
- WPK/1DPW 独立复验：`{CURRENT_1DPW_REPORT}` 第 9–14、25–30 行。
- 武器 IDX→1DPW 边界说明：`{RUN2_PHYSICAL_README}` 第 5–7 行。

## 本目录文件

- `fpk_scope_trace.json`：机器可读来源链、计数、路径、原文行与证据边界。
- `current_64_fpk_header_scope.csv`：64 个 FPK 的保留首 64 字节、`0x20` 分类及“历史 55 成员未知”标记。
- `build_fpk_scope_audit.py`：只读复跑脚本；不访问 FPK/WPK 正文和正式服目录。
- `artifact_sha256.json`：本目录交付件哈希与行数复核。
"""
    readme_path.write_text(readme, encoding="utf-8")

    # Reparse and recount before finalizing.
    reparsed = json.loads(json_path.read_text(encoding="utf-8"))
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    checks = {
        "json_reparse_ok": reparsed["current_64_retained_head_snapshot"]["count"] == 64,
        "csv_data_rows": len(csv_rows),
        "csv_rows_equal_64": len(csv_rows) == 64,
        "zstd_rows_equal_59": sum(x["zstd_magic_at_0x20"] == "True" for x in csv_rows) == 59,
        "non_zstd_names_match": [x["file"] for x in csv_rows if x["zstd_magic_at_0x20"] != "True"] == [
            "002.fpk", "010.fpk", "013.fpk", "020.fpk", "021.fpk"
        ],
        "expected_old_list_absent": not EXPECTED_OLD_LIST.exists(),
    }
    if not all(v is True or (k == "csv_data_rows" and v == 64) for k, v in checks.items()):
        raise AssertionError(checks)

    manifest_targets = [Path(__file__), csv_path, json_path, readme_path]
    manifest = {
        "verification": checks,
        "artifacts": [
            {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in manifest_targets
        ],
    }
    manifest_path = OUT / "artifact_sha256.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "output_root": str(OUT),
        "fpk_count": len(fpk_rows),
        "total_bytes": total_bytes,
        "zstd_at_0x20": len(zstd),
        "non_zstd": non_zstd,
        "wpk_total_run2": wpk["total_wpk_files_in_run_002_root_inventory"],
        "wpk_groups": wpk["group_counts"],
        "exact_55_membership": "unresolved",
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
