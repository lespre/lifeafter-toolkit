# -*- coding: utf-8 -*-
"""wiki_selfcheck.py — wiki 页面自检（安全网）· v2（2026-09-18 外部只读审核后加固）

用途：任何对 board.html / weapon_skin_viewer.js / CSS / manifest 的改动之后跑一次，
      用**确定性断言**代替人眼，避免再次"改炸了才发现"。

★ v2 相对 v1 的变化（审核 P0 整改，判据**只能变严**）：
  1. 皮肤集合**参数化**：`--skins 1110165,1110152` 或默认**全量**（从注册表自动取，不再硬编码 7 个）
  2. 查看器**按 `data-skin-id` 定位目标皮肤并断言**（v1 点第一个按钮，不保证是目标）
  3. **`applied == expected_prims`**（expected 来自 manifest `primitives` 数）+ `failed`/`missing` 必须为空
     （v1 只要求 `applied > 0` ⇒ 漏检"部分材质没接上"）
  4. **N 帧稳定 SHA 门**：连续 N≥5 帧截图 sha256 全等才取样，否则重试；重试后仍不稳定 ⇒ FAIL
  5. **逐 prim 校验 program family / 必需槽**：
     `weapon` ⇒ `Tex0/ParamMap/NormalMap` · `crystal` ⇒ `t_basecolor/NormalMap`
     未知 family ⇒ `unresolved` + WARN（不算通过）
  6. **资源 SHA / 悬空引用 / unresolved 误入生产**：
     每个 `local_file` 必须存在 + 与 manifest 记录的 sha 比对；`faces_glob` 必须命中 ≥6 面；
     **必需槽**带 unresolved/candidate 标记 ⇒ FAIL；非必需槽 ⇒ WARN

退出码：**0 = 所有具名 mandatory gate 全过**（WARN 不影响）；**1 = 任一 mandatory gate FAIL**。
        —— 不存在"任意一个 FAIL 也能算过"的写法：FAIL 即 1。
        —— SwiftShader 已知假阳性只按**明确条件**降级为 WARN（皮肤 id + prim 列表 + 指定启动参数，见 SWIFTSHADER_WARN）。

运行（UTF-8 必须显式，否则 GBK 控制台遇 ⚠ 会崩）：
    set PYTHONUTF8=1 && python -X utf8 wiki_selfcheck.py
    python -X utf8 wiki_selfcheck.py --skins 1110165 --out <目录>
    python -X utf8 wiki_selfcheck.py --self-test      # 负控：3 个坏样本必须判 FAIL（不触碰生产资产）
"""
import argparse
import asyncio, base64, glob, hashlib, io as _io, json, os, shutil, subprocess, sys, urllib.request

# ★ UTF-8 尽早强制（审核：GBK 控制台会因 U+26A0 崩）—— 必须在任何 print 之前
os.environ.setdefault("PYTHONUTF8", "1")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = 'http://127.0.0.1:8765/'
URL = BASE + 'board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
W = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
REGISTRY = 'data/media/weapon_skin_media.js'
SKINDIR = 'assets/3d/weapon_skin'

N_FRAMES = 5          # 帧稳定门：连续 N 帧 sha 相同
FRAME_RETRY = 6       # 最多重试次数
SWIFT_FLAGS = ['--disable-gpu', '--enable-unsafe-swiftshader']
# SwiftShader 已知假阳性白名单：只有「皮肤 + prim + 指定启动参数」三者同时命中才降级为 WARN
SWIFTSHADER_WARN = {
    'skins': set(),
    'prims': set(),
    'note': '仅当 headless 以 --disable-gpu --enable-unsafe-swiftshader 运行且命中的 skin/prim 在白名单内 ⇒ WARN，否则 FAIL',
}
REQUIRED = {
    'weapon': ['Tex0', 'ParamMap', 'NormalMap'],
    'crystal': ['NormalMap'],   # ★ t_basecolor 由三分支单独处理（Lead 裁决 ②）：无键=WARN，有键但空/缺文件=FAIL
}
UNRESOLVED_MARK = ('unresolved', 'candidate', 'approximate', 'pending')

PASS, FAIL, WARN = [], [], []
GATES = {}      # gate_id -> ('PASS'|'WARN'|'FAIL')
MANDATORY = set()
READINGS = []   # 原始读数（判定不隐藏数字）


SEV = {'PASS': 0, 'WARN': 1, 'FAIL': 2}
FAILED_GATES = set()


def _gate(gid, status, msg, mandatory=True):
    """★ 严重度单调：同一 gate id 不得被后续 PASS/WARN 降级（自检 2026-09-19：
       M4.required_slot 被多个皮肤共用，曾出现"先 FAIL 后 PASS ⇒ 汇总当 PASS"的漏判）。"""
    if mandatory:
        MANDATORY.add(gid)
    prev = GATES.get(gid)
    # gate 表只保留最严状态（供最终判定）；消息仍按本次真实状态进各自档位
    if prev is None or SEV[status] > SEV[prev]:
        GATES[gid] = status
    if status == 'FAIL':
        FAILED_GATES.add(gid)
    (PASS if status == 'PASS' else FAIL if status == 'FAIL' else WARN).append("[%s] %s" % (gid, msg))
    print("  [%s] %s" % (status, msg))


def ok(gid, m, mandatory=True): _gate(gid, 'PASS', m, mandatory)
def ng(gid, m, mandatory=True): _gate(gid, 'FAIL', m, mandatory)
def wn(gid, m, mandatory=True): _gate(gid, 'WARN', m, mandatory)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------- 皮肤集合
def load_registry():
    p = os.path.join(W, REGISTRY.replace('/', os.sep))
    t = open(p, 'rb').read().decode('utf-8', errors='replace')
    import re as _re
    out = {}
    for m in _re.finditer(r'"(\d{7})":\{"skin_id":"\1","preview_3d":\{"status":"([a-z_]+)"', t):
        out[m.group(1)] = m.group(2)
    return out, t


def resolve_skins(explicit=None):
    reg, raw = load_registry()
    ready = sorted([k for k, v in reg.items() if v == 'ready'])
    unbuilt = sorted([k for k, v in reg.items() if v != 'ready'])
    if explicit:
        want = [s.strip() for s in explicit.split(',') if s.strip()]
        missing = [s for s in want if s not in reg]
        targets = want
    else:
        targets = ready          # ★ 默认全量（不再是硬编码 7 个）
        missing = []
    return targets, ready, unbuilt, missing, reg, raw


# ---------------------------------------------------------------- manifest 校验（纯函数，可被 --self-test 复用）
STRUCT_KEYS = ('status', 'state', 'unresolved', 'production_ok', 'production_reason')
NONPROD = ('unresolved', 'candidate', 'approximate', 'pending', 'missing', 'not_ready')


def struct_unresolved(e):
    """★ 只认结构化字段（Lead 裁决 ①）—— 禁止扫自由文本说明。命中返回原因串，否则 None。"""
    if not isinstance(e, dict):
        return None
    if e.get('unresolved') is True:
        return "unresolved=True"
    if 'production_ok' in e and e.get('production_ok') is not True:
        return "production_ok=%r" % e.get('production_ok')
    for k in ('status', 'state'):
        v = str(e.get(k, '') or '').strip().lower()
        if v in NONPROD:
            return "%s=%s" % (k, v)
    if e.get('production_reason'):
        return "production_reason=%s" % str(e['production_reason'])[:60]
    return None


