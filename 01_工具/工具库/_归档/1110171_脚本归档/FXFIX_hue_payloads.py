# -*- coding: utf-8 -*-
"""FXFIX_hue_payloads.py — 对 1003_010 的 27 个候选载荷逐个给出：
① 色相（从 uniform 色轨道 u_*color*_Keyframe / ColorFrame 提取 RGB → HSV 分类 蓝紫/青/金/白）
② 节点分布（Model/Sprite/ParticleRes/ParticleSystem/Dummy）
③ mesh 引用（mod_skin_1003_010_zs_* 等）与贴图名
⇒ 按参考图（蓝紫 + 大量 Model 飘带）排序。只读，写 _target_1110171\\FXFIX_*。
"""
import os, re, json, glob, hashlib, collections, colorsys
import xml.etree.ElementTree as ET

D = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
TAGS = {'Sprite', 'ParticleSystem', 'Dummy', 'Model', 'ParticleRes', 'Trail'}


def hue_bucket(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
    if s < 0.15 and v > 0.25:
        return '白/灰'
    d = h * 360
    if d < 20 or d >= 330:
        return '红/品红'
    if d < 70:
        return '金/橙'
    if d < 160:
        return '绿'
    if d < 215:
        return '青/蓝绿'
    if d < 250:
        return '蓝'
    if d < 300:
        return '蓝紫/紫'
    return '品红'


rows = []
for p in sorted(glob.glob(os.path.join(D, 'gpk_effect_01_*.bin'))):
    raw = open(p, 'rb').read()
    if b'<FxGroup' not in raw[:400]:
        continue
    txt = raw.decode('gbk', 'replace')
    if 'skin_1003_010' not in txt:
        continue
    frame = int(re.search(r'_f(\d+)_', os.path.basename(p)).group(1))
    try:
        root = ET.fromstring(txt)
    except Exception as e:
        rows.append({'frame': frame, 'error': str(e)[:80]})
        continue
    tags = collections.Counter()
    meshes, texs = set(), set()
    hues = collections.Counter()
    color_samples = []

    def walk(el):
        if el.tag in TAGS:
            tags[el.tag] += 1
            if el.tag == 'Model' and el.get('ModelName'):
                meshes.add(el.get('ModelName'))
        if el.tag in ('Sprite', 'ParticleSystem') and el.get('Texture'):
            texs.add(el.get('Texture'))
        if re.search(r'color', el.tag, re.I) or el.tag in ('ColorFrame', 'ColorFramePar'):
            for f in el.iter('Frame'):
                vs = (f.get('Value') or '').split(',')
                nums = []
                for x in vs:
                    try:
                        nums.append(float(x))
                    except Exception:
                        pass
                if len(nums) >= 3:
                    r, g, b = nums[-3], nums[-2], nums[-1]
                    w = nums[0] if len(nums) == 4 else 255.0
                    if w > 20 and max(r, g, b) > 8:
                        hb = hue_bucket(r, g, b)
                        hues[hb] += 1
                        if len(color_samples) < 6:
                            color_samples.append({'tag': el.tag, 'rgb': [int(r), int(g), int(b)], 'bucket': hb})
        for ch in el:
            walk(ch)
    walk(root)
    rows.append({'frame': frame, 'bytes': len(raw), 'sha16': hashlib.sha256(raw).hexdigest()[:16],
                 'nodes': sum(tags.values()), 'tags': dict(tags), 'hues': dict(hues),
                 'color_samples': color_samples,
                 'meshes_010': sorted(m.split('\\')[-1] for m in meshes if '1003_010' in m),
                 'meshes_other': sorted(set(m.split('\\')[-1].split('_')[2] for m in meshes if 'skin_1003_010' not in m))[:4],
                 'textures': sorted(t.split('\\')[-1] for t in texs)})
# 排序：Model 数多 + 蓝紫占比高
def rank(r):
    m = (r.get('tags') or {}).get('Model', 0)
    h = r.get('hues') or {}
    tot = sum(h.values()) or 1
    blue = (h.get('蓝', 0) + h.get('蓝紫/紫', 0) + h.get('品红', 0)) / tot
    return (0 if m >= 10 else 1, -blue, -m)
rows.sort(key=rank)
json.dump({'rows': rows}, open(os.path.join(OUT, 'FXFIX_hue_payloads.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('== 27 个候选载荷的色相与节点分布（按 Model 数 + 蓝紫占比排序）==')
print('%-7s %-17s %-5s %-26s %-30s %s' % ('frame', 'sha16', 'nodes', 'tags', '色相分布', 'zs mesh / 关键贴图'))
for r in rows:
    if r.get('error'):
        print('%-7s ERROR %s' % (r['frame'], r['error'])); continue
    ms = [m for m in r['meshes_010'] if '_zs_' in m]
    print('%-7d %-17s %-5d %-26s %-30s %s' % (
        r['frame'], r['sha16'], r['nodes'], json.dumps(r['tags'], ensure_ascii=False),
        json.dumps(r['hues'], ensure_ascii=False), (','.join(ms[:3]) if ms else '-') + ' | ' + ','.join(r['textures'][:3])))
print('\n== 蓝紫占比最高的前 5（含色样例）==')
for r in rows[:5]:
    if r.get('error'):
        continue
    tot = sum((r['hues'] or {}).values()) or 1
    blue = ((r['hues'] or {}).get('蓝', 0) + (r['hues'] or {}).get('蓝紫/紫', 0) + (r['hues'] or {}).get('品红', 0)) / tot
    print('   frame %-7d Model=%-3d 蓝紫占比=%.2f  %s' % (r['frame'], (r['tags'] or {}).get('Model', 0), blue,
                                                        json.dumps(r['color_samples'], ensure_ascii=False)[:180]))
print('json ->', os.path.join(OUT, 'FXFIX_hue_payloads.json'))
