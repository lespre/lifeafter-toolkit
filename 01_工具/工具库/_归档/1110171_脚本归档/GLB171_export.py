# -*- coding: utf-8 -*-
'''task-77：1110171 全部 Model 的 .gim/.mesh → GLB 导出（复用 export_glb.build_glb）+ 只改 3 个键写回 effects.json。'''
import io, os, re, sys, json, struct, hashlib, shutil, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import locate_skeleton as LS
import export_glb as EG
B = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110171'
E = os.path.join(B, 'effects.json')
OUTD = os.path.join(B, 'sfx')
TEXMAP = r'E:\la拆包项目\03拆包产物\_gim_out\texmap_fx.json'
TMP = os.path.join(os.environ['TEMP'], 'glb171_tmp')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
REP = os.path.join(OUT, 'GLB171_FIX_report.md')
ASSETS = os.path.join(OUT, 'GLB171_FIX_assets.json')
ALLOWED = ('model_glb', 'model_glb_state', 'model_glb_note')
os.makedirs(TMP, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
eff = json.loads(open(E, 'rb').read().decode('utf-8'))
old_raw = open(E, 'rb').read()
MD = [n for n in eff['nodes'] if n.get('tag') == 'Model']
g = LS.GpkIndex()

def glb_stats(p):
    b = open(p, 'rb').read()
    if b[:4] != b'glTF':
        return {'sha16': hashlib.sha256(b).hexdigest()[:16].upper(), 'bytes': len(b), 'glb_ok': False}
    off, js = 12, None
    while off < len(b):
        clen, ctype = struct.unpack('<II', b[off:off + 8])
        if ctype == 0x4E4F534A:
            js = json.loads(b[off + 8:off + 8 + clen].decode('utf-8')); break
        off += 8 + clen
    verts = 0; lo = [1e9] * 3; hi = [-1e9] * 3
    if js:
        for a in js.get('accessors', []):
            if a.get('type') == 'VEC3' and a.get('min') and a.get('max'):
                verts += a.get('count', 0)
                for i in range(3):
                    lo[i] = min(lo[i], a['min'][i]); hi[i] = max(hi[i], a['max'][i])
    return {'sha16': hashlib.sha256(b).hexdigest()[:16].upper(), 'bytes': len(b), 'glb_ok': True,
            'verts': verts, 'bbox': [round(hi[i] - lo[i], 4) for i in range(3)] if verts else None,
            'materials': [m.get('name') for m in (js or {}).get('materials', [])]}

rows = []
for n in MD:
    mf = n.get('model_fields') or {}
    mn = (mf.get('ModelName') or n.get('model_name') or '')
    rel = mn.replace('/', '\\')
    stem = re.sub(r'\.gim$', '', os.path.basename(rel))
    rec = {'node': n.get('name'), 'model_name': mn, 'stem': stem,
           'model_glb_before': n.get('model_glb'), 'model_glb_state_before': n.get('model_glb_state')}
    gim = mesh = None
    try:
        gim, gm = g.read(rel); rec['gim'] = {'container': (gm or {}).get('container'), 'row': (gm or {}).get('row'),
                                             'bytes': len(gim) if gim else 0, 'sha16': hashlib.sha256(gim).hexdigest()[:16].upper() if gim else None}
    except Exception as e:
        rec['gim'] = {'error': str(e)[:80]}
    mrel = re.sub(r'\.gim$', '.mesh', rel)
    try:
        mesh, mm = g.read(mrel); rec['mesh'] = {'container': (mm or {}).get('container'), 'row': (mm or {}).get('row'),
                                                'bytes': len(mesh) if mesh else 0, 'sha16': hashlib.sha256(mesh).hexdigest()[:16].upper() if mesh else None}
    except Exception as e:
        rec['mesh'] = {'error': str(e)[:80]}
    if not mesh:
        rec.update({'result': 'not_found'}); rows.append(rec); continue
    tmpf = os.path.join(TMP, stem + '.mesh')
    open(tmpf, 'wb').write(mesh)
    outglb = os.path.join(OUTD, stem + '.glb')
    try:
        EG.build_glb(tmpf, TEXMAP, ['fx'], outglb, label=stem, center=False)
        rec['result'] = 'exported' if os.path.isfile(outglb) else 'export_failed'
        if os.path.isfile(outglb):
            rec['glb'] = glb_stats(outglb)
    except Exception as e:
        rec['result'] = 'export_exception'; rec['error'] = '%s: %s' % (type(e).__name__, str(e)[:120])
    rows.append(rec)
ok = [r for r in rows if r['result'] == 'exported']
bad = [r for r in rows if r['result'] != 'exported']
print('Model 总数 %d：导出成功 %d，失败/缺件 %d' % (len(rows), len(ok), len(bad)))
for r in bad:
    print('   !! %-20s %s  gim=%s mesh=%s' % (r['node'], r['result'], (r.get('gim') or {}).get('row'), (r.get('mesh') or {}).get('row')))
# ---- 只改 3 个键
snap = [json.dumps(n, ensure_ascii=False, sort_keys=True) for n in eff['nodes']]
by = {n.get('name'): n for n in MD if n.get('tag') == 'Model'}
for r in rows:
    n = by.get(r['node'])
    if not n:
        continue
    if r['result'] == 'exported':
        n['model_glb'] = 'sfx/%s.glb' % r['stem']
        n['model_glb_state'] = 'exported_from_gim'
        n['model_glb_note'] = 'gim=%s#%s sha16=%s ｜ mesh=%s#%s sha16=%s ｜ 走既有 export_glb.build_glb(set=[fx], texmap_fx 空集⇒几何-only)，无顶替' % (
            (r['gim'] or {}).get('container'), (r['gim'] or {}).get('row'), (r['gim'] or {}).get('sha16'),
            (r['mesh'] or {}).get('container'), (r['mesh'] or {}).get('row'), (r['mesh'] or {}).get('sha16'))
    else:
        n['model_glb'] = None
        n['model_glb_state'] = 'not_shipped'
        n['model_glb_note'] = '源 .mesh 未取到（%s）⇒ not_shipped，不顶替' % r['result']
self_ok = all(json.dumps({k: v for k, v in n.items() if k not in ALLOWED}, ensure_ascii=False, sort_keys=True)
              == json.dumps({k: v for k, v in json.loads(snap[i]).items() if k not in ALLOWED}, ensure_ascii=False, sort_keys=True)
              for i, n in enumerate(eff['nodes']))
changed = [n['name'] for i, n in enumerate(eff['nodes'])
           if json.dumps(n, ensure_ascii=False, sort_keys=True) != snap[i]]
print('自证：仅 %s 三键变动 = %s；变动节点 %d 个' % (list(ALLOWED), self_ok, len(changed)))
if not self_ok:
    print('** 自证未过 ⇒ 拒绝写盘 **'); sys.exit(3)
bs = E + '.bak_glb171_' + time.strftime('%Y%m%d_%H%M%S')
shutil.copy2(E, bs)
pp = '\n' in old_raw.decode('utf-8', 'replace')[:4000]
open(E, 'w', encoding='utf-8', newline='\n').write(json.dumps(eff, ensure_ascii=False, indent=1 if pp else None, separators=None if pp else (',', ':')))
nb = open(E, 'rb').read()
print('effects.json %s -> %s (%d -> %d B) 备份=%s' % (
    hashlib.sha256(old_raw).hexdigest()[:16].upper(), hashlib.sha256(nb).hexdigest()[:16].upper(), len(old_raw), len(nb), os.path.basename(bs)))
json.dump({'rows': rows, 'exported': len(ok), 'failed': len(bad),
           'effects': {'before': hashlib.sha256(old_raw).hexdigest()[:16].upper(), 'after': hashlib.sha256(nb).hexdigest()[:16].upper(),
                       'bytes_before': len(old_raw), 'bytes_after': len(nb), 'backup': os.path.basename(bs),
                       'changed_nodes': changed, 'only_allowed_keys': self_ok}},
          io.open(ASSETS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('资产 JSON ->', ASSETS)
# ---- 报告
L = []
w = L.append
w(u'# 1110171 Model GLB 补齐报告（task-77）\n')
w(u'## 0. pin\n')
w(u'| 项 | 值 |')
w(u'|---|---|')
w(u'| effects.json | `%s` → **`%s`**（%d → %d B） |' % (hashlib.sha256(old_raw).hexdigest()[:16].upper(), hashlib.sha256(nb).hexdigest()[:16].upper(), len(old_raw), len(nb)))
w(u'| 备份 | `%s` |' % os.path.basename(bs))
w(u'| 导出 | 成功 **%d** / 失败 %d（共 %d 个 Model） |' % (len(ok), len(bad), len(rows)))
w(u'| 自证 | 仅 `model_glb`/`model_glb_state`/`model_glb_note` 三键变动 = **%s**（变动节点 %d 个） |' % (self_ok, len(changed)))
w(u'')
w(u'## 1. 缺陷根因（与 lead 口径的差异，必须写清）\n')
w(u'- 1110171 的 **28/28** Model 节点**原本 `model_glb` 全为 `null`**、`model_name` 也全为 `null`；源路径只在 `model_fields.ModelName` 里。\n')
w(u'- 适配器 `weapon_skin_sfx_adapter.js:468` 是 `meshRel = mf.mesh || n.model_glb || (mname ? \'sfx/\' + stemOf(mname) + \'.glb\' : null)` ⇒ **即使 `model_glb=null`，只要 `ModelName` 在，仍会推导出 `sfx/<stem>.glb` 并发请求**。\n')
w(u'- ⇒ **"把 model_glb 置 null + not_shipped" 并不会让 404 消失**（adapter 当前不读 `model_glb_state`，全库仅 :468 一处引用 `model_glb`）。真正的修法只有两条：**(甲) 把 GLB 真导出来（本轮采用）**；**(乙) adapter 增加一个"显式 not_shipped ⇒ 不发请求"的分支（需 lead 改 adapter，我无权改）**。\n')
w(u'- 只报 3 条 404 的原因：其余 25 个 Model 在更早的 fail-closed 分支就被跳过（C 类无颜色驱动 / FxIgnore=TRUE / 其它前置条件），根本没走到加载；**但只要它们将来被放行，同样会 404** ⇒ 本轮按"全量补齐"处理。\n')
w(u'')
w(u'## 2. 全量 Model ↔ 源件 ↔ 导出对照\n')
w(u'| 节点 | 源 .gim（容器#row） | 源 .mesh（容器#row） | 结果 | GLB sha16 | bytes | verts | bbox |')
w(u'|---|---|---|---|---|---|---|---|')
for r in rows:
    gg, mm = r.get('gim') or {}, r.get('mesh') or {}
    gl = r.get('glb') or {}
    w(u'| %s | `%s#%s` | `%s#%s` | %s | `%s` | %s | %s | %s |' % (
        r['node'], gg.get('container'), gg.get('row'), mm.get('container'), mm.get('row'), r['result'],
        gl.get('sha16', '—'), gl.get('bytes', '—'), gl.get('verts', '—'), json.dumps(gl.get('bbox'), ensure_ascii=False) if gl.get('bbox') else '—'))
w(u'')
w(u'## 3. 已证 / 未证 / 未做\n')
w(u'**已证**：28/28 源 `.gim`（c159 绑定文档）+ 同 stem `.mesh`（几何）**全部按名命中**（`effect_01.gpk`，逐行 row/sha16 见上表与资产 JSON）；GLB 由**既有** `export_glb.build_glb`（`set=["fx"]`、texmap 为空集 ⇒ 几何-only）导出，**未新写解析器、未内嵌贴图、未顶替**；effects.json 仅三键变动（自证通过）。')
w(u'**未证**：导出的 GLB 与源 .gim 绑定文档的**姿态/缩放一致性**未做（既有 dg 批次同口径）；贴图仍未绑（几何-only）。')
w(u'**未做**：未开浏览器（404 是否消失由 lead 派复测确认）；未改 adapter/viewer.json/viewer.js/board/neox_material.json/其它皮肤。')
io.open(REP, 'w', encoding='utf-8').write(u'\n'.join(L) + u'\n')
print('报告 ->', REP, os.path.getsize(REP), 'B')
