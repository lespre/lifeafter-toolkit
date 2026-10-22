# RX_energy_budget：源式晶体 BRDF 为何让画面变暗 —— 能量预算诊断（只读）

> **一句话结论**：**Lead 的假设成立** —— 源 shader 有一套**完整的环境辐照/环境漫反射预算**（SH `u_env_sh` + `u_ambient`×`u_char_ambient` + 实时天空 cube `t_realtime_env_spec` 的加权累加，`L564-578` / `L626-628`），而**我们的链只覆写了镜面 radiance（`getIBLRadiance`），从未触碰 irradiance** ⇒ `diffuse ×= (1−metal)` 抽掉的能量**没有任何东西补上** ✓。
> **未改任何文件**；未起浏览器。**pin 校验**：`adapter 544D3A4A1B2CC591` ✓ · `viewer.json(1110177) 7575FAFAD33DD670` ✓ · manifest `1110171 64A07D5DF157EC16` / `1110177 A05C4F2C8DDFCF9A` ✓ · **`viewer.js` 实测 `40618CC0FF433C3F`（364,606 B, 09-19 17:09）≠ 你给的 `876C249A695667BA`** ⇒ 本文 viewer 行号以 **`40618CC0FF433C3F`** 为准。

---

## 1. 本链进入 final color 的间接项（逐项 + 量级证据）

| 项 | 本链状态 | 证据（文件:行号 / 命令） |
|---|---|---|
| **`getIBLIrradiance`（环境漫反射/辐照）** | **从未被本链改动**；其值来自 three 的 `scene.environment`，而该 environment 是**中性 PMREM 棚**（不是源资产）；且在 `envAllowed=false` 时 `envMapIntensity=0` ⇒ **连这份也归 0** | **grep `getIBLIrradiance` 在 `viewer.js` 内 0 命中** ✓（注入只改名/覆写 `getIBLRadiance`：`L1415-1423`、`L1528-1529` `#define getIBLRadiance getIBLRadiance_three`）；环境来源 `L274 state.scene.environment=pmrem.fromScene(envScene,…)`；`L296` 注释「scene.environment 保持…中性 PMREM」；门闸 `L1377/L1405 envMapIntensity:(envAllowed?1.0:0.0)` |
| **`getIBLRadiance`（环境镜面 radiance）** | **被本链接管**：从源 cube 产出（`uCustomIbl`），并带 `uIblScale / uIblMix / uIblRot / uIblRotOn` | `L1415-1431`（新增函数 + `uCustomIbl`）、`L1476-1478`（rot 开关）、`L1516-1517`（uniform 声明） |
| `sourceEnvWeight`（注入链 `q_envW`） | 存在（片元标记 `has_q_envW=true`，我早期实测 15/15 prim） | `RX_CRYSTAL_census`：`__fragMarkers().has_q_envW` 全 true ✓ |
| `uCubeBrightness`（`u_cube_brightness` 接线） | 已接但**效果极小**（±0.5%~2.7%） | task-45 实测（Lead 转述）✓ |
| `uIblRot` | 已接（默认 0；task-45 接源值后仍 ±0.5%~2.7%） | `L1465/L1476-1478` ✓ |
| **源侧 SH 环境辐照 / 实时天空 cube / lightmap 系数** | **本链完全没有**（无 uniform、无采样、无注入） | §2 逐项 ✓ |
| 直接光 | 三盏 rig 灯（`HemisphereLight` + 2×`DirectionalLight`） | 我早期实测 `__matDump().lights` ✓ |

**⇒ 关键核实结论**：**`getIBLIrradiance` 在本链"结构上"没有被源化，且在 `envAllowed=false` 时被 `envMapIntensity=0` 直接归零** ⇒ **"环境漫反射"这一预算在本链里等于不存在** ✓（与 Lead 假设一致）

## 2. 源 shader 的能量预算（DXBC 反汇编，代表变体 `_disasm\cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm`）

