# -*- coding: utf-8 -*-
"""用 all_equips_data（挂件作为「时装道具」的本体表）回填挂饰卡：魅力值 / 描述 / 品级，
并把特技说明换成特技定义表的权威文本。

═══════════════════════════════════════════════════════════════════════════
★ 结论先说（这是用户质疑「肯定还有别的表」的核实结果）

  挂件**作为时装道具**的本体表就是 `all_equips_data`：
      id / name / desc / icons / **_charm_value** / level / weapon_type …
  实测（见 `_bits/post__all_equips_data_auto_oversea_data_yk.py.bin`）：

      270000 蓝白猫咪    charm_value 10    level 3
      270058 赤焰栖梧    charm_value 200   level 4
      270121 心易俱乐部  charm_value 10    level 3

  但**这张表里没有任何特技字段**（字段清单里没有 special_effect / effect_ids 之类），
  所以「哪个挂件带哪个特技」只能从 `gift_data` 的挂饰礼盒 desc 里读到。

★ 数据来源

  1. `_bits/post__all_equips_data_auto_oversea_data_yk.py.bin`（热更增量清单，2227 行）
     → 只含**本次变更**的 14 个挂件（270xxx），能补 charm_value / desc / level
     ※ 全量 all_equips_data 在 PE 还原树是 MergedTableData 空壳，真实 _base/_inc/_del
       三张表不在树里、也在缺的 168 卷里 —— 这是覆盖率上不去的唯一原因。
  2. `equip_special_effect_data`（289 条特技定义）→ 用权威 desc 替换礼盒尾段截出来的粗糙文本

★ 用法
    python fill_pendant_from_all_equips.py --dry
    python fill_pendant_from_all_equips.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BITS = (PROJ / "01_索引与产物/10_索引/热更检测"
        / "post_update_20261015_213737_all_equips_cli/_bits")
AE_MAIN = BITS / "post__all_equips_data_auto_oversea_data_yk.py.bin"
AE_CHS = BITS / "post__all_equips_data_auto_oversea_data_yk_chs.py.bin"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLEAN_RE = re.compile(r"#c[0-9a-fA-F]{6}|#n|#r|#c")


def clean(s: str) -> str:
    return CLEAN_RE.sub("", s or "").replace("#", "").strip()


def gs(blob, pool, off, d=0):
    if d > 6:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    k, els = g
    o = []
    if k == 0x0B:
        for e in els:
            o += gs(blob, pool, e, d + 1)
    elif k == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                o.append(pool[e])
    return o


def val(v, blob, pool):
    if isinstance(v, tuple) and len(v) == 2:
        if str(v[1]).startswith("jump:"):
            try:
                return gs(blob, pool, int(str(v[1]).split(":")[1]))
            except Exception:
                return []
        return [v[1]]
    return [v]


def load_bin(main: pathlib.Path, chs: pathlib.Path):
    raw = main.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    cb = chs.read_bytes()
    cat = cb.find(b"x{")
    pool = BT.parse_legacy_chs_pool(cb[cat - 6:] if cat > 6 else cb)
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    out = []
    for r in rows:
        out.append({"key": r["key"], **{k: val(v, blob, pool) for k, v in r["values"].items()}})
    return out


def first(rec: dict, k: str, default=None):
    v = rec.get(k)
    if isinstance(v, list) and v:
        return v[0]
    return default


def build_skill_dict() -> dict:
    """equip_special_effect_data：特技名 → 权威说明"""
    p = CD / "equip_special_effect_data.py"
    if not p.is_file():
        return {}
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return {}
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    cp = CD / "equip_special_effect_data_chs.py"
    pool = []
    if cp.is_file():
        try:
            pool = BT.parse_legacy_chs_pool(cp.read_bytes())
        except Exception:
            pool = []
    try:
        rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    except Exception:
        return {}
    out = {}
    for r in rows:
        nm = first({"x": val(r["values"].get("name"), blob, pool)}, "x")
        ds = first({"x": val(r["values"].get("desc"), blob, pool)}, "x")
        if isinstance(nm, str) and nm:
            out[nm] = clean(ds or "")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    if not AE_MAIN.is_file():
        print("缺 %s" % AE_MAIN)
        return 1
    ae = load_bin(AE_MAIN, AE_CHS)
    by_id, by_name = {}, {}
    for r in ae:
        iid = first(r, "id")
        nm = first(r, "name")
        if isinstance(iid, int) and 270000 <= iid <= 271999:
            by_id[iid] = r
            if isinstance(nm, str):
                by_name[nm] = r

    skills = build_skill_dict()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    st = {"挂饰卡": 0, "all_equips命中": 0, "魅力补上": 0, "描述更新": 0,
          "品级补上": 0, "特技说明优化": 0}
    hits = []
    for it in board["items"]:
        if (it.get("part_bucket") or [None])[0] != "挂饰":
            continue
        st["挂饰卡"] += 1
        nm = (it.get("name") or "").strip()
        # 按道具 id 匹配（最稳），退化为名字
        rec = None
        for x in (it.get("provenance", {}).get("icon_item_ids") or []):
            if x in by_id:
                rec = by_id[x]
                break
        if rec is None:
            rec = by_name.get(nm)
        if rec:
            st["all_equips命中"] += 1
            hits.append((nm, first(rec, "id")))
            cv = first(rec, "charm_value")
            ds = clean(first(rec, "desc") or "")
            lv = first(rec, "level")
            if isinstance(cv, int) and cv > 0:
                st["魅力补上"] += 1
                if not a.dry:
                    it["charm_value"] = cv
                    it.pop("charm_note", None)
                    it.setdefault("provenance", {})["charm_source"] = "all_equips_data.charm_value"
            if ds and (not it.get("desc") or it.get("desc") != ds):
                st["描述更新"] += 1
                if not a.dry:
                    it["desc"] = ds
                    it["desc_note"] = ("挂饰本体描述（all_equips_data#%s）" % first(rec, "id"))
            if isinstance(lv, int) and lv > 0 and it.get("grade_level") != lv:
                st["品级补上"] += 1
                if not a.dry:
                    it["grade_level"] = lv
                    it["grade_levels"] = [lv]
                    it["grade_source"] = "all_equips_data.level"

        # 特技说明换成定义表权威文本
        eff = it.get("effect") or {}
        sks = eff.get("skills") or []
        if sks and skills:
            better = []
            changed = False
            for s in sks:
                if s in skills and skills[s]:
                    if not eff.get("skill_desc") or s not in (eff.get("skill_desc") or ""):
                        better.append("%s：%s" % (s, skills[s]))
                        changed = True
                    else:
                        better.append("%s：%s" % (s, skills[s]))
            if better and not a.dry:
                eff = dict(eff)
                eff["skill_desc"] = " ".join(better)
                eff["skill_desc_source"] = "equip_special_effect_data"
                it["effect"] = eff
                parts = [eff.get("proficiency")
                         or "战斗、制作、采集熟练度获取 +5%（通用规则）"]
                parts.append("特技：" + "、".join(sks))
                parts.append(eff["skill_desc"])
                it["effect_text"] = " ｜ ".join(parts)
                it["effect_source"] = (str(it.get("effect_source") or "")
                                       + " + equip_special_effect_data")
            if changed:
                st["特技说明优化"] += 1

    print("=== all_equips 回填 ===")
    for k, v in st.items():
        print("  %-12s %d" % (k, v))
    print("  命中挂件：", hits[:16])
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_ae" % ts))
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_ae" % ts))
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s" % BOARD.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
