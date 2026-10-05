# -*- coding: utf-8 -*-
r"""tool_seg_map.py — 「工具 × 段位」映射（三线三带）。

唯一判据（可核，不靠名字猜）
---------------------------
段位按【该工具产物的主要下一站是谁】定：

    下游解析器/程序   → ① 解码定位复原线
    人眼 / 耳朵       → ② 图文音频渲染线
    浏览器            → ③ 前端展示交互线
    上游导航          → 带 H 热更定位带（服务端清单 / 本地快照 / 包级归因）
    接口与字段口径    → 带 D 数据契约带
    交付闸门结论      → 带 Q 质量·交付·治理带
    不产出业务产物    → 横切（入口壳 / GUI / 测试 / 限流 / 调度 / 根定位）

每条记录都带 `judge`（判据来自哪里：显式表 / 目录 / 关键词 / 未命中）
与 `why`（一句话理由），所以映射表可以逐条复核，不需要相信本模块。

★ 目录 ≠ 段位：功能域（目录）与工作流段位是正交两根轴，本模块专门把
  「不一致」标出来（`dir_mismatch`）—— 那正是不按段位重排目录的理由。

用户：CLI `run_all.py map`（打印）· docs/gen_tool_seg_map.py（落盘 .md/.json）
"""
from __future__ import annotations

import json
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Iterable

# ═══════════════════════════════════════════════════════════════════════════
# 一、段位定义（与 gen_home.py 的 LANES / BAND_UP / BANDS 一致）
# ═══════════════════════════════════════════════════════════════════════════

SEGMENTS: "OrderedDict[str, dict[str, str]]" = OrderedDict([
    ("H-1", {"band": "带H", "name": "版本清单对比",
             "q": "这次热更更新了哪些包", "next": "①/②/③ 的取材范围"}),
    ("H-2", {"band": "带H", "name": "本地冻结与终态",
             "q": "本地哪些容器真的变了（内容而非 mtime）", "next": "① 的容器范围 / ② 的新资产"}),
    ("H-3", {"band": "带H", "name": "包级归因",
             "q": "新内容归到哪一族", "next": "①/② 的族级取材"}),
    ("①-0", {"band": "①", "name": "索引地基",
             "q": "库建好了吗、新鲜吗、容器登记全吗", "next": "①-1/①-2 的查询底座"}),
    ("①-1", {"band": "①", "name": "定位与复原",
             "q": "给一个路径/编号，它在哪个包哪一行、这一行是什么", "next": "下一次解析"}),
    ("①-2", {"band": "①", "name": "批量质检",
             "q": "单条能解，批量是不是都对", "next": "交付前的清单与报告"}),
    ("②-1", {"band": "②", "name": "三维装配",
             "q": "装配帧/网格/材质能不能装成模型", "next": "人眼（3D 查看器）"}),
    ("②-2", {"band": "②", "name": "媒体定位",
             "q": "贴图/音频是哪一张、是哪一段、在哪", "next": "人眼与耳朵"}),
    ("②-3", {"band": "②", "name": "三维出图校准",
             "q": "渲染图与源的颜色/明暗对不对得上", "next": "人眼（交付图）"}),
    ("③-1", {"band": "③", "name": "页面与看板",
             "q": "数据怎么变成能点的页面", "next": "浏览器"}),
    ("③-2", {"band": "③", "name": "服务与契约",
             "q": "页面靠什么接口拿数据", "next": "浏览器/页面"}),
    ("③-3", {"band": "③", "name": "资产落地与投影",
             "q": "东西怎么落到站点侧可重建的资产", "next": "浏览器（静态资产）"}),
    ("带D", {"band": "带D", "name": "数据契约带",
             "q": "三条线交换数据时的字段/口径约定", "next": "三条线（横切接口）"}),
    ("带Q", {"band": "带Q", "name": "质量·交付·治理带",
             "q": "交付前必须过哪几道闸门", "next": "交付（横切闸门）"}),
    ("横切", {"band": "横切", "name": "被多条线共用 / 工具自身",
              "q": "入口壳、GUI、测试、限流、调度、根定位", "next": "不产出业务产物"}),
    ("归档", {"band": "归档", "name": "已归档",
              "q": "历史脚本，不参与现役流程", "next": "—"}),
    ("未分类", {"band": "未分类", "name": "未分类",
                "q": "没有命中任何判据，需要人工定段", "next": "—"}),
])

CRITERION = ("段位按【产物下一站】定：下游解析器→① / 人眼耳朵→② / 浏览器→③ / "
             "上游导航→带H / 接口口径→带D / 闸门结论→带Q / 不产业务产物→横切")

# 带 H 的宿主说明：H-1/H-2 的实现模块刻意留在 00_共享核心/toolkit_core（见
# 04_热更定位/README.md 的取舍理由），段位归属仍按 H-1/H-2 记。
H_HOST_NOTE = ("H-1/H-2 模块宿主在 00_共享核心/toolkit_core/（与 source_lock 引擎同包，"
               "避免相对导入手术）；带 H 的家在 04_热更定位/")

# ═══════════════════════════════════════════════════════════════════════════
# 二、判据
# ═══════════════════════════════════════════════════════════════════════════

# 不产出业务产物的入口壳 / GUI / 打包
ENTRY_SHELLS = {"run_all", "exe_cli", "toolkit_cli", "app", "main_qt", "rebuild_fixtures"}

