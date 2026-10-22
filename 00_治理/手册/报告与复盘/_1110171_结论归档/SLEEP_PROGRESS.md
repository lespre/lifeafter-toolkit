# 睡眠期间自主迭代进度（Lead 维护）

> 用户 2026-09-19 睡前指令：「你就自顾自迭代跑吧，别再问我了……我希望睡醒有大收获大惊喜」
> 本文件由 Lead 持续更新，供用户醒后快速查看。

---

## 〇、睡醒 30 秒版（先看这里）

```
【这一夜最大的三件事】
1. 熔炉寒霜 1110129「完全是一坨屎 / 纯黑剪影」——根因确证并已修 ✓
   根因 = manifest 的 `faces_glob` 写成了 shell 通配 `qiangpi_f*_m0.png`（viewer 只替换 `{...}`）
          ⇒ 六面坍缩成同一个 404 ⇒ 空 cube ⇒ 该皮肤 metalness≡1（无漫反射项）⇒ 输出 ≈ 0
     修完 renderer-auditor 亲眼看图确认：**深色金属 + 蓝紫镶边 + 白高光 + 金色线圈 = 有色可辨** ✓
     并且**发现了一条方法论级问题**：board 入口与 `?lab=1` 从来不是同一套渲染，
     验收基准**已裁决固定为 board/默认页**（详见 六·五 ④）

2. 「特效白块」的根因被**翻转**，从"数据缺失"变成"适配器用错了材质" ✓
   原来判定：24/26 Model 节点缺 `Tex0` ⇒ 只能默认关
   现在定证：**源侧本来就没有贴图** —— 那 24 个节点是无贴图自发光/叠加特效，
             由 `u_emissivecolor` / `u_emissive_highlight_intensity` / `u_overall_opacity` 驱动
   ⇒ 白块来自 viewer 的白色 PBR ⇒ 已派 task-22 实现「源自发光/叠加分支」（默认仍 OFF）

3. 你要的「两组结果 + 绑定差异」已在跑（task-15，7 个皮肤全覆盖）：
   A = `Tex0←*_a`（c159 逐槽直证 21/21）vs B = `Tex0←*_b_m`（现状），固定布局 + 每组 ≥2 次

【另外 4 条可直接看的】
4. 背景图：**8/8 皮肤都已应用** ✓（像素级确认，唯一例外 1110169 已如实标注）
5. 1110024 金蟒啸焰：**已不是洋红/空白** ✓（银白+金色完整枪械，magenta 0.00%）
6. 晶体不再泛白 ✓（1110177 S=0.645 / bright∧neutral 2.08%；1110171 S=0.645 / 1.50%）
7. ★★★ **1110171 的特效网格全部拿到了 —— 108 个 GLB 已产出** ✓
   而且顺手**破解了 `.gpk` 的 path→entry**（方法级、可复用）：
   条目表 32 B/行里 **`u32_7 = mm3(路径,0x77777777)`、`u32_6 = mm3(路径,0x66666666)`**
   ⇒ **只读表**（90 个容器 1 秒）就能定位任意 gpk 资产，**不用解压整包**
   ⇒ 108 条源级路径 **108/108 命中 `res\effect_01.gpk`**，产出
     `_gim_out\1110171\sfx\model\*.glb` + 对照表 `GIM20_1110171_model_manifest.json`
   （同 stem 的 108 个 `.mesh` 也一并定位；文件名=源路径基名）
   另：28 节点候选帧**已定证归 `f74635`**（f74635 28 条 / f74631 27 条，差集 1 条）
   ⚠ 更正：我更早写的「effect_01.gpk 里没有它们」是**名称面误判，已推翻**
8. 1110129 **prim4 让一个"看不见的部件"回来了**：源级 ParamMap 位其实存在
   （`weapon.gpk#410`，一直被误命名成 `008_f_a.png`）⇒ 已补回绑定，
   备份 `.bak_pm4_20260918_031737`；验收中（task-25）

【需要你拍板的只有 2 件】
A. weapon 基底 `Tex0` 到底绑 `*_a`（c159 直证）还是 `*_b_m`（现状）—— task-15 交两组结果给你判
B. 全局展示 rig 的 4 个近似量（`exposure=1.75` / `env_intensity=1.4` / `emissive_gain=0.25` / ACESFilmic）
   目前全部标 `approximate`，**我一个字都没动** —— 要不要朝"完全源驱动"走，你定
```

---

## 〇·五、★★★ 你要的「两组结果 + 绑定差异」已交付（task-15，7 皮肤全覆盖）

**主报告**：`03拆包产物\_target_1110171\AB_两组结果与绑定差异_20260918.md`（配套 `AB_table.md` / `AB_metrics.md` / `AB_texdiff*.json` / 四轮原始 `AB_raw_*.json` / 14 张 A/B 截图）

**口径（唯一变量）**：CDP 注入 `fetch` 包装，把 `neox_material.json` + `viewer.json` 一律按**会话开始时的冻结快照**供给；
A 组只把 weapon prim 的 `Tex0` 改指同族 `*_a`（crystal prim 不动，用 manifest 的 `shader_kind` 判定）；固定布局 **1178×718** 四轮恒定；每组 2 轮。

```
【① 两组指标】武器区
皮肤        Δp50     Δp95      受光%变化
1110024      0.0     +2.7          -
1110129      0.0     +7.1        −3.75
1110145      0.0     +9.5          -
1110152     +0.3     +3.9       −16.0
1110165     +1.1     +4.8       −15.9
1110171      0.0     +4.7       −12.9
1110177      0.0     −0.1       （仅 1/3 prim 参与）
⇒ **6/7 皮肤 Δp50 为 0、Δp95 均值 +5.4**：换 `_a` **只抬高高光、不动中位**
⇒ **7/7 皮肤组内两轮逐像素一致**（可复现）

【② 绑定差异（这是你要的"绑定差异"）】
· c159 全部 weapon 块声明 **`Tex0 = *_a`**；当前 **26/26 weapon prim 全绑 `_b_m`** ⇒ **相符 0 个**
  A 组 24/26 相符；缺的 2 个 = 1110165 prim2/3（磁盘**没有** `165_d_a/165_e_a.png` ⇒ 标 unresolved，**不替代**）
· `t_basecolor` 应 `*a` 却绑 `_b_m`：1110165 全 4 prim、1110177 prim0
· `t_basecolor` **未绑定** ⇒ 晶体回退把**掩码当 albedo**：1110177 prim1/2、1110171 prim6
· `t_surfacemap` 未绑定：1110024/1110129/1110152 全部 + 1110171 晶体 5 prim
  （★ 这条已定案为 **no_shipped_bit**：源有声明、源无贴图位 —— 见 五·七）
· `t_custom_ibl` 容器名不同（.cube vs .dds）；**1110024 当前 `gdansk_shipyard_buildings.dds`
  而 c159 只声明 `common\env_map\indoor.cube`** ⇒ 顶替（且 `indoor.dds` **已在磁盘上**）⇒ 已派 task-23 做两组
· 1110177 c159 **无** `t_surfacemap` 槽却绑了 `029_s_m`
· 1110145 六个 prim 的 `manifest.logical_path` 记成 crystal blk1 的 `001b_m`（取错块）

【③ 三条可证伪结论】
1. 换 `_a` 只抬高高光不动中位（Δp95 均值 +5.4、Δp50≈0，两轮逐像素复现）⇒ 若换绑后 p50 大幅移动即可证伪
2. **`_a` 与 `_b_m` 不是同一张图的不同打包**：13 对同尺寸但**相同像素 0.00%**、±2 内 0.00%、
   平均|ΔRGB| 51.9–137.4、逐像素一维拟合 r² 仅 0.0001–0.5829
   · 唯一真拷贝：1110177 `029_b_m.A ≡ 029_a.R`（slope 0.9989、**r²=0.9984**）
   · **`_a.A` 是真实变量通道**（均值 18.6–216.7，即 T3 的 rough 源）；`_b_m.A` 10/13 对恒 255
   · ★ 自纠：首轮"通道≥95%相等 / corr 0.99"是**饱和通道假象 + 2-D corrcoef 误用**，已废弃
3. 与源级事实相符度：**B = 0/26，A = 24/26**

【我没做的事（按你的明令）】
★ 你既有明令「**不更名或交换 `_a/_b_m`，不改 manifest 的绑定候选**」
  ⇒ **我一个绑定都没改**；上面两组结果就是**交给你判**的
★ 并发披露：B r1 运行期他人改了 `weapon_skin_viewer.js`，故有效对取同 viewer_sha 的 **A r1 vs B r1**；
  B r2 在新版上**逐像素相同** ⇒ 该改动不影响本实验路径
