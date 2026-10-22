# task-47 只读准备笔记（未动一行代码）+ 三条与 `RX_BRDF_wiring_spec` 相关的**新证据**

作者：shader-auditor ｜ 2026-09-19 ｜ 状态：**只读**（viewer.js 仍 = `57D181F1432095F3`，本轮未改）
依据：`RX_BRDF_wiring_spec_20260919.md`（下称 spec）+ 本轮亲测（hash / alpha / manifest 字段 / three 源码）。

---

## A. 三条新证据（都会改变 task-47 的可接线范围）

### A1. **两个 DetailMap 都可用 manifest 自己记录的哈希逐字节定证**（spec 的 U2 需要收窄/撤销）

| 文件 | 字节 | sha256（前 32） | manifest 里的记录 | 判定 |
|---|---|---|---|---|
| `1110171/src_tex/crystal_bump_n_uvva.png` | 254,853 | `a2625d7757c72099d08ae676d26a04d9` | prim1/prim5 `sha256` **= 同值**，`confidence=high`，`binding_basis=res\063.fpk#3747 …` | **已接受绑定**（基准） |
| `1110177/src_tex/crystal_bump_n_uvva.png` | 254,853 | **同上，逐字节相同** | prim2：`file=null / confidence=none / sha256=null`，但 **`source.sha16 = a2625d7757c72099`** | **内容与已接受绑定完全相同** ⇒ 可证可解析 |
| `1110177/src_tex/crystal_bump_n02.png` | 162,075 | `2c5bd70ff4877e13b7bade53fdf7650d` | prim1：`file=null / confidence=none`，但 **`source.sha16 = 2c5bd70ff4877e13`** | **内容与 manifest 记录的 source.sha16 完全一致** ⇒ 可证可解析 |

* alpha 实测（决定 `w = m²·D.a` 能否退化为 `w = m²`）：**三个文件 A ≡ 255（min=max=255，uniq=1）** ⇒ `D.a ≡ 1.000` ✅
  （spec §1.2 的 `crystal_bump_n_uvva` 结论成立，且**同一结论对 `crystal_bump_n02` 也成立**，spec 未测后者。）
* ⚠ 结论边界：`confidence=none` 是**manifest 的接受状态**，属于 lead 的 manifest/注册表辖区，**我不改**。
  ⇒ 请 lead 裁定：这两个 slot 是否可视为"已定证可接线"；若是，manifest 由其所有者补 `file/sha256`，我只读它。

### A2. **1110171 prim5 的 `u_crystal_metallic` 两个源冲突（必须裁定，否则 task-47 会取错值）**

| prim | `crystal_params` | `source_uniforms`（原始字节） | 备注 |
|---|---|---|---|
| 1110171 prim1/2 | 1 | 1（`01000000`, entry 3813/4628, conf high） | 一致 |
| 1110171 prim3 | 0.75 | 0.75（`0000403f`, entry 5434） | 一致 |
| **1110171 prim5** | **1** | **0.75**（`0000403f`, entry 2498, payload 2503, conf **high**） | **冲突** |
| 1110171 prim6 | 0.75 | 0.75（`0000403f`, entry 3260） | 一致 |
| 1110177 prim1 | 0.6 / 0.95 | 0.6（`9a99193f`, entry 2497）/ 0.95（`3333733f`, entry 2506） | 一致 |
| 1110177 prim2 | — / 1 | — / 1（`01000000`, entry 3316） | 一致 |

* `crystal_params` 来自派生产物 `_known_loop/c159_params_001265.json`；`source_uniforms` 带 **entry/payload 偏移 + raw hex + confidence**（原始证据级）。
* **强烈倾向 `source_uniforms` 的 0.75**：prim5 与 prim6 都标 `mtl_idx=3`，且兄弟 prim6 两个源都是 0.75；prim5 的 raw hex 明写 `0000403f`=0.75。
  ⇒ 若 lead 同意，task-47 一律**只读 `source_uniforms`**，并在探针里把"两源不一致"显式报出（不静默取一）。
* 另注：`01000000`（i32=1）与 `0000403f`（f32=0.75）**类型不同**，说明审计对 1.0 的记录方式与其它值不同 —— 这一条我**未定证**，标 unresolved，不影响 0.75 的判定。

### A3. **`spec` 因子对这两个皮肤是恒等**（缩小 task-47 的实际改动面）

