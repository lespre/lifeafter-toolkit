"""直接抽 NeoX .py 的字符串池（属性名/方法名 = 语义线索 ✓ 不依赖完整反编译 ✓）"""
import re
from collections import Counter
from pathlib import Path

S = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\ui\weapon_skin')
OUT = Path(r'E:\la拆包项目\03_执行\90_临时\decoded')
OUT.mkdir(parents=True, exist_ok=True)

KEY = ('rotate', 'revolve', 'spin', 'drag', 'mouse', 'touch', 'camera', 'light',
       'weather', 'cube', 'env', 'ibl', 'scene', 'bg', 'preview', 'model',
       'angle', 'yaw', 'pitch', 'scale', 'offset', 'pos', 'move', 'track',
       'show', 'weapon', 'skin', 'fashion', 'panel', 'ui', 'node', 'scene')

for name in ('WeaponSkinPreview.py', 'WeaponSkinExperience.py'):
    p = S / name
    raw = p.read_bytes()
    print('  ── %s (%d B) ──' % (name, len(raw)), flush=True)
    # ① 可读 ASCII 串（长度≥3 ✓ 有界 ✓）
    runs = re.findall(rb'[\x20-\x7E]{3,80}', raw)
    seen = []
    for r in runs:
        s = r.decode('ascii', 'replace')
        if s not in seen:
            seen.append(s)
    print('     可读串去重 %d 条' % len(seen), flush=True)
    (OUT / (name + '.strings.txt')).write_text('\n'.join(seen), encoding='utf-8')

    # ② 带点号的符号（类.方法 ✓ 最能说明结构 ✓）
    dotted = [s for s in seen if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+', s)]
    print('     ★ 带点符号 %d 条:' % len(dotted), flush=True)
    for s in dotted[:60]:
        print('        %s' % s, flush=True)

    # ③ 关键语义串
    hit = [s for s in seen if any(k in s.lower() for k in KEY)]
    print('     ★ 关键语义串 %d 条:' % len(hit), flush=True)
    for s in hit[:70]:
        print('        %s' % s, flush=True)
