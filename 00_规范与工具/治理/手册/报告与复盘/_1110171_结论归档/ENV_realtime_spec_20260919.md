# task-60：`t_realtime_env_spec`(t8) / `t_env_spec_array`(t6) 可否源化 —— 只读取证

**一句话答案**：**两者都是「引擎运行时全局天空」绑定，不是按名可取的皮肤资产**（`unresolved`）。它们在 DXBC RDEF 里以固定槽位资源出现（t6 `cubearray` / t8 `cube`，配 s0 `s_env_spec_array`），**在 35,275 个 weapon c159 中 0 命中、也不是任何材质槽**；且只出现在 **2–3 / 35** 个 PS 变体里，与声明 `t_custom_ibl` 的 **16/35** 个变体**互斥** ⇒ 对本链两皮肤（材质声明 `t_custom_ibl`）而言不属于被执行变体的预算。容器穷举 **390 种子 → 17,212 候选名 / 313 容器 / 6,148,466 行（+253.2 MB fpk 索引）→ 0 命中**（仅 3 个阳性对照命中，证明检索链有效）。

**pin 自核**（我独立复算，与 Lead 给的一致）：`viewer.js 8B8E80213F5C0CA8`（376,205 B）· `board.html 5008117AA03BB7A0`（108,744 B）· `1110171/neox_material.json 64A07D5DF157EC16` · `1110177/neox_material.json A05C4F2C8DDFCF9A`。
**只读**：未起浏览器；未改 viewer.js / adapter / manifest / viewer.json / board / 注册表；只写 `ENV_realtime_spec.json` + 本文件。

---

## 1. t8/t6 是怎么被绑定的

### 1.1 RDEF 直读（shader 侧，逐行）
`03拆包产物\render_1003_010\_disasm\cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm`：

| asm 行 | 原文 | 说明 |
|---|---|---|
| L253-255 | `// Resource Bindings:` + 表头 | RDEF 资源绑定表 |
| L257 | `s_env_spec_array  sampler  NA  NA  s0  1` | 与 t6 配对的采样器 |
| L272 | `t_env_spec_array  texture  float4  cubearray  t6  1` | **t6 = cube 数组** |
| L274 | `t_realtime_env_spec  texture  float4  cube  t8  1` | **t8 = 实时天空 cube** |
| L332 | `dcl_resource_texturecubearray (float,float,float,float) t6` | 槽位声明 |
| L334 | `dcl_resource_texturecube (float,float,float,float) t8` | 槽位声明 |
| L278-282 | `NeoxUBOLocal cb0` / `NeoxUBOGlobal1..4 cb1..4` | 全局 cbuffer 族 |
| （RX 报告 L42/L59-61 引 L624-626） | `cb1[281].z = u_realtime_skylight_max_mip_level` → `sample_l(texturecube) ..., t8, s0, r7.w` | 天空 cube 的采样 mip 由**全局** cb1 控制 |

⇒ 名字来自 RDEF、绑定在**固定槽位**；同族还带一个控制其 mip 的**全局**常量。

