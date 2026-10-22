# PC WPK 真实 1DPW 条目独立复验报告

**结论：PASS — 当前哈希锁定真实 WPK 条目的 1DPW/WPD1 AC 层已被事实性解开**

对当前 ui.idx SHA-256 锁定快照中的零基记录 5，已从 ui4.wpk 精确读取 0x30+275 字节，恢复 AC stage-1 的 DTSZ/Zstandard 数据，并严格解出可由 Pillow verify+load 的 240×184 DDS。正确链通过且五项负对照全部失败，因此这不是只切出 1DPW 外壳或偶然 magic 命中；该真实 AC/DTSZ 实例的 1DPW 层事实上已破解。

## 范围与证据边界

- 只读事实源：`E:/mrzh`。
- 固定复验 1 条当前 UI IDX 记录，不作 4811 条全量解码覆盖声明。
- 本条链路为 `IDX → ui4.wpk → 1DPW → AC → DTSZ → Zstandard → DDS → Pillow`。
- 未启动客户端，未修改任何原始文件。
- **FPK 是另一容器层；本次未读取 FPK，绝不作“FPK=1DPW”表述。**
- 本样本不覆盖 3 条 PC tag，也不覆盖 ENON 分支；只证明当前哈希锁定 AC/DTSZ 实例及其 1DPW 层已被真实解开。

## 源锁

| 路径 | 大小 | SHA-256 | 哈希期间稳定 |
|---|---:|---|---|
| `E:\mrzh\Documents\res\ui.idx` | 173232 | `cbba19c9a56e68fc0f68c6a431411aa97c329b4c8da5618eb16da765e6a8341f` | True |
| `E:\mrzh\Documents\res\ui4.wpk` | 2097152 | `4bd07c4f0dd8d9d9503c43eb809614e308bb4d04ccbda0e5ac5e5e5421bc07c3` | True |

## IDX 与物理边界

- IDX：头 `0x20`，记录 `0x24`，声明/按长度推导均为 **4811** 条，尾部 4 字节。
- 目标：零基序号 **5**，IDX 记录偏移 `0xD4`，hash `77f55b584213beb7a0f0c0410b56ec86`。
- 来源：`E:\mrzh\Documents\res\ui4.wpk`，pkg raw `0x00000004` / low8 `4`。
- WPK 偏移 `0x001DC000`；头长 `48`；payload `275`；总读取 `323`。
- `header_field=0x0EBD0030`：low16=`0x0030`，high16 padding=3773。
- 精确条目结束 `0x001DC143`；补零后 `0x001DD000`；下一条 `0x001DD000` 且 magic=`1DPW`。
- padding 全零：True；padding SHA-256 `d2e83c604222ccf15234b3d43115d2a7e8a7669279cba79d0487a60122e357c1`。

## 完整解码链

| 层 | 大小 | 头部 | SHA-256 |
|---|---:|---|---|
| 1DPW outer entry | 323 | `314450570200000077f55b584213beb7` | `216c6672a0caa839ab8d68e4f44b978e627356c1eee9c0287e21ef01a1234e19` |
| WPD1 payload | 275 | `414301009b58ef31c3c3d9c1f2d6719d` | `0d34e780b14cdb2942c28d0472137d84ca7012b21baf317ca88e0803b6ebac76` |
| stage-1 decoded | 267 | `4454535a28b52ffd6014aced0700420b` | `0e322cd8f92f73ced698fc721b700b871905ce2f1feab9b4c60472e28fcd7612` |
| final resource | 44308 | `444453207c00000007100800b8000000` | `b6daa6d78217f494c69aab68039b37f7e519d9ff10512f901d2623c71fcd5a28` |
| derived preview | 634 | `89504e470d0a1a0a0000000d49484452` | `aa585f272df63c9c5e56a544af62986a7ab3af9fad6b5ba32479554c80572d5a` |

- WPD1：tag `AC` / `0x4341`，p=1，t=0。
- body_len=267，AES 前缀=128 字节，key=`0e0b01006a6b2e7c3036382f6e65745c`。
- stage-1 首部恢复为 `DTSZ 28 B5 2F FD`；Zstd eof=True，unused=0，frame content size=44308。
- 最终 DDS：240×184，mode=RGBA；Pillow verify=True / load=True。
- 像素验收：18 种 RGBA，非透明 43480/44160，非黑 RGB 808；不是纯空白=True。

## 负对照

| 对照 | 输出头 | 命中完整 pipeline | 对照通过 |
|---|---|---|---|
| `payload_size_misread_as_total_minus_0x30` | `ac2de3b9aa25a34aef25ad2e4f93eb0b` | False | True |
| `kdf_body_len_minus_1` | `7c968cdabf73ce80be8bf3788f0cf285` | False | True |
| `zero_aes_key` | `118aad79bf2a9b17d899d63be05e7cb3` | False | True |
| `skip_ac_reverse_xor_5a` | `c3792a4f8ad67bca0d8a0a7fd1bff09c` | False | True |
| `entry_offset_plus_1` | `44505702` | False | True |

关键负对照包括：把 IDX `payload_size` 错当总长（少读 0x30）、错误 KDF body length、零 AES key、跳过 AC 64 字节头变换、条目偏移 +1。它们均未通过 wrapper→codec→Pillow 完整验收。

## 现有工具审计

- 工具 SHA-256：`6cd2375d2f937c310cbc6cc109a813bf46e081e0e56bbf59af8176dc085a5584`。
- 结论：not reused for WPD1/AC: this snapshot only slices/strips 1DPW and has no AC/PC stage-1 or DTSZ/ENON decoder。
- 因此未把该脚本的“切出 1DPW”冒充解密成功；专项验证器内置并逐层验收 WPD1 算法。

## 验收检查

- PASS — `source_sha_locks_match`
- PASS — `source_stable_end_to_end`
- PASS — `idx_magic_layout_count_and_trailer`
- PASS — `all_idx_wpk_and_slot_sources_resolved`
- PASS — `target_idx_hash_and_pkg_match`
- PASS — `wpk_and_embedded_magics_match`
- PASS — `payload_size_excludes_0x30_header`
- PASS — `idx_and_embedded_1dpw_fields_match`
- PASS — `entry_padding_and_next_boundary_match`
- PASS — `wpd1_ac_stage1_restores_dtsz`
- PASS — `zstd_strict_eof_no_unused_and_size_match`
- PASS — `final_dds_manual_header_and_pillow_parse`
- PASS — `final_dds_not_pure_blank_by_pixel_stats`
- PASS — `preview_pixels_match_final_dds`
- PASS — `all_negative_controls_rejected`
- PASS — `all_artifacts_read_back_with_hashes`

## 复跑

```bat
py -3 E:\提取成果\明日拆包\03_WPK_1DPW\verify_1dpw_entry.py
```

源 SHA 不同会硬失败，不会静默套用旧 offset。
