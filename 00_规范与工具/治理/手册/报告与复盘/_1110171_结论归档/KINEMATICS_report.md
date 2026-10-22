# KINEMATICS_report

> task-89 · 写作用域：`weapon_skin_sfx_adapter.js` + 本报告。**阶段一（只读取证）** —— 实现/测量见 §3、§4（未做）。

## 1. 现状：适配器里写死的运动学（逐行原文）

| 行号 | 原文 | 问题 |
|---|---|---|
| **L723** | `var ang = p.r2 * Math.PI * 2, rad = sys.emitR * p.r3;` | 发射方向 = **均匀随机角**（无源 `PlaneDir`/`EmissionDirDegree`/`EmissionType`） · 半径只有 `EmissionRadius` 一项 |
| **L724** | `var drift = sys.vel * p.age * 20;` | **写死的量纲系数 `20`** ✗（无源依据） |
| **L725-727** | `… Math.cos(ang)*rad + Math.cos(ang)*drift,` / `sys.basePos[1] + (p.r4-0.5)*sys.emitR*0.6 + (p.r4-0.5)*drift,` / `… Math.sin(ang)*rad + Math.sin(ang)*drift)` | 径向漂移 + **另一个写死系数 `0.6`** ✗（竖直随机）；**无 `Gravity`/`AccelForward`/速度区间/噪声/自转/按距离发射** |
| L632-634（已有源口径的部分） | `emitRdecl = first(flat(n.emit && n.emit.EmissionRadiusFrame))` · `emitR = … U(emitRdecl)` · `emitR_source` | **`EmissionRadius` 已是源值 + `U()` 单位换算** ✓（说明"源驱动 + `U()`"的既有范式可复用） |

## 2. 源 `.sfx` 的运动学字段：**都存在**（两文件计数）

| 字段 | hit.sfx | jisha.sfx | 备注 |
|---|---|---|---|
| `PlaneDir` | 7 | 9 | 发射平面方向 ✓ |
| `EmissionDirDegree` | 21 | 27 | **帧动画**（FloatKeyFrame）✓ |
| `EmissionType` | 7 | 9 | 发射类型 ✓ |
| `DirType` | 18 | 36 | 方向类型 ✓ |
| `EmissionRadius` | 42 | 54 | **已接** ✓（L632-634） |
| `MinSpriteVelocity` | 21 | 27 | 速度下限 ✓ |
| `MaxSpriteVelocity` | 21 | 27 | 速度上限 ✓ |
| `Gravity` | 21 | 27 | **帧动画** ✓ |
| `AccelForward` | 7 | 9 | 前向加速度 ✓ |
| `NoiseStrength` | 21 | 27 | **帧** ✓ |
| `NoiseFrequency` | 7 | 9 | ✓ |
| `NoiseOctaves` | 7 | 9 | ✓ |
| `XDirDisturb` | 21 | 27 | 扰动 ✓ |
| `RandomSum` | 14 | 18 | 随机和 ✓ |
| `ParticlesPerUnitDistance` | 7 | 9 | **按距离发射** ✓（挥砍关键） |
| `CollisionPlane` | 14 | 18 | 碰撞面 ✓ |
| `RebondAttenuation` | 7 | 9 | 反弹衰减 ✓ |
| `Friction` | 14 | 18 | ✓ |
| `RotDegreeSpeed` | 35 | 45 | **自转** ✓（出现最多） |
| `RandomOrigRotate` | 7 | 9 | 初始随机旋转 ✓ |
| `SpinAxis` | — | 1 | 仅 jisha ✓ |
| `InitRotation` | — | 1 | 仅 jisha ✓ |
| `MinScale/MaxScale` | — | 1 | 仅 jisha ✓ |

## 3. 实现计划（阶段二，**未做**）—— 逐项独立开关（严格源式默认 ON / 有猜测默认 OFF）

| 开关（拟） | 替换/新增 | 源依据 | 默认 | 说明 |
|---|---|---|---|---|
| `kinDir` | 替换 `L723` 的 `ang=r2*2π` | `PlaneDir` + `EmissionDirDegree`(帧) + `EmissionType` + `DirType` | **ON**（严格源式） | 方向由源平面角/帧插值给出；随机分量仅保留源声明的随机源 |
| `kinVel` | **删掉 `L724` 的 `*20`** | `Min/MaxSpriteVelocity` + `Gravity`(帧) + `AccelForward` | **ON** | 位移 = `v0*t + ½(g+a)t²`，全部经既有 `U()` 换算；**不给任何新系数** |
| `kinEmitDistance` | 新增按位移发射 | `ParticlesPerUnitDistance` >0 | **ON** | 用**武器/节点世界位移距离**累计触发；=0 ⇒ 保持按时间发射（源语义） |
| `kinSpin` | 精灵自转 | `RotDegreeSpeed` + `InitRotation` + `RandomOrigRotate` | **ON** | 精灵可旋转（`sprite.material.rotation`） |
| `kinNoise` | 扰动 | `NoiseStrength/Frequency/Octaves` | **OFF（有猜测成分）** | 源噪声参数可读，但**噪声函数形式未定证** ⇒ 不许用正弦冒充 ✗；先登记 `unimplemented`/OFF 并写原因 |
| `kinCollision` | 碰撞/反弹 | `CollisionPlane`/`RebondAttenuation`/`Friction` | **OFF（有猜测成分）** | 需要地面/武器碰撞面语义，源侧未定证 ⇒ OFF |

## 4. 待做（阶段二/三）与验收对照

- 阶段二：adapter 逐项开关实现（**唯一写者**）+ `copy2` 备份 + `node --check`；**默认态（全开关 OFF）必须与开工前逐字节一致**（负控）
- 阶段三：同载入 A/B 逐项开关 —— `alive/可见数`、粒子世界位置包围盒/质心、`effect-only%`、截图 sha16 + **亲眼描述**；`applied==expected`（1110177=3 / 1110171=7）、`failed/missing` 空、`__errs=[]`
- 禁区遵守：**不改**曝光/灯光/bloom/ACES；**不为好看加系数**；写死的 `*20` 与 `0.6` 都要删掉并给替换依据 ✓
- **未证**（必须如实说）：删掉 `*20` 后的**单位一致性**要用 `U()` 逐项验证；`NoiseStrength` 的噪声实现形式未定证 ⇒ 该项只能 OFF/登记