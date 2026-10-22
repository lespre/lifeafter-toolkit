# 37 个典藏/传世皮肤 · 骨骼复原产出总表（task-36）

源：`E:\la拆包项目\03拆包产物\_target_1110171\ROSTER_g5_g6.json`；产出：`03拆包产物\_gim_out\skel\<id>_skeleton.json|.glb`（有骨架）、`<id>_mount.json`（无骨架）

工具：`01拆包器本体\工具库\06_皮肤定位链\locate_skeleton.py`（.gpk path→entry + .mesh v4 骨骼块）


## 汇总

| 口径 | 数值 |
|---|---|
| id 行数（典藏 L5 22 + 传世 L6 15） | 37 |
| 不同模型（按 gim 去重） | 34 |
| `.mesh` 命中 | 37/37 = 100% |
| **有骨架（bone_count>0）** | **24/37 = 64.9%**（优化前 21/37 = 56.8%，+3：1110021→`_2`、1110129→`_2`、1110032→`_1`） |
| **无骨架（源侧无骨骼块）** | **13/37**（10 个不同模型；四重证据见文末） |
| 骨架资产 `.glb`（仅骨骼节点+层级，无几何） | 24 个，头部/JSON 校验全部通过 |
| 挂点复原 `.mount.json` | 13 个，`MatrixToBone` 记录全部取到（含 socket 级 6~8 条/模型） |

失败分类计数：`no_weapon_skeleton__gim_binding_only = 13`（其余 0）


## 典藏 L5（22 行）

