/* board.html 尾部增强块：性能条 / 分类导航 / 技术详情 / 窄列宽（2026-10-30 拆出）。 */
(function(){
  if(!document || !document.documentElement || !document.documentElement.style) return;
  var bar = document.querySelector ? document.querySelector('.hd2') : null;
  if(!bar) return;
  function sync(){ try{ document.documentElement.style.setProperty('--top-h', bar.offsetHeight + 'px'); }catch(e){} }
  sync();
  if(window && window.addEventListener){
    window.addEventListener('resize', sync);
    window.addEventListener('scroll', function(){
      try{ document.body.classList.toggle('scrolled', (window.scrollY||0) > 40); }catch(e){}
      sync();
    }, {passive:true});
  }
  if(window && window.ResizeObserver){ try{ new ResizeObserver(sync).observe(bar); }catch(e){} }
})();


(function(){
  var T=window.WIKI_TAXONOMY, M=window.WIKI_MANIFEST;
  if(!T||!M) return;
  var byId={}; (M.boards||[]).forEach(function(b){byId[b.board]=b;});
  function cleanName(s){
    return String(s||'')
      .replace(/^当前包\s*·\s*/,'')
      .replace(/（[^）]*）/g,'')
      .replace(/\([^)]*\)/g,'')
      .split('·')[0]
      .replace(/全量|图鉴/g,'')
      .replace(/总表$/,'')
      .trim();
  }

  var ICON = {
    preview: '<img class="gi" src="assets/skin_posters/1110012.png" alt="">',
    fashion: '<img class="gi" src="assets/fashion_icon_refs/icon_40095_b.png" alt="">',
    combat:  '<img class="gi" src="assets/core_icons/item_icon_jin_bing_b.png" alt="">',
    activity:'<img class="gi" src="assets/lottery_icons/102602.png" alt="">',
    reference:'<img class="gi" src="assets/item_icons/icon_10004_b.png" alt="">',
    service_package:'<img class="gi" src="assets/item_icons/icon_fushegaoxiao_box1_b.png" alt="">'
  };
  var cur=new URLSearchParams(location.search).get('b')||'';
  var TITLES={};
  function ntag(id){ var b=byId[id]; return (b && String(b.name||'').indexOf('（内测版）')===0) ? '（内测版）' : ''; }
  function cleanNm(x){
    return String(x||'').replace(/^当前包\s*·\s*/,'').replace(/（[^）]*）/g,'')
      .replace(/\([^)]*\)/g,'').split('·')[0].replace(/全量|图鉴/g,'').replace(/总表$/,'').trim();
  }
  /* 2026-11-01：多卡叶子共用「 · 」前缀时（如「…（武器 · 护甲） · 简单生存服」），
     取尾段作服别后缀，避免侧栏出现多个同名行；无公共前缀则返回 null（沿用原名）。 */
  function branchSuffix(ids){
    var names=ids.map(function(id){return String((byId[id]||{}).name||id);});
    var p=names[0];
    for(var i=1;i<names.length;i++){
      var j=0; while(j<p.length&&j<names[i].length&&p.charAt(j)===names[i].charAt(j))j++;
      p=p.slice(0,j);
    }
    var cut=p.lastIndexOf(' · ');
    if(cut<0) return null;
    var out={};
    for(var k=0;k<names.length;k++){
      var seg=names[k].slice(cut+3).trim();
      if(!seg) return null;
      out[ids[k]]=seg;
    }
    return out;
  }
  /* 2026-11-01：跟随首页的「显示内测板块」开关（localStorage: wiki_show_preview）
     ★ 必须先于 TITLES 计算，否则内测卡的页面标题会退回分类名（四张分服卡同名）。 */
  var SHOW_PREVIEW_NAV=(function(){try{return localStorage.getItem('wiki_show_preview')==='1';}catch(e){return false;}})();
  function _navVis(id){var b=byId[id];return !!b && (SHOW_PREVIEW_NAV || !/内测/.test(String(b.name||'')));}
  (T['树']||[]).forEach(function(top){
    (top.children||[]).forEach(function(leaf){
      var ids=(leaf.boards||[]).filter(_navVis);
      var br=(ids.length>1)?branchSuffix(ids):null;
      ids.forEach(function(id){
        if(ids.length===1){ TITLES[id]=leaf.name; return; }
        if(br){ TITLES[id]=cleanNm(byId[id].name||id)+' · '+br[id]; }
      });
    });
  });
  window.__BOARD_TITLES=TITLES;
  var nav=document.getElementById('siteNav');
  var html='<div class="hd"><a class="board-home" href="wiki.html" aria-label="返回 Wiki 首页"><img class="nav-logo" src="assets/logo_lifeafter_wiki.png" alt="LIFEAFTER WIKI"></a></div>'+'<a class="leafrow" id="navOptPreviewRow" href="javascript:void(0)" style="display:flex!important;align-items:center;gap:6px;color:#c9d3e6!important"><input type="checkbox" id="navOptPreview" style="width:13px;height:13px;accent-color:#b6a7df"'+(SHOW_PREVIEW_NAV?' checked':'')+'>显示内测板块</a>';
  function _esc(v){return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');}
  var _NAVCLOSED=(function(){try{return JSON.parse(localStorage.getItem('board_nav_closed')||'[]');}catch(e){return [];}})();
  function _isClosed(k){return _NAVCLOSED.indexOf(k)>=0;}
  (T['树']||[]).forEach(function(top){
    var tid=String(top.id||top.name), body='';
    (top.boards||[]).forEach(function(id){
      if(!_navVis(id)) return;
      body += '<a class="leafrow'+(id===cur?' on':'')+'" href="board.html?b='+encodeURIComponent(id)+'">'+
              ntag(id)+top.name.replace(/^[^、]*、/,'')+'</a>';
    });
    (top.children||[]).forEach(function(leaf){
      var ids=(leaf.boards||[]).filter(_navVis);
      if(!ids.length) return;
      if(ids.length===1){
        body += '<a class="leafrow'+(ids[0]===cur?' on':'')+'" href="board.html?b='+encodeURIComponent(ids[0])+'">'+
                ntag(ids[0])+leaf.name+'</a>';
        return;
      }
      var lid=tid+'/'+leaf.name, br=branchSuffix(ids), lc=_isClosed(lid);
      body += '<div class="leafhd'+(lc?' closed':'')+'" data-leaf="'+_esc(lid)+'" role="button" tabindex="0">'+
              '<span>'+_esc(leaf.name)+'</span><i class="car">▾</i></div>';
      body += '<div class="leafbody" data-lbody="'+_esc(lid)+'"'+(lc?' style="display:none"':'')+'>';
      ids.forEach(function(id){
        body += '<a class="sub'+(id===cur?' on':'')+'" href="board.html?b='+encodeURIComponent(id)+'">'+
                ntag(id)+cleanName(byId[id].name||id)+(br?(' · '+br[id]):'')+'</a>';
      });
      body += '</div>';
    });
    if(!body) return;
    var tc=_isClosed(tid);
    html += '<div class="grp'+(tc?' closed':'')+'" data-grp="'+_esc(tid)+'" role="button" tabindex="0">'+
            (ICON[top.id]||'')+'<span>'+_esc(top.name)+'</span><i class="car">▾</i></div>';
    html += '<div class="grpbody" data-gbody="'+_esc(tid)+'"'+(tc?' style="display:none"':'')+'>'+body+'</div>';
  });
  nav.innerHTML=html;
  /* 类目折叠：点大目录 / 子分组标题收放，状态记 localStorage(board_nav_closed) */
  (function(){
    var KEY='board_nav_closed';
    function load(){try{return JSON.parse(localStorage.getItem(KEY)||'[]');}catch(e){return [];}}
    function save(a){try{localStorage.setItem(KEY,JSON.stringify(a));}catch(e){}}
    function toggle(el,key){
      var closed=el.classList.toggle('closed');
      var body=el.nextElementSibling;
      if(body) body.style.display=closed?'none':'';
      var a=load(),i=a.indexOf(key);
      if(closed){ if(i<0) a.push(key); } else if(i>=0){ a.splice(i,1); }
      save(a);
    }
    nav.addEventListener('click',function(ev){
      var g=ev.target.closest('.grp[data-grp]');
      if(g){ toggle(g,g.getAttribute('data-grp')); return; }
      var h=ev.target.closest('.leafhd[data-leaf]');
      if(h){ toggle(h,h.getAttribute('data-leaf')); }
    });
    nav.addEventListener('keydown',function(ev){
      if(ev.key!=='Enter'&&ev.key!==' ') return;
      var el=ev.target.closest('.grp[data-grp],.leafhd[data-leaf]');
      if(!el) return;
      ev.preventDefault();
      toggle(el, el.getAttribute('data-grp')||el.getAttribute('data-leaf'));
    });
  })();
  (function(){
    var cb=document.getElementById('navOptPreview');
    if(!cb)return;
    cb.addEventListener('change', function(){
      try{ localStorage.setItem('wiki_show_preview', cb.checked ? '1' : '0'); }catch(e){}
      location.reload();
    });
  })();
  /* 侧栏自适应：优先缩字号（最小 9px）保证单行放得下，仍放不下才回退省略号 */
  function fitNav(){
    var els=nav.querySelectorAll('a, .leafhd, .grp');
    for(var i=0;i<els.length;i++){
      var el=els[i];
      el.style.fontSize='';
      var fs=parseFloat(getComputedStyle(el).fontSize)||12;
      var guard=0;
      while(el.scrollWidth>el.clientWidth && fs>9 && guard<20){ fs-=0.5; el.style.fontSize=fs+'px'; guard++; }
      if(el.scrollWidth>el.clientWidth) el.style.textOverflow='ellipsis';
    }
  }
  fitNav();
  window.addEventListener('resize', fitNav);
})();


