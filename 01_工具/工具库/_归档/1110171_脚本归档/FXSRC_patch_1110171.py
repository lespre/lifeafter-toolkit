# -*- coding: utf-8 -*-
"""FXSRC_patch_1110171.py — 1110171/effects.json 标注修订（只改标注，不改任何数值）。
① attach 改为已锁死的源级证据（fx_idle_01 4×4 平移 (0,0,1.4462)）+ per_node_offset + unresolved
② 顶层加 texture_binding_status = candidate_content_feature_not_source
③ 四个无源项逐个标 source: absent/derived（顶层 field_provenance + 节点级 source_flags）
备份写到 _target_1110171\\FXSRC_1110171_effects_backup.json（不覆盖项目文件以外的任何东西）。
"""
import json, os, shutil

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
EFF = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171', 'effects.json')
AUD = os.path.join(OUT, 'FXSRC_1003_audit.json')

eff = json.load(open(EFF, encoding='utf-8'))
shutil.copyfile(EFF, os.path.join(OUT, 'FXSRC_1110171_effects_backup.json'))
aud = json.load(open(AUD, encoding='utf-8'))
xml_nodes = {n['name']: n for n in aud['A_xml']['nodes']}

# ① per_node_offset（源值 PosOffset）
per_node_offset = {}
for n in eff['nodes']:
    xn = xml_nodes.get(n['name'])
    a = (xn or {}).get('attrs', {})
    po = a.get('PosOffset')
    if po:
        per_node_offset[n['name']] = [float(x) for x in po.split(',')]
eff['attach'] = {
    'mode': 'binding_fx_idle_01',
    'anchor': [0.0, 0.0, 1.4462],
    'evidence': ('源级：weapon/001209.c159（含 skin_1003_010 与 fx_idle_01）中 fx_idle_01 名后 @1128 的 16 float '
                 '= 列主序仿射 [1,0,0,0 | 0,1,0,0 | 0,0,1,0 | 0,0,1.4462,1] ⇒ 平移量 (0,0,1.4462)。'
                 'FX XML 侧无骨骼挂点：20 节点全部 BindBonesHead=FALSE / SelBindBonesIdx="" / AnchorSum=0。'
                 '⇒ 挂点 = c159 fx_idle_01 4×4 + 各节点 PosOffset（源值）+ Dummy 父链（L_zong / L_空特效 / L_box_01，FixDummyTrack=TRUE）。'
                 '证据文件：FXSRC_c159_matrix.json、FXSRC_1003_audit.json'),
    'per_node_offset': per_node_offset,
    'unresolved': ('同 c159 内其它 socket（bag/hongwai/sound/muzzle_fire）的 4×4 对齐尚未锁死（其平移量已在文件中命中但矩阵对齐未证），'
                   '本皮肤不使用，不猜。'),
}
# ② 顶层状态
eff['texture_binding_status'] = 'candidate_content_feature_not_source'
eff['texture_binding_status_note'] = (
    '.sfx 的 Texture 是完整逻辑路径（11 条），但 effect.idx（10,026 条）只有 128-bit idx_hash、零路径串；'
    '实测 3,696 次哈希（md5/sha1/sha256/sha512 × utf-8/utf-16/latin1 × 斜杠/大小写/去扩展名/加\\0）对 875 个 idx_hash 0 命中；'
    '项目 toolkit_core/texture_extractor.py 自述匿名 gpk 无路径 fid（已 6 路证伪路径反推）⇒ 现映射为内容特征候选，非源级。'
    '这是“特效不像游戏内”的根因之一，使用者须知。')
