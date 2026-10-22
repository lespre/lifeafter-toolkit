# C159PARSE · `find_groups` 修复 + `Tex0` 矛盾判定（只读诊断 / 唯一改动=c159_pair.py 的 L128-143）

**本轮改动**：`01拆包器本体\工具库\06_皮肤定位链\c159_pair.py`（**最小改动**：仅替换 `find_groups` 的"按 TransparentMode 分段 + 连续重复去重"两段，API 不变）
- 改前：15228 B · mtime 2026-09-14 08:28:17 · sha256 `88338B8F6075937833FC486362DAFC085B56F6E8BEED8621F071B20B1DE55BAF`
- 备份：`c159_pair.py.bak_20260918_023638`（同 sha256）
- 未改动：皮肤资产 / manifest / viewer.js / sfx_adapter.js / board.html / 注册表

---

## 1. 卡点根因（先诊断后改）

**我上一轮报的根因是对的，但中途自我"更正"错了，现给出严格证据：**

| 文件 | pre 组数 | post 组数 | L139-142 实丢 |
|---|---|---|---|
| `001265.c159` | **14** | **9** | **5 组**（含 `pre[1]==pre[2]`：**两份完全相同的 8 槽 crystal012 材料**） |
| `003996.c159` | 6 | 5 | 1 组（1 槽噪声，无害 ⇒ 029 一直 19/19） |

关键：`001265` 的 **7 个材料段全部来自同一个 u16 run**（`align=0, st=514, len=166`，`TransparentMode` 出现在第 `[9,39,69,97,107,137,165]` 位 ⇒ **7 段**），段长 10/30/30/28/10/30/28 ⇒ 字符串槽 **5/8/8/7/5/8/7 = 48** ✓ 与文件里 48 条路径串**完全相等**。
原实现把 `pre[1]==pre[2]`（双枪的第二份 crystal012）当"重复副本"删掉 ⇒ 材料数 7→6、字符串槽 48→40 ⇒ **后序材料整体错位**。

> 我上一轮"更正"失败的原因：用 `[g for g in pre if not (g in post)]` 判断被删项 —— 被删组与保留组**内容相等**，因此该表达式查不到它。已用**逐索引比对**确认（pre=14/post=9）。

## 2. 最小改法

只把"连续重复去重"从**同对齐内也生效**改为**仅跨对齐(align 0↔1)生效**（跨对齐重复才是"双字节对齐各扫一遍"的产物；同文件里两份相同材料是**合法**的），并**保留 align 信息**用于判定。返回类型仍是 `list[list[int]]`。

## 3. 回归（必须全过）

| 回归项 | 结果 |
|---|---|
| 既有 `test_c159_parser.py`（029 ×4 LOD + 028 皮毛 + 034 武器 + 034 场景拒绝） | **7/7 全部通过**（配对评分 41/39 不变；029 组列表由 `[9,34,34,14,12]`→`[9,34,34,14,12,12]`，多出的正是被误删的重复材料） |
| **1110177 (003996) 自检** | **19 行 / 19 串 / 余 0 / 冲突 0** ✓ 与 `C159_PARAM_PAIRING.md` 逐行一致 |
| **1110171 5 槽自检** | `001265` blk0 = Tex0`*_a` · ParamMap`*_m` · t_surfacemap`*_s_m` · NormalMap`*_n` · t_custom_ibl`*.cube` ✓ 与 manifest 自述一致 |
| 001265 全材料 | **7 材料 / 48 行 / 48 串 / 余 0**（修前 6/40/余 8）✓ |

## 4. 修后全量表（8 个 c159；每行 = 槽位类 ← 明文引用）

### 4.1 weapon 基底组（模板固定 5 槽：Tex0, ParamMap, t_surfacemap, NormalMap, t_custom_ibl）
| 皮肤 | c159 | 材料 | Tex0 | ParamMap | t_surfacemap | NormalMap | t_custom_ibl |
|---|---|---|---|---|---|---|---|
|1110171_dual|001265|blk0|`012001a`|`012001m`|`012001s_m`|`012001n`|`qiangpi.cube`|
|1110171_dual|001265|blk4|`010001a`|`010001m`|`010001s_m`|`010001n`|`qiangpi.cube`|
|1110171_single|001223|blk0|`010001a`|`010001m`|`010001s_m`|`010001n`|`qiangpi.cube`|
|1110177|003996|blk0|`029001a`|`029001m`|（该族无 surfacemap 槽）|`029001n`|`qiangpi.cube`|
|1110152|002731|blk0/blk1|`009001a` / `009_1001a`|`009001m` / `009_1001m`|`009001s_m` / `009_1001s_m`|`009001n` / `009_1001n`|`qiangpi.cube` ×2|
|1110129|000334|blk0..3|`008001a` / `008_1001a` / …|`…001m` / `…_1001m`|`…001s_m` / `…_1001s_m`|`…001n` / `…_1001n`|—|
|1110024|001386|blk0/2/3/4|`004001a` ×3 + `004_1001a`|`004001m` / `004_1001m`|`004001s_m` / `004_1001s_m`|`004001n` / `004_1001n`|`indoor.cube`|
|1110145|000654|blk0/2/3|`014001a` ×3|`014001m`|`014001s_m`|`014001n`|—|
|1110165|001631|blk0/1/2|`1001a` / `001a`|`1001m` / `001m`|`1001s_m` / `001s_m`|`1001n` / `001n`|`qiangpi.cube`|

