# 03_1dpw — 单条真实 PC WPK 复验包

入口：`wpk_1dpw_verifier.py`（本目录内，2026-09-26 更正）

```bat

py -3 E:\la拆包项目\01_工具\工具库\03_WPK_1DPW\wpk_1dpw_verifier.py

```

> ★ 2026-09-26 更正：原 README 指向 `E:\mrzh_audit\run_004_PC_BinDict与1DPW专项_001\03_1dpw\verify_1dpw_entry.py`，

> 该目录已不存在（`run_004` 下只剩 `02_bindict`）。本目录自有可跑的

> `wpk_1dpw_verifier.py` / `wpk_1dpw_decryptor.py` / `batch_wpk_textures.py`，入口改指向它们。

成功标准不是命中可打印 magic，而是同时通过：IDX/1DPW 字段与 4 KiB 边界、AC stage-1、完整 DTSZ Zstandard frame（EOF 且无 unused data）、DDS 手工头、Pillow verify/load、输出回读 SHA，以及五项负对照。

事实源只读 `E:/mrzh`；派生文件只在本目录。FPK 是另一层，本包不读取 FPK，也不把 FPK 称为 1DPW。

优先查看：

1. `verification_report.md`

2. `verification_report.json`

3. `artifact_manifest.csv`

4. `artifacts/*_final.dds` 与 `artifacts/*_preview.png`

5. `RUN_HASHES.sha256`
