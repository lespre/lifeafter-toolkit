# -*- coding: utf-8 -*-
"""深度解析weapon_skin_data.nxs，尝试提取武器皮肤配置数据"""
import sys, os, struct, marshal, dis, json

skin_path = r'E:\提取成果\拆包产物\_nxs配置\weapon_skin_data.nxs'

with open(skin_path, 'rb') as f:
    raw = f.read()

print(f'文件大小: {len(raw):,} bytes')
print()

# 分析文件结构
print('=== 文件结构分析 ===')
# 前6字节
print(f'偏移0-5: {raw[:6].hex()}')
# 路径字符串
path_start = 6
path_end = raw.find(b'.py', path_start) + 3
print(f'路径字符串(偏移{path_start}-{path_end}): {raw[path_start:path_end]}')

# 路径后的数据
after_path = raw[path_end:]
print(f'路径后数据前32字节: {after_path[:32].hex()}')
print(f'路径后数据长度: {len(after_path)}')

# 尝试从不同偏移量marshal加载
print()
print('=== 尝试marshal加载（多个偏移量）===')
for offset in range(path_end, min(path_end+50, len(raw))):
    try:
        obj = marshal.loads(raw[offset:])
        print(f'  偏移{offset}: 成功! 类型={type(obj).__name__}')
        if isinstance(obj, int):
            print(f'    值={obj}')
        elif isinstance(obj, str):
            print(f'    值={obj[:100]}')
        elif hasattr(obj, 'co_consts'):
            print(f'    code对象: {obj.co_name}')
            print(f'    co_consts数量: {len(obj.co_consts)}')
            print(f'    co_names数量: {len(obj.co_names)}')
            print(f'    co_names: {obj.co_names[:30]}')
        break
    except Exception as e:
        pass

# 尝试连续marshal加载（可能是多个对象序列）
print()
print('=== 尝试连续marshal加载 ===')
import io
offset = path_end
loaded = []
while offset < len(raw):
    try:
        obj = marshal.loads(raw[offset:])
        loaded.append((offset, obj))
        # 计算这个对象占用的字节数
        # marshal没有直接的方法，我们尝试重新序列化来比较
        try:
            serialized = marshal.dumps(obj)
            offset += len(serialized)
        except:
            break
    except:
        offset += 1

print(f'成功加载 {len(loaded)} 个对象')
for i, (off, obj) in enumerate(loaded[:20]):
    print(f'  [{i}] 偏移{off}: 类型={type(obj).__name__}', end='')
    if isinstance(obj, int):
        print(f', 值={obj}')
    elif isinstance(obj, str):
        print(f', 值={obj[:50]}')
    elif isinstance(obj, bytes):
        print(f', 长度={len(obj)}')
    elif hasattr(obj, 'co_consts'):
        print(f', code={obj.co_name}, consts={len(obj.co_consts)}')
    else:
        print()

# 如果找到code对象，反汇编它
print()
print('=== 反汇编code对象 ===')
for off, obj in loaded:
    if hasattr(obj, 'co_consts'):
        print(f'code对象: {obj.co_name}')
        print(f'co_filename: {obj.co_filename}')
        print(f'co_firstlineno: {obj.co_firstlineno}')
        print(f'co_names: {obj.co_names}')
        print(f'co_varnames: {obj.co_varnames}')
        print()
        print('常量:')
        for i, c in enumerate(obj.co_consts):
            if isinstance(c, str):
                print(f'  [{i}] str: {c[:100]}')
            elif isinstance(c, (int, float)):
                print(f'  [{i}] {type(c).__name__}: {c}')
            elif hasattr(c, 'co_consts'):
                print(f'  [{i}] code: {c.co_name}')
            elif isinstance(c, bytes):
                print(f'  [{i}] bytes: {len(c)} bytes')
            else:
                print(f'  [{i}] {type(c).__name__}: {str(c)[:100]}')
        print()
        print('字节码（前100条指令）:')
        try:
            instructions = list(dis.get_instructions(obj))
            for i, inst in enumerate(instructions[:100]):
                print(f'  {i:3d}: {inst.opname:20s} {inst.argrepr}')
        except Exception as e:
            print(f'  反汇编失败: {e}')
        break
