/* board.html 主渲染逻辑（从 board.html 内联 <script> 拆出，2026-10-30）。
   依赖：assets/board_dict.js（字典）须先加载。 */

// 通用板块渲染：board.html?b=<board文件名>，动态加载 data/boards/<b>.js

const FIXED=new Set(["id","name","evidence","source","evidence_level","provenance","text_provenance","sfx_items","timed_variants","timed_variant_count","weapon_type_inference","name_resolution","reference_fields","behavior_resources","field_provenance","variant_items","display_name","stats","variants","all_row_keys","schema_refs","text_provenance_note","weapon_type_label","weapon_type_code","rewards","pools","activity_pool_refs","status_tags","search_text","_media","scene_ids","server_types","source_kinds","row_keys","merged_rows"]);
const HUGE_TABLE_MIN=15000;
function buildHugeIndex(d){
  // 大表（如全道具总表 35986 行）：预构建轻量检索串，避免每次按键 JSON.stringify 全表。
  d._hay=(d.items||[]).map(it=>{
  const vids=(it.variant_items||[]).map(v=>`${v.skin_id} ${v.display_name||v.name||""}`).join(" ");
  return `${it.search_text||""} ${it.id} ${it.item_id??""} ${it.name||""} ${it.desc||""} ${it.icon||""} ${vids}`.toLowerCase();
});
}


const STATE_CLASS={verified:"verified",unresolved:"unresolved",quarantined:"quarantined","static config":"static-config","runtime final unknown":"runtime-final-unknown",unverified:"unverified"};
const esc=s=>String(s??"").replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
// 字段取值：优先顶层字段，其次 static_fields（候选板把 grade/weapon_type_label/sale_ts 放在 static_fields）。
// 两处都是同快照真实字段，只读取、不推断。
function pick(it,field){
  if(!it)return undefined;
  const v=it[field];
  if(v!==undefined&&v!==null&&v!=="")return v;
  const sf=it.static_fields;
  return sf?sf[field]:undefined;
}
function renderStateTags(tags){
  if(!Array.isArray(tags)||!tags.length)return "";
  return `<span class="state-tags">${tags.map(tag=>`<span class="state-tag ${STATE_CLASS[tag]||"unresolved"}">${esc(STATE_CN[tag]||COMMON_VAL_CN[tag]||tag)}</span>`).join("")}</span>`;
}
// 游戏富文本染色：#f(N) 色段 / #cRRGGBB / #r 换行 / #n 复位 / {0} 变量保留
// 色号为游戏文本近似映射（5=高亮金），可按实例校准

// 游戏富文本：单次扫描。token 表（按数据实测）：
//   #cRRGGBB 文字色(6位) | #n 复位 | #r 换行 | #f(N) 色号(1..10 有近似映射，其余继承) 
//   #p(路径) 内联图片 → 占位（本轮不做图片链，路径只进 title 便于审计）
//   #H(...) 分段指令 → 按换行渲染（具体度量未证，注释保留原文）
//   其它 #x / #x(..) / #xN 控制码 → 隐藏，不泄漏原文（title 保留）
// 注意：#r1 / #r2019年 / #n(30天) 都是「token + 普通文本」，不得吞掉后面的数字/括号。
const RT_TOKEN=/#(c[0-9a-fA-F]{6}|n|r|f\([^)]*\)|p\([^)]*\)|H\([^)]*\)|[A-Za-z](?:\([^)]{0,80}\)|\d{1,3})?)/g;
function richText(s){
  const t=esc(String(s??""));
  let out="",i=0,m;
  RT_TOKEN.lastIndex=0;
  while((m=RT_TOKEN.exec(t))!==null){
    out+=t.slice(i,m.index);
    const tok=m[1];
    if(tok.length===7&&tok[0]==="c"){out+=`</span><span class="rt" style="color:#${tok.slice(1)}">`;}
    else if(tok==="n"){out+='</span><span class="rt">';}
    else if(tok==="r"){out+="<br>";}
    else if(tok.startsWith("f(")){const id=tok.slice(2,-1);out+=`</span><span class="rt" style="color:${RT_COLORS[id]||"inherit"}">`;}
    else if(tok.startsWith("p(")){out+=`<span class="rt-img" title="${esc("图片：" + tok.slice(2,-1))}">［图片］</span>`;}
    else if(tok.startsWith("H(")){out+="<br>";}
    else {out+=`<span class="rt-ctl" title="${esc(tok)}"></span>`;}
    i=m.index+m[0].length;
  }
  out+=t.slice(i);
  return `<span class="rt">${out}</span>`;
}
function isRichText(v){return typeof v==="string"&&/#[A-Za-z]/.test(v)&&v.length<8000;}
function getParam(k){return new URLSearchParams(location.search).get(k);}
const initialQuery=getParam("q")||"";
const partFilter=(getParam("part")||"").split(",").map(s=>s.trim()).filter(Boolean);
// 必须与 wiki.html 卡面规则一致：卡名仅显示分类尾段，不泄露生成器内部板名。
/* 服别切换器：meta.server_branch = 当前服；meta.sibling_cards = ["<board_id>（<服名> · 数据卡）", …]
   有兄弟分服卡时在标题下渲染服别按钮组（当前服高亮，其余为跳转链接）。 */
function renderServerSwitch(m){
  const box=document.getElementById("serverSwitch");
  if(!box)return;
  const cur=String(m.server_branch||"").trim();
  const sibs=(m.sibling_cards||[]).map(s=>{
    const mm=String(s).match(/^([A-Za-z0-9_]+)（(.+?)）$/);
    if(!mm)return null;
    return {board:mm[1],label:mm[2].replace(/ · 数据卡$/,"").trim()};
  }).filter(x=>x&&x.board&&x.label);
  if(!cur&&sibs.length===0){box.style.display="none";return;}
  let html="<em>服别</em>";
  if(cur)html+=`<span class="srv-cur" title="当前分服子卡">${esc(cur)}</span>`;
  html+=sibs.map(x=>
    `<a class="srv-btn" href="?b=${encodeURIComponent(x.board)}" title="切换到 ${esc(x.label)} 子卡">${esc(x.label)}</a>`
  ).join("");
  box.innerHTML=html;
  box.style.display="flex";
}
function boardCardTitle(meta){  try{
    const bid=(new URLSearchParams(location.search)).get("b")||"";
    const t=(window.__BOARD_TITLES||{})[bid];
    const tag=String(meta?.name??"").startsWith("（内测版）")?"（内测版）":"";
    if(t) return tag+t;
  }catch(e){}
  const category=String(meta?.category??"").trim();
  const tail=category.split(" / ").pop().trim();
  const tag=String(meta?.name??"").startsWith("（内测版）")?"（内测版）":"";
  return tag+zhTitle(tail||String(meta?.name??"未命名板块").trim());
}
function wbProjectionIds(){
  const m=window.WIKI_WORKBENCH_MANIFEST;
  return new Set(((m&&m.projections)||[]).map(p=>p.projection_id));
}
// v1.3：大数据 Domain 默认 API-first（不加载几十 MB board.js）；离线全量必须显式 ?offline=1
const WB_API_FIRST={item_master_active:"",lottery_pool_active:"",lottery_rewards_active:""};
const WB_OFFLINE_LABEL="offline_full_projection（artifacts/active 派生，数十 MB）";
const WB_VIEW="wiki";  // Workbench 界面已下线（2026-10-22），只保留 Wiki View
function boardTitle(b){
  const m=window.WIKI_WORKBENCH_MANIFEST;
  const hit=((m&&m.projections)||[]).find(p=>p.projection_id===b);
  return (hit&&hit.domain)?("Workbench · "+hit.domain):String(b);
}
function wbApiFirst(b){
  return Object.prototype.hasOwnProperty.call(WB_API_FIRST,b)&&getParam("offline")!=="1";
}
function wbApiFirstNotice(b){
  const page=WB_API_FIRST[b];
  document.getElementById("title").textContent=boardTitle(b);
  document.querySelector(".controls").style.display="none";
  const n=document.getElementById("notes");n.style.display="block";
  n.innerHTML="此板块数据量较大（单页 ≤ 200 行），默认不做全量加载。"
   +"<div style=\"margin-top:6px\"><a href=\"?b="+encodeURIComponent(b)+"&offline=1\">→ 显式加载离线全量投影</a>"
   +" <span class=\"sub\">("+WB_OFFLINE_LABEL+")</span></div>";
  document.getElementById("grid").innerHTML='<div class="empty">未加载数据：大数据板块默认走 API，不做静默回退。</div>';
}
function loadBoard(b,cb){
  if(wbApiFirst(b)){wbApiFirstNotice(b);return;}   // API-first：不加载全量投影，也不静默回退 legacy board
  const s=document.createElement("script");
  // Workbench 模式：projection 存在则读 artifacts/active 派生数据；否则回落 legacy board（兼容，未删除）
  s.src=wbProjectionIds().has(b)
    ? `data/workbench_boards/${b}.js?v=wb2`
    : `data/boards/${b}.js?v=${encodeURIComponent(getParam("v")||"20261101facemedia")}`;
  s.onload=()=>{
    const d=window["WIKI_BOARD_"+b];
    if(!d||!d.meta||!Array.isArray(d.items)){showLoadError("数据格式不完整："+b);return;}
    // 按编号排序（meta.sort_by_code）：先类型分组，再编号升序，显示层兜底
    if(d.meta.sort_by_code){
      const KN={"头像":0,"头像框":1,"名片框":2};
      d.items.sort((x,y)=>{
        const kx=(KN[x.kind]!=null?KN[x.kind]:9), ky=(KN[y.kind]!=null?KN[y.kind]:9);
        if(kx!==ky)return kx-ky;
        const nx=Number(x.item_id), ny=Number(y.item_id);
        const vx=Number.isFinite(nx)?nx:1e15, vy=Number.isFinite(ny)?ny:1e15;
        return vx-vy;
      });
    }
    cb(d);
  };
  s.onerror=()=>showLoadError("板块数据文件读取失败："+b);
  document.head.appendChild(s);
}
function showLoadError(reason){
  document.getElementById("title").textContent="板块加载失败";
  document.querySelector(".controls").style.display="none";
  const n=document.getElementById("notes");n.style.display="block";
  n.textContent=reason+"。请刷新页面重试；仍失败时，请检查 data/boards 下文件是否完整。可从顶部返回 Wiki 总入口。";
  document.getElementById("grid").innerHTML='<div class="empty">未加载数据，没有把缺失数据视为空表。</div>';
}
let searchTimer=null;
function scheduleSearch(event){
  clearTimeout(searchTimer);
  if(event&&event.isComposing)return;
  searchTimer=setTimeout(render,160);
}
/* 2026-10-30：头像板按类型打类名 —— 名片框/头像是三种完全不同的图型，卡面要分开对待 */
const AVATAR_KIND_CLS={"头像":"k-da","头像框":"k-af","名片框":"k-nc"};

// 英文枚举值 → 中文（只改显示；data 内原始值不变）



// ── v1.3.1 canonical 状态词表（只做显示/筛选；业务结论一律来自 service / active artifact）──
// listing_status = 唯一上架状态字段（verified_listed / verified_unlisted / unresolved）
// release_state 仅出现在 legacy 板（data/boards/*）的旧派生值，仅作显示兼容，不是 canonical。
// 上架状态可选值 = canonical listing_status + legacy 板 release_state（两个数据源都保留，标签统一用中文短名）


VALUE_CN.listing_status=LISTING_CN;
VALUE_CN.release_state=LISTING_CN;
VALUE_CN.name_status=NAME_CN;
// canonical 优先，legacy 别名兜底（读值，不做判断）
// ★ 2026-10-18（用户口径）：上架状态改为**按 sale_ts 实时算**，静态 release_state 只作无时间戳时的回落，
//   否则皮肤到点上架了页面还写着「预告 · 未到上架日」。
function listingOf(it){
  const ts=Number((it&&it.sale_ts)||0);
  if(ts>0)return ts<=Date.now()/1000?"on_sale":"upcoming";
  const v=it&&it.listing_status;   // canonical 优先
  if(v!==undefined&&v!==null&&v!=="")return v;
  const r=it&&it.release_state;                 // legacy 板字段兜底（保留数据源）
  return (r===undefined||r===null)?"":r;}
/* 距上架倒计时（只对未到点的有意义；已上架返回空串） */
function saleCountdownCN(it){
  const ts=Number((it&&it.sale_ts)||0);
  if(!(ts>0))return "";
  const sec=ts-Date.now()/1000;
  if(!(sec>0))return "";
  const d=Math.floor(sec/86400),h=Math.floor(sec%86400/3600),m=Math.floor(sec%3600/60);
  if(d>0)return `${d} 天 ${h} 小时后上架`;
  if(h>0)return `${h} 小时 ${m} 分后上架`;
  return `${Math.max(1,m)} 分钟后上架`;
}
function nameStatusOf(it){const v=it.name_status;if(v)return v;
  return it.candidate_name?"candidate":(it.name?"verified":"unresolved");}
/* 卡面只给「已上架 / 未上架」两档短标签（2026-10-29 用户口径：不再单列「上架状态」一项，
   直接跟在「上架 <日期>」后面）；其余状态（未解析/未配时间/仅行为资源）不标，避免卡面出现长解释。 */
function listingShortCN(v){
  if(v==="on_sale"||v==="verified_listed")return "已上架";
  if(v==="upcoming"||v==="verified_unlisted")return "未上架";
  return "";}
function listingSupported(){
  const v=(DATA&&DATA.meta&&DATA.meta.status_vocab&&DATA.meta.status_vocab.listing_status)||null;
  return v&&Array.isArray(v.supported_today)?v:null;}
/* ── 2026-10-18 上架状态配色（用户口径）：已上架=绿、预告=橙，其余中性 ──
   class 由状态值安全化得到（只留 [A-Za-z0-9_-]），值本身不改、只是显示层上色。 */
function lsClass(v){
  const k=String(v==null?"":v).replace(/[^A-Za-z0-9_-]/g,"");
  return k?"ls-"+k:"ls-none";}
function lsLabel(v){return LISTING_CN[v]||(String(v||"")===""?"（无字段）":String(v));}
/* 顶部统计里的「上架状态 已上架 116 / 预告 3」——与卡面共用 ls-* 配色 */
function listingStatHTML(items){
  const acc={};
  for(const it of items){const k=listingOf(it)||"";acc[k]=(acc[k]||0)+1;}
  const vs=listingSupported();
  return Object.entries(acc).map(([k,v])=>
      `<span class="ls-chip ${lsClass(k)}" title="${esc(lsLabel(k))}">${esc(lsLabel(k))} ${v}</span>`).join(" / ")+
    (vs?`（canonical 支持类别：${vs.supported_today.map(x=>esc(lsLabel(x))).join("、")}）`:"");
}
/* ── 2026-10-18 卡片密度（紧凑/舒适）：只切 body class，不重绘、不改数据 ── */
const DENSITY_KEY="board_density";
function densityStored(){
  try{return localStorage.getItem(DENSITY_KEY)==="compact"?"compact":"comfortable";}
  catch(e){return "comfortable";}}
function applyDensity(v,persist){
  const compact=v==="compact";
  try{
    const cl=document.body&&document.body.classList;
    if(cl){if(compact){cl.add&&cl.add("density-compact");}else{cl.remove&&cl.remove("density-compact");}}
  }catch(e){}
  const btn=document.getElementById("fDensity");
  if(btn){
    btn.textContent=compact?"密度：紧凑":"密度：舒适";
    btn.setAttribute("aria-pressed",String(compact));
    if(btn.dataset)btn.dataset.density=compact?"compact":"comfortable";
    btn.title=compact?"卡片密度：紧凑（小图 5 列）— 点击切回舒适":"卡片密度：舒适（大图 4 列）— 点击切紧凑";
  }
  if(persist){try{localStorage.setItem(DENSITY_KEY,compact?"compact":"comfortable");}catch(e){}}
}
// 工程字段：不进卡面，统一折叠进「技术详情 / 数据来源 / 审计信息」
const TECH_KEYS=new Set(["provenance","text_provenance","field_provenance","name_resolution","source","source_entries",
  "locator_chain","upstream","source_lock_sha256","source_file_id","source_id","source_path","source_sha256",
  "package_sha256","decoded_sha256","row_key","entry_index","file_id","field_refs","field_chs_slot","value_chs_slot",
  "scalar_type","schema_ref","schema_refs","structural_record_key","search_text","status_tags","publication_tier",
  "identity_status","identity_state","identity_reason","evidence","evidence_level","audit_status","reliability_state",
  "hide_in_bag_state","name_evidence","sfx_consensus_state","source_record_layer","source_kind","scope","chain_status",
  "component","dataset_partition","status","kind","role","src","record_key","record_id","text_provenance_note",
  "candidate_name_source","candidate_name_status","candidate_reference_fields","static_fields",
  "verified_weapon_skin_identity","variant_relation_state","variant_relation_rule","variant_relation_target","variant_relation_target_state","main_skin_id","variant_type",
  "dataset","manifest_path","source_entry","node_type","value_type","origin","notes_src",
  "icon","icon_path","texture","model","res_path","paths","sample_paths","sfx_paths","asset_paths","label_path",
  "physical_fid","payload_sha","payload_sha256","source_state","identity_namespace","identity_ns","evidence_refs",
  // 冗余/原始字段（与已有中文字段重合或仅是原始配置），收进技术详情
  "sale_ts","instance_exp_ts","name_field_chs_slot","name_value_chs_slot","desc_field_chs_slot",
  "desc_value_chs_slot","static_reward_raw","item_master_id"]);
// 数据里可能写死的英文术语 → 中文（只在显示层替换，旧产物不用重跑）

function zhText(s){let out=String(s??"");for(const [re,rp] of TERM_CN)out=out.replace(re,rp);return out;}
/* 板级「来源表」：把 meta.tech_sources 按角色分组渲染（口径见 tools/build/sync_board_tech_sources.py）*/
const SRC_ROLE_CN={primary:"主源表（直接产出行条目）",comparison:"对照表（补字段 / 交叉校验）",chs:"文本池（中文名 / 描述）",lock_only:"仅校验（快照锁，不出条目）",unlabeled:"其它表（快照锁内未标注角色）",other:"其它"};
const SRC_KIND_CN={row:"行表",field:"字段补充",chs:"文本池",lock_only:"快照锁"};
function techSourcesHtml(ts){
  if(!ts||!Array.isArray(ts.tables)||!ts.tables.length)return "";
  const groups={};
  for(const t of ts.tables){const g=t.role||"other";(groups[g]=groups[g]||[]).push(t);}
  const order=["primary","comparison","chs","lock_only","unlabeled","other"];
  let html='<div class="k">来源表</div><div class="v srv">';
  html+=`<div class="srchint">本板块读取 <b>${ts.table_count??ts.tables.length}</b> 张表 · 快照锁 <b>${ts.lock_count??0}</b> 条；每张表的角色与命中的卡片数如下。</div>`;
  for(const g of order){
    const arr=groups[g];if(!arr)continue;
    html+=`<div class="srcgroup"><div class="srcgname">${esc(SRC_ROLE_CN[g]||g)}</div>`;
    for(const t of arr){
      const meta=[SRC_KIND_CN[t.kind]||t.kind];
      if(t.cards)meta.push(`${t.cards} 卡`);
      if(t.fields&&t.fields.length)meta.push("字段 "+t.fields.join("/"));
      html+=`<div class="srcrow"><code>${esc(t.table)}</code><span>${esc(meta.filter(Boolean).join(" · "))}</span></div>`;
    }
    html+="</div>";
  }
  return html+"</div>";
}
/* 字段级来源块：描述 / 图标 / 魅力值 / 部位 各自来自哪张表哪一行。
   注：这些是「跨源补字段」，独立成块，不并入 locator_chain（契约禁跨源字段 join）。*/
function fieldSrcText(v){
  if(v==null)return "";
  if(typeof v==="string")return v;
  const out=[];
  if(v.table)out.push(v.table);
  if(v.row_key!=null)out.push("行 "+v.row_key);
  if(v.field_refs&&v.field_refs.length)out.push(v.field_refs.join("/"));
  if(v.note)out.push(v.note);
  return out.length?out.join(" · "):(v.source_id||"");
}
function pushFieldSources(p,pairs){
  if(!p)return;
  if(p.desc_source)pairs.push(["描述来源",fieldSrcText(p.desc_source)]);
  if(p.icon_source)pairs.push(["图标来源",fieldSrcText(p.icon_source)]);
  if(p.charm_source)pairs.push(["魅力值来源",fieldSrcText(p.charm_source)]);
  if(p.part_source)pairs.push(["部位来源",fieldSrcText(p.part_source)]);
  if((p.supplement_locks||[]).length){
    const ls=(p.supplement_locks||[]).map(l=>l&&(l.source_id||l.sha256)).filter(Boolean);
    if(ls.length)pairs.push(["补充来源",ls.join(" / ")]);
  }
}
function renderTechSection(pairs){
  // Wiki View / Workbench View 分层：折叠容器与标题始终保留（旧契约不变），只在容器内部换内容
  if(WB_VIEW!=="workbench"){
    return '<details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="sub">'
      +'Wiki View：技术字段（溯源 / 快照基准 / 证据）已隐藏；'
      +'已隐藏。</div></details>';
  }
  const rows=(pairs||[]).filter(([k,v])=>v!==null&&v!==undefined&&v!=="");
  if(!rows.length)return "";
  const html=rows.map(([k,v])=>{
    const val=typeof v==="object"?JSON.stringify(v):fmtVal(k,v);
    return `<div class="k" title="${esc(k)}">${esc(FIELD_CN[k]||k)}</div><div class="v mono">${esc(val)}</div>`;
  }).join("");
  return `<details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="kv">${html}</div></details>`;
}
// 标题清理：板块标题里不允许出现裸英文工程词

function zhTitle(s){let out=String(s??"");for(const [re,rp] of TITLE_CN)out=out.replace(re,rp);return out;}
function fmtVal(k,v){
  // 板级品级注释（如时装：5 典藏 / 6 幻彩 / 7 殿堂）
  if(DATA&&DATA.meta&&DATA.meta.grade_labels&&/^(grade_level|grade|level)$/.test(k)){
    const lb=DATA.meta.grade_labels[String(v)];
    if(lb)return String(v)+" "+lb;
  }
  if(k==="bundle"&&Array.isArray(v))return v.map(b=>`${b.name}×${b.count}`).join("、");
  if(k==="trial_variants"&&Array.isArray(v))return v.map(t=>`${t.name}${t.属性?`（${t.属性}）`:``}`).join("  ｜  ");
  if(k==="star_entries"&&Array.isArray(v))return v.map(s=>`${s.star}星：${s.text}`).join("  ｜  ");
  if(k==="skills"&&Array.isArray(v))return v.map(s=>s&&s.id!=null?(`${s.name?("「"+s.name+"」"):""}技能 ${s.id}${s.name_status==="未解出"?"（名未解出）":""}`):String(s)).join("\n");
  if(k==="talents"&&Array.isArray(v))return v.map(t=>`${t&&t.name?t.name:("科技 "+(t&&t.id))}${t&&t.max_level!=null?`（上限 ${t.max_level}）`:""}`).join("、");
  if(k==="classic_ref"&&v&&typeof v==="object")return `经典服名册：名 ${v.name||"—"} ｜ 品级 ${v.level??"—"}${v.desc?" ｜ "+v.desc:""}`;
  if(k==="server_branches"&&Array.isArray(v))return v.join("、");
  if(k==="recipe_materials"&&Array.isArray(v))return v.map(m=>`${m.name||("食材类"+m.type_id)}×${m.count}`).join("、");
  if(k==="version_status"&&VERSION_STATUS_CN[v])return VERSION_STATUS_CN[v];
  if(v===true)return "是";if(v===false)return "否";
  if(typeof v==="string"){
    const m=VALUE_CN[k];if(m&&m[v])return m[v];
    if(COMMON_VAL_CN[v]&&!FIELD_CN[v])return COMMON_VAL_CN[v];
    return zhText(v);
  }
  if(k==="mesh_total"&&typeof v==="number")return (v/1024).toFixed(1)+" KB";
  if(k==="gold_score"&&typeof v==="number")return (v*100).toFixed(1)+"%";
  if(typeof v==="object"&&v!==null){
    if(Array.isArray(v))return v.map(x=>(typeof x==="object"&&x!==null)?JSON.stringify(x):x).join("、");
    return Object.entries(v).map(([a,b])=>`${a}星：${b}`).join("\n");
  }
  return String(v);
}
// 活动子卡：rewards 逐格渲染（一个活动一张卡，格子=面板展示奖励）
function renderRewardsList(list){
  return `<section class="rewards"><div class="rewards-title">活动奖励面板（${list.length} 格）</div>`+
    list.map(r=>{
      const pos=r.position!=null?`<span class="r-pos">${r.position+1}</span>`:"";
      const meta=[r.item_id!=null?`道具ID ${r.item_id}`:""].filter(Boolean);
      if(r.prob!=null)meta.push(`概率 ${(r.prob*100).toFixed(4)}%`);
      if(r.config_exp)meta.push(`过期 ${r.config_exp}`);
      const cand=r.name_candidate?`<div class="r-cand">候选：${esc(r.name_candidate)}</div>`:"";
      return `<div class="reward"><div class="r-name">${pos}${esc(r.name||("ID "+r.item_id))}</div>`+
        `<div class="r-meta">${meta.join(" · ")}</div>${cand}</div>`;
    }).join("")+`</section>`;
}
// 兜底：任何 section/details 若渲染后没有任何内容行，则整体不输出（不出现空标题块）
function dropEmptySections(html){
  if(!html)return html;
  return html.replace(/<(section|details)\b[^>]*>[\s\S]*?<\/\1>/g,(blk)=>{
    const inner=blk.replace(/^<(section|details)\b[^>]*>/,"").replace(/<\/?(section|details)>$/,"");
    // 内容行判定：覆盖全部真实行类名（含 perf-row / k / v / skin-hist / desc / stars 等）；
    // 2026-10-29 音效改表格（audio-table），table/td 也要算有内容，否则整个音效块被误删
    const hasRow=/<(div|li|span|table)\b[^>]*class="[^"]*(kv|reward|pool|vv-row|behavior-resource|sfx-child|tech|sub|perf-row|skin-hist|desc|stars|nucleus-desc|rich|fact|audio-row|audio-table)\b[^"]*"/.test(inner)
      || /<(div|li)\b[^>]*class="(k|v)\b/.test(inner)
      || /<td\b/.test(inner);
    return hasRow?blk:"";
  });
}
function fmtPct(p){
  if(p==null)return "";
  const s=(p*100).toFixed(6).replace(/0+$/,"").replace(/\.$/,"");
  return `概率 ${s}%`;
}
// 子奖池映射：池 → slot → 奖励（含概率/过期原值/展示名桥/内部标记）
function renderPools(pools){
  if(!Array.isArray(pools)||!pools.length)return "";
  return `<section class="pools"><div class="rewards-title">子奖池映射（${pools.length} 池）</div>`+
    pools.map(p=>{
      const rows=(p.rows||[]).map(r=>{
        const meta=[r.slot!=null?`槽位 ${r.slot}`:""].filter(Boolean);
        if(r.prob!=null)meta.push(fmtPct(r.prob));
        if(r.prob_note)meta.push(`概率说明 ${zhText(r.prob_note)}`);
        if(r.config_exp)meta.push(`过期 ${r.config_exp}`);
        if(r.item_id!=null)meta.push(`道具ID ${r.item_id}`);
        if(r.source_internal_marker&&r.source_internal_marker!==r.display_name&&r.source_internal_marker!==r.name)meta.push(`内部标记 ${r.source_internal_marker}`);
        if(r.layer)meta.push(zhText(r.layer));
        const nm=r.display_name||r.name||"(无ID)";
        const bridge=(r.display_name&&r.display_name!==r.name)?`<div class="r-cand">展示名桥：${esc(r.name)}</div>`:"";
        return `<div class="reward"><div class="r-name">${esc(nm)}</div><div class="r-meta">${meta.join(" · ")}</div>${bridge}</div>`;
      }).join("");
      return `<div class="pool"><div class="pool-head">池 ${esc(p.pool_id)} · ${esc(p.name)}（${p.rows?p.rows.length:0} 行）</div><div class="pool-rows">${rows}</div></div>`;
    }).join("")+`</section>`;
}
function renderActivityPoolRefs(refs){
  if(!Array.isArray(refs)||!refs.length)return "";
  return `<section class="pools activity-pool-refs"><div class="rewards-title">逻辑活动池关系</div>`+
    refs.map(r=>{
      const meta=[zhText(r.role||""),zhText(r.status||"")].filter(Boolean).join(" · ");
      return `<div class="pool"><div class="pool-head">池 ${esc(r.pool_id)}${meta?` · ${esc(meta)}`:""}</div>`+
        `<div class="pool-rows"><div class="reward"><div class="r-name">${esc(r.note||"")}</div></div></div></div>`;
    }).join("")+`</section>`;
}
let DATA=null;
// ---- 溯源板级常量上提后的回退（2026-10-30）--------------------------------
//   背景：溯源常量（如 package_sha256 / table / snapshot）原被逐条重复写入，
//   30,252 条重复同一批常量 ⇒ 板体积多出数十 MB。
//   现改为按「条目形态」上提到 meta.provenance_defaults，条目里只留行级定位事实。
//   ★ 读取必须走 effProv()，否则「源快照摘要」「定位表」等展示会空掉。
// ★ 语义与后端 tools/provenance_defaults.py 保持一致（逐子键合并、条目级优先）。
// ★ 签名只认条目上的 _prov_shape 字段：后端上提时已把它写进条目，
//   这是**唯一权威来源**。前端不自己算签名（浏览器的哈希实现与 Python 不同，
//   自行计算会算出不同的签名 ⇒ 回退失效 ⇒ 展示项凭空消失）。
function effProv(it){
  const p=(it&&it.provenance)||{};
  const defs=(DATA&&DATA.meta&&DATA.meta.provenance_defaults)||null;
  if(!defs) return p;
  const sig=it&&it._prov_shape;
  if(typeof sig!=="string") return p;      // 无签名 ⇒ 未上提过的条目，直接用原值
  const sd=defs[sig];
  if(!sd) return p;
  const merged={};
  for(const k of Object.keys(sd)){
    const dv=sd[k], pv=p[k];
    if(dv&&typeof dv==="object"&&!Array.isArray(dv)){
      if(pv&&typeof pv==="object"&&!Array.isArray(pv)){
        merged[k]=Object.assign({},dv,pv);       // 逐子键合并（条目级优先）
      }else if(pv===undefined){
        merged[k]=Object.assign({},dv);           // 条目级无此键 ⇒ 用板级默认
      }else{
        merged[k]=pv;                            // 非对象（如字符串）⇒ 条目级优先
      }
    }else{
      merged[k]=dv;
    }
  }
  for(const k of Object.keys(p)){
    const pv=p[k], mv=merged[k];
    if(pv&&typeof pv==="object"&&!Array.isArray(pv)&&mv&&typeof mv==="object"&&!Array.isArray(mv)){
      continue;                                   // 已逐子键合并，不整体覆盖
    }
    merged[k]=pv;
  }
  return merged;
}
// ---- skin-mode（武器皮肤图鉴）紧凑卡片 ----
function gradeLabel(n){const m=(DATA&&DATA.meta&&DATA.meta.grade_labels)||null;
  return m&&m[String(n)]?String(n)+" "+m[String(n)]:String(n);}
function skinGradeTxt(it){return it.grade||(it.level!=null?("品级"+it.level):"");}
// ── B. 品级视觉分级：层级由真实 grade/level 派生（不改底层 grade 数据）──
//   6传世 / 5典藏 / 4紫皮 / 3直售 / 2白送 = 快照真实枚举的展示短名；未配置/未知 → 中性样式
const GRADE_TIERS={6:{cls:"t6",label:"传世"},5:{cls:"t5",label:"典藏"},4:{cls:"t4",label:"紫皮"},
  3:{cls:"t3",label:"直售"},2:{cls:"t2",label:"白送"}};
function gradeTier(it){
  const raw=String(it.grade||"").trim();
  const m=raw.match(/^(\d)/);
  const lv=m?Number(m[1]):(typeof it.level==="number"?it.level:null);
  const neutral=!raw||["未配置","未知","无","未确认"].includes(raw);
  return GRADE_TIERS[lv]||{cls:"unknown",label:neutral?"品级未确认":raw};
}
// ── C. 表现摘要：只用已有可回放字段（combat_panel[].cat / behavior_resources[].field），不新增推断 ──
//   类目名 = 同快照 UI 面板类目；行为字段只映射语义可确认的，其余统一进「其他表现」
const PERF_PANEL_CAT={"命中效果":"命中特效","击败特效":"击败特效","伤害跳字":"伤害跳字","攻击弹道":"枪口/弹道",
  "挥砍特效":"挥砍特效","护臂开合":"护臂开合","战斗音效":"音效","攻击准星":"攻击准星","蓄力效果":"蓄力表现",
  "核芯联动":"核芯联动","切枪动画":"切枪动画","特殊交互":"特殊交互"};
const PERF_BEHAVIOR_CAT={fire_sfx_path:"开火表现",hit_sfx_path:"命中特效",extension_defeat_sfx:"击败特效",
  explode_sfx_path:"爆炸特效",brass_sfx_path:"弹壳表现",
  trajectory_sfx_path:"枪口/弹道",trajectory_sfx_path_nor:"枪口/弹道",trajectory_path_real:"枪口/弹道",
  trajectory_sfx_path_trace:"枪口/弹道",trajectory_path_special:"枪口/弹道"};
const PERF_OTHER="其他表现";
// sfx_type 码 → 类目（码与标签均来自同快照 sfx_type_label，不新增语义）
const PERF_SFX_TYPE={3:"命中特效",4:"击败特效",6:"枪口/弹道",7:"音效",9:"攻击准星",10:"伤害跳字",
  13:"核芯联动",14:"蓄力表现",15:"专属动作",16:"专属待机动作",20:"切枪动画"};
function perfSummary(it){
  const labels=[],detail=[];
  const push=(label,name,src,tip)=>{
    if(!labels.includes(label))labels.push(label);
    detail.push({label:label,name:name||"",src:src,tip:tip||""});
  };
  const panel=Array.isArray(it.combat_panel)?it.combat_panel:[];
  if(panel.length){
    for(const row of panel){
      if(!row||!row.cat)continue;
      push(PERF_PANEL_CAT[row.cat]||PERF_OTHER,row.name||"",row.src==="es"?"UI 面板":"同快照配置",row.name||"");
    }
  }else{
    // 无 UI 面板时用 SFX 子项类目兜底（类目名=同快照 sfx_type_label；弱名只记类目）
    for(const c of (it.sfx_items||[])){
      if(!c)continue;
      const label=PERF_SFX_TYPE[c.sfx_type]||PERF_OTHER;
      push(label,isWeakName(c.display_name)?"":(c.display_name||""),c.sfx_type_label||"SFX 子项",c.sfx_params||"");
    }
  }
  for(const r of (it.behavior_resources||[])){
    if(!r||!r.field)continue;
    push(PERF_BEHAVIOR_CAT[r.field]||PERF_OTHER,"","行为资源",r.path||"");
  }
  const named=detail.filter(d=>d.name&&!isWeakName(d.name));
  return {labels:labels,count:detail.length,named:named,detail:detail};
}
// ── 特效与战斗表现：统一业务项（用户 2026-09-13 口径；固定顺序 1–10 + 其它）──
// 只渲染业务项，不按 source/table 名拆栏目；同一信息只出现一次。
const BIZ_ORDER=[
 {k:"hit_effect",t:"命中效果"},
 {k:"kill_effect",t:"击败特效"},
 {k:"damage_number",t:"伤害跳字"},
 {k:"attack_visual",t:"攻击弹道",melee:"挥砍特效"},
 {k:"combat_sound",t:"战斗音效"},
 {k:"combat_crosshair",t:"攻击准星"},
 {k:"special_interaction",t:"特殊交互"},
 {k:"nucleus_linkage",t:"核芯联动"},
 {k:"exclusive_combat_animation",t:"专属战斗动作"},
 {k:"exclusive_idle_animation",t:"专属待机动作"}
];
const BIZ_OTHER_T="其它";
const BIZ_FROM_PANEL={"命中效果":"hit_effect","击败特效":"kill_effect","伤害跳字":"damage_number",
 "攻击弹道":"attack_visual","挥砍特效":"attack_visual","战斗音效":"combat_sound","攻击准星":"combat_crosshair",
 "攻击准心":"combat_crosshair","特殊交互":"special_interaction","核芯联动":"nucleus_linkage",
 "蓄力效果":"charge","切枪动画":"special_interaction","护臂开合":"arm_open"};
const BIZ_FROM_SFX={3:"hit_effect",4:"kill_effect",6:"attack_visual",7:"combat_sound",9:"combat_crosshair",
 10:"damage_number",13:"nucleus_linkage",14:"charge",15:"exclusive_combat_animation",
 16:"exclusive_idle_animation",20:"special_interaction"};
const BIZ_FROM_BEHAVIOR={hit_sfx_path:"hit_effect",fire_sfx_path:"combat_sound",hold_sfx_path:"combat_sound",
 hold_sfx_loop_path:"combat_sound",trajectory_sfx_path:"attack_visual",trajectory_sfx_path_nor:"attack_visual",
 trajectory_path_real:"attack_visual",trajectory_sfx_path_trace:"attack_visual",trajectory_path_special:"attack_visual",
 skin_replace_anims:"exclusive_combat_animation",defeat_args:"kill_effect",defeat_model:"kill_effect",
 extension_defeat_sfx:"kill_effect",explode_sfx_path:"explode",brass_sfx_path:"brass",
 socket:"special_interaction",preview_range_sfx_path:"preview_extra"};

const BIZ_FROM_CANON={hit_effect:"hit_effect",kill_effect:"kill_effect",damage_number:"damage_number",
 projectile_effect:"attack_visual",slash_effect:"attack_visual",combat_sound:"combat_sound",
 combat_crosshair:"combat_crosshair",special_interaction:"special_interaction",nucleus_linkage:"nucleus_linkage",
 exclusive_combat_animation:"exclusive_combat_animation",exclusive_idle_animation:"exclusive_idle_animation",
 other:"preview_extra"};
function combatItems(it){
  const isMelee=/冷兵器|护臂/.test(it.weapon_type_label||"");
  /* 2026-10-31 用户口径：卡片可标 no_audio=true —— 该皮肤不展示任何音效类战斗表现 */
  const noAudio=it.no_audio===true;
  const AUDIO_KEYS={combat_sound:1};
  // 其余项顺序（非 10 项内）：保留各自业务名，不按 source 表名生成
  const EXTRA_ORDER=["charge","arm_open","explode","brass","preview_extra","switch_anim"];
  const acc={};
  const base=p=>{const t=String(p||"");const i=t.lastIndexOf("/");return i>=0?t.slice(i+1):t;};
  const put=(k,name,src,internal)=>{
    if(!k)return;
    if(noAudio&&AUDIO_KEYS[k])return;
    const o=acc[k]||(acc[k]={srcs:[],names:[],internals:[]});
    if(src&&o.srcs.indexOf(src)<0)o.srcs.push(src);
    if(name&&!isWeakName(name)&&o.names.indexOf(name)<0)o.names.push(name);
    const b=base(internal);
    if(b&&!/^[0-9]+$/.test(b)&&o.internals.indexOf(b)<0)o.internals.push(b);
  };
  (it.combat_panel||[]).forEach(r=>{if(r&&r.cat)put(BIZ_FROM_PANEL[r.cat],r.name,r.src==="es"?"UI 面板":"同快照配置");});
  (it.sfx_items||[]).forEach(c=>{if(c)put(BIZ_FROM_SFX[c.sfx_type],c.display_name||c.sfx_name,"同快照配置",c.sfx_params);});
  (it.behavior_resources||[]).forEach(r=>{if(r&&r.field)put(BIZ_FROM_BEHAVIOR[r.field],"","行为资源",r.path);});
  const ef=it.effects;
  if(ef&&ef.types)Object.keys(ef.types).forEach(t=>{
    const o=ef.types[t]||{};const nm=(o.names&&o.names[0])||"";
    put(BIZ_FROM_CANON[t],nm,"canonical");
  });
  const main=[];
  BIZ_ORDER.forEach(b=>{const o=acc[b.k];if(!o)return;
    main.push({k:b.k,label:(b.melee&&isMelee)?b.melee:b.t,name:o.names[0]||"",internals:o.internals,srcs:o.srcs});});
  // 其余项：逐项成行（如「护臂开合」是护臂专属特效，自己一行）；无标签的合并进「其它」
  const known=EXTRA_ORDER.filter(k=>acc[k]);
  known.forEach(k=>main.push({k:k,label:BIZ_EXTRA_LABEL[k],name:acc[k].names[0]||"",internals:acc[k].internals,srcs:acc[k].srcs}));
  const normSlot=t=>String(t||"").replace(/[（(][^）)]*[）)]/g,"").trim();
  const showMap={};
  (it.effect_show||[]).forEach(r=>{if(r&&r.name){const h={name:r.name,icon:r.icon_rel||""};showMap[normSlot(r.slot_key||r.slot)]=h;showMap[normSlot(r.slot)]=h;}});
  const SLOT_ALIAS={"攻击准心":"攻击准星","命中特效":"命中效果","专属战斗动作":"特殊交互","挥砍特效":"攻击弹道","特殊交互":"专属战斗动作"};
  main.forEach(d=>{const k=normSlot(d.label);const hit=showMap[k]||showMap[SLOT_ALIAS[k]];if(hit){d.note=d.name;d.name=hit.name;d.icon=hit.icon;d.official=true;}});
  /* effect_show 里有、但上面的合并没覆盖到的槽位 → 单独成「官方名」行 */
  (it.effect_show||[]).forEach(r=>{
    if(!r||!r.name)return;
    const slot=normSlot(r.slot_key||r.slot);
    if(noAudio&&/音效/.test(slot))return;
    if(main.some(d=>{const L=normSlot(d.label);return L===slot||SLOT_ALIAS[L]===slot||SLOT_ALIAS[slot]===L;}))return;
    main.push({k:"es:"+slot,label:slot,name:r.name,internals:[],srcs:[],official:true,
               icon:r.icon_rel||"",note:""});
  });
  /* 统一槽位顺序：effect_show 补进来的行也按业务顺序排 */
  const SLOT_ORDER=["命中效果","击败特效","伤害跳字","攻击弹道","挥砍特效","攻击准星","特殊交互",
                    "核芯联动","专属战斗动作","专属待机动作","蓄力效果","护臂开合"];
  main.sort((a,b)=>{
    const ia=SLOT_ORDER.indexOf(normSlot(a.label)), ib=SLOT_ORDER.indexOf(normSlot(b.label));
    return (ia<0?99:ia)-(ib<0?99:ib);
  });
  const rest=Object.keys(acc).filter(k=>!BIZ_ORDER.some(b=>b.k===k)&&known.indexOf(k)<0);
  if(rest.length){
    const srcs=[],names=[];
    rest.forEach(k=>{acc[k].srcs.forEach(x=>{if(srcs.indexOf(x)<0)srcs.push(x);});
      names.push(acc[k].names[0]||BIZ_EXTRA_LABEL[k]||k);});
    main.push({k:"other",label:"其它",name:names.join("、"),srcs:srcs});
  }
  return main;
}
function renderCombatUnified(it){
  const items=combatItems(it);
  if(!items.length)return "";
  const rows=items.map(d=>{
    const tip=d.detail?` title="${esc(d.detail)}"`:"";
    const internals=(d.internals||[]).slice(0,3).map(x=>`<code class="perf-internal">${esc(x)}</code>`).join("");
    const fallback=(d.internals||[])[0]||"";
    const ico=d.icon?`<img class="perf-icon" src="${esc(d.icon)}" alt="">`:`<span class="perf-icon blank"></span>`;
    /* 2026-10-29（用户口径）：内部备注特效名不与正式名并排展示；
       title 始终带全名（窄栏截断时可悬浮看全名），有内部备注名再附在后面 */
    const nameTip=` title="${esc(d.name)}${(d.note&&d.official)?`｜内部备注名：${esc(d.note)}`:""}"`;
    return `<li class="perf-row" data-cat="${esc(d.label)}"${tip}>`+ico+`<span class="perf-cat">${esc(d.label)}</span>`+
      (d.name?`<span class="perf-name${d.official?" official":""}"${nameTip}>${esc(d.name)}</span>`
             :(fallback?`<span class="perf-name">${esc(fallback)}</span>`:`<span class="perf-name weak">已配置</span>`))+
      `${d.srcs&&d.srcs.length?`<span class="perf-src perf-hidden" hidden></span>`:""}</li>`;}).join("");
  return `<ul class="perf-list">${rows}</ul>`;
}
/* 2026-10-29（用户口径）：删掉「音效真名（内部名）」块 —— jump_b_attack_01 之类是动作通用
   音效的内部名，与皮肤展示无关；且音频库文件未随数据分发，该块此前只剩真名列表。 */
