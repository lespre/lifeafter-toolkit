# -*- coding: utf-8 -*-
r"""散文件层内容索引（H-2）—— 把 loose 产物变成【按内容可查】的 sidecar。

## 为什么这么做（实测口径，2026-09-30）

```
loose 产物 5,124 个明文文件
  entry.hash == 落盘文件 md5   5,124/5,124  ✅（内容 md5，不是路径哈希）
  能内容寻址到 (容器,行)→树路径    394        （多数树里已有，属重复下载）
  认不出（树里没有这份内容）     4,730        ← 本次热更新的新/变资源
```
★ 这 4,730 的**逻辑路径在客户端里拿不到**：客户端对散文件层就是**内容寻址**存储
  （`res/<家族>/<32hex>` = md5(载荷)），`.idx` 条目只有
  `hash/pkg/offset/payload_size/header_size`，**没有路径字段**。
  「路径名算哈希撞条目」这条早被证伪（327,712 组合全 0，见 skill 禁重试清单）。
⇒ 能做的是：**建内容索引**，让工具/渲染线能「按内容找文件」，并把「认领不了」如实标出来。

产物：`03_执行/10_索引/loose/loose_content_index.jsonl`（一行一条，含 md5/大小/家族/落盘路径/认领结果）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
from collections import Counter
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
INDEX = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
ROWMAP = PROJ / "03_执行/10_索引/indexes/row_path_map.db"
OUT_DIR = PROJ / "03_执行/10_索引/loose"


def main() -> int:
    ap = argparse.ArgumentParser(description="散文件层内容索引（按 md5 可查）")
    ap.add_argument("--loose", type=Path,
                    default=PROJ / "03_执行/30_分析/资源层热更_20260930/loose")
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    man = json.loads((args.loose / "_manifest.json").read_text(encoding="utf-8"))
    print("★ 散文件层内容索引：manifest %d 条" % len(man))

    con = sqlite3.connect("file:%s?mode=ro" % INDEX.as_posix(), uri=True)
    md5_to_row = {}
    for c, ri, size, md5 in con.execute("SELECT container,row_index,size,md5 FROM content_hashes"):
        md5_to_row.setdefault(md5, (c, ri, size))
    con.close()
    rm = sqlite3.connect("file:%s?mode=ro" % ROWMAP.as_posix(), uri=True)

    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / "loose_content_index.jsonl"
    stats = Counter()
    fam = Counter()
    claimed = 0
    t0 = time.time()
    with out.open("w", encoding="utf-8") as fh:
        for r in man:
            e = r.get("entry") or {}
            p = Path(r["output"])
            if not p.is_file():
                stats["落盘缺失"] += 1
                continue
            md5 = hashlib.md5(p.read_bytes()).hexdigest()
            size = p.stat().st_size
            names_ok = (md5 == e.get("hash"))
            stats["hash==md5"] += 1 if names_ok else 0
            fam[e.get("family") or "?"] += 1
            rec = {"md5": md5, "size": size, "family": e.get("family"),
                   "pkg": e.get("pkg"), "idx": e.get("index"),
                   "layers": r.get("layers"), "ac_tag": r.get("ac_tag"),
                   "loose_file": str(p), "type": r.get("type")}
            hit = md5_to_row.get(md5)
            if hit:
                c, ri, _sz = hit
                rr = rm.execute("SELECT path,in_tree FROM rows WHERE container=? AND row_index=?",
                                (c, ri)).fetchone()
                rec["claims"] = {"container": c, "row": ri,
                                 "path": (rr[0] if rr else None),
                                 "in_tree": (rr[1] if rr else None)}
                claimed += 1
            else:
                rec["claims"] = None
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    rm.close()

    total = len(man)
    print("★ 产物 → %s（%.1fs）" % (out, time.time() - t0))
    print("   条数 %d · 能认领(容器,行) %d · 认不出 %d"
          % (total, claimed, total - claimed))
    print("   家族分布 top10: %s" % dict(fam.most_common(10)))
    print("   校验: %s" % dict(stats))
    (args.out / "loose_content_index_summary.json").write_text(json.dumps(
        {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "loose_dir": str(args.loose),
         "total": total, "claimed": claimed, "unclaimed": total - claimed,
         "families": dict(fam),
         "boundary": ("散文件层是内容寻址：.idx 条目无路径字段，认领不了的那部分"
                      "在客户端里也没有名字（路径名算哈希撞条目已证伪）"),
         }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 摘要 → %s" % (args.out / "loose_content_index_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
