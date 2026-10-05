# -*- coding: utf-8 -*-
'''task-69：把源 FxIgnore（TRUE=源禁用）按各自源补进两把皮肤的 effects.json。
- 只新增 `fxIgnore`(bool) + `fx_ignore_source`(provenance) 两个键；**其它字段零改动**（自证门不过即拒绝写盘）；
- 用法：python FXIGNORE_carry.py --dry-run | (无参数=真跑：copy2 备份 → 写盘 → 生成报告)
- 属性写法兼容 `Name = "x"`（GBK sfx，= 两侧有空格）⇒ 一律用 \\s*=\\s*。'''
import io, json, os, re, sys, hashlib, shutil, time, glob
sys.stdout.reconfigure(encoding='utf-8')
DRY = '--dry-run' in sys.argv
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
E177 = os.path.join(W, '1110177', 'effects.json')
E171 = os.path.join(W, '1110171', 'effects.json')
HIT = os.path.join(W, '1110177', 'sfx', 'fx_skin_2003_029_hit.sfx')
JISHA = os.path.join(W, '1110177', 'sfx', 'fx_skin_2003_029_jisha.sfx')
BIN171 = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'
INV = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_inventory.json'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FXIGNORE_carry_report.md'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite')
NEW = ('fxIgnore', 'fx_ignore_source')

def parse_sfx(txt):
    '''返回 {节点名: (bool|None, 原始值)}；只认 TAGS 顶层标签上的 Name/FxIgnore'''
    out = {}
    for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), txt):
        d = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', m.group(2)))
        nm = d.get('Name')
        if not nm:
            continue
        raw = d.get('FxIgnore')
        out[nm] = ((str(raw).strip().upper() == 'TRUE') if raw is not None else None, raw)
    return out

def read_txt(p):
    return io.open(p, 'rb').read().decode('gbk', 'replace')

def sh(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16].upper()

# ---- 源 1/2：1110177 的两个 sfx
src = {}
for label, p in (('fx_skin_2003_029_hit.sfx', HIT), ('fx_skin_2003_029_jisha.sfx', JISHA)):
    if not os.path.exists(p):
        print('!! 缺文件', p); sys.exit(2)
    src[label] = parse_sfx(read_txt(p))
    c = {'TRUE': 0, 'FALSE': 0, 'none': 0}
    for _n, (b, _r) in src[label].items():
        c['TRUE' if b is True else ('FALSE' if b is False else 'none')] += 1
    print('[源] %-32s 节点 %d  TRUE=%d FALSE=%d 无该属性=%d' % (label, len(src[label]), c['TRUE'], c['FALSE'], c['none']))
# ---- 源 3：1110171 bin
if not os.path.exists(BIN171):
    print('!! 缺文件', BIN171); sys.exit(2)
src171_label = os.path.basename(BIN171)
src171 = parse_sfx(read_txt(BIN171))
c = {'TRUE': 0, 'FALSE': 0, 'none': 0}
for _n, (b, _r) in src171.items():
    c['TRUE' if b is True else ('FALSE' if b is False else 'none')] += 1
print('[源] %-32s 节点 %d  TRUE=%d FALSE=%d 无该属性=%d（%d B）' % (src171_label, len(src171), c['TRUE'], c['FALSE'], c['none'], os.path.getsize(BIN171)))
# ---- 源 4：dg（自解 row 32153，与 lead JSON 同源）
import zstandard
inv = json.loads(open(INV, 'rb').read().decode('utf-8'))['source']
f = open(r'E:\mrzh\Documents\gres\0057.gpk', 'rb'); f.seek(inv['block_base'] + inv['off'] + 20)
raw = f.read(inv['comp']); f.close()
dg_txt = zstandard.ZstdDecompressor().decompress(raw, max_output_size=inv['dec'] * 4).decode('gbk', 'replace')
src_dg = parse_sfx(dg_txt)
c = {'TRUE': 0, 'FALSE': 0, 'none': 0}
for _n, (b, _r) in src_dg.items():
    c['TRUE' if b is True else ('FALSE' if b is False else 'none')] += 1
print('[源] %-32s 节点 %d  TRUE=%d FALSE=%d 无该属性=%d' % ('gres\\0057.gpk#32153', len(src_dg), c['TRUE'], c['FALSE'], c['none']))

