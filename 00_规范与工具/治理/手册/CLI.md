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
| `vehicle extract [--only deep\|lore]` | （三）载具板：提取冻结产物（魅力值/速度物理参数 ／ 描述/特技/氮气/生命） |
| `vehicle build [--only params\|lore]` | （三）载具板：回填到 vehicle_full（须先 extract） |
| `skin fx-names [--out PATH] [--cdata DIR]` | 武器皮肤：从还原树解「战斗表现」正式名（62 皮肤 / 270 条），写 JSON |
| `skin check` | 与现有产物逐项比对（新增/消失/变更），漂移即非 0 退出 |
| `web build|serve|shot|refresh|check` | 站点：manifest / 服务 / 截图 / 刷新 |
| `hotfix plan|apply|report` | 热更 |
| `spine --filter <词>` | Spine 三件套导出 |
| `npk export|query` | item_icon 图标库 |
| `watch device|cdn|logcat` | 热更/设备监测 |
| `tool <…>` | 透传 toolkit_cli（逃生舱） |

## 武器皮肤正式名（特效真名）

不复用旧工作副本，直接读还原树 cdata：

```bash
python la.py skin fx-names                     # 生成 01_索引与产物/30_分析/weapon_skin_effect_show.json
python la.py skin fx-names --out /tmp/x.json   # 换输出（比对用）
python la.py skin check                        # 与现有产物比对：无差异退出码 0
LA_CDATA=<cdata 目录> python la.py skin check  # 换树（另一份客户端）
```

输出结构：`{skin_id: [{order, slot, slot_gun, slot_melee, name, icon, icon_melee, record_off}]}`，
`slot` = 枪械面板显示名，`slot_melee` = 近战同位置名（近战面板显示「挥砍特效」）。

解析器：`02_wiki/web/pipelines/parsing/effect_show_names.py`。
同目录 `effect_show.py` 是旧的 entry 级入口（依赖已清理的工作副本，仅供历史调用方）。

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

## （三）载具板深挖链

两期分离，各有一份冻结产物，`extract` 提取、`build` 回填，互不覆盖：

```bash
# 提取（只读源包与还原树 → 01_索引与产物/30_分析/载具深挖_2026xxxx/）
python la.py vehicle extract                 # 两期全跑
python la.py vehicle extract --only deep     # 第一期：魅力值 / 加速度 / 最大速度
python la.py vehicle extract --only lore     # 第二期：描述 / 特技 / 氮气 / 生命量

# 回填（冻结产物 → data/boards/vehicle_full.{json,js}）
python la.py vehicle build                   # 两期全跑（params → lore，顺序固定）
python la.py vehicle build --dry-run         # 只算不写
python la.py web build                       # 回填后重建 manifest
```

单脚本也能直接跑（等效于上面的命令，路径自动从脚本位置推断）：

```bash
python 03_执行/vehicle_deep_extract.py   --out DIR [--server classic|kj1|yk]
python 03_执行/vehicle_lore_extract.py   --out DIR
python 02_wiki/web/tools/build_vehicle_params.py --dry-run
python 02_wiki/web/tools/build_vehicle_lore.py   --dry-run
```

口径与已知坑见各脚本头部注释；`vehicle_modding_data` 的 0x0b 指针基址（=28）
由脚本暴力自解，行↔块按序配平**不可靠**，特技归属一律以 `ref_vehicle_id` 为准。

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
- **解释器**：须用项目 venv（`00_规范与工具/环境/venv/Scripts/python.exe`）。
  系统 python 缺 `cryptography` / `yaml`，`la.py` 与解包工具链都会 import 失败。
- **路径**：所有脚本一律从 `__file__` 反推项目根，禁止写死 `E:/la拆包项目`，
  否则项目一搬目录就全废。需要改指向时用 `--root` / `--cd` / `--out` / `--board`。
