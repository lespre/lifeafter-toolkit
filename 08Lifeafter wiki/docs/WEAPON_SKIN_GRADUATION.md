# 武器皮肤 · 毕业报告

生成：2026-09-13T10:10:29+08:00　｜　状态：**WEAPON_SKIN_GRADUATED = true**

## 唯一入口
- 板：`data/boards/weapon_skin_sfx_text_sources.json` → `board.html?b=weapon_skin_sfx_text_sources`
- 基准：**当前包 `508bb5bd`（2026-09-13 10:02 热更）**，FID 直读（entry 序号不承载语义）
- 覆盖：**131 行** = 113 主卡 + 18 时限变体（嵌父卡）+ 2 行为资源预告

## 名称
- verified 113 ｜ candidate 5（变体级）｜ unresolved 2（1110185/1110186：无主行无道具行 ⇒ **正式名静态不可得**，非缺工）
- 禁止从父静默拼名

## 表现 / 分级 / 变体 / 商务
- 表现：单一「特效与战斗表现」业务区，固定顺序，多源折叠（sfx_function 当前 **352** 行）
- 分级：level 2–6 单轴（白送/直售/紫皮 user_defined、典藏/传世 official）
- 变体：18 条时限；规则 = 8 位块 + `//10` 归父；末位不承载判断
- 商务三链独立：Listing `bounded_unresolved`｜Sale `verified_sale_config_present`(18)｜Acquisition `graduated_with_bounded_unresolved`

## canonical 结构视图
- `artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl`（126，基准 BA8A pre-09-10）→ **superseded_for_display**
- 投影 `weapon_skin_active` = internal（`published_hidden`，不进首页、直链可开）

## 残差（全部显式）
- A_sound: sfx_function 的 jump 目标集与 sound 表行键无交集（该表命名空间不同）
- B_animation: 行内无可取文本（引用池未闭环）⇒ 动画子类型维持 unresolved
- C_map_detail: 元素数分布与父表 ref 数不一致 ⇒ 语义未定，正式 residual 保留
- D_store_price: 价格字段多为空；jump 目标未能在本基准已定位表内闭环 ⇒ 维持 bounded_unresolved
- E_exchange: 元素命名空间仍未识别（多数值不在道具键域）
- F_gift: 礼盒表内无皮肤域整数（仅经 jump 组间接引用，目标非皮肤身份）
- G_lottery: 抽奖表未出现皮肤域直接引用 ⇒ replacement 路径维持 unresolved（需 runtime/服务端）
- H_timed_grant: 时限 id 与永久 id 在静态销售配置中未区分授予路径 ⇒ 维持 unresolved（服务端下发）
- I_sale_ts_semantics: 同快照未发现 sale_ts 的 consumer/独立 source ⇒ 维持 likely（release/first-publish 假设），不升级
- J_deferred_relations_new_sources: 三张关系表现已在客户端存在且可定位（旧基准未收）；payload=引用图格式，本轮未解出语义 ⇒ 从「无源」升级为「有源待解析」
- 永久断点：listing / sale_ts / server_branch

## 验收
板可一键重建 ✓｜583 项测试全绿（1 expected failure）✓｜**board truth dependency = 0** ✓｜残差显式 ✓｜源锁已登记 ✓

## 快照事件
- 2026-09-10 22:04：`328b8446…`（canonical artifacts 仍挂 BA8A）
- **2026-09-13 10:02：`508bb5bd…`（本次重建基准；weapon_skin_data 仍 131 行）**

## 展示图来源（永久断点，2026-09-13 实测定论）

**客户端不存在"武器皮肤展示图"这一静态资源。** 实测四条证据链：

| 探源 | 手段 | 结果 |
|---|---|---|
| 脚本包表引用 | 全包扫描 27,519 entry，抓 UI 声明路径 | 261 条 `.gim` 模型 + 109 条 UI 壳 PNG；**无皮肤展示图** |
| `ui.wpk`（ui idx, pkg4） | `03_WPK_1DPW/batch_wpk_textures.py --png` | 287 张 UI 贴图（标签/图标/图鉴格子壳），0 失败；非皮肤本体 |
| `weapon.wpk` | 同上 | 91 张材质贴图（1024/512 规格），非展示图 |
| `res.gpk`（31MB / 9,699 zstd frame） | 具名路径宽扫（`tools/scan_packs_for_skin_assets.py`） | 30 条皮肤路径，**全部 `.gim`，0 张 PNG**；关键词 `mvp`×22、`_nan`/`_nv` 各 11 |

关键证据：每个皮肤配的是 **`skin_XXXX_YYY_mvp_nan.gim` / `_mvp_nv.gim`（男/女两版 MVP 展示模型）**
⇒ 图鉴里那张图是客户端**实时渲染模型**，不是静态图。

**结论**：Wiki 的皮肤展示图唯一可靠来源 = **实机截图**（官方渲染，不受资源限制）。
归档工具：`tools/attach_skin_shots.py`（按文件名里的皮肤 ID 或皮肤名匹配 → 归位 `03拆包产物/skin_shots/已归档/`
→ 出 `data/exports/skin_shot_manifest.json`）。投放目录说明见 `03拆包产物/skin_shots/README.md`。

**未走的路（记录成本，非遗漏）**：自己解析 `.gim` + 渲染管线（成本高、收益等同截图）；全扫 gres 大包
（每个 2GB，扫描速度 ≈1.3 秒/MB ⇒ 全量十几小时，ROI 为零）。
