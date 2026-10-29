# -*- coding: utf-8 -*-
"""武器皮肤「战斗表现」正式名解析（可复用，读还原树，不依赖任何工作副本）。

数据：`<cdata>/weapon_skin_effect_show_data.py` + `_chs.py`
产物：`{skin_id: [{order, slot, slot_gun, slot_melee, name, icon, icon_melee, record_off}]}`

布局（实测确认，别拿通用解码器硬蹭）：
  file = [263B 容器头][x{][u32 body_len][body]
  body = [u32 nrows][u32 0][nrows*4 全零占位][blob]
  blob = [u32 de][data(4..de)][索引尾 @ de]
  索引尾 = 76 01 0b <bucket 数> <bucket 数 × 8B>
  行 @ row_start = 27 0b <n> <n × uleb 记录偏移>   ← n = 皮肤项数，顺序 = 面板顺序
  记录 @ off    = 86 0a <cold_icon><cold_label><hot_icon><hot_label><name><order>
                  07 02 01 <extra> 0b <jump>
  槽位名与名称同存一条记录（都是字串池索引）⇒ 映射不依赖任何顺序假设。
  cold = 冷兵器（近战，面板显示「挥砍特效」）；hot = 热兵器（枪械）。

对外：parse(cdata=None) -> (result, stats)；self_check(result) -> [问题]
CLI：python la.py skin fx-names [--out ...] [--cdata ...] ／ python la.py skin check
"""
from __future__ import annotations

import os
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
_CORE = REPO / "00_规范与工具/工具/工具库/00_共享核心"
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))

from toolkit_core import bindict_table as BT  # noqa: E402

TABLE = "weapon_skin_effect_show_data"


def resolve_cdata(explicit: str | Path | None = None) -> Path:
    """定位 cdata 目录：显式参数 → LA_CDATA → profiles.yml → 常见树布局。"""
    def ok(p: Path) -> bool:
        return (p / (TABLE + ".py")).is_file() and (p / (TABLE + "_chs.py")).is_file()

    if explicit:
        p = Path(explicit)
        if not ok(p):
            raise FileNotFoundError("--cdata 下缺 %s.py / _chs.py：%s" % (TABLE, p))
        return p
    env = os.environ.get("LA_CDATA")
    if env and ok(Path(env)):
        return Path(env)

    tried: list[str] = []
    # profiles.yml 是权威映射（sources.<pe|pc|documents>.cdata 为相对项目根路径）
    prof = REPO / "profiles.yml"
    if prof.is_file():
        try:
            import yaml  # 可选依赖，没有就跳过

            cfg = yaml.safe_load(prof.read_text(encoding="utf-8")) or {}
            src = os.environ.get("LA_SOURCE") or cfg.get("source") or "pe"
            rel = ((cfg.get("sources") or {}).get(src) or {}).get("cdata")
            if rel:
                p = REPO / rel
                tried.append(str(p))
                if ok(p):
                    return p
        except Exception:  # noqa: BLE001
            pass

    for rel in ("01_索引与产物/41_还原树/pe/配置/com/cdata",
                "01_索引与产物/41_还原树/com/cdata"):
        p = REPO / rel
        tried.append(str(p))
        if ok(p):
            return p

    try:
        from toolkit_core.paths import cdata_dir

        p = Path(cdata_dir())
        tried.append(str(p))
        if ok(p):
            return p
    except Exception:  # noqa: BLE001
        pass

    raise FileNotFoundError(
        "找不到 %s.py。试过：\n  %s\n用 --cdata 指定目录，或设 LA_CDATA。" % (TABLE, "\n  ".join(tried)))