# ③ 字段来源总表 + 节点级标记
eff['field_provenance'] = {
    'start': 'source: XML@FxStartTime', 'life': 'source: XML@FxLifeSpan',
    'radius': 'source_if_XML@Radius_present_else_derived',
    'blend_mode': 'source: XML@BlendMode', 'pos_offset': 'source: XML@PosOffset',
    'texture': 'source: XML@Texture(逻辑路径)', 'texture_candidate': 'candidate: content_feature_not_source',
    'texture_binding': 'candidate: content_feature_not_source',
    'fxIgnore': 'source: XML@FxIgnore', 'emitAtBegin': 'source: XML@EmitAtBegin',
    'preEmitTime': 'source: XML@PreEmitTime', 'sprWorkMode': 'source: XML@SprWorkMode',
    'sprSpeedRate': 'source: XML@SprSpeedRate', 'isSprBlend': 'source: XML@IsSprBlend',
    'particlesPerSecond': 'source: XML@ParticlesPerSecond',
    'minParticlesPerSecond': 'source: XML@MinParticlesPerSecond',
    'minSpriteLifespan': 'source: XML@MinSpriteLifespan', 'maxSpriteLifespan': 'source: XML@MaxSpriteLifespan',
    'randomStartSpr': 'derived: XML 无 RandomStartSpr（ParticleSystem 节点）',
    'color_track': 'source: XML ColorFrame', 'color_track_par': 'source: XML ColorFramePar',
    'scale_track': 'source: XML TrackScale', 'smooth_start': 'source: XML SmoothStartFrame',
    'smooth_stop': 'source: XML SmoothStopFrame',
    'emit': 'source: XML 子标签 Gravity/Max·MinSpriteVelocity/RotDegreeSpeed/EmissionRadius(2)/SpriteScale/SpriteHeight/HWRatio/EmissionDirDegree/NoiseStrength/X·Y·ZDirDisturb',
    'is_sprite_sheet': 'source: XML@SprWorkMode/IsSprBlend + Texture 扩展名 .spr 判定',
    'lifespan_anomaly': 'derived: 解析时对 Min/Max 异常的记录',
    'attach': 'source: c159 fx_idle_01 4×4（anchor）+ XML PosOffset（per_node_offset）',
    'environment': 'approximate: neutral_fixed（源 cube 未定位）',
    'particle_rule': 'derived/implementation note（播放规则说明，非源参数）',
    'sheet_correction': 'derived/correction note（对旧错误的更正，非源参数）',
}
absent_radius = [n['name'] for n in eff['nodes'] if 'Radius' not in (xml_nodes.get(n['name'], {}).get('attrs') or {})]
absent_rss = [n['name'] for n in eff['nodes'] if 'RandomStartSpr' not in (xml_nodes.get(n['name'], {}).get('attrs') or {})]
eff['source_absent'] = {
    'randomStartSpr': {'source': 'absent', 'nodes': absent_rss, 'note': 'XML 这些节点无 RandomStartSpr 属性'},
    'radius': {'source': 'derived', 'nodes': absent_radius, 'note': 'XML 这些节点无 Radius 属性，值为派生/占位'},
    'texture_candidate': {'source': 'candidate', 'note': '内容特征候选，非源级'},
    'texture_binding': {'source': 'candidate', 'note': '内容特征候选，非源级'},
    'attach_note': {'source': 'removed', 'note': '旧 note“挂点为模型包围盒近似”与实测矛盾，已删除'},
}
for n in eff['nodes']:
    xn = xml_nodes.get(n['name'], {})
    a = xn.get('attrs') or {}
    sf = {}
    if 'RandomStartSpr' not in a:
        sf['randomStartSpr'] = 'absent'
    if 'Radius' not in a:
        sf['radius'] = 'derived'
    sf['texture_candidate'] = 'candidate'
    n['source_flags'] = sf
json.dump(eff, open(EFF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已写回', EFF)
print('attach.per_node_offset 条数', len(per_node_offset))
print('非零 PosOffset:', {k: v for k, v in per_node_offset.items() if any(abs(x) > 1e-9 for x in v)})
print('texture_binding_status =', eff['texture_binding_status'])
print('source_absent: randomStartSpr 节点 %d 个 / radius(无源) 节点 %d 个' % (len(absent_rss), len(absent_radius)))
print('顶层键:', sorted(eff.keys()))
