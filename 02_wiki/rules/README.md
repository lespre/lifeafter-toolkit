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
| `boards/<board>.yml` | 每块板的来源、条目数、主产出脚本、后处理脚本、重建风险等级 | 自动生成，勿手改 |
| `pipeline.yml` | 重建流水线总览：三层边界、发布门禁命令、高风险板清单 | 自动生成，勿手改 |
| `tools_inventory.yml` | 全部 tools 脚本的角色分类（build/patch/check/probe/infra） | 自动生成，勿手改 |

## 自动生成 vs 手工维护

- **手工维护**：`servers.yml`、`equip_scope.yml`、`vehicle.yml`、`known_issues.yml`
- **自动生成**：`boards/*.yml`、`pipeline.yml`、`tools_inventory.yml`
  由 `python 02_wiki/web/tools/build/gen_rules_inventory.py` 生成（幂等，可随时重跑）。

## 使用约定

1. 脚本里**禁止**硬编码服名映射、排除列表、字段来源优先级 —— 一律从本目录读。
2. 口径变更流程：改本目录 → 重跑 `gen_rules_inventory.py` → 重建受影响板 → 跑门禁 → 写交接卡。
3. 新增板：先在对应 `boards/<board>.yml` 出现（脚本会识别），再补该板的专属口径到 `servers.yml` / `equip_scope.yml` 等。
4. `rules/` 变更必须体现在 diff 报告的「口径变更」小节，与「数据变更」分开呈现。
