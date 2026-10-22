# FXADAPT：26 个 Model 定位/材质复核（2026-09-18）

对象：`assets/weapon_skin_sfx_adapter.js`（sha16 `7FD818AF…`→最新，见文末）· 页面 `board.html?b=weapon_skin_sfx_text_sources&view=wiki`
复现：`python %TEMP%\fxmodel2.py ab`（开）· `… fc`（fail-closed 默认）· Chrome152/CDP，合成 PointerEvent，`__sfxTime(0.5)` 定相位

## ① 定位/尺度：**实测是对的**（不是定位错）
逐条比对 `__probe().models[].measured`（three `Box3().setFromObject` 世界盒）与源 `model_fields.mesh_evidence.bbox_span`：

| 节点 | 源 bbox_span | 实测 size | groupScale |
|---|---|---|---|
| L_m_弹夹圈 | [-1.2838,-0.7466,-1.2838] | **1.2838 / 0.7466 / 1.2838** | 1 |
| H_m_弹夹圈_1 | [-0.9007,-1.0933,-0.9007] | **1.261 / 1.0933 / 1.261** | 1.4（= 源 XScale/ZScale 1.4） |
| H_m_枪托喷出 | [-0.586,-0.586,-2.4729] | **0.586 / 0.586 / 2.4728** | 1 |
| H_m_枪口圈 | [-1.9122,-2.2031,-9.0763] | **1.9122 / 2.203 / 9.0762** | 1 |

- 父级只有一层：`modelGroup.position = attach.anchor + PosOffset`，`modelGroup` 挂在 `sfx-layer`（`scene` 上、每帧 `matrix.copy(root.matrixWorld)`）⇒ **无双重变换**、**无武器缩放叠加**（`groupScale` 已含源轨道）。
- 26 个 GLB 全部按 `model_fields.mesh` = `sfx/model/<stem>.glb` 加载成功（26/26 `ok`，`loadErrors=[]`）。
⇒ 用户看到的"大片平板"**不是坐标/尺度错**，而是**材质**（见 ②）。

## ② 材质：缺 alpha/贴图通道 ⇒ 整片实心 ⇒ 平板 + 盖住武器
源里这批 FX 网格靠 **UV + alpha 贴图**做镂空/流动；`effects.json` 的 Model 节点**没有贴图槽**（1110152 源几乎无主贴图，只有 `u_emissivecolor_Keyframe`/`u_emissive_highlight_intensity_Keyframe`）⇒ 我们只能纯色填充。
三档实拍 A/B（**均已人工看过**）：
- `FXADAPT_ab_normal.png`（NormalBlending）：**不透明浅蓝板**，盖住武器 ✗
- `FXADAPT_ab_add02.png`（Additive ×0.2）：**半透明青色发光，武器本体清晰可见** ✓ ← **最佳**
- `FXADAPT_ab_addsrc.png`（Additive × 源 highlight）：更亮，边缘过曝 ✗

## ③ fail-closed 默认关（已实现）
- 默认 `MODELS_FORCE=null` 且 `effects.models_enabled !== true` ⇒ 26 节点 `state='disabled_fail_closed'`、**不加载不显示**；
  截图 `FXADAPT_fc_main.png`：武器干净、只有那 4 个 Sprite 的青色小环 ✓（**SFX 开关状态＝“SFX 开启”**）。
- 显式开关：`WikiSfxAdapter.models(true|false|null)`；材质：`WikiSfxAdapter.modelMaterial('additive'|'normal', k)`。
- 默认材质改为 **additive×0.2**，并在代码注释里标明它是**显示近似（非源常量）**，源 alpha 通道补上后应移除。

## ④ 旋转回归（26 个 mesh 全部在场景里）
- idle 逐帧 `projCenter` **distinct=1（零跳变）**
- drag：net (−0.0301, +0.0684) · maxstep 0.0077 · `clipped=false`
⇒ Model 未进 root 包围盒（`sfx-layer` 在 scene + `syncToRoot()`），乱转未复发。

## ⑤ 卡点（复核后更正）
- ❌ **更正上轮误读**：`_gim_out\texmap_fx.json` **不是 texmap 表** —— 20 B、内容 `{"sets": {"fx": {}}}`（**空映射**）；我读的是 `GIM_manifest.json` 的 `texmap` **指针字段**，误当"已有 texmap"。与 lead 实测一致 ✓。
- **`.gim` 原始载荷复核**（`_gim_out\raw\`，24 个 `.gim` 全读）：
  - 类名字段表里**有 alpha/blend 字段名**：`OWLAlphaTestMerge`、`PreZAlphaBlend`、`TriSortMethod`（**24/24 均有**）；
  - 但载荷只有 **339–489 B** = 类名表 + `BoundingCenter/BoundingHalf` + `MtlIdx`(=149 等) + 若干**布尔** + `Name`（`Plane003`/`quan_glow`/`fa_zhen`）；布尔 token：`true` 1–3 / `false` 5；
  - **无 alpha 数值、无颜色、无任何贴图路径**（`.tga/.dds/.png/.mat/.cgmat` 正则 **24 个文件全 0 命中**）；
  - 布尔 token 顺序 ≠ 类名字段顺序 ⇒ `OWLAlphaTestMerge/PreZAlphaBlend` 的**值无法可靠映射** ⇒ 标 **unresolved**（不猜）。
- ⇒ 按 fail-closed：**保留 `additive ×0.2` + "显示近似、非源常量" 标注 + Model 默认关**。
- 下一步线索（给 `env-auditor`/chain-auditor）：源 `.sfx` 串池有 **5 条贴图逻辑路径**，其中
  `effect\textures\ring\tex_ring_keji_hgz01_04.tga` 与 `effect\textures\special\heitiane_04_lmq_djs.tga`
  **未被绑到任何 Sprite**（4 个 Sprite 只用另外 3 条）⇒ 很可能就是 Model 的 **`u_maintex`**（其 alpha 才是镂空来源）；
  类名表里还有 `u_maintex_rotation_Keyframe`/`u_overall_opacity_Keyframe`/`u_dissolve_amount_Keyframe` 等轨道名
  ⇒ 建议查 Model 节点的 `ShaderComponent/Uniforms` 块中的 `u_maintex` 绑定与贴图池是否已解出该 `.tga`。
