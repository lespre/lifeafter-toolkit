# RX_CRYSTAL 源公式（DXBC 反汇编级证据）— 1110171 / 1110177 晶体四层

> 只读产出。**靶子**：`assets\weapon_skin_viewer.js` sha16 **`113692F0F38362C4`**（本文引用 viewer 行号只对该版有效）。
> **反汇编来源与入口（本轮实际路径）**
> 1. 管线 DXBC 容器：`03拆包产物\render_1003_010\_game_shader_db\pipes\*.pipe`（共 **1036** 支；其中管道名含 `pbr_crystal` 的 **13 种**、文件 **578** 支）。样例 `d11_deferred_quality2_shader_pbr_crystal.nfx2_985fea6c_b2d62c97_d11.pipe` 偏移 40 处即 `DXBC` 容器（含 SHEX/RDEF 等 5 个 chunk）。
> 2. 既有反汇编树（fxc 风格、**带 cbuffer 成员名+Offset+[unused] 标记**）：`03拆包产物\render_1003_010\_disasm\**\*.asm`（**968** 个；归属 `pbr_crystal` 管道 **30** 个 = PS 15 + VS 15）。
> 3. **代表文件（本文所有行号以此为准）**：`_disasm\cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm`
>    —— PS · `shader=d11_deferred_quality2_shader_pbr_crystal` · 22 个 c159 uniform 中 20 个有指令体引用 · 14 条采样指令。
> 4. 交叉核对：**15/15 个 crystal PS 变体的层纹理绑定/采样形态一致**（见 §6）。
> 工具：`%TEMP%\RXFORM_census.py`（全量普查）· `RXFORM_trace.py` / `RXFORM3.py` / `RXFORM4.py`（数据流追踪）· `RXFORM5.py`（声明名与族静态推导）。

## 0. ★ 先给结论（对 task-43 直接可用）

| 项 | 结论 | 证据强度 |
|---|---|---|
| 全部 14 个晶体 uniform 在**源 shader 里真的被消费** | ✓ 每个都在 15/15 个 PS 里被引用（明细 §1） | **强**（指令体引用计数） |
| caustic：tilling / depth / brightness 语义 | tilling=**UV 乘**；depth=**视差偏移标量**；brightness=**乘性增益**；整层以 **`×caustic.a` 加项**混入基色 | **强**（L461-466） |
| refraction：rotation / contrast / brightness / color | rotation=**角度×2π**、驱动**方向旋转 + 角度→UV 球面映射**；contrast=**线性 remap + saturate**；brightness/color=**乘性** | **强**（L471-527） |
| `t_reflection_tex` | **源侧不采样**（15/15 PS 未绑定、无 sample） | **强**（15 文件一致） |
| detail：tilling / intensity / offset_x,y | uv=`(uv0+offset)×tilling`；intensity 重定标 xy（±1 clamp）与 z（`1+I·(z-1)`）；结果再乘 `m=saturate(Tex0.r)` | **强**（L396-405）；**分量到 `d` 的最终去向 = 部分待闭环** |
| specular / metallic 的源公式 | `specular=lerp(u_base_specular,u_crystal_specular,w)`（L441-442）· `metallic=lerp(u_base_metallic,u_crystal_metallic,w)`（L443） | **强** |
| `u_rotate_angle` | 代表变体**未声明**（仅 6/15 变体有，off=160）⇒ 消费点 **unresolved** | 弱（见 §5） |
| **新增发现** | `cb0[322].x = u_refraction_mipmap`（采样 LOD）、`cb0[322].z = u_refraction_opacity` —— **Lead 清单里没有这两个名字** | **强**（cbuffer 成员表） |

## 1. c159 uniform → cbuffer 槽位（`NeoxUBOLocal` = cb0）与消费计数

| uniform | 槽位 | 15 个 PS 中引用数 | 指令体引用合计 |
|---|---|---|---|
| u_detail_tilling | cb0[316].w | 15 | 72 |
| u_detail_offset_x / _y | cb0[317].x / .y | 15 / 15 | 60 / 63 |
| u_detail_intensity | cb0[317].z | 15 | 63 |
| u_base_metallic | cb0[319].w | 15 | 90 |
| u_crystal_metallic | cb0[320].x | 15 | 79 |
| u_base_specular | cb0[320].y | 15 | 82 |
| u_crystal_specular | cb0[320].z | 15 | 74 |
| u_caustic_tilling | cb0[320].w | 15 | 76 |
| u_caustic_depth | cb0[321].x | 15 | 82 |
| u_caustic_brightness | cb0[321].y | 15 | 86 |
| u_refraction_rotation | cb0[321].z | 15 | 91 |
| u_refraction_contrast | cb0[321].w | 15 | 93 |
| **u_refraction_mipmap**（新） | cb0[322].x | 15 | （采样 LOD 操作数） |
| u_refraction_brightness | cb0[322].y | 15 | 59 |
| **u_refraction_opacity**（新） | cb0[322].z | 15 | （L1123 一处） |
| u_base_color | cb0[184] | 15 | 30 |
| u_crystal_color | cb0[185] | 15 | 25 |
| u_refraction_color | cb0[186] | 15 | 15 |
| u_subsurface_color | cb0[187] | 15 | 15 |
| u_emissive_strength / _fresnel | cb0[318].x / .y | 3 / 3 | 13 / 14 |
| u_rotate_angle | off=160（归属待核） | 6 | 40 |

