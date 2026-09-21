# -*- coding: utf-8 -*-
"""分析weapon.gpk中95个大纹理，识别铠甲勇士武器皮肤"""
import sys, os, struct, json

weapon_dir = r'E:\提取成果\拆包产物\weapon'
preview_dir = r'E:\提取成果\拆包产物\_武器纹理预览\铠甲勇士武器皮肤集'
os.makedirs(preview_dir, exist_ok=True)

# 获取所有大于5MB的dds文件
big_dds = []
for f in os.listdir(weapon_dir):
    if f.endswith('.dds'):
        fpath = os.path.join(weapon_dir, f)
        size = os.path.getsize(fpath)
        if size > 5 * 1024 * 1024:
            big_dds.append((f, size, fpath))

big_dds.sort(key=lambda x: x[0])
print(f'=== weapon.gpk中大于5MB的dds纹理: {len(big_dds)}个 ===')

# 分析每个dds的头部信息
print()
print('=== DDS纹理头部分析 ===')
dds_info = []
for f, size, fpath in big_dds:
    with open(fpath, 'rb') as fh:
        header = fh.read(128)
    
    # DDS格式解析
    if header[:4] != b'DDS ':
        print(f'  {f}: 不是标准DDS格式 (头部={header[:4].hex()})')
        continue
    
    # 解析DDS头部
    height = struct.unpack_from('<I', header, 12)[0]
    width = struct.unpack_from('<I', header, 16)[0]
    pitch = struct.unpack_from('<I', header, 20)[0]
    depth = struct.unpack_from('<I', header, 24)[0]
    mipmaps = struct.unpack_from('<I', header, 28)[0]
    
    # 像素格式
    pf_size = struct.unpack_from('<I', header, 76)[0]
    pf_flags = struct.unpack_from('<I', header, 80)[0]
    pf_fourcc = header[84:88].decode('ascii', errors='ignore')
    pf_rgb_bitcount = struct.unpack_from('<I', header, 88)[0]
    
    info = {
        'file': f,
        'size': size,
        'width': width,
        'height': height,
        'mipmaps': mipmaps,
        'format': pf_fourcc if pf_fourcc.strip() else f'RGB{pf_rgb_bitcount}',
        'pitch': pitch,
    }
    dds_info.append(info)
    
    print(f'  {f}: {width}x{height}, {mipmaps} mipmaps, 格式={info["format"]}, 大小={size/1024/1024:.1f}MB')

# 按尺寸分组
print()
print('=== 按尺寸分组 ===')
size_groups = {}
for info in dds_info:
    key = f'{info["width"]}x{info["height"]}'
    if key not in size_groups:
        size_groups[key] = []
    size_groups[key].append(info)

for size_key, infos in sorted(size_groups.items()):
    print(f'  {size_key}: {len(infos)}个')
    files = [info['file'] for info in infos]
    print(f'    文件: {files[0]} ~ {files[-1]}')

# 转换前20个大纹理为png预览
print()
print('=== 转换前20个大纹理为PNG预览 ===')
sys.path.insert(0, r'E:\提取成果\明日拆包\工具库\01_核心解包器')
import lifeafter_unpacker_full as unpacker

converted = 0
for info in dds_info[:20]:
    fpath = os.path.join(weapon_dir, info['file'])
    outpath = os.path.join(preview_dir, info['file'].replace('.dds', '.png'))
    try:
        unpacker.dds2png(fpath, outpath)
        print(f'  转换成功: {info["file"]} -> {info["file"].replace(".dds", ".png")}')
        converted += 1
    except Exception as e:
        print(f'  转换失败: {info["file"]} - {e}')

print(f'\n成功转换 {converted}/20 个纹理')
print(f'预览目录: {preview_dir}')

# 保存纹理信息到JSON
info_path = os.path.join(preview_dir, '纹理信息.json')
with open(info_path, 'w', encoding='utf-8') as f:
    json.dump(dds_info, f, ensure_ascii=False, indent=2)
print(f'纹理信息已保存: {info_path}')
