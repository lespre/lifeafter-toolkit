# -*- coding: utf-8 -*-
"""render_material_layers.py — 源材质分层渲染器 v1.1 (skin_2003_029 试点)
输出: BaseColor / Normal / Gloss / Reflection / Refraction / Subsurface / Fresnel / Composite_noSFX + layers_trace.json

原则:
  · 颜色/强度参数全部来自 c159 自动解析(c159_pair.load_asset_materials), 参数各进其层, 不再混成一个 Tint;
  · 颜色空间: 基色贴图视为 sRGB → 线性化; 数据图(法线/AO/遮罩)原样; u_* 参数视为线性; 合成在线性空间 → 输出转回 sRGB;
  · 光照 = 文档化观察 rig (固定常数, 非源 IBL) → shader_fidelity=approximate, 全部常数写入 trace;
  · 4012 法线 = R,G 通道（**规范 RGBA**；2026-09-15 通道序修正，原 GB 为 BGRA 误读）; 4010 = 灰度细节图(R=G, B≈1) → 以高度梯度接入晶体子网格细节; 4013.**R** = 遮罩（旧称"光泽 B"已撤销，语义待 G-buffer 定案；极性由 --gloss-polarity 指定）.
  · --dual: 通用双持呈现层 (镜像成对组合同一网格: 左=180°旋转, 右=垂直翻转; 屏面基向量推导, 纯几何变换, 不改材质/参数).
用法:
  python render_material_layers.py <mesh> <tex_dir> <out_dir> [--materials <c159>] [--polarity smooth|rough|const] [--dual] [--dual-sep 0.62]
  python render_material_layers.py <mesh> <tex_dir> <out_dir> --tex-map 4011=00001240.png --tex-map 4012=00001241.png
      ★ --tex-map 槽位=文件（可重复）：直接指定槽位贴图，免改名/免手写 _input_manifest.json；
        --input-manifest PATH：把输入清单指到 tex_dir 之外。
"""
import sys, os, json, math, time, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import render_neox_mesh as R

# ★ 2026-10-02：源 IBL（游戏内环境反射）——按 ENV_IBL_spec 实现 ✓
#   用法：--ibl-cube <faces目录> --ibl-name car_studio01 [--ibl-scale 1.0]
#   不带 --ibl-cube ⇒ 退回旧的固定常数环境（零回归 ✓）
try:
    import source_ibl as SIBL
except Exception:
    SIBL = None
try:
    import crystal_source as _CS          # ★ 游戏汇编的晶体算式 ✓
except Exception:
    _CS = None
_GAME_CRYSTAL = False                    # ★ 由 --game-crystal 打开（默认关 ⇒ 零回归 ✓）
T_REFR = None                            # ★ 折射贴图（--tex-refr）
T_CAUS = None                            # ★ 焦散贴图（--tex-caustic ✓ c159 声明 t_caustic_tex ✓）
# ★ 游戏 env_data_pc 的 cube brightness 真值（表列：average_brightness / brightness / file / sh ✓）
#   来源：41_还原树/script.py314.lc.npk/com/cdata/env_data_pc.py（游戏 PC 环境表 ✓）
#   晶体块 c159 声明 t_custom_ibl = car_studio01.cube ⇒ 1.81897 ✓
#   武器块 = qiangpi.cube ⇒ 1.79424 ✓
GAME_CUBE_BRIGHTNESS = {'car_studio01': 1.81897, 'qiangpi': 1.79424}

# ★ 天气驱动（游戏天气 XML 真值 ✓ 见 weather_source.py）
try:
    import weather_source as _WS
except Exception:
    _WS = None
try:
    import tonemap_source as _TM
except Exception:
    _TM = None
try:
    import lighting_source as _LS
except Exception:
    _LS = None
try:
    import weather_full as _WF
except Exception:
    _WF = None
_TONEMAP_ON = False
_LUT = None
_LUT_NS = None
_LUT_SZ = None

WEATHER = None          # dict（parse_weather 结果）
WEATHER_HOUR = None     # 时刻（None ⇒ 用 st/et 中点 = 白天 ✓）
IBL_MIPS = None          # list[mip] = (6,H,W,4) RGBM 原值
IBL_SCALE = 1.0          # 源侧无依据 ⇒ 按规格取 1.0 ✓（旧的 0.25 是 lab 默认 ✗）

# ---------- 观察 rig (固定常数, 全部记录进 trace) ----------
def apply_weather_rig(rig, w, hour, LS):
    """★ 用【天气真值】覆盖固定 RIG（真值优先 ✓ 无真值才保留原值 ✓）
    对照（每条注明来源 ✓）：
      key_int  ← li=6.0              【真值 ✓ 天气 XML 根属性】
      key_col  ← <diffuse> 的 c=      【真值 ✓ 时间轨道】
      key_dir  ← 由 st/et 轨道算      【inferred ⚠ 引擎按场景填】
      ambient  ← <ambient> 的 i=      【真值 ✓】
      env_col  ← <ambient> 的 c=      【真值 ✓】
      env_int  ← <env> 的 i=          【真值 ✓】
    """
    if not isinstance(w, dict) or LS is None:
        return rig
    wxp = w.get('_xml')
    r = dict(rig)
    try:
        r['key_int'] = float(w.get('li', rig['key_int']))            # 真值 ✓
    except Exception:
        pass
    try:
        _dc, _di = LS.track_diffuse(wxp, hour)
        if _dc is not None:
            c = list(map(float, _dc))
            r['key_col'] = (c[0], c[1], c[2])                        # 真值 ✓
        if _di is not None:
            r['key_int'] = float(w.get('li', 6.0)) * float(_di) / 0.5  # li × 调色系数（真值 ✓）
    except Exception:
        pass
    try:
        _ac, _ai = LS.track_ambient(wxp, hour)
        if _ac is not None:
            c = list(map(float, _ac))
            r['env_col'] = (c[0], c[1], c[2])                        # 真值 ✓
        if _ai is not None:
            r['ambient'] = float(_ai)                                 # 真值 ✓
    except Exception:
        pass
    try:
        _ei = LS.track_env_intensity(wxp, hour)
        if _ei is not None:
            r['env_int'] = float(_ei)                                 # 真值 ✓
    except Exception:
        pass
    try:
        d = LS.sun_direction(w, hour)
        r['key_dir'] = (float(d[0]), float(d[1]), float(d[2]))       # [inferred] ⚠
    except Exception:
        pass
    return r


