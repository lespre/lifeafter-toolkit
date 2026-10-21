# PROJECT_STATE

> Workbench version: **v1.3（Web Client / Projection Performance）** · 生成 2026-09-13T05:00:01

## 运行方式
- API：`python -m api.server --host 127.0.0.1 --port 8770`（只读；无写端点 ⇒ POST 405）
- CLI：`python -m api.cli status|items|entity|coverage|pools|rewards|skins|fashion|residuals|evidence`（无 Wiki 也能用）
- 投影：`python -m pipelines.projection.build_boards`（默认只出 lightweight；`--offline-full` 才重建全量导出）

## Active artifacts
| domain | artifact | 规模 | 默认 Web 路径 |
|---|---|---|---|
| item | `artifacts/active/item/ITEM_MASTER.jsonl` | 30,467 行 / 6 namespace | **API 分页** `/api/items`（≤200/页） |
| lottery | `LOTTERY_POOL.jsonl` + `LOTTERY_REWARD_TARGETS.jsonl` | 24,041 / 23,567 | **API 分页** `/api/lottery/*` |
| weapon_skin | `WEAPON_SKIN_RESOLVED.jsonl` | 115 行（113 verified） | 静态投影（小 Domain） |
| fashion | `FASHION_IDENTITY_STATE.json` | 状态型，**不伪造 entity detail** | 静态投影 |

## 首屏 payload（实测）
| 页面 | 旧 | 新 |
|---|---|---|
| item | 35,748,342 B（34.09 MB board.js） | 22,200 B（`/api/items?page_size=50`） |
| lottery pool | 16,782,690 B（16.01 MB） | 22,260 B |
| lottery rewards | 21,097,666 B（20.12 MB） | 34,703 B |
| entity 详情 | — | 5,222 B（`/api/entity`） |
| 状态页 | — | 25,058 B（`/api/coverage`） |

## 投影定位（v1.3）
- **lightweight**（默认生成，KB 级）：`item_stats`、`lottery_stats`、`fashion_active`（weapon_skin_active 已降为 internal 审计投影）
- **offline_full_projection**（数十 MB，`web_default=false`）：`item_master_active`、`lottery_pool_active`、`lottery_rewards_active`
  —— 仅离线/导出/兼容，**不作为默认 Web 路径**（board.html 需显式 `?offline=1` 才加载）

## 视图分层
- **Wiki View**（wiki.html / board.html）：名称/分类/属性/奖池内容；技术字段隐藏在渲染层
- **Workbench View**（workbench.html / workbench_items.html / workbench_lottery.html / workbench_entity.html / workbench_status.html）：
  snapshot 基准、provenance、evidence、residual、binding status、source
- 两者**共享同一 Domain 数据**（services → API），不维护两份业务数据

## 统一 Entity Detail（Identity / Data / Source / Raw presence / Evidence / Provenance / Residuals / Media）
适用：item、weapon_skin、lottery_pool、lottery_reward。`/api/entity?kind=…`
- snapshot 基准硬规则：`Snapshot basis` 与 `Current snapshot binding` 分开显示，**不得简化为 verified**
- `media` 区域预留（本轮不做图片链）

## 四条核心链（状态不变）
- Item：closed ｜ residual **554**（549 无 namespace 成员 + 5 ambiguous）
- Fashion：closed ｜ 语义 verified ｜ 绑定类全 unresolved（A2F native 硬阻断）
- Weapon Skin：**Golden Chain CLOSED（v1.4 Phase 2）** ｜ 主体 = canonical weapon_skin_data @BA8A（126 行）｜ payload binding 已登记（data 11817 / CHS 21177）｜ name verified 122（canonical_row_field_chs 链）｜ name unresolved 4（11100061/11101341/11101681/11101831，canonical 无名称行）｜ board-only 4 行（1110184/1110185/1110186/1110190）只留 diff/链级样本 ｜ grade = deprecated_board_derived（canonical 只有 level/priority）｜ listing_status 仅 unresolved ｜ timed_relation unresolved（不重调查）
- Lottery：layered_closed ｜ pool/static typing verified ｜ unresolved **1,665** ｜ runtime_final = unresolved_replacement_overlay

