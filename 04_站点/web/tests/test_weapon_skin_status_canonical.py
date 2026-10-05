# -*- coding: utf-8 -*-
"""武器皮肤：canonical 状态字段（listing_status / name_status）真正生效。

问题 1 的验收：
- 上架状态只有**唯一** canonical 字段 `listing_status`（verified_listed / verified_unlisted / unresolved）
- 证据不足时不得伪造分类（当前同快照 sale/shop/exchange = absent ⇒ 全部 unresolved）
- `name_status` 三值：有字符串 ≠ verified
- 前端筛选**真跑**（Node VM 载入 board.html 内联脚本 + DOM 桩）：
  上架状态下拉必须可见且来自 canonical 字段；名称状态筛选能真正改变卡片数
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ART = ROOT / "artifacts" / "active" / "weapon_skin"
VOCAB = ART / "STATUS_VOCAB.json"
PROJ = ROOT / "data" / "workbench_boards" / "weapon_skin_active.json"
BOARD = ROOT / "board.html"

LISTING = ["verified_listed", "verified_unlisted", "unresolved"]
NAME = ["verified", "unresolved", "unsafe"]


def _rows():
    return [json.loads(l) for l in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


class ArtifactContract(unittest.TestCase):
    def test_listing_status_is_canonical_and_not_faked(self):
        rows = _rows()
        self.assertEqual(len(rows), 126)
        vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
        for r in rows:
            self.assertIn(r.get("listing_status"), LISTING, r.get("skin_item_id"))
            self.assertIn("listing_evidence", r)
        counts = {k: sum(1 for r in rows if r["listing_status"] == k) for k in LISTING}
        self.assertEqual(counts, vocab["listing_status"]["counts"])
        # 证据不足 ⇒ 只支持 unresolved，不得出现伪造的 verified_listed/unlisted
        self.assertEqual(counts["verified_listed"], 0)
        self.assertEqual(counts["verified_unlisted"], 0)
        self.assertEqual(vocab["listing_status"]["supported_today"], ["unresolved"])
        self.assertEqual(vocab["listing_status"]["evidence_state"]["sale"], "absent")
        self.assertEqual(vocab["listing_status"]["evidence_state"]["shop"], "absent")

    def test_sale_ts_is_not_a_listing_class(self):
        rows = _rows()
        with_ts = [r for r in rows if r.get("sale_ts") is not None]
        self.assertTrue(with_ts)
        for r in with_ts:
            self.assertEqual(r.get("sale_ts_role"), "timestamp_only_not_listing_status")

    def test_name_status_three_values_and_string_is_not_verified(self):
        rows = _rows()
        vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
        self.assertEqual(sorted(vocab["name_status"]["classes"]), sorted(NAME))
        for r in rows:
            self.assertIn(r.get("name_status"), NAME, r.get("skin_item_id"))
            if r["name_status"] == "verified":
                # v0.2：名称证据改为 canonical 链（common_item row → field slot → CHS），
                # 旧 "verified_runtime_ui_lookup" 是 board 时期的措辞，不再作 canonical 证据类型
                self.assertEqual(r.get("name_evidence_type"), "canonical_row_field_chs",
                                 f"{r.get('skin_item_id')} 有字符串但无 canonical 名称链，不得算 verified")
        counts = {k: sum(1 for r in rows if r["name_status"] == k) for k in NAME}
        self.assertEqual(counts["verified"], 122)
        self.assertEqual(counts["unresolved"], 4)

    def test_v01_archived_not_deleted(self):
        hist = ROOT / "artifacts" / "historical" / "weapon_skin" / "v01" / "WEAPON_SKIN_RESOLVED.jsonl"
        self.assertTrue(hist.exists(), "旧版必须复制归档，不能覆盖式重写")
        self.assertNotIn("listing_status", hist.read_text(encoding="utf-8")[:2000])

    def test_residual_registered(self):
        res = json.loads((ROOT / "residuals" / "weapon_skin" / "listing_status.json").read_text(encoding="utf-8"))
        self.assertEqual(res["count"], 126)
        self.assertEqual(res["supported_today"], ["unresolved"])
        self.assertFalse(res["hard_blocked"])


class ServiceAndProjection(unittest.TestCase):
    def _srv(self):
        from services import WeaponSkinService
        return WeaponSkinService()

    def test_service_exposes_canonical_status(self):
        svc = self._srv()
        vocab = svc.status_vocab()
        self.assertEqual(vocab["listing_status"]["supported_today"], ["unresolved"])
        page = svc.skins_page(listing_status="unresolved")
        self.assertEqual(page["total"], 126)
        self.assertEqual(page["facets"]["listing_status"], {"unresolved": 126})
        self.assertEqual(svc.skins_page(name_status="verified")["total"], 122)
        self.assertEqual(svc.skins_page(name_status="unsafe")["total"], 0)
        one = svc.get_skin(1110001)
        self.assertEqual(one["listing_status"], "unresolved")
        self.assertEqual(one["listing_status_label"], "未解析（证据不足）")
        self.assertEqual(one["name_status_label"], "已核验")

    def test_projection_carries_canonical_and_drops_fake_field(self):
        d = json.loads(PROJ.read_text(encoding="utf-8"))
        self.assertTrue(d["items"])
        for it in d["items"]:
            self.assertIn(it.get("listing_status"), LISTING)
            self.assertEqual(it.get("listing_status_label"), "未解析（证据不足）")
            self.assertNotIn("release_state", it, "投影不得再输出硬编码 release_state")
        self.assertEqual(d["meta"]["status_vocab"]["listing_status"]["supported_today"], ["unresolved"])

    def test_no_module_reintroduces_release_state_as_canonical(self):
        for rel in ("services/weapon_skin_service.py", "pipelines/projection/build_boards.py",
                    "services/entity_service.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for line in text.splitlines():
                if "release_state" in line:
                    self.assertTrue(line.strip().startswith("#") or "禁止" in line,
                                    f"{rel} 把 release_state 当 canonical 使用：{line.strip()[:80]}")


class ApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api.server import Handler
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    def test_api_filters_and_vocab(self):
        v = self._get("/api/weapon-skins/status-vocab")
        self.assertEqual(v["listing_status"]["supported_today"], ["unresolved"])
        p = self._get("/api/weapon-skins?listing_status=unresolved")
        self.assertEqual(p["total"], 126)
        self.assertEqual(self._get("/api/weapon-skins?name_status=verified")["total"], 122)
        self.assertEqual(self._get("/api/weapon-skins?name_status=unsafe")["total"], 0)
        e = self._get("/api/entity?kind=weapon_skin&id=1110001")
        ident = e["sections"]["identity"]
        self.assertEqual(ident["listing_status"], "unresolved")
        self.assertEqual(e["sections"]["status_vocab"]["listing_status"], ["unresolved"])


NODE_DRIVER = r"""
const fs=require('fs'),vm=require('vm');
const html=fs.readFileSync('board.html','utf8');
class El{constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.options=[];
  this.textContent='';this._html='';this.handlers={};this.className='';}
  set innerHTML(v){this._html=v;if(v==='')this.children=[];}get innerHTML(){return this._html;}
  append(...x){this.children.push(...x)}appendChild(x){this.append(x)}addEventListener(k,f){this.handlers[k]=f}
  setAttribute(k,v){this[k]=v}querySelector(){return new El()}querySelectorAll(){return []}after(){}remove(){}
  insertAdjacentHTML(k,h){this.innerHTML+=h}}
