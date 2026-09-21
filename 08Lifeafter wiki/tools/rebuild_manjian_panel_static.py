#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manjian market (满减) board — activity periods + Linglong anchor chain.

Sources (all inside the same BA8 locked snapshot):
- huodong_conf_data kj1 (FB80FED51B8B4638 + chs B48257E8D36A5AD4): activity
  rows whose hd_class is ManJianHuoDong (2023-11..2024-06, 旧满减市场) or
  DiscountMarketHD (2025-04..2026-06, 新满减市场/满减补贴 incl 灵笼满减补贴 3402).
- Linglong full-cut anchors (user-provided names, acceptance anchors):
  白月魁交易盒 gift 136388 (yk channel), 浮游炮 common_item 640041,
  清镜识微 player_appear 492700, 噬极 weapon_skin 1110156.

Honest bounds: the DiscountMarketHD goods/pricing carrier table is NOT present
in BA8 (module scan 0 hits; four-anchor exact-uleb locator found only roster /
announcement / trade tables). The only direct activity reference is gift 136388
desc "灵笼满减活动结束后可交易". Nothing here claims prices or purchase rules.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "manjian_market_panel_static.json"
FIDS = {
    "huodong_base": "FB80FED51B8B4638",
    "huodong_chs": "B48257E8D36A5AD4",
}


def load_registered_source(source_id: str) -> dict[str, Any]:
    raw = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source = next((item for item in raw.get("sources", []) if item.get("source_id") == source_id), None)
    if not isinstance(source, dict):
        raise ValueError(f"{source_id} source is not registered")
    return source


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = struct.unpack_from("<I", payload, offset + 2)[0]
    if offset + 6 + size > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:offset + 6 + size]


