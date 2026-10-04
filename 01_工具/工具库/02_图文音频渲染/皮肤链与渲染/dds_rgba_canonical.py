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

DX10_FMT = {98: 'bc7', 77: 'bc3', 71: 'bc1', 72: 'bc1', 83: 'bc5', 80: 'bc4', 95: 'bc6h', 96: 'bc6h',
            # ★ 2026-10-02 补全常用 DXGI（原来只有 8 个 ⇒ 其余会落到 None 变静默）
            70: 'bc1', 73: 'bc2', 74: 'bc3', 75: 'bc2', 76: 'bc3',
            78: 'bc4', 79: 'bc4', 81: 'bc4', 82: 'bc4',
            84: 'bc5', 85: 'bc5',          # BC5_SNORM
            87: 'raw_bgra', 88: 'raw_bgra', 28: 'raw_rgba', 29: 'raw_rgba',
            10: 'raw_rgba16f', 11: 'raw_rgba16f', 2: 'raw_rgba32f', 6: 'raw_rgba32f'}
DX10_FMT_UNSUPPORTED = {89: 'r8g8b8a8_snorm', 93: 'r16g16b16a16_unorm', 97: 'r16g16b16a16_float'}
# ★ 2026-10-02 引擎对标补：ATI1 原本缺失 ⇒ 327 个 .dds 全灭（实测 ValueError('unsupported uncompressed bpp=0')）
#   ATI1 = 单通道 BC4（与 ATI2=BC5 双通道对应），补上即可解。
#   ★ 另：按扩展名筛贴图会漏 .bc7/.cube —— 它们是 DDS 伪装（.bc7 的 fourcc 竟然是 DXT5）⇒ 别用扩展名筛。
FOURCC_FMT = {b'DXT1': 'bc1', b'DXT3': 'bc3', b'DXT5': 'bc3', b'ATI1': 'bc4',
              b'ATI2': 'bc5', b'BC4U': 'bc4', b'BC4S': 'bc4', b'BC5U': 'bc5', b'BC5S': 'bc5'}

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
             amask=struct.unpack_from('<I', b, 104)[0],
             # ★ 2026-10-02 新增：dwCaps2（立方体贴图判据之一）
             caps2=struct.unpack_from('<I', b, 0x6C)[0])
    d['data_off'] = 128
    d['dxgi'] = None
    # ★ 2026-10-02 修（bug #3）：未知格式【不再静默归成 uncompressed】
    #   旧行为：fourcc 不认识就一律当未压缩 ⇒ 后续按 bpp 猜通道，静默出图但内容错 ✗
    #   新行为：显式给出 unknown_fourcc:<四字节> / unknown_dxgi:<n> / unknown_pf:<flags>，
    #           调用方一眼能看出"这个没支持"，而不是拿到一张错的图。
    DDPF_FOURCC = 0x4
    if d['fourcc'] == b'DX10':
        d['dxgi'] = struct.unpack_from('<I', b, 128)[0]
        d['data_off'] = 148
        if d['dxgi'] in DX10_FMT:
            d['fmt'] = DX10_FMT[d['dxgi']]
        elif d['dxgi'] in DX10_FMT_UNSUPPORTED:
            d['fmt'] = 'unsupported_dxgi_%d' % d['dxgi']
        else:
            d['fmt'] = 'unknown_dxgi_%d' % d['dxgi']
    elif d['fourcc'] in FOURCC_FMT:
        d['fmt'] = FOURCC_FMT[d['fourcc']]
    elif d['fourcc'] == b'\x00\x00\x00\x00':
        pf = d['pf_flags']
        d['fmt'] = 'uncompressed' if (pf & _DDPF_RGB) else 'unknown_pf_0x%x' % pf
    else:
        d['fmt'] = 'unknown_fourcc_%s' % d['fourcc'].decode('latin1', 'replace').strip() or 'unknown_fourcc'
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
    """未压缩 DDS → RGBA。

    ★ 2026-10-02 引擎对标修（bug #2）：**按像素掩码取通道**，不再假定 BGRA。
      原因：旧实现写死 `a[..., [2,1,0,3]]`，只对 D3D 默认 BGRA 碰巧正确；
      实测 1,416 个未压缩文件里，掩码并不都是默认值 ⇒ 旧写法会静默换错通道。
      兼容：掩码全 0（老包偶见）时回退到旧的 BGRA 行为，保证既有成功路径不变。
    """
    w, h, off = d['w'], d['h'], d['data_off']
    bpp = d['rgbbits'] // 8
    if bpp not in (3, 4):
        raise ValueError('unsupported uncompressed bpp=%s' % bpp)
    n = w * h * bpp
    a = np.frombuffer(b[off:off + n], np.uint8).reshape(h, w, bpp)
    rmask, gmask, bmask, amask = d['rmask'], d['gmask'], d['bmask'], d['amask']
    if rmask and gmask and bmask:
        def _byte_index(mask):
            if not mask:
                return None
            # 取最低置位的位号，再换算到字节下标
            shift = (mask & -mask).bit_length() - 1
            return shift // 8
        ri, gi, bi = _byte_index(rmask), _byte_index(gmask), _byte_index(bmask)
        ai = _byte_index(amask)
        out = np.empty((h, w, 4), np.uint8)
        for ch, ix in ((0, ri), (1, gi), (2, bi)):
            out[..., ch] = a[..., ix] if (ix is not None and ix < bpp) else 0
        out[..., 3] = a[..., ai] if (ai is not None and ai < bpp) else 255
        return out
    # 掩码缺失 ⇒ 回退旧行为（不破坏既有路径）
    if bpp == 3:
        a = np.dstack([a, np.full((h, w, 1), 255, np.uint8)])
    return a[..., [2, 1, 0, 3]].copy()