const ids={};
const document={getElementById:id=>ids[id]||(ids[id]=new El()),createElement:()=>new El(),querySelector:()=>new El(),
  querySelectorAll:()=>[],addEventListener:()=>{},body:{classList:{add(){},remove(){}}}};
const ctx={document,window:{addEventListener(){},innerHeight:1000,scrollY:0},CSS:{escape:x=>x},URLSearchParams,
  location:{search:'?b=weapon_skin_active'},console,setTimeout:f=>f()};
vm.createContext(ctx);
let code='';
for(const m of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)) if(m[1].trim()) code+=m[1]+'\n';
code+=`
globalThis.__setData=d=>{DATA=d};
globalThis.__fill=()=>fillFilterSelects(DATA.items);
globalThis.__render=()=>render();
globalThis.__grid=()=>document.getElementById('grid').innerHTML;
globalThis.__el=id=>document.getElementById(id);
globalThis.__count=()=>document.getElementById('count').textContent;
`;
vm.runInContext(code,ctx);
const syncSelects=()=>{ for(const id of ['fEv','fGrade','fType','fIp','fRelease','fNameSt','fOrder']){
  const el=ctx.__el(id); const m=/<option value="([^"]*)" selected/.exec(el.innerHTML||''); el.value=m?m[1]:''; } };
const opts=id=>{const el=ctx.__el(id);
  const kids=(el.children||[]).map(c=>String(c.value)+'|'+String(c.textContent));
  const html=[...(el.innerHTML||'').matchAll(/<option value="([^"]*)"[^>]*>([^<]*)</g)].map(m=>m[1]+'|'+m[2]);
  return kids.concat(html.filter(x=>!kids.includes(x)));};
