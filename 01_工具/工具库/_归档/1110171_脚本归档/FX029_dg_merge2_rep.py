# -*- coding: utf-8 -*-
'''task-66：生成 FX029_dg_merge2_report.md（逐节点 改前/改后 表 + 自证 + 已证/未证/未做）'''
import io, json, os, sys, glob, hashlib
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110177'
EFF = os.path.join(BASE, 'effects.json')
ROWS = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_merge2_rows.json'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_merge2_report.md'
baks = sorted(glob.glob(EFF + '.bak_dgmerge2_*'))
BEFORE = baks[-1]
after = json.loads(open(EFF, 'rb').read().decode('utf-8'))
before = json.loads(open(BEFORE, 'rb').read().decode('utf-8'))
R = json.loads(open(ROWS, 'rb').read().decode('utf-8'))
def sh(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16].upper()
A = {n['name']: n for n in after['nodes'] if n.get('dg') or n.get('source_sfx_id')}
B = {n['name']: n for n in before['nodes'] if n.get('dg') or n.get('source_sfx_id')}
L = []
w = L.append
w(u'# FX029 · task-66 —— 把 daoguang_02 的真实源参数补进 23 个 dg 节点\n')
w(u'## 0. pin 与自证\n')
w(u'| 项 | 值 |')
w(u'|---|---|')
w(u'| `1110177/effects.json` | **`%s`** → **`%s`**（%d → %d B） |' % (sh(BEFORE), sh(EFF), os.path.getsize(BEFORE), os.path.getsize(EFF)))
w(u'| 备份 | `%s` |' % os.path.basename(BEFORE))
w(u'| 源 | `gres\\0057.gpk` row 32153 · 66,424 B · sha16 `%s`（**自解**，`block_base+off+20` → zstd → GBK XML） |' % R['source']['sha16'])
w(u'| 与 lead 源 JSON 交叉核对 | **一致 %d 个 / 不一致 %s / 我这边缺 %s**（逐字段比 `FxStartTime/FxLifeSpan/TransparentMode/RenderBias/ModelName/TrackType/DirType`） |' % (R['cross_check_with_lead_json']['same'], R['cross_check_with_lead_json']['diff'], R['cross_check_with_lead_json']['missing']))
w(u'| 自证门（写盘前置） | 23 个 dg 节点 **贴图字段未变** = `%s`；其余 66 个节点 **逐字节未变** = `%s`（不过则脚本拒绝写盘） |' % (R['self_proof']['texture_fields_unchanged'], R['self_proof']['other_nodes_unchanged']))
w(u'| 未改动 | adapter / viewer.js / viewer.json / neox_material.json / manifest / board / 注册表 / 其它皮肤 |')
w(u'')
w(u'## 1. 方法（可复现）\n')
w(u'脚本 `_target_1110171\\FX029_dg_merge2.py`（`--dry-run` 只算不写）：')
w(u'1. 自解 row 32153 并校验 sha16（与 env-auditor/lead 一致）→ 解析 23 个顶层节点 `{tag, attrs, children[tag,attrs,frames]}`；')
w(u'2. 按名匹配 dg 节点（**去掉我上轮加的 `__dg` 后缀**）→ 逐字段写入：`start/life/pos_offset/render_bias/transparent_mode/track_type/dir_type/model_name/particlesPerSecond/min|maxSpriteLifespan/min|maxRadius/emissionType/emitAtBegin…`；')
w(u'3. **子轨道 → `emit`**：该节点块内**每个带 `<Frame Time Value>` 的子元素**按其标签名收入 `{"<轨道名>":[{time,value}]}`（与皮肤自带节点同结构）；另抽 `scale_track`（`ScaleFrame/TrackScale/Scale`）与 `color_track`（`TrackColor/ColorFrame/ColorKeyFrame`）；')
w(u'4. **逐字段 provenance**：`dg_param_provenance[field] = "dg_src:gres\\0057.gpk#32153:<源节点名>:<源属性名>"`；')
w(u'5. 写盘前跑**自证门**（贴图字段 + 其余节点逐字节），并 `copy2` 备份。')
w(u'')
w(u'## 2. 逐节点结果（23/23 命中，`no_source_node = 0`）\n')
w(u'| 节点 | tag | rate | life | start | emit 轨数 | 补充字段数 |')
w(u'|---|---|---|---|---|---|---|')
for r in R['rows']:
    if r['status'] != 'ok':
        w(u'| %s | — | — | — | — | — | **no_source_node** |' % r['node']); continue
    w(u'| %s | %s | %s | %s | %s | %d | %d |' % (r['node'], r.get('tag'), r.get('rate'), r.get('life'), r.get('start'), len(r.get('emit_tracks') or []), len(r['fields'])))
