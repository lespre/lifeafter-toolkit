# -*- coding: utf-8 -*-
"""生成 ref_graph_report.md（第二版：修正 Q4 匹配口径与 Q5 域内清单定义）"""
import json, pathlib, collections, re, sys

PROJ = pathlib.Path(r'E:/la拆包项目')
TMP = PROJ / '90_临时'
sys.path.insert(0, str(TMP))
import _ref_scan as S

recs = [json.loads(l) for l in (TMP / 'ref_scan_cache.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
ok = {r['t']: r for r in recs if r['ok'] == 1}
VER = json.loads((TMP / 'ref_scan_verify.json').read_text(encoding='utf-8'))
ROWS = {t: r['n'] for t, r in ok.items()}
SKIP = [r for r in recs if r['ok'] != 1]

SKIP_REASON = collections.Counter()
for r in SKIP:
    e = r.get('err', '')
    if 'no x{' in e:
        SKIP_REASON['表体缺失（.py 只剩字节码壳，无 x{ 容器）'] += 1
    elif 'CHS' in e:
        SKIP_REASON['文本池不可解（_chs 为空族 / 格式不符）'] += 1
    elif '0x76' in e:
        SKIP_REASON['索引尾不是 0x76 族'] += 1
    elif 'reserved' in e:
        SKIP_REASON['表头 reserved != 0'] += 1
    elif 'ULEB' in e:
        SKIP_REASON['ULEB 截断'] += 1
    elif 'bucket' in e:
        SKIP_REASON['索引桶计数异常'] += 1
    elif 'value tag' in e:
        SKIP_REASON['未知值标记 0x11'] += 1
    else:
        SKIP_REASON['其他'] += 1

TOTAL_ROWS = sum(ROWS.values())


def tier(r, tgt='F'):
    """F/A/M：行键空间是大整数 id 段，命中率 ≥95% 即“值域就是这套 id”；
    0.3~0.95 才用 lift（随机密度基线）判别。FID 目标是小整数域，全场无判别力。"""
    if tgt == 'FID':
        return '无判别力'
    if r['ratio'] >= 0.95:
        return '确认'
    if (r['lift'] or 0) >= 5:
        return '可能'
    return '碰撞'


def pct(x):
    return f'{x*100:.0f}%'


def tbl(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(str(c) for c in r) + ' |')
    return '\n'.join(out)


def load(n):
    return S.load_table(n)


FD = load('fashion_data')[0]
PA = load('player_appear_data')[0]
PM = load('player_module_appear_data')[0]
FE = load('fashion_data_for_export')[0]
SF = load('simple_fashion_data')[0]

FD_KEYS = {int(r['key']) for r in FD}
PA_KEYS = {int(r['key']) for r in PA}
PM_KEYS = {int(r['key']) for r in PM}
FE_KEYS = {int(r['key']) for r in FE}
SF_KEYS = {int(r['key']) for r in SF}
K2F = {int(r['key']): int(r['values']['fashion_id'][1]) for r in FE if 'fashion_id' in r['values']}
FID = set(K2F.values())


def fields(rows):
    s = set()
    for r in rows:
        s |= set(r['values'])
    return s


fd_f, pa_f, pm_f, fe_f, sf_f = map(fields, (FD, PA, PM, FE, SF))
BINS = [(0, 100000), (100000, 1000000), (1000000, 10000000), (10000000, 10**12)]
BIN_COUNT = [sum(1 for k in PA_KEYS if lo <= k < hi) for lo, hi in BINS]

q1, q2, q3, qm = VER['F'], VER['A'], VER['FID'], VER['M']
q1c = [r for r in q1 if tier(r, 'F') == '确认']
q1m = [r for r in q1 if tier(r, 'F') == '可能']
q1x = [r for r in q1 if tier(r, 'F') == '碰撞']
q2c = [r for r in q2 if tier(r, 'A') == '确认']
q2m = [r for r in q2 if tier(r, 'A') == '可能']
q3_lift = [r for r in q3 if (r['lift'] or 0) >= 5]

t1 = collections.Counter(tier(r, 'F') for r in q1)
t2 = collections.Counter(tier(r, 'A') for r in q2)
tm = collections.Counter(tier(r, 'M') for r in qm)


def indeg(lst, target_table, tgt):
    return sum(1 for r in lst if r['table'] != target_table and tier(r, tgt) != '碰撞')


IDEG = [
    ('fashion_data', indeg(q1, 'fashion_data', 'F'), len(q1c), len(q1m)),
    ('player_appear_data', indeg(q2, 'player_appear_data', 'A'), len(q2c), len(q2m)),
    ('player_module_appear_data', indeg(qm, 'player_module_appear_data', 'M'), 0, sum(1 for r in qm if tier(r, 'M') == '可能')),
    ('fashion_data_for_export', sum(1 for r in q1 + q2 if r['table'] == 'fashion_data_for_export'), 0, 0),
    ('simple_fashion_data', sum(1 for r in q1 + q2 if r['table'] == 'simple_fashion_data'), 0, 0),
]

# ---------------- Q4 ----------------
TOK = {'fashion', 'appear', 'appears', 'dress', 'outfit', 'suit', 'suits', 'hair', 'hat', 'icon', 'icons', 'skin'}
Q4_RULE = ('字段名按 `_` 切词，任一词元命中 {fashion, appear, dress, outfit, suit, hair, hat, icon, skin}，'
           '或整名含 `model_id` / `model_name` 片段。')


def name_hit(k):
    kl = k.lower()
    if 'model_id' in kl or 'model_name' in kl:
        return True
    return any(t in TOK or t.startswith('fashion') or t.startswith('appear') for t in kl.split('_'))


LOOSE = re.compile(r'fashion|appear|model_id|model_name|dress|outfit|suit|hair|hat|icon|skin', re.I)
loose_extra = set()
for t, rec in ok.items():
    for k in (rec.get('allf') or {}):
        if LOOSE.search(k) and not name_hit(k):
            loose_extra.add(k)

fn = collections.defaultdict(lambda: {'tables': 0, 'rows': 0})
for t, rec in ok.items():
    for k in (rec.get('allf') or {}):
        if name_hit(k):
            fn[k]['tables'] += 1
            fn[k]['rows'] += rec['n']
q4_top = sorted(fn.items(), key=lambda x: (-x[1]['tables'], -x[1]['rows']))[:60]
q4_tables = {t for t, rec in ok.items() if any(name_hit(k) for k in (rec.get('allf') or {}))}

CAT = {k: [0, 0] for k in ('fashion', 'appear', 'icon', 'model', 'suit', 'hair', 'skin')}
_cat_tab = {k: set() for k in CAT}
for t, rec in ok.items():
    for k in (rec.get('allf') or {}):
        if not name_hit(k):
            continue
        kl = k.lower()
        toks = kl.split('_')
        if any(x.startswith('fashion') for x in toks):
            c = 'fashion'
        elif any(x.startswith('appear') for x in toks):
            c = 'appear'
        elif 'icon' in toks or 'icons' in toks:
            c = 'icon'
        elif 'model_id' in kl or 'model_name' in kl:
            c = 'model'
        elif 'suit' in toks:
            c = 'suit'
        elif 'hair' in toks:
            c = 'hair'
        elif 'skin' in toks:
            c = 'skin'
        else:
            continue
        CAT[c][0] += 1
        _cat_tab[c].add(t)
for c in CAT:
    CAT[c][1] = len(_cat_tab[c])

icon_tables = collections.Counter()
for t, rec in ok.items():
    for k in (rec.get('allf') or {}):
        if k in ('icon', 'icons', 'female_icon'):
            icon_tables[k] += 1

# ---------------- Q5 ----------------
NAME_PAT = re.compile(r'fashion|appear|dress|outfit|suit|hair', re.I)
CORE = [c for c in ['fashion_data', 'fashion_data_for_export', 'simple_fashion_data',
                    'player_appear_data', 'player_module_appear_data',
                    'player_module_appear_data_for_export'] if c in ok]
DOMAIN = sorted(set(t for t in ok if NAME_PAT.search(t)) | set(CORE))

outdeg = collections.Counter()
for lst, tg in ((q1, 'F'), (q2, 'A'), (qm, 'M')):
    for r in lst:
        if tier(r, tg) != '碰撞':
            outdeg[r['table']] += 1

dom_rows = sorted(({'t': t, 'rows': ROWS[t], 'out': outdeg.get(t, 0),
                    'fields': len(ok[t].get('allf') or {})} for t in DOMAIN),
                  key=lambda x: (-x['rows'], -x['out']))
max_dom = dom_rows[0]
top_all = sorted(ROWS.items(), key=lambda x: -x[1])[:10]

CAP = [
    ('商品名 name / show_name', lambda f: bool({'name', 'show_name'} & f)),
    ('描述 desc', lambda f: 'desc' in f),
    ('图标 icon / icons', lambda f: bool({'icon', 'icons', 'female_icon'} & f)),
    ('部位 part / part_type', lambda f: bool({'part', 'part_type'} & f)),
    ('魅力值 charm_value', lambda f: 'charm_value' in f),
    ('资源指针 appear_ids', lambda f: 'appear_ids' in f),
    ('模型名 model_name', lambda f: 'model_name' in f),
    ('模型 id model_id', lambda f: 'model_id' in f),
    ('模型路径 model_paths / v2_socket_model_path', lambda f: bool({'model_paths', 'v2_socket_model_path'} & f)),
    ('部位隐藏 hide_head / hide_face', lambda f: bool({'hide_head', 'hide_face', 'hide_pendant'} & f)),
]
CAP_T = [('fashion_data', fd_f), ('fashion_data_for_export', fe_f), ('simple_fashion_data', sf_f),
         ('player_appear_data', pa_f), ('player_module_appear_data', pm_f)]

_dom_fail = sorted(r['t'] for r in SKIP
                   if NAME_PAT.search(r['t']) or re.search(r'model|skin|dress|outfit', r['t'], re.I))

out = []
W = out.append

W('# 时装 / 外观域 反向引用扫描报告')
W('')
W('> 数据源：`01_索引与产物/41_还原树/pe/配置/com/cdata/`（还原树内已解码表；未触碰线上客户端 npk）。')
W('> 脚本：`90_临时/_ref_scan.py`（全表扫描）→ `_verify.py`（候选复核）→ `_report.py`（本报告）。')
W('> 缓存：`90_临时/ref_scan_cache.jsonl`（逐表原始结果，可断点续跑）、`ref_scan_verify.json`、`ref_scan_agg.json`。')
W('')
W('---')
W('')
W('## 0. 口径与覆盖率')
W('')
W(f'- 目录内基础表 **{len(recs)}** 张（不含 `_chs`）。')
W(f'- 成功解码 **{len(ok)}** 张，legacy 0x73 + `lenient=True`，共 **{TOTAL_ROWS:,}** 行。')
W(f'- 失败 **{len(SKIP)}** 张，逐表记录原因，**不参与任何统计、不用占位值**：')
W('')
W(tbl(['失败原因', '表数'], [[k, v] for k, v in SKIP_REASON.most_common()]))
W('')
W('**值域提取**：`0x01` 字面整数；`0x03` 布尔（丢弃）；`0x05` 文本池字符串（仅纯 ASCII 十进制串转 int）；')
W('`0x0b` `jump:<off>` 用 `BT.read_27_group` 展开，按 kind 递归（`0x0b` 子组偏移继续、`0x01` 元素是字面 id、`0x05` 元素是池索引）。')
W('列表字段把**所有元素**摊平进字段值域。')
W('')
W('**题目口径**：字段去重值中命中数 `hit ≥ 5` 且 `hit / 去重值数 ≥ 30%`。')
W('')
W('**追加的碰撞检验**（因为 Q3 的目标集合只有 403 个值却铺在 83~1054，密集度 41%，任何小整数都会“命中”）：')
W('对每个候选算随机基线 `base = |目标集合 ∩ [候选值域]| / 区间宽度`，`lift = 命中率 / base`，分三层：')
W('')
W('- **确认**：命中率 ≥ 95%（≥5 个去重值里几乎全部是合法 id —— 在 6~9 位 id 空间里，这靠巧合做不到）')
W('- **可能**：命中率 30%~95% 且 `lift ≥ 5`（混合命名空间，但明显高于随机密度）')
W('- **碰撞**：命中率 30%~95% 且 `lift < 5`（没有超过随机密度，判为命名空间巧合）')
W('')
W('注意：`lift` **不能**用作 100% 命中字段的判据——时装主键在 `166000~166999`、`460xxx~479xxx` 这类块里是**连续**的，')
W('块内随机密度本身就接近 100%，真引用的 lift 反而只有 1~3。所以 95% 以上走“全命中”判据，中段才用 lift。')
W('')
W(tbl(['目标', '来源', '规模'], [
    ['F', '`fashion_data` 行键', f'{len(FD_KEYS):,}（{min(FD_KEYS)} ~ {max(FD_KEYS)}）'],
    ['A', '`player_appear_data` 行键', f'{len(PA_KEYS):,}（{min(PA_KEYS)} ~ {max(PA_KEYS)}）'],
    ['M', '`player_module_appear_data` 行键', f'{len(PM_KEYS):,}（{min(PM_KEYS)} ~ {max(PM_KEYS)}）'],
    ['FID', '`fashion_data_for_export.fashion_id` 去重', f'{len(FID)}（来自 {len(K2F)} 行，{min(FID)} ~ {max(FID)}）'],
]))
W('')
W('---')
W('')

# ---- Q1 ----
W('## Q1 谁引用了 `fashion_data` 的行键')
W('')
W(f'过阈值 **(表,字段) = {len(q1)}**：确认 **{t1["确认"]}** / 可能 **{t1["可能"]}** / 碰撞 **{t1["碰撞"]}**。')
W('')
W('### 确认引用（%d 条，值域几乎全是合法行键）' % len(q1c))
W('')
W(tbl(['#', '表', '字段', '命中/去重', '命中率', '表行数', 'lift'],
      [[i + 1, f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift']]
       for i, r in enumerate(q1c)]))
W('')
W(f'**结论**：`fashion_data` 行键被 **{len({r["table"] for r in q1c})} 张表 / {len(q1c)} 个字段** 直接当“商品 id”引用。')
W('三个入口族：① 商店/商城 `fashion_store_data.item_id`(721/722)、`fashion_store_current_data.item_id`(202/202)、`store_data.item_id`(898/1112)；')
W('② 图鉴/收集 `fashion_obtain_handbook_data.fashion_ids`(861/867)、`fashion_free_set_data.fashion_black_list`(233/245)；')
W('③ 奖励投放 `yk_month_card_item_data.item_ids`、`optional_gift_data.pre_item_ids`、`wish_fashion_reward_data.item_ids`、`huodong_reward_data.preview_fashion_ids`。')
W('另有 4 个“标签/图鉴”族：`record_label_suit_data.suit_item_id`(42/42)、`record_label_data.suit_ids`(28/28)、')
W('`record_label_brand_hd_label_conf.free_fashion_whitelist`(110/110)、`fashion_recommend_data.item_ids`(110/110)。')
W(f'这 21 条的取值下界最低为 {min(r["vmin"] for r in q1c)}（全部落在 366xxx / 46xxxx / 47xxxx 等时装专属段），没有小整数混入。')
W('')
W('**抽样复核**（证明这些不是解析巧合）：`fashion_store_data.item_id` 去重 722 个值，721 命中，取值是连续的 `166000,166001,166002…`；')
W('唯一未命中的 `650040110` 落在时装键段 `6500401xx` 内部（该段实际存在 650040130~650040136），属于**表内悬空引用**，')
W('而不是解码错位。同理 `express_action_data.fashion_action_appear_id` 1176 个值命中 1168 个，取值 `30320,30380,30381…` 连续成段。')
W('')
W('### 可能引用（混合命名空间，共 %d 条，列前 20）' % len(q1m))
W('')
W(tbl(['表', '字段', '命中/去重', '命中率', '表行数', 'lift'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift']]
       for r in q1m[:20]]))
W('')
W('性质一致：字段是跨品类 id 容器（商店货架、礼包、抽奖奖池、爬塔排名烟花、随机奖励池），时装只占其中一类。')
W('')
W('### 碰撞（%d 条，阈值过但无判别力）' % len(q1x))
W('')
W(tbl(['表', '字段', '命中/去重', '命中率', '表行数', 'lift'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift']]
       for r in q1x]))
W('')
W('这些命中率虽过 30%，但 `lift < 5`：所在数值窗口本身很密（如 `monster_data_470.id` 的 id 段压在 166xxx 上），')
W('命中率没有超过随机密度，判定为**命名空间巧合**，不算引用。')
W('')

# ---- Q2 ----
W('## Q2 谁引用了 `player_appear_data` / `player_module_appear_data` 的行键')
W('')
W(f'过阈值：`player_appear_data` **{len(q2)}**（确认 {t2["确认"]} / 可能 {t2["可能"]} / 碰撞 {t2["碰撞"]}）；'
  f'`player_module_appear_data` **{len(qm)}**（确认 0 / 可能 {tm["可能"]} / 碰撞 {tm["碰撞"]}）。')
W('')
W('### A. `player_appear_data` 确认引用（%d 条）' % len(q2c))
W('')
W(tbl(['#', '表', '字段', '命中/去重', '命中率', '表行数', 'lift'],
      [[i + 1, f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift']]
       for i, r in enumerate(q2c)]))
W('')
_nh = re.compile(r'fashion|appear|dress|outfit|suit|hair|skin|do_face', re.I)
_low = [r for r in q2c if not _nh.search(r['table']) and not _nh.search(r['field'])]
W(f'可信度分层：{len(q2c) - len(_low)} 条来自表名本身就属于外观/捏脸体系的表（`*appear*` / `*fashion*` / `*do_face*`），语义与值域互相印证；')
W(f'{len(_low)} 条表名和字段名都不带外观语义，但值域"整段落进" appear 的 id 段，**需人工再确认**，本报告只登记不下结论：')
W('')
W('`' + '`、`'.join(r['table'] + '.' + r['field'] + f'(vmin={r["vmin"]})' for r in _low) + '`')
W('')
W('**结论**：资源层入口收敛在四个族——')
W('① `appear_ids`（`fashion_data` 4478/4538、`fashion_data_for_export` 4318/4378、`simple_fashion_data` 1817/1820，均 99~100%）；')
W('② 动作/表情 `express_action_data.fashion_action_appear_id`（1168/1176）；')
W('③ 捏脸/发型 `*_do_face_*.hair_appear_id`、`do_face_v4_*.fashion_id`；')
W('④ 自指 `player_appear_data.uncap_app_id_new / replace_flower_id / suit_app_id`（uncap 变体指向本体行键）。')
W('')
W('注意：三张 fashion 表的 `appear_ids` **不是同一份数据**（去重值 4538 / 4378 / 1820），是不同粒度的视图，不能互相替代。')
W('')
W('### B. `player_appear_data` 可能引用（%d 条，列前 20）' % len(q2m))
W('')
W(tbl(['表', '字段', '命中/去重', '命中率', '表行数', 'lift'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift']]
       for r in q2m[:20]]))
W('')
W('**结论（Q2 最重要的发现）**：`player_appear_data` 的行键空间**不是单一段**：')
W('')
W(tbl(['键区间', '键数'], [['[0, 100000)', BIN_COUNT[0]], ['[100000, 1000000)', BIN_COUNT[1]],
                           ['[1000000, 10000000)', BIN_COUNT[2]], ['[10000000, ∞)', BIN_COUNT[3]]]))
W('')
W('它从 10000 一直铺到 1430450303（uncap 变体）。于是 `monster_data_*.equip_ids`、`refresh_entities_*.group_id`、')
W('`refresh_defence_buildings_*.id` 这些**怪物/村庄刷新 id 段会与它部分重叠**，产生 30%~50%、lift 10~20 的“半命中”。')
W('这些是**不同系统复用同一数字空间**，不是外观引用；真正可信的是确认级 %d 条。' % len(q2c))
W('')
W('### C. `player_module_appear_data`（模块外观：头饰/面饰/挂饰）')
W('')
W(tbl(['表', '字段', '命中/去重', '命中率', '表行数', 'lift', '判定'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), r['rows'], r['lift'], tier(r, 'M')]
       for r in qm]))
W('')
W('**结论：按行键口径「未找到」引用方。** 4 个候选中 2 个 lift<5（`mission_step_data_52.id`、`home_party_modules_data.item_id`，')
W('值域 260010~260070 与模块键 260xxx 同段，但属不同 id 体系）；2 个 lift≥5 的语义完全无关')
W('（`npc_gossips_data.mission_hide` 是任务隐藏标记、`yk_season_store_data.reward_id` 是赛季商店奖励 id）。')
W('模块外观更可能由“模块 id / `model_socket` 槽位名”间接定位，而不是行键直连。')
W('')

# ---- Q3 ----
W('## Q3 值域命中「时装 id 序号（fashion_id）」的表')
W('')
W(f'映射先落地：`fashion_data_for_export` {len(FE):,} 行里**只有 {len(K2F)} 行带 `fashion_id`**，去重 {len(FID)} 个值，范围 {min(FID)}~{max(FID)}。')
W(f'样本核对：行键 166000 → fashion_id **{K2F.get(166000)}**（与题目一致）。')
W('')
W(f'按 30%/≥5 口径扫全表：**{len(q3)}** 个 (表,字段) 过阈值——但这几乎是纯噪音，因为：')
W('')
W(f'- 目标集合只有 {len(FID)} 个值却铺在 {max(FID)-min(FID)+1} 的区间上，**基线密度 {len(FID)/(max(FID)-min(FID)+1):.0%}**；')
W('- 阈值 30% 低于基线，等于“随便一个小整数字段都能过”。')
W('')
W(f'加上 lift 检验后，只有 **{len(q3_lift)}** 个候选 lift ≥ 5，且全部语义不符：')
W('')
W(tbl(['表', '字段', '命中/去重', '命中率', '随机基线', 'lift', '命中值样本'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), f'{r["base"]:.3f}', r['lift'],
        ', '.join(map(str, r['sample'][:6]))] for r in q3_lift]))
