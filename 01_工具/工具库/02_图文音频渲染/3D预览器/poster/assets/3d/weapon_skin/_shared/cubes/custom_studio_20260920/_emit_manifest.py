# -*- coding: utf-8 -*-
u"""_emit_manifest.py —— 由 provenance.json 生成 `04_站点\\web/data/media/weapon_skin_cubes_custom.js`。

为什么用生成器：sha256 全部从 provenance.json 读，**杜绝手抄错**。
生成物与另一路代理的 `weapon_skin_cubes.js`（环境立方体总清单）**分离**，便于并行合并且互不覆盖。

★ 已按**已落盘的**总清单 schema 对齐（`weapon_skin_cubes.js` → `window.WIKI_WEAPON_SKIN_CUBES`，
  schema `weapon_skin_cubes/v1`，条目用显式 `faces[]` URL 数组）。因此本条目可**直接 append**：
      window.WikiWeaponSkinCubesCustom.mergeInto(window.WIKI_WEAPON_SKIN_CUBES);

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\\python.exe' '<本文件>'
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = r'E:\la拆包项目\04_站点\\web'
OUT_JS = os.path.join(WIKI, r'data\media\weapon_skin_cubes_custom.js')
PROV = os.path.join(HERE, 'provenance.json')
FACE_DIR_REL = 'assets/3d/weapon_skin/_shared/cubes/custom_studio_20260920/'

HEADER = u"""/* weapon_skin_cubes_custom.js —— **自造近似**环境立方体清单（custom / self-authored）
 *
 * ⚠️⚠️ 本文件里的 cube **不是游戏资产**。它由游戏自己的背景板重采样而来，属于**自造近似**
 *      （status = self_authored_approximate），authority = user_authorized_manual_20260920。
 *      **不得**当作「游戏实际使用该环境」的证据，**不得**计入「源数据驱动」目标。
 *
 * 为什么单独一个文件：`weapon_skin_cubes.js`（真源 cube 总清单，schema weapon_skin_cubes/v1）
 * 由另一路代理生成。为了**不互相覆盖**，自造条目写在本文件，并导出 mergeInto() 供上级并入：
 *
 *     window.WikiWeaponSkinCubesCustom.mergeInto(window.WIKI_WEAPON_SKIN_CUBES);
 *
 * ⚠ 给选择器实现者的两条注意：
 *   ① 本条目 status='self_authored_approximate'，**故意落在**总清单既有枚举
 *      (source_verified/partial/unresolved) **之外** —— 这样它绝不会被误统计为「已定位源 cube」。
 *      若要让它出现在下拉里，请**显式**接受该状态，并把它排到单独分组、标「自造近似（非游戏资产）」。
 *   ② faces[] 指向 **rgbm/** 子目录：查看器源 IBL 分支按 asm 542-544 `pow(rgb*a*16,2)` 解码、
 *      且 cube 纹理 colorSpace=NoColorSpace，源六面 alpha≈0.015 即 RGBM 乘子。
 *      直接喂**无 alpha** 的 sRGB 面会 a=1.0 ⇒ 亮约 4400×（实测 p50 0.9679 / >0.85 76.58%，
 *      纯属编码假象）。faces_srgb[] 仅供人眼看图，**不要**喂给查看器。
 *
 * 本文件**无副作用**、不自动改 DOM、不改任何查看器状态；只注册两个全局对象（若主清单已在则顺带合并）。
 * 由 _shared/cubes/custom_studio_20260920/_emit_manifest.py 生成 —— 请勿手改，改生成器。
 */
