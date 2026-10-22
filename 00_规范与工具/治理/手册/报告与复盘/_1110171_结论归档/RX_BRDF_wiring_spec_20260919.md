# RX_BRDF_wiring_spec：晶体 BRDF 源值接线规格（task-54 → 供 task-47 照抄实现）

> **只读**产出（未改 viewer.js / manifest / board / 注册表）。证据来自 DXBC 反汇编 + manifest `crystal_params`。
> **靶子**：`assets\weapon_skin_viewer.js` 实测 sha16 **`75784198127282DC`**（324,568 B）——⚠ **与 Lead 给的 `641DDC2CBA6FFEC4` 不同**（shader-auditor 正在改），本文所有 viewer 行号以 **`75784198127282DC`** 为准。
> 反汇编代表文件：`03拆包产物\render_1003_010\_disasm\cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm`（PS · d11_deferred_quality2_shader_pbr_crystal）；变体对照 `2490ff82_…`、`598c3c59_e852d979_…`。
> 结构化版：同目录 `RX_BRDF_wiring_spec.json`（含逐 prim 值表、`w` 输入分布、可证伪预测、unresolved）。

---

## 1. metalness 插值式（确切行号 + `w` 完整求值链）—— **已复核，闭环**

### 1.1 公式与来源行（代表变体）

```
L443   add     r4.w, -cb0[319].w, cb0[320].x        ; u_crystal_metallic − u_base_metallic
L444   mad_sat r4.w, r1.w, r4.w, cb0[319].w         ; ★ metal = saturate(lerp(u_base_metallic, u_crystal_metallic, w))
```
⇒ **`metal = saturate(lerp(u_base_metallic, u_crystal_metallic, w))`** ✓（`r1.w` 即 `w`；`mad_sat` 自带 saturate ✓）
**同批还给出 specular 与 F0 两条**（见 §2），三条共享同一个 `w` ✓。

### 1.2 `w` 的完整求值链（逐步行号 + 寄存器）

```
L392   sample_b_indexable(texture2d)(...) r6.xyzw, v0.xyxx, t0.xyzw, s1, l(-1.000000)   ; t0 = Tex0(b_m)
L393   mov_sat  r6.xyzw, r6.xyzw                                                        ; m = saturate(Tex0)
L396   add      r8.xy, v0.xyxx, cb0[317].xyxx                                          ; uv + (u_detail_offset_x, u_detail_offset_y)
L397   mul      r8.xy, r8.xyxx, cb0[316].wwww                                          ; × u_detail_tilling
L398   sample_indexable(texture2d)(...) r8.xyzw, r8.xyxx, t2.xyzw, s3                  ; t2 = DetailMap
L405   mul      r8.xyzw, r6.xxxx, r8.xyzw                                               ; r8.w = m × DetailMap.a
L438   mul      r1.w, r6.x, r8.w                                                        ; ★ w = m² × DetailMap.a
```
- **`r1.w` 在整文件只有一个写点（L438），且不在任何 `if/else` 内** ⇒ 无多分支歧义 ✓
- 8 个读点中，**只有 L442（spec）与 L444（metal）是"权重"语义**；`L466 mad r1.xyz, r1.xyzx, r1.wwww, r9.xyzx` 用的是**caustic 的 alpha**（同寄存器复用）⇒ **实现时不要把 L466 当权重** ✓
- 本项目 `crystal_bump_n_uvva.png` 实测 **A ≡ 1.000** ⇒ **`w = m²`**（`m = saturate(Tex0.r)`）✓
- **变体一致性**：`2490ff82…`（L434 + 同形链 L388/389/392/393/394/401）、`598c3c59_e852d979…`（L337 先 `r7 *= m`、L369 权重）三变体**语义一致**；但 **cbuffer 槽位逐变体不同**（代表 `cb0[319].w/320.x`；另一族 `cb0[10].w/11`；`e852d979` 族 `cb0[137]`）⇒ **必须按名绑定，禁止硬编偏移** ✓

## 2. specular / F0（含 0.079956 的 raw hex 与常量位置）

### 2.1 specular 插值式
```
L441   add r3.w, -cb0[320].y, cb0[320].z    ; u_crystal_specular − u_base_specular
L442   mad r3.w, r1.w, r3.w, cb0[320].y     ; ★ spec = lerp(u_base_specular, u_crystal_specular, w)
```

