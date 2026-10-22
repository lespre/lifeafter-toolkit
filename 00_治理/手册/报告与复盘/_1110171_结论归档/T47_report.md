# task-47 报告 —— 晶体源 BRDF（metalness 插值）接线 + 全套负控/正控读数

作者：shader-auditor ｜ 2026-09-19 ｜ **结论先说：接线本身完全按源式生效且可控可逆（N0/N1/N2/N4/P4 全通过），
但 spec §5 的"可证伪预测"被实测**反向证伪**：把源 metalness 接上后晶体整体**变暗**（`>0.5` −41.2%），
门槛未达 ⇒ 默认保持 OFF，**未上 1110177 prim2（P3）**，等 lead 裁定。**

## 0. 钉（pins）

| 项 | 值 |
|---|---|
| viewer.js **最终**（含 D3 强制门） | **`40618CC0FF433C3F`**（364,606 B / 4885 行 / `node --check` OK） |
| viewer.js 主体接线版（D3 前） | `876C249A695667BA`（363,112 B） |
| viewer.js 改前 | `57D181F1432095F3`（348,136 B） |
| 备份 | `%TEMP%\wsv_bak_task47_20260919_164235.js`（= `57D181F1432095F3`）、`%TEMP%\wsv_bak_task47D3_20260919_170939.js`（= `876C249A695667BA`） |
| 其余 pin（改前复核一致） | `1110177/viewer.json 7575FAFAD33DD670`、`1110171/viewer.json 62E7BDDC9CF6EC6D`、`1110177/effects.json 10CC9A938BE92A10` |
| manifest（我未改动） | `1110171/neox_material.json = 64A07D5DF157EC16`、`1110177/neox_material.json = A05C4F2C8DDFCF9A` |
| 未动 | manifest / adapter / board.html / 注册表 / `wiki_selfcheck.py`；未放宽任何 fail-closed |

## 1. 落地内容（6 处，逐处见 §E2.1；串自查为脚本计数）

1. **注入头部（IBL 块，所有族）**：`uniform float uBrdfOn/uBaseMetal/uCrystalMetal;` + 全局 `float q_metal = 0.0; float q_diffW = 1.0;`
   ⇒ 未接线/未就绪/开关关/链注入被跳过四种情形**都可编译且与接线前逐像素相同**。
2. **per-prim 值（IBL 块）**：只读 `pr.source_uniforms`；`uBrdfOn` 初值 = 开关∧有值∧`envMode==='source_ibl'`；
   `uBaseMetal` 缺失 ⇒ **0.0（现值，不借值）**；`uCrystalMetal` 缺失 ⇒ 整 prim 不接线；写 `m.userData.__brdfSrc`（含 `conflict`）。
3. **`patchMulti()` 新增**：同 chunk 多串替换（每串命中必须=1）+ 只重插一次 include（命中必须=1）；**原 `patch()` 未动**。
4. **`lights_physical_fragment` 按族分叉**：weapon 族替换串与改前**逐字节相同**；crystal 族改用 `q_metal` 并加 `diffuseColor * q_diffW`。
5. **晶体链 `injC` 追加（仅当 IBL 块生效）**：`q_metal = mix(0.0, clamp(mix(uBaseMetal,uCrystalMetal, clamp(q_mm*q_dd,0,1)),0,1), uBrdfOn); q_diffW = 1.0 - q_metal;`
   —— `w` 用链里**已有**的 `q_mm`（源 L393 的 m）× `q_dd`（源 L405 的 m·D.a）= 源 L438 的 `w = m²·D.a`；未绑 DetailMap 时退化 `m²`（`D.a≡1` 已证），**两条路径同值**。
6. **mesh 循环之后**：`window.__brdfSrc(on)`（唯一开关 + 就绪门）+ `window.__brdfSrcProbe()`（逐 prim + 编译源码自证 + `patchLog`）。

**three r180 定证（"三条线→两条线"）**：`metalnessFactor` 全文 6 次、`material.metalness` **0 次**
⇒ metalness 只经 `material.diffuseColor = diffuseColor.rgb*(1−metalnessFactor)` 与
`material.specularColor = mix(vec3(0.04), diffuseColor.rgb, metalnessFactor)` 两条线影响着色，
与源 `L548`/`L551` 一一对应；非 IOR 分支 `specularF90=1.0` 与 metalness 无关。

