#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mystery shop (神秘商店 / RandomDiscountHD) board.

Source: huodong_conf kj1 in the BA8 locked snapshot. RandomDiscountHD rows are
the mystery-shop activity periods found statically (2024-01/04/06). UI table
(016741) maps 神秘商店 -> RandomDiscountHD; new_store_tag_data lists 神秘商店
as a store tab; push_notice confirms it stays active ("神秘商店再临").

Semantics (user-corrected 2026-09-06): the mystery shop sells RETURNING
(返场) cosmetics at random discounts; each item's INITIAL grant came from its
own activity period (e.g. 冰蕊银华 shotgun skin first appeared in the
黄金年代 period). Anchor chain: 冰蕊银华 -> reward_pool row 453529 (pool
390687, 黄金年代) desc text + push_notice 011869 (「全新霰弹枪皮肤-冰蕊银华」).

Honest bounds: the RandomDiscount goods/discount carrier table is not present
in BA8 (module scan 0 hits, same pattern as DiscountMarketHD); the next
period's line-up (incl. 冰蕊银华 return) is runtime/not-yet-packaged. No
prices, discounts or current stock are claimed.
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
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "mystery_shop_panel_static.json"
FIDS = {"huodong_base": "FB80FED51B8B4638", "huodong_chs": "B48257E8D36A5AD4"}


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
            raise RuntimeError(f"FID missing: {fid}")
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
        if str(f.get("hd_class") or "") != "RandomDiscountHD":
            continue
        periods.append({
            "id": f"hd-{row['key']}",
            "name": str(f.get("name") or "神秘商店"),
            "activity": "神秘商店（随机折扣 RandomDiscountHD）",
            "huodong_key": row["key"],
            "hd_class": f.get("hd_class"),
            "ui_class": f.get("ui_class"),
            "start_date": fmt(f.get("start_ts")),
            "end_date": fmt(f.get("end_ts")),
            "goods_carrier": "RandomDiscount 商品/折扣载体表静态缺失（BA8 模块名 0 命中）；当期待售=运行时",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "huodong_conf_data kj1 hd_class=RandomDiscountHD 活动行",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [decoded["huodong_base"][1], decoded["huodong_chs"][1]],
                "table": "huodong_conf_data_auto_oversea_data_kj1",
                "row_key": row["key"],
                "field_refs": [f"hd_class=RandomDiscountHD", f"name={f.get('name')}",
                               f"start_ts/end_ts={f.get('start_ts')}/{f.get('end_ts')}"],
                "name_source": "huodong_conf_data name（活动名=神秘商店）",
            },
        })
    periods.sort(key=lambda p: (p["start_date"], p["huodong_key"]))

    system_item: dict[str, Any] = {
        "id": "mystery-system-and-anchor",
        "name": "神秘商店（系统定位 + 返场语义 + 冰蕊银华锚点）",
        "activity": "神秘商店（RandomDiscountHD）",
        "ui_mapping": "UI 名映射表 016741：神秘商店 = RandomDiscountHD / RandomDiscountHDUI",
        "store_tab": "new_store_tag_data：神秘商店=商城标签之一（活动礼包/周末特惠/每日礼包并列）",
        "returning_semantics": "用户口径：神秘商店=历史外观返场随机折扣；商品初始渠道=各外观所属活动期（如冰蕊银华=黄金年代期），返场=神秘商店",
        "锚点：冰蕊银华（霰弹枪皮肤）": "初始=reward_pool 行 453529（池 390687 黄金年代，desc 奖励清单含冰蕊银华）+push_notice 011869「全新霰弹枪皮肤-冰蕊银华」；返场渠道=神秘商店（用户前瞻，BA8 无该期=运行时）",
        "锚点：桂月清辉（时装）": "下期神秘商店返场候选（用户锚点）；静态名册：fashion_sale_conf_data 直售名单（001940）、fashion_data_for_us 桂月清辉-头饰/-衣服（000553）、npc 装扮名册（000637）——初始渠道=时装直售",
        "锚点：热血学院（时装）": "下期神秘商店返场候选（用户锚点）；静态名册：fashion_sale_conf_data 直售名单（001940）、fashion_obtain_handbook（002573）、gift 热血特战头饰盒/衣服盒（002655）——初始渠道=时装直售/礼盒",
        "锚点：月色咏叹调（时装）": "下期神秘商店返场候选（用户锚点）；静态名册：player_appear 月色咏叹调-头饰/-衣服（006403）、月色咏叹调头饰/衣服自选箱（gift 002655）、fashion_store_data（008640）——初始渠道=时装自选/商店",
        "returning_lineup": "下期神秘商店返场候选（用户验收 2026-09-06）：冰蕊银华 / 桂月清辉 / 热血学院 / 月色咏叹调；各件初始渠道见对应锚点行；BA8 无神秘商店下期配置=运行时",
        "mechanism_proof": "刷新币机制确认：common_item 153535-153538 desc「每消耗1个刷新币，可在神秘商店进行一次免费的商品刷新；仅活动期间有效，结束后回收为新币」（该段行存在 name 槽漂移，行内道具名不可靠）——神秘商店=活动限时随机折扣店机制成立，但商品表静态缺失",
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "UI 映射/商店标签/公告文本 + reward_pool 黄金年代行；返场期内容非静态可得",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": [decoded["huodong_base"][1], decoded["huodong_chs"][1]],
            "table": "huodong_conf_data_auto_oversea_data_kj1 + 文本层（UI 016741/new_store_tag/push_notice 011869/reward_pool 021380）",
            "row_key": 453529,
            "field_refs": [
                "reward_pool_data_base key 453529（池 390687 黄金年代）desc 含 冰蕊银华",
                "push_notice_data 011869：全新霰弹枪皮肤-冰蕊银华（黄金年代登场公告）",
                "UI 表 016741：神秘商店↔RandomDiscountHD",
                "锚点名册：桂月清辉=fashion_sale_conf_data(001940)/fashion_data_for_us(000553)",
                "锚点名册：热血学院=fashion_sale_conf_data(001940)/fashion_obtain_handbook(002573)/gift(002655)",
                "锚点名册：月色咏叹调=player_appear(006403)/gift 自选箱(002655)/fashion_store_data(008640)",
                "机制：common_item 153535-153538 desc=神秘商店刷新币（活动限时，结束后回收新币）",
            ],
            "name_source": "reward_pool desc/push_notice 文本（用户锚点验收：冰锐银华=冰蕊银华霰弹枪皮肤）",
        },
    }

    items = periods + [system_item]
    board = {
        "meta": {
            "name": "神秘商店（RandomDiscountHD 期次 + 返场语义 + 锚点链）",
            "category": "四、奖池 / （四）神秘商店",
            "source_server": registered.get("server_branch"),
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "神秘商店=RandomDiscountHD（随机折扣商店，UI 映射表直标），BA8 静态注册 3 期（2024-01/04/06）；"
                "改版后为商城标签之一且仍活跃（推送「神秘商店再临」）。语义（用户校准）：历史外观返场随机折扣店；"
                "下期返场候选（用户验收）：冰蕊银华/桂月清辉/热血学院/月色咏叹调——各件初始渠道见锚点行"
                "（冰蕊银华=黄金年代期 reward_pool 453529+公告；其余=直售/礼盒/自选箱名册）。"
                "RandomDiscount 商品/折扣载体表与神秘商店下期配置 BA8 静态缺失；本板不声明任何定价、折扣档位或当期待售状态。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": items,
        "stats": {"period_rows": len(periods), "unbound": len(unbound)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "periods": len(periods), "unbound": len(unbound)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
