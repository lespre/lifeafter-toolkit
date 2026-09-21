# -*- coding: utf-8 -*-
"""匿名 GPK 纹理提取 / 未上线新内容筛选器（2026-08-31 第一项攻坚固化，只读源）。

为什么需要它
------------
皮肤专属 PBR 贴图（.tga 源）在打包后进入**匿名 gpk**（如 weapon.gpk），条目
只有 c1/c2 内容指纹、没有路径 fid，无法用逻辑路径直接定位（已 6 路证伪路径反推）。
本模块用两条已验证的判据绕开匿名墙，把"找某类皮肤贴图"变成可重复流程：

1. **版本独有判据**：匿名条目 c1/c2 去桥全量 fpk/npk 索引，桥不到 fid 的就是
   本版独有新内容（weapon.gpk 实测 4948 dds -> 仅 324 张独有，6.5%）。
2. **颜色特征筛选**：解码 BCn 主 mip，按 HSV/RGB 规则打分（默认"金色"用于
   铠甲勇士联动这类金武器），多进程排序后出候选 PNG + 联系表，再人工/多模态确认。

依赖：texture2ddecoder、Pillow、numpy；索引能力来自 resource_resolver。

CLI:
  python -m toolkit_core.texture_extractor scan <已解包gpk目录> --res E:\\mrzh\\res \
      --out 输出目录 --color gold --only-unique --sheet
"""
from __future__ import annotations
import argparse, json, os, struct
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np


# ----------------------------------------------------------------------
# 单张 DDS 解码（放在模块顶层，便于多进程序列化）
# ----------------------------------------------------------------------
def decode_dds_file(path: str | Path):
    """读一个解包出来的 .dds，返回 (PIL.Image 主mip, (w,h,fourcc)) 或 None。"""
    from toolkit_core.resource_resolver import decode_bcn_dds
    data = Path(path).read_bytes()
    im = decode_bcn_dds(data)
    if im is None:
        return None
    four = data[84:88].decode("latin1", "replace")
    return im, (im.size[0], im.size[1], four)


# ----------------------------------------------------------------------
# 颜色评分
# ----------------------------------------------------------------------
def _gold_mask(R, G, B, mx, mn):
    """金色：R>G>B、红蓝差明显、较亮、有彩色度（非灰白）。"""
    return (R > G) & (G > B) & (R - B > 0.20) & (R > 0.45) & (mx - mn > 0.15) & (G > 0.30)


_COLOR_RULES = {"gold": _gold_mask}


def color_score(im, rule: str = "gold", thumb: int = 128):
    """对 PIL 图算指定颜色占比（缩到 thumb 加速），返回 0~1；透明像素不计。"""
    s = im.convert("RGBA"); s.thumbnail((thumb, thumb))
    a = np.asarray(s, dtype=np.float32) / 255.0
    al = a[..., 3]
    m = al > 0.3
    if m.sum() < 30:
        return 0.0
    R, G, B = a[..., 0][m], a[..., 1][m], a[..., 2][m]
    mx = np.maximum(np.maximum(R, G), B); mn = np.minimum(np.minimum(R, G), B)
    fn = _COLOR_RULES.get(rule, _gold_mask)
    return float(fn(R, G, B, mx, mn).mean())


def _worker(args):
    path, rule = args
    try:
        r = decode_dds_file(path)
        if r is None:
            return None
        im, meta = r
        return Path(path).stem, color_score(im, rule), meta
    except Exception:
        return None