W('')
W('对照：lift ≈ 1（命中率完全等于随机）的典型噪音样本：')
W('')
_bad = [r for r in q3 if (r['lift'] or 0) < 1.2][:10]
W(tbl(['表', '字段', '命中/去重', '命中率', '随机基线', 'lift', '命中值样本'],
      [[f'`{r["table"]}`', f'`{r["field"]}`', f'{r["hit"]}/{r["nd"]}', pct(r['ratio']), f'{r["base"]:.3f}', r['lift'],
        ', '.join(map(str, r['sample'][:6]))] for r in _bad]))
W('')
W('**结论**：')
W('')
W('- **除 `fashion_data_for_export.fashion_id` 自身（定义方，403/403=100%）外，本次可解码的 9808 张表里没有任何字段以「fashion_id 序号」为引用目标。**')
W(f'- 这是**有证据的排除**，不是没找到：{len(q3)} 个过阈值候选中 {len(q3)-len(q3_lift)} 个 lift < 5，'
  f'剩下 {len(q3_lift)} 个 lift ≥ 5 的全是半径/血量/相机高度/圈大小。')
W('- **命名陷阱**：多个字段名叫 `fashion_id` 却存行键——`store_daily_recommended_fashion_data.fashion_id`（223/223 命中 fashion_data 行键）、')
W('  `do_face_v4_preset_data.fashion_id`（19/19 命中 appear 行键）、`saint_beast_conf_data.fashion_id`（7/7 命中行键）。**字段名不可信，值域才可信。**')
W(f'- `fashion_id` 只覆盖 {len(K2F)}/{len(FE)} 行（{len(K2F)/len(FE):.1%}），说明这个“序号”是**局部发行编号**，不是全量时装编号体系。')
W('- **反向证据**：1018 个候选里，字段名带 `fashion` / `appear` 的只有 **1** 个（就是定义它的 `fashion_data_for_export.fashion_id` 本身，lift 仅 2.41）。')
W('  也就是说，连“名字最像时装”的字段都不指向序号，序号在当前还原树里没有任何二级引用者。')
W('')

