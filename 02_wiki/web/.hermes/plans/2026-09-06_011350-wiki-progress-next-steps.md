# 08LifeAfter Wiki 现状盘点与下一步计划

> **执行纪律：** 本计划不是开工指令。任何影响 `data/boards/`、生成 `.js`、主页、policy、测试产物或 Git 的动作，都要在用户明确说“继续”后才执行。

**目标：** 保持已发布 14 板的可信边界，先收束数据源与铠甲再临的活动级证据，再决定是否重建或发布。

**权威记录：** `E:\la拆包项目\06（agent写）拆包器进展与交接日志.md`。最新 checkpoint 为 **27.60**；今后每个可复用结论、停损与发布状态必须先/同时同步到该日志。

---

## 1. 当前状态（2026-09-06 只读快照）

### 1.1 已发布：14 板

| 大类 | 已发布板 | 当前条目 | 状态 |
|---|---|---:|---|
| 一、道具总表 | `common_item_text_sources`、`gift_data_text_sources` | 35,986 + 5,443 | 行级文字/结构 provenance 已通过 |
| 二、时装类 | 时装总表、面饰/发饰、背包/挂件、荧光棒、投影、最佳动画/击败播报、武器皮肤 | 1,428 / 180 / 79 / 108 / 39 / 13 / 114 | 7 栏均已有已发布板 |
| 三、战力类 | 武器 schema、核芯卡、芯片名册 | 196 / 77 / 67 | 无人机栏尚无已发布板 |
| 四、奖池 | 铠甲再临静态面板、兑换商店静态结构 | 1 / 1,757 | 均为静态结构板，不等于在线活动完整事实 |

- `nucleus_cards` 已 retired；目录中其他旧 JSON（如 `fashion_kaijia`、`lottery_kaijiazailin`）未在 policy 标记为 published，不得混入“上线板”统计。
- 当前 Git HEAD：`6884803 docs: clarify unresolved all-equips name boundary`。
- 已提交稳定验证停留在日志 27.55/27.56：14 板、45,488 条、`unittest 31/31 OK`。**这不是对当前未提交铠甲工具/标题改动的验证结果。**

### 1.2 已发布板的明确边界

- `weapon_attrs_schema_static`：196 = 154 `name-slot` + 15 `desc-first-map` + 27 `unresolved`。27 条保持匿名，禁止按同 ID、模型、图标或串入文本补名。
- `nucleus_cards_classic`：77 张核芯卡已闭合品级、武器类型、特技和 5/9/12 星文本；中间星级数值仍无静态源，已搁置。
- `chip_item_catalog`：67 个静态名册条目；品级颜色、完整效果长文没有可靠 script 静态源，不能伪造。
- 奖池类的 `audit_status=passed` 只说明 provenance/发布契约合格，**不说明活动已启用、当前可得、主子池完整或概率完整。**

### 1.3 铠甲再临：已发布内容与真实未闭合项

当前已发布 `lottery_kaijia_panel_static`：

- 锁定 BA8 源 `ba8a239a…`；页面仍是 **1 张活动卡**。
- `391782` 只作为 `shared-reference-only` 的 `lottery_id`，不展开，已排除历史家具污染。
- 展开 `390704` 的 9 条旧链秘宝记录（均有旧链概率）与 `391783` 的 1 条福袋记录（概率未定位）。
- 面板展示 10 个 ID；`633080140` 只完成“飞影召唤器”名称证据，未认领为 `390704` 的 direct slot。
- 板数据内部 meta 名仍为“铠甲再临 · 静态面板配置”，但子页标题已由 `category` 尾段统一驱动；不存在单板标题硬编码。

未闭合：

1. 在线本期将 `391782` 唯一选择/分派到哪些 reward pool 的**活动级 selector**；
2. 主奖池、全部子奖池及逐项概率的同源链；
3. `火刑裁决`（公开前瞻名称）与静态叶子 `1110182 / 火刑电光炮` 的 ID/名称关系；
4. 飞影召唤器的 direct pool slot 与概率。

### 1.4 尚未发布的正式服中间工作

- `tools/extract_kaijia_formal_tables.py`：从 `E:\LifeAfter\Documents\script.py314.lc.npk`（SHA `79c0d06f…`）只读定向提取 8 表；未提交。
- `tools/trace_kaijia_formal_reward_chain.py`：输出 136 条 reward trace；未提交、未接入 builder。
- `tools/rebuild_kaijia_panel_static.py`：仅有一行未提交标题源改动；**仍默认使用 BA8 `documents-py314-current`，不能把它误称为正式服重建器。**
- 27.57 已记录正式服 `key=232` 的 `{4:391783}` 福袋映射、10 格展示数组、六礼盒 field-level 链和 selector 缺口；这些均不能直接升级成完整奖池页面。

---

## 2. 下一步顺序与停损线

