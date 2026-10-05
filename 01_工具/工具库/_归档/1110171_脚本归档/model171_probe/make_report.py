# -*- coding: utf-8 -*-
'''task-79：生成 MODEL171_probe_report.md（只读取证结论，不改 effects.json）'''
import io, os, json, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
P = os.path.join(OUT, 'MODEL171_probe.json')
REP = os.path.join(OUT, 'MODEL171_probe_report.md')
D = json.loads(open(P, 'rb').read().decode('utf-8'))
rows = D['rows']
E = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110171\effects.json'
eh = hashlib.sha256(open(E, 'rb').read()).hexdigest()[:16].upper()
A17 = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177'
L = []
w = L.append
w(u'# 1110171 Model 层求证报告（task-79）—— ok:3 / visible:0 / 22×C 类\n')
w(u'## 0. 一句话结论（问 C）\n')
w(u'> **1110171 的 Model 层现在「结构上能上屏」，但按当前 adapter 规则会是 0 个上屏，原因分三块：'
  u'(1) 22/28 被判 C 类是【规则缺口】——源里其实有颜色驱动（`u_main_color1..3`/`u_overall_opacity`/`u_emissive_highlight_intensity`），'
  u'我们的 A/B/C 规则只认 `u_emissivecolor` / `u_diffuse_color`；'
  u'(2) 真正「源里就没有颜色」的只有 2 个（`L_模型_水晶01`、`M_模型_水晶02`）；'
  u'(3) 已 `ok` 的 3 个上不了屏是【两个可验证的机制】：`fixedTime` 不受 `% loop` 约束的时间窗问题 + 单位空间差异导致的 10× 缩小。** 这三个都需要 adapter/数据的后续动作，见 §4 最小补丁。\n')
w(u'## 1. 取证（只读，compromises 无）\n')
w(u'| 项 | 值 |')
w(u'|---|---|')
w(u'| `1110171/effects.json`（**本次未改动**） | `%s` |' % eh)
w(u'| 源 bin | `gpk_effect_01_f74635_59115620b779a5e8.bin`（GBK，44 节点 = Dummy 3 / **Model 28** / ParticleSystem 7 / ParticleRes 2 / Sprite 4） |')
w(u'| 探针脚本 | `model171_probe\\model171_probe.py`（只读） |')
w(u'| 机读 | `MODEL171_probe.json` |')
w(u'')
w(u'## 2. B：22 个 C 类逐个求证（**是解析/规则缺口，不是源里没有**）\n')
w(u'统计：**源侧 26/28 节点带颜色相关 uniform**；effects.json 里 **24/28** 带 `uniform_tracks`（4 个连 `uniform_tracks` 都没有 ⇒ 二次缺口）；'
  u'但当前规则只把 **6 个**判为 A/B（A 5 / B 1）⇒ **20 个有源颜色却被判 C**。\n')
w(u'| 节点 | 现判 | 源侧颜色/相关 uniform（原文键名） | 洞见 |')
w(u'|---|---|---|---|')
for r in rows:
    if r['cls_now'] != 'C':
        continue
    sc = r['src_colors']
    note = u'源里有 `%s` ⇒ **规则缺口**' % sc[0].replace('_Keyframe', '') if sc else u'**源里确无颜色 uniform** ⇒ `no_color_source_in_src`'
    w(u'| %s | C | %s | %s |' % (r['node'], json.dumps(sc, ensure_ascii=False) if sc else '—', note))
