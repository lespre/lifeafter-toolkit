"""Small, source-only front-end regressions: no NPK reads or rebuilds."""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class FrontendUsabilityTests(unittest.TestCase):
    def test_home_navigation_and_policy_statistics(self):
        code = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('wiki.html','utf8');
class El {
 constructor(){this.children=[];this.dataset={};this.style={};this.value='';this.hidden=false;this.textContent='';this.handlers={};}
 append(...xs){this.children.push(...xs)} appendChild(x){this.append(x)}
 addEventListener(k,fn){this.handlers[k]=fn} setAttribute(k,v){this[k]=v}
}
const ids={},groups={};
for(const m of html.matchAll(/data-wiki-group="([^"]+)"/g))groups[m[1]]=new El();
const document={getElementById:id=>ids[id]||(ids[id]=new El()),
 createElement:()=>new El(),querySelector:q=>q.startsWith('[data-wiki-group=')?groups[q.slice(18,-2)]:new El(),
 querySelectorAll:()=>[],addEventListener:()=>{}};
const policy=JSON.parse(fs.readFileSync('data/publication_policy.json','utf8'));
const ctx={document,window:{WIKI_PUBLICATION_POLICY:policy},CSS:{escape:x=>x},URLSearchParams,location:{search:''},console};
vm.createContext(ctx);vm.runInContext(fs.readFileSync('data/manifest.js','utf8'),ctx);
for(const m of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g))if(m[1].trim())vm.runInContext(m[1],ctx);
assert.match(ids.gen.textContent,/已隔离旧板块 8\b/,'retired/unpublished must not count as quarantined');
assert.match(html,/id="homeSearch"/,'home board search is missing');
assert.match(html,/id="categoryNav"/,'category navigation is missing');
assert(ids.homeSearch.handlers.input,'search input must be wired');
ids.homeSearch.value='绝不命中的搜索';ids.homeSearch.handlers.input();
assert.match(ids.searchStatus.textContent,/0/);
assert.equal(ids.homeEmpty.hidden,false);
ids.homeSearch.value='核芯';ids.homeSearch.handlers.input();
assert.equal(ids.homeEmpty.hidden,true);
const cards=Object.values(groups).flatMap(g=>g.children).filter(c=>c.className==='card published');
assert.equal(cards.length,ctx.window.WIKI_MANIFEST.boards.length,'all published boards retain a card');
assert.deepEqual(ids.categoryNav.children.map(x=>x.textContent.slice(0,1)),['零','一','二','三','四'],'navigation must follow published category order');
assert(cards.some(c=>!c.hidden)&&cards.some(c=>c.hidden),'query filters board cards');
ids.homeSearch.value='';ids.homeSearch.handlers.input();assert(cards.every(c=>!c.hidden));
console.log('HOME_USABILITY_OK cards='+cards.length);
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_board_keyboard_debounce_and_load_failure(self):
        code = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('board.html','utf8');
const script=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const els={};const el=id=>els[id]||(els[id]={style:{},textContent:'',innerHTML:'',value:'',setAttribute(k,v){this[k]=v;}});
let timer=null,events=[],loaded=false;
const ctx={window:{},location:{search:''},URLSearchParams,console,
 document:{getElementById:el,querySelector:()=>el('controls'),createElement:()=>({}),head:{appendChild(s){events.push(s)}}},
 setTimeout:fn=>{timer=fn;return 1},clearTimeout:()=>{timer=null}};
vm.createContext(ctx);vm.runInContext(script,ctx);
assert.match(html,/role="button" tabindex="0" aria-expanded="false"/,'expand headers must be keyboard accessible');
let detail={hidden:true};let head={parentElement:{querySelector:()=>detail},classList:{toggle(){}},setAttribute(k,v){this[k]=String(v)}};
let prevented=0;ctx.head=head;ctx.event={key:'Enter',preventDefault(){prevented++}};
vm.runInContext('onDetailKey(event,head)',ctx);assert.equal(detail.hidden,false);assert.equal(head['aria-expanded'],'true');assert.equal(prevented,1);
ctx.event.key=' ';vm.runInContext('onDetailKey(event,head)',ctx);assert.equal(detail.hidden,true);
vm.runInContext('var calls=0;render=()=>calls++;scheduleSearch({});scheduleSearch({})',ctx);assert.equal(ctx.calls,0);timer();assert.equal(ctx.calls,1);
vm.runInContext('scheduleSearch({isComposing:true})',ctx);assert.equal(ctx.calls,1);
ctx.cb=()=>{loaded=true};vm.runInContext('loadBoard("example",cb)',ctx);events.at(-1).onload();assert.equal(loaded,false);assert.match(el('title').textContent,/加载失败/);
vm.runInContext('loadBoard("example",cb)',ctx);events.at(-1).onerror();assert.match(el('notes').textContent,/刷新/);
console.log('BOARD_USABILITY_OK keyboard+debounce+malformed+missing');
'''
        result = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_filter_options_preserve_quotes_as_text(self):
        code = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('board.html','utf8');
const js=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const ctx={window:{},location:{search:''},URLSearchParams,document:{getElementById:()=>({}),createElement:()=>({}),querySelector:()=>({style:{}})}};
vm.createContext(ctx);vm.runInContext(js,ctx);
assert.equal(vm.runInContext('typeof fillOptions',ctx),'function');
ctx.sel={children:[],innerHTML:'',appendChild(x){this.children.push(x)}};
ctx.values=['a"b','<img src=x>','单引号\'测试'];
vm.runInContext('fillOptions(sel,new Set(values),"全部品级")',ctx);
assert.equal(ctx.sel.children.length,4);
ctx.values.forEach((v,i)=>{assert.equal(ctx.sel.children[i+1].value,v);assert.equal(ctx.sel.children[i+1].textContent,v)});
assert.equal(ctx.sel.innerHTML,'');
console.log('SAFE_OPTIONS_OK quotes+markup+label');
'''
        r = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_skin_summary_is_keyboard_toggle(self):
        code = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('board.html','utf8');
