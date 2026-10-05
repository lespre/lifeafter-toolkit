# -*- coding: utf-8 -*-
"""①-4 名字还原：游戏内路径 → 64 位 fid → 索引里的【容器 + 行号】。

## 机制（2026-09-27 实测成立，推翻旧结论）

    fid = murmur3_x86_32(path_ascii, 0x77777777) << 32
        | murmur3_x86_32(path_ascii, 0x66666666)

哈希实现**不在本模块重写**：直接调 `toolkit_core.path_fid`（全项目唯一实现）。

### 三条实测规矩（本模块按此写死，不再试别的写法）

1. **路径形式 = 包内相对路径原样拼**（UI 类带 `ui/` 前缀）。
   「剥前导目录」实测 0% 命中，「补容器名」也不对 —— 所以本模块**不做变体猜测**。
2. **算哈希前 `/` 必须换 `\\`** —— `path_fid.fid_of(normalize_sep=True)` 已默认完成。
3. **优先查索引的 `fid_hex` 列**（`idx_entries_fid` 上有索引）——
   这是快路径；索引不在或缺列时**明确报错，不静默降级**（见 `IndexUnavailable`）。

## 旧结论为什么错

旧结论「GPK 首字段=内容指纹、名字永久不可还原」是在**只算一条 seed** 的前提下得的。
双 seed 拼 64 位后，拿 220,406 条字典路径抽 400 条去索引查：原样命中 100 条（25.0%）。
命中样例（全是 .gpk —— 本客户端 60 容器里 58 个是 .gpk）：

    effect\\fx\\guochang\\fx\\ar_laiwenshi_dimian.sfx  → res\\effect_01.gpk row 8311
    ui/renwu_icon/xinshoujiaocheng/img_jiaocheng162_s.jpg → res\\ui_01.gpk row 71678
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from toolkit_core.path_fid import KNOWN_EXTS, fid_of, murmur3_x86_32

#: 一条 SQL 里给多少个 fid 做 IN 查询（SQLite 变量数上限保守取值）
CHUNK = 500
#: 单个文本文件最多读多少字节（防一把读进几百 MB 的产物）。
#: ★ 2026-09-30：改为可调（LA_NAMES_MAX_FILE_MB）。默认 64 MB 不够用 ——
#:   本轮宽开采里 F=热更快照 raw（script.py314.lc.npk 135 MB）、
#:   G=站点 common_item_text_sources.json（94 MB）都超过 64 MB，会被整份跳过。
MAX_FILE_BYTES = int(os.environ.get("LA_NAMES_MAX_FILE_MB", "64")) * 1024 * 1024
#: 每个开采源最多扫多少个文件。★ 0 = 不限。
#:   默认 5000 是「只挖一个角落」的旧值：脚本层主体有 10 万级 .bin，
#:   按 5000 截断后 `files_read` 会停在 5,010 —— 那不是「源里没东西」，
#:   是扫描被上限砍掉了。宽开采必须显式放开（LA_NAMES_MAX_FILES=0）。
MAX_FILES_PER_SOURCE = int(os.environ.get("LA_NAMES_MAX_FILES", "5000"))
#: 开采源里认哪些后缀
TEXT_EXTS = {".txt", ".list", ".lst", ".csv", ".md", ".json", ".jsonl", ".log", ".ini", ".cfg"}
#: ★ 2026-09-30：二进制文本载体（按 bytes 读、utf-8 replace）—— 脚本层与资源块的
#: **资源路径字面量全在这些文件里**，白名单只认纯文本会把它们整个跳过
#: （实测：7 个源只读成 5,010 个文件、候选仅 13,369 条）。
BINARY_TEXT_EXTS = {".bin", ".py", ".nxs", ".lc", ".pyc", ".bytes", ".dat", ".xml", ".meta",
                    # ★ 2026-09-30 宽开采补：只在这批点名的源里出现、且确实带文本的载体
                    ".js",       # 04_站点/web/data（58 个）
                    ".marshal",  # 两个脚本层 _未命名 目录（Python marshal 转储，含字符串常量）
                    ".csb"}      # ui 的 Cocos Studio 二进制（含资源名）
SCAN_EXTS = TEXT_EXTS | BINARY_TEXT_EXTS
#: 遍历开采源时跳过的目录名（大件产物 / 缓存，无差别递归会被拖死）
SKIP_DIRS = {"__pycache__", ".git", ".venv", "node_modules", "_归档", "25_全量拆包",
             "20_提取", "site_data", "site_analysis", "site_artifacts"}

HEX16 = re.compile(r"^[0-9A-Fa-f]{16}$")
_EXT_ALT = "|".join(sorted((e.lstrip(".") for e in KNOWN_EXTS), key=len, reverse=True))
#: 从自由文本里捞「像路径的东西」：至少含一个分隔符，且结尾是已知资源后缀。
_TOKEN_RE = re.compile(r"[A-Za-z0-9_\-./\\\u4e00-\u9fff]{2,240}?\.(?:%s)" % _EXT_ALT, re.I)


class IndexUnavailable(RuntimeError):
    """索引库不存在 / 打不开 / 缺 fid_hex 列 —— 明确报错，不静默降级。"""


# ── 哈希（唯一实现来自 path_fid） ───────────────────────────────
def fid_hex(path: str) -> str:
    """路径 → 16 位大写 HEX。★ `/` → `\\` 由 fid_of 的 normalize_sep=True 完成。"""
    return "%016X" % fid_of(path)


def norm_path(p: str) -> str:
    """清掉引号/逗号等包裹，并把分隔符统一成反斜杠（规矩 2）。"""
    return p.strip().strip('"\',;:').replace("/", "\\")


def hash_selftest() -> dict:
    """算法自检：空串采样 + 三条已被索引核对过的 ground truth。

    ★ ground truth 不是「算出来再抄回来的」——两条路径的 fid 已由索引里真实存在的
      (容器, 行号) 反向核对（见模块头）。所以这里能抓住「算法被改坏 / 分隔符没归一」。
    """
    known = (
        (r"ui/renwu_icon/xinshoujiaocheng/img_jiaocheng162_s.jpg", "13248644DF9CD05B"),
        (r"ui\renwu_icon\xinshoujiaocheng\img_jiaocheng162_s.jpg", "13248644DF9CD05B"),
        (r"effect\fx\guochang\fx\ar_laiwenshi_dimian.sfx", "52EC2D0685131318"),
    )
    mismatch = []
    for path, want in known:
        try:
            got = fid_hex(path)
        except ValueError as exc:
            mismatch.append({"path": path, "error": type(exc).__name__})
            continue
        if got != want:
            mismatch.append({"path": path, "got": got, "want": want})
    empty = murmur3_x86_32(b"", 0)
    if empty != 0:
        mismatch.append({"probe": "murmur3(b'', 0)", "got": empty, "want": 0})
    return {"ok": not mismatch, "checked": len(known) + 1, "mismatch": mismatch}


# ── 索引（只读打开 + 结构校验） ─────────────────────────────────
def open_index(db) -> sqlite3.Connection:
    db = Path(db)
    if not db.is_file():
        raise IndexUnavailable("索引库不存在：%s（先跑 `run_all.py index build`）" % db)
    try:
        return sqlite3.connect("file:%s?mode=ro" % db.as_posix(), uri=True)
    except sqlite3.Error as exc:                       # noqa: BLE001
        raise IndexUnavailable("索引库打不开：%s（%s）" % (db, exc)) from exc


def verify_schema(conn: sqlite3.Connection) -> dict:
    """确认 entries.fid_hex 存在 —— 缺了就直接报错，不猜、不降级去扫全库。"""
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='entries'").fetchone()
    if not row:
        raise IndexUnavailable("索引库里没有 entries 表")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(entries)")]
    if "fid_hex" not in cols:
        raise IndexUnavailable("entries 表没有 fid_hex 列（旧版索引）—— 名字还原查不了，不降级")
    indexes = [r[1] for r in conn.execute("PRAGMA index_list(entries)")]
    return {"columns": cols, "indexes": indexes,
            "fid_indexed": any("fid" in (n or "") for n in indexes)}


def lookup(target: str, db, *, limit: int = 20) -> dict:
    """一个路径（或 16 位 fid）→ 容器 + 行号。查不到就是 found=False，如实返回。"""
    raw = (target or "").strip()
    if not raw:
        raise ValueError("没有给路径")
    mode = "fid" if HEX16.match(raw) else "path"
    fid = raw.upper() if mode == "fid" else fid_hex(raw)
    conn = open_index(db)
    try:
        schema = verify_schema(conn)
        rows = conn.execute(
            "SELECT container,row_index,kind,flag,decoded FROM entries "
            "WHERE fid_hex=? LIMIT ?", (fid, int(limit))).fetchall()
        # ★ 总行数取 containers 表的 rows 之和（60 行，1.5 ms），不是 `count(*) entries`
        #   —— 后者要 2.3M 行的全表统计（实测 427 ms），主页轮询路径上付不起。
        #   两者实测一致（sum(rows)==count(*)==2,300,843）。
        total = conn.execute("SELECT sum(rows) FROM containers").fetchone()[0]
    finally:
        conn.close()
    hits = [{"container": c, "row_index": r, "kind": k, "flag": f, "decoded": d}
            for (c, r, k, f, d) in rows]
    return {"input": raw, "mode": mode, "fid": fid, "found": bool(hits), "hits": hits,
            "index_rows": total, "db": str(db), "fid_indexed": schema["fid_indexed"]}


def hits_for_fids(conn: sqlite3.Connection, fids, chunk: int = CHUNK) -> dict:
    """批量查一批 fid → {fid: [(container, row_index)]}。分块 IN，避免变量数上限。"""
    fids = list(fids)
    out: dict[str, list] = {}
    for i in range(0, len(fids), chunk):
        part = fids[i:i + chunk]
        sql = ("SELECT fid_hex,container,row_index FROM entries WHERE fid_hex IN (%s)"
               % ",".join("?" * len(part)))
        for fid, container, row in conn.execute(sql, part):
            out.setdefault(fid, []).append((container, row))
    return out


# ── 字典开采 ───────────────────────────────────────────────────
def extract_paths(text: str) -> set:
    """从一段自由文本里捞「像包内相对路径的 token」。

    ★ 只做最保守的取法：含分隔符 + 结尾是已知资源后缀。不做大小写/前缀猜测，
      所以捞出来的都能直接拿去查索引，不产生「看着像但其实不是」的噪声条目。
    """
    out = set()
    for m in _TOKEN_RE.finditer(text):
        t = norm_path(m.group(0))
        if "\\" not in t or ".." in t:
            continue
        if t.startswith("\\") or any(tok in ("", ".", "..") for tok in t.split("\\")):
            continue
        out.add(t)
    return out


def _iter_files(src: Path, cap: int | None = None):
    if cap is None:
        cap = MAX_FILES_PER_SOURCE          # ★ 0 = 不限
    if src.is_file():
        yield src
        return
    if not src.is_dir():
        return
    n = 0
    for p in sorted(src.rglob("*")):
        if cap and n >= cap:
            return
        if not p.is_file() or p.suffix.lower() not in SCAN_EXTS:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        n += 1
        yield p


def _read_file_paths(path: Path):
    """一个文件 → (路径集合, 错误串)。读不动就如实报错，不算成功。"""
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return set(), "文件过大（>%d MB），跳过" % (MAX_FILE_BYTES // 2 ** 20)
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return set(), "读失败：%s" % exc
    return extract_paths(text), None


def build(sources, out, *, db=None, limit=None, workers: int | None = None,
          force: bool = False) -> dict:
    """开采文本产物 → 建/扩字典（path → fid_hex）。默认不覆盖已有输出。

    返回报告 dict：`ok` 为假表示「跑了但有错」（未命中的源 / 索引不可用），
    绝不因为「大部分成功」就把失败咽下去。

    workers：★ 不给就走智能调度（`throttle.global_jobs("light")`）——
             读文本产物属轻任务（纯文本、单文件不大），可以吃满预算。
    """
    started = time.time()
    out = Path(out)
    if out.exists() and not force:
        raise FileExistsError(
            "输出已存在，未覆盖：%s\n⇒ 要覆盖请显式加 --force（默认不覆盖是硬约定）" % out)
    srcs = [Path(s) for s in sources]
    files, missing = [], []
    for s in srcs:
        if s.is_file() or s.is_dir():
            files.extend(_iter_files(s))
        else:
            missing.append(str(s))

    paths: set = set()
    errors: dict[str, str] = {}
    # ★ 智能调度：并发数不给就按硬件自动定（读文本产物 = 轻任务）
    if workers is None:
        try:
            from toolkit_core import throttle as _TH
            workers = _TH.global_jobs("light")
        except Exception:
            workers = 4
    workers = max(1, int(workers))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for f, (got, err) in zip(files, pool.map(_read_file_paths, files)):
            if err:
                errors[str(f)] = err
            paths |= got

    ordered = sorted(paths)
    if limit and len(ordered) > int(limit):
        # ★ 按【等距抽样】取 N 条，不是取"字典序前 N 条"：
        #   实测 sorted() 前 400 条命中 0%（同一批路径随机抽 400 条是 25%）——
        #   字典序靠前的名字正好都不是这个客户端的资源。等距抽样既可复现，
        #   又能真实反映整批的命中水平，不会给出误导性的 0%。
        step = len(ordered) / float(int(limit))
        ordered = [ordered[int(i * step)] for i in range(int(limit))]

    entries = {}
    bad_paths = []
    for p in ordered:
        try:
            entries[p] = fid_hex(p)
        except ValueError as exc:
            bad_paths.append({"path": p, "error": type(exc).__name__})
    # fid 去重（同一 fid 保留最短的书写形式，通常是路径更规范的写法）
    by_fid: dict[str, str] = {}
    for p, f in entries.items():
        old = by_fid.get(f)
        if old is None or len(p) < len(old):
            by_fid[f] = p
    entries = {p: f for f, p in sorted(by_fid.items(), key=lambda kv: kv[1])}

    hit_stats = None
    index_error = None
    if db is not None and entries:
        try:
            conn = open_index(db)
            try:
                verify_schema(conn)
                hits = hits_for_fids(conn, list(entries.values()))
            finally:
                conn.close()
            per_container: dict[str, int] = {}
            hit = 0
            for p, f in entries.items():
                if f in hits:
                    hit += 1
                    for container, _row in hits[f]:
                        per_container[container] = per_container.get(container, 0) + 1
            hit_stats = {"hit": hit, "total": len(entries),
                         "rate": (hit / len(entries)) if entries else None,
                         "containers": dict(sorted(per_container.items(),
                                                   key=lambda kv: -kv[1]))}
        except IndexUnavailable as exc:
            index_error = str(exc)

    report = {
        "action": "build", "ok": bool(entries) and not missing and not index_error,
        "out": str(out), "sources": [str(s) for s in srcs],
        "missing_sources": missing, "files_read": len(files) - len(errors),
        "file_errors": errors, "candidates": len(paths), "kept": len(entries),
        "limit": limit, "workers": workers,
        "unencodable": bad_paths,
        "index": str(db) if db is not None else None,
        "index_error": index_error, "hits": hit_stats,
        "seconds": round(time.time() - started, 3),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "sources": [str(s) for s in srcs], "count": len(entries),
               "hits": (hit_stats or {}).get("hit"),
               "entries": entries,
               "entry_list": [{"path": p, "fid": f} for p, f in entries.items()]}
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    report["out_bytes"] = out.stat().st_size
    return report


# ── 字典读取（两种落盘格式并存，读取端必须都认） ────────────────
#   实测 names/ 下【两种格式并存】（2026-09-28 直接读文件头核对）：
#     ① 裸映射 `{fid_hex: 路径}`              —— v2…v13 全是这个（v13 = 1,061,631 条）
#     ② 带包装 `{…, "entries": {路径: fid_hex}}` —— `names build` 的输出（213,996 条）
#   旧 stats() 只认②，拿 v13 去读 ⇒ `d.get("entries")` 是 None ⇒ 静默读成 0 条，
#   而哈希自检仍然通过（自检跟字典无关）—— 这正是「230 万行索引 + 86 MB 字典 = 0 条」的成因。
#   判向靠【键本身】：键是 16 位 HEX 就是①，否则是②。不猜、不靠文件名。
def dict_format(payload) -> str:
    """字典 payload 的落盘格式：'wrapped'（build 输出） 或 'flat'（裸 {fid: 路径}）。"""
    if isinstance(payload, dict) and isinstance(payload.get("entries"), dict):
        return "wrapped"
    return "flat"


def fid_map(payload) -> dict:
    """任意落盘格式 → `{fid_hex: 路径}` —— 字典的【行】，无损。

    ★ 这是统计口径的基准（规模 / 命中率都按行算）；`entries_of` 是有损的路径视图。
    """
    if not isinstance(payload, dict):
        raise ValueError("字典格式不对：顶层不是 JSON 对象")
    table = payload.get("entries") if dict_format(payload) == "wrapped" else payload
    if not table:
        return {}
    if HEX16.match(next(iter(table))):            # ① 裸映射：键就是 fid
        return {k.upper(): v for k, v in table.items() if isinstance(v, str)}
    return {str(v).upper(): k for k, v in table.items() if isinstance(v, str)}   # ② 包装


def entries_of(payload) -> dict:
    """任意落盘格式 → `{路径: fid_hex}`（路径为键的视图）。

    ★ 有损：实测 v13 有 15,807 条路径各自对应 2 个 fid（1,061,631 行 → 1,045,803 个键）。
      要报规模/命中率请用 `fid_map`（无损行口径），别用这里。
    """
    return {p: f for f, p in fid_map(payload).items()}


def stats(dict_path, db) -> dict:
    """字典规模 / 命中多少条 / 各容器覆盖率排行（命中数是现场查索引，不读旧记录）。"""
    dict_path = Path(dict_path)
    if not dict_path.is_file():
        raise FileNotFoundError("字典不存在：%s（先跑 `names build`）" % dict_path)
    d = json.loads(dict_path.read_text(encoding="utf-8"))
    fmt = dict_format(d)
    # ★ 口径 = 字典的【行】数（一个 fid → 一条路径），不是「去重后的路径数」：
    #   实测 v13 有 15,807 条路径各自对应 2 个 fid（文件 1,061,631 行 / 唯一路径 1,045,803 条）。
    #   build 的包装格式入库时本就按 fid 去重 —— 两种格式的 count 口径必须一致。
    by_fid = fid_map(d)                           # {fid_hex: 路径}
    n_paths = len(set(by_fid.values()))
    out = {"action": "stats", "dict": str(dict_path), "count": len(by_fid),
           "dict_format": fmt, "unique_paths": n_paths,
           # 裸映射格式没有元信息 —— 如实报 None，不冒充「建于 None 的字典」
           "built": d.get("built") if fmt == "wrapped" else None,
           "sources": (d.get("sources") or []) if fmt == "wrapped" else [],
           "index": str(db),
           "selftest": hash_selftest()}
    conn = open_index(db)
    try:
        verify_schema(conn)
        hits = hits_for_fids(conn, list(by_fid))
        out["index_rows"] = conn.execute("SELECT count(*) FROM entries").fetchone()[0]
    finally:
        conn.close()
    per_container: dict[str, int] = {}
    hit = 0
    for f in by_fid:
        if f in hits:
            hit += 1
            for container, _row in hits[f]:
                per_container[container] = per_container.get(container, 0) + 1
    out["hit"] = hit
    out["miss"] = len(by_fid) - hit
    out["rate"] = (hit / len(by_fid)) if by_fid else None
    out["containers"] = dict(sorted(per_container.items(), key=lambda kv: -kv[1]))
    out["containers_covered"] = len(per_container)
    out["ok"] = True
    return out
