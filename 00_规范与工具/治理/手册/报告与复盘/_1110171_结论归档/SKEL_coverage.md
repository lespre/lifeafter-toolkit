# 骨骼定位全量覆盖率报告（task-33）

工具：`01拆包器本体\工具库\06_皮肤定位链\locate_skeleton.py`（`--id/--gim/--all --out`）
名单：`_target_1110171/ROSTER_g5_g6.json`（典藏 L5 22 行 + 传世 L6 15 行 = **37 个 id / 34 个不同模型**）

## 一、优化前后对比

| 口径 | 骨骼数>0 | 占比 | 失败 | 说明 |
|---|---|---|---|---|
| v1 仅主 stem `.mesh` | 21/37 | 56.8% | 16 | `--no-variant-fallback` |
| v2 主+变体回退（当前） | 24/37 | 64.9% | 13 | 变体序：`_lod01.._lod03/_preview/_shadow/_1/_2/_3` |

变体回退修好的 3 个 id：1110021（`_2`, 18 骨）、1110129（`_2`, 8 骨）、1110032（`_1`, 52 骨）

## 二、逐皮肤表（37 行）

| id | 中文名 | gim | mesh 行号 | 骨骼数 | 骨骼名条数 | 层级 | 状态/原因 |
|---|---|---|---|---|---|---|---|
| 1110013 | 幻影狩蝎 | weapon/skin/skin_1006_002/skin_1006_002.gim | 1310 | 14 | 14 | verified_parent_lt_child | OK |
| 1110021 | 紫焰蛇矛 | weapon/skin/skin_2003_005/skin_2003_005.gim | 3406 | 18 | 18 | verified_parent_lt_child | OK |
| 1110022 | 赤蛇御火 | weapon/skin/skin_1007_002/skin_1007_002.gim | 1715 | 13 | 13 | verified_parent_lt_child | OK |
| 1110024 | 金蟒啸焰 | weapon/skin/skin_1006_004/skin_1006_004.gim | 1373 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110031 | 沧鳞破浪 | weapon/skin/skin_1001_004/skin_1001_004.gim | 249 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110032 | 九霄狐啸 | weapon/skin/skin_1013_003/skin_1013_003.gim | 3066 | 52 | 52 | unresolved_violations | OK |
| 1110036 | 森林之主 | weapon/skin/skin_1007_004/skin_1007_004.gim | 1813 | 13 | 13 | verified_parent_lt_child | OK |
| 1110121 | 极狐破坏者 | weapon/skin/skin_1003_005/skin_1003_005.gim | 1121 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110128 | 诡秘之颅 | weapon/skin/skin_2003_019/skin_2003_019.gim | 3774 | 19 | 19 | verified_parent_lt_child | OK |
| 1110129 | 熔炉寒霜 | weapon/skin/skin_1001_008/skin_1001_008.gim | 338 | 15 | 15 | verified_parent_lt_child | OK |
| 1110137 | 焚古龙息 | weapon/skin/skin_1013_007/skin_1013_007.gim | 3168 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110145 | 天马行空 | weapon/skin/skin_1001_014/skin_1001_014.gim | 653 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 11101451 | 天马行空（14天） | weapon/skin/skin_1001_014/skin_1001_014.gim | 653 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110146 | 龙渊永寂 | weapon/skin/skin_1002_007/skin_1002_007.gim | 869 | 4 | 4 | verified_parent_lt_child | OK |
| 1110151 | 阿赖耶识 | weapon/skin/skin_2003_022/skin_2003_022.gim | 3857 | 2 | 2 | verified_parent_lt_child | OK |
| 1110152 | 灵态诱导 | weapon/skin/skin_1012_009/skin_1012_009.gim | 2718 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110165 | 墨隐麒麟 | weapon/skin/skin_1006_011/skin_1006_011.gim | 1618 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110169 | 灰色协议 | weapon/skin/skin_1002_009/skin_1002_009.gim | 912 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 11101691 | 灰色协议（14天） | weapon/skin/skin_1002_009/skin_1002_009.gim | 912 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110171 | 光影咏叹调 | weapon/skin/skin_1003_010/skin_1003_010.gim | 1210 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110177 | 极光剑 | weapon/skin/skin_2003_029/skin_2003_029.gim | 3995 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 11101771 | 极光剑（7天） | weapon/skin/skin_2003_029/skin_2003_029.gim | 3995 | 0 | 0 | - | no_weapon_skeleton__gim_binding_only |
| 1110115 | - | weapon/skin/skin_2003_013/skin_2003_013.gim | 3606 | 5 | 5 | verified_parent_lt_child | OK |
| 1110116 | - | weapon/skin/skin_2003_017/skin_2003_017.gim | 3685 | 35 | 35 | verified_parent_lt_child | OK |
| 1110117 | - | weapon/skin/skin_2003_018/skin_2003_018.gim | 3729 | 28 | 28 | verified_parent_lt_child | OK |
| 1110131 | - | weapon/skin/skin_1006_008/skin_1006_008.gim | 1461 | 22 | 22 | verified_parent_lt_child | OK |
| 1110132 | - | weapon/skin/skin_1006_009/skin_1006_009.gim | 1504 | 34 | 34 | verified_parent_lt_child | OK |
| 1110133 | - | weapon/skin/skin_1006_010/skin_1006_010.gim | 1549 | 49 | 49 | verified_parent_lt_child | OK |
| 1110142 | - | weapon/skin/skin_1007_007/skin_1007_007.gim | 2013 | 13 | 13 | verified_parent_lt_child | OK |
| 1110143 | - | weapon/skin/skin_1007_008/skin_1007_008.gim | 2097 | 13 | 13 | verified_parent_lt_child | OK |
| 1110144 | - | weapon/skin/skin_1007_009/skin_1007_009.gim | 2226 | 13 | 13 | verified_parent_lt_child | OK |
| 1110159 | - | weapon/skin/skin_1001_011/skin_1001_011.gim | 462 | 41 | 41 | verified_parent_lt_child | OK |
| 1110160 | - | weapon/skin/skin_1001_012/skin_1001_012.gim | 518 | 46 | 46 | unresolved_violations | OK |
| 1110161 | - | weapon/skin/skin_1001_013/skin_1001_013.gim | 574 | 46 | 46 | unresolved_violations | OK |
| 1110173 | - | weapon/skin/skin_1012_011/skin_1012_011.gim | 2778 | 11 | 11 | verified_parent_lt_child | OK |
| 1110174 | - | weapon/skin/skin_1012_012/skin_1012_012.gim | 2835 | 43 | 43 | verified_parent_lt_child | OK |
| 1110175 | - | weapon/skin/skin_1012_013/skin_1012_013.gim | 2893 | 43 | 43 | verified_parent_lt_child | OK |

