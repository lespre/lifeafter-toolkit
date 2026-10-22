# SFX「闪一下 / 一大块 / 很劣质」修复报告 — task-53（chain-auditor）

## 0. 状态：**代码已改完并语法通过；浏览器侧前后对照因 lead 同期改 viewer.json 而跨版本，不能归因 ⇒ 未标完成**

| 产物 | 读数 |
|---|---|
| adapter 改前 | 57,692 B / sha16 `1cd4ac5454d1f27a`（= 基线 harness 的 pin） |
| adapter 改后 | 69,455 B / sha16 `a19f8b4551dbde49`（= AFTER harness 的 pin） |
| 备份 1 | `weapon_skin_sfx_adapter.js.bak_task53_20260918_234555`（56,891 B 内容态；含枚举注释版） |
| 备份 2 | `weapon_skin_sfx_adapter.js.bak_task53ps_20260918_234933` |
| `node --check` | 每步后均 **OK** |

## 1. 逐处改动（行号为改后文件）

| # | 位置 | 原文 | 新文 |
|---|---|---|---|
| 1 | 常量区（`var LIVE_RECS` 之前） | — | 新增 `SPRITE_FIX=true` / `SPRITE_CLAMP_K=0.60` / `SPRITE_ON=null` / `BLEND7='normal'` / `LIVE_SFX` + 依据注释 |
| 2 | `var BLEND = {...}` | `{0:'normal',2:'additive',5:'additive',8:'additive'}` | 加 `7: BLEND7`（=normal）并注明值表 unresolved、禁止用观测分布反推 |
| 3 | `function texFor` 之前 | — | 新增 `weaponDiag()`（缓存 500ms 的武器包围盒对角线）与 `clampQuad()`（只做上限钳制） |
| 4 | Sprite 创建后 | `group.add(sp); sprites.push(sp);` | 追加 `.spr` 描述符 fetch + 帧矩形解析（`ud.sliced/rects/sheet/frames/slice_reason`，**候选级**） |
| 5 | Sprite 每帧 | `sp.scale.setScalar(Math.max(d.radius * (sc?..:1), 0.02));` | 先按 `frame_index` 设 `map.repeat/offset`（切片生效），再用 `clampQuad()` 设 scale 并记录 `quad_raw/quad_clamped` |
| 6 | 粒子每帧 | `sp.scale.setScalar(Math.max(1.2*..., 0.05));` | 同上经 `clampQuad()` |
| 7 | 精灵创建 userData | `{kind,nodeName,start,life,radius,color,ss,se,scale,ready}` | 追加 `texName` / `blendUsed`（探针用） |
| 8 | `var rootObj = ctx.root...` 之前 | — | 新增 `LIVE_SFX={sprites,systems,fixedTime,weaponDiag,nodeSummary}`（供只读探针） |
| 9 | `WikiSfxAdapter.__probe` 之前 | — | 新增 `__sfxDiag()`（只读：逐节点 quad/比值/切片/blend/寿命/存活数）与 `sprites(on)` 精灵层独立开关 + `__spriteOn()` |
| 10 | 粒子 tick 分支（**靶子 1**） | `updateParticles(sys,t);` 后直接结束 | **新增 `PS_SINGLE_QUAD` 单四边形回退**：源 `rate<=0` 但节点有贴图/时间窗 ⇒ 渲染 1 个四边形（按该节点 color/scale/radius，经钳制），把『数据说可渲染、运行侧从不出现』补上 |

## 2. 靶子 1（ParticleSystem 从未渲染）：机制已定位 + 已修 + 探针已证

- **机制**：适配器对 `tag=ParticleSystem` 只走 `updateParticles()`；该函数按源 `ParticlesPerSecond` 出生 ⇒ **源无速率(rate=0)时永不生成粒子**，节点虽 `drivable=true` 却全时间轴不可见。另有 `!n.texture_candidate` 的分支把无贴图节点标 `drivable:false`（不伪造出生）。

- **已改**：`PS_SINGLE_QUAD=true` 回退（见改动 10），不伪造出生率、不引入强度系数。

- **探针证据（改后）**：`__sfxDiag()` 逐节点读数显示 6 个 rate=0 的 PS 节点 **pool 0→1**（单四边形已建）：`H_p_闪电` / `H_p_星点_02` / `H_ shandian01_1_1` / `H_鬼火_lizi_1` / `M_lizi_科技_01` / `L_p_星点_02`（全部 `visible=0`，因采样时间在其窗口外，见下）。

