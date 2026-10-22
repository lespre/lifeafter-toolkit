# -*- coding: utf-8 -*-
r"""按【像素内容】判贴图性质 —— 别再靠形状/尺寸猜「人眼能不能看懂」。

## 为什么需要（2026-10-17 实测）

`hotfix_bundle.classify_image()` 原来只有两路判据：名字关键词、形状尺寸。
于是**法线图**（非方形、短边≥256）被判成「能看的图/立绘大图」——
本批抽看 5 张全是法线图集、灰度掩码、渐变色带，没有一张是立绘。
用户口径：「视觉产出要看得懂的图」，把法线图当立绘交出去就是错。

## 判据（都只用降采样后的像素统计，不看文件大小/尺寸）

| 类别 | 依据 | 说明 |
|---|---|---|
| `normal`（法线图） | 蓝通道显著高于红绿（`b > r+20 且 b > g+20` 的像素占多数）且 r≈g | 法线贴图把法线编码进 RGB，典型 (128,128,255) 系 |
| `mask`（掩码/通道图） | 低彩度（max-min 小）+ 明度跨度大 | 灰度掩码、粗糙度/金属度图 |
| `ramp`（渐变色带） | 低彩度或单方向渐变，行/列方差比极端 | 颜色查找表、粒子色带 |
| `color`（彩色图） | 彩度充足且分布散 | 立绘/界面/图标才可能是这类 |
| `unknown` | 以上都不像 | 老实说不认识 |

`viewable()` = 只有 `color` 才算「人眼能看懂」（且彩度均值达阈值）。
"""
from __future__ import annotations

from pathlib import Path

__all__ = ["stats_of", "kind_of", "viewable", "classify_bytes", "classify_file"]

DOWN = 64                     # 降采样到 64×64 就够判性质


def _render_dir() -> Path:
    """皮肤链与渲染目录（DDS 解码器所在）—— 不在 00_共享核心 下，需要按需挂 sys.path。"""
    return Path(__file__).resolve().parents[2] / "02_图文音频渲染" / "皮肤链与渲染"


def _rgba_of(data: bytes, name: str = ""):
    """把 DDS/PNG/JPG/TGA 解成 (w,h,像素列表[(r,g,b,a)])；解不出返回 None。"""
    ext = Path(name).suffix.lower()
    if ext == ".dds" or data[:4] == b"DDS ":
        try:
            import sys
            d = str(_render_dir())
            if d not in sys.path:
                sys.path.insert(0, d)
            from dds_rgba_canonical import decode_dds_rgba_u8   # noqa
            img = decode_dds_rgba_u8(data)
        except Exception:                                       # noqa: BLE001
            return None
        if img is None:
            return None
        try:
            return _pil_pixels(img)
        except Exception:                                       # noqa: BLE001
            return None
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        im.load()
        return _pil_pixels(im)
    except Exception:                                           # noqa: BLE001
        return None


def _pil_pixels(img):
    """PIL 图 → (w,h,[(r,g,b,a)])；统一转 RGBA 再降采样。"""
    from PIL import Image
    if not hasattr(img, "mode"):
        # 已是 numpy (h,w,4)
        return _np_pixels(img)
    im = img.convert("RGBA")
    im.thumbnail((DOWN, DOWN))
    return im.width, im.height, list(im.getdata())


