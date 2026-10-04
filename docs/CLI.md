# CLI 手册 — `toolkit_cli.py`

统一入口。**所有命令都只读源包**；写入一律落到 `03_执行/` 或 `--out` 指定目录。

```bash
export PYTHONPATH="<repo>/01_工具/工具库/00_共享核心"
python 01_工具/工具库/00_共享核心/命令行/toolkit_cli.py <命令> [子命令] [参数]
```

> Windows 下把 `export X=Y` 换成 `set X=Y`（cmd）或 `$env:X="Y"`（PowerShell）。

---

## 全局参数

| 参数 | 说明 |
|---|---|
| `--root ROOT` | 项目根（覆盖环境变量与自动探测） |
| `--jobs JOBS` | 并行数：`auto`（默认，按硬件+任务类型自动）或具体数字 |
| `--cpu-limit N` | 整机 CPU 占用上限 %（默认 80；超了自动让路） |
| `--gpu-limit N` | GPU 占用上限 %（默认 80） |
| `--gpu {auto,on,off}` | GPU 加速：`auto` 能上才上 / `on` 强制试 / `off` 禁用 |
| `--no-throttle` | 关掉反馈限流（跑满机器，适合没人在用电脑时） |

---

## 命令一览（42 个）

段位标记：`①-0` 底座 · `①-1` 定位 · `①-2` 提取 · `②-x` 渲染 ·
`H-x` 热更 · `横切` 跨层工具。

### ① 索引与定位

#### `index` — 统一文件索引 `[①-0]`
建立/更新容器条目索引（SQLite）。
```bash
toolkit_cli.py index build
toolkit_cli.py index status
```

#### `verify` — 端到端自检 `[①-0]`
SQLite + 三条已知路径全链自检。**每次大改后跑一次**。
```bash
toolkit_cli.py verify
```

#### `find` — 逻辑路径查物理候选 `[①-1]`
一个逻辑路径可能落在多个容器 ⇒ 全部列出。
```bash
toolkit_cli.py find 'weapon\skin\skin_1003_010\skin_1003_010.mtg'
```

#### `names` — 名字还原 `[①-1]`
路径 → 容器 + 行号（双 seed murmur3 → 索引 `fid_hex`）。
```bash
toolkit_cli.py names lookup 'model\login56\textures\login56_diban_d.tga'
toolkit_cli.py names build        # 从文本产物挖路径，建/扩字典
toolkit_cli.py names stats        # 字典规模 / 命中率 / 覆盖率排行
toolkit_cli.py names candidates   # 候选名册（候选 ≠ 名字，不进字典）
toolkit_cli.py names items        # item_id → 名字 回填链
```

#### `locate` — 行号 ↔ 文件 `[①-1]`
```bash
toolkit_cli.py locate 'res.gpk' 4400            # 容器+行 → 产物文件
toolkit_cli.py locate --fid B2F857EE05EFD56C    # fid 反查容器/行（可多次）
toolkit_cli.py locate 'res.gpk' 4400 --head 64  # 额外打印前 N 字节 hex
```

#### `extract` — 定点提取 `[①-1]`
```bash
toolkit_cli.py extract 'res.gpk' 4400 --out out/
```

#### `materialize` — 产物 → 还原树 `[①-1]`
按**源路径**物化（硬链接，幂等）。用最新字典，不是模块的 v6 默认。
```bash
toolkit_cli.py materialize
```

#### `resolver` — 资源物理桥定位器 `[①-1]`
原 `resource_resolver` 的独立入口。
```bash
toolkit_cli.py resolver --help
```

#### `restore` — 文件名还原 `[①-1]`
配置表 → `path_id` → `ui.npk`。
```bash
toolkit_cli.py restore
```

#### `thfb` — THFB 哈希提取 `[①-1]`
`.thx/.thh`：24 B 条目 `[16B hash][u32][u32]`；`hash → IDX → 1DPW → DDS`。
```bash
toolkit_cli.py thfb
```

#### `bindict-check` — BinDict 自检 `[①-1]`
AUG attrs + KJ1 转印。
```bash
toolkit_cli.py bindict-check
```

