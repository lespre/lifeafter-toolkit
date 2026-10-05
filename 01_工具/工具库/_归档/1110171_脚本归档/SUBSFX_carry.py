# -*- coding: utf-8 -*-
'''task-72：拆 ParticleRes 子特效 js_04 / zs_01 → 解析节点树 + .spr 真图集导出 + 合并进两把皮肤。
用法：python SUBSFX_carry.py --dry-run   # 只解析/解析图集可达性，不写任何文件
      python SUBSFX_carry.py             # copy2 备份 → 导图集 → 合并 → 出报告'''
import io, os, re, sys, json, hashlib, shutil, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import locate_skeleton as LS
import spr_atlas_resolver as SAR
DRY = '--dry-run' in sys.argv
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
REP = os.path.join(OUT, 'SUBSFX_report.md')
ASSETS = os.path.join(OUT, 'SUBSFX_assets.json')
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite', 'Trail')
JOBS = [
    {'skin': '1110177', 'parent': 'M_ParticleRes',
     'path': r'effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_js_04.sfx', 'subdir': 'sfx/sub'},
    {'skin': '1110171', 'parent': '<2×ParticleRes>',
     'path': r'effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_zs_01.sfx', 'subdir': 'sfx/sub'},
]
g = LS.GpkIndex()

def frames_of(body):
    out = []
    for fm in re.finditer(r'<Frame\s+([^>/]*)/?>', body):
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', fm.group(1)))
        if 'Time' not in a or 'Value' not in a:
            continue
        v = a['Value']
        val = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', v)] if ',' in v else (
            float(v) if re.match(r'^-?\d+(\.\d+)?$', v.strip()) else v)
        out.append({'time': float(a['Time']), 'value': val})
    return out

def parse_nodes(txt):
    out = []
    for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), txt):
        tag, at = m.group(1), m.group(2)
        nxt = re.search(r'<(?:%s)\b' % '|'.join(TAGS), txt[m.end():])
        blk = txt[m.end():(m.end() + nxt.start()) if nxt else (m.end() + 60000)]
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
        if not a.get('Name'):
            continue
        tex = sorted(set(re.findall(r'[A-Za-z0-9_\\/\.\-]+\.(?:spr|tga)', blk)))
        emit = {}
        for cm in re.finditer(r'<([A-Za-z_]\w*)\b([^>]*?)(?:/>|>(.*?)</\1>)', blk, re.S):
            if cm.group(1) in TAGS or cm.group(1) in ('FxGroup', 'Semantic', 'Variables', 'Macros', 'Uniforms', 'ShaderComponent'):
                continue
            fr = frames_of(cm.group(3) or '')
            if fr:
                emit[cm.group(1)] = fr
        out.append({'tag': tag, 'attrs': a, 'textures': tex, 'emit': emit, 'block_len': len(blk)})
    return out

# 图集索引
IDX = os.path.join(os.environ.get('TEMP', '.'), 'spr_atlas_index.json')
IDXJ = json.loads(open(IDX, 'rb').read().decode('utf-8')) if os.path.exists(IDX) else None
print('[索引] spr_atlas_index 顶层类型=%s' % (type(IDXJ).__name__ if IDXJ is not None else 'None'))
SPRMAP = {}
def walk_idx(o, ctx=''):
    if isinstance(o, dict):
        nm = o.get('name') or o.get('spr') or o.get('file')
        if nm and (o.get('row') is not None):
            SPRMAP[str(nm)] = {'container': o.get('container'), 'row': o.get('row')}
        for k, v in o.items():
            walk_idx(v, k)
    elif isinstance(o, list):
        for v in o:
            walk_idx(v, ctx)
if IDXJ is not None:
    walk_idx(IDXJ)
    if not SPRMAP and isinstance(IDXJ, dict):
        # 形如 {"<name>": {container,row}} 或 {"<name>": row}
        for k, v in IDXJ.items():
            if isinstance(v, dict) and v.get('row') is not None:
                SPRMAP[k] = {'container': v.get('container'), 'row': v.get('row')}
            elif isinstance(v, int):
                SPRMAP[k] = {'container': v.get('container') if isinstance(v, dict) else None, 'row': v}
print('[索引] 可解析 .spr→row 条目数: %d；样例: %s' % (len(SPRMAP), json.dumps(dict(list(SPRMAP.items())[:3]), ensure_ascii=False)[:300]))

results = []
for j in JOBS:
    print()
    print('=== %s  %s ===' % (j['skin'], j['path']))
    d, meta = g.read(j['path'])
    if not d:
        print('  !! 按名 MISS'); results.append({'job': j, 'found': False}); continue
    sha = hashlib.sha256(d).hexdigest()[:16].upper()
    print('  [定位] container=%s row=%s off=%s comp=%s dec=%s flag=%s  bytes=%d sha16=%s' % (
        meta.get('container'), meta.get('row'), meta.get('off'), meta.get('comp'), meta.get('dec'), meta.get('flag'), len(d), sha))
    txt = d.decode('gbk', 'replace')
    nodes = parse_nodes(txt)
    from collections import Counter
    print('  [节点] %d 个  类型=%s' % (len(nodes), json.dumps(dict(Counter(n['tag'] for n in nodes)), ensure_ascii=False)))
    alltex = sorted({t for n in nodes for t in n['textures']})
    print('  [贴图声明] %s' % json.dumps(alltex, ensure_ascii=False))
    for n in nodes:
        a = n['attrs']
        print('   %-22s %-14s start=%s life=%s FxIgnore=%s rate=%s life2=%s MinScale=%s MaxScale=%s emit=%d 轨 tex=%s' % (
            a.get('Name'), n['tag'], a.get('FxStartTime'), a.get('FxLifeSpan'), a.get('FxIgnore'),
            a.get('ParticlesPerSecond'), (a.get('MinSpriteLifespan') or '') + '/' + (a.get('MaxSpriteLifespan') or ''),
            a.get('MinScale'), a.get('MaxScale'), len(n['emit']), json.dumps(n['textures'], ensure_ascii=False)[:60]))
    # 图集可达性
    atlas = []
    for t in alltex:
        base = os.path.basename(t.replace('/', '\\'))
        hit = SPRMAP.get(base) or SPRMAP.get(t)
        atlas.append({'tex': t, 'kind': t.split('.')[-1].lower(), 'spr_row': (hit or {}).get('row'),
                      'container': (hit or {}).get('container'), 'resolvable': bool(hit)})
    print('  [图集] %s' % json.dumps(atlas, ensure_ascii=False)[:400])
    results.append({'job': j, 'found': True, 'meta': meta, 'sha16': sha, 'bytes': len(d),
                    'nodes': nodes, 'textures': alltex, 'atlas': atlas})
if DRY:
    print()
    print('** dry-run：未写任何文件 **')
    json.dump([{k: v for k, v in r.items() if k != 'nodes'} for r in results], io.open(os.path.join(OUT, 'SUBSFX_dryrun.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('dry-run 摘要 -> SUBSFX_dryrun.json')
    sys.exit(0)
