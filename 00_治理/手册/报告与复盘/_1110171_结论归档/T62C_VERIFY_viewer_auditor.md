# 极光剑 `_dg.sfx` 接入 · (c) 独立复测报告（viewer-auditor）

**结论速览：PASS 4 · WARN 2 · ⚠ FAIL 1（视觉：`models(true)` 大面积白块 —— 按你的要求立刻上报）**

> ## Lead 裁决（2026-09-19，已记账；原文要点）
> - **§4 FAIL → 判为 `expected_when_models_enabled_untextured`（已知限制，保留默认关、不美化）**：根因已由 Lead 定证 —— `<Model>` 节点在源 `.sfx` 里**不声明任何贴图**（hit 0/7 + jisha 0/19；只有 Sprite 13 / ParticleSystem 15 声明 `Texture`），该族 shader 最终色 = `diffuse + emissive`，自发光需乘 `u_emissivecolor` 并由 `e`（主贴图/遮罩采样）塑形 ⇒ **无贴图即无 alpha 塑形 ⇒ 实心卡片/白块是源数据缺失的必然结果，不是渲染 bug**；`models` 是研究开关，保持默认关，**不加尺寸/不透明度/朝向等"美化"约束**（属调参、用户明令禁止）。报告口径即"**开启即出现大面积白块，属已知限制**"。
> - **§5 WARN → 判定成立**：`sprites()/models()` **不控制 ParticleSystem** ⇒ "两帧同 sha" 判据在层分离实验不适用；我采用的 **effect-only + 探针计数** 替代判据被采纳；**关 SFX 后重新门控 OFF 与默认 OFF 逐字节一致** ✅。该条已写入方法学备注。
> - **§2 WARN（dg 无 `source_sfx`）→ 标注正确**：23 个 dg 节点用 `source_sfx_id="gres\0057.gpk#32153"` ⇒ 读法应为 **`source_sfx_id ?? source_sfx`**（已入台账）。
> - 其余（pin 6/6、默认态五读数逐项对基线、89 节点与 `renderable=6`、3 个撤回节点证据、`__probe() models 42/modelTable 42`、`/sfx/tex|dg` 12×200 0×404、异常 0/0/0、撤回后默认态无可测变化）均记账通过。