## 2. 读数（同一 harness；改前基线先抓，见 §3 的 pre 列）

### N0 默认 OFF 锚（**同 harness 改前 vs 改后**）
| 皮肤 | 改前 OFF sha | 改后 OFF sha | 五读数（pre = post） |
|---|---|---|---|
| 1110177 | `9dbb3449da619f56` | **`9dbb3449da619f56`** | p50 0.2829 / p95 0.5745 / >0.5 18.242 / >0.75 0.989 / 暖色 0.689 / mask 1.826 |
| 1110171 | `403d89842b145e3c` | **`403d89842b145e3c`** | p50 0.1232 / p95 0.4865 / >0.5 3.394 / >0.75 0.273 / 暖色 0.106 / mask 2.449 |

⇒ **默认 OFF 与接线前逐字节相同 + 五读数逐项相同**（跨 harness 的 sha 不可比，此处只比**同 harness**）。

### N1 反复切换（可逆可复现）
| 皮肤 | off 集合 | on 集合 |
|---|---|---|
| 1110177 | {`9dbb3449da619f56`}（off 各次全等） | {`a19c6625c9dc4710`}（on1=on2） |
| 1110171 | {`403d89842b145e3c`} | {`77f4941bddf94a10`} |
另：N3 的**独立页面**settle 后 OFF/ON 与上表**同 sha** ⇒ 跨页面可复现。

### N2 ON 状态内"无值 prim"负控
| 皮肤 | 无值 prim | changed | 五读数 |
|---|---|---|---|
| 1110177 | prim0（weapon） | **False** | 逐位相同（0.2239/0.5303/7.274/1.24/0.864） |
| 1110171 | prim0、prim4（weapon） | **False** | 逐位相同 |

### N3 窗口期负控 —— **代码路径证据 + D3 后已升级为"实测证据"（强制门法）**

**第一轮的缺陷（我的错，作废）**：窗口判据用 `__texReady().meshes[*].envMode!=='source_ibl'`，之后又等 3 帧稳定（≥2 s）⇒
真窗口早已关闭；取到的时刻探针显示 `ibl_ready:true / faces:6 / pending_hidden:false` ⇒ `before≠after` 是**接线合法生效**，
既不能证明门失效、也不能证明门通过。
**第二轮（`t47_n3.py`，紧轮询活体口径）**：`__brdfSrc` 首次可用时（1110171 @3606 ms、1110177 @975 ms→1510 ms）
所有 wireable prim 已 `ibl_ready=true, faces=6, pending_hidden=false`，采样到 445 s/171 s 仍是全 ready
⇒ **`ibl_ready=false` 的真实时刻在本两皮肤上不可观测**（源 cube 六面在任何材质可被探针看到之前就已就绪）⇒ 该子句曾仅有**代码路径证据**。

**D3 强制门法（lead 批准，新增探针专用 `__brdfForceNotReady`）—— 实测成对读数（`t47_p3.py`）**

| 皮肤 | ① OFF 锚 | ② 强制假 + 开开关 | ③ 解除强制 + settle + 开开关 | ④ 再强制假 |
|---|---|---|---|---|
| 1110177 | `9dbb3449da619f56`（= 锚 ✅） | `9dbb3449da619f56`（**逐字节等于 OFF** ✅） | `a19c6625c9dc4710`（**与 OFF 不同** ✅） | `9dbb3449da619f56`（**回到 OFF** ✅） |
| 1110171 | `403d89842b145e3c`（= 锚 ✅） | `403d89842b145e3c`（**逐字节等于 OFF** ✅） | `77f4941bddf94a10`（**与 OFF 不同** ✅） | `403d89842b145e3c`（**回到 OFF** ✅） |

