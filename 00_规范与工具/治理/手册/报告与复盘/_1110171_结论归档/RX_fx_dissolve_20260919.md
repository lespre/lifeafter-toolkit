# RX_fx_dissolve：dissolve 的两个开口补完 + `u_dissolve_amount` 逐节点源值表

> **文件名（本轮的交付）**：`03拆包产物\_target_1110171\RX_fx_dissolve_20260919.md`（单文件；上一份 `RX_fx_family_extra_*` 与 `RX_fx_models_spec_*` 均**未改动**）。**只读**、未起浏览器。
> 证据文件（可复核）：`_target_1110171/fx_family/9053b046_7c6dc86e_d11_blob1.dxbc.asm`（PS）· `1110177/sfx/fx_skin_2003_029_{hit,jisha}.sfx`

---

## 1. `base`（L384 里的 `r2.w`）完整溯源 —— **= 主贴图 `Tex0` 的 alpha**

**寄存器链（全部行号 = 上面的 PS 反汇编）**
```
L302  add  r0.zw, v0.yyyx, l(0,0,-0.5,-0.5)      ; uv 以 0.5 为中心（旋转基准）
L335  mul  r0.y, cb0[10].x, l(0.017453)          ; 角度→弧度（t1 的旋转角）
L336  sincos r4.x, r5.x, r0.y                    ; 旋转
L337  mul  r2.zw, r0.zzzw, r4.xxxx               ; ┐ 旋转后的 uv（写的是 r2.zw ⇒ 这里 r2 只是 UV 暂存）
L338-339 mad（sin/cos 组合）
L340  add  r2.zw, r4.xxxy, l(0,0,0.5,0.5)        ; 回到 0..1
L341  mul  r4.xy, cb0[9].zwzz, cb1[87].yyyy      ; speed × 时间（cb1[87].y = 引擎时间）
L342  mad  r2.zw, r2.zzzw, cb0[8].zzzw, r4.xxxy  ; × tilling + speed 项
L343  add  r2.zw, r2.zzzw, cb0[9].xxxy           ; + offset
L344  mad  r2.xy, r2.xyxx, cb0[10].zzzz, r2.zwzz ; 与原始 uv 混合
L345-347   clamp(0.01..0.99) 后取差值
L348  mad  r2.xy, cb0[4].xyxx, r2.zwzz, r2.xyxx  ; 视差/扰动位移
L349  add  r2.xy, r2.xyxx, v2.zwzz               ; + 顶点传入的 uv
L350  sample_indexable(texture2d) r2.xyzw, r2.xyxx, t1.xyzw, s0   ; ★★ t1 采样，**四个分量全部被覆盖**
...
L383  add  r0.z, -r0.y, r2.w                     ; 这里的 r2.w 就是 L350 的 t1.alpha
L384  mad  r0.y, cb0[16].y, r0.z, r0.y           ; mask' = mask + u_dissolve_opacitymix·(t1.a − mask)
```
**纹理绑定表（同一 asm 头部）**：`t0 = t_distort_tex1` · **`t1 = Tex0`** · `t2 = t_mask01` · `t3 = t_dissolve_tex` · `s0 = s_fresnel_normalmap`
**⇒ 结论**：**`base` = 主贴图 `Tex0`（t1）采样结果的 alpha 通道** ✓（**不是**顶点色、**不是** `u_base_color`、也不是别的插值；L337-347 对 `r2.zw` 的写入只是**采样前的 UV 暂存**，L350 用整寄存器覆盖 ✓）
**⇒ 实现含义**：`u_dissolve_opacitymix` 的混合基准 = **主贴图 alpha**（无需顶点色/顶点属性）✓ —— 这条让 dissolve 可在 three 侧直接用基色图的 alpha 复现 ✓

## 2. `u_dissolve_rotation` 与 dirmask —— 窗口已定位；dirmask **不在可用变体里**

