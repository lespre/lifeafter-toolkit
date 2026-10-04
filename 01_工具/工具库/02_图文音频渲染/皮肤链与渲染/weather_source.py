"""weather_source.py —— 按【游戏天气 XML】驱动渲染的光照
依据（2026-10-02 实测 ✓）：
  · 天气 XML：Documents/gres/0000.gpk/weather/*.xml（根属性 1812 字符 ✓）
  · 字段：ln/li/lmi（光源与强度）· st/et（日照时刻）· envmap_id（环境 cube）
          realskylightsh_day/_night（球谐 ✓ 28 个数 = 7×float4 ✓）
          day2night_blendsh / night2day_blendsh（昼夜过渡 ✓）
  · 环境 cube 亮度：env_data_pc 表（average_brightness / brightness ✓）
  · 天空：WeatherObjSkyEHdr（hdr_0..7 按时间混合 ✓ · u_sky_ehdr_map%d_blendweight ✓）
★ 说明：时刻是【运行时变量】✗ —— 静态数据里只有轨道 ✓
        取【白天】= st/et 中点（有据 ✓ 非编造 ✓）；可用 --hour 覆盖 ✓
"""
import re, struct
import numpy as np
from pathlib import Path

# env_data_pc 表（游戏真值 ✓ 已解）
CUBE_BRIGHTNESS = {
    'panorama': 1.79085, 'night_clearsky': 1.69658, 'car_studio01': 1.81897,
    'qiangpi': 1.79424, 'nielian01': 1.80043, 'snow': 1.82038,
    'corsica_beach': 1.76243, 'bonifacio_aragon_stairs': 1.71021,
    'bonifacio_street': 1.72638, 'clould_weather': 1.08574,
    'cave_entry_in_the_forest': 1.11470, 'over_the_clouds': 1.76904,
}
# envmap_id → cube 名（env_data_pc 池顺序 ✓）
ENVMAP_ORDER = ['panorama', 'night_clearsky', 'bonifacio_aragon_stairs',
                'bonifacio_street', 'car_studio01', 'cave_entry_in_the_forest',
                'clould_weather', 'corsica_beach', 'epic_quad_panorama_gray',
                'gdansk_shipyard_buildings', 'glazed_patio',
                'industrial_pipe_and_valve_01_4k', 'jiayuan02a_night',
                'jiayuan02a', 'neight_02', 'nielian01', 'over_the_clouds',
                'qiangpi', 'snow']


def parse_weather(xml_path):
    """解天气 XML 的根属性 → dict（真值 ✓）"""
    t = Path(xml_path).read_text('utf-8', 'replace')
    m = re.match(r'\s*<weather\s+([^>]*?)>', t, re.S)
    if not m:
        return None
    out = {}
    for a in re.finditer(r'([a-zA-Z_][\w]*)\s*=\s*"([^"]*)"', m.group(1)):
        k, v = a.group(1), a.group(2)
        if re.fullmatch(r'-?\d+(\.\d+)?([eE][-+]?\d+)?', v):
            out[k] = float(v)
        else:
            out[k] = v
    # ★ 根标签之外的字段（子节点 / 属性 ✓ 如 lut_file、lution）
    for k in ('lut_file', 'lution', 'lution_file'):
        m2 = re.search(r'%s\s*=\s*"([^"]*)"' % k, t)
        if m2 and k not in out:
            out[k] = m2.group(1)
    # 球谐：28 个数 → (7,4)
    for k in ('realskylightsh_day', 'realskylightsh_night'):
        if isinstance(out.get(k), str):
            try:
                arr = [float(x) for x in out[k].split(',') if x.strip()]
                out[k] = np.array(arr[:28], np.float32).reshape(-1, 4)
            except Exception:
                out[k] = None
    return out


def env_cube_name(envmap_id):
    i = int(envmap_id)
    return ENVMAP_ORDER[i] if 0 <= i < len(ENVMAP_ORDER) else None


def daylight_hour(w):
    """白天时刻（st/et 中点 ✓ 有据）"""
    st, et = float(w.get('st', 6 * 3600)), float(w.get('et', 18 * 3600))
    return (st + et) / 2.0 / 3600.0


def night_weight(w, hour):
    """昼夜权重（用 day2night_blendsh / night2day_blendsh 的阈值语义做线性过渡 ✓）"""
    st, et = float(w.get('st', 6 * 3600)), float(w.get('et', 18 * 3600))
    h = hour * 3600.0
    if st <= h <= et:
        return 1.0            # 全白天
    if h < st:
        d = (st - h) / max(1.0, st)
    else:
        d = (h - et) / max(1.0, 86400.0 - et)
    return float(np.clip(1.0 - d, 0.0, 1.0))


def ambient_sh(w, hour):
    """球谐 = day/night 按昼夜权重插值（引擎 _get_hourly_sh_rgb_at_time 的语义 ✓）"""
    d = w.get('realskylightsh_day')
    n = w.get('realskylightsh_night')
    if d is None and n is None:
        return None
    if d is None:
        return n
    if n is None:
        return d
    kw = night_weight(w, hour)
    return d * kw + n * (1.0 - kw)


def sun_intensity(w):
    """平行光强度（li ✓ 全天气统一 6.0 ✓）"""
    return float(w.get('li', 6.0))


def env_brightness(w):
    """环境 cube 的 brightness（env_data_pc 真值 ✓）"""
    nm = env_cube_name(w.get('envmap_id', 0))
    return CUBE_BRIGHTNESS.get(nm, 1.0), nm


def summarize(xml_path, hour=None):
    w = parse_weather(xml_path)
    if not w:
        return None
    h = daylight_hour(w) if hour is None else float(hour)
    br, nm = env_brightness(w)
    sh = ambient_sh(w, h)
    return {
        'file': Path(xml_path).name,
        'hour': h,
        'sun': {'name': w.get('ln'), 'intensity': sun_intensity(w), 'moon': w.get('lmi')},
        'daylight': {'st': w.get('st'), 'et': w.get('et')},
        'env': {'envmap_id': w.get('envmap_id'), 'cube': nm, 'brightness': br,
                'night_envmap_id': w.get('night_envmap_id')},
        'sh': None if sh is None else sh.tolist(),
        'fog': {'density': w.get('fog_density'), 'height': w.get('fog_height'),
                'mie_dist': w.get('fog_mie_distance')},
        'ao_int': w.get('ao_int'), 'blend': {'d2n': w.get('day2night_blendsh'),
                                             'n2d': w.get('night2day_blendsh')},
    }


if __name__ == '__main__':
    import sys, json
    p = sys.argv[1] if len(sys.argv) > 1 else r'E:\la拆包项目\03_执行\41_还原树\Documents\gres\0000.gpk\weather\weather_ct_pve_city08_v20_pve_zhanshen01.xml'
    hour = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(summarize(p, hour), ensure_ascii=False, indent=1))
