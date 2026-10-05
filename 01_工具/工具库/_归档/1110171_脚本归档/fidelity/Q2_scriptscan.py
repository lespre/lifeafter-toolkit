# -*- coding: utf-8 -*-
"""Q2_scriptscan.py（v3，bytes.count 预筛版）— Q2 枚举表猎取：全部 NPK 条目载荷关键词扫描。

性能历程（如实登记）：
  v1：每载荷 27 关键词 × 2 编码 = 54 次 re.finditer ⇒ >10 分钟仅完成半个容器（未完成）。
  v2：合并为 1 个交替正则 ⇒ 实测 1.77 GB 需 99.6s（226k 命中 ⇒ finditer 的 match 对象开销是瓶颈）。
  v3（本版）：先用 C 速度的 `bytes.lower()` + `bytes.count()` 数命中（每关键词一次 memchr 级扫描），
      只有 count>0 的载荷才用正则取上下文 ⇒ 全量 15.4 GB 预期 3–6 分钟。
只读源包；命中载荷落盘到 fidelity/q2_payloads/。
"""
import hashlib, io, json, os, re, sys, time
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import gpk_npk_index as G
from npk_reader import unpack_entry
import zstandard as zstd
import lz4.block as lz4b

T = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
HITS = os.path.join(T, 'q2_payloads')
os.makedirs(HITS, exist_ok=True)
T0 = time.time()


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


def unpack_fast(raw, ds, fl):
    try:
        if fl == 2:
            return lz4b.decompress(raw, uncompressed_size=ds)
        if fl == 12:
            return zstd.ZstdDecompressor().decompress(raw, max_output_size=max(ds, 1) * 4 + 4096)
    except Exception:
        return unpack_entry(raw, ds, fl)
    return unpack_entry(raw, ds, fl)


KW = ['BlendMode', 'blend_mode', 'BlendModeType', 'BlendSrc', 'BlendDst', 'SrcBlend', 'DstBlend',
      'AlphaBlend', 'AdditiveBlend', 'BlendOp', 'DEFAULT_BLEND_MODE', 'BLEND_STATE_OPTION',
      'TransparentMode', 'SprWorkMode', 'SprSpeedRate', 'IsSprBlend', 'CycleType', 'TrackType',
      'ColorKeyFrame', 'ColorFrame', 'RenderBias', 'DirType']
KWL = [(k, k.lower().encode('ascii')) for k in KW]
KWU = [(k, b'\x00'.join(bytes([c]) for c in k.lower().encode('ascii'))) for k in KW]
RX_CTX = {k: re.compile(re.escape(k.encode('ascii')), re.I) for k in KW}
RX_CTX_U = {k: re.compile(re.escape(b'\x00'.join(bytes([c]) for c in k.encode('ascii'))), re.I) for k in KW}

TARGETS = [r'E:\mrzh\res.npk', r'E:\mrzh\res\ui.npk', r'E:\mrzh\script.npk',
           r'E:\mrzh\script.py314.lc.npk', r'E:\mrzh\Documents\script.npk',
           r'E:\mrzh\Documents\script.py3.npk', r'E:\mrzh\Documents\script.py314.lc.npk',
           r'E:\LifeAfter\res.npk', r'E:\LifeAfter\res\ui.npk', r'E:\LifeAfter\script.npk',
           r'E:\LifeAfter\script.py3.npk', r'E:\LifeAfter\script.py314.lc.npk',
           r'E:\LifeAfter\Documents\script.npk', r'E:\LifeAfter\Documents\script.py3.npk',
           r'E:\LifeAfter\Documents\script.py314.lc.npk']
TARGETS = [p for p in TARGETS if os.path.isfile(p)]
res = {'schema': 'Q2_script_scan/v3', 'method': 'bytes.lower()+count() 预筛，命中者才取上下文', 'keywords': KW,
       'containers': [], 'hits': [], 'totals': {'containers': 0, 'entries': 0, 'unpacked': 0, 'fail': 0,
                                                'bytes_scanned': 0}, 'kw_counts': {}, 'entries_with_any_hit': 0}
