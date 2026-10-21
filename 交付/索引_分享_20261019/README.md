# 明日之后 资源索引（PE 测试服 + PC 测试服）

## 内容

| 文件 | 说明 |
|---|---|
| `index.html` | 单文件离线查询页，双击打开就能搜（PE 图标行 + PC 全量 + npk 图库 + 板块目录） |
| `pe_paths.csv.gz` | PE 侧全部**有名字**的资源：1261348 行，字段 `path,pack,row` |
| `pc_paths.csv.gz` | PC 侧已标定路径：135619 行，字段 `path,pack,row` |
| `npk_icons.csv` | item_icon npk 图库：22114 条，字段 `npk_id,width,height,dhash` |
| `boards.csv` | 图鉴板块目录（板块 id / 名称 / 分类 / 条目数 / 图片数） |

## 路径 → 资源的口径

资源查找靠 64 位 fid（murmur3-64，与路径字符串一一对应）：

```python
fid = murmur3_x86_32(path, 0x77777777) << 32 | murmur3_x86_32(path, 0x66666666)
```

同一个资源在两个客户端的路径差异只有扩展名：

| 客户端 | 落盘扩展名 |
|---|---|
| PE（安卓测试服） | `.ktx`（DDS 内容） |
| PC（PC 测试服） | `.bc7`（BC7 DDS），另有 `.png` `.jpg` `.atlas` `.json` |

所以拿到一个路径，把扩展名换掉就能在另一侧找同一个文件。

## 覆盖率（实测，按图鉴全部引用路径算）

```
PE  3,720 / 3,843 = 96.80%
PC  3,696 / 3,853 = 95.93%
```

缺口原因：新一期时装图标只在单侧下发（如 `icon_bag_f_3317001` 连 PC 文件名清单都没有）；核芯特技图标两边命名体系不同（PE `other_icon/jinghejineng/icon_X`，PC `font_icon/icon_new/icon_X_new`）。

## 用法示例

```bash
# 查某个图标在哪
zcat pe_paths.csv.gz | grep 'icon_b_m_3399001_b'

# 输出：ui/item_icon/icon_b_m_3399001_b.ktx,0003.gpk,4364
```

`pack` 是资源包名（如 `0003.gpk`），`row` 是该包内的行号；按行号即可解码出图（DDS/BC7 + zstd）。

## 数据版本

- PE：测试服 2026-10-16 构建，174 个包 / 1,801,666 行，其中 1,261,348 行已恢复名字
- PC：测试服 2026-09-25 基础包（`ui_01~05`）+ 2026-10-15/17 热更包（`Documents/gres`）
- npk：`item_icon.layers.1.257.npk`，22,114 张图标，尺寸 300×152 / 156×80 / 600×300 / 116×116
