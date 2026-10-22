# FX029 · task-66 —— 把 daoguang_02 的真实源参数补进 23 个 dg 节点

## 0. pin 与自证

| 项 | 值 |
|---|---|
| `1110177/effects.json` | **`4696FF22F57966B2`** → **`9C60BED52F3014E3`**（536463 → 565949 B） |
| 备份 | `effects.json.bak_dgmerge2_20260919_214342` |
| 源 | `gres\0057.gpk` row 32153 · 66,424 B · sha16 `9F4FE3A6AD3F8851`（**自解**，`block_base+off+20` → zstd → GBK XML） |
| 与 lead 源 JSON 交叉核对 | **一致 20 个 / 不一致 [] / 我这边缺 []**（逐字段比 `FxStartTime/FxLifeSpan/TransparentMode/RenderBias/ModelName/TrackType/DirType`） |
| 自证门（写盘前置） | 23 个 dg 节点 **贴图字段未变** = `True`；其余 66 个节点 **逐字节未变** = `True`（不过则脚本拒绝写盘） |
| 未改动 | adapter / viewer.js / viewer.json / neox_material.json / manifest / board / 注册表 / 其它皮肤 |

## 1. 方法（可复现）

脚本 `_target_1110171\FX029_dg_merge2.py`（`--dry-run` 只算不写）：
1. 自解 row 32153 并校验 sha16（与 env-auditor/lead 一致）→ 解析 23 个顶层节点 `{tag, attrs, children[tag,attrs,frames]}`；
2. 按名匹配 dg 节点（**去掉我上轮加的 `__dg` 后缀**）→ 逐字段写入：`start/life/pos_offset/render_bias/transparent_mode/track_type/dir_type/model_name/particlesPerSecond/min|maxSpriteLifespan/min|maxRadius/emissionType/emitAtBegin…`；
3. **子轨道 → `emit`**：该节点块内**每个带 `<Frame Time Value>` 的子元素**按其标签名收入 `{"<轨道名>":[{time,value}]}`（与皮肤自带节点同结构）；另抽 `scale_track`（`ScaleFrame/TrackScale/Scale`）与 `color_track`（`TrackColor/ColorFrame/ColorKeyFrame`）；
4. **逐字段 provenance**：`dg_param_provenance[field] = "dg_src:gres\0057.gpk#32153:<源节点名>:<源属性名>"`；
5. 写盘前跑**自证门**（贴图字段 + 其余节点逐字节），并 `copy2` 备份。

## 2. 逐节点结果（23/23 命中，`no_source_node = 0`）

| 节点 | tag | rate | life | start | emit 轨数 | 补充字段数 |
|---|---|---|---|---|---|---|
| L_空特效_1_1__dg | Dummy | None | 1.500 | 0.000 | 0 | 4 |
| L_空特效_2__dg | Dummy | None | 0.500 | 0.000 | 0 | 4 |
| H_模型bian_glow | Model | None | 0.250 | 0.002 | 2 | 12 |
| M_模型_an_1 | Model | None | 0.450 | 0.023 | 2 | 12 |
| H_模型bian_an_1 | Model | None | 0.300 | 0.100 | 2 | 12 |
| L_模型red_1 | Model | None | 0.350 | 0.050 | 2 | 12 |
| L_模型twl01 | Model | None | 0.380 | 0.001 | 2 | 12 |
| H_mod_外圈电 | Model | None | 0.300 | 0.050 | 2 | 12 |
| M_模型red03_1 | Model | None | 0.450 | 0.000 | 2 | 12 |
| L_模型tou_2 | Model | None | 0.300 | 0.000 | 2 | 12 |
| L_空特效__dg | Dummy | None | 0.500 | 0.000 | 0 | 4 |
| H_mod_刀光_04 | Model | None | 0.400 | 0.000 | 2 | 12 |
| H_mod_刀光_02 | Model | None | 0.450 | 0.003 | 2 | 12 |
| H_mod_刀光_05 | Model | None | 0.350 | 0.001 | 2 | 12 |
| L_模型白边 | Model | None | 0.300 | 0.030 | 2 | 12 |
| M_模型尾_2 | Model | None | 0.300 | 0.001 | 2 | 12 |
| M_鬼火_长条 | ParticleSystem | 20.000 | 0.200 | 0.000 | 18 | 21 |
| H_p_烟雾_02 | ParticleSystem | 20.000 | 0.200 | 0.050 | 18 | 21 |
| M_模型qiliu_2 | Model | None | 0.300 | 0.060 | 2 | 12 |
| H_ParticleRes | ParticleRes | 20.000 | 0.200 | 0.050 | 12 | 13 |
| M_模型尾_glow_1 | Model | None | 0.300 | 0.000 | 2 | 12 |
| M_模型尾_glow_3 | Model | None | 0.300 | 0.000 | 2 | 12 |
| H_鬼火_星点_1 | ParticleSystem | 20.000 | 0.200 | 0.050 | 18 | 21 |