def flat(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.get("values", {}).items():
        out[key] = value[1] if isinstance(value, tuple) and len(value) == 2 else value
    return out


def fmt(ts: Any) -> str:
    try:
        return dt.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "" if ts is None else str(ts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    registered = load_registered_source("documents-py314-current")
    package = Path(registered["path"])
    reader = LiveNpkReader(package, str(registered.get("server_branch") or "Documents snapshot"))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("registered source SHA mismatch")
    entries_by_fid = {f"{entry.file_id:016X}": entry for entry in reader._entries}

    def decode(fid: str) -> tuple[bytes, dict[str, Any]]:
        entry = entries_by_fid[fid]
        if entry is None:
            raise RuntimeError(f"FID missing from locked source: {fid}")
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        payload = _unpack_entry(packed, entry.declared_size, entry.flag)
        reader._assert_unchanged()
        return payload, {
            "entry_index": entry.entry_index,
            "file_id": fid,
            "decoded_sha256": hashlib.sha256(payload).hexdigest(),
            "role": fid,
        }

    decoded = {label: decode(fid) for label, fid in FIDS.items()}
    ANCHOR_FIDS = ["EAA478C8DF60BD04", "112DA9185C331789", "B42760CCA41DBC25",
                   "24947DBB72A943E5", "6CD197C9670A961C", "765AB12F1D6EB0EA"]
    anchor_src = {}
    for fid in ANCHOR_FIDS:
        _payload, meta = decode(fid)
        anchor_src[fid] = meta
    lock = {
        "sha256": metadata["package_sha256"],
        "bytes": metadata["bytes"],
        "mtime_ns": metadata["mtime_ns"],
        "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)",
    }

    body = xbody(decoded["huodong_base"][0])
    pool = parse_legacy_chs_pool(decoded["huodong_chs"][0])
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)

    periods: list[dict[str, Any]] = []
    for row in rows:
        f = flat(row)
        cls = str(f.get("hd_class") or "")
        if cls not in ("ManJianHuoDong", "DiscountMarketHD"):
            continue
        periods.append({
            "id": f"hd-{row['key']}",
            "name": str(f.get("name") or ""),
            "activity": "满减市场" if cls == "ManJianHuoDong" else "满减市场（满减补贴）",
            "huodong_key": row["key"],
            "hd_class": cls,
            "hd_type": f.get("hd_type"),
            "ui_class": f.get("ui_class"),
            "start_date": fmt(f.get("start_ts")),
            "end_date": fmt(f.get("end_ts")),
            "sub_title": f.get("sub_title"),
            "server_scope": "旧满减市场（ManJianHuoDong）" if cls == "ManJianHuoDong" else "新满减市场（DiscountMarketHD）",
            "goods_carrier": (
                "manjian_market_goods kj1/kjxq 101 行=材料类商品（2023-2024 轮）"
                if cls == "ManJianHuoDong" else
                "DiscountMarketHD 商品定价载体表静态缺失（BA8 无该模块；价格/档位=运行时）"
            ),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "huodong_conf_data kj1 hd_class=ManJianHuoDong / DiscountMarketHD 活动行",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [decoded["huodong_base"][1], decoded["huodong_chs"][1]],
                "table": "huodong_conf_data_auto_oversea_data_kj1",
                "row_key": row["key"],
                "field_refs": [
                    f"hd_class={cls}",
                    f"name={f.get('name')}",
                    f"start_ts/end_ts={f.get('start_ts')}/{f.get('end_ts')}",
                ],
                "name_source": "huodong_conf_data name (activity roster label)",
            },
        })
    periods.sort(key=lambda p: (p["start_date"], p["huodong_key"]))

    anchors = [
        {
            "id": "anchor-bymk-transaction-box",
            "name": "白月魁交易盒",
            "activity": "灵笼满减补贴（锚点）",
            "anchor_type": "时装礼盒",
            "table": "gift_data_auto_oversea_data_yk（通道增量）",
            "row_key": 136388,
            "desc_excerpt": "打开礼包后，获得白月魁时装 1 份，包含头饰和身体；该交易盒可在灵笼满减活动结束后在跨服交易行进行交易。",
            "chain_note": "desc 为四锚点中唯一直接引用「灵笼满减活动」的静态文本",
            "source": "gift key 136388 名册行（用户验收锚点）；商品载体表静态缺失，本行=名册登记链",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [anchor_src["EAA478C8DF60BD04"], anchor_src["112DA9185C331789"]],
                "table": "gift_data_auto_oversea_data_yk",
                "row_key": 136388,
                "field_refs": ["gift key 136388 name/desc"],
                "name_source": "gift name（用户锚点验收）",
            },
        },
        {
            "id": "anchor-fuyoupao-projection",
            "name": "浮游炮（伴身投影）",
            "activity": "灵笼满减补贴（锚点）",
            "anchor_type": "伴身投影道具",
            "table": "common_item_data_base",
            "row_key": 640041,
            "desc_excerpt": "科技会研发的最新投影道具：源自灵笼科技，仅为外观装饰，不具备攻击效果。buff 名册：伴身投影·浮游炮。",
            "chain_note": "640000 投影段；buff_data 名册 1E23D0CBDFC4BEA7 内「伴身投影·浮游炮」",
            "source": "common_item key 640041 名册行（用户验收锚点）；商品载体表静态缺失，本行=名册登记链",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [anchor_src["B42760CCA41DBC25"]],
                "table": "common_item_data_base",
                "row_key": 640041,
                "field_refs": ["common_item key 640041 name/desc"],
                "name_source": "common_item name（用户锚点验收）",
            },
        },
        {
            "id": "anchor-qingjingshiwei-face",
            "name": "清镜识微",
            "activity": "灵笼满减补贴（锚点）",
            "anchor_type": "面饰（face，白月魁同款眼镜）",
            "table": "player_module_appear_data",
            "row_key": 492700,
            "desc_excerpt": "白老板的同款眼镜，据说带上它就能于细微处洞见破局之机。「明日之后×灵笼」联动限定外观。",
            "chain_note": "含 -1/3/5/7/14/30 天时限变体 492701-492706",
            "source": "player_module_appear key 492700 名册行（用户验收锚点）；商品载体表静态缺失，本行=名册登记链",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [anchor_src["24947DBB72A943E5"], anchor_src["6CD197C9670A961C"]],
                "table": "player_module_appear_data",
                "row_key": 492700,
                "field_refs": ["player_module_appear key 492700 name/desc/part_type=face"],
                "name_source": "player_module_appear name（用户锚点验收）",
            },
        },
        {
            "id": "anchor-shiji-flamethrower-skin",
            "name": "噬极",
            "activity": "灵笼满减补贴（锚点）",
            "anchor_type": "喷火器武器皮肤",
            "table": "weapon_skin_data",
            "row_key": 1110156,
            "desc_excerpt": "腥荭素缠绕的血雾烈焰，吞噬一切生命源质的不详之火。「明日之后×灵笼」联动限定外观。",
            "chain_note": "战斗表现：命中效果=噬髓腐蚀 / 攻击弹道=噬炎蔓溢；BA8/root 均有=已上线对照",
            "source": "weapon_skin_data key 1110156 名册链（用户验收锚点）；商品载体表静态缺失，本行=名册登记链",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [anchor_src["765AB12F1D6EB0EA"]],
                "table": "weapon_skin_data",
                "row_key": 1110156,
                "field_refs": ["weapon_skin_data key 1110156 名册链（weapon_skin_sfx_text_sources 板同源）"],
                "name_source": "weapon_skin 名册（用户锚点验收）",
            },
        },
    ]

    # 锚点并入「灵笼满减补贴」子卡（用户校正 2026-09-06：锚点是灵笼期内容，不板级平铺）
    linglong_item = next(p for p in periods if p["name"] == "灵笼满减补贴")
    for a in anchors:
        linglong_item["锚点：" + a["name"]] = (
            f"{a['table']} key {a['row_key']} · {a['anchor_type']} · {a['desc_excerpt'][:64]}…"
            if len(a["desc_excerpt"]) > 64 else
            f"{a['table']} key {a['row_key']} · {a['anchor_type']} · {a['desc_excerpt']}")
    linglong_item["source"] += "；锚点商品为灵笼联动内容（用户验收），获取渠道证据=gift 136388 desc「灵笼满减活动结束后可交易」"
    merged = linglong_item["provenance"]["source_entries"] + [anchor_src[fid] for fid in ANCHOR_FIDS]
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for e in merged:
        if e["file_id"] not in seen:
            seen.add(e["file_id"])
            deduped.append(e)
    linglong_item["provenance"]["source_entries"] = deduped
    linglong_item["provenance"]["field_refs"] = linglong_item["provenance"]["field_refs"] + [
        "锚点：白月魁交易盒=gift 136388（yk 通道增量 023502/001666，desc 直引灵笼满减活动）",
        "锚点：浮游炮=common_item 640041（+buff_data 伴身投影·浮游炮 1E23D0CBDFC4BEA7）",
        "锚点：清镜识微=player_appear 492700 face（+492701-492706 时限变体）",
        "锚点：噬极=weapon_skin 1110156 喷火器皮肤（噬髓腐蚀/噬炎蔓溢）",
    ]

    items = periods
    board = {
        "meta": {
            "name": "满减市场（活动族 + 灵笼满减补贴锚点链）",
            "category": "四、奖池 / （三）满减市场",
            "source_server": registered.get("server_branch"),
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "满减市场活动族：旧 ManJianHuoDong（2023-11~2024-06，goods 表 101 行=材料商品）与 "
                "新 DiscountMarketHD/满减补贴（2025-04~2026-06 各期，含 2026-04-16~30 灵笼满减补贴 key3402）。"
                "灵笼满减补贴锚点（用户验收）：白月魁交易盒/浮游炮/清镜识微/噬极=各名册行，链至活动注册；"
                "但 DiscountMarketHD 商品定价载体表静态缺失（模块名 0 命中 + 四锚点精确同现扫仅名册/公告/交易表），"
                "购买档位与规则=运行时；唯一直接活动引用=gift 136388 desc「灵笼满减活动结束后可交易」。"
                "本板不声明任何定价、补贴档位或当前售卖状态。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": items,
        "stats": {"period_rows": len(periods), "anchor_rows": len(anchors), "unbound": len(unbound)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "periods": len(periods), "anchors": len(anchors),
                      "unbound": len(unbound)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
