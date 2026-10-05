# 04_热更定位 —— 带 H 的家

日期：2026-09-28 ｜ 段位定义见 `04_站点/web/tools/gen_home.py` 的 `BAND_UP`
（`H-1 版本清单对比 · H-2 本地冻结与终态 · H-3 包级归因`）与
`00_治理/规范/结构调整设计_三线三带_20260928.md`。

带 H 是**三条线的入口带**：先知道「哪里变了」，才知道去哪找。所以它的产物是
**「去哪里找」的导航**，不是行级事实、也不是能看能听的东西 —— 这是它算「带」不算「线」的理由。

---

## 一、这个目录放什么

| 放什么 | 例子 |
|---|---|
| 带 H 的**入口说明与取舍记录** | 本文件 |
| 带 H 的**产物索引** | 见第三节（产物不落在这个目录，落 `03_执行/10_索引/`） |
| 后续新增的 H 专属脚本（**仅当**它不是可复用库、也不该进 `00_共享核心` 时） | 目前无 |

**不放**：命令定义（唯一处在 `00_共享核心/命令行/toolkit_cli.py`）、
H-1/H-2 的实现模块（见第二节的理由）。

```
00_共享核心/toolkit_core/patch_delta.py      H-1 实现（服务端版本清单对比）
00_共享核心/toolkit_core/patch_snapshot.py   H-2 实现（本地容器快照 + 写入窗口守卫）
00_共享核心/toolkit_core/source_lock.py      H-2 的引擎（内容寻址快照 + 前后比对）
00_共享核心/测试/test_patch_delta.py         H-1 契约测试（15 条）
00_共享核心/测试/test_source_lock.py         H-2 引擎契约测试
```

## 二、为什么 H-1/H-2 的模块**没有**搬进本目录（取舍记录）

用户口径给了两条路：**(a)** 搬过来 + 改引用；**(b)** 留在 `toolkit_core`，在本目录放
README + H 专属可跑脚本，并在「工具 × 段位」映射表里标明归属。**本次选 (b)**，理由三条：

1. **依赖方向会倒置。** `patch_snapshot.py` 的核心依赖是 `toolkit_core/source_lock.py`
   （内容寻址快照引擎 + snapshot schema）。搬出包外，它就得做相对导入手术
   （`from . import source_lock` → `from toolkit_core import source_lock` + 自举 `sys.path`），
   **引擎留在共享核心、表面搬到带目录** ⇒ 责任被劈成两半，日后改 schema 要在两处找。
2. **引用面虽然不大，但都是承重面。** 现役引用只有 3 处代码
   （`toolkit_cli.py` · `04_站点/web/tools/refresh_sidecars.py` · `测试/test_patch_delta.py`），
   但其中两处是「命令定义唯一处」与「契约测试」—— 搬动它们等于同时动 CLI 与测试基线，
   收益是「目录看起来更整齐」，风险是「三条线共用内核被拆散」。
3. **项目已有明文结论。** `00_治理/规范/CLI与EXE统一方案.md` §六：
   > ✗ 不重组 `01_工具/工具库` 的目录 —— 功能域与工作流阶段是正交两根轴；
   > 06_皮肤定位链 54 个脚本横跨 6 个段，硬塞反而更难找。

   本次「工具 × 段位」映射表的实测支持这句话：**现役 363 个工具里，目录所表达的线与
   产物所属段不一致的有 35 个**（`run_all.py map --json` 里的 `dir_mismatch`）。
   带 H 只是其中最典型的一例：它的两个模块住在「共享核心」这个功能域里。

> 结论：带 H 的「家」= 本目录（**入口 + 说明 + 段位归属**）；
> 带 H 的「引擎」= `00_共享核心/toolkit_core/`（与 `source_lock` 同包，依赖方向不倒置）。
> 这不是妥协，是**表面与引擎分离**的常规做法，代价是目录不整齐，收益是不动承重面。

## 三、三段边界（防以后又糊在一起）

| 段 | 输入 | 产出 | 明确不做 |
|---|---|---|---|
| **H-1** 版本清单对比 | 服务端版本清单（CDN，只读） | 包级增量（新增/变更/删除） | 不读本地客户端目录 |
| **H-2** 本地冻结与终态 | 本地容器 mtime/尺寸（只读） | 冻结快照 + 前后 sha + 终态记录 | 不对比包内内容 |
| **H-3** 包级归因 | H-1 + H-2 | 「新内容归到哪一族」 | 不承诺「包里哪张图」——那要包内名字，哈希不可逆 |

## 四、命令入口与产物

```bash
# ── H-1 版本清单对比（只读 CDN，不碰本地）──
python 01_工具/run_all.py delta fetch           # 拉 5 个入口清单到本地缓存
python 01_工具/run_all.py delta diff            # release vs playertest：新增/变更/删除包
python 01_工具/run_all.py delta families        # 按族聚合（H-3 当前由它承担）
#   缓存：03_执行/10_索引/patch_manifests/<entry>.json

# ── H-2 本地冻结与终态（只读 E:\mrzh）──
python 01_工具/run_all.py snapshot scan                    # 全量（68 GB，首次约几十分钟，见下）
python 01_工具/run_all.py snapshot scan --only bin/x64-a50  # 小规模实测（几秒）
python 01_工具/run_all.py snapshot scan --suffix .npk       # 只算某类后缀
python 01_工具/run_all.py snapshot diff                    # 最近两次快照按内容比
#   产物：03_执行/10_索引/patch_snapshots/<时间戳>/
#         source_lock.json（内容寻址快照）· patch_delta.json（与基线比）· CURRENT_STATE.json
```

**H-2 的三条规矩**（`patch_snapshot.py` 里实现，这里只复述，便于复核）：

1. **两段式快扫**：先廉价 stat 扫全部容器，只对「新增 / size 或 mtime 变了」的候选算 sha256；
   其余沿用基线哈希 ⇒ 日常只重算少量文件。
2. **mtime ≠ 内容**：sha 相同、mtime 变 ⇒ 记为 `mtime_only_changed`，**永不作为更新证据**。
3. **写入窗口守卫**（实测踩过：5 个 `.idx`/`.wpk` 的扫描值与复核值不同）：算 sha256 前后各读一次
   `(size, mtime_ns)`，不一致就重试，仍不稳则标 `unstable` 并**排除出内容结论**。

**治理边界（硬约束）**：`snapshot` 只允许扫 `E:\mrzh`（体验服）。正式服安装目录 `E:\LifeAfter`
与其它路径一律拒绝（`toolkit_cli._snapshot_guard()`，退出码 2）。默认根就是 `E:\mrzh`。

**全量耗时**：实测见 `00_治理/规范/工具层与CLI整理_20260928.md` 第三节（含小规模实测吞吐
与 68 GB 外推）。首次无基线 ⇒ 全量算哈希；之后每次只重算变动项。

## 五、待补（H-3 与判据）

- **H-3 家族词表**：`delta families` 现在用「包名前缀」当家族（`<家族>.layers.<起>.<止>.npk`）。
  词表与 `<起>/<止>` 区间语义还没有单独维护的地方 —— 补在哪要单独裁决（台账 or 本目录）。
- **H-2 判据**：`04_站点/web/tools/checks.py` 里 H-1 有 `@delta_entry` 判据，H-2/H-3 还没有
  对应判据落进台账（台账 `## 带H 热更定位带` 段当前只登记了 H-1）。
- **H-2 与索引的联动**：快照变了 ⇒ 索引该重建的提示，目前靠人看 `CURRENT_STATE.json`，
  没有自动联动（`refresh_sidecars.py` 只刷 sidecar）。
