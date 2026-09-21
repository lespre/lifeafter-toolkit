# -*- coding: utf-8 -*-
"""
gpk包内定向提取器（多进程优化版）
自动识别CPU核心数，使用80%核心并行加速。
用法: python gpk_targeted_extract.py <gpk文件名> <关键词1> [关键词2] ...
"""
from __future__ import annotations
import struct, sys, os, json, time
from pathlib import Path
from multiprocessing import Pool, cpu_count, Manager
from Crypto.Cipher import AES

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import la_unpack_core as core

KEY = bytes.fromhex('606308D8A32C782013D26C2F226F686D')
GPK_DIR = Path(r'E:/mrzh')
OUT_ROOT = Path(r'E:/la拆包项目/03拆包产物/_gpk_extract')   # 改写到项目产物目录（不越写盘红线）

# 自动识别CPU，智能调度
CPU_COUNT = cpu_count() or 8
MAX_WORKER_RATIO = 0.8  # 最高使用80%核心
CPU_USAGE_THRESHOLD = 70  # CPU使用率超过70%时减少worker

def get_smart_worker_count():
    """智能计算worker数量：检测CPU使用率和其他进程，动态调整。"""
    base_workers = max(1, int(CPU_COUNT * MAX_WORKER_RATIO))
    
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 检测其他Python进程的CPU占用
        other_python_cpu = 0
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    if proc.info['pid'] != os.getpid():
                        other_python_cpu += proc.info['cpu_percent'] or 0
            except:
                pass
        
        print(f'  [智能调度] CPU核心数: {CPU_COUNT}, 当前CPU使用率: {cpu_percent}%, 其他Python进程CPU: {other_python_cpu:.1f}%')
        
        # 根据CPU使用率动态调整
        if cpu_percent > 90:
            workers = max(1, int(CPU_COUNT * 0.2))
            print(f'  [智能调度] CPU使用率过高({cpu_percent}%)，仅用 {workers} 个进程')
        elif cpu_percent > 80:
            workers = max(1, int(CPU_COUNT * 0.4))
            print(f'  [智能调度] CPU使用率较高({cpu_percent}%)，用 {workers} 个进程')
        elif cpu_percent > CPU_USAGE_THRESHOLD:
            workers = max(1, int(CPU_COUNT * 0.6))
            print(f'  [智能调度] CPU使用率中等({cpu_percent}%)，用 {workers} 个进程')
        else:
            workers = base_workers
            print(f'  [智能调度] CPU空闲({cpu_percent}%)，用 {workers} 个进程 (80%)')
        
        return workers
    except ImportError:
        print(f'  [智能调度] psutil未安装，默认用 {base_workers} 个进程 (80%)')
        return base_workers
    except Exception as e:
        print(f'  [智能调度] 检测失败: {e}，默认用 {base_workers} 个进程')
        return base_workers

WORKER_COUNT = get_smart_worker_count()
BATCH_SIZE = 500  # 每个worker一次处理的条目数

def aes_ecb(data):
    pad = (16 - len(data) % 16) % 16
    return AES.new(KEY, AES.MODE_ECB).decrypt(data + b'\x00' * pad)[:len(data)]

def detect_type(data):
    if data[:4] == b'DDS ': return 'dds'
    elif data[:8] == b'\x89PNG\r\n\x1a\n': return 'png'
    elif data[:4] == b'RIFF': return 'riff'
    elif data[:4] == b'FSB5': return 'fsb'
    elif data[:4] == b'RGIS': return 'rgis'
    elif len(data) > 0 and data[0] == 0x1b: return 'lua'
    else: return 'bin'

MAX_FILE_SIZE = 20 * 1024 * 1024  # 最大保存20MB，超过的只记录不保存

def has_readable_chinese(data):
    """检查数据是否包含可读的中文文本（避免二进制误命中）。"""
    try:
        text = data.decode('utf-8', errors='ignore')
        # 统计中文字符比例
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_count > 10:  # 至少10个中文字符
            return True
    except:
        pass
    
    try:
        text = data.decode('gbk', errors='ignore')
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_count > 10:
            return True
    except:
        pass
    
    return False

