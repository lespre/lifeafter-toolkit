# 0x56 容器族：已解（2026-10-22）

## 一句话

`0x56` = 哈希键控的**单行字段字典**，不是「83 行表」。`body[0:4]` 是**字段数**，不是行数。

## 结构（PE pe_20261020 实测，142 张表同族）

```
body = [u32 field_count][u32 0][field_count x u32 名字池 ends]
blob = body[8 + 4*field_count :]
blob[0:4] = u32 de              # 索引起点（相对 blob）
tail = blob[de:]
tail = 56 05 <u8 n>             # marker, key_type=0x05, 字段条数
       n x (u32 字段名 hash, u32 字段值三元组偏移)
行区 = tail[3 + 8n :]           # 每个有值字段一个三元组
三元组 = [uleb field_idx][u8 type][value]
字段名 = chs_pool[field_idx]
```

type 映射：

```
0x01 uleb 整数     0x03 bool      0x05 CHS 池字符串
0x0B uleb 偏移跳转  0x12 f32       0x22 f64
```

## 验证

```
vehicle_basic_conf   字段 83、记录 81（hit_01/hit_02 缺省）、三元组 81/81
                     抽样：winch_link_dist=200、throw_off_damage_max_pct=50.0、
                           max_speed=250、max_gasoline=5000、roll_limit_in_air=±15°
nucleus_conf         字段 8、记录 8、三元组 8/8（无 _chs 池，字段名不可得）
同族扫描              com/cdata 下 142 张 blob[de]==0x56，解析器 141/142 通过
                     唯一例外 upload_files_info_other.py（0xc9 未知 tag）
```

## native 侧印证

客户端 `bindict` 扩展模块（`PyInit_bindict` @0x1b3bd5c）：

```
bindict.parse(bindict_buf) @0x1b3fe18  -> base + u32[base] 取 de
sub_1b2f424                            -> 容器分派：0x56/0x66/0x76/0x36/0x96/0xC6/0xD6
                                          0x56 = 只有 key_type 一字节
                                          0x76 = key_type + value_type 两字节
                                          tag >= 0x40：哈希体（8B (hash, rel) 对）
                                          tag <  0x40：0x36 顺序对
```

结论：`0x56` 与 `0x76` 由同一函数处理，差别只是类型字节个数、count 起点前移 1 字节。

## 对 wiki 的影响

- `vehicle_basic_conf` 是**全局物理/上限参数**（单行），不是车辆名册。
- 每辆车 + 中文名在 `vehicle_ui_data`（0x76，277 行）。
- `vehicle_catalog` 已改用 `vehicle_ui_data` 补 provenance：82/125 命中；
  剩 43 条只有型号代号、无中文名（标 `table-absent`）。

## 代码位置

```
00_规范与工具/工具/工具库/00_共享核心/toolkit_core/bindict_hash_index.py   索引族结构解析（0x56/0x66/0x76）
00_规范与工具/工具/工具库/00_共享核心/toolkit_core/bindict_56.py            0x56 单行字段字典解析
02_wiki/web/tools/backfill_vehicle.py                            vehicle_catalog 回填
```