### 2.1 ★ 环境辐照 / 环境漫反射（**我们缺的就是这项**）
```
L564  mul r13.xyz, cb1[0].xyzx, cb1[284].xyzx     ; 环境色 = u_ambient × u_char_ambient
L567  mov r14.w, 1.0
L568  dp4 r15.x, cb1[148].xyzw, r14.xyzw          ; ┐ SH band1（u_env_sh = cb1[148..150]）
L569  dp4 r15.y, cb1[149].xyzw, r14.xyzw          ; │
L570  dp4 r15.z, cb1[150].xyzw, r14.xyzw          ; ┘
L571  mul r14.xyzw, r4.xyyy, r14.yyzx
L572  dp4 r16.x, cb1[151].xyzw, r14.xyzw          ; ┐ SH band2（cb1[151..153]）
L573  dp4 r16.y, cb1[152].xyzw, r14.xyzw          ; │
L574  dp4 r16.z, cb1[153].xyzw, r14.xyzw          ; ┘
L575  add r14.xyz, r15.xyzx, r16.xyzx             ; 环境辐照 = band1 + band2
L576  mul r4.w, r4.z, r4.z
L577  mad r4.w, r4.x, r4.x, -r4.w
L578  mad r14.xyz, cb1[154].xyzx, r4.wwww, r14.xyzx   ; + 二次项（cb1[154]）
```
```
L624  add r7.w, l(-1.000000), cb1[281].z          ; mip 上限（u_realtime_skylight_max_mip_level，2/15 变体用）
L626  sample_l_indexable(texturecube)(...) r7.xyz, r7.xyzx, t8.xyzw, s0, r7.w   ; ★ t8 = t_realtime_env_spec（实时天空 cube）
L627  mul r7.xyz, r13.xyzx, r7.xyzx               ; × (u_ambient × u_char_ambient)
L628  mad r15.xyz, r7.xyzx, r6.xxxx, r15.xyzx     ; ★ 累加进环境项累加器 r15（权重 r6.x）
```
**⇒ 源侧环境漫反射 = `SH(cb1[148..154])` ⊕ `realtime_sky_cube(t8) × u_ambient × u_char_ambient`（再乘权重）** ⇒ **这就是 `(1−metal)` 抽掉漫反射后源里用来补的那一项** ✓

### 2.2 逐系数状态与位置（15 个 crystal PS 普查）
| 系数 | cbuffer 槽位 | 可用 / `[unused]` | 用途证据 |
|---|---|---|---|
| `u_env_sh` | **cb1[148]**（off 2368，声明 L157 ✓） | **9 / 6** | `dp4` × 6 行（L568-574 ✓） |
| `u_ambient` | **cb1[0]**（off 0，声明 L100 ✓） | **9 / 6** | `L564 mul …, cb1[0].xyzx, cb1[284].xyzx` ✓（`2490ff82` L588 亦用 ✓） |
| `u_char_ambient` | **cb1[284]**（off 4544，声明 L209 ✓） | **9 / 6** | `L564` + `L1087 mul r2.xyz, v4.xyzx, cb1[284].wwww` ✓ |
| `u_env_day2night_exposure` | **cb1[239]**（off 3824，声明 L175 ✓） | **6 / 9** | `2490ff82 L585 mul r5.xyz, r5.xyzx, cb1[239].xxxx` ✓ |
| `u_lightmap_factor` | **cb1[86]**（off 1384，声明 L135 ✓） | **6 / 9** | `2490ff82 L582 mov_sat r3.w, cb1[86].z` / `L620 iadd r5.w, l(-1), cb1[86].x`（本变体 5 处）✓ |
| `u_env_intensity` | cb1（off 未取） | **0 / 15** | **15/15 `[unused]`** ⇒ 该族不用它（解释 task-45 的"环境旋钮效果小"一半来自此处 ✓） |
| `u_ambient_range` | — | **0 / 15** | 15/15 `[unused]` |
| `u_vlm_*`（全部 19 个：`u_vlm_uv_scale`/`u_vlm_indirect_origin_uv`/…） | — | **0 / 15** | **15/15 `[unused]`** ⇒ **VLM（体素光图）路径在该族未启用 ⇒ 排除**（不是缺项）✓ |
| `u_realtime_skylight_max_mip_level` | cb1[281] | 2 / 13 | `L624` ✓ |
| `t_realtime_env_spec`（实时天空 cube） | t8 | 绑定 2/15 | `L274` 绑定表 + `L626 sample_l` ✓ |
| `t_env_spec_array`（探针 cube 数组） | t6 | 绑定 3/15 | `L272` 绑定表 ✓ |

**⇒ 我们链缺的三项（按重要性）**：
1. **SH 环境辐照**（`u_env_sh` cb1[148..154] + `u_ambient`×`u_char_ambient`）——**漫反射环境预算** ✗
2. **实时天空 cube**（`t_realtime_env_spec` t8）——环境色的来源（与我们绑的 `qiangpi` 皮肤 cube 不是同一资产）✗
3. **lightmap/shadow 系数**（`u_lightmap_factor` cb1[86]）与其分支（`L630-640`）✗

