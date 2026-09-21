# -*- coding: utf-8 -*-
"""搜索所有武器皮肤模型路径，分析命名规则"""
import sys, os, re, runpy, json

sys.path.insert(0, r'E:\提取成果\明日拆包\工具库\05_BinDict解码器')

# 加载all_equips解码器
_LIB = r'E:\提取成果\明日拆包\工具库\05_BinDict解码器\bindict_lib\decode_current_all_equips_D6_scalar_006.py'
M = runpy.run_path(str(_LIB), run_name='search')
ver, n, src = M['unpack_members']()
slots = M['strings'](src[M['CHS']]['body'])

print('=== 1. 搜索所有包含mod_skin的路径 ===')
mod_skin_paths = []
for i, s in enumerate(slots):
    if 'mod_skin' in s.lower() or ('skin' in s.lower() and '.gim' in s.lower()):
        mod_skin_paths.append((i, s))
        print(f'  slot[{i}] = {s}')
print(f'总计: {len(mod_skin_paths)}个mod_skin路径')

print()
print('=== 2. 搜索所有包含weapon_skin或skin的字符串 ===')
skin_strings = []
for i, s in enumerate(slots):
    if 'weapon_skin' in s.lower() or ('skin' in s.lower() and len(s) < 100):
        skin_strings.append((i, s))
        print(f'  slot[{i}] = {s}')
print(f'总计: {len(skin_strings)}个skin字符串')

print()
print('=== 3. 分析mod_skin路径命名规则 ===')
# 从路径中提取武器ID和皮肤名称
for i, path in mod_skin_paths:
    # 匹配 mod_skin_<武器ID>_<皮肤名>_<编号>.gim
    match = re.search(r'mod_skin_(\d+)_(\w+)_(\d+)', path, re.IGNORECASE)
    if match:
        weapon_id = match.group(1)
        skin_name = match.group(2)
        index = match.group(3)
        print(f'  武器ID={weapon_id}, 皮肤名={skin_name}, 编号={index}')
    else:
        print(f'  无法解析: {path}')

print()
print('=== 4. 搜索effect/mesh/weapon目录下的所有模型 ===')
effect_weapon_models = []
for i, s in enumerate(slots):
    if 'effect/mesh/weapon' in s.lower() or 'effect\\mesh\\weapon' in s.lower():
        effect_weapon_models.append((i, s))
        print(f'  slot[{i}] = {s}')
print(f'总计: {len(effect_weapon_models)}个effect/mesh/weapon模型')

print()
print('=== 5. 搜索包含铠甲勇士关键词的模型路径 ===')
armor_keywords = ['dihuang', 'xingtian', 'feiying', 'jiguang', 'zhanshen', 'caijue', 'jiying', 'kaijia']
for i, s in enumerate(slots):
    if any(kw in s.lower() for kw in armor_keywords):
        if len(s) < 200:
            print(f'  slot[{i}] = {s}')

print()
print('=== 6. 查看weapon_skin_data.nxs的详细二进制结构 ===')
skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'
with open(skin_path, 'rb') as f:
    raw = f.read()

# 从偏移35开始，分析marshal数据
print(f'文件大小: {len(raw)} bytes')
print(f'偏移35开始的前64字节: {raw[35:99].hex()}')

# 尝试用marshal连续加载，记录每个对象的类型和值
import marshal
offset = 35
objects = []
while offset < len(raw):
    try:
        obj = marshal.loads(raw[offset:])
        # 计算序列化后的长度
        try:
            serialized = marshal.dumps(obj)
            obj_len = len(serialized)
        except:
            obj_len = 0
        objects.append((offset, type(obj).__name__, obj, obj_len))
        if obj_len > 0:
            offset += obj_len
        else:
            offset += 1
    except:
        offset += 1

print(f'成功加载 {len(objects)} 个对象')
print()
print('对象列表（前50个）:')
for i, (off, typ, val, length) in enumerate(objects[:50]):
    val_str = str(val)[:60]
    print(f'  [{i:2d}] 偏移{off:5d} 长度{length:4d} {typ:10s} = {val_str}')

# 查找字符串对象
print()
print('字符串对象:')
for i, (off, typ, val, length) in enumerate(objects):
    if typ == 'str' and len(val) > 1:
        print(f'  [{i}] 偏移{off} = {repr(val[:100])}')

# 查找code对象
print()
print('code对象:')
for i, (off, typ, val, length) in enumerate(objects):
    if hasattr(val, 'co_consts'):
        print(f'  [{i}] 偏移{off} = code: {val.co_name}, consts={len(val.co_consts)}, names={len(val.co_names)}')
