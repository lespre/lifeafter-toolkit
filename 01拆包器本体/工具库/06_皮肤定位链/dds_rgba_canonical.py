# -*- coding: utf-8 -*-
"""dds_rgba_canonical.py — 唯一 DDS → 规范 RGBA 解码入口（外审 v6 修复令 · 强制唯一入口）

规则（不可绕过）:
  1. 底层 `texture2ddecoder` 的 BCn 输出通道序为 **BGRA**（实证 2026-09-15: our_ch0≡OIIO_ch2, maxdiff 0.0000）。
  2. 本入口**立即**执行 R↔B 交换，输出规范 RGBA。
  3. 全工具链（渲染器 / 分析器 / raw_anchor / 因果实验 / GLB 导出 / 3D Wiki 预览）
     **只能**使用本入口；任何工具不得自行决定是否交换通道。
  4. provenance 必录: 原始 DDS sha256 · 解码器名+版本 · 原始输出通道序 · 应用 swizzle ·
     规范 RGBA 像素 sha256 · OpenImageIO 独立对照(maxdiff/ok)。

用法（库）:
    import dds_rgba_canonical as CAN
    u8, prov  = CAN.decode_dds_rgba_u8(dds_path)          # uint8 HxWx4 规范RGBA
    f32, prov = CAN.decode_dds_rgba_float(dds_path)        # float32 0..1 规范RGBA
    u8, prov  = CAN.decode_bcn_bytes_canonical(data)       # 内存字节（toolkit_core 用）
"""
import os, struct, hashlib
import numpy as np
import texture2ddecoder as _t2d

DECODER_NAME = 'texture2ddecoder'
try:
    from importlib.metadata import version as _ver
    DECODER_VERSION = _ver('texture2ddecoder')
except Exception:
    DECODER_VERSION = 'unknown'
RAW_CHANNEL_ORDER = 'BGRA'
APPLIED_SWIZZLE = 'BGRA->RGBA'

DX10_FMT = {98: 'bc7', 77: 'bc3', 71: 'bc1', 72: 'bc1', 83: 'bc5', 80: 'bc4', 95: 'bc6h', 96: 'bc6h'}
FOURCC_FMT = {b'DXT1': 'bc1', b'DXT3': 'bc3', b'DXT5': 'bc3', b'ATI2': 'bc5',
              b'BC4U': 'bc4', b'BC4S': 'bc4', b'BC5U': 'bc5', b'BC5S': 'bc5'}

# DDS header flags / masks (未压缩路径)
_DDPF_RGB = 0x40
_DDPF_RGBA = 0x41


def parse_header(b):
    if b[:4] != b'DDS ':
        raise ValueError('not a DDS file')
    d = dict(size=struct.unpack_from('<I', b, 4)[0],
             h=struct.unpack_from('<I', b, 12)[0],
             w=struct.unpack_from('<I', b, 16)[0],
             mips=struct.unpack_from('<I', b, 28)[0],
             pf_flags=struct.unpack_from('<I', b, 80)[0],
             fourcc=b[84:88],
             rgbbits=struct.unpack_from('<I', b, 88)[0],
             rmask=struct.unpack_from('<I', b, 92)[0],
             gmask=struct.unpack_from('<I', b, 96)[0],
             bmask=struct.unpack_from('<I', b, 100)[0],
             amask=struct.unpack_from('<I', b, 104)[0])
    d['data_off'] = 128
    d['dxgi'] = None
    if d['fourcc'] == b'DX10':
        d['dxgi'] = struct.unpack_from('<I', b, 128)[0]
        d['data_off'] = 148
        d['fmt'] = DX10_FMT.get(d['dxgi'])
    elif d['fourcc'] in FOURCC_FMT:
        d['fmt'] = FOURCC_FMT[d['fourcc']]
    else:
        d['fmt'] = 'uncompressed'
    return d


def _raw_decode_bgra(data, w, h, fmt):
    """底层解码（保持库的原始通道序 BGRA）。"""
    if fmt == 'bc7':
        px = _t2d.decode_bc7(data, w, h)
    elif fmt == 'bc3':
        px = _t2d.decode_bc3(data, w, h)
    elif fmt == 'bc1':
        px = _t2d.decode_bc1(data, w, h)
    elif fmt == 'bc5':
        px = _t2d.decode_bc5(data, w, h)
    elif fmt == 'bc4':
        px = _t2d.decode_bc4(data, w, h)
    elif fmt == 'bc6h':
        px = _t2d.decode_bc6(data, w, h)
    else:
        raise ValueError('unsupported BC format: %r' % fmt)
    return np.frombuffer(px, np.uint8).reshape(h, w, 4)