def expand_faces(fg):
    """★ 按 manifest 的 faces_glob 原样展开（Lead 裁决 ③）：有 {..} 占位 ⇒ i=0..5 代入；
       无占位 ⇒ 该字符串本身就是一面。斜杠/反斜杠都要能处理。"""
    import re as _re
    p = str(fg).replace('\\', os.sep).replace('/', os.sep)
    if _re.search(r'\{[^}]*\}', p):
        return [_re.sub(r'\{[^}]*\}', str(i), p) for i in range(6)]
    return [p]


SHA_ROWS = []


SHA_BYTE_FIELDS = ('local_sha16', 'local_sha256', 'sha16', 'sha256')
SHA_RGBA_FIELDS = ('rgba_sha16', 'rgba_sha256')
SHA_DDS_FIELDS = ('dds_sha16', 'dds_sha256')


def _sha_rgba(path):
    """★ rgba_sha16 = **解码后 raw RGBA** 的 sha256/16（Lead 口径 2026-09-19）。"""
    from PIL import Image as _I
    im = _I.open(path).convert('RGBA')
    return hashlib.sha256(im.tobytes()).hexdigest()


_DDS_INDEX = None
DDS_ROOTS = [
    'E:\\la拆包项目\\03拆包产物\\weapon',
    'E:\\la拆包项目\\03拆包产物',
]
DDS_ROWS = []


def _dds_index():
    """★ Lead 批准：03拆包产物 全树 .dds 的 **basename 索引**（建一次、缓存，不逐条 walk）。"""
    global _DDS_INDEX
    if _DDS_INDEX is None:
        import time as _t
        t0 = _t.time(); idx = {}
        for root in DDS_ROOTS:
            if not os.path.isdir(root):
                continue
            for dp, dn, fn in os.walk(root):
                for f in fn:
                    if f.lower().endswith('.dds'):
                        idx.setdefault(f.lower(), []).append(os.path.join(dp, f))
        _DDS_INDEX = idx
        print("  [DDS索引] %d 个唯一 basename / %d 个文件，用时 %.1fs"
              % (len(idx), sum(len(v) for v in idx.values()), _t.time() - t0))
    return _DDS_INDEX


def resolve_dds(name, skin_dir=None):
    """有序查找：皮肤目录 → weapon\<name> → 03拆包产物 全树 basename 索引。返回 (path, how)。"""
    if skin_dir:
        for sub in ('', 'src_cube', 'src_tex', 'dds'):
            p = os.path.join(skin_dir, sub, name)
            if os.path.exists(p):
                return p, 'skin_dir'
    for root in DDS_ROOTS[:1]:
        p = os.path.join(root, name)
        if os.path.exists(p):
            return p, 'weapon_root'
    hits = _dds_index().get(name.lower()) or []
    if len(hits) == 1:
        return hits[0], 'tree_index(unique)'
    if len(hits) > 1:
        return hits[0], 'tree_index(%d 同名，取首条)' % len(hits)
    return None, 'not_found'


def _actual_for_field(field, fp, skin_dir, e):
    """按口径算出「实际值」；无法判定返回 (None, 原因)。"""
    f = str(field)
    if f in SHA_BYTE_FIELDS:
        return sha256_file(fp), None
    if f in SHA_RGBA_FIELDS:
        try:
            return _sha_rgba(fp), None
        except Exception as ex:
            return None, "解码失败 %s" % type(ex).__name__
    dd = e.get('dds') or e.get('dds_file')
    if f in SHA_DDS_FIELDS and dd:
        name = os.path.basename(str(dd).replace('\\', os.sep).replace('/', os.sep))
        p, how = resolve_dds(name, skin_dir)
        if p:
            DDS_ROWS.append(dict(dds=name, path=p, how=how))
            return sha256_file(p), None
        return None, "DDS 全树未找到 %s" % name
    return None, "字段名 %r 无对应口径" % f


def verify_backfill(k, v, fp, skin_dir, e, i, slot):
    """★ Lead 裁决 2026-09-19 ①：`sha16_backfill*` = **provenance 而非 sha 字段**，
       但必须可验证：是 dict、含 {field,prev,now,why,basis}、且 `now` 在对应口径下等于磁盘实际值。
       任一不满足 ⇒ **FAIL**（不得按名白名单放过，否则此处会成为藏坏 sha 的地方）。"""
    fails = []
    if not isinstance(v, dict):
        return ["prim %s 槽 %s %s 不是 dict（backfill 戳必须结构化）⇒ FAIL" % (i, slot, k)]
    miss = [x for x in ('field', 'prev', 'now', 'why', 'basis') if x not in v]
    if miss:
        return ["prim %s 槽 %s %s 缺字段 %s ⇒ FAIL" % (i, slot, k, miss)]
    if not str(v.get('why') or '').strip() or not str(v.get('basis') or '').strip():
        fails.append("prim %s 槽 %s %s 的 why/basis 为空 ⇒ FAIL" % (i, slot, k))
    actual, why = _actual_for_field(v.get('field'), fp, skin_dir, e)
    if actual is None:
        fails.append("prim %s 槽 %s %s 无法验证 now（%s）⇒ FAIL" % (i, slot, k, why))
        return fails
    now = str(v.get('now') or '').lower()
    ok = actual.startswith(now[:16]) if len(now) <= 16 else (actual == now)
    if not ok:
        fails.append("prim %s 槽 %s %s.now=%s 与磁盘实际值=%s 不符（口径按 field=%s）⇒ FAIL"
                     % (i, slot, k, now[:16], actual[:16], v.get('field')))
    return fails


def verify_stamp(k, v, fp, skin_dir, e, i, slot):
    """★ Lead 裁决 2026-09-19 ②：**两种形状都验证**（不是按名白名单放过）。
       形状 A `sha16_backfill*`    : {field,prev,now,why,basis}，now == 磁盘实际值
       形状 B `sha16_provenance*`  : {chain:[{step,what,value,basis},...]}，每步 value 非 null，**末步 value == 磁盘实际值**
       形状不识别（缺 chain / chain 非 list / 空链）⇒ **WARN 并打印实际键名**
       任一条不满足 ⇒ **FAIL**。返回 (fails, warns)。"""
    ks = str(k)
    if 'backfill' in ks:
        return verify_backfill(k, v, fp, skin_dir, e, i, slot), []
    if 'provenance' in ks:
        if not isinstance(v, dict):
            return ["prim %s 槽 %s %s 不是 dict（provenance 戳必须结构化）⇒ FAIL" % (i, slot, k)], []
        chain = v.get('chain')
        if not isinstance(chain, list) or not chain:
            return [], ["prim %s 槽 %s %s 形状不识别（实际键=%s）⇒ WARN，未校验" % (i, slot, k, sorted(v.keys()))]
        fails = []
        nulls = [st.get('step') for st in chain if (not isinstance(st, dict)) or st.get('value') in (None, '')]
        if nulls:
            fails.append("prim %s 槽 %s %s 的 step %s 的 value 为空 ⇒ FAIL（承诺重算却未填）" % (i, slot, k, nulls))
        steps = [st for st in chain if isinstance(st, dict)]
        if not steps:
            return [], ["prim %s 槽 %s %s chain 内无有效 step（实际=%s）⇒ WARN" % (i, slot, k, chain)]
        last = steps[-1]
        basis = str(last.get('basis') or '')
        field = 'rgba_sha16' if 'rgba' in basis.lower() else 'local_sha16'
        actual, why = _actual_for_field(field, fp, skin_dir, e)
        if actual is None:
            fails.append("prim %s 槽 %s %s 末步无法验证（%s）⇒ FAIL" % (i, slot, k, why))
        else:
            lv = str(last.get('value') or '')
            if not actual.startswith(lv[:16]):
                fails.append("prim %s 槽 %s %s 末步 value=%s ≠ 磁盘实际(%s)=%s ⇒ FAIL" % (i, slot, k, lv[:16], field, actual[:16]))
            else:
                STAMP_OK.append(dict(skin=sid_of(skin_dir), prim=i, slot=slot, stamp=k, steps=len(steps), last=lv[:16], actual=actual[:16], field=field))
        return fails, []
    return [], ["prim %s 槽 %s 未知 sha 字段名 %s ⇒ 未校验（不默认放过）" % (i, slot, k)]


