# cdata「裸块行」容器格式破解报告

日期：2026-11-01 · 仓库：`E:/la拆包项目` · 目标目录：`01_索引与产物/41_还原树/pe/配置/com/cdata/`

> 结论一句话：**破解成功**。这批"解不出来"的表并不是加密容器，而是 **bindict 表的第三种行编码**——行不是 schema 行（0x96/0xd6/c6/0x36），而是「裸块链」（`27`/`07`/`36`/`86`），且映射表干脆没有行区（`de == 4`，索引值本身就是字面量）。

---

## 1. 格式（逐字节，全部实测自证）

### 1.1 容器层（与已有结论一致，非新东西）

```
文件 = 0x73 code object
  0x00      73
  0x01..14  5×u32  (argcount, posonly, kwonly, stacksize, flags)
  0x15      fb + u32(co_code len) + co_code
  ...
  偏移 264  7b + u32(67055) + payload      ← 表体 bytes 常量
```

★ **更正一处既有误判**：`raw.find(b'x{') == 263` 是**巧合**。263 的 `78` 是另一个 marshal 标签，
真正的 bytes 常量头是 **264 的 `7b` + 265 的 u32 长度**；表体起点 = **269 = 264+5**。
两者算出来的 body 起点相同（263+6 == 264+5），所以不影响取数，但不要把它当"x{ 标记"。

### 1.2 payload 层（三种头变体，同一套 blob）

```
payload = [u32 N][u32 0][N×u32 ends][blob]
  N = 字面量池槽位数。
    N == 0  → 没有 ends 表、没有自带池，blob 直接从 offset 8 开始   ← 5 张映射表全在此族
    N >  0  → standard 头：blob 从 8+4N 开始（ends 实测全 0）
  ★ 变体 B（自带池）：[u32 N][u32 0][N×u32 ends][字符串区][blob]
    判定：8+4N+ends[-1] 处能解出「de + 0x76 索引尾」即成立。
    实测：monster_horde_model_data（池 259 条）、sync_socket_model_anim_data（池 3351 条）
```

### 1.3 blob 层

```
blob = [u32 de][行区 4..de][索引尾 @de]
索引尾 = 76 kt vt
         + uleb(bucket_count)                    ← 是 uleb，不是 u8
         + bucket_count × 8B  (u32 hash 升序, u32 node_off)
         + node 区：连续 (uleb key, uleb value)，恰好铺到 blob 末尾
自证三条（本批 45 张全过）：
  ① hash 严格升序且唯一
  ② 桶偏移唯一，且 min(node_off) == 桶表末尾（节点区紧贴桶表，无 padding）
  ③ 从 min(node_off) 顺序解 (uleb,uleb) 恰好得到 bucket_count 对、且正好吃到 blob 末尾
```

★ **`value` 的含义由 `vt`（索引尾第 3 字节）决定 —— 这是之前 0 行的直接原因**：

| vt | 含义 | 出现在 |
|---|---|---|
| `0x01` | 字面整数（就是映射目标 id） | appear_id_2_fashion_id / appear_id_2_equip_id / new_appear_id_2_appear_id / pet_appear_suit_map / jk_adapt_suit_str_map … |
| `0x05` | 字面池索引 | fashion_charm_desc_data / zx_fashion_id_2_fashion_str / super_fashion_change_color_part2_data |
| `0x0b` | 行区偏移（原语义） | armors_to_appears_data / appear_id_to_action_id / 以及所有带行区的表 |

### 1.4 行区（新编码）

行 = `span[row_start, 下一个 row_start)`，内容是若干**块**串联：

```
27 <elem_type> <uleb n> n×值                同构列表   elem_type ∈ {01,0b,05,11,12,22,03}
07 <uleb n> n×(类型字节, 值)                 异构元组
36 <kt> <vt> <uleb n> n×(k,v)               内联映射
86 <uleb schema_ref> <内联 bitmap (bits+7)//8 字节> <值流>
06 <uleb n=0>                               空组
```

★ 关键修正：`86` 是**内联位图**的嵌套行（`86 + schema_ref + bitmap + 值流`），
和 `bindict_table.decode_86_row`（`86 + schema_ref + bitmap_ref + bitmap`，共享位图）**不是同一种**。
按共享位图解会得到 `schema=383 / bitmap=1d` 这种离谱值；按内联位图解，`fashion_set_data` 6/6 行、
`fashion_card_fashion_data` 14/14 行一次铺满（后者直接解出中文名"时光童话"）。

### 1.5 为什么 `decode_table_rows` 返回 0 行（根因）

