# pack 目标规格 —— weapon_skin 一套资产怎么落地

生成：2026-09-26 ｜ 方法：**只读**现场扫目录 + 读脚本 + 读既有报告；每个结论后面给路径。
本文只新建这一个文件，未改动任何其它文件（未跑 rebuild，未跑任何写脚本）。

---

## 0. 一句话结论

**历史上一套资产不是"一条 pack 命令"产出的，而是七八条一次性脚本 + 大量人工目视定案拼出来的。**
可机械化的是几何/贴图/cube/派生图/清单骨架；不可机械化的是**槽位归属的候选级裁决、姿势与相机的目视定案、缺资源的 fail-closed 登记**。
真正能封成 `pack` 的只有前半段 + 门禁；后半段必须留成**人工交接口**（§7.4）。

---

## 1. 事实基线（现场实测，2026-09-26）

| 事实 | 数字 | 来源 |
|---|---|---|
| `assets/3d/weapon_skin/` 下一级子目录 | **115** | `ls \| wc -l` |
| 其中 `_` 前缀（索引器跳过） | 3 → `_shared` / `_skeletons` / `_template` | `ls -d _*` |
| 含 `viewer.json` 的目录 | **38**（非 `_`）＋ `_template` 1 = **39 个 viewer.json 文件** | `*/viewer.json` 计数 |
| 只有 `model_white.glb`、无 `viewer.json` | **74** | 目录内容分类脚本 |
| 含 `model_white.glb` | 100 | 同上 |
| `neox_material.json` | 37（26 个 schema `neox_material/v1` + 11 个 `v2`） | 逐文件 `json.load` 统计 |
| `poster.webp` 11 ／ `model.glb` 10 ／ `dual.glb` 3 ／ `effects.json` 6 ／ `sfx/` 4 ／ `provenance.json` 4 ／ `src_tex/` 13 ／ `src_cube/` 13 ／ `texmap.json` 26 ／ `*.mesh` 26 | — | 同上 |

### ★ 1.1 硬门禁现状：`rebuild` 目前**跑不过去**（按代码推导，未实跑）

`04_站点/web/tools/rebuild_weapon_skin_media.py`：

* L31-33 `sorted(MODEL_ROOT.glob("*/viewer.json"))`，**只跳过 `_` 前缀目录** ⇒ `1110171_cand` 会被索引。
* L38-40：`skin_id` 重复即 `raise ValueError("重复 skin_id: …")`。
* L16-26 `validate_config`：`states[].model` 必须真实存在，否则 `FileNotFoundError`。

按此逻辑对 38 个目录静态复算（我用 Python 复刻了这三段判断，**没有执行 rebuild**）：

| 违规 | 目录 | 具体 |
|---|---|---|
| `FileNotFoundError` | `1110115` | `viewer.json.states[0].model = "skin_2003_013.glb"`，该文件**全库 `find` 0 命中**；目录里只有 `model_white.glb` |
| `FileNotFoundError` | `1110171_cand` | `states[1].model = "single.glb"` 不存在（只有 `dual.glb`） |
| `ValueError 重复 skin_id` | `1110171_cand` | 它的 `skin_id` 写的是 `"1110171"`，与 `1110171/` 撞 |

⇒ 当前能成功登记的只有 **36** 个。另：`00_治理/规范/前端交付要求.md` 写的"39/39 model 存在"**不准确**，实为 37/39（`_template` 的 `viewer.json` 声明 `dual.glb`/`single.glb`，而 `_template/` 里只有 `viewer.json`）。

---

## 2. 文件清单（每个文件是什么 / 必需性 / 从什么生成）

以 `assets/3d/weapon_skin/<skin_id>/` 为根。

| 文件 | 必需性 | 是什么 | 从什么生成 | 证据路径 |
|---|---|---|---|---|
| `viewer.json` | ★硬必需 | 查看器入参：形态/相机/背景/渲染开关/材质层/特效 | **无模板机**（见 §3.6）；`_template/viewer.json` 只是 1110171 的旧版拷贝 | `tools/rebuild_weapon_skin_media.py` L31（缺则不进索引）；`board.html` 按钮 |
| `<states[].model>` 指定的 `.glb` | ★硬必需 | 几何（可多形态：`dual.glb`+`single.glb`） | `export_glb.py`（源 `.mesh` 直出，见 §3.1a）或 `skin3d_pipeline.py` 白模（§3.1b） | `rebuild_weapon_skin_media.py` L25-26 |
| `neox_material.json` | ★真材质必需（缺则不崩但材质退回 GLB 自带） | 逐 prim 槽位绑定（唯一真源） | 手工 dict（`_build_t5/build_manifest.py`）或 `s25_write_manifest.py`；材料信息来自 `003996.c159` 之类 | `assets/3d/weapon_skin/1110177/neox_material.json` |
| `src_tex/*.png` | 条件必需 | 解码后的源贴图 + 派生重排图 | `dds_rgba_canonical.decode_dds_rgba_u8`（BC7→BGRA→RGBA，保 alpha）；派生图见 §3.3 | `1110177/_build_t5/build_assets.py` L40-94 |
| `src_cube/<name>.dds` + `src_cube/faces/<name>_f{0..5}_m0.png` | 条件必需 | 源 IBL 立方体及六面 | `cube_faces_export.py`（face-major 切法）；`build_assets.py` 里的 `decode_cube_legacy` 是同一规则的简化版 | `01_工具/工具库/06_皮肤定位链/cube_faces_export.py` 头注 |
| `poster.webp` | ○可选 | 卡片海报 | `tools/export_poster.py`（headless Chrome + CDP 截查看器本体，2260×1150） | `04_站点/web/tools/export_poster.py` L1-12 |
| `effects.json` + `sfx/` | ○可选 | 特效节点 + 特效 GLB/图集 | `parse_sfx_tracks.py`（`.sfx` GBK XML → 节点树）；贴图经 GPK 解包 | `06_皮肤定位链/parse_sfx_tracks.py` 头注；`1110177/sfx/` |
| `provenance.json` | ○可选（**诚实标注载体，勿删**） | 构建来源/近似项/unresolved 清单 | 手写或 `weapon_skin_pipeline.py` 的 `prov` 段（L594-634） | `1110177/provenance.json` |
| `texmap.json` | 构建期中间件（前端不读） | `{"sets":{...}}` → `export_glb.py` 的贴图入参 | 构建脚本顺手落盘 | `1110013/texmap.json` = `{"sets": {"skin_1006_002": {}}}`；`1110177/_build_t5/build_assets.py` L120-127 |
| `*.mesh` | 构建期中间件（前端不读） | 源网格原件，留档 | 源包解出后拷入 | `1110013/skin_1006_002.mesh` |
| `_build/` `_build_t5/` | 内部工作目录（`_` 开头不进索引） | 探针脚本/对照图/中间 JSON | 各专项作业 | `1110177/_build_t5/`、`1110165/_build/` |
| `*.variant_*.json` / `*.meta.json` | 实验支线，不进索引 | A/B 变体留档 | `mk_variant_1110025.py` 一类 | `1110025/viewer.variant_*.json` |

