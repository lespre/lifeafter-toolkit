# -*- coding: utf-8 -*-
"""路径 → fid 的唯一实现。所有调用方都从这里取，禁止再各写一份。

## 为什么要有这个模块

项目里曾经【五份】path_id 实现，各自约定不同。实测（2026-09-26）已确认至少两处不一致：

    npk_reader.path_id            utf-8      不归一分隔符
    gpk_npk_index.path_id_raw     utf-8      不归一分隔符
    thfb_toolkit.path_id          utf-8      不归一分隔符
    unified_index.path_fid        latin1     归一（/ → \\）
    resource_resolver.path_id     latin1     归一（/ → \\）

实测出的具体不一致：

    路径 ui/damoshi_icon/jijianbiaoqing_icon/ku.png
      npk_reader / gpk_index / thfb → F3B7AC1AE39B3C20
      resource_resolver             → E719403AB6824519      ← 不同

    路径 黑名单/测试表.csv（含中文）
      resource_resolver             → UnicodeEncodeError     ← 直接抛

后果：同一路径换个入口就得到不同 fid；resource_resolver 遇中文路径抛异常，
     其上层（texture_extractor 等）因此静默拿不到数据；且没有统一口径，
     无法判断哪条链更可信。

## 本模块的立场：不猜，给变体空间

游戏侧对路径的规范化规则（编码 / 分隔符 / 大小写 / 扩展名）无法从外部百分百确证，
所以本模块**不写死一种「唯一正确」**，而是把可能空间显式化：

    fid_of(path, encoding, normalize_sep)   纯函数，参数显式
    fids_for(path, ...)                     → [(变体规格, fid)] 变体空间
    resolve(path, available)                → 命中的变体 or None

于是「哪条链更可信」变成**可测量的事实**（resolve 在语料上的命中率），
而不是各写各的约定。
"""
from __future__ import annotations

from pathlib import Path

# ── 常量 ────────────────────────────────────────────────────
SEED_HI = 0x77777777
SEED_LO = 0x66666666
#: 默认编码。游戏路径按 UTF-8 存储的概率更高（中文资源名存在），
#: 且对纯 ASCII 路径 utf-8 与 latin1 逐字节等价 —— 所以取 utf-8 不会伤到 ASCII 场景，
#: 却能覆盖 latin1 直接编不出来的中文路径。
DEFAULT_ENCODING = "utf-8"
#: 变体空间里尝试的编码顺序（默认编码优先）
ENCODINGS = ("utf-8", "latin1")
#: 路径结尾常见扩展名，用于「去扩展名 / 换大小写」变体
KNOWN_EXTS = (".png", ".dds", ".tga", ".jpg", ".mesh", ".gim", ".mat", ".cubemap",
              ".fsb", ".wav", ".ogg", ".mp3", ".json", ".txt", ".xml", ".bin",
              ".atlas", ".anim", ".sfx", ".prefab", ".cgfx", ".cgmat", ".mtg",
              ".skeleton", ".pvr", ".ini", ".csv", ".nxs", ".lua", ".py")


# ── 基础算法 ────────────────────────────────────────────────
def murmur3_x86_32(data: bytes, seed: int) -> int:
    """MurmurHash3 x86 32-bit（游戏 path_id 用的就是它）。"""
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
    tail = data[end:]
    if tail:
        k = 0
        for i, byte in enumerate(tail):
            k |= byte << (8 * i)
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h & 0xFFFFFFFF


def fid_of(path: str, *, encoding: str = DEFAULT_ENCODING,
           normalize_sep: bool = True) -> int:
    """逻辑路径 → 64 位 fid = (murmur3(SEED_HI) << 32) | murmur3(SEED_LO)。

    编码与分隔符归一都**显式给出**，不再由各调用方偷偷决定。
    编码失败时抛 ValueError（如实失败，不静默换算法）。
    """
    text = path.replace("/", "\\") if normalize_sep else path
    try:
        raw = text.encode(encoding)
    except UnicodeEncodeError as exc:
        raise ValueError(f"路径不能按 {encoding} 编码：{path!r}") from exc
    return ((murmur3_x86_32(raw, SEED_HI) << 32) | murmur3_x86_32(raw, SEED_LO))


# ── 变体空间 ────────────────────────────────────────────────
def _case_variants(name: str) -> list[str]:
    out = [name]
    for cand in (name.lower(), name.upper()):
        if cand not in out:
            out.append(cand)
    stem = name.rsplit("\\", 1)
    if len(stem) == 2:
        for cand in (stem[0].lower() + "\\" + stem[1],
                     stem[0] + "\\" + stem[1].lower(),
                     stem[0].lower() + "\\" + stem[1].lower()):
            if cand not in out:
                out.append(cand)
    return out


