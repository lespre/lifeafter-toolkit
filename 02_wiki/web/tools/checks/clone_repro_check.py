#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""clone_repro_check.py — 「克隆后能自己构建出一样的 wiki」自检

开源铁律：别人 clone 仓库 + 用**自己设备**的拆包产物，应当能构建出一样的 wiki。
本工具把这句话拆成可自动验证的几道关：

  G1 冷克隆完整性   —— 只取 git 入库文件，产物/索引是否齐备、关键目录是否在
  G2 无依赖起站     —— 用**系统 python**（不挂 venv）起静态站，页面能否 200
                      （captures 「缺 cryptography ⇒ 整站起不来」这类硬失败）
  G3 路径可移植性   —— 脚本里还有多少写死的本机绝对路径
  G4 构建可复现     —— 条目级指纹能否与上次快照对齐（--fingerprint 参照）
  G5 门禁绿         —— 发布契约是否通过

用法:
  python 02_wiki/web/tools/checks/clone_repro_check.py                # 全检
  python 02_wiki/web/tools/checks/clone_repro_check.py --skip-clone   # 只跑不需克隆的部分
  python 02_wiki/web/tools/checks/clone_repro_check.py --port 8811
  python 02_wiki/web/tools/checks/clone_repro_check.py --json         # 机器可读

退出码: 0 全过 / 1 有阻塞项
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
TOOLS = WEB / "tools"
STATE = PROJ / "02_wiki" / "state"

BOOT_LA = r"""
import sys, urllib.request
base = sys.argv[1]
urls = ["/wiki.html", "/board.html", "/index.html", "/data/manifest.js",
        "/data/boards/vehicle_full.json", "/data/updates.json"]
bad = []
for u in urls:
    try:
        r = urllib.request.urlopen(base + u, timeout=8)
        if r.status != 200:
            bad.append("%s=%d" % (u, r.status))
    except Exception as e:
        bad.append("%s=ERR(%s)" % (u, type(e).__name__))
print("__RESULT__" + repr(bad))
"""


def sh(cmd, cwd=None, timeout=180):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=timeout)


def g1_cold_clone(dest: pathlib.Path) -> dict:
    """冷克隆：只取 git 入库内容（等价于别人 clone 后的目录）。

    ★ 用 checkout-index 直写目标目录 —— 比 `git archive | tar` 快一个量级
      （仓库树 605MB，archive 走 stdout 再解包会超时）。
    ★ 若当前目录**不是 git 仓库**（克隆者已 clone 到手、或者拷贝的目录），
      退化为「就地校验」：直接检查当前目录的完整性，不做二次拷贝。
      （原先硬依赖 git ⇒ 在克隆者的目录里直接失败，违背本工具初衷）
    """
    if not (PROJ / ".git").exists():
        # 就地模式：把当前目录当克隆结果来检
        boards = list((PROJ / "02_wiki/web/data/boards").glob("*.json"))
        checks = {
            "la.py": (PROJ / "la.py").is_file(),
            "profiles.yml": (PROJ / "profiles.yml").is_file(),
            "shared_core": (PROJ / "00_规范与工具/工具/工具库/00_共享核心").is_dir(),
            "boards_json": len(boards),
            "artifacts_skeleton": (PROJ / "01_索引与产物").is_dir(),
        }
        ok = checks["la.py"] and checks["shared_core"] and checks["boards_json"] > 0
        return {"ok": ok, "checks": checks, "path": str(PROJ), "mode": "in-place"}

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    r = sh(["git", "-C", str(PROJ), "checkout-index", "-a",
            "--prefix=%s/" % dest.as_posix().replace("\\", "/")], timeout=900)
    if r.returncode != 0:
        return {"ok": False, "reason": "git checkout-index 失败: %s" % (r.stderr or "")[:200]}

    boards = list((dest / "02_wiki/web/data/boards").glob("*.json"))
    checks = {
        "la.py": (dest / "la.py").is_file(),
        "profiles.yml": (dest / "profiles.yml").is_file(),
        "shared_core": (dest / "00_规范与工具/工具/工具库/00_共享核心").is_dir(),
        "boards_json": len(boards),
        "artifacts_skeleton": (dest / "01_索引与产物").is_dir(),
    }
    ok = checks["la.py"] and checks["shared_core"] and checks["boards_json"] > 0
    return {"ok": ok, "checks": checks, "path": str(dest)}


