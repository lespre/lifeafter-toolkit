#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""池成员映射 v2（修正版）

修正的问题
----------
v1 用字节 grep `27 01 02 + uleb(pool_id)` 判池成员 —— 已证伪：
`27 <type> <count>` 是「uint 列表」通用编码，全 blob 出现 29,502 次
（每条 `[道具id,数量]` 奖励叶子都是它），扫出来的是**引用者**不是**成员**。

v2 判定层级（每条成员必须带 evidence 标签）
------------------------------------------
  L1_JUMP   活动行 jump 字段直解（panel_show_item_ids / left_item_id / shop_display_item_id）
            —— 官方展示层，最硬
  L2_BC     reward_pool_data_base 行 broadcast_content 含活动名
            —— 硬，但只覆盖"会播报的"行
  L3_EXP    同 expiration_time cohort 但**无广播**的行
            —— 不可归属，必须显式标 UNATTRIBUTED，不得计入成员数
  SIBLING   同 cohort 但广播属于**别的活动** → 明确排除（族兄活动）

禁用
----
  字节 grep marker（任何 tag+uleb 组合）。池号 ≠ 行 key：
  `reward_pool_data_base` 行里**没有池号字段**，池归属是包内不存在的显式关系。
"""
from __future__ import annotations

import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

TC = Path(r"E:\la拆包项目\01_工具\工具库\00_共享核心")
sys.path.insert(0, str(TC))
sys.path.insert(0, r"E:\la拆包项目\04_站点\\web\tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa

REWARD_TABLE_IDX = 25636          # com\cdata\reward_pool_data_base.py
REWARD_CHS_IDX = 12708            # …_chs.py
ACT_TABLE_IDX = 15163             # com\cdata\huodong_conf_data.py
ACT_CHS_IDX = 9642


def _rd(ent: Path, i: int) -> bytes:
    return (ent / ("%06d.bin" % i)).read_bytes()


def _xbody(p: bytes) -> bytes:
    at = p.find(b"x{")
    while at != -1:
        if at + 6 <= len(p):
            bl = struct.unpack_from("<I", p, at + 2)[0]
            if bl > 0 and at + 6 + bl <= len(p):
                b = p[at + 6:at + 6 + bl]
                if len(b) >= 8 and struct.unpack_from("<I", b, 4)[0] == 0:
                    return b
        at = p.find(b"x{", at + 1)
    raise ValueError("no x{ body")


class PoolMap:
    """池成员映射器（v2）。"""

    def __init__(self, entries_dir: str | Path):
        self.ent = Path(entries_dir)
        bb = _xbody(_rd(self.ent, REWARD_TABLE_IDX))
        pool = parse_legacy_chs_pool(_rd(self.ent, REWARD_CHS_IDX))
        self.rows, _ = decode_table_rows_with_chs_slots(bb, pool)
        cc, _ = struct.unpack_from("<II", bb, 0)
        self.blob = bb[8 + 4 * cc:]
        self.by_key = {r.get("key"): r for r in self.rows}

    @staticmethod
    def val(v: dict, f: str):
        got = v.get(f)
        return got[1] if got else None

    def leaf(self, v: dict):
        rj = self.val(v, "reward")
        if isinstance(rj, str) and rj.startswith("jump:"):
            try:
                return resolve_jump_group(self.blob, int(rj.split(":")[1]))
            except Exception:
                return None
        return None

    # ---------- L2 / L3 / SIBLING ----------
    def scan_by_broadcast(self, act_name: str, alias: tuple = ()):
        """返回 (L2 命中行, L3 同 cohort 无广播行, SIBLING 别的活动行)"""
        names = (act_name,) + tuple(alias)
        l2, exps = [], []
        for r in self.rows:
            v = r["values"]
            bc = str(self.val(v, "broadcast_content") or "")
            if any(n in bc for n in names):
                l2.append(self._pack(r, "L2_BC"))
                exps.append(self.val(v, "expiration_time"))
        if not l2:
            return [], [], {}, None
        exp = Counter(e for e in exps if e).most_common(1)[0][0]
        l3, sib = [], defaultdict(list)
        for r in self.rows:
            v = r["values"]
            if self.val(v, "expiration_time") != exp:
                continue
            bc = str(self.val(v, "broadcast_content") or "")
            if any(n in bc for n in names):
                continue
            if not bc:
                l3.append(self._pack(r, "L3_EXP_UNATTRIBUTED"))
            else:
                sib[self._act_of(bc)].append(self._pack(r, "SIBLING"))
        return l2, l3, dict(sib), exp

    @staticmethod
    def _act_of(bc: str) -> str:
        import re
        m = re.search(r"在(.+?)活动中获得", bc)
        return m.group(1).strip() if m else bc[:20]

    def _pack(self, r, evidence: str) -> dict:
        v = r["values"]
        lf = self.leaf(v)
        return {
            "key": r.get("key"),
            "note": self.val(v, "note"),
            "prob": self.val(v, "prob_note"),
            "rank": self.val(v, "reward_rank"),
            "p_group": self.val(v, "p_group_id"),
            "limit": self.val(v, "obtain_limit"),
            "leaf": lf,
            "exp": self.val(v, "expiration_time"),
            "evidence": evidence,
        }

    # ---------- L1：活动行 jump 字段 ----------
    def activity_jump(self, act_names: tuple, act_idx: int = ACT_TABLE_IDX, act_chs: int = ACT_CHS_IDX):
        ab = _xbody(_rd(self.ent, act_idx))
        acc, _ = struct.unpack_from("<II", ab, 0)
        ablob = ab[8 + 4 * acc:]
        act_pool = parse_legacy_chs_pool(_rd(self.ent, act_chs))
        arows, _ = decode_table_rows_with_chs_slots(ab, act_pool)
        out = []
        for r in arows:
            v = r["values"]
            blobtxt = json.dumps(v, ensure_ascii=False, default=str)
            if not any(n in blobtxt for n in act_names):
                continue
            item = {"key": r.get("key"), "fields": {}}
            for f, got in v.items():
                if isinstance(got[1], str) and got[1].startswith("jump:"):
                    t = int(got[1].split(":")[1])
                    try:
                        g = resolve_jump_group(ablob, t)
                    except Exception:
                        g = None
                    item["fields"][f] = {"jump": t, "group": g}
                elif got[0] in ("0x01", "0x05"):
                    item["fields"][f] = got[1]
            out.append(item)
        return out


def dump(name: str, ent: str, aliases: tuple = ()):
    pm = PoolMap(ent)
    l2, l3, sib, exp = pm.scan_by_broadcast(name, aliases)
    print("=" * 70)
    print("活动「%s」  exp/有效期 = %s" % (name, exp))
    print("  L2_BC（广播直证成员）: %d 行" % len(l2))
    uniq = {}
    for x in sorted(l2, key=lambda y: -(float(y["prob"]) if y["prob"] else 0)):
        uniq.setdefault((x["note"], str(x["leaf"])), x)
    for x in uniq.values():
        print("     %-24s prob=%-11s rank=%s pg=%-5s 限%-5s 叶子=%s" %
              (str(x["note"])[:22], x["prob"], x["rank"], x["p_group"], x["limit"], x["leaf"]))
    print("  → 去重后 %d 件" % len(uniq))
    print("  L3_EXP_UNATTRIBUTED（同有效期无广播，不可归属）: %d 行" % len(l3))
    for x in sorted(l3, key=lambda y: -(float(y["prob"]) if y["prob"] else 0))[:12]:
        print("     %-24s prob=%-11s pg=%-5s 叶子=%s" %
              (str(x["note"])[:22], x["prob"], x["p_group"], x["leaf"]))
    print("  SIBLING（别的活动，已排除）: %d 个" % len(sib))
    for k, arr in sib.items():
        print("     %-18s %d 行" % (k, len(arr)))
    print("\n  L1_JUMP 活动行字段:")
    for item in pm.activity_jump((name,))[:3]:
        print("     key=%s" % item["key"])
        for f, val in item["fields"].items():
            print("        %-24s %s" % (f, json.dumps(val, ensure_ascii=False, default=str)[:110]))
    return {"act": name, "exp": exp, "L2_direct": list(uniq.values()),
            "L3_unattributed": l3, "SIBLING": sib}


if __name__ == "__main__":
    ENT = (r"E:\la拆包项目\02_资料\\源包\post_update_20260924_1610"
           r"\analysis\script_workcopy_cb85b4d1ed44\entries")
    res = dump("幻夜神谕", ENT, aliases=("神谕童话",))
    OUT = Path(r"E:\la拆包项目\02_资料\\源包\post_update_20260924_1610\analysis\huanye")
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT / "mapping_v2_huanye.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, default=str)
    print("\n落盘 %s" % (OUT / "mapping_v2_huanye.json"))