function renderSkinAudio(it){
  const bank=(window.WEAPON_SKIN_AUDIO_ATTACHMENTS||{}).skins||{};
  let rec=bank[String(it.skin_id??it.id??"")];
  /* 时限变体行（天马行空（14天）等）：音效目录与主卡相同 → 按去掉「（…）」的主卡名回退查找 */
  if(!rec){
    const base=String(it.name||"").replace(/（[^）]*）\s*$/,"").trim();
    if(base&&base!==String(it.name||"")){
      const hit=Object.keys(bank).find(k=>String(bank[k].name||"")===base);
      if(hit)rec=bank[hit];
    }
  }
  const hasFiles=rec&&Array.isArray(rec.groups)&&rec.groups.length;
  if(!hasFiles)return "";
  let n=0;
  /* 2026-10-29（用户口径）：表头 含义 / 原名 / 试听 只在最顶部出现一次；
     分组标签改为表内整行小标题（colspan=3），不再每组重复一张表 */
  const bodyRows=rec.groups.map(g=>{
    const items=g.items||[];n+=items.length;
    const gRow=(rec.groups.length>1&&g.label)?`<tr class="a-group"><td colspan="3">${esc(g.label)}</td></tr>`:"";
    const rows=items.map(x=>{
      const pend=x.pending?'<i class="pres-mark">待确认</i>':"";
      const stem=String(x.file||"").replace(/\.wav$/i,"");
      const src="assets/audio/weapon_skin/"+(g.dir||rec.dir)+"/"+x.file;
      return `<tr title="${esc(x.file)}"><td class="a-mean">${esc(x.label||"音效")}${pend}</td>`+
        `<td class="a-raw"><code>${esc(stem)}</code></td>`+
        `<td class="a-play"><audio controls preload="metadata" src="${esc(src)}"></audio></td></tr>`;
    }).join("");
    return gRow+rows;
  }).join("");
  const table=`<table class="audio-table"><thead><tr><th>含义</th><th>原名</th><th>试听</th></tr></thead><tbody>${bodyRows}</tbody></table>`;
  const head=`皮肤音效 ${n} 条`;
  return `<details class="audio"><summary>${head}</summary>${table}`+
    `<div class="audio-note">音频为客户端音频库静态提取，含义为人工听辨标注，仅供试听参考。</div></details>`;
}
function renderPerfDetail(it){
  const items=combatItems(it);
  if(!items.length)return "";
  /* 2026-10-29（用户口径）：口径说明文字折叠进「技术详情」，不再占表现区版面 */
  /* 2026-10-29（用户口径）：删类目汇总徽章（命中效果 ×1 之类与下方列表冗余），只留列表 */
  return `<details class="perf"><summary>特效与战斗表现 ${items.length} 项</summary>${renderCombatUnified(it)}</details>`;
}

/* ★★ 补回（2026-09-18）：viewer 接线块 —— 此前从 git HEAD 还原 board.html 时丢失，
   本块来自损坏版（中文乱码、代码完好）。中文串已按英文键名修复。 */
function skinMediaRecord(it){
  const bank=(window.WEAPON_SKIN_MEDIA||{}).skins||{};
  const keys=[it.skin_id,it.skin_item_id,it.id,it.structural_record_key].filter(value=>value!==null&&value!==undefined);
  for(const key of keys){if(bank[String(key)])return bank[String(key)];}
  return null;
}
function mediaPosterSrc(record){const poster=record&&record.poster;return typeof poster==="string"?poster:(poster&&poster.src)||"";}
/* 3D 渲染截图不是 2D 海报：media 里这 7 条（1110152/1110165/1110169/1110171/1110177/1110185/1110186）
   的 poster 指向 assets/3d/.../poster.webp 且无 poster_source —— 属 3D 管线产物，
   卡面不得拿它顶 2D 图（用户 2026-10-18 口径）。 */
function mediaPosterIsRender(record){
  const src=mediaPosterSrc(record);
  if(!src)return false;
  const poster=record&&record.poster;
  if(poster&&typeof poster==="object"&&poster.is_render)return true;
  return src.indexOf("assets/3d/")>=0||/^\/?3d\//.test(src);
}
function media2DPosterSrc(record){return mediaPosterIsRender(record)?"":mediaPosterSrc(record);}
function mediaPreviewReady(record){
  const preview=record&&record.preview_3d;
  return !!(preview&&preview.status==="ready"&&(preview.manifest||preview.model||(preview.states&&Object.keys(preview.states).length)));
}
/* 2026-10-18（用户口径）：卡面只放 2D 海报。3D 入口/材质保真徽标一律进「展开后」详情区，
   卡面无 2D 图就整块不渲染 —— 不拿 3D 渲染图顶卡面。 */
function renderSkinMedia(it,name){
  /* ★ 2026-10-24：data/media/weapon_skin_media.js 可能没随数据包分发（新设备实测缺整个 data/media/）。
     查不到 record 时，退回板内自带的 _media.images —— 不再让卡面整块消失。 */
  const record=skinMediaRecord(it);
  const fallback=(()=>{
    const imgs=(it&&it._media&&it._media.images)||[];
    const hit=imgs.find(x=>x&&x.png&&!/3d\//i.test(String(x.png)))||imgs[0];
    return hit&&hit.png?hit.png:"";
  })();
  if(!record){
    if(!fallback)return "";
    return `<div class="skin-media"><img src="${esc(fallback)}" alt="${esc(name)}预览" loading="lazy" decoding="async"></div>`;
  }
  const poster=media2DPosterSrc(record);
  if(!poster){
    if(!fallback)return "";
    return `<div class="skin-media"><img src="${esc(fallback)}" alt="${esc(name)}预览" loading="lazy" decoding="async"></div>`;
  }
  /* ★ 2026-10-17：这张图可能根本不是海报而是**素材底图**（法线图/掩码/色带/平铺）——
     按像素内容判过才有的字段；有就明说，别让人把法线图当皮肤预览看。无值不加标签。 */
  const kindLabel=(record&&record.poster_kind)||"";
  return `<div class="skin-media"><img src="${esc(poster)}" alt="${esc(name)}预览" loading="lazy" decoding="async">`+
    `${kindLabel?`<span class="skin-media-fidelity" title="按像素内容判定：这是素材底图，不是皮肤海报">素材底图 · ${esc(kindLabel)}</span>`:""}</div>`;
}
/* 3D 预览按钮：只出现在展开后的详情区（卡面不出现）。取值口径与卡面一致：mediaPreviewReady。 */
function renderSkinPreview3D(it){
  const record=skinMediaRecord(it);
  if(!record||!mediaPreviewReady(record))return "";
  const material=(record.preview_3d&&record.preview_3d.material_fidelity)||"";
  const note=(record.preview_3d&&record.preview_3d.fidelity_note)||"";
  /* 2026-09-19：取值口径统一为有定义的四个（+ 兼容旧值）；徽标 hover 显示该条的依据与未决项 */
  const fidelity={source_matched:"源材质匹配",source:"源数据",source_candidate:"源数据（候选级）",
                  approximate:"材质近似",unbuilt:"未建（无材质链）"}[material]||material;
  const fidTitle=note?`材质保真度依据：${note}`:(material||"");
  return `<div class="skin-preview3d"><button class="skin-media-button" type="button" data-skin-id="${esc(it.skin_id??it.skin_item_id??it.id)}" onclick="openSkin3D(event,this)">3D 预览</button>`+
    `${fidelity?`<span class="skin-media-fidelity" title="${esc(fidTitle)}">${esc(fidelity)}</span>`:""}`+
    `<span class="skin-preview3d-note">按源模型与材质实时绘制，与卡面 2D 图来源不同。</span></div>`;
}
function openSkin3D(event,button){
  event.preventDefault();event.stopPropagation();
  const bank=(window.WEAPON_SKIN_MEDIA||{}).skins||{},record=bank[String(button.dataset.skinId)];
  if(!record)return;
  const card=button.closest(".skin-card"),title=card&&card.querySelector(".skin-name");
  if(window.WikiWeaponViewer)window.WikiWeaponViewer.open(record,{title:title?title.textContent:"武器 3D 预览"});
}

/* ★★ 骨骼接线（2026-09-19，Lead）：把已有骨骼/挂点产出绑进 wiki。
   数据源 data/media/weapon_skin_skeleton.js（由 SKEL2_all_37.json + _skeletons/ 实际文件生成）。
   诚实口径：逐骨 TRS 未定证 ⇒ 预览是"层级自动布局"，页面必须明说；源侧无骨架的给挂点复原。 */
function skinSkeletonRecord(it){
  const bank=(window.WEAPON_SKIN_SKELETON||{}).skins||{};
  const keys=[it.skin_id,it.skin_item_id,it.id,it.structural_record_key].filter(value=>value!==null&&value!==undefined);
  for(const key of keys){if(bank[String(key)])return bank[String(key)];}
  return null;
}
function renderSkinSkeleton(it){
  const rec=skinSkeletonRecord(it);if(!rec)return "";
  const id=esc(rec.skin_id),parts=[];
  if(rec.has_skeleton){
    const nr=(rec.roots&&rec.roots.length>1)?`（${rec.roots.length} 个根）`:"";
    parts.push(`<span class="skel-tag" title="源 .mesh 内骨骼名数；逐骨 92 B 绑定数据块的字段语义未定证">骨骼 <b>${esc(rec.bone_count)}</b> 根${nr}</span>`);
    parts.push(`<a class="skel-link primary" href="${esc(rec.preview)}">3D 层级预览</a>`);
    if(rec.skeleton_glb)parts.push(`<a class="skel-link" href="${esc(rec.skeleton_glb)}" download>骨架 GLB</a>`);
    if(rec.skeleton_json)parts.push(`<a class="skel-link" href="${esc(rec.skeleton_json)}" download>骨架 JSON</a>`);
  }else{
    parts.push(`<span class="skel-tag" title="四重证据：全变体 flag=0 ／ biped 串=0 ／ .gim 无 CutBones ／ 64 条命名探测 0 命中">源侧无骨架 · 挂点复原</span>`);
    parts.push(`<a class="skel-link primary" href="${esc(rec.preview)}">3D 挂点预览</a>`);
    if(rec.mount_json)parts.push(`<a class="skel-link" href="${esc(rec.mount_json)}" download>挂点 JSON</a>`);
  }
  const vRaw=rec.self_check&&rec.self_check.parent_lt_self_violations;
  const vN=Array.isArray(vRaw)?vRaw.length:(typeof vRaw==="number"?vRaw:0);
  const warn=vN?`<span class="skel-warn" title="自检：parent&lt;self 违规 ${esc(vN)} 处（页面用真实 children 树渲染，不用 parent 索引）">⚠ ${esc(vN)} 处自检告警</span>`:"";
  /* 时限变体（11101451/11101691/11101771）各有独立 id 与骨骼/挂点产出，但基卡不渲染独立行
     ⇒ 在这里补成 37/37 可查（2026-09-19，viewer-auditor 发现 34/37 后由 Lead 补）。 */
  const bank=(window.WEAPON_SKIN_SKELETON||{}).skins||{},base=String(rec.skin_id),vparts=[];
  for(const v of (it.variant_items||[])){
    const vid=(v&&v.skin_id!=null)?String(v.skin_id):null;
    if(!vid||vid===base)continue;
    const vr=bank[vid];if(!vr)continue;
    const label=vr.has_skeleton?`变体 ${vid}：骨骼 ${vr.bone_count} 根`:`变体 ${vid}：源侧无骨架 · 挂点`;
    vparts.push(`<a class="skel-link" href="${esc(vr.preview)}" title="时限变体 id（与基卡共用模型）">${esc(label)}</a>`);
  }
  return `<div class="skin-skel">${parts.join("")}${warn}${vparts.join("")}</div>`;
}

function skinTypeTxt(it){return it.weapon_type_label||it.weapon_type!=null?("类型"+it.weapon_type):"";}
function renderSkinCard(it,cidx){
  // 卡面只放普通玩家关心的字段；工程字段走 renderSkinDetail 里的「技术详情」折叠区
  const name=it.name_display||it.name||it.display_name||("未命名皮肤 · ID "+(it.skin_id??it.id));
  const tier=gradeTier(it);
  const tags=[];   // 只放 facts/头部未覆盖的信息（上架时间·武器类型·联动IP·上架/名称状态只在头部与 facts 各出现一次）
  // 卡面顺序：品级 → 武器种类 → 上架时间/状态 → 联动IP → 表现摘要 → 时限变体 → 名称/预告等状态
  // 品级徽章已移到大标题左侧（.skin-head-row），tags 里不再重复渲染

  /* 2026-10-29（用户口径）：卡面去掉「表现特性 N 项 + 前 3 个表现名」「时限变体 N」——
     这三项在展开区（表现详情 / 时限变体）里都有，卡面重复且噪音大。 */
  if(it.catalog_layer==="behavior_preview_only")tags.push('<span class="skin-tag preview">仅行为资源</span>');
  // ── 卡面标注（用户 2026-09-13 卡统一设计）：武器类型 / 特效数目 / 部分特效名 / 联动IP / 状态 ──
  const facts=[];
  const wtCn=it.weapon_type_cn||typeCN(it.weapon_type_label||pick(it,"weapon_type_label")||"");
  if(wtCn)facts.push(`<span class="fact"><b>武器类型</b>${esc(wtCn)}</span>`);
  {const ef=it.effects;
   if(ef&&ef.count!=null)facts.push(`<span class="fact" title="按 canonical 字段判定的特效类别数">`+
     `<b>特效</b>${ef.count} 项${ef.present&&ef.present.length?`（${esc(ef.present.slice(0,3).join("、"))}${ef.present.length>3?"…":""}）`:""}</span>`);
   if(ef&&ef.names&&ef.names.length)facts.push(`<span class="fact" title="特效名来自展示层（legacy 板副本，presentation_only）">`+
     `<b>特效名</b>${esc(ef.names.slice(0,3).join("、"))}${ef.names_total>3?` 等 ${ef.names_total} 个`:""}<i class="pres-mark">历史</i></span>`);}
  {const ip=it.ip_liaison||it.ip_now;   // 没有 IP 就不显示这一项（用户 2026-09-13）
   // 来源必须在 title 里说清：用户参考目录 / 官方描述提取 / 配置参数（候选级）
   const ipSrc=it.ip_liaison?"联动IP（展示层：用户参考目录，presentation_only）"
     :(it.ip_now_state==="config_param_candidate"
       ?`联动IP（配置证据：${it.ip_now_evidence||"同快照配置参数"}）`
       :"联动IP（同快照官方描述提取）");
   if(ip)facts.push(`<span class="fact" title="${esc(ipSrc)}"><b>联动IP</b>${esc(ip)}</span>`);}
  /* 2026-10-29（用户口径）：卡面「上架状态」「名称」两项删除 —— 上架状态并到头部「上架 <日期>」后面
     （只要已上架/未上架两档），名称状态进展开区/技术详情。 */
  const detail=renderSkinDetail(it);
  const qNow=String((DATA&&DATA._query)||"");
  const vFocus=qNow&&(it.variant_items||[]).some(v=>variantHit(v,qNow));
  /* 2026-10-29（用户口径）：卡面海报也包 c2-posterwrap + IP 角标——对比钉停靠栏复用卡面 HTML，
     不包的话钉住后海报左上角就不显示 IP 了；品级色变量一并注入，角标色随品级 */
  const ipCard=it.ip_liaison||it.ip_now||"";
  const accCard=GRADE_ACCENT[tier.cls]||GRADE_ACCENT.unknown;
  return `<div class="skin-card grade-${tier.cls}${vFocus?" open":""}"${cidx==null?"":` data-cidx="${esc(String(cidx))}"`}>`+
    `<div class="c2-posterwrap" style="--gc:${accCard[0]};--gsoft:${accCard[1]};--gbg:${accCard[2]}">${renderSkinMedia(it,name)}${ipCard?`<span class="c2-ipbadge">×${esc(ipCard)}</span>`:""}</div>`+`
    <div class="skin-summary" role="button" tabindex="0" aria-expanded="${vFocus?"true":"false"}" onclick="toggleSkin(this)" onkeydown="onSkinKey(event,this)">
      <div class="skin-head-row">
        <span class="skin-tag grade-badge ${tier.cls}" title="level=${esc(it.level!=null?it.level:"未配置")}">${esc(tier.label)}</span>
        <span class="skin-name">${esc(name)}</span>
        <span class="skin-head-right">
          <span class="skin-sale" title="上架时间（sale_ts／sale_date）+ 上架状态">${(()=>{
            const d=it.sale_date,c=saleCountdownCN(it),v=listingOf(it),t=listingShortCN(v);
            const when=d?`上架 ${esc(d)}${c?`（${esc(c)}）`:""}`:(t?"":"上架 未知");
            const st=t?`<span class="skin-ls ${lsClass(v)}" title="上架状态：${esc(lsLabel(v))}">${esc(t)}</span>`:"";
            return when+st;})()}</span>
          <span class="skin-id" title="skin_item_id">皮肤ID ${esc(it.skin_id??it.id)}</span>
        </span>
      </div>
      <div class="skin-facts">${facts.join("")}</div>
      <div class="skin-tags">${tags.join("")}</div>
    </div>
    <div class="skin-detail"${vFocus?"":" hidden"}>${detail}</div>
  </div>`;
}
function toggleSkin(head){
  const card=head.parentElement,detail=card.querySelector(".skin-detail");
  if(!detail)return;
  detail.hidden=!detail.hidden;card.classList.toggle("open",!detail.hidden);
  head.setAttribute("aria-expanded",String(!detail.hidden));
}
function onSkinKey(event,head){
  if(event.key==="Enter"||event.key===" "){event.preventDefault();toggleSkin(head);}
}
/* 官方描述来源 → 中文角标（2026-10-29：新增道具行回填来源） */

function skinDescMark(it){
  const src=it&&it.official_desc_source;
  if(!src)return "";
  const label=DESC_SRC_CN[src]||"历史目录";
  const tip=src==="common_item_data_base_row"
    ?"描述来自同快照 common_item 道具行 desc 字段（CHS 回放），槽位与快照摘要见技术详情"
    :"描述来自用户参考目录（历史整理），非同快照字段直读";
  return `<i class="pres-mark" title="${esc(tip)}">${esc(label)}</i>`;
}
function renderSkinDetail(it,opts){
  // 展开顺序（用户 2026-09-11）：官方描述 → 时限变体 → 表现详情 → 历史参考 → 技术详情
  // opts：noPreview（3D 预览已放左栏）/ noDesc（官方描述已放右栏顶部）——供 D2 方案A 分栏复用
  const parts=[];
  /* 2026-10-18：3D 预览入口只在展开后出现（卡面只放 2D 海报）。 */
  const preview3d=(opts&&opts.noPreview)?"":renderSkinPreview3D(it);
  if(preview3d)parts.push(`<h4>模型预览</h4>${preview3d}`);
  if(!(opts&&opts.noDesc)&&it.official_desc)parts.push(`<h4${opts&&opts.anchor?` id="sec-desc"`:""}>官方描述</h4><div class="skin-desc">${isRichText(it.official_desc)?richText(it.official_desc):esc(it.official_desc)}${skinDescMark(it)}</div>`);
  // 历史参考信息：只输出**有值**的行；全部为空 ⇒ 整块不渲染（不写「—」占位）
  {
    const histRows=[];
    if(it.legacy_grade_label)histRows.push(`<div>旧版品级标签：${esc(it.legacy_grade_label)}　<i class="pres-mark">旧板派生 · 仅历史展示</i></div>`);
    // 枚举/内部码 → 中文；无信息（none/null）直接省略该行
    const HIST_CN={none:"无",name_slot:"名称槽直读",desc_first_map:"描述首句点名",
      derived_from_sale_ts_utc:"由上架时间戳推导",derived_from_sale_ts:"由上架时间戳推导",
      legacy_board:"旧板派生",user_catalog:"用户参考目录",
      canonical_row_field_chs:"名称槽字段直读（主表行）",
      "user-provided-historical-catalog":"用户参考目录",
      "user_catalog_ip":"用户参考目录（联动IP）",
      legacy_board_presentation:"旧板展示层"};
    const _cn=v=>v==null?"":(HIST_CN[String(v)]||String(v));
    const _ne=_cn(it.name_evidence_type), _sd=_cn(it.sale_date_source);
    const _skip=v=>!v||v==="无";
    if(!_skip(_ne)||!_skip(_sd))histRows.push(`<div>${_skip(_ne)?"":`名称证据：${esc(_ne)}`}${(!_skip(_ne)&&!_skip(_sd))?"　":""}${_skip(_sd)?"":`上架日期来源：${esc(_sd)}`}</div>`);
    const _rsRaw=((it.historical_ref||{}).reference_source);
    // 未知内部码不展示原文（可见区禁英文/术语）——只给中文泛称，原文进 title
    const _rs=_rsRaw?(HIST_CN[String(_rsRaw)]||"用户/历史参考"):"";
    if(_rs)histRows.push(`<div>历史目录来源：${esc(_rs)}</div>`);
    if(histRows.length)parts.push(`<h4${opts&&opts.anchor?` id="sec-ref"`:""}>历史参考信息</h4><div class="skin-hist">${histRows.join("")}</div>`);
  }
  if(it.variant_items&&it.variant_items.length)parts.push(`${opts&&opts.anchor?"<div id=\"sec-var\">":""}${renderVariantItems(it.variant_items,it)}${opts&&opts.anchor?"</div>":""}`);
  /* 2026-10-29（用户口径）：表现移入 D2 左栏、音效放右栏描述下方——由 skinD2BodyA 取出单独摆放，
     这里用 noPerf/noAudio 跳过；非 D2（网格卡）仍是原顺序堆叠 */
  const perfDetail=(opts&&opts.noPerf)?"":renderPerfDetail(it);
  const audioDetail=(opts&&opts.noAudio)?"":renderSkinAudio(it);
  if(perfDetail)parts.push(`${opts&&opts.anchor?"<div id=\"sec-perf\">":""}${perfDetail}${opts&&opts.anchor?"</div>":""}`);
  if(audioDetail)parts.push(audioDetail);
  const ref=renderReferenceFields(it.reference_fields,it);
  if(ref)parts.push(ref);
  {const skel=renderSkinSkeleton(it);
   if(skel)parts.push(`<details class="tech"><summary>骨骼 / 挂点 / 3D 预览</summary><div class="kv">${skel}</div></details>`);}
  parts.push(`${opts&&opts.anchor?"<div id=\"sec-tech\">":""}${renderTechSection([
    ["表现条目顺序与文本口径","条目按固定业务顺序展示（命中效果/击败特效/伤害跳字/攻击弹道·挥砍/战斗音效/攻击准心/特殊交互/核芯联动/专属战斗动作/专属待机动作/其它）；文本来自 UI 面板名、同快照配置名或行为资源字段，不是皮肤正式名称。"],
    ["skin_id",it.skin_id],["catalog_layer",it.catalog_layer],["model_path",it.model_path],
    ["version_status",it.version_status],["sfx_consensus_state",it.sfx_consensus_state],
    ["official_name_status",it.official_name_status],["reference_fields",it.reference_fields],
    ["field_provenance",it.field_provenance],["provenance",effProv(it)],["source",it.source],
    ["asset_paths",(it.behavior_resources||[]).map(r=>`${BEHAVIOR_FIELD_CN[r.field]||r.field}: ${r.path}`)],
  ])}${opts&&opts.anchor?"</div>":""}`);
  return dropEmptySections(parts.join(""));
}
// 战斗表现面板：SFX 行即战斗表现（同源）。类目在左、名字在右（与游戏 UI 一致）。
const COMBAT_ORDER=[3,4,10,6,7,9,14,13];

function isWeakName(n){const t=String(n==null?"":n).trim();return !t||/^(未装配|未命名|占位|暂无|无$|待定)/.test(t)||/未命名|占位|未配置/.test(t)||["跳字","音效","弹道","准星","核芯联动","特殊切换","蓄力","命中","战斗动作","休闲待机","切枪动画","专属动作","专属待机","待机","动作","皮肤特效","特殊待机"].indexOf(t)>=0;}
function renderSfxChildren(children){
  if(!Array.isArray(children)||!children.length)return "";
  return `<section class="sfx-children"><div class="sfx-children-title">表现子项（${children.length}）</div>`+
    children.map(child=>{
      /* 本次热更的表现行没有 CHS 文本（child.text_status=no_chs_text）⇒ 标签直接用配置类目中文，
         不再输出「未命名 SFX 配置」这类占位词（口径：无值项不写占位，也不把类目名当正式名）。 */
      let label=String(child.display_name||child.sfx_name||"").trim();
      const catOnly=!label;
      if(catOnly)label=String(child.sfx_type_label||"").replace(/（\d+）$/,"")||"表现配置";
      const weak=!catOnly&&/^(未装配|未命名|占位)/.test(label);
      const type=child.sfx_type_label||(`类型 ${child.sfx_type??"未配置"}`);
      const tip=catOnly?` title="该表现行本次热更无文本名（按配置类目显示）"`:(child.sfx_params?` title="${esc(child.sfx_params)}"`:"");
      const cls=weak?"sfx-child weak":"sfx-child";
      if(weak)label="（"+label+"）";
      return `<div class="${cls}"${tip}><div class="sfx-child-name">${esc(label)}</div><div class="sfx-child-meta">${esc(type)} · 行 ${esc(child.row_key)}</div></div>`;
    }).join("")+
    `</section>`;
}
function renderReferenceFields(ref,cur){
  if(!ref||typeof ref!=="object")return "";
  const pairs=[];
  // 仅保留当前无法直接读取的历史事实：曾用名、版本状态
  const curName=(cur&&(cur.name||cur.display_name))||"";
  if(ref.name&&curName&&ref.name!==curName)pairs.push(["历史曾用名",ref.name]);
  else if(ref.name&&!curName)pairs.push(["历史整理参考名",ref.name]);
  if(!pairs.length)return "";
  return `<section class="reference"><div class="reference-title">历史参考（曾用名）</div>`+
    pairs.map(([k,v])=>`<div class="kv"><div class="k">${esc(k)}</div><div class="v">${esc(v)}</div></div>`).join("")+`</section>`;
}

function renderBehaviorResources(resources){
  if(!Array.isArray(resources)||!resources.length)return "";
  const rows=resources.map(r=>{
    const cn=BEHAVIOR_FIELD_CN[r.field]||FIELD_CN[r.field]||"表现资源";
    return `<div class="behavior-resource" title="${esc(r.path)}"><span class="br-cn">${esc(cn)}</span><span class="br-path">已配置</span></div>`;
  }).join("");
  return `<section class="behavior-resources"><div class="behavior-resources-title">行为资源（武器特效路径配置）</div>${rows}</section>`;
}
// 时限变体 = 主卡内的附属信息：紧凑列表，不生成子卡，只展示与主项不同的字段
function variantDurationLabel(v){
  const src=String(v.display_name||v.name||"");
  const m=src.match(/（(\d+)天）/);
  if(m)return m[1]+"天版";
  return "时限版";
}
function variantDiffChips(v,main){
  const chips=[];
  if(v.grade&&main&&v.grade!==main.grade)chips.push(`品级 ${esc(v.grade)}`);
  if(v.weapon_type_label&&main&&v.weapon_type_label!==main.weapon_type_label)chips.push(`武器类型 ${esc(v.weapon_type_label)}`);
  const vDate=v.sale_date||(v.sale_ts?new Date(v.sale_ts*1000).toLocaleDateString("zh-CN"):"");
  const mDate=(main&&(main.sale_date||(main.sale_ts?new Date(main.sale_ts*1000).toLocaleDateString("zh-CN"):"")))||"";
  if(vDate&&vDate!==mDate)chips.push(`上架时间 ${esc(vDate)}`);
  const vn=String(v.name||"");
  if(vn){
    const base=String((main&&(main.name||main.display_name))||"");
    if(vn.replace(/（[^）]*）/g,"")!==base)chips.push(`名 ${esc(vn)}`);
  }
  if(Array.isArray(v.sfx_items)&&v.sfx_items.length)chips.push(`${v.sfx_items.length} 项表现`);
  if(v.behavior_resources&&v.behavior_resources.length)chips.push(`${v.behavior_resources.length} 项行为资源`);
  if(v.official_name_status==="no_item_row")chips.push("无道具行");
  return chips;
}
function variantHit(v,q){
  if(!q)return false;
  return String(v.skin_id).includes(q)||String(v.display_name||v.name||"").toLowerCase().includes(q);
}
function renderVariantItems(variants,main){
  if(!Array.isArray(variants)||!variants.length)return "";
  const q=String((DATA&&DATA._query)||"");
  let anyHit=false;
  const rows=variants.map(v=>{
    const hit=variantHit(v,q);if(hit)anyHit=true;
    const tech=[`时限皮肤 ID ${v.skin_id}`,`永久皮肤 ${v.permanent_skin_id}`,
      v.model_path?`模型 ${v.model_path}`:"",v.version_status?`版本状态 ${v.version_status}`:"",
      v.variant_relation_rule?`关系依据 ${v.variant_relation_rule}`:""].filter(Boolean).join(" ｜ ");
    return `<li class="vv-row${hit?" vv-hit":""}" data-vid="${esc(v.skin_id)}" title="${esc(tech)}">`+
      `<span class="vv-dur">${esc(variantDurationLabel(v))}</span>`+
      `<span class="vv-id">ID ${esc(v.skin_id)}</span>`+
      variantDiffChips(v,main).map(c=>`<span class="vv-chip">${c}</span>`).join("")+`</li>`;
  }).join("");
  return `<details class="vv"><summary>时限变体 ${variants.length}</summary><ul class="vv-list">${rows}</ul></details>`;
}
function referenceTitle(ref){
  return ref&&ref.name?`<div class="reference-name">历史整理参考：${esc(ref.name)}</div>`:"";
}
// 候选板时限变体：紧凑行（期限版 · 时限皮肤ID · 仅与父项不同的字段）；不生成子卡、不重复父项内容。
// 每条时限记录自身的静态/审计字段保留在「时限变体逐记录」折叠区，技术板仍可逐条追溯。
function renderTimedVariants(variants,main){
  if(!Array.isArray(variants)||!variants.length)return "";   // 空块不渲染
  const q=String((DATA&&DATA._query)||"");
  let anyHit=false;
  const rows=variants.map(v=>{
    const hit=!!q&&String(v.skin_id).includes(q); if(hit)anyHit=true;
    const chips=[];
    if(v.grade&&v.parent_grade&&v.grade!==v.parent_grade)chips.push(`品级 ${esc(v.grade)}`);
    if(v.weapon_type_label&&v.parent_weapon_type_label&&v.weapon_type_label!==v.parent_weapon_type_label)chips.push(`武器种类 ${esc(typeCN(v.weapon_type_label))}`);
    const vd=v.sale_ts?new Date(v.sale_ts*1000).toLocaleDateString("zh-CN"):"";
    const pd=v.parent_sale_ts?new Date(v.parent_sale_ts*1000).toLocaleDateString("zh-CN"):"";
    if(vd&&vd!==pd)chips.push(`上架时间 ${esc(vd)}`);
    // 名称只在「去掉期限后缀后确实不同」时才显示，避免重复父项名称
    const stripDur=s=>String(s||"").replace(/[（(][^）)]*[)）]/g,"").trim();
    const vn=stripDur(v.candidate_name),mn=stripDur(main&&main.candidate_name);
    if(vn&&vn!==mn)chips.push(`名 ${esc(vn)}`);
    const tech=[`时限皮肤ID ${v.skin_id}`,`永久皮肤ID ${v.permanent_skin_id}`,
      v.variant_relation_state?`关系依据 ${v.variant_relation_state}`:""].filter(Boolean).join(" ｜ ");
    return `<li class="vv-row${hit?" vv-hit":""}" data-vid="${esc(v.skin_id)}" title="${esc(tech)}">`+
      `<span class="vv-dur">${esc(v.duration_label)}</span>`+
      `<span class="vv-id">ID ${esc(v.skin_id)}</span>`+
      chips.map(c=>`<span class="vv-chip">${c}</span>`).join("")+`</li>`;
  }).join("");
  const audit=variants.map(v=>{
    const r=v.record||{};
    const sf=r.static_fields||{};
    const pairs=[["时限皮肤ID",v.skin_id],["永久皮肤ID",v.permanent_skin_id],
      ["等级 level",sf.level],["优先级 priority",sf.priority],["legacy 品级标签（board 派生 · 仅历史展示）",sf.legacy_grade_label],
    ["武器种类",sf.weapon_type_label],["上架时间",sf.sale_ts],
      ["名称状态",r.name_status],["身份状态",r.identity_status],["数据等级",r.publication_tier],
      ["模型",sf.model_path],["结构记录键",r.structural_record_key],["来源层",r.source_record_layer]];
    return `<div class="vv-audit"><div class="vv-audit-id">时限皮肤 ID ${esc(v.skin_id)}</div><div class="kv">`+
      pairs.filter(([,x])=>x!==null&&x!==undefined&&x!=="").map(([k,x])=>`<div class="k">${esc(k)}</div><div class="v">${esc(fmtVal(k,x))}</div>`).join("")+
      `</div></div>`;
  }).join("");
  return `<details class="vv"><summary>时限变体 ${variants.length}</summary><ul class="vv-list">${rows}</ul>`+
    `<details class="vv-tech"><summary>时限变体逐记录（技术 / 审计字段）</summary><div class="vv-audit-list">${audit}</div></details></details>`;
}
function renderCandidateSfxChildren(children){
  if(!Array.isArray(children)||!children.length)return "";
  return `<section class="sfx-children"><div class="sfx-children-title">SFX 静态子项（${children.length}；文本不是皮肤正式名）</div>`+
    children.map(child=>{
      const sf=child.static_fields||{};
      const label=child.sfx_static_text||"未命名 SFX 配置";
      const type=sf.sfx_type_label||(`类型 ${sf.sfx_type??"未配置"}`);
      const tip=sf.sfx_params?` title="${esc(sf.sfx_params)}"`:"";
      return `<div class="sfx-child"${tip}><div class="sfx-child-name">${esc(label)}</div>`+
        `<div class="sfx-child-meta">${esc(type)} · ${esc(child.structural_record_key||"")} · identity unresolved</div></div>`;
    }).join("")+`</section>`;
}
function renderCandidatePairs(title,obj){
  if(!obj||typeof obj!=="object")return "";
  const rows=Object.entries(obj).filter(([,v])=>v!==null&&v!==""&&!(Array.isArray(v)&&!v.length));
  if(!rows.length)return "";
  return `<section class="reference"><div class="reference-title">${esc(title)}</div>`+
    rows.map(([k,v])=>`<div class="kv"><div class="k">${esc(FIELD_CN[k]||k)}</div><div class="v">${esc(fmtVal(k,v))}</div></div>`).join("")+`</section>`;
}
function renderCandidateSkinCard(it,cidx){
  // 玩家图鉴优先展示：candidate_name > 未命名皮肤 · ID；候选名不得升级为 verified
  const dispName=it.name_display||it.candidate_name||("未命名皮肤 · ID "+(it.structural_record_key||it.id));
  const candStatus=it.name_status||(it.candidate_name?"candidate":"unresolved");
  const candTier=gradeTier({level:pick(it,"level")});
  const candType=pick(it,"weapon_type_label");
  const candVariants=Array.isArray(it.timed_variants)?it.timed_variants:[];
  const candQuery=String((DATA&&DATA._query)||"");
  const candVFocus=!!candQuery&&candVariants.some(v=>String(v.skin_id).includes(candQuery));
  const variantBlock=candVariants.length?renderTimedVariants(candVariants,it):"";
  const candidate=it.candidate_name?`<div class="reference-name">候选名来源：历史整理参考表（未核验，非正式身份）</div>`:"";
  const ui=(it.ui_short_name_candidates||[]).map(x=>`<div class="reward"><div class="r-name">${esc(x.text)}</div><div class="r-meta">${esc(x.status||"candidate")} · 非正式皮肤名</div></div>`).join("");
  const uiSection=ui?`<section class="rewards"><div class="rewards-title">UI / 战斗表现短名候选</div>${ui}</section>`:"";
  const entry=it.source_entry||{};
  const sourceEntry=entry.package?`<div class="skin-row mono">${esc(entry.package)} · 条目号 ${esc(entry.entry_index)} · 文件标识 ${esc(entry.file_id)}</div>`:"";
  return `<div class="skin-card${candVFocus?" open":""}"${cidx==null?"":` data-cidx="${esc(String(cidx))}"`}><div class="skin-summary" role="button" tabindex="0" aria-expanded="${candVFocus?"true":"false"}" onclick="toggleSkin(this)" onkeydown="onSkinKey(event,this)">
      <div class="skin-top"><div><div class="skin-name">${esc(dispName)}</div>${candidate}</div><div class="skin-id">${esc(it.id)}</div></div>
      <div class="skin-tags"><span class="skin-tag grade-badge ${candTier.cls}" title="level=${esc(pick(it,"level")!=null?pick(it,"level"):"未配置")}">${esc(candTier.label)}</span>${candType?`<span class="skin-tag" title="weapon_type_label">武器种类 ${esc(typeCN(candType))}${pick(it,"weapon_type_state")==="candidate_asset_path_convention"?"（候选·资源路径推导）":""}</span>`:""}${candStatus==="candidate"?`<span class="skin-tag name-candidate" title="name_status">名称待确认</span>`:`<span class="skin-tag name-unresolved" title="name_status">未命名</span>`}${candVariants.length?`<span class="skin-tag" title="时限变体（并入本卡，不单独成卡）">时限变体 ${candVariants.length}</span>`:""}${it.sfx_items&&it.sfx_items.length?`<span class="skin-tag">${it.sfx_items.length} 项表现（特效）</span>`:""}</div>
    </div><div class="skin-detail"${candVFocus?"":" hidden"}>
      ${variantBlock}${uiSection}${renderBehaviorResources(it.behavior_resources)}${renderCandidateSfxChildren(it.sfx_items)}
      <details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary>${sourceEntry}
        ${renderCandidatePairs("静态配置字段",it.static_fields)}
        ${renderCandidatePairs("历史参考字段（候选）",it.candidate_reference_fields)}
        <div class="kv"><div class="k" title="source">来源说明</div></div><div class="kv"><div class="k">审计明细</div><div class="v"><a href="board.html?b=weapon_skin_static_candidates_v01">武器皮肤 · 静态候选（隐藏审计板 · 逐记录）</a></div></div><div class="v">${esc(it.source)}</div></div></details>
    </div></div>`;
}
function typeCN(label){return String(label||"").replace(/（\d+）$/,"");}
function fillOptions(sel,values,label,key,counts){
  sel.innerHTML="";
  const all=document.createElement("option");all.value="";all.textContent=label;sel.appendChild(all);
  for(const value of values){const option=document.createElement("option");option.value=String(value);
    let base=String((key&&VALUE_CN[key]&&VALUE_CN[key][value])||zhText(value));
    if(key==="grade")base=base.replace(/级$/,"");   // 品级展示去掉尾部"级"（只改文案，不动值）
    const n=counts&&counts[value]!=null?`（${counts[value]}）`:"";
    option.textContent=base+n;sel.appendChild(option);}
}
/* 品级筛选（2026-09-19，用户要求）：**控件仍是"一个下拉"，点开列表后在里面勾选（可多选）**。
   语义：勾 0 个 = 全部；勾 N 个 = 命中其中任一即显示（OR）。
   值仍沿用 canonical level / legacy grade 的字符串（不改数据口径，只换控件）。 */