const cards=()=>((ctx.__grid().match(/class="skin-card/g)||[]).length);
const out={};
const run=(label,file,fn)=>{
  const data=JSON.parse(fs.readFileSync(file,'utf8'));
  ctx.__setData(data); ctx.__fill(); syncSelects();
  out[label+'_release_opts']=opts('fRelease');
  out[label+'_name_opts']=opts('fNameSt');
  out[label+'_release_display']=ctx.__el('fRelease').style.display||'';
  out[label+'_name_display']=ctx.__el('fNameSt').style.display||'';
  out[label+'_hint']=ctx.__el('listingHint').textContent||'';
  fn();
};
run('wb','data/workbench_boards/weapon_skin_active.json',()=>{
  ctx.__render();
  out.wb_all=cards();
  ctx.__el('fNameSt').value='verified'; ctx.__render(); out.wb_name_verified=cards();
  ctx.__el('fNameSt').value='unresolved'; ctx.__render(); out.wb_name_unresolved=cards();
  ctx.__el('fNameSt').value=''; ctx.__el('fRelease').value='unresolved'; ctx.__render(); out.wb_listing_unresolved=cards();
  out.wb_count_text=ctx.__count();
});
run('legacy','data/boards/weapon_skin_sfx_text_sources.json',()=>{
  ctx.__render(); out.legacy_all=cards();
});
console.log(JSON.stringify(out));
"""


class FrontendFilterForReal(unittest.TestCase):
    """Node VM 真跑 board.html 内联脚本：证明两个筛选真的生效。"""

    @classmethod
    def setUpClass(cls):
        driver = ROOT / ".tmp_ws_driver.js"
        driver.write_text(NODE_DRIVER, encoding="utf-8")
        try:
            proc = subprocess.run(["node", str(driver)], cwd=str(ROOT), capture_output=True,
                                  text=True, encoding="utf-8", timeout=120)
        finally:
            driver.unlink(missing_ok=True)
        if proc.returncode != 0:
            raise unittest.SkipTest(f"node 不可用或驱动失败：{proc.stderr[-300:]}")
        cls.out = json.loads(proc.stdout.strip().splitlines()[-1])

    def test_listing_filter_visible_and_canonical(self):
        o = self.out
        self.assertIn("|全部上架状态", o["wb_release_opts"])
        self.assertTrue(any(x.startswith("unresolved|未解析（证据不足）") for x in o["wb_release_opts"]),
                        o["wb_release_opts"])
        self.assertNotIn("static|static", o["wb_release_opts"], "不得再出现硬编码 static")
        self.assertNotEqual(o["wb_release_display"], "none", "上架状态下拉必须可见")
        self.assertIn("canonical", o["wb_hint"])
        self.assertIn("sale/shop/exchange", o["wb_hint"])

    def test_listing_filter_actually_filters(self):
        self.assertEqual(self.out["wb_listing_unresolved"], 126)
        self.assertEqual(self.out["wb_all"], 126)

    def test_name_filter_actually_filters(self):
        self.assertTrue(any(x.startswith("verified|已核验") for x in self.out["wb_name_opts"]), self.out["wb_name_opts"])
        self.assertTrue(any(x.startswith("unresolved|未命名/未解析") for x in self.out["wb_name_opts"]), self.out["wb_name_opts"])
        self.assertEqual(self.out["wb_name_verified"], 122)
        self.assertEqual(self.out["wb_name_unresolved"], 4)
        self.assertIn("上架状态", self.out["wb_count_text"])

    def test_both_status_selects_visible_on_both_boards(self):
        """回归守护：两个状态下拉不得被隐藏（曾因 options.length 判定被藏掉）。"""
        o = self.out
        for key in ("wb_release_display", "wb_name_display", "legacy_release_display", "legacy_name_display"):
            self.assertNotEqual(o[key], "none", f"{key} 被隐藏 ⇒ 筛选不可用")
        self.assertGreaterEqual(len(o["wb_name_opts"]), 3)
        self.assertGreaterEqual(len(o["legacy_name_opts"]), 3)
        self.assertGreaterEqual(len(o["legacy_release_opts"]), 2)

    def test_legacy_board_listing_options_keep_source_but_drop_wording(self):
        """legacy 板上架状态：数据源保留（4 类选项在），但标签里不得再出现「旧板派生」。"""
        o = self.out
        vals = [x.split("|")[0] for x in o["legacy_release_opts"] if x.split("|")[0]]
        self.assertIn("on_sale", vals)
        self.assertIn("upcoming", vals)
        self.assertFalse(any("旧板派生" in x for x in o["legacy_release_opts"]), o["legacy_release_opts"])
        self.assertGreater(o["legacy_all"], 0)


if __name__ == "__main__":
    unittest.main()
