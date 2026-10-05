# -*- coding: utf-8 -*-
r"""产物定位器 —— 把「容器 + 行号 → 产物路径」做成唯一实现。

★ 为什么要有这个模块：
  历史上多个脚本各自写「逐行 glob 目录」去定位产物，导致：
    · 23,322 行 × 单次 glob 5 万文件目录 = 天荒地老
    · 三个不同脚本反复踩同一个坑
  ⇒ 统一到这里：目录【只列一次】建 {行号: 路径} 映射，之后 O(1) 查。

用法：
    from toolkit_core import artifact_locator as AL
    loc = AL.Locator()                    # 默认产物根
    p = loc.path("gres\\0000.gpk", 7776)  # → Path 或 None
    loc.rows("gres\\0000.gpk")            # → {行号: Path}
    loc.stats()                           # 命中统计
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, Optional

DEFAULT_ROOT = Path(r"E:/la拆包项目/03_执行/20_提取/全量实测_20260926/files")

_RN = re.compile(r"^(\d{8})(?:\.|$)")


def _paths():
    """延迟导入 paths（避免模块级循环依赖）。"""
    from toolkit_core import paths as P
    return P


def default_tree_root() -> Path:
    """★ 唯一权威产物根：`03_执行/41_还原树`。"""
    return _paths().TREE_ROOT


def row_path_map_db() -> Path:
    """★ S1 产物：`(容器, 行号) → 还原树路径` 映射库。"""
    return _paths().INDEX_ROOT / "indexes" / "row_path_map.db"


class TreeResolver:
    """★ 用 S1 的 row_path_map sidecar 把 (容器, 行号) 解析到【还原树】里的文件。

    为什么需要它：初拆产物（`20_提取`）是**可重建的中间态**，架构改造后会被清掉；
    还原树才是唯一权威。老代码全部按 `20_提取` 定位 ⇒ 载荷一删就全哑。

    与 `Locator` 的区别：
      · Locator      按「产物目录 + 8 位行号文件名」猜（只适用于 20_提取 的铺法）
      · TreeResolver 查 sidecar 表，直接拿到树里的真实相对路径（含 _未命名 的真实扩展名）

    用法：
        tr = TreeResolver()
        tr.path("gres\\0000.gpk", 7776)   # → Path 或 None
        tr.rows("gres\\0000.gpk")         # → {行号: Path}
    """

    def __init__(self, tree_root: str | Path | None = None,
                 db: str | Path | None = None):
        self.tree_root = Path(tree_root) if tree_root else default_tree_root()
        self.db = Path(db) if db else row_path_map_db()
        self._ready = False
        self._rows_cache: Dict[str, Dict[int, Path]] = {}
        self._hits = 0
        self._miss = 0

    @property
    def available(self) -> bool:
        return self.db.is_file() and self.tree_root.is_dir()

    def _connect(self):
        if not self.db.is_file():
            raise FileNotFoundError(
                "row_path_map.db 不存在：%s\n"
                "先跑 `toolkit_cli index rowmap`（或 build_row_path_map.py）建它。" % self.db)
        con = sqlite3.connect("file:%s?mode=ro" % self.db.as_posix(), uri=True)
        con.row_factory = sqlite3.Row
        return con

    def rows(self, container: str) -> Dict[int, Path]:
        """容器 → {行号: 还原树里的文件}（只含实际存在的）。"""
        got = self._rows_cache.get(container)
        if got is not None:
            return got
        if not self.available:
            self._rows_cache[container] = {}
            return {}
        out: Dict[int, Path] = {}
        con = self._connect()
        try:
            for r in con.execute(
                    "SELECT row_index, path FROM rows WHERE container=? AND in_tree=1",
                    (container,)):
                p = self.tree_root / str(r["path"]).replace("\\", "/")
                if p.is_file():
                    out[int(r["row_index"])] = p
        finally:
            con.close()
        self._rows_cache[container] = out
        return out

    def path(self, container: str, row: int) -> Optional[Path]:
        p = self.rows(container).get(int(row))
        if p is None:
            self._miss += 1
        else:
            self._hits += 1
        return p

    def read(self, container: str, row: int, limit: int | None = None) -> Optional[bytes]:
        p = self.path(container, row)
        if p is None:
            return None
        if limit is None:
            return p.read_bytes()
        with p.open("rb") as fh:
            return fh.read(limit)

    def stats(self) -> dict:
        return {"source": "tree", "tree_root": str(self.tree_root),
                "db": str(self.db), "available": self.available,
                "cached_containers": len(self._rows_cache),
                "hits": self._hits, "miss": self._miss}


class UnifiedResolver:
    """★★ 架构改造后的【统一产物读取入口】：**还原树优先，提取回退**。

    ★ 新代码一律用它，别再直接 new Locator（那等于把自己绑死在可删的初拆载荷上）。

    `source` 三档：
      · "auto"（默认） 先查还原树；树里没有（本期新增、尚未 apply）再回退初拆载荷
      · "tree"          只查还原树（架构改造完成后的目标态；载荷删了也能跑）
      · "extract"       只查初拆载荷（等价于老 Locator，用于对照/回归）

    用法：
        r = UnifiedResolver()
        r.path("gres\\0000.gpk", 7776)   # → Path 或 None
        r.read("gres\\0000.gpk", 7776)   # → bytes 或 None
        r.stats()                        # 两个来源各命中多少
    """

    def __init__(self, tree_root: str | Path | None = None,
                 extract_root: str | Path | None = None,
                 db: str | Path | None = None, source: str = "auto"):
        if source not in ("auto", "tree", "extract"):
            raise ValueError("source 只能是 auto / tree / extract，收到 %r" % source)
        self.source = source
        self._tree: Optional[TreeResolver] = None
        self._extract: Optional[Locator] = None
        self._tree_root = tree_root
        self._extract_root = extract_root
        self._db = db
        self._from_tree = 0
        self._from_extract = 0

    @property
    def tree(self) -> TreeResolver:
        if self._tree is None:
            self._tree = TreeResolver(self._tree_root, self._db)
        return self._tree

    @property
    def extract(self) -> Locator:
        if self._extract is None:
            self._extract = Locator(self._extract_root or DEFAULT_ROOT)
        return self._extract

    def path(self, container: str, row: int) -> Optional[Path]:
        if self.source in ("auto", "tree"):
            p = self.tree.path(container, row)
            if p is not None:
                self._from_tree += 1
                return p
            if self.source == "tree":
                return None
        p = self.extract.path(container, row)
        if p is not None:
            self._from_extract += 1
        return p

    def read(self, container: str, row: int, limit: int | None = None) -> Optional[bytes]:
        p = self.path(container, row)
        if p is None:
            return None
        if limit is None:
            return p.read_bytes()
        with p.open("rb") as fh:
            return fh.read(limit)

    def rows(self, container: str) -> Dict[int, Path]:
        """合并两个来源的 {行号: 路径}（树优先，提取补缺）。"""
        if self.source == "tree":
            return self.tree.rows(container)
        if self.source == "extract":
            return self.extract.rows(container)
        out = dict(self.tree.rows(container))
        for k, v in self.extract.rows(container).items():
            out.setdefault(k, v)
        return out

    def stats(self) -> dict:
        return {"source": self.source,
                "from_tree": self._from_tree, "from_extract": self._from_extract,
                "tree": self.tree.stats(),
                "extract_hits": self._extract._hits if self._extract else 0,
                "extract_miss": self._extract._miss if self._extract else 0}


def default_product_root() -> Path:
    """★ 产物根的智能默认值 —— 载荷在就用载荷，不在就退回树所在（架构改造过渡用）。

    背景（2026-09-29 S5）：初拆载荷（`20_提取/.../files`）已按架构改造清掉。
    老代码把「载荷路径」写死成默认值 ⇒ 载荷一删，所有没显式传 `--product-root`
    的命令都指向不存在的目录（静默返回 0 结果，比报错更危险）。

    ★ 口径：
      ① 载荷目录还在 → 返回它（保持老行为，零回归）
      ② 载荷没了     → 返回 TREE_ROOT（新代码走 UnifiedResolver 即可自动适配）
    ⇒ 调用点不需要判断，拿到的路径永远是可用的那个。
    """
    legacy = DEFAULT_ROOT
    if legacy.is_dir():
        return legacy
    return default_tree_root()


def default_product_root_or_none() -> Optional[Path]:
    """载荷没了、且树也不可用时返回 None（让调用方明确报错，而不是静默 0 结果）。"""
    p = default_product_root()
    return p if p.is_dir() else None


def read_any(container: str, row: int, limit: int | None = None) -> Optional[bytes]:
    """★ 读一条产物的【推荐入口】：树优先、载荷回退、都没有就 None。

    新代码一律用它，别再自己拼 `20_提取/.../files/<容器>/<8位>.ext`。
    """
    return UnifiedResolver(source="auto").read(container, row, limit)


def dir_name_of(container: str, root: str | Path | None = None) -> str:
    """容器名 → 产物目录名（模块级便捷函数，供其它模块复用，避免各写一份）。

    规则见 `Locator.dir_of`：**「把分隔符换成 __ 的规范化名」存在就用它，否则退回 stem。**
    实测对 60 个容器全部命中，且能区分 `script.py314.lc` 与 `Documents\\script.py314.lc`
    （旧实现用 `Path.stem` 会把两者折成同一个，导致查 A 容器串到 B 容器的产物）。

    ★ 别再写第二份：历史上 `container_probe` / `restore_tree` 各有一份，
      其中一份把 `script.py314.lc` 硬编码成特例 —— 三者行为不完全等价。

    ★★ 2026-09-30 修正：**这里绝不能复用 `Locator.dir_of().name`** ——
      对标 E:\\mrzh 之后 `dir_of` 返回的是「装行文件的那个目录」(`<容器>/_未命名`)，
      它的 `.name` 恒为 `_未命名`，会让所有用本函数拼路径的地方全错。
      本函数只负责**老铺法的目录名**（`Documents__script.py314.lc` 这种），
      判据保持原样：**规范化名存在就用它，否则退回 stem**。
    """
    raw = str(container)
    stem = raw.replace("/", "\\").rsplit("\\", 1)[-1]
    stem = stem.rsplit(".", 1)[0] if "." in stem else stem
    norm = raw.replace(".npk", "").replace(".gpk", "")
    norm = norm.replace("\\", "__").replace("/", "__")
    p = Path(root or DEFAULT_ROOT)
    for cand in (norm, stem):
        if (p / cand).is_dir():
            return cand
    # ★ 兜底必须是 **stem**（老行为）：载荷目录被清掉后 `norm` 目录往往不存在，
    #   这时退回 stem 才能与 `container_probe` / 老契约一致
    #   （副作用：`script.py314.lc.npk` 与 `Documents\script.py314.lc.npk` 会折成同一个名字 ——
    #    这正是「不能再用它定位」的证据，定位改由 `TreeResolver`/`row_path_map` 负责）。
    return stem


def stem_of(container: str) -> str:
    return Locator.stem_of(container)


class Locator:
    """容器名/行号 → 产物路径 的缓存定位器。"""

    def __init__(self, root: str | Path = DEFAULT_ROOT, use_sqlite: bool = False,
                 cache_dir: str | Path | None = None):
        self.root = Path(root)
        self._maps: Dict[str, Dict[int, Path]] = {}
        self._cmap: Dict[str, Path] = {}
        self._hits = 0
        self._miss = 0
        # ★★ 线程安全：`_ensure_dir` 的慢路径（首次列目录 + 写缓存）必须串行化。
        #    实测不加锁时 24 线程并行 = 1.79 核 / 32 核（0 CPU 挂住）。
        import threading as _th
        self._lock = _th.RLock()
        self.use_sqlite = use_sqlite
        # ★ 磁盘缓存：列一次大目录（如 0000/ 有 54,292 个文件、scene_03/ 有 79,161 个）
        #   要几十秒。缓存 {行号: 文件名} 后，后续进程直接读，不用重列。
        #   失效判据：目录 mtime 比缓存新 ⇒ 重列。
        #   ★ 合成/临时根（测试用）不写缓存，免得污染临时目录。
        import tempfile as _tf
        if cache_dir is None and str(self.root).lower().startswith(
                str(Path(_tf.gettempdir())).lower()):
            self.cache_dir = None
        else:
            self.cache_dir = Path(cache_dir) if cache_dir else \
                (self.root.parent / "_product_row_cache")

    # ── 磁盘缓存 ────────────────────────────────────────────
    def _cache_file(self, d: Path) -> Path:
        import hashlib
        k = hashlib.sha1(str(d).encode("utf-8")).hexdigest()[:16]
        return self.cache_dir / ("%s_%s.json" % (d.name[:40], k))

    def _load_cache(self, d: Path):
        if self.cache_dir is None:
            return None
        f = self._cache_file(d)
        if not f.is_file():
            return None
        try:
            if f.stat().st_mtime < d.stat().st_mtime:
                return None                      # 目录变过 ⇒ 失效
            raw = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        # ★ 只有 IO/格式错才吞；下面若出错应让它抛（编程错不该静默）
        return {int(k): d / v for k, v in raw.items()}

    def _save_cache(self, d: Path, m: Dict[int, Path]) -> None:
        if self.cache_dir is None:
            return
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            f = self._cache_file(d)
            f.write_text(json.dumps({str(k): v.name for k, v in m.items()},
                                    ensure_ascii=False, separators=(",", ":")),
                         encoding="utf-8")
        except OSError:
            pass

    # ── 内部 ────────────────────────────────────────────────
    @staticmethod
    def stem_of(container: str) -> str:
        """`gres\\0000.gpk` / `Documents\\script.py314.lc.npk` → `0000` / `script.py314.lc`

        ★ 只做「取文件名去扩展名」这一层；**不要用它当产物目录名** ——
        容器 `script.py314.lc.npk` 与 `Documents\\script.py314.lc.npk` 会折成同一个 stem，
        而实际产物目录是 `script.py314.lc` 与 `Documents__script.py314.lc`（两个不同目录）。
        要拿目录请用 `dir_of()`。
        """
        s = str(container).replace("\\", "/")
        return Path(s).stem

    def dir_of(self, container: str) -> Path:
        """容器 → 产物目录（含歧义消解）。★ 优先【对标 E:\\mrzh 的新层级】。

        ★ 2026-09-30 新增新层级（用户定的迁移目标）：
              `<树根>/<容器相对路径>/_未命名/<8位行号>.<ext>`
              例：`script.py314.lc.npk/_未命名/00000003.bin`
                  `Documents/script.py314.lc.npk/_未命名/00019141.bin`
        判定顺序（新 → 旧，双兼容，迁移途中也能跑）：
          ① 新层级：`<根>/<容器（反斜杠→斜杠）>/_未命名/` 真的存在 ⇒ 用它
          ② 旧铺法规范化名：`<根>/Documents__script.py314.lc`（把 \\ 换成 __）
          ③ 旧铺法 stem：`<根>/script.py314.lc`
        为什么还要 ②③：迁移是**分批**做的，老路径在被删前仍要能读到。
        """
        got = self._cmap.get(container)
        if got is not None:
            return got
        raw = str(container)
        stem = self.stem_of(raw)
        norm = raw.replace(".npk", "").replace(".gpk", "")
        norm = norm.replace("\\", "__").replace("/", "__")
        rel = raw.replace("\\", "/")
        d = None
        for cand in (Path(rel) / "_未命名", norm, stem):
            p = self.root / cand
            if p.is_dir():
                d = p
                break
        if d is None:
            d = self.root / stem          # 都不存在也返回 stem 目录（上层会返回 None）
        with self._lock:                  # ★ 与 _ensure_dir 同一把锁：并发写 dict 也要保护
            self._cmap[container] = d
        return d

    def _ensure(self, stem: str) -> Dict[int, Path]:
        return self._ensure_dir(self.root / stem)

    def _ensure_dir(self, d: Path) -> Dict[int, Path]:
        key = str(d)
        # ★★ 快路径：已建好直接返回（无锁，最常用）
        got = self._maps.get(key)
        if got is not None:
            return got
        # ★★★ 慢路径必须【串行化】—— 否则 N 个线程同时首次访问同一目录时：
        #    各自把几万文件的目录列一遍（N 遍！）+ 同时写同一个缓存文件 ⇒ 抢文件锁，
        #    实测退化成 1.79 核/32 核（0 CPU 挂住），看起来像死锁。
        #    修法：双检锁 —— 抢到锁的建，其余等它建完直接用。
        with self._lock:
            got = self._maps.get(key)          # 双检：可能别人已建好
            if got is not None:
                return got
            m = self._load_cache(d) if d.is_dir() else None
            if m is None:
                m = {}
                if d.is_dir():
                    # ★ 关键：只列一次
                    for e in d.iterdir():
                        mm = _RN.match(e.name)
                        if mm and e.is_file():
                            m[int(mm.group(1))] = e
                    self._save_cache(d, m)
            self._maps[key] = m
            return m

    # ── 公开 ────────────────────────────────────────────────
    def rows(self, container: str) -> Dict[int, Path]:
        """容器 → {行号: 产物路径}。★ 用 dir_of 做歧义消解。"""
        return self._ensure_dir(self.dir_of(container))

    def path(self, container: str, row: int) -> Optional[Path]:
        p = self._ensure_dir(self.dir_of(container)).get(int(row))
        if p is None:
            self._miss += 1
        else:
            self._hits += 1
        return p

    def read(self, container: str, row: int, limit: int | None = None) -> Optional[bytes]:
        p = self.path(container, row)
        if p is None:
            return None
        if limit is None:
            return p.read_bytes()
        with p.open("rb") as fh:
            return fh.read(limit)

    def head(self, container: str, row: int, n: int = 148) -> Optional[bytes]:
        return self.read(container, row, n)

    def stats(self) -> dict:
        return {"cached_containers": len(self._maps),
                "cached_rows": sum(len(v) for v in self._maps.values()),
                "hits": self._hits, "miss": self._miss}

    def selfcheck(self, *, sample_dirs: int = 3, sample_rows: int = 10) -> dict:
        """自检：已建映射的目录，其 `{行号: 路径}` 与在该目录里 glob 出来的是否一致。

        ★ 注意：`self._maps` 的 key 是【目录的完整路径字符串】（不是 stem）——
        因为容器 `Documents\\script.py314.lc.npk` 与 `script.py314.lc.npk` 的 stem 会撞车。
        所以这里要 `Path(key)` 而不是 `self.root / key`。

        ★ 只抽样少量目录与少量行 —— 全量 glob 在 5 万文件的目录上要几十秒，
        不适合放进单元测试。
        """
        out = {"ok": True, "checked": 0, "mismatch": []}
        keys = [k for k in list(self._maps) if self._maps[k]][:sample_dirs]
        for key in keys:
            m = self._maps[key]
            d = Path(key)
            if not d.is_dir():
                continue
            for row in list(m)[:sample_rows]:
                direct = None
                for cand in d.glob("%08d.*" % row):
                    direct = cand
                    break
                if direct != m[row]:
                    out["ok"] = False
                    out["mismatch"].append("%s r%d: %s != %s" % (d.name, row, m[row], direct))
                out["checked"] += 1
        return out


# ── 便捷：一次性按容器批量取行（避免重复建映射） ──────────────
def read_many(root, items, loader=None):
    """items = [(container, row), ...] → [(container, row, bytes|None), ...]"""
    loc = Locator(root)
    for c, r in items:
        yield c, r, loc.read(c, r)


def locate_fids(db, mapping: Dict[str, str], target="*"):
    """给 {fid_hex: 路径}，从 SQLite 索引取 (fid, container, row)。
    ★ 注意：npk 容器的 fid ≠ murmur3(路径)，所以必须用字典自带的 fid，不能重算。
    """
    import sqlite3
    if isinstance(db, (str, Path)):
        db = sqlite3.connect(str(db), uri=str(db).startswith("file:"))
    out = {}
    for c, n in db.execute("SELECT container,count(*) FROM entries GROUP BY container"):
        if target != "*" and target not in c:
            continue
        for f, r in db.execute("SELECT fid_hex,row_index FROM entries WHERE container=?", (c,)):
            if f in mapping:
                out[f] = (c, r)
    return out


if __name__ == "__main__":
    import time
    t0 = time.time()
    loc = Locator()
    m = loc.rows("gres\\0000.gpk")
    t1 = time.time()
    print("gres\\0000.gpk: %d 行，列目录 %.3f 秒" % (len(m), t1 - t0))
    p = loc.path("gres\\0000.gpk", 7776)
    print("r7776 → %s" % p)
    t2 = time.time()
    for i in range(7770, 7790):
        loc.path("gres\\0000.gpk", i)
    print("20 次查询 %.4f 秒（对比：旧法每次 glob ≈ 0.02~0.5 秒）" % (time.time() - t2))
    print(loc.selfcheck())
