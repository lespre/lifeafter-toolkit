# GRADEFILTER 验收报告：board.html 品级筛选「按钮 + 弹出面板勾选」版（task-35）

只读验收（未改 board.html / 任何默认文件）。证据仅写 `_target_1110171/GRADEFILTER_*`。
**本报告为「列表下拉 → 面板勾选」新形态**；此前按旧版（工具条平铺复选框）跑的那批结论已作废。

## 0. 刷新方式与 URL（排除缓存旧文件）
- URL：`http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki`
- 刷新方式：`Page.navigate` → **`Page.reload(ignoreCache=True)`（Ctrl+F5 等价）**，另加 `Network.setCacheDisabled(true)`
- 证据：`performance.getEntriesByType('navigation')[0].type = "reload"` · `transferSize = 102 922`（>0 ⇒ 确为网络重新拉取，非缓存）
- 作用域 `<style>`（含 `!important`）已生效：`styleBlockHasImportant = true` ✓

## 1. 控件形态
- `#fGrade` = **DIV**（不再是 `<select>`；其内 `<select>` 计数 = **0**）
- `#fGradeBtn` = **BUTTON**，文案 `品级：全部▾`（`#fGradeLabel` + `▾`）
- `#fGradePanel`：`display=none`（初始）· `position=absolute` · `z-index=60` · `max-height=290px` · `overflow-y=auto`
- 面板内 6 行，每行 `<input type="checkbox">`：`2白送级（8）` / `3直售级（27）` / `4紫皮级（44）` / `5典藏级（19）` / `6传世级（15）` / `未配置（2）` ✓（**checkbox 不是 select** ✓）

## 2. ★ 面板几何（`getBoundingClientRect()` 实测，面板展开态）

| 项 | 实测值 | 期望 | 判定 |
|---|---|---|---|
| `#fGradePanel` rect | `x=969 · y=304.86 · width=**250** · height=186.5 · left=969 · right=**1219** · bottom=491.36` | width≈250（不是≈400） | ✅ |
| computed | `width:250px` · `max-width:320px` · `box-sizing:border-box` | — | ✅ |
| 行 `#fGradePanel>div` | 每行 `width=**236**` · `height=28.75`，6 行一致 | — | ✅ |
| 第 1 行 checkbox | `x=**984** · width=14` | — | ✅ |
| 第 1 行文字 `span` | `x=**1006** · width=75.98` | — | ✅ |
| **ΔX（span.x − cb.x）** | **22.0 px（6 行全部 =22）** | ≈22（>150 即未修好） | ✅ |
| 视口 | `1578×902`；`fitsViewport=true` · `clippedByViewport=false` | 不裁掉 | ✅ |
| `elementFromPoint` | 面板中心 → 面板内 ✓；checkbox 处 → `INPUT` 面板内 ✓；文字处 → `SPAN` 面板内 ✓ | 不被遮挡 | ✅ |

**文字截断（每行 `span.scrollWidth` vs `clientWidth`）—— 全部未截断：**

| 行 | 全文 | clientWidth | scrollWidth | 截断 |
|---|---|---|---|---|
| 0 | `2白送级（8）` | 76 | 76 | False |
| 1 | `3直售级（27）` | 83 | 83 | False |
| 2 | `4紫皮级（44）` | 83 | 83 | False |
| 3 | `5典藏级（19）` | 83 | 83 | False |
| 4 | `6传世级（15）` | 83 | 83 | False |
| 5 | `未配置（2）` | 69 | 69 | False |

⇒ 用户报的「复选框贴最左、文字贴最右被截成 `2…`、面板撑到 ~400px」**已修复** ✓（截图 `GRADEFILTER_面板几何.png` 亲眼看：勾选框紧邻文字、计数完整、面板 250px）

## 3. 面板交互（真实鼠标事件 `Input.dispatchMouseEvent`）
| 检查 | 读数 | 判定 |
|---|---|---|
| 点按钮 → 面板打开 | `display=block`，rect 250×186.5 | ✅ |
| **勾 1 项后面板仍开** | `display=block` · checked=`["2白送级"]` · 标签 `品级：2白送` · 卡数 **8** | ✅ |
| 连勾第 2 项（仍开） | `display=block` · `["2白送级","3直售级"]` · 标签 `品级：2白送、3直售` · 卡数 **35** | ✅ |
| 连勾第 3 项 | `display=block` · 3 项 · 标签 `品级：2白送、3直售 等3项` · 卡数 **79** | ✅ |
| **点面板外关闭** | `display=none`，勾选保留、标签不变、卡数仍 79 | ✅ |
| 全部取消 | 标签回 `品级：全部` · checked=[] · 卡数 **115** | ✅ |