def fids_for(path: str, *, encodings=ENCODINGS, sep_variants: bool = True,
             case_variants: bool = True, ext_variants: bool = False):
    """路径的变体空间 → [(规格, fid)]。

    规格是一个 dict，说明这条 fid 是怎么算出来的（编码/分隔/大小写/扩展名），
    便于命中后【如实报告是哪一种】，而不是笼统说「找到了」。
    """
    base = path.strip()
    names = [base]
    if sep_variants:
        alt = base.replace("\\", "/")
        if alt not in names:
            names.append(alt)
    if case_variants:
        for n in list(names):
            for c in _case_variants(n):
                if c not in names:
                    names.append(c)
    if ext_variants:
        for n in list(names):
            low = n.lower()
            for ext in KNOWN_EXTS:
                if low.endswith(ext):
                    bare = n[: -len(ext)]
                    if bare and bare not in names:
                        names.append(bare)
                    break
    out, seen = [], set()
    for name in names:
        for norm in (True, False):
            for enc in encodings:
                try:
                    fid = fid_of(name, encoding=enc, normalize_sep=norm)
                except ValueError:
                    continue
                if fid in seen:
                    continue
                seen.add(fid)
                out.append(({"input": name, "encoding": enc, "normalize_sep": norm}, fid))
    return out


def resolve(path: str, available, **kw):
    """在 `available`（可用 fid 的集合）里解析路径。

    返回 (规格, fid) 或 None。**命中率 = resolve 在语料上非 None 的比例** ——
    这就是全项目统一的命中率口径。
    """
    for spec, fid in fids_for(path, **kw):
        if fid in available:
            return spec, fid
    return None


def hit_rate(pairs, available, **kw) -> dict:
    """批量算命中率。pairs: [(标签, 路径)] 或 [路径]。"""
    total = hit = 0
    miss = []
    by_encoding, by_norm = {}, {}
    for item in pairs:
        label, path = item if isinstance(item, (tuple, list)) else (item, item)
        total += 1
        got = resolve(path, available, **kw)
        if got is None:
            miss.append(label)
        else:
            spec, _fid = got
            hit += 1
            by_encoding[spec["encoding"]] = by_encoding.get(spec["encoding"], 0) + 1
            by_norm[str(spec["normalize_sep"])] = by_norm.get(str(spec["normalize_sep"]), 0) + 1
    return {"total": total, "hit": hit,
            "rate": (hit / total) if total else None,
            "by_encoding": by_encoding, "by_normalize_sep": by_norm,
            "miss_sample": miss[:10]}


# ── 交叉校验：其它实现是否与本模块一致 ──────────────────────
#: 已知的其它 path_id 实现（用于一致性核对）。键是给人看的名字。
def known_callers(project_root: Path | None = None) -> list[dict]:
    """列出项目里现存的 path_id 实现位置（供 cross_check 逐个核对）。"""
    import importlib.util
    root = Path(project_root) if project_root else Path(r"E:/la拆包项目")
    tools = root / "01_工具" / "工具库"
    return [
        {"name": "npk_reader.path_id",
         "path": tools  / "01_解码定位复原" / "解包与扫描" / "npk_reader.py", "attr": "path_id",
         "note": "utf-8，不归一分隔符"},
        {"name": "gpk_npk_index.path_id_raw",
         "path": tools  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py", "attr": "path_id_raw",
         "note": "utf-8，不归一分隔符"},
        {"name": "unified_index.path_fid", "module": "toolkit_core.unified_index",
         "path": tools  / "00_共享核心" / "toolkit_core" / "unified_index.py", "attr": "path_fid",
         "note": "latin1，归一分隔符"},
        {"name": "resource_resolver.path_id", "module": "toolkit_core.resource_resolver",
         "path": tools  / "00_共享核心" / "toolkit_core" / "resource_resolver.py",
         "attr": "path_id", "note": "latin1，归一分隔符"},
        {"name": "thfb_toolkit.path_id",
         "path": tools  / "01_解码定位复原" / "哈希提取" / "thfb_toolkit.py", "attr": "path_id",
         "note": "utf-8，不归一分隔符"},
    ]


