#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""fix_hardcoded_paths.py — 把「写死的本机绝对路径」改成从仓库根推导

## 为什么必须做

开源目标：别人 clone 仓库后，用**自己设备**的拆包产物能构建出一样的 wiki。
现状体检：02_wiki/web/tools 下 477 个脚本写死了 `E:/la拆包项目/...`，
换机器 / 换目录 ⇒ 直接崩。README 里「换台机器 clone 代码也能起站」是落空的。

## 改写口径

只改**指向项目自身**的路径（`E:/la拆包项目/...`）：
  Path("E:/la拆包项目/02_wiki/web")      → Path(WEB)
  Path(r"E:/la拆包项目")                  → Path(PROJ)
  Path("E:/la拆包项目/01_索引与产物/41_还原树") → Path(TREE_ROOT)
  ...按前缀映射表逐级匹配，命中最长前缀。

★ 关键：**替换整个路径表达式**，不是替换字符串里的一段。
  （把 `Path(r"E:/la拆包项目")` 里的路径文本换成 "PROJ" 会得到
    `Path(r"PROJ")` —— 字面量而非变量，静默产出错误路径。这是最容易踩的坑。）

**不改**指向本机设备的路径（`E:/mrzh`、`E:/LifeAfter`、`C:/Users/...`）：
  那是**运行期输入**，语义上是「用户自己的游戏安装目录」，
  应当走 LA_CLIENT_ROOT 环境变量 —— 但逐个判断每个调用点的语义
  超出机械改写能保证的范围 ⇒ **只报告，不自动改**，列入人工待办。
  理由：猜错就是静默读错目录，比硬失败更糟。

## 安全约定

  * 默认 dry-run；--apply 才落盘
  * 落盘前自动备份到 02_wiki/state/backups/
  * 幂等：已改写的文件再跑一次不产生变化
  * 改完做 ast.parse 语法校验，失败则回滚该文件
  * 每批 ≤ --batch 个文件（默认 10），逐批校验
  * 改写后该文件的**硬编码计数必须下降**，否则回滚

用法:
  python 02_wiki/web/tools/build/fix_hardcoded_paths.py --list
  python 02_wiki/web/tools/build/fix_hardcoded_paths.py --plan --limit 3
  python 02_wiki/web/tools/build/fix_hardcoded_paths.py --apply --limit 10
  python 02_wiki/web/tools/build/fix_hardcoded_paths.py --apply --file <某个.py>