/* 板级「技术详情」并到 meta 行尾，点开才展开 */
(function(){
  function ensureLink(){
    var meta=document.getElementById('metaline'), notes=document.getElementById('notes');
    if(!meta||!notes||meta.querySelector('.techlink')) return;
    var sep=document.createElement('span'); sep.className='techlink-sep'; sep.textContent=' · ';
    var a=document.createElement('a'); a.className='techlink'; a.href='javascript:void(0)';
    a.textContent='技术详情';
    a.onclick=function(e){
      e.preventDefault();
      var panel=document.getElementById('techPanel');
      if(!panel){
        panel=document.createElement('div');
        panel.id='techPanel';
        panel.style.cssText='margin:10px 0 0;padding:10px 12px;border:1px solid #262f3b;border-radius:8px;background:#0f141b;font-size:12px;color:#9aa7b6;max-height:320px;overflow:auto';
        var hd=document.querySelector('.hd2'); if(hd) hd.appendChild(panel);
      }
      var html=notes.innerHTML.replace(/<summary[^>]*>[\s\S]*?<\/summary>/,'');
      if(panel.style.display==='block' && panel.dataset.src===html){ panel.style.display='none'; return; }
      panel.innerHTML=html; panel.dataset.src=html; panel.style.display='block';
    };
    var wrap=document.createElement('span'); wrap.className='techlink-wrap';
    wrap.appendChild(a);
    meta.appendChild(wrap);
    var bar=document.querySelector('.hd2');
    if(bar && notes.parentNode!==bar){ bar.appendChild(notes); }
    var det=notes.querySelector('details');
    if(location.hash==='#tech'){ notes.classList.add('open'); notes.style.display='block'; if(det) det.open=true; }
    else if(!notes.classList.contains('open')){ notes.style.display='none'; }
  }
  document.addEventListener('DOMContentLoaded', function(){
    ensureLink();
    var meta=document.getElementById('metaline');
    if(meta) new MutationObserver(ensureLink).observe(meta,{childList:true,characterData:true,subtree:true});
    var notes=document.getElementById('notes');
    if(notes) new MutationObserver(function(){
      if(!notes.classList.contains('open')) notes.style.display='none';
    }).observe(notes,{childList:true,subtree:true,attributes:true,attributeFilter:['style','class']});
  });
})();


/* 头像/核芯/料理：默认卡偏宽 → 直接给网格设窄列宽（内联，压过任何外部样式） */
(function(){
  /* 2026-11-02：核芯板子卡再收窄（150px，接近正方形），其余两板维持 210px */
  var NARROW={avatar_catalog:210, mutation_core_full:150, edible_catalog:210};
  function apply(){
    var b=new URLSearchParams(location.search).get('b');
    if(!NARROW[b]) return;
    var g=document.getElementById('grid');
    if(!g) return;
    g.style.gridTemplateColumns='repeat(auto-fill,minmax('+NARROW[b]+'px,1fr))';
    g.style.gap=b==='mutation_core_full'?'10px':'12px';
  }
  document.addEventListener('DOMContentLoaded', apply);
  var g=document.getElementById('grid');
  if(g) new MutationObserver(apply).observe(g,{childList:true});
})();