# -*- coding: utf-8 -*-
"""清理 _f0 首帧转储 + 对渲染仍散架的条目回退静态图。

- 删除 assets/avatar_anim/*_fN.png（页面不引用，只写不读）
- build_avatar_anim.py 不再写 _f0
- 指定条目（默认 da_450002）去掉 _media.anim，改标 anim_status=render_broken（卡面回落官方静态图）
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目/02_wiki/web")
ANIM = ROOT / "assets/avatar_anim"
CAT = ROOT / "data/boards/avatar_catalog.json"
BUILD = ROOT / "tools/build_avatar_anim.py"

BROKEN = {
    "da_450002": "骨架 setup pose 即散架（与动画无关）：角色与粒子/光效分布在画布两端，"
                 "拼装后主体缩在一角；疑与 bone 层级缩放/子骨坐标解释有关，未定位",
}


def main() -> int:
    # 1) 清 _f0
    killed = 0
    for p in ANIM.glob("*_f[0-9]*.png"):
        p.unlink()
        killed += 1
    print("删除首帧转储 %d 张" % killed)

    # 2) 停止生成 _f0
    s = BUILD.read_text(encoding="utf-8")
    old = """        f0 = ANIM_DIR / (iid + "_f0.png")
        if not f0.is_file():
            frs[0].save(f0)
"""
    if old in s:
        s = s.replace(old, "", 1)
        BUILD.write_text(s, encoding="utf-8")
        print("build_avatar_anim.py：已停止写 _f0")
    else:
        print("build_avatar_anim.py：_f0 写入代码已不存在（跳过）")

    # 3) 回退静态图
    d = json.loads(CAT.read_text(encoding="utf-8"))
    hit = 0
    for it in d["items"]:
        if it["id"] in BROKEN:
            m = it.get("_media") or {}
            if m.pop("anim", None):
                hit += 1
            m.pop("anim_meta", None)
            it["anim_status"] = "render_broken"
            it["anim_note"] = BROKEN[it["id"]]
            hit += 1
    CAT.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("回退静态图条目 %d 条" % len(BROKEN), "｜改动", hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