* 两个皮肤**所有晶体 prim** 的 `u_crystal_specular = 1`；`u_base_specular` 仅 1110177 prim2 有 = 1。
* 现有链的等效 `spec` 现值 = 1.0（因为现有 patch 把 `F0_diel` 直接设成 `0.079956` = `1.0 × 0.079956`）。
  ⇒ `spec = lerp(现值=1, u_crystal_specular=1, w) = 1` **恒为 1** ⇒ **F0 不需改**，spec §2.4 的注入②对本轮两皮肤无收益（可留待有 `base_specular≠crystal_specular` 的皮肤再上）。
  ⇒ **task-47 的真实杠杆 = metalness 插值这一条**。

---

## B. 接线设计草案（**未落地**，等 GO；口径：默认关 + 逐项开关 + 缺失不覆盖 + IBL 就绪联动）

### B1. 目标式（按 spec §1.1/§2.1）

```
w      = saturate(Tex0.r)² × DetailMap.a      ; 本项目 D.a≡1 ⇒ w = m²
metal  = saturate( lerp(<现值>, u_crystal_metallic, w) )   ; <现值> = 该 prim 的 u_base_metallic；缺失 ⇒ 0.0（= 现有硬编值）
spec   = lerp(<现值=1.0>, u_crystal_specular, w)           ; 本轮恒 1 ⇒ 不注入（report 里说明）
F0     = lerp(spec × 0.079956, albedo, metal)              ; three 侧 = mix(vec3(0.079956), diffuseColor.rgb, metal)
diffuse= albedo × (1 − metal)                              ; three 自带，metalnessFactor 传对即可
```

### B2. 落地点（三处，均在现有 `onBeforeCompile` 内）

1. **计算 `q_w` / `q_metal`**：在现有晶体链注入处（`<map_fragment>` 之后，那里已有 `q_mm = clamp(Tex0.r,0,1)`）追加
   `q_w = q_mm*q_mm`（若有 DetailMap 采样则乘其 a）；`q_metal = clamp(mix(uBaseMetal, uCrystalMetal, q_w), 0.0, 1.0)`；
   `q_diffW = 1.0 - q_metal`。
2. **改 `lights_physical_fragment` 的三行**（要用"同一 chunk 多次替换、只重插一次"的新 patch 变体，**现有 `patch()` 只能对同一 chunk 打一次**）：
   * `material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );` → `… * q_diffW;`
   * `material.metalness = metalnessFactor;` → `material.metalness = q_metal;`
   * `material.specularColor = mix( vec3( 0.079956 …), diffuseColor.rgb, metalnessFactor );` → `…, q_metal );`（spec 因子恒 1 故不动 0.079956）
   （**必须逐串校验命中数 = 1 且 include 命中 = 1**，否则记 `__patchLog` 并抛错 —— 沿用现有 `patch()` 的纪律。）
3. **uniform + 逐 prim 值**：`uBrdfOn`(0/1)、`uBaseMetal`、`uCrystalMetal`；值一律读 `source_uniforms`（见 A2）；
   **`uCrystalMetal` 缺失 ⇒ 整 prim 不接线**（金属度保持 0）；`uBaseMetal` 缺失 ⇒ 用 0.0（现值）。

### B3. 就绪门（spec 风险 1 的硬要求）

* 只有该 prim **当前**处于 `envMode==='source_ibl'` 且 `uCustomIbl` 六面就绪时，才把 `uBrdfOn=1`；否则 `uBrdfOn=0`（metalness 保持 0）。
* 实现位置：与现有 `pendingHide` 恢复/`__iblRebindPending` 重建同批（重建时 `onBeforeCompile` 会重跑，uniform 自然反映当时就绪状态）；
  另在 `__brdfSrc(true)` 时按"当前就绪"逐 prim 设值，并在探针里回报 `ibl_ready` 与 `on`。

### B4. 开关 + 探针（沿用第 1/2 项已验证的形状）

* `window.__brdfSrc(true|false)`：唯一开关，只写 uniform，不造第二状态源。
* `window.__brdfSrcProbe()`：逐 prim 回报
  `{prim, w_mode:'m2'|'needs_detailmap', base_metal, crystal_metal, value_source:'source_uniforms', conflict:true|false,
    ibl_ready, on, uBrdfOn_live, uBaseMetal_live, uCrystalMetal_live, fragDecl, fragMetalPatch, fragDiffPatch}`。

### B5. 验收判据（spec §5 可证伪预测 + lead 门槛）

