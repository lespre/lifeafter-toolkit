# -*- coding: utf-8 -*-
"""render_source_only.py v2 — Source-only 渲染: 只用未修改的源贴图与源数据, 零人工校色/选面/覆盖。
输出:
  source_minimal.png       源贴图 + 观察灯光 (无任何人工叠加)
  source_normal_RG.png     + 源法线 4012 (R,G通道解码 · 规范RGBA)
  source_fresnel.png       + 刃口光 [近似: 菲涅尔/定向光泽系数为人工近似, 非源数值]
  source_unlit_albedo.png  严格 Unlit: 仅 Base Color (无光照/无高光/无环境/无泛光/无knee/无后处理)
  source_only_trace.json   代码路径 / 输入哈希 / 贴图映射 / 通道选择 / 近似项标记
"""
import sys, os, json, hashlib, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_neox_mesh as R

MESH = r'E:\la拆包项目\03拆包产物\weapon\003995.mesh'
TEXD = r'E:\la拆包项目\03拆包产物\render_jiguangjian'
OUT  = r'E:\la拆包项目\03拆包产物\render_jiguangjian\source_only'
os.makedirs(OUT, exist_ok=True)

P, uv, idx, meta = R.parse_mesh(MESH)
T = {n: os.path.join(TEXD, f'tex_{n}.png') for n in (4009, 4010, 4011, 4012, 4013)}
TEXMAP = {1: T[4009], 2: T[4009]}   # sub1/sub2 晶体材质 -> b_m(4009) 假设

LIGHT = dict(spec_str=0.78, spec_pow=48, spec2_str=0.15, glow=0.34, bloom=0.13,
             ambient=0.115, diffuse=0.80, nl_pow=1.50, base_gamma=1.0,
             knee=0.70, knee_k=2.8, envk=0.26, rimk=0.8)
GEOM  = dict(sub_offsets=meta['sub_offsets'], roll_deg=50.0, weld_smooth=True, ss=2, size=(1560,1100))

# A 最小(源贴图+观察灯光)
R.render(P, uv, idx, os.path.join(OUT,'source_minimal.png'),
         tex=T[4011], tex_map=TEXMAP, emi=None, nrm=None, edgek=0.0, edge_sheen_k=0.0, **LIGHT, **GEOM)
# B + 源法线(4012 R,G通道 · 规范RGBA)
R.render(P, uv, idx, os.path.join(OUT,'source_normal_GB.png'),
         tex=T[4011], tex_map=TEXMAP, emi=None,
         nrm=T[4012], nrm_map={0:T[4012]}, nrm_ch=(0,1), nrm_str=1.0, edgek=0.0, edge_sheen_k=0.0, **LIGHT, **GEOM)
# C + 刃口光(近似项)
R.render(P, uv, idx, os.path.join(OUT,'source_fresnel.png'),
         tex=T[4011], tex_map=TEXMAP, emi=None,
         nrm=T[4012], nrm_map={0:T[4012]}, nrm_ch=(0,1), nrm_str=1.0,
         edgek=0.68, edge_sheen_k=0.55, edge_sheen_mu=0.52, edge_sheen_sigma=0.22,
         edgecol=(0.78,0.87,1.00), **LIGHT, **GEOM)
# D 严格 Unlit: 仅 Base Color
UNLIT = dict(sub_offsets=meta['sub_offsets'], roll_deg=50.0, weld_smooth=True, ss=2, size=(1560,1100),
             spec_str=0.0, spec2_str=0.0, rimk=0.0, edgek=0.0, edge_sheen_k=0.0,
             glow=0.0, bloom=0.0, ambient=1.0, diffuse=0.0, nl_pow=1.0, base_gamma=1.0,
             knee=1.0, knee_k=1.0, envk=0.0)
R.render(P, uv, idx, os.path.join(OUT,'source_unlit_albedo.png'),
         tex=T[4011], tex_map=TEXMAP, emi=None, nrm=None, **UNLIT)
print('ALL DONE')

def _sha(p):
    try: return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
    except Exception: return None
