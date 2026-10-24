# 全量道具总表 item_master_full · 构建报告

生成：2026-10-23 ｜ 板块：全量道具总表 · 经典服 / 简单生存 / 会员专享 ｜ 条目：**8300**

## 1. 各源解码行数

| 源表 | 服型 | 行数 | 用途 |
|---|---|---|---|
| `common_item_data_auto_oversea_data_kj1` | 简单生存 | 1372 | 入行（id_space=item，kind=名字/号段） |
| `common_item_data_auto_oversea_data_kjxq` | 简单生存 | 1376 | 入行（id_space=item，kind=名字/号段） |
| `common_item_data_auto_oversea_data_yk` | 会员专享 | 255 | 入行（id_space=item，kind=名字/号段） |
| `gift_data` | 经典服 | 5591 | 入行（id_space=gift，kind=礼盒） |
| `all_equips_data_auto_oversea_data_kj1` | 简单生存 | 1218 | 入行（id_space=equip，kind=装备） |
| `fashion_data` | 经典服 | 10801 | 补充表（仅用于 kind/名字），不产生行（键=key，与道具 id 空间无键可 join） |
| `vehicle_ui_data` | 经典服 | 205 | 补充表（仅用于 kind/名字），不产生行（键=key，与道具 id 空间无键可 join） |
| `body_sfx_data` | 经典服 | 43 | 补充表（仅用于 kind/名字），不产生行（键=buff_item_id，与道具 id 空间无键可 join） |
| `cook_recipe_data` | 经典服 | 571 | 补充表（仅用于 kind/名字），不产生行（键=key，与道具 id 空间无键可 join） |

原始合计 9812 行 → 合并后 **8300 条**。

## 2. kind 分布

| kind | 条数 | kind_group | 规则依据样例 |
|---|---|---|---|
| 礼盒 | 6132 | 礼盒 | source_table:gift_data 礼盒表×5591；name_suffix:自选箱×468；name_suffix:宝箱×25 |
| 装备 | 1218 | 装备 | source_table:all_equips_data 装备表×1218 |
| 道具 | 783 | 道具 | fallback:未匹配名字/号段规则×783 |
| 材料 | 64 | 材料 | name_suffix:材料×64 |
| 建筑 | 63 | 材料 | id_band:90000-99999 建筑构件号段×52；name_suffix:建筑构件×6；name_token:建筑构件×5 |
| 家具 | 32 | 道具 | name_suffix:家具×29；id_band:90060000-90199999 独享版家具号段×3 |
| 货币 | 4 | 货币 | name_token:钻石×2；name_token:金币×2 |
| 消耗品 | 3 | 消耗品 | name_token:血清×1；name_token:药剂×1；name_token:营养液×1 |
| 图纸 | 1 | 道具 | name_token:图纸/蓝图/残图×1 |

未命中规则的 fallback 783 条（9.4%），号段 top：200000×460, 100000×144, 300000×90, 0×53, 600000×10, 1300000×10, 1400000×6, 1200000×5。

## 3. 服型与去重

- 同 id 同名合并：142 条记录带 `servers[]`；同 id 异名 **0** 个 id 已拆成多行并带 `server_type`。
- 跨 id 空间同号（数值相同、实体不同）：0 个 —— ``。

### 服型冲突 id（同 id 异名）

| id_space | item_id | 名字 | 涉及服型 |
|---|---|---|---|

## 4. 图标

- 有图 **6210** / 8300（74.8%）｜ 无图 2090
- 导出通道：{'PE': 6210}（PE=安卓热更包 .ktx；PC=PC 端 .bc7 兜底）
- 状态：{'已导出': 6210, '未下发': 1440, '无图标字段': 650}
- 候选基名 7860 ｜ PE 命中并导出 2218 ｜ 未解出 5642

## 5. 未命名清单

**0 条**（六个源表都有 _chs 名字池，无空名）


## 6. 未下发清单（有 icon 字段但解不出）

按 kind 汇总，明细见 `_report_item_master_full_missing.csv`。

| kind | 未下发条数 | 样例 |
|---|---|---|
未下发 1440 条；另有 650 条源行无 icon 字段（走模板仍无命中）。

| 礼盒 | 995 | 男红粉救生包(130022)、男藏青小背包(130023)、普通技能书(130100)、高级技能书(130101)、端午食袋(130571) |
| 装备 | 278 | 中级机枪(10056)、喷火器(10086)、喷火器(10087)、基础机枪(10092)、中级机枪(10093) |
| 道具 | 152 | 精密透镜(9901)、残垣戈壁·抗灾勋章(128626)、单次开启抵扣券(152439)、单次购买五折券(152440)、文化宫剧目单(152477) |
| 建筑 | 11 | 莹雪椅子(93768)、寒梅屏风(95846)、迷你雷云(96007)、夕阳无限(98240)、星光慵懒沙发(98244) |
| 材料 | 3 | 毛线(9289)、黑麦种子(152483)、音浪前线初见粉(240085) |
| 家具 | 1 | 手工编织挂画(152505) |

## 7. 纪律与边界

- 名字只取 `<表>_chs.py` 池；缺失即 null，未编造、未跨表按相似度拼名。
- 未改 `publication_policy` / `wiki_taxonomy` / `manifest` / 其它板；`E:/mrzh` 只读。
- 该板尚未登记进 `data/publication_policy.json`（本轮按题不修改策略），故 build_wiki 会导出 `item_master_full.js` 但不列入 manifest 首页；登记后即可公开（契约校验见 §8）。

## 8. frozen-v3 契约校验

`publication_policy.publication_contract_errors(strict_v2=True)` → **0 项（通过）**

```
ok — 无错误项
```
