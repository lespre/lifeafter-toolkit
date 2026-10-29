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
    reference:'<img class="gi" src="assets/item_icons/icon_10004_b.png" alt="">'
  };
  var cur=new URLSearchParams(location.search).get('b')||'';
  var TITLES={};
  function ntag(id){ var b=byId[id]; return (b && String(b.name||'').indexOf('（内测版）')===0) ? '（内测版）' : ''; }
  function cleanNm(x){
    return String(x||'').replace(/^当前包\s*·\s*/,'').replace(/（[^）]*）/g,'')
      .replace(/\([^)]*\)/g,'').split('·')[0].replace(/全量|图鉴/g,'').replace(/总表$/,'').trim();
  }
  (T['树']||[]).forEach(function(top){
    (top.children||[]).forEach(function(leaf){
      var ids=(leaf.boards||[]).filter(function(x){return byId[x];});
      ids.forEach(function(id){
        TITLES[id]=(ids.length===1) ? leaf.name : cleanNm(byId[id].name||id);
      });
    });
  });
  window.__BOARD_TITLES=TITLES;
  var nav=document.getElementById('siteNav');
  var html='<div class="hd"><a class="board-home" href="wiki.html" aria-label="返回 Wiki 首页"><img class="nav-logo" src="assets/logo_lifeafter_wiki.png" alt="LIFEAFTER WIKI"></a></div>';
  (T['树']||[]).forEach(function(top){
    html += '<div class="grp">'+ICON[top.id] + '<span>' + top.name + '</span></div>';
    var rows=[];
    (top.boards||[]).forEach(function(id){
      if(!byId[id]) return;
      rows.push({kind:'row', id:id, label:ntag(id)+top.name.replace(/^[^、]*、/,'')});
    });
    (top.children||[]).forEach(function(leaf){
      var ids=(leaf.boards||[]).filter(function(x){return byId[x];});
      if(!ids.length) return;
      if(ids.length===1){ rows.push({kind:'row', id:ids[0], label:ntag(ids[0])+leaf.name}); return; }
      rows.push({kind:'head', label:leaf.name});
      ids.forEach(function(id){ rows.push({kind:'sub', id:id, label:ntag(id)+cleanName(byId[id].name||id)}); });
    });
    rows.forEach(function(r){
      if(r.kind==='head'){ html += '<div class="leafhd">'+r.label+'</div>'; return; }
      html += '<a class="'+(r.kind==='sub'?'sub':'leafrow')+(r.id===cur?' on':'')+
              '" href="board.html?b='+encodeURIComponent(r.id)+'">'+r.label+'</a>';
    });
  });
  nav.innerHTML=html;
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
  var NARROW={avatar_catalog:228, mutation_core_full:228, edible_catalog:228};
  function apply(){
    var b=new URLSearchParams(location.search).get('b');
    if(!NARROW[b]) return;
    var g=document.getElementById('grid');
    if(!g) return;
    g.style.gridTemplateColumns='repeat(auto-fill,minmax(210px,1fr))';
    g.style.gap='12px';
  }
  document.addEventListener('DOMContentLoaded', apply);
  var g=document.getElementById('grid');
  if(g) new MutationObserver(apply).observe(g,{childList:true});
})();