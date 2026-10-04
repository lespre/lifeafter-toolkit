# -*- coding: utf-8 -*-
"""FXSRC_parse_new.py — 解析 1110152 / 1110024 的源级 .sfx，检查节点/颜色能否解释参考图（青 / 金）。只读+写本目录。"""
import os, sys, json, importlib.util, collections

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
EX = os.path.join(OUT, 'FXSRC_exact')
TOOL = r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\parse_sfx_tracks.py'
spec = importlib.util.spec_from_file_location('pst', TOOL)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def hue(r, g, b):
    import colorsys
    return colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)


rep = {}
for tag, fn in (('1110152', 'sibling_fx_skin_1012_009_idle_01.sfx'),
                ('1110024', 'sibling_fx_skin_1006_004_zishen.sfx')):
    src = os.path.join(EX, fn)
    dst = os.path.join(OUT, 'FXSRC_tracks_%s.json' % tag)
    mod.main(src, dst)
    d = json.load(open(dst, encoding='utf-8'))
    nodes = d['nodes']
    tags = collections.Counter(n['tag'] for n in nodes)
    tex = collections.Counter()
    hues = []
    for n in nodes:
        if n.get('texture'):
            tex[n['texture']] += 1
        ck = n['tracks'].get('ColorFrame') or n['tracks'].get('ColorFramePar') or []
        for f in ck:
            v = f['value']
            if len(v) >= 4:
                a, r, g, b = v[0], v[1], v[2], v[3]
                if a > 20:
                    h, s, vv = hue(r, g, b)
                    hues.append({'node': n['name'], 'h': round(h * 360, 1), 's': round(s, 2), 'v': round(vv, 2), 'rgba': v})
    # 颜色判定
    cyan = [x for x in hues if 150 <= x['h'] <= 210 and x['s'] > 0.2 and x['v'] > 0.2]
    gold = [x for x in hues if 20 <= x['h'] <= 70 and x['s'] > 0.2 and x['v'] > 0.2]
    rep[tag] = {'file': fn, 'bytes': d.get('source'), 'node_count': d['node_count'],
                'tags': dict(tags), 'textures': dict(tex),
                'color_frames_total': len(hues),
                'cyan_like_frames': len(cyan), 'gold_like_frames': len(gold),
                'cyan_examples': cyan[:5], 'gold_examples': gold[:5],
                'anomalies': len(d.get('anomalies') or [])}
    print('== %s  %s' % (tag, fn))
    print('   节点 %d  %s' % (d['node_count'], json.dumps(dict(tags), ensure_ascii=False)))
    print('   贴图引用 %d 种: %s' % (len(tex), json.dumps(dict(tex), ensure_ascii=False)[:400]))
    print('   色帧总数 %d；青色调频帧 %d；金色调帧 %d' % (len(hues), len(cyan), len(gold)))
    for x in cyan[:3]:
        print('      青:', x)
    for x in gold[:3]:
        print('      金:', x)
    print('   animations/anomalies:', rep[tag]['anomalies'])
json.dump(rep, open(os.path.join(OUT, 'FXSRC_parse_new.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_parse_new.json'))
