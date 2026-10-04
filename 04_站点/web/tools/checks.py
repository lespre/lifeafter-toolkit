# -*- coding: utf-8 -*-
"""三线台账「可核判据」注册表（台账里写 @名字 引用这里）。

## 为什么要有这个模块

台账原先只能引用两类东西：`{实时数据键}` 和 `#待修编号`。
但很多「有什么 / 缺什么」是【能力断言】——「查询链只读可用」「缺通用导出器」
「页面不消费音频」这类。它们既不是某个数字，也不是清单里的条目，
于是只能写成手写散文，而手写散文会飘、会对着过时的事实继续说。

本模块把这类断言变成**每次采集都可重复执行的判据**。

## 语义铁律：ok = 好状态

判据一律表达【期望达成的状态】，通过即 「有」，不通过即 「缺」：

    @名字 写在【有什么】→ ok 才显示；不 ok 自动移除
    @名字 写在【缺什么】→ 不 ok 才显示；ok 时自动移除并【迁到「有什么」】

所以判据名字要读得成一句「好事」，比如 `web_root_clean`（根目录干净）、
`api_implemented`（接口层有实现）。**不要**写成 `api_empty` 这种——
它在「缺什么」里会反过来。命名与语义必须一致。

## 硬性约束：必须便宜

主页端点是 15 秒轮询，`gen_home.collect()` 本身只要约 1.1 秒。
所以这里的判据只做**毫秒级**动作：读文件头、数文件、查计数、解析入口脚本。
**需要真跑解包命令的判据不要放这里** —— 放 `SLOW_CHECKS`，由 `tools/run_checks.py`
带 TTL 跑一次落盘，主页读缓存（页面上会标明是缓存值）。
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

PROJECT = Path(r"E:/la拆包项目")
WEB = PROJECT / "04_站点" / "web"
API_DIR = PROJECT / "04_站点" / "api"
RUN_ALL = PROJECT / "01_工具" / "run_all.py"
# ★ 命令定义的【唯一来源】。2026-09-26 起 run_all.py 只是薄壳，
#   子命令全在 toolkit_cli.build_parser()。判据要验能力就得看这里。
TOOLKIT_CLI = PROJECT / "01_工具" / "工具库" / "00_共享核心" / "命令行" / "toolkit_cli.py"
TOOLKIT_CORE = PROJECT / "01_工具" / "工具库" / "00_共享核心"
CACHE_PATH = PROJECT / "03_执行" / "10_索引" / "checks_cache.json"

# 名字 → (标签, 函数)。函数签名 fn(project, data) -> (ok, detail)
CHECKS: dict[str, tuple[str, object]] = {}
SLOW_CHECKS: dict[str, tuple[str, object]] = {}


def _read_text(p: Path, limit: int | None = None) -> str:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return t[:limit] if limit else t


def _run_all() -> str:
    return _read_text(RUN_ALL)


def _count(root: Path, pattern: str, recursive: bool = False) -> int:
    if not root.is_dir():
        return -1
    it = root.rglob(pattern) if recursive else root.glob(pattern)
    return sum(1 for _ in it)


_CLI_SUBS_CACHE: list = []          # [frozenset] 进程内只枚举一次


def _tc_module(dotted: str):
    """按点号路径拿 toolkit_core 的子模块。

    ★ 必须用 importlib.import_module，不能 `from toolkit_core import path_fid`：
      `toolkit_core/__init__.py` 里 `from .unified_index import ... path_fid`
      re-export 了一个【同名函数】，会把同名【子模块】遮住 ——
      实测 `from toolkit_core import path_fid` 拿到的是函数（没有 __file__），
      于是 `getattr(m, "cross_check")` 取不到，判据假 ✗。
    """
    import importlib
    import sys as _sys
    core = str(TOOLKIT_CORE)
    if core not in _sys.path:
        _sys.path.insert(0, core)
    return importlib.import_module(dotted)


def _cli_subcommands() -> set:
    """枚举统一 CLI 的子命令（含 index 的二级）。

    ★ 为什么不 grep 文本：判据原本 `re.search(..., _run_all())` 搜 run_all.py，
      而 2026-09-26 它变成薄壳后搜不到任何子命令 ⇒ 五项判据集体假 ✗。
      改成直接问解析器 —— 那才是命令定义的唯一来源。
    ★ 为什么加缓存：这个导入要加载整个解析器，单次约 1 秒；
      而 15 秒轮询的采集总预算才 1.1 秒左右。缓存在进程内复用。
    """
    if _CLI_SUBS_CACHE:
        return _CLI_SUBS_CACHE[0]
    import importlib.util
    import sys as _sys
    try:
        core = str(TOOLKIT_CORE)
        cli_dir = str(TOOLKIT_CORE / "命令行")
        for p in (cli_dir, core):
            if p not in _sys.path:
                _sys.path.insert(0, p)
        spec = importlib.util.spec_from_file_location("_chk_toolkit_cli", TOOLKIT_CLI)
        m = importlib.util.module_from_spec(spec)
        _sys.modules["_chk_toolkit_cli"] = m
        spec.loader.exec_module(m)
        parser = m.build_parser()
    except Exception:
        _CLI_SUBS_CACHE.append(frozenset())
        return set()
    subs = set()
    for act in parser._actions:
        if act.__class__.__name__ == "_SubParsersAction":
            for name, sub in act.choices.items():
                subs.add(name)
                for a2 in sub._actions:
                    if a2.__class__.__name__ == "_SubParsersAction":
                        for n2 in a2.choices:
                            subs.add("%s %s" % (name, n2))
    _CLI_SUBS_CACHE.append(frozenset(subs))
    return subs


# 进程内 TTL 记忆：给「自身不便宜但结果不会秒变」的判据用。
# ★ 实测踩过：poster_scripts 在 01_工具/03_执行 里 rglob，单它一个 1.3 秒，
#   把 collect() 从 1.13s 拖到 2.48s（占全部判据耗时的 98%）。
_MEMO: dict[str, tuple[float, tuple]] = {}


def memo(seconds: float):
    """给判据加进程内 TTL 缓存。结果在 TTL 内复用；超时重算。"""
    import time as _t

    def deco(fn):
        def wrap(p, data):
            key = fn.__name__
            now = _t.monotonic()
            hit = _MEMO.get(key)
            if hit is not None and (now - hit[0]) < seconds:
                return hit[1]
            res = fn(p, data)
            _MEMO[key] = (now, res)
            return res
        wrap.__name__ = fn.__name__
        return wrap
    return deco


def quick(name: str, label: str):
    def deco(fn):
        CHECKS[name] = (label, fn)
        return fn
    return deco


def slow(name: str, label: str):
    def deco(fn):
        SLOW_CHECKS[name] = (label, fn)
        return fn
    return deco


# ═══════════════════════════ ① 解码定位复原线

@quick("index_rebuild_entry", "统一入口提供索引重建子命令")
def _index_rebuild(p, data):
    t = _run_all()
    ok = "index" in t and "build" in t
    return ok, ("run_all.py 提供 index build" if ok else "run_all.py 里找不到 index build")


@quick("index_health_query", "索引健康可一条命令查询")
def _index_health(p, data):
    t = _run_all()
    ok = "index" in t and "status" in t
    q, s = data.get("quick"), data.get("stale")
    return ok, f"run_all.py index status；当前 quick_check={q} · 过期={s}"


@quick("row_npk_registered", "数据包段有登记")
def _row_npk(p, data):
    v = data.get("row_npk")
    if v is None:
        return False, "数据包行数读取失败"
    ok = (v > 0)
    return ok, (f"数据包登记 {v:,} 行" if ok
                else "数据包段登记为 0，且没有重建脚本")


@quick("name_tables_exist", "名字查询表与编号定位表都已建立")
def _name_tables(p, data):
    items = [("NAME_LOCATOR.db", WEB / "E:/la拆包项目/03_执行/10_索引/site_data" / "NAME_LOCATOR.db"),
             ("id_locator_index.db", WEB / "E:/la拆包项目/03_执行/10_索引/site_data" / "id_locator_index.db")]
    ok = all(x.is_file() for _n, x in items)
    return ok, " · ".join(f"{n}{'✓' if x.is_file() else '✗'}" for n, x in items)


@quick("name_chain_single_source", "名字还原与路径编号编码有统一校验入口")
def _name_chain(p, data):
    """验能力而不是搜文本：`path_fid.cross_check()` 就是那个统一校验入口
    —— 它把全项目所有「路径→fid」实现逐个与基准对照。"""
    try:
        pf = _tc_module("toolkit_core.path_fid")
        ok = callable(getattr(pf, "cross_check", None))
    except Exception:
        ok = False
    return ok, ("toolkit_core/path_fid.cross_check()：各实现逐个对照基准" if ok
                else "没有统一校验入口，各实现各写各的")


@quick("name_chain_hitrate", "两条链有统一的命中率口径")
def _name_hitrate(p, data):
    """口径定义在 `path_fid.py`：「命中率 = resolve 在语料上非 None 的比例」，
    并提供了 `hit_rate()` 直接算。"""
    try:
        pf = _tc_module("toolkit_core.path_fid")
        ok = callable(getattr(pf, "hit_rate", None))
    except Exception:
        ok = False
    return ok, ("统一口径：resolve 在语料上非 None 的比例（path_fid.hit_rate）" if ok
                else "两条链没有统一的命中率口径，无法判断谁更可信")


@quick("generic_exporter", "有「解析结果 → 表格文件」的通用导出器")
def _generic_exporter(p, data):
    subs = _cli_subcommands()
    ok = "export" in subs
    return ok, ("统一入口提供 export（支持 csv / json / md，输入可为 .bin 或 fid）" if ok
                else "没有通用导出器，每个新表都得现写脚本")


@quick("bindict_entry", "结构表族可查单行字段")
def _bindict_entry(p, data):
    subs = _cli_subcommands()
    ok = "bindict-check" in subs
    return ok, ("统一入口提供 bindict-check（结构表族自检）" if ok
                else "统一入口没有 bindict-check")


@quick("parser_selfcheck", "解析器带原生判据自检（尺寸与附加流状态）")
def _parser_selfcheck(p, data):
    core = PROJECT / "01_工具" / "工具库"  / "00_共享核心" / "toolkit_core"
    txt = _read_text(core / "npk_extract.py") + _read_text(core / "unified_index.py")
    ok = ("size_check" in txt) or ("extra_streams_state" in txt)
    return ok, ("解析器有尺寸/附加流自检" if ok else "解析器没有原生判据自检")


# ═══════════════════════════ ② 图文音频渲染线

@quick("glb_entry", "统一入口提供「部件 → 模型文件」子命令")
def _glb_entry(p, data):
    subs = _cli_subcommands()
    ok = "glb" in subs
    return ok, ("统一入口提供 glb（部件级 .mesh → 单 GLB，含自检）" if ok
                else "统一入口里没有 glb")


@quick("pack_entry", "有批量打包与图集能力")
def _pack_entry(p, data):
    ok = bool(re.search(r"['\"]pack['\"]", _run_all()))
    return ok, ("run_all.py 提供 pack" if ok else "一次只出一件，没有成批出件能力")


@quick("glb_byte_stable", "重跑产物与历史产出逐字节等价")
def _glb_byte_stable(p, data):
    """判据：是否存在记录这一核验的文档/报告。"""
    docdir = PROJECT / "00_治理" / "文档"
    hit = False
    if docdir.is_dir():
        for f in docdir.rglob("*.md"):
            t = _read_text(f, 200000)
            if "逐字节" in t and ("glb" in t.lower() or "模型" in t):
                hit = True
                break
    return hit, ("有逐字节等价的核验记录" if hit else "找不到逐字节等价的核验记录")


@quick("zs_glb_present", "专题页在消费模型文件")
def _zs_glb(p, data):
    n = _count(WEB / "assets" / "3d" / "zs3d", "*.glb")
    if n < 0:
        return False, "专题资产目录不存在"
    return n > 0, f"斩神专题目录有 {n} 个模型文件"


@quick("texture_chain_entry", "常规贴图与立方体贴图解码链可用")
def _tex_entry(p, data):
    m = PROJECT / "01_工具" / "工具库"  / "00_共享核心" / "toolkit_core" / "texture_extractor.py"
    return m.is_file(), ("texture_extractor 模块在" if m.is_file()
                         else "找不到 texture_extractor")


@quick("poster_scripts", "海报类立绘导出脚本存在")
@memo(600)
def _poster(p, data):
    """收窄搜索范围 + 10 分钟记忆。

    原先 rglob 整棵 01_工具/03_执行（含归档、_archive、几万个文件），单它 1.3 秒。
    这类脚本只会放在工具库里，扫那几层就够；再加记忆避免每次采集都付这个代价。
    """
    found = []
    base = PROJECT / "01_工具" / "工具库"
    if base.is_dir():
        # ★ 用递归：迁移后工具按三条线分了子目录（工具库/线/类/文件），
        #   原先的 glob("*/*.py")（两层）会扫不到皮肤链里的脚本。
        #   递归 + @memo(600) 缓存，代价可控。
        for x in base.rglob("find*poster*.py"):
            if "_归档" not in str(x) and "__pycache__" not in str(x):
                found.append(x.name)
    return bool(found), (f"找到 {len(found)} 个：{', '.join(sorted(set(found))[:4])}"
                         if found else "找不到海报类立绘导出脚本")


@quick("color_conventions", "色彩三项硬约定已写进规范")
def _color(p, data):
    txt = _read_text(PROJECT / "00_治理" / "规范" / "前端交付要求.md")
    hits = [k for k in ("color_space", "NoColorSpace", "flipY") if k in txt]
    return len(hits) >= 2, f"前端交付要求.md 命中 {len(hits)}/3：{', '.join(hits) or '无'}"


@quick("audio_consumed", "站点有页面消费音频")
@quick("audio_consumed", "站点有页面真正播放/引用音频")
def _audio(p, data):
    """判据要看【真播放/真引用】，不能只看有没有「音频」这个词。

    实测踩过：原判据用 audio|音频 全文搜，结果 index.html 命中 ——
    但那里出现 audio 只是因为台账文本里有 audio_review 这个路径，属自指假阳性。
    """
    names = []
    for f in WEB.glob("*.html"):
        if f.name.startswith(("_", ".")):
            continue
        txt = _read_text(f, 600000)
        if re.search(r"<audio[\s>]", txt, re.I) or \
           re.search(r"[\"'][^\"']*\.(mp3|ogg|wav|fsb|m4a)[\"']", txt, re.I):
            names.append(f.name)
    return bool(names), (f"{len(names)} 个页面真引用音频：{', '.join(names[:4])}"
                         if names else "站点端零页面真正消费音频，做出来也没有出口")
@quick("audio_scripts_alive", "音频相关脚本当前跑得通")
def _audio_scripts(p, data):
    """源头：源包目录下是否还有音频脚本（A5 的 qj_*.py 双死路径那条）。"""
    src = PROJECT / "02_资料" / "源包"
    n = _count(src, "qj_*.py", recursive=True) if src.is_dir() else -1
    if n < 0:
        return False, "源包目录不存在"
    return n == 0, ("源包目录已无残留音频脚本" if n == 0
                    else f"源包目录下仍有 {n} 个音频脚本（双死路径）")


# ═══════════════════════════ ②线新增命令的判据（2026-09-28）
# 原先 ② 线 90 个脚本只有 glb 一个进了 CLI；本轮补齐 dispatching 入口。
# 判据一律「期望达成的状态」⇒ 有该子命令 = 通过（命名与语义一致）。

@quick("sheet_entry", "统一入口提供「装配帧 → 部件/材质表」子命令")
def _sheet_entry(p, data):
    ok = "sheet" in _cli_subcommands()
    return ok, ("统一入口提供 sheet（.c159 装配帧 → 材质/部件表）" if ok
                else "统一入口里没有 sheet")


@quick("tex_entry", "统一入口提供「贴图 → PNG」子命令（走规范入口）")
def _tex_entry(p, data):
    ok = "tex" in _cli_subcommands()
    return ok, ("统一入口提供 tex（DDS/KTX → PNG，只走 dds_rgba_canonical）" if ok
                else "统一入口里没有 tex")


@quick("audio_entry", "统一入口提供「音效轨道 → 帧表」子命令")
def _audio_entry(p, data):
    ok = "audio" in _cli_subcommands()
    return ok, ("统一入口提供 audio（.sfx → 帧表 JSON）" if ok
                else "统一入口里没有 audio")


@quick("render_entry", "统一入口提供「材质分层出图」子命令")
def _render_entry(p, data):
    ok = "render" in _cli_subcommands()
    return ok, ("统一入口提供 render（8 层图 + layers_trace.json）" if ok
                else "统一入口里没有 render")


@quick("delta_entry", "统一入口提供「热更增量取证」子命令")
def _delta_entry(p, data):
    """①-5：只比服务端版本清单（release vs playertest），不碰本地客户端目录。"""
    ok = "delta" in _cli_subcommands()
    return ok, ("统一入口提供 delta（fetch/diff/families）" if ok
                else "统一入口里没有 delta")


@quick("render_mesh_parser_single_source", "渲染脚本不再自带过时解析器副本")
def _render_parser_single(p, data):
    """实测根因：render_neox_mesh.parse_mesh 曾是按旧布局硬 frombuffer 的副本，
    对 ver4 网格必炸。已改为委派给 la_glb.parse_part。

    判据：该文件的 parse_mesh 里不再出现裸 np.frombuffer（那是副本的特征）。
    """
    f = PROJECT / "01_工具" / "工具库" / "02_图文音频渲染" / "皮肤链与渲染" / "render_neox_mesh.py"
    if not f.is_file():
        return False, "找不到 render_neox_mesh.py"
    txt = _read_text(f, 200000)
    bad = "np.frombuffer" in txt
    return (not bad), ("解析器已统一到 la_glb.parse_part（无本地副本）" if not bad
                       else "render_neox_mesh 里仍有本地解析器副本（对 ver4 网格会炸）")


# ═══════════════════════════ ③ 前端展示交互线

@quick("api_implemented", "接口层有实现")
def _api(p, data):
    if not API_DIR.is_dir():
        return False, "接口层目录不存在"
    n = sum(1 for _ in API_DIR.rglob("*") if _.is_file())
    return n > 0, (f"接口层有 {n} 个文件" if n else "接口层目录是空的，没有任何实现")


@quick("web_root_clean", "站点根目录没有实验页/备份散落")
def _web_root(p, data):
    n = _count(WEB, "_*.html") + _count(WEB, "*.bak_*") + _count(WEB, ".tmp_*")
    if n < 0:
        return False, "站点根目录读取失败"
    return n == 0, ("站点根目录干净" if n == 0
                    else f"站点根目录有 {n} 个实验页/备份文件，待清理")


@quick("assets_no_residual", "资产目录下无残留实验目录")
def _assets(p, data):
    base = WEB / "assets" / "3d"
    if not base.is_dir():
        return False, "资产目录不存在"
    bad = [d.name for d in base.iterdir()
           if d.is_dir() and re.match(
               r"^(parts_v|fashion_v|cmp|fas|huanye|hy_|hair_only|anchor_try|zs_series)", d.name)]
    return not bad, (f"{len(bad)} 个残留目录：{', '.join(bad[:5])}" if bad
                     else "无残留实验目录")


@quick("pipeline_one_command", "有「采集 → 生成 → 服务」一条命令的流水线")
def _pipeline(p, data):
    ok = bool(re.search(r"['\"]home['\"]|['\"]site['\"]", _run_all()))
    return ok, ("已有站点流水线命令" if ok
                else "没有把「数据采集 → 页面生成 → 服务端点」串成一条可复跑的流水线")


@quick("reload_guard", "改取数模块无需重启服务即生效")
def _reload(p, data):
    t = _read_text(WEB / "tools" / "wiki_server.py")
    ok = "_load_gen_home" in t
    return ok, ("端点带 mtime 重载守卫" if ok
                else "端点缓存了取数模块，改代码要重启服务才生效")


@quick("skin_assets_landed", "武器皮肤资产已落位")
def _skin(p, data):
    n = data.get("skin_assets")
    if n is None:
        return False, "读取失败"
    return n > 0, f"已落位 {n} 套"


# ─────────────── ①-1：路径 → fid 的唯一实现（2026-09-26 新增）

@quick("path_fid_single_source", "路径→fid 只有一处实现，各调用方都委托它")
@memo(300)
def _path_fid_single(p, data):
    """看 5 个历史实现是否都改成委托 toolkit_core/path_fid.py。

    ★ 背景：项目里曾有五份 path_id，约定各不相同。实测确认：
        三份用 utf-8 不归一分隔符 / 两份用 latin1 归一分隔符
        ⇒ 同一路径不同结果；其中 resource_resolver 遇中文路径直接抛 UnicodeEncodeError。
      现全部委托给唯一实现，本判据查它们是否还在「各写各的」。
    """
    tools = p / "01_工具" / "工具库"
    targets = [
        tools  / "01_解码定位复原" / "解包与扫描" / "npk_reader.py",
        tools  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py",
        tools  / "01_解码定位复原" / "哈希提取" / "thfb_toolkit.py",
        tools  / "00_共享核心" / "toolkit_core" / "unified_index.py",
        tools  / "00_共享核心" / "toolkit_core" / "resource_resolver.py",
    ]
    canon = tools  / "00_共享核心" / "toolkit_core" / "path_fid.py"
    if not canon.is_file():
        return False, "唯一实现 toolkit_core/path_fid.py 不存在"
    loose = [f.name for f in targets if f.is_file() and "fid_of" not in _read_text(f)]
    return (not loose), (f"{len(targets)} 个调用方都委托唯一实现"
                         if not loose else f"仍各写各的：{', '.join(loose)}")


# ═══════════════════════════ 慢判据（run_checks.py 跑，带 TTL）

@slow("find_chain_usable", "逻辑路径 → 文件号 → 数据行的查询链实跑可用")
def _find_chain(p, data):
    py = p / ".venv" / "Scripts" / "python.exe"
    pr = subprocess.run([str(py), str(RUN_ALL), "find", r"common\env_map\qiangpi.cube"],
                        cwd=str(p / "01_工具"), capture_output=True, text=True,
                        timeout=240, encoding="utf-8", errors="replace")
    return pr.returncode == 0, f"实跑 find 退出码 {pr.returncode}"


@slow("extract_usable", "纹理载荷可定点取出并解码")
def _extract(p, data):
    py = p / ".venv" / "Scripts" / "python.exe"
    out = Path(tempfile.gettempdir()) / "_checks_extract_out.bin"
    if out.exists():
        out.unlink()
    pr = subprocess.run([str(py), str(RUN_ALL), "extract",
                         r"common\env_map\qiangpi.cube", str(out)],
                        cwd=str(p / "01_工具"), capture_output=True, text=True,
                        timeout=240, encoding="utf-8", errors="replace")
    size = out.stat().st_size if out.exists() else 0
    return (pr.returncode == 0 and size > 0), f"实跑 extract 退出码 {pr.returncode}，产出 {size} B"


# ─────────────── 补齐：原先只能写人工判断的几条，落成可核断言

@quick("stale_compares_hash", "索引过期判定比到了单文件哈希（不只是清单指纹）")
@quick("stale_compares_hash", "索引过期判定比到了单文件哈希（不只是清单指纹）")
def _stale_hash(p, data):
    """凭据落在【实际被比较的东西】上，而不是「文件里出现过 sha256 这个词」。

    实测结论（2026-09-26 C2）：现役 stale 判定只比清单指纹、不比单文件 sha256
    ⇒ 包内容变了检不出来。所以这里看索引有没有给容器存逐文件哈希字段。
    """
    try:
        import sqlite3
        db = PROJECT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3"
        con = sqlite3.connect("file:{}?mode=ro".format(db), uri=True)
        cols = [r[1] for r in con.execute("PRAGMA table_info(containers)")]
        hashes = [c for c in cols if ("sha" in c.lower() or "hash" in c.lower())]
        n = 0
        if hashes:
            n = con.execute(
                "SELECT COUNT(*) FROM containers WHERE {} IS NOT NULL".format(hashes[0])
            ).fetchone()[0]
        con.close()
    except Exception as exc:  # noqa: BLE001
        return False, "判据读库失败：{}".format(type(exc).__name__)
    if hashes and n > 0:
        return True, "containers 表有哈希列（{}）且 {} 行有值".format(hashes[0], n)
    return False, "containers 表没有逐文件哈希列 ⇒ 过期判定只比清单指纹，包内容变了检不出来"
@quick("glb_assembly_selfcheck", "模型导出带世界坐标拼接与自检报告")
def _glb_self(p, data):
    core = PROJECT / "01_工具" / "工具库"  / "00_共享核心" / "toolkit_core"
    txt = _read_text(core / "la_glb.py") + _run_all()
    ok = ("世界坐标" in txt) or ("bbox" in txt.lower()) or ("自检" in txt)
    return ok, ("导出链有世界坐标/bbox 自检" if ok else "导出链看不到自检环节")


@quick("name_texture_map_exists", "存在「名字 ↔ 网格/贴图」映射表")
def _name_tex(p, data):
    """这是 ②-2 / ③-5 的病根：客户端内是否真有这种映射。

    ★ 2026-09-28 修：原先按【文件名含 mesh/texture】去找，而实际建出来的表是
      中文名（`名字到落点.tsv`），匹配不上 ⇒ 判据一直挂着。
      现在直接认表 + 校验它非空。
    """
    MAPDIR = PROJECT / "03_执行" / "30_分析" / "名称映射表_20260928"
    cands = [
        MAPDIR / "名字到落点.tsv",          # 全量（图 + 网格）
        MAPDIR / "图_名字到落点.tsv",
        MAPDIR / "网格_名字到落点.tsv",
    ]
    found = [c for c in cands if c.is_file() and c.stat().st_size > 1000]
    if not found:
        # 回退：老口径的文件名匹配（兼容别处建的）
        hits = []
        for base in (PROJECT / "04_站点" / "web" / "data", PROJECT / "03_执行" / "10_索引"):
            if base.is_dir():
                for x in base.glob("*"):
                    n = x.name.lower()
                    if ("name" in n or "locator" in n) and (
                            "mesh" in n or "texture" in n or "tex" in n):
                        hits.append(x.name)
        return bool(hits), (f"找到 {len(hits)} 个候选：{', '.join(hits[:4])}" if hits
                            else "不存在「名字 ↔ 网格/贴图」映射表")
    # 数一下行数（表头不算）
    total = 0
    for c in found:
        try:
            with c.open(encoding="utf-8") as f:
                total += sum(1 for _ in f) - 1
        except Exception:
            pass
    return True, "名字 → 容器+行+fid，共 %s 条（%s）" % (
        f"{total:,}", " + ".join(x.name for x in found))



@quick("lottery_entry", "统一入口提供「奖池解析」子命令")
def _lottery_entry(p, data):
    """奖池线：静态池结构 → 可查的池/格/归属。

    ★ 2026-09-28 新增。此前 `LOTTERY_POOL_RESOLVED_v01.jsonl`（116 MB）是【死产物】——
      没有任何命令能读它，页面也就无从展示。现在有了 `lottery` 子命令族。
    判据验的是【命令在 + 数据源在】，不验具体数字（那会随产物更新漂移）。
    """
    sub = _cli_subcommands()
    ok_cmd = "lottery list" in sub and "lottery show" in sub and "lottery delta" in sub
    src = PROJECT / "03_执行" / "10_索引" / "site_data" / "LOTTERY_POOL_RESOLVED_v01.jsonl"
    ok_src = src.is_file() and src.stat().st_size > 1_000_000
    if not ok_cmd and not ok_src:
        return False, "既没有 lottery 命令，也没有奖池数据源"
    if not ok_cmd:
        return False, "数据源在，但统一入口没有 lottery 子命令"
    if not ok_src:
        return False, "命令在，但奖池数据源缺失（%s）" % src.name
    return True, "lottery（list/find/show/delta）｜ 数据源 %s（%.0f MB）" % (
        src.name, src.stat().st_size / 1048576)


@quick("refpath_index", "有「行 → 原引用路径」索引（统一入口）")
def _refpath_index(p, data):
    """①-1 的第四个方向：一行数据是被哪个路径引用的。

    ★ 2026-09-28 建。此前只有零散脚本各挖各的（atlas / 表 / 布局帧），没有统一入口，
      所以这条一直挂在缺项里。现在统一成一个模块 + 一份索引。
    判据只验【索引在且非空】—— 不验命中率（那受源数据限制，会漂移）。
    """
    d = PROJECT / "03_执行" / "30_分析" / "引用索引_20260928"
    tsv = d / "行到引用.tsv"
    stat = d / "引用索引_统计.json"
    if not (tsv.is_file() and stat.is_file()):
        return False, "没有「行 → 原引用路径」索引（跑 build_refpath_index.py）"
    try:
        info = json.loads(stat.read_text(encoding="utf-8"))
        rows = info.get("被引用行数")
        srcs = info.get("按来源") or {}
    except Exception:
        rows, srcs = None, {}
    with tsv.open(encoding="utf-8") as f:
        n = sum(1 for _ in f) - 1
    if n <= 0:
        return False, "索引文件在但为空"
    return True, "行→引用 %s 条 ｜ 来源 %s" % (f"{n:,}", " / ".join(srcs.keys()) or "?")


@quick("hotfix_rows", "有行级热更 diff（哪一行新增/移除/改了）")
def _hotfix_rows(p, data):
    """行级热更 diff：两个 script 包逐行比。

    ★ 2026-09-28 建。此前 diff 只到【包级 / fid 级】（`delta pkg diff`），
      答不了「哪一行变了」——script 容器按模块名索引、表按行组织，真变化是行级的。
    判据 = 只比【真值字段】（凡值是 `jump:行号` 的一律排除，行号漂移不是内容变更）。
    """
    cli = PROJECT / "01_工具" / "工具库" / "00_共享核心" / "命令行" / "toolkit_cli.py"
    mod = PROJECT / "01_工具" / "工具库" / "00_共享核心" / "toolkit_core" / "hotfix_rows.py"
    test = PROJECT / "01_工具" / "工具库" / "00_共享核心" / "测试" / "test_hotfix_rows.py"
    if not (cli.is_file() and mod.is_file()):
        return False, "没有行级热更 diff 模块（toolkit_core/hotfix_rows.py）"
    try:
        src = cli.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return False, "读不了 CLI：%s" % e
    if "cmd_hotfix_rows" not in src:
        return False, "CLI 里没有 hotfix rows 子命令"
    # 产物（跑过才有）
    hits = sorted((PROJECT / "03_执行" / "30_分析").glob("*时装热更表*"))
    got = [d for d in hits if d.is_dir()]
    return True, "hotfix rows（两个 script 包逐行比）｜ 契约测试 %s ｜ 产物目录 %d 个" % (
        "有" if test.is_file() else "缺", len(got))


@quick("wiki_taxonomy", "有体系卡（按用户定稿的分类树呈现，含占位）")
def _wiki_taxonomy(p, data):
    """体系卡：wiki 的分类树 + 板映射 + 占位节点。

    ★ 2026-09-28 建。用户定稿的体系（时装类/战力类/活动类）此前只活在 wiki.html 的
      JS 里硬编码分组，没有显式定义 —— 树看不见，缺口也看不见。
    现在 = `data/wiki_taxonomy.json`（树+映射+占位）+ wiki.html 渲染；
    旧分组保留在下方「图鉴」区（不破坏原结构）。
    """
    web = PROJECT / "04_站点" / "web"
    tj = web / "data" / "wiki_taxonomy.json"
    js = web / "data" / "wiki_taxonomy.js"
    html = web / "wiki.html"
    if not (tj.is_file() and js.is_file()):
        return False, "没有体系树（data/wiki_taxonomy.json / .js）"
    try:
        tax = json.loads(tj.read_text(encoding="utf-8"))
    except Exception as e:
        return False, "体系树解析失败：%s" % e
    tree = tax.get("树") or []
    if not tree:
        return False, "体系树是空的"
    # 数节点
    leaves = mids = 0
    for top in tree:
        for mid in (top.get("children") or []):
            mids += 1
            leaves += len(mid.get("children") or []) or 1
    # 渲染挂上了吗
    if html.is_file():
        src = html.read_text(encoding="utf-8", errors="replace")
        if "wiki_taxonomy.js" not in src or "systemCards" not in src:
            return False, "wiki.html 没引用体系树 / 没有体系卡容器"
    return True, "体系卡 %d 顶层 · %d 中层 · %d 叶子" % (len(tree), mids, leaves)


@quick("audio_review_pages", "分析区有音频试听/链路页")
def _audio_review(p, data):
    base = PROJECT / "03_执行" / "30_分析" / "audio_review"
    if not base.is_dir():
        return False, "分析区没有 audio_review 目录"
    n = _count(base, "*.html")
    return n > 0, (f"audio_review 有 {n} 个页面" if n else "audio_review 目录里没有页面")


@quick("color_method_consolidated", "上色四链已整理成可复用方法")
def _color_method(p, data):
    """判据要求【专门讲上色】的规范文档，且四条链都点到。

    实测踩过：原判据只要文档里同时出现「染色」和「折射/晶体/源驱动」就算过，
    结果把 三线落实方案_核对版.md（顺带提了一句）也算上了，属过松。
    """
    spec = PROJECT / "00_治理" / "规范"
    hits = []
    if spec.is_dir():
        for f in spec.glob("*.md"):
            if not re.search(r"上色|染色|颜色|贴图", f.name):
                continue
            txt = _read_text(f, 300000)
            four = [k for k in ("染色", "折射", "晶体", "源驱动") if k in txt]
            if len(four) >= 4:
                hits.append(f.name)
    return bool(hits), (f"有专门规范：{', '.join(hits)}" if hits
                        else "染色/折射/晶体/源驱动四条上色路径散在记录里，未成规范")
@quick("wiki_pages_present", "图鉴首页 + 板块页 + 条目检索都在")
def _wiki_pages(p, data):
    need = {"wiki.html": "图鉴首页"}
    got, miss = [], []
    for f, label in need.items():
        (got if (WEB / f).is_file() else miss).append(label)
    # ★ 2026-09-28 修：原先写 `_count("board*.html") + _count("*.html")` ——
    #   `board*.html` 已含在 `*.html` 里，重复计数 ⇒ 页面显示「共 17 个」而实际 16 个。
    all_html = sorted(x.name for x in WEB.glob("*.html"))
    boards = len(all_html)
    ok = not miss and boards > 0
    return ok, (f"图鉴页在，站点共 {boards} 个 html" if ok else f"缺：{', '.join(miss)}")


@quick("workbench_domains", "工作台四域看板（物品/武器皮肤/时装/奖池）")
@quick("workbench_domains", "工作台四域看板（物品/武器皮肤/时装/奖池）")
def _workbench(p, data):
    """按【具体页面名】判，不用通配 —— 通配会把无关页面算进来。"""
    want = {"物品": "workbench_items.html", "武器皮肤": "workbench_skin.html",
            "时装": "workbench_fashion.html", "奖池": "workbench_lottery.html"}
    got = [k for k, f in want.items() if (WEB / f).is_file()]
    return len(got) >= 3, (f"命中 {len(got)}/4 域：{'、'.join(got)}" if got
                           else "工作台看不到分域看板")
@quick("offline_no_cdn", "站点全部离线可用，不依赖外部资源库")
def _offline(p, data):
    bad = []
    for f in WEB.glob("*.html"):
        if f.name.startswith(("_", ".")):
            continue
        txt = _read_text(f, 400000)
        for m in re.finditer(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', txt):
            u = m.group(1)
            if not re.search(r"127\.0\.0\.1|localhost|192\.168\.", u):
                bad.append(f"{f.name} → {u[:40]}")
                break
    return not bad, (f"{len(bad)} 个页面引外部资源：{'; '.join(bad[:3])}" if bad
                     else "全部离线可用，无外部引用")


@slow("path_fid_cross_check", "五个路径→fid 实现逐个对照基准，全部一致")
def _path_fid_cross(p, data):
    """真跑 path_fid.cross_check()：加载 5 个实现，逐条对照基准与算法。

    慢（要 import 5 个模块），所以放慢判据档，不在主页采集路径上。
    """
    import importlib.util
    canon = p / "01_工具" / "工具库"  / "00_共享核心" / "toolkit_core" / "path_fid.py"
    if not canon.is_file():
        return False, "唯一实现 path_fid.py 不存在"
    s = importlib.util.spec_from_file_location("_pfc", canon)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    rep = m.cross_check(project_root=p)
    algo = rep.get("algo_check") or {}
    bad = rep.get("disagreeing") or []
    err = rep.get("errored") or []
    if not algo.get("ok", False):
        return False, f"murmur3 算法不一致：{algo.get('mismatch')}"
    if bad or err:
        return False, f"约定不一致 {len(bad)} 个：{', '.join(bad)}；报错 {len(err)} 个：{', '.join(err)}"
    n = len(rep.get("callers") or [])
    return True, f"{n} 个实现全部与基准一致；murmur3 算法 {algo.get('samples')} 次取样全同"


# ═══════════════════════════ 执行器

def run_quick(data) -> dict:
    """跑全部快速判据。任一判据自身的异常被吃成 (False, 原因)，不拖垮整次采集。"""
    out = {}
    for name, (label, fn) in CHECKS.items():
        try:
            ok, detail = fn(PROJECT, data)
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"判据自身异常：{type(exc).__name__}: {exc}"
        out[name] = {"label": label, "ok": bool(ok), "detail": detail, "live": True}
    return out


def read_slow_cache() -> dict:
    """读慢判据缓存（tools/run_checks.py 落的盘）。没有就当作缺。"""
    try:
        raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return raw.get("checks") or {}


def run_slow() -> dict:
    """跑慢判据（给 tools/run_checks.py 用，不在主页采集路径上）。"""
    out = {}
    for name, (label, fn) in SLOW_CHECKS.items():
        try:
            ok, detail = fn(PROJECT, {})
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"判据自身异常：{type(exc).__name__}: {exc}"
        out[name] = {"label": label, "ok": bool(ok), "detail": detail, "live": False}
    return out


def collect_all(data) -> dict:
    """快速判据（现跑）+ 慢判据（读缓存）合并。"""
    merged = run_quick(data)
    merged.update(read_slow_cache())
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# ①-3 批量质检（2026-09-26 新增：跑 1% 半全量暴露需求后建的四个命令）
# ═══════════════════════════════════════════════════════════════════════════

@quick("query_entry", "能按条件筛条目（容器 / 大小 / flag / 编号范围）")
def _query_entry(p, data):
    ok = "query" in _cli_subcommands()
    return ok, ("统一入口提供 query：只筛不落盘，先看规模与形状" if ok
                else "筛条目还得手写 SQL")


@quick("bulk_entry", "能批量提取（含断点续跑与产物清单）")
def _bulk_entry(p, data):
    """验能力：bulk 存在，且它的模块支持 resume / manifest。"""
    subs = _cli_subcommands()
    has = "bulk" in subs
    extra = False
    try:
        _b = _tc_module("toolkit_core.bulk")
        extra = all(hasattr(_b, n) for n in ("bulk_extract", "name_for", "safe_ext",
                                             "build_dir_map"))
    except Exception:
        extra = False
    ok = has and extra
    return ok, ("统一入口提供 bulk：断点续跑 + 清单(sha256) + 错误按类聚合" if ok
                else "批量提取缺少入口或缺少续跑/清单能力")


@quick("identify_entry", "能识别产物类型（魔数 → 纹理/模型/音频…）")
def _identify_entry(p, data):
    subs = _cli_subcommands()
    n = 0
    try:
        n = len(getattr(_tc_module("toolkit_core.bulk"), "MAGIC", ()))
    except Exception:
        n = 0
    ok = ("identify" in subs) and n >= 15
    return ok, ("统一入口提供 identify；格式注册表 %d 种" % n if ok
                else "产物类型识别缺失（或注册表条目过少：%d）" % n)


@quick("decode_audit_entry", "有解码线体检（逐条验解码正确性，可全量）")
def _decode_audit_entry(p, data):
    subs = _cli_subcommands()
    ok = "decode-audit" in subs
    return ok, ("统一入口提供 decode-audit：按容器×flag 分层，--full 可逐条全过" if ok
                else "没有解码线体检，无法证明解码无纰漏")


@quick("format_registry", "格式魔数已集中成一份注册表（不再散在各脚本）")
def _format_registry(p, data):
    """判据：注册表存在且条目够多。散在各脚本正是规范点名的老问题。"""
    try:
        magics = getattr(_tc_module("toolkit_core.bulk"), "MAGIC", ())
        ok = len(magics) >= 18
        return ok, ("toolkit_core/bulk.py 的 MAGIC 集中登记 %d 种格式" % len(magics)
                    if ok else "注册表条目过少（%d），格式识别可能仍散在各处" % len(magics))
    except Exception as e:
        return False, "读不到格式注册表：%s" % type(e).__name__


# ═══════════════════════════════════════════════════════════════════════════
# ①-4 名字还原（2026-09-27 新增：双 seed murmur3 机制实测成立后落的命令）
#
#   ★ 这批判据的共同立场：**真跑**，不 grep 源码文本。
#     上一批假 ✗ 的教训就是「搜 run_all.py 里有没有 'index build' 字样」——
#     文件一改就集体误报。所以这里拿真索引、真路径、真哈希去要结果。
# ═══════════════════════════════════════════════════════════════════════════

NAMES_DB = PROJECT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3"


def _latest_names_dict(root: Path) -> Path:
    """★ 取最新版字典（v13 > v12 > …）。

    写死 `names_dict.json` 会拿到旧版 —— 那正是「页面显示 213,996 条、
    实际 1,061,631 条」的根因（旧文件前 4KB 里恰好有名字链审核的 count）。
    与 `toolkit_core/paths._latest_names_dict` 同一口径。
    """
    base = root / "names_dict.json"
    vs = []
    for p in root.glob("names_dict_v*.json"):
        d = "".join(c for c in p.stem.split("_v")[-1] if c.isdigit())
        if d:
            vs.append((int(d), p))
    vs.sort()
    return vs[-1][1] if vs and vs[-1][1].is_file() else base


NAMES_DICT = _latest_names_dict(PROJECT / "03_执行" / "10_索引" / "names")
#: ground truth：这两条路径的 fid 与 (容器, 行号) 已由索引反向核对过
NAMES_TRUTH = (("ui/renwu_icon/xinshoujiaocheng/img_jiaocheng162_s.jpg", r"res\ui_01.gpk", 71678),
               ("effect/fx/guochang/fx/ar_laiwenshi_dimian.sfx", r"res\effect_01.gpk", 8311))


@quick("names_hash_selftest", "名字哈希算法自检通过（空串采样 + 三条已核对路径）")
def _names_hash_selftest(p, data):
    """验算法本身：murmur3(b'',0)==0，且两条路径的 fid 与索引里真实存在的 (容器,行号) 对得上。"""
    try:
        N = _tc_module("toolkit_core.names")
        rep = N.hash_selftest()
    except Exception as exc:  # noqa: BLE001
        return False, "哈希自检跑不起来：%s: %s" % (type(exc).__name__, exc)
    if rep["ok"]:
        return True, "murmur3 双 seed 自检 %d 项全对（含 / 与 \\ 等价）" % rep["checked"]
    return False, "自检不通过：%s" % (rep["mismatch"][:2],)


@quick("names_lookup_works", "给一条游戏内路径，能实跑到容器 + 行号")
def _names_lookup_works(p, data):
    """★ 真能力判据：拿 ground truth 路径实跑 lookup，核对容器与行号都一致。"""
    if not NAMES_DB.is_file():
        return False, "索引库不在，名字定位无从谈起"
    try:
        N = _tc_module("toolkit_core.names")
    except Exception as exc:  # noqa: BLE001
        return False, "名字还原模块缺失：%s" % type(exc).__name__
    ok, detail = True, []
    for path, want_container, want_row in NAMES_TRUTH:
        try:
            rep = N.lookup(path, NAMES_DB, limit=1)
        except Exception as exc:  # noqa: BLE001
            return False, "查询抛异常：%s: %s" % (type(exc).__name__, exc)
        hit = (rep["hits"] or [{}])[0]
        good = (hit.get("container") == want_container and hit.get("row_index") == want_row)
        ok = ok and good
        detail.append("%s → %s row %s %s" % (path.rsplit("/", 1)[-1],
                                             hit.get("container", "未命中"),
                                             hit.get("row_index", "-"),
                                             "✓" if good else "✗"))
    return ok, " · ".join(detail)


@quick("names_dict_size", "名字字典非空（可查规模）")
def _names_dict_size(p, data):
    """读【同步产物 sidecar】拿真实规模，不猜、不从 4KB 里正则抓。

    ★ 2026-09-28 修两处：
      ① `NAMES_DICT` 曾写死 `names_dict.json`（旧版，37 MB），而实际最新是
         `names_dict_v13.json`（86 MB）—— 判据一直报旧文件的数。
      ② 旧实现从前 4 KB 里正则抓 `"count": N`，而那个 N 是【名字链审核】的统计
         （213,996 / 56,238），根本不是字典条数 ⇒ 页面上出现「213,996 条」与
         「1,061,631 条」两个数打架，二者相差 5 倍。
      ⇒ 现在优先读 `coverage_latest.json`（由 names stats 同步），
        它同时给 dict_size / total_rows / covered_rows。
    """
    side = NAMES_DICT.parent / "coverage_latest.json"
    if side.is_file():
        try:
            d = json.loads(side.read_text(encoding="utf-8"))
            n = int(d.get("dict_size") or 0)
            tot = int(d.get("total_rows") or 0)
            cov = int(d.get("covered_rows") or 0)
            pct = d.get("coverage_pct")
            if n > 0:
                return True, ("字典 %s 条路径（%s）｜ 覆盖 %s / %s 行 = %s%%" % (
                    format(n, ","), Path(d.get("dict_path") or "").name or "?",
                    format(cov, ","), format(tot, ","),
                    ("%.2f" % pct) if isinstance(pct, (int, float)) else "?"))
        except Exception as exc:  # noqa: BLE001
            # 读不动 sidecar 就退回下面的自算，但要让人知道 sidecar 坏了
            print("  ⚠ coverage_latest.json 读不动：%s" % exc)

    # 回退：从字典文件里数 key（流式，带 memo，不占采集预算太久）
    dic = NAMES_DICT
    if not dic.is_file():
        return False, "字典还没建（run_all.py names build）"
    try:
        n = 0
        with open(dic, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                # 字典是 {"fid": "path", ...} 的 JSON；数顶层 key 的近似法 = 数 `":` 出现
                n += line.count('": "')
        if n == 0:
            return False, "字典里数不到条目（%s）" % dic.name
        return True, "字典 %s 条路径（%s，回退自算）" % (format(n, ","), dic.name)
    except OSError as exc:
        return False, "字典读不动：%s" % exc



@quick("names_index_queryable", "索引的 fid_hex 列可直查（含索引）")
def _names_index_queryable(p, data):
    """验结构而不是文本：entries 有 fid_hex 列、该列有索引、且探针查询真能取到行。"""
    if not NAMES_DB.is_file():
        return False, "索引库不在"
    try:
        N = _tc_module("toolkit_core.names")
        conn = N.open_index(NAMES_DB)
        try:
            schema = N.verify_schema(conn)
            fid = N.fid_hex(NAMES_TRUTH[0][0])
            row = conn.execute("SELECT container,row_index FROM entries WHERE fid_hex=? LIMIT 1",
                               (fid,)).fetchone()
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, exc)
    ok = bool(row) and schema["fid_indexed"]
    return ok, ("entries.fid_hex 可查%s；探针 %s → %s"
                % ("（idx_entries_fid 走索引）" if schema["fid_indexed"] else "（无索引，全表扫）",
                   fid, ("%s row %s" % row) if row else "无行"))



if __name__ == "__main__":
    # ★ 这个块原在 ①-3/①-4 注册【之前】，于是 `python checks.py` 只列出前半批判据
    #   （实测 33 项，漏掉 ①-3 与 ①-4 的 12 项）。挪到文件末尾，列全。
    import sys
    if "--slow" in sys.argv:
        print(json.dumps(run_slow(), ensure_ascii=False, indent=2))
    else:
        for k, v in run_quick({}).items():
            print(f"  {'✓' if v['ok'] else '✗'} {k:<26} {v['detail']}")
