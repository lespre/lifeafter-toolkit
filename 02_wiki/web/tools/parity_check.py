# -*- coding: utf-8 -*-
"""双源一致性检查：同一个 builder 分别用 PE / PC 表根跑一次，比对条目 id 集合。

用法：
    python tools/parity_check.py build_server_types.py server_types
    python tools/parity_check.py build_gene_board.py gene_potential_catalog
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
PY = sys.executable
BOARD_DIR = WEB / "data/boards"


def run(builder: str, source: str):
    env = dict(os.environ, LA_SOURCE=source)
    env.pop("LA_CDATA_ROOT", None)
    r = subprocess.run([PY, "-u", str(WEB / "tools" / builder)], cwd=str(WEB),
                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def ids(board: str):
    p = BOARD_DIR / ("%s.json" % board)
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    return {str(i.get("id")) for i in d.get("items", [])}


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    builder, board = sys.argv[1], sys.argv[2]
    target = BOARD_DIR / ("%s.json" % board)
    backup = target.with_suffix(".json.parity_bak")
    if target.exists():
        shutil.copy2(target, backup)

    rc_pe, out_pe = run(builder, "pe")
    set_pe = ids(board) or set()
    shutil.copy2(backup, target) if backup.exists() else None

    rc_pc, out_pc = run(builder, "pc")
    set_pc = ids(board) or set()

    if backup.exists():
        shutil.copy2(backup, target)
        backup.unlink()

    print("builder:", builder)
    print("PE  rc=%s 条目=%d" % (rc_pe, len(set_pe)))
    print("PC  rc=%s 条目=%d" % (rc_pc, len(set_pc)))
    only_pe = sorted(set_pe - set_pc)[:10]
    only_pc = sorted(set_pc - set_pe)[:10]
    print("交集 %d ｜ 仅 PE %d ｜ 仅 PC %d" % (len(set_pe & set_pc), len(set_pe - set_pc), len(set_pc - set_pe)))
    if only_pe:
        print("  仅 PE 示例:", only_pe)
    if only_pc:
        print("  仅 PC 示例:", only_pc)
    if rc_pe != 0:
        print("  PE 输出尾部:", out_pe.strip().splitlines()[-1:])
    if rc_pc != 0:
        print("  PC 输出尾部:", out_pc.strip().splitlines()[-1:])
    return 0 if set_pe == set_pc and rc_pe == rc_pc == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
