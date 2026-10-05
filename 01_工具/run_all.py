# -*- coding: utf-8 -*-
"""明日之后拆包工具包 — 统一入口

用法：`python run_all.py <子命令> [选项]`，子命令见 `--help`。

## 这个文件现在只是个壳

命令定义（`build_parser()`）唯一来源：
    `01_工具/工具库/00_共享核心/命令行/toolkit_cli.py`

★ 2026-09-26 收敛前：这里手写 9 个子命令，`toolkit_cli.build_parser()` 另有一套。
  两套定义的后果是「改一处行为，另一处的消费方静默坏掉」——A15 已实证：
  把 `index status` 改成默认同步 sidecar 后 stdout 不再输出 JSON，
  依赖它的主页采集器**不报错、只是全部显示「读取失败」**。
  现在命令定义只有一份，run_all.py / exe_cli.py / GUI 都调它。

本文件仍负责三件事（都不属于「命令定义」）：
  1. 定位工具库根（向上搜索，不手算 parents[N]）
  2. 把 `00_共享核心` 与 `00_共享核心/命令行` 挂进 sys.path
  3. 启动环境自检（解释器是否在项目专用环境、关键依赖是否齐）

只读 E:/mrzh；产物写 03_执行/90_临时/工具产出/（惰性创建）。
"""
from __future__ import annotations

import sys
from pathlib import Path

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


def _toolkit_root() -> Path:
    """向上搜索工具库根（判据：同时含 00_共享核心 与 01_解码定位复原）。"""
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "工具库" / "00_共享核心").is_dir() and (up / "工具库" / "01_解码定位复原").is_dir():
            return up / "工具库"
    raise RuntimeError("找不到工具库根：向上没有含 工具库/00_共享核心 的目录")


ROOT = _toolkit_root()
CORE_DIR = ROOT / "00_共享核心"
CLI_DIR = CORE_DIR / "命令行"

_CRITICAL_DEPS = {
    "zstandard": "index / extract / 全格式解包",
    "lz4": "NPK flag 2 解压",
    "Crypto": "NPK flag 0 AES 解密",
    "numpy": "索引与网格计算",
    "PIL": "贴图读写",
    "texture2ddecoder": "DXBC/DXT 贴图解码",
    "capstone": "着色器反汇编",
    "scipy": "网格处理",
}


def _env_selfcheck(quiet=False) -> int:
    """启动自检：解释器 + 关键依赖。只警告不阻断 —— 缺依赖属「当前环境不支持」。"""
    import importlib
    tag = "[env]"
    exe = Path(sys.executable)
    venv_hint = Path(__file__).resolve().parents[1] / ".venv" / "Scripts" / "python.exe"
    in_venv = "la拆包项目" in str(exe)
    if not in_venv:
        print("%s 当前解释器不在项目专用环境里：" % tag)
        print("%s   现在用的是 %s" % (tag, exe))
        if venv_hint.exists():
            print("%s   推荐改用 %s" % (tag, venv_hint))
        print("%s   （外部环境可能缺依赖；本检查只提示，不阻断）" % tag)

    missing = []
    for mod, why in _CRITICAL_DEPS.items():
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append((mod, why))
    if missing:
        print("%s 缺少 %d 个关键依赖（相关命令会失败）：" % (tag, len(missing)))
        for mod, why in missing:
            print("%s   ✗ %-20s 影响：%s" % (tag, mod, why))
        print("%s   安装（本环境由 uv 创建，没有 pip，别用 python -m pip）：" % tag)
        print("%s     uv pip install --python \"%s\" -r 01_工具/requirements.lock.txt"
              % (tag, venv_hint))
    elif not quiet and not in_venv:
        print("%s 关键依赖齐全 ✓" % tag)
    return len(missing)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    _env_selfcheck(quiet=not argv or argv[0] in {"-h", "--help", "help"})
    for p in (CLI_DIR, CORE_DIR):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from toolkit_cli import main as toolkit_main
    return toolkit_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