强制中 `__brdfSrc(true)` 的返回：`force_not_ready:true`、每行 `ibl_ready:false, faces:6, pending_hidden:false, on:false`，
`s.uBrdfOn=0`（live uniform 读回）⇒ **门确实在"就绪为假"时把金属度压回 0**；
解除强制后同一开关立刻生效 ⇒ **N3 = 实测证据（不再是代码路径）** ✅
即：`ibl_pending ⇒ metalness 保持 0`（spec §4 风险 1）**已被实测闭环**。

### N4 缺值皮肤恒等（**32 个皮肤恒等**）
* 全树扫描（34 个有 `neox_material.json` 的皮肤）：`u_crystal_metallic` 有值者**仅 2 个**（1110171、1110177）
  ⇒ 其余 **32 个必然逐字节恒等**（无值 ⇒ 整 prim 不接线）。
* 实测控制组 5 皮肤 OFF sha **pre = post 逐字节相同**：
  `1110024 3ea7207fc2cd12be`、`1110129 9d08a508b18810a5`、`1110145 23094258cfc115c6`、
  `1110152 f29ff414f8339c4b`、`1110165 e3415ff917391086`；五读数与 `applied`（5/5、5/5、7/7、2/2、4/4）逐项相同。
* 另：1110171/1110177 的**weapon prim** 在 ON 下也不变（N2）。

### P4 自证（`__brdfSrcProbe()`）
* `patchLog`：prim0 `dielectricF0_weapon ok=true hits="1" inc=1 strs=1`；crystal prims
  `crystalBRDF_qmetal ok=true hits="1+1" inc=1 strs=2`；`sourceEnvWeight ok=true hits=1` ⇒ **命中数全部=1** ✓
* `fragDecl=true / fragDefault=true`（所有 prim）；`fragDiffPatch=true / fragSpecPatch=true`（仅 crystal，weapon=false）✓
* live uniform 与报告值一致（prim1 `uBrdfOn=1, uBaseMetal=0.6, uCrystalMetal=0.95`；prim2 `0/1`；prim3 `0/0.75`…）✓
* ⚠ `fragAssign=false` 的**解释（非缺陷）**：探针读的 `mm.userData.__frag` 是 **IBL 阶段快照**（在晶体链注入之前赋值），
  而 `q_metal = …` 那行由晶体链在**之后**追加（`__fragCrystal` 里才有）⇒ 该字段天然为 false；实际生效由帧变化 + live uniform 证明。
  （若要让它也自证，需把探针改读 `__fragCrystal` —— **属代码改动、会改 pin，等 lead 批**，见 D4。）
* **`conflict` 实测命中（C2 生效，未截断复核）**：1110171 **prim5** 行 =
  `{prim:5, base_metal:0, crystal_metal:0.75, crystal_params_value:1, conflict:true, wireable:true, base_specular:0, crystal_specular:1,
    value_source:'source_uniforms', uCrystalMetal:0.75, on:true, uBrdfOn:1, fragDiffPatch:true, fragSpecPatch:true}` ✓
  —— 即：**取 source_uniforms 的 0.75、并显式报出两源冲突**（`crystal_params=1`）。其余 prim `conflict:false`。
  manifest 未被我改动：`1110171/neox_material.json = 64A07D5DF157EC16`、`1110177/neox_material.json = A05C4F2C8DDFCF9A`。

### P5 方法学
bg 一律 `__primShow(-1)`（未用 `__primOnly`）；逐 prim 用 `__primShow(i)`；每状态"连续 3 帧同 sha"；
ON 全视图用 N=5；协议严格 `open → 等 applied → sleep(8) → __post(false) → __hidePanels(true) → __sfxTime(0)`。
⚠ 协议陷阱（本轮实测）：**逐 prim 往返后不得用后续帧当 OFF 基线**（`__primShow(null)` 会把所有 mesh 置 visible）——见 §4c。

## 3. P1（1110171）—— **门槛不通过，方向与 spec §5 预测相反**