`decode_table_rows` 只认 `ROW_MARKERS = (0x96, 0xd6, 0xc6)` + `0x36`。这批表的行头是 `27/07/86`，
所以 `known_schemas` 为空 → 直接返回 `[{"error": "no schemas discovered"}]`。
另外 `_chs.py` 里 10 字节常量是空池，`parse_legacy_chs_pool` 找不到 `{ CHS` 报错**是正常的**——
这批表 `count == 0`，本来就没有池（字段名/文案全无）。

---

## 2. 五张映射表（实跑结果）

| 表 | 行数 | 唯一行区 | kt/vt | 模式 | 结构自证 |
|---|---|---|---|---|---|
| `appear_id_2_fashion_id` | **4560** | 4560 | 01 / **01** | 字面值（无行区，de=4） | 节点区 4560 对铺满；hash 升序；min(off)==桶尾 |
| `appear_id_2_equip_id` | **543** | 543 | 01 / **01** | 字面值（de=4） | 同上 |
| `armors_to_appears_data` | **320** | 255 | 01 / **0b** | 行区 4..2468 | 255 行从 4 顺序铺到 de=2468，一字节不剩 |
| `appear_id_to_action_id` | **1510** | 598 | 01 / **0b** | 行区 4..2979 | 598 行铺满 de=2979 |
| `appear_trade_ids` | **0（无表体）** | — | — | — | 542 B 模块，常量 `const[0] = 135576`（数据长度占位），载荷不在文件里，也无 `.nxs` |

前 3 行（按 key 升序）：

```
appear_id_2_fashion_id : 10120 → 166001 ; 10150 → 166002 ; 10170 → 166003
                         末两条 1337360201 → 637360230 ; 1430450303 → 476320
appear_id_2_equip_id   : 10010 → 32528  ; 10011 → 32529  ; 10012 → 32530
armors_to_appears_data : 30001 → [30050, 130090] ; 30002 → [30052, 130092] ; 30003 → [30051, 130091]
                         另有 270154 → [5016401, 15016401]（男/女版：15016401 == "1"+5016401）
appear_id_to_action_id : 11155 → [32163] ; 11156 → [32164] ; 30320 → [15]
```

### 2.1 自证（必须的交叉验证，全部实跑）

| 表 | key 命中 `player_appear_data`(5604 行) | 值命中 `fashion_data`(11169 行) | 其它 |
|---|---|---|---|
| `appear_id_2_fashion_id` | **4499 / 4560** | **2257 / 2280（唯一值）** | 值命中 appear 0/2280（方向正确，不是反的） |
| `appear_id_2_equip_id` | **543 / 543** | 0 / 273（本来就是 equip id） | 与 `armors_to_appears_data` 互证 **501 / 543** 对 |
| `armors_to_appears_data` | 21 / 320（key 是护甲 id） | — | 值命中 `player_appear_data` **501 / 501** |
| `appear_id_to_action_id` | **1445 / 1510** | — | 值 601 个（动作 id 段） |

> 未命中的 61 个 key 全是 10 位数（`1337250201` 这种），不在 `player_appear_data` 里；
> 未命中的 23 个值全是 `1330000-1330010` / `637360110…` / `650040230` 这类无对应行的 id。

---

## 3. 批量验证：74 张（不是 60）

筛选条件：文件名含 `fashion/appear/suit/model/skin`（排除 `_chs`），共 **319 张**；
legacy 路径（`body = raw[at+6:at+6+L]` + `decode_table_rows`）**245 张正常、74 张失败**。

74 张的最终归类（全部实跑）：

| 归类 | 张数 | 说明 |
|---|---|---|
| **完全解出** | **45** | 43 张走新格式（行区铺满 + 全部块可解）；1 张 `0x56` 族（`weapon_skin_special_nucleus_res_data`，1 行 47 字段）；1 张池+blob 族（`monster_horde_model_data`，80 行，自带 259 条字符串池） |
| 部分解出 | 3 | `do_face_default_appears_data`(2 行) / `village_appear_texture_mapping_data`(22 行) / `weapon_skin_sound_mutual_exclusion_data`(35 行)：行边界已自证，但行内有 `0x16`/`0x1b` 未知块 |
| **空表（声明长度 0，真 0 行）** | 13 | `cat_appear_data` `fashion_item_spine_data` `model_data`(拆分表，转 `model_data_base`) `only_fashion_hd_tag_conf` `nt_super_fashion_gift_data/_index_data` `spec_fashion_voucher_data` `zx_fashion_id_2_hd_id` `camp_style_model_tree_scale_data` `levin_dungeon_fixed_appear_day` `fashion_charm_magazine_time_data` `scene_model_break_conf_data` `scene_model_break_export_data` |
| **载荷缺失** | 9 | `const[0]` 是声明长度但文件里没有数据：`appear_trade_ids`(135576) `change_color_fashion_ids`(366758) `eu_appear_id_convert_data`(30370) `fashion_buff_id_set`(13274) `fashion_sfx_buff_id_set`(20001) `weapon_skin_accessory_items`(1140001) `weapon_skin_blacklist_conf_data`(10003) `weapon_skin_replace_mf_set`(795) `fashion_charm_version_data`(7) |
| 仍未解 | 4 | `sync_socket_model_anim_data`（池+blob 已定位，1111 个节点，行块首字节 `0x04` 不在已知块集合）；`fashion_charm_period_data` / `store_daily_recommended_fashion_timestamps` / `weapon_skin_idle_anim_data`（0x73 模块顶层 code 解析失败，常量里既无二进制表体也无 `TD(...)` 行，`script_table_replay` 亦 0 行） |