* 顺序：**先 1110171**（`w` mean 0.173 / >0.5 仅 4.0%）→ 再 **1110177 prim2**（`w` mean 0.724 ⇒ 近乎整面金属化，风险高）。
* 五读数：`p95 / >0.5 / >0.75 / 暖色% 上升`，`p50 基本不变`；门槛 `R1≥2.5% ∧ R2≥0.10% ∧ R3>0 ∧ |Δp50|≤0.02`。
* 负控：开关 OFF ↔ ON 的 sha 必须**可逆可复现**（同页 off→on→off→on→off）；OFF 锚必须 = 接线前锚点。
* 正控：`on` 时逐 prim `>0.75` 必须上升；若 `p50` 明显下降 ⇒ IBL 门失效（metalness 抬升而环境未就绪）。
* 眼证：逐 prim OFF/ON PNG + 文字描述（不得只凭数字）。

---

## C. lead 裁决（2026-09-19，已全部落定；**不再是卡点**）

| # | 事项 | 裁决 | 执行影响 |
|---|---|---|---|
| **C1** | `1110177` 两个 DetailMap（`crystal_bump_n_uvva.png`@prim2 / `crystal_bump_n02.png`@prim1）的 manifest 接受状态为 `confidence=none` | **内容层已定证、两个 prim 都可接线**（证据级别写 `content_verified_by_manifest_hash`）。**manifest 的 `file/sha256` 补齐推迟到 task-47 A/B 之后**，由 lead 作为独立小改动做（理由：补了会让 `uHasDetail` 由 0 变 1 ⇒ 同一轮 A/B 多一个变量）。**我全程不碰 manifest。** | 且因 §E2.0（`w = q_mm×q_dd`，两路径同值）⇒ **1110177 prim1 无需任何特判**，接线与 A/B 不被 manifest 状态阻塞 |
| **C2** | 1110171 prim5 `u_crystal_metallic`：`crystal_params=1` vs `source_uniforms=0.75`（raw `0000403f`, entry 2498, payload 2503, conf high） | **取 0.75**（原始字节级证据；prim5/prim6 同 `mtl_idx=3`、兄弟 prim6 两源皆 0.75 ⇒ `crystal_params=1` 判为解析产物） | 探针**必须**显式报 `conflict:true`，不许静默取一；lead 会把该冲突写进 manifest 备注（收工后） |
| **C3** | `spec` 因子本轮恒 1（A3：`u_crystal_specular=1` 全部、`u_base_specular` 仅 1110177 prim2 且=1） | **本轮不注入 spec 因子**，结论写进报告（留待 `base_specular≠crystal_specular` 的皮肤） | 真实杠杆只有 metalness 插值一条 ⇒ 改动面 = 2 行 + 1 段链内赋值 |
| **C4** | P3 回闸条款 | 1110177 prim2（`w` mean 0.724）**若 `p50` 明显下降（>0.02 或判断"变黑"）立即回闸并报 lead**，不硬推 | 写进 §F 的 P3 判据 |

## D. 顺带发现（不在 task-47 范围，登记不实现）

* `1110171 prim6` 的 `u_crystal_roughness = 0.12`（`8fc2f53d`, entry 3251, `source_uniforms` 有、`crystal_params` 无）**无消费点** ⇒ 现有链 roughness 恒 1.0 / `ParamMap.R`；
  与"高光不足"可能有关系，但**未定证 ⇒ 本项不接线**，仅登记。
* task-45 第 3 项（作者 mip）维持"可做、低优先"（见主报告 §8）。

---

## E. 逐处行文（**已对着 vendored 构建逐字核过**；落地时按此写，命中数必须 = 1）

### E1. **纠正设计草案的一处错（lead 已采纳并写进报告）**：three r180 **没有 `material.metalness` 这个字段** ⇒ **"三条线 → 两条线"**

**定证方式（可复核）**：对 `assets\vendor\three\three.module.min.js` 全文计数 —— `metalnessFactor` 出现 **6 次**、`material.metalness` 出现 **0 次**。

在 `assets/vendor/three/three.module.min.js` 里全文搜 `metalnessFactor` 共 **6 次**、`material.metalness` **0 次**：

| # | 位置 | 形态 | 是否本轮路径 |
|---|---|---|---|
| 1 | chunk `lights_physical_fragment` | `material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );` | **★ 要改** |
| 2 | 同 chunk（`#ifdef IOR`+`#ifdef USE_SPECULAR` 内） | `material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );` | 否（我们的材质无 IOR/USE_SPECULAR；且 `0.04` 那条 patch 命中=1 已反证走的是 `#else`） |
| 3 | 同 chunk（IOR 分支） | `material.specularColor = mix( min( pow2( … ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );` | 否 |
| 4 | 同 chunk（`#else` 分支） | `material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );` + `material.specularF90 = 1.0;` | **★ 要改**（现有 `dielecticF0` patch 已把它改成 `0.079956`） |
| 5/6 | chunk `metalnessmap_fragment` | `float metalnessFactor = metalness;` / `metalnessFactor *= texelMetalness.b;` | 否（定义处，不动） |