def lookup_177(n):
    nm = n.get('name')
    if n.get('source_sfx_id'):
        key = nm.replace('__dg', '')
        v = src_dg.get(key)
        return ('gres\\0057.gpk#32153', key, v) if v else (None, key, None)
    lab = n.get('source_sfx')
    if lab in src:
        v = src[lab].get(nm)
        return (lab, nm, v) if v else (None, nm, None)
    return (None, nm, None)

def lookup_171(n):
    nm = n.get('name')
    v = src171.get(nm)
    return (src171_label, nm, v) if v else (None, nm, None)

def carry(path, lookup, skin):
    eff = json.loads(open(path, 'rb').read().decode('utf-8'))
    before = {n.get('name'): n for n in eff['nodes']}
    # ★ 不能按 name 建索引比较：1110177 有 4 处既有重名（hit↔jisha 各一份）⇒ 后一份会覆盖前一份、误报自证失败。
    #   改为**按位置**逐个快照。
    snap = [json.dumps({kk: vv for kk, vv in n.items() if kk not in NEW}, ensure_ascii=False, sort_keys=True)
            for n in eff['nodes']]
    stat = {'nodes': len(eff['nodes']), 'TRUE': 0, 'FALSE': 0, 'no_source_node': 0, 'ignored': [], 'had_before': 0}
    for n in eff['nodes']:
        lab, key, v = lookup(n)
        if v is None:
            stat['no_source_node'] += 1
            n['fx_ignore_status'] = 'no_source_node'    # 只登记，不写 fxIgnore
            continue
        b, raw_attr = v
        if 'fxIgnore' in n:
            stat['had_before'] += 1
        n['fxIgnore'] = bool(b)
        n['fx_ignore_source'] = 'source_sfx:%s:%s:FxIgnore' % (lab, key)
        stat['TRUE' if b else 'FALSE'] += 1
        if b:
            stat['ignored'].append({'node': n.get('name'), 'tag': n.get('tag'),
                                    'renderable_by_adapter': bool(n.get('renderable_by_adapter')),
                                    'has_texture': bool(n.get('texture') or n.get('texture_candidate') or n.get('texture_binding')),
                                    'src': '%s:%s' % (lab, key)})
    # 自证：除新增键外逐字节相同（按位置比）
    ok = True
    for i, n in enumerate(eff['nodes']):
        now = json.dumps({kk: vv for kk, vv in n.items() if kk not in NEW}, ensure_ascii=False, sort_keys=True)
        if i < len(snap) and now != snap[i]:
            ok = False
    print('[%s] TRUE=%d FALSE=%d no_source_node=%d 已置 ignored=%d 其中 renderable_by_adapter=true = %d ｜ 自证(除新增键外逐字节相同)=%s'
          % (skin, stat['TRUE'], stat['FALSE'], stat['no_source_node'], len(stat['ignored']),
             sum(1 for x in stat['ignored'] if x['renderable_by_adapter']), ok))
    return eff, stat, ok, path

r177, s177, ok177, p177 = carry(E177, lookup_177, '1110177')
r171, s171, ok171, p171 = carry(E171, lookup_171, '1110171')
if DRY:
    print('\n** dry-run：未写任何文件 **')
    print('1110171 ignored:', json.dumps([x['node'] for x in s171['ignored']], ensure_ascii=False))
    print('1110177 ignored:', json.dumps([x['node'] for x in s177['ignored']], ensure_ascii=False))
    sys.exit(0)
if not (ok177 and ok171):
    print('** 自证未过 ⇒ 拒绝写盘 **'); sys.exit(3)
res = {}
for path, eff in ((E177, r177), (E171, r171)):
    old = open(path, 'rb').read()
    bs = path + '.bak_fxignore_' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy2(path, bs)
    pp = '\n' in old.decode('utf-8', 'replace')[:4000]
    open(path, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(eff, ensure_ascii=False, indent=1 if pp else None, separators=None if pp else (',', ':')))
    nb = open(path, 'rb').read()
    res[os.path.basename(os.path.dirname(path))] = {
        'path': path, 'sha_before': hashlib.sha256(old).hexdigest()[:16].upper(), 'bytes_before': len(old),
        'sha_after': hashlib.sha256(nb).hexdigest()[:16].upper(), 'bytes_after': len(nb),
        'backup': os.path.basename(bs), 'json_ok': bool(json.loads(nb.decode('utf-8')))}
    print('[写] %s  %s(%d B) -> %s(%d B)  备份=%s' % (path, res[os.path.basename(os.path.dirname(path))]['sha_before'],
          len(old), res[os.path.basename(os.path.dirname(path))]['sha_after'], len(nb), os.path.basename(bs)))
