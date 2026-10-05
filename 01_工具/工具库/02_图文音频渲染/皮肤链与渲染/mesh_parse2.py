# -*- coding: utf-8 -*-
"""mesh_parse2.py — .mesh v4 通用解析器（变长子网格 + 额外流自动识别）
布局: header + [subs: (vc u32, fc u32, flag u16) ×N] + term u16 + tv u32 + tf u32 + bbox 6f +
      pos(tv*6) + nrm(tv*6) + pad(2) + idx(tf*6) + uv(tv*4) + [extra streams(tv*4 each)] + trailer(16)
- N 子网格数量由 [term==1, tv==Σvc, tf==Σfc] 三重校验自动定位；
- extra streams 由尺寸算术确定数量（**floor**，2026-09-18 修正见下）；>0 时最后一个 extra 暂按 u8×4 顶点色解析（010 实证）；
- flag 位: 0x101/0x102 见注（低位=UV 层数提示, 0x100=含 color 流提示）。
★ 2026-09-18 修正（additive，保守）：附加流数量改用 floor；带骨骼块变体实测 24/24 `extra_bytes` 不整除 tv*4
  （UV 流之后另有一块不被本布局记账的数据），原 `round()` 会多算一条流并越界读顶点色。
  现 meta 新增 `trailing_bytes` / `extra_streams_state`(exact|trailing_unaccounted|file_shorter_than_layout) /
  `vcol_read`；越界时**不静默截断**（vcol=None，状态可判定），`sizes_ok` 语义不变。
  ⇒ **通过判据请用 `sizes_ok=True`（且 extra_streams_state=='exact'），不要只看"没抛异常"。**
输出: P(3D), uv(Nx2), idx(Fx3), meta{subs,flags,tv,tf,bbox,n_extra,vcol,sub_offsets,trailing_bytes,
      extra_streams_state,vcol_read,layout_variant,...}
★ 2026-09-27 修正（additive，带骨骼块的 .mesh 现在能解出几何了；两个独立原因）:
  ① 骨名块起点只找 b'biped '（带尾空格）⇒ 首个骨名恰好就叫 `biped`（无后缀，槽内 \x00 结尾）时
     会落到**第 2 个**骨名上，n_bones 条校验走到最后一个槽位（bone_camera/空槽）必然失败
     ⇒ 抛 bone_block_layout_unrecognized。修：候选 key 加 b'biped\x00'（取最早命中）。
  ② 骨块之后找 sub 表的窗口只有 8192 B，而实测骨名块尾 → sub 表间隔 ≈ 92 B/骨
     （90 骨 ⇒ 2982 → 11277，间隔 8295 B）⇒ 窗口刚好差一点，永远找不到。
     修：窗口放宽到文件尾，并追加「流布局必须放得进文件」的判据（挡随机 u16 假阳）。
  ③ 新增 `_scan_sub_table_anywhere()` 全文件兜底（term==1 + tv==Σvc + tf==Σfc + 布局可容纳），
     覆盖骨名非 biped 系 / 无 bflag 标记等情形。meta.layout_variant 记录走了哪条路。
  实测：斩神 11/11 原本报错的带骨骼网格全部解出，且每个文件**恰好只有 1 个**候选通过该判据；
         对照组 h_m_3716_1（原本就成功）经新路径得到完全相同的 tv/tf/subs 与顶点数据。
"""
import struct
import numpy as np

# ★ 2026-09-27 新增（供带骨骼块变体与兜底扫描共用；不改任何既有成功路径）：
def _sub_table_fits(d, off, tv, tf):
    """该 sub 表声明的流布局能否完整放进文件。
    账目：pos(tv*6) + nrm(tv*6) + pad(2) + idx(tf*6) + uv(tv*4)，再加 bbox(24)。
    ⇒ 用来挡「把随机 u16 当 vc/fc 读」的假阳（那种候选的 tv 动辄 65536/131072 级，
      布局远超文件长度）。实测 11/11 带骨块网格 ⇒ 每个文件恰好只有 1 个候选通过。"""
    need = tv * 6 + tv * 6 + 2 + tf * 6 + tv * 4
    return (off + 10 + 24) + need <= len(d)


