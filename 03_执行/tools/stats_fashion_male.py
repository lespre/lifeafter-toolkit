# -*- coding: utf-8 -*-
"""统计时装板图片缺口：按 base 模式分组，准备男图候选。"""
import json, re, collections, sys

WARD = r"E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json"

FAM_RX = [
    ('bag',   re.compile(r'^icon_bag_([fm])_(\d+)$')),
    ('b',     re.compile(r'^icon_b_([fm])_(\d+)$')),
    ('hat',   re.compile(r'^icon_h_([fm])_(\d+)$')),
    ('suit',  re.compile(r'^icon_suit_([fm])_(\d+)$')),
    ('light', re.compile(r'^icon_light_([fm])_(\d+)$')),
    ('cloth', re.compile(r'^icon_cloth_c_(\d+)_(\d+)$')),
    ('num',   re.compile(r'^icon_(\d+)_([12])$')),
    ('plain', re.compile(r'^icon_(\d+)$')),
]


def norm(base):
    """剥目录、剥扩展名、剥 _b/_s 后缀。"""
    b = (base or '').strip().replace('\\', '/').rsplit('/', 1)[-1]
    b2 = re.sub(r'\.(ktx|dds|png|bc7)$', '', b, flags=re.I)
    return b2


def classify(base):
    b = norm(base)
    stem = re.sub(r'_[bs]$', '', b)
    for fam, rx in FAM_RX:
        m = rx.match(stem)
        if m:
            if fam == 'cloth':
                return fam, None, m.group(1), 'cloth_%s_%s' % (m.group(1), m.group(2))
            if fam == 'num':
                return 'num', ('m' if m.group(2) == '1' else 'f'), m.group(1)
            if fam == 'plain':
                return 'plain', None, m.group(1)
            return fam, m.group(1), m.group(2)
    return 'other', None, stem


def main():
    d = json.load(open(WARD, encoding='utf-8'))
    items = d['items']
    cnt = collections.Counter()
    for it in items:
        imgs = ((it.get('_media') or {}).get('images') or [])
        cnt[len(imgs)] += 1
    print('图片数分布:', sorted(cnt.items()))

    # 需要补的卡（<2 张）
    need = [it for it in items if len(((it.get('_media') or {}).get('images') or [])) < 2]
    print('需关注卡数 <2图:', len(need))

    grp = collections.Counter()
    for it in need:
        imgs = ((it.get('_media') or {}).get('images') or [])
        if not imgs:
            # 看 icons_all 里有无性别提示
            ia = it.get('icons_all') or []
            fams = set()
            for c in ia:
                fam, g, iid = classify(c.get('path', ''))
                fams.add((fam, g))
            grp[('0图', tuple(sorted(fams)))] += 1
        else:
            for im in imgs:
                fam, g, iid = classify(im.get('base', ''))
                grp[(len(imgs), fam, g)] += 1
    print('\n=== <2图 卡的 base 模式分布 ===')
    for k, v in grp.most_common(40):
        print(v, k)

    # 零图卡的 icons_all 性别可用性
    z = [it for it in items if not ((it.get('_media') or {}).get('images') or [])]
    has_m = sum(1 for it in z if any('_m_' in (c.get('path') or '') or re.search(r'_1$', (c.get('path') or '').rsplit('/', 1)[-1]) for c in (it.get('icons_all') or [])))
    print('\n零图卡 %d，其中 icons_all 含男图路径线索 %d' % (len(z), has_m))


if __name__ == '__main__':
    main()
