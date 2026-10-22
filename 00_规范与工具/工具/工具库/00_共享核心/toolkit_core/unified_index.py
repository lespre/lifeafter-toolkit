# -*- coding: utf-8 -*-
"""统一文件索引：逻辑路径 -> 全部容器条目 -> 定点提取。

GPK/NPK 解析委托给已验证的 ``06_皮肤定位链/gpk_npk_index.py``；
FPK 条目流式导入现有 ``fpk_fid_index.json``。SQLite 只写派生索引，源包只读。
同一 fid 的全部命中都会返回；没有明确优先级时绝不自动取第一条。
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from toolkit_core.path_fid import fid_of as _fid_of  # 路径→fid 的唯一实现
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

SCHEMA_VERSION = 2   # v2：containers 增加 sha256 列（逐容器内容哈希，供 --deep 校验）
SUPPORTED_SUFFIXES = {".gpk", ".fpk", ".npk"}
# 16 位十六进制 fid（与 entries.fid_hex 同形）；用于让 find/extract/export 认得「直接给 fid」
_FID_RE = re.compile(r"[0-9A-F]{16}")


class IndexNotReady(RuntimeError):
    pass


class AmbiguousMatch(RuntimeError):
    pass


@dataclass(frozen=True)
class IndexHit:
    fid_hex: str
    container: str
    kind: str
    row: int
    offset: int
    payload_offset: int
    packed: int
    decoded: int
    flag: int
    source: str
    matched_path: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class FindResult:
    query: str
    candidates: tuple[str, ...]
    hits: tuple[IndexHit, ...]

    @property
    def status(self) -> str:
        return "MISS" if not self.hits else ("UNIQUE" if len(self.hits) == 1 else "AMBIGUOUS")

    def as_dict(self) -> dict:
        return {"query": self.query, "status": self.status,
                "candidate_count": len(self.candidates), "candidates": list(self.candidates),
                "hit_count": len(self.hits), "hits": [h.as_dict() for h in self.hits]}


def _verified_module_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py"


def load_verified_index_module():
    name = "_lifeafter_verified_gpk_npk_index"
    if name in sys.modules:
        return sys.modules[name]
    path = _verified_module_path()
    if not path.is_file():
        raise IndexNotReady(f"缺少已验证容器解析器：{path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise IndexNotReady(f"无法加载容器解析器：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def murmur3_x86_32(data: bytes, seed: int) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for off in range(0, end, 4):
        k = int.from_bytes(data[off:off + 4], "little")
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail, k = data[end:], 0
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if tail:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16; h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h & 0xFFFFFFFF


def path_fid(logical_path: str, *, encoding: str = "utf-8") -> int:
    """逻辑路径 → 64 位 fid。委托给唯一实现 toolkit_core.path_fid。

    ★ 2026-09-26：默认编码由 latin1 改为 utf-8。原因：latin1 编不出中文路径
      （实测直接抛），而 utf-8 对纯 ASCII 与 latin1 逐字节等价 ⇒
      改默认不会动到任何 ASCII 路径的结果，只是让中文路径从「报错」变成「能算」。
      归一分隔符（/ → \）保持：游戏内部存的是反斜杠。
    """
    return _fid_of(logical_path, encoding=encoding, normalize_sep=True)


def path_candidates(path: str, *, variants: bool = False, deep: bool = False) -> list[str]:
    canonical, out = path.strip().replace("/", "\\"), []
    def add(value):
        if value and value not in out: out.append(value)
    add(canonical)
    if not variants:
        return out
    stem, ext = os.path.splitext(canonical)
    for new_ext in ({".tga": (".dds", ".png"), ".dds": (".tga",),
                     ".png": (".tga",)}.get(ext.lower(), ())):
        add(stem + new_ext)
    if "\\" in canonical: add(canonical.split("\\", 1)[1])
    for value in list(out):
        add(value.lower()); add(value.upper()); add(value[:1].upper() + value[1:])
    if deep:
        for value in list(out):
            base, suffix = os.path.splitext(value)
            for extra in ("_lod01", "_lod02", "_lod1", "_1", "_high", "_preview"):
                add(base + extra + suffix)
    return out


def _iter_json_object_items(path: Path, object_name: str) -> Iterator[tuple[str, object]]:
    """流式读取超大 JSON 中的指定对象，避免一次载入 253 MB。"""
    marker, decoder = json.dumps(object_name) + ":", json.JSONDecoder()
    with path.open("r", encoding="utf-8") as handle:
        buf, pos, eof = "", 0, False
        def refill():
            nonlocal buf, pos, eof
            if pos: buf, pos = buf[pos:], 0
            block = handle.read(1 << 20)
            if not block: eof = True; return False
            buf += block; return True
        while marker not in buf:
            if eof: raise KeyError(f"{path} 中没有对象 {object_name!r}")
            if len(buf) > len(marker) * 2: buf = buf[-len(marker) * 2:]
            refill()
        pos = buf.index(marker) + len(marker)
        while True:
            while True:
                while pos < len(buf) and buf[pos] in " \r\n\t,{": pos += 1
                if pos < len(buf): break
                if not refill(): raise ValueError(f"{object_name!r} 对象意外结束")
            if buf[pos] == "}": return
            try: key, pos2 = decoder.raw_decode(buf, pos)
            except json.JSONDecodeError:
                if not refill(): raise
                continue
            pos = pos2
            while True:
                while pos < len(buf) and buf[pos] in " \r\n\t": pos += 1
                if pos < len(buf): break
                if not refill(): raise ValueError("键后缺少冒号")
            if buf[pos] != ":": raise ValueError(f"键后不是冒号，位置 {pos}")
            pos += 1
            while True:
                while pos < len(buf) and buf[pos] in " \r\n\t": pos += 1
                try: value, pos2 = decoder.raw_decode(buf, pos); break
                except json.JSONDecodeError:
                    if not refill(): raise
            pos = pos2
            yield str(key), value


def _inventory(root: Path) -> list[Path]:
    return sorted((p for p in root.rglob("*") if p.is_file()
                   and p.suffix.lower() in SUPPORTED_SUFFIXES), key=lambda p: str(p).lower())


def inventory_fingerprint(root: Path) -> tuple[str, int]:
    digest, files = hashlib.sha256(), _inventory(root)
    for path in files:
        stat = path.stat()
        rel = os.path.relpath(path, root).replace("/", "\\")
        digest.update(f"{rel}\0{stat.st_size}\0{stat.st_mtime_ns}\n".encode("utf-8"))
    return digest.hexdigest(), len(files)


def container_sha256(path: Path | str, chunk: int = 8 << 20) -> str:
    """整个容器文件的 sha256（流式，8 MB 一块）。

    ★ 为什么必须落到「读内容」：现有的 inventory_fingerprint 只用
      名字 + 大小 + mtime 拼哈希，一个字节的内容都不读。
      包内容变了但大小与 mtime 没变（或被工具保留）就检不出来 ——
      实测 C2 已确认这是真缺口。深层校验靠这个函数补上。
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def migrate_schema(conn: sqlite3.Connection) -> list[str]:
    """把旧库补到当前 schema。返回做了哪些改动（供如实报告）。"""
    done = []
    cols = [r[1] for r in conn.execute("PRAGMA table_info(containers)")]
    if "sha256" not in cols:
        conn.execute("ALTER TABLE containers ADD COLUMN sha256 TEXT")
        done.append("containers 增加 sha256 列")
    if done:
        conn.commit()
    return done