def smart_workers(cap: float = 0.8, keep: int = 2):
    """智能进程数：逻辑核 *cap，且至少留 keep 核；检测到高负载再减半。"""
    cpu = os.cpu_count() or 8
    w = max(1, min(int(cpu * cap), cpu - keep))
    load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0
    if load > cpu * 0.6:
        w = max(1, w // 2)
    return w


# ----------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------
def scan_dir(unpacked_dir, out_dir, res_dir=None, rule: str = "gold",
             only_unique: bool = True, min_side: int = 0, make_sheet: bool = True,
             top: int = 60, workers: int | None = None):
    """扫描一个已解包 gpk 目录（含 manifest.json），输出颜色候选。

    Parameters
    ----------
    unpacked_dir : 解包目录（平铺 *.dds + manifest.json，entries 含 crc1/crc2）
    out_dir      : 候选 PNG / 评分 json / 联系表输出目录
    res_dir      : 游戏 res 目录；给了且 only_unique 时先按 c1c2 独有判据过滤
    rule         : 颜色规则（目前 gold）
    only_unique  : 只保留 bridge 不到全量索引的独有条目（未上线候选）
    min_side     : 仅处理宽/高 >= 该值的纹理（0 不限）
    """
    unpacked_dir = Path(unpacked_dir); out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    man_p = next(unpacked_dir.glob("*.json"))
    man = json.loads(man_p.read_text(encoding="utf-8"))
    entries = man["entries"] if isinstance(man, dict) and "entries" in man else man

    allow = None
    if only_unique:
        if res_dir is None:
            raise ValueError("only_unique=True 需要 res_dir 建索引")
        from toolkit_core.resource_resolver import ResourceResolver
        r = ResourceResolver(res_dir).build_index()
        allow = set()
        for e in entries:
            if e.get("ext") != ".dds":
                continue
            if r._cc_to_fid.get(f"{e['crc1']:08x}/{e['crc2']:08x}") is None:
                allow.add(e["idx"])
        print(f"[独有判据] {sum(1 for e in entries if e.get('ext')=='.dds')} dds "
              f"-> 独有 {len(allow)}")

    tasks = []
    for e in entries:
        if e.get("ext") != ".dds":
            continue
        idx = e["idx"]
        if allow is not None and idx not in allow:
            continue
        p = unpacked_dir / f"{idx:06d}.dds"
        if p.exists():
            tasks.append((str(p), rule))
    workers = workers or smart_workers()
    print(f"[解码] {len(tasks)} 张，{workers} 进程")
    rows, done = [], 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker, t) for t in tasks]
        for fu in as_completed(futs):
            r = fu.result(); done += 1
            if r:
                stem, score, meta = r
                if meta[0] >= min_side and meta[1] >= min_side:
                    rows.append({"stem": stem, "score": round(score, 4),
                                 "w": meta[0], "h": meta[1], "fourcc": meta[2]})
    rows.sort(key=lambda x: -x["score"])
    (out_dir.parent / f"{unpacked_dir.name}_{rule}_评分.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    # 导出 Top PNG
    for old in out_dir.glob("*.png"):
        old.unlink()
    for row in rows[:top]:
        src = unpacked_dir / f"{int(row['stem']):06d}.dds"
        r = decode_dds_file(src)
        if r:
            r[0].save(out_dir / f"{row['stem']}_{row['w']}x{row['h']}_{rule}{row['score']:.2f}.png")
    if make_sheet:
        _contact_sheet(rows[:top], unpacked_dir, out_dir, rule)
    print(f"[完成] 有效 {len(rows)}，Top{min(top,len(rows))} -> {out_dir}")
    return rows


def _contact_sheet(rows, unpacked_dir, out_dir, rule, cell=260, cols=6):
    from PIL import Image, ImageDraw
    pages = [(rows[i:i + 30]) for i in range(0, len(rows), 30)]
    for pi, chunk in enumerate(pages):
        rn = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cell, rn * cell), (25, 25, 25))
        dr = ImageDraw.Draw(sheet)
        for k, row in enumerate(chunk):
            p = unpacked_dir / f"{int(row['stem']):06d}.dds"
            r = decode_dds_file(p)
            if not r:
                continue
            im = r[0].convert("RGBA"); im.thumbnail((cell - 10, cell - 28))
            x, y = (k % cols) * cell, (k // cols) * cell
            sheet.paste(im, (x + 5, y + 24), im)
            dr.text((x + 5, y + 5),
                    f"{row['stem']} {rule}{row['score']:.2f} {row['w']}", fill=(0, 255, 120))
        sheet.save(out_dir.parent / f"{out_dir.name}_联系表{pi + 1}.png")


def _main():
    ap = argparse.ArgumentParser(description="匿名GPK纹理颜色筛选/未上线候选")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("unpacked_dir")
    s.add_argument("--res", default=r"E:\mrzh\res")
    s.add_argument("--out", required=True)
    s.add_argument("--color", default="gold")
    s.add_argument("--all", action="store_true", help="不只看独有（默认只看独有）")
    s.add_argument("--min-side", type=int, default=0)
    s.add_argument("--top", type=int, default=60)
    a = ap.parse_args()
    if a.cmd == "scan":
        scan_dir(a.unpacked_dir, a.out, a.res, a.color,
                 only_unique=not a.all, min_side=a.min_side, top=a.top)


if __name__ == "__main__":
    _main()