### 2.1 rotation（在）：`u_dissolve_rotation` = **cb0[18].w（offset 300）**
（★ **更正**我在 `RX_fx_family_extra` 里按 offset 推断写的 `.z`：成员表 `off=300 u_dissolve_rotation`（声明 L65）⇒ cb0[18].w ✓）
```
L355-359  （前置：掩码/反相的选择链）
L360  mul  r0.y, cb0[18].w, l(0.017453)      ; ★ u_dissolve_rotation 角度→弧度
L361  sincos r1.x, r4.x, r0.y                ; 旋转
L362-364  mad（sin/cos 旋转 uv）
L365  add  r0.yz, r5.xxyx, l(0,0.5,0.5,0)    ; 居中
L366  mul  r1.xw, cb0[18].yyyz, cb1[87].yyyy ; ★ u_dissolvetex_speed_x/.y × 时间
L367  mad  r0.yz, r0.yyzy, cb0[17].yyzy, r1.xxwx  ; × u_dissolvetex_tilling_y（及另一分量）
L368  add  r4.x, r0.y, cb0[17].w             ; + u_dissolvetex_offset_x
L369  add  r4.y, r0.z, cb0[18].x             ; + u_dissolvetex_offset_y
L370-372   clamp(0.01..0.99)
L373  mad  r0.yz, cb0[5].xxyx, r0.yyzy, r4.xxyx   ; 视差/扰动
L374  ne   r0.w, cb0[15].y, l(0)             ; 开关（u_dissolve_distort / cb0[15].y）
L375-376   and/add ⇒ 最终溶解 UV
L377  sample_indexable(texture2d) r0.yz, r0.yzyy, t3.yxwz, s0   ; ★ t3 = t_dissolve_tex
```
**⇒ 溶解 UV 窗口 = `L355-392`**（含 rotation/speed/tilling/offset/clamp/distort 到采样与阈值判定）✓

### 2.2 dirmask（**不在本变体**）
- `u_dissolve_dirmask_channel`（cb0[19].y，off 308）与 `u_dissolve_dirmask_pixel_size`（cb0[19].z，off 312）在本变体**0 引用** ✗
- 整个 PS 只有 **4 条 sample**：`t0 = t_distort_tex1`(L312) · `t2 = t_mask01`(L322) · `t1 = Tex0`(L350) · `t3 = t_dissolve_tex`(L377) ⇒ **没有 dirmask 贴图** ✗
- 与 c159 的宏名对照：`USE_DISSOLVE_DIR_PIXELATE_UV` / `USE_DISSOLVE_DIR_POLAR_UV` / `USE_DISSOLVE_DIR_ROTATION_UV` / `USE_DISSOLVE_DIR` 等均为**独立编译变体**；运行时缓存该族目录里**只有 2 个 pipe**（`9053b046_7c6dc86e` / `d8673b60_7c6dc86e`），**都不含 dirmask 路径** ✗
**⇒ 结论**：**dirmask 分支 = unresolved**（需一个带 `USE_DISSOLVE_DIR*` 宏的编译变体；本机缓存当前没有）✓ —— 已有的是 **rotation + speed + tilling/offset + distort** 这条主路径 ✓
**关系总结**：`u_dissolvetex_channel`(cb0[17].x) 选 `t3` 的通道（L378-379）· `u_dissolve_tex_anti`(cb0[19].x) 决定是否反相（L380-382）· `u_dissolve_dir_length`(cb0[19].w) 只出现在阈值偏移项 `θ = amount·(dir_length+1) − 1`（L386-387）✓ —— **三者互不依赖**，dirmask 那组参数（cb0[19].y/.z）在本变体完全不参与 ✓

## 3. `u_dissolve_amount` 逐节点源值表（12 个组件）