⇒ **没有任何一个是 `[unused]`**（15/15 PS 一致）—— 即 **viewer 链里"没消费"的这些量，源 shader 全部在用**（这正是 task-43 要接回来的部分）。

## 2. caustic 层（`t_caustic_tex` = t4，采样器 s2 名为 `s_reflection_tex`）

```
L461  mad   r1.x, r6.x, cb0[321].x, cb0[321].x     ; r1.x = u_caustic_depth × (r6.x + 1)
L462  mul   r1.xy, -r1.xxxx, r5.xyxx               ; × (−深度项)，r5.xy = 上方 dp3 得到的视差方向
L463  mad   r1.xy, v0.xyxx, cb0[320].wwww, r1.xyxx ; uv = v0.uv × u_caustic_tilling + 视差偏移
L464  sample_indexable(...) r1.xyz, r1.xyxx, t4.xyzw, s2
L465  mul   r1.xyz, r1.xyzx, cb0[321].yyyy         ; × u_caustic_brightness（乘性）
L466  mad   r1.xyz, r1.xyzx, r1.wwww, r9.xyzx      ; caustic.rgb × caustic.a + 基色累加器 r9
```
**公式**：`uv_c = uv0 · u_caustic_tilling + dir_parallax · (−u_caustic_depth·(r6.x+1))`；
`caustic = tex(t_caustic_tex, uv_c) × u_caustic_brightness`；`color += caustic.rgb × caustic.a`。
⇒ **tilling 是乘**、**depth 是视差偏移幅度（不是自发光/不是加项）**、**brightness 是乘性增益**、**混合方式是 alpha 加权加项**。

## 3. refraction 层（`t_refraction_tex` = t5，采样器 s5 = `s_refraction_tex`）

```
L471  mul    r6.z, cb0[321].z, l(6.283185)          ; u_refraction_rotation × 2π ⇒ 角度(弧度)
L472  sincos r8.x, r9.x, r6.z                       ; sin/cos 构造旋转
L473-476    由方向 r7 经 sin/cos 混合 ⇒ 旋转后的方向 r5
L505-516    acos/atan2 多项式近似 + ×(0.159155, 0.318310) + 0.5
             ; = ×(1/2π, 1/π) + 0.5 ⇒ 把方向映射到 [0,1] 的球面 UV
L517  sample_l_indexable(...) r5.xyz, r5.xyxx, t5.xyzw, s5, cb0[322].x   ; LOD = u_refraction_mipmap
L518-520    非线性重整：r8 = r5²; r5.x = 2·r5.z; r5 = r5.x · r8   （即 ∝ 2·z·rgb²）
L521  add    r6.z, cb0[321].w, l(1.000000)          ; contrast + 1
L522  add    r6.z, r6.z, cb0[321].w                 ; + contrast ⇒ 2·contrast + 1
L523  mad_sat r6.z, r5.x, r6.z, -cb0[321].w         ; saturate(sample.r × (2c+1) − c)
L524  mul    r6.z, r6.z, cb0[322].y                 ; × u_refraction_brightness
L525  mul    r8.xyz, r6.zzzz, cb0[186].xyzx         ; × u_refraction_color
L526-527    × 表面权重 r3.w ⇒ 累加进最终色
```
**公式**：`rot = u_refraction_rotation × 2π`（**角度**，用于旋转**入射/视线方向**，再经 acos/atan2 映射为球面 UV —— 不是简单 UV 旋转，也不是解析法线扰动）；
`t = tex(t_refraction_tex, uv_sphere, lod=u_refraction_mipmap)`；
`refr = saturate(t.r × (2·u_refraction_contrast + 1) − u_refraction_contrast) × u_refraction_brightness × u_refraction_color`；
最后 ×表面权重累加。
⇒ **contrast 是"线性 remap + saturate"（不是阈值/阶跃）**；brightness/color 都是**乘性**。

## 4. reflection 层：**源侧不采样**（明确负结论）

