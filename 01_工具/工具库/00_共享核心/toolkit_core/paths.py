# -*- coding: utf-8 -*-
"""新拆包器核心：所有派生产物只能写到 EXE 同级或用户显式选择的外置目录。

## 项目根怎么定位（四优先级，2026-09-26 起不再硬编码）

  1. 命令行 `--root <path>`
  2. 环境变量 `LA_ROOT`
  3. 可执行文件同级**向上**找项目标记（打包后 EXE 放哪都能找到）
  4. 源码树推断：`__file__` 向上找项目标记（**仅开发期**）

  标记 = 同时存在 `<root>/00_治理/索引.md` 与 `<root>/01_工具/工具库`
         （规格里原写 `00_治理/MANIFEST.md`，该文件 2026-09-26 已改名 `索引.md`）

  **找不到就明确报错，不猜。** 报错里列出找过的每个位置，便于排查。

## 为什么原来是硬伤

旧版第 8 行 `PROJECT_ROOT = Path(r"E:/la拆包项目").resolve()` 是**唯一单点**
（`OUTPUT_ROOT` / `INDEX_ROOT` 全基于它）：项目搬家、换机、EXE 分发 → 全废。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

MARKER_DIR = "00_治理"
MARKER_FILE = "索引.md"
# ★ 判据里必须是【相对根的完整子路径】。原先写 ("01_工具", "工具库") 是错的 ——
#   `工具库` 在 `01_工具/工具库` 下，不在根上，于是根上判据恒为假、
#   连真实项目根都认不出来（实测四优先级全失败）。
MARKER_SIBLING = ("01_工具/工具库",)


class ProjectRootNotFound(RuntimeError):
    """四种定位方式都失败时抛出 —— 明确报错，不猜。"""


def _looks_like_root(p: Path) -> bool:
    try:
        if not (p / MARKER_DIR / MARKER_FILE).is_file():
            return False
        return all((p / s).is_dir() for s in MARKER_SIBLING)
    except OSError:
        return False


def find_project_root(cli_root: Optional[Path | str] = None) -> Path:
    """按四优先级定位项目根。找到就返回，找不到抛 ProjectRootNotFound。"""
    tried: list[str] = []

    # ① 显式传入（命令行 --root 的落地方式）
    # ★ 显式给了却不合法 ⇒ 【直接报错，不往下回退】。
    #   否则用户以为在 A 项目上跑，实际跑在 B 项目上 —— 这正是「不猜」要防的。
    if cli_root:
        p = Path(cli_root).resolve()
        if _looks_like_root(p):
            return p
        raise ProjectRootNotFound(
            "① 命令行 --root = %s 不是项目根。\n"
            "判据：该目录下须同时有 `%s/%s` 与 `%s`。\n"
            "⇒ 显式指定的根无效时不会回退到自动探测（免得你以为在 A 上跑、实际在 B 上）。"
            % (p, MARKER_DIR, MARKER_FILE, " / ".join(MARKER_SIBLING)))

    # ② 环境变量
    env = os.environ.get("LA_ROOT")
    if env:
        p = Path(env).resolve()
        if _looks_like_root(p):
            return p
        tried.append("② 环境变量 LA_ROOT = %s（不是项目根）" % p)

    # ③ 可执行文件同级向上（打包后 sys.executable 就是 exe 本体）
    import sys
    exe = getattr(sys, "executable", "") or ""
    if exe and str(exe) not in ("", "python", "python.exe"):
        base = Path(exe).resolve().parent
        seen = set()
        for up in [base, *base.parents]:
            if up in seen:
                continue
            seen.add(up)
            if _looks_like_root(up):
                return up
            tried.append("③ exe 同级向上：%s" % up)

    # ④ 源码树推断（仅开发期）
    here = Path(__file__).resolve()
    for up in here.parents:
        if _looks_like_root(up):
            return up
        tried.append("④ 源码树向上：%s" % up)

    raise ProjectRootNotFound(
        "找不到项目根。判据：该目录下须同时有 `%s/%s` 与 `%s`。\n"
        "已尝试：\n  %s\n"
        "⇒ 请用 --root <项目根> 或设环境变量 LA_ROOT 显式指定。"
        % (MARKER_DIR, MARKER_FILE, " / ".join(MARKER_SIBLING),
           "\n  ".join(tried[:12])))


# 模块级常量：保持向后兼容（原先就是这三个名字，全项目在用）
PROJECT_ROOT = find_project_root()
DEFAULT_OUTPUT_ROOT = (PROJECT_ROOT / "03_执行" / "20_提取")
INDEX_ROOT = (PROJECT_ROOT / "03_执行" / "10_索引")

# ── ★★★ 统一产物根（2026-09-29 架构改造：产物根单一来源） ─────────────
#   背景：原先各命令自己拼 `PROJECT_ROOT/"03_执行"/"90_临时"` 这类字符串，
#   结果是「有的读 20_提取、有的读 41_还原树、有的读某次复核副本」，
#   产物过期类 bug 反复出现（实证：奖池产物建于 9/10，9/28 新增的池查不到）。
#
#   改造后的口径：
#     · TREE_ROOT  = 唯一权威产物（按路径的还原树）★ 一切读产物优先走它
#     · EXTRACT_ROOT = 初拆载荷，**可重建**；二拆校验通过后可清理
#     · 其余为分析/临时/待删/审阅/站点/源包，各有明确角色
TREE_ROOT = (PROJECT_ROOT / "03_执行" / "41_还原树")
EXTRACT_ROOT = DEFAULT_OUTPUT_ROOT                     # 初拆（= 03_执行/20_提取）
ANALYSIS_ROOT = (PROJECT_ROOT / "03_执行" / "30_分析")
TEMP_ROOT = (PROJECT_ROOT / "03_执行" / "90_临时")
PENDING_DELETE_ROOT = (PROJECT_ROOT / "03_执行" / "95_待清理")
REVIEW_ROOT = (PROJECT_ROOT / "03_执行" / "96_审阅区")
SITE_ROOT = (PROJECT_ROOT / "04_站点")
SOURCE_PKG_ROOT = (PROJECT_ROOT / "02_资料" / "源包")
GOVERNANCE_ROOT = (PROJECT_ROOT / "00_治理")


def tree_file(rel: str | Path) -> Path:
    """还原树里的一个文件路径（把 `/` 或 `\\` 分隔的相对路径接上 TREE_ROOT）。

    ★ 读产物一律走这里，别在调用点拼 `PROJECT_ROOT/"03_执行"/"41_还原树"/...`。
    """
    return TREE_ROOT / str(rel).replace("/", os.sep).replace("\\", os.sep)


def cdata_dir() -> Path:
    """`com\\cdata` 配置表目录（★ 新层级，对标 E:\\mrzh 之后）。

    层级：`<树>/<容器>/com/cdata/`；同名表每容器一份 ⇒ 取【Documents 层 script 容器】
    （= 当前态），取不到再退底座容器，最后才退老扁平（迁移期兜底，正常不会走到）。
    所有「要个 cdata 目录」的调用方都走这里，别再各自拼 `TREE_ROOT/"com"/"cdata"`。
    """
    try:
        from toolkit_core import table_locator as _TL      # 懒导入，避免循环依赖
        dirs = _TL.cdata_dirs()
        if dirs:
            return Path(dirs[0])
    except Exception:                                      # noqa: BLE001
        pass
    for rel in (("Documents", "script.py314.lc.npk"), ("script.py314.lc.npk",)):
        p = TREE_ROOT.joinpath(*rel) / "com" / "cdata"
        if p.is_dir():
            return p
    return TREE_ROOT / "com" / "cdata"


def cdata_table(name: str) -> Path:
    """`com\\cdata` 下一张表在还原树里的路径（如 `desc_info_data_chs.py`）。

    这是「按表名读配置表」的规范入口 —— 与「按容器+行号」那条链并列。

    ★★ 2026-09-30 对标 E:\\mrzh 后修正：**扁平路径不再唯一** ——
      同名表在每个容器里各有一份（`script.py314.lc.npk/com/cdata/…`、
      `Documents/script.py314.lc.npk/com/cdata/…`，内容可能不同）。
      ⇒ 这里必须**按 fid + 层序**解析（overlay/Documents 优先），
        解析不出才退回新层级目录（再不行才老扁平兜底）。
    """
    base = str(name).replace("/", "\\").split("\\")[-1]
    try:
        from toolkit_core import table_locator as _TL      # 懒导入，避免循环依赖
        p = _TL.best_table_path(base)
        if p:
            return Path(p)
    except Exception:                                      # noqa: BLE001
        pass
    d = cdata_dir()
    if (d / base).is_file():
        return d / base
    return TREE_ROOT / "com" / "cdata" / base

# ── ①-4 名字还原：字典的落点与默认开采源 ──────────────────────
#   字典是【产物】不是【源】：统一放 INDEX_ROOT/names，别散在脚本里拼字符串。
NAMES_ROOT = INDEX_ROOT / "names"


def _latest_names_dict(root: Path) -> Path:
    """★ 取最新版字典（v11 > v10 …）。字典迭代了十几版，写死 names_dict.json
    会拿到旧版（覆盖不全），让上层命令「跑了但 0 结果」。"""
    base = root / "names_dict.json"
    vs = []
    for p in root.glob("names_dict_v*.json"):
        d = "".join(c for c in p.stem.split("_v")[-1] if c.isdigit())
        if d:
            vs.append((int(d), p))
    vs.sort()
    return vs[-1][1] if vs and vs[-1][1].is_file() else base


DEFAULT_NAMES_DICT = _latest_names_dict(NAMES_ROOT)
#   默认开采源 = 仓库里现存的「路径文本产物」（只读）。给 --source 时以命令行给的为准。
DEFAULT_NAME_SOURCES = (
    PROJECT_ROOT / "03_执行" / "30_分析" / "_target_1110025" / "public_refs" / "FileNames.list",
    PROJECT_ROOT / "00_治理" / "文档" / "报告与复盘" / "_1110171_结论归档"
    / "_证据数据" / "h16" / "truth_pairs.json",
)


def set_root(path: Path | str) -> Path:
    """运行期改根（给 --root 用）。返回新的项目根。"""
    global PROJECT_ROOT, DEFAULT_OUTPUT_ROOT, INDEX_ROOT, NAMES_ROOT, DEFAULT_NAMES_DICT
    global DEFAULT_NAME_SOURCES, TREE_ROOT, EXTRACT_ROOT, ANALYSIS_ROOT, TEMP_ROOT
    global PENDING_DELETE_ROOT, REVIEW_ROOT, SITE_ROOT, SOURCE_PKG_ROOT, GOVERNANCE_ROOT
    p = find_project_root(path)
    PROJECT_ROOT = p
    DEFAULT_OUTPUT_ROOT = (p / "03_执行" / "20_提取")
    INDEX_ROOT = (p / "03_执行" / "10_索引")
    NAMES_ROOT = INDEX_ROOT / "names"
    DEFAULT_NAMES_DICT = NAMES_ROOT / "names_dict.json"
    # ★ 统一产物根同步（否则 --root 之后 TREE_ROOT 还指着旧根）
    TREE_ROOT = (p / "03_执行" / "41_还原树")
    EXTRACT_ROOT = DEFAULT_OUTPUT_ROOT
    ANALYSIS_ROOT = (p / "03_执行" / "30_分析")
    TEMP_ROOT = (p / "03_执行" / "90_临时")
    PENDING_DELETE_ROOT = (p / "03_执行" / "95_待清理")
    REVIEW_ROOT = (p / "03_执行" / "96_审阅区")
    SITE_ROOT = (p / "04_站点")
    SOURCE_PKG_ROOT = (p / "02_资料" / "源包")
    GOVERNANCE_ROOT = (p / "00_治理")
    DEFAULT_NAME_SOURCES = (
        p / "03_执行" / "30_分析" / "_target_1110025" / "public_refs" / "FileNames.list",
        p / "00_治理" / "文档" / "报告与复盘" / "_1110171_结论归档"
        / "_证据数据" / "h16" / "truth_pairs.json",
    )
    return p


class OutputPolicy:
    """输出目录安全策略，不依赖 PyInstaller 的临时解包目录。"""

    def __init__(self, exe_dir: Optional[Path] = None) -> None:
        # ★ 不再手算 parents[N]：显式给了就用，否则退回项目根
        self.exe_dir = Path(exe_dir).resolve() if exe_dir else PROJECT_ROOT

    @staticmethod
    def _is_relative_to(child: Path, parent: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    def resolve(self, selected: Optional[Path | str], *, source_root: Path | str) -> Path:
        """返回已创建、且永远不落在原始游戏目录内的输出根。"""
        source = Path(source_root).resolve()
        target = (Path(selected) if selected else DEFAULT_OUTPUT_ROOT).resolve()
        if self._is_relative_to(target, source):
            raise ValueError("输出目录不能位于游戏源目录内，请选工具包外置 output")
        if "_MEI" in str(target).upper():
            raise ValueError("输出目录不能位于 PyInstaller 临时目录")
        target.mkdir(parents=True, exist_ok=True)
        for folder in ("jobs", "logs", "exports"):
            (target / folder).mkdir(exist_ok=True)
        return target


def resolve_index_database(*, output_dir: Path, exe_dir: Path, default_root: Path,
                           meipass: Path | None = None) -> Path:
    """索引库发现链：用户输出目录 → exe 同级（内置）→ 默认产物根 → 冻结资源目录。

    未命中的候选都保留原义：返回第一个候选（=输出目录路径），供“重建索引”使用。
    """
    candidates = [Path(output_dir) / "indexes" / "lifeafter_files.sqlite3",
                  Path(exe_dir) / "indexes" / "lifeafter_files.sqlite3",
                  Path(default_root) / "indexes" / "lifeafter_files.sqlite3"]
    if meipass is not None:
        candidates.append(Path(meipass) / "indexes" / "lifeafter_files.sqlite3")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]