let GRADE_SELECTED=new Set();   // 模块级勾选状态（面板重建时不丢）
function fillGradeGroup(box,values,label,key,counts){
  const panel=box&&box.querySelector("#fGradePanel");
  if(!panel)return;
  panel.innerHTML="";
  for(const value of values){
    const cbId="fgcb_"+String(value).replace(/[^0-9A-Za-z_-]/g,"_");
    /* ★ 行元素用 <div> 而不是 <label>：board_shadcn.css 里有针对 label 的全局规则
       （曾把行撑成全宽、复选框贴左文字贴右 ⇒ 面板被拉宽，用户已看到该故障）。
       用 div + 显式 inline 样式，并逐项钉死宽度/对齐，避免再被全局规则影响。 */
    const row=document.createElement("div");
    row.style.cssText="display:flex;flex-direction:row;align-items:center;justify-content:flex-start;"
      +"gap:8px;width:100%;box-sizing:border-box;font-size:12.5px;line-height:1.5;color:#3f3f46;"
      +"padding:5px 8px;border-radius:7px;cursor:pointer;white-space:nowrap;text-align:left";
    row.addEventListener("mouseenter",()=>{row.style.background="#f4f4f5";});
    row.addEventListener("mouseleave",()=>{row.style.background="transparent";});
    const cb=document.createElement("input");
    cb.type="checkbox";cb.id=cbId;cb.name="fGrade";cb.value=String(value);
    cb.checked=GRADE_SELECTED.has(String(value));
    cb.style.cssText="margin:0;flex:0 0 auto;width:14px;height:14px;accent-color:#6d28d9;cursor:pointer";
    let base=String((key&&VALUE_CN[key]&&VALUE_CN[key][value])||zhText(value));
    if(key==="grade")base=base.replace(/级$/,"");
    const n=counts&&counts[value]!=null?`（${counts[value]}）`:"";
    const txt=document.createElement("span");
    txt.textContent=base+n;
    txt.style.cssText="flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis";
    row.appendChild(cb);row.appendChild(txt);
    /* 点行（非复选框本身）切换勾选，并派发 change 让容器的监听器统一处理 */
    row.addEventListener("click",function(e){
      if(e.target===cb)return;
      cb.checked=!cb.checked;
      cb.dispatchEvent(new Event("change",{bubbles:true}));
    });
    panel.appendChild(row);
  }
  updateGradeBtnLabel();
}
/* 按钮文案：品级：全部 / 品级：典藏 / 品级：典藏、传世 / 品级：典藏、传世 等4项 */
function updateGradeBtnLabel(){
  const lab=document.getElementById("fGradeLabel");
  if(!lab)return;
  if(!GRADE_SELECTED.size){lab.textContent="品级：全部";return;}
  const txt=[...GRADE_SELECTED].map(v=>String((VALUE_CN.level&&VALUE_CN.level[v])||zhText(v)).replace(/级$/,""));
  lab.textContent="品级："+(txt.length<=2?txt.join("、"):(txt.slice(0,2).join("、")+" 等"+txt.length+"项"));
}
/* 读取当前勾选的品级集合（空集 = 全部） */
function readGradeChecked(){
  const panel=document.getElementById("fGradePanel");
  if(panel)return new Set([...panel.querySelectorAll('input[type=checkbox]:checked')].map(x=>x.value));
  return GRADE_SELECTED;
}
function fillFilterSelects(items){
  // ★ 时装板走自己的筛选模组（frBuildFilters）：这里直接隐藏武器/皮肤系列的筛选与排序控件，
  //   否则「level」字段会让 skinLike 判真，凭空长出 品级/武器种类/上架状态 这些无意义下拉。
  if(FASHION_BOARD||VEHICLE_BOARD||CHIP_BOARD){
    ["fGrade","fType","fIp","fRelease","fNameSt","fOrder","fDir"].forEach(id=>{
      const el=document.getElementById(id);if(el)el.style.display="none";
    });
    const sh=document.getElementById("sortHint");if(sh)sh.style.display="none";
    const lh=document.getElementById("listingHint");if(lh)lh.style.display="none";
    const wrap=document.getElementById("fCustomWrap");if(wrap)wrap.innerHTML="";
    if(DATA)DATA._custFilters=[];
    return;
  }
  // 板级自定义筛选（meta.filters 配置）：与武器皮肤筛选模组解耦
  const cfg=DATA.meta&&Array.isArray(DATA.meta.filters)?DATA.meta.filters:null;
  const oSel=document.getElementById("fOrder");
  // 核芯卡排序控件独立于筛选（meta.filters 不隐藏它）
  const nucleusSort=items.some(it=>it.sort_660);
  if(nucleusSort){
    oSel.innerHTML=`<option value="new" selected>排序：新出在前</option><option value="old">排序：旧出在前</option>`;
    oSel.selectedIndex=0;oSel.style.display="";
  }
  // 期次板时间排序（items 带 period_date=按活动期次时间排；默认近期到早期）
  const timeSort=!nucleusSort&&items.some(it=>it.period_date);
  if(timeSort){
    oSel.innerHTML=`<option value="new" selected>排序：近期到早期</option><option value="old">排序：早期到近期</option>`;
    oSel.selectedIndex=0;oSel.style.display="";
    const gSel=document.getElementById("fGrade"),tSel=document.getElementById("fType"),
          iSel=document.getElementById("fIp"),wrap=document.getElementById("fCustomWrap"),
          relSel2=document.getElementById("fRelease"),nsSel2=document.getElementById("fNameSt");
    gSel.style.display=tSel.style.display=iSel.style.display=relSel2.style.display=nsSel2.style.display="none";
    wrap.innerHTML="";DATA._custFilters=[];
    return;
  }
  const gSel=document.getElementById("fGrade"),tSel=document.getElementById("fType"),
        iSel=document.getElementById("fIp"),relSel=document.getElementById("fRelease"),
        nsSel=document.getElementById("fNameSt"),
        wrap=document.getElementById("fCustomWrap");
  wrap.innerHTML="";DATA._custFilters=[];
  if(cfg&&cfg.length){
    gSel.style.display=tSel.style.display=iSel.style.display=relSel.style.display=nsSel.style.display="none";
    if(!nucleusSort)oSel.style.display="none";
    cfg.forEach((f,ix)=>{
      const set=new Set();
      items.forEach(it=>{const v=it[f.key];if(v!=null&&String(v)!=="")set.add(String(v));});
      if(!set.size)return;
      const sel=document.createElement("select");
      const GRADE_ORDER=["极品","高级","中级","基础"];
      let vals=[...set].sort();
      if(f.key==="grade_name"||f.key==="grade_clean"||f.key==="grade_label"){
        vals=vals.sort((a,b)=>{
          const ia=GRADE_ORDER.findIndex(g=>String(a).includes(g));
          const ib=GRADE_ORDER.findIndex(g=>String(b).includes(g));
          return (ia<0?99:ia)-(ib<0?99:ib);
        });
      }
      if(f.key==="month")vals.reverse();
      /* 核芯属性筛选：固定 火/冰/酸/电 顺序 */
      if(f.key==="element")vals=["火","冰","酸","电"].filter(e=>set.has(e));
      fillOptions(sel,vals,"全部"+zhText(f.label||FIELD_CN[f.key]||f.key),f.key);
      const dv=(DATA.meta.filter_defaults||{})[f.key];
      if(dv!=null&&[...sel.options].some(o=>o.value===dv))sel.value=dv;
      sel.setAttribute("aria-label",zhText(FIELD_CN[f.key]||f.label||f.key));
      sel.onchange=render;
      wrap.appendChild(sel);
      DATA._custFilters.push({key:f.key,sel});
    });
    return;
  }
  const skinLike=items.some(it=>pick(it,"level")!=null||pick(it,"weapon_type_label"));
  document.getElementById("sortHint").style.display="none";
  const dirEl0=document.getElementById("fDir");
  if(!skinLike){gSel.style.display=tSel.style.display=iSel.style.display=relSel.style.display=nsSel.style.display=oSel.style.display="none";if(dirEl0)dirEl0.style.display="none";return;}
  gSel.style.display=tSel.style.display=iSel.style.display=relSel.style.display=nsSel.style.display=oSel.style.display="";
  if(items.some(it=>it.sort_660)){
    // 核芯卡：默认新出在前（660 编号降序）
    oSel.innerHTML=`<option value="new" selected>排序：新出在前</option><option value="old">排序：旧出在前</option>`;
    oSel.selectedIndex=0;
  } else if(items.some(it=>pick(it,"level")!=null||pick(it,"weapon_type_label")||pick(it,"sale_ts"))){
    // 武器皮肤图鉴 / 静态候选：排列依据与方向分开（排列依据=皮肤ID / 上架时间）。
    // 本快照无可靠图鉴顺序字段（catalog_order/collection_order/sort_order/图鉴序号 全空，
    // priority 只有 16 个去重值=分级不是顺序）→ 不提供「图鉴顺序」项，也不拿名称/sale_ts/ID 伪造，
    // 默认「皮肤 ID ↓」（顶层只有永久主记录；时限变体并入主卡、不参与顶层排列）。
    document.getElementById("sortHint").textContent="排列依据：无可靠图鉴顺序字段 → 默认皮肤 ID ↓（顶层仅永久主记录；时限变体并入主卡、不参与排列）";
    document.getElementById("sortHint").style.display="";
    oSel.innerHTML=`<option value="id" selected>排列依据：皮肤 ID</option><option value="sale">排列依据：上架时间</option><option value="charm">排列依据：魅力值</option>`;
    oSel.selectedIndex=0;
    const dirEl=document.getElementById("fDir");
    if(dirEl&&!dirEl.dataset.dir){dirEl.dataset.dir="desc";dirEl.textContent="↓ 降序";}
    if(dirEl)dirEl.style.display="";
  } else {
    oSel.innerHTML=`<option value="gallery">排序：游戏图鉴序列</option><option value="id">排序：皮肤ID</option><option value="charm">排序：魅力值</option>`;
  }
  // 五路独立筛选（真实枚举生成，可任意组合；与排序互不干扰）
  const grades=new Set(),types=new Set(),ips=new Set(),rels=new Set(),nsts=new Set();
  const relCounts={},nsCounts={},gradeCounts={};
  items.forEach(it=>{
    // 品级筛选：优先 canonical level；legacy 板没有 level 时退回其自带 grade（仅该板展示用）
    const lv=pick(it,"level"),gRaw=pick(it,"grade");
    const tKey=(gRaw!=null&&gRaw!=="")?String(gRaw):(lv!=null?String(lv):null);
    if(tKey!=null){grades.add(tKey);gradeCounts[tKey]=(gradeCounts[tKey]||0)+1;}
    const wt=pick(it,"weapon_type_label");
    if(wt)types.add(typeCN(wt));
    const ipv=pick(it,"ip_now")||pick(it,"ip_liaison");   // legacy=ip_now；canonical=ip_liaison（展示层）
  if(ipv)ips.add(ipv);
    const ls=listingOf(it);if(ls){rels.add(ls);relCounts[ls]=(relCounts[ls]||0)+1;}
    const nsv=nameStatusOf(it);nsts.add(nsv);nsCounts[nsv]=(nsCounts[nsv]||0)+1;
  });
  // 「（无联动）」只在确实存在联动与非联动混合时提供，避免整板无联动数据时出现空筛选
  if(ips.size&&items.some(it=>!(pick(it,"ip_now")||pick(it,"ip_liaison"))))ips.add("（无联动）");
  const fill=(sel,set,allLabel,mapKey,counts)=>{
    fillOptions(sel,[...set].sort((a,b)=>String(a).localeCompare(String(b),"zh-CN",{numeric:true})),allLabel,mapKey,counts);
    // 该维度没有真实值 → 不显示空下拉（如候选板无联动IP）
    if(sel.options.length<=1)sel.style.display="none";
  };
  // 品级筛选：**勾选制（可多选）**，不再是单选下拉；未勾选 = 全部
  const gradeSorted=[...grades].sort((a,b)=>String(a).localeCompare(String(b),"zh-CN",{numeric:true}));
  fillGradeGroup(gSel,gradeSorted,"品级","level",gradeCounts);
  gSel.style.display=grades.size?"":"none";
  fill(tSel,types,"全部武器种类");
  fill(iSel,ips,"全部联动IP");
  // 两个状态筛选：**只要行里有该字段就显示**（不再用 options.length 这种 HTML-only 判定，
  // 否则真实浏览器外的环境/缓存差异会让下拉"消失"，表现为"筛选不可用"）
  fill(relSel,rels,"全部上架状态","listing_status",relCounts);
  fill(nsSel,nsts,"全部名称状态","name_status",nsCounts);
  relSel.style.display=rels.size?"":"none";
  nsSel.style.display=nsts.size?"":"none";
  const relHint=document.getElementById("listingHint");
  if(relHint){
    const vs=listingSupported();
    relHint.style.display="none";
    if(!rels.size){
      relHint.textContent="上架状态：本板行内没有上架状态字段（listing_status / release_state 均缺失）→ 不提供该筛选";
      relHint.style.display="";
    } else if(rels.size===1&&vs&&vs.supported_today){
      const only=[...rels][0];
      relSel.title="canonical listing_status 当前支持类别："+vs.supported_today.join("、")
        +((vs.evidence_state&&vs.evidence_state.note)?("；"+vs.evidence_state.note):"");
      relHint.textContent="上架状态：仅 "+vs.supported_today.map(x=>LISTING_CN[x]||x).join("、")
        +"（canonical 字段；同快照无 sale/shop/exchange 证据，不伪造分类）";
      relHint.style.display="";
    }
  }
}
function renderItemCard(it){
  const rows=Object.entries(it)
    .filter(([k,v])=>!FIXED.has(k)&&v!==null&&v!=="")
    .map(([k,v])=>`<div class="k">${esc(FIELD_CN[k]||k)}</div><div class="v">${esc(fmtVal(k,v))}</div>`);
  const media=renderItemMedia(it._media);
  return `<div class="i">${media}<div class="i-head">
    <div><div class="i-name">${esc(it.name||it.display_name||it.id)}</div>
    <div class="i-id" title="id">道具ID ${esc(it.item_id??it.id)}</div></div>
    <span class="head-tags"><span class="ev ${it.evidence}">${EV_CN[it.evidence]||it.evidence}</span>${renderStateTags(it.status_tags)}</span></div>
    <div class="kv">${rows.join("")}</div>
    ${renderTechSection([["provenance",effProv(it)],["field_provenance",it.field_provenance],["source",it.source],["evidence_level",it.evidence_level],["status_tags",it.status_tags]])}</div>`;
}
/* 时装图标（游戏内真实引用）：最多显示 6 张，其余计数；无资源时用客户端占位图 */
function renderItemMedia(m){
  if(!m)return "";
  /* 2026-10-30：动态头像 / 头像框 / 名片框 的 APNG 挂在**主图**（role=frame）上。
     卡面默认只显示游戏内静态图，悬停或开详情才换 src 播放 —— 673 张卡不会一进页面就拉 300 个动图。
     ★ 背景图（role=background，名片场景底图）不是边框图，不能挂动图、也不占主图位。 */
  const anim=m.anim?esc(m.anim):"";
  const imgs=(m.images||[]).slice(0,6).map((x,i)=>{
    const bg=(x.role==="background");
    const hot=(anim&&i===0&&!bg);
    return `<figure class="mi${hot?" mi-anim":""}${bg?" mi-bg":""}"><img src="${esc(x.png)}" alt="${esc(x.base||x.suffix||"")}" loading="lazy"${hot?` data-anim="${anim}"`:""}>${hot?`<span class="anim-dot" title="有 Spine 动画，悬停播放 / 点开详情自动播放">动</span>`:""}<figcaption>${esc(x.label||x.suffix||"raw")}</figcaption></figure>`;
  }).join("");
  const ph=m.placeholder?`<figure class="mi ph"><img src="${esc(m.placeholder)}" alt="客户端占位图" loading="lazy"><figcaption>占位</figcaption></figure>`:"";
  /* 边框图在当前包快照里确实缺失 → 如实占位，不用场景图顶替 */
  const nofig=(m.frame_status==="missing")?`<figure class="mi nofig"><span>边框图缺失<br>（当前包快照无该资源）</span><figcaption>缺口</figcaption></figure>`:"";
  const more=(m.images||[]).length>6?`<span class="mi-more">+${m.images.length-6}</span>`:"";
  return `<div class="i-media">${nofig}${imgs}${ph}${more}</div>`;
}
/* 2026-10-30：动图播放。全局委托，卡片网格与 D2 灯箱共用一套；
   灯箱内（.c2-stage）放开了就不回退，卡片上移出即还原静态图。 */
