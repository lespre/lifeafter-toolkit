# -*- coding: utf-8 -*-
"""
《明日之后》体验服资源包全面拆包器 lifeafter_unpacker_full.py
==============================================================
覆盖 E:\\mrzh 下已攻破的全部资源格式（完整解码能力汇总）。

功能模块（命令行参数）:
  extract-gpk   解包 .gpk（AES 头部 + 条目表 + zstd/lz4/原始 + 魔数识别）
  extract-fpk   解析 .fpk 头部（AES 解密 NXPK 头 + hash 表提取 + 体验服/正式服独有包对比）
  extract-fpk-full <fpk> <outdir>  全量拆包单个 fpk（NXPK头+条目表+zstd数据区+魔数识别）
  search-fpk <fpk> <kw1> [kw2...]  定向搜索单个 fpk（只提取含关键词的文件，UTF-8/GBK/UTF-16LE）
  search-all-fpk <kw1> [kw2...]     批量定向搜索所有体验服独有 fpk
  extract-wpk   解析 .wpk/.idx 容器（FKPW/SKPW 条目表 + 数据块提取 + MD5 撞库映射 gpk 明文）
  extract-npk   一步到位：script.py314.lc.npk 解包 + nxs 配置解密提取中文
  extract-nxs   按逻辑 .nxs 路径（双 Murmur3）从 npk 精确提取单表
  inspect-nxs   提取 + BinDict 解析（x{ framing / 0x76 索引 / CHS 字段池）
  verify-source source lock 校验：SHA-256 防旧 offset 误用新包
  decrypt-nxs   批量解密 .nxs 配置（AES-ECB + 16B 头 + zlib -> 提取中文/ASCII 文本）
  parse-thfb    解析 THFB 纹理索引（thx/thh -> hash 清单）
  extract-fsb   FSB5 音频库转 WAV（fsb5 + vgmstream 双通道）
  dds2png       DDS 贴图批量转 PNG
  detect        魔数/熵检测：识别真图片 vs 加密伪装数据
  stat          资源包统计

依赖: pip install pycryptodome lz4 zstandard fsb5 Pillow
vgmstream: 建议下载 r2117+ 到 VGMSTREAM_CLI（音频 FSB5 Vorbis 解码兜底）
"""
import struct, os, sys, json, time, re, math, hashlib
from collections import Counter

# 新增共享内核（同目录）。显式入 path，保证被其它目录下的脚本加载也能工作。
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import la_unpack_core as core

# ---------------------------------------------------------------- 常量
AES_KEY = bytes.fromhex('606308d8a32c782013d26c2f226f686d')
RES_DIR = r"E:\mrzh\res"
DOC_RES_DIR = r"E:\mrzh\Documents\res"
UNPACK_DIR = r"E:\la拆包项目\03拆包产物"
VGMSTREAM_CLI = r"C:\Users\Administrator\AppData\Local\Temp\vgm\ex\vgmstream-cli.exe"

MAGIC_TABLE = [
    (b'DDS ',            'DDS',   'dds'),
    (b'\x89PNG',         'PNG',   'png'),
    (b'\xff\xd8\xff',    'JPEG',  'jpg'),
    (b'BM',              'BMP',   'bmp'),
    (b'RIFF',            'RIFF',  'riff'),
    (b'OggS',            'OGG',   'ogg'),
    (b'\xabKTX ',        'KTX',   'ktx'),
    (b'ID3',             'MP3',   'mp3'),
    (b'\x1f\x8b',        'GZIP',  'gz'),
    (b'FBX',             'FBX',   'fbx'),
    (b'FSB',             'FSB',   'fsb'),
    (b'\xc1\x59\x41\x0d','c159',  'c159'),
    (b'RGIS',            'RGIS',  'rgis'),
    (b'\x31\x44\x50\x57','1DPW',  '1dpw'),
    (b'\x34\x80\xc8\xbb','MESH',  'mesh'),
]

# ================================================================ 通用 AES
def aes_decrypt_head(data, key=AES_KEY):
    from Crypto.Cipher import AES
    pad = (16 - len(data) % 16) % 16
    return AES.new(key, AES.MODE_ECB).decrypt(data + b'\x00' * pad)

# ================================================================ gpk
def parse_gpk_entries(path, max_head=64 * 1024 * 1024):
    from Crypto.Cipher import AES
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    with open(path, 'rb') as f:
        head = f.read(max_head)
    head = head + b'\x00' * ((16 - len(head) % 16) % 16)
    pt = cipher.decrypt(head)
    B = struct.unpack_from('<I', pt, 20)[0]
    need = 64 + B * 32
    if need > len(pt):
        with open(path, 'rb') as f:
            head2 = f.read(need + 64)
        head2 = head2 + b'\x00' * ((16 - len(head2) % 16) % 16)
        pt = cipher.decrypt(head2)
    fs = os.path.getsize(path)
    ents = []
    for i in range(B):
        base = 64 + i * 32
        if base + 32 > len(pt):
            break
        o, cmp_, dec_, c1, c2, fl = struct.unpack_from('<IIIIII', pt, base)
        if o >= 64 and o + 36 + cmp_ <= fs and fl in (0, 2, 12):
            ents.append((o, cmp_, dec_, c1, c2, fl))
    return ents

def ext_of(d):
    for magic, name, ext in MAGIC_TABLE:
        if d[:len(magic)] == magic:
            return '.' + ext
    if d[:2] == b'\xff\xd8' and d[2:4] not in (b'\xff\xe0', b'\xff\xe1', b'\xff\xe2', b'\xff\xdb', b'\xff\xc0', b'\xff\xc4', b'\xff\xda', b'\xff\xfe', b'\xff\xd9'):
        return '.enc_jpg'
    return '.bin'

def extract_gpk(path, outdir, max_entries=None):
    """解包 .gpk。flag 2 = LZ4；0 = 原样；其余尝试 zstd。

    2026-09-20：
    * zstd 改用 ``core.decompress_zstd``（**每线程一个实例**），修掉共享
      ``ZstdDecompressor`` 导致的 ``ACCESS_VIOLATION 0xC0000005`` 静默崩溃。
    * 记录 ``codec`` 统计；判不出的条目记 ``unresolved`` 并留痕（不静默当 raw）。
    """
    ents = parse_gpk_entries(path)
    manifest, ok, fail, total = [], 0, 0, 0
    codecs = Counter()
    unresolved = []
    os.makedirs(outdir, exist_ok=True)
    with open(path, 'rb') as f:
        for i, (o, cmp_, dec_, c1, c2, fl) in enumerate(ents):
            if max_entries and i >= max_entries:
                break
            try:
                f.seek(o + 36)
                seg = f.read(cmp_)
                if fl == 0:
                    d = seg
                    codec = 'raw'
                elif fl == 2:
                    d = core.decompress_lz4_block(seg, dec_)
                    codec = 'lz4'
                else:
                    d = core.decompress_zstd(seg, dec_)
                    codec = 'zstd'
                codecs[codec] += 1
                ext = ext_of(d)
                fn = os.path.join(outdir, '%06d%s' % (i, ext))
                with open(fn, 'wb') as fo:
                    fo.write(d)
                total += len(d); ok += 1
                manifest.append({'idx': i, 'offset': o, 'comp': cmp_, 'decomp': dec_,
                                 'crc1': c1, 'crc2': c2, 'flag': fl, 'codec': codec,
                                 'ext': ext, 'size': len(d)})
            except Exception as e:
                fail += 1
                codecs['unresolved'] += 1
                unresolved.append({'idx': i, 'offset': o, 'flag': fl, 'error': str(e)[:160]})
                manifest.append({'idx': i, 'offset': o, 'flag': fl, 'codec': 'unresolved',
                                 'error': str(e)[:160]})
    with open(os.path.join(outdir, 'manifest.json'), 'w', encoding='utf-8') as fo:
        json.dump({'source': path, 'files': len(ents), 'ok': ok, 'fail': fail,
                   'total_bytes': total, 'codec_counts': dict(codecs),
                   'unresolved': unresolved[:200], 'entries': manifest}, fo, ensure_ascii=False)
    return ok, fail, total