def _scan_sub_table_anywhere(d, lo=0x12):
    """★ 2026-09-27 新增兜底：从 lo 扫到文件尾，找合法 sub 表。
    判据 = term==1 AND tv==Σvc AND tf==Σfc AND _sub_table_fits(...)（三重校验 + 布局可容纳）。
    什么时候用：骨块识别失败（骨名非 biped 系）/ 骨块后搜索窗不够 / 无 bflag 标记。
    返回与既有路径相同的 best=(k, term_off, subs, tv, tf)；找不到返回 None。"""
    n = len(d)
    for cand in range(lo, n - 34):
        if d[cand] != 1 or d[cand + 1] != 0:
            continue
        tv, tf = struct.unpack_from('<II', d, cand + 2)
        if tv == 0 or tf == 0 or tv * 16 > n:      # 下界：pos+nrm+uv ≥ tv*16
            continue
        for k2 in range(1, 33):
            b2 = cand - 10 * k2
            if b2 < 0:
                break
            subs2 = [struct.unpack_from('<IIH', d, b2 + 10 * i) for i in range(k2)]
            if sum(s[0] for s in subs2) == tv and sum(s[1] for s in subs2) == tf:
                if _sub_table_fits(d, b2, tv, tf):
                    return (k2, cand, subs2, tv, tf)
    return None


# ================= ★ 2026-10-02 引擎对标：流偏移的唯一权威来源 =================
def _engine_streams(d, off, subs, tv, tf, ver, flag8, typ, half):
    """按 libclient FUN_0210e860 / FUN_02113860 的真实顺序逐段推进游标。
    依据（函数地址见 03_执行/30_分析/引擎对标_网格顶点流_20261002.md）：
      · ver>=0x50004: pos=3×u16(6B/顶点) 且其前有 6×f32 量化包围盒[maxXYZ,minXYZ]；nrm=3×u16
      · ver<0x50004: pos=3×f32(12B/顶点, 无包围盒)；nrm=8B(half) 或 12B
      · u16 标志(旧名 pad) != 0 ⇒ 其后跟 tv*(8|6|12) 的流
      · 每子网格 extras 条数 = sub.flag 低字节，尺寸按该子网格 vc * (4 if half else 8)
      · sub.flag 高字节 == 1 ⇒ extras 之后另有 vc*4 的 u32 重映射块
      · typ==1 ⇒ 蒙皮块 + 32B 位掩码
    返回各流绝对偏移；`ok` = 游标落在 len-16（标准 footer）或 len。"""
    k = len(subs)
    # 注意：本代码里 `off` 是 **term 偏移**（= sub 表起点 + 10*k），三个定位器口径一致
    q = off                                           # term u16 + tv u32 + tf u32
    o = {'ver': ver, 'flag8': flag8, 'typ': typ, 'half': half,
         'off': off, 'subtab_off': off - 10 * k, 'k': k, 'tv': tv, 'tf': tf}
    o['term'] = struct.unpack_from('<H', d, q)[0]

    if o['term'] == 0:                                # 引擎此处直接 return，无顶点数据
        o['pos_off'] = o['nrm_off'] = o['idx_off'] = None
        o['extras'] = []; o['remaps'] = []; o['end'] = q + 10
        o['footer'] = len(d) - o['end']; o['ok'] = False
        return o
    q += 10

    # 1) 量化包围盒 (仅 v>=0x50004) + 位置流
    if ver >= 0x50004:
        o['bounds_off'] = q
        o['bbox'] = struct.unpack_from('<6f', d, q)   # [maxXYZ, minXYZ]
        q += 24
        o['pos_off'] = q; o['pos_bytes'] = tv * 6; o['pos_mode'] = 'u16x3'
        q += tv * 6
    else:
        o['bounds_off'] = None; o['bbox'] = None
        o['pos_off'] = q; o['pos_bytes'] = tv * 12; o['pos_mode'] = 'f32x3'
        q += tv * 12

    # 2) 法线流
    if ver >= 0x50004:
        o['nrm_off'] = q; o['nrm_bytes'] = tv * 6; o['nrm_mode'] = 'u16x3'; q += tv * 6
    elif half:
        o['nrm_off'] = q; o['nrm_bytes'] = tv * 8; o['nrm_mode'] = '8B'; q += tv * 8
    else:
        o['nrm_off'] = q; o['nrm_bytes'] = tv * 12; o['nrm_mode'] = 'f32x3'; q += tv * 12

    # 3) u16 存在位标志（旧名 “pad”）+ 可选流
    o['flag48_off'] = q
    o['flag48'] = struct.unpack_from('<H', d, q)[0]
    q += 2
    if o['flag48'] != 0:
        nb = (tv * 8 if ver < 0x50004 else tv * 6) if half else tv * 12
        o['s48_off'] = q; o['s48_bytes'] = nb; q += nb

    # 4) 索引流
    o['idx_off'] = q; o['idx_bytes'] = tf * 6; q += tf * 6

    # 5) 每子网格的 extra 流（条数 = sub.flag 低字节，尺寸按该子网格 vc）
    ex = []
    for i, (vc, fc, f) in enumerate(subs):
        n = f & 0xff
        pv = 4 if half else 8
        ex.append(dict(sub=i, off=q, n=n, vc=vc, per_vertex=pv, total=n * vc * pv))
        q += n * vc * pv
    o['extras'] = ex

    # 6) sub.flag 高字节 == 1 ⇒ 额外 vc*4 的 u32 重映射块
    rm = []
    for i, (vc, fc, f) in enumerate(subs):
        if (f >> 8) == 1:
            rm.append(dict(sub=i, off=q, bytes=vc * 4))
            q += vc * 4
    o['remaps'] = rm

    # 7) 蒙皮块（typ==1）
    if typ == 1:
        if ver < 0x50004:
            o['skin'] = dict(mode='v<0x50004 tv*20', off=q, bytes=tv * 20); q += tv * 20
            if ver >= 0x50003:
                o['bitset'] = dict(off=q, bytes=32); q += 32
        else:
            if q < len(d) and d[q] == 1:
                sw = struct.unpack_from('<h', d, q + 1)[0]
                cnt = struct.unpack_from('<H', d, q + 3)[0]
                idw = 1 if sw == 8 else 2
                o['skin'] = dict(mode='palette', off=q, palette_width=sw, palette_count=cnt,
                                 palette_bytes=5 + cnt * 4, index_width=idw)
                q += 5 + cnt * 4 + tv * idw + tv * 6
            else:
                o['skin'] = dict(mode='raw(tag0) idx tv*4', off=q)
                q += 1 + tv * 4 + tv * 6
            if ver >= 0x50003:
                o['bitset'] = dict(off=q, bytes=32); q += 32

    o['end'] = q
    o['footer'] = len(d) - q
    o['ok'] = o['footer'] in (16, 0)
    return o