# ---- Q4 ----
W('## Q4 字段名维度（不依赖值域，交叉验证）')
W('')
W(f'匹配规则：{Q4_RULE}')
W('')
W(f'结果：**{len(fn)}** 个不同字段名，分布在 **{len(q4_tables)}** 张表。')
W(f'（若改用宽松子串，会多出 {len(loose_extra)} 个噪音字段名，例如 '
  + '、'.join(f'`{x}`' for x in ['chat_id', 'chat_msg', 'be_hated_male', 'condition_disappear_id']) +
  ' —— `chat` 里的 `hat`、`disappear` 里的 `appear`、`hated` 里的 `hat` 都会被误伤。）')
W('')
W('按词元归类（同一字段名只归一类，优先级 fashion > appear > icon > model > suit > hair > skin）：')
W('')
W(tbl(['词元组', '字段名数', '涉及表数', '说明'], [
    ['fashion*', CAT['fashion'][0], CAT['fashion'][1], '真正的时装域字段'],
    ['appear*', CAT['appear'][0], CAT['appear'][1], '外观指针/怪物外观（`monster_appears` 占大头）'],
    ['icon*', CAT['icon'][0], CAT['icon'][1], '图标 id / 路径，绝大部分是 UI、地图、称号图标'],
    ['model_id / model_name', CAT['model'][0], CAT['model'][1], '模型资源引用（资源层旁路，不走行键）'],
    ['suit*', CAT['suit'][0], CAT['suit'][1], '套装'],
    ['hair*', CAT['hair'][0], CAT['hair'][1], '发型'],
    ['skin*', CAT['skin'][0], CAT['skin'][1], '皮肤/肤色'],
]))
W('')
W(tbl(['#', '字段名', '出现表数', '累计行数'],
      [[i + 1, f'`{k}`', v['tables'], f'{v["rows"]:,}'] for i, (k, v) in enumerate(q4_top)]))