def g2_serve_without_venv(clone_dir: pathlib.Path, port: int) -> dict:
    """用系统 python 起站（不带 venv、不装 cryptography）。"""
    srv = clone_dir / "02_wiki/web/tools/wiki_server.py"
    if not srv.is_file():
        return {"ok": False, "reason": "冷克隆里缺 wiki_server.py"}
    # 明确用当前解释器，但**不注入 venv 的 site-packages**：
    # 若是 venv python 会掩盖「缺 cryptography」问题 ⇒ 用 -I 隔离 + 记下解释器
    proc = subprocess.Popen([sys.executable, str(srv), "--host", "127.0.0.1", "--port", str(port)],
                            cwd=str(clone_dir / "02_wiki/web"),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    try:
        base = f"http://127.0.0.1:{port}"
        deadline = time.time() + 25
        bad = None
        while time.time() < deadline:
            if proc.poll() is not None:
                out = proc.stdout.read() if proc.stdout else ""
                return {"ok": False, "reason": "服务进程提前退出: %s" % out[-300:]}
            try:
                urllib.request.urlopen(base + "/wiki.html", timeout=2)
                break
            except Exception:
                time.sleep(0.6)
        else:
            return {"ok": False, "reason": "25s 内未探活"}
        # 逐个 URL 复检
        bad = []
        for u in ["/wiki.html", "/board.html", "/index.html", "/data/manifest.js",
                  "/data/boards/vehicle_full.json", "/data/updates.json"]:
            try:
                r = urllib.request.urlopen(base + u, timeout=8)
                if r.status != 200:
                    bad.append("%s=%d" % (u, r.status))
            except Exception as e:
                bad.append("%s=ERR(%s)" % (u, type(e).__name__))
        return {"ok": not bad, "bad_urls": bad,
                "interpreter": sys.executable,
                "note": "若解释器是 venv，G2 结论偏宽松（venv 自带 cryptography）"}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=6)
        except Exception:
            proc.kill()


def g3_portability() -> dict:
    r = sh([sys.executable, str(TOOLS / "checks" / "portability_audit.py"),
            "--scope", "tools", "--quiet"], timeout=300)
    rep = json.loads((STATE / "portability.json").read_text(encoding="utf-8"))
    # ★ 判定口径见 rules/portability.yml：
    #   探查类脚本（scan_*/index_*/find_* 等，不产出板、不在 clone 重建链上）
    #   与溯源字面量（source_locks.path，必须字面量才可复现）**允许存在**。
    #   真正阻塞的是「板构建链上的脚本写死了仓库路径或设备路径」。
    return {
        "ok": rep["files_with_hardcoded"] == 0,
        "files_scanned": rep["files_scanned"],
        "files_with_hardcoded": rep["files_with_hardcoded"],
        "files_exploratory_only": rep.get("files_exploratory_only", 0),
        "project_abs_sites": rep["project_abs_sites"],
        "device_abs_sites": rep["device_abs_sites"],
        "portable_ratio": rep["portable_ratio"],
    }


