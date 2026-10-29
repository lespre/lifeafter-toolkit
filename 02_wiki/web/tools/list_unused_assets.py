import sys
# -*- coding: utf-8 -*-
"""列出 assets 下没有被任何 html/js 引用的子目录（候选删除）。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

W = pathlib.Path(WEB)
A = W / "assets"
texts = []
for pat in ("*.html", "*.js"):
    for p in W.glob(pat):
        texts.append(p.read_text(encoding="utf-8", errors="ignore"))
for p in (W / "tools").glob("*.py"):
    texts.append(p.read_text(encoding="utf-8", errors="ignore"))
blob = "\n".join(texts)

rows = []
for d in sorted(A.iterdir()):
    if not d.is_dir():
        continue
    name = d.name
    used = (name in blob) or ("assets/%s/" % name in blob)
    size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
    rows.append((used, size / 1048576, name))
rows.sort()
for used, mb, name in rows:
    print("%-5s %8.1f MB  assets/%s" % ("用" if used else "未用", mb, name))