⇒ **metalness 在 r180 只通过"漫反射权重"与"specularColor(F0) 混合"两条线影响着色**，且 **`specularF90` 在非 IOR 分支恒 `1.0`**。
⇒ **task-47 只需改 2 行**（原草案写的第 3 行 `material.metalness = …` 不存在，删掉）——**改动面比草案更小**，正好与源 `L548`/`L551` 一一对应。

### E2. 落地改动清单（**未执行**；`<...>` 为待定数值源）

#### E2.0 **重大简化（对着现有链读出来的）**：`w` 已经有一半算好了，**不需要新绑任何贴图**

现有晶体链注入 `injC`（viewer L1735-1746，紧跟 `#include <map_fragment>`、**main 作用域**）已经声明：

```
vec3  q_T  = diffuseColor.rgb;                                        // 或 vec3(1.0)（无 t_basecolor）
float q_mm = clamp(texture2D(uCrystalMask, vMapUv).r, 0.0, 1.0);     // = m = saturate(Tex0.r)  ← 源 L393
float q_dd = (uHasDetail>0.5) ? (clamp(texture2D(uDetailMap,vMapUv).a,0,1) * q_mm) : q_mm;
                                                                      // = m·DetailMap.a          ← 源 L405 (r8.w)
```
⇒ **源的 `w` 就是这两者的乘积：`w = m²·D.a = q_mm × q_dd`**（`L438: mul r1.w, r6.x, r8.w`）——
* DetailMap 绑定时：`q_dd = D.a·m` ⇒ `q_w = m²·D.a` **逐字等于源式**；
* DetailMap 未绑定时（`uHasDetail=0`）：`q_dd = m` ⇒ `q_w = m²`，即 `D.a≡1` 的已证退化式（A1）。
**两种情况都成立** ⇒ 无需绑定/采样新贴图，**也无需在 1110177 prim1 上做任何特判**（该 prim 的 DetailMap 缺失与否只影响 `q_dd` 的取值路径，而两条路径在本资源下同值）。

#### E2.1 改动表

| # | 位置 | find（逐字） | replace |
|---|---|---|---|
| 1 | 注入头部（IBL 块，**所有族**） | — | `uniform float uBrdfOn;\nuniform float uBaseMetal;\nuniform float uCrystalMetal;\nfloat q_metal = 0.0;\nfloat q_diffW = 1.0;\n`<br>（全局常量初始化合法；**默认值 = 不金属化 ⇒ 未接线 prim 与现状一致**） |
| 2 | `injC` 末尾（晶体链内，**赋值而非声明**） | — | `q_metal = mix(0.0, clamp(mix(uBaseMetal, uCrystalMetal, clamp(q_mm*q_dd,0.0,1.0)), 0.0, 1.0), uBrdfOn);`<br>`q_diffW = 1.0 - q_metal;` |
| 3 | `lights_physical_fragment`（**同一 chunk 只能打一次 ⇒ 必须换成 `patchMulti`，且替换串按族分叉**） | **weapon**：`material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );` | weapon：`material.specularColor = mix( vec3( 0.079956 ), diffuseColor.rgb, metalnessFactor );`（= 现状不变） |
| 4 | 同上 | **crystal**：同上那条 **+** `material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );` | crystal：`material.specularColor = mix( vec3( 0.079956 ), diffuseColor.rgb, q_metal );` **＋** `material.diffuseColor = diffuseColor.rgb * q_diffW;` |
| 5 | 逐 prim JS | — | 读 `pr.source_uniforms`：`uCrystalMetal` 有值 且 `w` 可算 ⇒ 该 prim 可接线；`uBaseMetal` 缺失 ⇒ `0.0`（现值，**不借值**）；`uCrystalMetal` 缺失 ⇒ `uBrdfOn` 永远 0；`m.userData.__brdfSrc={...}` |
| 6 | `patch()` 助手 | 现版本对同一 chunk 只能打一次 | **新增 `patchMulti(name,[[find,repl],…],tag)`**：对 **chunk 副本**逐个替换（每串命中必须=1，否则记 `__patchLog` + `throw`），再一次性替换材质里的 `#include <name>`（命中必须=1）。**原 `patch()` 保留** |
| 7 | 循环之后 | — | `window.__brdfSrc(on)` + `window.__brdfSrcProbe()` |