def parse_mesh2(path, load_vcol=True):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x34\x80\xc8\xbb', 'magic mismatch'
    ver = struct.unpack_from('<H', d, 4)[0]
    # 1) 定位 sub 表: 假设 0x0E 起每 10B 一项, 试探 k=1..10, 用 (term==1, tv==Σvc, tf==Σfc) 校验
    best = None
    variant = None       # ★ 2026-09-27：记录命中路径，仅供报告/诊断（不参与判定）
    for k in range(1, 11):
        off = 0x0E + 10 * k
        if off + 2 + 8 + 24 > len(d): break
        term = struct.unpack_from('<H', d, off)[0]
        tv, tf = struct.unpack_from('<II', d, off + 2)
        if term != 1 or tv == 0 or tf == 0: continue
        subs = [struct.unpack_from('<IIH', d, 0x0E + 10 * i) for i in range(k)]
        if sum(s[0] for s in subs) == tv and sum(s[1] for s in subs) == tf:
            best = (k, off, subs, tv, tf); variant = 'sub_table_0x0e'; break
    bone_block = None
    if best is None:
        # ★ 新增分支（2026-09-18，只加分支、不动上方成功路径）：带骨骼块的 .mesh 变体。
        # 判据（字段级，7/7 精确 + 对照组 6/6 无假阳）：u16@8 低字 == 1 ⇒ 含 bone 块，
        # 高字 n_bones == 量到的骨名条数。成功样本该低字恒为 0 且无骨名。
        # 骨名定长 32B 步进；**块尾对齐偏移未定，故不假设偏移，改为向后搜索 sub 表**。
        bflag, n_bones = struct.unpack_from('<HH', d, 8)
        if bflag == 1 and n_bones >= 1:
            def _find_bone_start():
                st = -1
                # ★ 2026-09-27 修正：加入 b'biped\x00'。斩神这批网格的**首个骨名恰好就叫
                #   `biped`（无后缀，槽内以 \x00 结束）**，只找 b'biped '（带尾空格）会落到
                #   第 2 个骨名上（102 → 134），校验一路走到最后一个槽位（bone_camera / 空槽）
                #   必然失败 ⇒ 骨块被误判为「不认识的布局」并抛错。
                for key in (b'biped ', b'biped_', b'biped\x00'):
                    j = d.find(key, 0, min(4096, len(d)))
                    if j >= 0 and (st < 0 or j < st): st = j
                if st > 0 and d[st - 1:st] == b'-': st -= 1
                return st
            st = _find_bone_start()
            if st >= 0:
                ok = True
                for i in range(n_bones):
                    p = st + 32 * i
                    if d[p:p + 5] != b'biped' and d[p:p + 6] != b'-biped':
                        ok = False; break
                bone_block = st if ok else None
            # ★ 2026-09-27：骨块识别失败**不再直接抛错** —— 上方只认 biped 系骨名，
            #   非人形骨名（背包/道具等）会全程 MISS。改为落到文件尾的全文件扫兜底。
            if bone_block is not None:
                # 从骨块之后向后搜索 (term==1, tv==Σvc, tf==Σfc)，k 上限 64
                # ★ 2026-09-27：搜索窗从 end+8192 放宽到文件尾。实测骨名块之后还有约 92 B/骨
                #   的骨数据块：90 骨 ⇒ 骨名块尾 2982、sub 表在 11277，间隔 8295 B > 8192
                #   ⇒ 原窗口刚好差一点，带骨骼网格 100% 找不到 sub 表。
                end = bone_block + 32 * n_bones
                for cand in range(end, len(d) - 34):
                    if struct.unpack_from('<H', d, cand)[0] != 1: continue
                    tv2, tf2 = struct.unpack_from('<II', d, cand + 2)
                    if tv2 == 0 or tf2 == 0: continue
                    for k2 in range(1, 65):
                        b2 = cand - 10 * k2
                        if b2 < 0: break
                        subs2 = [struct.unpack_from('<IIH', d, b2 + 10 * i) for i in range(k2)]
                        if sum(s[0] for s in subs2) == tv2 and sum(s[1] for s in subs2) == tf2:
                            # ★ 追加「流布局放得进文件」，挡随机 u16 假阳（既有成功样本照样通过）
                            if _sub_table_fits(d, b2, tv2, tf2):
                                best = (k2, cand, subs2, tv2, tf2)
                                variant = 'bone_block_forward_scan'; break
                    if best is not None: break
    if best is None:
        # ★ 2026-09-27 兜底：全文件扫 sub 表（骨块识别失败 / 无 bflag 标记 / 骨块后窗口不够）
        best = _scan_sub_table_anywhere(d)
        if best is not None:
            variant = 'full_file_scan'
    if best is None:
        bflag0, n_bones0 = struct.unpack_from('<HH', d, 8)
        if bflag0 == 1 and n_bones0 >= 1:
            # 保持原异常契约：带骨骼块变体全扫仍失败时抛这个
            raise ValueError('bone_block_layout_unrecognized')
        raise ValueError('无法定位 sub 表 (term/tv/tf 校验失败)')
    k, off, subs, tv, tf = best

    # ================= ★ 2026-10-02 引擎对标：偏移全部由 _engine_streams 给出 =========
    # 旧版本（additive 保留说明）：曾用 bbox@off+10 + pos(tv*6)+nrm(tv*6)+pad(2)+idx(tf*6)+uv(tv*4)
    # 硬套；实测只对 ver>=0x50004 成立，且把 extras 条数当成“剩余字节 // (tv*4)”。现全部替换。
    ver24 = struct.unpack_from('<I', d, 4)[0] & 0xffffff
    flag8 = struct.unpack_from('<I', d, 4)[0] >> 24
    typ = struct.unpack_from('<H', d, 8)[0]
    half = (ver24 > 0x50003) or (flag8 == 2)
    eng = _engine_streams(d, off, subs, tv, tf, ver24, flag8, typ, half)

    pos_off = eng['pos_off']; nrm_off = eng['nrm_off']; idx_off = eng['idx_off']
    extras = [e['off'] for e in eng['extras']]
    n_extra = sum(e['n'] for e in eng['extras'])
    after_uv = extras[0] if extras else (idx_off + tf * 6 if idx_off is not None else pos_off)
    uv_off = after_uv

    # bbox：ver>=0x50004 用文件内 [maxXYZ,minXYZ]；老版（无包围盒）从 pos 实算
    if eng['bbox'] is not None:
        b6 = eng['bbox']
        bmin = np.array(b6[3:6], np.float32); bmax = np.array(b6[0:3], np.float32)
    else:
        _P0 = np.frombuffer(d, dtype='<f4', count=tv * 3, offset=pos_off).reshape(-1, 3)
        bmin = _P0.min(0).astype(np.float32); bmax = _P0.max(0).astype(np.float32)

    extra_bytes = len(d) - (uv_off + eng['footer'])
    ok_sizes = eng['ok']
    trailing_bytes = max(0, eng['footer'] - 16)
    if eng['footer'] == 16:
        extra_streams_state = 'exact'
    elif eng['footer'] == 0:
        extra_streams_state = 'exact_no_footer'
    elif eng['footer'] < 0:
        extra_streams_state = 'file_shorter_than_layout'
    else:
        extra_streams_state = 'trailing_unaccounted'

    # 位置解码：引擎语义——ver>=0x50004 是 u16 量化 + 包围盒；老版是裸 f32
    if eng['pos_mode'] == 'u16x3':
        pos_raw = np.frombuffer(d, dtype='<u2', count=tv * 3, offset=pos_off).reshape(-1, 3)
        f = (pos_raw.astype(np.float32) + 0.5) / 65536.0
        P = bmin + f * (bmax - bmin)
    else:
        P = np.frombuffer(d, dtype='<f4', count=tv * 3, offset=pos_off).reshape(-1, 3).astype(np.float32)
    idx = np.frombuffer(d, dtype='<u2', count=tf * 3, offset=idx_off).reshape(-1, 3).astype(np.int64)
    if n_extra >= 1 and uv_off + tv * 4 <= len(d):
        uv = np.frombuffer(d, dtype='<f2', count=tv * 2, offset=uv_off).reshape(-1, 2).astype(np.float32)
    else:
        uv = np.zeros((tv, 2), np.float32)
    vcol = None
    vcol_read = None
    if n_extra >= 1 and load_vcol:
        co = extras[-1]
        # 引擎语义：extras 是“非记账流”，只有非 half（8B/顶点）时最后一个才可能是 u8×4 颜色
        if eng['ok'] and (not half) and co + tv * 4 <= len(d):
            vcol = np.frombuffer(d, dtype=np.uint8, count=tv * 4, offset=co).reshape(-1, 4).astype(np.float32) / 255.0
            vcol_read = dict(offset=co, count=tv * 4, state='read')
        else:
            vcol_read = dict(offset=co, count=tv * 4, state='skipped_engine_layout',
                             footer=eng['footer'], half=half)
    o = 0; sub_offsets = []
    for vc, fc, u in subs:
        sub_offsets.append((o, o + vc)); o += vc
    meta = dict(ver=ver, subs=subs, flags=[u for _, _, u in subs], tv=tv, tf=tf,
                bbox=(bmin, bmax), dataoff=pos_off, n_extra=n_extra, extra_offsets=extras,
                extra_bytes=extra_bytes, sizes_ok=ok_sizes, vcol=vcol, sub_offsets=sub_offsets,
                # 未记账尾部与顶点色读取状态，供调用方判定
                trailing_bytes=trailing_bytes, extra_streams_state=extra_streams_state,
                vcol_read=vcol_read,
                # 命中的定位路径（sub_table_0x0e | bone_block_forward_scan | full_file_scan）
                layout_variant=variant,
                nrm_off=nrm_off, idx_off=idx_off, uv_off=uv_off,
                # ★ 2026-10-02 新增：引擎对标字段（真实版本/精度/逐流偏移/尾部记账）
                eng=eng, ver24=ver24, flag8=flag8, typ=typ, half=half,
                eng_ok=eng['ok'], footer_bytes=eng['footer'])
    return P, uv, idx, meta

if __name__ == '__main__':
    import sys, os
    for p in sys.argv[1:]:
        try:
            P, uv, idx, meta = parse_mesh2(p)
            print('%s: v=%d f=%d subs=%d flags=%s extra=%d ok=%s state=%s trailing=%s bbox_span=(%.2f,%.2f,%.2f)' % (
                os.path.basename(p), meta['tv'], meta['tf'], len(meta['subs']),
                [hex(u) for u in meta['flags']], meta['n_extra'], meta['sizes_ok'],
                meta['extra_streams_state'], meta['trailing_bytes'],
                *(meta['bbox'][1] - meta['bbox'][0])))
        except Exception as e:
            print(os.path.basename(p), 'ERR:', e)
