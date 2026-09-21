import sys, os, time
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体')
from toolkit_core.fpk_frames import iter_fpk_frames
targets = [
    r'E:\mrzh\res\weapon.gpk',
    r'E:\mrzh\res\utility.gpk',
    r'E:\mrzh\res\textures.gpk',
]
for t in targets:
    if not os.path.exists(t):
        print('MISS', t); continue
    t0 = time.time(); n = 0; hits = []
    try:
        for fr in iter_fpk_frames(t):
            n += 1
            name = (fr.get('name') or b'').decode('latin1', 'replace') if isinstance(fr.get('name'), bytes) else str(fr.get('name') or '')
            nl = name.lower()
            if 'qiangpi' in nl or nl.endswith('.cube'):
                hits.append((name, fr.get('offset'), fr.get('size')))
    except Exception as e:
        print('ERR', t, e)
    print('%s frames=%d hits=%d %.0fs' % (os.path.basename(t), n, len(hits), time.time() - t0))
    for h in hits[:40]:
        print('   HIT', h)