---

## 3. 生成链（逐产物追源）

### 3.1a 几何 GLB —— **源驱动链（当前唯一"真几何"路线）**

```
源包 .mesh（weapon.gpk 匿名条目）
   → mesh_parse2.parse_mesh2()            解头(14B)+sub表+tv/tf+bbox(6f)+pos/nrm/idx/uv
   → texmap.json（本地 PNG 路径，a/n/m 三槽）
   → export_glb.build_glb(mesh, texmap, set_names, out, label, center, submap)
   → <skin>.glb（POSITION/NORMAL/TEXCOORD_0 + 每子网格一 primitive，不导出 TANGENT）
```
证据：`01_工具/工具库/06_皮肤定位链/export_glb.py` L29 `def build_glb(...)` 与头注；
调用实例 `1110177/_build_t5/build_assets.py` L128-131（`EG.build_glb(MESH, tmp, ['…_blade','…_crystal'], glb, label=…, center=True, submap=['blade','crystal','crystal'])`）；
`1110025/_scripts/s25_build_glb.py` 全程。
`--submap` 是"子网格→材质集"的**显式指定**，不是按名推断（`1110177/_build_t5/build_assets.py` L136）。

### 3.1b 白模链 —— **100 个 `model_white.glb` 的真实来源**

两个脚本：`02_资料/源包/post_update_20260924_1610/skin3d_pipeline.py`（v1，353 行）与 `skin3d_batch.py`（v0，288 行）。
链路（pipeline 头注 L5-11）：
```
① skin_id → model_path     读 web/data/boards/weapon_skin_sfx_text_sources.json
② model_path → fid          murmur3 双 seed（0x77777777 / 0x66666666，反斜杠原样）
③ fid → 源行 → c159 定义帧  poff = row_off + gpk_payload_delta(块 base)
④ → BoundingInfo half       bbox 认领编译网格（rel < 0.02）
⑤ → 解析几何（复用 qj_geo.find_sub_table / parse_geo_bytes）
⑥ → 自写 export_glb()（纯 POSITION+TEXCOORD_0，固定 baseColorFactor [0.86,0.82,0.74]）
   输出 OUT / <skin_id> / "model_white.glb"
```
证据：`skin3d_pipeline.py` L283 `out = OUT / skin["skin_id"] / "model_white.glb"`；L34-38 的 `OUT = WIKI/"assets"/"3d"/"weapon_skin"`；L13 注释"118 个皮肤共用"。
**但它写的是重构前的路径**：`ROOT/03拆包产物/source_snapshots/...`、`ROOT/08Lifeafter wiki`、`ROOT/01拆包器本体/工具库`（L33-38）⇒ 5 区重构后**已失效**，只有 `E:\mrzh\Documents\gres` 这条源路径仍然有效（L50）。

### 3.2 src_tex（源贴图解码）

```
<idx>.dds（BC7/DX10 等）
  → dds_rgba_canonical.decode_dds_rgba_u8(path, verify_oiio=False)
     返回 (u8 RGBA, prov{width,height,fmt,mips,dds_sha256,canonical_pixel_sha256,decoder,applied_swizzle})
  → PIL 存 PNG（保 alpha，绝不 clamp/调色）
  → 落 src_tex/<fam>_<a|b_m|n|m|s_m>.png
```
证据：`01_工具/工具库/06_皮肤定位链/dds_rgba_canonical.py` L164 `def decode_dds_rgba_u8`；
命名与字段实例 `1110177/_build_t5/build_assets.py` L73-79；`1110025/_scripts/s25_build_tex.py` 全篇（含 `led['pngs'][…]['note']='BC7 解码后立即 BGRA->RGBA，alpha 原样保留'`）。
槽位角色（`skin_<dir>_<LOD><slot>.tga`）来自**材料 c159 的路径块**，见 §3.5。

### 3.3 派生图 param_repack / rough_repack

| 产物 | 公式 | 生成器 | 依据 |
|---|---|---|---|
| `param_repack_<fam>.png` | `R=255；G=round(255*clamp(src.R,0.02,1))（rough）；B=round(255*sat(src.G))（metal）；A=255` | **`gen_param_repack.py`（库内、可复跑）** | 头注：DXBC `metal=sat(ParamMap.G)`、`rough=clamp(ParamMap.R,0.02,1)`；three r180 读 `metalnessMap.B`/`roughnessMap.G` |
| `rough_repack_<fam>.png` | `R=255；G=src_a.alpha；B=255；A=255` | ⚠ **库内无生成器**；`gen_param_repack.py` 头注**明说不产它**。逐处是**一次性脚本**重写的 | `1110177/_build_t5/_t5_rule_check.json`（逐像素比规则）；`1110025/_scripts/s25_gen_repack.py`（`evidence_level='cross_skin_rule_7of8_exact_not_dxbc_proof'`）；`1110145/_build/REPACK_014_PROVENANCE.md` |