w(u'')
w(u'- **规则缺口涉及的 uniform 形态**（源里出现、我们的判据不认）：`u_main_color1_Keyframe`/`u_main_color2_Keyframe`/`u_main_color3_Keyframe`、`u_overall_opacity_Keyframe`、`u_emissive_highlight_intensity_Keyframe`。')
w(u'- **4 个节点连 `uniform_tracks` 都没有**（注入缺口）：`L_模型_水晶01`、`M_模型_水晶02`、`M_模型_气流暗`、`H_模型_底暗`（前两个源里也无颜色 uniform；后两个源里有 `u_overall_opacity_Keyframe`）。')
w(u'- **为什么先前漏了**：这套 A/B/C 判据是我在 **task-61 给 1110177** 时按**该皮肤源里只出现 `u_emissivecolor`/`u_diffuse_color`** 的事实定的（1110177 的 dg 批次 20/20 命中该形态）；1110171 的源用的是**另一组命名**（`u_main_color*` / 纯 `u_overall_opacity` / 纯 highlight），**规则没有跨皮肤泛化**，于是 20 个有源颜色的节点被判 C。**这是规则缺口，不是源里没有。**')
w(u'')
w(u'## 3. A：3 个 `ok` 为什么不上屏（逐道门取值）\n')
w(u'3 个 ok = `M_模型_顶渐变`、`H_模型_球03`、`M_模型_球04`（判据：非 C 且 `fxIgnore=FALSE`）。\n')
w(u'| 门 | 取值（三者相同） | 依据 |')
w(u'|---|---|---|')
w(u'| `rec.obj` | **存在**（GLB 加载 ok，404 已归零） | task-78 读数 `ok:3` |')
w(u'| `start` | **0**（`mf.FxStartTime` 缺失 ⇒ `Number(undefined)||0`） | adapter L437 |')
w(u'| `life` | **= `loop` = 2.0**（`mf.FxLifeSpan` 缺失 ⇒ `Number(undefined)||loop`） | adapter L438 + `loop = Number(effects.loop_seconds)` = 2.0（L215） |')
w(u'| `t` / `lt` | `t` 自由运行时 `% loop` ∈ [0,2)；**但 `fixedTime` 冻结时 `t = fixedTime` 且不取模** | adapter **L732-733** |')
w(u'| 可见门 `lt<0 \\|\\| lt>life` | 自由运行 ⇒ 恒假 ⇒ `group.visible=true`；**`fixedTime>2.0` ⇒ 恒真 ⇒ 全部 `visible=false`** | adapter L820-822 |')
w(u'| `scale_track` | **空**（`scale_track:[]`）⇒ 组缩放 = 1×U() | 探针 |')
w(u'| `color_track` | **空**（颜色走 `uniform_tracks`，非 `color_track`） | 探针 |')
w(u'| `opacity_src` | `M_模型_球04` 有 `u_overall_opacity`；另两个无 | 探针 ut |')
w(u'| `TransparentMode` | **缺失（null）** ⇒ 走 `MODEL_BLEND` 默认 additive | 探针 |')
w(u'| GLB 几何（源空间） | `顶渐变` size `[0.464,0.953,3.434]` min `[0.052,0.775,-0.471]`；`球03/球04` size `[0.564,0.408,0.419]` min `[-0.282,0.372,0.753]` | task-77 导出 GLB |')
w(u'| 乘 `U()=0.1` 后 | 变成 **0.05–0.34 模型单位**（≈毫米级） | 计算 |')
w(u'')
w(u'**三分类判定**：')
w(u'- **(i) 该画被 bug 挡住 —— 证据成立（第一嫌疑）**：`fixedTime` 分支**不取模**（L732-733 只在自由运行时 `% loop`），而 1110171 的 `life` 因缺 `fx_life_span` 恒等于 `loop`=2.0；只要复测把时间冻结在 `>2.0 s`，**28 个节点会全部 `visible=false`**。这解释了"`ok:3` 却 `visible:0`"且**像素差为 0**。⇒ 需 lead 在浏览器里读一次 `__sfxDiag().fixedTime`（若 >2.0 即坐实）。')
w(u'- **(iii) 视口外/过小 —— 证据成立（第二嫌疑）**：导出 GLB 的源空间尺度：**1110177 = 13–163（cm 量级）**、**1110171 = 0.46–3.43（m 量级）** ⇒ 同一个 `U()=0.1` 对 1110171 **多缩了 10×**；即使可见也只是毫米级小块。**单位换算不能跨皮肤一刀切**（要么按皮肤定标，要么从源属性推）。')
w(u'- **(ii) 源参数缺失导致本该不可见 —— 部分成立**：`TransparentMode`/`RenderBias`/`FxStartTime`/`FxLifeSpan`/`scale_track` 在 1110171 的 Model 上**全缺**（源 bin 里都有）⇒ 不仅影响时间窗，也让混合模式只能吃默认值。')
w(u'')
w(u'## 4. 最小补丁建议（**我没有改 adapter**，按纪律写在这里）\n')
w(u'1. **规判据泛化（1 行级，adapter）**：`rec.cls` 的判据从"只认 `u_emissivecolor`/`u_diffuse_color`"扩成"**A = 有任一自发光色族（`u_emissivecolor`/`u_emissive_color`/`u_main_color1..3`）/ B = 有 `u_diffuse_color`**"，并把 `u_overall_opacity` 作为**透明度驱动**（不是分类依据）。最小改法：把 `mf.uniform_tracks` 的键前缀集合判为 A/B，其余（仅 opacity/highlight）归 B（有 opacity）或 C。**建议先只做"有 `u_main_color*` 或 `u_overall_opacity` 的节点不再判 C"这一步**，回报读数后再决定是否接进材质。')
w(u'2. **时间窗（bug）**：`L732-733` 的 `fixedTime` 分支应与自由运行一致地 `% loop`（或 `life` 默认值改为**该节点的源 `FxLifeSpan`**，缺则 `loop`）。最小补丁：`var t = (fixedTime !== null ? fixedTime : ...) % loop;`')
w(u'3. **单位（数据/换算）**：`U()=0.1` 是 **1110177 的 cm 空间**推导值；1110171 的 GLB 已是 **m 量级** ⇒ 该皮肤应走 `U()=1`（或按皮肤配置），否则 10× 过缩。**需要你裁定口径**（我可以按"按皮肤定标 + 逐项留档"补数据/开关）。')
w(u'4. **数据补齐（我可以做，需你一句 GO）**：从源 bin 给 28 个 Model **按名新增**：`fx_start_time/fx_life_span/transparent_mode/render_bias/track_type/dir_type/render_order/pos_offset` + `uniform_tracks`（含 4 个当前完全没注入的节点）+ provenance；只新增、canonical diff 通过才写盘。')
w(u'')
w(u'## 5. 已证 / 未证 / 未做\n')
w(u'**已证**：源 bin 44 节点（Model 28）；源侧 26/28 带颜色相关 uniform；effects.json 24/28 有 `uniform_tracks`；当前判 A5/B1/C22；3 个 ok 的 `start=0`、`life=loop=2.0`、`scale_track`/`color_track` 空、`TransparentMode` null；adapter L732-733 的 `fixedTime` 不取模；两皮肤 GLB 尺度差 10×。')
w(u'**未证**：浏览器实际的 `fixedTime` 值（决定 A 的第一嫌疑是否坐实）；1110171 武器对角线（用于把"10× 过缩"量化到"是否真的不可见"）；`u_main_color*` 在源 shader 里的**语义**（属另一族/另一套通道，未反汇编）。')
w(u'**未做**：**未改任何文件**（本轮纯只读；写作用域内的 `1110171/effects.json` 我**没有动**，故 sha16 仍为 `%s`）；未开浏览器；未改 adapter/viewer.json/viewer.js/board/neox_material.json。**没有顶替、没有编造。**' % eh)
io.open(REP, 'w', encoding='utf-8').write(u'\n'.join(L) + u'\n')
print('报告 ->', REP, os.path.getsize(REP), 'B sha16=', hashlib.sha256(open(REP, 'rb').read()).hexdigest()[:16].upper())
print('effects.json 未改动 sha16 =', eh)
