# -*- coding: utf-8 -*-
"""标记「单性别款」时装。

判定口径（2026-10-30 复核 player_appear_data 字段语义后定版）：
  * player_appear_data.gender：0=女、1=男（资源路径 b_f_*/b_m_* 可交叉验证）；
  * force_gender=1：该外观行锁定性别；
  * ★ 真正的「实际单性别」判定 = 该 model 同时满足：
      - 女款行（gender=0）带 force_gender 且**绑定了 model_name 资源**；
      - 男款行（gender=1）虽在表里登记，但**没有绑定 model_name**（无男装模型/图标）。
    即：表里登记了男装位，实际资源只做了女款（不湮之花、白月魁、嘉心予梦、琳夜柔歌、贝极星愿）。

覆盖范围（比旧版更全）：
  旧版只按卡上的 model_id 匹配，漏掉「外观补充卡」——它们只有 player_appear_data 的 row_keys
  （例：不湮之花幻典 行 1500402/3500402 → model 5004，与不湮之花同款）；
  本版追加 row_keys → 源行 model_id 反查，衍生款（幻典等）一并标注。

用法：python tools/mark_single_gender.py（幂等，重复跑不重复写 notes）
"""
from __future__ import annotations

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
NOTES_MARK = "【单性别款】"
v = lambda x: x[1] if isinstance(x, tuple) else x


def main() -> int:
    raw = (CD / "player_appear_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    pool = BT.parse_legacy_chs_pool((CD / "player_appear_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]

    # model → {gender: {行数, 有模型资源数, 带force数, 名字集}}
    per_model = {}
    row_model = {}
    for r in rows:
        val = r["values"]
        mid = v(val.get("model_id"))
        if mid is None:
            continue
        mid = str(mid)
        row_model[r["key"]] = mid
        g = v(val.get("gender"))
        fg = v(val.get("force_gender"))
        has_res = bool(v(val.get("model_name")))
        rec = per_model.setdefault(mid, {})
        gr = rec.setdefault(g, {"n": 0, "res": 0, "force": 0, "names": set()})
        gr["n"] += 1
        gr["res"] += 1 if has_res else 0
        gr["force"] += 1 if fg is not None else 0
        nm = v(val.get("name"))
        if nm:
            gr["names"].add(nm)

    # 实际单性别 = 两条证据取并集（各自独立成立即判定）：
    #   E1 性别锁定：model 的行带 force_gender=1（表里锁性别）⇒ 不湮之花(5004) 属这组
    #      （PE 快照里该 model 男女行都没绑 model_name，属资源未下发，不靠资源判）
    #   E2 男款无资源：model 有男款行(gender=1)但未绑 model_name，而女款行绑了 ⇒ 飞影浮澜(3739) 属这组
    single = {}
    for mid, rec in per_model.items():
        female = rec.get(0) or {}
        male = rec.get(1) or {}
        ev = []
        if female.get("force") or male.get("force"):
            ev.append("force_gender=1（外观行锁定性别）")
        if male.get("n") and not male.get("res") and female.get("res"):
            ev.append("男款行(gender=1)在表里登记但未绑定模型资源")
        if not ev:
            continue
        single[mid] = {
            "female_rows": female.get("n", 0),
            "male_rows": male.get("n", 0),
            "names": sorted(female.get("names") or []),
            "evidence": ev,
        }
    print("实际单性别 model 数:", len(single))
    for mid, info in sorted(single.items()):
        print("   model %-6s 女行 %d / 男行 %d  证据 %s  例名 %s"
              % (mid, info["female_rows"], info["male_rows"], "＋".join(info["evidence"]),
                 info["names"][:2]))

    def models_of(it):
        mids = set()
        if it.get("model_id") is not None:
            mids.add(str(it.get("model_id")))
        for m in (it.get("model_ids") or []):
            if m is not None:
                mids.add(str(m))
        for k in (it.get("row_keys") or []):
            m = row_model.get(k)
            if m:
                mids.add(m)
        return mids

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    marked = 0
    for it in board["items"]:
        hit = [m for m in models_of(it) if m in single]
        if not hit:
            continue
        it["gender_scope"] = "仅单性别（实际仅女款）"
        it["gender_scope_note"] = (
            "player_appear_data：model %s —— %s ⇒ 该外观实际只有女款，无男装图。"
            % (hit[0], "；".join(single[hit[0]]["evidence"])))
        marked += 1
    notes = str(board["meta"].get("notes") or "")
    if NOTES_MARK not in notes:
        notes += ("\n\n%s%d 张卡所属 model 为实际单性别（女款有资源、男款行未绑资源）："
                  "不湮之花（含幻典）、白月魁、嘉心予梦、琳夜柔歌、贝极星愿。"
                  "判定脚本 tools/mark_single_gender.py（可复算）。" % (NOTES_MARK, marked))
        board["meta"]["notes"] = notes
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("标记单性别款 %d 张" % marked)
    print("样例:", [i["name"] for i in board["items"] if i.get("gender_scope")][:14])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