## 覆盖度（数据覆盖 residual，一律保留不追）
- current CHS 绑定 unresolved ｜ current base/inc/del 组件级绑定 ｜ 10 表无 canonical FID ｜ 554 / 1665
- BA8A（inventory 基准）14 表 data+CHS 全 ok ｜ current 4 表 data 可 FID 定位、CHS 未定

## 口径（用户修正，继续有效）
snapshot entry-space mismatch 是**当前继续解析/复现的主要基础设施阻断**；修复后需重新分类，
**不能预设 residual 会全部消失**（仍可能存在真正没有 namespace / runtime 证据的 ID）。

## Workbench v1.3 = frozen
- 冻结范围：API-first 分页查询、统一 Entity Detail、Wiki/Workbench 视图分层、projection 轻量/离线双轨、只读 API。
- 冻结后**不再新增功能**；后续任何改动需新的阶段指令。

## 下一阶段（已确定，不含图片）
**Locator Chain Consolidation** —— 重新整理并固化这条链：
`runtime → namespace → logical table → snapshot → FID → entry → CHS → decoded row → schema/field → business identity → name`
- Wiki / 图片 / 新 Domain **全部暂停**，不在本阶段范围。


## Workbench v1.4 — Locator Chain Consolidation
- Phase 1 = CLOSED（`3f51205`）：链模型 / registry / auditor 10 项 / explain。
- **Phase 2 — Weapon Skin Golden Chain = CLOSED**
  - 一/二 已登记：`registry/tables.json#snapshot_payload_bindings.weapon_skin`（BA8A data entry 11817 / CHS entry 21177，entry 走 v1.2 PayloadResolver；FID 该快照不可得 ⇒ 如实留空）。
  - 三 canonical 重建：`tools/rebuild_weapon_skin_v02.py`（只用 locator+decoder，构建期零 board 读取）→ 126 行；diff：intersection 111 / canonical-only 15 / board-only 4。
  - 四 名称链：`skin_item_id → common_item_data_base 行 → name field slot → CHS text`，122 条逐条给证据；1110185 / 1110186 保持 unresolved（不补假名）。
  - 五 去 board 依赖：RULES.generated_from = canonical；board 降级 historical/presentation；测试 `test_weapon_skin_v02_canonical.py::test_build_succeeds_with_legacy_board_hidden` 临时隔离 board 仍可重建；registry legacy_debt = **repaid**。
  - 六 v0.2 产物：`artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl`（+RULES/STATUS_VOCAB/MANIFEST/audit）；v0.1 → `artifacts/historical/weapon_skin/v01`（原版）与 `v01_status_patch`（带状态补丁版）；迁移记录 `state/weapon_skin_v02_migration.json`。
  - 七 Listing Status：不变更、不扩展调查；作为独立 residual 落 `residuals/weapon_skin/listing_status.json`（全部 unresolved）。


## 武器皮肤（毕业态 · 2026-09-13）

- **唯一图鉴入口**：`data/boards/weapon_skin_sfx_text_sources.json` → `board.html?b=weapon_skin_sfx_text_sources`
  基准 = **当前包 `508bb5bd`（2026-09-13 10:02 热更）**，FID 直读，不用 entry 序号。
- **覆盖**：131 行 = 113 主卡（current_parent）+ 18 时限变体（嵌父卡，8 位块 `//10` 归父）+ 2 行为资源预告（1110185/1110186）。
- **canonical 结构视图**：`artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl`（126，基准 `test-documents-ba8a239a` pre-09-10）
  → 状态 `superseded_for_display`，保留作内部审计/交叉核对；投影 `weapon_skin_active` = `internal`（`published_hidden`，不进首页）。
- **残差**：见 `analysis/audit/weapon_skin_optional_pass.json`（10 项 bounded_unresolved，含已试路线）+ `residuals/weapon_skin/`。
- **毕业报告**：`analysis/audit/WEAPON_SKIN_GRADUATION.json` / `docs/WEAPON_SKIN_GRADUATION.md`。

