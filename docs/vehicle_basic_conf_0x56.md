# vehicle_basic_conf 索引变体分析（2026-10-22）

## 现象

`decode_table_rows` 报：

```
not a supported 0x76 index tail: 56055163
```

## 已确认的结构

```
表体            3,155 B
count(u32)      83
reserved(u32)   0
blob            2,815 B
blob[0:4]       1728  （de）
tail            blob[1728:]  1,087 B
tail 前 12 字节 56 05 51 63 72 de 02 58 09 00 00 45
```

## 已经排除的解释

1. **不是 0x76 换个字节**
   把 `tail[0]` 从 `0x56` 改成 `0x76` 后仍失败：
   `index bucket count unreadable or offsets out of range`。

2. **不是 0x76 的布局平移**
   逐组穷举 `start(0..15) × stride(6/8/12/16) × 偏移字段(0/4)`，
   共 1,000+ 组合，**没有任何一组能让 4 字节值命中 0x86/0x96 行头**。

3. **行不在 tail 前段**
   tail 内确实有 **81 个** 8 字节步长的 4 字节值落在 `[de, blob_len)` 区间
   （`tail+7, +15, +23 …`），但它们指向的字节是 `0x49 0x29 0x22 0x45 0x46 0x1c`，
   不是行标记；值差也无规律（348, -32, -301, -3 …），说明这不是「键 → 行偏移」索引。

4. **直接扫行标记不可行**
   `blob` 里 `0x86` 出现在 218/268/600/732/746 等位置，
   `decode_86_row` 在这些位置分别报 `0x96 不是 0x86` / `unhandled scalar type 0xc0` /
   `index out of range` —— 说明这些字节是值流里的巧合，不是行头。

## 结论

`0x56` 是**另一种容器族**，不是 `0x76` 的变体。要解它需要：

```
① 先确定它有没有行键（现在连 key 的位置都没定下来）
② 定位值流的起点与每行边界
③ 用 _schema_at 反推字段结构，再和 board 里的 125 条逐条比对
```

在新族结构确认前，**不补 vehicle_catalog 的 provenance**（补了就是编）。

## 影响面

- `vehicle_catalog` 125 条仍是 source 文本级证据，无机读定位链
- 同类 `0x56` 表若还有，后续会同样报错；可在 `parse_index` 里先抛更明确的异常
  （例如「未知索引族 0x56」），便于以后一次性归类
