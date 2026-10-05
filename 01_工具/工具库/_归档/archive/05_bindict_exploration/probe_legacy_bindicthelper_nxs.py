"""Zero-execution calibration probe for the legacy BindictHelper NXS variant.

This reads only an extracted test-server work copy, never imports/executes the
payload, and accepts output only after exact zlib framing plus a marshal-code
first-byte check. It is a legacy opcode calibration artifact, not a value decoder.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
HELPER = Path(r"C:\Users\<user>\mrzh_bindict_static_reverse\nxs_static_stage_probe.py")
RAW = Path(r"C:\Users\<user>\mrzh_weapon_skin_mapping\bindict_candidate_payloads\script_0EF6B1F0B69A79CB_com_utils_BindictHelper.py.bin")
REPORT = RUN / "体验服旧版_BindictHelper_NXS静态校准_001.json"
RECOVERED = RUN / "体验服旧版_BindictHelper_候选marshal_001.bin"


def load_static_functions():
    spec = importlib.util.spec_from_file_location("nxs_static_probe", HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load static probe helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # imports only the local analysis helper; never the target payload
    return module


def main() -> None:
    helper = load_static_functions()
    raw = RAW.read_bytes()
    header = helper.header_info(raw)
    body_offset = int(header["body_offset"])
    variants = {
        "full_decode_buffer": helper.decode_buffer(raw),
        "body_decode_buffer": helper.decode_buffer(raw[body_offset:]),
        "full_unmodified": raw,
        "body_unmodified": raw[body_offset:],
    }
    attempts = []
    successes = []
    for name, data in variants.items():
        record, recovered = helper.run_candidate(name, data)
        attempts.append(record)
        if recovered is not None:
            successes.append((name, recovered))
    if len(successes) > 1:
        raise RuntimeError("ambiguous transform: multiple exact candidates")
    result = {
        "analysis_mode": "static_zero_execution_legacy_calibration",
        "source_lock": "E:\\mrzh extracted legacy script member; source package remains read-only",
        "raw_path": str(RAW),
        "raw_size": len(raw),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "nxs_header": header,
        "attempts": attempts,
        "accepted_candidate_count": len(successes),
        "boundary": "Any accepted bytes are retained only as non-executed marshal evidence. No marshal.loads, CodeType construction, eval, exec, import of target, or bindict operation is performed.",
    }
    if successes:
        name, recovered = successes[0]
        RECOVERED.write_bytes(recovered)
        result["accepted_candidate"] = {
            "name": name,
            "path": str(RECOVERED),
            "size": len(recovered),
            "sha256": hashlib.sha256(recovered).hexdigest(),
            "first16_hex": recovered[:16].hex(),
        }
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "accepted_candidate_count": len(successes), "accepted": result.get("accepted_candidate"), "attempts": attempts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
