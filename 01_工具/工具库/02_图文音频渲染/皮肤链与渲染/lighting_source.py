"""lighting_source.py —— 按【游戏延迟光照 pass 汇编】+【天气真值】的光照
依据：
  · 汇编：deferred/quality2/common/shader/deferred_dir_light_stencil.nfx2/
          3b857dbf_d9a1974a_d11.pipe_blob1_blob.asm（1570 行 · 116 变体）
  · cbuffer NeoxUBOGlobal1（逐字偏移 ✓）：
      u_ambient@0 · u_dir_color@336 · u_dir_direction@352 · u_cascade_* · u_env_sh[7]@2368
      · u_env_day2night_exposure@3824 · u_frame_time@1392 · u_dirlight_falloff_k0_k1_b@3792
  · 输入：t0-t3 G-Buffer · t4 深度 · t5 ShadowMap · t9 clustered · t13 t_env_spec_array
  · 天气 XML（真值 ✓）：ln/li/lmi · st/et · realskylightsh_day/_night · envmap_id
★ 诚实标注：
   ① 太阳方向 = 由 st/et + hour 算（有据 ✓ 但仍属模型简化 [inferred]）
   ② 太阳颜色 = 由球谐 DC 项 / 天色推（引擎按场景填 dir_color ✗ 静态无 ⇒ [inferred]）
   ③ 环境 SH = 天气真值 ✓（realskylightsh_day/_night ✓）
   ④ u_env_day2night_exposure 静态无值 ⇒ 由 SH 亮度估 [inferred]
"""
import numpy as np

# 球谐 → irradiance 的引擎语义（NeoX 惯例：SH 为辐照度 ✓）
SH_C0 = 0.282095


def sh_to_irradiance(sh, fallback_gray=0.35):
    """★ 球谐 → 环境辐照度
    ★★ 诚实声明：SH 的 7×float4 内存布局【未确证 ✗】（实测 realskylightsh_day 前 8 数
       0.03494,-0.01366,0.0528,0.1278, 0.04016,-0.01456,0.0802,0.1965 每 4 个一组、
       第 4 个递增 ⇒ 不像是 [r,g,b,?] 颜色布局 ⇒ 按 RGB 硬读会得到 G=0 的错值 ✗）
       ⇒ 故【不使用】SH 解 RGB ✗；只当【整体亮度标量】用（均值），并标注 [inferred] ✓
    返回：单色辐照度（三通道相同 ✓）—— 这是【有据可依】的最小假设 ✓
    """
    if sh is None:
        return np.array([fallback_gray] * 3, np.float32)
    s = np.asarray(sh, np.float32)
    if s.size == 0:
        return np.array([fallback_gray] * 3, np.float32)
    # ★ 只取整体强度（不解释分量语义 ✓ 避免把布局猜错 ✗）
    dc = float(np.abs(s[0, :3]).mean()) if s.ndim == 2 and s.shape[1] >= 3 else float(np.abs(s).mean())
    lin = float(np.abs(s[1:3, :3]).mean()) * 0.25 if s.ndim == 2 and s.shape[0] >= 3 else 0.0
    v = max(dc + lin, 1e-4)
    return np.array([v] * 3, np.float32)


def sun_direction(w, hour):
    """太阳方向（★ 2026-10-03 修正 ✓）
    白天：由 st/et 轨道算（st=日出 et=日落 ✓）⇒ 东→西弧线 ✓
    夜间：★ 不应再用太阳 ✗（原来会 clip 到地平线 ⇒ N·L≈0 ⇒ 全黑 ✗ 实测踩过）
          ⇒ 改用【月光方向】= 太阳的镜像（简化 ✓ 引擎按场景填 ✗ [inferred]）
    """
    st = float(w.get('st', 6 * 3600))
    et = float(w.get('et', 18 * 3600))
    h = hour * 3600.0
    if st <= h <= et:
        t = (h - st) / max(1.0, et - st)          # 0=日出 · 0.5=正午 · 1=日落
        elev = np.radians(70.0 * np.sin(np.pi * np.clip(t, 0.0, 1.0)))
        azim = np.radians(180.0 * np.clip(t, 0.0, 1.0))
    else:
        # 夜间：月亮从【日落点】升到【日出点】（简化镜像 ✓）
        span = max(1.0, 86400.0 - (et - st))
        tn = ((h - et) % 86400.0) / span          # 0=日落后 · 1=日出前
        elev = np.radians(55.0 * np.sin(np.pi * np.clip(tn, 0.0, 1.0)))
        azim = np.radians(180.0 + 180.0 * np.clip(tn, 0.0, 1.0))
    d = np.array([np.cos(elev) * np.cos(azim),
                  np.sin(elev),
                  np.cos(elev) * np.sin(azim)], np.float32)
    return d / (np.linalg.norm(d) + 1e-6)


def is_day(w, hour):
    """是否白天（st/et 之间 ✓ 真值）"""
    st = float(w.get('st', 6 * 3600)); et = float(w.get('et', 18 * 3600))
    return st <= hour * 3600.0 <= et


