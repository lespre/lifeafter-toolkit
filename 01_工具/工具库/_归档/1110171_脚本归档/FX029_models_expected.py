# -*- coding: utf-8 -*-
'''task-61 步骤2-b：从改后的 effects.json 导出「适配器应做成的样子」期望表 + 追加报告 §16'''
import io, os, re, json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
E = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177\effects.json'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_expected.json'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_report.md'
J = json.loads(open(E, 'rb').read().decode('utf-8'))
MD = [n for n in J['nodes'] if n.get('tag') == 'Model']
rows = []
for n in MD:
    mf = n.get('model_fields') or {}
    ut = mf.get('uniform_tracks') or {}
    cls = 'A' if (ut.get('u_emissivecolor_Keyframe') or ut.get('u_emissive_color_Keyframe')) else ('B' if ut.get('u_diffuse_color_Keyframe') else 'C')
    op = ut.get('u_overall_opacity_Keyframe')
    db = ut.get('u_depth_bias_Keyframe')
    unw = sorted(k for k in ut if re.search(r'dissolve|highlight_intensity|u_intensity|emissive_power|softparticle|uvspeed|tilling|uv_offset|speed_', k))
    sk = lambda t: ([round(x['value'][0], 4) for x in t if isinstance(x['value'], list)] if False else [x['value'] for x in t])
    rows.append({
        'node': n['name'], 'class': cls, 'glb': mf.get('model_name') or n.get('model_name'),
        'transparent_mode': mf.get('transparent_mode'), 'render_bias': mf.get('render_bias'),
        'drivers_used': sorted(ut.keys()), 'unwired': unw, 'tex_bound': False,
        'opacity_src': 'u_overall_opacity' if op else None, 'opacity_frames': (len(op) if op else 0),
        'opacity_first': (op[0]['value'] if op else None),
        'emissive_src': ('u_emissivecolor' if ut.get('u_emissivecolor_Keyframe') else ('u_emissive_color' if ut.get('u_emissive_color_Keyframe') else None)),
        'diffuse_src': ('u_diffuse_color' if ut.get('u_diffuse_color_Keyframe') else None),
        'depth_bias_src': ('u_depth_bias' if db else None), 'depth_bias_first': (db[0]['value'] if db else None),
        'color_first': ((ut.get('u_emissivecolor_Keyframe') or ut.get('u_emissive_color_Keyframe') or ut.get('u_diffuse_color_Keyframe')) or [{}])[0].get('value'),
        'fallback_reason': (None if cls != 'C' else 'no_color_driver_unresolved'),
        'expected_render': cls in ('A', 'B'),
    })