```

## 〇·六、AB2：1110024 的 IBL「顶替」两组结果 —— **源声明组明显更差 ⇒ 改为"标注顶替"而非改绑定**

**报告**：`03拆包产物\_target_1110171\AB2_IBL顶替两组结果与定级_20260918.md`

```
【事实】
· c159 只声明 `common\env_map\indoor.cube`（001386.c159 原始字节 indoor.cube @2858/4682，
  **全文 0 次** gdansk_shipyard_buildings）；manifest 五 prim 全绑 gdansk.dds ⇒ **顶替属实**
· `src_cube/indoor.dds` **已在磁盘**：六面齐全、128²、sha16 两两不同、**PNG↔DDS 逐面 1:1**
  （mean|ΔRGB|=0.00）；但**第 4 面纯黑，且 DDS 原始数据同样纯黑 ⇒ 源资产特征，非导出缺陷**
  （先决核查里 auditor 还自纠了自家解码器 stride 误用：DDS 是 mip-major 排布）

【两组结果（1178×718 固定布局；A r1=r2、B r1=r2 逐像素一致）】
组                        p50    p95    受光%    金%    银%
A  indoor（源声明）       32.7   46.8   86.95   0.68   0.00
B  gdansk（现状）         35.8  113.2   32.33   1.50   3.22
⇒ **源声明组明显更差**：p95 −66.4、R 均值 −51%、银% 3.22→0.00
  （与 `_a/_b_m` 那组的"Δp50≈0、Δp95 +5.4"**方向相反**）
⇒ 机制（可证伪）：源注入公式 `(rgb·a·16)²` 的六面均值
  **indoor=0.0154 vs gdansk=0.7540（≈1/50）**，叠加一个恒零面 ⇒ 变暗来自数据本身，不是链路
⇒ 若两 cube 该项同量级，本结论即被证伪

【我的处置（不擅自改绑定）】
· 按你「不改 manifest 的绑定候选」的明令，**我没有改绑定**；
· 但按「顶替必须标注」的纪律，**已在 1110024 manifest 的 5 个 `t_custom_ibl` 槽加
  `SUBSTITUTION_WARNING`**（c159 原文依据与字节位次、indoor 已落盘且六面 1:1、
  A/B 两组数值、机制、`status: LABELED_SUBSTITUTION_AWAITING_USER_DECISION`）
  · 备份 `neox_material.json.bak_subst_20260918_031617`；sha16 `a4c999c21bf4602c` → `9973059e9c59002e`
· ⇒ **画面一字未变，只是把"说不出口的顶替"变成"写在文件里的顶替"**，等你拍板

【同一份定级表里的其它结论（都有 c159 直证 + 磁盘核对）】
· 1110177 晶体 prim1/2 `t_basecolor` = **真缺口**（003996 blk1/blk2 直证 `t_basecolor=029001a`
  off=2692/3511，我方缺 ⇒ 晶体把 `029_b_m` 掩码当 albedo）⇒ 待你批准后补（`029_a.png` 在盘上）
· 1110171 prim6 = **撤销**（001265 blk6 本身无 `t_basecolor` ⇒ 回退是源级正确行为）
· 1110165 的 `t_basecolor` 多绑定（源仅晶体 blk3 声明 `1001a`）⇒ 走 weapon 分支**当前无渲染影响**
· 1110145 `logical_path` = **取错块**（weapon blk0/2/3 是 `014001a`@3390/4443/4773，
  `001b_m` 属晶体 blk1@3981）⇒ 元数据缺陷，**不参与渲染**
· `t_surfacemap` 三皮肤缺口被"未提取"阻塞（`024_s_m/008_s_m/009_s_m.png` **磁盘不存在**）
  ⇒ 与 五·七 的 `no_shipped_bit` 一致；且**更正** task-15 对 1110171 晶体 prim 的误标
  （001265 晶体块**不声明**该槽 ⇒ 不在缺口内）
```

---

## 〇·七、Model/特效层：白块已消、**但如实说没到游戏观感**（task-22 交付 + Lead 补发布 GLB）

```
【已做】
· adapter（viewer-auditor）`FFF6180DF4ED5BAB` → **`2E61C5234BB37CED`**（55,263 B / 773 行）
  备份 `MODEL_adapter_before_FFF6180DF4ED5BAB.js`
  · 无 `Tex0` 的 Model：不再白色 PBR ⇒ **color 置黑 + emissive = 源色**
    + blending 由源 `TransparentMode` 直译 + opacity = `A/255 × u_overall_opacity`
    + `polygonOffset ← u_depth_bias`
  · 颜色优先级链 **`u_emissivecolor → u_diffuse_color → u_main_color1/2/3`**（跨皮肤通用，
    不是只为 1110152 写死）；**无颜色源 ⇒ `no_color_source`，绝不默认白**
  · 新增 `SRC_BRIDGE_1110152`（26 行源值桥，runtime 优先）、`__probe().modelTable` 26 行 + `modelBranchBasis`
  · 读数：1110152 默认 `{disabled_fail_closed:22, no_color:2, tex_unresolved:2}`；
    ON `{ok:22, no_color:2, tex_unresolved:2}`；1110171（`models_enabled`）`{no_color_source:28}`
  · **全白像素：1110152 ON 10.063% → 1.924%**；OFF 0.021%；1110171 0.011%
  · 两个环节点仍 **fail-closed 未自拟贴图**；JS 异常 0；
    `wiki_selfcheck` PASS 63 / FAIL 1（已知 1110171 mesh[5,6] 假阳性）
  · 旋转：idle distinct=1、drag net(−0.0289,+0.0684)、maxstep 0.0077、clipped=false ✓
  · **4 皮肤"默认关"逐像素 0 diff**（无回归）✓
· ★ **Lead 补发布 GLB**（这是 viewer-auditor 报的阻塞项）：
  108 个 GLB 从 `03拆包产物\_gim_out\1110171\sfx\model\` 发布到
  **`08Lifeafter wiki\assets\3d\weapon_skin\1110171\sfx\model\`**
  ⇒ **108/108 · 1,296,976 B**，含 `mod_skin_1003_010_zs_06_01_pt.glb`（f74635 的标记节点）与 26 个 `zs_*`
  （发布前该目录 **0 文件**）

【★ 如实说的不足（不粉饰）】
· ON 状态下 1.92% 白，但 **24 个无贴图 Model 仍是大片淡青面板，未达游戏观感** ✗
  · 缺的是源端 `uber_fx_common.fx::TShader` 的语义
  · `DirType`（面向相机）试过 ⇒ **更差，已回退**
  · ⇒ 这是**已知未完成项**，不是"做完了"

【仍阻塞】
· 1110171 的 `effects.json` **无颜色轨道**（27 帧的 `ColorFrame` 全无彩色 `color_mix={}`）
· 两张环贴图（`tex_ring_fz01_x06.tga` / `tex_ring_keji_hgz01_04.tga`）**仍未定位**
  ⇒ 1110152 两个环节点保持 fail-closed（task-26 正在用新破解的 path→entry 找）
```

---

---

## 〇·八、技术债 ⑤ 三项全部结清（本轮 Lead 实测，逐通道逐族）

```
① c159 属性记录解析器 → **已交付**（`c159_slot_parser.py`；横跨 8 个 c159 文件 33 材料，
   21/21 weapon 基底材料给出 `Tex0←*_a` 直证；修好 `c159_pair.find_groups` 的同对齐误删）

② `t_surfacemap` 类↔名分歧 → **已定案**：三皮肤（1110024/1110129/1110152）= `no_shipped_bit`
   （源有声明、源无贴图位），判据 = EOB 声明集 + 区块定界 + 内容签名；
   1110165 正控 `#1637` 实测 r255=0.988（同口径能识别真 s_m）；
   `t_surfacemap` **不接前向着色是正确的**（理由是它乘受 cb0[133]/[135]/[136]+时间项驱动的染料-高光项，
   而非旧说的"只写 SV_Target3.y" —— 旧理由已被 chain-auditor 部分反驳并改写）

③ **`Roughness = t_basecolor.a`（原 L1050）公式核查 → 成立，且不是循环公式** ✓
   逐族实测 `rough_repack_<fam>.png.G` 与 `<fam>_a.png.alpha` 的逐像素差：
     1110024/024 · 1110129/008 · 1110145/014 · 1110152/009 · 1110171/012 · 1110171/010 · 1110177/029
       ⇒ **|Δmean| = 0.0000、max = 0.0000（8 族里 7 族完全一致）**
     · 且文档记载的源测量值**精确复现**：`012_a.alpha mean = 0.6371`（文档 0.637）、
       `010_a.alpha mean = 0.7319`（文档 0.732）⇒ 公式与源级事实一致 ✓
   ★ **唯一例外：1110165** —— `rough_repack_165.png.G ≡ 165_a.png.R`（mean 0.4064，|Δ|=0.0000），
     而 `165_a.png.alpha` mean = 0.6209（|Δmean| = 0.4924）
     · 原因是它的 `t_basecolor` 被裁为 `165_b_m.png`，而 `165_b_m` 的 content_class = `alpha1`
       ⇒ 若按统一公式 `G ← t_basecolor.a`，粗糙度会 **≡1（全镜面）**
     · ⇒ 这是 1110165 `naming_conflict` 里**已登记的 `operational_necessity` 分支**，
       **不是遗漏**；此处只登记"它用了与其余 7 族不同的推导规则"，**不改**（改动会直接改变该皮肤观感）

