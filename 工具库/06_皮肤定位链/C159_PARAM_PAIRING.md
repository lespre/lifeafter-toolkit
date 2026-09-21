# c159 材质参数 · 名称-数值配对报告（skin_2003_029 极光剑）

> 生成：2026-09-14 · 工具：`c159_pair.py`（可复用解析器，本目录）· 原始数据：`E:\la拆包项目\03拆包产物\weapon\_pairing_003996.json`
> 源文件：`003996.c159`（LOD1 材质，3872B）· 交叉验证：`004008.c159`（LOD0，3948B）+ `003997.c159`（子网格↔材质绑定）

## 0. 格式（实测）

```
名字表: [组件名 0..23][参数名 24..48]
  组件: AnimParam, DetailMap, ..., Macro0..6, ..., Material_0..2, NeoX, NormalMap, ParamMap, ParamTable, RenderStates, ..., Tex0, TransparentMode
  参数: t_basecolor(24), t_caustic_tex(25), t_custom_ibl(26), t_reflection_tex(27), t_refraction_tex(28),
        u_base_color(29), u_base_metallic(30), u_base_specular(31), u_caustic_brightness(32), u_caustic_depth(33),
        u_caustic_tilling(34), u_crystal_color(35), u_crystal_metallic(36), u_crystal_specular(37), u_cube_brightness(38),
        u_detail_intensity(39), u_detail_tilling(40), u_emissive_fresnel(41), u_emissive_strength(42),
        u_refraction_brightness(43), u_refraction_color(44), u_refraction_contrast(45), u_refraction_rotation(46),
        u_rotate_angle(47), u_subsurface_color(48)
槽位引用组: 文件头区(~@936) 三组 u16 列表 — [宏槽3..9][数值槽...][贴图槽(Tex0/24/16/1/25/26/27/28)][23]
数值块条目: [magic 01 00 01 13][type][payload]   type: 01=str · 02=i32 · 05=f32 · 06=f32[n]
配对规则: 正向对齐 —— 数值块条目[k] ↔ 组内「数值槽」序列[k]（宏槽/字符串槽不消耗条目）
材料归属: Sub0→skim_0(pbr_default) · Sub1→skim_1(pbr_crystal) · Sub2→skim_2(pbr_crystal+折射)  ← 003997 实测绑定
```

## 1. 材质 1（skim_1 · 护手晶体）↔ 块1（19 条，段A）

| slot | 参数名 | 类型 | 偏移 | 原始字节 | 解码值 | 绑定说明 |
|---|---|---|---|---|---|---|
| 40 | u_detail_tilling | f32 | 2393 | `6666a63f` | 1.3 | 细节平铺 |
| 39 | u_detail_intensity | f32 | 2402 | `6666a63f` | 1.3 | 细节强度 |
| 42 | u_emissive_strength | f32 | 2411 | `48e1fa3e` | 0.49 | 自发光强度 |
| 41 | u_emissive_fresnel | f32 | 2420 | `cdcc4c3f` | 0.8 | 菲涅尔 |
| 47 | u_rotate_angle | f32 | 2429 | `8fc24540` | 3.09 | 自转角度 |
| 38 | u_cube_brightness | f32 | 2438 | `8fc2353f` | 0.71 | 环境亮度 |
| 29 | **u_base_color** | f32[4] | 2447 | `04000000 96b2ac3e×3 0000803f` | **(0.3373, 0.3373, 0.3373, 1)** | 基色（银灰系）|
| 35 | **u_crystal_color** | f32[4] | 2472 | `04000000 1283803e d3de603e 1ff46c3e 0000803f` | **(0.2510, 0.2196, 0.2314, 1)** | 晶体色（中性深灰）|
| 30 | u_base_metallic | f32 | 2497 | `9a99193f` | 0.6 | 金属度 |
| 36 | u_crystal_metallic | f32 | 2506 | `3333733f` | 0.95 | 晶体金属度 |
| 37 | u_crystal_specular | i32 | 2515 | `01000000` | 1 | 晶体高光开关 |
| 34 | u_caustic_tilling | i32 | 2524 | `01000000` | 1 | 焦散平铺 |
| 33 | u_caustic_depth | f32 | 2533 | `14ae473f` | 0.78 | 焦散深度 |
| 32 | u_caustic_brightness | f32 | 2542 | `52b89e3f` | 1.24 | 焦散亮度 |
| 46 | u_refraction_rotation | f32 | 2551 | `b81e853e` | 0.26 | 折射旋转 |
| 45 | u_refraction_contrast | i32 | 2560 | `01000000` | 1 | 折射对比 |
| 43 | u_refraction_brightness | f32 | 2569 | `9a99993f` | 1.2 | 折射亮度 |
| 44 | **u_refraction_color** | f32[4] | 2578 | `04000000 1ea7283f c4b12e3f cac3423f 0000803f` | **(0.6588, 0.6824, 0.7608, 1)** | 折射色（冷蓝灰）|
| 48 | **u_subsurface_color** | f32[4] | 2603 | `04000000 9d80863e be9f9a3e fbcbce3e 0000803f` | **(0.2627, 0.3020, 0.4039, 1)** | 次表面色（暗蓝）|
| 22/24/16/1/25/26/27 | Tex0/t_basecolor/NormalMap/DetailMap/t_caustic/t_custom_ibl/t_reflection | 字符串槽 | — | — | (见贴图串区) | 7 槽 ↔ 7 贴图串（b_m/a/n/bump/caustic/studio01/reflection）|

