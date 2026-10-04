"""武器皮肤卡统一设计（2026-09-13）守护：结构（静态）+ 真实浏览器渲染。

卡面：品级在标题左 → 大标题=武器名 → 右上角 上架时间+皮肤ID → facts（武器类型/特效/特效名/联动IP/状态）
展开：官方描述 → 特效详情 → 历史参考信息 → 技术详情（跳转 + 折叠区保留）
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "board.html"
WB = ROOT / "data" / "workbench_boards" / "weapon_skin_active.json"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

WRAPPER = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><pre id="probe">pending</pre>
<iframe id="fr" src="board.html?b=weapon_skin_active" style="width:1500px;height:700px"></iframe>
<script>
const fr=document.getElementById("fr");
fr.onload=()=>setTimeout(()=>{const d=fr.contentDocument,out={};
 const cards=[...d.querySelectorAll(".skin-card")];out.total=cards.length;
 // 取一张确实带「特效详情」折叠块的卡（canonical effects 或表现条目）
 cards.forEach(x=>x.querySelector(".skin-summary").click());
 const c=cards.find(x=>x.querySelector(".skin-detail details.perf")&&x.querySelector(".skin-desc"))||cards.find(x=>x.querySelector(".skin-detail details.perf"))||cards[0];
 const head=c.querySelector(".skin-head-row");
 out.head=[...head.children].map(e=>e.className);
 out.facts=[...c.querySelectorAll(".skin-facts .fact")].map(e=>e.textContent.replace(/\\s+/g," ").trim());
 c.querySelector(".skin-summary").click();
 out.sections=[...c.querySelectorAll(".skin-detail h4")].map(e=>e.textContent);
 out.fxsummary=(c.querySelector("details.perf summary")||{}).textContent||null;
 out.fxchips=[...c.querySelectorAll(".fx-chip")].length;
 out.perf_rows=[...c.querySelectorAll("details.perf li.perf-row")].length;
 const j=c.querySelector(".tech-jump a");
 out.jump=j?j.getAttribute("href"):null;
 out.tech=(c.querySelector(".tech summary")||{}).textContent||null;
 out.badges=c.querySelectorAll(".grade-badge").length;
 document.getElementById("probe").textContent="PROBE "+JSON.stringify(out);},2000);
</script></body></html>"""


class StaticLayout(unittest.TestCase):
    def test_head_row_order_grade_then_name_then_meta(self):
        h = BOARD.read_text(encoding="utf-8")
        i = h.find('class="skin-head-row"')
        self.assertGreater(i, 0, "卡面缺少 .skin-head-row")
        seg = h[i:i + 900]
        for token in ("grade-badge", "skin-name", "skin-head-right", "skin-sale", "skin-id"):
            self.assertIn(token, seg, token)
        self.assertLess(seg.find("grade-badge"), seg.find("skin-name"), "品级必须在标题左侧")
        self.assertLess(seg.find("skin-name"), seg.find("skin-head-right"), "右上角元信息在标题之后")

    def test_facts_row_has_required_labels(self):
        h = BOARD.read_text(encoding="utf-8")
        for label in ("武器类型", "特效", "特效名", "联动IP", "上架状态", "名称"):
            self.assertIn(f"<b>{label}</b>", h, label)
        self.assertIn("if(ip)facts.push", h)      # 无 IP ⇒ 不渲染该项

    def test_detail_sections_and_tech_jump(self):
        h = BOARD.read_text(encoding="utf-8")
        for sec in ("官方描述", "历史参考信息"):
            self.assertIn(f"<h4>{sec}</h4>", h, sec)
        # 特效详情 = 折叠块（canonical 类别 chips + 展示层特效名），与技术详情同构
        self.assertIn("<summary>特效与战斗表现", h)
        self.assertNotIn("<summary>表现详情", h)
        self.assertNotIn("<h4>战斗表现</h4>", h)      # 单一栏目：不得再出现「战斗表现」独立块
        self.assertIn('class="perf-list"', h)          # 统一业务项单列表
        self.assertIn("BIZ_ORDER", h)
        # 技术详情区块保留（含 summary），但不再有跳转链接
        self.assertNotIn("tech-jump", h)
        self.assertIn("技术详情 / 数据来源 / 审计信息", h)

    def test_presentation_fields_are_marked(self):
        h = BOARD.read_text(encoding="utf-8")
        self.assertIn("pres-mark", h)
        self.assertIn("历史展示", h)
        self.assertIn("board 派生 · 仅历史展示", h)

    def test_projection_carries_card_fields(self):
        if not WB.exists():
            self.skipTest("投影未生成")
        wb = json.loads(WB.read_text(encoding="utf-8"))
        it = next(i for i in wb["items"] if i["skin_item_id"] == 1110012)
        self.assertEqual(it["weapon_type_cn"], "喷火器")
        self.assertEqual(it["sale_date"], "2026-02-12")
        self.assertGreaterEqual(it["effects"]["count"], 1)
        self.assertIn("命中效果", it["effects"]["present"])
        self.assertEqual(it["ip_liaison_state"], "unresolved")
        self.assertIn("workbench_entity.html", it["tech_link"])
        self.assertEqual(it["official_desc_source"], "user_provided_historical_catalog")
        for i in wb["items"]:
            self.assertNotIn("grade", i)


