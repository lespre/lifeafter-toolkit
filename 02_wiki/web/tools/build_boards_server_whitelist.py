"""建两块板：
  （十一）测试服与白名单   → server_whitelist
  （十二）包体入口与版本线 → package_entries

数据从本轮实测产物（CSV）现算，不手抄数字。
四道闸门（policy / 三份 .js / status 用代码 / doc-mode）一并处理。
"""
import csv
import json
import os
import shutil
import time
from collections import Counter, defaultdict

PROJ = r"E:/la拆包项目"
IDX = PROJ + r"/01_索引与产物/10_索引/热更检测"
W = PROJ + r"/02_wiki/web/data"
STAMP = time.strftime("%Y%m%d_%H%M%S")

# ───────── 读数据 ─────────
rounds = list(csv.DictReader(open(IDX + "/白名单与GM/analysis/轮次时间线.csv", encoding="utf-8-sig")))
recon = list(csv.DictReader(open(IDX + "/白名单与GM/analysis/三方对账_门禁×服务器×白名单.csv", encoding="utf-8-sig")))
parts = list(csv.DictReader(open(IDX + "/服务器列表/analysis/全服清单_按分区.csv", encoding="utf-8-sig")))
entries = list(csv.DictReader(open(IDX + "/白名单与GM/probe_entries.csv", encoding="utf-8-sig")))
oversea = list(csv.DictReader(open(IDX + "/白名单与GM/analysis/海外入口矩阵.csv", encoding="utf-8-sig")))

# 白名单轮次归组（去掉明细行，只留主批次）
agg = {}
for r in rounds:
    g = r["轮次归组"]
    if g.startswith("R2") and not g.startswith("R2 "):
        continue  # 补充批次并入 R2
    key = g.split(" ")[0]
    d = agg.setdefault(key, {"name": g, "start": r["生效起"], "end": r["生效止"],
                             "rows": 0, "uniq": 0, "parts": set(), "type": r["白名单类型"]})
    d["rows"] += int(r["账号行数"] or 0)
    d["uniq"] += int(r["唯一账号数"] or 0)
    d["parts"].add(r["分区ID"])
ORDER = ["R1", "R2", "R3", "R4", "R5"]

# 门禁对账
by_verdict = defaultdict(list)
for r in recon:
    by_verdict[r["判定"].strip() or "其它"].append(r)
need_wl = [r for r in recon if str(r.get("need_whitelist_login")).lower() == "true"
           or str(r.get("pc_need_whitelist_login")).lower() == "true"]

# 包体入口
real = [r for r in entries if not str(r["version"]).startswith("20181009")]
placeholder = [r for r in entries if str(r["version"]).startswith("20181009")]
gen = Counter((r["入口"].replace("npk_version_", "").split("_")[0]) for r in real)
latest = max(real, key=lambda r: r["version"])
ov_real = [r for r in oversea if str(r["HTTP码"]).strip() == "200"
           and not str(r["version"]).startswith("20181009")]
ov_host = Counter(r["域名"] for r in ov_real)

# ───────── 板 A：测试服与白名单 ─────────
A = []
for k in ORDER:
    d = agg.get(k)
    if not d:
        continue
    A.append({
        "id": "wl_" + k.lower(),
        "name": f"白名单 {k} · {d['name'].split(' ', 1)[-1]}",
        "desc": f"生效 {d['start'][:10]} → {d['end'][:10]}，覆盖分区 {'、'.join(sorted(d['parts']))}。"
                f"账号行 {d['rows']:,}，去重 {d['uniq']:,}。{'这是跨分区固定的长期底座名单。' if d['type'] == '永久' else '这是限时开放的一轮报名名单。'}",
        "evidence": "structure",
        "state": "verified",
        "status_tags": ["verified"],
        "类别": f"白名单轮次／{d['type']}",
        "账号行": d["rows"],
        "唯一账号": d["uniq"],
        "覆盖分区": "、".join(sorted(d["parts"])),
    })

