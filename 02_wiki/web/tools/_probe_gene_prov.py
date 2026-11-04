# -*- coding: utf-8 -*-
"""看 gene 板 provenance 结构：好条目 vs 缺字段条目。"""
import json
from pathlib import Path

P = Path(r"E:\la拆包项目\02_wiki\web\data\boards\gene_potential_catalog.json")


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    items = d["items"]
    bad = [i for i in items if not ((i.get("provenance") or {}).get("upstream")
                                    and (i.get("provenance") or {}).get("name_source"))]
    good = [i for i in items if i not in bad]
    print("总", len(items), "| 缺字段", len(bad))
    if good:
        g = good[0]["provenance"]
        print("好样例 keys", list(g))
        print("  ", json.dumps(g, ensure_ascii=False)[:500])
    if bad:
        print("坏样例 id", [b.get("id") for b in bad][:5])
        print("  ", json.dumps(bad[0].get("provenance"), ensure_ascii=False)[:500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
