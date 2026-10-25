# -*- coding: utf-8 -*-
r"""核芯升星数值：A 绝对值型（buff 参数即百分比）/ B 系数型（面板=基础×系数）。"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT

STAR_RE = re.compile(r"^(?P<name>.+)-(?P<star>\d{1,2})星$")


def scan(blob, off, span=160):
    out = []
    for pos in range(off, min(off + span, len(blob) - 8)):
        v = struct.unpack_from("<d", blob, pos)[0]
        if 0.005 <= v <= 3.0 and abs(v - round(v, 6)) < 1e-9:
            out.append(round(v, 6))
    return out


def main():
    p = CD / "buff_data.py"
    c = CD / "buff_data_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    body = b[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    per_core = {}
    for r in rows:
        m = STAR_RE.match(str(g(r, "name") or ""))
        if not m:
            continue
        v = g(r, "buf_custom_params")
        if not isinstance(v, str) or not v.startswith("jump:"):
            continue
        arr = scan(blob, int(v.split(":")[1]))
        if arr:
            per_core.setdefault(m.group("name").strip(), {})[int(m.group("star"))] = arr

    picked = {}
    for core, stars in per_core.items():
        # A) 百分比列：某列在 0.02–1.0 且单调
        seqs = {}
        for star, arr in stars.items():
            for i, v in enumerate(arr):
                seqs.setdefault(i, {})[star] = v
        bestA = None
        for seq in seqs.values():
            if len(seq) < 3:
                continue
            ks = sorted(seq)
            vals = [seq[k] for k in ks]
            if not all(vals[j] <= vals[j + 1] + 1e-9 for j in range(len(vals) - 1)):
                continue
            if len(set(vals)) < 2 or not all(0.02 <= v <= 1.0 for v in vals):
                continue
            if bestA is None or len(vals) > len(bestA[1]):
                bestA = (vals[-1], seq)
        # B) 系数列：每星取 (1.0, 2.0] 最大值
        seqB = {}
        for star, arr in stars.items():
            cand = [v for v in arr if 1.0 < v <= 2.0]
            if cand:
                seqB[star] = max(cand)
        okB = False
        if len(seqB) >= 3:
            ks = sorted(seqB)
            vals = [seqB[k] for k in ks]
            okB = all(vals[j] <= vals[j + 1] + 1e-9 for j in range(len(vals) - 1)) and len(set(vals)) >= 2

        if bestA and (not okB or len(bestA[1]) >= len(seqB)):
            picked[core] = ("percent", bestA[1])
        elif okB:
            picked[core] = ("factor", seqB)

    bp = WEB / "data/boards/mutation_core_full.json"
    d = json.loads(bp.read_text(encoding="utf-8"))
    n_abs = n_fac = 0
    for it in d["items"]:
        it.pop("star_values", None)
        it.pop("star_factor", None)
        got = picked.get(str(it.get("name") or "").strip())
        if not got:
            continue
        kind, seq = got
        ks = sorted(seq)
        vals = [seq[k] for k in ks]
        if kind == "percent":
            it["star_values"] = [{"star": k, "pct": round(seq[k] * 100, 2)} for k in ks]
            it["star_value_kind"] = "percent"
            n_abs += 1
        else:
            it["star_factor"] = [{"star": k, "factor": round(seq[k], 4)} for k in ks]
            it["star_value_kind"] = "factor"
            n_fac += 1

    d["meta"]["field_labels"]["star_values"] = "升星属性"
    d["meta"]["field_labels"]["star_factor"] = "星级系数"
    d["meta"]["notes"] = (str(d["meta"].get("notes") or "") +
                          "\n升星数值：绝对值型 %d 枚；系数型 %d 枚（基础值不在客户端）。" % (n_abs, n_fac)).strip()
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/mutation_core_full.js").write_text(
        "window.WIKI_BOARD_mutation_core_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("绝对值型", n_abs, "｜系数型", n_fac)
    for it in d["items"]:
        if it.get("star_values"):
            print("A", it["name"], it["star_values"][:5]); break
    for it in d["items"]:
        if it.get("star_factor"):
            print("B", it["name"], it["star_factor"][:5]); break


if __name__ == "__main__":
    main()
