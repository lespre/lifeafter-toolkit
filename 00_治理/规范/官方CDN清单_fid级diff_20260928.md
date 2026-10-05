# ★ 官方 CDN 清单入口打通 —— fid 级热更 diff 成立

日期：2026-09-28 ｜ 状态：**入口 ✅ · 格式 ✅ · fid 级 diff ✅ 首次跑通**

---

## 一、入口（可复现）

```
清单入口（给版本号 + CDN 目录名）：
  https://g66.update.netease.com/pl/npk_version_newpc4[_<入口>]
  <入口> ∈ { (空)=release, _playertest, _futuretest, _bisai, _kol_zy }

★ 清单里【没有直接给 CDN 目录】的地方 —— 要从 pkg_lst.name / pkg_N.pi.name 取：
    "20260917_015403_release_newpc/pkg_1.pi"
    ⇒ 目录 = 20260917_015403_release_newpc
    ⇒ 规律 = <时间戳>_<cloud_dir_name>

包体基址：
  https://g66.gph.netease.com/<目录>/<文件名>

实测 200：
  .../20260917_015403_release_newpc/pkg_lst.pl     59 B
  .../20260917_015403_release_newpc/pkg_1.pi       3,535,840 B
  .../20260917_015403_release_newpc/pkg_17.pi      8 B
✗ 资源包本体（res/ui_04.layers.1.1.npk 等）在该目录下 404 —— 该目录只放客户端程序与索引
✗ res.npk.txt / res.npk.map / res.skip.txt 在明日之后【不存在】（那是第五人格的）
```

## 二、清单里的关键字段（此前没人挖过）

```
version              = "20260915_220933_release_newpc"
cloud_dir_name       = "release_newpc"
bc7_only             = true          ← ★ 全量 BC7（印证 2048² 那批是 DX10/BC7）
use_overlay          = true          ← ★ 覆盖层机制开着
★ script.py314.lc.overlay3.<时间戳>.npk  19,491,884 B   ← ★ overlay 层的实例
★ zstd_dict          = {30: shader_cache_20260730.dct}  ← ZSTD 字典
★ neox_index_mapped  = 50
★ low_quality_saved_size_by_layer = {"1_1":0,"1_257":0,"256_257":0,...}  ← 「layer」口径
   ★ 键形如 <a>_<b>，与 <.layers.<起>.<止>.npk> 的命名同源
revision             = 5704733
svn_branch           = "2026_09_17_release"
pkg_lst              = {name: ".../pkg_lst.pl", size: 59}
pkg_1.pi ~ pkg_17.pi = {name: ".../pkg_N.pi", size: ...}
inc_files            = {}            ← 空（本次）
```

## 三、★★★ `pkg_N.pi` 的格式（逆向出来了）

```
[0:4]   uint32  条目数 n
[4:8]   uint32  保留（=0）
[8:]    n × 8 字节  64 位大端？—— 实测 <Q 小端读出后 100% 唯一、值域巨大
                   ⇒ 语义 = 【64 位文件哈希】，与我们索引里的 fid 同一个空间

判据（全部机械可核）：
  · 441,979 × 8 + 8 = 3,535,840 = 文件大小 ✓ 完全整除
  · 100% 唯一值
  · 拿本地 2,300,843 个 fid 去撞 → 命中 404,112 (17.564%)
  · 熵 8.00/8.00 —— 不是加密，是哈希表本来的高熵（★ 别误判成加密）
```

## 四、★★★★ fid 级热更 diff（首次跑通）

```
两版本目录：
  release    version 20260915_220933_release_newpc → 目录 20260917_015403_release_newpc
  playertest version 20260923_164313_playertest_newpc → 目录 20260924_121205_playertest_newpc

pkg_1.pi 相减：
  release    441,979 条
  playertest 450,110 条
  ★ 新增 fid  11,222 个
  ★ 移除 fid   3,091 个
    共有      438,888 个

★★★ 新增的 11,222 个 fid，去本地索引查 → 100% 命中，且分布：
    Documents\gres\0000.gpk   11,168   ← 增量包就是落点
    res\effect_01.gpk             36
    res\utility.gpk               18
```

**⇒ 这一条把「热更定位」从「容器级」推进到了「fid 级」——之前认为做不到的。**

## 五、闭环验证（幻夜神谕）· ★ 全 17 包合并后

