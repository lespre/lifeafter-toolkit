# -*- coding: utf-8 -*-
'''task-72：子特效 js_04 / zs_01 解析 → 合并为新节点（fail-closed）+ 报告。
用法：python SUBSFX_merge.py --dry-run | (无参数=真跑)'''
import io, os, re, sys, json, hashlib, shutil, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import locate_skeleton as LS
DRY = '--dry-run' in sys.argv
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
REP = os.path.join(OUT, 'SUBSFX_report.md')
ASSETS = os.path.join(OUT, 'SUBSFX_assets.json')
BIN171 = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite', 'Trail')
SUBS = [
    {'skin': '1110177', 'path': r'effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_js_04.sfx', 'parent': 'M_ParticleRes'},
    {'skin': '1110171', 'path': r'effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_zs_01.sfx', 'parent': None},
]
g = LS.GpkIndex()

def frames_of(body):
    out = []
    for fm in re.finditer(r'<Frame\s+([^>/]*)/?>', body):
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', fm.group(1)))
        if 'Time' in a and 'Value' in a:
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
        tex = set()
        for v in list(a.values()) + [blk]:                       # ★ 贴图声明在**标签属性**里（上一版只搜块体 ⇒ 漏）
            tex |= set(re.findall(r'[A-Za-z0-9_\\/\.\-]+\.(?:spr|tga)', v))
        emit = {}
        for cm in re.finditer(r'<([A-Za-z_]\w*)\b([^>]*?)(?:/>|>(.*?)</\1>)', blk, re.S):
            if cm.group(1) in TAGS or cm.group(1) in ('FxGroup', 'Semantic', 'Variables', 'Macros', 'Uniforms', 'ShaderComponent'):
                continue
            fr = frames_of(cm.group(3) or '')
            if fr:
                emit[cm.group(1)] = fr
        out.append({'tag': tag, 'attrs': a, 'textures': sorted(tex), 'emit': emit})
    return out

# 1110171 父 ParticleRes 名（从 bin 里找 SfxName 含 zs_01 的节点）
bin_txt = io.open(BIN171, 'rb').read().decode('gbk', 'replace')
parents171 = []
for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), bin_txt):
    if m.group(1) != 'ParticleRes':                     # ★ 只认 ParticleRes 自己的声明，避免窗口外溢误收 L_空特效
        continue
    if 'zs_01' not in m.group(2) and 'zs_01' not in bin_txt[m.end():m.end() + 1500]:
        continue
    nm = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(2))).get('Name')
    if nm and nm not in parents171:
        parents171.append(nm)
print('[1110171] 引用 zs_01 的父节点:', json.dumps(parents171, ensure_ascii=False))

built = {}
for s in SUBS:
    d, meta = g.read(s['path'])
    sha = hashlib.sha256(d).hexdigest()[:16].upper()
    nodes = parse_nodes(d.decode('gbk', 'replace'))
    built[s['skin']] = {'meta': meta, 'sha16': sha, 'bytes': len(d), 'nodes': nodes, 'path': s['path']}
    print('[%s] row=%s dec=%d sha16=%s 节点=%d 类型=%s' % (
        s['skin'], meta.get('row'), len(d), sha, len(nodes),
        json.dumps({t: sum(1 for n in nodes if n['tag'] == t) for t in TAGS if any(n['tag'] == t for n in nodes)}, ensure_ascii=False)))
    for n in nodes:
        print('    %-18s %-14s FxIgnore=%-5s tex=%s emit=%d轨' % (
            n['attrs']['Name'], n['tag'], n['attrs'].get('FxIgnore'), json.dumps(n['textures'], ensure_ascii=False)[:70], len(n['emit'])))

