# APK 拆包思路

> 权威原件：`02_资料/源包/apk_20261002/README_分析记录.md`
> 实测时间 2026-10-02。

---

## 0. 先搞清楚一件事：APK 是哪个服

```text
★ APK / 模拟器 = 【正式服（release）】
★ PC 客户端（如 E:\mrzh）= 可能是【体验服 / 测试服】
⇒ 两者的资源 / 名字 / fid 【可能不同】！
⇒ 凡涉名字/fid/资源的结论，必须【标服别】；两套不要混用
```

判断方法见 [CDN-AND-VERSION.md](CDN-AND-VERSION.md) §3。

---

## 1. 目标与边界

| 目标 | 能不能 |
|---|---|
| 拿到 APK 里的**资源**（纹理/模型/配置/脚本） | ✅ 能 |
| 读**引擎逻辑**（`.so` 反汇编） | ✅ 能读 |
| **提取/加载**引擎（复用它的渲染） | ❌ 不能（符号已剥 + 私有 ABI） |
| **修改客户端 / 动态注入** | ❌ 禁止（违反用户协议 + 反作弊红线） |
| **动态内存 dump / 调试器 attach** | ❌ 禁止（反作弊红线） |

> 只能**静态**读。想要"用游戏引擎渲染"⇒ 走 [复原算法](../README.md#核心概念两类条目) 的路。

---

## 2. APK 就是 ZIP —— 第一步永远是解压

```bash
unzip mrzh_release_netease_744.apk -d apk_out/
```

### 解出来看什么

```text
apk_out/
├── assets/                     ★ 资源与脚本
│   ├── script.py314.lc.npk     ★ 403 MB，与 PC 端【同名同格式】⇒ 数据侧一致
│   ├── res.npk / *.npk         其他资源包
│   └── ...
├── lib/
│   └── arm64-v8a/
│       └── libclient.so        ★ 83 MB，整个客户端引擎
├── res/                        Android 资源（图标/布局，与游戏资源无关）
├── classes*.dex                Java 层（SDK / launcher，不是引擎）
└── META-INF/                   签名
```

> **关键发现**：APK 里的 `assets/script.py314.lc.npk` 与 PC 端**同名同格式**
> ⇒ **数据侧的解析工具可以复用**（同一套 `toolkit_core`）。

---

## 3. 资源侧：直接复用 PC 工具链

```bash
# 把 APK 的 assets 当普通源包处理（格式一致）
toolkit_cli.py index build
toolkit_cli.py npk <apk_out/assets/script.py314.lc.npk>     # 只取头 + 条目表
toolkit_cli.py extract <容器> <行号> --out out/
toolkit_cli.py tex out/ --out png/
```

**格式速查**（与 PC 相同）：

| 扩展名 | 格式 |
|---|---|
| `.npk` | `NXPK` · AES-ECB 头/表 + 48 B 条目 |
| `.gpk` | `HPGF` · 16 B 头 + 块链 + 32 B/条 |
| `.fpk` | 32 B 头 + Zstd 帧流 |
| 热更/散文件 | `.idx`=`SKPW` · `.wpk`=`FKPW` · 载荷片=`1DPW` |

> ⚠️ **服别提醒**：APK 是**正式服** ⇒ 拿它解出来的东西**不要**和 PC 测试服的
> 名字/fid 混用。

---

## 4. 引擎侧：`libclient.so` 静态分析

### 4.1 实测记录（2026-10-02）

```text
① 节名混淆 = XOR 0xBB
   （shstrtab 解出来是 .text / .rodata / .dynsym / .PyRuntime / .text1 …）
② 大节熵 3.3 ~ 6.9 ⇒ 【未加密】，可静态分析 ✓
③ 内含嵌入式 CPython（.PyRuntime）+ NeoX 引擎
   （mangled 符号如 neox::filesystem::t_zstd_ctx）
④ .dynsym 2013 个符号，全是导入项 ⇒ 引擎自身符号【已剥】
⑤ 关键标识符（npk/nxs/marshal/cdata/bindict）不在字符串表
   ⇒ 需 IDA/Ghidra 交叉引用才找得到
```

### 4.2 第一步：还原节名（否则 IDA 里看不懂）

```text
节名字节串整体 XOR 0xBB ⇒ 得到可读节名
产物：libclient_arm64_deobf.so   ← 节名已还原，可直接喂 IDA / Ghidra
```

### 4.3 第二步：喂给反汇编器

```bash
# Ghidra headless（本项目踩过 ClassNotFoundException: LaunchSupport ⇒ 用 .bat）
analyzeHeadless.bat <proj_dir> <proj_name> -import libclient_arm64_deobf.so
```

```text
能拿到什么：
  · 反汇编 + 交叉引用
  · mangled 符号名（能认出 neox:: 命名空间下的类/方法）
拿不到什么：
  · 源码（符号已剥，只有导入项）
  · 可直接调用的 C 接口（引擎不导出）
```

### 4.4 第三步：定位关键逻辑

```text
思路：从【已知字符串 / 魔数 / 常量】反向找交叉引用
  例：找 npk 头魔数 NXPK ⇒ 找读它的函数 ⇒ 看到头部布局与 AES 调用点
      找 murmur3 常量 0x77777777 / 0x66666666 ⇒ 找到路径哈希算法
      找 marshal 标签分发 ⇒ 看到 NeoX 方言的 opcode 表
```

> 本项目已验证的几条：
> **路径 fid** = 双 seed murmur3（高 `0x77777777` / 低 `0x66666666`）·
> **GPU 哈希 fid** = `(murmur3_x86_32(raw,0x77777777)<<32) | murmur3_x86_32(raw,0x66666666)`

---

## 5. 与 PC 端的对照（什么时候该用哪个）

| 场景 | 用哪个 |
|---|---|
| 拿资源（纹理/模型/表） | 看你在哪个服玩 ⇒ **对应的客户端** |
| 读引擎算法（哈希/解码/渲染规则） | `.so`（APK）或 `.so`（PC，另有 x64 未混淆版）都行 |
| 追新内容 | PC 客户端 + [热更线](CDN-AND-VERSION.md) |
| 对比两服差异 | `toolkit_cli.py delta` |

---

## 6. 常见坑

| 现象 | 真因 | 解法 |
|---|---|---|
| IDA 里节名全是乱码 | 节名 XOR 0xBB 混淆 | 先还原节名 |
| 找不到关键字符串 | 标识符不在字符串表 | 从魔数/常量做交叉引用 |
| 想直接调引擎函数 | 符号已剥 + 不导出 | 做不到，只能读汇编复刻 |
| APK 解出来的 fid 对不上 PC | **两套服别不同** | 别混；结论标服别 |
| `assets/script.*.npk` 解不开 | 用错了层级（它是 NPK 不是 GPK） | 用 `parse_npk` / `npk` 命令 |

---

## 7. 合规红线（再强调一次）

```text
✗ 修改客户端文件
✗ 动态注入 / hook
✗ 动态内存 dump
✗ 调试器 attach（反作弊红线）
✗ 连接未授权服务器
✓ 静态读取（解压 / 解析 / 反汇编）—— 学习研究范围内
```

---

## 8. 复现清单

```bash
# ① 解压
unzip <apk> -d apk_out/

# ② 资源侧（复用 PC 工具链）
toolkit_cli.py npk apk_out/assets/script.py314.lc.npk
toolkit_cli.py index build && toolkit_cli.py extract <容器> <行号> --out out/

# ③ 引擎侧
#   还原节名（XOR 0xBB）→ libclient_arm64_deobf.so
#   喂 Ghidra 分析
```

**相关文件**：
`02_资料/源包/apk_20261002/{README_分析记录.md, libclient_arm64_deobf.so, mumu_5.0.679/}`