```
gres\0000.gpk 54,292 行的构成：
  在 release 清单里    30,867
  在 playertest 清单里 54,189  (99.8%)   ← ★ 铁证：它就是热更增量包
  两边都不在              103

★ 关注项（全 17 包合并）—— 全部确认：
  huanyeshenyu_female.atlas  (7781361D9C2DFFBD)  ★ 新增 ✓
  huanye_bg.atlas            (B940B2491EB0EF0D)  ★ 新增 ✓
  幻夜神谕立绘A r7776 (7273DC844F76A954)         ★ 新增 ✓
  幻夜神谕立绘B r7783 (C929D20D7278BD8A)         ★ 新增 ✓
  幻夜神谕光效  r7784 (C23BBC156DD64032)         ★ 新增 ✓

★ 教训：只看 pkg_1 时，立绘「不在差异里」⇒ 差点误判成没更新。
  全 17 包合并后全部为「新增」。★ 再次印证：绝不能由「没找到」反推结论。
```

## 五之二、★★★★ 官方清单给了「名字天花板」的权威分母

```
官方 playertest 清单 = 2,298,533 个 fid
  ★ 其中本地字典有名字:   919,418  (40.00%)
    官方有、名字没有   : 1,379,115  (60.00%)
```

**⚠ 以下这段结论已被 2026-09-28 晚些时候的实测更正（见 `pkg有序布局表与16万缺口_20260928.md`）：**

> ~~本地索引 2,300,843 行 ≈ 官方 2,298,533（差 2,310）
> ⇒ ★★★ 本地【是完整的】。名字缺失不是「本地不全」，是「名字本身不在客户端里」。~~

**⇒ 这句下早了。** 那是**总数**接近，不是**集合**一致：
```
官方去重             2,298,533
本地唯一 fid         2,272,237   （entries 2,300,843 行，重复 28,606）
交集                 2,138,879
★ 官方有、本地无   159,654
★ 本地有、官方无   133,358
校验 2,138,879 + 133,358 = 2,272,237 ✓ 数字自洽
```

**「60% 的名字不存在」这个结论本身仍成立**（分母是官方的 2,298,533，本地字典只覆盖 919,418），
但「本地是完整的」这句不成立 —— 两边各有十几万独有项，原因未查清。

```
本地字典 1,058,427 条：
  官方清单里【有】 919,418 (86.87%)
  官方清单里【没有】139,009  ← ★ 待查：这 13.9 万个名字哪来的（推断还是官方清单不含某些包）
```

## 六、这条路的价值

```
① H-3 包级归因：官方清单直接给「哪个 fid 属于哪个官方包」→ 不用再用前缀猜（前缀匹配 175/210 那套可退役）
② H-1 版本对比：从「包哈希变了」升级到「fid 级新增/移除清单」
③ 本地完整性：官方清单 vs 本地索引 → 能算「本地缺了什么」
④ ★ 成本极低：17 × 3.5 MB ≈ 60 MB/版本，不用下 42 GB 的大包
```

## 七、下一步

```
① 下齐 pkg_1~pkg_17 两版本（进行中）→ 重做 diff   ✅ 已完成
② 用全量差异回答「立绘 r7776/r7783 属于哪个官方包 + 是不是本次新增」  ✅ 已完成
③ 把 `pkg_N.pi` 解析接进 CLI（`delta` 加 `pkg` 子命令）  ✅ 已完成（见 §九）
④ 用官方清单给 H-3 包级归因换权威数据源  ⏳ 待做
```

## 九、★ 已接进 CLI（2026-09-28）

```
toolkit_core/patch_pkg.py                 新模块（CDN pkg_N.pi 全能力）
CLI: delta pkg fetch                      下载 pkg_1..17.pi（≈18 MB/版本）
     delta pkg info                       看 CDN 目录名 / 版本 / 包顺序 / bc7_only / use_overlay
     delta pkg diff --a DIR --b DIR       两个已下载版本做 fid 级 diff
CLI: loose scan --out DIR                 解密散文件层全部家族（.idx + *.wpk）
     loose match --dir DIR                内容 MD5 撞本地索引 → 容器+行号（不靠名字）
```

实测：`delta pkg info` ✓ · `delta pkg diff` ✓（新增 23,322 / 移除 3,879）·
`loose scan` 57/57 ✓ · 治理边界 rc=2 ✓ · pytest 105 passed ✓ · help 逐字节相同 ✓

### 附带修掉一个真局限（不是 bug）

`wpk_1dpw_decryptor.batch_decrypt_wpk` 原先**写死单一家族**：

