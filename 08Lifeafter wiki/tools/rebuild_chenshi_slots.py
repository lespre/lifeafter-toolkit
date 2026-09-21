# -*- coding: utf-8 -*-
"""
rebuild_chenshi_slots.py ——（三）宸世臻藏子卡（四、奖池区）

从 common_item 全量解码中筛「宸世臻藏」真道具：desc 含【宸世臻藏】或名字属两货币体系
（宸晶臻石/稀世之证/宸世之钥/臻藏时装兑换券）。判定=活动归属文本，绝不按名字撞词
（241377+ 「XX稀世礼」=主题家具礼盒=desc 无宸世归属=不收录——用户 2026-09-06
「这些家具啥的怎么可能在里面」定版）。
复用 tools/rebuild_common_item_text_sources.py 的解码/行级链（同源同格式）。
"""
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import rebuild_common_item_text_sources as base

CURRENCY_NAMES = {"宸世之钥", "宸晶臻石", "稀世之证", "臻藏时装兑换券"}


def is_chenshi_item(name: str, desc: str) -> bool:
    if name in CURRENCY_NAMES or "宸晶臻石" in name or "宸世之钥" in name:
        return True
    return "宸世臻藏" in desc or "宸世" in desc


def main(argv: list[str] | None = None) -> int:
    registry = ROOT / "data" / "live_sources.json"
    full = base.build_board(registry)  # 全道具总表（解码一次；货币行=common_item 名册有=卡内不重复列）

    # 期次层：optional_version_data（004463 双源共享，FID 2E00546E44D8BEF1）=宸世臻藏版本期次行
    # （每期=臻藏/稀世两店 effect 路径+mission_conf_id+start_ts；2024-04-26~2026-08-20 每月一期）
    import re
    import struct as _s
    import datetime as _dt
    from toolkit_core.bindict_table import parse_legacy_chs_pool as _pool
    from bindict_provenance import decode_table_rows_with_chs_slots as _dec
    ent = ROOT / ".." / "03拆包产物" / "config_work" / "script_py314_docs_BA8A239A" / "entries"
    raw = (ent / "004463.bin").read_bytes()
    at = raw.find(b"x{")
    body = raw[at + 6: at + 6 + _s.unpack_from("<I", raw, at + 2)[0]]
    pool = _pool((ent / "007912.bin").read_bytes())
    rows, _un = _dec(body, pool)
    import hashlib
    _sha_b = hashlib.sha256(raw).hexdigest()
    _sha_c = hashlib.sha256((ent / "007912.bin").read_bytes()).hexdigest()
    _src_entries = [
        {"entry_index": 4463, "file_id": "2E00546E44D8BEF1", "decoded_sha256": _sha_b, "role": "optional_version_data base"},
        {"entry_index": 7912, "file_id": "50B88E1D47F3650B", "decoded_sha256": _sha_c, "role": "optional_version_data chs"},
    ]
    vers = []
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        hp = str(f.get("high_shop_effect_path") or "")
        m = re.search(r"ui/spine_new/([a-z0-9_]+)/", hp)
        theme_py = m.group(1) if m else ""
        st = f.get("start_ts")
        ds = _dt.datetime.fromtimestamp(st).strftime("%Y-%m-%d") if isinstance(st, (int, float)) and st > 1e9 else "?"
        vers.append({
            "id": f"ver-{r['key']}", "item_id": None, "name": f"宸世臻藏期（{ds}）",
            "period_key": r["key"], "period_date": ds, "theme_path": theme_py,
            "mission_conf_id": f.get("mission_conf_id"),
            "evidence": "structure", "evidence_level": "structure-only",
            "source": "optional_version_data 004463（双源共享）版本期次行；臻藏商店 effect 路径含 chenshizhencang_zhencang、稀世商店=xishi",
            "provenance": {
                "source_lock_sha256": full["meta"]["provenance"]["source_locks"][0]["sha256"],
                "source_entries": _src_entries,
                "table": "optional_version_data",
                "row_key": r["key"],
                "field_refs": [f"optional_version_data key={r['key']}", "high_shop_effect_path",
                               "low_shop_effect_path", "start_ts", "mission_conf_id"],
                "name_source": "optional_version_data start_ts→日期派生期名；theme_path=high_shop_effect_path 首段主题拼音",
            },
        })
    vers.sort(key=lambda v: v["period_date"])
    # 公告内容层：官方更新公告「宸世臻藏」段按起始日对齐（经典/简单服差异分列）
    try:
        cont = json.loads((ROOT / "data/external_refs/chenshi_period_content.json").read_text(encoding="utf-8"))
    except Exception:
        cont = {}
    for v in vers:
        c = cont.get(v["period_date"])
        if c:
            parts = []
            if c.get("classic"):
                parts.append("（经典服）" + "；".join(c["classic"]))
            if c.get("simple"):
                parts.append("（简单服）" + "；".join(c["simple"]))
            if parts:
                v["desc"] = "／".join(parts)
                v["content_source"] = "announce_chenshi.json（mrzh.163.com 官方更新公告）"

    # ── 商品主体层：002962 静态池拆包（2026-09-06 用户「不要实机截图=拆包+定位链=截图只是锚」定版）──
    # 行结构（27.109）：每商品行=[21011,行号][品id][品id,1][货币,价]；行内无限购周期/时间字段
    # → 常驻/限时=服务端维度=静态不可分（板上不做该断言）；实机锚点只作命名/验证字段。
    pool = json.loads((ROOT / "data/external_refs/chenshi_static_pool_002962.json").read_text(encoding="utf-8"))
    import hashlib as _hl2962
    _sha2962 = _hl2962.sha256(
        (ROOT / ".." / "03拆包产物" / "config_work" / "script_py314_docs_BA8A239A" / "entries" / "002962.bin").read_bytes()
    ).hexdigest()
    # 锚点命名（用户 2026-09-06 实机：UI 名↔静态 id 对应=verified）；价=002962 行内静态价（标 static）
    ANCHOR_VERIFIED = {
        156182: ("重构转印器", 2, "臻藏"), 139267: ("帝皇战翼交易盒", 3, "臻藏"),
        660060: ("异变核芯-贯通战术", 30, "稀世"), 660076: ("异变核芯-余烬流火", 30, "稀世"),
        640015: ("浑天穹焰", 5, "臻藏"), 640011: ("时空裂隙", 50, "稀世"),
        1110021: ("紫焰蛇矛", 4, "臻藏"), 366126: ("霓虹恶魔", 450, "稀世"),
        152182: ("飞行载具改装模块", 10, "稀世"), 153523: ("银蛇迅影升级芯片", None, "臻藏"),
    }
    SEG_CN = [("660", "异变核芯"), ("1110", "武器皮肤"), ("640", "外观/投影"), ("57", "主题时装系"),
              ("15", "材料/道具"), ("152", "载具升级件"), ("167", "宠物件"), ("122", "家装"),
              ("240", "自选箱"), ("38", "喷漆"), ("194", "载具/无人机"), ("182", "载具/无人机"),
              ("469", "载具涂装"), ("470", "载具涂装"), ("46", "时装/涂装"), ("47", "时装/涂装"),
              ("103", "配方"), ("105", "配方"), ("63", "召唤器段"), ("65", "舞/特效"),
              ("97", "道具"), ("27", "道具"), ("21", "道具")]
    def seg_of(iid):
        st = str(iid)
        for pre, nm in SEG_CN:
            if st.startswith(pre):
                return nm
        return "其他"
    # ── 商品池内容层：002962 静态池 205 品=并入「常驻商品池」单卡（2026-09-06 用户
    #    「不要每项目一子卡=塞回常驻/每期里面」定版；卡=容器=内容=族分组清单文本）
    SEG_ORDER = [("660", "异变核芯"), ("1110", "武器皮肤"), ("640", "外观/投影"), ("57", "主题时装系"),
                 ("15", "材料/道具"), ("152", "载具升级件"), ("240", "自选箱"), ("167", "宠物件"),
                 ("122", "家装"), ("38", "喷漆"), ("380", "喷漆"), ("65", "舞/特效"),
                 ("194", "载具/无人机(名册缺)"), ("182", "载具/无人机(名册缺)"),
                 ("469", "载具涂装(名册缺)"), ("470", "载具涂装(名册缺)"),
                 ("46", "涂装/时装(名册缺)"), ("47", "涂装/时装(名册缺)"),
                 ("103", "配方(名册缺)"), ("105", "配方(名册缺)"), ("63", "召唤器段(名册缺)"),
                 ("97", "道具(名册缺)"), ("27", "道具(名册缺)"), ("21", "道具(名册缺)"),
                 ("150", "材料道具"), ("151", "材料道具"), ("153", "材料道具"), ("154", "材料道具"),
                 ("155", "材料道具"), ("156", "材料道具"), ("135", "材料道具(部分gift名)")]
    pool_named = {str(it["id"]): it["name"] for it in pool.get("named", [])}
    all_ids = sorted({str(x) for x in pool.get("unnamed_ids", [])} | set(pool_named.keys()))
    def seg_of(iid):
        st = str(iid)
        for pre, nm in SEG_ORDER:
            if st.startswith(pre):
                return nm
        return "其他(名册缺)"
    segs = {seg: [] for _, seg in SEG_ORDER}
    for iid in all_ids:
        sg = seg_of(iid)
        if sg not in segs:
            segs[sg] = []
        segs[sg].append(iid)
    seg_lines = []
    for seg, ids in segs.items():
        items_txt = []
        for st in ids:
            iid = int(st)
            if iid in ANCHOR_VERIFIED:
                items_txt.append(f"{ANCHOR_VERIFIED[iid][0]}({st})▲实机在售")
            else:
                nm = pool_named.get(st)
                items_txt.append(f"{nm}({st})" if nm else f"ID {st}")
        seg_lines.append(f"〔{seg}〕{'；'.join(items_txt)}")
    pool_card = {
        "id": "chenshi-pool", "item_id": None,
        "name": "宸世商店 · 常驻商品池（002962 静态=候选目录，含常驻与返场候选）",
        "period_date": "2099-12-31",
        "evidence": "structure", "evidence_level": "structure-only",
        "desc": "002962 客户端静态候选池 205 品（服务端每期从中选品上架并下发新品；常驻/限时=服务端维度=静态不可分；▲=2026-09-06 实机在售锚点）",
        "pool_catalog": "｜".join(seg_lines),
        "source": "optional_hd_exchange_shop_data 002962（双源共享 FID 1E888FAB015CA82D）",
        "content_source": "002962 静态拆包（BA8A239A 快照）",
        "provenance": {
            "source_lock_sha256": full["meta"]["provenance"]["source_locks"][0]["sha256"],
            "source_entries": [{"entry_index": 2962, "file_id": "1E888FAB015CA82D",
                                "decoded_sha256": _sha2962,
                                "role": "optional_hd_exchange_shop_data 静态池"}],
            "table": "optional_hd_exchange_shop_data", "row_key": "002962-pool",
            "field_refs": ["pool_catalog"],
            "name_source": "common_item 名册 + 用户锚点 2026-09-06 + 未命名留 ID",
        },
    }
    vers.insert(1, pool_card)

    items = vers

    meta = dict(full["meta"])
    meta["name"] = "（二）宸世臻藏 · 期次与货币（宸晶臻石/稀世之证两体系）"
    meta["category"] = "四、奖池 / （二）宸世臻藏"
    meta["notes"] = (
        "宸世臻藏活动：期次 28 期（optional_version_data 004463 双源共享，2024-04-26~2026-08-20 "
        "每月一期，key=策划添加序非时间序，按 start_ts 排列；theme_path=当期主题资源目录拼音）；"
        "货币体系（common_item 行级）：宸世之钥 153035（开启宸世宝箱）→ 宸晶臻石 153036（臻藏商店"
        "货币，不回收永久）+ 稀世之证 153040（稀世/稀有商店货币）+ 臻藏时装兑换券 155956；含旧版/"
        "独享版 99736/99741/90099736/90099741。判定=desc 含【宸世臻藏】或名字属两货币体系——"
        "名字撞「稀世」的 241377+ 主题家具稀世礼=不含宸世归属=不收录（用户 2026-09-06 定版）。"
        "商店静态链（穷尽双 npk 实证）：optional_hd_exchange_shop_data 主族 002962=81.5KB 当期商店（双服"
        "同 FID 同 SHA f2573710…=同一份）；yk 005580/ykxq 007946（76KB×2）与 002962 解出内容逐条相同"
        "（30 商品/同 id 序）=三通道同内容冗余=客户端只有当期单快照——历史 27 期商店无任何静态快照"
        "（服务端期到时下发，热更覆盖）→ 历史期商店内容=静态不可得，只留 004463 期次行+官方公告文本。"
        "002962 静态=30 商品 id 级存在（含核芯 660060/投影 640015/载具 194140/召唤器 633090140 等返场），"
        "但商品↔店↔价配对无结构证据（启发近邻配对已证伪=2026-09-06 撤）→ 不发布拆包商品清单；"
        "当期两店清单=2026-08-20 期卡 store_zhencang/store_xishi 字段=用户实机全量快照（2026-09-06 截图 14+ 张=服务端当期 UI=最高权威，两店全分类共 53 品=臻藏 31+稀世 22；9-01 核验 30 品为其子集已并入；002962 静态=参考层标差异）="
        "常驻位（无倒计时）与限时档（倒计时 10-13 天）在品行〔〕标注；庄园页=乐居币 15 换宸晶臻石×10。"
    )
    board = {"meta": meta, "items": items, "stats": {"total": len(items),
             "periods": len(vers)}}
    out = ROOT / "data" / "boards" / "chenshi_slots.json"
    out.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"chenshi_slots: 期次 {len(vers)} = {len(items)} 行 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