15/15 个 crystal PS 中：纹理绑定表**没有** `t_reflection_tex`（`s_reflection_tex` 只是**采样器名**，被 L464 用来采样 `t_caustic_tex`）；所有 `sample*` 指令的资源操作数只有 `t0/t1/t2/t3/t4/t5/t6/t8/t9…` ⇒ **无一处采样反射贴图**。
（对比：清单里 `t_reflection_tex` 在 viewer/manifest 侧被当作层存在。⇒ 该槽是**源侧声明残留**；task-43 不应为它建采样。）

## 5. detail 层（`DetailMap` = t2，采样器 s3 = `s_detailmap`）

```
L396  add   r8.xy, v0.xyxx, cb0[317].xyxx          ; uv + (u_detail_offset_x, u_detail_offset_y)
L397  mul   r8.xy, r8.xyxx, cb0[316].wwww          ; × u_detail_tilling
L398  sample_indexable(...) r8.xyzw, r8.xyxx, t2.xyzw, s3
L399  mad   r9.xy, r8.xyxx, l(2,2), l(-1,-1)       ; xy: [0,1]→[-1,1]
L400  mul   r9.xy, r9.xyxx, cb0[317].zzzz          ; × u_detail_intensity
L401/402 max/min ±1                                ; clamp
L403  add   r0.w, r8.z, l(-1.000000)
L404  mad   r8.z, cb0[317].z, r0.w, l(1.000000)    ; z: 1 + u_detail_intensity×(z−1)
L405  mul   r8.xyzw, r6.xxxx, r8.xyzw              ; × m = saturate(Tex0.r)  ← 源公式的 m
```
**公式**：`uv_d = (uv0 + offset_x,y) × u_detail_tilling`；
`N_d = clamp(2·D.xy − 1, ±1) × u_detail_intensity` · `z_d = 1 + I·(D.z − 1)`；
`d_raw = m × (N_d.x, N_d.y, z_d, D.w)`（`m = saturate(Tex0.r)`）。
⇒ **与 viewer 现行 `d = m × DetailMap.a` 不同**：源用 **xy（法线）与 z**、并显式引入 intensity/offset/tilling；
**待闭环**：`r8` 后续哪一分量进入 `d`（下一步追踪，见 §7 U-2）。

## 6. specular / metallic / rotate_angle

```
L441  add  r3.w, -cb0[320].y, cb0[320].z    ; -u_base_specular + u_crystal_specular
L442  mad  r3.w, r1.w, r3.w, cb0[320].y     ; specular = lerp(u_base_specular, u_crystal_specular, r1.w)
L443  add  r4.w, -cb0[319].w, cb0[320].x    ; -u_base_metallic + u_crystal_metallic ⇒ 同形 lerp
```
⇒ `specular = lerp(base_spec, crystal_spec, w)` · `metallic = lerp(base_metallic, crystal_metallic, w)`
（与 `viewer.js:2356` 引用的"反汇编 L368-369"**同形**，但**偏移不同**：viewer 记 `cb0[316].z/.w`、本变体是 `cb0[319].w`/`cb0[320].x` ⇒ 属**变体差异**，登记以免误用。）

## 7. 顺带三条小确认

