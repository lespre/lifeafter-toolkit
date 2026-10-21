# CHANGELOG

## 2026-10-22 — 解码器 / 反编译链 / 伤害系统 / wiki 大改

### ★ 本次两条主线

**A. PE / PC 双源 2D 定位打通**

- `la.py pe best <路径>` / `pe resolve` / `pe export`：同一逻辑路径在 PE `.ktx`、PC `.bc7`、`.dds`、`.png` 里找，**多档候选按命名档位 + 像素尺寸取最高清**，短边 < 96px 判低清直接跳过。
- 修正一个长期误判：`ui/…/icon_*.png` 这类 UI 图标在 PE 里是 `.ktx`，只查 `.png` 会「未命中」——名片框 454 条里实测可定位 450 条。
- 名片框图标批量导出 **369 张**（160×160 RGBA，按内容 sha1 去重，81 条低清/重复跳过），已挂到 wiki 卡面。
- 新增 `pe_fetch_hires.py`（候选枚举 + 档位排序 + 尺寸闸门）。

**B. 活动表定位**

- `activity_master` 886 条（进行中 51 / 未开始 9 / 已结束 794 / 无时间 32），按开始时间倒序，补 `sub_title`（656 条）。
- 活动 → 奖池 → 展示奖励 三层链已建：`huodong_conf`(hd_class) → `multi_optional_lottery` / `super_fashion_lottery` / `common_hd_show_reward`。
- 场景平衡 98 组与活动表按 `scene_id` 对得上，PvP 场景可直接查档位。

### 1. 配置表解码器（`toolkit_core/bindict_table.py`）

- 新增 `decode_table_rows(..., lenient=False)`：不再整行丢弃「行尾混排列表 / 0x27 组截断 / overrun / 缺行边界 / 0x36 map 截断」的行，已解字段保留、行尾落 `__tail__`，并标 `lenient_recovered=<原因>`。
- 默认 `lenient=False`，与历史输出逐字节一致（596/596 张表回归全等）。
- 全库实测：652 张表里 **137 张行数变多，回收 60,025 行**（`310,761 → 370,786`），残留丢弃 `69,520 → 9,495`。
  回收最多：`huodong_reward_data +15,984`、`mission_step_event_data +10,485`、`simple_fashion_data +9,405`、`player_ai_monster_equip_data +2,843`。
- CLI：`bindict-check --lenient/--table/--cdata/--json`，不给开关时行为不变。

### 2. 脚本反编译链（`toolkit_core/script_decode.py`）

py314 方言补齐，`HurtCalc.py` 从 64 个可解函数 → **99/99 全部可解**：

- 新增标签：`0x30/0xB0`(float64)、`0x3F`(int64)、`0x3C`(1 字节常量，之前当 int8 多读 1 字节导致整表错位)、`0x28`(长字符串 u32+UTF8)、`0x04/0x08/0x10`(小整数)。
- 修正表序变体：部分函数是 `consts → localsplusnames → names`（与常规相反），交换后属性名恢复（62 项）。
- 修正 `co_consts` count 多算 1 导致三表错位的变体。
- 新增 `neox_dis3.py`（反汇编，带常量/名字解析）与 `neox_pseudo.py`（栈式伪代码）。

### 3. 伤害系统逆向

- 反编译 `hurt_calc`（20,786 B），拿到出伤主公式：
  `护甲差值 = max(0, 破甲-护甲) → 有效系数 → 分段插值 → 保底 → 固定值 + 基数×系数`。
- 部位系数 `get_body_part_hurt_rate`、暴击 `handle_critical_hit`、分段换算 `_apply_rate_factor`、护盾/穿透链全部落地。
- 压缩：`AttributeHelper._apply_attr_factor` 为分段线性；经典服 155 条压缩曲线、简单生存服 18 条。
- 场景平衡：`special_hurt_params_data` 98 组 × `space_data` 场景名 → 70 组有名（南希市 0.95~1.05、夏尔镇 0.6~1.8、远星城 0.8~1.9、红杉镇 0.8~1.8 / 0.95~1.2、雷达模式 0.8~1.8）。
- 经典服同一参数表 693 组（无场景维度，按伤害来源分组），推定上下限分布已导出。

### 4. Wiki

- 板块：26 个公开板块 / 120,405 条；导航 26 引用、0 孤儿、0 失效。
- 新增「PvP 场景平衡」表（63 组，同名同值合并，重点场景置顶，带区间跨度）。
- 新增「伤害公式」页（公式 + 变量来源 + 乘区顺序 + 证据边界）。
- 恢复「服型」板块；「头像总表」改名「名片框外观」。
- 结构：战力类只留 核芯/芯片/无人机/料理/场景平衡；天赋×2、潜能、状态效果 移入资料层。
- 视觉：暖色主题（官方红 #d14b32 + 暖黑底）、hero 换三把随机传世/典藏皮肤、卡片 hover、顶部红色强调线。

### 5. 数据来源修正

- 审计 40 条抽样：**40/40 可定位、193/215 字段一致、0 不一致**（负向对照有效）。
- 修正 provenance 表名 **52,000+ 条**：`common_item_data_base.py`→`common_item_data.py`(36,510)、`fashion_data_chs.py.py`→`fashion_data.py`(1,153)、`fashion_data_for_export_base.py`→`fashion_data_for_export.py`(10,542)、ykxq 变体→yk(658)、注解剥离 2,927、chip 注解 65。
- 剩余 3,092 条均标注原因（归档自引用 1,848 / 退役板 1,189 / 本地模块 21 / 自动筛选逻辑名 26）。

### 6. 容器与二进制

- 新增 `gpk_reader.py`：GPK（新版多包容器）头解析——`AES-ECB(32B)` → magic `HPGF` → ver/table_off/count。
- 排除结论：GPK 条目表不是 AES-ECB/CBC/CTR，不是单字节/seed/tail XOR，不是 zstd/lz4/zlib；客户端 Python 侧校验为 `SIGNATURE ^ a ^ b` 的块结构。
- 从雷电模拟器拉取 `libclient.so`（85 MB ARM64），确认含 `[AttachGpk]` / `decrypt_content` / `GPK API version (current: 6)`；搭建 Ghidra 12.1.4 + JDK21 无头分析环境（`E:\ghidra`）。
- 新增 ARM64 xref 扫描器（ADRP/ADR/rela.dyn 三种），供后续定位 GPK 解密函数。

### 7. 新增工具（节选）

```
toolkit_core/android_gpk.py, bindict_73.py, pe_index.py
命令行/pe全量索引.py, 安卓gpk导出.py, 解码_0x73.py, dedupe_tree.py, repair_tree.py,
      图集_9月28以来新增.py, 本批overlay图集.py, 校验_本期热更.py …
04_站点/web/tools/  build_scene_board_v2.py, render_scene_table_v3.py, decode_hurt_arrays.py,
      probe_factor_groups.py, fix_provenance_tables.py, apply_provenance_fix.py,
      check_board_tables_v2.py, wiki_tidy.py, wiki_restructure*.py, gpk_reader.py, dis_arm64.py …
```