**成功率：45/74 = 60.8% 完全解出；48/74 = 64.9% 至少解出内容。**
若把 22 张"物理上没数据"的排掉，则 **45/52 = 86.5%**。

完全解出的 45 张（名称 → 行数，逐张实跑）：

```
appear_id_2_fashion_id 4560            appear_id_2_equip_id 543
appear_id_to_action_id 1510            armors_to_appears_data 320
new_appear_id_2_appear_id 1794         pet_appear_suit_map 1319
monster_model_name_to_id_data 1648     monster_appear_params_to_id_data 392
fashion_charm_magazine_comment_data 1096   plate_id_2_fashion_ids 625
fashion_model_id_2_plate_id 153        jk_adapt_suit_str_map 102
fashion_card_fashion_data 14           fashion_collect_group_data 14
fashion_set_data 6                     fashion_id_2_season_id 4
fashion_charm_magazine_conf_data 6     fashion_charm_desc_data 1
fashion_preset_do_face_item_key_data 10   fashion_preset_do_face_key_data 38
brand_fashion_data 2                   super_fashion_gift_index_data 4
super_fashion_change_color_part_data 3 / _part2_data 11 / _unlock_data 3 / _fx_data 7
skin_2_sfx_function_map 82             skin_function_item_id_to_anim_name 47
skin_replace_anims_dict 39             skin_auto_gen_nucleus_knife_light_data 20
store_user_portrait_fashion_2_user_data 60   store_v2_fashion_type_data 5
ship_fashion_camera_data 6             ship_model_map_with_different_level 8
player_overload_same_appears_data 2    team_art_model_config_data 1
coldarm_type_to_skin_item_data 3       weapon_kind_to_skin_item_data 10
weapon_skin_cold_combo_data 2          weapon_skin_coldarm_knife_light_data 20
weapon_skin_effect_show_data 65        weapon_skin_sfx_display_order_data 1
zx_fashion_id_2_fashion_str 2          monster_horde_model_data 80（池+blob 族）
weapon_skin_special_nucleus_res_data 1（0x56 族）
```
（共 45 项：上列 43 张新格式 + 上述 2 张其他族）

---

## 4. `appear_id_2_fashion_id` 提供新映射吗？——**不提供，是冗余索引**

反推基准（实跑）：`fashion_data` 11169 行，`appear_ids` 字段 11169/11169 都是 `0x0b` 帧、
`read_27_group` **kind=0x01、11169/11169 全解**（基址 = blob 起点，即 `body[8+4*20162:]`）→
**4538 个 appear id / 22338 条 (appear, fashion) 对**（一个 appear 可对应多个 fashion）。

| 指标 | 数值 |
|---|---|
| 表行数 | **4560** |
| 反推 appear id 数 | **4538** |
| 反推 (appear,fashion) 对数 | **22338** |
| key 交集 | **4520** |
| 表中 (appear,fashion) 对落在反推里 | **4514 / 4560**（98.99% 可直接反推） |
| **表独有 appear key** | **40**（其中 **39 个真实存在于 `player_appear_data`**） |
| 表独有 (appear,fashion) 对 | 46 |
| 反推独有 appear key | 18（`11085-11088`、`31085-31088`、`40190`、`111085-111088`、`131085-131088`、`140190`） |

多出来的 40 个 key（示例 5 条，`fashion` 一列是否在 `fashion_data` 里存在）：

| appear | fashion | fashion 在 fashion_data? | 说明 |
|---|---|---|---|
| 70892 | 1330000 | **否**（0/40 全不存在） | 1330000-1330010 是染色/预设段，无时装行 |
| 70893 | 1330001 | **否** | 同上 |
| 1337360201 | 637360230 | **否** | 637360xxx 整段在 fashion_data 无行 |
| 1373401 | 1330000 | **否** | |
| 1373201 | 637320110 | **否**（反推给的是 637320111-116） | 表指向"基板"110，fashion_data 只登记 111-116 派生款 |

