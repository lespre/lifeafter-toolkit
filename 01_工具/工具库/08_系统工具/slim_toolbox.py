# -*- coding: utf-8 -*-
"""01_工具 架构精简：旧版本脚本下沉 + 空目录清理 + 统一 CLI 入口。"""
from __future__ import annotations

import json
import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
TOOLS = ROOT / "01_工具/工具库"
PARK = ROOT / "03_执行/95_待清理/治理与工具_20261022/旧版本脚本"
PARK.mkdir(parents=True, exist_ok=True)

moved = []
# 1) 旧版本脚本 → 待清理（保留最后一版）
KEEP = {"decode_ms_v6.py", "neutralize_index4.py", "decode_model_show4.py", "neox_dis2.py"}
for pat in ("decode_ms_v*.py", "neutralize_index*.py", "decode_model_show*.py", "neox_dis*.py"):
    for p in TOOLS.rglob(pat):
        if p.name in KEEP or "_归档" in p.as_posix() or "95_待清理" in p.as_posix():
            continue
        dst = PARK / p.name
        i = 1
        while dst.exists():
            dst = PARK / ("%s_%d%s" % (p.stem, i, p.suffix))
            i += 1
        shutil.move(str(p), str(dst))
        moved.append(p.relative_to(ROOT).as_posix())

# 2) 空目录
emptied = []
for p in sorted(TOOLS.rglob("*"), key=lambda x: -len(x.parts)):
    if p.is_dir() and not any(p.iterdir()):
        try:
            p.rmdir()
            emptied.append(p.relative_to(ROOT).as_posix())
        except OSError:
            pass
for extra in (ROOT / "01_工具/03_执行",):
    if extra.is_dir() and not any(extra.iterdir()):
        extra.rmdir()
        emptied.append(extra.relative_to(ROOT).as_posix())

# 3) la.py 统一入口：新增 tool 透传
la = ROOT / "la.py"
s = la.read_text(encoding="utf-8")
if 'add_parser("tool"' not in s:
    s = s.replace(
        '    sub.add_parser("doctor", help="自检：环境/索引/CLI/服务")',
        '    tp = sub.add_parser("tool", help="透传到 toolkit_cli（tables/lottery/atlas/locate/...）\n'
        '    tp.add_argument("rest", nargs=argparse.REMAINDER)\n\n'
        '    sub.add_parser("doctor", help="自检：环境/索引/CLI/服务")', 1)
    s = s.replace(
        '    if a.cmd == "doctor":',
        '    if a.cmd == "tool":\n'
        '        import subprocess as _sp\n'
        '        env = dict(os.environ)\n'
        '        env["PYTHONPATH"] = str(PROJ / "01_工具/工具库/00_共享核心")\n'
        '        return _sp.call([PY, "-u", str(PROJ / "01_工具/工具库/00_共享核心/命令行/toolkit_cli.py")] + a.rest, env=env)\n'
        '    if a.cmd == "doctor":', 1)
    la.write_text(s, encoding="utf-8")
    cli_added = True
else:
    cli_added = False

print(json.dumps({"moved_versions": moved, "empty_dirs_removed": emptied,
                  "cli_tool_added": cli_added}, ensure_ascii=False, indent=1))
