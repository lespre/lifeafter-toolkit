# -*- coding: utf-8 -*-
r"""礼盒「内含」父子关系：解析 desc 文本（候选级）。"""
from __future__ import annotations

import collections
import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
P = WEB / "data/boards/item_master_full.json"

COLOR = re.compile(r"#c[0-9a-fA-F]{6,8}|#n|#r|#b")
TOK = re.compile(r"[\u3001,\uff0c\u3002;\uff1b\n]")
CNT = re.compile(r"^(.*?)[*\u00d7](\d+)$")
PAREN = re.compile(r"[\uff08(][^\uff09)]*[\uff09)]$")
PRE = ("\u5185\u542b", "\u6253\u5f00\u540e\u83b7\u5f97", "\u6253\u5f00\u83b7\u5f97", "\u83b7\u5f97")


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    items = d["items"]

    by_name = collections.defaultdict(list)
    for it in items:
        nm = str(it.get("name") or "").strip()
        if nm:
            by_name[nm].append(it)

    def pick(nm):
        cands = [c for c in by_name.get(nm, []) if str(c.get("kind")) != "\u793c\u76d2"]
        if not cands:
            cands = list(by_name.get(nm, []))
        if not cands:
            return None
        cands.sort(key=lambda c: (0 if ((c.get("_media") or {}).get("images")) else 1,
                                 int(c.get("item_id") or 0)))
        return cands[0]

    def exists(nm):
        return nm in by_name or PAREN.sub("", nm).strip() in by_name

    linked = pairs = 0
    for it in items:
        if str(it.get("kind")) != "\u793c\u76d2":
            continue
        desc = COLOR.sub("", str(it.get("desc") or ""))
        if not desc:
            continue
        bundle, seen = [], set()
        for piece in TOK.split(desc):
            piece = piece.strip()
            for pre in PRE:
                if piece.startswith(pre):
                    piece = piece[len(pre):].strip()
            if not piece or len(piece) > 40:
                continue
            m = CNT.match(piece)
            nm, cnt = (m.group(1).strip(), int(m.group(2))) if m else (piece, 1)
            if not nm or not exists(nm):
                continue
            tgt = pick(nm)
            if not tgt:
                continue
            iid = tgt.get("item_id")
            if iid in seen:
                continue
            seen.add(iid)
            bundle.append({"name": nm, "count": cnt, "item_id": iid, "resolved": True})
            pairs += 1
        if not bundle:
            continue
        it["bundle"] = bundle
        it["bundle_state"] = "desc-parsed"
        it["evidence_level"] = "candidate"
        it["status_tags"] = sorted(set(list(it.get("status_tags") or []) + ["desc \u89e3\u6790"]))
        linked += 1

    d["meta"]["state_summary"]["\u793c\u76d2\u542b\u5185\u542b"] = linked
    d["meta"]["notes"] = (str(d["meta"].get("notes") or "") +
                          "\n\u793c\u76d2\u300c\u5185\u542b\u300d\u7531 desc \u6587\u672c\u89e3\u6790\uff0cevidence_level=candidate\u3002").strip()
    P.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/item_master_full.js").write_text(
        "window.WIKI_BOARD_item_master_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("\u793c\u76d2\u5efa\u5173\u7cfb", linked, "\uff5c\u5185\u542b\u6761\u76ee", pairs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