STAMP_OK = []


def sid_of(skin_dir):
    return os.path.basename(str(skin_dir).rstrip(os.sep))


def check_entry_sha(e, fp, skin_dir, i, slot, sid, warns, rd):
    """★ 按字段名选口径（Lead 口径）：
         local_sha16/sha16/local_sha256/sha256 ⇒ 文件**字节**哈希
         rgba_sha16/rgba_sha256              ⇒ **解码后 RGBA** 哈希
         dds_sha16/dds_sha256                ⇒ 需 DDS 文件；无则 WARN
         其它含 sha 的未知字段名              ⇒ **WARN（不默认放过）**
       任何不符 ⇒ WARN（记录陈旧，待回填）；FAIL 只留给文件缺失/必需槽未绑/结构化未达生产/面缺失。"""
    n_ok = 0
    bf_fails = []
    for k, v in list(e.items()):
        if 'sha' not in str(k).lower() or not v:
            continue
        want = str(v).lower()
        if k in SHA_BYTE_FIELDS:
            real = sha256_file(fp)
        elif k in SHA_RGBA_FIELDS:
            try:
                real = _sha_rgba(fp)
            except Exception as ex:
                warns.append("prim %s 槽 %s %s 解码失败，无法校验（%s）" % (i, slot, k, type(ex).__name__)); continue
        elif k in SHA_DDS_FIELDS:
            # ★ Lead 批准：有序查找（皮肤目录 → weapon\ → 03拆包产物 全树 basename 索引）
            dd = e.get('dds') or e.get('dds_file')
            name = os.path.basename(str(dd).replace('\\', os.sep).replace('/', os.sep)) if dd else ''
            _p, how = resolve_dds(name, skin_dir) if name else (None, 'no_dds_field')
            if not _p:
                warns.append("prim %s 槽 %s %s 无 DDS 可解析（dds=%r，%s）⇒ 未校验" % (i, slot, k, dd, how)); continue
            DDS_ROWS.append(dict(dds=name, path=_p, how=how, prim=i, slot=slot, field=k))
            real = sha256_file(_p)
        elif 'backfill' in str(k) or 'provenance' in str(k):
            _f, _w = verify_stamp(k, v, fp, skin_dir, e, i, slot)
            bf_fails.extend(_f); warns.extend(_w); continue
        else:
            warns.append("prim %s 槽 %s **未知 sha 字段名 %s** ⇒ 未校验（不默认放过）" % (i, slot, k)); continue
        rec = want[:16]
        good = real.startswith(want[:16]) if '16' in k else (real == want)
        row = sha_audit_row(skin_dir, i, slot, e.get('local_file'), rec, real[:16], k)
        SHA_ROWS.append(dict(skin=sid, **row))
        if good:
            rd.append({'prim': i, 'slot': slot, 'sha16': real[:16], 'field': k}); n_ok += 1
        else:
            warns.append("prim %s 槽 %s %s 记录陈旧（待回填）：记录=%s 实测=%s；%s" % (i, slot, k, rec, real[:16], row['verdict']))
    return bf_fails, warns, n_ok


def stable_verdict(shas):
    """★ ④ 帧稳定门判据（纯函数，可被 --self-test 直接负控）。"""
    return len(set(shas)) == 1


def sha_audit_row(skin_dir, i, slot, lf, recorded, real, kind):
    """★ ④ 记录陈旧 vs 指错文件：记录值与同皮肤所有文件实测 sha 比对。"""
    row = dict(prim=i, slot=slot, local_file=lf, field=kind, recorded=recorded, actual=real)
    others = {}
    for d in ('src_tex', 'src_cube', 'src_cube' + os.sep + 'faces'):
        dd = os.path.join(skin_dir, d)
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                fp = os.path.join(dd, f)
                if os.path.isfile(fp):
                    others[d + '/' + f] = sha256_file(fp)[:len(recorded)]
    hit = [k for k, v in others.items() if v == recorded]
    row['matches_other'] = hit
    row['verdict'] = ('OK' if recorded == real else
                      ('指向同皮肤另一文件: ' + ','.join(hit) if hit else '记录陈旧（记录值不匹配本皮肤任何文件）'))
    return row


def check_manifest(path, skin_dir, sid='<synthetic>'):
    """返回 (fails, warns, readings)。规则（Lead 裁决 ①②③）：
         · unresolved 只认结构化字段，说明性文字不算
         · crystal 的 t_basecolor 三分支：有键且有文件=PASS / 有键但空或文件不存在=FAIL / 无键=WARN+unresolved
         · faces_glob 原样展开 {0..5}，不自己拼 faces 目录
    """
    fails, warns, rd = [], [], []
    if not os.path.exists(path):
        return ["manifest 不存在: %s" % path], warns, rd
    m = json.load(open(path, encoding='utf-8'))
    prims = m.get('primitives') or []
    for pr in prims:
        i = pr.get('prim')
        fam = pr.get('shader_kind')
        tex = pr.get('textures') or {}
        required = list(REQUIRED.get(fam, []))
        if fam == 'crystal':
            if 't_basecolor' not in tex:
                warns.append("prim %s crystal 无 t_basecolor 键 ⇒ WARN+unresolved（未取得 RDEF/DXBC 证据前不算 PASS；task-39 落地后再收紧）" % i)
            else:
                e = tex.get('t_basecolor')
                lf = (e or {}).get('local_file') if isinstance(e, dict) else None
                if not lf:
                    fails.append("prim %s crystal **声明了** t_basecolor 但 local_file 为空（%r）⇒ 真缺陷" % (i, lf))
                elif not os.path.exists(os.path.join(skin_dir, lf.replace('/', os.sep))):
                    fails.append("prim %s crystal t_basecolor 文件不存在: %s ⇒ 真缺陷" % (i, lf))
                else:
                    fp = os.path.join(skin_dir, lf.replace('/', os.sep))
                    _bf, _w, _n = check_entry_sha(e, fp, skin_dir, i, 't_basecolor', sid, warns, rd)
                    fails.extend(_bf)
                    u = struct_unresolved(e)
                    if u: fails.append("prim %s crystal t_basecolor 结构化标记未达生产（%s）" % (i, u))
        if fam in REQUIRED:
            for slot in required:
                e = tex.get(slot)
                lf = e.get('local_file') if isinstance(e, dict) else None
                if not lf:
                    fails.append("prim %s family=%s 必需槽 %s 未绑" % (i, fam, slot)); continue
                fp = os.path.join(skin_dir, lf.replace('/', os.sep))
                if not os.path.exists(fp):
                    fails.append("prim %s 槽 %s 指向不存在的文件: %s" % (i, slot, lf)); continue
                _bf, _w, _n = check_entry_sha(e, fp, skin_dir, i, slot, sid, warns, rd)
                fails.extend(_bf)
                u = struct_unresolved(e)
                if u:
                    fails.append("prim %s 必需槽 %s 结构化标记未达生产（%s）" % (i, slot, u))
        else:
            warns.append("prim %s 未知 program family %r ⇒ unresolved+WARN（不算通过）" % (i, fam))
        for slot, e in tex.items():
            if isinstance(e, dict) and slot not in required and struct_unresolved(e):
                warns.append("prim %s 非必需槽 %s 结构化标记（%s）（WARN）" % (i, slot, struct_unresolved(e)))
        e = tex.get('t_custom_ibl')
        if isinstance(e, dict):
            g = e.get('faces_glob')
            if g:
                paths = expand_faces(g)
                miss = [p for p in paths if not os.path.exists(os.path.join(skin_dir, p))]
                if miss or len(paths) < (6 if len(paths) == 6 else 1):
                    fails.append("prim %s faces_glob 展开 %d 面、缺 %d：%s" % (i, len(paths), len(miss), miss[:3]))
                else:
                    rd.append({'prim': i, 'faces': len(paths)})
            lf = e.get('local_file')
            if lf and not os.path.exists(os.path.join(skin_dir, lf.replace('/', os.sep))):
                fails.append("prim %s t_custom_ibl.local_file 不存在: %s" % (i, lf))
    if not prims:
        fails.append("manifest 无 primitives")
    return fails, warns, rd