| 读数 | OFF | ON | Δ（pp） | Δ（%） | spec §5 预测 |
|---|---|---|---|---|---|
| `p50` | 0.1232 | 0.1223 | −0.0009 | −0.73% | 基本不变或微升 ⇒ ✅ 通过（且 `|Δp50|=0.0009 ≤ 0.02`） |
| `p95` | 0.4865 | 0.4593 | **−0.0272** | −5.59% | **上升** ⇒ ❌ 反向 |
| `>0.5` | 3.394 | 1.995 | **−1.399** | −41.2% | **上升（R1≥2.5%）** ⇒ ❌ 反向 |
| `>0.75` | 0.273 | 0.273 | 0.000 | 0% | **明显上升（R2≥0.10%）** ⇒ ❌ 未动 |
| `暖色%` | 0.106 | 0.106 | 0.000 | 0% | **上升（R3>0）** ⇒ ❌ 未动 |
| `mask%` | 2.449 | 2.445 | −0.004 | −0.16% | （掩模几乎不变，几何一致） |

**门槛判定**：`R1≥2.5% ∧ R2≥0.10% ∧ R3>0 ∧ |Δp50|≤0.02` ⇒ **不通过**（只有 |Δp50| 与"p50 基本不变"两项满足）。

**逐 prim（`__primShow(i)`，OFF→ON）**：**5 个晶体 prim 全部变暗**，2 个 weapon prim 逐位不变：

| prim | crystal_metal | mean OFF→ON | `>0.5` OFF→ON | `>0.75` OFF→ON |
|---|---|---|---|---|
| 1 | 1.0 | 0.3894 → 0.3783（−2.85%） | 14.204 → 11.768（**−17.2%**） | 1.890 → 1.837 |
| 2 | 1.0 | 0.3833 → 0.3617（−5.63%） | 10.372 → 5.459（**−47.4%**） | 0.411 → 0.412 |
| 3 | 0.75 | 0.3821 → 0.3754（−1.75%） | 19.858 → 16.912（**−14.8%**） | 0.709 → 0.735 |
| 5 | **0.75（C2 取值）** | 0.3899 → 0.3650（−6.39%） | 15.736 → 3.054（**−80.6%**） | 0.023 → 0.023 |
| 6 | 0.75 | 0.3285 → 0.3081（−6.21%） | 1.025 → 1.066 | 0 → 0 |
| 0 / 4 | —（weapon） | 逐位不变 | 逐位不变 | 逐位不变 |

## 4. 为什么方向是"变暗"（诚实归因，未再接线）

1. 源式要求 `diffuse = albedo × (1 − metal)`：晶体 `w` 抬升后 metal≈0.17~0.77 ⇒ **漫反射被大幅削弱**；
2. 而本项目里**环境镜面补偿很弱**——与 task-45 两项的结论同根：晶体 `metalness` 接上后
   `u_cube_brightness`(0.71/2.74)、`u_rotate_angle` 的逐 prim 效果仅 ±0.5%~2.7%，
   说明**环境项（`indirectSpecular`）在晶体亮度里占比过小**；
3. 于是"删掉漫反射、换来的镜面不足以补回" ⇒ 全 prim 变暗、高光阈值（`>0.75`）不动。
   ⇒ **spec §5 的预测建立在"环境镜面足以补偿"的假设上，本链不满足**；这不是接线错误，而是**链的更深层缺陷**
   （环境/直射的能量分配与源不同；本项只改了 BRDF 的 metalness 通道）。
4. 因此本轮**不宣称**"晶体 BRDF 已源级复原"：只实现了 spec §1.1/§2.3 的 metalness 一条（`spec` 因子按 C3 未注入），
   且实测其净效果与参考图方向相反。

## 4b. P3（1110177 prim2 取证，lead 裁决 D2：跑一次、不改默认）—— **回闸条款触发**

全视图（同一 bg、同协议）：

| 读数 | OFF | ON | Δ |
|---|---|---|---|
| `p50` | 0.2829 | 0.2437 | **−0.0392（−13.9%）** ⇒ **回闸条款（`p50` 降 >0.02）触发** |
| `p95` | 0.5745 | 0.5110 | −0.0635（−11.1%） |
| `>0.5` | 18.242 | **5.807** | **−12.435 pp（−68.2%）** |
| `>0.75` | 0.989 | 1.003 | +0.014（+1.4%） |
| 暖色% | 0.689 | 0.699 | +0.010 |
| `mask%` | 1.826 | 1.800 | −0.026 |