⚠ `param_repack_014.png` 的 B 通道 ≡1 却**无法由任何本地源图派生**（`1110145/_build/REPACK_014_PROVENANCE.md` §2）⇒ 该文件生成规则 **unresolved**。
⚠ `1110165` 的 `rough_repack` 走的是 `165_a.R` 分支（不是 `a.alpha`）⇒ 已降级 `approximate/unresolved`（`00_治理/文档/报告与复盘/皮肤渲染定位链_可复用流程_v1.md` §S5）。

### 3.4 src_cube（源 IBL 立方体）

```
common\env_map\<name>.cube（GPK 匿名条目，需按内容定位）
  → 拷成 src_cube/<name>.dds（legacy DDS, B8G8R8A8_UNORM, 128², 6 faces, mips=8）
  → cube_faces_export.py（face-major：面 i 的 mip 链起点 = 128 + i×87380）
  → src_cube/faces/<name>_f0..5_m0.png
```
证据：`06_皮肤定位链/cube_faces_export.py` 头注（含 mip-major 历史错切法的取证复现开关）；
`1110177/_build_t5/verify_rules.py` L29-58 `decode_cube_legacy` 与 1110171 既有面逐字节比对；
`1110177/_build_t5/_t5_rule_check.json` 的 `cube_qiangpi.all_equal`。
**只保证"面号↔字节偏移"正确，不主张朝向正确**（同文件头注）。六面必须互异，否则 viewer 报 `duplicate_face_urls_ibl`（`00_治理/文档/报告与复盘/交接_3D预览器_缝合指南_20260921.md` §4）。

### 3.5 neox_material.json

两条已知生成方式：

**(a) 手工 dict 直写** —— `1110177/_build_t5/build_manifest.py`（184 行）
把三个 prim 的 `textures{}` 逐槽写死，每个槽带 `logical_path / slot / local_file / sha256 / evidence / confidence / classification_rule / color_space`（L25-29 的 `def T(...)`），
`source{}` 记 bind/material/mesh 的 c159 名与 sha256（L109-112），
`slot_binding_basis{}` 写三重依据 A/B/C（L119-126）。
缺口资源一律 `def MISS(logical, slot)`（L32-37）→ `state:'missing'`、`confidence:'none'`、**不顶替**。

**(b) 半自动写** —— `1110025/_scripts/s25_write_manifest.py`（23 KB，同类）

**(c) 参数回填脚本**（后处理，不重建文件）
* `1110177/_build_t5/build_crystal_params.py`：把 `c159_029_pair.json` 的 per-material 参数块写成 `primitives[].crystal_params`，并**用 1110177 旧 viewer.json 的 `per_submesh` 交叉印证**角色归属（L46-64）。
* `1110177/_build_t5/build_fix.py`：把 `t_basecolor` 从渲染输入移到 `withheld_slots`（**不删源路径**，给 `restore_rule`），并把三组受控对照 D0b/D1/D2 的 blue/red/silver 占比写进 `binding_basis_summary.evidence`。

**(d) 上游素材清单** —— `06_皮肤定位链/build_material_manifest.py`：
```
parse_bind(绑定 c159) → submesh → MtlIdx → 绑定材质名      [evidence: high]
c159_pair.load_asset_materials → shader + 参数名/类型/值/字节偏移 [high]
material c159 字符串 → 贴图槽名 → 路径                    [heuristic]
mesh sub 表 → submesh → index_range / faces              [high]
```
每条边单独标 evidence（L122-132），并明确 `texture_paths='heuristic（槽名↔路径归属未直证）'`。
`06_皮肤定位链/apply_source_materials.py` 再把 manifest 的参数写进 `viewer.json.material_layers`（用法 L10）。

### 3.6 viewer.json —— **它是怎么造出来的**

**答：没有模板机。三条不同做法，全部带手工成分。**

| 批次 | 目录 | 时机 | 做法 |
|---|---|---|---|
| **甲：20 个"极简骨架"** | 1110013 1110021 1110022 1110031 1110032 1110036 1110116 1110117 1110121 1110128 1110131 1110132 1110133 1110142 1110143 1110144 1110146 1110151 1110159 1110160 1110161 1110173 1110174 1110175（＋1110115 / 1110137 邻近时刻） | **2026-09-18 21:51:39.6 → .9**（20 个文件 mtime 间隔 ~10 ms ⇒ **一次批处理循环**） | 只有 5 个键：`schema_version / skin_id / default_state / states[].{id:'single',label:'单件',model:'<skin_XXX_YYY>.glb'} / material_layers{status:'source_neutral', global_rig{env_intensity,exposure,tone_mapping:'NoToneMapping',emissive_gain:0,lights:0}}`。**见 `1110013/viewer.json`、`1110146/viewer.json`** |
| **乙：深度手搓** | 1110024 1110129 1110145 1110165（09-18 21:25:29 同一秒）、1110152 | 09-18 21:25 | 25-26 个键，含 `camera_presets[4]`、`camera_basis{eye,target,up0,roll_deg,basis}`、`pose_rule`、`pose_accepted_by`、`background_source{file,origin,sha16,usage}`、`material_layers.per_submesh`（晶体参数） |
| **丙：模板深拷贝 + 字段级替换** | **1110025** | 09-26 01:28 重生成 | `_target_1110025/_scripts/s25_write_viewer.py` L3 明写：**读 1110024 的 viewer.json 做深拷贝，只替换特有/无法沿用的字段** ⇒「字段级同构可机检」。L22-23 把 `rotation_note` 改成"**未做**用户目视姿势确认（模板值是 1110024 的用户结论，不适用本皮肤）」 |
| 丁：另起炉灶 | 1110169（09-15）、1110171_cand（09-17）、1110171（09-20）、1110177（09-17 建 / 09-26 改）、1110185+1110186（09-25） | — | 各专项脚本；1110185/1110186 见 §3.9 |

