# -*- coding: utf-8 -*-
r"""LifeAfter 拆包项目统一 CLI。

用法：
  python la.py status                  # 一眼看服务/索引/数据
  python la.py web refresh             # 全站数据刷新（规范化 → 计数同步 → manifest → 审计）
  python la.py web build               # 只跑发布校验 + 生成 manifest
  python la.py web check               # 契约测试 + 数据审计
  python la.py web serve [--port 8765] # 起 wiki 服务
  python la.py web shot <url> <out> [宽] [高]   # CDP 截图
  python la.py index all               # 拉包 + 重建索引 + 名字回填
  python la.py watch device|cnd|logcat # 起监测
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJ = Path(__file__).resolve().parent
WEB = PROJ / "04_站点" / "web"
TOOLS = WEB / "tools"
DET = PROJ / "03_执行" / "30_分析" / "热更检测"
PY = sys.executable
INDEX_CLI = PROJ / "01_工具" / "工具库" / "00_共享核心" / "命令行" / "pe全量索引.py"
FETCH = PROJ / "01_工具" / "工具库" / "01_解码定位复原" / "图集与取图"


def run(name: str, args: list[str], *, cwd: Path = WEB, quiet: bool = False) -> int:
    cmd = [PY, "-u"] + [str(a) for a in args]
    if not quiet:
        print("\n▶ %s" % name)
    t0 = time.time()
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or "").strip().splitlines()[-4:]
    for line in tail:
        print("   " + line[:200])
    if r.returncode != 0 and (r.stderr or "").strip():
        print("   ✗ stderr:", (r.stderr or "").strip().splitlines()[-1][:200])
    print("   %s (%.1fs)" % ("✓" if r.returncode == 0 else "✗ rc=%d" % r.returncode, time.time() - t0))
    return r.returncode


def http_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


# ---------------- status ----------------
def cmd_status(_a) -> int:
    print("== 服务 ==")
    print("  wiki 8765        %s" % ("✓ 200" if http_ok("http://127.0.0.1:8765/wiki.html") else "✗ 未运行"))
    print("== 数据 ==")
    man_p = WEB / "data" / "manifest.json"
    if man_p.is_file():
        man = json.loads(man_p.read_text(encoding="utf-8"))
        boards = man.get("boards") or []
        print("  manifest         %d 块 / %d 条" % (len(boards), sum(b.get("items", 0) for b in boards)))
    else:
        print("  manifest         缺")
    pol_p = WEB / "data" / "publication_policy.json"
    if pol_p.is_file():
        pol = json.loads(pol_p.read_text(encoding="utf-8")).get("boards", {})
        from collections import Counter
        print("  发布状态         %s" % dict(Counter(v.get("publication_status") for v in pol.values())))
    print("== 索引 ==")
    db = DET / "pe_index.sqlite3"
    if db.is_file():
        import sqlite3
        try:
            con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True, timeout=5)
            tot = con.execute("select count(*) from rows").fetchone()[0]
            named = con.execute("select count(*) from rows where name is not null and name<>'' and name not like '%_未命名%'").fetchone()[0]
            packs = con.execute("select count(distinct pack) from rows").fetchone()[0]
            print("  pe_index         %d 包 / %d 行 / 真名 %.1f%% / %.0f MB"
                  % (packs, tot, named * 100.0 / max(tot, 1), db.stat().st_size / 1048576))
        except sqlite3.OperationalError as e:
            print("  pe_index         %.0f MB（正被写入：%s）" % (db.stat().st_size / 1048576, e))
    else:
        print("  pe_index         缺")
    print("== 监测 ==")
    for name, f in (("设备", DET / "device_watch.log"), ("CDN", DET / "cdn_watch.log"),
                    ("logcat", DET / "cdn_download.log")):
        if f.is_file():
            last = f.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-1:] or [""]
            print("  %-8s %s" % (name, last[0][:90]))
    return 0


# ---------------- web ----------------
def cmd_web(a) -> int:
    if a.action == "refresh":
        rc = 0
        rc |= run("规范化 provenance", [TOOLS / "normalize_provenance.py"])
        rc |= run("部位纠偏（以源表 part_type 为准）", [TOOLS / "fix_fashion_parts.py", "--apply"])
        rc |= run("图轨去重（只留高清）", [TOOLS / "dedupe_media.py", "--apply"])
        rc |= run("同步 manifest 计数", [TOOLS / "sync_manifest_counts.py"])
        rc |= run("发布校验 + 生成 manifest", [TOOLS / "build_wiki.py"])
        rc |= run("数据审计", [TOOLS / "project_audit.py"])
        return rc

    if a.action == "build":
        return run("发布校验 + 生成 manifest", [TOOLS / "build_wiki.py"])

    if a.action == "check":
        core = ["tests/test_publication_gate.py", "tests/test_frontend_usability.py",
                "tests/test_weapon_skin_board_filters_sort.py", "tests/test_timed_variant_ui.py"]
        targets = ["tests/"] if getattr(a, "all_tests", False) else core
        rc = run("契约测试", ["-m", "pytest"] + targets + ["-q"], cwd=WEB)
        rc |= run("数据审计", [TOOLS / "project_audit.py"])
        return rc

    if a.action == "tidy":
        return run("归档备份 + 生成 tools 索引", [TOOLS / "tidy_workspace.py"])

    if a.action == "serve":
        print("▶ wiki 服务 http://127.0.0.1:%d/" % a.port)
        return subprocess.call([PY, "-u", str(TOOLS / "wiki_server.py"),
                                "--host", "0.0.0.0", "--port", str(a.port)], cwd=str(WEB))

    if a.action == "shot":
        if not a.url or not a.out:
            print("用法: la.py web shot <url> <out.png> [宽] [高]")
            return 2
        args = [TOOLS / "cdp_shot_local.py", a.url, a.out, str(a.width), str(a.height)]
        if a.js:
            args.append(a.js)
        return run("CDP 截图", args)

    print("未知 web 动作")
    return 2


# ---------------- index ----------------
def cmd_index(a) -> int:
    if a.action in ("all", "pull"):
        rc = run("拉取 gpk 包", [INDEX_CLI, "pull", "--jobs", "8", "--out", DET / "pe_packs"])
        if a.action == "pull":
            return rc
    else:
        rc = 0
    if a.action in ("all", "build"):
        rc |= run("重建索引", [INDEX_CLI, "build", "--jobs", "8", DET / "pe_packs"])
        if a.action == "build":
            return rc
    if a.action in ("all", "names"):
        rc |= run("字典回填名字", [DET / "refill_names_by_fid.py"])
        rc |= run("配置表路径挖掘", [DET / "harvest_paths_from_cdata.py"])
        rc |= run("路径变体扩展 + 回填", [DET / "expand_and_fill_from_cdata.py"])
        rc |= run("索引瘦身", [DET / "shrink_index.py"])
    return rc


# ---------------- npk icons ----------------
def cmd_npk(a) -> int:
    if a.action == "export":
        return run("导出 item_icon npk", [DET / "export_item_icon_npk.py"])
    if a.action == "query":
        args = [DET / "npk_icon_query.py"]
        if a.image:
            args.append(a.image)
        if a.image_id:
            args += ["--id", a.image_id]
        return run("按图反查 npk", args)
    print("未知 npk 动作")
    return 2


# ---------------- pc fetch ----------------
def cmd_pe(a) -> int:
    if a.action == "check":
        return run("PE 覆盖统计", [FETCH / "pe_fetch.py"])
    if a.action == "resolve" and a.path:
        return run("PE resolve", [FETCH / "pe_fetch.py", "resolve", a.path])
    if a.action == "export" and a.path and a.out:
        return run("PE export", [FETCH / "pe_fetch.py", "export", a.path, a.out])
    if a.action == "best" and a.path:
        if str(FETCH) not in sys.path:
            sys.path.insert(0, str(FETCH))
        import pe_fetch_hires as H
        H.describe(a.path)
        return 0
    print("未知 pe 动作")
    return 2


def cmd_pc(a) -> int:
    if a.action == "check":
        return run("PC 取图覆盖统计", [FETCH / "pc_fetch.py"])
    if a.action == "resolve" and a.path:
        return run("PC 解析单个路径", [FETCH / "pc_fetch.py", "resolve", a.path])
    if a.action == "export" and a.path and a.out:
        return run("PC 导出", [FETCH / "pc_fetch.py", "export", a.path, a.out])
    print("未知 pc 动作")
    return 2


# ---------------- watch ----------------
def cmd_watch(a) -> int:
    if a.action == "device":
        return subprocess.call([PY, "-u", str(DET / "device_watch.py"), "--interval", str(a.interval)])
    if a.action == "cdn":
        return subprocess.call([PY, "-u", str(DET / "cdn_watch.py"), "watch",
                                "--interval", str(a.interval), "--auto"])
    if a.action == "logcat":
        return subprocess.call([PY, "-u", str(DET / "cdn_download_watch.py")])
    print("未知监测类型")
    return 2


BANNER = """明日之后拆包项目 CLI

  定位 2D 图/资源（先读 资源定位_速查.md）
    python la.py pe  check | resolve <路径> | export <路径> -o out.png
    python la.py pc  check | resolve <路径>
    python la.py npk query <图片> | --id <hex>

  站点数据
    python la.py web refresh | check | tidy

  索引
    python la.py index ...

