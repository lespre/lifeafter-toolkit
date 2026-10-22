"""ParserDraft: 0x56 index-tail family (hash-keyed single-row field dict).

Structure (verified on PE 2026-10-20 source, 142 tables):

    x{  u32 body_len
    body = [u32 field_count][u32 0][field_count x u32 ends]   <- field-name CHS pool ends
           ... value/group area (jump targets live here) ...
    blob = body[8 + 4*field_count :]
    blob[0:4] = u32 de                              <- offset of the index tail
    tail = blob[de:]
    tail[0] = 0x56  tail[1] = 0x05  tail[2] = u8 n  <- record count
    n x 8B records: (u32 hash, u32 offset)          <- sorted by hash
    row area = tail[3 + 8n :]                       <- one triple per populated field:
        [uleb field_idx][u8 type][value]
        type 0x01/0x0b/0x05/0x02 -> uleb, 0x12 -> f32, 0x22 -> f64, 0x03 -> u8 bool

There is exactly ONE row.  body[0:4] is the FIELD count (== paired *_chs pool
length), not a row count; the 8B records are keyed by a hash of the field name
(hash function not identified) and each record offset points at that field's
triple.  Field name = chs_pool[field_idx].

jump (0x0b) values are offsets into `blob`.  Some targets sit 1-2 bytes before
the real 0x27 group (wrapper bytes 0x06 0x00 / 0x07 0x00), and some are 0x36
mapping rows; both are handled here.

No execution, no writes: read-only on the restore tree.
"""
from __future__ import annotations

import struct
import sys
from typing import Any

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core.bindict_table import uleb, parse_legacy_chs_pool, resolve_jump_group  # noqa: E402

TAIL_MARKER = 0x56
VAL_ULEB = (0x01, 0x02, 0x05, 0x0B, 0x0C)


def split_body(raw: bytes) -> bytes:
    p = raw.find(b"x{")
    if p < 0:
        raise ValueError("no x{ frame")
    ln = struct.unpack_from("<I", raw, p + 2)[0]
    body = raw[p + 6:p + 6 + ln]
    if len(body) != ln:
        raise ValueError("truncated x{ body")
    return body


def load_chs_pool(raw: bytes) -> list[str]:
    return parse_legacy_chs_pool(raw)


def detect(body: bytes) -> dict[str, Any]:
    field_count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * field_count:]
    de = struct.unpack_from("<I", blob, 0)[0]
    if not (4 <= de < len(blob)):
        raise ValueError(f"bad de {de}")
    tail = blob[de:]
    if tail[:1] != bytes([TAIL_MARKER]) or len(tail) < 4:
        raise ValueError(f"not a 0x56 tail: {tail[:4].hex()}")
    n = tail[2]
    if 3 + 8 * n > len(tail):
        raise ValueError("record table out of bounds")
    return dict(field_count=field_count, blob=blob, de=de, tail=tail, nrec=n,
                row_area=de + 3 + 8 * n)


def read_triple(blob: bytes, pos: int, end: int) -> tuple[int, int, Any, int]:
    idx, p = uleb(blob, pos, end)
    t = blob[p]
    p += 1
    if t == 0x12:
        v = struct.unpack_from("<f", blob, p)[0]; p += 4
    elif t == 0x22:
        v = struct.unpack_from("<d", blob, p)[0]; p += 8
    elif t == 0x03:
        v = blob[p]; p += 1
    elif t in VAL_ULEB:
        v, p = uleb(blob, p, end)
    else:
        raise ValueError(f"unknown value tag {t:#04x} at {p - 1}")
    return idx, t, v, p


def read_groups(blob: bytes, pos: int) -> tuple[list[Any], int]:
    """Read a 0x27 group / 0x36 mapping row starting at pos (prefix tolerant)."""
    for skip in (0, 1, 2):
        t = pos + skip
        if t >= len(blob):
            break
        if blob[t] == 0x27:
            g = resolve_jump_group(blob, t)
            if g is not None:
                return g, t
        if blob[t] == 0x36:                     # [36][kt][vt][uleb n] + n x (uleb,uleb)
            try:
                n, p = uleb(blob, t + 3, len(blob))
                pairs = []
                for _ in range(n):
                    k, p = uleb(blob, p, len(blob))
                    v, p = uleb(blob, p, len(blob))
                    pairs.append((k, v))
                return pairs, t
            except ValueError:
                pass
    return [], pos


def parse_table(raw_base: bytes, raw_chs: bytes | None = None) -> dict[str, Any]:
    body = split_body(raw_base)
    meta = detect(body)
    blob, field_count, nrec = meta["blob"], meta["field_count"], meta["nrec"]
    pool = load_chs_pool(raw_chs) if raw_chs else []
    records = [struct.unpack_from("<II", meta["tail"], 3 + 8 * i) for i in range(nrec)]

    pos = meta["row_area"]
    triples = []
    while pos < len(blob):
        idx, t, v, np_ = read_triple(blob, pos, len(blob))
        triples.append((pos, idx, t, v))
        pos = np_

    row: dict[str, Any] = {}
    detail = []
    for spos, idx, t, v in triples:
        name = pool[idx] if 0 <= idx < len(pool) else f"<field_{idx}>"
        out = v
        if t in (0x05,) and pool:
            out = pool[v] if 0 <= v < len(pool) else f"<chs_oob:{v}>"
        if t == 0x0B:
            grp, at = read_groups(blob, v)
            if grp:
                out = {"jump": v, "at": at, "values": grp}
        row[name] = out
        detail.append(dict(off=spos, idx=idx, name=name, tag=t, raw=v, value=out))

    return dict(
        field_count=field_count, nrec=nrec, rows=1, fields=len(triples),
        row=row, detail=detail, blob=blob, de=meta["de"], tail=meta["tail"],
        records=records,
        offsets_are_triple_starts={o for _, o in records} <= {d["off"] for d in detail},
        missing_field_idx=[i for i in range(field_count) if i not in {d["idx"] for d in detail}],
    )


if __name__ == "__main__":
    import os
    base = r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata"
    for stem in ("vehicle_basic_conf", "nucleus_conf"):
        raw = open(os.path.join(base, stem + ".py"), "rb").read()
        chs_p = os.path.join(base, stem + "_chs.py")
        raw_chs = open(chs_p, "rb").read() if os.path.exists(chs_p) else None
        r = parse_table(raw, raw_chs)
        print(f"== {stem}: fields={r['field_count']} records={r['nrec']} rows={r['rows']} "
              f"populated={r['fields']} offs==triples={r['offsets_are_triple_starts']} "
              f"missing={r['missing_field_idx']}")
        for name, val in list(r["row"].items()):
            print("   ", name, "=", val)