还有 6 条"同 key 不同值"，全部是同一现象：表给 `…110`（基板/基础配色），
反推给 `…111..116`（实际登记的派生款）：

```
1373201  → 637320110   (反推: 637320111..116)
3373201  → 637320130   (反推: 637320131..136)
3375201  → 637520130   (反推: 637520131..136)
11373201 → 637320110 ; 13373201 → 637320130 ; 13375201 → 637520130
```

**判定：冗余索引，且比反推更"窄"。** 它给的是「appear → 唯一那个 fashion」的 1:1 视图，
反推是 1:N（22338 对）；表里 98.99% 的对都能从 `fashion_data.appear_ids` 反推出来，
唯一"新增"的 40 条**全部指向 `fashion_data` 里不存在的行**（悬空），拿不到任何新时装。
若要用它，唯一价值是当「appear → 基板 fashion id」的快捷索引（省一次反查），不是新信息。

---

## 5. 时装域：板上还没用到的表

板上 `fashion_wardrobe.json`（3152 卡）实际只吃：`fashion_data`(+chs)、`player_appear_data`(+chs)、
`player_module_appear_data`、`body_sfx_data`、`fashion_preset_do_face_config_data`、`do_face_v4_preset_data`、
`buff_data`、`common_item`、`follow_charm_conf_data`、`all_equips_data`、`simple_fashion_data`。

（注意：`grep` 到 `local_restore_tree.json` 里出现的表名只是全量清单，不算"被板上使用"。）

下面 5 条按价值排序，全部是本次实跑解出的：

| 表 | 里面有什么（实测） | 对时装图鉴的价值 |
|---|---|---|
| `fashion_model_change_color_data`（623 行，legacy 可解） | `fashion_model_id` + `plate_name`（如"桃粉"）+ `max_scheme` / `level` / `dye_num` / `saturation_range` / `value_range` / `preset_color_ids` | **最高**。染色方案名+可染段位，直接能给每张时装卡补"配色/染色"分组 |
| `plate_id_2_fashion_ids`（625）+ `fashion_model_id_2_plate_id`（153） | 版型→时装 id 列表；model→版型列表（实测 `31686 → [570203,570050,…] 8 个`；`570652 → [637340130]`） | **高**。正是"同一 model 的多个派生款（637320110/111…）"的父子关系，能解决第 4 节那 6 条基板悬空映射，也是合并重复图鉴卡的依据 |
| `appear_change_color_data`（705 行，legacy 可解） | `colors` / `color_values` / `change_color_switch`（jump 组） | **高**。外观维度实际可用颜色集，和上一条配合能出"每款可染哪几种" |
| `fashion_collect_group_data`（14 行，本次新解） | 收集组：图标路径（`ui/zhutihuodong…/icon_hua.png`）、起止时间、组内时装 id 列表、`向光生长` 之类组名 | **中高**。图鉴"系列/收集组"分组与封面图，板上现在没有系列维度 |
| `fashion_review_score_data`（1526 行，legacy 可解） | 每行 `styles`（jump 组）——评分配置 | **中**。若要做"评分/口碑"排序可用，但要先展开 `styles` 组确认字段 |
| 备选：`fashion_card_fashion_data`(14) / `fashion_set_data`(6) / `brand_fashion_data`(2) / `pet_appear_suit_map`(1319) / `new_appear_id_2_appear_id`(1794) / `appear_id_to_action_id`(1510) / `armors_to_appears_data`(320) / `fashion_charm_magazine_comment_data`(1096，含"守夜人一号/来自小红书"等中文评论) | 时装卡、整套、品牌系列、宠物外观套装、新旧外观 id、外观→展示动作、护甲→外观(男/女)、杂志评论 | 时装卡/整套/品牌可做图鉴分区；`appear_id_to_action_id` 能给卡配"预览动作"；`appear_id_2_equip_id` 正是板上 meta 里写明"尚未解开"的那张，现在可解（543 条） |

---

## 6. 可复用解码函数建议（**未改** `toolkit_core`，只给建议）

建议在 `toolkit_core/bindict_table.py` 新增 `decode_block_row`，并在 `decode_table_rows` 里加一条
"没有 schema 行时不要直接返回 `no schemas discovered`，先试裸块行"的分支（不改默认行为：

