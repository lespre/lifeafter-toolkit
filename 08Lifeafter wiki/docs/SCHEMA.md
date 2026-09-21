# Lifeafter Wiki 数据规范（SCHEMA v0.3）

> **默认拒绝发布。** 只有同时通过发布策略与行级定位链契约的 board 才能进入公开 `manifest.js`。
>
> 本规范约束正式服（经典服）与测试服（简单生存服）两个当前 Documents 快照的**并行读取**；包内静态存在不等于当前活动、货架、奖励已启用或尚未上线。

## 1. 目录与职责

```text
08Lifeafter wiki/
├── wiki.html                         # 公开入口：只读 manifest.js
├── board.html                        # policy-gated board 页面
├── live_reader.html                  # localhost NPK 检查工具，不是图鉴类别
├── data/
│   ├── boards/                       # board JSON；可保留隔离旧档
│   ├── publication_policy.json       # board 的 published/quarantined 状态与原因
│   ├── publication_policy.js         # builder 生成，供静态页面读取
│   ├── manifest.js                   # builder 生成，仅含可公开 board
│   ├── live_sources.json             # 只读 NPK 服务的当前源锁
│   └── quarantine_legacy_html/       # 被隔离旧静态页的逐字节归档
├── docs/SCHEMA.md                    # 本规范
└── tools/
    ├── publication_policy.py         # 行级发布契约
    ├── build_wiki.py                 # policy + 契约门禁 builder
    ├── live_npk_reader.py            # 单条按需读取
    └── wiki_server.py                # 127.0.0.1 只读服务
```

旧 JSON、旧 HTML 和中间 CSV 可以保留审计，但未放行前不得成为公开图鉴入口。

## 2. 发布状态

`data/publication_policy.json` 是唯一公开开关：

- `published`：可被 builder 尝试发布，但仍必须通过第 4 节的行级契约。
- `quarantined`：旧档/候选/错链材料，只能显示隔离原因，不加载其数据。
- 未登记：默认与 `quarantined` 相同。

不得依据旧 `meta.evidence`、一段 `source` 文案、派生产物 SHA 或页面标题推断 `published`。

## 3. 源锁（source lock）

每个公开 board 的 `meta.provenance.source_locks` 至少有一个锁：

```json
{
  "sha256": "64 位小写 SHA-256",
  "bytes": 270106156,
  "mtime_ns": 1788266451099903500,
  "path_hint": "Documents/script.py314.lc.npk"
}
```

- 当前业务结论优先使用 Documents 当前快照；根目录 py314 全量基线和历史脚本包只能按 `live_sources.json` 的 source set 作为**独立、锁定、带快照标签**的回退/考古源，绝不静默补当前字段。
- base 与 CHS 必须同包、同快照配对。跨包配池未经过行级验证时，字段名可能静默串位。
- 若源包 SHA、bytes 或 mtime 不符，相关记录降为未验证，不能沿用旧 offset 或名称。
- 若表族使用热更分片，`base ∪ inc − del` 只能在同一锁定 NPK 内、经 entry/FID/loader 复放后执行；未复证前一律标 `unresolved-composition`，不得把其他包当作 `base` / `inc` / `del`。

### 3.1 双源并行读取与差异归属（2026-09-06 起）

`data/live_sources.json` 的两个**当前 Documents**源属于默认读取范围；同一 registry 中的根目录全量基线与历史包属于已锁定的备选源，默认不由 localhost reader 打开：

| source_id | 角色 | 允许证明 |
|---|---|---|
| `lifeafter-classic-current` | 正式服（经典服）当前快照 | 正式服包内静态存在、字段/配置链；不自动证明当前活动启用 |
| `documents-py314-current` | 测试服（简单生存服）当前快照 | 测试服包内预先资源/配置存在；不自动证明未上线或必将上线 |