## 3. 量化"缺多少"（用已有读数估算 + 可证伪预测）

**能量账**：开 `(1−metal)` 后，漫反射被抽走 `metal × albedo × (直射漫反射 + 环境漫反射)`，同时 F0 抬到 `albedo`（镜面增益）。实测**净**变化：
- 1110171 全图 `p95 −5.59%`、`>0.5 −41.2%`（`3.394→1.995`）、`p50` 几乎不动（−0.7%）——**净损失集中在亮部** ⇒ 亮部原本由**漫反射主导** ⇒ 被抽走的漫反射**没有被补回**，且镜面增益不足以抵消 ✓
- **逐 prim**：prim5 **−6.39%** 且 **`>0.5` −80.6%** ⇒ 该 prim 的亮像素几乎全是漫反射 ⇒ 环境+直射漫反射是其主项 ✓
- **反推漫反射占比上界**：我实测晶体 prim 的 `w`（⇒ `metal`）分布为 `012_b_m: w mean 0.173 / p90 0.450`、`010_b_m: mean 0.303 / p90 0.765` ⇒ 若 `metal≈0.2`，则整体 −5.6% ⇒ **漫反射占总辐射 ≈ 5.6%/0.2 ≈ 25%（下界，因镜面增益已部分抵消）**；亮部（`>0.5`）损失 41–81% ⇒ **亮部漫反射占比 ≥ 50–80%** ✓
- **可证伪预测（A/B 可直接跑）**
  1. **若只补镜面侧（现状）**：`>0.5` 仍应停在 ~2%（≈ −40%）⇒ **若果然如此，即证明缺的是漫反射辐照、不是镜面** ✓
  2. **若补上"与直射同量级的辐照"**：`>0.5` 应回到 **≥ OFF 基线 3.394%**（不再是 1.995%），且 prim5 的 `>0.5` 应从 −80.6% 收敛到 **≥ −10%**；`p95` 应回到 **≥ 0.4865**
  3. **反例（预测失败）**：若补辐照后 `p50` 明显抬升（>+10%）或 `p95` 超过基线 5% 以上 ⇒ 补的辐照过强（与我们只有"直射 rig 灯"、源有完整 SH/天空预算的差异有关，需按源系数缩放 ✗ 而系数不可得 ⇒ 见 §4）
  4. **若在"保持漫反射不缩"下开 F0（方案 e）**：`>0.5` 不应下降（会双计能）⇒ 若下降，说明 F0 反而压低了输出（例如 `spec` 因子把 `0.079956` 缩放得过小）

## 4. 可实现方案（按代价排序）

| # | 方案 | 改动点 | 依赖的源证据 | 代价/风险 | 判定 |
|---|---|---|---|---|---|
| **a** | **保持源式 BRDF OFF（现状）**，直到辐照预算就位 | 无（默认 OFF 已实现 ✓） | `L564-578`/`L626-628`：源公式**预设**了环境预算 ⇒ 只接一半比现状**更不忠实** | 0 / 无 | **建议**（短期） |
| **b** | **接源 SH 系数**（`u_env_sh`/`u_ambient`/`u_char_ambient`/`u_env_day2night_exposure`） | 需先在注入链给 `getIBLIrradiance` 提供 SH 求值 | 位置全部已知：`cb1[148..154]`、`cb1[0]`、`cb1[284]`、`cb1[239]`（§2.2 ✓） | — | **当前不能补** ✗：这些是**运行时 cbuffer 值**（引擎按场景/时段注入），**不在 c159/manifest/资产中** ⇒ `unresolved`（位置已给，等运行时抓取） |
| **c** | **用源资产重建辐照**：把**源 cube**（已绑定的 `qiangpi` 六面 / `t_custom_ibl`）交给 three 的 `getIBLIrradiance`（而不是中性 PMREM），即让 `envMap`/`scene.environment` 用源 cube 并放行 irradiance | `viewer.js L274/L296`（environment 来源）、`L1377/L1405`（`envMapIntensity` 门闸）、注入侧需**不再只改名 radiance** | 源侧**确用环境 cube**（`t_realtime_env_spec` t8 / `t_env_spec_array` t6 ✓）+ 源用 SH 近似同一环境（`u_env_sh` ✓） | 中 / 风险：可能整体提亮或变灰（SH 的 albedo/曝光缩放未知） | **可做，但必须标"重建近似（非源值）"** ✓ 建议先做 1110171（`w` 小、幅度小）A/B，观察 `p50` 是否漂移 |
| **d** | 手填环境常数/增益 | — | **无源依据** | — | **不能补** ✗（禁止为了好看造项） |
| **e** | 只接 F0 不缩漫反射（保亮） | 注入侧去掉 `diffuse *= (1−metal)` | 与源 `L548 albedo×(1−metal)` **冲突** | 低 / 双计能 | **不建议**（会双计能量，且不忠实 ✗）；仅在"必须保住亮部"时作为**对照实验** |
| **f** | 抓运行时 cbuffer（b 的前置） | 注入游戏进程 | 位置：`cb1[0]/[86]/[148..154]/[239]/[284]` | 高 / 越界 | **本任务不涉及**（Lead 已禁注入）；如要，需 Lead 另开 |

