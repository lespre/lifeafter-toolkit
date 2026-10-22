# RX_fx_family_extra：`u_dissolve_amount` 公式 + TransparentMode/depth_bias 静态可得性 + 默认值勘察

> **只读追加**（上一份 `RX_fx_family_formulas_20260919.md` 保持冻结不动；本轮新增本文件 + `RX_fx_family_extra.json`）。未起浏览器、未改任何既有文件。
> 证据文件：`_target_1110171/fx_family/9053b046_7c6dc86e_d11_blob1.dxbc.asm`（PS）· `uber_fx_common.nfx2.bin`（c159 声明图）· `1110177/sfx/fx_skin_2003_029_{hit,jisha}.sfx` · 两个 FX pipe。

---

## 1. ★ `u_dissolve_amount` 完整公式（已展开，L374-404）

### 1.1 涉及的槽位（成员名已全部落到 offset）
| uniform | offset | 槽位 | 角色 |
|---|---|---|---|
| `u_dissolve_distort` | 244 | cb0[15].y | 开关：`L374 ne r0.w, cb0[15].y, 0` |
| **`u_dissolve_amount`** | **248** | **cb0[15].z** | **阈值主参**（L387） |
| `u_dissolve_edgewidth` | 252 | cb0[15].w | **边缘宽度，按 0.01 缩放**（L389） |
| `u_dissolve_smooth` | 256 | cb0[16].x | 平滑度 → **取倒数**（L391 `div 1.0, cb0[16].x`） |
| `u_dissolve_opacitymix` | 260 | cb0[16].y | 掩码与基准的混合（L384） |
| `u_use_edgecolor` | 264 | cb0[16].z | 边色开关（L423） |
| `u_dissolve_edgecolor_intensity` | 268 | cb0[16].w | 边色强度（L422） |
| `u_dissolvetex_channel` | 272 | cb0[17].x | 溶解贴图通道选择（L378-379） |
| `u_dissolvetex_tilling_y/_offset_x/_offset_y/_speed_x/_speed_y` | 280/284/288/292/296 | cb0[17].z?..cb0[18] | 溶解 UV（L376 用 r0.yz/r1.xy ✓） |
| `u_dissolve_rotation` | 300 | cb0[18].z | UV 旋转（本窗口未展开） |
| **`u_dissolve_tex_anti`** | **304** | **cb0[19].x** | **掩码反相开关**（L381） |
| `u_dissolve_dir_length` | 316 | cb0[19].w | 阈值偏移项 `(x+1)`（L386） |

