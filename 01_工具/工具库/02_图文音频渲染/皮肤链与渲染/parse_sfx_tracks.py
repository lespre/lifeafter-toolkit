# -*- coding: utf-8 -*-
"""解析 .sfx（GBK XML FxGroup）→ 完整节点树 + 变换/颜色/缩放/alpha 轨道
用于网页 SFX 适配器（独立层）。所有数值来自源 XML，不做推测。

输出结构（每节点）：
  name / tag / parent / pos_offset / start / life / radius / blend_mode / texture /
  color:  [(t,A,R,G,B)…]   scale: [(t,x)…]  smooth_start/stop: [(t,255,0,0,0)→(t,255,255,255,255)]
  emit: {sprite_scale, hw_ratio, emission_radius, gravity, velocity…}（ParticleSystem 用）
用法：python parse_sfx_tracks.py <sfx.bin> <out.json>
"""
import sys, json, os
import xml.etree.ElementTree as ET
import numpy as np

TAGS = {'Dummy', 'Sprite', 'ParticleSystem', 'Model', 'ParticleRes', 'Trail'}
KEY_TAGS = {'ColorFrame', 'ColorFramePar', 'TrackScale', 'SmoothStartFrame', 'SmoothStopFrame',
            'SpriteScaleFrame', 'SpriteHeightFrame', 'HWRatioFrame', 'EmissionRadiusFrame',
            'EmissionRadius2Frame', 'EmissionDirDegreeFrame', 'GravityFrame', 'NoiseStrengthFrame',
            'MaxSpriteVelocityFrame', 'MinSpriteVelocityFrame', 'RotDegreeSpeedFrame',
            'ScaleFrame', 'XDirDisturb', 'YDirDisturb', 'ZDirDisturb'}


def frames(el, node_name=None, track_name=None, anomalies=None):
    """显式 {time, value} 结构 + 严格校验（GPT 复核要求）：
    · 结构固定为 {"time": float, "value": [float,...]}，time 绝不混进 value
    · 校验：time 有限、value 分量数一致且全部有限
    · 异常一律**报告**（记入 anomalies），不截前 4 项、不补 0、不静默丢弃
    """
    out = []
    for f in el.iter('Frame'):
        ts, vs = f.attrib.get('Time'), f.attrib.get('Value')
        if ts is None or vs is None:
            if anomalies is not None:
                anomalies.append({'node': node_name, 'track': track_name, 'raw': dict(f.attrib),
                                  'issue': 'Frame 缺 Time 或 Value'})
            continue
        try:
            tf = float(ts)
        except ValueError:
            if anomalies is not None:
                anomalies.append({'node': node_name, 'track': track_name, 'raw': dict(f.attrib), 'issue': 'Time 非数值'})
            continue
        if not np.isfinite(tf):
            if anomalies is not None:
                anomalies.append({'node': node_name, 'track': track_name, 'raw': dict(f.attrib), 'issue': 'Time 非有限'})
            continue
        try:
            nums = [float(x) for x in vs.split(',')]
        except ValueError:
            if anomalies is not None:
                anomalies.append({'node': node_name, 'track': track_name, 'raw': dict(f.attrib), 'issue': 'Value 含非数值'})
            continue
        bad = [x for x in nums if not np.isfinite(x)]
        if bad:
            if anomalies is not None:
                anomalies.append({'node': node_name, 'track': track_name, 'raw': dict(f.attrib), 'issue': 'Value 含非有限值'})
            continue
        out.append({'time': tf, 'value': nums})
    return out


def num(v, idx=None, default=None):
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, list):
        if idx is not None and idx < len(v):
            return float(v[idx])
        return [float(x) for x in v]
    return default


def walk(el, parent, acc, anomalies=None):
    tag = el.tag
    if tag in TAGS:
        a = el.attrib
        node = {
            'name': a.get('Name'), 'tag': tag, 'parent': parent,
            'pos_offset': [float(x) for x in (a.get('PosOffset') or '0,0,0').split(',') if x != ''],
            'start': float(a.get('FxStartTime') or 0.0),
            'life': float(a.get('FxLifeSpan') or 0.0),
            'radius': float(a.get('Radius')) if a.get('Radius') else None,
            'blend_mode': int(a.get('BlendMode')) if a.get('BlendMode') else None,
            'texture': a.get('Texture'),
            'direction': a.get('Direction'),
            'dir_type': a.get('DirType'),
            'spr_work_mode': a.get('SprWorkMode'),
            'render_order': a.get('RenderOrder'),
            'tracks': {},
            'emit': {},
        }
        for ch in el:
            if ch.tag == 'TrackScale':
                for ax in ch:
                    fs = frames(ax, None, 'TrackScale/' + ax.tag, anomalies)
                    if fs:
                        node['tracks']['scale_' + ax.tag] = fs
                yz = ch.attrib.get('YZCopyFromX')
                if yz:
                    node['emit']['yz_copy_from_x'] = (yz == 'TRUE')
                node['emit']['track_scale_len'] = ch.attrib.get('TimeLen')
                node['emit']['track_scale_cycle'] = ch.attrib.get('CycleType')
            elif ch.tag in KEY_TAGS:
                fs = frames(ch)
                if fs:
                    node['tracks'][ch.tag] = fs
            elif ch.tag == 'TrackFixPoint':
                node['tracks']['fixpoint'] = ch.attrib.get('Forward')
            elif not (set(ch.attrib) == set() and len(ch) == 0):
                if ch.tag in ('ShaderComponent', 'Uniforms', 'Macros', 'Semantic', 'Variables'):
                    node.setdefault('shader', {})[ch.tag] = len(ch)
        acc.append(node)
        nxt = node['name']
    else:
        nxt = parent
    for ch in el:
        walk(ch, nxt, acc, anomalies)


def main(src, dst):
    txt = open(src, 'rb').read().decode('gbk', errors='replace')
    root = ET.fromstring(txt)
    acc = []
    anomalies = []
    walk(root, None, acc, anomalies)
    out = {
        'value_structure': '{time: float, value: [float,...]}（time 不并入 value；异常记入 anomalies）',
        'anomalies': anomalies,
        'source': os.path.basename(src),
        'root_attrib': dict(root.attrib),
        'node_count': len(acc),
        'color_key_format': 'Value = (A,R,G,B)，A 为 alpha 包络（源值直读，未归一）',
        'coord_note': 'pos_offset 为源局部坐标；节点为树状，子节点继承父节点',
        'nodes': acc,
    }
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('节点 %d → %s' % (len(acc), dst))
    for n in acc:
        ck = n['tracks'].get('ColorFrame') or n['tracks'].get('ColorFramePar') or []
        sk = n['tracks'].get('scale_XScale') or []
        print('  %-22s %-15s start=%.3f life=%.3f radius=%s blend=%s 色帧=%d 缩放帧=%d tex=%s' % (
            n['name'], n['tag'], n['start'], n['life'], n['radius'], n['blend_mode'], len(ck), len(sk),
            (os.path.basename((n['texture'] or '').replace('\\', '/'))) if n['texture'] else '-'))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
