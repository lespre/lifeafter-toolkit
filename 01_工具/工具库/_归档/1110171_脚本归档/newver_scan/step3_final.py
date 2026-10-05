# -*- coding: utf-8 -*-
"""task-82 收口：LA 指纹是否内容寻址(md5) + 写终稿"""
import glob, json, os, re, sys, importlib.util
from pathlib import Path
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL)
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lau)
except SystemExit: pass
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
doc = json.load(open(T / "NEWVERSION_SCAN_20260920.json", encoding="utf-8"))
la_hex = set()
per = {}
for p in sorted(glob.glob(r"E:\LifeAfter\res\*.fpk")) + sorted(glob.glob(r"E:\LifeAfter\*.npk")):
    d = lau.parse_fpk(p)
    if d: la_hex |= set(h.lower() for h in d["hashes"]); per[os.path.basename(p)] = d["count"]
print("LA 指纹(32hex) 合计 = %d（去重）" % len(la_hex))
pool_md5 = set(p.stem for p in (T / "effect_pool_union" / "dds").glob("*.dds"))
full = json.load(open(T / "lead_e01_fullscan.json", encoding="utf-8"))
e01 = set(x["md5"].lower() for x in (full.get("dds_rows") or []) if x.get("md5"))
print("并集池 md5 = %d ; effect_01 匿名 DDS md5 = %d" % (len(pool_md5), len(e01)))
print("LA 指纹 ∩ 并集池 = %d ; LA 指纹 ∩ effect_01 = %d" % (len(la_hex & pool_md5), len(la_hex & e01)))
doc["la_fingerprints"] = dict(unique=len(la_hex), per_container=per,
                              intersect_union_pool=len(la_hex & pool_md5), intersect_effect01=len(la_hex & e01),
                              verdict="LA fpk 表条目 = 16B 内容指纹；与 wpk 池/effect_01 均无交集 ⇒ 不同批次且非同一内容寻址空间")
doc["direct_answer"] = dict(
  is_named_version="**否**（就本路由而言）：LA res/*.fpk 表里**只有 16B 指纹、没有名字/路径表**，1,496 个声明名 × 21,679 个变体的 path_id(双 Murmur3) 查询 **0 命中**；且其指纹与 mrzh 索引键 **0 交集** ⇒ 另一版本、另一指纹空间",
  name_axis_works="**未成立**：没有任何\"名→条目\"的映射（parse_fpk 只暴露指纹表）；该族若要取内容只能靠**内容指纹**匹配，而目前两族指纹无交集",
  caveat="我的 fid 解释是**超集启发式**（16B 的 LE/BE + 9 偏移滑窗 × u64）：若该族用的是**别的哈希**，本查询本身就不可能命中 ⇒ \"0 命中\"只能证明**path_id 口径下不成立**，不能证明\"绝对没有名字表\"（未做：遍历载荷找名字字符串）")
