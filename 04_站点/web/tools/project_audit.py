# -*- coding: utf-8 -*-
r"""项目自查：板块数据完整性 / 索引一致性 / 资源引用 / 发布策略覆盖。
只读检查，输出问题清单与计数。
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
BOARDS = WEB / "data/boards"


def load(p: pathlib.Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("  ✗ 解析失败", p.name, e)
        return None


def check_boards(manifest_boards: dict) -> None:
    print("== 板块数据 ==")
    for f in sorted(BOARDS.glob("*.json")):
        if f.name.startswith("_") or f.name in ("index.json",):
            continue
        d = load(f)
        if not d or "items" not in d:
            continue
        items = d["items"]
        miss_prov = sum(1 for x in items
                        if not all((x.get("provenance") or {}).get(k)
                                   for k in ("source_id", "locator_chain",
                                             "source_lock_sha256", "upstream", "name_source")))
        miss_img = 0
        img_total = 0
        for x in items:
            for i in ((x.get("_media") or {}).get("images") or []):
                png = i.get("png")
                if not png:
                    continue
                img_total += 1
                if not (WEB / png).is_file():
                    miss_img += 1
        dup = [k for k, v in Counter(str(x.get("id")) for x in items).items() if v > 1]
        man = manifest_boards.get(f.stem)
        man_n = man.get("items") if man else None
        flags = []
        if miss_prov:
            flags.append("provenance缺%d" % miss_prov)
        if miss_img:
            flags.append("图缺%d/%d" % (miss_img, img_total))
        if dup:
            flags.append("重复id%d" % len(dup))
        if man_n is not None and man_n != len(items):
            flags.append("manifest条目%d≠%d" % (man_n, len(items)))
        if not man:
            flags.append("未登记manifest")
        mark = "✓" if not flags else "⚠"
        print("  %s %-30s %5d 条 %s" % (mark, f.stem, len(items), ("｜" + " ".join(flags)) if flags else ""))


def check_taxonomy(manifest_boards: dict, policy: dict) -> None:
    print("\n== 首页导航 / 发布策略 ==")
    tax = load(WEB / "data/wiki_taxonomy.json") or {}
    refs = []

    def walk(n):
        for b in (n.get("boards") or []):
            refs.append(b)
        for c in (n.get("children") or []):
            walk(c)

    for top in tax.get("树", []):
        walk(top)

    orphan = [b for b in refs if b not in manifest_boards]
    print("  导航引用 %d 个板 ｜ 不在 manifest 的 %d 个 %s" % (len(refs), len(orphan), orphan[:6]))

    published = [b for b, v in policy.items() if v.get("publication_status") in ("published",)]
    not_in_nav = [b for b in published if b not in refs]
    print("  published 板 %d ｜ 未挂进导航 %d 个 %s" % (len(published), len(not_in_nav), not_in_nav[:6]))

    st = Counter(v.get("publication_status") for v in policy.values())
    print("  发布状态分布:", dict(st))


def check_pages() -> None:
    print("\n== 页面资源引用 ==")
    for name in ("wiki.html", "board.html"):
        p = WEB / name
        if not p.is_file():
            print("  ✗ 缺", name)
            continue
        html = p.read_text(encoding="utf-8")
        refs = set(re.findall(r'(?:src|href)="(assets/[^"?]+)', html))
        refs |= set(re.findall(r'url\("?(assets/[^")?]+)', html))
        missing = [r for r in refs if not (WEB / r).is_file()]
        print("  %-12s 引用 %3d 个本地资源 ｜ 缺 %d %s"
              % (name, len(refs), len(missing), missing[:5]))
    for css in ("board_shadcn.css", "assets/board_theme_aftermath.css", "assets/weapon_skin_viewer.css"):
        p = WEB / css
        if p.is_file():
            print("  css %-38s %6d B" % (css, p.stat().st_size))


def check_index() -> None:
    print("\n== PE 索引 ==")
    import sqlite3
    db = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/热更检测/pe_index.sqlite3")
    if not db.is_file():
        print("  ✗ 索引不存在")
        return
    try:
        con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True, timeout=10)
        tot = con.execute("select count(*) from rows").fetchone()[0]
        named = con.execute("select count(*) from rows where name is not null and name<>'' and name not like '%_未命名%'").fetchone()[0]
        packs = con.execute("select count(distinct pack) from rows").fetchone()[0]
    except sqlite3.OperationalError as e:
        print("  索引正被写入，跳过（%s）｜ %.0f MB" % (e, db.stat().st_size / 1048576))
        return
    print("  %d 包 ｜ %d 行 ｜ 已命名 %d (%.1f%%) ｜ %.0f MB"
          % (packs, tot, named, named * 100.0 / max(tot, 1), db.stat().st_size / 1048576))


def main() -> int:
    man = load(WEB / "data/manifest.json") or {}
    mb = {b["board"]: b for b in man.get("boards", [])}
    pol = (load(WEB / "data/publication_policy.json") or {}).get("boards", {})
    check_boards(mb)
    check_taxonomy(mb, pol)
    check_pages()
    check_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
