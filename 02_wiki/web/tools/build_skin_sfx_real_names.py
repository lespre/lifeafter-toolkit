# -*- coding: utf-8 -*-
"""建立「皮肤 → 音效真名（内部名）」映射。

链路：weapon_skin_sfx_function_data(skin_id → 行 key)
      → weapon_skin_sound_data_for_query(行 inline_groups 里带 <key, 真名> 对)
      → 真名（如 nucleus_attack_04_01）+ jump 事件引用
"""
from __future__ import annotations

import json
import struct
import sys
import pathlib
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, TOOLKIT_CORE, WEB  # noqa: E402
sys.path.insert(0, str(TOOLKIT_CORE))
sys.path.insert(0, str(WEB / "tools"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

ROOT = pathlib.Path(PROJ)
OUT = ROOT / "01_索引与产物/30_分析/weapon_skin_sfx_real_names.json"


def body(p: pathlib.Path) -> bytes:
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def load(name: str):
    CD = cdata_dir()
    py = CD / (name + ".py")
    if not py.exists():
        return []
    chs = CD / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(body(py), pool)
    return rows


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def main() -> int:
    sfx_rows = load("weapon_skin_sfx_function_data")
    snd_rows = load("weapon_skin_sound_data_for_query")
    print("sfx_function 行 %d ｜ sound 表行 %d" % (len(sfx_rows), len(snd_rows)))

    # 皮肤 → 该皮的 sfx 行 key
    skin_keys: dict[int, list[int]] = defaultdict(list)
    for r in sfx_rows:
        v = {k: val(x) for k, x in (r.get("values") or {}).items()}
        sid = v.get("skin_id")
        if isinstance(sid, int):
            skin_keys[sid].append(int(r["key"]))

    # sound 表：inline_groups / values 里出现的 <key, 名字>
    key2names: dict[int, set[str]] = defaultdict(set)
    key2refs: dict[int, set[str]] = defaultdict(set)
    for r in snd_rows:
        v = {k: val(x) for k, x in (r.get("values") or {}).items()}
        for k, x in v.items():
            if isinstance(x, str) and x.startswith("jump:"):
                key2refs[int(r["key"])].add(x)
        for g in r.get("inline_groups") or []:
            vals = g.get("values") or []
            if len(vals) == 2:
                a, b = val(vals[0]), val(vals[1])
                if isinstance(a, int) and isinstance(b, str):
                    key2names[a].add(b)
                elif isinstance(b, int) and isinstance(a, str):
                    key2names[b].add(a)

    print("sound 表里 <key, 真名> 对覆盖 key 数 %d" % len(key2names))

    out = {}
    covered = 0
    for sid, keys in sorted(skin_keys.items()):
        names = sorted({n for k in keys for n in key2names.get(k, ())})
        refs = sorted({x for k in keys for x in key2refs.get(k, ())})
        if names or refs:
            covered += 1
        out[str(sid)] = {"sfx_keys": keys, "real_names": names, "event_refs": refs}
    print("有真名/事件引用的皮肤 %d / %d" % (covered, len(skin_keys)))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    for sid in list(out)[:5]:
        print(" ", sid, out[sid]["real_names"][:6], out[sid]["event_refs"][:4])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
