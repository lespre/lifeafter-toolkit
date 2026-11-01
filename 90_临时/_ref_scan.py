# -*- coding: utf-8 -*-
"""反向引用扫描：单表解码 + 字段名登记 + 值域命中统计（可断点续跑）"""
import sys, os, struct, json, time, pathlib, traceback

PROJ = pathlib.Path(r'E:/la拆包项目')
sys.path.insert(0, str(PROJ / '00_规范与工具' / '工具' / '工具库' / '00_共享核心'))
from toolkit_core import bindict_table as BT

CD = PROJ / '01_索引与产物' / '41_还原树' / 'pe' / '配置' / 'com' / 'cdata'
TMP = PROJ / '90_临时'
CACHE = TMP / 'ref_scan_cache.jsonl'

TARGETS = {}   # name -> set[int]
POOL = {}


def load_table(name):
    raw = (CD / f'{name}.py').read_bytes()
    at = raw.find(b'x{')
    if at < 0:
        raise ValueError('no x{ header')
    L = struct.unpack_from('<I', raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    if len(body) < 8:
        raise ValueError('body too short')
    cnt = struct.unpack_from('<I', body, 0)[0]
    blob = body[8 + 4 * cnt:]
    chs = CD / f'{name}_chs.py'
    if chs.exists():
        pool = BT.parse_legacy_chs_pool(chs.read_bytes())
    else:
        pool = []
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, unbound, blob, pool, cnt


MAX_ELEM = 4000


def _as_int(s):
    """仅接受 ASCII 十进制串，避免 '①' 这类 isdigit() 为真但 int() 失败的值。"""
    if isinstance(s, str) and s.isascii() and s.isdigit():
        try:
            return int(s)
        except ValueError:
            return None
    return None


def _from_group(blob, pool, kind, elems, out, depth):
    if depth > 6:
        return
    if kind == 0x01:
        for e in elems:
            out.append((e, False))
    elif kind == 0x05:
        for e in elems:
            if 0 <= e < len(pool):
                iv = _as_int(pool[e])
                if iv is not None:
                    out.append((iv, True))
    elif kind == 0x0B:
        for e in elems:
            if len(out) > MAX_ELEM:
                return
            g = BT.read_27_group(blob, e)
            if g is not None:
                _from_group(blob, pool, g[0], g[1], out, depth + 1)
    elif kind == 0x07:
        i = 0
        while i + 1 < len(elems):
            tb, val = elems[i], elems[i + 1]
            if tb == 0x01:
                out.append((val, False))
            elif tb == 0x05:
                if 0 <= val < len(pool):
                    iv = _as_int(pool[val])
                    if iv is not None:
                        out.append((iv, True))
            elif tb == 0x0B:
                g = BT.read_27_group(blob, val)
                if g is not None:
                    _from_group(blob, pool, g[0], g[1], out, depth + 1)
            i += 2


def walk(blob, pool, v, out, depth=0):
    if depth > 6 or len(out) > MAX_ELEM:
        return
    if isinstance(v, tuple) and len(v) == 2:
        m, p = v
        if m == '0x01':
            if isinstance(p, int) and not isinstance(p, bool):
                out.append((p, False))
        elif m == '0x05':
            iv = _as_int(p)
            if iv is not None:
                out.append((iv, True))
        elif m == '0x0b':
            if isinstance(p, str) and p.startswith('jump:'):
                try:
                    off = int(p[5:])
                except ValueError:
                    return
                g = BT.read_27_group(blob, off)
                if g is not None:
                    _from_group(blob, pool, g[0], g[1], out, depth + 1)
        return
    if isinstance(v, dict):
        for vv in v.values():
            walk(blob, pool, vv, out, depth + 1)
    elif isinstance(v, list):
        for vv in v:
            walk(blob, pool, vv, out, depth + 1)


def scan_one(name):
    rec = {'t': name, 'ok': 1}
    try:
        rows, unbound, blob, pool, cnt = load_table(name)
    except Exception as e:
        rec['ok'] = 0
        rec['err'] = f'{type(e).__name__}: {e}'[:200]
        rec['n'] = 0
        rec['f'] = []
        return rec
    rec['n'] = len(rows)
    rec['cnt'] = cnt
    rec['unb'] = len(unbound)
    per = {}
    order = []
    allf = {}
    rec['ok'] = 1
    try:
      for r in rows:
          vals = r.get('values') or {}
          for k, v in vals.items():
              allf[k] = allf.get(k, 0) + 1
              if k not in per:
                  per[k] = {'occ': 0, 'd': set(), 's': set()}
                  order.append(k)
              out = []
              walk(blob, pool, v, out)
              if out:
                  s = per[k]
                  s['occ'] += len(out)
                  for iv, isd in out:
                      s['d'].add(iv)
                      if isd:
                          s['s'].add(iv)
      fields = []
      for k in order:
          s = per[k]
          nd = len(s['d'])
          if nd == 0:
              continue
          hit = []
          for key, tset in TARGETS.items():
              h = s['d'] & tset
              hs = len(h & s['s'])
              hit.append((len(h), hs))
          fields.append([k, s['occ'], nd] + [x for pair in hit for x in pair])
      rec['f'] = fields
      rec['allf'] = allf
    except Exception as e:
        rec['ok'] = 2
        rec['err'] = f'value-stage {type(e).__name__}: {e}'[:200]
    return rec


def init_worker(targets):
    global TARGETS
    TARGETS = targets


def main():
    t0 = time.time()
    names = sorted(p.stem for p in CD.glob('*.py') if not p.stem.endswith('_chs'))
    print(f'[scan] tables={len(names)}', flush=True)

    # 目标集合
    tgt = {}
    for nm, key in (('fashion_data', 'F'), ('player_appear_data', 'A'),
                    ('player_module_appear_data', 'M')):
        rows, _, _, _, _ = load_table(nm)
        tgt[key] = {int(r['key']) for r in rows}
        print(f'[scan] target {key}={nm} keys={len(tgt[key])}', flush=True)
    rows, _, _, _, _ = load_table('fashion_data_for_export')
    tgt['FID'] = {int(r['values']['fashion_id'][1]) for r in rows
                  if 'fashion_id' in r['values']}
    print(f'[scan] target FID=fashion_id distinct={len(tgt["FID"])}', flush=True)

    done = set()
    if CACHE.exists():
        with CACHE.open('r', encoding='utf-8') as f:
            for line in f:
                try:
                    done.add(json.loads(line)['t'])
                except Exception:
                    pass
    todo = [n for n in names if n not in done]
    print(f'[scan] cached={len(done)} todo={len(todo)}', flush=True)
    if not todo:
        return

    import multiprocessing as mp
    ctx = mp.get_context('spawn')
    nproc = min(20, max(4, (os.cpu_count() or 8) // 2))
    with CACHE.open('a', encoding='utf-8') as fout:
        with ctx.Pool(nproc, initializer=init_worker, initargs=(tgt,)) as pool:
            i = 0
            for rec in pool.imap_unordered(scan_one, todo, chunksize=8):
                fout.write(json.dumps(rec, ensure_ascii=False) + '\n')
                i += 1
                if i % 250 == 0:
                    fout.flush()
                    el = time.time() - t0
                    print(f'[scan] {i}/{len(todo)} {el:.0f}s eta={el/i*(len(todo)-i):.0f}s', flush=True)
    print(f'[scan] done in {time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