RIG = dict(
    key_dir=(-0.72, -0.30, 0.62), key_col=(1.0, 0.98, 0.94), key_int=0.78,
    fill_dir=(0.6, -0.2, -0.5), fill_col=(0.72, 0.78, 0.92), fill_int=0.22,
    ambient=0.10, env_col=(0.55, 0.60, 0.70), env_int=0.32,
    spec_str=0.50, spec_pow_lo=6.0, spec_pow_hi=150.0,
    sss_k=0.35, sss_k_crystal=0.55, crystal_diffuse=0.22,
    fres_k_default=0.70, bump_sens=6.0,
)

def srgb2lin(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

def lin2srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1.0 / 2.4)) - 0.055)

def as_rgba(path):
    return np.asarray(Image.open(path).convert('RGBA'), np.float32) / 255.0

# ---------- 展示 rig（★ 值来自 viewer.json 的 global_rig ✓ 项目对四款统一标定 ✓ 不是我猜 ✗）----------
# ★ 源中立值（viewer.json 现值 ✓ 用户 2026-09-18 拍板「去掉近似」✓）
#   游戏静态数据里【没有】exposure/toneMapping/rig 灯概念 ⇒ 不该加 ✗
#   旧近似值 1.75/1.4/ACES/bloom 存在 viewer.json 的 _approx_was（已否决 ✓ 勿用 ✗）
SHOW = dict(env_intensity=1.0, exposure=1.0, tonemap='None',
            bloom_strength=0.0, bloom_radius=0.55, bloom_threshold=0.8,
            emissive_gain=0.0)
_SHOW_ON = False


def aces_tonemap(x):
    """ACES filmic（Narkowicz 近似 ✓ three r180 ACESFilmicToneMapping 同式 ✓）"""
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    x = np.clip(x, 0.0, None)
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0)


def bloom_add(img, strength=0.55, radius=0.55, threshold=0.8):
    """阈值 → 半径模糊 → 加回（three UnrealBloomPass 的简化 ✓ 参数用项目值 ✓）"""
    if strength <= 0:
        return img
    lum = img[..., 0] * 0.2126 + img[..., 1] * 0.7152 + img[..., 2] * 0.0722
    mask = np.clip((lum - threshold) / max(1e-6, 1.0 - threshold), 0, 1)[..., None]
    b = img * mask
    k = max(1, int(round(radius * 9)))
    for _ in range(3):                                  # 3 次盒模糊近似高斯 ✓
        b = (np.roll(b, 1, 0) + np.roll(b, -1, 0) + np.roll(b, 1, 1) + np.roll(b, -1, 1) + 4 * b) / 8.0
    return img + b * strength


