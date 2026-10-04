# -*- coding: utf-8 -*-
'''task-62：dg 源侧 A/B/C 期望复核 + 报告 §19 追加'''
import io, json, hashlib, os, sys
sys.stdout.reconfigure(encoding='utf-8')
INV = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_inventory.json'
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_report.md'
D = json.loads(open(INV, 'rb').read().decode('utf-8'))
md = [n for n in D['nodes'] if n['tag'] == 'Model']
cls = {}
for n in md:
    t = set(n['tracks'])
    c = 'A' if ('u_emissivecolor' in t or 'u_emissive_color' in t) else ('B' if 'u_diffuse_color' in t else 'C')
    cls.setdefault(c, []).append(n['name'])
print('dg 16 Model 源侧 A/B/C:', {k: len(v) for k, v in cls.items()})
print('C 行:', cls.get('C'))
print('A 行:', cls.get('A'))
print('dg 节点名全表唯一:', len({n['name'] for n in D['nodes']}) == len(D['nodes']))
sec = u'''

---

## §19 task-62 (b) 前置：`_dg.sfx` 解包互证 + dissolve 裁决登记 + 交接书

### 19.1 `_dg.sfx` 独立解包（已与 env-auditor 互证）
`E:\\mrzh\\Documents\\gres\\0057.gpk` **row 32153**：`block_base=1,823,837,828 + off=652,984 + 20 = 1,824,490,832`，`comp=4,654`、`flag=12(zstd, 28b52ffd…)` ⇒ **解出 66,424 B = dec 精确吻合，sha16 `9F4FE3A6AD3F8851`**（与 env-auditor 的解**逐位一致**）。格式 = GBK 明文 `<FxGroup Name="MyFx" …>`；**23 节点 = Dummy 3 / Model 16 / ParticleSystem 3 / ParticleRes 1**；**全 23 节点无 Bool 宏**。
- 16 个 Model 的 `ModelName` 全为新增 `…_dg_wl_01..08_djs.gim` + `…_dg_{01,02,04,08,09,10,12,14}_djs.gim`（**与 `_hit.sfx` 交集 0**）。
- **3 个需隔离的同名 Dummy**：`L_空特效`、`L_空特效_1_1`、`L_空特效_2`。
- dg 驱动**声明节点数**：`u_overall_opacity` 15 · `u_emissivecolor` 9 · `u_dissolve_amount` 5 · `u_emissive_desaturate` 3 · `u_emissive_highlight_intensity` 3 · `u_depth_bias` 3 · `u_mask_power` 1（口径＝"声明该 uniform 的节点数"，与 env-auditor 的"关键帧帧数"口径不同，引用须写清）。
- 机读清单：`_target_1110171\\FX029_dg_inventory.json`（脚本 `FX029_dg_unpack.py`）。

### 19.2 dissolve —— **不做**（lead 裁决 2026-09-19，选乙）
`u_dissolve_amount` 的公式（renderer-auditor，`RX_fx_dissolve_20260919.md`）虽已展开为最小式，但最小式仍需要 **`mask = t_dissolve_tex`（sampler t3）的采样值**与 **`base = Tex0.a`**：
- `<Model>` 节点在源里**不声明任何贴图槽**（lead 亲自核：hit 0/7 + jisha 0/19）；`Tex0` 语义仅 **1 个** Model 节点出现；**`t_dissolve_tex` 无任何节点声明** ⇒ **mask 源不存在**。
- 按最小式接线只能造"无源 mask" ⇒ 会引入**新的白块/黑洞**且**无可观测差异**，违反"不猜/不顶替"纪律。
⇒ **本轮不接线**，只登记 **`dissolve_state='declared_blocked(mask_source_unavailable)'`**（12 个组件），列为本报告「仍未解决」项；**待纹理绑定定证后**再评估。

### 19.3 交接书（给下一棒）
`_target_1110171\\FX029_dg_handover.md` —— 含：当前 pin、脚本与用法、`_dg.sfx` 已证事实、**(b) 注入字段清单与来源规则**（`source_sfx` 隔离 / `model_glb='sfx/dg/<stem>.glb'` / `uniform_tracks` 注入口径 / 3 个 Dummy 改名并改写 `parent`）、**7 条验收断言**（节点 66→89、`source_sfx` 分布、dg A/B/C 期望、42 个 glb 必须存在、默认关帧 sha16 仍为 `61A8171DAE53D73A`…）、已踩过的坑（gres 偏移 `block_base+row_off+20`、源无贴图、unitScale=0.1、GBK 控制台、单浏览器礼仪）。

### 19.4 未做（明确）
- (a) 16 个 `.gim`→GLB 导出 = **env-auditor**（写域 `1110177/sfx/dg/`）；(b) 合并 = 交接书所指下一棒；(c) 测量 = **viewer-auditor**。
- 本步**未改** adapter / `effects.json` / viewer.js / viewer.json / manifest / board / registry；仅新增 `FX029_dg_unpack.py`、`FX029_dg_inventory.json`、`FX029_dg_handover.md` 与本 §19。
'''
old = io.open(REP, 'r', encoding='utf-8').read()
if u'§19 task-62' not in old:
    io.open(REP, 'a', encoding='utf-8').write(sec)
    print('已追加 §19')
print('报告 sha16 =', hashlib.sha256(open(REP, 'rb').read()).hexdigest()[:16].upper(), os.path.getsize(REP), 'B')
print('交接书 sha16 =', hashlib.sha256(open(r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_handover.md', 'rb').read()).hexdigest()[:16].upper())
