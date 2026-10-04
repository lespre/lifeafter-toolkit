# -*- coding: utf-8 -*-
'''task-85 步1/2（只读取证部分）：自解 res.npk entry 8858 → 权威源尺寸表 + 5 张真图集/候选判定。'''
import io, os, re, sys, json, hashlib, time
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
import gpk_npk_index as G
from npk_reader import unpack_entry
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
P = r'E:\mrzh\res.npk'
TARGET_BYTES = 80369252
rec, rows_fn = G.parse_npk(P)
data = None
for (i, fid, o, ps, ds, fl) in rows_fn():
    if ds != TARGET_BYTES:
        continue
    f = open(P, 'rb'); f.seek(o); raw = f.read(ps); f.close()
    d = unpack_entry(raw, ds, fl)
    if b'"checksum"' in d:
        data = d; print('[解出] entry i=%s fid=%s off=%s comp=%s dec=%s flag=%s -> %d B' % (i, fid, o, ps, ds, fl, len(d)))
        break
if data is None:
    print('!! 未定位到含 "checksum" 的 80,369,252 B 条目'); sys.exit(2)
print('payload 前 300 字节:', data[:300])
NAME_RE = re.compile(rb'([A-Za-z0-9_][A-Za-z0-9_/\.\-]{3,150}\.(?:tga|dds|spr|png))')
CK_RE = re.compile(rb'[Cc]hecksum"?\s*[:=]\s*"?([0-9a-fA-F]{32})')
AL_RE = re.compile(rb'has_alpha"?\s*[:=]\s*(true|false|True|False|1|0)')
SZ_RES = [re.compile(rb'img_size"?\s*[:=]\s*\[\s*(\d+)\s*[, ]\s*(\d+)\s*\]'),
          re.compile(rb'img_size"?\s*[:=]\s*\{?[^0-9]{0,20}(\d+)\s*[,xX ]\s*(\d+)'),
          re.compile(rb'"width"?\s*[:=]\s*(\d+)\s*,\s*"height"?\s*[:=]\s*(\d+)')]
MAN = {}
t0 = time.time()
for m in NAME_RE.finditer(data):
    nm = m.group(1).decode('latin1')
    win = data[m.start():m.start() + 700]
    ck = CK_RE.search(win); al = AL_RE.search(win); sz = None
    for rx in SZ_RES:
        g = rx.search(win)
        if g:
            sz = (int(g.group(1)), int(g.group(2))); break
    if nm not in MAN:
        MAN[nm] = {'checksum': (ck.group(1).decode('latin1').lower() if ck else None),
                   'has_alpha': (al.group(1).decode('latin1').lower() in ('true', '1') if al else None),
                   'dims': sz}
print('[清单] 记录 %d 条（%.1fs）；样例: %s' % (len(MAN), time.time() - t0, json.dumps(dict(list(MAN.items())[:3]), ensure_ascii=False)[:400]))
for probe in ('dian_12.tga', 'glow_01.tga', 'glow_16_yh_djs.tga'):
    hit = [k for k in MAN if k.endswith(probe)]
    print('  阳性对照 %-18s -> %s' % (probe, json.dumps({k: MAN[k] for k in hit[:2]}, ensure_ascii=False)[:260]))
# 收集两皮肤声明名
def collect(skin):
    eff = json.loads(open(os.path.join(W, skin, 'effects.json'), 'rb').read().decode('utf-8'))
    names = {}
    for n in eff['nodes']:
        for k in ('texture', 'texture_candidate', 'texture_binding', 'spr_sheet', 'spr_frames', 'atlas_provenance', 'spr_frames_source', 'spr_source'):
            v = n.get(k)
            if v is None:
                continue
            s = json.dumps(v, ensure_ascii=False)
            for nm in re.findall(r'[A-Za-z0-9_][A-Za-z0-9_/\.\-]*\.(?:tga|dds|spr|png)', s):
                names.setdefault(os.path.basename(nm), []).append('%s:%s' % (n.get('name'), k))
    return eff, names
report = {}
for skin in ('1110177', '1110171'):
    eff, names = collect(skin)
    print()
    print('=== %s：声明名 %d 个 ===' % (skin, len(names)))
    hits = miss = 0
    for nm in sorted(names):
        m = MAN.get(nm)
        if m:
            hits += 1
            print('  %-46s 源 %sx%s  alpha=%s  (用于 %s)' % (nm, (m['dims'] or ('?', '?'))[0], (m['dims'] or ('?', '?'))[1], m['has_alpha'], ','.join(names[nm][:2])))
        else:
            miss += 1
            print('  %-46s **清单 MISS**  (用于 %s)' % (nm, ','.join(names[nm][:2])))
    report[skin] = {'names': {nm: MAN.get(nm) for nm in names}, 'uses': names, 'hits': hits, 'miss': miss}
    print('  命中 %d / 缺 %d' % (hits, miss))
# 5 张真图集帧名
SPRS = ['lightning07_cs.tga', 'lightning_01.tga', 'shandian_05_yh_djs.tga', 'smoke25.tga', 'tex_special_fangkuai_tp52.tga']
print()
print('=== 5 张 .spr 真图集帧名 → 源尺寸 ===')
for s in SPRS:
    m = MAN.get(s)
    print('  %-34s %s' % (s, json.dumps(m, ensure_ascii=False) if m else '清单 MISS'))
json.dump({'manifest_entries': len(MAN), 'source': {'container': 'res.npk', 'entry_bytes': TARGET_BYTES},
           'spr_frame_names': {s: MAN.get(s) for s in SPRS}, 'skins': report},
          io.open(os.path.join(OUT, 'BINDING_AUDIT_20260920.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('机读 -> BINDING_AUDIT_20260920.json', os.path.getsize(os.path.join(OUT, 'BINDING_AUDIT_20260920.json')), 'B（**本轮未改任何 effects.json**）')