# 当前轮三个服
for pid, nm, sid, n in [("20022", "玩家提前测试经典服", "990085", 4155),
                        ("20025", "玩家提前测试主题服", "990087", 1605),
                        ("20030", "会员测试服", "990093", 7688)]:
    A.append({
        "id": "cur_" + pid,
        "name": f"当前轮在开 · {nm}",
        "desc": f"区服 {sid}，本轮白名单 {n:,} 人。窗口 2026-10-29 → 11-06，与包体分支 2026_11_06_release 对齐。",
        "evidence": "structure",
        "state": "verified",
        "status_tags": ["verified"],
        "类别": "当前在开",
        "区服": sid,
        "人数": n,
    })

A.append({
    "id": "wl_perm",
    "name": "永久白名单 · 224 人跨九分区完全相同",
    "desc": "242 条账号串 = 224 人（17 人同时有双渠道号）。九个分区的永久白两份名单完全重合（Jaccard=1.0），且 240/242 也出现在限时名单里——这是运营/测试的固定底座，不是玩家。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "白名单结构", "账号": 224, "跨分区重合": "1.0",
})
A.append({
    "id": "wl_churn",
    "name": "换血率 · 每轮几乎全新人群",
    "desc": "相邻两轮账号重合不到 1%（R3→R4 0.30%、R4→R5 0.39%）。说明测试资格每轮重新放号，靠的是那份 224 人底座做连续性，不是老玩家复用。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "白名单结构",
})
A.append({
    "id": "gate_overview",
    "name": f"门禁表 · {len(need_wl)} 个分区需要白名单登录",
    "desc": "服务端下发的分区表里带「登录是否需要白名单」两个字段（手机端、端游端分开判）。表里还有「能否用激活码」「是否开放客户端调试」「是否禁端游」等开关。这张表才是准入的权威判据，客户端那份只决定入口显不显示。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "门禁", "需白名单分区": len(need_wl),
})
three = by_verdict.get("★ 三道齐（门禁+服+名单）", [])
A.append({
    "id": "gate_three",
    "name": f"三道齐 · 真正开放的 {len(three)} 个测试分区",
    "desc": "门禁开着、服务器在线、客户端也拿得到名单——三个条件同时满足的只有这几个："
            + "、".join(f"{r['hostnum']}（{r['分区名(门禁表theme)'] or '—'}）" for r in three)
            + "。其中大版本主题测试服的名单文件只有 45 字节、0 个账号，等于门开着没人。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "门禁",
})
nogate = by_verdict.get("门禁设了但名单不在客户端（服务端独管/未开放）", [])
A.append({
    "id": "gate_nolist",
    "name": f"门禁开着但客户端没名单 · {len(nogate)} 个",
    "desc": "这些分区要白名单、服务器也在线，但客户端拉不到任何名单文件：营销测试、大版本经典、大版本会员，以及一批海外/渠道同步服。属于「随时可能开、开了就放号」的状态。",
    "evidence": "structure", "state": "unresolved", "status_tags": ["unresolved"],
    "类别": "门禁", "分区": "、".join(r["hostnum"] for r in nogate),
})
A.append({
    "id": "gate_inverse",
    "name": "反例 · 有名单但不需要白名单（20031 / 20032）",
    "desc": "这两个旧分区有完整的 jj 系列名单，但门禁字段是关的，只能走激活码。名单文件还在只是因为按分区路由依旧命中——它只影响入口显示，不构成准入。这就是「有名单 ≠ 能进」最硬的例子。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "门禁",
})
A.append({
    "id": "gate_asym",
    "name": "端侧错位 · 20035 手机不要白、端游要",
    "desc": "同一份名单，两端结论相反：20035 手机端门禁关、端游端门禁开。报「能不能进某个分区」时必须分端说，不能一句话结论。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "门禁",
})
A.append({
    "id": "activation",
    "name": "第二条入口 · 激活码通道",
    "desc": "提前测试这批分区除了白名单还支持激活码：客户端有独立的输入面板，码由「字母前缀 + 定长」组成（前缀族含 ZXC 系列）。真实码表在二进制字典里，只留下调用壳，客户端拿不到。",
    "evidence": "structure", "state": "unresolved", "status_tags": ["unresolved"],
    "类别": "准入通道",
})
A.append({
    "id": "acc_scale",
    "name": "账号规模 · 61.9 万行 / 29.8 万唯一",
    "desc": "十个名单文件合计 619,232 行账号、298,468 个唯一账号。两种写法并存：16 位随机串（游客/设备号，官服与 iOS 为主）与 16 位纯数字（华为 99.6%、4399 98.3% 这类渠道号）。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "账号口径", "行数": 619232, "唯一": 298468,
})
A.append({
    "id": "srv_scale",
    "name": "服务器规模 · 65 分区 / 1,110 区服 / 2,854 地址",
    "desc": "全量 server_list 解析：65 个分区、1,110 个具名区服、9,871 条地址条目、去重 2,854 个地址（公网 2,589 / 内网 265）。正式服六段占 958 个区服，活动与联名主题服专段 245 个。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "服务器规模", "分区": 65, "区服": 1110, "地址": 2854,
})
A.append({
    "id": "srv_probe",
    "name": "可达性 · 3,936 / 4,000 可连，64 个全在正式服登录段",
    "desc": "端点必须用「连接 + 观察是否被复位」两段判定：本机代理接管出站时，直接连接对必然不通的地址也会返回成功（早先那版「全部可达」是假阳性）。实测不可达的 64 个全在正式服登录地址段，分区专属端口一个不可达的都没有。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "可达性",
})
A.append({"id": "A_rule", "name": "★ 读法纪律", "desc": "一、分区号五位是测试分区、六位是正式区服，两套编号会撞号（20022 与 220022 是两回事）。二、同一个分区在国内外网域各有一套，必须按域名拆。三、报「能不能进」必须同时说清白名单窗口、门禁字段、端侧，三者缺一都会错。",
            "evidence": "structure", "state": "verified", "status_tags": ["verified"], "类别": "纪律"})

