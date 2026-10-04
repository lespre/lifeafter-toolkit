# -*- coding: utf-8 -*-
import sys, os, json, hashlib, struct
import zstandard as zstd
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
import gpk_npk_index as G

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\crystal_tex_located_20260921'
os.makedirs(OUT, exist_ok=True)
p = r'E:\mrzh\res.gpk'
rec, rows = G.parse_gpk(p)
base = rec.get('payload_delta_by_block')  # 或按公式
print('容器:', os.path.basename(p), '| 条目:', rec.get('entries'), '| family:', rec.get('family'), flush=True)
print('blocks:', json.dumps(rec.get('blocks'), ensure_ascii=False)[:300], flush=True)

targets = {
 0x4D2CB455231DDC0A: 'crystal_bump_n_uvva.tga',
 0xB41F9B0A404CCD02: 'crystal_caustic_uvva.tga',
 0x35AF6AE955F29891: 'crystal_reflection_uvva.tga',
 0xE2DC6958F9F38ACC: 'refraction_envmap_3.dds',
}
dctx = zstd.ZstdDecompressor()
found = {}
DELTA = G.GPK_PAYLOAD_ROW_DELTA  # 20；单块 block_base=16 → 36
if callable(rows):
    rows = rows()
for row in rows:
    # row = (序号, fid, off, comp, dec, flag)  兼容不同返回形状
    if len(row) >= 6:
        idx, fid, off, comp, dec, flag = row[0], row[1], row[2], row[3], row[4], row[5]
    else:
        continue
    try: fidv = int(fid)
    except Exception: fidv = fid
    t = targets.get(fidv)
    if t is None: continue
    deltas = rec.get('payload_delta_by_block')
    d = 16 + DELTA  # 单块
    abs_off = d + off
    with open(p,'rb') as f:
        f.seek(abs_off); blob = f.read(int(comp))
    ok=False
    if int(flag) == 12:
        try:
            out = dctx.decompressobj().decompress(blob)
            ok = True
        except Exception as e:
            out = None
    elif int(flag) == 0:
        out = blob; ok=True
    else:
        out=None
    if out is None:
        found[t] = {'fid': hex(fidv), 'off_abs': abs_off, 'error': '解压失败'}
        continue
    sha = hashlib.sha256(out).hexdigest()
    fp = os.path.join(OUT, t)
    open(fp,'wb').write(out)
    head = out[:32]
    info = {'fid': hex(fidv), 'container': p, 'row_off': off, 'off_abs': abs_off,
            'packed': int(comp), 'decoded': len(out), 'flag': int(flag),
            'sha256': sha, 'file': fp,
            'head_hex': head[:16].hex(),
            'is_dds': out[:4]==b'DDS ', 'is_tga_hint': False}
    # TGA 头：第 2 字节 = 图像类型
    if len(out) > 18:
        info['tga_image_type'] = out[2]
        info['tga_w'] = struct.unpack_from('<H', out, 12)[0]
        info['tga_h'] = struct.unpack_from('<H', out, 14)[0]
        info['tga_bpp'] = out[16]
    found[t] = info
    print('★ 提取:', t, info, flush=True)

json.dump(found, open(os.path.join(OUT,'extract_report.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('完成。命中', len(found), '/', len(targets), flush=True)
