"""抽 RenderHelpers / PostProcessHelpers / weapon_skin_data 等关键模块的字符串（语义线索 ✓）"""
import re
from pathlib import Path

S = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk')
OUT = Path(r'E:\la拆包项目\03_执行\90_临时\decoded')
OUT.mkdir(parents=True, exist_ok=True)

CAND = [
    'com/utils/RenderHelpers.py',
    'com/utils/FashionCharmHelpers.py',
    'com/cdata/weapon_skin_data.py',
    'com/cdata/weapon_skin_base_conf.py',
    'com/utils/EquipSkinHelpers.py',
]
# 找 PostProcessHelpers 与 engine_utils
for pat in ('PostProcessHelpers', 'engine_utils'):
    for p in S.rglob('*%s*' % pat):
        if p.is_file():
            CAND.append(str(p.relative_to(S)).replace('\\', '/'))

KEY = ('rotate', 'revolve', 'spin', 'drag', 'mouse', 'touch', 'camera', 'light',
       'weather', 'cube', 'env', 'ibl', 'scene', 'model', 'angle', 'yaw', 'pitch',
       'scale', 'offset', 'position', 'show', 'create', 'add', 'set', 'helper',
       'post', 'tonemap', 'lut', 'bloom', 'exposure', 'bg', 'env_map', 'sky',
       'sun', 'shadow', 'fog', 'ambient', 'ssr', 'reflect')

seen_files = set()
for rel in CAND:
    p = S / rel
    if not p.is_file() or rel in seen_files:
        continue
    seen_files.add(rel)
    raw = p.read_bytes()
    print('  ── %s (%d B) ──' % (rel, len(raw)), flush=True)
    runs = re.findall(rb'[\x20-\x7E]{3,90}', raw)
    u = []
    for r in runs:
        s = r.decode('ascii', 'replace')
        if s not in u:
            u.append(s)
    (OUT / (rel.replace('/', '_') + '.strings.txt')).write_text('\n'.join(u), encoding='utf-8')
    dotted = [s for s in u if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+', s)]
    hit = [s for s in u if any(k in s.lower() for k in KEY)]
    print('     串 %d · 带点 %d · 关键 %d' % (len(u), len(dotted), len(hit)), flush=True)
    for s in dotted[:45]:
        print('     . %s' % s, flush=True)
    for s in hit[:55]:
        print('     * %s' % s, flush=True)