def initialize_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
      CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
      CREATE TABLE containers(container TEXT PRIMARY KEY,kind TEXT NOT NULL,bytes INTEGER,
        mtime_ns INTEGER,rows INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL,error TEXT,
        sha256 TEXT);
      CREATE TABLE entries(fid_hex TEXT NOT NULL,container TEXT NOT NULL,kind TEXT NOT NULL,
        row_index INTEGER NOT NULL,offset INTEGER NOT NULL,payload_offset INTEGER NOT NULL,
        packed INTEGER NOT NULL,decoded INTEGER NOT NULL,flag INTEGER NOT NULL,source TEXT NOT NULL,
        UNIQUE(kind,container,row_index));
    """)


def _set_meta(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta VALUES(?,?)",
                 (key, json.dumps(value, ensure_ascii=False, separators=(",", ":"))))


def _batches(rows: Iterable[tuple], size=50_000):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) >= size: yield batch; batch = []
    if batch: yield batch


def build_database(db_path: Path | str, *, res_root: Path | str,
                   fpk_index: Path | str | None = None,
                   include: Sequence[str] = ("gpk", "fpk", "npk"),
                   hash_containers: bool = True,
                   progress: Callable[[str], None] | None = print) -> dict:
    target, root = Path(db_path).resolve(), Path(res_root).resolve()
    fpk_path = Path(fpk_index).resolve() if fpk_index else None
    kinds = {x.lower() for x in include}
    if kinds - {"gpk", "fpk", "npk"}: raise ValueError(f"未知容器族：{kinds}")
    if not root.is_dir(): raise FileNotFoundError(f"资源根不存在：{root}")
    if "fpk" in kinds and (fpk_path is None or not fpk_path.is_file()):
        raise FileNotFoundError(f"FPK 索引不存在：{fpk_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".building")
    temp.unlink(missing_ok=True)
    conn, totals, failures = sqlite3.connect(temp), {"gpk": 0, "fpk": 0, "npk": 0}, []
    started = time.time()
    try:
        conn.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=MEMORY;")
        initialize_schema(conn)
        migrate_schema(conn)
        module = load_verified_index_module() if kinds & {"gpk", "npk"} else None
        items = ([c for c in module.scan_containers(str(root), "all")
                  if c["kind_hint"] in kinds and c["kind_hint"] != "fpk"]
                 if module is not None else [])
        for number, item in enumerate(items, 1):
            path, kind = Path(item["path"]), item["kind_hint"]
            rel = os.path.relpath(path, root).replace("/", "\\")
            try:
                if kind == "gpk":
                    rec, factory, _ = module._gpk_blockchain(str(path))
                    limits, cursor = [], 0
                    for block in rec.get("blocks", []):
                        cursor += int(block["entries"]); limits.append((cursor, int(block["payload_delta"])))
                    def rows():
                        block_pos = 0
                        for row, fid, off, packed, decoded, flag in factory():
                            while block_pos + 1 < len(limits) and row >= limits[block_pos][0]: block_pos += 1
                            delta = limits[block_pos][1] if limits else int(rec["payload_delta"])
                            yield (f"{fid:016X}", rel, kind, row, off, off + delta,
                                   packed, decoded, flag, "gpk-table-8u32")
                else:
                    rec, factory = module.parse_npk(str(path))
                    def rows():
                        for row, fid, off, packed, decoded, flag in factory():
                            yield (f"{fid:016X}", rel, kind, row, off, off,
                                   packed, decoded, flag, "npk-table-48b")
                count = 0
                for batch in _batches(rows()):
                    conn.executemany("INSERT INTO entries VALUES(?,?,?,?,?,?,?,?,?,?)", batch); count += len(batch)
                stat = path.stat()
                digest = container_sha256(path) if hash_containers else None
                conn.execute(
                    "INSERT OR REPLACE INTO containers"
                    "(container,kind,bytes,mtime_ns,rows,status,error,sha256) VALUES(?,?,?,?,?,?,?,?)",
                    (rel, kind, stat.st_size, stat.st_mtime_ns, count, "ok", None, digest))
                totals[kind] += count
                if progress: progress(f"[{number}/{len(items)}] {kind} {rel}: {count} rows")
            except Exception as exc:
                stat = path.stat(); failures.append({"container": rel, "kind": kind, "error": repr(exc)})
                digest = container_sha256(path) if hash_containers else None
                conn.execute(
                    "INSERT OR REPLACE INTO containers"
                    "(container,kind,bytes,mtime_ns,rows,status,error,sha256) VALUES(?,?,?,?,?,?,?,?)",
                    (rel, kind, stat.st_size, stat.st_mtime_ns, 0, "error", repr(exc), digest))
                if progress: progress(f"[ERROR] {kind} {rel}: {exc!r}")
            conn.commit()
        if "fpk" in kinds and fpk_path is not None:
            by_name = {}
            for path in _inventory(root): by_name.setdefault(path.name.lower(), []).append(path)
            counts, unresolved, skipped = {}, set(), 0
            def fpk_rows():
                nonlocal skipped
                for fid, value in _iter_json_object_items(fpk_path, "fid2info"):
                    if not isinstance(value, list) or len(value) < 8: continue
                    name = str(value[0])
                    if not name.lower().endswith(".fpk"): skipped += 1; continue
                    matches = by_name.get(Path(name).name.lower(), [])
                    def _size_ok(p):
                        try:
                            return p.stat().st_size >= int(value[2]) + int(value[3])
                        except OSError:
                            return False
                    viable = [p for p in matches if _size_ok(p)]
                    chosen = viable[0] if len(viable) == 1 else (matches[0] if len(matches) == 1 else None)
                    if chosen is None:
                        # ★ 修复（2026-09-26）：物理包解析不到时【不再写入条目】。
                        # 旧行为是照样 yield —— 当 fpk_fid_index.json 过期（例如客户端重装后
                        # FPK 被移除）时，会把两百万条幽灵条目灌进索引，导致 find 命中
                        # 当前客户端根本不存在的容器。诊断信息仍经 unresolved / containers
                        # 的 missing-container 保留。
                        unresolved.add(name)
                        skipped += 1
                        continue
                    rel = os.path.relpath(chosen, root).replace("/", "\\")
                    counts[rel] = counts.get(rel, 0) + 1
                    yield (str(fid).upper().zfill(16), rel, "fpk", int(value[1]), int(value[2]),
                           int(value[2]), int(value[3]), int(value[4]), int(value[7]), "fpk_fid_index")
            count = 0
            for batch in _batches(fpk_rows()):
                conn.executemany("INSERT OR IGNORE INTO entries VALUES(?,?,?,?,?,?,?,?,?,?)", batch); count += len(batch)
                if progress and count % 250_000 < len(batch): progress(f"[FPK] {count} rows")
            totals["fpk"] = count
            for rel, rows_count in counts.items():
                path = root / rel
                if path.is_file():
                    stat = path.stat()
                    values = (rel, "fpk", stat.st_size, stat.st_mtime_ns, rows_count, "ok", None,
                              container_sha256(path) if hash_containers else None)
                else: values = (rel, "fpk", None, None, rows_count, "missing-container",
                                "索引有条目但物理包未唯一解析", None)
                conn.execute(
                    "INSERT OR REPLACE INTO containers"
                    "(container,kind,bytes,mtime_ns,rows,status,error,sha256) VALUES(?,?,?,?,?,?,?,?)",
                    values)
            _set_meta(conn, "fpk_skipped_non_fpk_aliases", skipped)
            _set_meta(conn, "fpk_unresolved_container_names", sorted(unresolved))
            if progress: progress(f"[FPK] complete: {count} rows, unresolved names={len(unresolved)}")
        conn.execute("CREATE INDEX idx_entries_fid ON entries(fid_hex)")
        conn.execute("CREATE INDEX idx_entries_container_row ON entries(container,row_index)")
        fingerprint, file_count = inventory_fingerprint(root)
        for key, value in {"schema_version": SCHEMA_VERSION, "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "res_root": str(root), "inventory_fingerprint": fingerprint,
                           "inventory_file_count": file_count, "included_kinds": sorted(kinds),
                           "row_totals": totals, "failures": failures,
                           "builder": str(_verified_module_path())}.items(): _set_meta(conn, key, value)
        if fpk_path:
            stat = fpk_path.stat(); _set_meta(conn, "fpk_index", {"path": str(fpk_path), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
        _set_meta(conn, "build_seconds", round(time.time() - started, 3))
        conn.commit()
        if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok": raise RuntimeError("SQLite quick_check 失败")
    except Exception:
        conn.close(); temp.unlink(missing_ok=True); raise
    conn.close(); os.replace(temp, target)
    return {"database": str(target), "schema_version": SCHEMA_VERSION, "res_root": str(root),
            "row_totals": totals, "rows": sum(totals.values()), "failures": failures,
            "seconds": round(time.time() - started, 3), "bytes": target.stat().st_size}


class UnifiedFileIndex:
    def __init__(self, database: Path | str, *, res_root: Path | str | None = None):
        self.database = Path(database).resolve()
        if not self.database.is_file(): raise IndexNotReady(f"统一索引不存在：{self.database}")
        self.conn = sqlite3.connect(f"file:{self.database.as_posix()}?mode=ro", uri=True)
        self.conn.row_factory = sqlite3.Row
        if self.meta("schema_version") != SCHEMA_VERSION:
            self.close(); raise IndexNotReady("索引模式不兼容，请重建")
        self.res_root = Path(res_root or self.meta("res_root")).resolve()

    def close(self):
        if getattr(self, "conn", None) is not None: self.conn.close(); self.conn = None
    def __enter__(self): return self
    def __exit__(self, *_): self.close()
    def meta(self, key, default=None):
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return default if row is None else json.loads(row[0])

    def status(self, *, check_sources=True, deep=False) -> dict:
        """索引健康与过期检查。

        deep=False（默认，快层）：现有「名字+大小+mtime」指纹 + 逐容器 stat 对照。
            秒级。能抓到绝大多数变化，但抓不到「大小和 mtime 都没变、内容却变了」。
        deep=True（深层）：逐容器重算 sha256 与库内比对。
            要读全部容器字节（本项目 res 族约数十 GB），几十秒级。**这才是真校验。**
        """
        quick = self.conn.execute("PRAGMA quick_check").fetchone()[0]
        current = count = inventory_stale = fpk_index_stale = stale = None
        container_changed, container_missing, deep_checked = [], [], 0
        # 旧库可能还没有 sha256 列（schema v1）。这是「还没迁移」，不是「不该发生」，
        # 所以降级说明而不是抛 OperationalError。
        _cols = {r[1] for r in self.conn.execute("PRAGMA table_info(containers)")}
        has_sha = "sha256" in _cols
        _sha_expr = "sha256" if has_sha else "NULL"
        if check_sources and self.res_root.is_dir():
            current, count = inventory_fingerprint(self.res_root)
            inventory_stale = current != self.meta("inventory_fingerprint")
            # 逐容器对照（便宜：只 stat）
            for rel, bytes_, mtime_ns, sha in self.conn.execute(
                    "SELECT container,bytes,mtime_ns,%s FROM containers" % _sha_expr):
                path = self.res_root / rel
                try:
                    st = path.stat()
                except OSError:
                    container_missing.append(rel)
                    continue
                if st.st_size != bytes_ or st.st_mtime_ns != mtime_ns:
                    container_changed.append({"container": rel, "why": "大小或 mtime 变了"})
                elif deep and sha:
                    if container_sha256(path) != sha:
                        container_changed.append(
                            {"container": rel, "why": "内容变了（大小与 mtime 未变）"})
                    deep_checked += 1
            fpk_meta = self.meta("fpk_index")
            if fpk_meta:
                fpk_source = Path(fpk_meta["path"])
                if not fpk_source.is_file():
                    fpk_index_stale = True
                else:
                    stat = fpk_source.stat()
                    fpk_index_stale = (stat.st_size != fpk_meta["bytes"]
                                       or stat.st_mtime_ns != fpk_meta["mtime_ns"])
            stale = inventory_stale or bool(fpk_index_stale)
        return {"database": str(self.database), "schema_version": self.meta("schema_version"),
                "built_at": self.meta("built_at"), "res_root": str(self.res_root),
                "quick_check": quick, "rows": self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
                "row_totals": self.meta("row_totals", {}),
                "failed_containers": self.conn.execute("SELECT COUNT(*) FROM containers WHERE status!='ok'").fetchone()[0],
                "stored_inventory_fingerprint": self.meta("inventory_fingerprint"),
                "current_inventory_fingerprint": current, "current_inventory_file_count": count,
                "inventory_stale": inventory_stale, "fpk_index_stale": fpk_index_stale,
                "container_changed": container_changed,
                "container_missing": container_missing,
                "deep_checked": deep_checked,
                "hash_coverage": (self.conn.execute(
                    "SELECT COUNT(*) FROM containers WHERE sha256 IS NOT NULL").fetchone()[0]
                    if has_sha else None),
                "container_count": self.conn.execute(
                    "SELECT COUNT(*) FROM containers").fetchone()[0],
                "deep": bool(deep),
                "deep_available": bool(has_sha),
                "schema_note": (None if has_sha else
                                "本库还是旧 schema（containers 无 sha256 列）："
                                "深层校验不可用。跑一次 index build 迁移并填充哈希。"),
                "stale": (None if stale is None else bool(stale or container_changed
                                                          or container_missing))}

    def containers(self) -> list[dict]:
        """容器清单（构建期扫描结果，只读）。"""
        rows = self.conn.execute(
            "SELECT container, kind, bytes, rows, status FROM containers ORDER BY container").fetchall()
        return [{"container": r[0], "kind": r[1], "bytes": int(r[2] or 0),
                 "rows": int(r[3] or 0), "status": r[4] or ""} for r in rows]

    def find(self, logical_path: str, *, variants=False, deep=False) -> FindResult:
        # ★ 输入可以直接就是 fid。
        #   `export` / `extract` 的 --help 与 docstring 一直承诺「逻辑路径 / fid」两种输入，
        #   但旧实现一律把输入当【路径】做 path→fid 哈希 ⇒ 传 16 位十六进制 fid
        #   会被哈希成一个毫不相干的 fid、永远命中 0，用户看到的是「索引里也查不到」。
        #   判据取最保守的一种：形如 fid【且】库里确实有这条 ⇒ 才走 fid 直达；
        #   否则仍按路径处理（对既有输入行为零改动，不会把恰好像 hex 的路径吃掉）。
        raw = (logical_path or "").strip().upper()
        if _FID_RE.fullmatch(raw):
            rows = self.conn.execute(
                "SELECT * FROM entries WHERE fid_hex = ? ORDER BY kind,container,row_index", (raw,)
            ).fetchall()
            if rows:
                hits = tuple(IndexHit(r["fid_hex"], r["container"], r["kind"], r["row_index"],
                                      r["offset"], r["payload_offset"], r["packed"], r["decoded"],
                                      r["flag"], r["source"], raw) for r in rows)
                return FindResult(logical_path, (raw,), hits)
        candidates = path_candidates(logical_path, variants=variants, deep=deep)
        by_fid = {}
        for candidate in candidates: by_fid.setdefault(f"{path_fid(candidate):016X}", []).append(candidate)
        placeholders = ",".join("?" for _ in by_fid)
        rows = self.conn.execute(f"SELECT * FROM entries WHERE fid_hex IN ({placeholders}) ORDER BY kind,container,row_index", tuple(by_fid)).fetchall()
        hits = tuple(IndexHit(r["fid_hex"], r["container"], r["kind"], r["row_index"], r["offset"],
                              r["payload_offset"], r["packed"], r["decoded"], r["flag"], r["source"],
                              by_fid[r["fid_hex"]][0]) for r in rows)
        return FindResult(logical_path, tuple(candidates), hits)

    def extract_hit(self, hit: IndexHit, output: Path | str, *, decode=True, overwrite=False) -> dict:
        source = (Path(hit.container) if Path(hit.container).is_absolute() else self.res_root / hit.container).resolve()
        try: source.relative_to(self.res_root.resolve())
        except ValueError as exc: raise RuntimeError(f"容器路径越出资源根：{source}") from exc
        if not source.is_file(): raise FileNotFoundError(f"容器不存在：{source}")
        size = source.stat().st_size
        if hit.payload_offset < 0 or hit.packed <= 0 or hit.payload_offset + hit.packed > size:
            raise RuntimeError(f"条目越界：offset={hit.payload_offset} packed={hit.packed} container_bytes={size}")
        with source.open("rb") as handle: handle.seek(hit.payload_offset); packed = handle.read(hit.packed)
        if len(packed) != hit.packed: raise RuntimeError(f"载荷短读：{len(packed)}/{hit.packed}")
        data = load_verified_index_module().unpack_entry(packed, hit.decoded, hit.flag) if decode else packed
        destination = Path(output).resolve()
        try:
            destination.relative_to(self.res_root.resolve())
        except ValueError:
            pass
        else:
            raise RuntimeError(f"输出路径不能位于游戏源目录：{destination}")
        if destination.exists() and not overwrite: raise FileExistsError(f"输出已存在；使用 --force 才允许覆盖：{destination}")
        destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(data)
        return {"hit": hit.as_dict(), "container_path": str(source), "output": str(destination),
                "decoded": decode, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

    def extract_path(self, logical_path, output, *, container=None, row=None, variants=False,
                     deep=False, decode=True, overwrite=False):
        hits = list(self.find(logical_path, variants=variants, deep=deep).hits)
        if container:
            needle = container.lower().replace("/", "\\")
            hits = [h for h in hits if needle in h.container.lower().replace("/", "\\")]
        if row is not None: hits = [h for h in hits if h.row == row]
        if not hits: raise KeyError(f"路径未命中：{logical_path}")
        if len(hits) != 1: raise AmbiguousMatch(f"路径有 {len(hits)} 个候选；请用 --container/--row 明确选择")
        return self.extract_hit(hits[0], output, decode=decode, overwrite=overwrite)


__all__ = ["AmbiguousMatch", "FindResult", "IndexHit", "IndexNotReady", "UnifiedFileIndex",
           "build_database", "initialize_schema", "inventory_fingerprint", "path_candidates", "path_fid"]