### 2.2 字面量 `0.079956`
- 出现行：**`L549 mul r8.w, r3.w, l(0.079956)`**、**`L550 mad r11.xyz, -r3.wwww, l(0.079956,0.079956,0.079956,0.000000), r1.xyzx`** ⇒ **`F0_diel = spec × 0.079956`** ✓
- **raw hex（IEEE754 single）**：LE **`f9bfa33d`** / BE **`3da3bff9`**（注意：**0.04 = `0ad7233d`，不是本字面量**）
- **常量位置（字节偏移，可复核）**：pipe `d11_deferred_quality2_shader_pbr_crystal.nfx2_03e9e23d_b2d62c97_d11.pipe`（59,860 B）中该 4 字节模式出现 4 次 @ 文件偏移 **42528 / 42560 / 42564 / 42568**；DXBC 容器起于文件偏移 **48** ⇒ **DXBC 相对偏移 42480 / 42512 / 42516 / 42520**（chunk 标签 `ISGN/OSGN/RDEF/SHEX/STAT`）✓；对照：deferred 变体 `598c3c59_e852d979` 的 pipe 中该字面量出现 **0 次** ✓

### 2.3 F0 最终组合（**关键**，决定怎么接线）
```
L547   add r6.z, -r4.w, l(1.000000)                  ; (1 − metal)
L548   mul r10.xyz, r1.xyzx, r6.zzzz                 ; albedo × (1 − metal)  ← 漫反射权重
L550   mad r11.xyz, -r3.wwww, l(0.079956,…), r1.xyzx ; albedo − spec·0.079956
L551   mad r11.xyz, r4.wwww, r11.xyzx, r8.wwww       ; ★ F0 = lerp(F0_diel, albedo, metal)
```
⇒ **`F0 = lerp(spec·0.079956, albedo, metal)`**，且 **`diffuse = albedo × (1 − metal)`** ✓✓
⇒ **这与 three `MeshStandardMaterial` 的金属工作流同构**（`F0 = mix(vec3(dielectricF0), diffuseColor, metalness)`；`diffuseColor *= 1 − metalness`）——
⇒ **2026-09-15「不得把 u_crystal_metallic 映射到 three metalness」的旧结论**（viewer `L2606-2612` 注释）担忧的"映射后 albedo 不参与着色"**恰恰被 L548 的 `(1−metal)` 权重覆盖** ⇒ **该禁令可在本证据下重估** ✓（这只是证据陈述，最终决定权在 Lead/shader-auditor）。

### 2.4 three 侧如何等价表达（最小实现）
| 通道 | 结论 |
|---|---|
| **metalness** | **有等价通道**：直接 `material.metalness = saturate(lerp(u_base_metallic, u_crystal_metallic, w))`（three 的 `diffuse×(1−metal)` 与 `L548` 同构 ✓；晶体路径已支持 `cfg.metalness`：viewer `L2612`） |
| **specular/F0 的 `spec` 因子** | **three 无独立通道**（`specularColor` 来自 `0.16·reflectivity²` + albedo mix）⇒ 按三种方案：<br>① **已有 patch**（viewer `L1475` 原串 → `L1476` 替换串）已把 `vec3(0.04)` 改成 `vec3(0.079956)` —— **但缺 `spec` 因子**（源是 `spec×0.079956`）；<br>② **最小注入（推荐）**：把 `L1476` 的替换串改为<br>`material.specularColor = mix( vec3( 0.079956 * uSpecFactor ), diffuseColor.rgb, metalnessFactor );`<br>其中 `uSpecFactor = lerp(u_base_specular, u_crystal_specular, w)`；<br>③ 等价 reflectivity（仅在无金属混合、纯介电时成立）：`reflectivity = sqrt(F0/0.16)`，对 `F0=0.079956` ⇒ **`reflectivity = 0.70691`**（本地 three 为压缩单行构建 `assets\vendor\three\three.module.min.js`，故只给数值关系、不给行号） |
| 注入位置 | 现有 patch 已精确匹配 `material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );` 这一行 GLSL（viewer `L1475`）⇒ 实现只需改这一串 ✓（`L1473` 已注明不会误伤 clearcoat 的 `vec3(0.04)`） |

