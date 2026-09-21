# DeepSeek V4F 接手说明：LifeAfter Wiki / 武器皮肤名称链

> **唯一正式记录**：`E:\la拆包项目\06（agent写）拆包器进展与交接日志.md`，先读其 **27.11** 与 **27.12**。
>
> 本文件是快速启动卡，不与正式日志竞争结论；两者冲突时以正式日志和当前原始包为准。

## 0. 接手后的第一目标（2026-09-03 晚已完成）

**正式名正源已找到并闭环**：BA8 `common_item_data_base`（entry 18005，FID `B42760CCA41DBC25`）+ `common_item_data_base_chs`（entry 23928，FID `EF3A8474A5E5F7A4`），35,948 行，行 `key==skin_id` 的 `name`/`desc` 带可回放 CHS 槽。111 主皮肤全部 verified，14 时限变体收为子卡，3 行为预告未回填。详见正式日志 **27.13**。

后续最高优先级（见 §6）：

```text
exchange_static_structure 名称 join（同快照 common_item_data_base / gift_data 兜底）
→ 仍缺 runtime selector/consumer → 不得宣称当前货架
```

不要重做武器皮肤图鉴，不要先扫 GPK/贴图。

## 1. 原始主源与硬边界

**热更架构速览（详见正式日志 27.14）**：根目录 = 全量基线（res.npk 2024-12 / script.py314.lc.npk 8-27）；Documents = 热更覆盖区（当前 = 9-01 BA8）。业务表以 `xxx.py MergedTableData 合并壳 + _base + _inc + _del` 组织，当前表 = base ∪ inc − del；`_base` 是完整快照（如 common_item_data_base 35,948 行）。资源热更 = Documents/res 的 wpk 分卷 + Documents/gres 的 gpk；client_doc@1_1103xxxx 空文件是已应用补丁的编号点序列。

当前体验服唯一事实主源：

```text
E:\mrzh\Documents\script.py314.lc.npk
SHA-256: 328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f
bytes: 270106156
mtime_ns: 1788266451099903500
```

- 原始包和 `E:\mrzh` **严格只读**；写入只允许 `E:\la拆包项目\03拆包产物`、`E:\la拆包项目\08Lifeafter wiki` 和临时目录。
- root `E:\mrzh\script.py314.lc.npk`（SHA `0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7`）只用于 key-presence 版本对照，**不得给当前 display_name 回填名称**。
- `common_item_data` 的 BA8 base FID `1232F498D07A0EBB` 是 815B 占位模块，无 `x{` 表体；其孤立 CHS、root/旧 CSV 都不能给 BA8 current 回填名称。
- 静态入包不证明活动开启、可得、价格、概率、战力或业务归属。

## 2. 已完成且不要回退的内容

### 2.1 全量图鉴

公开 board：`data/boards/weapon_skin_sfx_text_sources.json`

```text
128 catalog rows
= 125 current_parent (weapon_skin_data)
+ 3 behavior_preview_only (weapon_skin_behavior_res_data)
321 nested SFX rows
75 parents with SFX / 50 parents without SFX
```

三个行为资源预告：

```text
1110184 → skin_2003_033（2 条路径）
1110186 → skin_2003_031（2 条路径）
1110190 → skin_1006_013（5 条路径）
```

核心当前表 FID / entry：

| 表 | base | CHS |
|---|---|---|
| `weapon_skin_data` | `765AB12F1D6EB0EA` / entry 11817 | `D35E3103168889D2` / entry 21177 |
| `weapon_skin_sfx_function_data` | `B693DB548E5412B6` / entry 18238 | `5C56D035B329BEBB` / entry 9096 |
| `weapon_skin_behavior_res_data` | `9F445AE2AA87D880` / entry 15939 | `E59CCA1F31417C6A` / entry 22997 |

关键入口：

```text
tools/rebuild_weapon_skin_catalog_current.py
tools/rebuild_weapon_skin_sfx_text_sources.py  # 兼容委托入口
tests/test_rebuild_weapon_skin_catalog_current.py
tests/test_rebuild_weapon_skin_sfx_text_sources.py
```

### 2.2 历史整理参考层

用户上传的旧表已原字节固化：

```text
data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv
128 rows
SHA-256: 827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456
```

它提供名称、描述、联动、动作、战斗表现，输出到每项 `reference_fields`。可在 UI 可见，但必须标为：

```text
历史整理参考（用户提供；非当前正式名正源）
```

构建器已强制 SHA 相等；更改 CSV 后必须先审计、更新测试和 source hash，不能直接覆盖。

