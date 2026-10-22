# -*- coding: utf-8 -*-
"""武器攻击力/火力表（可复跑、只读、自包含，不依赖任何已删除的中间副本）。

链路：script.py314.lc.npk
  -> all_equips BASE(fid A130A31532FAF63C, 装备属性总表) + CHS(fid 94AB0B3FD057EF01, 字段/文本池)
  -> 每个 D6 武器行：name(CHS 文本) + 0x0B(type=11) 跳转操作数
  -> 操作数绝对定位到 attrs 对象(schema_ref=6109, 55 字段)
  -> schema field23 = hurt(攻击力)、field35 = power(火力)，命名绑定
  -> 输出 武器名 -> {hurt 攻击力, power 火力, ...} JSON + CSV

明日之后伤害公式：伤害 = 攻击力(hurt) × 火力(power)。
注意：fid 可能随大版本漂移；若解出的 55 字段名不合法，用同目录 scan_equips_base_mp.py 重定位 BASE/CHS。
"""
from __future__ import annotations
import csv, json, os, struct, zlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PKG = Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT = Path(__file__).resolve().parent / 'output' / 'weapon_attrs'
K = bytes.fromhex('606308d8a32c782013d26c2f226f686d')
BASE = int('A130A31532FAF63C', 16)   # all_equips 装备属性总表（2026-09-01 于 780363b86008 快照定位）
CHS = int('94AB0B3FD057EF01', 16)    # 配对字段/文本池
ATTRS_SCHEMA = 6109                 # attrs 对象 schema，field23=hurt field35=power
KNOWN = {1, 3, 5, 11, 17, 18, 34}


def aes(x):
    n = len(x) // 16 * 16
    d = Cipher(algorithms.AES(K), modes.ECB()).decryptor()
    return d.update(x[:n]) + d.finalize() + x[n:]


def unpack(dec):
    for skip in (18, 16, 0):
        for wb in (15, -15):
            try:
                return zlib.decompress(dec[skip:], wb)
            except zlib.error:
                pass
    raise ValueError('unpack fail')


def body_of(raw):
    q = raw.find(b'x{'); ln = struct.unpack_from('<I', raw, q + 2)[0]
    return raw[q + 6:q + 6 + ln]


def uleb(d, p, e):
    v = 0; s = 0
    for _ in range(10):
        b = d[p]; p += 1; v |= (b & 127) << s
        if not b & 128:
            return v, p
        s += 7
    raise ValueError('uleb overlong')


def strings(body):
    c, _ = struct.unpack_from('<II', body, 0); te = 8 + 4 * c
    ends = struct.unpack_from(f'<{c}I', body, 8)
    out = []; last = 0
    for e in ends:
        out.append(body[te + last:te + e].decode('utf-8', 'replace')); last = e
    return out


def base_blob(body):
    c, _ = struct.unpack_from('<II', body, 0); te = 8 + 4 * c
    b = body[te:]; de = struct.unpack_from('<I', b, 0)[0]
    t = b[de:]; bc = t[3]
    nodes = sorted({struct.unpack_from('<I', t, 4 + 8 * i + 4)[0] >> 8 for i in range(bc)})
    rows = []
    for ni, s in enumerate(nodes):
        e = nodes[ni + 1] if ni + 1 < len(nodes) else len(b); p = s
        while p < e:
            key, p = uleb(b, p, e); start, p = uleb(b, p, e); rows.append((key, start))
    return b, de, dict(rows)


def load():
    with PKG.open('rb') as f:
        h = aes(f.read(32)); _r, mg, ver, to, n = struct.unpack_from('<QIIII', h)
        f.seek(to); T = aes(f.read(n * 48)); src = {}
        for i in range(n):
            fid, off, ps, ds, a, b2, fl = struct.unpack_from('<QIIIIIi', T, i * 48)
            if fid in (BASE, CHS):
                f.seek(off); src[fid] = body_of(unpack(aes(f.read(ps))))
    slots = strings(src[CHS])
    blob, de, keystarts = base_blob(src[BASE])
    return ver, slots, blob, de, keystarts


def schema_at(blob, slots, ref):
    p = ref; n2, p = uleb(blob, p, len(blob)); bits, p = uleb(blob, p, len(blob)); fs = []
    for ix in range(n2):
        slot, p = uleb(blob, p, len(blob)); typ = blob[p]; p += 1
        fs.append({'i': ix, 'slot': slot, 't': typ, 'name': slots[slot] if slot < len(slots) else f'<bad{slot}>'})
    return n2, bits, fs, p


def read_val(blob, typ, p, slots):
    if typ == 1:
        v, p = uleb(blob, p, len(blob))
    elif typ == 3:
        v = blob[p]; p += 1
    elif typ == 5:
        s, p = uleb(blob, p, len(blob)); v = slots[s] if s < len(slots) else f'<bad{s}>'
    elif typ == 11:
        v, p = uleb(blob, p, len(blob))          # 0x0B 绝对跳转操作数
    elif typ == 17:
        u, p = uleb(blob, p, len(blob)); v = (u >> 1) ^ (-(u & 1))
    elif typ == 18:
        v = struct.unpack_from('<f', blob, p)[0]; p += 4
    elif typ == 34:
        v = struct.unpack_from('<d', blob, p)[0]; p += 8
    else:
        raise ValueError(f'type {typ}')
    return v, p


