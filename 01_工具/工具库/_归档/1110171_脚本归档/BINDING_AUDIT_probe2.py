# -*- coding: utf-8 -*-
'''task-85 步1 修正版：清单是**全路径**键 ⇒ 用"末段精确相等"匹配；产出权威源尺寸表 + 候选判定。'''
import io, os, re, sys, json, time
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
import gpk_npk_index as G
from npk_reader import unpack_entry
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
P = r'E:\mrzh\res.npk'
rec, rows_fn = G.parse_npk(P)
data = None
for (i, fid, o, ps, ds, fl) in rows_fn():
    if ds != 80369252:
        continue
    f = open(P, 'rb'); f.seek(o); raw = f.read(ps); f.close()
    d = unpack_entry(raw, ds, fl)
    if b'"checksum"' in d:
        data = d; break
assert data is not None
LINE = re.compile(rb'^([A-Za-z0-9_][^\s"]{3,180}\.(?:tga|dds|spr|png)) \{"checksum": "([0-9a-f]{32})", "has_alpha": (\d), "img_size": \[(\d+), (\d+)\]\}', re.M)
MAN = {}
for m in LINE.finditer(data):
    p, ck, al, w, h = m.group(1).decode('latin1'), m.group(2).decode(), m.group(3).decode(), int(m.group(4)), int(m.group(5))
    MAN[p] = {'checksum': ck, 'has_alpha': al == '1', 'dims': [w, h]}
print('[清单] 严格行解析 %d 条（应为 529,370）' % len(MAN))
BY = {}
for p, v in MAN.items():
    BY.setdefault(p.rsplit('/', 1)[-1], []).append({'path': p, 'dims': v['dims'], 'has_alpha': v['has_alpha'], 'checksum': v['checksum']})
print('[索引] 末段名 %d 个；多命中(≥2)的名字数 %d' % (len(BY), sum(1 for v in BY.values() if len(v) > 1)))
for probe in ('dian_12.tga', 'glow_01.tga', 'glow_16_yh_djs.tga'):
    print('  阳性对照 %-22s -> %s' % (probe, json.dumps(BY.get(probe, 'MISS'), ensure_ascii=False)[:300]))
def uses_of(skin):
    eff = json.loads(open(os.path.join(W, skin, 'effects.json'), 'rb').read().decode('utf-8'))
    u = {}
    for n in eff['nodes']:
        for k in ('texture', 'texture_candidate', 'texture_binding', 'spr_sheet', 'spr_frames', 'atlas_provenance', 'spr_frames_source', 'spr_source', 'texture_status'):
            v = n.get(k)
            if v is None:
                continue
            s = json.dumps(v, ensure_ascii=False)
            for nm in re.findall(r'[A-Za-z0-9_][A-Za-z0-9_/\.\-]*\.(?:tga|dds|spr|png)', s):
                u.setdefault(os.path.basename(nm), []).append({'node': n.get('name'), 'field': k, 'dims_ctx': (n.get('spr_sheet') if k in ('texture_candidate', 'atlas_provenance', 'spr_sheet') else None)})
    return eff, u
res = {}
for skin in ('1110177', '1110171'):
    eff, u = uses_of(skin)
    hit = [b for b in u if b in BY]
    print()
    print('=== %s：声明名（末段）%d 个 → 清单命中 %d，MISS %d ===' % (skin, len(u), len(hit), len(u) - len(hit)))
    for b in sorted(u):
        v = BY.get(b)
        if v:
            vv = v[0]
            multi = '' if len(v) == 1 else '（%d 条同名路径！）' % len(v)
            print('  %-44s 源 %sx%s alpha=%-5s %s  ← %s' % (b, vv['dims'][0], vv['dims'][1], vv['has_alpha'], multi,
                  ','.join('%s:%s' % (x['node'], x['field']) for x in u[b][:2])))
        else:
            print('  %-44s **MISS**  ← %s' % (b, ','.join('%s:%s' % (x['node'], x['field']) for x in u[b][:2])))
    res[skin] = {'declared': {b: BY.get(b) for b in u}, 'uses': u}
SPRS = ['lightning07_cs.tga', 'lightning_01.tga', 'shandian_05_yh_djs.tga', 'smoke25.tga', 'tex_special_fangkuai_tp52.tga']
print()
print('=== 5 张 .spr 真图集帧名 → 源尺寸（独立校验用）===')
for s in SPRS:
    v = BY.get(s)
    print('  %-34s %s' % (s, json.dumps(v, ensure_ascii=False)[:260] if v else '清单 MISS'))
json.dump({'manifest_records': len(MAN), 'by_basename': {k: v for k, v in list(BY.items())}, 'skins': res,
           'spr_frame_names': {s: BY.get(s) for s in SPRS}},
          io.open(os.path.join(OUT, 'BINDING_AUDIT_20260920.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('权威表 -> BINDING_AUDIT_20260920.json', os.path.getsize(os.path.join(OUT, 'BINDING_AUDIT_20260920.json')), 'B')
print('**本轮未改任何 effects.json**')