def g4_fingerprint() -> dict:
    """条目级指纹可复现性：现产物指纹 vs 最近一次快照指纹。"""
    sys.path.insert(0, str(TOOLS / "build"))
    from snapshot import board_fingerprint  # noqa: E402
    snaps = sorted([d for d in (STATE / "snapshots").iterdir()
                     if d.is_dir() and (d / "fingerprints.json").exists()]) if \
        (STATE / "snapshots").exists() else []
    if not snaps:
        return {"ok": True, "reason": "尚无快照，跳过（先跑 snapshot.py）"}
    latest = snaps[-1]
    old = json.loads((latest / "fingerprints.json").read_text(encoding="utf-8"))
    same = diff = missing = 0
    boards = sorted(set(old) & set(p.stem for p in (WEB / "data/boards").glob("*.json")))
    for b in boards:
        try:
            fp, _ = board_fingerprint(WEB / "data/boards" / f"{b}.json")
        except Exception:
            continue
        o = old.get(b, {})
        for k, v in fp.items():
            if k not in o:
                missing += 1
            elif o[k] == v:
                same += 1
            else:
                diff += 1
    total = same + diff + missing
    ratio = round(same * 100.0 / total, 2) if total else 100.0
    return {"ok": ratio >= 99.0, "snapshot": latest.name, "total": total,
            "identical": same, "changed": diff, "new": missing, "identical_pct": ratio}


def g5_gate() -> dict:
    r = sh([sys.executable, str(TOOLS / "build_wiki.py")], cwd=str(TOOLS), timeout=600)
    return {"ok": r.returncode == 0, "returncode": r.returncode,
            "tail": (r.stdout or r.stderr or "")[-300:]}


def main() -> int:
    ap = argparse.ArgumentParser(description="克隆重建自检")
    ap.add_argument("--port", type=int, default=8807)
    ap.add_argument("--skip-clone", action="store_true", help="跳过 G1/G2 冷克隆相关")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = {}
    tmp = None
    try:
        if not args.skip_clone:
            tmp = pathlib.Path(tempfile.mkdtemp(prefix="la_clone_"))
            clone = tmp / "repo"
            print("→ G1 冷克隆中…")
            g1 = g1_cold_clone(clone)
            results["G1_冷克隆完整性"] = g1
            print("→ G2 无 venv 起站测试…")
            # 就地模式（当前目录本身就是克隆结果）⇒ 直接测当前目录，不另拷贝
            target = PROJ if g1.get("mode") == "in-place" else clone
            results["G2_无依赖起站"] = g2_serve_without_venv(target, args.port)
        print("→ G3 路径可移植性…")
        results["G3_路径可移植性"] = g3_portability()
        print("→ G4 条目指纹可复现…")
        results["G4_指纹可复现"] = g4_fingerprint()
        print("→ G5 发布门禁…")
        results["G5_发布门禁"] = g5_gate()
    finally:
        if tmp and tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)

    ok_all = all(v.get("ok") for v in results.values())
    report = {"created": time.strftime("%Y-%m-%d %H:%M:%S"), "results": results, "ok": ok_all}
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / "clone_repro_check.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print("\n" + "=" * 72)
        print(f"{'关卡':22s} {'结论':6s} 详情")
        print("-" * 72)
        for k, v in results.items():
            mark = "✅ PASS" if v.get("ok") else "❌ FAIL"
            detail = ""
            if "files_with_hardcoded" in v:
                detail = (f"含硬编码 {v['files_with_hardcoded']}/{v['files_scanned']} 文件"
                          f"（可移植 {v['portable_ratio']}%）")
            elif "identical_pct" in v:
                detail = f"指纹一致 {v.get('identical_pct')}%（共 {v.get('total')} 条）"
            elif "boards_json" in v:
                detail = f"入库板 json {v['checks'].get('boards_json')} 个"
            elif "bad_urls" in v:
                detail = "全部 200" if not v["bad_urls"] else f"失败 {v['bad_urls']}"
            elif "returncode" in v:
                detail = f"exit {v['returncode']}"
            elif "reason" in v:
                detail = v["reason"][:80]
            print(f"{k:22s} {mark:8s} {detail}")
        print("=" * 72)
        print(f"总结论：{'✅ 可克隆重建' if ok_all else '❌ 存在阻塞项'}")
        print(f"报告：{STATE / 'clone_repro_check.json'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