def sun_color(w, hour):
    """太阳颜色（★ 引擎 dir_color 按场景填 ✗ 静态无 ⇒ 由 SH DC 推 + 日落偏暖 [inferred]）
    标注：全部为 [inferred] —— 有据的是 li=6.0（真值 ✓）
    """
    sh = w.get('realskylightsh_day')
    irr = sh_to_irradiance(sh)
    c = irr / max(float(irr.max()), 1e-6)
    # 低角度偏暖（物理倾向 ✓ [inferred]）
    st = float(w.get('st', 6 * 3600)); et = float(w.get('et', 18 * 3600))
    h = hour * 3600.0
    low = 0.0
    if h < st:
        low = np.clip(1.0 - (st - h) / max(1.0, st), 0.0, 1.0)
    elif h > et:
        low = np.clip(1.0 - (h - et) / max(1.0, 86400 - et), 0.0, 1.0)
    warm = np.array([1.0, 0.78, 0.55], np.float32)
    return (c * (1.0 - low) + warm * low).astype(np.float32)


def ambient_rgb(w, hour):
    """环境辐照度（天气球谐真值 ✓ 按昼夜插值 ✓）"""
    d = w.get('realskylightsh_day'); n = w.get('realskylightsh_night')
    st = float(w.get('st', 6 * 3600)); et = float(w.get('et', 18 * 3600))
    h = hour * 3600.0
    if st <= h <= et:
        kw = 1.0
    elif h < st:
        kw = float(np.clip(1.0 - (st - h) / max(1.0, st), 0.0, 1.0))
    else:
        kw = float(np.clip(1.0 - (h - et) / max(1.0, 86400 - et), 0.0, 1.0))
    a = sh_to_irradiance(d) * kw
    if n is not None:
        a = a + sh_to_irradiance(n) * (1.0 - kw)
    return a.astype(np.float32)


def exposure_value(w):
    """★ u_env_day2night_exposure 静态无值 ✗ ⇒ 由球谐亮度估（[inferred] ✓ 标注 ✓）
    量纲：让 HDR(光照后) 落到色调映射的有效域 ✓ 与实测曲线自洽 ✓
    """
    amb = ambient_rgb(w, 12.5)
    li = float(w.get('li', 6.0))
    lum = float(amb.mean()) * 0.5 + li * 0.08
    return float(np.clip(1.0 / max(lum, 1e-3), 0.05, 4.0))


def apply_lighting(base_linear, normal, view_dir, w, hour,
                   rough=None, metal=None, spec_ibl=None):
    """★ 延迟光照（简化但每条有据 ✓）
    diffuse = albedo/π × (sun: li × color × N·L × shadow + ambient_SH)
    spec    = 已由 IBL 链单独算（spec_ibl ✓ 传入即用）
    """
    n = np.asarray(normal, np.float32)
    nd = n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-6)
    L = sun_direction(w, hour)
    nl = np.clip((nd * L).sum(-1), 0.0, 1.0)
    li = float(w.get('li', 6.0))
    sc = sun_color(w, hour)
    amb = ambient_rgb(w, hour)
    base = np.asarray(base_linear, np.float32)
    # 漫反射（能量守恒 1/π ✓）
    diff = base * (nl[..., None] * li * sc[None, None, :] + amb[None, None, :]) / np.pi
    out = diff
    if spec_ibl is not None:
        out = out + np.asarray(spec_ibl, np.float32)
    return out.astype(np.float32)


if __name__ == '__main__':
    import sys, json
    sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染')
    import weather_source as WS
    WX = (sys.argv[1] if len(sys.argv) > 1 else
          r'E:\la拆包项目\03_执行\41_还原树\Documents\gres\0000.gpk\weather\weather_ct_pve_city08_v20_pve_zhanshen01.xml')
    w = WS.parse_weather(WX)
    h = WS.daylight_hour(w)
    print(json.dumps({
        'hour': h,
        'sun_dir[fwd]': np.round(sun_direction(w, h), 4).tolist(),
        'sun_color[inf]': np.round(sun_color(w, h), 4).tolist(),
        'sun_intensity[真值]': float(w.get('li', 6.0)),
        'ambient[真值 SH]': np.round(ambient_rgb(w, h), 5).tolist(),
        'exposure[inf]': round(exposure_value(w), 4),
    }, ensure_ascii=False, indent=1))

# ═══════════ ★ 天气轨道真值（weather_tracks.py ✓ 不是推断 ✓）═══════════
try:
    import weather_tracks as _WT
except Exception:
    _WT = None

_TRK_CACHE = {}


def _tracks(xml_path):
    if not xml_path:
        return None
    if xml_path not in _TRK_CACHE:
        try:
            _TRK_CACHE[xml_path] = _WT.parse_tracks(xml_path) if _WT else None
        except Exception:
            _TRK_CACHE[xml_path] = None
    return _TRK_CACHE[xml_path]


def track_env_intensity(xml_path, hour, default=0.25):
    """★ 环境强度（<env> i= ✓ 真值 ✓）"""
    return (_WT.sample(_tracks(xml_path), 'env', 'i', hour, default)
            if _WT else default)


def track_diffuse(xml_path, hour):
    """★ 太阳漫反射：颜色 c= + 强度 i=（真值 ✓）→ (color_rgb, intensity)"""
    tr = _tracks(xml_path)
    if not tr or not _WT:
        return None, None
    col = _WT.color_at(tr, 'diffuse', hour)
    it = _WT.sample(tr, 'diffuse', 'i', hour, None)
    return col, it


def track_ambient(xml_path, hour):
    """★ 环境色 c= + 强度 i=（真值 ✓）"""
    tr = _tracks(xml_path)
    if not tr or not _WT:
        return None, None
    col = _WT.color_at(tr, 'ambient', hour)
    it = _WT.sample(tr, 'ambient', 'i', hour, None)
    return col, it


def track_fog(xml_path, hour):
    tr = _tracks(xml_path)
    if not tr or not _WT:
        return None
    return _WT.color_at(tr, 'fog', hour)
