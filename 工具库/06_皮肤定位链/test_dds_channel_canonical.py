# -*- coding: utf-8 -*-
"""test_dds_channel_canonical.py — 通道序规范化测试（外审 v6 强制项 · 非自证循环）

原则:
  · 期望值**只来自独立实现**（OpenImageIO）或**语义先验**（法线图 B 高值），
    绝不用 texture2ddecoder 自身生成期望值。
  · 覆盖: ①合成贴图（通道值互异）②真实资产逐通道交叉解码一致性 ③语义断言 ④旧 BGRA 序必须被检出。

运行: python test_dds_channel_canonical.py   (exit 0 = 全过)
"""
import os, sys, struct, hashlib
import numpy as np
import dds_rgba_canonical as CAN

W = r'E:\la拆包项目\03拆包产物\weapon'
OUT = r'E:\la拆包项目\03拆包产物\render_1003_010\_tests'
os.makedirs(OUT, exist_ok=True)
FAILS = []


def check(name, cond, detail=''):
    print('%-4s | %-46s | %s' % ('PASS' if cond else 'FAIL', name, detail))
    if not cond:
        FAILS.append(name)


def oiio_read(path):
    import OpenImageIO as oiio
    img = oiio.ImageInput.open(path)
    spec = img.spec()
    a = np.array(img.read_image(format='float')).reshape(spec.height, spec.width, spec.nchannels)
    img.close()
    return a


# ---------- ① 合成贴图：通道值互异 (R=0.1 G=0.3 B=0.7 A=0.9) ----------
print('== ① 合成贴图 ==')
synt_dds = os.path.join(OUT, 'synthetic_rgba_uncompressed.dds')
vals = np.array([26, 77, 179, 230], np.uint8)  # ≈0.1/0.3/0.7/0.9
w = h = 8
pix = np.tile(vals.reshape(1, 1, 4), (h, w, 1)).astype(np.uint8)
# 手写 DDS（未压缩 RGBA8, D3D 约定字节序 BGRA）
hdr = bytearray(128)
hdr[0:4] = b'DDS '
struct.pack_into('<I', hdr, 4, 124)
struct.pack_into('<I', hdr, 8, 0x1 | 0x2 | 0x4 | 0x1000)      # CAPS|HEIGHT|WIDTH|PIXELFORMAT
struct.pack_into('<I', hdr, 12, h)
struct.pack_into('<I', hdr, 16, w)
struct.pack_into('<I', hdr, 28, 1)                             # mipmapcount
struct.pack_into('<I', hdr, 76, 32)                            # pf size
struct.pack_into('<I', hdr, 80, 0x41)                          # RGB|ALPHAPIXELS
struct.pack_into('<I', hdr, 88, 32)                            # bits
struct.pack_into('<I', hdr, 92, 0x00FF0000)                    # R mask
struct.pack_into('<I', hdr, 96, 0x0000FF00)                    # G mask
struct.pack_into('<I', hdr, 100, 0x000000FF)                   # B mask
struct.pack_into('<I', hdr, 104, 0xFF000000)                   # A mask
struct.pack_into('<I', hdr, 108, 0x1000)
payload = pix[..., [2, 1, 0, 3]].tobytes()                     # 存为 BGRA 字节
open(synt_dds, 'wb').write(bytes(hdr) + payload)
u8, prov = CAN.decode_dds_rgba_u8(synt_dds, verify_oiio=True)
check('合成贴图 规范RGBA == 期望(R0.1/G0.3/B0.7/A0.9)',
      np.array_equal(u8[0, 0], vals), 'got %s' % u8[0, 0].tolist())
ref = oiio_read(synt_dds)
check('合成贴图 与 OIIO 独立解码一致(逐通道 maxdiff<=2)',
      np.abs(np.round(ref[0, 0, :4] * 255) - vals).max() <= 2, 'OIIO=%s' % np.round(ref[0, 0, :4] * 255).tolist())
check('合成贴图 OIIO 对照 ok', (prov.get('oiio_crosscheck') or {}).get('ok') in (True,), str(prov.get('oiio_crosscheck')))

