# -*- coding: utf-8 -*-
"""NAMES_finalize.py — 把结论注入 NAMES_audit.json（只写该文件）。"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
p = os.path.join(OUT, 'NAMES_audit.json')
a = json.load(open(p, encoding='utf-8'))

a['task'] = '名字与身份可靠性核对（只读板数据与既有 JSON；不改任何默认文件）'
a['generated_by'] = ['NAMES_audit.py', 'NAMES_audit2.py', 'NAMES_audit3.py', 'NAMES_finalize.py']
a['summary'] = {
    'board_115': {
        'official_name_status': {'verified': 113, 'no_item_row': 2},
        'name_status': {'verified': 113, 'unresolved': 2},
        'name_resolution_state': {'verified': 113, 'behavior_preview_no_current_name_source': 2},
        'non_official_ids': ['1110185', '1110186'],
        'note': '2 条非 official 的 name=null，页面显示「未命名皮肤 · ID」；均为 behavior_preview_only / behavior_only / 无父项无道具行。'
    },
    'board_stats_three_tier': {'verified': 126, 'candidate': 5, 'unresolved': 2,
                               'total': 133,
                               'composition': '113 主皮肤 + 18 时限变体 + 2 预告层',
                               'candidate_definition': '可回放候选名（主名+时限后缀推导），页面标「名称待确认」，不得升级为 verified',
                               'candidate_ids_in_board_file': None,
                               'candidate_ids_note': '板 JSON 只给计数，未列出这 5 个 id'},
    'timed_layer_local_enumeration': {
        'source': '03拆包产物/weapon_skin_data_rows.json（本地导出）',
        'main_rows': 111, 'timed_rows': 14, 'total': 125,
        'timed_with_item_row': 8, 'timed_without_item_row': ['11100061', '11101341', '11101681', '11101771',
                                                             '11101781', '11101811'],
        'discrepancy': '本地枚举 14 变体/6 无道具行 vs 板 stats 18 变体/5 candidate ⇒ 跨快照范围差异，标 unresolved，不互相替代',
        'roster_timed_variants': {'11101451': 'has_item_row(official)', '11101691': 'has_item_row(official)',
                                  '11101771': 'no_item_row(candidate)'}
    },
    'g6_group_relation': {
        'verdict': '每组 3 个 id = 同一皮肤的「升格阶段」变体，共享同一个正式名；不是不同武器类型、也不是各自独立命名的皮肤',
        'basis_verified': ['同组 3 个 id 的 name / name_status=verified / official_name_status=verified 完全相同',
                           '同组 weapon_type 唯一（50/4/3/1/7 各一组）且 weapon_type_label 一致',
                           '同组 sale_date 相同、catalog_layer=current_parent、grade=6传世级、level=6',
                           '同组 model_path 三份互不相同（各阶段自有几何）',
                           '道具描述明文：前两个「可升格武器，外观和战斗表现会随升格变化」，第三个「当前已升至最高阶段」（5 组中 4 组如此）'],
        'basis_corroborating': ['ROSTER_g5_g6.json 的 charm_value 同组递增 1000/1500/2500（来自 weapon_skin_data 行）',
                                '板数据无 stage/upgrade_level 字段 ⇒ 阶段序号（1/2/3）为由「描述 + charm_value 递增」推出的 inferred，不是直证字段'],
        'exception': '水晶玫瑰组（1110173/174/175）三条描述均为「可升格武器…」，无「当前已升至最高阶段」明文 ⇒ 该组的末阶标记缺失',
        'falsifiable': '若任一组 3 个 id 的 weapon_type 不同，或描述不含升格语义，或三者 model_path 相同 ⇒ 本判定被证伪'
    },
    'q3_specials': {
        '1110169': {'name': '灰色协议', 'name_status': 'verified', 'official_name_status': 'verified',
                    'release_state': 'on_sale', 'catalog_layer': 'current_parent', 'version_status': 'BA8/root 均有',
                    'grade': '5典藏级', 'weapon_type': '5（狙击枪）', 'sale_date': '2026-06-24',
                    'variant_item_count': 1, 'sfx_consensus_state': 'no_sfx_text',
                    'asset_anomaly': '资产目录缺 neox_material.json（无材质源链 manifest）；有 model.glb + viewer.json；effects.json.status=not_extracted',
                    'verdict': '名字与发布状态正常（非异常）；异常在资产侧'},
        '1110146': {'name': '龙渊永寂', 'name_status': 'verified', 'official_name_status': 'verified',
                    'release_state': 'on_sale', 'catalog_layer': 'current_parent', 'version_status': 'BA8/root 均有',
                    'grade': '5典藏级', 'weapon_type': '5（狙击枪）', 'sale_date': '2026-02-11',
                    'variant_item_count': 0, 'sfx_consensus_state': 'no_sfx_text',
                    'asset_anomaly': '缺 model.glb（几何为 skin_1002_007.glb，viewer.json 已指向它）；viewer.json 的 material_layers.status=source_neutral、tone_mapping=NoToneMapping、lights=0、exposure=1（非生产 rig）；_build/BLOCKED.md 记录四轮封存复核（含「未生成 viewer.json/neox_material.json、未注册、请勿上板」）',
                    'doc_vs_disk_conflict': 'BLOCKED.md 2c.5/2d.5 声称 viewer.json / neox_material.json 未生成，但磁盘上两者都在（neox_material.json 已在）⇒ 文档与磁盘状态冲突，需 Lead 裁定是否上板',
                    'verdict': '名字与发布状态正常（非异常）；异常在资产侧 + 文档/磁盘冲突'}
    },
    'secondary_tiers': {
        'sfx_consensus_not_no_sfx_text': {'insufficient_sfx_names': ['1110009'],
                                          'ambiguous_sfx_names': ['1110151', '1110152', '1110154', '1110168', '1110182'],
                                          'sfx_consensus_unpromoted': ['1110178', '1110181', '1110183', '1110184', '1110190'],
                                          'note': '这些条目的显示名仍是 verified；未定的是 SFX 文本层命名'},
        'release_state_anomalies': {'no_sale_field': ['1110087', '1110088'], 'upcoming': ['1110184', '1110190'],
                                    'behavior_only': ['1110185', '1110186']},
        'version_status': {'BA8新增': ['1110181', '1110182', '1110183', '1110184', '1110190'],
                           '仅当前BA8行为资源；无父项无道具行': ['1110185', '1110186']}
    },
    'cross_snapshot_gap': {
        'finding': '本地 common_item_data_rows.json（34949 行）中 1110177 及其时限变体 11101771 无道具行，而板数据称 1110177 名字 verified（来源=同快照 common_item_data_base）',
        'interpretation': 'unresolved：属本地导出与板所用 BA8A 快照的范围差异，不做推断、不用别行替代'
    },
    'discipline': '只读板数据与既有 JSON；未修改任何默认文件；名称一律取自表字段原文，不猜名、不用版本号当名字。'
}
json.dump(a, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('NAMES_audit.json 已写入 sections:', sorted(a.keys()))
print('bytes', os.path.getsize(p))
