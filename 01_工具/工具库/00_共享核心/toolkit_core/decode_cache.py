# -*- coding: utf-8 -*-
r"""表解码缓存：同一份载荷只解一次（跨波次、跨命令复用）。

为什么：`hotfix rows` 880 张表要 10 小时，绝大部分时间花在「同一张表反复解」——
同一次跑里 pre/post 各解一次、不同命令（对比报告/时装热更表/单侧表）又各解一次。
载荷内容没变结果就不会变 ⇒ 直接按【载荷哈希】缓存解出的行。

存储：`03_执行/10_索引/indexes/decode_cache.sqlite3`，表 cache(key, kind, blob, made_at)。
上限：默认 1 GB（`--no-cache` 关；超限按最旧淘汰）。

★ key = sha1(kind + 载荷字节)，与表名无关 —— 同一张表改名/换路径也能命中。
"""
from __future__ import annotations

import hashlib
import pickle
import sqlite3
import time
from pathlib import Path

DEFAULT_PATH = Path(r"E:/la拆包项目/03_执行/10_索引/indexes/decode_cache.sqlite3")
DEFAULT_LIMIT = 1_000_000_000        # 1 GB


def key_of(kind: str, *blobs: bytes) -> str:
    h = hashlib.sha1(kind.encode())
    for b in blobs:
        if b:
            h.update(b)
    return h.hexdigest()


class DecodeCache:
    def __init__(self, path: Path | str | None = None, limit: int = DEFAULT_LIMIT,
                 enabled: bool = True):
        self.enabled = enabled
        self.path = Path(path) if path else DEFAULT_PATH
        self.limit = int(limit)
        self.hits = 0
        self.misses = 0
        self._con: sqlite3.Connection | None = None
        if not self.enabled:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._con = sqlite3.connect(str(self.path), timeout=30)
            self._con.execute(
                "CREATE TABLE IF NOT EXISTS cache ("
                " key TEXT PRIMARY KEY, kind TEXT, blob BLOB, made_at REAL)")
            self._con.execute("CREATE INDEX IF NOT EXISTS idx_made ON cache(made_at)")
            self._con.commit()
        except sqlite3.Error:
            self._con = None

    # ── 读 ────────────────────────────────────────────────
    def get(self, key: str):
        if not self.enabled or self._con is None:
            return None
        try:
            row = self._con.execute("SELECT blob FROM cache WHERE key=?", (key,)).fetchone()
        except sqlite3.Error:
            return None
        if not row:
            self.misses += 1
            return None
        try:
            obj = pickle.loads(row[0])
        except Exception:                                        # noqa: BLE001
            return None
        self.hits += 1
        return obj

    # ── 写 ────────────────────────────────────────────────
    def put(self, key: str, kind: str, obj) -> None:
        if not self.enabled or self._con is None:
            return
        try:
            blob = pickle.dumps(obj, protocol=4)
        except Exception:                                        # noqa: BLE001
            return
        try:
            self._con.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?,?)",
                              (key, kind, blob, time.time()))
            self._con.commit()
        except sqlite3.Error:
            return
        if len(blob) > 2_000_000:
            self.trim()

    def trim(self) -> None:
        """超上限就按时间淘汰最旧的（一次删掉 20%）。"""
        if self._con is None:
            return
        try:
            total = self._con.execute("SELECT COALESCE(SUM(LENGTH(blob)),0) FROM cache").fetchone()[0]
            if total <= self.limit:
                return
            target = total - int(self.limit * 0.8)
            cut = self._con.execute(
                "SELECT key, LENGTH(blob) FROM cache ORDER BY made_at ASC").fetchall()
            freed = 0
            for k, n in cut:
                self._con.execute("DELETE FROM cache WHERE key=?", (k,))
                freed += n
                if freed >= target:
                    break
            self._con.commit()
        except sqlite3.Error:
            pass

    def stats(self) -> dict:
        n = size = 0
        if self._con is not None:
            try:
                n, size = self._con.execute(
                    "SELECT COUNT(*), COALESCE(SUM(LENGTH(blob)),0) FROM cache").fetchone()
            except sqlite3.Error:
                pass
        return {"enabled": self.enabled, "path": str(self.path), "entries": n,
                "bytes": size, "hits": self.hits, "misses": self.misses}


_SHARED: DecodeCache | None = None


def shared(enabled: bool = True) -> DecodeCache:
    """进程内共享一个实例（避免每次调用重开库）。"""
    global _SHARED
    if _SHARED is None or _SHARED.enabled != enabled:
        _SHARED = DecodeCache(enabled=enabled)
    return _SHARED