| # | id | 中文名 | gim | mesh(容器#行) | 骨骼数 | 无骨架 | 产出 | status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1110013 | 幻影狩蝎 | `weapon\skin\skin_1006_002\skin_1006_002.gim` | weapon.gpk#1310 | 14 | 否 | `1110013_skeleton.glb` + `.json` | ok |
| 2 | 1110021 | 紫焰蛇矛 | `weapon\skin\skin_2003_005\skin_2003_005.gim` | weapon.gpk#3406 | 18 | 否 | `1110021_skeleton.glb` + `.json` | ok |
| 3 | 1110022 | 赤蛇御火 | `weapon\skin\skin_1007_002\skin_1007_002.gim` | weapon.gpk#1715 | 13 | 否 | `1110022_skeleton.glb` + `.json` | ok |
| 4 | 1110024 | 金蟒啸焰 | `weapon\skin\skin_1006_004\skin_1006_004.gim` | weapon.gpk#1373 | 0 | 是 | `1110024_mount.json` | no_skeleton__mount_recovered |
| 5 | 1110031 | 沧鳞破浪 | `weapon\skin\skin_1001_004\skin_1001_004.gim` | weapon.gpk#249 | 0 | 是 | `1110031_mount.json` | no_skeleton__mount_recovered |
| 6 | 1110032 | 九霄狐啸 | `weapon\skin\skin_1013_003\skin_1013_003.gim` | weapon.gpk#3066 | 52 | 否 | `1110032_skeleton.glb` + `.json` | ok_with_selfcheck_warning |
| 7 | 1110036 | 森林之主 | `weapon\skin\skin_1007_004\skin_1007_004.gim` | weapon.gpk#1813 | 13 | 否 | `1110036_skeleton.glb` + `.json` | ok |
| 8 | 1110121 | 极狐破坏者 | `weapon\skin\skin_1003_005\skin_1003_005.gim` | weapon.gpk#1121 | 0 | 是 | `1110121_mount.json` | no_skeleton__mount_recovered |
| 9 | 1110128 | 诡秘之颅 | `weapon\skin\skin_2003_019\skin_2003_019.gim` | weapon.gpk#3774 | 19 | 否 | `1110128_skeleton.glb` + `.json` | ok |
| 10 | 1110129 | 熔炉寒霜 | `weapon\skin\skin_1001_008\skin_1001_008.gim` | weapon.gpk#338 | 15 | 否 | `1110129_skeleton.glb` + `.json` | ok |
| 11 | 1110137 | 焚古龙息 | `weapon\skin\skin_1013_007\skin_1013_007.gim` | weapon.gpk#3168 | 0 | 是 | `1110137_mount.json` | no_skeleton__mount_recovered |
| 12 | 1110145 | 天马行空 | `weapon\skin\skin_1001_014\skin_1001_014.gim` | weapon.gpk#653 | 0 | 是 | `1110145_mount.json` | no_skeleton__mount_recovered |
| 13 | 1110146 | 龙渊永寂 | `weapon\skin\skin_1002_007\skin_1002_007.gim` | weapon.gpk#869 | 4 | 否 | `1110146_skeleton.glb` + `.json` | ok |
| 14 | 1110151 | 阿赖耶识 | `weapon\skin\skin_2003_022\skin_2003_022.gim` | weapon.gpk#3857 | 2 | 否 | `1110151_skeleton.glb` + `.json` | ok |
| 15 | 1110152 | 灵态诱导 | `weapon\skin\skin_1012_009\skin_1012_009.gim` | weapon.gpk#2718 | 0 | 是 | `1110152_mount.json` | no_skeleton__mount_recovered |
| 16 | 1110165 | 墨隐麒麟 | `weapon\skin\skin_1006_011\skin_1006_011.gim` | weapon.gpk#1618 | 0 | 是 | `1110165_mount.json` | no_skeleton__mount_recovered |
| 17 | 1110169 | 灰色协议 | `weapon\skin\skin_1002_009\skin_1002_009.gim` | weapon.gpk#912 | 0 | 是 | `1110169_mount.json` | no_skeleton__mount_recovered |
| 18 | 1110171 | 光影咏叹调 | `weapon\skin\skin_1003_010\skin_1003_010.gim` | weapon.gpk#1210 | 0 | 是 | `1110171_mount.json` | no_skeleton__mount_recovered |
| 19 | 1110177 | 极光剑 | `weapon\skin\skin_2003_029\skin_2003_029.gim` | weapon.gpk#3995 | 0 | 是 | `1110177_mount.json` | no_skeleton__mount_recovered |
| 20 | 11101451 | 天马行空（14天） | `weapon\skin\skin_1001_014\skin_1001_014.gim` | weapon.gpk#653 | 0 | 是 | `11101451_mount.json` | no_skeleton__mount_recovered |
| 21 | 11101691 | 灰色协议（14天） | `weapon\skin\skin_1002_009\skin_1002_009.gim` | weapon.gpk#912 | 0 | 是 | `11101691_mount.json` | no_skeleton__mount_recovered |
| 22 | 11101771 | 极光剑（7天） | `weapon\skin\skin_2003_029\skin_2003_029.gim` | weapon.gpk#3995 | 0 | 是 | `11101771_mount.json` | no_skeleton__mount_recovered |

## 传世 L6（15 行）