## 2. 材质 2（skim_2 · 宝石晶体）↔ 块2（18 条，段B）★宝石红来源

| slot | 参数名 | 类型 | 偏移 | 原始字节 | 解码值 | 绑定说明 |
|---|---|---|---|---|---|---|
| 40 | u_detail_tilling | i32 | 3221 | `02000000` | 2 | 细节平铺 |
| 39 | u_detail_intensity | f32 | 3230 | `cdcc4c3e` | 0.2 | 细节强度 |
| 42 | u_emissive_strength | f32 | 3239 | `c3f5a83f` | 1.32 | 自发光强度 |
| 47 | u_rotate_angle | f32 | 3248 | `66662640` | 2.6 | 自转角度 |
| 38 | u_cube_brightness | f32 | 3257 | `295c2f40` | 2.74 | 环境亮度 |
| 29 | **u_base_color** | f32[4] | 3266 | `04000000 6c09f93d 9fcdca3e aa82013f 0000803f` | **(0.1216, 0.3961, 0.5059, 1)** | 基色（青蓝系）|
| 35 | **u_crystal_color** | f32[4] | 3291 | `04000000 35ef783e 00000000 00000000 0000803f` | **(0.2431, 0, 0, 1)** | **晶体色 = 暗红（宝石主色）** |
| 36 | u_crystal_metallic | i32 | 3316 | `01000000` | 1 | 晶体金属度 |
| 31 | u_base_specular | i32 | 3325 | `01000000` | 1 | 基础高光 |
| 37 | u_crystal_specular | i32 | 3334 | `01000000` | 1 | 晶体高光 |
| 34 | u_caustic_tilling | f32 | 3343 | `cdcccc3d` | 0.1 | 焦散平铺 |
| 33 | u_caustic_depth | f32 | 3352 | `b81e853e` | 0.26 | 焦散深度 |
| 32 | u_caustic_brightness | f32 | 3361 | `3d0a173f` | 0.59 | 焦散亮度 |
| 46 | u_refraction_rotation | f32 | 3370 | `ec51383e` | 0.18 | 折射旋转 |
| 45 | u_refraction_contrast | i32 | 3379 | `ffffffff` | -1 | 折射对比 |
| 43 | u_refraction_brightness | i32 | 3388 | `05000000` | 5 | 折射亮度 |
| 44 | **u_refraction_color** | f32[4] | 3397 | `04000000 0000803f 00000000 00000000 0000803f` | **(1.0, 0, 0, 1)** | **折射色 = 纯红** |
| 48 | **u_subsurface_color** | f32[4] | 3422 | `04000000 bada5a3f 00000000 00000000 0000803f` | **(0.8549, 0, 0, 1)** | **次表面色 = 红** |
| 22/24/16/1/25/26/27/28 | Tex0/t_basecolor/NormalMap/DetailMap/t_caustic/t_custom_ibl/t_reflection/t_refraction | 字符串槽 | — | — | (见贴图串区) | 8 槽 ↔ 8 贴图串（b_m/a/n/bump/caustic_uvva/fashion_qiangpi/reflection/refraction）|

