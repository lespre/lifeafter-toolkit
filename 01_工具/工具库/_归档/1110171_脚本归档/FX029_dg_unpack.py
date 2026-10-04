# -*- coding: utf-8 -*-
'''task-62 步1：解出 _dg.sfx（gres\0057.gpk row 32153）→ 节点/驱动清单（只读 + 落盘清单 JSON）'''
import io, json, os, re, sys, hashlib, struct
sys.stdout.reconfigure(encoding='utf-8')
GPK = r'E:\mrzh\Documents\gres\0057.gpk'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\GAP_1110177_dg_20260919.md'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_inventory.json'
BLOCK_BASE = 1823837828
ROW = 32153

# 从 env-auditor 报告的 JSON 附录取该行字段（避免手抄）
rep = io.open(REP, 'rb').read().decode('utf-8', 'replace')
blocks = re.findall(r'```json\s*(.*?)```', rep, re.S)
info = None
for b in blocks:
    try:
        j = json.loads(b)
    except Exception:
        continue
    def find(o):
        if isinstance(o, dict):
            if str(o.get('row')) == str(ROW) and o.get('container', '').endswith('0057.gpk'):
                return o
            for v in o.values():
                r = find(v)
                if r: return r
        elif isinstance(o, list):
            for v in o:
                r = find(v)
                if r: return r
        return None
    r = find(j)
    if r: info = r; break
print('报告附录该行字段:', json.dumps(info, ensure_ascii=False) if info else '未找到（用手工参数）')
off = int(info.get('off')) if info and info.get('off') is not None else 652984
comp = int(info.get('comp')) if info and info.get('comp') is not None else 4654
dec = int(info.get('dec')) if info and info.get('dec') is not None else 66424
bb = int(info.get('block_base')) if info and info.get('block_base') is not None else BLOCK_BASE
f = open(GPK, 'rb'); f.seek(bb + off + 20); raw = f.read(comp); f.close()
print('读取 %d B @%d  头=%s' % (len(raw), bb + off + 20, raw[:4].hex()))
import zstandard
try:
    data = zstandard.ZstdDecompressor().decompress(raw, max_output_size=dec * 4)
except Exception as e:
    print('zstd 直解失败(%s)，改用流式' % type(e).__name__)
    data = zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)).read()
print('解出 %d B (期望 %d) sha16=%s' % (len(data), dec, hashlib.sha256(data).hexdigest()[:16].upper()))
txt = data.decode('gbk', 'replace')
print('头部:', re.sub(r'\s+', ' ', txt[:200]))
# 顶层节点
tags = re.findall(r'<(Dummy|Model|ParticleSystem|ParticleRes|Sprite)\b[^>]*>', txt)
tags_all = re.findall(r'<([A-Za-z_]\w*)', txt)
from collections import Counter
print('顶层标签计数:', json.dumps(dict(Counter(tags)), ensure_ascii=False))
nodes = []
for m in re.finditer(r'<(Dummy|Model|ParticleSystem|ParticleRes|Sprite)\b([^>]*)>', txt):
    tag, at = m.group(1), m.group(2)
    a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
    nm = a.get('Name')
    i = m.end()
    nxt = re.search(r'<(?:Dummy|Model|ParticleSystem|ParticleRes|Sprite)\b', txt[i:])
    blk = txt[i:(i + nxt.start()) if nxt else (i + 60000)]
    uni = re.search(r'<Uniforms>.*?</Uniforms>', blk, re.S)
    tr = sorted(set(x.group(1) for x in re.finditer(r'<(u_[A-Za-z0-9_]+)\b', uni.group(0)))) if uni else []
    frames = len(re.findall(r'<Frame\s', uni.group(0))) if uni else 0
    mac = re.findall(r'<Semantic\s+Name\s*=\s*"([^"]+)"\s+Type\s*=\s*"([^"]+)"\s+Value\s*=\s*"([^"]*)"', blk)
    mx = [x[0] for x in mac if x[1] == 'Bool']
    nodes.append({'tag': tag, 'name': nm, 'attrs': {k: v for k, v in a.items() if k in
        ('ModelName', 'FxStartTime', 'FxLifeSpan', 'TransparentMode', 'RenderBias', 'RenderOrder', 'DirType', 'TrackType', 'Texture', 'PosOffset')},
        'tracks': [x.replace('_Keyframe', '') for x in tr], 'frames': frames, 'macros': mx})
print('节点数:', len(nodes))
cnt = Counter(n['tag'] for n in nodes)
print('分类:', json.dumps(dict(cnt), ensure_ascii=False))
drv = Counter()
for n in nodes:
    for t in n['tracks']:
        drv[t] += 1
print('驱动声明计数:', json.dumps(dict(sorted(drv.items(), key=lambda x: -x[1])), ensure_ascii=False))
print('Model 节点 ModelName 样例:', [n['attrs'].get('ModelName') for n in nodes if n['tag'] == 'Model'][:4])
print('Dummy 名字:', [n['name'] for n in nodes if n['tag'] == 'Dummy'])
print('宏:', json.dumps({n['name']: n['macros'] for n in nodes if n['macros']}, ensure_ascii=False)[:300])
json.dump({'source': {'container': 'gres\\0057.gpk', 'row': ROW, 'off': off, 'comp': comp, 'dec': dec,
                      'block_base': bb, 'offset_rule': 'block_base + row_off + 20', 'flag': 12, 'algo': 'zstd'},
           'sha16': hashlib.sha256(data).hexdigest()[:16].upper(), 'bytes': len(data),
           'tag_counts': dict(cnt), 'driver_counts': dict(sorted(drv.items(), key=lambda x: -x[1])),
           'nodes': nodes}, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('清单 ->', OUT, os.path.getsize(OUT), 'B')