W('')
W('**结论**：')
W('')
W(f'- 名称维度补上了值域扫不到的“语义引用”：`model_name`（{fn["model_name"]["tables"]} 张表）/`model_name_prefix`'
  f'（{fn["model_name_prefix"]["tables"]} 张）/`monster_appears`（{fn["monster_appears"]["tables"]} 张）。')
W('  这些表只存**模型路径/模型名**，不存 `player_appear_data` 行键，所以 Q1/Q2 一条都扫不到。')
W(f'- 图标是**分散**的：`icon`（{icon_tables["icon"]} 张）/ `icon_path`（{fn["icon_path"]["tables"]} 张）/ '
  f'`icons`（{icon_tables["icons"]} 张）/ `female_icon`（{icon_tables["female_icon"]} 张）。')
W('  “图标 id”和“图标路径字符串”两套并存，**没有任何“图标主表”被行键引用**（Q1/Q2 里没有图标表）。')
W(f'  但要留意：{CAT["icon"][0]} 个 icon 字段横跨 {CAT["icon"][1]} 张表，绝大多数是地图/称号/UI 图标，**只有 `icons` 这一支属于时装域**。')
W(f'- 时装域真正的字段级指针只有三个：`appear_ids`（{fn["appear_ids"]["tables"]} 张表）、`fashion_ids`（{fn["fashion_ids"]["tables"]} 张）、'
  f'`hair_appear_id`（{fn["hair_appear_id"]["tables"]} 张）——与 Q1/Q2 的确认级结果吻合，构成交叉验证。')