### 3.6.1 39 个 viewer.json 的"共同模板"是什么

**没有一份可机填的模板，只有一份"事实上的参照系" = `1110024/viewer.json`。**
* `_template/viewer.json` **不是模板**：它内容是 **1110171 的旧版**（`skin_id:"1110171"`、`states:[dual,single]`），mtime 2026-09-14 20:38（最早的 viewer.json）⇒ 它是历史遗留。
* 真正的复用证据是 `1110025/_scripts/s25_write_viewer.py`（深拷贝 1110024）与 `02_资料/源包/post_update_20260924_1610/zm_bg.py`（"照 1110024 口径"补背景）、`zn_cam.py`（对照 1110024 的 `game_reference` 是"用户实调值"）。
* **`pose_rule` / `camera_basis` / `rotation_note` 确实是人工目视定案的**：
  * `1110024/viewer.json`：`pose_rule = "用户定稿（2026-09-15）：正面相机 position=[-9,0,0] + rotation_degrees=[180,0,0]"`；`states[0].rotation_note = "按用户目视确认：正面相机需 +180°（绕视线轴）才与卡片同姿势"`；`camera_presets[0].basis = "用户实调参数（position/target/up/distance 原样保留）；左右转为世界竖直轴纯自转，up 随相机同步旋转以保持画面滚转恒定"`；`pose_accepted_by="游戏内参考图（用户提供 8bdf3a6f）"`。
  * `1110024/viewer.json` 的 `camera_basis.basis = "源渲染器 rig：eye=-X, up0=+Z, roll=90°（导出器 B=单位阵，故 B*vec=vec）"` ⇒ 数值可算，但 **"和卡片同姿势"这个判据只能人眼看**。
  * `1110186/1110185` 的 `pose_rule` 被 `zn_cam.py` 写成 **"未定稿：本皮肤无游戏内参考图，朝向 = GLB 原始导出（--center，未旋转）；未做用户目视姿势确认"**（`02_资料/源包/post_update_20260924_1610/zn_cam.py` L44）。
  * 而 `1110025` 的 `pose_rule` 是"项目统一展示 rig（6 款同组值）；1110024 的…**未在 1110025 上复核**"（`s25_write_viewer.py` L30-31）。

### 3.7 poster.webp

`04_站点/web/tools/export_poster.py`：headless Chrome（`--headless=new --enable-unsafe-swiftshader --remote-debugging-port=9831`）+ CDP
→ 加载 `board.html?...&view=wiki` → `WikiWeaponViewer.open(...)` → 切形态 → 覆盖 CSS 固定 2260×1150 → 复位视角 → 截图 → 写 `poster.webp`，并回写 `provenance.json`。
验收口径：`__state()` 的 `projCenter≈[0.5,0.5]` 且 `clipped=false`（L1-6）。
另有 `provenance.json.poster.{renderer,eye,roll,size,pose_preset}` 记录渲染参数（`1110177/provenance.json`）。

### 3.8 effects.json + sfx/

`06_皮肤定位链/parse_sfx_tracks.py`：`.sfx`（GBK XML `FxGroup`）→ 节点树（`name/tag/parent/pos_offset/start/life/radius/blend_mode/texture/color/scale/emit`），严格 `{"time":float,"value":[...]}` 结构。
`1110177/effects.json`（673 KB）与 `1110177/viewer.json.effects` 是**两份**，viewer 运行时读的是后者（`交接_3D预览器_缝合指南_20260921.md` §4/§6：`particle_radius_to_world` 只写在 effects.json 会导致整层不画）。

### 3.9 最后一步：登记（索引门禁）

```
cd 04_站点\web　&&　python tools/rebuild_weapon_skin_media.py
   → 读 assets/3d/weapon_skin/*/viewer.json（跳过 _ 前缀）
   → validate_config：states 非空 + 每形态 model 存在
   → 写 data/media/weapon_skin_media.json 与 .js（window.WEAPON_SKIN_MEDIA）
   → 打印 "weapon skin 3D index: N ready"
```
证据：`04_站点/web/tools/rebuild_weapon_skin_media.py` L16-68。
`preview_3d.status` 恒为 `ready`，另带 `material_fidelity`/`sfx_fidelity`（取自 `viewer.json.fidelity`，默认 `approximate`/`none`）。
另有后处理脚本 `02_资料/源包/post_update_20260924_1610/zl_ready.py`：把 `material_fidelity` 改成 `source_candidate` 并把长文证据写进 `fidelity_note`。

### 3.10 1110185 / 1110186（最近一次完整实操，最有参考价值）

顺序（脚本名即流水线）：`zf_wiki3d.py`（GLB+poster+viewer.json+登记）
→ `zj_build_mat.py <albedo_i> <mask_i> <normal_i>`（src_tex + neox_material.json + viewer.json）
→ `zp_paramrepack.py`（`param_repack_031.png`，**先拿 1110025 自校准：差异像素必须为 0，否则 `raise SystemExit(1)`**）
→ `zl_ready.py`（改 `weapon_skin_media.json` 状态 + `fidelity_note`）
→ `zm_bg.py`（补 `background_image`/`background_source`/`env_from_background`）
→ `zn_cam.py`（补 `camera_presets`/`default_camera`/`camera_basis`）。
全部在 `02_资料/源包/post_update_20260924_1610/`，**路径同为重构前（`08Lifeafter wiki` / `03拆包产物`）⇒ 现已失效**。