## 三、失败分类计数（v2）

- `no_weapon_skeleton__gim_binding_only` × **13 id**（10 个不同模型）

## 四、失败类归因与「资源是否真不在容器里」的证据

`no_weapon_skeleton__gim_binding_only` 共 13 id / 10 个不同模型。判据（四重）：

1. **该皮肤全部 mesh 变体 flag=0**（逐条列出变体与 flag，见 `SKEL_coverage.json` 的 `mesh_variants_checked`）；
2. **`biped` 串计数 = 0**（与带骨骼皮肤 `biped == bone_count` 完全对应，双重判据）；
3. **`.gim` 模型文档**：这些 gim **无 `CutBones`**（带骨骼皮肤 21/21 有、无骨骼皮肤 0/13 有），但**有 `MatrixToBone` + `Socket_*`**（13/13）⇒ 源侧语义为该网格以绑定矩阵挂到**角色侧骨骼/插槽**，武器资产本身不含骨骼；
4. **64 条扩展名/命名探测**（`_skeleton/_skel/_bone/_bones/_rig/_root/_bind` × `.skeleton/.skel/.bone/.bones/.rig/.bind/.bnd/.anim`）全部 0 命中。

扫描范围（容器级证据）：可表寻址 .gpk **56 个**（res 55 + res.gpk 1；`Documents\gres` 的 35 个头部不是 HPGF/FPGH、格式不同未解）。逐表行数：

```
building_01.gpk                      32325
building_02.gpk                      1810
building_03.gpk                      33455
building_04.gpk                      16062
character_01.gpk                     47390
character_02.gpk                     22914
character_03.gpk                     21246
character_04.gpk                     58704
character_05.gpk                     77827
character_06.gpk                     21160
character_07.gpk                     39991
character_08.gpk                     41655
character_09.gpk                     22902
effect_01.gpk                        212152
effect_02.gpk                        3049
effect_cache.gpk                     99801
model_01.gpk                         22611
model_02.gpk                         17488
model_03.gpk                         18895
model_04.gpk                         9890
model_05.gpk                         17737
model_06.gpk                         15275
model_07.gpk                         11281
model_08.gpk                         11932
model_09.gpk                         17582
model_10.gpk                         16396
model_11.gpk                         7966
model_high_2024_01.gpk               10012
model_high_2024_02.gpk               1058
model_high_2024_03.gpk               16127
model_high_2024_04.gpk               22142
model_high_2024_05.gpk               12046
model_high_2024_06.gpk               3449
res.gpk                              19600
scene_01.gpk                         84295
scene_02.gpk                         110664
scene_03.gpk                         79144
scene_04.gpk                         70841
scene_05.gpk                         2759
scene_bw_01.gpk                      147403
scene_bw_02.gpk                      135552
scene_bw_03.gpk                      51043
scene_bw_04.gpk                      92261
scene_bw_05.gpk                      92934
sound.gpk                            1436
textures.gpk                         564
textures_bw.gpk                      614
ui_01.gpk                            79769
ui_02.gpk                            7764
ui_03.gpk                            4922
ui_04.gpk                            30003
ui_05.gpk                            25583
utility.gpk                          21426
utility_scene.gpk                    8097
video.gpk                            306
weapon.gpk                           51665
```

## 五、骨骼块字段与偏移依据（本批 21 个带骨骼网格实证）

| 字段 | 偏移/规则 | 依据 |
|---|---|---|
| magic | `34 80 c8 bb` @0x00 | 21/21 |
| version | u16@0x04 = 4 | 34/34 |
| const | u16@0x06 = 5 | 34/34 |
| bone_flag | u16@0x08（无骨骼时 0，且 u32@0x0A=文件长度-16） | 21/21 ↔ 13/13 |
| bone_count | u16@0x0A | 与 `biped` 串数完全相等 21/21 |
| 父索引区 | byte[0x0D .. 0x0D+n-1]（0xFF=无父） | 19/21 零违规（1110160/1110161 违规→层级 unresolved，原始字节已存档） |
| 骨名区 | 起 0x0C+n，**步长 32 B** | 21/21 通过 32 步长校验；16/24/48/64 全 0 命中 |
| 逐骨块 | 骨名区尾+1，**92 B × n**，尾随 1×u32 | `sub_table_off - names_end == 1 + 92n + 4` 21/21 |
| sub 表 | 逐骨块之后 | `term==1, tv==Σvc, tf==Σfc` 三重校验（同 mesh_parse2） |

未定证（写 unresolved，不猜）：逐骨 92 B 块的字段语义；1110160/1110161 的父索引编号口径。
