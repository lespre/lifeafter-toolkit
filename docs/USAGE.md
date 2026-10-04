# 使用说明 — 实战工作流

面向"我拿到一个需求，该按什么顺序做"。每条都是跑通过的。

> 前置：`export PYTHONPATH="<repo>/01_工具/工具库/00_共享核心"`
> 命令前缀：`python 01_工具/工具库/00_共享核心/命令行/toolkit_cli.py`

---

## 0. 开工三件事

```bash
# ① 服务/环境自检
toolkit_cli.py verify

# ② 看这次热更改了什么
toolkit_cli.py delta
toolkit_cli.py hotfix patchlog

# ③ 确认索引是新的
toolkit_cli.py index status
```

> **如果页面/工具"改了没生效"**：先探活 web 服务（`curl -o /dev/null -w '%{http_code}'`），
> 再怀疑代码。服务静默死过一次会骗你半小时。

---

## 1. 找一张资源（最常见）

### 1.1 有明确路径

```bash
toolkit_cli.py names lookup 'model\login56\textures\login56_diban_d.tga'
```

- **命中** ⇒ 输出 `容器 + 行号`，接着取件：

```bash
toolkit_cli.py locate 'Documents\gres\0000.gpk' 19503
```

- **未命中** ⇒ 见 1.2。

### 1.2 路径查不到（多半是「无名条目」）

**不要去猜路径写法。** 从**引用它的文件**入手：

```bash
# ① 找到引用方（.mtg / .c159），逐字抽它声明的路径
python 01_工具/工具库/02_图文音频渲染/皮肤链与渲染/resolve_asset.py \
  --ref "03_执行/41_还原树/.../skin_1003_010.mtg" --container 'res\weapon.gpk'
```

```text
输出会是：
  ① 引用声明 N 条（每条带 fid）
  ③ 索引库定位：命中 X / N   ← 命中的是【有名】资源
```

- 命中的直接取件；
- **没命中的** ⇒ 这些是**无名条目**，用**邻接**找：

```text
① 先在容器里定位「引用方自己」的行（它多半有名）
     toolkit_cli.py names lookup 'weapon\skin\skin_1003_010\skin_1003_010.mtg'   ⇒ 得行号 R
② 贴图往往就在 R 附近的连续行
     到 41_还原树/<容器>/_未命名/ 里按 00000RRR.dds 邻近区间找
③ 用【通道统计】判身份（不用肉眼）
     resolve_asset.py --semantic <png目录>
```

### 1.3 实例（`skin_1003_010` 光影咏叹调）

```text
容器 res\weapon.gpk（51,826 行）
  r1223  gim · r1224 mesh · r1225 mtg · r1235/1236 preview     ← 哈希锚定
  r1237  001223.c159（3,781 B）                                  ← 材质槽位表
  r1238  基色   r1239 参数   r1241 法线   r1243 表面             ← 邻接锚定
  r1240/1244 细节法线 · r1242 单通道（蒙版/发光）

槽位绑定（c159 解析）：
  blk0 pbr_weapon : Tex0←001a · ParamMap←001m · t_surfacemap←001s_m · NormalMap←001n
  blk1 pbr_crystal: Tex0←001b_m · DetailMap←crystal_bump_n_uvva · t_caustic_tex←crystal_caustic_uvva
                    t_reflection_tex←crystal_reflection_uvva · t_refraction_tex←refraction_envmap_3
                    t_custom_ibl←car_studio01.cube
```

> **金属感/发光来自材质参数与宏**：`u_crystal_color` / `EMISSIVE_MODE` /
> `u_caustic_*` / `u_subsurface_color` —— **不是**基色图的颜色，**不是** IBL。

---

## 2. 新版本热更落地

```bash
# ① 看差在哪（默认 dry-run，安全）
toolkit_cli.py hotfix apply

# ② 确认后真应用（就地增补进 41_还原树）
toolkit_cli.py hotfix apply --real

# ③ 出标准交付结构
toolkit_cli.py hotfix bundle
```

**散文件层**（客户端额外下载的内容，新皮肤/新资源常在这）：

```bash
toolkit_cli.py loose scan  --out 03_执行/90_临时/loose_scan
toolkit_cli.py loose match --dir 03_执行/90_临时/loose_scan
```