**⇒ 推荐路径**：短期 (a) 保持 OFF → 中期 **(c) 用源 cube 重建辐照并明确标注"重建"** → 长期 (b) 若能取得运行时 SH 值则替换为源值 ✓

## 5. 与 task-45 的关系：环境项占比小 = 源本身如此，还是我们丢失？

**分两半回答（有证据）**：
1. **镜面侧的小占比，部分源本身如此** ✓：`u_env_intensity` / `u_ambient_range` 在该族 **15/15 `[unused]`** ✓ ⇒ 这类"环境强度旋钮"在该 shader 家族**根本没被使用** ⇒ 接上 `u_cube_brightness`/`u_rotate_angle` 只有 ±0.5–2.7% 属**预期** ✓
2. **漫反射侧的小占比，是我们链丢失** ✗：源的**漫反射环境预算**来自 `u_env_sh`(9/15) + `t_realtime_env_spec`(t8) × `u_ambient`×`u_char_ambient`（L564-578 / L626-628 ✓），**本链一项都没有** ⇒ 我们看到的"环境贡献小"里，**漫反射那一大块是缺失，不是天然小** ✓✓

## 6. unresolved + 已排除

**unresolved（都不猜）**
| id | 项 | 为什么不可得 |
|---|---|---|
| U1 | `u_env_sh` 的实际 SH 系数（cb1[148..154]） | 运行时 cbuffer（引擎按场景/时段注入），c159/manifest/资产中均无 ✓ 位置已给 |
| U2 | `u_ambient`(cb1[0]) / `u_char_ambient`(cb1[284]) / `u_env_day2night_exposure`(cb1[239]) 的数值 | 同上 |
| U3 | `u_lightmap_factor`(cb1[86]) 与 shadow/lightmap 分支（`L630-640`）的实际启用状态 | 运行时分支条件（`cb1[20].w`/`v6.w`）不可得 |
| U4 | `t_realtime_env_spec`(t8) 与 `t_env_spec_array`(t6) 在**该皮肤**是否真的有内容（绑定 2–3/15 变体） | 需运行时探针（shader-auditor 在跑） |
| U5 | 1110171/1110177 实际命中的 quality 变体是哪个（15 个 PS 中 9 个用 SH、6 个 `[unused]`） | 需运行时看实际编译的 program（我只有静态 15 变体） |
**已排除**
- **VLM/体素光图**：`u_vlm_*` 全 19 个在 **15/15 变体 `[unused]`** ⇒ 不是本族缺项 ✓
- `u_env_intensity` / `u_ambient_range`：15/15 `[unused]` ⇒ 不是可用的补偿旋钮 ✓
- `uIblScale` 0.25→1.0：已证非偏暗主因（p95 仅 +4.1%）✓
- "只是 F0 没接"：本诊断证明缺的是**漫反射辐照**（`>0.5 −41%` 与 `p50` 不动同时出现，只有漫反射被抽走才解释得通）✓

## 7. 复核命令
```
venv\Scripts\python.exe %TEMP%\RXEB_census.py    # 15 个 crystal PS 的环境/光图系数普查（[unused] 状态）→ RXEB_census.txt
venv\Scripts\python.exe %TEMP%\RXEB2.py          # 逐系数 offset + 使用点行号 → RXEB_detail.json
venv\Scripts\python.exe %TEMP%\rxeb3.py          # 代表变体 SH 累加窗（L558-585）与 lightmap 窗（L620-640）
```
> 反汇编路径更正：task 正文写的 `03拆包产物/render_1003_010/_disasm/cand/*.asm` ✓（`_target_1110171/cand/` 为空，上一轮已反馈）。