def search_in_data(data, keywords, encodings=('utf-8', 'gbk', 'utf-16-le')):
    hits = {}
    for kw in keywords:
        for enc in encodings:
            try:
                kw_bytes = kw.encode(enc)
                idx = data.find(kw_bytes)
                if idx >= 0:
                    start = max(0, idx - 40)
                    end = min(len(data), idx + len(kw_bytes) + 60)
                    context = data[start:end]
                    try:
                        context_text = context.decode(enc, errors='replace')
                    except:
                        context_text = context.hex()
                    hits[kw] = {'encoding': enc, 'offset': idx, 'context': context_text[:120]}
                    break
            except:
                continue
    return hits

def worker_process(args):
    """worker进程：处理一批条目。"""
    gpk_path, start_idx, end_idx, table_bytes, keywords, out_dir = args
    
    hits = []
    try:
        with open(gpk_path, 'rb') as f:
            for i in range(start_idx, end_idx):
                off, comp, decomp, crc1, crc2, flag = struct.unpack_from('<IIIIII', table_bytes, i * 32)
                
                if decomp > 50 * 1024 * 1024:
                    continue
                
                f.seek(off + 36)
                data = f.read(comp)
                
                try:
                    # 2026-09-20：统一走 core 的原生优先 LZ4 与**每线程一个实例**的 zstd。
                    # 旧写法每次 new 一个 ZstdDecompressor 虽不共享，但慢；
                    # 而"共享一个实例"则会在多进程/多线程下 ACCESS_VIOLATION 静默崩。
                    if flag == 2:
                        raw = core.decompress_lz4_block(data, decomp)
                    elif flag == 12:
                        raw = core.decompress_zstd(data, decomp)
                    elif flag == 0:
                        raw = data
                    else:
                        res = core.classify_codec(data, len(data), decomp, flag)
                        if not res.ok:
                            continue
                        raw = res.data
                except Exception:
                    continue
                
                kw_hits = search_in_data(raw, keywords)
                if kw_hits:
                    ext = detect_type(raw)
                    filename = f'{i:06d}.{ext}'
                    
                    # 检查是否包含可读中文（避免二进制误命中）
                    is_text = has_readable_chinese(raw)
                    is_too_large = len(raw) > MAX_FILE_SIZE
                    
                    hit_info = {
                        'entry': i,
                        'filename': filename,
                        'type': ext,
                        'size': len(raw),
                        'keywords': list(kw_hits.keys()),
                        'details': kw_hits,
                        'has_readable_chinese': is_text,
                        'saved': False
                    }
                    
                    # 只保存包含可读中文且不超过大小限制的文件
                    if is_text and not is_too_large:
                        out_path = Path(out_dir) / filename
                        out_path.write_bytes(raw)
                        hit_info['saved'] = True
                    elif is_too_large:
                        hit_info['note'] = '文件过大，仅记录不保存'
                    else:
                        hit_info['note'] = '无可读中文，疑似二进制误命中，仅记录不保存'
                    
                    hits.append(hit_info)
    except Exception as e:
        return {'error': str(e), 'hits': hits, 'range': (start_idx, end_idx)}
    
    return {'hits': hits, 'range': (start_idx, end_idx)}

