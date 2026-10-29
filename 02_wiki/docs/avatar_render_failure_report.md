# 头像板动图渲染失败 · 根因报告

> 生成时间：2026-10-30 06:30
> 范围：`board.html?b=avatar_catalog` 动态头像（Spine→APNG）+ 名片框静态边框
> 结论：**渲染"乱七八糟"的根因是渲染内核的 3 个几何/着色 bug（已修）；**
> **"一直渲染失败"的根因是 63 条数据在 PE/PC 包快照里确实缺失（非代码问题）。**

---

## 0. 一句话结论

| 现象 | 真正根因 | 性质 |
|---|---|---|
| 动态头像"乱七八糟"、主体丢失 | `draw_mesh` 重心坐标**坐标系错位** + mesh 路径**漏应用 slot 颜色** | 代码 bug（已修） |
| 帧内色块/反转/乱码 | APNG 编码前 `quantize()` 摧毁多帧透明通道 | 代码 bug（已修） |
| 主体只占画面一小块 | 包围盒用**并集**，被飞散粒子撑大 | 代码 bug（已修） |
| 一张图要 8~13 秒 | `tint()`/`draw_mesh` 每帧拷 1400×1400 全画布 | 代码 bug（已修，43×） |
| 某些头像整块空白 | **61 条贴图页在包快照里真的不存在** | **数据缺口（非 bug）** |
| 某些头像框整块空白 | **2 条 atlas 本身三路不可得** | **数据缺口（非 bug）** |
| 名片框显示风景场景 | 旧脚本用 `resource_path`（`_b_` 场景底图）当边框 | 代码 bug（已修） |

---

## 1. 渲染管线结构（先看懂再改）

```
条目(it) ──spine_path──▶ ① 资源层：PE 索引 → PC 索引 → PC 校准表（三级回源）
                              │  取 .atlas / .json / 页贴图(.png|.dds|.bc7|.ktx)
                              ▼
                         ② 解析层：atlas 解析 → regions{名称→页内矩形}
                                   骨架 json → slots/bones/animations
                              ▼
                         ③ 渲染层：bone_world(增量动画) → apply_ik
                                   → 逐 slot: region 走 sprite 合成
                                            mesh/skinnedmesh 走三角形光栅化
                              ▼
                         ④ 编码层：RGBA 帧 → APNG（save_all + append_images）
```

工具落点：

| 文件 | 职责 |
|---|---|
| `02_wiki/web/tools/spine_render_fix.py` | 渲染内核（本次 3 个 bug 都在这里） |
| `02_wiki/web/tools/avatar_resolve.py` | 三级回源解析器 `Resolver` |
| `02_wiki/web/tools/build_avatar_anim.py` | 动图构建（新版，主用） |
| `02_wiki/web/tools/build_avatar_media.py` | 动图构建（旧版，已去量化，勿再直接用） |
| `02_wiki/web/tools/build_avatar_frames.py` | 静态边框图归位 + 缺图占位 |
| `02_wiki/web/tools/qa_avatar_anim.py` | APNG 体检（帧数/时长/帧间差） |
| `02_wiki/web/tools/qa_frame_hollow.py` | 中空边框检测（中心 alpha 覆盖率） |
| `02_wiki/web/tools/diag_avatar_render.py` | **新增** 全量渲染诊断 |
| `02_wiki/web/tools/audit_avatar_gap.py` | **新增** 贴图页缺口权威判定 |

---

## 2. 已修复的代码 bug（详细）

### ★★ Bug 1（致命）· `draw_mesh` 重心坐标坐标系错位

**位置**：`spine_render_fix.py` → `draw_mesh()`

**现象**：mesh 主体整块不绘制。**离画布中心越远越画不出**——粒子贴图小、坐标接近中心还能画出来，
主体坐标在 544~917 就全丢。这正是"只剩零星粒子和碎片"的成因。

**根因**：

```python
ys, xs = np.mgrid[ly0:ly1 + 1, lx0:lx1 + 1]   # ← 相对 out 的【局部】坐标（从 0 起）
px = xs + 0.5
py = ys + 0.5
w0 = ((y1 - y2) * (px - x2) + ...) / den       # ← x0/y0 是【画布绝对】坐标
```