1. **新侦查先双读、后裁决。** 同一目标表/资源须分别锁两源并产出 presence diff；不得再由任一生成器的默认 source 静默替代另一服的读取。
2. **跨源不拼接。** base、CHS、reward、名称或字段链仍必须在同一快照内闭合；两服相同 ID/路径/表 FID 只可作为“双方存在”事实，不能互拿字段补全。
3. **结果分类只描述快照可见性：**`both`、`formal-only`、`test-only`、`conflict`。它们不等同于“已上线 / 未上线 / 可得 / 过期”。
4. **测试服独有预告准入：**只有 `test-only` 条目已经对照 `E:\la拆包项目\明日之后完整历史更新汇总_2018-2026.md` 排除历史已上线，且具测试服同快照行级/资源 provenance，才能进入主页 **「零、新更新与预告专栏」**。显示时必须带“测试服独有预告”及源锁；不能混入一至四类的当前图鉴卡。
5. **未通过历史排除的 test-only 条目**留作候选/隔离档；正式服独有条目同样只标 `formal-only`，不得据此反推测试服遗漏或版本状态。
6. 历史已发布单源板不自动失效，但下一次重建前必须补双源 presence 检查；未完成前其 provenance 必须继续准确标示实际单源，而不能宣称双源结论。

## 4. 公开 board 的最小行级契约

### 4.1 `meta.provenance`

```json
{
  "audit_status": "passed",
  "source_locks": ["...source lock..."]
}
```

### 4.2 每一项

公开 item 同时保留兼容字段 `id/name/evidence/source`，以及以下可机读字段：

```json
{
  "id": "原始业务 ID；无原始 ID 时不得伪装成已核验图鉴项",
  "name": "显示名；未有名称正源时可为空或“未回填（ID …）”",
  "evidence_level": "见第 5 节",
  "provenance": {
    "source_lock_sha256": "必须属于 meta.provenance.source_locks",
    "source_entries": [
      {
        "entry_index": 22570,
        "file_id": "E1645717C83FC968",
        "decoded_sha256": "64 位 payload SHA-256",
        "role": "base 或 chs"
      }
    ],
    "table": "原表/资源结构名",
    "row_key": 1110181,
    "field_refs": ["skin_id", "model_path", "name:chs_slot=…"],
    "name_source": "同快照 common_item_data.id == skin_id"
  }
}
```

字段含义：

- `row_key` 是原始 row key、item ID 或可复跑 row offset；`wardrobe_0001`、`wattr_0001` 等合成序号不能替代。
- `field_refs` 逐项说明显示字段来自哪个原始字段/CHS slot，不允许用“整行字符串筛选”代替。
- `name_source` 必须说明同快照的结构化名称关系；相邻 CHS 文本、主题词、尺寸/形态、旧 CSV、模型目录名都不是名称正源。
- `source_entries` 要列出所有参与结论的 base、CHS、资源或 bridge 条目。

### 4.3 当前同快照文字表的额外契约

当 board 公开的是中文名称、说明等 CHS 文本来源，而不只是使用文本作显示标签时，每个已展示文本都必须额外保存可回放的槽位链：

```json
{
  "text_provenance": {
    "name": {
      "field_chs_slot": 123,
      "value_chs_slot": 4567,
      "scalar_type": "0x05",
      "text": "与 item.name 相同的文字"
    }
  }
}
```

- `field_chs_slot` 是 base schema 中字段名所在的同包 CHS 槽位；`value_chs_slot` 是该行文本值所在的同包 CHS 槽位。
- 只有字段槽位和文本槽位都能在已锁定的同包 CHS payload 中复放，才可称为“同快照名称来源”。仅保留已解码中文、不保留槽位编号，不满足文字来源链。
- 文字表只证明该 row 的字段文本；不自动证明道具当前可得、可购买、可开启、奖励内容、价格、货币、限购或活动启用。

## 5. 证据等级

公开数据只使用以下枚举：