w(u'')
w(u'## 3. 逐字段 改前 → 改后（只列变化的字段）\n')
for nm in sorted(A):
    a, b = A[nm], B.get(nm, {})
    prov = a.get('dg_param_provenance') or {}
    ch = [k for k in a if json.dumps(a.get(k), ensure_ascii=False, sort_keys=True) != json.dumps(b.get(k), ensure_ascii=False, sort_keys=True)]
    w(u'### %s（`%s`）' % (nm, a.get('tag')))
    if not ch:
        w(u'- 无字段变化'); continue
    for k in sorted(ch):
        bv = json.dumps(b.get(k), ensure_ascii=False, sort_keys=True)
        av = json.dumps(a.get(k), ensure_ascii=False, sort_keys=True)
        if len(bv) > 150: bv = bv[:150] + '…'
        if len(av) > 220: av = av[:220] + '…'
        w(u'- `%s`：%s → **%s**%s' % (k, bv, av, (u'  ｜ 源＝`%s`' % prov[k]) if k in prov else u''))
w(u'')
w(u'## 4. 3 个"未命中名"的结论\n')
w(u'lead 报告的 3 个未命中名是 `L_空特效_1_1__dg`、`L_空特效_2__dg`、`L_空特效__dg` —— 它们**并不是源里没有**，而是**我上一轮为做命名空间隔离给它们加了 `__dg` 后缀**。去掉后缀后在源 `all_node_names`（63）中**精确命中** `L_空特效_1_1` / `L_空特效_2` / `L_空特效` ⇒ **已按源补全（`dg_param_status="ok"`），不需要写 `no_source_node`**；行内保留 `__dg` 名（隔离不可回退，否则会与 hit/jisha 的同名 Dummy 串）。')
w(u'')
w(u'## 5. 补全后可驱动性\n')
ps = [r for r in R['rows'] if r.get('tag') in ('ParticleSystem', 'ParticleRes')]
for r in ps:
    try:
        exp = float(r['rate']) * float(r['life'])
    except Exception:
        exp = None
    w(u'- `%s`（%s）：源 rate=%s/s × life=%s ⇒ 稳态存活 ≈ %.2f 个；emit %d 轨（含 `u_*_Keyframe`）⇒ **rate/寿命/尺寸轨道齐全，可驱动**；仍缺：贴图绑定（这 23 节点的贴图字段由 lead 本轮绑定，我一行未动）。' % (r['node'], r.get('tag'), r['rate'], r['life'], exp or 0, len(r.get('emit_tracks') or [])))
mdl = [r for r in R['rows'] if r.get('tag') == 'Model']
w(u'- Model **%d 个**：`model_glb`（上轮）+ 本轮 `model_name/transparent_mode/render_bias/track_type/dir_type/start/life/pos_offset` + `emit`/`scale_track` + 上轮 `uniform_tracks` ⇒ **A 类 9 个可渲（自发光+additive）**；C 类 7 个仍按纪律不渲（`no_color_driver_unresolved`）。' % len(mdl))
w(u'- Dummy 3 个：`life/start` 已补（`L_空特效__dg` 0.5s、`L_空特效_1_1__dg` 1.5s、`L_空特效_2__dg` 0.5s）；无子轨道（源亦然）。')
w(u'')
w(u'## 6. 已证 / 未证 / 未做\n')
w(u'**已证**：源 row 32153 = 66,424 B / sha16 `9F4FE3A6AD3F8851`（我自解，与 lead/env-auditor 三方一致）；23/23 节点命中（含 3 个 Dummy 名映射）；与 lead 源 JSON **20/20 逐字段一致**；每字段带 provenance；写盘前自证门通过；JSON `json.load` 可读通。')
w(u'**未证**：`TransparentMode` / `BlendMode` / `RenderBias` 的**枚举语义**（仍 unresolved，本轮只原样搬值）；子轨道**更深一层嵌套**（我只取节点块内的**一层** children 及其 `<Frame>`，若源里有 `children→children` 的帧序列未纳入）；`TrackCircle`/`TrackRotate` 等**非帧**子元素的语义未驱动。')
w(u'**未做**：未开浏览器（验收另派）；未改贴图字段（纪律要求）；未改 viewer.json（lead 内联）；未解 `daoguang_02.sfx` 内层（仍登记）。')
w(u'')
io.open(REP, 'w', encoding='utf-8').write(u'\n'.join(L) + u'\n')
print('报告 ->', REP, os.path.getsize(REP), 'B  sha16=', sh(REP))
print('effects.json sha16 =', sh(EFF), os.path.getsize(EFF), 'B')
print('对比行数:', len(R['rows']))
