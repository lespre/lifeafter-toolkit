# -*- coding: utf-8 -*-
"""生成「伤害公式」页面（反编译结论 + 证据行号 + 参数结构）。"""
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web/analysis")

HTML = r"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>伤害公式 · 反编译结论</title>
<style>
body{margin:0;padding:24px 28px;background:#0b1116;color:#dfe7ec;font:14px/1.7 "Segoe UI","Microsoft YaHei",sans-serif;max-width:1180px}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:26px 0 10px;color:#dfe7ec;border-left:3px solid #3f6a80;padding-left:10px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:18px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:16px 18px;margin-bottom:14px}
pre{background:#0d151b;border:1px solid #1e2b33;border-radius:8px;padding:12px 14px;overflow:auto;font:12.5px/1.65 ui-monospace,Consolas,monospace;color:#c3cfd7;margin:0}
code{color:#d9a441;font-family:ui-monospace,Consolas,monospace}
table{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:6px}
th,td{padding:6px 9px;border-bottom:1px solid #1a252d;text-align:left;vertical-align:top}
th{color:#7d8e99;font-weight:500;font-size:11.5px}
.ok{color:#8fbf7f}.warn{color:#d9a441}.mute{color:#7d8e99}
.note{color:#7d8e99;font-size:12px;margin-top:8px}
</style></head><body>
<h1>伤害公式 · 反编译结论</h1>
<div class="sub">源 com/formula/HurtCalc.py（APK 树 271 KB / 99 个 code 对象全部解出）· 2026-10-21</div>

<h2>一、主公式</h2>
<div class="card"><pre>护甲差值 = max(0, 破甲值 − 目标护甲值)
有效系数 = (目标护甲率 + 1) × 护甲差值 − 攻击力
伤害基数 = 插值(有效系数; interval, factor, offset)
下  限   = min(M × 攻击力, min_attack)
基  数   = max(伤害基数, 下限)
最终伤害 = 固定值 + 基数 × 技能系数</pre>
<div class="note">对应 hurt_calc 反汇编 offset 3600~4200 段（伪代码行 171–201）。</div>
</div>

<h2>二、变量从哪来</h2>
<div class="card"><table>
<thead><tr><th>变量</th><th>含义</th><th>来源</th></tr></thead>
<tbody>
<tr><td class="mono">armor_penetration</td><td>破甲值</td><td><code>additional_data.get('armor_penetration', 0)</code></td></tr>
<tr><td class="mono">target_attrs.armor</td><td>目标护甲</td><td>属性 7 护甲值</td></tr>
<tr><td class="mono">target_attrs.armor_ratio</td><td>目标护甲率</td><td>属性表护甲率</td></tr>
<tr><td class="mono">v2</td><td>攻击力</td><td>属性 1；参与 <code>M×攻击力</code> 与 <code>min_attack</code> 比较</td></tr>
<tr><td class="mono">v1</td><td>技能系数</td><td>调用方传入（技能/武器倍率）</td></tr>
<tr><td class="mono">v3</td><td>固定值</td><td>调用方传入</td></tr>
<tr><td class="mono">interval / factor / offset</td><td>分段曲线</td><td><code>special_hurt_params_data</code> 每组参数自带</td></tr>
</tbody></table></div>

<h2>三、参数组怎么选</h2>
<div class="card"><table>
<thead><tr><th>伤害来源</th><th>使用的参数前缀</th></tr></thead>
<tbody>
<tr><td>普通攻击</td><td class="mono">source_hurt_*</td></tr>
<tr><td>怪物 → 玩家</td><td class="mono">m2p_source_hurt_* / m2p_a_class_*</td></tr>
<tr><td>无人机 → 玩家</td><td class="mono">d2p_source_hurt_* / d2p_a_class_*</td></tr>
<tr><td>玩家 → 玩家</td><td class="mono">p2p_a_class_*</td></tr>
</tbody></table>
<div class="note">选择逻辑：<code>source_owner_type</code> 与 <code>target_owner_type</code> 的位掩码（2 = 怪物，33554433 = 玩家）。</div>
</div>

<h2>四、后续乘区（依次叠加）</h2>
<div class="card"><pre>基数 → 部位系数（get_body_part_hurt_rate）
     → 暴击（handle_critical_hit，基础 150%）
     → (1 + Σ伤害加成) × (1 − Σ伤害减免)
     → 护盾 / 穿透（shield_calc / replace_ignore_shield）</pre>
<div class="note">加成与减免各自先过 <code>compressed_attr_data</code> 的分段线性压缩，再进乘区。</div>
</div>

<h2>五、上下限（实测值）</h2>
<div class="card"><table>
<thead><tr><th>场景类型</th><th>加成倍率区间</th><th>说明</th></tr></thead>
<tbody>
<tr><td>南希市 / 皇牌空战</td><td class="mono">0.95 ~ 1.05</td><td>公平竞技，加成基本无效</td></tr>
<tr><td>红杉镇-全面战争</td><td class="mono">0.95 ~ 1.20</td><td>限 ±20%</td></tr>
<tr><td>夏尔镇 / 远星城 / 雷达模式</td><td class="mono">0.60 ~ 1.90</td><td>放宽到 ±80%</td></tr>
<tr><td>常规 PvE 副本</td><td class="mono">0.50 ~ 1.70</td><td>统一</td></tr>
<tr><td>矿坑 / 神秘树林</td><td class="mono">0.50 ~ 2.00</td><td>最宽松</td></tr>
</tbody></table>
<div class="note">来源：<code>special_hurt_params_data(kj1)</code> 的 min/max_hurt_additional_rate，共 98 组（详见「PvP 场景平衡」）。</div>
</div>

<h2>六、证据边界</h2>
<div class="card"><table>
<thead><tr><th>环节</th><th>状态</th></tr></thead>
<tbody>
<tr><td>主公式结构（护甲/攻击/分段/保底）</td><td class="ok">已证死（反编译）</td></tr>
<tr><td>三处乘区顺序（部位/暴击/加成）</td><td class="ok">已证死（calc_internal 调用顺序）</td></tr>
<tr><td>加成上下限数值</td><td class="ok">已证死（98 组参数表）</td></tr>
<tr><td>攻击力 = Σ装备+天赋+潜能+改造</td><td class="warn">聚合层，逐项明细不在客户端</td></tr>
<tr><td>interval/factor/offset 的具体数值</td><td class="warn">interval 与 offset 已解出部分，factor 仍是共享数组描述符，未解</td></tr>
<tr><td>护甲率 armor_ratio 的取值</td><td class="mute">属性表有该属性，具体公式在服务端</td></tr>
</tbody></table></div>

</body></html>"""

dest = WEB / "damage_formula.html"
dest.write_text(HTML, encoding="utf-8")
print("写出", dest, len(HTML), "字节")
