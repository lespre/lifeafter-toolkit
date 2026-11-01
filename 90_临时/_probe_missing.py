# -*- coding: utf-8 -*-
"""检查 fashion_data 的 100 个字段里，哪些还没落进板产物。"""
import sys, pathlib, struct, collections, json, re
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'fashion_data.py').read_bytes(); at=raw.find(b'x{')
L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((CD/'fashion_data_chs.py').read_bytes())
F=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]
def mk(blob,pool):
    def ev(g,out):
        k,els=g
        for e in els:
            if k==0x0b:
                g2=BT.read_27_group(blob,e)
                if g2: ev(g2,out)
            elif k==0x05: out.append(pool[e] if e<len(pool) else None)
            else: out.append(e)
    def one(r,f):
        got=r['values'].get(f)
        if not got: return None
        tag,v=got
        if tag!='0x0b': return v
        try:
            off=int(str(v).split(':')[1]); out=[]
            g=BT.read_27_group(blob,off)
            if g: ev(g,out)
            return out
        except Exception: return None
    return one
fo=mk(blob,pool)
v=lambda x: x[1] if isinstance(x,tuple) else x
# 字段 → 非空行数 + 样例
info={}
for r in F:
    for f,x in r['values'].items():
        if x in (None,'',[],{}): continue
        d=info.setdefault(f, {'n':0,'ex':[]})
        d['n']+=1
        if len(d['ex'])<2:
            s=str(fo(r,f) if f in ('change_color_id','hair_change_color_id','model_change_color_id','start_show_ts','gift_package_id','bg_ids','anim_graph_id','ui_anim_graph_id','value_word_ids','other_get_methods','uncap_appear_gender','new_bone_soft_bone_id','green_model_path_female','green_model_path_female_high','forbid_primary_high_model','theme_codes','faked_times_limit','valid_scene_ids','special_idle_anims','suit_buff_id','mutex_modules','appear_ids','icons','replace_flower_path') else v(x))[:46]
            d['ex'].append((str(v(r['values'].get('name'))), s))
board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
blob_txt=json.dumps(board, ensure_ascii=False)
print('fashion_data 字段数', len(info))
# 已在产物里出现过的字段名（按卡片字段名 + 技术字段名映射）
mapped = {
 'name','desc','man_desc','female_desc','man_name','female_name','charm_value','level','icons','part_type','brand_id',
 'model_id','appear_ids','valid_days','show_no_have','fashion_preview','force_gender','reborn_vis','replace_flower_path',
 'replace_flower_id','suit_buff_id','mutex_modules','takeoff_head','not_show_rebirth_makeup','special_idle_anims2',
 'fashion_action_id','point_light_id','foreign_name','is_2025','is_climb_tower','new_fashion_id_str','sort_key',
 'change_color_id','hair_change_color_id','model_change_color_id','start_show_ts','gift_package_id','bg_ids',
 'anim_graph_id','ui_anim_graph_id','value_word_ids','rebirth_tex','other_get_methods','uncap_appear_gender',
 'is_new_bone','new_bone_soft_bone_id','green_model_path_female','green_model_path_female_high','preview_id',
 'friendliness','socket_model_use_high_model','forbid_primary_high_model','theme_codes','is_slim_bag',
 'faked_times_limit','valid_scene_ids',
}
print('\n== 未落板的 fashion_data 字段（非空行数 ≥ 1）==')
miss=[]
for f,d in sorted(info.items(), key=lambda kv:-kv[1]['n']):
    if f in mapped: continue
    miss.append((f,d['n'],d['ex']))
for f,n,ex in miss:
    print(f'  {f:34s} 行{n:6d}  例: {ex[0]}')
print('\n未落字段数', len(miss))
