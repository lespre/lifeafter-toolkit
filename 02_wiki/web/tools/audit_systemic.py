# -*- coding: utf-8 -*-
"""系统性纠错扫描：一次找出「同类错误」的全部实例，而不是逐个踩。

四类：
A 被引用但仓库里没有 / 被 gitignore 吞掉的站点依赖（新设备会报错的根因）
B 桩文件冒充真表（<1KB 的 cdata 表）
C 图路径扩展名与实际资源不符（.png 声明 vs .ktx/.bc7 实体）
D 资源重复（同内容不同名，会挂错图）

用法：python tools/audit_systemic.py [--json]
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import subprocess
import sys

PROJ = pathlib.Path(__file__).resolve().parents[3]
WEB = PROJ / "02_wiki" / "web"
TREE = PROJ / "01_索引与产物/41_还原树"


def repo_tracked() -> set[str]:
    try:
        out = subprocess.run(["git", "-C", str(PROJ), "ls-files"], capture_output=True,
                             text=True, timeout=120).stdout
        return {line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()}
    except Exception:
        return set()


def a_missing_site_deps(tracked: set[str]) -> list[dict]:
    """页面/脚本引用的本地文件，存在但没入库（新设备拿不到）。"""
    pat = re.compile(r"""["'(](?:\.\./)?((?:assets|data|design)/[^"')\s]+\.(?:js|json|png|css|webp|svg))""")
    refs: set[str] = set()
    for f in list(WEB.glob("*.html")) + list((WEB / "tools").glob("*.py")):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in pat.finditer(text):
            refs.add(m.group(1))
    out = []
    for r in sorted(refs):
        p = WEB / r
        if not p.exists():
            continue
        rel = str(p.relative_to(PROJ)).replace("\\", "/")
        if rel not in tracked:
            out.append({"path": rel, "bytes": p.stat().st_size})
    return out


def b_stub_tables() -> list[dict]:
    out = []
    for p in TREE.rglob("*.py"):
        if p.stat().st_size < 1024 and "cdata" in str(p):
            out.append({"path": str(p.relative_to(PROJ)).replace("\\", "/"),
                        "bytes": p.stat().st_size, "stem": p.stem})
    return out


def c_ext_mismatch() -> list[dict]:
    """板里写的图标路径是 .png，但真实资源是 .ktx/.bc7。"""
    idx = PROJ / "01_索引与产物/30_分析/热更检测/pe_index.sqlite3"
    if not idx.exists():
        return []
    import sqlite3
    con = sqlite3.connect(idx)
    names = {r[0].replace("\\", "/").rsplit(".", 1)[0]
             for r in con.execute("select name from rows where name like '%.ktx' limit 400000")}
    names |= {r[0].replace("\\", "/").rsplit(".", 1)[0]
              for r in con.execute("select name from rows where name like '%.bc7' limit 400000")}
    miss = hit = 0
    samples = []
    for b in (WEB / "data/boards").glob("*.json"):
        try:
            d = json.loads(b.read_text(encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items") or []:
            for im in (it.get("_media") or {}).get("images") or []:
                png = str(im.get("png") or "")
                if not png.endswith(".png"):
                    continue
                base = png.rsplit(".", 1)[0]
                if (WEB / png).exists():
                    hit += 1
                elif base in names or base.replace("assets/img_cache/", "ui/") in names:
                    miss += 1
                    if len(samples) < 5:
                        samples.append(png)
                else:
                    miss += 1
    return [{"png_ok": hit, "png_missing": miss, "samples": samples}]


def d_dup_assets() -> list[dict]:
    seen: dict[str, list[str]] = {}
    for p in (WEB / "assets").rglob("*.png"):
        try:
            h = hashlib.md5(p.read_bytes()).hexdigest()
        except Exception:
            continue
        seen.setdefault(h, []).append(str(p.relative_to(PROJ)).replace("\\", "/"))
    return [{"md5": h, "files": v} for h, v in seen.items() if len(v) > 1][:20]


def main() -> int:
    tracked = repo_tracked()
    a, b, c, d = a_missing_site_deps(tracked), b_stub_tables(), c_ext_mismatch(), d_dup_assets()
    rep = {"A_未入库依赖": a, "B_桩表": b, "C_图扩展名": c, "D_重复资源": d}
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 0
    print("A 被引用但未入库的文件：%d" % len(a))
    for x in a[:12]:
        print("   %-64s %8d B" % (x["path"], x["bytes"]))
    print("B 桩表（<1KB，多半是空壳）：%d" % len(b))
    for x in b[:12]:
        print("   %-70s %4d B" % (x["path"], x["bytes"]))
    print("C 图路径：存在 %s ｜ 缺 %s ｜ 例 %s" %
          (c[0]["png_ok"] if c else 0, c[0]["png_missing"] if c else 0,
           (c[0]["samples"][:2] if c else [])))
    print("D 同内容不同名（可能挂错）：%d 组" % len(d))
    for g in d[:5]:
        print("   %s %s" % (g["md5"][:8], g["files"][:3]))
    out = PROJ / "01_索引与产物/30_分析/系统性纠错_20261024.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("明细 →", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
