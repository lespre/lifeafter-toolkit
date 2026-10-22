# 明日之后 .nxs 配置表解码器 使用说明

## 概述

`nxs_config_decoder.py` 是一个可复用的 .nxs 配置表通用解码器，适用于明日之后游戏中的大型配置表文件（如物品配置、礼包配置、武器皮肤配置等）。

## 解码原理

### 核心方法
1. **直接UTF-8解码**：.nxs 配置表中的字符串数据以UTF-8编码存储，可以直接解码提取
2. **关键词搜索定位**：在原始字节中搜索关键词，快速定位相关配置
3. **上下文提取**：找到关键词位置后，提取前后指定大小的上下文
4. **正则表达式提取**：用正则表达式提取结构化数据（如武器皮肤名称、时装名称等）

### 适用文件类型
- 大型配置表（>100KB）：如 `1B249D5C9984E1B4.nxs`（900KB，物品/礼包配置表）
- 包含大量中文字符串的配置文件
- 物品名称、描述、获取方式等文本配置

### 不适用文件类型
- 小型索引文件（如 `weapon_skin_data.nxs`，9.7KB，包含编码引用）
- 纯二进制数值配置
- 加密的配置文件

## 使用方法

### 命令行使用

```bash
python nxs_config_decoder.py <nxs文件路径> [关键词1] [关键词2] ...
```

### 示例

```bash
# 基本使用（只提取字符串）
python nxs_config_decoder.py 1B249D5C9984E1B4.nxs

# 带关键词搜索
python nxs_config_decoder.py 1B249D5C9984E1B4.nxs 武器皮肤 极光剑 战神烈火剑

# 搜索铠甲勇士联动相关内容
python nxs_config_decoder.py 1B249D5C9984E1B4.nxs 铠甲勇士 刑天 飞影 帝皇侠
```

### Python API 使用

```python
from nxs_config_decoder import NxsConfigDecoder

# 创建解码器
decoder = NxsConfigDecoder('1B249D5C9984E1B4.nxs')

# 提取中文字符串
chinese_strings = decoder.extract_chinese_strings(min_length=2)
print(f"找到 {len(chinese_strings)} 个中文字符串")

# 提取ASCII字符串
ascii_strings = decoder.extract_ascii_strings(min_length=4)
print(f"找到 {len(ascii_strings)} 个ASCII字符串")

# 搜索关键词
results = decoder.search_keyword('极光剑', context_size=200)
for r in results:
    print(f"偏移{r['offset']}: {r['context'][:100]}")

# 批量搜索关键词
multi_results = decoder.search_multiple_keywords(['武器皮肤', '极光剑', '战神烈火剑'])

# 提取武器皮肤列表
weapon_skins = decoder.extract_weapon_skins()
print("武器皮肤列表:")
for skin in weapon_skins:
    print(f"  - {skin}")

# 提取时装列表
fashion_items = decoder.extract_fashion_items()
print("时装列表:")
for item in fashion_items:
    print(f"  - {item}")

# 用自定义正则表达式提取
pattern = r'打开可以获得([^：:]+)[:：]([^*]+)\*'
custom_results = decoder.extract_pattern(pattern, group_index=2)

# 获取文件信息
info = decoder.get_file_info()
print(f"文件大小: {info['file_size_human']}")
print(f"修改时间: {info['modify_time']}")

# 导出所有结果
outputs = decoder.export_results('output_dir', keywords=['武器皮肤', '极光剑'])
```

## 输出文件说明

运行后会在当前目录创建 `nxs_decoded_<文件名>/` 目录，包含：

| 文件名 | 说明 |
|---|---|
| `文件信息.json` | 文件基本信息（大小、修改时间、字符串数量等） |
| `中文字符串.txt` | 所有提取的中文字符串（带偏移位置） |
| `ASCII字符串.txt` | 所有提取的ASCII字符串（带偏移位置） |
| `关键词搜索结果.json` | 关键词搜索结果（JSON格式，含完整上下文） |
| `关键词搜索结果.txt` | 关键词搜索结果（可读文本格式） |
| `武器皮肤列表.txt` | 自动提取的武器皮肤名称列表 |
| `时装列表.txt` | 自动提取的时装名称列表 |

## 已验证的配置表

### 1B249D5C9984E1B4.nxs（物品/礼包配置表）
- **文件大小**：879.47 KB
- **内容类型**：物品配置、礼包配置、武器皮肤、时装、联动活动
- **中文字符串**：5381个
- **ASCII字符串**：8775个
- **武器皮肤**：9个（帝皇裁决、战神烈火剑、极光剑、极光盾、极狐终结刃、灵态诱导、疾影枪、重力震爆、阿赖耶识）
- **铠甲勇士联动**：刑天系列、飞影系列、帝皇系列完整配置

## 扩展功能

### 添加自定义提取模式

在 `NxsConfigDecoder` 类中添加新方法：

```python
def extract_custom_items(self):
    """提取自定义物品列表"""
    pattern = r'你的正则表达式'
    results = self.extract_pattern(pattern, group_index=1)
    
    # 去重
    unique_items = []
    seen = set()
    for r in results:
        name = r['text']
        if name not in seen:
            seen.add(name)
            unique_items.append(name)
    
    return unique_items
```

### 调整上下文大小

```python
# 搜索时指定上下文大小（默认200字节）
results = decoder.search_keyword('关键词', context_size=500)
```

### 调整字符串最小长度

```python
# 提取中文字符串时指定最小长度（默认2）
chinese = decoder.extract_chinese_strings(min_length=5)

# 提取ASCII字符串时指定最小长度（默认4）
ascii_strings = decoder.extract_ascii_strings(min_length=8)
```

## 注意事项

1. **编码问题**：部分配置表可能使用其他编码，如遇乱码可尝试修改解码方式
2. **性能**：大型文件（>10MB）可能需要较长时间，建议先用关键词定位
3. **去重**：提取的字符串可能有大量重复，使用时注意去重
4. **上下文截断**：关键词上下文可能被非打印字符截断，建议适当调大context_size

## 相关文件

- `nxs_config_decoder.py` - 主解码器脚本
- `extract_weapon_skin_records.py` - 武器皮肤专项提取脚本
- `find_bindict_in_weapon_skin.py` - BinDict特征查找脚本
- `weapon_skin_extracted.json` - 武器皮肤提取结果（JSON）
- `武器皮肤列表.txt` - 武器皮肤列表（文本）

## 更新日志

### v1.0 (2026-08-29)
- 初始版本
- 支持UTF-8字符串提取
- 支持关键词搜索和上下文提取
- 支持武器皮肤和时装自动提取
- 支持结果导出为JSON和文本格式
- 已验证：1B249D5C9984E1B4.nxs（物品/礼包配置表）
