# -*- coding: utf-8 -*-
"""游戏富文本染色（richText）回归护栏。

真实数据里的 token 形态（2026-09-12 从 boards 统计）：
``#cRRGGBB``(6位) / ``#n`` 复位 / ``#r`` 换行 / ``#f(N)`` 色号 / ``#p(路径)`` 内联图片 / ``#H(..)`` 分段 / 其它 ``#x`` 控制码。
关键不变量：**渲染结果里不得残留任何控制码原文**（否则玩家会看到 #cffc8a4 这类字面量），
且 ``#r1.`` / ``#r2019年`` / ``#n(30天)`` 必须把后面的数字与括号当普通文本保留。
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_HTML = ROOT / "board.html"
DEFAULT_SOURCE = "weapon_skin_sfx_text_sources"

NODE_DRIVER = r"""
const fs=require('fs'),vm=require('vm');
class El{constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.hidden=false;this.options=[];
 this.textContent='';this.innerHTML='';this.handlers={};this.className='';}
 append(...x){this.children.push(...x)}appendChild(x){this.append(x)}addEventListener(k,f){this.handlers[k]=f}
 setAttribute(k,v){this[k]=v}querySelector(){return new El()}querySelectorAll(){return []}after(){}remove(){}}
const ids={};
const document={getElementById:i=>ids[i]||(ids[i]=new El()),createElement:()=>new El(),querySelector:()=>new El(),
 querySelectorAll:()=>[],addEventListener:()=>{},body:{classList:{add(){},remove(){}}}};
const ctx={document,window:{addEventListener(){},innerHeight:900,scrollY:0},CSS:{escape:x=>x},URLSearchParams,
 location:{search:'?b=__BOARD__'},console,setTimeout:f=>f()};
vm.createContext(ctx);
let code='';
for(const m of fs.readFileSync('board.html','utf8').matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) if(m[1].trim()) code+=m[1]+'\n';
code+='globalThis.__rt=richText;globalThis.__isrt=isRichText;';
vm.runInContext(code,ctx);
const rt=ctx.__rt,isrt=ctx.__isrt;
const samples=[
 "#cffc8a4当前已升至最高阶段#n赤雷裂空斩碎干重夜，破月流光饮尽万壑霜。",
 "可通过装配武器,并在主界面#cffc8a4长按TAB#n呼出武器列表,使用#cffc8a4鼠标中键滚轮上下滑动#n快速切换武器",
 "获得：#r1.营地金库商人夏冬凉处购买（禁交易）#r2.在野外开启箱子有概率获得",
 "旧时代中在建筑物上常见贴纸。#r2019年春节活动中获得的道具",
 "#H(0.5)副手#f(5)使用手枪#n时，#f(5)增益#n：副手射击暴击时",
 "可在身份认证活动中领取上民补给#p(ui/zhutihuodong_v5/zhaixin/btn_chakan_hong_dis.png)",
 "纯度为#c21f45130%#n的冷却液混合物",
 "打开礼包后，获得#cffc8a4启航研究服-衣服#n(30天)*1。 #r#cffc8a4累计打开3次本礼包#n",
 "#f(1249)「伤害抵御」#n 与 #f(5)火力提升至{0}#n",
 "#cffffff【使用方式】#r蘑菇会释放特殊的泡泡包裹住你！",
];
const out={samples:[],detect:{}};
for(const s of samples){
  const html=rt(s), plain=html.replace(/<[^>]*>/g,'');
  out.samples.push({in:s, plain:plain, html:html,
    leak: /#(c[0-9a-fA-F]{6}|n\b|r\b|f\(|p\(|H\()/.test(plain)});
}
out.detect={rich:isrt(samples[0]),plain:isrt('普通文本，没有控制码'),picture:isrt('#p(a.png)'),varOnly:isrt('火力提升至 {0}')};
// 事件：真实板数据里所有富文本字段都必须无泄漏
const board=JSON.parse(fs.readFileSync('data/boards/__BOARD__.json','utf8'));
const chk=[];
const walk=(v,path)=>{ if(typeof v==='string'){ if(isrt(v)){ const plain=rt(v).replace(/<[^>]*>/g,'');
    if(/#(c[0-9a-fA-F]{6}|n\b|r\b|f\(|p\(|H\()/.test(plain)) chk.push(path); } }
  else if(Array.isArray(v)) v.forEach((x,i)=>walk(x,path+'['+i+']'));
  else if(v&&typeof v==='object') Object.entries(v).forEach(([k,x])=>walk(x,path+'.'+k)); };
walk(board.items,'items');
out.boardLeaks=chk.slice(0,5);
out.boardChecked=board.items.length;
console.log(JSON.stringify(out));
"""


def run_driver(board: str = DEFAULT_SOURCE) -> dict:
    script = NODE_DRIVER.replace("__BOARD__", board)
    done = subprocess.run(["node", "-e", script], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    if done.returncode != 0:
        raise AssertionError(f"node driver failed: {done.stderr or done.stdout}")
    return json.loads(done.stdout.strip().splitlines()[-1])


class RichTextRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = BOARD_HTML.read_text(encoding="utf-8")
        cls.out = run_driver()

    def test_no_control_code_leaks_in_samples(self):
        leaks = [s["in"] for s in self.out["samples"] if s["leak"]]
        self.assertEqual(leaks, [], f"渲染后仍残留控制码：{leaks}")

    def test_user_reported_example_colors_then_resets(self):
        s = self.out["samples"][0]
        self.assertIn("当前已升至最高阶段", s["plain"])
        self.assertIn("赤雷裂空斩碎干重夜，破月流光饮尽万壑霜。", s["plain"])
        self.assertIn('color:#ffc8a4', s["html"])
        # 复位后回到默认色（新的 .rt span，不带 style）
        self.assertIn('</span><span class="rt">赤雷裂空斩', s["html"])

    def test_newline_keeps_following_digits_and_parens(self):
        joined = " ".join(s["plain"] for s in self.out["samples"])
        self.assertIn("1.营地金库商人夏冬凉处购买", joined)
        self.assertIn("2019年春节活动", joined)
        self.assertIn("(30天)*1", joined)

    def test_picture_token_becomes_placeholder_with_path_only_in_title(self):
        pic = next(s for s in self.out["samples"] if "utihuodong" in s["in"])
        self.assertIn("［图片］", pic["plain"])
        self.assertNotIn(".png", pic["plain"])
        self.assertIn("btn_chakan_hong_dis.png", pic["html"])   # 路径只在 title

    def test_unknown_color_id_falls_back_without_leak(self):
        s = next(x for x in self.out["samples"] if "1249" in x["in"])
        self.assertNotIn("1249", s["plain"])
        self.assertIn("color:inherit", s["html"])

    def test_detection_helper(self):
        d = self.out["detect"]
        self.assertTrue(d["rich"] and d["picture"])
        self.assertFalse(d["plain"])
        self.assertFalse(d["varOnly"], "纯 {0} 变量不该被当富文本")

    def test_no_leak_across_published_boards(self):
        # 覆盖图鉴板 + 候选板（两块都有大量富文本字段）
        for board in (DEFAULT_SOURCE, "weapon_skin_static_candidates_v01"):
            out = self.out if board == DEFAULT_SOURCE else run_driver(board)
            self.assertEqual(out["boardLeaks"], [], f"{board} 存在残留控制码：{out['boardLeaks']}")
            self.assertGreater(out["boardChecked"], 0)

    def test_skin_detail_routes_official_desc_through_richtext(self):
        self.assertIn("isRichText(it.official_desc)?richText(it.official_desc)", self.html.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
