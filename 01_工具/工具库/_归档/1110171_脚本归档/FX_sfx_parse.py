# -*- coding: utf-8 -*-
"""FX_sfx_parse.py — 用项目自带解析器实测源 .sfx（XML FxGroup）结构 / 节点数 / 关键字段（只读）。

源文件（不在 08 wiki，而在拆包产物里，扩展名是 .bin）：
  03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f14761_bc3a874b70893946.bin
  sha16 bc3a874b70893946 == effects.json.sfx_source.sha16（对账用）
解析器：01拆包器本体\工具库\06_皮肤定位链\parse_sfx_tracks.py（GBK XML → 节点树 + 轨道）
输出：FX_sfx_tracks.json（本目录）/ 控制台摘要
"""
import json, os, sys, hashlib, collections, importlib.util, urllib.request, urllib.error

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
PACK = r'E:\la拆包项目\03拆包产物'
TOOL = r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\parse_sfx_tracks.py'
SRC = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'gpk_effect_01_f14761_bc3a874b70893946.bin')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
EFF = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171', 'effects.json')
BASE = 'http://127.0.0.1:8765/'

spec = importlib.util.spec_from_file_location('parse_sfx_tracks', TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

rep = {}
raw = open(SRC, 'rb').read()
rep['source'] = {'path': SRC, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                 'sha256_16': hashlib.sha256(raw).hexdigest()[:16]}
eff = json.load(open(EFF, encoding='utf-8'))
rep['effects_json'] = {'path': EFF, 'sfx_source': eff.get('sfx_source'), 'status': eff.get('status'),
                       'nodes': len(eff.get('nodes') or []), 'loop_seconds': eff.get('loop_seconds'),
                       'textures_dir': eff.get('textures_dir'), 'assets_base': eff.get('assets_base')}
rep['sha_match'] = (rep['source']['sha256_16'] == str((eff.get('sfx_source') or {}).get('sha16')))
rep['bytes_match'] = (rep['source']['bytes'] == (eff.get('sfx_source') or {}).get('bytes'))

dst = os.path.join(OUT, 'FX_sfx_tracks.json')
mod.main(SRC, dst)
parsed = json.load(open(dst, encoding='utf-8'))
rep['parsed'] = {'node_count': parsed.get('node_count'), 'root_attrib': parsed.get('root_attrib'),
                 'anomalies': len(parsed.get('anomalies') or []),
                 'tag_counts': dict(collections.Counter(n['tag'] for n in parsed['nodes']))}
print('== 源 .sfx', rep['source'])
print('== sha16 与 effects.json 一致: %s / bytes 一致: %s' % (rep['sha_match'], rep['bytes_match']))
print('== root 属性:', json.dumps(parsed.get('root_attrib'), ensure_ascii=False)[:300])
print('== 解析节点数 = %s；标签分布 = %s；anomalies = %d' % (
    parsed.get('node_count'), json.dumps(rep['parsed']['tag_counts'], ensure_ascii=False), rep['parsed']['anomalies']))
print('%-24s %-15s %-8s %-8s %-8s %-6s %-6s %-6s %-6s %s' % ('name', 'tag', 'start', 'life', 'radius', 'blend', '色帧', '缩放帧', 'emit键', 'texture'))
pnodes = []
for n in parsed['nodes']:
    ck = n['tracks'].get('ColorFrame') or n['tracks'].get('ColorFramePar') or []
    sk = n['tracks'].get('scale_XScale') or []
    pnodes.append({'name': n['name'], 'tag': n['tag'], 'parent': n.get('parent'), 'start': n['start'], 'life': n['life'],
                   'radius': n['radius'], 'blend_mode': n['blend_mode'], 'texture': n['texture'],
                   'color_frames': len(ck), 'scale_frames': len(sk), 'track_keys': sorted(n['tracks'].keys()),
                   'emit_keys': sorted(n['emit'].keys()), 'pos_offset': n['pos_offset']})
    print('%-24s %-15s %-8s %-8s %-8s %-6s %-6d %-6d %-6d %s' % (
        n['name'], n['tag'], n['start'], n['life'], n['radius'], n['blend_mode'], len(ck), len(sk),
        len(n['emit']), os.path.basename((n['texture'] or '').replace('\\', '/')) or '-'))
rep['parsed_nodes'] = pnodes

# ---- effects.json 节点对照 ----
en = eff.get('nodes') or []
rep['effects_nodes'] = []
print('\n== effects.json 的 %d 个节点（含贴图候选与存在性）' % len(en))
for n in en:
    tc = n.get('texture_candidate')
    rel = str(eff.get('assets_base') or '') + str(eff.get('textures_dir') or 'sfx/tex/') + str(tc or '').replace('.dds', '.png')
    local = os.path.normpath(os.path.join(os.path.dirname(EFF), rel))
    url = BASE + 'assets/3d/weapon_skin/1110171/' + rel
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=15) as r:
            st = r.status
    except urllib.error.HTTPError as e:
        st = e.code
    except Exception as e:
        st = 'ERR:' + type(e).__name__
    rec = {'name': n.get('name'), 'tag': n.get('tag'), 'start': n.get('start'), 'life': n.get('life'),
           'radius': n.get('radius'), 'blend_mode': n.get('blend_mode'), 'texture': n.get('texture'),
           'texture_candidate': tc, 'rel': rel, 'disk': os.path.isfile(local), 'http': st,
           'color_track_frames': len(n.get('color_track') or []), 'scale_track_frames': len(n.get('scale_track') or []),
           'smooth_start_frames': len(n.get('smooth_start') or []), 'smooth_stop_frames': len(n.get('smooth_stop') or []),
           'emit_keys': sorted((n.get('emit') or {}).keys()), 'keys': sorted(n.keys())}
    rep['effects_nodes'].append(rec)
    print('  %-22s %-15s start=%-6s life=%-6s radius=%-6s blend=%-3s 色帧=%-3d 缩放帧=%-3d 贴图=%s %s' % (
        rec['name'], rec['tag'], rec['start'], rec['life'], rec['radius'], rec['blend_mode'],
        rec['color_track_frames'], rec['scale_track_frames'], tc, ('OK' if rec['disk'] else 'MISSING') + '/' + str(rec['http'])))
# 名称对齐
pnames = [n['name'] for n in pnodes]
enames = [n['name'] for n in en]
rep['diff'] = {'parsed_not_in_effects': [x for x in pnames if x not in enames],
               'effects_not_in_parsed': [x for x in enames if x not in pnames],
               'parsed_total': len(pnames), 'effects_total': len(enames)}
print('\n== 节点对齐：解析 %d / effects.json %d；解析有而 effects 缺失=%s；effects 有而解析缺失=%s' % (
    len(pnames), len(enames), rep['diff']['parsed_not_in_effects'], rep['diff']['effects_not_in_parsed']))
print('== 贴图存在性：磁盘 %d/%d，HTTP200 %d/%d' % (
    sum(1 for r in rep['effects_nodes'] if r['disk']), len(rep['effects_nodes']),
    sum(1 for r in rep['effects_nodes'] if r['http'] == 200), len(rep['effects_nodes'])))
json.dump(rep, open(os.path.join(OUT, 'FX_effects_nodes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FX_effects_nodes.json'))
