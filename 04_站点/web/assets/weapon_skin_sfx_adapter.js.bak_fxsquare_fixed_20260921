/* 武器皮肤 SFX 网页适配器 v5（独立层·实验模式）—— 光影咏叹调 fx_skin_1003_010_zs_02.sfx
 *
 * 按 GPT 复核意见修正：
 *  · ColorFrame/ColorFramePar：源实测 69 帧**全部 4 分量**（{time,value} 结构）；4 分量顺序仍无证据 → 标 unproven
 *  · 粒子：按源 ParticlesPerSecond 出生、按 [MinSpriteLifespan,MaxSpriteLifespan] 存活、到寿死亡
 *    （不再固定 10 个 sprite 永久漂移）；Min>Max 的异常按原值顺序保留，不交换
 *  · FxIgnore=TRUE 的粒子节点默认禁用（5 个里 4 个）
 *  · .spr：规范解码实测 256x256 单帧（此前"256 帧精灵表"系我读错 DDS 头字段，已作废）→ 无翻页
 *  · 固定时间 + 固定种子 → 确定性重现（同一 (seed,t) 出同一张图）
 *  · 贴图仍是候选：仅在实验模式显示，标记 candidate
 */
(function () {
  'use strict';

  /* ★ FXADAPT Model 分支：GLTFLoader 与本文件的相对位置（脚本用 <script defer src="assets/weapon_skin_sfx_adapter.js"> 引入，
     故 document.currentScript 在加载期可拿到自身 URL；three addons 与 three 同源同实例）。 */
  var SELF_URL = (document.currentScript && document.currentScript.src) || null;
  /* ★ FXADAPT：defer 脚本下 `document.currentScript` 可能为空 ⇒ 多候选：
     ① currentScript ② 按 src 反查 <script> ③ 固定位置 assets/vendor/... ④ ../assets/... ⑤ vendor/... */
  var SELF_URL_SRC = 'document.currentScript';
  if (!SELF_URL) {
    try {
      var el = document.querySelector('script[src*="weapon_skin_sfx_adapter"]');
      if (el && el.src) { SELF_URL = el.src; SELF_URL_SRC = 'querySelector(script[src*])'; }
    } catch (e) { /* ignore */ }
  }
  var GLTF_LOADER_CANDIDATES = (function () {
    var out = [];
    try {
      var base = SELF_URL ? new URL('.', SELF_URL).href : null;
      if (base) out.push(base + 'vendor/three/addons/loaders/GLTFLoader.js');
    } catch (e) { /* ignore */ }
    out.push(abs('assets/vendor/three/addons/loaders/GLTFLoader.js'));
    out.push(abs('../assets/vendor/three/addons/loaders/GLTFLoader.js'));
    out.push(abs('vendor/three/addons/loaders/GLTFLoader.js'));
    var seen = {}; return out.filter(function (u) { return u && !seen[u] && (seen[u] = 1); });
  })();
  var GLTF_LOADER_URL = GLTF_LOADER_CANDIDATES[0];
  var LOADER_ERRORS = [];
  /* 调试/验证用：把模型基址指向别处（生产默认用 effects.json 的 model_fields.mesh，相对 manifestURL 解析）。
     例：WikiSfxAdapter.__modelsBase = 'http://127.0.0.1:10051/' */
  var MODELS_BASE_OVERRIDE = null;
  /* ★ FXADAPT fail-closed：Model（26 个 GLB）**默认关** —— 未调好的几何会盖住武器；
     只有 effects.models_enabled===true 或显式 WikiSfxAdapter.models(true) 才渲染。 */
  var MODELS_FORCE = null;      // null = 跟随 effects.models_enabled；true/false = 强制
  /* 默认材质：**源级**（MODEL_BLEND_K = null ⇒ 不加任何自造强度系数）
     · opacity = 源 u_emissivecolor 的**首分量 A**（已证 (A,R,G,B)） × 源 u_maintex*_opacity（缺失则 1.0，标 absent）
     · emissiveIntensity = 源 u_maintex*_brightness/100（0–100 百分比口径；缺失则回落源 u_emissive_highlight_intensity）
     仅 blending 选型（additive vs normal）无源字段 ⇒ 按三档实拍 A/B 选 additive，并在素材里标 approximate。 */
  var MODEL_BLEND = 'additive'; // 'normal' | 'additive'（源里 Model 无 blend_mode ⇒ 实拍选定，标 approximate）
  var MODEL_BLEND_K = null;     // null = 源级；显式数字 = 只为 A/B 对照的近似系数
  /* ★ task-61：源公式子集开关（renderer-auditor 反汇编 L409-415）——
     true（默认）= 自发光项按源公式带上 u_emissive_highlight_intensity（仅当该节点**有声明**）；
     false = 去掉该因子作 A/B 对照基线；未声明的因子(grey_intensity/mix/desaturate)一律**省略**、不中性顶替。 */
  var MODEL_HIGHLIGHT = true;
  /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20（本轮裁定，配置驱动）：**Model 的源级 fail-closed 门**。
     背景（1110025 实测，见 FIX_SFXFOLLOW_FINAL_20260920.md §2）：
       · 12 个 Model 节点在源里**没有可解析贴图**（`texture`/`texture_candidate` 全空、无 `Tex0` 绑定）；
       · 12/12 的 `ScaleFrame/XScale/YScale/ZScale` 全 `empty_in_source`（当前几何只靠常量回落 `SFX_UNIT_TO_MODEL`）；
       · 11 个 `sfx/*.glb` 材质一律 `MAT_fx`（baseColorFactor=[1,1,1,1]、metalness=1、roughness=1、无 emissive、OPAQUE）
         ⇒ 画出来是**无据的白/灰大板**（用户原话「sfx一开完全开始一坨占在那」）。
     规则：**只有数据侧显式声明** `effects.models_require_source_texture_and_scale === true` 时才生效；
     生效时，`src_texture` 与 `src_scale` **任一为 absent** 的 Model rec ⇒ 不加载、不绘制、state 显式记为
     `disabled_unresolved_source_texture_and_scale`（并把缺项写进 `fallback_reason`）。
     **缺省 false ⇒ 其它皮肤逐字沿用旧行为**（不设该字段即旧行为；1110152/1110171/1110177 均未设）。
     本门只"不画"，**不改任何强度/混合/颜色系数**；可取证通道见 `WikiSfxAdapter.models(true)` / `__modelIso()`。 */
  var MODEL_SRC_GATE_ON = false;   // attach 时由 effects.models_require_source_texture_and_scale 赋值
  var MODEL_SRC_GATE_STATE = 'off_default';
  /* ★ Lead 20260920：`.mtg` 源参数作为 Model 发光**取值来源**的开关（默认 OFF）。
     ON 时：`u_emissivecolor` → 发光色、`u_emissive_highlight_intensity` → 强度（**只改来源，不新增乘法**）。
     依据：`MTG_MODEL_MATERIAL_report.md`（42 节点逐条）+ `MTG_MATERIALS_20260919.json`（30/33 stem 有值）。
     ⚠ Model 层**无贴图直证**、GLB **无顶点色**（40/40 无 COLOR_0）⇒ 打开后是"白面片 → 源色面片"，**仍非成品外观**。 */
  var MTG_PARAMS_ON = false;
  /* ★ 枚举值表禁令（2026-09-18，chain-auditor；裁决③）：TransparentMode/RenderBias/DirType/BlendMode 的
     name↔int 值表在已扫范围内**不存在**（详见 modelBranchBasis.enumValueTable 与
     `03拆包产物\_target_1110171\FXENUM_probe_report.json`）
     ⇒ 本模块对它们的任何映射只能是 **approximate（观测分布，非值表）**；
     ★ **禁止用观测分布反推枚举名**（观测分布只能证明"哪些整数出现过"，不能证明"哪个整数叫什么"）。 */
  /* ★ task-53（用户实测「闪一下/一大块/很劣质」）精灵层修复开关与依据：
     · SPRITE_FIX：切片 + 尺寸钳制 + blend=7 保守默认；false 时逐字节退回旧行为
     · SPRITE_CLAMP_K：quad 世界边长上限 = 武器包围盒对角线 × K（null/false = 不钳制）。
       依据：武器 bbox 对角线实测 15.455（1110177，本轮 reg48_flash 基线），源 radius=4–6 且
       scale_track=[] ⇒ 旧行为把 radius 当渲染直径 ⇒ SFX 包围盒 70.71 = 武器 4.58×（"一大块"量化）。
       源 `radius` 语义仍 unresolved ⇒ 只做上限钳制，不改源值语义、不加任何人工强度系数。 */
  var SPRITE_FIX = true;
  /* task-53 靶子1：源 ParticleSystem 若无粒子速率（rate<=0）会被 updateParticles 早退 ⇒ 数据说可渲染、
     运行侧从不出现（改前实测 6/6 ParticleSystem 全时间轴缺席）。回退=按该节点自己的
     FxStartTime/FxLifeSpan + color_track + scale_track/radius 渲染**单个四边形**（不伪造出生率、不加强度系数）。 */
  var PS_SINGLE_QUAD = true;
  var CLAMP_ON = true;            /* 取证用开关：false = 关掉尺寸钳制（复现改前 4.58×） */
  var PS_FALLBACK_ON = true;
  /* ★ task-57（根因修复）：SFX 空间单位 = 厘米，模型空间 1 单位 ~ 1 分米 => SFX_UNIT_TO_MODEL = 0.1。
     该值由**5 条源长度证据推导**（非调参）：FarCull=800 / FarFade=600 / NearCull=0 => 8m/6m/0 才物理合理；
     DecalYMax=20 => 20cm；PosOffset 非零分量中位 0.47 / p90 8.55 / max 41.373；Radius=5..50 => 5..50cm；
     模型侧武器对角线 15.4552 单位 ~ 1.5m 剑 => 1 模型单位 ~ 1dm。凡 sfx 空间长度都必须乘本常量。 */
  var SFX_UNIT_TO_MODEL = 0.1;
  /* ★ Lead 20260920：**逐皮肤**的 Model 单位定标（数据驱动，缺省 = 上面那个由 1110171/1110177 长度证据推导的值）。
     依据（chain-auditor task-79 实测 bbox）：1110177 的 GLB 源空间是 **cm 量级**（bbox 13–163）⇒ ×0.1 正确；
     1110171 的 GLB 源空间已是 **m 量级**（bbox 0.46–3.43）⇒ 再 ×0.1 会多缩 10×（乘完 0.05–0.34 模型单位，肉眼不可见）。
     ⇒ 该值由 `effects.model_unit_scale` 提供（数据侧写清来源与 bbox 依据），缺省回落常量，**不是手调系数**。 */
  var MODEL_UNIT_SCALE = null;
  /* ★★★ 新增（2026-09-20，ENVWIRE·辉光流动第 ② 项）：**粒子半径的源→世界单位定标**（逐皮肤数据驱动）。
     为什么需要它（实测缺陷，非观感）：粒子 quad 世界边长 = `U(radius) * SpriteScale当前帧`，
     而 `U()` 用的是 **SFX 空间长度**换算 `SFX_UNIT_TO_MODEL=0.1`（那条 0.1 由 `FarCull=800`/
     `DecalYMax=20`/`PosOffset` 等**大尺度**字段的物理合理性推出，对它们是自洽的）。
     但**粒子半径不属于同一类量纲**：1110025 的 `PosOffset.z=7.491`、`Radius=0.15..0.30`——
     把 0.15..0.30 再乘 0.1 得 0.015..0.030 模型单位；相机 dist=14.886 / fov=34（≈88 px/单位）
     ⇒ **quad 仅 1.3–2.6 px**，`SpriteScale` 平均 ~1.2 ⇒ 仍然只有 2 px 量级
     ⇒ 实测 `M_鬼火_花瓣` 池内 2 个粒子全部在画、但**肉眼不可见**（`__sfxDiag` quad=0.02）。
     反解屏幕目标（对照 `REF_game_full_1280x720.png` 里花瓣/光点约为武器长度的 2–4%，
     武器对角线 9.0934 ⇒ 目标 world 0.18–0.36/SpriteScale）⇒ 与**源 radius 原值 0.15..0.30 直接对应**
     ⇒ 本皮肤的 `radius` 已是模型单位量级，**不应再乘 0.1**。
     修法：与 `model_unit_scale` 同一模式 —— **数据侧提供 + 带依据**，缺省回落 `SFX_UNIT_TO_MODEL`
     ⇒ 其它皮肤逐字不变；本皮肤在 `effects.json` 写 `particle_radius_to_world=1.0`。
     标注：该值是**由屏幕尺寸与源 PosOffset/Radius 的相对尺度反解**得到的（approximate），
     不是 c159 里的直证字段；且**不引入任何倍率**（1.0 = 不缩放）。
     A/B：`WikiSfxAdapter.particleUnit(k)` 可运行期改，供复核方复现 0.1 vs 1.0。 */
  var PARTICLE_RADIUS_TO_WORLD = null;
  /* ★ task-90 定证（依据 `03拆包产物/_target_1110171/FIDELITY_EVIDENCE_20260920.md` Q1）：
     ColorKeyFrame 四分量顺序 = **argb**（alpha=列0，RGB=列1..3）。判据（两皮肤全部节点，多键可判轨道 28+7 条）：
     ① RGB 色相跳变 argb 下 188.3°→**56.3°**（1110177）/ 315.0°→**147.1°**（1110171）；② alpha 端点恰为 0/255：
     列0 = **27/28 与 25/28**，列3 只有 4/28 与 7/28；③ 1110177 在 argb 下 RGB 聚在 **44°（金/琥珀）**，与源节点名
     `L_模型_顶黄 / L_模型_枪口黄 / M_模型_金线1` 一致（rgba 下聚 129° 绿）；④ 逐轨判定 argb **17:1**（1110177）/ **5:1**（1110171）。
     ⇒ 三条消费路径只有 argb 下才互相一致：**粒子路径 L742 原本就写死 argb（忽略本开关）**，精灵 L814 与模型 mdlRGB L226
     此前走 rgba，且模型层把列0 同时当 R 和 A（自相矛盾）。旧默认 'rgba' 的 task-58 推导已被上述定量判据推翻。 */
  var COLOR_ORDER = 'argb';
  /* ★ task-90 Q1 附带发现（事实级）：源 `.sfx` 的 `ColorFrame` 常是**编辑器默认单键**（两皮肤 22 个粒子节点全是同一值
     `(255,92,243,107)`），真实多键渐变在 `ColorFramePar`。1110177 的 28 条多键轨道里 **15 条在 `color_track_par`**，
     1110171 的 7 条**全部**在 par；而此前 adapter **只采样 `color_track`** ⇒ 这些节点画的是默认常数、不是 ramp。
     取值规则：par 非空 ⇒ 用 par，否则回 `color_track`。
     ⚠ `ColorFramePar` 的 "Par" 语义**未定证**（本机无文档）⇒ 本条＝事实驱动 + 强推断，开关 `colorTrackPar(false)` 一键回退。 */
  var COLOR_TRACK_PAR = true;
  function colorTrackOf(n) {
    if (COLOR_TRACK_PAR && n && n.color_track_par && n.color_track_par.length) return n.color_track_par;
    return (n && n.color_track) || [];
  }
  /* task-58 GO：粒子路径 .spr 帧矩形切片开关与取帧口径。
     · 帧索引按粒子自身 age/life 均匀取 = **implementation choice，非源直证**（CycleType/TimeLen 播放语义未定证）；
       若源语义日后定证，只需改 SPR_FRAME_MODE 的实现。 */
  var SPR_SLICE_ON = true;
  /* ★ Lead 20260920：**运动学 kinVel**（默认 ON）—— 删掉写死的位移放大系数。
     依据（renderer-auditor task-89 实测）：旧式 `drift = sys.vel * age * 20` 不经 `U()`，
     例 `H_p_烟雾_02`（源 minV/maxV = 5/15、life 0.20）⇒ `15*0.2*20 = 60` 模型单位
     = **武器对角线(6.882) 的 872%**，相对 cm/s 源式（0.10–0.30）**放大约 200×** —— 这是
     "开 sfx 就散成一团/一大块"的根因。ON 时改为**源式**：
       位移 s(t) = v0·t + ½·g·t² ，v0 取源 [MinSpriteVelocity, MaxSpriteVelocity]（按粒子出生随机取），
       g 取源 Gravity 帧；长度一律经既有 `U()`（与 `EmissionRadius` 同一范式、同一单位假设 cm/s）。
     无源值 ⇒ 该分量取 0（不猜）。OFF 分支**逐字保留旧表达式** ⇒ 默认态可比对。
     ⚠ `AccelForward` 是方向向量、模长语义未定证 ⇒ 不参与（登记在报告里）。 */
  var KIN_VEL = true;
  function kinFirst(n, key) {
    var t = n && n.emit && n.emit[key];
    if (!t || !t.length) return null;
    var row = t[0], v = row && row.value;
    var x = (v && v.length) ? Number(v[0]) : Number(row);
    return isFinite(x) ? x : null;
  }
  function kinV0(n, r) {
    var a = kinFirst(n, 'MinSpriteVelocityFrame'), b = kinFirst(n, 'MaxSpriteVelocityFrame');
    if (a === null && b === null) return null;
    var lo = (a === null) ? b : a, hi = (b === null) ? a : b;
    if (hi < lo) { var t = lo; lo = hi; hi = t; }   /* 源异常(Min>Max)按原值顺序，不交换语义 */
    return lo + (isFinite(r) ? r : 0.5) * (hi - lo);
  }
  function kinG(n) { var g = kinFirst(n, 'GravityFrame'); return (g === null) ? 0 : g; }
  /* ★ Lead 20260920：源 `.sfx` 的 `FxIgnore="TRUE"` = **该节点在源里被禁用**（证据：1110171 源里
     成对复制节点恰有一份 TRUE —— `L_模型_顶黄`(TRUE, ...zs_ql01) / `L_模型_顶黄_1`(FALSE, ...zs_02_pt)、
     `M_模型_五线谱`(TRUE, ql0101) / `_1`(FALSE, ql0102)、`H_星点粒子`(TRUE, rate5) / `_1`(FALSE, rate6)、
     `M_g_光晕暗_01`(TRUE) / `M_g_光晕亮_01`(FALSE) —— 两者除"变体/开关"外同源；且 1110177/daoguang 源里
     我们已验收渲染的 11 个节点**全部 FALSE**）。此前两把皮肤的 effects.json **完全没有搬 `fxIgnore` 字段**
     ⇒ 被禁用的节点照样在画。默认按源语义**尊重**该标志；开关供 A/B（若语义日后被否证，关掉即回到旧行为）。 */
  var HONOR_FXIGNORE = true;
  var SPR_FRAME_MODE = 'age';
  var colorOrderOf = function () { return COLOR_ORDER; };
  var UNIT_SCALE_ON = true;      /* 取证用开关：false = 关掉 ParticleSystem 单四边形回退（复现"6/6 缺席"） */
  var SPRITE_CLAMP_K = 0.60;
  var SPRITE_ON = null;          /* null = 跟随 SFX 总开关；true/false = 只控精灵/粒子层（负控用） */
  var BLEND7 = 'normal';         /* blend_mode=7：值表 NOT_FOUND ⇒ 保守默认 alpha（不走加法，避免未知贴图被加成白块）；标 unresolved */
  var LIVE_SFX = null;           /* attach 期间暴露 { sprites, systems, nodes, weaponDiag, slicedCount } 供只读探针 */
  var LIVE_CTX = null;           /* ★ FIX-SFXFOLLOW 2026-09-20：attach 时的 ctx（只读探针用，不参与渲染） */
  var DIAG_SCALE_K = 1;          /* ★ 只读取证：Model 几何缩放乘子，默认 1（生产恒为 1，见 WikiSfxAdapter.__scaleAll） */

  var LIVE_RECS = null;         // attach 期间登记的 model rec（供运行时开关/材质切换）
  var LIVE_API = null;          // ★ FIX-SFXFOLLOW-FINAL：attach 内部的只读探针（模块级挂点，见 attach 内注释）
  var LIVE_LOAD = null;         // ★ attach 时暴露的 loadModel，使 models(true) 能**当场加载**（不必重建查看器）
  var LIVE_APPLY = null;        // ★ attach 时暴露的 applyModelMaterial。模块层 modelMaterial() 原先直接调用 attach 内的局部
                                //   函数 ⇒ **每次都抛 26 次 ReferenceError**（被 catch 成 errors:26）；之所以"看着也生效"
                                //   是 tick() 每帧按模块变量重刷材质 —— 属侥幸生效，本版修掉并让 errors 归 0。

  /* ★ task-22：**源值桥**（1110152）。来源＝ `03拆包产物\_target_1110171\MODELTEX_1110152.json:q4_table`
     （xml_line 逐节点给出）+ 同族 `MODEL_src_values_1110152.json`（从源 XML 逐节点提取的
     u_overall_opacity / u_depth_bias / TransparentMode / RenderBias / TrackType / Tex0）。
     键 = `<ModelName 文件名>#<同 stem 出现序号>`（effects.json 的 Model 顺序 == 源 XML 顺序，已核对 ✓）。
     **运行时优先**：若 effects.json 里出现 transparent_mode/render_bias/u_overall_opacity_Keyframe/
     u_depth_bias_Keyframe，则用运行时值，本表自动让位（见 rec.srcBridge 的 bridge_source 字段）。 */
  var SRC_BRIDGE_1110152 = {
    "mod_skin_1012_009_zs_danxia_quan_hgz01_02.gim#1": { tm: "0", rb: "2", tt: "0", line: 727, op: 1.5, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_danxia_lg_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "4", line: 822, op: 3.0, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_qt_penqi_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 945, op: 1.0, db: 0.0, tex0: null },
    "mod_skin_1012_009_zs_qkqt_quan_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1040, op: 1.5, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_fw_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1135, op: 0.5, db: 1.0, tex0: null },
    "mod_skin_1012_009_zs_dianlu_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1230, op: 3.0, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_shujuliu_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1325, op: 1.0, db: 0.5, tex0: null },
    "mod_skin_1012_009_zs_shujuliu_raodong_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1468, op: 0.5, db: 0.5, tex0: null },
    "mod_skin_1012_009_zs_liuguang_hgz01_01.gim#1": { tm: "0", rb: "4", tt: "0", line: 1623, op: 5.0, db: 0.5, tex0: null },
    "mod_skin_1012_009_zs_shujuliu_glow_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1718, op: 1.0, db: 0.5, tex0: null },
    "mod_skin_1012_009_zs_shujuliu_hou_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1813, op: 1.0, db: 0.0, tex0: null },
    "mod_skin_1012_009_zs_shujuliu_hou_glow_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 1908, op: 1.0, db: 0.0, tex0: null },
    "mod_skin_1012_009_zs_piaodai_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "0", line: 2009, op: 1.0, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_piaodai_glow_hgz01_01.gim#1": { tm: "2", rb: "0", tt: "0", line: 2104, op: 0.5, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_piaodai_hgz01_02.gim#1": { tm: "0", rb: "2", tt: "0", line: 2199, op: 1.0, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_piaodai_hgz01_03.gim#1": { tm: "0", rb: "2", tt: "0", line: 2294, op: 1.0, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_piaodai_hgz01_03_pt.gim#1": { tm: "0", rb: "2", tt: "0", line: 2389, op: null, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_piaodai_glow_hgz01_02.gim#1": { tm: "2", rb: "0", tt: "0", line: 2449, op: 0.5, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_bagua_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "3", line: 2544, op: 1.0, db: 0.1, tex0: null },
    "mod_skin_1012_009_zs_dafazhen_hgz01_01.gim#1": { tm: "0", rb: "2", tt: "4", line: 2671, op: 1.0, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_dafazhen_hgz01_01.gim#2": { tm: "0", rb: "2", tt: "4", line: 2805, op: 1.0, db: 0.2, tex0: "effect\\textures\\ring\\tex_ring_fz01_x06.tga" },
    "mod_skin_1012_009_zs_dafazhen_hgz01_01.gim#3": { tm: "0", rb: "2", tt: "4", line: 2961, op: 1.0, db: 0.2, tex0: "effect\\textures\\ring\\tex_ring_keji_hgz01_04.tga" },
    "mod_skin_1012_009_zs_dafazhen_hgz01_02.gim#1": { tm: "0", rb: "2", tt: "4", line: 3117, op: 1.0, db: 0.2, tex0: null },
    "mod_skin_1012_009_zs_quan_lg_hgz01_01.gim#1": { tm: "0", rb: "1", tt: "0", line: 3255, op: 3.0, db: 0.3, tex0: null },
    "mod_skin_1012_009_zs_dafazhen_glow_hgz01_01.gim#1": { tm: "2", rb: "-1", tt: "0", line: 3350, op: 0.5, db: 0.3, tex0: null },
    "mod_skin_1012_009_zs_quan_lg_hgz01_01_pt.gim#1": { tm: "0", rb: "1", tt: "0", line: 3445, op: null, db: 0.3, tex0: null }
  };

  function abs(rel, base) { try { return new URL(rel, base || document.baseURI).href; } catch (e) { return rel; } }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function hash01(seed, i, salt) {
    var x = (seed * 73856093) ^ (i * 19349663) ^ (salt * 83492791);
    x = (x ^ (x >>> 13)) * 1274126177; x = x ^ (x >>> 16);
    return ((x >>> 0) % 100000) / 100000;
  }
  function sample(track, t, comps) {
    if (!track || !track.length) return null;
    var k = Math.max(0, Math.min(1, t));
    if (k <= track[0][0]) return track[0].slice(1);
    for (var i = 1; i < track.length; i++) {
      if (k <= track[i][0]) {
        var t0 = track[i - 1][0], t1 = track[i][0];
        var u = (t1 - t0) > 1e-6 ? (k - t0) / (t1 - t0) : 0;
        var a = track[i - 1].slice(1), b = track[i].slice(1);
        var n = Math.min(comps || a.length, a.length, b.length), out = [];
        for (var j = 0; j < n; j++) out.push(lerp(Number(a[j]) || 0, Number(b[j]) || 0, u));
        return out;
      }
    }
    return track[track.length - 1].slice(1);
  }
  /* 兼容三种结构：① 新 {time,value:[...]} 帧数组 ② 旧 [t,[v...]] ③ effects.json 的
     `model_fields.uniform_tracks.<name>_Keyframe` **包装对象** {attrib,n_frames,frames:[{time,value}]}。
     ★ Lead 20260920 缺陷修复（1110025 特效层「点了开关零像素」根因）：
       1110025 的 12 个 Model 节点轨道全部是 ③（实测 u_depth_bias_Keyframe = {attrib,n_frames,frames:[…]}），
       而旧 `flat()` 直接 `(track||[]).map(...)` ⇒ `TypeError: (track || []).map is not a function`
       在 `attach()` 的 `allNodes.forEach`（L471→L499 trackFirst(ut.u_depth_bias_Keyframe)）抛出，
       **整个 attach() 抛异常**（CDP Runtime.exceptionThrown 实证），于是 state.effectsHandle 恒为 null、
       特效层一行都不渲染、且没有任何 404（因为连贴图都没去取）。
       见 03拆包产物\_target_1110025\PROBE_fx_root_20260920.json。time 绝不并入 value。 */
  function flat(track) {
    var arr = Array.isArray(track) ? track
      : (track && Array.isArray(track.frames)) ? track.frames
        : [];
    return arr.map(function (f) {
      if (f && typeof f === 'object' && !Array.isArray(f) && 'time' in f) {
        var v = f.value; return [Number(f.time)].concat(Array.isArray(v) ? v : [v]);
      }
      var v2 = f[1]; return [f[0]].concat(Array.isArray(v2) ? v2 : [v2]);
    });
  }
  function first(track, dflt) { var v = sample(track, 0, 4); return v ? Number(v[0]) : dflt; }
  /* ★ task-22：取轨道在 t=0 的首个数值（用于 u_overall_opacity / u_depth_bias / u_emissive_highlight_intensity） */
  function trackFirst(track) {
    var f = flat(track);
    if (!f || !f.length) return null;
    var v = Number(f[0][1]);
    return isFinite(v) ? v : null;
  }
  /* ★ task-61：Model 源色（ColorKeyFrame，8bit）列序 —— **复用已独立 PASS 的 COLOR_ORDER**：
       'rgba'（默认，alpha 末位）⇒ 取列 0/1/2；'argb' ⇒ 取列 1/2/3。返回值归一到 0..1。
       U5 登记：1110152 时代 Model 路径曾写死 (A,R,G,B)；本皮肤按 lead 给出的 8bit RGBA 证据取 0..2，
       两说并存、由 colorOrder() 一处可切，待源级公式定证。 */
  function mdlRGB(col) {
    if (!col) return [1, 1, 1];
    var r, g, b;
    if (COLOR_ORDER === 'argb') { r = col[1]; g = col[2]; b = col[3]; }
    else { r = col[0]; g = col[1]; b = col[2]; }
    return [Number(r) / 255, Number(g) / 255, Number(b) / 255];
  }

  /* ★ FIX-SFXFOLLOW 2026-09-20：Model 的**源色**与**源不透明度**取值收敛到这两个纯函数，
     使「加载时初始化」与「每帧 tick」走**同一套口径**（旧代码两处不一致：加载时写死白/1）。
     · modelRGB(rec,u)：源 u_emissivecolor / u_diffuse_color 的 RGB（列序走模块级 COLOR_ORDER=argb）
     · modelOpacity(rec,u)：u_overall_opacity > AlphaMtl_Keyframe > ColorKeyFrame 列0(A)；
       量纲按 >1.5 判为 0..255 并 /255（AlphaMtl 是 0..1 浮点、ColorKeyframe 列是 0..255）。
     无源值 ⇒ 返回 {val:1, src:'no_source_opacity_unresolved'}（与旧行为一致，不猜）。 */
  function modelRGB(rec, u) {
    var col = sample(rec && rec.color, (u === undefined ? 0 : u), 4);
    return col ? mdlRGB(col) : [1, 1, 1];
  }
  function modelOpacity(rec, u) {
    if (!rec) return { val: 1, src: 'no_rec' };
    var opr = sample(rec.opTrack, (u === undefined ? 0 : u), 1);
    if (opr && rec.opacity_src) return { val: Number(opr[0]), src: 'source:u_overall_opacity' };
    var fb = (rec.opacityFallback && rec.opacityFallback.length)
               ? sample(rec.opacityFallback, (u === undefined ? 0 : u), 1) : null;
    if (fb && isFinite(Number(fb[0]))) {
      var a = Number(fb[0]);
      if (a > 1.5) a = a / 255;
      return { val: a, src: (rec.opTrack && rec.opTrack.length) ? 'source:u_overall_opacity(Keyframe)'
                    : ((rec.alphaMtlTrack && rec.alphaMtlTrack.length) ? 'source:AlphaMtl_Keyframe'
                                                                      : 'source:ColorKeyFrame_col0(A)') };
    }
    return { val: 1, src: 'no_source_opacity_unresolved' };
  }

  /* ★ task-53：blend_mode=7 原为「未收录 ⇒ 落 additive」，会把未知贴图加成整块发白。
     现显式取保守默认 alpha（BLEND7，可切回 'additive'）；**枚举值表仍 unresolved**（禁止用观测分布反推枚举名）。 */
  var BLEND = { 0: 'normal', 2: 'additive', 5: 'additive', 7: BLEND7, 8: 'additive' };
  /* ★ task-90 Q2 一致性修复：原写法 `BLEND[x] || 'additive'` 让**未收录的数值**（源里真实存在 `3` 与 `6`，分布 3 条与 3,083 条）
     落 additive，而 `7` 被特意保守为 normal —— 同一类"未知"两种默认。现：数值型未知 ⇒ `BLEND7`（保守，避免未知贴图被加成白块）；
     源**未声明** blend_mode（null/undefined）⇒ 沿用原 'additive'（本次不动，避免非本任务口径的行为漂移）。 */
  function blendOf(v) {
    if (v === null || v === undefined) return 'additive';
    var m = BLEND[v];
    return m ? m : BLEND7;
  }
  var ANCHOR_FALLBACK = [0, 0.66, 1.65];
  var MAX_PARTICLES = 200;          // 安全上限（源未给总量，只用速率×寿命约束）

  var WikiSfxAdapter = {
    attach: function (ctx) {
      var THREE = ctx && ctx.THREE, effects = (ctx && ctx.effects) || {};
      if (!THREE) return null;
      LIVE_CTX = ctx;                    /* ★ FIX-SFXFOLLOW 2026-09-20：只读探针取 THREE/root 用 */
      var allNodes = (effects.nodes || []);
      var nodes = allNodes.filter(function (n) { return n.texture_candidate; });
      if (!nodes.length) return null;

      /* ══════════════════════════════════════════════════════════════════════════════════════
         ★★★ 新增（2026-09-20，ENVWIRE·辉光流动第 ① 项）：**`.spr` 16 帧图集切帧（粒子路径）**。

         缺陷（实测，非推测）：
           `updateParticles()` 的切帧门是 `sys.node.spr_frames && sys.node.spr_frames.length`，
           而 `effects.json` 的节点**根本没有 `spr_frames` / `spr_sheet` 字段**
           （只有 `is_sprite_sheet`、`sprWorkMode`）⇒ 该门**恒不成立**
           ⇒ 实测 `__sfxDiag().particles[2]`：`sliced_frames=0 / sheet=null`
           ⇒ 16 帧 leaf 图集（`tex_leaf_huaban_hgz01_02__atlas206045.png`，256×256）
             **整张当单帧贴**，帧**从不推进** ⇒ 用户看到的"辉光流动"缺失。

         修法（**数据驱动、零猜值**）：就地为**声明了 `.spr` 的节点**解析它自己的 `.spr` 文本
           （源侧明文本描述符，`.spr` = 帧矩形表），把结果写回 `n.spr_frames` / `n.spr_sheet`，
           使既有切帧代码原样生效（不改它的算法）。
           · 帧矩形解析口径与 Sprite 分支**逐字一致**（第 3 行起、5 token、`.tga` 后缀）
             ⇒ 同一份 `.spr` 在两条路径得到同一组矩形；
           · 图集尺寸：head 有 w/h 就用 head，否则由帧矩形边界推 pow2（与 Sprite 分支同法）
             ⇒ 本份 max right/bottom=255 ⇒ **256×256**，与 `effects.json.atlas_provenance.atlas_dims`
               和 `.spr` 自身 4×4 平铺**自校验一致**；
           · 只对 `.spr` 后缀的 texture 生效；`dian_12.tga` / `tex_glow_dian_x04.tga` 两条
             **unresolved 贴图不做任何处理、不顶替**（它们的节点本来就 `renderable_by_adapter=false`）。
         标注：帧矩形本身来自**源 `.spr` 明文本**（source_verified 结构）；帧索引按粒子 age/life
           均匀取 = 既有 `implementation choice`（未改）。
         ══════════════════════════════════════════════════════════════════════════════════════ */
      var sprCache = {};
      function fetchSprFrames(node, onReady) {
        var fn = String(node.texture || '').split(/[\\/]/).pop();
        if (!/\.spr$/i.test(fn)) { onReady(null); return; }
        if (sprCache[fn]) { sprCache[fn].then(onReady); return; }
        sprCache[fn] = fetch(baseUrl + fn).then(function (r) { return r.ok ? r.text() : null; })
          .then(function (txt) {
            if (!txt) return null;
            var lines = txt.replace(/\r/g, '').split('\n').filter(function (x) { return x.trim(); });
            var head = lines[0].trim().split(/\s+/);
            var rects = [];
            for (var i = 3; i < lines.length; i++) {
              var q = lines[i].trim().split(/\s+/);
              if (q.length === 5 && /\.tga$/i.test(q[0])) rects.push([+q[1], +q[2], +q[3], +q[4]]);
            }
            if (!rects.length) return null;
            var hw = +head[1], hh = +head[2], basis = 'head[1],head[2] (source header)';
            if (!(hw > 0) || !(hh > 0)) {
              var mx = 0, my = 0;
              for (var k2 = 0; k2 < rects.length; k2++) {
                if (rects[k2][2] > mx) mx = rects[k2][2];
                if (rects[k2][3] > my) my = rects[k2][3];
              }
              hw = Math.pow(2, Math.ceil(Math.log2(mx + 1)));
              hh = Math.pow(2, Math.ceil(Math.log2(my + 1)));
              basis = 'derived_from_spr_frame_rects (max right/bottom=' + mx + '/' + my + ' ⇒ pow2 ' + hw + 'x' + hh + ')';
            }
            return { frames: rects, sheet: [hw, hh], basis: basis };
          }).catch(function () { return null; });
        sprCache[fn].then(onReady);
      }

      var loop = Number(effects.loop_seconds) || 2.0;
      /* ★ Lead 20260920：逐皮肤 Model 单位定标（数据侧提供 + 带 bbox 依据；缺省回落 SFX_UNIT_TO_MODEL） */
      MODEL_UNIT_SCALE = (typeof effects.model_unit_scale === 'number' && isFinite(effects.model_unit_scale))
        ? Number(effects.model_unit_scale) : null;
      /* ★★ 新增（2026-09-20，ENVWIRE）：粒子半径的源→世界定标（逐皮肤；缺省回落 SFX_UNIT_TO_MODEL
         ⇒ 未设该字段的皮肤**逐字不变**）。见文件头 PARTICLE_RADIUS_TO_WORLD 的推导与标注。 */
      PARTICLE_RADIUS_TO_WORLD = (typeof effects.particle_radius_to_world === 'number' && isFinite(effects.particle_radius_to_world))
        ? Number(effects.particle_radius_to_world) : null;
      /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：源级 fail-closed 门（配置驱动；未设该字段 = 旧行为，逐字不变） */
      MODEL_SRC_GATE_ON = (effects.models_require_source_texture_and_scale === true);
      MODEL_SRC_GATE_STATE = MODEL_SRC_GATE_ON ? 'on_by_source_config' : 'off_default(absent_in_effects_json)';
      /* ★ task-53 加固（lead/viewer-auditor 定位：effects.assets_base='sfx/tex/' + textures_dir='' 时
         `||` 会把空串再补一次默认值 ⇒ 'sfx/tex/sfx/tex/' ⇒ 5 条贴图 404 ⇒ SFX 什么都不画）。
         改为**显式 undefined/null 判定**：空串被如实保留（= 调用方明确不要该段）。 */
      var _ab = (effects.assets_base === undefined || effects.assets_base === null) ? '' : String(effects.assets_base);
      var _td = (effects.textures_dir === undefined || effects.textures_dir === null) ? 'sfx/tex/' : String(effects.textures_dir);
      var baseUrl = abs(_ab + _td, ctx.manifestUrl);
      var ANCHOR = (effects.attach && effects.attach.anchor) || ANCHOR_FALLBACK;
      /* ★ Lead 20260920 缺陷修复（COLORFIX 终验定位）：此处原有一行
             `var COLOR_ORDER = 'unproven:[A,R,G,B]';`
         **在 `attach()` 内遮蔽了模块级 `COLOR_ORDER`** ⇒ 精灵路径（tick 内 `=== 'rgba'` 判定）永远读不到真实列序、
         而 `WikiSfxAdapter.colorOrder()` 只改模块级 ⇒ **开关只改报告、不改画面**（实测：切 'argb'/'rgba' 帧 diff 0 px）。
         已删除该局部声明：精灵路径与模型路径现在**同读模块级 `COLOR_ORDER`**（默认 'argb'，见文件头定证注释）。
         模块级函数 `mdlRGB()` 一直在读模块级变量（不受此遮蔽影响）——终验报告里"mdlRGB 读局部值"一句据此更正。 */

      /* ★ 新增（2026-09-18，FXADAPT 审计）：源节点里适配器渲染不了的部分必须**显式暴露**，
         不允许用 sfxDiag 的 0 把它盖掉。
         1110152 实测：源 40 节点 = Sprite 4（本适配器渲染）· Model 26 · ParticleRes 4 · Dummy 6。
         归因（全部有证据，见 03拆包产物\_target_1110171\FXADAPT_missing_resources.json）：
           · Model(26)：源 .sfx 串池里确有 **ModelName** 字段与 26 条
             `effect\mesh\weapon\skin\skin_1012_009\mod_skin_1012_009_zs_*.gim`；但 .gim 本体
             全盘 0 命中（未解包），且工具库无 .gim→mesh 解析器 ⇒ **缺资产，不渲**（禁止占位几何）。
           · ParticleRes(4)：effects.json 里该类型 texture/emit/color 全空，只在源里引用子帧
             `fx_skin_1012_009_idle_part_01/02.sfx`（part_02 连源文件都缺）⇒ **缺参数，不渲**。 */
      var tagCount = {}, renderedCount = {};
      allNodes.forEach(function (n) {
        var tg = String(n.tag || '?');
        tagCount[tg] = (tagCount[tg] || 0) + 1;
        if (n.texture_candidate) renderedCount[tg] = (renderedCount[tg] || 0) + 1;
      });
      var notRendered = allNodes.filter(function (n) { return !n.texture_candidate; }).map(function (n) {
        var tg = String(n.tag || '?');
        var why = tg === 'Dummy' ? 'container_only'
          : tg === 'Model' ? 'needs_mesh_asset(.gim): 源有 ModelName 路径，但 .gim 未解包 + 无 .gim 解析器'
          : tg === 'ParticleRes' ? 'needs_params: effects.json 该节点 texture/emit/color 全空，仅引用子帧 .sfx'
          : 'no_texture_candidate';
        return { name: n.name, tag: tg, why: why };
      });

      var group = new THREE.Group(); group.name = 'sfx-layer';
      /* ★ FXADAPT Model 分支（2026-09-18，freeze-auditor 交付 24 个 per-model GLB）：
         Model 节点按 model_fields.mesh（= 'sfx/model/<stem>.glb'，相对 manifestURL）加载；
         GLB 挂到 group（group 在 scene 上、每帧抄 root.matrixWorld）⇒ **不进 root 包围盒**，不会重演"乱转"。
         颜色/发光/缩放全部取源轨道：uniform_tracks.u_emissivecolor_Keyframe（已证 (A,R,G,B)）、
         u_emissive_highlight_intensity_Keyframe、tracks.ScaleFrame / scale_XScale|YScale|ZScale。 */
      var modelRecs = [], modelCache = {}, gltfLoaderP = null, MODEL_STEM_SEEN = {};
      var MODELS_ON = (MODELS_FORCE === null) ? (effects.models_enabled === true) : !!MODELS_FORCE;
      LIVE_RECS = modelRecs; LIVE_LOAD = loadModel; LIVE_APPLY = applyModelMaterial;
      function getGLTFLoader() {
        if (!gltfLoaderP) {
          gltfLoaderP = (function tryAt(i) {
            if (i >= GLTF_LOADER_CANDIDATES.length) {
              LOADER_ERRORS.push({ stage: 'loader_import', tried: GLTF_LOADER_CANDIDATES.slice(), error: 'all candidates failed' });
              console.error('[sfx-adapter] GLTFLoader 全部候选加载失败:', GLTF_LOADER_CANDIDATES);
              return Promise.reject(new Error('no GLTFLoader'));
            }
            var url = GLTF_LOADER_CANDIDATES[i];
            return import(url).then(function (m) {
              GLTF_LOADER_URL = url;      /* 记录**实际**成功的 URL */
              return m.GLTFLoader || (m.default && m.default.GLTFLoader) || m.default;
            }).catch(function (e) {
              LOADER_ERRORS.push({ stage: 'loader_import_try', url: url, error: String((e && e.message) || e) });
              return tryAt(i + 1);
            });
          })(0);
        }
        return gltfLoaderP;
      }
      function stemOf(p) { return String(p || '').split(/[\\/]/).pop().replace(/\.gim$/i, ''); }
      function modelURL(rel) {
        if (MODELS_BASE_OVERRIDE) return MODELS_BASE_OVERRIDE.replace(/\/?$/, '/') + String(rel).split('/').pop();
        return abs(rel, ctx.manifestUrl);
      }
      function applyModelMaterial(m, rec, a, rgb, hiv) {
        if (!m) return;
        /* ★ task-22：无 Tex0 的 Model 走「无贴图自发光/叠加」分支 —— **不用白色 PBR 基色**。
           · color 置黑：消除 GLB 导出的白色 baseColor+metal/rough 在灯光下的白色贡献（这是"白块"的来源之一）
           · emissive = 源 u_emissivecolor 的 rgb（直读，不自拟）
           · 强度 = 1（中性恒等）：源 u_emissive_highlight_intensity 的语义是**高光项**，当作全局强度未证 ⇒ 不乘、留原值
           · opacity = 源 u_emissivecolor[0](A)/255 × 源 u_overall_opacity，clamp[0,1]（源值 >1 是增强，源公式未取到 ⇒ residual）
           · blending = 源 TransparentMode 直译（'0'→Normal，'2'→Additive；映射语义未在源中验证 ⇒ approximate）
           · depthWrite=false；polygonOffset 由源 u_depth_bias 驱动（单位语义未证 ⇒ approximate，原值记录在 probe） */
        /* ★ task-61 口径（族 = shader\uber_fx_common.fx 已定证；uniform 语义/公式 **unresolved** ⇒ 不做解释性运算）：
           · A 类（源有 u_emissivecolor / u_emissive_color）：emissive=源色、color 置黑、additive、depthWrite=false / depthTest=true；
           · B 类（源仅有 u_diffuse_color）：color=源色、emissive 置黑、normal、depthWrite=false / depthTest=true；
           · C 类（无颜色驱动）：不渲染（rec.state=disabled_no_color_driver，fallback_reason=no_color_driver_unresolved）；
           · opacity **只取源 u_overall_opacity**（无 ⇒ 1，探针 opacity_src=null）：不乘颜色 alpha、不乘任何强度系数；
           · u_emissive_highlight_intensity（含单帧 50）/ u_dissolve_amount / u_intensity / u_softparticle …
             = present_unwired：只在探针登记，**一律不进公式**。 */
        var isB = (rec.cls === 'B');
        if (m.color) { if (isB) m.color.setRGB(rgb[0], rgb[1], rgb[2]); else m.color.setRGB(0, 0, 0); }
        if (m.emissive) { if (isB) m.emissive.setRGB(0, 0, 0); else m.emissive.setRGB(rgb[0], rgb[1], rgb[2]); }
        if (m.metalness !== undefined) m.metalness = 0;
        if (m.roughness !== undefined) m.roughness = 1;
        var tm = (rec.mf && rec.mf.transparent_mode !== undefined && rec.mf.transparent_mode !== null)
                   ? String(rec.mf.transparent_mode)
                   : (rec.srcBridge && rec.srcBridge.tm !== null && rec.srcBridge.tm !== undefined ? String(rec.srcBridge.tm) : null);
        /* additive：B 类一律 normal；A 类按源 TransparentMode='2' ⇒ additive，否则随 MODEL_BLEND（'normal' 可强制关，供 A/B 对照）。
           ⚠ TransparentMode 枚举语义**未定证** ⇒ 此处只是「值→分支」的保守映射，枚举含义不上报为结论。 */
        /* ★ FIX-SFXFOLLOW 2026-09-20：**源属性优先**。
           优先级：rec.transparentModeSrc（源 XML 的 TransparentMode，直读）> srcBridge.tm（1110152 源值桥）> MODEL_BLEND。
           映射沿用既有 Sprite 口径：'0'→Normal、'2'→Additive（approximate：枚举值表仍 NOT_FOUND）。
           本皮肤 12/12 节点源值均为 '0' ⇒ 从"全局 additive"改为"源声明 normal"，
           消除多块大面片互相加成造成的白块；无该属性的调用方行为**逐字不变**。 */
        var tmSrc = (rec.transparentModeSrc !== undefined && rec.transparentModeSrc !== null)
                      ? String(rec.transparentModeSrc) : null;
        var additive;
        if (isB) { additive = false; }
        else if (tmSrc !== null) { additive = (tmSrc === '2'); rec.blend_src_used = 'source:TransparentMode=' + tmSrc; }
        else if (tm === '2') { additive = true; rec.blend_src_used = 'bridge:TransparentMode=2'; }
        else { additive = (MODEL_BLEND !== 'normal'); rec.blend_src_used = 'fallback:MODEL_BLEND=' + MODEL_BLEND; }
        m.blending = additive ? THREE.AdditiveBlending : THREE.NormalBlending;
        m.transparent = true; m.depthWrite = false; m.depthTest = true; m.side = THREE.DoubleSide;
        var k = (MODEL_BLEND_K === null || MODEL_BLEND_K === undefined) ? 1 : Number(MODEL_BLEND_K);
        var useOp = (rec.opacity_src !== null && rec.opacity_src !== undefined);
        m.opacity = Math.max(0, Math.min(1, (useOp ? a : 1) * k));   /* 缺源透明度 ⇒ 1（不猜 "opacity×alpha" 语义） */
        /* ★ task-61 源公式子集（renderer-auditor 反汇编 L409-415 / L425，槽位 cb0[3].xyz / cb0[24].x）：
           源式 r2=e*highlight ｜ r1=grey*grey_int - r2 ｜ r1=mix*r1+r2 ｜ r1=desaturate(lum(r1)) ｜ r1=r1*u_emissivecolor ｜ final=diffuse+r1。
           本实现**只带源有声明的因子**：u_emissivecolor（必带）+ u_emissive_highlight_intensity（有声明才乘，否则标 omitted_undeclared）；
           grey_intensity / mix / desaturate / mask_intensity / 贴图采样 e **未声明或不可得 ⇒ 整个子项省略**（不填中性值顶替）。
           ⚠ 子项 e(自发光贴图采样) 不可得（26/26 未绑贴图）⇒ 本项是源公式的 **子集/近似**，探针记 omitted_undeclared + approx_reason。
           emissiveIntensity 承载被乘的 highlight 因子；B 类恒 1（不伪造 emissive）。 */
        m.emissiveIntensity = (rec.cls === 'A') ? Math.max(0, Number(hiv) || 1) : 1;
        /* ★ task-61 修正（renderer-auditor 反汇编证据 2026-09-19，`RX_fx_family_formulas_20260919.md`）：
           `u_depth_bias` = cb0[26].z **在本族 shader 内 0 引用**（4 份 asm 全 [unused]）⇒ 属引擎渲染状态侧，
           **不得**当作 z 偏移 ⇒ 一律不启用 polygonOffset；源值只在探针以 present_unwired 登记（10/26 节点存在）。 */
        m.polygonOffset = false;
        m.needsUpdate = true;
      }
      /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：源级 fail-closed 门（**只在数据侧显式打开时生效**）。
         返回 true = 已按门禁处理（不加载、不绘制）。判据全是"源里有没有"，不做任何观感判断：
           · 源里没有可解析贴图（`texture`/`texture_candidate`/`Tex0` 绑定全无）
           · 且 源里没有缩放（`ScaleFrame`/`XScale`/`YScale`/`ZScale` 全空 ⇒ 几何大小只靠常量回落）
         两者同时成立 ⇒ 画出来只能是"无据的白/灰大板"（11 个 GLB 的 `MAT_fx` 材质 = 白基色 + metalness 1 + OPAQUE）。
         `models(true)`（取证通道）会把 `state` 保留为同一个显式标签，但允许加载、允许显示。 */
      function unresolvedSourceInputs(rec) {
        var out = [];
        var texAbsent = (rec.src_texture && rec.src_texture.state === 'absent_in_source');
        if (texAbsent) out.push('texture(no_source_texture_and_no_Tex0_binding)');
        /* 几何缩放 unresolved：源里可能**有**缩放轨道但适配器读不到（本门按"实际决定几何大小的是什么"判） */
        var scaleAbsent = !!(rec.src_scale && !rec.src_scale.wired_to_geometry);
        if (scaleAbsent) out.push('scale(geometry_scale_unresolved: source ScaleFrame not wired to geometry; '
                                  + 'size falls back to constant SFX_UNIT_TO_MODEL=0.1, not a source value)');
        if (!rec.color || !rec.color.length) out.push('color(no_color_driver_track)');
        return { list: out, tex_absent: texAbsent, scale_absent: scaleAbsent };
      }
      function srcGateBlocks(rec) {
        var u = unresolvedSourceInputs(rec);
        return { blocked: (u.tex_absent && u.scale_absent), unresolved: u };
      }
      function applySrcGate(rec, gate) {
        rec.src_gate_blocked = true;
        rec.fail_closed_source_gate = 'unresolved_then_disabled_source_gate'
          + (MODEL_SRC_GATE_ON ? '(on_by_source_config)' : '(off_default_legacy)')
          + '(honest_fallback_used_for_size=' + (gate.unresolved.scale_absent ? 'SFX_UNIT_TO_MODEL_constant' : 'none') + ')';
        if (MODEL_SRC_GATE_ON) {
          rec.state = 'disabled_unresolved_source_texture_and_scale';
          rec.fallback_reason = gate.unresolved.list.join('+');
        } else if (rec.color && rec.color.length) {
          /* 门禁关（旧行为）：颜色驱动决定加载；尺寸仍靠常量回落。state 与旧版语义一致，只是不再"不画却说 ok"。 */
          if (gate.unresolved.scale_absent) {
            rec.state = 'disabled_source_gate_off_scale_absent';
            rec.fallback_reason = 'scale empty_in_source; gate off by config(honest_label_only)';
          } else {
            rec.state = 'disabled_texture_unresolved'; rec.fallback_reason = 'texture_unresolved';
          }
        } else {
          rec.state = 'disabled_no_color_source'; rec.fallback_reason = 'no_color_source';
        }
      }
      function attachModel(rec, ent) {
        if (!ent || ent.state !== 'ok' || !ent.scene) { rec.state = (ent && ent.state) || 'fail'; return; }
        var obj = ent.scene.clone(true);
        /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 B「一坨白色巨块」的**第三根因，也是最直接的那个**）：
           旧代码对刚挂上的材质调用 `applyModelMaterial(o.material, rec, 1, [1,1,1], 1)`
           —— **写死 rgb=[1,1,1]（纯白）**。于是材质初值是「color=白 / emissive=白×强度1」，
           真正的源色只在 `tick()` 里、且只有当该 rec 通过 `visible` 门之后才会被写回。
           实测（isolation 截图 + `__modelDiag().mat_on_attach`）：大面片在加载后到 tick 生效前
           一直以**纯白**渲染；任何 tick 未覆盖到的时刻/记录都会停在白块上。这就是用户看到的大白板。
           修法：加载时就用**源值**初始化 —— 颜色取源 `u_diffuse_color`（本皮肤 12/12 Model 均为 B 类，
           走 mdlRGB 的 argb 列 1..3），alpha 取与 tick 完全同一套口径 `modelOpacity()`（见下），
           不再传白、不再传 1。 */
        var a0 = modelOpacity(rec, 0).val;
        var rgb0 = modelRGB(rec, 0);
        obj.traverse(function (o) {
          if (!o.isMesh && !o.isPoints) return;
          o.material = o.material ? o.material.clone() : new THREE.MeshBasicMaterial();
          o.renderOrder = rec.renderOrder; o.frustumCulled = false;
          applyModelMaterial(o.material, rec, a0, rgb0, 1);
        });
        /* ★ FIX-SFXFOLLOW 2026-09-20：把**加载时**已落盘的材质读数快照记下（与每帧 tick 无关）⇒ 探针可直读 */
        (function () {
          var m0 = null;
          obj.traverse(function (o) { if (!m0 && o.material) m0 = o.material; });
          if (m0) rec.mat_on_attach = { blending: m0.blending, opacity: +(+m0.opacity).toFixed(4),
                                        color: m0.color ? m0.color.getHexString() : null,
                                        emissive: m0.emissive ? m0.emissive.getHexString() : null,
                                        emissiveIntensity: (m0.emissiveIntensity === undefined ? null : +m0.emissiveIntensity.toFixed(4)),
                                        transparent: !!m0.transparent, depthWrite: !!m0.depthWrite,
                                        blend_src_used: rec.blend_src_used || null };
        })();
        rec.obj = obj;
        /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：取证强制加载时**不把 state 改回 'ok'** —— 门禁记录的 state
           恒为显式 `disabled_unresolved_source_texture_and_scale`（验收直读；它是"源不足所以默认不画"的事实，
           与"这一次被人工强制加载过"是两件事，后者记在 `forced_evidence_load`）。
           非门禁记录逐字沿用旧行为 `rec.state='ok'`。 */
        if (rec.src_gate_blocked) {
          rec.forced_evidence_load = true;
          rec.state = 'disabled_unresolved_source_texture_and_scale';
        } else {
          rec.state = 'ok';
        }
        rec.group.add(obj);
      }
      function measureModel(rec) {
        if (!rec.obj) return null;
        var box = new THREE.Box3().setFromObject(rec.obj);
        if (box.isEmpty()) return null;
        var sz = box.getSize(new THREE.Vector3()), ctr = box.getCenter(new THREE.Vector3());
        return { size: [+sz.x.toFixed(4), +sz.y.toFixed(4), +sz.z.toFixed(4)],
                 center: [+ctr.x.toFixed(4), +ctr.y.toFixed(4), +ctr.z.toFixed(4)],
                 groupScale: +rec.group.scale.x.toFixed(4) };
      }
      function loadModel(rec) {
        if (!rec.meshRel) { rec.state = 'no_mesh_field'; return; }
        var hit = modelCache[rec.meshRel];
        if (hit) {
          if (hit.state === 'ok') { attachModel(rec, hit); }
          else { (hit.waiters = hit.waiters || []).push(rec); rec.state = hit.state; }   /* ★ 同 stem 多节点：等首个加载完再一起挂 */
          return;
        }
        modelCache[rec.meshRel] = { state: 'loading', waiters: [rec] };
        rec.state = 'loading';
        var url = modelURL(rec.meshRel);
        getGLTFLoader().then(function (GLTFLoader) {
          new GLTFLoader().load(url, function (gltf) {
            var prev = modelCache[rec.meshRel] || {};
            var ent = { state: 'ok', scene: gltf.scene, waiters: prev.waiters || [] };   /* ★ 必须把 waiters 带过来，否则同 stem 的后续节点永久停在 loading */
            modelCache[rec.meshRel] = ent;
            ent.waiters.forEach(function (r) { attachModel(r, ent); });
            if (rec.state !== 'ok') attachModel(rec, ent);
          }, undefined, function (e) {
            var ent = { state: 'load_fail', url: url, error: String((e && e.message) || e || 'HTTP error') };
            modelCache[rec.meshRel] = ent;
            LOADER_ERRORS.push({ stage: 'glb_load', url: url, error: ent.error });
            console.error('[sfx-adapter] GLB 加载失败(不静默):', url, ent.error);
            (ent.waiters || []).forEach(function (r) { r.state = 'load_fail'; });
          });
        }).catch(function (e) { rec.state = 'no_loader'; LOADER_ERRORS.push({ stage: 'loader_import', error: String((e && e.message) || e) }); });
      }
      var disposed = false, enabled = true, raf = 0, t0 = performance.now();
      var fixedTime = null, rngSeed = 1;
      var sprites = [], systems = [], texCache = {};

      /* ★ task-53：武器包围盒对角线（缓存 500ms）+ quad 上限钳制（只做上限，不改源值语义） */
      var _wd = { t: -1e9, diag: 0 };
      function weaponDiag() {
        var nowms = performance.now();
        if (nowms - _wd.t > 500) {
          _wd.t = nowms;
          try {
            var b = new THREE.Box3().setFromObject(ctx.root);
            if (!b.isEmpty()) { var s = b.getSize(new THREE.Vector3()); _wd.diag = s.length(); }
          } catch (e) { }
        }
        return _wd.diag;
      }
      /* task-57：sfx 空间长度 -> 模型单位（唯一换算入口） */
      function U(v) { return UNIT_SCALE_ON ? (Number(v) * SFX_UNIT_TO_MODEL) : Number(v); }
  /* ★★ 新增（2026-09-20，ENVWIRE）：**粒子半径**专用定标（与 U() 分开，理由见函数头注释）。
     缺省 = SFX_UNIT_TO_MODEL（⇒ 其它皮肤逐字不变）；数据侧设了 particle_radius_to_world 就用它。 */
  function UR(v) {
    var k = UNIT_SCALE_ON
      ? ((PARTICLE_RADIUS_TO_WORLD !== null && isFinite(PARTICLE_RADIUS_TO_WORLD)) ? PARTICLE_RADIUS_TO_WORLD : SFX_UNIT_TO_MODEL)
      : 1;
    return Number(v) * k;
  }

      function clampQuad(raw) {
        var k = (SPRITE_FIX && SPRITE_CLAMP_K && CLAMP_ON) ? Number(SPRITE_CLAMP_K) : 0;
        if (!k || !raw || !isFinite(raw)) return { v: raw, clamped: false, cap: null };
        var cap = weaponDiag() * k;
        if (!isFinite(cap) || cap <= 0) return { v: raw, clamped: false, cap: null };
        return { v: Math.min(raw, cap), clamped: raw > cap, cap: cap };
      }

      function texFor(n, onReady) {
        var url = baseUrl + String(n.texture_candidate).replace(/\.dds$/, '.png');
        if (texCache[url]) { onReady(texCache[url]); return; }
        new THREE.TextureLoader().load(url, function (tex) {
          if (disposed) { tex.dispose(); return; }
          tex.colorSpace = THREE.SRGBColorSpace; texCache[url] = tex; onReady(tex);
        }, undefined, function () { onReady(null); });
      }

      allNodes.forEach(function (n) {
        var ignored = String(n.fxIgnore).toUpperCase() === 'TRUE';
        var isPS = /^Particle/i.test(String(n.tag || ''));   /* ★ FXADAPT：源里粒子节点是 ParticleRes（本皮肤无 ParticleSystem） */
        var blendMode = blendOf(n.blend_mode);
        var blendConst = blendMode === 'additive' ? THREE.AdditiveBlending : THREE.NormalBlending;
        var off = n.pos_offset || [0, 0, 0];
        /* task-57：anchor 与 pos_offset 都是 sfx 空间长度 => 统一乘 SFX_UNIT_TO_MODEL */
        var basePos = [U(ANCHOR[0]) + U(off[0]), U(ANCHOR[1]) + U(off[1]), U(ANCHOR[2]) + U(off[2])];

        /* ★ FXADAPT：Model 节点（26 个）→ 按 model_fields.mesh 加载 GLB；无 mesh 字段则如实标缺。
           **fail-closed**：默认关（effects.models_enabled 未 true 时不加载/不显示）——未调好的几何会盖住武器。 */
        if (String(n.tag || '') === 'Model') {
          var mf = n.model_fields || {};
          /* ★ task-61 修复（实测发现）：ModelName / glb 实际在**节点级**（`n.model_name` = 源 .gim 路径、`n.model_glb` = 'sfx/<stem>.glb'），
             而 `mf.ModelName` / `mf.mesh` 在本 effects.json 里 0/26 存在 ⇒ 旧写法使 26/26 全落 `no_mesh_field`（models(true) 一个都不加载、8 帧逐字节相同）。 */
          var mname = mf.ModelName || mf.model_name || n.model_name || null;
          var g = new THREE.Group(); g.name = 'sfx-model:' + n.name;
          g.position.set(basePos[0], basePos[1], basePos[2]);
          group.add(g);
          var ut = (mf.uniform_tracks || {});
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**源级可解析性**（只读登记，供 fail-closed 门与探针直读）。
             判据全部是"源里有没有"，不是"像不像"：
               · src_texture：`n.texture` / `n.texture_candidate` / 源 `Tex0` 绑定 —— 三者皆无 ⇒ 'absent_in_source'；
               · src_scale：`ScaleFrame` 或 `XScale/YScale/ZScale` 至少一条非空 ⇒ 'present_in_source'，否则 'empty_in_source'；
               · src_color：有任一颜色驱动轨道（与 rec.cls 的 A/B/C 分类同源）⇒ 'present_in_source'。 */
          function srcTexState(nn, br) {
            if (nn.texture || nn.texture_candidate) {
              return { state: 'present_in_source', value: String(nn.texture_candidate || nn.texture) };
            }
            if (br && br.tex0) return { state: 'present_in_source_binding_only', value: String(br.tex0) };
            return { state: 'absent_in_source', value: null };
          }
          function srcScaleState(nn, tr) {
            var keys = ['ScaleFrame', 'XScale', 'YScale', 'ZScale', 'TrackScale/XScale', 'TrackScale/YScale', 'TrackScale/ZScale'];
            var hit = [];
            /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20（核查更正）：缩放轨道在**三层**都可能存在三处不同落点 ——
               `mf.tracks`（1110152/1110171）、节点级 `tracks_all`（1110025/1110177）、以及源 `scale_track`。
               旧登记口径只读 `mf.tracks` ⇒ 对 1110025 会误报"源里没有缩放"，而 1110025 的 12/12 节点
               `tracks_all.ScaleFrame` 其实**有值**（实测 frames=[{time,value:[1.0]}]）——
               **源里有，但适配器的几何分支从不读这一层**（tick 只读 `mf.tracks.scale_*`/`ScaleFrame`）⇒ 几何大小
               实际只由常量回落 `SFX_UNIT_TO_MODEL` 决定。故本条如实记为"**几何缩放未接线（unresolved）**"，
               **不写成"源里缺失"**。挂 `scale_face` 记录读数来自哪一层与实测首帧值。 */
            var scan = [];
            scan.push({ face: 'model_fields.tracks', obj: (tr || {}) });
            scan.push({ face: 'node.tracks_all', obj: ((nn && nn.tracks_all) || {}) });
            scan.push({ face: 'node.scale_track', obj: null });
            scan.forEach(function (f) {
              keys.forEach(function (kk) {
                var v;
                if (f.obj) v = flat(f.obj[kk]);
                else v = flat((nn && nn.scale_track) || null);
                if (v && v.length && hit.indexOf(kk) < 0) { hit.push(kk); f.hit = (f.hit || 0) + 1; }
              });
            });
            var faceObj = ((nn && nn.tracks_all) || {}).ScaleFrame || (tr || {}).ScaleFrame || null;
            var firstVal = null;
            try {
              var ff = flat(faceObj);
              firstVal = (ff && ff.length) ? ff[0].slice(1) : null;
            } catch (e) { firstVal = null; }
            var wired = !!(tr && (tr.ScaleFrame || tr.XScale || tr.YScale || tr.ZScale));
            return { state: hit.length ? 'present_in_source_not_wired_to_geometry' : 'empty_in_source',
                     tracks: hit, wired_to_geometry: wired,
                     geometry_scale_source: wired ? 'model_fields.tracks(源值)' : 'constant_fallback:SFX_UNIT_TO_MODEL=0.1(非源值)',
                     scale_face: hit.length ? 'tracks_all/node_level(适配器未读)' : null,
                     first_frame_value: firstVal };
          }
          /* ★ task-22：源属性/源均匀量的运行时优先读取；effects.json 尚无这些字段时回落到
             SRC_BRIDGE_1110152（逐节点源值桥，含 xml 行号，见文件顶部常量区；一旦 env-auditor 把它们
             写进 effects.json，运行时字段优先、桥自动让位）。 */
          var bridge = {
            tm: (mf.transparent_mode !== undefined && mf.transparent_mode !== null) ? mf.transparent_mode : null,
            rb: (mf.render_bias !== undefined && mf.render_bias !== null) ? mf.render_bias : null,
            tt: (mf.track_type !== undefined && mf.track_type !== null) ? mf.track_type : null,
            op: trackFirst(ut.u_overall_opacity_Keyframe),
            db: trackFirst(ut.u_depth_bias_Keyframe),
            hi: trackFirst(ut.u_emissive_highlight_intensity_Keyframe),
            tex0: (mf.texture_binding && mf.texture_binding.Tex0) ? mf.texture_binding.Tex0
                   : ((mf.texture_slots && mf.texture_slots.slot_params && mf.texture_slots.slot_params.Tex0) ? mf.texture_slots.slot_params.Tex0 : null),
            d: (mf.DirType !== undefined && mf.DirType !== null) ? String(mf.DirType) : null,   /* ★ DirType 源属性（effects.json 已有） */
            bridge_source: 'runtime'
          };
          var rec_bridge_key = null;
          var sb = (function () {
            /* ★ 桥键用**带 .gim 的文件名**（stemOf 会去掉 .gim ⇒ 曾导致 26/26 都匹配不到、分支回落成 additive 白块） */
            var fn = mname ? String(mname).split(/[\\/]/).pop() : null;
            if (!fn) return null;
            MODEL_STEM_SEEN[fn] = (MODEL_STEM_SEEN[fn] || 0) + 1;
            rec_bridge_key = fn + '#' + MODEL_STEM_SEEN[fn];
            return SRC_BRIDGE_1110152[rec_bridge_key] || null;
          })();
          if (sb) {
            if (bridge.tm === null) bridge.tm = sb.tm;
            if (bridge.rb === null) bridge.rb = sb.rb;
            if (bridge.tt === null) bridge.tt = sb.tt;
            if (bridge.op === null) bridge.op = sb.op;
            if (bridge.db === null) bridge.db = sb.db;
            if (bridge.tex0 === null) bridge.tex0 = sb.tex0;
            bridge.bridge_source = 'SRC_BRIDGE_1110152(xml@L' + sb.line + '; runtime 缺项才用)';
          }
          var _srcTex = srcTexState(n, bridge), _srcScl = srcScaleState(n, mf.tracks || {});
          var rec = { node: n, group: g, mf: mf, name: n.name, srcBridge: bridge, bridgeKey: rec_bridge_key,
                      src_texture: _srcTex, src_scale: _srcScl,
                      hasTex0: !!(bridge.tex0),
                      meshRel: mf.mesh || n.model_glb || (mname ? ('sfx/' + stemOf(mname) + '.glb') : null),
                      state: 'pending', obj: null, iso_vis: null,   /* iso_vis: null=按原判据；true/false=只读取证强制 */
                      start: Number(mf.FxStartTime) || 0,
                      life: Math.max(Number(mf.FxLifeSpan) || loop, 0.05),
                      renderOrder: Number(mf.RenderOrder) || 0,
                      /* ★ 颜色源按优先级取**源 uniform**（跨皮肤通用；缺失 ⇒ 走 no_color_source fail-closed，绝不默认白） */
                      color: flat(ut.u_emissivecolor_Keyframe || ut.u_diffuse_color_Keyframe
                                  || ut.u_main_color1_Keyframe || ut.u_main_color2_Keyframe || ut.u_main_color3_Keyframe),
                      colorSource: (ut.u_emissivecolor_Keyframe ? 'u_emissivecolor_Keyframe'
                                  : ut.u_diffuse_color_Keyframe ? 'u_diffuse_color_Keyframe'
                                  : ut.u_main_color1_Keyframe ? 'u_main_color1_Keyframe'
                                  : ut.u_main_color2_Keyframe ? 'u_main_color2_Keyframe'
                                  : ut.u_main_color3_Keyframe ? 'u_main_color3_Keyframe' : null),
                      hi: flat(ut.u_emissive_highlight_intensity_Keyframe),
                      /* ★ 源级材质通道（有则用，无则标 absent —— 不冒充源级）：
                         u_maintex{1,2,3}_opacity_Keyframe / _brightness_Keyframe / u_maintex_rotation_Keyframe */
                      mtOpacity: flat(ut.u_maintex1_opacity_Keyframe || ut.u_maintex2_opacity_Keyframe || ut.u_maintex3_opacity_Keyframe),
                      mtBright: flat(ut.u_maintex1_brightness_Keyframe || ut.u_maintex2_brightness_Keyframe || ut.u_maintex3_brightness_Keyframe),
                      rot: flat(ut.u_maintex_rotation_Keyframe),
                      sx: flat((mf.tracks || {}).scale_XScale), sy: flat((mf.tracks || {}).scale_YScale),
                      sz: flat((mf.tracks || {}).scale_ZScale), sf: flat((mf.tracks || {}).ScaleFrame),
                      expected: (mf.mesh_evidence && mf.mesh_evidence.bbox_span) || null };
          /* ★ task-61：A/B/C 分类**只看源驱动项是否存在**（不猜语义）：A=有 u_emissivecolor(_color)，B=仅 u_diffuse_color，C=两者皆无 */
          rec.cls = (ut.u_emissivecolor_Keyframe || ut.u_emissive_color_Keyframe) ? 'A'
                  : (ut.u_diffuse_color_Keyframe ? 'B' : 'C');
          /* ★ Lead 20260920 判据泛化（**只改标签，不接材质**）：1110171 的源 bin 用的是**另一组命名**
             `u_main_color1/2/3_Keyframe` / `u_overall_opacity_Keyframe` / `u_emissive_highlight_intensity_Keyframe`
             ⇒ 26/28 个 Model **源里确实有颜色相关驱动**，只是不在 A/B 两族里。
             先前把它记成 `disabled_no_color_driver`（= 源里没有颜色）是**归因错误**。
             `u_main_color1/2/3` 的 **slot 语义未定证** ⇒ 本轮**不拿它当颜色**（不猜），
             但状态改为 `disabled_color_semantics_unresolved`，并把命中的轨道名记进 `rec.color_family_unresolved`。 */
          rec.other_color_tracks = Object.keys(ut).filter(function (k) {
            return /^u_main_color[123]_Keyframe$/.test(k) || /^u_overall_opacity_Keyframe$/.test(k)
                   || /^u_emissive_highlight_intensity_Keyframe$/.test(k);
          });
          rec.color_family_unresolved = (rec.cls === 'C' && rec.other_color_tracks.length) ? rec.other_color_tracks : null;
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：源色可解析性登记（与 rec.cls 同一判据，只读） */
          rec.src_color = {
            state: (rec.cls === 'A' || rec.cls === 'B') ? 'present_in_source' : 'absent_in_source',
            source: rec.colorSource || null,
            other_color_tracks: rec.other_color_tracks
          };
          rec.emissive_src = ut.u_emissivecolor_Keyframe ? 'u_emissivecolor'
                           : (ut.u_emissive_color_Keyframe ? 'u_emissive_color' : null);   /* U4：两种拼写各自取用，不合并 */
          rec.diffuse_src = ut.u_diffuse_color_Keyframe ? 'u_diffuse_color' : null;
          rec.opacity_src = ut.u_overall_opacity_Keyframe ? 'u_overall_opacity' : null;
          rec.opTrack = flat(ut.u_overall_opacity_Keyframe);
          /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 B「白色巨块」）：**源级不透明度的回落链**。
             事实（1110025 逐节点实测，12/12 Model）：`uniform_tracks` 里**没有** `u_overall_opacity_Keyframe`
             ⇒ 旧写法 `useOp=false` ⇒ `m.opacity = 1`（完全不透明）。与此同时**源里确实有 alpha 源**：
               · `tracks_all.AlphaMtl_Keyframe`（源 XML 内 `<AlphaMtl_Keyframe>`），12/12 存在，3 帧 0.5/0.35/0.5 等；
               · `u_diffuse_color_Keyframe` 的第 0 列（ColorKeyFrame 四分量已定证为 argb ⇒ 列 0 = A），
                 例 `L_模型glow` = 172、`H_模型宝石` = 127（<255 ⇒ 源本来就是半透）。
             ⇒ 语义未定证，但"有 alpha 轨道却按 1.0 渲染"是**缺项**而不是选择。本改动只把 `u_overall_opacity`
                的**缺失**用上述两个源轨道补上（优先级：u_overall_opacity > AlphaMtl > color 列0），
                **不新增任何乘法/系数**，并且把实际来源写进 `rec.opacity_src_used` 供探针直读。 */
          rec.alphaMtlTrack = flat(((n.tracks_all || {}).AlphaMtl_Keyframe) || null);
          rec.colorAlphaTrack = flat(ut.u_diffuse_color_Keyframe || ut.u_emissivecolor_Keyframe
                                     || ut.u_emissive_color_Keyframe || null);
          rec.opacityFallback = rec.opTrack && rec.opTrack.length ? rec.opTrack
                              : (rec.alphaMtlTrack && rec.alphaMtlTrack.length ? rec.alphaMtlTrack : null);
          rec.db = trackFirst(ut.u_depth_bias_Keyframe);
          /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 B「一坨白色巨块」的第二个根因）：**源级 TransparentMode 直读**。
             事实（1110025 逐节点从 `raw_xml` 正则抽取，12/12 Model）：`raw_xml` 的 `<Model …>` 属性里
             **全部** `TransparentMode="0"`；同一字段在 1110152(directlight) 的 `mf.transparent_mode` 里也是 0，
             而 Sprite 路径早已把它当**源级透明/混合**依据（`applyModelMaterial` 原注释：
             "'0'→Normal，'2'→Additive；映射语义未在源中验证 ⇒ approximate"）。
             但 Model 路径**从 effects.json 拿不到该字段**（本皮肤 model_fields 只有 note/shader/uniform_tracks/xml_attrs）
             ⇒ 旧桥 `rec.srcBridge.tm` 只对 1110152 生效 ⇒ 本皮肤恒走 `MODEL_BLEND='additive'` 全局默认。
             后果（实测）：12 个 Model 全走加法混合，其中 `H_模型上_3`/`M_模型上_2`（源色 247,205,221 / 236,100,138）
             + `H_模型宝石_1`（255,121,165）三块大面片叠在一起 ⇒ 互相加成 ⇒ 纯特效掩码里
             **min(r,g,b)>=200 的像素 25,195 个**（"一坨大白块"）。
             修法：把源属性**直读**进 rec，作为 blending 的**首选**来源；映射沿用 Sprite 路径已有的
             `'0'→Normal / '2'→Additive`（approximate，枚举值表仍 NOT_FOUND）。缺字段时逐字回落到旧的 MODEL_BLEND。 */
          var tmSrc = null;
          try {
            var mm2 = /TransparentMode\s*=\s*"([^"]*)"/.exec(String(n.raw_xml || ''));
            if (mm2) tmSrc = String(mm2[1]);
          } catch (e2) { tmSrc = null; }
          rec.transparentModeSrc = tmSrc;         /* '0' | '2' | null */
          rec.transparentModeSrcSrc = (tmSrc !== null) ? 'source:xml_attr:TransparentMode(raw_xml)' : 'absent_in_source';
          rec.drivers_used = Object.keys(ut).sort();
          rec.drivers_used = Object.keys(ut).sort();
          rec.highlight_src = ut.u_emissive_highlight_intensity_Keyframe ? 'u_emissive_highlight_intensity' : null;
          /* ★ task-61：源式里**未声明/不可得**的因子 ⇒ 整个子项省略（不填中性值顶替），逐项登记 */
          rec.omitted = ['u_emissive_grey_intensity', 'u_emissive_mix', 'u_emissive_desaturate', 'u_mask_intensity']
                          .filter(function (kk) { return !ut[kk + '_Keyframe']; });
          if (rec.cls === 'A') rec.omitted.push('emissive_sample_e(=u_emissivecolor 的贴图采样项)');
          rec.approx_reason = (rec.cls === 'A') ? 'tex_unbound_e_sampler_unavailable + omitted_undeclared' : null;
          /* ★ task-61（lead 2026-09-19 裁定 1）：`u_emissive_color` 拼写变体（仅 M_模型喇叭）按**该节点自身声明**视为自发光，
             但必须标 spelling_variant + confidence=medium（U4 未定证）；其 u_diffuse_color 仍记录在 diffuse_src 供负控。 */
          rec.spelling_variant = !!ut.u_emissive_color_Keyframe && !ut.u_emissivecolor_Keyframe;
          rec.confidence = rec.spelling_variant ? 'medium' : 'high';
          /* ★ task-61（lead 2026-09-19 追加 2）：`.sfx` 的 <Macros><Variables><Semantic Type="Bool"> 是 Bool=TRUE 开关
             ⇒ 用作「该节点哪些 uniform 才有意义」的**门**（USE_EMISSIVE_CONTROL / USE_SOFTPARTICLE / USE_SFXLIGHT_FOG /
             USE_VERTEXCOLOR / USE_MASK01）。来源：model_fields.shader.ShaderComponent 里 Type==='Bool' 的条目（effects.json 已有，无需再内联）。 */
          rec.macros = (((mf.shader || {}).ShaderComponent) || []).filter(function (e) {
            return e && typeof e === 'object' && e.Type === 'Bool';
          }).map(function (e) { return String(e.Name) + '=' + String(e.Value); });
          rec.gates = rec.macros.slice();
          rec.depth_bias_state = ut.u_depth_bias_Keyframe ? 'present_unwired(engine_state_unresolved)' : null;
          /* present_unwired：源里有、但本轮**明确不接线**的项（溶解/UV speed/功率等），只登记。
             ⚠ u_emissive_highlight_intensity 已按源公式**接线**（L409）⇒ 不在本表；其状态见 highlight_state。 */
          rec.unwired = rec.drivers_used.filter(function (kk) {
            return /u_dissolve|u_intensity|u_emissive_power|softparticle|uvspeed|tilling|uv_offset|speed_/.test(kk)
                   && !/highlight_intensity/.test(kk);
          });
          rec.tex_bound = false;                 /* 26/26 GLB 无内嵌图像、贴图槽↔源名 unresolved ⇒ 一律未绑 */
          /* ★ Lead 20260920：`.mtg` 的源参数（`MTG_MATERIALS_20260919.json` 逐 stem 解出）。
             只登记**源值**，不改任何既有字段；仅当 `WikiSfxAdapter.mtgParams(true)`（默认 OFF）时
             才作为发光的**源值来源**（替换 srcBridge 的色/强度取值），乘法仍只保留 L317 一处。 */
          rec.mtgParams = (n.mtg_params && typeof n.mtg_params === 'object') ? n.mtg_params : null;
          rec.mtgStem = n.mtg_stem || null;
          rec.mtgShader = n.mtg_shader || null;
          rec.fallback_reason = null;
          rec.ignored = ignored;
          modelRecs.push(rec);
          g.visible = MODELS_ON;
          var _gate = srcGateBlocks(rec);
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**源级 fail-closed 门**放在最前（FxIgnore 之后）——
             源里既无可解析贴图、又无缩放时，画出来只能是无据白/灰大板 ⇒ 默认不画，并把 state 写成显式标签
             （禁止 `state:'ok'` 与"实际没画"并存）。未在 effects.json 设 `models_require_source_texture_and_scale`
             的皮肤 `_gate.blocked` 恒 false（src_texture 只要存在即 'present_in_source'）⇒ 逐字走旧分支。 */
          if (HONOR_FXIGNORE && ignored) { rec.state = 'disabled_fxignore'; rec.fallback_reason = 'FxIgnore=TRUE'; }   /* ★ 源里禁用 ⇒ 不加载 */
          else if (_gate.blocked) { applySrcGate(rec, _gate); }   /* 源贴图+缩放皆缺 ⇒ 显式 disabled（可被 models(true) 强制取证加载） */
          else if (rec.cls === 'C') {
            /* ★ Lead 20260920：C 类里"源里有别族颜色轨道但 slot 语义未定证"的 ⇒ 用**诚实标签**，
               不再记成"源里没有颜色"（两者都不渲染，唯一区别是归因正确）。 */
            if (rec.color_family_unresolved) {
              rec.state = 'disabled_color_semantics_unresolved';
              rec.fallback_reason = 'color_slot_semantics_unresolved:' + rec.color_family_unresolved.join('|');
            } else {
              rec.state = 'disabled_no_color_driver'; rec.fallback_reason = 'no_color_driver_unresolved';
            }
          }
          else if (rec.hasTex0) { rec.state = 'disabled_texture_unresolved'; rec.fallback_reason = 'texture_unresolved'; }       /* 源贴图未定 ⇒ 不顶替、不渲 */
          else if (!MODELS_ON) { rec.state = 'disabled_fail_closed'; }
          else { loadModel(rec); }
          return;
        }

        /* ★ FXADAPT：无贴图候选的源粒子节点（本皮肤 4 个 ParticleRes）登记为 **不可驱动**，
           只为让 sfxDiag 如实报「源有几个粒子节点 / 有几个真能跑」，**不伪造粒子参数**。 */
        if (!n.texture_candidate) {
          if (isPS) {
            systems.push({ node: n, drivable: false, ignored: ignored,
              why: 'effects.json 该节点 texture/emit/color 全空（源仅引用子帧 .sfx）→ 无速率/寿命/贴图可驱动',
              rate: 0, l0: 0.3, l1: 0.3, emitR: 0, vel: 0, scaleTrack: [], basePos: basePos,
              blendConst: blendConst, pool: [], tex: null, emitAtBegin: false });
          }
          return;                       /* 其余（Model/Dummy）不进渲染集，另由 nodeAudit 报告 */
        }

        if (!isPS) {
          var mat = new THREE.SpriteMaterial({ transparent: true, depthWrite: false, opacity: 0, blending: blendConst });
          var sp = new THREE.Sprite(mat);
          sp.position.fromArray(basePos); sp.visible = false;
          sp.userData = { kind: 'sprite', nodeName: n.name, start: n.start || 0, life: Math.max(n.life || loop, 0.12),
            radius: n.radius || 5, color: flat(colorTrackOf(n)), ss: flat(n.smooth_start), se: flat(n.smooth_stop),
            scale: flat(n.scale_track), ready: false,
            texName: (n.texture ? String(n.texture).split(/[\\/]/).pop() : null),
            blendUsed: (n.blend_mode === null || n.blend_mode === undefined) ? null : blendOf(n.blend_mode) };
          if (HONOR_FXIGNORE && ignored) { sp.userData.force_hidden = true; }   /* ★ 源 FxIgnore=TRUE ⇒ 不画 */
          group.add(sp); sprites.push(sp);
          /* ★ task-53：精灵表切片。`.spr` 是源声明的描述符（明文本），其帧矩形是**候选级**证据
             （content_candidate：图集实体的名字轴仍不可得）⇒ 只影响 UV 取帧，不宣称源级绑定。 */
          var ud = sp.userData;
          ud.sliced = false; ud.slice_reason = null; ud.rects = null; ud.sheet = null; ud.frames = null;
          if (SPRITE_FIX && /\.spr$/i.test(String(n.texture || ''))) {
            d.slice_reason = 'spr_declared_not_loaded';
            (function (dd) {
              fetch(baseUrl + String(n.texture).split(/[\\/]/).pop()).then(function (r) { return r.ok ? r.text() : null; })
                .then(function (txt) {
                  if (!txt) { dd.slice_reason = 'spr_fetch_empty'; return; }
                  var lines = txt.replace(/\r/g, '').split('\n').filter(function (x) { return x.trim(); });
                  var head = lines[0].trim().split(/\s+/);
                  var rects = [];
                  for (var i = 3; i < lines.length; i++) {
                    var p = lines[i].trim().split(/\s+/);
                    if (p.length === 5 && /\.tga$/i.test(p[0])) rects.push([+p[1], +p[2], +p[3], +p[4]]);
                  }
                  if (!rects.length) { dd.slice_reason = 'spr_no_rects'; return; }
                  /* ★★★ 修复（2026-09-20，ENVWIRE·辉光流动）：**图集尺寸从帧矩形推导**（原来只读 head）。
                     缺陷（effects.json.rendering_notes.sprite_sheet / pending 已如实登记，但未修）：
                       1110025 的 `tex_leaf_huaban_hgz01_02.spr` 头部**只有 1 个 token**（实测首行 = `0`，
                       次行 `16` = 帧数，三行 `1000` = 时长），`head[1]/head[2]` ⇒ `dd.sheet=[NaN,NaN]`
                       ⇒ L1115 的切片门 `sheet[0]>0 && sheet[1]>0` **不成立** ⇒ 精灵表不切片
                       （整张 256×256 当单帧）⇒ 16 帧 leaf 图集**不动**，用户看到的"辉光流动"缺失。
                     修法（**数据驱动、零猜值**）：head 前两 token 不是"宽 高"时，
                       用 **16 个帧矩形自身的边界**推出图集尺寸 =
                       `2^ceil(log2(max(right)+1)) × 2^ceil(log2(max(bottom)+1))`，
                       并写上 `sheet_basis` 说明来源。本份：max right/bottom = 255 ⇒ 2^8 = **256×256**，
                       与 `effects.json.atlas_provenance.atlas_dims=[256,256]`（BC7 DDS 实体尺寸）**一致** ⇒ 自校验通过。
                     纪律：只在 head 推导**失败**时启用；head 可用时逐字保持旧行为（其余皮肤不受影响）；
                       不做任何 UV 翻转/缩放以外的改动（帧矩形本身**未改一字**）。 */
                  var hw = +head[1], hh = +head[2];
                  var sheetBasis = 'head[1],head[2] (source header)';
                  if (!(hw > 0) || !(hh > 0)) {
                    var mx = 0, my = 0;
                    for (var ri = 0; ri < rects.length; ri++) {
                      if (rects[ri][2] > mx) mx = rects[ri][2];
                      if (rects[ri][3] > my) my = rects[ri][3];
                    }
                    var pw = Math.pow(2, Math.ceil(Math.log2(mx + 1)));
                    var ph = Math.pow(2, Math.ceil(Math.log2(my + 1)));
                    hw = pw; hh = ph;
                    sheetBasis = 'derived_from_spr_frame_rects (head lacks w/h tokens; max right/bottom='
                               + mx + '/' + my + ' ⇒ pow2 ' + pw + 'x' + ph + ')';
                  }
                  dd.sheet = [hw, hh]; dd.rects = rects; dd.frames = rects.length;
                  dd.sheet_basis = sheetBasis;
                  dd.sliced = true; dd.slice_reason = 'spr_rects_applied_content_candidate';
                }).catch(function () { dd.slice_reason = 'spr_fetch_failed'; });
            })(ud);
          }
          texFor(n, (function (s) { return function (tex) { if (disposed || !tex) return; s.material.map = tex; s.material.needsUpdate = true; s.userData.ready = true; }; })(sp));
          return;
        }

        // ── ParticleSystem：真粒子（出生/存活/死亡），按源速率与寿命 ──
        /* task-58：rate 现在来自 effects.json 的规范字段（source:xml_attr:ParticlesPerSecond）；
           此前 rate 恒 0 是**我方解析缺字段**，不是源事实（见 FX_UNIT_fix_report 更正段）。 */
        var rateRaw = (n.particlesPerSecond !== undefined && n.particlesPerSecond !== null) ? n.particlesPerSecond
                      : ((n.ParticlesPerSecond !== undefined && n.ParticlesPerSecond !== null) ? n.ParticlesPerSecond : null);
        var rateHasSource = (rateRaw !== null && isFinite(Number(rateRaw)));
        var rate = rateHasSource ? Number(rateRaw) : 0;
        var l0 = Number(n.minSpriteLifespan !== undefined ? n.minSpriteLifespan : n.MinSpriteLifespan);
        var l1 = Number(n.maxSpriteLifespan !== undefined ? n.maxSpriteLifespan : n.MaxSpriteLifespan);
        if (!isFinite(l0)) l0 = 0.3; if (!isFinite(l1)) l1 = 0.3;
        /* task-57：有声明则乘换算；无声明兜底 1.0 标 default_no_source */
        var emitRdecl = first(flat(n.emit && n.emit.EmissionRadiusFrame), null);
        var emitR = (emitRdecl === null || emitRdecl === undefined) ? 1.0 : U(emitRdecl);
        var emitRsrced = !(emitRdecl === null || emitRdecl === undefined);
        /* task-57：原为手调 0.02（无源依据）=> 改为源推导的单位换算 SFX_UNIT_TO_MODEL */
        var vel = U(first(flat(n.emit && n.emit.MaxSpriteVelocityFrame), 0));
        var scaleTrack = flat(n.emit && n.emit.SpriteScaleFrame);
        var sizeMin = (n.minRadius !== undefined && n.minRadius !== null) ? Number(n.minRadius) : null;
        var sizeMax = (n.maxRadius !== undefined && n.maxRadius !== null) ? Number(n.maxRadius) : null;
        var sys = { node: n, drivable: true, rate: rate, rate_has_source: rateHasSource,
                    size_min: sizeMin, size_max: sizeMax,
                    fallback_reason: rateHasSource ? null : 'source_rate_missing',
                    rate: rate, l0: l0, l1: l1, emitR: emitR, vel: vel, scaleTrack: scaleTrack,
                    basePos: basePos, ignored: ignored, blendConst: blendConst, pool: [], tex: null,
                    emitAtBegin: String(n.emitAtBegin).toUpperCase() === 'TRUE', emitR_source: emitRsrced };
        systems.push(sys);
        texFor(n, (function (s) { return function (tex) { s.tex = tex; }; })(sys));
        /* ★★ 新增（2026-09-20，ENVWIRE）：把该节点自己的 `.spr` 帧表接到 `spr_frames`/`spr_sheet`，
           使 `updateParticles()` 与单四边形兜底里**既有**的切帧门首次真正成立（16 帧动起来）。
           纯数据接线：不改切帧算法、不改帧矩形、不引入任何贴图。见上方 fetchSprFrames 注释。 */
        fetchSprFrames(n, (function (s, nn) { return function (sp) {
          if (!sp || !sp.frames || !sp.frames.length) return;
          nn.spr_frames = sp.frames; nn.spr_sheet = sp.sheet; nn.spr_sheet_basis = sp.basis;
          s.spr_frames = sp.frames; s.spr_sheet = sp.sheet; s.slice_path = sp.basis;
        }; })(sys, n));
      });

      /* ★ 修复（2026-09-18，ROTBUG）：特效层原先 `ctx.root.add(group)` —— 作为**模型根的子节点**。
         但 three 的 `Sprite` 自带 geometry（4 顶点 quad，three r180 `class Sprite ... this.geometry = ma`），
         而 `Box3.expandByObject()` 会 union `object.geometry.boundingBox × matrixWorld`，
         于是每个 SFX Sprite 都被算进 `Box3.setFromObject(state.root)`。
         viewer 的 `modelFocus()`（viewer.js L455-461）正是这个 Box3，`applyOrbit()`
         （viewer.js L2134-2138）用它当**旋转轴心**并做 `root.position.add(c0-c1)` 补偿：
           · 实测（ROTBUG_result_before.json）：挂上特效后轴心 NDC x 0.4925→0.7763（+0.284），
             投影盒宽 0.352→1.043（3.0×）、clipped 由 false→true；
             同一拖动 pc 净漂移 ×1.4、单步最大跳变 ×3.1（0.0045→0.0138）
           · 且 `setEnabled(false)` 只置 `group.visible=false`，Sprite 仍在包围盒里
             → 关掉开关后仍然偏（实测 idle pc 0.8138）⇒ 用户看到的「打开 SFX 后旋转乱转」
         修法：特效层挂到 **scene**，每帧把 `root.matrixWorld` 抄进 `group.matrix`（matrixAutoUpdate=false）。
         挂点语义不变（anchor/pos_offset 仍是**模型本地空间**，因为乘的正是 root.matrixWorld），
         但特效不再进入 root 的包围盒 → 旋转轴心与 off 基线一致。 */
      LIVE_SFX = {
        sprites: sprites, systems: systems, fixedTime: function () { return fixedTime; },
        weaponDiag: weaponDiag,
        nodeSummary: function () {
          return sprites.map(function (s) { return { name: s.userData.nodeName, sliced: !!s.userData.sliced, kind: 'sprite' }; })
            .concat(systems.map(function (sy) { return { name: (sy.node && sy.node.name) || null, sliced: false, kind: 'particle' }; }));
        }
      };
      /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 A「特效层不跟随旋转」根因修复）
         现象（实测 shots25/FXFOLLOW_result.json）：`__spinDemo('modelY',75)` 后武器本体变化 38,190 px，
         但「纯特效掩码」(FX-on − FX-off) IoU(0°,75°)=0.55–0.88、质心仅动 1~4 px ⇒ 特效层冻在原地。
         根因：`ctx.root` 是 `attach()` 时刻的**快照对象**；查看器每次重建模型都换新对象
         （`weapon_skin_viewer.js` L3388 `state.root=gltf.scene`；`attachEffects` L998 传的是当时那个 root）
         ⇒ `syncToRoot()` 每帧抄的是**旧 root** 的 matrixWorld，新 root 转多少都与特效无关。
         修法（最小、向后兼容）：viewer 传**活引用取数器** `getRoot()`（每帧调用 ⇒ 永远当前 root）；
         没有 `getRoot` 的旧调用方逐字沿用 `ctx.root`（旧行为不变）。
         挂点语义不变（anchor/pos_offset 仍是模型本地空间，因为乘的正是当前 root 的 matrixWorld）。 */
      var rootObj = ctx.root, sceneObj = ctx.scene;
      var getRootRef = (typeof ctx.getRoot === 'function') ? ctx.getRoot
                     : ((typeof ctx.getRootObject === 'function') ? ctx.getRootObject : null);
      var liveRoot = rootObj, rootSrc = getRootRef ? 'ctx.getRoot()' : 'ctx.root(snapshot)';
      function currentRoot() {
        if (!getRootRef) return rootObj;
        var r = null;
        try { r = getRootRef(); } catch (e) { r = null; }
        return (r && typeof r.updateMatrixWorld === 'function') ? r : rootObj;
      }
      /* useScene 的判据与旧版一致（scene 可用即挂 scene），但 root 侧改为每帧取活引用 */
      var useScene = !!(sceneObj && typeof sceneObj.add === 'function'
                        && ((getRootRef ? true : !!rootObj)));
      function syncToRoot() {
        if (!useScene) return;
        liveRoot = currentRoot();
        if (!liveRoot || typeof liveRoot.updateMatrixWorld !== 'function') return;
        liveRoot.updateMatrixWorld(true);
        group.matrix.copy(liveRoot.matrixWorld);
        group.matrixWorldNeedsUpdate = true;
      }
      if (useScene) { group.matrixAutoUpdate = false; sceneObj.add(group); syncToRoot(); }
      else { ctx.root.add(group); }        // 退化路径：无 scene 时保持旧行为

      function mkParticle(sys) {
        var mat = new THREE.SpriteMaterial({ transparent: true, depthWrite: false, opacity: 0, blending: sys.blendConst, map: sys.tex || null });
        var sp = new THREE.Sprite(mat); sp.visible = false; group.add(sp);
        return sp;
      }

      function updateParticles(sys, t) {
        var n = sys.node;
        var start = Number(n.start) || 0, life = Math.max(Number(n.life) || loop, 0.12);
        var tStart = start, tEnd = start + life;              // 发射窗口=节点 FxStartTime..+FxLifeSpan
        var wants = [];
        if (sys.rate > 0) {
          var kMax = Math.ceil(Math.min(t, tEnd) * sys.rate) + 2;
          for (var k = 0; k < kMax && wants.length < MAX_PARTICLES; k++) {
            var bt = tStart + k / sys.rate;
            if (bt > Math.min(t, tEnd)) break;
            var r1 = hash01(rngSeed, k, 1), r2 = hash01(rngSeed, k, 2), r3 = hash01(rngSeed, k, 3), r4 = hash01(rngSeed, k, 4);
            var plife = lerp(sys.l0, sys.l1, r1);             // 源异常(Min>Max)按原值顺序，不交换
            if (plife <= 0) continue;
            var age = t - bt;
            if (age < 0 || age > plife) continue;             // 未出生 / 已死亡 → 不画
            wants.push({ bt: bt, life: plife, age: age, r1: r1, r2: r2, r3: r3, r4: r4 });   /* task-58：带上出生随机 r1，供尺寸固定使用 */
          }
        }
        if (sys.emitAtBegin && t >= tStart && sys.l0 > 0) {
          var r = hash01(rngSeed, 9999, 5), r2b = hash01(rngSeed, 9999, 6), r3b = hash01(rngSeed, 9999, 7);
          wants.push({ bt: tStart, life: lerp(sys.l0, sys.l1, r), age: t - tStart, r2: r2b, r3: r3b, r4: 0.5 });
        }
        while (sys.pool.length < wants.length) sys.pool.push(mkParticle(sys));
        sys.pool.forEach(function (sp, i) {
          var p = wants[i];
          if (!p) { sp.visible = false; return; }
          var u = p.age / p.life;                             // 该粒子自身归一化年龄
          /* ★ task-90：颜色走 `colorTrackOf`（par 优先）；alpha=列0 / RGB=列1..3（argb 定证） */
          var col = sample(flat(colorTrackOf(n)), u, 4);
          var a = col ? col[0] / 255 : 1;                     /* argb：alpha 在列0（task-90 Q1 定证） */
          var rgb = col ? [col[1], col[2], col[3]] : [255, 255, 255];
          var s0 = sample(flat(n.smooth_start), u, 4), s1 = sample(flat(n.smooth_stop), u, 4);
          if (s0) a *= (s0[0] / 255) * (s0[1] / 255);
          if (s1) a *= (s1[0] / 255) * (s1[1] / 255);
          var sc = sample(sys.scaleTrack, u, 1);
          var ang = p.r2 * Math.PI * 2, rad = sys.emitR * p.r3;
          /* ★ Lead 20260920（KIN_VEL，默认 ON）：源式位移替换写死的 `*20`；OFF 逐字保留旧式。 */
          var drift, driftY, vertK;
          if (KIN_VEL) {
            var v0k = kinV0(n, p.r1), gk = kinG(n), tk = p.age;
            var sk = (v0k === null) ? 0 : (v0k * tk + 0.5 * gk * tk * tk);   /* cm */
            drift = U(sk);           /* → 模型单位（与 EmissionRadius 同范式） */
            driftY = 0;              /* 竖直分量由源 Gravity 已含在 sk 内；不再用写死的 0.6 */
            vertK = 1.0;
          } else {
            drift = sys.vel * p.age * 20;   /* 旧式（逐字保留，供 A/B 与负控） */
            driftY = drift;
            vertK = 0.6;
          }
          sp.position.set(sys.basePos[0] + Math.cos(ang) * rad + Math.cos(ang) * drift,
                          sys.basePos[1] + (p.r4 - 0.5) * sys.emitR * vertK + (p.r4 - 0.5) * driftY,
                          sys.basePos[2] + Math.sin(ang) * rad + Math.sin(ang) * drift);
          sp.material.color.setRGB(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255);
          sp.material.opacity = Math.max(0, Math.min(1, a));
          /* ★★★ FIX-FXSQUARE 2026-09-21：**贴图迟到回填 + 无贴图 fail-closed 不画**。
             缺陷（用户原话「有一朵花瓣真的出来了，但是还有别的是错的，比如说奇怪的正方体」）：
               池粒子由本函数**惰性创建**（下方 `while (sys.pool.length < wants.length) sys.pool.push(mkParticle(sys))`），
               而 `mkParticle` 只在**构造那一刻**取贴图：`map: sys.tex || null`；`texFor()` 是**异步** TextureLoader，
               attach 后第一帧 tick 必然早于 256×256 图集解码完成 ⇒ 首批 `pool[i].material.map === null`。
               旧代码此后**从不回填**（对比：精灵路径在 texFor 回调 L1017 里 `s.material.map = tex`；
               单四边形兜底路径每帧 L1274 都有 `if (sys.tex && sys.sq.material.map !== sys.tex) …`）——
               池路径是唯一漏掉回填的一条 ⇒ 这些粒子以 **map=null 的 SpriteMaterial** 渲染。
               SpriteMaterial 没有 map 就**没有 alpha 形状**，屏幕上是一整块实心色 quad
               ⇒ 就是用户看到的「奇怪的正方体」。
             实测（_fxsquare_diag_20260921.py，全新 profile，修前 8/8 采样一致）：
               `pool_map_null=1 / pool_map_bound=1`；pool[0] = `has_map=false, repeat=null, offset=null,
               color=a7c3ff, quad≈0.17`；pool[1] = `has_map=true, repeat=[0.24609,0.24609],
               offset=[0.25,0.50391], quad≈0.20`（= 63/256 与 64/256 / 1-127/256，即 `.spr` 帧 (64,64,127,127)
               在 256×256 图集上的正确 UV ⇒ **切片本身是对的，不是切片问题**）。
               屏幕掩码：FX-on−FX-off 的最大连通域 = 17×16 px **fill 0.87 的实心矩形**
               （而图集 16 帧的不透明占比仅 18.7%–36.5% ⇒ 带贴图的绘制**不可能**产出实心矩形）。
             修法（最小、与既有范式一致，零新参数/零系数）：
               ① 每帧把已就绪的 `sys.tex` 回填给池内粒子（含此前漏掉的旧粒子）⇒ 迟到的图集也能上屏，
                  于是"先出生的粒子"同样画成花瓣，而不是方块；
               ② `visible` 追加 `!!sp.material.map` 门 —— 源贴图未就绪/不可解析时**不画**
                  （源级 fail-closed：宁可少画一个粒子，也不许用纯色方块顶替；同 L1308 单四边形兜底路径口径）。 */
          if (sys.tex && sp.material.map !== sys.tex) { sp.material.map = sys.tex; sp.material.needsUpdate = true; }
          sp.visible = (sp.material.opacity > 0.01) && !!sp.material.map;
          /* task-58：粒子尺寸 = 源 [minRadius,maxRadius] 区间随机 x 源 SpriteScale 当前帧 x U() */
          var smn = (sys.size_min !== null && isFinite(sys.size_min)) ? sys.size_min : 1.2;
          var smx = (sys.size_max !== null && isFinite(sys.size_max)) ? sys.size_max : smn;
          /* task-58 修复：原为 Math.random() 且位于**每帧循环内** ⇒ 同一粒子每帧尺寸跳变（抖动 + A/B 不可复现）。
             改为使用**出生时算好的稳定随机** p.r1 ⇒ 每粒子整个生命周期固定；源 minRadius/maxRadius 的"区间随机"语义保留。 */
          var rnd = smn + ((p && p.r1 !== undefined) ? p.r1 : 0.5) * (smx - smn);
          /* ★★ 修改（2026-09-20，ENVWIRE）：粒子半径改用 `UR()`（逐皮肤定标），不再用 `U()`。
             见 UR()/PARTICLE_RADIUS_TO_WORLD 的注释：`U()` 的 0.1 是为 SFX **大尺度**字段推出的，
             套到 radius 上会把本皮肤粒子压到 1–2 px（实测 quad=0.02 world @88px/单位）。
             缺省 `PARTICLE_RADIUS_TO_WORLD=null` ⇒ k 回落 SFX_UNIT_TO_MODEL ⇒ 其它皮肤逐字不变。 */
          var rawP = Math.max(UR(rnd) * (sc ? Number(sc[0]) : 1), 0.02);
          var qp = SPRITE_FIX ? clampQuad(rawP) : { v: rawP, clamped: false, cap: null };
          sp.userData.quad_raw = rawP; sp.userData.quad = qp.v; sp.userData.quad_clamped = qp.clamped;
          sp.scale.setScalar(qp.v);
          /* task-58：粒子按 .spr 帧矩形取帧（切片 on 且该节点有 spr_frames 时） */
          if (SPR_SLICE_ON && sys.node && sys.node.spr_frames && sys.node.spr_frames.length && sp.material.map) {
            var NF = sys.node.spr_frames.length;
            var SH = sys.node.spr_sheet || [1, 1];
            var fi = (SPR_FRAME_MODE === 'first') ? 0 : Math.min(NF - 1, Math.max(0, Math.floor(u * NF)));
            var FR = sys.node.spr_frames[fi];
            var MM = sp.material.map;
            MM.matrixAutoUpdate = true;
            MM.repeat.set((FR[2] - FR[0]) / SH[0], (FR[3] - FR[1]) / SH[1]);
            MM.offset.set(FR[0] / SH[0], 1 - FR[3] / SH[1]);
            MM.needsUpdate = true;
            sys.frame_index_last = fi; sys.sliced_frames = NF;
          }
        });
      }

      function tick() {
        if (disposed || !enabled) return;
        syncToRoot();                       /* ★ ROTBUG 修复：特效层跟随模型世界矩阵（不再挂进模型子树） */
        /* ★ Lead 20260920 缺陷修复：冻结时间（`setTime`/取证复测用）此前**不取模** ⇒ 只要冻结值 > `loop`
           （1110171 的 Model 因缺 `FxLifeSpan` 使 `life === loop === 2.0`），逐帧时间窗 `lt > life` 恒成立
           ⇒ 全部节点 `visible=false`（浏览器实测：`models(true)` 却 `ok:3 / visible:0`、像素差 0）。
           源语义：`.sfx` 的 `Loop`/`EndLessPlay` 与 viewer 的 `loop_seconds` 都表明是**循环播放** ⇒ 冻结时间
           必须与自由运行同口径取模，否则复测读数不可比（这是**缺陷**，不是观感调整）。 */
        var now = ((fixedTime !== null) ? fixedTime : (performance.now() - t0) / 1000) % loop;
        var t = now;
        sprites.forEach(function (sp) {
          var d = sp.userData;
          if (SPRITE_ON === false) { sp.visible = false; return; }   /* ★ task-53：精灵层独立开关必须门控 tick，否则下一帧又被时间窗点亮 */
          if (HONOR_FXIGNORE && d.force_hidden) { sp.visible = false; return; }   /* ★ Lead 20260920：源 FxIgnore=TRUE 的精灵节点不画 */
          if (!d.ready) { sp.visible = false; return; }
          var lt = t - d.start;
          if (lt < 0 || lt > d.life) { sp.visible = false; return; }
          var u = lt / d.life;
          var col = sample(d.color, u, 4);
          /* task-90 定证：COLOR_ORDER 默认 'argb' ⇒ 此处**不重排**（A=列0、RGB=列1..3）；仅当显式切回 'rgba' 时才重排 */
          if (col && COLOR_ORDER === 'rgba') { col = [col[3], col[0], col[1], col[2]]; }
          var a = col ? col[0] / 255 : 1, rgb = col ? [col[1], col[2], col[3]] : [255, 255, 255];
          var s0 = sample(d.ss, u, 4), s1 = sample(d.se, u, 4);
          if (s0) a *= (s0[0] / 255) * (s0[1] / 255);
          if (s1) a *= (s1[0] / 255) * (s1[1] / 255);
          var sc = sample(d.scale, u, 1);
          sp.material.color.setRGB(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255);
          sp.material.opacity = Math.max(0, Math.min(1, a));
          sp.visible = sp.material.opacity > 0.01;
          /* ★ FXADAPT 修复（2026-09-18）：原为 `d.radius * 0.035 * ...` —— 0.035 是**适配器自造常数**，
             实测把 sprite 压成 0.028–0.105 世界单位（相机 dist 14.886/fov 34 ⇒ 1 单位≈88px ⇒ 仅 2–9px），
             加法混合下连 2/255 的差都产生不了 ⇒ **静止帧 0 像素变化**、特效"整体明显弱于参考图"。
             依据：源 class 字段表里有 `Scale / XScale / YScale / ZScale / ScaleFrame`（本 fx 的 Sprite
             `scale_track` 为空 ⇒ 缺省 1），而 `radius` 是源字段（1.0 / 0.82 / 3.0 / 0.8）。
             故取 `scale = radius × 源 scaleTrack(缺省 1)`，不再乘任何自造系数。 */
          /* ★ task-53：① 精灵表按 .spr 帧矩形取 UV（候选级）；② quad 尺寸上限钳制（防未定证 radius 盖满画面） */
          if (d.sliced && d.rects && d.frames && sp.material.map && d.sheet && d.sheet[0] > 0 && d.sheet[1] > 0) {
            var fw = d.sheet[0], fh = d.sheet[1];
            var fi = Math.min(d.frames - 1, Math.max(0, Math.floor(u * d.frames)));
            var rr = d.rects[fi];
            var mm = sp.material.map;
            mm.matrixAutoUpdate = true;
            mm.repeat.set((rr[2] - rr[0]) / fw, (rr[3] - rr[1]) / fh);
            mm.offset.set(rr[0] / fw, 1 - (rr[3] / fh));
            mm.needsUpdate = true;
            d.frame_index = fi;
          }
          /* task-57：radius(cm) 乘单位换算；再乘源 TrackScale 当前 XScale（YZCopyFromX=TRUE => y=z=x） */
          var sizeMul = (sc && isFinite(Number(sc[0]))) ? Number(sc[0]) : 1;
          var rawS = Math.max(U(d.radius) * sizeMul, 0.02);
          var qq = SPRITE_FIX ? clampQuad(rawS) : { v: rawS, clamped: false, cap: null };
          d.quad_raw = rawS; d.quad = qq.v; d.quad_clamped = qq.clamped; d.quad_cap = qq.cap;
          sp.scale.setScalar(qq.v);
        });
        systems.forEach(function (sys) {
          if (!sys.drivable) return;                                                            /* ★ FXADAPT：无源参数 → 不伪造粒子 */
          if (sys.ignored) { sys.pool.forEach(function (s) { s.visible = false; }); return; }   // FxIgnore=TRUE 默认不启用
          updateParticles(sys, t);
          /* ★ task-53 靶子1：rate<=0 时的单四边形回退（源无速率 ⇒ 不伪造粒子出生，只回退一格"该节点存在"的证据） */
          if (PS_SINGLE_QUAD && PS_FALLBACK_ON && SPRITE_ON !== false && (!sys.rate_has_source || !sys.rate)) {
            if (!sys.sq) {
              var sqm = new THREE.SpriteMaterial({ transparent: true, depthWrite: false, opacity: 0, blending: sys.blendConst });
              var sq = new THREE.Sprite(sqm);
              sq.position.fromArray(sys.basePos); sq.visible = false;
              sq.userData = { kind: 'particle_single_quad', nodeName: (sys.node && sys.node.name) || null,
                texName: (sys.node && sys.node.texture) ? String(sys.node.texture).split(/[\\/]/).pop() : null,
                blendUsed: (sys.node && sys.node.blend_mode !== null && sys.node.blend_mode !== undefined) ? blendOf(sys.node.blend_mode) : null,
                why: 'source_rate<=0_single_quad_fallback' };
              group.add(sq); sys.sq = sq; sys.pool.push(sq);
            }
            if (sys.tex && sys.sq.material.map !== sys.tex) { sys.sq.material.map = sys.tex; sys.sq.material.needsUpdate = true; }
            var nq = sys.node || {};
            var ltq = t - (nq.start || 0), lfq = Math.max(nq.life || loop, 0.05);
            if (ltq < 0 || ltq > lfq) { sys.sq.visible = false; }
            else {
              var uq = ltq / lfq;
              /* ★ Lead 20260920 缺陷修复：源无速率走**单四边形兜底**时，同样按 `.spr` 帧矩形取帧。
                 此前兜底路径不切片 ⇒ 带精灵表的节点会把整张表（N×N）当一块贴上去。
                 **数据驱动**：只在节点带 `spr_frames` + `spr_sheet` 时生效，其余节点逐帧行为不变。 */
              if (SPR_SLICE_ON && nq.spr_frames && nq.spr_frames.length && sys.tex) {
                var NFq = nq.spr_frames.length;
                var SHq = nq.spr_sheet || [1, 1];
                var fiq = (SPR_FRAME_MODE === 'first') ? 0 : Math.min(NFq - 1, Math.max(0, Math.floor(uq * NFq)));
                var FRq = nq.spr_frames[fiq];
                if (FRq && SHq[0] > 0 && SHq[1] > 0) {
                  sys.tex.matrixAutoUpdate = true;
                  sys.tex.repeat.set((FRq[2] - FRq[0]) / SHq[0], (FRq[3] - FRq[1]) / SHq[1]);
                  sys.tex.offset.set(FRq[0] / SHq[0], 1 - FRq[3] / SHq[1]);
                  sys.tex.needsUpdate = true;
                  sys.sliced_frames = NFq; sys.frame_index_last = fiq;
                  sys.slice_path = 'fallback_quad_sliced';
                  sys.sq.userData.sliced_frames = NFq; sys.sq.userData.frame_index_last = fiq;
                  sys.sq.userData.slice_path = 'fallback_quad_sliced';
                }
              }
              var cq = sample(flat(colorTrackOf(nq)), uq, 4);
              var aq = cq ? cq[0] / 255 : 1;
              var scq = sample(flat(nq.scale_track), uq, 1);
              var mulq = (scq && isFinite(Number(scq[0]))) ? Number(scq[0]) : 1;
              var rawq = Math.max(U(nq.radius || 1) * mulq, 0.05);
              var qq2 = SPRITE_FIX ? clampQuad(rawq) : { v: rawq, clamped: false };
              if (cq) sys.sq.material.color.setRGB(cq[1] / 255, cq[2] / 255, cq[3] / 255);
              sys.sq.material.opacity = Math.max(0, Math.min(1, aq));
              sys.sq.scale.setScalar(qq2.v);
              sys.sq.visible = sys.sq.material.opacity > 0.01 && !!sys.tex;
              sys.sq.userData.quad_raw = rawq; sys.sq.userData.quad = qq2.v; sys.sq.userData.quad_clamped = !!qq2.clamped;
            }
          }
        });
        /* ★ FXADAPT：Model 节点逐帧驱动（FxStartTime/FxLifeSpan 时间窗 + 源 uniform/scale 轨道） */
        modelRecs.forEach(function (rec) {
          if (!rec.obj) return;
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：源级门禁**逐帧权威**（见上面注释）。
           默认（未走取证通道）⇒ 恒不画；只有 `WikiSfxAdapter.modelsForce(true)` 期间才允许显示。 */
        if (rec.src_gate_blocked && !rec.forced_evidence_load) { rec.group.visible = false; return; }
        if (HONOR_FXIGNORE && rec.ignored) { rec.group.visible = false; return; }   /* ★ Lead 20260920：源 FxIgnore=TRUE 的 Model 节点不画 */
          /* ★ Lead 20260920 缺陷修复（浏览器实测 task-80）：本 loop **没有判 `models` 开关** ⇒
             一旦 `models(true)` 把 GLB 载入过，之后 `models(false)` 也照旧每帧 `visible=true`（开关关不回去、
             fail-closed 失效；实测 5 个冻结时刻 `models(F)` 与 `(T)` 逐字节相同）。此处补上开关门，
             **读 `MODELS_FORCE` 的当前值**（`MODELS_ON` 是 attach 时算的局部量，API 事后改 FORCE 时它是陈旧的）。 */
          if (!((MODELS_FORCE === null) ? (effects.models_enabled === true) : !!MODELS_FORCE)) {
            rec.group.visible = false; return;
          }
          var lt = t - rec.start;
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**逐 rec 只读取证可见性覆盖**（默认 null = 逐字走原判据）。
             背景：旧 `__modelIso(name)` 只设一次 `group.visible`，下一帧就被本 loop 覆写 ⇒
             "逐 rec 像素贡献"根本量不到（探针读数与画面不符）。现在 `iso_vis` 非 null 时本 loop 服从它，
             使 `__modelIso()` 成为**真的**逐 rec 隔离开关（只改 visible，不改任何参数）。 */
          var _isoOV = (rec.iso_vis === true || rec.iso_vis === false);
          var _vis = _isoOV ? rec.iso_vis : !(lt < 0 || lt > rec.life);
          if (HONOR_FXIGNORE && rec.ignored) _vis = false;
          rec.group.visible = _vis;
          if (!_vis) return;
          var u = rec.life > 0 ? lt / rec.life : 0;
          var col = sample(rec.color, u, 4);
          /* ★ task-61 / task-90：列序走 mdlRGB（默认 COLOR_ORDER='argb' ⇒ 取列 1..3；alpha=列0）； */
          var rgb = col ? mdlRGB(col) : [1, 1, 1];
          /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 B）：本段与 attachModel 的初始化共用 `modelOpacity()`
             （同一套口径：u_overall_opacity > AlphaMtl_Keyframe > ColorKeyFrame 列0；只补缺失项，
             `u_overall_opacity` 存在时行为与旧版逐字一致）。 */
          var _op = modelOpacity(rec, u);
          var a = _op.val;
          rec.opacity_src_used = _op.src;
          rec.opacity_val = Math.max(0, Math.min(1, a));
          /* ★ task-61：源公式子集 —— 有声明且开关打开时，highlight 因子随帧进入 emissiveIntensity；否则 1 */
          var hvv = sample(rec.hi, u, 1);
          var hmult = (MODEL_HIGHLIGHT && hvv && rec.highlight_src) ? Number(hvv[0]) : 1;
          /* ★ 源级旋转轨道 u_maintex_rotation（本皮肤仅 1/26 节点有）；轴假设=本地 Z，未证 ⇒ 标 approximate */
          var rr = sample(rec.rot, u, 1);
          if (rr) rec.group.rotation.z = Number(rr[0]) * Math.PI / 180;
          /* ★ task-22 记录：曾按 DirType='2' 试过"面向相机(billboard)"（源属性，语义未证）——
             实测**视觉更差**（面片正对相机 ⇒ 大片平白卡），已回退、不保留该分支。
             结论：DirType 的语义仍未定 ⇒ modelTable 记录原值，标 unresolved。 */
          var sf = sample(rec.sf, u, 1); var k = sf ? Number(sf[0]) : 1;
          var xs = sample(rec.sx, u, 1), ys = sample(rec.sy, u, 1), zs = sample(rec.sz, u, 1);
          /* ★ task-61：Model GLB 顶点空间与 sfx 同为 cm 空间 ⇒ 实例必须吃**同一个**单位换算 U()（随 unitScale 开关，可对照），
             源 Scale 轨道只作乘子。源侧数字依据：GLB bbox 最大维度 163.07 / 武器对角线 15.4552 = **10.55×**（直接挂载 ⇒ 铺满视口，
             截图 sha 771B5400A942660A 与"巨三角盖住武器"一致）；×0.1 后 = **1.055×**，与"特效几何与武器同尺度"相符。 */
          var uk = UNIT_SCALE_ON ? ((MODEL_UNIT_SCALE !== null && isFinite(MODEL_UNIT_SCALE)) ? MODEL_UNIT_SCALE : SFX_UNIT_TO_MODEL) : 1;
          uk = uk * DIAG_SCALE_K;   /* ★ 只读取证：默认 1，__scaleAll(k) 只用于量"若 unit_scale=k×"的几何大小 */
          rec.group.scale.set((xs ? Number(xs[0]) : 1) * k * uk, (ys ? Number(ys[0]) : 1) * k * uk, (zs ? Number(zs[0]) : 1) * k * uk);
          /* ★ Lead 20260920：`mtgParams(on)`（默认 OFF）—— 只把发光的**取值来源**换成 `.mtg` 的源参数，
             **不新增任何乘法**（highlight 仍只在 applyModelMaterial 的 L317 处乘一次，避免双重相乘）。
             源值按已解出的 `.mtg` 原样使用（`u_emissivecolor` 为 0–1 浮点，clamp[0,1]；无声明则不改）。 */
          var rgbUse = rgb, hivUse = hmult;
          if (MTG_PARAMS_ON && rec.mtgParams) {
            var me = rec.mtgParams.u_emissivecolor || rec.mtgParams.u_emissive_color || null;
            if (me && me.length >= 3) {
              rgbUse = [Math.min(1, Math.max(0, Number(me[0]) || 0)),
                        Math.min(1, Math.max(0, Number(me[1]) || 0)),
                        Math.min(1, Math.max(0, Number(me[2]) || 0))];
              rec.mtg_color_src = 'mtg:u_emissivecolor';
              rec.mtg_color_val = [rgbUse[0], rgbUse[1], rgbUse[2]];
            } else { rec.mtg_color_src = 'no_u_emissivecolor_declared'; rec.mtg_color_val = null; }
            var hi = rec.mtgParams.u_emissive_highlight_intensity;
            if (hi !== undefined && hi !== null && isFinite(Number(hi))) {
              hivUse = Number(hi); rec.mtg_highlight_src = 'mtg:u_emissive_highlight_intensity';
              rec.mtg_highlight_val = hivUse;
            } else { rec.mtg_highlight_src = 'no_u_emissive_highlight_intensity_declared'; rec.mtg_highlight_val = null; }
          } else if (rec.mtgParams) {
            /* 开关 OFF：源值只登记（供探针读），不参与渲染 */
            var me0 = rec.mtgParams.u_emissivecolor || rec.mtgParams.u_emissive_color || null;
            rec.mtg_color_src = (me0 && me0.length >= 3) ? 'declared_not_applied_switch_off' : 'no_u_emissivecolor_declared';
            rec.mtg_color_val = (me0 && me0.length >= 3) ? [Number(me0[0]), Number(me0[1]), Number(me0[2])] : null;
            var hi0 = rec.mtgParams.u_emissive_highlight_intensity;
            rec.mtg_highlight_src = (hi0 !== undefined && hi0 !== null && isFinite(Number(hi0)))
              ? 'declared_not_applied_switch_off' : 'no_u_emissive_highlight_intensity_declared';
            rec.mtg_highlight_val = (hi0 !== undefined && hi0 !== null && isFinite(Number(hi0))) ? Number(hi0) : null;
          }
          rec.obj.traverse(function (o) {
            var m = o.material; if (!m) return;
            applyModelMaterial(m, rec, a, rgbUse, hivUse);
          });
        });
        raf = requestAnimationFrame(tick);
      }
      raf = requestAnimationFrame(tick);

      var api = {
        fidelity: effects.status || 'partial',
        colorOrder: COLOR_ORDER,
        /* ★ FXADAPT 审计字段：让"渲了什么/缺什么"可被验收脚本直接读，不再用 0 掩盖 */
        nodesTotal: allNodes.length,
        nodeAuditByTag: tagCount,
        nodeRenderedByTag: renderedCount,
        unsupportedCount: notRendered.length,
        unsupportedNodes: notRendered,
        particleNodesInSource: (tagCount.ParticleRes || 0) + (tagCount.ParticleSystem || 0),
        modelNodes: modelRecs.length,
        modelsLoaded: modelRecs.filter(function (r) { return r.state === 'ok'; }).length,
        modelsFailed: modelRecs.filter(function (r) { return r.state === 'load_fail' || r.state === 'no_loader'; }).length,
        modelsNoMeshField: modelRecs.filter(function (r) { return r.state === 'no_mesh_field'; }).length,
        modelsBase: MODELS_BASE_OVERRIDE || 'manifest-relative(sfx/model/<stem>.glb)',
        spriteSizeBasis: 'adapter_constant: radius*0.035（**无源依据**：源 Scale/XScale/YScale/ScaleFrame 未抽取）',
        spriteNodes: sprites.length,
        particleSystems: systems.length,
        particleSystemsActive: systems.filter(function (s) { return s.drivable && !s.ignored; }).length,
        particleSystemsUndrivable: systems.filter(function (s) { return !s.drivable; })
          .map(function (s) { return { name: s.node.name, why: s.why }; }),
        ignoredParticleNodes: systems.filter(function (s) { return s.ignored; }).map(function (s) { return s.node.name; }),
        setTime: function (v) { fixedTime = (v === null || v === undefined) ? null : Number(v); if (fixedTime !== null && !raf) raf = requestAnimationFrame(tick); },
        seed: function (v) { rngSeed = (Number(v) || 1) >>> 0 || 1; },
        setEnabled: function (on) {
          enabled = !!on; group.visible = enabled;
          if (enabled) { t0 = performance.now(); if (!raf) raf = requestAnimationFrame(tick); }
          else if (raf) { cancelAnimationFrame(raf); raf = 0; }
        },
        dispose: function () {
          disposed = true;
          if (raf) cancelAnimationFrame(raf);
          sprites.concat.apply(sprites, systems.map(function (s) { return s.pool; })).forEach(function (sp) {
            if (sp.material.map) sp.material.map.dispose(); sp.material.dispose();
          });
          if (group.parent) group.parent.remove(group);
          sprites = []; systems = []; texCache = {};
        },
        /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**内部探针外挂点**。
           事实（tokenizer + 浏览器 ownPropertyNames 双重实测，见报告 §1）：本文件的对象字面量在
           `attach` 之后被 24 条 `WikiSfxAdapter.xxx = …` 顶层语句「吃掉」，那些赋值**实际落在 attach 的
           函数体里**（被 `var` 提升成局部函数）⇒ 外部只看得到 7 个 key，`__probe/__sfxDiag/__modelIso/
           __modelDiag/__unresolvedSourceInputs/__modelsAll` 全部 undefined，且对 `__modelIso` 的调用
           （tick 里的 `rec.iso_vis` 覆写门）**完全无效**。
           本改动**不改任何结构/渲染**，只把 attach 内已经存在的那几个**纯只读/只改 visible 的**函数**挂到返回的
           api 上**，让页面探针（Lead 的验收闸门）能读到真实状态。渲染路径一行未动。 */
        __probe: (typeof __probe === 'function') ? __probe : function () { return { err: 'no_probe_internal' }; },
        __modelDiag: (typeof __modelDiag === 'function') ? __modelDiag : function () { return { err: 'no_modelDiag_internal' }; },
        __modelIso: (typeof __modelIso === 'function') ? __modelIso : function () { return { err: 'no_modelIso_internal' }; },
        __modelIsoReset: (typeof __modelIsoReset === 'function') ? __modelIsoReset : function () { return { err: 'no_modelIsoReset_internal' }; },
        __unresolvedSourceInputs: (typeof __unresolvedSourceInputs === 'function') ? __unresolvedSourceInputs : function () { return { err: 'no_unresolvedSourceInputs_internal' }; },
        __modelsAll: (typeof __modelsAll === 'function') ? __modelsAll : function () { return { err: 'no_modelsAll_internal' }; },
        __sfxDiag: (typeof WikiSfxAdapter.__sfxDiag === 'function') ? WikiSfxAdapter.__sfxDiag : null,
        modelSrcGate: function () {
          return { gate_on: MODEL_SRC_GATE_ON, gate_state: MODEL_SRC_GATE_STATE,
                   models_require_source_texture_and_scale: (effects.models_require_source_texture_and_scale === true) };
        },
        /* ★ 取证通道：内部直接改 MODELS_FORCE（与 `WikiSfxAdapter.models()` 同语义；默认不调用 ⇒ 行为不变） */
        modelsForce: function (on) {
          MODELS_FORCE = (on === null || on === undefined) ? null : !!on;
          var want = (MODELS_FORCE === true), started = 0, forced = [];
          if (LIVE_RECS) LIVE_RECS.forEach(function (r) {
            if (r.group) r.group.visible = want;
            if (r.src_gate_blocked) {
              if (want) {
                forced.push(r.name);
                if (!r.obj && LIVE_LOAD && r.meshRel) { r.state = 'pending'; LIVE_LOAD(r); started++; }
              }
              return;
            }
            if (want && !r.obj && LIVE_LOAD && (r.state === 'disabled_fail_closed' || r.state === 'pending')) {
              r.state = 'pending'; LIVE_LOAD(r); started++;
            }
          });
          return { force: MODELS_FORCE, loadStarted: started, gate_forced_load: forced };
        }
      };
      /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**把 attach 内部的只读探针暴露到模块级**。
         事实（tokenizer + 浏览器 `ownPropertyNames` 实测，见报告 §1）：本文件的对象字面量把
         `attach` 之后的 24 条 `WikiSfxAdapter.xxx = …` 顶层语句**吞进了 attach 的函数体**（被 `var` 提升
         成局部函数）⇒ 模块级 `WikiSfxAdapter` 只有 7 个 key，`__probe/__modelDiag/__sfxDiag/__modelIso/
         __unresolvedSourceInputs/__modelsAll` 全为 undefined，任何页面探针都读不到真实状态。
         这里**不动结构、不动渲染**，只在 attach 内把已经算好的这几个函数转挂到模块级对象上
         （纯只读函数 + 只改 `group.visible` 的隔离函数 + 与 `models()` 同语义的强制加载通道）。 */
      LIVE_API = {
        probe: (typeof __probe === 'function') ? __probe : null,
        modelDiag: (typeof __modelDiag === 'function') ? __modelDiag : null,
        modelIso: (typeof __modelIso === 'function') ? __modelIso : null,
        modelIsoReset: (typeof __modelIsoReset === 'function') ? __modelIsoReset : null,
        unresolved: (typeof __unresolvedSourceInputs === 'function') ? __unresolvedSourceInputs : null,
        modelsAll: (typeof __modelsAll === 'function') ? __modelsAll : null,
        modelsForce: function (on) {
          MODELS_FORCE = (on === null || on === undefined) ? null : !!on;
          var want = (MODELS_FORCE === true), started = 0, forced = [];
          if (LIVE_RECS) LIVE_RECS.forEach(function (r) {
            if (r.group) r.group.visible = want;
            if (r.src_gate_blocked) {
              if (want) {
                /* ★ 取证强制加载：**state 标签保持显式 disabled**（供验收直读），只额外打 `forced_evidence_load=true`；
                   未加载过的先记下原 state 以便 models(false) 还原。加载完成后回到 'disabled_unresolved_source_texture_and_scale'。 */
                forced.push(r.name);
                if (!r.obj && LIVE_LOAD && r.meshRel) {
                  if (r.evidence_state_saved === undefined) r.evidence_state_saved = r.state;
                  r.forced_evidence_load = true;
                  r.state = 'disabled_unresolved_source_texture_and_scale';
                  LIVE_LOAD(r);
                  r.state = 'disabled_unresolved_source_texture_and_scale';
                  started++;
                } else if (r.obj) {
                  r.forced_evidence_load = true;
                  r.state = 'disabled_unresolved_source_texture_and_scale';
                }
              } else if (r.forced_evidence_load) {
                r.forced_evidence_load = false;
                r.state = 'disabled_unresolved_source_texture_and_scale';
              }
              return;
            }
            if (want && !r.obj && LIVE_LOAD && (r.state === 'disabled_fail_closed' || r.state === 'pending')) {
              r.state = 'pending'; LIVE_LOAD(r); started++;
            }
          });
          return { force: MODELS_FORCE, loadStarted: started, gate_forced_load: forced,
                   note: 'gate 记录的 state 恒为 disabled_unresolved_source_texture_and_scale（取证加载不改标签；见 forced_evidence_load）' };
        },
        srcGate: function () {
          return { gate_on: MODEL_SRC_GATE_ON, gate_state: MODEL_SRC_GATE_STATE,
                   models_require_source_texture_and_scale: (effects.models_require_source_texture_and_scale === true) };
        }
      };
      /* ★ FXADAPT：viewer 的 sfxDiag 只挑 6 个字段，审计明细在这里暴露，验收脚本可直读：
         WikiSfxAdapter.__audit.nodeAuditByTag / unsupportedNodes / missingAssets 等。 */
      WikiSfxAdapter.__audit = {
        skin: (effects.skin && (effects.skin.primary || effects.skin.display_name)) || null,
        status: effects.status || null,
        attachMode: (effects.attach && effects.attach.mode) || null,
        anchor: ANCHOR,
        nodesTotal: allNodes.length,
        nodeAuditByTag: tagCount,
        nodeRenderedByTag: renderedCount,
        unsupportedCount: notRendered.length,
        unsupportedNodes: notRendered,
        particleSystemsInSource: systems.length,
        particleSystemsDrivable: systems.filter(function (s) { return s.drivable; }).length,
        particleSystemsUndrivable: systems.filter(function (s) { return !s.drivable; })
          .map(function (s) { return { name: s.node.name, why: s.why }; }),
        spriteSizeBasis: 'adapter_constant: radius*0.035（无源依据；源 Scale/XScale/YScale/ScaleFrame 未抽取）',
        colorOrder: COLOR_ORDER,
        colorFormatFromSource: effects.color_format || null,
        missingAssets: notRendered.filter(function (u) { return u.tag === 'Model'; })
          .map(function (u) { return { node: u.name, needs: 'ModelName→.gim 本体（未解包）+ .gim 解析器' }; })
      };
      /* ★ FXADAPT：运行时探针（只读），用于回答"为什么静止帧没变化" —— 逐 sprite 的 ready/visible/opacity/scale/世界坐标 */
      /* ★ task-53：只读探针（无渲染副作用）——逐节点 quad 世界尺寸 / 与武器对角线的比 / 是否切片 / blend / 寿命 / 起始 */
  WikiSfxAdapter.__sfxDiag = function () {
    try {
      if (!LIVE_SFX) return { err: 'no_attach' };
      var wd = LIVE_SFX.weaponDiag();
      var now = (LIVE_SFX.fixedTime && LIVE_SFX.fixedTime !== null) ? LIVE_SFX.fixedTime : null;
      var alive = 0;
      var rows = LIVE_SFX.sprites.map(function (sp) {
        var d = sp.userData || {};
        var sz = sp.scale ? (+sp.scale.x) : null;
        if (sp.visible) alive++;
        return { name: d.nodeName, kind: 'sprite', texture: d.texName || null,
                 quad_size_world: (sz === null ? null : +sz.toFixed(4)),
                 quad_raw: (d.quad_raw === undefined ? null : +d.quad_raw.toFixed(4)),
                 quad_clamped: !!d.quad_clamped, clamp_cap: (d.quad_cap === null || d.quad_cap === undefined ? null : +d.quad_cap.toFixed(4)),
                 bbox_vs_weapon_ratio: (wd > 0 && sz !== null ? +((sz * 1.41421356) / wd).toFixed(4) : null),
                 weapon_diag: +wd.toFixed(4),
                 sliced: !!d.sliced, slice_reason: d.slice_reason || null, frames: d.frames || null,
                 frame_index: (d.frame_index === undefined ? null : d.frame_index),
                 blend_mode_used: d.blendUsed || null, life: d.life, start: d.start,
                 visible: !!sp.visible, opacity: (sp.material ? +(+sp.material.opacity).toFixed(4) : null),
                 /* ★ FIX-FXSQUARE 2026-09-21（**只读探针**，不改渲染）：贴图是否真绑上 + UV 变换的实际取值。
                    用途：区分「①切片未生效（有贴图但 UV 错）」「②无贴图 map=null（纯色方块）」
                    「③几何本身是方块」——三者在这两个字段上读数完全不同。 */
                 has_map: !!(sp.material && sp.material.map),
                 map_repeat: (sp.material && sp.material.map) ? [+sp.material.map.repeat.x.toFixed(5), +sp.material.map.repeat.y.toFixed(5)] : null,
                 map_offset: (sp.material && sp.material.map) ? [+sp.material.map.offset.x.toFixed(5), +sp.material.map.offset.y.toFixed(5)] : null };
      });
      var sysRows = LIVE_SFX.systems.map(function (s) {
        var vis = s.pool.filter(function (p) { return p.visible; }).length;
        alive += vis;
        return { name: (s.node && s.node.name) || null, kind: 'particle', in_pool: s.pool.length, visible: vis,
                 rate_source: (s.rate_has_source ? 'xml_attr:ParticlesPerSecond=' + s.rate : 'absent'),
                 alive_now: vis, per_particle_size_min: s.size_min, per_particle_size_max: s.size_max,
                 fallback: (s.fallback_reason || null), sliced_frames: (s.sliced_frames || 0),
                 slice_path: (s.slice_path || null), ignored: !!s.ignored,
                 fx_ignore_honored: HONOR_FXIGNORE,
                 frame_index_last: (s.frame_index_last === undefined ? null : s.frame_index_last),
                 sheet: (s.node && s.node.spr_sheet) || null,
                 quad: (s.pool[0] && s.pool[0].scale) ? +s.pool[0].scale.x.toFixed(4) : null,
                 /* ★ FIX-FXSQUARE 2026-09-21（**只读探针**，不改渲染）：源侧字段 + **逐粒子**贴图绑定/UV 实际值。
                    这是「奇怪的正方体」的定位证据：`pool_map_null>0` ⇒ 该池里有粒子以 map=null 渲染
                    ⇒ SpriteMaterial 无 alpha 形状 ⇒ 屏幕上就是一整块实心色 quad（纯色方块）。 */
                 texture_candidate: (s.node && s.node.texture_candidate) || null,
                 texture_status: (s.node && s.node.texture_status) || null,
                 blend_mode_source: (s.node && s.node.blend_mode !== null && s.node.blend_mode !== undefined) ? s.node.blend_mode : null,
                 min_radius_src: (s.node && s.node.minRadius !== undefined) ? s.node.minRadius : null,
                 max_radius_src: (s.node && s.node.maxRadius !== undefined) ? s.node.maxRadius : null,
                 pool_map_bound: s.pool.filter(function (p) { return !!(p.material && p.material.map); }).length,
                 pool_map_null: s.pool.filter(function (p) { return !(p.material && p.material.map); }).length,
                 pool: s.pool.map(function (p, pi) {
                   var mm = (p.material && p.material.map) || null;
                   return { i: pi, has_map: !!mm,
                     map_src: (mm && mm.image && mm.image.src) ? String(mm.image.src).split('/').pop() : null,
                     repeat: mm ? [+mm.repeat.x.toFixed(5), +mm.repeat.y.toFixed(5)] : null,
                     offset: mm ? [+mm.offset.x.toFixed(5), +mm.offset.y.toFixed(5)] : null,
                     opacity: p.material ? +(+p.material.opacity).toFixed(4) : null,
                     color: (p.material && p.material.color) ? p.material.color.getHexString() : null,
                     quad: p.scale ? +(+p.scale.x).toFixed(4) : null,
                     visible: !!p.visible };
                 }) };
      });
      return { weapon_diag: +wd.toFixed(4), clamp_k: SPRITE_CLAMP_K, sprite_fix: SPRITE_FIX,
               unit_scale_on: UNIT_SCALE_ON, sfx_unit_to_model: SFX_UNIT_TO_MODEL,
               /* ★ 新增（2026-09-20，ENVWIRE）：两个换算系数的**实际生效值**（回归判据）——
                  未设 `effects.particle_radius_to_world` 的皮肤，`particle_radius_to_world_effective`
                  必须**逐字等于** `sfx_unit_to_model` ⇒ 该皮肤粒子尺寸逐像素不变（可复核，不用换文件）。 */
               particle_radius_to_world_config: PARTICLE_RADIUS_TO_WORLD,
               particle_radius_to_world_effective: (UNIT_SCALE_ON
                 ? ((PARTICLE_RADIUS_TO_WORLD !== null && isFinite(PARTICLE_RADIUS_TO_WORLD)) ? PARTICLE_RADIUS_TO_WORLD : SFX_UNIT_TO_MODEL)
                 : 1),
               particle_radius_source: (PARTICLE_RADIUS_TO_WORLD !== null
                 ? 'effects.particle_radius_to_world' : 'fallback:SFX_UNIT_TO_MODEL'),
               color_order: COLOR_ORDER,
               sprites_total: LIVE_SFX.sprites.length, particles_total: sysRows.length,
               alive_now: alive, sliced_total: LIVE_SFX.sprites.filter(function (s) { return s.userData && s.userData.sliced; }).length,
               distinct_textures: LIVE_SFX.sprites.map(function (s) { return s.userData && s.userData.texName; }).filter(Boolean),
               nodes: LIVE_SFX.nodeSummary(), sprites: rows, particles: sysRows };
    } catch (e) { return { err: String((e && e.message) || e) }; }
  };
  /* ★ task-53：精灵/粒子层独立开关（默认 null = 跟随 SFX 总开关；不改任何强度系数） */
  WikiSfxAdapter.sprites = function (on) {
    if (on === null || on === undefined) { SPRITE_ON = null; }
    else { SPRITE_ON = !!on; }
    var tv = null;
    if (SPRITE_ON === null) return { spriteOn: null, note: 'follow_sfx_switch' };
    if (LIVE_SFX) {
      LIVE_SFX.sprites.forEach(function (s) { s.userData.forceVisible = SPRITE_ON; if (!SPRITE_ON) s.visible = false; });
      LIVE_SFX.systems.forEach(function (sys) { sys.pool.forEach(function (p) { if (!SPRITE_ON) p.visible = false; }); });
    }
    return { spriteOn: SPRITE_ON };
  };
  WikiSfxAdapter.__spriteOn = function () { return SPRITE_ON; };
  /* ★ task-53 取证开关（纯开关，默认不变；不影响其它任何系数） */
  WikiSfxAdapter.clamp = function (on) { if (on !== undefined && on !== null) CLAMP_ON = !!on; return { clampOn: CLAMP_ON, clampK: SPRITE_CLAMP_K }; };
  /* task-57：单位换算开关（默认 on；off = 旧行为，供同载入 A/B 负控） */
  WikiSfxAdapter.sprSlice = function (on) { if (on !== undefined && on !== null) SPR_SLICE_ON = !!on; return { sprSliceOn: SPR_SLICE_ON, mode: SPR_FRAME_MODE }; };
  WikiSfxAdapter.sprFrameMode = function (m) { if (m === 'age' || m === 'first') SPR_FRAME_MODE = m; return { mode: SPR_FRAME_MODE }; };
  WikiSfxAdapter.colorOrder = function (m) { if (m === 'rgba' || m === 'argb') COLOR_ORDER = m; return { colorOrder: COLOR_ORDER }; };
  /* ★ task-90：`ColorFramePar` 优先开关（默认 ON；依据见 COLOR_TRACK_PAR 注释）—— false = 回到只读 `color_track`（旧行为） */
  WikiSfxAdapter.colorTrackPar = function (on) { if (on !== undefined && on !== null) COLOR_TRACK_PAR = !!on; return { colorTrackPar: COLOR_TRACK_PAR, rule: 'par_if_nonempty_else_color_track' }; };
  WikiSfxAdapter.unitScale = function (on) { if (on !== undefined && on !== null) UNIT_SCALE_ON = !!on; return { unitScaleOn: UNIT_SCALE_ON, k: SFX_UNIT_TO_MODEL }; };
  /* ★★ 新增（2026-09-20，ENVWIRE）：粒子半径定标的 A/B（默认 = effects.particle_radius_to_world，
     null 时回落 SFX_UNIT_TO_MODEL）。只改"半径换算"，不动位置/速度/寿命/颜色/混合。 */
  WikiSfxAdapter.particleUnit = function (k) {
    if (k === null || k === undefined) {
      return { particleRadiusToWorld: PARTICLE_RADIUS_TO_WORLD, effective: (PARTICLE_RADIUS_TO_WORLD !== null ? PARTICLE_RADIUS_TO_WORLD : SFX_UNIT_TO_MODEL) };
    }
    var n = Number(k);
    if (!isFinite(n) || n <= 0) return { err: 'k 必须是正数或 null' };
    PARTICLE_RADIUS_TO_WORLD = n;
    return { particleRadiusToWorld: PARTICLE_RADIUS_TO_WORLD, effective: n };
  };
  WikiSfxAdapter.psFallback = function (on) { if (on !== undefined && on !== null) PS_FALLBACK_ON = !!on; return { psFallbackOn: PS_FALLBACK_ON }; };
  WikiSfxAdapter.adaptSwitches = function () { return { spriteFix: SPRITE_FIX, clampOn: CLAMP_ON, clampK: SPRITE_CLAMP_K, psFallbackOn: PS_FALLBACK_ON, spriteOn: SPRITE_ON, blend7: BLEND7, honorFxIgnore: HONOR_FXIGNORE, colorOrder: COLOR_ORDER, colorTrackPar: COLOR_TRACK_PAR, spriteClampNeverTriggered_13nodes: true }; };
  /* ★ Lead 20260920：源 `FxIgnore` 语义的 A/B 开关（默认 true = 尊重源禁用）。
     关掉它可复现"未搬该字段"的旧行为（被禁用节点照样画），供裁决。 */
  WikiSfxAdapter.honorFxIgnore = function (on) { if (on !== undefined && on !== null) HONOR_FXIGNORE = !!on; return { honorFxIgnore: HONOR_FXIGNORE }; };
  /* ★ Lead 20260920：运动学 `kinVel` A/B 开关（默认 ON = 源式位移；false = 旧式 `*20`，供负控）。 */
  WikiSfxAdapter.kinVel = function (on) { if (on !== undefined && on !== null) KIN_VEL = !!on; return { kinVelOn: KIN_VEL }; };
  /* ★ Lead 20260920：Model 发光取值改用 `.mtg` 源参数（默认 OFF；只改来源，不新增乘法）。 */
  WikiSfxAdapter.mtgParams = function (on) { if (on !== undefined && on !== null) MTG_PARAMS_ON = !!on; return { mtgParamsOn: MTG_PARAMS_ON, modelHighlight: MODEL_HIGHLIGHT }; };
  WikiSfxAdapter.mtgParamsInfo = function () {
    if (!LIVE_RECS) return { recs: 0, note: 'attach 后才可用' };
    var withP = LIVE_RECS.filter(function (r) { return !!r.mtgParams; });
    var withColor = withP.filter(function (r) { return r.mtg_color_src === 'mtg:u_emissivecolor'; });
    var withHi = withP.filter(function (r) { return r.mtg_highlight_src === 'mtg:u_emissive_highlight_intensity'; });
    return { recs: LIVE_RECS.length, with_mtg_params: withP.length, on: MTG_PARAMS_ON,
             applied_color: MTG_PARAMS_ON ? withColor.length : 0,
             applied_highlight: MTG_PARAMS_ON ? withHi.length : 0,
             declared_color: withP.filter(function (r) { return !!r.mtg_color_val; }).length,
             declared_highlight: withP.filter(function (r) { return r.mtg_highlight_val !== null && r.mtg_highlight_val !== undefined; }).length,
             sample: (MTG_PARAMS_ON ? withColor.concat(withHi) : withP).slice(0, 6).map(function (r) {
               return { node: (r.node && r.node.name) || null, stem: r.mtgStem, shader: r.mtgShader,
                        color_src: r.mtg_color_src || null, color_val: r.mtg_color_val || null,
                        highlight_src: r.mtg_highlight_src || null, highlight_val: r.mtg_highlight_val };
             }) };
  };

  /* ★ FIX-SFXFOLLOW 2026-09-20：逐 rec 只读诊断（**不加任何渲染副作用**）——
     回答"哪个 rec 是白色巨块"需要：世界 AABB 屏幕投影 + group/unit scale + 实际材质。
     这些量 probe 里已有 `measured`，但那是 rec.obj 的**局部** bbox，缺 group 缩放后的世界框 ⇒ 单列此函数。 */
  /* ★ FIX-SFXFOLLOW 2026-09-20：逐 rec 只读**可见性开关**（默认 null = 全部按原判据）。
     用途：把"哪一块是白色巨块"归因到具体 rec（单独显示 / 单独隐藏），**只改 visible，不改任何参数**。 */
  /* ★ FIX-SFXFOLLOW 2026-09-20：只读取证开关 —— 把当前所有 Model rec 的 `group.scale` **乘** k。
     目的：在不改任何数据文件的前提下，量出「若 effects.model_unit_scale = k×当前值」时的几何大小
     （tick 每帧会按 uk 重写 scale ⇒ 本开关的效果只维持到下一帧，属**纯取证**，无持久影响）。 */
  WikiSfxAdapter.__scaleAll = function (k) {
    if (!LIVE_RECS) return { err: 'no_attach' };
    var kk = Number(k);
    if (!isFinite(kk) || kk <= 0) return { err: 'bad_k' };
    DIAG_SCALE_K = kk;                    /* 让 tick 也按同一个 k 缩放（否则下一帧就被写回） */
    var n = 0;
    LIVE_RECS.forEach(function (r) {
      if (!r.group) return;
      r.group.scale.multiplyScalar(kk); n++;
    });
    return { scaled: n, k: kk, diag_scale_k: DIAG_SCALE_K };
  };
  WikiSfxAdapter.__scaleAllReset = function () { DIAG_SCALE_K = 1; return { diag_scale_k: 1 }; };
  /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：逐 rec 只读**隔离/取证**开关（只改 visible，不改任何参数）。
     · `__modelIso()`（无参）⇒ 全部显示 · `__modelIso(null)` ⇒ 全部显示 · `__modelIso(false)` ⇒ **全部隐藏**（"全部关闭"基线）
     · `__modelIso('<name>')` ⇒ 只显示该 rec（其余隐藏）
     实现：`iso_vis` 由 tick 每帧服从（否则下一帧就被时间窗/总开关覆写 ⇒ 读数与画面不符）。 */
  WikiSfxAdapter.__modelIso = function (name) {
    if (!LIVE_RECS) return { err: 'no_attach' };
    var allOff = (name === false);
    LIVE_RECS.forEach(function (r) {
      var v = allOff ? false : ((name === null || name === undefined) ? true : (String(r.name) === String(name)));
      r.iso_vis = v;
      if (r.group) r.group.visible = v;
    });
    return { iso: allOff ? 'all_off' : ((name === null || name === undefined) ? 'all' : String(name)),
             recs: LIVE_RECS.length, override_active: true };
  };
  WikiSfxAdapter.__modelIsoReset = function () {
    if (!LIVE_RECS) return { err: 'no_attach' };
    LIVE_RECS.forEach(function (r) { r.iso_vis = null; });
    return { override_active: false, recs: LIVE_RECS.length };
  };
  /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：Model 层**显式**状态汇总（`__probe` 里字段名沿用历史 `hasObj`，
     本函数把"加载了几个 / 现在真显示了几个 / 各 state 各几个"一次说清，避免"state=ok 却没画"这种自相矛盾）。 */
  /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**机读门禁摘要**（验收脚本可直接比对"被排除的 rec 有显式标注"）。
     只读，不参与渲染。 */
  WikiSfxAdapter.__unresolvedSourceInputs = function () {
    if (!LIVE_RECS) return { err: 'no_attach' };
    var rows = LIVE_RECS.map(function (r) {
      var u = unresolvedSourceInputs(r);
      return { name: r.name, tag: (r.node && r.node.tag) || null,
               source_texture: (r.src_texture ? r.src_texture.state : 'unknown'),
               source_scale: (r.src_scale ? r.src_scale.state : 'unknown'),
               source_color: (r.src_color ? r.src_color.state : 'unknown'),
               unresolved: u.list, src_gate_blocked: !!r.src_gate_blocked, state: r.state };
    });
    return { total: rows.length,
             blocked: rows.filter(function (x) { return x.src_gate_blocked; }).length,
             all_blocked_explicitly_annotated: rows.filter(function (x) { return x.src_gate_blocked; })
               .every(function (x) { return x.unresolved.length > 0 && String(x.state).indexOf('disabled_') === 0; }),
             gate_on: MODEL_SRC_GATE_ON, gate_state: MODEL_SRC_GATE_STATE, rows: rows };
  };
  WikiSfxAdapter.__modelsAll = function () {
    if (!LIVE_RECS) return { err: 'no_attach' };
    var byState = {};
    LIVE_RECS.forEach(function (r) { byState[r.state] = (byState[r.state] || 0) + 1; });
    return {
      total: LIVE_RECS.length,
      has_obj: LIVE_RECS.filter(function (r) { return !!r.obj; }).length,
      obj_visible_now: LIVE_RECS.filter(function (r) { return !!(r.obj && r.group && r.group.visible); }).length,
      explicit_disabled: LIVE_RECS.filter(function (r) {
        return String(r.state).indexOf('disabled_') === 0;
      }).length,
      state_histogram: byState,
      src_gate_on: MODEL_SRC_GATE_ON, src_gate_state: MODEL_SRC_GATE_STATE,
      models_require_source_texture_and_scale: MODEL_SRC_GATE_ON,
      rows: LIVE_RECS.map(function (r) {
        return { name: r.name, state: r.state, hasObj: !!r.obj,
                 group_visible: !!(r.group && r.group.visible), iso_vis: (r.iso_vis === undefined ? null : r.iso_vis),
                 src_texture: r.src_texture || null, src_scale: (r.src_scale ? r.src_scale.state : null),
                 src_color: (r.src_color ? r.src_color.state : null),
                 fallback_reason: r.fallback_reason || null,
                 fail_closed_source_gate: r.fail_closed_source_gate || null };
      })
    };
  };
  WikiSfxAdapter.__modelDiag = function () {
    try {
      if (!LIVE_RECS || !LIVE_RECS.length) return { err: 'no_attach' };
      var T = (LIVE_CTX && LIVE_CTX.THREE) ? LIVE_CTX.THREE : null;
      var out = { count: LIVE_RECS.length, scale_mode: 'unit_scale_on=' + UNIT_SCALE_ON
                  + '; sfx_unit_to_model=' + SFX_UNIT_TO_MODEL + '; model_unit_scale='
                  + (MODEL_UNIT_SCALE === null ? 'null(fallback)' : MODEL_UNIT_SCALE), models: [] };
      LIVE_RECS.forEach(function (r) {
        var row = { name: r.name, cls: r.cls, state: r.state, glb: r.meshRel,
                    unit_scale_used: (UNIT_SCALE_ON ? ((MODEL_UNIT_SCALE !== null && isFinite(MODEL_UNIT_SCALE)) ? MODEL_UNIT_SCALE : SFX_UNIT_TO_MODEL) : 1),
                    group_scale: r.group ? [+r.group.scale.x.toFixed(4), +r.group.scale.y.toFixed(4), +r.group.scale.z.toFixed(4)] : null,
                    local_bbox: measureModel(r),
                    scale_src: { ScaleFrame: (r.sf && r.sf.length) ? r.sf[0] : 'empty_in_source',
                                 XScale: (r.sx && r.sx.length) ? r.sx[0] : 'empty_in_source',
                                 YScale: (r.ys && r.ys.length) ? r.ys[0] : 'empty_in_source',
                                 ZScale: (r.sz && r.sz.length) ? r.sz[0] : 'empty_in_source',
                                 /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：上面四项只反映**适配器读的那一层**
                                    （`model_fields.tracks`）—— `empty_in_source` 字面容易被误读成"源里没有"。
                                    本字段给出**源侧实际在哪一层有值**与是否接线（只读，不改渲染）。 */
                                 _read_layer: 'model_fields.tracks(适配器唯一读取层)',
                                 _source_truth: (r.src_scale || null),
                                 _note: 'scale_src 的 empty_in_source = **适配器读不到**，不等于源里缺失；'
                                        + '见 _source_truth（本皮肤 12/12 在 node.tracks_all.ScaleFrame 有值 [1.0] 但未接线）' },
                    opacity_src_used: r.opacity_src_used || null, opacity_val: (r.opacity_val === undefined ? null : r.opacity_val),
                    blend_src_used: r.blend_src_used || null,
                    mat_on_attach: r.mat_on_attach || null,
                    transparentMode_src: (r.transparentModeSrc === undefined ? null : r.transparentModeSrc),
                    transparentMode_src_src: r.transparentModeSrcSrc || null,
                    color_source: r.colorSource || null, emissive_src: r.emissive_src || null,
                    color_track_first: (r.color && r.color.length) ? r.color[0] : null,
                    color_track_n: (r.color || []).length,
                    alphaMtl: (r.alphaMtlTrack || []).map(function (x) { return x.slice(1); }) };
        if (T && r.obj && r.group) {
          try {
            var box = new T.Box3().setFromObject(r.obj);
            if (!box.isEmpty()) {
              var sz = box.getSize(new T.Vector3()), ct = box.getCenter(new T.Vector3());
              row.world_size = [+sz.x.toFixed(3), +sz.y.toFixed(3), +sz.z.toFixed(3)];
              row.world_span = +sz.length().toFixed(3);
              row.world_center = [+ct.x.toFixed(3), +ct.y.toFixed(3), +ct.z.toFixed(3)];
              /* ★ 判"特效有没有跟着模型转"的关键量：rec 世界中心相对 **模型根** 的偏移向量。
                 跟随 ⇒ 该向量随根四元数一起转（长度不变、方向被根旋转）；冻结在世界坐标 ⇒ 偏移随根"倒转"。 */
              var rr0 = currentRoot();
              if (rr0) {
                var rp = new T.Vector3(); rr0.getWorldPosition(rp);
                row.off_from_root = [+(ct.x - rp.x).toFixed(4), +(ct.y - rp.y).toFixed(4), +(ct.z - rp.z).toFixed(4)];
                row.off_len = +Math.hypot(ct.x - rp.x, ct.y - rp.y, ct.z - rp.z).toFixed(4);
              }
            }
          } catch (e) { row.world_err = String((e && e.message) || e); }
        }
        out.models.push(row);
      });
      return out;
    } catch (e) { return { err: String((e && e.message) || e) }; }
  };

  WikiSfxAdapter.__probe = function () {        var V = THREE.Vector3;
        return {
          enabled: enabled, disposed: disposed, fixedTime: fixedTime, rafActive: !!raf,
          groupVisible: group.visible,
          groupParent: (group.parent && (group.parent.isScene ? 'scene' : (group.parent.isObject3D ? 'object3D' : 'other'))) || null,
          groupMatrixAutoUpdate: group.matrixAutoUpdate,
          groupWorldPos: (function () { var v = new V(); group.getWorldPosition(v); return v.toArray().map(function (x) { return +x.toFixed(3); }); })(),
          sprites: sprites.map(function (sp) {
            var v = new V(); sp.getWorldPosition(v);
            return { name: (sp.userData && sp.userData.nodeName) || null, ready: !!(sp.userData && sp.userData.ready),
                     visible: !!sp.visible, opacity: +(sp.material.opacity || 0).toFixed(4),
                     scale: +(sp.scale.x || 0).toFixed(4), hasMap: !!sp.material.map,
                     matrixWorldOK: !!(sp.matrixWorld && isFinite(sp.matrixWorld.elements[12])),
                     worldPos: v.toArray().map(function (x) { return +x.toFixed(3); }) };
          }),
          systems: systems.map(function (s) { return { name: s.node.name, drivable: !!s.drivable, ignored: !!s.ignored, pool: s.pool.length }; }),
          /* ★ task-61：逐节点规格探针（lead 指定字段：class / glb / drivers_used / tex_bound / opacity / opacity_src / emissive_src / fallback_reason） */
          models: modelRecs.map(function (r) {
            var m0 = null;
            if (r.obj) r.obj.traverse(function (o) { if (!m0 && o.material) m0 = o.material; });
            return { name: r.name, 'class': r.cls, glb: r.meshRel, state: r.state, hasObj: !!r.obj, objVisible: !!(r.obj && r.obj.visible),
                     groupVisible: !!(r.group && r.group.visible), visible: !!(r.group && r.group.visible && r.obj),
                     /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：把"是显式未画 / 还是画了"一次说清（禁止 state:'ok' 与'实际没画'并存） */
                     state_explicit_disabled: (String(r.state).indexOf('disabled_') === 0),
                     forced_evidence_load: !!r.forced_evidence_load,
                     src_gate_blocked: !!r.src_gate_blocked,
                     unresolved_source: (r.src_gate_blocked ? unresolvedSourceInputs(r).list : []),
                     src_texture: r.src_texture || null, src_scale: r.src_scale || null, src_color: r.src_color || null,
                     fail_closed_source_gate: r.fail_closed_source_gate || null,
                     iso_vis: (r.iso_vis === undefined ? null : r.iso_vis),
                     scale: r.obj ? +r.group.scale.x.toFixed(3) : null,
                     drivers_used: (r.drivers_used || []).length, drivers: r.drivers_used || [], unwired: r.unwired || [],
                     omitted_undeclared: r.omitted || [], approx: !!r.approx_reason, approx_reason: r.approx_reason || null,
                     highlight_src: r.highlight_src || null,
                     highlight_state: (r.cls !== 'A') ? 'not_applicable'
                       : (!r.highlight_src ? 'omitted_undeclared' : (MODEL_HIGHLIGHT ? 'applied' : 'disabled_by_modelsHighlight_false')),
                     emissiveIntensity: m0 ? +(m0.emissiveIntensity === undefined ? -1 : m0.emissiveIntensity).toFixed(4) : null,
                     blending_asserted: false,
                     blending_source: 'unresolved: TransparentMode(0/2/5)→混合状态映射表未定证（asm L423-424 只有整体分支）；A 类按 lead 指令取 additive、B 类 normal，两说可切',
                     depth_bias_state: r.depth_bias_state || null,
                     tex_bound: !!r.tex_bound,
                     opacity: m0 ? +(m0.opacity || 0).toFixed(4) : null, opacity_src: r.opacity_src || null,
                     opacity_src_used: r.opacity_src_used || null, opacity_val: (r.opacity_val === undefined ? null : r.opacity_val),
                     has_AlphaMtl_track: !!(r.alphaMtlTrack && r.alphaMtlTrack.length),
                     has_color_alpha_track: !!(r.colorAlphaTrack && r.colorAlphaTrack.length),
                     emissive_src: r.emissive_src || null, diffuse_src: r.diffuse_src || null,
                     spelling_variant: !!r.spelling_variant, confidence: r.confidence || 'high',
                     macros: r.macros || [], effective_gates: r.gates || [],
                     depth_bias_src: (r.db === undefined || r.db === null) ? null : 'u_depth_bias',
                     blending: m0 ? m0.blending : null, depthWrite: m0 ? !!m0.depthWrite : null, depthTest: m0 ? !!m0.depthTest : null,
                     polygonOffset: m0 ? !!m0.polygonOffset : null, polygonOffsetUnits: m0 ? m0.polygonOffsetUnits : null,
                     fallback_reason: r.fallback_reason || null,
                     measured: measureModel(r), expectedSpan: r.expected };
          }),
          modelsOn: (MODELS_FORCE === null ? (effects.models_enabled === true) : !!MODELS_FORCE),
          /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：源级 fail-closed 门状态（探针直读；缺省 off = 旧行为） */
          model_src_gate_on: MODEL_SRC_GATE_ON,
          model_src_gate_state: MODEL_SRC_GATE_STATE,
          models_require_source_texture_and_scale_declared: (effects.models_require_source_texture_and_scale === true),
          models_disabled_unresolved_source: modelRecs.filter(function (r) { return !!r.src_gate_blocked; }).length,
          models_visible_now: modelRecs.filter(function (r) { return !!(r.obj && r.group && r.group.visible); }).length,
          /* ★ FIX-SFXFOLLOW 2026-09-20：特效层挂点跟随的 root 来源（探针直读，证明用的是活引用而非快照） */
          root_source: rootSrc,
          root_is_live_getter: !!getRootRef,
          root_now_name: (liveRoot && liveRoot.name) ? String(liveRoot.name) : null,
          root_now_is_ctx_root: (liveRoot === rootObj),
          group_matrix_auto_update: group.matrixAutoUpdate,
          /* ★ task-22：26 行节点表 —— ModelName/has_Tex0/源值/材质分支/status，供验收直读 */
          modelTable: modelRecs.map(function (r) {
            var b = r.srcBridge || {};
            var col0 = r.color && r.color.length ? r.color[0].slice(1) : null;
            var m0 = null;
            if (r.obj) r.obj.traverse(function (o) { if (!m0 && o.material) m0 = o.material; });
            return { node: r.name, bridgeKey: r.bridgeKey, meshRel: r.meshRel,
                     has_Tex0: !!r.hasTex0, texture_source: b.tex0 || null, color_source: r.colorSource || null,
                     transparent_mode: b.tm, render_bias: b.rb, track_type: b.tt, xml_line: b.line,
                     u_overall_opacity: (b.op === undefined ? null : b.op), u_depth_bias: (b.db === undefined ? null : b.db),
                     u_emissivecolor_src: col0,
                     branch: (r.hasTex0 ? 'textured_failclosed' : 'emissive_unlit_no_texture'),
                     status: r.state,
                     applied: m0 ? { blending: m0.blending, opacity: +(m0.opacity || 0).toFixed(3),
                                     emissiveIntensity: +(m0.emissiveIntensity === undefined ? -1 : m0.emissiveIntensity).toFixed(3),
                                     color: m0.color ? m0.color.getHexString() : null,
                                     emissive: m0.emissive ? m0.emissive.getHexString() : null,
                                     polygonOffset: !!m0.polygonOffset, polygonOffsetUnits: m0.polygonOffsetUnits } : null };
          }),
          textureUnresolved: modelRecs.filter(function (r) { return r.hasTex0; })
            .map(function (r) { return { node: r.name, texture_source: (r.srcBridge || {}).tex0, status: r.state }; }),
          /* ★ 枚举值表探测结论（NOT_FOUND，2026-09-18，chain-auditor；证据 _target_1110171\FXENUM_probe_report.json）
             ★ 明文禁令：**禁止用观测分布反推枚举名** —— 观测分布只能证明"哪些整数取值出现过"，
               不能证明"哪个整数叫什么"；本项保持 unresolved，默认仍关、仍 fail-closed。 */
          modelBranchBasis: {
            /* ★ task-61 口径修正（additive 记录，不覆盖历史结论）：族 = shader\uber_fx_common.fx（两个 .sfx 唯一 shader 路径，
               容器 res.gpk row 15714 / dec 26,799 / flag 2 lz4，已由 renderer-auditor 与我各自复核一致）；
               但 uniform 语义/公式 = **unresolved**（_disasm 968 asm 0 命中）⇒ 本轮：
               A 类自发光+additive、B 类基色+normal、C 类不渲染；opacity 仅取源 u_overall_opacity；强度项(含单帧 50)不接线；
               TransparentMode/RenderBias 枚举值表仍 NOT_FOUND ⇒ 只原样上报，不解释。 */
            task61_rule: 'A(15): emissive=源 u_emissivecolor, additive, depthWrite=false, depthTest=true ｜ B(8): color=源 u_diffuse_color, normal ｜ C(3): 不渲染 fallback_reason=no_color_driver_unresolved',
            task61_sources: 'effects.json Model.model_fields.uniform_tracks（本轮由 FX029_model_keyframes.py 从两个 .sfx 的 <Uniforms><Variables><u_*_Keyframe><Frame Time Value/> 逐帧原样注入：96 轨道 / 254 帧）',
            task61_color_order: "RGB 列序复用 COLOR_ORDER（默认 'rgba' ⇒ 列 0..2）；U5：1110152 时代 Model 路径写死 (A,R,G,B)，两说并存、colorOrder() 一处置换，未定证前不上报为结论",
            'color/emissive': 'source: u_emissivecolor (A,R,G,B)；emissive=rgb，color 置黑以消除 GLB 白色基色（"白块"来源之一）',
            'intensity': 'emissiveIntensity=1（中性恒等）；源 u_emissive_highlight_intensity 的语义=高光项，作全局强度未证 ⇒ 不乘、原值在 modelTable',
            'opacity': 'source: u_emissivecolor[0]/255 × u_overall_opacity（源值>1 属增强，clamp 到 1；源公式未取到 ⇒ residual）',
            'blending': "approximate: TransparentMode '0'→NormalBlending / '2'→AdditiveBlending（映射语义未在源中验证；值为源属性原值；证据与禁令见 enumValueTable）",
            'depth': 'approximate: u_depth_bias→polygonOffset(units=源值)；尺度语义未证 ⇒ 原值在 modelTable',
            'bridge': 'SRC_BRIDGE_1110152（逐节点源值 + xml_line）；运行时字段优先',
            /* ★ 值表探测结论（NOT_FOUND）：已扫范围内不存在 name↔int 值表 ⇒ 现有映射一律标 approximate */
            enumValueTable: 'NOT_FOUND: 枚举值表在已扫范围内不存在'
              + '（① 10 个皮肤 .sfx（XML-like 文本）10/10 命中这 4 个属性名，但取值全是数值字符串、非数值取值 0 个；'
              + '② uber_fx_common.nfx2 里 TransparentMode/RenderBias/DirType/BlendMode 各 0 次，其 enum 只有宏名族 INSTANCE_TYPE_*/NEOX_DEBUG_*；'
              + '③ 客户端 bin 1,017 文件 / 4.26 GB 全扫（含 lifeafter.exe×4，无 >400MB 跳过），409 命中全在第三方库'
              + '（libcef/Chromium/Skia/Qt/ffmpeg），游戏自有模块 0 命中；④ task-30 既有台账：shader 0 / 50MB 脚本配置数据 0）'
              + ' ⇒ 当前映射是 approximate（观测分布，非值表）。全量观测分布（10 个皮肤 .sfx）：'
              + 'TransparentMode {0:213, 2:31, 5:29}；RenderBias {2:114, 0:67, 1:60, 3:35, 4:30, -1:21, 5:6, -2:6, 6:2}；'
              + 'DirType {2:280, 0:55, 7:4, 1:2}；BlendMode {2:32, 8:27, 0:9}；TrackType {0:316, 4:84, 3:14, 1:4}。'
              + '★ 禁令：禁止用观测分布反推枚举名（观测分布不能证明整数↔名字）。'
              + '★ 值表真值来源只剩引擎侧定义/静态逆向，不在本任务口径内 ⇒ 保持 unresolved。',
          },
          modelsOnAtAttach: MODELS_ON, modelsForce: MODELS_FORCE, modelBlend: MODEL_BLEND, modelBlendK: MODEL_BLEND_K,
          /* ★ 材质来源标注：哪几项源级 / 哪几项近似 */
          materialBasis: {
            blending: 'approximate（源 Model 无 blend_mode；三档实拍 A/B 选定 additive）',
            color_rgb: 'source: u_emissivecolor_Keyframe[1..3]（(A,R,G,B) 顺序）',
            opacity_alpha: 'source: u_emissivecolor_Keyframe[0] = A/255（color_format 明写首分量为 A）',
            opacity_maintex: 'source if present: u_maintex{1,2,3}_opacity_Keyframe；本皮肤 1110152 absent ⇒ ×1.0',
            intensity: 'source if present: u_maintex{1,2,3}_brightness_Keyframe/100（0–100 百分比口径；源公式未取到 ⇒ 半源级）；absent ⇒ 回落源 u_emissive_highlight_intensity',
            rotation: 'source if present: u_maintex_rotation_Keyframe（本皮肤仅 1/26 节点）；轴=本地 Z 未证 ⇒ approximate',
            intensityK: (MODEL_BLEND_K === null ? 'none（源级，无自造系数）' : 'approximate(A/B 对照用): ' + MODEL_BLEND_K)
          },
          sourceTracksPresent: (function () {
            var withOpacity = 0, withBright = 0, withRot = 0;
            modelRecs.forEach(function (r) { if (r.mtOpacity.length) withOpacity++; if (r.mtBright.length) withBright++; if (r.rot.length) withRot++; });
            return { nodes: modelRecs.length, with_maintex_opacity: withOpacity, with_maintex_brightness: withBright, with_maintex_rotation: withRot };
          })(),
          /* ★ 原始读数：直接从材质对象读 blending/opacity/emissiveIntensity（用于核对"是否真的生效"） */
          blendConst: { NormalBlending: THREE.NormalBlending, AdditiveBlending: THREE.AdditiveBlending },
          materialSample: (function () {
            var out = [];
            for (var i = 0; i < modelRecs.length && out.length < 4; i++) {
              var r = modelRecs[i]; if (!r.obj) continue;
              r.obj.traverse(function (o) {
                if (out.length < 4 && o.material) {
                  out.push({ node: r.name, type: o.material.type, blending: o.material.blending,
                             transparent: !!o.material.transparent, opacity: +(o.material.opacity || 0).toFixed(3),
                             depthWrite: !!o.material.depthWrite, side: o.material.side,
                             emissiveIntensity: +((o.material.emissiveIntensity === undefined ? -1 : o.material.emissiveIntensity)).toFixed(3),
                             color: o.material.color ? o.material.color.getHexString() : null,
                             hasMap: !!o.material.map });
                }
              });
            }
            return out;
          })(),
          loaderURL: GLTF_LOADER_URL, loaderCandidates: GLTF_LOADER_CANDIDATES, selfURL: SELF_URL, selfURLFrom: SELF_URL_SRC,
          loadErrors: LOADER_ERRORS, modelsBaseOverride: MODELS_BASE_OVERRIDE,
          t: (fixedTime !== null ? fixedTime : ((performance.now() - t0) / 1000) % loop)
        };
      };
      return api;
    }
  };

  window.WikiSfxAdapter = WikiSfxAdapter;
  /* ★ FXADAPT：验证脚本可在 attach 之前就改模型基址（生产默认 manifest-relative） */
  WikiSfxAdapter.setModelsBase = function (b) { MODELS_BASE_OVERRIDE = b || null; return MODELS_BASE_OVERRIDE; };
  /* ★ FXADAPT：Model 总开关（fail-closed；true=开，false=关，null=跟随 effects.models_enabled）
     ★ 修复（2026-09-18，lead 指出）：旧版只翻 `group.visible`，而未加载的 rec 仍停在 disabled_fail_closed
     ⇒ 必须"关开查看器重建"才能加载。现改为 **models(true) 就地触发 loadModel**（无需重建）。 */
  WikiSfxAdapter.models = function (on) {
    if (on === undefined) return MODELS_FORCE;
    MODELS_FORCE = (on === null) ? null : !!on;
    var want = (MODELS_FORCE === true);
    var started = 0, gate_forced = [];
    if (LIVE_RECS) LIVE_RECS.forEach(function (r) {
      /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：**先判源级门禁**，再决定 `group.visible`。
         旧写法无论门禁与否都先 `r.group.visible = want` ⇒ 只要有人（例如验收脚本里的 `models(true)`）
         调一次，被门禁的记录就会被显示出来（实测：白/灰平板 25,176 px 复活、B 项 FAIL）。
         现：门禁记录的可见性**只**由 `modelsForce()` 这条显式取证通道控制；`models(true)` 不再点亮它们。 */
      var gated = !!r.src_gate_blocked;
      if (gated) {
        if (want) { gate_forced.push(r.name); }
        return;   /* 不加载、不改 visible ⇒ 默认态与"被误调 models(true)"都不画 */
      }
      if (r.group) r.group.visible = want;
      /* ★ task-61：C 类即使 models(true) 也不加载、不渲染；★ Lead 20260920：有"别族颜色轨道"的
         改记 `disabled_color_semantics_unresolved`（归因正确，仍不渲染、不猜 slot 语义） */
      if (r.cls === 'C') {
        if (r.color_family_unresolved) {
          r.state = 'disabled_color_semantics_unresolved';
          r.fallback_reason = 'color_slot_semantics_unresolved:' + r.color_family_unresolved.join('|');
        } else {
          r.state = 'disabled_no_color_driver'; r.fallback_reason = 'no_color_driver_unresolved';
        }
        return;
      }
      if (r.hasTex0) { r.state = 'disabled_texture_unresolved'; r.fallback_reason = 'texture_unresolved'; return; }   /* ★ 源贴图未定 ⇒ 即使 models(true) 也不加载 */
      if (!r.color || !r.color.length) { r.state = 'disabled_no_color_source'; r.fallback_reason = 'no_color_source'; return; }  /* ★ 无源颜色 ⇒ 不加载（不默认白） */
      if (want && !r.obj && LIVE_LOAD && (r.state === 'disabled_fail_closed' || r.state === 'pending' || r.state === 'no_mesh_field')) {
        r.state = 'pending'; LIVE_LOAD(r); started++;
      }
    });
    return { force: MODELS_FORCE, loadStarted: started,
             source_gate_on: MODEL_SRC_GATE_ON, source_gate_state: MODEL_SRC_GATE_STATE,
             gate_forced_load: gate_forced,
             note: 'models(true) 是**取证通道**：会强制加载/显示源级门禁标记的 rec；默认（未调用/ false / null）不画' };
  };
  /* ★ task-61：源公式子集开关 API（默认 true；false = 无 highlight 因子的基线，供 A/B 对照） */
  WikiSfxAdapter.modelsHighlight = function (on) {
    if (on === undefined) return MODEL_HIGHLIGHT;
    MODEL_HIGHLIGHT = !!on;
    return MODEL_HIGHLIGHT;
  };
  /* ★ FXADAPT：材质 A/B（'normal' | 'additive'，k=强度系数） */
  WikiSfxAdapter.modelMaterial = function (mode, k) {
    MODEL_BLEND = (mode === 'additive') ? 'additive' : 'normal';
    if (k === undefined) { /* 保持当前强度口径 */ }
    else if (k === null) { MODEL_BLEND_K = null; }        /* ★ null = 源级（不加任何自造系数） */
    else { MODEL_BLEND_K = Number(k); }                  /* 数字 = A/B 对照用近似系数 */
    var errs = 0, firstErr = null;
    if (LIVE_RECS && LIVE_APPLY) LIVE_RECS.forEach(function (r) {
      if (!r.obj) return;
      r.obj.traverse(function (o) {
        if (!o.material) return;
        try {
          /* ★ task-61：切通道时按**源轨道**重取颜色/透明度（旧版直接把现有 color 传回 ⇒ A 类 color 已置黑会被写进 emissive） */
          var cc = sample(r.color, 0, 4);
          var rgb2 = cc ? mdlRGB(cc) : [1, 1, 1];
          var or2 = sample(r.opTrack, 0, 1);
          var a2 = (or2 && r.opacity_src) ? Number(or2[0]) : 1;
          LIVE_APPLY(o.material, r, a2, rgb2);
        } catch (err) {
          errs++;
          if (!firstErr) {
            firstErr = { name: (err && err.name) || 'Error', message: (err && err.message) || String(err),
                         stack: String((err && err.stack) || '').split('\n').slice(0, 3) };
            LOADER_ERRORS.push({ stage: 'model_material', error: firstErr.message, stack: firstErr.stack });
          }
        }
      });
    });
    return { blend: MODEL_BLEND, k: MODEL_BLEND_K, applied: !!(LIVE_RECS && LIVE_APPLY), errors: errs, firstError: firstErr };
  };
  /* ★ FIX-SFXFOLLOW-FINAL 2026-09-20：模块级探针（薄包装；attach 后才有数据，之前返回 no_attach）。
     存在原因见文件内 `LIVE_API` 注释：本文件对象字面量把 attach 之后的赋值吞进了函数体，
     模块级对象拿不到那些函数 ⇒ 这里补一层显式转发，使 `WikiSfxAdapter.__probe()` 等调用能读到真实状态。 */
  function needApi(name) {
    if (!LIVE_API || typeof LIVE_API[name] !== 'function') {
      return { err: 'no_attach(A1:call_after_attach)', probe: name };
    }
    return null;
  }
  WikiSfxAdapter.__probe = function () {
    var e = needApi('probe'); if (e) return e; return LIVE_API.probe();
  };
  WikiSfxAdapter.__modelDiag = function () {
    var e = needApi('modelDiag'); if (e) return e; return LIVE_API.modelDiag();
  };
  WikiSfxAdapter.__modelIso = function (name) {
    var e = needApi('modelIso'); if (e) return e; return LIVE_API.modelIso(name);
  };
  WikiSfxAdapter.__modelIsoReset = function () {
    var e = needApi('modelIsoReset'); if (e) return e; return LIVE_API.modelIsoReset();
  };
  WikiSfxAdapter.__unresolvedSourceInputs = function () {
    var e = needApi('unresolved'); if (e) return e; return LIVE_API.unresolved();
  };
  WikiSfxAdapter.__modelsAll = function () {
    var e = needApi('modelsAll'); if (e) return e; return LIVE_API.modelsAll();
  };
  WikiSfxAdapter.modelSrcGate = function () {
    var e = needApi('srcGate'); if (e) return e; return LIVE_API.srcGate();
  };
  WikiSfxAdapter.modelsForce = function (on) {
    var e = needApi('modelsForce'); if (e) return e; return LIVE_API.modelsForce(on);
  };
  WikiSfxAdapter.selfUrl = SELF_URL;
  WikiSfxAdapter.loaderCandidates = GLTF_LOADER_CANDIDATES;
  function register() {
    if (window.WikiWeaponViewer && typeof window.WikiWeaponViewer.registerEffectsAdapter === 'function') {
      window.WikiWeaponViewer.registerEffectsAdapter(WikiSfxAdapter); return true;
    }
    return false;
  }
  if (!register()) {
    document.addEventListener('DOMContentLoaded', register);
    window.addEventListener('load', register);
    var n = 0, iv = setInterval(function () { if (register() || ++n > 40) clearInterval(iv); }, 250);
  }
})();
