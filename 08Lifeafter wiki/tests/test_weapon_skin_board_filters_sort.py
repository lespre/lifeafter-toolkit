# -*- coding: utf-8 -*-
"""武器皮肤板：名称三级 / 变体聚合 / 独立筛选 / 三组排序 / 互不重置 —— 真跑前端逻辑。

用 Node VM 载入 board.html 内联脚本（DOM 桩）+ 注入真实板 JSON，驱动 render() 后断言
grid HTML 的卡片数与顺序；数据侧断言直接读板 JSON 与重建工具。
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_HTML = ROOT / "board.html"
CATALOG = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
CANDIDATES = ROOT / "data" / "boards" / "weapon_skin_static_candidates_v01.json"
TOOL = ROOT / "tools" / "rebuild_weapon_skin_catalog_current.py"

NODE_DRIVER = r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('board.html','utf8');
class El {
  constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.hidden=false;this.options=[];
    this.textContent='';this.innerHTML='';this.handlers={};this.className='';}
  append(...xs){this.children.push(...xs)} appendChild(x){this.append(x)}
  addEventListener(k,fn){this.handlers[k]=fn} setAttribute(k,v){this[k]=v}
  querySelector(){return new El()} querySelectorAll(){return []} after(){} remove(){}
}
const ids={};
const document={getElementById:id=>ids[id]||(ids[id]=new El()),createElement:()=>new El(),
  querySelector:()=>new El(),querySelectorAll:()=>[],addEventListener:()=>{},body:{classList:{add(){},remove(){}}}};
const ctx={document,window:{addEventListener(){},innerHeight:1000,scrollY:0},CSS:{escape:x=>x},
  URLSearchParams,location:{search:'?b=weapon_skin_sfx_text_sources'},console,setTimeout:(f)=>f()};
vm.createContext(ctx);
let code='';
for(const m of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) if(m[1].trim()) code+=m[1]+'\n';
// 桩不解析 HTML：用 innerHTML 里的 selected 选项模拟浏览器的默认选中
const syncSelects=()=>{
  for(const id of ['fEv','fGrade','fType','fIp','fRelease','fNameSt','fOrder']){
    const el=document.getElementById(id);
    const m=/<option value="([^"]*)" selected/.exec(el.innerHTML||'');
    el.value=m?m[1]:'';
  }
};
// 注入访问器：同一脚本作用域内才能拿到 let DATA / render / fillFilterSelects
code+=`
globalThis.__setData=d=>{DATA=d};
globalThis.__fill=()=>fillFilterSelects(DATA.items);
globalThis.__render=()=>render();
globalThis.__grid=()=>document.getElementById('grid').innerHTML;
globalThis.__sel=id=>document.getElementById(id);
`;
vm.runInContext(code,ctx);
const board=JSON.parse(fs.readFileSync('data/boards/weapon_skin_sfx_text_sources.json','utf8'));
ctx.__setData(board);
ctx.__fill();
syncSelects();
const sel=ctx.__sel;
const skins=()=>{const h=ctx.__grid();return [...h.matchAll(/class="skin-name">([^<]*)</g)].map(m=>m[1]);};
const idsOf=()=>{const h=ctx.__grid();return [...h.matchAll(/class="skin-id"[^>]*>皮肤ID (\d+)/g)].map(m=>Number(m[1]));};
const cards=()=>[...ctx.__grid().matchAll(/class="skin-card[" ]/g)].length;
const out={};
out.ok=true;
try {
  // 默认排序 = 皮肤 ID ↓
  ctx.__render();
  out.defaultSort=sel('fOrder').value;
  out.defaultOrder=idsOf();
  out.cardCount=cards();
  out.itemCount=board.items.length;
  out.mainsOnly=out.defaultOrder.every(id=>id<11100000);
  // 变体横幅：不应出现任何变体 id 作为顶层卡
  out.cardHeaderIds=idsOf();
  // 武器种类筛选
  sel('fType').value='霰弹枪'; ctx.__render(); out.typeCount=cards(); out.typeNames=skins().length;
  sel('fType').value='冷兵器'; ctx.__render(); out.meleeCount=cards();
  // 品级筛选（真实枚举）
  sel('fType').value=''; sel('fGrade').value='5典藏级'; ctx.__render(); out.gradeCount=cards();
  // 组合筛选
  sel('fType').value='霰弹枪'; ctx.__render(); out.comboCount=cards();
  // 排序切换不重置筛选
  sel('fOrder').value='id_asc'; ctx.__render();
  out.typeAfterSortChange=sel('fType').value; out.ascOrder=idsOf();
  // 筛选切换不重置排序
  sel('fType').value='冷兵器'; ctx.__render();
  out.sortAfterFilterChange=sel('fOrder').value;
  // 排序：上架时间
  sel('fType').value=''; sel('fOrder').value='sale_desc'; ctx.__render(); out.saleDescTop=idsOf().slice(0,3);
  sel('fOrder').value='sale_asc'; ctx.__render(); out.saleAscTop=idsOf().slice(0,3);
  // 名称状态筛选
  sel('fOrder').value='id_desc'; sel('fGrade').value=''; sel('fType').value='';
  sel('fNameSt').value='unresolved'; ctx.__render(); out.unresolvedNameCount=cards();
  sel('fNameSt').value='verified'; ctx.__render(); out.verifiedNameCount=cards();
  // 品级徽章与表现摘要（全量）
  sel('q').value=''; sel('fNameSt').value=''; ctx.__render();
  {
    const h=ctx.__grid();
    out.cards=cards();
    out.gradeClasses=[...new Set([...h.matchAll(/skin-card grade-([a-z0-9]+)/g)].map(m=>m[1]))].sort();
    const badges=[...h.matchAll(/grade-badge (t[0-9]|unknown)"[^>]*>([^<]*)</g)];
    out.badgeTotal=badges.length;
    out.badgeLabels=[...new Set(badges.map(m=>m[2]))].sort();
    out.perfCards=(h.match(/skin-tag perf-tag/g)||[]).length;
    out.perfDetails=(h.match(/<details class="perf">/g)||[]).length;
    out.noPerfCards=out.cards-out.perfCards;
    // 顺序：变体折叠块必须在特效详情之前、技术详情之前；特效详情在技术详情之前
    // 顺序在单卡内校验（见 sampleWithVariant.order）；全页顺序受排序影响，不做断言
    out.perfNote=(h.match(/不是皮肤正式名称/g)||[]).length;
  }
  // 单皮肤取样：传世级 / 无表现 / 含变体
  const oneOf=(q)=>{sel('q').value=q;ctx.__render();const h=ctx.__grid();
    const cls=(h.match(/skin-card grade-([a-z0-9]+)/)||[])[1];
    const lbl=(h.match(/grade-badge [a-z0-9]+"[^>]*>([^<]*)</)||[])[1];
    const perf=(h.match(/表现特性 (\d+) 项/)||[])[1]||null;
    const vv=(h.match(/<details class="vv"/)||[]).length;
    const iVv=h.indexOf('class="vv"'),iPerf=h.indexOf('<details class="perf">'),iTech=h.indexOf("技术详情 / 数据来源 / 审计信息");
    const order=(iVv>=0&&iPerf>=0&&iTech>=0)?(iVv<iPerf&&iPerf<iTech):null;
    return {cls,lbl,perf:perf?Number(perf):0,vv,order};};
  out.sampleT6=oneOf('1110115');   // 赤月晶魄（传世级，有表现）
  out.sampleT3NoPerf=oneOf('1110001'); // 鎏金锐魄（直售级，无表现）
  out.sampleWithVariant=oneOf('1110177'); // 极光剑（典藏级，1 个时限变体，多表现）
  sel('q').value='';
  // 搜索时限变体 ID → 定位主卡并高亮
  sel('fNameSt').value=''; sel('q').value='11101771'; ctx.__render();
  out.searchCards=cards(); out.searchHit=(ctx.__grid().match(/vv-hit/g)||[]).length;
  out.searchHasMain=/极光剑/.test(ctx.__grid());
  sel('q').value=''; ctx.__render();
} catch(e){ out.ok=false; out.error=String(e); }
console.log(JSON.stringify(out));
"""