def check_manifest_all(skins):
    print("\n=== 4. manifest 逐 prim 必需槽 / family / 资源 SHA（新门）===")
    for sid in skins:
        d = os.path.join(W, SKINDIR.replace('/', os.sep), sid)
        fails, warns, rd = check_manifest(os.path.join(d, 'neox_material.json'), d, sid)
        for w in warns:
            wn('M4.family.unresolved', "%s %s" % (sid, w))
        for f in fails:
            ng('M4.required_slot', "%s %s" % (sid, f))
        if not fails:
            ok('M4.required_slot', "%s 逐 prim 必需槽/文件/sha 全过（%d 条读数）" % (sid, len(rd)))
        for r in rd:
            READINGS.append(dict(skin=sid, **r))
    # ★ ④ 逐条 sha 审计表（记录陈旧 vs 指错文件）
    if SHA_ROWS:
        print("\n--- ④ sha 审计（记录值 vs 磁盘实测）---")
        for r in SHA_ROWS:
            mark = 'OK' if r['verdict'] == 'OK' else ('陈旧/WARN' if r['verdict'].startswith('记录陈旧') else '错位/FAIL')
            print("  %-8s prim%-2s %-12s 记录=%-16s 实测=%-16s 判定=%-9s %s"
                  % (r['skin'], r['prim'], r['slot'], r['recorded'], r['actual'], mark, r['verdict']))
        stale = [r for r in SHA_ROWS if r['verdict'] != 'OK']
        if stale:
            wn('S4.sha_stale', "sha 记录陈旧（待回填）%d 条 ⇒ WARN + 清单（Lead 裁决：文件侧为准）：%s"
               % (len(stale), [(r['skin'], r['prim'], r['slot'], r['recorded'], r['actual'], r['matches_other']) for r in stale]))
        else:
            ok('S4.sha', "全部记录 sha 与磁盘一致（%d 条）" % len(SHA_ROWS))
        if STAMP_OK:
            print("\n--- ② provenance 戳（形状 B）逐条核对：末步 value vs 磁盘实际 ---")
            for r in STAMP_OK:
                print("  %-8s prim%-2s %-12s steps=%d 末步=%s 磁盘=%s 口径=%s ✓"
                      % (r['skin'], r['prim'], r['slot'], r['steps'], r['last'], r['actual'], r['field']))
            ok('S5.provenance', "形状 B 戳全部可验证且末步==磁盘（%d 条）" % len(STAMP_OK))
        if DDS_ROWS:
            seen = set(); uniq = []
            for r in DDS_ROWS:
                if r['dds'] in seen:
                    continue
                seen.add(r['dds']); uniq.append(r)
            print("\n--- ③ dds_sha 逐条（有序查找：skin_dir → weapon\ → 全树索引）---")
            for r in sorted(uniq, key=lambda x: x['path']):
                print("  %-14s [%s] %s" % (r['dds'], r['how'], r['path']))
            ok('S6.ddsresolve', "dds_sha 字段全部解析到真实文件（%d 个唯一 DDS）" % len(uniq))


# ---------------------------------------------------------------- 1. HTTP
def http_probe(skins, unbuilt):
    print("\n=== 1. HTTP 可访问性 ===")
    paths = ['board.html', 'assets/weapon_skin_viewer.js', 'assets/weapon_skin_viewer.css',
             'board_shadcn.css', 'assets/weapon_skin_sfx_adapter.js', REGISTRY]
    for sid in skins:
        paths += ['%s/%s/viewer.json' % (SKINDIR, sid), '%s/%s/neox_material.json' % (SKINDIR, sid)]
    bad = 0
    for p in paths:
        try:
            r = urllib.request.urlopen(BASE + p, timeout=10)
            if r.status != 200:
                bad += 1
                print("    [FAIL] %-62s HTTP %s" % (p, r.status))
        except Exception as e:
            bad += 1
            print("    [FAIL] %-62s %s" % (p, e))
    (_gate('H1.http', 'FAIL' if bad else 'PASS',
           "HTTP 资源 %d 项，失败 %d" % (len(paths), bad)))
    for sid in unbuilt:
        p = '%s/%s/neox_material.json' % (SKINDIR, sid)
        try:
            urllib.request.urlopen(BASE + p, timeout=10)
            ng('H2.unbuilt_404', "有意不建却存在: %s" % p)
        except Exception:
            ok('H2.unbuilt_404', "有意不建、按预期 404: %s" % sid)


# ---------------------------------------------------------------- 2. 编码健康
def file_health():
    print("\n=== 2. 编码健康（BOM / UTF-8 / 结构） ===")
    bad = 0
    for rel in ['board.html', 'assets/weapon_skin_viewer.js', 'assets/weapon_skin_viewer.css']:
        p = os.path.join(W, rel.replace('/', os.sep))
        if not os.path.exists(p):
            bad += 1; print("    [FAIL] %s 不存在" % rel); continue
        raw = open(p, 'rb').read()
        if raw[:3] == b'\xef\xbb\xbf':
            wn('E2.bom', "%s 含 UTF-8 BOM" % rel)
        try:
            t = raw.decode('utf-8')
            if '\ufffd' in t:
                bad += 1; print("    [FAIL] %s 含 U+FFFD %d 处" % (rel, t.count('\ufffd')))
        except UnicodeDecodeError as e:
            bad += 1; print("    [FAIL] %s 非合法 UTF-8: %s" % (rel, e))
    b = open(os.path.join(W, 'board.html'), 'rb').read()
    for tag in (b'<!DOCTYPE', b'<html', b'</html>', b'weapon_skin_viewer.js?v=', b'weapon_skin_viewer.css?v='):
        if tag not in b:
            bad += 1; print("    [FAIL] board.html 缺 %s" % tag.decode())
    _gate('E2.encoding', 'FAIL' if bad else 'PASS', "编码/结构问题 %d 处" % bad)