## 4. 多选语义（每张卡 1 皮肤；"勾 N 个 ⇒ 显示 M 张卡"）
| 勾选 | 卡数 | 与 chip 计数一致 |
|---|---|---|
| 0 个（全部） | **115** | — |
| 2白送级 | 8 | ✓（8） |
| 3直售级 | 27 | ✓（27） |
| 4紫皮级 | 44 | ✓（44） |
| 5典藏级 | 19 | ✓（19） |
| 6传世级 | 15 | ✓（15） |
| 未配置 | 2 | ✓（2） |

- **两两组合 15/15 全部通过**：`n_ok`（= 两者之和）与 `set_ok`（= 两者单独卡集合的**并集，逐条一致**）均 True（例：2白送+3直售 = 35 = 8+27 ✓；2白送+4紫皮 = 52 ✓；2白送+6传世 = 23 ✓ …）
- **三连**：2白送+3直售+4紫皮 = **79 = 8+27+44** ✓ 且集合 = 三者并集 ✓
- **全部取消** ⇒ 115（= N_all）✓，集合与 N_all 逐条一致 ✓

## 5. JS 错误
- `window.onerror` 记录 = **`[]`** ✓；`Runtime.exceptionThrown` = **0 条**（无 SyntaxError）✓
- console `log.error` 仅 2 类，均非页面脚本错误：
  1. `GET /favicon.ico` → 404（无 favicon，环境性）
  2. `GET /assets/audio/weapon_skin/jg/jg_attack_jinghe_01.wav` → **ERR_CONNECTION_REFUSED**（本地服务对该请求拒连；**建议 Lead 留意**：这是 SFX 音频资源）

## 6. 与其它筛选组合（各 1 次，真实点击勾选）
| 组合 | 0 勾 | 单个 A | 单个 B | A+B | sum_ok | set_ok |
|---|---|---|---|---|---|---|
| 武器种类 → `电磁机枪` | 5 | 0 | 2 | 2 | ✓ | ✓ |
| 上架状态 → `behavior_only` | 2 | 0 | 0 | 0 | ✓ | ✓ |
| 名称状态 → `unresolved` | 2 | 0 | 0 | 0 | ✓ | ✓ |
| 排序 → `id` | 115 | 8 | 27 | 35 | ✓ | ✓ |
⇒ **互不干扰**，且各组合下多选 OR 语义保持一致 ✓（标签始终正确反映勾选集）

## 7. 截图（均亲眼看）
| 文件 | sha16 | 大小 | 内容 |
|---|---|---|---|
| `GRADEFILTER_面板展开.png` | `b1fba94d37f2583b` | 485 741 B | 面板展开、0 勾（3 张图之一） |
| `GRADEFILTER_勾2项.png` | `a130f55686658f5b` | 398 032 B | 勾 2 项、标签「品级：2白送、3直售」、计数「显示 35 / 115 款皮肤」 |
| `GRADEFILTER_0勾选.png` | `2612dd88ce12460f` | 481 377 B | 0 勾、标签「品级：全部」 |
| `GRADEFILTER_面板几何.png` | `b7cf1a8a6795369b` | 14 600 B | 面板特写（勾选框紧邻文字、计数完整、250px 宽） |
三张全屏图 sha 各不相同 ✓；取帧均走**稳定门**（连续帧 sha 相同，`tries=2`）✓

## 8. 浏览器运维（硬要求）
- **只起 1 个 Chrome**（headless=new，独立临时 profile，`--remote-debugging-port=1001x`）
- 结束 **`taskkill /T /F /PID <pid>` 杀整棵进程树** ✓
- 复查：`netstat -ano` 无该端口 LISTENING = **`[]`**；按 profile 匹配的残留 chrome.exe = **0**
- ⇒ **已关闭、无残留** ✓（四个脚本各自实测均为此结果）

> 说明：本任务全部用我既有的 headless Chrome + CDP 管线（一次性 profile + taskkill 整树），**未启用 Tabbit 浏览器**，以免在你的真实浏览器里留下标签/进程（你明确担心的残留问题）。

## 9. 命令清单
```
venv\Scripts\python.exe %TEMP%\GRADEFILTER2.py   # 新形态：控件/面板/遮挡/语义(15对+三连)/重置 + 3 张截图
venv\Scripts\python.exe %TEMP%\GRADEFILTER3.py   # 修正探针（行 rect 须在面板展开态读）：面板交互 3 项复测
venv\Scripts\python.exe %TEMP%\GEOM.py           # 几何量测（硬刷新后）：面板/行/checkbox/span x + 截断 + 遮挡
venv\Scripts\python.exe %TEMP%\COMBO.py          # 与武器种类/上架状态/名称状态/排序 各组合 1 次
```
（`%TEMP%\GRADEFILTER.py` 为**旧平铺复选框形态**，其结论已作废，仅留档。）

## 10. 一处如实登记的自我更正
第一次跑交互三项时，我在**面板还是 `display:none`** 时读行坐标 ⇒ 点击落在页面左上角（等于"点面板外"）⇒ 误报"勾 1 项后面板关闭"。修正为**在面板展开态读行 rect** 后复测，三项全部通过（见 §3）。**不是页面缺陷**。
