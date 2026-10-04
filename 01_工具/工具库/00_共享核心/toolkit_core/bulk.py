# -*- coding: utf-8 -*-
"""批量提取 / 条目筛选 / 产物识别 —— 半全量跑出来的「CLI 该有什么」的落点。

## 为什么有它

跑 1% 半全量（23,037 条 / 1.98 GB）时暴露了 9 条需求，当时**每一条都得手写脚本**：

  1. 按【容器 / 大小 / flag / 编号范围 / 条数上限】筛条目 —— 只能手写 SQL
  2. 进度与吞吐的【机器可读输出】—— 只能看人眼读的 print
  3. 错误按【类别聚合】而不是逐条刷屏
  4. 慢条目必须能被点出来（哪条拖慢了整批）
  5. 落盘命名策略 —— 临时编的 `容器/row_fid.bin`
  6. 落盘的【断点续跑】—— 断了只能整批重来
  7. 产出的【清单文件】（哪条 → 哪个文件 + sha256）
  8. 产物【类型识别】—— 解出来是一坨 bytes
  9. 按类型【转成可用格式】

本模块把这 9 条固定成可复用能力，CLI 只是壳。
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence

# ── 格式注册表（需求 8）。每条的「依据」都写明来源，不凭印象加 ──
# ★ 这份表是【集中】的：此前 `3480c8bb` / `c159410d` / `RGIS` 等魔数散在
#   `mesh_parse2.py`、`gpk_targeted_extract.py`、`lifeafter_unpacker_full.py` 各处，
#   每加一个消费方就得抄一遍。规范《对标_专业拆包流程》§格式识别 已点名
#   「已有（c159410d/3480c8bb/NXPK/SKPW），但散在脚本里 ⇒ 需集中成格式注册表」。
#   依据：00_治理/规范/格式拆解手册.md 附录 A10 + _1110171_结论归档/FX_FILE_AUDIT_report.md
MAGIC: list[tuple[bytes, str, str]] = [
    # ── 图像 / 纹理 ──
    (b"\x89PNG\r\n\x1a\n", "png", "PNG 图"),
    (b"\xff\xd8\xff", "jpg", "JPEG 图"),
    (b"DDS ", "dds", "DDS 纹理（手册 A10：'DDS ' + hdr=124 + 尺寸）"),
    (b"KTX 11", "ktx2", "KTX2 纹理"),
    (b"KTX ", "ktx", "KTX 纹理"),
    # ── 几何 / 材质 ──
    (b"\x34\x80\xc8\xbb", "mesh", ".mesh 网格（手册 A10：3480c8bb 0400 0500…，v4/const5/bone_flag/子网格表）"),
    (b"\xc1\x59\x41\x0d", "c159", ".c159 材质 / .gim 模型文档（手册 A10：c159410d…，非几何，是 c159 对象图）"
                             "★ 实证 2026-09-28：NeoX 字段序列化文本（头 = 魔数 + u32 长度 + 字段名字符串，"
                             "如 AnimationEventTracks / FileName / GisFiles / AnimParam / LightingMaterial）；"
                             "★ 内含【其他资源的引用路径】，可用 extract_c159_paths() 抽出 → 撞库复原文件名（实测 77% 命中）"),
    (b"RGIS", "rgis", ".rgis（手册 A10；character 包里的大件）"),
    # ── 音频 / 视频 ──
    (b"OggS", "ogg", "OGG 音频"),
    (b"RIFF", "riff", "RIFF（wav/webp 等，看第 8-12 字节）"),
    (b"FSB5", "fsb5", "FMOD FSB5 音频库（手册 A11，130 个 .fsb）"),
    # ── 打包 / 序列化 ──
    (b"PK\x03\x04", "zip", "ZIP（也常是 glb 容器/压缩包）"),
    (b"glTF", "glb", "glTF 二进制"),
    (b"\x1bLua", "luac", "Lua 字节码"),
    (b"UnityFS", "unityfs", "UnityFS 资源包"),
    (b"\xcc\xaa\x55\x66", "ccaa5566", "ccaa5566 序列化缓存/配置块"
                             "（FX 审计：effect_cache 99,801 行全此魔数，0 张图片）"
                             "★ 实证 2026-09-28：实为【编译后的着色器字节码】——头 = 魔数 + u32 版本(2) + u32 版本(2) + 零填充，"
                             "载荷内可见 TEXCOORD / float4 / NeoxUBOLocal / SV_Position / Microsoft Shader Compiler；"
                             "⇒ 无路径信息，不做文件名复原"),
    # ── 容器 / 索引（直接提条目时不会出现，但识别时要认得出） ──
    (b"NXPK", "npk", "NPK 容器头（magic@8）"),
    (b"SKPW", "skpw", "SKPW 索引（IDX）"),
    (b"1DPW", "1dpw", "1DPW 纹理包"),
    (b"\x02\x46\x47\x50", "gpk", "GPK 容器内层标记（0x46475002）"),
    (b"CVIS", "cvis", "CVIS（未见文档；同容器内成片出现，待定）"),
    (b"OCTL", "octl", "OCTL 分块容器（块标签 SP/LDGP/MH/LO；未见文档，待定）"),
]


# ── ★ 新增（2026-09-28）：.c159 内嵌路径提取 ──────────────────────────
# 实证依据：取样 2,000 个 .c159（21 MB）→ 抽出 5,899 种含斜杠的路径串；
#          取 400 条撞库 → 命中现有资源名 308 条（77%）。
# ★ 正则量词【必须有界】：无界 `{3,}` 在大段连续可打印字节上会灾难性回溯
#   卡死（此坑已踩过四次），所以下面全部用 {n,m} 有界量词。
_C159_PATH_RE = re.compile(
    rb"[\x20-\x7e]{2,200}[\\/][\x20-\x7e]{1,200}?\.(?:mesh|mtg|gim|gis|gis2"
    rb"|png|dds|tga|jpg|jpeg|sfx|atlas|json|nxs|py|cube|fis|txt|xml|bin"
    rb"|ccaa5566|c159|octl|cvis|rgis|font|mat|mtl)",
    re.I,
)
# 路径里不该出现的字符（出现则说明正则吃多了，切掉前缀）
_C159_BAD_HEAD = re.compile(rb"^[^\w\\/.]+")


def extract_c159_paths(data: bytes, dedupe: bool = True) -> list[str]:
    r"""从 .c159（NeoX 字段序列化文本）里抽出内嵌的【资源引用路径】。

    这些路径【不带容器前缀】（形如 ``model_high_2024\common\grass\yewai\x.gim``），
    抽出去重后交给调用方做【多前缀拼接 + murmur3 撞库】，即可为未命名行复原文件名。

    返回：去重后的路径字符串列表（utf-8 解不出的条目跳过）。
    """
    if not data or data[:4] != b"\xc1\x59\x41\x0d":
        return []
    out: list[str] = []
    seen: set[str] = set()
    for m in _C159_PATH_RE.finditer(data):
        s = _C159_BAD_HEAD.sub(b"", m.group(0))
        if len(s) < 5 or b"." not in s:
            continue
        try:
            t = s.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if dedupe:
            if t in seen:
                continue
            seen.add(t)
        out.append(t)
    return out


def extract_bin_paths(data: bytes, dedupe: bool = True) -> list[str]:
    r"""从 .bin（NeoX 有结构容器）里抽出内嵌的【资源引用路径】。

    ★ 实证 2026-09-28：取样 12 个 .bin → 5 个含路径串，共 290 条；
      熵 5.32 / 可打印率 36% ⇒ 是有结构的明文容器（非压缩非加密）；
      路径形如 ``renwu_icon/xinshoujiaocheng/img_laoxitongshengji902.png``
      （正斜杠、不带 ``ui/`` 前缀）—— 与 .c159 的引用表同类，可用于撞库复原文件名。
      .bin 共 556,606 个（13.5 GB），是第二大名字金矿。

    返回：去重后的路径字符串列表。
    """
    if not data:
        return []
    out: list[str] = []
    seen: set[str] = set()
    for m in _C159_PATH_RE.finditer(data):
        s = _C159_BAD_HEAD.sub(b"", m.group(0))
        if len(s) < 5 or b"." not in s:
            continue
        try:
            t = s.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if dedupe:
            if t in seen:
                continue
            seen.add(t)
        out.append(t)
    return out


def identify(data: bytes) -> tuple[str, str]:
    """返回 (短名, 说明)。认不出给 ('bin', '未知二进制')，不硬安一个。"""
    if not data:
        return "empty", "空载荷"
    # ★ 有些格式魔数不在第 0 字节：MP4/MOV 的 ftyp 在偏移 4（前面是 4 字节 box 长度）
    if len(data) >= 12:
        box = data[4:8]
        if box == b"ftyp":
            brand = data[8:12]
            name = {b"isom": "MP4 (isom)", b"mp42": "MP4 (mp42)", b"mp41": "MP4 (mp41)",
                    b"qt  ": "MOV/QuickTime"}.get(brand, "MP4/ISO-BMFF")
            return "mp4", "%s（ftyp@4，brand=%s）" % (name, brand.decode("ascii", "replace").strip())
        if box in (b"moov", b"mdat", b"free", b"wide", b"skip"):
            return "quicktime?", "疑似 MOV/MP4 中段（%s box@4）" % box.decode("ascii", "replace")
    for magic, short, desc in MAGIC:
        if data.startswith(magic):
            if short == "riff" and len(data) >= 12:
                sub = data[8:12]
                if sub == b"WAVE":
                    return "wav", "RIFF/WAVE 音频"
                if sub == b"WEBP":
                    return "webp", "RIFF/WEBP 图"
            return short, desc
    if re.match(rb"^[\x20-\x7e\r\n\t]{12,}", data):
        return "text", "可读文本"
    if data[:4] == b"\x28\xb5\x2f\xfd":
        return "zstd", "zstd 压缩流（未解压）"
    if data[:2] == b"\x78\xda" or data[:2] == b"\x78\x9c":
        return "zlib", "zlib 压缩流（未解压）"
    if data[:1] in b"[{(":
        return "marshal", "疑似 Python marshal 对象流"
    # DXT/BC 压缩纹理没有统一魔数；一个弱判据：长度是 128 的倍数且前 4 字节像宽高
    if len(data) % 128 == 0 and len(data) >= 4096:
        w = int.from_bytes(data[0:2], "little")
        h = int.from_bytes(data[2:4], "little")
        if 4 <= w <= 8192 and 4 <= h <= 8192:
            return "dds?", "疑似无头 DDS（长宽 %dx%d，长度是 128 的倍数）" % (w, h)
    return "bin", "未知二进制"


# ── 筛选（需求 1） ──
@dataclass
class Filter:
    containers: Sequence[str] = ()      # 容器名子串，任一命中即可
    flags: Sequence[int] = ()
    min_size: Optional[int] = None      # 按 decoded 算
    max_size: Optional[int] = None
    row_range: Optional[tuple[int, int]] = None
    fids: Sequence[str] = ()
    kinds: Sequence[str] = ()
    sample_per_container: Optional[int] = None
    percent: Optional[float] = None     # 0-100，按 (row_index*7919) % 1000 均匀取
    limit: Optional[int] = None

    def where(self) -> tuple[str, list[Any]]:
        w, p = ["1=1"], []
        if self.containers:
            w.append("(" + " OR ".join("container LIKE ?" for _ in self.containers) + ")")
            p += ["%" + c + "%" for c in self.containers]
        if self.flags:
            w.append("flag IN (" + ",".join("?" for _ in self.flags) + ")")
            p += list(self.flags)
        if self.kinds:
            w.append("kind IN (" + ",".join("?" for _ in self.kinds) + ")")
            p += list(self.kinds)
        if self.min_size is not None:
            w.append("decoded >= ?"); p.append(int(self.min_size))
        if self.max_size is not None:
            w.append("decoded <= ?"); p.append(int(self.max_size))
        if self.row_range:
            w.append("row_index BETWEEN ? AND ?"); p += [int(self.row_range[0]), int(self.row_range[1])]
        if self.fids:
            w.append("fid_hex IN (" + ",".join("?" for _ in self.fids) + ")")
            p += [f.upper() for f in self.fids]
        if self.percent is not None:
            mod = 1000
            w.append("(row_index * 7919) %% %d < ?" % mod)
            p.append(max(1, int(mod * self.percent / 100.0)))
        return " AND ".join(w), p

    def describe(self) -> str:
        bits = []
        if self.containers:
            bits.append("容器~%s" % "|".join(self.containers))
        if self.flags:
            bits.append("flag∈{%s}" % ",".join(map(str, self.flags)))
        if self.min_size is not None:
            bits.append("≥%s" % _sz(self.min_size))
        if self.max_size is not None:
            bits.append("≤%s" % _sz(self.max_size))
        if self.row_range:
            bits.append("row %d:%d" % self.row_range)
        if self.fids:
            bits.append("fid×%d" % len(self.fids))
        if self.sample_per_container:
            bits.append("每容器 %d 条" % self.sample_per_container)
        if self.percent is not None:
            bits.append("%.2f%%" % self.percent)
        if self.limit:
            bits.append("上限 %d" % self.limit)
        return " ".join(bits) or "（无筛选 = 全部）"


def _sz(n) -> str:
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return "%.1f%s" % (n, u)
        n /= 1024


COLS = ("container", "row_index", "fid_hex", "payload_offset", "packed", "decoded", "flag", "kind")


def select(conn, f: Filter) -> list[tuple]:
    """按筛选取条目。sample_per_container 在 SQL 之后再按容器截断。"""
    w, p = f.where()
    sql = "SELECT %s FROM entries WHERE %s ORDER BY container,row_index" % (",".join(COLS), w)
    rows = conn.execute(sql, p).fetchall()
    if f.sample_per_container:
        n = int(f.sample_per_container)
        per: dict[str, int] = {}
        kept = []
        for r in rows:
            c = r[0]
            if per.get(c, 0) < n:
                per[c] = per.get(c, 0) + 1
                kept.append(r)
            if f.limit and len(kept) >= f.limit:
                break
        rows = kept
    elif f.limit:
        rows = rows[: int(f.limit)]
    return rows


def summarize(rows: Iterable[tuple], by: str = "container") -> dict:
    """分组统计（需求 1 的「先看形状再决定抽多少」）。"""
    idx = {"container": 0, "flag": 6, "kind": 7}.get(by)
    if idx is None:
        raise ValueError("--by 只支持 container / flag / kind")
    agg: dict[str, dict] = {}
    for r in rows:
        k = str(r[idx])
        a = agg.setdefault(k, {"count": 0, "packed": 0, "decoded": 0})
        a["count"] += 1
        a["packed"] += r[4] or 0
        a["decoded"] += r[5] or 0
    return {"by": by, "groups": agg,
            "total": {"count": sum(v["count"] for v in agg.values()),
                      "packed": sum(v["packed"] for v in agg.values()),
                      "decoded": sum(v["decoded"] for v in agg.values())}}


# ── 批量提取（需求 2-7） ──
@dataclass
class BulkReport:
    selected: int = 0
    extracted: int = 0
    skipped_resume: int = 0
    empty_entries: int = 0       # 容器声明的 0 字节占位条目（合法，不算错误）
    bytes_out: int = 0
    seconds_select: float = 0.0
    seconds_read: float = 0.0
    seconds_decode: float = 0.0
    seconds_write: float = 0.0
    seconds_total: float = 0.0
    errors: dict = field(default_factory=dict)          # 类别 → 条数（需求 3）
    error_samples: dict = field(default_factory=dict)   # 类别 → 前 3 条样例
    signatures: dict = field(default_factory=dict)      # 类型 → 条数（需求 8）
    slow: list = field(default_factory=list)            # 最慢 N 条（需求 4）
    files: list = field(default_factory=list)           # 清单（需求 7）
    out_root: str = ""

    def as_dict(self) -> dict:
        d = dict(self.__dict__)
        d["seconds_total"] = round(self.seconds_total, 2)
        return d


_EXT_BAD = re.compile(r"[^0-9A-Za-z_]")


def safe_ext(short: str) -> str:
    """把 identify 的类型短名清洗成【能当扩展名】的形式。

    ★ 为什么必须清洗：identify 的弱猜测标签带 '?'（`dds?` / `quicktime?`），
      而 '?' 在 Windows 上是非法文件名字符 ⇒ 直接拼进路径写盘会
      `OSError: [Errno 22] Invalid argument`（全量实测实测 4 例，
      文件名 `00023708.dds?`）。清洗后为空就退回 'bin'。
    """
    s = _EXT_BAD.sub("", short or "")
    return s or "bin"


def build_dir_map(containers) -> dict:
    """容器 → 输出目录名。**只在真撞车时才消歧。**

    ★ 为什么不能一律用 Path(cont).stem：实测 `Documents\\script.py314.lc.npk` 与
      `script.py314.lc.npk` 的 stem 都是 `script.py314.lc` ⇒ 写进同一目录 ⇒
      行号相同的文件互相覆盖，全量实测【丢了 26,886 个】
      （2,300,843-67-26,886=2,273,890 与磁盘实测完全吻合）。
    ★ 为什么也不一律用完整路径：那样会**改掉所有容器的目录名**，
      已有的 227 万份产物全部作废、要 193 GB 重来。
      ⇒ 折中：stem 在本批容器里唯一就用 stem（人看得懂、且保住旧产物），
        撞车的那几个才用完整路径形式（`Documents__script.py314.lc`）。
    """
    stems = collections.Counter(Path(c).stem for c in containers)
    out = {}
    for c in containers:
        st = Path(c).stem
        if stems[st] == 1:
            out[c] = st
        else:
            s = c.replace("\\", "/").replace("/", "__")
            suf = Path(c).suffix
            out[c] = s[: -len(suf)] if suf else s
    return out


def cont_dir(cont: str, dir_map=None) -> str:
    """单个容器的目录名。不给 dir_map 时退回「完整路径」形式（保守，保证唯一）。"""
    if dir_map and cont in dir_map:
        return dir_map[cont]
    s = cont.replace("\\", "/").replace("/", "__")
    suf = Path(cont).suffix
    return s[: -len(suf)] if suf else s


def name_for(cont: str, row: int, fid: str, name_by: str, ext: str, dir_map=None) -> str:
    """命名（需求 5）。★ 游戏内逻辑路径当前拿不到，所以只能 row/fid —— 如实说明。

    ext 会先经 safe_ext 清洗（见那里对 '?' 的说明）。
    目录名由 build_dir_map 决定（stem 唯一就用 stem，撞车才用完整路径）。
    """
    base = cont_dir(cont, dir_map)
    ext = safe_ext(ext)
    if name_by == "fid":
        return "%s/%s.%s" % (base, fid, ext)
    if name_by == "row":
        return "%s/%08d.%s" % (base, row, ext)
    return "%s/%08d_%s.%s" % (base, row, fid, ext)


def bulk_extract(
    conn,
    res_root: Path,
    f: Filter,
    out_root: Path,
    *,
    unpack: Callable[[bytes, int, int], bytes],
    name_by: str = "row",
    resume: bool = False,
    manifest: Optional[Path] = None,
    progress: Optional[Callable[[dict], None]] = None,
    slow_n: int = 5,
    decode: bool = True,
    policy=None,
    workers: Optional[int] = None,
) -> BulkReport:
    """批量提取。**按容器并行**（容器内顺序读，容器间并行）。

    workers：显式并行数；不给则由 policy（默认 LoadPolicy）算 = 核数 × cpu_limit%。
    policy ：LoadPolicy，决定并行预算与限流上限。

    ★ 并行不改变结果：每条的「读—解—写」互相独立，只有计数与清单需要合并。
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from toolkit_core.throttle import LoadGate, LoadPolicy

    rep = BulkReport(out_root=str(out_root))
    t_all = time.time()
    pol = policy or LoadPolicy(kinds=("decode",))
    n_workers = workers or pol.workers()
    gate = LoadGate(pol, every=20000)

    t = time.time()
    rows = select(conn, f)
    rep.selected = len(rows)
    rep.seconds_select = time.time() - t

    # 按容器归组：一个容器一个任务
    by_cont: dict = {}
    for r in rows:
        by_cont.setdefault(r[0], []).append(r)
    # ★ 目录名映射：只在本批容器里 stem 撞车时才消歧（保住已有产物）
    dir_map = build_dir_map(by_cont.keys())

    state_path = out_root / ".bulk_state.json"
    done: set[str] = set()
    # ★ 只在 --resume 时【读】状态；但状态文件【总是写】（见 finally）。
    if resume and state_path.is_file():
        try:
            done = set(json.loads(state_path.read_text(encoding="utf-8")).get("done", []))
        except Exception:
            done = set()
    base_done = set(done)

    mf = None
    mf_lock = threading.Lock()
    if manifest:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        mf = manifest.open("a" if resume else "w", encoding="utf-8")

    cnt = [0]                       # 已处理条数（跨线程）
    cnt_lock = threading.Lock()

    def _one(cont: str, my_rows: list) -> dict:
        """处理一个容器的全部条目，返回局部结果（不共享可变状态）。"""
        local = {"extracted": 0, "skipped_resume": 0, "empty_entries": 0, "bytes": 0,
                 "read": 0.0, "decode": 0.0, "write": 0.0,
                 "signatures": {}, "errors": {}, "error_samples": {}, "files": [],
                 "slow": [], "done": []}
        src_path = res_root / cont
        if not src_path.is_file():
            local["errors"]["容器缺失"] = local["errors"].get("容器缺失", 0) + 1
            local["error_samples"].setdefault("容器缺失", []).append(cont)
            return local
        # 先在主线程已选好的行上过滤续跑，再开文件（避免空转 IO）
        todo = [r for r in my_rows if ("%s|%d" % (cont, r[1])) not in base_done]
        local["skipped_resume"] = len(my_rows) - len(todo)
        with src_path.open("rb") as handle:
            for row, fid, poff, packed, decoded, flag, kind in (
                    (r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in todo):
                key = "%s|%d" % (cont, row)
                try:
                    t0 = time.time()
                    handle.seek(poff)
                    raw = handle.read(packed)
                    d_read = time.time() - t0
                    if len(raw) != packed:
                        raise IOError("短读 %d/%d" % (len(raw), packed))
                    t0 = time.time()
                    data = unpack(raw, decoded, flag) if decode else raw
                    d_dec = time.time() - t0
                    if not data:
                        # 容器声明 0 字节 ⇒ 合法占位条目，不算错（A42）
                        if decoded <= 0 and packed <= 0:
                            local["empty_entries"] += 1
                            local["done"].append(key)
                            continue
                        raise ValueError("解出空（容器声明 decoded=%d/packed=%d）"
                                         % (decoded, packed))
                    if decode and decoded != packed and len(data) != decoded:
                        raise ValueError("长度不符 %d != %d" % (len(data), decoded))
                    short, _desc = identify(data)
                    t0 = time.time()
                    dest = out_root / name_for(cont, row, fid, name_by, safe_ext(short),
                                               dir_map)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                    d_wr = time.time() - t0

                    local["read"] += d_read
                    local["decode"] += d_dec
                    local["write"] += d_wr
                    local["extracted"] += 1
                    local["bytes"] += len(data)
                    local["signatures"][short] = local["signatures"].get(short, 0) + 1
                    # ★ 清单里同时记「识别原标签」与「实际扩展名」——两者可能不同
                    #   （如 type='dds?' → ext='dds'），不然后人看清单会困惑。
                    rec = {"fid": fid, "container": cont, "row": row, "file": str(dest),
                           "bytes": len(data), "type": short, "ext": safe_ext(short),
                           "sha256": hashlib.sha256(data).hexdigest()}
                    local["files"].append(rec)
                    local["done"].append(key)
                    if d_read + d_dec + d_wr > 0.02:
                        local["slow"].append({"seconds": round(d_read + d_dec + d_wr, 3),
                                              "container": cont, "row": row,
                                              "decoded": decoded, "flag": flag})
                except Exception as e:
                    k = type(e).__name__
                    local["errors"][k] = local["errors"].get(k, 0) + 1
                    s = local["error_samples"].setdefault(k, [])
                    if len(s) < 3:
                        s.append("%s row %s: %s" % (cont, row, str(e)[:100]))

                with cnt_lock:
                    cnt[0] += 1
                    n = cnt[0]
                if n % 20000 == 0:
                    gate.tick(n, force=True)
                    if progress:
                        el = time.time() - t_all
                        progress({"done": n, "total": len(rows),
                                  "extracted": rep.extracted + local["extracted"],
                                  "bytes": rep.bytes_out + local["bytes"],
                                  "elapsed": round(el, 2),
                                  "rate_rows_s": round(n / el, 1) if el else 0,
                                  "rate_MB_s": round((rep.bytes_out + local["bytes"]) / 2**20 / el, 2) if el else 0,
                                  "workers": n_workers})
        # 清单落盘（锁串行，避免交错）
        if mf and local["files"]:
            with mf_lock:
                for rec in local["files"]:
                    mf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if progress:
            el = time.time() - t_all
            n = cnt[0]
            progress({"done": n, "total": len(rows),
                      "extracted": rep.extracted + local["extracted"],
                      "bytes": rep.bytes_out + local["bytes"],
                      "elapsed": round(el, 2),
                      "rate_rows_s": round(n / el, 1) if el else 0,
                      "rate_MB_s": round((rep.bytes_out + local["bytes"]) / 2**20 / el, 2) if el else 0,
                      "workers": n_workers, "container_done": cont})
        return local

    try:
        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            futs = {ex.submit(_one, c, rs): c for c, rs in by_cont.items()}
            for fut in as_completed(futs):
                r = fut.result()
                rep.extracted += r["extracted"]
                rep.skipped_resume += r["skipped_resume"]
                rep.empty_entries += r["empty_entries"]
                rep.bytes_out += r["bytes"]
                rep.seconds_read += r["read"]
                rep.seconds_decode += r["decode"]
                rep.seconds_write += r["write"]
                for k, v in r["signatures"].items():
                    rep.signatures[k] = rep.signatures.get(k, 0) + v
                for k, v in r["errors"].items():
                    rep.errors[k] = rep.errors.get(k, 0) + v
                for k, v in r["error_samples"].items():
                    s = rep.error_samples.setdefault(k, [])
                    s.extend(v[:max(0, 3 - len(s))])
                rep.files.extend(r["files"])
                rep.slow.extend(r["slow"])
                done.update(r["done"])
    finally:
        if mf:
            mf.close()
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"done": sorted(done), "at": time.time()}),
                              encoding="utf-8")

    rep.slow.sort(key=lambda x: -x["seconds"])
    del rep.slow[slow_n:]
    rep.seconds_total = time.time() - t_all
    return rep
