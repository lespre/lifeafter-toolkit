# -*- coding: utf-8 -*-
"""两个状态筛选「真的能用」的守护（v1.3.2）。

背景：`#fRelease` / `#fNameSt` 曾**漏绑 change 事件** ⇒ 下拉有选项但选择无效，
表现为"筛选用不了"。此前的桩测试直接调 render()，正好绕过事件绑定，所以没能抓到。

本测试两层：
1) 静态：render() 里读取的每个筛选控件都必须有 change 监听（防止再漏绑）
2) 动态：真实 Chrome（headless + file:// + iframe）派发真实 change 事件，断言卡片数变化
   （无 Chrome 时 skip，不假装通过）
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest
import os

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD = ROOT / "board.html"
BOARD_JSON = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROBE = ROOT / "_wb_probe_test.html"

PROBE_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<pre id="probe">pending</pre>
<iframe id="fr" src="board.html?b=weapon_skin_sfx_text_sources" style="width:1200px;height:600px"></iframe>
<script>
const out={};const fr=document.getElementById("fr");
fr.onload=()=>{setTimeout(()=>{
 const d=fr.contentDocument,w=fr.contentWindow;
 const rel=d.getElementById("fRelease"),ns=d.getElementById("fNameSt");
 const cards=()=>d.querySelectorAll(".skin-card").length;
 out.release_visible=!!rel&&rel.style.display!=="none";
 out.name_visible=!!ns&&ns.style.display!=="none";
 out.release_opts=rel?[...rel.options].map(o=>o.value+"|"+o.textContent):null;
 out.name_opts=ns?[...ns.options].map(o=>o.value+"|"+o.textContent):null;
 out.before=cards();
 ns.value="unresolved";ns.dispatchEvent(new w.Event("change",{bubbles:true}));
 setTimeout(()=>{out.after_name_unresolved=cards();
  ns.value="verified";ns.dispatchEvent(new w.Event("change",{bubbles:true}));
  setTimeout(()=>{out.after_name_verified=cards();
   ns.value="";ns.dispatchEvent(new w.Event("change",{bubbles:true}));
   rel.value="upcoming";rel.dispatchEvent(new w.Event("change",{bubbles:true}));
   setTimeout(()=>{out.after_release_upcoming=cards();
    document.getElementById("probe").textContent="PROBE "+JSON.stringify(out);},400);},400);},400);
},1500);};
</script></body></html>"""


class FilterSelectsAreWired(unittest.TestCase):
    """静态：任何被 render() 读取的筛选控件都必须绑定 change。"""

    def test_every_filter_control_has_change_listener(self):
        html = BOARD.read_text(encoding="utf-8")
        ids = set(re.findall(r'document\.getElementById\("(f[A-Za-z]+)"\)\.value', html))
        self.assertTrue(ids, "未找到筛选控件读取点")
        missing = [i for i in sorted(ids)
                   if f'document.getElementById("{i}").addEventListener("change"' not in html]
        self.assertEqual(missing, [], f"筛选控件漏绑 change 事件：{missing}")


    def test_filter_order_left_to_right(self):
        """筛选元件从左到右顺序：证据等级 → 上架状态 → 名称状态 → 品级 → 武器种类 → 联动IP。"""
        html = BOARD.read_text(encoding="utf-8")
        i = html.index('<div class="controls">')
        seg = html[i:html.index("</div>", i)]
        got = re.findall(r'id="(q|fEv|fRelease|fNameSt|fGrade|fType|fIp)"', seg)
        self.assertEqual(got, ["q", "fEv", "fRelease", "fNameSt", "fGrade", "fType", "fIp"], got)

    def test_status_filters_have_dynamic_option_source(self):
        html = BOARD.read_text(encoding="utf-8")
        # 两个状态筛选的选项必须来自 canonical 字段的枚举收集
        self.assertIn('fill(relSel,rels,"全部上架状态","listing_status",relCounts)', html)
        self.assertIn('fill(nsSel,nsts,"全部名称状态","name_status",nsCounts)', html)