---

## 4. 字段结构（以真实文件为准）

### 4.1 `viewer.json`

**顶层键（39 个文件实测频次，括号＝出现次数）**

| 键 | 类型 | 次数 |
|---|---|---|
| `schema_version` | int | 39 |
| `skin_id` | str | 39 |
| `default_state` | str | 39 |
| `states` | list | 39 |
| `material_layers` | dict | 36 |
| `title` | str | 14 |
| `fidelity` | dict | 14 |
| `poster` | str\|null | 13 |
| `default_camera` | str | 13 |
| `camera_presets` | list | 13 |
| `background` | str(`#071015`) | 13 |
| `exposure` | float | 13 |
| `hemisphere_intensity` / `key_intensity` / `fill_intensity` / `env_intensity` | float | 各 12 |
| `pose_rule` | str | 12 |
| `background_image` / `background_source` / `env_from_background` | str/dict/bool | 各 12 |
| `effects` | dict | 11 |
| `camera_basis` | dict | 10 |
| `pose_accepted_by` | str | 10 |
| `_approx_was` / `_source_neutral_note` | dict / str | 各 8 |
| `cube_default_selection` / `source_chain` / `material_mapping` | dict | 各 3 |
| `position` / `environment_approximate` | list / bool | 各 2 |
| `lighting_approx` / `_fx_wiring_note` / `direct_light` / `direct_light_intensity` / `key_dir` / `_direct_light_note` / `note` / `unresolved` / `poster_note` / `state_for_pose` / `_t5` | 杂 | 各 1 |

**子结构**

* `states[]`：`id` `label` `model`（42 项）／`material_layers`（13）／**`rotation_note`（9）**／`geometry_source`（2）／`material_note`（1）
* `camera_presets[]`：`label` `position[3]` `target[3]` `fov`（44）／`id`（34）／`up[3]` `fit_span` `exact` `basis`（13）／`distance`（10）／`state`（9）
* `camera_basis`：`eye[3]` `target[3]` `up0[3]` `roll_deg` `basis`（`1110024/viewer.json`）
* `background_source`：`file` `origin` `sha16` `usage`（`1110024`）／`1110186` 版少了 `usage`
* `fidelity`：`material`(`approximate`/`source_matched`/`source_candidate`) `sfx`(`none`)；`1110171` 另有 `direct_light:"approximate_direct_lighting"`
* `material_layers`：`status`(36) `global_rig`(36) `basis` `material_level_source_factor` `not_yet_implemented`(各 10) `per_submesh` **`unoverridden_submeshes`** `notes` `crystal_submeshes` **`weapon_submeshes`** `other_submeshes` **`counts{weapon,crystal,other}`** `classification_basis`(各 8) `note`(2) `emissive_source`(1)
  * `global_rig`：`env_intensity` `exposure` `tone_mapping`(`NoToneMapping`/`ACESFilmic`) `note` `emissive_gain` `bloom{strength,radius,threshold,note}`
  * `per_submesh`：键为 submesh 序号的字符串；内含 `base_color` / `crystal_color` / `crystal_metallic` / `crystal_specular` / `cube_brightness` / `detail_intensity` / `detail_tilling` / `emissive_fresnel` / `emissive_strength` / `refraction_brightness` / `refraction_color` / `refraction_contrast` / `refraction_rotation` / `rotate_angle` / `subsurface_color` / `base_metallic` / `base_specular` / `caustic_brightness` / `caustic_depth` / `caustic_tilling`；**`_build_t5/build_manifest.py` L140-149 会把同一批键再补一份 `u_` 前缀版本**（viewer 读 `u_` 前缀）
* `effects`（`1110171`）：`schema` `note` `skin` `status` `status_reason` `frame_binding` `frame_evidence` `loop_seconds` `assets_base` `textures_dir` `color_format` `blend_mode_map` `attach` `texture_binding_status` `texture_selection` `sfx_source` `unsupported` `pending` `nodes` `model_field_patch` `model_texture_patch` `model_unit_scale` `model_unit_scale_basis` `bindings_review_20260920` `acceptance_grade` `lead_wiring_note`

> 前端只硬用到的键：`skin_id` / `states[].model` / `poster` / `fidelity`（`rebuild_weapon_skin_media.py` L17-52）、`effects`（`viewer.js:772`）、`material_layers`。其余是**诚实标注**，删了就丢证据。

### 4.2 `neox_material.json`（37 个文件实测）

**顶层键频次**：`schema` `skin`(37) ／ `primitives`(36) ／ `evidence_levels`(35) ／ `stem`(26) ／ `backend`(25) ／ `residuals`(25) ／ `block_rule`(10) ／ `source` `glb` `required_by_program_family` `slot_binding_basis`(各 9) ／ `geometry_glb_sha256`(8) ／ `parser_sha256`(6) ／ `observed_but_unbound`(6) ／ `declared_slots_union_ref`(5) ／ `display_name` `missing` `product_default_environment_cube`(各 3) ／ `cube_source` `render_note`(各 2) ／ `skeleton` `cube_default_override_20260921` `shader` `slots` `note` `src_provenance` `cube_declared_sets` `cube_unresolved` `unresolved` `param_repack` `naming_conflict` `source_level_facts` `_candidate` `crystal_params_crosscheck` `binding_basis_summary`(各 1)。
`schema` ∈ {`neox_material/v1`(26), `neox_material/v2`(11)}。