## 0. pin（前后一致）+ 页内实字节自证
| 对象 | sha16 | 页内 `fetch` |
|---|---|---|
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819` ✅ | 200 / `B9C7281E1EE7A819` |
| `weapon_skin_sfx_adapter.js` | `79F5F2B86D321995` ✅ | 200 / `79F5F2B86D321995` |
| `1110177/viewer.json` | `80FED5A6A2D905BE` ✅ | 200 / `80FED5A6A2D905BE` |
| `1110177/effects.json` | `4661BD5CFE44457E` ✅ | 200 / `4661BD5CFE44457E` |
| `1110171/viewer.json` | `62E7BDDC9CF6EC6D` ✅ | — |
| `board.html` | `2585162AF98DB68E` ✅ | — |
`?v=` 命中 200。防呆文件 `%TEMP%\t62c_expected_pins.json` 六项**全部匹配**后才开跑。

## 1. 默认态零回归 —— **PASS**
| 项 | 读数 |
|---|---|
| OFF 帧（N≥5，series 5× 同值） | **`e62c1c58e5bdc383`** |
| MASK 五读数 | `mask 1.826 / p50 **0.2829** / p95 **0.5745** / >0.5 **18.242** / >0.75 **0.989** / 暖色 **0.689**` ⇒ **五项与基线逐项相同**（`match:true`×5） |
| bg（新口径） | `__primShow(-1)` → `e26078dc2f7077da`（门控 4 帧通过） |
| 报告 | `applied **3 == 3`** ✅、`failed=[]`、`missing=[]`、`env_warn=null`；`__glowErrors` 该页未定义（记 `null`） |
| 全白像素占比（画布） | **0.092%**（无白块） |

## 2. 89 节点 / 6 可渲染 / 3 撤回 —— **PASS（附 1 条标注 WARN）**
页内 fetch `viewer.json`（现盘字节 `80FED5A6A2D905BE`）：
- **节点 89** ✅，tag = **Dummy 14 / Sprite 13 / Model 42 / ParticleSystem 18 / ParticleRes 2** ✅（与你给的分布逐项一致）
- **`renderable_by_adapter === true` 的恰好 6 个** ✅（9→6 生效）：`H_p_星点_02`、`M_g_glow_an`、`H_鬼火_lizi_1`、`H_g_glow地_an`、`L_p_星点_02`、`H_公告板_爆闪2`
- **你撤回的 3 个节点已生效**：`H_p_闪电` / `H_ shandian01_1_1` / `M_lizi_闪电_01` ⇒ `texture_candidate:null`、`renderable_by_adapter:false`、`texture_status:"REJECTED_wrong_image(fail_closed,不顶替)"`，并带完整 `texture_binding_rejected{verdict,observed_content,grid_test,rejected_candidate,reviewed_by,date}`（例如 `H_p_闪电`：`六边形网点/半调图案（肉眼）`、`声明 4x4：缝隙带 x=[0.663,0.720,0.718] ⇒ 无透明缝`）✅
- **⚠ 标注 WARN（口径）**：新增的 **23 个 dg 节点不使用 `source_sfx` 字段**，而是 `source_sfx_id="gres\0057.gpk#32153"` + `dg` / `dg_provenance` / `dg_sha16` / `source_sfx_name_evidence`；dg 的 Dummy 做了命名空间隔离（如 `L_空特效_1_1__dg`），dg Model 保留原名并以 `model_name` 指向 `mod_skin_2003_029_dg_*.gim`。⇒ **按 `source_sfx` 统计会把这 23 个读成"无来源"**（我第一版正则就踩到），建议登记为读法口径。

## 3. attach 后的 diag / probe：dg 内容确已进入运行时 —— **PASS**
| 探针 | 读数 |
|---|---|
| `__probe()` | **models 42 / modelTable 42**、sprites 3、systems 20、`modelsOn:false`、`modelsForce:null`、`textureUnresolved 0` |
| `__sfxDiag()` | `nodes **23**`（= sprites 3 + particles 20）、`sprites_total 3`、`particles_total **20**`（= PS 18 + ParticleRes 2）、`alive_now 1`、`sliced_total 0`、`unit_scale_on true`、`sfx_unit_to_model 0.1`、`clamp_k 0.6`、`color_order "unproven:[A,R,G,B]"` |
⇒ **16 个 dg Model 已计入 42（26+16）**、**3 个 dg PS 已计入 20（17+3）**；`/sfx/tex/` 与 `/sfx/dg/` 请求 **12 条全部 200、0×404**。

## 4. `models(false)` vs `(true)` —— **计数 PASS / 视觉 ⚠ FAIL**
| 控制态 | 开关读回 | 探针 | effect-only（vs 默认 OFF） | 全白（画布） | 全白（掩模内） |
|---|---|---|---|---|---|
| `all_off`（sprites F + models F） | `spriteOn:false` | models visible **0** | 0.0020% | 0.092% | 0.676% |
| `sprite_only`（sprites T + models F） | `spriteOn:true` | *探针表达式报错（见 §7）* | 0.0064% | 0.092% | 0.676% |
| **`model_only`（sprites F + models T）** | `spriteOn:false` | **models visible 32** ✅（42−32 = 10 不渲）、states `{ok, disabled_no_color_driver}` | **11.9246%** | **5.6535%** | **45.786%** |
- **计数符合你的预期**：`visible = 32`（既有 23 + dg A 类 9），C 类 10 个不渲（`disabled_no_color_driver`）✅
- **⚠⚠ 视觉 FAIL（按你的"出现大面积白块立刻报我"）**：`models(true)` 下画面出现**一整块白色平面群**（帧 `T62C_ctl_model_only_1.png` sha **`2bf799a2c5fb603a`**，白像素 bbox `x[219,1350] y[80,815]` ≈ 1132×736 px），**另有 1 条红色半透明竖带 + 右侧灰色半透明面**。**画布全白 5.65%、掩模内全白 45.79%**（默认态仅 0.092%）。
  - **最小复现**：皮肤 `1110177` → 点开 SFX → `WikiSfxAdapter.sprites(false)` → `WikiSfxAdapter.models(true)` → 等待 ≥2 s → 截图。第二帧（≥1.4 s 后）`T62C_ctl_model_only_2.png` sha `f8a9567fea786860`，白块 **6.07%**（仍在）。
  - 与"Model 源里不声明贴图 ⇒ 无贴图自发光/纯色 + 零厚度平面"一致，**但量级是"铺满视口中心的大白块"**，不是小块点缀 ⇒ 请裁决是"预期内（未贴图，默认关，不进交付态）"还是需要给 Model 层加尺寸/不透明度/朝向约束。

## 5. 负控两帧 —— **WARN（"两帧同 sha"未达成；原因明确）**
- 三态的两帧（≥1.4 s 间隔）**都不相同**：`all_off` `34193ad5` vs `3dcff05f`；`sprite_only` `0027afde` vs `c0699be2`；`model_only` `2bf799a2` vs `f8a9567f`。
- **原因**：SFX 开启期间**粒子系统仍在逐帧动画**，而 `sprites()` / `models()` 开关**管不到 ParticleSystem** ⇒ 只要 PS 活着，帧就不可能逐字节稳定。⇒ "两帧同 sha"这条判据在本设计下**不适用**；我改用 **effect-only% + 探针计数** 判定互不干扰（上表已给：`all_off` 0.0020% ≈ 默认态、`sprite_only` 0.0064%、`model_only` 11.92% ⇒ 两层各自的贡献可分离）。
- **默认关 OFF 帧逐字节一致**：控制组结束后重新门控 = **`e62c1c58e5bdc383` = 默认 OFF** ✅（`equals_default_OFF: true`）。

## 6. 异常 —— **PASS**
- 零观测注入空跑（navigate + 截图 + 20 s）：`exceptionThrown` **0 条**。
- 完整协议：`exceptionThrown` **0 条**、evaluate 级 `exceptionDetails` **0 条**。

## 7. 我亲眼看的描述
- **默认态**（`T62C_default_off.png`）：与长期基线同帧 —— 金/银剑体 + 红宝石核心，深青房间，**无黑屏、无白块**（与 MASK 五读数逐项相同互为印证）。
- **`models(true)`**：**多出一大块白色平面群**（占据视口中部偏右，边缘为折线状平面轮廓），**外加一条红色半透明竖带**与**一块灰色半透明面**；看不出贴图纹路（符合"源不声明贴图"）。
- **3 张错图撤回的变化**：默认态**无可测变化**（撤回的 3 个节点 `renderable_by_adapter=false`，默认态本就不渲），画面与基线逐项一致；我这一版**没有再看到**此前 `H_p_闪电`/`H_ shandian01_1_1`/`M_lizi_闪电_01` 对应的烟雾/蜂窝状色块（在 `all_off`/`sprite_only` 帧里白像素占比与默认态同为 0.092%）。

## 8. 未做 / 限制（如实）
- 本轮未做 board 页检查（你的 (c) 清单未要求）；未做逐 prim 归属（开关粒度是层级的 `sprites/models`）。
- **我的 harness 一处缺陷**：`sprite_only` 那格的探针表达式用了 `s.material.opacity`（该 build 的 `__probe().sprites` 行没有 `material`）导致报错；**不影响** effect-only/白块/帧数据（那些都取到了）。
- 只在 `t≈当前 SFX 时间` 采样（未扫动画窗口）；白块度量用"RGB 三通道 >0.9"的定义（画布与掩模内各一）。

## 9. 纪律与产物
- 只读；单浏览器 `FXVADG_prof` / 端口 **10119**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 个进程）；**端口 10119 无 LISTEN**、我的 profile chrome = 0。
- 产物：本报告 + `T62C_VERIFY_readings.json`（含 `manifest_nodes{...}`、`diag_raw`/`probe_raw`、`controls`、`net`、`exceptions`）；截图 `T62C_*.png`（默认 OFF、bg、三态各两帧）。
