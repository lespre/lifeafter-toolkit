"""weather_full.py —— 读天气 XML 的【全部光照轨道】真值（★ 2026-10-03 ✓）
依据：weather_ct_pve_city08_v20_pve_zhanshen01.xml 实测
  轨道块 = <name><adjust_N 字段="值" t="秒" tag="..."/></name>
  关键时刻 tag：min_time(0) tod1(29760) sunrise(31560) tod2(43200=正午)
               tod3(62040) sunset(65640) tod4(79200) max_time(86399)
"""
import re
from pathlib import Path

KEY = ('locallight_intensity_factor', 'cube_intensity_factor', 'atmo_param', 'exposure',
       'exposure_compensation', 'char_global_light_factor', 'char_local_light_factor',
       'ambient_quality_zero', 'ambient', 'diffuse', 'env', 'lightmap', 'fog')


def _num(v):
    try:
        return float(v)
    except Exception:
        return v


def parse_all_tracks(xml_path):
    """→ {block: [(t_sec, {field: val}), ...]}（全部块 ✓）"""
    txt = Path(xml_path).read_text('utf-8', 'replace')
    m0 = re.match(r'^\s*<weather\b[^>]*>(.*)</weather>\s*$', txt, re.S)
    inner = m0.group(1) if m0 else txt          # ★ 先剥根标签（否则 .*? 吞全文 ✗ 实测踩过）
    out = {}
    for m in re.finditer(r'<([a-zA-Z_][\w]*)\b[^>]*>(.*?)</\1>', inner, re.S):
        name, body = m.group(1), m.group(2)
        rows = []
        for a in re.finditer(r'<adjust_(\d+)\s+([^>]*?)/?>', body):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', a.group(2)))
            try:
                ts = float(attrs.get('t', 0))
            except Exception:
                continue
            d = {}
            for k, v in attrs.items():
                if k == 't':
                    continue
            # 保留字段语义
            for k, v in attrs.items():
                if k in ('t',):
                    continue
                d[k] = v if k == 'tag' else _num(v)
            rows.append((ts, d))
        if rows:
            rows.sort(key=lambda r: r[0])
            out[name] = rows
    return out


def sample(rows, field, hour, default=None):
    """按时刻插值（线性 ✓）"""
    sec = float(hour) * 3600.0
    pts = [(ts, d[field]) for ts, d in rows if field in d and not isinstance(d[field], str)]
    if not pts:
        return default
    if sec <= pts[0][0]:
        return pts[0][1]
    if sec >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        t0, v0 = pts[i]
        t1, v1 = pts[i + 1]
        if t0 <= sec <= t1:
            if t1 == t0:
                return v0
            f = (sec - t0) / (t1 - t0)
            try:
                return float(v0) * (1 - f) + float(v1) * f
            except Exception:
                return v0
    return default


def lighting_at(xml_path, hour):
    """★ 预览/场景光照真值（该时刻 ✓）"""
    tr = parse_all_tracks(xml_path)
    g = lambda b, f, d=None: sample(tr.get(b, []), f, hour, d)
    return {
        'hour': hour,
        'locallight_intensity_factor': g('locallight_intensity_factor', 'factor'),
        'cube_intensity_factor': g('cube_intensity_factor', 'factor'),
        'cube_shadow_factor': g('cube_intensity_factor', 'shadow_factor'),
        'atmo_ambint': g('atmo_param', 'ambint'),
        'atmo_dirint': g('atmo_param', 'dirint'),
        'atmo_phaseg': g('atmo_param', 'phaseg'),
        'atmo_vlmint': g('atmo_param', 'vlmint'),
        'exposure': g('exposure', 'a'),
        'exposure_compensation': g('exposure_compensation', 'compensate'),
        'char_global_light_factor': g('char_global_light_factor', 'a'),
        'char_local_light_factor': g('char_local_light_factor', 'a'),
        'blocks': len(tr),
    }


if __name__ == '__main__':
    import sys, json
    WX = (sys.argv[1] if len(sys.argv) > 1 else
          r'E:\la拆包项目\03_执行\41_还原树\Documents\gres\0000.gpk\weather\weather_ct_pve_city08_v20_pve_zhanshen01.xml')
    for h in (0, 8, 12.53, 16, 18, 22):
        print(json.dumps(lighting_at(WX, h), ensure_ascii=False, indent=None))