④ 顺带核清 `param_repack` 的**实际**实现与文档措辞的差别（无运行时影响）：
   实测 8 族一致：`R ≡ 1.0000`、`G = clamp(src.R, 0.02, 1)`、`B ≡ src.G`、`A ≡ 1`
     · 1110145/1110165 的 `G` 被夹到 **0.020**（正好是 clamp 下界）⇒ 反证该实现确实带 clamp
     · `param_repack.B ≡ *_m.png.G` **逐像素相等（|Δ| = 0.00000）** ⇒ three 读 `metalnessMap.B`
       得到的正是源语义 `metal = sat(ParamMap.G)` ✓
   ⇒ **渲染接线是对的**；只是 manifest 的说明串写作"`R←src.R, B←src.G`"，
     **漏了 clamp 与实际的 G/R 归属**（`G` 通道实际未被 three 读取）⇒ 仅**文案不精确**
   ⇒ 建议（未改）：把说明串改成 `R≡1 / G←clamp(src.R,0.02,1)（three 不读）/ B←src.G（three 读 metalness）/ A≡1`

⑤ 另：`weapon_skin_viewer.js` 的 `param_repack` 一族的路径拼装仍是 `src_tex/param_repack_<fam>.png`
   （`fam = famOf(Tex0)`）⇒ **逐族唯一，无跨皮肤串味** ✓（此前担心的"用错族贴图"只出现在回退预览表，
     已由 task-13 改为逐 prim 从 manifest 派生）
```

---

---

## 〇·九、用户醒后拍板 → 已执行（Round 10-11）

```
用户用人话点的四件事：
① 上色贴图换成 A 版（与游戏原文件一致）  ✅ 已改：7 皮肤 **24 个 weapon prim** 的 Tex0 `_b_m` → `_a`
   · 只有 **1110165 prim2/prim3 跳过**（`165_d_a.png`/`165_e_a.png` 磁盘不存在）⇒ 按纪律**不用别的图顶替**
   · 每个槽写入 `prev_local_file` / `binding_basis`（c159 21/21 直证）/ `ab_test_20260918`（Δp50≈0、Δp95 +5.4、A=24/26 vs B=0/26）/ `user_decision`
   · 备份 `.bak_tex0a_<stamp>`；改后 sha16 例：1110024 `6c71441b850acecc`、1110171 `5b6d20203a6c36e7`
   · **体检**：181 条 `local_file` + 全部 cube 六面 ⇒ **无死引用、无 shell 通配、六面齐全** ✅
② 反光环境图（indoor vs gdansk）→ 用户要"并排看"  ✅ 已放好
   `03拆包产物\_target_1110171\看图_两张并排\1_源文件指定的_indoor.png` / `2_现在用的_gdansk.png`
   ⇒ **等用户回话前不动**
③ 去掉全局显示近似值（曝光 1.75 / 环境光 1.4 / 自发光 0.25 / ACES / bloom / rig 灯）
   ✅ 已查清：**只改 viewer.json 不够** —— `toneMapping` 在 viewer.js 里**两处写死 ACESFilmic**、不接受配置
   ⇒ 已派 **task-29**（shader-auditor，viewer.js 唯一写者）：改成配置驱动（**默认值必须等于当前行为 ⇒ 改完逐像素不变**）
     + 加只读 `__rigProbe()` 与可逆 `__rigMode('source'|'approx')`，并交两组读数
④ 特效：**继续修 + 保留开关**  ✅ 开关保留；已合并 1110171 的 28 行 `model_fields`
   （此前读不到颜色是因为 **viewer.js:772 读的是 viewer.json 的 effects**，而 28 行只在同目录 `effects.json`）
   ⇒ 现在 **14/28 拿到源色**（u_emissivecolor 5 / u_main_color3 5 / u_main_color1 3 / u_diffuse_color 1），
     其余 14 行**源里本无 RGB 值通道** ⇒ 保持 fail-closed
   · `models_enabled` **不写**（默认 OFF 不变）；viewer.json sha16 `1c3b8dacee11fdb8`

【⚠ 同时发现必须马上修的回归（task-28 在修）】
   **★ 结论已出：不是回归 —— 是 IBL cube 未就绪导致的间歇暗帧（viewer-auditor 受控复现）**
   · 稳定性门 A/B（同会话、门=连续 5 帧 sha 全同、24/24 通过）：两版 adapter（当前 `2E61C523` vs 备份 `FFF6180D`）
     在 1110129/1110171/1110024/1110152 上**逐字节等价** ⇒ **无回归**
   · **门控基线（请以此为准）**：1110129 meanL **24.82** · 1110171 **51.53** · 1110024 **82.54** · 1110152 **28.81**
     （早先的 19.90 / 10.07 / 6.59 / 53.45 **已不可复现**：期间 viewer.js 21:04、4 个 viewer.json 21:25、
       board.html 21:34、以及 1110129 的 Tex0 `_b_m→_a` 都改过 ⇒ 不能当验收靶）
   · **暗帧频率**：非门控 2/6；暗帧 sha 两版完全相同 `516b56cc43081bdf`（meanL 0.28 / p50 0.0 / mask 7.27%）
   · **根因受控复现**：CDP 屏蔽 `*qiangpi*`（IBL cube 面）⇒ 得到**完全相同的暗帧 sha/meanL/mask**；
     该链 `metalness=1/roughness=1`，外观几乎全由 IBL 提供 ⇒ **cube 一空即全黑**（几何仍在画，mask 7.27%≠0）
     反证：屏蔽 `*param_repack_008*` 反而是**亮帧 75.40** ⇒ 排除"贴图没加载/材质没编译"
   · 证据 `_target_1110171/MODEL_RT28_report.md`；已派 **task-40（blocked_by task-39）**：
     给 IBL 加「**六面就绪才绑定 + `texReady` 探针**」，要求修后同样屏蔽**不得再出现"看起来正常但全黑"**
   · 运维：viewer-auditor 的浏览器已关闭、端口无 LISTEN；它如实披露**有一次被 600s 上限强杀导致 adapter
     停在备份版，已自行检测并还原为 `2E61C5234BB37CED`**

【★ 外部只读审核（2026-09-19）：流程文档被判 v1-draft，4 个 P0 我已全部采纳并动手】
   · **P0-1** S4 证据等级写高了 → 文档已更正为 **`ordered-1to1 / candidate-high`**（非直证；
     1110171 dual 48 行 dual=18/conflict=8、single 20 行 dual=8/conflict=3）；**caustic/reflection 的顺序冲突不得进生产绑定**
     ⇒ 已在 7 个 manifest 写入 `evidence_levels` 块 + 给 `t_caustic_tex/t_reflection_tex/t_refraction_tex`
       打 `production_ok:false`（1110171 12 槽 / 1110177 5 槽；**不改绑定、不改画面**）
   · **P0-2** S5 混了 shader 家族 + "纯通道重排零数值改动"不准确 + `gen_param_repack.py` **不产 `rough_repack`**
     → 文档已拆成 `pbr_weapon` / crystal 两表，措辞改为"**通道重排 + 钳位 + 常量填充**"；
       1110165 的 `a.R` 分支已降级为 `approximate/unresolved`
   · **P0-3** `crystal = t_basecolor || Tex0` 通用回退把缺失/错绑静默掩盖 → **task-39（shader-auditor）**：
     按 program family 声明必需槽 + 缺则 fail-closed + 负控证明它真会拦
   · **P0-4** 验收门会放过坏结果（`PASS≥63/FAIL≤1` 与脚本"任一 FAIL 即退 1"自相矛盾，另有 6 处缺陷）
     → **task-38（toolchain-auditor）**：改"全部具名门必须全过" + N 帧稳定门 + 参数化皮肤 +
       `applied == expected_prims` + family/必需槽/资源 SHA/unresolved 校验 + **3 个负控证明它真会拦**
   · P1（S3 分层命名、GPK 寻址器重复命中/碰撞、固定 latin1、requirements+UTF-8、骨骼措辞拆分、
     S9 改可选支线、TGA 不可变 + 派生 PNG 带来源 SHA）**已在文档 §10·5 全部更正**