- ⚠ **未证**：我自己的探针采样了 t=0/0.02/0.048/0.148/0.30，而 viewer-auditor 的闪帧窗口是 **t≈1.150–1.200** ⇒ 我这些读数全部 `alive_now=0`（不是没渲染，是**采在了窗口外**——我的采样点选错，已在报告中如实标注）。**闪帧时刻(1.175)的逐节点 alive/quad 对照未做**。

## 3. 靶子 2（尺寸）：钳制已实现，依据用基线实测

- 改前基线（`FX53_before_flash.json`）：`M_g_glow_an` 6×6 / `H_g_glow地_an` 13×13 / **`H_公告板_爆闪2` 50×50（diag 70.711）** ⇒ 特效层 diag **70.71** vs 武器 **15.455** = **4.58×**。

- 钳制：`quad 世界边长 ≤ 武器 bbox 对角线 × 0.60`（默认，可关：`SPRITE_CLAMP_K=null/false`；可调）。依据=上述实测 + **源 `radius` 语义仍 unresolved**（故只做上限、不改源值语义、不加系数）。

- ⚠ **未证**：钳制生效的**前后两帧**（要求『钳制开/关』对照）未拍 —— 需要同版本、窗口内采样（见 §6）。

## 4. 靶子 3（贴图/blend）

- 切片：`.spr` 帧矩形解析已接入（候选级 `content_candidate`，不宣称名轴直证）；改后 3 个 Sprite 源侧**本非精灵表**（`sliced_total=0`），因此本轮切片对 1110177 的闪帧**无可见影响**（诚实结论）。

- `blend_mode=7`：改前隐性落 `additive`（会把未知贴图加成整块发白）；改后显式 `BLEND7='normal'`（alpha）——理由：alpha 不会叠加亮度，是『未知贴图』最不具破坏性的选择；**值表仍 unresolved**，可一行切回。

## 5. 开关与负控

- `models_enabled` 仍**缺省（= 关）**；精灵层新增独立开关 `WikiSfxAdapter.sprites(true/false/null)`（null=跟随 SFX 总开关），**未引入任何人工强度系数**。

- 负控调用已执行，读数：{"step": "negative_controls", "sprites_off": "{\"spriteOn\":false}", "sprites_on": "{\"spriteOn\":true}", "models_off": "{\"force\":false,\"loadStarted\":0}", "models_on_then_off": "{\"force\":true,\"loadStarted\":0}"}

## 6. 验收现状（逐条，含跨版本阻断）

| # | 要求 | 状态 |
|---|---|---|
| 1 | 改前/改后 sha16+字节+备份+逐处原文/新文 | **已做**（§0/§1） |
| 2 | 同开关状态下前后闪帧对照 + 逐节点探针 | **部分**：探针已实现并运行（只读），但采样点选错（窗口外）；闪帧对照未做 |
| 3 | 默认(SFX OFF)逐字节不变（同会话 N≥5） | **不可判定（跨版本）**：基线 pin `v1110177=C59DD70479217BFE`，AFTER pin `v1110177=1652A648FB602465`（**lead 同期把 effects.json 内联进 viewer.json**）⇒ OFF 帧 `8352c4e30bbaf981`(前) vs `4631d869ea598ae4`(后) **不可比**，不能归因于本补丁（adapter pin 亦不同：`1CD4AC5454D1F27A`→`A19F8B4551DBDE49`）。**需冻结 viewer.json 后同版本重测** |
| 4 | 负控两帧 | **未做**（开关调用√，截图×） |
| 5 | `applied==expected_prims`、`__errs=[]` | **未取**（探针脚本只读了 `__sfxDiag`；`__errs` 在 `FX53_probe_readings.json.errs`） |
| 6 | 如实写未解决 | **已做**（本§与§2/§3/§4 的『未证』） |
| 7 | 同源时间扫描前后对照（t=1.175，alive/effect-only%） | **未做**：AFTER harness 跑出 `1110177 flash.active_samples=0（无 >500px 变化帧）`、`ratio 1.47`（基线 4.58）——**但这是跨版本读数**（vewer.json 已变），不能判定为『修好了』或『修坏了』 |
| 8 | 钳制开/关两帧 | **未做** |

## 7. 未做 / 未证（明确清单）

1. 冻结版本后的同版本前后对照（OFF 帧 N≥5、闪帧 t≈1.175、alive/effect-only、五个 MASK 读数）。

2. 钳制开/关两帧、精灵层/模型层负控两帧截图。

3. `applied==expected_prims` 与 `__errs=[]`/`__glowErrors=[]` 的读数（脚本可立刻补，需一次浏览器）。

