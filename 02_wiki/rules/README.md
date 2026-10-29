# rules/ — 规则层（唯一事实来源）

> 人与 agent 共同维护的**人工判定口径层**。构建器、RUNBOOK、memory 都引用这里，不各自复制一份。
> **本目录文件禁止被任何脚本自动覆盖。** 脚本只读，不写。

## 目录

| 文件 | 内容 | 维护时机 |
|---|---|---|
| `servers.yml` | 服名官方口径（简单生存服=kj1 / 经典服=base）、分服子卡铁律、缺失显式空卡 | 服名/分服口径变更时 |
| `equip_scope.yml` | 装备收录口径（键段划分、排除规则、trial 合并、待补项） | 用户逐类判定后 |
| `vehicle.yml` | 载具板口径（面板字段来源、速度量纲、modding 指针基址、氮气、hp 曲线） | 载具深挖有新结论时 |
| `known_issues.yml` | 已知问题登记（门禁红板、缺口、修复路径） | 每次体检后 |
| `pipeline_graph.yml` | **板级重建执行图**（编排器唯一执行来源，每步标注顺序依据与出处） | 人工判定板内脚本顺序后 |
| `boards/<board>.yml` | 每块板的来源、条目数、主产出脚本、后处理脚本、重建风险等级 | 自动生成，勿手改 |
| `pipeline.yml` | 重建流水线总览：三层边界、发布门禁命令、高风险板清单 | 自动生成，勿手改 |
| `tools_inventory.yml` | 全部 tools 脚本的角色分类（build/patch/check/probe/infra） | 自动生成，勿手改 |

## 自动生成 vs 手工维护

- **手工维护**：`servers.yml`、`equip_scope.yml`、`vehicle.yml`、`known_issues.yml`、`pipeline_graph.yml`
- **自动生成**：`boards/*.yml`、`pipeline.yml`、`tools_inventory.yml`
  由 `python 02_wiki/web/tools/build/gen_rules_inventory.py` 生成（幂等，可随时重跑）。

## 执行图 vs 角色分类（★ 关键区别，别混用）

`boards/<board>.yml` 的 `primary_builders` / `postprocess_scripts` 是**脚本角色分类**
（按函数名前缀判 build / patch / 其他），**不是执行顺序**。

实测证据：vehicle_full 的 7 个脚本里，角色分类给出的顺序与真实顺序**仅 1 处吻合**
（v1/v2 分类脚本是口径替代关系，v2 必须后跑；实测按角色分类排会把 v1 排到 v2 之后，
导致 v1 的旧口径 `vehicle_class` 覆盖 v2 的新口径）。

⇒ **执行顺序只能来自 `pipeline_graph.yml`**（人工判定，每步带 `order_basis` + `source`）。
编排器 `build_pipeline.py` 只认这个文件；未声明的板按 `inferred` 处理，默认不执行。

## 使用约定

1. 脚本里**禁止**硬编码服名映射、排除列表、字段来源优先级 —— 一律从本目录读。
2. 口径变更流程：改本目录 → 重跑 `gen_rules_inventory.py` → 重建受影响板 → 跑门禁 → 写交接卡。
3. 新增板：先在对应 `boards/<board>.yml` 出现（脚本会识别），再补该板的专属口径到 `servers.yml` / `equip_scope.yml` 等。
4. `rules/` 变更必须体现在 diff 报告的「口径变更」小节，与「数据变更」分开呈现。
5. **调整板内脚本顺序 → 改 `pipeline_graph.yml`**，不要去改 `boards/*.yml`（自动生成，会被覆盖）。
6. 重建板级产物统一走编排器（不要手敲脚本序列）：
   ```
   python 02_wiki/web/tools/build/build_pipeline.py --check                    # 体检
   python 02_wiki/web/tools/build/build_pipeline.py --board <板> --apply        # 重建单板
   python 02_wiki/web/tools/build/build_pipeline.py --all --apply               # 全量
   ```
   编排器会依次跑：灰度快照 → 主产出 → 后处理 → 溯源契约修复 pass → 发布门禁 → 条目级 diff → 更新日志草稿。
   **默认 dry-run**，`--apply` 才落盘；`--resume` 从上次中断处续跑。
7. 产物重建脚本**必须幂等**：同输入重跑产物字节不变。`meta.notes` 用
   `notes_util.append_note()` 幂等追加，**不要无条件拼接**（否则每跑一次多一段，
   噪声无界增长且幂等性永不成立）。
