# -*- coding: utf-8 -*-
import sys, struct, pathlib, json, collections
PROJ = pathlib.Path('E:/la拆包项目')
sys.path.insert(0, str(PROJ/'00_规范与工具/工具/工具库/00_共享核心'))
from toolkit_core import bindict_table as BT
CD = PROJ/'01_索引与产物/41_还原树/pe/配置/com/cdata'
raw=(CD/'fashion_data.py').read_bytes(); at=raw.find(b'x{')
L=struct.unpack_from('<I',raw,at+2)[0]; body=raw[at+6:at+6+L]
cnt=struct.unpack_from('<I',body,0)[0]; blob=body[8+4*cnt:]
pool=BT.parse_legacy_chs_pool((CD/'fashion_data_chs.py').read_bytes())
rows=BT.decode_table_rows(body,pool,resolve_jumps=False,lenient=True)[0]

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

board=json.loads(pathlib.Path('02_wiki/web/data/boards/fashion_wardrobe.json').read_text(encoding='utf-8'))
owner={}
for it in board['items']:
    for k in (it.get('row_keys') or []):
        try: owner[int(k)]=it['id']
        except Exception: pass

CANDS="""change_color_id change_color_idx change_color_socket hair_change_color_id model_change_color_id
other_get_methods gift_package_id gift_package_present_times_limit obtain_notify faked_times_limit
is_available_glowstick start_show_ts show_time_offset_ids time_offset_ori_show_valid_times valid_scene_ids
uncap_appear_gender is_slim_bag forbid_primary_high_model socket_model_use_high_model is_new_bone
new_bone_soft_bone_id green_model_path_female green_model_path_female_high rebirth_tex zhexing_type
theme_codes flowing_light_group_id dynamic_macro_name hd_run_replace_anim preview_id ui_anim_graph_id
anim_graph_id special_idle_anims2 can_hide_special_idle_anim bg_ids value_word_ids friendliness
team_match_bg_config team_match_bg_conf hide_other_part hide_part bag_fake_entryword special_fixed_attr_ids
training_rank_season_id force_gender action_disable_soft_bone anim_graph_id_unlink""".split()

out=[]
for f in CANDS:
    nrow=0; cards=set(); samples=[]
    for r in rows:
        v=one(r,f)
        if v in (None,'',[],{},0,False): continue
        nrow+=1
        oid=owner.get(r['key'])
        if oid: cards.add(oid)
        if len(samples)<3:
            s=str(v)[:40]
            if s not in samples: samples.append(s)
    if nrow==0: continue
    out.append((f,nrow,len(cards),samples))
out.sort(key=lambda x:-x[2])
for f,nr,nc,s in out:
    print(f'{f:34s}行{nr:6d}  卡{nc:5d}  {" | ".join(s)}')
