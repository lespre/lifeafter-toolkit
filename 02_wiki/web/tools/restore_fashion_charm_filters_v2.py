# -*- coding: utf-8 -*-
"""恢复人物时装的魅力值 / 性别 / 筛选轴（fashion_wardrobe 重建后这些字段丢失）。

- 魅力值：fashion_data.charm_value，按 row_keys（含时限变体 key）回填
- 性别：player_appear_data.model_name 里的 _f_ / _m_ 标记，按 model_ids 回填
- 筛选：part_bucket（数组）/ has_permanent / status_label / gender
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CDATA = PROJ / "01_索引与产物/41_还原树/pe_20261020/com/cdata"
TABLE = CDATA / "fashion_data.py"
BOARD = WEB / "data/boards/fashion_wardrobe.json"

BUCKET = {
    "cloth": "衣服", "hat": "头饰", "bag": "背包", "suit": "整套",
    "face": "面饰", "pendant": "挂饰", "proj": "投影", "light": "光源",
    "hair": "发饰", "整套": "整套", "面饰": "面饰", "挂饰": "挂饰",
    "投影": "投影", "光源": "光源", "荧光棒": "光源",
}
PART_CN = dict(BUCKET)


def _rows(path: pathlib.Path):
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return [], None
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = path.with_name(path.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                               resolve_jumps=False, lenient=True)[0]
    return rows, pool


def _val(v):
    return v[1] if isinstance(v, tuple) else v


def charm_map() -> dict:
    rows, _ = _rows(TABLE)
    out = {}
    for r in rows:
        v = r.get("values", {})
        cv, lv = _val(v.get("charm_value")), _val(v.get("level"))
        out[str(r.get("key"))] = {
            "charm_value": cv if isinstance(cv, (int, float)) else None,
            "level": lv if isinstance(lv, int) else None,
        }
    return out


def gender_map() -> dict:
    p = CDATA / "player_appear_data.py"
    if not p.exists():
        return {}
    rows, _ = _rows(p)
    out = {}
    for r in rows:
        mn = _val(r.get("values", {}).get("model_name"))
        if not isinstance(mn, str):
            continue
        if "_f_" in mn or "_female" in mn:
            out[str(r.get("key"))] = "女"
        elif "_m_" in mn or "_male" in mn:
            out[str(r.get("key"))] = "男"
    return out


def part_bucket(v) -> list:
    v = str(v or "")
    if v in BUCKET:
        return [BUCKET[v]]
    if "/" in v:
        parts, seen = [], set()
        for x in v.split("/"):
            b = BUCKET.get(x.strip())
            if b and b not in seen:
                seen.add(b)
                parts.append(b)
        if parts:
            return parts
    return ["其他"]


def part_cn(v) -> str:
    v = str(v or "")
    if v in PART_CN:
        return PART_CN[v]
    if "/" in v:
        return "+".join(PART_CN.get(x.strip(), x.strip()) for x in v.split("/"))
    return v or "未知"


def status_label(it) -> str:
    ic = str(it.get("icon_state") or "")
    if ic in ("有图", "已上架"):
        return "已上架"
    if "unresolved" in set(it.get("status_tags") or []):
        return "待确认"
    if ic in ("未下发", "无图标字段"):
        return "未下发"
    return "未知"


def variant_keys(it) -> list:
    out = []
    for v in (it.get("time_limited_variants") or []):
        if isinstance(v, dict):
            k = v.get("row_key") or v.get("key")
            if k:
                out.append(str(k))
        elif isinstance(v, (str, int)):
            out.append(str(v))
    return out


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    cm, gm = charm_map(), gender_map()
    for it in d["items"]:
        if it.get("charm_value") is None:
            for k in [str(x) for x in (it.get("row_keys") or [])] + variant_keys(it):
                c = cm.get(k, {}).get("charm_value")
                if c is not None:
                    it["charm_value"] = c
                    break

        gl = []
        for mid in (it.get("model_ids") or []):
            g = gm.get(str(mid))
            if g and g not in gl:
                gl.append(g)
        if gl:
            it["gender"] = "/".join(gl)

        it["part_label"] = part_cn(it.get("part"))
        it["part_bucket"] = part_bucket(it.get("part"))
        it["has_permanent"] = not bool(it.get("time_limited_variants"))
        it["status_label"] = status_label(it)

    d.setdefault("meta", {}).pop("filters", None)
    d["meta"]["notes"] = ((d["meta"].get("notes") or "")
                          + " ｜ 魅力值=fashion_data.charm_value；性别=player_appear_data.model_name 标记")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    n = len(d["items"])
    print("魅力值", sum(1 for i in d["items"] if i.get("charm_value") is not None), "/", n,
          "｜ 性别", sum(1 for i in d["items"] if i.get("gender")), "/", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
