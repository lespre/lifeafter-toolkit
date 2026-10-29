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
WEB = PROJ / "02_wiki" / "web"
TOOLS = WEB / "tools"
DET = PROJ / "01_索引与产物" / "30_分析" / "热更检测"
PY = sys.executable
INDEX_CLI = PROJ / "00_规范与工具/工具" / "工具库" / "00_共享核心" / "命令行" / "pe全量索引.py"
FETCH = PROJ / "00_规范与工具/工具" / "工具库" / "01_解码定位复原" / "图集与取图"


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


# ---------------- board ----------------
def cmd_board(a) -> int:
    """板块工具：check 校验 / run 跑构建脚本。"""
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    sys.path.insert(0, str(WEB / "tools"))
    if a.action == "check" and a.target:
        import json as _json
        bp = WEB / "data/boards" / (a.target + ".json")
        if not bp.is_file():
            print("板块不存在：", bp)
            return 2
        d = _json.loads(bp.read_text(encoding="utf-8"))
        meta, items = d.get("meta") or {}, d.get("items") or []
        errs = []
        for k in ("name", "category", "package_sha", "evidence", "provenance"):
            if not meta.get(k):
                errs.append("meta 缺 %s" % k)
        if len(str(meta.get("package_sha", ""))) != 64:
            errs.append("package_sha 非 64 位")
        ids = [i.get("id") for i in items]
        if len(ids) != len(set(ids)):
            errs.append("存在重复 id")
        for it in items:
            if "table-absent" in (it.get("status_tags") or []):
                continue
            prov = it.get("provenance") or {}
            miss = [k for k in ("source_id", "source_lock_sha256", "table", "row_key",
                                "field_refs", "name_source", "upstream", "locator_chain")
                    if not prov.get(k)]
            if miss:
                errs.append("%s provenance 缺 %s" % (it.get("id"), ",".join(miss)))
                break
        print("板块 %s ｜ 条目 %d ｜ %s" % (a.target, len(items), "通过" if not errs else "有问题"))
        for e in errs[:10]:
            print("  -", e)
        return 0 if not errs else 1
    if a.action == "run" and a.target:
        import runpy
        script = Path(a.target)
        if not script.is_absolute():
            script = (WEB / "tools" / a.target) if (WEB / "tools" / a.target).is_file() else script
        if not script.is_file():
            print("脚本不存在：", script)
            return 2
        sys.argv = [str(script)]
        runpy.run_path(str(script), run_name="__main__")
        return 0
    print("用法：la.py board check <board_id> | la.py board run <builder.py>")
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


TOOLKIT = PROJ / "00_规范与工具/工具/工具库/00_共享核心/命令行/toolkit_cli.py"


def _toolkit(args: list[str], label: str) -> int:
    return run(label, [TOOLKIT] + args)




# ---------------- profile 配置档案 ----------------

def _load_profiles():
    import yaml
    f = PROJ / "profiles.yml"
    if not f.is_file():
        return {}, None
    data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    return data.get("profiles") or {}, data.get("default")


def apply_profile(name: str | None) -> str | None:
    """切换档案：改 DET（索引目录）与 TREE（还原树）两个全局。"""
    global DET, TREE
    profiles, default = _load_profiles()
    if not profiles:
        return None
    key = name or default
    cfg = profiles.get(key)
    if not cfg:
        print("未知档案：%s（可用：%s）" % (key, ", ".join(profiles)))
        return None
    if cfg.get("index_dir"):
        DET = PROJ / cfg["index_dir"]
    if cfg.get("tree"):
        TREE = PROJ / cfg["tree"]
    return key




# ---------------- source 数据源 ----------------