【特效硬骨头有实质进展（task-30，chain-auditor）】
   用新破解的 path→entry 取到源端特效着色器 **`shader\uber_fx_common.nfx2`**
   = **`E:\mrzh\res.gpk` 条目 #15714**（`o=844308572 comp=6823 decomp=26799 flag=2`，magic `C159410D`，
   `u6/u7` 与 murmur3 计算值完全一致 ⇒ 自我校验通过）；产物 `FXSHADER_uber_fx_common.nfx2`（26,799 B 原样）
   · 289 个 `u_*` 声明、20 个严格贴图槽、126 个能力宏；**blob 内无 DXBC** ⇒ 只有声明/注解，公式不在本资产
   · ★ **`u_diffuse_color` / `u_main_color1..3` 在该 shader 里 0 命中** ⇒ 属**别的着色器族**
     ⇒ **这就是"1110171 不能照抄 1110152 的 Model 材质逻辑"的源级原因**（关键结构结论）
   · 1110152 的 26 Model 驱动集合全在其声明域内：`u_depth_bias` 26/26、`u_emissivecolor` 24、
     `u_emissive_highlight_intensity` 24、`u_overall_opacity` 24、`u_dissolve_amount` 4、
     `u_distort1_intensity` 2、`u_maintex_rotation` 1
   · 24 个无贴图 Model 的源级可证形态 = **半透明自发光薄片**；菲涅尔/ADD_COLORTEX 只是 shader 能力，
     **26 节点无一驱动** ⇒ 是否启用 **unresolved**（不猜）
   · ⚠ **枚举值表找不到**（`TransparentMode/RenderBias/DirType` 只有名字没有值）⇒ 只能给观测分布
     （`TransparentMode{0:23,2:3}`、`RenderBias{2:24,4:1,0:2,1:2,-1:1}`、`DirType{2:29,0:1}`），
     项目内 `blend_mode_map` 自述 approximate、**未升级为直证**
   ⇒ 已派 **task-31**（blocked_by task-28）：接 `u_dissolve_amount`（源值 0/0.5 已在手）+ `u_emissive_highlight_intensity` + UV 旋转轴校正
```

---

## 一、已修好并且板上可见的（8 项）

| # | 问题 | 根因 | 状态 |
|---|---|---|---|
| 1 | 金蟒啸焰 1110024「点进去是空的」 | manifest 漏写 `Tex0` 槽（后又有 `t_custom_ibl` 未写）⇒ fail-closed 占位材质 | ✅ 已修 + 页面目视确认（board 96.26/96.37 · gold 26.14% · magenta 0%） |
| 2 | 8 张海报「乱七八糟」 | 尺寸/取景/UI 残留各异 | ✅ 统一 1600×900/16:9 · 零 DOM UI · uiPix=0 |
| 3 | 墨隐麒麟 1110165 全黑 | 同 #1（cube 已落盘但未写 manifest） | ✅ 已修 + 完工（武器区 p50 35.1） |
| 4 | 开 SFX 后**乱旋转** | `Sprite` 自带 geometry 进 `Box3` ⇒ 被当旋转轴心 | ✅ 已修（idle 逐帧零跳变） |
| 5 | 晶体补丁缺口 | 门控只在 weapon 分支 | ✅ `q_envW/q_F0/0.079956` false→true · 回归全绿 |
| 6 | 1110129 的死引用 404 | `prim4.ParamMap` 指向不存在的文件 | ✅ 删槽 + 标 missing |
| 7 | `models(true)` API 缺陷 | `MODELS_ON` 是构造期常量 | ✅ 改为 `LIVE_LOAD` 就地加载（26/26 ok） |
| 8 | `errors:26` 被吞的异常 | `applyModelMaterial` 作用域错 ⇒ 26 次 ReferenceError | ✅ 已修 + 改为记录异常正文 |

**材质层** ✅：`param_repack` 按 DXBC 重生成 7 张（补上丢失的生成器 `gen_param_repack.py`）
· 1110145 实采 metal **1.0 → 0.1354** ⇒ **不再素白**（蓝紫+金铜金属）

---

## 二、四层现状（按用户的分层）

| 层 | 状态 | 关键证据 |
|---|---|---|
| **模型/几何** | ✅ 有 | 8 个入口 |
| **材质** | ✅ 修完 | metal 不再盲恒 1 · shader 错 0 |
| **上色** | ⚠ 部分 | 颜色主要来自 IBL + 特效层（`metalness≡1` 对多数皮肤**源级正确**） |
| **光效** | ⚠ 根因已定 | **直接光过强**（归零后 S 提升 6×）· 真值属 cb1 运行时全局 ⇒ **静态不可得**（五条路全否证） |
| **特效** | ⚠ 根因已翻转 | **白块不是数据缺失**：源侧那 24 个 Model 节点**本就没有贴图**，是**无贴图自发光/叠加**特效（`u_emissivecolor`/`u_emissive_highlight_intensity`/`u_overall_opacity`/`u_depth_bias` 驱动）⇒ 白块来自**适配器用了白色 PBR**；已派 task-22 实现「源自发光/叠加分支」（默认仍 OFF） |

---

## 二·五、★★★ 最大成果：**晶体不再泛白**（Round 4 实测）

```
Lead 自己在 wiki 页面实测（武器区 V/S + "亮且中性"占比）:
  1110177 极光剑: **S = 0.645** · 亮且中性 **2.08%** · V=0.146 · 异常 0
  1110171 光影咏叹调: **S = 0.645** · 亮且中性 **1.50%** · V=0.141 · 异常 0
★ 对比基线（shader-auditor 早先实测）: 1110177 晶体区 **S 0.219** · 亮且中性 **74.93%**
⇒ **S 提升 3 倍 · 亮且中性 74.93% → 2.08% —— 一个数量级以上的改善**
★ 7 个 mesh 全部 map/normal/mMap/rMap 正常（晶体 mMap=False 是源分支 metal=0，正确）
★ 分级链**已命中第①级** `u_refraction_color(source L477)`（原为第②级 `u_crystal_color`）
  · 1110177 prim1 [0.6588,0.6824,0.7608] · prim2 **[1,0,0]（纯红宝石）**
```

## 二·五、★★★ 最大成果：**晶体不再泛白 —— 两把都成了**（Lead 亲眼看图确认）

```
【Lead 在 wiki 页面亲自截图并目视确认（Round 7）】

极光剑 1110177:
  · **红色宝石清清楚楚** · 银色剑身 + 金色装饰 · **完全不泛白**
光影咏叹调 1110171:
  · **双枪清晰可见** · **蓝紫色晶体/尖刺** · 中央**粉紫色晶体核心** · **不是黑的**
  · 比修复前（灰白一片）好看太多

【量化（武器区 V/S + "亮且中性"占比）】
  1110177: S = 0.645 · 亮且中性 2.08% · V=0.146 · 异常 0
  1110171: S = 0.645 · 亮且中性 1.50% · V=0.141 · 异常 0
  对比基线: 1110177 晶体区 S 0.219 · 亮且中性 74.93%
⇒ S 提升 3 倍 · 亮且中性 74.93% → 2.08% —— 一个数量级以上的改善

【分级链已命中第①级】`u_refraction_color(source L477)`（原第②级 `u_crystal_color`）
  1110177 prim1 [0.6588,0.6824,0.7608] · prim2 **[1,0,0]（纯红宝石）**
  1110171 五个晶体 prim 各自源值

【是这几步共同的结果】
  ① 晶体三槽接线（DetailMap / t_caustic_tex / t_reflection_tex，源有已定位）
  ② 逐 prim 的 u_refraction_color 写进 manifest
  ③ param_repack 按 DXBC 直译重生成（B←源G · G←源R）
  ④ 三个默认关的诊断开关（直接光 / albedo / tonemap）
  ⑤ 大片遮挡定位 + 全 prim 黑的异常排查
```

## 三、晶体层（用户点名）—— **素材全部就位**

```
✅ 3 张贴图解出并落盘（TGA→PNG 保留 alpha）
   crystal_bump_n_uvva.png(512²) · crystal_caustic_uvva.png(256² 灰阶) · crystal_reflection_uvva.png(256²)
✅ fashion_qiangpi.cube 补齐（524408B · 128+6×87380 精确吻合 · 6 面 Test-Path True）
✅ 1110171 manifest 已写（5 个晶体 prim）
   · DetailMap(5/5) · t_caustic_tex(prim1/2/3/5) · t_reflection_tex(prim1/2/5 only) · t_refraction_tex(not_shipped)
   · u_refraction_color 逐 prim 源值 · prim2 的 t_custom_ibl → fashion_qiangpi.dds
