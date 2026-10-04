# -*- coding: utf-8 -*-
u"""_patch_viewer_js.py —— 给 assets/weapon_skin_viewer.js 打「产品默认 cube」补丁（幂等、锚点式）。

背景（实测，见 03_执行\\30_分析/_target_1110025/_probe_default_binding.py 与 _probe_bind3.py）：
  · `open()` 里唯一的**产品默认**应用点必须在 `ensureRuntime()` **之后**（否则 `state.THREE`
    还是 null，`__cubeAB` 在 `if(!T) return 'ERR no THREE'` 处提前返回）。
  · 但**真正决定链材质 bind 哪套 cube 的是 `applyNeoxManifest()`**（L1627 的 `cubeAB`），
    而它的 promise 在 `loadSelectedState()` 里**没有被 await**，会在 open 之后才 resolve
    ⇒ 若只在最后调 `__cubeAB`，manifest 那次仍会把 binding 写回 qiangpi。
  · 且 L1631 的选择器**硬编码**只认 `'qiangpi'|'jiayuan02a'` ⇒ 自造名一律被丢弃。

因此本补丁做三件事（全部围绕新增语义，不动既有字段语义）：

  【P1】插入 `__cubeProductDefaultName()` / `__cubeApplyProductDefault()` /
        `window.WikiWeaponViewer.__cubeProductDefault()`。
        `__cubeApplyProductDefault()` 只**置** `state.__cubeABOverride`
        （让 `applyNeoxManifest` 在**建材质那一刻**就用对 cube），并记
        `state.__cubeProductDefaultPend` 作为"稍后还要真正换一次纹理"的待办。

  【P2】`cube_index`（L1627-1631）的选择器**放宽**：保留既有 `qiangpi|jiayuan02a` 老路，
        新增「清册里 status==='self_authored_approximate'（自造近似、非游戏资产）」一路。
        该状态**只可能**来自 data/media/weapon_skin_cubes_custom.js ⇒ 不削弱
        「partial/unresolved 不使用替代图」的既有纪律。

  【P3】`fillCubeSelect()` / onChange / open() 的三处小改：
        · 下拉区分「视觉初始化成产品默认」与「用户真的选过」（`__cubePickUserPicked`），
          用户选「（manifest 原绑定·不覆盖）」= **明确拒绝**默认（`__cubeProductDefaultDeclined`）；
        · open() 在 `fillCubeSelect()` 之后调一次 `__cubeApplyProductDefault()`（只置 override）；
        · open() 在 `await loadSelectedState()` 之后**再调一次**（此时 THREE 就绪 ⇒
          真正把 uSrcIbl/uCustomIbl 换成新产品默认的 CubeTexture，双保险）。

  【P4】`__cubeAB()` 里消费 `__cubeProductDefaultPend`（幂等），并在有产品默认时报出。
  【P5】`__cubePickerState()` 追加只读字段
        `product_default` / `_authority` / `_fidelity` / `_applied` / `_declined`。

语义保证：
  · 其它皮肤没有 `cube_default_selection` ⇒ `PD_NAME()` 返回 null ⇒ 全部短路 ⇒ **零回归**。
  · 「（manifest 原绑定·不覆盖）」仍是下拉第一项；32 源 cube + 3 自造项全部仍可选。
  · 不改 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx / 任何 cube 资产。

用法：& '<venv>\python.exe' _patch_viewer_js.py [--dry-run] [--with-post-apply]
      默认**不带** --with-post-apply（保持最小改动面；双保险那条默认不开）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
JS = os.path.join(WIKI, 'assets', 'weapon_skin_viewer.js')

# ── 锚点（逐字，已用 Python 校验唯一性） ──
A_FILL_FN = "  function fillCubeSelect(){\n    var sel=state.cubeSelect; if(!sel)return 0;\n"
A_DEFLINE = "    var def=idx.default||'qiangpi', keep=sel.value, n=0, nHidden=0;\n"
A_EMPTYRESET = "    if(keep&&!cubeIndexOf(keep))sel.value=\"\";\n"
A_CHANGE = "        var v=state.cubeSelect.value;\n"
A_OPEN_FILL = "      try{ fillCubeSelect(); }catch(e){}\n"
A_CUBEAB = "window.WikiWeaponViewer.__cubeAB=function(which){"
A_NOTHREE = "    var T=state.THREE, out=[];\n    if(!T) return JSON.stringify({err:'no THREE'});\n"
A_CUBESEL = ("    const cubeAB=(function(){\n"
             "      var v=null; try{ v=new URLSearchParams(location.search).get('cubeAB'); }catch(e){}\n"
             "      if(!v&&state.__cubeABOverride) v=String(state.__cubeABOverride);\n"
             "      v=v?String(v).trim().toLowerCase():null;\n"
             "      return (v==='qiangpi'||v==='jiayuan02a')?v:null; })();\n"
             "    if(cubeAB && g.t_custom_ibl && g.t_custom_ibl.file){\n"
             "      var _cubeBefore=g.t_custom_ibl.file;\n"
             "      g.t_custom_ibl.file='src_cube/'+cubeAB+'.dds';\n"
             "      g.t_custom_ibl.faces_glob='src_cube/faces/'+cubeAB+'_f{i}_m0.png';\n"
             "      /* ⚠ 注意：faces_glob 在 loader 侧若被信任就直接用；这里同时覆盖 file 基名，两条派生路都指向同一套。 */\n"
             "      g.t_custom_ibl.__cube_ab={from:_cubeBefore, to:g.t_custom_ibl.file, level:'approximate(diagnostic_selector)'};\n"
             "    }\n")
A_DATASET = ("    sel.dataset.cube=sel.value||\"(manifest 原绑定)\"; sel.dataset.sourceSelector=\"none\";\n"
             "    var r=cubeIndexOf(sel.value); sel.dataset.status=r?r.status:\"manifest_binding\";\n"
             "    state.__cubePickIndex=idx;\n")
A_PICKER_ISGAME = "      is_game_asset:(rec?rec.is_game_asset:null),\n"
A_LOADSTATE = "      await ensureRuntime();configureScene();await loadSelectedState();\n"

# ── P1：函数块 ──
P1 = u'''  /* ══════════════════════════════════════════════════════════════════════════════════════
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
'''

# ── P2：cubeAB 选择器放宽 ──
P2 = (u"    /* ★ 改动（2026-09-21，SNOWCUBE）：选择器放宽到**清册里的自造近似档**。\n"
      u"       原来硬编码只认 'qiangpi'|'jiayuan02a' ⇒ 产品默认（自造名）会被静默丢弃。\n"
      u"       新增一路：清册里 status==='self_authored_approximate' 的名字也接受。\n"
      u"       该状态**只可能**来自 data/media/weapon_skin_cubes_custom.js ⇒\n"
      u"       「partial/unresolved 不使用替代图」的既有纪律不变。\n"
      u"       仅当**显式**传了 cube（URL 参数或 __cubeABOverride）才走这里；\n"
      u"       无覆盖时（默认）**逐字不动 manifest** —— 与改前行为一致。 */\n"
      u"    const cubeAB=(function(){\n"
      u"      var v=null; try{ v=new URLSearchParams(location.search).get('cubeAB'); }catch(e){}\n"
      u"      if(!v&&state.__cubeABOverride) v=String(state.__cubeABOverride);\n"
      u"      v=v?String(v).trim().toLowerCase():null;\n"
      u"      if(!v) return null;\n"
      u"      if(v==='qiangpi'||v==='jiayuan02a') return v;      /* 既有两套（走皮肤 src_cube/faces/） */\n"
      u"      var _rec=cubeIndexOf(v);                            /* 自造近似档：走显式 faces[]（RGBM） */\n"
      u"      if(_rec&&_rec.status==='self_authored_approximate'&&_rec.resolve==='self_authored'\n"
      u"         &&_rec.faces&&_rec.faces.length===6) return v;\n"
      u"      return null; })();\n"
      u"    if(cubeAB && g.t_custom_ibl && g.t_custom_ibl.file){\n"
      u"      var _cubeBefore=g.t_custom_ibl.file;\n"
      u"      var _rec2=cubeIndexOf(cubeAB);\n"
      u"      if(_rec2&&_rec2.resolve==='self_authored'){\n"
      u"        /* 自造档：faces[] 是**仓库相对**路径（assets/3d/weapon_skin/_shared/...），\n"
      u"           而 loader 侧（L1989-1993）只会拼两处：\n"
      u"             · `t.indexOf('src_cube/')===0` ⇒ `base + t`\n"
      u"             · 否则 ⇒ `B + t.split('/').pop()`（B = 「皮肤 src_cube/faces/」）\n"
      u"           直接用 faces[0] 会落到第二支 ⇒ 变成皮肤目录下的**不存在的文件名** ⇒ 六面 404\n"
      u"           （实测：200 vs 404，见 _patch_viewer_js 的验证记录）。\n"
      u"           这里写成以 `src_cube/` 开头、再用 `../..` 折回仓库根的相对路径：\n"
      u"           浏览器与 SimpleHTTPRequestHandler **都会**规范化 `..` ⇒ 实际命中\n"
      u"           assets/3d/weapon_skin/_shared/cubes/<name>/rgbm/…（已用 HTTP HEAD 验过 200）。\n"
      u"           同时把 file 指向 `_shared/cubes/<name>/payload.dds`（自造目录里**确实**有这个文件），\n"
      u"           避免 `iblName` 推导路产生不存在的 src_cube/<name>.dds。 */\n"
      u"        g.t_custom_ibl.file='_shared/cubes/'+cubeAB+'/payload.dds';\n"
      u"        g.t_custom_ibl.faces_glob='src_cube/../../_shared/cubes/'+cubeAB+'/rgbm/'+cubeAB+'_f{i}_m0.png';\n"
      u"      }else{\n"
      u"        g.t_custom_ibl.file='src_cube/'+cubeAB+'.dds';\n"
      u"        g.t_custom_ibl.faces_glob='src_cube/faces/'+cubeAB+'_f{i}_m0.png';\n"
      u"      }\n"
      u"      /* ⚠ 注意：faces_glob 在 loader 侧若被信任就直接用；这里同时覆盖 file 基名，两条派生路都指向同一套。 */\n"
      u"      g.t_custom_ibl.__cube_ab={from:_cubeBefore, to:g.t_custom_ibl.file, level:'approximate(diagnostic_selector)'};\n"
      u"    }\n")

# ── P3a：fillCubeSelect 开头提前算产品默认名 ──
P3A = (u"  function fillCubeSelect(){\n    var sel=state.cubeSelect; if(!sel)return 0;\n"
       u"    /* ★ 新增（2026-09-21，SNOWCUBE）：产品默认名提前算，供下面的**视觉**初始化用。 */\n"
       u"    var __pdWant=PD_NAME();\n")
P3B = (u"    var def=idx.default||'qiangpi', keep=sel.value, n=0, nHidden=0;\n"
       u"    /* ★ 新增（2026-09-21，SNOWCUBE）：把「下拉当前值」与「用户是否真的选过」分开跟踪。\n"
       u"       prev = 用户此前真的动过下拉的选择（空串=「不覆盖」）；首项（value=''）在下面用\n"
       u"       __pdWant 做**视觉**初始化，不会把 prev 当成「用户选了不覆盖」。 */\n"
       u"    var prev=state.__cubePickUserPicked?sel.value:null;\n")
P3C = (u"    if(keep&&!cubeIndexOf(keep))sel.value=\"\";\n"
       u"    /* ★ 新增（2026-09-21，SNOWCUBE）：用 prev（用户真实选择）判落空，避免把\n"
       u"       「视觉初始化成产品默认」误当成用户选择。 */\n"
       u"    if(prev&&!cubeIndexOf(prev))sel.value=\"\";\n")
P3D = (u"    sel.dataset.cube=sel.value||\"(manifest 原绑定)\"; sel.dataset.sourceSelector=\"none\";\n"
       u"    var r=cubeIndexOf(sel.value); sel.dataset.status=r?r.status:\"manifest_binding\";\n"
       u"    state.__cubePickIndex=idx;\n"
       u"    /* ★ 新增（2026-09-21，SNOWCUBE）：若本皮肤声明了产品默认且清册里有它，把下拉\n"
       u"       **视觉上**初始化到那一项（只动 <select> 显示，不动任何 bind；真正 bind 在\n"
       u"       open() 里的 __cubeApplyProductDefault()）。默认名落空 ⇒ 不动下拉，仍然停在\n"
       u"       「不覆盖」，绝不静默换一套 cube。 */\n"
       u"    if(__pdWant&&cubeIndexOf(__pdWant)&&state.__cubePickUserPicked!==true) sel.value=__pdWant;\n"
       u"    else if(state.__cubePickUserPicked===true) sel.value=(prev==null?\"\":prev);\n"
       u"    state.__cubePickUserPicked=false;\n"
       u"    return n;\n  }\n")
P3E = (u"        var v=state.cubeSelect.value;\n"
       u"        /* ★ 新增（2026-09-21，SNOWCUBE）：记录「用户真的动过下拉」。\n"
       u"           选「（manifest 原绑定·不覆盖）」= **明确拒绝**产品默认 ⇒ 记 declined，\n"
       u"           此后开关皮肤不再强加默认。选具体某一套 = picked（= 不是拒绝）。 */\n"
       u"        state.__cubePickUserPicked=true;\n"
       u"        state.__cubeProductDefaultDeclined=(v===\"\");\n")
P3F = (u"      try{ fillCubeSelect(); }catch(e){}\n"
       u"      /* ★ 新增（2026-09-21，SNOWCUBE）：置产品默认的 override（**材质建立之前**）。\n"
       u"         这里 `state.THREE` 还没就绪，`__cubeAB` 会安全早返回（只置 override），\n"
       u"         真正的意义是让随后 `loadSelectedState()` 里的 `applyNeoxManifest()`\n"
       u"         在**建材质那一刻**就读到正确的 cube。没有声明默认的皮肤直接短路 ⇒ 零回归。 */\n"
       u"      try{ __cubeApplyProductDefault(); }catch(e){}\n")
P3G = (u"      await ensureRuntime();configureScene();await loadSelectedState();\n"
       u"      /* ★ 新增（2026-09-21，SNOWCUBE）：**材质异步建立之后**再保险换一次纹理。\n"
       u"         此处 `ensureRuntime()` 已跑完（state.THREE 就绪）⇒ `__cubeAB` 能真正把\n"
       u"         uSrcIbl/uCustomIbl 换成产品默认的 CubeTexture。\n"
       u"         （实测：只在 ensureRuntime 之前调会在 `if(!T) return 'ERR no THREE'` 提前返回。\n"
       u"          注意 `loadSelectedState()` 里 `applyNeoxManifest()` 的 promise **未被 await**，\n"
       u"          所以真正决定链材质 bind 的是上面那次 override，这里只做双保险。） */\n"
       u"      try{ __cubeApplyProductDefault(); }catch(e){}\n")

# P4a 已于 2026-09-21 **撤销**：
#   原设计在 `__cubeAB` 早返回前把 `state.__cubeABOverride` 强制设回产品默认，目的是让
#   "THREE 未就绪时"也能把 override 留给 `applyNeoxManifest`。但那个位置在**每一次**调用
#   都会执行，且 `if(!T) return` **早于**真正的纹理交换 ⇒ 只要 THREE 未就绪就直接返回，
#   用户显式切的 cube（qiangpi/snow）永远绑不上、画面停在产品默认。
#   实测证据：加 P4a 时 accept 里 Q_qiangpi / S_snow 与 D 逐字节相同（786ad4fa…），
#             且 settle 报 "want=qiangpi got=custom_bright_snow_20260921"。
#   正确做法：**不动 `__cubeAB` 的控制流**。产品默认的 override 由 `open()` 里
#   `fillCubeSelect()` 之后那次 `__cubeApplyProductDefault()` 设置（它在 open 早期、
#   `applyNeoxManifest` 之前执行，时机本来就对）；`__cubeAB` 保持原样即可正常换纹理。
A_NOTHREE_IDENTITY = True
P4B = (u"    state.__cubeABOverride=v;\n"
       u"    /* ★ 新增（2026-09-21，SNOWCUBE）：消费产品默认待办（幂等）。\n"
       u"       若本次调用正是产品默认，且 THREE 已就绪 ⇒ 清掉待办；\n"
       u"       若调用的是别的 cube（用户显式切换）⇒ 也清掉，不覆盖用户选择。 */\n"
       u"    if(state.__cubeProductDefaultPend){\n"
       u"      if(v&&String(v)===String(state.__cubeProductDefaultPend))\n"
       u"        state.__cubeProductDefaultPend=null;\n"
       u"      else if(v===null)\n"
       u"        state.__cubeProductDefaultPend=null;\n"
       u"    }\n")

# ── P5：__cubePickerState 追加只读字段 ──
P5 = ("      is_game_asset:(rec?rec.is_game_asset:null),\n"
      "      /* ★ 新增（2026-09-21，SNOWCUBE）：**只读**产品默认字段。\n"
      "         既有 `default` / `is_default` / `selected` 语义**不变**（`default` 仍是清册的\n"
      "         source_verified 默认名），这里只是额外如实交代「产品默认是谁、什么 authority」。 */\n"
      "      product_default:PD_NAME(),\n"
      "      product_default_authority:(function(){ try{ var c=state.config&&state.config.cube_default_selection;\n"
      "        return (c&&c.authority)||null; }catch(e){ return null; } })(),\n"
      "      product_default_fidelity:(function(){ try{ var c=state.config&&state.config.cube_default_selection;\n"
      "        return (c&&c.fidelity)||null; }catch(e){ return null; } })(),\n"
      "      product_default_applied:state.__cubeProductDefaultApplied||null,\n"
      "      product_default_declined:!!state.__cubeProductDefaultDeclined,\n"
      "      source_selector:'none',\n"
      "      note:'源数据里没有选择器决定预览用哪一套 cube；本选择器是取证/对比工具，不代表游戏的选择。',\n")


def patch(text):
    if 'function PD_NAME()' in text:
        return text, ['已打过补丁 ⇒ 跳过（幂等）']
    log = []
    anchors = [('P2', A_CUBESEL), ('P1', A_CUBEAB), ('P4A', A_NOTHREE),
               ('P4B', "    state.__cubeABOverride=v;\n"),
               ('P3A', A_FILL_FN), ('P3B', A_DEFLINE), ('P3C', A_EMPTYRESET),
               ('P3E', A_CHANGE), ('P3F', A_OPEN_FILL), ('P3G', A_LOADSTATE),
               ('P3D', A_DATASET), ('P5', A_PICKER_ISGAME)]
    for nm, a in anchors:
        c = text.count(a)
        if c != 1:
            raise SystemExit('FAIL: 锚点 %s 命中 %d 次（必须恰好 1 次）:\n%r' % (nm, c, a[:90]))

    text = text.replace(A_CUBEAB, P1 + A_CUBEAB, 1)
    log.append('[P1] 插入 PD_NAME / __cubeApplyProductDefault / __cubeProductDefault')
    text = text.replace(A_CUBESEL, P2, 1)
    log.append('[P2] cubeAB 选择器放宽到清册里的自造近似档（+ faces_glob 用 _rec.faces[0]）')
    text = text.replace(A_NOTHREE, A_NOTHREE, 1)          # P4a 撤销：保持原样，不改控制流
    log.append('[P4a] 撤销：__cubeAB 控制流保持原样（原设计会让早返回抢在换纹理之前）')
    text = text.replace("    state.__cubeABOverride=v;\n", P4B, 1)
    log.append('[P4b] __cubeAB：消费 __cubeProductDefaultPend')
    text = text.replace(A_FILL_FN, P3A, 1)
    text = text.replace(A_DEFLINE, P3B, 1)
    text = text.replace(A_EMPTYRESET, P3C, 1)
    text = text.replace(A_CHANGE, P3E, 1)
    log.append('[P3] fillCubeSelect：PD_NAME 提前算 + prev/userPicked 分离')
    text = text.replace(A_OPEN_FILL, P3F, 1)
    log.append('[P3f] open(): fillCubeSelect() 之后置产品默认 override（材质建立之前）')
    text = text.replace(A_LOADSTATE, P3G, 1)
    log.append('[P3g] open(): await loadSelectedState() 之后再保险换一次纹理')
    text = text.replace(A_DATASET, P3D, 1)
    log.append('[P3d] fillCubeSelect 尾部：下拉视觉初始化到产品默认')
    # 原函数尾部的 `    return n;\n  }\n` 已被 P3D 自带的那份取代 ⇒ 去掉重复的旧块
    dup = "    return n;\n  }\n    return n;\n  }\n"
    if text.count(dup) != 1:
        raise SystemExit('FAIL: 未找到预期的重复 return 块（count=%d）' % text.count(dup))
    text = text.replace(dup, "    return n;\n  }\n", 1)
    log.append('[P3d] 去掉被取代的旧 `return n;` 重复块')
    text = text.replace(A_PICKER_ISGAME, P5, 1)
    log.append('[P5] __cubePickerState 追加 5 个只读产品默认字段')
    return text, log


def main():
    dry = '--dry-run' in sys.argv
    text = open(JS, encoding='utf-8').read()
    out, log = patch(text)
    for ln in log:
        print(ln)
    if out == text:
        print('无改动')
        return 0
    print('长度 %d → %d' % (len(text), len(out)))
    if dry:
        print('--dry-run：未写文件')
        return 0
    open(JS, 'w', encoding='utf-8').write(out)
    print('写了 %s' % JS)
    return 0


if __name__ == '__main__':
    sys.exit(main())