# ---- 报告
L = []
w = L.append
w(u'# FXIGNORE 携带报告（task-69）—— 显示集收缩，不是美化、不是回归\n')
w(u'## 0. pin 与自证\n')
w(u'| 皮肤 | 改前 sha16 | 改后 sha16 | 字节 | 备份 |')
w(u'|---|---|---|---|---|')
for k in ('1110177', '1110171'):
    r = res[k]
    w(u'| %s | `%s` | **`%s`** | %d → %d | `%s` |' % (k, r['sha_before'], r['sha_after'], r['bytes_before'], r['bytes_after'], r['backup']))
w(u'')
w(u'**自证门**：除新增 `fxIgnore`/`fx_ignore_source`（及缺源时的 `fx_ignore_status`）外，**每个节点的其余字段 canonical JSON 逐字节相同**（脚本判定不通过即拒绝写盘）：1110177 = %s、1110171 = %s；两份 `json.load` 均可读通。' % (ok177, ok171))
w(u'')
w(u'## 1. 计数\n')
w(u'| 皮肤 | 节点数 | TRUE（= 源禁用 ⇒ ignored） | FALSE | 缺源 |')
w(u'|---|---|---|---|---|')
for k, s in (('1110177', s177), ('1110171', s171)):
    w(u'| %s | %d | **%d** | %d | %d |' % (k, s['nodes'], s['TRUE'], s['FALSE'], s['no_source_node']))
w(u'')
w(u'源：1110177 = `fx_skin_2003_029_hit.sfx`(17F/4T) + `fx_skin_2003_029_jisha.sfx`(45F) + `gres\\0057.gpk#32153`(23F 全 FALSE)；1110171 = `%s`（28 TRUE / 16 FALSE）。属性正则一律 `\\s*=\\s*`（这两个 sfx 是 GBK，写法为 `Name = "x"`）。' % src171_label)
w(u'')
w(u'## 2. 被置为 ignored 的节点（逐条）\n')
for k, s in (('1110171', s171), ('1110177', s177)):
    w(u'### %s（%d 个）' % (k, len(s['ignored'])))
    if not s['ignored']:
        w(u'- 无'); continue
    w(u'| 节点 | tag | renderable_by_adapter=true | 有贴图 | 源 |')
    w(u'|---|---|---|---|---|')
    for x in sorted(s['ignored'], key=lambda y: y['node']):
        w(u'| %s | %s | %s | %s | `%s` |' % (x['node'], x['tag'], u'**是**' if x['renderable_by_adapter'] else u'否', u'是' if x['has_texture'] else u'否', x['src']))
w(u'')
w(u'## 3. 性质声明\n')
w(u'**这是一次显示集收缩**（不渲染源 `FxIgnore=TRUE` 的节点），**不是美化，也不是回归**：只按源语义把被禁用的节点从渲染集里去掉；未被禁用的节点其字段一字未动（自证门保证）。1110171 预计有 **%d** 个当前 `renderable_by_adapter=true` 的节点会因此不再渲染（lead 给的预期是 8 个）；1110177 预计 **%d** 个。'
  % (sum(1 for x in s171['ignored'] if x['renderable_by_adapter']), sum(1 for x in s177['ignored'] if x['renderable_by_adapter'])))
w(u'')
w(u'## 4. 已证 / 未证 / 未做\n')
w(u'**已证**：两皮肤各节点的 `fxIgnore` 均取自**其自身来源**（hit/jisha 按 `source_sfx` 分文件、dg 按容器 row、1110171 按 bin），逐节点带 `fx_ignore_source` provenance；缺源节点写 `fx_ignore_status="no_source_node"`（不编造）；除新增键外零改动。')
w(u'**未证**：`FxIgnore=TRUE` 在**引擎侧的实际行为**（我们按 lead 定证的语义解释为"禁用"；本轮不重新验证语义）；1110171 的 bin 是否为其唯一 sfx 源（按 task 给定的唯一源使用）。')
w(u'**未做**：未开浏览器（验收另派）；未改 adapter/viewer.json/viewer.js/board/neox_material.json；未动任何贴图字段。')
io.open(REP, 'w', encoding='utf-8').write(u'\n'.join(L) + u'\n')
json.dump({'1110177': res['1110177'], '1110171': res['1110171'], 'stat_177': s177, 'stat_171': s171},
          io.open(r'E:\la拆包项目\03拆包产物\_target_1110171\FXIGNORE_carry_rows.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('报告 ->', REP, os.path.getsize(REP), 'B sha16=', sh(REP))
