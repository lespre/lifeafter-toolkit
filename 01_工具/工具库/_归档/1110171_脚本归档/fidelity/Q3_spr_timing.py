# -*- coding: utf-8 -*-
"""Q3_spr_timing.py — Q3 精灵帧时序：源字段全量 + .spr 头部 param + 候选公式与反例检查。

源：`.sfx`（GBK XML-like）逐节点属性 + 子 track 的 CycleType/TimeLen；`.spr` 头部（mode W H / N / param / 帧矩形）。
判据：只在**源字段**里找帧推进依据，不引入观感参数。候选公式逐条给数值与反例。
"""
import io, json, math, os, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
SFX = {
    '1110177': [r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_src\fx_skin_2003_029_hit.sfx',
                r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_src\fx_skin_2003_029_jisha.sfx'],
    '1110171': [r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'],
}
SPR = {
    'lightning07_cs.spr': os.path.join(W, '1110177', 'sfx', 'tex', 'lightning07_cs.spr'),
    'lightning_01.spr': os.path.join(W, '1110177', 'sfx', 'tex', 'lightning_01.spr'),
    'shandian_05_yh_djs.spr': os.path.join(W, '1110177', 'sfx', 'tex', 'shandian_05_yh_djs.spr'),
    'smoke25.spr': os.path.join(W, '1110177', 'sfx', 'tex', 'smoke25.spr'),
    'tex_special_fangkuai_tp52.spr': os.path.join(W, '1110177', 'sfx', 'tex', 'tex_special_fangkuai_tp52.spr'),
    'tex_glow_tp07_02.spr': os.path.join(W, '1110171', 'sfx', 'tex', 'tex_glow_tp07_02.spr'),
}
NODE_TAGS = ('FxGroup', 'Sprite', 'ParticleSystem', 'Model', 'Dummy', 'ParticleRes', 'Decal', 'Light')
rx_tag = re.compile(r'<(/?)([A-Za-z_][A-Za-z0-9_]*)((?:\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*"[^"]*")*)\s*(/?)>')


def attrs(s):
    return {m.group(1): m.group(2) for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"([^"]*)"', s)}


def parse_sfx(path):
    raw = open(path, 'rb').read()
    txt = raw.decode('gbk', 'replace')
    nodes = []
    stack = []
    for m in rx_tag.finditer(txt):
        closing, tag, a, selfclose = m.group(1), m.group(2), attrs(m.group(3)), m.group(4)
        depth = len(stack)
        if closing:
            if stack:
                stack.pop()
            continue
        rec = {'tag': tag, 'attrs': a, 'depth': depth, 'tracks': []}
        if stack and stack[-1]['tag'] in NODE_TAGS and stack[-1]['tag'] != 'FxGroup' and not stack[-1].get('_closed'):
            stack[-1]['tracks'].append(rec)
        if tag in NODE_TAGS:
            nodes.append(rec)
            if not selfclose:
                stack.append(rec)
        elif selfclose:
            pass
        else:
            stack.append({'_nonnode': True, 'tag': tag})
    return txt, nodes


def spr_header(p):
    b = open(p, 'rb').read()
    txt = b[:200].decode('latin1', 'replace')
    lines = txt.split('\r\n')
    head = lines[0].split()
    n = int(lines[1]) if len(lines) > 1 else 0
    param = int(lines[2]) if len(lines) > 2 else None
    rects = []
    for ln in lines[3:3 + n]:
        parts = ln.split()
        if len(parts) == 5:
            rects.append([int(x) for x in parts[1:]])
    return {'mode': int(head[0]), 'sheet': [int(head[1]), int(head[2])], 'n_frames': n, 'param': param,
            'rects': rects, 'bytes': len(b)}


print('=== .spr 头部（源文件） ===')
sprs = {}
for name, p in SPR.items():
    if os.path.isfile(p):
        h = spr_header(p)
        sprs[name] = h
        cell = h['sheet'][0] // max(1, int(math.sqrt(h['n_frames'])))
        print('  %-30s mode=%d sheet=%dx%d n=%d param=%d bytes=%d' % (
            name, h['mode'], h['sheet'][0], h['sheet'][1], h['n_frames'], h['param'], h['bytes']))
    else:
        print('  %-30s MISSING %s' % (name, p))

print('\n=== sfx 源节点：spr 相关字段 ===')
allnodes = {}
for sid, paths in SFX.items():
    for p in paths:
        if not os.path.isfile(p):
            print('  sfx MISSING %s' % p)
            continue
        txt, nodes = parse_sfx(p)
        print('-- %s（%s，%d 字节，解析节点 %d）' % (os.path.basename(p), sid, len(txt.encode('gbk', 'replace')), len(nodes)))
        for n in nodes:
            a = n['attrs']
            tag = n['tag']
            tex = a.get('Texture', '')
            if tag in ('Sprite', 'ParticleSystem', 'ParticleRes', 'Decal') or 'SprSpeedRate' in a:
                keys = ['Name', 'Texture', 'SprWorkMode', 'SprSpeedRate', 'SprStartRandom', 'RandomStartSpr',
                        'IsSprBlend', 'TextureClockRotate', 'TextureFlip', 'TextureRatio', 'ScaleStyle',
                        'SpriteScale', 'SpriteHeight', 'HWRatio', 'BlendMode', 'TrackType', 'FxLifeSpan',
                        'FxStartTime', 'ColorType', 'EffectColorName', 'DecalColorName', 'Radius', 'MinRadius',
                        'MaxRadius', 'MinSpriteLifespan', 'MaxSpriteLifespan', 'ParticlesPerSecond']
                rec = {k: a[k] for k in keys if k in a}
                tracks = {}
                for t in n['tracks']:
                    tracks[t['tag']] = {k: t['attrs'][k] for k in ('TimeLen', 'CycleType', 'YZCopyFromX',
                                                                   'TrackActionType', 'TrackCacheType') if k in t['attrs']}
                rec['tracks'] = tracks
                allnodes.setdefault(sid, []).append(rec)
                print('   %-18s %-10s tex=%-52s SprWorkMode=%-3s SprSpeedRate=%-7s FxLifeSpan=%-6s tracks=%s' % (
                    a.get('Name', '?'), tag, (tex or '-')[-52:], a.get('SprWorkMode'), a.get('SprSpeedRate'),
                    a.get('FxLifeSpan'), json.dumps(tracks, ensure_ascii=False)))
        # 还打印带 SprSpeedRate=0 / SprWorkMode=1 的节点
        for n in nodes:
            if n['attrs'].get('SprSpeedRate') == '0.000' or n['attrs'].get('SprWorkMode') == '1':
                print('   ⚠ SprWorkMode/SprSpeedRate 特殊: %s' % json.dumps(
                    {k: n['attrs'].get(k) for k in ('Name', 'SprWorkMode', 'SprSpeedRate', 'Texture', 'FxLifeSpan')},
                    ensure_ascii=False))

print('\n=== 6 个 spr 节点的源字段表（与 effects.json 的 atlas 对应） ===')
json.dump({'spr_headers': sprs, 'sfx_nodes': allnodes}, io.open(os.path.join(OUT, 'Q3_spr_timing.json'), 'w',
          encoding='utf-8'), ensure_ascii=False, indent=1)
print('-> Q3_spr_timing.json（阶段 1：源字段提取完成）')
