# -*- coding: utf-8 -*-
r"""重建「限定芯片」奖池：按 special_chip_lottery_hd_conf_data(kj1) 每期取芯片 id。

修正点：旧清单把芯片错配到了别的期（实测 期4 应为 330025 异变赋能 / 331015 荆棘护盾，
旧板写成 全神贯注/从容不迫）。本脚本按期号直读 conf 行的 new_chips / up_chips /
active_pool_ids 三个 0x27 组，并给每条证据。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

BASE = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1.py"
CHS = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1_chs.py"


def groups_for(body: bytes, off: int):
    """从 off 起取 0x27 组；不在 off 就向后找最近的 0x27（最多 24B）。"""
    for delta in range(0, 25):
        g = BT.resolve_jump_group(body, off + delta)
        if g:
            return g, delta
    return None, None


def main() -> int:
    raw = BASE.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(CHS.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)

    # 芯片 id → 名字
    chip = json.loads((WEB / "data/boards/tactical_chip_full.json").read_text(encoding="utf-8"))
    names = {}
    for it in chip["items"]:
        nm = it.get("name")
        for k in ("id", "item_id", "chip_id"):
            v = it.get(k)
            if v:
                names[str(v).replace("chip_", "")] = nm

    out = []
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        members, ev = [], []
        for key in ("new_chips", "up_chips", "active_pool_ids"):
            v = f.get(key)
            if isinstance(v, str) and v.startswith("jump:"):
                g, d = groups_for(body, int(v.split(":")[1]))
                if g:
                    ev.append("%s@+%d" % (key, d))
                    for cid in g:
                        if cid not in members:
                            members.append(cid)
        out.append({
            "conf_key": r["key"],
            "chips": members,
            "names": [names.get(str(c)) for c in members],
            "evidence": ", ".join(ev) or "no-group",
        })
    ok = [x for x in out if x["chips"]]
    print("期", len(out), "｜解出芯片的期", len(ok))
    for x in ok[:8]:
        print("  期%-3s %s %s" % (x["conf_key"], x["chips"], x["names"]))
    (PROJ / "01_索引与产物/10_索引/热更检测/chip_lottery_fixed.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写 chip_lottery_fixed.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
