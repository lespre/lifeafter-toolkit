# -*- coding: utf-8 -*-
r"""奖池板归一管线（幂等）：补图脚本按旧快照写回后，用它把后面的修正全部重放。

顺序：
 1) 家族改名（4 个）
 2) 按 hd_class 归族（huodong → 家族）
 3) 关键词归族（无人机/典藏/惠选/礼盒/芯片/核芯）
 4) 其它抽奖活动 → 未归类（广播名单），并做同名合并（跳过芯片/返场型）
 5) 重建自选保底期次（含返场标注 + 随机/自选保底模式）
 6) 重建限定芯片时间线 + 锚点
 7) 正式名优先（广播简称进 alias / note_internal）
 8) 剔除 share_reward 配置 id
 9) 期内去重 + 计数回填
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
PY = str(PROJ / ".venv/Scripts/python.exe")
TOOLS = WEB / "tools"

RENAME = {"多时装抽奖": "自选保底奖池", "纯外观抽奖": "不放回抽奖",
          "幻彩典藏": "大版本奖池", "载具抽奖": "无人机奖池"}
RULES = [(r"无人机", "无人机奖池"), (r"典藏|幻彩|大版本", "大版本奖池"),
         (r"惠选|集市|商店|特卖|轮换", "商店轮换"), (r"礼盒|宝箱|福袋", "礼盒宝箱抽奖"),
         (r"芯片", "限定芯片"), (r"核芯|异变", "核芯抽奖"), (r"寻宝|羊狼", "羊狼寻宝")]
SKIP_MERGE = {"BeltChipSpecialLottery", "MultiOptional"}


def run(tool: str) -> None:
    p = TOOLS / tool
    if not p.is_file():
        print("  跳过（不存在）", tool)
        return
    r = subprocess.run([PY, "-u", str(p)], cwd=str(WEB), capture_output=True, text=True)
    out = (r.stdout or "").strip().splitlines()
    print(" ", tool, "→", out[-1] if out else ("rc=%d" % r.returncode))


def main() -> int:
    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))

    # 1) 改名
    n = 0
    for per in d["periods"]:
        if per.get("family") in RENAME:
            per["family"] = RENAME[per["family"]]
            n += 1
    for it in d["items"]:
        if it.get("family") in RENAME:
            it["family"] = RENAME[it["family"]]
    print("1) 改名", n)

    # 3) 关键词归族（先做，避免被 hd_class 覆盖）
    m = 0
    for per in d["periods"]:
        if per.get("family") not in ("其它抽奖活动",):
            continue
        nm = str(per.get("activity_name") or "")
        for pat, fam in RULES:
            if re.search(pat, nm):
                per["family"] = fam
                m += 1
                break
    print("3) 关键词归族", m)

    # 4) 其它 → 未归类 + 同名合并（跳过芯片/多时装）
    for per in d["periods"]:
        if per.get("family") == "其它抽奖活动":
            per["family"] = "未归类（广播名单）"
    by = {}
    for per in d["periods"]:
        if per.get("family_key") in SKIP_MERGE:
            continue
        key = (str(per.get("activity_name") or per.get("label")), per.get("family"))
        by.setdefault(key, []).append(per)
    drop, remap = set(), {}
    for k, g in by.items():
        if len(g) < 2:
            continue
        g.sort(key=lambda x: (x.get("start") or "9999", x["period_id"]))
        keep = g[0]
        for o in g[1:]:
            drop.add(o["period_id"])
            remap[o["period_id"]] = keep["period_id"]
            keep["start"] = keep.get("start") or o.get("start") or ""
            keep["end"] = keep.get("end") or o.get("end") or ""
    items, seen = [], set()
    for it in d["items"]:
        pid = remap.get(it["period_id"], it["period_id"])
        it["period_id"] = pid
        key = (pid, str(it.get("item_id")))
        if key in seen:
            continue
        seen.add(key)
        items.append(it)
    d["items"] = items
    d["periods"] = [x for x in d["periods"] if x["period_id"] not in drop]
    print("4) 同名合并", len(drop))

    # 8) 剔除 share_reward 配置 id
    before = len(d["items"])
    d["items"] = [i for i in d["items"] if str(i.get("item_id")) != "921954"]
    print("8) 剔除配置 id", before - len(d["items"]))

    for per in d["periods"]:
        per["member_count"] = sum(1 for i in d["items"] if i["period_id"] == per["period_id"])
    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    d["meta"]["state_summary"]["有图"] = sum(
        1 for i in d["items"] if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")

    # 5-7) 后续工具
    run("reclassify_lottery_families.py")
    run("rebuild_multioptional_periods.py")
    run("rebuild_chip_timeline.py")
    run("add_chip_anchors.py")
    run("normalize_lottery_names.py")

    r = subprocess.run([PY, str(TOOLS / "build_wiki.py")], cwd=str(WEB), capture_output=True, text=True)
    tail = (r.stdout or "").strip().splitlines()
    print("build:", tail[0] if tail else r.returncode)
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
