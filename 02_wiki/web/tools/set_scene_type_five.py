# -*- coding: utf-8 -*-
"""场景类型按 space_data.map_tag 分五档（不掺名字白名单）。

map_tag 实测语义：
  1 开放世界 · 2 营地/城镇 · 3 PvE 副本战役 · 4 PvP · 5 特殊活动
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys
from collections import defaultdict

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "02_wiki/web/tools"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

LABEL = {4: "PvP对抗", 3: "PvE副本", 1: "开放世界", 2: "营地城镇", 5: "特殊活动"}


def load_space():
    CD = cdata_dir()
    raw = (CD / "space_data.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = CD / "space_data_chs.py"
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(raw[at + 6: at + 6 + n], pool, resolve_jumps=False, lenient=True)
    by_name, tag_of = defaultdict(list), {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        sid, nm, tag = v.get("id"), v.get("name"), v.get("map_tag")
        if isinstance(sid, int) and isinstance(nm, str) and nm:
            by_name[nm].append(sid)
            if isinstance(tag, int):
                tag_of[sid] = tag
    return by_name, tag_of


def main() -> int:
    by_name, tag_of = load_space()
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    cnt = defaultdict(int)
    for it in d["items"]:
        nm = it.get("name") or ""
        ids = sorted(set(by_name.get(nm) or []))
        if not ids:
            m = re.search(r"场景\s*(\d+)", nm)
            if m and int(m.group(1)) in tag_of:
                ids = [int(m.group(1))]
        it["scene_ids"] = ids
        if ids:
            it["场景编号"] = "%d 个：%s" % (len(ids), ", ".join(str(x) for x in ids[:8]) + ("…" if len(ids) > 8 else ""))
            tags = [tag_of.get(i) for i in ids if tag_of.get(i)]
            # 多场景混合时按优先级：PvP > PvE副本 > 特殊活动 > 开放世界 > 营地城镇
            for t in (4, 3, 5, 1, 2):
                if t in tags:
                    label = LABEL[t]
                    break
            else:
                label = "未匹配"
        else:
            label = "未匹配"
        it["scene_type"] = label
        it["场景类型"] = label
        cnt[label] += 1
    meta = d.setdefault("meta", {})
    meta["filters"] = [{"key": "server_type", "label": "服型"},
                       {"key": "source_kind", "label": "来源类型"},
                       {"key": "scene_type", "label": "场景类型"}]
    meta["pvp_rule"] = ("场景类型 = space_data.map_tag：4→PvP对抗 / 3→PvE副本 / 1→开放世界 / "
                        "2→营地城镇 / 5→特殊活动；多场景混合按 4>3>5>1>2 取；无场景号→未匹配。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(dict(sorted(cnt.items(), key=lambda x: -x[1])), "共", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
