# RUNBOOK · 热更重建（LifeAfter Wiki）

> **本文件是 agent 唯一作业入口。** 新 agent 无需任何聊天记录，只读本文件 + `rules/` 即可完成全流程。
> 开工顺序固定：**本文件 → 最新交接卡（`state/handoff_*.md`）→ `rules/` → 现役脚本目录 `web/tools/`**。
> 凡与本文件冲突的记忆/旧脚本，**以本文件与 `rules/` 为准**；发现冲突就地修正本文件并写交接卡。

---

## 0. 环境与前置

| 项 | 值 |
|---|---|
| Python | `00_规范与工具/环境/venv/Scripts/python.exe`（含 yaml / cryptography / zstandard） |
| 项目根 | `E:/la拆包项目`（脚本内一律用 `__file__` 反推根目录，禁写死绝对路径） |
| 数据源铁律 | **只用 PE 还原树**（`41_还原树/pe/配置` + `30_分析` 冻结产物），不扫线上客户端 npk |
| 产物铁律 | `web/data/boards/*.json` 是**纯生成物，禁止手改**；一切修改走 `rules/` 或脚本 |

热更周期常见目录约定：`01_索引与产物/xx_快照<YYYYMMDD>/`（拆包落地）、`30_分析/`（分析产物）。

---

## 1. 重建主流程（八步）

```
① 拆包产物落点确认      → 01_索引与产物/xx_快照<日期>/
② 更新原始层引用        → 确认分析脚本读的是本次快照，不是旧快照
③ 生成规则层清单        → python 02_wiki/web/tools/build/gen_rules_inventory.py
④ 逐板重建（按板）      → 读 rules/boards/<board>.yml 的 primary/postprocess 顺序执行
⑤ 门禁体检              → python 02_wiki/web/tools/checks/gate_report.py   （先看红板，再跑门禁）
⑥ 发布门禁              → python 02_wiki/web/tools/build_wiki.py     （exit 0 才继续）
⑦ 条目级 diff + 更新日志草稿 → 对比上一快照，区分「数据变更」与「口径变更」
⑧ 前端抽查              → 3 个板冒烟：可渲染、无 JS 报错、图标不空
⑨ 写交接卡 + 发布       → state/handoff_<日期>.md，然后切 current
```

### ④ 逐板重建怎么做

`rules/boards/<board>.yml` 给出该板的三件事：
- `primary_builders`：主产出脚本（先跑）
- `postprocess_scripts`：后处理脚本（**顺序敏感**，脚本名含 v2/v3 的通常是迭代版，用新的）
- `rebuild_risk`：`high` = ≥10 脚本经手，改动前必须先备份该板 json

> ⚠️ 现存事实：`fashion_wardrobe` 有 73 个脚本经手（后处理 69）、`lottery_periods` 43 个、
> `weapon_skin_sfx_text_sources` 27 个、`avatar_catalog` 14 个、`item_master_full` / `mutation_core_full` 各 13 个、
> `scene_balance` 12 个 —— **这七块板是重建事故高发区**，热更后优先重跑并逐项比对条目数。

### ⑤ 发布门禁说明（易误解）

`build_wiki.py` **不是全量构建器**：它只校验既有 `data/boards/*.json`，通过后导出
`manifest.js` / `manifest.json` / 每板同名 `.js` / `build_meta.js`。退出码非 0 即禁止发布。

---

## 2. 质量闸门（DoD 硬条件）

| # | 闸门 | 判据 | 不通过怎么办 |
|---|---|---|---|
| G1 | 板完整性 | `build_wiki.py` exit 0，manifest 板数与预期一致 | 看报错逐条修，禁止手改 manifest |
| G2 | 条目数环比 | 各板条目数波动 ≤ ±20% | 查第 3 节红灯表，**禁止**为了"对得上"而回填假数 |
| G3 | 溯源完整 | 每条数据带 source_path + row_key，源真实存在 | 无溯源数据拒收，回原脚本补 |
| G4 | 不变量 | 概率池和=1；hp 曲线 150 级完整；navi_speed ≤ 250；分服子卡不混排 | 定位脚本，修源不修产物 |
| G5 | 资源完整 | 图标/海报文件存在性校验，缺失出清单 | 补资源或标记缺图（虚线占位），不猜图 |
| G6 | 口径一致 | 新产物与规则层一致（服名官方口径、排除范围、trial 合并） | 改 `rules/`，不手改产物 |
| G7 | 前端冒烟 | 抽查 3 板：渲染正常、无 JS 报错 | 修完再发 |

体检工具：`python 02_wiki/web/tools/checks/gate_report.py`
输出「每板契约错数 + 条目数环比 + 错误种类 Top」，写入 `state/gate_report.json`，退出码 0 全绿 / 1 有红板。
**重建后先跑体检（能提前看到环比异常），再跑发布门禁（决定能不能发）。**

---

## 2.5 已知红灯（截至 2026-10-30：**已全部修绿**）

此前有 5 块板契约不合格（`build_wiki.py` exit 1），已用 `tools/build/fix_provenance_contract.py`
按 `rules/provenance_fixes.yml` 修掉：talent_catalog 10,608 → equipment_attrs 6,596 →
drone_catalog 2,142 → gene_potential_catalog 504 → fashion_wardrobe 195，**现在契约错 0、门禁 exit 0**。
逐条根因与修复方式见 `rules/known_issues.yml`（KI-001 ~ KI-005）。

**下个热更周期若再出现红灯，按这个顺序查**：

