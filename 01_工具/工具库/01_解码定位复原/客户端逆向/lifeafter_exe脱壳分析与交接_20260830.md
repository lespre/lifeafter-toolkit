# lifeafter.exe 壳分析与脱壳交接（2026-08-30）

> 一句话结论：**这是借用 UPX 节名布局的「自定义加密/混淆壳」，不是改魔数标准 UPX，`upx -d` 路线已确认走不通。**
> 静态离线脱壳需先逆自解密 loader（对抗性强）；**动态脱壳技术可行但要绕网易反调试并实跑游戏主进程，属专业逆向活，建议人工/专用模型用 x64dbg 做**。
> 更重要：本项目原本想从 exe 取的三样东西，经核实**都不依赖脱壳**（见第五节），故 exe 已**不是主线阻塞项**，本文档用于交接与备用。

---

## 一、目标文件（多版本，按时间）

| 路径 | 大小 | 修改时间 | 说明 |
|---|---|---|---|
| `E:\mrzh\Documents\bin\x64\lifeafter.exe` | 41,657,336 | **2026-08-29** | **当前最新，主攻对象**，构建号 `2025_09_release_260820_c5dec41b3` |
| `E:\mrzh\Documents\bin\x64-3\lifeafter.exe` | 41,716,736 | 2026-08-29 | 并列新版 |
| `E:\mrzh\bin\x64-a50\lifeafter.exe` | 41,615,352 | 2026-08-27 | 稍旧 |
| `E:\mrzh\bin\x64-2\lifeafter.exe` | 39,177,728 | 2026-04-26 | 旧版（早期"NotPackedException"结论来自这代，壳结构一致） |
| `E:\lifeafter\bin\x64\lifeafter.exe` | 39,076,352 | — | 正式服对照 |

## 二、壳特征证据链（脚本见同目录 `exe_*.py`，只读可复跑）

1. **PE 节表（13 节）**：`.text/.rdata/.data/.pdata/.idata/.tls ... .UPX0/.UPX1/.reloc/.rsrc`
   - 原始节 `.text/.rdata/.data ...` 的 **RawSize=RawPtr=0**（磁盘无数据，运行时由壳填回虚拟内存）；
   - 唯一有实体代码的是 **`.UPX1`**（RawPtr=0x600，RawSize≈41.3MB，熵 7.47，**入口点在其中 RVA 0xf298eba**）；`.UPX0` RawSize=0（解压目标空洞）。
2. **UPX 魔数被抹除**：全文件搜 `UPX!` = **0 处**（标准 UPX 有 3 处）；仅节表残留名字 `UPX0/UPX1`。
3. **入口代码是加密数据，非解压 stub**：入口 `68 6bc9221a / e8 ...` 之后 capstone 第 3 条就崩成 `sahf`，后续是周期性 `xx 3d` 高熵流；入口首条 call 跳到 0x14f6bf073，反汇编仍是 `push r14/jmp/je/jmp/ror/clc/stc...` 的**混淆控制流，不是 UPX 规整的 NRV 解压循环**。
4. **TLS 目录异常**：AddressOfCallBacks=0x14d385b55（超出正常 .rdata 范围，疑似运行时修复，自解密入口候选）。
5. **导入表被掏空**：只剩 52 个函数 / 38 个 DLL，全是 loader 级（KERNEL32/USER32/bcrypt/CRYPT32/WS2_32…），真实 IAT 运行时重建。
6. **明文字符串**：61,294 个 ASCII 串里，游戏自有符号（murmur/Resource/gpk/fpk/NeoX/WpkResource/AttributeHelper/BinDict/weapon/skin…）**0 命中**；明文仅为静态链接第三方库（**NVIDIA PhysX/Blast 修饰名**）、DigiCert 证书 URL、PE 版本资源（公司 NetEase、构建号）。⇒ 自有代码/字符串确在加密段内。
7. 整体熵 7.982；`.rsrc` 熵 7.973（资源也压了）。