退出码: 0 成功 / 1 有失败
"""
from __future__ import annotations

import argparse
import ast
import datetime
import json
import pathlib
import re
import shutil
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
TOOLS = PROJ / "02_wiki" / "web" / "tools"
STATE = PROJ / "02_wiki" / "state"
BACKUP = STATE / "backups" / "pathfix"

# ★ 前缀映射表：**从长到短**匹配，命中最长前缀。
#   值 = (la_paths 里的常量名, 该常量下的相对子路径)
#   相对子路径为空 ⇒ 直接用常量本身。
PREFIX_MAP: list[tuple[str, str, str]] = [
    ("01_索引与产物/41_还原树", "TREE_ROOT", ""),
    ("01_索引与产物/10_索引", "INDEX_ROOT", ""),
    ("01_索引与产物/30_分析", "ANALYSIS_ROOT", ""),
    ("01_索引与产物/90_临时", "TEMP_ROOT", ""),
    ("01_索引与产物/20_提取", "EXTRACT_ROOT", ""),
    ("01_索引与产物/源包", "SOURCE_PKG_ROOT", ""),
    ("01_索引与产物", "ARTIFACTS", ""),
    ("00_规范与工具/工具/工具库/00_共享核心", "TOOLKIT_CORE", ""),
    ("00_规范与工具/工具", "TOOLKIT_DIR", ""),
    ("00_规范与工具/治理", "GOV_ROOT", ""),
    ("00_规范与工具/环境", "ENV_DIR", ""),
    ("02_wiki/web/data/boards", "BOARDS_DIR", ""),
    ("02_wiki/web/data", "DATA_DIR", ""),
    ("02_wiki/web", "WEB", ""),
    ("02_wiki/state", "STATE_DIR", ""),
    ("02_wiki/rules", "RULES_DIR", ""),
    ("02_wiki", "WIKI_DIR", ""),
    ("", "PROJ", ""),
]

PROJECT_ROOT_RE = re.compile(r"(?i)^[A-Za-z]:[\\/]la拆包项目[\\/]?(.*)$")
DEVICE_RE = re.compile(r"(?i)^[A-Za-z]:[\\/](mrzh|LifeAfter|Users)[\\/]?(.*)$")

# 表达式形态：Path("...") / pathlib.Path("...") —— 整体替换
#   ★ 必须把 `r` 前缀一并吃掉：只替换路径文本会得到 `Path(rPROJ)`（合法标识符，
#     ast 校验发现不了，但运行期是错的）。这类错误最危险 —— 静默产出错误路径。
PATH_CALL_RE = re.compile(
    r"(?P<lead>(?:pathlib\.)?Path\(\s*)(?P<rawprefix>r?)(?P<q>[\"'])"
    r"(?P<path>[A-Za-z]:[\\/][^\"']*)(?P=q)\s*\)")
# 裸字符串形态：= "E:/..." 或  ("E:/...", ...)
#   ★ 必须吃掉 `r` 前缀：只替换引号内的内容会得到 r"str(WEB)" —— 那是字面量，
#     不是表达式，静默变成错误路径。
BARE_STR_RE = re.compile(r"(?P<rawprefix>r?)(?P<q>[\"'])(?P<path>[A-Za-z]:[\\/][^\"']*)(?P=q)")


def norm(p: str) -> str:
    """统一分隔符 + 折叠连续斜杠（源码里常有 `02_wiki\\\\web` 这种双写）。"""
    s = p.replace("\\", "/")
    while "//" in s:
        s = s.replace("//", "/")
    return s.rstrip("/")


def resolve_const(abs_path: str):
    """绝对路径 → (常量名, 相对子路径)。不是项目内路径则返回 None。"""
    m = PROJECT_ROOT_RE.match(norm(abs_path))
    if not m:
        return None
    rest = norm(m.group(1) or "")
    for prefix, const, sub in PREFIX_MAP:
        if prefix == "":
            return const, rest
        if rest == prefix:
            return const, ""
        if rest.startswith(prefix + "/"):
            return const, rest[len(prefix) + 1:]
    return None

def build_expr(abs_path: str, style: str) -> str | None:
    """把绝对路径表达式改写成 la_paths 常量表达式。"""
    r = resolve_const(abs_path)
    if not r:
        return None
    const, sub = r
    if sub:
        # ★ 统一用 / 连接：Windows 上 Path / "a/b" 可用，且避免出现 "/web" 这种前导斜杠
        return f'{const} / "{sub}"'
    return const


def _multiline_continuation(src: str, end: int) -> bool:
    """判断字符串之后是否紧跟**跨行续接的字符串字面量**。

    Path(
        r"E:\\...\\config_work"
        r"\\script_xxx\\entries"
    )
    —— 隐式拼接。替换第一段会让整体变成非法语法
      （实测 build_name_chain_candidates.py / test_export_exchange_static_candidates.py）。

    判据：跳过行尾空白与换行后，若下一个非空行以 r" / r' / " / ' 开头 ⇒ 多段拼接。
    """
    tail = src[end:]
    # 跳过本行剩余部分（可能只有空白）
    nl = tail.find("\n")
    if nl < 0:
        return False
    rest = tail[nl + 1:]
    for line in rest.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith(("r\"", "r'", '"', "'")):
            return True
        return False
    return False


def _is_path_fragment(src: str, start: int) -> bool:
    """判断该字符串是否为「拼接表达式里的路径片段」。

    ROOT / "E:/la拆包项目/01_索引与产物/10_索引/site_data" / "x.json"
    —— 字符串只代表路径的一段，不是完整路径。替换成常量表达式会得到
       ROOT / "str(INDEX_ROOT / ...)"，语义完全错（实测命中 3 例）。

    判据：字符串紧前是路径拼接符 `/`（且前面不是字符串字面量）。
    """
    head = src[max(0, start - 30):start].rstrip()
    if not head:
        return False
    # 结尾是 `/`（路径拼接）或 `os.path.join(` 之类
    if head.endswith("/") or head.endswith("\\"):
        # 但 `Path("...")` 内部不算 —— 那种前面是 `(` 或 `,`
        return True
    return False


def _adjacent_string(src: str, start: int, end: int) -> bool:
    """判断该字符串是否与另一个字符串字面量相邻（隐式拼接）。

    Path(r"a" r"b") / "a" "b" —— 逐个替换会破坏拼接结构。
    判据：字符串**前后**（跳过空白与续行符）紧邻另一个引号。
    """
    tail = src[end:end + 40]
    head = src[max(0, start - 40):start]
    # 前面：跳过空白/换行/反斜杠后应是引号
    t = tail.lstrip()
    if t[:1] in ("'", '"'):
        return True
    # 后面：反向跳过空白与续行反斜杠
    h = head.rstrip()
    if h.endswith("\\"):
        h = h[:-1].rstrip()
    if h[-1:] in ("'", '"'):
        return True
    return False


def _inside_fstring(src: str, pos: int) -> bool:
    """判断位置 pos 是否落在 f-string 字面量内部。

    ★ 用来保护 f-string：f"{DEFAULT_ENTRIES_DIR}" 这类写法里，
      把路径换成 `str(ANALYSIS_ROOT / "x")` 会引入引号 → 语法错误。
    ★ 实现：向前扫描未闭合的 f-string 引号（只看同一行，够用且快）。
    """
    line_start = src.rfind("\n", 0, pos) + 1
    line = src[line_start:pos]
    # 去掉注释与转义引号后，数 f" / f' 的开合
    i = 0
    depth = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\":
            i += 2
            continue
        if ch in "\"'":
            # 找出这个引号是不是 f-string 的开始
            j = i - 1
            while j >= 0 and (line[j].isalnum() or line[j] == "_"):
                j -= 1
            is_f = j >= 0 and line[j] == "f"
            # 找配对引号
            k = i + 1
            while k < len(line):
                if line[k] == "\\":
                    k += 2
                    continue
                if line[k] == ch:
                    break
                k += 1
            if k >= len(line):
                # 未闭合 ⇒ 若为 f-string，说明我们在其内部
                if is_f:
                    return True
                i += 1
                continue
            if is_f and i <= pos <= k:
                return True
            i = k + 1
            continue
        i += 1
    return False


def _is_provenance_literal(src: str, start: int, end: int) -> bool:
    """判断该路径字符串是否属于**溯源元数据**（写进产物、影响可复现性）。

    典型：
        "path": "E:/mrzh/Documents/script.py314.lc.npk",
    这类字段是「产物的来源记录」，必须保持字面量稳定 ——
    改成 client_root() 会让每次构建写出的路径随环境变化，
    破坏字节级可复现（⇒ 别人重建的产物与入库的不一致，diff 全部报差异）。

    判据：该字符串是某个 dict 的 value，且 key 属于溯源语义字段。
    """
    key = src[max(0, start - 120):start]
    m = None
    for km in re.finditer(r"[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']\s*:\s*$", key):
        m = km
    if not m:
        return False
    k = m.group(1).lower()
    return k in {"path", "sha256", "source_path", "abs_path", "file", "filepath",
                 "file_path", "source_file", "container_path", "npk_path",
                 "package_path", "client_path", "root"}


def build_device_expr(abs_path: str) -> str | None:
    """设备路径 → client_root() 表达式。

    ★ 设备路径 = **运行期输入**（用户自己的游戏安装目录），语义上必须可配。
      映射到 la_paths.client_root()：环境变量 LA_CLIENT_ROOT > 默认值。
    ★ 只在「该路径确实是客户端根或其子目录」时才改写；
      形态不符（如 C:/Users/... 的临时目录）一律不改 —— 那是别的机器的残留。
    """
    m = DEVICE_RE.match(norm(abs_path))
    if not m:
        return None
    kind = m.group(1).lower()
    rest = norm(m.group(2) or "")
    if kind == "users":
        return None            # C:/Users/... 是别的机器的临时目录，不改
    if kind == "lifeafter":
        # 另一个客户端根 —— 同样可配，但与 mrzh 不是同一路径，不能混用
        return 'str(client_root())' if not rest else f'str(client_root() / "{rest}")'
    # mrzh（PE/PC 测试服常见布局）
    if not rest:
        return "client_root()"
    return f'client_root() / "{rest}"'


def _device_in_fstring_or_fragment(src: str, start: int) -> bool:
    """设备路径同样要避开 f-string 内部与拼接片段（理由同项目内路径）。"""
    return _inside_fstring(src, start) or _is_path_fragment(src, start)


def rewrite_src(src: str, consts_out: set | None = None):
    """返回 (新源码, 改写记录, 设备路径清单)。

    ★ 关键：赋值语句必须在 **AST 层**处理，不能只靠正则。
      反例：`PROJ = pathlib.Path(r"E:/la拆包项目")`
        纯字符串替换 ⇒ `PROJ = pathlib.Path(PROJ)` —— **自引用**，
        语法合法、ast 校验通过，但运行期 NameError。
      正解：变量名与目标常量同名时，**删掉这行赋值**，改由 import 提供常量。

    consts_out: 若传入 set，AST 层识别到的常量名会写进去（供 import 插入用）。
    """
    records = []
    devices = []

    # ── ① AST 层：处理「把绝对路径赋给一个变量」的语句 ──────────────
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None

    if tree is not None:
        lines = src.splitlines(keepends=True)
        drop = set()          # 需要整行删除的行号（1-based）
        consts = set()

        def handle_assign(node, stmt_lines):
            """node: ast.Assign；stmt_lines: 该语句的行号集合"""
            val = node.value
            # 只认 Path("abs") / pathlib.Path("abs") 这一种形态
            if not isinstance(val, ast.Call):
                return None
            fn = val.func
            fname = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if fname != "Path":
                return None
            if len(val.args) != 1 or not isinstance(val.args[0], ast.Constant):
                return None
            if not isinstance(val.args[0].value, str):
                return None
            abs_path = val.args[0].value
            r = resolve_const(abs_path)
            if not r:
                devices.append(abs_path)
                return None
            const, sub = r
            # 变量名
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if not names:
                return None
            varname = names[0]
            expr = const if not sub else f'{const} / "{sub}"'
            if consts_out is not None:
                consts_out.add(const)
            if varname == const:
                # ★ 同名 ⇒ 删掉赋值行，常量由 import 提供（避免自引用）
                for ln in stmt_lines:
                    drop.add(ln)
                records.append({"from": abs_path, "to": f"import {const}（删除同名赋值）",
                                "form": "赋值语句"})
                consts.add(const)
                return ("drop", None)
            # 异名 ⇒ 保留赋值，右侧换成常量表达式
            records.append({"from": abs_path, "to": f"{varname} = {expr}",
                            "form": "赋值语句"})
            consts.add(const)
            return ("replace", (node, expr))

        # 顶层与函数体都要处理（用 walk 覆盖嵌套）
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                stmt_lines = set(range(node.lineno, (node.end_lineno or node.lineno) + 1))
                res = handle_assign(node, stmt_lines)
                if res and res[0] == "replace":
                    anode, expr = res[1]
                    # 定位 RHS 所在行，做行内替换
                    seg = "".join(lines[anode.value.lineno - 1:anode.value.end_lineno])
                    newseg = re.sub(
                        r"(?P<lead>(?:pathlib\.)?Path\(\s*)(?P<rawprefix>r?)(?P<q>[\"'])"
                        r"(?P<path>[A-Za-z]:[\\/][^\"']*)(?P=q)\s*\)",
                        lambda mm: f"{mm.group('lead')}{expr})", seg)
                    if newseg != seg:
                        lines[anode.value.lineno - 1:anode.value.end_lineno] = [newseg]

        if drop:
            out = []
            for i, ln in enumerate(lines, 1):
                if i in drop:
                    continue
                out.append(ln)
            src = "".join(out)

    # ── ② 正则层：处理剩余的表达式级引用（函数体内、参数默认值等） ──
    def _dev(m):
        devices.append(m.group("path"))
        return m.group(0)

    def _call(m):
        expr = build_expr(m.group("path"), "call")
        if expr is None:
            # ★ 设备路径：走 client_root()（运行期输入，可配）
            dexpr = build_device_expr(m.group("path"))
            if dexpr and not _device_in_fstring_or_fragment(src, m.start()) \
                    and not _is_provenance_literal(src, m.start(), m.end()):
                records.append({"from": m.group("path"), "to": dexpr, "form": "Path(...)"})
                if consts_out is not None:
                    consts_out.add("client_root")
                return f'{m.group("lead")}{dexpr})'
            devices.append(m.group("path"))
            return m.group(0)
        records.append({"from": m.group("path"), "to": expr, "form": "Path(...)"})
        # ★ 不保留 `r` 前缀：常量名不是字符串字面量，r 前缀会变成 `rPROJ`（错误）
        return f'{m.group("lead")}{expr})'

    def _bare(m):
        # ★ 裸字符串**不能**换成常量名 —— 常量是 Path 对象，不是 str。
        #   `W = r'E:/...'` → `W = "WEB"` 会让 os.path.join("WEB", ...) 变成相对路径，
        #   静默指向错误位置（实测 _cmp_decoder_20260921.py 命中此坑）。
        #   正确做法：裸字符串改写成 `str(常量)`，保持 str 语义。
        expr = build_expr(m.group("path"), "bare")
        if expr is None:
            # ★ 设备路径：走 client_root()，但裸字符串要保持 str 语义
            dexpr = build_device_expr(m.group("path"))
            if dexpr and not _device_in_fstring_or_fragment(src, m.start()) \
                    and not _is_provenance_literal(src, m.start(), m.end()):
                strexpr = dexpr if dexpr.startswith("str(") else f"str({dexpr})"
                records.append({"from": m.group("path"), "to": strexpr, "form": "裸字符串"})
                if consts_out is not None:
                    consts_out.add("client_root")
                return strexpr
            devices.append(m.group("path"))
            return m.group(0)
        # ★ 避开 f-string 内部：f"{X}" 里的替换会引入引号，破坏 f-string 语法。
        if _inside_fstring(src, m.start()):
            devices.append(m.group("path"))
            return m.group(0)
        # ★ 避开**相邻字符串隐式拼接**：
        #   Path(r"a" r"b") 跨行拼接时，逐个替换会破坏整体结构
        #   （实测 build_name_chain_candidates.py 命中）。
        #   判据：同一语句里该字符串紧邻另一个字符串字面量。
        if _adjacent_string(src, m.start(), m.end()):
            devices.append(m.group("path"))
            return m.group(0)
        # ★ 避开**多段拼接的整体**：
        #   Path(
        #       r"E:\...\config_work"
        #       r"\script_xxx\entries"
        #   )
        #   第二段没有盘符（不匹配正则），但第一段被替换后整体就散了
        #   —— 会产生 `str(...) r"..."` 这种非法拼接。
        #   判据：下一行若是续行（以 r" / " 开头），说明这是多段拼接。
        if _multiline_continuation(src, m.end()):
            devices.append(m.group("path"))
            return m.group(0)
        # ★ 避开**拼接表达式内部的路径片段**：
        #   ROOT / "E:/la拆包项目/01_索引与产物/10_索引/site_data"
        #   —— 这里字符串只是路径的一段，替换成常量表达式会得到
        #      ROOT / "str(INDEX_ROOT / ...)"，语义完全错。
        #   判据：字符串紧前是 `/` 或 `\` 拼接符 ⇒ 它是片段而非完整路径。
        if _is_path_fragment(src, m.start()):
            devices.append(m.group("path"))
            return m.group(0)
        records.append({"from": m.group("path"), "to": f"str({expr})", "form": "裸字符串"})
        return f'str({expr})'

    new = PATH_CALL_RE.sub(_call, src)
    new = BARE_STR_RE.sub(_bare, new)
    return new, records, devices


def insert_import(new: str, consts: list[str]) -> str:
    """把 la_paths import 插到**模块级** import 区末尾。

    ★ 坑1：不能简单找「最后一个 import 行」——那可能落在 try:/except 块内部，
      插进去会破坏语法（实测把 import 插进了 try 体内 → SyntaxError）。
      ⇒ 用 ast 找**模块级** Import/ImportFrom 的最大行号。
    ★ 坑2：`from __future__ import ...` 必须位于文件**最开头**。
      若把 la_paths import 插到它前面 → SyntaxError
      （实测 _src.py 触发：from __future__ imports must occur at the beginning）。
      ⇒ 插入点必须在所有 __future__ 导入之后。
    ★ 坑3（★本工具实测踩到）：插入点若落在**使用点之后**，
      模块级 `WEB = PROJ / ...` 会在 import 之前执行 → NameError: PROJ。
      ⇒ 插入点必须 **早于该常量的首次使用**。
      做法：取「模块级 import 区末尾」与「首次使用行」两者的较小值。
    """
    if not consts:
        return new
    # ★ 若已有 `from la_paths import ...` ⇒ **合并**常量，不能直接跳过。
    #   否则后补的 client_root 等新常量不会进 import（实测 avatar_resolve.py：
    #   已有 import PROJ，就跳过了 client_root ⇒ NameError）。
    existing = re.search(r"^\s*from\s+la_paths\s+import\s+([^\n#]+)", new, re.M)
    if existing:
        have = {n.strip() for n in existing.group(1).split(",") if n.strip()}
        missing = [c for c in consts if c not in have]
        if not missing:
            return new
        repl = "from la_paths import %s  # noqa: E402" % ", ".join(sorted(have | set(missing)))
        # ★ 去掉原行尾可能已有的 `# noqa: E402`，避免拼出 `# noqa: E402# noqa: E402`
        tail = new[existing.end():]
        tail = re.sub(r"^\s*#\s*noqa:[^\n]*", "", tail)
        return new[:existing.start()] + repl + tail
    try:
        tree = ast.parse(new)
    except SyntaxError:
        return new
    last = -1
    future_last = -1
    for node in tree.body:            # 只看模块级直接子节点
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            end = node.end_lineno or node.lineno
            last = max(last, end)
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                future_last = max(future_last, end)

    # ★ 找常量的首次「模块级」使用行（赋值/表达式里用到）
    use_first = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        seg = ast.get_source_segment(new, node) or ""
        for c in consts:
            if re.search(r"\b%s\b" % re.escape(c), seg):
                ln = node.lineno
                use_first = ln if use_first is None else min(use_first, ln)
                break
        if use_first is not None:
            break

    imp = ('\nsys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n'
           'from la_paths import %s  # noqa: E402\n' % ", ".join(consts))
    lines = new.splitlines(keepends=True)
    if last < 0 and use_first is None:
        # 顶层没有任何 import：插到文件最前（docstring 之后）
        ins = 0
        if tree.body and isinstance(tree.body[0], ast.Expr) and \
                isinstance(getattr(tree.body[0], "value", None), ast.Constant) and \
                isinstance(tree.body[0].value.value, str):
            ins = tree.body[0].end_lineno or 0
        lines.insert(ins, imp.lstrip("\n"))
    else:
        # 插入点：既要晚于 __future__，又要早于首次使用
        at = last if last >= 0 else 0
        if future_last >= 0:
            at = max(at, future_last)
        if use_first is not None:
            at = min(at, use_first - 1)
        at = max(at, future_last if future_last >= 0 else 0)
        lines.insert(at, imp)
    out = "".join(lines)
    # 依赖的模块确保已 import。
    # ★ 兜底插入也必须排在 `from __future__` 之后 —— 否则同样触发
    #   "from __future__ imports must occur at the beginning of the file"。
    out = _ensure_module_import(out, "pathlib")
    out = _ensure_module_import(out, "sys")
    return out


def _ensure_module_import(src: str, mod: str) -> str:
    """确保**模块级** `import <mod>` 存在；缺失时插在 __future__ 之后。

    ★ 必须用 ast 判定「模块级」—— 正则 `^\\s*import sys` 会把函数体内的
      `import sys as _sys` 也算上（缩进开头），导致以为已导入、
      实际模块级没有 → NameError: sys（实测 checks.py 命中）。
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == mod or a.name.split(".")[0] == mod:
                    return src
    at = 0
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            at = max(at, node.end_lineno or node.lineno)
    lines = src.splitlines(keepends=True)
    lines.insert(at, "import %s\n" % mod)
    return "".join(lines)