function animPlay(img){
  if(!img||!img.dataset.anim||img.dataset.aPlaying)return;
  img.dataset.aStill=img.getAttribute("src");
  img.dataset.aPlaying="1";
  img.src=img.dataset.anim;
}
function animStop(img){
  if(!img||!img.dataset.aPlaying)return;
  delete img.dataset.aPlaying;
  if(img.dataset.aStill)img.src=img.dataset.aStill;
}
function animAutoPlay(root){
  (root||document).querySelectorAll(".mi-anim img[data-anim]").forEach(animPlay);
}
document.addEventListener("mouseover",e=>{
  const fig=e.target&&e.target.closest?e.target.closest(".mi-anim"):null;
  if(fig)animPlay(fig.querySelector("img[data-anim]"));
},true);
document.addEventListener("mouseout",e=>{
  const fig=e.target&&e.target.closest?e.target.closest(".mi-anim"):null;
  if(!fig)return;
  if(fig.closest(".c2-stage"))return;              // 灯箱里保持播放
  if(e.relatedTarget&&fig.contains(e.relatedTarget))return;
  animStop(fig.querySelector("img[data-anim]"));
},true);
/* ════════════════════ 时装模式（仅 board id = fashion_wardrobe）════════════════════
   用户 2026-10-18 口径：
     · 卡面只留「顶部图轨（≤4 张，多的 +N）+ 名字 + 部位 + model_id」
     · 其余字段（描述/品级/魅力/期限/变体名/图标绑定/行键/溯源）全部折进
       「技术详情 / 数据来源 / 审计信息」折叠区
     · 筛选：部位（多选）/ 期限 / 图示 / 性别，与既有搜索 + 证据等级并行
     · 筛选后顶部统计（#count 与 #pills）跟着变
   ★ 类名全部 fr-* 前缀 / 选择器全部挂在 body.fashion-mode 下 —— 武器皮肤板零影响。
   ★ 只用板上已有字段（part_bucket / has_permanent / icon_state / gender 由刷新脚本写入），
     不做任何推断：整套/光源没有图标命名约定就不按前缀判。 */
const FASHION_BOARD=(function(){try{return (getParam("b")||"")==="fashion_wardrobe";}catch(e){return false;}})();
const FR_BUCKETS=["头发","头饰","面饰","衣服","整套","背包","挂饰","荧光棒","投影","半感染者花苞","戒指","捏脸","其他"];
const FR_BUCKET_CLS={"头发":"hair","头饰":"hat","面饰":"face","衣服":"cloth","整套":"suit","背包":"bag","挂饰":"pendant","荧光棒":"light","投影":"proj","其他":"other"};
const FR={parts:new Set(),grade:"",img:"有图",gender:"",sort:"",named:true};
/* 筛选状态可从 URL 预置（可分享的深链）：?frpart=头饰,衣服&frdur=限时&frimg=有图&frgender=女&frsort=charm_desc */
(function(){
  try{
    const u=new URLSearchParams(location.search);
    (u.get("frpart")||"").split(",").map(s=>s.trim()).filter(Boolean).forEach(p=>FR.parts.add(p));
    FR.grade=u.get("frgrade")||"";
    FR.img=(u.get("frimg")===null?"有图":u.get("frimg"));
    const _nv=u.get("frnamed"); FR.named=(_nv===null?true:_nv==="1");
    FR.gender=u.get("frgender")||"";
    FR.sort=u.get("frsort")||"";
  }catch(e){}
})();
function frSyncUrl(){
  try{
    const u=new URLSearchParams(location.search);
    const put=(k,v)=>{if(v)u.set(k,v);else u.delete(k);};
    put("frpart",[...FR.parts].join(","));
    put("frgrade",FR.grade);put("frimg",FR.img);put("frgender",FR.gender);put("frsort",FR.sort);put("frnamed",FR.named?"1":"");
    history.replaceState(null,"",location.pathname+"?"+u.toString());
  }catch(e){}
}
/* 排序（先筛后排）：四个选项
   model_desc = 编号(model_id) 大→小【默认】｜ model_asc 小→大
   charm_desc = 魅力值 高→低      ｜ charm_asc 低→高
   缺失值（无 model / 无魅力）一律排最后；同值时按名字稳定排序 */
function frSortList(list){
  const mode=FR.sort||"model_desc";
  const isCharm=mode.indexOf("charm")===0;
  const asc=/_asc$/.test(mode);
  const val=it=>{
    let v;
    if(isCharm){v=it.charm_value;if(v==null||v===0)return null;}
    else{v=(it.model_id!=null?it.model_id:((it.model_ids||[])[0]));if(v==null||v==="")return null;}
    const n=Number(v);return isNaN(n)?null:n;
  };
  const arr=[...list];
  arr.sort((A,B)=>{
    const a=val(A),b=val(B);
    if(a==null&&b==null)return String(A.name||"").localeCompare(String(B.name||""),"zh-CN");
    if(a==null)return 1;
    if(b==null)return -1;
    if(a!==b)return asc?a-b:b-a;
    return String(A.name||"").localeCompare(String(B.name||""),"zh-CN");
  });
  return arr;
}
function frBuckets(it){
  const b=it&&it.part_bucket;
  if(Array.isArray(b)&&b.length)return b;
  return ["其他"];
}
/* 2026-10-30：性别归一——「仅女款/仅男款」按其实际性别计入筛选，
   否则选「女」会把单性别女款（不湮之花、白月魁等）全部筛掉、选「未标」又选不到。 */
function frGenders(it){
  const g=String((it&&it.gender)||"");
  if(!g)return [];
  if(g==="仅女款")return ["女"];
  if(g==="仅男款")return ["男"];
  return g.split("/");
}
function frPass(it){
  if(FR.parts.size){
    const bs=frBuckets(it);let ok=false;
    FR.parts.forEach(p=>{if(bs.indexOf(p)>=0)ok=true;});
    if(!ok)return false;
  }
  if(FR.grade&&String(it.grade_level==null?"":it.grade_level)!==FR.grade)return false;
  // 运行时特效/面容类「无独立 2D 图标」项：只要选中了它所在部位桶，即展示，不被
  // 「有图/含占位」图示筛选吞掉；默认（未选任何部位，全部视图）仍按图示筛选正常隐藏。
  const _fxNoImg=(it.icon_state||"").indexOf("无2D图")===0;
  const _skipImg=_fxNoImg&&FR.parts.size>0;
  if(!_skipImg){
    if(FR.img==="有图"&&it.icon_state!=="有图")return false;
    if(FR.img==="含占位"&&it.icon_state!=="含占位")return false;
  }
  if(FR.named&&it.name_visible===false)return false;
  if(FR.gender){
    const gs=frGenders(it);
    if(FR.gender==="未标"){ if(gs.length)return false; }
    else if(gs.indexOf(FR.gender)<0) return false;
  }
  return true;
}
/* 图轨：≤4 张真实图标；无图时落客户端占位图（placeholder 是对象，取 .png） */
function frRail(it){
  const m=it._media||{},imgs=Array.isArray(m.images)?m.images:[];
  if(!imgs.length){
    const ph=typeof m.placeholder==="string"?m.placeholder:(m.placeholder&&m.placeholder.png);
    return ph
      ? `<div class="fr-rail"><figure class="ph" title="客户端占位图（图标资源未随客户端下发）"><img src="${esc(ph)}" alt="占位" loading="lazy"></figure></div>`
      : `<div class="fr-rail"><figure class="ph"><span class="fr-dur">无图标</span></figure></div>`;
  }
  const show=imgs.slice(0,4).map((x,i)=>
    `<figure class="fr-zoom" data-idx="${i}" title="${esc((x.base||"")+(x.suffix||""))}"><img src="${esc(x.png)}" alt="${esc(x.base||"")}" loading="lazy"></figure>`).join("");
  const more=imgs.length>4?`<button type="button" class="fr-more fr-zoom" data-idx="4" title="该件共 ${imgs.length} 张图标，点击展开">+${imgs.length-4}</button>`:"";
  return `<div class="fr-rail">${show}${more}</div>`;
}
/* 2026-10-30（用户口径）：所有「能打开详细子卡（D2）」的板，卡面点图片一律开子卡，
   不再开大图；大图入口只保留在 D2 详情内部（点详情里的图才放大）。
   cardOpensD2 = 这张卡所属的板接了 D2 provider —— 网格卡与 .fr-zoom 图轨共用这一判定。 */
function cardOpensD2(card){
  if(!card)return false;
  return (card.classList.contains("chip-card")&&CHIP_BOARD)||
    (card.classList.contains("fcard")&&FASHION_BOARD)||
    (card.classList.contains("vcard")&&VEHICLE_BOARD)||
    (card.classList.contains("skin-card")&&document.body.classList.contains("skin-mode"))||
    (card.classList.contains("nucleus")&&CORE_BOARD)||
    (card.classList.contains("roster"));
}
/* ── 大图查看器（灯箱）：点缩略图或 +N 打开，可左右翻、Esc 关 ── */
const FR_IMGS=Object.create(null);
let FR_DYN_SEQ=0;
/* D2 详情内点任意图片看大图：收集该详情内的全部图片，按点击项定位起点，灯箱可左右翻。
   用于皮肤海报 / 核芯立绘 / 名册头像等「非 .fr-zoom 图轨」的图片。 */
function frOpenIn(scope,img){
  const list=[];let idx=0;
  scope.querySelectorAll("img").forEach(x=>{
    if(x.closest(".c2-side"))return;          /* 左右侧栏缩略图是「切换条目」，不是放大 */
    const src=x.getAttribute("src")||"";
    if(!src||src.slice(0,5)==="data:")return;
    if(x===img)idx=list.length;
    list.push(src);
  });
  if(!list.length)return;
  const key="__d2_"+(++FR_DYN_SEQ);
  FR_IMGS[key]=list;
  frOpen(key,idx);
}
function frOpen(id,idx){
  const list=FR_IMGS[id]||[];
  if(!list.length)return;
  let box=document.getElementById("frBox");
  if(!box){
    box=document.createElement("div");
    box.id="frBox";box.className="fr-box";
    box.innerHTML=`<div class="fr-box-body"><img alt=""><div class="fr-box-bar"><button type="button" data-act="prev">‹</button><span class="fr-box-idx"></span><button type="button" data-act="next">›</button><button type="button" data-act="close">关闭</button></div></div>`;
    box.addEventListener("click",e=>{
      const t=e.target;
      if(t===box||t.dataset.act==="close"){frClose();return;}
      const act=t.dataset.act;
      if(act==="prev"||act==="next"){
        const cur=parseInt(box.dataset.i||"0",10);
        const n=(FR_IMGS[box.dataset.id]||[]).length;
        const ni=(cur+(act==="next"?1:-1)+n)%n;
        frShow(box.dataset.id,ni);
      }
    });
    document.body.appendChild(box);
    document.addEventListener("keydown",e=>{
      if(!document.getElementById("frBox"))return;
      if(e.key==="Escape")frClose();
      else if(e.key==="ArrowLeft"||e.key==="ArrowRight"){
        const evt=new MouseEvent("click",{bubbles:true});
        const sel=e.key==="ArrowLeft"?'[data-act="prev"]':'[data-act="next"]';
        const btn=document.querySelector(sel);
        if(btn)btn.dispatchEvent(evt);
      }
    });
  }
  box.dataset.id=id;box.style.display="flex";
  frShow(id,idx);
}
function frShow(id,i){
  const box=document.getElementById("frBox");if(!box)return;
  const list=FR_IMGS[id]||[];if(!list.length)return;
  const n=list.length;i=(i+n)%n;
  box.dataset.i=String(i);
  box.querySelector("img").src=list[i];
  box.querySelector(".fr-box-idx").textContent=(i+1)+" / "+n;
}
function frClose(){
  const box=document.getElementById("frBox");
  if(box){box.style.display="none";box.querySelector("img").src="";}
}
document.addEventListener("click",e=>{
  const t=e.target.closest?e.target.closest(".fr-zoom"):null;
  if(!t)return;
  const card=t.closest(".fcard");
  const id=card&&card.dataset.frid;
  if(!id)return;
  /* 2026-10-30（用户口径）：能开 D2 子卡的板，卡面点图片一律开子卡，不开大图；
     大图入口只留在 D2 详情内部。网格卡里的 .fr-zoom 直接放行给下面的 D2 打开器。 */
  if(card.closest("#grid")&&cardOpensD2(card))return;
  e.preventDefault();e.stopPropagation();
  frOpen(id,parseInt(t.dataset.idx||"0",10));
},true);
/* 卡面 = 图轨 + 名字 + 部位 + model_id（别的全部进折叠区） */
const FD_OPEN_ALL=(function(){try{return new URLSearchParams(location.search).get('open')==='1';}catch(e){return false;}})();
function fdOpenAll(){
  try{ if(new URLSearchParams(location.search).get('open')!=='1')return; }catch(e){return;}
  document.querySelectorAll('details.fdesc').forEach(d=>d.open=true);
}
function frCard(it,cidx,full){
  const bk=frBuckets(it),bkCn=bk.join(" / ");
  const partCn=(it.all_parts&&it.all_parts.length?it.all_parts.map(p=>COMMON_PART_CN[p]||p).join(" / "):(COMMON_PART_CN[it.part]||it.part||""));
  const mid=(it.model_id!=null)?it.model_id:((it.model_ids&&it.model_ids[0])!=null?it.model_ids[0]:null);
  /* 外观补充卡并入后，主卡同时带短编号（fashion_data）与长编号（player_appear_data） */
  const refs=(it.model_refs||[]).filter(x=>x!=null&&String(x)!==String(mid));
  const cls=FR_BUCKET_CLS[bk[0]]||"other";
  FR_IMGS[it.id]=Array.isArray((it._media||{}).images)?it._media.images.map(x=>x.png):[];
  return `<div class="i fcard" data-frid="${esc(it.id)}"${cidx==null?"":` data-cidx="${esc(String(cidx))}"`}>
    ${frRail(it)}
    <div class="fr-head"><div class="fr-name" title="${esc(it.name||it.id)}">${esc(it.name||it.id)}</div>${
      it.grade_level!=null?`<span class="fr-grade" title="品级：fashion_data.level（表里只有数值档，无官方名）">品级 ${esc(it.grade_level)}</span>`:""}</div>
    <div class="fr-sub">
      <span class="fr-part b-${cls}" title="表的 part_type：${esc(it.part||"（表里无该字段）")}">${esc(partCn||"部位未标注")}</span>
      ${it.gender_scope?`<span class="fr-gender" title="${esc(it.gender_scope_note||it.gender_scope)}">${esc(it.gender||"仅单性别")}</span>`:""}
      <span class="fr-charm${it.charm_value?"":" na"}" title="魅力值：fashion_data.charm_value">${it.charm_value?"魅力 "+esc(it.charm_value):"魅力 —"}</span>
      ${mid!=null?`<span class="fr-model" title="model_id（fashion_data 表）${refs.length?` · 外观编号（player_appear_data）：${refs.join(" / ")}`:""}">model ${esc(mid)}${refs.length?`<span class="fr-ref"> · ${esc(refs[0])}${refs.length>1?`+${refs.length-1}`:""}</span>`:""}</span>`:`<span class="fr-model">model —</span>`}
      ${(()=>{const vm=it.version_merge;if(!vm||!(vm.aliases||[]).length)return "";
        return `<span class="fr-alt" title="同一 model 的另一条记录，已并入本卡：${esc(vm.aliases.join("、"))}">含${esc((vm.prefixes||[]).join("")||"新")}·版</span>`;})()}
      ${(()=>{const vma=it.alias_merge;if(!vma||!(vma.aliases||[]).length)return "";
        const nm=vma.aliases.map(x=>String(x).split("-")[0]).join("、");
        return `<span class="fr-alt fr-alias" title="表里同 model 同一件时装的另一条记录（开发/占位名），已并入本卡：${esc(vma.aliases.join("、"))}">别名 ${esc(nm)}</span>`;})()}
      ${(()=>{const g=(it._media&&it._media.missing)||[];if(!g.length)return "";
        const gs=[...new Set(g.map(x=>x.gender).filter(Boolean))].sort().join("");
        const who=gs==="男女"?"男女":(gs||"");
        return `<span class="fr-gap" title="表里登记了该性别的图标，但 PE/PC/refs 三处都没有这张图">缺${esc(who)}图${g.length>1?` · ${g.length}`:""}</span>`;})()}
    </div>
    ${full?frDetailsHTML(it,frKvHtml(it)):""}
  </div>`;
}
/* 审计键值对：D2 灯箱/停靠栏「技术详情」区专用（网格卡面不再渲染） */
function frKvHtml(it){
  const mid=(it.model_id!=null)?it.model_id:((it.model_ids&&it.model_ids[0])!=null?it.model_ids[0]:null);
  const refs=(it.model_refs||[]).filter(x=>x!=null&&String(x)!==String(mid));
  const durCn=it.duration_state==="unknown"?"期限未知":(it.duration_state==="timed"?"限时":(it.duration_state==="mixed"?"永久+限时":"永久"));
  const durDays=(it.durations||[]).length?`（${it.durations.join("/")}天）`:"";
  const pairs=[];
  if(it.grade_level!=null)pairs.push(["品级",(it.grade_levels&&it.grade_levels.length>1?it.grade_levels.map(gradeLabel).join("/")+"（取最高）":"品级 "+gradeLabel(it.grade_level))]);
  if(it.charm_value!=null)pairs.push(["魅力值",String(it.charm_value)]);
  pairs.push(["期限",durCn+durDays]);
  if((it.time_limited_variants||[]).length)pairs.push(["时限档",it.time_limited_variants.map(d=>d+"天").join(" / ")]);
  pairs.push(["性别",(it.gender||"图标未标性别")]);
  if(it.gender_scope)pairs.push(["性别范围",it.gender_scope+(it.gender_scope_note?(" · "+it.gender_scope_note):"")]);
  pairs.push(["图标",`${it.icon_state||"未知"}${it.icon_count!=null?` · ${it.icon_count} 张`:""}`]);
  /* 2026-11-01：图标有替代/缺口说明时如实列出（例：头饰面饰的男版图缺失、改用同模块女版）。
     原来这类说明只写在数据里没人显示，卡片等于"看着正常但没说清"。 */
  if(it.icon_note)pairs.push(["图标说明",it.icon_note]);
  if(it.icon_missing_reason&&it.icon_state!=="有图")pairs.push(["缺图原因",it.icon_missing_reason]);
  if((it.name_variants||[]).length>1)pairs.push(["表内变体名",it.name_variants.join("、")]);
  const bools=[];
  if(it.fashion_preview)bools.push("可预览");
  if(it.show_no_have)bools.push("未拥有也展示");
  if(it.hide_in_bag)bools.push("背包内隐藏");
  if(bools.length)pairs.push(["展示开关",bools.join(" / ")]);
  if((it.model_ids||[]).length>1)pairs.push(["全部模型ID",it.model_ids.join(" / ")]);
  if(refs.length)pairs.push(["外观编号",refs.join(" / ")]);
  const am=it.appearance_merge;
  if(am&&(am.ids||[]).length)pairs.push(["合并来源",
    `${am.ids.join(" / ")}（${(am.parts||[]).join("/")||"部位未标"}）${am.table?` · ${am.table}`:""}`]);
  const vm=it.version_merge;
  if(vm&&(vm.aliases||[]).length)pairs.push(["同套版本",vm.aliases.join(" / ")+(vm.note?` · ${vm.note}`:"")]);
  const vma=it.alias_merge;
  if(vma&&(vma.aliases||[]).length)pairs.push(["同款别名",vma.aliases.join(" / ")+(vma.note?` · ${vma.note}`:"")]);
  if(vma&&(vma.row_keys||[]).length)pairs.push(["别名行键",vma.row_keys.join(", ")]);
  const dm=it.duration_merge;
  if(dm&&(dm.names||[]).length){
    const nmTxt=dm.names.join(" / ");
    const dTxt=(dm.days||[]).filter(d=>!nmTxt.includes(d+"天")).map(d=>d+"天").join(" / ");
    pairs.push(["并入时限款",nmTxt+(dTxt?`（${dTxt}）`:"")]);
  }
  if(dm&&(dm.row_keys||[]).length)pairs.push(["时限款行键",dm.row_keys.join(", ")]);
  if(vm&&(vm.icon_paths||[]).length)pairs.push(["版本图标",vm.icon_paths.map(p=>String(p).split("/").pop()).join(" / ")]);
  pairs.push(["行键",(it.row_keys||[]).join(", ")]);
  if((it.tables||[]).length)pairs.push(["来源表",it.tables.join(" / ")]);
  const p=effProv(it);
  if(p.source_id)pairs.push(["来源标识",p.source_id]);
  if(p.table)pairs.push(["定位表",p.table]);
  if(p.field_refs)pairs.push(["字段出处",(p.field_refs||[]).join(" / ")]);
  pushFieldSources(p,pairs);
  if(p.source_lock_sha256)pairs.push(["源快照摘要",String(p.source_lock_sha256).slice(0,32)+"…"]);
  if(p.upstream&&p.upstream.entry_index!=null)pairs.push(["上游条目号",String(p.upstream.entry_index)]);
  if(p.locator_chain&&p.locator_chain.chain_status)pairs.push(["定位链",p.locator_chain.chain_status]);
  pairs.push(["证据等级",(EV_CN[it.evidence]||it.evidence||"")+(it.evidence_level?" · "+(VALUE_CN.evidence_level[it.evidence_level]||it.evidence_level):"")]);
  const ros=p.roster;
  if(ros)pairs.push(["证据类型",`名册级（${ros.evidence==="name-roster-only"?"字符串池名册":"静态导出"}）· 无行级溯源`+(ros.source_desc?` · ${ros.source_desc}`:"")]);
  if((it.status_tags||[]).length)pairs.push(["状态标签",it.status_tags.map(t=>STATE_CN[t]||t).join(" / ")]);
  const imgLines=((it._media&&it._media.images)||[]).map(x=>`${x.base}${x.suffix||""}${x.pack?"  ← "+x.pack+(x.row!=null?" row "+x.row:""):""}`);
  if(imgLines.length)pairs.push(["图标绑定",imgLines.join("\n")]);
  const gaps=(it._media&&it._media.missing)||[];
  if(gaps.length)pairs.push(["缺图槽",gaps.map(g=>`${g.base||"?"}${g.gender?`（${g.gender}）`:""}${g.why?" · "+g.why:""}`).join("\n")]);
  if(it._media&&it._media.placeholder&&it._media.placeholder.source)pairs.push(["占位图来源",it._media.placeholder.source+(it._media.placeholder.reason?`（${it._media.placeholder.reason}）`:"")]);
  return pairs.map(([k,v])=>{
    const mono=/(行键|定位表|来源标识|图标绑定|占位图来源|源快照摘要|上游条目号|外观编号|合并来源|全部模型ID|同套版本|版本图标|同款别名|别名行键|并入时限款|时限款行键)/.test(k);
    return `<div class="k">${esc(k)}</div><div class="v${mono?" mono":""}">${v===null||v===undefined?"":esc(String(v))}</div>`;
  }).join("");
}
/* 卡面下方的两个折叠区（详情 + 技术详情）：只在 D2 灯箱/停靠栏里渲染，网格卡面不再出现 */
function frDetailsHTML(it,kv){
  const fdesc=(it.desc||it.desc_note||it.effect_text||it.charm_note||it.reborn_vis!=null||it.back_weapon_vis!=null||(it.hide_parts||[]).length||it.gender||it.gender_scope)
    ?`<details class="fdesc"${FD_OPEN_ALL?" open":""}><summary>详情</summary><div class="fdesc-body">${
        ((it.vehicle_ids||[]).length>1?`<div class="fd-row"><span class="fd-k">全部编号</span><span class="fd-v mono">${it.vehicle_ids.join(" / ")}</span></div>`:"")+
        (it.gender?`<div class="fd-row"><span class="fd-k">性别</span><span class="fd-v">${esc(it.gender)}${it.gender_scope?` · <b>${esc(it.gender_scope)}</b>`:""}</span></div>`:"")+
        (it.gender_scope_note?`<div class="fd-row"><span class="fd-k">性别说明</span><span class="fd-v">${esc(it.gender_scope_note)}</span></div>`:"")+
        (it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${richText(it.desc)}</span></div>`:"")+
        (it.desc_note&&!it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${esc(it.desc_note)}</span></div>`:"")+
        (it.effect_text?`<div class="fd-row"><span class="fd-k">效果</span><span class="fd-v">${esc(it.effect_text)}</span></div>`:"")+
        (it.effect_text?`<div class="fd-row"><span class="fd-k">效果来源</span><span class="fd-v mono">${esc(it.effect_source||"—")}</span></div>`:"")+
        (it.charm_note?`<div class="fd-row"><span class="fd-k">魅力值</span><span class="fd-v">${esc(it.charm_note)}</span></div>`:"")+
        (it.reborn_vis!=null?`<div class="fd-row"><span class="fd-k">隐藏半感染者花苞</span><span class="fd-v">${it.reborn_vis?"是":"否"}</span></div>`:"")+
        ((it.hide_parts||[]).map(x=>`<div class="fd-row"><span class="fd-k">隐藏${esc(x)}</span><span class="fd-v">是</span></div>`).join(""))+
        (it.back_weapon_vis!=null?`<div class="fd-row"><span class="fd-k">隐藏副武器</span><span class="fd-v">${it.back_weapon_vis?"是":"否"}</span></div>`:"")
      }</div></details>`:"";
  return fdesc+`<details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="fr-kv">${kv}</div></details>`;
}
/* 折叠时显示描述的前一小段，展开看全文 */
function frDescHead(desc){
  const t=String(zhText(desc)).replace(/\s+/g," ").trim();
  return t.length>22?("描述 · "+t.slice(0,22)+"…"):("描述 · "+t);
}

/* 筛选控件：部位多选 + 期限/图示/性别单选；计数按全量板算（不随其它筛选浮动，避免误读） */
function frBuildFilters(items){
  const wrap=document.getElementById("fFashionWrap");
  if(!wrap)return;
  const cnt={parts:{},grade:{},img:{},gender:{}};
  for(const b of FR_BUCKETS)cnt.parts[b]=0;
  for(const it of items){
    frBuckets(it).forEach(b=>{if(cnt.parts[b]!=null)cnt.parts[b]++;});
    const gk=(it.grade_level==null)?"未标":String(it.grade_level);
    cnt.grade[gk]=(cnt.grade[gk]||0)+1;
    cnt.img[it.icon_state||"未知"]=(cnt.img[it.icon_state||"未知"]||0)+1;
    const _gs=frGenders(it);
    if(_gs.length)_gs.forEach(g=>{cnt.gender[g]=(cnt.gender[g]||0)+1;});
    else cnt.gender["未标"]=(cnt.gender["未标"]||0)+1;
  }
  const chip=(label,on,n,fn)=>{
    const b=document.createElement("button");
    b.type="button";b.className="fr-chip";b.textContent=label;
    b.setAttribute("aria-pressed",String(on));
    if(n!=null){const s=document.createElement("span");s.className="n";s.textContent=String(n);b.appendChild(s);}
    b.addEventListener("click",fn);
    return b;
  };
  const redraw=()=>{frSyncUrl();wrap.innerHTML="";frBuildFilters(items);};
  const grp=(title,chips)=>{
    const g=document.createElement("span");g.className="fr-grp";
    const em=document.createElement("em");em.textContent=title;g.appendChild(em);
    chips.forEach(c=>g.appendChild(c));return g;
  };
  const box=document.createElement("div");box.className="fr-filters";
  // 部位（多选；一个都不勾 = 全部）
  const pc=[chip("全部",FR.parts.size===0,null,()=>{FR.parts.clear();redraw();frRender();})];
  FR_BUCKETS.forEach(b=>{
    if(!cnt.parts[b]&&!FR.parts.has(b))return;   // 该部位在本板无条目就不摆空筛选项（深链带上的仍保留，便于取消）
    pc.push(chip(b,FR.parts.has(b),cnt.parts[b]||0,()=>{
      if(FR.parts.has(b))FR.parts.delete(b);else FR.parts.add(b);
      redraw();frRender();
    }));
  });
  box.appendChild(grp("部位",pc));
  const one=(title,key,opts,cur)=>{
    // opts 支持 [label, n] 或 [label, n, rawValue]；rawValue 用于「显示文案 ≠ 过滤值」的场景（如品级）
    const cs=opts.map(([label,n,rv])=>{
      const val=(rv===undefined)?label:rv;
      return chip(label,cur===val,n,()=>{FR[key]=(FR[key]===val)?"":val;redraw();frRender();});
    });
    return grp(title,cs);
  };

  const gk=Object.keys(cnt.grade).sort((a,b)=>{
    if(a==="未标")return 1; if(b==="未标")return -1; return Number(a)-Number(b);
  });
  box.appendChild(one("品级","grade",[["全部",items.length,""]].concat(gk.map(k=>[k==="未标"?"未标":"品级 "+gradeLabel(k),cnt.grade[k],k])) ,FR.grade));

  box.appendChild(one("图示","img",[["全部",items.length,""],["有图",cnt.img["有图"]||0],["含占位",cnt.img["含占位"]||0]],FR.img));
  // 玩家可用时装：默认勾选=仅显示玩家可使用时装；勾选框紧贴文案，切换只重画卡片区不重建筛选栏
  (function(){
    const namedN=items.filter(it=>it.name_visible!==false).length;
    const lab=document.createElement("label");
    lab.className="fr-check";
    lab.title="勾选=只显示玩家实际可用的时装（名字能对上玩家可见表）；取消勾选可看开发名/工程名条目";
    const cb=document.createElement("input");
    cb.type="checkbox";cb.checked=!!FR.named;
    cb.addEventListener("change",()=>{FR.named=cb.checked;frSyncUrl();frRender();});
    const tx=document.createElement("span");tx.className="t";tx.textContent="仅显示玩家可使用时装";
    const n=document.createElement("span");n.className="n";n.textContent="("+namedN+")";
    lab.appendChild(tx);lab.appendChild(cb);lab.appendChild(n);
    box.appendChild(lab);
  })();
  // 性别：只有板上确有男/女标记时才摆这一组（时装多为男女共用模型，字段为空就整组隐藏，不留 0 计数）
  if((cnt.gender["女"]||0)||(cnt.gender["男"]||0)){
    box.appendChild(one("性别","gender",[["全部",items.length,""],["女",cnt.gender["女"]||0],["男",cnt.gender["男"]||0],["未标",cnt.gender["未标"]||0]],FR.gender));
  }
  // 排序（先筛后排）：默认 = 板上原序；魅力值升降序时缺失值固定排最后
  const sortSel=document.createElement("select");
  sortSel.id="frSort";
  sortSel.setAttribute("aria-label","排序依据");
  sortSel.title="排序：默认按板上原序（归一名字序）；魅力值排序与上面的筛选叠加（先筛后排），无魅力值的固定排最后";
  [["model_desc","编号 ↓ 大→小（默认）"],["model_asc","编号 ↑ 小→大"],["charm_desc","魅力值 ↓ 高→低"],["charm_asc","魅力值 ↑ 低→高"]]
    .forEach(([v,t])=>{const o=document.createElement("option");o.value=v;o.textContent=t;sortSel.appendChild(o);});
  sortSel.value=FR.sort||"model_desc";
  sortSel.addEventListener("change",()=>{FR.sort=sortSel.value;frSyncUrl();frRender();});
  box.appendChild(sortSel);
  wrap.appendChild(box);
  wrap.style.display="";
}
/* 时装板顶部统计（随筛选变）：只重画 #pills 里时装自己的三行，不动通用 pill */
function frPills(items){
  const el=document.getElementById("pills");
  if(!el)return;
  const acc={};let perm=0,timed=0,img=0,unk=0;
  for(const it of items){
    frBuckets(it).forEach(b=>{acc[b]=(acc[b]||0)+1;});
    if(it.has_permanent===true)perm++;else if(it.has_permanent===false)timed++;else unk++;
    if(it.icon_state==="有图")img++;
  }
  el.innerHTML=`<span class="pill">筛选后 <b>${items.length}</b> / ${DATA?DATA.items.length:"?"} 件</span>`+
    FR_BUCKETS.filter(b=>acc[b]).map(b=>`<span class="pill">${esc(b)} <b>${acc[b]}</b></span>`).join("")+
    `<span class="pill">有图 <b>${img}</b></span>`+
    `<span class="pill">含永久款 <b>${perm}</b></span>`+
    `<span class="pill">仅限时 <b>${timed}</b></span>`+
    (unk?`<span class="pill">期限未知 <b>${unk}</b></span>`:"");
}
function frRender(){
  // 让既有 render() 走时装分支：这里只做一次轻量 repaint（不改任何通用状态）
  render();
}

/* ════════════════════ 载具模式（仅 board id = vehicle_full）════════════════════
   用户 2026-10-18 口径（与 fashion_wardrobe 同一套卡面纪律）：
     · 卡面只留「顶部图轨（≤4 张，多的 +N）+ 名字 + 分类 + 编号」
     · 其余字段（描述/品牌/主题/数值/获取方式/图标绑定/溯源）全部折进技术详情折叠区
     · 排序：编号 ↓ 大→小（默认）/ 编号 ↑ 小→大，缺失值排最后
     · 图轨复用时装那套灯箱（.fr-rail/.fr-zoom/.fr-box + FR_IMGS），一套交互两板共用
   ★ 类名全部 v*，图轨/灯箱复用 fr-*；样式挂 body.vehicle-mode —— 时装板与武器皮肤板零影响。 */
const SCENE_TABLE=(function(){try{return (getParam("b")||"")==="scene_balance";}catch(e){return false;}})();
if(SCENE_TABLE)document.body.classList.add("scene-mode");
const VEHICLE_BOARD=(function(){try{return (getParam("b")||"")==="vehicle_full";}catch(e){return false;}})();
const V={cls:new Set(),sub:new Set(),img:"",sort:""};
(function(){
  try{
    const u=new URLSearchParams(location.search);
    (u.get("vcls")||"").split(",").map(s=>s.trim()).filter(Boolean).forEach(p=>V.cls.add(p));
    V.img=u.get("vimg")||"";
    V.sort=u.get("vsort")||"";
  }catch(e){}
})();
function vSyncUrl(){
  try{
    const u=new URLSearchParams(location.search);
    const put=(k,v)=>{if(v)u.set(k,v);else u.delete(k);};
    put("vcls",[...V.cls].join(","));put("vimg",V.img);put("vsort",V.sort);
    history.replaceState(null,"",location.pathname+"?"+u.toString());
  }catch(e){}
}
/* 排序取值：编号 / 魅力值 / 速度 / 加速度
   速度·加速度取官方面板值（ui_speed/ui_acc，vehicle_ui_data），与卡面主签一致；
   缺失时退到载具行巡航值（navi_speed/navi_acc），再次缺失排最后。 */
