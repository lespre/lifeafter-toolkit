# -*- coding: utf-8 -*-
"""Read-only literal audit of the common_item split-table loader shell (BA8).

Locks the two smallest members of the BA8 ``common_item_data`` table family
and records only byte-level literal evidence recovered from them:

* ``001765.bin`` — ``common_item_data.py`` loader shell (815 B): the marshal
  constant table literally names ``MergedTableData``, ``SplitTableData`` and
  the ``_base`` / ``_inc`` / ``_del`` modules plus a version hash.
* ``016447.bin`` — ``common_item_data_del.py`` deletion module (147 B): a
  module that constructs a ``set`` named ``data``.

The audit never imports, marshal-loads, compiles or executes these payloads.
It reports framing literals only.  In particular it does NOT claim the merge
order, key-overwrite semantics, delete-key values, gray-release conditions or
live-server enablement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import datetime as dt
from pathlib import Path

BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "audit"

# SHA-256 locks captured from the locked BA8 working copy (2026-09-07).
LOCKED_SHA256 = {
    "001765.bin": "af4d91fec923b7aeaec4e6151b4d863991881686f396baa0ba6ae89d41325d51",
    "016447.bin": "fe1ef916bbe917900d54da70a756397ff4c8983a03d65a8bb61788ec183a9653",
}

SHELL_TERMS = [b"MergedTableData", b"SplitTableData", b"common_item_data_base",
               b"common_item_data_inc", b"common_item_data_del", b"data"]
DEL_TERMS = [b"set", b"data", b"common_item_data_del.py"]


def _ascii_runs(data: bytes, min_len: int = 2) -> list[dict[str, object]]:
    return [{"offset": m.start(),
             "text": m.group().decode("ascii", "backslashreplace")}
            for m in re.finditer(rb"[ -~]{%d,}" % min_len, data)]


def _audit_file(name: str, terms: list[bytes]) -> dict[str, object]:
    path = BA8_ENTRIES / name
    if not path.is_file():
        return {"status": "missing", "path": str(path)}
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    locked = LOCKED_SHA256.get(name)
    return {
        "entry": path.stem,
        "bytes": len(raw),
        "sha256": sha,
        "sha256_matches_lock": sha == locked,
        "locked_sha256": locked,
        "ascii_runs": _ascii_runs(raw),
        "term_offsets": {
            t.decode("ascii", "replace"): [i for i in range(len(raw))
                                           if raw.startswith(t, i)]
            for t in terms
        },
    }


def build_report() -> dict[str, object]:
    shell = _audit_file("001765.bin", SHELL_TERMS)
    dele = _audit_file("016447.bin", DEL_TERMS)
    locked_ok = all(
        f.get("sha256_matches_lock") is True
        for f in (shell, dele)
        if f.get("status") != "missing"
    ) and shell.get("status") != "missing" and dele.get("status") != "missing"
    has_shell_tokens = all(
        shell["term_offsets"].get(t.decode(), [])
        for t in (b"MergedTableData", b"common_item_data_base",
                  b"common_item_data_inc", b"common_item_data_del")
    )
    return {
        "meta": {
            "name": "BA8 common_item split-table loader shell — literal audit",
            "generated": dt.date.today().isoformat(),
            "scope": "BA8 locked working copy entries only; no payload "
                     "import/marshal/compile/exec; NPK sources untouched",
            "conclusion": (
                "components-located-loader-replay-pending"
                if (locked_ok and has_shell_tokens)
                else "audit-failed"
            ),
            "claims_not_made": [
                "merge order (base then inc)",
                "same-key overwrite semantics",
                "delete-key values or del runtime effect",
                "gray-release / branch enablement",
                "live-server applicability",
            ],
        },
        "shell_module_1765": shell,
        "del_module_16447": dele,
        "summary": {
            "sha_locks_match": locked_ok,
            "shell_names_all_three_parts": has_shell_tokens,
            "shell_mentions_split_util": bool(
                shell.get("term_offsets", {}).get("SplitTableData", [])),
            "del_constructs_set_named_data": bool(
                dele.get("term_offsets", {}).get("set", []))
            and bool(dele.get("term_offsets", {}).get("data", [])),
            "literal_facts": [
                "entry 1765 constant table names MergedTableData, "
                "SplitTableData, common_item_data_base/inc/del and version "
                "hash aaebe9f972c76ecd",
                "entry 1765 names output module com\\cdata\\common_item_data.py",
                "entry 16447 is a module building a set named data for "
                "common_item_data_del.py",
            ],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUTPUT,
                    help="audit output directory (default data/audit)")
    args = ap.parse_args()
    report = build_report()
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / "common_item_split_shell_audit.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    summary = report["summary"]
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"report -> {out_path}")
    return 0 if report["meta"]["conclusion"] == "components-located-loader-replay-pending" else 1


if __name__ == "__main__":
    sys.exit(main())
