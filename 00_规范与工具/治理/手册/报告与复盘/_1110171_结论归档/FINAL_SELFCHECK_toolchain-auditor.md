# FINAL_SELFCHECK_toolchain-auditor

> 生成：toolchain-auditor · 2026-09-19 · 范围：**静态门最终复核**（本期最后一轮，未起浏览器）
> 脚本：`01拆包器本体\工具库\06_皮肤定位链\wiki_selfcheck.py` · **sha16 `5300f68d95350010`** · 58,097 B · 1,030 行
> 备份：`wiki_selfcheck.py.bak_20260918_2355_stampverify`
> 复现：`set PYTHONUTF8=1 && python -X utf8 wiki_selfcheck.py --no-browser`
> 原始日志：`03拆包产物\_target_1110171\FINAL_SELFCHECK_static.log` · 结构化报告：`SELFCHECK_v2_report.json`

## 1. 三档终态

| 项 | 值 |
|---|---|
| **PASS** | **14** |
| **WARN** | **29** |
| **FAIL** | **0** |
| 具名 mandatory gate | 全部通过 |
| **判定 / 退出码** | **PASS / exit 0** |

判据口径：**所有具名 mandatory gate 全过才 exit 0**（无"任意 FAIL 也能过"的写法）；`FAIL` 即 1。SwiftShader 已知假阳性只按明确三条件（skin + prim 白名单 + `--disable-gpu --enable-unsafe-swiftshader`）降级 WARN，**白名单当前为空**。

## 2. pin 复核（逐个实测 sha256[:16]）

### 2.1 manifest（8/8 MATCH）
| 皮肤 | 期望（Lead） | 实测 | 判定 |
|---|---|---|---|
|1110024|cb092a5aa09e1841|cb092a5aa09e1841|MATCH|
|1110129|46f6137ec63e257f|46f6137ec63e257f|MATCH|
|1110145|4a91b3a5c6764dc1|4a91b3a5c6764dc1|MATCH|
|1110146|0bc547f0f355e231|0bc547f0f355e231|MATCH|
|1110152|db93a645f5b391da|db93a645f5b391da|MATCH|
|1110165|f6c9e89d14cc37b4|f6c9e89d14cc37b4|MATCH|
|1110171|64a07d5df157ec16|64a07d5df157ec16|MATCH|
|1110177|a05c4f2c8ddfcf9a|a05c4f2c8ddfcf9a|MATCH|

### 2.2 其它写者 pin（6/6 MATCH）
| 文件 | 期望 | 实测 | 判定 |
|---|---|---|---|
|`assets/weapon_skin_viewer.js`|8B8E80213F5C0CA8|8B8E80213F5C0CA8|MATCH|
|`assets/weapon_skin_sfx_adapter.js`|544D3A4A1B2CC591|544D3A4A1B2CC591|MATCH|
|`board.html`|5008117AA03BB7A0|5008117AA03BB7A0|MATCH|
|`1110171/viewer.json`|62E7BDDC9CF6EC6D|62E7BDDC9CF6EC6D|MATCH|
|`1110177/viewer.json`|7575FAFAD33DD670|7575FAFAD33DD670|MATCH|
|`1110177/effects.json`|10CC9A938BE92A10|10CC9A938BE92A10|MATCH|

⇒ **0 处不符**。

## 3. 剩余 WARN 逐条归类（29 条，**无新增**）

| 类 | 条数 | 说明 | 归属 |
|---|---|---|---|
|A. `t_surfacemap` 结构化标记 `state=missing` | **12** | 源无该槽 ⇒ 保持 missing（Lead 裁决 ⑥-2） | 已裁维持 |
|B. 非必需槽结构化标记 `production_ok=False` | **17** | 非必需槽（`t_caustic_tex`/`t_reflection_tex`/`t_refraction_tex`/`DetailMap` 等） | 已裁维持 |
|**C. 其它（= 新增 WARN）** | **0** | 无 | ✓ |
|合计 | **29**（上轮同为 29） | | |

逐条原文见日志 `FINAL_SELFCHECK_static.log` 的 `WARN 明细` 段（含 skin/prim/slot/键名）。
**FAIL 段不存在** ⇒ 0 条。

## 4. 静态门覆盖面（本轮实际执行的具名门）

- `H1.http` / `H2.unbuilt_404`：本地静态资源 HTTP 可达 + 有意不建者按预期 404
- `E2.encoding`：BOM / UTF-8 解码无 U+FFFD / board.html 结构标签
- `R1.registry`：注册表与目标皮肤一致
- `M4.required_slot`：逐 prim 必需槽（weapon `Tex0/ParamMap/NormalMap`；crystal `NormalMap` + `t_basecolor` 三分支）· 文件存在 · **sha 按字段名选口径**（字节 / 解码 RGBA / DDS）· **戳（形状 A `backfill*`、形状 B `provenance*`）必须可验证** · `faces_glob` 原样展开 {0..5}
- `S4.sha_stale` / `S5.provenance` / `S6.ddsresolve`：记录陈旧清单、戳末步==磁盘、DDS 逐条解析
- `M4.family.unresolved`：未知 family / 结构化未达生产 / 非必需槽标记

**dds 逐条解析（9 个唯一，全部 `[weapon_root]`，值 0 mismatch）**：
`000410.dds` · `001632.dds` · `001633.dds` · `001634.dds` · `001636.dds` · `001638.dds` · `001639.dds` · `001641.dds` · `001643.dds`
（有序查找：皮肤目录 → `03拆包产物\weapon\<name>` → `03拆包产物` 全树 basename 索引；本轮未触发全树索引）

## 5. 待收敛项（本轮**未动结构**，按 Lead 要求单独列出）

1. **同一规则两份实现**：DDS 口径校验在 `check_entry_sha` 与 `_actual_for_field` 各存一份 ⇒ 改一份不生效（本期已踩一次）。建议合并为单一实现、另一处调用。
2. **路径字面量静默失效**：`DDS_ROOTS` 曾用 raw 字符串 ⇒ 字面 `\u62c6`，全树索引静默 0 文件且不报错。建议加"索引为空 ⇒ `ng()`"自检。
3. **负控样本必须真图**：合成样本用假 PNG 会让 `_sha_rgba` 抛 `OSError`。已改为 PIL 生成真 PNG；建议固化为规则。

## 6. 未解 / 待命（不在本轮范围）

- **`B8.bind` N=5 复现统计**与 **3 条 `__env_ibl__ ibl_pending`**（1110165 prim2 / 1110171 prim1 / 1110177 prim2）+ `B9.envmode` 收紧：**等 task-49（shader-auditor 收敛式重试）完工**、拿到新 `viewer.js` sha16 后，一次跑完整 headless 提交（三档 + B8 N=5 + ibl_pending 结果）。
- 浏览器段未跑 ⇒ `A3.applied`（`applied == expected_prims` + `failed/missing` 必空）、`V6.target`（`data-skin-id` 定位）、`F6.framestable`（N=5 帧稳定 + 重试计数）、`K9.kill`（`taskkill /T /F` + 端口复查）本**期未实测**，其门实现与负控（`--self-test` 17/17 PASS）已就位。

## 7. 收尾

- 本端口 9931/9932/9933/10021：**无监听** ✓；chrome 进程数 **0** ✓（本轮未起浏览器，无需清理）。
- 本轮**只改** `wiki_selfcheck.py` 及其备份；未碰 viewer.js / adapter / board.html / viewer.json / effects.json / manifest。