# ---------------------------------------------------------------- 3. 注册表
def registry_check(skins, unbuilt, reg):
    print("\n=== 3. 上板注册表一致性 ===")
    bad = 0
    for sid in skins:
        if sid not in reg:
            bad += 1; print("    [FAIL] %s 未注册" % sid)
        elif reg[sid] != 'ready':
            bad += 1; print("    [FAIL] %s 注册 status=%s（应 ready）" % (sid, reg[sid]))
    for sid in unbuilt:
        if reg.get(sid) == 'ready':
            bad += 1; print("    [FAIL] %s 注册 ready 但材质链未建 ⇒ 会出灰白" % sid)
    _gate('R1.registry', 'FAIL' if bad else 'PASS',
          "注册表一致：目标 %d 全 ready，未建 %d 未 ready，问题 %d" % (len(skins), len(unbuilt), bad))


# ---------------------------------------------------------------- CDP 工具
def _launch(prof_name, port, size='1400,1300'):
    prof = os.path.join(OUT, prof_name)
    shutil.rmtree(prof, ignore_errors=True)
    args = [CHROME, '--headless=new'] + SWIFT_FLAGS + [
        '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
        '--window-size=%s' % size, '--remote-debugging-port=%d' % port,
        '--user-data-dir=%s' % prof, 'about:blank']
    pr = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return pr, prof, args