def _np_pixels(arr):
    import numpy as np
    a = np.asarray(arr)
    if a.ndim == 2:
        a = np.dstack([a] * 3 + [np.full_like(a, 255)])
    if a.shape[-1] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, a.dtype)])
    h, w = a.shape[:2]
    step = max(1, max(h, w) // DOWN)
    a = a[::step, ::step]
    return a.shape[1], a.shape[0], [tuple(int(x) for x in p[:4]) for p in a.reshape(-1, 4)]


def classify_bytes(data: bytes, name: str = "") -> dict:
    """→ {kind, viewable, stats}；解不出图时 kind 为 None。

    kind ∈ {normal, mask, ramp, color, unknown}
    """
    got = _rgba_of(data, name)
    if not got:
        return {"kind": None, "viewable": False, "stats": {}}
    return classify_pixels(*got)


def classify_pixels(w: int, h: int, px) -> dict:
    n = len(px)
    if not n:
        return {"kind": "unknown", "viewable": False, "stats": {}}
    # ★ 透明背景比例：立绘 / 界面图 / 图标普遍带透明底；材质贴图集几乎全不透明。
    #   这是「能看懂」最硬的一条正证据（低层统计判不出「画的是什么」，但判得出这个）。
    alpha_ratio = sum(1 for p in px if len(p) > 3 and p[3] < 250) / n
    opaque = [p for p in px if len(p) < 4 or p[3] > 8] or px
    m = len(opaque)
    # ★ 2026-10-17 修正：统计要**剔掉背景**再算 —— 实测黑底渲染海报（武器悬空 + 注释文字）
    #   整张图 95% 是近黑像素，按全图算会把「正经海报」判成「灰度掩码」。
    #   主体 = 亮度落在 (20, 245) 的像素（排除纯黑背景与纯白底），背景占比单独记。
    subject = [p for p in opaque if 20 < (0.299 * p[0] + 0.587 * int(p[1]) + 0.114 * int(p[2])) < 245]
    st_subject_ratio = len(subject) / max(1, len(opaque))
    base = subject or opaque
    mb = len(base)
    chroma = 0.0
    bluish = 0
    grayish = 0
    bluehue = 0
    lum_sum = 0.0
    for p in base:
        r, g, b = p[0], int(p[1]), int(p[2])
        mx, mn = max(r, g, b), min(r, g, b)
        chroma += mx - mn
        lum_sum += 0.299 * r + 0.587 * g + 0.114 * b
        if b > r + 20 and b > g + 20:
            bluish += 1
        if mx - mn <= 10:
            grayish += 1
        elif _hue_in(r, g, b, 180, 320):        # 蓝→紫→洋红：法线图的典型调色板
            bluehue += 1
    chroma /= mb
    st = {"w": w, "h": h, "pixels": n, "opaque_ratio": round(m / n, 3),
          "alpha_ratio": round(alpha_ratio, 3),
          "subject_ratio": round(st_subject_ratio, 3),
          "chroma": round(chroma, 1), "bluish": round(bluish / mb, 3),
          "bluehue": round(bluehue / mb, 3),
          "grayish": round(grayish / mb, 3), "lum": round(lum_sum / mb, 1)}

    # 法线图：① 蓝占绝对多数且红绿接近（标准 (128,128,255) 编码）；
    #        ② 或调色板集中在蓝紫洋红段（**紫调法线图**实测漏过 —— b>r+20 太窄）。
    rg_close = _rg_close_ratio(base)
    st["rg_close"] = round(rg_close, 3)
    # ★ 阈值按样本量出来的（见 references/素材分类阈值.md）：
    #   真法线 bluish 0.69~1.0 / bluehue 0.99~1.0；渲染海报 bluish ≤0.024 / bluehue ≤0.55。
    #   ⇒ 蓝调路径 bluish≥0.5；紫调路径 bluehue 收到 0.85（0.55 会把蓝色武器渲染误判）
    if (st["bluish"] >= 0.5 and rg_close >= 0.5) or \
            (st["bluehue"] >= 0.85 and st["grayish"] < 0.35):
        return {"kind": "normal", "viewable": False, "stats": st}
    # 掩码/通道图：几乎无彩度
    if st["grayish"] >= 0.7:
        return {"kind": "mask", "viewable": False, "stats": st}
    # 渐变色带：彩度中等但**行内方差远大于行间**（单方向渐变）
    if st["chroma"] >= 8 and _directional(px, w, h):
        return {"kind": "ramp", "viewable": False, "stats": st}
    if st["chroma"] >= 18:
        # ★ 彩色还不够 —— 彩色**平铺贴图集**同样「看不懂」（实测一批方块图集彩度很高）。
        #   判据：列/行均值曲线存在强周期性（同一图案横向/纵向重复）⇒ 图集/纹理，不是立绘。
        if _periodic(px, w, h):
            return {"kind": "atlas", "viewable": False, "stats": st}
        # ★ 最后一道：**透明底**（记录但**不作为判据** —— 实测 DXT5 的 alpha 常被当
        #   遮罩/高光通道，材质贴图的 alpha 也会铺满，据此断言「能看懂」会错）。
        #   ⇒ 「能看懂」不由低层统计断言：材质类一律进「看不懂的」，其余进「未判（需人看）」。
        return {"kind": "color", "viewable": False, "stats": st}
    return {"kind": "unknown", "viewable": False, "stats": st}


def _periodic(px, w: int, h: int) -> bool:
    """平铺/图集判据：降采样后的列（或行）亮度曲线**真的在重复**。

    ★ 2026-10-17 两处修正（都是实测踩出来的）：
      ① 曲线必须有足够对比度（std ≥ 6）—— 黑底渲染图整条曲线几乎平，自相关天然接近 1，
         按老写法会被判成「平铺」（11 张正经海报里 9 张中招）。
      ② 要求**多周期**成立：lag=L 有相关，2L 也得有（真平铺才会在倍数上继续相关）。
    """
    if w < 16 or h < 16 or len(px) < w * h:
        return False

    def profile(seq_groups):
        out = []
        for g in seq_groups:
            out.append(sum(0.299 * p[0] + 0.587 * int(p[1]) + 0.114 * int(p[2]) for p in g) / max(1, len(g)))
        return out

    rows = [px[y * w:(y + 1) * w] for y in range(h)]
    cols = list(zip(*rows))

    def axis_periodic(curve) -> bool:
        n = len(curve)
        mu = sum(curve) / n
        var = sum((v - mu) ** 2 for v in curve) / n
        if var ** 0.5 < 6:                      # ① 对比度不够 → 不算
            return False

        def corr(lag: int) -> float:
            if lag <= 0 or lag >= n:
                return 0.0
            num = sum((curve[i] - mu) * (curve[i + lag] - mu) for i in range(n - lag))
            den = var * (n - lag)
            return num / den if den else 0.0

        for lag in range(4, n // 2 + 1):
            if corr(lag) >= 0.6 and (2 * lag >= n or corr(2 * lag) >= 0.4):   # ② 多周期
                return True
        return False

    # ③ 要**两个方向都周期性**才算图集（真正的网格平铺）——
    #    只在一个方向「像重复」的多半是黑底 + 一个主体的渲染图（实测 6/11 张海报中招）。
    return axis_periodic(profile(rows)) and axis_periodic(profile(cols))


def _hue_in(r: int, g: int, b: int, lo: float, hi: float) -> bool:
    """RGB → 色相角（0..360），判断是否落在 [lo, hi) 区间。"""
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return False
    if mx == r:
        h = 60.0 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60.0 * ((b - r) / d + 2)
    else:
        h = 60.0 * ((r - g) / d + 4)
    return lo <= h < hi


def _rg_close_ratio(px) -> float:
    """红绿接近的像素占比（法线图 R/G 都在 128 附近）。"""
    if not px:
        return 0.0
    c = sum(1 for p in px if abs(int(p[0]) - int(p[1])) <= 12)
    return c / len(px)


def _directional(px, w: int, h: int) -> bool:
    """单方向渐变判据：按行/列分组后，组内方差 ≪ 组间方差。"""
    if w < 4 or h < 4 or len(px) < w * h:
        return False
    rows = [px[y * w:(y + 1) * w] for y in range(h)]
    cols = list(zip(*[rows[y] for y in range(h)]))

    def var(seq):
        vals = [0.299 * p[0] + 0.587 * int(p[1]) + 0.114 * int(p[2]) for p in seq]
        if not vals:
            return 0.0
        mu = sum(vals) / len(vals)
        return sum((v - mu) ** 2 for v in vals) / len(vals)

    def spread(groups):
        means = [sum(0.299 * g[0] + 0.587 * int(g[1]) + 0.114 * int(g[2]) for g in grp) / max(1, len(grp))
                 for grp in groups]
        mu = sum(means) / max(1, len(means))
        return sum((x - mu) ** 2 for x in means) / max(1, len(means))

    in_row = sum(var(r) for r in rows) / len(rows)
    in_col = sum(var(c) for c in cols) / len(cols)
    betw_row, betw_col = spread(rows), spread(cols)
    # 行内一致 + 行间变化大 ⇒ 竖直方向渐变（同理列）
    return (in_row < 4 and betw_row > 40) or (in_col < 4 and betw_col > 40)


def kind_of(stats: dict) -> str:
    """从已算好的 stats 直接出类别（供批量脚本复用）。"""
    return _kind_from_stats(stats or {})


def _kind_from_stats(st: dict) -> str:
    if (st.get("bluish", 0) >= 0.5 and st.get("rg_close", 0) >= 0.5) or \
            (st.get("bluehue", 0) >= 0.85 and (st.get("grayish") or 0) < 0.35):
        return "normal"
    if st.get("grayish", 0) >= 0.7:
        return "mask"
    chroma = st.get("chroma") or 0
    if chroma >= 18:
        return "color"
    if chroma >= 8:
        return "ramp"
    return "unknown"


#: 判定为「素材/材质」的种类 —— 一律进「看不懂的」，且**不需要人再看**。
MATERIAL_KINDS = ("normal", "mask", "ramp", "atlas")


def viewable(stats: dict) -> bool:
    """★ 一律 False —— 「人眼能不能看懂」**不由低层统计断言**（2026-10-17 实测修正）。

    为什么不留一个 True：彩度、尺寸、形状、alpha 四条都被实测证伪过 ——
    彩色平铺贴图集彩度 190+、DXT5 的 alpha 铺满整张材质图。
    能可靠判的只有**否定式**：法线图 / 灰度掩码 / 色带 / 平铺图集 = 材质。
    其余归「未判（需人看）」，交给人工或视觉模型，别用启发式冒充。
    """
    return False


def is_material(stats: dict) -> bool:
    """可靠判据：是材质类贴图（法线/掩码/色带/平铺）⇒ 可以直接归「看不懂的」。

    ★ 注意：`stats` 里没有周期性信息（`_periodic` 只看像素），所以**平铺图集判不出来**；
      要用完整体验就用 `is_material_kind(classify_file(p)["kind"])`。
    """
    return _kind_from_stats(stats) in MATERIAL_KINDS


def is_material_kind(kind: str | None) -> bool:
    """从 `classify_*()` 给出的 kind 直接判（含 atlas，推荐）。"""
    return kind in MATERIAL_KINDS


def classify_file(path) -> dict:
    p = Path(path)
    try:
        return classify_bytes(p.read_bytes(), p.name)
    except OSError:
        return {"kind": None, "viewable": False, "stats": {}}
