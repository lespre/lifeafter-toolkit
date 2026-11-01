# -*- coding: utf-8 -*-
"""串图巡检：全量比对动图，找出「首帧完全相同」的条目对（正常不会出现）。"""
import collections
import hashlib
import pathlib

from PIL import Image, ImageSequence

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
ANIM = WEB / "assets/avatar_anim"

h0 = collections.defaultdict(list)
hfull = collections.defaultdict(list)
for p in sorted(ANIM.glob("*.png")):
    try:
        im = Image.open(p)
        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(im)]
    except Exception as ex:          # noqa: BLE001
        print("读失败", p.name, ex)
        continue
    if not frames:
        continue
    h0[hashlib.md5(frames[0].tobytes()).hexdigest()].append(p.stem)
    allb = b"".join(hashlib.md5(f.tobytes()).digest() for f in frames)
    hfull[hashlib.md5(allb).hexdigest()].append(p.stem)

print("动图总数", sum(len(v) for v in h0.values()))
dups0 = {k: v for k, v in h0.items() if len(v) > 1}
dupf = {k: v for k, v in hfull.items() if len(v) > 1}
print("首帧重复组", len(dups0))
for v in list(dups0.values())[:20]:
    print("  ", v)
print("整组帧完全相同", len(dupf))
for v in list(dupf.values())[:20]:
    print("  ", v)