#### `bridge-audit` — 皮肤逻辑路径→IDX/WPK 物理桥审计 `[①-1]`
只读。查"逻辑路径能不能桥到物理实体"。
```bash
toolkit_cli.py bridge-audit
```

#### `fiddiff` — fid 增删对比 `[①-1]`
两个 `pkg_N.pi` 目录的 fid 增删。
```bash
toolkit_cli.py fiddiff <A> <B> --named      # 只看有名
toolkit_cli.py fiddiff <A> <B> --grep 关键词
```

### ① 概览与提取

#### `overview` — 全格式概览 `[①-0]`
NPK 条目数 + FPK 包分类。
```bash
toolkit_cli.py overview
```

#### `query` — 条件筛条目 `[①-2]`
只看规模和形状，**不落盘**。
```bash
toolkit_cli.py query --help
```

#### `bulk` — 批量提取 `[①-2]`
断点续跑 + 清单 + 类型识别 + 错误聚合。
```bash
toolkit_cli.py bulk <目标> --out <目录>
```

#### `identify` — 产物类型识别 `[①-2]`
魔数 → 纹理 / 配置 / 网格 / 音频。
```bash
toolkit_cli.py identify <目录>
```

#### `decode-audit` — 解码线体检 `[①-2]`
按【容器 × flag】分层抽样，判据不带盲区。
```bash
toolkit_cli.py decode-audit
```

### ② 渲染与资源

#### `tex` — 贴图 → PNG `[②-2]`
只走 `dds_rgba_canonical` 规范入口。支持 DDS / BC7 / KTX。
```bash
toolkit_cli.py tex <dds目录|文件|glob> --out <目录> [--force] [--ext dds]
```
> ⚠️ **只吃 `dds` / `ktx`**；`.tga` 要用 PIL 自己转。

#### `glb` — `.mesh` → GLB `[②-1]`
部件级 / 多部件，世界坐标拼接 + 自检报告。
```bash
toolkit_cli.py glb <mesh...> --out out.glb
```

#### `sheet` — 装配帧 → 材质表 `[②-1]`
`.c159` 解析，配对规则 `C159_PARAM_PAIRING`。
```bash
toolkit_cli.py sheet <xxx.c159>
```

#### `audio` — 音效轨道 `[②-2]`
`.sfx` → 帧表 JSON（节点树 / 色帧 / 绑定贴图）。
```bash
toolkit_cli.py audio <sfx> --out out/
```

#### `render` — 材质分层出图 `[②-3]`
非交付面 PNG + `layers_trace.json`。
```bash
toolkit_cli.py render <材质>
```

#### `texscan` — 匿名纹理筛选 `[②-2]`
匿名 GPK 纹理颜色筛选 / 未上线候选。
```bash
toolkit_cli.py texscan
```

#### `declared` — 声明路径 HIT/MISS 矩阵 `[②-2]`
`.c159` / `.mtg` / `.sfx` 里声明的资产路径 → 容器命中矩阵。
```bash
toolkit_cli.py declared --help
```

#### `atlas` — spine 图集层 `[②-2]`
```bash
toolkit_cli.py atlas list                    # 家底
toolkit_cli.py atlas discover                # 按尺寸认本体（复原真名）
toolkit_cli.py atlas export
```

### H 热更与散文件层

#### `loose` — 散文件层 `[H-2]`
客户端**单独下载**的文件（`.idx` + `*.wpk`）解密与内容寻址。
```bash
toolkit_cli.py loose scan --out out/ [--source-root E:\mrzh\Documents\res] [--pkg-filter 255]
toolkit_cli.py loose match --dir out/ [--limit 20] [--out report.json]
```
- `scan` = 解密（`1DPW` 容器 → 明文 DDS 等；扫全部家族）
- `match` = 内容 MD5 撞本地索引 ⇒ **不靠名字**定位「哪个容器哪一行」