| # | id | 中文名 | gim | mesh(容器#行) | 骨骼数 | 无骨架 | 产出 | status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1110115 | *(传世表无名，未取到)* | `weapon\skin\skin_2003_013\skin_2003_013.gim` | weapon.gpk#3606 | 5 | 否 | `1110115_skeleton.glb` + `.json` | ok |
| 2 | 1110116 | *(传世表无名，未取到)* | `weapon\skin\skin_2003_017\skin_2003_017.gim` | weapon.gpk#3685 | 35 | 否 | `1110116_skeleton.glb` + `.json` | ok |
| 3 | 1110117 | *(传世表无名，未取到)* | `weapon\skin\skin_2003_018\skin_2003_018.gim` | weapon.gpk#3729 | 28 | 否 | `1110117_skeleton.glb` + `.json` | ok |
| 4 | 1110131 | *(传世表无名，未取到)* | `weapon\skin\skin_1006_008\skin_1006_008.gim` | weapon.gpk#1461 | 22 | 否 | `1110131_skeleton.glb` + `.json` | ok |
| 5 | 1110132 | *(传世表无名，未取到)* | `weapon\skin\skin_1006_009\skin_1006_009.gim` | weapon.gpk#1504 | 34 | 否 | `1110132_skeleton.glb` + `.json` | ok |
| 6 | 1110133 | *(传世表无名，未取到)* | `weapon\skin\skin_1006_010\skin_1006_010.gim` | weapon.gpk#1549 | 49 | 否 | `1110133_skeleton.glb` + `.json` | ok |
| 7 | 1110142 | *(传世表无名，未取到)* | `weapon\skin\skin_1007_007\skin_1007_007.gim` | weapon.gpk#2013 | 13 | 否 | `1110142_skeleton.glb` + `.json` | ok |
| 8 | 1110143 | *(传世表无名，未取到)* | `weapon\skin\skin_1007_008\skin_1007_008.gim` | weapon.gpk#2097 | 13 | 否 | `1110143_skeleton.glb` + `.json` | ok |
| 9 | 1110144 | *(传世表无名，未取到)* | `weapon\skin\skin_1007_009\skin_1007_009.gim` | weapon.gpk#2226 | 13 | 否 | `1110144_skeleton.glb` + `.json` | ok |
| 10 | 1110159 | *(传世表无名，未取到)* | `weapon\skin\skin_1001_011\skin_1001_011.gim` | weapon.gpk#462 | 41 | 否 | `1110159_skeleton.glb` + `.json` | ok |
| 11 | 1110160 | *(传世表无名，未取到)* | `weapon\skin\skin_1001_012\skin_1001_012.gim` | weapon.gpk#518 | 46 | 否 | `1110160_skeleton.glb` + `.json` | ok_with_selfcheck_warning |
| 12 | 1110161 | *(传世表无名，未取到)* | `weapon\skin\skin_1001_013\skin_1001_013.gim` | weapon.gpk#574 | 46 | 否 | `1110161_skeleton.glb` + `.json` | ok_with_selfcheck_warning |
| 13 | 1110173 | *(传世表无名，未取到)* | `weapon\skin\skin_1012_011\skin_1012_011.gim` | weapon.gpk#2778 | 11 | 否 | `1110173_skeleton.glb` + `.json` | ok |
| 14 | 1110174 | *(传世表无名，未取到)* | `weapon\skin\skin_1012_012\skin_1012_012.gim` | weapon.gpk#2835 | 43 | 否 | `1110174_skeleton.glb` + `.json` | ok |
| 15 | 1110175 | *(传世表无名，未取到)* | `weapon\skin\skin_1012_013\skin_1012_013.gim` | weapon.gpk#2893 | 43 | 否 | `1110175_skeleton.glb` + `.json` | ok |

## 有骨架 24 个：层级树前 3 层（原样骨名）


### 1110013（幻影狩蝎，14 骨，roots=[0]，自检 通过）

```
biped root
`-- biped_bone00
    |-- biped_bone01
    |-- biped_bone02
    |-- biped_bone03
    |-- biped_bone04
    |-- biped_bone05
    |-- biped_bone06
    |-- biped_bone07
    |-- biped_bone08
    |-- biped_bone09
    |-- biped_bone10
    |-- biped_bone11
    `-- biped_bone12
```

### 1110021（紫焰蛇矛，18 骨，roots=[0, 17]，自检 通过）

```
biped bone00
|-- biped bone01
|   `-- biped bone11
|-- biped bone03
|   `-- biped bone04
|-- biped bone06
|   `-- biped bone07
`-- biped bone08
    `-- biped bone09
biped root
```

### 1110022（赤蛇御火，13 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone07
    `-- biped bone09