def cmd_source(a) -> int:
    import yaml
    f = PROJ / "profiles.yml"
    cfg = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    sources = cfg.get("sources") or {}
    cur = cfg.get("source") or "pe"

    if a.action in ("list", "detect"):
        print("当前数据源：%s" % cur)
        print()
        for name, v in sources.items():
            cdata = PROJ / (v.get("cdata") or "")
            idx = PROJ / (v.get("index") or "")
            tree = PROJ / (v.get("tree") or "")
            ok_c = cdata.is_dir()
            n_tab = len(list(cdata.glob("*.py"))) if ok_c else 0
            ok_i = idx.is_file()
            mark = "*" if name == cur else " "
            print("%s %-10s %s" % (mark, name, v.get("label", "")))
            print("    表根  %-6s %s（%d 张表）" % ("可用" if ok_c else "缺失", cdata, n_tab))
            print("    索引  %-6s %s" % ("可用" if ok_i else "缺失", idx.name))
            print("    树    %-6s %s" % ("可用" if tree.exists() else "缺失", v.get("tree")))
        return 0

    if a.action == "use":
        if a.name not in sources:
            print("未知数据源：%s（可用：%s）" % (a.name, ", ".join(sources)))
            return 2
        yaml.safe_dump  # noqa: B018
        text = f.read_text(encoding="utf-8")
        import re
        text = re.sub(r"^source: .*$", "source: %s" % a.name, text, count=1, flags=re.M)
        f.write_text(text, encoding="utf-8")
        print("数据源已切到：%s（%s）" % (a.name, sources[a.name].get("label", "")))
        return 0
    return 2

