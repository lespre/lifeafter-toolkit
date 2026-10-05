# -*- coding: utf-8 -*-
"""FXSRC_patch2_1110171.py — 按裁决停用 1110171 的错源特效（effects.json 侧）。
status: "wrong_source_unresolved" 会**不会**停用按钮（viewer 判据是 status!=="none"），
故写 status="none" + status_detail="wrong_source_unresolved" + 证据字段。
"""
import json, os, shutil

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
EFF = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171', 'effects.json')
shutil.copyfile(EFF, os.path.join(OUT, 'FXSRC_1110171_effects_backup2.json'))
d = json.load(open(EFF, encoding='utf-8'))
d['status'] = 'none'
d['status_detail'] = 'wrong_source_unresolved'
d['status_reason'] = ('现 sfx_source 绑定错误：该帧（effect_01.gpk frame 14761, size 83327）内 skin_1003_010 出现 0 次；'
                      '其 3 个 ModelName 与唯一 SfxName 全部属 skin_1006_010（fx_skin_1006_010_mvp_03_02.sfx）'
                      '⇒ 本 effects.json 的节点/颜色/贴图来自别的皮肤，已停用。'
                      '正确源线索：_sfx_010 内确有 27 帧内容含 skin_1003_010，但含 idle 字样者 0 个；'
                      'c159 socket 为 fx_idle_01 ⇒ 无法对齐；fx_skin_1003_010_zs_02.sfx 及 11 个命名变体在 '
                      'fpk_fid_index.json(2,069,650 fid) 中 0 命中（该皮肤 fx 仅存在于匿名 GPK）⇒ 帧↔文件名不可证。')
d['source_binding_status'] = 'wrong_source_unresolved_no_frame_name_index'
json.dump(d, open(EFF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', EFF)
print('status =', d['status'], '| status_detail =', d['status_detail'], '| nodes =', len(d['nodes']))
print('注意：运行时无任何代码读 effects.json；真正停用需 viewer.json.effects.status="none"（Lead 作用域）')