def _uncompressed_to_rgba(b, d):
    w, h, off = d['w'], d['h'], d['data_off']
    bpp = d['rgbbits'] // 8
    if bpp not in (3, 4):
        raise ValueError('unsupported uncompressed bpp=%s' % bpp)
    n = w * h * bpp
    a = np.frombuffer(b[off:off + n], np.uint8).reshape(h, w, bpp)
    if bpp == 3:
        a = np.dstack([a, np.full((h, w, 1), 255, np.uint8)])
    # D3D DDS 未压缩默认 BGR(A) 顺序（与 BCn 一致）
    return a[..., [2, 1, 0, 3]].copy()


def swap_rb(a):
    """BGRA -> RGBA（唯一允许的通道交换实现）。"""
    return np.ascontiguousarray(a[..., [2, 1, 0, 3]])


def pixel_sha256(u8):
    return hashlib.sha256(np.ascontiguousarray(u8, dtype=np.uint8).tobytes()).hexdigest()


def _prov_base(path=None, data=None):
    p = dict(decoder=DECODER_NAME, decoder_version=DECODER_VERSION,
             raw_channel_order=RAW_CHANNEL_ORDER, applied_swizzle=APPLIED_SWIZZLE,
             canonical_channel_order='RGBA')
    if path is not None:
        b = open(path, 'rb').read()
        p['dds_path'] = os.path.abspath(path)
        p['dds_sha256'] = hashlib.sha256(b).hexdigest()
        p['dds_bytes'] = len(b)
    elif data is not None:
        p['dds_sha256'] = hashlib.sha256(bytes(data)).hexdigest()
        p['dds_bytes'] = len(data)
    return p


def oiio_crosscheck(path, u8_canonical):
    """OpenImageIO 独立解码对照（非同一解码实现）。返回 dict(ok, maxdiff, per_channel)。"""
    out = dict(decoder='OpenImageIO', ok=None)
    try:
        import OpenImageIO as oiio
        img = oiio.ImageInput.open(str(path))
        if not img:
            out['error'] = 'oiio open failed'; return out
        spec = img.spec()
        arr = np.array(img.read_image(format='float')).reshape(spec.height, spec.width, spec.nchannels)
        img.close()
        if arr.shape[2] >= 4 and u8_canonical.shape[0] == arr.shape[0] and u8_canonical.shape[1] == arr.shape[1]:
            ref = np.clip(np.round(arr[:, :, :4] * 255.0), 0, 255)
            d = np.abs(ref - u8_canonical.astype(np.float64))
            out['maxdiff'] = float(d.max())
            out['per_channel_maxdiff'] = [float(d[:, :, c].max()) for c in range(4)]
            out['ok'] = bool(d.max() <= 2.0)
        else:
            out['ok'] = None
            out['error'] = 'shape mismatch oiio=%s canonical=%s' % (arr.shape, u8_canonical.shape)
    except Exception as e:
        out['error'] = repr(e)
    return out


def decode_bcn_bytes_canonical(data, verify_oiio_path=None):
    d = parse_header(data)
    if d['fmt'] == 'uncompressed':
        raw = _uncompressed_to_rgba(data, d)
        canon = raw  # 已在 _uncompressed_to_rgba 内交换
    else:
        raw = _raw_decode_bgra(data[d['data_off']:], d['w'], d['h'], d['fmt'])
        canon = swap_rb(raw)
    prov = _prov_base(data=data)
    prov.update(width=d['w'], height=d['h'], mips=d['mips'], fmt=d['fmt'], dxgi=d['dxgi'])
    prov['canonical_pixel_sha256'] = pixel_sha256(canon)
    if verify_oiio_path:
        prov['oiio_crosscheck'] = oiio_crosscheck(verify_oiio_path, canon)
    return canon, prov


def decode_dds_rgba_u8(path, verify_oiio=True):
    data = open(path, 'rb').read()
    canon, prov = decode_bcn_bytes_canonical(data)
    prov['dds_path'] = os.path.abspath(path)
    if verify_oiio:
        prov['oiio_crosscheck'] = oiio_crosscheck(path, canon)
    return canon, prov


def decode_dds_rgba_float(path, verify_oiio=False):
    canon, prov = decode_dds_rgba_u8(path, verify_oiio=verify_oiio)
    return canon.astype(np.float32) / 255.0, prov


CANON = dict(decoder=DECODER_NAME, version=DECODER_VERSION,
             raw_channel_order=RAW_CHANNEL_ORDER, swizzle=APPLIED_SWIZZLE)

if __name__ == '__main__':
    import sys, json
    for p in sys.argv[1:]:
        u8, prov = decode_dds_rgba_u8(p)
        print(json.dumps(prov, ensure_ascii=False, indent=1))
