# -*- coding: utf-8 -*-
"""生成 PvP 伤害链页面（属性表 + 结算链 + 压缩语义）。"""
from __future__ import annotations
import sys

import html
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

OUT = pathlib.Path(WEB / "analysis")
attrs = json.loads((OUT / "pvp_attrs.json").read_text(encoding="utf-8"))

STAGES = [
    ("pre_calc_hurt", "预计算入口（内容未展开）", "函数存在 @? 5030B 系列之外"),
    ("source_calc_stage_1 / _2", "攻击方两段结算（内容未展开）", "函数存在"),
    ("target_calc_stage_1 / _2", "防守方两段结算（内容未展开）", "函数存在"),
    ("calc_internal", "主结算，14 个入参（内容未展开）", "函数存在 @196679"),
    ("_apply_rate_factor", "加成换算：属性表插值 + 区间保底", "已反编译 @138530"),
    ("handle_critical_hit", "暴击率加法桶 + 抗暴相减 + 随机判定", "已反编译 @265408"),
    ("get_body_part_hurt_rate", "部位系数 + 头部加成 + 压缩", "已反编译 @48722"),
    ("calc_talent_parry", "天赋格挡（内容未展开）", "函数存在"),
    ("shield_calc / replace_ignore_shield", "护盾与穿透（内容未展开）", "函数存在"),
    ("calc_short_pass", "未击穿/跳弹（内容未展开）", "函数存在 @196519（6B，空实现）"),
]


def row(a):
    if a["identity"]:
        tag = '<span class="tag ok">不压缩</span>'
        curve = "y = x"
    elif a["curve"]:
        tag = '<span class="tag warn">压缩</span>'
        s = a["curve"]
        curve = "%s → %s" % (s["x"], s["y"])
    else:
        tag = '<span class="tag mute">无曲线</span>'
        curve = "—"
    return "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='mono'>%s</td></tr>" % (
        a["id"], html.escape(a["name"]), a["weight"] or "—", tag, html.escape(curve))


table = "".join(row(a) for a in attrs)
flow = "".join(
    '<div class="step"><div class="sname">%s</div><div class="sdesc">%s</div><div class="sev">%s</div></div>' % (
        html.escape(n), html.escape(d), html.escape(e)) for n, d, e in STAGES)

