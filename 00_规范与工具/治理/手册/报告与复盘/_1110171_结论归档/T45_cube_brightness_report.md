# task-45 第 1 项报告 —— `u_cube_brightness`（材质级环境辐照增益）接线 + 单变量 A/B

作者：shader-auditor ｜ 2026-09-19 ｜ 唯一写者：`08Lifeafter wiki\assets\weapon_skin_viewer.js`

## 0. 钉（pins）

| 项 | 值 |
|---|---|
| **viewer.js 改后** | **`B9DAF9434B73ECA0`**（342,366 B / 4644 行 / `node --check` OK） |
| viewer.js 改前 | `4647CF0BE061AD81`（335,971 B） |
| 备份 | `%TEMP%\wsv_bak_task45_20260919_161517.js`（复核 = `4647CF0BE061AD81`） |
| 1110177/viewer.json | `7575FAFAD33DD670`（本项**未改**） |
| adapter / board.html | `544D3A4A1B2CC591` / `CD298607B780B2F0`（**未改**） |

## 1. 改了什么（三处 + 一处探针自证，无其它改动）

1. **L1440-1456**（`m.onBeforeCompile` 内，紧接 `uIblScale`）：逐 prim 从
   **`neox_material.json` → `primitives[i].source_uniforms.u_cube_brightness`** 取值 →
   `uCubeBrightOn = {value:(state.__cubeBrightOn===true && 值存在 && |v−1|>1e-9) ? 1 : 0}`、
   `uCubeBright = {value: 值存在 ? v : 1.0}`；同时把 `{value, source:'manifest'|'absent', prim, on}` 写入
   `m.userData.__cubeBright`。**缺失 ⇒ 不覆盖**（恒 1.0）、**不跨皮肤借值**。
2. **注入头部**：`+'uniform float uCubeBrightOn;\nuniform float uCubeBright;\n'`
3. **radiance 出口**（紧跟 `q_env *= uIblScale;`）：`'  if( uCubeBrightOn > 0.5 ){ q_env *= uCubeBright; }\n'`
4. **L2494 之后（mesh 循环之外）**：`window.__cubeBright(true|false)` = **唯一开关**（只写 uniform，不造第二状态源）
   ＋ `window.__cubeBrightProbe()`（逐 prim 回报 prim/value/source/on ＋ live 自证 `uOn`/`uB`（真实 uniform 值）
   `fragDecl`/`fragBranch`（编译源码里是否含声明与分支））。

**定性**：这是**接上一个原本永不执行的消费点**，不是新增近似。
旧代码在 `applyMaterialLayers` 里写 `envMapIntensity = env*(cube_brightness)`，但该函数在
`state.neoxReport.applied>0` 时**早退**，消费点从未运行 ⇒ 1110177 prim2 一直按 1.0 算（**少 2.74×**）。
严格局部性：`q_env` 只喂 `indirectSpecular`（本项目的 `getIBLIrradiance` 仍恒 `vec3(0)`），
故本项**只**影响环境镜面项，**不**影响 albedo / 直射光 / toneMapping / 曝光 / bloom。

## 2. 源数据事实（本轮亲自复核）

* `1110177/neox_material.json`：prim1 `u_cube_brightness = 0.71`（entry 2438，raw `8fc2353f`）、
  prim2 `= 2.74`（entry 3257，raw `295c2f40`）；prim0 无。
* `1110171/neox_material.json`：**7 个 prim 全部 ABSENT**。
* **全树扫描（38 个皮肤目录）：只有 `1110177` 拥有该值** ⇒ 本项对其余任何皮肤都是恒等。
* 键名坑：manifest 文件是 **`neox_material.json`（列表键名 `primitives`）**；
  `viewer.json` 里只有 `material_layers.per_submesh[*].cube_brightness` 的展示副本 —— 我只读前者。

## 3. 验证（单浏览器、headless、同一页、同协议；`t45_cb2.py`）

协议：`__post(false)` / `__hidePanels(true)` / `__sfxTime(0)` → 等「连续 3 帧同 sha」→ 取帧；
bg = `__primShow(-1)`（只改 `visible`，无损）；PNG 1578×902。

### 3.1 反复切换（同页五态，唯一被切换的变量 = `uCubeBrightOn`）