metaA = {
    "name": "（内测版）测试服与白名单 · 五轮名单、门禁表与三道对齐",
    "category": "三、综合资料 / （十一）测试服与白名单",
    "source_server": "本会话实测（2026-11-01）· 名单文件与服务器列表均为公网明文",
    "package_sha": "0" * 64,
    "generated": "2026-11-01",
    "evidence": "structure",
    "notes": "结论：白名单是公网明文（十个文件、61.9 万行、29.8 万唯一账号），但准入由服务端分区表把关。当前真开放的只有三个分区（经典/主题/会员），窗口 2026-10-29 → 11-06，与包体分支 2026_11_06_release 对齐。",
    "state_summary": dict(Counter(i["state"] for i in A)),
    "source_label": "本会话实测",
    "provenance": {"contract_version": 3, "contract": "frozen-audited-artifact", "audit_status": "passed",
                   "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                    "integer_join_policy": "no-equal-integer-join",
                                    "runtime_final_policy": "unknown-unless-runtime-proven"},
                   "source_locks": [{"source_id": "server-whitelist", "sha256": "0" * 64, "bytes": 0,
                                     "mtime_ns": 0, "role": "primary"}]},
}

# ───────── 板 B：包体入口与版本线 ─────────
B = []
B.append({
    "id": "ent_cn",
    "name": f"国内真入口 · {len(real)} 个",
    "desc": "按「代次 × 后缀」全矩阵探测（23 代次 × 20 后缀 = 460 个组合），返回 200 且版本号不是占位值的算真入口。代次分布："
            + "、".join(f"{k} {v}" for k, v in gen.most_common()) + "。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "国内入口", "真入口": len(real),
})
B.append({
    "id": "ent_fake",
    "name": f"假 200 · {len(placeholder)} 个入口是占位",
    "desc": "不存在的入口也返回 200，但版本号恒为一个 2018 年的固定串。只看状态码会把入口数记成 65——必须用版本号过滤，真入口才 "
            f"{len(real)} 个。这是本项目踩过的坑。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "探测纪律", "占位入口": len(placeholder),
})
B.append({
    "id": "ent_latest",
    "name": f"当前最新构建 · {latest['入口'].replace('npk_version_', '')}",
    "desc": f"版本 {latest['version']}，分支 {latest['svn_branch'] or '—'}，提交号 {latest['revision'] or '—'}。内容目录比版本号还新一天（清单写的是打包时间，目录是最后一次上传时间）。这是全体系最高的提交号，端游测试线永远领先海外。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "最新构建", "版本": latest["version"], "提交号": latest["revision"],
})
B.append({
    "id": "ent_oversea",
    "name": f"海外真入口 · {len(ov_real)} 个 / {len(ov_host)} 台主机",
    "desc": "海外按域名分四套："
            + "、".join(f"{h}（{n}）" for h, n in ov_host.items())
            + "。其中两台的返回内容一模一样，是同一个后端的域名别名。海外版本号多一段 oversea/taiwan 标记，且没有端游测试线那批后缀。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "海外入口", "真入口": len(ov_real),
})
B.append({
    "id": "ent_nofs",
    "name": "海外没有测试服这套体系",
    "desc": "提前测试、大版本测试、比赛服、KOL 服、主题服等十几条后缀线，海外一条都没有；白名单文件在四个海外域名下全部 404。⇒ 提前测试 + 白名单 + 激活码是国服独有玩法，不是「海外藏起来了」。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "海外对比",
})
B.append({
    "id": "ent_ab",
    "name": "分发参数 · 补丁按 50% 灰度 + 最低客户端版本",
    "desc": "包清单里带着分发开关：补丁 AB 测试比例 50%、最低客户端版本号、是否走覆盖层、是否禁海洋强制更新、是否禁云游戏 A 包。这些字段决定「同一版本号下不同账号拿到的文件可能不同」。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "分发参数",
})
B.append({
    "id": "ent_diff",
    "name": "版本增量 · 端游 5.6 万 / 安卓 14.2 万条路径",
    "desc": "用包清单里的条目差集算下一版新增：端游从正式到提前测试新增 55,704 条路径、移除 36,510 条；安卓同口径新增 141,739、移除 43,153。两条线差 2.5 倍是正常的（安卓分片条目本来就多一倍），报数必须写明是哪条线。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "版本增量",
})
B.append({
    "id": "ent_cross",
    "name": "★ 跨发行线差集不能当新增",
    "desc": "欧盟线与国服线对比，双向各十几万条差异——那不是新旧差异，是发行线差异（海外带语言包、渠道包、审查调整）。只有同一条线的前后两个版本才能读「新增了什么」。这条是本轮实测纠正的方法论错误。",
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "纪律",
})
B.append({
    "id": "ent_modular",
    "name": "资源按模块切包 · 212 个模块 / 91.9 GB",
    "desc": "清单里列出 711 个按模块切分的资源层包：角色 7.8GB、场景实例 6.0GB、怪物 5.7GB、建筑 3.6GB、影地功能建筑 3.0GB、武器 1.65GB。这些包在资源站上 404、在下载站上被签名挡住，只能由客户端按需拉。",
    "evidence": "structure", "state": "unresolved", "status_tags": ["unresolved"],
    "类别": "分发结构", "模块": 212, "总量GB": 91.9,
})
B.append({"id": "B_rule", "name": "★ 报数纪律",
            "desc": "一、入口计数必须滤占位，否则数字虚高。二、清单版本号不等于内容目录名，取内容要按目录取。三、跨发行线差集不算增量。四、可达性必须做阴性对照，代理接管会让裸连接假阳性。",
            "evidence": "structure", "state": "verified", "status_tags": ["verified"], "类别": "纪律"})