### 1.2 公式链（逐行证据）
```
L376  add   r0.yz, r0.yyzy, r1.xxyx                       ; 溶解 UV = uv + offset（含 tilling/speed 派生）
L377  sample_indexable(texture2d) r0.yz, r0.yzyy, t3      ; ★ t3 = 溶解贴图，取两通道
L378  ne    r0.w, cb0[17].x, l(0)                         ; u_dissolvetex_channel
L379  movc  r0.y, r0.w, r0.z, r0.y                        ; 选 x 或 y 通道
L380  add   r0.z, -r0.y, l(1.0)                           ; 1 − mask
L381  ne    r0.w, cb0[19].x, l(0)                         ; u_dissolve_tex_anti
L382  movc  r0.y, r0.w, r0.z, r0.y                        ; ★ mask = anti ? 1−mask : mask
L383  add   r0.z, -r0.y, r2.w                             ; (base − mask)，base 来自插值量 r2.w
L384  mad   r0.y, cb0[16].y, r0.z, r0.y                   ; mask' = mask + opacitymix·(base − mask)
L386  add   r0.z, cb0[19].w, l(1.0)                       ; u_dissolve_dir_length + 1
L387  mad   r0.z, cb0[15].z, r0.z, l(-1.0)                ; ★ θ = u_dissolve_amount·(dir_length+1) − 1
L388  add   r0.w, -r0.z, r0.y                             ; mask' − θ
L389  mad   r0.z, cb0[15].w, l(0.01), r0.z                ; ★ θ_edge = θ + u_dissolve_edgewidth×0.01
L390  add   r0.y, -r0.z, r0.y                             ; mask' − θ_edge
L391  div   r0.z, l(1.0), cb0[16].x                       ; 1 / u_dissolve_smooth
L392  mul_sat r0.yw, r0.zzzz, r0.yyyw                     ; t_edge、t_main ∈ [0,1]
L393  mad   r0.z, r0.w, l(-2.0), l(3.0)                   ; 3 − 2t（t = t_main）
L394  mul   r0.w, r0.w, r0.w                              ; t²
L395  mul   r0.z, r0.w, r0.z                              ; t²(3−2t)  ← **smoothstep 多项式**
L396  min   r0.w, r0.z, l(1.0)
L397  mul   r0.x, r0.w, r0.x                              ; 基础 alpha × dissolve 曲线
L398-402  log/exp + 判定 + × cb0[25].x (u_mask_power)      ; 幂曲线（>0.0001 才生效）
L403  mul_sat r0.x, r0.x, cb0[24].w                       ; × u_mask_intensity
L404  mul   o0.w, r0.x, cb0[25].y                         ; × u_overall_opacity ⇒ 输出 alpha
```
**⇒ 可实现式**（供 chain-auditor 照抄；`base = 插值基准（r2.w，未逐级追溯）`、`mask = 溶解贴图所选通道`）：
```
mask = anti ? 1−mask : mask
mask' = mask + u_dissolve_opacitymix·(base − mask)
θ      = u_dissolve_amount·(u_dissolve_dir_length + 1) − 1
θ_edge = θ + u_dissolve_edgewidth × 0.01
t_main = saturate((mask' − θ)      / u_dissolve_smooth)
t_edge = saturate((mask' − θ_edge) / u_dissolve_smooth)
s      = min( (t_main²(3 − 2·t_main)), 1 )
alpha  = s · powFn(base_alpha) · u_mask_intensity · u_overall_opacity
```
- **★ 单位提示**：`edgewidth` 乘 **0.01**（即 1.0 的 edgewidth = 0.01 的 mask 跨度 ✓）—— 这是**可直接照用的比例**，不是猜测 ✓
- **边缘项**（`t_edge`）进入后面的**边色**分支（`u_use_edgecolor` cb0[16].z / `u_dissolve_edgecolor_intensity` cb0[16].w，见 L422-423 ✓）
- **部分 unresolved**：`base`（L383 的 `r2.w`）来自顶点/插值量，本轮未逐级追溯；`u_dissolve_rotation` 与本窗口之外的 dissolvetex dirmask 分支未展开

## 2. `TransparentMode` → 混合状态：**静态不可得**（已收窄到极限）

| 尝试的入口 | 结果 |
|---|---|
| `.sfx` 节点级 `TransparentMode` | 取值 **5 ×14 / 0 ×7 / 2 ×5**（26 节点全覆盖 ✓）——但它只是**枚举值**，`<Macros>` 里**没有** `TRANSPARENT_STAGE` 之类的宏 ✗（见下） |
| `.sfx` 非空 `<Macros>` 块（全部 10 个） | **只有 Bool=TRUE**：`USE_EMISSIVE_CONTROL=TRUE ×6` · `USE_SFXLIGHT_FOG=TRUE ×3` · `USE_VERTEXCOLOR=TRUE ×3` · `USE_SOFTPARTICLE=TRUE ×2` · `USE_MASK01=TRUE ×1` ⇒ **没有任何一处在编码混合状态** ✗ |
| c159（`uber_fx_common.nfx2.bin`） | 宏名表里**有** `TRANSPARENT_STAGE`（off 1704 ✓）以及 `ALPHA_TEST_ENABLE`/`MTL_USE_DEPTHBUFFER_FETCH`/`NO_ALPHA_CHANNEL` 等 ✓，但**该皮肤没有给 `TRANSPARENT_STAGE` 赋值**（未在任何宏块中出现 ✓）⇒ 无法据此判定 ✗ |
| 运行时缓存：同族 pipe 变体（仅 2 个） | 两个 pipe 的二进制里 **`DepthBias`/`BlendState`/`Rasterizer`/`Transparent` 全部 0 命中** ✗ ⇒ 渲染状态不在 pipe 里 |
| 引擎侧状态表（`.mtg` 等） | **工作区内无任何 `.mtg` 文件** ✗（`Get-ChildItem -Recurse -Include *.mtg` = 0） |
| shader 内的间接线索 | 只有一个**整体开关**：`L423 ne r0.w, cb0[16].z, l(0)` + `L424 and r0.xyz, r0.xyzx, r0.wwww`（用 `u_use_edgecolor` 门控边色项）—— **不足以定表** ✗ |

**⇒ 结论（就按 Lead 要的那句）**：**`TransparentMode` → 混合状态只能靠引擎状态解析，静态不可得** ✓（我已排除上述 6 条入口；**不建议**再从静态侧推测 ADD/ALPHA）

