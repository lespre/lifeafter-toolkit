"""Read-only native string audit for test-server bindict runtime names.
Does not load, execute, or modify any E:\\mrzh binary.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SOURCE = Path(r"E:\mrzh")
OUT = Path(__file__).resolve().parent / "体验服原生_Bindict运行时名称扫描_001"
OUT.mkdir(parents=True, exist_ok=True)
TOKENS = [b"GameServerRepo", b"BindictTuple", b"set_string_pool", b"bdata", b"bindict", b"TableImportHelper"]
EXTENSIONS = {".exe", ".dll", ".pyd"}
CHUNK = 1024 * 1024
OVERLAP = max(map(len, TOKENS)) - 1


def printable_context(data: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in data)


def scan(path: Path) -> list[dict]:
    hits: list[dict] = []
    tail = b""
    absolute = 0
    with path.open("rb") as handle:
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            window = tail + block
            origin = absolute - len(tail)
            for token in TOKENS:
                start = 0
                while True:
                    index = window.find(token, start)
                    if index < 0:
                        break
                    offset = origin + index
                    # Skip an overlap duplicate that belonged completely to previous chunk.
                    if offset >= absolute - len(tail):
                        left = max(0, index - 48)
                        right = min(len(window), index + len(token) + 48)
                        hits.append({
                            "token": token.decode("ascii"),
                            "offset": offset,
                            "context_ascii": printable_context(window[left:right]),
                            "context_hex": window[left:right].hex(),
                        })
                    start = index + 1
            absolute += len(block)
            tail = window[-OVERLAP:] if OVERLAP else b""
    # Exact de-dup if a boundary match was scanned twice.
    unique = {(x["token"], x["offset"]): x for x in hits}
    return [unique[key] for key in sorted(unique)]


def main() -> None:
    files = sorted((p for p in SOURCE.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS), key=lambda p: str(p).lower())
    entries = []
    errors = []
    for path in files:
        try:
            found = scan(path)
            if found:
                entries.append({
                    "source_path": str(path),
                    "file_size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "hits": found,
                })
        except Exception as exc:  # audit must finish other files
            errors.append({"source_path": str(path), "error": f"{type(exc).__name__}: {exc}"})
    token_counts = {token.decode("ascii"): 0 for token in TOKENS}
    for entry in entries:
        for hit in entry["hits"]:
            token_counts[hit["token"]] += 1
    # `bdata` is intentionally retained as a broad weak probe; only exact runtime names
    # below are eligible to identify a candidate decoder binary.
    runtime_tokens = ["GameServerRepo", "BindictTuple", "set_string_pool", "bindict"]
    runtime_entries = [
        entry for entry in entries
        if any(hit["token"] in runtime_tokens for hit in entry["hits"])
    ]
    result = {
        "source_lock": "E:\\mrzh only; original binaries read-only",
        "files_scanned": len(files),
        "tokens": [token.decode("ascii") for token in TOKENS],
        "per_token_hit_counts": token_counts,
        "runtime_tokens": runtime_tokens,
        "runtime_matched_files": len(runtime_entries),
        "runtime_entries": runtime_entries,
        "bdata_broad_probe_note": "bdata is a substring probe and may match unrelated CEF webdata strings; it is never decoder evidence alone.",
        "matched_files_any_token": len(entries),
        "entries_any_token": entries,
        "errors": errors,
    }
    output = OUT / "体验服原生_Bindict运行时名称扫描_001.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "files_scanned": len(files),
        "per_token_hit_counts": token_counts,
        "runtime_matched_files": len(runtime_entries),
        "errors": len(errors),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