`w0/w1/w2` 在两个不同坐标系里计算 → `inside` 几乎恒为 False → 三角形全被 `continue` 跳过。

**修法**：

```python
px = xs + minx + 0.5
py = ys + miny + 0.5
```

**验证**（同一 atlas、同一帧）：

| 样本 | 修前覆盖率 | 修后覆盖率 |
|---|---|---|
| `touxiang_ani_39` | 0.0000（全透明） | **0.6104** |
| `touxiang_ani_50` | 0.028 | **0.2548** |

> 教训：这个 bug 之所以长期没被发现，是因为**"主体"恰好大多靠近画布中心**，
> 而中心附近局部坐标≈绝对坐标，误差小到看不出。只有坐标偏得远的才暴露。

---

### ★ Bug 2 · atlas 解析把「页属性行」当成 region 名

**位置**：旧 `spine_render.py::parse_atlas`（`spine_render_fix.py` 已改为本地 `parse_atlas_fixed`）

**现象**：`regions` 里混入 `"size: 256,128"`、`"format: RGBA8888"`、`"filter: ..."`、`"repeat: none"`；
页归属（`region["page"]`）判定随之错乱。

**根因**：Spine atlas 里**页属性行是不缩进的**，与 region 名同层级：

```
touxiang_ani_39.png        ← 页名
size: 256,128              ← 页属性（不缩进！）—— 被旧解析器当成 region 名
format: RGBA8888           ← 同上
bg                        ← 真 region 名
  rotate: false           ← 缩进属性行
  xy: 2, 20
```

**修法**（`parse_atlas_fixed`）判定规则：

- 页名行 = 不缩进 且 非 `key:value` 形式
- 页属性行 = 不缩进 且 `key:value` → 只影响当前页，**不生成 region**
- region 名 = 不缩进 且 非 `key:value`，其后紧跟缩进属性行
- region 属性行 = 缩进（`xy/size/orig/offset/rotate/index`）

**验证**：`touxiang_ani_39` regions 由 16（含 4 个假）→ **12**；`touxiang_ani_55` → **13**。

---

### ★ Bug 3 · mesh 路径漏应用 slot 颜色

**位置**：`spine_render_fix.py` → `draw_mesh()` / `render_frame()`

**现象**：setup pose 里 `"color": "ffffff00"`（alpha=0，**隐藏**）的 slot 照样被画出来。
Spine 常用「alpha 淡入」做显隐动画，漏掉颜色 ⇒ 显隐失效、层叠错乱。

**根因**：region 路径有 `tint(tmp, col)`，**mesh 路径完全没有**。

**修法**：`draw_mesh(..., col=None)`，在混合时 RGB 相乘、alpha 相乘；`ca <= 0.002` 直接不画。

---

### ★ Bug 4 · APNG 编码前的 `quantize()` 摧毁多帧

**位置**：`build_avatar_media.py`、`build_avatar_anim.py`

**现象**：APNG 第 2~N 帧出现色块/反转/乱码，帧间差 **75~120**（正常动画 0~25）。

**根因**：

```python
q = [f.quantize(colors=180, method=Image.FASTOCTREE) for f in frs]
```

Pillow 的 `quantize()` 对多帧透明 APNG **只对首帧正确**，其余帧的调色板/透明通道被破坏。

**修法**：删掉量化，直接保存 RGBA：

```python
frs[0].save(out, format="PNG", save_all=True, append_images=frs[1:],
            duration=int(round(dur * 1000 / cnt)), loop=0, default_image=True)
```

**验证**：重新编码后帧间差 **0.0**。

> 历史教训：曾经两个渲染脚本并行写同一目录，**后写的赢** ⇒ 产物是混合体，
> 336/348 张是量化坏图。**铁律：同一产物目录只允许一个渲染进程在跑。**

---

### ★ Bug 5 · 包围盒用「并集」→ 主体被粒子撑成一小块

**现象**：头像框主方框只占画面一小块。

**根因**：并集包围盒被只在 1~2 帧出现的飞散粒子撑大。

**修法**：改**覆盖率法**——统计每像素在多少帧可见，只保留 ≥25% 帧可见的范围；
若全空则退回并集。

---

### ★ Bug 6 · 性能灾难（13 秒/帧）

