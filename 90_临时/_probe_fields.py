# -*- coding: utf-8 -*-
"""探针 4：抽奖族配置表的字段名清单（找「配置键字段」）。"""
from __future__ import annotations
import pathlib, sys

WEB = pathlib.Path(__file__).resolve().parents[1] / "02_wiki" / "web"
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "00_规范与工具" / "工具" / "工具库" / "00_共享核心"))
import rebuild_lottery_periods as RLP

T = pathlib.Path(__file__).resolve().parents[1] / "01_索引与产物" / "源包" / "pe_device_20261103" / "cdata" / "com" / "cdata"
RLP.TREE = T

NAMES = [
    "only_fashion_hd_lottery_conf", "multi_optional_lottery_conf_data",
    "super_fashion_lottery_conf_data", "nt_super_fashion_lottery_conf_data",
    "nucleus_lottery_pool_data", "pigeon_wish_lottery_data", "pigeon_wish_conf_data",
    "T2_bobj_lottery_reward_conf_data", "T1_bobj_lottery_v2_base_conf_data",
    "vehicle_lottery_base_conf_data", "xi_yang_yang_lottery_conf_data",
    "ac_lottery_conf_data", "greet_supply_conf_data", "optional_conf_data",
    "falcon_strike_round_conf_data", "falcon_strike_conf_data",
    "super_fashion_lottery_dragon_reward_ui_data", "optional_pool_replace_data",
]
SUFS = ["", "_auto_oversea_data_kj1", "_auto_oversea_data_kjxq", "_auto_oversea_data_yk"]

for nm in NAMES:
    for suf in SUFS:
        rel = nm + suf
        for base in (T, T / "oversea"):
            p = base / (rel + ".py")
            if not p.is_file():
                continue
            chs = base / (rel + "_chs.py")
            try:
                t = RLP.Table(p, chs if chs.is_file() else None)
            except Exception as e:
                print(f"{rel}: 解码失败 {e}")
                continue
            fields = {}
            for row in list(t.by_key.values())[:80]:
                for f, v in row["values"].items():
                    fields.setdefault(f, set()).add(type(v[1] if isinstance(v, tuple) else v).__name__)
            fs = ", ".join(f"{f}:{'/'.join(sorted(ts))}" for f, ts in fields.items())
            where = "oversea" if base == T / "oversea" else "base"
            print(f"[{where}] {rel}  行数 {len(t.by_key)}")
            print(f"      字段: {fs}")
            break