## 3. 逐字段 改前 → 改后（只列变化的字段）

### H_ParticleRes（`ParticleRes`）
- `dg_param_provenance`：null → **{"emissionType": "dg_src:gres\\0057.gpk#32153:H_ParticleRes:EmissionType", "emit": "dg_src:gres\\0057.gpk#32153:H_ParticleRes:children(<Frame Time Value>)", "emitAtBegin": "dg_src:gres\\0057.gpk#32153:H_ParticleRes:EmitA…**
- `dg_param_status`：null → **"ok"**
- `emissionType`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:EmissionType`
- `emit`：null → **{"EmissionDirDegreeFrame": [{"time": 0.0, "value": 0.0}], "EmissionRadius2Frame": [{"time": 0.0, "value": 0.0}], "EmissionRadiusFrame": [{"time": 0.0, "value": 1.0}], "GravityFrame": [{"time": 0.0, "value": 0.0}], "MaxSp…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:children(<Frame Time Value>)`
- `emitAtBegin`：null → **"TRUE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:EmitAtBegin`
- `inside`：null → **"TRUE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:Inside`
- `life`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:FxLifeSpan`
- `maxSpriteLifespan`：null → **2.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:MaxSpriteLifespan`
- `minParticlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:MinParticlesPerSecond`
- `minSpriteLifespan`：null → **2.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:MinSpriteLifespan`
- `particlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:ParticlesPerSecond`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:PosOffset`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:RenderLevel`
- `start`：null → **0.05**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:FxStartTime`
- `track_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_ParticleRes:TrackType`
### H_mod_刀光_02（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_02:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_02:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_02:FxLifeSpan", "model_name": …**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.38}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0733, "value": 0.6}, {"time": 0.1954, "value": 0.6}, {"time": 0.5511, "value": 0.6}, {"time": 0.6519, "value": 0.…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:children(<Frame Time Value>)`
- `life`：null → **0.45**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.003", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 10, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_07_djs.gim", "dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.003", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:PosOffset`
- `render_bias`：null → **"-2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.38}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:ScaleFrame`
- `start`：null → **0.003**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:TrackType`
- `transparent_mode`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_02:TransparentMode`
### H_mod_刀光_04（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_04:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_04:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_04:FxLifeSpan", "model_name": …**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.38}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0412, "value": 1.0}, {"time": 0.1954, "value": 1.0}, {"time": 0.4962, "value": 0.45}, {"time": 0.6168, "value": 0…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:children(<Frame Time Value>)`
- `life`：null → **0.4**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.400", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 13, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_06_djs.gim", "dir_type": "2", "fx_life_span": "0.400", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:PosOffset`
- `render_bias`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.38}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:ScaleFrame`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:TrackType`
- `transparent_mode`：null → **"5"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_04:TransparentMode`
### H_mod_刀光_05（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_05:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_05:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_mod_刀光_05:FxLifeSpan", "model_name": …**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.38}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0733, "value": 1.0}, {"time": 0.6153, "value": 1.0}, {"time": 0.7191, "value": 0.2}, {"time": 0.8672, "value": 0.…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:children(<Frame Time Value>)`
- `life`：null → **0.35**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.350", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 12, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_08_djs.gim", "dir_type": "2", "fx_life_span": "0.350", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:PosOffset`
- `render_bias`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.38}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:ScaleFrame`
- `start`：null → **0.001**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:TrackType`
- `transparent_mode`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_刀光_05:TransparentMode`
### H_mod_外圈电（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_mod_外圈电:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_mod_外圈电:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_mod_外圈电:FxLifeSpan", "model_name": "dg_sr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.5}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.4733, "value": 0.0875}, {"time": 0.7496, "value": 0.4}, {"time": 1.0, "value": 1.0}]}**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.050", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 4, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_09_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.050", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:PosOffset`
- `render_bias`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.5}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:ScaleFrame`
- `start`：null → **0.05**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:TrackType`
- `transparent_mode`：null → **"5"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_mod_外圈电:TransparentMode`
### H_p_烟雾_02（`ParticleSystem`）
- `blend_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:BlendMode`
- `color_track`：null → **[{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:TrackColor`
- `dg_param_provenance`：null → **{"blend_mode": "dg_src:gres\\0057.gpk#32153:H_p_烟雾_02:BlendMode", "color_track": "dg_src:gres\\0057.gpk#32153:H_p_烟雾_02:TrackColor", "dir_type": "dg_src:gres\\0057.gpk#32153:H_p_烟雾_02:DirType", "emissionType": "dg_src:gr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:DirType`
- `emissionType`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:EmissionType`
- `emit`：null → **{"ColorFrame": [{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}], "ColorFramePar": [{"time": 0.0, "value": [0.0, 227.0, 177.0, 128.0]}, {"time": 0.2076, "value": [30.0, 250.0, 242.0, 211.0]}, {"time": 1.0, "value": […**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:children(<Frame Time Value>)`
- `emitAtBegin`：null → **"TRUE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:EmitAtBegin`
- `inside`：null → **"TRUE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:Inside`
- `life`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:FxLifeSpan`
- `maxRadius`：null → **8.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:MaxRadius`
- `maxSpriteLifespan`：null → **1.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:MaxSpriteLifespan`
- `minParticlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:MinParticlesPerSecond`
- `minRadius`：null → **3.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:MinRadius`
- `minSpriteLifespan`：null → **0.9**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:MinSpriteLifespan`
- `particleDir`：null → **"0.000000,1.000000,0.000000"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:ParticleDir`
- `particlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:ParticlesPerSecond`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:PosOffset`
- `render_bias`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:RenderOrder`
- `start`：null → **0.05**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:FxStartTime`
- `track_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_p_烟雾_02:TrackType`
### H_模型bian_an_1（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_模型bian_an_1:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_模型bian_an_1:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_模型bian_an_1:FxLifeSpan", "model_n…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.45}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.3206, "value": 0.4}, {"time": 0.4992, "value": 0.105}, {"time": 0.6061, "value": 0.06}, {"time": 1.0, "value": 0.…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.100", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 6, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_03_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.100", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:PosOffset`
- `render_bias`：null → **"-2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.45}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:ScaleFrame`
- `start`：null → **0.1**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_an_1:TransparentMode`
### H_模型bian_glow（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:H_模型bian_glow:DirType", "emit": "dg_src:gres\\0057.gpk#32153:H_模型bian_glow:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:H_模型bian_glow:FxLifeSpan", "model_n…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.5}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.1359, "value": 0.975}, {"time": 0.429, "value": 0.925}, {"time": 0.6473, "value": 0.2}, {"time": 1.0, "value": 0.0…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:children(<Frame Time Value>)`
- `life`：null → **0.25**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.250", "fx_start_time": "0.002", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 6, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_01_djs.gim", "dir_type": "2", "fx_life_span": "0.250", "fx_start_time": "0.002", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:PosOffset`
- `render_bias`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.5}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:ScaleFrame`
- `start`：null → **0.002**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_模型bian_glow:TransparentMode`
### H_鬼火_星点_1（`ParticleSystem`）
- `blend_mode`：null → **"8"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:BlendMode`
- `color_track`：null → **[{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:TrackColor`
- `dg_param_provenance`：null → **{"blend_mode": "dg_src:gres\\0057.gpk#32153:H_鬼火_星点_1:BlendMode", "color_track": "dg_src:gres\\0057.gpk#32153:H_鬼火_星点_1:TrackColor", "dir_type": "dg_src:gres\\0057.gpk#32153:H_鬼火_星点_1:DirType", "emissionType": "dg_src:gr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:DirType`
- `emissionType`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:EmissionType`
- `emit`：null → **{"ColorFrame": [{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}], "ColorFramePar": [{"time": 0.0, "value": [0.0, 255.0, 187.0, 62.0]}, {"time": 0.0947, "value": [119.0, 255.0, 86.0, 53.0]}, {"time": 0.2208, "value": …**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:children(<Frame Time Value>)`
- `emitAtBegin`：null → **"FALSE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:EmitAtBegin`
- `inside`：null → **"FALSE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:Inside`
- `life`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:FxLifeSpan`
- `maxRadius`：null → **2.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:MaxRadius`
- `maxSpriteLifespan`：null → **0.5**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:MaxSpriteLifespan`
- `minParticlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:MinParticlesPerSecond`
- `minRadius`：null → **0.8**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:MinRadius`
- `minSpriteLifespan`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:MinSpriteLifespan`
- `particleDir`：null → **"0.000000,1.000000,0.000000"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:ParticleDir`
- `particlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:ParticlesPerSecond`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:PosOffset`
- `render_bias`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:RenderBias`
- `render_level`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:RenderOrder`
- `start`：null → **0.05**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:FxStartTime`
- `track_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:H_鬼火_星点_1:TrackType`
### L_模型red_1（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:L_模型red_1:DirType", "emit": "dg_src:gres\\0057.gpk#32153:L_模型red_1:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:L_模型red_1:FxLifeSpan", "model_name": "dg_sr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.52}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.2107, "value": 1.0}, {"time": 0.3679, "value": 1.0}, {"time": 0.5496, "value": 0.2625}, {"time": 0.6809, "value":…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:children(<Frame Time Value>)`
- `life`：null → **0.35**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.350", "fx_start_time": "0.050", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 6, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_10_djs.gim", "dir_type": "2", "fx_life_span": "0.350", "fx_start_time": "0.050", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:PosOffset`
- `render_bias`：null → **"1"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:RenderBias`
- `render_level`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.52}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:ScaleFrame`
- `start`：null → **0.05**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:TrackType`
- `transparent_mode`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型red_1:TransparentMode`
### L_模型tou_2（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:L_模型tou_2:DirType", "emit": "dg_src:gres\\0057.gpk#32153:L_模型tou_2:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:L_模型tou_2:FxLifeSpan", "model_name": "dg_sr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.58}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0962, "value": 0.0}, {"time": 0.2061, "value": 0.1507}, {"time": 0.3115, "value": 1.0}, {"time": 0.5557, "value":…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 14, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_04_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:PosOffset`
- `render_bias`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:RenderBias`
- `render_level`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.58}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:ScaleFrame`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:TrackType`
- `transparent_mode`：null → **"5"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型tou_2:TransparentMode`
### L_模型twl01（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:L_模型twl01:DirType", "emit": "dg_src:gres\\0057.gpk#32153:L_模型twl01:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:L_模型twl01:FxLifeSpan", "model_name": "dg_sr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.46}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0962, "value": 0.0}, {"time": 0.1893, "value": 0.8125}, {"time": 0.4275, "value": 0.9863}, {"time": 0.5557, "valu…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:children(<Frame Time Value>)`
- `life`：null → **0.38**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.380", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 13, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_12_djs.gim", "dir_type": "2", "fx_life_span": "0.380", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.2, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:PosOffset`
- `render_bias`：null → **"5"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:RenderBias`
- `render_level`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.46}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:ScaleFrame`
- `start`：null → **0.001**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:TrackType`
- `transparent_mode`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型twl01:TransparentMode`
### L_模型白边（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:L_模型白边:DirType", "emit": "dg_src:gres\\0057.gpk#32153:L_模型白边:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:L_模型白边:FxLifeSpan", "model_name": "dg_src:gres\\0…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.52}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0427, "value": 0.975}, {"time": 0.2076, "value": 1.0}, {"time": 0.5603, "value": 0.175}, {"time": 1.0, "value": 0…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.030", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 5, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_14_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.030", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:PosOffset`
- `render_bias`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:RenderBias`
- `render_level`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.52}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:ScaleFrame`
- `start`：null → **0.03**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_模型白边:TransparentMode`
### L_空特效_1_1__dg（`Dummy`）
- `dg_param_provenance`：null → **{"life": "dg_src:gres\\0057.gpk#32153:L_空特效_1_1:FxLifeSpan", "pos_offset": "dg_src:gres\\0057.gpk#32153:L_空特效_1_1:PosOffset", "start": "dg_src:gres\\0057.gpk#32153:L_空特效_1_1:FxStartTime", "track_type": "dg_src:gres\\0057…**
- `dg_param_status`：null → **"ok"**
- `life`：null → **1.5**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_1_1:FxLifeSpan`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_1_1:PosOffset`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_1_1:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_1_1:TrackType`
### L_空特效_2__dg（`Dummy`）
- `dg_param_provenance`：null → **{"life": "dg_src:gres\\0057.gpk#32153:L_空特效_2:FxLifeSpan", "pos_offset": "dg_src:gres\\0057.gpk#32153:L_空特效_2:PosOffset", "start": "dg_src:gres\\0057.gpk#32153:L_空特效_2:FxStartTime", "track_type": "dg_src:gres\\0057.gpk#3…**
- `dg_param_status`：null → **"ok"**
- `life`：null → **0.5**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_2:FxLifeSpan`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_2:PosOffset`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_2:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效_2:TrackType`
### L_空特效__dg（`Dummy`）
- `dg_param_provenance`：null → **{"life": "dg_src:gres\\0057.gpk#32153:L_空特效:FxLifeSpan", "pos_offset": "dg_src:gres\\0057.gpk#32153:L_空特效:PosOffset", "start": "dg_src:gres\\0057.gpk#32153:L_空特效:FxStartTime", "track_type": "dg_src:gres\\0057.gpk#32153:L…**
- `dg_param_status`：null → **"ok"**
- `life`：null → **0.5**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效:FxLifeSpan`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效:PosOffset`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:L_空特效:TrackType`
### M_模型_an_1（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型_an_1:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型_an_1:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型_an_1:FxLifeSpan", "model_name": "dg_sr…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.68}], "ShaderComponent": [{"time": 0.0312, "value": [240.0, 1.0, 11.0, 42.0]}, {"time": 0.0, "value": 0.0}, {"time": 0.1634, "value": 1.0}, {"time": 0.6214, "value": 0.125}, {"tim…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:children(<Frame Time Value>)`
- `life`：null → **0.45**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.023", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 5, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_02_djs.gim", "dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.023", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:PosOffset`
- `render_bias`：null → **"-1"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.68}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:ScaleFrame`
- `start`：null → **0.023**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型_an_1:TransparentMode`
### M_模型qiliu_2（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型qiliu_2:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型qiliu_2:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型qiliu_2:FxLifeSpan", "model_name": …**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.0, "value": 0.4}, {"time": 0.3623, "value": 0.55}, {"time": 1.0, "value": 0.6}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0595, "value": 0.0}, {"time": 0.1206, "value": 0.299…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.060", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 5, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_wl_05_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.060", "keyframe_source": {"container": "Uniforms/Variables", "f…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:PosOffset`
- `render_bias`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:RenderOrder`
- `scale_track`：null → **[{"time": 0.0, "value": 0.4}, {"time": 0.3623, "value": 0.55}, {"time": 1.0, "value": 0.6}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:ScaleFrame`
- `start`：null → **0.06**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型qiliu_2:TransparentMode`
### M_模型red03_1（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型red03_1:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型red03_1:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型red03_1:FxLifeSpan", "model_name": …**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 0.53}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.574, "value": 0.2125}, {"time": 1.0, "value": 1.0}, {"time": 0.0312, "value": [180.0, 64.0, 48.0, 2.0]}, {"time":…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:children(<Frame Time Value>)`
- `life`：null → **0.45**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 18, "node"… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_08_djs.gim", "dir_type": "2", "fx_life_span": "0.450", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:PosOffset`
- `render_bias`：null → **"-2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 0.53}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:ScaleFrame`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:FxStartTime`
- `track_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型red03_1:TransparentMode`
### M_模型尾_2（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型尾_2:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型尾_2:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型尾_2:FxLifeSpan", "model_name": "dg_src:gres…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 1.3}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.1924, "value": 0.9125}, {"time": 0.3099, "value": 0.9}, {"time": 0.4183, "value": 0.4106}, {"time": 0.5985, "value…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 6, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_02_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.001", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:PosOffset`
- `render_bias`：null → **"1"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 1.3}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:ScaleFrame`
- `start`：null → **0.001**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_2:TransparentMode`
### M_模型尾_glow_1（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_1:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_1:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_1:FxLifeSpan", "model_name…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 1.6}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0779, "value": 1.0}, {"time": 0.2031, "value": 1.0}, {"time": 0.4824, "value": 0.7625}, {"time": 0.7802, "value": …**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 7, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_04_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:PosOffset`
- `render_bias`：null → **"-1"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 1.6}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:ScaleFrame`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:TrackType`
- `transparent_mode`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_1:TransparentMode`
### M_模型尾_glow_3（`Model`）
- `dg_param_provenance`：null → **{"dir_type": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_3:DirType", "emit": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_3:children(<Frame Time Value>)", "life": "dg_src:gres\\0057.gpk#32153:M_模型尾_glow_3:FxLifeSpan", "model_name…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:DirType`
- `emit`：null → **{"ScaleFrame": [{"time": 0.5, "value": 1.45}], "ShaderComponent": [{"time": 0.0, "value": 0.0}, {"time": 0.0779, "value": 1.0}, {"time": 0.2031, "value": 1.0}, {"time": 0.5695, "value": 0.6125}, {"time": 0.7802, "value":…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:children(<Frame Time Value>)`
- `life`：null → **0.3**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:FxLifeSpan`
- `model_fields`：{"dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "frames_total": 6, "node":… → **{"ModelName": "effect\\mesh\\weapon\\skin\\skin_2003_029\\mod_skin_2003_029_dg_01_djs.gim", "dir_type": "2", "fx_life_span": "0.300", "fx_start_time": "0.000", "keyframe_source": {"container": "Uniforms/Variables", "fram…**
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:PosOffset`
- `render_bias`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:RenderOrder`
- `scale_track`：null → **[{"time": 0.5, "value": 1.45}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:ScaleFrame`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:FxStartTime`
- `track_type`：null → **"3"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:TrackType`
- `transparent_mode`：null → **"5"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_模型尾_glow_3:TransparentMode`
### M_鬼火_长条（`ParticleSystem`）
- `blend_mode`：null → **"8"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:BlendMode`
- `color_track`：null → **[{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:TrackColor`
- `dg_param_provenance`：null → **{"blend_mode": "dg_src:gres\\0057.gpk#32153:M_鬼火_长条:BlendMode", "color_track": "dg_src:gres\\0057.gpk#32153:M_鬼火_长条:TrackColor", "dir_type": "dg_src:gres\\0057.gpk#32153:M_鬼火_长条:DirType", "emissionType": "dg_src:gres\\00…**
- `dg_param_status`：null → **"ok"**
- `dir_type`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:DirType`
- `emissionType`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:EmissionType`
- `emit`：null → **{"ColorFrame": [{"time": 0.0, "value": [255.0, 92.0, 243.0, 107.0]}], "ColorFramePar": [{"time": 0.0, "value": [255.0, 255.0, 193.0, 102.0]}, {"time": 0.4213, "value": [150.0, 255.0, 167.0, 85.0]}, {"time": 0.6929, "valu…**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:children(<Frame Time Value>)`
- `emitAtBegin`：null → **"FALSE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:EmitAtBegin`
- `inside`：null → **"FALSE"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:Inside`
- `life`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:FxLifeSpan`
- `maxRadius`：null → **0.8**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:MaxRadius`
- `maxSpriteLifespan`：null → **0.4**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:MaxSpriteLifespan`
- `minParticlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:MinParticlesPerSecond`
- `minRadius`：null → **0.4**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:MinRadius`
- `minSpriteLifespan`：null → **0.2**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:MinSpriteLifespan`
- `particleDir`：null → **"0.000000,1.000000,0.000000"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:ParticleDir`
- `particlesPerSecond`：null → **20.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:ParticlesPerSecond`
- `pos_offset`：null → **[0.0, 0.0, 0.0]**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:PosOffset`
- `render_bias`：null → **"4"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:RenderBias`
- `render_level`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:RenderLevel`
- `render_order`：null → **"0"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:RenderOrder`
- `start`：null → **0.0**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:FxStartTime`
- `track_type`：null → **"2"**  ｜ 源＝`dg_src:gres\0057.gpk#32153:M_鬼火_长条:TrackType`

## 4. 3 个"未命中名"的结论

lead 报告的 3 个未命中名是 `L_空特效_1_1__dg`、`L_空特效_2__dg`、`L_空特效__dg` —— 它们**并不是源里没有**，而是**我上一轮为做命名空间隔离给它们加了 `__dg` 后缀**。去掉后缀后在源 `all_node_names`（63）中**精确命中** `L_空特效_1_1` / `L_空特效_2` / `L_空特效` ⇒ **已按源补全（`dg_param_status="ok"`），不需要写 `no_source_node`**；行内保留 `__dg` 名（隔离不可回退，否则会与 hit/jisha 的同名 Dummy 串）。

## 5. 补全后可驱动性

- `M_鬼火_长条`（ParticleSystem）：源 rate=20.000/s × life=0.200 ⇒ 稳态存活 ≈ 4.00 个；emit 18 轨（含 `u_*_Keyframe`）⇒ **rate/寿命/尺寸轨道齐全，可驱动**；仍缺：贴图绑定（这 23 节点的贴图字段由 lead 本轮绑定，我一行未动）。
- `H_p_烟雾_02`（ParticleSystem）：源 rate=20.000/s × life=0.200 ⇒ 稳态存活 ≈ 4.00 个；emit 18 轨（含 `u_*_Keyframe`）⇒ **rate/寿命/尺寸轨道齐全，可驱动**；仍缺：贴图绑定（这 23 节点的贴图字段由 lead 本轮绑定，我一行未动）。
- `H_ParticleRes`（ParticleRes）：源 rate=20.000/s × life=0.200 ⇒ 稳态存活 ≈ 4.00 个；emit 12 轨（含 `u_*_Keyframe`）⇒ **rate/寿命/尺寸轨道齐全，可驱动**；仍缺：贴图绑定（这 23 节点的贴图字段由 lead 本轮绑定，我一行未动）。
- `H_鬼火_星点_1`（ParticleSystem）：源 rate=20.000/s × life=0.200 ⇒ 稳态存活 ≈ 4.00 个；emit 18 轨（含 `u_*_Keyframe`）⇒ **rate/寿命/尺寸轨道齐全，可驱动**；仍缺：贴图绑定（这 23 节点的贴图字段由 lead 本轮绑定，我一行未动）。
- Model **16 个**：`model_glb`（上轮）+ 本轮 `model_name/transparent_mode/render_bias/track_type/dir_type/start/life/pos_offset` + `emit`/`scale_track` + 上轮 `uniform_tracks` ⇒ **A 类 9 个可渲（自发光+additive）**；C 类 7 个仍按纪律不渲（`no_color_driver_unresolved`）。
- Dummy 3 个：`life/start` 已补（`L_空特效__dg` 0.5s、`L_空特效_1_1__dg` 1.5s、`L_空特效_2__dg` 0.5s）；无子轨道（源亦然）。

## 6. 已证 / 未证 / 未做

**已证**：源 row 32153 = 66,424 B / sha16 `9F4FE3A6AD3F8851`（我自解，与 lead/env-auditor 三方一致）；23/23 节点命中（含 3 个 Dummy 名映射）；与 lead 源 JSON **20/20 逐字段一致**；每字段带 provenance；写盘前自证门通过；JSON `json.load` 可读通。
**未证**：`TransparentMode` / `BlendMode` / `RenderBias` 的**枚举语义**（仍 unresolved，本轮只原样搬值）；子轨道**更深一层嵌套**（我只取节点块内的**一层** children 及其 `<Frame>`，若源里有 `children→children` 的帧序列未纳入）；`TrackCircle`/`TrackRotate` 等**非帧**子元素的语义未驱动。
**未做**：未开浏览器（验收另派）；未改贴图字段（纪律要求）；未改 viewer.json（lead 内联）；未解 `daoguang_02.sfx` 内层（仍登记）。