## 皮肤音效（Web 区块 · 2026-09-13）
- 「皮肤音效」区块（`details.audio`，与「时限变体」「特效与战斗表现」同级，排其后）：**34 卡 / 386 条**（第二波 24 卡 + 第三波：极狐破坏者=专属音（与2.5同批）开火/换弹 6 条✓、焚古龙息=推断 flame_loop/shoot 2 条（未实机验证）、阿赖耶识+冰刀核芯）。
- 资产：`assets/audio/weapon_skin/`（272 WAV / 87.5 MB）；绑定数据 `data/weapon_skin_audio_attachments.{json,js}`；匹配证据 `artifacts/active/weapon_skin_audio/BATCH2_MATCH.json`。
- 听辨终审（2026-09-13）：极狐=专属音 开火/换弹✓（攻击/核芯✗）；焚古=推断（无参考，挂账 pending）；诡秘之颅/熔炉寒霜 ✓。扫描全档：`artifacts/active/weapon_skin_audio/SCAN_ROUND2_REPORT.json`。
- 守护测试：`tests/test_weapon_skin_audio_section.py`（32 块 / 逐块计数 / 阶段口径 / 真实 Chrome 实测）。
- 全链归档：`docs/WEAPON_SKIN_AUDIO_CHAIN.md`（全景图 `03_执行\\30_分析/audio_review/音效定位链_全景图.html`；含单皮 SOP / 证据等级 / 死引用 19 条）。

## PC 测试服热更覆盖层（2026-10-16）

- 图鉴板 `weapon_skin_sfx_text_sources` = BA8A 快照基线 119 条 + **PC 测试服 2026-10-15 热更覆盖层 4 条**
  （`overlay_id=playertest-newpc-hotfix-20261015`；客户端 `E:/mrzh` 只读；与正式服/APK 无关）。板共 122 条。
  - 新增主表父行：`1110188`（突击步枪 / level5 / `skin_1001_017`）、`1110191`（手枪 / level2 / `skin_1003_013`）、
    `1110192`（电磁机枪 / level4 / `skin_1008_007`，由原「仅行为资源行」升为主表行，就地升级非新增）。
  - 仅行为资源行：`1110189`（`skin_1013_010` 资源路径；无父行 / 无道具行 / 无名称，不计入主表新增款数）。
  - 名称纪律：本热更没有 `common_item_data_base` 道具行 ⇒ `1110191/1110192/1110189 = unresolved`；
    `1110188 = candidate`（「星魂追光」，仅礼包描述旁证 `gift_data` row 139415），页面标「（名称候选）」。
  - A-SOUL 线索：SFX 行 `1120382`（`sfx_type=15`、`sfx_params=ASoul`）+ 音效事件组 `/asoul_202609/*`；
    音频 16 条样本已导出（`assets/audio/weapon_skin/asoul_202609/`），bank/样本可播但**皮肤静态绑定=候选**，故未进「皮肤音效」区块。
- 证据形态：覆盖行 `evidence_level=structure-only`，`source_lock` 独立指向热更解码 payload 的 sha256
  （`_bits/post__weapon_skin_data.py.bin` / `post__weapon_skin_behavior_res_data.py.bin`），
  `upstream.entry_index=0` 仅表示整表转储（行身份靠 `row_key` + payload sha256），不与 BA8A 做字段 join。
- 管线：`tools/build_weapon_skin_hotfix_record.py`（只读解码 payload → `data/hotfix/weapon_skin_hotfix_<overlay>.json`）
  → `tools/apply_weapon_skin_hotfix_overlay.py`（校验锁 → 备份 → 合并 → 同步 `.json`/`.js`，`--check` 幂等）。
- 下游影响（都已同步改工具+契约测试）：冻结候选板 `weapon_skin_static_candidates_v01` 只投影冻结源行，
  覆盖行逐条留档于 `meta.excluded_overlay_rows`（顶层 119→118）；预告专栏 `skin_behavior_preview` 的
  「仅行为资源」名额由 `1110192` 换成 `1110189`（仍 6 条）；名称三级契约按「冻结源 / 覆盖层」分别约束。
- 守护测试：`tests/test_weapon_skin_hotfix_overlay.py`（payload 锁、字段、名称纪律、工具可重放、幂等）。
- 备注：仓库内另有一批与本次无关的历史失败（live source SHA mismatch 类、`wiki.html` 内联脚本语法），
  本次以「改板前后各跑一次全量 pytest 取差集」的方式区分，未扩大范围修它们。