def main():
    if len(sys.argv) < 3:
        print('用法: python gpk_targeted_extract.py <gpk文件名> <关键词1> [关键词2] ...')
        print('示例: python gpk_targeted_extract.py ui_01.gpk 铠甲勇士 刑天 飞影 帝皇 武器皮肤 时装 抽奖')
        return
    
    gpk_name = sys.argv[1]
    keywords = sys.argv[2:]
    gpk_path = GPK_DIR / gpk_name
    
    if not gpk_path.exists():
        print(f'文件不存在: {gpk_path}')
        return
    
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir = OUT_ROOT / gpk_name.replace('.gpk', '')
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print('=' * 80)
    print(f'定向提取（多进程优化版）: {gpk_name}')
    print(f'关键词: {", ".join(keywords)}')
    print(f'CPU核心数: {CPU_COUNT}, 使用进程数: {WORKER_COUNT} (80%)')
    print('=' * 80)
    print(f'文件大小: {gpk_path.stat().st_size / 1024 / 1024:.2f} MB')
    print()
    
    # 读取头部和条目表
    with open(gpk_path, 'rb') as f:
        head = aes_ecb(f.read(32))
        entry_count = struct.unpack_from('<I', head, 20)[0]
        table_offset = struct.unpack_from('<I', head, 16)[0]
        print(f'条目数: {entry_count}')
        print(f'条目表偏移: {table_offset}')
        print()
        
        f.seek(table_offset)
        # HPGF 格式：表在文件头部 AES 解密区的 head[64:] 起（32B/条）
        table_bytes = aes_ecb(f.read(64 + entry_count * 32))[64:]
    
    # 分批任务
    tasks = []
    for start in range(0, entry_count, BATCH_SIZE):
        end = min(start + BATCH_SIZE, entry_count)
        tasks.append((str(gpk_path), start, end, table_bytes, keywords, str(out_dir)))
    
    print(f'任务分批: {len(tasks)} 批，每批 {BATCH_SIZE} 条')
    print(f'开始多进程处理...')
    print()
    
    start_time = time.time()
    all_hits = []
    completed = 0
    
    with Pool(processes=WORKER_COUNT) as pool:
        for result in pool.imap_unordered(worker_process, tasks):
            if 'error' in result:
                print(f'  [警告] 批次 {result["range"]} 出错: {result["error"]}')
            all_hits.extend(result.get('hits', []))
            completed += 1
            elapsed = time.time() - start_time
            progress = completed / len(tasks) * 100
            eta = elapsed / completed * (len(tasks) - completed) if completed > 0 else 0
            print(f'  进度: {completed}/{len(tasks)} 批 ({progress:.1f}%) | '
                  f'命中: {len(all_hits)} | 耗时: {elapsed:.1f}s | 预计剩余: {eta:.1f}s')
    
    elapsed = time.time() - start_time
    print()
    print('=' * 80)
    print(f'定向提取完成!')
    print(f'  总条目: {entry_count}')
    print(f'  命中: {len(all_hits)} 个')
    print(f'  总耗时: {elapsed:.1f}s (平均 {elapsed/entry_count*1000:.3f}ms/条)')
    print(f'  输出目录: {out_dir}')
    print('=' * 80)
    
    # 按关键词统计
    print()
    print('--- 按关键词统计 ---')
    kw_stats = {}
    for hit in all_hits:
        for kw in hit['keywords']:
            kw_stats[kw] = kw_stats.get(kw, 0) + 1
    for kw, count in sorted(kw_stats.items(), key=lambda x: x[1], reverse=True):
        print(f'  {kw}: {count} 次')
    
    # 按文件类型统计
    print()
    print('--- 按文件类型统计 ---')
    type_stats = {}
    for hit in all_hits:
        type_stats[hit['type']] = type_stats.get(hit['type'], 0) + 1
    for ext, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f'  {ext}: {count} 个')
    
    # 保存结果
    result = {
        'gpk_name': gpk_name,
        'keywords': keywords,
        'entry_count': entry_count,
        'hit_count': len(all_hits),
        'elapsed_seconds': round(elapsed, 2),
        'worker_count': WORKER_COUNT,
        'cpu_count': CPU_COUNT,
        'keyword_stats': kw_stats,
        'type_stats': type_stats,
        'hits': sorted(all_hits, key=lambda x: x['entry'])
    }
    
    result_path = out_dir / '_提取结果.json'
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print()
    print(f'结果已保存: {result_path}')

if __name__ == '__main__':
    main()