## 3. `u_depth_bias` 的引擎消费点：**静态不可得**

| 入口 | 结果 |
|---|---|
| 族内 shader（2 pipe × VS/PS = 4 个 asm） | 全部「声明 1 处 + **指令体 0 处** + `[unused]`」✗（batch 变体 `u_depth_bias_batch[4]`@5968 亦 `[unused]`） |
| c159 声明图 | `u_depth_bias` **只作为名字**出现（含 `_batch`），**无渲染状态字段/无值** ✗ |
| pipe 二进制 | `DepthBias` 串 **0 命中** ✗ |
| `.mtg`/材质状态文件 | **工作区内不存在** ✗ |
**⇒ 结论**：`u_depth_bias` 的**单位与消费点 = 运行时引擎状态，静态不可得** ✓（下一步只能靠运行时抓取；本任务范围外）。**给 chain-auditor 的建议保持"不做 + 登记 `engine_state_unresolved`"** ✓

## 4. 四个"因子"的默认值来源：**c159 里没有默认值** ✗

| uniform | c159 中出现的 2 次是什么 | 邻近是否有默认值 |
|---|---|---|
| `u_emissive_grey_intensity` | `u_emissive_grey_intensity` + `…_batch`（@6376 / 6402） | **无**（前后 40B 全是下一个名字串 ✓） |
| `u_emissive_mix` | 同上（@6502 / 6517） | **无** |
| `u_emissive_desaturate` | 同上（@6326 / 6348） | **无** |
| `u_mask_intensity` | 同上（@8452 / 8469） | **无** |
（对照 `u_depth_bias` @3503/3516 同样只有 `name` + `name_batch` ✓ ⇒ **该 c159 是"名字池"，不含默认值表** ✗）
- `.sfx` **也没有**逐节点声明这 4 个 uniform ✗（此前 uniform 汇总里没有它们 ✓）⇒ **无逐节点源值、无静态默认值** ✓
- ⚠ **给 chain-auditor 的一个重要提醒**：**"省略"≠"等价于 0"** —— 既然 `.sfx` 设了 **`USE_EMISSIVE_CONTROL=TRUE`（6 处）**，说明这些节点走的是**自发光控制路径**，而该路径上的 `grey_intensity/mix/desaturate/mask_intensity` 会由**引擎材质默认值**填充（静态不可得）⇒ 实现时**省略这些因子并标 `omitted_undeclared` 是唯一诚实做法** ✓；若要验证观感差异，建议**只做一次 A/B**（省略 vs 显式 1.0）并如实标注为实验，不是源还原 ✓

## 5. 本轮 unresolved / 已排除

**unresolved**：U1 `TransparentMode`→混合状态（引擎侧）· U2 `u_depth_bias` 单位与消费点（引擎侧）· U3 这 4 个因子的**引擎材质默认值** · U4 dissolve 的 `base`(r2.w) 溯源与 `u_dissolve_rotation`/dirmask 分支 · U5 颜色关键帧色彩空间
**已排除**：① FX 的 DXBC 在容器/gpk ✗ ② 15 个命名变体能命中 ✗ ③ `_game_shader_db\pipes` 有 FX 族 ✗ ④ `u_depth_bias` 在 shader 内（4 asm 全 `[unused]`）✗ ⑤ `u_overall_opacity` 乘亮度 ✗（只乘 alpha ✓）⑥ `.sfx` 宏块编码混合状态 ✗ ⑦ pipe 里含渲染状态串 ✗ ⑧ 工作区有 `.mtg` ✗ ⑨ c159 含默认值表 ✗

## 6. 复核命令
```
# 反汇编（沿用已打通链路）
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\fxc.exe" /dumpbin /Fc out.asm blob.dxbc
venv\Scripts\python.exe %TEMP%\RXEX1.py   # dissolve 成员表 + cb0[15..19] 引用 + L376-404 窗口
venv\Scripts\python.exe %TEMP%\RXEX2.py   # 成员名补全 + c159 字符串/宏名 + 目标 uniform 上下文
venv\Scripts\python.exe %TEMP%\RXEX3.py   # .sfx 宏块 + Model TransparentMode 分布 + c159 uniform 出现次数
venv\Scripts\python.exe %TEMP%\RXEX4.py   # 非空 Macros 块原文 + 四个 uniform 的字节上下文
```
