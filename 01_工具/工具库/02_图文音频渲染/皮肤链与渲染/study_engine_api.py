"""RenderHelpers 全量字符串 → 按主题归类 ⇒ 形成【引擎渲染 API 手册】（学透用 ✓）"""
import re
from collections import defaultdict
from pathlib import Path

S = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk')
SUF = r'E:\la拆包项目\03_执行\90_临时\decoded'

TOPIC = {
    '场景': ('scene', 'ui_scene', 'render_scene', 'scn', 'renderobject', 'render_object'),
    '相机': ('camera', 'cam_', 'fov', 'view_', 'look_at', 'projection'),
    '光照': ('light', 'lamp', 'sun', 'shadow', 'illum', 'brightness', 'intensity'),
    '天气/环境': ('weather', 'env', 'sky', 'fog', 'cloud', 'sun_color', 'ibl', 'cube', 'atmo'),
    '后处理': ('postprocess', 'post_process', 'bloom', 'tonemap', 'tone_map', 'lut',
               'exposure', 'hdr', 'aa_', 'taa', 'dlss', 'ssao', 'dof', 'color_grade'),
    'SSR/反射': ('ssr', 'sssr', 'reflect', 'reflection', 'refract'),
    '材质/贴图': ('material', 'texture', 'tex_', 'map', 'shader', 'mat_', 'replace'),
    '模型': ('model', 'mesh', 'skeleton', 'anim', 'bone', 'attach', 'part'),
    '特效': ('effect', 'sfx', 'flash', 'glow', 'emissive', 'particle', 'fx'),
    '相机控制': ('rotate', 'drag', 'touch', 'zoom', 'scale', 'offset', 'position', 'move'),
}


def strs_of(rel):
    p = S / rel
    if not p.is_file():
        return None
    raw = p.read_bytes()
    u = []
    for m in re.finditer(rb'[\x20-\x7E]{3,110}', raw):
        s = m.group(0).decode('ascii', 'replace')
        if s not in u:
            u.append(s)
    return u


TARGETS = [
    'com/utils/RenderHelpers.py',
    'ui/weapon_skin/WeaponSkinPreview.py',
    'ui/PanelFashionPreview.py',
    'ui/commonui/CommonModelShowUI.py',
]
out = Path(SUF)
out.mkdir(parents=True, exist_ok=True)

for rel in TARGETS:
    u = strs_of(rel)
    if u is None:
        print('  ✗ 缺 %s' % rel)
        continue
    print()
    print('█' * 70)
    print('██ %s（%d 串）' % (rel, len(u)))
    print('█' * 70)
    buckets = defaultdict(list)
    for s in u:
        low = s.lower()
        for topic, keys in TOPIC.items():
            if any(k in low for k in keys):
                buckets[topic].append(s)
                break
    for topic in TOPIC:
        lst = buckets.get(topic) or []
        if not lst:
            continue
        print()
        print('  ◆◆ %s（%d）' % (topic, len(lst)))
        for s in lst[:70]:
            print('      %s' % s)
    (out / (rel.replace('/', '_') + '.bytopic.txt')).write_text(
        '\n'.join('%s\t%s' % (t, s) for t, lst in buckets.items() for s in lst),
        encoding='utf-8')
