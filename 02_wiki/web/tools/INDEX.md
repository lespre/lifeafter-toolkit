# tools 索引（自动生成）

共 558 个脚本；日常入口统一走 `python E:/la拆包项目/la.py`。

| 脚本 | 说明 |
|---|---|
| `__init__.py` | Workbench 工具包（可 python -m tools.<tool> 调用）。 |
| `_cmp_decoder_20260921.py` | 找 pool/xbody 的提供者 |
| `_fw_selfcheck.py` | 时装板自检：无头 Chrome(CDP 9333) 打开 board.html?b=fashion_wardrobe → 抓数 → 截图。 |
| `_probe_huodong2_20260921.py` |  |
| `_probe_huodong3_20260921.py` |  |
| `_probe_huodong4_20260921.py` |  |
| `_probe_huodong_20260921.py` |  |
| `_probe_ice_drone_20260921.py` |  |
| `_probe_nucleus2_20260921.py` | 660000 段核芯 + 名称含"核芯" |
| `_probe_nucleus3_20260921.py` |  |
| `_probe_nucleus_20260921.py` |  |
| `_src.py` | 还原树取值优先级：新 PE 树 → 旧 PE 树 → PC 树。 |
| `add_chip_anchors.py` | 把用户实机确认的限定芯片锚点写进奖池板（幂等，可重复跑）。 |
| `add_edible_craftable.py` | 料理板：加「是否可制作」（是否出现在食谱 output_item）+ 板级筛选配置。 |
| `add_fashion_part_cards.py` | 给「板上只有同套其他部位、缺本部位独立卡」的登记行补卡（如 不湮之花-头饰）。 |
| `add_named_only_toggle.py` | 时装板：默认只显示有图；新增「仅玩家可见名」勾选项。 |
| `add_perf_icons.py` | 战斗表现行加游戏面板同款小图标（18px，左对齐）。 |
| `add_perf_internal_names.py` | 武器皮肤「特效与战斗表现」补内部名：每行显示 中文真名 + 内部资源名（.sfx 基名）。 |
| `add_scene_pvp_filter.py` | 场景平衡：按场景名回挂 scene_id 列表 + PvP/PvE 分类（space_data.map_tag==4）。 |
| `add_scene_table_mode.py` | 场景平衡板：右侧改表格视图（含按服型/来源筛选、点表头排序）。 |
| `add_updates_20261026.py` | 站点更新通知：补本轮改动（场景平衡表格化 / 外观合并 / 种族修订 / MVP 修复 / 树归一）。 |
| `add_weapon_skin_status_v02.py` | 武器皮肤 canonical 状态字段 v0.2（listing_status / name_status）。 |
| `aggregate_skin_audio.py` | 把提取到的音频 bank 样本按**武器皮肤**归类，产出 Wiki 用的音频清单。 |
| `align_board_categories.py` | 把每个 board 的 meta.category 对齐到它在导航里的真实路径。 |
| `align_board_meta.py` | 把每个板块的 meta.category 对齐到 taxonomy（序号/名称唯一口径）。 |
| `analyze_client_file_map.py` | 客户端文件地图分析器：分类统计 / 差异对比 / 候选清单 / Markdown 报告。 |
| `annotate_new_skin_audio.py` | 给刚补的两张典藏/传世卡补证据标注，并把音频说明落到 attachments。 |
| `announce_calibrate.py` | announce_calibrate.py —— 官方更新公告校准源抓取（mrzh.163.com） |
| `apply_bag_bud_rule.py` | 按几何跨度给背包打「隐藏半感染者花苞」标记。 |
| `apply_brand_assets.py` | 把三张品牌图落进 wiki.html： |
| `apply_build_meta.py` | 横幅构建信息自动注入 + 页脚统计。 |
| `apply_namecard_frames.py` | 把已渲染好的 assets/avatar_frames/<id>.png 回写进 avatar_catalog.json。 |
| `apply_official_theme.py` | 把 wiki 主页换成官网《明日之后》视觉：冷蓝钢灰底 + 血红主按钮 + 金棕高亮。 |
| `apply_provenance_fix.py` | 把 provenance.table 修到真实表（已抽验 20/20 命中），并标注合成 row_key。 |
| `apply_weapon_skin_hotfix_overlay.py` | 把「PC 测试服热更覆盖记录」合并进武器皮肤图鉴板（data/boards/weapon_skin_sfx_text_sources.json）。 |
| `apply_wiki_theme.py` | 给 wiki 主页换上《明日之后》主题皮肤：暗色金属 + 锈橙警示色。 |
| `apply_wiki_theme_v2.py` | 主题 v2：卡片加宽 + 装甲细节 + 顶部档案标识。追加在 style 末尾，覆盖 v1。 |
| `apply_wiki_theme_v3.py` | 主题 v3：顶部军械库剪影 + 修掉一级项的小圆点 + 卡片排版微调。 |
| `apply_wiki_theme_v4.py` | 主题 v4：去掉重复箭头、把军械库剪影挪到顶栏下方并提亮。 |
| `attach_skin_posters.py` | 把 assets/skin_posters/<skin_id>.png 挂到武器皮肤媒体库里（用户提供的官方/实机图）。 |
| `attach_skin_shots.py` | 把**实机截图**按皮肤 ID 归档，并生成 Wiki 用的图片清单。 |
| `audit_boards_full.py` | 全板体检：条数 / 字段完整度 / 图覆盖 / 筛选轴，一次列出所有可量化的缺陷。 |
| `audit_common_item_dual_source.py` | Create an unpublished, source-preserving common_item dual-source audit. |
| `audit_common_item_family.py` | Static set-level audit of the BA8 common_item split table family. |
| `audit_common_item_split_shell.py` | Read-only literal audit of the common_item split-table loader shell (BA8). |
| `audit_coupling.py` | 盘点 wiki 构建脚本的耦合点：硬编码路径、直接写盘、重复解码。 |
| `audit_fashion_icons.py` | 时装图标双重校对（只读资源，产出校验图/CSV/JSON）。 |
| `audit_fashion_identity.py` | Independent audit for the P4-3 fashion identity bundle. |
| `audit_fixes.py` | 自查修复： |
| `audit_grade_effects.py` | 按 GRADE_EFFECT_RULES 核对 weapon_skin v0.2 的品级×特效覆盖（只读审计，不改任何数据）。 |
| `audit_item_identity.py` | Independent P4-2 item/equipment identity coverage and conflict audit. |
| `audit_item_identity_expansion.py` | P4-A2 audit of unresolved common_item base identity schemas. |
| `audit_item_master_v01.py` | Independent P4-A3 ITEM_MASTER v0.1 publication audit. |
| `audit_item_master_v01_fields.py` | P4-A1 narrow audit of two fields on 1,189 verified item identities. |
| `audit_live_sources.py` | Audit locked LifeAfter source packages without extracting or writing them. |
| `audit_locator_chains.py` | Chain Auditor（v1.4）：10 项定位链不变量检查。 |
| `audit_lottery_pool_resolved_v01.py` | Independently audit LOTTERY_POOL_RESOLVED v0.1 invariants. |
| `audit_male_part_mismatch.py` | 审计时装卡里「男图部位不匹配」的情况。 |
| `audit_name_chain.py` | Mechanical audit for NAME_CHAIN_CANDIDATES.jsonl and NAME_LOCATOR.db. |
| `audit_rebuildability.py` | 抽样审计：每个已发布板块能否在新设备全量拆包后重建。 |
| `audit_skin_sfx_events.py` | 武器皮肤音效：统计「行为 .sfx 路径 → FxGroup 索引 → EventName」的覆盖情况。 |
| `audit_systemic.py` | 系统性纠错扫描：一次找出「同类错误」的全部实例，而不是逐个踩。 |
| `audit_weapon_skin_optional.py` | 武器皮肤「可选残差」定界侦查（对任意 snapshot 基准可复跑）。 |
| `audit_wiki_full.py` | 全量核对：所有板块的 meta / items / 配图 / manifest 一致性。 |
| `backfill_fashion_face.py` | 用雷电源（pe_20261020）的 player_module_appear_data 给 fashion_face 补 provenance。 |
| `backfill_fashion_kaijia.py` | fashion_kaijia（9 条）：用 fashion_data 的 show_name 匹配补 provenance。 |
| `backfill_fashion_layers_prov.py` | 给时装板新增图层条目补 provenance（面饰/光源/投影/挂饰）。 |
| `backfill_fashion_layers_prov2.py` | 给时装板新增图层条目补 provenance —— 完全对齐板内既有条目的结构。 |
| `backfill_nucleus.py` | nucleus 回填：只补能在 PE 两张表里逐条对上的条目。 |
| `backfill_nucleus_build.py` | nucleus 剩余 76 条：用 nucleus_build_data(kj1) 的 76 行补 provenance。 |
| `backfill_nucleus_extra.py` | nucleus 收口：补上表里多出来的 2 个核芯；板上多出的 2 个标 table-absent。 |
| `backfill_provenance.py` | 回填已核验板块的 provenance（只补真实验证过的，不编）。 |
| `backfill_scene_names.py` | 把子代理查出的 25 个场景名回填进 scene_balance.json。 |
| `backfill_vehicle.py` | 用 vehicle_ui_data（0x76，277 行）给 vehicle_catalog 补 provenance。 |
| `bindict_provenance.py` | Read-only BinDict decoding with replayable CHS slot provenance. |
| `build_activity_master.py` | 活动总表：huodong_conf(kj1) 一行一个活动。 |
| `build_appearance_bud.py` | 建立「半感染者花苞」板块：取人物时装里带 reborn_vis（是否隐藏半感染者花苞）的卡。 |
| `build_appearance_extra.py` | 建「其他外观」板：player_appear_data 里 fashion_data 没有的发型/脸型/背包/挂饰/特效等。 |
| `build_audio_board.py` | 构建武器皮肤音效板：把能定位到的 WAV 复制进站点，生成 audio_catalog 板块。 |
| `build_avatar_full.py` | 重建「头像 / 头像框 / 名片框」全量板：三张表 + 分服变体 + 全量 2D 定位。 |
| `build_class_layer.py` | 按玩家用途补一层分类（学社区图鉴的纲）：配方表 + 道具总表的类别字段。 |
| `build_core_skill_board.py` | 抽出「12 星全量特技表」：极品核芯 50 条，特技全文 + 升星段。 |
| `build_equipment_attrs.py` | 建「装备属性」板：all_equips 的 attrs（伤害/护甲/血量加成…）从嵌套行帧解出后的落库。 |
| `build_fashion_identity_candidates.py` | P4-3 fashion identity candidate rules. |
| `build_fashion_identity_locator.py` | Build the P4-3 fashion identity SQLite locator. |
| `build_fashion_registry.py` | 生成人物时装全量登记表：fashion_data + player_appear_data + simple_fashion_data 三源合并。 |
| `build_field_names.py` | P2-1：字段名绑定（table + schema_ref + field_slot → 真实字段名）。 |
| `build_fpk_index.py` | 建立**武器皮肤图像定位链**的地基：全 fpk 帧级资源索引（一趟建好，永久复用）。 |
| `build_fsb_sample_index_pe.py` | 扫 gpk 里的 FSB5 bank，建/并「样本名 → (包, bank 偏移, 长度, 样本序号)」索引。 |
| `build_gene_board.py` | 潜能板增强：解析 gene_node_data 的四条序列。 |
| `build_id_locator.py` | P1-9：标识 → 出现位置 定位索引构建器（基于 file_index_entries.jsonl）。 |
| `build_id_occurrence.py` | P1-13：数字 ID 出现位置索引（复用 P1-12 row_index 定位与解码器行语义）。 |
| `build_issue3_pseudo_reply.py` | 把 calc_internal 伪代码按阶段整理成两条 issue 评论正文（Markdown）。 |
| `build_item_identity_candidates.py` | P4-2 item/equipment identity candidate rules and builders. |
| `build_item_identity_locator.py` | Build the P4-2 item/equipment identity SQLite locator. |
| `build_item_master_full.py` | 全量道具总表 item_master_full：经典服/简单生存/会员专享 的 common_item + gift_data + all_equips |
| `build_kill_broadcast.py` | 建「击败播报 / MVP 结算动画」板（2026-10-22 重建）。 |
| `build_kill_broadcast_kit.py` | 示例：用 board_kit 重建「击败播报」板块（展示第三方最小写法）。 |
| `build_locator_chains.py` | 生成 canonical Locator Chain 层（v1.4 Phase 1）。 |
| `build_lottery_board_v2.py` | 把 lottery_inventory + lottery_server_variants 合并成奖池板 v2。 |
| `build_lottery_board_v3.py` | 奖池板 v3：严格按活动表重建。 |
| `build_lottery_pool_resolved_v01.py` | Build LOTTERY_POOL_RESOLVED v0.1 from source-locked BinDict tables. |
| `build_misc_boards.py` | 补三张表：状态效果(buff_data) / 实体(common_entity_data) / 说明条目(desc_info_data)。 |
| `build_name_chain_candidates.py` | Build replayable name-chain candidate and audit records. |
| `build_name_locator.py` | 构建 NAME_CHAIN_CANDIDATES.jsonl 的 SQLite 名称定位库。 |
| `build_nucleus_board.py` | 重建 nucleus 核芯板：只用 PE 表，按服型标注，带筛选。 |
| `build_pc_index_layered.py` | 建分层 PC 索引：同一 fid 多份时按「包版本顺序」取最新，并记录候选数。 |
| `build_pvp_attr_table.py` | 生成 PvP 相关属性表：id / 名称 / 战力权重 / 是否吃压缩 / 压缩曲线。 |
| `build_recipe_board.py` | 食谱板块（三、活动类 / （四）食谱）：cook_recipe_data 571 条 → 卡面 + 成品图标 + 材料组。 |
| `build_registry_board.py` | 把 fashion_registry.json 生成成 wiki 板块 data/boards/fashion_registry.json。 |
| `build_release_pack.py` | 打包 wiki 数据包：板块 JSON/JS + live_sources + 图标素材（不含 3D/Spine/音频）。 |
| `build_release_pack_v2.py` | 打包 wiki 数据包 v2：**按引用收集**，不再硬编码白名单。 |
| `build_reliable_sources.py` | P3：可靠数据源筛选 v2 —— 源状态=类别关键槽聚合。 |
| `build_row_index.py` | P1-12：行级定位索引（test BA8 快照，全表数据体）。 |
| `build_scene_balance.py` | 场景 × 伤害加成上下限 映射表（hurt params + space_data 名字）。 |
| `build_scene_balance_branch.py` | 场景伤害加成（按服型分档）：经典服 / 简单生存服 并列，不混算。 |
| `build_scene_board.py` | 把场景加成上下限做成 wiki 板块（PvP 优先），并挂进三、活动类。 |
| `build_scene_board_v2.py` | 把场景加成上下限做成 wiki 板块（按场景名合并，PvP 优先）。v2 |
| `build_server_types.py` | 服型板块：以 toolkit_core/server_types.py 为唯一来源（本地已有结论）。 |
| `build_skin_assets.py` | 给**一个武器皮肤**构建完整素材（音效 + 图片）—— 单包作业，不搞全盘扫描。 |
| `build_skin_sfx_real_names.py` | 建立「皮肤 → 音效真名（内部名）」映射。 |
| `build_source_registry.py` | 统一 source registry 构建器（P0-6/7 收尾）。 |
| `build_stub_index.py` | 建「桩表 → 真表」索引：808/815B 的空壳表在还原树里另有同名/同族真身。 |
| `build_table_families.py` | P1-11：表族成员关系正式固化（family members 结构关系，无运行时推断）。 |
| `build_table_index.py` | P1-10：table_index 构建器 —— 从 BA8 全量条目找"配置表"（纯定位，无字段语义）。 |
| `build_table_inventory_for_basis.py` | A2：为**指定工作副本**建基线内的表清单（table inventory，含 FID）。 |
| `build_talent_by_prof.py` | 天赋按职业分类 + 种族潜能独立成表。 |
| `build_taxonomy_v2.py` | 按用户草稿重建 wiki 目录树（四分类），旧树备份为 wiki_taxonomy_旧_20261022.json。 |
| `build_taxonomy_v3.py` | 按草稿逐字重建 taxonomy：不加任何说明后缀，子级序号一一对应。 |
| `build_text_boards.py` | 补齐文字表板块：称号 / 头像（框+动态）/ 技能。 |
| `build_theme_talent.py` | 主题天赋总表（theme_new_talent_data, kj1 独有 2,572 行）。 |
| `build_upcoming_auto.py` | 重建「零、新更新与预告」：自动从武器皮肤板 / 奖池板筛「未上架」条目。 |
| `build_weapon_glb.py` | 武器本体网格 → GLB（几何 + UV + 计算法线，中性材质）。 |
| `build_weapon_skin_binding_phase2.py` | Weapon Skin Source Binding Phase 2 — Explicit Mapping Closure（用户 2026-09-13）。 |
| `build_weapon_skin_commerce_6b.py` | Weapon Skin Phase 6B — Listing / Acquisition Final Closure（用户 2026-09-13）。 |
| `build_weapon_skin_commerce_phase6.py` | Weapon Skin Phase 6 — Listing / Sale / Acquisition Graduation（用户 2026-09-13）。 |
| `build_weapon_skin_compendium.py` | Weapon Skin Final Phase — Compendium Reconciliation & Graduation。 |
| `build_weapon_skin_effect_standard.py` | Weapon Skin Effect Detail Standard（用户 2026-09-13 正式业务展示规则）。 |
| `build_weapon_skin_final_closure.py` | Weapon Skin Combat Presentation — Final Closure（用户 2026-09-13）。 |
| `build_weapon_skin_grade.py` | Weapon Skin Phase 4（口径修正版）— Grade / Classification。 |
| `build_weapon_skin_hotfix_record.py` | 从 PC 测试服热更落盘的解码 payload 里，抽出武器皮肤热更覆盖记录。 |
| `build_weapon_skin_presentation.py` | 生成 WEAPON_SKIN 展示层边车（PRESENTATION_LEGACY.jsonl）。 |
| `build_weapon_skin_rebaseline.py` | A3：武器皮肤链 —— 新基准(328b8446) vs 旧基准(BA8A) 双基解码与差异审计。 |
| `build_weapon_skin_source_bindings.py` | Weapon Skin Effect Source Binding（用户 2026-09-13 阶段：只做连边，不改分类/UI）。 |
| `build_weapon_skin_source_graph.py` | Weapon Skin Source Graph（用户 2026-09-13 最高优先级要求）。 |
| `build_weapon_skin_variant_phase5.py` | Weapon Skin Phase 5 — Variant / Timed Graduation（用户 2026-09-13）。 |
| `build_wiki.py` | 02_wiki\\web builder v0.1（骨架版） |
| `build_workcopy_current_package.py` | A1：为当前体验服 Documents 包（328b8446）建**验证式工作副本**。 |
| `calib_array_base.py` | 标定参数数组描述符的偏移基准：file / blob / 组头偏移三种假设逐个打分。 |
| `calibrate_business_chains.py` | calibrate_business_chains.py —— 业务定位链双服双版本校准器（2026-09-06 用户定版铁律） |
| `carve_fsb5_banks.py` | gres 包 → FSB5 bank → WAV（终版：先按条目解包，再在解出文件里开凿）。 |
| `carve_named_samples.py` | 按样本名从 FSB 索引精确取 WAV，并挂到指定皮肤卡的音效区。 |
| `cdp_probe.py` | CDP 探针：打印页面元素布局与计算样式，排查栅格宽度。 |
| `cdp_shot_local.py` | CDP 截图：打开页面 → 执行 JS（可选）→ 截图。用于本地主题验收。 |
| `check_audio_files.py` | 统计武器皮肤音效清单的文件命中率（按 basename 在全库 WAV 里找）。 |
| `check_board_tables.py` | 全量核对：所有 board 的 provenance.table 是否指向真实存在的文件。 |
| `check_board_tables_v2.py` | 全量核对 provenance.table（v2：先建索引，避免 glob 风暴）。 |
| `check_fashion_parts.py` | 核对时装板的部位归类：以 fashion_data 的 part_type 为准，列出不一致的条目。 |
| `check_image_alpha.py` | 统计板块引用图片里有多少是「不透明白底」，用于决定是否需要抠白。 |
| `check_latest_npk_for_skin.py` | 从最新 PE 测试服 script npk 直接取表，检查目标 id 是否已进最新数据。 |
| `check_parts_by_model.py` | 按 model_id 反查部位：只在「源表该 model 只有一种部位」时比对，避免整套误判。 |
| `checks.py` | 三线台账「可核判据」注册表（台账里写 @名字 引用这里）。 |
| `clean_junk_20261025.py` | 清理站点与仓库根目录的无用文件（备份 / 探针 / 旧页面 / 设计稿截图）。 |
| `clean_pc_tree_files.py` | 只清理 PC 树里的解压文件，保留目录骨架 + .gitkeep；索引库不动。 |
| `clean_site.py` | 站点清理 + 依赖归位。 |
| `compare_flame_skeletons.py` | 用骨骼名集合的 Jaccard 相似度，给喷火器皮肤找最接近的本体。 |
| `compare_server_scene_params.py` | 对比「经典服 / 简单生存服」的伤害加成上下限参数。 |
| `crack_mesh_layout.py` | 破解 .mesh 顶点布局：用【尺度无关的包围盒比值判据】穷举候选布局。 |
| `damage_calc.py` | 伤害计算器：武器攻击力 × 场景加成区间 × (1 − 目标减伤)。 |
| `decode_effect_show_v2.py` | 尝试解 weapon_skin_effect_show_data（皮肤战斗表现正式名表）。 |
| `decode_hurt_arrays.py` | 正确解析 special_hurt_params 的数组描述符：值起点 = 0x27 组头 +1。 |
| `decode_hurt_params.py` | 解 special_hurt_params_data（伤害加成真正的分段参数表）。 |
| `decode_probe.py` | decode_probe.py —— 解码探针：单表第一眼（表型指纹 + 行级解码 + 字段错位警示） |
| `decode_skin_effect_show.py` | 解 weapon_skin_effect_show_data：皮肤 → 战斗表现的正式特效名。 |
| `decrypt_npk.py` | 验证 CDN 下载的 npk 容器：前 8 字节明文 + AES-ECB(固定密钥) 的 NXPK。 |
| `dedupe_fashion_images.py` | 时装卡图轨去重：同一张图只留一张（_b / _s 只算尺寸档，不算不同图）。 |
| `dedupe_media.py` | 图轨去重：同一张图的高清/低清只留高清版。 |
| `dis_arm64.py` | 反汇编 GPK AttachGpk 附近代码（ARM64），并找 magic 常量比较。 |
| `download_pe_npk_full.py` | 全量下载 PE 客户端 npk（CDN 直链，断点续传 + 尺寸校验）。 |
| `download_pe_npk_full_v2.py` | 全量下载 PE 客户端 npk（CDN 直链，8 并发，断点续传 + 尺寸校验）。 |
| `drop_pc_skeleton.py` | 把 PC 树的目录骨架导出成清单文件，然后删掉这棵树（省空目录的 4KB 块浪费）。 |
| `dump_weapon_1013_10.py` | 1013_10 全链路拆解：本体资源清单 + 本地落地情况 + FSB 音频参数 + 结论。 |
| `enrich_skin_sfx_real_names.py` | 把「音效真名（内部名）」写进武器皮肤板的每张卡。 |
| `ensure_builder_inputs.py` | ensure_builder_inputs.py — 审计并补齐 builder 的隐式输入（非 board 依赖）。 |
| `estimate_coverage_ceiling.py` | 估算：PE 全量包到位后，各板「有图率」上限能到多少。 |
| `export_avatar_icons_hires.py` | 批量导出名片框/头像图标：PE 源，多档候选里只取最高清，低于阈值跳过。 |
| `export_classic_hurt_params.py` | 经典服 special_hurt_params_data：按数值特征推定 min/max 两列，导出 CSV。 |
| `export_effect_icons.py` | 导出武器皮肤战斗表现面板图标（12 个固定 UI 图标）并回填到板数据。 |
| `export_exchange_static_candidates.py` | 导出 Documents common_exchange_shop_data 的全量静态格子总表。 |
| `export_fashion_face.py` | 人物·面饰/挂饰板块。 |
| `export_fashion_kaijia.py` | 铠甲勇士联动·人物外观专题（BA 快照，经 lib_fashion 统一解码 + 面饰专池补充）。 |
| `export_fashion_wardrobe.py` | 全量时装衣柜板块（人物类）——★ 权威源换成【表结构解析的行】。 |
| `export_fpk_textures.py` | 从 fpk 主资源包导出贴图（含图集切片）——2026-09-13 定稿版。 |
| `export_kaijia_phase2.py` | 二期「铠甲再临(刑天飞影)」奖池板块 —— 已实装版（2026-09-01 快照 BA8A239A）。 |
| `export_lottery.py` | 导出板块：限时主题抽奖奖池（已上线帝皇 = verified；未上线铠甲再临 = candidate/structure） |
| `export_lottery_icons.py` | 给奖池板 402 条挂图标：PE .ktx 优先，PC .bc7 兜底，导出到 assets/lottery_icons/。 |
| `export_lottery_icons_fast.py` | 奖池图标批量导出（快版）：先 SQL 解析全部 fid，再按包一次性扫行解码。 |
| `export_poster.py` | 从当前查看器同一次运行导出海报（P2）。 |
| `export_vehicle_catalog.py` | 载具模型清单板块（图鉴类-载具）。 |
| `extract_asset_path_dictionary.py` | 从脚本包抽**全量资源路径字典**（路线 C：依赖图传播命名）。 |
| `extract_attr_curves.py` | 解析加成压缩曲线：special_attr_params_data + compressed_attr_data。 |
| `extract_compress_curves.py` | 抽取 compressed_attr_data 的折线端点（base + kj1），输出 JSON。 |
| `extract_gres_audio_banks.py` | 扫全部 gres 包，抽出其中的 FSB5 音频 bank → WAV（样本名取自 bank）。 |
| `extract_kaijia_formal_tables.py` | Extract only the formal-client tables needed for the Kaijia lottery trace. |
| `extract_pe_full_tree.py` | 全量 PE 还原树：把 176 个 gpk 逐条解出来，落成文件树（配置 + 资源一视同仁）。 |
| `extract_raw_asset.py` | 按逻辑路径从 PE gpk 原样导出任意资源（mesh/gim/mtg/sfx/png…）。 |
| `extract_ui_assets.py` | 按**UI 声明的路径**从资源包里挖图片（不用名字猜纹理）。 |
| `fetch_ui_icon_by_fid.py` | 按 fid 在 ui_*.gpk 里定位条目并导出（只读源包）。 |
| `fill_appearance_icons.py` | 给时装板里「其他外观」类条目补图标（挂饰 / 戒指 / 半感染者花苞 / 面饰 / 发型…）。 |
| `fill_board_icons_from_pe.py` | 给 0% 的板块灌图标：board icon 字段 → fid → pe_index(pack,row) → gpk 行 → PNG。 |
| `fill_board_icons_pe_batched.py` | 给 common_item_text_sources 补齐图标 —— 分批落盘、可续跑版本。 |
| `fill_board_provenance.py` | 补齐时装板里缺的可机读定位链（publication gate 要求 5 个 provenance 字段）。 |
| `fill_broadcast_only_activities.py` | 补齐「广播里有奖励、板上却没有期次」的活动。 |
| `fill_chip_effect.py` | 给战术芯片补「首档效果」：belt_chip_data.base_desc + base_params(jump 浮点组)。 |
| `fill_core_star_entries.py` | 给核芯板补「升星固定解锁」：nucleus_build_data.rank_to_desc（星级 → 文案）。 |
| `fill_core_star_values.py` | 核芯升星数值：A 绝对值型（buff 参数即百分比）/ B 系数型（面板=基础×系数）。 |
| `fill_fashion_by_model.py` | 按 model_id 直造反图候选，给「完全无图」的时装卡补图。 |
| `fill_fashion_detail_fields.py` | 给时装卡补三个「详情」字段：花苞可见、副武器可见、可隐藏部位（挂件等）。 |
| `fill_fashion_extra_icons.py` | 给时装板剩余缺图条目补图：面饰（slots 板 icon 字段）+ 挂饰（all_equips icons 跳转组）。 |
| `fill_fashion_from_icons_all.py` | 给「表里登记了 icons_all 但没取到图」的时装卡补图：直接按登记路径试 _b/_s。 |
| `fill_fashion_gender.py` | 用 appear_ids 定每套时装的性别（男/女/男/女/未知）。 |
| `fill_fashion_icons_by_model.py` | 按 fashion_data.icons 跳转组给时装板补图标。 |
| `fill_fashion_icons_generic.py` | 时装板补图（通用）：从 item id 数字段取号，依次查 |
| `fill_fashion_male.py` | 补齐时装卡的男角色图（只用 PE 源）。 |
| `fill_fashion_male_v2.py` | 用 fashion_data 的 icons 组反推男图：model_id → 该套注册的全部图标名。 |
| `fill_fashion_posters_pc.py` | 12 条仅 PC(ui_01.gpk) 命中的时装补图：尝试 pc 取图并回写 board。 |
| `fill_fashion_posters_pe.py` | 时装板补图（PE 索引命中版）：fid 命中 → pe_packs 解包 → assets/fashion_posters/<id>.png → 回写 _med |
| `fill_item_icons_from_pe_packs.py` | 从 PE（雷电模拟器）gpk 包批量导出道具图标，回写 item_master_full。 |
| `fill_item_images_from_binding.py` | 用 pe_icon_bind/binding_rows_v2.jsonl 给 item_master_full 灌图。 |
| `fill_item_master_icons.py` | 全量道具总表补图（按 icon 路径去重导出）。 |
| `fill_killboard_icons.py` | 击败播报 5 条配 2D 图标（PE only）。icon_jisha01..05 → _b/_s 后缀命中。 |
| `fill_lottery_building_icons.py` | 用 building_icon 族补奖池无图成员（家具/建筑类图标在 ui/building_icon/icon_<id>）。 |
| `fill_lottery_icons_all.py` | 给合并后的奖池板批量补图：icon 字段族 + item_icon + building_icon，按包一次扫完。 |
| `fill_lottery_icons_cached.py` | 用 _cache_official_icons.json 给奖池板补图（分批、可断点续跑）。 |
| `fill_lottery_icons_official.py` | 用完整道具表（36,510 行）的 icon 字段给奖池板补图。 |
| `fill_mvp_media.py` | MVP 8 条回写图片：优先用 assets/kill_broadcast 里已导出的 mvp_bq_mvp_0X[_cover].png。 |
| `fill_namecard_static.py` | 名片框（无 spine 的静态图款）补图：business_card_scheme_data.image_path → assets/avatar_frames |
| `fill_placeholder_names.py` | 占位名兜底：对每个「道具 <id>」在全部成对表里找该 key 行，取其中**最像名字的中文串**。 |
| `fill_sf_entry_items.py` | 给 SuperFashion 期次补入口三件（left_item_id / right_item_id / right_bag_item_id / share_ |
| `fill_show_reward_names.py` | 给「展示奖励 <id>」补名：跨表扫描 common_item / fashion / gift / vehicle / body_sfx / recipe。 |
| `fill_skin_audio.py` | 把皮肤音效按页面约定补到 assets/audio/weapon_skin/<dir>/<file>。 |
| `find_gim_by_bounds.py` | 按「已知边界体的 float32 字节」在 model_*.gpk 里定位 .gim 模型本体。 |
| `find_got_refs_all.py` | 全可执行段扫 GOT 槽引用（ADRP + 后续 LDR）。 |
| `find_gpk_got_refs.py` | 找指向 GPK API 字符串槽（GOT）的代码：ADRP+LDR 对。 |
| `find_gpk_reloc.py` | 用 .rela.dyn 的 addend 反查 GPK 字符串引用（GOT/指针表）。 |
| `find_gpk_xrefs2.py` | 找 GPK ReadFromFile / decrypt_content 字符串的 ARM64 xref。 |
| `find_gpk_xrefs_arm64.py` | 在 ARM64 libclient.so 里找 GPK 相关字符串的 xref（ADRP+ADD 模式）。 |
| `find_orphan_tests.py` | 找出「只测已删除板块」的测试文件，列出来供归档。 |
| `find_oversea_source.py` | 在多个 script npk 源里找 oversea 表的 fid，定位可恢复来源。 |
| `find_skin_audio_banks.py` | 定位并提取**武器皮肤音频**：在 gpk/npk 里裸搜 FSB5 bank + 皮肤音效名。 |
| `find_special_hurt_refs.py` | 找 special_hurt_params(经典服 693 行) 的 key 被谁引用。 |
| `fix_1110188_reload_is_voice.py` | 一魂共鸣换弹音效=角色语音（vo_gunreload_all），移除误挂的步枪通用换弹底座。 |
| `fix_1110189_base_audio.py` | 1110189（传世·喷火器）音频：改用新式喷火器底座 weapon_1013_10_*，并保留通用补充。 |
| `fix_1110189_paint_name.py` | 按用户实机口径修正 1110189：菌焰喷火器的「幻海」涂装，不是新一代武器。 |
| `fix_brand_ratio.py` | 横幅改回正常比例（不放大裁切）；侧栏底图铺满整列高度。 |
| `fix_bucket_pendants.py` | 修正时装板的部位归类： |
| `fix_cdata_paths.py` | cdata 归一后修引用：把硬编码的 配置_增量快照 / 配置_基线包 指向唯一一份 配置。 |
| `fix_coating_vs_skin.py` | 纠正：涂装(coating) 与 皮肤(skin) 是两套系统。 |
| `fix_core_layout.py` | 核芯详情整理：品级四档（极品/高级/中级/基础）+ 去重 + 技术信息二次折叠。 |
| `fix_core_stars.py` | 核芯表按经典服口径收口：品级色 + 星上限（蓝5/紫9/金12）。 |
| `fix_escape_and_rest.py` | 修正上一轮被 \f 转义破坏的路径，并处理剩余三类声明。 |
| `fix_fashion_gender_pairs.py` | 补时装缺失的另一个性别图。 |
| `fix_fashion_meta.py` | 时装板：删掉「全量登记表」入口；把图标命名规律写进技术详情（meta.notes）。 |
| `fix_fashion_parts.py` | 时装部位纠偏：以 fashion_data.part_type 为准，只改「名字完全对得上」的冲突项。 |
| `fix_gene_races.py` | 种族潜能修订（用户 2026-10-26 口径）： |
| `fix_hero_bg.py` | 修掉 .wp-hero 后置 background 覆盖横幅图的问题，合并为单条多图层。 |
| `fix_hero_crop.py` | 横幅取右半（避开图内自带 LA 文字），并隐藏旧的武器艺术图，避免叠字/叠图。 |
| `fix_hero_crop2.py` | 横幅放大裁到右半（去掉图内自带 LA 字样）；直接给 .wp-hero-art 加内联隐藏。 |
| `fix_legacy_provenance.py` | 给仍在发布的旧板补 provenance（发布门禁要求的 5 个字段），来源用板自带的 package_sha。 |
| `fix_lottery_period_names.py` | 把「典藏抽奖 配置N」这类占位期次换成真活动名 + 起止时间。 |
| `fix_male_by_name_part.py` | 按「卡名部位」校正男图：名字写 -头饰 就必须是 icon_h_m，-衣服 必须 icon_b_m。 |
| `fix_male_part_mismatch.py` | 修正「男图取成男衣服」的问题：男装图必须与卡部位同族，否则按女图换性别重取。 |
| `fix_male_part_mismatch_v2.py` | 修正「男图取成男衣服」：只处理「已知部位族且不匹配」的男图。 |
| `fix_meta_subtitles.py` | 精校副标题三要素：来源 / 生成日 / 源包摘要。 |
| `fix_mvp06_icon.py` | 补齐 mvp_06 图标：ui/shangcheng_icon/jingshi/icon_mvp06.ktx（0000.gpk row 12735）已导出。 |
| `fix_mvp06_media.py` | 补齐 mvp_bq_mvp_06（沙海月鸣）的男款主视觉，并如实标注图标未进包。 |
| `fix_mvp06_transparent.py` | MVP 沙海月鸣：删男款结算截图；图标立绘去黑底转透明。 |
| `fix_part_card_provenance.py` | 补齐部位补卡的 provenance（契约要求 source_id / locator_chain / source_lock_sha256 / upstrea |
| `fix_part_card_provenance2.py` | 给部位补卡生成契约合规的 provenance（严格照既有卡的形状）。 |
| `fix_projection_from_full_items.py` | 用完整道具表（pe_test_script/common_item_data_base.py，36,510 行）补齐时装板「投影」的 |
| `fix_provenance_tables.py` | 修正 board provenance.table 指向：先探测哪张真实表含这些 row_key，再回写。 |
| `fix_rebuild_paths.py` | 修 rebuild_wiki_v01.py 里 "str" / "str" 的路径拼接（会 TypeError）。 |
| `fix_sb_quote.py` | 修 board.html 里 sbRender 的引号语法错误（来源类型那一列）。 |
| `fix_scene_nav.py` | 场景/伤害分析页收口： |
| `fix_side_fullheight.py` | 侧栏：改为 sticky 满视口高度，底图铺满整列而不是只在文字处。 |
| `fix_source_label.py` | 副标题来源归一：把 meta.source_server 的长句压成可核对的口径，写进 meta.source_label。 |
| `fix_source_three_parts.py` | 副标题来源三要素：还原树源 + 数据源（表） + 服务器类型。 |
| `fix_source_three_parts2.py` | 副标题来源三要素（v2）：还原树源 · 数据源表 · 服务器类型。 |
| `fix_tree_refs.py` | 41_还原树 重排后的路径引用批量改写。 |
| `fix_wiki_grid.py` | 修正 wiki 渲染：每个大类一个瓦片网格（原来每个叶子节点各一格，导致一列一个）。 |
| `fix_wiki_polish.py` | wiki 修尾：标题中文化、时装缩略图、两行标题、路径去编号。 |
| `fix_ykxq_and_chip.py` | 处理 ykxq 变体缺失的 658 条 + chip 注解 65 条：能对上行的才改，否则标 unresolved。 |
| `gen_home.py` | 生成站点主页 index.html —— LifeAfter 拆包项目 · 左侧信息块 + 右侧三线三带。 |
| `gen_layout_mockups.py` | 生成 3 个 wiki 首页布局方案（真实数据抽样），供用户挑选。 |
| `img_kind.py` | 图片按**内容**判「是不是素材底图」—— 给 wiki 用的小封装。 |
| `import_pendants.py` | 把真正的「挂饰」（gift_data 中 icon_270xxx 的 28 条礼盒）配图并进人物时装板。 |
| `import_pendants_full.py` | 挂饰全量：all_equips_data(oversea kj1) 里 id 270xxx 段 = 挂饰本体（124 件）。 |
| `import_yk_preview_pools.py` | 把 yk（会员专享）变体里的池成员单独登记成「提前曝光」期次。 |
| `index_all_npk.py` | P1-8 Stage 3a：registry 全部 npk（script+资源）条目级索引。 |
| `index_fpk.py` | P1-8 Stage 3b-2：FPK 条目（zstd 帧）索引 —— 多进程按包并行版。 |
| `index_gpk.py` | P1-8 Stage 3b-1：GPK 条目索引（FPGH v2，与 NPK/WPK 解析链完全独立）。 |
| `index_script_packages.py` | P1-8a：script 家族 11 包条目级索引（目录表级，不解 payload）。 |
| `index_wpk_idx.py` | P1-8 Stage 3b-3：WPK/IDX 盘点与索引 —— 独立于 GPK/FPK/NPK 链。 |
| `inspect_mvp06.py` | 看 mvp_action_data 里 bq_mvp_06 一行都有什么资源字段（找立绘真实来源）。 |
| `lib_fashion.py` | 时装外观表可复用加载器（数据源映射路径：fashion_data base + CHS -> 结构化行）。 |
| `link_gift_bundles.py` | 礼盒「内含」父子关系：解析 desc 文本（候选级）。 |
| `list_orphan_boards.py` | 列出未被 taxonomy / policy 引用的孤儿板块文件。 |
| `list_orphan_pages.py` | 统计 web 下各 html 的入链（被其它页面引用次数），列出零入链页面。 |
| `list_unused_assets.py` | 列出 assets 下没有被任何 html/js 引用的子目录（候选删除）。 |
| `live_npk_reader.py` | LifeAfter script NPK lazy reader for the local Wiki. |
| `locate_all_equips_pair.py` | all_equips base/CHS 自定位解析器（FID 内容派生、随热更漂移时的兜底）。 |
| `make_logo.py` | 把白底 logo 处理成透明背景 PNG（边界泛洪，保留白色笔画内部）。 |
| `make_spine_thumbs.py` | 从 Spine atlas 切出最大区域做缩略图（展示真实元素，而不是整张贴图页）。 |
| `make_web_launcher.py` | 生成 GBK 编码的 Windows 启动脚本（cmd 默认代码页 936，UTF-8 中文会乱码）。 |
| `map_flame_skin_to_base.py` | 喷火器皮肤 ↔ 本体映射：用网格包围盒尺寸做定量比对。 |
| `map_scene_names.py` | 把伤害参数表的 scene_id 映射到地图名。 |
| `mark_missing_frames.py` | 28 条名片框：框资源在 PE/PC 索引均无命中（未下发）→ 去掉坏图，标记状态。 |
| `mark_missing_frames2.py` | 动态标记：所有「框」图仍是 1292×812 旧产物且资源不可得的名片框 → 去坏图标状态。 |
| `mark_single_gender.py` | 标记「单性别款」：player_appear_data 里 force_gender 有值的 model ⇒ 只做一种性别，不追男图。 |
| `mark_single_gender_cards.py` | 单性别款的卡：把 gender 统一标成「仅女款」，并保留原始字段。 |
| `match_and_carve_skin_audio.py` | 用 FSB 样本索引，把武器皮肤「音效真名」落到 bank 并导出 WAV。 |
| `match_skin_sfx_gap.py` | 对「有 sfx 真名但没音频」的皮肤，在 FSB bank 里按样本名精确匹配，输出可提名单。 |
| `merge_alias_cards.py` | 同名同款不同写法（开发名/占位名）的时装卡合并。 |
| `merge_appearance_cards.py` | 把「外观补充卡」（长编号）并入同名的时装主卡（短编号 + 魅力值）。 |
| `merge_broadcast_rewards.py` | 用 reward_pool_data 的 broadcast_content（含活动名）把奖励挂到对应期次。 |
| `merge_core_boards.py` | 把 nucleus 并入 mutation_core_full：核芯只保留一个全量表。 |
| `merge_duration_cards.py` | 把「永久款 + 时限款」拆成两张卡的时装合并成一张。 |
| `merge_edible_recipe.py` | 可食用 + 食谱合并：食谱成为「可烹饪」子项。 |
| `merge_extra_into_fashion.py` | 按用户口径重做：其他外观 796 条全部并入（一）人物时装，按 part_code 1~7 标注部位。 |
| `merge_fashion_layers.py` | 把时装四类附加图层并进 fashion_wardrobe：面饰 / 光源 / 挂饰（投影另一步）。 |
| `merge_fashion_media_into_board.py` | 把时装图标（游戏内真实引用）缝进「全量时装衣柜」总表。 |
| `merge_fashion_part_cards.py` | 时装板合并同套多部位卡片：同一 name + 同一 model_id 的 cloth/hat/light 合为一张卡。 |
| `merge_file_index.py` | P1-8 Stage 4：统一 file_index 合并器（由各格式 summary 驱动）。 |
| `merge_pe_cdata.py` | cdata 归一（A 档）：把 配置 / 配置_基线包 / 配置_增量快照 合成唯一一份。 |
| `merge_pe_config_tree.py` | 合成全量 PE 配置树：基线包打底 + 热更增量覆盖。 |
| `merge_same_key_cards.py` | 同名同部位同 model 的多张卡收敛为一张（拆卡后的收尾）。 |
| `merge_scene_balance.py` | 场景加成平衡去重：把 (name, range, min_attack) 相同的行并成一张卡。 |
| `merge_script_layer_then_cleanup.py` | 把旧配置树（除 com/cdata 外）硬链接进归一后的 配置，再删除三份留档目录。 |
| `merge_show_rewards.py` | 把 common_hd_show_reward_data（活动展示奖励，key=活动号）挂到对应期次。 |
| `merge_skin_effect_show.py` | 把 weapon_skin_effect_show.json（皮肤→战斗表现正式名）并进武器皮肤板。 |
| `merge_superfashion_preview.py` | 把 SuperFashion 的奖励预览（panel_show_item_ids）写进奖池板。 |
| `merge_talent_boards.py` | 天赋总表合并：new_talent_data(基础) + theme_new_talent_data(主题)。 |
| `merge_vehicle_cards.py` | 载具板：同名（含时限变体）合并成一张卡，保留全部 vehicle_id。 |
| `merge_version_cards.py` | 把「前缀版本卡」并入本体卡 —— 同一套时装在 fashion_data 里有多条记录。 |
| `merge_weapon_charm.py` | 把 weapon_skin_data 的 charm_value / weapon_type 合并进武器皮肤板（按 skin_id 整数对齐）。 |
| `normalize_board_meta.py` | 按 wiki_taxonomy 修正每个板块的 meta.category；时装类统一来源副标题（含详细还原树路径）。 |
| `normalize_fashion_parts_cn.py` | 统一人物时装的部位标签：把英文 part（cloth/hat/bag/light/suit）归一成中文， |
| `normalize_lottery_names.py` | 把广播表的内部简称换成正式名，并按 item_id 去重。 |
| `normalize_provenance.py` | 把已发布板块的 provenance 规范化成发布契约能过的最小完备形态。 |
| `normalize_scene_source.py` | 统一场景平衡板块的来源口径（去掉旧路径 pe_20261020）。 |
| `normalize_table_names.py` | 规范化 provenance.table：去掉注解后缀；仍解析不到的标 table_status=unresolved。 |
| `note_1110189_reserved.py` | 把 1110189 的穷举负证据写进卡面与报告，避免以后再挖一遍。 |
| `note_male_scope.py` | 技术详情补一条男图口径。 |
| `parity_check.py` | 双源一致性检查：同一个 builder 分别用 PE / PC 表根跑一次，比对条目 id 集合。 |
| `parse_attr_curves.py` | 解析 special_attr_params_data 的加成压缩曲线（0x27 帧 + 0x12/0x22/0x01 元素）。 |
| `parse_c159.py` | 解析 .c159 文档（明日之后 NeoX 资源描述符）为可读 JSON。 |
| `parse_chenshi_periods.py` | 把公告宸世段（announce_chenshi.json）按首日期对齐 optional_version_data 期次，更新 rebuild 脚本的期次内容层 |
| `parse_file_hash_pack.py` | P1-8 Stage 1：file_hash_pack.bin（FHPK v2）解析与评估。 |
| `patch_build_meta.py` | 让 build_wiki.py 生成 data/build_meta.js（版本/设备/时间），供 wiki 横幅自动读取。 |
| `patch_skin_audio_realnames.py` | board.html：皮肤音效区补「真名（内部名）」展示。 |
| `patch_skin_grade_1110189.py` | 改标：把「传世 + 周年庆」从 1110188（一魂共鸣）撤掉，标到 1110189（喷火器，行为预告行）。 |
| `patch_skin_grade_chuanshi.py` | 把 1110188 一魂共鸣的品级标成「传世（6）」+ 周年庆，并保留原始表值以便追溯。 |
| `patch_skin_names_20261017.py` | 把本批武器的**验证名 + 真值字段**写进看板  weapon_skin_sfx_text_sources。 |
| `patch_skin_names_note.py` | 收尾：把看板里「星魂追光只是候选名」的旧叙述改成「已由道具行正式名取代」。 |
| `patch_skin_names_stats.py` | 按 items 现状重算名字相关统计（stats + meta.notes 里的计数），避免页面数字和卡片打架。 |
| `polish_new_boards.py` | 修两个新板的展示层：state_summary 扁平化（消除 [object Object]）+ 卡面摘要 + 中文字段名。 |
| `preview_board_contract.py` | Frozen-artifact (publication contract v3) provenance for preview sub-cards. |
| `probe_bindict_uleb.py` | 试 uleb128 编码在 bindict payload 里能否找到 1500401 等 id。 |
| `probe_effect_show_01.py` | probe_effect_show_01 — 定位 weapon_skin_effect_show_data 的布局候选。 |
| `probe_effect_show_02.py` | probe_effect_show_02 — 用 body(269..) 走 decode_table_rows，看行/schema/索引。 |
| `probe_effect_show_03.py` | probe_effect_show_03 — 解出全部行，dump 1110171。 |
| `probe_effect_show_04.py` | probe_effect_show_04 — 定位目标字符串的 pool 索引，并在 blob 里搜索其出现位置。 |
| `probe_effect_show_05.py` | probe_effect_show_05 — 搜索目标 pool 索引在 blob 中的出现位置，并归到索引行区间。 |
| `probe_effect_show_06.py` | probe_effect_show_06 — dump 关键区块原始字节（头部/首个行块/1110171 候选块）。 |
| `probe_effect_show_07.py` | probe_effect_show_07 — 扫描全部 0x86 子记录并把行内 jump 元素解析到记录。 |
| `probe_effect_show_08.py` | probe_effect_show_08 — 用 weapon_skin_data 的 *_functions jump 组做独立交叉验证。 |
| `probe_effect_show_build.py` | probe_effect_show_build — 生成 weapon_skin_effect_show.json（皮肤ID → 战斗表现各项）。 |
| `probe_effect_show_layout.py` | 反推 weapon_skin_effect_show_data 行布局： |
| `probe_factor_groups.py` | 全面拆 factor：把参数表里所有 0x27 组建索引，再核对每个描述符指向什么。 |
| `probe_fashion_pe_coverage.py` | 抽样检查：时装板里的图片路径到底在 PE 索引里有没有（还是只能靠 PC 回落）。 |
| `probe_fashion_rows.py` | 在 fashion_data 里找某个名字的全部行（含部位/desc/model_id），核对是否漏录。 |
| `probe_fashion_rows_by_name.py` | 查某个时装名在 fashion_data / player_appear_data 里的全部行与字段（找男图线索）。 |
| `probe_files_db.py` | 看 lifeafter_files.sqlite3 能不能给出「表文件 → npk entry_index + file_id」。 |
| `probe_gender_scope.py` | 按 model_id 查 player_appear_data 的 gender / force_gender，判断是否仅女款。 |
| `probe_gpk_fid.py` | 验证 GPK 条目表里的 crc1/crc2 是否就是 fid 两半，并按 fid 取图标。 |
| `probe_gpk_table.py` | 试探 GPK 条目表的混淆方式：XOR 候选键 / AES 候选键，判据=记录字段是否合理。 |
| `probe_hat_match.py` | 按「配色 + 剪影」在全库找女头饰的男版：同尺寸 + 颜色直方图相似度排序。 |
| `probe_hat_neighbors.py` | 按「同尺寸邻居」找男头饰图标：女头饰图已知，男头饰应与它同分辨率、同包。 |
| `probe_hat_sheet.py` | 女头饰同包同尺寸、行号最接近的候选 → 逐张存 PNG → 拼 contact sheet（带行号）。 |
| `probe_hpgf_cbc.py` | HPGF 表加密模式继续标定：CBC 链式 IV 候选 / 分块试探。 |
| `probe_hpgf_modes.py` | 试 AES-CBC/CTR 等模式解 HPGF 条目表（IV 取头部若干候选）。 |
| `probe_hpgf_table_stats.py` | HPGF 条目表：先看统计结构（列熵、周期性、可能的 XOR 常量）。 |
| `probe_missing_male_cloth_hat.py` | 检查缺男图的「衣服/头饰」卡：其 model 的图标组里到底有没有男图。 |
| `probe_namecard_pages.py` | 名片框贴图页：宽后缀探 pe/pc 索引，命中即取图落到 spine_live/<atlas目录>/<page>。 |
| `probe_oversea_in_npk.py` | 检查 script npk 里能否按名字（fid）取回 oversea 表。 |
| `probe_scene_tables.py` | 在 PE 树里找带 scene id 的表，并尝试取名字。 |
| `probe_skin_sfx_rows.py` | 查某个武器皮肤 id 在音效相关表里的全部行。 |
| `probe_table_entry.py` | 用 fid = fid_of(表路径) 在 entries 里查 entry_index + file_id（容器可能是 script npk）。 |
| `probe_untyped_containers.py` |  |
| `probe_weapon_1013_10_owner.py` | 在装备总表里按「模型路径含 1013_10」或「名字含 菌焰/幻海」反查武器条目。 |
| `probe_weapon_skin_id.py` | 查某个 weapon_skin 行 ID 在所有相关表里的线索。 |
| `project_audit.py` | 项目自查：板块数据完整性 / 索引一致性 / 资源引用 / 发布策略覆盖。 |
| `provenance_standard.py` | Upgrade LifeAfter board provenance to the strict dual-source v2 contract. |
| `prune_unused_boards.py` | 删除未被 taxonomy 引用的板块文件（先核其它引用，有引用则保留）。 |
| `publication_policy.py` | Explicit publication gate for LifeAfter Wiki boards. |
| `purge_archived_toggle.py` | 彻底清掉 wiki.html 里 showArchived（已归档旧板）相关代码分支。 |
| `purge_retired_boards.py` | 清理已归档旧板：把 retired 状态的板块从站点移除（文件归档到 _备份归档，policy/导航清引用）。 |
| `push_pe_packs_to_device.py` | 把 182 个 PE gpk 断点式推回模拟器（只推尺寸不符的）。 |
| `query_fashion_identity.py` | Query the P4-3 fashion identity locator without implicit joins. |
| `query_id.py` | P1-13 查询 CLI：任意数字 ID → 所有出现位置。 |
| `query_id_locator.py` | P1-9 查询 CLI：任意标识 → 出现位置。 |
| `query_item_identity.py` | Query ITEM_IDENTITY_LOCATOR with unresolved data isolated by default. |
| `query_item_master_v01.py` | Query the published-only ITEM_MASTER v0.1 SQLite view. |
| `query_name_locator.py` | NAME_LOCATOR SQLite 查询器。 |
| `query_table.py` | P1-10 查询 CLI：table_index 查询。 |
| `read_large_npk.py` | 用工具库的 npk_reader 读**大容器**（res.npk / res.gpk）的目录，回答两个问题： |
| `rebuild_1110188_audio.py` | 重建 1110188（一魂共鸣）的音效分组：射击 / 换弹 / 切枪 / 语音。 |
| `rebuild_chenshi_slots.py` | rebuild_chenshi_slots.py ——（三）宸世臻藏子卡（四、奖池区） |
| `rebuild_chip_board_v3.py` | 重建「限定芯片」期次与成员（按 huodong 活动一行一期）。 |
| `rebuild_chip_board_v4.py` | 重建「限定芯片」期次与成员（schema 解码版）。 |
| `rebuild_chip_catalog.py` | rebuild_chip_catalog.py — 芯片图鉴板：chip_type 池 65 名全集（游戏图鉴同源） |
| `rebuild_chip_lottery.py` | 重建「限定芯片」奖池：按 special_chip_lottery_hd_conf_data(kj1) 每期取芯片 id。 |
| `rebuild_chip_lottery_board.py` | 用 conf 表重建「限定芯片」并写回奖池板（替换旧错配）。 |
| `rebuild_chip_timeline.py` | 重建限定芯片的 37 期时间线（来自 huodong_conf），保留已确认的芯片锚点。 |
| `rebuild_common_item_text_sources.py` | Build a replayable same-snapshot common_item text source board. |
| `rebuild_edible.py` | 从 PE 源直接重建「料理与食谱」板（食材 + 可烹饪），不依赖旧 board。 |
| `rebuild_fashion_bag_slots.py` | rebuild_fashion_bag_slots — 时装外观附件（背包）独立板导出器 |
| `rebuild_fashion_bestplay_slots.py` | rebuild_fashion_bestplay_slots — 本场最佳动画 & 击败播报（衣柜-社交类目） |
| `rebuild_fashion_face_slots.py` | rebuild_fashion_face_slots — 面饰/挂饰 face 槽行级槽位复证导出器（②b 交付） |
| `rebuild_fashion_glow_slots.py` | rebuild_fashion_glow_slots — 荧光棒板（player_appear_data 荧光棒名册） |
| `rebuild_fashion_projection_slots.py` | rebuild_fashion_projection_slots — 伴身投影（投影格）定位链板导出器 |
| `rebuild_fashion_wardrobe_full.py` | 全量重建 fashion_wardrobe（时装衣柜）—— 不靠旧板合并，从 fashion_data 表逐行解。 |
| `rebuild_fashion_wardrobe_slots.py` | Rebuild the fashion wardrobe board with row-level CHS-slot provenance. |
| `rebuild_future_lottery_preview.py` | Preview board: future-dated lottery activities in the BA8 snapshot. |
| `rebuild_gift_data_text_sources.py` | Build a replayable same-snapshot gift-data text source board. |
| `rebuild_illustration.py` | 图鉴收集总表重建：食物 + 特殊能力。 |
| `rebuild_item_master_from_v03.py` | 从 ITEM_MASTER_v03.jsonl 还原道具总表板（item_id / name / provenance）。 |
| `rebuild_item_master_icons.py` | 道具总表 item_master_v01（1189 条）补齐图标 —— 同表 icon 字段 → PE .ktx / PC .bc7 双源定位 → PNG。 |
| `rebuild_item_master_v02.py` | P4-A2 — ITEM_MASTER v0.2：把 common_item_data_base 七个 schema 的 27,753 候选批量升级/定档。 |
| `rebuild_item_master_v03.py` | P4-A3 — ITEM_MASTER v0.3：统一业务物品索引（common_item / belt_chip / gift_data）。 |
| `rebuild_kaijia_panel_static.py` | Rebuild the Armor Reappearance (phase 2) board with classic/simple branches. |
| `rebuild_lottery_periods.py` | 重建「奖池板块」看板：期次 → 奖池 → 成员（玩家视图）。 |
| `rebuild_lottery_pool_resolved_board.py` | Adapt frozen LOTTERY_POOL_RESOLVED v0.1 artifacts into a Wiki board. |
| `rebuild_lottery_research_panels.py` | Nucleus research (限定核芯研制) and chip guarantee (限定芯片保底) structure boards. |
| `rebuild_manjian_panel_static.py` | Manjian market (满减) board — activity periods + Linglong anchor chain. |
| `rebuild_multioptional_periods.py` | 重建「自选保底奖池」期次：同一个活动可能返场多次，一次活动 = 一个期次。 |
| `rebuild_mystery_shop_panel_static.py` | Mystery shop (神秘商店 / RandomDiscountHD) board. |
| `rebuild_nucleus_cards.py` | rebuild_nucleus_cards — 核芯卡（名册+特技+星级段，web 预览 v1） |
| `rebuild_nucleus_cards_classic.py` | rebuild_nucleus_cards_classic — 核芯卡合并版（双服：经典服 12 星主体 + 简单生存服独有） |
| `rebuild_nucleus_entry_slots.py` | rebuild_nucleus_entry_slots — 核芯词条板（nucleus_entry_data 87 条，含数值区间） |
| `rebuild_nucleus_item_catalog.py` | rebuild_nucleus_item_catalog — 异变核芯名册板（common_item 660000 段） |
| `rebuild_projection_rows.py` | 重建时装板的「投影」条目：正确数据源是 body_sfx_data（43 行，buff_item_id 640xxx）。 |
| `rebuild_skin_behavior_preview.py` | Preview board: weapon skins whose only presence is BA8 behavior resources. |
| `rebuild_weapon_attrs_schema_static.py` | Rebuild anonymous all_equips -> schema6109 attribute relations from BA8. |
| `rebuild_weapon_skin_catalog_current.py` | Rebuild the current BA8 weapon-skin catalog with verified official item names. |
| `rebuild_weapon_skin_media.py` | Build the browser-readable weapon-skin 3D index from viewer.json files. |
| `rebuild_weapon_skin_resolved_v01.py` | WEAPON_SKIN_RESOLVED_v0.1 — 只发布已成立的字段与关系。 |
| `rebuild_weapon_skin_sfx_text_sources.py` | Compatibility entrypoint for the current full weapon-skin catalog. |
| `rebuild_weapon_skin_static_candidates_board.py` | Publish existing weapon-skin rows as unresolved static candidates. |
| `rebuild_weapon_skin_v02.py` | WEAPON_SKIN_RESOLVED v0.2 —— 从 canonical payload 重建（去 legacy board 依赖）。 |
| `rebuild_wiki_v01.py` | Build the honest, frozen-source LifeAfter Wiki v0.1 boards. |
| `reclassify_fashion_parts.py` | 时装部位重定：以 desc 里的「 - 衣服（ / - 头饰（ / - 光源（」为准，不信 new_fashion_id_str。 |
| `reclassify_lottery_families.py` | 奖池板统一整理：按 huodong_conf 的 hd_class 重新归族 + 同名活动合并 + 期内去重。 |
| `reclassify_vehicle_class.py` | 载具分类改为按 vehicle_equip_type 码分（用户 2026-10-24 口径）。 |
| `reclassify_vehicle_class_v2.py` | 载具分类改为真表口径： |
| `record_regression.py` | 记录一次**真实**回归结果到 state/REGRESSION.json（不伪造任何数字）。 |
| `refetch_broken_cards.py` | 重取 28 条可疑名片框（1292×812 旧产物）：多扩展名/多后缀尝试。 |
| `refresh_fashion_wardrobe_live.py` | 全量时装衣柜（fashion_wardrobe）—— 用**当前树里的 fashion_data 表**重读刷新字段。 |
| `refresh_lottery_board.py` | 奖池板归一管线（幂等）：补图脚本按旧快照写回后，用它把后面的修正全部重放。 |
| `refresh_sidecars.py` | refresh_sidecars.py — 给主页生成「重活」sidecar。 |
| `register_board.py` | 把新板块登记进发布策略与首页体系树（幂等）。 |
| `register_mutation_core_full.py` | 把 mutation_core_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。 |
| `register_vehicle_full.py` | 把 vehicle_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。 |
| `regroup_1110189_audio.py` | 1110189：把音效分成「本体音 / 通用开火 / 通用补充」，并去掉与 lp1 完全相同的 lp2。 |
| `render_bonus_test.py` | 生成「加成-伤害」实测反推工具：填数据 → 自动判线性/找拐点。 |
| `render_compress_curves.py` | 把 attr_compress_curves.json 画成折线图 HTML（纯 SVG，无外链）。 |
| `render_damage_formula.py` | 生成「伤害公式」页面（反编译结论 + 证据行号 + 参数结构）。 |
| `render_namecard_frames.py` | 名片框 Spine 批量出图：解包三件套 → spine_view.html 渲染 → 裁切 PNG。 |
| `render_pvp_calc.py` | 生成 PvP 伤害倍率计算器（公式来自 HurtCalc 反编译）。 |
| `render_pvp_chain.py` | 生成 PvP 伤害链页面（属性表 + 结算链 + 压缩语义）。 |
| `render_scene_balance.py` | 【已废弃 2026-10-25】场景加成平衡统一走板块页 board.html?b=scene_balance。 |
| `render_scene_table.py` | 完整场景表页（98 条，含未收录）+ CSV。 |
| `render_scene_table_v2.py` | 场景加成上下限总表 v2：重点模块置顶 + 同名同值合并一行。 |
| `render_scene_table_v3.py` | 场景平衡表 v3：直接表格（带搜索 / 类型筛选），重点模块置顶，同名同值合并。 |
| `render_spine_index.py` | 生成 Spine 三件套预览页（离线可看：贴图页 + 骨架信息）。 |
| `repair_fashion_by_model_sample.py` | 按「同 model + 同部位」的正确图样本，修复错部位/缺性别的时装卡。 |
| `repair_fashion_posters.py` | 修时装板「男女角色取图不完整」：卡面引用的 png 已经不在磁盘上（断链）。 |
| `repair_reborn_vis.py` | 补「隐藏半感染者花苞」（reborn_vis）。 |
| `report_fashion_male.py` | 统计时装男图覆盖：已补 / 仍缺，并导出清单。 |
| `report_missing_male_detail.py` | 列出仍缺男图的卡（含现有图 base、model、部位），并写清单文件。 |
| `report_skin_audio_gap.py` | 生成武器皮肤音效缺口清单（真名/资源/音频三级状态）。 |
| `restore_fashion_charm_filters.py` | 恢复人物时装的魅力值与筛选（fashion_wardrobe 重建后 meta.filters/字段丢失）。 |
| `restore_fashion_charm_filters_v2.py` | 恢复人物时装的魅力值 / 性别 / 筛选轴（fashion_wardrobe 重建后这些字段丢失）。 |
| `reuse_same_model_images.py` | 同 model + 同部位 的卡之间复用已导出的图（参照款 → 缺图款）。 |
| `rewrite_wiki_A.py` | 按方案 A（档案馆）重写 wiki 首页：左导航 + 筛选条 + 密集卡片网格。 |
| `run_checks.py` | 跑三线台账的【慢判据】，结果落盘供主页读缓存。 |
| `scan_classic_weapon_cfg.py` | 经典服武器配置批量解码 + 定向检索（不把全量数据打进对话）。 |
| `scan_client_file_map.py` | 只读客户端文件地图采集器：枚举 mrzh / LifeAfter 全部文件（元数据 + 定向 SHA）。 |
| `scan_client_for_audio.py` | 找音频：在客户端容器里扫音频签名（不依赖任何音频解码器）。 |
| `scan_fev_events.py` | 扫 gpk 里的 FEV1 容器，打印偏移/长度与可打印字符串（找事件名与样本名同现）。 |
| `scan_fpk_ids.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_shuijin.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_sky1003.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_tujian.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_yuese.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fsb_names_in_pack.py` | 在指定 gpk 里扫 FSB5 bank，列出样本名；用于把「音效真名」落到具体 bank。 |
| `scan_local_wav_for_gap.py` | 在已落盘的音频资产里，按真名找工作区里已有但未挂到卡上的 WAV。 |
| `scan_names_for_show_rewards.py` | 全表扫：给定 id 列表，在所有 base+_chs 成对的 cdata 表里找同名行，回填名字。 |
| `scan_packs_for_name.py` | 在 182 个 PE 包里按名字直扫（绕过索引），确认某个 icon 到底在不在包里。 |
| `scan_packs_for_skin_assets.py` | 宽扫资源包：找**任何**与皮肤相关的图片路径（不限于脚本表引用）。 |
| `scan_scene_names.py` | 暴力扫全部 cdata 表：找行键命中 scene/类型 id 且带中文名字的表。 |
| `scan_sky1003_fpk.py` | 倒序扫描 049..037.fpk 的解压帧，定位 sky1003 皮肤资源。 |
| `scan_sky1003_fpk_064_050.py` | 倒序扫描 064..050.fpk，命中 sky1003 后停止并提取邻近 DDS/FSB5。 |
| `scan_table_family.py` | scan_table_family.py v2 —— 表族通道侦察器（BA8 工作副本） |
| `scan_tables_for_1110189.py` | 在经典服 cdata 全表里找 key 或值等于 1110189 的行（含 oversea 关键词表）。 |
| `scan_tables_for_skin_id.py` | 在可解码的 cdata 表里全表搜某个 skin id / 模型关键字，找 1110189 的更多线索。 |
| `scan_weapon_skin_ui_assets.py` | 扫描当前客户端包：找出**武器皮肤图鉴/UI 真正引用的图片资源路径**。 |
| `search_decompressed.py` | 在**解压后**的条目数据里搜目标皮肤（而不是容器原始字节）。 |
| `segment_scout.py` | segment_scout.py —— id 段侦察器：名册段 dump / jump 组引用收集 / 缺口对照 |
| `set_scene_type_by_tag.py` | 场景类型改为「只认可靠标志」：space_data.map_tag==4 → PvP，其余 PvE；无场景号则标未匹配。 |
| `set_scene_type_five.py` | 场景类型按 space_data.map_tag 分五档（不掺名字白名单）。 |
| `show_official_effect_names.py` | 武器皮肤卡：战斗表现优先显示游戏内正式名（weapon_skin_effect_show_data）， |
| `simplify_wiki_sidebar.py` | wiki 首页：删掉「显示已归档旧板」入口；状态行只留公开数。 |
| `slim_media.py` | 非时装板块：每个条目只保留一张最清晰的 2D 图（像素面积优先，其次 _b>标准>_s，再按文件大小）。 |
| `slim_media2.py` | 非时装板块：同一 kind/label 的 2D 图只保留最清晰的一张（像素面积 > 后缀档位 > 文件大小）。 |
| `source_presence.py` | Pure dual-source presence comparison; never merges source records. |
| `spine_fetch.py` | Spine 资源原始抓取（atlas / json / 贴图页）。 |
| `spine_probe.py` | CDP 探针：打开页面 → 抓 console/异常 → 执行 JS → 截图。 |
| `spine_render.py` | Spine 2.1 精简渲染器（region 附件）→ GIF。 |
| `split_appearance_extra.py` | 「其他外观」按用户口径重分七类，并把头饰/衣服/背包/挂饰合并进人物时装。 |
| `split_part_cards.py` | 把「同套多部位」合并卡拆回按部位的单卡（头饰一张、衣服一张）。 |
| `split_scene_by_server.py` | 场景平衡：按服型拆行，让「服型 / 来源类型」下拉筛选真正可用。 |
| `stage_namecard_pages.py` | 名片框 spine 贴图页补件：atlas 里列出的 page 若 spine_live 缺失， |
| `stage_namecard_pages_fast.py` | 名片框 spine 贴图页补件（快版）：只扫 还原树 里 */spine*/ 目录建文件名索引， |
| `stamp_board_contract.py` | stamp_board_contract.py — 为已发布板补齐 v3 机读定位链（不改任何数据声明）。 |
| `supplement_fashion_parts.py` | 用 player_appear_data 补齐时装板缺失的部位（如 不湮之花-头饰）。 |
| `sync_appearance_taxonomy.py` | taxonomy / publication_policy / board_builders 同步：去掉（六）其他外观，加捏脸·戒指·花苞。 |
| `sync_manifest_categories.py` | manifest 的分类路径按 taxonomy 重算（taxonomy 是唯一口径）。 |
| `sync_manifest_counts.py` | 同步 manifest 里各板块的条目数与分类（以 data/boards/*.json 实际内容为准）。 |
| `test_export_exchange_static_candidates.py` | 当前 Documents 静态商店候选总表的回归测试。 |
| `tidy_scene_cards.py` | 场景平衡卡面收口：把工程数组换成人类可读文本，并把这些键从卡面隐藏。 |
| `tidy_workspace.py` | 整理工作区：把散落的 .bak 备份收进 _备份归档/<日期>/，并生成 tools/INDEX.md。 |
| `trace_kaijia_formal_reward_chain.py` | Trace formal-client Kaijia lottery reward records from raw BinDict bytes. |
| `trace_placeholder_ids.py` | 查奖池里「道具 <id>」占位名到底来自哪张表、为什么没回填。 |
| `translate_skin_sfx_names.py` | 把武器皮肤音效的内部真名翻译成中文短标签（内部名保留，中文并列展示）。 |
| `tune_brand_assets.py` | 微调品牌图：横幅更明显、侧栏海报更清楚。 |
| `verify_fid_in_packs.py` | 绕过索引，直接扫 182 个包内的 entry.fid，验证某路径到底在不在包里。 |
| `verify_field_semantics.py` | P2-2：字段语义可信度验证（逐 (table, schema_ref, slot) 统计判据）。 |
| `verify_media_refs.py` | 收尾核验：两板 _media.images 引用的 png 是否真实存在；统计改后数字。 |
| `wiki_restructure.py` | 整理结构 + 换 hero 图（随机传世/典藏）+ 头像板改名。 |
| `wiki_restructure_fix.py` | 修正上一步：PvP 挪进战力类 + 中文序号（十一/十二/十三）。 |
| `wiki_server.py` | 127.0.0.1-only server for the LifeAfter Wiki and lazy script NPK inspection. |
| `wiki_structure_check.py` | wiki 结构体检：板块是否都被导航覆盖、编号是否连续、有无孤儿节点。 |
| `wiki_tidy.py` | 整理 wiki：清掉失效导航、隐藏两份重复/未解析板、修 三、活动类 编号。 |
| `wire_avatar_icons.py` | 把 assets/avatar_icons/<item_id>.png 挂到名片框板卡面（有图才挂）。 |
| `wire_nucleus_icons.py` | 给 nucleus 板每条接图标：icon_path → PE 定位 → 导出 PNG → 写 _media。 |
| `write_fashion_rules.py` | 把时装补图/去重/单性别的规则沉淀进板级技术详情（meta.notes）。 |
| `xref_all_arm64.py` | ARM64 全面 xref 扫描：ADRP(+ADD/LDR) 与 ADR，目标为给定字符串地址。 |
