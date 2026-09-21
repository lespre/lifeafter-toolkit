# -*- coding: utf-8 -*-
"""Static set-level audit of the BA8 common_item split table family.

Pure static facts only — NO merged/effective table is produced:

* row-key universe of base (entry 18005) vs inc (entry 5292): overlap,
  base-only, inc-only counts and key samples;
* for keys present in both, whether the replayable name text agrees
  (name-same / name-different / name-missing) — a *candidate* signal for
  row-modification rows, never a loader-order claim;
* del module (entry 16447) state: the deleted-key payload is a custom
  marshal bytecode constant set whose values are not statically recovered,
  so it is reported as ``payload-shape-unresolved`` and is NOT applied.

Every row keeps its source-role identity (base / increment).  The audit
reads the locked BA8 working copy only; the NPK sources are untouched.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "audit"

BASE_ENTRY, BASE_CHS = "018005.bin", "023928.bin"
INC_ENTRY, INC_CHS = "005292.bin", "002592.bin"
DEL_ENTRY = "016447.bin"

# SHA-256 locks from the locked BA8 working copy (2026-09-07).
LOCKED_SHA256 = {
    BASE_ENTRY: "79e25ffd2e4ab34e48717505018fa3ab6438bc637a35fa484aba2a5686208895",
    BASE_CHS: "3be82c3b4089494b0c167a021d24d4f1e58dd7bf18f3bb95b74fbac6ea45bb26",
    INC_ENTRY: "2c8864b07b4e65c7fe2c8260d4e7304b0cc7f07fa39e9892af28b0b6072e44e2",
    DEL_ENTRY: "fe1ef916bbe917900d54da70a756397ff4c8983a03d65a8bb61788ec183a9653",
}


def _load_tools() -> None:
    sys.path[:0] = [str(Path(__file__).resolve().parent),
                    r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"]


_load_tools()
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402


def _xbody(payload: bytes) -> bytes:
    at = payload.find(b"x{")
    length = struct.unpack_from("<I", payload, at + 2)[0]
    return payload[at + 6: at + 6 + length]


def _row_key_text_map(base_entry: str, chs_entry: str) -> dict[int, dict[str, Any]]:
    raw = (BA8_ENTRIES / base_entry).read_bytes()
    if hashlib.sha256(raw).hexdigest() != LOCKED_SHA256[base_entry]:
        raise RuntimeError(f"sha mismatch: {base_entry}")
    pool_raw = (BA8_ENTRIES / chs_entry).read_bytes()
    pool = parse_legacy_chs_pool(pool_raw)
    rows, _unbound = decode_table_rows_with_chs_slots(_xbody(raw), pool)
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        key = row["key"]
        texts: dict[str, Any] = {"decoded": True}
        for field in ("name", "desc", "icon"):
            value = row["values"].get(field)
            if isinstance(value, tuple) and value[0] == "0x05":
                texts[field] = value[1]
        out[key] = texts
    return out


def build_report() -> dict[str, Any]:
    base = _row_key_text_map(BASE_ENTRY, BASE_CHS)
    inc = _row_key_text_map(INC_ENTRY, INC_CHS)
    del_raw = (BA8_ENTRIES / DEL_ENTRY).read_bytes()

    base_keys = set(base)
    inc_keys = set(inc)
    both = sorted(base_keys & inc_keys)
    only_base = sorted(base_keys - inc_keys)
    only_inc = sorted(inc_keys - base_keys)

    name_state = {"same": [], "different": [], "base_missing": [],
                  "inc_missing": []}
    for key in both:
        b_name = base[key].get("name")
        i_name = inc[key].get("name")
        if b_name is None:
            name_state["base_missing"].append(key)
        elif i_name is None:
            name_state["inc_missing"].append(key)
        elif b_name == i_name:
            name_state["same"].append(key)
        else:
            name_state["different"].append(
                {"key": key, "base": b_name, "inc": i_name})

    return {
        "meta": {
            "name": "BA8 common_item split family — static set-level audit",
            "generated": dt.date.today().isoformat(),
            "scope": "BA8 locked working copy (base 018005+023928, inc "
                     "005292+002592, del 016447); no NPK writes; no payload "
                     "execution",
            "conclusion": "static-set-facts-only-loader-replay-pending",
            "claims_not_made": [
                "inc does/does not override base at runtime",
                "del removes the listed keys at runtime",
                "server-side gray-release or branch enablement",
                "effective/merged common_item table",
            ],
        },
        "universe": {
            "base_keys": len(base_keys),
            "inc_keys": len(inc_keys),
            "both": len(both),
            "only_base": len(only_base),
            "only_inc": len(only_inc),
        },
        "keys": {
            "both": both,
            "only_base_sample": only_base[:20],
            "only_inc": only_inc,
            "only_base_count": len(only_base),
        },
        "name_consistency_on_overlap": {
            "same": len(name_state["same"]),
            "different": len(name_state["different"]),
            "base_missing_name": len(name_state["base_missing"]),
            "inc_missing_name": len(name_state["inc_missing"]),
            "different_samples": name_state["different"][:10],
        },
        "del_module": {
            "entry": DEL_ENTRY,
            "bytes": len(del_raw),
            "sha256": hashlib.sha256(del_raw).hexdigest(),
            "state": "payload-shape-unresolved",
            "note": "deleted keys are a custom-marshal set constant; values "
                    "are not statically recovered, so no key is removed",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()
    report = build_report()
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / "common_item_family_composition_audit.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    u = report["universe"]
    n = report["name_consistency_on_overlap"]
    print(f"base={u['base_keys']} inc={u['inc_keys']} both={u['both']} "
          f"only_base={u['only_base']} only_inc={u['only_inc']}")
    print(f"name same={n['same']} different={n['different']} "
          f"base_missing={n['base_missing_name']} inc_missing={n['inc_missing_name']}")
    print(f"report -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
