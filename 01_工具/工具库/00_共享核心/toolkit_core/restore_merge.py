# -*- coding: utf-8 -*-
r"""把热更内容合并进【还原树】。

## 为什么需要

`41_还原树` 是从某一次全量索引物化出来的快照（实测 mtime = 建树那一刻）。
之后每期热更的内容（资源 overlay + 脚本/配置表）**不会自动进树**，
于是「从还原树读表」会读到旧版本 —— 这正是「奖池产物过期」那类问题的根源。

## 合并的两层（各自独立，都要做）

```
① 资源层：热更交付的 `01_还原树/`（已按路径还原好的资源）
   → 按【路径】合并进 tree_root
② 脚本层：script overlay/整包 .npk
   → 逐条解码 → fid 查名字字典得路径 → 按路径合并进 tree_root
   （命不中的落 `_未命名/<容器目录名>/<行号>.<ext>`）
```

## 纪律

- **覆盖前记 sha256**；台账里分 `added / updated / same / failed` 四类，**不静默跳过**。
- **`--dry-run` 先跑一遍**，确认数字再实做。
- 原来的文件不删（热更只做「新增/覆盖」；删除清单另列 `removed_candidates`，不自动删）。
- 台账落 `<tree_root>/_热更合并台账_<ts>.json`，**可复核每次合并的来源与前后 sha**。
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

__all__ = ["merge_tree_dir", "merge_script_pack", "MergeStats"]


#: 已知明文格式的开头（这些解出来就该原样，不算垃圾）
_KNOWN_MAGIC = (b"\x89PNG", b"DDS ", b"RIFF", b"OggS", b"FSB5", b"<?xml", b"<Fxg",
                b"PK\x03\x04", b"c159", b"nxs")
_MAGIC_HINT = (b"x{", b"\x73\x00\x00\x00", b"\xe3")


def _entropy(data: bytes) -> float:
    import collections
    import math
    if not data:
        return 0.0
    c = collections.Counter(data)
    n = len(data)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def _has_structure(data: bytes) -> bool:
    """有没有【结构标志】—— 脚本/表/明文格式都该有。"""
    if not data:
        return False
    if data[:4] == b"\x73\x00\x00\x00" or data[:1] == b"\xe3":
        return True
    if b"x{" in data[:8192]:
        return True
    return any(data.startswith(m) for m in _KNOWN_MAGIC)


def looks_sane(data: bytes) -> bool:
    """解出的内容「像不像话」—— ★ 用于拦住「拿垃圾覆盖正常文件」。

    ★ 为什么需要（2026-09-30 实测）：Documents 热更包里 flag=2 的条目解出来是高熵乱码，
      而树里现有那份看着正常（有 marshal 头 / `x{` 帧）。比例守卫拦不住这种
      「少量但致命」的错（只占 4.9%），必须在**每一条**上验内容。
    """
    return _has_structure(data) or _entropy(data) < 7.7


def suspicious_against(old: bytes, new: bytes) -> bool:
    """★ 对照式判据（比单看新内容可靠）：**旧的**有结构、**新的**没结构 ⇒ 可疑。

    ★ 只用熵不行：压缩垃圾的熵常在 7.5 上下，会漏过阈值（实测第一版只拦住 27/1,346）。
      结构标志（marshal 头 / `x{` / 明文魔数）是更硬的判据 ——
      树里那份有、新解出那份没有 ⇒ 十有八九是「拿垃圾换正常内容」。
    """
    return _has_structure(old) and not _has_structure(new)


def looks_sane_resource(data: bytes, declared: int = 0) -> bool:
    """★ **资源类**内容的合法性（`.gim/.csb/贴图/音频` 等二进制）。

    为什么单独一个：脚本/表那套判据（marshal 头 / `x{` 帧）对二进制资源**天生不成立**
    （实测：gpk 的 991 条跨容器重名里 1,963 个副本被那套判据全部拦下）。
    资源类的硬判据是【条目表声明的 decoded 尺寸】—— 解得对就必然相等。
    ★ 只在 **资源容器**（gpk 等）用；**脚本容器别用**：
      flag=0 的明文直通本来就是 packed==decoded，尺寸相等证明不了解对，
      用它会放过「拿垃圾覆盖」那类错（实测 X9Esports 的垃圾长度也正好等于 declare）。
    """
    if not data:
        return False
    return _has_structure(data) or (declared > 0 and len(data) == declared)


def _sha256(p: Path, limit: Optional[int] = None) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while True:
            b = fh.read(1 << 20)
            if not b:
                break
            h.update(b)
            if limit and fh.tell() > limit:
                break
    return h.hexdigest()


@dataclass
class MergeStats:
    source: str = ""
    layer: str = ""
    container: str = ""          # ★ 脚本层合并时记录处理的容器（便于核账）
    scanned: int = 0
    added: int = 0
    updated: int = 0
    same: int = 0
    failed: int = 0
    named: int = 0
    unnamed: int = 0
    suspicious: int = 0          # ★ 解出内容不像话 ⇒ 拒绝覆盖（2026-09-30）
    parallel_workers: int = 0    # ★ 实际用的解码并行度（0 = 串行）
    removed_candidates: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    samples: Dict[str, List[str]] = field(default_factory=lambda: {
        "added": [], "updated": [], "same": [], "failed": [], "suspicious": []})

    def note(self, kind: str, rel: str, keep: int = 15) -> None:
        if len(self.samples.get(kind, [])) < keep:
            self.samples.setdefault(kind, []).append(rel)

    def as_dict(self) -> dict:
        d = {"source": self.source, "layer": self.layer, "scanned": self.scanned,
             "added": self.added, "updated": self.updated, "same": self.same,
             "failed": self.failed, "named": self.named, "unnamed": self.unnamed,
             "removed_candidates": self.removed_candidates[:200],
             "samples": self.samples}
        if self.errors:
            d["errors"] = self.errors[:50]
        return d


def _place(src: Path, dst: Path, st: MergeStats, rel: str, dry: bool) -> None:
    """一个文件 → 目标位置（新增/覆盖/相同）。"""
    try:
        if dst.is_file():
            if dst.stat().st_size == src.stat().st_size and _sha256(src) == _sha256(dst):
                st.same += 1
                st.note("same", rel)
                return
            st.updated += 1
            st.note("updated", rel)
        else:
            st.added += 1
            st.note("added", rel)
        if dry:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        # 覆盖：先删再拷（硬链接会让「覆盖」变失败）
        if dst.exists():
            dst.unlink()
        shutil.copy2(src, dst)
    except Exception as e:                                          # noqa: BLE001
        st.failed += 1
        st.note("failed", rel)
        if len(st.errors) < 50:
            st.errors.append("%s: %r" % (rel, e))


def merge_tree_dir(src_tree: Path, tree_root: Path, *, dry_run: bool = False,
                   layer: str = "资源层") -> MergeStats:
    """① 资源层：把一棵【已按路径还原】的树合并进 tree_root。"""
    st = MergeStats(source=str(src_tree), layer=layer)
    src_tree = Path(src_tree)
    tree_root = Path(tree_root)
    if not src_tree.is_dir():
        st.errors.append("源树不存在：%s" % src_tree)
        return st
    for dirpath, _dirs, files in os.walk(src_tree):
        for fn in files:
            sp = Path(dirpath) / fn
            rel = os.path.relpath(str(sp), str(src_tree))
            st.scanned += 1
            _place(sp, tree_root / rel, st, rel, dry_run)
    return st


def _load_decoder():
    """项目现成的 NPK 条目解码器（★ 别自己写第二份）。

    `flag=0`：已是已知明文格式（MP4/DDS/PNG/FSB5/mesh/c159…）→ 直通；
             否则 AES-ECB 解密整块 → 判 i64@0==1 → 偏移 18 起 zlib 解压。
    `flag=2`：LZ4 block。
    ⇒ 早期版本我用 zstd 直解，得到的是【高熵密文】，与树里明文一比全是「覆盖」，
      制造出「覆盖 23,368 / 相同 0」的假象。
    ★★ 装载时必须先 `sys.modules[name] = mod` 再 exec ——
       该模块里有 `@dataclass`，dataclasses 会去 `sys.modules[cls.__module__]` 取
       命名空间；不注册就直接 `AttributeError: 'NoneType' object has no attribute '__dict__'`。
    """
    import importlib.util
    import sys as _sys
    p = (Path(__file__).resolve().parents[2] / "01_解码定位复原" / "解包与扫描"
         / "la_unpack_core.py")
    if not p.is_file():
        return None
    name = "_la_unpack_core_for_merge"
    if name in _sys.modules:
        return getattr(_sys.modules[name], "npk_decode_entry", None)
    spec = importlib.util.spec_from_file_location(name, p)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[name] = mod          # ★ 必须在 exec_module 之前
    try:
        spec.loader.exec_module(mod)
    except Exception:                                            # noqa: BLE001
        _sys.modules.pop(name, None)
        return None
    return getattr(mod, "npk_decode_entry", None)


def _dir_name_of(container: str) -> str:
    """容器名 → 产物目录名（复用 container_probe 的唯一实现，不另写一份）。"""
    try:
        from toolkit_core.container_probe import container_dir_name
        return container_dir_name(container)
    except Exception:
        s = str(container).replace("\\", "/")
        return s.split("/")[-1].rsplit(".", 1)[0]


def merge_script_pack(pack: Path, tree_root: Path, index_db: Path,
                      names: Dict[str, str], *, dry_run: bool = False,
                      container_dir: Optional[str] = None,
                      container: Optional[str] = None,
                      only_named: bool = False,
                      allow_suspicious: bool = False,
                      workers: Optional[int] = None) -> MergeStats:
    """② 脚本层：把一个 .npk 的条目按 fid→路径 合并进 tree_root。

    ★ 2026-09-30 修（两个 bug）：
      ① **必须按容器过滤**：原实现 `SELECT … FROM entries` 无 WHERE，
         会把【全部 60 个容器】230 万行都当成这个包的条目 —— 那是灾难（错配+极慢）。
         现在按 `container` 列过滤（不给则用 container_dir 反推）。
      ② **索引/容器不存在要明确报错**：原实现直接 sqlite3.connect 到不存在的路径，
         抛 `unable to open database file` 崩栈 —— 调用方看不出是配置问题。
    """
    st = MergeStats(source=str(pack), layer="脚本层")
    pack = Path(pack)
    if not pack.is_file():
        st.errors.append("包不存在：%s" % pack)
        return st
    index_db = Path(index_db)
    if not index_db.is_file():
        st.errors.append("索引库不存在：%s（脚本层合并必须给 --index-db）" % index_db)
        return st
    if not container:
        # 从容器目录名反推容器名（Documents__X → Documents\X）
        if container_dir and "__" in container_dir:
            parts = container_dir.split("__")
            container = parts[0] + "\\" + parts[1]
        else:
            # ★ 2026-09-30 修：**别用 `pack.stem`** —— 它会把 `script.py314.lc.npk`
            #   剥成 `script.py314.lc`，而索引里的容器名是【带 .npk 的全名】⇒ 扫 0 条。
            #   正解：拿包文件名去索引的容器清单里反查（唯一命中才用）。
            try:
                con0 = sqlite3.connect(str(index_db))
                cont_names = [c for (c,) in con0.execute(
                    "SELECT DISTINCT container FROM entries")]
                con0.close()
            except sqlite3.Error:
                cont_names = []
            hits = [c for c in cont_names
                    if str(c).replace("/", "\\").split("\\")[-1] == pack.name]
            if len(hits) == 1:
                container = hits[0]
            elif len(hits) > 1:
                # ★★ 2026-09-30：**歧义绝不许静默挑一个**。
                #   实测踩过：`script.py314.lc.npk` 与 `Documents\script.py314.lc.npk`
                #   同 basename，选错容器 ⇒ 把 overlay 内容拿去比底座行 ⇒ 假「覆盖 8 万条」+
                #   失败 2.5 万（lz4 解不出），`相同 0` 就是选错/解码错的铁证。
                #   热更快照包（路径含 post_update / Documents）→ 优先 Documents 层；
                #   否则**报错要求显式 --container**。
                docs = [c for c in hits if str(c).replace("/", "\\").split("\\")[0].lower()
                        == "documents"]
                hot = any(k in str(pack).lower()
                          for k in ("post_update", "pre_update", "documents", "热更"))
                if hot and len(docs) == 1:
                    container = docs[0]
                    st.errors.append(
                        "★ 容器名歧义（%s）：已按「热更快照 ⇒ Documents 层」取 %s"
                        "（其余候选 %s）—— 可用 --container 显式指定"
                        % (pack.name, container, [c for c in hits if c != container]))
                else:
                    st.errors.append(
                        "★ 容器名歧义（%s），候选 %s —— 必须显式 --container，已中止"
                        % (pack.name, hits))
                    return st
            elif pack.stem in cont_names:
                container = pack.stem
            else:
                container = pack.name if pack.name in cont_names else pack.stem
    decode = _load_decoder()
    if decode is None:
        st.errors.append("找不到条目解码器 la_unpack_core.npk_decode_entry —— "
                         "解码结果会是密文，已中止")
        return st
    st.container = container
    con = sqlite3.connect(str(index_db))
    cur = con.cursor()
    cur.execute("SELECT fid_hex,row_index,offset,packed,decoded,flag FROM entries "
                "WHERE container=?", (container,))
    rows = cur.fetchall()
    con.close()
    if not rows:
        st.errors.append("索引里容器 %r 没有条目（容器名口径要带前缀，如 "
                         "Documents\\script.py314.lc.npk）" % container)
        return st
    raw_pack = pack.read_bytes()
    stem = container_dir or _dir_name_of(container)
    # ★ 2026-09-30 用户定：还原树**对标 E:\mrzh 的层级** —— 写入落点必须带容器分区，
    #   否则同名表的多层副本会落到同一个路径（后果：层信息丢失，读到的可能是旧的那份）。
    #   新落点：`<树根>/<容器名>/<游戏内路径>`；无名 → `<树根>/<容器名>/_未命名/<8位行号>.bin`
    cont_dir = container.replace("/", "\\")
    # ── 组装任务（主线程，便宜）────────────────────────────────────
    tasks = []
    for fid_hex, row, off, packed, decoded, flag in rows:
        path = names.get((fid_hex or "").upper())
        if path:
            rel = os.path.join(cont_dir, path.replace("/", "\\"))
        else:
            if only_named:
                continue
            rel = os.path.join(cont_dir, "_未命名", "%08d.bin" % row)
        tasks.append((fid_hex, row, off, packed, decoded, flag, rel, bool(path)))
    st.scanned = len(tasks)
    st.named = sum(1 for t in tasks if t[7])
    st.unnamed = st.scanned - st.named

    # ── ★★ 多线程解码（2026-09-30 用户要求：解码必须吃智能调度）──────
    #   为什么能并行：zlib/lz4/zstd 都释放 GIL，解码是纯 CPU 无共享状态；
    #   统计只在**主线程**累加（`ex.map` 按序在调用方产出结果）⇒ 无竞态。
    #   并行度取 throttle.recommend_workers("mixed")（读+算的典型），
    #   受全局 `--cpu-limit` 约束；显式 `workers=` 可覆盖。
    try:
        from toolkit_core import throttle as _TH
        n_workers = int(workers) if workers else _TH.recommend_workers("mixed")
    except Exception:                                                # noqa: BLE001
        n_workers = int(workers) if workers else 8
    n_workers = max(1, min(n_workers, max(1, len(tasks))))

    def _one(t):
        """一条：解码 → 比对 → （非 dry-run）写。返回 (kind, rel, err)。"""
        _fid, _row, off, packed, decoded, flag, rel, _is_named = t
        dst = Path(tree_root) / rel
        try:
            data = decode(raw_pack[off:off + packed], decoded or 0, flag or 0) \
                if packed else b""
        except Exception as e:                                       # noqa: BLE001
            return ("failed", rel, "解码失败 %r" % (e,))
        try:
            if dst.is_file():
                old = dst.read_bytes()
                if old == data:
                    return ("same", rel, None)
                # ★★ 内容合法性守卫（2026-09-30）：新的没结构标志、旧的像话 ⇒ 拒写。
                if not allow_suspicious and suspicious_against(old, data):
                    return ("suspicious", rel, "解出内容没有结构标志（树里那份有）⇒ 拒绝覆盖")
                if not dry_run:
                    dst.unlink()
                    dst.write_bytes(data)
                return ("updated", rel, None)
            if not allow_suspicious and not looks_sane(data):
                return ("suspicious", rel, "新增条目解出内容不像话 ⇒ 跳过")
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    dst.unlink()
                dst.write_bytes(data)
            return ("added", rel, None)
        except Exception as e:                                       # noqa: BLE001
            return ("failed", rel, repr(e))

    if len(tasks) > 200 and n_workers > 1:
        from concurrent.futures import ThreadPoolExecutor
        st.parallel_workers = n_workers
        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            for kind, rel, err in ex.map(_one, tasks, chunksize=64):
                if kind == "same":
                    st.same += 1
                elif kind == "added":
                    st.added += 1
                elif kind == "updated":
                    st.updated += 1
                elif kind == "suspicious":
                    st.suspicious += 1
                else:
                    st.failed += 1
                st.note(kind, rel)
                if err and len(st.errors) < 50:
                    st.errors.append("%s: %s" % (rel, err))
    else:
        for t in tasks:
            kind, rel, err = _one(t)
            if kind == "same":
                st.same += 1
            elif kind == "added":
                st.added += 1
            elif kind == "updated":
                st.updated += 1
            elif kind == "suspicious":
                st.suspicious += 1
            else:
                st.failed += 1
            st.note(kind, rel)
            if err and len(st.errors) < 50:
                st.errors.append("%s: %s" % (rel, err))
    return st


def write_ledger(tree_root: Path, stats: List[MergeStats], *, dry_run: bool,
                 out_dir: Optional[Path] = None) -> Path:
    """写合并台账。

    ★ 位置规则（2026-09-29 修）：
      · 真写（dry_run=False）→ 台账落【还原树根】，与产物同源，便于「树 + 账」一起搬
      · dry-run            → 台账落 `out_dir`（默认 30_分析/还原树合并_<日期>），
        **不许污染 41_还原树** —— 那是唯一权威产物，dry-run 不得留任何痕迹。
    """
    ts = time.strftime("%Y%m%d_%H%M%S")
    if dry_run:
        base = Path(out_dir) if out_dir else (
            Path(tree_root).parent / "30_分析" / ("还原树合并_%s" % time.strftime("%Y%m%d")))
        base.mkdir(parents=True, exist_ok=True)
        p = base / ("_热更合并台账_%s_dryrun.json" % ts)
    else:
        p = Path(tree_root) / ("_热更合并台账_%s.json" % ts)
    p.write_text(json.dumps(
        {"schema": "restore-merge-ledger/v1", "generated": ts, "dry_run": dry_run,
         "layers": [s.as_dict() for s in stats]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return p
