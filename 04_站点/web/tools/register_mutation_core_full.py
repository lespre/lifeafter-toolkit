# -*- coding: utf-8 -*-
"""把 mutation_core_full 登记进三处入口：publication_policy / manifest / wiki_taxonomy。

★ 不跑 tools/build_wiki.py：它会把 data/boards/*.js 全部重写（含 fashion_wardrobe /
  vehicle_full / weapon_skin_* —— 本任务禁改）。这里只做定向登记，且每个文件都先
  做「原文件可无损重排」自检，再写回；不动其它板。
"""
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path('E:/la拆包项目/04_站点/web')
BOARD_ID = 'mutation_core_full'


def dump(obj, indent):
    return json.dumps(obj, ensure_ascii=False, indent=indent).replace('\n', '\r\n')


def lossless(raw, indent):
    return dump(json.loads(raw), indent) == raw


# ── 1. board ──
board = json.loads((ROOT / 'data/boards/mutation_core_full.json').read_text(encoding='utf-8'))
meta, items = board['meta'], board['items']
st = board['stats']
ic = meta['icon_stats']
evc = Counter(it['evidence'] for it in items)
chain = Counter(it.get('provenance', {}).get('locator_chain', {}).get('chain_status', 'missing')
                for it in items)

# ── 2. policy ──
pol_path = ROOT / 'data/publication_policy.json'
pol_raw = pol_path.read_text(encoding='utf-8')
pol = json.loads(pol_raw)
print('[格式自检] publication_policy  无损重排: %s' % lossless(pol_raw, 2))
pol['boards'][BOARD_ID] = {
    'publication_status': 'published',
    'category': meta['category'],
    'items': len(items),
    'reason': (
        '异变核芯全量表：common_item 660000 段 %d 行（%d 个唯一核芯名）逐行 name/desc/icon 槽位回放，'
        '按名字精确关联 gift_data 的「（禁交易）」礼包行 %d 个与核芯卡 skill_icon；'
        '全部 %d 张图逐张过 pe_file_index/gpk_loc0 精确命中后从 pe_packs 解码（命中率 %s）。'
        '品级取自 desc 原文前缀，不做推断。只证静态表内容与资源存在，不证当前可得/可购买。'
        % (len(items), st['unique_names'], st['gift_ids'], ic['png_files'], ic['hit_rate'])),
}
pol_path.write_text(dump(pol, 2), encoding='utf-8', newline='')
(ROOT / 'data/publication_policy.js').write_text(
    'window.WIKI_PUBLICATION_POLICY = ' + dump(pol, 2) + ';\r\n', encoding='utf-8', newline='')
print('[policy] boards 条目 %d（含 %s）' % (len(pol['boards']), BOARD_ID))

# ── 3. manifest ──
man_path = ROOT / 'data/manifest.js'
man_raw = man_path.read_text(encoding='utf-8')
prefix = 'window.WIKI_MANIFEST = '
assert man_raw.startswith(prefix), man_raw[:40]
man = json.loads(man_raw[len(prefix):].strip().rstrip(';'))
print('[格式自检] manifest            无损重排: %s'
      % lossless(man_raw[len(prefix):].strip().rstrip(';'), 2))
entry = {
    'name': meta['name'],
    'category': meta['category'],
    'board': BOARD_ID,
    'items': len(items),
    'generated': meta['generated'],
    'source_server': meta['source_server'],
    'package_sha': meta['package_sha'],
    'evidence': dict(evc),
    'state_summary': {},
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
print('[manifest] boards %d → %d（%s items=%d）' % (before, len(boards), BOARD_ID, len(items)))

# ── 4. taxonomy ──
tax_path = ROOT / 'data/wiki_taxonomy.json'
tax_raw = tax_path.read_text(encoding='utf-8')
tax = json.loads(tax_raw)
print('[格式自检] wiki_taxonomy       无损重排: %s' % lossless(tax_raw, 1))


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
    node = node or find(top, 'combat.nucleus')
assert node is not None, 'taxonomy 节点 combat.nucleus 不存在'
bl = node.setdefault('boards', [])
if BOARD_ID not in bl:
    bl.append(BOARD_ID)
tax_path.write_text(dump(tax, 1), encoding='utf-8', newline='')
(ROOT / 'data/wiki_taxonomy.js').write_text(
    'window.WIKI_TAXONOMY = ' + dump(tax, 1) + ';\r\n', encoding='utf-8', newline='')
print('[taxonomy] %s boards = %s' % (node['name'], bl))
print('generated', meta['generated'], date.today().isoformat())
