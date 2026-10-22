# FXADAPT：Model 材质升源级（2026-09-18 自主迭代）

适配器：`assets/weapon_skin_sfx_adapter.js`（本版 sha16 见 json 记录）· 证据 `FXADAPT_final.json` / `FXADAPT_final_*.png`

## ① 源级 / 近似 清单
**已换为源级**（`MODEL_BLEND_K` 默认 `null` = 不加任何自造系数）：
| 项 | 源 | 实测读数 |
|---|---|---|
| 颜色 RGB | `u_emissivecolor_Keyframe[1..3]` | `color:00f1ff`（源 (0,225,255)） |
| **opacity** | `u_emissivecolor_Keyframe[0]` = **A**/255（`color_format` 明写 (A,R,G,B)） | `opacity:0.894` = 228/255 ✓ |
| 强度 | `u_emissive_highlight_intensity` | `emissiveIntensity:1` |
| 缩放 | `ScaleFrame` / `scale_XScale|YScale|ZScale` | `groupScale 1.0/1.4` |
| 时间窗/排序 | `FxStartTime` / `FxLifeSpan` / `RenderOrder` | — |

**本皮肤 1110152 缺（0/26）**：`u_maintex{1,2,3}_opacity_Keyframe`、`u_maintex{1,2,3}_brightness_Keyframe`
（lead 给的那批是 **1110171** 的值）⇒ 按规则"缺失=×1.0 / 回落源 highlight"并标 absent。
**旋转**：`u_maintex_rotation_Keyframe` 本皮肤 **1/26** 节点有（`[{t0,[360]},{t5,[0]}]`）⇒ 已接线为 `group.rotation.z`，
但**轴=本地 Z 未证** ⇒ 标 approximate。
**仍近似**：blending 选型（源 Model 无 `blend_mode`）；显式传 k 时该系数为近似。
**归一说明**：若将来取到 brightness，按 **value/100**（0–100 百分比口径；源公式未取到 ⇒ 半源级）。

## ② 量化（同姿态同相位，`__sfxTime(0.5)`，SFX 开启）
| 状态 | 受影响像素 | 占比 | meanRGB |
|---|---|---|---|
| Model **默认关**（fail-closed） | 1,006 | 0.100% | [42,75,75]（只有 4 Sprite 的环） |
| Model **开 + 源级 additive** | **105,377** | **10.445%** | **[248,251,251] 近白** |
| Model 开 + normal（源级） | 105,425 | 10.449% | [210,238,238] |

## ③ 关键结论（否证"系数导致白块"）
换成**源级 opacity=0.894 + additive 后画面更白** ⇒ 白块**不是**近似系数造成的，而是缺 **`u_maintex` 的 alpha 遮罩**
（源里真正的"镂空"来源；本皮肤该轨道 0/26、贴图亦缺）⇒ **在拿到 maintex/alpha 之前，Model 应继续默认关**。

## ④ 回归
- 旋转：idle 逐帧 `projCenter` **distinct=1（零跳变）**；ON drag net (+0.0022,−0.0042)/maxstep 0.0053；OFF net (−0.0289,+0.0684)/0.0077；`clipped=false`
- `errors:0` · `loadErrors:[]` · `models(true)` → `{"loadStarted":26}` → 26/26 ok · 默认 `26×disabled_fail_closed`