```python
entries = parse_idx(res_dir / 'ui.idx')      # ← 只看 ui
wpk_path = res_dir / f'ui{pkg}.wpk'          # ← 只找 uiN.wpk
```

对 ui 家族完全正确，但 `E:\mrzh\Documents\res` 下实际有 **8 个家族**：

```
ui 19 · effect 18 · building 7 · character 5 · weapon 4
model_high_2024 2 · model 1 · scene_bw 1       合计 57 条（原来只处理 19 条）
```

通用化后（扫全部 `*.idx`，wpk = `<stem><pkg>.wpk`，产物名带家族前缀防撞名）：
**57/57 全解，失败 0。** 签名与返回不变，向后兼容。

## 十、★ 资源调度（CPU/GPU）现状与本次接入

### 已有的那套（不是新写，是接上）

```
toolkit_core/throttle.py  ── LoadPolicy + LoadGate
  真读负载：CPU 走 psutil · GPU 走 nvidia-smi（拿不到如实返回 None）
  算预算  ：worker 数 = 核数 × cpu_limit%
  反馈限流：跑动中采样，超上限就 sleep 让路（duty cycle）

★ 模块 docstring 记着历史实情：scheduler.py 的 SmartScheduler 只【生成计划】；
  GUI 那个「上限：CPU/GPU 约 80%」标签从来没接上执行器 —— 是个标签。
  CLI 更是完全没这个概念（全量体检单线程跑，32 核只用了 1 核）。
  throttle.py 就是补执行侧的那块。
```

### 本次接入前后

```
接入前（只有 2 个命令）：
  bulk          --cpu-limit / --gpu-limit
  decode-audit  --cpu-limit / --gpu-limit

本次新增：
  loose match   --workers / --cpu-limit / --gpu-limit
    ★ 理由：算 15.5 万个文件的 MD5 是典型 CPU 密集活
    实测：单线程跑 6 分钟没完 → 接调度后 32 核 × 80% = 并行 25，全量 1 分 6 秒
    命令输出会打印 [调度] 行；报告里带 policy + workers + throttle.summary()
```

### ★★ GPU 描述的更正（原描述过时）

原 docstring 写「venv 里没有 torch/cupy 等，所以解码线不碰 GPU」——**这句已过时**：

```
核实（2026-09-28）：
  torch   2.11.0+cu128  ✓  torch.cuda.is_available()=True · RTX 5080 · sm_120
  cupy    ✗ 确实没装（这句原来是对的）
  numpy   2.5.3 · PIL 12.3.0
  nvidia-smi 可读 ✓（gpu_percent 就靠它）
  ★ 全库【没有任何】import torch / 用 cuda 的代码
```

**⇒ 更正后的准确说法：**
```
解码线【在行为上】仍不碰 GPU —— 但理由不是「没有库」，而是「没有代码去用它」。
解压/解密/解码/识别这条路是 numpy + PIL 写的，跑不到 GPU 上。

gpu_applicable() 的判据本来就是 kinds ∈ {render, screenshot, glb_gpu}，
设计上已预留渲染/截图的 GPU 位；只是目前没有任何命令用 kinds=("render",)。

★ 未利用的机会：torch+CUDA 已就位。若把渲染 / 批量图像处理
  （如 alpha 内外差这类整型数组统计）挪到 GPU，那条分支才有真实场景，
  gpu_limit 也才有实际约束力。
```

`LoadPolicy.snapshot()` 新增 `torch_present` 字段（用 `importlib.util.find_spec`，
不真 import —— import torch 太慢），让报告诚实反映「有 GPU 能力 ≠ 在用 GPU」。

### 顺手修掉一个我自己引入的 bug

`loose match` 初版写了 `pol.as_dict()`，但 `LoadPolicy` 只有 `workers / gpu_applicable /
snapshot`（`as_dict` 是别的类的方法，看错类了）⇒ 改 `pol.snapshot()`。



## 八、脚本与产物

```
scratch/dl_all_pkg.sh              下载 17 包 × 2 版本
scratch/try_pi.py                  试解 pkg_N.pi（证明不是加密）
scratch/judge_pi.py                判定 8 字节语义 + 撞本地 fid
scratch/diff_pkg1.py               首个 fid 级 diff
scratch/verify_huanye.py           幻夜神谕闭环验证
03_执行/30_分析/官方清单_20260928/pkg1_release_vs_playertest.json
03_执行/30_分析/官方清单_20260928/终验_幻夜神谕_vs_官方差异.json
```