逐 prim：

| prim | crystal_metal（base） | changed | mean OFF→ON | `>0.5` OFF→ON | p95 OFF→ON |
|---|---|---|---|---|---|
| 0 | —（weapon） | False | 0.2409 → 0.2409（逐位相同） | 7.274 → 7.274 | 0.5303 → 0.5303 |
| 1 | 0.95（base 0.6） | **True** | 0.4845 → **0.2702（−44.2%）** | 58.736 → **0.16（−99.7%）** | 0.5868 → 0.3537 |
| 2 | 1.0（base 缺） | **True** | 0.3244 → 0.2910（−10.3%） | 0 → 0 | 0.3642 → 0.2906 |

**亲眼描述（PNG：`T47P3_P3_1110177_p1_off/on.png`，2 倍裁切对比 `T47P3_sbs_p1.png`）**：
OFF 帧里那组晶体叶片是**亮白/银白**、叶缘有明显近白高光；ON 帧**同一组叶片整体塌成暗紫褐色**，
白色高光**整片消失**（`>0.5` 由 58.736% 掉到 0.16%），轮廓仍在、位置不动 ⇒ 现象与数字一致：
**`(1−metal)` 抽掉漫反射后，没有任何环境辐照补回来。**
**处置**：按 C4 **立即回闸**——本次为"取证一次"，**未改默认、未继续推**；开关已复位 `__brdfSrc(false)` + `__brdfForceNotReady(false)`。
**默认 OFF ⇒ 零回归**（本页开跑前 OFF 帧 = 锚 `9dbb3449da619f56`，五读数与基线逐项相同）。

### 4c. 新发现（协议级，登记进 MASK 口径建议）

同一页面**逐 prim 往返之后**的 OFF 帧不再等于锚：1110177 结束帧 `a2e008540662ea83` ≠ `9dbb3449da619f56`，
而**同一页开跑前**的 OFF 帧 = 锚；1110171 本轮没有逐 prim 往返 ⇒ 结束帧**仍 = 锚** `403d89842b145e3c`。
⇒ 归因：`__primShow(null)` 会把**所有 mesh 置 `visible=true`**，把"按设计不可见"的 prim 也显示出来 ⇒ **逐 prim 测量后不得用后续帧当 OFF 基线**。
（与既有 `__primOnly` 往返非帧中性是同一类协议陷阱，建议写进 `MASK_CRITERION.md`。）

## 5. lead 裁决与执行结果（已闭环）

| # | 裁决 | 执行结果 |
|---|---|---|
| **D1** | **保持"已接线 + 默认 OFF"**，另立只读诊断（已派 renderer-auditor） | 已执行：默认 OFF 不动，锚点不变；诊断（task-59）已完成并**证实**"缺环境辐照"假设 |
| **D2** | **P3 跑一次取证、不改默认**；`p50` 降 >0.02 按 C4 立即回闸 | 已执行：见 §4b —— **回闸条款触发**（`p50` −0.0392），已回闸、未改默认 |
| **D3** | 加探针专用 `__brdfForceNotReady`，把 N3 升为实测 | 已执行：新 pin `40618CC0FF433C3F`，见 §N3 的成对读数（强制度假 ⇒ 逐字节不变；解除 ⇒ 必须变；再强制 ⇒ 回到 OFF） |
| **D4** | `fragAssign` 改读 `__fragCrystal` | lead 裁定**不用改**（解释照收），维持现状 |

**⑥ 默认 OFF ⇒ 零回归（本报告的核心安全结论）**：
最终 pin `40618CC0FF433C3F` 上，两皮肤默认 OFF 帧与**接线前同 harness 基线逐字节相同**
（`9dbb3449da619f56` / `403d89842b145e3c`）、五读数逐项相同；32 个无值皮肤恒等（含 5 个实测控制皮肤 pre=post）；
probe-only 的 D3 改动同样零渲染影响（改后 OFF 帧仍 = 锚）。**所有新能力都在默认关闭的开关后面，一次都没打开过默认。**