## 3. 逐皮肤 / 逐 prim 可用值表（BRDF 四值）

| 皮肤 | prim | 材质 | `u_base_metallic` | `u_crystal_metallic` | `u_base_specular` | `u_crystal_specular` | BRDF 可接线性 |
|---|---|---|---|---|---|---|---|
| 1110171 | 1 | skin_1003_012_1 | **缺失** | 1.0 | **缺失** | 1.0 | 2/4 |
| 1110171 | 2 | skin_1003_012_2 | **缺失** | 1.0 | **缺失** | 1.0 | 2/4 |
| 1110171 | 3 | skin_1003_012_3 | **缺失** | **0.75** | **缺失** | 1.0 | 2/4 |
| 1110171 | 5 | skin_1003_010_1 | **缺失** | 1.0 | **缺失** | 1.0 | 2/4 |
| 1110171 | 6 | skin_1003_010_2 | **缺失** | **0.75** | **缺失** | 1.0 | 2/4 |
| 1110177 | 1 | skin_2003_029_1 | **0.6** | **0.95** | **缺失** | 1 | 3/4 |
| 1110177 | 2 | skin_2003_029_2 | **缺失** | 1 | **1** | 1 | 3/4 |

**规则（按 Lead 要求执行）**：**缺失项一律不覆盖、不跨皮肤借值** ⇒ 落地式只能是
`metal = saturate(lerp(<该 prim 现值>, u_crystal_metallic, w))` / `spec = lerp(<该 prim 现值>, u_crystal_specular, w)`
（`<该 prim 现值>` = 现有链的值；**源侧"引擎默认端点值"未定证 ⇒ 见 unresolved U1**）
（数据源：各 manifest `crystal_params`；provenance 指向 `03拆包产物\_known_loop\c159_params_001265.json` ✓）

## 4. 与现行链的差异方向 + 风险

**现行（sha `75784198127282DC`）**：weapon 链 `metalness: 1.0`（`L1331`）· 晶体链 `metalness: 0.0`（`L1359`）· 晶体另有 `cfg.metalness` 通路（`L2612`，缺省 0）· `crystal_params` 注入点在 `L1525`。
**接线后方向**（按 `w` 的实测分布，见 §5）：

| 皮肤/prim | `w` 输入（`Tex0.r` 的 m 分布 ⇒ w=m²） | 预期 metalness 落点 | 方向 |
|---|---|---|---|
| 1110171 prim1/2/3（`012_b_m`） | m: mean 0.352 / p50 0.337 / p90 0.671；**w=m²: mean 0.173 / p90 0.450 / w>0.5 仅 4.0%** | ≈0.17（大面）～0.45（亮部） | **温和抬升**；亮点区更多镜面 |
| 1110171 prim5/6（`010_b_m`） | m: mean 0.472 / p90 0.875；**w: mean 0.303 / p90 0.765 / >0.5 占 26.5%** | ≈0.30 ～ 0.77 | **中等抬升** |
| **1110177 prim1/2（`029_b_m`）** | m: mean **0.826** / p50 0.898；**w: mean 0.724 / p90 1.000 / >0.5 占 77.2%** | ≈0.72 ～ 0.95（`u_crystal_metallic` 0.95/1.0） | **大幅抬升**（几乎整面金属化） |

**风险（必须预告）**
1. **无 IBL 的 prim 抬 metalness 会变黑** ✗：金属的 diffuse=0，若 `envMap/uCustomIbl` 未就绪（窗口期 `ibl_pending`）则只剩直射高光 ⇒ 整体变暗。**接线必须与 IBL 就绪同批**，或对 `ibl_pending` 的 prim **强制 metalness=0** ✓
2. **1110177 的 `w` 均值 0.72 ⇒ 抬升幅度大** ⇒ 风险最高，建议**先接 1110171（w 小、风险低）做 A/B，再上 1110177** ✓
3. **1110177 prim1 的 `DetailMap` 未解析**（`crystal_bump_n02.tga` / null）⇒ `w` **算不出来** ⇒ **该 prim 不可接线**（除非改为 `w=m²`，但那需要 `D.a≡1` 的前提——该资源缺失，无法验证 ✗）✓
4. **`spec` 因子注入会同时改 F0 与 IBL 高光强度** ⇒ 若 `u_base_specular` 缺失而按"保留现值"处理，实际是 `lerp(现值, 1, w)`；**现值必须来自同 prim 数据，不能借** ✓