W('')

# ---- Q5 ----
W('## Q5 有没有一张能覆盖这些散表的最大最全表？')
W('')
W('### 主干表被引用次数（合计 / 确认 / 可能；引用方不含自身）')
W('')
W(tbl(['目标表', '合计', '其中确认', '其中可能'],
      [[f'`{n}`', a, c, m] for n, a, c, m in IDEG]))
W('')
W('### 域内表清单（表名含 fashion/appear/dress/outfit/suit/hair，按行数排序）')
W('')
W(tbl(['#', '表', '行数', '引用主干(F/A/M)的字段数', '字段数'],
      [[i + 1, f'`{r["t"]}`', f'{r["rows"]:,}', r['out'], r['fields']] for i, r in enumerate(dom_rows[:30])]))
W('')
W(f'（域内共 {len(dom_rows)} 张，完整清单见缓存；此处列前 30。）')
W('')
W('### 能力矩阵（按真实字段名判定）')
W('')
W(tbl(['能力'] + [c for c, _ in CAP_T],
      [[lab] + ['Y' if pred(fset) else '—' for _, fset in CAP_T] for lab, pred in CAP]))
W('')
W('### 结论：**不存在单表覆盖**')
W('')
W('证据：')
W('')
_top_dom = [r['t'] for r in dom_rows if r['rows'] == max_dom['rows']]
W(f'1. **行数**：域内最大行数就是 **{max_dom["rows"]:,}**，由 ' + '、'.join(f'`{t}`' for t in _top_dom) +
  ' 并列（`simple_fashion_data` 只是 `fashion_data` 的 10 字段瘦身视图）。')