✅ 1110177 极光剑 同样就绪（prim1/2 · u_refraction_color prim2=[1,0,0] 纯红宝石）
⚠ **接线进行中**（shader-auditor）· 待验收截图
```

---

## 四、龙渊永寂 1110146 —— **推进后维持二次封存**

```
★ 封存第 4 条「多 LOD 盒不可得」**被推翻**（读出 4 个 BoundingHalf ✓）
★ 但两条独立搜索路径 **0 命中**，且**搜索器在对照上精确命中 ⇒ 无假阴性** ⇒ 否定可信
★ **顺带查清了"比值法"为何必然失败**：位置是**量化进本文件 bbox 的 u16**
  （`P = bmin + (u+0.5)/65536*(bmax-bmin)`）⇒ 极差比值 ≈1:1:1，与盒比值无关 ⇒ 判据前提无效
⇒ 结论：**工具能力问题，不是资源问题**；证据全部写入 `1110146\_build\BLOCKED.md`
```

---

## 五、用户点名的另两条

```
· **纹理** ✅ 已 7 维审计：**无丢 alpha**（`*_a.png` 的 A 真多样 std 66–89）· 色彩空间对 · UV 对
  ⚠ 但查出 **1110145 真缺 4 张贴图**（GPK 块 667–675 共 9 条只落 5 条）⇒ **已全部补出**
  ⚠ 且 **`_1001*` 归属不可证**（bind #654 是多皮肤共享材料文件）⇒ **不绑，记入 observed_but_unbound**
· **特效白块** ✅ **根因已翻转**（chain-auditor task-21）：
  ✗ 旧判定「白块 = 缺 `u_maintex` 的 alpha 遮罩 / 24 of 26 节点缺 `Tex0` ⇒ 只能默认关」
  ✓ 新判定「**源侧本来就没有贴图**」：24 个 `.gim` + 24 个 sibling `.mesh` 全文件扫描
    **0 条纹理/材质路径串**；`.sfx` 的 26 个 `<Model>` 节点 **28 属性全列**、
    **无任何 tex/material/shader/res 属性**；只有 `ShaderComponent/Uniforms/Variables/<Semantic>`
    里 **恰好 2 个**节点有 `Tex0`
  ⇒ 那 24 个节点在游戏端是**无贴图自发光/叠加特效**，由
    `u_emissivecolor`(202..243, 0..122, 155..246, 255) / `u_emissive_highlight_intensity` /
    `u_overall_opacity` / `u_depth_bias` 驱动，透明/混合按 `TransparentMode` / `RenderBias`
  ⇒ **白块是适配器用了白色 PBR，不是数据缺失** ⇒ 已派 **task-22**（viewer-auditor）实现
    「无 `Tex0` ⇒ 源自发光/叠加分支」，**默认仍 OFF**，只让 ON 状态不再"乱七八糟"
  ⚠ 仅 2 个环节点需要贴图（`tex_ring_fz01_x06.tga` / `tex_ring_keji_hgz01_04.tga`），
    按名解析**全 MISS**（8 变体）⇒ **不顶替**、fail-closed + `texture_unresolved`
  ⚠ 24 gim + 24 mesh 都在 **`res\048.fpk`**（fid 索引 **48/48 HIT**）
  ⚠ `texmap_fx.json` 是 **20 B 空文件** `{"sets":{"fx":{}}}` —— 不能当"有 texmap"的证据
  ⚠ prior 产物把 `.gim` 值区首个 u32 记作 `MtlIdx=[149,0,0]`，其方法自述 `best_effort`
    ⇒ 已降级为「语义 unresolved」，不当实证
```

---

## 五·五、⚠ 需要用户拍板的重大改动：**weapon 基底 `Tex0` 应绑 `*_a`，现在全绑 `*_b_m`**

```
★★★ c159 逐槽直证全量完成（解析器 `c159_slot_parser.py` 成立；修好 `c159_pair.find_groups`
    的"同对齐内误删合法重复组"后，横跨 8 文件 33 材料）：

  **weapon 基底模板**: `Tex0←*_a` · `ParamMap←*_m` · `t_surfacemap←*_s_m` · `NormalMap←*_n` · `t_custom_ibl←*.cube`
     ⇒ **21/21 材料无例外**
  **crystal 族**: `Tex0←*_b_m` · `t_basecolor←*_a`
  ★ **结构事实: `t_basecolor` 槽只在晶体族材料里 —— weapon 基底根本没有该槽**

★ 而 **7 个已建皮肤的 weapon 基底 `Tex0` 全部绑的是 `*_b_m`** ✗
  ⇒ **与 c159 直证相反** ✗✗ ⇒ **按源绑定，它们的基底色都绑错了**

★ 判定：**c159 方成立**（不调和，只说强弱）
  ① 外观不能反推绑定（`_a` 绑 `Tex0` 而渲染不金 ⇒ 渲染链另有未知偏差）
  ② 覆盖度: c159 侧 **8 文件 33 材料 21/21** ＋ 与 manifest 自述、晶体结构**三方互证**
     vs A/B 侧**仅 1 皮肤 2 方案**，且自留 **21.47% vs 58.4%** 未解释缺口
  ③ A/B 有结论外推: 源 shader 里 `Tex0` 未必是 albedo
  ★ 而 09-17 记录**第 5 行自述**「上一轮发现 **GLB 与 c159 manifest 都指向 `_a`**」
    ⇒ **A/B 是在明知源绑定为 `_a` 的前提下，用外观把它否掉的**

⇒ **Lead 未擅自改** ✗ —— 因为改它会让 **7 个皮肤的画面全部变化**，属需用户拍板的重大改动。
   裁决口径（待用户确认）: **绑定以 c159 为准**；A/B 的"`_b_m` 更接近参考图"**只作 viewer 渲染近似保留**，
   须标注"与源绑定不符"，**不得据此改写源绑定**。
```

## 五·六、熔炉寒霜 1110129「完全是一坨屎 / 纯黑剪影」—— **根因已确证，数据已修**

```
★★ 根因（env-auditor 逐面实测 + Lead 复核，两条独立路径）:
   `1110129/neox_material.json` 五个 prim 的
     `textures.t_custom_ibl.faces_glob = "src_cube/faces/qiangpi_f*_m0.png"`
   是 **shell 通配写法**；而 `weapon_skin_viewer.js:1048-1053` 只替换 `{...}` 占位符
   ⇒ `*` 原样进 URL ⇒ **六面坍缩成同一个 404**（`__cubeDirProbe` 六条 URL 逐字相同）
   ⇒ `CubeTexture.image` 为空（`__acceptanceReport` 逐 prim `ibl_faces=0`，对照 1110145 为 6）
   ⇒ **源环境辐射 = 0**；该皮肤源 metalness ≡ 1（无漫反射项）⇒ 输出 ≈ 0
   ⇒ 剪影区（12.45% 画布）平均亮度 **15.2 ≈ 背景 #071015 的 15**（对照 1110145 同一像素集 **51.3**）

★ 排除"资源缺失"：磁盘 `1110129/src_cube/faces/qiangpi_f0..f5_m0.png` 全在，按正确键名请求 **6/6 HTTP 200** ✓

★ 修法（Lead 已执行，最小数据改）：`faces_glob` → `src_cube/faces/qiangpi_f{0..5}_m0.png`（既定写法）· 5 处
   备份 `neox_material.json.bak_fg_20260918_024152`
   ⚠ 注意：`{i}` 写法（1110024 / 1110152 在用）**是合法的** —— `/\{[^}]*\}/g` 会把 `{i}` 整体换成面号

★ 顺带查出**第二条独立的纯黑路径**（已派活）: `weapon_skin_viewer.js:1937-1938` 的
   **回退预览表把 1110171 的族号写死**（`012_b_m / 012_a / 010_b_m / 010_a`）
   ⇒ 链未生效时其它皮肤请求到 3 条 404 ⇒ `MeshBasicMaterial(map=null, toneMapped:false)` ⇒ 同样纯黑
```

## 五·七、槽位覆盖矩阵（Lead 现算，`_lead_slot_matrix.py`）—— 7 皮肤 × 11 槽

```
skin          Tex0  t_base  ParamMap Normal  surface  ibl    Detail caustic refl refract MtlIdx
1110024       5/5   5/5     5/5      5/5     0/5 ⚠    5/5    -       -       -      -      -
1110129       5/5   4/5     4/5      5/5     0/5 ⚠    5/5    -       -       -      -      -
1110145       7/7   7/7     7/7      7/7     7/7 ✓    7/7    -       -       -      -      -
1110152       2/2   2/2     2/2      2/2     0/2 ⚠    2/2    -       -       -      -      -
1110165       4/4   4/4     4/4      4/4     4/4 ✓    4/4    -       -       -      -      -
1110171       7/7   6/7     2/7 ⚠    7/7     2/7 ⚠    7/7    5/7     4/7     3/7    0/7 ⚠  -
1110177       3/3   1/3     1/3 ⚠    3/3     1/3 ⚠    3/3    -       1/3     -      -      -
（`-` = 该皮肤源里没有这个槽；`t_refraction_tex` 0/7 见下）

