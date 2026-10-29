import sys
# -*- coding: utf-8 -*-
"""让 build_wiki.py 生成 data/build_meta.js（版本/设备/时间），供 wiki 横幅自动读取。"""
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

p = pathlib.Path(WEB / "tools/build_wiki.py")
s = p.read_text(encoding="utf-8")

if "build_meta" not in s:
    helper = '''

def write_build_meta() -> None:
    """写 data/build_meta.js：版本( git tag )、设备( hostname )、构建时间。"""
    import socket
    import subprocess
    import datetime

    root = ROOT.parent
    ver = ""
    try:
        ver = subprocess.run(["git", "-C", str(root), "describe", "--tags", "--always"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        ver = ""
    if not ver:
        ver = "v1.3.0"
    if re.fullmatch(r"v?\\d", ver) or ver.startswith("v1.3.0-"):
        # describe 后面带 -N-gHASH 时只取 tag 部分
        ver = ver.split("-")[0]
    meta = {
        "version": ver,
        "host": socket.gethostname(),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    out = ROOT / "data/build_meta.js"
    out.write_text("window.WIKI_BUILD = %s;\\n" % __import__("json").dumps(meta, ensure_ascii=False),
                   encoding="utf-8")
    print("✅ build_meta.js 已生成：%s" % meta)

'''
    s = s.replace("\ndef main() -> int:", helper + "\ndef main() -> int:", 1)
    # 在 main 的 manifest 生成之后调用
    s = s.replace('    print(f"✅ manifest.js 已生成', '    try:\n        write_build_meta()\n    except Exception as _e:  # noqa: BLE001\n        print("⚠️ build_meta 生成失败：", _e)\n    print(f"✅ manifest.js 已生成', 1)
    p.write_text(s, encoding="utf-8")
    print("build_wiki.py 已接 build_meta")
else:
    print("已存在 build_meta 逻辑")