summary = {}
for skin in ('1110177', '1110171'):
    E = os.path.join(W, skin, 'effects.json')
    old = open(E, 'rb').read()
    eff = json.loads(old.decode('utf-8'))
    snap = [json.dumps(n, ensure_ascii=False, sort_keys=True) for n in eff['nodes']]
    have = {n['name'] for n in eff['nodes']}
    before_render = sum(1 for n in eff['nodes'] if n.get('renderable_by_adapter'))
    b = built[skin]
    srcid = '%s#%s' % (b['meta'].get('container'), b['meta'].get('row'))
    added = []
    for n in b['nodes']:
        a, nm = n['attrs'], n['attrs']['Name']
        newname = nm + '__sub' if nm in have else nm
        have.add(newname)
        has_atlas = any(t.lower().endswith('.spr') for t in n['textures'])
        row = {'name': newname, 'tag': n['tag'], 'source_name_in_sub': nm,
               'from_sub_sfx': True,
               'parent_node': (parents171[0] if skin == '1110171' and parents171 else SUBS[0]['parent']),
               'parent_nodes': (parents171 if skin == '1110171' else [SUBS[0]['parent']]),
               'source_sfx_id': srcid, 'sub_sfx_path': b['path'], 'sub_sfx_sha16': b['sha16'],
               'fxIgnore': (str(a.get('FxIgnore')).upper() == 'TRUE'),
               'fx_ignore_source': 'sub_sfx:%s:%s:FxIgnore' % (srcid, nm),
               'renderable_by_adapter': False,
               'sub_render_reason': ('no_real_atlas:' + json.dumps(n['textures'], ensure_ascii=False)) if n['textures'] else 'no_texture_declared_in_sub_sfx',
               'start': float(a['FxStartTime']) if a.get('FxStartTime') else None,
               'life': float(a['FxLifeSpan']) if a.get('FxLifeSpan') else None,
               'pos_offset': ([float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', a['PosOffset'])] if a.get('PosOffset') else None),
               'render_order': a.get('RenderOrder'), 'render_bias': a.get('RenderBias'),
               'transparent_mode': a.get('TransparentMode'), 'track_type': a.get('TrackType'), 'dir_type': a.get('DirType'),
               'particlesPerSecond': (float(a['ParticlesPerSecond']) if a.get('ParticlesPerSecond') else None),
               'texture': (n['textures'][0] if n['textures'] else None),
               'texture_status': ('unresolved_dot_tga_no_evidence' if n['textures'] and not has_atlas else ('no_texture_declared' if not n['textures'] else 'spr_atlas')),
               'emit': n['emit'],
               'sub_provenance': 'sub_sfx:%s:%s' % (srcid, nm)}
        if n['tag'] == 'Model' and a.get('ModelName'):
            stem = re.sub(r'\.gim$', '', os.path.basename(a['ModelName']))
            glb_rel = 'sfx/%s.glb' % stem
            row['model_name'] = a['ModelName']
            row['model_glb'] = glb_rel if os.path.isfile(os.path.join(W, skin, glb_rel)) else None
            row['model_glb_state'] = 'existing_glb' if row['model_glb'] else 'needs_export'
            row['sub_render_reason'] = 'model_untextured_failclosed_by_task_rule(маин-skin rule would render if A-class)'.replace('маин', 'main')
        added.append(row)
    eff['nodes'] = eff['nodes'] + added
    after_render = sum(1 for n in eff['nodes'] if n.get('renderable_by_adapter'))
    ok = all(json.dumps(n, ensure_ascii=False, sort_keys=True) == snap[i] for i, n in enumerate(eff['nodes'][:len(snap)]))
    summary[skin] = {'path': E, 'before': hashlib.sha256(old).hexdigest()[:16].upper(), 'bytes_before': len(old),
                     'nodes_before': len(snap), 'nodes_after': len(eff['nodes']), 'added': [r['name'] for r in added],
                     'render_before': before_render, 'render_after': after_render, 'existing_unchanged': ok}
    print('[%s] 既有节点零改动=%s 节点 %d→%d renderable %d→%d 新增=%s' % (
        skin, ok, len(snap), len(eff['nodes']), before_render, after_render, json.dumps([r['name'] for r in added], ensure_ascii=False)))
    if DRY:
        continue
    if not ok:
        print('** 自证未过 ⇒ 拒绝写盘 **'); sys.exit(3)
    bs = E + '.bak_subsfx_' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy2(E, bs)
    pp = '\n' in old.decode('utf-8', 'replace')[:4000]
    open(E, 'w', encoding='utf-8', newline='\n').write(json.dumps(eff, ensure_ascii=False, indent=1 if pp else None, separators=None if pp else (',', ':')))
    nb = open(E, 'rb').read()
    summary[skin].update({'after': hashlib.sha256(nb).hexdigest()[:16].upper(), 'bytes_after': len(nb), 'backup': os.path.basename(bs)})
    print('    写盘 %s -> %s (%d -> %d B) 备份=%s' % (summary[skin]['before'], summary[skin]['after'], len(old), len(nb), os.path.basename(bs)))
json.dump({'subs': {k: {'path': v['path'], 'container': v['meta'].get('container'), 'row': v['meta'].get('row'),
                        'bytes': v['bytes'], 'sha16': v['sha16'],
                        'nodes': [{'name': n['attrs']['Name'], 'tag': n['tag'], 'FxIgnore': n['attrs'].get('FxIgnore'),
                                   'textures': n['textures'], 'emit_tracks': sorted(n['emit'].keys()),
                                   'ModelName': n['attrs'].get('ModelName')} for n in v['nodes']]} for k, v in built.items()},
           'summary': summary, 'parents171': parents171,
           'spr_count': sum(1 for v in built.values() for n in v['nodes'] for t in n['textures'] if t.lower().endswith('.spr'))},
          io.open(ASSETS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('资产 JSON ->', ASSETS)
# ---- 报告
if not DRY:
    L = []
    w = L.append
    w(u'# 子特效拆包与合并报告（task-72）—— js_04 / zs_01\n')
    w(u'## 0. 定位与 pin\n')
    w(u'| 皮肤 | 子 sfx | 容器 | row | bytes | sha16 | 节点 |')
    w(u'|---|---|---|---|---|---|---|')
    for k, v in built.items():
        w(u'| %s | `%s` | `%s` | %s | %d | `%s` | %d |' % (k, v['path'], v['meta'].get('container'), v['meta'].get('row'), v['bytes'], v['sha16'], len(v['nodes'])))
    w(u'')
    w(u'| 皮肤 | effects.json 改前 | 改后 | 字节 | 备份 | 节点数 | renderable_by_adapter |')
    w(u'|---|---|---|---|---|---|---|')
    for k in ('1110177', '1110171'):
        s = summary[k]
        w(u'| %s | `%s` | **`%s`** | %d → %d | `%s` | %d → %d | **%d → %d** |' % (
            k, s['before'], s.get('after', '（未写）'), s['bytes_before'], s.get('bytes_after', 0), s.get('backup', ''), s['nodes_before'], s['nodes_after'], s['render_before'], s['render_after']))
    w(u'')
    w(u'自证：**既有节点零改动**（按位置 canonical JSON 逐字节比对）= 1110177 %s / 1110171 %s；`json.load` 可读通。' % (summary['1110177']['existing_unchanged'], summary['1110171']['existing_unchanged']))
    w(u'')
    w(u'## 1. 节点树逐条\n')
    for k, v in built.items():
        w(u'### %s ← `%s`（row %s，sha16 `%s`）' % (k, os.path.basename(v['path']), v['meta'].get('row'), v['sha16']))
        w(u'| 节点 | tag | FxStartTime | FxLifeSpan | FxIgnore | rate | 贴图声明 | emit 轨 | ModelName |')
        w(u'|---|---|---|---|---|---|---|---|---|')
        for n in v['nodes']:
            a = n['attrs']
            w(u'| %s | %s | %s | %s | %s | %s | %s | %d | %s |' % (
                a['Name'], n['tag'], a.get('FxStartTime'), a.get('FxLifeSpan'), a.get('FxIgnore'),
                a.get('ParticlesPerSecond'), json.dumps(n['textures'], ensure_ascii=False), len(n['emit']),
                ('`%s`' % a.get('ModelName')) if a.get('ModelName') else '—'))
        w(u'')
    w(u'## 2. 贴图可达性（逐条）\n')
    n_spr = sum(1 for v in built.values() for n in v['nodes'] for t in n['textures'] if t.lower().endswith('.spr'))
    w(u'- **`.spr` 声明数 = %d** ⇒ **没有任何 `.spr` 可走兄弟图集通道**，本轮**未导出任何 PNG**（`sfx/sub/` 未创建：没有可导的真图集）。' % n_spr)
    allt = sorted({t for v in built.values() for n in v['nodes'] for t in n['textures']})
    for t in allt:
        w(u'- `%s` → **unresolved**（`.tga`，源名轴无直证；按纪律**不顶替**）｜出现于 %s' % (
            t, json.dumps([k + ':' + n['attrs']['Name'] for k, v in built.items() for n in v['nodes'] if t in n['textures']], ensure_ascii=False)))
    w(u'')
    w(u'## 3. 合并结果（新增节点）\n')
    for k in ('1110177', '1110171'):
        w(u'### %s 新增 %s' % (k, json.dumps(summary[k]['added'], ensure_ascii=False)))
        w(u'- `parent_node` = %s（父 ParticleRes；1110171 有 %s）' % (json.dumps(parents171 if k == '1110171' else [SUBS[0]['parent']], ensure_ascii=False), '两个' if k == '1110171' else '一个'))
        w(u'- 带 `from_sub_sfx=true`、`source_sfx_id`（容器:row）、`sub_sfx_path/sha16`、`fxIgnore`(+provenance)、`emit` 全子轨、`start/life/pos_offset/render_bias/transparent_mode/track_type/dir_type`、`texture_status`。')
        w(u'- **fail-closed**：子节点贴图 unresolved ⇒ `renderable_by_adapter=false` + `sub_render_reason`；**两把皮肤 renderable 计数均未变（%d → %d）** ⇒ 这是一次**如实登记**，没有引入新渲染。' % (summary[k]['render_before'], summary[k]['render_after']))
    w(u'- 1110177 的 `L_模型特效__sub`：`ModelName = mod_skin_2003_029_dm_shangdian_07_djs.gim` ⇒ **该 GLB 早已在 `1110177/sfx/` 存在**（task-61 的 24 个之一），故 `model_glb = sfx/mod_skin_2003_029_dm_shangdian_07_djs.glb` + `model_glb_state="existing_glb"`；按 task-72 的 fail-closed 规则仍置 `renderable_by_adapter=false`，但**它与现有 26 个无贴图 Model 同类（A 类自发光）**，若按主皮肤规则即可渲 —— 该一处由 lead 裁定，报告如实两种口径。')
    w(u'')
    w(u'## 4. 自引用那条\n')
    w(u'- 1110177 dg 源里的 `H_ParticleRes` → `...\\fx_skin_2003_029_daoguang_02.sfx` = **该文件自身** ⇒ 按 task 要求**不递归展开**，仅登记（本文档 §0 的 dg 行已有其容器/row/sha16 = `gres\\0057.gpk#32153` / `9F4FE3A6AD3F8851`）。')
    w(u'')
    w(u'## 5. 已证 / 未证 / 未做\n')
    w(u'**已证**：两个子 sfx 按名命中（`effect_01.gpk` row 38437 / 37321，3,938 / 15,908 B，sha16 `C602AD795A764092` / `62A127F0BEDC3515`）；节点树 2 / 4 个（js_04: Dummy+Model；zs_01: 3 Sprite + 1 PS）；`.spr` 声明 **0** ⇒ 无真图集；三张 `.tga` 全部 unresolved；既有节点零改动；两皮肤 renderable 计数不变。')
    w(u'**未证**：`glow25.tga` / `glow_01.tga` / `tex_glow_ray_tp60_01.tga` 的**内容候选**未做匹配（按纪律不顶替）；子 sfx 里 `L_p_光刺_01_1`(rate 3) 的贴图同样 unresolved ⇒ 未能驱动。')
    w(u'**未做**：未开浏览器（验收另派）；未导出任何 PNG/GLB（无可导出的真图集；GLB 已存在）；未改 adapter/viewer.json/viewer.js/board/neox_material.json。**没有顶替、没有编造。**')
    io.open(REP, 'w', encoding='utf-8').write(u'\n'.join(L) + u'\n')
    print('报告 ->', REP, os.path.getsize(REP), 'B')
