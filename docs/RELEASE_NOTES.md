# 明日之后拆包工具箱 v1.1 · Agent 接手包

> **给 AI Agent 的下载说明** —— 拿到这个仓库，读完下面的三份文件就能开工。

---

## 这是什么

《明日之后》(LifeAfter / mrzh) 客户端资源**解码 · 定位 · 复原 · 可视化**工具链。

**核心能力 = 定位 + 渲染**：把资源从海量容器里**精确定位**出来，再按游戏产物**原样渲染**。

覆盖（不限于）：时装 · 武器皮肤 · 奖池/活动 · 场景/展示台 · 武器/装备 · 音效/特效 · 配置表/图集。

★ **有测试服源 ⇒ 可定位未上线内容**（测试服先于正式服下发新皮肤/新时装/新奖池）。

---

## Agent 接手：三步

### 1. 下载并解压

```bash
# 方式 A：直接克隆（推荐，能继续 pull 更新）
git clone https://github.com/lespre/lifeafter-toolkit.git
cd lifeafter-toolkit

# 方式 B：下载本 Release 的 Source code (zip) 并解压
```

### 2. 读这三份（按顺序）

| 顺序 | 文件 | 内容 |
|---|---|---|
| 1 | `docs/AGENT.md` | **Agent 冷启动手册** —— 30 秒了解 / 开工三件事 / 两类条目 / 验收纪律 / 8 个高频坑 / 硬规则 |
| 2 | `README.md` | 全貌 · 主要功能 · 资源定位四步法 · CLI 速查 · 容器格式 · 常见坑 |
| 3 | `docs/CLI.md` | 42 个 CLI 命令逐条手册 |

补：`docs/USAGE.md`（实战工作流）· `docs/CDN-AND-VERSION.md`（CDN/版本/切服）· `docs/APK-UNPACK.md`（APK 拆包）

### 3. 开工三件事（缺一必翻车）

```bash
# ① 依赖
python -m venv .venv && .venv/Scripts/pip install -r 01_工具/requirements.lock.txt

# ② ★ 设 PYTHONPATH —— 不设必报 ModuleNotFoundError: toolkit_core
export PYTHONPATH="$PWD/01_工具/工具库/00_共享核心"

# ③ 自检（需要自备游戏客户端，路径默认 E:\mrzh）
python 01_工具/工具库/00_共享核心/命令行/toolkit_cli.py verify
```

---

## 仓库里有什么 / 没有什么

**有**：完整工具链（`01_工具/工具库/**`，17 MB 脚本）· 可视化页面（`04_站点/web/**`）·
6 份文档 · 架构骨架。

**没有**（体积大 / 可重建 / 第三方内容）：

| 缺的 | 怎么补 |
|---|---|
| 游戏客户端源包（45G） | 自备客户端，路径 `E:\mrzh` |
| 还原树 | `toolkit_cli.py index build` → `materialize` |
| 索引库 | `toolkit_cli.py index build` |
| 提取产物 | `toolkit_cli.py bulk <目标> --out <目录>` |
| 热更产物 | `toolkit_cli.py hotfix all` / `loose scan` |

---

## Agent 必须知道的四条硬规矩

| 规矩 | 原因 |
|---|---|
| **`0 命中` 先怀疑代码** | 函数用错（gres 用 `parse_gpk`）、偏移错、路径写法错 —— 90% 是代码问题 |
| **引用逐字读** | 一个字符不同 ⇒ `murmur3` fid 全变 ⇒ 必然 0 命中 |
| **哈希自证** | 拿**已知命名文件**算 fid 必须命中；不中 = 方法错，不是数据没有 |
| **源包只读 / 服别不混 / 不编数据** | 安全底线；PC 客户端与 APK 可能不同服 ⇒ 结论必须标服别 |

---

## 硬红线（不可违反）

```text
✗ 修改游戏客户端文件
✗ 动态内存 dump / 调试器 attach（反作弊红线）
✗ 连接未授权服务器
✗ 为省事编造数据（信息不足就如实说"未命中"）
✓ 静态读取（解压 / 解析 / 反汇编）—— 学习研究范围内
```

---

## 一句话交给 Agent

> 解压 → 设 `PYTHONPATH` → 读 `docs/AGENT.md` + `README.md` + `docs/CLI.md` → 跑 `verify`。
> **`0 命中` 先查代码后疑数据**；**引用逐字读**；**哈希自证**；
> **源包只读、服别不混、不编数据**。

---

**合规**：仅供学习研究。请遵守游戏用户协议 —— 不要修改客户端、不要动态注入、不要连接未授权服务器。
