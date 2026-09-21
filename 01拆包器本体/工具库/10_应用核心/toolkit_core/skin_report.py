# -*- coding: utf-8 -*-
"""武器皮肤定位链专题：扫描 3D 素材目录 + 内置索引定位 + Markdown 报告。

链：皮肤ID → 3D 素材（模型/材质/源引用）→ 逻辑路径索引定位（容器/行/fid）→ 报告。
纪律：只报告证据（命中 / MISS / 匿名条目），不猜绑。
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

PATH_RE = re.compile(r"(?:common|weapon|character|ui)[A-Za-z0-9_\\/.]*\.(?:tga|dds|png|jpg|mesh|gim|mod|c159)", re.I)


def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def collect_skins(root) -> list[dict]:
    root = Path(root)
    if not root.is_dir():
        raise FileNotFoundError(f"3D 素材目录不存在：{root}")
    out: list[dict] = []
    for sub in sorted([p for p in root.iterdir() if p.is_dir() and p.name.isdigit()]):
        viewer = _load_json(sub / "viewer.json") or {}
        neox = _load_json(sub / "neox_material.json") or {}
        title = viewer.get("title") or neox.get("display_name") or ""
        glb = len(list(sub.rglob("*.glb")))
        mesh = len(list(sub.rglob("*.mesh")))
        js = len(list(sub.rglob("*.json")))
        refs: list[dict] = []
        src = neox.get("source")
        if isinstance(src, dict):
            for k in ("bind_c159", "material_c159", "mesh"):
                if src.get(k):
                    refs.append({"kind": k, "ref": str(src[k]),
                                 "container": src.get("container"),
                                 "sha256": src.get(f"{k}_sha256")})
        raw = json.dumps(neox, ensure_ascii=False)
        seen = set()
        for pth in sorted(set(PATH_RE.findall(raw))):
            if pth not in seen:
                seen.add(pth)
                refs.append({"kind": "path", "ref": pth})
        out.append({"skin_id": sub.name, "title": title, "dir": str(sub),
                    "glb": glb, "mesh": mesh, "json": js,
                    "data_summary": f"glb×{glb}｜mesh×{mesh}｜json×{js}",
                    "refs": refs, "state": "3D 就绪" if (sub / "viewer.json").exists() else "3D 缺失"})
    return out


def locate_refs(rows: list[dict], index) -> None:
    for r in rows:
        hits = 0
        total = 0
        details = []
        for ref in r.get("refs", []):
            if ref.get("kind") != "path":
                continue
            total += 1
            logical = re.sub(r"[\\/]+", "/", ref["ref"]).replace("/", "\\")
            res = None
            try:
                res = index.find(logical)
            except Exception:
                res = None
            if res is not None and getattr(res, "hits", None):
                h = res.hits[0]
                hits += 1
                details.append({"ref": ref["ref"], "status": "FOUND",
                                "container": h.container, "row": h.row, "fid": h.fid_hex})
            else:
                details.append({"ref": ref["ref"], "status": "MISS"})
        r["path_hits"] = hits
        r["path_total"] = total
        r["path_details"] = details
        r["hit_summary"] = f"{hits}/{total}" if total else "—"


def build_markdown_report(rows: list[dict], index, *, out_dir=None, log=print) -> Path:
    if out_dir is None:
        out_dir = Path(r"E:/la拆包项目/03拆包产物")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    locate_refs(rows, index)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = out_dir / f"报告_武器皮肤定位链_{ts}.md"
    tot = sum(r.get("path_total", 0) for r in rows)
    ok = sum(r.get("path_hits", 0) for r in rows)
    L = [f"# 武器皮肤定位链报告（{ts}）", "",
         f"- 皮肤数：{len(rows)}",
         f"- 贴图路径定位（内置索引）：{ok}/{tot} 命中",
         "- 数据源：3D 素材目录（viewer.json / neox_material.json）+ 内置统一索引",
         "- 说明：c159/mesh 为源容器匿名条目（无逻辑路径），只列容器与 sha256，不做索引补全。",
         "",
         "## 总览", "",
         "| 皮肤 ID | 名称 | 3D 数据 | 路径命中 | 状态 |",
         "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['skin_id']} | {r.get('title') or '—'} | {r['data_summary']} | {r.get('hit_summary', '—')} | {r['state']} |")
    L.append("")
    for r in rows:
        L.append(f"## {r['skin_id']} · {r.get('title') or '（未命名）'}")
        L.append("")
        for ref in r.get("refs", []):
            if ref.get("kind") != "path":
                L.append(f"- [{ref['kind']}] `{ref['ref']}`｜容器：`{ref.get('container') or '—'}`｜sha256 `{(ref.get('sha256') or '—')[:16]}`")
        for d in r.get("path_details", []):
            if d["status"] == "FOUND":
                L.append(f"- ✅ `{d['ref']}` → {d['container']} #{d['row']}（fid {d['fid']}）")
            else:
                L.append(f"- ❌ `{d['ref']}` → MISS（当前索引范围）")
        L.append("")
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    log(f"📄 定位链报告：{out}（{len(rows)} 皮肤，路径命中 {ok}/{tot}）")
    return out