**为什么这样分族是安全的**：`isWeapon` 在 IBL 块内已可用（`_isWeaponFam` 就是它）；weapon 保持原串 ⇒ 行为与今天逐字节相同；crystal 引用的 `q_metal/q_diffW` **一定在头里有定义**（默认 0.0/1.0），即使某个晶体 prim 的链注入被跳过（无 Tex0）也**能编译且行为=现状**，绝不会出现"未声明标识符"。

### E3. 就绪门的确切语义（负控要用）

* `uBrdfOn` 只在 **该 prim 当前 `envMode==='source_ibl'` 且 `uCustomIbl` 六面就绪** 时为 1；否则 0 ⇒ `q_metal ≡ 0` ⇒ 与接线前逐像素相同。
* JS 侧判定复用现有事实源：`state.__iblGate[name].ready` / `rec.envMode`；**不新增第二状态源**。
* `__brdfSrc(true)` 只把 `state.__brdfSrcOn=true` 并**按当下就绪态**逐 prim 写 `uBrdfOn`；**不**强制把未就绪 prim 打开。

## F. 负控 / 正控计划（**做完必须逐条给读数**）

| id | 控制 | 判据 |
|---|---|---|
| **N0** | 默认 OFF 锚点 | 1110177 = `49c6f3adcaea235b`、1110171 = `9b08a1134bfc484e`，**逐字节相等**（各 3 次） |
| **N1** | 同页反复切换 off→on→off→on→off | 全部 off* 同 sha 且 = 锚点；全部 on* 同 sha；OFF 期间**任何** prim 不得变化 |
| **N2** | 同 ON 状态内的"无值 prim 负控" | 1110177 prim0（weapon，无 crystal_metallic）在 ON 下逐位不变；1110171 若有 prim 缺值同样必须不变 |
| **N3** | **IBL 未就绪窗口负控**（最关键） | 窗口期（`envMode!=='source_ibl'`）调 `__brdfSrc(true)`：帧必须**逐字节不变**（因为全部 `uBrdfOn=0`）；settle 后再调同开关必须**变** |
| **N4** | 缺值皮肤恒等 | **全树扫描（34 个有 `neox_material.json` 的皮肤）实测：`u_crystal_metallic` 有值的只有 2 个皮肤** —— `1110171`（p1=1, p2=1, p3=0.75, **p5=0.75**, p6=0.75）、`1110177`（p1=0.95, p2=1）；`u_base_metallic` 仅 `1110177` p1=0.6 ⇒ **其余 32 个皮肤必然逐字节恒等**（无值 ⇒ 整 prim 不接线）。另加实测控制组 5 皮肤（`1110024/1110129/1110145/1110152/1110165`）锚点与旧记录相同 |
| **P1** | 正控·1110171（`w` mean 0.173，低风险） | `>0.75` / `>0.5` / `p95` / 暖色% **上升**，`p50` 基本不变；门槛 `R1≥2.5% ∧ R2≥0.10% ∧ R3>0 ∧ |Δp50|≤0.02` |
| **P2** | 正控·内部排序 | 1110171 prim1/2（`u_crystal_metallic=1`）的抬升幅度 **>** prim3/6（`0.75`）；prim5 取 0.75（C2） |
| **P3** | 正控·1110177 prim2（`w` mean 0.724，高风险） | 同上五读数；**回闸条款（lead 确认）**：若 `p50` 明显下降（`>0.02`）或判定"变黑" ⇒ **立即回闸并报 lead，不硬推** |
| **P4** | 自证 | `__brdfSrcProbe()`：`fragDiffPatch=true`、`fragSpecPatch=true`、`fragDecl=true`、live uniform 值 = 报告值；`__patchLog` 全部 `ok:true` 且命中=1 |
| **P5** | 流程 | 每次状态"等连续 3 帧同 sha"再取帧；**bg 一律用 `__primShow(-1)`**（禁用 `__primOnly` 往返，见主报告 §4）；逐 prim 用 `__primShow(i)`；每状态存 PNG 并**亲眼描述** |

## G. 落地时序（等 lead GO）

1. 备份 → 改 E2 的 6 处 → `node --check` → 报**新 sha16 + 逐处行文**给 lead；
2. N0/N1/N2/N3/N4 + P1（1110171）一轮脚本跑完 → 报读数；
3. lead 点头后再开 P3（1110177 prim2，高风险）；
4. 全程只用一个浏览器进程、只杀自己的 profile；**任何测量在飞时不改 viewer.js**。