```

### 1110032（九霄狐啸，52 骨，roots=[0]，自检 见警告）

```
biped root
`-- biped bone00
    |-- biped bone03
    |-- biped bone07
    |-- biped bone53
    |-- biped bone54
    |-- biped bone55
    |-- biped bone56
    |-- biped bone57
    |-- biped bone58
    `-- biped bone59
```
`parent<self` 违规：[{"bone": 2, "parent": 3}, {"bone": 4, "parent": 5}, {"bone": 5, "parent": 6}, {"bone": 7, "parent": 10}, {"bone": 8, "parent": 14}, {"bone": 9, "parent": 15}, {"bone": 10, "parent": 16}, {"bone": 11, "parent": 17}]

### 1110036（森林之主，13 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone07
    `-- biped bone09
```

### 1110128（诡秘之颅，19 骨，roots=[0, 18]，自检 通过）

```
biped bone00
|-- biped bone01
|-- biped bone03
|-- biped bone04
|-- biped bone05
|-- biped bone06
|-- biped bone07
|-- biped bone08
|-- biped bone09
|-- biped bone10
|-- biped bone11
|-- biped bone12
|-- biped bone13
|-- biped bone14
|-- biped bone15
|-- biped bone16
|-- biped bone17
`-- biped bone18
biped root
```

### 1110129（熔炉寒霜，15 骨，roots=[0, 14]，自检 通过）

```
biped bone00
|-- biped bone01
`-- biped bone02
    |-- biped bone04
    |-- biped bone05
    |-- biped bone06
    |-- biped bone08
    |-- biped bone09
    |-- biped bone10
    |-- biped bone11
    |-- biped bone17
    |-- biped bone18
    |-- biped bone19
    `-- biped bone20
biped root
```

### 1110146（龙渊永寂，4 骨，roots=[0, 3]，自检 通过）

```
biped bone00
|-- biped bone01
`-- biped bone02
biped root
```

### 1110151（阿赖耶识，2 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
```

### 1110115（-，5 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    `-- biped bone01
```

### 1110116（-，35 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone10
    |-- biped bone11
    |-- biped bone12
    |-- biped bone13
    |-- biped bone14
    |-- biped bone15
    |-- biped bone16
    |-- biped bone20
    |-- biped bone21
    |-- biped bone22
    |-- biped bone23
    |-- biped bone24
    |-- biped bone25
    |-- biped bone26
    |-- biped bone30
    |-- biped bone31
    |-- biped bone32
    |-- biped bone33
    |-- biped bone34
    |-- biped bone35
    |-- biped bone36
    |-- biped bone37
    |-- biped bone38
    |-- biped bone39
    |-- biped bone40
    |-- biped bone41
    |-- biped bone42
    |-- biped bone43
    |-- biped bone44
    `-- biped bone45
```

### 1110117（-，28 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone10
    |-- biped bone11
    |-- biped bone12
    |-- biped bone14
    |-- biped bone16
    |-- biped bone20
    |-- biped bone21
    |-- biped bone22
    |-- biped bone23
    |-- biped bone24
    |-- biped bone25
    |-- biped bone26
    |-- biped bone27
    |-- biped bone28
    |-- biped bone29
    |-- biped bone30
    |-- biped bone31
    |-- biped bone32
    |-- biped bone33
    |-- biped bone34
    |-- biped bone35
    |-- biped bone40
    `-- biped bone41
```

### 1110131（-，22 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone06
    |-- biped bone07
    |-- biped bone08
    |-- biped bone09
    |-- biped bone10
    |-- biped bone11
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    `-- biped bone22
```

### 1110132（-，34 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone06
    |-- biped bone07
    |-- biped bone08
    |-- biped bone09
    |-- biped bone10
    |-- biped bone11
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    |-- biped bone22
    |-- biped bone30
    |-- biped bone31
    |-- biped bone32
    |-- biped bone33
    |-- biped bone34
    |-- biped bone35
    |-- biped bone36
    |-- biped bone37
    `-- biped bone38
