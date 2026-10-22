# 绑定差异表（task-15）

> **更正（task-23 复核，2026-09-18）**：本表"其它槽"对 `t_surfacemap` 使用**全皮肤声明集合**比较，
> 导致 1110171 晶体 prim1/2/3/5/6 被误标"未绑定"。001265.c159 的晶体块**不声明** `t_surfacemap`
> （仅 weapon blk0/blk4 声明，manifest 已绑 `012_s_m`/`010_s_m`）⇒ 那 5 个 prim 属**源级正确**，该行作废。
> 真正未绑且源有声明的是 1110024 / 1110129 / 1110152（其 `*_s_m.png` 磁盘尚不存在）。详见
> `AB2_IBL顶替两组结果与定级_20260918.md` §4 第 4/4b 条。

口径：**源 c159 = `C159PARSE_skins_fixed.json` 的 `material_block/slot_class/ref` 直读**；当前 local_file 与 sha16 取自磁盘实际文件；A 组 = weapon prim 的 Tex0 改指同族 `*_a.png`。

## 1110024（c159=001386.c159，块 [0, 1, 2, 3, 4]；weapon 块 [0, 2, 3, 4] / crystal 块 [1]）
c159 weapon 块 Tex0 声明：['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] ｜ crystal 块 Tex0 声明：['skin_1006_004001s_m.tga']

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | — | src_tex/024_b_m.png | c98422dad01c0fe2 | ['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] | src_tex/024_a.png | 7f03f8c8d009639a | 024_a.png vs 024_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/024_b_m.png ⇒ 不符 |
| 1 | weapon | Tex0 | — | src_tex/024_b_m.png | c98422dad01c0fe2 | ['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] | src_tex/024_a.png | 7f03f8c8d009639a | 024_a.png vs 024_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/024_b_m.png ⇒ 不符 |
| 2 | weapon | Tex0 | — | src_tex/024_b_m.png | c98422dad01c0fe2 | ['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] | src_tex/024_a.png | 7f03f8c8d009639a | 024_a.png vs 024_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/024_b_m.png ⇒ 不符 |
| 3 | weapon | Tex0 | — | src_tex/024_b_m.png | c98422dad01c0fe2 | ['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] | src_tex/024_a.png | 7f03f8c8d009639a | 024_a.png vs 024_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/024_b_m.png ⇒ 不符 |
| 4 | weapon | Tex0 | — | src_tex/024_b_m.png | c98422dad01c0fe2 | ['skin_1006_004001a.tga', 'skin_1006_004_1001a.tga'] | src_tex/024_a.png | 7f03f8c8d009639a | 024_a.png vs 024_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/024_b_m.png ⇒ 不符 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/024_n.png | ['skin_1006_004001n.tga', 'skin_1006_004_1001n.tga'] | ok(名族同) | [0, 1, 2, 3, 4] |
| ParamMap | src_tex/024_m.png | ['skin_1006_004001m.tga', 'skin_1006_004_1001m.tga'] | ok(名族同) | [0, 1, 2, 3, 4] |
| t_basecolor | src_tex/024_a.png | ['skin_1006_004001a.tga'] | ok(名族同) | [0, 1, 2, 3, 4] |
| t_custom_ibl | src_cube/gdansk_shipyard_buildings.dds | ['indoor.cube'] | 名称不同 | [0, 1, 2, 3, 4] |
| t_surfacemap | — | ['skin_1006_004001s_m.tga', 'skin_1006_004_1001s_m.tga'] | 未绑定 | [0, 1, 2, 3, 4] |

## 1110129（c159=000334.c159，块 [0, 1, 2, 3]；weapon 块 [0, 1, 2, 3] / crystal 块 []）
c159 weapon 块 Tex0 声明：['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] ｜ crystal 块 Tex0 声明：[]

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | — | src_tex/008_b_m.png | 0f93b7948571f6c9 | ['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] | src_tex/008_a.png | b3f82249f64a7a33 | 008_a.png vs 008_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/008_b_m.png ⇒ 不符 |
| 1 | weapon | Tex0 | — | src_tex/008_c_b_m.png | 70e4de565cbaeb8a | ['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] | src_tex/008_c_a.png | c232fd2aa20527f1 | 008_c_a.png vs 008_c_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/008_c_b_m.png ⇒ 不符 |
| 2 | weapon | Tex0 | — | src_tex/008_d_b_m.png | 9f4cac6256e09893 | ['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] | src_tex/008_d_a.png | 7107460fcdeb3b8a | 008_d_a.png vs 008_d_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/008_d_b_m.png ⇒ 不符 |
| 3 | weapon | Tex0 | — | src_tex/008_e_b_m.png | 58badcda7b8e6eb5 | ['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] | src_tex/008_e_a.png | e7ace4ebfb21d4b8 | 008_e_a.png vs 008_e_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/008_e_b_m.png ⇒ 不符 |
| 4 | weapon | Tex0 | — | src_tex/008_f_b_m.png | 5d9c872381b3f1a0 | ['skin_1001_008001a.tga', 'skin_1001_008_1001a.tga', 'skin_1001_008_2001a.tga'] | src_tex/008_f_a.png | 4338d03349b4932e | 008_f_a.png vs 008_f_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/008_f_b_m.png ⇒ 不符 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/008_c_n.png | ['skin_1001_008001n.tga', 'skin_1001_008_1001n.tga', 'skin_1001_008_2001n.tga'] | ok(名族同) | [1] |
| NormalMap | src_tex/008_d_n.png | ['skin_1001_008001n.tga', 'skin_1001_008_1001n.tga', 'skin_1001_008_2001n.tga'] | ok(名族同) | [2] |
| NormalMap | src_tex/008_e_n.png | ['skin_1001_008001n.tga', 'skin_1001_008_1001n.tga', 'skin_1001_008_2001n.tga'] | ok(名族同) | [3] |
| NormalMap | src_tex/008_f_n.png | ['skin_1001_008001n.tga', 'skin_1001_008_1001n.tga', 'skin_1001_008_2001n.tga'] | ok(名族同) | [4] |
| NormalMap | src_tex/008_n.png | ['skin_1001_008001n.tga', 'skin_1001_008_1001n.tga', 'skin_1001_008_2001n.tga'] | ok(名族同) | [0] |
| ParamMap | — | ['skin_1001_008001m.tga', 'skin_1001_008_1001m.tga', 'skin_1001_008_2001m.tga'] | 未绑定 | [4] |
| ParamMap | src_tex/008_c_m.png | ['skin_1001_008001m.tga', 'skin_1001_008_1001m.tga', 'skin_1001_008_2001m.tga'] | ok(名族同) | [1] |
| ParamMap | src_tex/008_d_m.png | ['skin_1001_008001m.tga', 'skin_1001_008_1001m.tga', 'skin_1001_008_2001m.tga'] | ok(名族同) | [2] |
| ParamMap | src_tex/008_e_m.png | ['skin_1001_008001m.tga', 'skin_1001_008_1001m.tga', 'skin_1001_008_2001m.tga'] | ok(名族同) | [3] |
| ParamMap | src_tex/008_m.png | ['skin_1001_008001m.tga', 'skin_1001_008_1001m.tga', 'skin_1001_008_2001m.tga'] | ok(名族同) | [0] |
| t_basecolor | src_tex/008_a.png | — | c159 无该槽 | [0] |
| t_basecolor | src_tex/008_c_a.png | — | c159 无该槽 | [1] |
| t_basecolor | src_tex/008_d_a.png | — | c159 无该槽 | [2] |
| t_basecolor | src_tex/008_e_a.png | — | c159 无该槽 | [3] |
| t_custom_ibl | src_cube/qiangpi.dds | — | c159 无该槽 | [0, 1, 2, 3, 4] |
| t_surfacemap | — | ['skin_1001_008001s_m.tga', 'skin_1001_008_1001s_m.tga', 'skin_1001_008_2001s_m.tga'] | 未绑定 | [0, 1, 2, 3, 4] |

## 1110145（c159=000654.c159，块 [0, 1, 2, 3, 4]；weapon 块 [0, 2, 3, 4] / crystal 块 [1]）
c159 weapon 块 Tex0 声明：['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] ｜ crystal 块 Tex0 声明：['skin_1001_014001b_m.tga']

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 1 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 2 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 3 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 4 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 5 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |
| 6 | weapon | Tex0 | weapon\skin\skin_1001_014\textures\skin_1001_014001b_m.tga | src_tex/014_b_m.png | bcfa541e2e2bd841 | ['skin_1001_014001a.tga', 'skin_1001_014_1001a.tga'] | src_tex/014_a.png | d5964ac91d0e3cc1 | 014_a.png vs 014_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/014_b_m.png ⇒ 不符 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/014_n.png | ['skin_1001_014001n.tga', 'skin_1001_014_1001m.tga'] | ok(名族同) | [0, 1, 2, 3, 4, 5, 6] |
| ParamMap | src_tex/014_m.png | ['skin_1001_014001m.tga'] | ok(名族同) | [0, 1, 2, 3, 4, 5, 6] |
| t_basecolor | src_tex/014_a.png | ['skin_1001_014001a.tga'] | ok(名族同) | [0, 1, 2, 3, 4, 5, 6] |
| t_custom_ibl | src_cube/bg61f_light_spherereflectioncapture_1.dds | ['bg61f_light_spherereflectioncapture_1.cube'] | 名称不同 | [0, 1, 2, 3, 4, 5, 6] |
| t_surfacemap | src_tex/014_s_m.png | ['skin_1001_014001s_m.tga'] | ok(名族同) | [0, 1, 2, 3, 4, 5, 6] |

## 1110152（c159=002731.c159，块 [0, 1]；weapon 块 [0, 1] / crystal 块 []）
c159 weapon 块 Tex0 声明：['skin_1012_009001a.tga', 'skin_1012_009_1001a.tga'] ｜ crystal 块 Tex0 声明：[]

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | — | src_tex/009_b_m.png | b087bb70d0967c3f | ['skin_1012_009001a.tga', 'skin_1012_009_1001a.tga'] | src_tex/009_a.png | 632ddb54d19ead68 | 009_a.png vs 009_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/009_b_m.png ⇒ 不符 |
| 1 | weapon | Tex0 | — | src_tex/009_c_b_m.png | 969bc4bb812074fd | ['skin_1012_009001a.tga', 'skin_1012_009_1001a.tga'] | src_tex/009_c_a.png | c08f9a64e78773a7 | 009_c_a.png vs 009_c_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/009_c_b_m.png ⇒ 不符 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/009_c_n.png | ['skin_1012_009001n.tga', 'skin_1012_009_1001n.tga'] | ok(名族同) | [1] |
| NormalMap | src_tex/009_n.png | ['skin_1012_009001n.tga', 'skin_1012_009_1001n.tga'] | ok(名族同) | [0] |
| ParamMap | src_tex/009_c_m.png | ['skin_1012_009001m.tga', 'skin_1012_009_1001m.tga'] | ok(名族同) | [1] |
| ParamMap | src_tex/009_m.png | ['skin_1012_009001m.tga', 'skin_1012_009_1001m.tga'] | ok(名族同) | [0] |
| t_basecolor | src_tex/009_a.png | — | c159 无该槽 | [0] |
| t_basecolor | src_tex/009_c_a.png | — | c159 无该槽 | [1] |
| t_custom_ibl | src_cube/qiangpi.dds | ['qiangpi.cube'] | 名称不同 | [0, 1] |
| t_surfacemap | — | ['skin_1012_009001s_m.tga', 'skin_1012_009_1001s_m.tga'] | 未绑定 | [0, 1] |

## 1110165（c159=001631.c159，块 [0, 1, 2, 3]；weapon 块 [0, 1, 2] / crystal 块 [3]）
c159 weapon 块 Tex0 声明：['skin_1006_011001a.tga', 'skin_1006_011_1001a.tga'] ｜ crystal 块 Tex0 声明：['skin_1006_011_1001b_m.tga']

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | — | src_tex/165_b_m.png | 8801d31e863d6645 | ['skin_1006_011001a.tga', 'skin_1006_011_1001a.tga'] | src_tex/165_a.png | d89290e73d550a4d | 165_a.png vs 165_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/165_b_m.png ⇒ 不符 |
| 1 | weapon | Tex0 | — | src_tex/165_c_b_m.png | 0859c7d3a72284c7 | ['skin_1006_011001a.tga', 'skin_1006_011_1001a.tga'] | src_tex/165_c_a.png | 0a77bca79ca45c3d | 165_c_a.png vs 165_c_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/165_c_b_m.png ⇒ 不符 |
| 2 | weapon | Tex0 | — | src_tex/165_d_b_m.png | 49ec41d2f063f0a7 | ['skin_1006_011001a.tga', 'skin_1006_011_1001a.tga'] | src_tex/165_d_a.png | — | 165_d_a.png vs 165_d_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/165_d_b_m.png ⇒ 不符（A 组无法覆盖：同族 `_a.png` 磁盘缺失） |
| 3 | weapon | Tex0 | — | src_tex/165_e_b_m.png | 530d39b5fcca8dbb | ['skin_1006_011001a.tga', 'skin_1006_011_1001a.tga'] | src_tex/165_e_a.png | — | 165_e_a.png vs 165_e_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/165_e_b_m.png ⇒ 不符（A 组无法覆盖：同族 `_a.png` 磁盘缺失） |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/165_c_n.png | ['skin_1006_011001n.tga', 'skin_1006_011_1001n.tga'] | ok(名族同) | [1, 3] |
| NormalMap | src_tex/165_n.png | ['skin_1006_011001n.tga', 'skin_1006_011_1001n.tga'] | ok(名族同) | [0, 2] |
| ParamMap | src_tex/165_a.png | ['skin_1006_011001m.tga', 'skin_1006_011_1001m.tga'] | ok(名族同) | [0, 2] |
| ParamMap | src_tex/165_c_a.png | ['skin_1006_011001m.tga', 'skin_1006_011_1001m.tga'] | ok(名族同) | [1, 3] |
| t_basecolor | src_tex/165_b_m.png | ['skin_1006_011_1001a.tga'] | 名称不同 | [0] |
| t_basecolor | src_tex/165_c_b_m.png | ['skin_1006_011_1001a.tga'] | 名称不同 | [1] |
| t_basecolor | src_tex/165_d_b_m.png | ['skin_1006_011_1001a.tga'] | 名称不同 | [2] |
| t_basecolor | src_tex/165_e_b_m.png | ['skin_1006_011_1001a.tga'] | 名称不同 | [3] |
| t_custom_ibl | src_cube/glazed_patio.dds | ['bonifacio_street.cube', 'qiangpi.cube'] | 名称不同 | [2, 3] |
| t_custom_ibl | src_cube/qiangpi.dds | ['bonifacio_street.cube', 'qiangpi.cube'] | 名称不同 | [0, 1] |
| t_surfacemap | src_tex/165_s_m.png | ['skin_1006_011001s_m.tga', 'skin_1006_011_1001s_m.tga'] | ok(名族同) | [0, 1, 2, 3] |

## 1110171（c159=001265.c159，块 [0, 1, 2, 3, 4, 5, 6]；weapon 块 [0, 4] / crystal 块 [1, 2, 3, 5]）
c159 weapon 块 Tex0 声明：['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] ｜ crystal 块 Tex0 声明：['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga']

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | weapon\skin\skin_1003_012\textures\skin_1003_012001b_m.tga | src_tex/012_b_m.png | fddc36be831b17f1 | ['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] | src_tex/012_a.png | 9c703956ac3dacf6 | 012_a.png vs 012_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/012_b_m.png ⇒ 不符 |
| 1 | crystal | Tex0 | weapon\skin\skin_1003_012\textures\skin_1003_012001b_m.tga | src_tex/012_b_m.png | fddc36be831b17f1 | ['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga'] | src_tex/012_a.png | 9c703956ac3dacf6 | 012_a.png vs 012_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |
| 2 | crystal | Tex0 | weapon\skin\skin_1003_012\textures\skin_1003_012001b_m.tga | src_tex/012_b_m.png | fddc36be831b17f1 | ['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga'] | src_tex/012_a.png | 9c703956ac3dacf6 | 012_a.png vs 012_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |
| 3 | crystal | Tex0 | weapon\skin\skin_1003_012\textures\skin_1003_012001b_m.tga | src_tex/012_b_m.png | fddc36be831b17f1 | ['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga'] | src_tex/012_a.png | 9c703956ac3dacf6 | 012_a.png vs 012_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |
| 4 | weapon | Tex0 | weapon\skin\skin_1003_010\textures\skin_1003_010001b_m.tga | src_tex/010_b_m.png | 6e1684657f4954e5 | ['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] | src_tex/010_a.png | 12abe6f0b22682c1 | 010_a.png vs 010_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/010_b_m.png ⇒ 不符 |
| 5 | crystal | Tex0 | weapon\skin\skin_1003_010\textures\skin_1003_010001b_m.tga | src_tex/010_b_m.png | 6e1684657f4954e5 | ['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga'] | src_tex/010_a.png | 12abe6f0b22682c1 | 010_a.png vs 010_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |
| 6 | crystal | Tex0 | weapon\skin\skin_1003_010\textures\skin_1003_010001b_m.tga | src_tex/010_b_m.png | 6e1684657f4954e5 | ['skin_1003_010001b_m.tga', 'skin_1003_012001b_m.tga'] | src_tex/010_a.png | 12abe6f0b22682c1 | 010_a.png vs 010_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/010_n.png | ['skin_1003_010001n.tga', 'skin_1003_012001n.tga'] | ok(名族同) | [4, 5, 6] |
| NormalMap | src_tex/012_n.png | ['skin_1003_010001n.tga', 'skin_1003_012001n.tga'] | ok(名族同) | [0, 1, 2, 3] |
| ParamMap | — | ['skin_1003_010001m.tga', 'skin_1003_012001m.tga'] | 未绑定 | [1, 2, 3, 5, 6] |
| ParamMap | src_tex/010_m.png | ['skin_1003_010001m.tga', 'skin_1003_012001m.tga'] | ok(名族同) | [4] |
| ParamMap | src_tex/012_m.png | ['skin_1003_010001m.tga', 'skin_1003_012001m.tga'] | ok(名族同) | [0] |
| t_basecolor | — | ['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] | 未绑定 | [6] |
| t_basecolor | src_tex/010_a.png | ['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] | ok(名族同) | [4, 5] |
| t_basecolor | src_tex/012_a.png | ['skin_1003_010001a.tga', 'skin_1003_012001a.tga'] | ok(名族同) | [0, 1, 2, 3] |
| t_custom_ibl | src_cube/car_studio01.dds | ['car_studio01.cube', 'qiangpi.cube'] | 名称不同 | [1, 3, 5, 6] |
| t_custom_ibl | src_cube/fashion_qiangpi.dds | ['car_studio01.cube', 'qiangpi.cube'] | 名称不同 | [2] |
| t_custom_ibl | src_cube/qiangpi.dds | ['car_studio01.cube', 'qiangpi.cube'] | 名称不同 | [0, 4] |
| t_surfacemap | — | ['skin_1003_010001s_m.tga', 'skin_1003_012001s_m.tga'] | 未绑定 | [1, 2, 3, 5, 6] |
| t_surfacemap | src_tex/010_s_m.png | ['skin_1003_010001s_m.tga', 'skin_1003_012001s_m.tga'] | ok(名族同) | [4] |
| t_surfacemap | src_tex/012_s_m.png | ['skin_1003_010001s_m.tga', 'skin_1003_012001s_m.tga'] | ok(名族同) | [0] |

## 1110177（c159=003996.c159，块 [0, 1, 2]；weapon 块 [0] / crystal 块 [1, 2]）
c159 weapon 块 Tex0 声明：['skin_2003_029001a.tga'] ｜ crystal 块 Tex0 声明：['skin_2003_029001b_m.tga']

| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | weapon | Tex0 | weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga | src_tex/029_b_m.png | 6349a3f2f761f83f | ['skin_2003_029001a.tga'] | src_tex/029_a.png | 0082f6ec8caa7dca | 029_a.png vs 029_b_m.png | weapon：c159 全块声明 Tex0=*a；当前 src_tex/029_b_m.png ⇒ 不符 |
| 1 | crystal | Tex0 | weapon\skin\skin_2003_029\textures\skin_2003_029001b_m.tga | src_tex/029_b_m.png | 6349a3f2f761f83f | ['skin_2003_029001b_m.tga'] | src_tex/029_a.png | 0082f6ec8caa7dca | 029_a.png vs 029_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |
| 2 | crystal | Tex0 | weapon\skin\skin_2003_029\textures\skin_2003_029001b_m.tga | src_tex/029_b_m.png | 6349a3f2f761f83f | ['skin_2003_029001b_m.tga'] | src_tex/029_a.png | 0082f6ec8caa7dca | 029_a.png vs 029_b_m.png | crystal：c159 声明 Tex0=*_b_m（掩码），当前 符合 |

其它槽（汇总，prim 列表）：
| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |
|---|---|---|---|---|
| NormalMap | src_tex/029_n.png | ['skin_2003_029001n.tga'] | ok(名族同) | [0, 1, 2] |
| ParamMap | — | ['skin_2003_029001m.tga'] | 未绑定 | [1, 2] |
| ParamMap | src_tex/029_m.png | ['skin_2003_029001m.tga'] | ok(名族同) | [0] |
| t_basecolor | — | ['skin_2003_029001a.tga'] | 未绑定 | [1, 2] |
| t_basecolor | src_tex/029_b_m.png | ['skin_2003_029001a.tga'] | 名称不同 | [0] |
| t_custom_ibl | src_cube/car_studio01.dds | ['car_studio01.cube', 'fashion_qiangpi.cube', 'qiangpi.cube'] | 名称不同 | [1] |
| t_custom_ibl | src_cube/fashion_qiangpi.dds | ['car_studio01.cube', 'fashion_qiangpi.cube', 'qiangpi.cube'] | 名称不同 | [2] |
| t_custom_ibl | src_cube/qiangpi.dds | ['car_studio01.cube', 'fashion_qiangpi.cube', 'qiangpi.cube'] | 名称不同 | [0] |
| t_surfacemap | src_tex/029_s_m.png | — | c159 无该槽 | [0] |