# 目录 → 段位（工具库内，粗粒度；显式表优先）
DIR_DEFAULT: dict[str, tuple[str, str]] = {
    "01_解码定位复原/表解码": ("①-1", "目录=表解码：产物是行级事实，下一站=解析器"),
    "01_解码定位复原/名字还原": ("①-1", "目录=名字还原：路径↔行"),
    "01_解码定位复原/哈希提取": ("①-1", "目录=哈希提取：名字/路径→哈希，定位用"),
    "01_解码定位复原/容器格式": ("①-1", "目录=容器格式：把包解成条目 / 提取载荷"),
    "01_解码定位复原/客户端逆向": ("①-1", "目录=客户端逆向：只读侦察 exe，产出定位结论"),
    "01_解码定位复原/解包与扫描": ("①-1", "目录=解包与扫描：包→条目→内容"),
    "01_解码定位复原/资源索引": ("①-0", "目录=资源索引：容器登记与地基"),
    "02_图文音频渲染/皮肤表": ("①-1", "产物是皮肤全量表（行级事实），下一站=渲染链/展示"),
    "02_图文音频渲染/纹理转换": ("②-2", "产物是 PNG（下一站人眼）"),
    "02_图文音频渲染/皮肤链与渲染": ("②-1", "目录=皮肤链与渲染：先按装配判，例外见显式表"),
    "03_前端展示交互": ("③-1", "目录=前端展示交互"),
    "04_热更定位": ("H-1", "目录=带 H（具体段位见显式表）"),
    "00_共享核心/独立工具": ("横切", "目录=独立工具：单入口小工具，段位见显式表"),
    "00_共享核心/打包": ("横切", "打包脚本：不产出业务产物"),
    "00_共享核心/图形界面": ("横切", "GUI：不产出业务产物"),
    "docs": ("横切", "文档与生成器：不产出业务产物"),
}