### 1.2 c159 / 材质侧：**两名字 0 命中**
- `03拆包产物\weapon\` 下 **35,275 个 c159** 全字节扫描：`t_realtime_env_spec` **0**、`t_env_spec_array` **0**。
  （对照：`t_custom_ibl` 403 个文件、`t_reflection_tex` 302、`t_refraction_tex` 280、`t_caustic_tex` 321、`t_surfacemap` 2871、Tex0 17512、NormalMap 9142、ParamMap 9111、DetailMap 410、t_basecolor 298。）
- 目标三文件（`001265`/`001223`/`003996`）的参数名表（25/25/26 项）里也没有它们；材料槽全集 = `Tex0, NormalMap, DetailMap, ParamMap, t_basecolor, t_surfacemap, t_caustic_tex, t_custom_ibl, t_reflection_tex, t_refraction_tex`。`001386`（1110024）多一条 `u_refraction_mipmap`。
- **对照判定**：`t_custom_ibl` 既在 403 个 c159 里声明、又在 16/35 个 PS 变体里声明 ⇒ **材料级按名绑定**；t6/t8 **无任何材料名对应** ⇒ 不是材料绑定，只能由引擎注入。**证据级别：高（两侧直接读取 + 全库对照）**。

### 1.3 变体矩阵：两条路径**互斥**
35 个 PS(blob1) 变体（`_game_shader_db\pipes\_disasm4` 8 个 + `_disasm\cand` 27 个；含 VS 共 70 asm）：

| 资源 | 出现变体数 | 绑定槽位 | 具名变体 |
|---|---|---|---|
| `t_custom_ibl` | **16 / 35** | t4 / t5 / t6（随变体） | 24da1bb5@t5、3f7860cd@t6、d982f18f@t6、fddea810@t6、2490ff82@t6、dd3b77c4@t6、9d91bfd3@t5、28f1ff44@t5、4d5c7e52@t5、02ac9f54@t4、04e9cd45@t4、12de16c6@t4、1dc77496@t4、46015f31@t4、65b2e6e8@t4、e2c89ce1@t4 |
| `t_env_spec_array` | **3 / 35** | t6 | 03e9e23d、b49859b1、efe1a9fc |
| `t_realtime_env_spec` | **2 / 35** | t8 | 03e9e23d、efe1a9fc |
| **同时有 `t_custom_ibl` 与 t6/t8** | **0 / 35** | — | **无（结构性互斥）** |

⚠ 值得注意：`s_env_spec_array`（采样器 s0）在多数 `t_custom_ibl` 变体里**仍被声明**，但对应的 **cubearray 纹理不在该变体里** ⇒ 采样器是编译残留，纹理才代表真实预算。

---

## 2. 容器穷举：**0 命中**（含阳性对照）

工具：`gpk_npk_index.py`（**只读 import**，未重写解析器；`candidates()` 的变体展开照用）。

- **阳性对照**：`do_selftest` 全过 —— `common\env_map\qiangpi.cube` → res.npk row **14213**，fid `D763973EACDC554E`（u6 `ACDC554E`/u7 `D763973E`），offset 1710400516 / packed 446736 / decoded 524408 / flag 2 ✓；`car_studio01.cube`、`fashion_qiangpi.cube` 同法命中 ✓。
- **种子 390 个** = 12 根目录 × 8 名字 × 4 扩展名 + 6 显式：

| 维度 | 取值 |
|---|---|
| 根目录（12） | `common\env_map\`、`common\env\`、`common\sky\`、`common\realtime_env\`、`common\realtime\`、`res\common\env_map\`、`res\env\`、`env\`、`env_map\`、`sky\`、`effect\env\`、`assets\env\` |
| 名字（8） | `t_realtime_env_spec`、`t_env_spec_array`、`realtime_env_spec`、`env_spec_array`、`env_spec`、`realtime_env`、`realtime_skylight`、`sky_spec` |
| 扩展名（4） | `.cube`、`.dds`、`.tga`、`.png` |
| 显式补充（6） | `common\env_map\realtime_env_spec.cube`、`common\env_map\env_spec_array.cube`、`common\sky\realtime_env_spec.cube`、`common\sky\realtime_skylight.cube`、`common\env_map\t_realtime_env_spec.dds`、`common\env_map\t_env_spec_array.dds` |

- **工具再展开**为 **17,212 个候选名**（原样/斜杠互换/扩展名互换/去一层目录/lower/UPPER/首字母大写/`_lod01|lod02|lod1|_1|_high|_preview`，且 utf-8 与 latin1 两种编码各算一次）。完整清单见 `ENV_realtime_spec.json.candidates_full`。
- **覆盖**：249 个 `.gpk`/`.gpk(gres)`/`.npk` 容器**全部解析成功**（GPK 行 4,579,785 + NPK 行 1,568,681 = **6,148,466 行**）+ 64 个 `.fpk` 经 `fpk_fid_index.json`（**253.2 MB 单遍扫描**）= **313 个容器**；耗时 218.4 s。
- **结果**：**命中 3 个，全部是阳性对照**（qiangpi / car_studio01 / fashion_qiangpi）。env-spec 类候选 **0 命中**（gpk/npk 0；fpk 0，fpk 唯一命中就是对照 `fashion_qiangpi.cube`）。

⇒ 零命中证据口径：**已排除 17,212 种写法（390 种子）× 313 个容器 × 6,148,466 行（+64 fpk / 253.2 MB 索引）**。

---

## 3. 该族 c159 的**环境类槽位全集**与绑定状态

| 槽位 | c159 声明 | shader RDEF 归属 | 我们 manifest | 状态 |
|---|---|---|---|---|
| **`t_custom_ibl`** | 三文件均声明（全库 403） | 16/35 PS（t4/t5/t6） | 已绑：`qiangpi.dds`（prim0/4 与 1110177 prim0）、`car_studio01.dds`（prim1/2/3/5/6、1110177 prim1）、`fashion_qiangpi.dds`（1110177 prim2） | ✅ **已源化**（镜面环境，`getIBLRadiance` 已接管） |
| `t_reflection_tex` | 三文件均声明 | 全变体（sampler `s_reflection_tex`；纹理行随变体） | 已绑 `crystal_reflection_uvva.png` | 绑定 ✓；数值侧 `u_*` 已落盘、**未接线** |
| `t_refraction_tex` | 三文件均声明 | 全变体（t5/t4） | 已绑 `refraction_envmap_3.png` | 同上 |
| `t_caustic_tex` | 三文件均声明 | 全变体（t4/t3） | 1110171 已绑；**1110177 prim1 = null** | 部分（1 处缺口） |
| `t_surfacemap` / `DetailMap` / `NormalMap` / `Tex0` / `t_basecolor` / `ParamMap` | 按族声明 | 见 RDEF 表 | 已绑 | 绑定 ✓ |
| **`t_env_spec_array`（t6）** | **0 / 35,275** | 3/35 PS | 无此槽 | **unresolved（运行时全局，非皮肤资产）** |
| **`t_realtime_env_spec`（t8）** | **0 / 35,275** | 2/35 PS | 无此槽 | **unresolved（运行时全局，非皮肤资产）** |
| `u_env_sh` / `u_ambient` / `u_char_ambient` / `u_env_day2night_exposure` | 0（属 cb1 全局） | cb1[148..154] / cb1[0] / cb1[284] / cb1[239] | 无 | **unresolved（运行时 cbuffer 值）** |

---

## 4. 可行性结论

**`unresolved`（运行时全局，非皮肤资产）**，且不是"暂时找不到"，而是**结构性**的：

1. 资产侧 0 命中（§2）：按名、按常见变体、按 313 个容器穷举都没有对应物。
2. 变体侧互斥（§1.3）：t8/t6 只活在 2–3/35 个变体里，而这些变体**没有** `t_custom_ibl`；反之本链两皮肤材质声明的是 `t_custom_ibl`（16/35 那支）⇒ 即便把天空 cube 取到手，也**不能**当作本皮肤执行变体的环境预算（变体归属 U5 仍 unresolved，但两支互斥是硬事实）。
3. 因此 t8/t6 **不能**作为"漫反射辐照源"或"`getIBLRadiance` 第二层"接入 —— 没有源级证据支撑，接入即为顶替。

**"环境预算 = 项目硬边界"这个表述的准确性**（按 Lead 要求逐字校准）：
- ✅ **准确的部分**：**漫反射环境预算**（源侧 = 运行时 SH/ambient 常量 + 另一支变体的全局天空 cube）在**只读静态资产**条件下确实拿不到 ⇒ 这一块是硬边界；本链现在把漫反射交给 three 的中性 PMREM 影棚（`viewer.js L274`），不是源数据。
- ❌ **不准确的部分**：不能说"环境预算整体不可得"——**镜面侧已经源化**（`t_custom_ibl` 六面 ✓）；且存在一条**有源证据支撑的近似路径**：用**已绑的源 cube** 重建辐照（task-59c 的 `getIBLIrradiance` 接入，`reconstruction approximation`，必须显式标 `approx:true`）。实测该近似**更暗**（`p50 −76.5%`、`p95 −15.2%`、`>0.5 −61.5%`，T47 §8.3），说明"源 cube ≠ 源天空预算"，据此**只能称重建近似、不得称源值**。
- 建议对外表述：**"源环境预算的漫反射部分（SH/ambient + 实时天空 cube）不可从静态资产源化——这是本项目的硬边界；镜面部分已源化；漫反射只能用源 cube 做标注过的重建近似。"**

---

## 5. U4 核实："t8/t6 绑定 2–3/15 变体"

- **出处**：`03拆包产物\_target_1110171\RX_energy_budget_20260919.md` **L60-61**（`t_realtime_env_spec(t8) 绑定 2/15`、`t_env_spec_array(t6) 绑定 3/15`）与 **L107-108**（U4/U5 原文，"15 个 PS 变体"）；机读版 `RX_energy_budget.json` 的 `unresolved.U4`（"绑定 2–3/15"）。
- **我的独立复算**（同一 asm 语料，35 个 PS 变体）：`t_realtime_env_spec` **2/35**、`t_env_spec_array` **3/35**，且具名可复现（realtime：03e9e23d、efe1a9fc；array：再加 b49859b1）⇒ **与 2/15、3/15 同量级、数字一致**。
- **可靠性判定：`partial`**
  - ✅ **计数可靠**：可复现、变体具名；含义是"多少变体声明该纹理"。
  - ⚠ **语料身份 unresolved**：那份交付物里只有计数，**没有 15 个变体的成员清单**，我无法逐一对齐到它的 15 个（我这边是 35 个 PS 的全语料）。
  - ⚠ **原问题的另一半仍 unresolved**：计数**不能**说明"该皮肤运行时是否真有内容"（需运行时探针；本任务未起浏览器）⇒ 按任务要求标 `unresolved`，不得用计数替代结论。

---

## 6. 复现命令（只读）

```powershell
$py="C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$TK="E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链"
# ① 阳性对照（fid 约定 + res.npk 行号）
& $py "$TK\gpk_npk_index.py" --selftest
# ② 单名探测（示例；完整 390 种子见 ENV_realtime_spec.json.seeds）
& $py "$TK\gpk_npk_index.py" --find "common\env_map\t_realtime_env_spec.cube" --variants --deep-variants
# ③ 本次穷举的等价重放（脚本在 %TEMP%，只读）：%TEMP%\ENV_spec_find.py
& $py "$env:TEMP\ENV_spec_find.py"
# ④ RDEF 绑定表
Select-String -Path "E:\la拆包项目\03拆包产物\render_1003_010\_disasm\cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm" -Pattern "t_env_spec_array|t_realtime_env_spec|dcl_resource_texturecube"
```

**未决（照实登记）**：① t8/t6 运行时是否真有绑定内容（需运行时探针，未批准）；② 本链两皮肤实际执行的 quality 变体身份（U5）；③ 诊断那 15 变体语料的成员清单；④ 运行时 SH/ambient cbuffer 值；⑤ 若将来确需天空 cube 形态资产，容器里按名不可达（可能以匿名帧存在，但**不猜、不顶替**）。