function vSortVal(it,key){
  if(/charm/.test(key))return it.charm_value;
  const pm=it.params||{},nv=pm.navi||{};
  if(/^spd/.test(key))return it.ui_speed!=null?it.ui_speed:(nv.navi_speed!=null?nv.navi_speed:null);
  if(/^acc/.test(key))return it.ui_acc!=null?it.ui_acc:(nv.navi_acc!=null?nv.navi_acc:null);
  return it.vehicle_id;
}
/* 排序：编号(vehicle_id) 优先，缺失值固定排最后，同号按名字 */
function vSortList(list){
  const key=(V.sort||"id_desc");
  const asc=/_asc$/.test(key);
  const num=it=>{
    const v = vSortVal(it,key);
    if(v==null||v==="")return null;const n=Number(v);return isNaN(n)?null:n;
  };
  const arr=[...list];
  arr.sort((A,B)=>{
    const a=num(A),b=num(B);
    if(a==null&&b==null)return String(A.name||"").localeCompare(String(B.name||""),"zh-CN");
    if(a==null)return 1;
    if(b==null)return -1;
    if(a!==b)return asc?a-b:b-a;
    return String(A.name||"").localeCompare(String(B.name||""),"zh-CN");
  });
  return arr;
}
function vPass(it){
  if(V.cls.size&&!V.cls.has(it.vehicle_class||"（未标注）"))return false;
  if(V.sub.size&&!V.sub.has(it.vehicle_subclass||"（未标注）"))return false;
  if(V.img&&it.icon_state!==V.img)return false;
  return true;
}
/* 卡面参数小签
   ★ 口径校准（2026-10-30）：以游戏内载具面板为准 —— 速度 / 加速度 / 生命 / 氮气 四签。
     校准样本「天蝎座」193031：面板 速度125(+15) 加速度140(+10) 生命352 氮气2000，
     与 vehicle_ui_data 该行（ui_speed/ui_acc/ui_nitrogen_*_addition）+ attr hp 曲线 lv8
     + all_equips.max_nitrogen 逐项吻合。
   ★ 因此卡面主签一律用 vehicle_ui_data 的 UI 展示值；
     vehicle_proto_data 的物理量（top_speed 355.2 / acc 2618.7）**不同量纲**，
     不是面板速度，只留在技术详情里，不摆到卡面。 */
function vNum(x){
  if(x==null)return null;
  const n=Number(x);if(!isFinite(n))return null;
  const a=Math.abs(n);
  return a>=1000?String(Math.round(n)):(a>=100?String(Math.round(n*10)/10):String(Math.round(n*100)/100));
}
function vPerfChips(it){
  const pm=it.params||null;
  const charm=`<span class="fr-charm${it.charm_value!=null?"":" na"}" title="魅力值 charm_value（all_equips 载具行，主口径经典服）${
    it.charm_note?" · "+esc(it.charm_note):""}">${it.charm_value!=null?"魅力 "+esc(it.charm_value):"魅力 —"}</span>`;
  if(!pm)return charm;
  const nt=pm.nitrogen||{};
  // 速度：ui_speed（vehicle_ui_data，官方面板值）+ 氮气加成黄字
  const spTxt=it.ui_speed!=null
    ?`<span class="v-perf ui" title="速度 ${esc(it.ui_speed)}（vehicle_ui_data.ui_speed，游戏面板同值）${
        nt.ui_speed_addition!=null?" ｜ 氮气状态下 +"+esc(nt.ui_speed_addition):""}${
        pm.navi&&pm.navi.navi_speed!=null?" ｜ 巡航速度 navi_speed="+esc(vNum(pm.navi.navi_speed)):""}">速度 ${esc(vNum(it.ui_speed))}${
        nt.ui_speed_addition!=null?`<span class="v-nadd">+${esc(vNum(nt.ui_speed_addition))}</span>`:""}</span>`
    :"";
  // 加速度：ui_acc（官方面板值）+ 氮气加成黄字
  const acTxt=it.ui_acc!=null
    ?`<span class="v-perf ui" title="加速度 ${esc(it.ui_acc)}（vehicle_ui_data.ui_acc，游戏面板同值）${
        nt.ui_acc_addition!=null?" ｜ 氮气状态下 +"+esc(nt.ui_acc_addition):""}">加速 ${esc(vNum(it.ui_acc))}${
        nt.ui_acc_addition!=null?`<span class="v-nadd">+${esc(vNum(nt.ui_acc_addition))}</span>`:""}</span>`
    :"";
  return charm+spTxt+acTxt+vFuncChips(it);
}
/* 二期小签：生命 / 氮气 / 特技（生命=等级 hp 曲线；氮气=all_equips.max_nitrogen） */
function vFuncChips(it){
  const pm=it.params||{}, out=[];
  const hp=pm.health||{};
  // 官方面板生命值 = hp 曲线「当前等级」取值（校准样本：天蝎座 lv8 → 352）
  // 卡面给 lv1 基线，完整曲线在 tooltip 与技术详情
  const cv=hp.hp_curve||[];
  if(cv.length){
    const lv1=cv[0], lvMax=cv[cv.length-1];
    const parts=[`等级生命曲线：${esc(hp.levels_total||cv.length)} 级`,
                 `${esc(lv1[0])} 级 ${esc(vNum(lv1[1]))} → ${esc(lvMax[0])} 级 ${esc(vNum(lvMax[1]))}`];
    if(hp.garage_hp_bonus!=null)parts.push(`车库功能基础血量 +${esc(hp.garage_hp_bonus)}（全局）`);
    parts.push("游戏面板显示的是「当前等级」的血量，非固定值");
    out.push(`<span class="v-perf hp" title="${esc(parts.join(' ｜ '))}">生命 ${esc(vNum(lv1[1]))}→${esc(vNum(lvMax[1]))}</span>`);
  }else if(hp.ui_health!=null){
    out.push(`<span class="v-perf hp" title="UI 生命条 ${esc(vNum(hp.ui_health))}（vehicle_ui_data.ui_health）">生命 ${esc(vNum(hp.ui_health))} 条</span>`);
  }
  const nt=pm.nitrogen||{};
  if(nt.max_nitrogen){
    const parts=[`氮气容量上限 ${esc(vNum(nt.max_nitrogen))}（all_equips.max_nitrogen，0 = 无氮气）`];
    if(nt.cost_per_second!=null)parts.push(`加速每秒耗 ${esc(vNum(nt.cost_per_second))}`);
    if(nt.restore_per_second!=null)parts.push(`每秒回 ${esc(vNum(nt.restore_per_second))}`);
    if(nt.garage_limit_bonus!=null)parts.push(`车库功能 +${esc(nt.garage_limit_bonus)}（全局）`);
    out.push(`<span class="v-perf nit" title="氮气：${esc(parts.join(' ｜ '))}">氮气 ${esc(vNum(nt.max_nitrogen))}</span>`);
  }
  const tg=it.tags||[], pk=it.perks||[], ml=it.modding_levels||[];
  if(tg.length){
    const names=tg.map(t=>t.name||("标签"+t.tag_id)).join(" / ");
    const tip="特技标签（vehicle_ui_data.vehicle_garage_tags 跳转列表 → vehicle_tags_data）：\n"
              +tg.map(t=>t.name+(t.desc?("："+t.desc):"")+(t.level!=null?(" [Lv"+t.level+"]"):"")).join("\n");
    out.push(`<span class="v-perf perk" title="${esc(tip)}">${esc(names)}</span>`);
  }else if(pk.length)out.push(`<span class="v-perf perk" title="特技：${esc(pk.map(p=>p.name||p.desc).join(' / '))}">特技 ${esc(pk.length)}</span>`);
  else if(ml.length)out.push(`<span class="v-perf perk" title="改装等级解锁：${esc(ml.map(x=>'Lv'+x.level+' '+(x.func_name||x.func_desc||'')).join(' / '))}">改装 ${esc(ml.length)}</span>`);
  return out.join("");
}
/* 卡面 = 图轨 + 名字 + 分类 + 编号（载具表没有品级字段 → 不摆空位） */
function vCard(it,i){
  const clsCn=it.vehicle_class||"（未标注）";
  const pairs=[];
  pairs.push(["载具类型",clsCn+(it.vehicle_class_token?"（ui_vehicle_icon 后缀 "+it.vehicle_class_token+"：表里无中文类型字段，token 直译）":"")]);
  if(it.brand_name)pairs.push(["品牌系列",it.brand_name]);
  if(it.theme)pairs.push(["主题标记",it.theme]);
  if(it.sort_in_garage!=null)pairs.push(["排序号 sort_in_garage",String(it.sort_in_garage)]);
  if(it.vehicle_level!=null)pairs.push(["载具等级 vehicle_level",String(it.vehicle_level)]);
  if(it.vehicle_equip_type!=null)pairs.push(["装备类型码 vehicle_equip_type",String(it.vehicle_equip_type)]);
  const num=(k,v)=>{if(v!=null)pairs.push([k,String(v)]);};
  num("生命 ui_health",it.ui_health);num("加速 ui_acc",it.ui_acc);num("速度 ui_speed",it.ui_speed);
  num("氮气加速加成",it.ui_nitrogen_acc_addition);num("氮气速度加成",it.ui_nitrogen_speed_addition);
  num("水域加速加成",it.ui_acc_water_add);num("水域速度加成",it.ui_speed_water_add);
  /* ── 2026-10-30 二期：描述 / 特技 / 氮气 / 生命量 / 改装等级 ── */
  if(it.desc)pairs.push(["载具描述 desc",it.desc+"  ← vehicle_ui_data.desc"]);
  const pk=it.perks||[];
  if(pk.length){
    pairs.push(["特技（"+pk.length+" 项）",pk.map(p=>{
      const lv=p.level!=null?"Lv"+p.level+" ":"";
      const tp=p.type!=null?"["+p.type+"] ":"";
      return lv+tp+(p.name||"")+(p.desc?"："+p.desc:"");
    }).join("\n")+"\n← vehicle_modding_function_conf_data（ref_vehicle_id 归属）"]);
  }else{
    pairs.push(["特技","表内无 ref_vehicle_id 指向该编号 → 无可归属特技"]);
  }
  const tg=it.tags||[];
  if(tg.length){
    pairs.push(["特技标签（"+tg.length+" 项）",tg.map(t=>{
      const lv=t.level!=null?"Lv"+t.level+" ":"";
      return lv+(t.name||"")+(t.desc?"："+t.desc:"");
    }).join("\n")+"\n← vehicle_ui_data.vehicle_garage_tags 跳转列表 → vehicle_tags_data（基址 2716）"]);
  }else{
    pairs.push(["特技标签","vehicle_garage_tags 为空或无标签"]);
  }
  const ml=it.modding_levels||[];
  if(ml.length){
    pairs.push(["改装等级解锁",ml.map(x=>"Lv"+x.level+" → "+(x.func_name||x.func_desc||x.func_id)).join("\n")
      +"\n← vehicle_modding_data（行↔块归属为按序配平，confidence=inferred）"]);
  }
  /* ── 2026-10-29 深挖：魅力值 + 加速度/最大速度（all_equips 载具行 × vehicle_proto_data）── */
  const pm=it.params||null;
  if(pm){
    const bs=it.charm_by_server||{};
    const bsTxt=Object.keys(bs).filter(k=>bs[k]!=null).map(k=>k+" "+bs[k]).join(" / ");
    pairs.push(["魅力值 charm_value",it.charm_value!=null
      ?String(it.charm_value)+(bsTxt?"（分服："+bsTxt+"）":"")
      :"表内未标注"]);
    pairs.push(["参数来源服",pm.server+"（主口径）；命中服 "+((pm.servers_present||[]).join(" / ")||"—")]);
    if(pm.proto_id!=null)pairs.push(["物理原型 proto_id",String(pm.proto_id)]);
    const pr=pm.proto||{};
    if(pr.top_speed!=null)pairs.push(["物理极速 top_speed",String(pr.top_speed)+"  ← vehicle_proto_data（引擎内部量）"]);
    if(pr.acc!=null)pairs.push(["净加速度 acc",String(pr.acc)
      +"  =（驱动力 "+pr.driving_force+" − 摩擦阻力 "+pr.frictional_force+"）÷ 质量 "+pr.mass]);
    const np=(k,v)=>{if(v!=null)pairs.push([k,String(v)]);};
    np("驱动力 driving_force",pr.driving_force);np("摩擦阻力 frictional_force",pr.frictional_force);
    np("质量 C_Mass",pr.mass);np("峰值扭矩 DDE_PeakTorque",pr.peak_torque);
    np("引擎最高角速度 DDE_MaxOmega",pr.max_omega);np("主减速比 DG_FinalRatio",pr.final_ratio);
    np("油门上升速率 KS_AccelRiseRate",pr.accel_rise);np("刹车上升速率 KS_BrakeRiseRate",pr.brake_rise);
    if(pm.proto==null&&pm.proto_id!=null)pairs.push(["物理原型","proto_id "+pm.proto_id+" 不在还原树 vehicle_proto_data（86 行）内"]);
    const nv=pm.navi||{};
    np("巡航/导航速度 navi_speed",nv.navi_speed);
    np("巡航加速度 navi_acc",nv.navi_acc);np("巡航减速度 navi_dec",nv.navi_dec);
    np("巡航转向 navi_turn",nv.navi_turn);np("野外巡航速度 field_navi_speed",nv.field_navi_speed);
    const ad=pm.adds||{};
    np("氮气·最大速度加成",ad.nitrogen_max_speed_addition);np("氮气·加速度加成",ad.nitrogen_acceleration_addition);
    np("公路·最大速度加成",ad.highway_road_max_speed_addition);np("公路·加速度加成",ad.highway_road_acceleration_addition);
    np("水中速度比 water_speed_ratio",ad.water_speed_ratio);
    const at=pm.attr||null;
    if(at){
      pairs.push(["等级属性 attr_id",String(at.attr_id)+"（vehicle_attr_data 共 "+at.levels_total+" 级）"]);
      pairs.push(["生命曲线 hp","等级 "+at.hp_curve.map(x=>x[0]+" → "+x[1]).join(" ｜ ")]);
      np("车辆减伤 car_rate",at.car_rate);np("爆炸减伤 explode_rate",at.explode_rate);
      np("撞击伤害速度区间",at.min_hurt_speed+" ~ "+at.max_hurt_speed);
      np("对玩家伤害系数 player_rate",at.player_rate);
    }
    /* 二期：氮气全套 + 生命量 */
    const nt=pm.nitrogen||null;
    if(nt){
      const n2=(k,v,lbl)=>{if(v!=null)pairs.push([lbl,String(v)]);};
      n2("max_nitrogen",nt.max_nitrogen,"氮气容量上限 max_nitrogen");
      n2("cost",nt.cost_per_second,"氮气消耗 /秒 acc_cost_nitrogen_per_second");
      n2("restore",nt.restore_per_second,"氮气回复 /秒 restore_nitrogen_per_second");
      n2("navi_save",nt.navi_save_ratio,"导航状态消耗折扣 in_navi_save_acc_cost_nitrogen_ratio");
      n2("phase",nt.phase_ratio,"氮气阶段系数 nitrogen_phase_ratio");
      n2("air_impulse",nt.air_impulse,"空中氮气冲量 nitrogen_air_impulse");
      n2("ui_acc_add",nt.ui_acc_addition,"氮气加速加成（UI）ui_nitrogen_acc_addition");
      n2("ui_spd_add",nt.ui_speed_addition,"氮气速度加成（UI）ui_nitrogen_speed_addition");
      if(nt.garage_limit_bonus!=null)pairs.push(["车库功能氮气上限 +",String(nt.garage_limit_bonus)
        +"  ← vehicle_garage_function_conf_data（全局功能，非逐车；数值取自 func_desc 文本标记位）"]);
    }else{
      pairs.push(["氮气","该编号 max_nitrogen 为 0 或字段缺失 → 无氮气系统"]);
    }
    const hh=pm.health||null;
    if(hh){
      if(hh.ui_health!=null)pairs.push(["生命量 ui_health",String(hh.ui_health)]);
      if(hh.hp_curve&&hh.hp_curve.length)pairs.push(["等级生命曲线 hp","等级 "
        +hh.hp_curve.map(x=>x[0]+" → "+x[1]).join(" ｜ ")+(hh.levels_total?"（共 "+hh.levels_total+" 级）":"")]);
      if(hh.garage_hp_bonus!=null)pairs.push(["车库功能基础血量 +",String(hh.garage_hp_bonus)
        +"  ← vehicle_garage_function_conf_data（全局功能，非逐车）"]);
    }
    const caps=(DATA&&DATA.meta&&DATA.meta.params_meta&&DATA.meta.params_meta.caps)||null;
    if(caps)pairs.push(["全局上限","max_speed "+caps.max_speed+" ｜ max_acc "+caps.max_acc
      +" ｜ ui_speed_ratio "+caps.ui_speed_ratio+"（"+caps.source+"）"]);
    pairs.push(["单位口径","表内无单位换算字段 → 本板只给原值，不换算 km/h"]);
  }else{
    pairs.push(["魅力值 / 速度参数",it.param_state||"未在 all_equips 载具行内"]);
  }
  pairs.push(["可获取 player_available",it.player_available===true?"是":(it.player_available===false?"否":"表里未标注")]);
  if(it.available_ts!=null)pairs.push(["上架时间 available_ts",String(it.available_ts)]);
  if(it.hide_when_not_own!=null)pairs.push(["未拥有时隐藏",it.hide_when_not_own?"是":"否"]);
  if(it.jump_text)pairs.push(["获取途径文案",zhText(it.jump_text)]);
  if(it.vehicle_garage_tags)pairs.push(["车库标签",String(it.vehicle_garage_tags)]);
  if(it.special_function!=null)pairs.push(["special_function",String(it.special_function)]);
  if(it.garage_scale!=null)pairs.push(["车库缩放 garage_scale",String(it.garage_scale)]);
  if(it.regions)pairs.push(["可用区域 regions",String(it.regions)]);
  if(it.garage_idle_anim)pairs.push(["车库待机动画",String(it.garage_idle_anim)]);
  if(it.garage_role_anim)pairs.push(["车库角色动画",String(it.garage_role_anim)]);
  pairs.push(["坐姿 / 玩家位模型","表内 jump 组 kind=0x5，解码器不支持 → 未解出，留空不猜"]);
  pairs.push(["图标状态",(it.icon_state||"")+" · "+(it.icon_count||0)+" 张"]);
  pairs.push(["图标核验","只导出 gpk_loc0 逐图命中的图；本卡 "+(it.icon_verified_by_gpk_loc0?"全部命中":"存在未命中")]);
  const imgLines=((it._media&&it._media.images)||[]).map(x=>{
    const kind=x.kind==="类型"?"[类型] ":"[专属] ";
    return kind+x.base+(x.suffix?" · "+x.suffix:"")+(x.pack?"  ← "+x.pack+(x.row!=null?" row "+x.row:""):"")+(x.fid?" fid "+x.fid:"");
  });
  if(imgLines.length)pairs.push(["图标绑定",imgLines.join("\n")]);
  const md=(it._media&&it._media.note)||"";
  if(md)pairs.push(["配图说明",md]);
  if((it.vehicle_ids||[]).length>1){
    pairs.push(["全部编号",(it.vehicle_ids||[]).join(" / ")]);
    pairs.push(["编号数",String(it.vehicle_ids.length)]);
  }else{
    pairs.push(["载具 ID（行键）",String(it.vehicle_id)]);
  }
  if((it.tables||[]).length)pairs.push(["来源表",it.tables.join(" / ")]);
  pairs.push(["解码路径",it.decode_path==="permissive"
    ?"行尾内联变体宽容重放（列表字段仍空）":"严格 D6 行解码"]);
  const p=effProv(it);
  if(p.table)pairs.push(["定位表",p.table]);
  if(p.field_refs)pairs.push(["字段出处",(p.field_refs||[]).join(" / ")]);
  pushFieldSources(p,pairs);
  if(p.name_source)pairs.push(["名称出处",p.name_source]);
  if(p.source_lock_sha256)pairs.push(["源快照摘要",String(p.source_lock_sha256).slice(0,32)+"…"]);
  if(p.locator_chain&&p.locator_chain.chain_status)pairs.push(["定位链",p.locator_chain.chain_status]);
  pairs.push(["证据等级",(EV_CN[it.evidence]||it.evidence||"")+(it.evidence_level?" · "+(VALUE_CN.evidence_level[it.evidence_level]||it.evidence_level):"")]);
  const ros=p.roster;
  if(ros)pairs.push(["证据类型",`名册级（${ros.evidence==="name-roster-only"?"字符串池名册":"静态导出"}）· 无行级溯源`+(ros.source_desc?` · ${ros.source_desc}`:"")]);
  if((it.status_tags||[]).length)pairs.push(["状态标签",it.status_tags.map(t=>STATE_CN[t]||t).join(" / ")]);
  const kv=pairs.map(([k,v])=>{
    const mono=/(行键|定位表|来源表|图标绑定|源快照摘要|名称出处)/.test(k);
    return `<div class="k">${esc(k)}</div><div class="v${mono?" mono":""}">${v===null||v===undefined?"":esc(String(v))}</div>`;
  }).join("");
  FR_IMGS[it.id]=Array.isArray((it._media||{}).images)?it._media.images.map(x=>x.png):[];
  const typeTag=it.icon_state==="专属图"?"":`<span class="fr-tagtype" title="表里 ui_vehicle_icon 指向的「载具类型」按钮图标，不是这辆车的专属立绘">类型图</span>`;
  const cardCls = it.icon_state === "专属图" ? "vcard" : "vcard typeonly";
  return `<div class="i fcard ${cardCls}" data-frid="${esc(it.id)}"${i!=null?` data-cidx="${esc(String(i))}"`:""}>
    ${frRail(it)}
    <div class="fr-head"><div class="fr-name" title="${esc(it.name||it.id)}">${esc(it.name||it.id)}</div></div>
    ${it.desc?`<div class="fr-desc" title="${esc(it.desc)}">${esc(it.desc)}</div>`:""}
    <div class="fr-sub">
      <span class="fr-part b-veh" title="类型=vehicle_brand_data.type_name">${esc(clsCn)}</span>${it.vehicle_subclass?`<span class="fr-part b-veh" style="opacity:.8" title="子类=vehicle_brand_data.brands 品牌">${esc(it.vehicle_subclass)}</span>`:""}
      <span class="fr-model" title="载具编号（同名含时限变体）">${(it.vehicle_ids&&it.vehicle_ids.length>1)?`编号 ×${it.vehicle_ids.length}`:`编号 ${esc(it.vehicle_id)}`}</span>
      ${vPerfChips(it)}
      ${it.has_trial?'<span class="fr-tagtype" title="该卡包含体验版编号">含体验版</span>':""}
      ${typeTag}
    </div>
    ${(it.desc||it.desc_note||it.effect_text||it.charm_note||it.reborn_vis!=null||it.back_weapon_vis!=null||(it.hide_parts||[]).length)
      ?`<details class="fdesc" hidden><summary>详情</summary><div class="fdesc-body">${
          ((it.vehicle_ids||[]).length>1?`<div class="fd-row"><span class="fd-k">全部编号</span><span class="fd-v mono">${it.vehicle_ids.join(" / ")}</span></div>`:"")+
          (it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${richText(it.desc)}</span></div>`:"")+
          (it.desc_note&&!it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${esc(it.desc_note)}</span></div>`:"")+
          (it.effect_text?`<div class="fd-row"><span class="fd-k">效果</span><span class="fd-v">${esc(it.effect_text)}</span></div>`:"")+
          (it.effect_text?`<div class="fd-row"><span class="fd-k">效果来源</span><span class="fd-v mono">${esc(it.effect_source||"—")}</span></div>`:"")+
          (it.charm_note?`<div class="fd-row"><span class="fd-k">魅力值</span><span class="fd-v">${esc(it.charm_note)}</span></div>`:"")+
          (it.reborn_vis!=null?`<div class="fd-row"><span class="fd-k">隐藏半感染者花苞</span><span class="fd-v">${it.reborn_vis?"是":"否"}</span></div>`:"")+
          ((it.hide_parts||[]).map(x=>`<div class="fd-row"><span class="fd-k">隐藏${esc(x)}</span><span class="fd-v">是</span></div>`).join(""))+
          (it.back_weapon_vis!=null?`<div class="fd-row"><span class="fd-k">隐藏副武器</span><span class="fd-v">${it.back_weapon_vis?"是":"否"}</span></div>`:"")
        }</div></details>`:""}
    <details class="tech" hidden><summary>技术详情 / 数据来源 / 审计信息</summary><div class="fr-kv">${kv}</div></details>
  </div>`;
}
/* 2026-10-29：卡内「详情/技术详情」折叠按钮全部下架（用户口径：三板只留 D2 子卡看详情），
   数据仍在缓存卡 HTML 里，D2 嵌入时由 embedD2Body 解除 hidden 展示 */
/* 折叠时显示描述的前一小段，展开看全文 */
function frDescHead(desc){
  const t=String(zhText(desc)).replace(/\s+/g," ").trim();
  return t.length>22?("描述 · "+t.slice(0,22)+"…"):("描述 · "+t);
}
function vCountBy(items,key){
  const acc={};
  for(const it of items){const k=it[key]||"（未标注）";acc[k]=(acc[k]||0)+1;}
  return acc;
}
function vPills(items){
  const el=document.getElementById("pills");
  if(!el)return;
  const total=DATA?DATA.items.length:items.length;
  const own=items.filter(it=>it.icon_state==="专属图").length;
  const typ=items.filter(it=>it.icon_state==="仅类型图").length;
  const chm=items.filter(it=>it.charm_value!=null).length;
  const phy=items.filter(it=>it.params&&it.params.proto).length;
  el.innerHTML=`<span class="pill">筛选后 <b>${items.length}</b> / ${total} 辆</span>`+
    `<span class="pill">专属图 <b>${own}</b></span>`+
    `<span class="pill">仅类型图 <b>${typ}</b></span>`+
    `<span class="pill" title="魅力值 charm_value（all_equips 载具行）">有魅力值 <b>${chm}</b></span>`+
    `<span class="pill" title="命中 vehicle_proto_data 物理原型（acc / top_speed）">有物理参数 <b>${phy}</b></span>`;
}
function vBuildFilters(items){
  const wrap=document.getElementById("fFashionWrap");
  if(!wrap)return;
  const clsCnt=vCountBy(items,"vehicle_class");
  const imgCnt=vCountBy(items,"icon_state");
  const chip=(label,on,n,fn)=>{
    const b=document.createElement("button");
    b.type="button";b.className="fr-chip";b.textContent=label;
    b.setAttribute("aria-pressed",String(on));
    if(n!=null){const s=document.createElement("span");s.className="n";s.textContent=String(n);b.appendChild(s);}
    b.addEventListener("click",fn);
    return b;
  };
  const redraw=()=>{vSyncUrl();wrap.innerHTML="";vBuildFilters(items);};
  const grp=(title,chips)=>{
    const g=document.createElement("span");g.className="fr-grp";
    const em=document.createElement("em");em.textContent=title;g.appendChild(em);
    chips.forEach(c=>g.appendChild(c));return g;
  };
  const box=document.createElement("div");box.className="fr-filters";
  const cls=[chip("全部",V.cls.size===0,null,()=>{V.cls.clear();redraw();render();})];
  Object.keys(clsCnt).sort((a,b)=>clsCnt[b]-clsCnt[a]).forEach(k=>{
    if(!clsCnt[k]&&!V.cls.has(k))return;
    cls.push(chip(k,V.cls.has(k),clsCnt[k],()=>{
      if(V.cls.has(k))V.cls.delete(k);else V.cls.add(k);
      redraw();render();
    }));
  });
  box.appendChild(grp("类型",cls));
  const subCnt=vCountBy(items,"vehicle_subclass");
  const subs=[chip("全部",V.sub.size===0,null,()=>{V.sub.clear();redraw();render();})];
  Object.keys(subCnt).sort((a,b)=>subCnt[b]-subCnt[a]).forEach(k=>{
    if(!subCnt[k]&&!V.sub.has(k))return;
    subs.push(chip(k,V.sub.has(k),subCnt[k],()=>{
      if(V.sub.has(k))V.sub.delete(k);else V.sub.add(k);
      redraw();render();
    }));
  });
  box.appendChild(grp("子类",subs));
  const one=(title,key,opts,cur)=>{
    const cs=opts.map(([label,n])=>chip(label,cur===label,n,()=>{V[key]=(V[key]===label)?"":label;redraw();render();}));
    return grp(title,cs);
  };
  box.appendChild(one("图示","img",[["全部",items.length],["专属图",imgCnt["专属图"]||0],["仅类型图",imgCnt["仅类型图"]||0]],V.img));
  const sortSel=document.createElement("select");
  sortSel.id="vSort";
  sortSel.setAttribute("aria-label","排序依据");
  sortSel.title="排序：编号 = 载具 ID（行键）；魅力值 = all_equips.charm_value；速度 = vehicle_ui_data.ui_speed（游戏面板同值，缺失退 navi_speed 巡航速度）；加速度 = vehicle_ui_data.ui_acc（缺失退 navi_acc）；缺失值固定排最后，同值按名字";
  var vopts=[["id_desc","编号 ↓ 大→小（默认）"],["id_asc","编号 ↑ 小→大"]];
  var _has=function(f){return (DATA.items||[]).some(f);};
  if(_has(function(x){return x.charm_value!=null;})){
    vopts.push(["charm_desc","魅力值 ↓ 高→低"],["charm_asc","魅力值 ↑ 低→高"]);
  }
  if(_has(function(x){return x.ui_speed!=null||(x.params&&(x.params.navi||{}).navi_speed!=null);})){
    vopts.push(["spd_desc","速度 ↓ 高→低"],["spd_asc","速度 ↑ 低→高"]);
  }
  if(_has(function(x){return x.ui_acc!=null||(x.params&&(x.params.navi||{}).navi_acc!=null);})){
    vopts.push(["acc_desc","加速度 ↓ 高→低"],["acc_asc","加速度 ↑ 低→高"]);
  }
  vopts.forEach(([v,t])=>{const o=document.createElement("option");o.value=v;o.textContent=t;sortSel.appendChild(o);});
  sortSel.value=V.sort||"id_desc";
  sortSel.addEventListener("change",()=>{V.sort=sortSel.value;vSyncUrl();render();});
  box.appendChild(sortSel);
  wrap.appendChild(box);
  wrap.style.display="";
}

/* ════════════════════ 战术芯片模式（仅 board id = tactical_chip_full）════════════════════
   2026-10-18 新增，与载具/时装同一套卡面纪律：
     · 卡面只留「图轨（_b 大图 + _s 小图，≤4 张）+ 名字 + 品质色档 + 类型 + 编号」
     · 满级属性 / 12 档数值表 / 道具行 / 奖池 / 图标绑定 / 溯源全部折进卡内「技术详情」
     · 排序：编号 ↓（默认，编号=道具行 id，无道具行用 chip_type 行键）/ 编号 ↑，缺失值排最后
     · 筛选：类型（进攻/防御）、品质（基础/高级/特级）、图标（有图/仅小图）、投放（奖池/仅道具行/无道具行）
   ★ 类名全部 chip-* / c* —— 图轨与灯箱复用 fr-*，样式挂 body.chip-mode，其它板零影响。 */
const CHIP_BOARD=(function(){try{return (getParam("b")||"")==="tactical_chip_full";}catch(e){return false;}})();
const CORE_BOARD=(function(){try{return (getParam("b")||"")==="mutation_core_full";}catch(e){return false;}})();
const CQ={fam:new Set(),q:new Set(),img:"",sort:""};
(function(){
  try{
    const u=new URLSearchParams(location.search);
    (u.get("cfam")||"").split(",").map(s=>s.trim()).filter(Boolean).forEach(p=>CQ.fam.add(p));
    (u.get("cq")||"").split(",").map(s=>s.trim()).filter(Boolean).forEach(p=>CQ.q.add(p));
    CQ.img=u.get("cimg")||"";CQ.sort=u.get("csort")||"";
  }catch(e){}
})();
function cSyncUrl(){
  try{
    const u=new URLSearchParams(location.search);
    const put=(k,v)=>{if(v)u.set(k,v);else u.delete(k);};
    put("cfam",[...CQ.fam].join(","));put("cq",[...CQ.q].join(","));
    put("cimg",CQ.img);put("csort",CQ.sort);
    history.replaceState(null,"",location.pathname+"?"+u.toString());
  }catch(e){}
}
/* 芯片富文本：本表 desc 的高亮 token 是「裸 #f」（无参数，无括号；1908 处 #f / 1884 处 #n，
   没有 #f(N) 形式），与通用 richText 的 #f(N)/#f+数字 分支不兼容（会把数值首位吃掉），
   因此芯片卡走这套独立渲染，不改通用 richText。 */