def decode(raw: bytes, pool: list) -> tuple[dict, dict]:
    at = raw.find(b"x{")
    if at < 0:
        raise ValueError("找不到 x{ 帧：不是预期容器")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    nrows, reserved = struct.unpack_from("<II", body, 0)
    if reserved != 0:
        raise ValueError("body 保留位非 0（%d）：布局变了" % reserved)
    blob = body[8 + 4 * nrows:]
    de = struct.unpack_from("<I", blob, 0)[0]
    if blob[de:de + 3] != b"\x76\x01\x0b":
        raise ValueError("索引尾不是 76 01 0b：%s" % blob[de:de + 4].hex())

    records: dict[int, dict] = {}
    for off in range(4, de - 16):
        if blob[off] != 0x86 or blob[off + 1] != 0x0A:
            continue
        try:
            q = off + 2
            vals = []
            for _ in range(6):
                v, q = BT.uleb(blob, q, de)
                vals.append(v)
            if blob[q:q + 3] != b"\x07\x02\x01":
                continue
            q += 3
            extra, q = BT.uleb(blob, q, de)
            if blob[q] != 0x0B:
                continue
            q += 1
            jump, q = BT.uleb(blob, q, de)
        except (ValueError, IndexError):
            continue
        if not all(0 <= v < len(pool) for v in vals):
            continue
        ci, cl, hi, hl, name, order = vals
        records[off] = dict(off=off, cold_icon=ci, cold_label=cl, hot_icon=hi,
                            hot_label=hl, name=name, order=order, extra=extra, jump=jump)

    if not records:
        raise ValueError("0 条 86 0a 记录：布局或字串池不匹配")

    starts = sorted(records)
    result: dict[str, list] = {}
    delta = Counter()
    for key, row_start in BT.parse_index(blob):
        if blob[row_start] != 0x27:
            raise ValueError("行起点不是 0x27（skin=%s）" % key)
        kind, n = blob[row_start + 1], blob[row_start + 2]
        if kind != 0x0B:
            raise ValueError("组类型不是 0x0b（skin=%s kind=%#x）" % (key, kind))
        q = row_start + 3
        elems = []
        for _ in range(n):
            v, q = BT.uleb(blob, q, de)
            elems.append(v)
        items = []
        for pos, e in enumerate(elems, 1):
            cand = [r for r in starts if 0 <= e - r <= 12]
            if len(cand) != 1:
                raise ValueError("元素 %d 无法唯一命中记录（skin=%s 候选=%s）" % (e, key, cand))
            rec = records[cand[0]]
            delta[e - cand[0]] += 1
            items.append({
                "order": pos,
                "slot": pool[rec["hot_label"]],
                "slot_gun": pool[rec["hot_label"]],
                "slot_melee": pool[rec["cold_label"]],
                "name": pool[rec["name"]],
                "icon": pool[rec["hot_icon"]],
                "icon_melee": pool[rec["cold_icon"]],
                "record_off": rec["off"],
            })
        result[str(key)] = items

    stats = {
        "skins": len(result),
        "items": sum(len(v) for v in result.values()),
        "records": len(records),
        "elem_delta": dict(delta),
        "per_skin": dict(Counter(len(v) for v in result.values())),
        "chs_strings": len(pool),
    }
    return result, stats


def parse(cdata: str | Path | None = None) -> tuple[dict, dict]:
    cd = resolve_cdata(cdata)
    raw = (cd / (TABLE + ".py")).read_bytes()
    pool = BT.parse_legacy_chs_pool((cd / (TABLE + "_chs.py")).read_bytes())
    data, stats = decode(raw, pool)
    stats["cdata"] = str(cd)
    return data, stats


def self_check(result: dict) -> list[str]:
    """结构自洽检查（不依赖人工真值）。返回问题清单，空 = 通过。"""
    problems = []
    dup = [k for k, v in result.items() if len({x["slot"] for x in v}) != len(v)]
    if dup:
        problems.append("同一皮肤内重复槽位：%s" % dup[:5])
    empty = [k for k, v in result.items() if any(not x.get("name") for x in v)]
    if empty:
        problems.append("有项缺名称：%s" % empty[:5])
    slots = {x["slot"] for v in result.values() for x in v}
    names = {x["name"] for v in result.values() for x in v}
    cross = sorted(slots & names)
    if cross:
        problems.append("槽位名与特效名交叉（可能串味）：%s" % cross[:5])
    return problems


if __name__ == "__main__":
    d, st = parse()
    print("皮肤 %d ｜ 表现项 %d ｜ 记录 %d" % (st["skins"], st["items"], st["records"]))
    print("每皮肤项数", st["per_skin"])
    print("自检", self_check(d))
