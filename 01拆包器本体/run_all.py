# -*- coding: utf-8 -*-
"""明日之后拆包工具包 — 统一入口（v2.0）

用法：
  python run_all.py index build         # GPK/FPK/NPK → 统一 SQLite 文件索引
  python run_all.py index status        # 索引健康/过期检查
  python run_all.py find <逻辑路径>     # 索引查询，返回全部候选
  python run_all.py extract <路径> <输出> # 唯一命中后定点提取
  python run_all.py verify              # 索引 + 已知路径端到端自检
  python run_all.py overview            # 全格式概览：NPK条目数 + FPK 64包分类 + 1DPW 自检
  python run_all.py restore            # 文件名还原（170 条资源路径 + 解包验证）
  python run_all.py bindict-check      # BinDict 自检：AUG attrs + KJ1 转印（需 E:/mrzh）
  python run_all.py bridge-audit       # 皮肤逻辑路径→IDX/WPK物理桥审计（只读）

只读 E:/mrzh；产物写本目录 output/。
"""
from __future__ import annotations
import importlib.util,json,struct,sys
from pathlib import Path

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

ROOT = Path(__file__).resolve().parent / "工具库"
OUT = Path(__file__).resolve().parent / "output"
APP_CORE = ROOT / "10_应用核心"

def npk_entries(pkg: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("npkr", ROOT / "01_核心解包器" / "npk_reader.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    with pkg.open("rb") as f:
        h = m.aes_ecb(f.read(32))
        _r, magic, ver, to, n = struct.unpack_from("<QIIII", h)
        if magic != 0x4B50584E:
            return None
        f.seek(to)
        tab = m.aes_ecb(f.read(n * 48))
        return n, ver

def cmd_overview():
    print("== NPK 条目数 ==")
    for name in ("script.npk", "script.py3.npk", "script.py314.lc.npk"):
        p = Path(r"E:/mrzh/Documents") / name
        if p.exists():
            r = npk_entries(p)
            print(f"  {name}: {r[0]} entries (v{r[1]})" if r else f"  {name}: 不可读")
    for name in ("res.npk", "ui.npk"):
        p = Path(r"E:/mrzh/res") / name
        if not p.exists():
            p = Path(r"E:/mrzh") / name
        if p.exists():
            r = npk_entries(p)
            print(f"  {name}: {r[0]} entries (v{r[1]})" if r else f"  {name}: 不可读")
    print("\n== FPK 64 包分类（前 8MB 扫描，40 帧内）==")
    spec = importlib.util.spec_from_file_location("fpk", ROOT / "02_FPK工具" / "fpk_toolkit.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.cmd_overview()

def cmd_restore():
    print("== 文件名还原（配置表 → path_id → ui.npk）==")
    spec = importlib.util.spec_from_file_location("fr", ROOT / "06_文件名还原" / "filename_restore.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.main()

def cmd_thfb():
    print("== THFB 哈希提取 ==")
    spec = importlib.util.spec_from_file_location("th", ROOT / "09_THFB工具" / "thfb_toolkit.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.main()

def cmd_bridge_audit():
    print("== 皮肤逻辑路径 → IDX/WPK 物理桥审计 ==")
    spec = importlib.util.spec_from_file_location("bridge", ROOT / "10_应用核心" / "physical_bridge_audit.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.main([])


def cmd_bindict_check():
    print("== BinDict 自检 ==")
    import runpy
    base = ROOT / "05_BinDict解码器"
    for script in ("bindict_attrs_decoder.py", "bindict_kj1_transfer_decoder.py"):
        p = base / script
        if p.exists():
            print(f"-- {script} --")
            try:
                runpy.run_path(str(p), run_name="__check__")
            except Exception as e:
                print(f"  ERR {e!r}")

def _unified(argv):
    if str(APP_CORE) not in sys.path:
        sys.path.insert(0, str(APP_CORE))
    from toolkit_cli import main as toolkit_main
    return toolkit_main(argv)


def _print_help():
    print(__doc__)
    print("兼容命令：overview / restore / bindict-check / thfb / bridge-audit")


def main(argv=None):
    OUT.mkdir(parents=True, exist_ok=True)
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "overview"
    if cmd in {"index", "find", "extract", "verify"}:
        return _unified(argv)
    if cmd in {"-h", "--help", "help"}:
        _print_help()
        return 0
    commands = {
        "overview": cmd_overview,
        "restore": cmd_restore,
        "bindict-check": cmd_bindict_check,
        "thfb": cmd_thfb,
        "bridge-audit": cmd_bridge_audit,
    }
    action = commands.get(cmd)
    if action is None:
        print(f"未知命令：{cmd}", file=sys.stderr)
        _print_help()
        return 2
    action()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
