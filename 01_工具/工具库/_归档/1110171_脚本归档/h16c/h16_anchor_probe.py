# -*- coding: utf-8 -*-
'''task-91：① 正锚 H_星点粒子_3 邻域 4/8/16 字节字段取证；⑥ H16 表 vs entry 表的"同序关系"验证。只读。'''
import io, os, re, sys, json, hashlib, struct
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
os.makedirs(os.path.join(OUT, 'h16c'), exist_ok=True)
BIN = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'
ANCHOR_PATH = 'effect/textures/glow/star_xing_02_tp165.tga'
ANCHOR_CK = 'f1524e26d09832be95734d4527208051'
TP = os.path.join(OUT, 'h16', 'truth_pairs.json')
res = {'anchor': {'path': ANCHOR_PATH, 'manifest_checksum': ANCHOR_CK}, 'neighborhood': [], 'same_order': None}
# ---------- ① 邻域取证 ----------
txt = io.open(BIN, 'rb').read().decode('gbk', 'replace')
i = txt.find('H_星点粒子_3')
print('[①] H_星点粒子_3 命中偏移 =', i, '（文件 %d B）' % len(txt))
if i >= 0:
    lo = max(0, i - 2048); hi = min(len(txt), i + 2048)
    seg = txt[lo:hi]
    print('    邻域文本片段（含 star_xing / Texture 的行）:')
    for ln in seg.split('\n'):
        s = ln.strip()
        if s and re.search(r'star_xing|Texture|Name|ParticlesPerSecond|FxIgnore|TransparentMode', s):
            print('      ', s[:150])
    # 全文件里搜锚点的常量（md5 / 其 hex / ascii）
    ck_b = bytes.fromhex(ANCHOR_CK)
    raw = io.open(BIN, 'rb').read()
    probes = {'md5_raw16': ck_b, 'md5_ascii': ANCHOR_CK.encode(), 'md5_upper': ANCHOR_CK.upper().encode(),
              'path_ascii': ANCHOR_PATH.encode(), 'path_bs': ANCHOR_PATH.replace('/', '\\').encode(),
              'basename': b'star_xing_02_tp165.tga'}
    for k, b in probes.items():
        p = raw.find(b)
        res['neighborhood'].append({'probe': k, 'found': p >= 0, 'offset': p if p >= 0 else None, 'in_node_block': (lo <= p <= hi) if p >= 0 else None})
        print('    探针 %-12s %s%s' % (k, '命中 @%d' % p if p >= 0 else '未命中', ('（在节点块邻域内）' if p >= 0 and lo <= p <= hi else '')))
    # 邻域内所有 16/8/4 字节字段（按可打印/二进制分别列出）
    NEI = raw[lo:hi]
    u16 = [NEI[j:j + 16] for j in range(0, max(0, len(NEI) - 15))]
    print('    邻域 16B 滑窗 %d 个；与 md5_raw16 相等的滑窗数 = %d' % (len(u16), sum(1 for x in u16 if x == ck_b)))
    res['neighborhood'].append({'probe': '16B_sliding_windows', 'count': len(u16), 'equal_md5': sum(1 for x in u16 if x == ck_b)})
# ---------- ⑥ 同序关系 ----------
if os.path.exists(TP):
    T = json.loads(open(TP, 'rb').read().decode('utf-8'))
    print('[⑥] truth_pairs 类型=%s' % type(T).__name__)
    pairs = T if isinstance(T, list) else (T.get('pairs') or T.get('rows') or next((v for v in T.values() if isinstance(v, list)), []))
    print('    真值对 %d 条；首条键=%s' % (len(pairs), json.dumps(sorted(pairs[0].keys()), ensure_ascii=False) if pairs and isinstance(pairs[0], dict) else '?'))
    if pairs and isinstance(pairs[0], dict):
        anch = [p for p in pairs if ANCHOR_PATH.split('/')[-1] in json.dumps(p, ensure_ascii=False)]
        print('    锚点相关真值对:', json.dumps(anch[:2], ensure_ascii=False)[:400])
    # 同序检验：按 (fpk) 分组，看 H16 下标（若真值给 H16 与 entry_index）是否 == entry_index
    ks = [k for k in ('fpk', 'entry_index', 'H16', 'h16', 'hash', 'path', 'payload_md5') if pairs and isinstance(pairs[0], dict) and k in pairs[0]]
    print('    可用字段:', json.dumps(ks, ensure_ascii=False))
    same = diff = 0; ex = []
    if 'entry_index' in ks and ('H16' in ks or 'h16' in ks):
        for p in pairs:
            e = p.get('entry_index'); h = p.get('H16') or p.get('h16')
            if isinstance(h, int) and isinstance(e, int):
                if h == e: same += 1
                else:
                    diff += 1
                    if len(ex) < 5: ex.append((p.get('fpk'), e, h))
        res['same_order'] = {'int_h16_eq_entry': same, 'int_h16_neq_entry': diff, 'examples': ex,
                             'note': 'H16 若为 16 字节键则不可直接比整数；此处只统计"真值里同时给整型 H16 与 entry_index"的子集'}
        print('    H16(整型) == entry_index: %d ｜ !=: %d ｜ 例: %s' % (same, diff, json.dumps(ex, ensure_ascii=False)))
json.dump(res, io.open(os.path.join(OUT, 'H16_CONSUMER_20260920.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('产物 -> H16_CONSUMER_20260920.json', os.path.getsize(os.path.join(OUT, 'H16_CONSUMER_20260920.json')), 'B（**未改任何 wiki 文件**）')
