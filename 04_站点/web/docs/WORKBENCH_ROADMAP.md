# LifeAfter Wiki / 本地数据工作台 · 四链优先路线图（P0–P7）

> 状态标记：[x] 完成 · [~] 部分完成（注明） · [ ] 未开始
> 纪律（用户定版）：client（测试服/正式服）与 server branch（经典服/简单生存服）是独立维度，
> 仅凭客户端目录不能判定服务器分支，无法证明一律 unresolved；禁止模型直接写 Wiki boards。
> 更新时间：2026-09-07（四链优先级正式冻结）
>
> **唯一执行路线：P4-A 道具总表 → P4-B 时装 → P4-C 武器皮肤 → P4-D 抽奖奖池 → 四链稳定后统一重建 Wiki。**
> 当前仅激活 P4-A；P4-B～P4-D 等待，不得自动启动。P0～P3 的旧全游戏横向清单仅保留为历史地图，不能据此恢复活动、商店、载具或其他已暂停方向。
>
> 暂停范围：活动定位、商店/兑换、载具专项、普通武器专项、任务/副本、其他业务表、图片/模型资源。
> 执行边界：不因相同整数跨表认领实体；无法证明即 unresolved；P3 unsafe/unresolved 不越级；`all_equips.name/desc/icon` 永久禁用；`server_branch` 保持 unresolved，除非出现独立证据。

## P0 数据源基础

- [x] 1. 盘点测试服客户端全部文件 —— 11,344 文件清单
      `data/audit/client_file_maps/mrzh_file_inventory.jsonl`（路径/大小/ext/mtime/SHA）
- [x] 2. 盘点正式服客户端全部文件 —— 17,588 文件清单
      `data/audit/client_file_maps/lifeafter_file_inventory.jsonl`
- [x] 3. 标记每个文件/包的大概用途 —— 路径身份特判+扩展名映射+魔数抽检
      （verified=抽检命中样本 / likely=映射 / unknown=4+3 条）
- [~] 4. 区分配置/文字/UI/贴图/模型/音频/其他 —— **文件层**已完成（report B 段）；
      包内条目级分类属 P1/P2（script 容器内才是文字/配置主体）
- [x] 5. 修正客户端与服务器分支关系 —— client 维度 verified（任务指定+体验服.lnk/正式服.exe）；
      server_branch 一律 **unresolved**，历史 mrzh↔简单生存服绑定不进入新结论
- [x] 6. 建立统一 source registry —— `data/source_registry.json` schema v1：
      398 源（test 324 / live 74），含容器/script/散装配置/文件清单；server_branch 一律 unresolved；
      构建器 `tools/build_source_registry.py`，回归 `tests/test_source_registry_unified.py`（5/5）
- [x] 7. 给所有数据源做 SHA/snapshot 锁定 —— registry 内 398 项 **sha_missing=0**；
      补算 mrzh 5 个 >3GB 大 npk SHA；与 live_sources.json 11 script 项交叉一致 11/11；
      媒体/缓存/日志不纳入（记录排除原因）

## P1 全游戏索引

- [~] 8. 建立全部包文件索引 —— P1-8 进行中：
      Stage 1 FHPK 评估 ✅（官方文件级清单 1,580/1,526）；
      Stage 2+3a script/npk 166/166 ✅（1,932,449 条目）；
      Stage 3b gpk 136/136 ✅（2,169,772 条目）+ idx 27/27 ✅（61,277 记录）+ wpk 118 登记 ✅；
      fpk 73 包帧索引后台进行中；Stage 4 统一 file_index 合并器已就绪（tools/merge_file_index.py）
- [ ] 9. 建立 FID / entry 索引
- [ ] 10. 建立全部配置表索引
- [ ] 11. 记录 base / CHS / inc / del 表族关系（common_item 家族已有先例：base 18005/inc 5292/del 16447/壳 1765）
- [ ] 12. 建立行级 row / key / offset 索引
- [ ] 13. 建立 ID 全局出现位置索引

## P2 字段解析

- [ ] 14. 逐表确认字段含义
- [ ] 15. 标记可信字段
- [ ] 16. 标记错位 / 不可信字段
- [ ] 17. 建立 FIELD_RULES
- [ ] 18. 无法确认的字段保持 unresolved

## P3 可靠数据源筛选

> 四链所需的 P3 基础已建立；业务级放行仍必须在各链内重新经过字段、身份、负对照和 provenance 门禁。旧的全业务来源盘点暂停。

