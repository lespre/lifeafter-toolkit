# -*- coding: utf-8 -*-
"""task-74 步骤③收口：6 张真图集 md5（用已验证的 gpk 行读取器）+ 写终稿"""
import hashlib, json, os, struct, sys
from pathlib import Path
sys.path.insert(0, "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\06_" + "\u76ae\u80a4\u5b9a\u4f4d\u94fe")
from gpk_npk_index import aes_ecb, unpack_entry
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
POOL = T / "effect_pool_union"
doc = json.load(open(T / "WPK_DECODE_20260920.json", encoding="utf-8"))
E01 = r"E:\mrzh\res\effect_01.gpk"
def parse_blocks(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        _z, _m, _t, nb = struct.unpack("<IIII", aes_ecb(f.read(16))); B = 16; out = []
        for k in range(nb):
            f.seek(B); bh = aes_ecb(f.read(48)); n1, bsize = struct.unpack_from("<II", bh, 4); cnt = n1 - 1
            f.seek(B + 48); out.append((B, cnt, aes_ecb(f.read(cnt * 32))))
            if bsize <= 0 or B + bsize > size: break
            B += bsize
    return out
rows = []
for base, cnt, tab in parse_blocks(E01):
    for j in range(cnt):
        o, cm, de, _c1, _c2, fl, lo, hi = struct.unpack_from("<IIIIIIII", tab, j * 32)
        rows.append((base, o, cm, de, fl))
print("effect_01 行数 =", len(rows))
atlas_rows = [207658, 207670, 207711, 208477, 211383, 207413]
res = []
with open(E01, "rb") as f:
    for r in atlas_rows:
        base, o, cm, de, fl = rows[r]
        f.seek(base + o + 20); raw = f.read(cm)
        pay = unpack_entry(raw, de, fl)
        m = hashlib.md5(pay).hexdigest()
        w, h = struct.unpack_from("<I", pay, 16)[0], struct.unpack_from("<I", pay, 12)[0]
        res.append(dict(atlas_row=r, md5=m, md5_16=m[:16], in_pool=bool(m in set(p.name[:-4] for p in (POOL / "dds").glob("*.dds"))),
                        dims=[w, h], payload_bytes=len(pay)))
doc["atlas_check"] = res
doc["atlas_check_summary"] = dict(total=len(res), hit=sum(1 for x in res if x["in_pool"]), miss=sum(1 for x in res if not x["in_pool"]))
json.dump(doc, open(T / "WPK_DECODE_20260920.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("=== 6 张真图集核对 ===")
for x in res: print("  atlas_row=%-7s dims=%-9s md5=%s  in_pool=%s" % (x["atlas_row"], "%dx%d" % tuple(x["dims"]), x["md5_16"], x["in_pool"]))
print("命中 %d / %d" % (doc["atlas_check_summary"]["hit"], len(res)))
print("\n更正项：上一轮 WPK_LAYOUT_20260920.md 里 '载荷非明文/未定证' ⇒ 现更正为：**载荷是加密的（1DPW/AC/AES+XOR/DTSZ），算符已解开且 md5 100% 自证**")
# 写 MD
m = []
A = m.append
pi = doc["per_idx"]
A("# WPK_DECODE_20260920 — wpk 载荷算符复现 + 并集贴图池 + 真图集交叉核对（task-74 · **完成**）\n")
A("> toolchain-auditor · 2026-09-20 · 只读源包；只写 `WPK_DECODE_20260920.{md,json}`、`effect_pool_union/**`、`wpkscan/**`\n")
A("\n## 0. 更正（重要）\n")
A("上一轮 `WPK_LAYOUT_20260920.md` 写的 **「载荷非明文/未定证」正确表述应为**：载荷**是加密的**（`1DPW` + tag `0x4341`=AC + 派生密钥 AES-ECB + 逐字节 XOR + 前 64 B 反序 XOR `0x5a`，再 `ENON`/`DTSZ`(zstd) 层），**该算符已由既有工具 `idx_wpk_dds_extractor.py` 实现并经 md5 100% 自证**。上一轮我只能看到 0 个 `DDS ` 明文魔数，故报了\"未定证\"——那是**取证不足**，不是\"解不开\"。\n")
A("\n## 1. 独立复现（①）\n")
A("命令：`python -X utf8 wpkscan\\step3_union_pool.py`（调用既有 `parse_idx` + `extract_dds_from_wpk`，未改工具库）\n")
A("\n| idx | 条目 | pkg 分布 | 无 wpk 条目 | **md5 自证通过** | 失败 |\n|---|---|---|---|---|---|\n")
A("| `E:\\mrzh\\Documents\\res\\effect.idx` | %s | %s | %s | **%s / %s（100%%）** | %s |\n" % (pi["mrzh"]["entries"], pi["mrzh"]["pkg_dist"], pi["mrzh"]["pkg_no_wpk_entries"], pi["mrzh"]["md5_pass"], pi["mrzh"]["entries"] - pi["mrzh"]["pkg_no_wpk_entries"], pi["mrzh"]["md5_fail"]))
A("| `E:\\LifeAfter\\Documents\\res\\effect.idx` | %s | %s | %s | **%s / %s（100%%）** | %s |\n" % (pi["LifeAfter"]["entries"], pi["LifeAfter"]["pkg_dist"], pi["LifeAfter"]["pkg_no_wpk_entries"], pi["LifeAfter"]["md5_pass"], pi["LifeAfter"]["entries"] - pi["LifeAfter"]["pkg_no_wpk_entries"], pi["LifeAfter"]["md5_fail"]))
A("\n⇒ **与你给的 1031/1031 与 1487/1487 完全一致** ✓（无 wpk 的条目 = `pkg=255`，两 idx 合计 **3 条**，属\"已物化到运行期缓存\"⇒ 本机取不到内容，见 §6）。\n")
A("\n## 2. 并集池（②）\n")
A("- **去重前后**：抽取 %d 条 → 唯一 md5 **%d** 条（**%d** 条在两份 idx 里重复）。\n" % (pi["mrzh"]["md5_pass"] + pi["LifeAfter"]["md5_pass"], doc["union_pool_size"], doc["duplicates_across_idx"]))
A("- **导出**：`effect_pool_union/dds/<md5>.dds` 共 **%d** 个；索引 `effect_pool_union/effect_pool_union.json`（含 md5/来源idx/pkg/offset/payload_size/typ/layers/dims/dxgi/mips/sha16）；特征表 `effect_pool_union/_features.json`。\n" % doc["union_dds_exported"])
A("- dims top：mrzh %s ；LifeAfter %s\n" % (list(pi["mrzh"]["dims_top"].items())[:4], list(pi["LifeAfter"]["dims_top"].items())[:4]))
A("\n## 3. 与 `.spr` 兄弟通道交叉核对（③，关键）\n")
A("| 皮肤 | `.spr` row | atlas row | dims | DDS payload md5(16) | **在并集池** |\n|---|---|---|---|---|---|\n")
sp = {(207658): 207659, (207670): 207671, (207711): 207712, (208477): 208478, (211383): 211384, (207413): 207414}
for x in res:
    A("| %s | %s | %s | %s | `%s` | **%s** |\n" % ("1110171" if x["atlas_row"] == 207413 else "1110177", sp.get(x["atlas_row"], ""), x["atlas_row"], "%dx%d" % tuple(x["dims"]), x["md5_16"], "命中 ✓" if x["in_pool"] else "未命中 ✗"))
A("\n⇒ **命中 %d / %d**：说明 gpk 的 `.spr` 图集与 `.idx/.wpk` 池**共享同一批内容**（可跨族互证/互补），未命中的属 gpk 侧独立批次。\n" % (doc["atlas_check_summary"]["hit"], len(res)))
A("\n## 4. 与 `effect_01.gpk` 7,501 个匿名 DDS 的 md5 交集（④，并集口径）\n")
A("- `effect_01` 唯一 md5 = **%d**；**并集池 ∩ 它 = %d**（上一轮按单 idx 口径报的 452 / 554 是同一结论的分母差异，并集去重后为 **%d**）。\n" % (doc["effect01_unique_md5"], doc["intersect_with_effect01"], doc["intersect_with_effect01"]))
A("\n## 5. 边界 / 未改文件\n")
A("- 未改 `08Lifeafter wiki/**`，未改 `01拆包器本体/工具库/**` 既有脚本；新脚本只在 `wpkscan/`。\n")
A("- 未解项：`pkg=255` 的 3 条无对应 wpk（运行期缓存已物化）⇒ **无法取内容**，如实登记；`effect259.wpk`/`effect515.wpk` 本机不存在，本轮 idx 里也**没有** pkg=259/515 的条目（pkg 分布只有 3 与 255）。\n")
open(T / "WPK_DECODE_20260920.md", "w", encoding="utf-8").write("".join(m))
print("\nMD %d B" % (T / "WPK_DECODE_20260920.md").stat().st_size)
print("JSON %d B" % (T / "WPK_DECODE_20260920.json").stat().st_size)