| 皮肤 | off1 / off2 / off3 | on1 / on2 | 结论 |
|---|---|---|---|
| 1110177 | `49c6f3adcaea235b`（**= 接线前锚点**） | `00684d16fd84bd28`（两次一致） | 可逆、可复现 ⇒ 帧差**由本接线引起** |
| 1110171 | `9b08a1134bfc484e`（**= 接线前锚点**） | `9b08a1134bfc484e`（**完全相同**） | 无值 ⇒ ON 也**逐字节恒等**（有效=假） |

⇒ **默认 OFF 与接线前逐字节相同**（两皮肤各命中各自旧锚点）；
⇒ 有值才生效、无值恒等 —— 这正是"缺失不覆盖"的实证。

### 3.2 逐 prim 归属（1110177，`__primShow(i)` 单独显示该 prim）

| prim | 源值 | 帧 | mean | p50 | p95 | >0.5 | 判定 |
|---|---|---|---|---|---|---|---|
| 0 | absent | 不变 | 0.2409 → 0.2409 | 0.2239 → 0.2239 | 0.5303 → 0.5303 | 7.274 → 7.274 | 恒等 ✔ |
| 1 | **0.71** | **变** | 0.4845 → **0.4821** | 0.5325 → **0.5305** | 0.5868 → 0.5841 | 58.736 → **58.277** | **变暗** ✔ 方向符合 |
| 2 | **2.74** | **变** | 0.3244 → **0.3301** | 0.2154 → **0.2199** | 0.3642 → **0.3763** | 0.0 → **0.23** | **变亮** ✔ 方向符合 |

1110171 的 7 个 prim 逐个测：**全部 changed=False，统计量逐位相同**。

### 3.3 其它

* `__cubeBrightProbe()`：`fragDecl=true` / `fragBranch=true`（每个接线 prim）＋ `uOn`/`uB` 与报告一致；
* `__glowErrors = []`、`renderErr = null`；settle `applied=3/3`（1110177）、`7/7`（1110171），
  `failed=missing=env_warn=0`、`bad=0`、`retry=1~2`、`exhausted=false`、`ph_source=read_time`；
* `all_green` 1.3 s（1110177）/ 3.9 s（1110171）。

## 4. 撤回：第一轮（`t45_cb.py`）作废

第一轮用 OFF(N=5) → **`__primOnly(-1)` 取 bg → `__primOnly(null)`** → ON(N=5) → OFF(N=5)，
得到 **三个不同的 sha**；而 **1110171（逻辑上恒等）也换了 sha** ⇒ 帧变化**不能**归因于本接线。
根因：**`__primOnly` 往返还并非帧中性**（把材质换成纯白 `MeshBasicMaterial` 再换回，会留下可见残差）。
故第一轮的 OFF/ON 统计（`p50 0.2829→0.2830` 等）与"back≠OFF"**全部作废**，改以 §3 的可判别设计为准。
**副产品（给 MASK 协议的修正）**：`__primOnly` 往返会改帧 ⇒ 掩码/bg 采集后**不得**把"往返后"的帧
与"往返前"的帧当同一状态比较；需 bg 时应改用 `__primShow(-1)`（只改 `visible`，无损，实测往返后逐位可复现）。

## 5. 诚实结论（含缺口）

1. 接线**有效且方向正确**：0.71 使 prim1 变暗、2.74 使 prim2 变亮，无值 prim 恒等。
2. **但视觉量级很小**：全图 MASK `p50 0.2829 → 0.2830`、`>0.5 18.242 → 18.116`（几乎不动）；
   逐 prim 相对变化仅 ±0.5%~+1.8%。原因：晶体材质在本查看器里 `metalness=0`（F0=0.079956），
   环境项只走 `indirectSpecular`，被直射/自发光/注入链稀释。
   ⇒ **本项不能当作"填平 1110177 观感差"的手段**，它只是"把源里本来就该乘的因子接上"。
3. **未做**（不在本项范围）：`u_rotate_angle`（1110177 prim1 3.09 / prim2 2.6，`uIblRot` 目前无读值、
   默认 0）、作者 mip 开关。
4. 仍 `unresolved`（写进 `__cubeBrightProbe().unresolved`）：`envMapIntensity` 实际失效、
   `u_lightmap_factor` / `u_env_day2night_exposure` 为运行时逐帧 cbuffer（无材质级源值）、
   `uIblScale` 的 0.25 无源依据（已撤到 1.0）。

