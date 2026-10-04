# LifeAfter Unpacker Toolkit（明日之后拆包工具箱）

> 个人研究向的《明日之后》(PC) 离线拆包工具集 —— 从只读源包到可读产物的一站式流水线。
> ⚠️ 屎山警告：长期个人迭代的产物，目录里同时有“权威链路”和“历史实验”，以
> `00_治理/文档/工具说明/统一索引与拆包流程.md` 与 `00_治理/规范/格式拆解手册.md` 为准。

## 界面预览

| 拆包任务（防呆选包） | 皮肤 3D 预览器 |
| :---: | :---: |
| ![拆包器界面](../00_治理/文档/工具说明/screenshots/unpacker-gui.png) | ![皮肤预览器](../00_治理/文档/工具说明/screenshots/skin-viewer.png) |

## 下载

- **图形化 EXE 已降级（暂不排期）**：旧的 `明日之后拆包器_新.exe` 现归档在 `03_执行/90_临时/工具区归档_20260926/_archive/`（工具侧归档已迁出工具区）。
  用户明示「现在的拆包功能还一直是半吊子，我们还得接着优化拆包」⇒ **先补功能，再谈打包**。
  需要源码构建时：`pyinstaller 工具库/00_共享核心/打包/明日之后拆包器_新.spec`。

## 能力一览

- **统一文件索引（索引优先）**：逻辑路径 → 64 位 fid → 容器/行/偏移，一次构建（GPK/FPK/NPK 全量），全流程定点查询与提取。
- **双线拆包**：按「文字线（数据/文本）」与「渲染线（贴图/模型/材质）」分线归档，目录自动分树。
- **解包后自动转可读**（可选）：DDS/TGA/KTX → PNG；bin/二进制 → 字符串表；原文件永不动，产物入 `_readable/`。
- **防呆选取**：勾选拆包方向后按内置索引自动选取待拆容器，可逐项勾除。
- **武器皮肤定位链专题**：扫描 3D 素材目录 + 索引逐条定位源引用，可一键生成 Markdown 报告。
- **3D 预览器缝合**：与本地 Wiki 的皮肤海报预览器同源（three.js + 本地静态服务，见交接文档）。

## 快速开始

```bash
# 1) 依赖（本环境由 uv 创建，没有 pip，别用 python -m pip）
uv pip install --python ".venv/Scripts/python.exe" -r 01_工具/requirements.lock.txt

# 2) 统一索引（只读源包，产物在 03_执行/10_索引/indexes/）
python run_all.py index status
python run_all.py index build          # mrzh 重装后才需要重建

# 3) 定点查询 / 提取
python run_all.py find "common\env_map\qiangpi.cube"
python run_all.py extract "common\env_map\qiangpi.cube" out.dds --container res.npk --row 14213
python run_all.py verify
```

> 依赖只有一份权威清单：`requirements.lock.txt`（带版本锁）。历史的 `requirements.txt`
> 经比对确认是它的**子集**，2026-09-26 移进 `03_执行/90_临时/工具区归档_20260926/_archive/requirements.txt`，不再维护。

## 统一入口子命令

```
index build|status   统一 SQLite 文件索引（GPK/FPK/NPK）      overview      全格式概览（NPK/FPK/1DPW）
find <逻辑路径>      索引查询，返回全部候选                  restore       文件名还原（170 条 + 解包验证）
extract <路径> <输出> 唯一命中后定点提取                     bindict-check BinDict 自检（AUG attrs + KJ1 转印）
verify              索引 + 已知路径端到端自检                thfb          THFB 哈希提取
glb <mesh>          部件级/多部件 .mesh → 单个 GLB           bridge-audit  皮肤逻辑路径→IDX/WPK 物理桥审计（只读）
export <输入> --out x.csv   解析结果 → 表格（csv/json/md）
```

兼容壳：`工具库/01_解码定位复原/解包与扫描/batch_unpack_ui.py`（旧文件名入口，等价于 `run_all.py`）。

## 目录结构（简）

```
01_工具/                           ← 根上只有 3 个文件 + 1 个目录
├── run_all.py                     命令行统一入口
├── requirements.lock.txt          依赖唯一清单（版本锁）
├── README.md                      本文件
└── 工具库/                        全部功能模块
    ├── 00_共享核心/               统一索引核心
│   ├── toolkit_core/          核心库（Python 包名，import 锚点，勿改名）
│   ├── 命令行/                 toolkit_cli.py
│   ├── 图形界面/               app.py（GUI 源码）
│   ├── 独立工具/               physical_bridge_audit.py · strings_search.py
│   ├── 测试/                   契约测试 + fixtures + conftest.py
│   └── 打包/                   明日之后拆包器_新.spec
    ├── 01_解码定位复原/           解包与扫描 · 容器格式 · 表解码 · 名字还原 · 哈希提取 · 资源索引 · 客户端逆向
    ├── 02_图文音频渲染/           皮肤表 · 皮肤链与渲染 · 纹理转换 · 3D预览器/
    ├── 03_前端展示交互/           GUI 资源（样式表等）
    ├── docs/                      脚本清单（自动生成）
    └── _归档/                     归档脚本
```