```text
scan  = 1DPW 容器 → 明文（实测 5,588 条成功 / 0 失败）
match = 内容 MD5 → 容器 + 行号 + 真 fid   ← 完全不依赖名字
```

---

## 3. 出图 / 出页

```bash
# 贴图 → PNG
toolkit_cli.py tex <dds目录> --out 03_执行/90_临时/tex_out --force

# .tga 用 PIL（tex 只吃 dds/ktx）
python -c "from PIL import Image; from pathlib import Path
for f in Path('dir').glob('*.tga'): Image.open(f).save(f.with_suffix('.png'))"

# .mesh → GLB
toolkit_cli.py glb 03_执行/20_提取/.../001264.mesh 001265.mesh --out dual.glb

# 起站点
python 01_工具/工具库/02_图文音频渲染/皮肤链与渲染/serve_web.py 8770

# 截图 + 读运行时状态（__dbg / __realTex）
python 01_工具/工具库/02_图文音频渲染/皮肤链与渲染/shot_page.py \
  "http://127.0.0.1:8770/skin_preview_v2.html?sid=1110171" out.png 1600 1000
```

> **页面验收靠运行时读数**，不靠肉眼：
> `window.__dbg`（步骤 / 包围盒 / 相机 / 材质名 / 贴图数）、
> `window.__realTex`（真贴图挂载数）。

---

## 4. 配置表

```bash
toolkit_cli.py tables list                    # 家底分类
toolkit_cli.py tables find model_show         # 找表
toolkit_cli.py tables chs --keyword model_show --out out/   # 抽中文名
toolkit_cli.py tables copies --audit          # 查副本，确认用的是哪一份
```

**BinDict 表体结构**（外层 `x{`）：

```text
x{  +  u32(len)  +  body[len]
body: +0 u32 count · +4 48B 保留 · +52 u32 池长 · +56 值流 · +52+池长 行体
值流 tag：0x12=f32 · 0x22=f64 · 0x03=bool · 0x0b=ref · 07 03=分组
```

---

## 5. 脚本模块（UI 代码）

NeoX 字节码**还原不了源码**，但**字符串池**能拿到全部类名/方法名/导入，
足够读懂模块结构和调用关系：

```bash
python 01_工具/工具库/02_图文音频渲染/皮肤链与渲染/decode_preview_ui.py   # 抽字符串池

# 或自抽（最快）
python -c "import re;from pathlib import Path
raw=Path('x.py').read_bytes()
print('\n'.join(dict.fromkeys(m.group(0).decode('ascii','replace')
      for m in re.finditer(rb'[\x20-\x7E]{3,110}', raw))))"
```

> 例：`ui/weapon_skin/WeaponSkinPreview.py` 的字符串池给出
> `on_model_touch_start` / `rotate_speed_x` / `rotate_time` /
> `RenderHelpers` / `PostProcessHelpers` / `set_model_show_weather` …

---

## 6. 验收纪律

| 规则 | 说明 |
|---|---|
| **0 命中先怀疑代码** | 函数用错（如 gres 用 `parse_gpk`）、偏移错、路径写法错 |
| **哈希自证** | 拿**已知命名文件**算 fid ⇒ 必须命中；不中说明方法错，不是数据没有 |
| **不靠行号推测** | 先用哈希锚定，再看邻居 |
| **完整 8 字节** | 4 字节命中在 ~90 MB 高熵数据里**可能只是巧合** |
| **引用逐字读** | 一个字符不同 ⇒ fid 全变 ⇒ 必然 0 命中 |
| **修复带契约测试** | 改完必须验无回归 |

---

## 7. 本仓库不含什么（以及怎么重建）

| 缺的东西 | 重建方式 |
|---|---|
| 源包（45G） | 自备游戏客户端，路径 `E:\mrzh` |
| 还原树 | `toolkit_cli.py materialize`（先 `index build`） |
| 索引库 | `toolkit_cli.py index build` |
| 提取产物 | `toolkit_cli.py bulk <目标> --out <目录>` |
| 热更产物 | `toolkit_cli.py hotfix all` / `loose scan` |

> 全部产物都可由本仓库脚本从原始客户端重建 ⇒ 因此不入库，
> 仓库保持轻量（代码 + 页面 + 文档）。