## 6. 默认值裁定（lead 2026-09-19 裁决：**保持默认 OFF**）

lead 三条理由（原样收进本条）：
1. **纪律一致性**：task-45/47 一律"默认关 + 逐项开关"（用户要求"开关留给我对比"）；不因"源里有值"改默认。
2. **收益量级**：实测全图 MASK `p50 0.2829→0.2830`、`>0.5 18.242→18.116` 几乎不动，逐 prim 仅 −0.5%~+1.8%，
   不足以承担"默认帧变化"的代价。
3. **不破坏已建基线**：默认 ON 会把 1110177 锚改成 `00684d16fd84bd28`，作废本轮一串验收基线；
   保持 OFF 则锚仍是 `49c6f3adcaea235b` / `9b08a1134bfc484e`，可继续叠加第 2 项与 task-47。

⇒ **开关保留可切**：若用户要"完全按源数据渲染"，一键 `__cubeBright(true)`（+ 第 2 项的 `__srcRot(true)`）
即可，代价是 1110177 的锚点变化（单开第 1 项 = `00684d16fd84bd28`；单开第 2 项 = `58a10b0f34fce803`）。

## 7. task-45 第 2 项报告 —— `u_rotate_angle` → `uIblRot`（源 IBL 采样方向）

**钉**：viewer.js = **`57D181F1432095F3`**（348,136 B / 4707 行 / `node --check` OK；改前 `B9DAF9434B73ECA0`）。
viewer.json / adapter / board / 注册表 / `wiki_selfcheck.py` 均未动。

### 7.1 改了什么（两处 + 一处开关/探针，风格与第 1 项完全一致）

1. **L1457-1491**（第 1 项代码块之后）：读 `pr.source_uniforms['u_rotate_angle']` → `rotVal`（弧度，可为 null）；
   `uIblRotOn={value:(state.__iblRotSrcOn===true && rotVal!==null)?1:0}`；
   `uIblRot.value = (On ? rotVal : (state.iblRot===undefined?0.0:state.iblRot))`；
   `m.userData.__iblRotSrc={value,source,prim,on,manual_rot}`。
2. **mesh 循环之后**（`__cubeBright` 旁）：`window.__srcRot(true|false)` 唯一开关 + `window.__srcRotProbe()`。
3. **默认 OFF**：`uIblRot` 严格保持既有取值路径（`state.iblRot`，默认 0）⇒ 默认渲染与接线前**逐字节相同**。
   ⚠ 交互已显式化：`__iblParams({rot:N})` 写 `state.iblRot`，源开关 ON 时对有源值的 prim 不生效；
   探针每行同时回报 `manual_rot`，不会被当成假 A/B。

**源数据 / 映射证据**（本项**未**自行推断）：`1110177 prim1 = 3.09 rad`（f32@2429 / payload 2434，raw `8fc24540`）、
`prim2 = 2.60 rad`（@3248 / 3253，raw `66662640`）；1110171 全 prim **无声明**（且无参数名，0 命中）。
`u_rotate_angle ↔ uIblRot` 的等价性由**四路交叉证据**支撑（lead 侧 `ENV_IBL_spec_1110171_1110177_20260919.md` L45、
`报告_1110171_源驱动材质_P1结构复原_20260916.md` L29/L121-143、`接手核验记录_1110171…_20260916.md` L74-78、
`折射层公式复原规格_20260917.md` L46-53）：`cb0[7].w = u_rotate_angle`（材质级 `NeoxUBOLocal`@124；
weapon PS 为 `cb0[4].x`），晶体 PS 只在 **IBL 方向 sincos（L532）** 用它，**与折射链无关**。

### 7.2 验证（`t45_rot.py`，单浏览器、逐皮肤新开页面、同协议）

| 皮肤 | off1/off2/off3 | on1/on2 | 结论 |
|---|---|---|---|
| 1110177 | `49c6f3adcaea235b`（**= 接线前锚点**） | `58a10b0f34fce803`（两轮一致） | 可逆可复现 ⇒ 帧差由本接线引起 |
| 1110171 | `9b08a1134bfc484e`（**= 接线前锚点**） | `9b08a1134bfc484e` | 无值 ⇒ ON 也逐字节恒等（`effective=false`） |