### 4.2 crystal 族（含 `t_basecolor` 槽）
| 皮肤 | 材料 | Tex0 | t_basecolor | NormalMap | DetailMap | t_caustic | t_custom_ibl | t_reflection | t_refraction |
|---|---|---|---|---|---|---|---|---|---|
|1110177|blk1|`029001b_m`|`029001a`|`029001n`|`crystal_bump_n02`|`crystal_caustic_uvva002`|`car_studio01.cube`|`crystal_reflection_uvva`|—|
|1110177|blk2|`029001b_m`|`029001a`|`029001n`|`crystal_bump_n_uvva`|`crystal_caustic_uvva`|`fashion_qiangpi.cube`|`crystal_reflection_uvva`|`refraction_envmap_3`|
|1110171_dual|blk1/2/5|`…b_m`|`…a`|`…n`|`crystal_bump_n_uvva`|见 ⚠|`car_studio01.cube`|见 ⚠|`refraction_envmap_3`|
|1110171_single|blk1|`010001b_m`|`010001a`|`010001n`|`crystal_bump_n_uvva`|见 ⚠|`car_studio01.cube`|见 ⚠|`refraction_envmap_3`|
|1110145|blk1|`014001b_m`|`014001a`|`014001n`|`crystal_bump_n02`|`caustic3`|—|见 ⚠|`refraction_envmap_6`|
|1110165|blk3|`1001b_m`|`1001a`|`1001n`|`crystal_bump_n_uvva`|见 ⚠|`bonifacio_street.cube`|见 ⚠|`refraction_envmap_3`|

⚠ = **`t_caustic_tex`/`t_reflection_tex` 双路冲突**（槽序给 `caustic←*reflection*`、`reflection←*caustic*`，与文件名语义相反）：见 §6 卡点，**该类对 unresolved**。

### 4.3 修后余串
`1110177 0` · `1110171_dual 0` · `1110171_single 0` · `1110152 0` · `1110165 0` · `1110024 0` · `1110129 3`（`_2001*`/`_4001*` 两套未被任何槽消费）· `1110145 6`（`_1001*` 只有 a/m/n 三条，另 3 条无法归属）

---

## 5. ★★ `Tex0` 矛盾判定

### 5.1 双向证据（材料级计数，8 文件 / 33 材料）
| 材料模板 | 槽 | 明文文件 | 材料数 |
|---|---|---|---|
| **weapon 基底**（`Tex0, ParamMap, t_surfacemap, NormalMap, t_custom_ibl`，无 `t_basecolor`） | **Tex0** | **`*_a`** | **21 / 21（无例外）** |
| crystal（含 `t_basecolor`） | Tex0 | `*_b_m` | 9 |
| crystal（含 `t_basecolor`） | t_basecolor | `*_a` | 10 |
| crystal-无-basecolor（7 槽，含 caustic/reflection/refraction） | Tex0 | `*_b_m` | 2 |
| crystal（1110024 blk1，离群） | Tex0 | `*_s_m` | 1 |

⇒ **`*_a` 与 `*_b_m` 各自的槽位是明确的**：
- **`*_a`** 落在 **crystal 的 `t_basecolor`**，以及 **weapon 基底的 `Tex0`**；
- **`*_b_m`** 只落在 **crystal 族的 `Tex0`**（含"无 t_basecolor 的 7 槽晶体材料"）；
- **`ParamMap ← *_m`、`t_surfacemap ← *_s_m`、`NormalMap ← *_n`、`t_custom_ibl ← *.cube`** 全材料一致。
- 结构事实：**`t_basecolor` 槽只存在于晶体族材料**；weapon 基底的模板里根本没有该槽。

### 5.2 与 09-17 A/B 的对照（`裁定_weapon基色真值_20260917.md`）
该文件自己的记录：
- 第 5 行：**「上一轮发现 GLB 与 c159 manifest 都指向 `_a`」** —— 即 A/B 是**在明知源绑定为 `_a` 前提下**做的外观对照；
- 方法：`__abcProbe('a'|'b')` **只切换 weapon 的 `map`**（不动 metalness/roughness/normal/env/光照/曝光）；
- 结果：`_b_m` → gold **21.47%** / violet 10.53%；`_a` → gold **0.0%** / violet **37.02%**；参考图 gold 58.4%；
- 判定理由：参考图金色为主，`_a` 给 0% 金色 ⇒ "`_a` 更可能是细节/掩码层，而非 albedo"；
- 自留缺口（第 39-44 行）：`_b_m` 21.47% vs 参考 58.4%，**口径不同**（武器区 vs 整帧），未收窄到纯 prim0/4。