```

### 1110133（-，49 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone06
    |-- biped bone07
    |-- biped bone08
    |-- biped bone09
    |-- biped bone10
    |-- biped bone11
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    |-- biped bone22
    |-- biped bone30
    |-- biped bone31
    |-- biped bone32
    |-- biped bone33
    |-- biped bone34
    |-- biped bone35
    |-- biped bone36
    |-- biped bone37
    |-- biped bone38
    |-- biped bone39
    |-- biped bone40
    |-- biped bone41
    |-- biped bone42
    |-- biped bone43
    |-- biped bone52
    `-- biped bone53
```

### 1110142（-，13 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone07
    `-- biped bone09
```

### 1110143（-，13 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone07
    `-- biped bone09
```

### 1110144（-，13 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone01
    |-- biped bone03
    |-- biped bone04
    |-- biped bone05
    |-- biped bone07
    `-- biped bone09
```

### 1110159（-，41 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone04
    |-- biped bone10
    |-- biped bone12
    |-- biped bone15
    |-- biped bone16
    |-- biped bone17
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    |-- biped bone23
    |-- biped bone25
    |-- biped bone43
    |-- biped bone44
    |-- biped bone45
    `-- biped bone46
```

### 1110160（-，46 骨，roots=[0]，自检 见警告）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone04
    |-- biped bone10
    |-- biped bone12
    |-- biped bone15
    |-- biped bone16
    |-- biped bone17
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    |-- biped bone23
    |-- biped bone25
    |-- biped bone28
    |-- biped bone43
    |-- biped bone44
    |-- biped bone45
    `-- biped bone46
```
`parent<self` 违规：[{"bone": 29, "parent": 31}]

### 1110161（-，46 骨，roots=[0]，自检 见警告）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone02
    |-- biped bone04
    |-- biped bone10
    |-- biped bone12
    |-- biped bone15
    |-- biped bone16
    |-- biped bone17
    |-- biped bone18
    |-- biped bone19
    |-- biped bone20
    |-- biped bone21
    |-- biped bone23
    |-- biped bone25
    |-- biped bone43
    |-- biped bone44
    |-- biped bone45
    `-- biped bone46
```
`parent<self` 违规：[{"bone": 29, "parent": 31}]

### 1110173（-，11 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    |-- biped bone04
    `-- biped bone05
```

### 1110174（-，43 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    `-- biped bone29
```

### 1110175（-，43 骨，roots=[0]，自检 通过）

```
biped root
`-- biped bone00
    |-- biped bone01
    `-- biped bone29