4. 我自己的探针采样点应改为 t∈{1.13,1.15,1.175,1.20,1.25}（对齐 viewer-auditor 的闪帧窗口）——**下一轮第一件事**。

5. 切片对 1110177 闪帧无影响（3 个 Sprite 源侧非精灵表）；真正受益的是 `.spr` 声明的精灵表节点（其贴图为 content_candidate）。

## 8. 浏览器卫生

- 两次我自己的浏览器运行（探针 + AFTER harness）均**单浏览器**；探针脚本按 `user-data-dir=fx53_prof` / 端口 10091 反查并 `taskkill /T /F`；运行后复查 **无残留 chrome 进程**。

- 未改 viewer.json / neox_material.json / 1110177/effects.json（后者属 task-52 写域）。

### 9.5 lead 更正后的核对结论（补充）
- **每次运行均为单次载入、pin 由脚本当场实测** ⇒ 单次运行内部不下跨版本结论；**跨运行**对照按纪律标“跨版本，不可归因”。
- pin 链：基线(23:41) viewer.js `641DDC2C…` / viewer.json `C59DD704…` → AFTER harness(23:52) viewer.js `7578419812…` → A/B(冻结口径) viewer.js **`A8F023D8A8174164`**（= lead 确认的新版）/ viewer.json `1652A648FB602465` / adapter `F9CBAAA8966659C4` / board `718202FC4D29F603`。
- **settle/OFF 帧跨版本一致**：1110177 OFF = `8352c4e30bbaf981`（基线 23:41 与 A/B 冻结态相同）；1110171 OFF = `13c8c5ce35bb869e`（基线 与 AFTER harness 相同）⇒ 与 lead 预期一致：`pending_hidden` 只影响 IBL 未就绪的**窗口期**帧，settle 帧不变；窗口期差异属策略变更，不判为回归。
- **硬阻断（未解）**：冻结口径载入内 SFX 全程不渲染（t∈{1.10..1.25} 全 alive=0；3 Sprite `map` 空、`visible=false`、quad 恒 1；`neg_sprite_only`/`neg_model_only` 与纯 OFF 帧同 sha）⇒ `clamp off/on`、`psFallback off/on` 四组读数完全相同、**无判别力**。
- **下一探针（决定性）**：页面内打印 adapter 计算的 `baseUrl`，对 `glow_01__13211b02.png` 等 URL 做 `fetch`/`Image` 状态读取（区分 404 与路径拼接错误）。

## 10. 404 修复后的浏览器验收（冻结口径，单次载入内 A/B）

pin（脚本当场实测）：adapter `6349FA1637D9CE88`（测量态；之后修 sprites 门控 => `c3affd4f77f042c1`，默认路径不变）· viewer.js `A8F023D8A8174164` · viewer.json(1110177) `21092BC9D218F91C` · board `718202FC4D29F603`。

### 10.1 已证
1. 钳制负控：clamp off 复现 H_公告板_爆闪2 50x50 = ratio 4.5752（基线 4.58x）、effect-only 46.596%；clamp on 压到 q=9.2731 = 武器对角线 x 0.60（设计上限）；M_g_glow_an 6 未被压。
2. PS 回退负控：psFallback off => alive=3、6 个 ParticleSystem 全 vis=0（复现基线缺席）；on => alive=7 = 3 Sprite + 4 个 PS **单四边形**（H_ shandian01_1_1 / H_鬼火_lizi_1 / M_lizi_科技_01 / L_p_星点_02；另 2 个无 texture_candidate 按 fail-closed 不画）。
3. 默认态逐 t(1.10-1.25) effect-only 3.37-3.59%（基线 peak 38.08% => 面积约 1/10）；1110177 OFF x5 连续同 sha `8352c4e30bbaf981`。
4. exceptionDetails 0 条；URL 拼接加固（显式 undefined/null）后 node --check 通过。

### 10.2 未证（带原因）
1. applied==expected_prims：读法错了（少一层 .report）=> 正解 `__neox().report.applied` / `.report.applied_prims` / `.report.failed` / `.report.missing`（lead 口径更正）；本轮未重测。
2. 404 归零断言：注入正则转义失败 => tex_requests_n=0（断言未取到，不是没有请求）。
3. 精灵层/模型层负控：受 sprites(on) 未门控 tick 影响（已修 c3affd4f77f042c1），未复测。
4. t=1.175 与 clamp_on 帧 effect-only=0.000 异常：疑为同相位 OFF 参照帧取帧时机，需重抓。
5. 1110171 OFF x5 = `be705c410590cf61` != lead 期望 `13c8c5ce35bb869e` => 已报 lead，未下结论（属 viewer.js 改动面，转交 shader-auditor）。