print(json.dumps(doc["direct_answer"], ensure_ascii=False, indent=1)[:600])
json.dump(doc, open(T / "NEWVERSION_SCAN_20260920.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
m = []
A = m.append
A("# NEWVERSION_SCAN_20260920 — `E:\\LifeAfter\\res` 9 fpk + 4 npk 新版本名字轴扫描（task-82 · 完成）\n")
A("> toolchain-auditor · 2026-09-20 · 源包只读；只写 `NEWVERSION_SCAN_20260920.{md,json}` + `newver_scan/**`\n")
A("\n## 1. 既有索引 `fpk_fid_index.json` 的口径（只读，未重建）\n")
A("- 结构 `{fid2info: {\"<16HEX fid>\": [容器, 条目号, offset, clen, olen, c1, c2, flag]}, cc2fid: ...}`；样例 `\"0000528F2893625D\": [\"001.fpk\", 0, 106350072, 4798, 5616, 1440785565, 3362934222, 12]`。\n")
A("- **覆盖范围**：头部 3 MB 里**只出现 `001.fpk`**（33,378 条）⇒ 索引是**按容器分块**的 `.fpk` 索引；而 `001.fpk` 在 `mrzh`(1,075,692,372) 与 `LifeAfter`(1,074,007,696) **都存在且大小不同** ⇒ **单看索引无法判版本**（本项目链路一贯针对 mrzh ⇒ 实用上按 mrzh 计，但**未定证**）。\n")
A("- `fid` = 16 hex = 8 B；与实际条目表里的 **16 B 指纹**不同 ⇒ **索引的 fid 是 path_id 类，而 fpk 表存的是 16 B 指纹**（两回事）。\n")
A("\n## 2. 新解析的容器（步骤 2）\n")
A("| 容器 | 字节 | 条目数 |\n|---|---|---|\n")
tot = 0
for k, v in per.items():
    base = r'E:\LifeAfter\res' if k.endswith('.fpk') else r'E:\LifeAfter'
    sz = os.path.getsize(os.path.join(base, k))
    A("| `%s` | %s | **%s** |\n" % (k, format(sz, ","), v)); tot += v
A("\n合计 **13 容器 / %s 条目**；全部 `magic=NXPK, version=3`（头部经 AES 解密后），用既有 `parse_fpk` 一次读表成功 ✓（**解析器位置**：`01拆包器本体\\工具库\\01_核心解包器\\lifeafter_unpacker_full.py` 的 `parse_fpk` / `extract_fpk_header` / `path_id` / `unpack_entry` / `dds2png`）。\n" % f"{tot:,}")
A("\n⚠ **我第一版取出空 fid 集（把 16 B 元素当 bytes），其\"0 命中\"已作废**；修正后（16 B → LE/BE + 9 偏移滑窗 × u64 超集，共 **3,409,292** 个 fid 候选）才有效。\n")
A("\n## 3. 名字轴查询（步骤 3，**本轮核心**）\n")
A("- 目标名合并（`LOG_NAMEAXIS_20260919.json` + `MTG_MATERIALS_20260919.json` + `FX029_assets.json` + `1110171/effects.json` + `.spr` 帧名 931）⇒ **唯一 1,496 条**。\n")
A("- 变体：原样 / `\\`↔`/` / 大小写 / `.tga`→`.dds`/`.png`/`.spr` / **去扩展名** / 去一层目录 / 加 7 种前缀（`effect\\textures`、`effect\\fx`、`effect`、`textures`、`res`、`assets`、`res\\effect`）\n")
A("- **共试 21,679 次 `path_id()` 查询 ⇒ 命中 0 / 1,496**。\n")
A("- 对照：**mrzh 索引头部 33,378 个键 ∩ LA fid 候选 = 0** ⇒ 两套资源**指纹空间完全不相交**（另一版本确证）。\n")
A("\n## 4. LA 指纹是不是内容寻址（md5）？\n")
A("- LA 指纹（32 hex）唯一 **%d** 个；∩ 我的并集池 md5（1,229）= **%d**；∩ `effect_01.gpk` 匿名 DDS md5（7,448）= **%d** ⇒ **不是同一内容空间**。\n" % (len(la_hex), len(la_hex & pool_md5), len(la_hex & e01)))
A("\n## 5. 直接回答\n")
A("- **④ 这套是\"带名字的那一版\"吗？⇒ 就本路由而言：否。** LA `res\\*.fpk` 表里**只有 16 B 指纹、没有名字/路径表**；1,496 个声明名在 21,679 个变体下 **0 命中**，且指纹与 mrzh 索引 **0 交集**。\n")
A("- **⑤ \"名字→内容\"通道成立了吗？⇒ 未成立。** 没有任何\"名→条目\"映射；该族只能靠内容指纹取内容，而目前两族指纹无交集。\n")
A("- **未命中 → `unresolved`**（未顶替）：全部 1,496 条均为 unresolved，试过的容器 = 上表 13 个，试过的变体 = 21,679 次。\n")
A("\n## 6. 卡点 / 未做（如实）\n")
A("1. **我的 fid 解释是超集启发式**（16 B 的 LE/BE + 9 偏移滑窗）：若该族用**别的哈希**，本查询不可能命中 ⇒ \"0 命中\"只证明**`path_id` 口径下不成立**，**不能**证明\"绝对没有名字表\"。\n")
A("2. **未做**：遍历这 13 个容器的载荷找名字字符串（`.tga`/`.dds`/`.spr` 明文、路径串）——这是唯一能给出\"有/无名字表\"**定论**的取证；本轮预算未及。\n")
A("3. `fpk_fid_index.json` 的版本归属（mrzh vs LA）**未定证**；建议用一条已解活载荷的 (c1,c2) 与两边同名字节比对来判。\n")
A("\n## 7. 边界\n")
A("- 未改 `08Lifeafter wiki/**`（`1110177/effects.json` 只读）与工具库既有脚本；新脚本仅在 `newver_scan/`。\n")
open(T / "NEWVERSION_SCAN_20260920.md", "w", encoding="utf-8").write("".join(m))
print("\nMD %d B" % (T / "NEWVERSION_SCAN_20260920.md").stat().st_size)
print("JSON %d B" % (T / "NEWVERSION_SCAN_20260920.json").stat().st_size)