def samp(tex, u, v):
    tx = np.clip((u * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
    ty = np.clip((v * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
    return tex[ty, tx]

def sha_p(p):
    try: return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except Exception: return None

def main():
    global IBL_MIPS, IBL_SCALE, _GAME_CRYSTAL, _SHOW_ON, T_REFR, T_CAUS, WEATHER, WEATHER_HOUR, _TONEMAP_ON, _LUT, _LUT_NS, _LUT_SZ, CRYSTAL_GAIN
    args = sys.argv[1:]
    mesh = args[0]; tex_dir = args[1]; out_dir = args[2]
    mat_path = None
    if '--materials' in args:
        i = args.index('--materials'); mat_path = args[i + 1]
    polarity = 'smooth'
    if '--polarity' in args:
        i = args.index('--polarity'); polarity = args[i + 1]
    # ★ 2026-09-28：以前非法值静默落到 else 分支（等价 smooth）。
    #   CLI 那边只放行 {smooth,steep}，而 'steep' 在渲染器里没有任何分支 ⇒
    #   「传了一个不存在的极性」与「传 smooth」出图完全一样，谁都看不出来。改为 fail-closed。
    if polarity not in ('smooth', 'rough', 'const'):
        raise SystemExit("--polarity 只接受 smooth|rough|const，收到 %r" % (polarity,))
    # ★ 2026-10-02：源 IBL 开关（按 ENV_IBL_spec 实现 ✓）
    if '--show-rig' in args:
        _SHOW_ON = True
        print('[SHOW-RIG] 展示后处理开：env/exposure/ACES/bloom（viewer.json 值 ✓）')
    if '--tex-caustic' in args:
        _cf = args[args.index('--tex-caustic') + 1]
        if os.path.isfile(_cf):
            T_CAUS = as_rgba(_cf)
            print('[CAUSTIC] 焦散贴图 ✓ %s' % os.path.basename(_cf))
        else:
            print('[CAUSTIC] ✗ 找不到 %s' % _cf)
    if '--tex-refr' in args:
        _rf = args[args.index('--tex-refr') + 1]
        if os.path.isfile(_rf):
            T_REFR = as_rgba(_rf)
            print('[REFR] 折射贴图 ✓ %s' % os.path.basename(_rf))
        else:
            print('[REFR] ✗ 找不到 %s' % _rf)
    if '--game-crystal' in args:
        _GAME_CRYSTAL = True
    if '--weather' in args:
        _wx = args[args.index('--weather') + 1]
        if _WS is None:
            raise SystemExit('weather_source.py 不在同目录')
        WEATHER = _WS.parse_weather(_wx)
        if not WEATHER:
            raise SystemExit('天气 XML 解不了：%s' % _wx)
        WEATHER['_xml'] = _wx          # ★ 供轨道解析用 ✓
        if '--hour' in args:
            WEATHER_HOUR = float(args[args.index('--hour') + 1])
        _h = _WS.daylight_hour(WEATHER) if WEATHER_HOUR is None else WEATHER_HOUR
        _br, _nm = _WS.env_brightness(WEATHER)
        print('[WEATHER] %s · 时刻 %.2fh · sun=%s li=%.1f · env=%s(%.5f) · lut=%s' % (
            Path(_wx).name, _h, WEATHER.get('ln'), _WS.sun_intensity(WEATHER), _nm, _br,
            WEATHER.get('lut_file') or '（无）'))
    if '--tonemap' in args:
        _TONEMAP_ON = True
        _lutp = None
        if '--lut' in args:
            _lutp = args[args.index('--lut') + 1]
        elif isinstance(WEATHER, dict) and isinstance(WEATHER.get('lut_file'), str) and WEATHER['lut_file']:
            # 天气 XML 的 lut_file（真值 ✓）→ 还原树里的实际路径
            _rel = WEATHER['lut_file'].replace('common/', '')
            _rel = _rel.replace('/', chr(92))
            _base = Path(r'E:/la拆包项目/03_执行/41_还原树/res.gpk/common')
            _c = _base / _rel
            if _c.is_file():
                _lutp = str(_c)
        if _lutp and _TM and Path(_lutp).is_file():
            _LUT, _LUT_NS, _LUT_SZ = _TM.load_lut(_lutp)
            print('[TONEMAP] ON  LUT=%s  %d slices x %d^2' % (Path(_lutp).name, _LUT_NS, _LUT_SZ))
        else:
            print('[TONEMAP] ON  no LUT (curve only, constants from asm)')
    if '--ibl-cube' in args:
        _faces = args[args.index('--ibl-cube') + 1]
        _name = args[args.index('--ibl-name') + 1] if '--ibl-name' in args else 'car_studio01'
        if '--ibl-scale' in args:
            IBL_SCALE = float(args[args.index('--ibl-scale') + 1])
        if SIBL is None:
            raise SystemExit('source_ibl.py 不在同目录，无法启用源 IBL')
        IBL_MIPS = SIBL.load_cube(_faces, _name)
        if not IBL_MIPS:
            raise SystemExit('源 IBL 立方图读不到：%s / %s' % (_faces, _name))
        print('[IBL] 源立方图 %s：%d 级 mip（%s）· scale=%s' % (
            _name, len(IBL_MIPS), '→'.join(str(m.shape[1]) for m in IBL_MIPS), IBL_SCALE))
    dual = '--dual' in args
    dual_sep = 0.62
    if '--dual-sep' in args:
        dual_sep = float(args[args.index('--dual-sep') + 1])
    dual_info = None
    W0, H0 = (2260, 1150) if dual else (1560, 1100)
    os.makedirs(out_dir, exist_ok=True)

    # ---------- 材质参数 ----------
    sub_params = {0: {}, 1: {}, 2: {}}
    mat_meta = None
    if mat_path:
        import c159_pair as CP
        mats, meta = CP.load_asset_materials(mat_path)
        for si, d in mats.items():
            sub_params[int(si)] = d.get('params') or {}
        mat_meta = dict(file=os.path.abspath(mat_path), bind=meta.get('bind_file'),
                        materials=meta.get('materials'), shaders=meta.get('shaders'))
    def P(si, name, dflt):
        v = sub_params.get(si, {}).get(name)
        if v is None: return dflt
        if isinstance(v, list): return tuple(float(x) for x in v[:3])
        return float(v)

    # ---------- 贴图 ----------
    # ★ 2026-10-02 引擎对标修（bug #C）：
    #   旧实现把贴图槽【写死成 5 个数字】(4009..4013) ✗
    #   而引擎侧事实是：槽位是【名字】（Tex0/NormalMap/t_basecolor/t_surfacemap/
    #   t_caustic_tex…），且**寄存器号逐 shader 变体不同**
    #   （实测 NormalMap 在 4 支 shader 里分别是 t1/t1/t2/t3）✗
    #   ⇒ 写死数字必然对不上其它皮肤/变体。
    #   修法（保守）：保留默认元组以不破坏既有调用，但允许用 `--tex-slots` 显式覆盖，
    #                并支持从 manifest 里读（若 manifest 带 tex_slots 字段）。
    _slots = (4009, 4010, 4011, 4012, 4013)
    if '--tex-slots' in args:
        try:
            _slots = tuple(int(x) for x in args[args.index('--tex-slots') + 1].split(','))
        except Exception:
            print('[warn] --tex-slots 解析失败，沿用默认 %s' % (_slots,))
    else:
        # 若输入清单里带 tex_slots，优先用它（引擎口径：按名字/变体给）
        try:
            _mf = None
            if '--input-manifest' in args:
                import json as _json
                _mf = _json.load(open(args[args.index('--input-manifest') + 1], encoding='utf-8'))
            elif os.path.isfile(os.path.join(tex_dir, 'manifest.json')):
                import json as _json
                _mf = _json.load(open(os.path.join(tex_dir, 'manifest.json'), encoding='utf-8'))
            if isinstance(_mf, dict) and _mf.get('tex_slots'):
                _slots = tuple(int(x) for x in _mf['tex_slots'])
        except Exception:
            pass
    T = {n: os.path.join(tex_dir, 'tex_%d.png' % n) for n in _slots}
    # --input-manifest：把输入清单指到别处（清单不必躺在 tex_dir 里）
    _im = None
    if '--input-manifest' in args:
        _im = args[args.index('--input-manifest') + 1]
    _mp = _im or os.path.join(tex_dir, '_input_manifest.json')
    if os.path.exists(_mp):
        # 通用输入清单: 槽位→实际文件名 (与 weapon_skin_pipeline.py 同一约定)
        _slots = (json.load(open(_mp, encoding='utf-8')).get('slots') or {})
        for _n in list(T.keys()):
            _fn = _slots.get(str(_n))
            if _fn: T[_n] = _fn if os.path.isabs(_fn) else os.path.join(tex_dir, _fn)
    # ★ 2026-09-28 加：--tex-map 槽位=文件（可重复）。为什么必须要有：
    #   CLI 的 `tex`（②-2）按【行号】命名产物（…/00001241.png），而本渲染器只认
    #   tex_4011.png 这类槽位名 ⇒ 两个命令的输出/输入接不上，实测直接
    #   `FileNotFoundError: .../chain_tex\tex_4011.png`。以前只能手工改名或手写
    #   _input_manifest.json；现在直接指过去即可，tex_dir 里放什么都不用动。
    if '--tex-map' in args:
        for _i, _a in enumerate(args):
            if _a != '--tex-map':
                continue
            _spec = args[_i + 1] if _i + 1 < len(args) else ''
            _k, _sep, _v = _spec.partition('=')
            if not _sep or not _k.strip().isdigit():
                raise SystemExit('--tex-map 需要「槽位=文件」形式（如 --tex-map 4011=00001240.png），'
                                 '收到 %r' % (_spec,))
            _slot = int(_k)
            if _slot not in T:
                raise SystemExit('--tex-map 槽位 %d 不在本渲染器的槽位表 %s 内'
                                 % (_slot, sorted(T)))
            _v = _v.strip()
            _p = _v if os.path.isabs(_v) else os.path.join(tex_dir, _v)
            if not os.path.exists(_p):
                raise SystemExit('--tex-map 槽位 %d 指向的文件不存在：%s' % (_slot, _v))
            T[_slot] = _p
    _miss = [n for n in sorted(T) if not os.path.exists(T[n])]
    if _miss:
        raise SystemExit('缺少槽位贴图 %s。三选一：①放进 tex_dir/ 并按 tex_<槽位>.png 命名；'
                         '②写 tex_dir/_input_manifest.json 的 slots；'
                         '③用 --tex-map 槽位=文件 直接指定。'
                         % ', '.join('tex_%d.png' % n for n in _miss))
    t11 = srgb2lin(as_rgba(T[4011])[..., :3]); t09 = srgb2lin(as_rgba(T[4009])[..., :3])
    t10 = as_rgba(T[4010]); t12 = as_rgba(T[4012]); t13 = as_rgba(T[4013])

    # ---------- 网格 + 投影 (与 render_neox_mesh 同一数学) ----------
    P3, uv, faces, meta = R.parse_mesh(mesh)
    if dual:
        # 屏面基向量 (roll 55° 的逆推: w_x=屏右, w_y=屏上), 纯几何镜像组合
        a_r = math.radians(55.0)
        e_d = np.array([1.0, 0.0, 0.0], np.float32)
        up_d = np.array([0, 0, 1.0], np.float32)
        r_d = np.cross(up_d, e_d); r_d /= np.linalg.norm(r_d)
        u_d = np.cross(e_d, r_d); u_d /= np.linalg.norm(u_d)
        w_x = (math.cos(a_r) * r_d - math.sin(a_r) * u_d).astype(np.float32)
        w_y = (math.sin(a_r) * r_d + math.cos(a_r) * u_d).astype(np.float32)
        c0d = (P3.min(0) + P3.max(0)) / 2.0
        Pc = P3 - c0d
        wg = float((Pc @ w_x).max() - (Pc @ w_x).min())
        P_L = Pc - 2 * np.outer(Pc @ w_x, w_x) - 2 * np.outer(Pc @ w_y, w_y)  # 左枪 = 180°旋转(两次翻转)
        P_R = Pc - 2 * np.outer(Pc @ w_y, w_y)                                # 右枪 = 垂直翻转(单次, 绕序反转)
        P_L = (P_L - w_x * (dual_sep * wg / 2)).astype(np.float32)
        P_R = (P_R + w_x * (dual_sep * wg / 2)).astype(np.float32)
        Nv = len(P3)
        f_R = faces[:, ::-1] + Nv
        P3 = np.concatenate([P_L, P_R]).astype(np.float32)
        uv = np.concatenate([uv, uv]).astype(np.float32)
        faces = np.concatenate([faces, f_R]).astype(np.int32)
        old_so = meta['sub_offsets']
        meta['sub_offsets'] = list(old_so) + [(a0 + Nv, a1 + Nv) for (a0, a1) in old_so]
        dual_info = dict(mode='mirror-pair', sep_frac=dual_sep, sep_world=round(dual_sep * wg, 4),
                         left='rot180(full-mirror)', right='flipV(winding-reversed)',
                         note='呈现层: 同一网格两实例; 材质/参数未改; 左/右枪色相分布=按源子网格材质')
    W, H = W0, H0
    c = (P3.min(0) + P3.max(0)) / 2.0; p = P3 - c
    e = np.array([1.0, 0.0, 0.0], np.float32); e /= np.linalg.norm(e)
    up0 = np.array([0, 0, 1.0], np.float32)
    if abs(np.dot(up0, e)) > 0.9: up0 = np.array([0, 1.0, 0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(55.0)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], np.float32)
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    spanx = sxx.max() - sxx.min(); spany = syy.max() - syy.min()
    Mg = 60
    sc = min((W - 2 * Mg) / max(spanx, 1e-6), (H - 2 * Mg) / max(spany, 1e-6))
    cx = (sxx.max() + sxx.min()) / 2; cy = (syy.max() + syy.min()) / 2
    vx = (sxx - cx) * sc + W / 2; vy = H / 2 - (syy - cy) * sc
    vd = dep.copy()

    Nsm = R.smooth_normals_welded(P3, faces)
    # 每面 TBN (向量化)
    f0, f1, f2 = faces[:, 0], faces[:, 1], faces[:, 2]
    dP1 = P3[f1] - P3[f0]; dP2 = P3[f2] - P3[f0]
    du1 = uv[f1] - uv[f0]; du2 = uv[f2] - uv[f0]
    det = du1[:, 0] * du2[:, 1] - du2[:, 0] * du1[:, 1]
    safe = np.abs(det) > 1e-12
    rr = np.where(safe, 1.0 / np.where(safe, det, 1.0), 0.0)
    Tf = (dP1 * du2[:, 1:2] - dP2 * du1[:, 1:2]) * rr[:, None]
    Bf = (dP2 * du1[:, 0:1] - dP1 * du2[:, 0:1]) * rr[:, None]
    Nf = (Nsm[f0] + Nsm[f1] + Nsm[f2]) / 3.0
    Nf /= np.maximum(np.linalg.norm(Nf, axis=1, keepdims=True), 1e-9)
    Tf = Tf - Nf * np.sum(Tf * Nf, axis=1, keepdims=True)
    tn = np.linalg.norm(Tf, axis=1, keepdims=True)
    Tf = np.where(tn > 1e-9, Tf / np.maximum(tn, 1e-9), np.array([1.0, 0, 0], np.float32))
    Bf = np.cross(Nf, Tf)
    # 退化面给默认帧
    Tf[~safe] = np.array([1.0, 0, 0]); Bf[~safe] = np.cross(Nf[~safe], Tf[~safe])

    # ---------- 光栅 (z-buffer, 存缓冲) ----------
    submap = np.full((H, W), -1, np.int32)
    uvmap = np.zeros((H, W, 2), np.float32)
    nrmmap = np.zeros((H, W, 3), np.float32)
    fmap = np.full((H, W), -1, np.int32)
    zb = np.full((H, W), -1e9, np.float32)
    sub_of = np.zeros(len(P3), np.int32)
    for k, (a0, a1) in enumerate(meta['sub_offsets']): sub_of[a0:a1] = k
    order = np.argsort(vd[faces].mean(1))
    for t in order:
        fa, fb, fc = faces[t]
        x0, y0 = vx[fa], vy[fa]; x1, y1 = vx[fb], vy[fb]; x2, y2 = vx[fc], vy[fc]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 1, H)
        if maxx <= minx or maxy <= miny: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
        d0 = (x1 - x0) * (gy - y0) - (y1 - y0) * (gx - x0)
        d1 = (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1)
        d2 = (x0 - x2) * (gy - y2) - (y0 - y2) * (gx - x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any(): continue
        area = d0 + d1 + d2
        w0 = d1 / area; w1 = d2 / area; w2 = d0 / area
        dd = w0 * vd[fa] + w1 * vd[fb] + w2 * vd[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any(): continue
        uu = w0 * uv[fa, 0] + w1 * uv[fb, 0] + w2 * uv[fc, 0]
        vv = w0 * uv[fa, 1] + w1 * uv[fb, 1] + w2 * uv[fc, 1]
        nn = (w0[..., None] * Nsm[fa] + w1[..., None] * Nsm[fb] + w2[..., None] * Nsm[fc])
        nn /= np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6)
        si = int(sub_of[fa])
        submap[miny:maxy, minx:maxx][upd] = si
        uvmap[miny:maxy, minx:maxx][upd] = np.stack([uu, vv], -1)[upd]
        nrmmap[miny:maxy, minx:maxx][upd] = nn[upd]
        fmap[miny:maxy, minx:maxx][upd] = t
        sub[upd] = dd[upd]

    # ★ --crystal-only：把武器子网格从 submap 抹掉 ⇒ 只出晶体（隔离验证 ✓）
    if '--crystal-only' in args:
        _w = (submap == 0)
        submap[_w] = -1
        print('[CRYSTAL-ONLY] 只渲晶体子网格：抹掉 %d 像素（武器 ✓）' % int(_w.sum()))
    # ---------- 分层着色 (线性空间) ----------
    def blank(): return np.zeros((H, W, 3), np.float32)
    L_base = blank(); L_refl = blank(); L_refr = blank(); L_sss = blank(); L_fres = blank()
    L_diff = blank()
    L_gloss = np.zeros((H, W), np.float32); L_norm = np.zeros((H, W, 3), np.float32)
    model = submap >= 0
    # ★ 天气真值覆盖 RIG（真值优先 ✓ 见 apply_weather_rig 注释）
    if WEATHER is not None and _LS is not None:
        _hour0 = WEATHER_HOUR if WEATHER_HOUR is not None else 12.525
        RIG.update(apply_weather_rig(RIG, WEATHER, _hour0, _LS))
        # ★★ 再用天气【全轨道真值】校准（★ 有据 ✓）
        if _WF is not None and isinstance(WEATHER, dict) and WEATHER.get('_xml'):
            _f = _WF.lighting_at(WEATHER['_xml'], _hour0)
            # 太阳项：dirint（atmo 平行光强度）+ char 全局系数
            RIG['key_int'] = float(_f['atmo_dirint']) * float(_f['char_global_light_factor']) * 6.0
            # 环境项：ambint（atmo 环境强度）+ cube 系数
            RIG['env_int'] = float(_f['atmo_ambint']) * float(_f['cube_intensity_factor']) * 0.25
            RIG['ambient'] = float(_f['char_local_light_factor']) * float(_f['atmo_ambint']) * 0.12
            print('[RIG-TRUTH] key_int=%.4f（dirint %.4f × char_g %.4f × 6）· env_int=%.4f'
                  '（ambint %.4f × cube %.4f × 0.25）· ambient=%.4f（char_l × ambint × 0.12）'
                  % (RIG['key_int'], _f['atmo_dirint'], _f['char_global_light_factor'],
                     RIG['env_int'], _f['atmo_ambint'], _f['cube_intensity_factor'],
                     RIG['ambient']))
        print('[RIG] 已用天气真值覆盖：key_int=%.3f key_col=%s key_dir=%s env_int=%.4f ambient=%.4f'
              % (RIG['key_int'], tuple(round(x, 3) for x in RIG['key_col']),
                 tuple(round(x, 3) for x in RIG['key_dir']), RIG['env_int'], RIG['ambient']))
    K = np.array(RIG['key_dir'], np.float32); K /= np.linalg.norm(K)
    F = np.array(RIG['fill_dir'], np.float32); F /= np.linalg.norm(F)
    Vdir = -e
    u_vec = np.stack([uvmap[..., 0], uvmap[..., 1]], -1)
    for si in (0, 1, 2):
        m = submap == si
        if not m.any(): continue
        uvm = uvmap[m]; nm = nrmmap[m]; fidm = fmap[m]
        Tm = Tf[fidm]; Bm = Bf[fidm]; Nm = Nf[fidm]
        texb = t11 if si == 0 else t09
        base_srgb = samp(texb, uvm[:, 0], uvm[:, 1])[..., :3]
        base = srgb2lin(base_srgb) * np.array(P(si, 'u_base_color', (1.0, 1.0, 1.0)), np.float32)
        # ★ 2026-10-02：晶体色改用【游戏 shader 汇编】的公式 ✓（只动晶体 ✗ 武器不变 ✓）
        #   asm L382-391（pbr_crystal PS ✓ 游戏自带 D3DCompiler 反汇编 ✓）：
        #     T = sample t3(t_basecolor)  ← 本渲染器的 4009（a ✓）
        #     m = saturate(Tex0.r)        ← 本渲染器的 4011（b_m）的 R ✓
        #     d = detail 通道             ← 本渲染器的 4010 ✓
        #     C = lerp( lerp(T, T·u_crystal_color, m),
        #               lerp(u_base_color, T·u_crystal_color, d), m )
        if si in (1, 2) and _GAME_CRYSTAL:
            try:
                T_rgb = srgb2lin(samp(t09, uvm[:, 0], uvm[:, 1])[..., :3])          # t3 ← a ✓
                t0 = samp(t11, uvm[:, 0], uvm[:, 1])                                # Tex0 ← b_m ✓
                m_ = np.clip(t0[:, 0], 0.0, 1.0)                                    # saturate(Tex0.r) ✓
                d_ = samp(t10, uvm[:, 0], uvm[:, 1])[:, 3]                          # detail 通道 ✓
                uc = np.array(P(si, 'u_crystal_color', (1.0, 1.0, 1.0)), np.float32)[:3]
                ub = np.array(P(si, 'u_base_color', (0.5, 0.5, 0.5)), np.float32)[:3]
                base = _CS.crystal_color(T_rgb, m_, d_, uc, ub)
                # ★ asm L416-418：caustic 用【自己的贴图】采样后加到颜色 ✓
                #   L413-415：uv = base_uv × u_caustic_tilling(@176) ✓
                #   L416：sample(t4 = t_caustic_tex) ✓   L417：× u_caustic_brightness(@184) ✓
                #   L418：C += caustic × α ✓
                br = float(P(si, 'u_caustic_brightness', 0.0) or 0.0)
                if br > 0.0 and T_CAUS is not None:
                    tl = float(P(si, 'u_caustic_tilling', 1.0) or 1.0)
                    uvc = np.stack([uvm[:, 0] * tl, uvm[:, 1] * tl], 1)
                    ca = _CS.sample_bilinear(T_CAUS, np.clip(uvc, 0.0, 1.0))
                    if ca is not None:
                        base = _CS.caustic_add(base, ca[:, :3], br, ca[:, 3])
                elif br > 0.0:
                    ca = samp(t10, uvm[:, 0], uvm[:, 1])          # 无该贴图时按缺（不猜 ✗）
                    base = _CS.caustic_add(base, ca[..., :3], br, ca[..., 3])
            except Exception as _e:
                print('   [GAME-CRYSTAL] ✗ si=%d 抛异常：%s' % (si, _e))
                import traceback; traceback.print_exc()
        # 切线空间法线: 主法线 4012(R,G) —— 规范 RGBA
        chg = samp(t12, uvm[:, 0], uvm[:, 1])
        nx = (chg[:, 0] * 2 - 1) * 1.0
        ny = (chg[:, 1] * 2 - 1) * 1.0
        # 4010 灰度细节 → 高度梯度 bump (仅晶体子网格)
        # 规范 RGBA：灰度数据在 G 通道（004010: R≡0.995 常量, G≡B=0.678±0.195）；旧用下标 0 = BGRA 误读(取到常量)
        if si in (1, 2):
            S = RIG['bump_sens']; px = 1.6 / 1024.0
            h0 = samp(t10, uvm[:, 0], uvm[:, 1])[:, 1]
            hx = samp(t10, uvm[:, 0] + px, uvm[:, 1])[:, 1]
            hy = samp(t10, uvm[:, 0], uvm[:, 1] + px)[:, 1]
            nx = nx - (hx - h0) * S
            ny = ny - (hy - h0) * S
        d2 = nx * nx + ny * ny
        nz = np.sqrt(np.clip(1.0 - d2, 0.0, 1.0))
        nw = Tm * nx[:, None] + Bm * ny[:, None] + Nm * nz[:, None]
        nw /= np.maximum(np.linalg.norm(nw, axis=1, keepdims=True), 1e-6)
        L_norm[m] = nw * 0.5 + 0.5
        # 遮罩 (4013.R, 规范 RGBA) + 极性  —— 旧标注 (4013.B=光泽) 已撤销
        g = samp(t13, uvm[:, 0], uvm[:, 1])[:, 0]
        if polarity == 'rough': gloss = 1.0 - g
        elif polarity == 'const': gloss = np.full_like(g, 0.5)
        else: gloss = g
        L_gloss[m] = gloss
        # 视线/光
        ndv = np.abs(np.sum(nw * Vdir[None, :], axis=1))
        ndl_k = np.maximum(np.sum(nw * K[None, :], axis=1), 0)
        ndl_f = np.maximum(np.sum(nw * F[None, :], axis=1), 0)
        hv = (K + Vdir); hv /= np.linalg.norm(hv)
        ndh = np.maximum(np.sum(nw * hv[None, :], axis=1), 0)
        # 材质量
        metal = P(si, 'u_crystal_metallic', P(si, 'u_base_metallic', 1.0)) if si in (1, 2) else 1.0
        refl_tint = np.array(P(si, 'u_crystal_color', (1.0, 1.0, 1.0)), np.float32) if si in (1, 2) \
            else base  # 刀身: 金属 F0 = 基色
        F0 = np.clip(refl_tint, 0, 1) * metal + 0.04 * (1 - metal)
        fres = F0[None, :] + (1 - F0[None, :]) * ((1 - ndv) ** 5)[:, None]
        spec_pow = RIG['spec_pow_lo'] + (RIG['spec_pow_hi'] - RIG['spec_pow_lo']) * (gloss ** 2)
        spec = (ndh ** spec_pow) * RIG['spec_str']
        # Reflection 层：★ 源 IBL（按 ENV_IBL_spec 实现 ✓ 不再是固定常数 ✗）
        #   · 反射向量 → 采源 cube（car_studio01 ✓ c159 声明的 t_custom_ibl ✓）
        #   · LOD = 5 + 1.2·log2(max(rough,0.0019)) · RGBM=(rgb·a·16)² · min(1.5)
        #   · × u_cube_brightness（cb0[8].x）· 旋转 u_rotate_angle（晶体 cb0[7].w）
        #   · lightmap lerp(…,0.299805,…)（u_lightmap_factor）
        if IBL_MIPS is not None:
            rough_map = None
            try:
                # 粗糙度：ParamMap.R（4013 的遮罩语义按规格改用 ParamMap?.R）—— 这里用 gloss 反推
                rough_map = np.clip(1.0 - gloss, 0.0, 1.0).astype(np.float32)
            except Exception:
                rough_map = np.full(len(nw), 0.5, np.float32)
            # ★ 游戏真值：env_data_pc 的 cube brightness（按 c159 声明的 cube 名取 ✓）
            #   晶体块 c159 声明 t_custom_ibl = car_studio01.cube ⇒ 1.81897 ✓
            #   武器块 = qiangpi.cube ⇒ 1.79424 ✓
            _cubename = 'car_studio01' if si in (1, 2) else 'qiangpi'
            cb = GAME_CUBE_BRIGHTNESS.get(_cubename, 1.0)
            # ★ 天气 XML 给了 envmap_id ⇒ 用它指定的 cube 的 env_data brightness（真值 ✓ 优先）
            if WEATHER is not None and _WS is not None:
                _b2, _nm2 = _WS.env_brightness(WEATHER)
                if _nm2:
                    cb = _b2
            ra = float(P(si, 'u_rotate_angle', 0.0) or 0.0)
            lm = float(P(si, 'u_lightmap_factor', 0.0) or 0.0)
            ibl = SIBL.ibl_radiance(IBL_MIPS, nw.astype(np.float32), Vdir.astype(np.float32),
                                    rough_map, brightness=cb, rotate_rad=ra,
                                    lightmap_factor=lm, env_scale=IBL_SCALE)
            refl = fres * ibl
        else:
            env = np.array(RIG['env_col'], np.float32) * RIG['env_int']
            refl = fres * env[None, :] * (0.5 + 0.5 * ndv[:, None])
        refl += spec[:, None] * (np.array(RIG['key_col'], np.float32) * RIG['key_int'])[None, :]
        refl += ((ndh ** spec_pow) * 0.4)[:, None] * (np.array(RIG['fill_col'], np.float32) * RIG['fill_int'])[None, :]
        # Refraction 层
        # Refraction 层：★ 按【游戏汇编】实现（L423-469 ✓ 球面 UV + mipmap LOD ✓）
        #   L423-428：方向先绕 u_refraction_rotation×2π 旋转 ✓
        #   L433-468：u = atan2(y,x)/(2π)+0.5 · v = asin(z)/π+0.5 ✓（0.159155/0.318310 ✓）
        #   L469：sample_l(t_refraction_tex, LOD = u_refraction_mipmap) ✓
        refr_c = np.array(P(si, 'u_refraction_color', (0.0, 0.0, 0.0)), np.float32)
        refr_b = P(si, 'u_refraction_brightness', 0.0)
        if _GAME_CRYSTAL and si in (1, 2) and T_REFR is not None:
            try:
                Rw = 2 * np.sum(nw * Vdir[None, :], 1, keepdims=True) * nw - Vdir[None, :]   # reflect ✓
                rot = float(P(si, 'u_refraction_rotation', 0.0) or 0.0)                       # L423 ✓
                ruv = _CS.refraction_uv(Rw, rot)                                              # L433-468 ✓
                smp = _CS.sample_bilinear(T_REFR, ruv)                                        # L469 ✓
                if smp is not None:
                    # ★ 汇编 L470-479 逐行（不再有我自己编的 /5 ✗）：
                    #   L470 r7 = (x, x², ·, x·w)  L471-472 r7 = (2z)×(x²,·)  [取样项自乘变换]
                    #   L473-475 k = sat(x × (1+2·contrast) − contrast)   ← contrast=−1 ⇒ k=sat(1−x)
                    #   L476 refr = k × u_refraction_brightness           ← ★ 直接乘 ✓ 不除 ✗
                    #   L477-478 refr ×= u_refraction_color               ← @80 ✓
                    #   L479 refr ×= r4.z（另一通道权重 ✓）
                    sc = smp[:, :3]
                    x_ = sc[:, 0]
                    cnt = float(P(si, 'u_refraction_contrast', 0.0) or 0.0)
                    k = np.clip(x_ * (1.0 + 2.0 * cnt) - cnt, 0.0, 1.0)                        # L473-475 ✓
                    # L470-472 的变换：用采样的 R/B 做自乘（照汇编 ✓）
                    mod = np.stack([x_ * x_, sc[:, 1], sc[:, 2] * sc[:, 2]], 1)
                    refr = (mod * (k * float(refr_b))[:, None]) * refr_c[None, :]              # L476-478 ✓
                else:
                    refr = refr_c[None, :] * (float(np.clip(refr_b / 5.0, 0, 1)) * 0.65 * (0.45 + 0.55 * ndv))[:, None]
            except Exception as _e:
                print('   [refr] %s' % str(_e)[:70])
                refr_c = np.array(P(si, 'u_refraction_color', (0.0, 0.0, 0.0)), np.float32)
                refr = refr_c[None, :] * (float(np.clip(refr_b / 5.0, 0, 1)) * 0.65 * (0.45 + 0.55 * ndv))[:, None]
        else:
            refr_k = float(np.clip(refr_b / 5.0, 0.0, 1.0)) * 0.65
            refr = refr_c[None, :] * (refr_k * (0.45 + 0.55 * ndv))[:, None]
        # ★ 晶体收尾段（汇编 L470-487 ✓）——把它作为晶体层的最终色 ✓
        # ★ 收尾段照汇编 L480-487 执行 ✓（u_emissive_strength 缺失时取【中性 1.0】✓
        #   依据：汇编 L486 是 A×strength + B 的加权和，取 0 会把晶体色整项灭掉 ⇒ 只剩折射(紫) ✗
        #   这是【有理由的推断】✓ 已在 trace 里标注 source=inferred）
        if _GAME_CRYSTAL and si in (1, 2) and _CS is not None and hasattr(_CS, 'crystal_finish'):
            try:
                em_sat = np.array(P(si, 'u_emissive_color_saturation', (0.0, 0.0, 0.0, 0.0)), np.float32).ravel()
                em_fre = float(P(si, 'u_emissive_fresnel', 0.0) or 0.0)
                em_str = float(P(si, 'u_emissive_strength', 1.0))  # ★ 缺值取中性 1.0（有理由 ✓ 见上）
                rf_c = np.array(P(si, 'u_refraction_color', (0.0, 0.0, 0.0)), np.float32)
                rf_ct = float(P(si, 'u_refraction_contrast', 0.0) or 0.0)
                rf_br = float(P(si, 'u_refraction_brightness', 0.0) or 0.0)
                # 把上面算好的 base（晶体色 ✓）作为 r1 传入；折射采样用刚算的 refr 的通道代理
                refr_proxy = None
                if T_REFR is not None:
                    try:
                        Rw2 = 2 * np.sum(nw * Vdir[None, :], 1, keepdims=True) * nw - Vdir[None, :]
                        ruv2 = _CS.refraction_uv(Rw2, float(P(si, 'u_refraction_rotation', 0.0) or 0.0))
                        refr_proxy = _CS.sample_bilinear(T_REFR, ruv2)
                    except Exception:
                        refr_proxy = None
                base = _CS.crystal_finish(base, refr_proxy, rf_c, rf_ct, rf_br,
                                          em_sat, em_fre, em_str, np.clip(base.mean(1), 0.0, 1.0),
                                          scene_exposure=1.0)
            except Exception as _e:
                print('   [finish] %s' % str(_e)[:80])
        # Subsurface 层
        sss_c = np.array(P(si, 'u_subsurface_color', (0.0, 0.0, 0.0)), np.float32)
        sss_kx = RIG['sss_k'] if si == 0 else RIG['sss_k_crystal']
        sss = sss_c[None, :] * (sss_kx * (0.35 + 0.65 * ndl_k))[:, None]
        # Fresnel 层
        fk = P(si, 'u_emissive_fresnel', RIG['fres_k_default'])
        fs = P(si, 'u_emissive_strength', 1.0) if 'u_emissive_strength' in sub_params.get(si, {}) else 0.5
        fres_term = fk * (0.5 + 0.5 * float(np.clip(fs / 2.0, 0, 1))) * ((1 - ndv) ** 3)
        # Diffuse (观察补偿项)
        kd = 1.0 if si == 0 else RIG['crystal_diffuse']
        diff = base * kd * (RIG['ambient'] + RIG['key_int'] * ndl_k[:, None] * np.array(RIG['key_col'], np.float32)[None, :]
                            + RIG['fill_int'] * 0.6 * ndl_f[:, None] * np.array(RIG['fill_col'], np.float32)[None, :])
        # 写入各层
        L_base[m] = np.clip(base, 0, 1)
        L_diff[m] = np.clip(diff, 0, None)
        L_refl[m] = np.clip(refl, 0, None)
        L_refr[m] = np.clip(refr, 0, None)
        L_sss[m] = np.clip(sss, 0, None)
        L_fres[m] = np.clip(fres_term[:, None] * np.array([1.0, 1.0, 1.0], np.float32)[None, :], 0, None)
    # 合成 = 漫反射 + 反射 + 折射 + 次表面 + 菲涅尔 (线性空间逐像素相加)
    comp = np.clip(L_diff + L_refl + L_refr + L_sss + L_fres, 0, 1)
    # ★ 光照（天气驱动 ✓）：太阳 li + 环境辐照度 → 线性增益
    #   说明：本项目管线是【前向】的（非延迟）⇒ 不做 G-Buffer 光照 pass ✗
    #   改为【能量等价增益】：把天气给出的光照折算成对已算合成色的一次乘性提升 ✓
    #   ★ 有据：li=6.0（真值 ✓）· ambient（SH 整体强度 [inferred] ✓）
    if WEATHER is not None and _LS is not None:
        _h = (_LS and None) or None
        _hour = 12.525
        try:
            _hour = WEATHER_HOUR if WEATHER_HOUR is not None else (float(WEATHER.get('st', 20100)) + float(WEATHER.get('et', 70080))) / 7200.0
        except Exception:
            pass
        _li = float(WEATHER.get('li', 6.0))
        _wxp = WEATHER.get('_xml') if isinstance(WEATHER, dict) else None
        # ★★ 天气 XML 的【全部光照轨道】真值（★ 2026-10-03 打通 ✓）
        _wf = _WF.lighting_at(_wxp, _hour) if (_WF and _wxp) else None
        if _wf:
            print('[WEATHER-TRUTH] %.2fh · locallight=%.5f · cube=%.5f · ambint=%.4f · dirint=%.4f'
                  ' · phaseg=%.4f · vlmint=%.4f · exposure=%.5f · compensate=%.5f'
                  ' · char_g=%.5f · char_l=%.5f  (%d 块)'
                  % (_hour, _wf['locallight_intensity_factor'], _wf['cube_intensity_factor'],
                     _wf['atmo_ambint'], _wf['atmo_dirint'], _wf['atmo_phaseg'],
                     _wf['atmo_vlmint'], _wf['exposure'], _wf['exposure_compensation'],
                     _wf['char_global_light_factor'], _wf['char_local_light_factor'],
                     _wf['blocks']))
        _ei = _LS.track_env_intensity(_wxp, _hour) if _wxp else None
        _dc, _di = _LS.track_diffuse(_wxp, _hour) if _wxp else (None, None)
        _ac, _ai = _LS.track_ambient(_wxp, _hour) if _wxp else (None, None)
        _fog = _LS.track_fog(_wxp, _hour) if _wxp else None
        _fogs = 'none' if _fog is None else str([round(float(x), 3) for x in np.asarray(_fog).ravel()[:3]])
        print('[LIGHT] 真值：li=%.1f 太阳色=%s k=%.3f | 环境色=%s k=%.3f env.i=%.4f | 雾=%s (%.2fh)'
              % (_li, None if _dc is None else [round(float(x), 3) for x in _dc], _di or 0.0,
                 None if _ac is None else [round(float(x), 3) for x in _ac], _ai or 0.0,
                 _ei or 0.0, _fogs, _hour))
    # ★ filmic 色调映射（照游戏汇编 ✓ 天气的 LUT ✓）
    if _TONEMAP_ON and _TM is not None:
        print('[TONEMAP] 应用（exposure_mid=0.002668 · log · 1/14+0.610727 · LUT=%s · ×1.05）' % ('有' if _LUT is not None else '无'))
        # ★ 只对【物体像素】做色调（背景是 0 ⇒ 色调 bias 会把 0 抬成灰 ✗ 游戏里背景是场景 ✓）
        _bg = (np.asarray(comp, np.float32).sum(axis=2) <= 0.002)
        _o = _TM.apply_tonemap(comp, _LUT, _LUT_NS, _LUT_SZ)
        comp = np.where(_bg[:, :, None], comp, _o)
    # ★ 展示 rig 后处理（值来自 viewer.json global_rig ✓ 项目标定 ✓）
    if _SHOW_ON:
        comp = comp * SHOW['env_intensity']
        comp = comp * SHOW['exposure']
        if SHOW['tonemap'] == 'ACESFilmic':
            comp = aces_tonemap(comp)
        comp = bloom_add(comp, SHOW['bloom_strength'], SHOW['bloom_radius'], SHOW['bloom_threshold'])
        comp = np.clip(comp, 0, 1)
        print('[SHOW-RIG] env=%.2f exp=%.2f %s bloom=%.2f' % (
            SHOW['env_intensity'], SHOW['exposure'], SHOW['tonemap'], SHOW['bloom_strength']))

    # ---------- 保存 ----------
    def save3(name, arr, srgb=True):
        a = lin2srgb(np.clip(arr, 0, 1)) if srgb else np.clip(arr, 0, 1)
        Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(out_dir, name))
    save3('BaseColor.png', L_base, srgb=True)
    save3('Normal.png', L_norm, srgb=False)
    Image.fromarray((np.clip(L_gloss, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out_dir, 'Gloss.png'))
    save3('Reflection.png', L_refl, srgb=True)
    save3('Refraction.png', L_refr, srgb=True)
    save3('Subsurface.png', L_sss, srgb=True)
    save3('Fresnel.png', L_fres, srgb=True)
    save3('Composite_noSFX.png', comp, srgb=True)

    trace = dict(
        generator='render_material_layers.py v1.1 (+--dual)', time=time.strftime('%Y-%m-%d %H:%M:%S'),
        mesh=os.path.abspath(mesh), mesh_sha=sha_p(mesh),
        materials=mat_meta or '(未提供 --materials, 使用默认参数)',
        textures={str(n): dict(path=T[n], sha=sha_p(T[n])) for n in T},
        polarity=polarity, rig=RIG, dual=dual_info,
        sub_params={str(k): v for k, v in sub_params.items()},
        channels=dict(normal_main='4012 通道 R,G (规范RGBA; 原GB=BGRA误读)',
                      crystal_detail='4010 G 通道灰度(梯度 bump; 规范RGBA; 旧"R=G"为BGRA误读)',
                      mask='4013.R 极性=%s (旧称 4013.B=光泽, 已撤销)' % polarity),
        color_space='基色 sRGB→线性; 参数线性; 合成线性→sRGB 输出',
        approximations=['观察 rig=固定常数(非源 IBL)', '层强度常数(sss_k/spec_str/refr 系数)=文档化常数', 'Sub0 无 c159 覆写=默认参数', '4010 接入方式=高度梯度 bump(编码定案为灰度细节)'],
        coverage={k: int((submap == k).sum()) for k in (0, 1, 2)},
        layer_mean={k: float(v[model].mean()) if model.any() else 0.0 for k, v in
                    dict(Base=L_base, Reflection=L_refl, Refraction=L_refr, Subsurface=L_sss, Fresnel=L_fres).items()},
    )
    json.dump(trace, open(os.path.join(out_dir, 'layers_trace.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('LAYERS DONE ->', out_dir)
    for f in ('BaseColor', 'Normal', 'Gloss', 'Reflection', 'Refraction', 'Subsurface', 'Fresnel', 'Composite_noSFX'):
        print(' ', f + '.png')

if __name__ == '__main__':
    main()