**`primitives[]` 键频次**（150 个 prim 合计）：`prim` `shader_kind` `textures`(150) ／ `shader`(62) ／ `mtl_idx` `material` `glb_material`(54) ／ `missing_required`(50) ／ `shader_kind_basis`(38) ／ `attribution`(31) ／ `GROUP_INDEX`(30) ／ `shader_kind_evidence` `shader_kind_source`(22) ／ `chain_material_raw`(17) ／ `crystal_params` `block_end` `n_paths`(14) ／ `missing`(10) ／ `source_uniforms`(9) ／ `group_size` `source_uniforms_provenance` `source_uniforms_note`(7) ／ `faces` `shader_declared_by_material_c159` `declared_slot_groups`(5) ／ `group_prefix` `t_custom_ibl`(4) ／ `unresolved_source_textures` `crystal_params_evidence` `crystal_params_basis` `withheld_slots` `binding_basis`(2) ／ `material_label_note`(1)。
`shader_kind` ∈ {`weapon`, `crystal`, `subsurface`, `unresolved`}。

**`textures{}` 槽位键频次**：`NormalMap` `Tex0` `t_custom_ibl`(150) ／ `t_basecolor`(148) ／ `ParamMap`(130) ／ `t_surfacemap`(129) ／ `t_caustic_tex` `t_refraction_tex` `DetailMap`(13) ／ `t_reflection_tex`(8) ／ `<unresolved>`(1)。
与前端白名单（10 槽，`00_治理/规范/前端交付要求.md` §三）**完全一致**。

**单个槽位对象字段频次**：`local_file`(150) ／ `status`(101) ／ `why`(96) ／ `binding_basis`(52) ／ `slot`(49) ／ `evidence_level`(47) ／ `logical_path` `confidence`(45) ／ `why_not_direct`(38) ／ `content_class`(32) ／ `evidence`(29) ／ `sha256`(22) ／ `color_space`(24) ／ `classification_rule`(17) …… 以及一大批带日期的一次性证据键（`ab_test_20260918` `user_decision` `changed_by` `bind_fix_20260919` `sha16_provenance_20260919` `rgba_basis_20260919` `round3_rule` `family_feature_mean_rgb` `POS_IN_GROUP` …）。
**前端真读的只有 `local_file`（+ `logical_path` / `faces_glob` / `faces` 用于 IBL）**；其余全是证据。

### 4.3 前端契约（不可回退的硬规则）

来自 `00_治理/规范/前端交付要求.md` + `assets/weapon_skin_viewer.js`：

1. `primitives[]` **必须与 GLB 里 mesh 的遍历顺序逐一对应**（`const mesh = meshes[i], pr = prims[i]`，`weapon_skin_viewer.js:1521-1523`）——**顺序错不报错，静默贴错子网格**。
2. 目录名逐字：`src_tex/` `src_cube/` `src_cube/faces/`。
3. `local_file` 解析：以 `src_tex/` 开头 → 原样；否则只有形如 `skin_1003_<3位>(001)?(a|b_m|n|m|s_m)` 会被自动映射；**其它命名必须写完整 `src_tex/...` 路径**（`weapon_skin_viewer.js:1525-1536` + `:1443-1447`）。
4. 判的是 **`local_file`，不是 `file`**（`weapon_skin_viewer.js` L895-906 做 `local_file → file` 归一化）。
5. IBL cube 路径**只信任以 `src_cube/` 开头**的写法；要指 `_shared/cubes/…` 必须写 `src_cube/../../…`（`交接_3D预览器_缝合指南_20260921.md` §4）。
6. `faces_glob` **只替换 `{...}` 占位符**；写 `f*` 这种通配会六面坍缩成同一 URL ⇒ 空 cube ⇒ 全黑。
7. fail-closed：必需槽缺失 ⇒ 不显示该材质，**不用 `||` 回退**。
8. `cube_default_selection.cube` **必须保持空串**，填名会打断 IBL。

---

## 5. 手工成分 vs 可计算

| 环节 | 可计算 | 人必须做的判断 |
|---|---|---|
| 几何 GLB | ✅ 全自动（`export_glb.py`） | LOD/变体选哪条 `.mesh`；`--submap` 子网格→材质集指定 |
| 白模 GLB | ✅ 全自动（`skin3d_pipeline.py`） | bbox 认领阈值（已有 `rel<0.02`，但"选中即对"仍靠人工复核） |
| src_tex 解码 | ✅ 全自动 | **槽位角色归属**（`_a` 是 Tex0 还是 t_basecolor）—— `ordered-1to1/candidate-high`，**不是直证**，conflict 必须人工保留不裁决 |
| param_repack | ✅ 全自动（库内有生成器） | 无（公式来自 DXBC） |
| rough_repack | ⚠ 规则可写死（7/8 一致） | **1110165 例外须人工裁决**；源公式未取得 DXBC 直证 ⇒ 只能标 `approximate` |
| cube 六面 | ✅ 全自动 | **朝向（面号↔±X/±Y/±Z）未定证**，不主张 |
| `neox_material.json` | 骨架可自动（`build_material_manifest.py`） | 每个槽的 `confidence` / `evidence_level` / `missing vs not_shipped` / `withheld_slots` 的口径 —— **全部人工** |
| `viewer.json` | `schema_version`/`skin_id`/`states[].model` 可自动 | **`pose_rule` / `camera_basis` / `rotation_note` / `pose_accepted_by` / `cube_default_selection` / `lighting_approx` / `_approx_was` / `enabled` 开关** —— 全是人工，且部分需**用户目视确认** |
| `poster.webp` | ✅ 可自动（headless Chrome） | 需先有已定案的姿势/相机 |
| `effects.json` | 节点树可自动 | 贴图 `name→物理条目` **unresolved 且禁止顶替**；Model 默认 OFF 的开关口径人工 |
| 登记 | ✅ 全自动 | 无（但见 §1.1 门禁现状） |

---

## 6. 找不到的东西（诚实清单）