W('   没有任何时装域表超过它。全库行数前十为：' + '、'.join(f'`{t}`({n:,})' for t, n in top_all) + '，')
W('   其中没有一张属于时装域——**不存在隐藏的大一统表**。')
W('2. **字段互缺**（见矩阵）：`fashion_data` 有 `icons`/`show_name`/`charm_value`/`appear_ids`，但**没有 `model_name`、没有 `hide_head/hide_face`**；')
W('   `player_appear_data` 有 `model_name`/`high_model_name`/`hide_head`/`hide_face`，但**121 个字段里 0 个图标字段**，也没有商城向的 `show_name`。')
W('   两者不能互相推导：商品层给不出渲染所需的主模型名，资源层给不出商品图标与售价。')
W(f'3. **`fashion_data_for_export` 是切片不是全集**：行数 {len(FE):,} < {len(FD):,}（少 {len(FD)-len(FE)} 行），键 {len(FE_KEYS & FD_KEYS)}/{len(FE_KEYS)} 全落在 `fashion_data` 内；')
W('   字段上多 `fashion_id`/`fashion_tasting_args`/`is_functional_bag`，少 `hide_part`/`new_fashion_id_str`；')
W('   **`is_available_glowstick` 两张表都有**（题目里“少 is_available_glowstick”的说法不成立，实测共有）。')
W(f'4. **`simple_fashion_data` 是瘦身视图**：同为 {len(SF):,} 行 / {len(SF_KEYS & FD_KEYS)} 键重叠，但只有 10 个字段'
  '（`name/desc/part/valid_days/icons/model_id/model_change_color_id/appear_ids/new_fashion_id_str/change_color_id`），')