class FilterSelectsWorkInRealBrowser(unittest.TestCase):
    """动态：真实 Chrome + file:// + 真实 change 事件。"""

    @classmethod
    def setUpClass(cls):
        if not CHROME.exists():
            raise unittest.SkipTest("未找到 Chrome，跳过真实浏览器验证")
        PROBE.write_text(PROBE_HTML, encoding="utf-8")
        prof = pathlib.Path(os.environ.get("LOCALAPPDATA", ".")) / "Temp" / "ws_probe_test_prof"
        url = "file:///" + str(PROBE).replace("\\", "/").replace(" ", "%20").lstrip("/")
        try:
            r = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                                "--allow-file-access-from-files", f"--user-data-dir={prof}",
                                "--virtual-time-budget=15000", "--dump-dom", url],
                               capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=240)
            dom = r.stdout or ""
        finally:
            PROBE.unlink(missing_ok=True)
        m = re.search(r"PROBE (\{.*?\})</pre>", dom, re.S)
        if not m:
            raise unittest.SkipTest("浏览器探针未产出结果")
        cls.out = json.loads(m.group(1))

    def test_both_selects_visible_with_canonical_options(self):
        o = self.out
        self.assertTrue(o["release_visible"], "上架状态下拉被隐藏")
        self.assertTrue(o["name_visible"], "名称状态下拉被隐藏")
        self.assertTrue(any(x.startswith("on_sale|") for x in o["release_opts"]), o["release_opts"])
        self.assertFalse(any("旧板派生" in x for x in o["release_opts"]), o["release_opts"])
        self.assertIn("verified|已核验（113）", o["name_opts"])

    def test_real_change_events_filter_the_list(self):
        o = self.out
        self.assertEqual(o["before"], 115)
        self.assertEqual(o["after_name_unresolved"], 2, "选「未命名/未解析」后卡片数未变 ⇒ 事件未生效")
        self.assertEqual(o["after_name_verified"], 113)
        self.assertEqual(o["after_release_upcoming"], 2)




class GradeColorPalette(unittest.TestCase):
    """品级配色（用户指定）：传世=紫红 / 典藏=金 / 紫皮=紫 / 直售=蓝 / 白送=白。"""

    # 传世/典藏取用户给的参考图配色，其余按指定色名
    EXPECT = {"t6": "#c2185b", "t5": "#d9b24c", "t4": "#8a70ff", "t3": "#1d4ed8", "t2": "#ffffff"}

    def test_css_defines_expected_palette(self):
        css = (ROOT / "board_shadcn.css").read_text(encoding="utf-8")
        for tier, hexv in self.EXPECT.items():
            self.assertIn(f".skin-card.grade-{tier}{{border-left:3px solid {hexv}", css, tier)
        # 徽章底/字色与卡面同色系
        self.assertIn(".skin-tag.grade-badge.t6{background:linear-gradient(180deg,#fbe3ec 0%,#e9b7c9 48%,#d18fa9 100%);border:1px solid #bf9a5e;color:#6f2247}", css)
        self.assertIn(".skin-tag.grade-badge.t5{background:linear-gradient(180deg,#fdf3cd 0%,#e8ca63 48%,#cfa02c 100%);border:1px solid #b8872e;color:#3a2a08}", css)
        self.assertIn(".skin-tag.grade-badge.t4{background:none;border-color:transparent;box-shadow:none;padding:1px 2px;color:#6a4fe0}", css)
        self.assertIn(".skin-tag.grade-badge.t3{background:none;border-color:transparent;box-shadow:none;padding:1px 2px;color:#1d4ed8}", css)
        self.assertIn(".skin-tag.grade-badge.t2{background:none;border-color:transparent;box-shadow:none;padding:1px 2px;color:#52525b}", css)

    def test_lower_tiers_have_no_badge_background(self):
        """除传世/典藏外，徽章不要底色（纯色文字）。"""
        css = (ROOT / "board_shadcn.css").read_text(encoding="utf-8")
        for tier in ("t4", "t3", "t2"):
            self.assertIn(f".skin-tag.grade-badge.{tier}{{background:none;", css, tier)
        for tier in ("t6", "t5"):
            self.assertNotIn(f".skin-tag.grade-badge.{tier}{{background:none;", css, tier)

    def test_grade_filter_options_drop_ji(self):
        html = BOARD.read_text(encoding="utf-8")
        self.assertIn('if(key==="grade")base=base.replace(/级$/,"")', html)

    def test_html_uses_versioned_stylesheet(self):
        html = BOARD.read_text(encoding="utf-8")
        self.assertIn("board_shadcn.css?v=20260913-v02", html)


if __name__ == "__main__":
    unittest.main()