#### `hotfix` — 热更线总入口 `[带H]`
```bash
toolkit_cli.py hotfix all              # 下载 + 解包定位 + 官方对比 + 报告
toolkit_cli.py hotfix report           # 只出报告（不下载）
toolkit_cli.py hotfix bundle           # 生成标准交付结构
toolkit_cli.py hotfix rows             # 行级热更 diff（新增/移除/真内容变更）
toolkit_cli.py hotfix patchlog         # 读客户端补丁日志 plcoht_ag（XOR 0xAA）
toolkit_cli.py hotfix apply            # 就地增补进还原树（默认 dry-run）
```

#### `delta` — 版本差异取证 `[H-1]`
正式服 vs 测试服差在哪。
```bash
toolkit_cli.py delta
```

#### `snapshot` — 容器快照 `[H-2]`
写入窗口守卫；**只读 `E:\mrzh`**。
```bash
toolkit_cli.py snapshot
```

#### `ovl` — overlay 包 `[H-1]`
overlay 包 = 普通 NPK 容器。
```bash
toolkit_cli.py ovl entries <包>     # 看条目表
toolkit_cli.py ovl unpack <包>      # 全量解包分类落盘
```

#### `npk` — NPK 头与条目表 `[①-x]`
解 48 B 头（AES-ECB）+ 读条目，**支持 CDN URL**。
```bash
toolkit_cli.py npk <文件或URL>      # 只取头 + 表
```

### 横切工具

#### `tables` — 配置表层
```bash
toolkit_cli.py tables list              # 按奖池/活动/时装/商店/文字 分类计数
toolkit_cli.py tables find model_show   # 按关键词找表
toolkit_cli.py tables chs --keyword model_show --out out/   # 抽中文名（UTF-8）
toolkit_cli.py tables refimg            # 抽表里明文的图片路径
toolkit_cli.py tables copies --audit    # 表副本：一张表有几份、该用哪份
```

#### `lottery` — 奖池层
```bash
toolkit_cli.py lottery list
toolkit_cli.py lottery find <关键词>
toolkit_cli.py lottery show <池>
toolkit_cli.py lottery delta            # 本次热更涉及哪些池
```

#### `shader` — 着色器层
```bash
toolkit_cli.py shader list              # 家底
toolkit_cli.py shader info <blob>       # 看 blob
toolkit_cli.py shader export <blob>     # 拆成 .dxbc（可选 .asm）
```

#### `script` — 脚本模块方言读取 `[①-x]`
抽字符串 / 整数（NeoX 魔改 marshal；**还原不了字节码**）。
```bash
toolkit_cli.py script <目标>
```

#### `servers` — 服型后缀总表
中文名 / 依据 / 本客户端是否真有表族。
```bash
toolkit_cli.py servers
```

#### `content` — 内容指纹索引
容器+行 → 内容 MD5，建一次以后秒查。
```bash
toolkit_cli.py content
```

#### `sched` — 智能调度
看硬件 / 并行预算 / 哪些任务真能上 GPU。
```bash
toolkit_cli.py sched
```

#### `map` — 工具 × 段位映射
```bash
toolkit_cli.py map [--seg ②-2] [--files] [--json]
```

#### `export` — 通用导出器 `[①-1]`
解析结果 → 表格文件（csv / json / md）。
```bash
toolkit_cli.py export <输入> --out x.csv
```

---

## 退出码约定

| 码 | 含义 |
|---|---|
| `0` | 成功（`--strict` 下例外） |
| `1` | 失败，或 `--strict` 下出现单项失败 |

---

## 配套脚本（不在 CLI 内）

| 脚本 | 用途 |
|---|---|
| `02_图文音频渲染/皮肤链与渲染/resolve_asset.py` | **资源定位四步法**（`--ref` / `--find` / `--semantic`） |
| `02_图文音频渲染/皮肤链与渲染/shot_page.py` | 起 CDP + 截图 + 读 `window.__dbg` |
| `02_图文音频渲染/皮肤链与渲染/serve_web.py` | 起站点服务（先探活再起） |
| `02_图文音频渲染/皮肤链与渲染/decode_preview_ui.py` | 抽 NeoX `.py` 的字符串池 |
| `02_图文音频渲染/皮肤链与渲染/study_engine_api.py` | 渲染 API 按主题归类 |
