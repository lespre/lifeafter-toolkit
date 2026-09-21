# -*- coding: utf-8 -*-
"""「皮肤音效」区块守护（用户 2026-09-13 口径）。

要求：
  1) 与「时限变体」「特效与战斗表现」同级（details.audio），渲染顺序放在两者之后
  2) 绑定 34 卡：第一批 8 卡 + 第二批 24 卡（典藏/传世扩皮）+ 第三波 2 卡（极狐破坏者/焚古龙息，听辨收窄）
  3) 音频资产必须在 assets/audio/weapon_skin/<dir>/ 下真实存在（共 386 条引用）
  4) 升格口径：id 大→小 = 三/二/一阶；一阶、二阶音效相同；_1/lv1 一阶、_3/lv3 三阶
  5) 械骨人（种族）不得混入；「待确认」项 = 6（水晶玫瑰蓄力循环分层 ×3 卡 ×2）
  6) 多套音频皮肤（紫焰蛇矛）用组级目录 dir；未认领皮肤必须留档于 BATCH2_MATCH.json
  7) 真实 Chrome（headless + file:// + iframe）实测：32 块、逐块计数一致
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
CSS = ROOT / "board_shadcn.css"
ATT_JS = ROOT / "data/weapon_skin_audio_attachments.js"
ATT = ROOT / "data/weapon_skin_audio_attachments.json"
AUDIO = ROOT / "assets/audio/weapon_skin"
CHROME = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PROBE = ROOT / "_audio_probe_test.html"

EXPECTED = {
    # 第一批（听辨标注）
    "1110171": 15, "1110169": 14, "1110142": 9, "1110143": 9,
    "1110144": 10, "1110173": 10, "1110174": 10, "1110175": 10,
    # 第二批（机械匹配 + 文件名标注）
    "1110013": 5, "1110021": 16, "1110022": 10, "1110024": 12,
    "1110031": 9, "1110032": 15, "1110036": 13,
    "1110115": 18, "1110116": 18, "1110117": 18,
    "1110121": 6, "1110137": 2, "1110128": 7, "1110129": 5,
    "1110131": 9, "1110132": 9, "1110133": 9,
    "1110145": 5, "1110146": 5, "1110151": 13, "1110152": 4,
    "1110159": 17, "1110160": 17, "1110161": 17,
    "1110165": 15, "1110177": 25,
}
TOTAL = 386
BLOCKS = 34

PROBE_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<pre id="probe">pending</pre>
<iframe id="fr" src="board.html?b=weapon_skin_sfx_text_sources" style="width:1400px;height:900px"></iframe>
<script>
const out={};const fr=document.getElementById("fr");
fr.onload=()=>{setTimeout(()=>{
 const d=fr.contentDocument;
 out.cards=d.querySelectorAll(".skin-card").length;
 const blocks=[...d.querySelectorAll("details.audio")];
 out.audio_blocks=blocks.length;
 out.summaries=blocks.map(b=>{const s=b.querySelector("summary");return s?s.textContent.trim():"";});
 out.rows=blocks.map(b=>b.querySelectorAll("li.audio-row").length);
 out.audio_elems=d.querySelectorAll("details.audio audio").length;
 out.dirs=blocks.map(b=>[...b.querySelectorAll("audio")].map(a=>(a.getAttribute("src")||"").split("/")[3])[0]||"");
 document.getElementById("probe").textContent="PROBE "+JSON.stringify(out);
},4000);};
</script></body></html>"""


def _items(rec):
    return [x for g in rec["groups"] for x in g["items"]]


