# -*- coding: utf-8 -*-
r"""拿 9/28 的 pkg_N.pi 当基线，判「哪些 fid 是 9.28 之后才有的」，并核对几个具体对象。

基线：01_索引与产物/30_分析/全量拆包复核_20260928/03_download/pi/pkg_*.pi（9/28 官方布局）
现态：post_update_20261017_batch2/pkg_cache/pt/pkg_*.pi（10/16）
参考：batch2_overlay_recheck/prev_pkg/pkg_*.pi（10/15，仅作对照）
"""
from __future__ import annotations

import json
import pathlib

PROJ = pathlib.Path(r"E:/la拆包项目")
BASE0928 = PROJ / "01_索引与产物/30_分析/全量拆包复核_20260928/03_download/pi"
CUR = PROJ / "01_索引与产物/30_分析/热更检测/post_update_20261017_batch2/pkg_cache/pt"
PREV1015 = PROJ / "01_索引与产物/30_分析/热更检测/batch2_overlay_recheck/prev_pkg"
OUT = PROJ / "01_索引与产物/30_分析/热更检测/post_update_20261017_batch2/校验"


def fids(d: pathlib.Path) -> set[str]:
    out = set()
    for f in sorted(d.glob("pkg_*.pi")):
        b = f.read_bytes()
        if len(b) < 8:
            continue
        n = int.from_bytes(b[0:4], "little")
        if n * 8 + 8 != len(b):
            print("  ! 自检不过 %s (%d 条, %d B)" % (f.name, n, len(b)))
            continue
        for i in range(n):
            out.add(b[8 + i * 8: 16 + i * 8].hex().upper())
    return out


a = fids(BASE0928)
b = fids(CUR)
c = fids(PREV1015)
print("9/28 基线 fid：%d" % len(a))
print("10/16 现态 fid：%d" % len(b))
print("10/15 上一批 fid：%d" % len(c))

added_since_0928 = b - a
removed_since_0928 = a - b
print("\n★ 9/28 → 10/16：新增 %d ｜ 移除 %d ｜ 共有 %d"
      % (len(added_since_0928), len(removed_since_0928), len(a & b)))
print("   （对照 10/15 → 10/16：新增 %d）" % len(b - c))

# 具体对象（索引里的 fid 是小端字节反序的 hex，这里两种都试）
CHECK = {
    "兔子背包 0006 r3731": "AB5C59DFF9441E4E",
    "性别卡 0006 r68499": "79B0A2583CFB3CEB",
}


def variants(f: str) -> list[str]:
    raw = bytes.fromhex(f)
    return [f.upper(), raw[::-1].hex().upper()]


print("\n★ 具体对象")
for name, fid in CHECK.items():
    v = variants(fid)
    in0928 = any(x in a for x in v)
    in1015 = any(x in c for x in v)
    in_cur = any(x in b for x in v)
    print("   %-22s fid=%s → 9/28:%s ｜ 10/15:%s ｜ 10/16:%s"
          % (name, fid, in0928, in1015, in_cur))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "对账_9月28基线.json").write_text(json.dumps({
    "baseline": str(BASE0928), "cur": str(CUR),
    "base_fids": len(a), "cur_fids": len(b), "prev1015_fids": len(c),
    "added_since_0928": len(added_since_0928),
    "removed_since_0928": len(removed_since_0928),
    "common": len(a & b),
    "added_1015_to_1016": len(b - c),
    "checks": {k: {"fid": v, "in_0928": any(x in a for x in variants(v)),
                   "in_1015": any(x in c for x in variants(v)),
                   "in_cur": any(x in b for x in variants(v))} for k, v in CHECK.items()},
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n产物 →", OUT / "对账_9月28基线.json")