def cmd_profile(a) -> int:
    profiles, default = _load_profiles()
    if not profiles:
        print("没有 profiles.yml，先建一个")
        return 2
    if a.action == "list":
        for k, v in profiles.items():
            mark = "*" if k == default else " "
            print("%s %-20s %s" % (mark, k, v.get("label", "")))
            print("   树  %s" % v.get("tree", "-"))
            print("   索引 %s" % v.get("index_dir", "-"))
        return 0
    if a.action == "show":
        key = a.name or default
        cfg = profiles.get(key)
        if not cfg:
            print("未知档案：", key)
            return 1
        import yaml
        print(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
        return 0
    return 0

def cmd_find(a) -> int:
    """索引定位：逻辑路径 → (层, 包, 行, 大小)。PE 优先，PC 兜底。"""
    sys.path.insert(0, str(FETCH))
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    import sqlite3
    from toolkit_core.path_fid import fid_of

    stem = a.path
    for ext in (".ktx", ".dds", ".png", ".bc7", ".jpg"):
        if stem.lower().endswith(ext):
            stem = stem[: -len(ext)]
            break
    variants = [stem + e for e in (".ktx", ".dds", ".png", ".bc7")]
    if stem.endswith("_b"):
        variants += [stem[:-2] + "_s" + e for e in (".ktx", ".dds", ".png", ".bc7")]
    elif stem.endswith("_s"):
        variants += [stem[:-2] + "_b" + e for e in (".ktx", ".dds", ".png", ".bc7")]

    # PC 侧优先用分层索引（同 fid 多版本时取最新层并记录候选数）
    pc_layered = DET / "pc_index_layered.sqlite3"
    dbs = [("PE", DET / "pe_index.sqlite3"),
           ("PC", pc_layered if pc_layered.is_file() else DET / "pc_index.sqlite3")]
    found = []
    for layer, db in dbs:
        if not db.is_file():
            continue
        con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
        for v in variants:
            fid = "%016X" % (fid_of(v) & 0xFFFFFFFFFFFFFFFF)
            cols = "pack,row,decoded,flag"
            has_layer = False
            try:
                con.execute("select layer from rows limit 1")
                has_layer = True
                cols += ",layer,pack_no,candidates"
            except Exception:
                pass
            r = con.execute("select %s from rows where fid=? limit 1" % cols, (fid,)).fetchone()
            if r:
                extra = ""
                if has_layer and len(r) >= 7:
                    extra = " 层=%s 包号=%s 候选=%s" % (r[4], r[5], r[6])
                found.append({"layer": layer, "path": v, "pack": r[0], "row": r[1],
                              "decoded": r[2], "flag": r[3], "extra": extra})
                break
    if not found:
        if _find_table_fallback(a.path):
            return 0
        print("未命中：%s" % a.path)
        print("提示：先 la.py img best 看候选，或换扩展名（.ktx/.bc7）再试")
        return 1
    for f in found:
        print("[%s] %s → %s #%s（%s 字节, flag=%s）%s"
              % (f["layer"], f["path"], f["pack"], f["row"],
                 f["decoded"], f["flag"], f.get("extra", "")))
    return 0


def _find_table_fallback(raw: str):
    """兜底：配置表（com/cdata/*.py）查 name_index（经典服表名索引）+ npk 条目 + 还原树。

    命中返回 True。只读 cdata_name_index.sqlite3 / npk_index.sqlite3，不写任何库。
    """
    import sqlite3
    from pathlib import Path

    ni_db = DET / "cdata_name_index.sqlite3"
    if not ni_db.is_file():
        return False
    npk_db = DET / "npk_index.sqlite3"

    q = raw.replace("\\", "/").strip()
    ql = q.lower()
    stem = Path(ql).name.rsplit(".", 1)[0]
    cands = []
    if "/" in ql:
        cands.append(ql)
    cands += [stem, stem + ".nxs", "com/cdata/" + stem + ".nxs",
              "com/cdata/" + stem + ".py",
              "com/cdata/oversea/" + stem + ".py",
              "com/cdata/oversea/" + stem + ".nxs"]

    con = sqlite3.connect("file:%s?mode=ro" % str(ni_db).replace("\\", "/"), uri=True)
    hit = None
    for c in cands:
        r = con.execute("select name_index.fid,name_index.entry,name_index.path,"
                        "name_index.key,name_index.size,name_index.content_len "
                        "from name_alias join name_index on name_index.fid=name_alias.fid "
                        "where name_alias.alias=? limit 2", (c,)).fetchall()
        if len(r) == 1:
            hit = r[0]
            break
        if len(r) > 1:
            print("表名候选 %d 条（%s）：" % (len(r), c))
            for x in r[:5]:
                print("   %s  entry=%s  %s" % (x[0], x[1], x[2]))
            hit = r[0]
            break
    if hit is None:
        con.close()
        return False
    fid, entry, path, key, size, clen = hit
    print("[表] %s" % path)
    print("     经典服表索引 entry=%s key=%s size=%s 载荷=%s fid=%s"
          % (entry, key, size, clen, fid))

    if npk_db.is_file():
        try:
            nc = sqlite3.connect("file:%s?mode=ro" % str(npk_db).replace("\\", "/"), uri=True)
            loc = nc.execute("select layer,row,declared,flag from entries where file_id=? "
                             "order by layer desc", (fid,)).fetchall()
            nc.close()
            if loc:
                for layer, row, decl, flag in loc:
                    print("     npk  %-9s #%s（%s 字节, flag=%s）" % (layer, row, decl, flag))
            else:
                print("     npk  本仓 npk_index 无此 fid（该表未随当前客户端下发）")
        except Exception:
            pass

    tn = Path(path).as_posix()
    if tn.startswith("com/cdata/"):
        rel = tn
    else:
        rel = "com/cdata/" + Path(tn).name
    stem2 = rel.rsplit(".", 1)[0]
    shown = False
    for root in (PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照",
                 PROJ / "01_索引与产物/41_还原树/pe/配置_基线包"):
        if not root.is_dir():
            continue
        for ext in (".nxs", ".py"):
            f = root / (stem2 + ext)
            if f.is_file():
                print("     树   %s" % f)
                shown = True
                break
        if shown:
            break
    if not shown:
        print("     树   本地还原树无此表（源包独有或未解出）")
    con.close()
    return True


def cmd_locate(a) -> int:
    args = ["locate"]
    if a.container:
        args.append(a.container)
    if a.row is not None:
        args.append(str(a.row))
    if a.fid:
        args += ["--fid", a.fid]
    return _toolkit(args, "取行")


def cmd_tables(a) -> int:
    if a.action == "list":
        return _toolkit(["tables", "list"], "配置表清单")
    if a.action == "show" and a.name:
        return _toolkit(["tables", "find", a.name], "查表：%s" % a.name)
    if a.action == "export" and a.name:
        return _toolkit(["tables", "find", a.name], "导出表：%s" % a.name)
    print("用法：la.py tables list | show <表名> | export <表名>")
    return 2


def _idx_con(layer: str = "PE"):
    import sqlite3
    db = (DET / "pe_index.sqlite3") if layer == "PE" else (DET / "pc_index.sqlite3")
    if not db.is_file():
        return None
    return sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)


