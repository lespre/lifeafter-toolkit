# 无人机总表 · 建板报告

- 板块 id：`drone_catalog`（`02_wiki/web/data/boards/drone_catalog.json` / `.js`）
- 生成脚本：`01_索引与产物/30_分析/无人机总表/build_drone_catalog.py`（宽松解码器 `lenient_rows.py`、服型对比 `server_diff.py`）
- 源包：`E:/mrzh/Documents/script.py314.lc.npk`
  - sha256 `c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523`
  - 195,840,216 B，mtime_ns 1792168962775981000（2026-10-17 快照）
- 服型：简单生存服（kj1，`com/cdata/oversea/*_auto_oversea_data_kj1*`）
- 证据等级：`structure` / `structure-only`（静态度量，非实机可得性证明）
- 校验：`publication_contract_errors(strict_v2=True)` → **0 错**；`python tools/build_wiki.py` → **exit 0**

## 1. 总条数

| 项 | 数 | 说明 |
|---|---|---|
| all_equips kj1 索引行 | 1552 | 严格解码成功 1218，未绑定 334 |
| 带 `drone_type_name` 的机体行 | **56** | 无人机机体全集（含 7 条体验版） |
| 入板卡片 | **49** | 剔除 7 条「体验版」重复行（见 `meta.excluded_variants`） |
| 类型（kind） | 16 | 基础/医疗/战斗/战虎/负重/自爆/采集/战辅/盾补/镭蛇/狡兔/灵龙/猎犬/火凤/奔马/晶蝶 |
| 品级 | 基础 15 / 进阶 14 / 高阶 15 / 典藏 5 | 取 `drone_quality_level` 0–3 |
| 战力列 base_score | 100–150 | 表内评分基数，**未证明**等于实机面板战力 |

每张卡：`name / kind / grade / power / desc / icon / skills / talents / obtain(未证明→null) / function_tips / model / monster_id / module_id / released_cbg / provenance`。

## 2. 有图 / 未下发

| 项 | 有图 | 未下发 |
|---|---|---|
| 机体图标（`icon` 字段） | **49 / 49** | 0 |
| 类型徽标（`drone_type_icon`） | 41 / 49 | 8（去重后 3 个类型：基础 `icon_type_jichu`、负重 `icon_type_fuzhong`、战辅 `icon_type_zhanfu`） |
| 导出 PNG 总数 | 91 | → `02_wiki/web/assets/drone_icons/` |

- PE 命中 83 张（`_b` 300×150 / `_s` 154×78，来自 `pe_index.sqlite3` + `pe_packs`）。
- PE 未命中 11 个路径，PC 兜底补 8 张（`_max` 600×300 / `_omg_*` 变体，`pc_fid_calib/hit_table.csv` + `pc_export.export_path`）。
- 剩余 3 个类型徽标在 PE 与 PC 两侧包里都不存在，卡片记 `kind_icon_state="未下发"`，**未用占位图冒充**。
- 抽样目视核对：`icon_180022_max.png`=红色战斗无人机（FIRE 涂装）、`icon_180031_max.png`=黑色负重无人机，解码正确。

## 3. 解码失败表（如实记录，未补齐）

| 表 | 现象 | 处理 |
|---|---|---|
| `all_equips_data_oversea_kj1` | 334 行 `inline list variant`（机体行末尾挂未声明内联数组，严格解码整行判废）；其中 180xxx 段 44 行、含 **11 台无人机机体** | 新增 `lenient_rows.decode_rows_lenient`：同 schema/bitmap 语义，余量记 `leftover` 不判废。对严格解码成功的 1218 行做过全字段 diff → **0 处不同**，救回 11 台机体 |
| `drone_conf_data_kj1` | 表体仅 33 B，只有 `auto_release_max_wait_time` 一个标量字段 | 该表在本服**不含机体名册**；名册改从 all_equips 机体行取 |
| `drone_base_conf_kj1` | 289 B，索引尾 `56 05 05 b7` 不在支持列表 → 0 行 | 未解，卡片不引用 |
| `drone_power_conf_kj1` | 55 B，索引尾 `56 05 02 14`（76 05 02 变体）→ 0 行 | **战力公式表未解**；战力列因此用 all_equips.base_score |
| `drone_item_2_drone_level_kj1` | count=0，空表；CHS 池也解不出 | 无「道具→等级」链 |
| `drone_talent_v3_level_data_kj1` | 表体解不出 + CHS 池位解析失败 | 层级曲线未解，天赋只出 `drone_talent_v2` |
| `drone_monster_skill_data_*` | 全部服务器均 572 B 壳、无 `x{` 表体、无 CHS 文件 | 无人机怪物技能名不可得 |
| `skill_data` 查名 | `normal_attack_skill_id=5209`、模块技能 5116/5103/5204/5203 在 skill_data 无行 | 名称置 `null` + `name_status="未解出"`，只保留 id，**不猜名** |

技能/天赋的可得性边界：

- `drone_skill_mapping_data` 仅 3 行（光盾/电弧/灵龙 无人机）；只有**灵龙**在机体名册里有载体（守御灵龙/青龙/赤龙），技能名解出 `净化之祝1`（id 270406–270409）。
- 其余机体只有 `normal_attack_skill_id` + `sub_mesh_skill_ids`（13 行机体有后者），名称无源。
- `drone_talent_v2` 的 7 条科技线（血量增强/百战成钢/屹立不倒/超强火力/进化武器/清除感染/精准打击）是**账号级**无人机科技，非单机专属；卡片 `talents[].scope="global"`、`talent_scope` 已注明。
- `obtain` 一律 `null`：静态表无获取途径文本列；`released_cbg` 只表示藏宝阁交易白名单。

## 4. 服型差异（各服 all_equips 机体行对比）

| 服型 | 状态 | 机体行 |
|---|---|---|
| kj1（简单生存服） | ok，1552 索引行 | 56（本板基准） |
| kjxq | ok，1552 索引行 | 56，与 kj1 **完全一致**（无独有/无缺失） |
| yk | ok，2227 索引行 | **0**（该服 all_equips 无 `drone_type_name` 机体行） |
| kjjp / kjna / kjsea / kjhmt | 壳模块 310–311 B，无 `x{` 表体 | 0（该服未下发无人机表，非解析失败） |

明细落盘：`01_索引与产物/30_分析/无人机总表/server_diff.json`。

## 5. 发布状态

- 本板 **未写入** `publication_policy.json` / `wiki_taxonomy` / `manifest`（按分工由主线程登记）。
- 因此 `build_wiki.py` 不校验真值契约也不把它列进 manifest；已用 `publication_contract_errors(..., strict_v2=True)` 单独验证为 **0 错**（contract_version=3 / frozen-audited-artifact / 单源 lock / 每条 decoded-table-row 定位链，未伪造 entry_index/file_id）。
- 主线程登记时建议：`publication_status` 按 `structure` 定级，`items: 49`，category `二、战力类 / （六）无人机`。
