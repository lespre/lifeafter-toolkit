import json
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path('02_wiki/web/assets/lottery_icons')
board = json.loads(Path('02_wiki/web/data/boards/lottery_periods.json').read_text(encoding='utf-8'))
nm = {}
for i in board['items']:
    if i.get('item_id'): nm.setdefault(str(i['item_id']), i.get('name') or '')
ids = list(dict.fromkeys(str(i['item_id']) for i in board['items'] if i.get('item_id')))
idx = json.loads(Path('01_索引与产物/30_分析/common_item_icon_index.json').read_text(encoding='utf-8'))
local = idx['local_ktx']
repF = json.loads(Path('01_索引与产物/30_分析/lottery_icons_fill_families_report.json').read_text(encoding='utf-8'))
fam = [d['id'] for d in repF['detail']]
fams = set(fam)
a_ids = [i for i in ids if i in local and i not in fams and (OUT / f'{i}.png').exists()]

def spread(lst, n):
    if len(lst) <= n: return lst
    step = len(lst) / n
    return [lst[int(k * step)] for k in range(n)]

fuzzy = [d['id'] for d in repF['detail'] if d.get('fuzzy')]
picks = spread(a_ids, 6) + spread(fam, 6)
picks += fuzzy[:3]
picks = list(dict.fromkeys(picks))[:12]
CELL = 170
cols = 4
rows = (len(picks) + cols - 1) // cols
sheet = Image.new('RGBA', (cols * CELL, rows * (CELL + 34)), (24, 24, 28, 255))
dr = ImageDraw.Draw(sheet)
for k, iid in enumerate(picks):
    p = OUT / f'{iid}.png'
    im = Image.open(p).convert('RGBA')
    im.thumbnail((CELL - 14, CELL - 14))
    x = (k % cols) * CELL
    y = (k // cols) * (CELL + 34)
    for by in range(0, CELL, 16):
        for bx in range(0, CELL, 16):
            shade = (58, 58, 64, 255) if (bx // 16 + by // 16) % 2 == 0 else (42, 42, 48, 255)
            dr.rectangle([x + bx, y + by, x + bx + 15, y + by + 15], fill=shade)
    sheet.alpha_composite(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
    dr.text((x + 4, y + CELL + 2), f'{iid}', fill=(255, 255, 255, 255))
    dr.text((x + 4, y + CELL + 16), (nm.get(iid) or '')[:20], fill=(180, 200, 255, 255))
out = Path('02_wiki/web/tools/_contact_sheet_lottery_icons.png')
sheet.convert('RGB').save(out)
print(out.resolve())
for i in picks:
    im = Image.open(OUT / f'{i}.png')
    print(i, nm.get(i), im.size, im.mode)