**下一步（lead 已预告，等 GO，未抢跑）**：task-59 批准方案 (c) —— **用已绑定的源 cube 重建环境辐照（`reconstruction approximation`，必须显式标 `approx:true`）**，
放行 `getIBLIrradiance` + 不再只改名 radiance，默认 OFF + `__iblIrrSrc(true|false)` 三段式
（OFF / 只辐照 / 辐照+源式 BRDF），验收按诊断的可证伪预测（`>0.5` 回到 ≥ 3.394%、prim5 `>0.5` 收敛到 ≥ −10%、`p95 ≥ 0.4865`；
`p50` 抬 >+10% 或 `p95` 超基线 >5% ⇒ 补过头立即回闸）。

## 6. 仍未解决项（照旧登记，不实现）

* **环境辐照（漫反射）结构性缺失**（task-59 只读诊断已证实）：本链从未触碰 `getIBLIrradiance`（全文件 0 命中），
  环境是中性 PMREM 棚且 `envAllowed=false` 时 `envMapIntensity=0` ⇒ 环境漫反射 ≈ 0；
  源侧的 `u_ambient×u_char_ambient`（L564）、`u_env_sh`（L568-574）、`L575/578`、`t_realtime_env_spec`（L626-628）**一项都没接**；
  **SH/ambient 系数是运行时 cbuffer ⇒ 不能按值接（`unresolved`）**。这正是 P1 反向证伪的根因。
* 贴图 candidate（SFX 侧 `content_candidate` 未定证项）、BlendMode `NOT_FOUND`、单位属推导；
* `1110171 prim6 u_crystal_roughness=0.12`（entry 3251）**无消费点**（roughness 恒 1.0 / ParamMap.R）——与高光不足可能相关但**未定证**；
* `u_base_metallic / u_base_specular` 缺失项的**源侧端点值**未定证 ⇒ 用现值、不借值；
* 源 cube 六面顺序/基变换未定证；
* `spec` 因子（`spec = lerp(base_spec, crystal_spec, w)`）本轮**未注入**（两目标皮肤恒 1）；
* **manifest 侧 DetailMap 接受状态待补**（C1 推迟项：1110177 prim1/prim2 的 `file/sha256/confidence`，由 lead 在 A/B 之后作为独立小改动做）；
* `__brdfForceNotReady` 是**探针专用**入口，不参与渲染决策；它只在被显式调用时把就绪判据置假（默认 false ⇒ 行为等价）。

## 7. 健康项

`applied` 3/3（1110177）、7/7（1110171）；`failed=0`、`missing=0`、`env_warn=0`、`bad=[]`；
`exceptionDetails`：无（`renderErr=null`）；`__glowErrors` 在 board 页 **`typeof === 'undefined'`** ⇒ 记 `null`（不是 `[]`）；
控制皮肤 `applied` 5/5、5/5、7/7、2/2、4/4，全部 `failed/missing/env_warn=0`。
浏览器卫生：每轮 `taskkill /T /F` + `left_after=0` + `PORT_LISTEN=0`。

---

## 8. task-59 (c) 段：用源 cube 重建环境辐照 —— **已实现 + 默认 OFF；三段式 A/B 与预测相反（更暗）⇒ 已回闸**

**钉**：viewer.js 终版 **`8B8E80213F5C0CA8`**（376,205 B / 5001 行 / `node --check` OK）。
中间版：`E028EB9121D61D23`（首版，**有缺陷，见 8.1**）、`D40843F2248A795E`（花括号修复）、改前 `40618CC0FF433C3F`。
备份：`%TEMP%\wsv_bak_task59c_20260919_171502.js`（= `40618CC0FF433C3F`）。manifest/adapter/board/注册表未动。

### 8.1 首版缺陷（我自己抓到并已修）+ **三条自查护栏的正面证据**

