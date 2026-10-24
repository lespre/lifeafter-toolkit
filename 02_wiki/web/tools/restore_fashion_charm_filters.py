# -*- coding: utf-8 -*-
"""恢复人物时装的魅力值与筛选（fashion_wardrobe 重建后 meta.filters/字段丢失）。

做三件事：
1. 从 fashion_data 解出 key → charm_value / level，按 row_keys 回填；
2. 由 status_tags 生成 status_label（上架状态筛选用）；
3. 重建 meta.filters（部位、上架状态）。
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TABLE = PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/fashion_data.py"
BOARD = WEB / "data/boards/fashion_wardrobe.json"


def gender_map() -> dict:
    """player_appear_data.model_name 里带 _f_ / _m_，据此得到 model_id → 性别。"""
    p = TABLE.with_name("player_appear_data.py")
    if not p.exists():
        return {}
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = p.with_name(p.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                                resolve_jumps=False, lenient=True)[0]
    out = {}
    import re as _re
    for r in rows:
        key = str(r.get("key"))
        mn = r.get("values", {}).get("model_name")
        mn = mn[1] if isinstance(mn, tuple) else mn
        if not isinstance(mn, str):
            continue
        if "_f_" in mn or "_female" in mn:
            out[key] = "女"
        elif "_m_" in mn or "_male" in mn:
            out[key] = "男"
    return out


def charm_map() -> dict:
    raw = TABLE.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = TABLE.with_name(TABLE.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                                resolve_jumps=False, lenient=True)[0]
    out = {}
    for r in rows:
        key = str(r.get("key"))
        v = r.get("values", {})
        cv = v.get("charm_value")
        if isinstance(cv, tuple):
            cv = cv[1]
        lv = v.get("level")
        if isinstance(lv, tuple):
            lv = lv[1]
        if isinstance(cv, (int, float)) or isinstance(lv, int):
            out[key] = {"charm_value": cv if isinstance(cv, (int, float)) else None,
                        "level": lv if isinstance(lv, int) else None}
    return out


PART_CN = {
    "cloth": "衣服", "hat": "头饰", "bag": "背包", "cloth/hat": "衣服+头饰",
    "整套": "整套", "面饰": "面饰", "挂饰": "挂饰", "投影": "投影",
    "光源": "荧光棒", "荧光棒": "荧光棒", "light": "荧光棒", "suit": "整套",
}


def part_cn(v) -> str:
    v = str(v or "")
    if v in PART_CN:
        return PART_CN[v]
    if "/" in v:
        return "+".join(PART_CN.get(x, x) for x in v.split("/"))
    return v or "未知"


BUCKET = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "suit": "整套",
          "face": "面饰", "pendant": "挂饰", "proj": "投影", "light": "光源",
          "hair": "发饰", "整套": "整套", "面饰": "面饰", "挂饰": "挂饰",
          "投影": "投影", "光源": "光源", "荧光棒": "光源"}


def part_bucket(v) -> list:
    v = str(v or "")
    if v in BUCKET:
        return [BUCKET[v]]
    if "/" in v:
        parts, seen = [], set()
        for x in v.split("/"):
            b = BUCKET.get(x.strip())
            if b and b not in seen:
                seen.add(b); parts.append(b)
        if parts:
            return parts
    return ["其他"]


def status_label(tags) -> str:
    t = set(tags or [])
    if "on_sale" in t or "在售" in t:
        return "在售"
    if "off_sale" in t or "已下架" in t:
        return "已下架"
    if "unresolved" in t:
        return "待确认"
    return "未知"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    cm = charm_map()
    gm = gender_map()
    got = 0
    for it in d["items"]:
        keys = [str(k) for k in (it.get("row_keys") or [])]
        for k in keys:
            if k in cm:
                it["charm_value"] = cm[k]["charm_value"]
                if cm[k]["level"] is not None:
                    it.setdefault("level", cm[k]["level"])
                if it["charm_value"] is not None:
                    got += 1
                break
        it["part_label"] = part_cn(it.get("part"))
        it["part_bucket"] = part_bucket(it.get("part"))
        tlv = it.get("time_limited_variants")
        it["has_permanent"] = not bool(tlv)
        ic = str(it.get("icon_state") or "")
        if ic in ("有图", "已上架"):
            it["status_label"] = "已上架"
        elif ic in ("未下发", "无图标字段"):
            # 性别：按 model_ids 映射（男女都有就是 男/女）
        gl = []
        for mid in (it.get("model_ids") or []):
            g = gm.get(str(mid))
            if g and g not in gl:
                gl.append(g)
        if gl:
            it["gender"] = "/".join(gl)
        else:
            # 性别：按 model_ids 映射（男女都有就是 男/女）
        gl = []
        for mid in (it.get("model_ids") or []):
            g = gm.get(str(mid))
            if g and g not in gl:
                gl.append(g)
        if gl:
            it["gender"] = "/".join(gl)
    # 时装板自带筛选模组（部位多选/期限/图示/性别/排序），不再叠加 meta.filters，避免两套控件打架
    d.setdefault("meta", {}).pop("filters", None)
    d["meta"]["notes"] = (d["meta"].get("notes") or "") + " ｜ 魅力值取自 fashion_data.charm_value"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    n = len(d["items"])
    charm = sum(1 for i in d["items"] if i.get("charm_value") is not None)
    print("回填魅力值", got, "｜现覆盖", charm, "/", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