trace = {
 "script": "render_source_only.py v2 (实际执行路径)",
 "run_id": time.strftime('%Y%m%d_%H%M%S')+"_SRC",
 "code_path": {
   "parser": "render_neox_mesh.parse_mesh",
   "renderer": "render_neox_mesh.render",
   "geometry_ops": ["weld_smooth=True (顶点按位置焊接 7943->4013 后平均法线, 修 UV 缝分裂)"],
   "lighting_observation": "渲染器固定观察灯光(非源数据): spec .78/48+.15, amb .115, dif .80, nl_pow 1.5, envk .26, bloom .13, knee .70",
   "unlit_variant": "diffuse/spec/env/fresnel/bloom/knee 全关, ambient=1.0 -> 仅 Base Color",
 },
 "input_hashes_sha256_16": {
   "script": _sha(os.path.abspath(__file__)),
   "renderer": _sha(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render_neox_mesh.py')),
   "mesh": _sha(MESH),
   "c159_material": _sha(os.path.join(os.path.dirname(MESH), '003996.c159')),
   "c159_object": _sha(os.path.join(os.path.dirname(MESH), '003997.c159')),
   "textures": {str(n): _sha(T[n]) for n in (4009,4010,4011,4012,4013)},
 },
 "texture_mapping": {
   "sub0": {"base":"tex_4011.png (004011=001a, 未修改)", "normal":"tex_4012.png (004012=001n), 通道 R,G (规范RGBA)",
   "mask":"tex_4013.png (004013=001m) 仅R通道变化 (规范RGBA; 旧称 B通道=光滑度/光泽度 已撤销, 语义待G-buffer定案); 接入途径=render_material_layers.py --polarity smooth",
            "emissive":"未接入"},
   "sub1": {"base":"tex_4009.png (004009=001b_m, 假设)"},
   "sub2": {"base":"tex_4009.png (假设)"}
 },
 "channel_decisions": {"normal_4012": "R,G (规范RGBA; 原'GB'结论源于解码器 BGRA 误读, 2026-09-15 修正)"},
 "c159_param_probe": {
   "status": "部分解析 (序列化格式已破: [01 00 01 13][类型][值]; 名称-数值完整配对待确认)",
   "found": {
     "material0_floats": [2.82, 0.33, 1.3, 1.3, 0.49, 0.8, 3.09, 0.71, 0.6, 0.95, 0.78, 1.24, 0.26, 1.2],
     "material0_colors": [[0.3373,0.3373,0.3373],[0.2510,0.2196,0.2314],[0.6588,0.6824,0.7608],[0.2627,0.3020,0.4039]],
     "material1_red_colors": [[1.0,0.0,0.0],[0.8549,0.0,0.0],[0.2431,0.0,0.0]],
     "note": "材料1(pbr_crystal,护手/宝石)块内解析出三个纯红颜色 -> 宝石红色来自源参数, 无需人工Tint"
   }
 },
 "approximations_marked": [
   "刃口菲涅尔(edgek=0.68)/定向光泽(sheen .55/.52/.22) 系数 = 人工近似(非源数值, 待与 c159 参数配对后替换)",
   "观察灯光整组 = 渲染器固定值(非源)",
   "跨缝法线调和(在管线中) = 几何处理(非源数据)",
 ],
 "disabled": ["edgeface_mask/edgeface_rgb", "坐标阈值选面(spike/grip)", "屏幕距离带",
             "tex_4011_v19.png", "_mk_silver", "tint_map", "face_overrides", "发光染色", "后处理R2-R7(本脚本)"],
 "pipeline_source_mode": "weapon_skin_pipeline.py --source : 走同一源材质路径, 绕过 post_process, 输出 provenance.json (source_data_integrity / shader_fidelity 两拆分)"
}
with open(os.path.join(OUT,'source_only_trace.json'),'w',encoding='utf-8') as f:
    json.dump(trace,f,ensure_ascii=False,indent=1)
print('trace:', os.path.join(OUT,'source_only_trace.json'))