- [x] 19. 名称链来源基础 —— P4-1 已关闭
- [x] 20. 物品身份来源基础 —— P4-2 已关闭
- [~] 21. 时装来源基础 —— 当前执行与审计完成，0 verified self-ID，等待真正身份链
- [ ] 22. 武器皮肤来源 —— 仅限 P4-C 启动后盘点
- [ ] 23. 抽奖奖池来源 —— 仅限 P4-D 启动后盘点
- [x] 24. `FIELD_RULES` / `RELIABLE_SOURCES` / provenance 基础
- [~] 25. `server_branch` —— 保持 unresolved，禁止从客户端目录推断

## P4 四条业务身份链

### 已关闭基础阶段

- [x] P4-1 名称链 —— 已关闭
- [x] P4-2 物品身份链 —— 已关闭
- [~] P4-3 时装身份执行与独立审计 —— 当前阶段基本完成；0 verified self-ID，不伪造闭环

### P4-A 道具总表（当前唯一激活）

- [ ] 扩大 verified item self-ID 覆盖
- [ ] 明确 `common_item` 的 base / inc / del 各自可证明范围
- [ ] 核对 `name`、`max_stack_num`、`hide_in_bag`、`type` 等可靠字段
- [ ] 区分正式道具、内部配置、占位项
- [ ] 建立可信 `ITEM_MASTER`
- [ ] 审计重复 ID、多名称、缺名称

### P4-B 时装（等待）

- [ ] 正式收口当前时装阶段
- [ ] 继续寻找真正可证明的 fashion self-ID
- [ ] 验证 `fashion_id` / `row_key` / 名称关系
- [ ] 查找静态消费者或显式映射
- [ ] `fashion_data.py` 当前 P3 likely，不越级使用
- [ ] 建立“时装 ID → 正式名称”链

### P4-C 武器皮肤（等待）

- [ ] 盘点 verified 来源并验证 `weapon_skin_data` 等核心来源
- [ ] 审核 `skin_id` / `weapon_id` / `parent_id` 等可靠字段
- [ ] 区分 self-ID / foreign reference / variant reference
- [ ] 验证主皮肤 / 变体关系
- [ ] `sfx_name` 不得冒充皮肤正式名
- [ ] 禁止相同整数直接撞 `common_item` 补名称
- [ ] 建立 `WEAPON_SKIN_IDENTITY`

### P4-D 抽奖奖池（等待）

- [ ] 盘点 verified 的 lottery / reward_pool 来源
- [ ] 识别奖池 self-ID
- [ ] 建立“奖池 → reward group → reward slot → item ID”链
- [ ] 验证数量、权重 / 概率
- [ ] 仅在末端接入已验证道具 ID 和名称链
- [ ] 禁止同整数直接 join
- [ ] 建立 `LOTTERY_POOL_RESOLVED`

### P4 暂停项

- [ ] 活动定位 —— 暂停
- [ ] 商店 / 兑换 —— 暂停
- [ ] 载具专项 —— 暂停
- [ ] 普通武器专项 —— 暂停
- [ ] 任务 / 副本及其他业务表 —— 暂停

## P5 统一文字数据库（四链稳定后）

- [ ] 汇总四链 raw / parsed / resolved 结果
- [ ] 在已证明的业务身份内去重，不做跨表整数猜测
- [ ] 建立四链实体关系与逐条 provenance
- [ ] 禁止模型直接写 Wiki boards

## P6 Wiki 统一重建（四链稳定后）

- [ ] boards 只从四链 resolved 产物自动生成
- [ ] 重做分类页、实体详情页与全局搜索
- [ ] 加客户端、版本/snapshot、证据状态筛选
- [ ] `server_branch` 在无独立证据时只展示 unresolved
- [ ] 加原始数据与证据链查看入口

## P7 图片 / 模型资源（暂停）

- [ ] 图标、UI 图片、贴图、模型索引 —— 暂停
- [ ] 图片与实体 ID 绑定 —— 暂停
- [ ] 图文 Wiki 升级 —— 四链文字与身份稳定后再评估

## 当前完成度对照（2026-09-07）

- P0～P3：四链执行所需的定位、字段、来源与名称基础已建立；旧全游戏横向扩展暂停
- P4-1：名称链已关闭
- P4-2：物品身份链已关闭
- P4-3：时装身份执行与审计基本完成，0 verified self-ID
- **当前：仅 P4-A 道具总表激活，但尚未自动开始扫描、解码或构建**
- P4-B～P4-D：等待
- P5/P6：四链稳定后进入
- P7：暂停

## 文件地图产物（P0 交付）

- `tools/scan_client_file_map.py`：只读全盘枚举 + 定向 SHA（容器/配置类）
- `tools/analyze_client_file_map.py`：分类/差异/候选/报告（可复跑）
- `data/audit/client_file_maps/`：mrzh+lifeafter inventory JSONL、report.md、facts.json
- 分类结论分级：verified（魔数抽检/路径身份）/ likely（扩展名+目录角色）/ unknown