# ★ 2026-10-02 新增（bug #3）：立方体贴图识别 + 六面拆分
_DDS_CAPS2_OFFSET = 0x6C          # dwCaps2
_DDSCAPS2_CUBEMAP = 0x00000200


def is_cubemap(d, file_size=None):
    """判断是否立方体贴图。

    两条判据（任一成立即可）：
      ① dwCaps2 的 CUBEMAP 位置位；
      ② 尺寸算术：file_size 恰好等于「6 面 × 单面 mip 链」（实测 .cube 文件用这条成立）。
    ⚠ 实测本树 dwCaps2 全树统一 0x401008（不含 0x200）⇒ 【不能只靠 ①】，
      所以 ② 是主要判据。
    """
    caps2 = d.get('caps2')
    if caps2 is not None and (caps2 & _DDSCAPS2_CUBEMAP):
        return True
    if file_size is None:
        return False
    w, h, mips = d['w'], d['h'], max(1, int(d.get('mips') or 1))
    fmt = d.get('fmt')
    size = 0
    for m in range(mips):
        cw, ch = max(1, w >> m), max(1, h >> m)
        if fmt in ('bc1', 'bc4'):
            blk = cw * ch // 2
        elif fmt in ('bc3', 'bc5', 'bc6h', 'bc7'):
            blk = cw * ch
        elif fmt == 'uncompressed':
            blk = cw * ch * (d['rgbbits'] // 8)
        else:
            return False
        size += max(16 if fmt in ('bc1', 'bc4', 'bc3', 'bc5', 'bc6h', 'bc7') else 1, blk)
    return file_size == size * 6


def split_cubemap(path_or_bytes):
    """立方体贴图 → 6 个单面 RGBA（返回 list[np.ndarray]，顺序 +X -X +Y -Y +Z -Z）。

    ★ 仅做「按 6 等分 + 逐面解 mip0」的保守实现：不做跨面去重、不做通道猜测，
      解不出的面返回 None（宁缺勿猜）。
    """
    b = Path(path_or_bytes).read_bytes() if isinstance(path_or_bytes, (str, os.PathLike)) \
        else bytes(path_or_bytes)
    d = parse_header(b)
    if not is_cubemap(d, len(b)):
        raise ValueError('不是立方体贴图')
    mips = max(1, int(d.get('mips') or 1))
    fmt = d.get('fmt')
    face = 0
    for m in range(mips):
        cw, ch = max(1, d['w'] >> m), max(1, d['h'] >> m)
        if fmt in ('bc1', 'bc4'):
            face += max(16, cw * ch // 2)
        elif fmt in ('bc3', 'bc5', 'bc6h', 'bc7'):
            face += max(16, cw * ch)
        elif fmt == 'uncompressed':
            face += cw * ch * (d['rgbbits'] // 8)
        else:
            raise ValueError('立方体贴图暂不支持的格式: %r' % fmt)
    faces = []
    for i in range(6):
        seg = b[d['data_off'] + i * face: d['data_off'] + (i + 1) * face]
        try:
            if fmt == 'uncompressed':
                dd = dict(d)
                dd['data_off'] = 0
                faces.append(_uncompressed_to_rgba(seg, dd))
            else:
                faces.append(_raw_decode_bgra(seg, d['w'], d['h'], fmt))
        except Exception:
            faces.append(None)
    return faces


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
