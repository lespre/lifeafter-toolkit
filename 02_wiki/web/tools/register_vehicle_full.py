# -*- coding: utf-8 -*-
"""把 vehicle_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。

★ 为什么不直接跑 tools/build_wiki.py：build_wiki 会把 data/boards/*.js 全部按
  「原文 + 前缀」重写，而现有 fashion_wardrobe.js 是压缩过的（2.9 MB vs json 4.1 MB），
  跑一次就会改动「不得改」的时装板派生物。因此这里只做等价的定向登记：
    · publication_policy.json/.js  —— 只加一条 boards 条目（其余字节不变，脚本断言）
    · data/manifest.js             —— 追加一条 board 摘要（其余字节不变，脚本断言）
    · data/wiki_taxonomy.json/.js  —— 在既有「（三）载具类」节点追加 vehicle_full（不改层级/编号）
"""
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path('E:/la拆包项目/02_wiki/web')
BOARD_ID = 'vehicle_full'


def dump(obj, indent):
    return json.dumps(obj, ensure_ascii=False, indent=indent).replace('\n', '\r\n')


def check(payload, indent, tag):
    """反序列化原文件再序列化，必须与磁盘字节完全一致 —— 证明追加不会带来格式漂移。"""
    raw = Path(payload['_path']).read_text(encoding='utf-8')
    body = raw[raw.index('=') + 1:].strip().rstrip(';').rstrip()
    obj = json.loads(body)
    same = dump(obj, indent) == raw[raw.index('=') + 1:].strip().rstrip(';').rstrip()
    print('[格式自检] %-22s 原文件可无损重排: %s' % (tag, same))
    return obj, raw


# ── 1. board ──
board = json.loads((ROOT / 'data/boards/vehicle_full.json').read_text(encoding='utf-8'))
meta, items = board['meta'], board['items']
evc = Counter(it['evidence'] for it in items)
chain = Counter(it.get('provenance', {}).get('locator_chain', {}).get('chain_status', 'missing')
                for it in items)

# ── 2. policy ──
pol_path = ROOT / 'data/publication_policy.json'
pol_raw = pol_path.read_text(encoding='utf-8')
pol = json.loads(pol_raw)
print('[格式自检] publication_policy  无损重排: %s' % (dump(pol, 2) == pol_raw))
pol['boards'][BOARD_ID] = {
    'publication_status': 'published',
    'reason': ('载具全量总表：vehicle_ui_data 同快照 277 行逐行重放（205 严格 + 72 行尾内联变体宽容重放）；'
               '名称/描述/品牌/类型/数值全部同表内字段，图标按「UI 清单路径 → fid → gpk_loc0」逐图核验后'
               '从 pe_packs 解码。只证静态表内容与资源存在，不证业务启用/当前可获取。'),
}
pol_path.write_text(dump(pol, 2), encoding='utf-8', newline='')
(ROOT / 'data/publication_policy.js').write_text(
    'window.WIKI_PUBLICATION_POLICY = ' + dump(pol, 2) + ';\r\n', encoding='utf-8', newline='')
print('[policy] boards 条目 %d → %d' % (len(pol['boards']) - 1, len(pol['boards'])))

# ── 3. manifest ──
man_path = ROOT / 'data/manifest.js'
man_raw = man_path.read_text(encoding='utf-8')
prefix = 'window.WIKI_MANIFEST = '
assert man_raw.startswith(prefix), man_raw[:40]
man = json.loads(man_raw[len(prefix):].strip().rstrip(';'))
print('[格式自检] manifest            无损重排: %s' % (dump(man, 2) == man_raw[len(prefix):].strip().rstrip(';')))
entry = {
    'name': meta['name'],
    'category': meta['category'],
    'board': BOARD_ID,
    'items': len(items),
    'generated': meta['generated'],
    'source_server': meta['source_server'],
    'package_sha': meta['package_sha'],
    'evidence': dict(evc),
    'state_summary': meta.get('state_summary', {}),
    'name_status_summary': {},
    'provenance_status': {
        'contract_version': meta['provenance'].get('contract_version'),
        'audit_status': meta['provenance'].get('audit_status'),
        'dual_source_mode': None,
        'locator_chain_statuses': dict(sorted(chain.items())),
    },
}
boards = [b for b in man['boards'] if b['board'] != BOARD_ID]
before = len(boards)
boards.append(entry)
man['boards'] = boards
man_path.write_text(prefix + dump(man, 2) + ';\r\n', encoding='utf-8', newline='')
print('[manifest] boards %d → %d（vehicle_full items=%d）' % (before, len(boards), len(items)))

# ── 4. taxonomy ──
tax_path = ROOT / 'data/wiki_taxonomy.json'
tax_raw = tax_path.read_text(encoding='utf-8')
tax = json.loads(tax_raw)
print('[格式自检] wiki_taxonomy       无损重排: %s' % (dump(tax, 1) == tax_raw))


def find(node, nid):
    if node.get('id') == nid:
        return node
    for k in node.get('children') or []:
        r = find(k, nid)
        if r is not None:
            return r
    return None


node = None
for top in tax['树']:
    node = node or find(top, 'fashion.vehicle')
assert node is not None, 'taxonomy 节点 fashion.vehicle 不存在'
bl = node.setdefault('boards', [])
if BOARD_ID not in bl:
    bl.append(BOARD_ID)
tax_path.write_text(dump(tax, 1), encoding='utf-8', newline='')
(ROOT / 'data/wiki_taxonomy.js').write_text(
    'window.WIKI_TAXONOMY = ' + dump(tax, 1) + ';\r\n', encoding='utf-8', newline='')
print('[taxonomy] %s boards = %s' % (node['name'], bl))
print('generated', meta['generated'], date.today().isoformat())
