# 通用 CLI 方案

生效：2026-09-26 ｜ 目标：**把重复劳动收敛成命令，把 token 消耗降一个数量级**

---

## 一、诊断：token 到底花在哪

**现状**
```
工具库 235 个 .py，只有 9 个挂统一入口 run_all.py
06_皮肤定位链 45+ 个脚本，只有 6 个带 argparse
其余大量是「有 main 但无参数解析」⇒ 参数/路径写死在脚本里
```

**后果（就是 token 黑洞）**
```
做一件新东西 → 读 3~5 个脚本理解 → 写新脚本（qj_xxx.py）→ 调试
每次 ≈ 50k token，而且脚本内容、报错、重试全进上下文
历史证据：本轮会话写了 40+ 个 qj_*.py，全部是为「同一件事换个对象」重写
```

**根因**：脚本是「一次性的」，不是「参数化的」。

---

## 二、目标：重复操作只剩 6 件

| # | 重复操作 | 现状 | 目标命令 | 收益 |
|---|---|---|---|---|
| 1 | 按路径找条目 | `run_all.py find` ✓ | 不动 | — |
| 2 | 提取载荷 | `run_all.py extract` ✓ | 不动 | — |
| 3 | **装配帧 → 部件表** | 散落，每次现写 | `run_all.py sheet <帧>` | ★★★ |
| 4 | **网格 → GLB** | `export_glb.py` 无 argparse | `run_all.py glb <网格> --mat <c159>` | ★★★ |
| 5 | **一件 → 前端五件套** | `build_wiki_3d_batch.py` 写死典藏皮肤 | `run_all.py pack <id>` | ★★ |
| 6 | **建专题页** | 手工复制 `zhanshen.html` 改 4 处 | `run_all.py page <名> --items <json>` | ★★ |
| 7 | **交付前验证** | 4~5 个脚本分开跑 | `run_all.py check <url>` | ★ |

**预期**：从 ~50k token/件 → ~2~3k token/件。

---

## 三、设计原则

```
1. 不改现有脚本的 main 部分
   ⇒ 现有流程零风险，随时可回滚（删掉新层即可）

2. 新层只 import 现有脚本的【函数】，不 subprocess 调脚本
   ⇒ 不从 stdout 解析，不依赖脚本的参数解析

3. 不加新依赖
   ⇒ 只用 py312_env 已有的（numpy、zstandard、Pillow）

4. 所有路径从 toolkit_core.paths 取
   ⇒ 禁硬编码（这是重构的目标，新层不能又犯）

5. 默认拒绝覆盖；覆盖必须显式 --force
   ⇒ 对标 AssetStudioMod `-r` / QuickBMS `-o`

6. 失败要记账
   ⇒ 每条失败进失败清单，禁静默跳过
```

---

## 四、接口设计

### 4.1 `sheet` —— 装配帧 → 部件表

```bash
python run_all.py sheet "<装配帧路径>" [--json out.json]
```
**输入**：`.c159` 或装配帧文件路径
**输出**：JSON + 人可读表
```json
{
  "frame": "...",
  "parts": [
    {"name":"b_m_3715", "gis":".../b_m_3715a_4.gis",
     "lods":[".../b_m_3715a_4_lod01.gim", "..."],
     "bbox":{"ctr":[2.07,5.82,-1.61], "dim":[3.04,11.62,2.92]}}
  ]
}
```
**依据**：装配帧是权威 —— 它给 `Name` + `BoundingInfo` + `GisFiles` + `Lods`（每部件自己精确的 lod 路径）

### 4.2 `glb` —— 网格 → GLB

```bash
python run_all.py glb "<网格路径>" [--mat <c159>] [--tex <目录>] [--out x.glb] [--force]
```
**输入**：`.mesh` / `.gim` 路径 +（可选）材质 c159 + 贴图目录
**输出**：GLB 文件 + 同目录 provenance JSON
**内部**：调 `mesh_parse2.py` 的解析 + `export_glb.py` 的导出
**要点**：多部件直接按世界坐标拼（顶点已是世界坐标，无需归位）