### 10.3 未做
- 与 viewer-auditor 同判据（MASK 五读数）复测；- task-55 的浏览器只读验证。

数据以 `FX53_AB_readings.json` 为准；本报告不伪造表格。

## 11. 收尾轮（冻结口径，单次载入；数据源 FX53_final_readings.json）

### 11.1 pin 表（脚本运行当场实测）
- adapter `C3AFFD4F77F042C1` / viewer.json(1110177) `D7DA78F87C625303` / viewer.json(1110171) `62E7BDDC9CF6EC6D` / board `718202FC4D29F603` == lead 基准；
- **viewer.js 实测 `33DD8FBCA398BF15`**：既不是 lead 上一条的 `9FFC8BC18E516277`，也不是冻结通报里的 `3B9999B992FE8763` => **本运行跨了 viewer.js 变更（第三版）**，按纪律：像素类读数只标数值、不跨版本归因；涉及 pending_hidden 的探针字段按本运行实测报告。

### 11.2 六项待办读数
1. **404 归零断言：仍未取到**。改用非正则 `indexOf("/sfx/tex/")` 过滤后 `n=0`（st200=0 / st404=0 / other=[]）=> 该页的 resource timing 里**没有任何含 /sfx/tex/ 的条目**（原因未定证）=> 记 **未证**，建议由 viewer-auditor 的网络侧 harness 取（上一轮它的 404 实况即来自网络侧）。
2. **同相位 OFF 参照重抓成功，eff%=0 异常已消**：同一 t 抓参照帧后，t=1.15 / 1.175 / 1.20 的 effect-only = **3.484% / 3.578% / 3.526%**（off_sha 均为 `8352c4e30bbaf981`）；对比基线 peak **38.08%** => 面积约 **1/10.6**。
3. **负控（SPRITE_ON 门控已修）**：
   - `sprite_only`（精灵开/模型关）：sha `2873eb380e0b6e30`，**1 秒后仍同 sha**，alive=**7**；
   - `model_only`（精灵关/模型开）：sha `8352c4e30bbaf981`（= 纯 OFF），**1 秒后仍同 sha**，alive=**0**；
   - `all_off`：sha 同纯 OFF，alive=0，1 秒后同 sha => **关掉后不会下一帧又被点亮 + 两开关互不干扰 = 已证**。
4. **撤回后的 report 复测（本运行实测，含 .report 口径更正）**：1110177 `report.applied=3`、`applied_prims=3`、`failed=0`、`missing=0`、`env_warn=null`、`prims[i].pending_hidden=[false,false,false]` => **applied == manifest prim 数(3) 且 failed/missing 为空（已证）**；1110171 `applied=7 / applied_prims=7 / failed=0 / missing=0`。
   - **绑定 9->8 的可见影响（如实）**：撤回的 `lightning07_cs` 节点在本轮 alive 中**未出现**（对应 PS 节点 pool=0，fail-closed）；本轮 alive=**7**（3 Sprite + 4 PS 单四边形）与上一轮同值，effect-only 3.578% vs 上一轮 3.4% —— **viewer.json 已换版（`21092bc9…` -> `d7da78f87c625303`），属数据变更，跨版本不可归因**。
5. **默认态 OFF（本版本 sha，未与旧锚点比较）**：1110177 `8352c4e30bbaf981` x5 **全同**；1110171 `09611e2e90b49bc0` x5 **全同**。
6. **与 viewer-auditor 同判据（MASK 五读数）：未做（委派）** —— 精确五读数公式在其 harness 内，我把近似值当可比数字会污染比对，故不做；由它按同 pin 独立复测。

### 11.3 未证 / 未做（收尾清单）
- 未证：① 404 归零（resource timing 无条目，断言未取到）；② 本运行出现 **1 条 Uncaught 异常**（`scriptId 20, line 0 col 22`，`exceptions` 记录一条），**无法证明其来自页面还是我的注入表达式** => 不能再用 exceptionDetails=0 作为无异常证据（上一轮是 0 条）；③ MASK 五读数。
- 未做：与 viewer-auditor 同判据复测（委派）；`effect-only` 与旧版本的严格可比性（数据变更）。
- 结论口径：**钳制/负控/PS 回退三条核心判据成立；404 与 MASK 两条未取到**；是否可判"修好了"由 lead + viewer-auditor 独立复测后定。