```

## 无骨架 13 个：四重证据（逐条）

四重证据口径：① 该皮肤**全部** mesh 变体 `bone_flag=0`；② mesh 全文 `biped` 串计数 = 0；③ `.gim` 有 `MatrixToBone`+`Socket_*` 但**无** `CutBones`（有骨架 21/21 有 CutBones）；④ 64 个扩展探针（`.skeleton/.skel/.bone/.bones/.rig/.bind/.bnd/.anim` × 8 种后缀）0 命中。

| id | 变体数(全 flag0) | biped 串 | CutBones | MatrixToBone/插槽 | 探针 | 挂点文件 |
|---|---|---|---|---|---|---|
| 1110024 | 6 个（0,0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `1110024_mount.json` |
| 1110031 | 6 个（0,0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `1110031_mount.json` |
| 1110121 | 6 个（0,0,0,0,0,0） | 0 | False | True / 7 个 `Socket_*` | 64/0 命中 0 | `1110121_mount.json` |
| 1110137 | 5 个（0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `1110137_mount.json` |
| 1110145 | 5 个（0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `1110145_mount.json` |
| 1110152 | 5 个（0,0,0,0,0） | 0 | False | True / 7 个 `Socket_*` | 64/0 命中 0 | `1110152_mount.json` |
| 1110165 | 5 个（0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `1110165_mount.json` |
| 1110169 | 5 个（0,0,0,0,0） | 0 | False | True / 6 个 `Socket_*` | 64/0 命中 0 | `1110169_mount.json` |
| 1110171 | 5 个（0,0,0,0,0） | 0 | False | True / 7 个 `Socket_*` | 64/0 命中 0 | `1110171_mount.json` |
| 1110177 | 5 个（0,0,0,0,0） | 0 | False | True / 5 个 `Socket_*` | 64/0 命中 0 | `1110177_mount.json` |
| 11101451 | 5 个（0,0,0,0,0） | 0 | False | True / 8 个 `Socket_*` | 64/0 命中 0 | `11101451_mount.json` |
| 11101691 | 5 个（0,0,0,0,0） | 0 | False | True / 6 个 `Socket_*` | 64/0 命中 0 | `11101691_mount.json` |
| 11101771 | 5 个（0,0,0,0,0） | 0 | False | True / 5 个 `Socket_*` | 64/0 命中 0 | `11101771_mount.json` |

> 注：条目表是**匿名 hash 表**，name-MISS **不构成缺席证据**；因此第 ① ② ③ 条为**内容级**证据，第 ④ 条只用于说明"按命名约定找不到骨骼文件"，不作为唯一依据。


### 无骨架 id 的挂点复原（B 块）

| id | 主 MatrixToBone 偏移/字节 | 主矩阵（row-major 4x4） | 插槽（名·是否有矩阵） | 同段绑定的对象 |
|---|---|---|---|---|
| 1110024 | 1341 / 70 B | (-0.9999, 0, 0.0125, 0); (0, 1, 0, 0); (-0.0125, 0, -0.9999, 0); (-0.09, 0.46, 5, 1) | pifuguashi✔; rotation✔; fx01✔; bag✔; hongwai✔; sound✔; muzzle_fire✔; muzzle_fire_02✘ | [utility\utility_1680\utility_1680.gim, effect\fx\weapon\skin\skin_1006_004\fx_skin_1006_004_zishen.sfx, weapon\hongwai\hongwai01.gim] |
| 1110031 | 778 / 70 B | (-0.9999, 0, 0.0125, 0); (0, 1, 0, 0); (-0.0125, 0, -0.9999, 0); (-0.0627, 0.1067, 3.904, 1) | pifuguashi✔; fx_zishen✔; rotation✔; bag✔; hongwai✔; sound✔; muzzle_fire✔; muzzle_fire_02✘ | [utility\utility_1680\utility_1680.gim, effect\fx\weapon\skin\skin_1001_004\fx_skin_1001_004_zishen_01_sx.sfx, weapon\hongwai\hongwai01.gim] |
| 1110121 | 1105 / 70 B | (1, 0, 0, 0); (0, 1, 0, 0); (0, 0, 1, 0); (0, 0.0127, 0.447, 1) | bag✔; hongwai✔; sound✔; muzzle_fire✔; rotation✔; pifuguashi✔; fx01✘ | [weapon\hongwai\hongwai01.gim, utility\utility_1680\utility_1680.gim, effect\fx\weapon\skin\skin_1003_005\fx_skin_1003_005_idle_01_kj.sfx] |
| 1110137 | 1149 / 70 B | (1, 0, 0, 0); (0, 1, 0, 0); (0, 0, 1, 0); (0, 0.1792, -0.3703, 1) | bag✔; hongwai✔; sound✔; pifuguashi✔; rotation✔; muzzle_fire✔; muzzle_fire_02✔; fx01✘ | [weapon\hongwai\hongwai01.gim, utility\utility_1680\utility_1680.gim, effect\fx\weapon\skin\skin_1013_007\fx_skin_1013_007_zishen_01.sfx] |
| 1110145 | 1667 / 70 B | (-1, 0, 0.0028, 0); (0, 1, 0, 0); (-0.0028, 0, -1, 0); (-0.1381, 0.33, 5.627, 1) | pifuguashi✔; rotation✔; bag✔; sound✔; muzzle_fire✔; muzzle_fire_02✔; hongwai✔; fx01✘ | [utility\utility_1680\utility_1680.gim, weapon\hongwai\hongwai01.gim, effect\fx\weapon\skin\skin_1001_014\fx_skin_1001_014_zishen.sfx] |
| 1110152 | 914 / 70 B | (-1, 0, 0.0028, 0); (0, 1, 0, 0); (-0.0028, 0, -1, 0); (-0.506, 0.4902, 4.213, 1) | pifuguashi✔; fx_idle_01✔; bag✔; sound✔; rotation✔; muzzle_fire✔; muzzle_fire_02✘ | [utility\utility_1680\utility_1680.gim, effect\fx\weapon\skin\skin_1012_009\fx_skin_1012_009_idle_01.sfx] |
| 1110165 | 1230 / 70 B | (1, 0, 0, 0); (0, 1, 0, 0); (0, 0, 1, 0); (0, 0.1792, -0.3703, 1) | bag✔; sound✔; pifuguashi✔; rotation✔; muzzle_fire✔; muzzle_fire_02✔; hongwai✔; fx01✘ | [utility\utility_1680\utility_1680.gim, weapon\hongwai\hongwai01.gim, effect\fx\weapon\skin\skin_1006_011\fx_skin_1006_011_01_zishen_dsj.sfx] |
| 1110169 | 906 / 70 B | (-1, 0, -0.0053, 0); (0, 1, 0, 0); (0.0053, 0, -1, 0); (-0.16, 0.78, 7.7, 1) | pifuguashi✔; rotation✔; sound✔; hongwai✔; muzzle_fire✔; fx_idle_01✘ | [utility\utility_1680\utility_1680.gim, weapon\hongwai\hongwai01.gim, effect\fx\weapon\skin\skin_1002_009\fx_skin_1002_009_zishen_01_dsj.sfx] |
| 1110171 | 1023 / 70 B | (0.85, 0, 0, 0); (0, 0.85, 0, 0); (0, 0, 0.85, 0); (0, 0, 0, 1) | fx_idle_01✔; rotation✔; bag✔; hongwai✔; sound✔; muzzle_fire✔; pifuguashi✘ | [effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_zs_02.sfx, weapon\hongwai\hongwai01.gim, utility\utility_1680\utility_1680.gim] |
| 1110177 | 996 / 70 B | (1, 0, 0, 0); (0, 1, 0, 0); (0, 0, 1, 0); (0, -0.25, 5.205, 1) | rotation✔; muzzle_fire✔; muzzle_fire_02✔; pifuguashi✔; fx01✘ | [utility\utility_1740\utility_1740.gim, effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_idle_02.sfx] |
| 11101451 | 1667 / 70 B | (-1, 0, 0.0028, 0); (0, 1, 0, 0); (-0.0028, 0, -1, 0); (-0.1381, 0.33, 5.627, 1) | pifuguashi✔; rotation✔; bag✔; sound✔; muzzle_fire✔; muzzle_fire_02✔; hongwai✔; fx01✘ | [utility\utility_1680\utility_1680.gim, weapon\hongwai\hongwai01.gim, effect\fx\weapon\skin\skin_1001_014\fx_skin_1001_014_zishen.sfx] |
| 11101691 | 906 / 70 B | (-1, 0, -0.0053, 0); (0, 1, 0, 0); (0.0053, 0, -1, 0); (-0.16, 0.78, 7.7, 1) | pifuguashi✔; rotation✔; sound✔; hongwai✔; muzzle_fire✔; fx_idle_01✘ | [utility\utility_1680\utility_1680.gim, weapon\hongwai\hongwai01.gim, effect\fx\weapon\skin\skin_1002_009\fx_skin_1002_009_zishen_01_dsj.sfx] |
| 11101771 | 996 / 70 B | (1, 0, 0, 0); (0, 1, 0, 0); (0, 0, 1, 0); (0, -0.25, 5.205, 1) | rotation✔; muzzle_fire✔; muzzle_fire_02✔; pifuguashi✔; fx01✘ | [utility\utility_1740\utility_1740.gim, effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_idle_02.sfx] |

## 角色侧骨架线索（B-3 判定）

候选容器（本次统计可表寻址行数）：

| 容器 | 条目行数 |
|---|---|
| `character_01.gpk` | 47390 |
| `character_02.gpk` | 22914 |
| `character_03.gpk` | 21246 |
| `character_04.gpk` | 58704 |
| `character_05.gpk` | 77827 |
| `character_06.gpk` | 21160 |
| `character_07.gpk` | 39991 |
| `character_08.gpk` | 41655 |
| `character_09.gpk` | 22902 |
| `effect_01.gpk` | 212152 |
| `effect_02.gpk` | 3049 |
| `effect_cache.gpk` | 99801 |
| `model_01.gpk` | 22611 |
| `model_02.gpk` | 17488 |
| `model_03.gpk` | 18895 |
| `model_04.gpk` | 9890 |
| `model_05.gpk` | 17737 |
| `model_06.gpk` | 15275 |
| `model_07.gpk` | 11281 |
| `model_08.gpk` | 11932 |
| `model_09.gpk` | 17582 |
| `model_10.gpk` | 16396 |
| `model_11.gpk` | 7966 |
| `model_high_2024_01.gpk` | 10012 |
| `model_high_2024_02.gpk` | 1058 |
| `model_high_2024_03.gpk` | 16127 |
| `model_high_2024_04.gpk` | 22142 |
| `model_high_2024_05.gpk` | 12046 |
| `model_high_2024_06.gpk` | 3449 |
| `utility.gpk` | 21426 |
| `utility_scene.gpk` | 8097 |

结论：13/13 无骨架 id 的 `.gim` 仅用 **MatrixToBone + Socket_***（无 CutBones、无骨名）把网格挂到角色/插槽，武器包内不存在这些模型的骨骼；**下一步应到 `res\character_01..09.gpk` 找角色骨架**。角色骨架的**路径命名约定未定证**，故本轮未对这些容器做路径探针；`Documents\gres` 下 35 个容器头格式未解（非 HPGF/FPGH）⇒ 存在未覆盖面（unresolved）。


## unresolved（本轮未定证，未猜）

1. 逐骨 92 B 块**字段语义**未定证（已证：不是 4×4/3×3 矩阵行结构；只给偏移/长度/原始字节）。
2. `MatrixToBone` 记录的**归属对象**（模型根/容器/子网格/插槽）未定证；插槽级按"插槽段精确包含"判定，主矩阵按"唯一非插槽记录"标注为候选。
3. 16 float 的**行/列主序**未定证（两个仿射判据都给出）。
4. 绑定对象（.sfx/.gim/utility 路径）与插槽的从属关系按记录顺序推断，未定证（假设 A：属最后一个插槽；假设 B：属 Sockets 容器）。
5. `parent<self` 违规：1110032(41 条); 1110160(1 条); 1110161(1 条)（违规条数见各 id 的 `self_check`/`per_bone`）；该父索引可能是全局骨号或子集编号，未定证。
6. 角色骨架路径约定 + 35 个 gres 容器格式（见上）。
7. 传世 L6 的**中文名**在名单表里为空（未取到，未编造）。

## 命令清单

```
python locate_skeleton.py --all --out 03拆包产物\_gim_out\skel
python %TEMP%\sk2_assets.py ABC          # A 骨架资产 + B 挂点 + C 索引
python %TEMP%\sk2_mount2.py              # B 改进：插槽段精确归属
python %TEMP%\sk2_finalize.py            # C 合并索引/MD/覆盖率
python locate_skeleton.py --id 1110115 --layout-out <path> --dump-mesh <path>   # 布局接口
```