```python
NEW_ROW_MARKERS = (0x27, 0x07, 0x86, 0x06)   # 0x36 已有

def read_block_row(blob, pos, end, pool):
    """解一行裸块链：27/07/36/86/06 串联，必须恰好吃到 end。返回 (blocks, q, err)"""
    blocks, q = [], pos
    while q < end:
        m = blob[q]
        if m == 0x27:
            et = blob[q+1]; n, r = uleb(blob, q+2, end)
            vals = []
            for _ in range(n):
                v, r = _decode_value(blob, r, et, pool); vals.append(v)
            blocks.append(("27", n, vals)); q = r
        elif m == 0x07:
            n, r = uleb(blob, q+1, end); vals = []
            for _ in range(n):
                t = blob[r]; v, r = _decode_value(blob, r+1, t, pool); vals.append(v)
            blocks.append(("07", n, vals)); q = r
        elif m == 0x86:                      # ★ 内联位图，不是 decode_86_row 的共享位图
            ref, r = uleb(blob, q+1, end)
            n, r = uleb(blob, ref, end); bits, r2 = uleb(blob, r, end)
            fields = []
            for _ in range(n):
                _slot, r2 = uleb(blob, r2, end); fields.append(blob[r2]); r2 += 1
            bsz = (bits + 7) // 8; bm = blob[r:r+bsz]; r += bsz
            vals = []
            for i, t in enumerate(fields):
                if i < bits and not (bm[i//8] >> (i % 8)) & 1: continue
                v, r = _decode_value(blob, r, t, pool); vals.append(v)
            blocks.append(("86", ref, vals)); q = r
        elif m == 0x36:                      # 复用既有 0x36 逻辑
            ...
        elif m == 0x06:
            n, r = uleb(blob, q+1, end); blocks.append(("06", n, [])); q = r
        else:
            return blocks, q, "unknown block 0x%02x @%d" % (m, q)
    return blocks, q, None
```

配套两条索引侧规则（否则仍会 0 行）：

```python
# 1) 头：N == 0 时 blob = body[8:]（不需要 ends 表）；N > 0 时 blob = body[8+4*N:]
# 2) 索引尾 value 语义看 vt：
#      vt == 0x01 -> 字面整数（映射目标就是它，de 通常 == 4，无行区）
#      vt == 0x05 -> 字面池索引
#      vt == 0x0b -> 行区偏移，去 read_block_row
# 3) 变体 B（自带池）：8+4N+ends[-1] 之后还有 blob，池用 ends 自行切
```

建议同时把 `bindict_73.decode_73_table` 的 `_looks_like_body` 放宽：现在它要求
`data[de] == 0x76 且 kt∈{01,05}、vt∈{01,0b}`，本批 `vt=0x11`（sync_socket）会被挡掉。

---

## 7. 被否证的假设（避免重复踩）

1. ~~`cnt` 在 0 但行表在 `8+4*cnt` 之外~~ → 不成立。`cnt=0` 就是"没有 ends 表也没有池"，
   行表就在 `body[8:]`；`decode_table_rows` 的 `table_end = 8 + 4*count` 其实算对了，错的是行编码。
2. ~~这批表用 0x7B 索引~~ → 不成立。索引尾首字节是 `0x76`，位置在 blob 内 `de` 处，
   和普通表完全一样；bucket_count 是 **uleb**（4560 = `d0 23`），读成 u8 会得到 208 个桶。
3. ~~chs 池是新格式 0x75 大常量表~~ → 不成立。这批表 `count=0`、本来无池；
   `_chs.py` 里只有一个 10 字节空常量 + 一个 8 字节全零常量，`parse_legacy_chs_pool` 报错是预期行为，
   不要为了让它不报错去改池解析。
4. ~~`at=263` 的 `x{` 是表体起点~~ → 巧合，见 1.1。
5. ~~0x86 是"共享位图嵌套行"~~ → 本批是**内联位图**（`86 + schema_ref + bitmap + 值流`）。
   按共享位图解会得到 `schema=383 / bitmap=1d` 之类离谱值，且 `value_end` 对不上下一个行起点。

## 8. 遗留

- `sync_socket_model_anim_data`（1111 节点）行块首字节为 `0x04`，未识别；
  布局（3351 条池 + blob）已定位，只差块语义。
- `fashion_charm_period_data` / `store_daily_recommended_fashion_timestamps` / `weapon_skin_idle_anim_data`
  三张 0x73 模块内没有数据（顶层 code 解析失败或常量无行），`script_table_replay` 也是 0 行。
- `appear_trade_ids` 等 9 张：载荷物理缺失，只有长度占位，除非从热更包再取一次否则不可解。
- 本报告所有数字均来自实跑；临时脚本已删除，只保留本文件。
