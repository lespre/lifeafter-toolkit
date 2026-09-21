# 武器皮肤表定位（工具库 11 号）

## 目标

重建《武器皮肤全量表》（v5 格式）：`skin_id / 名字 / 名字来源 / model_path / 版本状态 / 品级 / 品级名 / 武器类型 / 武器类型名 / 特效描述`。

## 数据源与 join 链

```text
weapon_skin_data（125 行，py314 entry 11762+21081）
├─ skin_id（key 1110001~1110xxx）
├─ model_path（weapon/skin/skin_XXXX_YYY.gim）
├─ level（品级 1-6）/ weapon_type（武器类型编码）
└─ 其他：link_nucleus / sale_ts / charm_value / obtain_limit / priority

common_item_data（道具表，py3.npk 34,949 行）
└─ **id == skin_id 直接 join**（皮肤道具的 item_id 与 skin_id 同号）
   ├─ name  = 皮肤名（权威来源，覆盖 ~90%）
   └─ desc  = 皮肤描述（含联动 IP 标注，如「明日之后×铠甲勇士」）

weapon_skin_sfx_function_data（特效表 321 行）
└─ sfx_name → 补充道具表缺失的皮肤名（疾影枪 1110181 等 8-29 新增）
   └─ 特效路径：effect/fx/weapon/skin/skin_XXXX_YYY/*.sfx

weapon_skin_kind_data 池（20 字符串）
└─ 武器类型名映射：1=突击步枪 3=弓箭 4=霰弹枪 5=狙击枪 6=手枪
   7=榴弹炮 8=电磁机枪 20=喷火器 50=冷兵器 51=护臂/盾
```

## 关键机制（实测确认）

1. **join 键：`common_item_data.id == weapon_skin_data.key`（同号）**——鎏金锐魄 item 1110001 == skin 1110001
2. **重名陷阱处理**：道具表里"疾影枪/极光剑"等名字**可能对应家具/植物 item**（不同 id）——**必须按 id join，禁止按 name 搜**（按 name 搜会撞上"极光剑=建筑自选箱 item 240494"这类重名）
3. 极光剑(1110177)/极光盾(1110197) 不在 py3 道具表——名字需从池/人工补充（v5 已固化）
4. 品级名映射：2=品级2 3=品级3 4=品级4 5=典藏/联动 6=传世(升格)
5. 版本状态：py314 vs py3 对照（"两个版本都有" / "★8-29新增"）

## 使用

```bash
.buildenv/Scripts/python.exe 工具库/11_武器皮肤表定位/build_weapon_skin_table.py [输出CSV]
```

## 前置产物

- `E:\la拆包项目\拆包产物\weapon_skin_data_rows.json`（125 行）
- `E:\la拆包项目\拆包产物\common_item_data_rows.json`（34,949 行）
- `E:\la拆包项目\拆包产物\weapon_skin_names.json`（特效表绑定 9 个）

## 参考（历史）

- v5 全量表：`E:\la拆包项目\拆包产物\weapon_skin_full.csv`（128 行，含限时版 7/14/30 天后缀行）
- 皮肤名分级：STRONG（命中/弹道/音效后缀+已知列表）/ MEDIUM / WEAK（纯特效名）