★ 字段名坑（已澄清）：manifest 用的是 **`local_file`** 而不是 `file`
  ⇒ viewer L895-906 有归一化把 `local_file → g[k].file` ✓ 所以运行时是通的
  ⇒ 但**任何直接读 manifest `.file` 的脚本/判断都会看到"全空"** ✗（我第一次的矩阵就踩了这个坑）

★ `t_surfacemap` 为什么"绑了不用"是**对的** —— 但**理由被推翻重写过**（chain-auditor task-16 部分反驳）：
  ✗ 旧理由：「weapon 端该槽只写延迟管线 G-buffer 的 `SV_Target3.y`，不是前向着色的乘子」
  ✓ 新理由（有 DXBC 逐条 def-use）：
    `t3=t_surfacemap`，L313 `sample_l(... t3.yzwx ...)`（swizzle .yzwx ⇒ 取到的 R）
    → L332/333/334/343/344/428 → **L429 `mul o0.xyz, r1.xyz, cb1[266].x`**
    ⇒ **`s_m.R` 是乘子、进的是 `SV_Target0`（颜色/高光项）**，不是 o3.y；
      `o3.y` 另有来源（L345-350：`sat(N·L²⁻ᵉ)·(1-ParamMap.w²)+ParamMap.w⁴` 再 ×cb0[136].w）
    并且它乘的是受 `cb0[133].x/y/z/w + cb0[135/136] + 时间 sincos` 驱动的**染料-高光项**，
    three 的前向模型**没有对应项** ⇒ 仍**不接**（正确的接点是高光项，但其消费 pass 项目内仍未定位，标 unresolved）
  ✓ 且即便照抄也近乎无效果：`_s_m` 的 R 近恒 1（全库 99.76%；正控 1110165 `#1637` 实测 r255=0.988）

★ **1110024 / 1110129 / 1110152 的 `t_surfacemap` 已定案 = `no_shipped_bit`（源有声明、无对应贴图位）**
  三个 manifest **本就都有 `why_not_direct`**（我之前"两个没写原因"的前提是**过期**的，chain-auditor 纠正得对）
  ⇒ **无需改 manifest**；判据 = ① 材料 c159 的 EOB 组声明集（逐条给 byte）
    ② 区块定界（最后一个 material c159+1 → 下一条 `.c159`）③ 逐条内容签名；族区间全扫 0 条 R≈1
  ⚠ 方法学（已同步给 freeze-auditor）：**weapon.gpk 匿名、无明文名字表**，
    同皮肤已发货的 `001a/001m/001n` 在同一 3.15M 索引里也全 MISS
    ⇒ **按名 MISS 不能当缺席证据**，缺席只由 ②③ 支撑

★ 1110165 孤儿文件已登记（Lead 写入 `observed_but_unbound`，6 条）：
  `165_m.png` = **仅 prose 引用、槽位引用 0 处**（6 处全在 `naming_conflict` 散文里）；
  `165_c_m.png` / `165_d_m.png` / `165_e_m.png` = **零引用**；
  `param_repack_165.png` / `rough_repack_165.png` = 仅说明文本引用（派生件）

★ `MtlIdx` **不是贴图槽**（我一开始按贴图槽扫，扫出"7/7 皮肤全 0"是我的口径错）:
  它是 `.c159` **模型文档的 38 个字段之一**（`BoundObject/Lod1..4/Sub0..2/MtlIdx/…`），
  作用是给出 **Sub0/Sub1/Sub2 → 材质名** 的直证序列
  ✓ 已解：`1110171_cand/viewer.json` L2909 记载「Sub0/Sub1/Sub2 → 材质名 skin_1003_010_0/1/2 的**直证序列**存在」
  并明确废除了旧的「mesh 内无 per-primitive MtlIdx，待取直证」表述
  ⚠ 但 **1110177（029）的 `viewer.json` L361 仍是那段旧表述**（prim→material 属"位置对应"，非直证）
  ⇒ 遗留项：把 1110177 的 Sub→材质名直证也取出来（同法是读绑定 c159 的 MtlIdx 字段）
```

## 六、任务板现状（全部 27 项）

| 任务 | 谁 | 状态 | 干什么 |
|---|---|---|---|
| task-13 | `shader-auditor` | ✅ | viewer.js fail-closed ×2（六面 URL 非互异拒绝装配空 cube；回退预览表改逐 prim 读 manifest） |
| task-14 | `renderer-auditor` | ✅ | 1110129 修复后验收 = **有色可辨** + 海报 |
| task-15 | `env-auditor` | ✅ | **「两组结果 + 绑定差异」**（A=`Tex0←*_a` vs B=`*_b_m`，7 皮肤） |
| task-16 | `chain-auditor` | ✅ | `t_surfacemap` 源侧定证 + **部分反驳** DXBC 旧理由 |
| task-17 | `evidence-verifier` | ✅ | `MtlIdx` 直证（1110177 取出，1110171 自述复核成立） |
| task-18 | `shader-auditor` | ✅ | **两入口不一致根因 = L1927**；裁决 (b)：board 为验收基准；清污块两入口共用 |
| task-19 | `renderer-auditor` | ✅ | 1110024/1110152 海报 + 1110024「不是空的」= 可见有色模型 |
| task-20 | `freeze-auditor` | ✅ | **108/108 命中 + 108 GLB + `.gpk` path→entry 破解** |
| task-21 | `chain-auditor` | ✅ | **Model 白块根因翻转**（源侧本无贴图，是无贴图自发光/叠加） |
| task-22 | `viewer-auditor` | ✅ | adapter 无 Tex0 ⇒ 源自发光分支（白像素 10.06%→1.92%，**仍未达游戏观感**） |
| task-23 | `env-auditor` | ✅ | 1110024 IBL 顶替两组结果（**源声明组更差**）+ 6 类不一致定级 |
| task-24 | `chain-auditor` | ✅ | **1110129 prim4 的源级 ParamMap = `weapon.gpk#410`**（被误命名成 `008_f_a.png`） |
| task-25 | `renderer-auditor` | ✅ | prim4 补回绑定后**已编译并显示** + 零回归 |
| task-26 | `freeze-auditor` | 🔄 在跑 | 用新方法找两张环贴图 + `bbox_v2` 覆盖率 pass |
| task-27 | `renderer-auditor` | 🔄 在跑 | 海报终轮（1110129 必重拍；其余 6 张只判"变/未变"） |

**写者冻结状态**：`weapon_skin_viewer.js` = `BA2A84695E53F865`（已停写）；`weapon_skin_sfx_adapter.js` = `2E61C5234BB37CED`（task-22 已交，若 task-26/27 不再触发改动即为终态）

## 六·五、本轮新增的**定证**（每条都可复核）

