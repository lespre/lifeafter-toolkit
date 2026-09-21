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
      extra_streams_state,vcol_read,...}
"""
import struct
import numpy as np

def parse_mesh2(path, load_vcol=True):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x34\x80\xc8\xbb', 'magic mismatch'
    ver = struct.unpack_from('<H', d, 4)[0]
    # 1) 定位 sub 表: 假设 0x0E 起每 10B 一项, 试探 k=1..10, 用 (term==1, tv==Σvc, tf==Σfc) 校验
    best = None
    for k in range(1, 11):
        off = 0x0E + 10 * k
        if off + 2 + 8 + 24 > len(d): break
        term = struct.unpack_from('<H', d, off)[0]
        tv, tf = struct.unpack_from('<II', d, off + 2)
        if term != 1 or tv == 0 or tf == 0: continue
        subs = [struct.unpack_from('<IIH', d, 0x0E + 10 * i) for i in range(k)]
        if sum(s[0] for s in subs) == tv and sum(s[1] for s in subs) == tf:
            best = (k, off, subs, tv, tf); break
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
                for key in (b'biped ', b'biped_'):
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
            if bone_block is None:
                raise ValueError('bone_block_layout_unrecognized')
            # 从骨块之后向后搜索 (term==1, tv==Σvc, tf==Σfc)，k 上限 64
            end = bone_block + 32 * n_bones
            for cand in range(end, min(len(d) - 34, end + 8192)):
                if struct.unpack_from('<H', d, cand)[0] != 1: continue
                tv2, tf2 = struct.unpack_from('<II', d, cand + 2)
                if tv2 == 0 or tf2 == 0: continue
                for k2 in range(1, 65):
                    b2 = cand - 10 * k2
                    if b2 < 0: break
                    subs2 = [struct.unpack_from('<IIH', d, b2 + 10 * i) for i in range(k2)]
                    if sum(s[0] for s in subs2) == tv2 and sum(s[1] for s in subs2) == tf2:
                        best = (k2, cand, subs2, tv2, tf2); break
                if best is not None: break
            if best is None:
                raise ValueError('bone_block_layout_unrecognized')
    if best is None:
        raise ValueError('无法定位 sub 表 (term/tv/tf 校验失败)')
    k, off, subs, tv, tf = best
    bbox = struct.unpack_from('<6f', d, off + 10)
    dataoff = off + 10 + 24
    pos_off = dataoff
    nrm_off = pos_off + tv * 6
    idx_off = nrm_off + tv * 6 + 2
    uv_off = idx_off + tf * 6
    after_uv = uv_off + tv * 4
    extra_bytes = len(d) - (after_uv + 16)
    # ★ 修正 2026-09-18（additive + 保守）：
    #   附加流数量必须用 **floor**。带骨骼块的 .mesh 变体在 UV 流之后还有一块不被本布局记账的数据
    #   （实测 24/24 extra_bytes 不整除 tv*4，比值 1.75/2.75/3.75/4.75…），原 round() 会**多算一条流**，
    #   导致下面读 vertex color 越过 EOF（ValueError: buffer is smaller than requested size）。
    #   现在：n_extra=floor（不虚报）；未记账尾部显式登记 trailing_bytes +
    #   extra_streams_state = exact | trailing_unaccounted | file_shorter_than_layout；
    #   sizes_ok 仍只在"整除"时为 True ⇒ 语义保持可判定，不静默截断、不伪造流。
    if tv and extra_bytes > 0:
        n_extra = int(extra_bytes // (tv * 4))
    else:
        n_extra = 0
    ok_sizes = (extra_bytes == n_extra * tv * 4)
    trailing_bytes = extra_bytes - n_extra * tv * 4
    if extra_bytes < 0:
        extra_streams_state = 'file_shorter_than_layout'
    elif ok_sizes:
        extra_streams_state = 'exact'
    elif extra_bytes > 0:
        extra_streams_state = 'trailing_unaccounted'
    else:
        extra_streams_state = 'none'
    bmin = np.array(bbox[:3], np.float32); bmax = np.array(bbox[3:], np.float32)
    pos_raw = np.frombuffer(d, dtype='<u2', count=tv * 3, offset=pos_off).reshape(-1, 3)
    f = (pos_raw.astype(np.float32) + 0.5) / 65536.0
    P = bmin + f * (bmax - bmin)
    idx = np.frombuffer(d, dtype='<u2', count=tf * 3, offset=idx_off).reshape(-1, 3).astype(np.int64)
    uv = np.frombuffer(d, dtype='<f2', count=tv * 2, offset=uv_off).reshape(-1, 2).astype(np.float32)
    extras = []
    for i in range(n_extra):
        o = after_uv + i * tv * 4
        extras.append(o)
    vcol = None
    vcol_read = None
    if n_extra >= 1 and load_vcol:
        co = extras[-1]
        if extra_streams_state != 'exact':
            # 保守：布局未完全记账（尾部有未解释数据）时**不猜**哪条流是顶点色 —— 不读、置 None
            vcol_read = dict(offset=co, count=tv * 4, state='skipped_layout_not_exact',
                             extra_streams_state=extra_streams_state, trailing_bytes=trailing_bytes)
        elif co + tv * 4 <= len(d):
            # 越界保护：不静默截断、不用短读凑数；能读才读
            vcol = np.frombuffer(d, dtype=np.uint8, count=tv * 4, offset=co).reshape(-1, 4).astype(np.float32) / 255.0
            vcol_read = dict(offset=co, count=tv * 4, state='read')
        else:
            vcol_read = dict(offset=co, count=tv * 4, eof=len(d), state='skipped_would_exceed_eof')
    o = 0; sub_offsets = []
    for vc, fc, u in subs:
        sub_offsets.append((o, o + vc)); o += vc
    meta = dict(ver=ver, subs=subs, flags=[u for _, _, u in subs], tv=tv, tf=tf,
                bbox=(bmin, bmax), dataoff=dataoff, n_extra=n_extra, extra_offsets=extras,
                extra_bytes=extra_bytes, sizes_ok=ok_sizes, vcol=vcol, sub_offsets=sub_offsets,
                # ★ 新增（additive）：未记账尾部与顶点色读取状态，供调用方判定
                trailing_bytes=trailing_bytes, extra_streams_state=extra_streams_state,
                vcol_read=vcol_read)
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
