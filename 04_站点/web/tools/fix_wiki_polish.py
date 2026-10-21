# -*- coding: utf-8 -*-
r"""wiki 修尾：标题中文化、时装缩略图、两行标题、路径去编号。"""
from __future__ import annotations

import pathlib

P = pathlib.Path(r"E:/la拆包项目/04_站点/web/wiki.html")

ZH_FN = r'''  var ZH_MAP=[[/identity unresolved/g,'身份待确认'],[/runtime final unknown/g,'运行时未确认'],
    [/LOTTERY_POOL_RESOLVED/gi,'奖池解析'],[/ITEM_MASTER/gi,'道具总表'],
    [/all_equips/g,'装备属性表'],[/common_item_data_base/g,'道具总表'],
    [/weapon_skin_data/g,'武器皮肤表'],[/reward_pool_data_base/g,'奖池表'],
    [/gift_data/g,'礼盒表'],[/huodong_conf/g,'活动配置'],
    [/schema\s*(\d+)/gi,'结构 $1'],[/\bschema\b/gi,'结构'],
    [/\bv0\.\d+/gi,''],[/\bsource-locked\b/gi,'锁源'],[/\bverified\b/gi,'已核验'],
    [/\bunresolved\b/gi,'待确认'],[/\bcandidate\b/gi,'候选'],[/\bstatic config\b/gi,'静态配置']];
  function zhName(s){
    var out=String(s==null?'':s);
    for(var i=0;i<ZH_MAP.length;i++) out=out.replace(ZH_MAP[i][0],ZH_MAP[i][1]);
    return out.replace(/\s*→\s*/g,' 的 ').replace(/\s{2,}/g,' ').replace(/\s*·\s*·\s*/g,' · ').trim();
  }
'''

CSS_FIX = r"""
/* --- 标题两行、缩略图、路径 --- */
.tile .tname{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden;font-size:12.5px;line-height:1.4;max-height:2.8em}
.tile{padding:11px 12px;align-items:flex-start}
.tile .thumb{margin-top:2px}
.tiles{grid-template-columns:repeat(auto-fill,minmax(272px,1fr))}
"""


def main() -> int:
    h = P.read_text(encoding="utf-8")
    # 1) 时装缩略图换成真实存在的文件
    h = h.replace("assets/fashion_icon_refs/icon_bag_f_3045003_3_b.png",
                  "assets/fashion_icon_refs/icon_110240_b.png")
    # 2) 插入中文映射函数（放在 cleanTitle 之前）
    if "function zhName(" not in h:
        i = h.find("  function cleanTitle(b, nm){")
        h = h[:i] + ZH_FN + "\n" + h[i:]
    # 3) cleanTitle 走中文化
    h = h.replace("    return s || nm;\n  }", "    return zhName(s || nm);\n  }")
    # 4) 路径 meta 去编号 + 中文化
    h = h.replace("(path ? ' · ' + path.split(' · ').pop() : '')",
                  "(path ? ' · ' + zhName(path.split(' · ').pop()).replace(/^[（(][^）)]*[）)]\\s*/,'') : '')")
    # 5) CSS 追加
    if "/* --- 标题两行" not in h:
        j = h.find("</style>")
        h = h[:j] + CSS_FIX + h[j:]
    P.write_text(h, encoding="utf-8")
    print("修尾完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