W('   没有 `show_name`、`charm_value`、`sort_key`、`max_stack_num`。')
W('')
W('### 真实结构：主干 + 三区')
W('')
W('```')
W('商品层主干  fashion_data (11169 行 / 100 字段)')
W('            ├─ 商品属性: name, show_name, desc, icons, charm_value, valid_days, level, part, part_type, sort_key')
W('            ├─ 资源指针: appear_ids ─────┐ (0x0b jump 组, kind 0x01 = 字面 id)')
W('            └─ 导出切片: fashion_data_for_export (10988 行, +fashion_id 序号, 覆盖 1178 行)')
W('                                      │')
W('资源层      player_appear_data (5604 行 / 121 字段) ←┘')
W('            主模型 model_name / high_model_name / oversea_*, 部位 part, hide_head / hide_face / hide_pendant, socket_*')
W('                                      │')
W('模块层      player_module_appear_data (1200 行 / 22 字段)  ← 独立，按行键无人引用')
W('            头饰/面饰/挂饰; icon + female_icon + desc (自带图标和文案)')
W('```')
W('')
W('### 缺失信息只能从哪张表补')
W('')
W('- **商品图标**：只有 `fashion_data.icons`（及其切片 `for_export` / `simple_fashion_data`）。`player_appear_data` 无任何图标字段，')
W('  所以“外观长什么样”在资源层查不到，必须回商品层；模块图标则只有 `player_module_appear_data.icon` / `female_icon`。')
W('- **主模型名**：只有 `player_appear_data`（`model_name`、`high_model_name`、`oversea_model_name`、`new_bone_model_name`…）。')
W('  `fashion_data` 虽带 `model_id` / `v2_socket_model_path` / `socket_models_male|female`，但**没有 `model_name`**，无法直接定位主模型文件。')
W('- **部位隐藏规则**：只有 `player_appear_data`（`hide_head`/`hide_face`/`hide_pendant`）。`fashion_data` 只有商品向的 `hide_part`/`hide_other_part`/`hide_in_bag`，语义不同。')
W('- **序号 fashion_id**：只有 `fashion_data_for_export`，且只覆盖 1178 行；`fashion_data` 内对应的是字符串键 `new_fashion_id_str`（如 `hat_3002_1_0`）。')
W('- **模块外观**：只有 `player_module_appear_data`（1200 行），`fashion_data` 里没有对应条目。')
W('')
W('### 已知盲区（解码失败但与本域强相关，未取任何数字）')
W('')
W(f'表名含 fashion/appear/suit/model/skin 的失败表共 **{len(_dom_fail)}** 张，列前 40：')
W('')
W(tbl(['表'], [[f'`{t}`'] for t in _dom_fail[:40]]))
W('')
W('这些表都落在「表体缺失（字节码壳无 `x{`）」或「文本池空族」里。其中 `appear_id_2_fashion_id`、`appear_id_2_equip_id`、')
W('`change_color_fashion_ids`、`plate_id_2_fashion_ids`、`new_appear_id_2_appear_id`、`opposite_fashion_appear_id_data` 从命名看极可能就是')
W('Q1/Q3 想找的“直连映射表”，**是本次报告最大的缺口，建议优先补解**。')
W('')
W('---')
W('')
W('## 附：交叉核对')
W('')
W('- `fashion_data` 11169 行 / 100 字段；`player_appear_data` 5604 行 / 121 字段；`player_module_appear_data` 1200 行 / 22 字段 —— 与题目基线一致。')
W(f'- `fashion_data_for_export` {len(FE)} 行，键交集 {len(FE_KEYS & FD_KEYS)}/{len(FE_KEYS)} —— 与题目一致（全为子集）。')
W(f'- `simple_fashion_data` {len(SF)} 行 / 10 字段，键交集 {len(SF_KEYS & FD_KEYS)}/{len(SF_KEYS)} —— fashion_data 的瘦身视图。')
W('- 所有数字可由 `_ref_scan.py` → `_verify.py` → `_report.py` 全链路复现。')

(TMP / 'ref_graph_report.md').write_text('\n'.join(out), encoding='utf-8')
print('ok chars=', sum(len(x) for x in out))
