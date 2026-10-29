# -*- coding: utf-8 -*-
"""la_paths.py — Wiki 工具层的**统一路径入口**

## 为什么有这个模块

开源目标：别人 clone 仓库后，用**自己设备**的拆包产物能构建出一样的 wiki。
原先 wiki 工具层有 476 个脚本写死了 `E:/la拆包项目/...`（本机绝对路径），
换机/换目录即失效 —— clone 下来根本跑不起来。

本模块把「路径从哪来」收敛成**唯一一处**：

  项目根（四优先级，与 toolkit_core.paths 同口径）
    ① 环境变量 LA_ROOT
    ② 命令行 --root（由调用方 set_root 传入）
    ③ 从 __file__ 向上找仓库标记文件
    ④ 当前工作目录向上找
    找不到 → 明确报错，不猜

  客户端根（运行期输入，别人设备各不相同）
    ① 环境变量 LA_CLIENT_ROOT
    ② 命令行 --client-root
    ③ 默认 E:/mrzh（仅 PE/PC 测试服常见布局；正式环境必须显式指定）

## 用法

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, WEB, BOARDS_DIR, RULES_DIR, TREE_ROOT, client_root
```

或在脚本顶部：
```python
from la_paths import PROJ, WEB
```

★ 纪律：**新脚本一律用本模块，不要再写 `Path(PROJ)`。**
   体检工具：python 02_wiki/web/tools/checks/portability_audit.py
"""
from __future__ import annotations

import os
import pathlib
import sys

# ── 仓库标记：用于向上定位项目根 ────────────────────────────────────
#   判定 = 同时存在这些相对路径（任选其一组合），避免误判到父目录。
_MARKER_CANDIDATES = (
    ("la.py", "02_wiki/web"),
    ("00_规范与工具", "02_wiki/web"),
    ("02_wiki", "web/tools"),
)


def _looks_like_root(p: pathlib.Path) -> bool:
    try:
        for combo in _MARKER_CANDIDATES:
            if all((p / c).exists() for c in combo):
                return True
    except OSError:
        pass
    return False


def find_project_root(explicit: str | os.PathLike | None = None) -> pathlib.Path:
    """四优先级定位项目根。找不到就抛错，不猜。"""
    tried: list[str] = []

    if explicit:
        p = pathlib.Path(explicit).resolve()
        if _looks_like_root(p):
            return p
        raise RuntimeError(
            f"指定的 --root 不是项目根：{p}\n"
            f"判据：需同时存在 {', '.join('/'.join(c) for c in _MARKER_CANDIDATES)}")

    env = os.environ.get("LA_ROOT")
    if env:
        p = pathlib.Path(env).resolve()
        if _looks_like_root(p):
            return p
        tried.append(f"② 环境变量 LA_ROOT={p}（不是项目根）")

    # ③ 从本文件向上找
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if _looks_like_root(up):
            return up
        tried.append(f"③ 文件向上 {up}")

    # ④ 从当前工作目录向上找
    try:
        cwd = pathlib.Path.cwd().resolve()
        for up in cwd.parents:
            if _looks_like_root(up):
                return up
            tried.append(f"④ cwd 向上 {up}")
        tried.append(f"④ cwd 自身 {cwd}")
    except OSError:
        pass

    raise RuntimeError(
        "找不到项目根。\n已尝试：\n  " + "\n  ".join(tried[:14]) +
        "\n⇒ 请设环境变量 LA_ROOT=<仓库路径>，或传 --root <仓库路径>。")


# ── 项目根与派生目录 ────────────────────────────────────────────────
PROJ: pathlib.Path = find_project_root()
WEB: pathlib.Path = PROJ / "02_wiki" / "web"
WIKI_DIR: pathlib.Path = PROJ / "02_wiki"
BOARDS_DIR: pathlib.Path = WEB / "data" / "boards"
DATA_DIR: pathlib.Path = WEB / "data"
RULES_DIR: pathlib.Path = PROJ / "02_wiki" / "rules"
STATE_DIR: pathlib.Path = PROJ / "02_wiki" / "state"
ARTIFACTS: pathlib.Path = PROJ / "01_索引与产物"
TREE_ROOT: pathlib.Path = ARTIFACTS / "41_还原树"
INDEX_ROOT: pathlib.Path = ARTIFACTS / "10_索引"
ANALYSIS_ROOT: pathlib.Path = ARTIFACTS / "30_分析"
TEMP_ROOT: pathlib.Path = ARTIFACTS / "90_临时"
EXTRACT_ROOT: pathlib.Path = ARTIFACTS / "20_提取"
SOURCE_PKG_ROOT: pathlib.Path = ARTIFACTS / "源包"
PENDING_DELETE_ROOT: pathlib.Path = ARTIFACTS / "95_待清理"
REVIEW_ROOT: pathlib.Path = ARTIFACTS / "96_审阅区"
TOOLKIT_DIR: pathlib.Path = PROJ / "00_规范与工具" / "工具"
TOOLKIT_LIB: pathlib.Path = TOOLKIT_DIR / "工具库"
TOOLKIT_CORE: pathlib.Path = TOOLKIT_LIB / "00_共享核心"
GOV_ROOT: pathlib.Path = PROJ / "00_规范与工具" / "治理"
ENV_DIR: pathlib.Path = PROJ / "00_规范与工具" / "环境"


def client_root(explicit: str | os.PathLike | None = None) -> pathlib.Path:
    """客户端根（游戏安装目录 / 模拟器目录）—— **运行期输入**。

    优先级：显式参数 → 环境变量 LA_CLIENT_ROOT → 默认 E:/mrzh。
    默认值只是 PE/PC 测试服的常见布局；正式环境应当显式指定，
    脚本里写死设备路径会让换设备的人直接崩。
    """
    if explicit:
        return pathlib.Path(explicit).resolve()
    env = os.environ.get("LA_CLIENT_ROOT")
    if env:
        return pathlib.Path(env).resolve()
    return pathlib.Path(r"E:/mrzh").resolve()


def rel(p: pathlib.Path) -> str:
    """把绝对路径转成相对项目根的字符串（写进产物/日志时用，避免泄露本机布局）。"""
    try:
        return str(pathlib.Path(p).resolve().relative_to(PROJ)).replace("\\", "/")
    except (ValueError, OSError):
        return str(p)


def ensure_shared_core_on_path() -> None:
    """把 toolkit_core 所在目录挂到 sys.path（等价于 README 里那句 export PYTHONPATH）。"""
    s = str(TOOLKIT_CORE)
    if s not in sys.path:
        sys.path.insert(0, s)


if __name__ == "__main__":
    print(f"项目根    : {PROJ}")
    print(f"客户端根  : {client_root()}")
    print(f"板目录    : {BOARDS_DIR}")
    print(f"规则目录  : {RULES_DIR}")
    print(f"状态目录  : {STATE_DIR}")
    print(f"还原树    : {TREE_ROOT}  (存在={TREE_ROOT.exists()})")