> **已迁出工具区（2026-09-26 二轮整理）**
> - `统一索引与拆包流程.md` + 界面配图（原 `docs/screenshots/`）→ `00_治理/文档/工具说明/`
> - `_archive/`（旧 EXE · readme.txt · requirements.txt · 旧索引_20260921/）→ `03_执行/90_临时/工具区归档_20260926/_archive/`
> - `.buildenv/`（孤儿 venv，718 MB，其中 `Scripts/activate.bat` 的 `VIRTUAL_ENV` 指向已不存在的旧路径）→ **已删除**；
>   依赖统一用 `E:\la拆包项目\.venv\Scripts\python.exe`。
> - `3D预览器/` → `工具库/02_图文音频渲染/3D预览器/`（`app.py` 按 `INDEX_HOME/工具库/02_图文音频渲染/3D预览器/poster` 取）。
```

## 自检

```bash
# 源码测试（当前基线：84 passed）
cd 01_工具/工具库/00_共享核心 && <venv>/python -m pytest 测试/ -q

# 可执行产物带一键自检：--smoke / --index-smoke / --viewer-smoke / --unpack-smoke
```

## 格式破解进度（原 readme.txt 要点，2026-09 现状）

**已完全破解**
```
.gpk       AES-ECB 解密 + 32 字节条目表 + lz4/zstd 解压 + 魔数判扩展名
.npk(PC)   NXPK 魔数 + AES-ECB 头/表 + 48 字节条目 + Murmur3 双哈希 path_id
.fpk       32 字节头 + Zstd 帧流（连续帧，magic 28 B5 2F FD，帧间 1~3 B 零填充）
           64 包分类：DDS 纹理流 58 / 活动时装 001 / MP4 002 / FSB5 010 / 模型网格 8 / 半加密 3
.wpk/.idx  1DPW 外壳 + AC/PC/XC 派生 AES-ECB + 尾部 XOR + ENON/DTSZ + Zstd → DDS
.ktx       伪装 KTX 头 + ASTC 8x8 + mipmap 链 → PNG
APK script.bin  AES-ECB + 16 字节头 + zlib
FSB5       音频库解析（采样名/轨道数），vgmstream 转 WAV
THFB(.thx/.thh) 24 B 条目 [16 B hash][u32][u32]，27.3 万条全量提取，hash→IDX→1DPW→DDS
BinDict .nxs  x{容器 + 0x76 索引 / 0x96 行式 + D6/C6 schema + bitmap + 标量值流
              武器 attrs: field23=hurt(攻击力), field35=power(火力)；转印 KJ1 11 配方×6 配置
文件名还原   双 Murmur3 x86_32（高 seed 0x77777777 / 低 seed 0x66666666），命中≠成功须解包验证
```

**部分破解**
```
FPK 加密网格 013/020/021：明文 float 元数据头(44/56 B) + 加密数据体（熵 6.84/8，疑似流变换，收益递减先搁置）
```

**未破解**
```
lifeafter.exe        修改版 UPX + 整体加密（标准脱壳失败），唯一剩余主线
.enc_jpg 时装图标    伪装 JPEG，样本未找到，待别的模型处理
```

**存疑（以规范为准）**
```
gres .gpk 分卷的 RPGF/CPGF/KPGF：旧 readme.txt 判「非魔数、是偶然字节」；
00_治理/规范/格式拆解手册.md 反过来把它列为长期 hard bone（分卷主链未打通）⇒ 以手册为准。
```

**两个容易踩的算法细节**
```
FPK 帧循环：zstd.decompressobj() + obj.eof + obj.unused_data + find(magic)，
           不要按固定长度切帧（帧间有 1~3 B 零填充）。
path_id：  file_id = murmur3_x86_32(path,0x77777777) << 32 | murmur3_x86_32(path,0x66666666)，
           路径用反斜杠、UTF-8。
```

## 常见问题

- **exe 双击没反应？** 首次启动要解压运行库，等 10~30 秒；仍不行检查杀软是否拦截。
- **解出来全是 .bin / .dds 看不了？** .dds 用拆包器预览页（自动转 PNG）或 Intel Texture Works / GIMP；
  .bin 需要对应格式的解析器，FSB5 音频可用 vgmstream 转 WAV。
- **为什么有些文件解包失败？** 见上面「部分破解 / 未破解」—— 不是「不知道」，而是**明确没破**。
- **怎么找未上线的新内容？** ① `resource_locator.py` 与正式服解包目录对比；
  ② 拆包器「近 30 天内更新」模式；③「定向搜索」模式搜已知关键词。
- **文件名怎么还原？** `run_all.py restore`（`工具库/01_解码定位复原/名字还原/filename_restore.py`），
  双 Murmur3 匹配路径字典；字典越大还原率越高。
- **文档写在哪？** 权威规范 `00_治理/规范/`；现役账 `00_治理/台账/`；过程记录 `00_治理/日志/`；
  可删性总表 `00_治理/索引.md`。

## 历史文档

- 旧 `readme.txt`（v5.0，548 行，含 v4.0 时代的算法细节与旧目录树）已归档到 **`03_执行/90_临时/工具区归档_20260926/_archive/readme.txt`**。
  其中**仍然成立**的部分（破解进度、算法细节、常见问题）已并入本文件；
  **已过期**的部分（`文档索引/`、`工具库/01_核心解包器~10_应用核心` 等旧目录名）不再搬进来。
- 单脚本的历史用法（`fpk_scanner.py` / `fpk_001_full_scan.py` / 各 `bindict_*.py` 的命令行）
  在 `03_执行/90_临时/工具区归档_20260926/_archive/readme.txt` 里；现役替代入口是 `run_all.py` 的子命令与 `工具库/docs/脚本清单.json`。

## 免责声明

- 本仓库仅供**个人学习 / 逆向工程研究**使用；**不包含任何游戏素材或数据**（贴图/模型/表格等一律不入仓）。
- 游戏及素材版权归 **网易 (NetEase)** 所有；请勿将本工具或其产物用于商业用途或传播游戏素材。
- 使用本工具须自行遵守当地法律与游戏用户协议；作者不对任何误用负责。