| 目标 | 结论 | 我找过哪里 |
|---|---|---|
| **2026-09-18 21:51:39 那批 20 个 viewer.json 的生成脚本** | ❌ **库内不存在**（一次性脚本已不在，或已被 `_PRUNED_LAB_SCRIPTS_20260921.txt` 回收） | 见下 |
| `rough_repack` 的库内生成器 | ❌ 不存在（`gen_param_repack.py` 头注明说不产它） | 同上 |
| `param_repack_014.png` 的生成规则 | ❌ unresolved（B≡1 无法由本地源派生） | `1110145/_build/REPACK_014_PROVENANCE.md` 自述 |
| `skin3d_pipeline.py` / `skin3d_batch.py` 的可运行性 | ❌ 重构前路径，已失效 | L33-38 |

**找过的地方（逐条）**
1. `01_工具/工具库/06_皮肤定位链/`（全目录 + `_PRUNED_LAB_SCRIPTS_20260921.txt` 339 行 + `README_新增工具.md` + `使用说明.md`）
2. `02_资料/源包/post_update_20260924_1610/`（约 600 个脚本：`skin3d_pipeline.py` `skin3d_batch.py` `qiji_build.py` `zf_wiki3d.py` `zg_tex2.py` `zi_xc_batch.py` `zj_build_mat.py` `zl_ready.py` `zm_bg.py` `zn_cam.py` `zo_isolate.py` `zp_paramrepack.py` …）
3. `03_执行/30_分析/_target_1110025/_scripts/`（`s25_audit` `s25_blockrule` `s25_build_glb` `s25_build_tex` `s25_cmp1124` `s25_ddsfeat` `s25_gen_repack` `s25_inventory` `s25_write_manifest` `s25_write_viewer`）＋ `_target_1110025/` 顶层 462 项
4. `03_执行/30_分析/_target_1110171/`（`NAMES_*` `GLB171_export.py` `fidelity/FID_build.py` `AB_*` …）
5. `03_执行/90_临时/`（`脚本/` `旧临时存放/` `备份_5区重构前/` `备份_工具库_改路径前/` `_freeze_v1.2/`）
6. `04_站点/web/`（`tools/` 全部 ~150 个 py、`analysis/audit/`、`assets/3d/weapon_skin/*/_build*`、`assets/3d/weapon_skin/_shared/cubes/*/`、`board.html`、`assets/weapon_skin_viewer.js`）
7. `02_资料/交付/`（`交付_1110171_源驱动_20260916/neox_l1c.py` `neox_l2.py` `neox_l3coord.py` `neox_l3diag.py` `neox_srcchain.py`）
8. 全局检索（`search_files` + `grep -rl`）：`viewer.json` / `neox_material` / `pose_accepted_by` / `camera_basis` / `rotation_note` / `单件` / `source_neutral` / `ordered_1to1_candidate_high` / `evidence_levels` / `1110115` / `1110116` / `1110121` / `1110159` / `1110173` / `1110175` —— **除 viewer.json/neox_material.json 自身外 0 个"生成者"命中**
9. 非 git 仓库（`git log` → `fatal: not a git repository`）⇒ **无版本历史可回溯**

---

## 7. `pack` 命令目标规格（要做的那个东西）

### 7.1 命令形态

```
python 03_执行/<…>/pack_skin3d.py --skin <skin_id> \
      [--source-root <gres/res>] [--out <assets/3d/weapon_skin/<skin_id>>] \
      [--glb <mesh|白模>] [--states dual,single] [--skip-poster] \
      [--accept-readonly] [--write]
```
* 默认 **dry-run（只报清单与门禁结果，不写盘）**；`--write` 才落盘（沿用工具库既有约定，见 `README_新增工具.md` 通用约定）。
* 落盘前对目标目录按 `mtime + sha256` 备份（纪律第 4 条）。
* 退出码：`0` 全过 ／ `2` 缺源 ／ `3` 门禁不过 ／ `4` 写盘失败 ／ `5` 需要人工交接口未填。

### 7.2 步骤（每一步标注"自动/人工"）

| # | 步骤 | 产出 | 自动? |
|---|---|---|---|
| S0 | `skin_id → model_path → fid → 容器行`（murmur3 双 seed，反斜杠，latin1） | 源行台账 | ✅ |
| S1 | 解 `bind.c159` / `material.c159` / `.mesh` | 三件源 | ✅ |
| S2 | `build_material_manifest.py` → 子网格/MtlIdx/shader/参数/槽名/路径 + 逐边 evidence | `material_manifest.json` | ✅（路径归属标 `heuristic`） |
| S3 | `mesh_parse2` + `export_glb.build_glb(..., submap=…)` | `<states[].model>.glb` | ✅（`submap` 需人给） |
| S4 | 逐槽 DDS → `dds_rgba_canonical` → `src_tex/<fam>_{a,b_m,n,m,s_m}.png` | `src_tex/*.png` + 每张 `dds_sha256`/`canonical_pixel_sha256` | ✅ |
| S5 | `gen_param_repack` 公式 → `param_repack_<fam>.png`；`rough_repack` 按 §3.3 规则（**1110165 类例外必须人工裁决**） | 派生图 ×2 | ✅ / ⚠ |
| S6 | cube 定位 → `cube_faces_export.py --apply` | `src_cube/<name>.dds` + `faces/*_f{0..5}_m0.png` | ✅（朝向不主张） |
| S7 | 写 `neox_material.json` | 骨架自动 + **槽位 confidence/evidence/missing 人工** | ⚠ |
| S8 | 写 `viewer.json` | 骨架自动（照 `_template` 的**最小 5 键** + `default_state`）+ **相机/姿势人工** | ⚠ |
| S9 | `export_poster.py` | `poster.webp`（可选） | ✅（需 S8 定案） |
| S10 | `parse_sfx_tracks.py` + GPK 解包 | `effects.json` + `sfx/`（可选） | ✅ / 贴图 unresolved |
| S11 | 写 `provenance.json`（近似项 + unresolved 清单） | `provenance.json` | ✅（内容人工审） |
| S12 | `rebuild_weapon_skin_media.py` + 浏览器自检 | 登记 + `__neox()` 报告 | ✅ |

