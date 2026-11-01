# -*- coding: utf-8 -*-
"""探查 shining_title_conf_data（动态称号?）与其它称号相关表字段。只读。"""
import sys, collections, json
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B


def dump(stem, limit=1):
    rows = B.decode(stem)
    print(f"\n== {stem}  行数={len(rows)}")
    if not rows:
        return rows
    keys = sorted(rows[0]["values"].keys())
    print("字段:", keys)
    for x in rows[:limit]:
        print(json.dumps({k: (v[1] if isinstance(v, tuple) else v) for k, v in x["values"].items()},
                         ensure_ascii=False)[:600])
    return rows

s = dump("shining_title_conf_data", 3)
if s:
    print("\nshining 的 title 关联字段样例全表前20 key:",
          [x["key"] for x in s[:20]])
dump("title_conf_data_kj1", 2)
dump("title_conf_data_yk", 2)
dump("ring_special_effect_type_title_data", 2)
dump("newspaper_title_bg_data", 2)
dump("title_quest_2_title_info", 2)
