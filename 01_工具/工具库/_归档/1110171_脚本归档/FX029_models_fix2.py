# -*- coding: utf-8 -*-
'''task-61 步骤2-c：确认拼写变体节点、修期望表口径、追加报告 §17'''
import io, os, re, json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
E = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177\effects.json'
J = json.loads(open(E, 'rb').read().decode('utf-8'))
MD = [n for n in J['nodes'] if n.get('tag') == 'Model']
var = []
for n in MD:
    ut = (n.get('model_fields') or {}).get('uniform_tracks') or {}
    if 'u_emissive_color_Keyframe' in ut:
        var.append({'node': n['name'], 'sfx': n.get('source_sfx'),
                    'has_emissivecolor': 'u_emissivecolor_Keyframe' in ut,
                    'has_diffuse_color': 'u_diffuse_color_Keyframe' in ut,
                    'frames_emissive_color': len(ut['u_emissive_color_Keyframe']),
                    'first': ut['u_emissive_color_Keyframe'][0]['value'],
                    'keys': sorted(k for k in ut if 'emissive' in k or 'diffuse' in k)})
print('拼写变体节点:', json.dumps(var, ensure_ascii=False))
# 重算两类口径
A2 = sum(1 for n in MD if ('u_emissivecolor_Keyframe' in ((n['model_fields'].get('uniform_tracks')) or {})
                           or 'u_emissive_color_Keyframe' in ((n['model_fields'].get('uniform_tracks')) or {})))
B2 = sum(1 for n in MD if 'u_emissivecolor_Keyframe' not in ((n['model_fields'].get('uniform_tracks')) or {})
         and 'u_emissive_color_Keyframe' not in ((n['model_fields'].get('uniform_tracks')) or {})
         and 'u_diffuse_color_Keyframe' in ((n['model_fields'].get('uniform_tracks')) or {}))
print('口径对比: 含拼写变体视为自发光 ⇒ A=%d B=%d C=%d ｜ 只认 u_emissivecolor ⇒ A=15 B=8 C=3' % (A2, B2, len(MD) - A2 - B2))
# 期望表 unwired 口径修正（highlight 已接线）
P = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_expected.json'
D = json.loads(open(P, 'rb').read().decode('utf-8'))
for r in D['rows']:
    r['unwired'] = [u for u in r.get('unwired', []) if 'highlight_intensity' not in u]
D['summary']['unwired_rows'] = sum(1 for r in D['rows'] if r['unwired'])
D['summary']['unwired_items'] = sorted({u for r in D['rows'] for u in r['unwired']})
D['summary']['class_counts_spelling_variant_as_emissive'] = {'A': A2, 'B': B2, 'C': len(MD) - A2 - B2}
D['summary']['note_class_rule'] = 'u_emissive_color（拼写变体）按节点自身声明视为自发光 ⇒ A=16/B=7/C=3；只认 u_emissivecolor 则为 A=15/B=8/C=3（lead 原清单口径）。'
json.dump(D, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('期望表已更新:', json.dumps(D['summary'], ensure_ascii=False))
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16].upper()
for p, nm in [(r'E:\la拆包项目\08Lifeafter wiki\assets\weapon_skin_sfx_adapter.js', 'adapter'),
              (E, '177/effects.json'), (P, 'FX029_models_expected.json'),
              (r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177\viewer.json', '177/viewer.json')]:
    print('  %-26s %s  %d B' % (nm, sha(p), os.path.getsize(p)))
sec = u'''

---

## §17 task-61 步骤② 补正（源公式子集落地 + 两处口径修正）

1. **按 lead 新口径落地源公式子集**（证据：renderer-auditor asm `L409-415`/`L425`，槽位 `u_emissivecolor`=cb0[3].xyz、`u_emissive_highlight_intensity`=cb0[24].x）：
   A 类自发光项 = `u_emissivecolor`（必带）× `u_emissive_highlight_intensity`（**仅当该节点有声明**；无声明 ⇒ 不乘并记 `omitted_undeclared`）。
   **未声明/不可得的因子**（`u_emissive_grey_intensity`、`u_emissive_mix`、`u_emissive_desaturate`、`u_mask_intensity`、
   以及自发光贴图采样项 `e`）**整个子项省略**，探针 `omitted_undeclared[]` 逐项登记，**不以"中性默认值"顶替**。
   ⇒ 本实现是源公式的**子集**：`approx:true`，`approx_reason='tex_unbound_e_sampler_unavailable + omitted_undeclared'`。
   `emissiveIntensity` 承载 highlight 因子（MeshStandardMaterial 的 emissive 通道 = shader 内 `final = diffuse + r1` 的自发光项加法结构）。
2. **新增开关 `WikiSfxAdapter.modelsHighlight(true|false)`**：默认 `true`（按 lead 指令接线）；`false` = 去掉该因子的基线，用于 A/B 对照。
3. **`u_depth_bias` 不进 shader**：按 lead 口径 5 与本轮证据（4 份 asm 内 `[unused]`）**一律不启用 polygonOffset**，探针记
   `depth_bias_state='present_unwired(engine_state_unresolved)'`（10/26 节点存在该轨道）。上一版 §16 第 9 条「仅源有则启用 polygonOffset」**作废**（本条为准）。
4. **类别口径修正**：拼写变体 `u_emissive_color`（1 个节点，非"2 处"）按 lead「按节点各自声明取用、不合并」的口径**视为自发光声明** ⇒
   适配器实测分类 **A=16 / B=7 / C=3**；若只认 `u_emissivecolor`（lead 原清单口径）则为 A=15 / B=8 / C=3。两口径差在**同一个节点**，已在期望表登记。
5. 期望表 `FX029_models_expected.json` 同步修正 `unwired`（**highlight 已接线，移出 unwired**）并附两口径计数。
6. 探针新增字段：`omitted_undeclared` / `approx` / `approx_reason` / `highlight_src` / `highlight_state` / `emissiveIntensity` /
   `blending_asserted=false` / `blending_source`（TransparentMode 映射未定证）/ `depth_bias_state`。
'''
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_report.md'
old = io.open(REP, 'r', encoding='utf-8').read()
if u'§17 task-61' not in old:
    io.open(REP, 'a', encoding='utf-8').write(sec)
    print('已追加 §17')
print('报告 sha16 =', sha(REP), os.path.getsize(REP), 'B')
