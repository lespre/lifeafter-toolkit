# -*- coding: utf-8 -*-
r"""资源层差分（只读）：客户端【新的】gres/0000.gpk vs 索引里记录的旧状态。

判据：按 (fid, payload_off, packed, decoded, flag, c1, c2) 逐行比 ——
      全同 = 未变；fid 同但尺寸/校验变 = 内容变更；行新增/消失 = 增删。
★ 只读，不写任何东西（写入等差分结果确认后再做）。
"""
from __future__ import annotations
import importlib.util
import json
import sqlite3
import sys
import time
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
GPKI = PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染/gpk_npk_index.py"
INDEX = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
CONTAINER = r"Documents\gres\0000.gpk"
CLIENT = Path(r"E:\mrzh\Documents\gres\0000.gpk")


def _mod():
    name = "_gpki_diff"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, GPKI)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    print("════ ① 客户端新 gpk ════")
    st = CLIENT.stat()
    print("   %s  %d B  mtime %s" % (CLIENT, st.st_size,
          time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))))
    mod = _mod()
    print("   reader: %s" % GPKI.name)
    t0 = time.time()
    rec, rows_fn, blocks = mod._gpk_blockchain(str(CLIENT), with_crc=True)
    print("   块链 blocks: %s" % (blocks if not isinstance(blocks, list) or len(blocks) < 8
                                else "%d 块" % len(blocks)))
    if isinstance(rec, dict):
        for k in ("blocks", "payload_delta", "count", "entries"):
            if k in rec:
                v = rec[k]
                print("   rec[%s] = %s" % (k, ("%d 项" % len(v)) if isinstance(v, list) else v))
    new = {}
    for i, fid, payload_off, packed, decoded, flag, c1, c2 in rows_fn():
        new[i] = (fid, payload_off, packed, decoded, flag, c1, c2)
    print("   ★ 新容器条目数 = %d（%.1fs）" % (len(new), time.time() - t0))

    print("\n════ ② 索引里记录的旧状态 ════")
    con = sqlite3.connect("file:%s?mode=ro" % INDEX.as_posix(), uri=True)
    old = {}
    for fid, row, off, poff, packed, decoded, flag in con.execute(
            "SELECT fid_hex,row_index,offset,payload_offset,packed,decoded,flag "
            "FROM entries WHERE container=?", (CONTAINER,)):
        old[row] = (fid, off, poff, packed, decoded, flag)
    cmeta = con.execute("SELECT bytes,rows,sha256 FROM containers WHERE container=?",
                        (CONTAINER,)).fetchone()
    con.close()
    print("   旧容器元信息: bytes=%s rows=%s sha256=%s" % cmeta)
    print("   ★ 旧条目数 = %d" % len(old))
    if cmeta:
        d = st.st_size - int(cmeta[0])
        print("   体积差 = %+d B（%+.2f MB）" % (d, d / 1048576))

    print("\n════ ③ 逐行差分 ════")
    same = changed = 0
    added, removed = [], []
    changed_rows = []
    for row, nv in new.items():
        ov = old.get(row)
        if ov is None:
            added.append(row)
            continue
        nfid, npoff, npacked, ndecoded, nflag, nc1, nc2 = nv
        ofid, ooff, opoff, opacked, odecoded, oflag = ov
        if (nfid == ofid and npacked == opacked and ndecoded == ndecoded
                and nflag == oflag):
            same += 1
        elif nfid == ofid:
            changed += 1
            if len(changed_rows) < 20:
                changed_rows.append({"row": row, "fid": nfid,
                                     "old": [opacked, odecoded],
                                     "new": [npacked, ndecoded]})
        else:
            changed += 1
            if len(changed_rows) < 20:
                changed_rows.append({"row": row, "fid": nfid, "old_fid": ofid,
                                     "old": [opacked, odecoded], "new": [npacked, ndecoded]})
    for row in old:
        if row not in new:
            removed.append(row)
    print("   未变 %d · 变更 %d（含换 fid）· 新增行 %d · 消失行 %d" %
          (same, changed, len(added), len(removed)))
    for c in changed_rows[:12]:
        print("      r%-7s fid=%s 旧(p=%s,d=%s) → 新(p=%s,d=%s)%s"
              % (c["row"], c["fid"], c["old"][0], c["old"][1], c["new"][0], c["new"][1],
                 "  ⚠换 fid(旧 %s)" % c.get("old_fid") if c.get("old_fid") else ""))
    if added:
        print("   新增行样例: %s" % added[:12])

    out = PROJ / "03_执行/30_分析/资源层热更_20260930" / "gres_diff.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "container": CONTAINER, "client_bytes": st.st_size,
        "old_bytes": int(cmeta[0]) if cmeta else None,
        "old_sha256": cmeta[2] if cmeta else None,
        "new_entries": len(new), "old_entries": len(old),
        "same": same, "changed": changed,
        "added_rows": added, "removed_rows": removed,
        "changed_sample": changed_rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n★ 报告 → %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
