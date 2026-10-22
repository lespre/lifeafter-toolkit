# tools 索引（自动生成）

共 199 个脚本；日常入口统一走 `python E:/la拆包项目/la.py`。

| 脚本 | 说明 |
|---|---|
| `__init__.py` | Workbench 工具包（可 python -m tools.<tool> 调用）。 |
| `_cmp_decoder_20260921.py` | 找 pool/xbody 的提供者 |
| `_probe_huodong2_20260921.py` |  |
| `_probe_huodong3_20260921.py` |  |
| `_probe_huodong4_20260921.py` |  |
| `_probe_huodong_20260921.py` |  |
| `_probe_ice_drone_20260921.py` |  |
| `_probe_nucleus2_20260921.py` | 660000 段核芯 + 名称含"核芯" |
| `_probe_nucleus3_20260921.py` |  |
| `_probe_nucleus_20260921.py` |  |
| `add_weapon_skin_status_v02.py` | 武器皮肤 canonical 状态字段 v0.2（listing_status / name_status）。 |
| `aggregate_skin_audio.py` | 把提取到的音频 bank 样本按**武器皮肤**归类，产出 Wiki 用的音频清单。 |
| `analyze_client_file_map.py` | 客户端文件地图分析器：分类统计 / 差异对比 / 候选清单 / Markdown 报告。 |
| `announce_calibrate.py` | announce_calibrate.py —— 官方更新公告校准源抓取（mrzh.163.com） |
| `apply_weapon_skin_hotfix_overlay.py` | 把「PC 测试服热更覆盖记录」合并进武器皮肤图鉴板（data/boards/weapon_skin_sfx_text_sources.json）。 |
| `apply_wiki_theme.py` | 给 wiki 主页换上《明日之后》主题皮肤：暗色金属 + 锈橙警示色。 |
| `apply_wiki_theme_v2.py` | 主题 v2：卡片加宽 + 装甲细节 + 顶部档案标识。追加在 style 末尾，覆盖 v1。 |
| `apply_wiki_theme_v3.py` | 主题 v3：顶部军械库剪影 + 修掉一级项的小圆点 + 卡片排版微调。 |
| `apply_wiki_theme_v4.py` | 主题 v4：去掉重复箭头、把军械库剪影挪到顶栏下方并提亮。 |
| `attach_skin_posters.py` | 把 assets/skin_posters/<skin_id>.png 挂到武器皮肤媒体库里（用户提供的官方/实机图）。 |
| `attach_skin_shots.py` | 把**实机截图**按皮肤 ID 归档，并生成 Wiki 用的图片清单。 |
| `audit_common_item_dual_source.py` | Create an unpublished, source-preserving common_item dual-source audit. |
| `audit_common_item_family.py` | Static set-level audit of the BA8 common_item split table family. |
| `audit_common_item_split_shell.py` | Read-only literal audit of the common_item split-table loader shell (BA8). |
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
| `audit_name_chain.py` | Mechanical audit for NAME_CHAIN_CANDIDATES.jsonl and NAME_LOCATOR.db. |
| `audit_weapon_skin_optional.py` | 武器皮肤「可选残差」定界侦查（对任意 snapshot 基准可复跑）。 |
| `bindict_provenance.py` | Read-only BinDict decoding with replayable CHS slot provenance. |
| `build_fashion_identity_candidates.py` | P4-3 fashion identity candidate rules. |
| `build_fashion_identity_locator.py` | Build the P4-3 fashion identity SQLite locator. |
| `build_field_names.py` | P2-1：字段名绑定（table + schema_ref + field_slot → 真实字段名）。 |
| `build_fpk_index.py` | 建立**武器皮肤图像定位链**的地基：全 fpk 帧级资源索引（一趟建好，永久复用）。 |
| `build_id_locator.py` | P1-9：标识 → 出现位置 定位索引构建器（基于 file_index_entries.jsonl）。 |
| `build_id_occurrence.py` | P1-13：数字 ID 出现位置索引（复用 P1-12 row_index 定位与解码器行语义）。 |
| `build_item_identity_candidates.py` | P4-2 item/equipment identity candidate rules and builders. |
| `build_item_identity_locator.py` | Build the P4-2 item/equipment identity SQLite locator. |
| `build_item_master_v01.py` | Build P4-A3 ITEM_MASTER v0.1 from frozen P4-1/P4-2/P4-A1 evidence. |
| `build_locator_chains.py` | 生成 canonical Locator Chain 层（v1.4 Phase 1）。 |
| `build_lottery_pool_resolved_v01.py` | Build LOTTERY_POOL_RESOLVED v0.1 from source-locked BinDict tables. |
| `build_name_chain_candidates.py` | Build replayable name-chain candidate and audit records. |
| `build_name_locator.py` | 构建 NAME_CHAIN_CANDIDATES.jsonl 的 SQLite 名称定位库。 |
| `build_reliable_sources.py` | P3：可靠数据源筛选 v2 —— 源状态=类别关键槽聚合。 |
| `build_row_index.py` | P1-12：行级定位索引（test BA8 快照，全表数据体）。 |
| `build_skin_assets.py` | 给**一个武器皮肤**构建完整素材（音效 + 图片）—— 单包作业，不搞全盘扫描。 |
| `build_source_registry.py` | 统一 source registry 构建器（P0-6/7 收尾）。 |
| `build_table_families.py` | P1-11：表族成员关系正式固化（family members 结构关系，无运行时推断）。 |
| `build_table_index.py` | P1-10：table_index 构建器 —— 从 BA8 全量条目找"配置表"（纯定位，无字段语义）。 |
| `build_table_inventory_for_basis.py` | A2：为**指定工作副本**建基线内的表清单（table inventory，含 FID）。 |
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
| `calibrate_business_chains.py` | calibrate_business_chains.py —— 业务定位链双服双版本校准器（2026-09-06 用户定版铁律） |
| `carve_fsb5_banks.py` | gres 包 → FSB5 bank → WAV（终版：先按条目解包，再在解出文件里开凿）。 |
| `cdp_probe.py` | CDP 探针：打印页面元素布局与计算样式，排查栅格宽度。 |
| `cdp_shot_local.py` | CDP 截图：打开页面 → 执行 JS（可选）→ 截图。用于本地主题验收。 |
| `checks.py` | 三线台账「可核判据」注册表（台账里写 @名字 引用这里）。 |
| `crack_mesh_layout.py` | 破解 .mesh 顶点布局：用【尺度无关的包围盒比值判据】穷举候选布局。 |
| `decode_probe.py` | decode_probe.py —— 解码探针：单表第一眼（表型指纹 + 行级解码 + 字段错位警示） |
| `export_exchange_static_candidates.py` | 导出 Documents common_exchange_shop_data 的全量静态格子总表。 |
| `export_fashion_face.py` | 人物·面饰/挂饰板块。 |
| `export_fashion_kaijia.py` | 铠甲勇士联动·人物外观专题（BA 快照，经 lib_fashion 统一解码 + 面饰专池补充）。 |
| `export_fashion_wardrobe.py` | 全量时装衣柜板块（人物类）——★ 权威源换成【表结构解析的行】。 |
| `export_fpk_textures.py` | 从 fpk 主资源包导出贴图（含图集切片）——2026-09-13 定稿版。 |
| `export_kaijia_phase2.py` | 二期「铠甲再临(刑天飞影)」奖池板块 —— 已实装版（2026-09-01 快照 BA8A239A）。 |
| `export_lottery.py` | 导出板块：限时主题抽奖奖池（已上线帝皇 = verified；未上线铠甲再临 = candidate/structure） |
| `export_poster.py` | 从当前查看器同一次运行导出海报（P2）。 |
| `export_vehicle_catalog.py` | 载具模型清单板块（图鉴类-载具）。 |
| `extract_asset_path_dictionary.py` | 从脚本包抽**全量资源路径字典**（路线 C：依赖图传播命名）。 |
| `extract_gres_audio_banks.py` | 扫全部 gres 包，抽出其中的 FSB5 音频 bank → WAV（样本名取自 bank）。 |
| `extract_kaijia_formal_tables.py` | Extract only the formal-client tables needed for the Kaijia lottery trace. |
| `extract_ui_assets.py` | 按**UI 声明的路径**从资源包里挖图片（不用名字猜纹理）。 |
| `fill_board_provenance.py` | 补齐时装板里缺的可机读定位链（publication gate 要求 5 个 provenance 字段）。 |
| `find_gim_by_bounds.py` | 按「已知边界体的 float32 字节」在 model_*.gpk 里定位 .gim 模型本体。 |
| `find_skin_audio_banks.py` | 定位并提取**武器皮肤音频**：在 gpk/npk 里裸搜 FSB5 bank + 皮肤音效名。 |
| `fix_bucket_pendants.py` | 修正时装板的部位归类： |
| `fix_legacy_provenance.py` | 给仍在发布的旧板补 provenance（发布门禁要求的 5 个字段），来源用板自带的 package_sha。 |
| `fix_rebuild_paths.py` | 修 rebuild_wiki_v01.py 里 "str" / "str" 的路径拼接（会 TypeError）。 |
| `fix_wiki_grid.py` | 修正 wiki 渲染：每个大类一个瓦片网格（原来每个叶子节点各一格，导致一列一个）。 |
| `fix_wiki_polish.py` | wiki 修尾：标题中文化、时装缩略图、两行标题、路径去编号。 |
| `gen_home.py` | 生成站点主页 index.html —— LifeAfter 拆包项目 · 左侧信息块 + 右侧三线三带。 |
| `img_kind.py` | 图片按**内容**判「是不是素材底图」—— 给 wiki 用的小封装。 |
| `import_pendants.py` | 把真正的「挂饰」（gift_data 中 icon_270xxx 的 28 条礼盒）配图并进人物时装板。 |
| `import_pendants_full.py` | 挂饰全量：all_equips_data(oversea kj1) 里 id 270xxx 段 = 挂饰本体（124 件）。 |
| `index_all_npk.py` | P1-8 Stage 3a：registry 全部 npk（script+资源）条目级索引。 |
| `index_fpk.py` | P1-8 Stage 3b-2：FPK 条目（zstd 帧）索引 —— 多进程按包并行版。 |
| `index_gpk.py` | P1-8 Stage 3b-1：GPK 条目索引（FPGH v2，与 NPK/WPK 解析链完全独立）。 |
| `index_script_packages.py` | P1-8a：script 家族 11 包条目级索引（目录表级，不解 payload）。 |
| `index_wpk_idx.py` | P1-8 Stage 3b-3：WPK/IDX 盘点与索引 —— 独立于 GPK/FPK/NPK 链。 |
| `lib_fashion.py` | 时装外观表可复用加载器（数据源映射路径：fashion_data base + CHS -> 结构化行）。 |
| `live_npk_reader.py` | LifeAfter script NPK lazy reader for the local Wiki. |
| `locate_all_equips_pair.py` | all_equips base/CHS 自定位解析器（FID 内容派生、随热更漂移时的兜底）。 |
| `merge_fashion_media_into_board.py` | 把时装图标（游戏内真实引用）缝进「全量时装衣柜」总表。 |
| `merge_file_index.py` | P1-8 Stage 4：统一 file_index 合并器（由各格式 summary 驱动）。 |
| `normalize_provenance.py` | 把已发布板块的 provenance 规范化成发布契约能过的最小完备形态。 |
| `parse_c159.py` | 解析 .c159 文档（明日之后 NeoX 资源描述符）为可读 JSON。 |
| `parse_chenshi_periods.py` | 把公告宸世段（announce_chenshi.json）按首日期对齐 optional_version_data 期次，更新 rebuild 脚本的期次内容层 |
| `parse_file_hash_pack.py` | P1-8 Stage 1：file_hash_pack.bin（FHPK v2）解析与评估。 |
| `patch_skin_grade_1110189.py` | 改标：把「传世 + 周年庆」从 1110188（一魂共鸣）撤掉，标到 1110189（喷火器，行为预告行）。 |
| `patch_skin_grade_chuanshi.py` | 把 1110188 一魂共鸣的品级标成「传世（6）」+ 周年庆，并保留原始表值以便追溯。 |
| `patch_skin_names_20261017.py` | 把本批武器的**验证名 + 真值字段**写进看板  weapon_skin_sfx_text_sources。 |
| `patch_skin_names_note.py` | 收尾：把看板里「星魂追光只是候选名」的旧叙述改成「已由道具行正式名取代」。 |
| `patch_skin_names_stats.py` | 按 items 现状重算名字相关统计（stats + meta.notes 里的计数），避免页面数字和卡片打架。 |
| `preview_board_contract.py` | Frozen-artifact (publication contract v3) provenance for preview sub-cards. |
| `probe_files_db.py` | 看 lifeafter_files.sqlite3 能不能给出「表文件 → npk entry_index + file_id」。 |
| `probe_table_entry.py` | 用 fid = fid_of(表路径) 在 entries 里查 entry_index + file_id（容器可能是 script npk）。 |
| `probe_untyped_containers.py` |  |
| `project_audit.py` | 项目自查：板块数据完整性 / 索引一致性 / 资源引用 / 发布策略覆盖。 |
| `provenance_standard.py` | Upgrade LifeAfter board provenance to the strict dual-source v2 contract. |
| `publication_policy.py` | Explicit publication gate for LifeAfter Wiki boards. |
| `query_fashion_identity.py` | Query the P4-3 fashion identity locator without implicit joins. |
| `query_id.py` | P1-13 查询 CLI：任意数字 ID → 所有出现位置。 |
| `query_id_locator.py` | P1-9 查询 CLI：任意标识 → 出现位置。 |
| `query_item_identity.py` | Query ITEM_IDENTITY_LOCATOR with unresolved data isolated by default. |
| `query_item_master_v01.py` | Query the published-only ITEM_MASTER v0.1 SQLite view. |
| `query_name_locator.py` | NAME_LOCATOR SQLite 查询器。 |
| `query_table.py` | P1-10 查询 CLI：table_index 查询。 |
| `read_large_npk.py` | 用工具库的 npk_reader 读**大容器**（res.npk / res.gpk）的目录，回答两个问题： |
| `rebuild_chenshi_slots.py` | rebuild_chenshi_slots.py ——（三）宸世臻藏子卡（四、奖池区） |
| `rebuild_chip_catalog.py` | rebuild_chip_catalog.py — 芯片图鉴板：chip_type 池 65 名全集（游戏图鉴同源） |
| `rebuild_common_item_text_sources.py` | Build a replayable same-snapshot common_item text source board. |
| `rebuild_fashion_bag_slots.py` | rebuild_fashion_bag_slots — 时装外观附件（背包）独立板导出器 |
| `rebuild_fashion_bestplay_slots.py` | rebuild_fashion_bestplay_slots — 本场最佳动画 & 击败播报（衣柜-社交类目） |
| `rebuild_fashion_face_slots.py` | rebuild_fashion_face_slots — 面饰/挂饰 face 槽行级槽位复证导出器（②b 交付） |
| `rebuild_fashion_glow_slots.py` | rebuild_fashion_glow_slots — 荧光棒板（player_appear_data 荧光棒名册） |
| `rebuild_fashion_projection_slots.py` | rebuild_fashion_projection_slots — 伴身投影（投影格）定位链板导出器 |
| `rebuild_fashion_wardrobe_slots.py` | Rebuild the fashion wardrobe board with row-level CHS-slot provenance. |
| `rebuild_future_lottery_preview.py` | Preview board: future-dated lottery activities in the BA8 snapshot. |
| `rebuild_gift_data_text_sources.py` | Build a replayable same-snapshot gift-data text source board. |
| `rebuild_item_master_board.py` | Adapt frozen ITEM_MASTER v0.1 artifacts into a Wiki board. |
| `rebuild_item_master_v02.py` | P4-A2 — ITEM_MASTER v0.2：把 common_item_data_base 七个 schema 的 27,753 候选批量升级/定档。 |
| `rebuild_item_master_v03.py` | P4-A3 — ITEM_MASTER v0.3：统一业务物品索引（common_item / belt_chip / gift_data）。 |
| `rebuild_kaijia_panel_static.py` | Rebuild the Armor Reappearance (phase 2) board with classic/simple branches. |
| `rebuild_lottery_pool_resolved_board.py` | Adapt frozen LOTTERY_POOL_RESOLVED v0.1 artifacts into a Wiki board. |
| `rebuild_lottery_research_panels.py` | Nucleus research (限定核芯研制) and chip guarantee (限定芯片保底) structure boards. |
| `rebuild_manjian_panel_static.py` | Manjian market (满减) board — activity periods + Linglong anchor chain. |
| `rebuild_mystery_shop_panel_static.py` | Mystery shop (神秘商店 / RandomDiscountHD) board. |
| `rebuild_nucleus_cards.py` | rebuild_nucleus_cards — 核芯卡（名册+特技+星级段，web 预览 v1） |
| `rebuild_nucleus_cards_classic.py` | rebuild_nucleus_cards_classic — 核芯卡合并版（双服：经典服 12 星主体 + 简单生存服独有） |
| `rebuild_nucleus_entry_slots.py` | rebuild_nucleus_entry_slots — 核芯词条板（nucleus_entry_data 87 条，含数值区间） |
| `rebuild_nucleus_item_catalog.py` | rebuild_nucleus_item_catalog — 异变核芯名册板（common_item 660000 段） |
| `rebuild_skin_behavior_preview.py` | Preview board: weapon skins whose only presence is BA8 behavior resources. |
| `rebuild_weapon_attrs_schema_static.py` | Rebuild anonymous all_equips -> schema6109 attribute relations from BA8. |
| `rebuild_weapon_skin_catalog_current.py` | Rebuild the current BA8 weapon-skin catalog with verified official item names. |
| `rebuild_weapon_skin_media.py` | Build the browser-readable weapon-skin 3D index from viewer.json files. |
| `rebuild_weapon_skin_resolved_v01.py` | WEAPON_SKIN_RESOLVED_v0.1 — 只发布已成立的字段与关系。 |
| `rebuild_weapon_skin_sfx_text_sources.py` | Compatibility entrypoint for the current full weapon-skin catalog. |
| `rebuild_weapon_skin_static_candidates_board.py` | Publish existing weapon-skin rows as unresolved static candidates. |
| `rebuild_weapon_skin_v02.py` | WEAPON_SKIN_RESOLVED v0.2 —— 从 canonical payload 重建（去 legacy board 依赖）。 |
| `rebuild_wiki_v01.py` | Build the honest, frozen-source LifeAfter Wiki v0.1 boards. |
| `record_regression.py` | 记录一次**真实**回归结果到 state/REGRESSION.json（不伪造任何数字）。 |
| `refresh_fashion_wardrobe_live.py` | 全量时装衣柜（fashion_wardrobe）—— 用**当前树里的 fashion_data 表**重读刷新字段。 |
| `refresh_sidecars.py` | refresh_sidecars.py — 给主页生成「重活」sidecar。 |
| `register_mutation_core_full.py` | 把 mutation_core_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。 |
| `register_vehicle_full.py` | 把 vehicle_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。 |
| `run_checks.py` | 跑三线台账的【慢判据】，结果落盘供主页读缓存。 |
| `scan_client_file_map.py` | 只读客户端文件地图采集器：枚举 mrzh / LifeAfter 全部文件（元数据 + 定向 SHA）。 |
| `scan_client_for_audio.py` | 找音频：在客户端容器里扫音频签名（不依赖任何音频解码器）。 |
| `scan_fpk_ids.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_shuijin.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_sky1003.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_tujian.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_fpk_yuese.py` | 扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。 |
| `scan_packs_for_skin_assets.py` | 宽扫资源包：找**任何**与皮肤相关的图片路径（不限于脚本表引用）。 |
| `scan_sky1003_fpk.py` | 倒序扫描 049..037.fpk 的解压帧，定位 sky1003 皮肤资源。 |
| `scan_sky1003_fpk_064_050.py` | 倒序扫描 064..050.fpk，命中 sky1003 后停止并提取邻近 DDS/FSB5。 |
| `scan_table_family.py` | scan_table_family.py v2 —— 表族通道侦察器（BA8 工作副本） |
| `scan_weapon_skin_ui_assets.py` | 扫描当前客户端包：找出**武器皮肤图鉴/UI 真正引用的图片资源路径**。 |
| `search_decompressed.py` | 在**解压后**的条目数据里搜目标皮肤（而不是容器原始字节）。 |
| `segment_scout.py` | segment_scout.py —— id 段侦察器：名册段 dump / jump 组引用收集 / 缺口对照 |
| `source_presence.py` | Pure dual-source presence comparison; never merges source records. |
| `stamp_board_contract.py` | stamp_board_contract.py — 为已发布板补齐 v3 机读定位链（不改任何数据声明）。 |
| `sync_manifest_counts.py` | 同步 manifest 里各板块的条目数与分类（以 data/boards/*.json 实际内容为准）。 |
| `test_export_exchange_static_candidates.py` | 当前 Documents 静态商店候选总表的回归测试。 |
| `tidy_workspace.py` | 整理工作区：把散落的 .bak 备份收进 _备份归档/<日期>/，并生成 tools/INDEX.md。 |
| `trace_kaijia_formal_reward_chain.py` | Trace formal-client Kaijia lottery reward records from raw BinDict bytes. |
| `verify_field_semantics.py` | P2-2：字段语义可信度验证（逐 (table, schema_ref, slot) 统计判据）。 |
| `wiki_server.py` | 127.0.0.1-only server for the LifeAfter Wiki and lazy script NPK inspection. |