class RealBrowserLayout(unittest.TestCase):
    def _probe(self) -> dict:
        if not CHROME.exists():
            self.skipTest("无 Chrome")
        wrapper = ROOT / "_wb_card_layout_probe.html"
        wrapper.write_text(WRAPPER, encoding="utf-8")
        prof = Path(os.environ.get("LOCALAPPDATA", ".")) / "Temp" / "ws_card_layout_prof"
        try:
            r = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--allow-file-access-from-files", f"--user-data-dir={prof}",
                                "--virtual-time-budget=16000", "--dump-dom",
                                wrapper.resolve().as_uri()],
                               capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=300)
            m = re.search(r"PROBE (\{.*?\})</pre>", r.stdout or "", re.S)
            self.assertIsNotNone(m, "探针无输出")
            return json.loads(m.group(1))
        finally:
            wrapper.unlink(missing_ok=True)

    def test_real_browser_card(self):
        d = self._probe()
        self.assertEqual(d["total"], 126)
        self.assertTrue(d["head"][0].startswith("skin-tag grad"), d["head"])
        self.assertIn("skin-name", d["head"][1])
        self.assertIn("skin-head-right", d["head"][2])
        joined = " | ".join(d["facts"])
        for label in ("武器类型", "特效", "上架状态", "名称"):
            self.assertIn(label, joined)
        if "联动IP" in joined:            # 没 IP 的卡不显示该项；有值时必须带值
            self.assertRegex(joined, r"联动IP\s*\S+")
        if "特效名" in joined:            # 有展示层特效名时必须标「历史」
            self.assertIn("历史", joined, joined)
        self.assertIn("历史参考信息", d["sections"])
        self.assertTrue(str(d.get("fxsummary") or "").startswith("特效与战斗表现"), d.get("fxsummary"))
        self.assertFalse([x for x in (d.get("sections") or []) if x == "战斗表现"], "不得有「战斗表现」独立栏目")
        self.assertIn("官方描述", d["sections"])       # 该样本卡带官方描述
        self.assertEqual(d.get("fxchips") or 0, 0)          # fx chips 已并入统一业务项列表
        self.assertGreaterEqual(d.get("perf_rows") or 0, 1)  # 标准：只显示存在的项（不造空栏目）
        self.assertEqual(d["tech"], "技术详情 / 数据来源 / 审计信息")
        self.assertEqual(d["badges"], 1, "每张卡只应有一个品级徽章")


if __name__ == "__main__":
    unittest.main()