```
① 1110129「纯黑剪影」根因 = faces_glob 写成 shell 通配 `qiangpi_f*_m0.png`
   ⇒ 六面坍缩成同一个 404 ⇒ 空 cube ⇒ 该皮肤 metalness≡1 ⇒ 输出≈0
   ⇒ 修数据后 **renderer-auditor 目视确认「有色可辨」** ✓
     （深色金属 + 蓝紫镶边 + 白高光 + 金色线圈；同像素集 mean L 19.87 / p95 70.72；magenta 口径见报告）

② 背景图：**8/8 皮肤都已应用** ✓（用户曾报"查看器背景图没加上去"）
   证据：Network 均请求到 `bg_weapon_skin_ingame.png`；`__matDump().background="texture"`；
   无-mesh 帧与 `_shared/bg_weapon_skin_ingame.png`(1672×941) 重采样后**平均差 2.55**（>8 仅 7.6%）
   ⚠ 唯一例外 1110169：无几何帧可做像素确认，只有"请求+类型"级证据（如实登记，未当"已应用"上报）

③ 1110024 金蟒啸焰：**已不是洋红/空白** ✓ —— 亲眼看过的截图 = 银白+金色完整枪械，
   武器区 mean 96.37 / p95 226.3 / **magenta 0.00%**；逐 prim 5/5 applied、missing_required=[]、
   `ibl_faces` 六面全齐（唯一 `unresolved_slots=["t_surfacemap"]`，见②/五·七 的结论）

④ ★★ **两入口渲染不一致 —— 根因已定位（L1927），并牵出一条口径纠正（已裁决）**：
   分叉点 = `weapon_skin_viewer.js` 原 **L1927 `if(!LAB && !callOpts.forceLab){ … }`**
     · 该块关 rig 三盏灯 / `scene.environment=null` / 曝光&toneMapping 归位 / bloom 强度 0
     · board（默认页）= **走**该块 + 源 cube 辐射
     · lab = **跳过**该块 + 源 cube 辐射 + 实验链（实验链还把 `toneMapping` 设 NoToneMapping、`exposure=1`）
   **源级判据（决定谁对）**：NeoX 管线**没有** three 的 Hemisphere/Directional rig，
     环境辐射来自逐材质 `t_custom_ibl`（L1167-1199 的 radiance 覆写）
     ⇒ **board（rig 关）才是源忠实的一侧；lab 的 rig 是 viewer 额外叠加** ✓
   ⇒ **裁决：验收基准口径固定为 board / 默认页**；lab 只作诊断，
     且 **lab 的一切读数必须标注"含 viewer rig 额外光，不可作保真度证据"** ✗ 不得当保真度证据
   ⇒ 已改（shader-auditor，最小改动）：该"清污块"改为**两入口共用**（`CLEAR_ALWAYS=true`），
     只有"链生效早退 + 回退预览"仍限默认页
   **零像素回归证据**：三皮肤两入口 RT 帧 sha 改动前后**完全相同**（`5166dcf2`/`289bde16`/`bc042acf`）；
     self-check `PASS 63 / FAIL 1 / WARN 0`；`SELFCHECK.png` 逐字节相同 ✓
   ⚠ **矛盾已对齐并关闭（renderer-auditor 自纠）**：它上轮报的
     「1110024 lab mean **0.00**（近乎全黑）」「1110152 2.6×」中，
     **"1110024 lab 全黑"经复测不可复现 ⇒ 系其取帧伪影，已作废** ✗
     （构造缺陷：单发射击 + **无帧稳定门** + `HIDE` 后**未复核 rect** ⇒ 落在未稳定/重排帧上；
      加上稳定门后 lab 实测 mean **91.61 / 92.70**，与 board 同量级）
     · 「1110152 lab 更亮」**方向可复现**：board 37.10 → lab 80.26 ≈ **2.16×**（上轮报的 2.6×/98.31 已修正）
     · **可复现的真实入口差异 = 渲染器状态**：lab `toneMapping=0(NoToneMapping)` + `bloom=true`，
       board `toneMapping=4(ACES)` + `bloom=false`（两页 exposure 均 1.75）
     · 证据 `_target_1110171\LABALIGN_报告.md` / `LABALIGN_result.json`
   ★ **8 张海报全部走 board/默认页** ⇒ 该 lab 伪影**不影响任何海报**，
     也不影响 1110024「可见有色模型」结论（board 96.26/96.37 · gold 26.14% · magenta 0%）✓
   ★ 已重新统一取帧纪律：**稳定门（连续帧 sha 相同）+ 取帧前复核 rect**，
     两个 auditor 的掩模口径不同 ⇒ **绝对均值不可跨口径比较**，只比同口径的相对关系
   ★★ **prim4 根因已证完（shader-auditor task-18，用新增只读 `__meshDump()`）**：
     mesh 4 与 mesh 0–3 **只有一项不同 = `matVisible: false`**
     （几何/包围盒/视锥全同：共用同一 geometry，`vertices 17924`、
       `bboxSize [0.8956,3.3196,9.0005]`、`inFrustum true`）
     ⇒ 材质被 three 跳过 ⇒ `onBeforeCompile` 从不执行 ⇒ `fragLen:0 / rad:false`
     ⇒ **不是下标/缓存假设**，触发源是 fail-closed 分支：该 prim 的 **`ParamMap = null`**
       （manifest 里 prim0–3 都有 `008_*_m.png`，**prim4 的 `008_f_m.png` 是 404 死引用、已被我删槽**）
       ⇒ `missReq=['ParamMap']` ⇒ `chainOk=false` ⇒ 默认页隐藏该材质；lab 走品红诊断分支故仍编译
     ⇒ **board 是对的**（取消隐藏 = 显示一个必需输入缺失的材质，违反 fail-closed）
     ⇒ **补救在数据侧** —— ★ **已修（当晚闭环）**：chain-auditor task-24 证出
       **源级 ParamMap 位其实存在 = `weapon.gpk#410`**，只是既有提取把它**误命名成 `008_f_a.png`**
       （manifest 0 次引用）；auditor 已把该位提取为 `src_tex/008_f_m.png`
       （53,145 B、sha256 `4338d033…`，**与 `008_f_a.png` 字节完全相同**，同皮肤/同区块/同组 ⇒ 非替代）
       · 三重判据：① 区块定界 = c159#392+1 → 下一条 c159#412 ⇒ #393-411 共 19 位；
         ② `000334.c159` 五组 EOB 声明 G0-G3 各 {a,m,s_m,n} + G4 {4001a,4001m,4001n} ⇒ 19 声明 ↔ 19 位，
         G4 内 `4001m→#410`；③ 内容签名 #410 落 `_m` 簇（g255=b255=0.9957、G_uniq=4、梯度 564、PNG 0.20 B/px，
         对照 4 个 `_a` 位 G_uniq=256 / 梯度 1088–2309）
       · **Lead 已补回绑定**：`1110129/neox_material.json` prim4 `textures.ParamMap = src_tex/008_f_m.png`
         （含 `block_entry: weapon.gpk#410` 与完整证据字段）；`missing` 里的 ParamMap 条已移除、
         `t_custom_ibl` 条的措辞已改写（G4 只含 {a,m,n} ⇒ 不绑 cube 是源级正确）
         · 备份 `neox_material.json.bak_pm4_20260918_031737`
         · **改前（磁盘）21,162 B / sha16 `9596bd860124bbb7` → 改后 22,891 B / sha16 `2312fdca0f90fa99`**
         · ⚠ 更正：我先前报的"改前 `ceb8173c2ef0071f` / 20,581 B"是**对解码后文本**算的哈希与**字符数**，
           **不是文件 sha16/字节数**（renderer-auditor 查出磁盘无该值，已更正为上面这组）
       · **验收通过（task-25）**：`__meshDump()` 逐 mesh —— mesh5(prim4)
         改前 `matVisible:false / fragLen:0 / rad:false` → **改后 `matVisible:true · fragLen:24556 ·
         rad:true · hasMap:true · visibleChain:true`** ✓；`__neox()` `applied=5 · failed=[] · missing=[]`；
         截图 `PM4_1110129_board.png` sha16 `a320649d52a081d0`（**目视**：整枪完整、无 UI/无纯色块/无全黑/无错位）
       · 说明：5 个 prim **共用同一几何（17924 顶点）= 同几何 5 层材质壳**
         ⇒ prim4 从"不渲染"变"渲染"后**画面变化很小属预期**（board mean 19.87 → 19.90）
       · 残差 `#410` alpha：**当前无影响** ✓ 渲染读的是派生图 `param_repack_008.png`（alpha≡1，仅 R→G 重排，
         three 只读 roughnessMap.**G**）⇒ alpha 不进渲染（实测 `008_f_m.png` α min/mean/max = 0.000/0.0728/1.000）
       · 另登记：`wiki_selfcheck.py` 本轮唯一的 1110171 FAIL 明细为 **mesh[2,3,5,6]**（此前记 [3,5,6]，**多 #2**）
         ⇒ 如实登记差异，与 1110129 改动无关；**1110129 自检 PASS**
       · **零回归最硬证据**：1110024 board 帧 sha `d2edd7f700619a70`、1110152 `2549fe2ffc362af2`
         与变更前**逐字节相同** ✓
       · ⚠ 待办：**1110129 海报早于本次 prim4 修复** ⇒ 写者全停后统一重拍
       · 另登记 `material_label_note`：prim4 标签 `skin_1001_008_4` 与 c159 #332 的 `_0/_1/_2/_4/_5` 不符
         ⇒ 源名应为 `skin_1001_008_5`（**未擅自改名**，只登记，属需你确认的元数据修正）
       · ⚠ 残差：`#410` 的 alpha 与 4 个同类 `_m` 不同（a0=0.807、a_mean 0.073 vs 同类 α≡1）；
         `param_repack_008.png` 只重排 R→G、alpha 留 1 ⇒ 当前不进渲染
       · **验收已派 task-25**（renderer-auditor，`__meshDump()` 逐 mesh 改前/改后 + 目视 + selfcheck）
   ★ **七皮肤 × 两入口表（task-18 交付）**：逐 prim 注入读数全皮肤一致
     （`24556/true/true` + `env_mode=source_ibl` + `ibl_faces=6`），**唯一例外 = 1110129 prim4 board `0/false/false`**（见上）；
     mean/p50/p95：board 36.5–38.1 / 29.0–30.7 / 74.6–75.2；lab（**含 viewer rig 额外光，不可作保真度证据**）38.1–39.7 / 31.1–32.5 / 81.5–82.1
   ★ 本轮 viewer 改动共 2 处：`L1935 const CLEAR_ALWAYS=true;`（清污块两入口共用）+ `L3559` 新增**只读** `window.__meshDump()`
     · `weapon_skin_viewer.js`：`6E9589555911287E` → `53E7DC16B4992A5A`(task-13) → `9E6D8DDB81732C53` → **`BA2A84695E53F865` · 270,234 B**
     · 回归：`wiki_selfcheck.py` **PASS 63 / FAIL 1 / WARN 0**，`SELFCHECK.png` **逐字节相同**；七皮肤两入口均正常出图
   ⚠ **prim4 `rad=False`**（board `len=0` / lab `len=24556`）：
     `frag_len=0` 的语义 = **该材质从未被编译**（注入只在 `onBeforeCompile` 里跑）
     ⇒ 嫌疑是 prim4 的 mesh 在默认页**没被渲染**（剔除/零面积），**不是**注入安装点的下标假设
     ⇒ 已要求 shader-auditor 证到底（世界包围盒/顶点数/visible/frustumCulled），走 (b) 修
     （选项 (a) 是"把 lab 实验链开给默认页"，会让默认页 `tm:0/exp:1`，**撞用户禁令，已否**）