html_doc = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>PvP 伤害链</title>
<style>
body{margin:0;padding:26px;background:#0b1116;color:#dfe7ec;font:14px/1.65 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:21px;margin:0 0 4px}
h2{font-size:15px;margin:26px 0 10px;color:#dfe7ec}
.sub{color:#7d8e99;font-size:12px;margin-bottom:16px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:16px 18px;margin-bottom:14px}
table{width:100%%;border-collapse:collapse;font-size:12.5px}
th,td{padding:7px 9px;border-bottom:1px solid #1e2b33;text-align:left;vertical-align:top}
th{color:#7d8e99;font-weight:500}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;color:#a9b8c2}
.tag{display:inline-block;padding:1px 7px;border-radius:9px;font-size:11px}
.ok{background:#16241a;color:#8fbf7f;border:1px solid #24402a}
.warn{background:#2a2013;color:#d9a441;border:1px solid #443318}
.mute{background:#1a2026;color:#7d8e99;border:1px solid #24303a}
.step{display:grid;grid-template-columns:210px 1fr 128px;gap:12px;padding:8px 0;border-bottom:1px dashed #1e2b33}
.sname{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#6f9fba}
.sdesc{font-size:12.5px;color:#c3cfd7}
.sev{font-size:11px;color:#7d8e99;text-align:right}
.k{color:#d9a441}
.note{font-size:12px;color:#a9b8c2}
</style></head><body>
<h1>PvP 伤害链</h1>
<div class="sub">源：com/formula/HurtCalc.py（APK 树 271 KB / 64 个函数，已反编译）· attribute_data · compressed_attr_data</div>

<h2>一、PvP 相关属性</h2>
<div class="card"><table>
<thead><tr><th>id</th><th>名称</th><th>战力权重</th><th>压缩</th><th>曲线</th></tr></thead>
<tbody>__TABLE__</tbody></table>
<div class="note" style="margin-top:10px">两条核心属性：<span class="k">140 对玩家造成伤害增加</span> 与 <span class="k">141 受到玩家伤害减免</span>，权重都是 800，曲线为恒等（y=x）⇒ <b>PvP 数值不经过分段压缩</b>。</div>
</div>

<h2>二、通用结算属性（PvP 同样生效，非 PvP 专属）</h2>
<div class="card"><table>
<thead><tr><th>id</th><th>名称</th><th>权重</th><th>作用</th></tr></thead>
<tbody>
<tr><td>13</td><td>伤害影响百分比</td><td>1000</td><td>造成伤害的总加成桶（主入口）</td></tr>
<tr><td>10</td><td>伤害减免百分比</td><td>500</td><td>受到伤害的总减免桶</td></tr>
<tr><td>5</td><td>暴击伤害加成</td><td>500</td><td>暴击倍率，基础 150%</td></tr>
<tr><td>6</td><td>暴击伤害减免</td><td>100</td><td>降低被暴击时的倍率</td></tr>
<tr><td>15-19</td><td>伤害加成系数（头/胸/腹/手/腿）</td><td>333-500</td><td>部位乘区</td></tr>
<tr><td>138</td><td>最大生命值</td><td>—</td><td>血量上限</td></tr>
<tr><td>228-230</td><td>狙击枪 / 榴弹炮 / 突击步枪伤害减免</td><td>250</td><td>按武器类型减伤</td></tr>
<tr><td>170 / 182 / 183 / 184</td><td>受感染者 / 人形怪 / 野生动物伤害降低</td><td>700 / 100</td><td>PvE 专用，PvP 不生效</td></tr>
</tbody></table>
<div class="note" style="margin-top:10px">13 与 10 是一对：<b>最终伤害同时受自身伤害加成和目标伤害减免影响</b>（attribute_data 原文）。</div>
</div>

<h2>三、函数清单（按 code 偏移排列，不代表调用顺序）</h2>
<div class="card">__FLOW__</div>

<h2>四、压缩语义</h2>
<div class="card"><table>
<thead><tr><th>属性</th><th>曲线</th><th>含义</th></tr></thead>
<tbody>
<tr><td>140 对玩家伤害增加</td><td class="mono">[0,0.5,1] → [0,0.5,1]</td><td>恒等，直接进加法桶</td></tr>
<tr><td>141 受到玩家伤害减免</td><td class="mono">[0,0.5,1] → [0,0.5,1]</td><td>恒等</td></tr>
<tr><td>53 针对野生动物伤害</td><td class="mono">[450,2450] → [200,2200]</td><td>PvE：低值段压 2.25 倍</td></tr>
<tr><td>425 不可压缩的暴击率</td><td class="mono">[450,2450] → [200,2200]</td><td>名字与曲线矛盾，存疑</td></tr>
<tr><td>426 不可压缩的伤害加成</td><td class="mono">[450,2450] → [200,2200]</td><td>同上</td></tr>
</tbody></table>
<div class="note" style="margin-top:10px">528 行压缩表里，<b>PvP 与百分比类属性统一走恒等曲线</b>，只有固定值类属性（采集速度、抗性、弹药量）才有真实压缩段。</div>
</div>

<h2>五、尚未定死的点</h2>
<div class="card"><div class="note">
1. <b>425/426/427</b>：名字写「不可压缩」，表里却挂着 450→2450 的压缩曲线，语义未定。<br>
2. <b>AttributeSet.add_compressed_attribute_def 是 native 实现</b>，Python 侧无源码，端点如何转成 interval/factor/offset 只能从 _apply_attr_factor 反推。<br>
3. <b>护甲/穿透/格挡</b>的数值来源（skill/hurt_params 分表）尚未逐个展开。
</div></div>
</body></html>""".replace("__TABLE__", table).replace("__FLOW__", flow)

dest = OUT / "pvp_chain.html"
dest.write_text(html_doc, encoding="utf-8")
print("写出", dest, len(html_doc), "字节")
