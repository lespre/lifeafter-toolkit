# -*- coding: utf-8 -*-
"""二期「铠甲再临(刑天飞影)」奖池板块 —— 已实装版（2026-09-01 快照 BA8A239A）。

证据链（同包闭环）：
  super_fashion_lottery_conf_data key=232 → lottery_id=391782（主池）/ fortune_bag 391783
  → left/right_item_id（左右大奖）+ panel_show_item_ids（奖池面板展示清单，jump 解析）。
命名来源严格分级（吸取 all_equips name/desc 跨记录错位教训）：
  CONFIRMED 用户/硬证据确认；SKIN《武器皮肤总表v3》skin_id 硬命中；gift_data 礼盒名表（key=item_id 可靠）；
  INFER 仅按 ID 段/主题推断（降 structure）。
  ⚠ all_equips_data 的 name/desc/icon 字段在载具/道具行上跨记录错位（194190 被错写成“火箭筒体验版/
    盾补:金木研”，实为载具火刑战驱），故 all_equips 只用于武器数值、绝不用于本板块命名。
板块只列本期面板 10 件；reward_pool 逐格的历史复用旧行一律剔除（原始 slot 证据留 workcopy 备查）。
只读源。"""
import sys, json, struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool, resolve_jump_group

WC = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A")
PKG_SHA = "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
FID = {"super_base":"7E5A5A83B1F07D31","super_chs":"512C733C3B263D37",
       "gift_base":"C5998AD60B305608","gift_chs":"938D86FE498D1B1A"}
# 用户确认 / 有其他硬证据（verified）
CONFIRMED = {
 194190:("火刑战驱","载具","载具结构字段 vehicle_type=3、body_model=character/carrier2025/car_2001005（刑天主题载具，对应刑天载具音频 g66_202608_xingtian），用户确认；all_equips 的 name/desc 跨记录错位已弃用"),
 633070140:("刑天召唤器","召唤器","秘宝池390704 slot22 硬命中“刑天召唤器/刑天变身器”，本期面板展示"),
}
# 武器皮肤名来自《武器皮肤总表_整理版_v3.csv》（8-29 新增段，已交叉核对）
SKIN = {1110181:("疾影枪","手枪 · 紫皮(4)"), 1110182:("火刑电光炮/火刑裁决","榴弹炮 · 紫皮(4)"),
        1110183:("战神烈火剑","冷兵器 · 紫皮(4)")}
# 仅按 ID 段+主题推断（structure，不硬说）
INFER = {633080140:("飞影召唤器","按 633070=刑天召唤器 的 ID 段+本期主题推断，未被名表硬命中")}

man = json.loads((WC/"manifest.json").read_text(encoding="utf-8")); by={e["file_id"]:e for e in man["entries"]}
def xb(p):
    d=p.read_bytes(); at=d.find(b"x{"); s=struct.unpack_from("<I",d,at+2)[0]; return d[at+6:at+6+s]
def load(b,c):
    body=xb(WC/by[FID[b]]["output_file"]); pool=parse_legacy_chs_pool((WC/by[FID[c]]["output_file"]).read_bytes())
    rows,_=decode_table_rows(body,pool); return rows,body
def vv(r): return {k:v[1] for k,v in r.get("values",{}).items()}

# 只用 gift 礼盒名表（key=item_id，可靠）；不使用 all_equips 命名
gift={}
for r in load("gift_base","gift_chs")[0]:
    x=vv(r)
    if x.get("name"): gift[r["key"]]=(x["name"],str(x.get("desc") or ""))

sup,sup_body=load("super_base","super_chs")
gc=struct.unpack_from("<I",sup_body,0)[0]; blob=sup_body[8+4*gc:]
cfg=next(r for r in sup if r["key"]==232); cv=vv(cfg)
panel=resolve_jump_group(blob,int(cv["panel_show_item_ids"].split(":",1)[1]))
left,right=cv.get("left_item_id"),cv.get("right_item_id")

def name_of(iid):
    if iid in CONFIRMED: n,extra,how=CONFIRMED[iid]; return n,how,"verified",extra
    if iid in SKIN: return SKIN[iid][0],"武器皮肤总表v3(skin_id 硬命中)","verified",SKIN[iid][1]
    if iid in INFER: n,how=INFER[iid]; return n,how,"structure","召唤器(推断)"
    if iid in gift:
        n,desc=gift[iid]; return n,"gift_data 礼盒名表硬命中","verified",desc[:48]
    return "(待命名)","gift/皮肤总表/硬证据均未命中","candidate",""

items=[]
for iid in panel:
    n,how,ev,extra=name_of(iid)
    role="左大奖(时装箱)" if iid==left else ("右大奖(时装箱)" if iid==right else "面板展示")
    items.append({"id":f"panel_{iid}","name":n,"evidence":ev,
        "source":f"super_fashion_lottery_conf_data key232 panel_show_item_ids；{how}",
        "tier":role,"item_id":iid,"slot":extra,"layer":"面板展示/大奖"})

evc={}
for it in items: evc[it["evidence"]]=evc.get(it["evidence"],0)+1
board={"meta":{"name":"抽奖奖池·铠甲再临(刑天飞影)（已实装 2026-09-01）","category":"奖池类-限时主题",
    "source_server":"Documents 体验服 script.py314 快照 BA8A239A（9-1 20:40 二期实装推送）",
    "package_sha":PKG_SHA,"generated":"2026-09-01","evidence":"verified",
    "notes":("二期已实装。主池 lottery_id=391782、福袋 391783、UI=PanelSuperFashionLotteryV15、宣传视频 huodong/kaijiayongshixia.mp4；"
        "左大奖=刑天铠甲时装箱(139292)、右大奖=飞影铠甲时装箱(139293)。面板 10 件：刑天主题载具火刑战驱、"
        "3 把联动武器皮肤(疾影枪/火刑电光炮/战神烈火剑)、刑天/飞影召唤器、球状闪电与酸焰激流核芯。"
        "命名只用 gift 礼盒表/武器皮肤总表/硬证据；all_equips 的 name/desc 因跨记录错位不参与命名。"
        "reward_pool 逐格里被历史活动复用的无关旧行已全部剔除（原始 slot 证据留 workcopy 备查）。"
        f"证据分布 {evc}。")},
    "items":items}
out=ROOT/"data"/"boards"/"lottery_kaijiazailin.json"
out.write_text(json.dumps(board,ensure_ascii=False,indent=1),encoding="utf-8")
print("写出",out.name,"共",len(items),"条",evc)
for it in items: print(" ",it["evidence"],it["item_id"],it["name"])
