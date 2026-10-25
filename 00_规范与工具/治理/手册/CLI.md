# CLI 手册（2026-10-22 精简版）

只有一个入口：`python la.py <命令>`

## 命令表

| 命令 | 作用 |
|---|---|
| `doctor` | 环境自检：项目根 / 索引行数 / CLI 命中 / 服务 |
| `status` | 服务与数据概览 |
| `index build|status|all` | 重建 / 查看索引 |
| `find <路径>` | 逻辑路径 → PE/PC 包与行（自动换扩展名、_b/_s 档） |
| `locate [容器] [行] [--fid HEX]` | 行 → 内容 / fid 反查 |
| `tables list` / `tables show <表>` | 配置表清单 / 单表定位 |
| `img best <路径>` | 列出图片全部候选（按档位与尺寸排序） |
| `img export <路径> [-o out.png]` | 导出图（PE `.ktx` → PC `.bc7` 兜底） |
| `board check <板块>` | 校验板块契约 |
| `board run <脚本>` | 跑板块构建（board_kit） |
| `web build|serve|shot|refresh|check` | 站点：manifest / 服务 / 截图 / 刷新 |
| `hotfix plan|apply|report` | 热更 |
| `spine --filter <词>` | Spine 三件套导出 |
| `npk export|query` | item_icon 图标库 |
| `watch device|cdn|logcat` | 热更/设备监测 |
| `tool <…>` | 透传 toolkit_cli（逃生舱） |

## 典型链路

```bash
python la.py find ui/item_icon/icon_410001.png
python la.py img best ui/item_icon/icon_410001
python la.py img export ui/item_icon/icon_410001 -o out.png
python la.py tables show nucleus_build_data
python la.py board run tools/build_kill_broadcast_kit.py
python la.py board check kill_broadcast
python la.py web build
python la.py hotfix plan
```

## PC 源（`E:\mrzh` 只读）

PC 与 PE 共用同一套路径哈希，所以名字不用重做；只有容器索引要单独建。

```bash
# 索引（只读包头条目表，几分钟跑完 60 包）
python 00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描/build_pc_index.py \
    --root "E:/mrzh" --out 01_索引与产物/10_索引/pc_index.sqlite3
python .../build_pc_index.py --probe 3        # 只扫 3 个包验证

# 还原树（按名字表还原路径落盘）
python .../build_pc_tree.py --workers 4
python .../build_pc_tree.py --pack ui_01.gpk  # 单包

# 取图
python 00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pc_fetch.py <逻辑路径> out.png
```

本机实测规模：`pc_index` 60 包 / 2,363,986 行 · `pc_index_layered` 2,271,372 · `pc_index_res` 2,091,980 · `pc_index_gres` 201,747。
名字口径：`murmur3_x86_32(路径)` 双 seed（高 `0x77777777` / 低 `0x66666666`），`names_join.sqlite3` 2,895,737 条，PE/PC 通用。

## 设计口径

- 顶层命令按「用户要做什么」分组，不按代码模块分组。
- 一个命令只做一件事；复杂组合走 `tool` 逃生舱。
- `la.py doctor` 通过即可直接跑，不需要手动设 PYTHONPATH。