# 尝试合成 BC7（离线无编码器则记录并提供替代证据）
bc7_note = 'skipped: no offline BC7 encoder available'
try:
    import OpenImageIO as oiio
    spec = oiio.ImageSpec(w, h, 4, 'uint8')
    spec.attribute('dds:compression', 'bc7')
    op = oiio.ImageOutput.create(os.path.join(OUT, 'synthetic_bc7.dds'))
    ok = bool(op and op.open(os.path.join(OUT, 'synthetic_bc7.dds'), spec) and op.write_image(ref))
    if ok:
        op.close()
        b = open(os.path.join(OUT, 'synthetic_bc7.dds'), 'rb').read()
        if b[84:88] == b'DX10' and struct.unpack_from('<I', b, 128)[0] == 98:
            bc7_note = 'OIIO 写出 BC7 成功'
        else:
            bc7_note = 'OIIO 伪 BC7（dxgi=%s）' % (struct.unpack_from('<I', b, 128)[0] if b[84:88] == b'DX10' else b[84:88])
except Exception as e:
    bc7_note = 'BC7 合成失败: %r' % e
print('     [note] 合成 BC7: %s' % bc7_note)

# ---------- ② 真实资产：逐通道交叉解码一致性（期望值来自 OIIO） ----------
print('== ② 真实资产交叉解码一致性（期望值仅来自 OIIO）==')
assets = ['001224', '001225', '001226', '001227', '001228', '001229',
          '003991', '003992', '003993', '004009', '004010', '004011', '004012', '004013']
worst = 0.0
for f in assets:
    p = os.path.join(W, f + '.dds')
    if not os.path.exists(p):
        continue
    u8, prov = CAN.decode_dds_rgba_u8(p, verify_oiio=True)
    oc = prov.get('oiio_crosscheck') or {}
    md = oc.get('maxdiff')
    worst = max(worst, md or 0)
    check('%s 规范RGBA ≡ OIIO (maxdiff %s)' % (f, md), oc.get('ok') is True,
          'per_ch=%s' % (oc.get('per_channel_maxdiff'),))
print('     [note] 最大逐通道差异 = %s (BC7 两个独立实现应逐位一致)' % worst)

# ---------- ③ 语义断言（先验） ----------
print('== ③ 语义断言 ==')
def stats(f):
    u8, _ = CAN.decode_dds_rgba_u8(os.path.join(W, f + '.dds'), verify_oiio=False)
    a = u8.astype(np.float32) / 255.0
    return a, [float(a[:, :, c].mean()) for c in range(4)]
a, m = stats('001227')
check('001227 法线图签名 R/G≈0.5, B 高', abs(m[0] - 0.5) < 0.05 and abs(m[1] - 0.5) < 0.05 and m[2] > 0.9, 'mean=%s' % np.round(m, 3).tolist())
a, m = stats('004012')
check('004012 法线图签名 R/G≈0.5, B 高', abs(m[0] - 0.5) < 0.05 and abs(m[1] - 0.5) < 0.05 and m[2] > 0.9, 'mean=%s' % np.round(m, 3).tolist())
a, m = stats('001228')
var = [float(a[:, :, c].std()) for c in range(4)]
check('001228 仅 R 变化 (G/B/A 常量)', var[0] > 0.05 and max(var[1:]) < 0.01, 'std=%s' % np.round(var, 4).tolist())
a, m = stats('004013')
var = [float(a[:, :, c].std()) for c in range(4)]
check('004013 仅 R 变化 (G/B/A 常量)', var[0] > 0.05 and max(var[1:]) < 0.01, 'std=%s' % np.round(var, 4).tolist())

# ---------- ④ 旧 BGRA 序必须被检出 ----------
print('== ④ 旧通道序检测 ==')
u8, _ = CAN.decode_dds_rgba_u8(os.path.join(W, '001228.dds'), verify_oiio=False)
old = CAN.swap_rb(u8)  # 模拟旧管线（BGRA 当 RGBA 用）
var_old = [float(old[:, :, c].std()) for c in range(4)]
check('旧 BGRA 序下 001228 变为"仅第3通道变化"（即旧管线误读）',
      var_old[2] > 0.05 and max(var_old[:2] + var_old[3:]) < 0.01, 'std=%s' % np.round(var_old, 4).tolist())

print()
if FAILS:
    print('FAILED %d: %s' % (len(FAILS), FAILS))
    sys.exit(1)
print('ALL PASS')