### 4.3 `pack` —— 一件 → 前端五件套

```bash
python run_all.py pack <skin_id> [--dir assets/3d/weapon_skin] [--force]
```
**输出**（按 `前端交付要求.md` 的实测口径）：
```
viewer.json            ★硬必需（缺 → 无 3D 按钮）
<state.model>.glb      ★硬必需
neox_material.json     ★真材质必需（primitives[] 必须与 GLB mesh 顺序一一对应）
src_tex/*.png          条件必需
src_cube/faces/*.png   条件必需
```
**收尾必须自动跑**：`python tools/rebuild_weapon_skin_media.py`（硬门禁）

### 4.4 `page` —— 建专题页

```bash
python run_all.py page <页名> --items items.json [--title "标题"] [--dir assets/3d/xxx]
```
**items.json**：`[{"g":"组名（件数）","items":[{"f":"文件名.glb","label":"显示名"}]}]`
**做四件事**：① 从 `zhanshen.html` 复制 ② 改 4 处 ③ 注册进 `wiki.html` 的 `EXTRA_LINKS` ④ 保留返回按钮与自检钩子

### 4.5 `check` —— 交付前验证

```bash
python run_all.py check <url> [--mobile] [--items "标签1,标签2"]
```
**做三件事**：桌面截图 + 手机截图 + 逐条目点一遍，读 `window.__loaded` / `window.__err`

---

## 五、实现顺序

```
第 1 步  la_common.py     通用库：路径、失败清单、覆盖策略、JSON 读写
第 2 步  sheet            最简单、无渲染依赖，先把「通用层」跑通
第 3 步  glb              复用 mesh_parse2 + export_glb
第 4 步  pack             串起 glb + 落位 + rebuild 门禁
第 5 步  page / check     最后做（依赖前端模板稳定）
```

**每步验收**：拿一个**已知正确的历史案例**跑，产物与历史定版**逐字节或逐字段对比**。

---

## 六、验收标准

```
□ 现有流程不受影响：run_all.py 的 9 个子命令行为不变
□ 新命令带 --help 且参数完整
□ 用一个历史案例跑通，产物与历史定版一致
□ 失败进失败清单，不静默
□ 默认拒绝覆盖，--force 才覆盖
□ 新层不含硬编码路径（grep 验证）
□ 现场记录：改造前后做同一件事的 token 量对比
```

---

## 七、这条为什么能省 token（给下一个 AI 看）

```
改造前的工作流：
  用户说「把这件渲染一下」
  → 我 ls 工具库 → 读 export_glb.py（196 行）→ 读 mesh_parse2.py（152 行）
  → 读 c159_pair.py（351 行）→ 理解参数 → 写 qj_new.py → 跑 → 报错 → 改 → 再跑
  总计 ≈ 50k token，且这 700 行脚本内容永久留在上下文里

改造后的工作流：
  用户说「把这件渲染一下」
  → python run_all.py glb "<网格>" --mat "<c159>" --out x.glb
  → 看输出
  总计 ≈ 2~3k token

★ 关键：新层的《接口》要写进 `拆包流程.md` 的命令速查表
  ⇒ 下一个 AI 只读速查表就知道有什么命令，不用读实现
```

---

## 八、为什么先做 sheet / glb / pack

```
出现频率最高：每一件皮肤/时装/头饰都要走「找网格 → 出 GLB → 落前端」
历史重工证据：本轮 40+ 个 qj_*.py 里，超过一半是这三件事的重写
且三者有依赖关系：sheet 是 glb 的输入准备，pack 是 glb 的批量壳
⇒ 先打通一条完整链，后面 page/check 才有东西可验证
```

**改造方式选「另建通用层」而不是「改现有脚本」**：
- 现有 235 个脚本里大量是历史证据（含已证伪方法的负结果），改它们有丢失证据的风险
- 另建一层 = 随时可删回原状
- 而且现有脚本的**函数**本身是干净的（脏的是 main 里的硬编码路径），import 函数即可
