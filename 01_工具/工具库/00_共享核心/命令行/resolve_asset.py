#!/usr/bin/env python3
"""★ 模板：任意资源 → 引用 → 哈希 → 定位 → 判身份（四步全自动 ✓）

用法：
    python resolve_asset.py --ref <mtg或c159文件>            # 从引用文件解出它要的资源
    python resolve_asset.py --find 'weapon\\skin\\skin_1003_010' --ext mtg
    python resolve_asset.py --semantic <png目录>

设计原则（都是踩过坑总结的）：
 ① 引用【逐字】从 mtg/c159 取，不手打路径
 ② fid = path_id_raw（双 seed murmur3）；gres 必须用 parse_gpk_gres
 ③ parse_gpk/parse_gpk_gres 返回 (rec, rows_fn)；★ rows_fn 是【函数】必须调用
 ④ 0 命中先怀疑代码（函数/偏移），再怀疑数据
 ⑤ 判身份用【通道恒定性 + 相关度】，不用肉眼
"""
import argparse
import importlib.util
import re
import sqlite3
import struct
import sys
from pathlib import Path

ROOT = Path(r'E:\la拆包项目')
PD = ROOT / '01_工具/工具库/02_图文音频渲染/皮肤链与渲染'
CORE = ROOT / '01_工具/工具库/00_共享核心'
for p in (str(PD), str(CORE)):
    if p not in sys.path:
        sys.path.insert(0, p)

_spec = importlib.util.spec_from_file_location('gpkidx', str(PD / 'gpk_npk_index.py'))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

ROWDB = ROOT / '03_执行/10_索引/indexes/row_path_map.db'
MRZH = Path(r'E:\mrzh')


def declared_paths(ref_file):
    """① 从 mtg/c159 逐字抽出所有资源路径（保序去重）。"""
    raw = Path(ref_file).read_bytes()
    pat = re.compile(rb'[\x20-\x7E]{5,220}\.(?:tga|dds|png|cube|array|ktx)')
    out = []
    for m in pat.finditer(raw):
        s = m.group(0).decode('ascii', 'replace')
        if s not in out:
            out.append(s)
    return out


def fid_of(path):
    return '%016X' % G.path_id_raw(path)


def locate_by_index(fid):
    """③a 索引库（最全，含 gres）"""
    con = sqlite3.connect(str(ROWDB))
    cur = con.cursor()
    r = cur.execute('SELECT container,row_index,path,in_tree FROM rows WHERE fid_hex=? LIMIT 5',
                    (fid,)).fetchall()
    con.close()
    return r


def iter_container(container):
    """③b 直接读容器：gres 用 parse_gpk_gres，其余用 parse_gpk。"""
    p = MRZH / container
    if not p.is_file():
        return None
    fn = G.parse_gpk_gres if 'gres' in container.lower() else G.parse_gpk
    rec, rows_fn = fn(str(p))
    return rows_fn()          # ★ 函数必须调用


def locate_by_container(container, fids):
    """在指定容器里按 fid 找行。"""
    it = iter_container(container)
    if it is None:
        return []
    out = []
    for row in it:
        if not hasattr(row, '__iter__'):
            continue
        h = '%016X' % (row[1] & 0xFFFFFFFFFFFFFFFF)
        if h in fids:
            out.append((row[0], h, row[2], row[4]))
    return out


def semantic_kind(png_path):
    """④ 通道恒定性 + 相关度 ⇒ 身份（不用肉眼）。"""
    try:
        import numpy as np
        from PIL import Image
    except Exception:
        return 'numpy/PIL 不可用'
    a = np.asarray(Image.open(png_path).convert('RGB')).astype(float).reshape(-1, 3)
    mean = a.mean(0)
    std = a.std(0)
    m = a

    def corr(x, y):
        if x.std() < 1e-6 or y.std() < 1e-6:
            return 1.0
        return float(np.corrcoef(x, y)[0, 1])
    const = [i for i in range(3) if std[i] < 1.5]
    n_const = len(const)
    if abs(mean[0] - 128) < 25 and abs(mean[1] - 128) < 25 and mean[2] > 200:
        return '法线图(标准)'
    if 2 in const and std[2] < 1.5 and mean[2] > 200:
        return '法线图(细节)'
    if n_const >= 2:
        return '单通道数据图(蒙版/发光)'
    if n_const == 1 and mean[const[0]] > 240:
        return '参数图(ParamMap)'
    c = corr(m[:, 0], m[:, 1])
    sat = float(np.abs(m.max(1) - m.min(1)).mean())
    if c > 0.8 and sat > 40:
        return '基色图'
    if c > 0.8 and sat <= 40:
        return '表面图/灰度图'
    return '未定'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', help='mtg/c159 文件 ⇒ 列出它声明的资源并定位')
    ap.add_argument('--find', help='名字片段（配 --ext）⇒ 在索引里找')
    ap.add_argument('--ext', default='', help='扩展名过滤，如 mtg')
    ap.add_argument('--container', help='额外在某容器里按哈希核验')
    ap.add_argument('--semantic', help='png 目录 ⇒ 判每张的身份')
    a = ap.parse_args()

    if a.semantic:
        d = Path(a.semantic)
        for p in sorted(d.glob('*.png')):
            print('  %-22s %s' % (p.name, semantic_kind(p)))
        return 0

    if a.find:
        con = sqlite3.connect(str(ROWDB))
        cur = con.cursor()
        q = "SELECT container,row_index,fid_hex,path,in_tree FROM rows WHERE path LIKE ?"
        args = ['%' + a.find + '%']
        if a.ext:
            q += ' AND path LIKE ?'
            args.append('%.' + a.ext)
        q += ' ORDER BY path LIMIT 80'
        for r in cur.execute(q, args):
            print('  [%s] r%-8s tree=%s %s' % (r[0], r[1], r[4], r[3]))
        con.close()
        return 0

    if a.ref:
        paths = declared_paths(a.ref)
        print('  ① 引用声明 %d 条：' % len(paths))
        fids = {}
        for p in paths:
            f = fid_of(p)
            fids[f] = p
            print('     %s  %s' % (f, p))
        print()
        print('  ③ 索引库定位：')
        hit = 0
        for f, p in fids.items():
            r = locate_by_index(f)
            if r:
                hit += 1
                for c, row, path, in_tree in r:
                    print('     ★ [%s] r%-8s %s' % (c, row, path))
        print('     命中 %d / %d' % (hit, len(fids)))
        if a.container:
            print()
            print('  ③b 容器核验 %s：' % a.container)
            for r, h, off, dec in locate_by_container(a.container, set(fids)):
                print('     ★ r%-8s fid=%s off=%-10s dec=%-9s ← %s' % (
                    r, h, off, dec, fids[h]))
        return 0

    ap.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