kwc = Counter()
payload_writes = 0

for p in TARGETS:
    base = os.path.basename(p)
    rec, rows_fn = G.parse_npk(p)
    st = {'npk': p, 'bytes_file': rec['bytes'], 'entries': rec['entries'], 'unpacked': 0, 'fail': 0,
          'bytes_scanned': 0, 'hits': 0, 'entries_with_hit': 0, 'seconds': 0}
    t = time.time()
    fh = open(p, 'rb')
    try:
        for (i, fid, off, ps, ds, fl) in rows_fn():
            if not (0 < off < rec['bytes'] and 0 <= ps <= rec['bytes'] - off):
                st['fail'] += 1
                continue
            try:
                fh.seek(off)
                data = unpack_fast(fh.read(ps), ds, fl)
            except Exception:
                st['fail'] += 1
                continue
            st['unpacked'] += 1
            st['bytes_scanned'] += len(data)
            if not data:
                continue
            low = data.lower()
            hit_here = 0
            for k, kl in KWL:
                c = low.count(kl)
                if c:
                    hit_here += c
                    kwc[k] += c
            for k, ku in KWU:
                c = low.count(ku)
                if c:
                    hit_here += c
                    kwc[k + '@utf16'] += c
            if hit_here:
                st['hits'] += hit_here
                st['entries_with_hit'] += 1
                res['entries_with_any_hit'] += 1
                for k, kl in KWL:
                    for m in list(RX_CTX[k].finditer(data))[:3]:
                        a, b = max(0, m.start() - 160), min(len(data), m.end() + 200)
                        res['hits'].append({'npk': base, 'entry': i, 'fid': '%016x' % fid, 'flag': fl,
                                            'entry_bytes': len(data), 'keyword': k, 'enc': 'ascii',
                                            'off': m.start(), 'ctx': data[a:b].decode('utf-8', 'replace'),
                                            'payload_sha16': hashlib.sha256(data).hexdigest()[:16]})
            if (b'blendmode' in low or b'blend_mode' in low) and payload_writes < 400:
                fn = '%s_e%d_%s.bin' % (base.replace('.', '_'), i, hashlib.sha256(data).hexdigest()[:12])
                fp = os.path.join(HITS, fn)
                if not os.path.exists(fp):
                    open(fp, 'wb').write(data)
                    payload_writes += 1
            if st['unpacked'] % 50000 == 0:
                log('   %s 进度 %d/%d 命中 %d' % (base, st['unpacked'], rec['entries'], st['hits']))
    finally:
        fh.close()
    st['seconds'] = round(time.time() - t, 1)
    res['containers'].append(st)
    res['totals']['containers'] += 1
    for k in ('entries', 'unpacked', 'fail', 'bytes_scanned'):
        res['totals'][k] += st[k]
    log('%-28s 条目 %-7d 解出 %-7d 失败 %-4d 扫描 %6.2f GB 命中 %-8d 命中条目 %-5d %5.1fs' % (
        base, st['entries'], st['unpacked'], st['fail'], st['bytes_scanned'] / 1e9, st['hits'],
        st['entries_with_hit'], st['seconds']))
    json.dump(res, io.open(os.path.join(T, 'Q2_scriptscan.partial.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

res['kw_counts'] = dict(kwc.most_common())
res['payloads_saved'] = payload_writes
json.dump(res, io.open(os.path.join(T, 'Q2_scriptscan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n=== 合计：容器 %d / 条目 %d / 解出 %d / 失败 %d / 扫描 %.2f GB / 命中条目 %d ===' % (
    res['totals']['containers'], res['totals']['entries'], res['totals']['unpacked'], res['totals']['fail'],
    res['totals']['bytes_scanned'] / 1e9, res['entries_with_any_hit']))
print('=== 关键词命中：%s' % json.dumps(res['kw_counts'], ensure_ascii=False))
print('=== 落盘命中载荷 %d 个 -> %s' % (payload_writes, HITS))