### 2.3 父/子与命名铁律

```text
weapon_skin_data.key == weapon_skin_sfx_function_data.skin_id
```

只证明父/子关系，**不证明 `sfx_name` 是正式皮肤名**。

- SFX 只能嵌套在精确 `skin_id` 父项下，绝不平铺为皮肤。
- 即使多条同 ID SFX 去后缀后同根，也只能状态 `sfx_consensus_unpromoted`；父项 current `name` 仍为“未回填（武器皮肤 ID …）”。
- 根包名称、旧 v5/v7 CSV、模型路径、目录名、CHS 相邻文字、视觉相似性都不能提升 current 名。
- `behavior_preview_only` 只有行为资源路径，不伪称正式皮肤。

### 2.4 铠甲面板已同步修正

`lottery_kaijia_panel_static` 现在只允许当前 `gift_data.name` 回填。

```text
1110181 / 1110182 / 1110183
= 未回填（ID …）
```

已删除 `resolve_unanimous_sfx_name` 分支，别恢复。

## 3. 推荐执行路径：找 BA8 正式名称父表

1. **先做 source lock**：用 `data/live_sources.json` 和 `tools/live_npk_reader.py` 校验包 SHA/bytes。失败立即停止，不能沿用 entry index。
2. 从 BA8 原 NPK 的当前 code/module 条目中搜索名称表 consumer/loader 线索；工作副本只能做 locator，最终必须回原包按 FID 读取。
3. 候选 base+CHS 必须同时通过：
   - base 有真实 `x{` BinDict 表体，非加载壳；
   - base 与 CHS 来自同一 BA8 快照；
   - CHS field slot 能复放预期字段名，value slot 能复放正式文本；
   - 行 key 或显式字段能与 `skin_id` 直接、可解释地 join；
   - 抽样检查字段语义，不能只是“能解出中文”。
4. 只在找到 `skin_id → formal-name` 的可回放结构化关系后，才新增 `official_display_name` / `official_name_status=verified`，并将对应父项 current `name` 升级。
5. 先写 RED 测试：不合格候选表、SFX/历史参考/root 名源都必须被拒绝；再实现、重建、全套测试、HTTP 验收。

**已排除的反例**：

```text
BA8 common_item_data base: 815B 占位，不能用
lib_fashion.py 旧配对：字段/值串位，不能用
旧 behavior entry 15858/22893：已漂移为加载壳/错误 index，不能用
```

## 4. 当前产物与验收基线

```text
data/boards/weapon_skin_sfx_text_sources.json
  SHA-256 fb98e5089792f6856c2b92e1d6a885ce9eff3ac31102d206ea0da1eb5368896e
  1,540,249 B

data/exports/weapon_skin_catalog_current.csv
  SHA-256 0b516298781db178289c0faa30caad958b223668c01e2f72ac65ca71fc8f5e09
  65,885 B

data/boards/lottery_kaijia_panel_static.json
  SHA-256 a0063057766513943d6ad243e02960c8f53392c60668e56bb37587f0cbca81ff
```

最后已验证：

```text
unittest discover: 22/22 PASS
HTTP: 5 published boards / 7534 records
128 catalog / 125 parents / 3 previews / 321 SFX / 128 CSV rows
kaijia SFX-derived names: 0
legacy weapon_attrs: 404
```

## 5. 开始命令与交付门槛

```bash
cd 'E:\la拆包项目\08Lifeafter wiki'
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python tools/rebuild_weapon_skin_catalog_current.py
PYTHONDONTWRITEBYTECODE=1 python tools/rebuild_kaijia_panel_static.py
PYTHONDONTWRITEBYTECODE=1 python tools/build_wiki.py
```

改动完成后必须：

```text
py_compile → 定向 RED/GREEN 测试 → 全套 unittest → localhost HTTP → 临时 ad-hoc verifier
```

临时验证脚本只能放系统 Temp，结束必须删除。所有正式结论追加到唯一正式日志，别在 root 新建杂项日志。

## 6. 第二优先级（名称链之后）

`exchange_static_structure` 目前仅为 BA8 匿名静态结构：70 mapping rows / 1757 pairs / 1738 decoded details / 19 unresolved。

要回填商品名称，需要另建：

```text
current exchange detail → 同快照 item/gift 正式名 join
→ runtime selector / consumer
→ 才能讨论当前货架、价格、货币、限购或活动
```

在此之前不能把静态 `shop_key/slot_key/detail` 写成当前在售商品。