def attrs_obj(blob, slots, off):
    """解析 schema6109 的 attrs 对象，返回 {字段名: 值}。"""
    if off >= len(blob) or blob[off] not in (0xc6, 0x86, 0xd6):
        return None
    p = off + 1; sr, p = uleb(blob, p, len(blob))
    if sr != ATTRS_SCHEMA:
        return None
    br, p = uleb(blob, p, len(blob))
    n2, bits, fs, _ = schema_at(blob, slots, sr)
    bm = blob[br:br + (bits + 7) // 8]
    use = [f for f in fs if f['i'] >= bits or bm[f['i'] // 8] & (1 << (f['i'] % 8))]
    vals = {}
    for f in use:
        v, p = read_val(blob, f['t'], p, slots)
        if f['t'] != 11:
            vals[f['name']] = v
        else:
            vals['_jump'] = v
    return vals


def main():
    ver, slots, blob, de, keystarts = load()
    n2, bits, afields, _ = schema_at(blob, slots, ATTRS_SCHEMA)
    assert n2 == 55 and afields[23]['name'] == 'hurt' and afields[35]['name'] == 'power', \
        f'attrs schema 漂移: n={n2} f23={afields[23]["name"]} f35={afields[35]["name"]}，请重定位'

    weapons = []
    for key, st in keystarts.items():
        if blob[st] != 0xd6:
            continue
        try:
            p = st + 1; sref, p = uleb(blob, p, len(blob)); bref, p = uleb(blob, p, len(blob))
            sn, sb, sfs, _ = schema_at(blob, slots, sref)
            bm = blob[bref:bref + (sb + 7) // 8]
            use = [f for f in sfs if f['i'] >= sb or bm[f['i'] // 8] & (1 << (f['i'] % 8))]
            row = {'key': key, '_sref': sref}; jumps = []
            for f in use:
                v, p = read_val(blob, f['t'], p, slots)
                if f['t'] == 11:
                    # 只有名为 attrs 的跳转字段才指向 schema6109 属性对象；
                    # 其余 type=11（rand_attr_ids/slots/affect_types 等）是数组/ID 引用，不能当攻击力
                    if f['name'] == 'attrs':
                        jumps.append(v)
                else:
                    row[f['name']] = v
            for jt in jumps:  # 接上 attrs 对象
                av = attrs_obj(blob, slots, jt)
                if av and 'hurt' in av:
                    row['hurt'] = av['hurt']; row['power'] = av.get('power')
                    row['_attrs_off'] = jt
            # 只收武器主 schema（164051，含 name+attrs+fire_speed 的枪械/近战模板）；
            # 道具/时装/家具是别的 schema，其 attrs 是共享默认槽，会张冠李戴
            if 'hurt' in row and isinstance(row.get('name'), str) and row.get('_sref') == 164051:
                weapons.append(row)
        except Exception:
            continue

    import math
    def clean_name(nm):
        return (isinstance(nm, str) and 0 < len(nm) <= 16
                and '#r' not in nm and not any(ch in nm for ch in '。，、！？：；“”'))
    def valid_row(r):
        h, pw = r.get('hurt'), r.get('power')
        if not (isinstance(h, int) and 1 <= h <= 3000):
            return False
        if pw is not None and not (isinstance(pw, (int, float)) and math.isfinite(pw) and 0.3 <= pw <= 40):
            return False
        return clean_name(r.get('name'))
    # 去重：同名武器取一条，hurt/power 数值化；清洗掉描述串误接/非规格浮点
    seen = {}
    for r in weapons:
        if not valid_row(r):
            continue
        nm = r['name']
        # 同名保留 hurt 最大者（正常版本，而非体验残血版）
        if nm not in seen or (r.get('hurt') or 0) > (seen[nm].get('hurt') or 0):
            seen[nm] = r
    table = []
    for nm, r in sorted(seen.items(), key=lambda x: -(x[1].get('hurt') or 0)):
        table.append({'name': nm, 'hurt_攻击力': r.get('hurt'), 'power_火力': r.get('power'),
                      'fire_speed': r.get('fire_speed'), 'durability': r.get('durability'),
                      'base_score': r.get('base_score'),
                      'weapon_type': r.get('weapon_type'), 'weapon_kind': r.get('weapon_kind')})

    OUT.mkdir(parents=True, exist_ok=True)
    cols = ['name', 'hurt_攻击力', 'power_火力', 'fire_speed', 'durability', 'base_score', 'weapon_type', 'weapon_kind']
    (OUT / '武器攻击力火力表.json').write_text(json.dumps(
        {'source': str(PKG), 'version': ver, 'count': len(table),
         'binding': '武器行 schema164051 的 attrs 字段 -> attrs schema6109；field23=hurt(攻击力) field35=power(火力)；伤害=攻击力×火力',
         'table': table}, ensure_ascii=False, indent=2), encoding='utf-8')
    with (OUT / '武器攻击力火力表.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(table)

    print(f"武器条目 {len(weapons)} 去重后 {len(table)}，输出 {OUT}")
    for kw in ('AUG', 'SCAR', '突击'):
        print(f"\n== 含 {kw} ==")
        for r in table:
            if kw in r['name'].upper():
                print(' ', r)
    print("\n== hurt 155~166（定位 SCAR=161）==")
    for r in table:
        if isinstance(r['hurt_攻击力'], int) and 155 <= r['hurt_攻击力'] <= 166:
            print(' ', r)
    print("\n== hurt 最高前 15 ==")
    for r in table[:15]:
        print(' ', r['name'], 'hurt', r['hurt_攻击力'], 'power', r['power_火力'])


if __name__ == '__main__':
    main()