def cmd_info(a) -> int:
    """容器信息：行数 / flag 分布 / 名字覆盖 / 样例。"""
    con = _idx_con(getattr(a, "layer", "PE"))
    if con is None:
        print("索引不存在，先跑 la.py index build")
        return 2
    pack = a.pack
    rows = con.execute("select count(*) from rows where pack=?", (pack,)).fetchone()[0]
    if not rows:
        print("包里没有条目：", pack)
        return 1
    flags = con.execute("select flag,count(*) from rows where pack=? group by flag order by 2 desc limit 5",
                        (pack,)).fetchall()
    named = con.execute("select count(*) from rows where pack=? and name is not null and name<>''",
                        (pack,)).fetchone()[0]
    sample = con.execute("select row,name,decoded from rows where pack=? limit 3", (pack,)).fetchall()
    print("容器      %s" % pack)
    print("条目      %s" % format(rows, ","))
    print("有名字    %s（%.1f%%）" % (format(named, ","), named * 100.0 / rows))
    print("flag 分布 %s" % ", ".join("%s×%s" % (f, n) for f, n in flags))
    for r, nm, dec in sample:
        print("  行 %-8s %-60s %s 字节" % (r, (nm or "(无名)")[:60], dec))
    return 0


def cmd_list(a) -> int:
    """列出容器条目，支持 --filter 通配 / --limit / --json。"""
    import fnmatch
    import json as _json
    con = _idx_con(getattr(a, "layer", "PE"))
    if con is None:
        print("索引不存在")
        return 2
    q = "select row,fid,name,decoded,flag from rows where pack=?"
    args = [a.pack]
    if a.filter:
        q += " and name like ?"
        args.append("%" + a.filter.replace("*", "%") + "%")
    q += " order by row limit ?"
    args.append(a.limit)
    out = []
    for row, fid, name, dec, flag in con.execute(q, args):
        if a.filter and not fnmatch.fnmatch(name or "", a.filter):
            continue
        out.append({"row": row, "fid": fid, "name": name, "decoded": dec, "flag": flag})
    if a.json:
        Path(a.json).write_text(_json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("写出 %s（%d 条）" % (a.json, len(out)))
        return 0
    for o in out:
        print("%-8s %-58s %s" % (o["row"], (o["name"] or "(无名)")[:58], o["decoded"]))
    print("共 %d 条" % len(out))
    return 0


def cmd_img(a) -> int:
    """2D 图：best 看候选，export 导出，fill 按板块批量补图。"""
    if a.action == "fill":
        sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
        from toolkit_core import img_pipeline as IP
        boards = [a.path] if a.path else [p.stem for p in (PROJ / "02_wiki/web/data/boards").glob("*.json")]
        for b in boards:
            IP.fill_board(b)
        return 0
    path = a.path
    if not path:
        print("用法：la.py img best|export <逻辑路径> [-o 输出.png]")
        return 2
    sys.path.insert(0, str(FETCH))
    if a.action == "best":
        import pe_fetch_hires as H
        H.describe(path)
        return 0
    out = Path(a.out or (path.rsplit("/", 1)[-1] + ".png"))
    import pe_fetch as PE
    import pc_fetch as PC
    if PE.export(path, out):
        print("PE 命中 →", out)
        return 0
    if PC.export(path, out):
        print("PC 命中 →", out)
        return 0
    print("两侧都未命中：", path)
    return 1


def cmd_spine(a) -> int:
    script = ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描/spine_export.py"
    args = [script, "--filter", a.filter or ""]
    if a.out:
        args += ["--out", a.out]
    return run("Spine 三件套导出", args)


# ---------------- vehicle ----------------
VEH_DEEP = PROJ / "03_执行" / "vehicle_deep_extract.py"
VEH_LORE = PROJ / "03_执行" / "vehicle_lore_extract.py"
VEH_PARAMS = TOOLS / "build_vehicle_params.py"
VEH_LORE_BUILD = TOOLS / "build_vehicle_lore.py"


def _stream(name: str, args: list[str], cwd: Path = WEB) -> int:
    """实时输出版 run()：提取/回填耗时长，不能只留最后 4 行。"""
    print("\n▶ %s" % name)
    t0 = time.time()
    r = subprocess.run([PY, "-u"] + [str(x) for x in args], cwd=str(cwd))
    print("   %s (%.1fs)" % ("✓" if r.returncode == 0 else "✗ rc=%d" % r.returncode,
                             time.time() - t0))
    return r.returncode


def cmd_skin(a) -> int:
    """武器皮肤：fx-names 解析战斗表现正式名 / check 与现有产物比对。"""
    sys.path.insert(0, str(WEB))
    from pipelines.parsing import effect_show_names as ESN   # noqa: PLC0415

    default_out = PROJ / "01_索引与产物/30_分析/weapon_skin_effect_show.json"
    try:
        data, st = ESN.parse(a.cdata)
    except Exception as e:                                   # noqa: BLE001
        print("解析失败：%s" % e)
        return 2

    print("皮肤 %d ｜ 表现项 %d ｜ 记录 %d ｜ 字串池 %d"
          % (st["skins"], st["items"], st["records"], st.get("chs_strings", 0)))
    print("每皮肤项数 %s" % st["per_skin"])
    problems = ESN.self_check(data)
    print("自检 %s" % ("通过" if not problems else problems))

    out = Path(a.out) if a.out else default_out
    if a.action == "fx-names":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("写出 %s（%d B）" % (out, out.stat().st_size))
        return 0 if not problems else 1

    # check：与已有产物比对
    if not out.is_file():
        print("产物不存在：%s（先跑 skin fx-names）" % out)
        return 2
    old = json.loads(out.read_text(encoding="utf-8"))
    added = sorted(set(data) - set(old))
    gone = sorted(set(old) - set(data))
    changed = sorted(k for k in set(data) & set(old) if data[k] != old[k])
    print("比对 %s：新增皮肤 %d ｜ 消失 %d ｜ 内容变更 %d"
          % (out.name, len(added), len(gone), len(changed)))
    for label, keys in (("新增", added), ("消失", gone), ("变更", changed)):
        if keys:
            print("  %s %s%s" % (label, keys[:5], " …" if len(keys) > 5 else ""))
    bad = bool(added or gone or changed) or bool(problems)
    print("结论 %s" % ("与现有产物一致" if not bad else "存在差异"))
    return 1 if bad else 0


def cmd_vehicle(a) -> int:
    """（三）载具板深挖：extract 提取冻结产物 / build 回填到板。

    与 board_kit 类脚本不同，这两条链路有独立的冻结产物目录，
    所以走专用子命令而不是 board run。
    """
    root = a.root or str(PROJ)
    rc = 0

    # --only 取值随动作而异：extract 只认 deep/lore，build 只认 params/lore
    allowed = {"extract": ("deep", "lore"), "build": ("params", "lore")}[a.action]
    if a.only and a.only not in allowed:
        print("vehicle %s 不支持 --only %s（可选：%s）" % (a.action, a.only, " / ".join(allowed)))
        return 2

    if a.action == "extract":
        if a.only in (None, "deep"):
            args = [VEH_DEEP, "--root", root]
            if a.cd:
                args += ["--cd", a.cd]
            if a.out:
                args += ["--out", a.out]
            rc |= _stream("载具提取 第一期：魅力值 / 加速度 / 最大速度", args)
        if a.only in (None, "lore"):
            args = [VEH_LORE, "--root", root]
            if a.cd:
                args += ["--cd", a.cd]
            if a.out:
                args += ["--out", a.out]
            rc |= _stream("载具提取 第二期：描述 / 特技 / 氮气 / 生命量", args)
        return rc

    if a.action == "build":
        if a.only in (None, "params"):
            args = [VEH_PARAMS, "--root", root]
            if a.board:
                args += ["--board", a.board]
            if a.dry_run:
                args += ["--dry-run"]
            rc |= _stream("载具回填 第一期：魅力值 / 速度 / 等级属性", args)
        if a.only in (None, "lore"):
            args = [VEH_LORE_BUILD, "--root", root]
            if a.board:
                args += ["--board", a.board]
            if a.dry_run:
                args += ["--dry-run"]
            rc |= _stream("载具回填 第二期：描述 / 特技 / 氮气 / 生命量", args)
        if not a.dry_run:
            print("\n▸ 板已更新，记得刷新页面（缓存号见 board.html）：python la.py web build")
        return rc

    print("用法：la.py vehicle extract|build [--only deep|lore|params]")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(prog="la", description="明日之后拆包项目 CLI")
    sub = ap.add_subparsers(dest="cmd")

    ap.add_argument("--profile", help="配置档案名（见 la.py profile list）")

    src = sub.add_parser("source", help="数据源：list 检测 / use <pe|pc|documents>")
    src.add_argument("action", nargs="?", choices=["list", "use", "detect"], default="list")
    src.add_argument("name", nargs="?")

    pr = sub.add_parser("profile", help="配置档案：list / show <名>")
    pr.add_argument("action", nargs="?", choices=["list", "show"], default="list")
    pr.add_argument("name", nargs="?")

    sub.add_parser("doctor", help="环境自检：根/索引/CLI/服务")
    sub.add_parser("status", help="服务与数据概览")

    ix = sub.add_parser("index", help="索引：build / status")
    ix.add_argument("action", choices=["build", "status", "all"])

    fi = sub.add_parser("find", help="索引定位：逻辑路径 → 包/行")
    fi.add_argument("path")
    fi.add_argument("--json")

    lo = sub.add_parser("locate", help="取行：容器+行 或 --fid")
    lo.add_argument("container", nargs="?")
    lo.add_argument("row", nargs="?", type=int)
    lo.add_argument("--fid")

    tb = sub.add_parser("tables", help="配置表：list / show / export")
    tb.add_argument("action", choices=["list", "show", "export"])
    tb.add_argument("name", nargs="?")

    inf = sub.add_parser("info", help="容器信息：条目数/flag/名字覆盖/样例")
    inf.add_argument("pack")
    inf.add_argument("--layer", choices=["PE", "PC"], default="PE")

    ls = sub.add_parser("list", help="列出容器条目（--filter 通配 / --limit / --json）")
    ls.add_argument("pack")
    ls.add_argument("--filter")
    ls.add_argument("--limit", type=int, default=50)
    ls.add_argument("--json")
    ls.add_argument("--layer", choices=["PE", "PC"], default="PE")

    im = sub.add_parser("img", help="2D 图：best / export / fill（统一补图）")
    im.add_argument("action", choices=["best", "export", "fill"])
    im.add_argument("path", nargs="?")
    im.add_argument("-o", "--out")

    bd = sub.add_parser("board", help="板块：check / run")
    bd.add_argument("action", choices=["check", "run"])
    bd.add_argument("target", nargs="?")

    wb = sub.add_parser("web", help="站点：build / serve / shot / refresh / check / tidy")
    wb.add_argument("action", choices=["build", "serve", "shot", "refresh", "check", "tidy"])
    wb.add_argument("url", nargs="?")
    wb.add_argument("out", nargs="?")
    wb.add_argument("--port", type=int, default=8765)
    wb.add_argument("--width", type=int, default=1400)
    wb.add_argument("--height", type=int, default=900)
    wb.add_argument("--js")
    wb.add_argument("--all-tests", dest="all_tests", action="store_true")

    hf = sub.add_parser("hotfix", help="热更：plan / apply")
    hf.add_argument("action", choices=["plan", "apply", "report"])

    sp = sub.add_parser("spine", help="Spine 三件套导出")
    sp.add_argument("--filter", default="")
    sp.add_argument("--out")

    nk = sub.add_parser("npk", help="item_icon 图标库")
    nk.add_argument("action", choices=["export", "query"])
    nk.add_argument("image", nargs="?")
    nk.add_argument("--id", dest="image_id")

    wt = sub.add_parser("watch", help="监测：device / cdn / logcat")
    wt.add_argument("action", choices=["device", "cdn", "logcat"])
    wt.add_argument("--interval", type=int, default=0)

    tp = sub.add_parser("tool", help="透传 toolkit_cli（逃生舱）")
    tp.add_argument("rest", nargs=argparse.REMAINDER)

    vh = sub.add_parser("vehicle", help="（三）载具板深挖：extract 提取 / build 回填")
    vh.add_argument("action", choices=["extract", "build"])
    vh.add_argument("--only", choices=["deep", "lore", "params"],
                    help="只跑其中一期（extract: deep|lore ／ build: params|lore）")
    vh.add_argument("--root", help="项目根（默认 la.py 所在目录）")
    vh.add_argument("--cd", help="还原树 cdata 目录（仅 extract）")
    vh.add_argument("--out", help="冻结产物输出目录（仅 extract）")
    vh.add_argument("--board", help="板数据文件（仅 build）")
    vh.add_argument("--dry-run", action="store_true",
                    help="只算不写（仅 build）")

    sk = sub.add_parser("skin", help="武器皮肤：fx-names 解战斗表现正式名 / check 与现有产物比对")
    sk.add_argument("action", choices=["fx-names", "check"])
    sk.add_argument("--cdata", help="cdata 目录（默认按项目根推算，或 LA_CDATA）")
    sk.add_argument("--out", help="产物路径（默认 01_索引与产物/30_分析/weapon_skin_effect_show.json）")

    a = ap.parse_args()
    _pname = apply_profile(getattr(a, "profile", None))
    if _pname and getattr(a, "cmd", None) not in (None, "profile"):
        print("▸ 档案 %s" % _pname)
    if not a.cmd:
        print(BANNER)
        ap.print_help()
        return 0
    if a.cmd == "doctor":
        return cmd_doctor(a)
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "index":
        return cmd_index(a)
    if a.cmd == "find":
        return cmd_find(a)
    if a.cmd == "locate":
        return cmd_locate(a)
    if a.cmd == "tables":
        return cmd_tables(a)
    if a.cmd == "source":
        return cmd_source(a)
    if a.cmd == "profile":
        return cmd_profile(a)
    if a.cmd == "info":
        return cmd_info(a)
    if a.cmd == "list":
        return cmd_list(a)
    if a.cmd == "img":
        return cmd_img(a)
    if a.cmd == "board":
        return cmd_board(a)
    if a.cmd == "web":
        return cmd_web(a)
    if a.cmd == "hotfix":
        a.action = a.action
        return _toolkit(["hotfix", a.action], "热更 %s" % a.action)
    if a.cmd == "spine":
        return cmd_spine(a)
    if a.cmd == "vehicle":
        return cmd_vehicle(a)
    if a.cmd == "skin":
        return cmd_skin(a)
    if a.cmd == "npk":
        return cmd_npk(a)
    if a.cmd == "watch":
        if a.interval == 0:
            a.interval = 20 if a.action == "device" else 300
        return cmd_watch(a)
    if a.cmd == "tool":
        return _toolkit(a.rest, "toolkit")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
