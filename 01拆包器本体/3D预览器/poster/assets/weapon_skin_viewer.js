(function(){
  "use strict";

  const scriptUrl=(document.currentScript&&document.currentScript.src)||location.href;
  const assetBase=new URL(".",scriptUrl);
  const runtimeUrls={
    three:new URL("vendor/three/three.module.min.js",assetBase).href,
    loader:new URL("vendor/three/addons/loaders/GLTFLoader.js",assetBase).href,
    controls:new URL("vendor/three/addons/controls/OrbitControls.js",assetBase).href,
    trackball:new URL("vendor/three/addons/controls/TrackballControls.js",assetBase).href,
  };
  const state={
    shell:null,dialog:null,stage:null,poster:null,loading:null,status:null,title:null,subtitle:null,
    stateSelect:null,cameraSelect:null,sfxButton:null,fidelity:null,fullscreen:null,
    runtimePromise:null,THREE:null,GLTFLoader:null,OrbitControls:null,
    renderer:null,scene:null,camera:null,controls:null,root:null,mixer:null,clock:null,
    resizeObserver:null,frame:0,generation:0,record:null,config:null,manifestUrl:null,
    states:[],cameras:[],effectsAdapter:null,effectsHandle:null,lastFocus:null,bodyOverflow:"",
  };

  const esc=s=>String(s==null?"":s).replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const isObject=v=>v&&typeof v==="object"&&!Array.isArray(v);

  function fidelityLabel(value){
    const labels={source_matched:"源材质匹配",source:"源数据",approximate:"材质近似",none:"无 SFX",partial:"部分 SFX",matched:"SFX 已匹配"};
    return labels[String(value||"")]||String(value||"");
  }

  /* ══════════════════════════════════════════════════════════════════════════════════════
     ★★★ 新增（2026-09-20，CUBE_PICKER）：环境立方体（IBL cube）选择器的数据侧。
     全部口径以 data/media/weapon_skin_cubes.js 为唯一来源（该文件由
     03拆包产物/_target_1110025/_cubepick_build.py 按名字哈希 mm3(path,0x66666666)/
     mm3(path,0x77777777) 枚举源容器后解码生成，逐面与 DDS 字节自证）。
     ⚠ 源数据里没有「预览该用哪一套 cube」的选择器 ⇒ 本选择器是**取证/对比工具**。
     ══════════════════════════════════════════════════════════════════════════════════════ */
  function cubeIndexOf(name){
    var idx=window.WIKI_WEAPON_SKIN_CUBES;
    if(!idx||!idx.cubes||!name)return null;
    for(var i=0;i<idx.cubes.length;i++){ if(idx.cubes[i].name===name)return idx.cubes[i]; }
    return null;
  }
  /* cube 六面 URL 解析（**只影响新选项**，默认档行为逐字不变）：
       · resolve==='skin'（仅 qiangpi / jiayuan02a，= 接线前唯一允许的两个值）
         ⇒ 走皮肤自己的 src_cube/faces/，URL 与接线前完全相同 ⇒ 任何皮肤零回归；
       · resolve==='shared'（本轮新增的源 cube）⇒ 走皮肤无关的
         assets/3d/weapon_skin/_shared/cubes/<name>/faces/（跨皮肤可用）；
       · resolve==='self_authored'（自造近似档，非游戏资产）⇒ 同样必须走**显式 faces[]**。
     ★ 改动（2026-09-20，MERGE_FIX）：放行条件由 `resolve==='shared'` 放宽为 shared|self_authored。
       依据是**实测**而不是推测：自造 cube 的
         src_cube/faces/custom_studio_20260920_f0_m0.png  sha256=78e55829…（= 清册 faces_srgb[0]，无 alpha）
         _shared/cubes/custom_studio_20260920/rgbm/…_f0_m0.png sha256=98514675…（= faces_encoding 'rgbm'）
       查看器按 asm 542-544 `pow(rgb*a*16,2)` 且 cube 纹理 NoColorSpace 解码 ⇒ 若在这里落到
       src_cube/faces/ 兜底路径，就会喂进 a=1.0 的 sRGB 面、解码亮约 4400×（实测 p50 0.9679）——
       那是**编码假象**，不是环境更亮。故自造条目必须命中它的显式 faces[]（= rgbm/ 六面）。 */
  function cubeFaceUrls(name){
    var rec=cubeIndexOf(name);
    if(rec&&(rec.resolve==='shared'||rec.resolve==='self_authored')&&rec.faces&&rec.faces.length===6&&typeof location!=="undefined"){
      try{ return rec.faces.slice(0,6).map(function(r){ return new URL(r,location.href).href; }); }catch(e){}
    }
    var B=(state.modelDir||'')+'src_cube/faces/';
    return [0,1,2,3,4,5].map(function(i){ return B+name+'_f'+i+'_m0.png'; });
  }
  var CUBE_STATUS_CN={source_verified:"源已验证",partial:"解码不全",unresolved:"未找到"};
  /* ★ 新增（2026-09-20，MERGE_FIX）：自造近似档的**独立分组名**（下拉里单独一段，文案写明非游戏资产）。 */
  var CUBE_SELF_GROUP="自造·近似（非游戏资产）";
  /* 填充下拉。
     ★ 改动（2026-09-20，MERGE_FIX，用户第②条「还有一堆失效的你也不删掉」）：
       原来把清册里**全部 56 项**都建成 option（partial 17 / unresolved 7 灰掉禁用）⇒ 下拉 57 项、24 项禁用。
       用户明确要求**不要留失效项** ⇒ 现在这 24 项**根本不建 option**（不是灰掉，是不出现）。
       下拉 = 1「（manifest 原绑定）」+ 32 项 source_verified + 1 项自造近似 = **34 项**，零禁用项。
       ⚠ 原始枚举台账（含 partial/unresolved 记录）**完整保留**在 data/media/weapon_skin_cubes.js，
         只是在 UI 层不展示 —— 取证链不断，只是不摆在用户面前。
     ★ 自造近似档（status='self_authored_approximate'，**非游戏资产**）：
       显式放行并**单独分组**。该状态**只可能**来自 data/media/weapon_skin_cubes_custom.js
       ⇒ 不削弱「partial/unresolved 不使用替代图」的既有纪律。 */
  function fillCubeSelect(){
    var sel=state.cubeSelect; if(!sel)return 0;
    /* ★ 新增（2026-09-21，SNOWCUBE）：产品默认名提前算，供下面的**视觉**初始化用。 */
    var __pdWant=PD_NAME();
    var idx=window.WIKI_WEAPON_SKIN_CUBES;
    if(!idx||!idx.cubes||!idx.cubes.length){
      if(!sel.dataset.warned){ sel.dataset.warned="1";
        sel.innerHTML='<option value="qiangpi">qiangpi（清册未加载）</option>'; }
      return 0;
    }
    var def=idx.default||'qiangpi', keep=sel.value, n=0, nHidden=0;
    /* ★ 新增（2026-09-21，SNOWCUBE）：把「下拉当前值」与「用户是否真的选过」分开跟踪。
       prev = 用户此前真的动过下拉的选择（空串=「不覆盖」）；首项（value=''）在下面用
       __pdWant 做**视觉**初始化，不会把 prev 当成「用户选了不覆盖」。 */
    var prev=state.__cubePickUserPicked?sel.value:null;
    sel.innerHTML="";
    /* ★ 首项 = **不覆盖**（= manifest 原绑定）。默认停在这一项 ⇒ 打开皮肤时**不改变任何东西**，
       与接线前逐字节同行为；只有用户主动选具体某套时才走 __cubeAB 的取证近似档。 */
    var o0=document.createElement("option");
    o0.value="";
    o0.textContent="（manifest 原绑定·不覆盖）";
    o0.title="不覆盖：沿用 viewer.json / neox_material.json 里 t_custom_ibl 声明的那一套 cube。"
           +"这是打开查看器时的默认状态，本选择器不参与。";
    sel.appendChild(o0);
    var gSrc=document.createElement("optgroup"); gSrc.label="源已验证（source_verified）";
    var gSelf=document.createElement("optgroup"); gSelf.label=CUBE_SELF_GROUP;
    idx.cubes.forEach(function(c){
      if(c.status==="self_authored_approximate"){
        /* ★ 自造近似档（非游戏资产）：显式放行 + 单独分组标注。
           只有 status==='self_authored_approximate' 能走这一支；该状态**只可能**来自
           data/media/weapon_skin_cubes_custom.js ⇒ 不削弱「partial/unresolved 不使用替代图」的既有纪律。 */
        var os=document.createElement("option");
        os.value=c.name;
        os.textContent=c.name+" · 自造近似（非游戏资产）";
        os.dataset.status=c.status;
        os.dataset.isGameAsset="false";
        os.title="**自造近似立方体，非游戏资产**。authority="+(c.authority||"?")
               +"\nmethod="+(c.method||"?")
               +"\nfaces="+(c.faces||[]).length+" 条，编码="+(c.faces_encoding||"?")+"（接入必须用 RGBM 那套："
               +(c.faces||[])[0]
               +"）\n仅用于观察环境反射对观感的影响；不得作为「游戏实际使用该环境」的证据，"
               +"也不得计入「源数据驱动」目标。status="+c.status+"（**故意不在** source_verified/partial/unresolved 枚举内）。";
        if(c.name===keep)os.selected=true;
        gSelf.appendChild(os); n++;
        return;
      }
      if(c.status!=="source_verified"){
        /* ★ 不建 option（原来在这里 o.disabled=true 灰掉），只计数以便在 select.title 里如实交代。 */
        nHidden++;
        return;
      }
      var o=document.createElement("option");
      o.value=c.name;
      o.textContent=c.name+(c.name===def?"（默认）":"")+" · "+(CUBE_STATUS_CN[c.status]||c.status);
      o.dataset.status=c.status;
      o.title="container="+(c.container||"?")+"  row="+(c.row||"?")+"  sha16="+(c.sha16||"?")
             +"  "+(c.dims||"")+"  resolve="+(c.resolve||"?")+"  faces="+(c.faces||[]).length;
      if(c.name===keep)o.selected=true;
      gSrc.appendChild(o); n++;
    });
    if(gSrc.childElementCount)sel.appendChild(gSrc);
    if(gSelf.childElementCount)sel.appendChild(gSelf);
    sel.dataset.hiddenNonusable=String(nHidden);
    sel.title="环境 cube（取证/对比工具，不代表游戏的选择）。"
             +"本下拉只列**可用**项："+n+" 项（32 源已验证 + 1 自造近似）。"
             +"已按用户要求**从下拉移除** "+nHidden+" 项不可用项（partial/unresolved，不使用替代图）；"
             +"原始枚举台账仍完整保留在 data/media/weapon_skin_cubes.js。"
             +"「"+CUBE_SELF_GROUP+"」组内为**自造近似立方体，非游戏资产**。";
    if(!sel.value||sel.selectedIndex<0)sel.value="";   /* 默认 = 不覆盖（manifest 原绑定） */
    if(keep===""||keep===undefined)sel.value="";
    /* ★ 新增：上一次选中的项若本轮已被移除（不可用项不再展示），keep 会落空 ⇒ 显式回到「不覆盖」，
       绝不静默改成另一套 cube。 */
    if(keep&&!cubeIndexOf(keep))sel.value="";
    /* ★ 新增（2026-09-21，SNOWCUBE）：用 prev（用户真实选择）判落空，避免把
       「视觉初始化成产品默认」误当成用户选择。 */
    if(prev&&!cubeIndexOf(prev))sel.value="";
    sel.dataset.cube=sel.value||"(manifest 原绑定)"; sel.dataset.sourceSelector="none";
    var r=cubeIndexOf(sel.value); sel.dataset.status=r?r.status:"manifest_binding";
    state.__cubePickIndex=idx;
    /* ★ 新增（2026-09-21，SNOWCUBE）：若本皮肤声明了产品默认且清册里有它，把下拉
       **视觉上**初始化到那一项（只动 <select> 显示，不动任何 bind；真正 bind 在
       open() 里的 __cubeApplyProductDefault()）。默认名落空 ⇒ 不动下拉，仍然停在
       「不覆盖」，绝不静默换一套 cube。 */
    if(__pdWant&&cubeIndexOf(__pdWant)&&state.__cubePickUserPicked!==true) sel.value=__pdWant;
    else if(state.__cubePickUserPicked===true) sel.value=(prev==null?"":prev);
    state.__cubePickUserPicked=false;
    return n;
  }

  function ensureShell(){
    if(state.shell)return;
    const root=document.createElement("div");
    root.className="wv-root";root.id="weaponSkinViewer";root.hidden=true;
    root.innerHTML=`<button class="wv-backdrop" type="button" tabindex="-1" aria-label="关闭 3D 预览"></button>
      <section class="wv-dialog" role="dialog" aria-modal="true" aria-labelledby="wvTitle" aria-describedby="wvSubtitle">
        <header class="wv-head"><div class="wv-title-wrap"><div class="wv-title" id="wvTitle">3D 预览</div><div class="wv-subtitle" id="wvSubtitle"></div></div><button class="wv-close" type="button" aria-label="关闭 3D 预览">×</button></header>
        <div class="wv-stage"><img class="wv-poster" alt=""><div class="wv-canvas" aria-label="可旋转缩放的武器三维模型"></div><pre class="wv-params" aria-live="off"></pre><button class="wv-copy-params" type="button" title="复制当前相机参数（含模型朝向，可直接发给 AI 复现）">复制参数</button><button class="wv-apply-params" type="button" title="粘贴参数 JSON 以还原视角（与「复制参数」配套）">应用参数</button><div class="wv-loading" role="status" aria-live="polite">准备加载 3D 模型…</div><div class="wv-status" aria-live="polite"></div></div>
        <footer class="wv-tools">
          <label class="wv-state-wrap">形态<select class="wv-state-select" aria-label="选择武器形态"></select></label>
          <label class="wv-camera-wrap">视角<select class="wv-camera-select" aria-label="选择展示视角"></select></label>
          <button class="wv-reset" type="button">复位视角</button>
          <label class="wv-toggle" title="默认关闭：不允许上下（俯仰）旋转；左右旋转不受影响"><input type="checkbox" class="wv-pitch-toggle">上下</label>
          <label class="wv-toggle" title="默认关闭：不允许缩放（滚轮/双指）"><input type="checkbox" class="wv-zoom-toggle">缩放</label>
          <select class="wv-rotaxis" title="左右拖动的旋转轴（可切换，默认世界 Y 轴）">
            <option value="worldY">左右转：世界Y</option>
            <option value="modelY">左右转：模型Y</option>
            <option value="view">左右转：画面内</option>
            <option value="native">左右转：原生</option>
          </select>
          <button class="wv-rot-h" type="button" title="左右旋转 180°（快捷键 H）">H180</button>
          <button class="wv-rot-v" type="button" title="上下旋转 180°（快捷键 V）">V180</button>
          <button class="wv-sfx" type="button" disabled aria-pressed="false">SFX 未提供</button>
          <button class="wv-ibl" type="button" aria-pressed="false" title="IBL 缩放 = 自定义 IBL 的曝光倍数（源 = cb1[239].x u_env_day2night_exposure）。该源常量**尚未取到** ⇒ 默认 0.25 是从 lab_src.html 拷来的值、**无源依据**。此按钮仅供**显示对照**（0.25 ↔ 1.0），不作为源级结论，也不改变默认值。">IBL 缩放 0.25（无源依据）</button>
          <label class="wv-cube-wrap" title="环境立方体（IBL cube）选择器 = **取证/对比工具**，不是源结论。源数据里**没有**任何选择器决定预览该用哪一套 cube：1110025 的两组材质容器 001348.c159 只声明 common\env_map\qiangpi.cube、001360.c159 只声明 common\env_map\jiayuan02a.cube，没有任何字段在两者之间选；special_preview_model_path 只指 .gim 模型、与 cube 无关。故本控件**不代表「游戏就是这么选的」**。默认值不变（仍是 qiangpi）。">环境 cube<select class="wv-cube-select" aria-label="选择环境立方体（IBL cube，取证对比用）"></select><span class="wv-cube-note" style="color:#94a3b8;font-size:9px;white-space:nowrap">取证用·源无选择器</span></label>
          <label class="wv-emis-wrap" title="自发光两档开关（默认全关 = 现状）。A1 源值档：仅 prim3，emissiveMap=该 prim 自身 albedo、emissiveIntensity=0.7（源 001348.c159@4198，仅 M3/prim3），证据等级 source_present_value_unreadable ⇒ 开启时标『源值·近似』。A2 近似档：恢复既有 global_rig.emissive_gain 载体（基色贴图作自发光贴图的全局增益，gain 0.25，approximate）。两档互不耦合、可各自单开。不动曝光/ACES/bloom/灯光/环境强度，不替换贴图。">
            <button class="wv-emis-a1" type="button" aria-pressed="false" title="A1 源值档（默认关）：仅 prim3，emissiveMap=自身 albedo + emissiveIntensity=0.7（源值 001348.c159@4198）。证据等级 source_present_value_unreadable（运行时排列绑定未定证）">自发光A1 源值档：关</button>
            <button class="wv-emis-a2" type="button" aria-pressed="false" title="A2 近似档（默认关）：恢复既有 global_rig.emissive_gain（基色贴图作自发光贴图的全局增益，gain=0.25，approximate）">自发光A2 近似档：关</button>
          </label>
          <span class="wv-spacer"></span><span class="wv-fidelity"></span>
          <button class="wv-fullscreen" type="button">全屏</button>
        </footer>
      </section>`;
    document.body.appendChild(root);
    state.shell=root;state.dialog=root.querySelector(".wv-dialog");state.stage=root.querySelector(".wv-stage");
    state.poster=root.querySelector(".wv-poster");state.params=root.querySelector(".wv-params");state.copyBtn=root.querySelector(".wv-copy-params");state.applyBtn=root.querySelector(".wv-apply-params");state.loading=root.querySelector(".wv-loading");state.status=root.querySelector(".wv-status");
    state.title=root.querySelector(".wv-title");state.subtitle=root.querySelector(".wv-subtitle");
    state.stateSelect=root.querySelector(".wv-state-select");state.cameraSelect=root.querySelector(".wv-camera-select");
    state.sfxButton=root.querySelector(".wv-sfx");state.fidelity=root.querySelector(".wv-fidelity");state.fullscreen=root.querySelector(".wv-fullscreen");
    /* ★ 新增（2026-09-18，用户请求）：把 IBL 缩放做成**页面上可见的开关**（默认仍 0.25 不动）。
       理由：源真值 cb1[239].x(u_env_day2night_exposure) 未取到 ⇒ 改默认即 fitted（用户禁令）。
       故此按钮只做**显示对照**，UI 上明确标注「无源依据」，不写进任何源级结论。 */
    state.iblButton=root.querySelector(".wv-ibl");
    state.iblLabelBase="IBL 缩放 ";
    if(state.iblButton)state.iblButton.addEventListener("click",function(){
      try{
        var cur=(state.iblScale===undefined?1.0:Number(state.iblScale));   /* ★ task-45：默认与渲染主路径统一为 1.0（撤销无源依据常量），按钮组 1.0↔0.25 切换保持不变 */
        var next=(Math.abs(cur-1.0)<1e-6)?0.25:1.0;
        if(window.WikiWeaponViewer&&typeof window.WikiWeaponViewer.__iblParams==="function")
          window.WikiWeaponViewer.__iblParams({scale:next});
        else state.iblScale=next;
        state.iblButton.setAttribute("aria-pressed",String(next===1.0));
        state.iblButton.textContent=state.iblLabelBase+next.toFixed(2)+(next===0.25?"（无源依据）":"（无源依据·显示对照）");
        if(state.status)state.status.textContent="IBL 缩放 = "+next.toFixed(2)+"（无源依据的显示调节；默认 0.25 未改）";
      }catch(e){}
    });
    /* ★★★ 新增（2026-09-20，CUBE_PICKER）：**环境立方体（IBL cube）选择器**。
       定性（必须照抄，不许升级成源结论）：源数据里**没有**选择器决定预览该用哪一套 cube ——
         · 1110025 的两组材质容器各只声明一套：001348.c159 → common\env_map\qiangpi.cube、
           001360.c159 → common\env_map\jiayuan02a.cube，没有任何字段在两者间选；
         · special_preview_model_path 只指 .gim 模型（与 cube 无关），且 1110025 该字段为空；
         · 静态数据里也查不到「预览界面用哪套 cube」的判据。
       ⇒ 本下拉是**取证/对比工具**（diagnostic selector），不代表「游戏就是这么选的」。
       默认值**不变**（仍是 qiangpi）—— 不选中就不碰原有 manifest 绑定路径。
       选项来自 data/media/weapon_skin_cubes.js（本轮按名字哈希枚举 + 解码的源 cube 清册）；
       只有 status==='source_verified' 的才可选，partial/unresolved 一律禁用（**不使用替代图**）。 */
    state.cubeSelect=root.querySelector(".wv-cube-select");
    state.cubeNote=root.querySelector(".wv-cube-note");
    if(state.cubeSelect)state.cubeSelect.addEventListener("change",function(){
      try{
        var v=state.cubeSelect.value;
        /* ★ 新增（2026-09-21，SNOWCUBE）：记录「用户真的动过下拉」。
           选「（manifest 原绑定·不覆盖）」= **明确拒绝**产品默认 ⇒ 记 declined，
           此后开关皮肤不再强加默认。选具体某一套 = picked（= 不是拒绝）。 */
        state.__cubePickUserPicked=true;
        state.__cubeProductDefaultDeclined=(v==="");
        var r=(window.WikiWeaponViewer&&typeof window.WikiWeaponViewer.__cubeAB==="function")
              ? window.WikiWeaponViewer.__cubeAB(v===""?null:v) : null;
        state.__cubePickLast=r;
        /* DOM 镜像一律以**只读探针**为唯一真值源（避免 __cubeAB 的 status 描述的是「实际装载的那套」
           而探针描述的是「当前是否有覆盖」这另一个问题，两者在 null 档会不一致）。 */
        try{ var q=JSON.parse(String(window.WikiWeaponViewer.__cubePickerState()));
             state.cubeSelect.dataset.cube=(q&&q.selected)||"(manifest 原绑定)";
             state.cubeSelect.dataset.status=(q&&q.status)||'unknown';
             state.cubeSelect.dataset.sourceSelector=(q&&q.source_selector)||'none'; }catch(e2){}
        if(state.status)state.status.textContent=(v==="")
          ? "环境 cube = manifest 原绑定（不覆盖；取证选择器未参与）"
          : "环境 cube = "+v+"（取证/对比工具；源数据无选择器，**不代表游戏的选择**；默认档仍为 manifest 原绑定）";
      }catch(e){}
    });
    fillCubeSelect();
    /* ★ 新增（2026-09-18，lead 批准）：三个**默认关**的诊断开关，用于分离基础层过曝三因。
       一律 UI 标注「诊断用·非源级」，默认 = 原值/原图/ACES ⇒ **不改变任何现有行为**。
         ① __diagLight(on)：hemi/key/fill 强度整体归 0（还原时按备份恢复）
         ② __diagAlb(on)  ：晶体 map 临时换 1×1 中性灰（只改运行时纹理，不碰磁盘/资产/manifest；
                            保留 USE_MAP 定义 ⇒ `vMapUv` 与晶体注入不受影响）
         ③ __diagTone(on) ：ACES ↔ NoToneMapping（只切 tone mapping，不动 exposure） */
    (function(){
      var bar=state.sfxButton&&state.sfxButton.parentElement; if(!bar)return;
      var mk=function(label,title){ var b=document.createElement("button"); b.type="button";
        b.textContent=label; b.title=title; b.setAttribute("aria-pressed","false"); bar.appendChild(b); return b; };
      var dL=document.createElement("span"); dL.className="wv-dgl"; dL.textContent="直接光 ×1.00（诊断用·非源值）";
      dL.title="诊断：hemi/key/fill 强度按倍率等比缩放，分离直接光贡献。默认 ×1.00 = 源值，仅诊断。"; bar.appendChild(dL);
      var _LKS=[];
      [1,0.75,0.5,0.25,0].forEach(function(kv){ var b=document.createElement("button"); b.type="button";
        b.className="wv-dg"; b.dataset.k=String(kv); b.textContent="×"+kv.toFixed(2);
        b.setAttribute("aria-pressed", kv===1?"true":"false");
        b.addEventListener("click",function(){ window.__diagLight(kv); }); bar.appendChild(b); _LKS.push(b); });
      var dA=mk("albedo 原图（诊断用·非源级）","诊断：晶体 map 临时换 1×1 中性灰（只改运行时，不改磁盘），分离暖 albedo 贡献。默认=原图。");
      var dT=mk("tonemap ACES（诊断用·非源级）","诊断：ACES ↔ NoToneMapping，只切 tone mapping、不动 exposure。默认=ACES。");
      var _L=null, _A=[], _T=null;
      window.__diagLight=function(k){ try{ var s=state.scene; if(!s)return 'no scene';
        if(typeof k==='boolean')k=k?0:1; if(k===undefined||k===null)k=1;
        k=Number(k); if(!isFinite(k))k=1; k=Math.max(0,Math.min(1,k));
        if(!_L){ _L=[]; s.traverse(function(o){ if(o.isLight)_L.push({o:o,i:o.intensity}); }); }
        _L.forEach(function(x){ x.o.intensity=x.i*k; });
        dL.textContent="直接光 ×"+k.toFixed(2)+"（诊断用·非源值）";
        _LKS.forEach(function(b){ b.setAttribute("aria-pressed", Math.abs(Number(b.dataset.k)-k)<1e-6?"true":"false"); });
        try{_forceRender();}catch(e){} return JSON.stringify({lights:_L?_L.length:0,k:k}); }catch(e){ return 'ERR '+e; } };
      window.__diagAlb=function(on){ try{ var T=state.THREE; if(!T||!state.scene)return 'no scene';
        if(!state.__grayTex){ state.__grayTex=new T.DataTexture(new Uint8Array([128,128,128,255]),1,1); state.__grayTex.needsUpdate=true; }
        var n=0; state.scene.traverse(function(o){ if(!o.isMesh)return; var m=o.material; if(Array.isArray(m))m=m[0];
          if(!m||!m.userData||!m.userData.chain||m.userData.chain.kind!=='crystal')return;
          if(on){ if(!m.userData.__savedMap){ m.userData.__savedMap=m.map; _A.push(m); } m.map=state.__grayTex; }
          else if(m.userData.__savedMap){ m.map=m.userData.__savedMap; delete m.userData.__savedMap; }
          m.needsUpdate=true; n++; });
        dA.textContent="albedo "+(on?"中性灰":"原图")+"（诊断用·非源级）"; dA.setAttribute("aria-pressed",String(!!on));
        try{_forceRender();}catch(e){} return JSON.stringify({mats:n,on:!!on}); }catch(e){ return 'ERR '+e; } };
      window.__diagTone=function(on){ try{ var r=state.renderer; if(!r)return 'no renderer';
        if(on){ if(_T===null)_T=r.toneMapping; r.toneMapping=state.THREE.NoToneMapping; }
        else if(_T!==null){ r.toneMapping=_T; }
        dT.textContent="tonemap "+((_T!==null)?"NoToneMapping":"ACES")+"（诊断用·非源级）"; dT.setAttribute("aria-pressed",String(!!on));
        try{_forceRender();}catch(e){} return JSON.stringify({toneMapping:r.toneMapping}); }catch(e){ return 'ERR '+e; } };
      dL.addEventListener("click",function(){}); /* dL 现为倍率读数标签，缩放改由 ×1.00/×0.75/×0.50/×0.25/×0 按钮组驱动 */
      dA.addEventListener("click",function(){ window.__diagAlb(dA.getAttribute("aria-pressed")!=="true"); });
      dT.addEventListener("click",function(){ window.__diagTone(dT.getAttribute("aria-pressed")!=="true"); });
    })();
    root.querySelector(".wv-backdrop").addEventListener("click",close);
    root.querySelector(".wv-close").addEventListener("click",close);
    root.querySelector(".wv-reset").addEventListener("click",()=>{rebuildControls();applyCamera(selectedCamera(),true);});
    state.pitchToggle=root.querySelector(".wv-pitch-toggle");state.zoomToggle=root.querySelector(".wv-zoom-toggle");
    state.pitchToggle.addEventListener("change",()=>{state.allowPitch=state.pitchToggle.checked;state.pinnedPolar=null;state.pinnedUp=null;state.pinnedUp0=null;state.baseAz=null;state.pinnedUp0=null;state.baseAz=null;
      if(state.status)state.status.textContent=state.allowPitch?"上下旋转：已允许":"上下旋转：已锁定（可左右旋转）";});
    state.zoomToggle.addEventListener("change",()=>{state.allowZoom=state.zoomToggle.checked;
      if(state.controls)state.controls.noZoom=!state.allowZoom;
      if(state.status)state.status.textContent=state.allowZoom?"缩放：已允许":"缩放：已锁定";});
    // 左右拖动旋转轴：可在面板切换（默认世界 Y 轴=过模型中心），用户可自选，不由代码猜
    state.rotMode="worldY";
    (function(){var sel=root.querySelector(".wv-rotaxis");if(!sel)return;
      state.rotMode=sel.value||"worldY";
      sel.addEventListener("change",function(){state.rotMode=sel.value;
        if(state.controls)state.controls.noRotate=(sel.value==="native");
        if(state.status)state.status.textContent="左右旋转轴："+({worldY:"世界 Y 轴（过模型中心）",modelY:"模型自身 Y 轴",view:"画面平面内",native:"原生自由"})[sel.value];});
    })();
    root.querySelector(".wv-rot-h").addEventListener("click",()=>rotate180("h"));
    root.querySelector(".wv-rot-v").addEventListener("click",()=>rotate180("v"));
    state.stateSelect.addEventListener("change",()=>loadSelectedState());
    state.cameraSelect.addEventListener("change",()=>applyCamera(selectedCamera(),true));
    state.sfxButton.addEventListener("click",toggleEffects);
    state.fullscreen.addEventListener("click",toggleFullscreen);
    /* ★ 新增（2026-09-20，EMISTOGGLE）：自发光 A1/A2 两个**默认关**的开关接到页面控件。
       点击只改运行期 state 并重建材质层（applyMaterialLayers），**不写任何文件**；
       文案上把 A1 的来源与「近似」属性写死，避免被读成源级已验证。 */
    (function(){
      var b1=root.querySelector(".wv-emis-a1"),b2=root.querySelector(".wv-emis-a2");
      var sync=function(){
        var st=state.__emissiveState||{source:{},approx:{}};
        var s=!!(st.source&&st.source.enabled),a=!!(st.approx&&st.approx.enabled);
        if(b1){ b1.setAttribute("aria-pressed",String(s));
          b1.textContent="自发光A1 源值档："+(s?("开·prim"+(st.source.prim!==undefined?st.source.prim:3)+"×"+(st.source.strength!==undefined?st.source.strength:0.7)+"（源值·近似）"):"关"); }
        if(b2){ b2.setAttribute("aria-pressed",String(a));
          b2.textContent="自发光A2 近似档："+(a?("开·gain "+(st.approx.gain!==undefined?st.approx.gain:0.25)):"关"); }
      };
      var apply=function(){ try{ emisRun(); }catch(e){} try{ if(state.root)applyMaterialLayers(state.root); }catch(e){} try{_forceRender&&_forceRender();}catch(e){} sync();
        if(state.status){ var st=state.__emissiveState||{};
          state.status.textContent="自发光开关：A1(源值档,仅prim3,0.7)="+((st.source&&st.source.enabled)?'开':'关')
            +" / A2(近似档,gain 0.25)="+((st.approx&&st.approx.enabled)?'开':'关')+"（默认全关；A1 标源值·近似）"; } };
      if(b1)b1.addEventListener("click",function(){ state.__emissiveState.source.enabled=!state.__emissiveState.source.enabled; apply(); });
      if(b2)b2.addEventListener("click",function(){ state.__emissiveState.approx.enabled=!state.__emissiveState.approx.enabled; apply(); });
      state.__emisSync=sync; sync();
    })();
    if(state.copyBtn)state.copyBtn.addEventListener("click",()=>{
      const txt=paramsText(true);
      const done=()=>{state.copyBtn.textContent="已复制";setTimeout(()=>{state.copyBtn.textContent="复制参数";},1500);};
      if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(txt).then(done).catch(()=>fallbackCopy(txt,done));
      else fallbackCopy(txt,done);
    });
    /* ★ 新增（2026-09-17）：应用参数 —— 与「复制参数」配套，使复制/粘贴闭环。
       还原 target / position(按 distance 归一) / up / fov / span / 形态 / 模型朝向(model_rot)。
       模型朝向按 quat → yaw_deg → euler_deg 优先级取（quat 最准确）。
       注意：本查看器的拖动是转**模型**（applyOrbit），相机全程不动，故必须一并还原 model_rot，
       否则「粘贴参数」只会回到初始姿态。 */
    /* 导出放到文件后段（window.WikiWeaponViewer 创建之后）——此处过早赋值会因对象不存在而抛异常。 */
    if(state.applyBtn)state.applyBtn.addEventListener("click",()=>{
      const raw=window.prompt('粘贴参数 JSON（会立即应用到当前视角）：');
      if(raw===null)return;
      if(typeof window.__applyParamsJSON!=='function'){ if(state.status)state.status.textContent='应用参数未就绪'; return; }
      const r=window.__applyParamsJSON(raw);
      state.applyBtn.textContent=r.ok?'已应用':'应用失败';
      if(!r.ok&&state.status)state.status.textContent='参数应用失败：'+(r.err||'');
      setTimeout(()=>{ state.applyBtn.textContent='应用参数'; },1800);
    });
    root.addEventListener("keydown",onDialogKey);
    document.addEventListener("keydown",event=>{
      if(state.shell.hidden)return;
      const tag=(event.target&&event.target.tagName||"").toLowerCase();
      if(tag==="input"||tag==="select"||tag==="textarea")return;
      const k=String(event.key||"").toLowerCase();
      if(k==="h"){event.preventDefault();rotate180("h");}
      else if(k==="v"){event.preventDefault();rotate180("v");}
    });
    document.addEventListener("fullscreenchange",()=>{if(state.fullscreen)state.fullscreen.textContent=document.fullscreenElement?"退出全屏":"全屏";});
  }

  function setLoading(message,error){
    if(!state.loading)return;
    state.loading.textContent=message||"";
    state.loading.hidden=!message;
    state.loading.dataset.error=error?"1":"0";
  }

  function showPoster(src,alt){
    if(!state.poster)return;
    if(src){state.poster.src=src;state.poster.alt=alt||"武器预览海报";state.poster.hidden=false;}
    else{state.poster.removeAttribute("src");state.poster.alt="";state.poster.hidden=true;}
  }

  function normalizeCollection(value,fallbackLabel){
    if(Array.isArray(value))return value.filter(isObject);
    if(isObject(value))return Object.entries(value).map(([id,v])=>({id,label:(v&&v.label)||fallbackLabel||id,...(isObject(v)?v:{model:v})}));
    return [];
  }

  function absoluteUrl(path,base){
    if(!path)return "";
    try{return new URL(String(path),base||location.href).href;}catch(_){return String(path);}
  }

  async function resolveConfig(record){
    const inline=isObject(record.preview_3d)?record.preview_3d:{};
    let config={...inline},base=location.href;
    if(inline.manifest){
      const manifestUrl=absoluteUrl(inline.manifest,location.href);
      const response=await fetch(manifestUrl,{cache:"no-store"});
      if(!response.ok)throw new Error(`3D 清单读取失败（HTTP ${response.status}）`);
      const manifest=await response.json();
      if(!isObject(manifest))throw new Error("3D 清单格式无效");
      state.manifestUrl=manifestUrl;base=manifestUrl;
      config={...inline,...manifest,manifest:inline.manifest};
    }else state.manifestUrl=null;
    let states=normalizeCollection(config.states,"默认");
    if(!states.length&&config.model)states=[{id:"default",label:"默认",model:config.model,scene:config.scene}];
    if(!states.length)throw new Error("3D 清单没有可加载的模型形态");
    states=states.map((item,index)=>({...item,id:String(item.id||`state-${index+1}`),label:item.label||item.name||`形态 ${index+1}`,model:absoluteUrl(item.model,base)}));
    if(states.some(item=>!item.model))throw new Error("3D 形态缺少 model 路径");
    const cameras=normalizeCollection(config.camera_presets||config.cameras,"视角").map((item,index)=>({...item,id:String(item.id||`camera-${index+1}`),label:item.label||item.name||`视角 ${index+1}`}));
    return {...config,_base:base,_states:states,_cameras:cameras};
  }

  function fillSelect(select,items,selected){
    select.innerHTML=items.map(item=>`<option value="${esc(item.id)}">${esc(item.label)}</option>`).join("");
    if(selected&&items.some(item=>item.id===String(selected)))select.value=String(selected);
    select.parentElement.hidden=items.length<2;
  }

  async function ensureRuntime(){
    if(!state.runtimePromise){
      state.runtimePromise=Promise.all([import(runtimeUrls.three),import(runtimeUrls.loader),import(runtimeUrls.controls),import(runtimeUrls.trackball)])
        .then(([THREE,loader,controls,trackball])=>({THREE,GLTFLoader:loader.GLTFLoader,OrbitControls:controls.OrbitControls,TrackballControls:trackball.TrackballControls}));
    }
    const rt=await state.runtimePromise;
    state.THREE=rt.THREE;state.GLTFLoader=rt.GLTFLoader;state.OrbitControls=rt.OrbitControls;state.TrackballControls=rt.TrackballControls;
    return rt;
  }

  function configureScene(){
    disposeScene();
    const THREE=state.THREE,config=state.config||{};
    state.scene=new THREE.Scene();
    state.scene.background=new THREE.Color(config.background||"#071015");
    state.camera=new THREE.PerspectiveCamera(Number(config.fov)||36,1,.01,10000);
    state.renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:"high-performance"});
    state.renderer.outputColorSpace=THREE.SRGBColorSpace;
    /* ★ 改动（2026-09-18，task-29）：toneMapping 改为**配置驱动**（默认 ACESFilmic = 原写死值）；
       exposure 的默认显式化且 **0 合法**（原 `Number(config.exposure)||1` 会把 0 吃掉）。 */
    state.renderer.toneMapping=toneMapOf(THREE,config);
    state.renderer.toneMappingExposure=numCfg(config.exposure,1);
    state.renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
    state.renderer.domElement.setAttribute("aria-label","可旋转缩放的武器三维模型");
    const canvasHost=state.shell.querySelector(".wv-canvas");canvasHost.replaceChildren(state.renderer.domElement);
    /* ★ 同上：三盏 rig 灯的强度同样走 numCfg（默认 1.35/2.2/0.75 = 原写死值，0 合法）。 */
    const hemi=new THREE.HemisphereLight(config.sky_color||0xffffff,config.ground_color||0xffffff,numCfg(config.hemisphere_intensity,1.35));
    /* ★★ Lead 20260920（task-11，任务一+任务二）：**可选 rig 灯**（两个开关都缺省 ⇒ 与改动前逐字相同）。
       `rigOn` = `config.key_shadow`（任务一：要投阴影就必须有一盏**可见**的投影灯）
               或 `config.direct_light`（任务二：恢复 three 标准直接光项）。
       为什么"可见"是硬前提：three 的 `projectObject()` 对 `object.visible===false` **直接 return**
         ⇒ 该灯既不进 `currentRenderState.pushLight`（⇒ `NUM_DIR_LIGHTS=0`，直接光项在编译期被整段删掉），
            也不进 `pushShadow`（⇒ 阴影贴图根本不渲染）。见本文件 CLEAR_ALWAYS 块内的修复注释。
       `config.key_dir` = 主光**位置方向**（"光从哪来"），**仅在 rigOn 时读取**；
         rigOn=false ⇒ 仍是写死的 (3,4,5)，默认帧逐字节不变。
       证据等级：方向的**具体数值**为 `approximate_direction_from_reference_screenshot`
         （参考图 `REF_game_1110025.png` 是 732×273 裁剪，无法反解真实光源）；
         但"屏幕 ↔ 世界轴"的映射是**实测**的（`__expAxes([0,0,0])` 截图 +
         `__state().proj` 与手算逐位一致；见 SHADOW_TUNE_20260920.md §1）。 */
    const rigOn=!!(config.key_shadow||config.direct_light);
    const keyDir=(rigOn&&Array.isArray(config.key_dir)&&config.key_dir.length>=3)?config.key_dir.map(Number):[3,4,5];
    /* 任务二：直接光通道。`direct_light_intensity` 优先于 `key_intensity`（本皮肤 viewer.json 把
       key/fill/hemisphere 全设 0，故直接光必须有自己的强度字段，否则开关开了也是黑）。
       只动**直接光**这一个通道：不改曝光 / toneMapping / bloom / env_intensity。 */
    const keyInt=config.direct_light?(numCfg(config.direct_light_intensity,numCfg(config.key_intensity,2.2))):numCfg(config.key_intensity,2.2);
    const key=new THREE.DirectionalLight(config.key_color||0xffffff,keyInt);
    key.position.set(keyDir[0],keyDir[1],keyDir[2]);
    /* ★ 灯是新建的，但 `state` 不重建（见 disposeScene）⇒ 每帧清掉 QA 探针在灯上留的备份，
       否则换 manifest 后 `__shadowToggleQa(null)` 会把"上一轮已改小的 near/far"当成原值还原
       ⇒ 关影帧与开影帧变成同一帧、影子指标恒为 0。 */
    try{ delete key.__qaNear; delete key.__qaFar; }catch(e){ key.__qaNear=undefined; key.__qaFar=undefined; }
    const fill=new THREE.DirectionalLight(config.fill_color||0xffffff,numCfg(config.fill_intensity,.75));fill.position.set(-4,1,-3);
    state.scene.add(hemi,key,fill);
    /* ★★★ LASTMILE 20260920（S1）：**强制全局光照近似**（用户授权手填 ⇒ 证据等级 approximate，**非源数据**）。
       背景（用户判定「还是不像」，要求枪身近纯白/饰件明确金色带高光）：
         · 本皮肤 `viewer.json` 的 rig 三灯强度全为 0（源中立），渲染只剩 IBL；
         · 32 套可选环境 cube **全是"暗棚"捕获**（最亮 `car_studio01` p50 0.5093 / p95 0.9375 /
           >0.85 仅 7.49%）⇒ 换 cube **结构性地**补不齐亮度，不是选型问题；
         · 源侧真实光照能量字段（`u_env_sh` / `u_ambient×u_char_ambient` / `u_dir_color` /
           `u_scene_ao_factors` / `t_realtime_env_spec` / 未在 manifest 声明的 `u_cube_brightness`）
           是**运行时 cbuffer**，静态不可得 ⇒ 无法"按源接入"。
       处置：用户 2026-09-20 明确授权手填本项以改善观感。**近似项，必须集中登记**，页面文案同步标注。
       纪律（本块严格遵守）：
         · **不触碰** exposure / toneMapping / bloom 任何数值 / rig 三灯（hemi·key·fill）强度
           —— 那是**既有**通道；本项是**新增**的一盏灯，与 rig 并存、可单独摘除；
         · `lighting_approx.enabled=false` ⇒ 整块不执行 ⇒ **一键回源态**（与改动前逐字同帧）；
         · 不得据此外报"已完成源数据驱动"。
       测档钩子 `window.__LASTMILE_S1_INTENSITY`（仅内存、仅供四档对比测量；manifest 不写该键）。 */
    try{
      const __la=(config&&config.lighting_approx)||null;
      state.__lightingApprox=null;state.__lightingApproxMeta=null;
      if(__la&&__la.enabled){
        let __laI=numCfg(__la.intensity,0);
        const __ovr=Number(window.__LASTMILE_S1_INTENSITY);
        if(Number.isFinite(__ovr))__laI=__ovr;                 /* 测档覆盖，仅内存 */
        const __laLight=new THREE.HemisphereLight(__la.sky_color||0xffffff,
                                                  __la.ground_color||0xffffff,__laI);
        __laLight.name='lastmile_lighting_approx';
        state.scene.add(__laLight);
        state.__lightingApprox=__laLight;
        state.__lightingApproxMeta={enabled:true,mode:__la.mode||'hemisphere_ambient',
          intensity:__laI,configured_intensity:numCfg(__la.intensity,0),
          overridden_by_test_hook:Number.isFinite(__ovr),
          authority:__la.authority||'',fidelity:__la.fidelity||'approximate'};
      }
      window.__lastmileS1Set=function(v){
        if(!state.__lightingApprox)return null;
        const n=Number(v);
        if(Number.isFinite(n))state.__lightingApprox.intensity=n;
        return state.__lightingApprox.intensity;
      };
      window.__lastmileS1State=function(){
        const m=state.__lightingApproxMeta;
        return m?JSON.stringify({present:true,intensity:state.__lightingApprox?state.__lightingApprox.intensity:null,
          mode:m.mode,authority:m.authority,fidelity:m.fidelity,
          overridden_by_test_hook:m.overridden_by_test_hook,configured_intensity:m.configured_intensity})
          :JSON.stringify({present:false});
      };
    }catch(e){ state.__lightingApprox=null; state.__lightingApproxMeta=null; }
    state.__rigOn=rigOn;
    state.__keyDir=keyDir.slice();
    /* ★★ Lead 20260920：**可选**打光/阴影通道（配置驱动，默认关 ⇒ 既有皮肤逐字节不变）。
       背景（用户实拍对比）：游戏内皮肤预览里武器会在场景上投下**随朝向变化**的影子；而本查看器
       此前三盏 rig 灯强度被置 0（`numCfg(0,d)` 会让 0 合法透传 ⇒ 灯全灭，只剩 IBL），并且
       **全文没有 shadowMap / castShadow / receiveShadow** ⇒ 是**结构性缺失**，不是调参问题
       （证据：`numCfg` 定义 + 三灯强度字段 + 全文关键字计数 0）。
       本块只在 `config.key_shadow` 为真时执行：
         · renderer.shadowMap + key.castShadow（正交阴影相机，范围/偏移可配）
         · 一块**只显示阴影**的 `ShadowMaterial` 地板（不引入可见地面几何，不遮挡背景图）
         · 模型 mesh 的 castShadow 由 tick 懒标记（模型可被重建，故按 root 记一次）
       关闭时整块不执行 ⇒ 默认态与改动前一致（验收负控要求逐字节相同）。 */
    state.keyShadow=!!config.key_shadow;
    /* ★ 任务：平台开启时，旧 ShadowMaterial 地板默认被移除（见 platform 块）。
       此时若 `key_shadow` 也开，`state.shadowFloor` 会是 `null` ⇒ `__rigState` 里
       `shadowFloor:null` 是"被平台取代"的正常状态，不是缺陷。 */
    if(state.keyShadow){
      state.renderer.shadowMap.enabled=true;
      state.renderer.shadowMap.type=THREE.PCFSoftShadowMap;
      /* ★★ Lead 20260920：`key.castShadow` 只有在 **key.visible=true** 时才真的产出 shadow map
         （three 的 projectObject 对不可见灯直接 return）—— 这就是 `state.__rigOn` 同时被
         `key_shadow` 点亮的理由，见 CLEAR_ALWAYS 块内的修复注释。 */
      key.castShadow=true;
      /* ★ 调参后的缺省（task-11 任务一）：extent 9→12（实测阴影足迹在光空间横向达 ±10.0，
         9 会把两端切掉）；floor_y −6→+2.4（原 −6 是 PMREM 环境地板的 y，在屏幕上跑到模型**上方**，
         永远接不到投影；+2.4 才把地板平面投在背景板栅格地面上，见 SHADOW_TUNE_20260920.md §1）。
         注意：这两个缺省**只在 key_shadow 为真时生效** ⇒ 缺省帧逐字节不变。
         ★ 平台开启时，`platform.shadow_*` 覆盖这里的字段（在平台块里应用）。 */
      const ext=numCfg(config.key_shadow_extent,12);
      const ms=numCfg(config.key_shadow_map,2048);
      key.shadow.mapSize.set(ms,ms);
      const sc=key.shadow.camera;
      sc.left=-ext; sc.right=ext; sc.top=ext; sc.bottom=-ext;
      sc.near=numCfg(config.key_shadow_near,.5); sc.far=numCfg(config.key_shadow_far,40);
      sc.updateProjectionMatrix();
      key.shadow.bias=numCfg(config.key_shadow_bias,-0.0006);
      key.shadow.normalBias=numCfg(config.key_shadow_normal_bias,.02);
      const floor=new THREE.Mesh(new THREE.PlaneGeometry(ext*6,ext*6),
        new THREE.ShadowMaterial({opacity:numCfg(config.key_shadow_opacity,.42)}));
      floor.rotation.x=-Math.PI/2;
      floor.position.y=numCfg(config.key_shadow_floor_y,2.4);
      floor.receiveShadow=true; floor.name='__shadowFloor';
      state.shadowFloor=floor;
      state.scene.add(floor);
    }
    /* ★★ Lead 20260920（task：展示平台 + 阴影定标）：**可选**「展示平台」= 一块**有厚度、带前缘直角**的台面。
       用户原话（看游戏内整屏截图，圈出地板前缘拐角）："类似桌子拐角处" —— 即游戏里地面是一块**有厚度、
       有前缘直角的台面**；要求 wiki 预览里也有这块台面，且武器要把影子投在上面。
       证据：`REF_SHADOW_TARGETS_20260920.md`（同房间 NCC 0.9117、地板带、影子 −0.1527@x=591）+
       `platform_analysis/`（本代理重测：台面顶边 / 前缘逐列 / 拐角红圈 / 格栅周期 / 纹理来源像素）。

       设计口径（与旧 `key_shadow` 的 ShadowMaterial 地板**互补，不冲突**）：
         · `config.platform.enabled` 默认 **false** ⇒ 整块不执行，默认帧与改动前逐字节一致（负控）。
         · 台面用**真实像素**做纹理（来自参考图/背景板裁剪，见 `1110025\platform\README.txt`），
           不手绘；若只用近似颜色，`color_from_reference_screenshot` 标为近似。
         · **拐角**由几何天然给出：台面（水平面）+ 前缘面（竖直面）在 z_front 处相交，
           左右两侧再补两块竖侧面 ⇒ 前缘是一条**直角棱**，随相机转动始终是直角（不是画上去的）。
         · 台面 `receiveShadow=true` 且 `castShadow=true`（能接影、也能对下方投影）。
         · 阴影：本块**不重复造投影灯**。若 `key_shadow` 未开，则本块自己把 `renderer.shadowMap` +
           `key.castShadow`（那盏 rig key 灯）打开，并允许 `platform.shadow_*` 覆盖原 `key_shadow_*`
           缺省 ⇒ 单独开 `platform` 也能有影可看。
         · 反向开关 `config.platform_keep_key_shadow_floor=false`：平台开启时**移除**旧的
           `ShadowMaterial` 地板（否则同平面两块阴影面会**双重压暗**）。 */
    state.platformOn=!(!config.platform||config.platform.enabled!==true);
    if(state.platformOn){
      const p=(config.platform&&typeof config.platform==='object')?config.platform:{};
      const pnum=(v,d)=>numCfg(v,d);
      const psize=Array.isArray(p.size)&&p.size.length>=2?p.size:[16,10];
      const px0=pnum(p.x,0);
      const pz0=pnum(p.z,0);
      const py0=pnum(p.y,1);
      const pth=Math.max(1e-3,pnum(p.thickness,.5));
      const pdx0=psize[0]*pnum(p.repeat_x,1);
      const pdz0=psize[1]*pnum(p.repeat_y,1);
      /* ★ `shadow_strength`（0..1，默认 1）：平台**只接受多少比例的键光**。
         为什么需要它：任务要求"台面最暗处相对同区域无影帧下降 0.10~0.15"，而灯全开时
         实测暗化达 0.44（比参考图的 0.1527 重得多）。`platform.shadow_strength` 与
         `platform.color` 联动（灯泡 → 同时把 albedo 提亮）即可在**不碰曝光/ACES/环境强度/
         武器材质**的前提下把"影子绝对压暗量"标到目标区间。 */
      let pst=pnum(p.shadow_strength,1);
      pst=Math.max(0,Math.min(1,pst));
      const pColorScale=(pst>1e-6)?(1.0/pst):1.0;
      const T=new THREE.TextureLoader();
      const baseT=state.manifestUrl||location.href;
      const load=(rel,wrap)=>{
        if(!rel) return Promise.resolve(null);
        const u=new URL(rel,baseT).href;
        return new Promise(res=>T.load(u,t=>{
          t.colorSpace=THREE.SRGBColorSpace;
          t.wrapS=t.wrapT=THREE.RepeatWrapping;
          t.anisotropy=(state.renderer&&state.renderer.capabilities)?state.renderer.capabilities.getMaxAnisotropy():1;
          t.repeat.set(wrap[0],wrap[1]);
          res(t);
        },undefined,()=>res(null)));
      };
      /* 旧地板与平台同平面会双重压暗 ⇒ 平台开启时按开关移除（默认移除）。 */
      if(state.shadowFloor&&config.platform_keep_key_shadow_floor!==true){
        state.scene.remove(state.shadowFloor);
        if(state.shadowFloor.geometry)state.shadowFloor.geometry.dispose();
        if(state.shadowFloor.material)state.shadowFloor.material.dispose();
        state.shadowFloor=null;
      }
      if(!config.key_shadow){
        state.renderer.shadowMap.enabled=true;
        if(state.renderer.shadowMap.type===undefined||!config.key_shadow)
          state.renderer.shadowMap.type=THREE.PCFSoftShadowMap;
        key.castShadow=true;
      }
      /* ★ 平台自己那套阴影相机参数：**无论 key_shadow 开不开都应用**，
         这样平台单独开（key_shadow 缺省）时，阴影范围也由 platform.shadow_* 决定，
         而不是被 key_shadow 的缺省挡住。只在确实提供了值时覆盖，否则保留 key_shadow 算出的值。
         参数同时抄给 `__platformSoftKey`（平台补光），否则"关影子"探针改不到它。 */
      const SH_EXT=pnum(p.shadow_extent,numCfg(config.key_shadow_extent,12));
      const SH_MAP=pnum(p.shadow_map,numCfg(config.key_shadow_map,2048));
      const SH_NEAR=pnum(p.shadow_near,numCfg(config.key_shadow_near,.5));
      const SH_FAR=pnum(p.shadow_far,numCfg(config.key_shadow_far,40));
      const SH_BIAS=pnum(p.shadow_bias,numCfg(config.key_shadow_bias,-0.0006));
      const SH_NBIAS=pnum(p.shadow_normal_bias,numCfg(config.key_shadow_normal_bias,.02));
      {
        key.shadow.mapSize.set(SH_MAP,SH_MAP);
        const psc=key.shadow.camera;
        psc.left=-SH_EXT; psc.right=SH_EXT; psc.top=SH_EXT; psc.bottom=-SH_EXT;
        psc.near=SH_NEAR; psc.far=SH_FAR;
        psc.updateProjectionMatrix();
        key.shadow.bias=SH_BIAS;
        key.shadow.normalBias=SH_NBIAS;
      }
      const grp=new THREE.Group(); grp.name='__platform';
      /* ★ pitch_deg：台面绕世界 X 轴的**前倾角**。为什么需要：本查看器 game_reference 相机
         几乎**水平**（相机 y=-2.09、视线 y 分量 +0.14、up=(-0.83,-0.56,-0.10)），水平面在屏幕上
         几乎是**一条线**（实测 y=3 时可见深度仅 1.14 单位 → 屏幕上 ~6px），照不出"台面"。
         前倾 60° 后水平面才有可见面积，且**前缘仍是一条直线棱**（面积足够、直角仍在）。 */
      const pitch=(pnum(p.pitch_deg,0))*Math.PI/180;
      const baseCol=new THREE.Color(p.color||0xffffff);
      const topMat=new THREE.MeshStandardMaterial({color:baseCol,
        roughness:pnum(p.roughness,.82),metalness:pnum(p.metalness,.15),
        side:THREE.DoubleSide,envMapIntensity:pnum(p.env_intensity,.35)});
      const frontMat=new THREE.MeshStandardMaterial({color:new THREE.Color(p.front_color||0x8f9a92),
        roughness:pnum(p.front_roughness,.6),metalness:pnum(p.front_metalness,.25),
        side:THREE.DoubleSide,envMapIntensity:pnum(p.front_env_intensity,.35)});
      const sideMat=new THREE.MeshStandardMaterial({color:new THREE.Color(p.side_color||0x4a5450),
        roughness:pnum(p.side_roughness,.75),metalness:pnum(p.side_metalness,.2),
        side:THREE.DoubleSide,envMapIntensity:pnum(p.side_env_intensity,.3)});
      /* ★★ `shadow_strength`（0..1，默认 1）—— 把"影子压暗量"标到参考图区间用的**平台专用补光**。
         原理：影子只吃掉"直接光那一份"。给平台额外加一盏**只照平台**（three 的 `layers` 隔离）
         的同向平行光，强度 = keyInt·(1−s)；则
             台面亮处亮度  ≈ 原来的 (1−s) + 影子里被保住的那份 ⇒ **外观基本不变**
             影子压暗量    ≈ 原来的 s 倍 ⇒ 可直接按 s 标定
         只影响平台网格（`layers.set(1)`），**不碰武器、不碰曝光/ACES/bloom/环境强度**。 */
      /* ★★ `shadow_strength`（0..1，默认 1）——**影子压暗量的标定旋钮**。
         ⚠ 实测限制（本代理 2026-09-20）：把平台挪到"专用灯光层 + 非投影补光"来缩弱影子时，
         平台会**完全收不到投影灯的直接光**（三组 fill 扫描均 Δ=0.0000，材质 needsUpdate 无效），
         影子与平台一起消失 ⇒ 该分支不可用于交付，交付配置一律用 **1.0**（保留默认灯光层）。
         保留字段是为了**记录这条负面结论**，不是推荐开启。 */
      const sshadow=Math.max(0.0,Math.min(1.0,pnum(p.shadow_strength,1)));
      if(sshadow<0.999){
        const soft=new THREE.DirectionalLight(key.color?key.color.getHex():0xffffff,keyInt*sshadow);
        soft.position.copy(key.position);
        soft.name='__platformSoftKey';
        soft.layers.set(1);
        soft.castShadow=true;
        soft.shadow.mapSize.set(SH_MAP,SH_MAP);
        const ssc=soft.shadow.camera;
        ssc.left=-SH_EXT; ssc.right=SH_EXT; ssc.top=SH_EXT; ssc.bottom=-SH_EXT;
        ssc.near=SH_NEAR; ssc.far=SH_FAR;
        ssc.updateProjectionMatrix();
        soft.shadow.bias=SH_BIAS;
        soft.shadow.normalBias=SH_NBIAS;
        state.scene.add(soft);
        state.platformSoftKey=soft;
        const fk=pnum(p.fill_key,1.0);
        const fill2=new THREE.HemisphereLight(pnum(p.fill_sky,0xdff0ff),pnum(p.fill_ground,0x203030),
          keyInt*(1.0-sshadow)*fk);
        fill2.name='__platformFill';
        fill2.layers.set(1);
        state.scene.add(fill2);
        state.platformFill=fill2;
        [topMat,frontMat,sideMat].forEach(function(mm){ mm.needsUpdate=true; });
      }
      Promise.all([
        load(p.top_texture,(pdx0||1,pdz0||1)),
        load(p.front_texture,(pnum(p.repeat_x,1)||1,1))
      ]).then(function(texs){
        if(!state.scene) return;
        if(texs[0]) topMat.map=texs[0];
        if(texs[1]) frontMat.map=texs[1];
        topMat.needsUpdate=true; frontMat.needsUpdate=true;
        const top=new THREE.Mesh(new THREE.PlaneGeometry(psize[0],psize[1]),topMat);
        top.rotation.x=-Math.PI/2+pitch;
        /* 前倾后，让**前缘中点**保持在 (px0, py0, pz0) 不动：
           台面中心 = 前缘 + 半深度 × 切向；切向 = R_x(pitch)·(0,1,0) = (0, cos p, sin p)
           ⇒ 中心 y = py0 + cos(p)·hd，z = pz0 + sin(p)·hd（**这个符号对应 rotation.x=-π/2+pitch**）。 */
        const hd=psize[1]/2;
        top.position.set(px0, py0+Math.cos(pitch)*hd, pz0+Math.sin(pitch)*hd);
        top.receiveShadow=true; top.castShadow=true; top.name='__platformTop';
        const front=new THREE.Mesh(new THREE.PlaneGeometry(psize[0],pth),frontMat);
        front.position.set(px0,py0-pth/2,pz0);
        front.receiveShadow=true; front.castShadow=true; front.name='__platformFront';
        const sideL=new THREE.Mesh(new THREE.PlaneGeometry(psize[1],pth),sideMat);
        sideL.rotation.y=-Math.PI/2;
        sideL.position.set(px0-psize[0]/2,py0-pth/2,pz0-hd);
        const sideR=sideL.clone(); sideR.position.x=px0+psize[0]/2;
        [sideL,sideR].forEach(function(s){s.receiveShadow=true;s.castShadow=true;});
        sideL.name='__platformSideL'; sideR.name='__platformSideR';
        /* shadow_strength<1 时把平台网格放到**层 1**（默认层 0 的 key 灯不再照它），
           只由 __platformSoftKey 照明 ⇒ 影子强度 = s。层只影响灯光，不影响相机可见性。 */
        if(sshadow<0.999){
          [top,front,sideL,sideR].forEach(function(o){ o.layers.set(1); });
        }
        grp.add(top,front,sideL,sideR);
        if(state.scene){state.scene.add(grp);state.platformGroup=grp;}
      })['catch'](function(){});
    }
    // 程序化摄影棚环境(IBL)：金属材质(metallic=1)在无环境贴图时会渲染成近黑，
    // 用 PMREM 从简易自发光面片生成环境贴图（纯 core three，无外部依赖）。
    try{
      const pmrem=new THREE.PMREMGenerator(state.renderer);
      pmrem.compileEquirectangularShader();
      const envScene=new THREE.Scene();
      const mkplane=(color,intensity,w,h,pos,rot)=>{const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(color).multiplyScalar(intensity),side:THREE.DoubleSide}));m.position.set(...pos);if(rot)m.rotation.set(...rot);envScene.add(m);};
      mkplane(config.sky_color||0xdbeafe,1.2,12,12,[0,6,0],[-Math.PI/2,0,0]);
      mkplane(0xffffff,1.5,8,8,[-7,2,4],[0,Math.PI/2,0]);
      mkplane(0x8bbcff,0.9,8,8,[7,1,-3],[0,-Math.PI/2,0]);
      mkplane(config.ground_color||0x172033,0.18,14,14,[0,-6,0],[Math.PI/2,0,0]);
      state.scene.environment=pmrem.fromScene(envScene,Number(config.env_blur)||0.04).texture;
    // 源环境：若提供游戏内皮肤背景图（config.background_image），则用它做背景 + 由它生成环境（PMREM），
    // 替代程序化摄影棚 rig —— 枪身金属与晶体的反射来源正是这张图所代表的场景。
    const bgImage=config.background_image||(config.background&&/\.(png|jpe?g|webp)$/i.test(String(config.background))?config.background:null);
    if(bgImage){
      const url=new URL(bgImage,state.manifestUrl||location.href).href;
      new state.THREE.TextureLoader().load(url,tex=>{
        // ★ 背景=固定背板：必须用默认 UVMapping（屏幕空间铺满，不随相机旋转）。
        //   若设成 EquirectangularReflectionMapping，three 会按天空盒渲染 → 转武器时背景跟着转（已修）。
        tex.colorSpace=state.THREE.SRGBColorSpace;
        tex.wrapS=tex.wrapT=state.THREE.ClampToEdgeWrapping;
        if(state.scene){state.scene.background=tex;}
        // ★ 环境与背景分离：源证据里材质引用的 t_custom_ibl 是明亮摄影棚 cube（qiangpi/car_studio01），
        //   与场景背景图不是同一件事。因此默认只把这张图当背景；
        //   仅当 env_from_background=true 才由它生成环境（会显著压暗，仅用于对照实验）。
        if(config.env_from_background===true){
          const bgScene=new state.THREE.Scene();
          const sph=new state.THREE.Mesh(new state.THREE.SphereGeometry(50,48,24),
            new state.THREE.MeshBasicMaterial({map:tex,side:state.THREE.BackSide}));
          bgScene.add(sph);
          // ★ P0-4：截图 ≠ 等距环境图 ≠ cubemap —— 只作 background，禁止生成 scene.environment
          if(state.scene){state.scene.background=tex;}
          // scene.environment 保持上面已建好的中性 PMREM（源 cube 找到后再替换）
          }
        state.bgImageApplied=url.split('/').pop();
      });
    }
      state.scene.environmentIntensity=numCfg(config.env_intensity,1.0);   /* ★ task-29：默认显式化，0 合法 */
      pmrem.dispose();
    }catch(_){}
    // 用 TrackballControls（球面自由旋转）而不是 OrbitControls：
    // Orbit 锁定"上方向"，转到极点会锁死（竖拖到顶就停住）；Trackball 无上方向约束，
    // 横竖都能 360° 无限继续转（用户要求）。禁止平移，只保留旋转+缩放。
    state.controls=new state.TrackballControls(state.camera,state.renderer.domElement);
    state.rotMode=state.rotMode||"worldY";
    state.controls.noPan=true;
    state.controls.noRotate=((state.rotMode||'worldY')!=='native');   // ★ 默认 worldY → 旋转由 applyOrbit 接管，上下锁死    // ★ 旋转由 applyOrbit 接管（Trackball 自由球旋转会让画面歪/绕圈）
    state.controls.noZoom=!state.allowZoom;      // ★ 开关默认关闭=不允许缩放
    state.controls.noPan=true;
    state.controls.staticMoving=true;            // ★ 关掉阻尼余速：否则松手后惯性继续转，锁会被拉扯出上下晃
    state.controls.dynamicDampingFactor=0.0;
    state.controls.rotateSpeed=Number(state.config&&state.config.rotate_speed)||3.0;
    state.controls.rotateSpeed=2.4;
    state.controls.zoomSpeed=1.1;
    state.controls.staticMoving=false;
    state.controls.dynamicDampingFactor=0.12;
    state.renderer.domElement.addEventListener("dblclick",()=>applyCamera(selectedCamera(),true));
    state.controls.addEventListener("change",function(){renderOnce();scheduleParams();});   /* ★ 修复（2026-09-17）：原仅 renderOnce —— 转动/缩放时画面重绘但**右下角参数面板从不刷新**，一直显示旧值。updateParams() 早已定义却从未接到事件上。现按 rAF 节流刷新。 */
    state.clock=new THREE.Clock();
    state.resizeObserver=new ResizeObserver(resize);
    state.resizeObserver.observe(state.stage);
    resize();startLoop();
  }

  function resize(){
    if(!state.renderer||!state.camera||!state.stage)return;
    const width=Math.max(1,state.stage.clientWidth),height=Math.max(1,state.stage.clientHeight);
    state.renderer.setSize(width,height,false);state.camera.aspect=width/height;state.camera.updateProjectionMatrix();
    if(state.controls&&state.controls.handleResize)state.controls.handleResize();
    renderOnce();
  }

  function startLoop(){
    bindOrbitPointer(state.renderer&&state.renderer.domElement);
    cancelAnimationFrame(state.frame);
    const tick=()=>{
      if(!state.renderer)return;
      state.frame=requestAnimationFrame(tick);
      if(state.mixer&&state.clock)state.mixer.update(Math.min(state.clock.getDelta(),.05));
      pinPitch();   // 上下旋转锁（默认锁定）：update 前钉一次，避免控制器的内部状态累积俯仰
      if(state.controls)state.controls.update();
      pinPitch();   // update 后再钉一次，保证渲染出的就是锁定角度（只锁俯仰，左右不受影响）
      /* ★ Lead 20260920：key_shadow 开启时，给**当前模型**的 mesh 标 castShadow（按 root 记一次，
         模型被重建时会重新标记）。仅作用于 state.root（武器本体），不碰特效层精灵。 */
      if((state.keyShadow||state.platformOn)&&state.root&&state.__keyShadowMarkedFor!==state.root){
        state.__keyShadowMarkedFor=state.root;
        state.root.traverse(function(o){ if(o.isMesh)o.castShadow=true; });
      }
      renderFrame();
      updateParams();
    };
    tick();
  }

  // 全局后处理（bloom）：源管线有 HDR 辉光，参考图亮部显著高于当前渲染 → 属全局 rig，非逐皮肤上色。
  // 参数来自 viewer.json material_layers.global_rig.bloom；strength=0 → 不建 composer（行为与之前完全一致）。
  // ── 源颜色混合调试（pbr_crystal，prim5）：C = lerp(lerp(T,T*uc,m), lerp(ub,T*uc,d), m)
  //   T = t_basecolor 采样, m = saturate(Tex0.r), d = m * DetailMap.a
  //   说明：DetailMap(crystal_bump_n_uvva) 资源未定位 → d 不可用，显式报错，不用常数权重冒充 ✗
  const CRYSTAL_C_SRC = {
    basecolor: 'assets/3d/weapon_skin/1110171/src_tex/t_basecolor_010.png',
    tex0:      'assets/3d/weapon_skin/1110171/src_tex/tex0_010.png',
    detail:    null,                       // ← 唯一资源阻碍：common\textures\crystal_bump_n_uvva.tga 未定位
    detailOffset: null,                    // ★ block3 无 u_detail_offset_x/y 覆写 → 引擎默认未决（不补值 ✗）
    detailTiling: [4.0, 4.0]               // block3 的 u_detail_tilling=4（源值）
  };
  async function crystalCDebug(on){
    const T=state.THREE;
    if(!T||!state.root) return {error:'no root'};
    const rep = state.__crystalC||{};
    if(on===false){ if(rep.restore) {rep.restore(); state.__crystalC=null;} if(state.root)applyMaterialLayers(state.root); renderOnce(); return {mode:'off'}; }
    if(!rep.loaded){
      const L=u=>new Promise((res,rej)=>{new T.TextureLoader().load(u,x=>{x.colorSpace=T.SRGBColorSpace;x.wrapS=x.wrapT=T.RepeatWrapping;res(x);},undefined,()=>rej(new Error('纹理加载失败: '+u)));});
      const out={};
      try{ out.basecolor=await L(CRYSTAL_C_SRC.basecolor); }catch(e){ out.basecolor=null; }
      try{ out.tex0=await L(CRYSTAL_C_SRC.tex0); }catch(e){ out.tex0=null; }
      out.detail=null; out.missing=[];
      if(!out.basecolor) out.missing.push('t_basecolor');
      if(!out.tex0) out.missing.push('Tex0');
      if(!CRYSTAL_C_SRC.detail) out.missing.push('DetailMap(crystal_bump_n_uvva) 资源未定位 → d 不可用');
      rep.loaded=out; state.__crystalC=rep;
    }
    const S=rep.loaded, ml=(selectedState()||{}).material_layers||{};
    const crystalList=[5];   // ★ 调试只作用 prim5（用户的 prim5 参数/纹理不得套到其他晶体）
    const ub=(ml.per_submesh&&ml.per_submesh['5']&&ml.per_submesh['5'].u_base_color)||[0.1216,0.3961,0.5059];
    const uc=(ml.per_submesh&&ml.per_submesh['5']&&ml.per_submesh['5'].u_crystal_color)||[0,0,1];
    const saved=[];
    let idx=-1;
    state.root.traverse(function(o){
      if(!o.isMesh)return; idx++;
      if(!crystalList.includes(idx))return;
      saved.push([o,o.material]);
      const m=new T.MeshBasicMaterial({map:S.basecolor,toneMapped:true,side:o.material&&o.material.side!==undefined?o.material.side:0});
      m.userData.__crystalC=true;
      m.onBeforeCompile=function(sh){
          sh.uniforms.uTex0={value:S.tex0};
          sh.uniforms.uUB={value:new T.Vector3(ub[0],ub[1],ub[2])};
          sh.uniforms.uUC={value:new T.Vector3(uc[0],uc[1],uc[2])};
          sh.uniforms.uDetailMap={value:S.detail||null};
          sh.uniforms.uHasDetail={value:S.detail?1:0};
          sh.uniforms.uMissing={value:(S.detail||state.__crystalCAssumeA1)?0:1};
          sh.uniforms.uAssumeA1={value:state.__crystalCAssumeA1?1:0};
          sh.uniforms.fDetailOffset={value:(CRYSTAL_C_SRC.detailOffset?new T.Vector2(CRYSTAL_C_SRC.detailOffset[0],CRYSTAL_C_SRC.detailOffset[1]):new T.Vector2(0,0))};
          sh.uniforms.fDetailTiling={value:new T.Vector2((CRYSTAL_C_SRC.detailTiling&&CRYSTAL_C_SRC.detailTiling[0])||1.0,(CRYSTAL_C_SRC.detailTiling&&CRYSTAL_C_SRC.detailTiling[1])||1.0)};
        sh.uniforms.uUC={value:new T.Vector3(uc[0],uc[1],uc[2])}; sh.uniforms.uHasDetail={value:S.detail?1:0};
        sh.fragmentShader=sh.fragmentShader
          .replace('#include <common>','#include <common>\nuniform sampler2D uTex0;uniform sampler2D uDetailMap;uniform vec3 uUB;uniform vec3 uUC;uniform float uHasDetail;uniform float uMissing;uniform float uAssumeA1;uniform vec2 fDetailOffset;uniform vec2 fDetailTiling;')
          .replace('#include <map_fragment>', [
            'vec3 T_=texture2D(map,vMapUv).rgb;',
            'float m_=clamp(texture2D(uTex0,vMapUv).r,0.0,1.0);',
            'float d_=0.0;',
            'if(uAssumeA1>0.5){',
            '  d_=clamp(m_,0.0,1.0);              // 诊断：假设 DetailMap.a=1 ⇒ d=m（真参与计算）',
            '}else if(uHasDetail>0.5){',
            '  vec2 duv=(vMapUv+fDetailOffset)*fDetailTiling;',
            '  vec4 D=texture2D(uDetailMap,duv);',
            '  d_=clamp(m_*D.a,0.0,1.0);',
            '}',
            '// DetailMap 缺失时 d 不可用 → 由 uMissing 控制显示为"输入缺失"标记色（不冒充源结果）',
            'if(uMissing>0.5){ gl_FragColor=vec4(1.0,0.0,1.0,1.0); return; }',
            'vec3 A_=mix(T_,T_*uUC,m_);',
            'vec3 B_=mix(uUB,T_*uUC,d_);',
            'vec3 C_=mix(A_,B_,m_);',
            'diffuseColor.rgb*=C_;'].join('\n'));
        m.userData.__shader=sh;
      };
      o.material=m; o.visible=true;
    });
    rep.restore=function(){ saved.forEach(function(pr){pr[0].material=pr[1];}); };
    rep.savedRefs=saved.map(function(pr){return pr[0];});
    rep.inspect=function(){ // 取实际编译用的片段着色器源码与 uniform 值
      const o=rep.savedRefs[0]; const sh=o&&o.material&&o.material.userData&&o.material.userData.__shader;
      if(!sh) return null;
      const frag=sh.fragmentShader||'';
      const hit=frag.split('\n').filter(function(l){return /uAssumeA1|uHasDetail|uMissing|d_=|C_=|diffuseColor\.rgb\*=/.test(l);});
      const u=sh.uniforms||{};
      return {fragLines:hit, uniformValues:{uAssumeA1:u.uAssumeA1&&u.uAssumeA1.value, uMissing:u.uMissing&&u.uMissing.value,
              uHasDetail:u.uHasDetail&&u.uHasDetail.value, uDetailMap:!!(u.uDetailMap&&u.uDetailMap.value),
              fDetailOffset:u.fDetailOffset&&u.fDetailOffset.value, fDetailTiling:u.fDetailTiling&&u.fDetailTiling.value,
              uUB:u.uUB&&u.uUB.value, uUC:u.uUC&&u.uUC.value},
              programKey:(o.material&&o.material.customProgramCacheKey)?o.material.customProgramCacheKey():null,
              hasMap:!!(o.material&&o.material.map)};
    };
    renderOnce();
    return {mode:(state.__crystalCAssumeA1?'C_assumeDetailA1':'C'), missing:S.missing,
            detailMapUsed:!!S.detail, assumeA1:!!state.__crystalCAssumeA1, u_base_color:ub, u_crystal_color:uc,
            detailOffset:CRYSTAL_C_SRC.detailOffset, detailTiling:CRYSTAL_C_SRC.detailTiling,
            meshes:(function(){let a=[],i=-1;state.root.traverse(function(o){if(o.isMesh){i++;if(crystalList.includes(i))a.push({i:i,mat:o.material.type,hasMap:!!o.material.map});}});return a;})()};
  }

  async function ensureComposer(){
    try{
      const rig=((selectedState()||{}).material_layers||(state.config||{}).material_layers||{}).global_rig||{};
      const bl=rig.bloom||{};
      if(state.noPost)return;   // 诊断期固定关闭后处理（用户 §三/§四：A/B 两组都关 bloom）
      const strength=Number(bl.strength); if(!Number.isFinite(strength)||strength<=0)return;
      if(state.composer)return;
      const b=new URL("./vendor/three/addons/",assetBase).href;
      const [EC,RP,UBP,OP]=await Promise.all([
        import(b+"postprocessing/EffectComposer.js"),import(b+"postprocessing/RenderPass.js"),
        import(b+"postprocessing/UnrealBloomPass.js"),import(b+"postprocessing/OutputPass.js")]);
      const T=state.THREE,sz=new T.Vector2();state.renderer.getSize(sz);
      const c=new EC.EffectComposer(state.renderer);
      c.addPass(new RP.RenderPass(state.scene,state.camera));
      const bp=new UBP.UnrealBloomPass(new T.Vector2(sz.x,sz.y),
        strength,Number.isFinite(Number(bl.radius))?Number(bl.radius):0.5,
        Number.isFinite(Number(bl.threshold))?Number(bl.threshold):0.85);
      c.addPass(bp); c.addPass(new OP.OutputPass());
      state.composer=c;state.bloomPass=bp;
      if(state.status)state.status.textContent="全局后处理：bloom 已启用";
    }catch(e){}
  }
  function renderFrame(){
    /* ★ 修复（2026-09-18，对抗复核 ①）：**整个函数体**（含 pinPitch / scheduleParams / 前置 guard）
       都在 try 内 —— 渲染或前置逻辑抛错时绝不静默变黑屏：
       写 state.__renderErr / window.__renderErr 并照常返回，下一帧继续。
       补充说明（实测）：tick 在调用 renderFrame **之前**就已 re-arm requestAnimationFrame(L274)，
       故 rAF 本身不会因抛错而断；真正的风险是 (a) updateParams 被跳过、(b) 异常穿出到
       renderOnce()/promise 链（调用方无 .catch）。本改动同时覆盖这两条。 */
    try{
      /* ★ 新增（2026-09-18，shader-auditor，task-40）：IBL 就绪门的**推迟重绑**（每帧最多触发一次）。
         cube 六面未就绪时不绑（避免空 cube 全黑）；六面到齐后由加载回调置 __iblRebindPending，
         在这里重建一次材质把 cube 挂上。守卫：仅在源链已建好（state.neoxReport 存在）、无重绑在飞、
         且重建次数 ≤3 时才执行，避免循环/抖动；失败只记录，不抛。 */
      /* ★★ (B)+(C) 收敛式重做（2026-09-19，shader-auditor，task-49；备份 wsv_bak_task49e_20260918_234852.js = 641DDC2CBA6FFEC4）。
         旧实现的两个缺陷：① `__iblRebindPending=false` 是**一次性**的 —— 若那一次重建早于某些 prim 材质建立、
         或被守卫跳过，就**永久不再重试**（实测导致 prim0/prim4 永久 `missing_source_ibl`，我已回退）；
         ② 重建完成后**不检查结果**，无从判断收敛。
         现改为**收敛式**：每次重建 resolve 后**实测**场景里还有多少 prim 没拿到 IBL（envMap/uCustomIbl 二者皆无为缺），
         仍有缺且计数 < 上限 ⇒ **继续保持 pending 重试**；达到上限仍缺 ⇒ 置**明确可判**的
         `state.__iblRetryExhausted=true`（不再静默，见 __texReady()/__acceptanceReport() 暴露的 retry_* 字段）。
         **上限 `IBL_RETRY_CAP=6`**（写入报告）；计数 `__iblRetryCount` 每次尝试递增。 */
      if(state.__iblRebindPending && state.root && state.neoxReport && !state.__iblRebuilding){
        state.__iblRebindPending=false;
        state.__iblRetryCount=(state.__iblRetryCount||0)+1;
        state.__iblRebindTries=state.__iblRetryCount;
        var IBL_RETRY_CAP=6;
        if(state.__iblRetryCount<=IBL_RETRY_CAP){
          state.__iblRebuilding=true;
          var missingIbl=function(){
            try{
              var n=0;
              state.scene.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0];
                if(!m||!m.userData||!m.userData.chain) return;
                var u=(m.userData.__sh&&m.userData.__sh.uniforms)||{};
                var has=!!m.envMap||!!(u.uCustomIbl&&u.uCustomIbl.value);
                if(!has) n++; });
              return n;
            }catch(e){ return 0; }
          };
          try{
            applyNeoxManifest(state.root).then(function(r){
              state.neoxReport=r; state.__iblRebuilding=false;
              try{ if(state.__glowSet&&state.__glowOn!==false) state.__glowSet(true); }catch(e){}
              var left=missingIbl();
              state.__iblRetryLastMissing=left;
              /* ★ 新增（2026-09-19，task-49 裁决 (ii) 附加 1/2）：**收敛即恢复窗口期隐藏的 prim**
                 （`__pendingHidden` 标记）；**达上限（exhausted）也必须恢复可见** ⇒ 绝不永久消失。 */
              if(left===0 || state.__iblRetryExhausted || state.__iblRetryCount>=IBL_RETRY_CAP){
                try{ state.scene.traverse(function(o){ if(o.isMesh&&o.userData&&o.userData.__pendingHidden){
                  o.visible=true; o.userData.__pendingHidden=false; } }); }catch(e){}
              }
              if(left>0 && state.__iblRetryCount<IBL_RETRY_CAP){ state.__iblRebindPending=true; }   /* 未收敛 ⇒ 继续重试 */
              else if(left>0){ state.__iblRetryExhausted=true; }                                    /* 达上限仍缺 ⇒ 明确可判 */
              else { state.__iblRetryExhausted=false; }
              try{_forceRender();}catch(e){}
            })['catch'](function(e){ state.__iblRebuilding=false;
              state.__iblRebindErr=String((e&&e.message)||e);
              if(state.__iblRetryCount<IBL_RETRY_CAP) state.__iblRebindPending=true; else state.__iblRetryExhausted=true; });
          }catch(e){ state.__iblRebuilding=false; state.__iblRebindErr=String((e&&e.message)||e);
            if(state.__iblRetryCount<IBL_RETRY_CAP) state.__iblRebindPending=true; else state.__iblRetryExhausted=true; }
        } else { state.__iblRetryExhausted=true; }
      }
      pinPitch();
      /* ★ 修复（2026-09-17，第 2 版）：参数面板刷新必须挂在**渲染函数本身**上。
         第 1 版挂在 renderOnce 上无效 —— 转动的真实路径是
         `requestAnimationFrame(tick) → renderFrame()`，绕过了 renderOnce。
         此处每次渲染都调用（含 RAF 循环），靠 updateParams 的「值不变则不写 DOM」自去重。 */
      try{ scheduleParams(); }catch(e){}
      if(!(state.renderer&&state.scene&&state.camera))return;
      if(state.composer){try{state.composer.render();return;}catch(e){ /* 不回退销毁 */ }}
      state.renderer.render(state.scene,state.camera);
      state.__renderErr=null;
    }catch(e){
      var _m='[renderFrame] '+String((e&&e.message)||e)+(e&&e.stack?(' @ '+String(e.stack).split('\n')[1]||''):'');
      state.__renderErr=_m; window.__renderErr=_m;
      state.__renderErrCount=(state.__renderErrCount||0)+1;
      if(state.__renderErrCount<=3){ try{ console.error(_m); }catch(_){ } }
    }
  }
  function renderOnce(){renderFrame();}
  function selectedState(){return state.states.find(item=>item.id===state.stateSelect.value)||state.states[0];}
  function selectedCamera(){return state.cameras.find(item=>item.id===state.cameraSelect.value)||state.cameras[0]||null;}

  function applyTransform(root,item){
    if(!root||!item)return;
    if(Array.isArray(item.scale))root.scale.fromArray(item.scale);
    else if(Number.isFinite(Number(item.scale)))root.scale.setScalar(Number(item.scale));
    if(Array.isArray(item.position))root.position.fromArray(item.position);
    if(Array.isArray(item.rotation_degrees))root.rotation.set(...item.rotation_degrees.map(value=>state.THREE.MathUtils.degToRad(Number(value))));
    else if(Array.isArray(item.rotation))root.rotation.set(...item.rotation.map(Number));
  }

  function fitObject(root){
    const THREE=state.THREE;
    const box=new THREE.Box3().setFromObject(root);
    if(box.isEmpty())return;
    const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
    const radius=Math.max(size.length()*.5,.01);
    root.position.sub(center);
    state.controls.target.set(0,0,0);
    state.camera.near=Math.max(radius/1000,.001);state.camera.far=Math.max(radius*100,100);state.camera.updateProjectionMatrix();
    state.camera.position.set(radius*1.55,radius*.85,radius*1.9);
    state.controls.minDistance=radius*.25;state.controls.maxDistance=radius*8;
    state.controls.update();
  }

  function modelFocus(){
    if(!state.root||!state.THREE)return null;
    const box=new state.THREE.Box3().setFromObject(state.root);
    if(box.isEmpty())return null;
    const center=box.getCenter(new state.THREE.Vector3()),size=box.getSize(new state.THREE.Vector3());
    return {center:center,radius:Math.max(size.length()*.5,.01)};
  }

  // 模型在画布中的投影框（NDC → [0,1]，原点左上）
  function projectedSpan(){
    const cam=state.camera,root=state.root,THREE=state.THREE;
    if(!cam||!root||!THREE)return null;
    const box=new THREE.Box3().setFromObject(root);
    if(box.isEmpty())return null;
    const v=new THREE.Vector3(),mn=box.min,mx=box.max;
    let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
    for(let i=0;i<8;i++){
      v.set(i&1?mx.x:mn.x,i&2?mx.y:mn.y,i&4?mx.z:mn.z).project(cam);
      const sx=v.x*.5+.5,sy=1-(v.y*.5+.5);
      x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);
    }
    return {x0:x0,x1:x1,y0:y0,y1:y1,sx:x1-x0,sy:y1-y0};
  }

  // 迭代求"刚好装下"的相机距离：目标=包围盒中心，模型占画布 targetSpan
  function fitDistanceToFocus(focus,dir,targetSpan){
    const cam=state.camera;
    const vfov=cam.fov*Math.PI/180,hfov=2*Math.atan(Math.tan(vfov/2)*Math.max(cam.aspect,1e-3));
    let d=Math.max(focus.radius/Math.sin(vfov/2),focus.radius/Math.sin(hfov/2))*1.02;
    if(!Number.isFinite(d)||d<=0)d=focus.radius*2.5;
    for(let i=0;i<5;i++){
      cam.position.copy(focus.center).addScaledVector(dir,d);
      cam.lookAt(focus.center);cam.updateMatrixWorld(true);
      const p=projectedSpan();
      if(!p)break;
      const s=Math.max(p.sx,p.sy);
      if(!Number.isFinite(s)||s<=1e-6)break;
      const k=s/targetSpan;
      if(Math.abs(1-k)<0.004)break;
      d*=k;
    }
    return d;
  }

  // 单步：把相机距离调到"投影跨度 = targetSpan"
  function fitSpanStep(focus,dir,targetSpan){
    const cam=state.camera;
    const p=projectedSpan();
    if(!p)return;
    const s=Math.max(p.sx,p.sy);
    if(!Number.isFinite(s)||s<=1e-6)return;
    const k=s/targetSpan;
    if(Math.abs(1-k)<0.004)return;
    const d=cam.position.distanceTo(state.controls.target)*k;
    cam.position.copy(state.controls.target).addScaledVector(dir,d);
    cam.lookAt(state.controls.target);cam.updateMatrixWorld(true);
  }

  // 单步：把投影重心从画布中心偏移处拉回中心（透视下投影框并不对称）
  function recenterStep(){
    const cam=state.camera,THREE=state.THREE;
    const p=projectedSpan();
    if(!p||!THREE)return;
    const cx=(p.x0+p.x1)/2,cy=(p.y0+p.y1)/2;
    const dx=0.5-cx,dy=0.5-cy;
    if(Math.abs(dx)<0.002&&Math.abs(dy)<0.002)return;
    const d=cam.position.distanceTo(state.controls.target);
    const vfov=cam.fov*Math.PI/180,hfov=2*Math.atan(Math.tan(vfov/2)*Math.max(cam.aspect,1e-3));
    const right=new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld,0);
    const up=new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld,1);
    const off=new THREE.Vector3()
      .addScaledVector(right,-dx*2*d*Math.tan(hfov/2))
      .addScaledVector(up,dy*2*d*Math.tan(vfov/2));
    state.controls.target.add(off);cam.position.add(off);
    cam.lookAt(state.controls.target);cam.updateMatrixWorld(true);
  }

  // 清控制器残留状态。★ 关键：本查看器用的是 TrackballControls（不是 Orbit），
  //   Trackball 的旋转余量存在 _movePrev/_moveCurr 里；只清 Orbit 的 _sphericalDelta 是无效的。
  function clearControlInertia(){
    clearTrackballState();
  }
  function clearTrackballState(){
    const c=state.controls;
    if(!c)return;
    try{
      // TrackballControls 内部状态：把"上一个/当前"指针位置对齐 → 不再产生旋转增量
      if(c._movePrev&&c._moveCurr){c._movePrev.copy(c._moveCurr);}
      if(c._zoomStart&&c._zoomEnd){c._zoomEnd.copy(c._zoomStart);}
      if(c._panStart&&c._panEnd){c._panEnd.copy(c._panStart);}
      if(typeof c._zoomChanged!=="undefined")c._zoomChanged=false;
      if(typeof c._wheelDelta==="number")c._wheelDelta=0;
      if(typeof c._lastAngle==="number")c._lastAngle=0;
      // Orbit（若将来切换控制器）的字段一并清，避免双份残留
      const sd=c._sphericalDelta;
      if(sd){if("theta" in sd||"phi" in sd){sd.theta=0;sd.phi=0;}else if(sd.set)sd.set(0,0);}
      if(c._panOffset&&c._panOffset.set)c._panOffset.set(0,0,0);
      if(typeof c._scale==="number")c._scale=1;
    }catch(error){}
  }
  // 硬复位：销毁并重建控制器（清除一切内部残留；用于"复位视角/切换形态/应用预设"）
  function rebuildControls(){
    if(!state.camera||!state.renderer)return;
    try{if(state.controls&&state.controls.dispose)state.controls.dispose();}catch(error){}
    const C=state.TrackballControls||(state.THREE&&state.THREE.TrackballControls);
    if(!C)return;
    state.controls=new C(state.camera,state.renderer.domElement);
    state.controls.noPan=true;
    state.controls.noRotate=((state.rotMode||'worldY')!=='native');
    state.controls.noZoom=!state.allowZoom;
    state.controls.rotateSpeed=Number(state.config&&state.config.rotate_speed)||3.0;
    state.controls.zoomSpeed=1.2;
    state.controls.staticMoving=true;      // 无阻尼 → 不会有余速把复位带偏
    state.controls.dynamicDampingFactor=0.2;
  }

  // 相机基换算（源渲染器约定 → three 约定）：不旋转模型，只转换完整相机基
  //   f = normalize(target-eye); u = normalize(up0 - dot(up0,f)*f); u_roll = rotateAroundAxis(u, f, roll)
  // 查看器自动适配距离时保留方向：position = modelCenter - normalize(f)*fittedDistance; up = u_roll; lookAt(modelCenter)
  function cameraBasisFrom(cfg){
    const THREE=state.THREE,cb=cfg&&cfg.camera_basis;
    if(!THREE||!cb||!Array.isArray(cb.eye)||!Array.isArray(cb.target))return null;
    const eye=new THREE.Vector3().fromArray(cb.eye.map(Number));
    const tgt=new THREE.Vector3().fromArray(cb.target.map(Number));
    const up0=new THREE.Vector3().fromArray((cb.up0||[0,0,1]).map(Number));
    const f=new THREE.Vector3().subVectors(tgt,eye);
    if(f.lengthSq()<1e-12)return null;
    f.normalize();
    const u=up0.clone().addScaledVector(f,-up0.dot(f));
    if(u.lengthSq()<1e-12)u.set(0,1,0);else u.normalize();
    const roll=(Number(cb.roll_deg)||0)*Math.PI/180;
    const uRoll=roll?u.clone().applyAxisAngle(f,roll).normalize():u.clone();
    return {dir:eye.clone().sub(tgt).normalize(),up:uRoll,f:f.clone()};
  }

  function applyCamera(preset,announce){
    if(!state.camera||!state.controls)return;
    // ── 按口径：① 先暂停俯仰锁并清除旧基准 ② 清控制器残留 ③ 设相机（方向+target+up/滚转）
    state.__rotating=true;                 // 暂停俯仰/滚转锁（避免它和我们争相机）
    state.pinnedPolar=null;state.pinnedUp=null;
    clearTrackballState();
    if(preset&&Number.isFinite(Number(preset.fit_span)))state.fitSpan=Number(preset.fit_span);
    if(preset&&Number(preset.fov))state.camera.fov=Number(preset.fov);
    state.camera.updateProjectionMatrix();
    const THREE=state.THREE;
    const focus=modelFocus();
    const dir=new THREE.Vector3();
    if(preset&&Array.isArray(preset.position))dir.fromArray(preset.position.map(Number));
    if(dir.lengthSq()<1e-9)dir.set(1,.6,1);
    dir.normalize();
    // 方向与滚转：预设显式 up 优先 → 源相机基 → 皮肤默认 up；三者都没有才保持现值
    const cb=cameraBasisFrom(state.config);
    if(cb&&cb.dir&&!(preset&&preset.no_basis))dir.copy(cb.dir);   // __setCam/对齐预设可旁路 camera_basis
    const upFromPreset=(preset&&Array.isArray(preset.up))?new THREE.Vector3().fromArray(preset.up.map(Number)):null;
    const upBasis=(cb&&cb.up)?cb.up.clone():null;
    const upDefault=(preset&&Array.isArray(preset.up0))?new THREE.Vector3().fromArray(preset.up0.map(Number)):null;
    const upChosen=upFromPreset||upBasis||upDefault;
    if(upChosen&&upChosen.lengthSq()>1e-9)state.camera.up.copy(upChosen.normalize());
    // ★ 精确复现模式：预设同时给了 target 与 distance 时，按"位置=target+方向×距离"原样还原，
    //   不做自动取景（否则用户调好的 xyz/距离会被取景改掉）
    const tgt=(preset&&Array.isArray(preset.target))?new THREE.Vector3().fromArray(preset.target.map(Number)):null;
    const distFix=(preset&&Number.isFinite(Number(preset.distance)))?Number(preset.distance):null;
    if(tgt&&distFix){
      // 方向必须取 preset.position - preset.target（不能用相机当前位置，那时相机还是初始状态）
      const d2=new THREE.Vector3();
      if(preset&&Array.isArray(preset.position))d2.fromArray(preset.position.map(Number)).sub(tgt);
      if(d2.lengthSq()<1e-12)d2.copy(dir);
      d2.normalize();
      // ★ 轨道中心=模型几何中心（加载时就吸附）：否则首次拖动会"跳"一下，且绕注视点转会让模型画圈
      const fc=(typeof modelFocus==='function')?modelFocus():null;
      const ctr2=(fc&&fc.center)?fc.center.clone():tgt;
      state.controls.target.copy(ctr2);
      state.camera.position.copy(ctr2).addScaledVector(d2,distFix);
      state.camera.lookAt(ctr2);
      state.camera.near=Math.max(distFix/500,.001);state.camera.far=Math.max(distFix*40,focus?focus.radius*100:1000);
      state.controls.minDistance=Math.max((focus?focus.radius*.2:.01),.01);
      state.controls.maxDistance=Math.max(distFix*6,(focus?focus.radius*12:10));
      state.camera.updateProjectionMatrix();
      clearTrackballState();state.controls.update();clearTrackballState();state.controls.update();
      const nb0=new THREE.Vector3().subVectors(state.camera.position,state.controls.target).normalize();
      state.pinnedUp0=state.camera.up.clone();
      state.baseAz=Math.atan2(nb0.x,nb0.z);
      state.pinnedPolar=Math.acos(Math.max(-1,Math.min(1,nb0.clone().normalize().y)));
      state.__rotating=false;renderOnce();
      if(announce&&state.status)state.status.textContent=preset?`视角：${preset.label||""}`:"视角已复位";
      return;
    }
    if(focus){
      state.controls.target.copy(focus.center);
      state.camera.aspect=(state.camera.aspect>0?state.camera.aspect:1.78);
      const dist=(preset&&Number(preset.distance))||fitDistanceToFocus(focus,dir,state.fitSpan);
      state.camera.position.copy(focus.center).addScaledVector(dir,dist);
      // ★ 取景只允许"沿既定方向改距离 + 平移居中"：方向与滚转在整个收敛过程中保持不变
      const dirKeep=dir.clone(), upKeep=state.camera.up.clone();
      for(let i=0;i<3;i++){fitSpanStep(focus,dirKeep,state.fitSpan);recenterStep();}
      fitSpanStep(focus,dirKeep,state.fitSpan);
      // 收敛后再断言一次：方向/滚转未被取景改动（若被改动则按既定值恢复）
      const dNow=new THREE.Vector3().subVectors(state.camera.position,state.controls.target).normalize();
      if(dNow.dot(dirKeep)<0.9999){state.camera.position.copy(state.controls.target).addScaledVector(dirKeep,state.camera.position.distanceTo(state.controls.target));}
      state.camera.up.copy(upKeep);
      state.controls.minDistance=Math.max(focus.radius*.3,.01);state.controls.maxDistance=Math.max(dist*4,focus.radius*8);
      state.camera.near=Math.max(dist/500,.001);state.camera.far=Math.max(dist*20,focus.radius*100);
    }else{
      if(preset&&Array.isArray(preset.position))state.camera.position.fromArray(preset.position.map(Number));
      if(preset&&Array.isArray(preset.target))state.controls.target.fromArray(preset.target.map(Number));
    }
    state.camera.lookAt(state.controls.target);
    state.camera.updateProjectionMatrix();
    clearTrackballState();
    state.controls.update();               // 让控制器与相机一致
    clearTrackballState();                 // 稳定后再清一次残留
    state.controls.update();
    // ── 相机已稳定：记录新基准（俯仰角按世界 +Y 定义，滚转记录 up），再解除暂停
    const nb=new THREE.Vector3().subVectors(state.camera.position,state.controls.target);
    if(nb.lengthSq()>1e-12){
      state.pinnedUp0=state.camera.up.clone();
      state.baseAz=Math.atan2(nb.x,nb.z);
      state.pinnedPolar=Math.acos(Math.max(-1,Math.min(1,nb.clone().normalize().y)));
    }
    state.__rotating=false;
    renderOnce();
    if(announce&&state.status)state.status.textContent=preset?`视角：${preset.label||""}`:"视角已复位";
  }

  function disposeMaterial(material){
    if(!material)return;
    for(const value of Object.values(material)){if(value&&value.isTexture)value.dispose();}
    if(material.dispose)material.dispose();
  }

  function disposeObject(root){
    if(!root)return;
    root.traverse(obj=>{if(obj.geometry&&obj.geometry.dispose)obj.geometry.dispose();if(Array.isArray(obj.material))obj.material.forEach(disposeMaterial);else disposeMaterial(obj.material);});
    if(root.parent)root.parent.remove(root);
  }

  function disposeEffects(){
    if(state.effectsHandle&&typeof state.effectsHandle.dispose==="function")state.effectsHandle.dispose();
    state.effectsHandle=null;
    if(state.sfxButton){state.sfxButton.setAttribute("aria-pressed","false");state.sfxButton.textContent="SFX 关闭";}
  }

  function disposeScene(){
    cancelAnimationFrame(state.frame);state.frame=0;disposeEffects();
    if(state.resizeObserver)state.resizeObserver.disconnect();state.resizeObserver=null;
    if(state.mixer){state.mixer.stopAllAction();state.mixer=null;}
    if(state.root)disposeObject(state.root);state.root=null;
    if(state.controls)state.controls.dispose();state.controls=null;
    if(state.renderer){state.renderer.dispose();if(state.renderer.forceContextLoss)state.renderer.forceContextLoss();state.renderer.domElement.remove();}
    state.renderer=null;state.scene=null;state.camera=null;state.clock=null;
  }

  async function attachEffects(){
    const effects=state.config&&state.config.effects;
    if(!effects||effects.status==="none")return;
    if(!state.effectsAdapter||typeof state.effectsAdapter.attach!=="function")return;
    disposeEffects();
    /* ★ FIX-SFXFOLLOW 2026-09-20（缺陷 A）：除 `root`（attach 时的**快照**）外，再传 `getRoot` 活引用取数器。
       根因：`loadSelectedState()`（本文件 `state.root=gltf.scene` 那行）与切状态都会**重建** root 对象，
       快照永远指向被丢弃的旧对象 ⇒ 适配器 `syncToRoot()` 每帧抄旧矩阵、特效层冻在原地。
       `getRoot` 每帧返回**当前** state.root；不传该字段的旧适配器/调用方行为不变（向后兼容）。 */
    state.effectsHandle=await state.effectsAdapter.attach({scene:state.scene,root:state.root,getRoot:function(){return state.root;},camera:state.camera,renderer:state.renderer,effects,manifestUrl:state.manifestUrl,THREE:state.THREE});
  }

  async function toggleEffects(){
    if(!state.effectsHandle){await attachEffects();if(!state.effectsHandle)return;}
    const on=state.sfxButton.getAttribute("aria-pressed")!=="true";
    state.sfxButton.setAttribute("aria-pressed",String(on));state.sfxButton.textContent=on?"SFX 开启":"SFX 关闭";
    if(typeof state.effectsHandle.setEnabled==="function")state.effectsHandle.setEnabled(on);
  }

  function updateEffectsButton(){
    const effects=state.config&&state.config.effects;
    const available=effects&&effects.status!=="none"&&state.effectsAdapter&&typeof state.effectsAdapter.attach==="function";
    state.sfxButton.disabled=!available;state.sfxButton.setAttribute("aria-pressed","false");
    state.sfxButton.textContent=available?"SFX 关闭":effects&&effects.status!=="none"?"SFX 运行时待接入":"SFX 未提供";
    state.sfxButton.title=available?"切换实时特效":effects&&effects.status!=="none"?"效果清单已存在，但网页效果适配器尚未安装":"该模型没有 SFX 清单";
  }

  // 材质层：按 viewer.json 的 material_layers 把指定子网格换成带透射的晶体材质。
  // 依据=源 c159 的材质表（pbr_crystal 组），参数全部来自配置，不在代码里写死颜色/数值。
  // ─────────────────────────────────────────────────────────────
  // A/B/C 诊断（只做对照；不改源值、不交换贴图、不补色、不做后处理补光）
  //   A = 当前正式材质结果（默认，不做任何改动）
  //   B = 原绑定贴图 Unlit：原 UV/贴图/子网格绑定；基色乘数=白；不应用未证乘色、自发光、
  //       反射、透射、bloom、色调映射；正确按 sRGB 显示（不把 sRGB 当线性）
  //   C = 保守基线：保留确认的原贴图绑定及已证语义；暂停未证 u_base_color 乘算与
  //       subsurface_color→emissive；不用"基色贴图×统一增益"的人为自发光；主体不透明；
  //       晶体关闭未证 transmission/thickness/ior；使用真正无色的诊断灯光/环境（背景不变）；
  //       bloom 关、envBright 关；粗糙度用统一诊断常数（标 diagnostic，不称源粗糙度）
  // ─────────────────────────────────────────────────────────────
  let __rigBackup=null;
  function setColorlessRig(on){
    try{
      const THREE=state.THREE;if(!THREE||!state.scene)return;
      const cfg=state.config||{};
      if(on){
        if(!__rigBackup){
          __rigBackup={lights:[]};
          state.scene.traverse(function(o){if(o.isLight)__rigBackup.lights.push({o:o,c:o.color.clone(),i:o.intensity});});
          __rigBackup.env=state.scene.environment;__rigBackup.envInt=state.scene.environmentIntensity;
        }
        state.scene.traverse(function(o){if(o.isLight)o.color.setRGB(1,1,1);});
        const pm=new THREE.PMREMGenerator(state.renderer);pm.compileEquirectangularShader();
        const es=new THREE.Scene();
        const mk=function(c,it,w,h,pos,rot){const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),
          new THREE.MeshBasicMaterial({color:new THREE.Color(c).multiplyScalar(it),side:THREE.DoubleSide}));
          m.position.set.apply(m.position,pos);if(rot)m.rotation.set.apply(m.rotation,rot);es.add(m);};
        mk(0xffffff,1.0,12,12,[0,6,0],[-Math.PI/2,0,0]);
        mk(0xffffff,1.0,8,8,[-7,2,4],[0,Math.PI/2,0]);
        mk(0xffffff,1.0,8,8,[7,1,-3],[0,-Math.PI/2,0]);
        mk(0x808080,0.35,14,14,[0,-6,0],[Math.PI/2,0,0]);   // 中性灰地面，非蓝色
        state.scene.environment=pm.fromScene(es,0.03).texture;state.scene.environmentIntensity=1.0;
      }else if(__rigBackup){
        __rigBackup.lights.forEach(function(r){r.o.color.copy(r.c);r.o.intensity=r.i;});
        state.scene.environment=__rigBackup.env;state.scene.environmentIntensity=__rigBackup.envInt;
        __rigBackup=null;
      }
      renderOnce();
    }catch(e){}
  }
  function setDiagABC(mode){
    // mode: 'A' | 'B' | 'C'
    state.diagMode=mode;
    setColorlessRig(mode==='C');
    // B/C 期间关闭后处理与 envBright（诊断不得含 bloom 补光）
    if(mode!=='A'){/* 保留 composer，仅暂停 pass */}
    if(state.root)applyMaterialLayers(state.root);
    renderOnce();
    return {mode:mode,colorlessRig:mode==='C',bloom:(mode==='A')};
  }
  
// ★ P0-2：GLB 只作几何容器。纹理一律按 neox_material.json 的角色加载，
//   不再使用 glTF 里被错误翻译的 baseColorTexture（旧 GLB 把控制图 _b_m 当颜色图）。
/* ★ 新增（2026-09-18，shader-auditor，task-29）：rig 配置读取的**显式化**（默认值 = 当前行为）。
   · numCfg(v,d)：`0` 是**合法值**（不得被 `||` 吃掉）；仅当缺键/NaN/非有限时才用默认 d。
   · toneMapOf(T,cfg)：把 `viewer.json.tone_mapping` 映射到 three 常量，接受
     'ACESFilmic' / 'NoToneMapping'（大小写、下划线、连字符、空格均不敏感）；
     **缺键或无法识别 ⇒ ACESFilmic（= 本文件此前两处写死的值）**。 */
function numCfg(v,d){ var n=Number(v); return Number.isFinite(n)?n:d; }
/* ★★★ 修复（2026-09-20，ENVWIRE·Step5）：`tone_mapping` **配置被忽略**的缺陷。

   实测现场（1110025 `viewer.json`，磁盘直读）：
     · `states[0].material_layers.global_rig.tone_mapping` = **"ACESFilmic"**（选中态，项目同组近似值）
     · `material_layers.global_rig.tone_mapping`         = **"NoToneMapping"**（顶层，2026-09-18 拍板的"源中立"值）
     · **顶层 `tone_mapping` 键不存在**
   而 `toneMapOf(cfg)` 此前**只**读 `cfg.tone_mapping` ⇒ 两个 `global_rig.tone_mapping` **全文件无人读**
   ⇒ 永远走 `ACESFilmic` 默认。`__rigProbe().toneMapping_source` 报的
   "代码默认 ACESFilmic（配置无 tone_mapping）"是**如实**的，正是缺陷本身。

   修法（**只改"读哪里"，不引入曲线/系数/预设**）：按**具体度**建一条解析链，逐级回落：
     ① `cfg.tone_mapping`                  （顶层；显式最高优先，保持向后兼容）
     ② 选中态 `states[selected].material_layers.global_rig.tone_mapping`
        —— 与 `applyMaterialLayers()` 读的**同一个 `selectedState()`**（L3451-3452 同源），
           避免"渲染参数读选中态、tone mapping 读顶层"的**双口径**（缺陷的根因形态）
     ③ 顶层 `material_layers.global_rig.tone_mapping`
     ④ 都没有 ⇒ `ACESFilmic`（= 改动前的默认行为，逐字不变）
   本皮肤三级都有值：② = `ACESFilmic` ⇒ 生效值**仍是 ACES**（与改动前一致，见报告两档读数）；
   但 `rigProbe` 的来源标注从此变成 `states[selected]...global_rig.tone_mapping`，**不再谎称"配置无此键"**。
   纪律：**不新增任何 tone mapping 预设**；允许的取值仍只有本函数原本认识的
   `NoToneMapping` / ACES 两条（大小写/下划线/连字符/空格不敏感）。
   标注：`tone_mapping` 在**源侧不存在**（`001348/001360.c159` 的 33 条参数核里曝光/色调映射类
   uniform = 0 个）⇒ 三者都是**展示 rig 的近似值**，本处只做"配置读取接线"，不改其数值。 */
function toneMapRawOf(cfg){
  var norm=function(v){ return (v===undefined||v===null)?null:String(v); };
  var direct=norm(cfg&&cfg.tone_mapping);
  if(direct!==null&&direct.trim()!=='') return {raw:direct,src:'config.tone_mapping'};
  var sel=null;
  try{ if(typeof selectedState==='function') sel=selectedState(); }catch(e){ sel=null; }
  var a=norm(sel&&sel.material_layers&&sel.material_layers.global_rig&&sel.material_layers.global_rig.tone_mapping);
  if(a!==null&&a.trim()!=='')
    return {raw:a,src:'states[selected].material_layers.global_rig.tone_mapping'};
  var b=norm(cfg&&cfg.material_layers&&cfg.material_layers.global_rig&&cfg.material_layers.global_rig.tone_mapping);
  if(b!==null&&b.trim()!=='')
    return {raw:b,src:'material_layers.global_rig.tone_mapping'};
  return {raw:'',src:'absent__code_default_ACESFilmic'};
}
function toneMapOf(T,cfg){
  var r=toneMapRawOf(cfg);
  var s=String(r.raw||'').replace(/[_\s-]/g,'').toLowerCase();
  if(s==='notonemapping'||s==='none'||s==='linear'||s==='no') return T.NoToneMapping;
  return T.ACESFilmicToneMapping;      /* 默认 = 当前行为 */
}
function neoxPng(logical){
  const b=String(logical).split(/[\\/]/).pop().replace(/\.(tga|dds|png)$/i,'');
  const m=b.match(/^skin_1003_(\d{3})(?:001)?(a|b_m|n|m|s_m)$/);
  return m?('src_tex/'+m[1]+'_'+m[2]+'.png'):null;
}
async function applyNeoxManifest(root){
  try{ const q=new URLSearchParams(location.search);
       if(q.get('neoxView')) state.neoxView=q.get('neoxView');
       if(q.get('diagA1')==='1') state.neoxDiagA1=true; }catch(e){}
  const base=state.modelDir;
  if(!base) return {error:'modelDir 未记录'};
  let man=null;
  try{
    const res=await fetch(base+'neox_material.json?t='+Date.now());
    if(!res.ok) throw new Error('HTTP '+res.status);
    man=await res.json();
  }catch(e){ return {error:'manifest 读取失败: '+((e&&e.message)||String(e))+' @ '+base}; }
  const prims=man.primitives||[]; const meshes=[];
  root.traverse(o=>{ if(o.isMesh) meshes.push(o); });
  const TL=new state.THREE.TextureLoader(); const cache={};
  /* ★ 新增（2026-09-19，shader-auditor，task-49；lead 裁决 (i) + 附加 1/2/3）：**会话级 sha256 摘要缓存**。
     · 缓存键 = **绝对 URL（base+file）**；同时存 `bytes`（字节数），命中时**校验长度一致**，不一致 ⇒ miss 重算
       （防"同 URL 不同内容"）。
     · **校验本身从不跳过**（无"跳过校验"分支）：miss 时照旧 `fetch` + `crypto.subtle.digest('SHA-256')`。
     · 生命周期 = **单次页面会话**（`state.__shaDigestCache` 随页面销毁）⇒ **换文件必须重载页面**
       （与"写入者串行 + pin 冻结"纪律一致）；**不做跨会话持久缓存**。
     · 计数进 `__perfStages()`：验收要求 **首轮全 miss / 次轮全 hit**（`sha_hits`/`sha_misses`）。 */
  if(!state.__shaDigestCache) state.__shaDigestCache={};
  if(!state.__perf) state.__perf={sha_hits:0,sha_misses:0,head_checks:0,sha_ms:0,rebuilds:0};
  const shaCache=state.__shaDigestCache, PERF=state.__perf;
  PERF.rebuilds++;
  async function sha256(file){
    try{
      const url=base+file;
      const hit=shaCache[url];
      if(hit&&typeof hit.bytes==='number'){
        /* 命中路径：只做一次 HEAD 校验长度（不读全文、不重算摘要）；失败/长度不符 ⇒ 落到 miss 重算 */
        try{
          PERF.head_checks++;
          const hr=await fetch(url,{method:'HEAD'});
          if(hr&&hr.ok){ const len=Number(hr.headers.get('content-length'));
            if(Number.isFinite(len)&&len===hit.bytes){ PERF.sha_hits++; return hit.digest; } }
        }catch(e){}
      }
      PERF.sha_misses++;
      const t0=performance.now();
      const r=await fetch(url); const b=await r.arrayBuffer();
      const h=await crypto.subtle.digest('SHA-256', b);
      PERF.sha_ms+=Math.round(performance.now()-t0);
      const d=Array.from(new Uint8Array(h)).slice(0,16).map(x=>x.toString(16).padStart(2,'0')).join('');
      shaCache[url]={digest:d, bytes:b.byteLength};
      return d;
    }catch(e){ return null; }
  }
  /* ★ 新增（2026-09-19，task-49）：只读阶段探针（**默认不打印、不参与渲染**；只反映 sha 缓存与重建计数）。
     `__perfStages(true)` 仅用于显式清零；`__perfStages()` 返回读数。 */
  window.__perfStages=function(reset){
    try{ if(reset===true){ state.__perf={sha_hits:0,sha_misses:0,head_checks:0,sha_ms:0,rebuilds:0}; return 'reset'; }
      return JSON.stringify({perf:state.__perf, sha_cache_entries:Object.keys(state.__shaDigestCache||{}).length,
        note:'单会话缓存；换文件须重载页面；校验从不跳过（miss 走真 fetch+digest）'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); }
  };
  /* ★ 新增（2026-09-17）：各向异性过滤。
     此前 viewer 从未设置 texture.anisotropy（默认为 1）。掠射角下 mip 选择会沿切线方向抹开，
     表现为「色块莫名延伸 / 材质像没贴上去」——正是用户报告的症状。
     这里取硬件上限；对已设过的不重复覆盖。不改变任何颜色/亮度/贴图内容。 */
  const MAXANISO=(function(){ try{ return state.renderer&&state.renderer.capabilities&&state.renderer.capabilities.getMaxAnisotropy?state.renderer.capabilities.getMaxAnisotropy():1; }catch(e){ return 1; } })();
  const aniso=function(t){ try{ if(t&&t.anisotropy!==undefined&&MAXANISO>1) t.anisotropy=MAXANISO; }catch(e){} return t; };
  const tex=(f,srgb)=>{ if(!f) return null; if(cache[f]) return cache[f];
    const t=TL.load(base+f);
    t.colorSpace=srgb?state.THREE.SRGBColorSpace:state.THREE.NoColorSpace;
    t.wrapS=t.wrapT=state.THREE.RepeatWrapping; t.flipY=false;
    aniso(t);
    cache[f]=t; return t; };
  const rep={applied:0,applied_prims:[],failed:[],missing:[],prims:[],
             base:base,meshes:meshes.length,prims_total:prims.length,
             manifest_sha:null,glb_sha:man.geometry_glb_sha256||null,
             parser_sha:man.parser_sha256||null};
  for(let i=0;i<meshes.length;i++){
    const mesh=meshes[i], pr=prims[i];
    if(!pr) continue;
    const T=pr.textures||{}; const g={};
    for(const k in T){ const lf=(T[k]&&(T[k].local_file||T[k].logical))||null;
      // ★ 修复（2026-09-16）：t_custom_ibl 是 cube（local_file 形如 src_cube/<name>.dds），
      //   而 neoxPng() 只解析 skin_1003_*.tga 材质贴图名，对 cube 路径恒返回 null →
      //   iblPath=null → iblName=null → iblCube=null → envMode 恒为 missing_source_ibl、
      //   envMapIntensity=0。源 IBL 因此永不加载（即外审报告 §六.2「源环境缺失」的真正原因）。
      //   cube 槽位直接消费 manifest 的 local_file；六面按 src_cube/faces/<name>_f{i}_m0.png 装载。
      const mapped=lf?(lf.indexOf('src_tex/')===0?lf:neoxPng(lf)):null;
      g[k]={file:(k==='t_custom_ibl'?lf:mapped), color_space:(T[k]&&T[k].color_space)||'linear',
            logical:(T[k]&&(T[k].logical_path||T[k].logical))||null, sha:(T[k]&&T[k].sha256)||null,
            /* ★ 新增（2026-09-18，对抗复核 ②）：把 manifest 自带的 faces_glob 带下来，
               供 cube 六面 URL 直接使用（比从 cube 名派生更可靠）。 */
            faces_glob:(T[k]&&T[k].faces_glob)||null}; }
    const missRequired=(pr.missing_required||pr.missing||[]).slice();
    /* ══════════════════════════════════════════════════════════════════════════════════════
       ★★★ 新增（2026-09-20，CRYSTAL_WIRE2）：把**源 c159 声明的 common 贴图**接进晶体槽位。

       背景（Lead 第一步诊断 Q3）：4 张已定证贴图落盘在
         `assets/3d/weapon_skin/1110025/src_tex/common/`（带 `PROVENANCE_common_tex.json`，
          名字哈希 + 自解包 + 自哈希 7/7 命中，行号 8488/8452/8706/8556），
       但 **manifest `pr.textures` 里 4 个槽位一个都没有**（prim1/2/4 的 `missing[]` 里写着
         `state: not_shipped__declared_by_material_c159_but_not_extracted_in_this_build_scope`）
       ⇒ 晶体链的 `causticFile/refrFile/detailFile` 恒 null ⇒ **贴图虽在磁盘上，却从未被材质引用**。

       绑定依据 = **同 prim 的 `declared_slot_groups.this_prim`（源 c159 按 Material_0..4 切段的
       声明路径流，逐 prim 直读）**，不是按槽声明序猜（Lead 裁决 C11 已推翻"按声明序推定"）。
       三档标注：
         · NormalMap  ← crystal_bump_n03  = **source_verified**
             （Lead 裁决 C11：内容铁证 B 主导占比 1.0000 ⇒ 判为法线图；prim1/prim4 均声明该名）
         · t_caustic_tex ← caustic3       = **source_verified**
             （Lead 裁决 C11 定证 4 条之一；prim1/prim4 声明该名）
         · t_refraction_tex ← refraction_envmap_1 = **source_verified**
             （Lead 裁决 C11 定证 4 条之一；prim1/prim4 声明该名）
         · DetailMap ← detail_normal_snake_02_m   = **source_verified**
             （Lead 裁决 C11 定证 4 条之一；prim3 声明该名）
         · t_reflection_tex ← gem_fire    = **unresolved（按源名直接贴并标注，不猜）**
             （Lead 裁决 C11：gem_fire 仅为 t_reflection_tex 的**候选**，未定证；
               本处按"声明了该槽就必须有来源"接上，并在 chain 上显式标 unresolved）
         · `crystal_caustic_01`（prim4 声明）= **unresolved**：与 caustic3 同属 caustic 候选，
           因 `caustic3` 已被 C11 定为 t_caustic_tex，本 prim 不再重复占用该槽 ⇒ 记 unresolved 不接。
       纪律：**绝不用别的图顶替、绝不猜未列出的槽**；只在 `g` 上补槽，不改 manifest 文件。
       ══════════════════════════════════════════════════════════════════════════════════════ */
    const COMMON_TEX_DIR='src_tex/common/';
    const _srcDeclared=(pr.declared_slot_groups&&Array.isArray(pr.declared_slot_groups.this_prim))
      ? pr.declared_slot_groups.this_prim.map(function(x){ return String(x||'').toLowerCase().replace(/\\/g,'/'); }) : [];
    const _declares=function(stem){ return _srcDeclared.some(function(p){ return p.indexOf(String(stem).toLowerCase())>=0; }); };
    /* 该 prim 的源声明槽 → 落盘 common 文件（只有同时满足"源声明了"才接） */
    const SRC_COMMON_SLOTS=[
      {slot:'NormalMap',        stem:'crystal_bump_n03',         file:'crystal_bump_n03.png',         level:'source_verified'},
      {slot:'t_caustic_tex',    stem:'caustic3',                 file:'caustic3.png',                 level:'source_verified'},
      {slot:'t_refraction_tex', stem:'refraction_envmap_1',      file:'refraction_envmap_1.png',      level:'source_verified'},
      {slot:'DetailMap',        stem:'detail_normal_snake_02_m', file:'detail_normal_snake_02_m.png', level:'source_verified'},
      /* ★★ 改动（2026-09-20，ENVROUTE S2）：`gem_fire` **不再占用 `t_reflection_tex` 槽位**。
         原实现把它写成 `slot:'t_reflection_tex'`（注释自标 `unresolved(candidate_by_source_name)`），
         但「**候选**槽位名」与「**已定证**槽位」混在同一条绑定通路里 ⇒ 违反本任务红线
         **「3 张 unresolved 按源名直接贴并标注，不许猜槽位名」**。
         现改为 `slot:null` + `slot_candidate:'t_reflection_tex'`：贴图**仍按源名登记**
         （`srcSlotUnresolved` 可读、探针可见、报告可见），但**不写进 `g[]`、不绑 uniform、不参与颜色运算**。 */
      {slot:null, slot_candidate:'t_reflection_tex', stem:'gem_fire', file:'gem_fire.png',
       level:'unresolved(candidate_by_source_name)'}
    ];
    const srcSlotMeta={};
    const srcSlotConflict=[];
    /* ★ 新增（2026-09-20，ENVROUTE S2）：**按源名登记但不占槽位**的 unresolved 贴图（不猜槽位名）。 */
    const srcSlotUnresolved=[];
    SRC_COMMON_SLOTS.forEach(function(S){
      if(!_declares(S.stem)) return;                       /* 源没声明 ⇒ 不接（不猜） */
      if(!S.slot){ srcSlotUnresolved.push({source_stem:S.stem, source_name:COMMON_TEX_DIR+S.file,
                    slot:null, slot_candidate:S.slot_candidate||null, level:S.level,
                    rule:'source_name_registered_only__no_slot_guess'});
                   return; }
      if(g[S.slot]&&g[S.slot].file){
        /* manifest 已给 file ⇒ **尊重 manifest，不覆盖**。
           ★ 改动（2026-09-20，ENVROUTE S2）：只有**指向不同文件**才算真冲突。
             manifest 与源声明指向**同一文件**是「两处一致（互相印证）」，不得记成 `conflict`
             —— 否则 S2 把 4 张定证贴图写进 manifest 之后，每个 prim 都会**假报**冲突。 */
        if(String(g[S.slot].file)===COMMON_TEX_DIR+S.file){
          srcSlotMeta[S.slot]={file:g[S.slot].file, level:S.level, declared_stem:S.stem,
                               origin:'manifest(local_file)+source_declared_agrees'};
          return;
        }
        srcSlotConflict.push({slot:S.slot, kept:g[S.slot].file, source_declared:COMMON_TEX_DIR+S.file,
                              source_level:S.level, rule:'manifest_first__source_declaration_recorded_only'});
        return;
      }
      g[S.slot]={file:COMMON_TEX_DIR+S.file, color_space:'linear', logical:null, sha:null, faces_glob:null};
      srcSlotMeta[S.slot]={file:COMMON_TEX_DIR+S.file, level:S.level, declared_stem:S.stem,
                           origin:'declared_slot_groups.this_prim + PROVENANCE_common_tex.json'};
    });
    /* ══════════════════════════════════════════════════════════════════════════════════════
       ★★★ 新增（2026-09-20，CRYSTAL_WIRE2）：IBL cube 的 **A/B 档开关**（只改指向，不改文件内容）。

       Lead 裁决 C10：本皮肤用哪套 IBL cube = **unresolved**（静态数据无选择器）。
         · 源证据（route 1，直证）：`model_path` 路径解析 → weapon.gpk#1346/1347/1348 → qiangpi
         · 内容旁证（route 2）：jiayuan02a 是冷蓝白室内房间，更像游戏截图背景
       现状：manifest `t_custom_ibl.local_file` 只写一套（qiangpi），没有选择器可言。
       为让 A/B **可复现且不伪造证据**，这里只做一件事：把 `local_file` 的基名与 `faces_glob`
       同步指向 URL 指定的那套 cube（两套六面都已落盘，sha16 已登记）。
       标注：**approximate（诊断用选择器）** —— 默认（无参数）时**逐字不动 manifest**，行为与改动前一致。
       用法：`&cubeAB=qiangpi|jiayuan02a`（也有 `state.__cubeABOverride`）。
       ══════════════════════════════════════════════════════════════════════════════════════ */
    /* ★ 改动（2026-09-21，SNOWCUBE）：选择器放宽到**清册里的自造近似档**。
       原来硬编码只认 'qiangpi'|'jiayuan02a' ⇒ 产品默认（自造名）会被静默丢弃。
       新增一路：清册里 status==='self_authored_approximate' 的名字也接受。
       该状态**只可能**来自 data/media/weapon_skin_cubes_custom.js ⇒
       「partial/unresolved 不使用替代图」的既有纪律不变。
       仅当**显式**传了 cube（URL 参数或 __cubeABOverride）才走这里；
       无覆盖时（默认）**逐字不动 manifest** —— 与改前行为一致。 */
    const cubeAB=(function(){
      var v=null; try{ v=new URLSearchParams(location.search).get('cubeAB'); }catch(e){}
      if(!v&&state.__cubeABOverride) v=String(state.__cubeABOverride);
      v=v?String(v).trim().toLowerCase():null;
      if(!v) return null;
      if(v==='qiangpi'||v==='jiayuan02a') return v;      /* 既有两套（走皮肤 src_cube/faces/） */
      var _rec=cubeIndexOf(v);                            /* 自造近似档：走显式 faces[]（RGBM） */
      if(_rec&&_rec.status==='self_authored_approximate'&&_rec.resolve==='self_authored'
         &&_rec.faces&&_rec.faces.length===6) return v;
      return null; })();
    if(cubeAB && g.t_custom_ibl && g.t_custom_ibl.file){
      var _cubeBefore=g.t_custom_ibl.file;
      var _rec2=cubeIndexOf(cubeAB);
      if(_rec2&&_rec2.resolve==='self_authored'){
        /* 自造档：faces[] 是**仓库相对**路径（assets/3d/weapon_skin/_shared/...），
           而 loader 侧（L1989-1993）只会拼两处：
             · `t.indexOf('src_cube/')===0` ⇒ `base + t`
             · 否则 ⇒ `B + t.split('/').pop()`（B = 「皮肤 src_cube/faces/」）
           直接用 faces[0] 会落到第二支 ⇒ 变成皮肤目录下的**不存在的文件名** ⇒ 六面 404
           （实测：200 vs 404，见 _patch_viewer_js 的验证记录）。
           这里写成以 `src_cube/` 开头、再用 `../..` 折回仓库根的相对路径：
           浏览器与 SimpleHTTPRequestHandler **都会**规范化 `..` ⇒ 实际命中
           assets/3d/weapon_skin/_shared/cubes/<name>/rgbm/…（已用 HTTP HEAD 验过 200）。
           同时把 file 指向 `_shared/cubes/<name>/payload.dds`（自造目录里**确实**有这个文件），
           避免 `iblName` 推导路产生不存在的 src_cube/<name>.dds。 */
        g.t_custom_ibl.file='_shared/cubes/'+cubeAB+'/payload.dds';
        g.t_custom_ibl.faces_glob='src_cube/../../_shared/cubes/'+cubeAB+'/rgbm/'+cubeAB+'_f{i}_m0.png';
      }else{
        g.t_custom_ibl.file='src_cube/'+cubeAB+'.dds';
        g.t_custom_ibl.faces_glob='src_cube/faces/'+cubeAB+'_f{i}_m0.png';
      }
      /* ⚠ 注意：faces_glob 在 loader 侧若被信任就直接用；这里同时覆盖 file 基名，两条派生路都指向同一套。 */
      g.t_custom_ibl.__cube_ab={from:_cubeBefore, to:g.t_custom_ibl.file, level:'approximate(diagnostic_selector)'};
    }

    const unresolved=Object.keys(g).filter(k=>!g[k].file);
    /* ══════════════════════════════════════════════════════════════════════════════════════
       ★★★ 新增（2026-09-20，CRYSTAL_WIRE2 接手写手）：**让源声明驱动分支**（修 gate，不绕 gate）。

       缺陷（Lead 第一步诊断要求，实测证据见 CRYSTAL_WIRE2_20260920.md §1）：
         `neox_material.json` 把 1110025 的 5 个 prim **一律**写成
           `shader=null` + `shader_kind='weapon'`（prim0/prim3 写 `shader=shader\pbr_weapon.fx::TShader`），
         而**同一文件的 `shader_declared_by_material_c159` 字段如实写着源 c159 的声明族**：
           prim1 = `shader\pbr_crystal.fx::TShader`、prim4 = `shader\pbr_crystal.fx::TShader`、
           prim2 = `shader\pbr_subsurface.fx::TShader`。
         `isWeapon` 只读 `pr.shader_kind` ⇒ 恒 true ⇒ **`if(!isWeapon)` 的整条晶体链（C 公式注入、
         caustic/refraction 层、晶体槽位）一个都没执行**；同时 `progFamilyOf()` 因 `pr.shader===null`
         回落 `shader_kind` ⇒ 族恒 `pbr_weapon` ⇒ 与"晶体链"完全不相干。

         这就是「晶体/IBL 改动没有可见效果」的**机械原因**（不是数值太小，是分支根本没走）。

       修法（按 Lead 指示：**源声明驱动分支**，不绕过 gate、不改材质的 shader 名）：
         分支判定改用**有效 shader 字符串** `effShader`，取值优先级：
           ① manifest `pr.shader`（已有直证时尊重它，prim0/prim3=weapon 保持不变）
           ② manifest `pr.shader_declared_by_material_c159`（**源 c159 声明族**，本皮肤 prim1/2/4 的真值）
         两者都空 ⇒ 才回落到 `pr.shader_kind` 的旧口径（向后兼容，行为与改动前一致）。
         族判定 `progFamilyOf()` 同步改读 `effShader`（它原先只读 `pr.shader` ⇒ 同一处漏洞）。

       证据级别：`shader_declared_by_material_c159` 是**源数据字段直读**（source_verified）；
         本字段的语义（c159 material 文档里 SubMesh→MtlIdx→shader 路径）已在
         `neox_material.json.primitives[*].shader_kind_basis` 中写明，且与
         `declared_slot_groups.this_prim`（prim1/2/4 声明了 crystal/subsurface 专属槽）自洽。
         ⚠ 仍未取得的**直证**：运行时引擎到底给这些 SubMesh 绑哪个 PS（需运行时抓 cbuffer/RDEF）；
          故本处标 **source_declared（源字段直读）**，非 runtime_verified。
       ══════════════════════════════════════════════════════════════════════════════════════ */
    const declaredShader=String(pr.shader_declared_by_material_c159||'');
    const effShader=String(pr.shader||'').trim()?String(pr.shader):declaredShader;
    const effShaderSource=String(pr.shader||'').trim()?'manifest.shader'
                        :(declaredShader?'manifest.shader_declared_by_material_c159':'manifest.shader_kind(fallback)');
    /* ③ 回落：两者都空时才用旧口径 */
    const effKind=effShader?null:(String(pr.shader_kind||'').toLowerCase()||null);
    const isWeapon=(function(){
      var s=effShader.toLowerCase();
      if(s.indexOf('subsurface')>=0) return false;     /* pbr_subsurface 必先于 crystal/weapon 判 */
      if(s.indexOf('crystal')>=0)    return false;     /* pbr_crystal / pbr_subsurface_crystal */
      if(s.indexOf('clear_coat')>=0) return false;     /* 白名单族，按晶体口径 */
      if(s.indexOf('pbr_weapon')>=0||s.indexOf('pbr_default')>=0) return true;
      if(effKind) return (effKind==='weapon'||effKind==='default');
      return true;                                     /* 未知 ⇒ 保持改动前行为（weapon），不擅自改判 */
    })();
    /* 供探针/报告读取：源声明族 vs 清单族是否冲突（不静默取一）。 */
    const _kindMismatch=((String(pr.shader_kind||'').toLowerCase()==='weapon')!==isWeapon);
    const colorSlot=isWeapon?'Tex0':'t_basecolor';
    const old=mesh.material||null;
    const rec={prim:i, mtl_idx:pr.mtl_idx, material:pr.material, shader:pr.shader,
               /* ★★ 新增（2026-09-20，CRYSTAL_WIRE2）：把"源声明族 vs 清单族"的冲突显式带到报告里。 */
               shader_declared_by_material_c159:pr.shader_declared_by_material_c159||null,
               eff_shader:effShader||null, eff_shader_source:effShaderSource,
               manifest_shader_kind:pr.shader_kind||null, is_weapon:!!isWeapon,
               kind_mismatch:(_kindMismatch?{manifest_shader_kind:pr.shader_kind||null,
                                              source_declared:pr.shader_declared_by_material_c159||null,
                                              rule:'source_declaration_drives_branch'}:null),
               source_common_slots:srcSlotMeta, source_slot_conflicts:srcSlotConflict,
               /* ★ 新增（2026-09-20，ENVROUTE S2）：按源名登记但**不占槽位**的 unresolved 贴图
                  （`gem_fire` 等）—— `slot:null`、不绑 uniform、不参与颜色运算，只作如实登记。 */
               source_unresolved_slots:srcSlotUnresolved,
               pass_hint:pr.pass_hint||null, color_slot:colorSlot,
               slots:{}, sha256:{}, missing_required:missRequired,
               unresolved_slots:unresolved,
               old_material:{type:(old&&old.type)||null, had_map:!!(old&&old.map),
                             had_metalnessMap:!!(old&&old.metalnessMap),
                             map_uuid:(old&&old.map)?String(old.map.uuid):null},
               neox_replaced:false, status:'pending'};
    for(const k in g){
      rec.slots[k]={file:g[k].file, logical:g[k].logical, color_space:g[k].color_space,
                    from_source_common:!!(srcSlotMeta[k])};
      if(g[k].file) rec.sha256[k]=await sha256(g[k].file);
    }
    const ok = missRequired.length===0;
    const colorFile=(g[colorSlot]||{}).file;
    const view = state.neoxView || null;
    let m;
    if(view==='DEBUG_RED'){
      m=new state.THREE.ShaderMaterial({uniforms:{},
        vertexShader:'void main(){ gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} ',
        fragmentShader:'void main(){ gl_FragColor=vec4(1.0,0.0,0.0,1.0);} ',
        side:state.THREE.DoubleSide});
      m.userData.neox={mtl_idx:pr.mtl_idx, material:pr.material, view:'DEBUG_RED'};
    } else if(view){
      const FULL=['Tex0','t_basecolor','NormalMap','DetailMap','t_caustic_tex','t_refraction_tex','t_custom_ibl','t_reflection_tex'];
      const NEED={'T_linear':['t_basecolor'],'T_sRGB':['t_basecolor'],'m':['Tex0'],
                  'C_base':['t_basecolor','Tex0'],'forward_family':['t_basecolor','Tex0'],'source_strict':FULL.slice()};
      const need=NEED[view]||[];
      const vmiss=need.filter(k=>!g[k]||!g[k].file);
      const strict=(view==='source_strict');
      const VN={'T_linear':0,'T_sRGB':1,'m':2,'C_base':3,'forward_family':4,'source_strict':5};
      m=new state.THREE.ShaderMaterial({uniforms:{
          uView:{value:(VN[view]!==undefined?VN[view]:0)},
          uCol:{value:tex(g.t_basecolor?g.t_basecolor.file:null, view!=='T_linear')},
          uMask:{value:tex(g.Tex0?g.Tex0.file:null,false)},
          uDet:{value:tex(g.DetailMap?g.DetailMap.file:null,false)},
          uHasDet:{value:(g.DetailMap&&g.DetailMap.file)?1:0},
          uBaseColor:{value:[0.1098,0.3961,0.502,1.0]},
          uCrystalColor:{value:[0.0,0.2118,0.8,1.0]},
          uDiagA1:{value:(state.neoxDiagA1===true)?1:0},
          uMissing:{value:(strict&&vmiss.length)?1:0}},
        vertexShader:'varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);} ',
        fragmentShader:'uniform sampler2D uCol,uMask,uDet; uniform int uView; uniform float uHasDet,uDiagA1,uMissing; uniform vec4 uBaseColor,uCrystalColor; varying vec2 vUv; void main(){ if(uMissing>0.5){ gl_FragColor=vec4(1.0,0.0,1.0,1.0); return;} vec4 T=texture2D(uCol,vUv); float mm=texture2D(uMask,vUv).r; if(uView==0||uView==1){ gl_FragColor=vec4(T.rgb,1.0); return;} if(uView==2){ gl_FragColor=vec4(vec3(mm),1.0); return;} float d=(uHasDet>0.5)?(texture2D(uDet,vUv).a*mm):(uDiagA1>0.5?1.0:mm); vec3 A=mix(T.rgb,T.rgb*uCrystalColor.rgb,mm); vec3 B=mix(uBaseColor.rgb,T.rgb*uCrystalColor.rgb,d); vec3 C=mix(A,B,mm); gl_FragColor=vec4(C,1.0);} ',
        side:state.THREE.DoubleSide});
      m.userData.neoxView={view:view, program_family:(isWeapon?'deferred_weapon':'forward_basecolor_3f_d982'),
        strict:strict, need:need, missing_inputs:vmiss,
        textures:Object.fromEntries(Object.entries(g).map(([k,v])=>[k,{file:v.file,cs:v.color_space}]))};
      m.userData.neox={mtl_idx:pr.mtl_idx, material:pr.material, shader:pr.shader, view:view};
    } else {
      // 生产规则：默认即 source_strict（人工近似已停用）；只有显式 reference_approximate 才走近似
      const LAB=(function(){try{return new URLSearchParams(location.search).get('lab')==='1';}catch(e){return false;}})();
      const strictMode=(state.neoxFidelity!=='reference_approximate');
      // 逐层校验：基础色层真正需要的输入（已全部由 GPK 内容匹配取得）
      /* ★★ 改动（2026-09-18，shader-auditor，task-39 / 外审 P0-3）：**按 program family 逐族声明必需槽**，
         取消 `t_basecolor || Tex0` 这类通用 `||` 回退（它会把「缺失/错误绑定」静默掩盖，与 fail-closed 自相矛盾）。
         族的判定依据 = manifest 的 `shader` 路径（program family），并要求与 `shader_kind` 一致；
         不一致或无法识别 ⇒ 视为 **unknown family ⇒ unresolved + fail-closed**（不得默认通过、不得用 Tex0 顶替）。
         · pbr_weapon  : 必需 `Tex0`/`ParamMap`/`NormalMap`；`t_surfacemap`/`t_custom_ibl` **声明了才必需**
         · pbr_crystal : 必需 `Tex0`(源公式的掩码输入 q_mm=Tex0.r)/`NormalMap`；`t_basecolor` **声明了才必需**
                         （**声明了却没有 file ⇒ 直接 fail-closed：本 prim 不绘制**）
         · 其它/未识别 : 必需槽 = 哨兵 `__unknown_family__` ⇒ 必然 missReq 非空 ⇒ fail-closed
         **唯一豁免（显式白名单，不靠 `||`）**：晶体族中存在「**从未声明 t_basecolor**」的变体
         （族名来自 viewer.json material_layers 的 forward_crystal_roughness_24da 记录），此类 prim 按
         「无基础色贴图」处理：颜色全部来自材质常量（u_crystal_color/u_base_color），注入分支取 q_T=vec3(1.0)。
         ⚠ 证据级别如实标注：本仓库内可得的证据是 **manifest 逐 prim `textures` 键集合**（拆包器从 c159
         材质路径块解析）＋ 既有反汇编结论（晶体公式 C=mix(A,B,q_mm)、A/B 只用 u_* 常量）；
         **RDEF/DXBC 级「该变体不读 t_basecolor」直证尚未取得 ⇒ 标 unresolved**，一旦取得应在下方白名单处补引用。 */
      const progFamilyOf=function(){
        /* ★★ 修复（2026-09-20，CRYSTAL_WIRE2）：原只读 `pr.shader` —— 本皮肤 prim1/2/4 的
           `pr.shader===null` ⇒ 即便上方 `isWeapon` 已按源声明改为 false，族仍会回落 `shader_kind`
           的 `weapon` ⇒ `kindMatchesFamily` 判为不符 ⇒ `family='unresolved_unknown_family'`
           ⇒ `REQUIRED=['__unknown_family__']` ⇒ **整 prim fail-closed 不出画**。
           现与 `isWeapon` 同源：读**有效 shader 字符串** `effShader`
           （manifest.shader 优先；为空时用 manifest.shader_declared_by_material_c159）。 */
        var s=effShader.toLowerCase();
        /* ★★ 新增（2026-09-18，lead 指示 ②）：两个**实测存在**的真实族。
           注意顺序：`subsurface_crystal` 含子串 `crystal` ⇒ **必须先判它**，否则会被 pbr_crystal 抢先。 */
        if(s.indexOf('subsurface_crystal')>=0) return 'pbr_subsurface_crystal';
        if(s.indexOf('clear_coat')>=0) return 'pbr_clear_coat';
        if(s.indexOf('pbr_crystal')>=0) return 'pbr_crystal';
        if(s.indexOf('pbr_weapon')>=0||s.indexOf('pbr_default')>=0) return 'pbr_weapon';
        /* ★★ 新增（2026-09-20，CRYSTAL_WIRE2）：源 c159 的**裸族名**（本皮肤 prim2 =
           `shader\pbr_subsurface.fx::TShader`、prim1/4 = `shader\pbr_crystal.fx::TShader`）。
           源里可能带 `shader\` 前缀与 `.fx::TShader` 后缀，也可能只给族名；统一按子串判。
           顺序纪律同前：先 subsurface 再 crystal。 */
        if(s.indexOf('subsurface')>=0) return 'pbr_subsurface';
        if(s.indexOf('crystal')>=0)    return 'pbr_crystal';
        if(s.indexOf('weapon')>=0||s.indexOf('default')>=0) return 'pbr_weapon';
        /* ★★ 紧急修复（Lead，2026-09-18）：**manifest 的字段不是统一的** ——
           1110129 等有 `shader`（形如 `shader\pbr_crystal.fx::TShader`），
           而 **1110171 的 prim 只有 `shader_kind`、没有 `shader`**（其 prim 键集合 =
           prim/mtl_idx/material/glb_material/shader_kind/block_end/n_paths/textures/...）。
           原实现在 `shader` 缺失时直接 `return null` ⇒ family 变 `unresolved_unknown_family`
           ⇒ REQUIRED=['__unknown_family__'] ⇒ 必然 missReq 非空 ⇒ **7 个 prim 全部 fail-closed**
           ⇒ 页面表现为"武器不出画"（mask=0.00%、7 个 prim 的 map/metal/rough/normal 全 None、
           与 __primOnly(-1) 空场帧逐字节相同、稳定 sha 7ad37f89f32f4148）。
           现按 `shader_kind` 回退（crystal ⇒ pbr_crystal；weapon/default ⇒ pbr_weapon）。
           ⚠ 仍然保持 fail-closed 语义：**两者都识别不出时才返回 null**。 */
        var k=String((pr&&pr.shader_kind)||'').toLowerCase();
        if(k==='subsurface_crystal') return 'pbr_subsurface_crystal';   /* 同上：先于 crystal */
        if(k==='clear_coat') return 'pbr_clear_coat';
        if(k==='crystal') return 'pbr_crystal';
        /* ★★ 新增（2026-09-20，ENVROUTE S1）：源 c159 **裸族名** `pbr_subsurface`（本皮肤 prim2）的
           **清单口径**。S1 已把 `neox_material.json.primitives[2].shader_kind` 按源声明族写成
           `'subsurface'`（依据 `shader_declared_by_material_c159=shader\pbr_subsurface.fx::TShader`，
           CRYSTAL_SRC_20260920 §3.1/§7.3）。
           此前该取值在本表**无对应项 ⇒ 返回 null ⇒ family=unresolved_unknown_family ⇒ fail-closed**
           ——即"清单里写对了、运行时仍不出画"。现补上，使 `shader_kind` 成为**真正可独立驱动路由**的字段
           （不再只依赖 `shader` / `shader_declared_by_material_c159` 两个字段也在场）。
           归口与 `pbr_subsurface_crystal` 一致：晶体侧（见下方 `CRYSTAL_SIDE`）。 */
        if(k==='subsurface') return 'pbr_subsurface';
        if(k==='weapon'||k==='default') return 'pbr_weapon';
        return null;                                   /* 未知 ⇒ fail-closed */
      };
      const progFamily=progFamilyOf();
      /* ★ 新增（2026-09-18，task-39，lead 指示 1）：**family 判定优先级显式化并可验收分辨**：
           ①  manifest 的 `shader` 路径（program family 直证）    → family_source='shader'
           ②  `shader` 缺失/无法识别时回落 `shader_kind`          → family_source='shader_kind'
           ③  两者都识别不出                                       → family=null ⇒ unknown ⇒ fail-closed，source='unknown'
         现状：1110129/1110024/1110145/1110152/1110165/1110177 走 ①；
               **1110171 的 7 个 prim 的 `shader` 字段为 null（只有 shader_kind）⇒ 走 ②**。 */
      /* ★★ 扩白名单（2026-09-18，lead 指示 ②；evidence-verifier 实测存在）：
         两个**真实族**必须被识别，否则其 prim 会落 unknown ⇒ 无条件 fail-closed：
           · `pbr_clear_coat`          （1110146 prim0/1、1110161 prim4）
           · `pbr_subsurface_crystal`  （1110173 / 1110174 / 1110175 的 prim3）
         **证据级别（照 lead 要求逐条写明）**：
           · 族名来源 = c159 材料文档的 **shader 路径（直证）**；
           · 必需槽来源 = **该 prim 的 `textures` 声明集（结构证据）** —— 不抄别的族的必需集；
           · **RDEF/DXBC 级语义（该族实际消费哪些槽）未取得 ⇒ 标 unresolved**，不得当作已证语义。
         归口规则（按 lead 指示，不自拟）：
           · `pbr_clear_coat`：若声明集含 `Tex0`+`ParamMap`+`NormalMap` ⇒ 按 **weapon 口径**；
             否则**单独列一族**，`required_slots = 声明集 ∩ 已知槽名`。
           · `pbr_subsurface_crystal`：按 **晶体口径**（`t_basecolor` 若声明则必需）。 */
      const KNOWN_SLOTS=['Tex0','t_basecolor','ParamMap','NormalMap','DetailMap',
                         't_surfacemap','t_caustic_tex','t_reflection_tex','t_custom_ibl','t_refraction_tex'];
      const WEAPON_SIDE=['pbr_weapon','pbr_clear_coat'];
      /* ★★ 新增（2026-09-20，CRYSTAL_WIRE2）：`pbr_subsurface`（源 c159 裸族名，本皮肤 prim2）。
         它必须与 `pbr_subsurface_crystal` 同归**晶体侧**：
           · 进 CRYSTAL_SIDE ⇒ `crystalSide=true` ⇒ 走晶体基础色层（而非 weapon 层）；
           · 且 `kindExpect` 该族给 `false` ⇒ `!isWeapon===true` ⇒ 与上方按源声明算出的 `isWeapon` 一致
             ⇒ `kindMatchesFamily` 通过（**共同修一处**：若只加一边，本 prim 会立刻 fail-closed 不出画）。 */
      const CRYSTAL_SIDE=['pbr_crystal','pbr_subsurface_crystal','pbr_subsurface'];
      const shaderRecognized=(function(){
        /* ★★ 修复（2026-09-20，CRYSTAL_WIRE2）：原只读 `pr.shader` ⇒ 本皮肤 prim1/2/4
           （`shader===null`，真值在 `shader_declared_by_material_c159`）会被判 `shaderRecognized=false`
           ⇒ `familySource='shader_kind'`，报告把"源声明族"误标成"清单族"。现与 `isWeapon` 同源。 */
        var s=effShader.toLowerCase();
        return s.indexOf('pbr_crystal')>=0||s.indexOf('pbr_weapon')>=0||s.indexOf('pbr_default')>=0
            || s.indexOf('clear_coat')>=0||s.indexOf('subsurface')>=0||s.indexOf('crystal')>=0;
      })();
      const familySource=shaderRecognized?'shader':((progFamily!==null)?'shader_kind':'unknown');
      const declaredSlot=function(k){ return !!(pr&&pr.textures&&Object.prototype.hasOwnProperty.call(pr.textures,k)); };
      const declTriple=(declaredSlot('Tex0')&&declaredSlot('ParamMap')&&declaredSlot('NormalMap'));
      /* 族 ↔ shader_kind 一致性：仅对能给出确定期望值的族断言（其余族自成一类，不误判为 mismatch）。 */
      const kindExpect=(progFamily==='pbr_weapon')?true
                      :(progFamily==='pbr_crystal')?false
                      :(progFamily==='pbr_clear_coat')?(declTriple?true:null)
                      :(progFamily==='pbr_subsurface_crystal')?false
                      /* ★★ 新增（2026-09-20，CRYSTAL_WIRE2）：源 c159 裸族 `pbr_subsurface`
                         （本皮肤 prim2）属晶体侧 ⇒ 期望 `isWeapon===false`，与按源声明算出的
                         `isWeapon` 一致 ⇒ 不放宽、不绕过 gate（只把该族的**确定期望值**写出来）。 */
                      :(progFamily==='pbr_subsurface')?false
                      :null;
      const kindMatchesFamily=(progFamily===null)?false
        :(kindExpect===null)?true
        :(kindExpect===!!isWeapon);
      /* 白名单：晶体侧族中**未声明 t_basecolor** 的变体（见上方证据级别说明）。 */
      const CRYSTAL_NO_BASE_WHITELIST=true;
      const whitelistNoBase=(CRYSTAL_SIDE.indexOf(progFamily)>=0 && !declaredSlot('t_basecolor') && CRYSTAL_NO_BASE_WHITELIST);
      const family=(progFamily&&kindMatchesFamily)?progFamily:'unresolved_unknown_family';
      const weaponSide=(WEAPON_SIDE.indexOf(family)>=0);
      const crystalSide=(CRYSTAL_SIDE.indexOf(family)>=0);
      /* ★ 修正（2026-09-18，task-39，本文件自测暴露的第二处同类漏洞）：
         **可选槽按「有可用 file」才进必需集**，不再按"键存在"。
         证据（真实 manifest）：`t_surfacemap` 键在但 `local_file:null` 的情形见于
           1110024(5/5 prim)、1110129(5/5)、1110152(2/2) —— 按"键存在即必需"会让这三个皮肤的
           **全部 prim fail-closed（实测 __acceptanceReport: mat_visible=false / status='failed_hidden'）**，
           而 `__neox()` 仍报 failed=[] 空 ⇒ **报告与实际可见性不一致**。
         现：无 file 的可选槽记入 `declared_unlocated` 如实暴露（不静默、不顶替、也不隐藏整个 prim）；
             **颜色槽 `t_basecolor`（晶体）仍按键存在即必需** ⇒ 负控（键保留、file 置 null）必须隐藏。 */
      const slotHasFile=function(k){ return !!(g[k]&&g[k].file); };
      const declaredUnlocated=KNOWN_SLOTS.filter(function(k){ return declaredSlot(k)&&!slotHasFile(k); });
      const REQ_BY_FAMILY={
        pbr_weapon:['Tex0','ParamMap','NormalMap']
          .concat(slotHasFile('t_surfacemap')?['t_surfacemap']:[])
          .concat(slotHasFile('t_custom_ibl')?['t_custom_ibl']:[]),
        pbr_crystal:['Tex0','NormalMap'].concat(declaredSlot('t_basecolor')?['t_basecolor']:[]),
        /* clear_coat：声明集含 weapon 三件套 ⇒ 同 weapon 口径；否则**按声明集 ∩ 已知槽名**（结构证据，非抄别族） */
        pbr_clear_coat:(declTriple
          ? ['Tex0','ParamMap','NormalMap']
              .concat(slotHasFile('t_surfacemap')?['t_surfacemap']:[])
              .concat(slotHasFile('t_custom_ibl')?['t_custom_ibl']:[])
          : KNOWN_SLOTS.filter(function(k){ return declaredSlot(k); })),
        /* subsurface_crystal：晶体口径（t_basecolor 若声明则必需） */
        pbr_subsurface_crystal:['Tex0','NormalMap'].concat(declaredSlot('t_basecolor')?['t_basecolor']:[]),
        /* ★★ 新增（2026-09-20，CRYSTAL_WIRE2）：源 c159 裸族名 `pbr_subsurface`（本皮肤 prim2）。
           必需槽 = 按本 prim 的**声明集**推（结构证据）：prim2 声明 Tex0/t_basecolor/ParamMap/
           NormalMap/t_surfacemap ⇒ 晶体口径下取 `Tex0`(掩码 q_mm=Tex0.r) + `NormalMap`，
           `t_basecolor` 声明了 ⇒ 必需（与 pbr_crystal 同口径，不另造一套）。
           ⚠ RDEF/DXBC 级“该族实际消费哪些槽”未取得 ⇒ 标 unresolved（与 1110025 既有口径一致）。 */
        pbr_subsurface:['Tex0','NormalMap'].concat(declaredSlot('t_basecolor')?['t_basecolor']:[])
      };
      const REQUIRED = REQ_BY_FAMILY[family] || ['__unknown_family__'];
      // 尚未实现的后续层（如实登记，不影响基础色层）
      /* ★ 改动（2026-09-16）：DetailMap 由 REQUIRED 移入 PENDING_LAYERS。
         原设计把 DetailMap 当作晶体基础色层的必需项，缺失即 fail-closed；但 manifest 中它是
         state=missing / no_source_resource_located，于是 5 个晶体 prim 全部被丢弃
         （lab 显品红诊断色、生产 m.visible=false）—— 即用户反馈的「晶体没上色」。
         依据：源公式里 DetailMap 只参与 d = m × D.a **一项**；缺它时 viewer 既有分支已把 d 退化为 m
         （与 ?neoxView=C_base 的 uDiagA1 分支同构），颜色仍由已验证输入
         t_basecolor × u_crystal_color + u_base_color 决定。
         这是**带标注的降级渲染**，不是静默补位：链上 detail_map_status 会明确记为
         'unresolved: 以 d=m 降级渲染'，pending_layers 亦保留 DetailMap。 */
      /* ★ 新增（2026-09-18，shader-auditor；lead 指示 ④＋修正）：t_reflection_tex 按**键是否存在**判断。
         规则（lead 2026-09-18 修正）：**没有键 ⇒ 该 prim 根本没有这一层**（不建 uniform、不登记缺口）；
         有键但 local_file 为空 / state=not_shipped ⇒ 登记为未发布，同样不绑。
         原实现按 `state==='absent'` 判断是错的 —— manifest 一度给 prim3/6 写了 `{state:'absent'}`
         的空键，导致 viewer 尝试处理该槽、prim3 的 map 变 null（自检 FAIL 由 mesh[5,6] 扩到 [3,5,6]）。
         现只看键存在性，与 manifest 是否带 state 字段解耦。 */
      const hasReflKey=!!(pr.textures && Object.prototype.hasOwnProperty.call(pr.textures,'t_reflection_tex'));
      const PENDING_LAYERS = (isWeapon ? []
        : ['DetailMap','t_caustic_tex','t_refraction_tex','t_custom_ibl'].concat(hasReflKey?['t_reflection_tex']:[]));
      // 环境参与颜色运算（源材质 metalness=1）：cube 未装成时 strict 必须 fail-closed
      const iblMissing = !(g.t_custom_ibl && g.t_custom_ibl.file);
      /* ★ 改动（2026-09-18，shader-auditor，task-13 B）：envMode / envAllowed 由此处**下移到 cube IIFE 之后**。
         原判定只看 `t_custom_ibl.file` 字符串是否存在 ⇒ 六面 URL 坍缩成同一张 404 的空 cube
         会冒充 `source_ibl`，问题被静默掩盖（= 1110129 纯黑剪影的"静默面"）。
         现改为按 **cube 解析结果 + 本次解析的错误标记** 后置判定，见下方 `const envMode=...`。 */
      const missReq = REQUIRED.filter(k=>!g[k]||!g[k].file);
      const chainOk = missReq.length===0;
      const bm=(g.Tex0&&g.Tex0.file)||((g.t_basecolor&&g.t_basecolor.file)?g.t_basecolor.file.replace(/_a\.png$/,'_b_m.png'):null);
      // ★ 修复：不再猜文件名。族号从 manifest 的任意真实路径中提取（允许 .png/.tga 与查询串，任意槽位）
      const famOf=function(p){var m=String(p||'').match(/(?:^|\/)(\d{3})_[a-z_]+(?:\.(?:png|tga))?(?:\?|$)/);return m?m[1]:null;};
      /* ★★ 改动（2026-09-18，task-39 P0-3）：删除 `albedoSlot = isWeapon ? Tex0 : (t_basecolor||Tex0)` 的通用回退。
         颜色槽**按族逐一显式取值**：weapon ⇒ Tex0；crystal ⇒ 仅当 manifest 声明了 t_basecolor 才取它；
         crystal 且未声明 ⇒ 白名单的「无基础色贴图」情形（srcA=null，颜色全来自材质常量）。 */
      const albedoSlotName = weaponSide ? 'Tex0'
                           : (declaredSlot('t_basecolor') ? 't_basecolor'
                             : (whitelistNoBase ? 'none(该族未声明 t_basecolor：白名单，颜色取材质常量)' : 'none'));
      const albedoSlot = weaponSide ? (g.Tex0||{})
                       : ((crystalSide&&declaredSlot('t_basecolor')) ? (g.t_basecolor||{}) : {});
      const srcA = albedoSlot.file || null;                       // 直接消费 manifest 路径（无回退、无拼接）
      const fam = famOf(srcA) || famOf((g.Tex0||{}).file) || famOf((g.NormalMap||{}).file)
               || famOf((g.ParamMap||{}).file) || famOf((g.t_surfacemap||{}).file) || null;
      const srcM = fam ? ('src_tex/param_repack_'+fam+'.png') : null;
      // ★ 逐材质源 IBL：按 manifest 的 t_custom_ibl.local_file 装载（绝不共享、绝不 PMREM）
      const iblPath=(g.t_custom_ibl&&g.t_custom_ibl.file)||null;
      /* ★★ 修复（2026-09-18）：原为 cube 名白名单 `/(qiangpi|car_studio01)/`，
         任何其它 cube（如天马行空的 `bg61f_light_spherereflectioncapture_1.dds`）都取不到
         ⇒ iblName=null ⇒ iblCube=null ⇒ **IBL 注入整块不触发** ⇒ 画面偏暗。
         现改为**从 manifest 的文件基名派生**，不再有白名单。 */
      /* ★★ 修复（2026-09-18，对抗复核 ②）：cube 名派生的四个反例。
         原式 `iblPath.split('/').pop().replace(/\.(dds|png|cube)$/i,'')`：
           ① local_file 为 null 时 L828 回落到 `logical` ⇒ `common\env_map\qiangpi.cube`（**反斜杠**）
              ⇒ split('/') 得整串 ⇒ iblName='common\env_map\qiangpi' ⇒ 面 URL 含反斜杠 = 404 ✗
           ② `?v=2` 查询串、③ 大写扩展名、④ 尾空格 同样出错 ✗
         现统一规范化：反斜杠→斜杠、取基名、去查询串、trim、扩展名（不分大小写）后置剥离。 */
      const iblName=iblPath?(function(p){
        var s=String(p).replace(/\\/g,'/');
        s=s.split('?')[0].split('#')[0].trim();
        s=s.split('/').pop()||'';
        return s.replace(/\.(dds|png|cube|tga)$/i,'');
      })(iblPath):null;
      const iblCube=(function(){
        /* ★ 改动（2026-09-18，shader-auditor，task-13 A）：每次解析重置错误标记 ——
           该标记只反映**本次**解析结果（缓存命中视为上次已验证通过 ⇒ null）。 */
        state.__cubeDirErr=null;
        if(!iblName) return null;
        if(!state.__srcCubeCache) state.__srcCubeCache={};
        if(state.__srcCubeCache[iblName]){
          /* ★ 新增（2026-09-18，task-40）：缓存命中也要过**就绪门** —— 未就绪不得绑定（返回 null），
             否则首个 prim 触发加载、其余 prim 从缓存拿到同一个「空 cube」照样会全黑。 */
          var g0=state.__iblGate&&state.__iblGate[iblName];
          return (g0&&g0.ready)?state.__srcCubeCache[iblName]:null;
        }
        /* ★★ 修复（2026-09-18）：原把 cube 面目录**写死为 1110171** ⇒ 其它皮肤的 cube 装不上。
           现从 manifest 基址 `base` 派生（L783 fetch(base+'neox_material.json') 已证明 base 以 / 结尾）。 */
        const T=state.THREE;
        /* ★ 修复（2026-09-18，对抗复核 ③）：base 非字符串时**不再静默回落到 1110171 的 cube 目录**
           （换皮肤会取错目录且不报错）⇒ 显式记录并 fail-closed（返回 null，不加载错误资源）。 */
        if(!(typeof base==='string'&&base)){
          state.__cubeDirErr='[cube] manifest base 非字符串（'+(typeof base)+'）→ 拒绝回落到 1110171 目录，本次不加载 cube';
          try{ console.error(state.__cubeDirErr); }catch(e){}
          return null;
        }
        const B=base.replace(/\/?$/,'/')+'src_cube/faces/';
        /* ★ 对抗复核 ②（首选路径）：manifest 自带 faces_glob（如 src_cube/faces/qiangpi_f{0..5}_m0.png）
           时直接用它构造六面 URL；缺失才回落到 iblName 派生。 */
        const fg=(g.t_custom_ibl&&g.t_custom_ibl.faces_glob)||null;
        const urls=[0,1,2,3,4,5].map(function(i){
          if(fg){ var t=String(fg).replace(/\{[^}]*\}/g,String(i));
                  if(t.indexOf('src_cube/')===0) return base.replace(/\/?$/,'/')+t;
                  return B+t.split('/').pop(); }
          return B+iblName+'_f'+i+'_m0.png';
        });
        if(window.__cubeDirProbe!=='object') window.__cubeDirProbe={};
        window.__cubeDirProbe[iblName]={base:B, faces_glob:fg, urls:urls};
        /* ★ 新增（2026-09-18，shader-auditor，task-13 A）：六面 URL **互异性守门**（env-auditor 方案 C）。
           背景：1110129 的 5 个 prim 曾把 faces_glob 写成 shell 通配 `qiangpi_f*_m0.png`；
           L1049 只替换 `{...}` 占位符 ⇒ `*` 原样进 URL ⇒ 六面坍缩成**同一个 404**
           ⇒ CubeTexture.image 全空（ibl_faces=0）⇒ 源环境辐射=0；该皮肤源 metalness=1 ⇒ 输出≈0
           ⇒ 剪影亮度 15.2 ≈ 背景 15（而正常皮肤同像素集 51.3）。
           这里按**结果**断言：六条 URL 不互异即拒绝装配，且**不写入 state.__srcCubeCache**（不缓存坏 cube）。 */
        (function(){
          var uniq=new Set(urls).size;
          if(window.__cubeDirProbe[iblName]) window.__cubeDirProbe[iblName].unique=uniq;
          if(uniq!==6){
            state.__cubeDirErr='[cube] 六面 URL 非互异（唯一 '+uniq+' 条）⇒ 拒绝装配空 cube：'+urls[0];
            try{ console.error(state.__cubeDirErr); }catch(e){}
            if(window.__cubeDirProbe[iblName]) window.__cubeDirProbe[iblName].rejected=true;
          }
          return uniq;
        })();
        if(state.__cubeDirErr) return null;      // fail-closed：不加载、不缓存
        /* ★★ 新增（2026-09-18，shader-auditor，task-40）：**六面就绪门（先绑后校验 → 改成就绪才绑）**。
           动机（viewer-auditor 受控复现）：该链 metalness=1/roughness=1，外观几乎全由 IBL 提供，
           cube 一空即全黑（暗帧 sha `516b56cc43081bdf` / meanL 0.28，~21% 概率；CDP 屏蔽 `*qiangpi*` 可复现同一 sha）。
           判据：`CubeTexture.image` 的 6 个 HTMLImageElement 全部 `complete && naturalWidth>0`。
           **未就绪 ⇒ 本函数返回 null（不绑 envMap / uCustomIbl）**，绝不把空 cube 送进着色；
           同时登记 `state.__iblGate[iblName]` 并置 `__iblRebindPending`，六面到齐后由 `renderFrame` 触发**一次重绑**。 */
        const gate={tex:null, total:6, loaded:0, ready:false, failed:false, retries:0, bound:false};
        if(!state.__iblGate) state.__iblGate={};
        state.__iblGate[iblName]=gate;
        const facesLoaded=function(x){
          try{ var im=x&&x.image; if(!im||!im.length) return 0; var c=0;
            for(var i=0;i<im.length;i++){ var e=im[i];
              if(e&&(e.complete===undefined||e.complete)&&(e.naturalWidth===undefined||e.naturalWidth>0)) c++; }
            return c; }catch(err){ return 0; }
        };
        const t=new T.CubeTextureLoader().load(urls, function(){
          gate.loaded=facesLoaded(t); gate.ready=(gate.loaded>=6);
          /* ★★ (C) 补齐（2026-09-19，shader-auditor，task-49；备份 wsv_bak_task49f_20260918_235157.js = 75784198127282DC）。
             上一轮只做了"收敛式重试"，触发点仍是 `renderFrame` tick ⇒ 实测 all_green 仍 8.7–9.4 s。
             这里把**触发点提前到 onLoad 内**：就绪即置 `__iblRebindPending` 并**在下一帧尝试**（不再等待"最后一个 cube"），
             **但绝不再用"清 flag"式写法** —— 收敛逻辑（renderFrame 内）会在重建后实测缺 IBL 的 prim 数，
             未收敛且未达上限（`IBL_RETRY_CAP=6`）就**继续保持 pending 重试**，达上限 ⇒ `__iblRetryExhausted=true`。
             另：`__iblRetryCount` 在本 cube 首次就绪时**不清零**（跨 cube 累计，上限为总尝试数），避免"每个 cube 各 6 次"放大噪声。 */
          if(gate.ready){
            state.__iblRebindPending=true;
            state.__iblReadyAt=state.__iblReadyAt||{};
            state.__iblReadyAt[iblName]=Math.round(performance.now());
            try{_forceRender();}catch(e){}   /* 只重绘当前状态（不重建），使就绪帧尽早落地；重建由 tick 收敛逻辑负责 */
          }
        }, undefined, function(){ gate.failed=true; });
        t.colorSpace=T.NoColorSpace;      // DDS 头 = B8G8R8A8_UNORM，无 sRGB 标志
        t.generateMipmaps=true;           // 诊断需 mip0/显式 LOD，正式资源保留 mip 链
        t.minFilter=T.LinearMipmapLinearFilter; t.magFilter=T.LinearFilter;
        t.wrapS=t.wrapT=T.ClampToEdgeWrapping;
        try{ if(MAXANISO>1) t.anisotropy=MAXANISO; }catch(e){}
        gate.tex=t; gate.loaded=facesLoaded(t); gate.ready=(gate.loaded>=6);
        state.__srcCubeCache[iblName]=t;   // 纹理对象仍缓存（供后续 prim 复用与重绑），但**未就绪不返回**
        return gate.ready?t:null;
      })();
      /* ★ 改动（2026-09-18，shader-auditor，task-13 B）：envMode／envAllowed 的**后置判定**。
         cube IIFE 已在本 prim 上跑完（`state.__cubeDirErr` 只反映本次解析），故此处可准确区分三种失败：
           · 无源槽（t_custom_ibl 无 file）        ⇒ missing_source_ibl（与旧行为一致）
           · 六面 URL 坍缩（守门拒绝装配空 cube）  ⇒ duplicate_face_urls_ibl（**新增，不再冒充 source_ibl**）
           · 解析成功                              ⇒ source_ibl
         验收线：1110145/1110171/1110177 必须仍为 source_ibl 且 ibl_faces=6（不得回归）。 */
      const cubeErr=(state.__cubeDirErr||null);
      /* ★ 改动（2026-09-19，task-49）：窗口期状态改为可判的 `ibl_pending` —— 不再用 `missing_source_ibl`
         冒充"资源缺失"（cube 存在、只是六面尚未就绪时是**暂时**状态，且会被 onLoad 直接修复）。 */
      /* ★ 口径修正（2026-09-19，task-49，lead 指示 ①）：`ibl_pending` 判据覆盖两种情况 ——
         **cube 尚未就绪** 与 **gate 尚未登记**（gate 未登记 ≠ 资源缺失；prim 材质可能早于 gate 建立）。
         仅当"无 iblName / gate 已登记且 failed / 无 cube 目录错误"时才落 `missing_source_ibl`。 */
      const g0=(iblName&&state.__iblGate)?state.__iblGate[iblName]:null;
      const cubePending=!!(iblName && (!g0 || (!g0.ready && !g0.failed)));
      const envMode = strictMode
        ? (iblCube ? 'source_ibl'
                   : (cubeErr ? 'duplicate_face_urls_ibl' : (cubePending ? 'ibl_pending' : 'missing_source_ibl')))
        : 'diagnostic_environment';
      const envAllowed = (envMode!=='missing_source_ibl' && envMode!=='duplicate_face_urls_ibl');
      /* ★★ 改动（2026-09-18，task-39）：albedoOk 改为**族感知 + 白名单显式**。
         · weapon / 声明了 t_basecolor 的晶体 ⇒ 必须有 srcA（缺 ⇒ fail-closed，不再回退）
         · 白名单晶体（未声明 t_basecolor）⇒ 允许 srcA=null：颜色由材质常量给出（注入取 q_T=vec3(1.0)） */
      const albedoOk = srcA ? true : (whitelistNoBase===true && crystalSide);
      // 逐族一致性断言（跨槽必须同族，否则 fail-closed）
      const fams=[famOf(srcA),famosCheck()].filter(Boolean);
      function famosCheck(){ var out=[]; ['Tex0','t_basecolor','ParamMap','NormalMap','t_surfacemap'].forEach(function(k){ var f=g[k]&&g[k].file; if(f) out.push(famOf(f)); }); return out.length?out[0]:null; }
      if(strictMode && albedoOk && fam){
        var allF=['Tex0','t_basecolor','ParamMap','NormalMap','t_surfacemap'].map(function(k){return g[k]&&g[k].file?famOf(g[k].file):null;}).filter(Boolean);
        if(new Set(allF).size>1){ state.__famMismatch=(state.__famMismatch||0)+1; }
      }
      const MTL_METAL={0:1.0,1:1.0,2:1.0,3:0.75,4:1.0,5:1.0,6:0.75};
      const primIdx=i;
      // ★ 正式链只读源贴图；weapon Tex0 = 001a（源），ParamMap = 001m（通道重排）
      /* srcA/srcM 已由上方 manifest 直读得到（不再拼名） */
      if(strictMode && !(albedoOk && (!isWeapon || srcM))){
        // ★ 修复（2026-09-16）：原为 `m=null;` —— 但下方 m.userData.chain(L938) 与 m.visible(L950)
        //   都要求材质对象非空。空指针异常会抛出 applyNeoxManifest，导致整条源链中断，
        //   全部 7 个材质退化为 GLB 默认黑材质（症状：武器黑剪影、__neox() 无 report、
        //   setNeoxView('DEBUG_RED') 失效、度量遮罩为空）。
        //   改为建占位材质：fail-closed 语义完全保留（由 !chainOk 分支置 m.visible=false 不绘制），
        //   但不再影响其余 prim 正常出链。
        state.__strictFailClosed=(state.__strictFailClosed||0)+1;
        m=new state.THREE.MeshStandardMaterial({metalness:1.0,roughness:1.0,envMapIntensity:0.0});
        m.userData.failClosedPlaceholder=true;
      }
      else if(isWeapon){
        m=new state.THREE.MeshStandardMaterial({
          map: tex(srcA, true),
          metalnessMap: tex(srcM, false), roughnessMap: tex(srcM, false),
          metalness: 1.0, roughness: 1.0, envMapIntensity: (envAllowed?1.0:0.0),
          normalMap: tex((g.NormalMap||{}).file,false) });
        if(iblCube){ m.envMap=iblCube; }
        m.userData.ibl=iblName||null;
      } else {
        // 晶体基底色层：C = mix(A,B,q_mm)，由下方注入实现。
        // ★ 修正（2026-09-16）：metalness 由 1.0 改为 0.0（介电）。
        //   依据本文件 L1295-1301 早已记录的结构结论：u_crystal_metallic(cb0[10].y) 属"晶体层"参数，
        //   **不等于基底 albedo 的金属度**；一旦映射到 Three 的 metalness，albedo 就退出漫反射着色，
        //   外观几乎全由环境反射决定 → 晶体变暗发闷、亮紫/亮蓝丢失（用户反馈「紫色蓝色要染回去」即此症状）。
        //   晶体层（反射/折射/焦散）尚未实现 → 关闭并标 unresolved；基底层按介电处理。
        //   源值 u_crystal_metallic 仍保留在 crystal_params 中并记入 userData，语义 unresolved，不参与渲染。
        /* ★ 修正（2026-09-17，用户口径第 4 条）：晶体 roughness 不得继续硬编码 1.0。
           源公式：Roughness = t_basecolor.a（外审报告 §3.5 已证）→ 实测 012_a 均值 0.637 / 010_a 均值 0.732。
           Three 从 roughnessMap.G 读粗糙度，故使用派生贴图 rough_repack_<fam>.png
           （G = 对应 *_a.png 的 alpha，R/B 置 255；**纯通道重排，无任何数值改动**）。
           对应 lod = 5 + 1.2*log2(0.637) ≈ 4.23，而非原先硬编码 1.0 导致的固定 5.0。
           DetailMap 对 base/crystal/detail 混合的贡献仍缺 → 保持 incomplete，不补常数。 */
        /* ★ 改动（2026-09-18，task-39）：白名单晶体（未声明 t_basecolor）**不绑任何 albedo 贴图**；
           但注入公式采样用 `vMapUv`，而 three 只在 USE_MAP 时声明该 varying（uv_pars_fragment）
           ⇒ 仍绑 Tex0 作 **UV/掩码载体**，并在链上显式标注其角色。这不是"用 Tex0 顶替 t_basecolor"：
           `srcA` 保持 null、`albedo_slot` 记为 none，颜色由常量给出（注入取 q_T=vec3(1.0)）。 */
        const crystalMapFile = srcA ? srcA : (whitelistNoBase ? ((g.Tex0&&g.Tex0.file)||null) : null);
        const crystalMapRole = srcA ? 'albedo(srcA)'
          : (whitelistNoBase ? 'uv/mask_carrier(Tex0)：不参与颜色（q_T=vec3(1.0)，颜色来自 u_crystal_color/u_base_color）'
                             : 'none');
        m=new state.THREE.MeshStandardMaterial({
          map: tex(crystalMapFile, true),
          metalness: 0.0, roughness: 1.0, envMapIntensity: (envAllowed?1.0:0.0),
          roughnessMap: fam?tex('src_tex/rough_repack_'+fam+'.png', false):null,
          normalMap: tex((g.NormalMap||{}).file,false) });
        if(iblCube){ m.envMap=iblCube; }
        m.userData.ibl=iblName||null;
      }
      /* ★ 口径重写（2026-09-17，用户定版）：
         「恢复 Three 的完整 BRDF，只用源 cube 替换环境辐射输入」
         禁止对 outgoingLight 额外叠加；禁止整体覆盖最终颜色。

         做法：替换 Three 的 getIBLRadiance，使其从**源 cube** 产出 radiance，
         再由 Three 原有的 direct/indirect diffuse、specular、F0、Fresnel、遮蔽与 toneMapping 链加权。
         依据：Three r180 的 getIBLRadiance 仅在 ENVMAP_TYPE_CUBE_UV 下有实现，
         而本项目持有原始 CubeTexture（明令禁止用 PMREM 冒充源 shader），故 Three 自带 IBL 恒返回 vec3(0.0)
         —— 必须由我们提供 radiance 输入，但**不得**接管最终颜色。

         注入手法（避免函数重定义）：
           ① 片元顶部 #define getIBLRadiance getIBLRadiance_three  → Three 原定义被改名
           ② 在 void main() 之前 #undef getIBLRadiance，再定义同名函数

         ⚠ 路径定性（用户第 8 条）：source textures + source cube + Three BRDF approximation。
           这不是完整 NeoX 源级复原；完整源级版本需先恢复 ASM 中的 r13 及相关全局常量，
           再替换 Three BRDF。 */
      if(iblCube && strictMode){
        m.onBeforeCompile=function(sh){
          sh.uniforms.uCustomIbl={value:iblCube};
          sh.uniforms.uIblRot=sh.uniforms.uIblRot||{value:(state.iblRot===undefined?0.0:state.iblRot)};
          sh.uniforms.uIblMix=sh.uniforms.uIblMix||{value:(state.iblMix===undefined?0.0:state.iblMix)};
          /* ★★ 改动（2026-09-19，shader-auditor，task-45 第 1 项，lead 裁定）：默认 `uIblScale` **0.25 → 1.0**。
             依据：源常量 `u_env_day2night_exposure`（asm 549 / cb1[239].x）**不可得**（运行时逐帧 cbuffer，
             RDEF 位置已知 @3824）⇒ **0.25 是从 lab_src.html 拷来的人工值、无源依据**；
             1.0 = **不引入任何比例因子**。定性是「**撤销一个无源依据的人工常量**」，**不是**调亮/拟合参考图。
             开关保留（`__iblParams({scale})` / 页面按钮组 1.0↔0.75↔0.5↔0.25↔0）。
             同文件另三处默认此前不一致（L2491/L3457=1.0，按钮组与 __iblDiag=0.25）⇒ 本次统一为 1.0。 */
          sh.uniforms.uIblScale=sh.uniforms.uIblScale||{value:(state.iblScale===undefined?1.0:state.iblScale)};
          /* ★★ 新增（2026-09-19，shader-auditor，task-45 第 1 项）：**材质级环境辐照增益 `u_cube_brightness`**。
             源：`003996.c159` f32，entry@2438/3257（1110177 prim1 = 0.71、prim2 = 2.74；**1110171 五个晶体 prim 无此声明**）。
             现状缺陷：生产路径的消费点（`applyMaterialLayers` 内 `envMapIntensity = env*(b)`）**永不执行**
             （`applied>0` 早退）⇒ prim2 一直按 1.0 算、**少 2.74×**。
             现就地接在 radiance 出口（与 `uIblScale` 同一处乘性），**值一律从 manifest 逐 prim 读**（`source_uniforms.u_cube_brightness`），
             **缺失 ⇒ 不覆盖（off 且值恒 1.0）**，**不跨皮肤借值**。
             **默认 OFF**（`state.__cubeBrightOn!==true`）：默认态与接线前**逐字节相同**；开关 `__cubeBright(true|false)`。
             且**不再有第二状态源**：开关状态只体现在 uniform 值上，探针从材质读。 */
          var cbVal=(function(){ var e=((pr&&pr.source_uniforms)||{})['u_cube_brightness'];
            if(e===null||e===undefined) return null;
            var v=(typeof e==='object'&&('value' in e))?e.value:e;
            var n=Number(v); return Number.isFinite(n)?n:null; })();
          /* ★★★ 新增（2026-09-20，CRYSTAL_WIRE2）：本皮肤 `u_cube_brightness` 的**源区间近似**接线。
             Lead 裁决 C12：001348/001360（本皮肤两个 c159）名字表各 78 条、参数核 33 条**均无此名**
             ⇒ `source_present_value_unreadable`；引擎默认值 ⇒ 只允许**源侧区间扫描并标 approximate**。
             同族源值（`CRYSTAL_SRC_20260920` §1 / PINS_RULINGS C12）：**0.71 / 0.99 / 2.74**。
             实现（三档标注）：
               · `source`（默认）= manifest `source_uniforms.u_cube_brightness` —— **本皮肤 absent** ⇒ 不接线（原行为）；
               · `approx`         = 源区间档位（0.71 / 0.99 / 2.74 / 1.0 对照），**默认 OFF**，
                 必须由 `__cubeBright(true)` 或 `?cubeBright=<v>` 显式选择 ⇒ 默认渲染与接线前逐像素相同；
               · 值一律**逐 prim**作用于 radiance 出口，**不跨皮肤借值**、不引入任何其它比例因子。 */
          var cbApprox=(function(){
            var q=null; try{ q=new URLSearchParams(location.search).get('cubeBright'); }catch(e){}
            if(q!==null&&q!==undefined&&String(q).trim()!==''){ var n=Number(q); if(Number.isFinite(n)) return {value:n,src:'url:?cubeBright='+q}; }
            var g0=(state.__cubeBrightApproxDefault!==undefined&&state.__cubeBrightApproxDefault!==null)
              ?Number(state.__cubeBrightApproxDefault):null;
            if(Number.isFinite(g0)) return {value:g0, src:'state.__cubeBrightApproxDefault'};
            return null; })();
          var cbLevel=(cbVal!==null)?'source(manifest)':(cbApprox?'approximate(source_range_scan)':'absent');
          /* ★★ 修正（2026-09-20，CRYSTAL_WIRE2 自查发现）：近似档**必须自己开闸**。
             原实现在这里只写 uniform 值，而 `uCubeBrightOn` 仍只认 `state.__cubeBrightOn===true`
             ⇒ 四档 0.71/0.99/2.74/1.0 实测**逐像素相同、changed_px 完全一致**（探针实测
             `uCubeBrightOn=0 / uCubeBright=2.74`）——即"档位切换了、闸门没开"。
             现：显式 URL 档（`?cubeBright=<v>`）**自己就是那道闸**（用户/Lead 主动要求该档 ⇒ 开）；
             `state.__cubeBrightOn===true`（`__cubeBright(true)`）仍然可以单独开闸。
             默认（两者皆无）⇒ On=0 ⇒ 逐像素与接线前相同（default-OFF 纪律不变）。 */
          var cbFromUrl=!!(cbApprox&&String(cbApprox.src||'').indexOf('url:')===0);
          if(cbVal===null&&cbApprox) cbVal=cbApprox.value;

          const uCubeBrightOn={value:(((state.__cubeBrightOn===true)||cbFromUrl) && cbVal!==null && Math.abs(cbVal-1)>1e-9)?1.0:0.0};
          const uCubeBright={value:(cbVal===null?1.0:cbVal)};
          sh.uniforms.uCubeBrightOn=uCubeBrightOn; sh.uniforms.uCubeBright=uCubeBright;
          try{ m.userData.__cubeBright={value:(cbVal===null?null:cbVal), source:(cbVal===null?'absent':cbLevel),
                                        approx:(cbLevel.indexOf('approximate')===0),
                                        approx_src:(cbApprox?cbApprox.src:null),
                                        approx_basis:'Lead 裁决 C12：本皮肤未声明 u_cube_brightness ⇒ 只允许源侧区间扫描；'
                                                    +'同族源值 0.71/0.99/2.74（003996/004008.c159）+1.0 对照',
                                        prim:(pr&&pr.prim), on:uCubeBrightOn.value>0.5}; }catch(e){}
          /* ★★ 新增（2026-09-19，shader-auditor，task-45 第 2 项）：**材质级 IBL 旋转 `u_rotate_angle`**。
             源：1110177 晶体 prim1 = **3.09 rad**（f32@2429/payload 2434，raw `8fc24540`）、
             prim2 = **2.60 rad**（f32@3248/payload 3253，raw `66662640`）；1110171 全 prim **无声明**。
             真名映射证据（四路交叉，见 `_target_1110171\ENV_IBL_spec_1110171_1110177_20260919.md` L45、
             `报告_1110171_源驱动材质_P1结构复原_20260916.md` L29/L121-143、`接手核验记录_1110171…_20260916.md` L74-78、
             `折射层公式复原规格_20260917.md` L46-53）：`cb0[7].w = u_rotate_angle`（材质级 `NeoxUBOLocal`@124；
             **weapon PS 为 cb0[4].x**），仅用于 IBL 采样方向 sincos（晶体 PS L532）——
             与折射链**无关**（`u_refraction_rotation` 是另一条链，已有自己的开关）。
             现状缺陷：`uIblRot` 只来自 `state.iblRot`（默认 0）⇒ **源声明的 3.09 / 2.60 rad 从未生效**，
             反射方向与源相差 149°~177°（决定高对比 cube 上亮暗象限落点）。
             接法：**只改 uniform 值**（不新增第二状态源）——源开关 ON 且值存在 ⇒ 用源值；否则保持既有 `state.iblRot`（默认 0）。
             **默认 OFF**（`state.__iblRotSrcOn!==true`）⇒ 默认态与接线前**逐字节相同**；开关 `__srcRot(true|false)`。
             ⚠ 与 `__iblParams({rot:N})` 的交互：后者写 `state.iblRot`；源开关 ON 时对有源值的 prim **不生效**（探针同时回报 `manual_rot`，不会被当成假 A/B）。 */
          var rotVal=(function(){ var e=((pr&&pr.source_uniforms)||{})['u_rotate_angle'];
            if(e===null||e===undefined) return null;
            var v=(typeof e==='object'&&('value' in e))?e.value:e;
            var n=Number(v); return Number.isFinite(n)?n:null; })();
          var manualRot=(state.iblRot===undefined?0.0:state.iblRot);
          state.iblRotSrc=state.iblRotSrc||{};
          const uIblRotOn={value:(state.__iblRotSrcOn===true && rotVal!==null)?1.0:0.0};
          sh.uniforms.uIblRotOn=uIblRotOn;
          sh.uniforms.uIblRot.value=(uIblRotOn.value>0.5?rotVal:manualRot);
          try{ m.userData.__iblRotSrc={value:(rotVal===null?null:rotVal), source:(rotVal===null?'absent':'manifest'),
                                       prim:(pr&&pr.prim), on:uIblRotOn.value>0.5, manual_rot:manualRot}; }catch(e){}
          /* ★★ 新增（2026-09-19，shader-auditor，task-47）：**晶体源 BRDF 的逐 prim 值 + uniform**。
             源（spec `RX_BRDF_wiring_spec_20260919.md` §1.1/§2.3）：
               `metal    = saturate( lerp(u_base_metallic, u_crystal_metallic, w) )`   （asm L443-444）
               `spec     = lerp(u_base_specular, u_crystal_specular, w)`               （asm L441-442）
               `w        = m² · DetailMap.a`（asm L438；`m = saturate(Tex0.r)`）
               `F0       = lerp(spec·0.079956, albedo, metal)`、`diffuse = albedo·(1−metal)`（L547-551）
             值源：manifest `source_uniforms`（带 entry/payload 偏移 + raw hex，**原始字节级证据**）。
               ⚠ lead 裁决 C2：`1110171 prim5` 两源冲突（`crystal_params=1` vs `source_uniforms=0.75`，raw `0000403f`）
                 ⇒ **取 source_uniforms 的 0.75**，并把冲突写进 `__brdfSrc.conflict`（探针显式报出，**不静默取一**）。
             口径（缺值不覆盖、不借值）：
               · `uCrystalMetal` 缺失 ⇒ 该 prim **整 prim 不接线**（`uBrdfOn` 永远 0、金属度保持 0）；
               · `uBaseMetal` 缺失 ⇒ 用**现值 0.0**（现有晶体链硬编 `metalness:0.0` 的等效端点），**不跨 prim/皮肤借值**；
               · `spec` 因子本轮**不注入**（两个目标皮肤的 `u_crystal_specular` 全为 1、`u_base_specular` 仅 1110177 prim2 且=1
                 ⇒ `spec = lerp(1,1,w) ≡ 1`，即 0.079956 那处 patch 已等价）——结论写进报告。
             **就绪门**：`uBrdfOn` 只有在 `envMode==='source_ibl'`（源 cube 已就绪、`uCustomIbl` 六面可用）时才允许 1；
               窗口期 `ibl_pending ⇒ 0` ⇒ 金属度保持 0（否则金属化后无环境可反射会变黑，spec §4 风险 1）。
             **默认 OFF**：`state.__brdfSrcOn!==true` ⇒ `uBrdfOn=0` ⇒ 默认渲染与接线前逐字节相同。 */
          var suBrdf=function(k){ var e=((pr&&pr.source_uniforms)||{})[k];
            if(e===null||e===undefined) return null;
            var v=(typeof e==='object'&&('value' in e))?e.value:e;
            var n=Number(v); return Number.isFinite(n)?n:null; };
          var bmVal=suBrdf('u_base_metallic'), cmVal=suBrdf('u_crystal_metallic');
          var cpCm=((pr&&pr.crystal_params)||{}).u_crystal_metallic;
          var brdfWireable=(cmVal!==null);
          var iblReadyNow=(envMode==='source_ibl');
          const uBrdfOn={value:((state.__brdfSrcOn===true&&brdfWireable&&iblReadyNow)?1.0:0.0)};
          const uBaseMetal={value:(bmVal===null?0.0:bmVal)};
          const uCrystalMetal={value:(cmVal===null?0.0:cmVal)};
          sh.uniforms.uBrdfOn=uBrdfOn; sh.uniforms.uBaseMetal=uBaseMetal; sh.uniforms.uCrystalMetal=uCrystalMetal;
          /* ★ 新增（2026-09-19，task-59 (c)）：环境辐照（源 cube 重建）的三只 uniform。
             · `uIrrOn` 初值 = 开关 ∧ 该 prim 的 IBL 当前就绪（`envMode==='source_ibl'`）⇒ 未就绪保持 0；
             · `uIrrLod` 默认 **5.0**（= 源 LOD 公式在 roughness=1 时的取值，属**重建参数**，非源值）；
             · `uIrrScale` 默认 **1.0**（不引入任何未标注缩放，可经 `__iblIrrSrc(on,{scale})` 显式改）。 */
          const uIrrOn={value:((state.__iblIrrSrcOn===true&&iblReadyNow)?1.0:0.0)};
          const uIrrLod={value:((state.__iblIrrLod===undefined)?5.0:Number(state.__iblIrrLod))};
          const uIrrScale={value:((state.__iblIrrScale===undefined)?1.0:Number(state.__iblIrrScale))};
          sh.uniforms.uIrrOn=uIrrOn; sh.uniforms.uIrrLod=uIrrLod; sh.uniforms.uIrrScale=uIrrScale;
          /* ★★★ 新增（2026-09-21，GI2）：**④ 源 `q_diffW`（GI / lightmap 间接光项）** —— 六只 uniform。
             源（已定证，直接采信）：`d11_deferred_quality2_shader_pbr_weapon…cf349fa7…blob1.asm`
               L387 `min r9, r5, l(1.5)`                     → 立即数 **1.5**（source_immediate）
               L388 `mov_sat r1.w, cb1[86].z`                → `u_lightmap_factor` @1384
               L389 `mad r9, r9, l(0.299805…), -r5`          → 立即数 **0.299805**（source_immediate）
               L390 `mad r5, r1.w, r9, r5`                   → lerp(x, min(x,1.5)*0.299805, sat(lmf))
               L391 `mul r5, r5, cb1[239].xxxx`              → `u_env_day2night_exposure` @3824
               L392 `mul r5, r5, r7`
               L396/397 `dp3(luma)` → `× cb0[4].y`(`u_cube_brightness` @68) → `× l(2.761966)`（立即数）
                        → 与 lightmap 项 lerp ⇒ **q_diffW**
             值可得性：`u_cube_brightness` / `u_lightmap_factor` / `u_env_day2night_exposure`
               三只均为**运行时逐帧 cbuffer**（RDEF 位置已知 @68/@1384/@3824）⇒ 材质级**值不可读**，
               本皮肤 manifest 亦无声明 ⇒ 定性 `source_present_value_unreadable`。
               ⇒ **默认中性 1.0 / 0.0 / 1.0**（不引入任何比例因子），**不得**把 unreadable 的值当源值落默认。
             值域与可调档（逐档扫描用，全部经 `__gi2Gate`）：
               `uGi2Br`    = u_cube_brightness     默认 1.0
               `uGi2Lmf`   = sat(u_lightmap_factor) 默认 0.0
               `uGi2Exp`   = u_env_day2night_exposure 默认 1.0
               `uGi2Scale` = **诊断扫描增益**（非源值，标 diagnostic_scan）默认 1.0
               `uGi2Lod`   = 重建采样 mip（**重建参数**，非源值）默认 5.0
               `uGi2On`    = 总闸；**默认 0（关闭）** ⇒ 片元里整段不执行 ⇒ 默认帧与接线前逐字节相同。
             作用域：**只进间接漫反射（`iblIrradiance`）**；不碰 `direct_light` / `lighting_approx` /
               exposure / toneMapping / bloom / 任何灯强度。 */
          const uGi2On={value:((state.__gi2On===true)?1.0:0.0)};
          const uGi2Br={value:(Number.isFinite(Number(state.__gi2Br))?Number(state.__gi2Br):1.0)};
          const uGi2Lmf={value:(Number.isFinite(Number(state.__gi2Lmf))?Number(state.__gi2Lmf):0.0)};
          const uGi2Exp={value:(Number.isFinite(Number(state.__gi2Exp))?Number(state.__gi2Exp):1.0)};
          const uGi2Scale={value:(Number.isFinite(Number(state.__gi2Scale))?Number(state.__gi2Scale):1.0)};
          const uGi2Lod={value:(Number.isFinite(Number(state.__gi2Lod))?Number(state.__gi2Lod):5.0)};
          sh.uniforms.uGi2On=uGi2On; sh.uniforms.uGi2Br=uGi2Br; sh.uniforms.uGi2Lmf=uGi2Lmf;
          sh.uniforms.uGi2Exp=uGi2Exp; sh.uniforms.uGi2Scale=uGi2Scale; sh.uniforms.uGi2Lod=uGi2Lod;
          try{ m.userData.__gi2={prim:(pr&&pr.prim), on:(uGi2On.value>0.5),
                cube_brightness:uGi2Br.value, lightmap_factor:uGi2Lmf.value,
                day2night_exposure:uGi2Exp.value, scan_scale:uGi2Scale.value, lod:uGi2Lod.value,
                source_immediate:[2.761966,0.299805,1.5],
                value_level:'source_present_value_unreadable',
                channel:'indirect_diffuse(iblIrradiance)',
                basis:'asm cf349fa7 blob1 L387-392 + L396-397（q_diffW）；三 uniform 为运行时逐帧 cbuffer ⇒ 默认中性 1.0/0.0/1.0'}; }catch(e){}
          try{ m.userData.__iblIrrSrc={prim:(pr&&pr.prim), on:(uIrrOn.value>0.5), lod:uIrrLod.value, scale:uIrrScale.value,
                ibl:(iblName||null), ibl_ready_at_build:iblReadyNow, approx:true,
                approx_basis:'源 cube（uCustomIbl='+(iblName||'null')+'，来自 manifest t_custom_ibl 六面）重建的环境辐照；'+
                             '源侧为 u_env_sh(cb1[148..154])+u_ambient×u_char_ambient(cb1[0]/[284])+t_realtime_env_spec(t8) 加权累加 —— 运行时 cbuffer ⇒ 接不上'}; }catch(e){}
          try{ m.userData.__brdfSrc={prim:(pr&&pr.prim), base_metal:bmVal, crystal_metal:cmVal,
                base_specular:suBrdf('u_base_specular'), crystal_specular:suBrdf('u_crystal_specular'),
                value_source:'source_uniforms', wireable:brdfWireable,
                conflict:(cmVal!==null && cpCm!==undefined && cpCm!==null && Number(cpCm)!==Number(cmVal)),
                crystal_params_value:(cpCm===undefined?null:cpCm),
                ibl_ready_at_build:iblReadyNow, on:(uBrdfOn.value>0.5), ibl:(iblName||null)}; }catch(e){}
          sh.fragmentShader='uniform samplerCube uCustomIbl;\n'
            +'uniform float uIblRot;\nuniform float uIblMix;\nuniform float uIblScale;\n'
            /* ★ 新增（2026-09-19，task-45 第 1 项）：材质级环境辐照增益（源 `u_cube_brightness`）。
               `uCubeBrightOn` = 是否启用（0/1，默认 0 ⇒ 分支不生效）；`uCubeBright` = manifest 逐 prim 值。
               缺失 prim 的值恒为 1.0 且 On=0 ⇒ 与接线前逐字节相同的输出。 */
            +'uniform float uCubeBrightOn;\nuniform float uCubeBright;\n'
            /* ★★★ 新增（2026-09-21，GI2）：④ GI/lightmap 间接光项（源 q_diffW）的声明。
               `uGi2On` 默认 0 ⇒ 片元里 `q_gi2Irr` 立即 `return vec3(0.0)` ⇒ 逐像素零贡献。 */
            +'uniform float uGi2On;\nuniform float uGi2Br;\nuniform float uGi2Lmf;\n'
            +'uniform float uGi2Exp;\nuniform float uGi2Scale;\nuniform float uGi2Lod;\n'
            /* ★★ 新增（2026-09-19，shader-auditor，task-47）：晶体源 BRDF（metalness 插值）—— 此处只加**声明与安全默认**。
               · `q_metal / q_diffW` 为**全局变量**，默认 `0.0 / 1.0`（= 不金属化）；
               · 真正的赋值在晶体链注入 `injC` 末尾（且**仅当本 IBL 块已生效时**才追加）⇒
                 未接线 / 未就绪 / 开关关 / 链注入被跳过 的四种情形都与接线前**逐像素相同**，且**永远可编译**。 */
            +'uniform float uBrdfOn;\nuniform float uBaseMetal;\nuniform float uCrystalMetal;\n'
            +'float q_metal = 0.0;\nfloat q_diffW = 1.0;\n'
            /* ★★ 新增（2026-09-19，shader-auditor，task-59 (c)）：**源 cube 重建的环境辐照**（reconstruction approximation）。
               `uIrrOn` = 开关（默认 0）；`uIrrLod` = 重建用的 cube mip（默认 5.0，**与源 LOD 公式在 roughness=1 时的取值一致**，
               是重建参数、不是源值）；`uIrrScale` = 显式增益（默认 1.0，不引入任何未标注缩放）。
               **标签**：这是**近似**——源侧环境辐照来自 `u_env_sh`(cb1[148..154]) + `u_ambient×u_char_ambient`(cb1[0]/[284])
               + `t_realtime_env_spec`(t8) 的加权累加，全是**运行时 cbuffer ⇒ 接不上**；我们用**已在用的源 cube**
               （`uCustomIbl`，逐 prim 来自 manifest `t_custom_ibl` 的六面）重建它。 */
            +'uniform float uIrrOn;\nuniform float uIrrLod;\nuniform float uIrrScale;\n'
            +'/* ① 给 Three 原 getIBLRadiance 改名，腾出函数名 */\n'
            +'#define getIBLRadiance getIBLRadiance_three\n'
            +sh.fragmentShader;
          /* ② 在 main() 之前 #undef 并重建：**只产出 radiance** */
          var iblFn =
            '#undef getIBLRadiance\n'+
            'vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {\n'+
            '  float q_rough = max( roughness, 0.0019 );\n'+
            '  float q_lod   = 5.0 + 1.2 * log2( q_rough );                  /* asm 537-539 */\n'+
            '  vec3  q_R     = reflect( -viewDir, normal );                  /* 源反射方向 */\n'+
            '  q_R           = normalize( mix( q_R, normal, roughness * roughness ) );\n'+
            '  q_R           = inverseTransformDirection( q_R, viewMatrix );\n'+
            '  float q_c = cos( uIblRot ), q_s2 = sin( uIblRot );            /* asm 531 sincos cb0[7].w */\n'+
            '  /* P1 修复（2026-09-17，T2）：原先 sin/cos 次序互换，导致 iblRot=0 时环境被额外偏航 -90°。\n'+
            '     源 asm 的 sincos 首个目标是 sin、次个是 cos（与先前假设相反），故：\n'+
            '       x = cos*Rx + sin*Rz ;  z = -sin*Rx + cos*Rz   （rot=0 时为单位变换） */\n'+
            '  vec3  q_Rr = vec3( q_R.x*q_c + q_R.z*q_s2, q_R.y, -q_R.x*q_s2 + q_R.z*q_c );  /* asm 535-536 */\n'+
            '  vec4  q_sm = textureLod( uCustomIbl, q_Rr, q_lod );           /* asm 541 sample_l */\n'+
            '  vec3  q_L  = pow( q_sm.rgb * q_sm.a * 16.0, vec3(2.0) );      /* asm 542-544 RGBM 解码 */\n'+
            '  vec3  q_Lc = min( q_L, vec3(1.5) );                           /* asm 545 */\n'+
            '  vec3  q_env= q_L + uIblMix * ( q_Lc * 0.299805 - q_L );      /* asm 546-548 */\n'+
            '  q_env *= uIblScale;                                           /* asm 549 cb1[239].x 曝光 */\n'+
            /* ★ 新增（2026-09-19，task-45 第 1 项）：源 `u_cube_brightness`（003996.c159 f32，entry@2438/3257）。
               ⚠ 诚实标注：源 ASM 里这是**绑定在 cube 上的逐材质增益**，本处接在 radiance 出口，
               效果 = 与源同位置同形式（乘在环境辐照上），但**未**逐条比对源语句位置；
               仅 1110177 有值（1=0.71 / 2=2.74），**1110171 五个晶体 prim 无声明 ⇒ 不接线**。
               分支默认关（uniform=0）⇒ 默认渲染与接线前逐字节相同；`__cubeBright(true)` 才生效。 */
            '  if( uCubeBrightOn > 0.5 ){ q_env *= uCubeBright; }           /* asm 2438/3257 u_cube_brightness */\n'+
            '  return q_env;   /* ← 只交 radiance；F0 / Fresnel / BRDF / toneMapping 均由 Three 负责 */\n'+
            '}\n'+
            /* ═══ 新增（2026-09-19，shader-auditor，task-59 (c)）：**环境辐照（irradiance）的源 cube 重建** ═══
               为什么必须改**调用点**而不是只改函数：three r180 的 `lights_fragment_maps` 里
                 `#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )`
                   `iblIrradiance += getIBLIrradiance( geometryNormal );`  `#endif`
               而我们的材质 `m.envMap` 是**普通 CubeTexture**（非 PMREM）⇒ `ENVMAP_TYPE_CUBE_UV` **未定义**
               ⇒ 该调用点被整段编译掉（这正是"本链从未触碰 irradiance"的机制），
               所以改 `scene.environment` / `envMapIntensity` 门闸对这条路径**无效**；必须把调用点换成我们自己的函数
               （见下方 `patch('lights_fragment_maps', …)`）。
               取值：与 radiance 同一源 cube、同一旋转与 RGBM 解码，但用**固定高 mip**（`uIrrLod`）近似半球积分；
               返回 `π·L`（three 的约定：`irradiance = π·envColor`，随后 `RE_IndirectDiffuse` 再乘 `diffuseColor/π`）。
               `uIrrOn=0` ⇒ 返回 0 ⇒ 与接线前逐字节相同（调用点只多一个恒零项）。 */
            'vec3 q_iblIrrSrc( const in vec3 normal ) {\n'+
            '  vec3 q_In = inverseTransformDirection( normal, viewMatrix );\n'+
            '  float q_ic = cos( uIblRot ), q_is2 = sin( uIblRot );\n'+
            '  vec3 q_Inr = vec3( q_In.x*q_ic + q_In.z*q_is2, q_In.y, -q_In.x*q_is2 + q_In.z*q_ic );\n'+
            '  vec4 q_ism = textureLod( uCustomIbl, q_Inr, uIrrLod );\n'+
            '  vec3 q_iL  = pow( q_ism.rgb * q_ism.a * 16.0, vec3(2.0) );   /* RGBM 解码（同 radiance asm 542-544）*/\n'+
            '  vec3 q_iLc = min( q_iL, vec3(1.5) );                          /* asm 545 */\n'+
            '  vec3 q_iE  = q_iL + uIblMix * ( q_iLc * 0.299805 - q_iL );   /* asm 546-548 */\n'+
            '  q_iE *= uIblScale;                                            /* asm 549（与 radiance 同一曝光参数）*/\n'+
            '  if( uCubeBrightOn > 0.5 ){ q_iE *= uCubeBright; }             /* 逐 prim u_cube_brightness（有值时）*/\n'+
            '  q_iE *= ( uIrrOn * uIrrScale );                              /* 开关 × 显式重建增益（默认关、1.0）*/\n'+
            '  return 3.14159265 * q_iE;\n'+
            '}\n'+
            /* ═══ 新增（2026-09-21，GI2）：**④ 源 `q_diffW`（GI / lightmap 间接光项）** ═══
               源：`d11_deferred_quality2_shader_pbr_weapon…cf349fa7…blob1.asm` L387-392 + L396-397。
               为什么必须**单独**接：①②③（L545-549 / L2438 u_cube_brightness）都作用在 **radiance（间接镜面）**
                 出口上，而本段是**源侧的另一条链**（`q_diffW` = 间接漫反射的权重/辐照项）——
                 此前我们**完全缺失**（`q_diffW` 全局变量在晶体链里只有 `1.0-q_metal`，与源式无关）。
               语义（如实标注）：源把这条链的结果 `q_diffW` 用于**间接漫反射**；本处把它作为**加性间接辐照**接在
                 `iblIrradiance` 上（three 约定 `irradiance = π·L`，随后 `RE_IndirectDiffuse` 乘 `BRDF_Lambert`）。
               ⚠ 结构性限制（写进报告，不掩盖）：three 的间接漫反射最终乘 `material.diffuseColor`，
                 而 `diffuseColor = albedo·(1−metalnessFactor)`；对 **metalnessFactor=1** 的纹素该因子恒 **0**
                 ⇒ **本项对金属纹素的贡献按构造 = 0**，它只能抬升介电/漫反射区。
                 金属镜面区的亮度只可能来自 **radiance 通道**（即 ①②③ + cube 本身），由 B 组（换 cube）检验。
               立即数 `2.761966` / `0.299805` / `1.5` 按源直用（`source_immediate`）；
                 三个 uniform 默认中性 1.0 / 0.0 / 1.0（`source_present_value_unreadable`）。
               **默认 `uGi2On=0` ⇒ 立即返回 vec3(0.0)** ⇒ 与接线前逐字节相同。 */
            'vec3 q_gi2Irr( const in vec3 normal ) {\n'+
            '  if( uGi2On <= 0.5 ){ return vec3( 0.0 ); }             /* 默认关：零贡献 */\n'+
            '  vec3  q_gIn = inverseTransformDirection( normal, viewMatrix );\n'+
            '  float q_gc  = cos( uIblRot ), q_gs = sin( uIblRot );\n'+
            '  vec3  q_gR  = vec3( q_gIn.x*q_gc + q_gIn.z*q_gs, q_gIn.y, -q_gIn.x*q_gs + q_gIn.z*q_gc );\n'+
            '  vec4  q_gS  = textureLod( uCustomIbl, q_gR, uGi2Lod );  /* 重建采样（uGi2Lod 非源值） */\n'+
            '  vec3  q_gL  = pow( q_gS.rgb * q_gS.a * 16.0, vec3(2.0) );  /* RGBM 解码（同 asm 542-544） */\n'+
            '  vec3  q_gCc = min( q_gL, vec3(1.5) );                   /* asm 387 min(x,1.5) */\n'+
            '  vec3  q_gMd = q_gCc * 0.299805 - q_gL;                 /* asm 389（立即数 0.299805） */\n'+
            '  vec3  q_gLr = q_gL + clamp( uGi2Lmf, 0.0, 1.0 ) * q_gMd;  /* asm 388 sat(lmf) + asm 390 lerp */\n'+
            '  q_gLr *= uGi2Exp;                                      /* asm 391 u_env_day2night_exposure */\n'+
            '  float q_gLu = dot( q_gLr, vec3(0.2126,0.7152,0.0722) );/* asm 396 dp3 luma */\n'+
            '  q_gLu *= uGi2Br;                                       /* asm 397 cb0[4].y u_cube_brightness */\n'+
            '  q_gLu *= 2.761966;                                     /* asm 397 立即数（source_immediate） */\n'+
            '  q_gLu *= uGi2Scale;                                    /* 诊断扫描增益（非源值） */\n'+
            '  return 3.14159265 * q_gLu * q_gLr;\n'+
            '}\n';
          sh.fragmentShader=sh.fragmentShader.replace('void main() {', iblFn+'void main() {');
          /* ★★ 重做（2026-09-18，用户令 + 外审定因）：此前两处 `sh.fragmentShader.replace(...)` 
             **是静默 no-op** —— 目标语句不在 `ShaderLib.standard.fragmentShader` 顶层（实测 0 次匹配），
             而是各自位于 `lights_physical_fragment` / `lights_physical_pars_fragment` **chunk 内**；
             且 `onBeforeCompile` 在 `#include` 展开**之前**执行 ⇒ 直接替换正文必然无效。
             正确做法：从 `THREE.ShaderChunk` 取**字符串副本**改副本，再用改后的副本替换当前材质源码里的
             对应 `#include`。**不改全局 ShaderChunk**（避免污染其他材质）。
             **每一处都校验命中数**：chunk 内须恰好 1 次、材质内 include 须恰好 1 次；
             零次或多次直接记错误并抛出，**绝不静默继续**。 */
          m.userData.__patchLog=[];
          (function(){
            var T3=state.THREE;
            function patch(name, find, repl, tag){
              var chunk=T3.ShaderChunk[name];
              if(!chunk){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'ShaderChunk 无此 chunk'}); throw new Error('[patch] no chunk '+name); }
              var c=chunk.split(find).length-1;
              if(c!==1){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'chunk 内命中 '+c+' 次(须 1)'}); throw new Error('[patch] '+name+' hit '+c); }
              var mod=chunk.replace(find, repl);
              var inc='#include <'+name+'>';
              var ic=sh.fragmentShader.split(inc).length-1;
              if(ic!==1){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'材质内 '+inc+' 命中 '+ic+' 次(须 1)'}); throw new Error('[patch] include hit '+ic); }
              sh.fragmentShader=sh.fragmentShader.replace(inc, mod);
              m.userData.__patchLog.push({chunk:name,tag:tag,ok:true,chunkHits:c,includeHits:ic});
              return true;
            }
            /* ★★ 新增（2026-09-19，shader-auditor，task-47）：**同一 chunk 多次替换、只重插一次**。
               为什么必须新增：`patch()` 每次都要在材质里找到 `#include <name>`（命中=1），
               而第一次 patch 已把该 include 换成了改后的 chunk 正文 ⇒ 第二次必然命中 0 次而抛错。
               task-47 需要在 `lights_physical_fragment` 里同时改两行（diffuse 权重 + specularColor），
               故先对 **chunk 副本**逐个替换（**每串命中必须=1**），再一次性替换材质里的 include（命中必须=1）。
               **原 `patch()` 保留不动**（既有链路零影响）。 */
            function patchMulti(name, list, tag){
              var chunk=T3.ShaderChunk[name];
              if(!chunk){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'ShaderChunk 无此 chunk'}); throw new Error('[patchMulti] no chunk '+name); }
              var mod=chunk, hits=[];
              for(var i=0;i<list.length;i++){
                var find=list[i][0], repl=list[i][1];
                var c=mod.split(find).length-1;
                if(c!==1){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'第'+(i+1)+'串 chunk 内命中 '+c+' 次(须 1)'}); throw new Error('[patchMulti] '+name+' #'+(i+1)+' hit '+c); }
                mod=mod.replace(find, repl); hits.push(c);
              }
              var inc='#include <'+name+'>';
              var ic=sh.fragmentShader.split(inc).length-1;
              if(ic!==1){ m.userData.__patchLog.push({chunk:name,tag:tag,ok:false,why:'材质内 '+inc+' 命中 '+ic+' 次(须 1)'}); throw new Error('[patchMulti] include hit '+ic); }
              sh.fragmentShader=sh.fragmentShader.replace(inc, mod);
              m.userData.__patchLog.push({chunk:name,tag:tag,ok:true,chunkHits:hits.join('+'),includeHits:ic,strs:list.length});
              return true;
            }
            /* ★ 材质族条件（2026-09-18，审查助手令）：
               这两个 chunk patch 是 **weapon 专属**，此前写在共同分支里、晶体包装器又调 prevOBC(sh)，
               导致 weapon 补丁被套给晶体。现以 **isWeapon** 判定（该变量源于 manifest 的
               pr.shader_kind === 'weapon'，见本文件上方常量区，**不按 prim 序号硬编码**）。
               **本条件只包住这两个 patch，不包住上面的 IBL 资源绑定** —— 晶体已验证的源 cube 通路必须保留。
               开关：`?weaponPatch=0` 关闭。**在材质创建与首次编译之前确定**（直接读 location.search），
               故冷启动即生效，不依赖任何运行时重编译。 */
            var _isWeaponFam = (isWeapon === true);
            var _patchOn = (new URLSearchParams(location.search).get('weaponPatch') !== '0');
            m.userData.__family = _isWeaponFam ? 'weapon' : 'crystal';
            m.userData.__patchOn = _patchOn;
            /* ★ 2026-09-18（lead 批准后补齐）：晶体族**同样启用**本补丁。
               依据（源级实测，全部为**源常数**，未新增/未拟合）：
                 `pbr_crystal.nfx2_01393c07…_blob1_blob.asm`
                   · `l(0.079956)` @L501/L502                          → ① dielectricF0
                   · `mul_sat r8.w, r11.y, l(50.000000)` @L511          → ② saturate(q_F0.y*50.0)
                   · `l(-1.0,-0.027496,-0.571777,0.021988)` +
                     `l(1.0,0.042480,1.039062,-0.039978)` @L504         → ② q_c1..q_c4
               故原判据「晶体公式未核验 ⇒ skipped」的前提已不成立（源 spec 确有此三项）。
               开关与 weapon 族同一个：`?weaponPatch=0` 可关。 */
            m.userData.__patchEnabled = _patchOn;
            if(_patchOn){
              /* ① F0 介电常数：0.04 → 0.079956（源 asm L345-346）。
                 ⚠ 缺口如实保留：源 weapon 完整式是 F0 = metal*base + (1-metal)*0.079956*spec，
                   `spec`（= sat(lerp(ParamMap.A^4,1,sat(nv^2-0.3))*u_specular)）**尚未接齐** ⇒ 不称 F0 已源级复原。
                 ⚠ clearcoatF0 也是 vec3( 0.04 )，本匹配串只打 specularColor，**不误伤** clearcoat。
                 ★ 2026-09-19（task-47）：改用 `patchMulti` 并**按族分叉** ——
                   · **weapon 族：替换串与接线前逐字节相同**（保持 `metalnessFactor`，行为零变化）；
                   · **crystal 族：只用 `q_metal` 换掉 metalnessFactor，并把漫反射权重换成 `q_diffW`(=1−q_metal)**，
                     与源 `L547/L548`（diffuse=albedo×(1−metal)）与 `L550/L551`（F0=lerp(spec·0.079956, albedo, metal)）**一一对应**。
                     注意：three r180 **没有 `material.metalness` 字段**（全文 `metalnessFactor` 6 次、`material.metalness` 0 次）
                     ⇒ metalness 只经"漫反射权重 + specularColor"两条线影响着色，**只改这两行即与源等价**；
                     非 IOR 分支的 `material.specularF90 = 1.0` 与 metalness 无关，不动。
                   · `q_metal/q_diffW` 在注入头部已有**全局默认 0.0/1.0** ⇒ 即使晶体链注入被跳过也能编译且行为=现状。 */
              if(_isWeaponFam){
                patchMulti('lights_physical_fragment',
                      [['material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );',
                        'material.specularColor = mix( vec3( 0.079956 ), diffuseColor.rgb, metalnessFactor );']],
                      'dielectricF0_weapon');
              } else {
                patchMulti('lights_physical_fragment',
                      [['material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );',
                        'material.specularColor = mix( vec3( 0.079956 ), diffuseColor.rgb, q_metal );'],
                       ['material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );',
                        'material.diffuseColor = diffuseColor.rgb * q_diffW;']],
                      'crystalBRDF_qmetal');
              }
              /* ② 环境镜面权重：用源 r7.xyz 替换 Three 的 singleScattering。汇编 exp 以 2 为底 ⇒ exp2。
                 注：仅替换 singleScattering 这一行；Three 的 multiScattering 与间接漫反射**仍然保留**，
                 故**不得**据此宣布整个 NeoX BRDF 已恢复。 */
              patch('lights_physical_pars_fragment',
                    'reflectedLight.indirectSpecular += radiance * singleScattering;',
                    'vec3 q_F0 = material.specularColor;\n' +
                    'float q_rg = clamp( material.roughness, 0.019989, 1.0 );\n' +
                    'float q_ndv = saturate( dot( geometryNormal, geometryViewDir ) + 0.00001 );\n' +
                    'float q_c1 = 1.0 - q_rg;\n' +
                    'float q_c2 = 0.042480 - q_rg * 0.027496;\n' +
                    'float q_c3 = 1.039062 - q_rg * 0.571777;\n' +
                    'float q_c4 = q_rg * 0.021988 - 0.039978;\n' +
                    'float q_t0 = min( q_c1*q_c1, exp2( -9.28 * q_ndv ) );\n' +
                    'float q_t  = q_t0 * q_c1 + q_c2;\n' +
                    'float q_A  = -1.04 * q_t + q_c3;\n' +
                    'float q_B  =  1.04 * q_t + q_c4;\n' +
                    'vec3  q_envW = max( q_F0 * q_A + saturate( q_F0.y * 50.0 ) * q_B, vec3( 0.0 ) );\n' +
                    'reflectedLight.indirectSpecular += radiance * q_envW;',
                    'sourceEnvWeight');
              /* ③ ★ 新增（2026-09-19，shader-auditor，task-59 (c)）：**把环境辐照换成"源 cube 重建"**。
                 为什么改调用点：three r180 `lights_fragment_maps` 里这条调用被
                 `#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )` 门住；
                 而**实测证明该门在本链是成立的**（我第一版把整段换成"只调我们的函数"，OFF 时画面直接变黑 ⇒
                 说明原来的 `getIBLIrradiance(...)`（`scene.environment` 那套**中性 PMREM 棚**）**一直在贡献可观的漫反射**，
                 不是 0；这也**修正**了 task-59 诊断里"环境漫反射≈0"的推断）。
                 正解：**保留原调用，用 `mix(原值, 源 cube 重建值, uIrrOn)` 逐值切换** ——
                   · `uIrrOn=0` ⇒ `mix(a,b,0.0)` **恰好等于 a**（GLSL mix 恒等式）⇒ 默认态与接线前**逐值相同**；
                   · `uIrrOn=1` ⇒ **替换**（而不是叠加）中性 PMREM 棚的辐照，符合 lead"把 environment 换成源 cube"的口径，
                     且不双计能量。
                 外层 `#if defined( RE_IndirectDiffuse )` 与内层 CUBE_UV 门都**原样保留**。 */
              patch('lights_fragment_maps',
                    '#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )\n\t\tiblIrradiance += getIBLIrradiance( geometryNormal );\n\t#endif',
                    '#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )\n\t\tiblIrradiance += mix( getIBLIrradiance( geometryNormal ), q_iblIrrSrc( geometryNormal ), uIrrOn );\n\t\tiblIrradiance += q_gi2Irr( geometryNormal );\n\t#endif',
                    'irradianceSrcCube + gi2④(indirect_diffuse)');
              m.userData.__patchState = _isWeaponFam ? 'enabled_weapon_family' : 'enabled_crystal_family_source_verified';
            } else {
              m.userData.__patchLog.push({tag:'weaponPatchSkipped', family:(_isWeaponFam?'weapon':'crystal'),
                patchOn:_patchOn, ok:false,
                why:'weaponPatch=0（冷启动开关关闭）'});
              m.userData.__patchState = 'disabled_by_url_switch';
            }
          })();
          m.userData.__frag=sh.fragmentShader; m.userData.__sh=sh;
          m.userData.__iblRadianceOverride=true;
        };
        m.customProgramCacheKey=function(){ return 'srcIblRad_v5_'+(isWeapon?'weapon':'crystal')+'_wp'+((new URLSearchParams(location.search).get('weaponPatch')!=='0')?1:0)+'_'+iblName+'_'+primIdx; };
      }
      /* ══════════════════════════════════════════════════════════════════════════════════════
         ★★★ 新增（2026-09-20，ENVROUTE S2）：**pbr_weapon 的 `DetailMap` 槽真正绑进绘制程序**。

         源依据（槽位归属 = source_verified）：
           `neox_material.json.primitives[3].shader_declared_by_material_c159 = shader\pbr_weapon.fx::TShader`
           （M3=`skin_1006_003_3_mat`），声明串槽含 `DetailMap` 且块内唯一 common 贴图
           = `common\textures\detail_normal_snake_02_m.tga`
           （CRYSTAL_SRC_20260920 §3.4 / §7.3：`DetailMap ← detail_normal_snake_02_m`，依据「槽声明 + 路径名」）。

         缺口（**unresolved**，不折中成假公式）：
           `pbr_weapon` 对 `DetailMap` 的**采样点与复合指令（tilling/intensity/offset → 法线扰动）尚未定证**。
           本仓库已证的 detail 复合式（`xy→±1×u_detail_intensity / z=1+I(z−1) → ×m`）出自 **pbr_crystal**，
           且既有结论明确记录「其注入点必须在 `normal` 之后，与本链注入点结构冲突」
           （见下方 `__layer('detail')` 的 `LAYER_REASON.detail`）⇒ **禁止把它当成 weapon 的源式**。

         因此本处**只做真实绑定，不做颜色运算**：
           · `uWpnDetailMap` = 源声明文件（manifest `textures.DetailMap.local_file`，sha256 逐条核过）；
           · `uWpnDetailOn`  **默认 0** ⇒ 片元里那段采样**逐像素零贡献** ⇒ 默认态与接线前**逐像素相同**；
           · 闸门是 **uniform**（不是 `#if` 常量）⇒ GLSL 编译器**不能**把该 sampler 死代码消除
             ⇒ 它必然进入 linked program 的**活跃 uniform 表**（由 `__envrouteTexProbe()` 在 GPU 侧读回）；
           · `__wpDetailPreview(true)` 打开时输出 `texture2D(uWpnDetailMap, vMapUv).rgb`
             —— 这是**逐像素消费证明**（诊断预览，非源行为，报告里标注 diagnostic）。
         ⚠ 只对 **weapon 族**且 manifest **确实声明了该槽并给出 file** 的 prim 生效；
           没有该槽的 prim 一条指令都不加（键存在性是唯一判据，不按 prim 序号硬编码，也不跨 prim 借图）。
         ══════════════════════════════════════════════════════════════════════════════════════ */
      if(isWeapon && pr.textures && Object.prototype.hasOwnProperty.call(pr.textures,'DetailMap')){
        const wpDetailMeta=pr.textures.DetailMap||{};
        const wpDetailFile=(g.DetailMap&&g.DetailMap.file)||null;
        const uWpnDetailMap={value:(wpDetailFile?tex(wpDetailFile,false):null)};
        const uWpnDetailOn={value:0.0};
        const prevOBCW=m.onBeforeCompile, prevKeyW=m.customProgramCacheKey;
        m.onBeforeCompile=function(sh){
          if(typeof prevOBCW==='function') prevOBCW(sh);
          sh.uniforms.uWpnDetailMap=uWpnDetailMap;
          sh.uniforms.uWpnDetailOn=uWpnDetailOn;
          sh.fragmentShader='uniform sampler2D uWpnDetailMap;\nuniform float uWpnDetailOn;\n'+sh.fragmentShader;
          var AW='#include <map_fragment>';
          if(sh.fragmentShader.indexOf(AW)>=0){
            sh.fragmentShader=sh.fragmentShader.replace(AW,
              AW+'\n  /* ENVROUTE S2：pbr_weapon DetailMap 绑定（源公式 unresolved ⇒ 默认闸 0，诊断预览时才直显） */\n'
                +'  #if defined( USE_MAP )\n'
                +'  if(uWpnDetailOn > 0.5){ diffuseColor.rgb = texture2D(uWpnDetailMap, vMapUv).rgb; }\n'
                +'  #endif\n');
            m.userData.__patchLog.push({chunk:'map_fragment',tag:'envrouteWpDetailMap',ok:true,chunkHits:1,includeHits:1});
          }else{
            m.userData.__patchLog.push({chunk:'map_fragment',tag:'envrouteWpDetailMap',ok:false,why:'anchor <map_fragment> 未命中(1)'});
            (window.__glowErrors=window.__glowErrors||[]).push({where:'envrouteWpDetailMap',why:'anchor <map_fragment> 未命中(1) ⇒ DetailMap 未注入'});
          }
          m.userData.__fragWpDetail=sh.fragmentShader;
        };
        m.customProgramCacheKey=function(){ try{
          return 'envrouteWpDetail_'+primIdx+'_'+((typeof prevKeyW==='function')?prevKeyW.call(m):'');
        }catch(e){ return 'envrouteWpDetail_'+primIdx+'_err'; } };
        state.__envrouteWpDetail=(state.__envrouteWpDetail||[]);
        state.__envrouteWpDetail.push({
          prim:primIdx, material:pr.material, file:wpDetailFile,
          logical:(wpDetailMeta.logical_path||null), sha256:(wpDetailMeta.sha256||null),
          evidence_level:(wpDetailMeta.evidence_level||null),
          u:uWpnDetailMap, on:uWpnDetailOn, texObj:uWpnDetailMap.value,
          consumed_by:'uniform `uWpnDetailMap`（pbr_weapon 片元程序内声明 + 在 <map_fragment> 之后采样）；闸门 `uWpnDetailOn`',
          slot_evidence:'source_verified（M3 声明串槽含 DetailMap，块内唯一 common 贴图 = detail_normal_snake_02_m）',
          formula_evidence:'unresolved（pbr_weapon 的 DetailMap 采样/复合指令未定证 ⇒ 不发明 math）'});
      }
      /* ★ 新增（2026-09-16）：晶体源公式注入。
         此前主链的晶体只是 MeshStandardMaterial({map:t_basecolor})，真正的三次 lerp 公式
         只存在于 ?neoxView=C_base 诊断 shader 里，而那个 shader 把 prim5 的常量
         （uCrystalColor:[0,0.2118,0.8] / uBaseColor:[0.1098,0.3961,0.502]）套用到全部晶体，
         与「各材质用自己的 c159 块」相悖。
         现按 manifest 的 per-prim crystal_params 注入（源自 _known_loop/c159_params_001265.json，
         与外审报告 §3.4 同源、逐 prim 各自的值）：
             q_mm = clamp(Tex0.r, 0, 1)
             A    = mix(T, T * u_crystal_color, q_mm)
             B    = mix(u_base_color, T * u_crystal_color, q_mm)   // d = q_mm，DetailMap 缺失时的降级分支
             C    = mix(A, B, q_mm)
         注入点 <map_fragment> 之后 —— 此时 diffuseColor.rgb 已等于 map(t_basecolor) 的采样值 T.rgb。
         标识符一律 q_ 前缀（GLSL ES 3.00 保留含连续双下划线的标识符，见同日着色器事故）。
         链式调用上一个 onBeforeCompile，避免覆盖上面刚设好的 IBL 注入。 */
      if(!isWeapon){
        const cp=(pr.crystal_params||null);
        const v3=function(a,d){ return (Array.isArray(a)&&a.length>=3)?[+a[0],+a[1],+a[2]]:d; };
        /* ★ 修正（2026-09-16）：该族是否真的带基础色贴图。
           prim6 属 forward_crystal_roughness_24da，manifest required_slots **无 t_basecolor** ——
           即源材质没有基础色贴图。此前用 Tex0(_b_m，暖金) 当 T，`T × u_crystal_color` 被暖色污染：
           T=[0.47,0.41,0.31] × uc=[0.0039,0,0.6745] ≈ [0.002,0,0.21] → C 退化成灰蓝 [0.23,0.27,0.32]，
           实测该 prim silver 79.2%（发白发闷）。既然该族无基础色贴图，T 应为无色的 vec3(1.0)，
           颜色全部来自 u_crystal_color / u_base_color。 */
        const hasBaseTex=!!(g.t_basecolor&&g.t_basecolor.file);
        const maskFile=(g.Tex0&&g.Tex0.file)||null;
        /* DetailMap 候选（内容匹配，未升级为直证）：仅当开启 state.__useDetail 时才实际参与 d 的计算 */
        /* ★★ 修复（2026-09-19，shader-auditor，task-62，lead 令）：**去掉 `src_tex/gpk_1229.png` 的无条件加载（404 源）**。
           事实：该文件是 **1110171 目录独有**（1576284 B），**两个皮肤的 `neox_material.json` 里 0 命中**
           ⇒ 它不是任何槽位的声明值，只是历史内容候选；此前**每个晶体 prim 无条件** `tex()` ⇒
           其余皮肤（含 **1110177 极光剑**）必然 404，且当 manifest 解析不到 DetailMap 时会**以它顶替该槽位**
           （违反"不顶替贴图"）。
           现改为**默认不加载**：只有显式 `__legacyDetail(true)` 才加载；未加载的路径由 `__texReady().legacy_tex_missing` 暴露。
           **默认态行为**：`uDetailMap = detailFile ? tex(detailFile) : null`（不再顶替）；`uHasDetail` 的判据**一字未改**；
           其它皮肤已绑定的槽位**一律不动**。 */
        const legacyDetailPath='src_tex/gpk_1229.png';
        const legacyDetailTex=(state.__useLegacyDetail===true)?tex(legacyDetailPath,false):null;
        if(maskFile){
          m.userData.__crystalBlock=[primIdx, !!cp, maskFile];   // 诊断：块是否进入 / 有无 crystal_params / 掩码文件
          const prevOBC=m.onBeforeCompile, prevKey=m.customProgramCacheKey;
          const uCrystalColor={value:v3(cp&&cp.u_crystal_color,[0,0.2118,0.8])};
          const uBaseColor={value:v3(cp&&cp.u_base_color,[0.1098,0.3961,0.502])};
          m.onBeforeCompile=function(sh){
            window.__crystalOBC=(window.__crystalOBC||0)+1;
            window.__crystalOBCInfo=(window.__crystalOBCInfo||[]); window.__crystalOBCInfo.push(primIdx);
            if(typeof prevOBC==='function') prevOBC(sh);
            sh.uniforms.uCrystalMask={value:tex(maskFile,false)};
            sh.uniforms.uCrystalColor=uCrystalColor;
            sh.uniforms.uBaseColor=uBaseColor;
            /* ★ 新增（2026-09-17）：DetailMap 接入（可选）。
               源公式 §3.5：d = m × DetailMap.a。此前 DetailMap 缺失 → 降级 d = m。
               现有内容匹配候选 src_tex/gpk_1229.png（candidate-high，alpha 有效），
               做成运行时开关以便与降级版**逐图对比**，不直接改默认口径。 */
            /* ★ 新增（2026-09-18，shader-auditor；lead 指示 ①②）：按 manifest 实接 3 个槽。
               · DetailMap        = src_tex/crystal_bump_n_uvva.png（源声明 5/5 prim；512² **RGB·无 alpha**）
                 ⇒ 源公式 d = m × DetailMap.a；无 alpha ⇒ a≡1 ⇒ d=m
                 ⇒ **接上后画面逐字节不变是预期，不是接错**（判据：uDetailBound=1 且 __matDump 非 null）
               · t_caustic_tex    = src_tex/crystal_caustic_uvva.png（prim1/2/3/5；256² RGBA 灰阶）
               · t_reflection_tex = src_tex/crystal_reflection_uvva.png（**仅 prim1/2/5**）
                 prim3/6 manifest `state:'absent'`＋reason「源未声明」⇒ 无 file ⇒ **不接**（按 lead 指示 ①）
               · t_refraction_tex = **保持 not_shipped**：整族未发布（2728 变体 × 221 容器 0 命中）
                 ⇒ **不接、不做替身**（lead 指示 ⑤）。
               ⚠ caustic/reflection 的**源参与公式尚未恢复** ⇒ 默认**不进入颜色运算**（零默认改动），
                 只提供 `WikiWeaponViewer.__layer('caustic'|'reflection'|null)` 图层预览做绑定 A/B
                 （受光照·诊断用·非源值），**绝不用猜的 math 冒充源结果**。 */
            const detailFile=(g.DetailMap&&g.DetailMap.file)||null;
            const causticFile=(g.t_caustic_tex&&g.t_caustic_tex.file)||null;
            const reflFile=(g.t_reflection_tex&&g.t_reflection_tex.file)||null;
            const refrFile=(g.t_refraction_tex&&g.t_refraction_tex.file)||null;
            /* ★★ 新增（2026-09-19，shader-auditor，task-44）：三层公式体的**源值**（逐 prim，零硬编）。
               读 manifest `pr.source_uniforms`（1110171=1E091B35F713A1A4 / 1110177=DE07399720411145）；
               缺项/`absent_in_c159`/null ⇒ 该层不可用 ⇒ 开关强制关闭（不猜、不填默认几何值）。 */
            const SVF=function(k){ var e=(pr.source_uniforms||{})[k]; if(e===null||e===undefined) return null;
              var v=(typeof e==='object'&&('value' in e))?e.value:e; return (v===null||v===undefined)?null:v; };
            const svF=function(k){ var v=SVF(k); var n=Number(v); return Number.isFinite(n)?n:null; };
            const cauT=svF('u_caustic_tilling'), cauD=svF('u_caustic_depth'), cauB=svF('u_caustic_brightness');
            const refrRot=svF('u_refraction_rotation'), refrCon=svF('u_refraction_contrast'),
                  refrBri=svF('u_refraction_brightness');
            const refrCol=(function(){ var v=SVF('u_refraction_color');
              return (Array.isArray(v)&&v.length>=3)?[+v[0],+v[1],+v[2]]:null; })();
            /* ★★ 修复（2026-09-19，shader-auditor，task-44，lead 裁决 1）：**层级就绪门**（复用 task-40 判据）。
               原判定只看 manifest 路径 ⇒ 贴图请求失败时仍把 `uCausticTex`/`uRefrTex` 绑成**未加载纹理**：
               caustic 因 `× .a` 碰巧无害，但 **refraction 在 `u_refraction_contrast = -1`** 下会把"空采样=黑(0)"
               经 `clamp(x*(2c+1) − c)` remap 成 **1.0（纯白）** 再 mix 进基色 ⇒ **越缺越亮**（实测负控 3.325 vs 基线 2.841）。
               现：贴图必须 `image.complete && naturalWidth>0` **且**值齐备才 ready；未就绪 ⇒ uniform 恒 0 ⇒ 整段 GLSL
               不执行 ⇒ **任何情况下都不会把"贴图缺失"放大成亮色**（不依赖 `.a=0` 这类巧合）。
               贴图加载完成后挂一次性 load 监听请求**重绑**（复用 task-40 一次性重绑）使门自动放行。 */
            const cauTexObj=causticFile?tex(causticFile,false):null;
            const refrTexObj=refrFile?tex(refrFile,false):null;
            const imgReady=function(t){ try{ var im=t&&t.image; if(!im) return false;
              if(im.complete===undefined&&im.naturalWidth===undefined) return true;   /* 非 HTMLImage（已解码数据）视为就绪 */
              return !!(im.complete&&im.naturalWidth>0); }catch(e){ return false; } };
            try{ [cauTexObj,refrTexObj].forEach(function(tx){ var im=tx&&tx.image;
              if(im&&im.addEventListener&&!im.__layerHooked){ im.__layerHooked=true;
                im.addEventListener('load',function(){ state.__iblRebindPending=true; });
                im.addEventListener('error',function(){ state.__layerTexErr=(state.__layerTexErr||0)+1; }); } }); }catch(e){}
            const cauWhy=[]; if(!causticFile) cauWhy.push('manifest 无 t_caustic_tex');
              if(cauT===null||cauD===null||cauB===null) cauWhy.push('缺 u_caustic_* 值');
              if(causticFile&&!imgReady(cauTexObj)) cauWhy.push('贴图未就绪(complete/naturalWidth)');
            const refrWhy=[]; if(!refrFile) refrWhy.push('manifest 无 t_refraction_tex');
              if(refrRot===null||refrCon===null||refrBri===null||refrCol===null) refrWhy.push('缺 u_refraction_* 值');
              if(refrFile&&!imgReady(refrTexObj)) refrWhy.push('贴图未就绪(complete/naturalWidth)');
            const cauReady=(cauWhy.length===0);
            const refrReady=(refrWhy.length===0);
            const uCausticTex={value:cauTexObj};
            const uReflTex={value:reflFile?tex(reflFile,false):null};
            const uRefrTex={value:refrTexObj};
            const uLayer={value:0.0};
            const uCauOn={value:0.0}, uRefrOn={value:0.0};
            const uCauParams={value:new state.THREE.Vector3(cauT===null?0:cauT, cauD===null?0:cauD, cauB===null?0:cauB)};
            const uRefrParams={value:new state.THREE.Vector4(refrRot===null?0:refrRot, refrCon===null?0:refrCon,
                                                          refrBri===null?0:refrBri, 0)};
            const uRefrColor={value:new state.THREE.Vector3(refrCol?refrCol[0]:1, refrCol?refrCol[1]:1, refrCol?refrCol[2]:1)};
            sh.uniforms.uDetailMap={value:((detailFile?tex(detailFile,false):null)||legacyDetailTex)};
            sh.uniforms.uHasDetail={value:((detailFile||state.__useDetail) ? 1.0 : 0.0)};
            sh.uniforms.uCausticTex=uCausticTex; sh.uniforms.uReflTex=uReflTex; sh.uniforms.uLayer=uLayer;
            sh.uniforms.uRefrTex=uRefrTex;
            sh.uniforms.uCauOn=uCauOn; sh.uniforms.uCauParams=uCauParams;
            sh.uniforms.uRefrOn=uRefrOn; sh.uniforms.uRefrParams=uRefrParams; sh.uniforms.uRefrColor=uRefrColor;
            (function(){ state.__crystalLayer=(state.__crystalLayer||[]);
              state.__crystalLayer.push({prim:primIdx, uLayer:uLayer, hasCaustic:!!causticFile, hasRefl:!!reflFile,
                /* ★ 新增（2026-09-20，ENVROUTE S2）：`hasRefr` —— 供 `__layer('refraction')` 的
                   **逐像素消费证明**（诊断预览）与 `__crystalLayers` 的 `texture_bound` 如实读数使用。 */
                hasRefr:!!refrFile,
                uCauOn:uCauOn, uRefrOn:uRefrOn, cauReady:cauReady, refrReady:refrReady,
                cauValues:{u_caustic_tilling:cauT,u_caustic_depth:cauD,u_caustic_brightness:cauB},
                refrValues:{u_refraction_rotation:refrRot,u_refraction_contrast:refrCon,
                            u_refraction_brightness:refrBri,u_refraction_color:refrCol,
                            u_refraction_mipmap:null, u_refraction_opacity:null}});
              window.__crystalSlots=window.__crystalSlots||{};
              window.__crystalSlots[primIdx]={prim:primIdx,
                DetailMap:detailFile||null, t_caustic_tex:causticFile||null, t_reflection_tex:reflFile||null,
                t_refraction_tex:refrFile||null,
                t_reflection_tex_absent_by_source:!hasReflKey,
                uDetailBound:!!(detailFile||state.__useDetail), uCausticBound:!!causticFile,
                uReflBound:!!reflFile, uRefrBound:!!refrFile}; })();
            sh.fragmentShader='uniform sampler2D uCrystalMask;\nuniform vec3 uCrystalColor;\nuniform vec3 uBaseColor;\n'
              +'uniform sampler2D uDetailMap;\nuniform float uHasDetail;\n'
              +'uniform sampler2D uCausticTex;\nuniform sampler2D uReflTex;\nuniform float uLayer;\n'
              +'uniform sampler2D uRefrTex;\nuniform float uCauOn;\nuniform vec3 uCauParams;\n'
              +'uniform float uRefrOn;\nuniform vec4 uRefrParams;\nuniform vec3 uRefrColor;\n'+sh.fragmentShader;
            /* ★ 新增（2026-09-19，task-47）：本 IBL 块是否已装到本材质上。
               IBL 块（`if(iblCube && strictMode)`）里同时装了：uniform `uBrdfOn/uBaseMetal/uCrystalMetal`、
               头部全局 `q_metal/q_diffW` 默认值、以及 `lights_physical_fragment` 的两行补丁；
               三者**同生同灭** ⇒ 用 `prevOBC` 是否存在作唯一判据：不存在就**不追加**金属度赋值，
               避免"引用了未声明的全局变量"导致整帧着色器编译失败（fail-closed 纪律）。 */
            var brdfHeaderOn=(typeof prevOBC==='function');
            var injC=(hasBaseTex
                       ? '  vec3  q_T  = diffuseColor.rgb;\n'
                       : '  vec3  q_T  = vec3(1.0); /* 该族无 t_basecolor：无色，颜色全来自材质常量 */\n')+
                     '  float q_mm = clamp(texture2D(uCrystalMask, vMapUv).r, 0.0, 1.0);\n'+
                     '  float q_dd = (uHasDetail > 0.5) ? (clamp(texture2D(uDetailMap, vMapUv).a,0.0,1.0) * q_mm) : q_mm;\n'+
                     '  vec3  q_A  = mix(q_T, q_T * uCrystalColor, q_mm);\n'+
                     '  vec3  q_B  = mix(uBaseColor, q_T * uCrystalColor, q_dd);\n'+
                     '  diffuseColor.rgb = mix(q_A, q_B, q_mm);\n'+
                     /* ★ 新增（2026-09-18）：图层预览（诊断用·非源值）—— uLayer 1=caustic 2=reflection 0=材质本体（默认）。
                        只做「贴图确实绑上并按 vMapUv 采样」的 A/B 证据；源参与公式恢复前不参与颜色运算。 */
                     /* ★ 新增（2026-09-20，ENVROUTE S2）：`uLayer > 2.5` ⇒ **t_refraction_tex 的直显预览**。
                        为什么需要它：`uRefrOn`（源公式闸门）要求本 prim 自身的 `u_refraction_*` 值齐备，
                        而 M1 未序列化 rotation/brightness、M4 未序列化 color ⇒ **两个晶体 prim 的源公式闸门都开不了**。
                        若没有这条诊断分支，`refraction_envmap_1` 就只有"绑上了"而**无法**给出"被 GPU 逐像素消费"
                        的证据。本分支与既有 uLayer 预览同性质：**诊断用、非源行为**，默认 uLayer=0 不执行。 */
                     '  if(uLayer > 2.5){ diffuseColor.rgb = texture2D(uRefrTex, vMapUv).rgb; }\n'+
                     '  else if(uLayer > 1.5){ diffuseColor.rgb = texture2D(uReflTex, vMapUv).rgb; }\n'+
                     '  else if(uLayer > 0.5){ diffuseColor.rgb = texture2D(uCausticTex, vMapUv).rgb; }\n';
            /* ═══ 新增（2026-09-19，shader-auditor，task-47）：源 metalness 插值（asm L443-444）═══
               追加在 `injC` 之后（同一注入点、同一 main 作用域），只在 IBL 块已生效时追加（见 `brdfHeaderOn`）。
               `q_mm`（= saturate(Tex0.r)，源 L393 的 m）与 `q_dd`（= m·DetailMap.a，源 L405 的 r8.w）**本段上面已算好**
               ⇒ 源 `w`（L438 `w = m²·D.a`）就是 `q_mm × q_dd`：
                 · DetailMap 已绑定：`q_dd = D.a·m` ⇒ `q_mm*q_dd = m²·D.a`（**逐字等于源式**）；
                 · DetailMap 未绑定（`uHasDetail=0`）：`q_dd = q_mm` ⇒ `= m²`（`D.a≡1` 的已证退化式：
                   三份 DetailMap alpha 实测 min=max=255）——**两条路径在本资源下同值**，故 1110177 prim1 无需特判。
               `q_metal = mix(0.0, clamp(mix(uBaseMetal,uCrystalMetal,w),0,1), uBrdfOn)`：
                 · 开关 OFF / 该 prim 无源值 / IBL 未就绪 ⇒ `uBrdfOn=0` ⇒ `q_metal=0`、`q_diffW=1` = 接线前输出；
                 · `uBaseMetal` 缺失时其 uniform 已按"现值 0.0"预置（不借值、不跨 prim 取）；
                 · `spec` 因子本轮**不注入**（两目标皮肤 `u_crystal_specular≡1`、`u_base_specular` 仅 1110177 prim2 且=1
                   ⇒ `spec = lerp(1,1,w) ≡ 1`，既有 `0.079956` patch 已等价）。 */
            if(brdfHeaderOn){
              injC += '  /* task-47：源 metalness 插值（L443-444）；w = m²·D.a = q_mm×q_dd（L438 + L405） */\n'+
                      '  q_metal = mix(0.0, clamp(mix(uBaseMetal, uCrystalMetal, clamp(q_mm*q_dd, 0.0, 1.0)), 0.0, 1.0), uBrdfOn);\n'+
                      '  q_diffW = 1.0 - q_metal;\n';
            }
            /* ═══ 新增（2026-09-19，shader-auditor，task-44）：caustic + refraction **源公式体** ═══
               证据：RX_CRYSTAL_source_formulas_20260919.md（代表变体 cand\03e9e23d_b2d62c97_d11.pipe_blob1_blob.asm
               · PS · d11_deferred_quality2_shader_pbr_crystal；15/15 变体层绑定形态一致）
                 · caustic（t4，L461-466）：`r1.x = r6.x*cb0[321].x + cb0[321].x`（depth=**视差偏移幅度**）
                   → L462 视差方向 → `L463 r1.xy = v0.xy*cb0[320].w + r1.xy`（**tilling 乘 UV**）
                   → L464 sample → `L465 *= cb0[321].y`（**brightness 乘性**）
                   → `L466 mad …, r1.w, r9.xyz`（**以 caustic.a 加权加进基色**）
                 · refraction（t5，L471-527）：`r6.z = cb0[321].z*6.283185`（**rotation=角度×2π**）
                   → sincos + `L505-516` acos/atan2 近似 + `×(1/2π,1/π)+0.5`（**方向→球面 UV，非 UV 旋转**）
                   → `L517 sample_l …, cb0[322].x`（**u_refraction_mipmap 作 LOD**）
                   → `L521-523 mad_sat r6.z, r5.x, (2c+1), -c`（**contrast=线性 remap+saturate**）
                   → `L524 *= `（brightness 乘性）→ `L525 *= cb0[186].xyz`（**u_refraction_color 乘性**）→ L526-527 × 表面权重
               注入点选 `#include <normal_fragment_maps>`（**在 `<map_fragment>` 之后、`normal`/`vViewPosition` 已可用**）：
                 `<map_fragment>` 处还没有 `normal` 变量 ⇒ 若把球面 UV 放在那里就只能用假法线。
               **默认 OFF（uCauOn/uRefrOn=0）⇒ 本段整体不执行 ⇒ 与停手版逐字节一致。**
               ⚠ 两处如实标注的结构差异（不折中成假公式，见报告）：
                 ① 视差方向项 `r6.x`（L461/462）的具体寄存器语义未定证 ⇒ 此处用 **视差标准形**：以切线空间
                    视线方向的 xy 作偏移方向，幅度 = `u_caustic_depth`；
                 ② refraction 的"表面权重"（L526-527）未定证 ⇒ 用已有的 `q_mm`（= saturate(Tex0.r)）作权重。 */
            var injB='  if(uCauOn > 0.5){\n'+
              '    vec3  q_Vv = normalize(vViewPosition);\n'+
              '    vec2  q_par = normalize(vec2(q_Vv.x, -q_Vv.y) + vec2(1e-5));\n'+
              '    vec2  q_cuv = vMapUv * uCauParams.x + q_par * uCauParams.y;\n'+
              '    vec4  q_cs  = texture2D(uCausticTex, q_cuv);\n'+
              '    diffuseColor.rgb += q_cs.rgb * uCauParams.z * q_cs.a;   /* brightness 乘性 + 以 .a 加权加进基色 */\n'+
              '  }\n'+
              '  if(uRefrOn > 0.5){\n'+
              '    float q_ang = uRefrParams.x * 6.2831853;\n'+
              '    vec3  q_Nv  = normalize(normal);\n'+
              '    vec3  q_Vn  = normalize(vViewPosition);\n'+
              '    vec3  q_Rf  = reflect(-q_Vn, q_Nv);\n'+
              '    float q_phi = atan(q_Rf.z, q_Rf.x) + q_ang;            /* rotation = 角度×2π（加在方位角上） */\n'+
              '    float q_the = acos(clamp(q_Rf.y, -1.0, 1.0));\n'+
              '    vec2  q_ruv = vec2(q_phi * 0.15915494, q_the * 0.31830989) + 0.5;   /* 方向→球面 UV */\n'+
              '    vec3  q_rgb = textureLod(uRefrTex, q_ruv, 0.0).rgb;    /* LOD：u_refraction_mipmap 无材质级值 ⇒ 链默认 0.0 */\n'+
              '    q_rgb = clamp(q_rgb * (2.0 * uRefrParams.y + 1.0) - uRefrParams.y, 0.0, 1.0);   /* contrast remap+saturate */\n'+
              '    q_rgb *= uRefrParams.z;                                 /* brightness 乘性 */\n'+
              '    q_rgb *= uRefrColor;                                    /* u_refraction_color 乘性 */\n'+
              '    diffuseColor.rgb = mix(diffuseColor.rgb, q_rgb, q_mm);  /* × 表面权重（此处用 q_mm，见上方标注②） */\n'+
              '  }\n';
            sh.fragmentShader=sh.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n'+injC);
            var ANCHOR_B='#include <normal_fragment_maps>';
            if(sh.fragmentShader.indexOf(ANCHOR_B)>=0){
              sh.fragmentShader=sh.fragmentShader.replace(ANCHOR_B, ANCHOR_B+'\n'+injB);
            } else {
              (window.__glowErrors=window.__glowErrors||[]).push({where:'crystalLayers',why:'anchor <normal_fragment_maps> 未命中(1) ⇒ caustic/refraction 未注入'});
              try{ console.error('[crystalLayers] anchor miss: normal_fragment_maps'); }catch(e){}
            }
            m.userData.__fragCrystal=sh.fragmentShader;   // 供 __chainMats 验证注入是否真的生效
          };
          /* ★★ 修复（2026-09-18，shader-auditor 实测定位）：`prevKey` 是 `m.customProgramCacheKey`，
                  而它是 **three 的原型方法**（恒为函数）。无接收者调用 `prevKey()` 时，
                  three 默认实现会读 `this.onBeforeCompile.toString()`，此时 `this===undefined`
                  ⇒ **抛 TypeError ⇒ renderer.render() 中止 ⇒ 整帧黑屏**。
                  （触发条件：prim2 缺 fashion_qiangpi.cube ⇒ iblCube=null ⇒ prevKey 落到原型）
                  修法：`.call(m)` 并包 try/catch，保证它永远不会再把整帧弄黑。 */
           m.customProgramCacheKey=function(){ try{ return 'crystalSrc_'+primIdx+'_'+((typeof prevKey==='function')?prevKey.call(m):''); }catch(e){ return 'crystalSrc_'+primIdx+'_prevkey_err'; } };
          /* ★ 修正（2026-09-16）：原此处把 u_crystal_metallic 写入 m.metalness —— 已撤销。
             该值是"晶体层"参数，不是基底 albedo 的金属度；映射后 albedo 退出漫反射，
             导致晶体变暗、亮紫/亮蓝丢失（与本文件 L1295-1301 早已记录的同一条结论一致）。
             源值仍保留在 crystal_params 与链上，语义标 unresolved。 */
          m.userData.crystal_metallic_source=(cp&&cp.u_crystal_metallic!==undefined)?cp.u_crystal_metallic:null;
        }
        /* ★ 新增（2026-09-18，shader-auditor）：图层预览开关（默认 null ⇒ 材质本体，**零默认改动**）。
           只用于证明 caustic/reflection 贴图已按 prim 绑上并按 vMapUv 采样；
           源参与公式未恢复前，两者绝不进入颜色运算。 */
        /* ★★ 改动（2026-09-19，shader-auditor，task-43）：四层开关**统一入口**。
           现状（如实）：`caustic` / `reflection` 两张贴图已在 task-13 绑成 uniform（`uCausticTex`/`uReflTex`），
             故这两层的「图层预览」可测；`detail`（`uDetailMap` 已绑、源公式 d=m×DetailMap.a 已用，但
             **细节层复合公式 u_detail_tilling/intensity/offset_* 未定证**）与 `refraction`
             （manifest `t_refraction_tex=null`，**整族未发布**）**不实现采样**，只登记 unresolved 并保持 OFF
             —— 按 task-43 第 1 条「找不到源公式的层不实现」。
           默认全 OFF ⇒ 画面与本改动前逐字节一致。 */
        state.__crystalLayerOn=state.__crystalLayerOn||{detail:false,caustic:false,reflection:false,refraction:false};
        const LAYER_REASON={
          caustic:'已绑 uCausticTex（task-13）：**仅诊断预览**；源复合公式已由 DXBC 给出，但 manifest 无值表 ⇒ 不接线、保持 OFF',
          /* ★ 改动（2026-09-19，task-45 第 4 条）：源侧 **15/15 PS 不采样** t_reflection_tex
             （`s_reflection_tex` 只是采样器名；L464 实际用它采样 caustic）⇒ 本层**不是源行为**，
             开关保留仅供诊断对照，并明确标 source_not_sampled，不得当作源驱动。 */
          reflection:'**source_not_sampled**：源侧 15/15 PS 不采样 t_reflection_tex（RX_CRYSTAL_source_formulas_20260919.md 第 4 条：s_reflection_tex 仅采样器名、L464 用它采样 caustic）⇒ 保留诊断开关，但不是源行为',
          detail:'源公式已知（uv+offset → ×u_detail_tilling → sample → xy→±1×u_detail_intensity / z=1+I(z−1) → ×m）；**manifest 无 source_uniforms 值 ⇒ 不接线**',
          refraction:'贴图已就位（refraction_envmap_3.png）；源公式已知（rotation=角度×2π + 球面 UV / contrast=线性 remap+saturate / brightness× / u_refraction_color×）；**manifest 无 source_uniforms 值 ⇒ 不接线**'
        };
        /* ★ 新增（2026-09-19，task-45）：逐层「还缺哪些源 uniform 值」。值一律**从 manifest 逐 prim 读**
           （`pr.source_uniforms`），**不硬编**；实测两个 manifest 目前均无该字段（None）⇒ 全部 unresolved 且保持 OFF。 */
        const LAYER_NEEDS={
          detail:['u_detail_tilling','u_detail_intensity'],
          caustic:['u_caustic_tilling','u_caustic_depth','u_caustic_brightness'],
          refraction:['u_refraction_rotation','u_refraction_contrast','u_refraction_brightness','u_refraction_color'],
          reflection:[]
        };
        /* 可选值：缺了不阻塞 data_ready，按源公式默认行为处理（lead 口径）。 */
        const LAYER_NEEDS_OPTIONAL={
          detail:['u_detail_offset_x','u_detail_offset_y'],
          caustic:[], refraction:['u_refraction_mipmap','u_refraction_opacity'], reflection:[]
        };
        const suOf=(pr&&pr.source_uniforms)||null;
        /* 值一律读 manifest 的 source_uniforms（lead 已并入：1110171=1e091b35f713a1a4 / 1110177=de07399720411145），
           支持两种形态：裸值 或 `{value:…,type,entry_offset,confidence,…}`；**零硬编**。 */
        const suVal=function(k){ if(!suOf) return null; var e=suOf[k];
          if(e===null||e===undefined) return null;
          var v=(typeof e==='object'&&e!==null&&('value' in e))?e.value:e;
          return (v===null||v===undefined)?null:v; };
        const layerDataReady=function(k){
          var need=LAYER_NEEDS[k]||[];
          for(var i=0;i<need.length;i++){ if(suVal(need[i])===null) return false; }
          return true;
        };
        const layerValuesPresent=function(k){
          var out={}; (LAYER_NEEDS[k]||[]).concat(LAYER_NEEDS_OPTIONAL[k]||[]).forEach(function(u){ out[u]=suVal(u); });
          return out;
        };
        window.__layer=function(n){ try{
          var nm=(n===null||n===undefined||n==='off')?null:String(n);
          var known=['detail','caustic','reflection','refraction'];
          if(nm!==null && known.indexOf(nm)<0) return 'ERR layer 必须是 detail|caustic|reflection|refraction|off';
          if(nm!==null) state.__crystalLayerOn[nm]=true;
          else known.forEach(function(k){ state.__crystalLayerOn[k]=false; });
          state.__layerTex=(nm==='caustic'||nm==='reflection'||nm==='refraction')?nm:null;
          var hit=0, miss=[], unresolved=[];
          var cauHit=0, refrHit=0, notReady=[];
          (state.__crystalLayer||[]).forEach(function(r){
            /* ★ 改动（2026-09-20，ENVROUTE S2）：补 `refraction` 档（uLayer=3）——
               与 caustic/reflection 同为**诊断直显**，用于逐像素消费证明；源公式体仍由 uRefrOn 单独把闸。 */
            var v=(state.__layerTex==='caustic')?(r.hasCaustic?1.0:0.0)
                 :((state.__layerTex==='reflection')?(r.hasRefl?2.0:0.0)
                 :((state.__layerTex==='refraction')?(r.hasRefr?3.0:0.0):0.0));
            if(r.uLayer) r.uLayer.value=v;                       /* 诊断预览（非源）*/
            /* ★ task-44：真正的源公式体开关（默认 0 ⇒ 与停手版逐字节一致）*/
            var cOn=(state.__crystalLayerOn.caustic && r.cauReady)?1.0:0.0;
            var rOn=(state.__crystalLayerOn.refraction && r.refrReady)?1.0:0.0;
            if(r.uCauOn) r.uCauOn.value=cOn;
            if(r.uRefrOn) r.uRefrOn.value=rOn;
            if(cOn>0) cauHit++;
            if(rOn>0) refrHit++;
            if((state.__crystalLayerOn.caustic && !r.cauReady)||(state.__crystalLayerOn.refraction && !r.refrReady))
              notReady.push({prim:r.prim, caustic_ready:!!r.cauReady, refraction_ready:!!r.refrReady});
          });
          if(nm==='detail'){
            /* detail 层：源公式体需要**法线扰动**，而源式（L396-405，xy→±1×I、z=1+I(z−1)）的注入点
               必须在 `normal` 之后；本链的注入点结构与此冲突 ⇒ 按 lead 纪律**上报结构冲突、不折中成假公式**。 */
            unresolved.push({layer:'detail', applied:false, data_ready:layerDataReady('detail'),
              needs:(LAYER_NEEDS.detail||[]), reason:LAYER_REASON.detail, on:!!state.__crystalLayerOn.detail});
          }
          if(nm==='reflection'){
            unresolved.push({layer:'reflection', applied:!!state.__crystalLayerOn.reflection, source_not_sampled:true,
              data_ready:true, needs:[], reason:LAYER_REASON.reflection, on:!!state.__crystalLayerOn.reflection});
          }
          try{_forceRender();_forceRender();}catch(e){}
          return JSON.stringify({layer:nm, on:state.__crystalLayerOn, mats:(state.__crystalLayer||[]).length,
            preview_shown:hit, preview_skipped:miss,
            caustic_mats:cauHit, refraction_mats:refrHit, not_ready:notReady, unresolved:unresolved,
            note:'源公式体（caustic/refraction）默认 OFF；detail 因注入点结构冲突未实现；预览=texture2D 直显（非源）'});
        }catch(e){ return 'ERR '+e; } };
        /* ★ 新增（2026-09-19，task-43）：只读探针 —— 逐 prim 逐层 {on, applied, texture_bound} + 逐层 reason。 */
        window.__crystalLayers=function(){
          try{
            var out={layers:[], prims:[]};
            ['detail','caustic','reflection','refraction'].forEach(function(k){
              out.layers.push({layer:k, on:!!(state.__crystalLayerOn||{})[k],
                applied:(k==='caustic'),
                source_not_sampled:(k==='reflection'),
                data_ready:layerDataReady(k), needs:(LAYER_NEEDS[k]||[]),
                optional:(LAYER_NEEDS_OPTIONAL[k]||[]),
                values:(k==='caustic'||k==='detail'||k==='refraction')?layerValuesPresent(k):null,
                reason:LAYER_REASON[k]}); });
            (state.__crystalLayer||[]).forEach(function(r){
              out.prims.push({prim:r.prim,
                detail:{on:!!(state.__crystalLayerOn||{}).detail, applied:false, texture_bound:!!r.uDetailBound},
                caustic:{on:!!(state.__crystalLayerOn||{}).caustic, applied:true, texture_bound:!!r.hasCaustic},
                reflection:{on:!!(state.__crystalLayerOn||{}).reflection, applied:true, texture_bound:!!r.hasRefl},
                refraction:{on:!!(state.__crystalLayerOn||{}).refraction,
                            /* ★ 改动（2026-09-20，ENVROUTE S2）：原恒 `false/false`（当时 manifest 无 t_refraction_tex）。
                               S2 后 S1 的 `t_refraction_tex` 已在 M1/M4 绑上 ⇒ `texture_bound` 如实读数；
                               `applied` 指"有**诊断直显**通路"（源公式体仍由 `uRefrOn` 独立把闸，需本 prim 值齐备）。 */
                            applied:true, applied_kind:'diagnostic_preview_only',
                            source_formula_gated:true, texture_bound:!!r.hasRefr}}); });
            out.note='applied=false ⇒ 该层未接入采样（源公式未定证/无贴图），保持 OFF';
            return JSON.stringify(out);
          }catch(e){ return 'ERR '+((e&&e.message)||e); }
        };
        /* ═══ 新增（2026-09-18，shader-auditor）：源级「辉光」+「次表面」层 ═══
           公式来源（反汇编恢复，勿在此重新推导）：
             辉光   pbr_crystal.nfx2_01393c07 blob1 L477-487 + L1065（仅该变体 u_emissive_* 非 [unused]）
             次表面  pbr_crystal.nfx2_3f7860cd blob1 L493-496 + L978-981
           接在片元末尾（与 #include <dithering_fragment> 同级）—— **绝不进 getIBLRadiance**：
             源 L487 ÷u_hdr_luminance.x 与 L1066 ×u_hdr_luminance.x 相消 ⇒ 辉光不乘 HDR 曝光。
           标识符一律 q_ 前缀（GLSL ES 3.00 保留含连续双下划线的标识符——同日事故）。
           APPROXIMATE（已标注，不冒充源）：
             · u_emissive_color_saturation 在 029 c159 **未声明** ⇒ satMix 取材质自身颜色常量，
               分级 u_refraction_color → u_crystal_color → vec3(1.0)WORST_CASE（见下方 tintSrc）
             · DetailMap 缺失 ⇒ 源 r1.w 的 n.z 项降级为 1
             · 次表面 t4.a 门控实测恒 255（olen=262188）⇒ 门控退化为 1，与源一致 */
        if(maskFile){
          const __q=(function(){ try{ return new URLSearchParams(location.search); }catch(e){ return null; } })();
          const glowOn0=(__q&&__q.get('glow')==='0')?0.0:1.0;
          const surfOn0=(__q&&__q.get('surf')==='0')?0.0:1.0;
          const uGlowMask={value:tex(maskFile,false)};
          const uEmisStrength={value:(cp&&Number.isFinite(Number(cp.u_emissive_strength)))?Number(cp.u_emissive_strength):0.0};
          const uEmisFresnel={value:(cp&&Number.isFinite(Number(cp.u_emissive_fresnel)))?Number(cp.u_emissive_fresnel):0.0};
          /* ★ 修复（2026-09-18，紧急）：satMix 的降级**不能取 vec3(1.0)**。
             源 L480-481 为 `satMix = lerp(base, u_emissive_color_saturation.rgb, .a)`，
             其 `base` 是**材质自身的颜色**（非白）。`u_emissive_color_saturation` 在 029 c159 未声明，
             故按下述**显式分级**取 tint，并把实际用了哪一级写进 window.__glowTintSource[prim]：
               ① u_refraction_color（源 L477 `r8 = r7.w * u_refraction_color`；宝石=[1,0,0] 纯红）
               ② u_crystal_color（同族颜色常量，仍属材质自身颜色）
               ③ vec3(1.0) —— 最后兜底，标 WORST_CASE（会得到白宝石，已知不可取）
             诚实标注：源 `base` 严格说来自 L416-418 的基色贴图采样（r1.xyz），该值在此注入点不可得；
             故用上列材质颜色常量作**有源依据的代理**，不冒充源。 */
          const tintSrc=(function(){
            if(cp&&Array.isArray(cp.u_refraction_color)&&cp.u_refraction_color.length>=3)
              return {rgb:v3(cp.u_refraction_color,[1,1,1]), level:'u_refraction_color(source L477)'};
            if(cp&&Array.isArray(cp.u_crystal_color)&&cp.u_crystal_color.length>=3)
              return {rgb:v3(cp.u_crystal_color,[1,1,1]), level:'u_crystal_color(同族颜色常量)'};
            return {rgb:[1,1,1], level:'vec3(1.0) WORST_CASE'};
          })();
          const uEmisSat={value:new state.THREE.Vector3(tintSrc.rgb[0],tintSrc.rgb[1],tintSrc.rgb[2])};
          const uEmisSatW={value:1.0};
          window.__glowTintSource=(window.__glowTintSource||{});
          window.__glowTintSource[primIdx]={prim:primIdx, level:tintSrc.level, rgb:tintSrc.rgb};
          const uSubsurfColor={value:v3(cp&&cp.u_subsurface_color,[0,0,0])};
          const uGlowOn={value:glowOn0}, uSubsurfOn={value:surfOn0};
          const prevGlow=m.onBeforeCompile, prevGlowKey=m.customProgramCacheKey;
          /* ⚠ 尝试记录（2026-09-18，用户报「红色晶体泛白/过曝」）：曾把锚点改到
             `#include <tonemapping_fragment>` 之前（理由：源 o0 必经引擎 tone map），
             但**实测帧 sha 与改前逐字节相同**（`c137ac7f788c634a`）⇒ 对本场景无差异，
             故**已回退**到此锚点，不保留无证据的改动。
             量化结论：泛白主因在**基础层**（辉光 OFF 时晶体区三通道同剪仍 17.9%），
             辉光只是加重项（宝石 R 剪裁 18.21% → 42.25%）。详见 RED_*.png 与工具报告。 */
          const GLOW_ANCHOR='#include <dithering_fragment>';
          const GLOW_FRAG=
            '  /* ── 辉光：源 01393c07 blob1 L482-486 收束于 L1065（APPROXIMATE 见上）── */\n'+
            '  if(uGlowOn > 0.5){\n'+
            '    float q_m   = clamp(texture2D(uGlowMask, vMapUv).r, 0.0, 1.0);        /* r4.x = sat(Tex0.r) L345/346 */\n'+
            '    float q_dz  = 1.0;                                                     /* DetailMap 缺失 ⇒ n.z 项降级 */\n'+
            '    float q_w   = q_m * q_m * q_dz;                                        /* 源 r1.w L392 */\n'+
            '    float q_ndv = clamp(dot(normalize(vViewPosition), normal), 0.0, 1.0);  /* 源 r6.x = sat(NdotV) L404 */\n'+
            '    float q_fr  = 1.0 + uEmisFresnel * (q_ndv - 1.0);                      /* 源 L483 */\n'+
            '    vec3  q_sm  = mix(gl_FragColor.rgb, uEmisSat, uEmisSatW);              /* 源 L480/481 */\n'+
            '    vec3  q_E   = q_sm * (q_w * q_fr) * uEmisStrength;                     /* 源 L485/486 */\n'+
            '    gl_FragColor.rgb += q_w * q_E;                                         /* 源 L1065 */\n'+
            '  }\n'+
            '  /* ── 次表面：源 3f7860cd blob1 L493-496/L978-981（t4.a 门控恒 255 → 退化）── */\n'+
            '  if(uSubsurfOn > 0.5){\n'+
            '    float q_sg  = clamp(texture2D(uGlowMask, vMapUv).g, 0.0, 1.0);         /* Tex0.g */\n'+
            '    float q_snv = clamp(dot(normalize(vViewPosition), normal), 0.0, 1.0);  /* NdotV */\n'+
            '    gl_FragColor.rgb += (1.0 - q_sg) * uSubsurfColor * q_snv;\n'+
            '  }\n';
          m.onBeforeCompile=function(sh){
            if(typeof prevGlow==='function') prevGlow(sh);          /* 先跑 IBL / 晶体 / 不透明 三层 */
            sh.uniforms.uGlowMask=uGlowMask;
            sh.uniforms.uGlowOn=uGlowOn;
            sh.uniforms.uEmisStrength=uEmisStrength;
            sh.uniforms.uEmisFresnel=uEmisFresnel;
            sh.uniforms.uEmisSat=uEmisSat;
            sh.uniforms.uEmisSatW=uEmisSatW;
            sh.uniforms.uSubsurfOn=uSubsurfOn;
            sh.uniforms.uSubsurfColor=uSubsurfColor;
            /* ★ 锚点断言：命中数必须恰好 1；零次/多次 ⇒ 显式上报并**跳过注入**（保持 shader 可编译，
               不静默、也不把整帧弄黑——静默失败是本项目反复踩的坑）。 */
            var hits=String(sh.fragmentShader||'').split(GLOW_ANCHOR).length-1;
            if(hits!==1){
              var msg='[glow] prim'+primIdx+' 锚点 "'+GLOW_ANCHOR+'" 命中 '+hits+' 次（必须恰好 1 次）→ 已跳过注入';
              window.__glowErrors=(window.__glowErrors||[]); window.__glowErrors.push(msg);
              try{ console.error(msg); }catch(e){}
              if(m.userData) m.userData.__glowError=msg;
              return;
            }
            sh.fragmentShader='uniform sampler2D uGlowMask;\nuniform float uGlowOn;\n'
              +'uniform float uEmisStrength;\nuniform float uEmisFresnel;\n'
              +'uniform vec3 uEmisSat;\nuniform float uEmisSatW;\n'
              +'uniform float uSubsurfOn;\nuniform vec3 uSubsurfColor;\n'+sh.fragmentShader;
            sh.fragmentShader=sh.fragmentShader.replace(GLOW_ANCHOR, GLOW_FRAG+GLOW_ANCHOR);
            m.userData.__fragGlow=sh.fragmentShader; m.userData.__shGlow=sh;
            m.userData.__glow={prim:primIdx, anchorHits:hits,
              strength:uEmisStrength.value, fresnel:uEmisFresnel.value,
              subsurf:[uSubsurfColor.value[0],uSubsurfColor.value[1],uSubsurfColor.value[2]],
              glowOn:uGlowOn.value, surfOn:uSubsurfOn.value,
              basis:'glow=pbr_crystal 01393c07 blob1 L477-487+L1065; subsurface=3f7860cd blob1 L493-496+L978-981',
              tintLevel:tintSrc.level, tintRGB:tintSrc.rgb,
              approximate:['emissive_color_saturation 未声明→satMix 取 tint（'+tintSrc.level+'）','DetailMap 缺失→n.z 项=1','t4.a 门控恒 255→退化']};
          };
          m.customProgramCacheKey=function(){ try{ return 'glow2_'+primIdx+'_g'+uGlowOn.value+'_s'+uSubsurfOn.value+'_'+((typeof prevGlowKey==='function')?prevGlowKey.call(m):''); }catch(e){ return 'glow2_'+primIdx+'_err'; } };
          (state.__glowMats=state.__glowMats||[]).push({prim:primIdx, uGlowOn:uGlowOn, uSubsurfOn:uSubsurfOn});
        }
      }
      /* ★ 受控验证（2026-09-17，用户协议第 1/3/4 条）：强制不透明 + Alpha 语义分离。
         源 Blend / Depth / 透明排序状态未恢复前，一律按不透明输出：
           transparent=false / opacity=1 / alphaTest=0 / depthTest=true / depthWrite=true / blending=NoBlending
         并在片元末尾强制 gl_FragColor.a = 1.0，使**数据 Alpha 绝不进入显示 Alpha**。
         依据：t_basecolor.a = 粗糙度数据（外审 §3.5）；cube 采样 .a = RGBM HDR 解码系数（asm 542）。
         二者都不是透明度；把它们用作显示 Alpha 正是「画面发透明 + 黑金色条」的机制。
         晶体同样保持不透明，源 Blend/Depth/折射状态未恢复前标 incomplete，不自行开启透明。 */
      m.vertexTangents = !!(m.normalMap);   /* ★ 有法线图且几何已补切线 → 让 three 定义 USE_TANGENT */
      /* ★ 修复（2026-09-17）：改用 DoubleSide。
         用户报「枪管中空透明」——复现其视角(position[-14.6732,-2.0905,-1.388] roll-177.35 span0.27
         yaw-98.09)后确认：FrontSide 下近侧桶壁的正面背对相机被剔除，**透过外壳看到内壁**，
         呈现发白的半透明区块；切 DoubleSide 后枪管完全实心。
         注意：默认视角下两者只差 4.2%（曾据此误判「面剔除不是主因」），但在正对桶口看进去的
         角度差异极大 —— 单看一个视角的结论不可外推。
         依据：本武器资产是**薄壳**（GLB 无厚度），源管线渲染为实心外观；且 three 的
         MeshStandardMaterial 在 DoubleSide 下会自动翻转背面法线（gl_FrontFacing），光照正确。 */
      m.side = state.THREE.DoubleSide;
      m.transparent=false; m.opacity=1; m.alphaTest=0;
      m.depthTest=true; m.depthWrite=true;
      m.blending=state.THREE.NoBlending;
      m.userData.opaqueForced=true;
      m.userData.blend_depth_state='incomplete(源 Blend/Depth/折射状态未恢复)';
      (function(){
        var prev=m.onBeforeCompile, pk=m.customProgramCacheKey;
        m.onBeforeCompile=function(sh){
          if(typeof prev==='function') prev(sh);
          var A='#include <dithering_fragment>';
          if(sh.fragmentShader.indexOf(A)>=0){
            sh.fragmentShader=sh.fragmentShader.replace(
              A, A+'\n  gl_FragColor.a = 1.0;   /* 强制不透明：数据 Alpha 不得进入显示 Alpha */');
          }
        };
        /* ★ 修复（2026-09-18，shader-auditor）：原式 `'opaque_'+primIdx+'_'+(typeof pk==='function')?pk.call(m):''`
           因运算符优先级恒取三元真分支 ⇒ 当 pk 为 undefined 时 `pk.call(m)` 抛 TypeError ⇒ 整帧中止。
           现补括号 + try/catch（与 L1196 crystalSrc 同一类缺陷、同一修法）。 */
        m.customProgramCacheKey=function(){ try{ return 'opaque_'+primIdx+'_'+((typeof pk==='function')?pk.call(m):''); }catch(e){ return 'opaque_'+primIdx+'_err'; } };
      })();
      m.userData.chain={kind:(isWeapon?'weapon':'crystal'), albedo:srcA, mask_input:(bm||null), family:fam, prim:primIdx,
        rule: isWeapon?'BaseColor=Tex0.rgb（已证）':'C=lerp(lerp(T,T*u_crystal_color,m),lerp(u_base_color,T*u_crystal_color,d),m)',
        metalness_source: isWeapon?'ParamMap(001m) 重排':'u_crystal_metallic['+primIdx+']='+MTL_METAL[primIdx],
        roughness_source: isWeapon?'ParamMap(001m) R':'t_basecolor.a（Roughness=Ta）',
        detail_map_status:((g.DetailMap&&g.DetailMap.file)
          ? 'connected: d = m × DetailMap.a（源声明 5/5 prim；crystal_bump_n_uvva 512² RGB 无 alpha ⇒ a≡1 ⇒ 与 d=m 逐字节同，属预期）'
          : 'unresolved: 以 d=m 降级渲染（DetailMap 无 file）'),
        /* ★ 新增（2026-09-18，shader-auditor；lead 指示 ①⑤）：逐槽绑定状态如实登记（缺的/未发布的不冒名）。 */
        crystal_textures:{
          DetailMap:(g.DetailMap&&g.DetailMap.file)||null,
          t_caustic_tex:(g.t_caustic_tex&&g.t_caustic_tex.file)||null,
          t_reflection_tex:(g.t_reflection_tex&&g.t_reflection_tex.file)||null,
          t_refraction_tex:'not_shipped（整族未发布：2728 变体 × 221 容器 0 命中 ⇒ 不接、不做替身）'},
        absent_by_source:(hasReflKey ? [] : ['t_reflection_tex'])};
      m.userData.neox={mtl_idx:pr.mtl_idx, material:pr.material, shader:pr.shader,
        color_slot:'Tex0', albedo_slot:'SRC_ALBEDO_REMOVED'+primIdx,
        material_fidelity:(strictMode?'source_strict':'reference_approximate'),
        environment:envMode, environment_approximate:(envMode==='diagnostic_environment'),
        /* ★ 改动（2026-09-18，task-13 B）：六面坍缩也属 fail-closed；并如实带上本次 cube 解析错误与已解析面数。 */
        ibl_fail_closed:(envMode==='missing_source_ibl'||envMode==='duplicate_face_urls_ibl'),
        ibl_missing_source:iblMissing, cube_dir_err:cubeErr,
        ibl_faces_resolved:(iblCube&&iblCube.image)?iblCube.image.filter(Boolean).length:0,
        chain_driven:true, failed:!chainOk, missing_inputs:missReq,
        /* ★ 新增（2026-09-18，task-39 P0-3）：逐 prim 的**族 / 必需槽 / 运行期缺项 / 颜色槽 / 失败标记**，
           使「被 fail-closed 隐藏」的材质在 __neox() 里可被识别，而不是悄悄消失。 */
        family:family, family_source:familySource, required_slots:REQUIRED, runtime_missing:missReq,
        declared_unlocated:declaredUnlocated,
        albedo_slot:albedoSlotName, whitelist_no_base:whitelistNoBase, shader_kind:pr.shader_kind||null,
        map_role:(srcA?'albedo(srcA)':(whitelistNoBase?'uv/mask_carrier(Tex0)：不参与颜色（q_T=vec3(1.0)，颜色来自常量）':'none')),
        fail_closed:!chainOk};
      m.userData.chain.family=family; m.userData.chain.family_source=familySource;
      m.userData.chain.required_slots=REQUIRED; m.userData.chain.declared_unlocated=declaredUnlocated;
      m.userData.chain.runtime_missing=missReq; m.userData.chain.albedo_slot=albedoSlotName;
      m.userData.chain.required=REQUIRED; m.userData.chain.missing_inputs=missReq;
      /* ★ 改动（2026-09-18，task-13 B）：把后置判定的 env 模式回写进 **report 的 prim 记录**，
         使 __neox().report.prims[i] 能直接看到 env_mode（六面坍缩时不得再是 source_ibl）。 */
      try{ rec.env_mode=envMode; rec.ibl_faces=(iblCube&&iblCube.image)?iblCube.image.filter(Boolean).length:0;
           rec.cube_dir_err=cubeErr; rec.ibl_missing_source=iblMissing;
           /* ★ 新增（2026-09-18，task-39）：族/族来源/必需槽/缺项/白名单/未定位声明 进 report */
           rec.family=family; rec.family_source=familySource; rec.required_slots=REQUIRED;
           rec.runtime_missing=missReq; rec.declared_unlocated=declaredUnlocated;
           rec.albedo_slot=albedoSlotName; rec.whitelist_no_base=whitelistNoBase;
           rec.shader_kind=pr.shader_kind||null; rec.shader=(pr.shader||null);
           /* ★ 新增（2026-09-19，task-49）：**逐 prim env 警告** —— 凡 envMode != 'source_ibl' 即入列，
              使"某个 prim 拿不到 IBL"在 __neox() 里一眼可见（此前 applied=7/failed=[] 完全失明）。
              **不放宽 fail-closed**：这里只是把事实暴露出来，不改变任何隐藏/绘制决策。 */
           rec.env_warn=(envMode!=='source_ibl')
             ? {envMode:envMode, faces_loaded:(iblCube&&iblCube.image)?iblCube.image.filter(Boolean).length:0,
                envMap_bound:!!(m&&m.envMap), cube_dir_err:cubeErr, ibl_pending:cubePending}
             : null;
           /* ★ 新增（2026-09-19，task-49；lead 裁决 (ii) 候选 A）：**窗口期不提交该 prim 渲染**，
              避免用户看到"大块纯白扁平色块"（窗口帧 3c2249e56afa3638 实测 p50=1.000 / >0.5 58.0%）。
              规则（与 lead 附加 1 一致）：仅当 `envMode==='ibl_pending'` **且** 尚未达上限
              （`!state.__iblRetryExhausted`，或 retry_count < 6）时隐藏；**就绪/收敛 ⇒ 恢复**；
              **`retry_exhausted===true` 必须恢复可见**（绝不永久消失，安全阀）。
              这是**显示时序策略**（不改 final color / 曝光 / 灯光），开关 `__pendingHide(on)` 默认开。
              计数单列 `pending_hidden`，**严禁与 fail-closed 的 hidden/failed 混用**。 */
           if(!window.__pendingHide){
             window.__pendingHide=function(on){ try{ state.__pendingHideOff=(on===false);
               if(on!==false&&state.scene){ state.scene.traverse(function(o){ if(o.isMesh&&o.userData&&o.userData.__pendingHidden){ o.visible=true; o.userData.__pendingHidden=false; } }); try{_forceRender();}catch(e){} }
               return JSON.stringify({pendingHide:(state.__pendingHideOff?'off':'on'), note:'窗口期不提交渲染；达上限强制恢复'});
             }catch(e){ return 'ERR '+((e&&e.message)||e); } };
           }
           var pendHideOn=(state.__pendingHideOff!==true);
           /* ★★ 扩展（2026-09-19，task-49，Lead 裁决 ①）：`pendingHide` 覆盖条件由 `envMode==='ibl_pending'`
              扩到 **任何 `envMode!=='source_ibl'`**（含"门已 ready 但 IBL 注入尚未生效"、`missing_source_ibl` 等）——
              实测窗口帧白块"只减小、未消失"（p50 1.000 → 0.1301）⇒ 原条件过窄。
              **Lead 三条不可协商**：① 收敛（`left===0`）或 `retry_exhausted`（含 retry≥cap）⇒ renderFrame 的恢复块
              **必须恢复可见**（绝不永久消失）；② `rec.pending_hidden` 与 fail-closed 的 `hidden/failed` **分列**，
              且三源同源（已改 read-time 口径）；③ **settle 帧须逐字节一致**（1110171 = `9b08a1134bfc484e`）。 */
           if(pendHideOn && envMode!=='source_ibl' && !state.__iblRetryExhausted){
             m.visible=false; m.userData.__pendingHidden=true; rec.pending_hidden=true;
           } else { rec.pending_hidden=false; }
           }catch(e){}
      m.userData.chain.pending_layers=PENDING_LAYERS.filter(k=>!g[k]||!g[k].file);
      m.userData.chain.fail_closed=!chainOk;
      if(!chainOk){ /* ★ 新增（2026-09-18，task-39）：fail-closed 必须**可验收识别** —— 写进 report。 */
                    rec.fail_closed=true; rec.runtime_fail_closed=true; rec.hidden=(strictMode && !LAB);
                    rec.status=rec.hidden?'failed_hidden':'failed_needs_lab_diag';
                    rec.missing_required=missReq; rec.family=family; rec.required_slots=REQUIRED;
                    try{ rec.material_visible=m.visible; }catch(e){}
                    if(strictMode && !LAB){ m.visible=false; }   /* 生产：缺输入→不绘制（品红仅 lab 诊断） */
                    else if(strictMode){ m.color.setHex(0xff00ff); m.map=null; m.emissive.setHex(0x000000); } }
    }
     /* ★ 新增（2026-09-18，shader-auditor）：辉光 / 次表面 运行时开关（默认开）——A/B 与一键回退。
        冷启动关闭：URL 加 ?glow=0 / ?surf=0；运行中：WikiWeaponViewer.__glow(false) / .__surf(false)。
        只改 uniform.value，不需要重编译（与 uCrystalColor 同法）。 */
     window.__glowSet=function(on){
       try{ var n=0; (state.__glowMats||[]).forEach(function(r){ r.uGlowOn.value=on?1.0:0.0; n++; });
            state.__glow=!!on; return JSON.stringify({applied:n, glow:!!on}); }
       catch(e){ return 'ERR '+String((e&&e.message)||e); }
     };
     window.__surfSet=function(on){
       try{ var n=0; (state.__glowMats||[]).forEach(function(r){ r.uSubsurfOn.value=on?1.0:0.0; n++; });
            state.__surf=!!on; return JSON.stringify({applied:n, surf:!!on}); }
       catch(e){ return 'ERR '+String((e&&e.message)||e); }
     };
     window.__glowState=function(){
       try{
         var rows=[];
         if(state.scene) state.scene.traverse(function(o){
           if(!o.isMesh) return;
           var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
           if(!mm||!mm.userData||!mm.userData.__glow) return;
           var g=mm.userData.__glow, sh=mm.userData.__shGlow;
           rows.push({prim:g.prim, glowOn:g.glowOn, surfOn:g.surfOn, strength:g.strength, fresnel:g.fresnel,
                      subsurf:g.subsurf, anchorHits:g.anchorHits, fragGlow:!!mm.userData.__fragGlow,
                      err:mm.userData.__glowError||null,
                      hasUGlowOn:!!(sh&&sh.uniforms&&sh.uniforms.uGlowOn),
                      uGlowOnVal:(sh&&sh.uniforms&&sh.uniforms.uGlowOn)?sh.uniforms.uGlowOn.value:null,
                      uSubsurfOnVal:(sh&&sh.uniforms&&sh.uniforms.uSubsurfOn)?sh.uniforms.uSubsurfOn.value:null,
                      uSubsurfColor:(sh&&sh.uniforms&&sh.uniforms.uSubsurfColor)?sh.uniforms.uSubsurfColor.value:null,
                      uEmisStrength:(sh&&sh.uniforms&&sh.uniforms.uEmisStrength)?sh.uniforms.uEmisStrength.value:null,
                      tintLevel:g.tintLevel||null, tintRGB:g.tintRGB||null,
                      uEmisSat:(sh&&sh.uniforms&&sh.uniforms.uEmisSat)?[sh.uniforms.uEmisSat.value.x,sh.uniforms.uEmisSat.value.y,sh.uniforms.uEmisSat.value.z]:null,
                      glowCallsInFrag:(mm.userData.__fragGlow?((mm.userData.__fragGlow.match(/q_E/g)||[]).length):null)});
         });
         return JSON.stringify({mats:(state.__glowMats||[]).length, rows:rows, errors:(window.__glowErrors||[])});
       }catch(e){ return 'ERR '+String((e&&e.message)||e); }
     };
     try{ if(window.WikiWeaponViewer){ window.WikiWeaponViewer.__glow=window.__glowSet;
           window.WikiWeaponViewer.__surf=window.__surfSet;
           window.WikiWeaponViewer.__glowState=window.__glowState; } }catch(e){}
     /* ★ 新增（2026-09-18）：SFX/effects **运行时原始读数** —— 用于区分「磁盘声明」与「运行时实际拿到」。
        背景：1110152 的 viewer.json 磁盘写 status='partial'，但按钮显示「该模型没有 SFX 清单」且 disabled ⇒
        updateEffectsButton()(L722-727) 判定用的 state.config.effects 与磁盘不一致，必须看原始值而非推断。 */
     window.__cfgEffects=function(){
       try{
         var e=state.config&&state.config.effects;
         var s3=null; try{ s3=(state.record&&state.record.preview_3d)?state.record.preview_3d:null; }catch(_){}
         return JSON.stringify({
           hasConfig:!!state.config,
           config_manifest:(state.config&&state.config.manifest)||null,
           manifestUrl:state.manifestUrl||null,
           effects_type:typeof e,
           effects_status:(e&&e.status!==undefined)?e.status:'<absent>',
           effects_keys:e?Object.keys(e).slice(0,24):null,
           effects_node_count:(e&&(e.node_count||e.nodes_count||(e.nodes?e.nodes.length:null)))||null,
           adapter_present:!!state.effectsAdapter,
           adapter_attach_type:(state.effectsAdapter&&typeof state.effectsAdapter.attach)||null,
           handle_present:!!state.effectsHandle,
           btn_disabled:state.sfxButton?!!state.sfxButton.disabled:null,
           btn_text:state.sfxButton?state.sfxButton.textContent:null,
           btn_title:state.sfxButton?state.sfxButton.title:null,
           inline_preview3d_keys:s3?Object.keys(s3).slice(0,16):null,
           inline_has_effects:s3?Object.prototype.hasOwnProperty.call(s3,'effects'):null,
           inline_effects:(s3&&s3.effects!==undefined)?s3.effects:null
         });
       }catch(err){ return 'ERR '+String((err&&err.message)||err); }
     };
     try{ if(window.WikiWeaponViewer) window.WikiWeaponViewer.__cfgEffects=window.__cfgEffects; }catch(e){}
     window.__primSolid=function(on){
       try{
         var T=state.THREE; if(!T) return 'ERR no THREE';
         var PAL=[0xff0000,0x00ff00,0x0000ff,0xffff00,0xff00ff,0x00ffff,0xffffff];
         var k=0, map=[];
         if(!state.scene) return 'ERR no scene';
         state.scene.traverse(function(o){
           if(!o.isMesh) return;
           var om=o.material;
           var prim=(om&&om.userData&&om.userData.chain&&om.userData.chain.prim!==undefined)?om.userData.chain.prim:null;
           map.push({k:k, prim:prim, visible:!!o.visible, matType:(om&&om.type)||null});
           if(on){
             if(!o.userData.__origMat) o.userData.__origMat=om;
             var nm=new T.MeshBasicMaterial({color:PAL[k%7],toneMapped:false,fog:false});
             nm.userData.palIdx=k%7;
             o.material=nm;
           } else if(o.userData.__origMat){ o.material=o.userData.__origMat; }
           k++;
         });
         try{ _forceRender(); _forceRender(); }catch(e){}
         return JSON.stringify({count:k, map:map});
       }catch(e){ return 'ERR '+String((e&&e.message)||e); }
     };
     // 逐 prim 独占渲染：只显示 chain.prim===i 的网格（其余隐藏），用于无重叠掩码
     window.__chainMats=function(){
        try{
          var out=[];
          if(!state.scene) return JSON.stringify({err:'no scene'});
          state.scene.traverse(function(o){
            if(!o.isMesh) return;
            var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
            if(!mm){ out.push({name:o.name, mat:null}); return; }
            var ud=mm.userData||{};
            var fragIbl=ud.__frag||null, fragCry=ud.__fragCrystal||null;
            out.push({name:o.name, type:mm.type, visible:o.visible, matVisible:mm.visible,
              metalness:(mm.metalness!==undefined?mm.metalness:null),
              roughness:(mm.roughness!==undefined?mm.roughness:null),
              hasMap:!!mm.map, hasEnvMap:!!mm.envMap,
              transparent:!!mm.transparent, opacity:(mm.opacity!==undefined?mm.opacity:null),
              alphaTest:(mm.alphaTest!==undefined?mm.alphaTest:null),
              blending:(mm.blending!==undefined?mm.blending:null),
              depthTest:(mm.depthTest!==undefined?mm.depthTest:null),
              opaqueForced:!!ud.opaqueForced,
              blendDepthState:ud.blend_depth_state||null,
              side:(mm.side!==undefined?mm.side:null), depthWrite:(mm.depthWrite!==undefined?mm.depthWrite:null),
              colorHex:(mm.color&&mm.color.getHexString)?('#'+mm.color.getHexString()):null,
              envMapIntensity:(mm.envMapIntensity!==undefined?mm.envMapIntensity:null),
              chainPrim:(ud.chain&&ud.chain.prim!==undefined)?ud.chain.prim:null,
              previewMode:ud.__previewMode||null,
              hasIblInjection:!!(fragIbl&&fragIbl.indexOf('uCustomIbl')>=0),
              hasCrystalInjection:!!(fragCry&&fragCry.indexOf('uCrystalMask')>=0),
              crystalFragSet:!!fragCry,
              crystalFragLen:(fragCry?fragCry.length:null),
              crystalHasMapAnchor:!!(fragCry&&fragCry.indexOf('#include <map_fragment>')>=0),
              crystalHasDitherAnchor:!!(fragCry&&fragCry.indexOf('#include <dithering_fragment>')>=0),
              crystalMetallicSource:(ud.crystal_metallic_source!==undefined?ud.crystal_metallic_source:null),
              crystalBlock:(ud.__crystalBlock!==undefined?ud.__crystalBlock:null)});
          });
          return JSON.stringify({count:out.length, mats:out});
        }catch(e){ return 'ERR '+String((e&&e.message)||e); }
      };
      /* ★ 新增（2026-09-16）：只切可见性、**保留链材质**的逐 prim 显示。
         与 __primOnly 的区别：__primOnly 会把材质换成纯白 MeshBasic，只能看几何；
         本函数保留链材质，用于判断「某个 prim 单独看是什么颜色/是否发暗像透明」。 */
      window.__primShow=function(i){
        try{
          var n=0, shown=0;
          if(!state.scene) return 'ERR no scene';
          state.scene.traverse(function(o){
            if(!o.isMesh) return;
            var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
            var prim=(mm&&mm.userData&&mm.userData.chain&&mm.userData.chain.prim!==undefined)?mm.userData.chain.prim:null;
            if(i===null||i===undefined){ o.visible=true; }
            else if(prim===i){ o.visible=true; shown++; }
            else { o.visible=false; }
            n++;
          });
          try{ _forceRender(); _forceRender(); }catch(e){}
          return JSON.stringify({count:n, shown:shown, prim:i});
        }catch(e){ return 'ERR '+String((e&&e.message)||e); }
      };
      /* ★ 改写（2026-09-17，用户口径第 6 条）：A/B/C 对照 —— **同一套 Three BRDF，只变环境输入**
         A = Three BRDF，**不启用环境**（源 radiance 置 0）
         B = Three BRDF + 正确源 cube
         C = Three BRDF + **交换 cube 负面对照**（weapon↔crystal 互换）
         null = 还原。
         不改灯光、曝光、颜色、金属度；材质保持不透明。
         注意：A **不是**"裸 albedo"，而是 Three 完整 BRDF（direct/indirect diffuse、specular、
         F0、Fresnel、遮蔽、toneMapping）在无环境下的结果 —— 用于验证"表面层次是否仍在"。 */
      /* ★ 重定义（2026-09-18，用户令 Task4）：三组固定其它条件，只变目标变量。
         A = **正确源颜色纹理直出**（无光照 MeshBasicMaterial，toneMapped=false）—— 验纹理绑定
         B = 当前 BRDF，**关闭自定义 IBL**（uIblScale=0）—— 无其它照明时可能偏黑，**不得单凭黑色判失败**
         C = 同一 BRDF，**开启对应源 cube**（恢复 uIblScale 与 uCustomIbl）
         null = 还原。
         注意：A 用 `srcA`（= weapon 的 Tex0 / crystal 的 t_basecolor，即 manifest 的当前绑定），
         不自行挑图；B/C 与 A 共用同一 mesh 集合与相机，保证"固定其他条件"。 */
      window.__abcProbe=function(mode){
        try{
          var T=state.THREE;
          if(!state.scene) return 'ERR no scene';
          if(!state.__abcOrig) state.__abcOrig={};
          function cubeOf(name){
            state.__abcCubes=state.__abcCubes||{};
            if(state.__abcCubes[name]) return state.__abcCubes[name];
            var B=(state.modelDir||'')+'src_cube/faces/';
            var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return B+name+'_f'+i+'_m0.png';}));
            t.colorSpace=T.NoColorSpace; t.generateMipmaps=true;
            t.minFilter=T.LinearMipmapLinearFilter; t.magFilter=T.LinearFilter;
            t.wrapS=t.wrapT=T.ClampToEdgeWrapping;
            state.__abcCubes[name]=t; return t;
          }
          var baseScale=(state.iblScale===undefined?1.0:state.iblScale), n=0, skipped=[];   /* ★ task-45：与主路径统一为 1.0 */
          state.scene.traverse(function(o){
            if(!o.isMesh) return;
            var cur=o.material; if(Array.isArray(cur)) cur=cur[0];
            var orig=state.__abcOrig[o.uuid]||cur;
            if(!orig||!orig.userData||!orig.userData.chain) return;
            if(!state.__abcOrig[o.uuid]) state.__abcOrig[o.uuid]=orig;
            /* A：源颜色纹理直出 */
            if(mode==='A'){
              var t=(orig.map&&orig.map.clone)?orig.map.clone():null;
              if(t){ t.colorSpace=T.SRGBColorSpace; t.needsUpdate=true; }
              var mb=new T.MeshBasicMaterial({map:t, side:T.DoubleSide, toneMapped:false, fog:false});
              mb.userData={__abcDirect:true, __srcFile:(orig.map&&orig.map.image&&orig.map.image.src)||null};
              o.material=mb; n++; return;
            }
            o.material=orig;
            var sh=orig.userData.__sh;
            if(mode==='D'||mode==='F'){
              orig.side=(mode==='D')?T.DoubleSide:T.FrontSide; orig.needsUpdate=true; n++; return;
            }
            if(!sh||!sh.uniforms||!sh.uniforms.uCustomIbl||!sh.uniforms.uIblScale){
              skipped.push(orig.userData.chain.prim); n++; return;
            }
            var ibl=orig.userData.ibl||'qiangpi';
            if(mode==='B'){ sh.uniforms.uIblScale.value=0.0; }
            else { sh.uniforms.uIblScale.value=baseScale; sh.uniforms.uCustomIbl.value=cubeOf(ibl); }
            n++;
          });
          try{_forceRender();_forceRender();}catch(e){}
          return JSON.stringify({mode:mode||'restore', touched:n, skipped:skipped,
                                 iblScale:(mode==='B'?0:baseScale)});
        }catch(e){ return 'ERR '+String((e&&e.message)||e); }
      };
      /* ★ 新增（2026-09-17，用户口径第 7 条）：运行态输出实际 roughness / LOD / cube / F0。
         只报**实测值**，不做推断；roughnessMap 存在时真实 roughnessFactor = roughness × 贴图纹素，
         故额外给出 hasRoughnessMap 供外部结合贴图均值计算。 */
      window.__brdfState=function(){
        try{
          var out=[];
          if(!state.scene) return JSON.stringify({err:'no scene'});
          state.scene.traverse(function(o){
            if(!o.isMesh) return;
            var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
            if(!mm||!mm.userData||!mm.userData.chain) return;
            var ud=mm.userData, sh=ud.__sh;
            var rough=(mm.roughness!==undefined)?mm.roughness:null;
            var metal=(mm.metalness!==undefined)?mm.metalness:null;
            var lodMat=(typeof rough==='number')?(5.0+1.2*Math.log2(Math.max(rough,0.0019))):null;
            out.push({
              prim:ud.chain.prim, kind:ud.chain.kind,
              roughness:rough, hasRoughnessMap:!!mm.roughnessMap,
              metalness:metal,
              f0:((typeof metal==='number'&&metal>=0.999)?'baseColor(metal)':'0.04(dielectric)'),
              lod_from_material_roughness:(lodMat!==null?Math.round(lodMat*100)/100:null),
              iblSource:ud.ibl||null,
              iblScale:(sh&&sh.uniforms&&sh.uniforms.uIblScale)?sh.uniforms.uIblScale.value:null,
              iblRadianceOverride:!!ud.__iblRadianceOverride,
              cubemapFaces:(sh&&sh.uniforms&&sh.uniforms.uCustomIbl&&sh.uniforms.uCustomIbl.value&&sh.uniforms.uCustomIbl.value.image)?sh.uniforms.uCustomIbl.value.image.length:null,
              envMapIntensity:(mm.envMapIntensity!==undefined)?mm.envMapIntensity:null,
              transparent:!!mm.transparent, opacity:mm.opacity, alphaTest:mm.alphaTest,
              blending:mm.blending, depthTest:mm.depthTest, depthWrite:mm.depthWrite,
              blendDepthState:ud.blend_depth_state||null,
              detailMapStatus:(ud.chain&&ud.chain.detail_map_status)||null,
              /* ★ 诊断（2026-09-17）：DetailMap 运行时开关的真实状态 */
              hasUDetail:!!(sh&&sh.uniforms&&sh.uniforms.uHasDetail),
              uHasDetailVal:(sh&&sh.uniforms&&sh.uniforms.uHasDetail)?sh.uniforms.uHasDetail.value:null,
              hasUDetailMap:!!(sh&&sh.uniforms&&sh.uniforms.uDetailMap&&sh.uniforms.uDetailMap.value),
              normalScaleY:(mm.normalScale?mm.normalScale.y:null),
              useDetailFlag:(state.__useDetail===true)
            });
          });
          return JSON.stringify({count:out.length, mats:out});
        }catch(e){ return 'ERR '+String((e&&e.message)||e); }
      };
      /* ★ 新增（2026-09-17）方案对照开关：逐项开启/关闭可选实现，以便**逐图对比**而非靠推断。
         __optProbe('detail', true/false) → 晶体公式的 d 是否乘 DetailMap.a（源公式 d = m × D.a）
         __optProbe('ngflip', true/false) → 法线贴图 G 通道朝向翻转（等价 standard DirectX↔OpenGL，用 normalScale.y 实现）
         只改这两项；不动颜色/曝光/灯光/金属度。 */
      window.__optProbe=function(name,on){
        try{
          var n=0;
          if(name==='detail'){
            state.__useDetail=!!on;
            state.scene.traverse(function(o){
              if(!o.isMesh) return;
              var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
              var sh=mm&&mm.userData&&mm.userData.__sh;
              if(sh&&sh.uniforms&&sh.uniforms.uHasDetail){ sh.uniforms.uHasDetail.value=on?1.0:0.0; n++; }
            });
          } else if(name==='ngflip'){
            state.__ngFlip=!!on;
            state.scene.traverse(function(o){
              if(!o.isMesh) return;
              var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
              if(mm&&mm.normalMap&&mm.normalScale){ mm.normalScale.set(1.0, on?-1.0:1.0); mm.needsUpdate=true; n++; }
            });
          } else return 'ERR unknown option: '+name;
          try{_forceRender();_forceRender();}catch(e){}
          return JSON.stringify({option:name, on:!!on, touched:n});
        }catch(e){ return 'ERR '+String((e&&e.message)||e); }
      };
      window.__primOnly=function(i){
       try{
         var T=state.THREE; if(!T) return 'ERR no THREE';
         var n=0, shown=0;
         if(!state.scene) return 'ERR no scene';
         state.scene.traverse(function(o){
           if(!o.isMesh) return;
           var om=o.material;
           var prim=(om&&om.userData&&om.userData.chain&&om.userData.chain.prim!==undefined)?om.userData.chain.prim:null;
           if(!o.userData.__origMat) o.userData.__origMat=om;
           if(i===null||i===undefined){ o.visible=true; if(o.userData.__origMat) o.material=o.userData.__origMat; }
           else if(prim===i){ o.visible=true; o.material=new T.MeshBasicMaterial({color:0xffffff,toneMapped:false,fog:false}); shown++; }
           else { o.visible=false; }
           n++;
         });
         try{ _forceRender(); _forceRender(); }catch(e){}
         return JSON.stringify({count:n, shown:shown, prim:i});
       }catch(e){ return 'ERR '+String((e&&e.message)||e); }
     };
     // 诊断环境：用候选 cube（CANDIDATE_PROBE_REMOVED 级）替换中性棚光 —— 仅 diagnostic_environment，绝不进 strict
     window.__useCubeEnv=function(on){
       try{
         var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
         if(!state.__origEnv) state.__origEnv=state.scene.environment;
         var setEI=function(v){ try{ state.scene.traverse(function(o){ if(o.isMesh&&o.material&&o.userData&&o.userData.neox){
             o.material.envMapIntensity=v; o.material.needsUpdate=true; } }); }catch(e){} };
         if(!on){ state.scene.environment=state.__origEnv||null; state.__cubeEnvOn=false; setEI(0.0);
                  try{_forceRender();_forceRender();}catch(e){} return 'off'; }
         var base='assets/3d/weapon_skin/1110171/cube_cand/character_08_00745_f';
         var urls=[0,1,2,3,4,5].map(function(i){return base+i+'.png';});
         var pm=new T.PMREMGenerator(state.renderer);
         return new Promise(function(res){
           new T.CubeTextureLoader().load(urls, function(ct){
             ct.colorSpace=T.SRGBColorSpace;
             try{ state.scene.environment=pm.fromCubemap(ct).texture; state.__cubeEnvOn=true; setEI(1.0);
                  state.scene.environmentIntensity=1.0; }
             catch(e){ return res('ERR pm '+((e&&e.message)||e)); }
             try{_forceRender();_forceRender();_forceRender();}catch(e){}
             res('ok cube_env');
           }, undefined, function(){ res('ERR cube load'); });
         });
       }catch(e){ return 'ERR '+((e&&e.message)||e); }
     };
    try{ if(old&&old.dispose) old.dispose(); }catch(e){}
    mesh.material=m;
    /* ★ 新增（2026-09-20，EMISTOGGLE）：把两档自发光开关应用到**活的链材质**上（默认全 false ⇒ 不改任何东西）。
       放在 `mesh.material=m` 之后：此时 m.userData.chain（含 prim 序号）已由上方 L3018 区域装好。 */
    try{ if(typeof emisPatchMaterial==='function'){ emisPatchMaterial({mat:m,base:null},i,emisResolve()); } }catch(e){}
    rec.neox_replaced = (mesh.material===m) && (mesh.material.userData&&mesh.material.userData.neox===m.userData.neox);
    rec.runtime_refs = {map:!!m.map, normalMap:!!m.normalMap, metalnessMap:!!m.metalnessMap};
    /* ★ 改动（2026-09-18，task-39，lead 硬要求）：**报告必须与真实可见性一致** ——
       运行期 fail-closed（rec.runtime_fail_closed，含 unknown family / 缺必需槽 / 晶体缺 t_basecolor）
       的 prim 必须出现在 failed/missing 里，不能只写 rec.status 而让 rep.failed 保持空。 */
    if(ok && !rec.runtime_fail_closed){ rec.status='applied'; rep.applied++; rep.applied_prims.push(i); }
    else  { rec.status=rec.hidden?'failed_hidden':(rec.runtime_fail_closed?'failed_runtime':'failed');
            if(!rec.hidden && rec.runtime_fail_closed){ rec.status='failed_visible_diag'; }
            rep.failed.push({prim:i, mtl_idx:pr.mtl_idx, material:pr.material,
                             shader:pr.shader, missing:missRequired,
                             runtime_missing:(rec.runtime_missing||[]), family:rec.family||null,
                             hidden:!!rec.hidden});
            rep.missing.push({prim:i, slots:(missRequired.length?missRequired:(rec.runtime_missing||[])),
                              family:rec.family||null, hidden:!!rec.hidden}); }
    /* ★ 新增（2026-09-19，task-49）：env 警告进 `rep.env_warn`，并在 `rep.missing` 里以
       `slots:['__env_ibl__']` 呈现 —— 让"prim 拿不到 IBL"在验收主门里可见（不改 fail-closed 决策）。 */
    if(rec.env_warn){ rep.env_warn=rep.env_warn||[];
      rep.env_warn.push({prim:i, envMode:rec.env_warn.envMode, faces_loaded:rec.env_warn.faces_loaded});
      rep.missing.push({prim:i, slots:['__env_ibl__'], envMode:rec.env_warn.envMode}); }
    rep.prims.push(rec);
  }
  state.neoxReport=rep; state.neoxManifest=man;
  /* ★★ 新增（2026-09-19，shader-auditor，task-45 第 1 项）：`u_cube_brightness` 开关 + 探针。
     位置说明：**定义在 mesh 循环之后**（而非某个 `onBeforeCompile` 内）⇒ 只要 manifest 应用过就存在，
     与"是否存在 iblCube"无关；无接线材质的皮肤调它也只返回 `rows:[]`（不抛错、不伪造）。
     · `__cubeBright(true|false)`：唯一开关。**只改 uniform 值，不写第二状态源**（探针从材质读回）。
     · 值只来自 manifest `source_uniforms.u_cube_brightness`；`absent ⇒ 不覆盖`；
       `|v-1|<=1e-9`（即源值本身就是 1.0）也视为**无需接线**，不置 On。
     · `__cubeBrightProbe()`：逐 prim 回报 {prim,value,source,on} + 本次 task-45 的 `unresolved` 清单。 */
  if(!window.__cubeBright){
    window.__cubeBright=function(on){ try{
      state.__cubeBrightOn=(on!==false);
      var n=0, vals=[];
      if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
        if(!mm||!mm.userData) return; var sh2=mm.userData.__sh, cb=mm.userData.__cubeBright;
        if(!sh2||!sh2.uniforms||!sh2.uniforms.uCubeBrightOn) return;
        var v=(cb&&cb.value!==null&&cb.value!==undefined)?cb.value:1.0;
        var en=(state.__cubeBrightOn && cb && cb.source==='manifest' && Math.abs(v-1)>1e-9)?1.0:0.0;
        sh2.uniforms.uCubeBrightOn.value=en;
        sh2.uniforms.uCubeBright.value=(cb&&cb.value!==null&&cb.value!==undefined)?cb.value:1.0;
        if(mm.userData.__cubeBright) mm.userData.__cubeBright.on=en>0.5;
        n++; vals.push({prim:(cb?cb.prim:null), value:(cb?cb.value:null), source:(cb?cb.source:'absent'), on:en>0.5}); });
      try{_forceRender();_forceRender();}catch(e){}
      return JSON.stringify({cubeBright:(state.__cubeBrightOn?'on':'off'), mats:n, rows:vals,
        note:'值来源=manifest source_uniforms.u_cube_brightness；缺失不覆盖；默认 OFF'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  }
  window.__cubeBrightProbe=function(){ try{
    var out=[];
    if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.__cubeBright) return; var cb=mm.userData.__cubeBright;
      /* 自证字段（2026-09-19，task-45-1）：在 live 材质上读**真实的 uniform 值**与**编译源码里的接线痕迹**，
         使"开关是否真的进了 GPU 程序"不依赖任何外部推断。 */
      var u=(mm.userData.__sh&&mm.userData.__sh.uniforms)||{}, f=mm.userData.__frag||'';
      out.push({prim:cb.prim, value:cb.value, source:cb.source, on:!!cb.on,
                uOn:(u.uCubeBrightOn?u.uCubeBrightOn.value:null), uB:(u.uCubeBright?u.uCubeBright.value:null),
                fragDecl:(f.indexOf('uniform float uCubeBrightOn')>=0),
                fragBranch:(f.indexOf('q_env *= uCubeBright')>=0)}); });
    return JSON.stringify({switch:(state.__cubeBrightOn?'on':'off'), rows:out,
      unresolved:['envMapIntensity 实际失效（乘法在被覆写的 getIBLRadiance 体内）',
                  'u_lightmap_factor / u_env_day2night_exposure = 运行时逐帧 cbuffer ⇒ 无材质级源值',
                  'uIblScale 0.25 无源依据（已撤到 1.0）']});
  }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  /* ★★ 新增（2026-09-19，shader-auditor，task-45 第 2 项）：`u_rotate_angle`（IBL 采样方向）开关 + 探针。
     与 `__cubeBright` **同一定位**（mesh 循环之后 ⇒ manifest 应用过就存在），同一纪律：
       · 默认 OFF（`state.__iblRotSrcOn!==true`）⇒ 默认渲染与接线前**逐字节相同**（`uIblRot` 仍= `state.iblRot`，默认 0）；
       · 只改 uniform 值、不写第二状态源（探针从材质读回）；
       · 值只来自 manifest `source_uniforms.u_rotate_angle`（弧度）；`absent ⇒ 不覆盖`；
       · 与手动 `__iblParams({rot:N})` 的交互在返回值里显式暴露（`manual_rot`）。
     `fragRotRead` 自证：编译源码里确有 `cos( uIblRot )`（IBL 方向链的真实读取点）。 */
  if(!window.__srcRot){
    window.__srcRot=function(on){ try{
      state.__iblRotSrcOn=(on!==false);
      var n=0, rows=[];
      var manual=(state.iblRot===undefined?0.0:state.iblRot);
      if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
        if(!mm||!mm.userData) return; var ud=mm.userData, sh2=ud.__sh, rs=ud.__iblRotSrc;
        if(!sh2||!sh2.uniforms||!sh2.uniforms.uIblRotOn||!rs) return;
        var en=(state.__iblRotSrcOn && rs.source==='manifest' && rs.value!==null)?1.0:0.0;
        sh2.uniforms.uIblRotOn.value=en;
        sh2.uniforms.uIblRot.value=(en>0.5?rs.value:manual);
        rs.on=en>0.5; rs.manual_rot=manual;
        n++; rows.push({prim:rs.prim, value:rs.value, source:rs.source, on:en>0.5,
                        rot_used:sh2.uniforms.uIblRot.value, uRotOn:sh2.uniforms.uIblRotOn.value}); });
      try{_forceRender();_forceRender();}catch(e){}
      return JSON.stringify({srcRot:(state.__iblRotSrcOn?'on':'off'), mats:n, manual_rot:manual, rows:rows,
        note:'值来源=manifest source_uniforms.u_rotate_angle(rad)；缺失不覆盖（保持 state.iblRot）；默认 OFF'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  }
  window.__srcRotProbe=function(){ try{
    var out=[]; var manual=(state.iblRot===undefined?0.0:state.iblRot);
    if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.__iblRotSrc) return;
      var rs=mm.userData.__iblRotSrc, u=(mm.userData.__sh&&mm.userData.__sh.uniforms)||{}, f=mm.userData.__frag||'';
      out.push({prim:rs.prim, value:rs.value, source:rs.source, on:!!rs.on, manual_rot:manual,
                uRot:(u.uIblRot?u.uIblRot.value:null), uRotOn:(u.uIblRotOn?u.uIblRotOn.value:null),
                fragRotRead:(f.indexOf('cos( uIblRot )')>=0),
                fragCubeBrightDecl:(f.indexOf('uniform float uCubeBrightOn')>=0)}); });
    return JSON.stringify({switch:(state.__iblRotSrcOn?'on':'off'), manual_rot:manual, rows:out,
      unresolved:['源 cube 六面顺序/基变换与引擎采样约定（无 .cube 容器字段证据）',
                  '1110171 prim0/prim4（weapon）的 u_rotate_angle 引擎默认值（c159 无声明）']});
  }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  /* ★★ 新增（2026-09-19，shader-auditor，task-47）：晶体源 BRDF（metalness 插值）开关 + 探针。
     与 `__cubeBright` / `__srcRot` 同一定位（mesh 循环之后 ⇒ manifest 应用过就存在）与同一纪律：
       · **默认 OFF**（`state.__brdfSrcOn!==true`）⇒ `uBrdfOn=0` ⇒ `q_metal=0 / q_diffW=1` ⇒ 默认渲染与接线前**逐字节相同**；
       · 只改 uniform 值、不写第二状态源（探针从材质与 live uniform 读回）；
       · 缺失值不接线/不借值：`uCrystalMetal` 缺失 ⇒ 该 prim 永不接线；`uBaseMetal` 缺失 ⇒ 用现值 0.0；
       · **IBL 就绪门（关键）**：`ibl_ready` 为假（六面未齐 / 该 prim 仍 `pending_hidden`）时 **保持 0**
         ⇒ 金属化不会在没有环境可反射时发生（spec §4 风险 1）。
     `__brdfSrcProbe()` 另报编译源码自证：`fragDecl / fragDefault / fragAssign / fragDiffPatch / fragSpecPatch`
     与每材质的 `__patchLog`（`patchMulti` 命中数）。 */
  if(!window.__brdfSrc){
    window.__brdfSrc=function(on){ try{
      state.__brdfSrcOn=(on!==false);
      var n=0, rows=[];
      if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
        if(!mm||!mm.userData) return; var ud=mm.userData, sh2=ud.__sh, bs=ud.__brdfSrc;
        if(!sh2||!sh2.uniforms||!sh2.uniforms.uBrdfOn||!bs) return;
        var cube=sh2.uniforms.uCustomIbl&&sh2.uniforms.uCustomIbl.value;
        var faces=(cube&&cube.image)?cube.image.filter(Boolean).length:0;
        var pend=(ud.__pendingHidden===true);
        /* ★ 新增（2026-09-19，task-47，lead 裁决 D3）：**探针专用强制门**。
           只在 `__brdfForceNotReady(true)` 被显式调用时把就绪判据置假 ⇒ `uBrdfOn=0`（金属度保持 0）。
           **默认 false，不改变任何行为**：`state.__brdfForceNotReady!==true` 与原先逐字等价。
           用途：把"N3 窗口期负控"从代码路径证据升级为**实测证据**（强制假 ⇒ 开开关逐字节不变；
           解除强制并 settle ⇒ 同开关必须变）。不参与渲染决策之外的任何路径。 */
        var forced=(state.__brdfForceNotReady===true);
        var iblReady=(faces===6 && !pend) && !forced;
        var en=(state.__brdfSrcOn && bs.wireable===true && iblReady)?1.0:0.0;
        sh2.uniforms.uBrdfOn.value=en;
        bs.on=(en>0.5); bs.ibl_ready_live=iblReady; bs.faces_live=faces; bs.pending_hidden=pend; bs.force_not_ready=forced;
        n++; rows.push({prim:bs.prim, crystal_metal:bs.crystal_metal, base_metal:bs.base_metal, wireable:bs.wireable,
                        conflict:!!bs.conflict, ibl_ready:iblReady, faces:faces, pending_hidden:pend,
                        force_not_ready:forced, on:(en>0.5)});
      });
      try{_forceRender();_forceRender();}catch(e){}
      return JSON.stringify({brdf:(state.__brdfSrcOn?'on':'off'), mats:n, force_not_ready:(state.__brdfForceNotReady===true), rows:rows,
        note:'值来源=manifest source_uniforms；缺失不接线；IBL 未就绪 ⇒ 金属度保持 0；默认 OFF'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  }
  /* ★ 新增（2026-09-19，task-47，lead 裁决 D3）：**强制门（探针专用）**。
     `__brdfForceNotReady(true)` ⇒ `__brdfSrc` 把 `ibl_ready` 判为假（即使六面已齐），用于 N3 的实测负控；
     默认/解除后行为与接线前逐字等价（唯一读点在上面的 `forced`）。 */
  if(!window.__brdfForceNotReady){
    window.__brdfForceNotReady=function(on){ try{
      state.__brdfForceNotReady=(on===true);
      return JSON.stringify({force_not_ready:(state.__brdfForceNotReady===true),
        note:'探针专用：只影响 __brdfSrc 的就绪判据；默认 false；不改变渲染路径'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  }
  window.__brdfSrcProbe=function(){ try{
    var out=[], patches=[];
    if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.__brdfSrc) return;
      var bs=mm.userData.__brdfSrc, u=(mm.userData.__sh&&mm.userData.__sh.uniforms)||{}, f=mm.userData.__frag||'';
      (mm.userData.__patchLog||[]).forEach(function(p){ if(p&&String(p.chunk||'').indexOf('lights_physical')===0){
        patches.push({prim:bs.prim, chunk:p.chunk, tag:p.tag, ok:p.ok, hits:p.chunkHits, inc:p.includeHits, strs:p.strs}); } });
      out.push({prim:bs.prim, base_metal:bs.base_metal, crystal_metal:bs.crystal_metal,
                crystal_params_value:bs.crystal_params_value, conflict:!!bs.conflict, wireable:!!bs.wireable,
                base_specular:bs.base_specular, crystal_specular:bs.crystal_specular,
                value_source:bs.value_source, ibl:bs.ibl, ibl_ready_at_build:bs.ibl_ready_at_build,
                on:!!bs.on, uBrdfOn:(u.uBrdfOn?u.uBrdfOn.value:null),
                uBaseMetal:(u.uBaseMetal?u.uBaseMetal.value:null), uCrystalMetal:(u.uCrystalMetal?u.uCrystalMetal.value:null),
                fragDecl:(f.indexOf('uniform float uBrdfOn')>=0),
                fragDefault:(f.indexOf('float q_metal = 0.0')>=0),
                fragAssign:(f.indexOf('q_metal = mix(0.0, clamp(mix(uBaseMetal')>=0),
                fragDiffPatch:(f.indexOf('material.diffuseColor = diffuseColor.rgb * q_diffW')>=0),
                fragSpecPatch:(f.indexOf('material.specularColor = mix( vec3( 0.079956 ), diffuseColor.rgb, q_metal )')>=0),
                patchState:mm.userData.__patchState||null});
    });
    return JSON.stringify({switch:(state.__brdfSrcOn?'on':'off'), rows:out, patches:patches,
      unresolved:['spec 因子本轮不注入（两目标皮肤 spec 恒 1）',
                  '1110171 prim6 u_crystal_roughness=0.12 无消费点（roughness 恒 1.0 / ParamMap.R）',
                  'u_base_metallic / u_base_specular 缺失项的源侧端点值未定证 ⇒ 用现值、不借值',
                  '源 cube 六面顺序/基变换未定证']});
  }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  /* ★★ 新增（2026-09-19，shader-auditor，task-59 (c)）：**源 cube 重建的环境辐照** 开关 + 探针。
     与 `__brdfSrc` 同一定位与纪律，但性质不同 ⇒ **必须显式标近似**（`approx:true`）：
       · 源侧环境辐照 = `u_env_sh`(cb1[148..154]) + `u_ambient×u_char_ambient`(cb1[0]/[284])
         + `t_realtime_env_spec`(t8) × …（asm L564-578 / L626-628）—— **全是运行时 cbuffer ⇒ 接不上**；
       · 本实现用**已在用的源 cube**（`uCustomIbl`，逐 prim 来自 manifest `t_custom_ibl` 的六面）重建它，
         采样固定高 mip（`uIrrLod`，默认 5.0）近似半球积分，返回 `π·L`。
       ⇒ 报告与探针都写 **`reconstruction approximation`**，**不是源值**。
     纪律：默认 OFF（`state.__iblIrrSrcOn!==true` ⇒ `uIrrOn=0` ⇒ 函数返回 0 ⇒ 默认逐字节同接线前）；
     就绪门与 `__brdfSrc` 相同（`faces===6 ∧ !pending_hidden ∧ !force_not_ready`，后者为 D3 探针专用）；
     `__iblIrrSrc(true,{lod,scale})` 可选显式改重建参数（会被写进返回值与探针，便于复现）。 */
  if(!window.__iblIrrSrc){
    window.__iblIrrSrc=function(on,opts){ try{
      opts=opts||{};
      state.__iblIrrSrcOn=(on!==false);
      if(opts.lod!==undefined)   state.__iblIrrLod=Number(opts.lod);
      if(opts.scale!==undefined) state.__iblIrrScale=Number(opts.scale);
      var lod=(state.__iblIrrLod===undefined?5.0:Number(state.__iblIrrLod));
      var scale=(state.__iblIrrScale===undefined?1.0:Number(state.__iblIrrScale));
      var n=0, rows=[];
      if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
        if(!mm||!mm.userData) return; var ud=mm.userData, sh2=ud.__sh, is=ud.__iblIrrSrc;
        if(!sh2||!sh2.uniforms||!sh2.uniforms.uIrrOn||!is) return;
        var cube=sh2.uniforms.uCustomIbl&&sh2.uniforms.uCustomIbl.value;
        var faces=(cube&&cube.image)?cube.image.filter(Boolean).length:0;
        var pend=(ud.__pendingHidden===true), forced=(state.__brdfForceNotReady===true);
        var iblReady=(faces===6 && !pend) && !forced;
        var en=(state.__iblIrrSrcOn && iblReady)?1.0:0.0;
        sh2.uniforms.uIrrOn.value=en;
        sh2.uniforms.uIrrLod.value=lod;
        sh2.uniforms.uIrrScale.value=scale;
        is.on=(en>0.5); is.lod=lod; is.scale=scale; is.ibl_ready_live=iblReady; is.faces_live=faces;
        n++; rows.push({prim:is.prim, ibl:is.ibl, lod:lod, scale:scale, ibl_ready:iblReady, faces:faces,
                        pending_hidden:pend, force_not_ready:forced, on:(en>0.5)});
      });
      try{_forceRender();_forceRender();}catch(e){}
      return JSON.stringify({irr:(state.__iblIrrSrcOn?'on':'off'), approx:true,
        approx_basis:'用已绑定的源 cube（uCustomIbl）重建环境辐照；源为 u_env_sh/u_ambient×u_char_ambient/t_realtime_env_spec（运行时 cbuffer，接不上）',
        lod:lod, scale:scale, mats:n, rows:rows,
        note:'irradiation = π·L(cube, uIrrLod)；默认 OFF；就绪门同 __brdfSrc'});
    }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  }
  window.__iblIrrProbe=function(){ try{
    var out=[];
    if(state.scene) state.scene.traverse(function(o){ if(!o.isMesh) return; var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.__iblIrrSrc) return;
      var is=mm.userData.__iblIrrSrc, u=(mm.userData.__sh&&mm.userData.__sh.uniforms)||{}, f=mm.userData.__frag||'';
      out.push({prim:is.prim, ibl:is.ibl, approx:true, lod:is.lod, scale:is.scale, on:!!is.on,
                ibl_ready_at_build:is.ibl_ready_at_build,
                uIrrOn:(u.uIrrOn?u.uIrrOn.value:null), uIrrLod:(u.uIrrLod?u.uIrrLod.value:null), uIrrScale:(u.uIrrScale?u.uIrrScale.value:null),
                fragIrrFn:(f.indexOf('vec3 q_iblIrrSrc(')>=0),
                fragIrrMix:(f.indexOf('iblIrradiance += mix( getIBLIrradiance( geometryNormal ), q_iblIrrSrc( geometryNormal ), uIrrOn );')>=0),
                fragGateKept:(f.indexOf('#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )')>=0),
                approx_basis:is.approx_basis});
    });
    var lod=(state.__iblIrrLod===undefined?5.0:Number(state.__iblIrrLod));
    var scale=(state.__iblIrrScale===undefined?1.0:Number(state.__iblIrrScale));
    return JSON.stringify({switch:(state.__iblIrrSrcOn?'on':'off'), approx:true, lod:lod, scale:scale, rows:out,
      unresolved:['源 SH 系数 u_env_sh（cb1[148..154]）与 u_ambient/u_char_ambient（cb1[0]/[284]）为运行时 cbuffer ⇒ 不可得',
                  't_realtime_env_spec(t8) 在本皮肤是否有内容未定证（绑定 2/15 变体）',
                  'uIrrLod=5.0 / uIrrScale=1.0 是**重建参数**（非源值），已在返回值与报告显式标注']});
  }catch(e){ return 'ERR '+((e&&e.message)||e); } };
  return rep;
}

  /* ══════════════════════════════════════════════════════════════════════════════════════════
     ★★★ 新增（2026-09-20，EMISTOGGLE）：自发光**两档开关**（默认全 false）+ 只读探针 + 页面控件。

     背景（已定证，见 EMISTOGGLE_20260920.md）：自发光在本 viewer 里此前是**载体存在但被硬清零**
     （applyMaterialLayers 内对 matParams 的三处无条件 `emissive=(0,0,0)/emissiveIntensity=0/emissiveMap=null`）
     ⇒ 源里真实存在的 `u_emissive_strength` 从未进入画面。本块**不删**那段硬清零（enabled:false 时逐字保持现状），
     而是在**材质建立之后**按开关追加覆写。

     两档**互不耦合**、可各自单开：
       A1 `emissive_source`  仅 **prim3**：`emissiveMap=该 prim 的 albedo 贴图`、`emissiveIntensity=源值 0.7`、
                              `emissive=[1,1,1]`。源依据 = `weapon\001348.c159` @4198 `u_emissive_strength=0.7`
                              （全文件唯一 0.7）+ @4173 `u_emissive_color_saturation=[1,1,1,0.2902]`（**仅 M3/prim3**）。
                              颜色取 `[1,1,1]` 的依据：`u_emissive_strength` 是**标量**，源 shader 里以
                              `mul r4.xyz,r4.xyzx,cb0[133].xxxx` 消费（标量乘自发光色）；标量档不改变色相
                              ⇒ 乘性颜色取中性白。`u_emissive_color_saturation` 是**饱和处理**、`.a=0.2902` 语义未定
                              （未定证）⇒ 本轮**不实现**，不作为颜色来源（否则等于把未定语义当依据）。
                              证据等级 = `source_present_value_unreadable`（c159 无 index 字段、运行时排列绑定不可判）；
                              **不得**升级写成 `source_verified`。开启时按钮上明确标「近似」。
       A2 `emissive_approx`  恢复既有全局载体 `material_layers.global_rig.emissive_gain`（0.0 → 0.25 可调）：
                              语义 = **基色贴图作自发光贴图的全局增益**（近似源 SV_Target0）；tier=approximate。
      A1+A2 同时开时 A1 在 prim3 上**优先**（prim3 取源值 0.7，其余 prim 走全局增益）。

     ★ 红线（本块逐条遵守）：不改 exposure / ACES / toneMapping / bloom / 灯光 / 环境强度；
       不替换任何贴图（A1 用的是该 prim 自己的 albedo，A2 用基色贴图）；不跨材质复制（A1 只 prim3）；
       不把 `source_present_value_unreadable` 写成 `source_verified`。
     ══════════════════════════════════════════════════════════════════════════════════════════ */
  state.__emissiveState={source:{enabled:false},approx:{enabled:false},applied_at:null,diag:[]};
  /* ★ 关键不变量（2026-09-20，EMISTOGGLE）：这两个运行期 enabled 一经建立就**永远是权威**，
     且每次 applyEmissiveToggles 结束时会把它们原样写回 state.__emissiveState；
     缺键仍安全（emisResolve 在缺键时才回落到 viewer.json 的初值）。
     本行只是把「运行期权威已建立」这件事显式化，防止将来有人把键删掉后开关静默失效。 */
  state.__emissiveState.source.enabled=false;
  state.__emissiveState.approx.enabled=false;
  function emisViewerConfig(){ try{ return state.config||((typeof selectedState==='function'&&selectedState())||{}); }catch(e){ return {}; } }
  function emisSelectedCfg(){
    var s=null; try{ if(typeof selectedState==='function') s=selectedState(); }catch(e){}
    return (s&&s.material_layers)||(emisViewerConfig().material_layers)||{};
  }
  function emisNum(v,d){ var n=Number(v); return Number.isFinite(n)?n:d; }
  function emisResolve(){
    var ml=emisSelectedCfg();
    var s=Object.assign({enabled:false,prim:3,strength:0.7,
        tier:'source_present_value_unreadable',
        note:'源值来自 001348.c159@4198（仅 M3/prim3）；运行时排列绑定未定证 ⇒ 默认关，开启时标近似'},
      ((ml.emissive_source)||{}));
    var topMl=(emisViewerConfig().material_layers)||{};
    var ap=Object.assign({enabled:false,gain:0.25,tier:'approximate'},
      ((ml.global_rig||{}).emissive_approx||{}),
      ((topMl.global_rig||{}).emissive_approx||{}),
      ((topMl.emissive_approx)||{}));
    /* gain 来源登记：优先读 emissive_approx.gain（本开关的权威键，默认 0.25）；
       仅在**未声明**时回落到历史载体 global_rig.emissive_gain（本资产顶层 = 0.0 = 现状）。 */
    var gainSrc='emissive_approx.gain';
    if(ap.gain===undefined||ap.gain===null){
      var raw=(ml.global_rig||{}).emissive_gain;
      if(raw===undefined||raw===null) raw=(topMl.global_rig||{}).emissive_gain;
      ap.gain=emisNum(raw,0.0); gainSrc='global_rig.emissive_gain(legacy)';
      ap.gain_from_legacy=raw;
    }
    /* ★★ 修正（2026-09-20，EMISTOGGLE 第一次实测证伪后的修正）：
       运行期 state.__emissiveState 的 enabled 才是**权威**，viewer.json 的 enabled 只作**初值**。
       原实现在这里无条件用配置覆盖 ⇒ 每调一次 applyEmissiveToggles 都把 UI/探针刚打开的开关
       重新按 viewer.json 的 `false` 冲掉（实测：调 __emissiveA1(true) 后 diag 全 mode=none、
       四档截图 sha16 完全相同）。现改为：运行期键存在就用运行期，否则才取配置初值。
       默认（未提交过开关）二者同为 false ⇒ 现状不变。 */
    if(state.__emissiveState&&state.__emissiveState.source&&state.__emissiveState.source.enabled!==undefined)
      s.enabled=!!state.__emissiveState.source.enabled;
    if(state.__emissiveState&&state.__emissiveState.approx&&state.__emissiveState.approx.enabled!==undefined)
      ap.enabled=!!state.__emissiveState.approx.enabled;
    /* ★ 诊断用运行期强制值（**不写文件、不影响默认**）：`window.__emisForceStrength=<v>` 可把 A1 的
       源值档强度临时改成 v，用于「源值 0.7 是否把饱和度/gold 拉回游戏水平」的只读扫描。
       未设置时逐字用 viewer.json 的 0.7。 */
    if(window.__emisForceStrength!==undefined&&window.__emisForceStrength!==null){
      var fs=Number(window.__emisForceStrength);
      if(Number.isFinite(fs)) s.strength=fs, s.strength_forced_by='window.__emisForceStrength';
    }
    return {s:s,ap:ap,gainSrc:gainSrc,prim:emisNum(s.prim,3),srcStrength:emisNum(s.strength,0.7)};
  }
  function emisPatchMaterial(rec,idx,rs){
    try{
      var m=rec.mat, ud=(m&&m.userData)||{}, ch=ud.chain||{};
      if(!ch.prim&&ch.prim!==0){ if(typeof console!=='undefined'&&console.warn) console.warn('emissive: material without chain.prim',idx); }
      var p=emisNum(ch.prim,NaN), base=rec.base, gain=rs.ap.gain;
      var a1=(!!rs.s.enabled && Number.isFinite(p) && p===rs.prim);
      var a2=(!!rs.ap.enabled && Number.isFinite(gain) && gain>0);
      /* ★ 实地校正（2026-09-20，EMISTOGGLE 第一次实测证伪后的修正）：
         默认页的显示材质**不是** applyMaterialLayers 里那批 `MeshPhysicalMaterial` ——
         该函数在源链生效时 L3869(`applied>0`) **早退**，本循环根本不执行（实测探针
         `emissive_state.applied_at=null / diag=[]`，四档截图 sha16 完全相同）。
         真正显示的是 `applyNeoxManifest` 建的链材质（L2076/2105，末尾 L3450 `mesh.material=m`）。
         故自发光改用**就地改活材质**：A1 直接复用该 prim 自身的 `material.map`（= 该 prim 的
         源 albedo 贴图本身，wrap/aniso/色彩空间逐字相同，**不加载第二份、不替换贴图**）
         作为 emissiveMap；A2 同理对全部 prim 用各自 map。两处入口都调本函数。 */
      var mapTex=(base&&base.map)||m.map||null;
      var mode='none', inten=0;
      if(a1){ mode='A1_source'; inten=rs.srcStrength; }
      else if(a2){ mode='A2_approx'; inten=gain; }
      var prev=ud.__emissive;
      if(mode==='none'){
        m.emissiveIntensity=0;
        if(m.emissive&&m.emissive.setRGB) m.emissive.setRGB(0,0,0);
        m.emissiveMap=null;
      } else {
        if(m.emissive&&m.emissive.setRGB) m.emissive.setRGB(1,1,1);   // 中性乘性色（依据见块首）
        m.emissiveMap=mapTex;                                          // 该 prim **自己**的 albedo；不跨材质复制
        m.emissiveIntensity=inten;
      }
      var out={prim:p,mode:mode,intensity:inten,map:!!mapTex,
               strength:(mode==='A1_source')?rs.srcStrength:null,
               gain:(mode==='A2_approx')?gain:null,
               gain_source:(mode==='A2_approx')?rs.gainSrc:null,
               tier:(mode==='A1_source')?rs.s.tier:((mode==='A2_approx')?rs.ap.tier:null),
               map_source:(mode==='none')?null:'material.map(该prim自身源albedo贴图，未替换/未新载)'};
      ud.__emissive=out;
      /* 只在**状态真变化**时重编译（默认全关时 prev 恒 none、mode 恒 none ⇒ 一次也不编译，现状不改） */
      var changed=(!prev)||(prev.mode!==out.mode)||(prev.intensity!==out.intensity)||(prev.map!==out.map);
      if(changed){ try{ m.needsUpdate=true; }catch(e){} }
      out.needsUpdate=!!changed;
      return out;
    }catch(e){ return {prim:null,mode:'ERR',err:String((e&&e.message)||e)}; }
  }
  function applyEmissiveToggles(root){
    if(!root) return [];
    var rs=emisResolve(), diag=[];
    root.traverse(function(o){
      if(!o.isMesh) return;
      var mm=o.material; if(Array.isArray(mm)) mm=mm[0]; if(!mm) return;
      var ud=mm.userData||{};
      if(!ud.chain&&!ud.neox) return;                      // 只碰源链材质，不碰诊断材质
      diag.push(emisPatchMaterial({mat:mm,base:(ud.chain&&ud.chain.albedo)||null},null,rs));
    });
    state.__emissiveState={source:rs.s,approx:rs.ap,gain_source:rs.gainSrc,
      effective:{A1_on:!!rs.s.enabled,prim:rs.prim,strength:rs.srcStrength,
                 A2_on:!!rs.ap.enabled,gain:rs.ap.gain},
      applied_at:(new Date()).toISOString(),
      diag:diag,summary:{meshes:diag.length,
        a1:(diag.filter(function(d){return d.mode==='A1_source';})||[]).length,
        a2:(diag.filter(function(d){return d.mode==='A2_approx';})||[]).length}};
    return diag;
  }
  function emisRun(){
    try{ if(state.root) return applyEmissiveToggles(state.root); }catch(e){}
    return null;
  }
  function applyMaterialLayers(root,callOpts){ callOpts=callOpts||{};   // ★ 显式参数：{sourceIblEnabled, sourceIblMode}
    // ─────────────────────────────────────────────────────────────
    // 默认模式 = source_texture_preview：只忠实显示 manifest 的源颜色贴图。
    // 源贴图预览，NeoX 光照尚未完成 —— 非最终材质，不得冒充。
    // 仅 ?lab=1 才走实验链（自定义 IBL / 三态验收），失败不得影响默认页面。
    // ─────────────────────────────────────────────────────────────
    /* ★ 改动（2026-09-18，shader-auditor，task-18）：「清污块」改为**两入口共用**。
       原条件 `if(!LAB && !callOpts.forceLab)` 让 `?lab=1` **整块跳过** ⇒ lab 页额外保留了
       viewer 的 studio rig（HemisphereLight 0.8 + DirectionalLight 1.5/0.5）、`scene.environment`
       与 bloom strength（实测 1110024：board `bloom:false` vs lab `bloom:true`）。
       即两入口从来不是同一渲染：board = rig 关 + 源 cube 辐射；lab = rig 开 + 源 cube 辐射。
       源级依据：NeoX 管线**没有** three 的 Hemisphere/Directional rig，环境辐射来自
       `t_custom_ibl`（逐材质，见 L1167-1199 的 radiance 覆写）⇒ **board 一侧才是源忠实的**，
       lab 页的 rig 属 viewer 额外叠加（这不是"lab 更真"，而是 lab 多算了一遍环境）。
       现把清污块提到两入口共用；仅「链生效即早退/回退预览」仍限默认页，lab 仍可继续走实验链。 */
    const CLEAR_ALWAYS=true;
    const LAB=(function(){try{return new URLSearchParams(location.search).get('lab')==='1';}catch(e){return false;}})();
    if(CLEAR_ALWAYS){
      // 清除旧污染：关灯 / 关环境 / 关自发光 / 曝光=1 / 关后处理强度
      try{
        state.THREE.ColorManagement.enabled=true;
        if(state.scene) state.scene.environment=null;
        /* ★★ Lead 20260920 缺陷修复（task-11）：本行原为**无条件** `o.visible=false`。
           three 的 `projectObject()` 对 `object.visible===false` **直接 return** ⇒ 灯既不入
           `currentRenderState.pushLight`（⇒ `NUM_DIR_LIGHTS=0`，直接光项在编译期被整段删掉），
           也不入 `currentRenderState.pushShadow`（⇒ **阴影贴图根本不渲染**）。
           这解释了此前两个已实测但无解释的事实：
             ① 三盏灯强度 ×10 而武器像素零变化（AB_brightness_lightx10.json：mask p50 0.2480 不变、画布内 0 像素差）；
             ② `key_shadow:true` 的 lightshadow 变体与基线**零像素差**
                （AB_brightness_light.json、PROBE_dirlight_root_20260920.json 的 lightColors 读数）。
           现按开关放行：`state.__rigOn` 为真时保持灯可见；缺省 false ⇒ 与改动前逐字节一致。 */
        if(state.scene) state.scene.traverse(function(o){ if(o.isLight) o.visible=!!state.__rigOn; });
        /* ★ 修正（2026-09-17）：该"清除旧污染"块是为**无光照预览模式**写的，
           会把渲染器创建时的 ACESFilmicToneMapping 一并关掉。现在源链已接管渲染
           （见下方回退语义），继续强制 NoToneMapping 会让成品缺少 tone mapping 环节 ——
           实测武器区 p50/p95 仅为参考图的一半（0.115/0.444 vs 0.222/0.579）。
           故：**仅当源链未生效（即真的走无光照预览）时**才关 tone mapping；
           链生效时保留渲染器自身的 ACES 与配置曝光。不新引入任何曲线/系数。 */
        /* ★★ 再修（2026-09-18）：守卫本身在，但**时序**有洞 ——
           首次 applyMaterialLayers 调用发生在 state.neoxReport 置位**之前**（见 loadSelectedState 的调用顺序），
           那一次守卫不成立 ⇒ toneMapping 被强制关；而链生效后的那次调用**只跳过、不恢复** ⇒
           生产路径实测 toneMapping 仍为 0（NoToneMapping）。这会让成品缺少 tone mapping 环节。
           现改为**双向**：链生效 → **显式恢复渲染器自身的创建值**（L187 即 ACESFilmic，非新引入）；
           链未生效 → 才关。 */
        if(state.renderer){
          if(state.neoxReport && state.neoxReport.applied > 0){
            /* ★ 改动（2026-09-18，task-29）：第二处写死的 ACESFilmic 改为**配置驱动**（默认同值），
               exposure 走 numCfg（0 合法）。语义不变：链生效 ⇒ 恢复「创建时的配置值」。 */
            state.renderer.toneMapping=toneMapOf(state.THREE,state.config||{});
            state.renderer.toneMappingExposure=numCfg((state.config||{}).exposure,1);
          } else {
            /* 链未生效 = 无光照源贴图预览路径：固定 NoToneMapping（原行为，不动） */
            state.renderer.toneMapping=state.THREE.NoToneMapping;
            state.renderer.toneMappingExposure=1.0;
          }
        }
        if(state.renderer) state.renderer.outputColorSpace=state.THREE.SRGBColorSpace;
        /* ★ 试验后回退（2026-09-17）：曾按 viewer.json 的 global_rig.bloom(strength 0.55) 在链生效时
           保留 bloom，想补上参考图的辉光。**实测无收益且略降**：
             无 bloom 武器区 p95=0.444 / p50=0.115  →  开 bloom p95=0.423 / p50=0.117
           高光反而变暗，说明 composer 通道改变了输出链路而非单纯加辉光。
           按纪律「测不出收益的改动不留」，恢复为无条件关闭（原行为）。
           辉光缺口的真正来源仍未定论，见 03拆包产物\折射链去向更正与最终结论_20260917.md 第六节。 */
        if(state.bloom) state.bloom.strength=0;
        if(state.composer&&state.composer.passes) state.composer.passes.forEach(function(p){ if(p&&typeof p.strength==='number') p.strength=0; });
      }catch(e){}
      /* ★ 改动（2026-09-16）—— 默认页不再无条件用「无光照源贴图预览」覆盖源链材质。
         原实现把 applyNeoxManifest 刚装好的链材质整体替换为 MeshBasicMaterial，
         使四轮修复后的源链在默认页完全不可见（用户看到的仍是蓝紫平贴图）。
         现改为**回退语义**：源链成功装载（neoxReport.applied>0）则保留链材质；
         仅当链未生效时才退回无光照预览，保证任何情况下页面都有东西可看。 */
      /* ★ 改动（2026-09-18，task-18）：清污块到此结束（上面已无条件执行）。
         下面「链生效即保留链材质并早退」仍**只限默认页**；`?lab=1` 继续往下走实验链
         （自定义 IBL / 三态验收），但其光照/环境状态此刻已与默认页一致 ⇒ 两入口同一套渲染基线。 */
      }
      if(!LAB && !callOpts.forceLab){
      if(state.neoxReport && state.neoxReport.applied > 0){
        /* ★ 新增（2026-09-20，EMISTOGGLE）：早退前把两档自发光开关重新应用到活链材质
           （默认全 false ⇒ 此处什么也不改；开启后本函数每次被调都会重新落值）。 */
        try{ emisRun(); }catch(e){}
        try{_forceRender();}catch(e){}
        return 0;                       // 0 = 本次未做预览替换，链材质保持
      }
      // —— 以下为「源链未生效」时的回退预览 ——
      /* ★ 改动（2026-09-18，shader-auditor，task-13 C）：删除跨皮肤硬编码表。
         原表 `SRC={"0":"src_tex/012_b_m.png","1":"src_tex/012_a.png",...,"4":"src_tex/010_b_m.png",...}`
         写死的是 **1110171 的族号** ⇒ 链未生效时其它皮肤会请求不存在的 012_b_m/012_a/010_b_m
         （1110129 实测 3 条 404）⇒ `MeshBasicMaterial(map=null, toneMapped:false)` ⇒ **第二条独立纯黑剪影路径**。
         现改为**逐 prim 从 manifest 派生**，规则与上方 L1006-1007（albedoSlot）完全一致、不引入新的人工映射：
           · weapon prim  ⇒ textures.Tex0.file
           · crystal prim ⇒ textures.t_basecolor.file || textures.Tex0.file
           · 该 prim 无对应槽 ⇒ null（如实留空，userData.__srcTexFile=null）
         **禁止回落到别的皮肤/别的族号**。取数来源：`state.neoxManifest.primitives`（applyNeoxManifest
         在 L1874 置位 state.neoxManifest；本函数序中 root.traverse 的 mesh 序与 applyNeoxManifest
         的 meshes 序同源，故 prim 索引一一对应）。 */
      const mPrims=(state.neoxManifest&&state.neoxManifest.primitives)||null;
      const srcForPrim=function(pi){
        try{
          const pr=mPrims&&mPrims[pi]; if(!pr) return null;
          const TX=pr.textures||{};
          const fileOf=function(k){ const e=TX[k]; if(!e) return null;
            const lf=e.local_file||e.logical||null; if(!lf) return null;
            return (String(lf).indexOf('src_tex/')===0)?lf:neoxPng(lf); };
          return (pr.shader_kind==='weapon') ? fileOf('Tex0')
                                             : (fileOf('t_basecolor')||fileOf('Tex0'));
        }catch(e){ return null; }
      };
      const TL=new state.THREE.TextureLoader();
      let n=0, ki=-1;
      root.traverse(function(obj){
        if(!obj.isMesh) return; ki++;
        const f=srcForPrim(ki);
        let t=null;
        if(f){ t=TL.load((state.modelDir||'')+f); t.colorSpace=state.THREE.SRGBColorSpace;
               t.wrapS=t.wrapT=state.THREE.RepeatWrapping; t.flipY=false; }
        const sm=obj.userData.__srcMat, side=(sm&&sm.side!==undefined)?sm.side:0;
        /* ★★ 修复（2026-09-19，shader-auditor，task-62/D1）：**删掉构参里的 `emissive:0x000000, emissiveIntensity:0`**。
           `MeshBasicMaterial` **没有** `emissive` / `emissiveIntensity` 属性（它们属于 MeshStandard/Physical）⇒
           three 的 `Material.setValues()` 会打印 `THREE.Material: 'emissive' … is not a property of THREE.MeshBasicMaterial.`，
           每个 mesh 两条（1110177 三个 prim ⇒ 实测 6 条）。
           这两个键**本来就被 three 丢弃**（`m.emissive === undefined`；`__matDump()` 由此恒读到 `null`）⇒
           **删除不改变任何渲染语义**：材质构造参数其余逐字不变，`__previewMode/__srcTexFile/__label` 也不变。
           触发时机：`state.neoxReport.applied===0` 时的**回退预览**（含链就绪前的窗口期），随后被链材质替换。 */
        obj.material=new state.THREE.MeshBasicMaterial({map:t,color:0xffffff,toneMapped:false,fog:false,side:side});
        obj.material.userData.__previewMode='source_texture_preview';
        obj.material.userData.__srcTexFile=f||null;
        obj.material.userData.__label='源贴图预览，NeoX 光照尚未完成';
        obj.visible=true; n++;
      });
      try{_forceRender();}catch(e){}
      return n;
    }

    // 源驱动：params 来自 c159_pair.py 解析出的 c159 参数（viewer.json.material_layers.per_submesh）
    // 全局 rig 统一；材质级差异只用 u_cube_brightness；晶体表达仍为 approximate
    const THREE=state.THREE,sel=(typeof selectedState==='function'?selectedState():null)||{};
    const ml=sel.material_layers||(state.config||{}).material_layers;
    if(!THREE||!root||!ml)return 0;
    if(ml.global_rig&&Number.isFinite(Number(ml.global_rig.exposure))&&state.renderer){state.renderer.toneMappingExposure=Number(ml.global_rig.exposure);}
    try{if(typeof ensureComposer==='function'){ensureComposer().then(function(){renderOnce();});}}catch(e){}
    // 实验开关：只用于受控对照，默认全开=当前行为；不修改 viewer.json 里的源参数
    // 实验开关：只用于受控对照，默认全开=当前行为；不修改 viewer.json 里的源参数
    // 粗糙度模式由 global_rig.roughness_mode 驱动：
    //   'diagnostic_constant' = 统一诊断常数（不称源粗糙度；默认）
    //   'source_R_unproven'   = 沿用把 ParamMap.R 当粗糙度（未证假设）
    const __roughMode=((ml.global_rig||{}).roughness_mode)==='source_R_unproven'?'source_R_unproven':'neutral';
    const ex=state.expFlags||{baseColor:true,subsurfaceEmissive:true,onlySubmesh:null,roughnessMode:__roughMode,envBright:false,envBlend:0.0,idMap:false,unlitTex:false,whiteUnlit:false};
    // 粗糙度来源：'source_R_unproven'=沿用把 ParamMap.R 当粗糙度（未证）；'neutral'=固定中性常数（诊断用，不拟合）
    const ROUGH_NEUTRAL=0.5;
    // ── 源指令接入（安全版）：[393-401] 环境项 envSpec = mix( (env.rgb*env.a*16)^2, min(该值,1.5)*0.2998, cb1[86].z )
    //    约束：① 仅在锚点存在时注入 ② 不引用未声明标识（通过 onBeforeCompile 结尾钩子改 outgoingLight）
    //    ③ 注入后由渲染结果自检 → 若画面为空则视为失败，由外部脚本回退
    const ENV_BRIGHT_MUL=16.0, ENV_BRIGHT_CLAMP=1.5, ENV_BRIGHT_FLOOR=0.299805;
    // 源指令锚点：getIBLRadiance 内的 "reflectVec" 采样行（唯一；空白无关匹配）
    // 源指令锚点：getIBLRadiance 内的 envMap 采样行
    const ENV_ANCHOR=/#include <opaque_fragment>/;
    // ★ 逐条实现 asm d982 531-550：自定义 samplerCube，不走 Three envMap / 不走 PMREM
    const SRC_ENV_GLSL=[
      '/* 源 IBL：直接叠加到最终输出，不依赖 Three 的 USE_ENVMAP 路径 */',
      'float _rgh = max(uSrcRough, 0.0019);',
      'float _lod = 5.0 + 1.2 * log2( _rgh );',                                  /* asm 537-539 */
      'vec3 _Rv = reflect( normalize( vViewPosition ), normal );',                /* 源反射入射方向 */
      'float _c = cos(uIblRot), _sn = sin(uIblRot);',                            /* asm 531 sincos cb0[7].w → XZ 平面 = 绕 Y 轴旋转 */
      'vec3 _Rs = vec3( _Rv.x*_c + _Rv.z*_sn, _Rv.y, -_Rv.x*_sn + _Rv.z*_c );',   /* asm 535-536,540 — P1 修复(2026-09-17,T2)：原 sin/cos 次序互换，rot=0 会被偏航 -90° */
      'vec4 _sm = textureLod( uSrcIbl, _Rs, _lod );',                            /* asm 541 sample_l */
      'vec3 _L = pow( _sm.rgb * _sm.a * 16.0, vec3(2.0) ).xyz;',                 /* asm 542-544 (RGB*A*16)^2 */
      'vec3 _Lc = min( _L, vec3(1.5) );',                                        /* asm 545 */
      'vec3 _env = _L + uIblMix * ( _Lc * 0.299805 - _L );',                     /* asm 546-548 */
    
  /* ★ 移除（2026-09-18，用户令 Task2）：口径禁止对 outgoingLight 额外叠加。
     该行是旧口径实现，已被 getIBLRadiance 覆写（只产 radiance）取代。 */
    ].join('\n\t\t\t');
    const applySourceEnvBright=(mat,primIdx,mode)=>{
  /* ★★ 停用（2026-09-18，用户令 Task2）：这是旧口径的"环境叠加"实现，会写 `outgoingLight += …`，
     与"只用源 cube 替换 radiance 输入"的口径冲突；它此前仅靠 applyMaterialLayers 的早退被绕过，
     一旦链未生效就会激活 → **环境被算两次**。现全面停用，生产与诊断路径都不得再进入。
     环境贡献的唯一执行路径 = getIBLRadiance 覆写。 */
  if(mat&&mat.userData){ mat.userData.__srcEnvBright='removed_by_policy_20260918'; }
  return;
      state.__cSEB=(state.__cSEB||0)+1;
      const isC=(typeof primIdx==='number')?CUBE_FOR_PRIM(primIdx):null;
      if(!isC){ if(mat&&mat.userData) mat.userData.__srcEnvBright='no_source_cube'; return; }
      const ct=srcCube(isC);
      const prev=mat.onBeforeCompile;
      mat.onBeforeCompile=function(shader,...rest){
        if(prev)prev.call(this,shader,...rest);
        let fs=String(shader.fragmentShader||'');
        const ANCH='#include <opaque_fragment>';
        if(fs.indexOf(ANCH)<0){ if(mat.userData) mat.userData.__srcEnvBright='anchor_missing'; return shader; }
        fs=fs.replace(ANCH, SRC_ENV_GLSL+'\n\t'+ANCH);   // ★ 在 include 之前，normal/vViewPosition/outgoingLight 均在作用域内
        shader.uniforms.uSrcIbl={value:ct};
        shader.uniforms.uSrcRough={value:Number.isFinite(matParams&&matParams.roughness)?matParams.roughness:0.5};
        shader.uniforms.uIblRot={value:(state.iblRot!==undefined?state.iblRot:0.0)};
        shader.uniforms.uIblMix={value:(state.iblMix!==undefined?state.iblMix:0.0)};
        shader.uniforms.uIblScale={value:(state.iblScale!==undefined?state.iblScale:1.0)};
        shader.uniforms.uIblStrength={value:(state.iblStrength!==undefined?state.iblStrength:1.0)};
        shader.fragmentShader='uniform samplerCube uSrcIbl;\nuniform float uSrcRough;\nuniform float uIblRot;\nuniform float uIblMix;\nuniform float uIblScale;\nuniform float uIblStrength;\n'+fs;
        state.__cOBV=(state.__cOBV||0)+1;
        if(mat.userData){ mat.userData.__srcEnvBright='injected'; mat.userData.__srcIbl=isC; mat.userData.__sh=shader; mat.userData.__frag=shader.fragmentShader; }
        return shader;
      };
      mat.customProgramCacheKey=()=> 'srcibl_'+isC;
      state.__srcIblMats=state.__srcIblMats||[]; state.__srcIblMats.push(mat);
    };
    const CUBE_OF={0:'qiangpi',4:'qiangpi',1:'car_studio01',2:'car_studio01',3:'car_studio01',5:'car_studio01',6:'car_studio01'};
    const CUBE_FOR_PRIM=(i)=>CUBE_OF[i]||null;
    const CUBE_SHA={qiangpi:'173d52990b3ab836',car_studio01:'bea649d8525cdc3e'};
    const srcCube=(name)=>{
      state.__srcCubeCache=state.__srcCubeCache||{};
      if(state.__srcCubeCache[name]) return state.__srcCubeCache[name];
      const T=state.THREE, B=(state.modelDir||'')+'src_cube/faces/';
      const t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(i=>B+name+'_f'+i+'_m0.png'));
      t.colorSpace=T.NoColorSpace; t.generateMipmaps=true;
      t.minFilter=T.LinearMipmapLinearFilter; t.magFilter=T.LinearFilter;
      t.wrapS=t.wrapT=T.ClampToEdgeWrapping;
      state.__srcCubeCache[name]=t; return t;
    };
    const per=ml.per_submesh||{},rig=ml.global_rig||{},gEnv=Number(rig.env_intensity);
    let idx=-1,hit=0,k=0;
    root.traverse(o=>{if(o.isMesh)o.visible=true;});   // 先全部恢复，再按实验开关隔离
    root.traverse(obj=>{
      if(!obj.isMesh)return;
      idx++;
      if(ex.onlySubmesh!==null&&ex.onlySubmesh!==undefined&&ex.onlySubmesh!==idx)obj.visible=false;
      const hasCfg=!!per[String(idx)];
      const cfg=per[String(idx)]||{};                 // 无配置的子网格（如 010 的 Sub0）也要能被实验开关处理
      if(!obj.userData.__srcMat)obj.userData.__srcMat=obj.material;      // ★ 固定 GLB 原始材质（实验模式反复切换不能污染）
      const src=obj.userData.__srcMat,base=Array.isArray(src)?src[0]:src;
      // ★ 源 u_base_color 的落点修正：它不乘表面色（乘了会把源贴图里的金色压成近黑 ✗），
      //   而应作为晶体的"透射吸收色"（Beer-Lambert attenuation）。依据：
      //   ① 参考图晶体区呈金色，而 u_base_color 是蓝紫 → 若乘表面必然丢金；
      //   ② 源参数块里 u_base_color 与 transmission/refraction 同组 → 属透射路径。
      //   表面色 = 源基色贴图原样；吸收色 = u_base_color（仅晶体）。
      const col=new THREE.Color(1,1,1);
      const em=new THREE.Color(0,0,0);
      if(cfg.subsurface_color&&ex.subsurfaceEmissive!==false)em.setRGB(cfg.subsurface_color[0],cfg.subsurface_color[1],cfg.subsurface_color[2]);
      const emGain=(()=>{const g=Number(rig.emissive_gain);return Number.isFinite(g)?g:0;})();   // 全局自发光增益（源基色贴图 × 增益；0=关闭，行为不变）
      const env=Number.isFinite(gEnv)?gEnv:(state.envIntensity!==undefined?state.envIntensity:1);
      // 晶体（有源参数配置、且带晶体色）才用 transmission 近似；主枪身=源 pbr_weapon 不透明金属，
      // 不能套透射参数（透射会改变 three 的 IBL 路径，且源里枪身没有 transmission 语义）
      // ★ 晶体判定按源 shader（viewer.json.material_layers.crystal_submeshes，来自 c159 的 pbr_crystal 记录），
      //   不按"是否有 per_submesh 参数"——缺参数的晶体仍是晶体，只标参数未决，不得降成普通金属
      const crystalList=Array.isArray(ml.crystal_submeshes)?ml.crystal_submeshes.map(Number):null;
      const useEmis=(emGain>0&&base&&base.map&&ex.emissiveGain!==false);   // 诊断可关：ex.emissiveGain=false   // 自发光=源基色贴图×全局增益（晶体也适用：源晶体同样有自发光项）
      const isCrystal=crystalList?crystalList.includes(idx):(hasCfg&&(cfg.transmission!==undefined||(Array.isArray(cfg.crystal_color)&&!!cfg.crystal_color.length)||cfg.roughness!==undefined));
      const matParams={
        map:(base&&base.map)||null,normalMap:(base&&base.normalMap)||null,
        roughnessMap:(ex.roughnessMode==='neutral'?null:((base&&base.roughnessMap)||null)),metalnessMap:(base&&base.metalnessMap)||null,
        color:(hasCfg?col:((base&&base.color)?base.color.clone():col)),
        // ★ 源结构（pbr_crystal 反汇编 L381-389）：基底色 = t_basecolor 原色参与漫反射着色，
        //   u_crystal_metallic(cb0[10].y) 属"晶体层"参数，不等于基底 albedo 的金属度 →
        //   不得映射到 Three 的 metalness（映射后 albedo 不参与着色，金色丢失 ✗）。
        //   晶体层（反射/折射/焦散）尚未实现 → 关闭并标 unresolved；基底层按介电处理。
        // 金属度：源公式为 saturate(lerp(u_base_metallic, u_crystal_metallic, w1))（反汇编 L368-369，本变体 cb0[316].z/.w）
        //   —— 两个源值都未从 c159 解析出 → 缺省标 unresolved；此处 0 仅为 **diagnostic**，非源依据、不推广。
        metalness:isCrystal?(Number.isFinite(cfg.metalness)?cfg.metalness:0):((Number.isFinite(cfg.metalness)?cfg.metalness:((base&&Number.isFinite(base.metalness))?base.metalness:1.0))),
        roughness:(ex.roughnessMode==='neutral')?ROUGH_NEUTRAL:(Number.isFinite(cfg.roughness)?cfg.roughness:((base&&Number.isFinite(base.roughness))?base.roughness:0.5)),
        emissive:useEmis?new THREE.Color(1,1,1):em,
        emissiveMap:useEmis?base.map:null,
        emissiveIntensity:useEmis?emGain:((ex.subsurfaceEmissive!==false&&Number.isFinite(cfg.emissive_strength))?cfg.emissive_strength:0),
        envMapIntensity:env*(Number.isFinite(cfg.cube_brightness)?cfg.cube_brightness:1),
        side:(base&&base.side!==undefined)?base.side:0
      };
      // ★ 已撤销（2026-09-15）：此前把源 u_base_color 写入 attenuationColor、并自设 attenuationDistance
      //   —— 无源依据（不是已证实的源吸收逻辑）。源参数仍保存在解析数据里，语义标 unresolved。
      //   当前晶体层只是"通用 Three 材质近似"，不得称为源晶体还原。
      /* ★ 已删除（2026-09-17，用户受控验证要求）：以下是「因为材质是 crystal 就开启 transmission/transparent」
         的错误路径。源 Blend / Depth / 折射状态尚未从源数据恢复，任何自行开启透明都是无源依据的补位，
         且会与数据 Alpha（t_basecolor.a = 粗糙度）混淆。现硬禁用；晶体同样按不透明渲染并标 incomplete。
         原代码：
           if(isCrystal&&ex.crystalModule===true&&ex.noCrystalTransmission!==true){
             matParams.transmission=...; matParams.thickness=...;
             matParams.ior=...; matParams.transparent=true; }
      */
      if(false && isCrystal && ex.crystalModule===true && ex.noCrystalTransmission!==true){
        matParams.transmission=Number.isFinite(cfg.transmission)?cfg.transmission:0.35;
        matParams.thickness=Number.isFinite(cfg.thickness)?cfg.thickness:0.25;
        matParams.ior=Number.isFinite(cfg.ior)?cfg.ior:1.45; matParams.transparent=true; }
      // 诊断模式（只用于对照，不改源值/不交换贴图）：
      //  idMap  = 纯材质 ID 平色（Unlit、toneMapped:false）→ 定位 primitive，不受亮度/暖色影响
      //  unlitTex = 原绑定贴图直接 Unlit 显示（跳过材质模型）
      if(state.diagMode==='B'){
        // B：原绑定贴图 Unlit（正确 sRGB：贴图 colorSpace 已为 SRGB，toneMapped=false 直出）
        if(base&&base.map){try{base.map.colorSpace=THREE.SRGBColorSpace;base.map.needsUpdate=true;}catch(e){}}
        obj.material=new THREE.MeshBasicMaterial({map:(base&&base.map)||null,color:0xffffff,toneMapped:false,fog:false});
        obj.material.side=(base&&base.side!==undefined)?base.side:0;
        obj.visible=true;return;
      }
      if(state.diagMode==='C'){
        // C：保守基线（未证项全部不执行；粗糙度=统一诊断常数，标 diagnostic）
        const DIAG_ROUGH=0.5;
        const p={map:(base&&base.map)||null,color:0xffffff,emissive:0x000000,
                 metalness:(isCrystal?0.0:1.0),   // 1.0 仅对已证 pbr_weapon(ParamMap.y=1)；晶体为诊断值
                 roughness:DIAG_ROUGH,envMapIntensity:1.0,toneMapped:true,
                 side:(base&&base.side!==undefined)?base.side:0};
        obj.material=new THREE.MeshStandardMaterial(p);
        obj.material.userData.__diagC={roughness:'diagnostic-constant(0.5)',metalness:(isCrystal?'diagnostic-0.0':'source-proven-1.0'),
                                       noTransmission:true,noEmissive:true,noTint:true};
        obj.visible=true;return;
      }
      if(ex.idMap){
        const IDPAL=[0xff3b30,0x34c759,0x0a84ff,0xffd60a,0xaf52de,0x00c7be,0xff9f0a];
        obj.material=new THREE.MeshBasicMaterial({color:IDPAL[idx%IDPAL.length],toneMapped:false,fog:false});
        obj.material.userData.__idColor=IDPAL[idx%IDPAL.length];
        hit++;obj.visible=(ex.onlySubmesh===null||ex.onlySubmesh===undefined||ex.onlySubmesh===idx);return;
      }
      if(ex.whiteUnlit){
        obj.material=new THREE.MeshBasicMaterial({color:0xffffff,toneMapped:false,fog:false});
        hit++;obj.visible=(ex.onlySubmesh===null||ex.onlySubmesh===undefined||ex.onlySubmesh===idx);return;
      }
      if(ex.unlitTex){
        obj.material=new THREE.MeshBasicMaterial({map:(base&&base.map)||null,toneMapped:false,fog:false});
        hit++;obj.visible=(ex.onlySubmesh===null||ex.onlySubmesh===undefined||ex.onlySubmesh===idx);return;
      }
      if(ex.crystalModule===false){
        matParams.transmission=0;matParams.thickness=0;
        matParams.attenuationColor=new THREE.Color(1,1,1);matParams.attenuationDistance=Infinity;
        matParams.transparent=false;matParams.opacity=1;
      }
      try{const __ov=(state.matOverride||{})[String(idx)];if(__ov){Object.keys(__ov).forEach(function(k){matParams[k]=__ov[k];});}}catch(e){}
      const mat=new THREE.MeshPhysicalMaterial(matParams);
      if(isCrystal){ matParams.envMap=null; matParams.envMapIntensity=0; matParams.emissive=new THREE.Color(0,0,0); matParams.emissiveIntensity=0; matParams.emissiveMap=null; }
      else { matParams.envMap=null; matParams.envMapIntensity=0; matParams.emissive=new THREE.Color(0,0,0); matParams.emissiveIntensity=0; matParams.emissiveMap=null; }
      // ★ 显式参数驱动（不再读隐式 state 开关）
      if(callOpts.sourceIblEnabled){
        state.__cAML=(state.__cAML||0)+1;
        matParams.envMap=null; matParams.envMapIntensity=0;
        matParams.emissive=new THREE.Color(0,0,0); matParams.emissiveIntensity=0; matParams.emissiveMap=null;
        matParams.toneMapped=false;
        applySourceEnvBright(mat, idx, callOpts.sourceIblMode);
        try{ mat.needsUpdate=true; }catch(e){}
      } else if(mat&&mat.userData){ mat.userData.__srcEnvBright='disabled_by_default'; }
      /* ★ 新增（2026-09-20，EMISTOGGLE）：**在硬清零之后**按开关追加自发光（A1/A2 默认全 false）。
         放在这里的原因：① mat 已在 L3983 由 matParams 建好 ⇒ 覆写真正生效，不制造死代码；
         ② 位于上面三处硬清零**之后** ⇒ enabled:false 时那三处逐字照旧、此处不改任何东西，现状不变。
         ③ 与 callOpts.sourceIblEnabled 分支无关 ⇒ 两档可单独开、互不耦合。 */
      try{ if(typeof emisPatchMaterial==='function'){ emisPatchMaterial({mat:mat,base:base},idx,emisResolve()); } }catch(e){}
      obj.material=mat;hit++;obj.visible=(ex.onlySubmesh===null||ex.onlySubmesh===undefined||ex.onlySubmesh===idx);
    });
    return hit;
  }

  async function loadSelectedState(){
    const item=selectedState();if(!item||!state.scene)return;
    const generation=++state.generation;
    setLoading(`正在加载${item.label}…`,false);state.status.textContent="模型按需加载中";showPoster(state.poster.src,state.poster.alt);
    disposeEffects();if(state.mixer){state.mixer.stopAllAction();state.mixer=null;}if(state.root)disposeObject(state.root);state.root=null;
    try{
      state.modelDir=(new URL(String(item.model),location.href).href).replace(/[^/]*$/,'');   // ★ P0-2：manifest 与纹理都以它为基准（绝对路径）
      const loader=new state.GLTFLoader();
      const gltf=await loader.loadAsync(item.model);
      if(generation!==state.generation){disposeObject(gltf.scene);return;}
      state.root=gltf.scene;state.modelYAxis=null;state.materialLayerHits=applyMaterialLayers(state.root);
      /* ★ 补切线：GLB 无 TANGENT 属性 → 法线贴图此前只能走导数法。这里为每个 geometry 计算一次。 */
      try{ var nTan=0, nGeo=0;
        state.root.traverse(function(o){ if(o.isMesh&&o.geometry){ nGeo++; if(computeVertexTangents(o.geometry)) nTan++; } });
        state.__tangentStats={geometries:nGeo, withTangents:nTan};
      }catch(e){ state.__tangentStats={error:String(e&&e.message||e)}; }
  try{ if(state.neoxMode!==false) applyNeoxManifest(state.root).then(function(r){state.neoxReport=r; try{ if(!(new URLSearchParams(location.search).get('lab')==='1')) applyMaterialLayers(state.root); }catch(e){}
  try{ window.WikiWeaponViewer.applyDebugUi(false); }catch(e){}   /* no-op：刻意不隐藏用户控件栏 */
  if(state.status && r && r.missing && r.missing.length && state.__debugUi===true)
    state.status.textContent="NEOX: 缺必需槽 "+JSON.stringify(r.missing);
  else if(state.status && state.__debugUi!==true) state.status.textContent="";
  renderOnce();}); }catch(e){}applyTransform(state.root,item);state.scene.add(state.root);fitObject(state.root);
      if(gltf.animations&&gltf.animations.length&&!matchMedia("(prefers-reduced-motion: reduce)").matches){
        state.mixer=new state.THREE.AnimationMixer(state.root);gltf.animations.forEach(clip=>state.mixer.clipAction(clip).play());
      }
      applyCamera(selectedCamera(),false);showPoster("","");setLoading("",false);
      state.status.textContent=`${item.label} · 拖动旋转，滚轮或双指缩放`;
      if(state.effectsHandle)disposeEffects();
    }catch(error){
      if(generation!==state.generation)return;
      setLoading(`模型加载失败：${error&&error.message?error.message:"未知错误"}`,true);
      state.status.textContent="已回退到海报；文字图鉴仍可正常使用";
      showPoster(posterSrc(state.record),state.title.textContent);
    }
  }

  function posterSrc(record){const p=record&&record.poster;return typeof p==="string"?p:(p&&p.src)||"";}

  async function open(record,options){
    // ★ 每次打开皮肤复位两个开关（默认关闭）——否则上一个皮肤勾选状态残留，表现为某皮肤上下锁失效/能缩放
    state.allowPitch=false;state.allowZoom=false;state.diagMode='A';setColorlessRig&&0;
    try{
      if(state.pitchToggle)state.pitchToggle.checked=false;
      if(state.zoomToggle)state.zoomToggle.checked=false;
      if(state.controls){state.controls.noZoom=true;state.controls.noRotate=true;}
    }catch(e){}
    ensureShell();close(false);state.generation++;state.record=record||{};state.lastFocus=document.activeElement;
    state.bodyOverflow=document.body.style.overflow;document.body.style.overflow="hidden";
    state.shell.hidden=false;state.title.textContent=(options&&options.title)||record.title||"武器 3D 预览";
    state.subtitle.textContent="按需加载 · 关闭后释放模型资源";state.status.textContent="";state.fidelity.textContent="";
    showPoster(absoluteUrl(posterSrc(record),location.href),state.title.textContent);setLoading("正在读取 3D 清单…",false);
    state.shell.querySelector(".wv-close").focus();
    try{
      const config=await resolveConfig(record);state.config=config;state.states=config._states;state.cameras=config._cameras;
      fillSelect(state.stateSelect,state.states,config.default_state);fillSelect(state.cameraSelect,state.cameras,config.default_camera||config.default_camera_preset);
      /* ★ 新增（2026-09-20，CUBE_PICKER）：每次打开皮肤都重建 cube 选择器。
         默认**不选中**任何覆盖 ⇒ 仍是 manifest 原绑定（qiangpi 默认档不变）；
         仅当用户主动切换时才走 __cubeAB 的近似档（level=approximate(diagnostic_selector)）。 */
      try{ fillCubeSelect(); }catch(e){}
      /* ★ 新增（2026-09-21，SNOWCUBE）：置产品默认的 override（**材质建立之前**）。
         这里 `state.THREE` 还没就绪，`__cubeAB` 会安全早返回（只置 override），
         真正的意义是让随后 `loadSelectedState()` 里的 `applyNeoxManifest()`
         在**建材质那一刻**就读到正确的 cube。没有声明默认的皮肤直接短路 ⇒ 零回归。 */
      try{ __cubeApplyProductDefault(); }catch(e){}
      const fidelity=config.fidelity||{};
      state.fidelity.textContent=[fidelityLabel(fidelity.material||record.preview_3d&&record.preview_3d.material_fidelity),fidelityLabel(fidelity.sfx||record.preview_3d&&record.preview_3d.sfx_fidelity)].filter(Boolean).join(" · ")+" · 查看器 v1.8.0";
      updateEffectsButton();setLoading("正在启动本地 3D 查看器…",false);
      await ensureRuntime();configureScene();await loadSelectedState();
      /* ★ 新增（2026-09-21，SNOWCUBE）：**材质异步建立之后**再保险换一次纹理。
         此处 `ensureRuntime()` 已跑完（state.THREE 就绪）⇒ `__cubeAB` 能真正把
         uSrcIbl/uCustomIbl 换成产品默认的 CubeTexture。
         （实测：只在 ensureRuntime 之前调会在 `if(!T) return 'ERR no THREE'` 提前返回。
          注意 `loadSelectedState()` 里 `applyNeoxManifest()` 的 promise **未被 await**，
          所以真正决定链材质 bind 的是上面那次 override，这里只做双保险。） */
      try{ __cubeApplyProductDefault(); }catch(e){}
    }catch(error){
      setLoading(`无法打开 3D 预览：${error&&error.message?error.message:"未知错误"}`,true);
      state.status.textContent="已保留海报回退，不影响图鉴浏览";
    }
  }

  function close(restoreFocus=true){
    if(!state.shell)return;
    state.generation++;disposeScene();state.shell.hidden=true;document.body.style.overflow=state.bodyOverflow;if(state.params)state.params.textContent="";
    if(document.fullscreenElement&&document.exitFullscreen)document.exitFullscreen().catch(()=>{});
    if(restoreFocus&&state.lastFocus&&typeof state.lastFocus.focus==="function")state.lastFocus.focus();
    state.record=null;state.config=null;state.states=[];state.cameras=[];
  }

  function toggleFullscreen(){
    if(!document.fullscreenElement){if(state.dialog.requestFullscreen)state.dialog.requestFullscreen().catch(()=>{});}
    else if(document.exitFullscreen)document.exitFullscreen().catch(()=>{});
  }

  function onDialogKey(event){
    if(event.key==="Escape"){event.preventDefault();close();return;}
    if(event.key!=="Tab")return;
    const focusable=[...state.dialog.querySelectorAll('button:not(:disabled),select:not(:disabled),[tabindex]:not([tabindex="-1"])')].filter(el=>!el.hidden&&el.offsetParent!==null);
    if(!focusable.length)return;
    const first=focusable[0],last=focusable[focusable.length-1];
    if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
  }

  function registerEffectsAdapter(adapter){state.effectsAdapter=adapter||null;if(state.config)updateEffectsButton();}

  // QA/自测用只读访问器（不改行为）
  // QA/自测用只读访问器（不改行为）：含模型投影框，可直接判断是否被画布裁切
  // 俯仰锁定：把相机相对 target 的极角钉在 pinnedPolar（相对相机 up 轴），绕轴 180° 时同步更新基准
  function pinPitch(){
    return;   // ★ 已停用：左右=模型绕视线轴自转（相机全程不动），无需钉相机；旧逻辑会与自转打架
    if(state.allowPitch||state.__rotating)return;
    const cam=state.camera,ctl=state.controls,T=state.THREE;
    if(!cam||!ctl||!T)return;
    const off=new T.Vector3().subVectors(cam.position,ctl.target),r=off.length();
    if(r<1e-6)return;
    // ★ 基准轴 = 世界竖直轴 +Y（水平转盘）：
    //   左右转必须绕世界竖直轴，否则（当相机 up 是斜的/反向时）会画出一个倾斜的圆 —— 用户观察到的"圆周运动"。
    //   上下锁定 = 把"相对世界 +Y 的极角"钉住；同时冻结 up（roll），保证画面不歪。
    const up=new T.Vector3(0,1,0),u=off.clone().normalize();
    const polar=Math.acos(Math.max(-1,Math.min(1,u.dot(up))));
    if(state.pinnedPolar===null||!Number.isFinite(state.pinnedPolar)){state.pinnedUp0=cam.up.clone();state.baseAz=Math.atan2(off.x,off.z);state.pinnedPolar=polar;return;}
    if(Math.abs(polar-state.pinnedPolar)<5e-4)return;
    const perp=u.clone().addScaledVector(up,-up.dot(u));
    if(perp.lengthSq()<1e-9)return;
    perp.normalize();
    const nu=perp.multiplyScalar(Math.sin(state.pinnedPolar)).addScaledVector(up,Math.cos(state.pinnedPolar));
    cam.position.copy(ctl.target).addScaledVector(nu,r);
    clearTrackballState();   // ★ 每帧归零指针增量：锁定期间控制器不再累积任何旋转（含余速）
    // ★ 画面滚转保持恒定：up 随相机一起绕世界竖轴转同样的角度。
    //   若把 up 固定在世界空间（之前做法），相机绕轴转时画面就会相对滚 → 看着像"斜着转"。
    if(state.pinnedUp0){
      const azNow=Math.atan2(nu.x,nu.z);
      const d=azNow-(Number.isFinite(state.baseAz)?state.baseAz:azNow);
      const c=Math.cos(d),s=Math.sin(d),U=state.pinnedUp0;
      cam.up.set(U.x*c+U.z*s,U.y,-U.x*s+U.z*c).normalize();   // R_y(d) · up0
    }
    cam.lookAt(ctl.target);
  }
  // ★ 自管旋转（替代 TrackballControls 的自由球旋转）：
  //   左右 = 绕"相机 up 轴（= 屏幕竖直轴）"、以 controls.target 为中心旋转 ⇒ 画面不歪、模型不绕圈、原地自转
  //   上下 = 仅在允许时绕"屏幕水平轴"旋转；不允许时**直接忽略竖直分量**（真正的锁死）
  function applyOrbit(dxPx,dyPx){
    const cam=state.camera,ctl=state.controls,T=state.THREE;
    if(!cam||!ctl||!T||!state.root)return;
    const k=0.0060;
    const mode=state.rotMode||'worldY';
    const focusOf=function(){const f=(typeof modelFocus==='function')?modelFocus():null;return (f&&f.center)?f.center.clone():ctl.target.clone();};
    const axisOf=function(){
      if(mode==='worldY')return new T.Vector3(0,1,0);
      if(mode==='modelY'){
        const oy=new T.Vector3(0,1,0);
        if(state.root.matrixWorld)oy.applyMatrix4(new T.Matrix4().extractRotation(state.root.matrixWorld));
        return oy.normalize();
      }
      return new T.Vector3().subVectors(ctl.target,cam.position).normalize();   // view：视线轴（画面平面内自转）
    };
    if(dxPx&&mode!=='native'){
      const c0=focusOf(); const axis=axisOf();
      state.root.quaternion.premultiply(new T.Quaternion().setFromAxisAngle(axis,-dxPx*k));
      state.root.updateMatrixWorld(true);
      const c1=focusOf();
      state.root.position.add(c0.clone().sub(c1));      // 绕"过中心"的轴 → 中心不漂
      state.root.updateMatrixWorld(true);
      renderOnce();return;
    }
    if(state.allowPitch&&dyPx){
      const ctr=focusOf();
      const off=new T.Vector3().subVectors(cam.position,ctr), r=off.length();
      if(r>1e-6){
        const f=new T.Vector3().subVectors(ctr,cam.position).normalize();
        const right=new T.Vector3().crossVectors(f,cam.up.clone().normalize());
        if(right.lengthSq()>1e-12){
          right.normalize();
          off.applyAxisAngle(right,-dyPx*k);
          cam.up.applyAxisAngle(right,-dyPx*k);cam.up.normalize();
          cam.position.copy(ctr).addScaledVector(off.normalize(),r);
          cam.lookAt(ctr);cam.updateMatrixWorld(true);ctl.target.copy(ctr);
          clearTrackballState();renderOnce();
        }
      }
    }
  }
  // 指针接管（仅旋转；缩放仍由控制器开关控制；平移禁用）
  function bindOrbitPointer(canvas){
    if(!canvas||canvas.__orbitBound)return; canvas.__orbitBound=true;
    let dragging=false,lastX=0,lastY=0;
    canvas.addEventListener('pointerdown',e=>{
      if(e.button!==0)return; dragging=true; lastX=e.clientX; lastY=e.clientY;
      try{canvas.setPointerCapture(e.pointerId);}catch(error){}
      e.preventDefault();
    });
    canvas.addEventListener('pointermove',e=>{
      if(!dragging)return;
      const dx=e.clientX-lastX, dy=e.clientY-lastY; lastX=e.clientX; lastY=e.clientY;
      if(dx||dy)applyOrbit(dx,dy);
    });
    const up=e=>{dragging=false;try{canvas.releasePointerCapture(e.pointerId);}catch(error){}};
    canvas.addEventListener('pointerup',up); canvas.addEventListener('pointercancel',up);
    canvas.addEventListener('pointerleave',()=>{dragging=false;});
  }
  function screenRoll(){const cam=state.camera,ctl=state.controls,T=state.THREE;if(!cam||!ctl||!T)return null;
    const f=new T.Vector3().subVectors(ctl.target,cam.position).normalize();
    const pj=v=>{const w=v.clone().addScaledVector(f,-v.dot(f));return w.lengthSq()<1e-12?null:w.normalize();};
    const a=pj(cam.up.clone()),b=pj(new T.Vector3(0,1,0));
    if(!a||!b)return null;
    const right=new T.Vector3().crossVectors(f,b).normalize();
    return Math.atan2(a.dot(right),a.dot(b))*180/Math.PI;}
  // 180° 旋转：h=绕 up 轴（左右），v=绕"右"横轴（上下，同时翻转 up 使画面不倒立）
  function rotate180(mode){
    const cam=state.camera,ctl=state.controls,T=state.THREE;
    if(!cam||!ctl||!T)return null;
    state.__rotating=true;                       // ★ 翻转期间暂停俯仰锁，保证 180° 不被抢回
    const off=new T.Vector3().subVectors(cam.position,ctl.target),r=off.length();
    if(r<1e-6){state.__rotating=false;return null;}
    const u0=cam.up.clone().normalize();
    // 旋转轴必须与视线垂直：先把 up 去掉沿 off 的分量（否则 H 不是精确 180° 反极点）
    const up=u0.clone().addScaledVector(off.clone().normalize(),-u0.dot(off.clone().normalize()));
    if(up.lengthSq()<1e-9){state.__rotating=false;return null;}
    up.normalize();
    if(mode==="h"&&state.root){
      const focus=(typeof modelFocus==='function')?modelFocus():null;
      const c0=(focus&&focus.center)?focus.center.clone():ctl.target.clone();
      const axis=new T.Vector3().subVectors(ctl.target,cam.position).normalize();  // 视线轴（画面内自转）
      state.root.quaternion.premultiply(new T.Quaternion().setFromAxisAngle(axis,Math.PI));
      state.root.updateMatrixWorld(true);
      const f2=(typeof modelFocus==='function')?modelFocus():null;
      if(f2&&f2.center){state.root.position.add(c0.clone().sub(f2.center));state.root.updateMatrixWorld(true);}
      clearControlInertia();renderOnce();
      if(state.status)state.status.textContent="已左右旋转 180°（画面平面内）";
      return {mode:"h"};
    }
    if(mode==="h"){
      off.applyAxisAngle(new T.Vector3(0,1,0),Math.PI);
      cam.up.copy(u0);
    }else{
      const fwd=off.clone().normalize().negate();
      const right=new T.Vector3().crossVectors(fwd,up);
      if(right.lengthSq()<1e-9){state.__rotating=false;return null;}
      right.normalize();
      off.applyAxisAngle(right,Math.PI);
      cam.up.copy(u0).applyAxisAngle(right,Math.PI);
    }
    clearControlInertia();                       // 先清控制器惯性，避免它随后把相机再推走
    cam.position.copy(ctl.target).add(off);
    cam.lookAt(ctl.target);
    ctl.update();
    // ★ 翻转是显式用户动作：把俯仰基准显式写成翻转后的值（拔掉"锁定把它抢回去"）
    const nb=new T.Vector3().subVectors(cam.position,ctl.target).normalize();
    state.pinnedPolar=Math.acos(Math.max(-1,Math.min(1,nb.y)));
    state.pinnedUp=cam.up.clone();
    renderOnce();
    state.__rotating=false;
    if(state.status)state.status.textContent=(mode==="h"?"已左右旋转 180°":"已上下旋转 180°");
    return {mode:mode,position:cam.position.toArray(),up:cam.up.toArray()};
  }
  // 相机参数文本（面板显示 + 一键复制）：直接可用于 viewer.json 的 game_reference 预设
  function cameraParams(){
    const cam=state.camera,ctl=state.controls,T=state.THREE;
    if(!cam||!ctl||!T)return null;
    const off=new T.Vector3().subVectors(cam.position,ctl.target),dist=off.length();
    const f=off.clone().normalize().negate();                 // 视线方向
    /* ★ 修复（2026-09-17）：`up` 必须报**相机世界矩阵里的真实 Y 轴**。
       原实现直接报 `cam.up` —— 但 `cam.up` 是 rotate180 / applyOrbit 累积改写后的原始值，
       会被 three 在 lookAt 内部**正交化**后才真正参与渲染，因此它**不必与视线垂直**。
       实测用户一份参数：up·f = -0.900（应为 0，夹角约 154°）→ 用它复现画面会得到不同角度。
       这里改为从 matrixWorld 取第二列（相机自身 Y 轴，渲染实际所用，必然垂直），
       并另存 `up_raw` 保留原值备查；roll 也改用真实 Y 轴计算。 */
    cam.updateMatrixWorld?cam.updateMatrixWorld():0;
    const me=cam.matrixWorld&&cam.matrixWorld.elements;
    let upTrue;
    if(me){ upTrue=new T.Vector3(me[4],me[5],me[6]); if(upTrue.lengthSq()<1e-12) upTrue=null; else upTrue.normalize(); }
    if(!upTrue) upTrue=cam.up.clone().normalize();
    const wUp=new T.Vector3(0,1,0);
    const u0=wUp.clone().addScaledVector(f,-wUp.dot(f));      // 世界up在像平面上的投影
    let roll=0;
    if(u0.lengthSq()>1e-9){
      u0.normalize();
      const right=new T.Vector3().crossVectors(f,u0).normalize();
      const cu=upTrue.clone();
      roll=Math.atan2(cu.dot(right),cu.dot(u0))*180/Math.PI;
    }
    /* ★ 诊断（2026-09-17）：并入**模型朝向**。
       本查看器的左右拖动是 `state.root.quaternion` 自转（见 applyOrbit），**相机全程不动** ——
       因此只报相机参数时，转动模型面板不会有任何变化（用户报告"能转但右下角不动"）。
       这里把 root 的四元数与欧拉角一并带出，使面板能如实反映所见画面。 */
    let mr=null;
    try{
      if(state.root){
        const q=state.root.quaternion;
        const e=new T.Euler().setFromQuaternion(q,'XYZ');
        /* 本查看器的拖动是**绕单轴自转**（见 applyOrbit），故除四元数外再给一个可读单值：
           yaw_deg = 绕模型自身 Y 轴的自转角，归一化到 (-180,180]。复现时以 quat 为准，
           euler_deg 仅为参考 —— 角度超过 ±90° 时 three 的 XYZ 欧拉会写成 [±180, θ∓180, ±180] 的等价形式。 */
        let yaw=(q.x===0&&q.z===0)
          ? 2*Math.atan2(q.y,q.w||1)*180/Math.PI
          : null;
        if(yaw!==null){ yaw=((yaw+180)%360+360)%360-180; }
        mr={quat:q.toArray().map(v=>+v.toFixed(6)),
            yaw_deg:(yaw!==null?+yaw.toFixed(2):null),
            euler_deg:[+(e.x*180/Math.PI).toFixed(2),+(e.y*180/Math.PI).toFixed(2),+(e.z*180/Math.PI).toFixed(2)]};
      }
    }catch(e){}
    return {position:cam.position.toArray(),target:ctl.target.toArray(),
            up:upTrue.toArray(),                /* 真实相机 Y 轴（与视线垂直，可复现） */
            up_raw:cam.up.toArray(),            /* 原始 cam.up（可能不垂直，仅供溯源） */
            direction:f.toArray(),distance:dist,roll_deg:roll,fov:cam.fov,fit_span:state.fitSpan,
            model_rot:mr,
            state_id:(selectedState()||{}).id,camera_id:(selectedCamera()||{}).id||state.config&&state.config.default_camera};
  }
  const res0=function(){const c=state.renderer&&state.renderer.domElement;return c?(c.width+'x'+c.height):null;};
  function paramsText(asJson){
    const p=cameraParams(); if(!p)return "";
    /* ★ 修复（2026-09-17）：res 必须在此处算好 —— 之前写在文本分支里，
       而 JSON 分支先 return，导致「复制参数」里 res 恒为 null（用户实测发现）。 */
    p.__res=res0();
    const r=(v,n)=>(Number(v)||0).toFixed(n===undefined?3:n);
    if(asJson)return JSON.stringify({position:p.position.map(v=>+r(v,4)),target:p.target.map(v=>+r(v,4)),
      up:p.up.map(v=>+r(v,4)),distance:+r(p.distance,4),roll_deg:+r(p.roll_deg,2),fov:+r(p.fov,2),span:+r(p.fit_span,4),
      res:p.__res||null, model_rot:(p.model_rot?{yaw_deg:p.model_rot.yaw_deg,euler_deg:p.model_rot.euler_deg,quat:p.model_rot.quat}:null),
      state:p.state_id},null,0);
    /* ★ 重排（2026-09-17）：固定标签列(6) + 数值右对齐 + 按「相机 / 模型 / 画面」分组。
       原先各字段是陆续追加的，标签宽度不一、数字左右错位，且提示语挤在数据行里。 */
    const cv=(state.renderer&&state.renderer.domElement)||null;
    const resTxt=cv?(cv.width+'x'+cv.height):'?';
    const cssTxt=cv?(cv.clientWidth+'x'+cv.clientHeight):'?';
    const dprTxt=(typeof window!=='undefined'&&window.devicePixelRatio)?window.devicePixelRatio:1;
    const LW=6;                                        /* 标签列宽 */
    const lab=s=>String(s).padEnd(LW);
    const vec=(a,w)=>a.map(v=>r(v,2).padStart(w)).join(' ');
    const mr=p.model_rot;
    const yawTxt=(mr&&mr.yaw_deg!==null&&mr.yaw_deg!==undefined)?(r(mr.yaw_deg,1)+'°')
                 :(mr?'(非单轴)':'(未加载)');
    const eulTxt=(mr&&mr.euler_deg)?mr.euler_deg.map(v=>r(v,1)).join('/'):'-';
    return [
      lab('pos')   +vec(p.position,7),
      lab('target')+vec(p.target,7),
      lab('up')    +vec(p.up,7),
      lab('dist')  +r(p.distance,2).padStart(7)+'  scale '+r(state.fitSpan/Math.max(1e-6,p.distance)*30,3)
                   +'  fov '+r(p.fov,1)+'  roll '+r(p.roll_deg,1)+'°',
      '',
      lab('yaw')   +yawTxt.padStart(7)+'  euler '+eulTxt,
      '',
      lab('span')  +r(p.fit_span,3).padStart(7)+'  state '+(p.state_id||'-'),
      lab('res')   +resTxt.padStart(9)+'  dpr '+dprTxt+'  css '+cssTxt
    ].join('\n');
  }
  function fallbackCopy(txt,done){
    try{const ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();
      document.execCommand('copy');document.body.removeChild(ta);done();}catch(error){}
  }
  function updateParams(){
    if(!state.params||state.shell.hidden)return;
    var t=paramsText(false);
    if(t===state.__lastParamsText)return;          /* 值没变就不碰 DOM（60fps 下必需） */
    state.__lastParamsText=t; state.params.textContent=t;
    window.__paramsUpdates=(window.__paramsUpdates||0)+1;   /* 验证计数 */
  }
  /* ★ 修复（2026-09-17，审查员 P3）：`window.__VIEWER_SHA` 此前**只被读取、从未赋值**，
     导致 neoxState().viewer_sha 恒为 null —— 排查「浏览器里跑的是哪一版」时无法自证。
     这里在加载后取自身脚本源码算一个短哈希写入该全局（同源 fetch，异步、失败静默）。 */
  try{(function(){
    var sc=Array.prototype.filter.call(document.scripts||[],function(s){return s.src&&/weapon_skin_viewer\.js/.test(s.src);})[0];
    if(!sc) return;
    fetch(sc.src,{cache:'no-store'}).then(function(r){return r.text();}).then(function(t){
      var h=0x811c9dc5; for(var i=0;i<t.length;i++){ h^=t.charCodeAt(i); h=(h*0x01000193)>>>0; }
      window.__VIEWER_SHA=('00000000'+h.toString(16)).slice(-8);
      window.__VIEWER_SRC_BYTES=t.length;
    }).catch(function(){});
  })();}catch(e){}
  /* ★ 新增（2026-09-17）：rAF 节流的参数面板刷新，供 controls 的 change 事件调用。 */
  var __paramsRaf=0;
  function scheduleParams(){ if(__paramsRaf) return;
    __paramsRaf=requestAnimationFrame(function(){ __paramsRaf=0; updateParams(); }); }
  window.__refreshParams=function(){ updateParams(); return paramsText(false); };
  function debugState(){
    if(!state.camera||!state.controls)return null;
    const cv=state.renderer.domElement;
    const ctl=state.controls,off=[state.camera.position.x-state.controls.target.x,
      state.camera.position.y-state.controls.target.y,state.camera.position.z-state.controls.target.z];
    const r=Math.hypot(off[0],off[1],off[2])||1;
    const out={azimuth:Math.atan2(off[0],off[2]),polar:Math.acos(Math.max(-1,Math.min(1,off[1]/r))),
      distance:r,target:state.controls.target.toArray(),
      sfxDiag:(state.effectsHandle?{fidelity:state.effectsHandle.fidelity,colorOrder:state.effectsHandle.colorOrder,spriteNodes:state.effectsHandle.spriteNodes,particleSystems:state.effectsHandle.particleSystems,particleSystemsActive:state.effectsHandle.particleSystemsActive,ignoredParticleNodes:state.effectsHandle.ignoredParticleNodes}:null),noPan:!!state.controls.noPan,up:state.camera.up.toArray().map(v=>Math.round(v*1000)/1000),controller:state.controls.constructor&&state.controls.constructor.name,buffer:[cv.width,cv.height],cssBox:[cv.clientWidth,cv.clientHeight],crystalLayers:state.materialLayerHits||0,
      dpr:state.renderer.getPixelRatio(),aspect:state.camera.aspect,fov:state.camera.fov,version:"1.8.0",
      camPos:state.camera?state.camera.position.toArray().map(v=>Math.round(v*1000)/1000):null,
      envBrightStatus:(function(){const r=[];if(state.root)state.root.traverse(o=>{if(o.isMesh&&o.material)r.push({m:o.material.type,ud:(o.material.userData&&o.material.userData.__srcEnvBright)||'-',t:o.material.transmission||0,metal:o.material.metalness,rough:o.material.roughness});});return r;})()};
    try{
      if(state.root&&state.THREE){
        const box=new state.THREE.Box3().setFromObject(state.root),vv=new state.THREE.Vector3(),pts=[];
        const mn=box.min,mx=box.max;
        for(let i=0;i<8;i++){vv.set(i&1?mx.x:mn.x,i&2?mx.y:mn.y,i&4?mx.z:mn.z).project(state.camera);pts.push([vv.x*.5+.5,1-(vv.y*.5+.5)]);}
        const px=pts.map(p=>p[0]),py=pts.map(p=>p[1]);
        out.proj={x0:Math.min(...px),x1:Math.max(...px),y0:Math.min(...py),y1:Math.max(...py)};
        out.projCenter=[(out.proj.x0+out.proj.x1)/2,(out.proj.y0+out.proj.y1)/2];
        out.clipped=(out.proj.x0<-0.01||out.proj.x1>1.01||out.proj.y0<-0.01||out.proj.y1>1.01);
        out.projCenterNow=out.projCenter;
      }
    }catch(e){out.projError=String(e&&e.message||e);}
    return out;
  }
  // QA 探针: 临时切到任意方向取景（仅自测脚本使用，不改默认）
  function tryView(pos,fov,rotDeg){if(!state.camera||!state.controls)return null;if(rotDeg&&state.root){const d=Math.PI/180;state.root.rotation.set(rotDeg[0]*d,rotDeg[1]*d,rotDeg[2]*d);state.root.updateMatrixWorld(true);}applyCamera({position:pos,fov:Number(fov)||state.camera.fov||34,label:'QA'},false);return debugState();}
  window.WikiWeaponViewer={
  // 实验：在模型局部坐标画坐标轴（用于验证挂点矩阵/居中偏移）
  __expAxes:function(pos){
    const THREE=state.THREE;if(!THREE||!state.root)return null;
    if(state.__axes){state.root.remove(state.__axes);state.__axes.dispose&&state.__axes.dispose();state.__axes=null;}
    if(!pos)return null;
    const a=new THREE.AxesHelper(1.0);
    a.position.fromArray(pos.map(Number));
    a.name='exp-axes';
    state.root.add(a);state.__axes=a;
    return {pos:a.position.toArray()};
  },
  // 实验：给 SFX 层设定固定时间（统一时间轴，便于可重复截图）
  __sfxTime:function(t){const h=state.effectsHandle;if(h&&typeof h.setTime==='function'){h.setTime(t===null||t===undefined?null:Number(t));return true;}return false;},
  __sfxSeed:function(n){const h=state.effectsHandle;if(h&&typeof h.seed==='function'){h.seed(Number(n)||0);return true;}return false;},
  __exp:function(patch){
    // ★ 合并更新（不清空其他键）——避免 onlySubmesh / unlit / idMap / 覆写互相冲掉
    const cur=state.expFlags||{baseColor:true,subsurfaceEmissive:true,onlySubmesh:null,roughnessMode:'neutral',envBright:false,envBlend:0,idMap:false,unlitTex:false,whiteUnlit:false};
    state.expFlags=Object.assign({},cur,patch||{});
    if(state.expFlags.idMap||state.expFlags.unlitTex||state.expFlags.whiteUnlit){/* 保留 composer */}
    if(state.root)applyMaterialLayers(state.root);
    renderOnce();
    return {flags:state.expFlags,bloom:!!state.composer};
  },
  /* ★★ 修复（2026-09-19，shader-auditor，task-49，lead 裁决 1）：`env_warn` / `missing[__env_ibl__]` **陈旧**。
     旧实现把它们写在 `rec`（建材质时刻快照）里，而窗口期那次 `applyNeoxManifest` 的 promise 可能晚于重绑那次
     resolve ⇒ `state.neoxReport` 落后于真实状态（实测：settle 后 `__texReady()` 已 7/7 `source_ibl`，而
     `__neox().missing` 仍残留 `ibl_pending` 条目 ⇒ **验收门自己撒谎**）。
     现改为**读取时现算**：每次按 **当前材质的 envMap/uCustomIbl** + **state.__iblGate** 重新求值；
     旧 report 里所有 `__env_ibl__` 条目先剔除再重建；`rec.env_warn` 不再作为唯一来源。 */
  __neoxLiveEnv:function(){
    try{
      /* ★ 修法 (A)（2026-09-19，task-49，Lead 裁决；备份 wsv_bak_task49M_20260919_160315.js = 0B9F2148E6A9935D）：
         `state.neoxReport` 只在 `applyNeoxManifest()` **resolve 时**赋值，而 `pendingHide` 在**材质建立过程中**
         就打标记 ⇒ **窗口期 `state.neoxReport` 仍为 `null`**，原实现 `if(!rep) return rep;` 直接返回 null ⇒
         `__neox().report` 在窗口期**没有 prim 列表**，无法表达 pending（实测 `src_neox=[]` 而 live 两源为 `[0,1]`/2）。
         现按 (A)：**rep 为空时也从场景 live 材质（下面 byPrim）合成 prims**，并在合成时把口径标为
         `'read_time(scene-synthesized)'`。**不引入任何第二状态源**（不写 `state.__pendingHidden*` 之类新全局），
         **不改渲染、不改 fail-closed**，也不改 `state.neoxReport` 本体。 */
      var rep=state.neoxReport||{};
      var byPrim={}, gate=state.__iblGate||{};
      if(state.scene) state.scene.traverse(function(o){
        if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0];
        if(!m||!m.userData||!m.userData.chain) return;
        var c=m.userData.chain, sh=m.userData.__sh, u=(sh&&sh.uniforms)||{};
        var cube=(u.uCustomIbl&&u.uCustomIbl.value)||null, hasCustom=!!cube;
        var faces=0; try{ var im=cube&&cube.image;
          if(im&&im.length){ for(var k=0;k<im.length;k++){ var e=im[k];
            if(e&&(e.complete===undefined||e.complete)&&(e.naturalWidth===undefined||e.naturalWidth>0)) faces++; } } }catch(e){}
        var bound=!!m.envMap || hasCustom;
        byPrim[c.prim]={envMode:(bound?'source_ibl':((m.userData.neox&&m.userData.neox.environment)||'missing_source_ibl')),
                        envMap_bound:!!m.envMap, radiance_bound:hasCustom, faces_loaded:faces,
                        /* ★ 新增（2026-09-19，task-49 只读分析 §1.4 / lead 批准）：live 读取 pending 标记，
                           供下面把 `prims[*].pending_hidden` **按读取时刻现算**（修"report 侧陈旧快照"）。 */
                        pending_hidden:!!m.userData.__pendingHidden};
      });
      var miss=[], warn=[];
      (rep.missing||[]).forEach(function(x){ if(!(x.slots||[]).some(function(s){ return s==='__env_ibl__'; })) miss.push(x); });
      (rep.prims||[]).forEach(function(p){
        var L=byPrim[p.prim]; if(!L) return;
        if(L.envMode!=='source_ibl'){
          miss.push({prim:p.prim, slots:['__env_ibl__'], envMode:L.envMode});
          warn.push({prim:p.prim, envMode:L.envMode, envMap_bound:L.envMap_bound,
                     radiance_bound:L.radiance_bound, faces_loaded:L.faces_loaded});
        }
      });
      /* ★ 修复（2026-09-19，task-49；备份 wsv_bak_task49j_20260919_154024.js = 3B9999B992FE8763）：
         `report.prims[*].pending_hidden` 原是**建材质时刻的快照**（旧报告可能晚到覆盖）⇒ settle 后仍可能残留
         窗口期的值，与 `__texReady()/__acceptanceReport()` 的 **live 计数** 不一致（1110171 WARN：2 vs 0）。
         现按 **read-time** 口径重算：以 live 场景的 `userData.__pendingHidden` 为准覆写 `prims[*].pending_hidden`，
         **不改 `state.neoxReport` 本体**（避免污染其它读者），并标 `pending_hidden_source:'read_time'`。 */
      var primsLive=(rep.prims||[]).map(function(p){
        var L=byPrim[p.prim];
        return (L?Object.assign({}, p, {pending_hidden:!!L.pending_hidden}) : p);
      });
      /* ★ (A) 合成（2026-09-19，task-49）：把**只存在于场景、尚未进入 report** 的 prim 补进来
         （窗口期 `state.neoxReport===null` 或 report 尚未含目标 prim 时，这一路才可能表达 pending）。
         数据全部来自 live `byPrim`（同一份 `userData.__pendingHidden`/envMap/uCustomIbl），无第二状态源。 */
      var seen={}; primsLive.forEach(function(p){ if(p&&p.prim!==undefined) seen[p.prim]=1; });
      var synthesized=false;
      Object.keys(byPrim).forEach(function(k){
        if(seen[k]) return;
        var L=byPrim[k]; synthesized=true;
        primsLive.push({prim:(isFinite(Number(k))?Number(k):k), synthesized:true,
          pending_hidden:!!L.pending_hidden, envMode:L.envMode,
          envMap_bound:L.envMap_bound, radiance_bound:L.radiance_bound, faces_loaded:L.faces_loaded});
      });
      /* env 侧同样改以 `primsLive`（含合成项）为准 —— 否则窗口期 `missing/env_warn` 也会"看不见"未就绪 prim。 */
      var miss=[], warn=[];
      (rep.missing||[]).forEach(function(x){ if(!(x.slots||[]).some(function(s){ return s==='__env_ibl__'; })) miss.push(x); });
      primsLive.forEach(function(p){
        var L=byPrim[p.prim]; if(!L) return;
        if(L.envMode!=='source_ibl'){
          miss.push({prim:p.prim, slots:['__env_ibl__'], envMode:L.envMode});
          warn.push({prim:p.prim, envMode:L.envMode, envMap_bound:L.envMap_bound,
                     radiance_bound:L.radiance_bound, faces_loaded:L.faces_loaded});
        }
      });
      return Object.assign({}, rep, {prims:primsLive, missing:miss, env_warn:(warn.length?warn:null),
        pending_hidden_source:(synthesized?'read_time(scene-synthesized)':'read_time'),
        env_live:{computed:'read_time(材质 envMap/uCustomIbl + state.__iblGate)', prims:byPrim}});
    }catch(e){ return state.neoxReport; }
  },
  __neox:function(){return {report:this.__neoxLiveEnv(), mode:state.neoxMode, baseColorSRGB:state.neoxBaseColorSRGB===true, manifest:state.neoxManifest?{sha:state.neoxManifest.sha, counts:state.neoxManifest.counts}:null};},
  __post:function(on){  // 诊断期后处理开关（false=粘性关闭，applyMaterialLayers 不会重新开启）
    state.noPost=(on===false);
    if(on===false){}
    else{ensureComposer().then(function(){renderOnce();});}
    renderOnce();return {bloom:!!state.composer};
  },
  __matOverride:function(sub,patch){
    state.matOverride=state.matOverride||{};
    if(patch===null){delete state.matOverride[String(sub)];}
    else{state.matOverride[String(sub)]=Object.assign({},state.matOverride[String(sub)]||{},patch||{});}
    if(state.root)applyMaterialLayers(state.root);
    renderOnce();
    return state.matOverride;
  },
  __matDump:function(){
    // ★ 运行时真实材质（不看声明、看实例）
    function mi(t){return t?{name:(t.name||''),cs:(t.colorSpace||''),uuid:String(t.uuid||'').slice(0,8),
      w:(t.image&&t.image.width)||null,h:(t.image&&t.image.height)||null}:null;}
    const meshes=[];let i=-1;
    if(state.root)state.root.traverse(function(o){
      if(!o.isMesh)return;i++;
      const m=o.material;if(!m)return;
      meshes.push({i:i,visible:o.visible,matType:(m.type||''),
        color:(m.color?m.color.getHexString():null),
        metalness:(m.metalness===undefined?null:m.metalness),roughness:(m.roughness===undefined?null:m.roughness),
        map:mi(m.map),metalnessMap:mi(m.metalnessMap),roughnessMap:mi(m.roughnessMap),normalMap:mi(m.normalMap),
        transmission:(m.transmission===undefined?null:m.transmission),transparent:!!m.transparent,opacity:m.opacity,
        emissive:(m.emissive?m.emissive.getHexString():null),emissiveMap:mi(m.emissiveMap),
        emissiveIntensity:(m.emissiveIntensity===undefined?null:m.emissiveIntensity),
        envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
        toneMapped:(m.toneMapped===undefined?null:m.toneMapped)});
    });
    return {flags:state.expFlags||null,overrides:state.matOverride||null,
            bloom:!!state.composer,exposure:(state.renderer?state.renderer.toneMappingExposure:null),
            toneMapping:(state.renderer?state.renderer.toneMapping:null),
            envIntensity:(state.scene?state.scene.environmentIntensity:null),
            background:(state.scene&&state.scene.background&&state.scene.background.isColor)?state.scene.background.getHexString():'texture',
            lights:(function(){const a=[];state.scene&&state.scene.traverse(function(o){if(o.isLight)a.push(o.type+'#'+o.color.getHexString()+'@'+o.intensity);});return a;})(),
            meshCount:meshes.length,meshes:meshes};
  },
  __materialExperiment:function(opts){
    state.expFlags=Object.assign({baseColor:true,subsurfaceEmissive:true,onlySubmesh:null},opts||{});
    if(state.root)applyMaterialLayers(state.root);
    return {flags:state.expFlags,layers:(function(){const s=selectedState()||{};const m=s.material_layers||(state.config||{}).material_layers||{};return Object.keys(m.per_submesh||{});})()};
  },
  __setCam:function(azDeg,elevDeg,rollDeg,distScale,fitSpan){
    // 对齐用：按球坐标直接设定相机（方位/俯仰/滚转/距离），不动模型
    if(!state.camera||!state.controls)return null;
    const THREE=state.THREE;if(!THREE)return null;
    if(Number.isFinite(Number(fitSpan)))state.fitSpan=Number(fitSpan);
    const focus=modelFocus();
    const az=Number(azDeg||0)*Math.PI/180,el=Number(elevDeg||0)*Math.PI/180;
    const dir=new THREE.Vector3(Math.sin(az)*Math.cos(el),Math.sin(el),Math.cos(az)*Math.cos(el)).normalize();
    const up=new THREE.Vector3(0,1,0);
    up.applyQuaternion(new THREE.Quaternion().setFromAxisAngle(dir,(Number(rollDeg)||0)*Math.PI/180));
    const preset={label:'cal',no_basis:true,position:dir.toArray(),up:up.toArray()};
    if(focus&&Number.isFinite(Number(distScale))&&Number(distScale)>0)preset.distance=fitDistanceToFocus(focus,dir,state.fitSpan)*Number(distScale);
    applyCamera(preset,false);
    return debugState();
  },
  __preset:function(){return debugState();},__spinDemo:function(mode,deg){
    // 诊断：按三种候选轴各转 deg 度（仅实验用）
    const cam=state.camera,ctl=state.controls,T=state.THREE;
    if(!cam||!ctl||!T||!state.root)return null;
    const th=Number(deg||0)*Math.PI/180;
    const focus=(typeof modelFocus==='function')?modelFocus():null;
    const ctr=(focus&&focus.center)?focus.center.clone():ctl.target.clone();
    if(mode==='modelY'){                       // A: 模型自身 Y 轴
      if(!state.modelYAxis){const oy=new T.Vector3(0,1,0);oy.applyMatrix4(new T.Matrix4().extractRotation(state.root.matrixWorld));state.modelYAxis=oy.normalize().clone();}
      state.root.quaternion.premultiply(new T.Quaternion().setFromAxisAngle(state.modelYAxis,th));
      state.root.updateMatrixWorld(true);
    }else if(mode==='worldY'){                 // B: 世界 Y 轴（过模型中心）→ 等价于相机绕该轴公转
      const off=new T.Vector3().subVectors(cam.position,ctr);
      off.applyAxisAngle(new T.Vector3(0,1,0),th);
      cam.up.applyAxisAngle(new T.Vector3(0,1,0),th);cam.up.normalize();
      cam.position.copy(ctr).addScaledVector(off.normalize(),off.length());
      cam.lookAt(ctr);cam.updateMatrixWorld(true);ctl.target.copy(ctr);
    }else if(mode==='camUp'){                  // C: 相机自身 up 轴（过模型中心）
      const up=cam.up.clone().normalize();
      const off=new T.Vector3().subVectors(cam.position,ctr);
      off.applyAxisAngle(up,th);
      cam.position.copy(ctr).addScaledVector(off.normalize(),off.length());
      cam.lookAt(ctr);cam.updateMatrixWorld(true);ctl.target.copy(ctr);
    }
    renderOnce();return {mode:mode,deg:deg};
  },
  __params:function(){return cameraParams();},
  __crystalCInspect:function(){
    const rep=state.__crystalC;
    if(!rep||!rep.savedRefs||!rep.savedRefs.length)return {error:'C 模式未开启'};
    const o=rep.savedRefs[0],m=o.material,sh=m&&m.userData&&m.userData.__shader;
    const frag=(sh&&sh.fragmentShader)||'';
    const lines=frag.split('\n').filter(function(l){return /uAssumeA1|uHasDetail|uMissing|uTex0|uDetailMap|fDetailOffset|fDetailTiling|d_=|C_=|diffuseColor\.rgb\*=|gl_FragColor=vec4\(1\.0,0\.0,1\.0/.test(l);});
    const uni={};
    if(sh&&sh.uniforms){Object.keys(sh.uniforms).forEach(function(k){const v=sh.uniforms[k].value;
      if(v&&v.isVector2)uni[k]=[v.x,v.y];else if(v&&v.isVector3)uni[k]=[v.x,v.y,v.z];
      else if(v&&v.isTexture)uni[k]='<Texture '+((v.image&&v.image.width)||'?')+'x'+((v.image&&v.image.height)||'?')+'>';
      else uni[k]=v;});}
    return {meshIndex:(function(){let i=-1,tgt=null;state.root&&state.root.traverse(function(q){if(q.isMesh){i++;if(q===o)tgt=i;}});return tgt;})(),
            materialStillOnMesh:!!(o.material===m), visible:!!o.visible, matType:m.type, hasMap:!!m.map,
            programCacheKey:(m.customProgramCacheKey?m.customProgramCacheKey():null),
            injectedSource:lines, uniforms:uni,
            rendererProgramCount:(state.renderer&&state.renderer.info&&state.renderer.info.programs)?state.renderer.info.programs.length:null,
            stateAssumedA1:!!state.__crystalCAssumeA1};
  },
  __crystalC:function(on,assumeA1){state.__crystalCAssumeA1=!!assumeA1;return crystalCDebug(on!==false);},
  __rig:function(on){setColorlessRig(!!on);return true;},
  __rigInfo:function(){const a=[];state.scene&&state.scene.traverse(function(o){if(o.isLight)a.push(o.type+'#'+o.color.getHexString());});return a;},
  __crystalOpaque:function(on){state.expFlags=Object.assign({baseColor:true,subsurfaceEmissive:true,onlySubmesh:null,noCrystalTransmission:!!on},state.expFlags||{});if(state.root)applyMaterialLayers(state.root);renderOnce();return state.expFlags;},
  __diag:function(m){return setDiagABC(m||'A');},
  __diagInfo:function(){return {mode:state.diagMode||'A',flags:state.expFlags,lightColors:(function(){const a=[];state.scene&&state.scene.traverse(function(o){if(o.isLight)a.push(o.type+'#'+o.color.getHexString()+'@'+o.intensity);});return a;})()};},__screenRoll:function(){return screenRoll();},
  version:"1.8.0",open,close,registerEffectsAdapter,__state:debugState,__tryView:tryView,__rotate180:rotate180}
// ==== 供自动化验收使用的严格 API ====
/* 人工近似 API 已移除（invalidated_for_production） */
/* 只读：由 applyNeoxManifest 已经消费过的值缓存（不写死任何经验参数） */
window.WikiWeaponViewer.setNeoxApprox=function(){ return {removed:'invalidated_for_production', reason:'人工调参已停用'}; };
window.WikiWeaponViewer.getNeoxApprox=function(){ return null; };
window.WikiWeaponViewer.__bindCubes=function(mode){
  /* 逐材质 samplerCube 绑定：weapon←qiangpi, crystal←car_studio01；禁 scene.environment / 禁 PMREM
     mode: 'normal' | 'swap'（负面对照）| 'off'  */
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    var BASE='assets/3d/weapon_skin/1110171/cube_faces/';
    var NAMES={normal:{weapon:'qiangpi',crystal:'car_studio01'},swap:{weapon:'car_studio01',crystal:'qiangpi'},off:{}};
    var pick=NAMES[mode||'normal']; if(!pick) return 'ERR bad mode';
    state.scene.environment=null; state.scene.environmentIntensity=0;   /* 禁 scene-wide */
    if(state.__cubeLdr) state.__cubeLdr={}; else state.__cubeLdr={};
    var rep=[], n=0;
    var B0=state.__l0Base||{};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    M.forEach(function(o){
      var ch=(o.material.userData.chain)||{}; var kind=ch.kind||'?';
      var name=pick[kind];
      if(!name){ o.material.envMap=null; o.material.envMapIntensity=0; o.material.needsUpdate=true;
                 rep.push({prim:ch.prim, kind:kind, cube:null, sha:null, note:'unbound'}); n++; return; }
      var urls=[0,1,2,3,4,5].map(function(i){ return BASE+name+'_f'+i+'.png'; });
      var key=name;
      if(!state.__cubeLdr[key]){
        state.__cubeLdr[key]=new T.CubeTextureLoader().load(urls);
        state.__cubeLdr[key].colorSpace=T.SRGBColorSpace;
      }
      o.material.envMap=state.__cubeLdr[key];
      o.material.envMapIntensity=1.0;
      o.material.needsUpdate=true;
      rep.push({prim:ch.prim, kind:kind, cube:name, sha:(state.__cubeCubSha&&state.__cubeCubSha[name])||null});
      n++;
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    state.__cubeBind={mode:(mode||'normal'), sampling:'sampling_unresolved', scene_environment:(state.scene.environment?'SET':'null'), meshes:n, table:rep};
    return JSON.stringify(state.__cubeBind);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__envPlan=function(plan){
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    plan=plan||{};
    var S='assets/3d/weapon_skin/1110171/cube_cand/character_08_00745_f';
    var load=function(pr){ return new Promise(function(res){
      new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return pr+i+'.png';}),
        function(ct){ ct.colorSpace=T.SRGBColorSpace; res(ct); }, undefined, function(){ res(null); }); }); };
    var want={weapon:(plan.weapon?S:null), crystal:(plan.crystal?S:null)};
    var jobs=Object.keys(want).map(function(k){ return want[k]?load(want[k]).then(function(ct){return [k,ct];}):Promise.resolve([k,null]); });
    return Promise.all(jobs).then(function(pairs){
      var map={}; pairs.forEach(function(p){ map[p[0]]=p[1]; });
      state.scene.environment=null; state.scene.environmentIntensity=0;   /* 禁 scene-wide */
      var rep=[], n=0;
      state.scene.traverse(function(o){
        if(!o.isMesh||!o.material) return;
        var mud=o.material.userData||{}; if(!(mud.neox||mud.chain)) return;
        var ch=mud.chain||{}; var ct=map[ch.kind]||null;
        o.material.envMap=ct; o.material.envMapIntensity=ct?1.0:0.0; o.material.needsUpdate=true;
        rep.push({kind:ch.kind, prim:ch.prim, env:(ct?('candCube_'+ch.kind):'none')}); n++;
      });
      try{_forceRender();_forceRender();_forceRender();}catch(e){}
      return JSON.stringify({ok:true, scene_environment:(state.scene.environment?'SET':'null'), meshes:n});
    });
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};

/* IBL 诊断：独立于 PBR 的 samplerCube 直采样（不加任何人工色）
   标签：binding_verified / ibl_sampling_formula_unresolved
   spec = {mode:'off'|'weapon_only'|'crystal_only'|'normal'|'swap', mip:0} */
window.WikiWeaponViewer.__iblDiag=function(spec){
  spec=spec||{}; var mode=spec.mode||'off'; var MIP=Number(spec.mip||0);
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    var BASE='assets/3d/weapon_skin/1110171/cube_faces/';
    var PICK={off:{}, weapon_only:{weapon:'qiangpi'}, crystal_only:{crystal:'car_studio01'},
              normal:{weapon:'qiangpi',crystal:'car_studio01'},
              swap:{weapon:'car_studio01',crystal:'qiangpi'}}[mode];
    if(PICK===undefined) return 'ERR bad mode';
    state.scene.environment=null; state.scene.environmentIntensity=0;   /* 禁 scene-wide */
    if(!state.__cubeLdr) state.__cubeLdr={};
    function cubeOf(name){
      if(!state.__cubeLdr[name]){
        var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return BASE+name+'_f'+i+'.png';}));
        t.colorSpace=T.SRGBColorSpace; t.needsUpdate=true; state.__cubeLdr[name]=t;
      }
      return state.__cubeLdr[name];
    }
    state.__iblProbe={};   /* ★ 修复（2026-09-17，审查员 P2-1）：原为 `if(!…)` 从不清空 →
                                  __iblDiagFrag(idx) 按插入序索引会取到**上一轮**的旧条目，诊断证据错配。改为每轮清空。 */
    var B0=state.__l0Base||{};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var table=[];
    M.forEach(function(o,i){
      var ch=(o.material.userData.chain)||{}; var kind=ch.kind||'?';
      var name=PICK[kind]||null;
      var key='p'+i+'_'+mode+'_'+MIP;
      var ct=name?cubeOf(name):null;
      var mat=new T.MeshStandardMaterial({color:0xffffff, metalness:0.0, roughness:1.0, envMap:null});
      mat.onBeforeCompile=function(shader){
        shader.uniforms.uCustomIbl={value:ct};
        shader.uniforms.uDiagMip={value:MIP};
        shader.fragmentShader='uniform samplerCube uCustomIbl;\nuniform float uDiagMip;\n'+shader.fragmentShader;
        shader.fragmentShader=shader.fragmentShader.replace('#include <dithering_fragment>',
          'gl_FragColor = vec4(textureCubeLodEXT(uCustomIbl, normalize(normal), uDiagMip).rgb, 1.0);');
        if(!state.__iblProbe[key]) state.__iblProbe[key]={};
        state.__iblProbe[key].frag=shader.fragmentShader;
      };
      mat.customProgramCacheKey=function(){ return 'iblDiag_'+mode+'_'+MIP+'_'+i; };
      var old=o.material; o.material=mat;
      if(!o.userData.__origMat) o.userData.__origMat=old;
      table.push({prim:ch.prim, kind:kind, cube:name, mip:MIP,
                  uniform_isCube:(ct?!!ct.isCubeTexture:false),
                  cube_faces:(ct&&ct.image&&ct.image.length)?ct.image.length:0,
                  cacheKey:mat.customProgramCacheKey()});
    });
    try{ M.forEach(function(o){ o.material.needsUpdate=true; }); _forceRender();_forceRender();_forceRender(); }catch(e){}
    state.__iblDiag={mode:mode, mip:MIP, status:'binding_verified / ibl_sampling_formula_unresolved',
                     scene_environment:(state.scene.environment?'SET':'null'), table:table};
    return JSON.stringify(state.__iblDiag);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__iblDiagFrag=function(idx){ var p=state.__iblProbe||{}; var k=Object.keys(p)[idx||0]; return k?{key:k, hasSamplerCube:/uniform samplerCube uCustomIbl/.test(p[k].frag), hasTextureCube:/textureCubeLodEXT\(uCustomIbl/.test(p[k].frag), frag:p[k].frag}:null; };
window.WikiWeaponViewer.__iblDiagRestore=function(){ var n=0; state.scene.traverse(function(o){ if(o.isMesh&&o.userData&&o.userData.__origMat){ o.material=o.userData.__origMat; n++; } }); try{_forceRender();}catch(e){} return n; };

/* L0：常量色硬验证（不使用纹理/uniform）+ 逐网格 onBeforeRender 取证 */
/* ===== 源驱动正式链 __srcChain：逐材质源 cube + 源纹理 + 源公式 =====
   模式 off | weapon_only | crystal_only | normal | swap
   规则：weapon→qiangpi.cube / crystal→car_studio01.cube，绝不共享；scene.environment=null；
        无 PMREM；逐材质独立 samplerCube；方向变换与 LOD 未从 DXBC 恢复 → 标 sampling_unresolved */
window.WikiWeaponViewer.__srcChain=function(spec){
  spec=spec||{}; var mode=spec.mode||'off';
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Base) state.__l0Base={}; var B0=state.__l0Base;
    state.scene.environment=null;
    if(!state.__srcCubes) state.__srcCubes={};
    var BASE=(state.modelDir||'')+'src_cube/faces/';
    function cube(n){
      if(!state.__srcCubes[n]){
        var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return BASE+n+'_f'+i+'_m0.png';}));
        t.colorSpace=T.NoColorSpace;   /* 按 DDS 头 B8G8R8A8_UNORM：无 sRGB 标志，按线性数值处理 */
        t.generateMipmaps=false; t.minFilter=T.LinearFilter; t.magFilter=T.LinearFilter;
        t.wrapS=t.wrapT=T.ClampToEdgeWrapping; state.__srcCubes[n]=t;
      }
      return state.__srcCubes[n];
    }
    if(!state.__srcMats) state.__srcMats={};
    var ASSIGN={off:{weapon:null,crystal:null},
                weapon_only:{weapon:'qiangpi',crystal:null},
                crystal_only:{weapon:null,crystal:'car_studio01'},
                normal:{weapon:'qiangpi',crystal:'car_studio01'},
                swap:{weapon:'car_studio01',crystal:'qiangpi'}}[mode]||{weapon:null,crystal:null};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var items=[];
    M.forEach(function(o){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ch=((base&&base.userData)||{}).chain||{}, kind=ch.kind||null;
      var want=(kind&&ASSIGN[kind])?ASSIGN[kind]:null;
      if(!want){ o.material=base; items.push({prim:ch.prim,kind:kind,cube:null}); return; }
      var mk=key+'__'+want; var m=state.__srcMats[mk];
      if(!m){
        var tex=null; try{ tex=(state.__srcTex0&&state.__srcTex0[kind])||null; }catch(e){}
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});   /* 无 IBL 时只出源 BaseColor */
        m.userData.__cubeName=want; m.userData.__ct=cube(want); m.userData.__kind=kind;
        m.userData.__tex=tex;
        m.onBeforeCompile=function(sh){
          var ct=m.userData.__ct, tex=m.userData.__tex;
          sh.uniforms.uCustomIbl={value:ct};
          sh.uniforms.uIblStrength={value:(m.userData.__ibl===undefined?1.0:m.userData.__ibl)};
          if(tex) sh.uniforms.uTex0={value:tex};
          sh.vertexShader='varying vec3 vWdPos;\n'+sh.vertexShader;
          sh.vertexShader=sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n  vWdPos = (modelMatrix * vec4(transformed,1.0)).xyz;');
          sh.fragmentShader='varying vec3 vWdPos;\nuniform samplerCube uCustomIbl;\nuniform float uIblStrength;\n'+(tex?'uniform sampler2D uTex0;\n':'')+sh.fragmentShader;
          var body;
          if(tex){
            /* 源 BaseColor（已验证的角色绑定），再叠加该材质自己的源 IBL */
            body='vec3 albedo = texture2D(uTex0, vMapUv).rgb;\n'+
                 'vec3 Rv = normalize(vWdPos - cameraPosition);\n'+
                 'vec3 ibl = textureCube(uCustomIbl, Rv).rgb;\n'+
                 'gl_FragColor = vec4(albedo * 0.35 + ibl * uIblStrength, 1.0);';
          } else { body='gl_FragColor = vec4(0.0,0.0,0.0,1.0);'; }
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>', body);
          m.userData.__frag=sh.fragmentShader; m.userData.__sh=sh;
        };
        m.customProgramCacheKey=function(){ return 'srcChain_'+m.userData.__kind+'_'+m.userData.__cubeName; };
        state.__srcMats[mk]=m;
      }
      m.userData.__ct=cube(want); m.userData.__tex=(state.__srcTex0&&state.__srcTex0[kind])||null;
      m.map=m.userData.__tex;   /* 必须设 map，vMapUv 才在片元中存在（L2 已验证路径） */
      if(spec.ibl!==undefined){ m.userData.__ibl=Number(spec.ibl); if(m.userData.__sh) m.userData.__sh.uniforms.uIblStrength.value=Number(spec.ibl); }
      m.needsUpdate=true;
      o.material=m;
      items.push({prim:ch.prim, kind:kind, cube:want,
                  cubeSha:(want==='qiangpi'?'173d52990b3ab836':'bea649d8525cdc3e'),
                  tex:!!m.userData.__tex});
    });
    if(state.renderer){ state.renderer.toneMapping=T.NoToneMapping; state.renderer.debug.checkShaderErrors=true; }
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({mode:mode, items:items, scene_env_null:(state.scene.environment===null),
                           pmrem_used:false, dir_formula:'unresolved',
                           sampling:'sampling_unresolved', colorSpace:'per DDS B8G8R8A8_UNORM (no sRGB flag)',
                           frag_err:(function(){try{return String(Object.keys(state.__srcMats).map(function(k){return state.__srcMats[k].userData.__frag||''}).join('').match(/ERROR[^\\n]*/g)||'none');}catch(e){return 'n/a';}})()});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__srcAccept=function(spec){
  /* source 验收模式：bloom=0、无自发光、三灯全关、无后处理；不得用 exposure/灯光/toneMapping 拟合参考图 */
  spec=spec||{}; var mode=spec.mode||'ibl_off';   // ibl_off | qiangpi | car_studio01 | normal
  try{
    var T=state.THREE;
    if(state.scene) state.scene.environment=null;                       // 禁用 Three 环境路径
    if(state.renderer){ state.renderer.toneMapping=T.NoToneMapping; state.renderer.toneMappingExposure=1.0; state.renderer.debug.checkShaderErrors=true; }
    // 关后处理/bloom
    // ★ 不清空 composer（清空会打断页面渲染通道 → 无 draw call → onBeforeCompile 不触发）；只把 bloom 强度压到 0
    try{
      if(state.bloom&&state.bloom.strength!==undefined) state.bloom.strength=0;
      if(state.composer&&state.composer.passes) state.composer.passes.forEach(function(p){ if(p&&p.strength!==undefined) p.strength=0; });
      if(window.WikiWeaponViewer.__post) window.WikiWeaponViewer.__post(false);
    }catch(e){}
    // 关全部灯光
    var lights=0; if(state.scene) state.scene.traverse(function(o){ if(o.isLight){ o.visible=false; lights++; } });
    // emissive / bloom 相关开关
    state.srcIblOn=true;   // ★ 打开源 IBL 注入
    state.iblRot=0; state.iblMix=0; state.iblScale=1;
    state.srcIblOn=true; state.__srcIblEnabled=true; state.__srcAcceptMode=mode;
    try{ window.WikiWeaponViewer.__reapplyMaterialLayers({sourceIblEnabled:true, sourceIblMode:mode}); }catch(e){}
    var wantStrength=(mode==='ibl_off')?0.0:1.0;
    state.iblStrength=wantStrength;
    var swap=(mode==='car_studio01');
    state.__srcForceCube=(mode==='ibl_off'||mode==='normal')?null:(swap?'car_studio01':'qiangpi');
    var mats=[];
    if(state.scene) state.scene.traverse(function(o){
      if(!o.isMesh||!o.material) return;
      var m=o.material;
      if(m.envMap){ m.envMap=null; } m.envMapIntensity=0;               // 禁 Three envMap contribution
      if(m.emissive){ m.emissive.setRGB(0,0,0); } m.emissiveIntensity=0; m.emissiveMap=null;
      var u=(m.userData&&m.userData.__sh)?m.userData.__sh.uniforms:null;
      if(u){
        if(u.uIblStrength) u.uIblStrength.value=wantStrength;
        if(u.uIblRot) u.uIblRot.value=0; if(u.uIblMix) u.uIblMix.value=0; if(u.uIblScale) u.uIblScale.value=1;
        if(state.__srcForceCube && u.uSrcIbl){
          var nm=state.__srcForceCube; state.__srcCubeCache=state.__srcCubeCache||{};
          if(!state.__srcCubeCache[nm]){
            var B=(state.modelDir||'')+'src_cube/faces/';
            var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return B+nm+'_f'+i+'_m0.png';}));
            t.colorSpace=T.NoColorSpace; t.generateMipmaps=true; t.minFilter=T.LinearMipmapLinearFilter; t.magFilter=T.LinearFilter;
            state.__srcCubeCache[nm]=t;
          }
          u.uSrcIbl.value=state.__srcCubeCache[nm];
        }
        m.needsUpdate=true;
        mats.push({prim:(m.userData.chain&&m.userData.chain.prim), ibl:m.userData.__srcIbl,
                   strength:wantStrength, cube:u.uSrcIbl?(u.uSrcIbl.value&&u.uSrcIbl.value.name?'object':'object'):null,
                   srcEnv:m.userData.__srcEnvBright});
      }
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({mode:mode, lights_off:lights, scene_env:state.scene?state.scene.environment:null,
                           strength:wantStrength, forceCube:state.__srcForceCube, mats:mats,
                           toneMapping:state.renderer?state.renderer.toneMapping:null, exposure:state.renderer?state.renderer.toneMappingExposure:null});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__reapplyMaterialLayers=function(opts){
  opts=opts||{sourceIblEnabled:true, sourceIblMode:(state.__srcAcceptMode||null)};
  try{
    if(!state.root) return 'no_root';
    var c0=state.__cAML||0, c1=state.__cSEB||0, c2=state.__cOBV||0;      // 本次调用起点
    var n=applyMaterialLayers(state.root, opts);
    // ★ 只走渲染提交：显式 compile + render（不动 composer）
    var R=state.renderer, SC=state.scene, CAM=state.camera;
    try{ if(R&&SC&&CAM&&R.compile) R.compile(SC,CAM); }catch(e){}
    try{ if(R&&SC&&CAM) R.render(SC,CAM); }catch(e){}
    var u=[];
    (state.__srcIblMats||[]).forEach(function(m){
      var sh=m.userData&&m.userData.__sh; if(!sh) return;
      var U=sh.uniforms||{};
      u.push({ibl:m.userData.__srcIbl, srcEnv:m.userData.__srcEnvBright,
              uSrcIbl_faces:(U.uSrcIbl&&U.uSrcIbl.value&&U.uSrcIbl.value.image)?U.uSrcIbl.value.image.length:null,
              uSrcRough:(U.uSrcRough&&U.uSrcRough.value)||null,
              uIblRot:(U.uIblRot&&U.uIblRot.value)||null,
              uIblMix:(U.uIblMix&&U.uIblMix.value)||null,
              uIblScale:(U.uIblScale&&U.uIblScale.value)||null,
              uIblStrength:(U.uIblStrength&&U.uIblStrength.value)||null});
    });
    return JSON.stringify({reapplied:n, opts:opts,
      dCAML:(state.__cAML||0)-c0, dCSEB:(state.__cSEB||0)-c1, dCOBV:(state.__cOBV||0)-c2,
      emissive:(state.__emissiveState&&state.__emissiveState.summary)||null,
      uniforms:u, iblMatCount:(state.__srcIblMats||[]).length});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★★★ 新增（2026-09-20，EMISTOGGLE）：自发光两档的**运行期开关 + 只读探针**（都不写文件）。
   口径（必须照抄，不许升级）：
     · A1 `emissive_source` = `source_present_value_unreadable`（源值真实存在，但运行时排列绑定未定证）
     · A2 `emissive_approx` = `approximate`（历史近似值 0.25，恢复既有载体 emissive_gain）
   两档互不耦合、可各自单开；`enabled:false` ⇒ 逐字回到现状（applyMaterialLayers 的硬清零照旧）。 */
window.WikiWeaponViewer.__emissiveA1=function(on){
  try{
    if(on===undefined||on===null) return JSON.stringify(state.__emissiveState);
    state.__emissiveState.source.enabled=!!on;
    try{ emisRun(); }catch(e){}
    try{ if(state.root) applyMaterialLayers(state.root); }catch(e){}
    try{ _forceRender&&_forceRender(); }catch(e){}
    return JSON.stringify(state.__emissiveState);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__emissiveA2=function(on){
  try{
    if(on===undefined||on===null) return JSON.stringify(state.__emissiveState);
    state.__emissiveState.approx.enabled=!!on;
    try{ emisRun(); }catch(e){}
    try{ if(state.root) applyMaterialLayers(state.root); }catch(e){}
    try{ _forceRender&&_forceRender(); }catch(e){}
    return JSON.stringify(state.__emissiveState);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* 只读探针：两档开关状态 + 每档实际落到的 prim / intensity / emissiveMap + 来源键路径。 */
window.__emissiveState=function(){
  try{ return JSON.stringify(state.__emissiveState); }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ══════════════════════════════════════════════════════════════════════════════════════════
   ★★★ 新增（2026-09-20，CRYSTAL_WIRE2）：两个**近似档**的运行期接线 + 只读探针。

   为什么需要它：`u_cube_brightness` 与 IBL cube 选择是 Lead 允许接入的两个源项，但两者都
   只能在**材质建立时**读（uniform 值 + cube 文件路径），运行期改 state 不会重新读。
   为让验收/复核方**不必改文件、不必冷启动**就能逐档出数，这里提供**只重连 uniform** 的开关
   （不改材质参数、不改灯光、不改曝光/ACES/bloom，不引入任何值之外的比例因子）：
     · `__cubeAB('qiangpi'|'jiayuan02a'|null)`  —— 换 `uSrcIbl` / `uCustomIbl` 的 CubeTexture
     · `__cubeBrightApprox(v|null)`             —— 设 `uCubeBright` / `uCubeBrightOn`
   `null` = 撤销（回到源状态：无近似、manifest 绑定的 cube）。两者都不写文件。
   三档标注：两者都是 **approximate**（cube 为 diagnostic_selector；brightness 为源区间扫描）。
   ══════════════════════════════════════════════════════════════════════════════════════════ */
  /* ══════════════════════════════════════════════════════════════════════════════════════
     ★★★ 新增（2026-09-21，SNOWCUBE）：**产品默认环境 cube**（`viewer.json:cube_default_selection`）。
     ⚠ 源侧**没有**任何选择器决定预览用哪一套 cube ⇒ 该默认**不是源数据**，而是**产品选择**
       （authority=product_choice_20260921，fidelity=not_source_determined）。
       它只决定"进皮肤时 bind 哪套 cube"，**不**改任何渲染参数
       （exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx 全部不动），也不改任何 cube 资产。
     只对本皮肤生效：其它皮肤 viewer.json **没有**这个键 ⇒ PD_NAME() 返回 null ⇒ 整体短路 ⇒ **零回归**。
     为什么分两步（置 override + 稍后换纹理）：
       · 决定链材质 bind 哪套 cube 的是 `applyNeoxManifest()` 里的 `cubeAB`（建材质**那一刻**读
         `state.__cubeABOverride`）⇒ 必须在 open 早期就把它设好；
       · 但 `__cubeAB` 换纹理需要 `state.THREE` ⇒ 必须等 `ensureRuntime()` 之后才有效。
       两步都做，两条路都指向同一套 cube，结果一致。
     ══════════════════════════════════════════════════════════════════════════════════════ */
  function PD_NAME(){
    try{ var c=state.config&&state.config.cube_default_selection;
      return (c&&typeof c==='object'&&c.cube)?String(c.cube):null; }catch(e){ return null; }
  }
  function __cubeApplyProductDefault(){
    var want=PD_NAME();
    if(!want) return null;                                    /* 其它皮肤：短路 ⇒ 零回归 */
    if(state.__cubeProductDefaultDeclined) return null;       /* 用户明确选了"不覆盖" ⇒ 不再强加 */
    /* ① 让 applyNeoxManifest 在建材质那一刻就用对 cube（它会在建完材质后 resolve）。 */
    state.__cubeABOverride=want;
    state.__cubeProductDefaultApplied=want;
    /* ② 记一笔"稍后还要真正换一次纹理"，由 __cubeAB 幂等消费（见该函数内的消费点）。 */
    state.__cubeProductDefaultPend=want;
    var ab=window.WikiWeaponViewer.__cubeAB;
    return ab?ab(want):null;                                  /* THREE 未就绪时它会安全早返回 */
  }
  window.WikiWeaponViewer.__cubeProductDefault=function(){
    var c=(state.config&&state.config.cube_default_selection)||null;
    return JSON.stringify({has_product_default:!!c, cube:(c&&c.cube)||null,
      authority:(c&&c.authority)||null, fidelity:(c&&c.fidelity)||null,
      applied:state.__cubeProductDefaultApplied||null,
      pending:state.__cubeProductDefaultPend||null,
      declined:!!state.__cubeProductDefaultDeclined,
      override:state.__cubeABOverride||null, is_game_asset:false,
      note:c?String(c.note||''):'本皮肤 viewer.json 没有 cube_default_selection ⇒ 沿用 manifest 原绑定（零回归）'});
  };
window.WikiWeaponViewer.__cubeAB=function(which){
  try{
    var v=(which===null||which===undefined)?null:String(which).trim().toLowerCase();
    /* ★ 改动（2026-09-20，CUBE_PICKER）：白名单由写死的 `qiangpi|jiayuan02a` 放宽为
       「清册里有的名字，或 ^[a-z0-9_-]{1,64}$」—— 为的是让本轮新枚举出的源 cube（indoor /
       car_studio01 / night_clearsky …）可以被选择器选中。放宽的只是**名字可接受集**：
         · 路径分隔符 / 盘符 / `..` 仍然一律拒绝（不允许借名字做路径穿越）；
         · 清册里 status!=='source_verified' 的名字**拒绝**（不使用替代图冒充源 cube）；
         · 传 null 语义不变 = 撤销，回到 manifest 原绑定。
       不改变任何渲染参数：本函数只换 uSrcIbl/uCustomIbl 的 CubeTexture（同一条既有接线）。
       ★ 再改动（2026-09-20，MERGE_FIX）：额外放行 status==='self_authored_approximate'
         （自造近似档，**非游戏资产**）。只加这一个状态：它**只可能**来自
         data/media/weapon_skin_cubes_custom.js，因此 partial/unresolved 的拒绝纪律不变 ——
         任何源 cube 都不可能凭这个状态混进来。**不得**把自造档 status 改成 source_verified
         （那是自造资产冒充源资产，属任务红线）。 */
    if(v!==null){
      var rec0=cubeIndexOf(v);
      if(rec0&&rec0.status!=='source_verified'&&rec0.status!=='self_authored_approximate')
        return JSON.stringify({err:'该 cube 未解码通过，不进入可选清单（不使用替代图）',
                               name:v, status:rec0.status});
      if(!/^[a-z0-9_\-]{1,64}$/.test(v))
        return JSON.stringify({err:'名字非法：只允许 [a-z0-9_-]，长度 1..64', name:v});
    }
    state.__cubeABOverride=v;
    /* ★ 新增（2026-09-21，SNOWCUBE）：消费产品默认待办（幂等）。
       若本次调用正是产品默认，且 THREE 已就绪 ⇒ 清掉待办；
       若调用的是别的 cube（用户显式切换）⇒ 也清掉，不覆盖用户选择。 */
    if(state.__cubeProductDefaultPend){
      if(v&&String(v)===String(state.__cubeProductDefaultPend))
        state.__cubeProductDefaultPend=null;
      else if(v===null)
        state.__cubeProductDefaultPend=null;
    }
    var T=state.THREE, out=[];
    if(!T) return JSON.stringify({err:'no THREE'});
    var nm=v||'qiangpi';
    var urls=cubeFaceUrls(nm);   /* ★ 新增：解析 skin/shared 两种来源（见 cubeFaceUrls） */
    state.__srcCubeCache=state.__srcCubeCache||{};
    if(!state.__srcCubeCache[nm]){
      var t=new T.CubeTextureLoader().load(urls);
      t.colorSpace=T.NoColorSpace; t.generateMipmaps=true; t.minFilter=T.LinearMipmapLinearFilter; t.magFilter=T.LinearFilter;
      t.wrapS=t.wrapT=T.ClampToEdgeWrapping;
      state.__srcCubeCache[nm]=t;
    }
    var ct=state.__srcCubeCache[nm];
    state.scene.traverse(function(o){
      if(!o.isMesh||!o.material) return; var m=o.material;
      var sh=m.userData&&m.userData.__sh; if(!sh) return;
      var u=sh.uniforms||{};
      if(u.uSrcIbl) u.uSrcIbl.value=ct;
      if(u.uCustomIbl) u.uCustomIbl.value=ct;
      if(o.material.userData) o.material.userData.__srcIbl=(state.__cubeABOverride||null);
      o.material.needsUpdate=true;
      out.push({prim:(m.userData.chain&&m.userData.chain.prim), srcIbl:(m.userData.__srcIbl||null)});
    });
    try{_forceRender();}catch(e){}
    var recR=cubeIndexOf(nm);
    return JSON.stringify({cube:(v||'(manifest 原绑定)'), approx:true, level:'approximate(diagnostic_selector)',
                           meshes:out.length, faces:(ct.image||[]).length,
                           /* ★ 新增（2026-09-20，CUBE_PICKER）：把该 cube 的**源侧身份**一并回报，
                              使只读验收脚本不必查清册文件即可判「选了谁 / 什么 status / 哪来的」。
                              注意 `v===null`（撤销覆盖）时 status 报 **manifest_binding**（=当前无覆盖），
                              而不是被回落到的那套 cube 的 status —— 口径与 __cubePickerState 一致。 */
                           status:(v===null?'manifest_binding':(recR?recR.status:'unknown')),
                           container:(recR?recR.container:null), row:(recR?recR.row:null),
                           sha16:(recR?recR.sha16:null), resolve:(recR?recR.resolve:'manifest'),
                           urls:urls, source_selector:'none',
                           note:'源数据里没有选择器决定预览用哪一套 cube；本入口是取证/对比工具。'});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★★★ 新增（2026-09-20，CUBE_PICKER）：**只读探针** —— 当前选中的 cube 名 + 该 cube 的 status。
   给验收/复核脚本（CDP `Runtime.evaluate`）直接读；不需要知道内部 state 字段名。
   同时镜像到 DOM：`.wv-cube-select` 的 `data-cube` / `data-status` / `data-source-selector`。 */
window.WikiWeaponViewer.__cubePickerState=function(){
  try{
    var sel=(state.cubeSelect&&state.cubeSelect.value)||state.__cubeABOverride||null;
    var idx=window.WIKI_WEAPON_SKIN_CUBES||null, rec=cubeIndexOf(sel);
    var def=(idx&&idx.default)||'qiangpi';
    var cache=state.__srcCubeCache||{};
    var tex=sel?cache[sel]:null;
    return JSON.stringify({
      selected:sel||'(manifest 原绑定)', default:def, is_default:((sel||def)===def),
      status:(rec?rec.status:'manifest_binding'),
      container:(rec?rec.container:null), row:(rec?rec.row:null), sha16:(rec?rec.sha16:null),
      dims:(rec?rec.dims:null), format:(rec?rec.format:null), n_faces:(rec?rec.n_faces:0),
      resolve:(rec?rec.resolve:'manifest'),
      faces_loaded:(tex&&tex.image)?tex.image.filter(Boolean).length:0,
      options_total:(idx&&idx.cubes)?idx.cubes.length:0,
      options_selectable:(idx&&idx.cubes)?idx.cubes.filter(function(c){return c.status==='source_verified';}).length:0,
      /* ★ 新增（2026-09-20，MERGE_FIX）：把「清册层」与「下拉层」的口径分开报，便于独立闸门核对
         「UI 里只列可用的」。options_selectable 的**既有定义（source_verified 计数=32）不改**，
         以免动到既有闸门的期望值；下拉实际项数看 options_in_dropdown。 */
      options_in_dropdown:(state.cubeSelect&&state.cubeSelect.options)?state.cubeSelect.options.length:0,
      options_optgroups:(function(){ try{ return state.cubeSelect?
            Array.prototype.map.call(state.cubeSelect.querySelectorAll('optgroup'),function(g){return g.label;}) : []; }
            catch(e){ return []; } })(),
      options_selectable_with_self:(idx&&idx.cubes)?idx.cubes.filter(function(c){
            return c.status==='source_verified'||c.status==='self_authored_approximate';}).length:0,
      options_hidden_nonusable:(idx&&idx.cubes)?idx.cubes.filter(function(c){
            return c.status!=='source_verified'&&c.status!=='self_authored_approximate';}).length:0,
      options_disabled:(state.cubeSelect)?state.cubeSelect.querySelectorAll('option[disabled]').length:0,
      self_authored:((window.WikiWeaponSkinCubesCustom&&window.WikiWeaponSkinCubesCustom.names)
            ?window.WikiWeaponSkinCubesCustom.names():[]),
      is_game_asset:(rec?rec.is_game_asset:null),
      /* ★ 新增（2026-09-21，SNOWCUBE）：**只读**产品默认字段。
         既有 `default` / `is_default` / `selected` 语义**不变**（`default` 仍是清册的
         source_verified 默认名），这里只是额外如实交代「产品默认是谁、什么 authority」。 */
      product_default:PD_NAME(),
      product_default_authority:(function(){ try{ var c=state.config&&state.config.cube_default_selection;
        return (c&&c.authority)||null; }catch(e){ return null; } })(),
      product_default_fidelity:(function(){ try{ var c=state.config&&state.config.cube_default_selection;
        return (c&&c.fidelity)||null; }catch(e){ return null; } })(),
      product_default_applied:state.__cubeProductDefaultApplied||null,
      product_default_declined:!!state.__cubeProductDefaultDeclined,
      source_selector:'none',
      note:'源数据里没有选择器决定预览用哪一套 cube；本选择器是取证/对比工具，不代表游戏的选择。',
      source_selector:'none',
      note:'源数据里没有选择器决定预览用哪一套 cube；本选择器是取证/对比工具，不代表游戏的选择。',
      counts:(idx&&idx.counts)||null});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__cubeBrightApprox=function(v){
  try{
    var n=(v===null||v===undefined)?null:Number(v);
    if(n!==null&&!isFinite(n)) return JSON.stringify({err:'v 必须是数字或 null'});
    state.__cubeBrightApproxDefault=n;
    state.__cubeBrightOn=(n!==null);
    var out=[];
    state.scene.traverse(function(o){
      if(!o.isMesh||!o.material) return; var m=o.material;
      var sh=m.userData&&m.userData.__sh; if(!sh) return;
      var u=sh.uniforms||{};
      if(u.uCubeBright){
        u.uCubeBright.value=(n===null?1.0:n);
        if(u.uCubeBrightOn) u.uCubeBrightOn.value=((n!==null&&Math.abs(n-1)>1e-9)?1.0:0.0);
        out.push({prim:(m.userData.chain&&m.userData.chain.prim), on:(u.uCubeBrightOn?u.uCubeBrightOn.value:null),
                  value:u.uCubeBright.value});
        m.needsUpdate=true;
      }
    });
    try{_forceRender();}catch(e){}
    return JSON.stringify({value:n, approx:(n!==null), level:(n===null?'absent':'approximate(source_range_scan)'),
                           basis:'Lead 裁决 C12：目标皮肤未声明 u_cube_brightness；同族源值 0.71/0.99/2.74 + 1.0 对照',
                           meshes:out.length, rows:out});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ══════════════════════════════════════════════════════════════════════════════════════════
   ★★★ 新增（2026-09-21，GI2）：**④ GI/lightmap 间接光项（源 `q_diffW`）** 的唯一写入口 + 只读探针。

   为什么需要：三个源 uniform（`u_cube_brightness` / `u_lightmap_factor` / `u_env_day2night_exposure`）
   都是**运行时逐帧 cbuffer**，只能在**材质建立时**取到（实际取不到 ⇒ 默认中性）。若要让验收方逐档扫描
   而不冷启动，必须有一个“只重连 uniform”的入口 —— 本函数即该入口。
   纪律：**只改 6 只 uniform 的 value**；不改材质参数、不改任何灯、不改 exposure/ACES/toneMapping/bloom、
   不改 `lighting_approx`、不改 `direct_light`；不触发热重编译（`needsUpdate` 不动 ⇒ 不会把别的开关重置）。
   `__gi2Gate({on:0})` / `__gi2Gate(null)` ⇒ 回到默认关 ⇒ `q_gi2Irr` 立即 `return vec3(0.0)` ⇒ 逐像素与接线前相同。
   标注等级：`uGi2Br`/`uGi2Lmf`/`uGi2Exp` = **source_present_value_unreadable**（默认中性，不冒充源值）；
   `2.761966`/`0.299805`/`1.5` = **source_immediate**；`uGi2Scale`/`uGi2Lod` = **diagnostic_scan / reconstruction**（非源值）。
   ══════════════════════════════════════════════════════════════════════════════════════════ */
window.WikiWeaponViewer.__gi2Gate=function(o){
  try{
    o=(o===null||o===undefined)?{on:0}:(o||{});
    var num=function(v,d){ var n=Number(v); return Number.isFinite(n)?n:d; };
    if(o.on!==undefined)    state.__gi2On=(num(o.on,0)>0.5);
    if(o.br!==undefined)    state.__gi2Br=num(o.br,1.0);
    if(o.lmf!==undefined)   state.__gi2Lmf=num(o.lmf,0.0);
    if(o.exp!==undefined)   state.__gi2Exp=num(o.exp,1.0);
    if(o.scale!==undefined) state.__gi2Scale=num(o.scale,1.0);
    if(o.lod!==undefined)   state.__gi2Lod=num(o.lod,5.0);
    var out=[];
    state.scene.traverse(function(mo){
      if(!mo.isMesh||!mo.material) return; var m=mo.material;
      var sh=m.userData&&m.userData.__sh; if(!sh) return;
      var u=sh.uniforms||{}; if(!u.uGi2On) return;
      u.uGi2On.value=(state.__gi2On===true)?1.0:0.0;
      if(u.uGi2Br)    u.uGi2Br.value=(state.__gi2Br===undefined?1.0:state.__gi2Br);
      if(u.uGi2Lmf)   u.uGi2Lmf.value=(state.__gi2Lmf===undefined?0.0:state.__gi2Lmf);
      if(u.uGi2Exp)   u.uGi2Exp.value=(state.__gi2Exp===undefined?1.0:state.__gi2Exp);
      if(u.uGi2Scale) u.uGi2Scale.value=(state.__gi2Scale===undefined?1.0:state.__gi2Scale);
      if(u.uGi2Lod)   u.uGi2Lod.value=(state.__gi2Lod===undefined?5.0:state.__gi2Lod);
      out.push({prim:(m.userData.chain&&m.userData.chain.prim), on:u.uGi2On.value,
                br:(u.uGi2Br?u.uGi2Br.value:null), lmf:(u.uGi2Lmf?u.uGi2Lmf.value:null),
                exp:(u.uGi2Exp?u.uGi2Exp.value:null), scale:(u.uGi2Scale?u.uGi2Scale.value:null),
                lod:(u.uGi2Lod?u.uGi2Lod.value:null),
                fragFn:((m.userData.__frag||'').indexOf('vec3 q_gi2Irr(')>=0),
                fragCall:((m.userData.__frag||'').indexOf('iblIrradiance += q_gi2Irr( geometryNormal );')>=0)});
    });
    try{_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({applied:out.length, channel:'indirect_diffuse(iblIrradiance)',
      value_level:'source_present_value_unreadable', source_immediate:[2.761966,0.299805,1.5],
      diagnostic:{scale:'非源值（诊断扫描）', lod:'重建参数（非源值）'},
      note:'④ = 源 q_diffW（asm cf349fa7 blob1 L387-392 + L396-397）；on=0 ⇒ q_gi2Irr 立即 return vec3(0.0)',
      rows:out});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__gi2State=function(){
  try{
    var rows=[];
    state.scene.traverse(function(mo){
      if(!mo.isMesh||!mo.material) return; var m=mo.material;
      var sh=m.userData&&m.userData.__sh; if(!sh) return; var u=sh.uniforms||{};
      if(!u.uGi2On) return;
      rows.push({prim:(m.userData.chain&&m.userData.chain.prim), on:u.uGi2On.value,
        br:u.uGi2Br.value, lmf:u.uGi2Lmf.value, exp:u.uGi2Exp.value,
        scale:u.uGi2Scale.value, lod:u.uGi2Lod.value, meta:(m.userData.__gi2||null)});
    });
    return JSON.stringify({state:{on:(state.__gi2On===true), br:state.__gi2Br, lmf:state.__gi2Lmf,
      exp:state.__gi2Exp, scale:state.__gi2Scale, lod:state.__gi2Lod}, mats:rows});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__iblParams=function(p){ p=p||{};  if(p.rot!==undefined) state.iblRot=Number(p.rot);
  if(p.mix!==undefined) state.iblMix=Number(p.mix);
  if(p.scale!==undefined) state.iblScale=Number(p.scale);
  if(p.strength!==undefined){ state.iblStrength=Number(p.strength); }   /* ★ 修复（2026-09-17，viewer-auditor P1-3）：原写 state.__iblStrength，全文件无人读 → strength 不持久，重建材质后回到旧值。统一为真正被读取的 state.iblStrength。 */
  try{ state.scene.traverse(function(o){ if(!o.isMesh||!o.material||!o.material.userData||!o.material.userData.__sh) return;
        var u=o.material.userData.__sh.uniforms;
        if(u.uIblRot) u.uIblRot.value=state.iblRot||0;
        if(u.uIblMix) u.uIblMix.value=state.iblMix||0;
        if(u.uIblScale) u.uIblScale.value=state.iblScale===undefined?1:state.iblScale;
        if(u.uIblStrength&&p.strength!==undefined) u.uIblStrength.value=Number(p.strength);
        o.material.needsUpdate=true; }); _forceRender(); }catch(e){}
  return JSON.stringify({rot:state.iblRot,mix:state.iblMix,scale:state.iblScale,note:'cb0[7].w / cb1[86].z / cb1[239].x 源常量未取到 → 待填真实值'});
};
window.WikiWeaponViewer.__srcTexLoad=function(){
  try{
    var T=state.THREE; if(!state.__srcTex0) state.__srcTex0={};
    var P='assets/3d/weapon_skin/1110171/src_tex/';
    /* 角色绑定（用户口径）：weapon Tex0=001a；crystal t_basecolor=001a（Tex0=001b_m 仅作掩码） */
    state.__srcTex0.weapon=new T.TextureLoader().load(P+'012_b_m.png');   /* ★ 修复（2026-09-17，viewer-auditor P2-3）：weapon 颜色槽 Tex0 的正确绑定是 001b_m
     （内容指纹 tex0_010.png ≡ 010_b_m.png + 外审 §六.4 暖金 70.7% 实测），
     原写 012_a（金色 0.0%）与本文件回退预览表 SRC（0/4 → *_b_m）及 manifest 自相矛盾。 */
    state.__srcTex0.crystal=new T.TextureLoader().load(P+'012_a.png');
    state.__srcTex0.weapon.colorSpace=T.SRGBColorSpace; state.__srcTex0.crystal.colorSpace=T.SRGBColorSpace;
    state.__srcTex0.weapon.wrapS=state.__srcTex0.weapon.wrapT=T.RepeatWrapping;
    state.__srcTex0.crystal.wrapS=state.__srcTex0.crystal.wrapT=T.RepeatWrapping;
    /* ★ 修复（2026-09-17，T3 对抗复核）：原先返回**硬编码** '012_a.png'，而本函数上面实际加载的 weapon 是 012_b_m.png（P2-3 修复）
     → 任何用本探针核对 P2-3 的人都会得到相反结论。现返回实际加载的文件名。 */
  return JSON.stringify({weapon:'src_tex/012_b_m.png（实际加载；weapon Tex0）',
                         crystal:'src_tex/012_a.png（实际加载；crystal t_basecolor）'});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l3coord=function(spec){
  spec=spec||{}; var d=spec.dir||[0,1,0];
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Base) state.__l0Base={}; var B0=state.__l0Base;
    if(!state.__coordCube){
      var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return 'assets/3d/weapon_skin/1110171/cube_coord/coord_f'+i+'.png';}));
      t.generateMipmaps=false; t.minFilter=T.NearestFilter; t.magFilter=T.NearestFilter;
      t.wrapS=t.wrapT=T.ClampToEdgeWrapping; t.colorSpace=T.NoColorSpace;
      state.__coordCube=t;
    }
    if(state.renderer){ if(state.__diagPrevTone===undefined) state.__diagPrevTone=state.renderer.toneMapping; state.renderer.toneMapping=T.NoToneMapping; }
    var expr='vec3('+Number(d[0]).toFixed(2)+','+Number(d[1]).toFixed(2)+','+Number(d[2]).toFixed(2)+')';
    if(!state.__coordMats) state.__coordMats={};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var n=0;
    M.forEach(function(o){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ch=((base&&base.userData)||{}).chain||{};
      if(ch.kind!=='weapon'){ o.material=base; return; }
      var m=state.__coordMats[key];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});
        m.userData.__expr=expr; m.userData.__ct=state.__coordCube;
        m.onBeforeCompile=function(sh){
          sh.uniforms.uCustomIbl={value:m.userData.__ct||null};
          sh.fragmentShader='uniform samplerCube uCustomIbl;\n'+sh.fragmentShader;
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(textureCube(uCustomIbl, '+m.userData.__expr+').rgb, 1.0);');
          m.userData.__frag=sh.fragmentShader; m.userData.__sh=sh;
        };
        m.customProgramCacheKey=function(){ return 'L3coord_'+m.userData.__expr; };
        state.__coordMats[key]=m;
      }
      m.userData.__expr=expr; m.userData.__ct=state.__coordCube; m.needsUpdate=true;
      o.material=m; n++;
    });
    try{_forceRender();_forceRender();}catch(e){}
    var k=Object.keys(state.__coordMats)[0], mm=state.__coordMats[k];
    var lit=null; try{ lit=String(mm.userData.__frag).match(/gl_FragColor = vec4\(textureCube\(uCustomIbl, ([^)]*)\)/); }catch(e){}
    return JSON.stringify({expr_written:expr, literal:lit?lit[1]:null,
      cacheKey:(mm&&mm.customProgramCacheKey)?mm.customProgramCacheKey():null,
      matUuid:mm?mm.uuid:null, hasUniform:!!(mm&&mm.userData&&mm.userData.__ct), weaponMeshes:n});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l3diag=function(spec){
  /* 六色诊断 cube：验证 方向→面 的真实对应；关 mip、关 toneMapping、读画布内点 */
  spec=spec||{}; var mode=spec.mode||'off';
  var DIRS={'+X':[1,0,0],'-X':[-1,0,0],'+Y':[0,1,0],'-Y':[0,-1,0],'+Z':[0,0,1],'-Z':[0,0,-1]};
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Base) state.__l0Base={};
    var B0=state.__l0Base;
    if(!state.__l3dCube){
      var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return 'assets/3d/weapon_skin/1110171/cube_diag/diagcube_f'+i+'.png';}));
      t.generateMipmaps=false; t.minFilter=T.LinearFilter; t.magFilter=T.LinearFilter;
      t.wrapS=t.wrapT=T.ClampToEdgeWrapping; t.colorSpace=T.NoColorSpace;   /* 诊断：不做默认 sRGB */
      state.__l3dCube=t;
    }
    /* ★ 修复（2026-09-17，viewer-auditor P1-1）：原为无条件赋值，会把 NoToneMapping 存回同一键，
     导致 __l3coord → __l3diag → __l3diagRestore 之后**原始 toneMapping 永久丢失**、
     后续整个会话都不再过 tone mapping（诊断泄漏进生产渲染）。与 __l3coord 同样加 undefined 守卫。 */
  if(state.renderer){ if(state.__diagPrevTone===undefined) state.__diagPrevTone=state.renderer.toneMapping; }
    if(state.renderer){ state.renderer.toneMapping=T.NoToneMapping; state.renderer.debug.checkShaderErrors=true; }
    if(!state.__l3dMats) state.__l3dMats={};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var items=[];
    M.forEach(function(o){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ch=((base&&base.userData)||{}).chain||{}, kind=ch.kind||null;
      var tgt=(mode!=='off')&&(kind==='weapon');
      if(!tgt){ o.material=base; return; }
      var d=DIRS[mode]||[1,0,0];
      var m=state.__l3dMats[key];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});
        m.userData.__dir=d; m.userData.__ct=state.__l3dCube;
        m.onBeforeCompile=function(sh){
          var dd=m.userData.__dir||[1,0,0];
          sh.uniforms.uCustomIbl={value:m.userData.__ct||null};
          sh.fragmentShader='uniform samplerCube uCustomIbl;\n'+sh.fragmentShader;
          var expr='vec3('+dd[0].toFixed(1)+','+dd[1].toFixed(1)+','+dd[2].toFixed(1)+')';
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(textureCube(uCustomIbl, '+expr+').rgb, 1.0);');
          m.userData.__frag=sh.fragmentShader; m.userData.__sh=sh;
        };
        m.customProgramCacheKey=function(){ return 'L3diag_'+((m.userData.__dir||[]).join('_')); };
        state.__l3dMats[key]=m;
      }
      m.userData.__dir=d; m.userData.__ct=state.__l3dCube; m.needsUpdate=true;
      o.material=m;
      items.push({prim:ch.prim, kind:kind, dir:mode, cube:'diag'});
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    var frag=null; try{ var k=Object.keys(state.__l3dMats)[0]; frag=state.__l3dMats[k]&&state.__l3dMats[k].userData.__frag?state.__l3dMats[k].userData.__frag.match(/textureCube\(uCustomIbl,[^)]*\)[^;]*/):null; }catch(e){}
    return JSON.stringify({level:'L3diag', mode:mode, meshes:M.length, items:items, sample_expr:String(frag)});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l3diagRestore=function(){ try{ if(state.renderer&&state.__diagPrevTone!==undefined) state.renderer.toneMapping=state.__diagPrevTone; }catch(e){} var B=state.__l0Base||{}; var n=0; state.scene.traverse(function(o){ if(o.isMesh&&B[String(o.uuid)]){ o.material=B[String(o.uuid)]; n++; } }); try{_forceRender();}catch(e){} return n; };
window.WikiWeaponViewer.__l3=function(spec){
  /* L3：textureCube(uCustomIbl, 固定方向) 六方向验证；不使用 textureCubeLodEXT（实测 EXT 不支持） */
  spec=spec||{}; var mode=spec.mode||'off';
  var DIRS={'+X':[1,0,0],'-X':[-1,0,0],'+Y':[0,1,0],'-Y':[0,-1,0],'+Z':[0,0,1],'-Z':[0,0,-1]};
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Base) state.__l0Base={};
    var B0=state.__l0Base, BASE='assets/3d/weapon_skin/1110171/cube_faces/';
    if(!state.__l3Cubes) state.__l3Cubes={};
    function cube(name){
      if(!state.__l3Cubes[name]){
        var t=new T.CubeTextureLoader().load([0,1,2,3,4,5].map(function(i){return BASE+name+'_f'+i+'.png';}));
        t.colorSpace=T.SRGBColorSpace; state.__l3Cubes[name]=t;
      }
      return state.__l3Cubes[name];
    }
    if(!state.__l3Mats) state.__l3Mats={};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var items=[];
    M.forEach(function(o){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ch=((base&&base.userData)||{}).chain||{}, kind=ch.kind||null;
      var tgt=(mode!=='off')&&(kind==='weapon');
      if(!tgt){ o.material=base; return; }
      var ct=cube(spec.cube||'qiangpi'), d=DIRS[mode]||[1,0,0];
      var mkey=key+'__'+(spec.cube||'qiangpi'); var m=state.__l3Mats[mkey];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});
        m.userData.__dir=d; m.userData.__ct=ct; m.userData.__cube=(spec.cube||'qiangpi');
        m.onBeforeCompile=function(sh){
          var dd=m.userData.__dir||[1,0,0];
          sh.uniforms.uCustomIbl={value:m.userData.__ct||null};
          sh.fragmentShader='uniform samplerCube uCustomIbl;\n'+sh.fragmentShader;
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(textureCube(uCustomIbl, normalize(vec3('+dd[0]+'.0,'+dd[1]+'.0,'+dd[2]+'.0+0.0))).rgb, 1.0);');
          m.userData.__sh=sh;
        };
        m.customProgramCacheKey=function(){ return 'L3_'+((m.userData.__cube||'qiangpi'))+'_dir_'+((m.userData.__dir||[]).join('_')); };
        state.__l3Mats[mkey]=m;
      }
      m.userData.__dir=d; m.userData.__ct=ct; m.userData.__cube=(spec.cube||'qiangpi');
      if(m.userData.__sh){ m.userData.__sh.uniforms.uCustomIbl.value=ct; }
      m.needsUpdate=true;
      o.material=m;
      items.push({prim:ch.prim, kind:kind, dir:mode, cube:(spec.cube||'qiangpi'),   /* ★ 修复（2026-09-17，审查员 P2-2）：原硬编码 'qiangpi'，
                                     导致 __l3({cube:'car_studio01'}) 时报告与实际所用自相矛盾 */
                  cubeFaces:(ct.image&&ct.image.length)?ct.image.length:0});
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({level:'L3', mode:mode, meshes:M.length, items:items,
                           ext_lod:!!(state.renderer&&state.renderer.getContext&&state.renderer.getContext().getExtension('EXT_shader_texture_lod'))});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l2=function(spec){
  /* L2：采样已验证的 001a 二维贴图并直接输出（验纹理 uniform + UV 通路） */
  spec=spec||{}; var mode=spec.mode||'off';   /* off | tex */
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Base) state.__l0Base={};
    var B0=state.__l0Base;
    if(!state.__l2Mats) state.__l2Mats={};
    if(!state.__l2Tex){
      state.__l2Tex=new T.TextureLoader().load('assets/3d/weapon_skin/1110171/src_tex/010_a.png?v=2');
      state.__l2Tex.colorSpace=T.SRGBColorSpace;
      state.__l2Tex.wrapS=state.__l2Tex.wrapT=T.RepeatWrapping;
    }
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var items=[];
    M.forEach(function(o){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ch=((base&&base.userData)||{}).chain||{};
      var kind=ch.kind||null;
      var tgt=(mode!=='off')&&(kind==='weapon');
      if(!tgt){ o.material=base; return; }
      var m=state.__l2Mats[key];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false, map:state.__l2Tex});
        m.onBeforeCompile=function(sh){
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(texture2D(map, vMapUv).rgb, 1.0);');
        };
        m.customProgramCacheKey=function(){ return 'L2_diagTex_'+key.slice(0,6); };
        state.__l2Mats[key]=m;
      }
      m.map=state.__l2Tex; m.needsUpdate=true;
      o.material=m;
      items.push({prim:ch.prim, kind:kind, tex:'src_tex/010_a.png', hasMap:!!m.map});
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({level:'L2', mode:mode, meshes:M.length, items:items,
                           tex_loaded:!!(state.__l2Tex&&state.__l2Tex.image)});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l1=function(spec){
  /* L1：uniform vec3 uDiagColor 红/绿两态（机制与已通过的 L0 相同，仅把常量换成 uniform） */
  spec=spec||{}; var mode=spec.mode||'off';   /* off | red | green */
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l1Mats) state.__l1Mats={};
    if(!state.__l0Base) state.__l0Base={};
    var B0=state.__l0Base;
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var items=[], drew=[];
    M.forEach(function(o,i){
      var key=String(o.uuid);
      if(!B0[key]) B0[key]=o.material;
      var base=B0[key], ud=(base&&base.userData)||{};
      var ch=ud.chain||{};
      var kind=ch.kind||null;
      var tgt=(mode!=='off')&&(kind==='weapon');
      if(!tgt){ o.material=base; if(mode!=='off') items.push({prim:ch.prim,kind:kind,skipped:true}); return; }
      var m=state.__l1Mats[key];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});
        m.onBeforeCompile=function(sh){
          sh.uniforms.uDiagColor={value:new T.Color((m.userData.__mode||mode)==='green'?0x00ff00:0xff0000)};
          sh.fragmentShader='uniform vec3 uDiagColor;\n'+sh.fragmentShader;
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(uDiagColor, 1.0);');
          m.userData.__sh=sh;
        };
        m.customProgramCacheKey=function(){ return 'L1_uDiagColor_'+(m.userData.__mode||'none'); };
        state.__l1Mats[key]=m;
      }
      m.userData.__mode=mode;
      var _col=(mode==='green')?0x00ff00:0xff0000;
      if(m.userData.__sh&&m.userData.__sh.uniforms.uDiagColor){ m.userData.__sh.uniforms.uDiagColor.value.set(_col); }
      try{ state.scene.traverse(function(o2){ if(o2.isMesh&&o2.material&&o2.material.userData&&o2.material.userData.__sh&&o2.material.userData.__sh.uniforms&&o2.material.userData.__sh.uniforms.uDiagColor){ o2.material.userData.__sh.uniforms.uDiagColor.value.set(_col); } }); }catch(e){}
      m.needsUpdate=true;
      o.material=m;
      items.push({prim:ch.prim, kind:kind, matUuid:String(m.uuid).slice(0,8), cacheKey:m.customProgramCacheKey()});
    });
    try{_forceRender();_forceRender();_forceRender();}catch(e){}
    state.__l1={mode:mode, items:items, meshes:M.length, scene_environment:(state.scene.environment?'SET':'null')};
    return JSON.stringify(state.__l1);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l0=function(spec){
  spec=spec||{}; var mode=spec.mode||'off';   /* off | weapon | crystal | both */
  try{
    var T=state.THREE; if(!T||!state.scene) return 'ERR no THREE/scene';
    if(!state.__l0Draws) state.__l0Draws=[];
    state.__l0Draws.length=0;
    state.__l0Frame=(state.__l0Frame||0)+1;
    var B0=state.__l0Base||{};
    var M=[]; state.scene.traverse(function(o){ if(!o.isMesh) return; var mud=(o.material&&o.material.userData)||{}; if(mud.neox||mud.chain||B0[String(o.uuid)]) M.push(o); });
    var table=[];
    M.forEach(function(o,i){
      var ch=(o.material.userData.chain)||{}; var kind=ch.kind||'?';
      var tgt=(mode==='both')||(mode==='weapon'&&kind==='weapon')||(mode==='crystal'&&kind==='crystal');
      if(!state.__l0Base) state.__l0Base={};
      var _mu=String(o.uuid);
      if(!state.__l0Base[_mu]) state.__l0Base[_mu]=o.material;   /* 干净快照按 mesh uuid */
      o.material=state.__l0Base[_mu];                          /* ★ 每态都从干净快照还原，消除态间泄漏 */
      if(tgt){
        var mat=new T.MeshBasicMaterial({color:0xffffff, toneMapped:false, fog:false});
        mat.onBeforeCompile=function(sh){
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',
            'gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);');
          state.__l0Frag=sh.fragmentShader;
        };
        mat.customProgramCacheKey=function(){ return 'L0_red_'+kind+'_'+i; };
        o.material=mat;
      } else {
        o.material=(state.__l0Base&&state.__l0Base[String(o.uuid)])||o.material;
      }
      if(!o.userData.__l0Hook){
        o.userData.__l0Hook=true;
        o.onBeforeRender=function(renderer,scene,camera,geometry,material,group){
          if(state.__l0Draws.length<80) state.__l0Draws.push({
            frame:state.__l0Frame, prim:(material&&material.userData&&material.userData.chain)?material.userData.chain.prim:null,
            meshUuid:String(o.uuid).slice(0,8), matUuid:String(material&&material.uuid).slice(0,8),
            matType:(material&&material.type)||null, version:(material&&material.version)||null,
            cacheKey:(material&&material.customProgramCacheKey)?material.customProgramCacheKey():null,
            visible:!!o.visible, renderOrder:o.renderOrder});
        };
      }
      table.push({prim:ch.prim, kind:kind, targeted:!!tgt,
                  meshUuid:String(o.uuid).slice(0,8),
                  matUuid:String(o.material.uuid).slice(0,8),
                  matType:o.material.type,
                  cacheKey:(o.material.customProgramCacheKey?o.material.customProgramCacheKey():null)});
    });
    try{ _forceRender();_forceRender();_forceRender(); }catch(e){}
    state.__l0={mode:mode, table:table, draws:state.__l0Draws.slice(), frag_has_red:(state.__l0Frag||'').indexOf('vec4(1.0, 0.0, 0.0, 1.0)')>=0,
                programs:(state.renderer&&state.renderer.info&&state.renderer.info.programs)?state.renderer.info.programs.length:null};
    return JSON.stringify({mode:mode, frag_has_red:state.__l0.frag_has_red, programs:state.__l0.programs, draws:state.__l0.draws.length, table:table});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.WikiWeaponViewer.__l0Info=function(){ return JSON.stringify(state.__l0||{}); };
window.WikiWeaponViewer.__l0Restore=function(){ var n=0; var B=state.__l0Base||{};
  state.scene.traverse(function(o){ if(!o.isMesh) return; var m=B[String(o.uuid)]; if(m){ o.material=m; n++; } });
  try{_forceRender();}catch(e){} return n; };
/* ★ 新增（2026-09-17）补切线：GLB 的 7 个 primitive 只有 NORMAL/POSITION/TEXCOORD_0，
   **没有 TANGENT**（实测属性集 = ['NORMAL','POSITION','TEXCOORD_0']）。
   Three 在缺切线时只能用导数法（screen-space derivative）推算 TBN，
   在硬边/低模上方向不可靠 → 法线贴图细节看起来"错乱"。这是用户反馈"纹理乱"的一个真实机制。
   这里按业界标准的逐三角累加 + Gram-Schmidt 正交化补出 tangent（w 存手性），
   与 three 的 computeTangents 同法。只需算一次（几何是静态的）。
   代价：每个顶点多 4 个 float；收益：normalMap 走 USE_TANGENT 的正确切线空间。 */
function computeVertexTangents(geo){
  try{
    var T=state.THREE;
    if(!geo||!T) return false;
    if(geo.attributes.tangent) return true;
    var pos=geo.attributes.position, nor=geo.attributes.normal, uv=geo.attributes.uv;
    if(!pos||!nor||!uv) return false;
    var idx=geo.index, nv=pos.count;
    var t1=new Float32Array(nv*3), t2=new Float32Array(nv*3);
    var vA=new T.Vector3(), vB=new T.Vector3(), vC=new T.Vector3();
    var x1=new T.Vector3(), x2=new T.Vector3(), sd=new T.Vector3(), td=new T.Vector3();
    var tri = idx ? (idx.count/3) : (nv/3);
    for(var f=0; f<tri; f++){
      var i0=idx?idx.getX(f*3):f*3, i1=idx?idx.getX(f*3+1):f*3+1, i2=idx?idx.getX(f*3+2):f*3+2;
      vA.fromBufferAttribute(pos,i0); vB.fromBufferAttribute(pos,i1); vC.fromBufferAttribute(pos,i2);
      var ua=uv.getX(i0), va=uv.getY(i0), ub=uv.getX(i1), vb=uv.getY(i1), uc=uv.getX(i2), vc=uv.getY(i2);
      x1.subVectors(vB,vA); x2.subVectors(vC,vA);
      var s1=ub-ua, s2=uc-ua, q1=vb-va, q2=vc-va;
      var det=s1*q2 - s2*q1;
      var r = (Math.abs(det) < 1e-12) ? 0.0 : 1.0/det;
      sd.set((q2*x1.x - q1*x2.x)*r, (q2*x1.y - q1*x2.y)*r, (q2*x1.z - q1*x2.z)*r);
      td.set((s1*x2.x - s2*x1.x)*r, (s1*x2.y - s2*x1.y)*r, (s1*x2.z - s2*x1.z)*r);
      var ii=[i0,i1,i2];
      for(var k=0;k<3;k++){ var m=ii[k]*3;
        t1[m]+=sd.x; t1[m+1]+=sd.y; t1[m+2]+=sd.z;
        t2[m]+=td.x; t2[m+1]+=td.y; t2[m+2]+=td.z; }
    }
    var out=new Float32Array(nv*4);
    var n=new T.Vector3(), tv=new T.Vector3(), bv=new T.Vector3(), cv=new T.Vector3();
    for(var a=0;a<nv;a++){
      n.fromBufferAttribute(nor,a);
      tv.set(t1[a*3],t1[a*3+1],t1[a*3+2]);
      bv.set(t2[a*3],t2[a*3+1],t2[a*3+2]);
      /* Gram-Schmidt：t = normalize(t - n·(n·t))，全部用标量运算，避免向量原地修改串味 */
      var nx=n.x, ny=n.y, nz=n.z;
      var nl=Math.sqrt(nx*nx+ny*ny+nz*nz) || 1.0; nx/=nl; ny/=nl; nz/=nl;
      var d = tv.x*nx + tv.y*ny + tv.z*nz;
      var ox = tv.x - nx*d, oy = tv.y - ny*d, oz = tv.z - nz*d;
      var ol = Math.sqrt(ox*ox+oy*oy+oz*oz);
      if(ol < 1e-8){ ox=0; oy=0; oz=0; }
      else { ox/=ol; oy/=ol; oz/=ol; }
      cv.set(oy*bv.z - oz*bv.y, oz*bv.x - ox*bv.z, ox*bv.y - oy*bv.x);  /* cross(t, b) */
      var sgn = (cv.x*nx + cv.y*ny + cv.z*nz) < 0.0 ? -1.0 : 1.0;
      out[a*4]=ox; out[a*4+1]=oy; out[a*4+2]=oz; out[a*4+3]=sgn;
    }
    geo.setAttribute('tangent', new T.BufferAttribute(out,4));
    return true;
  }catch(e){ return false; }
}

window.WikiWeaponViewer.applyDebugUi=function(on){
  /* ★★ 更正（2026-09-17）—— 这是一次由我造成的回归，已撤销：
     本函数原**从未定义**，L1597 的调用被 try/catch 吞掉 = 本就什么都不做。
     我先前"补上真实现"时让它**默认隐藏 `.wv-params` 与 `.wv-tools`**，
     但 **`.wv-tools` 是用户的控件栏**（形态 / 视角 / 复位视角 / 旋转 / SFX / 全屏），
     而 L1597 每次加载模型都会调用它 → **用户整条控件被隐藏**。
     现恢复为**不改变任何 UI 状态**的安全实现：只记录状态并返回值，供探针查询。
     需要临时隐藏面板做无 UI 截图时，请显式调用 `__hidePanels(true)`。 */
  state.__debugUi=(on===true);
  return JSON.stringify({noop:true, note:'applyDebugUi 不再改动 UI；如需隐藏请用 __hidePanels(true)'});
};
/* ★ applyParamsJSON 定义在模块级（与导出同一作用域）——
   原先定义在初始化闭包内，导出处引用不到（曾报 applyParamsJSON is not defined）。 */
function applyParamsJSON(raw){
      let o=null;
      try{ o=(typeof raw==='string')?JSON.parse(raw):raw; }
      catch(e){ return {ok:false, err:'JSON 解析失败：'+String((e&&e.message)||e)}; }
      if(!o||typeof o!=='object') return {ok:false, err:'内容不是对象'};
      const T=state.THREE, cam=state.camera, ctl=state.controls;
      if(!T||!cam||!ctl) return {ok:false, err:'查看器尚未就绪'};
      const applied=[], skipped=[];
      try{
        if(o.state&&state.stateSelect){
          const has=Array.prototype.some.call(state.stateSelect.options,op=>op.value===o.state);
          if(has&&state.stateSelect.value!==o.state){
            state.stateSelect.value=o.state;
            state.stateSelect.dispatchEvent(new Event('change',{bubbles:true}));
            applied.push('state='+o.state+'(reload)');
          } else if(!has) skipped.push('state(无此形态)');
        }
        if(Array.isArray(o.target)&&o.target.length===3){ ctl.target.fromArray(o.target.map(Number)); applied.push('target'); }
        const dist=Number(o.distance);
        if(Array.isArray(o.position)&&o.position.length===3){
          let p=new T.Vector3().fromArray(o.position.map(Number));
          if(Number.isFinite(dist)&&dist>0){
            const off=p.clone().sub(ctl.target);
            if(off.lengthSq()>1e-12) p=ctl.target.clone().addScaledVector(off.normalize(),dist);
          }
          cam.position.copy(p); applied.push('position');
        } else if(Number.isFinite(dist)&&dist>0){
          const off=new T.Vector3().subVectors(cam.position,ctl.target);
          if(off.lengthSq()>1e-12) cam.position.copy(ctl.target).addScaledVector(off.normalize(),dist);
          applied.push('distance');
        }
        if(Array.isArray(o.up)&&o.up.length===3){ cam.up.fromArray(o.up.map(Number)); if(cam.up.lengthSq()>1e-12)cam.up.normalize(); applied.push('up'); }
        if(Number.isFinite(Number(o.fov))&&Number(o.fov)>0){ cam.fov=Number(o.fov); cam.updateProjectionMatrix(); applied.push('fov'); }
        if(Number.isFinite(Number(o.span))){ state.fitSpan=Number(o.span); applied.push('span'); }
        cam.lookAt(ctl.target); cam.updateMatrixWorld(true);
        if(state.root){
          const mr=o.model_rot||{};
          if(Array.isArray(mr.quat)&&mr.quat.length===4){
            state.root.quaternion.fromArray(mr.quat.map(Number));
            if(state.root.quaternion.lengthSq()>1e-12) state.root.quaternion.normalize();
            applied.push('model_rot.quat');
          } else if(Number.isFinite(Number(mr.yaw_deg))){
            const y=Number(mr.yaw_deg)*Math.PI/180;
            state.root.quaternion.set(0,Math.sin(y/2),0,Math.cos(y/2));
            applied.push('model_rot.yaw_deg');
          } else if(Array.isArray(mr.euler_deg)&&mr.euler_deg.length===3){
            state.root.quaternion.setFromEuler(new T.Euler(mr.euler_deg.map(v=>Number(v)*Math.PI/180),'XYZ'));
            applied.push('model_rot.euler_deg');
          } else skipped.push('model_rot');
          state.root.updateMatrixWorld(true);
        }
        try{ clearTrackballState(); }catch(e){}
        if(ctl.update) ctl.update();
        renderOnce(); updateParams();
        return {ok:true, applied:applied, skipped:skipped};
      }catch(e){ return {ok:false, err:String((e&&e.message)||e), applied:applied}; }
    }
window.__applyParamsJSON=applyParamsJSON;   /* 供初始化闭包里的按钮处理调用 */
/* ★ 新增（2026-09-18，用户令 Task3）：运行证据验收导出（只读）。
   记录最终 mesh.material 的 UUID、材质创建者、实际贴图 src、cube 六面 src、
   本次编译所用 shader 的特征（是否为我们的 radiance 覆写 / 是否残留叠加实现），
   以及环境贡献是否只进入一次。**不修改任何状态。** */
window.__acceptanceReport=function(){
  var out={};
  try{
    out.viewer_sha=window.__VIEWER_SHA||null;
    out.canvas=[state.renderer.domElement.width, state.renderer.domElement.height];
    out.programCount=(state.renderer.info&&state.renderer.info.programs)?state.renderer.info.programs.length:null;
    out.meshes=[];
    if(state.scene) state.scene.traverse(function(o){
      if(!o.isMesh) return;
      var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.chain) return;
      var ud=mm.userData, sh=ud.__sh, f=ud.__frag||'';
      var srcOf=function(t){ try{ return (t&&t.image&&t.image.src)?t.image.src.split('/').slice(-2).join('/'):null; }catch(e){ return null; } };
      out.meshes.push({
        mesh:o.name||'(unnamed)', mesh_uuid:o.uuid,
        mat_uuid:mm.uuid, mat_type:mm.type, mat_name:mm.name||null,
        created_by:(ud.chain&&ud.chain.creator)||'applyNeoxManifest',
        chain_prim:ud.chain.prim, kind:ud.chain.kind,
        map:srcOf(mm.map), normal_map:srcOf(mm.normalMap),
        roughness_map:srcOf(mm.roughnessMap), metalness_map:srcOf(mm.metalnessMap),
        envMap:srcOf(mm.envMap),
        ibl_faces:(sh&&sh.uniforms&&sh.uniforms.uCustomIbl&&sh.uniforms.uCustomIbl.value&&sh.uniforms.uCustomIbl.value.image)
          ? sh.uniforms.uCustomIbl.value.image.map(function(im){return im&&im.src?im.src.split('/').pop():null;}) : null,
        /* ★ 新增（2026-09-18，task-13 B）：逐材质 env 模式 + 已解析面数，供"六面坍缩不得冒充 source_ibl"验收直接读数。 */
        env_mode:(ud.neox&&ud.neox.environment)||null,
        ibl_faces_count:(ud.neox&&ud.neox.ibl_faces_resolved!==undefined)?ud.neox.ibl_faces_resolved:null,
        cube_dir_err:(ud.neox&&ud.neox.cube_dir_err)||null,
        /* ★ 新增（2026-09-18，task-39 P0-3）：逐 mesh 的族/必需槽/缺项/白名单/失败与**可见性**，
           使被 fail-closed 隐藏的材质在验收报告里可被直接识别（不再"悄悄消失"）。 */
        family:(ud.neox&&ud.neox.family)||(ud.chain&&ud.chain.family)||null,
        family_source:(ud.neox&&ud.neox.family_source)||(ud.chain&&ud.chain.family_source)||null,
        required_slots:(ud.neox&&ud.neox.required_slots)||(ud.chain&&ud.chain.required_slots)||null,
        runtime_missing:(ud.neox&&ud.neox.runtime_missing)||(ud.chain&&ud.chain.runtime_missing)||null,
        declared_unlocated:(ud.neox&&ud.neox.declared_unlocated)||(ud.chain&&ud.chain.declared_unlocated)||[],
        albedo_slot:(ud.neox&&ud.neox.albedo_slot)||(ud.chain&&ud.chain.albedo_slot)||null,
        whitelist_no_base:!!(ud.neox&&ud.neox.whitelist_no_base),
        map_role:(ud.neox&&ud.neox.map_role)||null,
        fail_closed:!!(ud.neox&&ud.neox.fail_closed),
        mesh_visible:!!o.visible, mat_visible:!!mm.visible,
        /* ★ 新增（2026-09-19，task-49 附加 2）：`pending_hidden` 逐 prim 镜像 —— 与 `__texReady().pending_hidden_total`
           同源（读 `userData.__pendingHidden`），**与 fail-closed 的 `fail_closed`/`status` 分列**，不混用、默认不打印。 */
        pending_hidden:!!ud.__pendingHidden,
        /* ★ 新增（2026-09-18，task-40）：IBL 就绪门读数进验收报告（六面未齐时 envMap_bound=false 可判）。 */
        tex_faces_loaded:(function(){ try{ var c=(sh&&sh.uniforms&&sh.uniforms.uCustomIbl&&sh.uniforms.uCustomIbl.value)||null;
          var im=c&&c.image; if(!im||!im.length) return 0; var n=0;
          for(var i=0;i<im.length;i++){ var e=im[i];
            if(e&&(e.complete===undefined||e.complete)&&(e.naturalWidth===undefined||e.naturalWidth>0)) n++; }
          return n; }catch(e){ return 0; } })(),
        tex_faces_total:6,
        tex_envMap_bound:!!mm.envMap,
        tex_radiance_bound:!!(sh&&sh.uniforms&&sh.uniforms.uCustomIbl&&sh.uniforms.uCustomIbl.value),
        tex_deferred_retries:(state.__iblRebindTries||0),
        status:(ud.neox&&ud.neox.fail_closed)?((mm.visible)?'failed_visible_diag':'failed_hidden'):'applied',
        uIblScale:(sh&&sh.uniforms&&sh.uniforms.uIblScale)?sh.uniforms.uIblScale.value:null,
        geometry_has_tangent:!!(o.geometry&&o.geometry.attributes&&o.geometry.attributes.tangent),
        source_env_bright:ud.__srcEnvBright||null,
        frag_len:f.length,
        frag_has_our_radiance_override:/q_Rr\s*=/.test(f),
        frag_has_additive_outgoinglight:/outgoingLight\s*\+=/.test(f),
        frag_has_04_F0:/vec3\( 0\.04 \)/.test(f),
        frag_has_079956:/0\.079956/.test(f),
        transparent:!!mm.transparent, opacity:mm.opacity, alphaTest:mm.alphaTest,
        blending:mm.blending, side:mm.side, depthTest:mm.depthTest, depthWrite:mm.depthWrite
      });
    });
    /* ★ 新增（2026-09-19，task-49 附加 2）：`pending_hidden_total` 计数（与 `__texReady()` 同源口径；
       仅统计窗口期"暂不提交渲染"的 prim，**与 fail-closed 的隐藏完全分列**）。 */
    out.pending_hidden_total = (out.meshes||[]).filter(function(m){ return m.pending_hidden===true; }).length;
    out.env_enters_once = out.meshes.every(function(m){
      return m.frag_has_our_radiance_override===true && m.frag_has_additive_outgoinglight===false;
    });
  }catch(e){ out.err=String((e&&e.message)||e); }
  return JSON.stringify(out, null, 1);
};
/* ★ 新增（2026-09-18，shader-auditor，task-18）：**只读**逐 mesh 几何/可见性探针。
   用途：定位「材质从未被编译」（`__acceptanceReport.frag_len=0`）—— 注入只写在 `onBeforeCompile` 里，
   只有该 mesh **真的被渲染**才会执行；判据是顶点数 / 世界包围盒 / 可见性链 / 视锥球，
   而不是注入安装点的下标假设。本函数**只读**：不改材质、不改可见性、不碰 manifest。 */
window.__meshDump=function(){
  var out=[]; try{
    var T=state.THREE;
    if(!state.scene){ return JSON.stringify({err:'no scene'}); }
    state.scene.traverse(function(o){
      if(!o.isMesh) return;
      var m=o.material; if(Array.isArray(m)) m=m[0];
      var ud=(m&&m.userData)||{}, ch=ud.chain||{};
      var g=o.geometry||{}, pos=g.attributes&&g.attributes.position;
      var sz=null, ctr=null;
      try{ if(T&&T.Box3){ var bb=new T.Box3().setFromObject(o), s=new T.Vector3(), c=new T.Vector3();
           bb.getSize(s); bb.getCenter(c);
           sz=[+s.x.toFixed(4),+s.y.toFixed(4),+s.z.toFixed(4)];
           ctr=[+c.x.toFixed(3),+c.y.toFixed(3),+c.z.toFixed(3)]; } }catch(e){}
      var visChain=true, p=o; while(p){ if(p.visible===false){ visChain=false; break; } p=p.parent; }
      out.push({name:String(o.name||'').slice(0,40), chain_prim:(ch.prim!==undefined?ch.prim:null), kind:ch.kind||null,
        visible:o.visible, visibleChain:visChain, frustumCulled:o.frustumCulled,
        vertices:(pos?pos.count:null), indexed:!!g.index, groups:((g.groups||[]).length),
        bboxSize:sz, bboxCenter:ctr,
        mat:((m&&m.type)||null), matUuid:((m&&m.uuid)||null), side:(m?m.side:null),
        matVisible:!!(m&&m.visible), hasMap:!!(m&&m.map), hasEnv:!!(m&&m.envMap),
        fragLen:((ud.__frag||'').length||0), obc:(typeof (m&&m.onBeforeCompile)==='function'),
        sphere:(function(){ try{ if(!g.boundingSphere) return null; var b=g.boundingSphere.clone().applyMatrix4(o.matrixWorld);
          return {c:[+b.center.x.toFixed(3),+b.center.y.toFixed(3),+b.center.z.toFixed(3)], r:+Math.max(b.radius,1e-6).toFixed(4)}; }catch(e){ return null; } })(),
        inFrustum:(function(){ try{ if(!T||!T.Frustum||!state.camera||!g.boundingSphere) return null;
          var fr=new T.Frustum();
          fr.setFromProjectionMatrix(new T.Matrix4().multiplyMatrices(state.camera.projectionMatrix,state.camera.matrixWorldInverse));
          var b=g.boundingSphere.clone().applyMatrix4(o.matrixWorld);
          return fr.intersectsSphere(b); }catch(e){ return null; } })()});
    });
  }catch(e){ out={err:String((e&&e.message)||e)}; }
  return JSON.stringify(out, null, 1);
};
/* ★ 新增（2026-09-18，shader-auditor，task-40）：只读 `__texReady()` —— IBL 就绪门的可观测读数。
   逐 cube：`{cube, faces_loaded, faces_total, ready, failed, bound, deferred_retries}`；
   逐材质：`{prim, kind, family, faces_loaded, faces_total, envMap_bound, radiance_bound,
             deferred_retries, envMode, tex_ready}`。只读：不改材质、不触发加载、不动 manifest。 */
/* ★ 新增（2026-09-19，shader-auditor，task-62）：**历史硬编码贴图的显式开关**（默认关）。
   目前只有一个：`src_tex/gpk_1229.png`（1110171 独有的内容候选、manifest 0 命中）。
   默认 `state.__useLegacyDetail!==true` ⇒ **不发起任何请求**（消除其余皮肤的 404），也不顶替任何槽位；
   显式 `__legacyDetail(true)` 才加载（仅供 1110171 的历史 A/B）。 */
window.__legacyDetail=function(on){ try{
  state.__useLegacyDetail=(on===true);
  return JSON.stringify({legacy:'src_tex/gpk_1229.png', loaded:(state.__useLegacyDetail===true),
    legacy_tex_missing:(state.__useLegacyDetail===true?[]:['src_tex/gpk_1229.png']),
    note:'默认 OFF ⇒ 不请求该文件、不顶替 DetailMap 槽位；仅 1110171 目录存在该文件'});
}catch(e){ return 'ERR '+((e&&e.message)||e); } };
/* ═══════════════════════════════════════════════════════════════════════════════════════════
   ★ 新增（2026-09-20，CRYSTAL_WIRE_20260920 渲染侧写手）：只读探针 `__crystalWireProbe()`。
   目的：把本任务的三件事**做成可读数**，而不是靠"看着像"：
     ① 族接线：逐 mesh 报 `chain.kind`（weapon/crystal）、`chain.family`（manifest progFamily）、
        `shader`/`shader_kind`（源 c159 声明族 vs 清单族）、crystal 注入是否真的进了片元（`crystalInj`）；
     ② 反射/高光源项：逐 mesh 读 **本次编译的真实 uniform 值** —— `uCustomIbl`（哪一套 cube）、
        `uIblScale`/`uCubeBrightOn`/`uCubeBright`/`uIblRotOn`/`uIblRot`/`uBrdfOn`/`uIrrOn`/`uBrdfOn`；
     ③ 贴图槽位：`uCrystalMask`(Tex0.r) / `uDetailMap` / `uCausticTex` / `uReflTex` / `uRefrTex` 的
        `image.src`（= 实际请求到的文件）+ 是否 image.complete（未就绪 ⇒ 不许当"已接"）。
   纪律（与既有探针一致）：**只读** —— 不写材质、不触发加载、不改 state、不碰 manifest。
   ═══════════════════════════════════════════════════════════════════════════════════════════ */
window.__crystalWireProbe=function(){
  try{
    var rows=[]; if(!state.scene) return JSON.stringify({err:'no scene'});
    var srcOf=function(t){ try{ var im=t&&t.image; var s=im&&im.src; if(!s) return null;
      var q=String(s).split('?')[0].split('/'); return q.slice(-2).join('/');
    }catch(e){ return null; } };
    var readyOf=function(t){ try{ var im=t&&t.image; if(!im) return false;
      if(im.complete===undefined&&im.naturalWidth===undefined) return true;
      return !!(im.complete&&im.naturalWidth>0); }catch(e){ return false; } };
    state.scene.traverse(function(o){
      if(!o.isMesh) return;
      var m=o.material; if(Array.isArray(m)) m=m[0];
      if(!m||!m.userData||!m.userData.chain) return;
      var ud=m.userData, sh=ud.__sh, u=(sh&&sh.uniforms)||{};
      var uv=function(k){ return (u[k]&&u[k].value!==undefined)?u[k].value:null; };
      var cube=uv('uCustomIbl');
      var cubeName=null; try{ var ci=cube&&cube.image; var cs=ci&&ci[0]&&ci[0].src;
        if(cs){ cubeName=String(cs).split('?')[0].split('/').pop().replace(/_f\d+_m0\.png$/,''); } }catch(e){}
      var cubeFaces=0; try{ var im=cube&&cube.image; if(im&&im.length){ for(var i=0;i<im.length;i++){
        var e=im[i]; if(e&&(e.complete===undefined||e.complete)&&(e.naturalWidth===undefined||e.naturalWidth>0)) cubeFaces++; } } }catch(e){}
      var fragIbl=ud.__frag||'', fragCry=ud.__fragCrystal||'';
      rows.push({
        mesh:String(o.name||'').slice(0,28), prim:(ud.chain.prim!==undefined?ud.chain.prim:null),
        kind:ud.chain.kind||null, family:ud.chain.family||null,
        shader:(ud.neox&&ud.neox.shader)||null, shader_kind:(ud.neox&&ud.neox.shader_kind)||null,
        mtl_idx:(ud.neox&&ud.neox.mtl_idx!==undefined)?ud.neox.mtl_idx:null,
        mat_type:m.type, mat_visible:!!m.visible,
        mat_metalness:(m.metalness!==undefined?m.metalness:null),
        mat_roughness:(m.roughness!==undefined?m.roughness:null),
        envMapBound:!!m.envMap, envMapIntensity:(m.envMapIntensity!==undefined?m.envMapIntensity:null),
        /* ① 晶体注入 */
        crystalInj:!!(fragCry&&fragCry.indexOf('uCrystalMask')>=0),
        crystalBlock:(ud.__crystalBlock!==undefined?ud.__crystalBlock:null),
        maskSrc:srcOf(uv('uCrystalMask')), maskReady:readyOf(uv('uCrystalMask')),
        /* ③ 槽位 */
        slot_src:{ DetailMap:srcOf(uv('uDetailMap')), t_caustic_tex:srcOf(uv('uCausticTex')),
                   t_reflection_tex:srcOf(uv('uReflTex')), t_refraction_tex:srcOf(uv('uRefrTex')) },
        slot_ready:{ DetailMap:readyOf(uv('uDetailMap')), t_caustic_tex:readyOf(uv('uCausticTex')),
                     t_reflection_tex:readyOf(uv('uReflTex')), t_refraction_tex:readyOf(uv('uRefrTex')) },
        uHasDetail:uv('uHasDetail'),
        uCrystalColor:uv('uCrystalColor'), uBaseColor:uv('uBaseColor'),
        /* ② 反射/高光源项 */
        cube:cubeName, cubeFacesLoaded:cubeFaces, cubeFacesTotal:6,
        uIblScale:uv('uIblScale'), uIblMix:uv('uIblMix'),
        uIblRotOn:uv('uIblRotOn'), uIblRot:uv('uIblRot'),
        uCubeBrightOn:uv('uCubeBrightOn'), uCubeBright:uv('uCubeBright'),
        uBrdfOn:uv('uBrdfOn'), uBaseMetal:uv('uBaseMetal'), uCrystalMetal:uv('uCrystalMetal'),
        uIrrOn:uv('uIrrOn'), uIrrLod:uv('uIrrLod'), uIrrScale:uv('uIrrScale'),
        frag_hasIblInjection:!!(fragIbl&&fragIbl.indexOf('uCustomIbl')>=0),
        progCacheKey:(function(){ try{ return (typeof m.customProgramCacheKey==='function')?String(m.customProgramCacheKey()).slice(0,80):null; }catch(e){ return 'ERR'; } })(),
        patchState:ud.__patchState||null, iblIrrSrc:(ud.__iblIrrSrc||null), brdfSrc:(ud.__brdfSrc||null),
        cubeBrightMeta:(ud.__cubeBright||null), chainRule:(ud.chain&&ud.chain.rule)||null,
        chain_textures:(ud.chain&&ud.chain.crystal_textures)||null
      });
    });
    return JSON.stringify({count:rows.length, rows:rows}, null, 1);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ═══════════════════════════════════════════════════════════════════════════════════════════════
   ★★★ 新增（2026-09-20，ENVROUTE S2）：**只读**运行时探针 `__envrouteTexProbe()` +
   weapon DetailMap 的逐像素消费证明开关 `__wpDetailPreview(on)`（诊断）。

   目的（对应任务 S3）：把「JSON 改了」与「GPU 真消费了」分开，且**不靠自述**：
     · `prog.*`      = **编译后的 GLSL 源码**（`userData.__fragCrystal/__fragWpDetail/__frag`）里的声明与采样点，
                       不是 manifest 声明；
     · `mat_bind.*`  = three 材质对象上**实际挂着的纹理**（.image.src 尾两段）；
     · `uni_bind.*`  = **live uniform** 上的纹理对象（晶体/weapon 的自定义槽）；
     · `programs[]`  = `renderer.info.programs` 逐 program：**活跃 sampler 表**（`getUniforms()`，
                       说明编译器**没有**把它当死代码消除）+ **GPU 侧实际绑定**（`gl.getUniform` 取纹理单元 →
                       `activeTexture` → `getParameter(TEXTURE_BINDING_2D/CUBE_MAP)` → 与期望纹理的
                       `__webglTexture` **按对象身份比对**）。
   纪律：**只读** —— 不改材质、不触发加载、不改 state（`__wpDetailPreview` 是显式诊断开关，默认不动）。
   ═══════════════════════════════════════════════════════════════════════════════════════════════ */
window.__envrouteTexProbe=function(){
  try{
    var R=state.renderer;
    if(!R) return JSON.stringify({err:'no renderer'});
    var gl=null; try{ gl=R.getContext?R.getContext():null; }catch(e){}
    var props=R.properties;
    var wglOf=function(t){ try{ if(!t) return null;
      if(props&&props.get){ var p=props.get(t); if(p&&p.__webglTexture) return p.__webglTexture; }
      return t.__webglTexture||null; }catch(e){ return null; } };
    var srcOf=function(t){ try{ var im=t&&t.image; var s=im&&im.src; if(!s) return null;
      return String(s).split('?')[0].split('/').slice(-2).join('/'); }catch(e){ return null; } };
    var readyOf=function(t){ try{ var im=t&&t.image; if(!im) return false;
      if(im.complete===undefined&&im.naturalWidth===undefined) return true;
      return !!(im.complete&&im.naturalWidth>0); }catch(e){ return false; } };
    var uvOf=function(u,k){ try{ return (u&&u[k]&&u[k].value!==undefined)?u[k].value:null; }catch(e){ return null; } };
    /* ---- 期望贴图集合（全部来自 live uniform / 材质对象，不读磁盘、不读 manifest）---- */
    var expected={};
    var SLOTMAP=[['uCrystalMask','Tex0'],['uDetailMap','DetailMap'],['uCausticTex','t_caustic_tex'],
                 ['uReflTex','t_reflection_tex'],['uRefrTex','t_refraction_tex'],['uWpnDetailMap','DetailMap(weapon)']];
    state.scene.traverse(function(o){ if(!o.isMesh) return;
      var m=o.material; if(Array.isArray(m)) m=m[0];
      if(!m||!m.userData||!m.userData.chain) return;
      var sh=m.userData.__sh, u=(sh&&sh.uniforms)||{}, pi=m.userData.chain.prim;
      SLOTMAP.forEach(function(p){ var t=uvOf(u,p[0]);
        if(t) expected[p[0]+'@prim'+pi]={slot:p[1], src:srcOf(t), ready:readyOf(t), wgl:wglOf(t)}; });
      [['normalMap',m.normalMap],['metalnessMap',m.metalnessMap],['roughnessMap',m.roughnessMap],
       ['emissiveMap',m.emissiveMap],['map',m.map]].forEach(function(p){
        if(p[1]) expected[p[0]+'@prim'+pi]={slot:p[0], src:srcOf(p[1]), ready:readyOf(p[1]), wgl:wglOf(p[1])}; });
    });
    /* ---- 逐 program：活跃 sampler 表 + GPU 侧实际绑定身份 ---- */
    var MARK=['uCrystalMask','uDetailMap','uCausticTex','uReflTex','uRefrTex','uWpnDetailMap','uCustomIbl'];
    var programs=[], progs=(R.info&&R.info.programs)||[];
    /* ★★ 修复（2026-09-20，ENVROUTE S2 自测发现）：`renderer.info.programs[i].fragmentShader` **不是 GLSL 源码**
       （three 在该字段上存的是 `WebGLShader` **句柄对象**）⇒ `String(p.fragmentShader)` 恒为
       `[object WebGLShader]`，markers 实测**全 false**（第一版探针就是这样，等于没读到任何证据）。
       现改为从 **linked program 实际挂着的着色器对象**读源码：
         `gl.getAttachedShaders(p.program)` → `gl.getShaderSource(shader)`，
       并取其中**含片元关键字**的那一个（不靠 attach 顺序假设）。这才是"GPU 侧那份代码"。 */
    var fragSrcOf=function(p){
      try{
        var att=gl.getAttachedShaders(p.program)||[], best=null, bestScore=-1;
        for(var k=0;k<att.length;k++){
          var s=gl.getShaderSource(att[k]); if(!s) continue;
          var sc=(s.indexOf('gl_FragColor')>=0?4:0)+(s.indexOf('pc_fragColor')>=0?4:0)
                +(s.indexOf('gl_FragDepth')>=0?4:0)+(s.indexOf('diffuseColor')>=0?2:0);
          if(sc>bestScore){ bestScore=sc; best=s; }
        }
        return best;
      }catch(e){ return null; }
    };
    for(var i=0;i<progs.length;i++){
      var p=progs[i], ck=String(p.cacheKey||'');
      var fs=fragSrcOf(p)||'';
      var marks={}; MARK.forEach(function(k){ marks[k]=fs.indexOf(k)>=0; });
      var prim=null, mm=ck.match(/crystalSrc_(\d+)_/)||ck.match(/envrouteWpDetail_(\d+)_/);
      if(mm) prim=parseInt(mm[1],10);
      var samplers=[];
      try{
        var uni=(typeof p.getUniforms==='function')?p.getUniforms():null;
        var umap=(uni&&uni.map)||null;
        if(umap&&gl){
          for(var nm in umap){ var e=umap[nm], ty=e&&e.type;
            var is2=(ty===gl.SAMPLER_2D), isC=(ty===gl.SAMPLER_CUBE);
            if(!is2&&!isC) continue;
            var unit=null, boundWgl=null, matches=[];
            try{
              var loc=gl.getUniformLocation(p.program,nm);
              if(loc){ var v=gl.getUniform(p.program,loc);
                if(typeof v==='number'){ unit=v; gl.activeTexture(gl.TEXTURE0+v);
                  boundWgl=gl.getParameter(isC?gl.TEXTURE_BINDING_CUBE_MAP:gl.TEXTURE_BINDING_2D);
                  for(var key in expected){ if(boundWgl&&expected[key].wgl&&expected[key].wgl===boundWgl) matches.push(key); } } }
            }catch(e2){}
            samplers.push({uniform:nm, type:(isC?'SAMPLER_CUBE':'SAMPLER_2D'), unit:unit,
                           bound_non_null:!!boundWgl, bound_matches:matches});
          }
        }
      }catch(e){}
      programs.push({idx:i, prim_guess:prim, cacheKeyHead:ck.slice(0,140), fragLen:fs.length,
                     usedTimes:(p.usedTimes||null), markers:marks, samplers:samplers});
    }
    /* ---- 逐 mesh：族/清单字段 / 编译后 GLSL / 材质级·uniform 级绑定 ---- */
    var meshes=[];
    state.scene.traverse(function(o){
      if(!o.isMesh) return;
      var m=o.material; if(Array.isArray(m)) m=m[0];
      if(!m||!m.userData||!m.userData.chain) return;
      var ud=m.userData, sh=ud.__sh, u=(sh&&sh.uniforms)||{};
      var f=ud.__frag||'', fc=ud.__fragCrystal||'', fw=ud.__fragWpDetail||'';
      /* ★ 修复（2026-09-20，ENVROUTE S2 自测发现）：原 `V()` 只认 Vector3/Vector4 的 `.x/.y/.z`，
         而 `uCrystalColor`/`uBaseColor` 是 **THREE.Color**（字段是 `.r/.g/.b`）⇒ 探针恒读成
         `[null,null,null]`，把"参数没生效"和"探针读不出"混为一谈。现两种都认。 */
      var V=function(x){ if(!x) return null;
        if(x.x!==undefined) return [x.x,x.y,x.z];
        if(x.r!==undefined) return [x.r,x.g,x.b];
        return null; };
      meshes.push({
        mesh:String(o.name||'').slice(0,28), prim:ud.chain.prim, kind:ud.chain.kind, family:ud.chain.family,
        family_source:ud.chain.family_source||null,
        shader:(ud.neox&&ud.neox.shader)||null, shader_kind:(ud.neox&&ud.neox.shader_kind)||null,
        declared:(ud.chain.shader_declared_by_material_c159||null),
        eff_shader:ud.chain.eff_shader||null, eff_shader_source:ud.chain.eff_shader_source||null,
        kind_mismatch:ud.chain.kind_mismatch||null,
        required_slots:ud.chain.required_slots||null, runtime_missing:ud.chain.runtime_missing||null,
        declared_unlocated:ud.chain.declared_unlocated||null,
        mesh_visible:!!o.visible, mat_visible:!!m.visible, mat_type:m.type,
        prog:{fragLen:f.length, crystalFragLen:fc.length, wpDetailFragLen:fw.length,
              has_crystal_injection:(fc.indexOf('uCrystalMask')>=0),
              has_crystal_mix_formula:(fc.indexOf('mix(q_A, q_B, q_mm)')>=0),
              has_caustic_decl:(fc.indexOf('uniform sampler2D uCausticTex')>=0),
              has_caustic_sample:(fc.indexOf('texture2D(uCausticTex')>=0),
              has_refr_decl:(fc.indexOf('uniform sampler2D uRefrTex')>=0),
              has_refr_sample:(fc.indexOf('textureLod(uRefrTex')>=0),
              has_refl_decl:(fc.indexOf('uniform sampler2D uReflTex')>=0),
              has_detail_decl:(fc.indexOf('uniform sampler2D uDetailMap')>=0),
              has_wpDetail_decl:(fw.indexOf('uniform sampler2D uWpnDetailMap')>=0),
              has_wpDetail_sample:(fw.indexOf('texture2D(uWpnDetailMap')>=0),
              has_ibl_override:(f.indexOf('uCustomIbl')>=0)},
        mat_bind:{map:srcOf(m.map), normalMap:srcOf(m.normalMap), metalnessMap:srcOf(m.metalnessMap),
                  roughnessMap:srcOf(m.roughnessMap), emissiveMap:srcOf(m.emissiveMap), envMap:srcOf(m.envMap)},
        metalness:(m.metalness!==undefined?m.metalness:null),
        roughness:(m.roughness!==undefined?m.roughness:null),
        emissive_hex:(m.emissive&&m.emissive.getHexString)?m.emissive.getHexString():null,
        emissiveIntensity:(m.emissiveIntensity!==undefined?m.emissiveIntensity:null),
        envMapIntensity:(m.envMapIntensity!==undefined?m.envMapIntensity:null),
        uni_bind:{Tex0:srcOf(uvOf(u,'uCrystalMask')), DetailMap:srcOf(uvOf(u,'uDetailMap')),
                  t_caustic_tex:srcOf(uvOf(u,'uCausticTex')), t_reflection_tex:srcOf(uvOf(u,'uReflTex')),
                  t_refraction_tex:srcOf(uvOf(u,'uRefrTex')), DetailMap_weapon:srcOf(uvOf(u,'uWpnDetailMap'))},
        uni_ready:{DetailMap:readyOf(uvOf(u,'uDetailMap')), t_caustic_tex:readyOf(uvOf(u,'uCausticTex')),
                   t_reflection_tex:readyOf(uvOf(u,'uReflTex')), t_refraction_tex:readyOf(uvOf(u,'uRefrTex')),
                   DetailMap_weapon:readyOf(uvOf(u,'uWpnDetailMap'))},
        uni_val:{uHasDetail:uvOf(u,'uHasDetail'), uLayer:uvOf(u,'uLayer'),
                 uCauOn:uvOf(u,'uCauOn'), uRefrOn:uvOf(u,'uRefrOn'), uWpnDetailOn:uvOf(u,'uWpnDetailOn'),
                 uCauParams:V(uvOf(u,'uCauParams')), uRefrParams:V(uvOf(u,'uRefrParams')),
                 uRefrColor:V(uvOf(u,'uRefrColor')), uCrystalColor:V(uvOf(u,'uCrystalColor')),
                 uBaseColor:V(uvOf(u,'uBaseColor')),
                 uEmisStrength:uvOf(u,'uEmisStrength'), uGlowOn:uvOf(u,'uGlowOn'),
                 uEmisSat:V(uvOf(u,'uEmisSat'))},
        crystal_layers:(function(){ var r=(state.__crystalLayer||[]).filter(function(x){return x.prim===ud.chain.prim;})[0]||null;
          return r?{cauReady:!!r.cauReady, refrReady:!!r.refrReady, hasCaustic:!!r.hasCaustic, hasRefl:!!r.hasRefl,
                    cauValues:r.cauValues, refrValues:r.refrValues}:null; })(),
        wp_detail:(function(){ var r=(state.__envrouteWpDetail||[]).filter(function(x){return x.prim===ud.chain.prim;})[0]||null;
          return r?{file:r.file, logical:r.logical, sha256:r.sha256, evidence_level:r.evidence_level,
                    consumed_by:r.consumed_by, slot_evidence:r.slot_evidence, formula_evidence:r.formula_evidence,
                    on:uvOf(u,'uWpnDetailOn')}:null; })()
      });
    });
    return JSON.stringify({gl:!!gl, programCount:progs.length, programs:programs,
                           expected_textures:expected, meshCount:meshes.length, meshes:meshes}, null, 1);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.__wpDetailPreview=function(on){
  try{
    state.__wpDetailPreview=!!on; var n=0, rows=[];
    (state.__envrouteWpDetail||[]).forEach(function(r){ r.on.value=(on?1.0:0.0);
      rows.push({prim:r.prim, on:r.on.value, file:r.file}); n++; });
    try{_forceRender();_forceRender();}catch(e){}
    return JSON.stringify({wpDetailPreview:!!on, mats:n, rows:rows,
      note:'诊断预览（非源行为）：uWpnDetailOn=1 ⇒ 片元 `diffuseColor.rgb = texture2D(uWpnDetailMap, vMapUv).rgb`；默认 0 = 逐像素零贡献'});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.__texReady=function(){
  try{
    var out={gate:[], meshes:[], deferred_retries:(state.__iblRebindTries||0),
             rebind_pending:!!state.__iblRebindPending, rebind_err:(state.__iblRebindErr||null),
             rebind_count:(state.__iblRebindTries||0),
             /* ★ 新增（2026-09-19，task-49 (B)+(C)）：收敛式重试的可判读数（上限 6，达上限仍缺 ⇒ exhausted=true） */
             retry_count:(state.__iblRetryCount||0), retry_cap:6,
             retry_last_missing:(state.__iblRetryLastMissing!==undefined?state.__iblRetryLastMissing:null),
             retry_exhausted:!!state.__iblRetryExhausted,
             /* ★ 新增（2026-09-19，task-49 裁决 (ii) 附加 2）：`pending_hidden` **独立计数**，
                与 fail-closed 的 hidden/failed **分列**（严禁混用；下面对 meshes 逐项累加）。 */
             pending_hidden_total:0, pendinghide:(state.__pendingHideOff===true?'off':'on'),
             /* ★ 新增（2026-09-19，task-62）：历史硬编码贴图的**未加载清单**（默认即含 gpk_1229）——
                目的是让"404 归零"这件事**在探针里可读**，而不是只能靠抓网络日志。
                `__legacyDetail(true)` 后该清单清空（只有显式要求时才去请求 1110171 独有的那个文件）。 */
             legacy_tex_missing:(state.__useLegacyDetail===true?[]:['src_tex/gpk_1229.png']),
             legacy_detail_on:(state.__useLegacyDetail===true)};
    /* ★ 任务-49 附加 2：`pending_hidden` 独立计数（与 fail-closed 的 hidden/failed 分列）——惰性统计一次。
       ★ 修复（2026-09-19，task-49；备份 wsv_bak_task49L_20260919_160128.js = 4F5630461B1EFAC1）：
       原判据读 **mesh 的 `o.userData.__pendingHidden`**，而隐藏标记实际写在 **材质 `m.userData.__pendingHidden`**
       （pendingHide 处 `m.visible=false; m.userData.__pendingHidden=true;`）⇒ 该计数**恒为 0**
       （实测窗口期 `vis="0H1H2v3v"`、`ph=[0,1]` 但 `th=0`）。现改读**材质**标记，与
       `__acceptanceReport()` 的 `ud=mm.userData` 同源 ⇒ 三源在窗口期亦应一致。 */
    try{ out.pending_hidden_total=0;
      if(state.scene) state.scene.traverse(function(o){
        var mm=(o&&o.isMesh)?(Array.isArray(o.material)?o.material[0]:o.material):null;
        if(mm&&mm.userData&&mm.userData.__pendingHidden) out.pending_hidden_total++;
      });
    }catch(e){}
    /* ★★★ 修复（2026-09-20，ENVWIRE）：`gate.bound` **恒 false** 的缺陷。
       缺陷（Lead 第一步诊断实测）：`state.__iblGate[cube].bound` 只在 L1705 初始化为 `false`，
       **全文件没有任何 `gate.bound=` 写入点**，而 `__texReady()` 又把它原样报出来
       ⇒ 探针显示 `faces_loaded=6/6 ready=true 但 bound=false`（自相矛盾），并被读成
       "环境立方体没绑上 / 360° 反射不参与"。实测反证：逐材质 `envMap_bound=true`、
       `radiance_bound=true`（uCustomIbl 六面皆就绪），且受控断开 cube 会改变 26386 px
       ⇒ cube **确实已参与着色**，是**探针字段没落地**，不是断线。

       修法（只让读数落地，不改任何渲染决策）：遍历一次材质，统计**真实绑定**到该 cube 的材质数，
       把它写成 `gate.bound` 与新增的 `bound_meshes`。判据与 L5311 的 `envMap_bound`/`radiance_bound`
       **同源**（`m.envMap===该 cube` 或 `sh.uniforms.uCustomIbl.value===该 cube`），不引入新口径。

       ⚠ 同时如实登记：`scene.environment` 为 null 是**设计**（本 viewer 走逐材质 uCustomIbl，
       多处显式置 null；见 L4269/4308/4335/4391/4467/5767）⇒ 它**不是** cube 断线的判据，
       故新增 `scene_environment` 与 `scene_environment_note` 把这件事写在读数里，避免再被误读。 */
    var G=state.__iblGate||{};
    var boundByCube={};
    try{
      if(state.scene) state.scene.traverse(function(o){
        if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0];
        if(!m) return;
        var sh=((m.userData||{}).__sh)||null;
        var cu=(sh&&sh.uniforms&&sh.uniforms.uCustomIbl&&sh.uniforms.uCustomIbl.value)||m.envMap||null;
        if(!cu) return;
        var nm=null;
        try{ var ci=cu.image, cs=ci&&ci[0]&&ci[0].src;
             if(cs) nm=String(cs).split('?')[0].split('/').pop().replace(/_f\d+_m0\.png$/,''); }catch(e){}
        if(!nm) return;
        boundByCube[nm]=(boundByCube[nm]||0)+1;
      });
    }catch(e){}
    Object.keys(G).forEach(function(k){ var g=G[k]||{};
      var bm=boundByCube[k]||0;
      g.bound=(bm>0);                       /* ← 缺陷修复：把真实绑定写回 gate（此前无任何写入点） */
      out.gate.push({cube:k, faces_loaded:g.loaded||0, faces_total:g.total||6, ready:!!g.ready,
                     failed:!!g.failed, bound:!!g.bound, bound_meshes:bm,
                     deferred_retries:out.deferred_retries,
                     bound_basis:'材质 envMap / uCustomIbl 实绑（本遍历计数）'}); });
    out.scene_environment=(state.scene&&state.scene.environment)?'SET':'null';
    out.scene_environment_note='null 是设计（逐材质 uCustomIbl，不走 scene-wide）；不代表 cube 未绑定';
    if(state.scene) state.scene.traverse(function(o){
      if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0];
      if(!m||!m.userData||!m.userData.chain) return;
      var ud=m.userData, sh=ud.__sh, u=(sh&&sh.uniforms)||{};
      var cube=(u.uCustomIbl&&u.uCustomIbl.value)||null, loaded=0;
      try{ var im=cube&&cube.image;
        if(im&&im.length){ for(var i=0;i<im.length;i++){ var e=im[i];
          if(e&&(e.complete===undefined||e.complete)&&(e.naturalWidth===undefined||e.naturalWidth>0)) loaded++; } } }catch(e){}
      out.meshes.push({prim:(ud.chain.prim!==undefined?ud.chain.prim:null), kind:ud.chain.kind||null,
        family:(ud.neox&&ud.neox.family)||null,
        faces_loaded:loaded, faces_total:6,
        envMap_bound:!!m.envMap, radiance_bound:!!(u.uCustomIbl&&u.uCustomIbl.value),
        deferred_retries:out.deferred_retries, envMode:(ud.neox&&ud.neox.environment)||null,
        mat_visible:!!m.visible, tex_ready:(!!m.envMap||loaded>=6)});
    });
    return JSON.stringify(out,null,1);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-18，shader-auditor，task-29）：rig 只读诊断。
   报「实际生效值 + 来源（viewer.json 键 / 代码默认）」，只读、不改任何状态、不碰文件。 */
window.__rigProbe=function(){
  try{
    var T=state.THREE, cfg=state.config||{}, r=state.renderer, s=state.scene;
    var rig=((cfg.material_layers||{}).global_rig)||{};
    var hasK=function(k){ return cfg[k]!==undefined&&cfg[k]!==null; };
    var lights=[]; if(s) s.traverse(function(o){ if(o.isLight) lights.push({type:o.type,intensity:o.intensity,visible:o.visible}); });
    var mats=0, emMax=0, envMax=0;
    if(s) s.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0]; if(!m) return;
      mats++; emMax=Math.max(emMax,numCfg(m.emissiveIntensity,0)); envMax=Math.max(envMax,numCfg(m.envMapIntensity,0)); });
    return JSON.stringify({
      toneMapping:(r?r.toneMapping:null),
      toneMapping_name:(r&&T&&r.toneMapping===T.NoToneMapping)?'NoToneMapping':'ACESFilmic',
      /* ★ 修复（2026-09-20，ENVWIRE）：来源标注改为**实际读到的键路径**（原实现只认顶层
         `cfg.tone_mapping`，两个 `global_rig.tone_mapping` 全文件无人读 ⇒ 标注与读取口径双标）。 */
      toneMapping_source:(function(){ try{
          var q=toneMapRawOf(cfg); return q.src+'（raw="'+String(q.raw||'')+'"; 源侧无此概念，属展示 rig 近似）';
        }catch(e){ return 'ERR '+e; } })(),
      toneMapping_raw:(function(){ try{ return toneMapRawOf(cfg).raw; }catch(e){ return null; } })(),
      toneMapping_keys_present:(function(){ try{
          var sel=null; try{ if(typeof selectedState==='function') sel=selectedState(); }catch(e2){}
          return {config_top:(cfg.tone_mapping!==undefined&&cfg.tone_mapping!==null),
                  state_selected:!!(sel&&sel.material_layers&&sel.material_layers.global_rig&&
                                    sel.material_layers.global_rig.tone_mapping!==undefined&&
                                    sel.material_layers.global_rig.tone_mapping!==null),
                  config_material_layers:!!(cfg.material_layers&&cfg.material_layers.global_rig&&
                                    cfg.material_layers.global_rig.tone_mapping!==undefined&&
                                    cfg.material_layers.global_rig.tone_mapping!==null)}; }catch(e){ return null; } })(),
      exposure:(r?r.toneMappingExposure:null),
      exposure_source:hasK('exposure')?'viewer.json: exposure':'代码默认 1',
      environmentIntensity:(s?s.environmentIntensity:null),
      environmentIntensity_source:hasK('env_intensity')?'viewer.json: env_intensity':'代码默认 1.0',
      sceneEnvironmentAssigned:(s?!!s.environment:false),
      emissiveGain:(Number.isFinite(Number(rig.emissive_gain))?Number(rig.emissive_gain):0),
      emissiveGain_source:(rig.emissive_gain!==undefined)?'material_layers.global_rig.emissive_gain':'代码默认 0',
      /* ★ 新增（2026-09-20，EMISTOGGLE）：两档开关的**实际生效值**（默认全 false ⇒ 现状不变）。 */
      emissive_switches:(function(){ try{ var st=state.__emissiveState||{};
        return {A1_source_enabled:!!(st.source&&st.source.enabled),A1_prim:(st.source&&st.source.prim),
                A1_strength:(st.source&&st.source.strength),A1_tier:(st.source&&st.source.tier),
                A2_approx_enabled:!!(st.approx&&st.approx.enabled),A2_gain:(st.approx&&st.approx.gain),
                A2_tier:(st.approx&&st.approx.tier),gain_source:st.gain_source||null,
                applied:(st.summary||null)}; }catch(e){ return null; } })(),
      emissive_effective_on_meshes:(function(){ try{ var a=[]; if(s)
        s.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(Array.isArray(m)) m=m[0];
          var ud=(m&&m.userData)||{}; if(ud.__emissive&&ud.__emissive.mode!=='none')
            a.push({prim:ud.__emissive.prim,mode:ud.__emissive.mode,intensity:m.emissiveIntensity,map:!!m.emissiveMap}); });
        return a; }catch(e){ return null; } })(),
      emissiveIntensityMaxOnMeshes:+emMax.toFixed(4), envMapIntensityMaxOnMeshes:+envMax.toFixed(4),
      bloomStrength:(state.bloom&&state.bloom.strength!==undefined)?state.bloom.strength:0,
      bloom_source:(state.composer?'global_rig.bloom（composer 已建；清污块压 0）':'无 composer'),
      lights:lights, meshes:mats, rigMode:(state.__rigModeApplied||'approx（未切换，即当前默认行为）')
    },null,1);
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-18，task-29）：**可逆** rig A/B 切换（不动文件、不改默认值）。
   'source' = 源中立：NoToneMapping / exposure 1.0 / environmentIntensity 1.0 /
              emissiveGain 0 / bloom 0 / rig 三灯 0；
   'approx' = 恢复切换前的现状值（首次调用时备份：renderer/灯/逐材质 emissive&env/bloom 强度）。
   注意：`environmentIntensity` 只影响 scene.environment；本 viewer 的源 IBL 走逐材质 `uCustomIbl`，
   故该值对「已接源 cube」的材质无影响 —— 这一点由 __rigProbe 的逐材质读数印证，不作保真度推断。 */
window.__rigMode=function(mode){
  try{
    var T=state.THREE; if(!T) return 'ERR no THREE';
    var m=(mode===undefined||mode===null)?'source':String(mode).toLowerCase();
    if(m!=='source'&&m!=='approx') return 'ERR mode 必须是 source|approx';
    if(!state.__rigBak){
      var lights=[], mats=[];
      if(state.scene) state.scene.traverse(function(o){
        if(o.isLight) lights.push({o:o,i:numCfg(o.intensity,0),v:o.visible});
        if(o.isMesh){ var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
          if(mm) mats.push({m:mm, em:numCfg(mm.emissiveIntensity,0), envI:numCfg(mm.envMapIntensity,1),
                            emCol:(mm.emissive&&mm.emissive.clone)?mm.emissive.clone():null}); }
      });
      var passes=[]; if(state.composer&&state.composer.passes) state.composer.passes.forEach(function(p){ if(p&&typeof p.strength==='number') passes.push({p:p,s:p.strength}); });
      state.__rigBak={tone:state.renderer.toneMapping, exp:state.renderer.toneMappingExposure,
        envInt:(state.scene?state.scene.environmentIntensity:null), lights:lights, mats:mats, passes:passes,
        bloom:(state.bloom&&state.bloom.strength!==undefined)?state.bloom.strength:null};
    }
    var B=state.__rigBak;
    if(m==='approx'){
      if(state.renderer){ state.renderer.toneMapping=B.tone; state.renderer.toneMappingExposure=B.exp; }
      if(state.scene) state.scene.environmentIntensity=B.envInt;
      B.lights.forEach(function(x){ x.o.intensity=x.i; x.o.visible=x.v; });
      B.mats.forEach(function(x){ x.m.emissiveIntensity=x.em; x.m.envMapIntensity=x.envI;
        if(x.emCol&&x.m.emissive&&x.m.emissive.copy) x.m.emissive.copy(x.emCol); x.m.needsUpdate=true; });
      B.passes.forEach(function(x){ x.p.strength=x.s; });
      if(state.bloom&&B.bloom!==null) state.bloom.strength=B.bloom;
    }else{
      if(state.renderer){ state.renderer.toneMapping=T.NoToneMapping; state.renderer.toneMappingExposure=1.0; }
      if(state.scene) state.scene.environmentIntensity=1.0;
      B.lights.forEach(function(x){ x.o.intensity=0; });
      B.mats.forEach(function(x){ x.m.emissiveIntensity=0; if(x.m.emissive) x.m.emissive.setRGB(0,0,0); x.m.needsUpdate=true; });
      B.passes.forEach(function(x){ x.p.strength=0; });
      if(state.bloom) state.bloom.strength=0;
    }
    state.__rigModeApplied=m;
    try{ _forceRender(); _forceRender(); }catch(e){}
    return JSON.stringify({mode:m, tone:(state.renderer?state.renderer.toneMapping:null),
      exposure:(state.renderer?state.renderer.toneMappingExposure:null),
      envIntensity:(state.scene?state.scene.environmentIntensity:null),
      lights:B.lights.length, mats:B.mats.length, note:'只读+可逆：不改任何文件与默认值'});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-20，lead，只读）：平台/阴影定标用的**投影探针**。
   为什么需要：`applyCamera()` 在预设同时带 `target+distance` 时走"精确复现"分支，相机位置
   = **模型几何中心** + 预设方向×预设距离（不是预设 `position`）⇒ 纯解析算不准屏幕↔世界映射。
   本组探针只**读**相机矩阵，不触发重编译、不改任何默认值、不写任何文件。 */
window.__camBasisQa=function(){
  try{
    const T=state.THREE,c=state.camera; if(!T||!c) return null;
    c.updateMatrixWorld(true);
    return JSON.stringify({pos:c.position.toArray(),up:c.up.toArray(),fov:c.fov,aspect:c.aspect,
      near:c.near,far:c.far,matrixWorld:c.matrixWorld.toArray(),
      projInv:c.projectionMatrixInverse.toArray(),
      target:(state.controls?state.controls.target.toArray():null),
      buffer:[c.aspect,(state.renderer?state.renderer.domElement.width:-1),
              (state.renderer?state.renderer.domElement.height:-1)]});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* 世界点 → 画布归一化坐标（x,y∈[0,1]，y 向下）。pts = [[x,y,z],...] */
/* ★ 新增（2026-09-20，仅 QA）：平台/阴影定标需要"同一帧 开/关阴影"的局部差分。
   阴影只随那盏 rig key 灯存在 ⇒ 把 key 灯强度临时置 0 即"无直接光也无阴影"，
   且**不重建场景、不动相机**（否则两帧不能逐像素比）。传 null 还原原强度。
   只影响运行时，不改任何文件/默认值。 */
window.__platformKeyIntensity=function(v){
  try{
    if(!state.scene) return null;
    const L=[]; state.scene.traverse(function(o){ if(o.isDirectionalLight) L.push(o); });
    /* rig 顺序：hemi, key, fill ⇒ 第一盏 DirectionalLight 就是 key（见 configureScene）。 */
    const key=L[0];
    if(!key) return null;
    if(v===null||v===undefined){
      if(typeof state.__keyIntBackup==='number') key.intensity=state.__keyIntBackup;
      try{ _forceRender(); _forceRender(); }catch(e){}
      return {restored:key.intensity};
    }
    if(typeof state.__keyIntBackup!=='number') state.__keyIntBackup=key.intensity;
    key.intensity=Number(v);
    try{ _forceRender(); _forceRender(); }catch(e){}
    return {keyIntensity:key.intensity,backup:state.__keyIntBackup};
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-20，只读）：把平台的每个子网格角点逐个投影，报**屏幕包围盒**。
   用途：平台摆放定标（"前缘拐角要在画宽 x≈0.43、台面落在下 55%~80% 高度带"）必须看屏幕位置，
   而本相机几乎水平、世界 y 与屏幕 y 的关系不直观 ⇒ 直接量。 */
window.__platBoxQa=function(){
  try{
    const T=state.THREE;
    if(!T||!state.platformGroup) return null;
    const out={};
    state.platformGroup.updateMatrixWorld(true);
    state.platformGroup.children.forEach(function(o){
      if(!o.isMesh||!o.geometry) return;
      const g=o.geometry.parameters||{};
      const w=(g.width||0)/2,h=(g.height||0)/2;
      const local=[[-w,-h,0],[w,-h,0],[-w,h,0],[w,h,0]];
      const pts=[];
      for(let i=0;i<4;i++){
        const v=new T.Vector3(local[i][0],local[i][1],local[i][2]);
        o.localToWorld(v);
        const p=v.clone().project(state.camera);
        pts.push({world:[v.x,v.y,v.z],screen:[p.x*.5+.5,1-(p.y*.5+.5)],ndc:[p.x,p.y,p.z]});
      }
      const xs=pts.map(function(p){return p.screen[0];}),ys=pts.map(function(p){return p.screen[1];});
      out[o.name]={bbox:[Math.min.apply(null,xs),Math.min.apply(null,ys),
                         Math.max.apply(null,xs),Math.max.apply(null,ys)],pts:pts};
    });
    out.camera={pos:state.camera.position.toArray(),fov:state.camera.fov,aspect:state.camera.aspect};
    return out;
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-20，仅 QA）：取"同区域**无影**帧"。
   做法：把阴影相机的 near/far 压成"镜头前方 1 单位内没有任何投影体" ⇒ 阴影贴图处处为"被照亮"；
   `castShadow` / 灯光强度 / 材质 / 相机 / toneMapping **全不变** ⇒ 两帧差异**只**来自影子。
   （换 `renderer.shadowMap.enabled` 会触发材质重编译、整帧基线漂移，故不用。）
   传 null 还原。注意：本查看器里只有 key 一盏灯投影（平台块的 __platformSoftKey 仅在
   shadow_strength<1 时存在；该分支实测会把影子一起抹掉，见报告 unresolved，故交付配置用 1.0）。 */
window.__shadowToggleQa=function(off){
  try{
    if(!state.scene) return null;
    const L=[]; state.scene.traverse(function(o){ if(o.isDirectionalLight&&o.castShadow&&o.shadow) L.push(o); });
    if(!L.length) return null;
    const out=[];
    L.forEach(function(li){
      const sc=li.shadow.camera;
      if(off===null||off===undefined){
        if(typeof li.__qaFar==='number'){ sc.near=li.__qaNear; sc.far=li.__qaFar; }
        sc.updateProjectionMatrix();
        if(li.shadow.map) li.shadow.needsUpdate=true;
        out.push({light:li.name||'key',near:sc.near,far:sc.far});
      }else{
        if(typeof li.__qaFar!=='number'){ li.__qaNear=sc.near; li.__qaFar=sc.far; }
        sc.near=0.001; sc.far=1.0;
        sc.updateProjectionMatrix();
        if(li.shadow.map) li.shadow.needsUpdate=true;
        out.push({light:li.name||'key',near:sc.near,far:sc.far});
      }
    });
    try{ _forceRender(); _forceRender(); }catch(e){}
    return {off:!(off===null||off===undefined),lights:out};
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.__rootBoxQa=function(){
  try{
    const T=state.THREE; if(!T||!state.root) return null;
    state.root.updateMatrixWorld(true);
    const b=new T.Box3().setFromObject(state.root);
    const c=b.getCenter(new T.Vector3()),s=b.getSize(new T.Vector3());
    return {min:b.min.toArray(),max:b.max.toArray(),center:c.toArray(),size:s.toArray(),
            diag:Math.sqrt(s.x*s.x+s.y*s.y+s.z*s.z)};
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
window.__projPointsQa=function(pts){
  try{
    const T=state.THREE,c=state.camera; if(!T||!c) return null;
    c.updateMatrixWorld(true);
    const out=[];
    for(let i=0;i<pts.length;i++){
      const v=new T.Vector3(+pts[i][0],+pts[i][1],+pts[i][2]).project(c);
      out.push({w:[+pts[i][0],+pts[i][1],+pts[i][2]],ndc:[v.x,v.y,v.z],
                px:[v.x*.5+.5,1-(v.y*.5+.5)]});
    }
    return {fov:c.fov,aspect:c.aspect,pos:c.position.toArray(),target:(state.controls?state.controls.target.toArray():null),pts:out};
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* 屏幕归一化点 → 与水平面 y=planeY 的世界交点 */
window.__unprojAtQa=function(nx,ny,planeY){
  try{
    const T=state.THREE,c=state.camera; if(!T||!c) return null;
    c.updateMatrixWorld(true);
    const p=new T.Vector3(nx*2-1,1-ny*2,0.5).unproject(c);
    const o=c.position.clone(), d=p.sub(o).normalize();
    if(Math.abs(d.y)<1e-9) return {err:'parallel'};
    const t=(planeY-o.y)/d.y;
    return {screen:[nx,ny],planeY:planeY,t:t,hit:o.clone().addScaledVector(d,t).toArray()};
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ FIX-SFXFOLLOW 2026-09-20（只读探针）：`__state()`=debugState() **不含 scene/root**
   ⇒ "特效层有没有跟着模型转"此前只能靠像素差猜。本函数给出 root / sfx-layer 的世界矩阵、
   四元数、包围盒与特效层内各 model 组的实际世界位置，全部只读、不改任何状态。 */
window.__sceneDiag=function(){
  try{
    const T=state.THREE; if(!T||!state.scene) return {err:'no THREE/scene'};
    const sc=state.scene; sc.updateMatrixWorld(true);
    let layer=null; sc.traverse(function(o){ if(o.name==='sfx-layer') layer=o; });
    const wtr=function(o){ return [o.matrixWorld.elements[12],o.matrixWorld.elements[13],o.matrixWorld.elements[14]].map(function(x){return +x.toFixed(4);}); };
    const wpos=function(o){ const v=new T.Vector3(); o.getWorldPosition(v); return v.toArray().map(function(x){return +x.toFixed(4);}); };
    const out={sceneChildren:sc.children.map(function(c){return c.name||c.type;})};
    if(state.root){
      out.root={name:state.root.name||state.root.type, world:wtr(state.root),
                pos:state.root.position.toArray().map(function(x){return +x.toFixed(4);}),
                quat:state.root.quaternion.toArray().map(function(x){return +x.toFixed(5);}),
                box:(function(){ try{ const b=new T.Box3().setFromObject(state.root); if(b.isEmpty()) return null;
                  const c=b.getCenter(new T.Vector3()), s=b.getSize(new T.Vector3());
                  return {center:c.toArray().map(function(x){return +x.toFixed(4);}), size:s.toArray().map(function(x){return +x.toFixed(4);}), diag:+s.length().toFixed(4)}; }catch(e){ return null; } })()};
    }
    if(layer){
      const mg=layer.children.filter(function(c){ return c.name&&c.name.indexOf('sfx-model:')===0; });
      out.layer={name:layer.name, world:wtr(layer), pos:layer.position.toArray().map(function(x){return +x.toFixed(4);}),
                 matrixAutoUpdate:!!layer.matrixAutoUpdate, children:layer.children.length, modelGroups:mg.length,
                 sameWorldAsRoot:(state.root? (wtr(layer).join()===wtr(state.root).join()) : null),
                 matrixPos:[+layer.matrix.elements[12].toFixed(4),+layer.matrix.elements[13].toFixed(4),+layer.matrix.elements[14].toFixed(4)],
                 firstModel:(function(){ const g=mg[0]; if(!g) return null; const o=g.children[0];
                   let sz=null; try{ const b=new T.Box3().setFromObject(g); if(!b.isEmpty()){ const s=b.getSize(new T.Vector3());
                     sz=[+s.x.toFixed(3),+s.y.toFixed(3),+s.z.toFixed(3)]; } }catch(e){}
                   return {name:g.name, visible:!!g.visible, world:(o?wpos(o):null), worldSize:sz}; })()};
    }
    return out;
  }catch(e){ return {err:String((e&&e.message)||e)}; }
};
/* ★ 新增（2026-09-20，lead，只读）：rig / 阴影 / 直接光通道的**运行时读数**。
   根因是灯 `visible=false`（three 直接跳过），而既有探针都不报灯的可见性 ⇒ 只能靠像素差猜。
   本探针只读，不触发重编译、不改任何默认值。 */
window.__rigState=function(){
  try{
    const cfg=state.config||{};
    const L=[];
    if(state.scene) state.scene.traverse(function(o){ if(o.isLight) L.push({type:o.type,visible:!!o.visible,
      intensity:o.intensity,pos:o.position.toArray(),castShadow:!!o.castShadow}); });
    let cast=0,recv=0,meshes=0;
    if(state.root) state.root.traverse(function(o){ if(o.isMesh){meshes++; if(o.castShadow)cast++; if(o.receiveShadow)recv++;} });
    const f=state.shadowFloor;
    const pg=state.platformGroup;
    let platInfo=null;
    if(pg){
      const top=pg.getObjectByName('__platformTop'),fr=pg.getObjectByName('__platformFront');
      platInfo={children:pg.children.length,
        top:(top?{pos:top.position.toArray(),size:[top.geometry.parameters.width,top.geometry.parameters.height],
                  receive:!!top.receiveShadow,cast:!!top.castShadow,mat:top.material.type,
                  hasMap:!!(top.material&&top.material.map)}:null),
        front:(fr?{pos:fr.position.toArray(),size:[fr.geometry.parameters.width,fr.geometry.parameters.height],
                   receive:!!fr.receiveShadow,cast:!!fr.castShadow,
                   hasMap:!!(fr.material&&fr.material.map)}:null)};
      try{const b=new state.THREE.Box3().setFromObject(pg);
        platInfo.bbox={min:b.min.toArray(),max:b.max.toArray()};}catch(e){}
    }
    return JSON.stringify({rigOn:!!state.__rigOn,keyDir:state.__keyDir||null,
      platformOn:!!state.platformOn,
      config:{key_shadow:cfg.key_shadow,key_dir:cfg.key_dir,direct_light:cfg.direct_light,
              direct_light_intensity:cfg.direct_light_intensity,key_intensity:cfg.key_intensity,
              key_shadow_floor_y:cfg.key_shadow_floor_y,key_shadow_opacity:cfg.key_shadow_opacity,
              key_shadow_extent:cfg.key_shadow_extent,platform:cfg.platform||null},
      lights:L, shadowMapEnabled:!!(state.renderer&&state.renderer.shadowMap.enabled),
      rootMeshes:meshes, rootCastShadow:cast, rootReceiveShadow:recv,
      shadowFloor:(f?{y:f.position.y,opacity:f.material.opacity,visible:!!f.visible,size:f.geometry.parameters.width}:null),
      platform:platInfo,
      toneMapping:(state.renderer?state.renderer.toneMapping:null),
      exposure:(state.renderer?state.renderer.toneMappingExposure:null),
      envIntensity:(state.scene?state.scene.environmentIntensity:null)});
  }catch(e){ return 'ERR '+((e&&e.message)||e); }
};
/* ★ 新增（2026-09-18，只读）：回读编译后片元源码，用于核实注入**是否真的落到了材质上**。
   此前只有"画面改变了"这类间接证据，不足以判定 replace() 是否静默失效。 */
window.__fragMarkers=function(){
  var out=[];
  try{
    state.scene.traverse(function(o){
      if(!o.isMesh) return;
      var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData||!mm.userData.chain) return;
      var f=mm.userData.__frag||'';
      out.push({
        prim:mm.userData.chain.prim, kind:mm.userData.chain.kind, len:f.length,
        has_q_envW:/q_envW/.test(f),                    /* 源环境权重（本轮新增） */
        has_q_F0:/q_F0/.test(f),
        has_079956:/0\.079956/.test(f),                 /* F0 常数补丁 */
        has_getIBLRadiance_override:/q_Rr\s*=/.test(f),
        has_singleScattering:/radiance \* singleScattering/.test(f),   /* 旧权重是否还在 */
        has_uIblStrength:/uIblStrength/.test(f)
      });
    });
  }catch(e){ out.push({err:String((e&&e.message)||e)}); }
  return JSON.stringify(out);
};
/* ★ 新增（2026-09-20，lead，只读）：回读**编译后片元源码原文**（`__fragMarkers` 只给布尔，查不到"为什么直接光为 0"）。
   用途：定位「三盏 DirectionalLight/HemisphereLight ×10 而武器像素零变化」的机制（直接光项是否还在源码里）。
   纯读取，不触发重编译、不改任何材质/默认值。 */
window.__fragSrc=function(prim){
  try{
    var hit=null;
    state.scene.traverse(function(o){
      if(hit||!o.isMesh) return;
      var mm=o.material; if(Array.isArray(mm)) mm=mm[0];
      if(!mm||!mm.userData) return;
      var p=(mm.userData.chain&&mm.userData.chain.prim!==undefined)?mm.userData.chain.prim:null;
      if(prim===undefined||prim===null||p===prim) hit={prim:p,frag:(mm.userData.__frag||''),sh:!!mm.userData.__sh};
    });
    if(!hit) return null;
    return {prim:hit.prim,len:hit.frag.length,hasShaderObject:hit.sh,
      markers:{numDirLights:(hit.frag.match(/NUM_DIR_LIGHTS/g)||[]).length,
               directionalLights:(hit.frag.match(/directionalLights/g)||[]).length,
               reDirectPhysical:(hit.frag.match(/RE_Direct_Physical/g)||[]).length,
               directDiffuse:(hit.frag.match(/reflectedLight\.directDiffuse/g)||[]).length,
               directSpecular:(hit.frag.match(/reflectedLight\.directSpecular/g)||[]).length,
               dotNL:(hit.frag.match(/dotNL/g)||[]).length,
               getDirectionalLightInfo:(hit.frag.match(/getDirectionalLightInfo/g)||[]).length,
               lightsFragmentBegin:(hit.frag.match(/lights_fragment_begin/g)||[]).length,
               reflectedLight_total:(hit.frag.match(/reflectedLight/g)||[]).length},
      frag:hit.frag};
  }catch(e){ return {err:String((e&&e.message)||e)}; }
};
/* ★★ 已废弃（2026-09-18，审查助手指出的一致性问题）：
   旧 `__setWeaponPatch(on)` 写 `state.__weaponPatch`，但 v5 的**实际判定与 cacheKey 已全部改读 URL**
   `?weaponPatch=` —— 它已成为**死开关**，会再次制造假 A/B。
   现改为明确失效并报错，**绝不可被验收脚本使用**。
   本轮冷启动回归**只能**用两份全新页面 URL：`?weaponPatch=0` 与 `?weaponPatch=1`。 */
window.WikiWeaponViewer.__setWeaponPatch=function(){
  return JSON.stringify({
    error:'DEPRECATED_DEAD_SWITCH',
    deprecated:true,
    why:'v5 已改为冷启动 URL 开关；这个方法写的 state.__weaponPatch 已不被任何代码读取。',
    use_instead:'全新页面加 URL 参数：&weaponPatch=0 或 &weaponPatch=1（必须冷启动，不能运行时切换）',
    forbidden_in_acceptance:true
  });
};
window.WikiWeaponViewer.__applyParams=function(o){
  return (typeof window.__applyParamsJSON==='function')
    ? window.__applyParamsJSON(o)
    : {ok:false, err:'applyParamsJSON 尚未就绪（查看器未初始化？）'};
};
/* ★ 修复（2026-09-17，T3）：原写 `window.WikiWeaponViewer.__hidePanels=window.__hidePanels;`，
   但 `window.__hidePanels` 在本行之后才定义 → 恒 undefined（过早赋值，静默失败）。
   改为运行时转发，无论先后都能取到。 */
window.WikiWeaponViewer.__hidePanels=function(h){ 
  return (typeof window.__hidePanels==='function') ? window.__hidePanels(h)
    : JSON.stringify({err:'__hidePanels 尚未定义'});
};
window.__hidePanels=function(hide){
  /* 显式、命名清楚的"隐藏面板"接口（仅供无 UI 截图/度量使用，默认不隐藏）。 */
  try{
    var r=document.getElementById('weaponSkinViewer')||document, hit=[];
    ['.wv-params','.wv-tools'].forEach(function(sel){
      var el=(r&&r.querySelector)?r.querySelector(sel):null;
      if(el){ el.style.display=(hide===false?'':'none'); hit.push(sel); }
    });
    return JSON.stringify({hidden:hide!==false, touched:hit});
  }catch(e){ return 'ERR '+String((e&&e.message)||e); }
};

window.WikiWeaponViewer.snapshot=function(){
  const T=state.THREE, r=state.renderer;
  if(!T||!r||!state.scene||!state.camera) return null;
  const w=r.domElement.width||1178, h=r.domElement.height||640;
  let rt=null, buf=null;
  try{
    rt=new T.WebGLRenderTarget(w,h,{format:T.RGBAFormat,type:T.UnsignedByteType,depthBuffer:true});
    const oldT=r.getRenderTarget(); r.setRenderTarget(rt); r.clear();
    state.scene.updateMatrixWorld(true); state.camera.updateMatrixWorld(true);
    r.render(state.scene,state.camera);
    buf=new Uint8Array(w*h*4); r.readRenderTargetPixels(rt,0,0,w,h,buf);
    r.setRenderTarget(oldT);
  }catch(e){ try{ r.setRenderTarget(null); }catch(_){} return {error:String(e)}; }
  finally{ if(rt) rt.dispose(); }
  const cv=document.createElement('canvas'); cv.width=w; cv.height=h;
  const ctx=cv.getContext('2d'); const img=ctx.createImageData(w,h);
  let R=0,G=0,B=0,mag=0,gr=0; const n=w*h;
  for(let y=0;y<h;y++){ const sy=h-1-y;
    for(let x=0;x<w;x++){ const si=(sy*w+x)*4, di=(y*w+x)*4;
      const rr=buf[si],gg=buf[si+1],bb=buf[si+2];
      const enc=v=>{ const t=v/255.0; const u=t<=0.0031308?12.92*t:1.055*Math.pow(t,1/2.4)-0.055; return Math.max(0,Math.min(255,Math.round(u*255))); };
      const er=enc(rr), eg=enc(gg), eb=enc(bb);
      img.data[di]=er; img.data[di+1]=eg; img.data[di+2]=eb; img.data[di+3]=255;
      R+=er;G+=eg;B+=eb;
      if(rr>190&&bb>190&&gg<90) mag++;
      if(Math.abs(rr-gg)<8&&Math.abs(gg-bb)<8) gr++; } }
  ctx.putImageData(img,0,0);
  return {png:cv.toDataURL('image/png'), w:w, h:h,
          mean:[+(R/n).toFixed(1),+(G/n).toFixed(1),+(B/n).toFixed(1)],
          magenta_pct:+(100*mag/n).toFixed(2), gray_pct:+(100*gr/n).toFixed(1)};
};
window.WikiWeaponViewer.canvasShot=function(n){ for(let i=0;i<((n||2));i++) _forceRender(); return state.__lastShot||null; };
window.WikiWeaponViewer.canvasPixels=function(){ const _r=state.renderer; if(!_r) return null;
  const gl=_r.getContext(); const w=_r.domElement.width,h=_r.domElement.height;
  const buf=new Uint8Array(w*h*4); gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,buf);
  let r=0,g=0,b2=0,mag=0,gr=0,n=w*h;
  for(let i=0;i<n;i++){const R=buf[i*4],G=buf[i*4+1],B=buf[i*4+2]; r+=R;g+=G;b2+=B;
    if(R>200&&B>200&&G<80) mag++; if(Math.abs(R-G)<6&&Math.abs(G-B)<6) gr++; }
  return {w:w,h:h,mean:[+(r/n).toFixed(1),+(g/n).toFixed(1),+(b2/n).toFixed(1)],
          magenta_pct:+(100*mag/n).toFixed(2), gray_pct:+(100*gr/n).toFixed(1)}; };
window.WikiWeaponViewer.neoxState=function(){
  const out={mode:(state.neoxView||'default'),fidelity:(state.neoxFidelity||'reference_approximate'),
             canvas:(state.renderer&&state.renderer.domElement)?[state.renderer.domElement.width,state.renderer.domElement.height]:null,
             viewer_sha:window.__VIEWER_SHA||null, manifest_sha:(state.neoxReport&&state.neoxReport.manifest_sha)||null,
             materials:[]};
  if(state.root) state.root.traverse(o=>{ if(o.isMesh&&o.material){
    const u=o.material.uniforms?Object.fromEntries(Object.entries(o.material.uniforms).map(([k,v])=>[k,Array.isArray(v.value)?v.value:(v.value&&v.value.isTexture?('tex:'+v.value.uuid.slice(0,8)):v.value)])):null;
    const _im=o.material.map&&o.material.map.image;
    out.materials.push({map_src:(_im&&(_im.src||_im.currentSrc))||null,
                        map_loaded:(o.material.map&&o.material.map.image)?(o.material.map.image.width||0):0,
                        normal_map_src:(o.material.normalMap&&o.material.normalMap.image&&(o.material.normalMap.image.src||''))||null,
                        uuid:String(o.material.uuid).slice(0,12), type:o.material.type, name:o.material.name||null,
                        view:(o.material.userData.neox&&o.material.userData.neox.view)||null,
                        fidelity:(o.material.userData.neox&&o.material.userData.neox.material_fidelity)||null,
                        uniforms:u}); } });
  return out; };
/* L1 ladder diagnostic: additive only; no scene.environment/PMREM is used here. */
function __ladderMeshes(){
  const out=[]; const B0=state.__l0Base||{};
  if(!state.__ladderBaseMats)state.__ladderBaseMats={};
  if(!state.scene)return out;
  state.scene.traverse(function(o){
    if(!o.isMesh)return;
    const key=String(o.uuid), cm=o.material||{}, cud=cm.userData||{};
    const bm=state.__ladderBaseMats[key]||cm, bud=(bm&&bm.userData)||{};
    if(!(cud.neox||cud.chain||bud.neox||bud.chain||B0[key]||state.__ladderBaseMats[key]))return;
    if(!state.__ladderBaseMats[key])state.__ladderBaseMats[key]=cm;
    const base=state.__ladderBaseMats[key], ud=(base&&base.userData)||{}, ch=ud.chain||cud.chain||{};
    out.push({o:o,key:key,base:base,kind:ch.kind||((ud.neox&&ud.neox.shader==='weapon')?'weapon':null)||'unknown',prim:ch.prim});
  });
  return out;
}
function __ladderPrepare(){
  if(state.renderer)state.renderer.debug.checkShaderErrors=true;
  if(state.scene){state.scene.environment=null;state.scene.environmentIntensity=0;}
  return __ladderMeshes();
}
function __ladderCompileDiagnostics(){
  const r=state.renderer,gl=r&&r.getContext&&r.getContext();
  const out={checkShaderErrors:!!(r&&r.debug&&r.debug.checkShaderErrors),extension_shader_texture_lod:false,programs:[]};
  if(!gl)return out;
  try{out.extension_shader_texture_lod=!!gl.getExtension('EXT_shader_texture_lod');}catch(e){out.extension_shader_texture_lod=false;}
  const ps=(r.info&&r.info.programs)||[]; out.program_count=ps.length;
  out.programs=ps.map(function(p,i){
    const q={index:i,cacheKey:p&&p.cacheKey||null,vertex_compile:null,fragment_compile:null,program_link:null,vertex_info_log:'',fragment_info_log:'',program_info_log:''};
    try{const vs=p&&p.vertexShader;q.vertex_compile=vs?!!gl.getShaderParameter(vs,gl.COMPILE_STATUS):null;q.vertex_info_log=vs?(gl.getShaderInfoLog(vs)||''):'';}catch(e){q.vertex_error=String(e&&e.message||e);}
    try{const fs=p&&p.fragmentShader;q.fragment_compile=fs?!!gl.getShaderParameter(fs,gl.COMPILE_STATUS):null;q.fragment_info_log=fs?(gl.getShaderInfoLog(fs)||''):'';}catch(e){q.fragment_error=String(e&&e.message||e);}
    try{const pr=p&&p.program;q.program_link=pr?!!gl.getProgramParameter(pr,gl.LINK_STATUS):null;q.program_info_log=pr?(gl.getProgramInfoLog(pr)||''):'';}catch(e){q.program_error=String(e&&e.message||e);}
    return q;
  });
  return out;
}
function __ladderShaderEvidence(items,level){
  const hit=items.find(function(x){return x.o&&x.o.material&&x.o.material.userData&&x.o.material.userData.__ladderShader;});
  const m=hit&&hit.o.material,sh=m&&m.userData&&m.userData.__ladderShader,frag=sh&&String(sh.fragmentShader||'')||'';
  const lines=frag.split('\n').filter(function(s){return s.indexOf('uDiagColor')>=0||s.indexOf('uDiagTex')>=0||s.indexOf('uCustomIbl')>=0||s.indexOf('texture2D(')>=0||s.indexOf('textureCube(')>=0||s.indexOf('textureCubeLodEXT')>=0||s.indexOf('gl_FragColor')>=0;});
  return {level:level,vertex_snippet:sh&&String(sh.vertexShader||'').split('\n').slice(0,12).join('\n')||null,frag_snippet:lines.slice(-24).join('\n')||null,material_uuid:m?String(m.uuid):null};
}
function __ladderResult(items,level,mode,extra){
  const r={level:level,mode:mode,items:items.map(function(x){return {key:x.key,kind:x.kind,prim:x.prim,visible:!!x.o.visible,material_type:x.o.material&&x.o.material.type||null};}),programs:(state.renderer&&state.renderer.info&&state.renderer.info.programs)?state.renderer.info.programs.length:null,compile:__ladderCompileDiagnostics(),shader:__ladderShaderEvidence(items,level),scene_environment:state.scene&&state.scene.environment?'SET':'null'};
  if(extra)Object.assign(r,extra); return r;
}
window.WikiWeaponViewer.__ladderL1=function(spec){
  spec=spec||{}; const mode=String(spec.mode||'off'),T=state.THREE;
  try{
    if(!T||!state.scene||!state.renderer)return {level:'L1',mode:mode,error:'ERR no THREE/scene/renderer'};
    const items=__ladderPrepare(); if(!items.length)return {level:'L1',mode:mode,error:'ERR no ladder meshes'};
    if(!state.__ladderL1Mats)state.__ladderL1Mats={}; state.__ladderL1Mode=mode;
    const color=mode==='green'?new T.Color(0x00ff00):new T.Color(0xff0000);
    items.forEach(function(x){
      x.o.material=x.base;
      if(mode!=='red'&&mode!=='green')return;
      if(x.kind!=='weapon')return;
      let m=state.__ladderL1Mats[x.key];
      if(!m){
        m=new T.MeshBasicMaterial({color:0xffffff,toneMapped:false,fog:false,side:(x.base&&x.base.side!==undefined)?x.base.side:T.FrontSide});
        m.userData.__ladderLevel='L1';m.userData.__ladderKind=x.kind;m.userData.__ladderMode='off';m.userData.__ladderColor=color.clone();
        m.onBeforeCompile=function(sh){
          sh.uniforms.uDiagColor={value:m.userData.__ladderColor.clone()};
          /* ★ 修复（2026-09-17，viewer-auditor P0-1）：原缺此声明，导致 GLSL
             `'uDiagColor' : undeclared identifier` → program 不链接 → **该诊断材质完全不绘制**，
             而 __ladderResult 仍谎报 weapon_injected:N。与正确的 __l1 路径对齐。 */
          sh.fragmentShader='uniform vec3 uDiagColor;\n'+sh.fragmentShader;
          sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>','gl_FragColor = vec4(uDiagColor, 1.0);');
          m.userData.__ladderShader=sh;
        };
        m.customProgramCacheKey=function(){return 'L1_uDiagColor_'+x.kind+'_'+String(m.userData.__ladderMode||'off');};
        state.__ladderL1Mats[x.key]=m;
      }
      m.userData.__ladderMode=mode;m.userData.__ladderColor.copy(color);
      if(m.userData.__ladderShader&&m.userData.__ladderShader.uniforms.uDiagColor)m.userData.__ladderShader.uniforms.uDiagColor.value.copy(color);
      m.needsUpdate=true; /* same material red↔green requires a program invalidation */
      x.o.material=m;
    });
    _forceRender();_forceRender();
    const hit=items.filter(function(x){return mode!=='off'&&x.kind==='weapon';});
    return __ladderResult(items,'L1',mode,{uniform:'uDiagColor',color:(mode==='green'?'green':mode==='red'?'red':'baseline'),weapon_injected:hit.length,needsUpdate_set:(mode==='red'||mode==='green')});
  }catch(e){return {level:'L1',mode:mode,error:'ERR '+String(e&&e.message||e),compile:__ladderCompileDiagnostics()};}
};
window.WikiWeaponViewer.__ladderCompile=function(){return __ladderCompileDiagnostics();};

function _forceRender(){
  const _r=state.renderer;
  try{ if(_r&&_r.domElement&&_r.domElement.toDataURL){ state.__lastShot=_r.domElement.toDataURL('image/png'); } }catch(e){}
  const T=state.THREE; const r=state.renderer;
  if(!r||!state.scene||!state.camera) return false;
  try{ if(r.setSize) r.setSize(r.domElement.clientWidth||r.domElement.width, r.domElement.clientHeight||r.domElement.height, false); }catch(e){}
  state.scene.updateMatrixWorld(true); state.camera.updateMatrixWorld(true);
  if(state.controls&&state.controls.update) state.controls.update();
  if(state.composer){ try{ state.composer.render(); return true; }catch(e){} }
  r.render(state.scene,state.camera);
  try{ state.__lastShot=r.domElement.toDataURL('image/png'); }catch(e){}
  return true; }
function _reapplyNeox(){ if(!state.root) return false;
  const r=applyNeoxManifest(state.root);
  if(r&&r.then) return r.then(x=>{ _forceRender(); _forceRender(); return x; });
  _forceRender(); _forceRender(); return true; }
;
})();
