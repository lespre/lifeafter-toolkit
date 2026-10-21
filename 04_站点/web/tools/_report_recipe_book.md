# 食谱板块交付报告（recipe_book）

- 生成日期：2026-10-19
- 板块：`三、活动类 / （四）食谱`
- 构建脚本：`04_站点/web/tools/build_recipe_board.py`（旧半成品备份：`build_recipe_board.py.bak_20261019_pre_fix`）
- 数据源：`03_执行/41_还原树/Documents/script.py314.lc.npk/com/cdata/cook_recipe_data.py`
  （+ `_chs.py`；成品道具行取 `edible_item_data.py` / `_chs.py`，同快照）
- 上游包：`E:/mrzh/Documents/script.py314.lc.npk`（195,840,216 B，sha256 `c9e12b43…`；`41_还原树/_热更合并台账_20261017_005239.json` 的 layers[].source 即此路径）

## 1. 交付物

| 文件 | 说明 |
|---|---|
| `data/boards/recipe_book.json` | 2.7 MB，571 条 |
| `data/boards/recipe_book.js` | `window.WIKI_BOARD_recipe_book = …`（build_wiki 亦会按 json 重写一份） |
| `assets/recipe_icons/*.png` | 294 张（299 条食谱引用；其余为同图复用），RGBA，`_b`=300×150 / `_s`=154×78 |
| `tools/_report_recipe_book.md` | 本报告 |

## 2. 校验结果

- `python tools/build_wiki.py` → **0 报错**，`✅ manifest.js 已生成：13 个板块，共 63754 条`（本板未登记 policy，按指示由主代理登记；登记后自然进入 manifest）。
- 对 `recipe_book.json` 单独跑严格门禁 `publication_policy.publication_contract_errors(board, strict_v2=True)` → **0 条**；
  `build_wiki.check_board()` → **0 条**。
- 571/571 条目具备 `id/name/evidence/evidence_level/status_tags/provenance`，provenance 8 个必需键齐全，`source_lock_sha256` 全为 64 位 hex。

## 3. 已知问题 (1)：item_ids 的 jump 组——已修并验证

旧实现 `group_ints()` 的问题：只认 `blob[j]==0x27`、跳过 kind 字节后**把下一字节直接当 count**（未按 uleb 读）、`limit=16` 静默截断、且从未与成品道具表对照。

现改为库函数 `toolkit_core.bindict_table.resolve_jump_group(blob, target)`（基准 `blob = body[8+4*count:]`，与解码器一致）：

- **571/571 行精确命中 0x27 组起点**（近邻兜底 0 行，未解析 0 行）。
- 每行解出 **6 个 id**，即同一道菜的 6 个品阶：例 `烤肉 → 77001/77101/77201/77301/77401/77501`、`果酱 → 77002…77502`。
- 与 `edible_item_data` 对照：**570 行找到成品道具行**（第 1 个命中的 id 作为 `dish_item_id`），
  名称一致性 **556/570**；14 例差异是 `食谱：XX`（全角冒号）与 `XX`，或 `苏眉鱼→烤苏眉鱼`、`火鼠鱼料理→火鼠鱼菜肴` 这类“食谱名 ≠ 成品名”，已在卡面同时保留 `name` 与 `dish_name`，不做合并。
- 571 行中成品行覆盖到的品阶数：6 档 273 行 / 5 档 158 / 4 档 136 / 3 档 1 / 2 档 2（未覆盖的档位在 `edible_item_data` 里没有行，不是解析失败）。

## 4. 已知问题 (2)：food_materials 的 0x16 组——已解出结构，语义部分未定证

字节形态（烤肉，行 101201）：`16 01 2a | 61 11 01 | 60 11 01 | 5f 11 01 | …`
解析规则（与行值编解码器的标量语义一致）：

```
16 <key_kind=01 uleb> <count>
count × ( key: key_kind      # 材料 type_id，uleb
          value: <tag><uleb> # tag 0x11=zigzag、0x01/0x04=uleb
        )
```
烤肉该组正好占 3 + 42×3 = 129 B，结束位置 = 下一组 `27 01 06`（item_ids）起点，边界自洽。

统计（571 行）：

| 项 | 数 |
|---|---|
| `food_materials` 字段缺失（字段本就不在该行） | 360 |
| 0x16 组解出 | **210 行 / 15,763 条 (type_id, 数量)** |
| 其中数量 = -1（zigzag） | 15,335 |
| 其中数量为正数 1–3 | 428 |
| jump 目标不是 0x16（指向 0x36 映射行，行 101244 不可描述的食物） | 1 |
| 解析错误 | 0 |