`__srcRot` 回报（1110177）：prim0 `absent, rot_used=0, uRotOn=0`；prim1 `3.09 → rot_used 3.09`；prim2 `2.6 → rot_used 2.6`；
`__srcRotProbe()`：`fragRotRead=true`（编译源码里确有 `cos( uIblRot )` 读取点）、`fragCubeBrightDecl=true`。
health：`applied=3/3`、`7/7`，`failed=missing=env_warn=0`、`bad=0`、`glowErrors=0`、`renderErr=null`。

**逐 prim（`__primShow(i)`，OFF/ON 各自等连续 3 帧同 sha）**：

| prim | 源值 | changed | mean | p50 | p95 | >0.5 | >0.75 |
|---|---|---|---|---|---|---|---|
| 0 | absent | False | 0.2409 / 0.2409 | 0.2239 / 0.2239 | 0.5303 / 0.5303 | 7.274 / 7.274 | 1.24 / 1.24 |
| 1 | 3.09 | **True** | 0.4845 / 0.4842 | 0.5325 / **0.5331** | 0.5868 / 0.5852 | 58.736 / **58.977** | 0 / 0 |
| 2 | 2.60 | **True** | 0.3244 / **0.3331** (+2.7%) | 0.2154 / 0.2166 | 0.3642 / **0.3708** | 0 / **1.378** | 0 / **0.23** |

### 7.3 「无值皮肤逐字节恒等」的证据（三条独立）

1. **manifest 全树扫描**：38 个皮肤目录中**只有 `1110177`** 的 `neox_material.json` 含
   `u_rotate_angle`（以及 `u_cube_brightness`）**数值**；
2. **代码层**：`absent ⇒ uIblRot` 保持原路径（`state.iblRot`，默认 0），新增的 `uIblRotOn` **不参与任何分支**；
3. **实测**：除 1110171（7 prim 全 prim 逐位不变）外，**另 5 个皮肤新开页面实测 OFF 锚点与本轮之前记录的同协议锚点逐字节相同** ——
   `1110024 81328c8267f7211b`、`1110129 954dc1eb9748b315`、`1110145 52ac39fbd0072cc9`、`1110152 02a21f72f3264c87`、`1110165 834e01e6c0c75b0c`（5/5 match，`stable3=true`，`applied` 5/5、5/5、7/7、2/2、4/4，`failed/missing/env_warn/glowErrors=0`）。

### 7.4 亲眼描述（PNG 存于 `_target_1110171\T45ROT_1110177_*.png`）

* **prim1（浅粉白色扁平碎片，3.09 rad）**：OFF 与 ON **肉眼分辨不出**；仅 `>0.5` 由 58.736 → 58.977（+0.24 pp）、p50 +0.0006。
  ⇒ 该 prim 的亮度**不由环境镜面主导**，转 177° 在视觉上几乎看不出。
* **prim2（两枚红色晶体核心，2.60 rad ≈149°）**：两枚红块**位置不动**；左上那枚在 ON 下**多出一小块更亮的面**
  （`>0.75` 0 → 0.23%、`>0.5` 0 → 1.378%、mean +2.7%），即**高光贴片出现/变亮**，但**没有整块高光的整体迁移**。
* 诚实定性：**"方向合理"这一条我只能给到"变化只出现在环境镜面项、且只增亮不减暗"，无法用肉眼判定 149°/177° 的落点是否与源一致** ——
  因为该皮肤环境镜面在晶体亮度里占比过小（与第 1 项结论一致）。**源 cube 的六面顺序/基变换**仍为 unresolved，
  在它定证之前，"转了就对"不成立。

### 7.5 给 lead 的结论

* 第 2 项**接线有效、默认 OFF 安全、值来源唯一（manifest）**；但**与第 1 项同样的病**：
  **源 IBL 在晶体亮度里占比很小 ⇒ 只接 `u_rotate_angle`/`u_cube_brightness` 无法改变 1110177 的观感**。
  真正的杠杆在 **task-47（晶体 BRDF：`metal = saturate(lerp(u_base_metallic,u_crystal_metallic,w))` 等）**
  —— 现在晶体被硬编成 `metalness=0`，环境镜面被 F0=0.079956 压住。