**根因**：
- `tint()` 对**每个 slot** 都做 1400×1400 全画布 float32 转换（31 MB/次）
- `draw_mesh()` 每个三角形都拷贝一次全画布

**修法**：
- `tint` 改为只对小 sprite 着色
- `draw_mesh` 先算三角形整体包围盒，**只在该范围**内做 numpy 运算
- region sprite 按 (页, region) 缓存

**效果**：4 帧 **53.4 s → 1.24 s（43×）**。全量 422 条从「数小时」降到可接受。

---

### ★ Bug 7 · 页贴图 fallback 顶替

**位置**：`build_avatar_anim.py` 组装 `img_of` 处

**现象**：同一份 atlas 渲染出「四个不同资源」；有时渲染出**别的图**。

**根因**：atlas 声明的页名找不到时，代码回退用 `base + ".png"` 顶替。

**修法**：严格按 atlas 声明的页名解析（页名 → 同名 `.bc7/.ktx/.png`），**取不到就如实放弃**，不顶替。

---

### ★ Bug 8 · 名片框用错资源字段

**现象**：名片框显示成风景场景图。

**根因**：旧脚本取 `resource_path`，而它指向的是 `_b_` **场景底图**（217 张全部如此）。
真正的静态边框是 `image_path`。

**修法**：`build_avatar_frames.py` 改为优先 `image_path` + 中空校验（中心 alpha 覆盖率），
场景图一律不作为边框。

---

## 3. 环境级根因（极易踩，务必记住）

### ★ `nohup ... &` 启动的后台进程会在工具调用结束时被回收

现象：`render3.log` 停在 `50/422`、`render_full.log` 停在 `200/347`，日志戛然而止、无报错。
**不是超时、不是崩溃，是被 kill**。曾因此误判"渲染卡住"。

**正确做法**：用执行器的正式后台机制（`run_in_background=true`），
不要用 `nohup &` / `setsid` / `disown`。

### ★ 同一产物目录禁止多进程并行写

两个脚本（`build_avatar_media.py` 与 `build_avatar_anim.py`）曾并行写 `assets/avatar_anim/`，
产物混合、哈希不可信。**清空后单进程全量重跑**是唯一可信姿势。

---

## 4. 数据缺口（不是 bug，别再查了）

### 判定方法（权威，可复用）

PC 包内条目按 **`[ATLAS, DDS, JSON]` 三元组**排列：

- ATLAS 首行 = 页名，随后 `size: W,H` 声明页尺寸
- 若**紧邻下一条目是 DDS**，则该 DDS 宽高**必等于** `W,H`
  （实测 `touxiang_ani_16` → `1024,128` ↔ DDS 1024×128；`touxiang_ani_18` → `2048,512` ↔ DDS 2048×512）
- 若下一条目**直接是 JSON**，则该 atlas 的贴图页**在本包快照里确实缺失**