**能确认的**：`(type_id, 数量)` 已按上述结构解出并逐条落在 `items[].materials`（`[[type_id, 数量], …]`，原值不动）；
`type_id` 空间 1–153，本板出现 130 个。

**未定证的（不在板上装作已知）**：

1. 数量 -1 的语义（不限量 / 默认 1 / 排除项）在配置层没有字段名或注释可证，故**不做折算**，也不改写成“数量 1”。
2. 正值条目每行 1–4 条（210 行中：1 条 54 行、2 条 101 行、3 条 48 行、4 条 7 行），形态与“烹饪需 1–4 种材料”吻合，因此单列 `materials_positive` 供卡面用；**但不把它命名为“必需材料”**，避免过度断义。
   典型正值样例：`果汁 [(3,2),(8,2)]`、`蜂糖水 [(8,3)]`、`烤肉 [(1,2)]`、`芝麻元宵 [(28,2)]`。
3. 负值条目不是全局共用集合（210 行里有 192 个不同的负值集合），所以既不是“全体材料表”，也不能当“排除表”直接用。
4. `type_id → 材料道具 id/名称` 未并入：同源表 `food_material_data.slot_0` 取值 1–153、疑似就是该类型编号，但语义未证，按 `no-cross-source-field-join` 不并入本板（已写进 `meta.notes` 与 `meta.material_stats`）。

## 5. 图标链路（严格按 路径 → fid → pe_index(包,行) → 解码）

`edible_item_data[row].icon` → `fid_of(icon + "_b"|"_s" + ".ktx")` → `pe_index.sqlite3.rows(fid)` → `(pack,row)`
→ 读 `pe_packs/<pack>` 行表、seek 到 `block_base + off`、校验行内 20 B 头 `(packed, decoded, flag)` → zstd/lz4 解压 → KTX/DDS/PNG → RGBA PNG。

- 有图 **299 / 571**（`evidence_level = physical-resource-chain`），写出 **294 张** PNG，`row_missing / header_mismatch / read_error / decode_error / bad_rgba` **全 0**。
- 抽检视觉核对：`icon_77001_b`=煎肉排、`icon_77005_s`=一杯水（热水）、`icon_77003_b`=烤蔬菜串（蒸烤蔬菜），与菜名吻合；同一批图标在包内行号连续（0003.gpk 2253/2255/2256…），说明 fid 命中不是撞号。
- 未下发 **271 条**：`icon` 字段有值但 `icon_770xx_b/_s.ktx` 在 pe_index（174 个安卓热更包）**无任何命中**；抽检 `icon_77038/77014/77015/77018/77019/77039` 在客户端 `gpk_loc0`（1,805,102 条）同样无命中 ⇒ 按“未下发”记录，**没有用任何替代图**。
- 另 1 条 `人参果`(101937) 的成品 id `200469…205469` 在 `edible_item_data` 里没有行 ⇒ `icon_state = 无成品道具行`（不是未下发，是取不到图标路径）。该条未做跨表取图。

## 6. 契约与来源

- `meta.provenance`：`contract_version=3`、`contract=frozen-audited-artifact`、`audit_status=passed`、
  `source_scope{ no-cross-source-field-join / no-equal-integer-join / unknown-unless-runtime-proven }`。
- `source_locks`：`cook-recipe-data`（role=primary，sha256/bytes/mtime_ns 均为文件实测）+ `edible-item-data`（role=comparison，实测 sha256）。
- 每条 item：`locator_chain.chain_status=replayed-structural`、`scope=record`、`no_cross_source_field_join=true`，
  step = `{kind:'decoded-table-row', source_id, table, row_key, field_refs}`；`upstream.package_sha256` = 上游 npk sha256。
- 成品道具行（名称/图标/等级）单独放在 `items[].dish` 并在 `_note` 里声明“不与食谱行做字段级合并”，不参与该 item 的 locator step。

## 7. 复现

```bash
cd E:/la拆包项目/04_站点/web
E:/la拆包项目/.venv/Scripts/python.exe tools/build_recipe_board.py   # ~3.2 s（294 张 PNG 全解）
E:/la拆包项目/.venv/Scripts/python.exe tools/build_wiki.py           # 0 报错
```

## 8. 未做 / 留给下一步

- `data/publication_policy.json` 与本板 category 的登记：按指示未改，由主代理登记（登记后跑一次 build_wiki 即进 manifest）。
- 材料 `type_id → 材料名` 的映射（`food_material_data` / `food_material_ids_by_type` 两张表的 0x73/变体布局尚未定证）：一旦定证可回填，`items[].materials` 结构不用改。
- 271 条未下发图标：如需补图，只能在服务端/后续版本包出现后重跑本脚本（脚本会按 fid 自动补）。
