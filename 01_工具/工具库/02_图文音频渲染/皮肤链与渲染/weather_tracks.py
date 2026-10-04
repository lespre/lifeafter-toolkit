"""weather_tracks.py —— 解天气 XML 的【时间轨道】（★ 这是游戏光照的真值来源 ✓）
结构（实测 2026-10-02 ✓）：
  <weather ...>                     ← 根属性（ln/li/st/et/envmap_id/lut_file ✓）
     <env>   <adjust_N i=".." a=".." t="秒" tag=".."/>   ← ★ 环境强度随时间
     <diffuse> <adjust_N .../>      ← 太阳漫反射色
     <ambient> <adjust_N .../>      ← 环境色
     <shadow_clr> <adjust_N .../>   ← 阴影色
     <cloud_color> · <planet> · <star> · <lightmap> · <fog> · <fog_near>
  tag 关键时刻：min_time(0) sunrise(28800) tod1(32400) tod2(43200)
                sunset(57600) tod3(61200) tod4(79200) max_time(86399)
★ 引擎语义：按帧时间 t 在相邻两条 adjust 之间插值 ✓（与 WeatherObjSkyEHdr 一致 ✓）
"""
import re
import numpy as np
from pathlib import Path

KEY_TAGS = {'min_time': 0, 'sunrise': 28800, 'tod1': 32400, 'tod2': 43200,
            'sunset': 57600, 'tod3': 61200, 'tod4': 79200, 'max_time': 86399}


def _parse_color(v):
    """颜色字段（整数打包 ✓ 引擎惯例 0xBBGGRR 或 0xAARRGGBB ⇒ 试解为 RGB 0-1）"""
    try:
        n = int(v)
    except Exception:
        return None
    b = np.array([(n >> 16) & 255, (n >> 8) & 255, n & 255], np.float32) / 255.0
    return b


def parse_tracks(xml_path):
    """→ {块名: [(t秒, {字段: 值}), ...]}"""
    t = Path(xml_path).read_text('utf-8', 'replace')
    # 去掉根标签内部，逐块扫
    out = {}
    # ★ 只取【已知的子色块】（跳过根 <weather> —— 它会把全文吞掉 ✗）
    BLOCKS = ('env', 'diffuse', 'ambient', 'shadow_clr', 'cloud_color', 'planet',
              'star', 'lightmap', 'fog', 'fog_near')
    for name in BLOCKS:
        m = re.search(r'<%s\b[^>]*>(.*?)</%s>' % (name, name), t, re.S)
        if not m:
            continue
        body = m.group(1)
        rows = []
        for a in re.finditer(r'<adjust_(\d+)\s+([^>]*?)/?>', body):
            attrs = dict(re.findall(r'(\w+)="([^"]*)"', a.group(2)))
            try:
                tt = float(attrs.get('t', 0))
            except Exception:
                continue
            vals = {}
            for k, v in attrs.items():
                if k == 't':
                    continue
                try:
                    vals[k] = float(v)
                except Exception:
                    vals[k] = v
            if 'tag' in attrs:
                vals['_tag'] = attrs['tag']
            rows.append((tt, vals))
        if rows:
            rows.sort(key=lambda x: x[0])
            out[name] = rows
    return out


def sample(tracks, block, field, hour, default=None):
    """在轨道上按时刻插值（小时 → 秒 ✓）"""
    rows = tracks.get(block)
    if not rows:
        return default
    sec = float(hour) * 3600.0
    pts = [(tt, v.get(field)) for tt, v in rows if field in v]
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


def env_intensity(xml_path, hour):
    """★ 环境强度（<env> 的 i= ✓ 真值 ✓ 不是推断 ✓）"""
    tr = parse_tracks(xml_path)
    return sample(tr, 'env', 'i', hour, 0.25)


def color_at(tracks, block, hour):
    """色块的颜色（c= 打包整数 ✓）"""
    rows = tracks.get(block)
    if not rows:
        return None
    sec = float(hour) * 3600.0
    best = min(rows, key=lambda r: abs(r[0] - sec))
    for k in ('c', 'color', 'rgb'):
        if k in best[1] and isinstance(best[1][k], (int, float)):
            return _parse_color(int(best[1][k]))
    return None


def key_times():
    return dict(KEY_TAGS)


if __name__ == '__main__':
    import sys, json
    WX = (sys.argv[1] if len(sys.argv) > 1 else
          r'E:\la拆包项目\03_执行\41_还原树\Documents\gres\0000.gpk\weather\weather_ct_pve_city08_v20_pve_zhanshen01.xml')
    tr = parse_tracks(WX)
    print('解析到的色块/轨道：')
    for k, rows in tr.items():
        fields = sorted({f for _, v in rows for f in v if not f.startswith('_')})
        print('  %-14s %2d 条  字段=%s' % (k, len(rows), fields[:8]))
    print()
    for h in (0, 8, 12.5, 16, 17, 22):
        print('  时刻 %5.2fh → env.i = %.4f   fog.c=%s  fog_near.c=%s'
              % (h, env_intensity(WX, h), color_at(tr, 'fog', h), color_at(tr, 'fog_near', h)))