* 若用户要"完全按源数据渲染"：`__cubeBright(true)` 与 `__srcRot(true)` 各一键切换；
  同时开两个开关时 1110177 锚点会与 `49c6f3adcaea235b` 不同（第 1 项单开 = `00684d16fd84bd28`，第 2 项单开 = `58a10b0f34fce803`）。

## 8. task-45 第 3 项（作者 mip）—— **只读可行性核查结论：可做，但只对 1110171 的两个 cube；按 lead 排程定级"低优先、task-47 之后再看"**

### 8.1 记录齐备性（按 lead 纠正的口径：看 JSON，不看 PNG 有无）

| 对象 | `cube_faces_mips.json` | 逐 (face,mip) 记录 |
|---|---|---|
| `1110171` | **有** = `EC6ED697609EB8F4`（与 lead 同） | `qiangpi` 与 `car_studio01` 均为 **face 0..5 × mip 0..7 = 48/48**（每级 `size` 128/64/32/16/8/4/2/1、`mean[3]`、`sha`） |
| `1110177` | **无该文件** | —— |
| `fashion_qiangpi`（1110171 亦有此 cube） | JSON 中**无该键** | 盘中只有 `_m0.png` ⇒ **无 mip 记录 ⇒ 必须 unresolved / 不接线** |

### 8.2 布局复核（与 lead 给的 face-major 口径一致）

`qiangpi.dds` = 524,408 B = **128 + 6×87,380**；而 `87,380 = (128²+64²+32²+16²+8²+4²+2²+1²)×4`
⇒ **face-major、每面 8 级、B8G8R8A8_UNORM** 的算术完全吻合（面 i base = `128+i×87380`，面内 mip m 偏移 = `Σ_{k<m} w_k·h_k·4`）。
盘中 `faces/` 亦已有全部 **48 张逐 mip PNG**（`_f{i}_m{k}.png`，IHDR 复核 128²→1²、colortype 6/8bit），另有旧版 `faces.bak_20260917_081053/`。

### 8.3 **实现通路已定证（查 vendored three r180 源码 `three.module.min.js` @273307 `uploadCubeTexture`）**

* three r180 的 cube 上传分两条路：
  * 面 `image[i]` 是**普通图片** ⇒ 只 `texImage2D(face, 0, …)` 上传 level 0，再由 GPU `generateMipmap` 生成；
  * 面 `image[0].isDataTexture === true` ⇒ 走 **DataTexture 路**：先 `texStorage2D(cube, levels, …)`（`levels = mipmaps.length + 1`），
    逐面 `texImage2D(face, 0, …, h[t])`，**再逐级上传 `texture.mipmaps[n].image[face].image`**；
  * 另：若是 CompressedTexture，则逐面 `image[face].mipmaps` 也被逐级上传。
* ⇒ **作者 mip 可以在 three 内部上传，无需 raw-GL 旁路**：构造 `CubeTexture{ image:[6×DataTexture(m0, RGBA)], mipmaps:[7×{image:[6×DataTexture(m_k)]}], generateMipmaps:false }` 即可。

### 8.4 自校验口径（已定证，可写成 48/48 断言）

`cube_faces_mips.json` 的 `sha` 不是文件哈希：实测 **= 解码后 RGB（去 alpha）裸像素的 sha256 前 12 hex**
（`qiangpi_f0_m0` → `b5422ed3aace`、`m7` → `0fbe4f8632c3` **双向命中**）；`mean` = RGB 三通道均值四舍五入
（实测 180.06→180、189.05→189、209.0→209）。
⇒ 实现时对每个 (cube,face,mip) 断言 `sha12(RGB裸像素)` 与 `mean` 双双命中，命中 48/48 才允许开开关，否则回落 unresolved。

### 8.5 定级与待办

* **可行**，但只覆盖 **1110171 的 qiangpi(weapon prim0/4) + car_studio01(晶体 prim1/2/3/5/6)**；`fashion_qiangpi` 与 **整个 1110177** 无记录 ⇒ 不接线。
* lead 裁定：**标"可做、低优先、task-47 之后再看"**。理由（我同意）：晶体 `metalness=0` 时环境项占比过小，
  mip 只改 `textureLod` 的 LOD 取值，收益远低于 task-47。
* 本项**尚未动一行代码**（浏览器已交 viewer-auditor，我停手待命）。