def cross_check(probe_paths=None, project_root=None) -> dict:
    """把各实现的输出与「本模块的基准」逐条对照。

    基准取 DEFAULT_ENCODING + normalize_sep=True。本函数不修改任何东西，
    只如实报告谁一致、谁不一致、谁直接抛异常。
    """
    import importlib.util
    probes = probe_paths or [
        r"common\env_map\qiangpi.cube",              # 纯 ASCII + 反斜杠
        "ui/damoshi_icon/jijianbiaoqing_icon/ku.png",  # 纯 ASCII + 正斜杠
        r"黑名单\测试表.csv",                          # 含中文
    ]
    rows = []
    for spec in known_callers(project_root):
        p = Path(spec["path"])
        if not p.is_file():
            rows.append({"caller": spec["name"], "error": "文件不存在", "note": spec["note"]})
            continue
        try:
            if spec.get("module"):
                # toolkit_core 内的模块有相对导入，按路径 exec 会炸，必须走包导入
                import importlib as _il
                m = _il.import_module(spec["module"])
            else:
                s = importlib.util.spec_from_file_location("_cc_" + spec["attr"], p)
                m = importlib.util.module_from_spec(s)
                s.loader.exec_module(m)
            fn = getattr(m, spec["attr"])
        except Exception as exc:  # noqa: BLE001
            rows.append({"caller": spec["name"], "error": f"加载失败：{type(exc).__name__}",
                         "note": spec["note"]})
            continue
        detail = []
        for probe in probes:
            try:
                got = fn(probe)
            except Exception as exc:  # noqa: BLE001
                detail.append({"probe": probe, "got": None,
                               "error": f"{type(exc).__name__}"})
                continue
            try:
                want = fid_of(probe)
            except ValueError:
                want = None
            detail.append({"probe": probe, "got": f"{got:016X}",
                           "want": f"{want:016X}" if want is not None else None,
                           "match": (want is not None and got == want)})
        bad = [d for d in detail if d.get("error") or d.get("match") is False]
        rows.append({"caller": spec["name"], "note": spec["note"],
                     "agree": not bad, "detail": detail})
    algo = _algo_check(project_root)
    return {"baseline": f"encoding={DEFAULT_ENCODING}, normalize_sep=True",
            "callers": rows,
            "algo_check": algo,
            "disagreeing": [r["caller"] for r in rows if r.get("agree") is False],
            "errored": [r["caller"] for r in rows if r.get("error")
                        or any(d.get("error") for d in r.get("detail", []))]}


def _algo_check(project_root=None) -> dict:
    """murmur3 逐位对照。

    ★ 算法不一致比约定不一致更危险 —— 约定不同只是命中与否，算法不同会算出【另一种】
      看似合理的 fid，静默错配。所以单独核对一遍。
    """
    import importlib.util
    import random
    random.seed(20260926)
    data = bytes(random.randrange(256) for _ in range(997))   # 非 4 字节对齐，覆盖尾部块
    seeds = (0, 1, 0x66666666, 0x77777777, 0xFFFFFFFF, 12345)
    out = {"samples": len(seeds) * 5, "mismatch": [], "missing": []}
    for spec in known_callers(project_root):
        p = Path(spec["path"])
        if not p.is_file():
            continue
        try:
            if spec.get("module"):
                import importlib as _il
                m = _il.import_module(spec["module"])
            else:
                s = importlib.util.spec_from_file_location("_algo_" + spec["attr"], p)
                m = importlib.util.module_from_spec(s)
                s.loader.exec_module(m)
            fn = getattr(m, "murmur3_x86_32", None)
        except Exception:  # noqa: BLE001
            continue
        if fn is None:
            out["missing"].append(spec["name"])
            continue
        for seed in seeds:
            try:
                if fn(data, seed) != murmur3_x86_32(data, seed):
                    out["mismatch"].append({"caller": spec["name"], "seed": hex(seed)})
            except Exception as exc:  # noqa: BLE001
                out["mismatch"].append({"caller": spec["name"], "seed": hex(seed),
                                        "error": type(exc).__name__})
    out["ok"] = not out["mismatch"]
    return out


if __name__ == "__main__":
    import json
    print("== 交叉校验：各 path_id 实现是否与基准一致 ==")
    print("   基准:", f"encoding={DEFAULT_ENCODING}, normalize_sep=True")
    rep = cross_check()
    for r in rep["callers"]:
        if r.get("error"):
            print(f"  ✗ {r['caller']:<34} {r['error']}")
            continue
        mark = "✓" if r["agree"] else "✗"
        print(f"  {mark} {r['caller']:<34} {r['note']}")
        for d in r["detail"]:
            if d.get("error"):
                print(f"      {d['probe'][:44]:<46} 抛 {d['error']}")
            elif d.get("match") is False:
                print(f"      {d['probe'][:44]:<46} 得 {d['got']} ≠ 基准 {d['want']}")
    algo = rep["algo_check"]
    print(f"  murmur3 算法逐位对照：{'✓ 全部一致' if algo['ok'] else '✗ 有不一致'}"
          f"（{algo['samples']} 次取样）")
    for x in algo["mismatch"]:
        print("      ✗", x)
    if algo["missing"]:
        print("      未暴露 murmur3 的实现：", ", ".join(algo["missing"]))
    print()
    print("  约定不一致：", rep["disagreeing"] or "无")
    print("  报错      ：", rep["errored"] or "无")