首版把 `lights_fragment_maps` 里那道 `#if defined( … ENVMAP_TYPE_CUBE_UV )` 门**整段删掉**、只留 `iblIrradiance += q_iblIrrSrc(...)`
（`uIrrOn=0` 时返回 0）。结果：**默认态直接变黑**（OFF 帧 ≠ 锚，`p50 0.0112` vs 基线 `0.1232`，肉眼为纯黑剪影）。
另有一个更早的纯语法错（插入函数时多留一个 `}` ⇒ GLSL 花括号不配平 ⇒ 全材质编译失败、画面只剩背景）。
**修正**：改为 **`mix( 原 getIBLIrradiance(...), q_iblIrrSrc(...), uIrrOn )`**（保留门与原调用）——
`uIrrOn=0 ⇒ mix(a,b,0.0) ≡ a`（逐值等于原来）；`uIrrOn=1 ⇒ 替换`（不叠加、不双计能）。修正后 OFF 帧 = 锚（逐字节）。

| 护栏 | 做法 | 本轮抓到什么 |
|---|---|---|
| **A. GLSL 花括号配平自查** | 脚本按 `iblFn` 区间统计 `{`/`}` 并断言相等（本轮 `4/4`） | 抓到"多留一个 `}`" ⇒ 全材质编译失败、画面只剩背景 |
| **B. 空画面即中止** | 测量脚本对 OFF 帧求掩模，`mask_px==0` ⇒ 打印 `RENDER_EMPTY` 并**立即中止本页** | 抓到 A 造成的"只剩背景"；否则会拿空掩模继续算出一堆无意义读数 |
| **C. 默认锚逐字节门（N0）** | 每次改动后**同 harness** 先取默认 OFF 帧，必须**逐字节等于**改前锚 | 抓到首版"整段删门"⇒ 默认变黑（`p50 0.0112`）；修正后 = 锚 `403d89842b145e3c` ✓ |

⇒ **"默认 OFF ⇒ 零回归"不是声明，而是被这三条门强制出来的**：三类缺陷各被其中一条拦下。

### 8.2 ★ 关键发现：**本链的环境辐照并不缺**（修正 task-59 §1 的推断）

首版"把原项换掉"就**变黑**，修正版把原项换成源 cube 重建（②）也**明显变暗** ⇒
**原来的 `getIBLIrradiance` 一直在贡献可观的漫反射**（即 `ENVMAP_TYPE_CUBE_UV` 门在本链**成立**：
来自 `scene.environment` 那套**中性 PMREM 棚**，由 `envMapIntensity` 门控）。
⇒ task-59 诊断"环境漫反射 ≈ 0 / 结构性缺失"**不成立**；准确说法：**环境漫反射存在，但来自"非源的中性影棚"，且比源 cube 的平均辐照更亮**；
真正缺的是**源的 SH/天空预算**（`u_env_sh` / `u_ambient×u_char_ambient` / `t_realtime_env_spec`）—— 运行时 cbuffer ⇒ **接不上**。

### 8.3 三段式 A/B（1110171，同页；N=5；bg=`__primShow(-1)`）

| 读数 | ① OFF（=锚 `403d89842b145e3c`） | ② 只辐照 `4a8f3fab06e412ff` | ③ 辐照+BRDF `e5c1f05a29d3da0a` | ④ 只 BRDF `77f4941bddf94a10` |
|---|---|---|---|---|
| `p50` | **0.1232** | 0.0289（**−76.5%**） | 0.0278 | 0.1223 |
| `p95` | **0.4865** | 0.4127（−15.2%） | 0.4124 | 0.4593 |
| `>0.5` | **3.394** | 1.307（−61.5%） | 1.305 | 1.995 |
| `>0.75` | 0.273 | 0.268 | 0.268 | 0.273 |
| 暖色% | 0.106 | 0.102 | 0.105 | 0.106 |
| `mask%` | 2.449 | 2.284 | 2.283 | 2.445 |

⑤ 全关复现：`403d89842b145e3c` = ① ⇒ **可逆** ✓

