# -*- coding: utf-8 -*-
r"""给战术芯片补「首档效果」：belt_chip_data.base_desc + base_params(jump 浮点组)。

base_params 结构：0x07 <n> 后接 n 个 [0x12 + float32]
占位符 {i} 用第 i 个浮点填充（去掉多余小数）。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
from _src import cdata_dir
CD = cdata_dir()
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def fmt(x: float) -> str:
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return ("%.2f" % x).rstrip("0").rstrip(".")


def read_floats(blob: bytes, off: int, want: int = 0):
    # 变体 A：0x27 组 → 数据从 off+3 起为裸 float32
    if blob[off] == 0x27:
        out = []
        pos = off + 3
        for _ in range(want or 8):
            if pos + 4 > len(blob):
                break
            out.append(struct.unpack_from("<f", blob, pos)[0])
            pos += 4
        return out
    if blob[off] != 0x07:
        return []
    n = blob[off + 1]
    pos = off + 2
    out = []
    for _ in range(n):
        tag = blob[pos]
        if tag == 0x12 and pos + 5 <= len(blob):
            out.append(struct.unpack_from("<f", blob, pos + 1)[0])
            pos += 5
        elif tag == 0x22 and pos + 9 <= len(blob):
            out.append(struct.unpack_from("<d", blob, pos + 1)[0])
            pos += 9
        else:
            break
    return out


def main() -> int:
    p = CD / "belt_chip_data.py"
    c = CD / "belt_chip_data_chs.py"
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

    by_type = {}
    for r in rows:
        ct = str(g(r, "chip_type") or "")
        if not ct:
            continue
        prof = g(r, "proficiency_point") or 0
        rec = {"ct": ct, "prof": prof, "desc": str(g(r, "base_desc") or ""),
               "params": str(g(r, "base_params") or "")}
        if ct not in by_type or prof < by_type[ct]["prof"]:
            by_type[ct] = rec

    cd = json.loads((WEB / "data/boards/tactical_chip_full.json").read_text(encoding="utf-8"))
    filled = 0
    for it in cd["items"]:
        ct = str(it.get("chip_type_id") or "")
        rec = by_type.get(ct)
        if not rec or not rec["desc"]:
            continue
        import re as _re
        want = max([int(m) for m in _re.findall(r"\{(\d+)\}", rec["desc"])] or [-1]) + 1
        vals = []
        if rec["params"].startswith("jump:"):
            vals = read_floats(blob, int(rec["params"].split(":")[1]), want)
        text = rec["desc"]
        for i, v in enumerate(vals):
            text = text.replace("{%d}" % i, fmt(v))
        text = text.replace("#f", "").replace("#n", "").replace("#r", "\n")
        import re
        text = re.sub(r"\{\d+\}", "?", text)
        it["effect_desc"] = text.strip()
        it["effect_level"] = rec["prof"]
        filled += 1

    cd["meta"]["card_summary"] = [["name", "芯片"], ["quality_label", "品质"],
                                  ["family", "类型"], ["effect_desc", "效果"]]
    cd["meta"]["field_labels"]["effect_desc"] = "首档效果"
    cd["meta"]["notes"] = (str(cd["meta"].get("notes") or "") +
                          "\n首档效果 = belt_chip_data 该 chip_type 熟练度最低一档的 base_desc，参数已代入。").strip()
    (WEB / "data/boards/tactical_chip_full.json").write_text(
        json.dumps(cd, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/tactical_chip_full.js").write_text(
        "window.WIKI_BOARD_tactical_chip_full = " + json.dumps(cd, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("补首档效果", filled, "/", len(cd["items"]))
    for it in cd["items"][:3]:
        print("  ", it["name"], "→", (it.get("effect_desc") or "")[:60])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
