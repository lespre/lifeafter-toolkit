# -*- coding: utf-8 -*-
"""试 uleb128 编码在 bindict payload 里能否找到 1500401 等 id。"""
import pathlib


def uleb(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n % 128
        n //= 128
        out.append(b + (128 if n else 0))
        if not n:
            return bytes(out)


raw = pathlib.Path("01_索引与产物/41_还原树/pe/配置/com/cdata/appear_id_2_equip_id.nxs").read_bytes()
payload = raw[269:264 + 7767]
print("payload", len(payload))
for v in (1500401, 1500402, 3500401, 3500402, 115):
    pat = uleb(v)
    hits = [i for i in range(len(payload)) if payload.startswith(pat, i)][:5]
    print(v, "uleb", pat.hex(), "位置", hits)