# 显式表：目录判不出来的，逐条写理由（★ 复核只有这一张表要读）
EXPLICIT: dict[str, tuple[str, str]] = {
    # ── 00_共享核心/toolkit_core ──
    "00_共享核心/toolkit_core/__init__.py": ("横切", "包声明，无产物"),
    "00_共享核心/toolkit_core/paths.py": ("横切", "项目根/输出策略：所有命令共用"),
    "00_共享核心/toolkit_core/throttle.py": ("横切", "CPU/GPU 限流：cross-command 关注点"),
    "00_共享核心/toolkit_core/lines.py": ("横切", "两条线（文字/渲染）分类模型：GUI 与批量共用"),
    "00_共享核心/toolkit_core/scheduler.py": ("横切", "任务调度计划器：不产出内容"),
    "00_共享核心/toolkit_core/job_runner.py": ("横切", "GUI 任务执行层：调度而非内容"),
    "00_共享核心/toolkit_core/unified_index.py": ("①-0", "索引库本体：index/verify 的引擎（产物=可重建的库）"),
    "00_共享核心/toolkit_core/path_fid.py": ("①-1", "路径→fid 唯一实现（定位）"),
    "00_共享核心/toolkit_core/names.py": ("①-1", "名字还原引擎：路径↔行（names 命令）"),
    "00_共享核心/toolkit_core/npk_paths.py": ("①-1", "NXPK tI 逻辑路径复原（行→路径）"),
    "00_共享核心/toolkit_core/npk_extract.py": ("①-1", "Nxpk 定点提取（行→内容）"),
    "00_共享核心/toolkit_core/fpk_frames.py": ("①-1", "FPK Zstd 帧顺序读取（载荷→内容）"),
    "00_共享核心/toolkit_core/fpk_raw.py": ("①-1", "FPK 原始资源导出与索引（包→资产文件）"),
    "00_共享核心/toolkit_core/bindict_rows.py": ("①-1", "BinDict 值行解码（行→字段值）"),
    "00_共享核心/toolkit_core/bindict_scan.py": ("①-1", "BinDict 帧发现（定位）"),
    "00_共享核心/toolkit_core/bindict_table.py": ("①-1", "BinDict 表对解码（表→行）"),
    "00_共享核心/toolkit_core/table_export.py": ("①-1", "解析结果→表格（export 引擎）"),
    "00_共享核心/toolkit_core/restore_tree.py": ("①-1", "按源路径物化目录树（行→路径→文件）"),
    "00_共享核心/toolkit_core/resource_resolver.py": ("①-1", "资源物理桥定位（resolver 引擎）"),
    "00_共享核心/toolkit_core/normalize.py": ("①-1", "解码产物规范化：载荷→可解析形态"),
    "00_共享核心/toolkit_core/readable.py": ("②-2", "解包后转可读（PNG/字符串表）：产物下一站是人眼"),
    "00_共享核心/toolkit_core/bulk.py": ("①-2", "批量筛/提取/类型识别（query·bulk·identify 引擎）"),
    "00_共享核心/toolkit_core/decode_audit.py": ("①-2", "解码线体检（decode-audit 引擎）"),
    "00_共享核心/toolkit_core/texture_extractor.py": ("②-2", "匿名 GPK 纹理筛选与导出（texscan 引擎；产物是图）"),
    "00_共享核心/toolkit_core/la_glb.py": ("②-1", "glb 子命令核心：.mesh→GLB（产物=模型）"),
    "00_共享核心/toolkit_core/skin_chain.py": ("②-1", "皮肤定位链目录（装配前取材清单）"),
    "00_共享核心/toolkit_core/skin_report.py": ("②-1", "皮肤 3D 素材扫描+定位报告（装配侧）"),
    "00_共享核心/toolkit_core/weapon_skin_table.py": ("①-1", "武器皮肤全量表（行级事实表）"),
    "00_共享核心/toolkit_core/reward_pool_export.py": ("①-1", "奖励池行归一化（表→行级事实）"),
    "00_共享核心/toolkit_core/source_lock.py": ("H-2", "内容寻址快照 + 前后比对：H-2 的引擎"),
    "00_共享核心/toolkit_core/patch_delta.py": ("H-1", "服务端版本清单对比（delta 引擎）"),
    "00_共享核心/toolkit_core/patch_snapshot.py": ("H-2", "本地容器快照 + 写入窗口守卫（snapshot 引擎）"),
    "00_共享核心/独立工具/physical_bridge_audit.py": ("①-1", "物理桥审计：逻辑皮肤路径→IDX/WPK（bridge-audit）"),
    "00_共享核心/独立工具/strings_search.py": ("①-1", "py314 字符串索引关键词检索（定位）"),
    # ── 01 线：目录判据的例外 ──
    "01_解码定位复原/资源索引/quick_scan_gres.py": ("①-0", "快扫 gres 登记容器（建库地基）"),
    "01_解码定位复原/资源索引/analyze_0058_gpk.py": ("①-0", "gpk 头部/条目表分析（容器登记）"),
    "01_解码定位复原/容器格式/wpk_1dpw_verifier.py": ("①-2", "只读复验 1DPW 解密正确性（质检形状，不产新事实）"),
    "01_解码定位复原/容器格式/batch_wpk_textures.py": ("②-2", "产物是 PNG 贴图（下一站人眼）：批量解密→PNG"),
    "01_解码定位复原/解包与扫描/batch_unpack_ui.py": ("①-2", "批量解包落盘（大批量落盘不走单条定位）"),
    "01_解码定位复原/表解码/bindict_lib/static_all_equips_audit.py": ("①-2", "只做全表静态审计（批量质检形状）"),
    "01_解码定位复原/表解码/bindict_lib/validate_current_all_equips_0x76_index.py":
        ("①-2", "只校验 0x76 索引结构、不解值（质检形状）"),
    # ── 02 线：皮肤链与渲染（55 个文件按产物下一站细分）──
    "02_图文音频渲染/皮肤链与渲染/c159_pair.py": ("②-1", "装配帧 .c159 解析（装配）"),
    "02_图文音频渲染/皮肤链与渲染/c159_pair_v4.py": ("②-1", "装配帧归属规则修复版（sheet 命令引擎）"),
    "02_图文音频渲染/皮肤链与渲染/c159_parser.py": ("②-1", "装配帧条目级解析（历史/调试用）"),
    "02_图文音频渲染/皮肤链与渲染/c159_slot_parser.py": ("②-1", "装配帧槽位↔引用路径配对（装配）"),
    "02_图文音频渲染/皮肤链与渲染/dual_submesh_sheet.py": ("②-1", "双枪子网格/材质隔离表（装配侧归属判定）"),
    "02_图文音频渲染/皮肤链与渲染/mesh_parse2.py": ("②-1", ".mesh v4 通用解析（网格→模型）"),
    "02_图文音频渲染/皮肤链与渲染/export_glb.py": ("②-1", "零依赖 GLB 导出（产物=模型文件）"),
    "02_图文音频渲染/皮肤链与渲染/locate_skeleton.py": ("②-1", "骨骼定位（装配需要）"),
    "02_图文音频渲染/皮肤链与渲染/extract_vcolor.py": ("②-1", "顶点色流读取（装配件）"),
    "02_图文音频渲染/皮肤链与渲染/probe_skin_3d_batch.py": ("②-1", "批量探测皮肤能否装配出 3D（装配可行性）"),
    "02_图文音频渲染/皮肤链与渲染/build_material_manifest.py": ("②-1", "材质清单（装配期槽位绑定表）"),
    "02_图文音频渲染/皮肤链与渲染/weapon_skin_pipeline.py": ("②-3", "一条命令出图管线（产物=交付图）"),
    "02_图文音频渲染/皮肤链与渲染/render_by_skin.py": ("②-3", "按皮肤 ID 出分层图（产物=图）"),
    "02_图文音频渲染/皮肤链与渲染/render_material_layers.py": ("②-3", "源材质分层渲染（render 命令引擎）"),
    "02_图文音频渲染/皮肤链与渲染/render_layers_multiset.py": ("②-3", "多材质集分层渲染（产物=图）"),
    "02_图文音频渲染/皮肤链与渲染/render_source_only.py": ("②-3", "source-only 渲染：不带人工校色（校准基线）"),
    "02_图文音频渲染/皮肤链与渲染/render_neox_mesh.py": ("②-3", "NeoX mesh 软件渲染（产物=图）"),
    "02_图文音频渲染/皮肤链与渲染/render_experimental_dxbc_pbr.py": ("②-3", "DXBC 源公式渲染实验（校准）"),
    "02_图文音频渲染/皮肤链与渲染/unlit_render.py": ("②-3", "无光照直出（校准对照）"),
    "02_图文音频渲染/皮肤链与渲染/unlit_blend.py": ("②-3", "双贴图混合无光照（校准诊断）"),
    "02_图文音频渲染/皮肤链与渲染/silhouette_render.py": ("②-3", "轮廓/分区平涂图（校准诊断图）"),
    "02_图文音频渲染/皮肤链与渲染/lighting_defuse.py": ("②-3", "Deferred 光照 gbuffer 语义追踪（校准）"),
    "02_图文音频渲染/皮肤链与渲染/dxbc_dataflow.py": ("②-3", "DXBC 寄存器 def-use 追踪（着色器口径）"),
    "02_图文音频渲染/皮肤链与渲染/dxbc_disasm.py": ("②-3", "D3DCompiler 反汇编（着色器口径）"),
    "02_图文音频渲染/皮肤链与渲染/dxbc_inspect.py": ("②-3", "DXBC 容器 + RDEF 反射解析（着色器口径）"),
    "02_图文音频渲染/皮肤链与渲染/snap_shader_db.py": ("②-3", "shader_compile.db 快照（着色器口径取证）"),
    "02_图文音频渲染/皮肤链与渲染/stats_variant_constants.py": ("②-3", "跨变体常量统计（校准唯一化依据）"),
    "02_图文音频渲染/皮肤链与渲染/gen_param_repack.py": ("②-3", "ParamMap 通道重排（校准落地）"),
    "02_图文音频渲染/皮肤链与渲染/make_material_id.py": ("②-3", "材质 ID 图（校准诊断图）"),
    "02_图文音频渲染/皮肤链与渲染/dds_rgba_canonical.py": ("②-2", "DDS→规范 RGBA 唯一入口（tex 命令引擎）"),
    "02_图文音频渲染/皮肤链与渲染/export_tex_png.py": ("②-2", "规范 RGBA 的 DDS→PNG（产物=贴图）"),
    "02_图文音频渲染/皮肤链与渲染/cube_faces_export.py": ("②-2", "cubemap 六面/mip 导出（产物=贴图）"),
    "02_图文音频渲染/皮肤链与渲染/tex_rgba_sheets.py": ("②-2", "贴图 RGBA 通道证据图（产物=图）"),
    "02_图文音频渲染/皮肤链与渲染/idx_wpk_dds_extractor.py": ("②-2", "IDX→WPK→DDS 提取（产物=贴图）"),
    "02_图文音频渲染/皮肤链与渲染/spr_atlas_resolver.py": ("②-2", ".spr 兄弟图集解析（产物=贴图）"),
    "02_图文音频渲染/皮肤链与渲染/parse_sfx_tracks.py": ("②-2", ".sfx 特效轨道→帧表（audio 命令引擎；给渲染/音效看）"),
    "02_图文音频渲染/皮肤链与渲染/build_skin_location_chain.py": ("①-1", "皮肤定位链构建（路径↔行映射表）"),
    "02_图文音频渲染/皮肤链与渲染/resolve_declared_paths.py": ("①-1", "声明路径→容器 HIT/MISS（定位）"),
    "02_图文音频渲染/皮肤链与渲染/gpk_npk_index.py": ("①-0", "容器全量条目索引/按候选名查找（建索引）"),
    "02_图文音频渲染/皮肤链与渲染/find_assets_by_checksum.py": ("①-1", "按源资产 checksum 找资产（定位）"),
    "02_图文音频渲染/皮肤链与渲染/parse_string_pool.py": ("①-1", "Python 字节码字符串池解析（挖路径）"),
    "02_图文音频渲染/皮肤链与渲染/pool_mapping_v2.py": ("①-1", "池成员映射（表→成员）"),
    "02_图文音频渲染/皮肤链与渲染/scan_fpk.py": ("①-1", "FPK 内字符串搜索（定位）"),
    "02_图文音频渲染/皮肤链与渲染/apply_source_materials.py": ("③-3", "把源材质参数写进 viewer.json（下一站=浏览器）"),
    "02_图文音频渲染/皮肤链与渲染/build_runtime_manifest.py": ("③-3", "runtime manifest：给查看器的资产索引"),
    "02_图文音频渲染/皮肤链与渲染/raw_anchor.py": ("带Q", "贴图↔源 DDS 锚定校验：对交付物下结论"),
    "02_图文音频渲染/皮肤链与渲染/source_strict_assert.py": ("带Q", "source_strict 自动化验收：假成功/缺槽位/旧残留"),
    "02_图文音频渲染/皮肤链与渲染/wiki_acceptance.py": ("带Q", "真实 wiki 页面生产验收（交付闸门）"),
    "02_图文音频渲染/皮肤链与渲染/wiki_selfcheck.py": ("带Q", "wiki 页面自检（交付闸门安全网）"),
    "02_图文音频渲染/皮肤链与渲染/wiki_3d_pixel_verify.py": ("带Q", "截图像素级决定性验收（交付闸门）"),
    "02_图文音频渲染/皮肤表/build_weapon_skin_table.py": ("①-1", "武器皮肤全量表生成（薄封装，产物=表）"),
    "02_图文音频渲染/纹理转换/ktx_to_png.py": ("②-2", "安卓 KTX→PNG（产物=贴图）"),
}