CANDIDATE_DRIVER = r"""
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('board.html','utf8');
class El {
  constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.hidden=false;this.options=[];
    this.textContent='';this.innerHTML='';this.handlers={};this.className='';}
  append(...xs){this.children.push(...xs)} appendChild(x){this.append(x)}
  addEventListener(k,fn){this.handlers[k]=fn} setAttribute(k,v){this[k]=v}
  querySelector(){return new El()} querySelectorAll(){return []} after(){} remove(){}
}
const ids={};
const document={getElementById:id=>ids[id]||(ids[id]=new El()),createElement:()=>new El(),
  querySelector:()=>new El(),querySelectorAll:()=>[],addEventListener:()=>{},body:{classList:{add(){},remove(){}}}};
const ctx={document,window:{addEventListener(){},innerHeight:1000,scrollY:0},CSS:{escape:x=>x},
  URLSearchParams,location:{search:'?b=weapon_skin_static_candidates_v01'},console,setTimeout:(f)=>f()};
vm.createContext(ctx);
let code='';
for(const m of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) if(m[1].trim()) code+=m[1]+'\n';
code+=`
globalThis.__setData=d=>{DATA=d};
globalThis.__fill=()=>fillFilterSelects(DATA.items);
globalThis.__render=()=>render();
globalThis.__grid=()=>document.getElementById('grid').innerHTML;
globalThis.__sel=id=>document.getElementById(id);
`;
vm.runInContext(code,ctx);
ctx.__setData(JSON.parse(fs.readFileSync('data/boards/weapon_skin_static_candidates_v01.json','utf8')));
ctx.__fill();
const sel=ctx.__sel;
const cards=()=>[...ctx.__grid().matchAll(/<div class="skin-card/g)].length;
const topIds=()=>[...ctx.__grid().matchAll(/<div class="skin-id">([^<]*)<\/div>/g)].map(m=>m[1]);
const out={ok:true};
try{
  sel('fOrder').value='id'; if(sel('fDir'))sel('fDir').dataset.dir='desc'; sel('fType').value=''; sel('fGrade').value='';
  ctx.__render();
  out.cards=cards(); out.topIds=topIds().slice(0,3);
  out.timedAtTop=topIds().filter(x=>/\d{8}/.test(x)).length;
  const h=ctx.__grid();
  out.variantBlocks=(h.match(/<details class="vv">/g)||[]).length;
  out.variantRows=(h.match(/class="vv-row"/g)||[]).length;
  out.auditGroups=(h.match(/class="vv-audit"/g)||[]).length;
  out.subCardsInVariants=/class="vv-row"[\s\S]{0,600}?class="skin-card/.test(h);
  out.timedKeys=JSON.parse(fs.readFileSync('data/boards/weapon_skin_static_candidates_v01.json','utf8'))
    .items.reduce((a,i)=>a.concat((i.timed_variants||[]).map(v=>v.skin_id)),[]);
  // 武器种类筛选
  sel('fType').value='霰弹枪'; ctx.__render(); out.typeCount=cards();
  // 品级 + 武器种类组合
  sel('fGrade').value='5典藏级'; ctx.__render(); out.comboCount=cards();
  out.comboKeepsType=sel('fType').value;
  // 切排列方向不清筛选
  if(sel('fDir'))sel('fDir').dataset.dir='asc'; ctx.__render();
  out.ascTop=topIds().slice(0,3); out.dirKeepsFilters=[sel('fType').value,sel('fGrade').value];
  if(sel('fDir'))sel('fDir').dataset.dir='desc'; ctx.__render(); out.descTop=topIds().slice(0,3);
  // 上架时间排列（先清筛选，保证样本量足够）
  sel('fType').value=''; sel('fGrade').value='';
  sel('fOrder').value='sale'; ctx.__render(); out.saleTopAll=topIds().slice(0,3);
  sel('fOrder').value='id'; ctx.__render(); out.idDescTopAll=topIds().slice(0,3);
  // 恢复「筛选 + 排列」并存，验证排列不清筛选
  sel('fOrder').value='sale'; sel('fType').value='霰弹枪'; sel('fGrade').value='5典藏级'; ctx.__render();
  out.saleTop=topIds().slice(0,3);
  out.saleKeepsFilters=[sel('fType').value,sel('fGrade').value];
  sel('fOrder').value='id'; sel('fType').value=''; sel('fGrade').value=''; ctx.__render();
  // 搜索时限变体 ID → 定位永久主卡 + 展开 + 高亮
  sel('q').value='11101771'; ctx.__render();
  out.searchCards=cards();
  out.searchOpen=(ctx.__grid().match(/<div class="skin-card[^"]*open/g)||[]).length;
  out.searchHit=(ctx.__grid().match(/vv-hit/g)||[]).length;
  out.searchName=(ctx.__grid().match(/class="skin-name">([^<]*)</)||[])[1]||null;
  sel('q').value=''; ctx.__render();
  out.defaultSortKey=sel('fOrder').value;
  out.defaultDir=sel('fDir')?sel('fDir').dataset.dir:null;
}catch(e){ out.ok=false; out.error=String(e); }
console.log(JSON.stringify(out));
"""