### 7.3 pack 自带的门禁（必须在写盘前全过）

1. `viewer.json` 存在且 `states` 非空、每形态 `model` 文件真实存在（复刻 `validate_config`）。
2. **`skin_id` 全库唯一**（防 `1110171_cand` 类撞车）。
3. 目录名 = 7 位数字（`_` 前缀目录一律不产出）。
4. `primitives[]` 数量 **==** GLB 里 mesh 的 primitive 数，且顺序对位。
5. 每 prim 按 program family 声明必需槽：`weapon → Tex0+ParamMap+NormalMap`；`crystal → Tex0+t_basecolor+NormalMap`；缺 ⇒ 该 prim 必须显式 `missing_required` 非空**或**记 `missing/withheld_slots`（fail-closed）。
6. 槽位名 ∈ 10 项白名单。
7. 每个 `textures[].local_file`：以 `src_tex/` 开头**且文件存在**；否则名字必须匹配 `skin_XXXX_YYY…` 自动映射规则。
8. `src_cube/faces/` 六面齐全、**六面 URL 互异**、`faces_glob` **不含 shell 通配**（`*`、`f*`）。
9. 派生图存在性与公式自校准（拿一个已知皮肤复算，差异像素必须为 0；照 `zp_paramrepack.py` 的做法）。
10. **无 `local_file: null` 出现在 family 必需槽**（除非该 prim 整体 fail-closed）。

### 7.4 必须保留的人工交接口（自动化到此为止）

| 交接口 | 谁定 | 落哪个字段 |
|---|---|---|
| 子网格 → 材质集 | 人（按源 c159 材质序） | `--submap` / `primitives[].glb_material` |
| 槽位角色归属与 `confidence` | 人（`ordered-1to1/candidate-high` 就是上限） | `textures[].confidence` / `evidence_level` / `binding_basis` |
| 缺资源登记（`missing` / `not_shipped` / `unresolved` / `withheld_slots`） | 人 | `missing_required` / `missing` / `withheld_slots` |
| 相机预设 + `pose_rule` + `rotation_note` + `pose_accepted_by` | **用户目视** | `camera_presets` / `camera_basis` / `states[].rotation_note` |
| 默认 Cube / 直接光强度 / `lighting_approx.enabled` | 用户授权 | `cube_default_selection`（**cube 名留空串**）/ `direct_light*` / `lighting_approx` |
| 保真度分级（`fidelity.material` / `material_layers.status` / `fidelity_note`） | 人 | `fidelity` |

### 7.5 pack 尚未具备、需要先补的工具

| 缺口 | 现状 |
|---|---|
| 源→行定位（新版路径） | `skin3d_pipeline.py` 逻辑可用但路径失效；需按 `03_执行/20_提取` + `E:\mrzh` 现状重接 |
| viewer.json 生成器 | **完全没有**。只有 §3.6 那三条一次性做法；需要新建（模板 = `_template` 的最小 5 键子集 + 从 `camera_presets` 台账填） |
| `rough_repack` 生成器 | 库内无；需把 §3.3 的规则收编进 `gen_param_repack.py` 或新脚本，并对 1110165 例外做显式裁决 |
| 全库唯一性 / 门禁自检脚本 | **完全没有**（正因如此 §1.1 那两个违规一直没被发现） |
| `poster.webp` 批量 | `export_poster.py` 只支持单皮肤（`sys.argv[1]`） |

---

## 8. 未解 / 风险（照实记）

| 项 | 状态 |
|---|---|
| `rebuild_weapon_skin_media.py` 当前因 `1110115` / `1110171_cand` 两个违规会中断 | ⚠ **未修**（本轮只读） |
| `前端交付要求.md` 的"39/39 model 存在"与实测 37/39 不符 | ⚠ 待更正 |
| `viewer.js:1540` 硬编码 `src_tex/gpk_1229.png`，该文件只在 `1110171`/`1110171_cand` 存在 ⇒ 其余 36 个皮肤每次载入 404 | `README_新增工具.md` 附节自述 |
| 8 个 `neox_material.json` 仍有 12 条不可消费的 `faces_glob`（`…_f{i}_m0.png` / `…_f*_m0.png`） | 同上 |
| cube 面号 ↔ 引擎 ±X/±Y/±Z 朝向 | 未定证 |
| `weapon\skin\*\textures\*.tga` 按名反查 **0 命中**（匿名 gpk）⇒ 贴图归属只能 `candidate-high`，**"按名 MISS ≠ 不存在"** | `README_新增工具.md` §1 已知边界 |
| `1110146` 骨块变体 mesh **布局未解**，`model.glb`/`viewer.json`/`neox_material.json` **不应生成**（现有 `viewer.json` 是"未注册"状态，且其 model 也不存在） | `1110146/_build/BLOCKED.md` §5/§2c.5 |
| `1110115` 只有 `.mesh` 没有 GLB、却带了 `viewer.json` | 本轮实测；成因未查（可能批次中断） |
| 水晶族 4 层（bump/reflection/refraction/caustic）采样关系 + crystal IBL cube | 未接入，全部标 `approximate` |
| `u_emissive_fresnel` / `u_emissive_strength` / `u_subsurface_color` / `u_refraction_color` / `u_cube_brightness` | 参数已落 manifest，**viewer 主链未消费**（`1110177/binding_basis_20260917.json` 的 `viewer_gap`） |
