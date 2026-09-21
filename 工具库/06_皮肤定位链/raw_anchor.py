# -*- coding: utf-8 -*-
"""raw_anchor.py — 贴图↔原始 DDS 锚定校验（provenance source_data_integrity 用）

v2（2026-09-15 · 外审 v6 修复令）:
  · 全部解码走**唯一入口** `dds_rgba_canonical`（底层 BGRA → 规范 RGBA）。
  · 锚定校验同时**检测 PNG 的通道序**：PNG 若只有 R/B 互换后才与 DDS 一致 =>
    match=False 且记录 png_channel_order='BGRA'（fail-closed，防止旧通道错误再次混入）。
  · provenance 记录: 解码器/版本、原始通道序、应用 swizzle、规范像素 sha256、OIIO 独立对照。
"""
import os, re, hashlib
import numpy as np
from PIL import Image
import dds_rgba_canonical as CAN


def decode_dds_bc7(path):
    """规范 RGBA 解码（唯一入口）。返回 uint8 HxWx4。"""
    u8, _ = CAN.decode_dds_rgba_u8(path, verify_oiio=False)
    return u8


def canonical_prov(path, verify_oiio=True):
    """规范解码 provenance（含 OIIO 独立对照）。"""
    _, prov = CAN.decode_dds_rgba_u8(path, verify_oiio=verify_oiio)
    return prov


def sha_arr(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]


def _png_u8(tex_png):
    return np.asarray(Image.open(tex_png).convert('RGBA'), np.uint8)


def _cmp(img, dds):
    """(match, maxdiff, swap_match, swap_maxdiff, png_order) —— 以规范 RGBA 为准。"""
    if img.shape != dds.shape:
        return False, None, False, None, 'unknown'
    d0 = np.abs(img.astype(np.int16) - dds.astype(np.int16)).max()
    swap = CAN.swap_rb(img)
    d1 = np.abs(swap.astype(np.int16) - dds.astype(np.int16)).max()
    order = 'RGBA' if d0 == 0 else ('BGRA' if d1 == 0 else 'unknown')
    return bool(d0 == 0), int(d0), bool(d1 == 0), int(d1), order


def _base_out(tex_png, raw_path, declared):
    out = dict(file=os.path.basename(tex_png), declared=bool(declared),
               raw_file=os.path.basename(raw_path),
               norm_path=os.path.normcase(os.path.abspath(tex_png)),
               decoder=CAN.DECODER_NAME, decoder_version=CAN.DECODER_VERSION,
               raw_channel_order=CAN.RAW_CHANNEL_ORDER, applied_swizzle=CAN.APPLIED_SWIZZLE)
    return out


def _verify(tex_png, raw_path, declared):
    out = _base_out(tex_png, raw_path, declared)
    if not os.path.exists(raw_path):
        out.update(match='no_raw', reason='原始 DDS 不存在: %s' % raw_path)
        return out
    try:
        dds, prov = CAN.decode_dds_rgba_u8(raw_path, verify_oiio=True)
    except Exception as e:
        out.update(match=False, reason='原始 DDS 解码失败: %r' % e)
        return out
    img = _png_u8(tex_png)
    out['sha256'] = sha_arr(img)
    out['raw_sha256'] = sha_arr(dds)
    out['canonical_pixel_sha256'] = prov.get('canonical_pixel_sha256')
    out['dds_sha256'] = prov.get('dds_sha256')
    oc = prov.get('oiio_crosscheck') or {}
    out['oiio_crosscheck_ok'] = oc.get('ok')
    out['oiio_maxdiff'] = oc.get('maxdiff')
    match, d0, smatch, d1, order = _cmp(img, dds)
    out['maxdiff'] = d0
    out['png_channel_order'] = order
    if match:
        out['match'] = True
        return out
    out['match'] = False
    if smatch:
        out.update(reason='PNG 通道序为 BGRA（R/B 互换后与 DDS 一致，maxdiff=0）——'
                          '须以 dds_rgba_canonical 重新导出贴图',
                   swap_maxdiff=d1, png_is_bgra=True)
    else:
        out['reason'] = '像素与原始 DDS 不一致 (maxdiff=%s, swapped=%s)' % (d0, d1)
    return out


def verify_texture_vs_raw(tex_png, raw_dir):
    base = os.path.basename(tex_png)
    m = re.search(r'(\d{4,6})', base)
    fid = m.group(1).zfill(6) if m else None
    if fid is None:
        return dict(file=base, fid=None, match=False, reason='无法从文件名提取资源号')
    raw = None
    for cand in (fid + '.dds', fid + '.DDS'):
        p = os.path.join(raw_dir, cand)
        if os.path.exists(p):
            raw = p
            break
    if raw is None:
        out = _base_out(tex_png, fid + '.dds', False)
        out.update(fid=fid, match='no_raw', reason='原始 DDS 未找到')
        return out
    out = _verify(tex_png, raw, declared=False)
    out['fid'] = fid
    out['raw_dir'] = os.path.abspath(raw_dir)
    return out


def verify_texture_vs_declared(tex_png, dds_path):
    """按 _input_manifest.json 声明的来源 DDS 锚定（替代按文件名推源）。"""
    out = _verify(tex_png, dds_path, declared=True)
    if out.get('match') == 'no_raw':
        out['reason'] = '声明来源不存在: %s' % dds_path
    return out


if __name__ == '__main__':
    import sys
    W = r'E:\la拆包项目\03拆包产物\weapon'
    D = r'E:\la拆包项目\03拆包产物\render_jiguangjian'
    for fid in ('4009', '4010', '4011', '4012', '4013'):
        r = verify_texture_vs_raw(os.path.join(D, 'tex_%s.png' % fid), W)
        print(fid, r.get('match'), r.get('maxdiff', '-'), r.get('png_channel_order'), r.get('reason', ''))
