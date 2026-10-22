# ROTBUG：打开 SFX 后旋转乱转 —— 复现 / 定因 / 修复对照

对象：`E:\la拆包项目\08Lifeafter wiki\assets\weapon_skin_sfx_adapter.js`（sha256 前16 = `7E707707CEFF7CFC`，262 行）
日期：2026-09-18 · 端口 10041 全新 profile · 未改 `viewer.js` / `board.html` / manifest / 资产

## 复现命令
```
python %TEMP%\rotbug2.py before      # 修复前（已临时回退）
python %TEMP%\rotbug2.py after       # 修复后
```
脚本流程：headless Chrome(152) → `board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc`
→ `WikiWeaponViewer.open({skin_id:'1110171', …viewer.json})` → 点 `.wv-sfx` 开/关
→ **合成 PointerEvent**（CDP 鼠标驱动不了 `bindOrbitPointer`）在 canvas 上 pointerdown + 10×(pointermove dx=18px) + pointerup
→ 每步读 `WikiWeaponViewer.__state()` 的 `proj / projCenter / clipped / camPos`。

## 客观量对照（同一拖动动作）

| 指标 | 修复前 OFF | **修复前 ON** | 修复前 ON→OFF | 修复后 OFF | **修复后 ON** | 修复后 ON→OFF |
|---|---|---|---|---|---|---|
| 静止 24 帧 `projCenter` | 0.49246 | **0.77629（轴心跳 +0.284）** | 0.81376 | 0.49246 | **0.48027（无跳变）** | 0.48066 |
| 拖动起手投影盒宽（NDC） | 0.352 | **1.043（3.0×）** | 0.926 | 0.352 | **0.352** | 0.374 |
| `clipped` | false | **true** | **true** | false | **false** | false |
| 拖动 `projCenter` 净漂移 | (−0.0122, +0.0315) | (+0.0375, +0.0699) | (+0.0064, +0.0305) | (−0.0122, +0.0315) | **(+0.0004, −0.0008)** | (+0.0103, −0.0266) |
| 单步最大跳变 | 0.0045 | **0.0138（3.1×）** | 0.0147 | 0.0045 | **0.0017** | 0.0045 |
| `camPos` | 全程不变 | 全程不变 | 全程不变 | 全程不变 | 全程不变 | 全程不变 |

原始数据：`ROTBUG_result_before.json` / `ROTBUG_result_after.json`；
截图：`ROTBUG_{before,after}_{off,on,off2}_{before,after}.png`
（`off`=未挂特效、`on`=点开 SFX、`off2`=点开后再点关）

## 根因（机制 + 行号）
1. `weapon_skin_sfx_adapter.js` 原 `ctx.root.add(group)`（旧 L116）⇒ 特效层是**模型根的子节点**（本地空间）✓ 语义没错。
2. three r180 的 `Sprite` **自带 geometry**（4 顶点 quad：`three.core.min.js` 内 `class Sprite ... this.geometry = ma`），
   `Box3.expandByObject()` 会 `union( object.geometry.boundingBox × matrixWorld )` ⇒ **每个 SFX Sprite 都进入 `Box3.setFromObject(state.root)`**。
3. `viewer.js:455-461 modelFocus()` = `new Box3().setFromObject(state.root)` ⇒ 被特效污染（实测轴心 NDC x +0.284、盒宽 3.0×）。
4. `viewer.js:2118-2141 applyOrbit()`：`c0=focusOf()`（L2134）→ `root.quaternion.premultiply(绕世界Y)`（L2135）
   → `c1=focusOf()`（L2137）→ `root.position.add(c0-c1)`（L2138「绕中心转→中心不漂」）。
   轴心既然偏移，模型就绕一个**偏出自身约 1 个模型尺寸**的点旋转 + 每步平移补偿 ⇒ 视觉「乱转」。
5. 附带证据：`setEnabled(false)` 只置 `group.visible=false`，Sprite 仍在包围盒里 ⇒ **修复前把 SFX 关掉后仍然偏**
   （`idle_off2` pc=0.81376、clipped=true）；必须整层移除才会恢复（用户看到的「关闭后正常」应是重载后）。

## 修复（只改 sfx_adapter.js）
特效层改挂 **scene**：`group.matrixAutoUpdate=false; scene.add(group);`，
每帧 `syncToRoot()`：`root.updateMatrixWorld(true); group.matrix.copy(root.matrixWorld); group.matrixWorldNeedsUpdate=true;`
（`tick()` 开头调用，挂点仍是**模型本地空间**，因为乘的正是 `root.matrixWorld`；`dispose()` 的 `group.parent.remove(group)` 兼容）。
`viewer.js` 未改动 ⇒ 若后续要让特效参与包围盒，应改 viewer 侧（例如 `Box3` 遍历时跳过 `userData.excludeFromBounds`）。

## 像素级复核（PIL，阈值 |Δ|>8）
| 对比 | 差异像素 | 说明 |
|---|---|---|
| `before_off_before` ↔ `after_off_before` | **0** | 对照：无特效路径逐像素一致 |
| `before_on_before` ↔ `after_on_before` | **0** | **修复对「开特效静止帧」完全透明**（特效挂点/画面未变） |
| `before_on_after` ↔ `after_on_after` | 46,997（4.66%），bbox x[517,888] y[259,585] | 同一次拖动后姿态不同 —— 轴心修正的直接结果（差异集中在模型区，非全屏） |

## 结论
- 复现成立：同一拖动下轴心跳变 +0.284 NDC、盒宽 3.0×、单步跳变 3.1×、clipped=false→true。
- 修后 SFX 开与关的轴心/盒宽/漂移回到同一基线（`projW` 0.352、`clipped=false`、`maxstep` 0.0017–0.0045）。
- 特效视觉未变（`before_on_before` ↔ `after_on_before` 0 像素差）。
- 附带发现：修复前「点开 SFX 再关掉」仍偏（`idle_off2` pc=0.81376、clipped=true），因为 `setEnabled(false)` 不移除 Sprite；
  修复后该路径也回到基线（0.48066 / clipped=false）。