def extract_all_gpk(res_dir=RES_DIR, out_root=UNPACK_DIR):
    files = sorted(f for f in os.listdir(res_dir) if f.lower().endswith('.gpk'))
    print('待解包 gpk:', len(files))
    os.makedirs(out_root, exist_ok=True)
    for name in files:
        outdir = os.path.join(out_root, name[:-4])
        mf = os.path.join(outdir, 'manifest.json')
        if os.path.exists(mf):
            print('SKIP(已解)', name); continue
        t0 = time.time()
        ok, fail, total = extract_gpk(os.path.join(res_dir, name), outdir)
        print('%-24s ok=%-7d fail=%-4d out=%.1fMB %.1fs'
              % (name, ok, fail, total / 1048576, time.time() - t0))

# ================================================================ fpk
def parse_fpk(path):
    """解析 fpk：AES 解密头 -> NXPK 头 + hash 表。返回 dict 或 None"""
    sz = os.path.getsize(path)
    with open(path, 'rb') as f:
        head = f.read(8 * 1024 * 1024)
    pt = aes_decrypt_head(head)
    if pt[8:12] != b'NXPK':
        return None
    ver = struct.unpack_from('<I', pt, 12)[0]
    cnt = struct.unpack_from('<I', pt, 20)[0]
    n16 = struct.unpack_from('<I', pt, 16)[0]
    # hash 表 @32 起 16B/条
    hashes = []
    need = 32 + cnt * 16
    if need <= len(pt):
        for i in range(min(cnt, 500000)):
            hashes.append(pt[32 + i * 16: 32 + i * 16 + 16].hex())
    return {'magic': 'NXPK', 'version': ver, 'count': cnt, 'n16': n16,
            'size': sz, 'hashes': hashes}

