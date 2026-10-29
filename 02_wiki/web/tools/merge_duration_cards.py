# -*- coding: utf-8 -*-
r"""把「永久款 + 时限款」拆成两张卡的时装合并成一张。

起因（2026-10-29 用户反馈）：
  冰雪礼赞 一套出了 4 张卡：永久款「冰雪礼赞-头饰 / -衣服」+ 时限款「冰雪礼赞-头饰(30天) / -衣服(30天)」。
  表里 366935/366936 的 name 就是「冰雪礼赞-头饰(30天)」（valid_days=30），
  而重建脚本的期限归一正则只认 `-30天`，不认 `(30天)` / `（1天）`，归一后跟永久款不是同一个 key → 分成两张卡。
  同类问题还有：「不羁黄-30天」→ 归一成「不羁黄」，而永久款叫「悠游探索 不羁黄」；
  「希望之翼-限时-头饰」带 -限时 标记；「三周年纪念-头饰」的表名其实是「三载之伴-头饰」。

判定条件：
  ① 只能是「纯时限卡」（无永久行、有期限档）去并「永久卡」（has_permanent）
  ② 同 model_id + 同部位
  ③ 名字归一后能对上唯一一张永久卡。归一口径：
     · 去尾部期限：-30天 / (30天) / （1天）
     · 去「-限时」标记
     · 去尾部部位词（衣服/头饰/背包/整套/套装/光源）
     · 名字对不上时，用表里 desc 开头的「<全名> - <部位>（N天）」再试一次
     · 仍然对不上，允许「一方名字是另一方后缀」（如 不羁黄 ⊂ 悠游探索 不羁黄）
  ④ 两卡图标路径有交集（同一套图）——防止同名不同图误并

合并后：
  · 永久卡 durations / time_limited_variants 并入，duration_state=mixed
  · 行键 / 表内变体名 / model_ids / 图标登记表 合并去重（永久卡缺图槽、时限卡有图时采用时限卡的图）
  · 永久卡新增 duration_merge：被并卡名 / id / 行键 / 期限档 / 依据
  · 被并卡进顶层 merged_away（kind=duration），可回滚

用法：
  python merge_duration_cards.py --dry
  python merge_duration_cards.py
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
from collections import Counter, defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"
ROWS_CSV = PROJ / "01_索引与产物/30_分析/表结构解析_20260928/结构2/fashion_data_chs.py.rows.csv"

DUR_PAT = re.compile(r"[-－]?\s*[(（]*\s*\d+\s*天\s*[)）]*$")
LIMIT_PAT = re.compile(r"[-－]\s*限时\s*(?=[-－]|$)")
PART_WORDS = ("衣服", "头饰", "背包", "整套", "套装", "光源")


def norm(name: str, strip_part: bool = False) -> str:
    s = (name or "").split("#")[0].strip()
    s = DUR_PAT.sub("", s)
    s = LIMIT_PAT.sub("-", s)
    s = re.sub(r"\s*[-－]\s*", "-", s)          # " - " → "-"
    s = re.sub(r"[-－]{2,}", "-", s).strip("-－ ")
    s = s.strip("(（)） ")          # 表里有「((30天)」这种多打一个括号的脏数据
    if strip_part:
        for pw in PART_WORDS:
            if s.endswith("-" + pw):
                s = s[: -len(pw) - 1]
                break
        s = s.strip("-－ ")
    return s


def load_board() -> dict:
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


def union(a, b):
    out = list(a or [])
    for x in (b or []):
        if x not in out:
            out.append(x)
    return out


def descs_of_timed(it: dict, rows: dict) -> list:
    out = []
    for rk in (it.get("row_keys") or []):
        d = (rows.get(str(rk), {}) or {}).get("desc") or ""
        if d:
            head = re.split(r"[。；;]", d, 1)[0]
            if head:
                out.append(head)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    rows = {}
    if ROWS_CSV.exists():
        with open(ROWS_CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows[r["row_key"]] = r

    d = load_board()
    items = d["items"]

    groups = defaultdict(list)
    for it in items:
        if it.get("model_id") and it.get("part"):
            groups[(it["model_id"], it["part"])].append(it)

    stat = Counter()
    pairs = []      # (永久卡, 时限卡, 依据)
    for key, g in groups.items():
        perms = [x for x in g if x.get("has_permanent")]
        timed = [x for x in g if not x.get("has_permanent") and (x.get("durations") or [])]
        if not perms or not timed:
            continue
        host_norm = {}

        def add_key(k, p):
            if p not in host_norm.setdefault(k, []):
                host_norm[k].append(p)

        for p in perms:
            add_key(norm(p["name"], strip_part=True), p)
            add_key(norm(p["name"]), p)

        for t in timed:
            # 收集候选：名字归一 / 名字原样 / 描述里的全名 / 名字后缀包含
            cands, seen = [], set()

            def add(p, tag):
                if p["id"] not in seen:
                    seen.add(p["id"])
                    cands.append((p, tag))

            keys = [(norm(t["name"], strip_part=True), "名字归一"),
                    (norm(t["name"]), "名字原样")]
            for dh in descs_of_timed(t, rows):
                keys.append((norm(dh, strip_part=True), "描述里的全名"))
            for kk, tag in keys:
                for h in (host_norm.get(kk) or []):
                    add(h, tag)
            tn = norm(t["name"], strip_part=True)
            if tn:
                for p in perms:
                    pn = norm(p["name"], strip_part=True)
                    if pn and (pn.endswith(tn) or tn.endswith(pn)):
                        add(p, "名字后缀包含")

            # 用图标交集做最终裁决：只有一套图对得上才算同一件
            tp = {x.get("path") for x in (t.get("icons_all") or []) if x.get("path")}
            ok = []
            for p, tag in cands:
                hp = {x.get("path") for x in (p.get("icons_all") or []) if x.get("path")}
                if not tp or not hp or (tp & hp):
                    ok.append((p, tag))
            if not ok:
                stat["对不上唯一永久卡"] += 1
                print("  跳过 %s：候选 %s 的图标都对不上（%s）" % (
                    t["name"], "/".join(p["name"] for p, _ in cands) or "无", sorted(tp)))
                continue
            if len(ok) > 1:
                stat["候选不唯一"] += 1
                print("  跳过 %s：多个候选 %s" % (t["name"], "/".join(p["name"] for p, _ in ok)))
                continue
            host, why = ok[0]
            stat["合并（%s）" % why] += 1
            pairs.append((host, t, why))

    for host, t, why in pairs:
        days = sorted(set(t.get("durations") or []))
        print("%-18s += %-22s 期限 %-10s [%s]  行键 %s ← %s" % (
            host["name"], t["name"], "/".join("%d天" % x for x in days), why,
            len(host.get("row_keys") or []), ",".join(str(x) for x in (t.get("row_keys") or []))))

    if not a.dry:
        for host, t, why in pairs:
            days = sorted(set(t.get("durations") or []))
            dm = host.get("duration_merge") or {"names": [], "ids": [], "row_keys": [], "days": []}
            dm["names"] = union(dm.get("names"), [t["name"]])
            dm["ids"] = union(dm.get("ids"), [t["id"]])
            dm["row_keys"] = union(dm.get("row_keys"), t.get("row_keys") or [])
            dm["days"] = sorted(set(dm.get("days") or []) | set(days))
            dm["note"] = "表里同一套的时限记录（%s），已按永久款一张卡处理" % "/".join(
                "%d天" % x for x in days)
            host["duration_merge"] = dm

            host["row_keys"] = union(host.get("row_keys"), t.get("row_keys") or [])
            host["name_variants"] = union(host.get("name_variants"), t.get("name_variants") or [])
            host["model_ids"] = union(host.get("model_ids") or host.get("model_id"),
                                      t.get("model_ids") or t.get("model_id"))
            host["durations"] = sorted(set(host.get("durations") or []) | set(days))
            host["time_limited_variants"] = sorted(
                set(host.get("time_limited_variants") or []) | set(days))
            host["has_permanent"] = True
            host["duration_state"] = "mixed" if host["time_limited_variants"] else "permanent"

            hicons = {x.get("path"): x for x in (host.get("icons_all") or [])}
            for ic in (t.get("icons_all") or []):
                p = ic.get("path")
                if p in hicons:
                    if not hicons[p].get("png") and ic.get("png"):
                        hicons[p]["png"] = ic.get("png")
                else:
                    host.setdefault("icons_all", []).append(dict(ic))
                    hicons[p] = host["icons_all"][-1]
            host["icon_count"] = sum(1 for x in (host.get("icons_all") or []) if x.get("png"))
            host["icon_state"] = "有图" if host["icon_count"] else "无图"

            gaps = (t.get("_media") or {}).get("missing") or []
            if gaps:
                hg = host.setdefault("_media", {}).setdefault("missing", [])
                for g in gaps:
                    # 同一性别只留一条；本条能给出图标名而旧条目没有时，补上去
                    same = next((x for x in hg
                                 if x.get("gender") == g.get("gender")
                                 and (not x.get("base") or not g.get("base")
                                      or x.get("base") == g.get("base"))), None)
                    if same is None:
                        hg.append(g)
                    elif not same.get("base") and g.get("base"):
                        same["base"] = g["base"]
            if host.get("provenance") and t.get("provenance"):
                host["provenance"]["row_keys"] = union(
                    host["provenance"].get("row_keys"), t["provenance"].get("row_keys") or [])

    gone = {t["id"] for _h, t, _w in pairs}
    if gone and not a.dry:
        by_id = {it["id"]: it for it in items}
        d["items"] = [x for x in items if x["id"] not in gone]
        ma = d.get("merged_away") or []
        for hid in gone:
            src = by_id[hid]
            ma.append({
                "id": hid, "name": src.get("name"), "part": src.get("part"),
                "model_ids": src.get("model_ids"), "provenance": src.get("provenance"),
                "into": next(h["id"] for h, t, _w in pairs if t["id"] == hid),
                "kind": "duration",
            })
        d["merged_away"] = ma
        d["meta"]["merged_cards"] = len(ma)
        st = d["meta"].get("state_summary") or {}
        st["有图"] = sum(1 for x in d["items"] if x.get("icon_state") == "有图")
        st["无图"] = len(d["items"]) - st["有图"]
        d["meta"]["state_summary"] = st
        if isinstance(d["meta"].get("rebuild"), dict):
            d["meta"]["rebuild"]["cards"] = len(d["items"])
        d["meta"]["notes"] = (d["meta"].get("notes") or "") + (
            "\n\n【永久款 + 时限款卡合并（2026-10-29）】\n"
            "同 model 同部位的纯时限卡，若名字归一后（去 -N天/(N天)/（N天）、去 -限时、"
            "去部位词、或取描述里的全名）能对上唯一一张永久卡，且图标有交集，则并入永久卡折成时限档，共 %d 张。\n"
            "根因：重建脚本期限归一正则原只认 -N天，`(30天)` / `（1天）` 写法没归到永久款上。\n" % len(gone))

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-22s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(items) - len(gone)))
    if a.dry:
        print("（dry-run，未写盘）")
    else:
        save_board(d)
        print("已写回", BOARD_JSON.name, "与", BOARD_JS.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