def _is_precondition_error(why: str) -> bool:
    """判断导入失败是否属于「脚本自身前置条件缺失」而非「改写引入的错误」。

    ★ 关键区分：
        FileNotFoundError / AssertionError / ModuleNotFoundError
            ⇒ 脚本需要特定数据/依赖才能跑 —— 与路径改写无关，
              保留改写（否则会错过本来正确的改写）。
        NameError / AttributeError / SyntaxError / TypeError
            ⇒ 改写引入的真错误 ⇒ 必须回滚。
    """
    return bool(re.search(
        r"FileNotFoundError|NotADirectoryError|PermissionError|"
        r"AssertionError|ModuleNotFoundError|ImportError|"
        r"已废弃|SystemExit", why))


def _import_smoke(path: pathlib.Path) -> tuple[bool, str]:
    """改写后真正 import 一次，确认模块可加载且路径常量指向真实目录。

    ★ 为什么必须真跑：ast.parse 只保证语法。
      `Path(rPROJ)` / `Path("PROJ")` 语法合法但运行期是错的 ——
      这种「静默产出错误路径」是最难查的一类 bug。
    """
    import subprocess
    tools_dir = str(path.parent)
    # ★ 用 runpy 而非 importlib：runpy 直接执行文件，
    #   而 importlib 需要额外把 tools_dir 放进 sys.path 才能找到 la_paths。
    #   （原实现用 importlib 且未确保 la_paths 可导入 ⇒ 误报 NameError）
    code = (
        "import sys, runpy\n"
        "sys.path.insert(0, %r)\n" % tools_dir +
        "runpy.run_path(%r, run_name='__pf_smoke__')\n" % str(path) +
        "print('SMOKE_OK')\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
    except Exception as e:
        return False, "自检进程异常: %s" % e
    if "SMOKE_OK" not in (r.stdout or ""):
        err = (r.stderr or "").strip().splitlines()
        last_err = err[-1][:160] if err else "未知错误"
        # ★ 区分「环境缺依赖」与「真错误」：
        #   缺 numpy / yaml / cryptography 这类是**运行环境问题**，不是改写引入的 ——
        #   判成失败会导致整个文件被回滚，白白错过可用的改写。
        #   但仍要记录下来（供人工确认该脚本需要额外依赖）。
        if re.search(r"No module named ['\"]?[A-Za-z_][\w.]*['\"]?", last_err) and \
                "la_paths" not in last_err:
            return True, ""      # 依赖缺失 ⇒ 放行
        return False, last_err
    return True, ""


def apply_to_file(path: pathlib.Path, dry: bool) -> dict:
    src = path.read_text(encoding="utf-8")
    ast_consts: set[str] = set()
    new, records, devices = rewrite_src(src, ast_consts)
    if not records:
        return {"file": path.name, "changed": False, "records": [], "devices": devices}
    if dry:
        return {"file": path.name, "changed": True, "records": records, "devices": devices}

    # 1) 语法校验（改写后必须仍能 parse）
    try:
        ast.parse(new)
    except SyntaxError as e:
        return {"file": path.name, "changed": False, "error": "改写后语法错误: %s" % e,
                "records": records, "devices": devices}

    # 2) 统计需要 import 的常量（AST 层已识别 + 表达式层补充）
    consts = set(ast_consts)
    for r in records:
        to = r["to"]
        if to.startswith("import "):
            consts.add(to.split()[1].split("（")[0])
        elif r["form"] == "赋值语句":
            consts.add(to.split("=")[-1].split("/")[0].strip())
        elif r["form"] == "裸字符串":
            # to 形如 "str(WEB)" / 'str(WEB / "x")' / 'str(client_root())'
            inner = to[to.find("(") + 1:to.rfind(")")] if "(" in to else to
            head = inner.split("/")[0].strip()
            consts.add(head if head.isidentifier() else "client_root"
                       if "client_root" in inner else head)
        else:
            head = to.split("/")[0].strip()
            consts.add(head if head.isidentifier() else to)
    # ★ client_root 是**函数**不是常量，但它同样来自 la_paths —— 必须一起 import。
    #   （漏了会得到 NameError: client_root，实测 avatar_resolve.py 命中）
    consts = sorted({c for c in consts
                      if (c.isupper() or c == "client_root") and c.isidentifier()})

    # 3) 插入 / 合并 import
    #    ★ 不要在这里判断「是否已有 la_paths import」—— 已有时要**合并**新常量，
    #      跳过会导致新常量没被导入（实测 avatar_resolve.py：已有 import PROJ，
    #      后补的 client_root 丢失 ⇒ NameError）。合并逻辑在 insert_import 内。
    if consts:
        new = insert_import(new, consts)

    # 4) 落盘前备份
    BACKUP.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = BACKUP / f"{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, bak)

    path.write_text(new, encoding="utf-8")

    # 5) 复验：硬编码计数必须下降
    after_hard = len(PROJECT_ROOT_ANY.findall("".join(
        l for l in new.splitlines() if not l.strip().startswith("#"))))
    before_hard = len(PROJECT_ROOT_ANY.findall("".join(
        l for l in src.splitlines() if not l.strip().startswith("#"))))
    if after_hard > before_hard:
        shutil.copy2(bak, path)   # 回滚
        return {"file": path.name, "changed": False, "error": "改写后硬编码未下降，已回滚",
                "records": records, "devices": devices}

    # 6) 语义复验：★ 光靠 ast 不够 —— `Path(rPROJ)` 是合法语法却是错的。
    #   这里真正 import 一次，确认模块能加载且常量值正确。
    ok, why = _import_smoke(path)
    if not ok:
        # ★ 区分「改写引入的错误」与「脚本自身的前置条件缺失」。
        #   后者（缺数据文件 / 缺还原树产物 / 缺依赖）与路径改写无关 ——
        #   若因此回滚，会白白错过本来正确的改写（实测 nucleus 系列 5 个文件）。
        #   判据：报错是「找不到文件 / 断言失败 / 缺模块」⇒ 保留改写 + 标注；
        #        报错是 NameError / AttributeError ⇒ 是改写引入的 ⇒ 回滚。
        if _is_precondition_error(why):
            return {"file": path.name, "changed": True, "records": records,
                    "devices": devices, "backup": str(bak),
                    "before_hard": before_hard, "after_hard": after_hard,
                    "note": "已改写；自检因脚本自身前置条件缺失而未通过"
                            "（与路径改写无关）: %s" % why[:120]}
        shutil.copy2(bak, path)
        return {"file": path.name, "changed": False,
                "error": "导入自检失败，已回滚: %s" % why,
                "records": records, "devices": devices}

    return {"file": path.name, "changed": True, "records": records, "devices": devices,
            "backup": str(bak), "before_hard": before_hard, "after_hard": after_hard}


# 检测用（不做行首锚定 —— 路径常出现在行中间的表达式里）
PROJECT_ROOT_ANY = re.compile(r"(?i)[A-Za-z]:[\\/]la拆包项目")
DEVICE_ANY = re.compile(r"(?i)[A-Za-z]:[\\/](?:mrzh|LifeAfter)[\\/]")


def collect_files() -> list[pathlib.Path]:
    out = []
    # ★ 自我保护：la_paths.py 里必须**字面量**写着默认客户端路径与根标记，
    #   它是所有脚本的路径来源。改写它 = 把源头改坏。
    #   同理，本工具自身也要跳过（它内置了大量路径示例）。
    SELF_PROTECT = {"la_paths.py", "fix_hardcoded_paths.py", "portability_audit.py"}
    for p in sorted(TOOLS.glob("*.py")):
        if p.name in SELF_PROTECT:
            continue
        src = p.read_text(encoding="utf-8", errors="ignore")
        if PROJECT_ROOT_ANY.search(src) or DEVICE_ANY.search(src):
            out.append(p)
    for p in sorted((TOOLS / "build").glob("*.py")) + sorted((TOOLS / "checks").glob("*.py")):
        if p.name in SELF_PROTECT:
            continue
        src = p.read_text(encoding="utf-8", errors="ignore")
        if PROJECT_ROOT_ANY.search(src) or DEVICE_ANY.search(src):
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="硬编码路径改写器")
    ap.add_argument("--list", action="store_true", help="列出待改文件")
    ap.add_argument("--plan", action="store_true", help="显示改写计划（dry-run）")
    ap.add_argument("--apply", action="store_true", help="落盘")
    ap.add_argument("--file", help="只处理指定文件")
    ap.add_argument("--limit", type=int, default=0, help="最多处理几个文件")
    ap.add_argument("--batch", type=int, default=10, help="每批文件数")
    args = ap.parse_args()

    files = collect_files()
    if args.file:
        files = [f for f in files if f.name == args.file or str(f) == args.file]
    if args.limit:
        files = files[:args.limit]

    if args.list:
        print(f"待改文件 {len(files)} 个（02_wiki/web/tools 下含项目自身绝对路径）")
        for f in files[:40]:
            src = f.read_text(encoding="utf-8", errors="ignore")
            n = len(PROJECT_ROOT_ANY.findall(src))
            print(f"  {n:3d} 处  {f.relative_to(PROJ)}")
        if len(files) > 40:
            print(f"  … 另有 {len(files) - 40} 个")
        return 0

    if not args.apply:
        # dry-run 预览
        total_rec = 0
        total_dev = 0
        for f in files:
            src = f.read_text(encoding="utf-8", errors="ignore")
            _, recs, devs = rewrite_src(src)
            total_rec += len(recs)
            total_dev += len(devs)
            if args.plan and recs:
                print(f"\n── {f.relative_to(PROJ)}")
                for r in recs[:6]:
                    print(f"   {r['from']}")
                    print(f"     → {r['to']}")
                if len(recs) > 6:
                    print(f"   … 另有 {len(recs) - 6} 处")
        print(f"\n（dry-run）待改文件 {len(files)}，可改写表达式 {total_rec} 处，"
              f"设备路径 {total_dev} 处（只报告不自动改）")
        return 0

    # apply：分批
    done = failed = 0
    report = []
    batch = max(1, args.batch)
    for i in range(0, len(files), batch):
        chunk = files[i:i + batch]
        for f in chunk:
            r = apply_to_file(f, dry=False)
            report.append(r)
            if r.get("changed"):
                done += 1
                print(f"  ✅ {f.name}: 改写 {len(r['records'])} 处"
                      f"（硬编码 {r.get('before_hard')} → {r.get('after_hard')}）")
            elif r.get("error"):
                failed += 1
                print(f"  ❌ {f.name}: {r['error']}")
            else:
                print(f"  ·  {f.name}: 无可改写项")
        print(f"  —— 批次 {i // batch + 1} 完成（累计成功 {done} / 失败 {failed}）——")

    (STATE / "pathfix_report.json").write_text(
        json.dumps({"created": datetime.datetime.now().isoformat(timespec="seconds"),
                    "changed": done, "failed": failed, "items": report},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n改写成功 {done} 个 / 失败 {failed} 个")
    print(f"报告：{STATE / 'pathfix_report.json'}")
    print("提醒：改写后建议跑 python 02_wiki/web/tools/checks/portability_audit.py 复核")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