### 阶段 A：先做双源 presence diff 与发布语义（最低成本，优先）

**目的：** 正式服与测试服均作为读取源；先按同目标分别锁源、输出 presence diff，再决定能否进入当前图鉴或零区。禁止把 BA8 静态板、经典服 trace 与在线状态混成同一事实链，也禁止跨源借字段补链。

**拟改文件（获准后）：**
- `tools/rebuild_kaijia_panel_static.py`
- `tests/test_rebuild_kaijia_panel_static.py`
- 必要时 `data/live_sources.json`（只使用既有注册源，不新增/修改包）
- `06（agent写）拆包器进展与交接日志.md`

**工作项：**
1. 给目标生成器加显式双源读取/参数选择：每源分别校验 registry 的 SHA、bytes，输出 `both` / `formal-only` / `test-only` / `conflict`，而非任一默认源覆盖另一源。
2. 写测试：两服 base/CHS/reward 不得静默混源；没有活动 selector 时正式服 trace 不能进入 `pools` 渲染；`test-only` 未完成历史排除不得进入零区。
3. 测试服独有候选只有完成《明日之后完整历史更新汇总_2018-2026.md》排除后，才可作为带源锁的“测试服独有预告”；正式服独有仅标 `formal-only`，不推断版本状态。

**完成门槛：** 两服 source lock 与 presence diff 在 meta、每条 provenance 和测试中一致；没有跨源字段拼接、没有重新定义业务池关系。

**停损线：** 仅为“让页面看起来更新”而改 JSON/JS、手改生成产物、跨源回填，或把 `test-only` 直接说成未上线，立即停止。

### 阶段 B：铠甲完整奖池证据链（高价值，但必须有 selector）

**目的：** 只在能证明活动上下文时，把正式服 trace 接入页面。

**前置条件（二选一）：**
1. 得到活动级 selector（客户端已解密配置、运行时可验证字段或服务器返回的非敏感活动配置）；或
2. 得到逐项概率、主/子池关系完整且可回溯的官方概率来源。

**允许的单次定向探针：** 先向用户说明“目标字段、预计范围、时间/额度、失败后立刻停止”，经明确同意后才执行。不得再用 Documents 混合缓存、媒体目录、公开前瞻或泛网络连接替代 selector。

**拟改文件（仅在前置条件满足后）：**
- `tools/trace_kaijia_formal_reward_chain.py`
- `tools/rebuild_kaijia_panel_static.py`
- `tests/test_rebuild_kaijia_panel_static.py`
- `tests/test_publication_gate.py`（若条数/发布结构变化）
- `data/boards/lottery_kaijia_panel_static.json`、生成 `.js`（只能由 rebuild/build 生成）
- `06（agent写）拆包器进展与交接日志.md`

**验收：**
- 每一个池成员都有 `活动 selector → pool_id/slot → reward jump → [item_id, quantity]`；
- 每个概率有同源字段与口径；
- 用户锚点逐项标为“已闭合 / 仅名称闭合 / 未闭合”，不能用名称相似补齐；
- `391782` 历史家具反证仍全数排除；
- 完整链未闭合则板保持受限静态状态，不升格为完整奖池。

### 阶段 C：其他板只按用户优先级推进

候选顺序建议：

1. **无人机栏**：先定位独立主表和名称/属性/品级证据，再建新板；无表不做“全量”。
2. **武器 27 条匿名**：仅等独立命名表或用户实机锚点，不再反复拿 all_equips 串位文本猜名。
3. **芯片效果/品级、中间星级数值**：目前属客户端/服务端展示层无静态源，继续搁置，除非用户给出明确新锚点或数据源。

---

## 3. 每轮强制交接与发布门禁

1. **开工前**：读 06 日志最新 checkpoint、`git status`、`data/live_sources.json`；明确源与本轮停损线。
2. **形成可复用结论时**：立即追加 06 日志，写清源 SHA、表/FID、已证明事项、禁止推论、未闭合项和是否已发布。
3. **重建前**：确认生成器只消费已闭合证据，JSON/JS 不手改。
4. **发布前**：`build_wiki.py` → 铠甲专项/相关单测 → `unittest discover` → Node 数据加载 → 本地预览 → 检查 manifest/policy/注入位。
5. **提交前**：06 日志已同步；`git status` 无意外生成物；提交信息只描述实际验证过的改变。
6. **停损**：一轮定向探针未获取预期 selector/字段，就写 06 日志并停，不扩扫。

---

## 4. 当前不执行项

- 不 rebuild、不跑会重写生成物的测试、不发布、不提交；
- 不重启 8765 服务；
- 不扩大扫正式服 Documents、混合媒体缓存、进程内存或网络；
- 不把在线活动状态、公开前瞻、面板展示 ID、礼盒配置和 reward-pool 行压成一条“完整奖池”结论。