### (a) `refraction_envmap_3` 的**名字级解析**：能解析，但扩展名是 **`.dds`** ✗≠源声明的 `.tga`
用 `03拆包产物\_gim_out\find_entry_by_path.py --batch`（对 91 容器只读表查询）：
| 尝试路径 | 结果 |
|---|---|
| `common\textures\refraction_envmap_3.tga` | **MISS** |
| `common\textures\refraction_envmap_3.dds` | **HIT** → `E:\mrzh\res.gpk` row **8710**, o=712,575,780, comp=45,186, dec=**174,928**, flag=12(zstd), c1=`C6242432`, c2=`20A84330` |
| `.png` / `.TGA` / 无扩展名 / 去 `common\` 前缀 / 大小写变体 / 皮肤内路径 | 全 **MISS** |
| `refraction_envmap{,1,2,4}.tga` | 全 **MISS** |
⇒ **结论：该资源在容器内存在（`.dds`，解压 174,928 B）**，manifest 里"`not_shipped`"的判断**需要更正**（命中 1/14）✓ —— 即 1110171 的折射层**是可接的**。

### (b) 材料文档声明名清单（来自 manifest `logical_path`，源侧声明）
| 皮肤 | 材料 | Tex0 | t_basecolor | ParamMap | NormalMap | t_surfacemap | 晶体层 |
|---|---|---|---|---|---|---|---|
| 1003_012（prim0-3） | skin_1003_012_0..3 | `…001b_m.tga` | `…001a.tga` | `…001m.tga` | `…001n.tga` | `…001s_m.tga` | prim1/2/3: `crystal_bump_n_uvva.tga` + `crystal_caustic_uvva.tga` + `crystal_reflection_uvva.tga`（prim3 无 reflection）；`refraction_envmap_3.tga` |
| 1003_010（prim4-6） | skin_1003_010_0/1/2 | `…001b_m.tga` | `…001a.tga`（prim6 **无**） | `…001m.tga`（prim5/6 **无**） | `…001n.tga` | `…001s_m.tga`（prim5/6 **无**） | prim5: bump+caustic+reflection；prim6: 仅 bump；均带 `refraction_envmap_3.tga` |
| 2003_029（1110177） | skin_2003_029_0 | `…029001a.tga` | `…029001a.tga` | `…029001m.tga` | `…029001n.tga` | `…029001s_m.tga` | — |
| 2003_029 | skin_2003_029_1 / _2 | `…029001b_m.tga` | **无** | **无** | `…029001n.tga` | **无** | prim1: `crystal_bump_n02.tga` + 跨皮肤 caustic（`skin_1012_013\testures\…`）+ `crystal_reflection_uvva.tga`；prim2: `crystal_bump_n_uvva.tga` + caustic(已解析) + reflection + refraction |
⇒ **"彩色基色图"（`*_a.tga`，即 `t_basecolor`）在 1003_010/012 与 2003_029(prim0) 源侧确被声明** ✓；**1110177 的两个晶体 prim1/2 源侧没有 `t_basecolor` 声明**（crystal 白名单情形，与 `viewer.js:1006-1008` 的 whitelist 一致 ✓）。

### (c) U1 / U2 的**静态预判**（推理，非实测；本轮不开浏览器）
- **U1（prim5/6 绑哪个 rough_repack）**：`famOf` 逐 prim 回退链（`viewer.js:1137/1147-1149`）：
  · prim5：srcA(`t_basecolor`)=`012_a`?? → 实测 prim5 的 t_basecolor = **`010_a.png`** ⇒ fam=`010` ⇒ **`rough_repack_010.png`**（盘上 ✓）
  · prim6：**无 t_basecolor** ⇒ 回退 `Tex0`=`010_b_m.png` ⇒ fam=`010` ⇒ **`rough_repack_010.png`**（盘上 ✓）
  · prim0–3：`012` ⇒ `rough_repack_012.png` ✓
  ⇒ **预判：prim5/6 = `_010`（不是 `_012`）**；仍需一次 `__matDump().meshes[5,6].roughnessMap.name` 闭环（U1 未闭环）。
- **U2（`local_file:null` 槽的运行时行为）**：`viewer.js:980-981/1521-1525` 用 `g[k] && g[k].file` 真值判断；`local_file:null` ⇒ `file` 为 falsy ⇒ **应判"未绑定"**（不是误判为已绑定）。**这是代码路径推理，未实测**。

## 8. unresolved 清单（不猜）
| id | 未定项 | 现状 |
|---|---|---|
| U-1 | `u_rotate_angle` 的消费点 | 代表变体未声明；6/15 变体有（off=160）⇒ 需逐文件核 cbuffer 归属与引用窗 |
| U-2 | detail 处理后 `r8` 的哪一分量进入 `d`、以及是否与 `D.w` 有关 | 已定位到 L405，下一步需继续追 `r8` 的消费者 |
| U-3 | `u_refraction_opacity`(cb0[322].z) 的用途 | 仅见 1 处引用（L1123 `mul r0.x, r0.x, cb0[322].z`），上下文未闭环 |
| U-4 | 15 个 VS 侧是否另有晶体层逻辑 | 本轮只追 PS（任务目标是"进最终色"的公式） |
| U-5 | 其它 quality 变体（quality3/4/5）是否公式一致 | 已核 15 个 PS 的**层绑定/采样形态一致**；**逐条指令级一致性未逐一比对** |

## 9. 复现命令
```
venv\Scripts\python.exe %TEMP%\RXFORM_census.py   # 968 asm × 管道归属 + 22 uniform 三元状态 → RXFORM_result.json
venv\Scripts\python.exe %TEMP%\RXFORM_trace.py    # 代表 PS 的 uniform 引用窗 + 采样 UV 链 → RXFORM2_dump.txt
venv\Scripts\python.exe %TEMP%\RXFORM3.py         # 采样→UV→消费者三段链 + 纹理名解析
venv\Scripts\python.exe %TEMP%\RXFORM4.py         # caustic/refraction 数学窗 + 成员名反查 + 15 PS 绑定核对 + detail 窗
venv\Scripts\python.exe %TEMP%\RXFORM5.py         # 声明名清单 + U1/U2 静态推导
venv\Scripts\python.exe 03拆包产物\_gim_out\find_entry_by_path.py --batch %TEMP%\refr_paths.txt   # (a) 名字级解析
```
