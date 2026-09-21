# 03_1dpw — 单条真实 PC WPK 复验包

入口：`verify_1dpw_entry.py`

```bat
py -3 E:\mrzh_audit\run_004_PC_BinDict与1DPW专项_001\03_1dpw\verify_1dpw_entry.py
```

成功标准不是命中可打印 magic，而是同时通过：IDX/1DPW 字段与 4 KiB 边界、AC stage-1、完整 DTSZ Zstandard frame（EOF 且无 unused data）、DDS 手工头、Pillow verify/load、输出回读 SHA，以及五项负对照。

事实源只读 `E:/mrzh`；派生文件只在本目录。FPK 是另一层，本包不读取 FPK，也不把 FPK 称为 1DPW。

优先查看：
1. `verification_report.md`
2. `verification_report.json`
3. `artifact_manifest.csv`
4. `artifacts/*_final.dds` 与 `artifacts/*_preview.png`
5. `RUN_HASHES.sha256`