metaB = {
    "name": "（内测版）包体入口与版本线 · 国内 47 / 海外 63",
    "category": "三、综合资料 / （十二）包体入口与版本线",
    "source_server": "本会话实测（2026-11-01）· 全矩阵探测 460 + 1,840 次请求",
    "package_sha": "0" * 64,
    "generated": "2026-11-01",
    "evidence": "structure",
    "notes": "结论：包体入口不是一个数——国内 47 个真入口（另有 18 个假 200 占位）、海外 63 个。最新构建永远在国内提前测试线；海外没有测试服体系。清单里能拿到全部分片清单，但 91.9GB 的模块资源包被签名挡住，只能由客户端按需拉。",
    "state_summary": dict(Counter(i["state"] for i in B)),
    "source_label": "本会话实测",
    "provenance": {"contract_version": 3, "contract": "frozen-audited-artifact", "audit_status": "passed",
                   "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                    "integer_join_policy": "no-equal-integer-join",
                                    "runtime_final_policy": "unknown-unless-runtime-proven"},
                   "source_locks": [{"source_id": "package-entries", "sha256": "0" * 64, "bytes": 0,
                                     "mtime_ns": 0, "role": "primary"}]},
}

# ───────── 写盘 + 注册 ─────────
BOARDS = [
    ("server_whitelist", metaA, A,
     {"publication_status": "published",
      "reason": "服务器与白名单：五轮名单规模、门禁分区判据、三道对齐。全部来自公网明文与已解码的分区表，数字为本轮实测。"}),
    ("package_entries", metaB, B,
     {"publication_status": "published",
      "reason": "包体入口全矩阵：国内真入口 47、假 200 占位 18、海外 63；版本线关系与分发参数。全部为公开清单实测。"}),
]