def extract_fpk_header(res_dir=RES_DIR, out_root=UNPACK_DIR, official_dir=None):
    """解析全部 fpk 头，输出资源清单（hash 表），对比正式服独有包"""
    os.makedirs(out_root, exist_ok=True)
    report = []
    total_hash = 0
    for name in sorted(os.listdir(res_dir)):
        if not name.lower().endswith('.fpk'):
            continue
        fp = os.path.join(res_dir, name)
        info = parse_fpk(fp)
        if info is None:
            report.append({'file': name, 'status': '非NXPK/无法解析'})
            continue
        total_hash += info['count']
        report.append({'file': name, 'version': info['version'], 'count': info['count'],
                       'size_mb': round(info['size'] / 1048576, 1), 'status': 'NXPK'})
        # 保存 hash 清单
        with open(os.path.join(out_root, name[:-4] + '_hashes.txt'), 'w') as f:
            f.write('\n'.join(info['hashes']))
    # 独有包对比
    if official_dir:
        off_files = {f for f in os.listdir(official_dir) if f.lower().endswith('.fpk')}
        exp_files = {f for f in os.listdir(res_dir) if f.lower().endswith('.fpk')}
        only = sorted(exp_files - off_files)
        print('体验服独有 fpk:', only)
        with open(os.path.join(out_root, '体验服独有fpk.txt'), 'w') as f:
            f.write('\n'.join(only))
    for r in report:
        print(r)
    print('总计 fpk 条目(hash):', total_hash)
    with open(os.path.join(out_root, 'fpk清单.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

# ================================================================ fpk 全量拆包 + 定向搜索
def extract_fpk_full(path, outdir, max_files=None):
    """全量拆包单个 fpk：NXPK头 + AES解密条目表(48B/条) + 载荷解码 + 魔数识别。
    返回 (saved, stats_dict)。

    2026-09-20 修复（缺陷 1）：压缩类型不再用 ``clen != olen ⇒ zstd`` 猜测，
    改为**载荷魔数 / 试解判定**（``core.classify_codec``）：
    zstd 魔数 ``28 B5 2F FD`` → zstd；lz4 block 无魔数 → 试解且长度须 == ``olen``；
    再退 raw；判不出来记 ``unresolved``。
    实测：``E:\\LifeAfter\\res\\*.fpk`` 的 35,511 条压缩载荷**全部是 LZ4**，
    旧口径把它们全判成 zstd 并失败（+9 条越界 = 35,520 行 ZstdError）。

    ``stats`` 保持原有 ``{扩展名: 条数}`` 结构，并新增保留键：

    * ``stats['codec']``    → ``{'lz4': n, 'raw': n, 'zstd': n, 'unresolved': n}``
    * ``stats['unresolved']`` → 判不出压缩类型的条目样本（含容器/条目定位）
    """
    from Crypto.Cipher import AES
    c = AES.new(AES_KEY, AES.MODE_ECB)
    d = open(path, 'rb').read()
    size = len(d)
    # NXPK 头（前48字节AES解密）
    head = c.decrypt(d[:48] + b'\x00' * ((16 - 48 % 16) % 16))
    if head[8:12] != b'NXPK':
        print('  非NXPK:', path)
        return 0, {}
    entry_off = struct.unpack_from('<I', head, 16)[0]
    entry_n = struct.unpack_from('<I', head, 20)[0]
    ver = struct.unpack_from('<I', head, 12)[0]
    print('  %s: NXPK v%d 条目表@%d 条目数=%d' % (os.path.basename(path), ver, entry_off, entry_n))
    # 解密条目表
    seg = d[entry_off:entry_off + entry_n * 48]
    entries = c.decrypt(seg + b'\x00' * ((16 - len(seg) % 16) % 16))
    os.makedirs(outdir, exist_ok=True)
    stats = {}
    codecs = Counter()
    unresolved = []
    saved = 0
    manifest = []
    for i in range(entry_n):
        if max_files and i >= max_files:
            break
        e = entries[i*48:(i+1)*48]
        if len(e) < 48:
            break
        fid = struct.unpack_from('<Q', e, 0)[0]
        off = struct.unpack_from('<I', e, 8)[0]
        clen = struct.unpack_from('<I', e, 12)[0]
        olen = struct.unpack_from('<I', e, 16)[0]
        typ = struct.unpack_from('<I', e, 20)[0]
        flag = struct.unpack_from('<i', e, 28)[0]
        if not (32 < off < size and 0 < clen < 100*1024*1024 and 0 < olen < 200*1024*1024):
            codecs['out_of_bounds'] += 1
            unresolved.append({'entry_index': i, 'file_id': '%016X' % fid, 'offset': off,
                               'packed': clen, 'decoded': olen, 'flag': flag,
                               'reason': 'packed range outside source',
                               'container': os.path.basename(path)})
            continue
        raw = d[off:off+clen]
        result = core.classify_codec(raw, clen, olen, flag)
        codecs[result.codec] += 1
        if not result.ok:
            # 纪律：无法判定的压缩类型如实报 unresolved 并记录容器/条目。
            unresolved.append({'entry_index': i, 'file_id': '%016X' % fid, 'offset': off,
                               'packed': clen, 'decoded': olen, 'flag': flag,
                               'how': result.how, 'error': result.error,
                               'payload_head16': raw[:16].hex(),
                               'container': os.path.basename(path)})
            continue
        data = result.data
        ext = ext_of(data)
        stats[ext] = stats.get(ext, 0) + 1
        fn = '%05d%s' % (i, ext)
        with open(os.path.join(outdir, fn), 'wb') as fo:
            fo.write(data)
        manifest.append({'idx': i, 'file_id': '%016X' % fid, 'offset': off,
                         'packed': clen, 'decoded': olen, 'type': typ, 'flag': flag,
                         'codec': result.codec, 'codec_how': result.how,
                         'ext': ext, 'size': len(data), 'file': fn})
        saved += 1
    stats['codec'] = dict(codecs)
    stats['unresolved'] = unresolved[:200]
    with open(os.path.join(outdir, 'manifest.json'), 'w', encoding='utf-8') as fo:
        json.dump({'source': path, 'version': ver, 'entry_count': entry_n,
                   'saved': saved, 'stats': stats,
                   'codec_counts': dict(codecs),
                   'unresolved_count': len(unresolved),
                   'unresolved': unresolved[:200], 'entries': manifest}, fo, ensure_ascii=False)
    print('  提取 %d 个文件: %s' % (saved, dict((k, v) for k, v in stats.items()
                                                if k not in ('codec', 'unresolved'))))
    print('  压缩类型统计: %s  未判定: %d' % (dict(codecs), len(unresolved)))
    return saved, stats

def search_fpk(path, keywords, outdir=None, max_scan=None, encodings=None):
    """定向搜索 fpk：解密条目表后逐条目读取数据区，搜索关键词(UTF-8/GBK/UTF-16LE)，
    只提取命中的文件。keywords 为字符串列表。返回命中列表。

    2026-09-20 修复（缺陷 1）：与 ``extract_fpk_full`` 同样改用
    ``core.classify_codec`` 的魔数/试解判定，不再把 LZ4 载荷误判为 zstd
    然后静默退回压缩字节（那会让关键词搜索在压缩数据上必然搜不到）。
    """
    from Crypto.Cipher import AES
    c = AES.new(AES_KEY, AES.MODE_ECB)
    d = open(path, 'rb').read()
    size = len(d)
    head = c.decrypt(d[:48] + b'\x00' * ((16 - 48 % 16) % 16))
    if head[8:12] != b'NXPK':
        print('  非NXPK:', path); return []
    entry_off = struct.unpack_from('<I', head, 16)[0]
    entry_n = struct.unpack_from('<I', head, 20)[0]
    seg = d[entry_off:entry_off + entry_n * 48]
    entries = c.decrypt(seg + b'\x00' * ((16 - len(seg) % 16) % 16))
    encs = encodings or ['utf-8', 'gbk', 'utf-16-le']
    hits = []
    codecs = Counter()
    unresolved = []
    scan_n = min(entry_n, max_scan) if max_scan else entry_n
    for i in range(scan_n):
        e = entries[i*48:(i+1)*48]
        if len(e) < 48: break
        fid = struct.unpack_from('<Q', e, 0)[0]
        off = struct.unpack_from('<I', e, 8)[0]
        clen = struct.unpack_from('<I', e, 12)[0]
        olen = struct.unpack_from('<I', e, 16)[0]
        flag = struct.unpack_from('<i', e, 28)[0]
        if not (32 < off < size and 0 < clen < 100*1024*1024):
            codecs['out_of_bounds'] += 1
            continue
        raw = d[off:off+clen]
        result = core.classify_codec(raw, clen, olen, flag)
        codecs[result.codec] += 1
        if not result.ok:
            unresolved.append({'idx': i, 'file_id': '%016X' % fid, 'offset': off,
                               'packed': clen, 'decoded': olen, 'flag': flag,
                               'how': result.how, 'error': result.error,
                               'container': os.path.basename(path)})
            continue
        data = result.data
        # 只扫描前 64KB（文本配置通常不大）
        scan_data = data[:65536]
        matched = []
        for kw in keywords:
            for enc in encs:
                try:
                    if kw.encode(enc) in scan_data:
                        matched.append(kw)
                        break
                except Exception:
                    continue
        if matched:
            ext = ext_of(data)
            hit = {'idx': i, 'file_id': '%016X' % fid, 'offset': off, 'packed': clen,
                   'decoded': olen, 'flag': flag, 'codec': result.codec,
                   'ext': ext, 'size': len(data), 'keywords': matched}
            hits.append(hit)
            if outdir:
                os.makedirs(outdir, exist_ok=True)
                fn = '%05d%s' % (i, ext)
                with open(os.path.join(outdir, fn), 'wb') as fo:
                    fo.write(data)
                hit['file'] = fn
    print('  %s: 扫描%d条, 命中%d个, 压缩类型=%s, 未判定=%d'
          % (os.path.basename(path), scan_n, len(hits), dict(codecs), len(unresolved)))
    search_fpk.last_codec_counts = dict(codecs)
    search_fpk.last_unresolved = unresolved
    return hits

def search_all_fpk(res_dir, keywords, out_root, only_exclusive=True, official_dir=None):
    """批量定向搜索所有 fpk。only_exclusive=True 时只搜体验服独有包（正式服没有的）。"""
    os.makedirs(out_root, exist_ok=True)
    exp_files = sorted(f for f in os.listdir(res_dir) if f.lower().endswith('.fpk'))
    if only_exclusive and official_dir:
        off_files = {f for f in os.listdir(official_dir) if f.lower().endswith('.fpk')}
        targets = [f for f in exp_files if f not in off_files]
        print('体验服独有 fpk (%d个): %s' % (len(targets), targets))
    else:
        targets = exp_files
        print('全部 fpk (%d个)' % len(targets))
    all_hits = {}
    for name in targets:
        fp = os.path.join(res_dir, name)
        outdir = os.path.join(out_root, name[:-4])
        hits = search_fpk(fp, keywords, outdir=outdir)
        if hits:
            all_hits[name] = hits
    # 汇总
    report = {'keywords': keywords, 'total_hits': sum(len(v) for v in all_hits.values()),
              'per_file': {k: len(v) for k, v in all_hits.items()},
              'details': all_hits}
    with open(os.path.join(out_root, 'search_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print('\n=== 搜索汇总 ===')
    print('关键词:', keywords)
    print('总命中:', report['total_hits'])
    for name, cnt in sorted(report['per_file'].items(), key=lambda x: -x[1]):
        print('  %s: %d个' % (name, cnt))
    return report

# ================================================================ wpk / idx
# 2026-09-20 修复（缺陷 2）：LA 的资源包在 pkg >= 10 时用**单个十六进制字母**做后缀，
# 且大小写混用：charactera..f.wpk（小写）与 modelA..E.wpk（大写）在同一目录并存。
# 旧口径 '%s%d.wpk' 只会拼出 character10.wpk 这类名字，文件不存在 → 静默跳过。
# 实测（E:\mrzh\Documents\res）：character 家族 13 个 .wpk 里 6 个是十六进制名，
# model 家族 12 个里 5 个是十六进制名；旧口径少解 1,020 + 573 = 1,593 条。

WPK_SKIP_LOG = core.SkipLog(stage='wpk_resolution')


def enumerate_wpk_files(directory, family=None):
    """枚举目录下所有 .wpk；给了 family 就只留 ``<family><后缀>.wpk``。

    ``<后缀>`` 允许 ``[0-9A-Fa-f]+``，所以十进制与十六进制名都能覆盖。
    返回 ``{文件名: 后缀}``。
    """
    if family is None:
        found = {}
        try:
            names = os.listdir(directory)
        except OSError:
            return found
        for name in sorted(names):
            if name.lower().endswith('.wpk') and os.path.isfile(os.path.join(directory, name)):
                found[name] = os.path.splitext(name)[0]
        return found
    return core.enumerate_family_wpk(directory, family)


def wpk_name_candidates(family, pkg):
    """生成候选包名：``[十进制, 十六进制大写, 十六进制小写]``（去重保序）。"""
    return core.wpk_name_candidates(family, pkg)


def resolve_wpk_path(directory, family, pkg, log=True):
    """把 ``(目录, 家族, 包号)`` 解析为实际 ``.wpk`` 路径。

    返回 ``(路径 或 None, 说明 dict)``。**解析不到时必定记录原因**，不静默跳过。
    ``pkg == 255`` 是 slot file 标记，条目不在任何 .wpk 里。
    """
    return core.resolve_wpk_path(directory, family, pkg, WPK_SKIP_LOG if log else None)


def iter_idx_entries(idx_path):
    """解析 ``.idx`` 条目表（32 B 头 + 36 B/条），并补上解析出的 ``wpk_path``。

    ``pkg`` 取自记录内偏移 ``0x14`` 的低字节；``hdr_size`` 取自 ``0x20``（u16）——
    **不写死 48**，与 ``MarcosVLl2/NeoXtractor core/wpk/idx_reader.py`` 一致。
    """
    entries = core.parse_idx_entries(idx_path)
    directory = os.path.dirname(os.path.abspath(idx_path))
    family = os.path.splitext(os.path.basename(idx_path))[0]
    for entry in entries:
        path, info = resolve_wpk_path(directory, family, entry['pkg'])
        entry['wpk_path'] = path
        entry['wpk_resolution'] = info
    return entries


def parse_wpk_idx(idx_path, wpk_path, gpk_md5_index=None):
    """解析 wpk+idx 容器：idx 条目(hash+offset+size) -> wpk 数据块；hash=内容MD5 撞库映射。
    gpk_md5_index: {md5_hex: 路径}，命中则说明该块与 gpk 明文一致（可绕过 1DPW 加密）

    签名不变。2026-09-20 加固：
    * ``hdr_size`` 改为**从 idx 记录读出**（偏移 0x20，u16），不再写死 48。
    * 越界条目**记录原因**（``e['skipped_reason']`` + ``WPK_SKIP_LOG``），不再静默丢。
    * 新增 ``codec`` 字段说明该块是否带 1DPW 外层。
    """
    idx = open(idx_path, 'rb').read()
    wpk = open(wpk_path, 'rb').read()
    # idx 头 32B，条目 36B
    entries = []
    for i in range(32, len(idx) - 35, 36):
        h = idx[i:i + 16]
        f1, f2, off, size = struct.unpack_from('<IIII', idx, i + 16)
        hdr_size = struct.unpack_from('<H', idx, i + 32)[0]
        entries.append({'hash': h.hex(), 'off': off, 'size': size, 'f1': f1, 'f2': f2,
                        'pkg': f2 & 0xFF, 'hdr_size': hdr_size,
                        'total_size': hdr_size + size})
    print('wpk 条目数:', len(entries))
    ok = miss = 0
    out = []
    for e in entries:
        off, size, hdr_size = e['off'], e['size'], e['hdr_size']
        if off + hdr_size + size > len(wpk):
            miss += 1
            e['skipped_reason'] = 'entry_range_outside_wpk'
            WPK_SKIP_LOG.record('entry_range_outside_wpk', offset=off, header=hdr_size,
                                payload=size, wpk_size=len(wpk))
            out.append(e)
            continue
        blk = wpk[off:off + hdr_size + size]
        if blk[:4] == b'1DPW':
            e['codec'] = '1dpw_wrapped'
            data = blk[hdr_size:hdr_size + size]
        else:
            e['codec'] = 'bare'
            data = blk[:size] if hdr_size == 0 else blk[hdr_size:hdr_size + size]
        md5 = hashlib.md5(data).hexdigest()
        mapped = None
        if gpk_md5_index:
            mapped = gpk_md5_index.get(md5) or gpk_md5_index.get(e['hash'])
        if mapped:
            ok += 1
            e['matched_gpk'] = mapped
        else:
            miss += 1
            e['unmatched'] = True
        out.append(e)
    print('匹配 gpk 明文:', ok, ' 未匹配(1DPW加密):', miss)
    return out

def build_gpk_md5_index(gpk_unpacked_root):
    """构建 gpk 明文库的 MD5 -> 路径 索引（慢，仅首次）"""
    index = {}
    for root, dirs, files in os.walk(gpk_unpacked_root):
        for f in files:
            if not f.lower().endswith(('.dds', '.png', '.jpg')):
                continue
            p = os.path.join(root, f)
            try:
                md5 = hashlib.md5(open(p, 'rb').read()).hexdigest()
                index[md5] = os.path.relpath(p, gpk_unpacked_root)
            except Exception:
                pass
    return index

# ================================================================ npk 脚本包
def murmur3_x86_32(data, seed):
    """MurmurHash3 x86 32-bit（与网易 NX 包路径 ID 算法一致）"""
    c1, c2 = 0xCC9E2D51, 0x1B873593
    value = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for off in range(0, end, 4):
        block = int.from_bytes(data[off:off + 4], 'little')
        block = (block * c1) & 0xFFFFFFFF
        block = ((block << 15) | (block >> 17)) & 0xFFFFFFFF
        block = (block * c2) & 0xFFFFFFFF
        value ^= block
        value = ((value << 13) | (value >> 19)) & 0xFFFFFFFF
        value = (value * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[end:]
    block = 0
    if len(tail) >= 3: block ^= tail[2] << 16
    if len(tail) >= 2: block ^= tail[1] << 8
    if tail:
        block ^= tail[0]
        block = (block * c1) & 0xFFFFFFFF
        block = ((block << 15) | (block >> 17)) & 0xFFFFFFFF
        block = (block * c2) & 0xFFFFFFFF
        value ^= block
    value ^= len(data)
    value ^= value >> 16
    value = (value * 0x85EBCA6B) & 0xFFFFFFFF
    value ^= value >> 13
    value = (value * 0xC2B2AE35) & 0xFFFFFFFF
    value ^= value >> 16
    return value & 0xFFFFFFFF

def path_id(logical_path):
    """逻辑 .nxs 路径 → 64 位 file_id（双 Murmur3：高 seed 0x77777777，低 seed 0x66666666）"""
    encoded = logical_path.encode('utf-8')
    return (murmur3_x86_32(encoded, 0x77777777) << 32) | murmur3_x86_32(encoded, 0x66666666)

def lz4_decompress(blob, expected):
    """LZ4 block 解压（小端 16-bit offset 标准 LZ4 block 格式）"""
    out = bytearray()
    pos = 0
    def ext(v):
        nonlocal pos
        if v == 15:
            while True:
                if pos >= len(blob): raise ValueError('lz4 ext truncated')
                part = blob[pos]; pos += 1
                v += part
                if part != 255: break
        return v
    while pos < len(blob) and len(out) < expected:
        token = blob[pos]; pos += 1
        lit = ext(token >> 4)
        if pos + lit > len(blob): raise ValueError('lz4 lit overflow')
        out.extend(blob[pos:pos + lit]); pos += lit
        if pos >= len(blob): break
        if pos + 2 > len(blob): raise ValueError('lz4 offset truncated')
        dist = blob[pos] | (blob[pos + 1] << 8); pos += 2
        if dist == 0 or dist > len(out): raise ValueError('lz4 bad dist')
        mlen = ext(token & 15) + 4
        rd = len(out) - dist
        for _ in range(mlen):
            out.append(out[rd]); rd += 1
    if len(out) != expected: raise ValueError('lz4 out %d != %d' % (len(out), expected))
    return bytes(out)

def unpack_entry(packed, expected_size, flag):
    """NPK 条目解压：flag 0=AES+zlib；2=lz4；12=zstd。返回明文 bytes（签名不变）。

    2026-09-20：flag 2 走原生 LZ4；flag 12 走 ``core.decompress_zstd``（每线程一个实例，
    修掉共享 ``ZstdDecompressor`` 导致的 ``ACCESS_VIOLATION 0xC0000005`` 静默崩溃）；
    其它 flag 不再静默原样返回，改走魔数/试解并如实报 ``unresolved``。
    """
    if flag in (0, 2, 12):
        return core.npk_decode_entry(packed, expected_size, flag)
    return core.npk_decode_entry(packed, expected_size, flag)


def unpack_entry_ex(packed, expected_size, flag):
    """``unpack_entry`` 的带判定信息版本（新增）：返回 ``core.CodecResult``。

    ``result.codec`` ∈ ``{'raw','lz4','zstd','aes_zlib','unresolved'}``，
    ``result.how`` 记录判定依据。判不出来时 ``result.ok is False`` 且 ``error`` 有原因。
    """
    if flag == 0:
        try:
            data = core.npk_decode_entry(packed, expected_size, flag)
        except Exception as exc:  # noqa: BLE001
            return core.CodecResult('unresolved', None, 'flag0_aes_zlib_failed',
                                    len(packed), expected_size, flag, repr(exc))
        if data is packed:
            return core.CodecResult('raw', data, core.CODEC_HOW_FLAG_RAW,
                                    len(packed), expected_size, flag)
        return core.CodecResult('aes_zlib', data, 'flag0_aes_zlib',
                                len(packed), expected_size, flag)
    if flag == 2:
        try:
            data = core.decompress_lz4_block(packed, expected_size)
        except Exception as exc:  # noqa: BLE001
            return core.CodecResult('unresolved', None, core.CODEC_HOW_FLAG_LZ4,
                                    len(packed), expected_size, flag, repr(exc))
        return core.CodecResult('lz4', data, core.CODEC_HOW_FLAG_LZ4,
                                len(packed), expected_size, flag)
    return core.classify_codec(packed, len(packed), expected_size, flag)

def extract_npk(path, outdir):
    """从 npk 解包全部条目（AES 解 NXPK 头 + 条目表 + 完整解压）。
    写明文文件并生成 manifest.json（file_id → 条目索引/逻辑路径）。"""
    from Crypto.Cipher import AES
    c = AES.new(AES_KEY, AES.MODE_ECB)
    d = open(path, 'rb').read()
    size = len(d)
    head = c.decrypt(d[:64] + b'\x00' * ((16 - 64 % 16) % 16))
    if head[8:12] != b'NXPK':
        print('非 NXPK:', path)
        return 0
    entry_off = struct.unpack_from('<I', head, 16)[0]
    entry_n = struct.unpack_from('<I', head, 20)[0]
    print('NXPK 条目@%d 条目数=%d' % (entry_off, entry_n))
    seg = d[entry_off:entry_off + entry_n * 48]
    entries = c.decrypt(seg + b'\x00' * ((16 - len(seg) % 16) % 16))
    os.makedirs(outdir, exist_ok=True)
    saved = 0
    manifest = []
    for i in range(entry_n):
        e = entries[i * 48:(i + 1) * 48]
        if len(e) < 48:
            break
        fid = struct.unpack_from('<Q', e, 0)[0]
        off = struct.unpack_from('<I', e, 8)[0]
        psize = struct.unpack_from('<I', e, 12)[0]
        dsize = struct.unpack_from('<I', e, 16)[0]
        flag = struct.unpack_from('<i', e, 28)[0]
        if not (32 < off < size and 0 < psize < 200 * 1024 * 1024):
            continue
        packed = d[off:off + psize]
        try:
            raw = unpack_entry(packed, dsize, flag)
        except Exception:
            raw = packed
        fn = '%06d.bin' % i
        with open(os.path.join(outdir, fn), 'wb') as fo:
            fo.write(raw)
        manifest.append({'index': i, 'file_id': '%016X' % fid, 'offset': off,
                         'packed': psize, 'decoded': dsize, 'flag': flag, 'file': fn})
        saved += 1
    with open(os.path.join(outdir, 'manifest.json'), 'w', encoding='utf-8') as fo:
        json.dump(manifest, fo, ensure_ascii=False)
    print('解包 %d 文件到 %s' % (saved, outdir))
    return saved

def extract_nxs_by_path(npk_path, logical_path, outfile=None):
    """按逻辑 .nxs 路径（双 Murmur3）从 npk 精确定位并解出条目。返回明文 bytes"""
    from Crypto.Cipher import AES
    c = AES.new(AES_KEY, AES.MODE_ECB)
    d = open(npk_path, 'rb').read()
    head = c.decrypt(d[:64])
    entry_off = struct.unpack_from('<I', head, 16)[0]
    entry_n = struct.unpack_from('<I', head, 20)[0]
    seg = d[entry_off:entry_off + entry_n * 48]
    entries = c.decrypt(seg + b'\x00' * ((16 - len(seg) % 16) % 16))
    fid = path_id(logical_path)
    for i in range(entry_n):
        e = entries[i * 48:(i + 1) * 48]
        if struct.unpack_from('<Q', e, 0)[0] == fid:
            off = struct.unpack_from('<I', e, 8)[0]
            psize = struct.unpack_from('<I', e, 12)[0]
            dsize = struct.unpack_from('<I', e, 16)[0]
            flag = struct.unpack_from('<i', e, 28)[0]
            raw = unpack_entry(d[off:off + psize], dsize, flag)
            print('命中 file_id=%016X 条目%d flag=%d 解出%dB' % (fid, i, flag, len(raw)))
            if outfile:
                open(outfile, 'wb').write(raw)
                print('已存', outfile)
            return raw
    print('未找到 file_id=%016X（路径 %s）' % (fid, logical_path))
    return None

# ================================================================ BinDict 解析（与 hermes 接力包交叉印证）
def uleb128(buf, pos, end):
    v = 0; sh = 0
    while pos < end:
        b = buf[pos]; pos += 1
        v |= (b & 0x7f) << sh
        if not (b & 0x80):
            return v, pos
        sh += 7
        if sh > 63:
            raise ValueError('ULEB>64')
    raise ValueError('truncated ULEB')

def parse_bindict_xbrace(raw):
    """custom BinDict `x{` + u32le(body_len)：返回 framing / 0x76 尾索引 / key→value-start / value spans。
    仅边界验证，value 内部 tag/字段语义不解。"""
    marker = raw.find(b'x{')
    if marker < 0:
        raise ValueError('x{ marker missing')
    body_len = struct.unpack_from('<I', raw, marker + 2)[0]
    body_start = marker + 6; body_end = body_start + body_len
    if body_end > len(raw):
        raise ValueError('x{ body exceeds payload')
    body = raw[body_start:body_end]
    slot_count, reserved = struct.unpack_from('<II', body, 0)
    ends = list(struct.unpack_from('<%dI' % slot_count, body, 8))
    blob = body[8 + 4 * slot_count:]
    data_end = struct.unpack_from('<I', blob, 0)[0]
    tail = blob[data_end:]
    if tail[:3] != b'\x76\x0b\x0b':
        raise ValueError('tail tag %s' % tail[:4].hex())
    bucket_count = tail[3]
    pair_end = 4 + bucket_count * 8
    nodes = []
    for i in range(bucket_count):
        bh, ptr = struct.unpack_from('<II', tail, 4 + i * 8)
        if not (pair_end <= ptr < len(blob)):
            raise ValueError('bucket ptr %d' % ptr)
        nodes.append((bh, ptr))
    positions = sorted({p for _, p in nodes})
    rows = {}
    for idx, pos in enumerate(positions):
        end = positions[idx + 1] if idx + 1 < len(positions) else len(blob)
        key, nxt = uleb128(blob, pos, end)
        vstart, final = uleb128(blob, nxt, end)
        if final != end:
            raise ValueError('node trailing bytes')
        rows[key] = vstart
    values = sorted(set(rows.values()))
    spans = [[v, values[i + 1] if i + 1 < len(values) else data_end] for i, v in enumerate(values)]
    return {'marker': marker, 'body_len': body_len, 'body_start': body_start, 'body_end': body_end,
            'slot_count': slot_count, 'reserved': reserved, 'ends': ends,
            'data_blob_len': len(blob), 'data_end': data_end,
            'tail_header_hex': tail[:4].hex(), 'bucket_count': bucket_count,
            'node_pointer': 'full_u32_relative_to_data_blob', 'rows': rows, 'value_spans': spans}

def parse_bindict_chs(raw):
    """CHS BinDict：direct `{` + u32le(body_len) + ends 表切 UTF-8 字符串池。返回字段名列表。"""
    for marker, byte in enumerate(raw):
        if byte != 0x7b or marker + 5 > len(raw):
            continue
        body_len = struct.unpack_from('<I', raw, marker + 1)[0]
        start, end = marker + 5, marker + 5 + body_len
        if end > len(raw) or body_len < 8:
            continue
        slot_count, reserved = struct.unpack_from('<II', raw, start)
        table_end = start + 8 + 4 * slot_count
        if not (0 < slot_count <= 128 and table_end <= end):
            continue
        ends = list(struct.unpack_from('<%dI' % slot_count, raw, start + 8))
        data = raw[table_end:end]
        if ends != sorted(ends) or (ends and ends[-1] > len(data)):
            continue
        try:
            strings = [data[(ends[i - 1] if i else 0):ends[i]].decode('utf-8') for i in range(slot_count)]
        except UnicodeDecodeError:
            continue
        return {'marker': marker, 'body_len': body_len, 'body_start': start, 'body_end': end,
                'slot_count': slot_count, 'reserved': reserved, 'ends': ends, 'strings': strings}
    raise ValueError('no valid CHS brace frame')

def inspect_nxs(npk_path, logical_path):
    """按路径提取 nxs 并解析 BinDict（x{ + CHS），一步到位。"""
    raw = extract_nxs_by_path(npk_path, logical_path)
    if not raw:
        return None
    out = {'path': logical_path, 'raw_size': len(raw)}
    try:
        out['bindict_xbrace'] = parse_bindict_xbrace(raw)
    except Exception as e:
        out['bindict_xbrace_error'] = repr(e)
    try:
        out['bindict_chs'] = parse_bindict_chs(raw)
    except Exception as e:
        out['bindict_chs_error'] = repr(e)
    return out

def verify_source_lock(npk_path, expected_sha=None):
    """source lock：校验当前包 SHA-256，防止用旧 offset 分析新包。"""
    h = hashlib.sha256()
    with open(npk_path, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    sha = h.hexdigest()
    exp = expected_sha or '7dc81841eb269a1eddce16415d961a5b655ff2631b6ab00417caa73a90ad6073'
    ok = sha == exp
    print('source lock: %s' % ('PASS' if ok else 'MISMATCH'))
    print('  live : %s' % sha)
    print('  expect: %s' % exp)
    if not ok:
        print('  !! 源包已更新，旧 offset/slot/value 全部降级为线索，须重新提取')
    return ok

# ================================================================ BinDict value record（与 hermes 交叉印证）
WEAPON_KIND = {1:'突击步枪',2:'步枪',3:'轻机枪',4:'霰弹枪',5:'狙击枪',6:'手枪及双枪',50:'冷兵器',
               51:'弓箭',52:'近战武器'}

def decode_bindict_record_9632(blob, start, end):
    """转印器小表 value grammar（已验证字节边界，禁赋业务语义）：
    96 32 + 6×ULEB128 + 0..n×(27 kind 02 ULEB128 ULEB128)，kind∈{01,0b}。
    返回 ULEB 值与 group 清单；0x0B 保持 opaque。"""
    pos = start
    if blob[pos:pos+2] != b'\x96\x32':
        raise ValueError('96 32 prefix missing at %d' % start)
    pos += 2
    six = []
    for _ in range(6):
        v, pos = uleb128(blob, pos, end)
        six.append(v)
    groups = []
    while pos < end:
        if pos + 3 > end or blob[pos] != 0x27:
            raise ValueError('group tag invalid at %d' % pos)
        kind, fixed = blob[pos+1], blob[pos+2]
        if kind not in (0x01, 0x0B) or fixed != 0x02:
            raise ValueError('group header invalid at %d' % pos)
        pos += 3
        a, pos = uleb128(blob, pos, end)
        b, pos = uleb128(blob, pos, end)
        groups.append({'kind': 'opaque_jump' if kind == 0x0B else 'val', 'pair': [a, b]})
    if pos != end:
        raise ValueError('span not closed')
    return {'prefix': '96 32', 'six_uleb': six, 'groups': groups}

def decode_bindict_record_9618(blob, start, end):
    """weapon_skin_behavior_res record grammar（已验证，与 hermes Type5 链交叉印证）：
    96 18 + field_count 位 field_control_bitmap + 每个 set bit 一个 ULEB，精确消费到 record 边界。
    0x0B 保持 opaque relative jump/reference。"""
    pos = start
    if blob[pos:pos+2] != b'\x96\x18':
        raise ValueError('96 18 prefix missing at %d' % start)
    pos += 2
    field_count = blob[pos]; pos += 1
    nbytes = (field_count + 7) // 8
    bm = blob[pos:pos+nbytes]; pos += nbytes
    bitmap_int = int.from_bytes(bm, 'little')
    values = []
    for f in range(field_count):
        if bitmap_int & (1 << f):
            v, pos = uleb128(blob, pos, end)
            values.append({'field': f, 'uleb': v})
    if pos != end:
        raise ValueError('record not closed (pos %d != end %d)' % (pos, end))
    return {'prefix': '96 18', 'field_count': field_count, 'bitmap_bytes': nbytes,
            'bitmap_hex': bm.hex(), 'set_bits': len(values), 'values': values}

def decode_bindict_value(npk_path, logical_path, fmt='auto'):
    """提取表并对每个 value span 按 record grammar 解码（仅字节边界/结构，不赋业务语义）。
    fmt: 9632=转印小表风格, 9618=weapon_skin_behavior_res 风格, auto=按前缀自动。"""
    raw = extract_nxs_by_path(npk_path, logical_path)
    if not raw:
        return None
    try:
        base = parse_bindict_xbrace(raw)
    except Exception as e:
        return {'error': repr(e)}
    blob_start = base['body_start'] + 32
    blob = raw[blob_start:blob_start + base['data_blob_len']]
    out = []
    for span in base['value_spans']:
        s, e = span
        pre = blob[s:s+2].hex()
        use = fmt if fmt != 'auto' else ('9618' if pre == '9618' else '9632')
        try:
            if use == '9618':
                rec = decode_bindict_record_9618(blob, s, e)
            else:
                rec = decode_bindict_record_9632(blob, s, e)
            rec['span'] = span
            out.append(rec)
        except Exception as exc:
            out.append({'span': span, 'prefix': pre, 'error': repr(exc)})
    return {'path': logical_path, 'rows': base['rows'], 'decoded_spans': out,
            'boundary': 'structure/byte-boundary only; no item/count/field semantics asserted; 0x0B is opaque'}

def npk_extract_and_decrypt(npk_path, outdir, txt_out=None):
    """一步到位：npk 解包 + nxs 解密提取中文。txt_out 为 None 时不写文本文件"""
    import zlib
    tmp = os.path.join(outdir, '_raw')
    os.makedirs(tmp, exist_ok=True)
    n = extract_npk(npk_path, tmp)
    nxss = fail = 0
    fout = open(txt_out, 'w', encoding='utf-8') if txt_out else None
    try:
        for i in range(n):
            fn = os.path.join(tmp, '%06d.bin' % i)
            try:
                res = extract_nxs_text(fn)
            except Exception:
                res = None
            if not res:
                fail += 1
                continue
            c, a = res
            if not c:
                continue
            nxss += 1
            if fout:
                fout.write('%06d.bin\tnxs\t%s\n' % (i, '|'.join(c)))
    finally:
        if fout:
            fout.close()
    print('nxs 解密成功(含中文): %d  失败: %d' % (nxss, fail))
    return n

# ================================================================ nxs 配置
def decrypt_nxs(path):
    """解密 nxs 配置（AES-ECB + 16B 头 + zlib）。返回解压后的 bytes 或 None"""
    import zlib
    data = open(path, 'rb').read()
    if len(data) < 40:
        return None
    try:
        dec = aes_decrypt_head(data)
        for off in (16, 8, 0, 24, 32):
            try:
                return zlib.decompress(dec[off:])
            except Exception:
                continue
    except Exception:
        return None
    return None

def extract_nxs_text(path, out_txt=None):
    """解密 nxs 并提取中文+ASCII 字符串"""
    import zlib
    raw = decrypt_nxs(path)
    if raw is None:
        return None
    # 中文 UTF-8
    t = raw.decode('utf-8', 'ignore')
    c = list(dict.fromkeys(re.findall(r'[\u4e00-\u9fff]{2,}', t)))
    a = [s.decode('ascii', 'ignore') for s in re.findall(rb'[\x20-\x7e]{3,}', raw)]
    return c, a

def decrypt_nxs_batch(indir, out_txt, hot_kw=None, max_files=None):
    """批量解密目录内全部 nxs 配置，输出中文文本"""
    import zlib
    files = [f for f in os.listdir(indir)]
    if max_files:
        files = files[:max_files]
    nxss = pycs = fail = 0
    hot = hot_kw or ['时装', '皮肤', '称号', '铠甲', '刑天', '帝皇', '飞影', '核芯', '转移', 'aug', 'AUG']
    with open(out_txt, 'w', encoding='utf-8') as fo:
        for fname in files:
            fp = os.path.join(indir, fname)
            try:
                res = extract_nxs_text(fp)
            except Exception:
                res = None
            if not res:
                fail += 1
                continue
            c, a = res
            if not c:
                pycs += 1
                continue
            nxss += 1
            fo.write(f'{fname}\tnxs\t{"|".join(c)}\n')
    print(f'nxs 解密成功(含中文): {nxss}  无中文: {pycs}  失败: {fail}')
    print('输出:', out_txt)

# ================================================================ THFB
def parse_thfb(path):
    """解析 THFB (thx/thh) 纹理索引。返回 (type, entries)"""
    b = open(path, 'rb').read()
    if b[:4] != b'THFB':
        return None
    ftype = struct.unpack_from('>I', b, 28)[0]   # 大端 1=thx 5=thh
    n = (len(b) - 104) // 56 if ftype == 1 else (len(b) - 104) // 16
    hashes = []
    for i in range(n):
        off = 104 + i * (56 if ftype == 1 else 16)
        hashes.append(b[off:off + 16].hex())
    return {'type': ftype, 'count': n, 'hashes': hashes}

def extract_all_thfb(dirs, out_txt):
    total = 0
    seen = set()
    with open(out_txt, 'w') as fo:
        for d in dirs:
            if not os.path.exists(d):
                continue
            for f in os.listdir(d):
                if not (f.endswith('.thx') or f.endswith('.thh')):
                    continue
                info = parse_thfb(os.path.join(d, f))
                if not info:
                    continue
                for h in info['hashes']:
                    if h not in seen:
                        seen.add(h)
                        fo.write(h + '\n')
                        total += 1
    print('THFB 唯一纹理 hash 数:', total)

# ================================================================ FSB5
def extract_fsb(path, outdir, pattern=None):
    import fsb5
    os.makedirs(outdir, exist_ok=True)
    data = open(path, 'rb').read()
    fsb = fsb5.FSB5(data)
    mode = fsb.header.mode
    print('FSB5 mode=%s samples=%d' % (mode.name, len(fsb.samples)))
    saved = []
    if mode.is_pcm or mode == fsb5.SoundFormat.MPEG or mode == fsb5.SoundFormat.VORBIS:
        for s in fsb.samples:
            if pattern and pattern not in s.name:
                continue
            try:
                wav = fsb.rebuild_sample(s)
                if isinstance(wav, bytes) and wav[:4] == b'RIFF':
                    fn = os.path.join(outdir, s.name + '.wav')
                    open(fn, 'wb').write(wav); saved.append(fn)
            except Exception:
                pass
    if os.path.exists(VGMSTREAM_CLI):
        import subprocess, shutil
        tmp = os.path.join(outdir, '_tmp_%d.fsb' % os.getpid())
        shutil.copy(path, tmp)
        for i, s in enumerate(fsb.samples):
            if pattern and pattern not in s.name:
                continue
            fn = os.path.join(outdir, s.name + '.wav')
            r = subprocess.run([VGMSTREAM_CLI, '-S', str(i + 1), '-o', fn, tmp],
                               capture_output=True)
            if os.path.exists(fn):
                saved.append(fn)
        os.remove(tmp)
    print('已转 %d 个' % len(saved))
    return saved

# ================================================================ DDS
def dds2png(src, dst):
    from PIL import Image
    try:
        im = Image.open(src); im.load(); im.save(dst, 'PNG')
        return True
    except Exception:
        return False

def batch_dds2png(srcdir, dstdir, limit=None):
    os.makedirs(dstdir, exist_ok=True)
    n = ok = 0
    for root, dirs, files in os.walk(srcdir):
        for f in files:
            if not f.lower().endswith('.dds'):
                continue
            n += 1
            if limit and n > limit:
                break
            rel = os.path.relpath(root, srcdir)
            od = os.path.join(dstdir, rel); os.makedirs(od, exist_ok=True)
            if dds2png(os.path.join(root, f), os.path.join(od, f[:-4] + '.png')):
                ok += 1
        if limit and n > limit:
            break
    print('DDS %d 个，成功转 PNG %d' % (n, ok))

# ================================================================ main
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print('\n示例:')
        print('  python lifeafter_unpacker_full.py extract-gpk')
        print('  python lifeafter_unpacker_full.py extract-fpk')
        print('  python lifeafter_unpacker_full.py extract-wpk <idx> <wpk>')
        print('  python lifeafter_unpacker_full.py decrypt-nxs <脚本提取目录> <输出txt>')
        print('  python lifeafter_unpacker_full.py parse-thfb')
        print('  python lifeafter_unpacker_full.py extract-fsb <库> <输出目录> [关键词]')
        print('  python lifeafter_unpacker_full.py dds2png <源目录> <目标目录>')
        return
    cmd = sys.argv[1]
    if cmd == 'extract-gpk':
        extract_all_gpk()
    elif cmd == 'extract-fpk':
        extract_fpk_header(RES_DIR, os.path.join(UNPACK_DIR, 'fpk'), r'E:\lifeafter\res')
    elif cmd == 'extract-fpk-full':
        # 全量拆包单个 fpk：extract-fpk-full <fpk路径> <输出目录>
        if len(sys.argv) >= 4:
            extract_fpk_full(sys.argv[2], sys.argv[3])
        else:
            print('用法: extract-fpk-full <fpk路径> <输出目录>')
    elif cmd == 'search-fpk':
        # 定向搜索单个 fpk：search-fpk <fpk路径> <关键词1> [关键词2] ...
        if len(sys.argv) >= 4:
            fpk = sys.argv[2]
            kws = sys.argv[3:]
            outdir = os.path.join(UNPACK_DIR, 'fpk_search', os.path.basename(fpk)[:-4])
            hits = search_fpk(fpk, kws, outdir=outdir)
            for h in hits[:20]:
                print('  条目%d %s %dB 命中:%s' % (h['idx'], h['ext'], h['size'], ','.join(h['keywords'])))
        else:
            print('用法: search-fpk <fpk路径> <关键词1> [关键词2] ...')
    elif cmd == 'search-all-fpk':
        # 批量搜索体验服独有 fpk：search-all-fpk <关键词1> [关键词2] ...
        if len(sys.argv) >= 3:
            kws = sys.argv[2:]
            out = os.path.join(UNPACK_DIR, 'fpk_search_all')
            search_all_fpk(RES_DIR, kws, out, only_exclusive=True, official_dir=r'E:\lifeafter\res')
        else:
            print('用法: search-all-fpk <关键词1> [关键词2] ...')
    elif cmd == 'extract-wpk':
        entries = parse_wpk_idx(sys.argv[2], sys.argv[3])
    elif cmd == 'extract-npk':
        # 一步到位：npk 解包 + nxs 解密（默认用 Documents 当前源 8-27 新版）
        if len(sys.argv) >= 4:
            npk_extract_and_decrypt(sys.argv[2], sys.argv[3],
                                    sys.argv[4] if len(sys.argv) > 4 else None)
        else:
            npk_extract_and_decrypt(r'E:\mrzh\Documents\script.py314.lc.npk',
                                    r'E:\la拆包项目\03拆包产物\配置数据\_script_raw',
                                    r'E:\la拆包项目\03拆包产物\配置数据\全解密中文.txt')
    elif cmd == 'extract-nxs':
        # 按逻辑路径（双 Murmur3）精确提取：extract-nxs <npk> <逻辑路径> [输出文件]
        extract_nxs_by_path(sys.argv[2], sys.argv[3],
                            sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'inspect-nxs':
        # 提取 + BinDict 解析（x{ + CHS 字段池）：inspect-nxs <npk> <逻辑路径>
        res = inspect_nxs(sys.argv[2], sys.argv[3])
        if res:
            print(json.dumps(res, ensure_ascii=False, indent=1))
    elif cmd == 'verify-source':
        # source lock 校验：verify-source [npk路径]
        verify_source_lock(sys.argv[2] if len(sys.argv) > 2 else r'E:\mrzh\Documents\script.py314.lc.npk')
    elif cmd == 'decode-value':
        # 对 BinDict value span 按 record grammar 解码：decode-value <npk> <逻辑路径> [9632|9618|auto]
        res = decode_bindict_value(sys.argv[2], sys.argv[3],
                                   sys.argv[4] if len(sys.argv) > 4 else 'auto')
        if res:
            print(json.dumps(res, ensure_ascii=False, indent=1))
    elif cmd == 'decrypt-nxs':
        decrypt_nxs_batch(sys.argv[2], sys.argv[3])
    elif cmd == 'parse-thfb':
        extract_all_thfb([r'E:\mrzh\Documents\thd'] + [r'E:\mrzh\Documents\thdext%d' % i for i in range(1, 11)],
                         r'E:\la拆包项目\03拆包产物\配置数据\thfb_hashes.txt')
    elif cmd == 'extract-fsb':
        extract_fsb(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == 'dds2png':
        batch_dds2png(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        print('未知命令', cmd)

if __name__ == '__main__':
    main()