| 现象 | 根因 | 处置 |
|---|---|---|
| 条目 source_id 与板级 lock 对不上 | 板级 meta 改了 lock，条目层没同步（历史上被临时手改出假 lock） | `fix_provenance_contract.py --board <id>`（规则驱动，先 dry-run） |
| 条目缺 upstream.file_id / entry_index | 冻结 JSON 提取缺 npk 定位层 | 按服别补**表级** file_id + entry_index（表定位取自 `30_分析/tI扫描_20260927/ti_paths_all.jsonl`） |
| 条目整块缺 provenance | 后处理/差分脚本写入时没盖戳 | 定位写入脚本（见 `rules/boards/<board>.yml` 的 postprocess_scripts）并补戳 |
| 名册级条目被契约判不合格 | 静态导出/字符串池条目本就没有行级溯源 | 走**名册级通道**（见下） |

### 名册级通道（2026-10-30 用户决策）

有些条目来自「静态导出 / 字符串池名册」，只有名字和图标，**没有行级解码定位**。
这类条目不伪造 locator_chain，契约改为：条目写 `provenance.roster`
（`evidence` ∈ {`name-roster-only`,`static-export`} + `source_id` + `source_desc` + 原标签留档），
并强制 `status_tags` 含 `unverified`；页面以虚线琥珀标签「◇ 名册级」与行级条目区分。

> ⚠️ 名册级通道只放宽「公开资格」，不改变数据本身。
> 禁止给名册级条目硬造 locator_chain —— 那等于伪造可回放溯源。

---

## 3. 红灯对照表（历史踩坑，最常撞）

| 现象 | 根因 | 处置 |
|---|---|---|
| `all_equips` 条目数暴跌 | 热更数据进了 inc 分片（base/_inc/_del），库内留盘 npk 没有 | 检查增量载荷是否入库；**未入库就出说明性空卡，不猜数** |
| 载具行 attrs 全空 | 提取器只留 attrs，漏掉 193000~196999 段（371 字段） | 走 `03_执行/vehicle_deep_extract.py` 专用链 |
| 载具面板值与游戏内不符 | 误用 `all_equips` 的 ui_acc/ui_health/ui_speed | 面板四值一律读 `vehicle_ui_data`，氮气读 `all_equips.max_nitrogen` |
| 载具特技/改装数据串行 | `vehicle_modding_data` 用按序配平 | 指针基址=28；归属用 `ref_vehicle_id` 反查 |
| 条目名为空 / 英文 ID | 名称在热更池（还原树 chs 池），不在行里 | 查热更字符串池（当前 11,632 串） |
| 名称串位（古典绅士↔月舞风华） | 行↔块顺序配平 | 同上，改用指针/反查 |
| 概率池对不上 | 渠道合并/overlay 顺序 | 用 `channel_merge_applied` / `merge_applied` 标记核对 |
| 板卡混排不同服 | 未按服别拆子卡 | 遵守 `rules/servers.yml`：分服子卡分开 |

---

## 4. diff 与更新日志

- diff 输入：本周期产物 vs 上一快照（快照保留最近 3 版，位于 `02_wiki/snapshots/<日期>/`）。
- 输出：`web/data/diffs/<日期>.json`，至少含：新增 / 删除 / 字段变更（板、条目 id、字段、前后值）。
- **必须区分两类变更**：
  - `data_change`：游戏源数据变了（写进更新日志正文）
  - `rule_change`：`rules/` 改了导致产物变化（写进更新日志的「口径变更」小节，并提示读者复核）
- 更新日志草稿由此生成，人工/agent 只做润色，不从零回忆。

---

## 5. 发布与回滚

- 构建先出到 `02_wiki/snapshots/<日期>/`，审完 diff 再切 `current` 指针发布；线上始终可用。
- 回滚 = 指针回切上一版（保留最近 3 版）。发现事故先回滚，再排查。

---

## 6. 交接卡（每次任务必写）

`state/handoff_<YYYYMMDD>.md`，内容：
1. 本次做了什么（拆包快照 / 重建了哪些板 / 改了哪些 rules）
2. `rules/` 变更清单（哪条规则、为什么改、影响哪些板）
3. 遗留问题与已知缺口（如护臂、进化武器等待增量载荷）
4. 下次开工注意事项（哪块板顺序敏感、哪个脚本别用旧版）

---

## 7. 边界（不要做的事）

- ❌ 不要手改 `web/data/boards/*.json`、`manifest.js`、`build_meta.js` —— 都是产物。
- ❌ 不要跑 `web/tools/_archive/` 下任何脚本。
- ❌ 不要为"凑条目数/对齐旧值"插值或猜数 —— 缺失就出说明性空卡。
- ❌ 不要用玩家俗称当服名（「共创服」只进 remark）。
- ❌ 不要把 `navi_speed` 与 `proto.top_speed` 混排或换算 km/h。
- ❌ 不要在未跑通闸门前发布。

---

## 8. 快速命令

```bash
PY="00_规范与工具/环境/venv/Scripts/python.exe"   # 项目根下执行

# 重建规则层清单（改了脚本或规则后跑）
$PY 02_wiki/web/tools/build/gen_rules_inventory.py

# 门禁体检（红板 + 条目数环比 + 错误种类）
$PY 02_wiki/web/tools/checks/gate_report.py

# 溯源契约修复（先 dry-run 看错误数变化，确认后再 --apply）
$PY 02_wiki/web/tools/build/fix_provenance_contract.py --all
$PY 02_wiki/web/tools/build/fix_provenance_contract.py --all --apply

# 发布门禁（重建完必须 exit 0）
$PY 02_wiki/web/tools/build_wiki.py

# 本地预览
$PY 02_wiki/web/tools/wiki_server.py    # http://127.0.0.1:8765/wiki.html
```