(function () {
  'use strict';

  var CUSTOM_CUBES = __CUSTOM_CUBES_JSON__;

  var API = {
    version: '20260920',
    kind: 'custom_self_authored',
    schema: 'weapon_skin_cubes_custom/v1',
    merges_into: 'WIKI_WEAPON_SKIN_CUBES (schema weapon_skin_cubes/v1)',
    /** ★ 全局诚实标注：本清单内所有 cube 均为自造近似，非游戏资产 */
    disclaimer: '**自造近似立方体，非游戏资产**。仅用于观察环境反射对观感的影响；不得作为「游戏实际使用该环境」的证据，也不得计入「源数据驱动」目标。',
    cubes: CUSTOM_CUBES,
    get: function (name) {
      var n = String(name == null ? '' : name).trim();
      for (var i = 0; i < CUSTOM_CUBES.length; i++) { if (CUSTOM_CUBES[i].name === n) return CUSTOM_CUBES[i]; }
      return null;
    },
    names: function () { return CUSTOM_CUBES.map(function (c) { return c.name; }); },
    isCustom: function (name) { return !!this.get(name); },
    /** 喂给查看器的六面 URL（RGBM 编码档），顺序 +X,-X,+Y,-Y,+Z,-Z */
    viewerFaces: function (name) { var c = this.get(name); return c ? c.faces.slice() : null; },
    /** 人眼看的六面 URL（sRGB 档），**不要**喂查看器 */
    displayFaces: function (name) { var c = this.get(name); return c ? c.faces_srgb.slice() : null; },
    /** 并入主清单：只追加，不覆盖同名条目（避免踩到真源 cube） */
    mergeInto: function (main) {
      if (!main || typeof main !== 'object') return { merged: 0, reason: 'no main manifest' };
      if (!Array.isArray(main.cubes)) main.cubes = [];
      var have = {};
      for (var i = 0; i < main.cubes.length; i++) { if (main.cubes[i] && main.cubes[i].name) have[main.cubes[i].name] = 1; }
      var n = 0;
      for (var j = 0; j < CUSTOM_CUBES.length; j++) {
        var c = CUSTOM_CUBES[j];
        if (have[c.name]) continue;
        var copy = JSON.parse(JSON.stringify(c));
        copy.origin = 'weapon_skin_cubes_custom.js';
        copy.is_game_asset = false;
        main.cubes.push(copy);
        n++;
      }
      if (!main.custom_merged) {
        main.custom_merged = { count: 0, source: 'weapon_skin_cubes_custom.js', disclaimer: API.disclaimer };
      }
      main.custom_merged.count += n;
      return { merged: n, total: main.cubes.length };
    }
  };

  if (typeof window !== 'undefined') {
    window.WikiWeaponSkinCubesCustom = API;
    /* 若主清单已先加载，顺手合并（幂等：同名不重复追加） */
    try { if (window.WIKI_WEAPON_SKIN_CUBES) API.mergeInto(window.WIKI_WEAPON_SKIN_CUBES); } catch (e) {}
  }
})();
"""


def main():
    prov = json.load(open(PROV, encoding='utf-8'))
    src = prov['derived_from'][0]
    derived = ['%s sha256:%s' % (src['path'], src['sha256'])]

    def urls(rel_dir, faces):
        return [FACE_DIR_REL + rel_dir + f['file'] for f in faces]

    rgbm = prov.get('rgbm_faces') or []
    entry = {
        'name': prov['name'],
        # ---- 诚实标注（任务书要求字段）----
        'status': prov['status'],
        'authority': prov['authority'],
        'fidelity': prov['fidelity'],
        'is_game_asset': False,
        'derived_from': derived,
        'method': prov['method'],
        'note': prov['note'],
        # ---- 对齐 weapon_skin_cubes/v1 的机械字段 ----
        'logical': 'self_authored://custom_studio_20260920',
        'container': None,
        'row': None,
        'sha16': None,
        'dims': '%dx%d' % (prov['face_size'], prov['face_size']),
        'format': 'PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐',
        'n_faces': 6,
        'resolve': 'self_authored',
        'in_skin': False,
        'identity_basis': 'self_authored_approximate — 无容器/无哈希命中，**不是**源 cube',
        # ---- 选择器实现者需要的显式提示 ----
        'selectable': True,
        'group': 'self_authored（自造近似，非游戏资产）',
        'requires_status_whitelist_extend': True,
        # ---- 六面 ----
        'cubemap_order': prov['cubemap_order'],
        'faces': urls('', rgbm) if rgbm else urls('', prov['faces']),
        'faces_srgb': urls('', prov['faces']),
        'faces_encoding': 'rgbm' if rgbm else 'srgb',
        'face_sha256_rgbm': [f['sha256'] for f in rgbm],
        'face_sha256_srgb': [f['sha256'] for f in prov['faces']],
        'rgbm_encoding': prov.get('rgbm_encoding'),
        'summary': prov['summary'],
        'no_photometric_gain': prov['no_photometric_gain'],
        'limitations': prov['limitations'],
    }

    body = json.dumps([entry], ensure_ascii=False, indent=2)
    with open(OUT_JS, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(HEADER.replace('__CUSTOM_CUBES_JSON__', body))
    print('wrote:', OUT_JS)
    print('  bytes:', os.path.getsize(OUT_JS),
          ' sha256:', hashlib.sha256(open(OUT_JS, 'rb').read()).hexdigest())
    print('  cube :', entry['name'], entry['status'], '| faces_encoding =', entry['faces_encoding'])
    for u, s in zip(entry['faces'], entry['face_sha256_rgbm']):
        print('    VIEWER %-100s %s' % (u, s[:16]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
