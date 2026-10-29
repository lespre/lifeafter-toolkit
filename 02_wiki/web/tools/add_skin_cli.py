# -*- coding: utf-8 -*-
"""给 la.py 加 skin 命令：fx-names 解武器皮肤战斗表现正式名 / check 与现有产物比对。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/la.py")


def main() -> int:
    s = P.read_text(encoding="utf-8")

    # 1) 实现函数：插到 cmd_vehicle 之前
    anchor = "def cmd_vehicle(a) -> int:"
    if anchor not in s:
        raise SystemExit("找不到 cmd_vehicle 锚点")
    func = '''def cmd_skin(a) -> int:
    """武器皮肤：fx-names 解析战斗表现正式名 / check 与现有产物比对。"""
    sys.path.insert(0, str(WEB))
    from pipelines.parsing import effect_show_names as ESN   # noqa: PLC0415

    default_out = PROJ / "01_索引与产物/30_分析/weapon_skin_effect_show.json"
    try:
        data, st = ESN.parse(a.cdata)
    except Exception as e:                                   # noqa: BLE001
        print("解析失败：%s" % e)
        return 2

    print("皮肤 %d ｜ 表现项 %d ｜ 记录 %d ｜ 字串池 %d"
          % (st["skins"], st["items"], st["records"], st.get("chs_strings", 0)))
    print("每皮肤项数 %s" % st["per_skin"])
    problems = ESN.self_check(data)
    print("自检 %s" % ("通过" if not problems else problems))

    out = pathlib.Path(a.out) if a.out else default_out
    if a.action == "fx-names":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("写出 %s（%d B）" % (out, out.stat().st_size))
        return 0 if not problems else 1

    # check：与已有产物比对
    if not out.is_file():
        print("产物不存在：%s（先跑 skin fx-names）" % out)
        return 2
    old = json.loads(out.read_text(encoding="utf-8"))
    added = sorted(set(data) - set(old))
    gone = sorted(set(old) - set(data))
    changed = sorted(k for k in set(data) & set(old) if data[k] != old[k])
    print("比对 %s：新增皮肤 %d ｜ 消失 %d ｜ 内容变更 %d"
          % (out.name, len(added), len(gone), len(changed)))
    for label, keys in (("新增", added), ("消失", gone), ("变更", changed)):
        if keys:
            print("  %s %s%s" % (label, keys[:5], " …" if len(keys) > 5 else ""))
    bad = bool(added or gone or changed) or bool(problems)
    print("结论 %s" % ("与现有产物一致" if not bad else "存在差异"))
    return 1 if bad else 0


'''
    s = s.replace(anchor, func + anchor, 1)

    # 2) 注册子命令：插在 vehicle 注册之后
    vanchor = '    vh.add_argument("--dry-run", action="store_true",\n                    help="只算不写（仅 build）")\n'
    if vanchor not in s:
        raise SystemExit("找不到 vehicle 注册锚点")
    reg = vanchor + '''
    sk = sub.add_parser("skin", help="武器皮肤：fx-names 解战斗表现正式名 / check 与现有产物比对")
    sk.add_argument("action", choices=["fx-names", "check"])
    sk.add_argument("--cdata", help="cdata 目录（默认按项目根推算，或 LA_CDATA）")
    sk.add_argument("--out", help="产物路径（默认 01_索引与产物/30_分析/weapon_skin_effect_show.json）")
'''
    s = s.replace(vanchor, reg, 1)

    # 3) 分发
    danchor = '    if a.cmd == "vehicle":\n        return cmd_vehicle(a)\n'
    if danchor not in s:
        raise SystemExit("找不到分发锚点")
    s = s.replace(danchor, danchor + '    if a.cmd == "skin":\n        return cmd_skin(a)\n', 1)

    P.write_text(s, encoding="utf-8")
    print("la.py 已加 skin 命令（fx-names / check）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