| # | sfx | 组件行 | `u_dissolve_amount` 关键帧 | 配对节点（推断） | 节点 TM |
|---|---|---|---|---|---|
| 1 | hit | L571 | `t0=0.6 · t0.5413=0.6 · t1=1` | **未配对**（在首个节点之前） | — |
| 2 | hit | L2078 | `t0=0.65 · t0.6992=0.65 · t1=0.65` | Model `M_模型核心电小_4`（`mz_shandian03`） | 5 |
| 3 | hit | L2259 | `t0=0.65 · t0.4565=0.65 · t1=1` | Model `H_模型核心电小_5`（`mz_shandian02`） | 2 |
| 4 | hit | L2414 | `t0.5=0.4`（单帧） | ParticleSystem `H_鬼火_射线_02` | — |
| 5 | hit | L3201 | `0=0.6 · 0.4645=0.62 · 0.6488=0.695 · 1=1` | ParticleSystem `H_p_星点_02` | — |
| 6 | jisha | L1786 | `0=0 · 0.6947=0.9875 · 1=1` | ParticleSystem `H_鬼火_lizi_1` | — |
| 7 | jisha | L4689 | `0=0.7 · 0.8137=0.7 · 0.8824=0.7487 · 0.9557=0.8162 · 1=1` | Model `M_模型气流升_1_1_1`（`jisha_qiliu_01`） | 5 |
| 8 | jisha | L5093 | `0=0 · 0.6321=0 · 1=1` | Model `L_模型特效_1`（`dm_qiliu_06`） | 2 |
| 9 | jisha | L5261 | `0=0 · 0.5008=0 · 1=1` | Model `M_mod_地裂流光_1_1`（`sandian_02_hjl`） | 5 |
| 10 | jisha | L5347 | `0.5=0`（单帧） | Model `M_模型_金线1`（`bp_baoci_hgz01_02`） | 0 |
| 11 | jisha | L6253 | `0=0 · 1=1` | Model `H_模型特效_3`（`dm_shangdian_07`） | 0 |
| 12 | jisha | L6337 | `0=0 · 1=1` | **未配对**（在末节点之后） | — |

**覆盖度（回答"哪些完整、哪些只有 amount"）**：**这 12 个组件全都只声明 `u_dissolve_amount` 一项** ✓ —— `u_dissolve_smooth` / `u_dissolve_edgewidth` / `u_dissolve_opacitymix` / `u_dissolve_tex_anti` / `u_dissolve_dir_length` / `u_dissolve_rotation` / `u_dissolvetex_*` **在两文件里都没有任何逐节点声明** ✗ ⇒ 它们一律取**引擎默认值**（静态不可得 ✓ 与上一轮结论一致 ✓）⇒ 实现时按"省略 + `omitted_undeclared`"处理 ✓
**带 dissolve 的 Model 节点 = 7 个**（hit 2 + jisha 5）；另 3 个 ParticleSystem 也带（ParticleSystem 不在 Model 分支内，仅登记 ✓）
**⇒ chain-auditor 可直接用的最小式**：`mask = t_dissolve_tex 通道（默认取 .x/.y 由 channel 参数，未知则取 .r）` → `θ = amount·(dir_length+1) − 1`（`dir_length` 无源值 ⇒ 省略 ⇒ **θ = amount − 1**）→ `t = saturate(mask − θ)`（smooth 无源值 ⇒ 省略分母）→ `alpha *= t²(3−2t)`；**`opacitymix` 无源值 ⇒ 省略（= 不做基色 alpha 混合）** ✓

## 4. ★ 一处必须转达的解析更正（影响 chain-auditor 手上的表）

我此前交付的 `RX_fx_models_spec.json` 的**逐节点 `name` 字段有污染** ✗：该解析对节点块取的是 **块内最后一个 `Name=`**，而后面的嵌套元素（uniform/子节点）也带 `Name=` ⇒ 表里出现的 `u_dissolve_amount`/`USE_EMISSIVE_CONTROL`/`u_depth_bias` 等"节点名"是**错的**。
**已在本轮修正**（只取 `<Tag ...>` 头部到第一个 `>` 的属性 ✓）：正确节点名如 `M_模型核心电小_4` / `H_鬼火_lizi_1` / `M_mod_地裂流光_1_1` 等 ✓（本文件 §3 的表就是修正后的 ✓）。
⚠ **`ModelName` / `TransparentMode` / `RenderBias` / `FxLifeSpan` 四列受影响较小**（属性名在块内基本唯一），但**建议 chain-auditor 以本轮 §3 的名称与 `_target_1110171/fx_family/` 的 asm 为准**，或让我再出一份完整修正表 ✓

## 5. 复核命令
```
venv\Scripts\python.exe %TEMP%\RXDS1.py   # r2.w 写点 + 源链回溯 + 输入签名 + 控制流
venv\Scripts\python.exe %TEMP%\RXDS3.py   # PS 纹理绑定 + 逐节点 dissolve（早期版本，名称列有污染）
venv\Scripts\python.exe %TEMP%\RXDS5.py   # ★ 修正后的逐节点表（只取头部属性）→ RXDS5.json
（反汇编：fxc /dumpbin /Fc out.asm blob.dxbc，blob 来自 runtime effect_cache 的 uber_fx_common.nfx2\*.pipe）
```