独立佐证：对 `ui/spine/touxiang_ani/touxiang_ani_15` 穷举 **256 种路径变体**
（`.png/.dds/.bc7/.ktx/.jpg/.tga/无扩展名` × `/` 与 `\` × 8 种路径前缀 × 大小写），
**只有 `.atlas` 和 `.json` 命中索引**，贴图页任何写法都不命中 ⇒ 索引里根本没有它的行。

### 缺口清单

| 类别 | 数量 | 说明 |
|---|---|---|
| 有 `spine_path` 的条目 | 422 | 全部进入诊断 |
| 资源齐备、可渲染 | **359** | atlas+json+页贴图 齐全 |
| **贴图页实测缺失** | **61** | 头像 25 / 头像框 15 / 名片框 21 |
| **atlas 三路不可得** | **2** | `da_450101`(头像)、`af_410179`(头像框) |

明细见 `01_索引与产物/30_分析/avatar_anim_gap_audit.json`。

### 结论

这 63 条**不是代码问题**，渲染器再修也画不出来——源数据不在盘上。
处置方式只能是**缺图占位**（页面已有 `.nofig` 样式），不要用场景图顶替。

---

## 5. 误判教训（血泪，最容易再踩）

### ★★ 尺寸撞车 → 邻接规则会误配

"atlas 后 +1..+4 行内找同尺寸 DDS"看似可靠，实则：
`touxiang_ani_17`（size 2048,512）会把 `touxiang_ani_18` 的贴图页（也是 2048×512）误认为自己的。

**必须加像素级校验**：把 DDS 解码成 RGBA，按 atlas 每个 region 的 `xy/size` 去页图对应位置采样，
**所有 region 全透明 ⇒ 配对错误**。

> 通用原则：**结构自洽 ≠ 语义正确。**
> "文件存在""尺寸对得上""哈希能匹配"都只是必要条件，必须用内容或已知事实校验。

### ★ 绿网格不是乱码

`da_450000` 覆盖率 0.976（近满幅）曾被当作"渲染错乱"。
实为 Spine 页贴图里**自带背景层**（`bg_blur` / `grid` / `fg_blur` 等 region），
是游戏内头像的真实设计，**不是 bug**。判断依据：整幅均匀、无色块断层、无反转。

### ★ 结构自洽的旧内核产出过"看起来很对"的错图

旧 `spine_render.py` 的 `bone_world` 对 3.x 字符串时间戳（`"0:0"`）正确，
但 Spine 2.1.27 的时间线是**逐帧数组**（`[{"time":0,"angle":0}]`）。
本项目骨骼是 **Spine 2.1.27**，3.x 写法会静默失配。**先确认 skeleton.spine 版本再写解析。**

---

## 6. 当前状态

### 已修复并落盘

- `spine_render_fix.py`：坐标系错位、mesh 颜色、atlas 解析、包围盒覆盖率、性能
- `build_avatar_anim.py`：去量化、严格页名解析
- `build_avatar_media.py`：去量化
- `build_avatar_frames.py`：优先 `image_path` + 同目录回退 + 缺图占位

### 待办

1. **全量重渲 422 条**（单进程、`run_in_background=true`）
   ```bash
   python 02_wiki/web/tools/build_avatar_anim.py --force
   ```
2. **QA**：`python 02_wiki/web/tools/qa_avatar_anim.py`
   （帧数 ≥6、帧间差 <30、无全透明首帧）
3. **63 条缺图**走缺图占位（`.nofig`），不落场景图
4. **`touxiang_ani_55` 类仍空**（覆盖率 0.0003）：191 slot / 159 mesh 的极端骨架，
   主体疑为 skinnedmesh 或特殊结构，**未定位**，需单独深挖
5. 浏览器截图复验 `board.html?b=avatar_catalog`

---

## 7. 复现与自检命令

```bash
PY="00_规范与工具/环境/venv/Scripts/python.exe"

# 全量渲染诊断（逐条记录失败阶段与原因）
$PY 02_wiki/web/tools/diag_avatar_render.py
#   → 01_索引与产物/30_分析/avatar_anim_render_report.json

# 只查资源链路（不渲染，16 秒）
$PY 02_wiki/web/tools/diag_avatar_render.py --no-render

# 贴图页缺口权威判定（含像素级校验）
$PY 02_wiki/web/tools/audit_avatar_gap.py
#   → 01_索引与产物/30_分析/avatar_anim_gap_audit.json

# APNG 体检
$PY 02_wiki/web/tools/qa_avatar_anim.py

# 中空边框检测
$PY 02_wiki/web/tools/qa_frame_hollow.py
```

---

## 8. 给后人的 10 条硬规矩

1. **先确认 `skeleton.spine` 版本**（本项目 = 2.1.27），再写时间线/mesh 解析。
2. **mesh 的 `uvs` 值域决定贴图来源**：0~1 归一化 → region 裁切；页图像素 → 整张页图。
3. **mesh 的 `path=None`** 时，附件名 = region 名。
4. **几何运算全程统一坐标系**；裁剪区索引与绝对坐标混用是本项目踩过的最贵 bug。
5. **region 路径和 mesh 路径的着色逻辑必须对齐**（都吃 slot color）。
6. **APNG 绝不量化**；`quantize()` 会毁掉第 2~N 帧。
7. **同一产物目录只允许一个写入进程**；先清空再全量重跑。
8. **后台任务用 `run_in_background=true`**，不要 `nohup &`（会被回收）。
9. **尺寸相等 ≠ 同一资源**；资源配对必须过像素级校验。
10. **找不到证据就如实缺图**，绝不拿近似的别的图顶替（顶替 = "乱七八糟"的最大来源）。