### 5.3 判定：**c159 一侧更强（绑定事实层面）**
**为什么**：
1. cx159 直接读出的是**源容器的槽位记录**（槽位类名 + 明文路径的逐槽配对），这是**绑定事实**；A/B 切换的是**渲染输入的试错**，得到的是**外观结果**。**外观不能反推绑定**——同一份 `_a` 在源里绑 `Tex0`，渲染出来却不金，只能说明**渲染链还有一处未知偏差**，不能说明源绑定不是 `_a`。
2. 覆盖面与自洽性：c159 侧 **8 文件 / 33 材料**、weapon 基底模板 **21/21 无例外**，且与"`t_basecolor` 槽只存在于晶体族、其值恒为 `*_a`"、"manifest 自述 001265 block0/4 只含 001a/001m/001s_m/001n/qiangpi.cube（无 b_m）"三方互证。A/B 侧只有 2 个方案 × 1 个皮肤（1110171）× 1 个口径，且**自留了 21.47% vs 58.4% 的未解释缺口**。
3. A/B 的推理存在**结论外推**：它由"`_a` 当 albedo 外观不对"直接推出"源绑定应为 `_b_m`"，中间缺一步——源 shader 里 `Tex0` 的语义**未必是 albedo**（本次直证显示 weapon 基底模板**没有** `t_basecolor` 槽，颜色来源本身待证）。

**⇒ 绑定记录（manifest/provenance 的"源绑定"字段）应以 c159 为准：weapon 基底 `Tex0 = *_a`。**
**⇒ 渲染口径是另一个决策**：A/B 证明"以 `_b_m` 作 albedo 更接近参考图"——这**可以**作为 viewer 的**渲染近似**保留，但必须标注"**与源绑定 `Tex0=*_a` 不符**"，并且**不得**拿它去改写"源绑定"记录，也不得据此关闭"weapon 基色来源"这个 unresolved（真正的缺口是：源里 weapon 基底的可见基色**来自哪个槽/哪个参数**——目前 no source slot 直接给出金色主体）。

**一句话**：**c159 方成立（源绑定 = `*_a`）；A/B 方不成立为"绑定证据"，但成立为"渲染结果"——两者的矛盾说明"渲染链还有一处未解的偏差"，而不是"源绑定要改"。**

---

## 6. 卡点（如实登记）

1. **`t_caustic_tex` / `t_reflection_tex` 双路冲突**：`001265`/`001223`/`000654`/`001631` 的晶体材料中，槽序给 `t_caustic←*reflection*`、`t_reflection←*caustic*`，与文件名语义相反；而 `003996`（029）两路**一致**。⇒ c159 字符串记录**不含逐条槽 id**，两种信号在源里确实可能不一致 ⇒ **该类对 unresolved**（不采用任一信号硬判）。
2. **`1110145 (000654)` 余 6 串**：该文件有 32 条路径串但只解出 26 个字符串槽（`_1001*` 只有 a/m/n 三条），⇒ **1110145 的 `_1001*` 逐槽归属仍 unresolved**（其类语义由 1110152/1110129/1110024 三套齐全文件推定：`_1001a→Tex0`、`_1001m→ParamMap`、`_1001s_m→t_surfacemap`、`_1001n→NormalMap`）。
3. **`1110129 (000334)` 余 3 串** + 该文件另有 `_2001*`×8、`_4001*`×3 未被任何槽组消费 ⇒ 是否"合并文件的多材料区"**unresolved**。
4. **`1110024 blk1` 离群**：crystal 模板却给 `Tex0←*_s_m`（1 例/33 材料）⇒ 疑其材料段边界仍受影响，**该材料单列 unresolved**。

---

## 7. 复现命令

```powershell
$py="C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"; $d="E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链"
# 回归（既有 7 项 + 029 跨 LOD）
& $py -B "$d\test_c159_parser.py"
# 全 8 个 c159 逐槽表
& $py -B "$d\c159_slot_parser.py" --skins --json "E:\la拆包项目\03拆包产物\_target_1110171\C159PARSE_skins_fixed.json"
# 单文件
& $py -B "$d\c159_slot_parser.py" "E:\la拆包项目\03拆包产物\weapon\001265.c159"
```
**回退**：`copy /Y "$d\c159_pair.py.bak_20260918_023638" "$d\c159_pair.py"`（sha256 `88338B8F…`）

**只读声明**：除 `c159_pair.py`（本轮唯一授权改动，已备份）与新增 `c159_slot_parser.py` / 本报告 / 结果 JSON 外，未改动任何皮肤资产、manifest、viewer、注册表；未重启服务。
