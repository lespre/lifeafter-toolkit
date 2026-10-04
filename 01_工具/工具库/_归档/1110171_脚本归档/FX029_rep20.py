# -*- coding: utf-8 -*-
'''task-62：报告 §20（已知技术债 + source_sfx 命名口径裁定 + (b) 就绪状态）'''
import io, hashlib, os, sys
sys.stdout.reconfigure(encoding='utf-8')
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_report.md'
sec = u'''

---

## §20 task-62 (b) 就绪状态 · source_sfx 命名口径 · 已知技术债

### 20.1 source_sfx 命名口径（lead 裁定 2026-09-19，已落到脚本）
`_dg.sfx` 的**文件名未被直证**（env-auditor 盘点清单只直证了同族 `fx_skin_2003_029_daoguang_02.sfx`）⇒ dg 节点**不写**无保留的 `source_sfx` 名，改为：
- **主键（直证）**：`source_sfx_id = "gres\\0057.gpk#32153"`；
- **人类可读名（降级）**：`source_sfx_name_inferred = "fx_skin_2003_029_dg.sfx"` + `source_sfx_name_evidence = "inferred_from_family_naming"`；
- 每行另带 `dg_provenance = {container, row:32153, off, dec:66424, sha16:"9F4FE3A6AD3F8851", note}`。
- **status_reason 表述统一为**：「**资产已按容器坐标定位并接入（名字为同族命名推定）**」。
干跑复核：A2 分布显示 `gres\\0057.gpk#32153` × **23**（不再是未加限定的文件名）。

### 20.2 已知技术债（不在本轮范围，仅登记）
1. **现有 66 节点内已有 4 处重名**：`L_空特效`、`L_空特效_1`、`L_空特效_1_1`、`H_鬼火_射线_02` —— **各 ×2，全部是 `fx_skin_2003_029_hit.sfx` 与 `fx_skin_2003_029_jisha.sfx` 各一份**（**task-61 之前即存在**，非 dg 引入、非本轮引入）。
   ⇒ 因此"全局 name 唯一"不能作为验收断言；**(b) 的断言改为「dg 不得引入新重名」**：合并前 4 处 → 合并后 4 处、**dg 新增 0**（dg 的 3 个同名 Dummy 已改名 `L_空特效__dg` / `L_空特效_1_1__dg` / `L_空特效_2__dg`）。
   ⇒ **若后续要按 `parent` 构建层级树，必须先对 hit/jisha 做命名空间隔离**（现有 `parent` 值如 `L_空特效_1_1 → L_空特效_1` 在两个文件里各有一套，按名解析会串）。
2. 现有 66 节点的 `parent` 中 **14 行为 `None`**；dg 侧 **`parent` 全为 `None`**（dg 源全文 `Parent` 类文字 **0 次命中**，排除 `TransparentMode`）⇒ 如实，非漏解析。

### 20.3 (b) 就绪状态（真实写盘未执行）
- 合并脚本 `_target_1110171\\FX029_dg_merge.py` 已就绪（`--dry-run` 只解析+断言、不写文件）。
- 干跑：**A1 66→89 ✓** ｜ **A2 分布 21 / 45 / 23 ✓** ｜ **A2b dg 新增重名 0 ✓** ｜ **A3 类分布 A25/B7/C10 ✓** ｜ **A6 `models_enabled` 缺省（默认关）✓** ｜ **A4 42 个 `model_glb`：26 在盘 / 16 个 dg 缺失 ⇒ 待 env-auditor 导出**（`1110177/sfx/dg/` 尚未创建）。
- **`effects.json` 未改动**，仍为 **`399223E5F0B15813`**（不存在半成品）。放行条件：A4 的 16 个缺失项消失。
- 默认关帧基线 **`61A8171DAE53D73A`** 必须在内联后由 (c) 复核（合并本身不影响默认关路径：dg 行 `renderable_by_adapter=False`、无 `models_enabled`）。
'''
old = io.open(REP, 'r', encoding='utf-8').read()
if u'§20 task-62' not in old:
    io.open(REP, 'a', encoding='utf-8').write(sec)
    print('已追加 §20')
print('报告 sha16 =', hashlib.sha256(open(REP, 'rb').read()).hexdigest()[:16].upper(), os.path.getsize(REP), 'B')
print('merge 脚本 sha16 =', hashlib.sha256(open(r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_dg_merge.py', 'rb').read()).hexdigest()[:16].upper())