## 5. 可证伪预测（接线正确的判据；供做完对照）

以 MASK 口径（`criterion=mask/weapon_box`）五读数：
| 读数 | 预测方向 | 理由 | 反例（=接线未生效/有误） |
|---|---|---|---|
| `p50` | **基本不变或微升（±10%）** | 金属化压低 diffuse、抬升 specular，部分抵消 | p50 明显下降 ⇒ metalness 抬升而 IBL 未就绪 |
| `p95` | **上升** | F0→albedo 的高反射 + IBL 高光 | 不升 ⇒ `w` 退化（Tex0/DetailMap 未绑 ⇒ m=0/1 两极） |
| `>0.5` | **上升** | 同上 | — |
| `>0.75` | **明显上升**（1110177 目标 4.68%，当前 0.989%；1110171 当前 0.273%） | 金属镜面高光集中在高亮区 | 不升或下降 ⇒ 接线错（或 `spec` 因子把 F0 压低） |
| 暖色% | **上升**（P1 3.01%；1110177 当前 0.689%） | 高光带上 albedo 的暖色 | 下降 ⇒ F0 走错（如把 `diffuseColor.rgb` 换成了冷色常量） |

**额外自检（零成本）**：`viewer` 自报探针 `L2256 f0: ((metal>=0.999)?'baseColor(metal)':'0.04(dielectric)')` —— 接线后晶体 prim 应显示 `baseColor(metal)`（因为 `u_crystal_metallic≈1` 且 `w` 高），若仍显示 `0.04(dielectric)` ⇒ 未接通 ✓
**顺序建议**：先接 1110171（`w`≈0.17–0.30，风险低）→ 观察五读数 → 再上 1110177（`w`≈0.72，风险高）✓

## 6. unresolved（不猜）+ 已排除

| id | 未定项 | 说明 |
|---|---|---|
| U1 | **PRIM 缺失声明的端点，源侧取什么值**（引擎默认/材质默认） | 未在 c159/反汇编中定证 ⇒ **一律不覆盖、不借值**；落地式只能"保留现值" |
| U2 | 1110177 prim1 的 `DetailMap` 未解析 ⇒ `w` 不可算 | 该 prim 不接线（除 `w=m²`，但那需 `D.a≡1`，资源缺失无法验证） |
| U3 | 宏开关 / 运行时 cbuffer 覆盖 | 不同 quality 变体槽位不同（`cb0[319/320]` vs `cb0[10/11]` vs `cb0[137]`）⇒ **按名绑定**；宏分支是否启用未定证 |
| U4 | three 的 `specularColor` 在 IBL 路径下是否与源"金属 F0=albedo"完全等价 | 源侧未见 clearcoat/二次 F0 项；three 的 IBL 用 `specularColor` 直接做 F0 ⇒ 形式一致但未做逐像素对照 |
| U5 | `u_base_specular`/`u_base_metallic` 缺失是否**真的**意味着"引擎不给该覆写"（而非 c159 解析漏项） | 本轮只核 manifest `crystal_params`；未回溯 c159 原始块 |
**已排除**：`uIblScale 0.25→1.0`（已证非偏暗主因，p95 仅 +4.1%）· 直接把 `u_crystal_metallic` 当常量 metalness（缺 `w`）· 只做 `0.04→0.079956` 的既有 patch（缺 `spec` 因子）· 把 `u_crystal_metallic` 映射到 `attenuationColor`（无源依据，viewer `L2620-2622` 已撤销）

## 7. 复核命令 / 文件
```
# 值表与 w 分布
venv\Scripts\python.exe %TEMP%\RXBRDF_json.py     # → RX_BRDF_wiring_spec.json
venv\Scripts\python.exe %TEMP%\RXBRDF_w.py        # → 追加 w 分布 + verdict 聚焦 BRDF 四值
# 反汇编取证
venv\Scripts\python.exe %TEMP%\RXBRDF_recon.py    # → 0.079956 hex/偏移 + three 侧 F0 + viewer 现行行
```