def run_driver(script: str = NODE_DRIVER) -> dict:
    done = subprocess.run(["node", "-e", script], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    if done.returncode != 0:
        raise AssertionError(f"node driver failed: {done.stderr or done.stdout}")
    return json.loads(done.stdout.strip().splitlines()[-1])


class WeaponSkinBoardUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.board = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
        cls.html = BOARD_HTML.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.drive = run_driver()

    # ── 名称三级 ──
    def test_candidate_names_survive_unresolved_identity(self):
        named = [i for i in self.candidates["items"] if i["candidate_name"]]
        self.assertTrue(named)
        for item in named:
            self.assertEqual(item["name_status"], "candidate")
            self.assertEqual(item["identity_status"], "unresolved")   # 身份未确认
            self.assertTrue(item["name_display"])                      # 名称未被清空
            self.assertFalse(item["verified_weapon_skin_identity"])

    def test_only_truly_nameless_show_unnamed_skin(self):
        for item in self.candidates["items"]:
            if item["name_status"] == "unresolved":
                self.assertIsNone(item["candidate_name"])
                self.assertEqual(item["name_display"], f"未命名皮肤 · ID {item['structural_record_key']}")
        previews = [i for i in self.board["items"] if i.get("name_status") == "unresolved"]
        self.assertTrue(all(i["name_display"].startswith("未命名皮肤 · ID ") for i in previews))

    # ── 变体聚合 ──
    def test_variants_are_never_top_level_cards(self):
        self.assertTrue(self.drive["mainsOnly"], "顶层卡必须全是永久主皮肤 ID")
        self.assertTrue(
            all(i < 11_100_000 for i in self.drive["cardHeaderIds"]),
            "顶层卡头不得出现时限变体 id",
        )
        self.assertEqual(self.drive["cardCount"], self.drive["itemCount"], "卡片数应等于顶层条目数")

    def test_timed_to_permanent_uses_floor_division(self):
        variants = [v for i in self.board["items"] for v in (i.get("variant_items") or [])]
        self.assertEqual(len(variants), 18)
        for v in variants:
            self.assertEqual(v["permanent_skin_id"], v["skin_id"] // 10)
            self.assertEqual(v["variant_type"], "timed")
            self.assertEqual(v["variant_relation_state"], "verified_runtime_rule")
            self.assertEqual(v["variant_relation_target_state"], "resolved")

    def test_timed_gate_is_interval_rule_not_parent_set(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import importlib.util

        spec = importlib.util.spec_from_file_location("wskin_rebuild", TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(module.is_timed_skin_id(11100041))
        self.assertTrue(module.is_timed_skin_id(11101831))
        self.assertFalse(module.is_timed_skin_id(1110004))
        self.assertFalse(module.is_timed_skin_id(1110190))
        body = module.is_timed_skin_id.__doc__ or ""
        self.assertIn("区间", body)
        # 门槛必须调用 is_timed_skin_id；不得由 parent_set 反推
        self.assertIn("is_timed_skin_id(k)", self.tool)
        self.assertNotIn("variant_ids = {k for k in parent_set if k > 9", self.tool)

    def test_timed_interval_bounds_match_runtime_evidence(self):
        """区间上下界必须与运行时模块只读核验到的字面量一致（不得漂移/不得靠样本反推）。"""
        import importlib.util

        spec = importlib.util.spec_from_file_location("wskin_rebuild_ev", TOOL)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        evidence = module.TIMED_SKIN_ID_EVIDENCE
        self.assertEqual(module.TIMED_SKIN_ID_MIN, evidence["literals_read"]["lower"])
        self.assertEqual(module.TIMED_SKIN_ID_MAX, evidence["literals_read"]["upper"])
        self.assertEqual(evidence["literals_read"]["lower"], 11_100_000)
        self.assertEqual(evidence["literals_read"]["upper"], 11_199_999)
        # 正式收口口径（用户 2026-09-11）：只记字面量与未决项，运算符不得声称已证
        self.assertEqual(evidence["runtime_lower_bound_literal"], 11_100_000)
        self.assertEqual(evidence["runtime_upper_bound_literal"], 11_199_999)
        self.assertEqual(evidence["exact_boundary_operators"], "opcode-level unresolved")
        board_notes = json.loads(CATALOG.read_text(encoding="utf-8"))["meta"]["notes"]
        self.assertIn("runtime lower-bound literal = 11,100,000", board_notes)
        self.assertIn("runtime upper-bound literal = 11,199,999", board_notes)
        self.assertIn("exact boundary operators = opcode-level unresolved", board_notes)
        self.assertEqual(evidence["literals_read"]["extra_conditions"], 0)
        self.assertIn("EquipSkinHelpers.py", evidence["definition"]["module"])
        self.assertEqual(evidence["definition"]["fid_current"], "A108220338E1AE9B")
        self.assertEqual(evidence["definition"]["entry_current"], 17364)
        self.assertIn("EquipSkinComp.py", evidence["consumers"][0]["module"])
        # 载体条目号/双包扫描范围必须写进证据（可复核）
        self.assertEqual(evidence["scan"]["entries_scanned"], 133245)

    def test_no_last_digit_threshold_anywhere(self):
        """末位数字只能出现在说明文字里；识别代码不得有末位门槛。"""
        self.assertIsNone(re.search(r"%\s*10\s*==", self.tool))
        code_lines = [
            line for line in self.tool.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        hit = [line for line in code_lines if "末位" in line and "is_timed_skin_id" not in line]
        # 注释/文档字符串可以解释"禁止末位"，可执行代码不行
        self.assertTrue(
            all('"""' in line or "禁止" in line or "不" in line for line in hit),
            f"识别代码里出现末位措辞：{hit[:3]}",
        )

    # ── 筛选 ──
    def test_weapon_type_filter(self):
        shotguns = [i for i in self.board["items"] if "霰弹枪" in str(i.get("weapon_type_label"))]
        self.assertEqual(self.drive["typeCount"], len(shotguns))
        self.assertTrue(self.drive["meleeCount"] > 0)

    def test_grade_filter(self):
        grade5 = [i for i in self.board["items"] if i.get("grade") == "5典藏级"]
        self.assertTrue(grade5)
        self.assertEqual(self.drive["gradeCount"], len(grade5))

    def test_combined_filters(self):
        combo = [
            i for i in self.board["items"]
            if "霰弹枪" in str(i.get("weapon_type_label")) and i.get("grade") == "5典藏级"
        ]
        self.assertTrue(combo, "霰弹枪+典藏级 至少应有一条")
        self.assertEqual(self.drive["comboCount"], len(combo))

    def test_name_status_filter(self):
        unresolved = [i for i in self.board["items"] if i.get("name_status") == "unresolved"]
        self.assertEqual(self.drive["unresolvedNameCount"], len(unresolved))
        self.assertEqual(self.drive["verifiedNameCount"], len([i for i in self.board["items"] if i.get("name_status") == "verified"]))

    # ── 排序 ──
    def test_default_sort_is_skin_id_desc_and_no_fake_catalog_order(self):
        self.assertEqual(self.drive["defaultSort"], "id")   # 排列依据=皮肤ID（方向由 fDir 控制，默认降序）
        order = self.drive["defaultOrder"]
        self.assertEqual(order, sorted(order, reverse=True))
        # 无可靠图鉴顺序字段 → 不提供伪造的「图鉴顺序」排序项，且在页面写明默认依据
        self.assertNotIn("排序：图鉴顺序", self.html)
        labels = re.findall(r"<option[^>]*>([^<]*)</option>", self.html)
        self.assertEqual([l for l in labels if "图鉴顺" in l], [], "不得提供伪造的图鉴顺序排序项")
        self.assertIn("无可靠图鉴顺序字段", self.html)

    def test_id_asc_sort(self):
        self.assertEqual(self.drive["ascOrder"], sorted(self.drive["ascOrder"]))

    def test_sale_time_sort(self):
        self.assertTrue(self.drive["saleDescTop"] and self.drive["saleAscTop"])
        self.assertNotEqual(self.drive["saleDescTop"], self.drive["saleAscTop"])
        ts = {i["skin_id"]: (i.get("sale_ts") or 0) for i in self.board["items"]}
        desc = [ts[i] for i in self.drive["saleDescTop"] if i in ts]
        self.assertEqual(desc, sorted(desc, reverse=True))

    def test_switching_sort_keeps_filters(self):
        self.assertEqual(self.drive["typeAfterSortChange"], "霰弹枪")

    def test_switching_filter_keeps_sort(self):
        self.assertEqual(self.drive["sortAfterFilterChange"], "id_asc")

    # ── 搜索与中文面 ──
    def test_search_timed_variant_locates_main_card(self):
        self.assertEqual(self.drive["searchCards"], 1)
        self.assertTrue(self.drive["searchHasMain"], "应定位到主卡极光剑")
        self.assertGreaterEqual(self.drive["searchHit"], 1, "命中变体应高亮")

    def test_player_visible_area_has_no_english_internals(self):
        face = self.html
        for banned in ("FID", "payload_sha", "schema_ref", "source_state", "identity_status"):
            self.assertNotIn(f'>{banned}<', face)
        for label in ("身份状态", "变体关系状态", "永久皮肤ID", "上架时间", "上架状态"):
            self.assertIn(label, face)


class WeaponSkinCardVisualTests(unittest.TestCase):
    """B 品级视觉分级 + C 表现摘要（纯展示，不改底层数据）。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.board = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.drive = run_driver()

    def test_every_card_has_grade_badge_with_real_tier(self):
        self.assertEqual(self.drive["cards"], len(self.board["items"]))
        self.assertEqual(self.drive["badgeTotal"], self.drive["cards"])
        # 展示短名（不带"级"）；数据枚举原值仍是 6传世级 / 5典藏级 …
        real = {"传世", "典藏", "紫皮", "直售", "白送"}
        seen = set(self.drive["badgeLabels"])
        self.assertTrue(seen & real, f"至少应出现真实品级：{seen}")
        self.assertTrue(seen - real <= {"品级未确认"},
                        f"非真实品级只能用中性标签「品级未确认」：{seen - real}")
        # 类名覆盖：真实层级 + unknown 中性
        for cls in ("t2", "t3", "t4", "t5", "t6", "unknown"):
            self.assertIn(cls, self.drive["gradeClasses"])

    def test_grade_tiers_come_from_snapshot_values_only(self):
        sys.path.insert(0, str(ROOT / "tools"))
        grades = {str(i.get("grade")) for i in self.board["items"] if i.get("grade")}
        self.assertTrue(grades <= {"6传世级", "5典藏级", "4紫皮级", "3直售级", "2白送级", "未配置"},
                        f"板内 grade 必须是真实枚举或未配置：{grades}")
        html = BOARD_HTML.read_text(encoding="utf-8")
        # 展示层用短名（不带"级"）
        for label in ("传世", "典藏", "紫皮", "直售", "白送"):
            self.assertIn(f'label:"{label}"', html)
        self.assertNotIn('label:"传世级"', html)
        # 未配置/未知 → 中性中文标签「品级未确认」（玩家面不露工程词）
        flat = html.replace(" ", "").replace("\n", "")
        self.assertIn('"品级未确认"', html)
        self.assertIn('["未配置","未知","无","未确认"].includes(raw)', flat)

    def test_perf_summary_present_only_when_data_exists(self):
        with_perf = [
            i for i in self.board["items"]
            if (i.get("combat_panel") or i.get("sfx_items") or i.get("behavior_resources"))
        ]
        self.assertEqual(self.drive["perfCards"], len(with_perf))
        self.assertEqual(self.drive["noPerfCards"], len(self.board["items"]) - len(with_perf))
        self.assertEqual(self.drive["perfDetails"], self.drive["perfCards"])

    def test_perf_detail_order_and_honest_note(self):
        self.assertTrue(self.drive["sampleWithVariant"]["order"], "单卡内顺序应为 时限变体 → 特效详情 → 技术详情")
        self.assertGreaterEqual(self.drive["perfNote"], self.drive["perfCards"], "每个特效详情都要带来源说明")

    def test_sample_skins(self):
        self.assertEqual(self.drive["sampleT6"]["lbl"], "传世")
        self.assertEqual(self.drive["sampleT6"]["cls"], "t6")
        self.assertGreater(self.drive["sampleT6"]["perf"], 0)
        self.assertEqual(self.drive["sampleT3NoPerf"]["lbl"], "直售")
        self.assertEqual(self.drive["sampleT3NoPerf"]["perf"], 0, "无表现数据不得硬显示")
        self.assertEqual(self.drive["sampleWithVariant"]["vv"], 1)
        self.assertGreater(self.drive["sampleWithVariant"]["perf"], 0)

    def test_perf_mapping_uses_real_field_names_and_categories(self):
        html = BOARD_HTML.read_text(encoding="utf-8")
        for field in ("fire_sfx_path", "hit_sfx_path", "extension_defeat_sfx", "trajectory_sfx_path"):
            self.assertIn(field, html)
        for cat in ("命中效果", "击败特效", "攻击弹道", "战斗音效", "核芯联动"):
            self.assertIn(cat, html)
        self.assertIn("其他表现", html)   # 无法可靠分类的兜底
        self.assertNotIn("珍藏", html)     # 不得出现数据里不存在的品级


class WeaponSkinAggregationAndSortTests(unittest.TestCase):
    """变体聚合（顶层只放永久主记录）+ 筛选/排列可用性：用户 2026-09-12 回归清单。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.cand = json.loads(CANDIDATES.read_text(encoding="utf-8"))
        cls.html = BOARD_HTML.read_text(encoding="utf-8")
        cls.tool = (ROOT / "tools" / "rebuild_weapon_skin_static_candidates_board.py").read_text(encoding="utf-8")
        cls.drive = run_driver(CANDIDATE_DRIVER)
        cls.drive_cat = run_driver()

    @staticmethod
    def _key(item):
        return item.get("skin_id") or item.get("structural_record_key")

    def test_driver_ran(self):
        self.assertTrue(self.drive.get("ok"), self.drive.get("error"))
        self.assertTrue(self.drive_cat.get("ok"), self.drive_cat.get("error"))

    # ── 1. 变体聚合 ──
    def test_timed_records_never_in_top_level_card_list(self):
        for board in (self.catalog, self.cand):
            keys = [self._key(i) for i in board["items"]]
            self.assertTrue(all(k < 11_100_000 for k in keys), f"顶层出现时限区间 ID: {keys}")
            self.assertTrue(all(i.get("variant_type") != "timed" for i in board["items"]))
        self.assertEqual(self.drive["timedAtTop"], 0)
        self.assertEqual([i for i in self.drive["topIds"] if re.search(r"\d{8}", i)], [])

    def test_one_top_level_card_per_permanent_skin(self):
        for board in (self.catalog, self.cand):
            keys = [self._key(i) for i in board["items"]]
            self.assertEqual(len(keys), len(set(keys)))

    def test_timed_variants_only_in_variants_list(self):
        timed = {}
        for item in self.cand["items"]:
            for v in (item.get("timed_variants") or []):
                self.assertNotIn(v["skin_id"], timed)
                timed[v["skin_id"]] = item["structural_record_key"]
                self.assertEqual(v["permanent_skin_id"], v["skin_id"] // 10)
                self.assertEqual(v["variant_type"], "timed")
                self.assertEqual(v["variant_relation_state"], "verified_runtime_rule")
                self.assertEqual(v["permanent_skin_id"], item["structural_record_key"])
        self.assertEqual(len(timed), 18)
        top = {self._key(i) for i in self.cand["items"]}
        self.assertFalse(set(timed) & top)
        self.assertEqual(sorted(timed), sorted(self.drive["timedKeys"]))

    def test_top_level_counts_exclude_timed_variants(self):
        stats = self.cand["stats"]
        self.assertEqual(stats["static_records"], 133)
        self.assertEqual(stats["top_level_records"], 115)
        self.assertEqual(stats["nested_timed_variant_rows"], 18)
        self.assertEqual(stats["timed_rows_at_top_level"], 0)
        self.assertEqual(len(self.cand["items"]), 115)
        grouping = self.cand["meta"]["player_view_grouping"]
        self.assertEqual(grouping["top_level"], "permanent_records_only")
        self.assertEqual(grouping["timed_rows_at_top_level"], 0)
        self.assertEqual(self.drive["cards"], 115)

    def test_candidate_cards_render_compact_variants_not_subcards(self):
        self.assertEqual(self.drive["variantBlocks"], 18)
        self.assertEqual(self.drive["variantRows"], 18)
        self.assertEqual(self.drive["auditGroups"], 18)
        self.assertFalse(self.drive["subCardsInVariants"], "变体行内不得出现完整子卡")
        # 变体行只保留期限 + 时限 ID（及其余真实差异），不重复父项名称/品级/武器种类
        self.assertIn("renderTimedVariants", self.html)
        self.assertIn("duration_label", self.html)

    def test_builder_groups_by_permanent_skin_id_with_invariants(self):
        self.assertIn("_group_timed_records", self.tool)
        self.assertIn("timed records leaked into top level", self.tool)
        self.assertIn("refusing top-level fallback", self.tool)
        self.assertIn("permanent_skin_id == key // 10", self.tool)

    # ── 2. 筛选可用性 ──
    def test_weapon_type_filter_effective(self):
        self.assertGreater(self.drive["typeCount"], 0)
        self.assertLess(self.drive["typeCount"], 115)
        self.assertGreater(self.drive_cat["typeCount"], 0)
        self.assertLess(self.drive_cat["typeCount"], 115)

    def test_grade_filter_effective(self):
        self.assertGreater(self.drive_cat["gradeCount"], 0)
        self.assertLess(self.drive_cat["gradeCount"], 115)
        levels = {i["static_fields"]["level"] for i in self.cand["items"] if i.get("static_fields")}
        self.assertTrue({2, 3, 4, 5, 6} & levels)

    def test_type_plus_grade_combo_effective(self):
        combo = self.drive["comboCount"]
        self.assertLessEqual(combo, self.drive["typeCount"])
        self.assertGreaterEqual(combo, 0)
        self.assertEqual(self.drive["comboKeepsType"], "霰弹枪")
        # 图鉴板：霰弹枪 + 典藏级 = 3（此前已核）
        self.assertEqual(self.drive_cat["comboCount"], 3)

    def test_name_status_filter_available(self):
        statuses = {i["name_status"] for i in self.cand["items"]}
        self.assertEqual(statuses, {"candidate", "unresolved"})
        self.assertIn('id="fNameSt"', self.html)

    # ── 3. 排列 ──
    def test_id_asc_desc_effective(self):
        asc, desc = self.drive["ascTop"], self.drive["descTop"]
        self.assertNotEqual(asc, desc)
        self.assertLess(asc[0], desc[0]) if asc and desc else None

    def test_sale_sort_effective(self):
        self.assertTrue(self.drive["saleTopAll"])
        self.assertNotEqual(self.drive["saleTopAll"], self.drive["idDescTopAll"],
                            "上架时间排列应与皮肤ID排列给出不同顺序")

    def test_no_catalog_order_field_and_default_is_id_desc(self):
        for board in (self.catalog, self.cand):
            blob = json.dumps(board, ensure_ascii=False)
            for field in ("catalog_order", "collection_order", "sort_order", "gallery_order"):
                self.assertNotIn(field, blob, f"发现图鉴顺序字段 {field}：需要提供图鉴顺序排列")
        self.assertEqual(self.drive["defaultSortKey"], "id")
        self.assertEqual(self.drive["defaultDir"], "desc")
        self.assertIn('排列依据：皮肤 ID', self.html)
        self.assertIn('排列依据：上架时间', self.html)

    def test_catalog_order_options_absent_when_no_reliable_field(self):
        self.assertNotIn("图鉴顺序 ↑", self.html)
        self.assertNotIn("图鉴顺序 ↓", self.html)
        self.assertIn("无可靠图鉴顺序字段", self.html)

    # ── 4. 状态保持 ──
    def test_sort_does_not_clear_filters(self):
        self.assertEqual(self.drive["dirKeepsFilters"], ["霰弹枪", "5典藏级"])
        self.assertEqual(self.drive["saleKeepsFilters"], ["霰弹枪", "5典藏级"])
        self.assertEqual(self.drive_cat["typeAfterSortChange"], "霰弹枪")

    def test_filter_does_not_reset_sort(self):
        self.assertEqual(self.drive_cat["sortAfterFilterChange"], "id_asc")

    # ── 5. 搜索时限变体 ──
    def test_search_timed_id_lands_on_permanent_card(self):
        self.assertEqual(self.drive["searchCards"], 1)
        self.assertEqual(self.drive["searchOpen"], 1)
        self.assertEqual(self.drive["searchHit"], 1)
        self.assertEqual(self.drive["searchName"], "极光剑")
        self.assertEqual(self.drive_cat["searchCards"], 1)
        self.assertEqual(self.drive_cat["searchHasMain"], True)

    def test_timed_variant_does_not_join_top_level_sorting(self):
        keys = [self._key(i) for i in self.cand["items"]]
        self.assertTrue(all(k < 11_100_000 for k in keys))
        self.assertNotIn("timed_variants", json.dumps(self.drive["topIds"], ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