> 结论：标准 UPX 的"改魔数后 upx -d"不适用——**解压 stub 本身被加密/混淆，且无 UPX! 头可供工具定位参数**。

## 三、反调试 / 保护组件（脱壳时需逐一处理）

导入 DLL 暴露的保护面：`CrashHunter_PC3.dll`（网易崩溃/反调试）、`NtUniSdkBase.dll`、`libenvsdk.dll`、`OrbitSDK.dll`（网易易盾/反外挂体系）。动态调试需先绕过这些的 IsDebuggerPresent/NtQueryInformationProcess/硬件断点/时序检测。

## 四、三条脱壳路线（按推荐度）

### 路线 ① 动态脱壳（最可行，推荐给专业逆向）
1. x64dbg + ScyllaHide（反反调试：屏蔽 IsDebuggerPresent、NtQuery、PEB.BeingDebugged、时序）；必要时先屏蔽上面 4 个保护 DLL 的加载或 hook 其检测点。
2. 载入 `Documents\bin\x64\lifeafter.exe`，**在 OEP 下断**：壳会自解密 .text/.rdata 并跳回原始 OEP（可对 `.UPX0`/`.text` 空洞区下**内存写入/执行断点**，或用"模块入口+栈回溯"找 jump to original OEP）。
3. OEP 处用 Scylla **dump + IAT 重建**（导入表运行时才完整，自动搜 IAT、修无效 thunk）。
4. 修复重定位/TLS，得到可静态分析（IDA/Ghidra）的明文 exe。
- 风险：需实跑游戏主进程（可能要资源完整、可能尝试联网/登录）；建议断网、副本环境、勿登主账号。

### 路线 ② 静态自写解压器（不跑程序，工作量大、不确定）
- 从唯一明文的最前置代码/TLS 回调入手，还原"谁解密了入口段"：先定位真正未加密的第 0 段 loader（TLS 回调或入口链最上游），逆出其解密算法（疑似自定义流/分组 + 可能 LZMA/NRV 二次解压）与密钥派生，再用 Python 离线还原 .UPX1 → .text/.rdata。
- 入口/首跳都已混淆，需要先去控制流混淆，对抗性强；**不建议在没有 IDA 的情况下硬啃**。

### 路线 ③ 旁证 / 降维（不脱壳也能拿部分）
- 游戏大量逻辑在 **Python 脚本包**（`script*.npk`，已能解，见 05_BinDict），引擎 C++ 底层才在 exe；多数业务问题（皮肤/奖池/时装/数值/资源路径）在脚本层已可答，无需脱壳。
- PhysX 等第三方符号明文，可用于判断引擎技术栈（NeoX + PhysX Blast + FMOD + CEF）。

## 五、为什么脱壳已不是本项目主线阻塞（重要）

原本想从 exe 取三样，现状：
1. **namehash 算法**：已用 8 步实验证明 GPK 的 c1/c2 是**内容指纹而非路径哈希**（见 `06_文件名还原/GPK文件名还原_最终结论与交接_20260830.md`），逆 namehash 对取名无意义 → **不需要 exe**。
2. **资源清单（路径→包/条目）**：属于**数据**，在 `ui.npk` / `script*.npk` 内（路线 A），静态解包即可 → **不需要 exe**。
3. **FPK raw 几何帧自研解压**：仅用于 OpenWorld/PVE **场景建筑**，用户已明确低价值、不拆 → 无收益。

⇒ 建议主线直接推进**路线 A（在 ui.npk 里找资源目录表）**；exe 脱壳作为并行/备用，按路线①交接给具备动态调试环境的一方。

## 六、复现方式
```
py exe_pe_recon.py      # PE 节区/熵/导入/壳签名
py exe_upx_probe.py     # UPX 魔数抹除核查
py exe_entry_probe.py   # 入口反汇编（需 capstone）
py exe_loader_probe.py  # 入口 call 目标/代码块分析
py exe_strings.py       # 明文字符串与关键词命中
```
均为只读分析，不修改、不运行目标 exe。
