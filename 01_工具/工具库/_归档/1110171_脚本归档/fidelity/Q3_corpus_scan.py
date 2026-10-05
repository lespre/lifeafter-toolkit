# -*- coding: utf-8 -*-
"""Q3_corpus_scan.py — 从 effect_01/02.gpk 扫出**全部 .sfx（FxGroup 文本）与 .spr 头部**，给 Q3 建立大样本。

口径：gres 多块行表 → 每行 `abs = 该行自己块的 base + off + 20` → zstd(max_output_size)；
判定：GBK 解码后含 `<FxGroup` ⇒ sfx；首行形如 `<mode> <W> <H>` 且第 3 行是整数 ⇒ spr 头。
只读源包；结果写 fidelity/Q3_corpus.json。
"""
import io, json, os, re, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import gpk_npk_index as G
import zstandard as zstd

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
T0 = time.time()


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


rx_tag = re.compile(r'<(/?)([A-Za-z_][A-Za-z0-9_]*)((?:\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*"[^"]*")*)\s*(/?)>')
rx_spr = re.compile(rb'^(\d+)[ \t]+(\d+)[ \t]+(\d+)\r?\n(\d+)\r?\n(\d+)\r?\n')


def attrs(s):
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', s)}


NODE_TAGS = ('Sprite', 'ParticleSystem', 'Model', 'Dummy', 'ParticleRes')
sfx_docs = []
spr_headers = []
files = [r'E:\mrzh\res\effect_01.gpk', r'E:\mrzh\res\effect_02.gpk']
for p in files:
    if not os.path.isfile(p):
        log('MISSING %s' % p)
        continue
    rec, rows_fn, blocks = G._gpk_blockchain(p)
    rows = rows_fn()
    bases = [(b['base'], b['entries']) for b in blocks]
    bi, cum, nxt = 0, 0, bases[0][1]
    n = n_sfx = n_spr = n_fail = 0
    t = time.time()
    with open(p, 'rb') as f:
        for (i, fid, off, comp, dec, fl) in rows:
            n += 1
            while i >= nxt and bi + 1 < len(bases):
                cum = nxt
                bi += 1
                nxt = cum + bases[bi][1]
            base = bases[bi][0]
            try:
                f.seek(base + off + 20)
                blob = f.read(comp)
                data = zstd.ZstdDecompressor().decompress(blob, max_output_size=max(dec, 1) * 4 + 4096) if fl == 12 else blob
            except Exception:
                n_fail += 1
                continue
            if not data:
                continue
            if data[:1] == b'<' and b'FxGroup' in data[:400]:
                txt = data.decode('gbk', 'replace')
                stack, nodes = [], []
                for m in rx_tag.finditer(txt):
                    closing, tag, a, selfclose = m.group(1), m.group(2), attrs(m.group(3)), m.group(4)
                    if closing:
                        if stack:
                            stack.pop()
                        continue
                    if tag in NODE_TAGS:
                        a['_tag'] = tag
                        a['_container'] = os.path.basename(p)
                        a['_row'] = i
                        nodes.append(a)
                    if not selfclose:
                        stack.append(tag)
                if nodes:
                    n_sfx += 1
                    sfx_docs.append({'container': os.path.basename(p), 'row': i, 'bytes': len(data),
                                     'sha16': __import__('hashlib').sha256(data).hexdigest()[:16],
                                     'nodes': nodes})
            else:
                m = rx_spr.match(data[:64])
                if m and int(m.group(1)) <= 4 and int(m.group(4)) < 4096:
                    n_spr += 1
                    spr_headers.append({'container': os.path.basename(p), 'row': i, 'bytes': len(data),
                                        'mode': int(m.group(1)), 'sheet': [int(m.group(2)), int(m.group(3))],
                                        'n_frames': int(m.group(4)), 'param': int(m.group(5)),
                                        'sha16': __import__('hashlib').sha256(data).hexdigest()[:16]})
    log('%s 行 %d 失败 %d → sfx %d / spr %d %.1fs' % (os.path.basename(p), n, n_fail, n_sfx, n_spr, time.time() - t))
    json.dump({'sfx_docs': sfx_docs, 'spr_headers': spr_headers},
              io.open(os.path.join(OUT, 'Q3_corpus.partial.json'), 'w', encoding='utf-8'), ensure_ascii=False)

json.dump({'sfx_docs': sfx_docs, 'spr_headers': spr_headers},
          io.open(os.path.join(OUT, 'Q3_corpus.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('sfx 文档 %d；spr 头 %d -> Q3_corpus.json' % (len(sfx_docs), len(spr_headers)))