"""


# ---------------- doctor ----------------
def _sqlite_meta(db: Path):
    import sqlite3
    if not db.is_file():
        return None, 0, 0
    try:
        c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True, timeout=5)
        tabs = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
        if "rows" not in tabs:
            return tabs, 0, 0
        n = c.execute("select count(*) from rows").fetchone()[0]
        packs = c.execute("select count(distinct pack) from rows").fetchone()[0]
        return tabs, n, packs
    except Exception:
        return None, 0, 0


def cmd_doctor(_a) -> int:
    ok = True
    print("== 环境 ==")
    print("  项目根      %s" % PROJ)
    print("  Python      %s" % sys.version.split()[0])
    client = Path(os.environ.get("LA_CLIENT_ROOT") or r"E:/mrzh")
    mark = "✓" if client.is_dir() else "✗ 未找到（设 LA_CLIENT_ROOT）"
    print("  客户端根    %s  %s" % (client, mark))
    if not client.is_dir():
        ok = False

    print("== 索引 ==")
    for label, name in (("PE 测试服", "pe_index.sqlite3"), ("PC 客户端", "pc_index.sqlite3")):
        tabs, n, packs = _sqlite_meta(DET / name)
        if n:
            print("  %-9s %s  %s 行 / %s 包" % (label, "✓", format(n, ","), packs))
        else:
            print("  %-9s ✗ 不可用（%s）" % (label, "表为空" if tabs is not None else "文件缺失"))

    print("== CLI ==")
    cases = [
        ("pe resolve", ["pe", "resolve", "ui/nielian_icon_v4/kongjian_icon/icon_touxiangkuang_01"]),
        ("pc resolve", ["pc", "resolve", "ui/nielian_icon_v4/kongjian_icon/icon_touxiangkuang_01"]),
    ]
    for label, args in cases:
        r = subprocess.run([PY, "-u", str(PROJ / "la.py")] + args, cwd=str(PROJ),
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        out = r.stdout or ""
        hit = ("未命中" not in out) and (".gpk" in out or ".npk" in out)
        print("  %-11s %s" % (label, "✓ 命中" if hit else "· 未命中（PC 索引为空时属预期）"))

    print("== 服务 ==")
    up = http_ok("http://127.0.0.1:8765/wiki.html")
    print("  wiki 8765   %s" % ("✓ 200" if up else "· 未运行（la.py web serve 启动）"))

    print("\n结论：%s" % ("可用" if ok else "有阻塞项，见上"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="la.py", description="LifeAfter 拆包项目统一 CLI")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("status", help="服务 / 数据 / 索引 概览")

    w = sub.add_parser("web", help="站点数据与页面")
    w.add_argument("action", choices=["refresh", "build", "check", "serve", "shot", "tidy"])
    w.add_argument("--port", type=int, default=8765)
    w.add_argument("url", nargs="?")
    w.add_argument("out", nargs="?")
    w.add_argument("--width", type=int, default=1440)
    w.add_argument("--height", type=int, default=900)
    w.add_argument("--js", default="")
    w.add_argument("--all-tests", action="store_true", help="web check 跑全部测试（默认只跑核心契约）")

    i = sub.add_parser("index", help="PE 索引")
    i.add_argument("action", choices=["all", "pull", "build", "names"])

    pe = sub.add_parser("pe", help="PE 测试服取图")
    pe.add_argument("action", choices=["check", "resolve", "export", "best"])
    pe.add_argument("path", nargs="?")
    pe.add_argument("-o", "--out")

    pc = sub.add_parser("pc", help="PC 客户端取图")
    pc.add_argument("action", choices=["check", "resolve", "export"])
    pc.add_argument("path", nargs="?")
    pc.add_argument("-o", "--out")

    npk = sub.add_parser("npk", help="item_icon npk 图标库")
    npk.add_argument("action", choices=["export", "query"])
    npk.add_argument("image", nargs="?")
    npk.add_argument("--id", dest="image_id")

    sub.add_parser("doctor", help="自检：环境/索引/CLI/服务")

    wt = sub.add_parser("watch", help="监测")
    wt.add_argument("action", choices=["device", "cdn", "logcat"])
    wt.add_argument("--interval", type=int, default=0)

    a = ap.parse_args()
    if not a.cmd:
        print(BANNER)
        ap.print_help()
        return 0
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "doctor":
        return cmd_doctor(a)
    if a.cmd == "web":
        return cmd_web(a)
    if a.cmd == "index":
        return cmd_index(a)
    if a.cmd == "pe":
        return cmd_pe(a)
    if a.cmd == "pc":
        return cmd_pc(a)
    if a.cmd == "npk":
        return cmd_npk(a)
    if a.cmd == "watch":
        if a.interval == 0:
            a.interval = 20 if a.action == "device" else 300
        return cmd_watch(a)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
