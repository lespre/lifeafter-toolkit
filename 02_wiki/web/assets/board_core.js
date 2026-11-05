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
    : `data/boards/${b}.js?v=${encodeURIComponent(getParam("v")||"20261103-media1")}`;
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
  /* 称号板：筛选只保留数据里真有的轴 —— 获取途径（分组同源）、颜色档位、特性（动态/美术字）。
     其它控件（武器/皮肤系列、排序）全部隐藏。 */
  if(TITLE_BOARD){
    ["fGrade","fType","fIp","fRelease","fNameSt","fDir"].forEach(id=>{
      const el=document.getElementById(id);if(el)el.style.display="none";
    });
    const sh=document.getElementById("sortHint");if(sh)sh.style.display="none";
    const lh=document.getElementById("listingHint");if(lh)lh.style.display="none";
    const wrap=document.getElementById("fCustomWrap");if(wrap)wrap.innerHTML="";
    DATA._custFilters=[];
    /* 排序轴：称号编号（item_id），默认大 → 小。沿用 #fOrder 的既有 id_asc/id_desc 语义。 */
    const oSel=document.getElementById("fOrder");
    if(oSel){
      oSel.innerHTML=`<option value="id_desc" selected>编号：大 → 小</option><option value="id_asc">编号：小 → 大</option>`;
      oSel.value="id_desc";
      oSel.title="按称号编号排序；勾选「按获取途径分组」后改为组内排序";
      oSel.style.display="";
    }
    const mk=(label,opts)=>{
      const s=document.createElement("select");
      s.innerHTML=`<option value="">${esc(label)}</option>`+
        opts.map(([k,l])=>`<option value="${k==null?"__none__":esc(k)}">${esc(l)}</option>`).join("");
      s.setAttribute("aria-label",label.replace(/^全部/,""));
      s.onchange=render;wrap.appendChild(s);return s;
    };
    DATA._custFilters.push({key:"obtain",sel:mk("全部获取途径",TITLE_GROUPS)});
    DATA._custFilters.push({key:"color",sel:mk("全部颜色",[["蓝","蓝色"],["紫","紫色"],["金","金色"],["红","红色"],["绿","绿色"]])});
    /* 特性是数组字段（flags），走自定义判定，不按字符串等值比较 */
    DATA._custFilters.push({sel:mk("全部特性",[["动态","动态"],["美术字","美术字"]]),
      test:(it,v)=>Array.isArray(it.flags)&&it.flags.includes(v)});
    /* 分组改为可勾选：默认平铺（整表按编号排），勾上才按获取途径分组 */
    const cbLabel=document.createElement("label");
    cbLabel.className="tg-toggle";
    cbLabel.innerHTML=`<input type="checkbox" id="tgGroup"><span>按获取途径分组</span>`;
    wrap.appendChild(cbLabel);
    const cb=cbLabel.querySelector("input");
    cb.checked=titleGroupOn;
    cb.onchange=()=>{titleGroupOn=cb.checked;render();};
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
    if(AVATAR_BOARD){
      /* 头像板排序：只有「标号」一轴；组内比较 item_id，默认大 → 小 */
      oSel.innerHTML=`<option value="id_desc" selected>标号：大 → 小（默认）</option><option value="id_asc">标号：小 → 大</option>`;
      oSel.value="id_desc";
      oSel.title="按标号（item_id）排序；先按类型分组（头像 / 头像框 / 名片框），再在组内比较标号";
      oSel.style.display="";
    } else if(CORE_BOARD){
      /* 核芯板：按编号（item_id）排序，默认小 → 大（保持原行序） */
      oSel.innerHTML=`<option value="code_asc" selected>编号：小 → 大（默认）</option><option value="code_desc">编号：大 → 小</option>`;
      oSel.value="code_asc";
      oSel.title="按核芯编号（item_id）排序";
      oSel.style.display="";
    } else if(!nucleusSort)oSel.style.display="none";
    cfg.forEach((f,ix)=>{
      /* 活动总表：月份由台账顶部的年份/月份索引承担，不再放下拉（避免两套月份入口） */
      if(ACTIVITY_BOARD&&f.key==="month")return;
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
    if(EDIBLE_BOARD){
      const n=items.filter(it=>String(it.kind||"")==="食材").length;
      const lb=document.createElement("label");
      lb.className="tg-toggle";
      lb.innerHTML=`<input type="checkbox" id="tgEdible"><span>展开食材 / 可食用物品（${n}）</span>`;
      wrap.appendChild(lb);
      const cb=lb.querySelector("input");
      cb.checked=edibleShowIngredients;
      cb.onchange=()=>{edibleShowIngredients=cb.checked;render();};
    }
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
/* ════════════════ 装备属性板（board id 前缀 equipment_attrs）════════════════════
   用户 2026-11-01 口径：子卡改成「人物时装同款」——
   顶部大图 + 名字 + 关键几项 pill + 描述；其余字段（等级/槽位/类型码/主属性/属性/
   模型/图标状态/服务器/溯源）全部折进「技术详情 / 其余字段」。
   ★ 类名 eq-* + body.equip-mode，其它板零影响。 */
const EQUIP_FACE=new Set(["id","name","row_key","equip_label","weapon_kind_label","durability",
  "max_shield","shield_label","base_score","charm_value","desc","level","icon","icon_state","_media"]);
/* 装备大图（_media.images 首个即 2:1 图标）：卡面与 D2 详情共用同一份图源 */
function equipImgs(it){return ((it._media&&it._media.images)||[]).filter(x=>x&&x.png);}
/* 关键属性 pill：卡面与详情共用，避免两处口径漂移 */
function equipPillsHTML(it){
  const sub=[];
  if(it.equip_label)sub.push(`<span class="fr-part" title="装备类型" data-k="equip_label">${esc(it.equip_label)}</span>`);
  if(it.weapon_kind_label)sub.push(`<span class="fr-part" title="武器细类（按 weapon_kind 归纳）" data-k="weapon_kind_label">${esc(it.weapon_kind_label)}</span>`);
  if(it.durability!=null)sub.push(`<span class="fr-part" title="耐久">耐久 ${esc(it.durability)}</span>`);
  if(it.max_shield!=null)sub.push(`<span class="fr-part" title="护盾值">护盾 ${esc(it.max_shield)}</span>`);
  if(it.shield_label)sub.push(`<span class="fr-part" title="护盾档位" data-k="shield_label">${esc(it.shield_label)}</span>`);
  if(it.base_score!=null)sub.push(`<span class="fr-charm" title="评分">评分 ${esc(it.base_score)}</span>`);
  if(it.charm_value!=null&&it.charm_value!=="")sub.push(`<span class="fr-charm" title="魅力值">魅力 ${esc(it.charm_value)}</span>`);
  return sub.join("");
}
/* 其余字段（卡内折叠区与 D2 详情共用同一份清单） */
function equipRestRows(it){
  const kv=[];
  Object.entries(it).forEach(([k,v])=>{
    if(EQUIP_FACE.has(k)||FIXED.has(k)||v==null||v===""||(Array.isArray(v)&&!v.length))return;
    const mono=(k==="model_path"||k==="row_key")?" mono":"";
    kv.push(`<div class="k">${esc(FIELD_CN[k]||k)}</div><div class="v${mono}">${esc(fmtVal(k,v))}</div>`);
  });
  return kv.join("");
}
function equipCardHTML(it,cidx){
  const imgs=equipImgs(it);
  const rail=imgs.length
    ? `<div class="fr-rail">${imgs.slice(0,1).map(x=>`<figure><img src="${esc(x.png)}" alt="" loading="lazy"></figure>`).join("")}</div>`
    : `<div class="fr-rail"><figure class="ph"><span class="fr-dur">无图标</span></figure></div>`;
  const desc=String(it.desc||"").trim();
  return `<div class="i eqcard"${cidx==null?"":` data-cidx="${cidx}"`}>
    ${rail}
    <div class="fr-head"><div class="fr-name" title="${esc(it.name||it.id)}">${esc(it.name||it.id)}</div>${
      it.level!=null?`<span class="fr-grade" title="等级">Lv ${esc(it.level)}</span>`:""}</div>
    <div class="fr-sub">${equipPillsHTML(it)}</div>
    ${desc?`<div class="eq-desc">${esc(desc)}</div>`:""}
    <details class="tech sub"><summary>其余字段 / 数据详情</summary>
      <div class="kv">${equipRestRows(it)}</div>
      ${renderTechSection([["provenance",effProv(it)],["field_provenance",it.field_provenance],["source",it.source],["evidence_level",it.evidence_level],["status_tags",it.status_tags]])}
    </details>
  </div>`;
}
/* 2026-11-02（用户反馈「点击不能打开子卡详情」）：
   D2 详情不能直接复用卡面 —— 卡面把字段折进 details，而 c2Render 会强制收起 tech 折叠区，
   点开看到的还是同一张缩小的卡。这里自建详情体：大图 + 关键 pill + 完整描述 + 属性表 + 其余字段，
   全部默认可见；只有溯源审计仍折叠。 */
function equipD2Body(it,mode){
  const imgs=equipImgs(it);
  FR_IMGS[it.id]=((it._media||{}).images||[]).map(x=>x.png);
  const rail=imgs.length
    ? `<div class="eq-d2-rail">${imgs.map((x,i)=>`<figure class="eq-d2-thumb${i===0?" fr-zoom":""}" data-idx="${i}" title="${i===0?"点击看大图":esc(x.base||"")}"><img src="${esc(x.png)}" alt="" loading="lazy"></figure>`).join("")}</div>`
    : `<div class="eq-d2-rail"><figure class="ph"><span class="fr-dur">无图标</span></figure></div>`;
  const desc=String(it.desc||"").trim();
  const rows=[];
  const put=(label,v)=>{if(v!==null&&v!==undefined&&v!=="")rows.push(`<div class="k">${esc(label)}</div><div class="v">${esc(v)}</div>`);};
  put("装备类型",it.equip_label);
  put("武器细类",it.weapon_kind_label);
  put("等级",it.level);
  put("耐久",it.durability);
  put("护盾值",it.max_shield);
  put("护盾档位",it.shield_label);
  put("基础评分",it.base_score);
  put("魅力值",it.charm_value);
  const rest=equipRestRows(it);
  const content=`<div class="c2-embed eq-d2">
    ${rail}
    <div class="fr-sub">${equipPillsHTML(it)}</div>
    ${desc?`<div class="eq-d2-desc">${esc(desc)}</div>`:""}
    ${rows.length?`<div class="fr-sec">属性</div><div class="fr-kv">${rows.join("")}</div>`:""}
    ${rest?`<div class="fr-sec">其余字段</div><div class="fr-kv">${rest}</div>`:""}
    ${renderTechSection([["provenance",effProv(it)],["field_provenance",it.field_provenance],["source",it.source],["evidence_level",it.evidence_level],["status_tags",it.status_tags]])}
  </div>`;
  return mode==="dock"?content:c2BarHTML(it,(C2.prov&&C2.prov.meta)?C2.prov.meta(it):"","main")+content;
}
/* 时装图标（游戏内真实引用）：最多显示 6 张，其余计数；无资源时用客户端占位图 */
function renderItemMedia(m){
  if(!m)return "";
  /* 2026-10-30：动态头像 / 头像框 / 名片框 的 APNG 挂在**主图**（role=frame）上。
     卡面默认只显示游戏内静态图，悬停或开详情才换 src 播放 —— 673 张卡不会一进页面就拉 300 个动图。
     ★ 背景图（role=background，名片场景底图）不是边框图，不能挂动图、也不占主图位。 */
  const anim=m.anim?esc(m.anim):"";
  /* 2026-11-01：名片框有「背景（role=background）」层时，与边框图（role=frame）
     叠成同一张整卡 —— 背景垫底、边框压上，才是游戏内名片的样子。
     只有背景、没有边框的卡片不叠（背景仍按次图小图展示）。 */
  const _all=(m.images||[]);
  const _fr=_all.find(x=>x.role!=="background");
  /* 只有量到「内孔」的静态高清边框才叠 —— 背景要铺进边框的透明内孔、框在外包住。
     Spine 首帧是 168×168 紧裁方图，套不进内孔，不叠（仍按次图展示）。 */
  const stack=!!(_fr&&_fr.hole&&_all.some(x=>x.role==="background"));
  const _h=(_fr&&_fr.hole)||[0.094,0.132,0.811,0.739];
  /* --ar：卡面比例锁死成边框图本身的宽高比。叠加模式的每个图层都绝对定位，
     否则悬停换成低分辨率 Spine 动图时，img 的内在尺寸一变整卡就跳高。 */
  const _ar=(_fr&&_fr.w&&_fr.h)?`--ar:${_fr.w}/${_fr.h};`:"";
  const stStyle=stack?` style="${_ar}--hl:${(_h[0]*100).toFixed(2)}%;--ht:${(_h[1]*100).toFixed(2)}%;--hw:${(_h[2]*100).toFixed(2)}%;--hh:${(_h[3]*100).toFixed(2)}%"`:"";
  const imgs=_all.slice(0,6).map((x,i)=>{
    const bg=(x.role==="background");
    /* 非矩形内孔：用边框量出来的透明区轮廓做 clip-path，背景只在孔里显形，
       矩形 bbox 兜不住斜边/角饰，不裁就会从框外露出来。 */
    const _cp=(bg&&_fr&&_fr.clip&&_fr.clip.length>=3)
      ?` style="clip-path:polygon(${_fr.clip.map(p=>`${(p[0]*100).toFixed(2)}% ${(p[1]*100).toFixed(2)}%`).join(",")})"`
      :"";
    /* 叠加模式照样挂动图：卡面比例已被 --ar 锁死，悬停换 src 不会改变卡面尺寸。
       只有排在后面的次图（非主图）不挂，避免一张卡上多个动图同时播放。 */
    const hot=(anim&&i===0&&!bg);
    /* 2026-11-02：烘焙过的背景（fit=frame）与边框图同尺寸，孔外已是全透明 alpha，
       直接 inset:0 铺满即可 —— 不再按 --hl/--hw 摆位，也不吃 clip-path。 */
    const _full=(bg&&x.fit==="frame")?" mi-bg-full":"";
    /* 2026-11-02：核芯特技图单独打标（核芯板 CSS 将其挪到子卡左上角当小角标） */
    const _skill=(x.kind==="核芯特技")?" mi-skill":"";
    return `<figure class="mi${hot?" mi-anim":""}${bg?" mi-bg":""}${_full}${_skill}"${_cp}><img src="${esc(x.png)}" alt="${esc(x.base||x.suffix||"")}" loading="lazy"${hot?` data-anim="${anim}"`:""}>${hot?`<span class="anim-dot" title="有 Spine 动画，悬停播放 / 点开详情自动播放">动</span>`:""}<figcaption>${esc(x.label||x.suffix||"raw")}</figcaption></figure>`;
  }).join("");
  const ph=m.placeholder?`<figure class="mi ph"><img src="${esc(m.placeholder)}" alt="客户端占位图" loading="lazy"><figcaption>占位</figcaption></figure>`:"";
  /* 边框图确实缺失 → 如实标注，但不拿场景图顶替「边框」这个身份；
     若手里还有名片背景，就让背景独占卡面（状态标签仍写「无边框图」），
     不要一块「缺口」占位框 + 一张缩小背景图并列显示。 */
  const nofig=(m.frame_status==="missing"&&_all.length===0)?`<figure class="mi nofig"><span>边框图缺失<br>（当前包快照无该资源）</span><figcaption>缺口</figcaption></figure>`:"";
  const more=(m.images||[]).length>6?`<span class="mi-more">+${m.images.length-6}</span>`:"";
  return `<div class="i-media${stack?" i-stack":""}"${stStyle}>${nofig}${imgs}${ph}${more}</div>`;
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
/* 2026-11-01：装备属性四卡（三服总览 + 三张分服卡）——卡面按人物时装同款渲染 */
const EQUIP_BOARD=(function(){try{return /^equipment_attrs/.test(getParam("b")||"");}catch(e){return false;}})();
/* ════════════════════ 基因潜能板（board id = gene_potential_catalog）════════════════════
   2026-11-02 用户口径：必须像装备属性板一样分服务器，不能把两服混进同一张视图。
   2026-11-04 起数据来自 PE 活树行级解码（133 条）：
   经典服 111 条（gene_node_data.nxs 141 行去掉 30 条 race=1 通用，全字段）+ 简单生存 48 条
   （kj1 63 行去 15 条通用）；其中简单生存独有 22 条（id 前缀 gene_kj1_）。
   两服同名节点分值不完全一致（初级 300/400），另一侧写在 node_score_branches。
   ⇒ 页内服别 Tab（两服总览 / 简单生存 / 经典服）；两页都用「种族 × 等级」矩阵，
      等级泳道按数据里实际出现的 level 动态生成（经典服有 Lv0–Lv6，不再写死 Lv0–Lv3）。
   ★ 类名统一 gene-*，样式只挂 body.b-gene_potential_catalog，其它板零影响。 */
const GENE_BOARD=(function(){try{return (getParam("b")||"")==="gene_potential_catalog";}catch(e){return false;}})();
const GENE_SERVERS=[
  {key:"overview",label:"两服总览",branch:null,desc:"服别入口"},
  {key:"kj1",label:"简单生存",branch:"简单生存",desc:"字段级 · 种族 × 等级"},
  {key:"classic",label:"经典服",branch:"经典服",desc:"行级字段 · 种族 × 6 档"}
];
const GENE_RACE_ORDER=["人类","半感染者","械骨人"];
const GENE_RACE_CLS={"人类":"r-human","半感染者":"r-infected","械骨人":"r-bone"};
const GENE_LEVEL_BASE=[0,1,2,3];
/* 等级泳道：基线 Lv0–Lv3（简单生存口径）∪ 数据里实际出现的 level。
   经典服表有 Lv4–Lv6（特级/超级/究级），写死 4 列会把它们整片藏掉。 */
function geneLaneLevels(list,idxs){
  const set=new Set(GENE_LEVEL_BASE);
  (idxs||[]).forEach(i=>{const v=Number(list[i]&&list[i].level);if(Number.isFinite(v))set.add(v);});
  return [...set].sort((a,b)=>a-b);
}
function geneLevelRange(list){
  const lv=geneLaneLevels(list,list.map((_,i)=>i));
  return lv.length?(lv.length===1?`Lv${lv[0]}`:`Lv${lv[0]}–Lv${lv[lv.length-1]}`):"—";
}
const GENE_TIER_ORDER=["初级","中级","高级","超级","特级","究级"];
let GENE_SERVER=(function(){
  try{
    const hit=GENE_SERVERS.find(s=>s.key===(getParam("gs")||""));
    return hit?hit.key:"overview";
  }catch(e){return "overview";}
})();
function geneServerDef(){return GENE_SERVERS.find(s=>s.key===GENE_SERVER)||GENE_SERVERS[0];}
function geneBranches(it){return Array.isArray(it&&it.server_branches)?it.server_branches:[];}
function geneInServer(it,branch){return !branch||geneBranches(it).includes(branch);}
function geneRaceOf(it){const r=String((it&&it.race_name)||"");return GENE_RACE_ORDER.includes(r)?r:"";}
function geneRaceCls(it){return GENE_RACE_CLS[geneRaceOf(it)]||"r-none";}
function geneIsRoster(it){return it.level===null||it.level===undefined||it.level==="";}
/* 卡面：族色条 + 名字 +（Lv / 分值 或 档位）徽章 + 效果（名册级给口径说明），证据标签压成圆点 */
function geneCardHTML(it,cidx){
  const roster=geneIsRoster(it);
  const cls=`i roster gene-card ${geneRaceCls(it)}${roster?" gene-mini":""}`;
  const badges=[];
  if(roster){
    if(it.tier)badges.push(`<span class="gene-b tier" data-tier="${esc(it.tier)}">${esc(it.tier)}</span>`);
  }else{
    if(it.level!=null)badges.push(`<span class="gene-b lv" title="潜能等级">Lv${esc(it.level)}</span>`);
    if(it.node_score!=null)badges.push(`<span class="gene-b sc" title="节点分值（静态表 node_score）">${esc(it.node_score)} 分</span>`);
  }
  const shared=geneBranches(it).length>1;
  if(shared)badges.push(`<span class="gene-b srv" title="简单生存与经典服同口径的字段级节点">两服共有</span>`);
  const eff=String(it.effect_desc||"").trim();
  const body=roster
    ? `<div class="gene-note">名册级 · 字段待解码回填</div>`
    : `<div class="gene-eff" title="${esc(eff)}">${esc(eff||"未给出效果文本")}</div>`;
  const tags=Array.isArray(it.status_tags)?it.status_tags:[];
  const dots=tags.length
    ? `<span class="gene-dots">${tags.map(t=>`<i class="gene-dot ${STATE_CLASS[t]||"unresolved"}" title="${esc(STATE_CN[t]||COMMON_VAL_CN[t]||t)}"></i>`).join("")}</span>`
    : "";
  return `<div class="${cls}" data-cidx="${cidx}" role="button" tabindex="0" aria-label="查看「${esc(it.name||it.id)}」详情">
    <span class="gene-race-bar" aria-hidden="true"></span>
    <div class="gene-top"><span class="gene-name" title="${esc(it.name||it.id)}">${esc(it.name||it.id)}</span>${dots}</div>
    <div class="gene-bads">${badges.join("")}</div>
    ${body}
  </div>`;
}
function geneTabsHTML(){
  return `<nav class="gene-tabs" role="tablist" aria-label="服别">
    ${GENE_SERVERS.map(s=>{
      const on=s.key===GENE_SERVER;
      return `<button type="button" class="gene-tab${on?" on":""}" role="tab" aria-selected="${on}" data-gene-server="${s.key}">
        <span class="gene-tab-nm">${esc(s.label)}</span><span class="gene-tab-ds">${esc(s.desc)}</span>
      </button>`;
    }).join("")}
  </nav>`;
}
function geneStatsHTML(list){
  const shared=list.filter(it=>geneBranches(it).length>1).length;
  if(GENE_SERVER==="classic"){
    const field=list.filter(it=>!geneIsRoster(it)).length;
    const roster=list.filter(geneIsRoster).length;
    return `<div class="gene-stats">
      <span class="gene-stat">条目 <b>${list.length}</b></span>
      <span class="gene-stat">字段级 <b>${field}</b></span>
      ${roster?`<span class="gene-stat">名册级 <b>${roster}</b></span>`:""}
      <span class="gene-stat">两服共有字段级 <b>${shared}</b></span>
    </div>`;
  }
  const races=GENE_RACE_ORDER.filter(r=>list.some(it=>geneRaceOf(it)===r)).length;
  const lv=[...new Set(list.map(it=>it.level).filter(v=>v!=null))].sort((a,b)=>a-b);
  const lvTxt=lv.length?(lv.length===1?`Lv${lv[0]}`:`Lv${lv[0]}–Lv${lv[lv.length-1]}`):"—";
  return `<div class="gene-stats">
    <span class="gene-stat">条目 <b>${list.length}</b></span>
    <span class="gene-stat">种族 <b>${races}</b></span>
    <span class="gene-stat">等级 <b>${lvTxt}</b></span>
    <span class="gene-stat">两服共有 <b>${shared}</b></span>
  </div>`;
}
function geneSectionHead(title,n,note){
  return `<div class="gene-sec-h"><span class="gene-sec-t">${esc(title)}</span><span class="gene-sec-n">${n} 条</span>${note?`<span class="gene-sec-note">${esc(note)}</span>`:""}</div>`;
}
/* 种族 × 等级矩阵：每个种族一行 4 列等级泳道（Lv0–Lv3） */
function geneRaceMatrix(list,htmls,idxs){
  const byRace=new Map();
  idxs.forEach(i=>{
    const r=geneRaceOf(list[i])||"未标注";
    if(!byRace.has(r))byRace.set(r,[]);
    byRace.get(r).push(i);
  });
  const order=[...GENE_RACE_ORDER,...[...byRace.keys()].filter(r=>!GENE_RACE_ORDER.includes(r))];
  const secs=[];
  order.forEach(race=>{
    const arr=byRace.get(race);
    if(!arr||!arr.length)return;
    const lanes=geneLaneLevels(list,idxs).map(lv=>{
      const lane=arr.filter(i=>Number(list[i].level)===lv);
      return `<div class="gene-lane">
        <div class="gene-lane-h"><span>Lv${lv}</span><b>${lane.length}</b></div>
        <div class="gene-lane-body">${lane.length?lane.map(i=>htmls[i]).join(""):`<span class="gene-lane-empty">无节点</span>`}</div>
      </div>`;
    }).join("");
    secs.push(`<section class="gene-race-sec ${GENE_RACE_CLS[race]||"r-none"}">
      <div class="gene-race-h"><i class="gene-race-dot" aria-hidden="true"></i><span class="gene-race-nm">${esc(race)}</span><span class="gene-race-cn">${arr.length} 条</span></div>
      <div class="gene-lanes">${lanes}</div>
    </section>`);
  });
  return `<div class="gene-matrix">${secs.join("")}</div>`;
}
/* 经典服名册级：6 个档位列 */
function geneTierBoard(list,htmls,idxs){
  const cols=GENE_TIER_ORDER.map(t=>{
    const arr=idxs.filter(i=>String(list[i].tier||"")===t);
    return `<div class="gene-tier-col" data-tier="${esc(t)}">
      <div class="gene-tier-h"><span>${esc(t)}</span><b>${arr.length}</b></div>
      <div class="gene-tier-body">${arr.length?arr.map(i=>htmls[i]).join(""):`<span class="gene-lane-empty">无条目</span>`}</div>
    </div>`;
  }).join("");
  return `<div class="gene-tiers">${cols}</div>`;
}
function geneBoardHTML(list,htmls){
  const tabs=geneTabsHTML(),stats=geneStatsHTML(list);
  if(GENE_SERVER==="classic"){
    const fieldIdx=[],rosterIdx=[];
    list.forEach((it,i)=>(geneIsRoster(it)?rosterIdx:fieldIdx).push(i));
    let body="";
    if(fieldIdx.length)body+=geneSectionHead("字段级节点",fieldIdx.length,"种族 × 潜能等级 · 与简单生存服同口径")+geneRaceMatrix(list,htmls,fieldIdx);
    if(rosterIdx.length){
      const uniq=new Set(rosterIdx.map(i=>String(list[i].name||"")).filter(Boolean)).size;
      body+=geneSectionHead("名册级条目",rosterIdx.length,`经典服池名册 · 仅名字与档位 · ${uniq} 个名字`);
      body+=geneTierBoard(list,htmls,rosterIdx);
    }
    return tabs+stats+body;
  }
  return tabs+stats+geneRaceMatrix(list,htmls,list.map((_,i)=>i));
}
function geneOvCard(key,label,desc,n,rows,cls){
  return `<button type="button" class="gene-ov-card ${cls||""}" data-gene-server="${key}">
    <span class="gene-ov-top"><span class="gene-ov-nm">${esc(label)}</span><span class="gene-ov-n">${n}<em>条</em></span></span>
    <span class="gene-ov-desc">${esc(desc)}</span>
    <span class="gene-ov-rows">${rows.map(r=>`<span>${esc(r)}</span>`).join("")}</span>
    <span class="gene-ov-go">进入 →</span>
  </button>`;
}
function geneOverviewRender(g,items){
  C2.prov=GENE_D2;C2.chips=[];C2.html={};
  const kj=items.filter(it=>geneInServer(it,"简单生存"));
  const cl=items.filter(it=>geneInServer(it,"经典服"));
  const shared=items.filter(it=>geneBranches(it).length>1);
  const clField=cl.filter(it=>!geneIsRoster(it)).length;
  const clRoster=cl.filter(geneIsRoster).length;
  const clKj1=kj.length-shared.length;  /* 简单生存独有节点（id 前缀 gene_kj1_） */
  const hit=(items.length!==DATA.items.length)
    ? `<div class="gene-ov-hit">当前搜索 / 筛选命中 ${items.length} 条 —— 点下方服别查看命中结果</div>`:"";
  g.innerHTML=geneTabsHTML()+hit+`<div class="gene-ov">
    ${geneOvCard("kj1","简单生存","字段级 · 种族 × 等级",kj.length,
      [`种族 ${GENE_RACE_ORDER.filter(r=>kj.some(it=>geneRaceOf(it)===r)).length} 个 · 潜能等级 ${geneLevelRange(kj)}`,
       "带效果文本与节点分值",
       `含两服共有 ${shared.length} 条`],"kj1")}
    ${geneOvCard("classic","经典服","行级字段 · 种族 × 6 档",cl.length,
      [`行级字段 ${clField} 条（含两服共有 ${shared.length} 条）`,
       `等级 ${geneLevelRange(cl)} · 6 档 + 特殊节点`,
       "效果文本 / 节点分值均取自表体；同名节点分值差异见 node_score_branches"],"classic")}
  </div>`+`<div class="gene-ov-note">两服共有 ${shared.length} 条同名节点会同时出现在两服页内；简单生存另有 ${clKj1} 条独有节点（id 前缀 gene_kj1_），经典服条目已全部是行级字段。</div>`;
  if(C2.open)c2Resync();
}
function geneCountText(list){
  const total=DATA.items.length;
  if(GENE_SERVER==="overview"){
    return `两服总览 · 共 ${total} 条 · 简单生存 ${DATA.items.filter(it=>geneInServer(it,"简单生存")).length} · 经典服 ${DATA.items.filter(it=>geneInServer(it,"经典服")).length} · 两服共有 ${DATA.items.filter(it=>geneBranches(it).length>1).length}`;
  }
  if(GENE_SERVER==="classic"){
    const field=list.filter(it=>!geneIsRoster(it)).length,roster=list.filter(geneIsRoster).length;
    return `显示 ${list.length} / ${total} 条 · 经典服 · 行级字段 ${field} 条`+(roster?` · 名册级 ${roster} 条`:"");
  }
  return `显示 ${list.length} / ${total} 条 · 简单生存 · ${GENE_RACE_ORDER.filter(r=>list.some(it=>geneRaceOf(it)===r)).length} 个种族 · ${new Set(list.map(it=>it.level).filter(v=>v!=null)).size} 个等级`;
}
function geneD2Body(it,mode){
  const rows=[];
  const put=(k,v)=>{if(v===null||v===undefined||String(v)==="")return;rows.push([k,String(v)]);};
  put("种族",it.race_name||"未标注（经典服名册级）");
  put("潜能等级",it.level!=null?`Lv${it.level}`:"未给出");
  put("节点分值",it.node_score!=null?it.node_score:"未给出");
  put("档位",it.tier);
  put("服型并集",geneBranches(it).join("、"));
  put("条目类型",it.kind);
  put("字段口径",it.fields_note);
  put("来源表",it.source);
  put("证据等级",EV_CN[it.evidence]||it.evidence);
  put("状态标签",(Array.isArray(it.status_tags)?it.status_tags:[]).map(t=>STATE_CN[t]||COMMON_VAL_CN[t]||t).join("、"));
  put("源表行键",it.provenance&&it.provenance.row_key);
  const eff=String(it.effect_desc||"").trim();
  const kv=rows.map(([k,v])=>`<div class="k">${esc(k)}</div><div class="v">${esc(v)}</div>`).join("");
  const content=`<div class="c2-embed gene-d2">
    <div class="gene-d2-eff"><span class="gene-d2-k">效果</span>${eff?esc(eff):'<span class="gene-d2-na">该条目只有池名册级信息（名字 + 档位），字段解码后回填</span>'}</div>
    <div class="fr-sec">字段</div>
    <div class="fr-kv">${kv}</div>
  </div>`;
  return mode==="dock"?content:c2BarHTML(it,(C2.prov&&C2.prov.meta)?C2.prov.meta(it):"","main")+content;
}
const GENE_D2={
  idOf:it=>it.id,
  name:it=>it.name||it.display_name||it.id,
  body:geneD2Body,
  meta:it=>{
    const parts=[];
    if(it.race_name)parts.push(`<span class="skin-tag">${esc(it.race_name)}</span>`);
    if(it.level!=null)parts.push(`<span class="skin-tag">Lv${esc(it.level)}</span>`);
    if(it.node_score!=null)parts.push(`<span class="skin-tag">${esc(it.node_score)} 分</span>`);
    if(it.tier)parts.push(`<span class="skin-tag">${esc(it.tier)}</span>`);
    parts.push(`<span class="c2-no">节点 ${esc(it.item_id??it.id)}</span>`);
    return parts.join("");
  }
};
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
  // 2026-11-01：gender_scope=通用（男女共用模型/挂点）⇒ 两种性别都能穿，性别筛选两边都要命中
  if(g==="通用")return ["女","男"];
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
  /* 2026-11-01：头饰/面饰/挂饰 一张卡会同时有男图和女图（player_module_appear_data 的
     icon / female_icon 两列），必须把「哪张是男、哪张是女」标在图上，否则两张并排看不出区别。 */
  const show=imgs.slice(0,4).map((x,i)=>{
    const gtag=(x.label==="男"||x.label==="女")?`<span class="fr-gtag" title="${x.label}款图标">${x.label}</span>`:"";
    return `<figure class="fr-zoom" data-idx="${i}" title="${esc((x.base||"")+(x.suffix||""))}">${gtag}<img src="${esc(x.png)}" alt="${esc(x.base||"")}" loading="lazy"></figure>`;
  }).join("");
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
    card.classList.contains("roster")||
    (card.classList.contains("eqcard")&&EQUIP_BOARD);
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
  /* 同 model 卡片内的缩略图不参与「点图看大图」 */
  if(e.target.closest&&e.target.closest("[data-sib-id]"))return;
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
/* 藏花（花苞替换）：优先用花部外观名，其次用 .gim 模型文件名，最后退到花部行号 */
function frFlowerText(it){
  const fb=it.flower_bud||{};
  if((fb.names||[]).length)return fb.names.join(" / ");
  const ps=(fb.paths||[]).map(p=>String(p).split(/[\\/]/).pop());
  if(ps.length)return ps.join(" / ");
  return (fb.appear_ids||[]).join(" / ")||"—";
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
      ${(it.charm_value||it.equip_charm) ? `<span class="fr-charm" title="魅力值：${esc(it.charm_note||(it.charm_value?"fashion_data.charm_value":"all_equips_data.charm_value（装备表）"))}${(it.charm_candidates||[]).length?" · 各款式行取值 "+esc(it.charm_candidates.join(" /"))+"（取主行）":""}">魅力 ${esc(it.charm_value||it.equip_charm)}</span>` : ""}
      ${mid!=null?`<span class="fr-model" title="model_id（fashion_data 表）${refs.length?` · 外观编号（player_appear_data）：${refs.join(" / ")}`:""}">model ${esc(mid)}${refs.length?`<span class="fr-ref"> · ${esc(refs[0])}${refs.length>1?`+${refs.length-1}`:""}</span>`:""}</span>`:`<span class="fr-model">model —</span>`}
      ${(()=>{const vm=it.version_merge;if(!vm||!(vm.aliases||[]).length)return "";
        return `<span class="fr-alt" title="同一 model 的另一条记录，已并入本卡：${esc(vm.aliases.join("、"))}">含${esc((vm.prefixes||[]).join("")||"新")}·版</span>`;})()}
      ${(()=>{const vma=it.alias_merge;if(!vma||!(vma.aliases||[]).length)return "";
        const nm=vma.aliases.map(x=>String(x).split("-")[0]).join("、");
        return `<span class="fr-alt fr-alias" title="表里同 model 同一件时装的另一条记录（开发/占位名），已并入本卡：${esc(vma.aliases.join("、"))}">别名 ${esc(nm)}</span>`;})()}
      ${((it.value_words||[]).length)?`<span class="fr-alt fr-vw" title="${esc(frValueWordsTitle(it))}">${esc(frValueWords(it).split(" / ")[0]||"卖点")}${(it.value_words||[]).length>1?` +${(it.value_words||[]).length-1}`:""}</span>`:""}
      ${(it.dye&&((it.dye.scheme_count||0)>0||((it.dye.hair||[]).length>0)))?`<span class="fr-alt fr-dye" title="${esc(frDyeText(it))}${it.dye&&(it.dye.hair||[]).length?"；发色 "+esc(frHairDyeText(it)):""}">可染色</span>`:""}
      ${it.reborn_vis?`<span class="fr-alt fr-bud" title="reborn_vis=1">藏花</span>`:""}
      ${it.flower_bud?`<span class="fr-alt fr-flower" title="换花：replace_flower_path 把花苞换成主题花，不走藏花；${it.flower_bud&&it.flower_bud.reborn_socket?"挂在 "+(it.flower_bud.reborn_socket.socket||"flower")+" 挂点、仅再生者形态挂载：":""}${esc(frFlowerText(it))}">换花</span>`:""}
      ${(()=>{const g=(it._media&&it._media.missing)||[];if(!g.length)return "";
        const gs=[...new Set(g.map(x=>x.gender).filter(Boolean))].sort().join("");
        const who=gs==="男女"?"男女":(gs||"");
        return `<span class="fr-gap" title="表里登记了该性别的图标，但 PE/PC/refs 三处都没有这张图">缺${esc(who)}图${g.length>1?` · ${g.length}`:""}</span>`;})()}
    </div>
    ${full?frDetailsHTML(it,frKvHtml(it)):""}
  </div>`;
}
/* 2026-11-01：染色方案（change_color_id → appear_change_color_data，384/388 对上）*/
function frDyeText(it){
  const d=it.dye;if(!d)return "";
  const parts=[];const n=d.scheme_count||0;
  if(n)parts.push(`${n} 套方案`);
  if((d.scheme_ids||[]).length)parts.push(`id ${d.scheme_ids.join(" / ")}`);
  if((d.colors||[]).length)parts.push(`配色 ${d.colors.slice(0,6).join(" ")}${(d.colors.length>6?" …":"")}`);
  return parts.join(" · ");
}
function frDyeSwatches(it){
  const cols=(it.dye&&it.dye.colors)||[];if(!cols.length)return "";
  const rgb=c=>(c.length>=8?c.slice(2):c);
  return `<span class="fr-swatch">${cols.slice(0,8).map(c=>`<i style="background:#${esc(rgb(c))}"></i>`).join("")}</span>`;
}
function frHairDyeText(it){
  const h=(it.dye&&it.dye.hair)||[];if(!h.length)return "";
  const out=[];
  for(const x of h){
    const cs=(x.color_socket||[]).filter(Boolean);
    out.push(`${x.id}${cs.length?"（"+cs.join("/")+"）":""}`);
  }
  return out.join(" · ");
}
/* 2026-11-01：同居好感度（fashion_data.friendliness → cohabit_level_data 五档）*/
function frCohabitText(it){
  const c=it.cohabit_level;if(!c)return "";
  const parts=[String(c.value)];
  if(c.reached)parts.push(`达「${c.reached}」`);
  if(c.next)parts.push(`距「${c.next}」还差 ${c.gap}`);
  return parts.join(" · ");
}
/* 2026-11-01：卖点标签（value_word_ids → fashion_value_word_data，26 个标签）*/
function frValueWords(it){
  const vw=(it.value_words||[]);
  if(!vw.length)return "";
  return vw.map(x=>x.text).filter(Boolean).join(" / ");
}
function frValueWordsTitle(it){
  const vw=(it.value_words||[]);
  if(!vw.length)return "";
  return vw.map(x=>`${x.text}：${x.long_text||""}`).join("\n");
}
/* 审计键值对：D2 灯箱/停靠栏「技术详情」区专用（网格卡面不再渲染） */
function frKvHtml(it){
  const mid=(it.model_id!=null)?it.model_id:((it.model_ids&&it.model_ids[0])!=null?it.model_ids[0]:null);
  const refs=(it.model_refs||[]).filter(x=>x!=null&&String(x)!==String(mid));
  const durCn=it.duration_state==="unknown"?"期限未知":(it.duration_state==="timed"?"限时":(it.duration_state==="mixed"?"永久+限时":"永久"));
  const durDays=(it.durations||[]).length?`（${it.durations.join("/")}天）`:"";
  const pairs=[];
  if(it.grade_level!=null)pairs.push(["品级",(it.grade_levels&&it.grade_levels.length>1?it.grade_levels.map(gradeLabel).join("/")+"（取最高）":"品级 "+gradeLabel(it.grade_level))]);
  if(it.charm_value!=null)pairs.push(["魅力值",String(it.charm_value)+(it.charm_note?(" · "+String(it.charm_note).split("（")[0]):"")]);
  if(it.equip_charm!=null)pairs.push(["魅力值（装备表）",String(it.equip_charm)+(it.equip_level!=null?" · 装备品级 "+it.equip_level:"")]);
  if((it.charm_candidates||[]).length)pairs.push(["魅力值候选",it.charm_candidates.join(" / ")+"（同一卡各款式行取值不一致，当前取主行，待核对）"]);
  if((it.equip_charm_candidates||[]).length)pairs.push(["魅力值候选",it.equip_charm_candidates.join(" / ")+"（同名装备行取值不一致，待核对）"]);
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
  if(it.show_no_have===true)bools.push("未拥有也展示");
  if(it.show_no_have===false)bools.push("不拥有就不显示");
  if(it.hide_in_bag)bools.push("背包内隐藏");
  if(it.glowstick_switchable)bools.push("荧光棒可切换");
  if(it.hide_idle_anim)bools.push("展示动作可关");
  if(bools.length)pairs.push(["展示开关",bools.join(" / ")]);
  /* 2026-11-01 用户点名补的维度：藏花 / 遮挡与再生者可见 / 分版描述 / 其它小参 */
  if(it.flower_bud)pairs.push(["换花",frFlowerText(it)+(it.flower_bud.appear_ids?`（花部行 ${it.flower_bud.appear_ids.join(" / ")}）`:"")+
    (it.flower_bud.reborn_socket?` · ${it.flower_bud.reborn_socket.only_reborn?"仅再生者挂载":"常规挂载"}`:"")]);
  if(it.reborn_vis!=null)pairs.push(["藏花",it.reborn_vis?"是 · reborn_vis=1":"否"]);
  if(it.desc_man)pairs.push(["男版描述",it.desc_man]);
  if(it.name_man||it.name_female)pairs.push(["分版命名",
    `女版 ${it.name_female||"—"} / 男版 ${it.name_man||"—"}`]);
  if(it.brand_id!=null)pairs.push(["品牌编号",String(it.brand_id)]);
  if((it.suit_buff_ids||[]).length)pairs.push(["套装 buff",it.suit_buff_ids.join(" / ")]);
  if((it.mutex_modules||[]).length)pairs.push(["互斥模块",it.mutex_modules.join(" / ")]);
  if(it.takeoff_head)pairs.push(["可脱帽","是"]);
  if(it.not_show_rebirth_makeup)pairs.push(["不显示再生妆容","是"]);
  if((it.special_idle_anims||[]).length)pairs.push(["展示动作",it.special_idle_anims.join(" / ")]);
  if(it.fashion_action_id!=null)pairs.push(["专属动作",String(it.fashion_action_id)]);
  /* 2026-11-01 用户点选的染色/获取/展示组 */
  if(it.dye)pairs.push(["染色方案",frDyeText(it)+(it.dye.appear_ids?` · 外观染色 ${it.dye.appear_ids.join(" / ")}`:"")+(it.dye.appear_sockets?` · 插槽 ${it.dye.appear_sockets.join(" / ")}`:"")]);
  if((it.dye&&(it.dye.hair||[]).length))pairs.push(["发色方案",frHairDyeText(it)]);
  if((it.model_change_color_id||[]).length)pairs.push(["默认配色 id",it.model_change_color_id.join(" / ")]);
  if(it.obtain_res)pairs.push(["获取途径",it.obtain_res]);
  if(it.theme)pairs.push(["套装主题",it.theme.name+(it.theme.open_time?` · 开放 ${it.theme.open_time}`:"")]);
  if(it.show_start)pairs.push(["上架时间",it.show_start]);
  if((it.gift_package||[]).length)pairs.push(["礼包 id",it.gift_package.join(" / ")]);
  if((it.display_bg||[]).length)pairs.push(["展示背景",it.display_bg.map(b=>`${b.img||("bg"+b.id)}${b.scn?" · "+b.scn:""}`).join(" ｜ ")]);
  if(it.anim_graph)pairs.push(["专属动作图",[it.anim_graph.anim?`动作 ${it.anim_graph.anim}`:"",it.anim_graph.ui?`UI ${it.anim_graph.ui}`:""].filter(Boolean).join(" · ")]);
  if((it.value_words||[]).length)pairs.push(["卖点标签",frValueWords(it)]);
  if(it.rebirth_tex)pairs.push(["再生形态贴图","是（背包专属贴图）"]);
  if((it.other_get_methods||[]).length)pairs.push(["其他获取方式",it.other_get_methods.map(m=>`${m.title?m.title+"：":""}${m.desc}`).join(" ｜ ")]);
  if(it.uncap_appear_gender)pairs.push(["未解锁外观",`版本 ${(it.uncap_appear_gender.values||[]).join(" / ")} · ${it.uncap_appear_gender.note||""}`]);
  if(it.bone_info)pairs.push(["新骨骼",`是${(it.bone_info.soft_bone_ids||[]).length?" · 软骨骼 "+(it.bone_info.soft_bone_ids||[]).join(" / "):""}`]);
  if(it.green_model)pairs.push(["风底形态模型",[...(it.green_model.female||[]),...(it.green_model.female_high||[])].join(" / ")||"—"]);
  if((it.preview_group||[]).length)pairs.push(["专属预览",it.preview_group.map(g=>`组 ${g.group}${(g.tags||[]).length?" · "+(g.tags||[]).join(" / "):""}${(g.anims||[]).length?" · "+(g.anims||[]).join(" / "):""}`).join(" ｜ ")]);
  if(it.model_paths){
    const mp=it.model_paths;
    pairs.push(["模型路径",[...(mp.model||[]).map(x=>"主体 "+x),...(mp.high||[]).map(x=>"高模 "+x),...(mp.body||[]).map(x=>"身体 "+x),...(mp.socket||[]).map(x=>"挂点 "+x),...(mp.v2_socket||[]).map(x=>"v2挂点 "+x)].join(" ｜ ")]);
  }
  if(it.npc_hidden)pairs.push(["NPC 展示","不在 NPC/怪物身上出现"]);
  if(it.cohabit_level)pairs.push(["friendliness 分值",frCohabitText(it)+"（按部位固定：背包1960/衣服1280/头饰680，与魅力值无关；语义待核）"]);
  if(it.part_code!=null)pairs.push(["内部部位码",`${it.part_code} · ${it.part_code_cn||"—"}（部位判定唯一口径）`]);
  if(it.show_name&&it.show_name!==it.name)pairs.push(["游戏内显示名",it.show_name]);
  if(it.man_show_name)pairs.push(["男版显示名",it.man_show_name]);
  if(it.show_schedule)pairs.push(["上架/可见时间",Object.entries(it.show_schedule).map(([k,v])=>`${k} ${Array.isArray(v)?v.join(" / "):v}`).join(" ｜ ")]);
  if(it.misc_flags){
    const mf=it.misc_flags;
    const MFLAB={"gift_package_present_times_limit":"礼包次数上限","bag_fake_entryword":"背包假词条","zhexing_type":"折星型",
      "training_rank_season_id":"训练赛赛季","special_fixed_attr_ids":"固定属性","hide_part":"隐藏部件",
      "team_match_bg_conf":"组队背景配置","hd_run_replace_anim":"疾跑替换动作","flowing_light_group_id":"流光组",
      "dynamic_macro_name":"动态宏","tex_compress_type":"贴图压缩","model_socket":"模型挂点",
      "max_stack_num":"最大堆叠","obtain_notify":"获取通知"};
    for(const [k,v] of Object.entries(mf))pairs.push([MFLAB[k]||k,Array.isArray(v)?v.join(" / "):String(v)]);
  }
  if(it.tech_flags){
    const tf=it.tech_flags;
    const TFLAB={"socket_names_female":"女版挂点名","socket_names_male":"男版挂点名","soft_bone_ids_female":"女版软骨骼",
      "soft_bone_ids_male":"男版软骨骼","v2_socket_names":"v2 挂点名","v2_soft_bone_id":"v2 软骨骼",
      "link_socket_names":"联动挂点名","link_softbone_ids":"联动软骨骼","body_soft_bone_id":"身体软骨骼",
      "action_disable_soft_bone":"动作禁用软骨骼","dynamic_socket_names_female":"女版动态挂点",
      "dynamic_socket_names_male":"男版动态挂点","socket_names_dont_load_in_cine":"剧场不加载挂点",
      "anim_graph_id_unlink":"解链动作图","hide_in_bag":"背包内隐藏"};
    for(const [k,v] of Object.entries(tf)){ if(TFLAB[k])pairs.push([TFLAB[k],Array.isArray(v)?v.join(" / "):String(v)]); }
    if(tf.socket_model_use_high_model)pairs.push(["挂点用高模","是（纯技术）"]);
    if((tf.forbid_primary_high_model||[]).length)pairs.push(["禁用主高模",tf.forbid_primary_high_model.join(" / ")+"（纯技术）"]);
    if((tf.theme_codes||[]).length)pairs.push(["主题码",tf.theme_codes.join(" / ")+"（全库仅此一值）"]);
    if(tf.is_slim_bag)pairs.push(["精简外观","是（实测：所有衣服/头饰/套装恒 1，与背包无关）"]);
    if((tf.faked_times_limit||[]).length)pairs.push(["时限次数上限",tf.faked_times_limit.join(" / ")+"（实测恒 1，与时限无关）"]);
    if((tf.valid_scene_ids||[]).length)pairs.push(["限定场景",tf.valid_scene_ids.join(" / ")+"（全库仅 4 行）"]);
  }
  if(it.point_light_id!=null)pairs.push(["光源预设",String(it.point_light_id)]);
  if(it.foreign_name)pairs.push(["外文名",it.foreign_name]);
  if(it.is_2025||it.is_climb_tower)pairs.push(["活动标签",
    [it.is_2025?"2025 款":null,it.is_climb_tower?"爬塔款":null].filter(Boolean).join(" / ")]);
  if(it.new_fashion_id_str)pairs.push(["部位代码",it.new_fashion_id_str]);
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
  const fdesc=(it.desc||it.desc_note||it.desc_man||it.flower_bud||it.effect_text||it.charm_note||it.reborn_vis!=null||it.back_weapon_vis!=null||(it.hide_parts||[]).length||it.gender||it.gender_scope||it.dye||it.obtain_res||it.theme||it.show_start||(it.value_words||[]).length||(it.other_get_methods||[]).length||it.uncap_appear_gender||it.rebirth_tex||(it.preview_group||[]).length||it.cohabit_level||it.part_code!=null||it.model_paths||it.npc_hidden||it.model_note||it.equip_charm!=null||(it.durations&&it.durations.length))
    ?`<details class="fdesc"${FD_OPEN_ALL?" open":""}><summary>详情</summary><div class="fdesc-body">${
        ((it.vehicle_ids||[]).length>1?`<div class="fd-row"><span class="fd-k">全部编号</span><span class="fd-v mono">${it.vehicle_ids.join(" / ")}</span></div>`:"")+
        (it.gender?`<div class="fd-row"><span class="fd-k">性别</span><span class="fd-v">${esc(it.gender)}${it.gender_scope?` · <b>${esc(it.gender_scope)}</b>`:""}</span></div>`:"")+
        (it.gender_scope_note?`<div class="fd-row"><span class="fd-k">性别说明</span><span class="fd-v">${esc(it.gender_scope_note)}</span></div>`:"")+
        (it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${richText(it.desc)}</span></div>`:"")+
        (it.desc_note&&!it.desc?`<div class="fd-row"><span class="fd-k">描述</span><span class="fd-v">${esc(it.desc_note)}</span></div>`:"")+
        (it.effect_text?`<div class="fd-row"><span class="fd-k">效果</span><span class="fd-v">${esc(it.effect_text)}</span></div>`:"")+
        (it.effect_text?`<div class="fd-row"><span class="fd-k">效果来源</span><span class="fd-v mono">${esc(it.effect_source||"—")}</span></div>`:"")+
        (it.charm_note?`<div class="fd-row"><span class="fd-k">魅力值</span><span class="fd-v">${it.charm_value!=null?esc(it.charm_value)+" · ":""}${esc(it.charm_note)}${(it.charm_candidates||[]).length?`<br><span style="opacity:.75">各款式行取值：${esc(it.charm_candidates.join(" / "))}（当前取主行，待核对）</span>`:""}</span></div>`:"")+
        (it.equip_charm!=null?`<div class="fd-row"><span class="fd-k">魅力值</span><span class="fd-v">${esc(it.equip_charm)}${it.equip_level!=null?` · 装备品级 ${esc(it.equip_level)}`:""}<br><span style="opacity:.75">来源：all_equips_data（装备表）· ${esc(it.equip_charm_source||"")}</span></span></div>`:"")+
        (it.reborn_vis!=null?`<div class="fd-row"><span class="fd-k">藏花</span><span class="fd-v">${it.reborn_vis?"是 · <span class=\"mono\">reborn_vis=1</span>":"否"}</span></div>`:"")+
        (it.flower_bud?`<div class="fd-row"><span class="fd-k">换花</span><span class="fd-v">${esc(frFlowerText(it))}${it.flower_bud.reborn_socket?`<br><span class="mono" style="opacity:.75">挂点 ${esc(it.flower_bud.reborn_socket.socket||"flower")} · ${it.flower_bud.reborn_socket.only_reborn?"仅再生者形态挂载":"常规挂载"}${(it.flower_bud.reborn_socket.models||[]).length?" · "+esc(it.flower_bud.reborn_socket.models[0]):""}</span>`:""}</span></div>`:"")+
        (it.dye?`<div class="fd-row"><span class="fd-k">染色方案</span><span class="fd-v">${esc(frDyeText(it))}${frDyeSwatches(it)}${(it.dye.hair||[]).length?`<br><span class="mono" style="opacity:.75">发色 ${esc(frHairDyeText(it))}</span>`:""}</span></div>`:"")+
        (it.obtain_res?`<div class="fd-row"><span class="fd-k">获取途径</span><span class="fd-v">${esc(it.obtain_res)}</span></div>`:"")+
        (it.theme?`<div class="fd-row"><span class="fd-k">套装主题</span><span class="fd-v">${esc(it.theme.name)}${it.theme.open_time?` · <span class="mono">开放 ${esc(it.theme.open_time)}</span>`:""}</span></div>`:"")+
        (it.show_start?`<div class="fd-row"><span class="fd-k">上架时间</span><span class="fd-v">${esc(it.show_start)}</span></div>`:"")+
        ((it.value_words||[]).length?`<div class="fd-row"><span class="fd-k">卖点标签</span><span class="fd-v">${esc(frValueWords(it))}</span></div>`:"")+
        ((it.other_get_methods||[]).length?`<div class="fd-row"><span class="fd-k">其他获取方式</span><span class="fd-v">${esc(it.other_get_methods.map(m=>`${m.title?m.title+"：":""}${m.desc}`).join(" ｜ "))}</span></div>`:"")+
        (it.uncap_appear_gender?`<div class="fd-row"><span class="fd-k">未解锁外观</span><span class="fd-v">版本 ${esc((it.uncap_appear_gender.values||[]).join(" / "))}<br><span style="opacity:.75">${esc(it.uncap_appear_gender.note||"")}</span></span></div>`:"")+
        (it.rebirth_tex?`<div class="fd-row"><span class="fd-k">再生形态贴图</span><span class="fd-v">是（背包专属贴图）</span></div>`:"")+
        ((it.preview_group||[]).length?`<div class="fd-row"><span class="fd-k">专属预览</span><span class="fd-v">${esc(it.preview_group.map(g=>`组 ${g.group}${(g.tags||[]).length?" · "+(g.tags||[]).join(" / "):""}${(g.anims||[]).length?" · "+(g.anims||[]).join(" / "):""}`).join(" ｜ "))}</span></div>`:"")+
        (it.model_paths?`<div class="fd-row"><span class="fd-k">模型路径</span><span class="fd-v mono">${esc([...(it.model_paths.model||[]).map(x=>"主体 "+x),...(it.model_paths.high||[]).map(x=>"高模 "+x),...(it.model_paths.body||[]).map(x=>"身体 "+x),...(it.model_paths.socket||[]).map(x=>"挂点 "+x),...(it.model_paths.v2_socket||[]).map(x=>"v2挂点 "+x)].join(" ｜ "))}</span></div>`:"")+
        (it.model_note?`<div class="fd-row"><span class="fd-k">模型说明</span><span class="fd-v">${esc(it.model_note)}</span></div>`:"")+
        (it.npc_hidden?`<div class="fd-row"><span class="fd-k">NPC 展示</span><span class="fd-v">不在 NPC/怪物身上出现</span></div>`:"")+
        
        (it.part_code!=null?`<div class="fd-row"><span class="fd-k">内部部位码</span><span class="fd-v"><span class="mono">${it.part_code}</span> · ${esc(it.part_code_cn||"")}（部位判定唯一口径）</span></div>`:"")+
        (it.show_name&&it.show_name!==it.name?`<div class="fd-row"><span class="fd-k">游戏内显示名</span><span class="fd-v">${esc(it.show_name)}</span></div>`:"")+
        
        (it.show_no_have!=null?`<div class="fd-row"><span class="fd-k">未拥有时</span><span class="fd-v">${it.show_no_have?"衣柜里也显示":"衣柜里不显示"}</span></div>`:"")+
        (it.desc_man?`<div class="fd-row"><span class="fd-k">男版描述</span><span class="fd-v">${richText(it.desc_man)}</span></div>`:"")+
        ((it.name_man||it.name_female)?`<div class="fd-row"><span class="fd-k">分版命名</span><span class="fd-v">女版 ${esc(it.name_female||"—")} / 男版 ${esc(it.name_man||"—")}</span></div>`:"")+
        ((it.hide_parts||[]).map(x=>`<div class="fd-row"><span class="fd-k">隐藏${esc(x)}</span><span class="fd-v">是</span></div>`).join(""))+
        (it.back_weapon_vis!=null?`<div class="fd-row"><span class="fd-k">隐藏副武器</span><span class="fd-v">${it.back_weapon_vis?"是":"否"}</span></div>`:"")
      }</div></details>`:"";
  /* 同 model：与「同系列图」同级、放在它上面 */
  const sibs=(function(){
    const m=(it.model_id!=null)?String(it.model_id):null;
    const g=m&&window.FR_MODEL_INDEX&&window.FR_MODEL_INDEX[m];
    if(!g||g.length<2)return [];
    return g.filter(x=>String(x.id)!==String(it.id));
  })();
  const sibHtml=sibs.length?`<details class="tech fr-sibbox"><summary>同 model ${sibs.length+1}</summary><div class="fr-sibs-grid">${
    sibs.map(function(x){
      const _im=(window.FR_IMGS&&window.FR_IMGS[String(x.id)])||[];
      const _src=(_im.length?_im[0]:(x.png||""));
      const _pg=(x.grade!=null?(" · 品级"+x.grade):"");
      return `<a class="fr-sib-card" href="#" data-sib-id="${esc(String(x.id))}" data-sib-from="${esc(String(it.id))}" title="${esc(x.name)}">`+
        (_src?`<img src="${esc(_src)}" alt="" loading="lazy">`:`<span class="noimg">无图</span>`)+
        `<div class="n">${esc(x.name)}</div><div class="p">${esc(x.part||"")}${esc(_pg)}</div></a>`;
    }).join("")
  }</div></details>`:"";
  const art=((it._media||{}).art)||[];
  const artHtml=art.length?`<details class="tech fr-artbox"><summary>同系列图 ${art.length}</summary><div class="fr-art">${
    art.map(a=>`<a href="${esc(a.png)}" target="_blank" rel="noopener" title="${esc(a.family||"")} · ${esc(a.source||"")}"><img src="${esc(a.png)}" alt="${esc(a.label||a.family||"")}" loading="lazy"><span>${esc(a.label||a.family||"")}</span></a>`).join("")
  }</div></details>`:"";
  return fdesc+sibHtml+artHtml+`<details class="tech"><summary>技术详情 / 数据来源 / 审计信息</summary><div class="fr-kv">${kv}</div></details>`;
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
if(SCENE_TABLE)document.body.classList.add("scene-mode","sbt-mode");
const PIECEWISE=(function(){try{return (getParam("b")||"")==="damage_bonus_piecewise";}catch(e){return false;}})();
if(PIECEWISE)document.body.classList.add("pw-mode");
/* 服务器类型（board id = server_types）：与场景平衡同款表格视图。
   本板只有 21 条、字段全是「后缀 / 标签 / 表数 / 判定依据 / 状态」这类结构化事实，
   卡片化会把它们压成看不清的长文本 ⇒ 走 sbt 表格（可点表头排序）。
   ★ sbt-mode 是表格外观的公共开关（样式见 board_base.css），scene-mode 只保留场景专属微调。 */
const ST_TABLE=(function(){try{return (getParam("b")||"")==="server_types";}catch(e){return false;}})();
if(ST_TABLE)document.body.classList.add("st-mode","sbt-mode");
/* 影音资源板（2026-11-02）：自助渲染 —— 左侧分类树 + 常驻播放器 + 可整组入队的队列。
   数据：data/boards/media_catalog.js（全量音频样本名 + 还原树视频清单）。 */
const MEDIA_BOARD=(function(){try{return (getParam("b")||"")==="media_catalog";}catch(e){return false;}})();
/* ── 可切换展示视图（?view=xxx）────────────────────────────────────────
   CDN 资源库 cdn_library：group（默认，目录组折叠 + 体积条）/ table（全量表格）
   本地还原树 local_restore_tree：index（默认，聚合概览 + 模块双列）/ dash（仅聚合概览）
   ★ 全部视图只用板内既有字段，不引入任何推断值；
     唯一的派生量（体积条宽度、占比、聚合计数）都由字段直接算出。
   ★ 2026-11-01 用户定稿：CDN 走「目录组折叠 + 体积条」，明细表在组内展开；
     还原树走「聚合概览 + 模块双列索引」（按文件名首段分模块，
     因为 .nxs 与 _chs.py 强配对、全局双列会 27774 : 5827 失衡）。 */
const CDN_BOARD=(function(){try{return (getParam("b")||"")==="cdn_library";}catch(e){return false;}})();
const TREE_BOARD=(function(){try{return (getParam("b")||"")==="local_restore_tree";}catch(e){return false;}})();
let VIEW=(function(){try{return (getParam("view")||"").toLowerCase();}catch(e){return "";}})();
if(CDN_BOARD||TREE_BOARD)document.body.classList.add("view-mode");
/* 当前视图名（各板默认值不同，非法值回退到默认视图） */
function curView(){
  const def=CDN_BOARD?"group":"index";
  const allow=CDN_BOARD?["group","table"]:["index","dash"];
  return allow.indexOf(VIEW)>=0?VIEW:def;
}
/* 视图切换：写入 URL 并重绘（可分享、可回退） */
function setView(v){
  VIEW=v;
  try{
    const u=new URLSearchParams(location.search);
    u.set("view",v);
    history.replaceState(null,"",location.pathname+"?"+u.toString());
  }catch(e){}
  /* 同步按钮高亮（切换器可能还没建好，故做空值保护） */
  try{
    const n=document.getElementById("viewSwitch");
    if(n)for(const btn of n.querySelectorAll(".viewsw-btn")){
      const on=btn.dataset.view===v;
      btn.classList.toggle("on",on);
      btn.setAttribute("aria-pressed",String(on));
    }
  }catch(e){}
  render();
}
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
          (it.charm_note?`<div class="fd-row"><span class="fd-k">魅力值</span><span class="fd-v">${it.charm_value!=null?esc(it.charm_value)+" · ":""}${esc(it.charm_note)}${(it.charm_candidates||[]).length?`<br><span style="opacity:.75">各款式行取值：${esc(it.charm_candidates.join(" / "))}（当前取主行，待核对）</span>`:""}</span></div>`:"")+
          (it.reborn_vis!=null?`<div class="fd-row"><span class="fd-k">藏花</span><span class="fd-v">${it.reborn_vis?"是":"否"}</span></div>`:"")+
          (it.obtain_res?`<div class="fd-row"><span class="fd-k">获取途径</span><span class="fd-v">${esc(it.obtain_res)}</span></div>`:"")+
          (it.theme?`<div class="fd-row"><span class="fd-k">套装主题</span><span class="fd-v">${esc(it.theme.name)}</span></div>`:"")+
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
/* 称号板（title_catalog，2026-11-01）：1539 条平铺太散，按「获取途径」分组。
   唯一可直译的结构化轴是源表 title_conf_data.quest（板上字段 obtain）；
   style 是等级档位（初/中/高级/资深…），不是分类，因此不参与分组。
   中文标签按各行 desc 实证归纳，不做跨表推断。 */
const TITLE_BOARD=(function(){try{return (getParam("b")||"")==="title_catalog";}catch(e){return false;}})();
/* 活动总表（activity_master，2026-11-02）：3519 条且无一张配图。
   按月份折叠为台账：状态概览 + 月份分组 + 紧凑行；仅本板生效。 */
const ACTIVITY_BOARD=(function(){try{return (getParam("b")||"")==="activity_master";}catch(e){return false;}})();
/* 料理与食谱板（edible_catalog，2026-11-02）：料理为主表，食材默认折叠为次级分组。
   折叠只影响可见范围，仍可勾选展开、仍可被类型筛选命中（不影响其它板）。 */
const EDIBLE_BOARD=(function(){try{return (getParam("b")||"")==="edible_catalog";}catch(e){return false;}})();
let edibleShowIngredients=false;
/* 头像 / 头像框 / 名片框板（avatar_catalog，2026-11-01）：三类混排，
   排序轴只有「标号」（item_id）。先按类型分组（头像 → 头像框 → 名片框），
   组内按标号排；默认大 → 小（新出的编号在前），可切小 → 大。 */
const AVATAR_BOARD=(function(){try{return (getParam("b")||"")==="avatar_catalog";}catch(e){return false;}})();
const AVATAR_KIND_ORD={"头像":0,"头像框":1,"名片框":2};
function avatarSort(a,b,sign){
  const ka=AVATAR_KIND_ORD[a.kind]!=null?AVATAR_KIND_ORD[a.kind]:9;
  const kb=AVATAR_KIND_ORD[b.kind]!=null?AVATAR_KIND_ORD[b.kind]:9;
  if(ka!==kb)return ka-kb;
  const na=Number(a.item_id),nb=Number(b.item_id);
  const va=Number.isFinite(na)?na:null, vb=Number.isFinite(nb)?nb:null;
  if(va!==null&&vb!==null&&va!==vb)return sign*(va-vb);   // 标号缺省（非数字）固定排最后
  if(va===null&&vb!==null)return 1;
  if(vb===null&&va!==null)return -1;
  return String(a.item_id||"").localeCompare(String(b.item_id||""));
}
/* 分组开关（2026-11-01）：默认平铺、整表按编号排；勾选后才按获取途径分组 */
let titleGroupOn=false;
const TITLE_GROUPS=[
  ["SpecProfLevel","职业认证"],
  ["ProfLevel","生存等级"],
  ["ItemGain","活动 / 物品获取"],
  ["ValentineDayTitleQuest","社区活动（情人节）"],
  ["Mayor","营地市长"],
  ["Dominate","地图占领"],
  ["PVERanking","排行榜"],
  ["SuperMem","网易会员"],
  ["WestWorldHonor","红杉镇势力"],
  ["ExploreFinish","地图探索"],
  [null,"未登记获取条件"],
];
function titleGroupKey(it){return String((it&&it.obtain)||"")||null;}
function titleGroupLabel(v){const hit=TITLE_GROUPS.find(g=>g[0]===v);return hit?hit[1]:"其他";}
function titleGroupOrder(v){const i=TITLE_GROUPS.findIndex(g=>g[0]===v);return i<0?TITLE_GROUPS.length-1:i;}
/* 称号属性小标：档位(style)、颜色(style 对应贴图)、特性(动态/美术字)。
   数据由 build_text_boards.py 从 title_conf_data 的 style / shining_style / style_icon 直读，
   前端只负责显示，不做二次推断。 */
function titleBadges(it){
  const out=[];
  if(it.color)out.push(`<span class="tb tb-c" data-c="${esc(it.color)}">${esc(it.color)}色</span>`);
  if(it.style)out.push(`<span class="tb tb-lv" title="源表 style 档位">档位 ${esc(it.style)}</span>`);
  (Array.isArray(it.flags)?it.flags:[]).forEach(f=>out.push(`<span class="tb tb-f">${esc(f)}</span>`));
  return out.length?`<div class="i-badges">${out.join("")}</div>`:"";
}
/* 称号视觉层：档位色贴图 + 美术字图（全部是真实资源导出，不画仿制）。
   贴图命名与来源见 web/tools/build_title_art_assets.py：
     line_N = 称号名下划线（1 蓝 / 2 紫 / 3 金 / 8 绿）
     bg_N   = 称号名底光（2 紫 / 3 金 / 4 红）
   红/蓝/绿没有对应 bg，紫/金没有双向缺失，因此按「有就叠、没有就只画一条」。 */
const TITLE_SKIN_BG={紫:"bg_2",金:"bg_3",红:"bg_4"};
const TITLE_SKIN_LINE={蓝:"line_1",紫:"line_2",金:"line_3",绿:"line_8"};
/* 称号文字颜色 + 描边：全部取自游戏原生贴图的实测像素（_probe_skin_colors.py）——
   线框贴图 img_chenghao_line_N 是 31x6 的小条，结构固定为「外圈深色描边 + 内芯横向渐变」，
   正好就是游戏里称号文字的「填充渐变 + 描边色」：
     line_1 蓝 芯 #7EA7AF→#AAE4E4 描边 #283249
     line_2 紫 芯 #A471A4→#CAA8DB 描边 #49283C
     line_3 金 芯 #BE9D5B→#F1CF7A 描边 #473625
     line_8 绿 芯 #87A85E→#C3E590 描边 #483726
   红没有线框贴图，只有 bg_4 光晕（芯 #E84F1C→#FF5522），描边按同一条「深色外圈」规则取暗红。
   5/6/7 档源表无对应贴图（颜色字段留空），照旧不上色、不叠贴图。 */
const TITLE_SKIN_TXT={
  蓝:["#7EA7AF","#AAE4E4","#283249"],
  紫:["#A471A4","#CAA8DB","#49283C"],
  金:["#BE9D5B","#F1CF7A","#473625"],
  红:["#E84F1C","#FF5522","#4A1B10"],
  绿:["#87A85E","#C3E590","#483726"]
};
/* 底光 / 下划线：锚在「称号名文字自身」的盒子上（.i-title = inline-block 收缩到文字宽），
   底光以文字中心为圆心按贴图原生比例 235:62 缩放，下划线贴住文字底边；
   不再用 import 时猜的 top/left 像素偏移，换字号/换列宽都不会错位。 */
function titleSkin(it){
  const c=String(it.color||"");
  const bg=TITLE_SKIN_BG[c];
  if(!bg)return "";
  return `<i class="sk-bg" aria-hidden="true" style="background-image:url('assets/title_skin/${bg}.png')"></i>`;
}
function titleLine(it){
  const c=String(it.color||"");
  const ln=TITLE_SKIN_LINE[c];
  if(!ln)return "";
  return `<i class="sk-ln" aria-hidden="true" style="background-image:url('assets/title_skin/${ln}.png')"></i>`;
}
/* 特殊装饰（title_conf_data.special_style）：love/star/cake 各有一枚小徽标贴图，
   取自还原树 ui/chenghao_icon/img_chenghao_<x>_3.png，贴在称号文字左侧。
   sun 在源表里没有对应贴图，按「取不到就不画」跳过。 */
const TITLE_SPECIAL={love:"love_3",star:"star_3",cake:"cake_3"};
function titleSpecial(it){
  const f=TITLE_SPECIAL[String(it.special_style||"")];
  return f?`<img class="i-sp" src="assets/title_skin/${f}.png" alt="">`:"";
}
/* 美术字 + 底图：游戏里这是一枚「称号图」的两层 —— 动态 csb 的底图/光效在下，
   美术字叠在上面（同一张图内叠加），不是上下两张分开排。
   · art_png 由 build_title_art_assets.py 只对「导出成功」的条目回填，不会 404；
   · 底图取 dyn_webp（逐帧动画，作为背景层）→ dyn_png（首帧）；
   · dyn_has_text：底图贴图本身已经把称号字画进去了（如 1214 骑士集结 的 vx 贴图），
     此时只显示底图，避免和美术字叠成重影。该标记来自资源实测，不是猜的。
   · 文字仍保留在 DOM（has-art 时隐藏），搜索/冒烟取文本不受影响。 */
function titleName(it){
  const nm=esc(it.name||it.display_name||it.id);
  const art=it.art_png,bg=it.dyn_webp||it.dyn_png;
  /* 2026-11-06 去重影：同一称号只画「一次」图像，优先级
     dyn(自带文字) > art_png > 底图柔光 > 纯文字
     · dyn_has_text：底图贴图本身已经把称号字画好了 → 只画底图（i-logo-solo），
       文字节点留在 DOM 里、由 has-art 规则视觉隐藏；
     · 同时有 art 和底图：art 是唯一的称号图像，底图退成背后一层
       放大 + 半透明的「柔光」（i-logo-glow）。绝不再让两层同尺寸同位置叠在一起 ——
       那正是重影的来源（同一份称号字被画两遍）；
     · 只有底图：底图当底板（i-logo-bg），文字压在上面。 */
  const txtNode=`<span class="i-name-txt">${nm}</span>`;
  if(bg&&it.dyn_has_text)
    return `<span class="i-title has-art"><img class="i-logo-solo" src="${esc(bg)}" alt="">${txtNode}</span>`;
  if(art){
    const inner=`<img class="i-art" src="${esc(art)}" alt="">${txtNode}`;
    if(bg)
      return `<span class="i-logo"><i class="i-logo-glow" aria-hidden="true" style="background-image:url('${esc(bg)}')"></i>${inner}</span>`;
    return `<span class="i-title has-art">${inner}</span>`;
  }
  const c=String(it.color||"");
  const t=TITLE_SKIN_TXT[c];
  /* 金色档自带自发光（游戏内金字外圈有暖金光晕），其余档位只上渐变色 + 描边。
     发光必须只作用在文字本身：文字单独包一层 .i-nm，避免 filter 波及底光/下划线/装饰图。 */
  const glow=c==="金";
  const sp=titleSpecial(it);
  const nmTxt=t?`<span class="i-nm">${nm}</span>`:nm;
  /* 无美术字的动态称号：同样是「文字叠在动态底图上」——底图当背景层，文字在上层；
     此时不再叠档位光晕（底图就是背景），保留档位字色 + 描边。 */
  const txt=`<span class="i-title${t?" tinted":""}${glow?" glow":""}${sp?" has-sp":""}"${t?` style="--ta:${t[0]};--tb:${t[1]};--ts:${t[2]}"`:""}>`
    +(bg?"":titleSkin(it))+sp+nmTxt+(bg?"":titleLine(it))+`</span>`;
  return bg
    ?`<span class="i-logo"><i class="i-logo-bg" aria-hidden="true" style="background-image:url('${esc(bg)}')"></i>${txt}</span>`
    :txt;
}
/* 分组头吸顶要让开 .controls 粘性条（半透明底，透出会糊字）。
   只算「控件条自身高度」塞给 --tg-h；垂直位置在 CSS 里与 .controls 用同一个
   --top-h 表达式相加，这样 board_plugins 事后校准 --top-h 时两者一起走，不会错位。 */
function syncTitleHeadTop(){
  if(!TITLE_BOARD)return;
  const c=document.querySelector(".controls");if(!c)return;
  document.documentElement.style.setProperty("--tg-h",`${c.offsetHeight}px`);
}
window.addEventListener("resize",syncTitleHeadTop);
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

/* 2026-11-01：同 model 跳转（定义在作用域内，才能访问 C2 / c2Open / frCard） */
function _frEnsureChip(item){
  if(!item||!C2.chips)return -1;
  const idOf=(x)=>{try{return String(c2IdOf(x));}catch(e){return String(x&&x.id);}};
  let i=C2.chips.findIndex(x=>idOf(x)===String(item.id));
  if(i<0){
    C2.chips.push(item); i=C2.chips.length-1;
    try{ if(C2.html){C2.html[idOf(item)]=frCard(item,i);}
         if(C2.htmlFull){C2.htmlFull[idOf(item)]=frCard(item,i,true);} }catch(e){}
  }
  return i;
}
window.__frJumpSibling=function(fromId,toId){
  const byId=(window.FR_ITEM_BY_ID)||{};
  const fromItem=byId[String(fromId)]||null, toItem=byId[String(toId)]||null;
  const idOf=(x)=>{try{return String(c2IdOf(x));}catch(e){return String(x&&x.id);}};
  const fi=fromItem?_frEnsureChip(fromItem):C2.chips.findIndex(x=>idOf(x)===String(fromId));
  const ti=toItem?_frEnsureChip(toItem):C2.chips.findIndex(x=>idOf(x)===String(toId));
  if(ti<0)return false;
  /* 钉住当前卡：直接设状态，不走 c2TogglePin —— 它内部会 c2Close()（history.back），
     back 是异步的，会在下面 c2Open 之后才触发 popstate，把刚打开的详情又关掉。 */
  if(fi>=0 && fromItem && !(C2.pinned&&idOf(C2.pinned)===String(fromItem.id))){
    try{ C2.pinned=fromItem; C2.lvP=0; c2DockShow(); }catch(e){}
  }
  c2Open(ti);
  document.querySelectorAll('.fr-sib-card').forEach(el=>el.classList.remove('seen'));
  const el=document.querySelector('.fr-sib-card[data-sib-id="'+String(toId).replace(/"/g,'')+'"]');
  if(el)el.classList.add('seen');
  return true;
};
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
      (it.charm_value ? `<span class="fr-charm">魅力 ${esc(it.charm_value)}</span>` : "")+
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
    if(img.closest("[data-sib-id]"))return;     /* 同 model 卡片：点图=跳转该子卡，不开大图 */
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
/* 2026-11-02：装备属性板 D2 详情（三服总览 + 三张分服卡共用）——
   自建详情体（equipD2Body），字段默认全部可见，不再复用卡面折叠区。 */
const EQUIP_D2={
  idOf:it=>it.id,
  name:it=>it.name||it.display_name||it.id,
  body:equipD2Body,
  meta:it=>{
    const sb=it.server_branch||"";
    return (sb?`<span class="skin-tag">${esc(sb)}</span>`:"")+
      `<span class="c2-no">行键 ${esc(it.row_key??it.id)}</span>`;
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
  const card=e.target.closest(".chip-card,.fcard,.skin-card,.i.nucleus,.i.roster,.i.eqcard,.i.fcard.vcard");
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
/* ── 2、“伤害加成”的分段函数：自定义公式视图 ─────────────────────────
   不再用名册卡：结论卡 + 三服曲线列（每服一张竖表），公式等宽字体分行显示。 */
const PW_SRV=[["经典服","pw-s-classic"],["简单生存服","pw-s-survival"],["月卡服","pw-s-month"]];
const PW_CURVE=[["a_class","a_class"],["p2p","p2p"],["m2p","m2p"]];
const PW_COLOR={"经典服":"#6ea8ff","简单生存服":"#f0a35e","月卡服":"#b79bff"};
/* 结论卡的白话文案：不展示原始公式，只讲人话（原始数值仍可在“说明与依据”里查）。 */
const PW_TITLE_CN={
  pw01:"结论①：加成不是照搬，要分段折算",
  pw02:"结论②：6 条加成曲线 + 1 条攻击力曲线",
  pw03:"结论③：每条配置都有生效窗口",
  pw04:"结论④：三服结构相同、参数不同",
  pw05:"结论⑤：PvP 服差主要在两张图",
  pw06:"结论⑥：经典服内部也有多套分段",
  pw13:"数据来源与复跑方式"
};
const PW_NOTE_CN={
  pw01:"原始加成不是直接照搬：系统把它切成几段，每段按固定比例折算，拐点处接上，得到实际加成。",
  pw02:"一共 6 条按“原始加成率”计算的曲线（a_class、p2p、d2p、m2p、b_class、c_class），外加 1 条按“攻击力”计算的曲线（source_hurt）。",
  pw03:"每条配置只在一定窗口内生效（有下限、上限），另有一档 p2d 下限；同一场景可能有多个档位行，不能只取第一条。",
  pw04:"南希 803：经典服 K=1.6、简单生存服 K=1.0、月卡服 K=1.2，M 都是 0.6 —— 三服共用同一套结构，只是参数不同。",
  pw05:"PvP 的服差集中在南希市和红杉镇-全面战争：简单生存服把 a_class 压到约 10%，经典服仍保留 100% 或 5 段形态。",
  pw06:"经典服自己也有至少 4 套 a_class 分段，不能用一个固定系数代表整个服，必须看具体场景的专属行。"
};
function pwFmt(x,unit){
  if(x===Infinity)return "∞";
  const v=unit==="rate"?x*100:x;
  const r=Math.round(v*10)/10;
  return (Math.abs(r-Math.round(r))<1e-6?String(Math.round(r)):String(r))+(unit==="rate"?"%":"");
}
/* 把 [a,b] kx+o 的分段文本解析成数字段；兼容 y= / ∞ / ；| 分隔。 */
function pwParse(v){
  const out=[];
  for(const raw of String(v||"").split(/[|；;\n]/)){
    const seg=raw.trim();
    if(!seg||seg==="—"||seg==="-")continue;
    const m=seg.match(/^\[\s*([-+]?[0-9.]+)\s*,\s*([^\]]+?)\s*\]\s*(?:y\s*=)?\s*(?:([-+]?[0-9.]+)\s*x)?\s*(?:([-+]\s*[0-9.]+))?$/);
    if(!m)continue;
    const a=Number(m[1]);
    const bs=m[2].trim();
    const b=/∞|inf/i.test(bs)?Infinity:Number(bs);
    const k=m[3]===undefined?0:Number(m[3]);
    const o=m[4]===undefined?0:Number(String(m[4]).replace(/\s/g,""));
    if(!isFinite(a)||(b!==Infinity&&!isFinite(b)))continue;
    out.push({a,b,k,o});
  }
  return out;
}
/* 原始分段公式（默认折叠，只给需要核对的人看）。 */
function pwSegs(v){
  const s=String(v??"").trim();
  if(!s||s==="—"||s==="-")return "";
  return s.split(/\n|；|;|\|/).map(x=>x.trim()).filter(Boolean)
    .map(x=>`<span class="pw-seg">${esc(x)}</span>`).join("");
}
/* 分段 → 中文说明。unit=rate 用百分比（0.3=30%），unit=atk 用原数值。 */
function pwCnSegs(v,unit){
  const segs=pwParse(v).filter(s=>s.b===Infinity||s.b>s.a);
  if(!segs.length)return "";
  const f=x=>pwFmt(x,unit);
  const parts=[];
  segs.forEach((s,i)=>{
    const yAt=x=>s.k*x+s.o;
    if(i===0){
      if(Math.abs(s.k-1)<1e-9&&Math.abs(s.o)<1e-9){
        parts.push(s.b===Infinity?"全程 100% 计入（不压缩）":`${f(s.a)}~${f(s.b)}：全额计入`);
        return;
      }
      if(s.b===Infinity){
        parts.push(`全程每 1 点只按 ${f(s.k)} 计入`);
        return;
      }
      parts.push(`${f(s.a)}~${f(s.b)}：每 1 点只按 ${f(s.k)} 计入（到 ${f(s.b)} 时实际约 ${f(yAt(s.b))}）`);
      return;
    }
    if(s.b===Infinity){
      parts.push(Math.abs(s.k)<1e-9
        ? `超过 ${f(s.a)} 后封顶（实际约 ${f(yAt(s.a))}）`
        : `超过 ${f(s.a)} 后：每多 1 点只算 ${f(s.k)}`);
      return;
    }
    parts.push(`${f(s.a)}~${f(s.b)}：超出部分每 1 点只算 ${f(s.k)}（到 ${f(s.b)} 时实际约 ${f(yAt(s.b))}）`);
  });
  return parts.join("；")+"。";
}
/* 曲线图：横轴原始值，纵轴折算后实际值；虚线是“完全不压缩”参考。 */
function pwChart(title,series,opt){
  const unit=(opt&&opt.unit)==="atk"?"atk":"rate";
  const f=x=>pwFmt(x,unit);
  const valid=(series||[]).filter(s=>s.segs&&s.segs.length);
  if(!valid.length)return `<figure class="pw-fig"><figcaption><b>${esc(title)}</b></figcaption><div class="pw-empty">无数据</div></figure>`;
  let xmax=0;
  for(const s of valid)for(const g of s.segs)if(g.b!==Infinity)xmax=Math.max(xmax,g.b);
  xmax=Math.max(unit==="rate"?1.2:1,(xmax*1.2||1));
  xmax=Math.round(xmax*100)/100;
  const pts=valid.map(s=>{
    const arr=[];
    for(const g of s.segs){
      if(g.b!==Infinity&&g.b<=g.a)continue;
      const lo=Math.max(0,g.a),hi=Math.min(g.b===Infinity?xmax:g.b,xmax);
      if(hi<lo)continue;
      arr.push([lo,g.k*lo+g.o],[hi,g.k*hi+g.o]);
    }
    return arr;
  });
  let ymax=unit==="rate"?0.2:1;
  pts.forEach(a=>a.forEach(([x,y])=>{if(isFinite(y))ymax=Math.max(ymax,y);}));
  ymax=Math.max(ymax*1.12,unit==="rate"?0.4:2);
  const W=340,H=196,L=44,R=12,T=26,B=34,pwW=W-L-R,ph=H-T-B;
  const sx=x=>L+(x/xmax)*pwW, sy=y=>T+ph-(Math.max(0,Math.min(ymax,y))/ymax)*ph;
  const h=['<svg viewBox="0 0 '+W+' '+H+'" class="pw-chart" role="img" aria-label="'+esc(title)+'">'];
  for(let i=0;i<=4;i++){
    const xv=xmax*i/4,yv=ymax*i/4;
    h.push(`<line x1="${sx(xv).toFixed(1)}" y1="${T}" x2="${sx(xv).toFixed(1)}" y2="${T+ph}" class="grid"/>`);
    h.push(`<text x="${sx(xv).toFixed(1)}" y="${T+ph+15}" class="tick" text-anchor="middle">${f(xv)}</text>`);
    h.push(`<line x1="${L}" y1="${sy(yv).toFixed(1)}" x2="${L+pwW}" y2="${sy(yv).toFixed(1)}" class="grid"/>`);
    h.push(`<text x="${L-6}" y="${(sy(yv)+3.5).toFixed(1)}" class="tick" text-anchor="end">${f(yv)}</text>`);
  }
  h.push(`<line x1="${L}" y1="${T+ph}" x2="${L+pwW}" y2="${T+ph}" class="axis"/>`);
  h.push(`<line x1="${L}" y1="${T}" x2="${L}" y2="${T+ph}" class="axis"/>`);
  if(unit==="rate"){
    const lim=Math.min(xmax,ymax);
    h.push(`<line x1="${sx(0)}" y1="${sy(0)}" x2="${sx(lim)}" y2="${sy(lim)}" class="pw-ref"/>`);
    h.push(`<text x="${sx(lim)-4}" y="${sy(lim)-6}" class="pw-reflab" text-anchor="end">不压缩参考线</text>`);
  }
  valid.forEach((s,idx)=>{
    const color=opt&&opt.colors?opt.colors[idx]:"#8fa3b0";
    const d=pts[idx].map(([x,y])=>`${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join(" ");
    if(d)h.push(`<polyline points="${d}" fill="none" stroke="${color}" class="pw-line"/>`);
  });
  h.push(`<text x="${L+pwW/2}" y="${H-6}" class="pw-axlab" text-anchor="middle">${unit==="rate"?"原始加成率":"攻击力"}</text>`);
  h.push(`<text x="12" y="${T+ph/2}" class="pw-axlab" transform="rotate(-90 12 ${T+ph/2})">${unit==="rate"?"折算后实际加成":"折算后系数"}</text>`);
  h.push("</svg>");
  const lg=valid.map((s,i)=>`<span class="pw-lg"><i style="background:${opt&&opt.colors?opt.colors[i]:"#8fa3b0"}"></i>${esc(s.name)}</span>`).join("");
  return `<figure class="pw-fig"><figcaption><b>${esc(title)}</b>${lg}</figcaption>${h.join("")}</figure>`;
}
function pwCurveCN(label,formula,unit){
  return `<div class="pw-curve"><b>${esc(label)}</b><div class="pw-cn">${esc(pwCnSegs(formula,unit)||"—")}</div></div>`;
}
function pwNoteHTML(it){
  const det=[it["说明"],it["依据"]].filter(Boolean).map(x=>`<p>${esc(x)}</p>`).join("");
  return `<article class="pw-note${it.id==="pw13"?" pw-wide":""}">
    <div class="pw-note-hd"><span class="pw-id">${esc(it.id)}</span><h3>${esc(PW_TITLE_CN[it.id]||it.name)}</h3></div>
    <p class="pw-concl">${esc(PW_NOTE_CN[it.id]||it["结论"]||"")}</p>
    ${det?`<details class="pw-det"><summary>说明与依据</summary>${det}</details>`:""}
  </article>`;
}
function pwServerHTML(it){
  const srv=it["服型"]||"";
  const cls=(PW_SRV.find(x=>x[0]===srv)||[])[1]||"";
  const curves=(it.rate_curves||[]).map(c=>pwCurveCN(c.label,c.formula,"rate")).join("");
  const raw=(it.rate_curves||[]).map(c=>`<div class="pw-raw-row"><b>${esc(c.label)}</b><code>${pwSegs(c.formula)}</code></div>`).join("");
  return `<article class="pw-srv-col ${cls}">
    <header>
      <h3>${esc(srv)}</h3>
      <div class="pw-meta">${esc(it["生效窗口"]||"")}<br>${esc(it["数据行"]||"")}</div>
    </header>
    <div class="pw-curves">${curves}</div>
    ${it.attack_curve?`<div class="pw-atk"><h4>source_hurt<span>按攻击力</span></h4><div class="pw-cn">${esc(pwCnSegs(it.attack_curve,"atk")||"—")}</div></div>`:""}
    <details class="pw-raw"><summary>原始分段公式</summary>${raw}
      ${it.attack_curve?`<div class="pw-raw-row"><b>source_hurt</b><code>${pwSegs(it.attack_curve)}</code></div>`:""}
    </details>
  </article>`;
}
function pwRender(items){
  const notes=items.filter(it=>it.kind==="结论");
  const rate=items.filter(it=>it.kind==="曲线族");
  const atk=items.filter(it=>it.kind==="攻击力曲线");
  const srvItems=[];
  for(const [srv] of PW_SRV){
    const one=rate.find(it=>it["服型"]===srv);
    const a=atk.find(it=>it["服型"]===srv);
    if(one||a)srvItems.push(pwServerHTML(one?Object.assign({},one,{attack_curve:a&&a.attack_curve}):a));
  }
  const RCOL=PW_SRV.map(x=>PW_COLOR[x[0]]);
  const rateSeries=k=>PW_SRV.map(([srv])=>{
    const it=rate.find(x=>x["服型"]===srv);
    const c=it&&(it.rate_curves||[]).find(x=>x.key===k);
    return c?{name:srv,segs:pwParse(c.formula)}:null;
  }).filter(Boolean);
  const atkSeries=()=>PW_SRV.map(([srv])=>{
    const it=atk.find(x=>x["服型"]===srv);
    return it&&it.attack_curve?{name:srv,segs:pwParse(it.attack_curve)}:null;
  }).filter(Boolean);
  const charts=[
    pwChart("a_class（主加成曲线）",rateSeries("a_class"),{unit:"rate",colors:RCOL}),
    pwChart("p2p（玩家对玩家）",rateSeries("p2p"),{unit:"rate",colors:RCOL}),
    pwChart("m2p（另一组方向）",rateSeries("m2p"),{unit:"rate",colors:RCOL}),
    pwChart("source_hurt（按攻击力）",atkSeries(),{unit:"atk",colors:RCOL})
  ].join("");
  const g=document.getElementById("grid");
  g.innerHTML=`<div class="pw-page">
    <section class="pw-sec">
      <div class="pw-sec-hd"><h2>结论</h2><span>${notes.length} 条 · 点开可看说明与依据</span></div>
      <div class="pw-notes">${notes.map(pwNoteHTML).join("")}</div>
    </section>
    <section class="pw-sec">
      <div class="pw-sec-hd"><h2>曲线长什么样</h2><span>横轴是原始加成率 / 攻击力，纵轴是折算后的实际值；虚线是“完全不压缩”参考</span></div>
      <div class="pw-figs">${charts}</div>
      <p class="pw-tip">数值都是小数：配置里写的 0.3 就是 30%、0.05 就是 5%，公式直接拿小数算，白话再换算成百分比。例如加成 25% 时，a_class 第一段是 0.7×0.25 = 17.5%。<br>负数怎么办：配置里每一段的起点最低就是 0（没有任何负数区间），所以图也只从 0 画起。攻击力 &lt; 0、加成率 &lt; 0 属于配置表之外的情况——表里没有定义，不能把 kx+o 往 0 左边外推当作真实结果。</p>
    </section>
    <section class="pw-sec">
      <div class="pw-sec-hd"><h2>三服中文对照</h2><span>a_class / p2p / m2p / source_hurt 的逐段白话；原始公式折叠在每列底部</span></div>
      <div class="pw-srv">${srvItems.join("")}</div>
    </section>
    <footer class="pw-src">数据来自 special_hurt_params_data（经典服）/ _kj1（简单生存服）/ _yk（月卡服）/ hurt_params_data（全局默认）。
      完整图表：<a href="${encodeURI("伤害系统逆向/场景平衡_分段函数.html")}" target="_blank">三服全曲线及逐段表</a>
      · <a href="${encodeURI("伤害系统逆向/场景平衡_PvP两服.html")}" target="_blank">PvP 两服 7 图对照</a></footer>
  </div>`;
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${items.length} / ${DATA.items.length} 条`;
}
function sbPvpHTML(name){
  const g=(DATA.meta&&DATA.meta.pvp_detail&&DATA.meta.pvp_detail[name])||{};
  const pickSegs=(srv,k)=>{
    for(const r of (((g.servers||{})[srv])||[])){
      const segs=pwParse(r.curves&&r.curves[k]);
      if(segs.length)return segs;
    }
    return [];
  };
  const RCOL=PW_SRV.map(x=>PW_COLOR[x[0]]);
  const charts=PW_CURVE.map(([k,lab])=>pwChart(lab,
    PW_SRV.map(([srv])=>({name:srv,segs:pickSegs(srv,k)})).filter(s=>s.segs.length),
    {unit:"rate",colors:RCOL})).join("");
  const cols=PW_SRV.map(([srv,cls])=>{
    const rows=((g.servers||{})[srv])||[];
    const body=rows.length?rows.map(r=>`<div class="pvd-row">
        <div class="pvd-meta"><b>${esc(r.label||"")}</b><span>${esc(r.meta||"")}</span></div>
        ${PW_CURVE.map(([k,lab])=>`<div class="pvd-curve"><b>${lab}</b><div class="pw-cn">${esc(pwCnSegs(r.curves&&r.curves[k],"rate")||"—")}</div></div>`).join("")}
        <details class="pvd-raw"><summary>原始公式</summary>
          ${PW_CURVE.map(([k,lab])=>`<div class="pw-raw-row"><b>${lab}</b><code>${pwSegs(r.curves&&r.curves[k])}</code></div>`).join("")}
        </details>
      </div>`).join(""):`<div class="pvd-empty">无专属行</div>`;
    return `<div class="pvd-col ${cls}"><div class="pvd-srv">${srv}<em>${rows.length} 行</em></div>${body}</div>`;
  }).join("");
  return `<div class="pvd"><div class="pvd-hd">${esc(name)} · 伤害加成怎么算<span>三服对照 · 曲线图 + 白话</span></div>
    <div class="pvd-charts">${charts}</div>
    <p class="pvd-tip">线越早往下弯，说明该服把加成压得越狠；灰虚线是“完全不压缩”参考（实际值 = 原始值）；表内没有负数区间，图从 0 起。</p>
    <div class="pvd-grid">${cols}</div></div>`;
}
function sbToggleDetail(tr,name){
  let nx=tr.nextElementSibling;
  if(nx&&nx.classList.contains("sb-xrow")&&nx.getAttribute("data-g")===name){
    const show=nx.hidden;
    nx.hidden=!show;
    tr.classList.toggle("open",show);
    return;
  }
  const xr=document.createElement("tr");
  xr.className="sb-xrow";xr.setAttribute("data-g",name);
  const td=document.createElement("td");
  td.colSpan=8;td.innerHTML=sbPvpHTML(name);
  xr.appendChild(td);tr.after(xr);tr.classList.add("open");
}
function sbToggleAll(open){
  const t=document.querySelector("table.sbt");
  if(!t)return;
  const seen=new Set();
  for(const tr of t.querySelectorAll("tbody tr.sb-pvp")){
    const name=tr.getAttribute("data-g");
    if(!name)continue;
    const isOpen=tr.classList.contains("open");
    if(open){
      /* 同一场景可能占多行（不同服型），展开全部时每个场景只插入一份面板 */
      if(seen.has(name)||isOpen)continue;
      seen.add(name);
      sbToggleDetail(tr,name);
    }else if(isOpen){
      sbToggleDetail(tr,name);
    }
  }
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
  const groups=new Set(items.filter(it=>it.pvp_group).map(it=>it.pvp_group));
  if(groups.size){
    const bar=document.createElement("div");
    bar.className="sb-bar";
    bar.innerHTML=`<span>PvP 场景 ${groups.size} 个 · 点场景行展开经典服 / 简单生存服 / 月卡服 的分段函数</span>
      <button type="button" data-act="open">展开全部</button>
      <button type="button" data-act="close">收起全部</button>`;
    bar.onclick=e=>{const a=e.target.getAttribute("data-act");if(a)sbToggleAll(a==="open");};
    g.appendChild(bar);
  }
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
    const pvp=(it.pvp_group&&DATA.meta.pvp_detail&&DATA.meta.pvp_detail[it.pvp_group])?it.pvp_group:null;
    const cells=[
      ["scene",(pvp?'<span class="sb-x">▸</span> ':"")+esc(it.name||"")+(pvp?'<span class="sb-pill">三服公式</span>':'')],
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
    if(pvp){
      tr.className="sb-pvp";
      tr.setAttribute("data-g",pvp);
      tr.onclick=()=>sbToggleDetail(tr,pvp);
    }
    tb.appendChild(tr);
  }
  t.appendChild(tb);g.appendChild(t);
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${items.length} / ${DATA.items.length} 条`;
}

/* ── 服务器类型表格视图（board id = server_types）───────────────────────
   列全部来自 board 数据字段，不做任何推断：
     服型后缀 suffix / 名称 name / 标签 label / 本端表数 table_count
     状态 state / 判定依据 why / 证据等级 evidence_level / 来源 source
   ★ 判定依据 why 是长句，单独给 wrap 类，避免被 nowrap 截断。 */
let ST_SORT={key:"suffix",dir:1};
function stVal(it,k){
  if(k==="服型后缀")return it.suffix||"";
  if(k==="名称")return it.name||"";
  if(k==="标签")return it.label||"";
  if(k==="本端表数")return Number(it.table_count||0);
  if(k==="状态")return it.state||"";
  if(k==="判定依据")return it.why||"";
  if(k==="证据等级")return it.evidence_level||"";
  if(k==="来源")return it.source||"";
  return it.name||"";
}
function stRender(items){
  const cols=["服型后缀","名称","标签","本端表数","状态","判定依据","证据等级","来源"];
  const sorted=items.slice().sort((a,b)=>{
    const k=ST_SORT.key,v1=stVal(a,k),v2=stVal(b,k);
    if(typeof v1==="number"&&typeof v2==="number"){
      if(v1!==v2)return (v1-v2)*ST_SORT.dir;
    }else{
      const c=String(v1).localeCompare(String(v2),"zh-CN");
      if(c)return c*ST_SORT.dir;
    }
    return String(a.suffix||"").localeCompare(String(b.suffix||""),"zh-CN");
  });
  const g=document.getElementById("grid");
  g.innerHTML="";
  const t=document.createElement("table");
  t.className="sbt";
  const thead=document.createElement("thead");
  const trh=document.createElement("tr");
  for(const c of cols){
    const th=document.createElement("th");
    th.textContent=c+(ST_SORT.key===c?(ST_SORT.dir>0?" ▲":" ▼"):"");
    th.onclick=()=>{
      if(ST_SORT.key===c)ST_SORT.dir*=-1;else{ST_SORT.key=c;ST_SORT.dir=1;}
      render();
    };
    trh.appendChild(th);
  }
  thead.appendChild(trh);t.appendChild(thead);
  const tb=document.createElement("tbody");
  for(const it of sorted){
    const tr=document.createElement("tr");
    const cells=[
      ["num",it.suffix||"-"],
      ["",esc(it.name||"-")],
      ["",`<span class="tag">${esc(it.label||"-")}</span>`],
      ["num",Number(it.table_count||0).toLocaleString("en-US")],
      ["",`<span class="tag">${esc(it.state||"-")}</span>`],
      ["wrap",esc(it.why||"-")],
      ["dim",esc(it.evidence_level||"-")],
      ["dim",esc(it.source||"-")],
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

/* ── 可切换视图：CDN 资源库 / 本地还原树 ────────────────────────────
   体积口径统一为十进制：MB ÷ 1000 = GB（与 meta.row_stats.total_gb 同源，
   避免同页出现 160.3 GB 与 164.1 GB 两个互相打架的数字）。 */
function fmtMB(mb){
  const v=Number(mb||0);
  /* 十进制 GB（÷1000）：与 meta.row_stats.total_gb 同源。
     保留 1 位小数 —— 板级事实是 164.1 GB，不能显示成 "164 GB"（精度丢失）。 */
  if(v>=1000)return (v/1000).toFixed(1)+" GB";
  return v.toLocaleString("en-US")+" MB";
}
function fmtInt(n){return Number(n||0).toLocaleString("en-US");}
function vEl(tag,cls,html){const e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
/* 本地状态三色：全在本地 / 部分在本地 / 全未下载（事实字段 local_state 的直译，不做推断） */
function cdnStateCls(done,part,n){
  if(done+part>=n)return "ok";
  if(done+part===0)return "miss";
  return "warn";
}
/* 两块板的统一筛选口径：证据等级 + 板级自定义筛选（meta.filters）+ 搜索框。
   ★ 与通用渲染路径的 filters 判定保持同一套语义，不另立口径。 */
/* 视图切换器（CDN 资源库 / 本地还原树）
   按钮组放在控件栏；当前视图写入 ?view=（可分享、可回退）。 */
const VIEW_OPTS={
  cdn_library:[["group","目录组"],["table","全量表格"]],
  local_restore_tree:[["index","概览+索引"],["dash","仅概览"]],
};
function buildViewSwitch(){
  const box=document.getElementById("viewSwitch");
  if(!box)return;
  const opts=VIEW_OPTS[b]||[];
  if(!opts.length){box.style.display="none";return;}
  box.style.display="";
  box.innerHTML="";
  const cur=curView();
  for(const [k,label] of opts){
    const btn=document.createElement("button");
    btn.type="button";
    btn.className="viewsw-btn"+(k===cur?" on":"");
    btn.dataset.view=k;
    btn.textContent=label;
    btn.setAttribute("aria-pressed",String(k===cur));
    btn.addEventListener("click",()=>{setView(k);});
    box.appendChild(btn);
  }
}
function viewFilterItems(){
  const q=(document.getElementById("q")||{}).value||"";
  const qLower=String(q).trim().toLowerCase();
  const feEl=document.getElementById("fEv");
  const fe=feEl?feEl.value:"";
  const cf=DATA&&Array.isArray(DATA._custFilters)?DATA._custFilters:[];
  const hay=TREE_BOARD?treeHay():cdnHay();
  const out=[];
  const src=(DATA&&DATA.items)||[];
  for(let i=0;i<src.length;i++){
    const it=src[i];
    if(fe&&it.evidence!==fe)continue;
    let skip=false;
    for(const c of cf){
      const v=c.sel?c.sel.value:"";
      if(v&&String(it[c.key]??"")!==v){skip=true;break;}
    }
    if(skip)continue;
    if(qLower&&!hay[i].includes(qLower))continue;
    out.push(it);
  }
  return out;
}
/* CDN 检索串：逻辑包名 / 目录组 / 变体文件 / 档位 / 本地状态（板内既有字段） */
function cdnHay(){
  if(!DATA._cdnHay){
    DATA._cdnHay=(DATA.items||[]).map(it=>
      `${it.name||""} ${it.group||""} ${it.variant_names||""} ${it.tiers||""} ${it.local_state||""} ${it.id||""}`.toLowerCase());
  }
  return DATA._cdnHay;
}

/* ── CDN 视图二（?view=table）：全量可排序表格（方案 A）──────────────── */
const CDN_TCOLS=["逻辑包","目录组","卷数","变体合计","单卷最大","条目数","档位数","本地","变体文件"];
function cdnVal(it,k){
  if(k==="逻辑包")return it.name||"";
  if(k==="目录组")return it.group||"";
  if(k==="卷数")return Number(it.files||0);
  if(k==="变体合计")return Number(it.size_total_mb||0);
  if(k==="单卷最大")return Number(it.size_max_mb||0);
  if(k==="条目数")return Number(it.entries||0);
  if(k==="档位数")return Number(it.tier_count||0);
  if(k==="本地")return it.local_state||"";
  if(k==="变体文件")return it.variant_names||"";
  return it.name||"";
}
let CDN_SORT={key:"变体合计",dir:-1};
function cdnTableRender(items){
  const sorted=items.slice().sort((a,b)=>{
    const k=CDN_SORT.key,v1=cdnVal(a,k),v2=cdnVal(b,k);
    if(typeof v1==="number"&&typeof v2==="number"){if(v1!==v2)return (v1-v2)*CDN_SORT.dir;}
    else{const c=String(v1).localeCompare(String(v2),"zh-CN");if(c)return c*CDN_SORT.dir;}
    return String(a.name||"").localeCompare(String(b.name||""),"zh-CN");
  });
  const g=document.getElementById("grid");g.innerHTML="";
  const t=vEl("table","vtab");
  const thead=vEl("thead");const trh=vEl("tr");
  for(const c of CDN_TCOLS){
    const th=vEl("th",null,esc(c)+(CDN_SORT.key===c?(CDN_SORT.dir>0?" ▲":" ▼"):""));
    th.onclick=()=>{if(CDN_SORT.key===c)CDN_SORT.dir*=-1;else{CDN_SORT.key=c;CDN_SORT.dir=(["变体合计","单卷最大","条目数","卷数","档位数"].indexOf(c)>=0)?-1:1;}render();};
    trh.appendChild(th);
  }
  thead.appendChild(trh);t.appendChild(thead);
  const tb=vEl("tbody");
  for(const it of sorted){
    const tr=vEl("tr");
    const cells=[
      ["mono",esc(it.name||"")],
      ["",esc(it.group||"-")],
      ["num",fmtInt(it.files)],
      ["num",fmtMB(it.size_total_mb)],
      ["num",fmtMB(it.size_max_mb)],
      ["num",fmtInt(it.entries)],
      ["num",fmtInt(it.tier_count)],
      ["",`<span class="vtag ${it.local_state==="完整"?"ok":(it.local_state==="部分"?"warn":"miss")}">${esc(it.local_state||"-")}</span>`],
      ["dim",esc(it.variant_names||"-")],
    ];
    for(const [cls,val] of cells){const td=vEl("td",cls,cls==="num"?"":val);if(cls==="num")td.textContent=val;tr.appendChild(td);}
    tb.appendChild(tr);
  }
  t.appendChild(tb);
  /* 全量表 9 列：外层给横向滚动容器，窄屏不撑破页面（rules/frontend.yml 硬规则） */
  const wrap=vEl("div","vscroll");
  wrap.appendChild(t);
  g.appendChild(wrap);
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${items.length} / ${(DATA.items||[]).length} 个逻辑包 · 点表头排序`;
}

/* ── CDN 视图一（默认 ?view=group）：目录组折叠 + 体积条 ───────────────
   体积条宽度 = 该组 size_total_mb 之和 ÷ 最大组之和（纯派生比例，无推断）；
   组内展开体是行内明细表（逻辑包级），即「目录组折叠为主、明细表为辅」。 */
function cdnPackTable(list){
  const t=vEl("table","vtab vtab-sub");
  t.innerHTML="<thead><tr><th>逻辑包</th><th>卷数</th><th>变体合计</th><th>单卷最大</th><th>条目数</th><th>档位</th><th>本地</th></tr></thead>";
  const tb=vEl("tbody");
  const s=list.slice().sort((a,b)=>(Number(b.size_total_mb)||0)-(Number(a.size_total_mb)||0));
  for(const it of s){
    const tr=vEl("tr");
    const cells=[
      ["mono",esc(it.name||"")],
      ["num",fmtInt(it.files)],
      ["num",fmtMB(it.size_total_mb)],
      ["num",fmtMB(it.size_max_mb)],
      ["num",fmtInt(it.entries)],
      ["dim",esc(it.tiers||"-")],
      ["",`<span class="vtag ${it.local_state==="完整"?"ok":(it.local_state==="部分"?"warn":"miss")}">${esc(it.local_state||"-")}</span>`],
    ];
    for(const [cls,val] of cells){const td=vEl("td",cls,cls==="num"?"":val);if(cls==="num")td.textContent=val;tr.appendChild(td);}
    tb.appendChild(tr);
  }
  t.appendChild(tb);return t;
}
function cdnGroupRender(items){
  const g=document.getElementById("grid");g.innerHTML="";
  const groups=new Map();
  for(const it of items){
    const k=it.group||"(未分组)";
    if(!groups.has(k))groups.set(k,[]);
    groups.get(k).push(it);
  }
  const rows=[...groups.entries()].map(([name,list])=>{
    const mb=list.reduce((s,x)=>s+(Number(x.size_total_mb)||0),0);
    const ent=list.reduce((s,x)=>s+(Number(x.entries)||0),0);
    const done=list.filter(x=>x.local_state==="完整").length;
    const part=list.filter(x=>x.local_state==="部分").length;
    return {name,list,mb,ent,done,part,n:list.length};
  }).sort((a,b)=>b.mb-a.mb||b.n-a.n);
  const maxMb=Math.max(...rows.map(r=>r.mb),1);
  const rs=(DATA.meta&&DATA.meta.row_stats)||{};
  const ss=(DATA.meta&&DATA.meta.state_summary)||{};
  const wrap=vEl("div","vwrap");
  const sum=vEl("div","vsum");
  const tile=(k,v,n)=>sum.appendChild(vEl("div","vtile",`<div class="vt-k">${esc(k)}</div><div class="vt-v">${esc(v)}</div><div class="vt-n">${esc(n||"")}</div>`));
  tile("逻辑包",fmtInt(rs.logical_packs!=null?rs.logical_packs:(DATA.items||[]).length),"全量 · 去掉分卷后缀归并");
  tile("文件卷",fmtInt(rs.files),"全量");
  tile("条目数",fmtInt(rs.entries),"全量");
  tile("变体合计",fmtMB((Number(rs.total_gb)||0)*1000),"全量 · 十进制 GB");
  tile("本地已下载",fmtMB((Number(rs.local_gb)||0)*1000),"全量");
  tile("本地状态",["完整","部分","未下载"].filter(k=>ss[k]!=null).map(k=>`${k} ${ss[k]}`).join(" · ")||"未记录","全量");
  wrap.appendChild(sum);
  const gs=vEl("div","vgroups");
  for(const r of rows){
    const box=vEl("div","vgroup");
    const h=vEl("div","vgroup-h");
    const caret=vEl("span","vcaret","▸");
    const bar=vEl("span","vbar");const fill=vEl("i");fill.style.width=Math.max(1,Math.round(r.mb/maxMb*100))+"%";bar.appendChild(fill);
    h.appendChild(caret);
    h.appendChild(vEl("span","vg-name",esc(r.name)));
    h.appendChild(bar);
    h.appendChild(vEl("span","vg-num",`${r.n} 包 · ${fmtMB(r.mb)} · 条目 ${fmtInt(r.ent)}`));
    h.appendChild(vEl("span","vtag "+cdnStateCls(r.done,r.part,r.n),`本地 ${r.done+r.part}/${r.n}`));
    const body=vEl("div","vgroup-b");body.hidden=true;
    body.appendChild(cdnPackTable(r.list));
    h.onclick=()=>{body.hidden=!body.hidden;caret.textContent=body.hidden?"▸":"▾";};
    box.appendChild(h);box.appendChild(body);gs.appendChild(box);
  }
  wrap.appendChild(gs);g.appendChild(wrap);
  const c=document.getElementById("count");
  if(c)c.textContent=`${rows.length} 个目录组 · 显示 ${items.length} / ${(DATA.items||[]).length} 个逻辑包`;
}
function cdnRender(items){
  if(curView()==="table"){cdnTableRender(items);return;}
  cdnGroupRender(items);
}

/* ── 还原树视图 ────────────────────────────────────────────────────────
   模块 = 文件名第一个下划线之前的片段（纯字符串切分，不含语义推断）。
   为什么不按 .py/.nxs 全局分两列：全量 .py 27,774 / .nxs 5,827 严重失衡，
   且 .nxs 与 _chs.py 强配对（5,249/5,827），按模块分组才看得出配对关系。 */
let TREE_MODS=[];
const TREE_MOD_CAP=200;
function treeModuleOf(it){
  const fn=String(it.name||"").split("/").pop()||"";
  const i=fn.indexOf("_");
  return i>0?fn.slice(0,i):fn;
}
/* 还原树检索串：文件名/扩展名/落盘时间/体积/来源（板内既有字段，不做推断） */
function treeHay(){
  if(!DATA._treeHay){
    DATA._treeHay=(DATA.items||[]).map(it=>`${it.name||""} ${it.ext||""} ${it.mtime||""} ${it.size_kb??""} ${it.source||""}`.toLowerCase());
  }
  return DATA._treeHay;
}
function treeItems(){
  const q=(document.getElementById("q").value||"").trim().toLowerCase();
  const fe=document.getElementById("fEv").value;
  const hay=treeHay();
  const out=[];
  for(let i=0;i<(DATA.items||[]).length;i++){
    const it=DATA.items[i];
    if(fe&&it.evidence!==fe)continue;
    if(q&&!hay[i].includes(q))continue;
    out.push(it);
  }
  return out;
}
/* 概览（板级全量事实，不随筛选变化） */
function treeOverview(){
  const m=DATA.meta||{};
  const ss=m.state_summary||{};
  const es=m.ext_stats||{};
  const box=vEl("div","vpanel");
  box.appendChild(vEl("div","vpanel-h","全量概览（板级事实 · 不随筛选变化）"));
  const tiles=vEl("div","vtiles");
  const tile=(k,v,n)=>tiles.appendChild(vEl("div","vtile",`<div class="vt-k">${esc(k)}</div><div class="vt-v">${esc(v)}</div><div class="vt-n">${esc(n||"")}</div>`));
  tile("文件总数",fmtInt(ss["文件"]!=null?ss["文件"]:itemsTotal()),"配置树 + 增量快照");
  tile(".py 表定义",fmtInt(es[".py"]!=null?es[".py"]:0),"可直接读的表定义");
  tile(".nxs 封装",fmtInt(es[".nxs"]!=null?es[".nxs"]:0),"打包/加密封装");
  tile("配置树",fmtInt(ss["配置树"]!=null?ss["配置树"]:0),"合并体");
  tile("增量快照",fmtInt(ss["仅增量快照"]!=null?ss["仅增量快照"]:0),"热更增量");
  tile("名称还原率",String(ss["已还原文件名比例"]!=null?ss["已还原文件名比例"]:"未记录"),"全量");
  box.appendChild(tiles);
  return box;
}
function itemsTotal(){return (DATA.items||[]).length;}
/* 当前筛选下的分布（派生自筛选后条目） */
function treeDist(items){
  const byExt=new Map(),byDay=new Map();
  let kb=0;
  for(const it of items){
    kb+=Number(it.size_kb)||0;
    const e=String(it.ext||"(无)").toLowerCase();byExt.set(e,(byExt.get(e)||0)+1);
    const d=String(it.mtime||"").slice(0,10)||"(无日期)";byDay.set(d,(byDay.get(d)||0)+1);
  }
  const box=vEl("div","vpanel");
  box.appendChild(vEl("div","vpanel-h","当前筛选的分布"));
  const bars=vEl("div","vbars");
  const addBar=(k,v,max,cls)=>{
    const row=vEl("div","vbar-row");
    row.appendChild(vEl("span","vb-k",esc(k)));
    const bar=vEl("span","vbar");const fill=vEl("i");fill.style.width=Math.max(1,Math.round(v/max*100))+"%";if(cls)fill.className=cls;bar.appendChild(fill);row.appendChild(bar);
    row.appendChild(vEl("span","vb-n",fmtInt(v)));
    bars.appendChild(row);
  };
  const ex=[...byExt.entries()].sort((a,b)=>b[1]-a[1]);
  const mxE=Math.max(...ex.map(x=>x[1]),1);
  for(const [k,v] of ex)addBar(k,v,mxE,"ok");
  const dy=[...byDay.entries()].sort((a,b)=>String(b[0]).localeCompare(String(a[0])));
  const mxD=Math.max(...dy.map(x=>x[1]),1);
  for(const [k,v] of dy)addBar(k,v,mxD,"warn");
  box.appendChild(bars);
  box.appendChild(vEl("div","vnote",`筛选后 ${fmtInt(items.length)} 个文件 · 合计 ${fmtInt(kb)} KB`));
  return box;
}
function treeModCol(mi,ci,list){
  const col=vEl("div","vcol");
  col.appendChild(vEl("div","vcol-h",`<span class="vtag ${ci===0?"ok":"warn"}">${ci===0?".py 表定义":".nxs 封装"}</span><span class="vg-num">${fmtInt(list.length)} 个</span>`));
  const b=vEl("div","vcol-b");
  b.dataset.mi=mi;b.dataset.ci=ci;
  col.appendChild(b);
  col._list=list;
  return col;
}
function treeModFill(b,offset){
  const col=b.parentNode;
  const list=col._list||[];
  const slice=list.slice(offset,offset+TREE_MOD_CAP);
  for(const it of slice){
    b.appendChild(vEl("div","vfile",
      `<span class="vp">${esc(String(it.name||"").split("/").pop())}</span>`
      +`<span class="vk">${esc(it.ext||"")}</span>`
      +`<span class="vk">${Number(it.size_kb||0).toLocaleString("en-US")} KB</span>`
      +`<span class="vk">${esc(it.mtime||"")}</span>`));
  }
  const rest=list.length-offset-slice.length;
  if(rest>0){
    const btn=document.createElement("button");
    btn.type="button";btn.className="vmore";btn.textContent=`加载更多（还有 ${fmtInt(rest)} 个）`;
    btn.onclick=(e)=>{e.stopPropagation();btn.remove();treeModFill(b,offset+TREE_MOD_CAP);};
    b.appendChild(btn);
  }
}
/* 还原树视图一（默认 ?view=index）：聚合概览 + 模块双列索引 */
function treeIndexRender(items){
  const g=document.getElementById("grid");g.innerHTML="";
  const wrap=vEl("div","vdash");
  wrap.appendChild(treeOverview());
  wrap.appendChild(treeDist(items));
  const modMap=new Map();
  for(const it of items){
    const mo=treeModuleOf(it);
    if(!modMap.has(mo))modMap.set(mo,[]);
    modMap.get(mo).push(it);
  }
  const mods=[...modMap.entries()].map(([name,list])=>({name,list})).sort((a,b)=>b.list.length-a.list.length||a.name.localeCompare(b.name));
  TREE_MODS=mods;
  const idx=vEl("div","vpanel");
  idx.appendChild(vEl("div","vpanel-h",`模块索引 · ${fmtInt(mods.length)} 个模块（按文件数降序；展开看模块内 .py / .nxs 双列）`));
  const list=vEl("div","vmods");
  mods.forEach((mo,mi)=>{
    const py=mo.list.filter(x=>x.ext===".py"),nx=mo.list.filter(x=>x.ext===".nxs");
    const box=vEl("div","vmod");
    const h=vEl("div","vmod-h");
    const caret=vEl("span","vcaret","▸");
    h.appendChild(caret);
    h.appendChild(vEl("span","vg-name",esc(mo.name)));
    h.appendChild(vEl("span","vg-num",`${mo.list.length} 个 · .py ${py.length} / .nxs ${nx.length}`));
    const body=vEl("div","vmod-b");body.hidden=true;
    h.onclick=()=>{
      if(body.hidden&&!body.dataset.built){
        body.dataset.built="1";
        const cols=vEl("div","vcols");
        const c0=treeModCol(mi,0,py),c1=treeModCol(mi,1,nx);
        cols.appendChild(c0);cols.appendChild(c1);
        body.appendChild(cols);
        treeModFill(c0.querySelector(".vcol-b"),0);
        treeModFill(c1.querySelector(".vcol-b"),0);
      }
      body.hidden=!body.hidden;
      caret.textContent=body.hidden?"▸":"▾";
    };
    box.appendChild(h);box.appendChild(body);list.appendChild(box);
  });
  idx.appendChild(list);
  wrap.appendChild(idx);
  g.appendChild(wrap);
  const c=document.getElementById("count");
  if(c)c.textContent=`${fmtInt(mods.length)} 个模块 · 显示 ${fmtInt(items.length)} / ${fmtInt(itemsTotal())} 个文件`;
}
/* 还原树视图二（?view=dash）：仅聚合概览 */
function treeDashRender(items){
  const g=document.getElementById("grid");g.innerHTML="";
  const wrap=vEl("div","vdash");
  wrap.appendChild(treeOverview());
  wrap.appendChild(treeDist(items));
  g.appendChild(wrap);
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${fmtInt(items.length)} / ${fmtInt(itemsTotal())} 个文件`;
}
function treeRender(items){
  if(curView()==="dash"){treeDashRender(items);return;}
  treeIndexRender(items);
}

/* ════════════════ 活动总表月度索引（activity_master，2026-11-02 方案 A）════════════════
   3519 条、0 张配图。101 个月份折叠头本身就有 5k+ px，首屏照样 10 屏；改为
   「状态概览 + 年份/月份索引 + 单月正文（60 行分页）」：索引两行 ≈ 90px，
   正文只放选中的一个月，默认当前月。搜索时隐藏索引、平铺命中（同样 60 行分页）。
   行点击复用 .i.roster 的 D2 链路，详情由 ACTIVITY_D2 自建。 */
let AM_GROUPS=null,AM_LIST=null,AM_INDEX=null,AM_SIG="",AM_SEL={year:null,month:null},AM_PAGE=60;
const AM_PAGE_STEP=60;
function amStatusCls(s){
  return s==="进行中"?"live":s==="未开始"?"up":s==="已结束"?"end":"none";
}
function amPlain(s){
  return String(s??"").replace(/#[A-Za-z](?:\([^)]{0,80}\)|\d{1,3})?/g,"").replace(/\s+/g," ").trim();
}
function amCurMonth(){
  const d=new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}`;
}
function amYearOf(key){
  return key==="无时间"?"":String(key).slice(0,4);
}
function amDateRange(it,key){
  const s=String(it.start||""),e=String(it.end||"");
  if(!s&&!e)return "无时间";
  const y=String(key||"").slice(0,4);
  const sh=d=>{
    if(!d)return "—";
    return (y&&d.slice(0,4)===y)?d.slice(5):d;
  };
  return `${sh(s)} → ${sh(e)}`;
}
function amSortList(items){
  return items.slice().sort((a,b)=>{
    const sa=String(a.start||""),sb=String(b.start||"");
    if(sa!==sb){
      if(!sa)return 1;
      if(!sb)return -1;
      return sb.localeCompare(sa);
    }
    return Number(b.item_id||0)-Number(a.item_id||0);
  });
}
function amGroupsOf(list){
  const m=new Map();
  for(const it of list){
    const k=String(it.month||"").trim()||"无时间";
    if(!m.has(k))m.set(k,[]);
    m.get(k).push(it);
  }
  return m;
}
function amMonthKeys(groups){
  return [...groups.keys()].sort((a,b)=>{
    if(a==="无时间")return 1;
    if(b==="无时间")return -1;
    return b.localeCompare(a);
  });
}
/* 状态概览口径：沿用当前「证据等级 + 板级筛选 + 搜索」，但剔除状态自身，
   这样切到「已结束」时另外三张卡的数字不会被清零。 */
function amCountBase(q,fe){
  const cf=DATA._custFilters||[];
  const out={"未开始":0,"进行中":0,"已结束":0,"无时间":0};
  for(const it of DATA.items){
    if(fe&&it.evidence!==fe)continue;
    let ok=true;
    for(const f of cf){
      if(f.key==="activity_status")continue;
      const v=f.sel?f.sel.value:"";
      if(v&&String(it[f.key]??"")!==v){ok=false;break;}
    }
    if(!ok)continue;
    if(q&&!JSON.stringify(it).toLowerCase().includes(q))continue;
    const s=it.activity_status||"无时间";
    out[s]=(out[s]||0)+1;
  }
  return out;
}
function amIndexHTML(keys){
  const byYear=new Map();
  for(const k of keys){
    if(k==="无时间")continue;
    const y=k.slice(0,4);
    if(!byYear.has(y))byYear.set(y,{n:0,months:[]});
    const o=byYear.get(y);o.n+=(AM_GROUPS.get(k)||[]).length;o.months.push(k);
  }
  const years=[...byYear.keys()].sort((a,b)=>b.localeCompare(a));
  const noneN=keys.includes("无时间")?(AM_GROUPS.get("无时间")||[]).length:0;
  const isNone=AM_SEL.month==="无时间";
  const yearSel=isNone?"无时间":(byYear.has(AM_SEL.year)?AM_SEL.year:(years[0]||"无时间"));
  const ychips=years.map(y=>{
    const on=yearSel===y;
    return `<button type="button" class="am-ychip${on?" on":""}" data-am-year="${esc(y)}" aria-pressed="${on}">${esc(y)}<span class="am-yn">${byYear.get(y).n}</span></button>`;
  }).join("")+(noneN?`<button type="button" class="am-ychip${isNone?" on":""}" data-am-year="无时间" aria-pressed="${isNone}">无时间<span class="am-yn">${noneN}</span></button>`:"");
  const mchips=isNone
    ?`<button type="button" class="am-mchip on" data-am-monthsel="无时间" aria-pressed="true">无时间<span class="am-mn">${noneN}</span></button>`
    :(byYear.get(yearSel)?byYear.get(yearSel).months.map(k=>{
      const g=AM_GROUPS.get(k)||[];
      const on=k===AM_SEL.month;
      const live=g.filter(it=>it.activity_status==="进行中").length;
      const label=`${k.slice(5)}月`;
      return `<button type="button" class="am-mchip${on?" on":""}" data-am-monthsel="${esc(k)}" aria-pressed="${on}" title="${esc(k)} · ${g.length} 条${live?` · 进行中 ${live}`:""}">${live?'<span class="am-mdot" aria-hidden="true"></span>':""}${esc(label)}<span class="am-mn">${g.length}</span></button>`;
    }).join(""):"");
  return `<div class="am-index">
    <div class="am-irow"><span class="am-ilabel">年份</span><div class="am-chips">${ychips}</div></div>
    <div class="am-irow"><span class="am-ilabel">月份</span><div class="am-chips">${mchips}</div></div>
  </div>`;
}
function amMoreHTML(rest){
  return `<button type="button" class="am-more" data-am-more>加载更多<span class="am-more-n">还有 ${rest} 条</span></button>`;
}
function amRowsHTML(group){
  return group.map(it=>{
    const idx=AM_INDEX&&AM_INDEX.has(String(it.id))?AM_INDEX.get(String(it.id)):-1;
    const st=it.activity_status||"无时间";
    const cls=amStatusCls(st);
    const name=it.name||it.display_name||it.id;
    const typ=it.activity_type||it.kind||"";
    const sub=amPlain(it.sub_title);
    const tab=amPlain(it.tab_name||it.first_level_tab);
    const note=sub||tab;
    return `<div class="i roster am-row" data-cidx="${idx}" role="button" tabindex="0" aria-label="查看「${esc(name)}」详情">
      <span class="am-dot ${cls}" aria-hidden="true"></span>
      <div class="am-main">
        <div class="am-name"><span class="am-nm">${esc(name)}</span>${typ?`<span class="am-type">${esc(typ)}</span>`:""}</div>
        ${note?`<div class="am-sub">${esc(note)}</div>`:""}
      </div>
      <div class="am-when">
        <span class="am-date">${esc(amDateRange(it,it.month))}</span>
        <span class="am-status ${cls}">${esc(st)}</span>
      </div>
    </div>`;
  }).join("");
}
function amOverviewHTML(counts,active){
  const keys=["进行中","未开始","已结束","无时间"];
  const total=keys.reduce((s,k)=>s+(counts[k]||0),0);
  return `<div class="am-sum-head"><span class="am-sum-title">状态概览</span><span class="am-sum-note">当前筛选 ${total} 条 · 不含状态筛选 · 点击切换</span></div>`+
    `<div class="am-sum">${keys.map(k=>{
      const on=active===k;
      return `<button type="button" class="am-stat${on?" on":""}" data-am-status="${esc(k)}" aria-pressed="${on}">
        <span class="am-stat-n">${counts[k]||0}</span>
        <span class="am-stat-l"><span class="am-dot ${amStatusCls(k)}" aria-hidden="true"></span>${esc(k)}</span>
      </button>`;
    }).join("")}</div>`;
}
function amRenderLedger(g,items,q,fe){
  const cf=DATA._custFilters||[];
  const stSel=cf.find(f=>f.key==="activity_status");
  const active=stSel?stSel.value:"";
  const counts=amCountBase(q,fe);
  const sig=[q,fe,...cf.map(f=>f.key+"="+(f.sel?f.sel.value:""))].join("|");
  if(sig!==AM_SIG){AM_SIG=sig;AM_PAGE=AM_PAGE_STEP;}
  const list=amSortList(items);
  AM_LIST=list;
  AM_INDEX=new Map(list.map((it,i)=>[String(it.id),i]));
  AM_GROUPS=amGroupsOf(list);
  C2.prov=ACTIVITY_D2;C2.chips=list;C2.html={};
  const countEl=document.getElementById("count");

  /* 搜索：索引让位给命中列表（仍分页，避免一次铺 3519 行） */
  if(q){
    const shown=list.slice(0,AM_PAGE);
    let html=amOverviewHTML(counts,active)
      +`<div class="am-flathead"><span class="am-flat-title">搜索命中 ${list.length} 条</span><span class="am-flat-note">按开始时间 ↓ · 已显示 ${shown.length}</span></div>`
      +`<section class="am-month open"><div class="am-rows" data-filled="1">${amRowsHTML(shown)}</div></section>`;
    if(list.length>AM_PAGE)html+=amMoreHTML(list.length-AM_PAGE);
    g.innerHTML=html;
    if(countEl)countEl.textContent=`搜索命中 ${list.length} 条 · 已显示 ${shown.length} / ${list.length}`;
    if(C2.open)c2Resync();
    return;
  }

  const keys=amMonthKeys(AM_GROUPS);
  /* 选中月份：默认当前月；当前月无数据取最新月；筛选后消失则回退 */
  if(keys.indexOf(AM_SEL.month)<0){
    AM_SEL.month=keys.indexOf(amCurMonth())>=0?amCurMonth():(keys[0]||"无时间");
    AM_PAGE=AM_PAGE_STEP;
  }
  AM_SEL.year=amYearOf(AM_SEL.month);
  const group=AM_GROUPS.get(AM_SEL.month)||[];
  const shown=group.slice(0,AM_PAGE);
  const live=group.filter(it=>it.activity_status==="进行中").length;
  const up=group.filter(it=>it.activity_status==="未开始").length;
  let html=amOverviewHTML(counts,active)
    +amIndexHTML(keys)
    +`<section class="am-month open">
      <div class="am-curhead">
        <span class="am-m">${AM_SEL.month==="无时间"?"无时间":esc(AM_SEL.month)}</span>
        <span class="am-mcount">${group.length} 条</span>
        ${live?`<span class="am-mlive">进行中 ${live}</span>`:""}
        ${up?`<span class="am-mup">未开始 ${up}</span>`:""}
        <span class="am-curpage">${shown.length} / ${group.length}</span>
      </div>
      <div class="am-rows" data-filled="1">${amRowsHTML(shown)}</div>
    </section>`;
  if(group.length>AM_PAGE)html+=amMoreHTML(group.length-AM_PAGE);
  g.innerHTML=html;
  if(countEl)countEl.textContent=`显示 ${items.length} / ${DATA.items.length} 条 · 选中 ${AM_SEL.month}（${group.length} 条）· ${keys.length} 个月份索引`;
  if(C2.open)c2Resync();
}
function amSetYear(y){
  if(y==="无时间"){
    AM_SEL.year="";AM_SEL.month="无时间";
  }else{
    const months=amMonthKeys(AM_GROUPS||new Map()).filter(k=>k!=="无时间"&&k.slice(0,4)===y);
    AM_SEL.year=y;
    AM_SEL.month=months.indexOf(AM_SEL.month)>=0?AM_SEL.month:(months[0]||"无时间");
  }
  AM_PAGE=AM_PAGE_STEP;
  render();
}
function amSetMonthSel(k){
  AM_SEL.month=k;
  AM_SEL.year=amYearOf(k);
  AM_PAGE=AM_PAGE_STEP;
  render();
}
function amSetStatus(k){
  const cf=(DATA._custFilters||[]).find(f=>f.key==="activity_status");
  if(!cf||!cf.sel)return;
  cf.sel.value=(cf.sel.value===k?"":k);
  render();
}
function amD2Body(it,mode){
  const rows=[];
  const add=(k,v)=>{if(v!=null&&String(v).trim()!=="")rows.push(`<div class="k">${esc(k)}</div><div class="v">${esc(v)}</div>`);};
  add("活动ID",it.item_id??it.id);
  add("活动类型",it.activity_type);
  add("类别",it.kind);
  add("子标题",amPlain(it.sub_title));
  add("常开",it.permanent);
  add("开始",it.start);
  add("结束",it.end);
  add("状态",it.activity_status);
  add("月份",it.month);
  add("页签",it.first_level_tab);
  add("页签名",amPlain(it.tab_name));
  add("来源",it.source);
  const pr=it.provenance||{};const tech=pr.tech||{};
  const tr=[];
  const tadd=(k,v)=>{if(v!=null&&String(v).trim()!=="")tr.push(`<div class="k">${esc(k)}</div><div class="v">${esc(v)}</div>`);};
  tadd("证据等级",EV_CN[it.evidence]||it.evidence);
  tadd("证据类型",it.evidence_level);
  tadd("源表行键",pr.row_key??it.item_id??it.id);
  tadd("原始类名",tech.hd_class);
  tadd("活动子类型",tech.hd_type);
  tadd("界面类",tech.ui_class);
  tadd("定位链状态",pr.locator_chain&&pr.locator_chain.chain_status);
  tadd("状态标签",Array.isArray(it.status_tags)?it.status_tags.join("、"):"");
  const sha=String(pr.source_lock_sha256||(pr.upstream&&pr.upstream.package_sha256)||"");
  tadd("源包摘要",sha?sha.slice(0,16)+"…":"");
  const content=`<div class="am-d2">
    <div class="am-d2-h">活动信息</div>
    <div class="kv">${rows.join("")}</div>
    <details class="tech sub"><summary>技术详情 · 数据来源 / 审计信息</summary><div class="kv">${tr.join("")}</div></details>
  </div>`;
  return mode==="dock"?content:c2BarHTML(it,(C2.prov&&C2.prov.meta)?C2.prov.meta(it):"","main")+content;
}
const ACTIVITY_D2={
  idOf:it=>it.id||it.item_id,
  name:it=>it.name||it.display_name||it.id,
  body:amD2Body,
  meta:it=>`${it.activity_type?`<span class="skin-tag">${esc(it.activity_type)}</span>`:""}<span class="c2-no">活动ID ${esc(it.item_id??it.id)}</span>`
};
if(ACTIVITY_BOARD){
  document.addEventListener("click",e=>{
    const yb=e.target.closest("[data-am-year]");
    if(yb){e.preventDefault();amSetYear(yb.getAttribute("data-am-year"));return;}
    const mb=e.target.closest("[data-am-monthsel]");
    if(mb){e.preventDefault();amSetMonthSel(mb.getAttribute("data-am-monthsel"));return;}
    const more=e.target.closest("[data-am-more]");
    if(more){e.preventDefault();AM_PAGE+=AM_PAGE_STEP;render();return;}
    const sb=e.target.closest("[data-am-status]");
    if(sb){e.preventDefault();amSetStatus(sb.getAttribute("data-am-status"));}
  });
  document.addEventListener("keydown",e=>{
    if(e.key!=="Enter"&&e.key!==" ")return;
    const row=e.target.closest&&e.target.closest(".am-row");
    if(!row)return;
    e.preventDefault();
    const i=parseInt(row.dataset.cidx||"-1",10);
    if(i>=0&&C2.chips[i])c2Open(i);
  });
}

/* ════════════════════ 无人机板「经典服名册 · 按类别分区」（2026-11-02 第二次口径）
   源修正：CBG 18xxxx 里的 181xxx 是无人机模块（能量核心/发动机/结构框架/导航仪），
   旧版整段并入把 60 条模块混进机体名册，已从源数据剔除（227 行 = 49 简单服 + 178 经典服卡）。
   经典服 all_equips 没有 kind 字段：生成器按机体文案「X无人机」/名称家族前缀推导 kind，
   并写 kind_source（desc/name-prefix/fallback）留痕；渲染只读数据，不再猜类型。
   同名合并：简单服记录补类型/品级，并让位一条 id 最小的经典行 → 179 条、21 个类别。
   ★ 类名统一 ds-*，样式挂 body.b-drone_catalog，其它板零影响。 */
const DRONE_BOARD=(function(){try{return (getParam("b")||"")==="drone_catalog";}catch(e){return false;}})();
const DRONE_CLASSIC_KIND="经典服收录";
const DRONE_GRADE_CLS={"基础":"g-绿","进阶":"g-蓝","高阶":"g-紫","典藏":"g-金"};
const DRONE_CAT_ORDER=["基础","医疗","战斗","战虎","负重","自爆","采集","战辅","盾补","守卫",
  "光盾","电弧","飞猪","镭蛇","狡兔","灵龙","猎犬","火凤","奔马","晶蝶","其他机体","机体部件"];
const DRONE_KIND_SRC={desc:"机体说明推导","name-prefix":"名称前缀推导",name:"名称推导",fallback:"其他/未归类",module:"部件名归类"};

/* 同名合并：每个有简单服记录的经典服名字只让位一行（id 最小的 18x 行），
   其余变体保留；简单服记录补进 kind/grade/power，供卡面与 D2 使用。 */
function droneUnified(items){
  const isCl=it=>String(it.server_branch||"").startsWith("经典服")||String(it.kind||"")===DRONE_CLASSIC_KIND;
  const classic=items.filter(isCl);
  const simple=items.filter(it=>!isCl(it));
  const byName=new Map();
  for(const it of classic){
    const n=String(it.name||"");
    if(!byName.has(n))byName.set(n,[]);
    byName.get(n).push(it);
  }
  const simpByName=new Map();
  for(const s of simple)simpByName.set(String(s.name||""),s);
  const drop=new Set();
  for(const [n,rows] of byName){
    const s=simpByName.get(n);
    if(!s)continue;
    rows.sort((a,b)=>Number(a.drone_id||0)-Number(b.drone_id||0));
    drop.add(rows[0]);            // 同名经典行让位给简单服完整记录
  }
  const out=simple.slice();
  for(const it of classic){
    if(drop.has(it))continue;
    const s=simpByName.get(String(it.name||""));
    out.push(s&&s.kind?Object.assign({},it,{kind:s.kind,grade:s.grade,power:s.power,grade_level:s.grade_level,__enriched:true}):it);
  }
  out.sort((a,b)=>String(a.name||"").localeCompare(String(b.name||""),"zh")
    ||Number(a.drone_id||0)-Number(b.drone_id||0));
  return out;
}
function droneCatRank(k){
  const i=DRONE_CAT_ORDER.indexOf(k);
  return i<0?999:i;
}
/* 按类别分组：类别顺序固定（基础→…→其他机体），同类别内保持名称序 */
function droneGroups(list){
  const m=new Map();
  for(const it of list){
    const k=String(it.kind||"其他机体");
    if(!m.has(k))m.set(k,[]);
    m.get(k).push(it);
  }
  return [...m.entries()].sort((a,b)=>
    droneCatRank(a[0])-droneCatRank(b[0])||b[1].length-a[1].length);
}
/* 统一行卡：图 + 名字 + 编号 +（有则）品级；类别由所属分区标题表达，行内不再重复 */
function droneRow(it,cidx,dup){
  const im=((it._media&&it._media.images)||[])[0];
  const grade=String(it.grade||"");
  const tags=[];
  if(grade)tags.push(`<span class="grade-pill ds-grade ${DRONE_GRADE_CLS[grade]||""}">${esc(grade)}</span>`);
  return `<div class="i roster ds-crow${dup?" ds-dup":""}" data-cidx="${cidx}">
    <span class="ds-crow-fig${im?"":" ds-empty"}">${im?`<img src="${esc(im.png)}" alt="" loading="lazy">`:'<span class="ds-fig-ph">无</span>'}</span>
    <span class="ds-crow-main">
      <span class="ds-crow-name"><span class="ds-crow-nm">${esc(it.name||it.id)}</span>${dup?'<span class="ds-dup-tag">同名列</span>':""}</span>
      <span class="ds-crow-meta"><span class="ds-crow-id">${esc(it.drone_id??it.id)}</span>${tags.join("")}</span>
    </span>
  </div>`;
}
/* D2 详情卡：与网格卡解耦（同一 id 只缓存这一份），字段平铺，不再逐卡重复审计标签 */
function droneD2Html(it){
  const kind=String(it.kind||"");
  const isClassic=String(it.server_branch||"").startsWith("经典服");
  const kindSrc=DRONE_KIND_SRC[String(it.kind_source||"")]||"";
  const im=(it._media&&it._media.total)?renderItemMedia(it._media):"";
  const rows=[];
  const put=(k,v)=>{if(v==null||String(v)==="")return;rows.push([k,String(v)]);};
  put("类型",kind?(kind+(kindSrc?`（${kindSrc}）`:"")):(isClassic?"经典服收录（类型未标注）":""));
  if(it.grade!=null)put("品级",it.grade);
  if(it.power!=null)put("评分基数",it.power+"（静态表 base_score，不等同实机面板战力）");
  if(it.desc)put("机体说明",it.desc);
  if(Array.isArray(it.function_tips)&&it.function_tips.length)put("功能提示",it.function_tips.join("、"));
  if(Array.isArray(it.skills)&&it.skills.length)put("技能",fmtVal("skills",it.skills));
  if(Array.isArray(it.talents)&&it.talents.length)put("账号级科技",fmtVal("talents",it.talents));
  if(it.talent_scope)put("科技口径",it.talent_scope);
  if(it.obtain_note)put("获取",it.obtain_note);
  if(it.released_cbg!=null)put("藏宝阁白名单",it.released_cbg?"在名单内（不等于当前可得）":"不在名单内");
  if(it.model)put("模型",it.model);
  if(it.monster_id!=null)put("怪物 ID",it.monster_id);
  if(it.module_id!=null)put("模块 ID",it.module_id);
  if(it.normal_attack_skill_id!=null)put("普攻技能",it.normal_attack_skill_id);
  if(it.classic_ref)put("经典服对照",fmtVal("classic_ref",it.classic_ref));
  if(it.server_branch)put("服型",it.server_branch);
  if(Array.isArray(it.server_branches)&&it.server_branches.length)put("服型并集",it.server_branches.join("、"));
  if(it.skills_note&&isClassic)put("技能口径",it.skills_note);
  put("证据等级",EV_CN[it.evidence]||it.evidence||"");
  if(Array.isArray(it.status_tags)&&it.status_tags.length)
    put("状态标签",it.status_tags.map(t=>STATE_CN[t]||COMMON_VAL_CN[t]||t).join("、"));
  put("来源",it.source);
  const kv=rows.map(([k,v])=>`<div class="k">${esc(k)}</div><div class="v">${esc(v).replace(/\n/g,"<br>")}</div>`).join("");
  return `<div class="i roster ds-detail">
    ${im}
    <div class="i-head"><div><div class="i-name">${esc(it.name||it.id)}</div>
      <div class="i-id">机体 ID ${esc(it.drone_id??it.id)}</div></div></div>
    <div class="i-detail" hidden><div class="kv">${kv}</div></div>
  </div>`;
}
function droneShelfRender(items,g){
  const list=droneUnified(items);
  C2.prov=ROSTER_D2;C2.chips=list;C2.html={};
  for(const it of list)C2.html[c2IdOf(it)]=droneD2Html(it);
  const cnt={},idx=new Map();
  list.forEach((it,i)=>{
    const n=String(it.name||"");
    cnt[n]=(cnt[n]||0)+1;
    idx.set(it,i);
  });
  const groups=droneGroups(list);
  const chips=groups.map(([k,arr],i)=>
    `<a class="ds-chip" href="#ds-cat-${i}">${esc(k)}<b>${arr.length}</b></a>`).join("");
  const secs=groups.map(([k,arr],i)=>{
    const rows=arr.map(it=>droneRow(it,idx.get(it),cnt[String(it.name||"")]>1)).join("");
    return `<section class="ds-cat" id="ds-cat-${i}">
      <div class="ds-cat-hd"><span class="ds-cat-name">${esc(k)}</span><span class="ds-cat-n">${arr.length} 条</span></div>
      <div class="ds-roster">${rows}</div>
    </section>`;
  }).join("");
  g.innerHTML=`<div class="ds-nav">
    <div class="ds-nav-hd">
      <span class="ds-nav-title">经典服无人机名册</span>
      <span class="ds-nav-sub">${list.length} 条 · ${groups.length} 个类别 · 按类别分区 · 同名并列已标记</span>
    </div>
    <nav class="ds-chips" aria-label="类别索引">${chips}</nav>
    <div class="ds-nav-note">类型不是 CBG 源字段：由机体说明「X无人机」或名称家族前缀推导（kind_source 留痕）；181xxx 能量核心/发动机/结构框架/导航仪属零部件，按名称归入「机体部件」类别保留。</div>
  </div>${secs}`;
  if(C2.open)c2Resync();
}

/* ═══════════════════════════════════════════════════════════════════
   影音资源板（board id = media_catalog，2026-11-02）
   左：分类树（音频按样本名前缀 / 视频按还原目录，仅导航，不是官方分类）
   右：常驻播放器 + 队列列表（整组入队 / 连播 / 倍速）
   数据：data/boards/media_catalog.js；音频 mp3 在 20_提取/影音/audio，
        视频直接引用 41_还原树 内 mp4（都不复制进 web）。
   ═══════════════════════════════════════════════════════════════════ */
const ML={cat:"all-audio",q:"",queue:[],qi:-1,auto:false,speed:1,limit:200,catNames:{},built:false};
function mlN(n){return Number(n||0).toLocaleString("zh-CN");}
function mlVisible(){
  let arr=ML.items||[];
  if(ML.cat==="all-audio")arr=arr.filter(x=>x.kind==="a");
  else if(ML.cat==="all-video")arr=arr.filter(x=>x.kind==="v");
  else arr=arr.filter(x=>x.category===ML.cat);
  const q=ML.q.toLowerCase();
  if(q)arr=arr.filter(x=>String(x.name||"").toLowerCase().includes(q)||String(x.file_stem||"").toLowerCase().includes(q));
  return arr;
}
function mlPlayers(){
  return {a:document.getElementById("mlAudio"),v:document.getElementById("mlVideo")};
}
function mlMsg(t){const el=document.getElementById("mlMsg");if(!el)return;el.textContent=t||"";el.style.display=t?"block":"none";}
function mlMarkRow(){
  document.querySelectorAll("#mlList .ml-row").forEach(el=>{
    el.classList.toggle("on",Number(el.dataset.i)===ML.qi);
    el.classList.toggle("playing",Number(el.dataset.i)===ML.qi);
  });
}
function mlSetNow(it){
  const t=document.getElementById("mlTitle"),s=document.getElementById("mlSub"),p=document.getElementById("mlPos");
  if(!t)return;
  if(!it){t.textContent="未选择条目";s.textContent="从右侧列表点一条开始";if(p)p.textContent="";return;}
  t.textContent=it.name;
  const cat=ML.catNames[it.category]||it.category||"";
  s.textContent=cat+(it.kind==="v"?" · 视频":" · 音频")+(it.kind==="a"?(it.extracted?"":" · 待提取"):"");
  if(p)p.textContent=ML.queue.length?`队列 ${ML.qi+1} / ${ML.queue.length}`:"";
}
function mlToggleLabel(){
  const {a,v}=mlPlayers();
  const it=ML.queue[ML.qi];
  const el=it&&it.kind==="v"?v:a;
  const btn=document.getElementById("mlToggle");
  if(!btn)return;
  const playing=el&&!el.paused&&!el.ended;
  btn.textContent=playing?"暂停":"播放";
  const wave=document.getElementById("mlWave");
  if(wave)wave.classList.toggle("playing",!!playing);
}
function mlPlayAt(i,queue){
  const arr=queue||mlVisible();
  if(!arr.length)return;
  ML.queue=arr;
  ML.qi=Math.max(0,Math.min(i,arr.length-1));
  const it=arr[ML.qi];
  const {a,v}=mlPlayers();
  mlSetNow(it);
  if(it.kind==="v"){
    a.pause();a.removeAttribute("src");a.style.display="none";a.load();
    v.style.display="block";
    v.src=encodeURI(it.media_path);v.load();v.playbackRate=ML.speed;
    mlMsg("");
    v.play().catch(()=>mlMsg("视频无法播放：请确认文件存在，且以本地文件方式打开本页。"));
  }else{
    v.pause();v.removeAttribute("src");v.style.display="none";v.load();
    if(!it.extracted){
      a.pause();a.removeAttribute("src");a.style.display="none";a.load();
      mlMsg("该样本尚未转码（待提取）。原音在 FSB5 音库中，运行 tools/convert_audio_to_mp3.py 后即可播放。");
    }else{
      a.style.display="block";
      a.src=encodeURI(it.media_path);a.load();a.playbackRate=ML.speed;
      mlMsg("");
      a.play().catch(()=>mlMsg("音频无法播放：请确认文件存在，且以本地文件方式打开本页。"));
    }
  }
  mlMarkRow();
  setTimeout(mlToggleLabel,30);
}
function mlRenderCats(){
  const box=document.getElementById("mlCats");if(!box)return;
  const cats=(DATA.meta.categories||[]);
  const a=cats.filter(c=>c.kind==="a"),v=cats.filter(c=>c.kind==="v");
  const c=DATA.meta.counts||{};
  const btn=(id,name,count)=>`<button type="button" class="ml-cat ${ML.cat===id?"on":""}" data-cat="${esc(id)}"><span>${esc(name)}</span><em>${mlN(count)}</em></button>`;
  box.innerHTML=
    `<div class="ml-group"><div class="ml-group-hd">音频 <span>${mlN(c.audio)}</span></div>`+
    btn("all-audio","全部音频",c.audio)+a.map(x=>btn(x.id,x.name,x.count)).join("")+`</div>`+
    `<div class="ml-group"><div class="ml-group-hd">视频 <span>${mlN(c.video)}</span></div>`+
    btn("all-video","全部视频",c.video)+v.map(x=>btn(x.id,x.name,x.count)).join("")+`</div>`;
}
function mlRenderList(){
  const list=document.getElementById("mlList");if(!list)return;
  const arr=mlVisible();
  const titleEl=document.getElementById("mlListTitle"),cntEl=document.getElementById("mlListCount");
  if(titleEl)titleEl.textContent=ML.cat==="all-audio"?"全部音频":ML.cat==="all-video"?"全部视频":(ML.catNames[ML.cat]||ML.cat);
  if(cntEl)cntEl.textContent=`${mlN(arr.length)} 条`+(ML.q?` · 搜索「${ML.q}」`:"");
  const limit=Math.min(ML.limit,arr.length);
  let html="";
  for(let i=0;i<limit;i++){
    const it=arr[i];
    const tag=ML.catNames[it.category]||it.category||"";
    const st=it.kind==="a"?(it.extracted?`<span class="ml-st ok">可播放</span>`:`<span class="ml-st wait">待提取</span>`):`<span class="ml-st vid">视频</span>`;
    html+=`<div class="ml-row${ML.qi>=0&&ML.queue[ML.qi]===it?" on":""}" data-i="${i}" title="${esc(it.name)}">`+
      `<span class="ml-ic">${it.kind==="a"?"♪":"▶"}</span>`+
      `<span class="ml-name">${esc(it.name)}</span>`+
      `<span class="ml-tag">${esc(tag)}</span>${st}`+
      `<span class="ml-go">播放</span></div>`;
  }
  list.innerHTML=html||`<div class="ml-empty">该分类下没有匹配条目</div>`;
}
function mlRefresh(){mlRenderCats();mlRenderList();}
function mediaLibraryRender(items){
  ML.items=items;
  const grid=document.getElementById("grid");
  const ctr=document.querySelector(".controls");
  if(ctr)ctr.style.display="none";
  const m=DATA.meta||{};
  if(!ML.built||!grid.querySelector("#mlWrap")){
    ML.catNames={};(m.categories||[]).forEach(c=>ML.catNames[c.id]=c.name);
    grid.innerHTML=
      `<div class="ml-wrap" id="mlWrap">`+
      `<aside class="ml-tree">`+
        `<div class="ml-tree-hd"><b>影音资源库</b><span>音频 ${mlN((m.counts||{}).audio)} · 视频 ${mlN((m.counts||{}).video)}</span></div>`+
        `<div class="ml-search"><input id="mlQ" type="search" placeholder="搜索条目名…" autocomplete="off"><button type="button" id="mlQClear" aria-label="清空">×</button></div>`+
        `<div class="ml-groups" id="mlCats"></div>`+
        `<div class="ml-tree-note">分类按样本名前缀 / 视频目录粗分组，仅作导航，不是官方分类。</div>`+
      `</aside>`+
      `<main class="ml-main">`+
        `<section class="ml-player">`+
          `<div class="ml-now"><div class="ml-kicker">正在播放</div><div class="ml-title" id="mlTitle">未选择条目</div><div class="ml-sub" id="mlSub">从右侧列表点一条开始</div></div>`+
          `<div class="ml-stage"><div class="ml-wave" id="mlWave">${Array.from({length:36},(_,i)=>`<i style="height:${18+(i*37)%64}%"></i>`).join("")}</div>`+
            `<audio id="mlAudio" controls preload="none" style="display:none"></audio>`+
            `<video id="mlVideo" controls playsinline preload="none" style="display:none"></video>`+
            `<div class="ml-msg" id="mlMsg" style="display:none"></div></div>`+
          `<div class="ml-ctl">`+
            `<button type="button" class="ml-btn" id="mlPrev">上一首</button>`+
            `<button type="button" class="ml-btn primary" id="mlToggle">播放</button>`+
            `<button type="button" class="ml-btn" id="mlNext">下一首</button>`+
            `<span class="ml-speed"><label for="mlSpeed">倍速</label><select id="mlSpeed"><option value="0.5">0.5×</option><option value="0.75">0.75×</option><option value="1" selected>1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option><option value="2">2×</option></select></span>`+
            `<label class="ml-auto"><input type="checkbox" id="mlAuto"> 连播</label>`+
            `<span class="ml-pos" id="mlPos"></span>`+
          `</div>`+
        `</section>`+
        `<section class="ml-listbox">`+
          `<div class="ml-list-head"><div><b id="mlListTitle">全部音频</b> <span id="mlListCount"></span></div>`+
            `<div class="ml-list-actions"><button type="button" id="mlQueueAll">整组入队</button><button type="button" id="mlRandom">随机一首</button></div></div>`+
          `<div class="ml-list" id="mlList"></div>`+
          `<button type="button" class="ml-more" id="mlMore">加载更多</button>`+
        `</section>`+
      `</main></div>`;
    mlBind();
    ML.built=true;
  }
  mlRefresh();
}
function mlBind(){
  const wrap=document.getElementById("mlWrap");if(!wrap)return;
  wrap.addEventListener("click",e=>{
    const cat=e.target.closest(".ml-cat");
    if(cat){ML.cat=cat.dataset.cat;ML.limit=200;mlRefresh();return;}
    const row=e.target.closest(".ml-row");
    if(row){mlPlayAt(Number(row.dataset.i),mlVisible());return;}
  });
  const q=document.getElementById("mlQ");
  if(q)q.addEventListener("input",()=>{ML.q=q.value.trim();ML.limit=200;mlRenderList();});
  const qc=document.getElementById("mlQClear");
  if(qc)qc.addEventListener("click",()=>{ML.q="";if(q)q.value="";ML.limit=200;mlRenderList();});
  const more=document.getElementById("mlMore");
  if(more)more.addEventListener("click",()=>{ML.limit+=200;mlRenderList();});
  const qa=document.getElementById("mlQueueAll");
  if(qa)qa.addEventListener("click",()=>{const arr=mlVisible();if(arr.length)mlPlayAt(0,arr);});
  const rnd=document.getElementById("mlRandom");
  if(rnd)rnd.addEventListener("click",()=>{const arr=mlVisible();if(arr.length)mlPlayAt(Math.floor(Math.random()*arr.length),arr);});
  const prev=document.getElementById("mlPrev");
  if(prev)prev.addEventListener("click",()=>{
    if(!ML.queue.length)return mlPlayAt(0,mlVisible());
    mlPlayAt(ML.qi<=0?ML.queue.length-1:ML.qi-1,ML.queue);
  });
  const next=document.getElementById("mlNext");
  if(next)next.addEventListener("click",()=>{
    if(!ML.queue.length)return mlPlayAt(0,mlVisible());
    mlPlayAt((ML.qi+1)%ML.queue.length,ML.queue);
  });
  const tg=document.getElementById("mlToggle");
  if(tg)tg.addEventListener("click",()=>{
    const it=ML.queue[ML.qi];
    if(!it)return mlPlayAt(0,mlVisible());
    const {a,v}=mlPlayers();
    const el=it.kind==="v"?v:a;
    if(el.paused)el.play().catch(()=>{});else el.pause();
  });
  const sp=document.getElementById("mlSpeed");
  if(sp)sp.addEventListener("change",()=>{
    ML.speed=Number(sp.value)||1;
    const {a,v}=mlPlayers();a.playbackRate=ML.speed;v.playbackRate=ML.speed;
  });
  const au=document.getElementById("mlAuto");
  if(au)au.addEventListener("change",()=>{ML.auto=au.checked;});
  const {a,v}=mlPlayers();
  const ended=()=>{
    mlToggleLabel();
    if(ML.auto&&ML.qi+1<ML.queue.length)mlPlayAt(ML.qi+1,ML.queue);
    else mlToggleLabel();
  };
  if(a){a.addEventListener("ended",ended);a.addEventListener("play",mlToggleLabel);a.addEventListener("pause",mlToggleLabel);}
  if(v){v.addEventListener("ended",ended);v.addEventListener("play",mlToggleLabel);v.addEventListener("pause",mlToggleLabel);}
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
  /* CDN 资源库 / 本地还原树：自带的「可切换展示视图」（?view=xxx）。
     ★ 必须拦在大表分支（HUGE_TABLE_MIN=15000）之前 ——
       local_restore_tree 有 33,601 条，若落进 hugeDraw 就会变成 3 万张卡片。
     ★ 筛选口径与通用路径一致：证据等级 + 板级自定义筛选（meta.filters）+ 搜索框。 */
  if(CDN_BOARD||TREE_BOARD){
    const vItems=viewFilterItems();
    if(CDN_BOARD)cdnRender(vItems); else treeRender(vItems);
    return;
  }
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
    /* 基因板：按服别 Tab 过滤 —— 两服绝不混排（overview 的 branch=null 表示不过滤） */
    if(GENE_BOARD&&!geneInServer(it,geneServerDef().branch))return false;
    if(EDIBLE_BOARD && !edibleShowIngredients && String(it.kind||"")==="食材")return false;
    if(fe&&it.evidence!==fe)return false;
    if(FASHION_BOARD&&!frPass(it))return false;
    if(VEHICLE_BOARD&&!vPass(it))return false;
    if(CHIP_BOARD&&!cPass(it))return false;
    if(partFilter.length&&!partFilter.includes(String(it.part??"")))return false;
    if(Array.isArray(DATA._custFilters)){
      for(const cf of DATA._custFilters){
        const v=cf.sel?cf.sel.value:"";
        if(!v)continue;
        /* 数组/多值字段走 test 回调；其余按字段等值比较 */
        if(typeof cf.test==="function"){if(!cf.test(it,v))return false;continue;}
        /* __none__ = 「该字段在源表里没登记」，与「空值不过滤」区分开 */
        if(v==="__none__"){if(String(it[cf.key]??"")!=="")return false;continue;}
        if(String(it[cf.key]??"")!==v)return false;
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
  if(PIECEWISE){ pwRender(items); return; }
  if(SCENE_TABLE){ sbRender(items); return; }
  if(MEDIA_BOARD||(DATA&&DATA.meta&&DATA.meta.board_mode==="media_library")){ mediaLibraryRender(items); return; }
  if(ST_TABLE){ stRender(items); return; }
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
  const droneList=DRONE_BOARD?droneUnified(items):null;
  const droneTotal=DRONE_BOARD?droneUnified(DATA.items).length:0;
  const countEl=document.getElementById("count");
  const countHtml=DRONE_BOARD
    ? `显示 ${droneList.length} / ${droneTotal} 条 · ${new Set(droneList.map(it=>String(it.kind||""))).size} 个类别 · 经典服名册（含 181xxx 机体部件）`
    : FASHION_BOARD
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
  if(GENE_BOARD)countEl.innerHTML=geneCountText(items);
  if(FASHION_BOARD)frPills(items);
  if(VEHICLE_BOARD)vPills(items);
  if(CHIP_BOARD)cPills(items);
  /* 基因板：两服总览只给服别入口，不铺条目（避免两服混排） */
  if(GENE_BOARD&&GENE_SERVER==="overview"){geneOverviewRender(g,items);return;}
  if(!items.length){
    g.innerHTML=GENE_BOARD?(geneTabsHTML()+'<div class="empty">无匹配条目</div>'):'<div class="empty">无匹配条目</div>';
    return;
  }
  /* 无人机板：统一经典服式名册（2026-11-02） */
  if(DRONE_BOARD){droneShelfRender(items,g);return;}
  if(ACTIVITY_BOARD){amRenderLedger(g,items,q,fe);return;}
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
    /* 同 model 索引：★ 用【未过滤】的 items 建（不受全局筛选影响），并挂整条 item 供跳转 */
    window.FR_MODEL_INDEX={};
    window.FR_ITEM_BY_ID={};
    for(const _it of ((DATA&&DATA.items)||items)){
      window.FR_ITEM_BY_ID[String(_it.id)]=_it;
      const _m=(_it.model_id!=null)?String(_it.model_id):null;
      if(!_m)continue;
      const _png=(((_it._media||{}).images||[])[0]||{}).png||"";
      (window.FR_MODEL_INDEX[_m]=window.FR_MODEL_INDEX[_m]||[]).push({id:_it.id,name:_it.name,part:_it.part,grade:_it.grade_level,png:_png});
    }
    C2.prov=FR_D2;C2.chips=frList;C2.html={};C2.htmlFull={};
    /* 深链：?d2=<卡id> 直接打开该卡的详情（也方便实测/分享某一子卡） */
    const _d2id=(function(){try{return getParam("d2");}catch(e){return "";}})();
    if(_d2id){
      const _di=frList.findIndex(x=>String(c2IdOf(x))===String(_d2id));
      if(_di>=0) setTimeout(()=>{try{c2Open(_di);
        const _openAll=(function(){try{return getParam("art");}catch(e){return "";}})()==="1";
        if(_openAll){
          document.querySelectorAll(".fr-artbox,.fr-sibbox").forEach(d=>d.open=true);
        }}catch(e){}},60);
    }
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
    : CORE_BOARD&&(orderBy==="code_asc"||orderBy==="code_desc")
    ? [...items].sort((a,b)=>orderBy==="code_asc"
        ? Number(a.item_id||0)-Number(b.item_id||0)
        : Number(b.item_id||0)-Number(a.item_id||0))
    : items;
  /* 称号板：分组由「按获取途径分组」勾选项控制；未勾选时整表按编号排，勾选后组内按编号排。
     注意 list 可能还是 items 本体（默认路径），这里只改顺序、不改集合。 */
  if(TITLE_BOARD){
    const st=sortState();
    const sign=st.dir==="asc"?1:-1;
    if(titleGroupOn){
      list.sort((a,b)=>titleGroupOrder(titleGroupKey(a))-titleGroupOrder(titleGroupKey(b))
        ||sign*(Number(a.item_id||0)-Number(b.item_id||0)));
    }else{
      list.sort((a,b)=>sign*(Number(a.item_id||0)-Number(b.item_id||0)));
    }
  }
  /* 头像板：先类型分组、组内按标号（item_id）；默认大 → 小。 */
  if(AVATAR_BOARD){
    const st=sortState();
    list.sort((a,b)=>avatarSort(a,b,st.dir==="asc"?1:-1));
  }
  let lastTitleGroup="";
  let edHeadShown=false;
  /* 2026-10-30：核芯板全量入 chips——基础（绿）核芯（家园守卫限定 4 条）无 skill_desc/升星段，
     之前按 rank_star_segments 过滤会把它们漏出 D2，且走普通 kv 卡分支格式乱 */
  const coreList=CORE_BOARD?list.slice():null;
  if(CORE_BOARD){C2.prov=CORE_D2;C2.chips=coreList;C2.html={};}
  /* 2026-10-29：名册类板（击败播报/头像头像框名片框等 card_mode=roster）接 D2 子卡。
     注意：mutation_core_full 的 meta 也带 card_mode:"roster"（核芯板初建时基于名册体系），
     核芯板必须保持 CORE_D2，否则 provider 被覆盖回旧版网格卡直嵌（2026-10-30 修复） */
  const rosterBoard=!CORE_BOARD&&String(DATA.meta&&DATA.meta.card_mode)==="roster";
  if(rosterBoard){C2.prov=GENE_BOARD?GENE_D2:ROSTER_D2;C2.chips=list;C2.html={};}
  /* 2026-11-02：装备属性四卡接 D2 —— 卡面点击打开自建详情（equipD2Body） */
  if(EQUIP_BOARD){C2.prov=EQUIP_D2;C2.chips=list;}
  /* 基因板：卡面换成「族色条 + 名字 + Lv/分值或档位 + 效果」的紧凑卡，按服别 Tab 重排 */
  const cardHTMLs=list.map((it,i)=>{
    if(GENE_BOARD){const h=geneCardHTML(it,i);C2.html[c2IdOf(it)]=h;return h;}
    /* 2026-11-02：装备属性四卡按「人物时装同款」卡面渲染 */
    if(EQUIP_BOARD)return equipCardHTML(it,i);
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
      /* 简略卡面（2026-11-02）：品级 pill 左对齐贴卡边 + 武器类型同排；核芯属性在名字后；其余全部折进详情 */
      const sum=[];
      if(it.grade_clean||it.grade_label){
        const gl=it.grade_label||it.grade_clean;
        const gc=it.grade_color?` g-${esc(it.grade_color)}`:"";
        sum.push(`<span class="grade-pill${gc}">${esc(gl)}</span>`);
      }
      if(it.weapon_type_display)sum.push(`<span class="core-wt">${esc(it.weapon_type_display)}</span>`);
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
      bodyHtml=`<div class="core-meta">${sum.join("")}</div>`+
        `<div class="i-detail" hidden><div class="kv">${det.join("")}</div>`+
        `${extraBlock}${techBlock}</div>`;
    }else if(rosterMode){
      /* 名册类板（meta.card_mode="roster"）：卡面只留 图轨(≤4 张) + 名字 + 编号(head) +
         meta.card_summary 声明的字段；其余字段、礼包逐条说明、溯源全部折进点开的详情区 */
      const sum=[];
      (Array.isArray(DATA.meta.card_summary)?DATA.meta.card_summary:[]).forEach(p=>{
        const k=p[0],label=p[1],v=it[k];if(v==null||v==="")return;
        /* 称号板：卡头已有「称号名 + 称号ID」，不再重复 name 行（1539 条时省掉整行冗余） */
        if(TITLE_BOARD&&k==="name")return;
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
      /* 料理板：卡面已用 card_summary 展示的字段（名称/类别/效果/制作设施）不再在详情里重复一遍 */
      const edSumKeys=EDIBLE_BOARD?new Set((Array.isArray(DATA.meta.card_summary)?DATA.meta.card_summary:[]).map(p=>p[0])):null;
      const rRows=extra.filter(p=>!hideSet.has(p[0])&&p[0]!=="gift_items"&&!(Array.isArray(p[1])&&!p[1].length)
          &&!(edSumKeys&&edSumKeys.has(p[0]))).map(([k,v])=>
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
        <div><div class="i-name${TITLE_BOARD&&it.art_png?" has-art":""}">${TITLE_BOARD?titleName(it):esc(it.name||it.display_name||it.id)}${nucleusMode&&it.element?`<span class="i-elem" data-el="${esc(it.element)}" title="核芯属性">${esc(it.element)}</span>`:""}${it.ip?`<span class="tag-ip">${esc(it.ip)}</span>`:""}</div>
        ${referenceTitle(it.reference_fields)}
        <div class="i-id" title="id">${nucleusMode||rosterMode?`${esc(DATA.meta.id_label||"道具ID")} ${esc(it.item_id??it.id)}`:`${esc(it.id)}`}</div>
        ${TITLE_BOARD?titleBadges(it):""}</div>
        <span class="head-tags">${nucleusMode?"":`<span class="ev ${it.evidence}">${EV_CN[it.evidence]||it.evidence}</span>${it.image_status?`<span class="ev gap" title="${esc(it.image_note||"该资源在当前包快照中不可得")}">${esc(it.image_status)}</span>`:""}${renderStateTags(it.status_tags)}`}</span>
      </div>
      ${bodyHtml}
    </div>`;
    if(CORE_BOARD&&nucleusMode)C2.html[c2IdOf(it)]=html;
    if(rosterMode)C2.html[c2IdOf(it)]=html;
    /* 称号板：分组头随卡片一起进网格（grid-column:1/-1），位置和数据顺序同源 */
    let tgHead="";
    if(TITLE_BOARD&&titleGroupOn){
      const gk=titleGroupKey(it);
      if(i===0||gk!==lastTitleGroup){
        lastTitleGroup=gk;
        const n=list.filter(x=>titleGroupKey(x)===gk).length;
        tgHead=`<div class="tg-head" data-tg="${esc(gk||"none")}"><span class="tg-name">${esc(titleGroupLabel(gk))}</span><span class="tg-n">${n} 条</span></div>`;
      }
    }
    let edHead="";
    if(EDIBLE_BOARD&&edibleShowIngredients&&String(it.kind||"")==="食材"&&!edHeadShown){
      edHeadShown=true;
      const n=list.filter(x=>String(x.kind||"")==="食材").length;
      edHead=`<div class="tg-head ed-head"><span class="tg-name">食材 / 可食用物品</span><span class="tg-n">${n} 条</span></div>`;
    }
    return edHead+tgHead+html;
  });
  g.innerHTML=GENE_BOARD?geneBoardHTML(list,cardHTMLs):cardHTMLs.join("");
  if((CORE_BOARD||rosterBoard||EQUIP_BOARD||GENE_BOARD)&&C2.open)c2Resync();
  if(TITLE_BOARD)syncTitleHeadTop();
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
/* limit=0 表示不翻页（空成员期次也要全部出现）；仅 period_empty=show 的板用这种模式 */
function pSet(k,v){window.PF[k]=v; if(k!=="limit")window.PF.limit=pNoCap()?0:40; render();}
function pNoCap(){return !!window.PF_EMPTY;}
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
function pToggleEmpty(k){window.PF.openEmpty=PF.openEmpty||{};PF.openEmpty[k]=!PF.openEmpty[k];render();}
function periodStatus(p){
  const t=new Date(); const s=p.start?new Date(p.start+"T00:00:00"):null;
  const e=p.end?new Date(p.end+"T23:59:59"):null;
  if(s&&t<s)return {k:"upcoming",txt:"即将开始"};
  if(e&&t>e)return {k:"ended",txt:"已结束"};
  return {k:"on",txt:"当期"};
}
/* ════════════════ 期次时间轴 + 奖池抽屉（仅本板，meta.period_empty="show"）════════════════
   布局 = 年度时间轴（年 → 月 → 期次），空期次在月内压成一行摘要；
   点期次不再就地展开，改为右侧抽屉看奖池成员（成员带图）。*/
function ptPick(id){PF.sel=(PF.sel===id?null:id);render();}
function ptClose(){PF.sel=null;render();}
function ptMonth(k){PF.month=PF.month||{};PF.month[k]=!PF.month[k];render();}
function ptYear(y){PF.year=y;PF.month={};PF.sel=null;render();}
/* 构建期查不到名字时会回退成「道具 <id>」，这是数据缺口，不是正式名 */
const PT_UNRES=/^道具\s*\d+$/;
function renderPeriodTimeline(periods,byPeriod,list,cleanLabel){
  const FAM=p=>p.family||"—";
  const YR=p=>String(p.start||"").slice(0,4)||"—";
  const MO=p=>String(p.start||"").slice(5,7)||"—";
  const stOf=p=>{
    const t=new Date();
    const s=p.start?new Date(p.start+"T00:00:00"):null;
    const e=p.end?new Date(p.end+"T23:59:59"):null;
    if(!s&&!e)return{k:"unknown",txt:"无时间"};
    if(s&&t<s)return{k:"upcoming",txt:"即将开始"};
    if(e&&t>e)return{k:"ended",txt:"已结束"};
    if(!e)return{k:"longrun",txt:"长期在架"};
    return{k:"on",txt:"当期"};
  };
  const RANK={on:0,upcoming:1,longrun:2,ended:3,unknown:4};
  const qv=((document.getElementById("q")||{}).value||"").trim();
  const stCount={on:0,upcoming:0,longrun:0,ended:0,unknown:0};
  periods.forEach(p=>stCount[stOf(p).k]++);
  const withMembers=periods.filter(p=>(byPeriod[p.period_id]||[]).length).length;
  const fams=[...new Set(periods.map(FAM))];
  const kinds=[...new Set(list.map(i=>i.kind).filter(Boolean))];
  const years=[...new Set(periods.map(YR))].sort((a,b)=>(Number(b)||-1)-(Number(a)||-1));
  if(!years.includes(PF.year))PF.year=years[0]||"—";
  const chip=(label,n,active,fn)=>`<button class="pf-chip${active?" on":""}" onclick="${fn}">${label}${n!=null?` <b>${n}</b>`:""}</button>`;
  const optsHtml=(cur,arr)=>arr.map(o=>`<option value="${esc(o.v)}"${o.v===cur?" selected":""}>${esc(o.t)}</option>`).join("");
  const famOpts=[{v:"all",t:"全部家族"},...fams.map(f=>({v:f,t:`${f}（${periods.filter(p=>FAM(p)===f).length}）`}))];
  const kindOpts=[{v:"all",t:"全部类型"},...kinds.map(k=>({v:k,t:`${k}（${list.filter(i=>i.kind===k).length}）`}))];
  const bar=`<div class="pf-bar pf-bar-one">
    <span class="pf-label">状态</span>
    ${chip("全部",null,PF.status==="all","pSet('status','all')")}
    ${chip("当期",stCount.on,PF.status==="on","pSet('status','on')")}
    ${chip("即将开始",stCount.upcoming,PF.status==="upcoming","pSet('status','upcoming')")}
    ${chip("长期在架",stCount.longrun,PF.status==="longrun","pSet('status','longrun')")}
    ${chip("已结束",stCount.ended,PF.status==="ended","pSet('status','ended')")}
    ${stCount.unknown?chip("无时间",stCount.unknown,PF.status==="unknown","pSet('status','unknown')"):""}
    <span class="pf-sep"></span>
    <select class="pf-sel" title="按家族筛选" onchange="pSet('family',this.value)">${optsHtml(PF.family,famOpts)}</select>
    <select class="pf-sel" title="按奖励类型筛选" onchange="pSet('kind',this.value)">${optsHtml(PF.kind,kindOpts)}</select>
    <span class="pf-sep"></span>
    ${chip("只看有内容",withMembers,PF.only==="1","pSet('only','1')")}
    ${chip("全部期次",periods.length,PF.only==="0","pSet('only','0')")}
  </div>`;
  /* 当期条：只在「最新年份 + 未筛家族 + 未筛状态」时出现，不打断历史浏览 */
  const showNow=PF.status==="all"&&PF.family==="all"&&PF.year===years[0]&&qv==="";
  const nowP=showNow?periods.filter(p=>["on","upcoming"].includes(stOf(p).k))
    .sort((a,b)=>RANK[stOf(a).k]-RANK[stOf(b).k]||String(a.start||"").localeCompare(String(b.start||""))):[];
  const nowHtml=nowP.length?`<div class="pt-now">${nowP.map(p=>{
    const st=stOf(p), n=(byPeriod[p.period_id]||[]).length;
    return `<div class="pt-nowcard" onclick="ptPick('${p.period_id}')">
      <div class="ptnc-t">${esc(cleanLabel(p.label)||p.period_id)}</div>
      <div class="ptnc-d">${esc(p.start||"—")}${p.end?" → "+esc(p.end):""}</div>
      <div class="ptnc-m"><span class="pstate ${st.k}">${st.txt}</span><span class="pfam">${esc(FAM(p))}</span>
        <span class="ptnc-n">${n?n+" 件":"—"}</span></div></div>`;
  }).join("")}</div>`:"";
  const yearsHtml=`<div class="pt-years">${years.map(y=>{
    const n=periods.filter(p=>YR(p)===y).length;
    return `<button class="${y===PF.year?"on":""}" onclick="ptYear('${esc(y)}')">${esc(y)}<b>${n}</b></button>`;
  }).join("")}</div>`;
  const memOf=p=>{
    let m=byPeriod[p.period_id]||[];
    if(PF.kind!=="all")m=m.filter(x=>x.kind===PF.kind);
    return m;
  };
  const base=periods.filter(p=>YR(p)===PF.year)
    .filter(p=>PF.status==="all"||stOf(p).k===PF.status)
    .filter(p=>PF.family==="all"||FAM(p)===PF.family);
  const hideEmpty=PF.only==="1"||qv!=="";
  const months=[...new Set(base.map(MO))].sort((a,b)=>b.localeCompare(a));   // 新月份在前
  let body="";
  months.forEach(m=>{
    const rows=base.filter(p=>MO(p)===m)
      .sort((a,b)=>RANK[stOf(a).k]-RANK[stOf(b).k]||String(b.start||"").localeCompare(String(a.start||"")));
    const live=rows.filter(p=>memOf(p).length), dead=rows.filter(p=>!memOf(p).length);
    if(!live.length&&(hideEmpty||!dead.length))return;
    body+=`<div class="pt-m"><span class="pt-mk">${esc(m)} 月</span>
      <span class="pt-ml">${live.length} 期有内容${dead.length?" · "+dead.length+" 期空":""}</span></div>`;
    live.forEach(p=>{
      const st=stOf(p), n=memOf(p).length;
      body+=`<div class="pt-row${PF.sel===p.period_id?" sel":""}" onclick="ptPick('${p.period_id}')">
        <span class="pt-dt">${esc(p.start||"—")}</span>
        <span class="pt-nm">${esc(cleanLabel(p.label)||p.period_id)}<span class="pfam">${esc(FAM(p))}</span><span class="pt-n">${n} 件</span>${st.k==="on"?'<span class="pstate on">当期</span>':""}</span>
        <span class="pt-ar">▸</span></div>`;
    });
    if(dead.length&&!hideEmpty){
      const key=PF.year+"|"+m, open=(PF.month||{})[key];
      body+=`<div class="pt-row pt-empty${open?" open":""}" onclick="ptMonth('${esc(key)}')">
        <span class="pt-dt">${dead.length} 期</span>
        <span class="pt-nm">暂无可证成员<span class="pt-n">${[...new Set(dead.map(FAM))].length} 个家族</span></span>
        <span class="pt-ar">${open?"▾":"▸"}</span></div>`;
      if(open)dead.forEach(p=>{
        body+=`<div class="pt-row pt-empty" onclick="event.stopPropagation()">
          <span class="pt-dt">${esc(p.start||"—")}</span>
          <span class="pt-nm">${esc(cleanLabel(p.label)||p.period_id)}<span class="pfam">${esc(FAM(p))}</span></span>
          <span class="pt-ar">${stOf(p).txt}</span></div>`;
      });
    }
  });
  const sel=PF.sel?periods.find(p=>p.period_id===PF.sel):null;
  let drawer="";
  if(sel){
    const st=stOf(sel), mem=byPeriod[sel.period_id]||[];
    const unresN=mem.filter(it=>PT_UNRES.test(String(it.name||"").trim())).length;
    const pools=new Map();
    mem.forEach(it=>{
      const k=it.pool_uid||it.pool_id||it.pool_label||"—";
      if(!pools.has(k))pools.set(k,{label:it.pool_label||k,items:[]});
      pools.get(k).items.push(it);
    });
    const poolHtml=[...pools.values()].map(pl=>{
      pl.items.sort((a,b)=>(a.slot??999)-(b.slot??999));
      const plName=pl.label&&pl.label!=="—"?pl.label:"奖池";
      return `<div class="ptd-pool">${esc(plName)} · ${pl.items.length} 件</div><div class="ptd-items">${
        pl.items.map(it=>{
          const im=((it._media||{}).images||[])[0];
          const pic=im&&im.png?`<img src="${esc(im.png)}" alt="" loading="lazy">`:`<span class="ptd-ph">无图</span>`;
          /* 名字未解析：构建期只能回退成「道具 <id>」，这里如实标注，不伪装成正式名 */
          const bad=PT_UNRES.test(String(it.name||"").trim());
          const kindLine=esc(it.kind||"")+(it.count!=null?" ×"+esc(String(it.count)):"")+(it.slot!=null?" · 槽位 "+esc(String(it.slot)):"")+(it.evidence==="candidate"?" · 候选":"");
          return `<div class="ptd-item${bad?" unres":""}" title="${bad?"名字未解析（源表只给到道具 id）":esc(it.name||"")}">
            <div class="ptd-img">${pic}</div>
            <div class="ptd-n">${bad?"未知道具":esc(it.name||it.id)}</div>
            <div class="ptd-k">${bad?"#"+esc(it.item_id||"")+" · 名字未解析":kindLine}</div>
          </div>`;
        }).join("")}</div>`;
    }).join("");
    drawer=`<div class="ptd-mask" onclick="ptClose()"></div>
      <aside class="pt-drawer" role="dialog" aria-label="期次奖池详情">
        <div class="ptd-head">
          <span class="pstate ${st.k}">${st.txt}</span><span class="pfam">${esc(FAM(sel))}</span>
          <button class="ptd-x" onclick="ptClose()" title="关闭">×</button>
          <div class="ptd-name">${esc(cleanLabel(sel.label)||sel.period_id)}</div>
          <div class="ptd-meta">${esc(sel.start||"—")}${sel.end?" → "+esc(sel.end):""} · ${sel.pool_count||1} 池 · 共 ${mem.length} 件${sel.pool_size?" · 池内 "+sel.pool_size+" 件（服务端下发）":""}${unresN?` · <span class="ptd-unres">其中 ${unresN} 件名字未解析</span>`:""}</div>
        </div>
        <div class="ptd-body">${mem.length?poolHtml:`<div class="ptd-gap">暂无可证成员${sel.gap_reason?" · "+esc(sel.gap_reason):""}</div>`}</div>
      </aside>`;
  }
  /* 抽屉必须挂在 body 下：#grid 在 .wrap(z-index:1) 的层叠上下文里，
     留在 #grid 内会被顶栏(z-index:30)盖住。*/
  setTimeout(()=>{
    document.querySelectorAll("body > .pt-drawer, body > .ptd-mask").forEach(e=>e.remove());
    const dr=document.querySelector("#grid .pt-drawer"), mk=document.querySelector("#grid .ptd-mask");
    if(dr)document.body.appendChild(dr);
    if(mk)document.body.appendChild(mk);
  },0);
  return bar+nowHtml+yearsHtml+`<div class="pt-list">${body||'<div class="empty">当前筛选下没有期次</div>'}</div>`+drawer;
}

function renderPeriodMode(list){
  const meta=DATA.meta||{};
  /* 仅本板（meta.period_empty="show"）启用的两件事：
     ① 无成员期次也渲染成卡（589 期不能凭空消失）；
     ② 家族内再按年份折叠（meta.period_group="family_year"）。
     其它 period 板（upcoming_auto、归档板）meta 没有这两个开关，行为完全不变。 */
  const showEmpty=String(meta.period_empty||"")==="show";
  const groupByYear=showEmpty&&String(meta.period_group||"")==="family_year";
  window.PF_EMPTY=showEmpty;
  if(meta._pfInit!==1){
    const qps=getParam("ps"),qpf=getParam("pf"),qpk=getParam("pk"),qpo=getParam("po");
    if(qps)PF.status=qps; if(qpf)PF.family=qpf; if(qpk)PF.kind=qpk;
    PF.only=(qpo==="1"||qpo==="0")?qpo:(showEmpty?"0":"1");
    PF.limit=showEmpty?0:40;   // 0 = 不翻页
    meta._pfInit=1;
  }
  const periods=(DATA.periods||[]).slice();
  const byPeriod={};
  list.forEach(it=>{(byPeriod[it.period_id]=byPeriod[it.period_id]||[]).push(it);});
  const cleanLabel=s=>String(s||"").replace(/（活动名未在活动表内）/g,"").trim();
  /* 状态判定：本板区分「长期在架」（无结束时间）与「当期」（有结束时间且覆盖今天）。
     否则 2022 年的周消费福利会被算成当期并置顶，首屏全是老日期 + 当期标签。 */
  const stOf=showEmpty?(p=>{
    const t=new Date();
    const s=p.start?new Date(p.start+"T00:00:00"):null;
    const e=p.end?new Date(p.end+"T23:59:59"):null;
    if(!s&&!e)return {k:"unknown",txt:"无时间"};
    if(s&&t<s)return {k:"upcoming",txt:"即将开始"};
    if(e&&t>e)return {k:"ended",txt:"已结束"};
    if(!e)return {k:"longrun",txt:"长期在架"};
    return {k:"on",txt:"当期"};
  }):periodStatus;
  const rankOrder={on:0,upcoming:1,longrun:2,ended:3,unknown:4};
  const rank=p=>{const v=rankOrder[stOf(p).k];return v==null?3:v;};
  const yrOf=p=>{const s=String((p&&p.start)||"");return s.slice(0,4)||"—";};
  const famOrder=[...new Set(periods.map(p=>p.family).filter(Boolean))];
  if(showEmpty){
    /* 当期置顶 → 家族 → 年份（新在前）→ 期次 */
    periods.sort((a,b)=>{
      const ra=rank(a),rb=rank(b);
      if(ra!==rb)return ra-rb;
      const fa=famOrder.indexOf(a.family),fb=famOrder.indexOf(b.family);
      if(fa!==fb)return fa-fb;
      const na=Number(yrOf(a)),nb=Number(yrOf(b));
      const ya=Number.isFinite(na)?na:-1,yb=Number.isFinite(nb)?nb:-1;
      if(ya!==yb)return yb-ya;
      return ra===1?String(a.start||"").localeCompare(String(b.start||""))
                   :String(b.start||"").localeCompare(String(a.start||""));
    });
  }else{
    periods.sort((a,b)=>{
      const fa=famOrder.indexOf(a.family), fb=famOrder.indexOf(b.family);
      if(fa!==fb)return fa-fb;
      const ra=rank(a),rb=rank(b);
      if(ra!==rb)return ra-rb;
      if(ra===1)return String(a.start||"").localeCompare(String(b.start||""));
      return String(b.start||"").localeCompare(String(a.start||""));
    });
  }
  /* 本板（789 期）改用「年度时间轴 + 右侧抽屉」布局：
     时间轴按 年 → 月 排列，空期次在月内压成一行摘要；点期次从右侧抽屉看奖池（带图）。
     其它 period 板没有 period_empty 开关，仍走下面的卡片布局。 */
  if(showEmpty)return renderPeriodTimeline(periods,byPeriod,list,cleanLabel);

  const fams=[...new Set(periods.map(p=>p.family).filter(Boolean))];
  const kinds=[...new Set(list.map(i=>i.kind).filter(Boolean))];
  const famYears={};
  periods.forEach(p=>{const f=p.family||"—";(famYears[f]=famYears[f]||new Set()).add(yrOf(p));});
  const stCount={on:0,upcoming:0,longrun:0,ended:0,unknown:0};
  let withMembers=0;
  periods.forEach(p=>{
    const n=(byPeriod[p.period_id]||[]).length;
    if(n)withMembers++;
    if(showEmpty||n)stCount[stOf(p).k]++;
  });
  const chip=(label,n,active,fn)=>`<button class="pf-chip${active?" on":""}" onclick="${fn}">${label}${n!=null?` <b>${n}</b>`:""}</button>`;
  /* 本板（789 期 / 20+ 家族 / 多种奖励类型）筛选条如果三条并排会吃掉首屏 300px：
     状态保留芯片（最常用），家族与类型收成下拉，合成一条工具栏。 */
  const selOne=(cur,opts,fn,title)=>{
    const html=opts.map(o=>`<option value="${esc(o.v)}"${o.v===cur?" selected":""}>${esc(o.t)}</option>`).join("");
    return `<select class="pf-sel" title="${esc(title)}" onchange="${fn}(this.value)">${html}</select>`;
  };
  const famOpts=[{v:"all",t:"全部家族"},...fams.map(f=>({v:f,t:`${f}（${periods.filter(p=>p.family===f).length}）`}))];
  const kindOpts=[{v:"all",t:"全部类型"},...kinds.map(k=>({v:k,t:`${k}（${list.filter(i=>i.kind===k).length}）`}))];
  const bar=showEmpty?`<div class="pf-bar pf-bar-one">
    <span class="pf-label">状态</span>
    ${chip("全部",null,PF.status==="all","pSet('status','all')")}
    ${chip("当期",stCount.on,PF.status==="on","pSet('status','on')")}
    ${chip("即将开始",stCount.upcoming,PF.status==="upcoming","pSet('status','upcoming')")}
    ${chip("长期在架",stCount.longrun,PF.status==="longrun","pSet('status','longrun')")}
    ${chip("已结束",stCount.ended,PF.status==="ended","pSet('status','ended')")}
    ${stCount.unknown?chip("无时间",stCount.unknown,PF.status==="unknown","pSet('status','unknown')"):""}
    <span class="pf-sep"></span>
    ${selOne(PF.family,famOpts,"pSet","按家族筛选")}
    ${selOne(PF.kind,kindOpts,"pSet","按奖励类型筛选")}
    <span class="pf-sep"></span>
    ${chip("只看有内容",withMembers,PF.only==="1","pSet('only','1')")}
    ${chip("全部期次",periods.length,PF.only==="0","pSet('only','0')")}
  </div>`:`<div class="pf-bar">
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
  <div class="pf-bar pf-bar-fam">
    <span class="pf-label">家族</span>
    ${chip("全部",null,PF.family==="all","pSet('family','all')")}
    ${fams.map(f=>chip(esc(f),periods.filter(p=>p.family===f).length,PF.family===f,`pSet('family','${esc(f).replace(/'/g,"\'")}')`)).join("")}
  </div>
  <div class="pf-bar">
    <span class="pf-label">奖励类型</span>
    ${chip("全部",null,PF.kind==="all","pSet('kind','all')")}
    ${kinds.map(k=>chip(esc(k),list.filter(i=>i.kind===k).length,PF.kind===k,`pSet('kind','${esc(k).replace(/'/g,"\'")}')`)).join("")}
  </div>`;

  let shown=0, total=0, lastFam=null, lastYear=null;
  const cap=showEmpty?0:(PF.limit||24);   // 0 = 不翻页
  /* 空期次按「家族 + 年份」聚合成一条可展开摘要：589 个空期次逐条铺开会把真实内容淹没 */
  const emptyByKey={}, yearTotal={};
  if(showEmpty){
    periods.forEach(p=>{
      const f=p.family||"—",y=yrOf(p),k=f+"|"+y;
      yearTotal[k]=(yearTotal[k]||0)+1;
      if(!(byPeriod[p.period_id]||[]).length)emptyByKey[k]=(emptyByKey[k]||0)+1;
    });
  }
  const emptyEmitted=new Set();
  const yearHead=new Set();
  const cards=[];
  for(const p of periods){
    let mem=byPeriod[p.period_id]||[];
    if(!mem.length && !showEmpty)continue;
    const st=stOf(p);
    if(PF.status!=="all"&&st.k!==PF.status)continue;
    if(PF.family!=="all"&&p.family!==PF.family)continue;
    if(PF.kind!=="all"){mem=mem.filter(x=>x.kind===PF.kind); if(!mem.length)continue;}
    if(PF.only==="1" && !mem.length)continue;
    total++;
    if(cap && shown>=cap)continue;
    shown++;
    const labelClean=cleanLabel(p.label)||cleanLabel(p.activity_name)||p.period_id;
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
    const imgs=mem.map(x=>{const a=((x._media||{}).images)||[];return a.length&&a[0]&&a[0].png?a[0].png:null;}).filter(Boolean);
    const withImg=imgs.length;
    const cover=imgs.slice(0,4).map(s=>`<img src="${esc(s)}" alt="" loading="lazy">`).join("");
    const famName=p.family||"—";
    const y=yrOf(p);
    if(lastFam!==famName){
      lastFam=famName; lastYear=null;
      if(PF.family==="all"){
        const famTotal=showEmpty
          ?periods.filter(x=>(x.family||"—")===famName).length
          :periods.filter(x=>(x.family||"—")===famName&&(byPeriod[x.period_id]||[]).length).length;
        const famWith=showEmpty?periods.filter(x=>(x.family||"—")===famName&&(byPeriod[x.period_id]||[]).length).length:famTotal;
        const closed=(PF.closed||{})[famName];
        cards.push(`<div class="pfam-head${closed?" closed":""}" onclick="pToggleFam('${esc(famName).replace(/'/g,"\'")}')">
          <span class="pfam-name">${esc(famName)}</span><span class="pfam-n">${famTotal} 期${showEmpty?` · 有内容 ${famWith}`:""}</span>
          <span class="pfam-arrow">${closed?"▸":"▾"}</span></div>`);
        if(closed){continue;}
      }
    }
    if(PF.family==="all" && (PF.closed||{})[famName]) continue;
    if(groupByYear && ((famYears[famName]||new Set()).size>1)){
      if(lastYear!==y){
        lastYear=y;
        const yKey=famName+"|"+y;
        const yClosed=(PF.closed||{})[yKey];
        const yTotalN=yearTotal[yKey]||periods.filter(x=>(x.family||"—")===famName&&yrOf(x)===y).length;
        /* 整年都没有成员：年份头并入下面的空期次摘要，避免
           「2026 20 期」+「2026 20 期 · 暂无可证成员」两行说同一件事。 */
        if(!((emptyByKey[yKey]||0)>=yTotalN)){
          yearHead.add(yKey);
          cards.push(`<div class="pfam-head pfam-year${yClosed?" closed":""}" onclick="pToggleFam('${esc(yKey).replace(/'/g,"\'")}')">
            <span class="pfam-name">${esc(y)}</span><span class="pfam-n">${yTotalN} 期</span>
            <span class="pfam-arrow">${yClosed?"▸":"▾"}</span></div>`);
        }
      }
      if((PF.closed||{})[famName+"|"+y]) continue;
    }
    /* 无成员期次：先按「家族 + 年份」折叠成一条摘要，展开后才是逐条紧凑行 */
    if(!mem.length){
      const eKey=famName+"|"+y;
      const openEmpty=(PF.openEmpty||{})[eKey];
      if(!emptyEmitted.has(eKey)){
        emptyEmitted.add(eKey);
        const n=emptyByKey[eKey]||1;
        /* 该年已有年份头时，摘要不再重复年份，只报「余下 n 期」 */
        const yShown=yearHead.has(eKey);
        cards.push(`<div class="pfam-empty${openEmpty?" open":""}${yShown?" under":""}" onclick="pToggleEmpty('${esc(eKey).replace(/'/g,"\'")}')">
          ${yShown?"":`<span class="pfe-name">${esc(y)}</span>`}<span class="pfe-n">${yShown?"余下 ":""}${n} 期 · 暂无可证成员</span>
          <span class="pfe-arrow">${openEmpty?"▾":"▸"}</span></div>`);
      }
      if(!openEmpty) continue;
      cards.push(`<div class="prow ${st.k}" title="${esc(p.gap_reason||"暂无可证成员")}">
        <span class="prow-date">${esc(p.start||"—")}</span>
        <span class="prow-name">${esc(labelClean)}</span>
        <span class="prow-state ${st.k}">${st.txt}</span>
        <span class="prow-note">暂无可证成员</span>
      </div>`);
      continue;
    }
    const dateParts=[];
    if(p.start)dateParts.push(esc(p.start)+(p.end?" → "+esc(p.end):""));
    else if(p.end)dateParts.push("→ "+esc(p.end));
    dateParts.push((p.pool_count||1)+" 池");
    dateParts.push(mem.length?("共 "+mem.length+" 件 · 有图 "+withImg):"暂无可证成员");
    if(p.pool_size)dateParts.push("池内 "+p.pool_size+" 件（服务端下发）");
    const dateLine=dateParts.join(" · ");
    const bodyHtml=mem.length?poolHtml
      :`<div class="pcard-gap">暂无可证成员${p.gap_reason?(" · "+esc(p.gap_reason)):""}</div>`;
    cards.push(`<div class="pcard ${st.k}${mem.length?"":" pempty"}">
      <div class="pcard-head" onclick="pToggleCard(this)" role="button" tabindex="0">
        <div class="pcard-title">
          <span class="pcard-name">${esc(labelClean)}</span>
          <span class="pstate ${st.k}">${st.txt}</span>
          <span class="pfam">${esc(p.family||"")}</span>
        </div>
        ${cover?`<div class="pcard-cover">${cover}</div>`:""}
        <div class="pcard-date">${dateLine}</div>
      </div>
      <div class="pcard-body" hidden>${bodyHtml}</div>
    </div>`);
  }
  const more=(cap&&shown<total)?`<div style="text-align:center;margin:6px 0 24px"><button class="pf-chip on" onclick="pMore()">加载更多（已显示 ${shown}/${total}）</button></div>`:"";
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
  if(EQUIP_BOARD){
    document.body.classList.add("equip-mode");
    const eqi=document.getElementById("q");
    if(eqi)eqi.placeholder="搜索：装备名 / 类型 / 武器细类 / 描述…";
  }
  if(GENE_BOARD){
    document.body.classList.add("gene-mode");
    const gqi=document.getElementById("q");
    if(gqi)gqi.placeholder="搜索：潜能名 / 种族 / 效果 / 档位…";
    /* 服别 Tab：点按钮即切换（深链写 ?gs=，不重载页面）；同页只绑一次委托 */
    document.addEventListener("click",e=>{
      const btn=e.target.closest("[data-gene-server]");
      if(!btn||!btn.closest("#grid"))return;
      e.preventDefault();
      const k=btn.getAttribute("data-gene-server");
      if(!GENE_SERVERS.some(s=>s.key===k)||k===GENE_SERVER)return;
      GENE_SERVER=k;
      try{
        const u=new URLSearchParams(location.search);
        if(k==="overview")u.delete("gs");else u.set("gs",k);
        history.replaceState(null,"",location.pathname+"?"+u.toString());
      }catch(err){}
      render();
    });
    document.addEventListener("keydown",e=>{
      if(e.key!=="Enter"&&e.key!==" ")return;
      const c=e.target.closest&&e.target.closest(".gene-card");
      if(!c)return;
      e.preventDefault();
      const i=parseInt(c.dataset.cidx||"-1",10);
      if(i>=0&&C2.chips[i])c2Open(i);
    });
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
  /* 公式块：meta.formula = [{t,e,n}]，显示在列表上方（伤害类板块用） */
  if(Array.isArray(m.formula)&&m.formula.length&&document.getElementById("grid")){
    const host=document.getElementById("grid").parentNode;
    const box=document.createElement("div");
    box.className="formula-box";
    box.innerHTML='<div class="fb-hd">计算公式</div>'+m.formula.map(r=>
      '<div class="fb-row">'+
        (r.t?'<div class="fb-t">'+esc(r.t)+'</div>':'')+
        (r.e?'<div class="fb-e mono">'+esc(r.e).replace(/\n/g,'<br>')+'</div>':'')+
        (r.n?'<div class="fb-n">'+esc(r.n)+'</div>':'')+
      '</div>').join("");
    host.insertBefore(box,host.firstChild);
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
  if(CDN_BOARD||TREE_BOARD)buildViewSwitch();
  render();
  /* 影音资源板：显式接管。个别环境里 render() 内的分派分支会被旧脚本缓存跳过，
     所以在启动链路里再调一次；mediaLibraryRender 幂等（已建好只刷新列表）。 */
  if(MEDIA_BOARD||(DATA&&DATA.meta&&DATA.meta.board_mode==="media_library")){
    try{ mediaLibraryRender(DATA.items); }catch(e){ console.error("mediaLibraryRender", e); }
  }
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


/* 2026-11-01：同 model 跳转 —— 点「同 model N」滚到同 model 的下一张卡并高亮
   只在时装板生效；被钉住（D2 灯箱）时也能用，因为卡片仍在列表 DOM 里。 */
document.addEventListener("click", function(e){
  const a=e.target.closest&&e.target.closest("[data-sib-model]");
  if(!a)return;
  e.preventDefault();
  const m=a.getAttribute("data-sib-model");
  const group=(window.FR_MODEL_INDEX||{})[m]||[];
  if(group.length<2)return;
  const cur=a.closest(".fcard");
  const curId=cur?cur.getAttribute("data-frid"):null;
  const idx=group.findIndex(x=>x.id===curId);
  const next=group[(idx+1)%group.length];
  const el=document.querySelector('.fcard[data-frid="'+String(next.id).replace(/"/g,'')+'"]');
  if(!el)return;
  el.scrollIntoView({behavior:"smooth",block:"center"});
  el.classList.add("fr-flash");
  setTimeout(()=>el.classList.remove("fr-flash"),1600);
});


/* 2026-11-01：详情内「同 model」点击 = 钉住当前卡 + 左侧打开目标卡（方案B 交互） */
function frEnsureChip(item){
  try{ if(!item||typeof C2==='undefined'||!C2.chips)return -1; }catch(e){ return -1; }
  const idOf=(x)=>{try{return String(c2IdOf(x));}catch(e){return String(x&&x.id);}};
  let i=C2.chips.findIndex(x=>idOf(x)===String(item.id));
  if(i<0){
    C2.chips.push(item); i=C2.chips.length-1;
    try{ if(C2.html){C2.html[idOf(item)]=frCard(item,i);}
         if(C2.htmlFull){C2.htmlFull[idOf(item)]=frCard(item,i,true);} }catch(e){}
  }
  return i;
}
function frJumpSibling(fromId,toId){
  const chips=(typeof C2!=='undefined'&&C2.chips)||[];
  const idOf=(x)=>{try{return String(c2IdOf(x));}catch(e){return String(x&&x.id);}};
  const byId=(window.FR_ITEM_BY_ID)||{};
  const fromItem=byId[String(fromId)]||null, toItem=byId[String(toId)]||null;
  const fi=(fromItem?frEnsureChip(fromItem):chips.findIndex(x=>idOf(x)===String(fromId)));
  const ti=(toItem?frEnsureChip(toItem):chips.findIndex(x=>idOf(x)===String(toId)));
  if(ti<0){
    var _b=(new URLSearchParams(location.search).get('b'))||'';
    location.href='board.html?b='+encodeURIComponent(_b)+'&d2='+encodeURIComponent(toId);
    return;
  }
  if(fi>=0 && !(C2.pinned && idOf(C2.pinned)===String(fromId))){
    const keep=C2.idx; C2.idx=fi;
    try{ c2TogglePin(); }catch(e){}
    C2.idx=keep;
  }
  try{ c2Open(ti); }catch(e){
    var _b2=(new URLSearchParams(location.search).get('b'))||'';
    location.href='board.html?b='+encodeURIComponent(_b2)+'&d2='+encodeURIComponent(toId);
  }
  document.querySelectorAll('.fr-sib-card').forEach(el=>el.classList.remove('seen'));
  const el=document.querySelector('.fr-sib-card[data-sib-id="'+String(toId).replace(/"/g,'')+'"]');
  if(el)el.classList.add('seen');
}
document.addEventListener("click", function(e){
  const a=e.target.closest&&e.target.closest("[data-sib-id]");
  if(!a)return;
  e.preventDefault(); e.stopPropagation();
  var from=a.getAttribute("data-sib-from"), to=a.getAttribute("data-sib-id");
  if(typeof window.__frJumpSibling==="function" && window.__frJumpSibling(from,to)) return;
  var _b=(new URLSearchParams(location.search).get('b'))||'';
  location.href='board.html?b='+encodeURIComponent(_b)+'&d2='+encodeURIComponent(to);
});