function cRich(s){
  let t=esc(String(s??""));
  t=t.replace(/#c([0-9a-fA-F]{6})/g,'</span><span class="rt" style="color:#$1">')
     .replace(/#f/g,'</span><span class="rt hl">')
     .replace(/#n/g,'</span><span class="rt">')
     .replace(/#r/g,"<br>");
  return `<span class="rt chip-rt">${t}</span>`;
}
function cNum(v){
  if(v===null||v===undefined||v==="")return "";
  if(typeof v==="number")return String(v);
  return String(v);
}
function cNo(it){return it.item_id!=null?it.item_id:it.chip_type_id;}
function cSortList(list){
  const asc=/_asc$/.test(CQ.sort||"no_desc");
  const arr=[...list];
  arr.sort((A,B)=>{
    const a=cNo(A),b=cNo(B);
    const am=A.item_id!=null,bm=B.item_id!=null;
    if(am!==bm)return am?-1:1;                 // 有道具行的在前，无道具行固定排最后
    if(a!==b)return asc?a-b:b-a;
    return String(A.name||"").localeCompare(String(B.name||""),"zh-CN");
  });
  return arr;
}
function cPass(it){
  if(CQ.fam.size&&!CQ.fam.has(it.family||"未标注"))return false;
  if(CQ.q.size&&!CQ.q.has(String(it.quality)))return false;
  if(CQ.img==="有图"&&!(it.icon_count>0))return false;
  if(CQ.img==="仅小图"&&!it.only_small)return false;
  return true;
}
/* 详情键值对（D2 灯箱审计区与对比钉停靠栏共用同一份字段清单；顺带登记 FR_IMGS 供大图查看器用） */
function cKvHtml(it){
  const q=it.quality||1;
  const pairs=[];
  pairs.push(["满级属性",cRich(it.desc||"（无描述）")]);
  pairs.push(["属性描述出处","belt_chip_data.base_desc（{N} 按 base_params 参数组按下标代入；差 3 枚参数个数与占位不符，保留原文）"]);
  pairs.push(["类型","%s（chip_type 行键首位 1=进攻 / 2=防御）".replace("%s",it.family||"未标注")]);
  pairs.push(["品质",`${it.quality_label||"未标注"}（chip_quality ${it.quality}）`]);
  pairs.push(["品质档名出处",it.quality_source||"—"]);
  pairs.push(["chip_type 行键",String(it.chip_type_id)]);
  if(it.item_id!=null)pairs.push(["道具行 id",String(it.item_id)]);
  else pairs.push(["道具行 id","无（common_item 330/331 段无同名图标行 → 静态配置名，id 静态不可得）"]);
  if(it.effect_label)pairs.push(["effect_label",it.effect_label]);
  if(it.effect_label_cd!=null)pairs.push(["effect_label_cd",String(it.effect_label_cd)]);
  if(it.max_chip_level!=null)pairs.push(["max_chip_level",String(it.max_chip_level)]);
  if(it.crystallite_count!=null)pairs.push(["晶石数 crystallite_count",String(it.crystallite_count)]);
  if(it.level_count)pairs.push(["档位数",String(it.level_count)]);
  pairs.push(["投放状态",it.release_state||"—"]);
  pairs.push(["奖池 pool_id",(it.pool_ids||[]).length?it.pool_ids.join("、"):"当前奖池未投放"]);
  pairs.push(["图标状态",`${it.icon_state} · ${it.icon_count} 张`]);
  pairs.push(["图标核验","只导出 gpk_loc0 逐图命中的图；本卡 "+(it.icon_verified_by_gpk_loc0?"全部命中":"存在未命中")]);
  const imgLines=((it._media&&it._media.images)||[]).map(x=>
    `${x.suffix==="b"?"[大图] ":"[小图] "}${x.base}${x.pack?`  ← ${x.pack} row ${x.row}`:""}${x.fid?` fid ${x.fid}`:""}`);
  if(imgLines.length)pairs.push(["图标绑定",imgLines.join("\n")]);
  const miss=((it.icon_missing)||[]).filter(m=>m&&m.reason);
  if(miss.length)pairs.push(["未下发图",miss.map(m=>`${m.base}_${m.suffix}：${m.reason}`).join("\n")]);
  if(it.item_name)pairs.push(["道具行名称",`${it.item_name}${it.item_link?"（"+it.item_link+"）":""}`]);
  const p=effProv(it);
  if(p.table)pairs.push(["定位表",p.table]);
  if((it.tables||[]).length)pairs.push(["来源表",it.tables.join(" / ")]);
  if(p.field_refs)pairs.push(["字段出处",(p.field_refs||[]).join(" / ")]);
  pushFieldSources(p,pairs);
  if(p.name_source)pairs.push(["名称出处",p.name_source]);
  if(p.source_lock_sha256)pairs.push(["源快照摘要",String(p.source_lock_sha256).slice(0,32)+"…"]);
  if(p.locator_chain&&p.locator_chain.chain_status)pairs.push(["定位链",p.locator_chain.chain_status]);
  pairs.push(["行键 row_keys",(it.row_keys||[]).join(", ")]);
  FR_IMGS[it.id]=Array.isArray((it._media||{}).images)?it._media.images.map(x=>x.png):[];
  return pairs.map(([k,v])=>{
    const mono=/(行键|定位表|来源表|图标绑定|源快照摘要|名称出处|未下发图)/.test(k);
    return `<div class="k">${esc(k)}</div><div class="v${mono?" mono":""}">${/(满级属性|属性描述出处)/.test(k)?v:esc(String(v))}</div>`;
  }).join("");
}
/* 卡面 = 图轨 + 名字 + 品质色档 + 类型 + 编号 + 首档效果
   （2026-10-29 卡内「12 档数值 / 技术详情」折叠区已删——详情统一走 D2 灯箱与对比钉停靠栏；
     cKvHtml 调用保留：它同时登记 FR_IMGS 供卡面图轨的大图查看器使用） */
function cCard(it,cidx){
  const q=it.quality||1;
  cKvHtml(it);
  const onlySmall=it.icon_count===1&&((it._media||{}).images||[])[0]&&((it._media||{}).images||[])[0].suffix==="s";
  return `<div class="i fcard chip-card q${q}" data-frid="${esc(it.id)}"${cidx==null?"":` data-cidx="${esc(String(cidx))}"`}>
    ${frRail(it)}
    <div class="fr-head"><div class="fr-name" title="${esc(it.name||it.id)}">${esc(it.name||it.id)}</div></div>
    <div class="fr-sub">
      <span class="fr-quality q${q}" title="品质档 chip_quality=${esc(String(q))}">${esc(it.quality_label||("品质"+q))}</span>
      <span class="fr-part b-chip">${esc(it.family||"未标注")}</span>
      <span class="fr-model" title="${esc(it.display_no_source||"编号")}">编号 ${esc(String(cNo(it)))}</span>
      ${it.max_chip_level?`<span class="fr-tagtype" title="芯片最高等级">最高 Lv${esc(String(it.max_chip_level))}</span>`:""}
      ${it.only_small?'<span class="fr-tagtype" title="该芯片 _b 大图 fid 未命中 gpk_loc0，仅小图可用">仅小图</span>':""}
    </div>
    ${it.effect_desc?`<div class="fr-desc" title="首档效果（熟练度 ${esc(String(it.effect_level||""))}）">${esc(it.effect_desc)}</div>`:""}
  </div>`;
}
function cCountBy(items,fn){
  const acc={};
  for(const it of items){const k=fn(it)||"（未标注）";acc[k]=(acc[k]||0)+1;}
  return acc;
}
function cPills(items){
  const el=document.getElementById("pills");
  if(!el)return;
  const total=DATA?DATA.items.length:items.length;
  el.innerHTML=`<span class="pill">筛选后 <b>${items.length}</b> / ${total} 枚</span>`+
    `<span class="pill">有图 <b>${items.filter(it=>it.icon_count>0).length}</b></span>`+
    `<span class="pill">仅小图 <b>${items.filter(it=>it.only_small).length}</b></span>`+
    `<span class="pill">在奖池 <b>${items.filter(it=>it.in_pool).length}</b></span>`;
}
function cBuildFilters(items){
  const wrap=document.getElementById("fFashionWrap");
  if(!wrap)return;
  const famCnt=cCountBy(items,it=>it.family);
  const qCnt=cCountBy(items,it=>String(it.quality));
  const chip=(label,on,n,fn)=>{
    const b=document.createElement("button");
    b.type="button";b.className="fr-chip";b.textContent=label;
    b.setAttribute("aria-pressed",String(on));
    if(n!=null){const s=document.createElement("span");s.className="n";s.textContent=String(n);b.appendChild(s);}
    b.addEventListener("click",fn);
    return b;
  };
  const redraw=()=>{cSyncUrl();wrap.innerHTML="";cBuildFilters(items);};
  const grp=(title,chips)=>{const g=document.createElement("span");g.className="fr-grp";
    const em=document.createElement("em");em.textContent=title;g.appendChild(em);
    chips.forEach(c=>g.appendChild(c));return g;};
  const box=document.createElement("div");box.className="fr-filters";
  const fams=[chip("全部",CQ.fam.size===0,null,()=>{CQ.fam.clear();redraw();render();})]
    .concat(Object.keys(famCnt).sort((a,b)=>famCnt[b]-famCnt[a]).map(k=>chip(k,CQ.fam.has(k),famCnt[k],()=>{
      if(CQ.fam.has(k))CQ.fam.delete(k);else CQ.fam.add(k);redraw();render();})));
  box.appendChild(grp("类型",fams));
  const qlabel={"1":"基础芯片","2":"高级芯片","3":"特级芯片"};
  const qs=Object.keys(qCnt).sort().map(k=>chip(qlabel[k]||("品质"+k),CQ.q.has(k),qCnt[k],()=>{
    if(CQ.q.has(k))CQ.q.delete(k);else CQ.q.add(k);redraw();render();}));
  box.appendChild(grp("品质",qs));
  box.appendChild(grp("图标",["有图","仅小图"].map(l=>chip(l,CQ.img===l,
    l==="有图"?items.filter(it=>it.icon_count>0).length:items.filter(it=>it.only_small).length,
    ()=>{CQ.img=(CQ.img===l)?"":l;redraw();render();}))));
  const sortSel=document.createElement("select");
  sortSel.id="cSort";sortSel.setAttribute("aria-label","排序依据");
  sortSel.title="排序：编号 = 道具行 id（无道具行用 chip_type 行键）；无道具行固定排最后";
  [["no_desc","编号 ↓ 大→小（默认）"],["no_asc","编号 ↑ 小→大"]]
    .forEach(([v,t])=>{const o=document.createElement("option");o.value=v;o.textContent=t;sortSel.appendChild(o);});
  sortSel.value=CQ.sort||"no_desc";
  sortSel.addEventListener("change",()=>{CQ.sort=sortSel.value;cSyncUrl();render();});
  box.appendChild(sortSel);
  wrap.appendChild(box);
  wrap.style.display="";
}

/* ══ D2 详情灯箱（2026-10-29）：点芯片卡 → 中央大卡飘在最前 ══
   交互契约（对齐主流 modal-as-route 实践）：
     · 打开 pushState(?id=…)、关闭 replaceState 去参 → 浏览器后退=关闭、详情链接可分享可刷新
     · ←/→ / 侧缩略卡切换用 replaceState，不污染历史
     · Esc 分级：对比模式先退回单卡，再按才关灯箱
     · role=dialog + 焦点陷阱 + 关闭还原焦点；开灯箱期间锁 body 滚动
     · 点图打开既有大图查看器（frBox z-index 更高，属同站惯例，不算堆叠模态） */
const C2={open:false,idx:-1,pinned:null,pushed:false,lastFocus:null,lv:0,lvP:0,chips:[],prov:null,html:null};
let c2FrWasOpen=false;
/* 各板条目的唯一 id：芯片/时装用 it.id；皮肤用 skin_id??id；候选板用结构键；核芯用道具行 id */
function c2IdOf(it){
  if(C2.prov&&C2.prov.idOf)return String(C2.prov.idOf(it));
  return String(it.id??it.item_id??"");
}
function c2ParamId(){
  try{return new URLSearchParams(location.search).get("id")||"";}catch(e){return "";}
}
function c2UrlFor(it){
  try{
    const u=new URLSearchParams(location.search);
    if(it)u.set("id",c2IdOf(it));else u.delete("id");
    return location.pathname+"?"+u.toString();
  }catch(e){return null;}
}
function c2Ensure(){
  let m=document.getElementById("c2mask");
  if(m)return m;
  m=document.createElement("div");
  m.id="c2mask";m.className="c2-mask";m.style.display="none";
  m.innerHTML=`<div class="c2-stage" role="dialog" aria-modal="true" aria-labelledby="c2title"></div>`;
  m.addEventListener("click",e=>{if(e.target===m)c2Close();});
  document.body.appendChild(m);
  window.addEventListener("popstate",c2OnPop);
  /* 大图查看器状态探测：frBox 开着时，Esc/方向键归它管（capture 先于 fr 的 bubble 监听执行） */
  document.addEventListener("keydown",()=>{
    const fb=document.getElementById("frBox");
    c2FrWasOpen=!!(fb&&fb.style.display==="flex");
  },true);
  document.addEventListener("keydown",c2Keys);
  return m;
}
function c2SideHTML(i,cls){
  if(C2.chips.length<2)return "";
  const n=C2.chips.length;
  const j=((i%n)+n)%n;
  const it=C2.chips[j];
  if(!it)return "";
  const img=((it._media||{}).images||[])[0];
  return `<div class="c2-side ${cls}" data-act="side" data-dir="${cls==="l"?-1:1}" title="切换到：${esc(it.name||it.id)}" role="button" tabindex="0">
    ${img?`<img src="${esc(img.png)}" alt="">`:""}
    <div class="t">${esc(it.name||it.id)}</div><div class="s">点击切换</div></div>`;
}
function c2HeadHTML(it,mode){
  const q=it.quality||1;
  const isP=!!(C2.pinned&&String(C2.pinned.id)===String(it.id));
  const pinBtn=mode==="main"
    ?(isP
      ?`<button type="button" class="c2-pin on" data-act="pin" title="取消钉住这张芯片">已钉住 ✓</button>`
      :`<button type="button" class="c2-pin" data-act="pin" title="${C2.pinned?"改钉这张（替换右侧对比栏）":"钉住这张：它靠到屏幕右侧，详情自动关闭，点列表任意芯片即可同屏对比"}">${C2.pinned?"改钉这张":"钉住对比"}</button>`)
    :"";
  return `<div class="c2-head">
    <span class="c2-name"${mode==="main"?` id="c2title"`:""}>${esc(it.name||it.id)}</span>
    <span class="fr-quality q${q}" title="品质档 chip_quality=${esc(String(q))}">${esc(it.quality_label||("品质"+q))}</span>
    <span class="fr-part b-chip">${esc(it.family||"未标注")}</span>
    <span class="c2-no">编号 ${esc(String(cNo(it)))}${it.max_chip_level?` · 最高 Lv${esc(String(it.max_chip_level))}`:""}</span>
    ${pinBtn}
    ${mode==="main"?`<button type="button" class="c2-x" data-act="close">关闭 ✕</button>`:""}
  </div>`;
}
function c2RailHTML(it){
  const m=it._media||{},imgs=Array.isArray(m.images)?m.images:[];
  if(!imgs.length){
    const ph=typeof m.placeholder==="string"?m.placeholder:(m.placeholder&&m.placeholder.png);
    return `<div class="c2-rail"><div class="big">${ph?`<img src="${esc(ph)}" alt="占位">`:`<span class="fr-dur">无图标</span>`}</div></div>`;
  }
  const bigIdx=imgs.findIndex(x=>x.suffix==="b");
  const bi=bigIdx>=0?bigIdx:0;
  const smalls=imgs.filter((x,i)=>i!==bi);
  return `<div class="c2-rail">
    <div class="big fr-zoom" data-idx="${bi}" title="点击看大图 · ${esc(imgs[bi].base||"")}"><img src="${esc(imgs[bi].png)}" alt=""></div>
    ${smalls.length?`<div class="smalls">${smalls.map(x=>{const i=imgs.indexOf(x);
      return `<figure class="fr-zoom" data-idx="${i}" title="点击看大图 · ${esc(x.base||"")}"><img src="${esc(x.png)}" alt=""></figure>`;}).join("")}</div>`:""}
  </div>`;
}
function c2LvSelHTML(it,panel){
  const n=(it.levels||[]).length;
  if(!n)return "";
  const cur=panel==="p"?C2.lvP:C2.lv;
  return `<div style="font-size:11px;color:var(--muted-2,#a1a1aa);margin:2px 0 4px">档位选择 · 点击定位并高亮该行</div>
    <div class="c2-lvrow" aria-label="档位选择">`+
    Array.from({length:n},(_,i)=>`<button type="button" class="c2-lvchip${cur===i+1?" on":""}" data-act="lv" data-panel="${panel||"m"}" data-lv="${i+1}">${i+1}</button>`).join("")+
    `</div>`;
}
function c2LevelTable(it,withIds,panel){
  const rows=(it.levels||[]).map((lv,i)=>{
    const sim=Object.entries(lv.sim||{}).map(([k,v])=>`${k}=${v}`).join(" · ");
    const dec=(lv.decompose||[]).map(([a,b])=>`${a}×${b}`).join(" ");
    const tip=[sim?("UI "+sim):"",dec?("拆解 "+dec):""].filter(Boolean).join("｜");
    return `<tr${withIds?` data-lv="${i+1}"`:""} title="${esc(tip)}">
      <td class="lv-tier">${lv.level==null?"—":lv.level}</td>
      <td class="lv-prof">${lv.proficiency_point==null?"—":lv.proficiency_point}</td>
      <td class="lv-num num">${(lv.params||[]).length?lv.params.map(x=>cNum(x)).join(" / "):"—"}</td>
      <td class="lv-desc">${cRich(lv.desc||"")}</td></tr>`;
  }).join("");
  return `<table class="chip-lv c2-lv"${panel?` data-panel="${panel}"`:""}><thead><tr><th>档</th><th>熟练度</th><th>数值(base_params)</th><th>属性</th></tr></thead><tbody>${rows}</tbody></table>`;
}
function c2BodyHTML(it,mode){
  if(C2.prov)return C2.prov.body(it,mode);
  const isDock=mode==="dock";
  const desc=(it.desc||it.effect_desc)?`<p class="c2-desc">${cRich(it.desc||it.effect_desc)}</p>`:"";
  const lvsel=c2LvSelHTML(it,isDock?"p":"m");
  const table=c2LevelTable(it,!isDock,isDock?"p":"m");
  const audit=`<details class="sub-tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="fr-kv">${cKvHtml(it)}</div></details>`;
  return (isDock?"":c2HeadHTML(it,"main"))+c2RailHTML(it)+desc+lvsel+table+audit;
}
function c2Render(){
  const m=c2Ensure(),stage=m.querySelector(".c2-stage");
  const it=C2.chips[C2.idx];
  if(!it){c2HardClose();return;}
  const n=C2.chips.length;
  const foot=`<div class="c2-foot">
    <button type="button" class="c2-nav" data-act="prev">‹ 上一个</button>
    <span>${C2.idx+1} / ${n}${C2.pinned?" · 右侧对比中":""} · ←/→ 切换 · Esc 关闭</span>
    <button type="button" class="c2-nav" data-act="next">下一个 ›</button></div>`;
  const isSkinA=(C2.prov===SKIN_D2);
  m.classList.toggle("skinwide",isSkinA);
  stage.innerHTML=c2SideHTML(C2.idx-1,"l")+
    `<div class="c2-card${isSkinA?" skin-a":""}">${c2BodyHTML(it,"main")}${foot}</div>`+
    c2SideHTML(C2.idx+1,"r");
  stage.querySelectorAll("[data-act]").forEach(el=>{
    el.addEventListener("click",ev=>{
      ev.stopPropagation();
      const act=el.dataset.act;
      if(act==="close")c2Close();
      else if(act==="pin")c2TogglePin();
      else if(act==="prev")c2Go(-1);
      else if(act==="next")c2Go(1);
      else if(act==="lv")c2PickLv(parseInt(el.dataset.lv||"1",10),el.dataset.panel);
      else if(act==="side")c2Go(parseInt(el.dataset.dir||"0",10));
    });
    el.addEventListener("keydown",ev=>{
      if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();ev.stopPropagation();el.click();}
    });
  });
  stage.querySelectorAll(".fr-zoom").forEach(el=>{
    if(!el.title||!el.title.includes("大图"))el.title="点击看大图"+(el.title?" · "+el.title:"");
    el.addEventListener("click",ev=>{
      ev.stopPropagation();
      const it2=C2.chips[C2.idx];if(!it2)return;
      frOpen(it2.id,parseInt(el.dataset.idx||"0",10));
    });
  });
  bindD2ImgZoom(stage);
  animAutoPlay(stage);   /* 2026-10-30：详情里直接播放动态头像 */
  if(isSkinA)c2SkinNav(stage);
  if(!stage.contains(document.activeElement)){
    const f=stage.querySelector('[data-act="close"],[data-act="pin"]');
    if(f)f.focus();
  }
  stage.querySelectorAll(".c2-embed details,.c2-split details").forEach(d=>{
    if(d.classList.contains("tech")||d.classList.contains("sub-tech")||d.classList.contains("vv-tech"))d.open=false;
    else d.open=true;
  });
  c2ApplyHl();
}
function c2ApplyHl(){
  const m=document.getElementById("c2mask");
  if(m&&C2.lv){
    const tr=m.querySelector(`.c2-lv[data-panel="m"] tr[data-lv="${C2.lv}"]`);
    if(tr){tr.classList.add("hl");
      const card=tr.closest(".c2-card");
      if(card)tr.scrollIntoView({block:"nearest",behavior:"smooth"});}
  }
  const dk=document.getElementById("c2dock");
  if(dk&&C2.lvP){
    const tr=dk.querySelector(`.c2-lv[data-panel="p"] tr[data-lv="${C2.lvP}"]`);
    if(tr){tr.classList.add("hl");
      tr.scrollIntoView({block:"nearest",behavior:"smooth"});}
  }
}
/* ── 对比钉停靠栏（B 方案式）：钉住的芯片靠右独立成栏，列表左移恢复可点 ── */
function c2DockEnsure(){
  let d=document.getElementById("c2dock");
  if(d)return d;
  d=document.createElement("aside");
  d.id="c2dock";d.className="c2-dock";
  d.innerHTML=`<div class="c2-dock-head">
      <span class="c2-dock-tag">对比钉</span>
      <span class="c2-dock-name"></span>
      <button type="button" data-act="unpin" title="取消钉住，收起本栏">取消钉住 ✕</button>
    </div><div class="c2-dock-body"></div>`;
  document.body.appendChild(d);
  return d;
}
function c2DockRender(){
  const d=c2DockEnsure(),it=C2.pinned;
  if(!it){c2Unpin();return;}
  d.querySelector(".c2-dock-name").textContent=(C2.prov&&C2.prov.name?C2.prov.name(it):(it.name||it.id));
  d.querySelector(".c2-dock-body").innerHTML=
    `<div class="c2-hint" style="margin:0 0 8px">已钉住 · 点列表任意卡片即可同屏对比 · Esc 取消钉住</div>`+
    c2BodyHTML(it,"dock");
  d.querySelectorAll("[data-act]").forEach(el=>{
    el.addEventListener("click",ev=>{
      ev.stopPropagation();
      if(el.dataset.act==="unpin")c2Unpin();
      else if(el.dataset.act==="lv")c2PickLv(parseInt(el.dataset.lv||"1",10),"p");
    });
    el.addEventListener("keydown",ev=>{
      if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();ev.stopPropagation();el.click();}
    });
  });
  d.querySelectorAll(".fr-zoom").forEach(el=>{
    el.addEventListener("click",ev=>{
      ev.stopPropagation();
      if(C2.pinned)frOpen(C2.pinned.id,parseInt(el.dataset.idx||"0",10));
    });
  });
  bindD2ImgZoom(d.querySelector(".c2-dock-body")||d);
  c2ApplyHl();
}
function c2DockShow(){
  c2DockEnsure().classList.add("on");
  document.body.classList.add("c2-dockopen");
  c2DockRender();
}
function c2Unpin(){
  C2.pinned=null;C2.lvP=0;
  const d=document.getElementById("c2dock");
  if(d)d.classList.remove("on");
  document.body.classList.remove("c2-dockopen");
  if(C2.open)c2Render();
}
function c2PickLv(n2,panel){
  if(panel==="p"){
    C2.lvP=(C2.lvP===n2)?0:n2;
    c2DockRender();
  }else{
    C2.lv=(C2.lv===n2)?0:n2;
    c2Render();
  }
}
function c2JumpTo(i){
  if(!C2.chips[i])return;
  C2.idx=i;C2.lv=0;
  const url=c2UrlFor(C2.chips[i]);
  if(url){try{history.replaceState(history.state,"",url);}catch(e){}}
  c2Render();
}
function c2Go(d){
  const n=C2.chips.length;
  if(!n)return;
  c2JumpTo(((C2.idx+d)%n+n)%n);
}
function c2TogglePin(){
  const it=C2.chips[C2.idx];
  if(!it)return;
  if(C2.pinned&&c2IdOf(C2.pinned)===c2IdOf(it)){c2Unpin();return;}
  C2.pinned=it;C2.lvP=0;
  c2DockShow();          // 钉住 → 右侧停靠栏出现，列表左移恢复可点
  if(C2.open)c2Close();  // 详情自动关闭：左侧留给用户自己点选对比卡片，不做两边同款
}
function c2Show(){
  C2.open=true;C2.lastFocus=document.activeElement;
  const m=c2Ensure();
  c2Render();
  m.style.display="flex";
  requestAnimationFrame(()=>m.classList.add("on"));
  document.body.classList.add("c2-lock");
}
function c2Open(i,opt){
  opt=opt||{};
  if(!C2.chips[i])return;
  C2.idx=i;C2.lv=0;
  c2Show();
  if(opt.push!==false){
    const url=c2UrlFor(C2.chips[i]);
    if(url){try{history.pushState({c2:1},"",url);C2.pushed=true;}catch(e){}}
  }
}
function c2Close(){
  if(C2.pushed){history.back();return;}   // 回退触发 popstate → c2HardClose，历史不留脏项
  c2HardClose();
  const url=c2UrlFor(null);
  if(url){try{history.replaceState(history.state,"",url);}catch(e){}}
}
function c2HardClose(){
  C2.open=false;C2.lv=0;C2.pushed=false;   // 钉住（C2.pinned）不随灯箱关闭消失，停靠栏继续在
  const m=document.getElementById("c2mask");
  if(m){m.classList.remove("on");
    setTimeout(()=>{if(!C2.open)m.style.display="none";},200);}
  document.body.classList.remove("c2-lock");
  if(C2.lastFocus&&C2.lastFocus.focus){try{C2.lastFocus.focus();}catch(e){}}
}
function c2Keys(e){
  if(c2FrWasOpen)return;
  if(e.key==="Escape"){
    if(C2.open){e.preventDefault();c2Close();}
    else if(C2.pinned){e.preventDefault();c2Unpin();}
    return;
  }
  if(!C2.open)return;
  if(e.key==="ArrowLeft"){e.preventDefault();c2Go(-1);}
  else if(e.key==="ArrowRight"){e.preventDefault();c2Go(1);}
  else if(e.key==="Tab"){
    const m=document.getElementById("c2mask");if(!m)return;
    const f=[...m.querySelectorAll("button,[href],input,select,textarea,[tabindex]:not([tabindex='-1'])")]
      .filter(el=>el.offsetParent!==null);
    if(!f.length)return;
    const first=f[0],last=f[f.length-1];
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
  }
}
function c2OnPop(){
  const id=c2ParamId();
  if(id){
    const i=C2.chips.findIndex(it=>c2IdOf(it)===id);
    if(i>=0){C2.idx=i;C2.lv=0;C2.lvP=0;C2.pushed=false;
      if(C2.open)c2Render();else c2Show();
      return;}
  }
  if(C2.open)c2HardClose();
}
function c2Resync(){
  if(C2.pinned){
    const pi=C2.chips.findIndex(x=>c2IdOf(x)===c2IdOf(C2.pinned));
    if(pi<0)c2Unpin();
    else{C2.pinned=C2.chips[pi];c2DockRender();}
  }
  if(!C2.open)return;
  const cur=C2.chips[C2.idx];
  const i=cur?C2.chips.findIndex(x=>c2IdOf(x)===c2IdOf(cur)):-1;
  if(i<0){c2HardClose();return;}
  C2.idx=i;
  c2Render();
}
function c2DeepLink(){
  const id=c2ParamId();
  if(!id||!C2.chips.length)return;
  const i=C2.chips.findIndex(it=>c2IdOf(it)===id);
  if(i>=0)c2Open(i,{push:false});
}
/* ══ 通用板 provider：人物时装 / 武器皮肤（含候选板）/ 异变核芯 ══
   这三块板直接复用各自板卡的完整详情 HTML（render 时逐卡缓存到 C2.html），
   嵌入灯箱/停靠栏时由 CSS 去卡壳、强制展开全部折叠区（.c2-embed 规则）。 */
function embedD2Body(it,mode){
  const id=c2IdOf(it);
  /* 优先用完整版（含详情折叠区）；芯片等自带 body 的板不走这里 */
  let html=((C2.htmlFull||{})[id])||((C2.html||{})[id])||"（无渲染数据）";
  /* 2026-10-29：名册类板（击败播报/头像等）卡内详情是 hidden 的 i-detail，嵌入 D2 时展开；
     载具卡 fdesc/tech 改为 hidden 上卡面，嵌入时同样解除；并去掉卡头内联 toggle */
  html=html.replace(/<div class="i-detail" hidden>/g,'<div class="i-detail">')
           .replace(/(<details class="(?:fdesc|tech)"[^>]*) hidden>/g,"$1>")
           .replace(/onclick="toggleDetail\(this\)"/g,"");
  const embed=`<div class="c2-embed">${html}</div>`;
  return mode==="dock"?embed:c2BarHTML(it,(C2.prov&&C2.prov.meta)?C2.prov.meta(it):"","main")+embed;
}
function c2BarHTML(it,metaHtml,mode){
  const isP=!!(C2.pinned&&c2IdOf(C2.pinned)===c2IdOf(it));
  const nm=(C2.prov&&C2.prov.name)?C2.prov.name(it):(it.name||it.id);
  return `<div class="c2-head">
    <span class="c2-name"${mode==="main"?` id="c2title"`:""}>${esc(nm)}</span>
    ${metaHtml||""}
    ${mode==="main"
      ?(isP
        ?`<button type="button" class="c2-pin on" data-act="pin" title="取消钉住这张">已钉住 ✓</button>`
        :`<button type="button" class="c2-pin" data-act="pin" title="${C2.pinned?"改钉这张（替换右侧对比栏）":"钉住这张：它靠到屏幕右侧，详情自动关闭，点列表任意卡片即可同屏对比"}">${C2.pinned?"改钉这张":"钉住对比"}</button>
          <button type="button" class="c2-x" data-act="close">关闭 ✕</button>`)
      :""}
  </div>`;
}
const FR_D2={
  idOf:it=>it.id,
  body:embedD2Body,
  meta:it=>{
    const bk=frBuckets(it),cls=FR_BUCKET_CLS[bk[0]]||"other";
    const partCn=(it.all_parts&&it.all_parts.length?it.all_parts.map(p=>COMMON_PART_CN[p]||p).join(" / "):(COMMON_PART_CN[it.part]||it.part||""));
    const mid=(it.model_id!=null)?it.model_id:((it.model_ids&&it.model_ids[0])!=null?it.model_ids[0]:null);
    return `<span class="fr-part b-${cls}">${esc(partCn||"部位未标注")}</span>`+
      `<span class="fr-charm${it.charm_value?"":" na"}">${it.charm_value?"魅力 "+esc(it.charm_value):"魅力 —"}</span>`+
      (mid!=null?`<span class="fr-model">model ${esc(mid)}</span>`:"");
  }
};
/* 皮肤板 D2 主卡：方案A 左图右文 + 方案一（右栏粘性锚点条、表现类目徽章跳转）
   + 方案三（品级色系贯穿：海报描边/IP角标叠图/色条标题/引用块描述）；
   品级色取站内 grade-badge 同系色；停靠栏（dock）仍走 embedD2Body 单栏复用 */
const GRADE_ACCENT={
  t6:["#6f2247","#f7d9e4","#fdf3f6"],t5:["#8a6a1c","#f7ecc0","#fdf9ec"],
  t4:["#6a4fe0","#e7e4fb","#f3f1fd"],t3:["#1d4ed8","#cfe0f9","#eff5fd"],
  t2:["#52525b","#e4e4e7","#fafafa"],unknown:["#71717a","#ececf0","#fafafa"]};
function skinD2BodyA(it,mode){
  if(mode!=="main")return embedD2Body(it,mode);
  const name=it.name_display||it.name||it.display_name||("未命名皮肤 · ID "+(it.skin_id??it.id));
  const tier=gradeTier(it);
  const wtCn=it.weapon_type_cn||typeCN(it.weapon_type_label||pick(it,"weapon_type_label")||"");
  const ip=it.ip_liaison||it.ip_now||"";
  const ls=listingOf(it);
  const stTxt=ls?lsLabel(ls):"";
  const rows=[];
  rows.push(["品级",`<span class="skin-tag grade-badge ${tier.cls}">${esc(tier.label)}</span>`]);
  if(wtCn)rows.push(["武器类型",esc(wtCn)]);
  if(ip)rows.push(["联动IP",`<span style="color:var(--gc,#534ab7)">${esc(ip)}</span>`]);
  if(it.sale_date)rows.push(["上架",esc(it.sale_date)+(stTxt?` · ${esc(stTxt)}`:"")]);
  rows.push(["皮肤ID",esc(String(it.skin_id??it.id))]);
  const facts=rows.map(([k,v])=>`<div class="frow"><span class="k">${esc(k)}</span><span class="v">${v}</span></div>`).join("");
  const desc=it.official_desc?(isRichText(it.official_desc)?richText(it.official_desc):esc(it.official_desc)):"";
  /* 2026-10-29（用户口径）：特效与战斗表现放左栏（海报栏，空位大）；皮肤音效放右栏描述下方 */
  const perfHtml=renderPerfDetail(it);
  const audioHtml=renderSkinAudio(it);
  const rest=renderSkinDetail(it,{noPreview:true,noDesc:true,noPerf:true,noAudio:true,anchor:true});
  const acc=GRADE_ACCENT[tier.cls]||GRADE_ACCENT.unknown;
  const vars=`--gc:${acc[0]};--gsoft:${acc[1]};--gbg:${acc[2]}`;
  /* 表现已移至左栏常驻，锚点条不再放「表现」 */
  const toc=[["sec-desc","描述",!!desc],["sec-var","时限变体",rest.includes(`id="sec-var"`)],
    ["sec-ref","参考",rest.includes(`id="sec-ref"`)],
    ["sec-tech","技术",rest.includes(`id="sec-tech"`)]]
    .filter(([,lb,ok])=>ok)
    .map(([id,lb])=>`<a data-t="${id}">${lb}</a>`).join("");
  return c2BarHTML(it,"","main")+`<div class="c2-split" style="${vars}">
    <div class="c2-split-l">
      <div class="c2-posterwrap">${renderSkinMedia(it,name)}${ip?`<span class="c2-ipbadge">×${esc(ip)}</span>`:""}</div>
      <div class="c2-gbar"></div>
      ${renderSkinPreview3D(it)}
      <div class="c2-facts">${facts}</div>
      ${perfHtml?`<div id="sec-perf" class="c2-lperf">${perfHtml}</div>`:""}
    </div>
    <div class="c2-split-r">
      ${toc?`<div class="c2-toc">${toc}</div>`:""}
      ${desc?`<p class="c2-desc0" id="sec-desc">${desc}${skinDescMark(it)}</p>`:""}
      ${audioHtml?`<div id="sec-audio">${audioHtml}</div>`:""}
      ${rest}
    </div>
  </div>`;
}
const SKIN_D2={
  idOf:it=>it.skin_id??it.id??"",
  name:it=>it.name_display||it.name||it.display_name||("未命名皮肤 · ID "+(it.skin_id??it.id)),
  body:skinD2BodyA,
  meta:()=>""
};
/* 皮肤 D2 右栏导航（方案一）：锚点条点击跳转+高亮、表现徽章跳对应行、滚动时锚点跟随 */
function c2SkinNav(stage){
  const r=stage.querySelector(".c2-split-r");if(!r)return;
  const flash=el=>{if(!el)return;el.classList.remove("flash");void el.offsetWidth;el.classList.add("flash");};
  const go=id=>{const t=r.querySelector(`#${id}`);if(!t)return;t.scrollIntoView({behavior:"smooth",block:"start"});flash(t);};
  r.querySelectorAll(".c2-toc a").forEach(a=>{
    a.addEventListener("click",ev=>{
      ev.preventDefault();ev.stopPropagation();
      r.querySelectorAll(".c2-toc a").forEach(x=>x.classList.remove("act"));
      a.classList.add("act");
      go(a.dataset.t);
    });
  });
  r.addEventListener("scroll",()=>{
    let cur=null;
    r.querySelectorAll("[id^='sec-']").forEach(s=>{
      const rt=r.getBoundingClientRect();
      if(s.getBoundingClientRect().top<rt.top+72)cur=s.id;
    });
    if(cur)r.querySelectorAll(".c2-toc a").forEach(x=>x.classList.toggle("act",x.dataset.t===cur));
  },{passive:true});
}
const CAND_D2={
  idOf:it=>it.structural_record_key||(it.id??""),
  name:it=>it.name_display||it.candidate_name||("未命名皮肤 · ID "+(it.structural_record_key||it.id)),
  body:embedD2Body,
  meta:it=>{
    const tier=gradeTier({level:pick(it,"level")});
    const candType=pick(it,"weapon_type_label");
    const st=it.name_status||(it.candidate_name?"candidate":"unresolved");
    return `<span class="skin-tag grade-badge ${tier.cls}">${esc(tier.label)}</span>`+
      (candType?`<span class="skin-tag">武器种类 ${esc(typeCN(candType))}</span>`:"")+
      `<span class="skin-tag">${st==="candidate"?"名称待确认":"未命名"}</span>`+
      `<span class="c2-no">ID ${esc(it.structural_record_key||it.id)}</span>`;
  }
};
/* 2026-10-30（用户口径）：D2 详情内点图片 = 看大图（卡面点图才是开子卡）。
   图轨缩略图（.fr-zoom）走各自的灯箱绑定；其余图片（皮肤海报 / 核芯立绘 / 名册头像 /
   3D 材质球等）统一挂到同一组大图里，可左右翻。 */
function bindD2ImgZoom(scope){
  if(!scope)return;
  scope.querySelectorAll("img").forEach(img=>{
    if(img.closest(".fr-zoom"))return;          /* 图轨另有绑定 */
    if(img.closest(".c2-side"))return;          /* 侧栏缩略图=切换条目 */
    if(img.closest("video,audio"))return;
    if(img.closest(".ph,.nofig"))return;         /* 客户端占位图 / 缺图占位，无可放大 */
    if(img.dataset.d2zoom)return;
    img.dataset.d2zoom="1";
    img.classList.add("c2-imgzoom");
    if(!img.title||!img.title.includes("大图"))img.title="点击看大图"+(img.alt?" · "+img.alt:"");
    img.addEventListener("click",ev=>{
      ev.preventDefault();ev.stopPropagation();
      frOpenIn(scope,img);
    });
  });
}
/* 2026-10-29（用户选「1+3 结合」）：方案三 hero 压顶 + 方案一 特技金卡 + 升星阶梯。
   配色全走主题变量（aftermath 暗色 / shadcn 亮色自适应），层次只靠字号/边框/留白 */
function coreD2PickMedia(it){
  const m=it._media||{},imgs=m.images||[];
  const skill=imgs.find(x=>x.suffix==="skill"||x.kind==="核芯特技")||null;
  const main=imgs.find(x=>x!==skill)||null;
  return {skill,main,ph:m.placeholder||""};
}
function coreD2BodyA(it,mode){
  const content=(()=>{
    const {skill,main,ph}=coreD2PickMedia(it);
    const gl=it.grade_label||it.grade_clean;
    const gc=it.grade_color?` g-${esc(it.grade_color)}`:"";
    const maxS=it.max_star==null?"":String(it.max_star);
    const heroImg=main?main.png:(ph||"");
    const hero=`<div class="cd-hero">
      <div class="cd-hero-txt">
        <span class="cd-kicker">异变核芯</span>
        <div class="cd-name">${esc(it.name||it.display_name||it.id)}</div>
        <div class="cd-chips">${gl?`<span class="grade-pill${gc}">${esc(gl)}</span>`:""}${it.element?`<span class="cd-chip">${esc(it.element)}属性</span>`:""}${it.weapon_type_display?`<span class="cd-chip">${esc(it.weapon_type_display)}</span>`:""}<span class="cd-chip">满星 ${maxS?esc(maxS)+"★":"待定"}</span></div>
      </div>
      ${heroImg?`<figure class="cd-hero-img"><img src="${esc(heroImg)}" alt="" loading="lazy"></figure>`:""}
    </div>`;
    const skillCard=it.skill_desc?`<div class="cd-skill">
      <div class="cd-skill-head">${skill?`<img src="${esc(skill.png)}" alt="">`:""}<span>专属特技</span></div>
      <div class="cd-skill-txt">${richText(String(it.skill_desc))}</div>
    </div>`:"";
    const segs=(it.rank_star_segments&&typeof it.rank_star_segments==="object")
      ?Object.keys(it.rank_star_segments).sort((a,b)=>Number(a)-Number(b)).map(s=>
        `<div class="cd-star${maxS&&s===maxS?" max":""}"><div class="cd-sn">${esc(s)}★</div><div class="cd-st">${richText(zhText(String(it.rank_star_segments[s])))}</div></div>`).join("")
      :"";
    const ladder=segs?`<div class="cd-stars">${segs}</div>`:"";
    const desc=it.desc?`<div class="cd-sec"><span class="cd-k">描述</span>${richText(zhText(String(it.desc)))}</div>`:"";
    /* 审计与溯源全折进技术详情；2026-10-29 二次口径：证据等级(结构已解析)/状态标签(静态配置)
       在子卡里连技术详情也一并删除，不再出现 */
    const sumKeys=new Set(["item_id","grade_clean","grade_name","grade_color","grade_label",
      "max_star","star_text","skill_icon","skill_desc","weapon_type_display","weapon_type_label",
      "weapon_type_code","rank_star_segments","desc","element"]);
    const allPairs=Object.entries(it).filter(([k])=>!FIXED.has(k)&&!sumKeys.has(k)&&it[k]!==null&&it[k]!=="");
    const audit=renderTechSection([...allPairs,["source",it.source]]);
    return `<div class="core-d2">${hero}${skillCard}${ladder}${desc}${audit}</div>`;
  })();
  return mode==="dock"?content:c2BarHTML(it,(C2.prov&&C2.prov.meta)?C2.prov.meta(it):"","main")+content;
}
/* 2026-10-29：名册类板（击败播报 / 头像头像框名片框）与载具板通用 D2——
   复用网格卡缓存 HTML，嵌入时展开卡内详情；meta 给 类型 + ID 两个轻标签 */
const ROSTER_D2={
  idOf:it=>it.id,
  name:it=>it.name||it.display_name||it.id,
  body:embedD2Body,
  meta:it=>{
    const kind=it.kind||it.vehicle_class||"";
    const idLabel=(DATA&&DATA.meta&&DATA.meta.id_label)||"ID";
    return (kind?`<span class="skin-tag">${esc(kind)}</span>`:"")+
      `<span class="c2-no">${esc(idLabel)} ${esc(it.item_id??it.vehicle_id??it.id)}</span>`;
  }
};
const CORE_D2={
  idOf:it=>it.item_id??it.id??"",
  name:it=>it.name||it.display_name||it.id,
  body:coreD2BodyA,
  meta:it=>{
    const gl=it.grade_label||it.grade_clean;
    const gc=it.grade_color?` g-${esc(it.grade_color)}`:"";
    return (gl?`<span class="grade-pill${gc}">${esc(gl)}</span>`:"")+
      `<span class="skin-tag">星上限 ${it.max_star==null?"待定":esc(it.max_star)}</span>`+
      (it.weapon_type_display?`<span class="skin-tag">${esc(it.weapon_type_display)}</span>`:"")+
      `<span class="c2-no">道具ID ${esc(it.item_id??it.id)}</span>`;
  }
};
/* 表现类目徽章已删（2026-10-29，与列表冗余）：相关委托一并移除 */
/* 点卡开详情（capture 阶段：赶在皮肤卡的行内 toggleSkin、核芯卡的 toggleDetail 之前拦下）；
   卡面空白处整体可点；summary/按钮/链接等已有交互的区域不劫持。
   2026-10-30（用户口径）：所有能开 D2 子卡的板，卡面点图片（fr-zoom 图轨）一律开子卡，
   不再开大图；大图入口只留在 D2 详情内部。+N 按钮同理。 */
document.addEventListener("click",e=>{
  if(C2.open)return;
  const zt=e.target.closest(".fr-zoom");
  if(zt){
    /* 点在图轨缩略图 / +N 上：所属卡能开 D2 就放行给 D2，否则回落到灯箱 */
    const zc=zt.closest(".fcard,.i.roster,.i.nucleus,.skin-card");
    if(!(zc&&zc.closest("#grid")&&cardOpensD2(zc)))return;
  }else if(e.target.closest("summary,button,a,select,input,label,audio,video"))return;
  const card=e.target.closest(".chip-card,.fcard,.skin-card,.i.nucleus,.i.roster,.i.fcard.vcard");
  if(!card||!card.closest("#grid"))return;
  if(!cardOpensD2(card))return;
  const i=parseInt(card.dataset.cidx||"-1",10);
  if(i>=0&&C2.chips[i]){e.preventDefault();e.stopPropagation();c2Open(i,{push:true});}
},true);

const HUGE_STEP=500;
let hugeScrollBound=false;
let hugeLoading=false;
function hugePrepare(q,fe){
  DATA._query=q;
  const hay=DATA._hay,matched=[];
  for(let i=0;i<DATA.items.length;i++){
    const it=DATA.items[i];
    if(fe&&it.evidence!==fe)continue;
    if(partFilter.length&&!partFilter.includes(String(it.part??"")))continue;
    if(q&&!hay[i].includes(q))continue;
    matched.push(it);
  }
  DATA._hugeMatched=matched;
  DATA._hugeQ=q;
}
function hugeUpdateCount(total,shown){
  const cnt=document.getElementById("count");
  cnt.textContent=DATA._hugeQ
    ? `命中 ${total} 条（关键字「${DATA._hugeQ}」）· 已显示 ${shown}`
    : `全表 ${DATA.items.length} 条 · 已显示 ${shown} 条 · 共 ${total} 条可浏览`;
}
function hugeDraw(reset){
  if(!reset&&hugeLoading)return;
  hugeLoading=true;
  setTimeout(()=>{hugeLoading=false;},180);
  const matched=DATA._hugeMatched||[];
  const g=document.getElementById("grid");
  if(reset){DATA._hugeOffset=0;g.innerHTML="";}
  if(!matched.length){
    if(reset)g.innerHTML='<div class="empty">无匹配条目</div>';
    hugeUpdateCount(0,0);
    const bar=document.getElementById("hugeBar");if(bar)bar.remove();
    return;
  }
  if(reset)g.innerHTML="";
  const start=DATA._hugeOffset;
  const slice=matched.slice(start,start+HUGE_STEP);
  if(slice.length)g.insertAdjacentHTML("beforeend",slice.map(renderItemCard).join(""));
  DATA._hugeOffset=start+slice.length;
  const total=matched.length,shown=Math.min(DATA._hugeOffset,total);
  hugeUpdateCount(total,shown);
  const old=document.getElementById("hugeBar");
  if(shown<total){
    if(old)old.querySelector("button").textContent=`加载更多（剩余 ${total-shown} 条）`;
    else{
      const bar=document.createElement("div");
      bar.id="hugeBar";
      bar.style.cssText="text-align:center;padding:18px 0 30px";
      bar.innerHTML=`<button style="cursor:pointer;padding:9px 26px;border:1px solid #d4d4d8;border-radius:8px;background:#fff;font-size:13px">加载更多（剩余 ${total-shown} 条）</button>`;
      bar.querySelector("button").addEventListener("click",()=>hugeDraw(false));
      g.after(bar);
    }
    if(!hugeScrollBound){
      hugeScrollBound=true;
      window.addEventListener("scroll",()=>{
        const bar=document.getElementById("hugeBar");
        if(!bar)return;
        if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-700){
          hugeDraw(false);
          setTimeout(()=>{
            const bar2=document.getElementById("hugeBar");
            if(bar2&&window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-700)hugeDraw(false);
          },220);
        }
      },{passive:true});
    }
  }else if(old)old.remove();
}
/* 场景平衡表格：列可点排序；沿用既有自定义筛选（服型/来源）与搜索 */
let SB_SORT={key:"name",dir:1};
function sbVal(it,k){
  if(k==="场景编号")return (it["场景编号"]||"").replace(/[^0-9,，]/g,"");
  if(k==="服型")return it["服型"]||"";
  if(k==="加成下限")return Number(it.lower);
  if(k==="加成上限")return Number(it.upper);
  if(k==="生效最低攻击")return Number(it.min_attack);
  if(k==="来源类型")return it["来源类型"]||"";
  if(k==="加成区间")return it.range||"";
  return it.name||"";
}
function sbRender(items){
  const cols=["场景","场景编号","服型","加成下限","加成上限","加成区间","生效最低攻击","来源类型"];
  const sorted=items.slice().sort((a,b)=>{
    const k=SB_SORT.key,v1=sbVal(a,k),v2=sbVal(b,k);
    if(typeof v1==="number"&&typeof v2==="number"){
      if(v1!==v2)return (v1-v2)*SB_SORT.dir;
    }else{
      const c=String(v1).localeCompare(String(v2),"zh-CN");
      if(c)return c*SB_SORT.dir;
    }
    return String(a.name||"").localeCompare(String(b.name||""),"zh-CN");
  });
  const g=document.getElementById("grid");
  g.innerHTML="";
  const t=document.createElement("table");
  t.className="sbt";
  const thead=document.createElement("thead");
  const trh=document.createElement("tr");
  for(const c of cols){
    const th=document.createElement("th");
    th.textContent=c+(SB_SORT.key===c?(SB_SORT.dir>0?" ▲":" ▼"):"");
    th.onclick=()=>{
      if(SB_SORT.key===c)SB_SORT.dir*=-1;else{SB_SORT.key=c;SB_SORT.dir=1;}
      render();
    };
    trh.appendChild(th);
  }
  thead.appendChild(trh);t.appendChild(thead);
  const tb=document.createElement("tbody");
  for(const it of sorted){
    const tr=document.createElement("tr");
    const cells=[
      ["scene",it.name||""],
      ["num",(it["场景编号"]||"").replace(" 个：","")],
      ["",`<span class="tag">${esc(it["服型"]||"-")}</span>`],
      ["num",it.lower??"-"],
      ["num",it.upper??"-"],
      ["num",it.range||"-"],
      ["num",it.min_attack??"-"],
      ["", `<span class="tag">${esc(it["来源类型"]||"-")}</span>`],
    ];
    for(const [cls,val] of cells){
      const td=document.createElement("td");
      if(cls)td.className=cls;
      if(cls==="num")td.textContent=val; else td.innerHTML=String(val);
      tr.appendChild(td);
    }
    tb.appendChild(tr);
  }
  t.appendChild(tb);g.appendChild(t);
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${items.length} / ${DATA.items.length} 条`;
}

function render(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  if(DATA)DATA._query=q;
  const fe=document.getElementById("fEv").value;
  const fg=readGradeChecked();   // 勾选制：空集 = 全部品级（多选，OR 命中）
  const ft=document.getElementById("fType").value;
  const fi=document.getElementById("fIp").value;
  const frel=document.getElementById("fRelease").value;
  const fns=document.getElementById("fNameSt").value;
  // v1.3.1：皮肤渲染器（含品级/武器种类/上架状态/名称状态筛选）改为**数据驱动**，
// 不再硬编码旧板 id —— 否则 Workbench 板 weapon_skin_active 会走通用渲染器，两个状态筛选等于没生效。
const skinBoard=b==="weapon_skin_sfx_text_sources"
  ||(Array.isArray(DATA&&DATA.items)&&DATA.items.some(it=>it.listing_status!==undefined||it.skin_item_id!==undefined
      ||(Array.isArray(it.variant_items)&&(it.grade!==undefined||it.weapon_type_label!==undefined))));
  // 排列 = 依据(fOrder) + 方向(fDir)；兼容旧的合并值（id_asc/sale_desc 等）
  const dirSel=document.getElementById("fDir");
  function sortState(){
    const raw=document.getElementById("fOrder").value;
    const legacy={id_asc:["id","asc"],id_desc:["id","desc"],sale_asc:["sale","asc"],sale_desc:["sale","desc"]}[raw];
    if(legacy)return {key:legacy[0],dir:legacy[1]};
    return {key:raw||"id",dir:(dirSel&&dirSel.dataset.dir)||"desc"};
  }
  function keyOf(it){
    if(!skinBoard)return 0;
    return it.skin_id||it.structural_record_key||0;
  }
  function saleOf(it){const s=pick(it,"sale_ts");return typeof s==="number"?s:0;}
  const candidateSkinBoard=b==="weapon_skin_static_candidates_v01";
  if(Array.isArray(DATA._hay)&&DATA.items.length>=HUGE_TABLE_MIN){
    // 大表（全道具总表等）：轻量索引过滤 + 分批渲染（按钮/滚动触底加载），可浏览到全部条目。
    hugePrepare(q,fe);
    hugeDraw(true);
    return;
  }
  /* 预告专栏「是否还在预告窗口」（2026-11-01 修）。
     原逻辑只按 expect_date 一刀切：奖池期次一开赛，整批成员（上架日=期次开始日）
     连带「预计日已过但仍未上线」的皮肤被全部隐藏 —— 实测 14 条只剩 1 条、页面近空。
     新口径：
       ① 奖池成员：期次状态 进行中/未开始 ⇒ 仍在窗口；期次结束（period_end 已过）才剔除；
       ② 武器皮肤：源表 release_state 仍为未上线 ⇒ 仍在窗口；预计上架日已过只标
          「已过预计」（跳票 ≠ 过期），不再整条隐藏；
       ③ 其余：有明确上架日且已过 ⇒ 剔除。 */
  const TODAY0=new Date(); TODAY0.setHours(0,0,0,0);
  const upDayPassed=s=>{
    if(!/^\d{4}-\d{2}-\d{2}$/.test(String(s||'')))return false;
    const d=new Date(String(s)+'T00:00:00');
    return !isNaN(d) && d<=TODAY0;
  };
  const upState=it=>{
    if(it.period_end && upDayPassed(it.period_end))return 'ended';
    if(it.period_status==='进行中'||it.period_status==='未开始')return 'live';
    if(it.kind==='武器皮肤'||it.family_key==='UpcomingSkin')return 'skin';
    return upDayPassed(it.expect_date)?'expired':'pending';
  };
  const upExpired=it=>upState(it)==='expired';
  const upLate=it=>upState(it)==='skin'&&upDayPassed(it.expect_date);
  const upcomingBoard=(b==='upcoming_auto');
  if(upcomingBoard){
    const gone=DATA.items.filter(upExpired).length;
    const late=DATA.items.filter(upLate).length;
    const pills=document.getElementById('pills');
    if(pills && !pills.querySelector('.up-gone') && (gone||late)){
      const pill=document.createElement('span');
      pill.className='pill up-gone';
      pill.textContent=[gone?('已过期剔除 '+gone):'',late?('已过预计上架日·仍未上线 '+late):'']
        .filter(Boolean).join(' · ');
      pill.title='奖池成员看期次状态；武器皮肤看源表 release_state —— 预计日过了但还没上线，不算过期';
      pills.appendChild(pill);
    }
  }
  const items=DATA.items.filter(it=>{
    if(upcomingBoard && upExpired(it))return false;
    if(fe&&it.evidence!==fe)return false;
    if(FASHION_BOARD&&!frPass(it))return false;
    if(VEHICLE_BOARD&&!vPass(it))return false;
    if(CHIP_BOARD&&!cPass(it))return false;
    if(partFilter.length&&!partFilter.includes(String(it.part??"")))return false;
    if(Array.isArray(DATA._custFilters)){
      for(const cf of DATA._custFilters){
        const v=cf.sel?cf.sel.value:"";
        if(v&&String(it[cf.key]??"")!==v)return false;
      }
    }
    if(fg.size){
      const lv=pick(it,"level"),gRaw=pick(it,"grade");
      const tKey=(gRaw!=null&&gRaw!=="")?String(gRaw):String(lv==null?"":lv);
      if(!fg.has(tKey))return false;   // 多选：命中任意一个勾选项即保留
    }
    if(ft){
      const wt=pick(it,"weapon_type_label");
      if(!wt||typeCN(wt)!==ft)return false;
    }
    if(fi){
      const ip=pick(it,"ip_now")||pick(it,"ip_liaison")||"";
      if((ip||"（无联动）")!==fi)return false;
    }
    if(frel&&String(listingOf(it)??"")!==frel)return false;
    if(fns){const ns=nameStatusOf(it);if(ns!==fns)return false;}
    if(q){const hay=JSON.stringify(it).toLowerCase();if(!hay.includes(q))return false;}
    return true;
  });
  // 预告专栏：给「预计日已过但源表仍算未上线」的条目打标（卡面显示「已过预计」）
  if(upcomingBoard){ items.forEach(it=>{ it._late=upLate(it); }); }
  if(SCENE_TABLE){ sbRender(items); return; }
  const g=document.getElementById("grid");g.innerHTML="";
  const hasSfxChildren=items.some(it=>Array.isArray(it.sfx_items));
  const childCount=items.reduce((sum,it)=>sum+(Array.isArray(it.sfx_items)?it.sfx_items.length:0),0);
  const currentParents=items.filter(it=>it.catalog_layer==="current_parent").length;
  const behaviorPreviews=items.filter(it=>it.catalog_layer==="behavior_preview_only").length;
  const variantCount=items.reduce((sum,it)=>sum+(Array.isArray(it.variant_items)?it.variant_items.length:0),0);
  const sfxInView=items.reduce((sum,it)=>sum+(Array.isArray(it.sfx_items)?it.sfx_items.length:0),0);
  // 名称三级统计（可见范围内；变体按附属记录计入）
  const nameStats=(m=>{
    const acc={verified:0,candidate:0,unresolved:0};
    for(const it of items){
      const st=it.name_status||(it.candidate_name?"candidate":(it.name?"verified":"unresolved"));
      if(acc[st]!==undefined)acc[st]++;
      for(const v of (it.variant_items||[])){
        const vs=v.name_status||(v.name?"verified":"candidate");
        if(acc[vs]!==undefined)acc[vs]++;
      }
    }
    return acc;
  })();
  const timedVariantsShown=items.reduce((sum,it)=>sum+((Array.isArray(it.timed_variants)?it.timed_variants.length:0)),0);
  const countEl=document.getElementById("count");
  const countHtml=FASHION_BOARD
    ? `显示 ${items.length} / ${DATA.items.length} 件 · 多图(>4) ${items.filter(it=>((it._media&&it._media.images)||[]).length>4).length} 件 · 仅占位 ${items.filter(it=>it.icon_state==="含占位").length} 件`
    : (VEHICLE_BOARD
      ? `显示 ${items.length} / ${DATA.items.length} 辆 · 专属图 ${items.filter(it=>it.icon_state==="专属图").length} 辆 · 仅类型图 ${items.filter(it=>it.icon_state==="仅类型图").length} 辆 · 图 ${items.reduce((s,it)=>s+(it.icon_count||0),0)} 张（gpk_loc0 逐图核验）`
      : (CHIP_BOARD
        ? `显示 ${items.length} / ${DATA.items.length} 枚芯片 · 有图 ${items.filter(it=>it.icon_count>0).length} 枚（仅小图 ${items.filter(it=>it.only_small).length}）· 图 ${items.reduce((s,it)=>s+(it.icon_count||0),0)} 张（gpk_loc0 逐图核验）· 在奖池 ${items.filter(it=>it.in_pool).length} 枚`
        : null));
  countEl.innerHTML=countHtml!=null?countHtml:candidateSkinBoard
    ? `显示 ${items.length} / ${DATA.items.length} 条静态候选（顶层仅永久记录；${timedVariantsShown} 个时限变体并入主卡、不计款） · 名称 ${nameStats.verified} 已核验 / ${nameStats.candidate} 待确认 / ${nameStats.unresolved} 未命名 · ${sfxInView} 个表现子项`
    : (skinBoard||hasSfxChildren)
    ? `显示 ${items.length} / ${DATA.items.length} 款皮肤 · ${currentParents} 主皮肤 · 时限变体 ${variantCount}（并入主卡，不单独计款） · ${behaviorPreviews} 行为预告 · 名称 ${nameStats.verified} 已核验 / ${nameStats.candidate} 待确认 / ${nameStats.unresolved} 未命名 · 上架状态 ${listingStatHTML(items)}`
    : `显示 ${items.length} / ${DATA.items.length} 条`;
  if(FASHION_BOARD)frPills(items);
  if(VEHICLE_BOARD)vPills(items);
  if(CHIP_BOARD)cPills(items);
  if(!items.length){g.innerHTML='<div class="empty">无匹配条目</div>';return;}
  if(CHIP_BOARD){
    // 芯片板：卡面 = 图轨/名字/品质色档/类型/编号/首档效果；点卡打开 D2 详情灯箱（12 档数值在灯箱内看）
    const list=cSortList(items);
    C2.chips=list;
    g.innerHTML=list.map((it,i)=>cCard(it,i)).join("");
    if(C2.open)c2Resync();
    return;
  }
  if(VEHICLE_BOARD){
    // 载具板：卡面只留 图轨/名字/分类/编号；其余在卡内折叠区；默认编号 ↓
    // 2026-10-29：接 D2 子卡（ROSTER_D2 复用 vCard 全卡缓存，嵌入时展开折叠区）
    const vlist=vSortList(items);
    C2.prov=ROSTER_D2;C2.chips=vlist;C2.html={};
    g.innerHTML=vlist.map((it,i)=>{const h=vCard(it,i);C2.html[c2IdOf(it)]=h;return h;}).join("");
    if(C2.open)c2Resync();
    return;
  }
  if(FASHION_BOARD){
    // 时装板：卡面只留 图轨/名字/部位/品级/魅力值/model_id；详情/技术详情只在 D2 灯箱里（frCard full 版缓存到 C2.htmlFull）
    // 顺序 = 先按筛选结果，再按排序控件（默认保留板上原序 = 归一名字序）
    const frList=frSortList(items);
    C2.prov=FR_D2;C2.chips=frList;C2.html={};C2.htmlFull={};
    g.innerHTML=frList.map((it,i)=>{
      const h=frCard(it,i);C2.html[c2IdOf(it)]=h;C2.htmlFull[c2IdOf(it)]=frCard(it,i,true);return h;
    }).join("");
    if(C2.open)c2Resync();
    return;
  }
  if(skinBoard){
    // 排序（默认 = 上架时间 ↓：新在前，预告排最前；同日按皮肤 ID ↓）
    const st=sortState();
    const NO_SALE=Number.MAX_SAFE_INTEGER;
    const sign=st.dir==="asc"?1:-1;
    const byId=(a,b)=>sign*((keyOf(a)||0)-(keyOf(b)||0));
    const bySale=(a,b)=>{
      const x=saleOf(a)||NO_SALE,y=saleOf(b)||NO_SALE;
      return sign*(x-y)||byId(a,b);
    };
    items.sort(st.key==="sale"?bySale:byId);
    C2.prov=SKIN_D2;C2.chips=items;C2.html={};
    g.innerHTML=items.map((it,i)=>{const h=renderSkinCard(it,i);C2.html[c2IdOf(it)]=h;return h;}).join("");
    if(C2.open)c2Resync();
    return;
  }
  if(candidateSkinBoard){
    const st=sortState();
    const sign=st.dir==="asc"?1:-1,NO_SALE=Number.MAX_SAFE_INTEGER;
    const byId=(a,b)=>sign*((a.structural_record_key||0)-(b.structural_record_key||0));
    const bySale=(a,b)=>sign*((pick(a,"sale_ts")||NO_SALE)-(pick(b,"sale_ts")||NO_SALE))||byId(a,b);
    items.sort(st.key==="sale"?bySale:byId);
    C2.prov=CAND_D2;C2.chips=items;C2.html={};
    g.innerHTML=items.map((it,i)=>{const h=renderCandidateSkinCard(it,i);C2.html[c2IdOf(it)]=h;return h;}).join("");
    if(C2.open)c2Resync();
    return;
  }
  if(String(DATA.meta&&DATA.meta.card_mode)==="group"){
    g.classList.remove("period-grid");
    g.innerHTML=renderGroupMode(items);
    return;
  }
  if(String(DATA.meta&&DATA.meta.card_mode)==="period"){
    g.classList.add("period-grid");
    g.innerHTML=renderPeriodMode(items);
    return;
  }
  g.classList.remove("period-grid");
  const orderBy=document.getElementById("fOrder").value;
  const timeOrder=items.some(it=>it.period_date)&&(orderBy==="new"||orderBy==="old")&&!items.some(it=>it.sort_660);
  const nucleusOrder=!timeOrder&&items.some(it=>it.sort_660)&&orderBy!=="";
  const charmOrder=(orderBy==='charm') && items.some(it=>it.charm_value!=null);
  const list=charmOrder
    ? [...items].sort((a,b)=>{
        const x=a.charm_value, y=b.charm_value;
        if(x==null&&y==null) return 0;
        if(x==null) return 1;
        if(y==null) return -1;
        const dir=(document.getElementById('fDir')||{}).dataset?.dir||'desc';
        return dir==='asc' ? x-y : y-x;
      })
    : timeOrder
    ? [...items].sort((a,b)=>orderBy==="old"
        ? String(a.period_date).localeCompare(String(b.period_date))
        : String(b.period_date).localeCompare(String(a.period_date)))
    : nucleusOrder
    ? [...items].sort((a,b)=>orderBy==="old"
        ? (a.sort_660||0)-(b.sort_660||0)
        : (b.sort_660||0)-(a.sort_660||0))
    : items;
  /* 2026-10-30：核芯板全量入 chips——基础（绿）核芯（家园守卫限定 4 条）无 skill_desc/升星段，
     之前按 rank_star_segments 过滤会把它们漏出 D2，且走普通 kv 卡分支格式乱 */
  const coreList=CORE_BOARD?list.slice():null;
  if(CORE_BOARD){C2.prov=CORE_D2;C2.chips=coreList;C2.html={};}
  /* 2026-10-29：名册类板（击败播报/头像头像框名片框等 card_mode=roster）接 D2 子卡。
     注意：mutation_core_full 的 meta 也带 card_mode:"roster"（核芯板初建时基于名册体系），
     核芯板必须保持 CORE_D2，否则 provider 被覆盖回旧版网格卡直嵌（2026-10-30 修复） */
  const rosterBoard=!CORE_BOARD&&String(DATA.meta&&DATA.meta.card_mode)==="roster";
  if(rosterBoard){C2.prov=ROSTER_D2;C2.chips=list;C2.html={};}
  g.innerHTML=list.map((it,i)=>{
    /* 核芯板所有条目都按核芯卡渲染（基础核芯无特技/升星段，卡面只剩品级+星上限+描述） */
    const nucleusMode=!!it.rank_star_segments||CORE_BOARD;
    const rosterMode=!nucleusMode&&rosterBoard;
    const sumKeys=nucleusMode?new Set(["item_id","grade_clean","grade_name","grade_color","grade_label",
      "max_star","star_text","skill_icon","skill_desc","weapon_type_display","weapon_type_label",
      "weapon_type_code","rank_star_segments","desc","element"]):new Set();
    const allPairs=Object.entries(it).filter(([k])=>!FIXED.has(k)&&!sumKeys.has(k)&&it[k]!==null&&it[k]!=="");
    const techPairs=allPairs.filter(([k])=>TECH_KEYS.has(k));
    const extra=allPairs.filter(([k])=>!TECH_KEYS.has(k));
    const techSection=renderTechSection([...techPairs,["source",it.source]]);
    const lotteryMode=!nucleusMode&&String(DATA.meta&&DATA.meta.category||"").startsWith("四、奖池");
    const rowHtml=([k,v])=>{
      const cn=FIELD_CN[k]||k;const mono=(k==="model_path"||k==="cc"||k==="file")?"mono":"";
      if(nucleusMode&&k==="rank_star_segments"&&v&&typeof v==="object"&&!Array.isArray(v)){
        const segs=Object.keys(v).sort((a,b)=>Number(a)-Number(b))
          .map(s=>`<div class="star"><b>${esc(s)}星</b><div class="star-txt">${richText(zhText(String(v[s])))}</div></div>`).join("");
        return `<div class="k">星级段</div><div class="v stars">${segs}</div>`;
      }
      if(k==="skill_desc")return `<div class="k">${cn}</div><div class="v nucleus-desc">${richText(String(v))}</div>`;
      if(k==="skill_icon"&&nucleusMode)return "";
      if(isRichText(v))return `<div class="k">${cn}</div><div class="v rich">${richText(zhText(String(v)))}</div>`;
      let val=fmtVal(k,v);
      if(k==="shape_hint"&&v)return `<div class="k">${cn}</div><div class="v"><span class="hint">${esc(v)}</span></div>`;
      if(k==="ip"&&v)return `<div class="k">${cn}</div><div class="v"><span class="tag-ip">${esc(v)}</span></div>`;
      return `<div class="k">${cn}</div><div class="v ${mono}">${esc(val)}</div>`;
    };
    const rows=extra.map(rowHtml).join("");
    const childSection=renderSfxChildren(it.sfx_items);
    const rewardsSection=Array.isArray(it.rewards)&&it.rewards.length?renderRewardsList(it.rewards):"";
    const poolsSection=renderPools(it.pools);
    const activityPoolRefsSection=renderActivityPoolRefs(it.activity_pool_refs);
    const referenceSection=renderReferenceFields(it.reference_fields);
    const behaviorSection=renderBehaviorResources(it.behavior_resources);
    const variantSection=renderVariantItems(it.variant_items,it);
    // 抽奖类卡（分类前缀「四、奖池」）：默认只显示概要 kv，点名称展开 rewards/pools/refs 等详情
    let bodyHtml;
    if(lotteryMode){
      const SUMMARY_SET=new Set(["activity","server_branch","branch_source","panel_rows",
        "store_zhencang","store_xishi","store_zhencang_source","store_xishi_source"]);
      const sum=[],det=[];
      for(const [k,v] of extra){ (SUMMARY_SET.has(k)?sum:det).push(rowHtml([k,v])); }
      const emptyRow='<div class="k">概要</div><div class="v">（无）</div>';
      bodyHtml=`<div class="kv">${sum.length?sum.join(""):emptyRow}</div>`+
        `<div class="i-detail" hidden><div class="kv">${det.length?det.join(""):emptyRow}</div>`+
        `${referenceSection}${rewardsSection}${poolsSection}${activityPoolRefsSection}${variantSection}${behaviorSection}${childSection}`+
        `${techSection}</div>`;
    }else if(nucleusMode){
      /* 简略卡面：只留 品级 / 星上限 / 武器类型；特技、升星段、溯源全部折进点开的详情 */
      const sum=[];
      if(it.grade_clean||it.grade_label){
        const gl=it.grade_label||it.grade_clean;
        const gc=it.grade_color?` g-${esc(it.grade_color)}`:"";
        sum.push(`<div class="k">品级</div><div class="v"><span class="grade-pill${gc}">${esc(gl)}</span></div>`);
      }
      sum.push(`<div class="k">星上限</div><div class="v">${it.max_star==null?"待定":esc(it.max_star)}</div>`);
      if(it.weapon_type_display)sum.push(`<div class="k">武器类型</div><div class="v">${esc(it.weapon_type_display)}</div>`);
      if(it.element)sum.push(`<div class="k">核芯属性</div><div class="v">${esc(it.element)}</div>`);
      const det=[];
      if(it.skill_desc)det.push(`<div class="k">核芯特技</div><div class="v nucleus-desc">${richText(it.skill_desc)}</div>`);
      if(it.rank_star_segments&&typeof it.rank_star_segments==="object"){const segs=Object.keys(it.rank_star_segments).sort((a,b)=>Number(a)-Number(b)).map(s=>`<div class="star"><b>${esc(s)}星</b><div class="star-txt">${richText(zhText(String(it.rank_star_segments[s])))}</div></div>`).join("");det.push(`<div class="k">升星解锁</div><div class="v stars">${segs}</div>`);}
      if(it.desc)det.push(`<div class="k">描述</div><div class="v nucleus-desc">${richText(zhText(String(it.desc)))}</div>`);
      const techBlock=(rows||techSection||referenceSection)?
        `<details class="tech sub"><summary>技术详情 · 数据来源 / 字段槽位</summary>`+
        `${rows?`<div class="kv">${rows}</div>`:""}${referenceSection}${techSection}`+
        /* 2026-10-29（用户口径）：结构已解析/静态配置等审计标签不上卡面，折到这里 */
        `<div class="kv"><div class="k">证据等级</div><div class="v">${esc(EV_CN[it.evidence]||it.evidence||"")}</div>`+
        `<div class="k">状态标签</div><div class="v">${esc((Array.isArray(it.status_tags)?it.status_tags:[]).map(t=>STATE_CN[t]||COMMON_VAL_CN[t]||t).join("、"))}</div></div></details>`:"";
      const extraBlock=`${rewardsSection}${poolsSection}${activityPoolRefsSection}${variantSection}${behaviorSection}${childSection}`;
      bodyHtml=`<div class="kv">${sum.join("")}<div class="i-detail" hidden><div class="kv">${det.join("")}</div>`+
        `${extraBlock}${techBlock}</div></div>`;
    }else if(rosterMode){
      /* 名册类板（meta.card_mode="roster"）：卡面只留 图轨(≤4 张) + 名字 + 编号(head) +
         meta.card_summary 声明的字段；其余字段、礼包逐条说明、溯源全部折进点开的详情区 */
      const sum=[];
      (Array.isArray(DATA.meta.card_summary)?DATA.meta.card_summary:[]).forEach(p=>{
        const k=p[0],label=p[1],v=it[k];if(v==null||v==="")return;
        sum.push(`<div class="k">${esc(label)}</div><div class="v${String(k).indexOf("desc")>=0?" nucleus-desc":""}">${richText(String(v))}</div>`);
      });
      if(Array.isArray(it.gift_ids)&&it.gift_ids.length)sum.push(`<div class="k">礼包</div><div class="v mono">${esc(it.gift_ids.join("、"))}</div>`);
      const gRows=(Array.isArray(it.gift_items)?it.gift_items:[]).map(g=>
        `<div class="k">礼包 ${esc(g.gift_id)}</div><div class="v">${richText(String(g.desc||""))}</div>`).join("");
      /* 字段中文名：板自带 meta.field_labels 优先，其次全局 FIELD_CN；都不命中才显示原始 key */
      const labels=DATA.meta.field_labels||{};
      const labelOf=k=>labels[k]||FIELD_CN[k]||k;
      /* meta.hide_fields：板上无意义的字段（如头像板 server 全板无跨服差异）整列不显示 */
      const hideSet=new Set(Array.isArray(DATA.meta.hide_fields)?DATA.meta.hide_fields:[]);
      const rRows=extra.filter(p=>!hideSet.has(p[0])&&p[0]!=="gift_items"&&!(Array.isArray(p[1])&&!p[1].length)).map(([k,v])=>
        `<div class="k">${esc(labelOf(k))}</div><div class="v${(k==="skill_desc"||k==="rank_segments")?" nucleus-desc":""}">${esc(fmtVal(k,v))}</div>`).join("");
      bodyHtml=`<div class="kv">${sum.join("")}</div>`+
        `<div class="i-detail" hidden><div class="kv">${rRows}${gRows}</div>${renderMvpVideos(it)}</div>`;
    }else{
      bodyHtml=`<div class="kv">${rows}</div>${referenceSection}${rewardsSection}${poolsSection}${activityPoolRefsSection}${variantSection}${behaviorSection}${childSection}${techSection}`;
    }
    /* 2026-10-29（用户口径）：MVP 结算动画卡面只保留立绘，视频封面图不再上卡；
       封面转作 D2 内视频播放器的 poster（renderMvpVideos） */
    const cardMedia=(b==="kill_broadcast"&&it._media)
      ?{...it._media,images:(it._media.images||[]).filter(x=>!/^(.*)_cover$/.test(x.base||""))}
      :it._media;
    const hasMedia = !!(cardMedia && (((cardMedia.images||[]).length) || cardMedia.placeholder));
    const NO_MEDIA=!!(DATA.meta&&DATA.meta.hide_media);
    const mediaBlock = rosterMode ? (hasMedia ? renderItemMedia(cardMedia) : (NO_MEDIA?"":`<div class="i-media empty"><span>无图</span></div>`)) : renderItemMedia(cardMedia);
    /* 2026-10-30：头像板按类型打类名 —— 名片框/头像框是中空边框图，卡面垫一层底板才看得出是"框" */
    const kindCls=AVATAR_KIND_CLS[it.kind]||"";
    const html=`<div class="i${nucleusMode?" nucleus":""}${lotteryMode?" lottery":""}${rosterMode?" roster":""}${kindCls?" "+kindCls:""}"${nucleusMode?` data-cidx="${coreList.indexOf(it)}"`:(rosterMode?` data-cidx="${i}"`:"")}>
      ${mediaBlock}
      <div class="i-head${nucleusMode||lotteryMode?" toggle":""}"${nucleusMode||lotteryMode?` role="button" tabindex="0" aria-expanded="false" onkeydown="onDetailKey(event,this)" onclick="toggleDetail(this)"`:""}>
        <div><div class="i-name">${esc(it.name||it.display_name||it.id)}${it.ip?`<span class="tag-ip">${esc(it.ip)}</span>`:""}</div>
        ${referenceTitle(it.reference_fields)}
        <div class="i-id" title="id">${nucleusMode||rosterMode?`${esc(DATA.meta.id_label||"道具ID")} ${esc(it.item_id??it.id)}`:`${esc(it.id)}`}</div></div>
        <span class="head-tags">${nucleusMode?"":`<span class="ev ${it.evidence}">${EV_CN[it.evidence]||it.evidence}</span>${it.image_status?`<span class="ev gap" title="${esc(it.image_note||"该资源在当前包快照中不可得")}">${esc(it.image_status)}</span>`:""}${renderStateTags(it.status_tags)}`}</span>
      </div>
      ${bodyHtml}
    </div>`;
    if(CORE_BOARD&&nucleusMode)C2.html[c2IdOf(it)]=html;
    if(rosterMode)C2.html[c2IdOf(it)]=html;
    return html;
  }).join("");
  if((CORE_BOARD||rosterBoard)&&C2.open)c2Resync();
}

/* 2026-10-29：MVP 结算动画 D2 详情内嵌视频播放（视频本体尚未提取 → onerror 兜底提示游戏内路径） */
function mvpVideoErr(el){
  const w=el.closest(".mvp-video");
  if(w)w.classList.add("missing");
}
function renderMvpVideos(it){
  if(b!=="kill_broadcast")return "";
  const vids=Array.isArray(it.videos)?it.videos:[];
  if(!vids.length)return "";
  const localCovers=((it._media&&it._media.images)||[]).filter(x=>/^(.*)_cover$/.test(x.base||""));
  const rows=vids.map((v,i)=>{
    const base=String(v).split("/").pop()||("video"+i);
    const cn=/_nan/i.test(base)?"男角色":(/_nv/i.test(base)?"女角色":("视频 "+(i+1)));
    const src="assets/kill_broadcast/video/"+base;
    const cover=localCovers[i]||localCovers[0];
    return `<div class="mvp-video"><div class="mvp-video-label">${esc(cn)}</div>`+
      `<video controls preload="metadata" src="${esc(src)}"${cover?` poster="${esc(cover.png)}"`:""} onerror="mvpVideoErr(this)"></video>`+
      `<div class="mvp-video-miss">视频文件未提取 · 游戏内路径 <code>${esc(v)}</code></div></div>`;
  }).join("");
  return `<div class="mvp-videos"><h4>动画视频</h4>${rows}</div>`;
}

/* ════════════════ 期次容器卡（card_mode="period"）════════════════
   一张卡 = 一个期次；卡内按奖池分组列成员，成员只给「图标 + 名字 + 槽位」，成员不单独成卡。*/
window.PF=window.PF||{status:"all",family:"all",kind:"all",limit:40,only:"1",closed:{}};
function pSet(k,v){window.PF[k]=v; if(k!=="limit")window.PF.limit=40; render();}
function pToggleFam(f){PF.closed=PF.closed||{};PF.closed[f]=!PF.closed[f];render();}
function pToggleCard(head){
  const card=head.closest(".pcard");
  const body=card.querySelector(".pcard-body");
  if(!body)return;
  const open=body.hidden;
  body.hidden=!open;
  card.classList.toggle("open",open);
}
function pMore(){window.PF.limit=(window.PF.limit||24)+24; render();}
function periodStatus(p){
  const t=new Date(); const s=p.start?new Date(p.start+"T00:00:00"):null;
  const e=p.end?new Date(p.end+"T23:59:59"):null;
  if(s&&t<s)return {k:"upcoming",txt:"即将开始"};
  if(e&&t>e)return {k:"ended",txt:"已结束"};
  return {k:"on",txt:"当期"};
}
function renderPeriodMode(list){
  if(DATA.meta._pfInit!==1){
    const qps=getParam("ps"),qpf=getParam("pf"),qpk=getParam("pk");
    if(qps)PF.status=qps; if(qpf)PF.family=qpf; if(qpk)PF.kind=qpk;
    DATA.meta._pfInit=1;
  }
  const periods=(DATA.periods||[]).slice();
  const byPeriod={};
  list.forEach(it=>{(byPeriod[it.period_id]=byPeriod[it.period_id]||[]).push(it);});
  const cleanLabel=s=>String(s||"").replace(/（活动名未在活动表内）/g,"").trim();
  const rank=p=>{const k=periodStatus(p).k;return k==="on"?0:(k==="upcoming"?1:2);};
  const famOrder=[...new Set(periods.map(p=>p.family).filter(Boolean))];
  periods.sort((a,b)=>{
    const fa=famOrder.indexOf(a.family), fb=famOrder.indexOf(b.family);
    if(fa!==fb)return fa-fb;
    const ra=rank(a),rb=rank(b);
    if(ra!==rb)return ra-rb;
    if(ra===1)return String(a.start||"").localeCompare(String(b.start||""));
    return String(b.start||"").localeCompare(String(a.start||""));
  });

  const fams=[...new Set(periods.map(p=>p.family).filter(Boolean))];
  const kinds=[...new Set(list.map(i=>i.kind).filter(Boolean))];
  const stCount={on:0,upcoming:0,ended:0};
  periods.forEach(p=>{if((byPeriod[p.period_id]||[]).length)stCount[periodStatus(p).k]++;});
  const chip=(label,n,active,fn)=>`<button class="pf-chip${active?" on":""}" onclick="${fn}">${label}${n!=null?` <b>${n}</b>`:""}</button>`;
  const bar=`<div class="pf-bar">
    <span class="pf-label">展示</span>
    ${chip("只看有内容",null,PF.only==="1","pSet('only','1')")}
    ${chip("全部期次",null,PF.only==="0","pSet('only','0')")}
    <span class="pf-sep"></span>
    <span class="pf-label">状态</span>
    ${chip("全部",null,PF.status==="all","pSet('status','all')")}
    ${chip("当期",stCount.on,PF.status==="on","pSet('status','on')")}
    ${chip("即将开始",stCount.upcoming,PF.status==="upcoming","pSet('status','upcoming')")}
    ${chip("已结束",stCount.ended,PF.status==="ended","pSet('status','ended')")}
  </div>
  <div class="pf-bar">
    <span class="pf-label">家族</span>
    ${chip("全部",null,PF.family==="all","pSet('family','all')")}
    ${fams.map(f=>chip(esc(f),periods.filter(p=>p.family===f).length,PF.family===f,`pSet('family','${esc(f).replace(/'/g,"\'")}')`)).join("")}
  </div>
  <div class="pf-bar">
    <span class="pf-label">奖励类型</span>
    ${chip("全部",null,PF.kind==="all","pSet('kind','all')")}
    ${kinds.map(k=>chip(esc(k),list.filter(i=>i.kind===k).length,PF.kind===k,`pSet('kind','${esc(k).replace(/'/g,"\'")}')`)).join("")}
  </div>`;

  let shown=0, total=0, lastFam=null;
  const cards=[];
  for(const p of periods){
    let mem=byPeriod[p.period_id]||[];
    if(!mem.length)continue;
    const st=periodStatus(p);
    if(PF.status!=="all"&&st.k!==PF.status)continue;
    if(PF.family!=="all"&&p.family!==PF.family)continue;
    if(PF.kind!=="all"){mem=mem.filter(x=>x.kind===PF.kind); if(!mem.length)continue;}
    if(PF.only==="1" && !mem.length)continue;
    total++;
    if(shown>=(PF.limit||24))continue;
    shown++;
    const pools=new Map();
    mem.forEach(it=>{
      const k=it.pool_uid||it.pool_id||it.pool_label||"—";
      if(!pools.has(k))pools.set(k,{label:it.pool_label||k,items:[]});
      pools.get(k).items.push(it);
    });
    const poolHtml=[...pools.values()].map(pl=>{
      pl.items.sort((a,b)=>(a.slot??999)-(b.slot??999));
      const chips=pl.items.map(it=>{
        const md=it._media||{}, im=(md.images||[])[0];
        const hasImg=!!(im&&im.png);
        return `<div class="pchip${hasImg?"":" noimg"}" title="${esc(it.name||"")}${it.alias?`（内部名：${esc(it.alias)}）`:""}">
          ${hasImg?`<div class="pchip-img"><img src="${esc(im.png)}" alt="" loading="lazy"></div>`:""}
          <div class="pchip-name">${esc(it.name||it.id)}${it._late?'<span class="pchip-cand">已过预计</span>':''}${it.evidence==="candidate"?'<span class="pchip-cand">候选</span>':""}</div>
          <div class="pchip-meta">${esc(it.kind||"")}${it.slot!=null?` · 槽位 ${esc(String(it.slot))}`:""}</div>
        </div>`;
      }).join("");
      return `<div class="ppool">
        <div class="ppool-head"><span class="ppool-name">${esc(pl.label)}</span><span class="ppool-n">${pl.items.length} 件</span></div>
        <div class="ppool-items">${chips}</div>
      </div>`;
    }).join("");
    const labelClean=cleanLabel(p.label)||cleanLabel(p.activity_name)||p.period_id;
    const imgs=mem.map(x=>{const a=((x._media||{}).images)||[];return a.length&&a[0]&&a[0].png?a[0].png:null;}).filter(Boolean);
    const withImg=imgs.length;
    const cover=imgs.slice(0,4).map(s=>`<img src="${esc(s)}" alt="" loading="lazy">`).join("");
    const famName=p.family||"—";
    if(PF.family==="all" && lastFam!==famName){
      lastFam=famName;
      const famTotal=periods.filter(x=>x.family===famName&&(byPeriod[x.period_id]||[]).length).length;
      const closed=(PF.closed||{})[famName];
      cards.push(`<div class="pfam-head${closed?" closed":""}" onclick="pToggleFam('${esc(famName).replace(/'/g,"\'")}')">
        <span class="pfam-name">${esc(famName)}</span><span class="pfam-n">${famTotal} 期</span>
        <span class="pfam-arrow">${closed?"▸":"▾"}</span></div>`);
      if(closed){continue;}
    }
    if(PF.family==="all" && (PF.closed||{})[famName]) continue;
    cards.push(`<div class="pcard ${st.k}">
      <div class="pcard-head" onclick="pToggleCard(this)" role="button" tabindex="0">
        <div class="pcard-title">
          <span class="pcard-name">${esc(labelClean)}</span>
          <span class="pstate ${st.k}">${st.txt}</span>
          <span class="pfam">${esc(p.family||"")}</span>
        </div>
        ${cover?`<div class="pcard-cover">${cover}</div>`:""}
        <div class="pcard-date">${esc(p.start||"")}${p.end?" → "+esc(p.end):""} · ${p.pool_count||1} 池 · 共 ${mem.length} 件 · 有图 ${withImg}${p.pool_size?` · 池内 ${p.pool_size} 件（服务端下发）`:""}</div>
      </div>
      <div class="pcard-body" hidden>${poolHtml}</div>
    </div>`);
  }
  const more=(shown<total)?`<div style="text-align:center;margin:6px 0 24px"><button class="pf-chip on" onclick="pMore()">加载更多（已显示 ${shown}/${total}）</button></div>`:"";
  return bar+(cards.length?cards.join("")+more:'<div class="empty">当前筛选下没有期次</div>');
}


/* ════════════════ 类型容器卡（card_mode="group"）════════════════
   一张卡 = 一个类型；卡内成员只给「图标 + 名字 + 品级 + 评分基数」，成员不单独成卡。*/
window.PG=window.PG||{grade:"all",limit:60};
function pgSet(k,v){window.PG[k]=v;render();}
function renderGroupMode(list){
  const field=(DATA.meta&&DATA.meta.group_field)||"kind";
  const label=(DATA.meta&&DATA.meta.group_label)||"类型";
  const groups=new Map();
  list.forEach(it=>{
    const k=it[field]||"—";
    if(!groups.has(k))groups.set(k,[]);
    groups.get(k).push(it);
  });
  const grades=[...new Set(list.map(i=>i.grade).filter(Boolean))];
  const chip=(label_,n,active,fn2)=>`<button class="pf-chip${active?" on":""}" onclick="${fn2}">${label_}${n!=null?` <b>${n}</b>`:""}</button>`;
  const bar=`<div class="pf-bar">
    <span class="pf-label">品级</span>
    ${chip("全部",null,PG.grade==="all","pgSet('grade','all')")}
    ${grades.map(g=>chip(esc(g),list.filter(i=>i.grade===g).length,PG.grade===g,`pgSet('grade','${esc(g).replace(/'/g,"\'")}')`)).join("")}
  </div>`;
  const cards=[];
  const names=[...groups.keys()].sort((a,b)=>groups.get(b).length-groups.get(a).length);
  for(const k of names){
    let mem=groups.get(k)||[];
    if(PG.grade!=="all")mem=mem.filter(i=>i.grade===PG.grade);
    if(!mem.length)continue;
    mem.sort((a,b)=>(b.power||0)-(a.power||0)||String(a.name).localeCompare(String(b.name)));
    const chips=mem.map(it=>{
      const md=it._media||{}, im=(md.images||[])[0];
      const img=im&&im.png?`<img src="${esc(im.png)}" alt="" loading="lazy">`:`<span class="pp-noimg">无图</span>`;
      return `<div class="pchip" title="${esc(it.name||"")}">
        <div class="pchip-img">${img}</div>
        <div class="pchip-name">${esc(it.name||it.id)}</div>
        <div class="pchip-meta">${esc(it.grade||"")}${it.power!=null?` · ${esc(String(it.power))}`:""}</div>
      </div>`;
    }).join("");
    cards.push(`<div class="pcard">
      <div class="pcard-head">
        <div class="pcard-title"><span class="pcard-name">${esc(k)}</span><span class="pfam">${mem.length} 台</span></div>
        <div class="pcard-date">按评分基数排序</div>
      </div>
      <div class="pcard-body"><div class="ppool-items">${chips}</div></div>
    </div>`);
  }
  return bar+(cards.length?cards.join(""):'<div class="empty">当前筛选下没有成员</div>');
}

function onDetailKey(event,head){
  if(event.key==="Enter"||event.key===" "){event.preventDefault();toggleDetail(head);}
}
function toggleDetail(head){
  const card=head.parentElement;
  const target=card.querySelector(".i-detail")||card.querySelector(".i-more");
  if(!target)return;
  target.hidden=!target.hidden;
  head.classList.toggle("open",!target.hidden);
  head.setAttribute("aria-expanded",String(!target.hidden));
}
const b=getParam("b");
try{document.body.classList.add("b-"+b);}catch(e){}
const POLICY=window.WIKI_PUBLICATION_POLICY;
const policyEntry=POLICY&&POLICY.boards?POLICY.boards[b]:null;
function showQuarantine(reason){
  document.title="板块已隔离 · Wiki";
  document.getElementById("title").textContent="该板块已隔离，暂不展示旧数据";
  document.getElementById("metaline").textContent="公开展示要求：源锁 → 条目/表 → 行级字段 → 名称来源 → 业务语义 → 证据等级。";
  document.querySelector(".controls").style.display="none";
  const n=document.getElementById("notes");
  n.style.display="block";
  n.textContent="隔离原因："+(reason||"该 board 未登记为可公开板块。")+" 原始 JSON 已保留，待逐行复证后才会重新发布。";
  document.getElementById("grid").innerHTML='<div class="empty">没有可公开展示的数据</div>';
}
if(!b){document.getElementById("title").textContent="缺少板块参数 ?b=";}
else if(!wbProjectionIds().has(b) && (!policyEntry || !["published","published_hidden"].includes(policyEntry.publication_status))){
  showQuarantine(policyEntry&&policyEntry.reason);
}
else loadBoard(b,d=>{
  DATA=d;document.getElementById("q").value=initialQuery;const m=d.meta;
  /* 2026-10-30：skin-mode 改为**数据驱动**（与 render() 里的 skinBoard 判定同源）——
     原先硬编码三个板 id，skin_behavior_preview 等皮肤板漏加 → 卡面样式与点图开 D2 都失效。 */
  if(b==="weapon_skin_sfx_text_sources"||b==="weapon_skin_static_candidates_v01"||b==="weapon_skin_active"
    ||(Array.isArray(DATA&&DATA.items)&&DATA.items.some(it=>it.listing_status!==undefined||it.skin_item_id!==undefined
      ||(Array.isArray(it.variant_items)&&(it.grade!==undefined||it.weapon_type_label!==undefined)))))
    document.body.classList.add("skin-mode");
  if(b==="mutation_core_full")document.body.classList.add("core-mode");
  if(VEHICLE_BOARD){
    document.body.classList.add("vehicle-mode");
    const vq=document.getElementById("q");
    if(vq)vq.placeholder="搜索：载具名 / 编号 / 品牌 / 类型 / 描述…";
  }
  if(FASHION_BOARD){
    document.body.classList.add("fashion-mode");
    const qi=document.getElementById("q");
    if(qi)qi.placeholder="搜索：时装名 / model_id / 描述 / 行键…";
  }
  if(CHIP_BOARD){
    document.body.classList.add("chip-mode");
    const cq=document.getElementById("q");
    if(cq)cq.placeholder="搜索：芯片名 / 编号 / 类型 / 品质 / 属性文本…";
  }
  const title=boardCardTitle(m);
  var _ml=document.getElementById("metaline"); if(_ml) _ml.title="源包摘要＝该板块生成时所用客户端快照的摘要（不同板块快照可能不同）";
  document.title=title+" · Wiki";
  document.getElementById("title").textContent=title;
  renderServerSwitch(m);
  document.getElementById("metaline").textContent=
    `来源：${m.source_label||zhTitle(m.source_server)||'未记录'} · 生成 ${String(m.generated||'未记录').slice(0,10)}`;
  if(m.registry){
    const ml=document.getElementById("metaline");
    if(ml&&!ml.querySelector(".reglink")){
      const a=document.createElement("a");
      a.className="techlink reglink"; a.href=m.registry; a.target="_blank";
      a.textContent=" · 全量登记表";
      a.title="人物时装全量登记表（fashion_data + player_appear_data + simple_fashion_data）";
      ml.appendChild(a);
    }
  }
  const cnt={};d.items.forEach(i=>cnt[i.evidence]=(cnt[i.evidence]||0)+1);
  document.getElementById("pills").innerHTML=
    `<span class="pill">条目 <b>${d.items.length}</b></span>`+
    (partFilter.length?`<span class="pill">部位筛选 <b>${esc(partFilter.join(" / "))}</b></span>`:"")+
    Object.entries(cnt).map(([k,v])=>`<span class="pill">${EV_CN[k]} <b>${v}</b></span>`).join("")+
    Object.entries(m.state_summary||{}).map(([k,v])=>`<span class="pill state-pill ${STATE_CLASS[k]||"unresolved"}">${esc(STATE_CN[k]||k)} <b>${v}</b></span>`).join("")+
    Object.entries(m.name_status_summary||{}).map(([k,v])=>`<span class="pill name-pill" title="name_status=${esc(k)}">名称${esc(VALUE_CN.name_status[k]||k)} <b>${v}</b></span>`).join("");
  {
    const n=document.getElementById("notes");n.style.display="block";
    const _sha=m.package_sha?String(m.package_sha).slice(0,16)+"…":"未记录";
    const _ev=EV_CN[m.evidence]||m.evidence||"未标注";
    let _kv="";
    if(m.notes&&!m.notes_hidden)_kv+=`<div class="k">板块说明</div><div class="v">${esc(m.notes)}</div>`;
    _kv+=techSourcesHtml(m.tech_sources);
    _kv+=`<div class="k">源包摘要</div><div class="v mono">${esc(_sha)}</div>`;
    _kv+=`<div class="k">条目等级</div><div class="v">${esc(_ev)}</div>`;
    _kv+=`<div class="k">生成时间</div><div class="v">${esc(String(m.generated||"未记录"))}</div>`;
    n.innerHTML=`<details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="kv">${_kv}</div></details>`;
  }
  if(m.liaison_descs&&m.liaison_descs.length){
    const notesEl=document.getElementById("notes");
    const box=document.createElement("div");
    box.className="notes";box.style.background="#ecfdf5";box.style.border="1px solid #a7f3d0";box.style.color="#065f46";
    box.innerHTML="<b>联动外观官方描述（按主题全局对应，不逐款绑定）</b><ul style='margin:6px 0 0;padding-left:18px;line-height:1.7'>"+
      m.liaison_descs.map(x=>`<li><b>${esc(x.theme)}</b>：${esc(x.text)}</li>`).join("")+"</ul>";
    notesEl.parentNode.insertBefore(box,notesEl.nextSibling);
  }
  document.getElementById("q").addEventListener("input",scheduleSearch);
  document.getElementById("q").addEventListener("compositionend",scheduleSearch);
  document.getElementById("fEv").addEventListener("change",render);
  /* 品级筛选：下拉面板（点开列表 → 里面勾选，可多选）。点面板外关闭。 */
  (function(){
    const box=document.getElementById("fGrade");
    if(!box)return;
    const btn=document.getElementById("fGradeBtn"),panel=document.getElementById("fGradePanel");
    if(!btn||!panel)return;
    btn.addEventListener("click",function(e){
      e.stopPropagation();
      const open=panel.style.display!=="none";
      panel.style.display=open?"none":"block";
      btn.setAttribute("aria-expanded",String(!open));
    });
    panel.addEventListener("click",function(e){e.stopPropagation();});
    document.addEventListener("click",function(){
      if(panel.style.display!=="none"){panel.style.display="none";btn.setAttribute("aria-expanded","false");}
    });
    box.addEventListener("change",function(){
      GRADE_SELECTED=new Set([...panel.querySelectorAll('input[type=checkbox]:checked')].map(x=>x.value));
      updateGradeBtnLabel();
      render();
    });
  })();
  document.getElementById("fType").addEventListener("change",render);
  document.getElementById("fIp").addEventListener("change",render);
  document.getElementById("fOrder").addEventListener("change",render);
  // v1.3.2 修复：两个状态筛选此前漏绑 change ⇒ 选项可见但选择无效（用户报「筛选用不了」）
  document.getElementById("fRelease").addEventListener("change",render);
  document.getElementById("fNameSt").addEventListener("change",render);
  {
    // 排列方向：独立按钮，只切方向，不动筛选
    const dirBtn=document.getElementById("fDir");
    if(dirBtn&&!dirBtn.dataset.bound){
      dirBtn.dataset.bound="1";
      dirBtn.addEventListener("click",()=>{
        const next=dirBtn.dataset.dir==="asc"?"desc":"asc";
        dirBtn.dataset.dir=next;
        dirBtn.textContent=next==="asc"?"↑ 升序":"↓ 降序";
        render();
      });
    }
  }
  {
    // 卡片密度：舒适（默认，图区 150px / 1440 宽 4 列）↔ 紧凑（图区 100px / 5 列）；只切 body class，不重绘
    const dBtn=document.getElementById("fDensity");
    if(dBtn&&!(dBtn.dataset&&dBtn.dataset.bound)){
      if(dBtn.dataset)dBtn.dataset.bound="1";
      applyDensity(densityStored(),false);   // 恢复上次选择（localStorage），不改数据
      dBtn.addEventListener("click",()=>{
        const next=(dBtn.dataset&&dBtn.dataset.density)==="compact"?"comfortable":"compact";
        applyDensity(next,true);
      });
      // 密度只对皮肤图鉴（.skin-card）有意义：其它板不显示这个按钮
      const cl=document.body&&document.body.classList;
      if(cl&&cl.contains&&!cl.contains("skin-mode"))dBtn.style.display="none";
    }
  }
  if((d.items||[]).length>=HUGE_TABLE_MIN)buildHugeIndex(d);
  fillFilterSelects(d.items);
  if(FASHION_BOARD){frBuildFilters(d.items);fdOpenAll();}
  if(VEHICLE_BOARD)vBuildFilters(d.items);
  if(CHIP_BOARD)cBuildFilters(d.items);
  render();
  c2DeepLink();   // D2 深链：?id= 直开详情（芯片/时装/武器皮肤/异变核芯四板；由 C2.chips 是否就绪自守卫）
  /* ★ 2026-10-18：上架状态实时刷新 —— 每 30 秒检查一次，有皮肤跨过 sale_ts 就重绘，
     不跨就不动（避免每分钟整页重排、丢展开状态）。 */
  (function(){
    let sig=null;
    const snap=()=>(DATA&&DATA.items||[]).map(it=>listingOf(it)).join(",");
    setInterval(()=>{
      if(!DATA||!DATA.items||!DATA.items.length)return;
      const s=snap();
      if(sig===null){sig=s;return;}
      if(s!==sig){sig=s;try{render();}catch(err){/* 保持页面可用，不因刷新失败白屏 */}}
    },30000);
  })();
});