# 3D 预览器（离线查看器）资产构建脚本：产品默认给浏览器看 ⇒ 逐条判到 ②/③
_PREV = "02_图文音频渲染/3D预览器/poster/assets/3d/weapon_skin/"
EXPLICIT.update({
    _PREV + "1110177/_build_t5/exp_render.py": ("②-3", "渲染+色彩度量（产物=图与度量）"),
    _PREV + "1110177/_build_t5/decode_stats.py": ("②-2", "解码候选 DDS 判槽位（贴图定位）"),
    _PREV + "1110177/_build_t5/recon.py": ("②-2", "c159 逻辑贴图路径→本地文件映射（媒体定位）"),
    _PREV + "1110177/_build_t5/verify_rules.py": ("带Q", "核对既有配方是否成立（结论）"),
    _PREV + "1110177/_build_t5/lab_probe.py": ("③-1", "lab 模式复核查看器页面（页面诊断）"),
    _PREV + "1110177/_build_t5/err_probe.py": ("③-1", "定位查看器 render 异常（页面诊断）"),
    _PREV + "1110177/_build_t5/diag_variant.py": ("③-1", "生成诊断 manifest 变体绕过查看器崩溃（页面诊断）"),
    _PREV + "1110177/_build_t5/accept_probe.py": ("③-3", "查看器资产验收探针（为查看器构建/验收）"),
    _PREV + "1110177/_build_t5/build_assets.py": ("③-3", "为 1110177 产查看器资产（下一站=浏览器）"),
    _PREV + "1110177/_build_t5/build_manifest.py": ("③-3", "生成 viewer.json/neox_material.json（查看器资产）"),
    _PREV + "1110177/_build_t5/build_crystal_params.py": ("③-3", "写 per-material 晶体参数进查看器资产"),
    _PREV + "1110177/_build_t5/build_fix.py": ("③-3", "把「晶体族 q_T=无色」口径落到 manifest"),
    _PREV + "1110177/_build_t5/slots_report.py": ("③-3", "槽位绑定状态表（查看器交付证据）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_build_bright_cube.py": ("②-3", "自造亮环境 cube 构造（校色）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_analyze_diff_20260921.py": ("②-3", "换 cube 改了哪些像素（校准取证）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_analyze_source.py": ("②-3", "源侧实测（校准取证）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_probe_conflict_20260921.py": ("②-3", "并发冲突下实际用哪套 cube（校准诊断）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_probe_envreach_20260921.py": ("②-3", "环境可达性判定（校准诊断）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_probe_tiers_20260921.py": ("②-3", "三档金属区对照（校准诊断）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_mk_report_20260921.py": ("②-3", "汇总校准报告（数字取自产物）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_emit_manifest.py": ("③-3", "自造 cube 登记进站点 manifest（浏览器资产）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_patch_default_20260921.py": ("③-3", "把默认 cube 档切到自造 cube（查看器默认档）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_revert_default_20260921.py": ("③-3", "回退默认 cube 档（查看器默认档）"),
    _PREV + "_shared/cubes/custom_bright_20260921/_verify_default_20260921.py": ("带Q", "默认切换的独立证据（结论）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_build_snow_cube.py": ("②-3", "自造亮雪环境 cube 构造（校色）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_sweep_gain_floor.py": ("②-3", "反解增益/抬底（校色求解）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_sweep_minimal.py": ("②-3", "最小整体增亮解（校色求解）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_sweep_refine.py": ("②-3", "细化网格解（校色求解）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_patch_manifest_default.py": ("③-3", "写 manifest 默认档（查看器资产）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_patch_viewer_js.py": ("③-3", "给查看器 JS 打默认 cube 补丁（浏览器资产）"),
    _PREV + "_shared/cubes/custom_bright_snow_20260921/_set_default_snow.py": ("③-3", "写 viewer.json 默认选择（查看器资产）"),
    _PREV + "_shared/cubes/custom_studio_20260920/_build_custom_cube.py": ("②-3", "自造环境 cube 构造（校色）"),
    _PREV + "_shared/cubes/custom_studio_20260920/_encode_rgbm.py": ("②-3", "生成与源 shader 编码一致的 RGBM 六面（校色）"),
    _PREV + "_shared/cubes/custom_studio_20260920/_emit_manifest.py": ("③-3", "由 provenance 生成站点 cube manifest（浏览器资产）"),
})

# ② 线关键词（仅用于「目录给了 ② 线但段位不明」时细分；显式表优先）
SEG2_KEYWORDS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("②-2", ("dds", "tex_", "texture", "cube", "ktx", "atlas", "spr", "sfx", "fsb",
              "audio", "sound", "poster", "wav", "bank", "sprite", "png"),
     "关键词命中媒体（贴图/音频）"),
    ("②-3", ("render", "unlit", "lighting", "blend", "material", "shader", "dxbc",
              "silhouette", "param_repack", "pipeline", "color", "tone", "grade"),
     "关键词命中出图/校色"),
    ("②-1", ("c159", "mesh", "glb", "skeleton", "vcolor", "submesh", "neox",
              "capture", "parts", "assemble", "bind"),
     "关键词命中三维装配"),
)

# ── 站点工具（04_站点/web/tools，164 个）：③ 线的宿主，但业务段位横跨全部段 ──
SITE_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("带Q", ("checks.py", "run_checks.py", "record_regression.py", "publication_policy.py",
             "source_presence.py", "stamp_board_contract.py", "verify_field_semantics.py",
             "audit_", "announce_calibrate", "calibrate_"),
     "只产出检查/门禁/审计结论（交付闸门）"),
    ("③-2", ("wiki_server.py", "live_npk_reader.py", "refresh_sidecars.py", "read_large_npk.py",
             "_cmp_decoder"),
     "本地服务/读取接口（页面靠它拿数据）"),
    ("③-1", ("gen_home.py", "build_wiki.py", "rebuild_wiki_v01.py", "export_poster.py"),
     "页面/看板生成"),
    ("①-0", ("index_", "merge_file_index.py", "build_fpk_index.py", "build_table_index.py",
             "build_row_index.py", "build_source_registry.py", "scan_client_file_map.py",
             "analyze_client_file_map.py", "build_field_names.py"),
     "建索引/登记容器（地基）"),
    ("①-1", ("query_", "build_id_locator.py", "build_name_locator.py", "build_locator_chains.py",
             "build_id_occurrence.py", "build_name_chain_candidates.py", "build_fashion_identity_locator.py",
             "build_item_identity_locator.py", "locate_", "parse_", "extract_", "scan_",
             "search_decompressed.py", "bindict_provenance.py", "build_table_families.py",
             "build_table_inventory_for_basis.py", "decode_probe.py", "find_gim_by_bounds.py",
             "crack_mesh_layout.py", "source_presence.py"),
     "定位/解析/查询 → 行级事实"),
    ("②-2", ("export_fpk_textures.py", "carve_fsb5_banks.py", "extract_gres_audio_banks.py",
             "aggregate_skin_audio.py", "find_skin_audio_banks.py", "scan_client_for_audio.py",
             "attach_skin_shots.py", "export_fashion_face.py"),
     "媒体（贴图/音频）定位与导出"),
    ("③-3", ("rebuild_", "build_weapon_skin_", "build_fashion_", "build_item_", "build_reliable_sources.py",
             "export_", "add_weapon_skin_status", "build_skin_assets.py", "build_workcopy_current_package.py",
             "build_weapon_skin_compendium.py", "build_locator_chains.py"),
     "站点板数据/资产落地（下一站=浏览器）"),
)


def _site_classify(name: str) -> tuple[str, str, str]:
    if name in SITE_EXPLICIT:
        seg, why = SITE_EXPLICIT[name]
        return seg, "显式表：" + why, "高"
    if name in {"__init__.py"}:
        return "横切", "包声明", "高"
    if name.startswith("test_"):
        return "横切", "测试：只验证实现", "高"
    for seg, keys, why in SITE_RULES:
        if any(k in name for k in keys):
            return seg, "站点工具关键词判据：" + why + "（待人工复核）", "中"
    return "未分类", "站点工具未命中任何关键词判据，需人工定段", "低"


# 站点工具里关键词判不出来的（逐条给理由，不留「未分类」）
SITE_EXPLICIT: dict[str, tuple[str, str]] = {
    "lib_fashion.py": ("横切", "站点内部公共库：被多个站点工具 import，不单独出产物"),
    "preview_board_contract.py": ("带D", "板数据契约冻结（字段/口径约定）"),
    "provenance_standard.py": ("带D", "provenance 字段标准（跨线交换口径）"),
    "probe_untyped_containers.py": ("①-0", "探测未登记容器并登记（地基）"),
    "segment_scout.py": ("①-1", "id 段侦察：名册/引用/缺口 → 行级事实"),
    "trace_kaijia_formal_reward_chain.py": ("①-1", "奖励链追踪 → 行级事实"),
    "build_lottery_pool_resolved_v01.py": ("③-3", "抽奖池落地数据（下一站=浏览器板）"),
    "_probe_huodong_20260921.py": ("①-1", "活动数据探针：从表里抠出目标行（行级事实）"),
    "_probe_huodong2_20260921.py": ("①-1", "活动数据探针（同上）"),
    "_probe_huodong3_20260921.py": ("①-1", "活动数据探针（同上）"),
    "_probe_huodong4_20260921.py": ("①-1", "活动数据探针（同上）"),
    "_probe_ice_drone_20260921.py": ("①-1", "冰雷无人机数据探针（同上）"),
    "_probe_nucleus_20260921.py": ("①-1", "芯片数据探针（同上）"),
    "_probe_nucleus2_20260921.py": ("①-1", "芯片数据探针（同上）"),
    "_probe_nucleus3_20260921.py": ("①-1", "芯片数据探针（同上）"),
}


def classify_site(name: str) -> tuple[str, str, str]:
    return _site_classify(name)


# ═══════════════════════════════════════════════════════════════════════════
# 三、归类
# ═══════════════════════════════════════════════════════════════════════════

def _dir_default(rel: str) -> tuple[str, str] | None:
    parts = rel.split("/")
    for depth in (2, 1):
        key = "/".join(parts[:depth])
        if key in DIR_DEFAULT:
            return DIR_DEFAULT[key]
    # 01_/02_/03_/04_ 线级兜底
    line = parts[0][:2]
    if parts[0].startswith(("01_", "02_", "03_", "04_")):
        seg = {"01": "①", "02": "②", "03": "③", "04": "带H"}[line]
        return seg, "目录只表达到线段（%s），段位需按产物下一站细化" % seg
    return None


def classify(rel: str, text: str = "") -> tuple[str, str, str]:
    """返回 (段位, 判据说明, 置信度)。置信度：高=显式表/无争议目录；中=关键词；低=未命中。"""
    parts = rel.split("/")
    name = parts[-1]
    stem = name[:-3] if name.endswith(".py") else name

    if parts[0] == "_归档":
        return "归档", "在 _归档/ 下：历史脚本，不参与现役流程", "高"
    if "测试" in parts or stem.startswith("test_") or name == "conftest.py":
        return "横切", "测试/夹具：只验证实现，不产出业务产物", "高"
    if rel in EXPLICIT:
        seg, why = EXPLICIT[rel]
        return seg, "显式表：" + why, "高"
    if stem in ENTRY_SHELLS:
        return "横切", "入口壳/启动器：命令定义或引导，不产出业务产物", "高"
    if parts[0] in {"图形界面", "打包"} or parts[:2] == ["00_共享核心", "图形界面"] \
            or parts[:2] == ["00_共享核心", "打包"]:
        return "横切", "GUI/打包：不产出业务产物", "高"
    if parts[0] == "docs":
        return "横切", "文档/生成器：不产出业务产物", "高"

    dflt = _dir_default(rel)
    if dflt and dflt[0] not in {"②"}:
        return dflt[0], "目录判据：" + dflt[1], "高" if "-" in dflt[0] else "中"
    if dflt and dflt[0] == "②":
        blob = (stem + " " + text[:1200]).lower()
        for seg, keys, why in SEG2_KEYWORDS:
            if any(k in blob for k in keys):
                return seg, "关键词判据：" + why, "中"
        return "②-1", "关键词未命中：按目录（皮肤链与渲染）默认归装配，待复核", "低"

    # 00_共享核心 其它（命令行/测试/conftest 已处理）
    if parts[0] == "00_共享核心":
        return "横切", "共享核心：被多条线共用或只服务工具自身", "中"
    return "未分类", "没有命中任何判据，需要人工定段", "低"


def collect(toolkit_root: Path | str, *, site_tools: Path | str | None = None,
            include_archive: bool = True) -> list[dict[str, Any]]:
    """扫两个根：01_工具/工具库（主）+ 04_站点/web/tools（③ 线宿主）。"""
    toolk = Path(toolkit_root).resolve()
    if site_tools is None:
        site_tools = toolk.parent.parent / "04_站点" / "web" / "tools"
    rows: list[dict[str, Any]] = []

    for p in sorted(toolk.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(toolk).as_posix()
        if not include_archive and rel.startswith("_归档"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        seg, why, conf = classify(rel, text)
        dflt = _dir_default(rel)
        line = seg.split("-")[0]
        dir_line = None
        if dflt:
            dir_line = dflt[0].split("-")[0]
        rows.append({
            "area": "工具库", "path": rel, "seg": seg,
            "seg_name": SEGMENTS.get(seg, {}).get("name", ""),
            "judge": why, "why": why, "confidence": conf,
            "lines": text.count("\n") + 1, "bytes": p.stat().st_size,
            "dir_line": dir_line,
            "dir_mismatch": bool(dir_line and dir_line != line and line not in ("横切",)),
        })

    st = Path(site_tools)
    if st.is_dir():
        for p in sorted(st.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            rel = p.relative_to(st).as_posix()
            if rel.startswith("tests/"):
                seg, why, conf = "横切", "测试：只验证实现", "高"
            else:
                seg, why, conf = _site_classify(p.name)
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            rows.append({
                "area": "站点", "path": rel, "seg": seg,
                "seg_name": SEGMENTS.get(seg, {}).get("name", ""),
                "judge": why, "why": why, "confidence": conf,
                "lines": text.count("\n") + 1, "bytes": p.stat().st_size,
                "dir_line": "③", "dir_mismatch": False,
            })
    return rows


def summarize(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """按段位汇总（只统计现役；归档单独一行）。"""
    buckets: "OrderedDict[str, list[dict]]" = OrderedDict((k, []) for k in SEGMENTS)
    for r in rows:
        buckets.setdefault(r["seg"], []).append(r)
    out = []
    for seg, defn in SEGMENTS.items():
        items = buckets.get(seg) or []
        out.append({
            "seg": seg, "band": defn["band"], "name": defn["name"],
            "question": defn["q"], "next": defn["next"],
            "count": len(items),
            "toolkit": sum(1 for i in items if i["area"] == "工具库"),
            "site": sum(1 for i in items if i["area"] == "站点"),
            "review": sum(1 for i in items if i["confidence"] != "高"),
            "low_confidence": sum(1 for i in items if i["confidence"] == "低"),
            "items": items,
        })
    return out


def match_seg(query: str) -> list[str]:
    """把 --seg 的写法解析成段位集合。

    接受：'②-2'（精确）· '②'（前缀，含全部 ②-*）· 'H'/'带H'（H-1..H-3）· 'D'/'带D' · '横切' · '归档'
    """
    q = (query or "").strip()
    if not q:
        return []
    if q in SEGMENTS:
        return [q]
    hits = [s for s in SEGMENTS if s.startswith(q)]
    alias = {"H": "H-", "带H": "H-", "带 H": "H-", "热更": "H-", "热更定位带": "H-",
             "D": "带D", "带D": "带D", "Q": "带Q", "带Q": "带Q",
             "①": "①-", "②": "②-", "③": "③-"}
    if not hits and q in alias:
        pre = alias[q]
        hits = [s for s in SEGMENTS if s.startswith(pre)]
    if not hits and q in SEGMENTS.get(q, {}):
        hits = [q]
    return hits


def totals(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    rows = list(rows)
    return {
        "total": len(rows),
        "toolkit": sum(1 for r in rows if r["area"] == "工具库"),
        "site": sum(1 for r in rows if r["area"] == "站点"),
        "archive": sum(1 for r in rows if r["seg"] == "归档"),
        "active": sum(1 for r in rows if r["seg"] not in {"归档"}),
        "dir_mismatch": sum(1 for r in rows if r.get("dir_mismatch")),
        "low_confidence": sum(1 for r in rows if r["confidence"] == "低"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 四、渲染
# ═══════════════════════════════════════════════════════════════════════════

def render_text(rows: list[dict[str, Any]], *, seg_filter: Iterable[str] | None = None,
                show_files: bool = False, by_seg: dict[str, list[str]] | None = None,
                limit: int | None = None) -> str:
    """人读格式。by_seg = 段位→CLI 命令清单（由 CLI 现场从 parser 里取）。"""
    want = None if not seg_filter else set(seg_filter)
    t = totals(rows)
    out: list[str] = []
    out.append("══ 工具 × 段位 映射（三线三带）══")
    out.append("判据：" + CRITERION)
    out.append("扫描：%d 个 .py（工具库 %d · 站点工具 %d）· 归档 %d · 目录与段位不一致 %d"
               % (t["total"], t["toolkit"], t["site"], t["archive"], t["dir_mismatch"]))
    out.append("")

    for blk in summarize(rows):
        seg = blk["seg"]
        if want is not None and seg not in want:
            continue
        if seg == "归档" and want is None:
            continue
        cmds = (by_seg or {}).get(seg) or []
        head = "%-8s %-14s %4d 个（工具库 %d · 站点 %d）" % (
            seg, blk["name"], blk["count"], blk["toolkit"], blk["site"])
        out.append(head)
        out.append("         答：%s ｜ 下一站：%s" % (blk["question"], blk["next"]))
        if cmds:
            out.append("         CLI：" + " · ".join(cmds))
        if blk["review"]:
            out.append("         ⚠ 待复核 %d 个（关键词判据 %d · 未命中 %d）"
                       % (blk["review"], blk["review"] - blk["low_confidence"], blk["low_confidence"]))
        if show_files or want is not None:
            items = blk["items"]
            if limit:
                items = items[:limit]
            for r in items:
                tag = {"高": " ", "中": "~", "低": "?"}[r["confidence"]]
                out.append("        %s %s%s" % (tag, r["path"], "  ← %s" % r["why"] if want else ""))
            if limit and blk["count"] > limit:
                out.append("        … 另 %d 个（--limit 0 看全部）" % (blk["count"] - limit))
        out.append("")

    if want is not None and not [b for b in summarize(rows) if b["seg"] in want]:
        out.append("（--seg %s 没有匹配到任何段位；可用：%s）"
                   % ("/".join(want), " · ".join(SEGMENTS)))
    out.append("图例：段位前的 [①②③H-N] 是 CLI 子命令里保留的段位前缀（跳转锚点）。")
    out.append("      ✓ 高置信（显式表/目录） · ~ 中（关键词） · ? 低（待人工定段）")
    return "\n".join(out)


def render_md(rows: list[dict[str, Any]], *, by_seg: dict[str, list[str]] | None = None,
              generated_by: str = "docs/gen_tool_seg_map.py") -> str:
    t = totals(rows)
    L: list[str] = []
    L.append("# 工具 × 段位 映射（三线三带）")
    L.append("")
    L.append("生成器：`%s` ｜ 逻辑唯一处：`00_共享核心/toolkit_core/tool_seg_map.py` ｜ "
             "现场打印：`run_all.py map`" % generated_by)
    L.append("")
    L.append("## 判据（唯一，可核）")
    L.append("")
    L.append(CRITERION)
    L.append("")
    L.append("| 段位 | 它回答什么 | 产物下一站 | 工具库 | 站点工具 | 待复核（关键词/未命中） |")
    L.append("|---|---|---|---|---|---|")
    for b in summarize(rows):
        if b["seg"] == "归档":
            continue
        L.append("| %s %s | %s | %s | %d | %d | %d/%d |"
                 % (b["seg"], b["name"], b["question"], b["next"],
                    b["toolkit"], b["site"],
                    b["review"] - b["low_confidence"], b["low_confidence"]))
    L.append("| 归档 | 历史脚本，不参与现役流程 | — | %d | %d | - |"
             % (sum(1 for r in rows if r["seg"] == "归档" and r["area"] == "工具库"),
                sum(1 for r in rows if r["seg"] == "归档" and r["area"] == "站点")))
    L.append("")
    L.append("合计 %d 个 .py（现役 %d · 归档 %d）｜ 工具库 %d · 站点工具 %d ｜ "
             "**目录与段位不一致 %d 个** ｜ 未命中判据（未分类）%d 个"
             % (t["total"], t["active"], t["archive"], t["toolkit"], t["site"],
                t["dir_mismatch"], t["low_confidence"]))
    L.append("")
    L.append("> 「目录与段位不一致」= 它所在的目录表达的功能域，与它产物的下一站不是同一条线。"
             "这正是**不按段位重排目录**的量化理由（功能域与工作流段位是正交两根轴）。")
    L.append("")
    L.append("段位前的 `[H-1]`/`[①-1]` 是 CLI 子命令 help 里保留的段位前缀（跳转锚点）。")
    L.append("")
    L.append("## 逐文件归属")
    L.append("")
    L.append("`✓` 高置信（显式表/目录判据）· `~` 中（关键词判据）· `?` 低（待人工定段）")
    L.append("")

    for area in ("工具库", "站点"):
        L.append("### %s（%s）" % (area, "01_工具/工具库" if area == "工具库"
                                   else "04_站点/web/tools —— ③ 线的宿主"))
        L.append("")
        for b in summarize(rows):
            items = [r for r in b["items"] if r["area"] == area]
            if not items:
                continue
            if b["seg"] == "归档" and len(items) > 8:
                L.append("#### %s %s —— %d 个（归档，不逐个列）" % (b["seg"], b["name"], len(items)))
                L.append("")
                continue
            cmds = (by_seg or {}).get(b["seg"]) or []
            title = "#### %s %s —— %d 个" % (b["seg"], b["name"], len(items))
            if cmds:
                title += " ｜ CLI：`%s`" % "` · `".join(cmds)
            L.append(title)
            L.append("")
            L.append("| 文件 | 判据 |")
            L.append("|---|---|")
            for r in items:
                tag = {"高": "✓", "中": "~", "低": "?"}[r["confidence"]]
                L.append("| `%s` | %s %s |" % (r["path"], tag, r["why"]))
            L.append("")
    return "\n".join(L) + "\n"


def write_artifacts(rows: list[dict[str, Any]], out_dir: Path | str, *,
                    by_seg: dict[str, list[str]] | None = None) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t = totals(rows)
    md = out / "工具段位映射.md"
    js = out / "工具段位映射.json"
    md.write_text(render_md(rows, by_seg=by_seg), encoding="utf-8", newline="\n")
    js.write_text(json.dumps({
        "schema": "lifeafter-tool-seg-map-v1",
        "criterion": CRITERION,
        "segments": [{"seg": k, **v} for k, v in SEGMENTS.items()],
        "totals": t,
        "segments_summary": [{k: v for k, v in b.items() if k != "items"} for b in summarize(rows)],
        "cli_by_seg": by_seg or {},
        "items": rows,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return {"md": md, "json": js}


def default_toolkit_root() -> Path:
    """工具库根（本文件在 <工具库>/00_共享核心/toolkit_core/ 下）。"""
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_共享核心").is_dir() and (up / "01_解码定位复原").is_dir():
            return up
    raise RuntimeError("找不到工具库根（期望同时含 00_共享核心 与 01_解码定位复原）")


if __name__ == "__main__":                       # 直接跑＝打印映射表
    _rows = collect(default_toolkit_root())
    print(render_text(_rows, show_files=False))
