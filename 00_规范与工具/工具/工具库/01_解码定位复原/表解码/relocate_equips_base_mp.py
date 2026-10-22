# -*- coding: utf-8 -*-
"""多进程全表定位 all_equips BASE：含合法 55 字段 schema(=attrs 6109 形态) 且大量 D6 行。只读。"""
import struct, zlib, os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PKG = r"E:/mrzh/Documents/script.py314.lc.npk"
K = bytes.fromhex('606308d8a32c782013d26c2f226f686d')
CHS = int('94AB0B3FD057EF01', 16)
KNOWN = {1, 3, 5, 11, 17, 18, 34}


def aes(x):
    n = len(x) // 16 * 16
    d = Cipher(algorithms.AES(K), modes.ECB()).decryptor()
    return d.update(x[:n]) + d.finalize() + x[n:]


def unpack(dec):
    for skip in (18, 16, 0):
        for wb in (15, -15):
            try:
                return zlib.decompress(dec[skip:], wb)
            except zlib.error:
                pass


def body_of(raw):
    q = raw.find(b'x{')
    if q < 0:
        return None
    ln = struct.unpack_from('<I', raw, q + 2)[0]
    b = raw[q + 6:q + 6 + ln]
    return b if 0 < ln <= len(raw) else None


def uleb(d, p):
    v = 0; s = 0
    for _ in range(10):
        if p >= len(d):
            return None
        b = d[p]; p += 1; v |= (b & 127) << s
        if not b & 128:
            return v, p
        s += 7
    return None


# 全局：worker 初始化时读一次 CHS 池 + 条目表
_SLOTS = None
_ROWS = None


def _init():
    global _SLOTS, _ROWS
    with open(PKG, 'rb') as f:
        h = aes(f.read(32)); _r, mg, ver, to, n = struct.unpack_from('<QIIII', h)
        f.seek(to); T = aes(f.read(n * 48))
        rows = [struct.unpack_from('<QIIIIIi', T, i * 48) for i in range(n)]
        _ROWS = rows
        for fid, off, ps, ds, a, b2, fl in rows:
            if fid == CHS:
                f.seek(off); raw = unpack(aes(f.read(ps))); body = body_of(raw)
                c, _ = struct.unpack_from('<II', body, 0); te = 8 + 4 * c
                ends = struct.unpack_from(f'<{c}I', body, 8); out = []; last = 0
                for e in ends:
                    out.append(body[te + last:te + e].decode('utf-8', 'replace')); last = e
                _SLOTS = out
                break


def _check(idx):
    fid, off, ps, ds, a, b2, fl = _ROWS[idx]
    if ds < 40000:
        return None  # 武器主表必然较大
    try:
        with open(PKG, 'rb') as f:
            f.seek(off); raw = unpack(aes(f.read(ps)))
        if raw is None:
            return None
        body = body_of(raw)
        if body is None:
            return None
        d6 = body.count(b'\xd6')
        if d6 < 200:
            return None
        # 找 37 37（uleb55,uleb55）+ 55 合法字段
        hit = None
        p = 0
        while True:
            j = body.find(b'\x37\x37', p)
            if j < 0:
                break
            p = j + 1
            q = j + 2; fs = []; ok = True
            for _i in range(55):
                r = uleb(body, q)
                if not r:
                    ok = False; break
                slot, q = r
                if q >= len(body):
                    ok = False; break
                typ = body[q]; q += 1
                if typ not in KNOWN or not (0 <= slot < len(_SLOTS)):
                    ok = False; break
                nm = _SLOTS[slot]
                if not nm or not all(c.isalnum() or c == '_' for c in nm):
                    ok = False; break
                fs.append(nm)
            if ok:
                hit = (j, fs); break
        if hit:
            return {'idx': idx, 'fid': f'{fid:016X}', 'ds': ds, 'body': len(body), 'd6': d6,
                    'schema_at': hit[0], 'f23': hit[1][23], 'f35': hit[1][35], 'fields': hit[1]}
    except Exception:
        return None
    return None


def main():
    _init()
    n = len(_ROWS)
    workers = max(1, min(25, int(os.cpu_count() * 0.8)))
    print("entries", n, "slots", len(_SLOTS), "workers", workers)
    idxs = [i for i in range(n) if _ROWS[i][3] >= 40000]
    print("大 entry 候选", len(idxs))
    hits = []
    with ProcessPoolExecutor(max_workers=workers, initializer=_init) as ex:
        futs = {ex.submit(_check, i): i for i in idxs}
        done = 0
        for fu in as_completed(futs):
            done += 1
            r = fu.result()
            if r:
                hits.append(r); print("命中", r['idx'], r['fid'], 'body', r['body'], 'd6', r['d6'], 'f23', r['f23'], 'f35', r['f35'])
            if done % 200 == 0:
                print("进度", done, "/", len(idxs), "命中", len(hits), flush=True)
    print("\n=== 最终命中 ===")
    for r in hits:
        print(r['idx'], r['fid'], 'body', r['body'], 'f23=', r['f23'], 'f35=', r['f35'])
        print("  fields:", r['fields'])


if __name__ == '__main__':
    main()
