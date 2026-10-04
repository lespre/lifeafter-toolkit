"""解码 WeaponSkinPreview.py / WeaponSkinExperience.py ⇒ 可读源码 ⇒ 落盘。"""
import sys
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')

from toolkit_core import script_decode as SD   # noqa: E402

S = Path(r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\ui\weapon_skin')
OUT = Path(r'E:\la拆包项目\03_执行\90_临时\decoded')
OUT.mkdir(parents=True, exist_ok=True)

for name in ('WeaponSkinPreview.py', 'WeaponSkinExperience.py'):
    p = S / name
    if not p.is_file():
        print('  ✗ 缺 %s' % name)
        continue
    print('  ── %s (%d B) ──' % (name, p.stat().st_size))
    try:
        reader, root, end = SD.load_module(str(p))
        print('     reader.error=%r root=%s' % (getattr(reader, 'error', None), type(root).__name__))
        codes = SD.all_codes_from_root(root) if root is not None else []
        if not codes:
            codes = SD.complete_codes(reader)
            print('     降级 complete_codes')
        print('     code 对象 %d 个' % len(codes))
        if hasattr(SD, 'complete_codes'):
            try:
                SD.complete_codes(root)
            except Exception as e:
                print('     complete_codes: %r' % e)
        # 收集字符串池（含属性名/方法名 ⇒ 语义线索 ✓）
        strings = []
        for c in codes:
            for attr in ('co_names', 'co_consts', 'co_varnames', 'names', 'consts'):
                v = getattr(c, attr, None)
                if not v:
                    continue
                for x in v:
                    if isinstance(x, str) and x not in strings:
                        strings.append(x)
        o = OUT / (name + '.strings.txt')
        o.write_text('\n'.join(strings), encoding='utf-8')
        print('     字符串 %d 条 → %s' % (len(strings), o.name))
        # 关键语义筛
        KEY = ('rotate', 'revolve', 'spin', 'drag', 'mouse', 'camera', 'light',
               'weather', 'cube', 'env', 'ibl', 'scene', 'model', 'bg', 'preview')
        hit = [s for s in strings if any(k in s.lower() for k in KEY)]
        print('     ★ 关键串 %d 条:' % len(hit))
        for s in hit[:60]:
            print('        %s' % s)
    except Exception as e:
        import traceback
        print('     ✗ %r' % e)
        traceback.print_exc()