| 值 | 能说什么 | 不能说什么 |
|---|---|---|
| `physical-resource-chain` | 路径/ID 已闭合到实体和 payload/entity hash | 不自动证明当前活动 |
| `structure-only` | 行、字段或静态结构可复跑 | 不证明业务启用、当前货架、概率语义 |
| `static/candidate` | 明确标作候选/匿名/未绑定材料 | 不命名为当前、未上线、商品或掉落 |
| `current-snapshot-verified` | 当前同快照、行级业务链已闭合 | 不跨服务器/快照外推 |
| `user-verified` | 用户实机锚点已记录 | 不补猜内部期数、概率、奖励 |
| `unverified-active` | 仅为待复证活跃线索 | 不得进入公开图鉴 |

`current-snapshot-verified` 必须额外有 `provenance.business_chain`；`user-verified` 必须有 `provenance.user_evidence`。两者缺失时 builder 拒绝发布。

## 6. 专题边界

- **奖池/商店/核芯**：静态表、`panel_show_item_ids`、入包资源或 `fortune_bag_dct` 只说明配置/展示层存在。要写当前期、在售、掉落、概率、保底，必须有 selector/consumer、时间或实机锚点和实际 reward/item 链。
- **武器皮肤**：正式名正源 = 同快照 BA8 `common_item_data_base` 行 `key==skin_id` 的 `name` 字段（CHS field/value slot 可回放）；描述同理取 `desc`。SFX 只能作为 `weapon_skin_data.key == weapon_skin_sfx_function_data.skin_id` 闭合后的**父皮肤子项**，不得并列成图鉴项，不得因去后缀根名一致而回填父项 `display_name`；一致根名最多记 `sfx_consensus_state` 审计线索。用户旧表名只留在 `reference_fields`（曾用名出处）。`pkg#entry`、c1/c2、mesh 数量、同目录或视觉相似都不是物理定位。
- **当前武器皮肤图鉴分层**：当前 BA8 基线 = **111 主皮肤**（`weapon_skin_data` 无时限后缀行；全部 verified 正式名/desc）+ **14 时限变体子卡**（`k%10==1` 且 `k//10` 为主皮肤：会员时限版，11 个有道具行正式名如"疾影枪（7天）"、3 个无道具行仅显示"主名（时限版）"）+ **3 行为资源预告项**（`1110184/1110186/1110190`，无父行无道具行，未回填）。顶层仅 111 主 + 3 预告 = 114 项；CSV 扁平 128 行。统计必须报告 `111/14/125/3/321/75`。旧 root 仅用于 key-presence 对照，且绝不能向 current `display_name` 回填旧名称。
- **时装/面饰/载具**：文本池、路径语素、主题白名单、投票/正则分类最多是候选；必须回到 row key、原始字段和同快照名称源。
- **匿名纹理**：展示为内容 hash 分组的匿名候选。没有 path/FID→实体→item/skin/config ID 和同版本差分，禁止称“未上线武器贴图”或“版本独有”。

## 7. 构建与验证

```text
python tools/build_wiki.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

builder 的规则：

1. 扫描所有 `data/boards/*.json`；
2. 只考虑 policy 明确 `published` 的 board；
3. 对每个候选执行行级 provenance 契约；
4. 任一已发布 board 契约失败，builder 失败且不生成新 manifest；
5. `manifest.js` 只包含通过的 board。

静态旧 URL 必须跳转到 `board.html?b=<id>`，由 policy 显示隔离原因；旧页面原文应保留到 `data/quarantine_legacy_html/`。

## 8. 迁移规则

1. 先新建带完整 provenance 的重建 board；不要就地把旧自由文本 `source` 改名成证据。
2. 每次重建先锁当前源包，并用现场按需读取或同快照工作副本复验 entry payload SHA。
3. 旧 board 只有在每项都有行级 provenance、审计状态为 `passed`、且业务表述与等级一致时，才可在 policy 中由 `quarantined` 改为 `published`。
4. 一个 board 内部分通过时，只发布通过行；其余保留隔离档案或候选池。
