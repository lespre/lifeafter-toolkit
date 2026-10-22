# FXADAPT：1110152 特效节点渲染补齐（只读复核 + 适配器修复）

对象：`E:\la拆包项目\08Lifeafter wiki\assets\weapon_skin_sfx_adapter.js`（写作用域内）
复现：`python %TEMP%\fxadapt2.py`（Chrome152/CDP 10045，合成 PointerEvent，`__sfxTime(0.5)` 固定相位）
证据：`FXADAPT_result.json` / `FXADAPT_probe.json` / `FXADAPT_missing_resources.json` / `FXADAPT_1110152_{off,on,on_afterdrag}.png`

## ① 26 个 Model：**能拿到路径，拿不到资产**
- 字段名 = **`ModelName`**（源 .sfx 的 class/字段名表：`Model·ModelName·PosOffset·ScaleFrame·TrackScale·XScale·YScale·ZScale`）。
  源文件 `03拆包产物\_target_1110171\FXSRC_exact\1110152_fx_skin_1012_009_idle_01.sfx.sfx`（33,093 B，c159 二进制对象图，**不是 XML**）。
- 串池里明文出 **24 条唯一 `.gim` 逻辑路径**（覆盖 26 个 Model 节点，其中 `dafazhen_hgz01_01` 被 3 个节点共用）：
  `effect\mesh\weapon\skin\skin_1012_009\mod_skin_1012_009_zs_{bagua,dafazhen(_glow),_danxia_lg,danxia_quan,dianlu,fw,liuguang,piaodai(_glow),_qkqt_quan,qt_penqi,quan_lg,shujuliu(_glow,_hou,_raodong)}_hgz01_0N(.gim)`（全表见 `FXADAPT_missing_resources.json`）。
- **`.gim` 本体：全盘 0 命中**（`Get-ChildItem E:\la拆包项目 -Recurse -Filter mod_skin_1012_009*`），且工具库只有
  `fpk_scene_extractor.py` / `find_*_model*.py`（只读路径字符串），**无 .gim→mesh 解析器**。
  ⇒ **缺资产 + 缺解析器，禁止占位几何**，26 个 Model 保持不渲染（适配器 `__audit.unsupportedNodes` 显式列出）。

## ② ParticleRes 4 / ParticleSystem 0：为什么是 0
- 旧实现两处过滤把它吃掉：`nodes.filter(n => n.texture_candidate)`（这 4 个节点 `texture_candidate=null`）+ `tag==='ParticleSystem'`（源里是 **`ParticleRes`**）。
- 且 `effects.json` 里这 4 个节点 `texture/emit/color_track` **全空**；源里它们只引用子帧
  `fx_skin_1012_009_idle_part_01/02.sfx`（part_01 已取出 2,111 B，其内容是 FxGroup/Model/Uniforms，**不是粒子参数表**；part_02 **源文件缺失**）。
  ⇒ 无速率/寿命/贴图可驱动，**不伪造粒子**。
- 适配器已改：粒子 tag 匹配放宽为 `/^Particle/i`，并把源粒子节点登记为 `drivable:false` + why。
  现在 `sfxDiag` = `{spriteNodes:4, particleSystems:4, particleSystemsActive:0}`（**4 = 源节点数，0 = 可驱动数**），
  明细在 `WikiSfxAdapter.__audit`（viewer 的 sfxDiag 只挑 6 个字段，所以我另开 `__audit`/`__probe`）。

## ③ colorOrder：**已证 = (A,R,G,B)**（不再是纯 unproven）
- 源 `ColorFrame` 值：`[236,23,177,255]`（M_旋转光环）、`[247,0,123,255]`、`[67,30,232,255]`。
- 两种解释的判别：ARGB ⇒ rgb=**青色** (23,177,255)，α=0.93；RGBA ⇒ rgb=**品红** (236,23,177)，α=1.0。
- 实测（`fx_pix.py`，开/关同相位差分）：特效像素**色相 80.8% 落 160–210°、11.9% 落 210–260°、品红 290–340° = 0.0%**，中位色相 180°
  ⇒ 渲染色是**青色**，与 ARGB 一致、与 RGBA（品红）矛盾 ✓ 结论：`(A,R,G,B)`，残留不确定性只在贴图是候选（非源级绑定）。

## ④ 真正让"特效弱到看不见"的原因（适配器自造常数）—— 已修
- 探针实测（修前）：4 个 sprite `ready:true, visible:true, opacity 0.066–0.242`，但 `scale = 0.028–0.105` 世界单位；
  相机 `dist 14.886 / fov 34` ⇒ 1 单位≈88 px ⇒ sprite 只有 **2–9 px**，加法混合下连 2/255 都改不动
  ⇒ **开/关静止帧 canvas 区 0 像素变化**（旧截图对：`FXSRC_1110152_sfxon/off_full.png` 也只差 134 px = SFX 按钮文字）。
- `0.035` 是适配器**自造系数**（无源依据）；源字段是 `radius`（1.0/0.82/3.0/0.8）+ `Scale/XScale/…`（本 fx 的 `scale_track` 为空 ⇒ 缺省 1）。
  改为 `scale = radius × 源 scaleTrack(缺省 1)`。
- 修后同一 A/B：**changed_px 134 → 1,140（8.5×）**，差分框 x[549,736] y[375,772]（画布内），
  色相 80.8% 青、中位 180°，mean RGB [46.5,77.7,79.3]、饱和度 0.475 ⇒ 青环真的画出来了。

## ⑤ 旋转回归（沿用 ROTBUG 修复：scene 挂载 + syncToRoot）
| | idle 逐帧 `projCenter` | 拖动净漂移 | 单步最大跳变 | clipped | 投影盒宽 |
|---|---|---|---|---|---|
| SFX OFF | distinct=1 | (−0.0301, +0.0684) | 0.0077 | false | 0.577 |
| SFX ON | **distinct=1（零跳变）** | (+0.0023, **−0.0042**) | 0.0055 | false | 0.483 |

⇒ 开 SFX 不再改变轴心（ON 的 `pc0` 与 OFF 结束时逐位相同 [0.4684,0.5703]），无乱转、无裁剪。

## ⑥ 卡点
26 Model 需要：**(a)** 从 effect 容器解出 `.gim`（24 条路径已给全）；**(b)** 一个 `.gim` 顶点/材质解析器（当前不存在）。
4 ParticleRes 需要：把 `part_01/02.sfx` 的内容（含 part_02 源文件）展开成 `emit/texture/color` 参数写进 `effects.json`
（`effects.json` 属皮肤资产，不在我写作用域，未改）。