const js=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const ctx={window:{},location:{search:''},URLSearchParams,document:{getElementById:()=>({})}};
vm.createContext(ctx);vm.runInContext(js,ctx);
const card=vm.runInContext('renderSkinCard({id:1,name:"测试",catalog_layer:"current_parent"})',ctx);
assert.match(card,/class="skin-summary" role="button" tabindex="0" aria-expanded="false"/);
assert.match(card,/class="skin-detail" hidden/);
const detail={hidden:true};let open=false,prevented=0;
const head={setAttribute(k,v){this[k]=v},parentElement:{querySelector:()=>detail,classList:{toggle(k,v){open=v}}}};
ctx.head=head;ctx.event={key:'Enter',preventDefault(){prevented++}};
vm.runInContext('onSkinKey(event,head)',ctx);assert.equal(detail.hidden,false);assert.equal(open,true);assert.equal(head['aria-expanded'],'true');
ctx.event.key=' ';vm.runInContext('onSkinKey(event,head)',ctx);assert.equal(detail.hidden,true);assert.equal(open,false);assert.equal(prevented,2);
console.log('SKIN_KEYBOARD_OK summary-only+Enter+Space+aria');
'''
        r = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_narrow_layout_overrides_fixed_minimums(self):
        css = (ROOT / 'board_shadcn.css').read_text(encoding='utf-8')
        self.assertIn('grid-template-columns:repeat(auto-fill', css)
        self.assertIn('input{min-width:260px', css)
        self.assertIn('outline-offset', css)

    def test_v01_status_badges_are_visible_in_normal_and_huge_boards(self):
        html = (ROOT / 'board.html').read_text(encoding='utf-8')
        css = (ROOT / 'board_shadcn.css').read_text(encoding='utf-8')
        for label in ('verified', 'unresolved', 'quarantined', 'static config', 'runtime final unknown'):
            self.assertIn(label, html)
        self.assertIn('function renderStateTags', html)
        self.assertIn('it.search_text||""', html)
        self.assertIn('renderStateTags(it.status_tags)', html)
        for cls in ('verified', 'unresolved', 'quarantined', 'static-config', 'runtime-final-unknown'):
            self.assertIn(f'.state-tag.{cls}', css)

class WeaponSkinBoardSortControls(unittest.TestCase):
    """武器皮肤图鉴排序控件：必须存在，且默认=上架时间 ↓（新在前）——用户 2026-09-11 指令。"""

    def test_sort_options_and_desc_default(self):
        """排序菜单只保留三组（图鉴顺序 / 皮肤ID / 上架时间）；本快照无图鉴顺序字段 → 默认皮肤 ID ↓。"""
        html = (ROOT / "board.html").read_text(encoding="utf-8")
        # 排列 = 排列依据（皮肤ID / 上架时间）+ 独立方向按钮（↑/↓），不再是一个大排序菜单
        for value, label in (
            ("id", "排列依据：皮肤 ID"),
            ("sale", "排列依据：上架时间"),
        ):
            self.assertIn('value="%s"' % value, html)
            self.assertIn(label, html)
        self.assertIn('<option value="id" selected>', html)          # 默认依据 = 皮肤 ID
        self.assertIn('id="fDir"', html)                              # 方向按钮
        self.assertIn("无可靠图鉴顺序字段", html)                      # 无可靠图鉴顺序不伪造
        # 不得再有名称/品级/武器类型等塞进排序菜单
        # 注：兜底分支（非皮肤板）保留「排序：游戏图鉴序列」，不在此列
        for banned in ("排序：名称", "排序：品级（高→低）", "排序：武器类型"):
            self.assertNotIn(banned, html)
        # 上架状态要在卡面可读（中文化映射）
        self.assertIn("RELEASE_CN", html)
        self.assertIn("上架状态", html)


if __name__ == '__main__':
    unittest.main()