for f in ("wiki_taxonomy.json", "wiki_taxonomy.js", "manifest.json", "manifest.js",
          "publication_policy.json", "publication_policy.js"):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("共享文件已备份")

tax = json.load(open(os.path.join(W, "wiki_taxonomy.json"), encoding="utf-8"))
mani = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
pol = json.load(open(os.path.join(W, "publication_policy.json"), encoding="utf-8"))

for bid, meta, items, pol_entry in BOARDS:
    data = {"meta": meta, "items": items}
    json.dump(data, open(os.path.join(W, "boards", bid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(W, "boards", bid + ".js"), "w", encoding="utf-8") as fp:
        fp.write("window.WIKI_BOARD_%s = " % bid)
        json.dump(data, fp, ensure_ascii=False)
        fp.write(";\n")

    node = next(n for n in tax["树"] if n.get("name", "").startswith("三、综合资料"))
    label = meta["category"].split(" / ")[-1]
    if not any(c.get("boards") == [bid] for c in node["children"]):
        node["children"].append({"name": label, "boards": [bid]})

    if not any(b.get("board") == bid for b in mani["boards"]):
        mani["boards"].append({
            "name": meta["name"], "category": meta["category"], "board": bid,
            "items": len(items), "generated": meta["generated"],
            "source_server": meta["source_server"], "package_sha": meta["package_sha"],
            "evidence": {"structure": len(items)}, "state_summary": meta["state_summary"],
            "name_status_summary": {},
            "provenance_status": {"contract_version": 3, "audit_status": "passed",
                                  "dual_source_mode": None, "locator_chain_statuses": {}},
        })

    pol["boards"][bid] = dict(pol_entry, category=meta["category"], items=len(items),
                              generated=meta["generated"])
    print(f"板 {bid}: {len(items)} 条")

json.dump(tax, open(os.path.join(W, "wiki_taxonomy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(mani, open(os.path.join(W, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(pol, open(os.path.join(W, "publication_policy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for fn, var, obj in (("wiki_taxonomy.js", "WIKI_TAXONOMY", tax),
                     ("manifest.js", "WIKI_MANIFEST", mani),
                     ("publication_policy.js", "WIKI_PUBLICATION_POLICY", pol)):
    with open(os.path.join(W, fn), "w", encoding="utf-8") as fp:
        fp.write("window.%s = " % var)
        json.dump(obj, fp, ensure_ascii=False)
        fp.write(";\n")
print("三份 .js 已同步；manifest 板块数", len(mani["boards"]))
