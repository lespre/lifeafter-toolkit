# -*- coding: utf-8 -*-
"""称号动态底图：按「每条称号自己的 csb 帧序列」重建循环动画（2026-11-07 复核口径）

## 为什么重写
旧口径 `build_title_dyn_from_pe.py` 按**家族**（ui/chenghao/<家族>/**）把同一家族下
所有带 loop/_00 的贴图当成一个序列，实测会把**不同变体的不同底图**拼成动画：
  ugc          = 金星 / 蓝晶 / 青山 三张完全不同的牌，轮流播 ⇒ 底图乱跳
  miwuhaiyu    = icon_chenghao_156000/1/2 三个不同图标
  kumufengchun = 01/02/03 三个变体的帧混在一起
  tianxie      = meilizhi_01 / meilizhi_02 / tianxie_02 三个变体混在一起
又用 `key in anim_csb` 子串把同一份家族动画挂给十几张卡 ⇒ 卡上底图根本不是自己的。
本脚本**不再引用** assets/title_dyn/pe/<家族>.webp。

## 数据链（全部可复核，无 LCS、无拼音猜测、无按名配平）
  item.dyn_tex  = csb 载荷里引用的首帧贴图名（build_title_dyn_assets.py 扫 csb 得到，属冻结产物）
    → 去掉末尾帧序号，得到精确序列前缀 P
    → pe_index.sqlite3 精确匹配 `ui/<P><2~5 位帧号>.<ext>`（帧号 ≤ 999，排除道具 ID 型编号）
    → 同前缀 ≥ MIN_SEQ_FRAMES 帧、按帧号排序、等距抽到 ≤ MAX_FRAMES 帧
    → PE 包 pe_gres_android/*.gpk 解 KTX 得 RGBA（只扫用到的 9 个包，每包一次）
    → 内容校验（见下）→ loop=0 的 WebP → assets/title_dyn/seq/<序列短名>_<hash>.webp
    → 回填 item.dyn_webp / dyn_webp_source / dyn_anim_frames / dyn_anim_ms / dyn_seq

## 内容校验（防止把「编号不同的静态图标」误当动画帧）
  ① 同尺寸：抽帧后所有帧尺寸必须一致（尺寸不同 ⇒ 是叠加层/别的资源，拒绝）
  ② 首帧一致：与 item.dyn_png（该卡已导出的静态首帧，bbox 归一后）平均像素差 ≤ 12
  ③ 邻帧平滑：相邻帧平均像素差中位数 ≤ 30，突跳帧占比 ≤ 1/4
  ④ 首尾闭合：末帧与首帧差 ≤ 3×中位+12（循环动画应回到起点；不同图标不满足）
  任何一条不过 ⇒ 不生成、不挂载，按铁律跳过并写进报告。

## 未通过序列校验的条目（两级回退，仍不猜）
  ① assets/title_dyn/anim/<csb 名>.webp 存在且通过同一套内容校验 ⇒ 用它；
  ② 否则保留静态首帧 dyn_png，清除 dyn_webp 等字段，标签如实写「动态 · 仅首帧」。
★ 这一步同时修掉「86 条磁盘上已有 csb 动画、板里却没挂 dyn_webp」的漏挂。

## 幂等
dry-run 默认；`--apply` 才写盘。所有产物由「板数据 + PE 索引 + PE 包」唯一决定，
同一输入重跑字节一致；`meta.notes` 用 notes_util.append_note() 幂等追加。

用法：
  python build_title_dyn_sequences.py            # dry-run，打印逐序列判据与汇总
  python build_title_dyn_sequences.py --apply    # 落盘（WebP + 板 .json/.js）
  python build_title_dyn_sequences.py --verify   # 只校验现有产物（文件/帧数/节奏/首帧），不写盘
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from la_paths import PROJ, WEB, INDEX_ROOT  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from notes_util import append_note  # noqa: E402
from title_anim_pace import frame_duration, read_durations  # noqa: E402

CORE = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))
from toolkit_core import android_gpk as AG  # noqa: E402

BOARD = WEB / "data/boards/title_catalog.json"
PE_DB = INDEX_ROOT / "热更检测/pe_index.sqlite3"
PE_PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
SEQ_DIR = WEB / "assets/title_dyn/seq"
ANIM_DIR = WEB / "assets/title_dyn/anim"

# ── 口径常量（唯一来源，改这里即可全量重算）────────────────────────
MIN_SEQ_FRAMES = 8       # 少于 8 张的多半是「编号不同的静态图标」，不是帧
MAX_FRAMES = 40          # 与既有导出器一致，控体积
MAX_FRAME_NO = 999       # 帧号上限；6 位道具 ID（如 icon_chenghao_156000）不算帧号
MAX_W = 160              # 卡片视觉槽只用 54/112px 高，160 宽足够
WEBP_QUALITY = 60
NORM_SIZE = (128, 64)    # 内容校验的归一化尺寸
IDENTITY_MAX_DIFF = 12.0       # 构建期：原始 KTX 首帧 vs 静态底图（实测合格帧接近 0）
VERIFY_IDENTITY_MAX_DIFF = 25.0  # 校验期：WebP 有损压缩 + 并集裁边后的容差
SMOOTH_MEDIAN_MAX = 30.0
OUTLIER_K = 3.0
OUTLIER_B = 12.0
TEX_EXT_RE = r"(?:ktx|png|jpg|bc7|dds)"
FRAME_RE = re.compile(r"(\d{2,5})\.(?:ktx|png|jpg|bc7|dds)$", re.I)


def sequence_prefix(dyn_tex: str) -> str | None:
    """csb 首帧贴图名 → 精确序列前缀（不做模糊匹配）。"""
    t = str(dyn_tex or "").replace("\\", "/")
    if t.lower().startswith("ui/"):
        t = t[3:]
    stem = re.sub(r"\.(?:png|ktx|jpg|bc7|dds)$", "", t, flags=re.I)
    m = re.search(r"(\d{2,5})$", stem)
    if not m or int(m.group(1)) > MAX_FRAME_NO:
        return None
    return "ui/" + stem[: m.start()]


def seq_key(prefix: str) -> str:
    """产物文件名：可读短名 + 前缀哈希（确定性、不依赖文件系统顺序）。"""
    short = re.sub(r"[^0-9A-Za-z_.-]", "_", prefix.rsplit("/", 2)[-2].replace("/", "_"))
    short = short[-28:] or "seq"
    return f"{short}_{hashlib.sha256(prefix.encode()).hexdigest()[:8]}.webp"


def bbox_norm(im: Image.Image) -> np.ndarray:
    """按 alpha 内容框裁边后统一尺寸、铺到同一深色底，消除导出时缩放/裁边差异。"""
    bb = im.getbbox()
    work = im.crop(bb) if bb else im
    bg = Image.new("RGBA", work.size, (24, 24, 30, 255))
    bg.alpha_composite(work)
    return np.asarray(bg.convert("RGB").resize(NORM_SIZE, Image.LANCZOS), dtype=np.float32)


def content_metrics(frames: list[Image.Image]) -> dict:
    """邻帧差 / 突跳 / 首尾闭合，全部可复算。"""
    arrs = [bbox_norm(im) for im in frames]
    diffs = [float(np.abs(a - b).mean()) for a, b in zip(arrs, arrs[1:])]
    med = float(np.median(diffs)) if diffs else 999.0
    mx = max(diffs) if diffs else 999.0
    closing = float(np.abs(arrs[-1] - arrs[0]).mean()) if len(arrs) > 1 else 999.0
    limit = OUTLIER_K * med + OUTLIER_B
    return {"n": len(frames), "median": med, "max": mx, "closing": closing,
            "limit": limit, "jumps": sum(1 for d in diffs if d > limit)}


def smooth_ok(m: dict) -> bool:
    """循环判据：帧间整体相近 + 首尾闭合 + 无大面积突变。

    ★ 不要求「零突跳」：真实循环动画里有短暂的爆闪/快速位移（如 long1 龙身挥动、
      jiamianqishi 间歇光效），只要首尾能回到起点就说明是同一条序列，不是把不同
      底图拼在一起。突跳占比超过 1/4 才判为混帧。
    """
    return (m["n"] >= 2 and 0.05 < m["median"] <= SMOOTH_MEDIAN_MAX
            and m["closing"] <= OUTLIER_K * m["median"] + OUTLIER_B
            and m["jumps"] <= max(1, int(m["n"] * 0.25)))


def identity_diff(frame0: Image.Image, dyn_png: str) -> float:
    """首帧 vs 该卡已导出的静态底图（无静态底图时返回 None 语义由调用方处理）。"""
    p = WEB / dyn_png
    if not dyn_png or not p.is_file():
        return None
    return float(np.abs(bbox_norm(frame0) - bbox_norm(Image.open(p).convert("RGBA"))).mean())


def collect_plan(board: dict, con: sqlite3.Connection) -> dict[str, list[tuple[str, str, int]]]:
    """序列前缀 → [(贴图名, 包, 行)]，按帧号排序；同时记录用了哪些卡。"""
    plan: dict[str, list[tuple[str, str, int]]] = {}
    for it in board["items"]:
        pre = sequence_prefix(it.get("dyn_tex") or "")
        if not pre or pre in plan:
            continue
        rows = con.execute("select name,pack,row from rows where name like ?", (pre + "%",)).fetchall()
        hits = []
        for name, pack, row in rows:
            m = FRAME_RE.search(name)
            if not m or int(m.group(1)) > MAX_FRAME_NO:
                continue
            # 精确：前缀之后只剩帧号 + 扩展名（避免把别的变体纳入）
            if not re.fullmatch(re.escape(pre) + r"\d{2,5}\." + TEX_EXT_RE, name, re.I):
                continue
            hits.append((name, pack, row))
        if len(hits) >= MIN_SEQ_FRAMES:
            hits.sort(key=lambda x: (int(FRAME_RE.search(x[0]).group(1)), x[0]))
            plan[pre] = hits
    return plan


def sample(items: list, k: int) -> list:
    """等距抽样（含首尾），确定性。"""
    if len(items) <= k:
        return list(items)
    return [items[round(i * (len(items) - 1) / (k - 1))] for i in range(k)]


def decode_frames(plan: dict[str, list[tuple[str, str, int]]]) -> dict[str, dict[str, Image.Image]]:
    """按包一次扫描，解出全部候选帧；返回 {前缀: {贴图名: RGBA 图}}。"""
    wanted: dict[str, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
    owner: dict[str, str] = {}
    for pre, hits in plan.items():
        for name, pack, row in sample(hits, MAX_FRAMES):
            wanted[pack][row].add(name)
            owner[name] = pre
    decoded: dict[str, dict[str, Image.Image]] = defaultdict(dict)
    for pack, need in sorted(wanted.items()):
        fp = PE_PACKS / pack
        if not fp.is_file():
            print(f"  PE 包缺失，跳过: {pack}")
            continue
        try:
            entries = AG.iter_entries(str(fp))
        except Exception as exc:  # noqa: BLE001
            print(f"  PE 包读取失败: {pack} {type(exc).__name__} {exc}")
            continue
        for e in entries:
            row, data = e.get("row"), e.get("payload")
            names = need.get(row)
            if not names or not data:
                continue
            try:
                info = AG.parse_ktx(data)
                im = Image.fromarray(np.ascontiguousarray(AG._ktx_rgba(data, info))).convert("RGBA")
            except Exception:  # noqa: BLE001
                continue
            for name in names:
                decoded[owner[name]][name] = im.copy()
        print(f"  扫描 {pack}: 本包需要 {sum(len(v) for v in need.values())} 行")
    return decoded


def build_webp(frames: list[Image.Image], dst: Path) -> tuple[int, int]:
    """并集内容框裁边 → 统一缩放 → 循环 WebP。返回 (帧数, 每帧毫秒)。"""
    boxes = [im.getbbox() for im in frames]
    valid = [b for b in boxes if b]
    if valid:
        x0 = min(b[0] for b in valid); y0 = min(b[1] for b in valid)
        x1 = max(b[2] for b in valid); y1 = max(b[3] for b in valid)
        frames = [im.crop((x0, y0, x1, y1)) for im in frames]
    dom = frames[0].size
    canvas = (min(MAX_W, dom[0]), max(1, round(dom[1] * min(MAX_W, dom[0]) / dom[0])))
    seq = [im.resize(canvas, Image.LANCZOS) for im in frames]
    dur = frame_duration(len(seq))
    seq[0].save(dst, "WEBP", save_all=True, append_images=seq[1:],
                duration=dur, loop=0, quality=WEBP_QUALITY, method=4)
    return len(seq), dur


def anim_webp_ok(path: Path, dyn_png: str) -> tuple[bool, dict, float | None]:
    """校验既有 anim/<csb>.webp 是否可直接用（同一套内容判据）。"""
    im = Image.open(path)
    frames = []
    try:
        i = 0
        while True:
            im.seek(i); frames.append(im.convert("RGBA").copy()); i += 1
    except EOFError:
        pass
    if len(frames) < 3:
        return False, {"n": len(frames)}, None
    m = content_metrics(frames)
    ident = identity_diff(frames[0], dyn_png)
    ok = smooth_ok(m) and (ident is None or ident <= IDENTITY_MAX_DIFF)
    return ok, m, ident


def verify_artifacts(board: dict) -> int:
    """只读校验：引用文件齐全、≥2 帧、整轮 1200~2400ms、首帧与静态底图一致。"""
    from title_anim_pace import TARGET_CYCLE_MS, MAX_CYCLE_MS
    items = [it for it in board["items"] if it.get("dyn_webp")]
    bad = []
    for it in items:
        p = WEB / it["dyn_webp"]
        if not p.is_file():
            bad.append((it["id"], "文件缺失")); continue
        if "/pe/" in it["dyn_webp"]:
            bad.append((it["id"], "仍引用已停用的家族动画"))
        im = Image.open(p)
        fs = []
        try:
            i = 0
            while True:
                im.seek(i); fs.append(im.convert("RGBA").copy()); i += 1
        except EOFError:
            pass
        if len(fs) < 2:
            bad.append((it["id"], "非动画（单帧）"))
        cyc = sum(read_durations(p))
        if not (TARGET_CYCLE_MS <= cyc <= MAX_CYCLE_MS):
            bad.append((it["id"], f"整轮 {cyc}ms 越界"))
        if it.get("dyn_png") and (WEB / it["dyn_png"]).is_file():
            gap = identity_diff(fs[0], it["dyn_png"])
            if gap > VERIFY_IDENTITY_MAX_DIFF:
                bad.append((it["id"], f"首帧差 {gap:.1f}"))
    print(f"校验 {len(items)} 条循环动画，问题 {len(bad)} 条")
    for x in bad[:20]:
        print("  ", x)
    return 0 if not bad else 1


def main() -> int:
    apply = "--apply" in sys.argv
    verify = "--verify" in sys.argv
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    if verify:
        return verify_artifacts(board)
    items = board["items"]
    con = sqlite3.connect(f"file:{PE_DB.as_posix()}?mode=ro", uri=True)
    plan = collect_plan(board, con)
    con.close()
    print(f"候选项：{len(items)} 条，精确序列前缀 {len(plan)} 个（≥{MIN_SEQ_FRAMES} 帧）")

    # ── ① 精确序列：解码、校验、生成 ───────────────────────────────
    decoded = decode_frames(plan)
    seq_map: dict[str, dict] = {}       # prefix -> 产物信息
    seq_reason: dict[str, str] = {}
    for pre, hits in sorted(plan.items()):
        picked = sample(hits, MAX_FRAMES)
        got = decoded.get(pre, {})
        frames = [got[n] for n, _p, _r in picked if n in got]
        if len(frames) < MIN_SEQ_FRAMES:
            seq_reason[pre] = f"解码不足 {len(frames)}/{len(picked)}"
            continue
        if len({f.size for f in frames}) != 1:
            seq_reason[pre] = "帧尺寸不一致（疑似叠加层）"
            continue
        m = content_metrics(frames)
        users = [it for it in items if sequence_prefix(it.get("dyn_tex") or "") == pre]
        ident = [identity_diff(frames[0], it.get("dyn_png") or "") for it in users]
        ident = [x for x in ident if x is not None]
        ident_max = max(ident) if ident else None
        if ident_max is not None and ident_max > IDENTITY_MAX_DIFF:
            seq_reason[pre] = f"首帧与静态底图不符 {ident_max:.1f}>{IDENTITY_MAX_DIFF}"
            continue
        if not smooth_ok(m):
            seq_reason[pre] = (f"不平滑 med={m['median']:.1f} max={m['max']:.1f} "
                               f"closing={m['closing']:.1f} limit={m['limit']:.1f} jumps={m['jumps']}")
            continue
        rel = "assets/title_dyn/seq/" + seq_key(pre)
        seq_map[pre] = {"rel": rel, "path": WEB / rel, "frames": frames,
                        "n": len(frames), "users": [it["id"] for it in users], "metrics": m}
        print(f"  PASS {pre}: {len(picked)} 帧 → {len(frames)} 帧, med={m['median']:.1f} "
              f"closing={m['closing']:.1f}, 引用 {len(users)} 条")
    for pre, why in sorted(seq_reason.items()):
        print(f"  SKIP {pre}: {why}")

    # ── ② 生成 / 复算产物 ─────────────────────────────────────────
    if apply:
        SEQ_DIR.mkdir(parents=True, exist_ok=True)
    made = {}
    for pre, info in sorted(seq_map.items()):
        dst = info["path"]
        if apply:
            n, dur = build_webp(info["frames"], dst)
        else:
            n, dur = info["n"], frame_duration(info["n"])
        made[pre] = {"rel": info["rel"], "n": n, "dur": dur}
        if verify and not dst.is_file():
            print(f"  VERIFY 缺文件 {dst.name}")
    # 清理本脚本产出的、但已不再被任何序列引用的旧 seq/*.webp（幂等）
    if apply:
        keep = {Path(v["rel"]).name for v in made.values()}
        for old in SEQ_DIR.glob("*.webp"):
            if old.name not in keep:
                old.unlink()
                print(f"  清理失效产物 {old.name}")

    # ── ③ 回填：精确序列 > 合法 csb 动画 > 静态首帧 ────────────────
    stats = defaultdict(int)
    for it in items:
        for k in ("dyn_webp", "dyn_webp_source", "dyn_anim_frames", "dyn_anim_ms", "dyn_seq"):
            it.pop(k, None)
        pre = sequence_prefix(it.get("dyn_tex") or "")
        hit = made.get(pre)
        if hit:
            it["dyn_webp"] = hit["rel"]
            it["dyn_seq"] = pre
            it["dyn_webp_source"] = "PE 精确帧序列（csb 引用贴图同名同前缀，内容校验通过）"
            it["dyn_anim_frames"] = hit["n"]
            it["dyn_anim_ms"] = hit["dur"]
            stats["精确序列"] += 1
            continue
        csb = str(it.get("anim_csb") or "").replace("\\", "/").rsplit("/", 1)[-1]
        if csb.endswith(".csb"):
            csb = csb[:-4]
        p = ANIM_DIR / (csb + ".webp")
        if p.is_file():
            ok, _m, _ident = anim_webp_ok(p, it.get("dyn_png") or "")
            if ok:
                it["dyn_webp"] = "assets/title_dyn/anim/" + p.name
                it["dyn_webp_source"] = "csb 帧序列（原导出器，内容校验通过）"
                ds = read_durations(p)
                it["dyn_anim_frames"] = len(ds)
                it["dyn_anim_ms"] = int(round(sum(ds) / len(ds))) if ds else 0
                stats["csb 动画"] += 1
                continue
        stats["仅静态首帧" if it.get("dyn_png") else "无资源"] += 1

    dyn_items = [it for it in items if "动态" in (it.get("flags") or [])]
    dyn_all = len(dyn_items)
    dyn_anim = sum(1 for it in dyn_items if it.get("dyn_webp"))
    still = sum(1 for it in dyn_items if not it.get("dyn_webp") and it.get("dyn_png"))
    none = sum(1 for it in dyn_items if not it.get("dyn_webp") and not it.get("dyn_png"))
    seq_used = sum(1 for it in dyn_items if it.get("dyn_seq"))
    csb_used = sum(1 for it in dyn_items if it.get("dyn_webp") and not it.get("dyn_seq"))
    print(f"\n动态条目 {dyn_all}，挂上循环动画 {dyn_anim}"
          f"（精确序列 {seq_used} + csb 动画 {csb_used}），仅静态首帧 {still}，底图未导出 {none}")

    labels = board["meta"].setdefault("field_labels", {})
    labels.update({"dyn_webp": "动态动画（逐帧合成）", "dyn_webp_source": "动态动画来源口径",
                   "dyn_anim_frames": "动画实际帧数", "dyn_anim_ms": "每帧时长（毫秒）",
                   "dyn_seq": "动画帧序列前缀（PE 索引路径）"})
    NOTE = ("动态底图按 item.dyn_tex 的精确帧序列前缀从 PE 索引取帧，"
            f"经同尺寸/首帧一致(≤{IDENTITY_MAX_DIFF:g})/邻帧平滑/首尾闭合四项校验后合成循环 WebP；"
            "旧按家族拼帧会把不同变体底图轮流播放，已停用；未通过校验的条目只显示静态首帧，不伪造动画")
    append_note(board, NOTE)
    # 板级技术详情里那句旧计数同步重算（口径由产物自身推得，不手填）
    for src in (board["meta"].get("tech_sources") or []):
        if isinstance(src, dict) and "称号美术字" in str(src.get("name") or ""):
            src["detail"] = (f"首帧 {sum(1 for it in items if it.get('dyn_png'))} 条、"
                             f"循环动画 {dyn_anim} 条（精确序列 {stats['精确序列']} / "
                             f"csb 动画 {stats['csb 动画']}）。"
                             "序列取自 PE 包内 csb 引用贴图的同名帧号，首帧与静态底图逐条校验；"
                             "未通过者只显示静态首帧。定位来源：PC 测试服容器 + PE 包；"
                             "PE 包内没有对应 csb 贴图的条目只能取 PC 测试服，非正式服。")

    if apply:
        write_board_pair(BOARD, board, "title_catalog")
        print(f"已写盘：{BOARD.name} / .js；WebP {len(made)} 个 → {SEQ_DIR}")
    else:
        print("dry-run，未写盘（加 --apply 落盘）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