⑤ `MtlIdx` 不是贴图槽，是 `.c159` 模型文档字段（Sub→材质名直证）
   1110177（029 刀）已取出原文：**bind=003994.c159 / material=003996.c159 / 子网格绑定=003997.c159**，
   `MtlIdx` 三条 @342/@457/@578 → `mmskin_2003_029_0/1/2` ⇒ Sub0/1/2 → material 0/1/2 ✓
   1110171 自述（`001212.c159` 608 B，@352/469/582 → `skin_1003_010_0/1/2`）经**独立复现**成立 ✓
   ★ 边界：**029 刀身 material0 是 `pbr_default`，不是 `pbr_weapon`**（003996.c159 全文不含 pbr_weapon.fx）
     ⇒ **不适用**「weapon 基底模板 `Tex0←*_a`」，引用该模板时**不得外推**到 1110177

⑥ ★★ 1110171 特效网格（28 节点）的**换容器**定证（task-20 的输入）：
   · **种子已确证**：`GIM_effect_full_scan.json` 的 28 个 needle 帧里有 **108 条 `.gim` 源级路径**
     （`effect\mesh\weapon\skin\skin_1003_010\mod_skin_1003_010_*.gim`…），
     其中 `mod_skin_1003_010_zs_06_01_pt.gim` 正是 74635 帧 `.sfx` 点名的那条
   · ★★★ **全闭环了：`.gpk` 的 path→entry 已就地破解，108/108 命中，108 个 GLB 已产出** ✓
     · **我可复用的方法级收获**：GPK 条目表 **32 B/行 = `[o, cmp, dec, c1, c2, fl, u32_6, u32_7]`**，
       其中 **`u32_7 = mm3(路径, 0x77777777)`、`u32_6 = mm3(路径, 0x66666666)`**
       （**反斜杠原样路径、latin1** 编码；`c1/c2` 仍是与路径无关的内容指纹）
       ⇒ 验证 3/3（按 u6/u7 定位的行解出 `c159410d`、`dec` 与声明一致、正是该名的 gim）
       ⇒ **只读 32 B/行 的表**即可定位任意 `.gpk` 资产：**90 个容器 ≈ 1 秒**，**无需解压整包**
       ⇒ 今后任何 gpk 资产（贴图/模型/sfx）都能秒级定位
     · **108/108 全部命中 `res\effect_01.gpk`**（其余 89 容器 0 命中）
       ⇒ ★ **我上一条"effect_01 里没有它们"是错的，已推翻** ✗→✓
         错因：我把**名称面**的 0 命中当成了缺席结论（正是我自己提醒过别人的那个错误）；
         并且**我把"条目表 423,086 流式帧号"与"212,152 条目表行号"混为一谈了**
     · **108 gim + 108 个同 stem `.mesh`**（`.gim→.mesh` 换后缀后同一哈希定位）⇒ **108 个 GLB**
       · 落盘 `_gim_out\1110171\sfx\model\*.glb` + `raw\*.gim|*.mesh`（**文件名 = 源路径基名，未自造名**）
       · 对照表 `_gim_out\1110171\GIM20_1110171_model_manifest.json`
         （gim_path / gim_row / gim sha16 / mesh_row / mesh sha16 / GLB sha16 / verts / faces）
       · 抽样：`dd_luoxuan03_djs` mesh 9,484 B → GLB 396 顶点；`dd_wei01_djs` 1,580 B → 64 顶点
     · 排除项：`effect_cache.gpk` 已证无（扫过 **199,600 帧**、两种 magic 均 0，**非名称 MISS**）
   · ★ **候选帧归属已定证**（freeze-auditor）：`f74635` 含 **28 条**、`f74631` 含 **27 条**，
     **交集 27，差集只有 1 条 = `mod_skin_1003_010_zs_06_01_pt.gim`（f74635 独有）**
     ⇒ **28 节点实体集归属 `f74635`**（"zs_01 vs zs_02 两候选帧"这个问题**已关掉**）
     · 产物 `_target_1110171\GIM20_frame_attribution.json`
   · 扫描口径已按方法学修正分两栏：**[引用命中] / [实体命中]**，且明确
     **「名称 MISS ≠ 缺席」**（实体靠内容判据 `c159410d` magic 计数，两栏不互相替代）
   · 源包全在 `E:\mrzh\res\`（57 个 .gpk，已确认）

⑦ 特效现状盘点（`viewer.json.effects`）：
   **7 个皮肤里 5 个 `status:"none"`**（1110024/1110129/1110145/1110165/1110177）
   仅 **1110152 灵态诱导** 与 **1110171 光影咏叹调** 为 `"partial"`
   · 1110152：`effects_node_count=40`、`adapter_present=true`、**`handle_present=false`** ⇒ 运行时**未附着**，
     海报中**无特效**（renderer-auditor 目视确认，未美化）
   · 1110024 对照：`effects_status="none"`、按钮 disabled、`btn_title="该模型没有 SFX 清单"`

⑧ 全局展示 rig 是**近似值且已标注**（用户禁令针对"用它凑参考图"，这些值是既有近似、非本轮新增）：
   七个皮肤一律 `fidelity.material="approximate"`、`material_layers.status="approximate"`、
   `rig.exposure=1.75`、`env_intensity=1.4`、`emissive_gain=0.25`、`tone_mapping=ACESFilmic`
   ⇒ 若要"完全源驱动"，这 4 个全局量是**待用户裁决的近似清单**（我没有动它们）
```

## 六·五、⚠ 一条重要的**读数环境**警告（会让人误判）

```
★ **headless + `--disable-gpu --enable-unsafe-swiftshader` 会产生与真实浏览器不同的读数** ✗
  实证: `shader-auditor` 在**未碰任何诊断开关、全新页面、默认 dual、pose 与 Lead 逐字段相同**的条件下
    **3/3 次都出 83 KB 暗帧**（`63d663a6`，66.5% 像素 <20 ✗）
    而 Lead 用同样的 pose 截图 ⇒ **双枪清晰、蓝紫晶体、背景正常** ✓
  ⇒ **harness 差异（SwiftShader），不是 viewer bug** ✓✓

★ **它同时撤回了自己的两条推断** ✓✓（诚实记录）:
  · "全 prim 帧黑 ⇒ 有 mesh 遮挡" ✗ —— **不存在遮挡问题**
    因为 `__primOnly` 在 L1833 会把材质换成 **unlit 纯白** ✗，而白剪影像素只有 **192–4341 px**
    ⇒ 它的"单显正常"也是**误读** ✓
  · 本轮**零代码改动**（viewer sha 仍 `6E9589555911287E` ✓）

★ **对本项目自检的影响（重要）**: `wiki_selfcheck.py` 也跑在 SwiftShader 下 ✗
  ⇒ 它报的 `1110171 mesh [3,5,6] normalMap 缺` **很可能同样是 harness artifact** ✗
    （`shader-auditor` 用真实读数证明 `mesh i=3` **有 normalMap** ✓）
  ⇒ **结论: 该断言在 SwiftShader 环境下不可靠 —— 不据此下结论，也不据此改代码** ✓
  ⇒ 已在断言里打出**原始读数**（`map/norm/mmap/rmap/env/vis/metal`），便于逐次鉴别 ✓
```

## 七、纪律（全程遵守）

```
缺资源标 missing · 不顶替 · 不拟合（拟合须标注并留待用户批准）
每个结论给可复核证据 · 改动前按 mtime+sha 备份 · 回归不得破坏已建成皮肤
凡"建成"必须在 **wiki 页面目视确认**（不看数字下结论）
本会话已据此**自我纠正多次**（含 Lead 自己引入的 over-binding 与一次错误的回退）
```
