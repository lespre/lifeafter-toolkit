# -*- coding: utf-8 -*-
"""「特效与战斗表现」统一业务项守护（用户 2026-09-13 口径）。

要求：
  1) 固定业务顺序：命中效果 / 击败特效 / 伤害跳字 / 攻击弹道（冷兵器=挥砍特效）/ 战斗音效 /
     攻击准心 / 特殊交互 / 核芯联动 / 专属战斗动作 / 专属待机动作 / 其它
  2) 只按业务项渲染，不得再叠一份面板子卡片（同一信息只出现一次）
  3) 不得出现 (15)/(16) 锚点泄漏
  4) 真实 Chrome（headless + file:// + iframe）实测：每个栏目 计数 == 渲染行数、块内顺序正确、无重复项

无 Chrome 时动态部分 skip，不假装通过。
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD = ROOT / "board.html"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROBE = ROOT / "_perf_probe_test.html"

LABEL_ALIAS = {"挥砍特效": "攻击弹道",          # 冷兵器：攻击弹道位显示为「挥砍特效」
               "护臂开合": "其它", "蓄力表现": "其它", "爆炸特效": "其它", "弹壳表现": "其它", "预览表现": "其它"}
BIZ_ORDER = ["命中效果", "击败特效", "伤害跳字", "攻击弹道", "战斗音效", "攻击准心",
             "特殊交互", "核芯联动", "专属战斗动作", "专属待机动作", "其它"]
# 旧口径的原始 source 类目名（不得出现在统一项表里当业务标签）
RAW_LABELS = ["命中特效", "枪口/弹道", "开火表现", "专属动作"]

PROBE_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<pre id="probe">pending</pre>
<iframe id="fr" src="board.html?b=weapon_skin_sfx_text_sources" style="width:1400px;height:900px"></iframe>
<script>
const out={};const fr=document.getElementById("fr");
fr.onload=()=>{setTimeout(()=>{
 const d=fr.contentDocument;
 const cards=[...d.querySelectorAll(".skin-card")];
 out.cards=cards.length;
 const blocks=d.querySelectorAll("details.perf");
 out.perf_blocks=blocks.length;
 out.legacy_panel_nodes=d.querySelectorAll("details.perf .combat-panel").length;
 out.legacy_ct_rows=d.querySelectorAll("details.perf .ct-row").length;
 out.fx_chips=d.querySelectorAll("details.perf .fx-chip").length;
 let all="";blocks.forEach(b=>{all+=b.textContent;});
 out.anchor_leak=/\(15\)|\(16\)/.test(all);
 const counts=[],rowsOut=[];
 [...blocks].slice(0,8).forEach(b=>{
   const sum=b.querySelector("summary");
   const lis=[...b.querySelectorAll("li.perf-row")];
   if(sum)counts.push([(sum.textContent.match(/(\\d+)\\s*项/)||[])[1],lis.length]);
   const g=(li,s)=>{const e=li.querySelector(s);return e?e.textContent.trim():"";};
   rowsOut.push(lis.map(li=>g(li,".perf-cat")+"|"+g(li,".perf-name")+"|"+g(li,".perf-src")));
 });
 out.counts=counts;out.blocks=rowsOut;
 document.getElementById("probe").textContent="PROBE "+JSON.stringify(out);
},2500);};
</script></body></html>"""


class PerfSectionUnified(unittest.TestCase):
    def test_static_business_order_and_no_raw_labels(self):
        html = BOARD.read_text(encoding="utf-8")
        self.assertIn("BIZ_ORDER", html)
        seg = html[html.find("const BIZ_ORDER"):html.find("function skinTypeTxt")]
        for label in BIZ_ORDER[:-1]:
            self.assertIn('"%s"' % label, seg, label)
        for raw in RAW_LABELS:
            self.assertNotIn('t:"%s"' % raw, seg, "统一项表里混入原始类目名：%s" % raw)
        self.assertIn('melee:"挥砍特效"', seg)

    def test_single_renderer_no_duplicate_block(self):
        html = BOARD.read_text(encoding="utf-8")
        i = html.find("function renderPerfDetail(it){")
        j = html.find("function skinTypeTxt(it){")
        body = html[i:j]
        self.assertNotIn("renderCombatPanel(", body, "不得再在同一栏目里叠一份面板子卡片")
        self.assertEqual(body.count("combatItems(it)"), 1)
        self.assertIn("renderCombatUnified(it)", body)

    def test_browser_rows_follow_order_and_count(self):
        if not CHROME.exists():
            self.skipTest("无 Chrome")
        PROBE.write_text(PROBE_HTML, encoding="utf-8")
        r = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                            "--virtual-time-budget=20000", "--dump-dom",
                            "file:///" + str(PROBE).replace("\\", "/")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        m = re.search(r"PROBE (\{.*?\})</pre>", r.stdout or "", re.S)
        self.assertIsNotNone(m, "未取到 PROBE 结果")
        out = json.loads(m.group(1))
        self.assertGreater(out["cards"], 50)
        self.assertGreater(out["perf_blocks"], 0)
        self.assertEqual(out["legacy_panel_nodes"], 0, "旧子卡片仍在")
        self.assertEqual(out["legacy_ct_rows"], 0, "旧 ct-row 仍在")
        self.assertEqual(out["fx_chips"], 0, "旧 fx chips 仍在（重复信息）")
        self.assertFalse(out["anchor_leak"], "锚点 (15)/(16) 泄漏到展示")
        self.assertTrue(out["counts"], "未读到任何栏目计数")
        for cnt, n in out["counts"]:
            self.assertEqual(int(cnt), n, "summary 计数与渲染行数不一致")
        for blk in out["blocks"]:
            seq = [x.split("|")[0] for x in blk]
            self.assertTrue(seq, "空 block")
            for s in seq:
                self.assertIn(LABEL_ALIAS.get(s, s), BIZ_ORDER, "出现非业务项类目：%s" % s)
            idx = [BIZ_ORDER.index(LABEL_ALIAS.get(s, s)) for s in seq]
            self.assertEqual(idx, sorted(idx), "块内顺序不符：%s" % seq)
            self.assertEqual(len(seq), len(set(seq)), "块内出现重复项：%s" % seq)
            core = [x for x in seq if x in BIZ_ORDER]        # 其余项（护臂开合/蓄力表现…）允许并存
            self.assertEqual(len(core), len(set(core)), "块内同一业务项重复：%s" % core)
            for row in blk:
                _, name, src = (row.split("|") + ["", "", ""])[:3]
                self.assertTrue(name, "空值项未省略或未标已配置：%s" % row)


if __name__ == "__main__":
    unittest.main()