**逐 prim（OFF / 只辐照 / 辐照+BRDF；mean 与 `>0.5`）**：
prim0(weapon) 0.0976/0.0755/0.0755、0.662/0.703/0.703；prim1 0.3894/0.2583/0.2548、14.204/6.174/6.229；
prim2 0.3833/0.1996/0.1905、10.372/3.168/3.105；prim3 0.3821/0.2253/0.2215、19.858/5.319/5.435；
prim4(weapon) 0.1460/0.1091/0.1091、0.993/1.202/1.202；**prim5 0.3899/0.1152/0.1049、15.736/0.339/0.324**；prim6 0.3285/0.1364/0.1245、1.025/0/0。
⇒ **所有 prim（含两个 weapon prim）都变暗**；晶体 prim `>0.5` 掉 55%~98%。

**可证伪预测判定**："补辐照 ⇒ `>0.5` 回到 ≥3.394%" **未命中**（1.307）；"prim5 `>0.5` ≥ −10%" **未命中**（−97.8%）；
"`p95 ≥ 0.4865`" **未命中**（0.4127）。回闸条款按字面（`p50` 抬 >+10% / `p95` 超基线 >5%）**未触发**——
因为实际是"更暗"而非"补过头" ⇒ 我按**实质**（画面显著更暗 + 预测全落空）**主动回闸**：恢复默认 OFF（⑤ 已验证回锚），**未上 1110177**。

**亲眼描述（`T59_sbs_grid.png` 四宫格：左上①OFF / 右上②只辐照 / 左下③辐照+BRDF / 右下④只 BRDF）**：
① 是**深青黑金属 + 可见银白晶体碎片 + 暖金色边缘高光**；②/③ **整体压暗、银白碎片失去亮度、金色边缘几乎消失**（不是变亮）；④ 与①接近。
⇒ 与数字一致：**源 cube 重建的辐照比原本那份中性棚辐照暗得多**，替换后画面更暗。

### 8.4 诚实结论与建议

1. **(c) 已实现、可切换、默认 OFF、零回归**（OFF 帧 = 锚，逐字节；`fragIrrFn/fragIrrMix/fragGateKept` 自证 true；
   `approx:true` + `approx_basis`（含 cube 名与源侧行号）在开关返回值与探针里都标注）。
2. **但 (c) 不能作为"让两把皮肤更接近源"的手段**：本链原本就有一份（非源）环境辐照且更亮 ⇒ 用源 cube 替换只会更暗；
   而"源 SH/天空预算"是运行时 cbuffer ⇒ **不可得** ⇒ **环境预算无法做成源级**，标 **`unresolved`**（本次已给量化）。
3. **`uIrrLod` 扫描（0..7）—— lead 裁决：不跑**。理由（采纳）：那是**重建参数、不是源值**，用户明令"不增加人工参数"；
   它只能给出"亮度上限"，**无法**变成源依据 ⇒ 不做，避免制造"看起来像源值"的假依据。
4. **方向已转："环境是什么"** —— lead 已派 **env-auditor 做 task-60（只读）**：查 `t_realtime_env_spec`(t8) / `t_env_spec_array`(t6)
   在源侧是**按名绑定的资产**还是**运行时全局天空**（含"已排除 N 种写法 / M 容器 / K 行"的零命中证据），并列出该族 c159 的**全部环境类槽位**（已绑 / `unresolved`）。
   **我不重复这份工作**（不自己去找资产）；若它找到 t8/t6 资产 ⇒ 那才是"环境源化"的唯一可做入口，届时按 lead 的 GO 再动手；若无 ⇒ 把"环境预算 = 本项目硬边界"写成正式结论。

### 8.5 状态与 pin（lead 已 bump）

* `viewer.js?v=8b8e80213f5c`（= **`8B8E80213F5C0CA8`**）；`board.html` 现 **`5008117AA03BB7A0`**。
* **我停手待命**：不再改 `weapon_skin_viewer.js`、不起浏览器；等 task-60 结论。
* 收口状态（若 task-60 无资产）：**默认 OFF ⇒ 两把皮肤零回归**（1110177 锚 `9dbb3449da619f56`、1110171 锚 `403d89842b145e3c`，均与改前逐字节相同）；
  已证修复项（task-45 两项接线、task-47 晶体 BRDF、task-59 (c) 辐照重建）全部在**默认关闭的开关**后面，可用 `__cubeBright/__srcRot/__brdfSrc/__iblIrrSrc` 逐项开启对比。