summ = {
    'rows': len(rows),
    'class_counts': {c: sum(1 for r in rows if r['class'] == c) for c in 'ABC'},
    'expected_rendered': sum(1 for r in rows if r['expected_render']),
    'opacity_src_rows': sum(1 for r in rows if r['opacity_src']),
    'depth_bias_rows': sum(1 for r in rows if r['depth_bias_src']),
    'unwired_rows': sum(1 for r in rows if r['unwired']),
    'unwired_items': sorted({u for r in rows for u in r['unwired']}),
}
json.dump({'summary': summ, 'rows': rows}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1))
print('期望表 ->', OUT, os.path.getsize(OUT), 'B')
sec = u'''

---

## §16 task-61 步骤② —— 实现落地（源字段注入 + 适配器保守材质）

### 一、改动清单（逐处行文）
**A. 数据侧（唯一写入 `1110177/effects.json`，脚本 `03拆包产物\\_target_1110171\\FX029_model_keyframes.py`）**
1. 26/26 Model 节点新增 `model_fields.uniform_tracks`（**源** uniform 关键帧，原样注入：96 轨道 / 254 帧；规则 `<u_*_Keyframe ChangeType Interpolator><Frame Time Value/>`）。
2. `model_fields.uniform_tracks_meta`（每轨 `ChangeType`/`Interpolator` 原值）+ `keyframe_source`（sfx 文件/节点/轨道清单/帧数，含「未做任何解释换算」声明）。
3. 源属性落到 `model_fields` 的既有小写键（供适配器运行时优先读取）：`transparent_mode/render_bias/track_type/render_order/dir_type/render_level/fx_start_time/fx_life_span/model_name/post_process_kind/scale_type`。
4. `model_field_patch.model_keyframes` 记录本次注入统计（含**源侧分类自检**：A=15 / B=8 / C=3，与既有驱动计数表一致）。
5. 备份 `effects.json.bak_modelkf_20260919_184146`；sha16 `10CC9A938BE92A10` → **`399223E5F0B15813`**（400,615 → 441,573 B）。
6. **未写入**：`models_enabled`（保持默认关）、`renderable_by_adapter`（未动）、任何贴图绑定（`tex_bound=false` 一律）。

**B. 适配器侧（`08Lifeafter wiki/assets/weapon_skin_sfx_adapter.js`）**
7. 新增 `mdlRGB(col)`：Model 源色列序**复用已独立 PASS 的 `COLOR_ORDER`**（默认 `'rgba'` ⇒ 列 0..2；`'argb'` ⇒ 1..3）。**U5 登记**：1110152 时代 Model 路径写死 `(A,R,G,B)`，两说并存、`colorOrder()` 一处置换，未定证前不作结论。
8. `rec` 新增：`cls`(A/B/C，**只看源驱动项存在性**)、`emissive_src`/`diffuse_src`/`opacity_src`、`opTrack`、`db`、`drivers_used`、`unwired`、`tex_bound=false`、`fallback_reason`。
9. `applyModelMaterial` 改为保守口径：A=emissive 源色 + `color` 置黑 + additive；B=`color` 源色 + emissive 置黑 + normal；两者 `depthWrite=false`/`depthTest=true`；`emissiveIntensity=1`（中性恒等，**源强度项一律不接线**）；`opacity` **只取** `u_overall_opacity`（无 ⇒ 1）；`polygonOffset` **仅源有 `u_depth_bias` 时启用**（10/26 节点）。
10. 逐帧驱动：RGB 走 `mdlRGB`；`a` 取 `u_overall_opacity`；**删除** 旧版 `a = 颜色alpha × u_maintex*_opacity`、`inten = u_maintex*_brightness/100 或 highlight`（源公式 unresolved ⇒ 不猜）。
11. `models(on)`：C 类**即使开也不加载**（`disabled_no_color_driver` / `no_color_driver_unresolved`）；`hasTex0` 仍不加载；默认仍 `MODELS_FORCE=null` ⇒ 跟随 `effects.models_enabled`（未写 ⇒ **默认关**，不改变默认行为）。
12. `modelMaterial(mode,k)`：改成按**源轨道**重取颜色/透明度后再套用（旧版把现有 `color` 当 rgb 传回 ⇒ A 类置黑的 color 会被写进 emissive，属旧缺陷）。`k=null` 默认不加任何系数。
13. `__sfxDiag().models[]` 逐节点新增 lead 指定字段：`'class'`、`glb`、`drivers_used`(数)+`drivers`(表)、`unwired`、`tex_bound`、`opacity`、`opacity_src`、`emissive_src`、`diffuse_src`、`depth_bias_src`、`blending`、`depthWrite`、`depthTest`、`polygonOffset(+Units)`、`fallback_reason`，并保留 `state/hasObj/objVisible/groupVisible/scale/measured/expectedSpan`。
14. `modelBranchBasis` **追加**（不覆盖历史）：`task61_rule` / `task61_sources` / `task61_color_order`。
15. **未改动**：`unitScale/sprSlice/colorOrder/psFallback` 的语义一行未改（Model 路径只是*调用* `COLOR_ORDER`）；`viewer.js`/`viewer.json`/`neuro_material.json`/manifest/board/registry 一律未碰。
16. 备份 `weapon_skin_sfx_adapter.js.bak_task61_20260919_184250`；`node --check` exit=0；sha16 `544D3A4A1B2CC591`(77,511 B) → **`6A0ED1DA58705F21`**(84,657 B)。

### 二、期望表（从改后数据静态导出，供浏览器实测对照）
见 `FX029_models_expected.json`（26 行 + summary）。

### 三、卡点（需 lead 处理才可测量）
- **viewer.json 需重新内联新 effects.json**（`399223E5F0B15813`）；否则页面里仍是旧数据 ⇒ 26 个 Model 全被判 C 类、`models(true)` 一个都不渲。当前 `1110177/viewer.json 7575FAFAD33DD670` 仍内联旧 effects（`10CC9A938BE92A10`）。
'''
old = io.open(REP, 'r', encoding='utf-8').read()
if u'§16 task-61' not in old:
    io.open(REP, 'a', encoding='utf-8').write(sec)
    print('已追加 §16')
b = open(REP, 'rb').read()
print('报告 sha16 =', hashlib.sha256(b).hexdigest()[:16].upper(), len(b), 'B')