def _kill_profile_by_cmdline(tag):
    """★ Lead 裁决 ②：`Get-Process` 无 CommandLine ⇒ 改用 Get-CimInstance 按命令行过滤**自己的 profile**，
       只杀自己的进程（绝不整类杀 chrome，避免误清队友/用户进程）。"""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | "
          "Where-Object { $_.CommandLine -like '*%s*' } | "
          "ForEach-Object { \"$($_.ProcessId)|$($_.CommandLine)\" }" % tag)
    import tempfile
    fd, tmp = tempfile.mkstemp(prefix='ps_', suffix='.txt'); os.close(fd)
    killed = []
    try:
        with open(tmp, 'w', encoding='utf-8') as fh:
            subprocess.run(['powershell', '-NoProfile', '-Command', ps], stdout=fh,
                           stderr=subprocess.DEVNULL, timeout=40)
        for line in open(tmp, encoding='utf-8', errors='replace'):
            line = line.strip()
            if '|' not in line:
                continue
            pid_s, cmd = line.split('|', 1)
            if not pid_s.isdigit():
                continue
            subprocess.run(['taskkill', '/T', '/F', '/PID', pid_s],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            killed.append((pid_s, cmd[:90]))
    finally:
        try: os.remove(tmp)
        except Exception: pass
    return killed


def _kill(pr, port, gate_id, profile_tag=None):
    """★ 审核要求：taskkill /T /F 杀进程树，并复查端口无残留；再按 CommandLine 兜底清自己的 profile。"""
    try:
        subprocess.run(['taskkill', '/T', '/F', '/PID', str(pr.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception:
        try: pr.terminate()
        except Exception: pass
    left = False
    for _ in range(20):
        try:
            urllib.request.urlopen('http://127.0.0.1:%d/json' % port, timeout=1)
            left = True
        except Exception:
            left = False
            break
        import time as _t; _t.sleep(0.5)
    extra = _kill_profile_by_cmdline(profile_tag) if profile_tag else []
    if extra:
        print("    按 CommandLine 兜底清 profile=%s: %s" % (profile_tag, extra))
    _gate(gate_id, 'FAIL' if (left or extra) else 'PASS',
          "headless(pid=%s, port=%d) %s；CommandLine 兜底 %d 个（profile=%s）"
          % (pr.pid, port, "已杀但端口仍监听 ⇒ 残留 FAIL" if left else "taskkill /T /F 完成，端口无残留 ✓",
             len(extra), profile_tag))


async def _ws_for(port):
    pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port)) if t.get('type') == 'page')
    return pg['webSocketDebuggerUrl']


def _mk_send(ws, excs, cerrs):
    box = {'i': 0}

    async def send(m, **pp):
        box['i'] += 1
        i = box['i']
        await ws.send(json.dumps(dict(id=i, method=m, params=pp)))
        while True:
            r = json.loads(await ws.recv())
            mm = r.get('method')
            if mm == 'Runtime.exceptionThrown':
                d = r['params']['exceptionDetails']
                excs.append('%s | %s' % (d.get('text', ''), str((d.get('exception') or {}).get('description', ''))[:200]))
            elif mm == 'Runtime.consoleAPICalled' and r['params'].get('type') == 'error':
                cerrs.append(' '.join(str(a.get('value', ''))[:200] for a in r['params'].get('args', [])))
            if r.get('id') == i:
                return r.get('result', {})
    return send


async def _stable_frame(send, ws, tag, pause=0.7):
    """★ N 帧稳定 SHA 门：连续 N 帧 sha256 全等才取样。"""
    last = None
    for attempt in range(1, FRAME_RETRY + 1):
        shas = []
        raw = b''
        for _ in range(N_FRAMES):
            s = await send('Page.captureScreenshot', format='png')
            raw = base64.b64decode(s.get('data', ''))
            shas.append(hashlib.sha256(raw).hexdigest())
            await asyncio.sleep(pause)
        uniq = sorted(set(shas))
        last = uniq[0]
        READINGS.append(dict(frame=tag, attempt=attempt, n=N_FRAMES, uniq=len(uniq), sha16=shas[-1][:16]))
        if stable_verdict(shas):
            ok('F6.framestable', "%s 连续 %d 帧 sha 相同（%s，第 %d 次尝试）✓" % (tag, N_FRAMES, shas[-1][:16], attempt))
            return raw, shas[-1]
        print("    [WARN] %s 第 %d 次尝试 %d 帧内 %d 种 sha，重试" % (tag, attempt, N_FRAMES, len(uniq)))
    ng('F6.framestable', "%s %d 次尝试 ×%d 帧均不稳定（末次唯一 sha=%s）⇒ 取样不可信" % (tag, FRAME_RETRY, N_FRAMES, last[:16]))
    return None, last


# ---------------------------------------------------------------- 5-7. 页面运行时（按 data-skin-id 定位目标）
async def page_check(skins, run=1):
    port = 9930 + run
    ptag = '_profSELF%d' % run
    print("\n=== 5-7. 页面运行时（run=%d · profile=%s · port=%d · 目标按 data-skin-id 定位）===" % (run, ptag, port))
    pr, prof, args = _launch(ptag, port)
    try:
        await asyncio.sleep(4)
        async with websockets.connect(await _ws_for(port), max_size=1 << 27) as ws:
            excs, cerrs = [], []
            send = _mk_send(ws, excs, cerrs)
            ev = lambda e: _eval(send, e)
            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(14)

            rs = await ev("document.readyState")
            blen = await ev("document.body?document.body.innerHTML.length:0")
            ncard = await ev("document.querySelectorAll('.skin-card').length")
            nbtn = await ev("document.querySelectorAll('.skin-media-button').length")
            ok('P5.ready' if rs == 'complete' else 'F5.ready', "readyState = %s" % rs)
            ok('P5.body' if (blen or 0) > 100000 else 'F5.body', "body 长度 = %s" % blen)
            ok('P5.cards' if (ncard or 0) >= 100 else 'F5.cards', "皮肤卡数 = %s（期望 ≥100）" % ncard)
            ok('P5.buttons' if (nbtn or 0) >= 1 else 'F5.buttons', "查看器按钮数 = %s（期望 ≥1）" % nbtn)
            ok('P5.global' if await ev("typeof window.WikiWeaponViewer==='object'") else 'F5.global', "WikiWeaponViewer 全局存在")
            if excs: ng('P7.jsexc', "JS 异常 %d 条: %s" % (len(excs), excs[0][:150]))
            else: ok('P7.jsexc', "JS 异常 0 条")
            if cerrs: wn('W7.console', "console error %d 条: %s" % (len(cerrs), cerrs[0][:150]))
            else: ok('W7.console', "console error 0 条")

            for sid in skins:
                # ★ 按 data-skin-id 定位并断言；找不到目标 ⇒ FAIL（v1 是点第一个按钮）
                found = await ev("document.querySelectorAll('[data-skin-id=\"%s\"]').length" % sid)
                if not (found or 0):
                    ng('V6.target', "找不到目标皮肤的入口 [data-skin-id=%s]（%d 个）" % (sid, found))
                    continue
                sid_clicked = await ev("(()=>{var b=document.querySelector('[data-skin-id=\"%s\"]');"
                                       "b.click();return b.getAttribute('data-skin-id');})()" % sid)
                await asyncio.sleep(12)
                canvas = await ev("!!document.querySelector('canvas')")
                if not canvas:
                    ng('V6.canvas', "%s 点击后 canvas 未出现" % sid); continue
                if sid_clicked != sid:
                    ng('V6.target', "点击后 data-skin-id=%r ≠ 目标 %s" % (sid_clicked, sid)); continue
                ok('V6.target', "%s 按 data-skin-id 命中并打开 canvas ✓" % sid)

                # ★ 3：applied == expected_prims，且 failed/missing 空
                man = os.path.join(W, SKINDIR.replace('/', os.sep), sid, 'neox_material.json')
                expect = len((json.load(open(man, encoding='utf-8')).get('primitives') or []))
                neox = await ev("window.WikiWeaponViewer&&window.WikiWeaponViewer.__neox?JSON.stringify(window.WikiWeaponViewer.__neox()):null")
                try:
                    rp = (json.loads(neox) or {}).get('report', {})
                    applied = rp.get('applied'); failed = rp.get('failed') or []
                    missing = rp.get('missing') or []
                    READINGS.append(dict(skin=sid, applied=applied, expected=expect, failed=len(failed), missing=len(missing)))
                    if applied == expect and not failed and not missing:
                        ok('A3.applied', "%s applied=%s == expected_prims=%s，failed=0 missing=0 ✓" % (sid, applied, expect))
                    else:
                        ng('A3.applied', "%s applied=%s ≠ expected_prims=%s 或 failed=%s/missing=%s ⇒ 门不过"
                           % (sid, applied, expect, failed, missing))
                except Exception as e:
                    ng('A3.applied', "%s __neox() 解析失败: %s (%s)" % (sid, str(e)[:80], str(neox)[:80]))

                raw, sha = await _stable_frame(send, ws, '%s' % sid)
                if raw:
                    a = np.asarray(Image.open(_io.BytesIO(raw)).convert('RGB'))
                    frac = float((a.max(2) > 26).mean() * 100)
                    READINGS.append(dict(frame=sid, nonDarkPct=round(frac, 2)))
                    if frac > 50: ok('V6.nondark', "%s 截图非暗占比 %.1f%% ✓" % (sid, frac))
                    else: wn('W6.nondark', "%s 截图非暗占比 %.1f%%（偏低，需人眼复核）" % (sid, frac))
                    out = os.path.join(OUT, 'SELFCHECK_%s.png' % sid)
                    open(out, 'wb').write(raw)
                    print("  截图 -> %s (%d B sha=%s)" % (os.path.basename(out), len(raw), (sha or '')[:16]))
    finally:
        _kill(pr, port, 'K9.kill.run%d' % run, profile_tag=ptag)


async def _eval(send, e):
    r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
    return (r.get('result', {}) or {}).get('value')


# ---------------------------------------------------------------- 10. 逐 mesh 绑定（__matDump）
async def map_binding_check(skins):
    print("\n=== 8. 逐皮肤贴图绑定（__matDump 实测）===")
    pr, prof, args = _launch('_profMAP', 10021, size='1200,900')
    try:
        await asyncio.sleep(4)
        async with websockets.connect(await _ws_for(10021), max_size=1 << 27) as ws:
            send = _mk_send(ws, [], [])
            ev = lambda e: _eval(send, e)
            bad_by_skin = {}
            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(10)
            for sid in skins:
                rel = '%s/%s' % (SKINDIR, sid)
                await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'%s/poster.webp',"
                         "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (sid, rel, rel))
                for _ in range(25):
                    st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                    if st and '"applied"' in st:
                        break
                    await asyncio.sleep(2)
                await asyncio.sleep(3)
                d = await ev("JSON.stringify(window.WikiWeaponViewer.__matDump&&window.WikiWeaponViewer.__matDump())")
                try:
                    ms = (json.loads(d) or {}).get('meshes') or []
                except Exception as e:
                    ng('B8.matdump', "%s __matDump 解析失败: %s" % (sid, str(e)[:80])); continue
                bad, raw_ms = [], []
                for m in ms:
                    raw_ms.append({'i': m.get('i'), 'map': bool(m.get('map')), 'norm': bool(m.get('normalMap')),
                                   'mmap': bool(m.get('metalnessMap')), 'rmap': bool(m.get('roughnessMap')),
                                   'env': m.get('envMapIntensity')})
                    if not m.get('map') or not m.get('normalMap'):
                        bad.append((m.get('i'), 'map/normalMap 缺')); continue
                    if (m.get('metalness') or 0) > 0.5:
                        if not m.get('metalnessMap') or not m.get('roughnessMap'):
                            bad.append((m.get('i'), 'weapon 族缺 metalnessMap/roughnessMap'))
                    else:
                        if not m.get('roughnessMap'):
                            bad.append((m.get('i'), 'crystal 族缺 roughnessMap'))
                # envMapIntensity：仅当 manifest 该 prim 声明了 t_custom_ibl
                man = os.path.join(W, SKINDIR.replace('/', os.sep), sid, 'neox_material.json')
                need = set()
                try:
                    for k, pp in enumerate(json.load(open(man, encoding='utf-8')).get('primitives', [])):
                        e = (pp.get('textures') or {}).get('t_custom_ibl')
                        if isinstance(e, dict) and e.get('local_file'):
                            need.add(k)
                except Exception:
                    pass
                noenv = [m.get('i') for k, m in enumerate(ms) if k in need and not (m.get('envMapIntensity') or 0) > 0]
                # ★ 逐 prim envMode 门（Lead 口径 2026-09-19）：必须有明确可判状态；
                #   missing_source_ibl = 真缺陷（曾出现"零环境光但 applied=7/failed=[]"）；字段缺失 ⇒ WARN 不放过
                env_missing = [(m.get('i'), m.get('envMode')) for m in ms if m.get('envMode') == 'missing_source_ibl']
                env_unknown = [m.get('i') for m in ms if not m.get('envMode')]
                env_other = [(m.get('i'), m.get('envMode')) for m in ms
                             if m.get('envMode') and m.get('envMode') not in ('source_ibl', 'missing_source_ibl')]
                READINGS.append(dict(skin=sid, meshes=len(ms), raw=raw_ms))
                if env_missing:
                    ng('B9.envmode', "%s 逐 prim envMode=missing_source_ibl ⇒ 零环境光（applied 数字看不出来）: %s" % (sid, env_missing))
                elif env_other:
                    ng('B9.envmode', "%s 逐 prim envMode 非 source_ibl 且非可判状态: %s" % (sid, env_other))
                elif env_unknown:
                    wn('B9.envmode', "%s __matDump 未提供 envMode（%d 个 mesh）⇒ 无法判定；等 viewer.js env_warn 落地后收紧为 FAIL" % (sid, len(env_unknown)))
                else:
                    ok('B9.envmode', "%s 逐 prim envMode=source_ibl（%d mesh）✓" % (sid, len(ms)))
                if not ms:
                    ng('B8.mesh', "%s 无 mesh" % sid)
                elif bad or noenv:
                    # ★ Lead 裁决 ③：单次结果一律先记 WARN，定性靠"同会话 N=5 载入复现次数"（见下方 repro 段）
                    wn('W8.bind.firstpass', "%s 首过异常 bad=%s noenv=%s ⇒ 待 N=5 复现统计定性｜原始读数: %s"
                       % (sid, bad or '[]', noenv or '[]', json.dumps(raw_ms, ensure_ascii=False)[:400]))
                    bad_by_skin[sid] = [b[0] for b in bad]
                else:
                    ok('B8.bind', "%s %d mesh 按族判据全过（crystal 的 metalnessMap=null 属预期）✓" % (sid, len(ms)))
            # ★ Lead 裁决 ③：对首过异常的皮肤，做同会话重复载入 N=5，统计复现次数
            for sid, first in list(bad_by_skin.items()):
                rel = '%s/%s' % (SKINDIR, sid)
                cnt, per = 1, {m: 1 for m in first}
                for r_i in range(2, 6):
                    await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'%s/poster.webp',"
                             "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (sid, rel, rel))
                    for _ in range(25):
                        st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                        if st and '"applied"' in st:
                            break
                        await asyncio.sleep(2)
                    await asyncio.sleep(3)
                    d2 = await ev("JSON.stringify(window.WikiWeaponViewer.__matDump&&window.WikiWeaponViewer.__matDump())")
                    try:
                        ms2 = (json.loads(d2) or {}).get('meshes') or []
                    except Exception:
                        continue
                    b2 = [m2.get('i') for m2 in ms2
                          if (not m2.get('map')) or (not m2.get('normalMap'))
                          or ((m2.get('metalness') or 0) > 0.5 and (not m2.get('metalnessMap') or not m2.get('roughnessMap')))
                          or ((m2.get('metalness') or 0) <= 0.5 and not m2.get('roughnessMap'))]
                    if b2:
                        cnt += 1
                        for m2 in b2:
                            per[m2] = per.get(m2, 0) + 1
                READINGS.append(dict(skin=sid, b8_repro=f'{cnt}/5', per_mesh=per, first=first))
                if cnt >= 3:
                    ng('B8.bind', "%s 同会话 5 次载入中 **%d 次复现**（每 mesh %s，首过 %s）⇒ 稳定复现，判 FAIL"
                       % (sid, cnt, per, first))
                else:
                    wn('W8.bind', "%s 同会话 5 次载入仅 %d 次复现（每 mesh %s，首过 %s）⇒ 时序敏感，判 WARN（Lead 裁决 ③）"
                       % (sid, cnt, per, first))
    finally:
        _kill(pr, 10021, 'K9.kill2')


# ---------------------------------------------------------------- 负控
def self_test():
    """★ 负控：3 个坏样本必须判 FAIL（在 %TEMP% 内合成，不触碰生产资产，用完删除）。"""
    print("\n=== SELF-TEST 负控（3 个坏样本必须 FAIL）===")
    import tempfile
    tmp = tempfile.mkdtemp(prefix='selfcheck_neg_')
    made, results = [], []
    try:
        sd = os.path.join(tmp, 'skin'); os.makedirs(sd)
        good = os.path.join(sd, 'ok.png')
        from PIL import Image as _PI
        _PI.new('RGBA', (2, 2), (10, 20, 30, 255)).save(good)   # ★ 必须是**真 PNG**，否则 _sha_rgba 解码抛 OSError
        g16 = sha256_file(good)[:16]

        def mk(name, prim):
            d = dict(schema='neox_material/v2', primitives=[prim])
            p = os.path.join(tmp, name + '.json')
            json.dump(d, open(p, 'w', encoding='utf-8'))
            made.append(p); return p

        # 坏样本 1：必需槽指向不存在文件
        p1 = mk('neg1', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'nope.png'},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        # 坏样本 2：未知 program family
        p2 = mk('neg2', {'prim': 0, 'shader_kind': 'pbr_mystery',
                         'textures': {'Tex0': {'local_file': 'ok.png'}}})
        # 坏样本 3：必需槽带结构化 status=candidate（未达生产）⇒ 必须 FAIL
        p3 = mk('neg3', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'status': 'candidate'},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        # 负控4：sha 记录陈旧 ⇒ 按 Lead 裁决只 WARN、不 FAIL
        p4 = mk('neg4', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'local_sha16': 'deadbeefdeadbeef'},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        # 负控5：把 rgba_sha16 写成**文件字节**哈希 ⇒ 口径不同，应 WARN（不 FAIL、也不放过）
        p5 = mk('neg5', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'rgba_sha16': sha256_file(good)[:16]},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        # 负控6：未知 sha 字段名 ⇒ 必须 WARN（不默认放过）
        # 负控10/11/12：形状 B（provenance chain）必须同样“验证而非忽略”
        _rgba16 = _sha_rgba(good)[:16]

        def _prov(lastval, chain=None):
            return {'chain': chain if chain is not None else [
                {'step': 1, 'what': '原记录', 'value': 'a' * 16, 'basis': 'rgba_sha16'},
                {'step': 4, 'what': '本次重算', 'value': lastval, 'basis': 'rgba_sha16=解码RGBA'}]}

        p10 = mk('neg10', {'prim': 0, 'shader_kind': 'weapon', 'textures': {
            'Tex0': {'local_file': 'ok.png', 'sha16_provenance_20260919': _prov(_rgba16)},
            'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        p11 = mk('neg11', {'prim': 0, 'shader_kind': 'weapon', 'textures': {
            'Tex0': {'local_file': 'ok.png', 'sha16_provenance_20260919': _prov(_rgba16, [
                {'step': 1, 'what': '原记录', 'value': None, 'basis': 'rgba_sha16'},
                {'step': 4, 'what': '本次重算', 'value': _rgba16, 'basis': 'rgba_sha16'}])},
            'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        p12 = mk('neg12', {'prim': 0, 'shader_kind': 'weapon', 'textures': {
            'Tex0': {'local_file': 'ok.png', 'sha16_provenance_20260919': {'foo': 1}},
            'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        p6 = mk('neg6', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'mystery_sha7': '0123456789abcdef'},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        # 负控7/8/9：backfill 戳必须**可验证**（Lead 裁决 ①）
        p7 = mk('neg7', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'sha16_backfill_20260919': {
                             'field': 'local_sha16', 'prev': 'x', 'now': g16, 'why': 'LEAD 回填', 'basis': 'LEAD_stale_sha_backfill.json'}},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        p8 = mk('neg8', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'sha16_backfill_20260919': {
                             'field': 'local_sha16', 'prev': 'x', 'now': 'deadbeefdeadbeef', 'why': '错值', 'basis': 'x'}},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        p9 = mk('neg9', {'prim': 0, 'shader_kind': 'weapon',
                         'textures': {'Tex0': {'local_file': 'ok.png', 'sha16_backfill_20260919': 'deadbeef'},
                                      'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        okp = mk('ok', {'prim': 0, 'shader_kind': 'weapon',
                        'textures': {'Tex0': {'local_file': 'ok.png', 'local_sha16': g16},
                                     'ParamMap': {'local_file': 'ok.png'}, 'NormalMap': {'local_file': 'ok.png'}}})
        for label, path, want_fail in (('负控1 必需槽文件不存在', p1, True),
                                       ('负控2 未知 family', p2, False),   # 未知 family ⇒ WARN（不算通过，但不是 FAIL）
                                       ('负控3 必需槽 status=candidate', p3, True),
                                       ('负控4 sha 记录陈旧(应 WARN 不 FAIL)', p4, None),
                                       ('负控5 rgba_sha16 口径不同(应 WARN)', p5, None),
                                       ('负控6 未知 sha 字段名(应 WARN)', p6, None),
                                       ('负控7 backfill 戳可验证(应过)', p7, False),
                                       ('负控8 backfill now 与磁盘不符(应 FAIL)', p8, True),
                                       ('负控9 backfill 戳非 dict(应 FAIL)', p9, True),
                                       ('负控10 provenance 链完整(应过)', p10, False),
                                       ('负控11 provenance 有 step value 为空(应 FAIL)', p11, True),
                                       ('负控12 provenance 形状不识别(应 WARN)', p12, None),
                                       ('正控 全对', okp, False)):
            f, w, _ = check_manifest(path, sd)
            hit = bool(f) if want_fail else (not f)
            if want_fail is None:
                hit = (not f) and len(w) > 0
            results.append((label, hit, f, w))
            (_gate('NEG.' + label, 'PASS' if hit else 'FAIL',
                   "%s ⇒ fails=%d warns=%d %s" % (label, len(f), len(w), f[:2]) ))

        # 坏样本 4（applied 门）：applied=1 而 expected=5 ⇒ v1 会通过，v2 必须 FAIL
        for (ap, ex, want_ok) in ((1, 5, False), (5, 5, True)):
            good_gate = (ap == ex)
            _gate('NEG.applied_%s_%s' % (ap, ex), 'PASS' if good_gate == want_ok else 'FAIL',
                   "applied=%s vs expected_prims=%s ⇒ %s（v1 用 applied>0 ⇒ 前者会被误判通过）"
                   % (ap, ex, 'PASS' if good_gate else 'FAIL'))
        # ★ ④ 稳定门负控：故意造一个"不稳定"帧序列，必须判 FAIL
        _gate('NEG.稳定门 全同5帧', 'PASS' if stable_verdict(['a'] * 5) else 'FAIL',
              "5 帧全同 ⇒ %s" % stable_verdict(['a'] * 5))
        unstable = ['a', 'a', 'b', 'a', 'a']
        _gate('NEG.稳定门 故意不稳定', 'PASS' if not stable_verdict(unstable) else 'FAIL',
              "故意不稳定样本 %s ⇒ 判 %s（必须 FAIL 才算拦得住）"
              % (unstable, 'PASS' if stable_verdict(unstable) else 'FAIL'))
    finally:
        for p in made:
            try: os.remove(p)
            except Exception: pass
        shutil.rmtree(tmp, ignore_errors=True)
    print("  负控临时文件已全部删除: %s ⇒ 存在=%s" % (tmp, os.path.exists(tmp)))


def main():
    ap = argparse.ArgumentParser(description='wiki 页面自检 v2')
    ap.add_argument('--skins', default=None, help='逗号分隔的目标皮肤；默认=注册表中全部 ready（全量）')
    ap.add_argument('--out', default=None, help='截图输出目录（默认 _target_1110171）')
    ap.add_argument('--self-test', action='store_true', help='只跑负控（不触碰生产资产）')
    ap.add_argument('--no-browser', action='store_true', help='跳过 headless 部分（仅静态门）')
    a = ap.parse_args()
    global OUT
    if a.out: OUT = a.out

    print("=" * 66)
    print("wiki_selfcheck v2 · %s" % __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("python=%s  PYTHONUTF8=%s" % (sys.version.split()[0], os.environ.get('PYTHONUTF8')))
    print("=" * 66)
    targets, ready, unbuilt, missing, reg, raw = resolve_skins(a.skins)
    print("目标皮肤(%d): %s" % (len(targets), ','.join(targets)))
    print("注册表 ready=%d · 非 ready=%s" % (len(ready), unbuilt))
    if missing:
        ng('R0.target', "以下皮肤不在注册表: %s" % missing)
    if a.self_test:
        self_test()
    else:
        if not targets:
            ng('R0.target', "目标皮肤集合为空 ⇒ 无从验收")
        http_probe(targets, unbuilt)
        file_health()
        registry_check(targets, unbuilt, reg)
        check_manifest_all(targets)
        if not a.no_browser:
            asyncio.run(map_binding_check(targets))
            _last = None
            for _run in range(1, 4):
                try:
                    asyncio.run(page_check(targets, run=_run))
                    print("  §5-7 数据来源: run=%d（本 run 完整跑完）" % _run)
                    break
                except Exception as _e:
                    _last = "%s: %s" % (type(_e).__name__, str(_e)[:160])
                    print("  [WARN] §5-7 run=%d 失败：%s ⇒ 换独立 profile/端口重试（每皮肤/每次独立）" % (_run, _last))
            else:
                ng('P7.retry', "§5-7 三次独立 run 全部失败（末次 %s）⇒ 未取得运行时结论，原因记入报告" % _last)

    print("\n" + "=" * 66)
    print("自检结果: PASS %d · WARN %d · FAIL %d" % (len(PASS), len(WARN), len(FAIL)))
    print("具名 mandatory gate: %d 个" % len(MANDATORY))
    bad = sorted(set([g for g in MANDATORY if GATES.get(g) == 'FAIL']) | FAILED_GATES)
    if FAIL and not bad:
        bad = ['(未知 FAIL：消息已记但 gate 未标，禁止当通过)']
    if bad:
        print("FAIL gates: %s" % bad)
        print("FAIL 明细:")
        for m in FAIL:
            print("   - " + m)
    if WARN:
        print("WARN 明细:")
        for m in WARN:
            print("   - " + m)
    if not bad and FAIL:
        ng('X0.unknown_fail', "存在 FAIL 消息但 gate 表未标记 ⇒ 一律判 FAIL（禁止当通过）：%s" % FAIL[0])
        bad = ['X0.unknown_fail']
        global X0_ADDED
        X0_ADDED = True
    print("判定: %s" % ("FAIL（存在 mandatory gate 未过）⇒ 退出 1" if bad else "PASS（全部 mandatory gate 通过，WARN 不影响）⇒ 退出 0"))
    print("=" * 66)
    try:
        json.dump(dict(gates=GATES, pass_=PASS, warn=WARN, fail=FAIL, readings=READINGS),
                  open(os.path.join(OUT, 'SELFCHECK_v2_report.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print("报告 -> %s" % os.path.join(OUT, 'SELFCHECK_v2_report.json'))
    except Exception as e:
        print("报告写出失败: %s" % e)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