## 3. 槽位组原文（文件头 @936，77 值 = 3 组）

- 组0（9）: `[3,4,47,38,22,17,16,26,23]` — 细分待定（宏槽 3,4 + 2 数值槽 + 4 贴图槽）
- 组1（34）: `[3..9, 40,39,42,41,47,38, 29,35,30,36,37,34,33,32, 46,45,43,44, 48, 22,24,16,1,25,26,27, 23]` ↔ 块1
- 组2（34）: `[3..9, 40,39,42,47,38, 29,35,36,31,37,34,33,32, 46,45,43,44, 48, 22,24,16,1,25,26,27,28, 23]` ↔ 块2

## 4. 交叉验证与结论

- **LOD0 004008.c159**：同结构、同两值块；四个颜色值逐字节一致（灰系/红系）；仅少数标量微差（如 detail_tilling 1.3→2.2）。颜色绑定 = 双文件一致。
- **宝石红 = 源参数驱动（确认）**：`u_crystal_color=(0.2431,0,0)` + `u_subsurface_color=(0.8549,0,0)` + `u_refraction_color=(1.0,0,0)`（skim_2）。护手银蓝 = skim_1 的灰系四色。
- **Sub0（刀刃，pbr_default）在 c159 中无覆写块** ⇒ 其 metallic/fresnel 等取引擎默认；渲染器刃口近似参数如实保留标注（不再宣称"待解析"）。
- **置信度**：颜色槽 = 高（双材料 × 双文件 × 类型精确对齐）；标量 = 中（正向对齐；3 个 i32 值(37/34/45)语义待定）；tint 映射模型 v1（0.5/0.3/0.2 权重）待与源 shader 公式最终对齐。
- **已接入**：`weapon_skin_pipeline.py --source --params-c159` → 由本表数值驱动晶体/宝石 tint，全部来源写入 `provenance.json`（含 src_file 与模型说明）。

## 5. v2 更新（通用化 + 测试 + 修正）

- **解析器通用化（c159_pair.py v3）**：去掉固定偏移/固定组号/固定两个材料块/固定文件名：
  - 名字表按首个 `*AnimParam` 串 + `t_basecolor` 自动切分（无 t_basecolor 的变体走 t_/u_ 回退；非材质文件清晰报错，不抛 IndexError）；
  - 槽位组 = 全文件 u16 段按**双字节对齐**扫描 + 垃圾段过滤 + 按 `TransparentMode` 槽位值分段（自动适配不同的 TransparentMode 索引）；
  - 数值块 = 条目按间隔<100B 聚簇（≥6 条），**不再用偏移区间**；
  - 块↔组 = 评分自动配对（颜色名↔数组/标量名↔标量 + 条数一致加分），不预设数量；
  - 材料↔组 = 与块配对成功的组按文件序对应晶体材料序，剩余材料留默认；
  - **`--params-c159` 接收实际路径**；SubMesh→Material 由同资产绑定文件自动建立（`003997` 类文件，按资产号 mid 校验，杜绝误配其他皮肤）。
- **"18/19" 疑问的解释**：旧版按偏移区间取"块"，区间右界顺手带进了下个材料段开头的 1 条字符串（b_m 路径），所以出现"18/19"。v3 按数值簇取块，输出显式统计（消耗条数/未消费条目/未匹配槽位），029 两材质块 = 19/19 与 18/18，无剩余。
- **跨 LOD / 跨资产测试（test_c159_parser.py，7/7）**：029 LOD0/L1/L2/L3 四文件自动解析一致（块[19,18]、配对评分 41/39、宝石红三色逐字节一致）；028 皮毛（不同 schema）、034 武器（无参数表）均无崩溃并正确提取材料/着色器；034 场景文件被清晰拒绝。
- **验证补充**：029 LOD1 vs LOD0 的组内容（19 槽/18 槽材料）语义一致（LOD0 索引整体 +1，因 Macro0–7 多一个宏槽）；小块差异（如 detail_tilling 1.3→2.2、caustic_brightness 1.24→1.29）为 LOD 版本差异，如实保留。
