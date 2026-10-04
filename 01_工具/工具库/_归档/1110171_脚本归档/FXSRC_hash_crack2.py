# -*- coding: utf-8 -*-
"""FXSRC_hash_crack2.py — 用 fhpk_path_hash_mapping.json 的 1572 组已知 (path, hash) 对反推路径哈希算法。
成功 ⇒ 可对任意逻辑路径算出 idx_hash ⇒ 在 effect.idx 里查到 byte offset/size ⇒ 帧与贴图精确绑定。
"""
import json, os, hashlib, itertools, struct

TOOL = r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\fhpk_path_hash_mapping.json'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
d = json.load(open(TOOL, encoding='utf-8'))
ents = d['entries'][:40]
print('已知对 %d 组（示例 %s → %s）' % (len(d['entries']), ents[0]['path'], ents[0]['hash']))

ALGS = ['md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'blake2s', 'sha3_256', 'sha3_512', 'md5-sha1']
ENCS = ['utf-8', 'utf-16-le', 'utf-16-be', 'latin1', 'gbk']


def variants(p):
    out = set()
    seps = ['/', '\\']
    bases = [p]
    bases.append(p.lower())
    bases.append(p.upper())
    try:
        bases.append(p.encode('gbk').decode('gbk'))
    except Exception:
        pass
    for b in bases:
        for s in seps:
            q = b.replace('/', s).replace('\\', s)
            out.add(q)
            out.add(q.lstrip(s))
            out.add(q + '\x00')
            out.add(os.path.basename(q))
            out.add(os.path.splitext(q)[0])
            out.add(os.path.splitext(os.path.basename(q))[0])
            for pre in ('res/', 'Documents/res/', 'documents/res/', 'res\\', 'Documents\\res\\'):
                out.add(pre + q)
                out.add((pre + q).replace('/', s))
    return sorted(out)


found = []
tested = 0
for e in ents[:6]:
    p, h = e['path'], e['hash']
    for v in variants(p):
        for enc in ENCS:
            try:
                bb = v.encode(enc)
            except Exception:
                continue
            for alg in ALGS:
                try:
                    hh = hashlib.new(alg, bb).hexdigest()
                except Exception:
                    continue
                tested += 1
                if hh[:32] == h.lower():
                    found.append({'path': p, 'variant': v, 'enc': enc, 'alg': alg, 'hash': hh[:32]})
                    print('   ★★ 命中 %s | %s | %s → %s' % (p, repr(v), alg + '/' + enc, hh[:32]))
                    break
            if found:
                break
        if found:
            break
    if found:
        break
print('尝试次数 %d；命中 %d' % (tested, len(found)))
if not found:
    # 打印两组已知，便于人工比对；并试 xxhash/murmur（若装了）
    for e in ents[:2]:
        print('   ', e['path'], '→', e['hash'])
    try:
        import xxhash
        print('   xxhash 可用')
    except Exception as ex:
        print('   xxhash 不可用:', ex)
    try:
        import mmh3
        print('   mmh3 可用')
    except Exception as ex:
        print('   mmh3 不可用:', ex)
    # 结构分析：哈希里是否含日期/长度线索
    print('   哈希前 8 字符分布样例:', [e['hash'][:8] for e in ents[:6]])
json.dump({'tested': tested, 'found': found}, open(os.path.join(OUT, 'FXSRC_hash_crack2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
