# -*- coding: utf-8 -*-
"""FXMODEL_fix1110171.py — 1110171：MtlIdx 从 _gim_out/1110171/raw 取；mesh 若 GLB 未导出则如实标 absent（附原因）。
"""
import os, json, struct, shutil

PACK = r'E:\la拆包项目\03拆包产物'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
GIM = os.path.join(PACK, '_gim_out')
OUT = os.path.join(PACK, '_target_1110171')
man = json.load(open(os.path.join(GIM, 'GIM_manifest_1110171.json'), encoding='utf-8'))
models = man['models'] if isinstance(man.get('models'), list) else list(man['models'].values())
print('manifest: frame=%s gim_hits=%s mesh_hits=%s glb_ok=%s fails=%s models=%d' % (
    man.get('frame'), man.get('gim_hits'), man.get('mesh_hits'), man.get('glb_ok'), man.get('fails'), len(models)))
glb_any = [m.get('glb') for m in models if m.get('glb')]
print('manifest 中带 glb 的条目:', len(glb_any), glb_any[:3])
sub = os.path.join(GIM, '1110171')
print('_gim_out/1110171 内容:', os.listdir(sub)[:6], '| raw 文件数:',
      len(os.listdir(os.path.join(sub, 'raw'))) if os.path.isdir(os.path.join(sub, 'raw')) else 0)
print('_gim_out/1110171 的 glb 数:', len([f for f in os.listdir(sub) if f.endswith('.glb')]))

eff_path = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171', 'effects.json')
eff = json.load(open(eff_path, encoding='utf-8'))
mtl_ok = 0
for n in eff['nodes']:
    if n.get('tag') != 'Model':
        continue
    mf = n.setdefault('model_fields', {})
    stem = os.path.splitext(os.path.basename((mf.get('ModelName') or '').replace('\\', '/')))[0]
    gp = os.path.join(sub, 'raw', stem + '.gim')
    if os.path.isfile(gp):
        b = open(gp, 'rb').read()
        i = b.find(b'MtlIdx')
        if i >= 0:
            seg = b[i + 6:i + 6 + 32]
            vals = []
            for off in range(0, min(20, len(seg) - 3)):
                v = struct.unpack_from('<I', seg, off)[0]
                if 0 <= v <= 512:
                    vals.append(v)
            mf['MtlIdx'] = vals
            mf['MtlIdx_evidence'] = {'source': '_gim_out/1110171/raw/%s.gim' % stem, 'offset': i,
                                     'method': 'bytes_after_MtlIdx_best_effort', 'hex': seg.hex()}
            n['source_flags']['MtlIdx'] = 'source(best-effort): .gim MtlIdx 邻域整数，未做结构级确认'
            mtl_ok += 1
        else:
            mf['MtlIdx'] = None
            n['source_flags']['MtlIdx'] = 'unresolved: .gim 内未定位到 MtlIdx'
    else:
        mf['MtlIdx'] = None
        n['source_flags']['MtlIdx'] = 'absent: 无 1110171 的 .gim 载荷'
    # mesh：GLB 未导出 ⇒ absent + 原因
    mf['mesh'] = None
    n['source_flags']['mesh'] = 'absent: GIM_manifest_1110171 的 glb=None（freeze-auditor 尚未导出 1110171 的 GLB）'
eff['model_field_patch'] = dict(eff.get('model_field_patch') or {})
eff['model_field_patch']['mesh_backfill'] = {
    'filled': 0, 'absent': sum(1 for n in eff['nodes'] if n.get('tag') == 'Model'),
    'reason': 'GIM_manifest_1110171.json 中 28 个模型的 glb 字段均为 None（未导出）；stem 匹配 28/28 已就绪，导出后即可回填',
    'mtlidx_extracted': mtl_ok}
json.dump(eff, open(eff_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
inj = os.path.join(OUT, 'FXMODEL_1110171_inj_viewer_effects.json')
json.dump(eff, open(inj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('1110171：MtlIdx 取自 .gim %d 个；mesh 全 absent（GLB 未导出）→ %s' % (mtl_ok, inj))