class SkinAudioSection(unittest.TestCase):
    def test_section_same_level_and_after_perf(self):
        html = BOARD.read_text(encoding="utf-8")
        i = html.find("function renderSkinDetail(it)")
        j = html.find("function skinTypeTxt(it)", i)
        body = html[i:j]
        iv = body.find("parts.push(renderVariantItems(")
        ip = body.find("parts.push(perfDetail)")
        ia = body.find("parts.push(audioDetail)")
        self.assertGreater(iv, 0, "时限变体推送缺失")
        self.assertGreater(ip, iv, "表现详情应在时限变体之后")
        self.assertGreater(ia, ip, "皮肤音效应放在时限变体与特效与战斗表现之后")
        self.assertIn('details class="audio"', html)
        self.assertIn("function renderSkinAudio(", html)
        self.assertIn('data/weapon_skin_audio_attachments.js', html)
        self.assertIn('(g.dir||rec.dir)', html, "组级目录回退缺失")

    def test_attachments_schema_and_assets(self):
        data = json.loads(ATT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "weapon-skin-audio-attachments-v1")
        skins = data["skins"]
        self.assertEqual(set(skins), set(EXPECTED))
        total = 0
        for sid, rec in skins.items():
            items = _items(rec)
            self.assertEqual(len(items), EXPECTED[sid], sid)
            total += len(items)
            for g in rec["groups"]:
                d = AUDIO / (g.get("dir") or rec["dir"])
                for x in g["items"]:
                    self.assertTrue((d / x["file"]).exists(), f"{sid}:{x['file']} 缺失")
        self.assertEqual(total, TOTAL)

    def test_stage_rules_and_exclusions(self):
        skins = json.loads(ATT.read_text(encoding="utf-8"))["skins"]
        def files(sid):
            return {x["file"] for x in _items(skins[sid])}
        # 第一批：金乌 / 水晶玫瑰（沿用原口径）
        j1, j2, j3 = files("1110142"), files("1110143"), files("1110144")
        self.assertEqual(j1, j2, "金乌：一阶、二阶音效应相同")
        self.assertTrue(any("_1." in f for f in j1))
        self.assertFalse(any("_3." in f for f in j1), "_3 文件不得出现在一阶/二阶卡")
        self.assertTrue(any("_3." in f for f in j3))
        m1, m2, m3 = files("1110173"), files("1110174"), files("1110175")
        self.assertEqual(m1, m2, "水晶玫瑰：一阶、二阶音效应相同")
        self.assertTrue(any("lv1" in f for f in m1))
        self.assertFalse(any("lv3" in f for f in m1), "lv3 文件不得出现在一阶/二阶卡")
        self.assertTrue(any("lv3" in f for f in m3))
        # 第二批三阶皮：按各自阶段标记校验
        for a, b, c, tag, tok1, tok3 in (
                ("1110115", "1110116", "1110117", "赤月晶魄", "lv1_atk", "lv3_atk"),
                ("1110131", "1110132", "1110133", "炽日耀斑", "shoot_lv1", "shoot_lv3"),
                ("1110159", "1110160", "1110161", "沙海月鸣", "lv1", "lv3")):
            f1, f2, f3 = files(a), files(b), files(c)
            self.assertEqual(f1, f2, f"{tag}：一阶、二阶音效应相同")
            self.assertTrue(any(tok1 in f for f in f1), tag)
            self.assertFalse(any(tok3 in f for f in f1), f"{tag}: 三阶文件不得出现在一阶/二阶卡")
            self.assertTrue(any(tok3 in f for f in f3), tag)
            self.assertFalse(any(tok1 in f for f in f3), f"{tag}: 一阶文件不得出现在三阶卡")
        self.assertTrue(any("1006_008_bp" in f for f in files("1110131")))
        self.assertTrue(any("1006_010_jibai" in f for f in files("1110133")))
        self.assertNotIn("bxr", ATT_JS.read_text(encoding="utf-8"), "械骨人（种族）不得混入")
        pend = [x for rec in skins.values() for g in rec["groups"] for x in g["items"] if x.get("pending")]
        self.assertEqual(len(pend), 6)
        for sid in ("1110173", "1110174", "1110175"):
            self.assertEqual(len([x for g in skins[sid]["groups"] for x in g["items"] if x.get("pending")]), 2)

    def test_multi_set_skin_and_unresolved_ledger(self):
        data = json.loads(ATT.read_text(encoding="utf-8"))
        zs = data["skins"]["1110021"]
        dirs = [g.get("dir") for g in zs["groups"]]
        self.assertEqual(dirs, ["huojianqiang", "core_660067", "weapon_2003_05"])
        bm = json.loads((ROOT / "artifacts/active/weapon_skin_audio/BATCH2_MATCH.json").read_text(encoding="utf-8"))
        unres = {u.get("skin_id") for u in bm["unresolved"]}
        self.assertIn("1110121", unres, "极狐破坏者候选须留档")
        self.assertEqual(data["skins"]["1110121"]["verified"], "user_listening(2026-09-13)")
        self.assertTrue((ROOT / "artifacts/active/weapon_skin_audio/SCAN_ROUND2_REPORT.json").exists())
        self.assertIn("1110137", unres, "焚古龙息须留档")
        self.assertEqual(data["skins"]["1110137"]["evidence"], "batch_inference_unverified")
        self.assertEqual(bm["counts"]["total_cards_with_audio"], BLOCKS)
        self.assertEqual(bm["counts"]["total_items"], TOTAL)

    def test_css_and_whitelist(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("details.audio", css)
        self.assertIn("li.audio-row", css)
        html = BOARD.read_text(encoding="utf-8")
        self.assertIn("audio-row)", html, "dropEmptySections 白名单缺 audio-row")

    def test_browser_counts(self):
        if not CHROME.exists():
            self.skipTest("无 Chrome")
        PROBE.write_text(PROBE_HTML, encoding="utf-8")
        r = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                            "--virtual-time-budget=40000", "--dump-dom",
                            "file:///" + str(PROBE).replace("\\", "/")],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        m = re.search(r"PROBE (\{.*?\})</pre>", r.stdout or "", re.S)
        self.assertIsNotNone(m, "未取到 PROBE 结果")
        out = json.loads(m.group(1))
        self.assertGreater(out["cards"], 50)
        self.assertEqual(out["audio_blocks"], BLOCKS, "皮肤音效区块数不符")
        self.assertEqual(sorted(out["rows"]), sorted(EXPECTED.values()), "逐块条数与预期不符")
        self.assertEqual(out["audio_elems"], TOTAL)
        for s, n in zip(out["summaries"], out["rows"]):
            self.assertRegex(s, r"^皮肤音效 \d+ 条$")
            self.assertEqual(int(re.search(r"(\d+)", s).group(1)), n, "计数与行数不一致")
        from collections import Counter
        self.assertEqual(Counter(out["dirs"]), {
            "shuijinmeigui": 3, "jinwu": 3, "yongtandiao": 1, "huisexieyi": 1,
            "diancang_shotgun": 1, "huojianqiang": 1, "snake_bow": 1, "snake_shotgun": 1,
            "aolie": 1, "1013_003": 1, "bow_senlin": 1, "dajian": 3, "hammer": 1,
            "ice_416": 1, "taiyangzhizi": 3, "ar_horse": 1, "rifle_icedragon": 1,
            "alys": 1, "linglong_launcher": 1, "shym": 3, "shotgun_myql": 1, "jg": 1, "pistol_2.5": 1, "flame": 1})


if __name__ == "__main__":
    unittest.main()
