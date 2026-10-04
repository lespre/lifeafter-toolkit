# 带 H · H-1 版本清单对比（delta）· 工具说明

建立：2026-09-28 ｜ 状态：**已落地、已实测、已带契约测试**
归属：**带 H · H-1 版本清单对比**（原写「解码链 ①-5 段」；2026-09-28 结构调整后热更增量升为「带 H」，
      文件名保留 `①-5_…` 以免断引用）｜ 模块 `toolkit_core/patch_delta.py` ｜ CLI `run_all.py delta`
      带 H 的家：`01_工具/工具库/04_热更定位/README.md`（H-2/H-3 同页）

---

## 一、它回答什么问题

```
这次热更更新了哪些包？  ⇒  新内容放到了哪一族？
```

用户原话：「你不是说能搞到每次更新的文件表吗，那你直接看上次热更更新了哪些文件，
就可以推知新内容放到哪去了啊」—— 这个工具就是把这句话做成可重跑的一环。

---

## 二、边界（很重要，别越界）

```
✅ 只拉【服务端版本清单】（CDN）         https://g66.update.netease.com/pl/npk_version_newpc4[_后缀]
✅ 只读【项目内缓存】                   03_执行/10_索引/patch_manifests/
❌ 绝不读本地客户端目录 —— 尤其禁止 E:\LifeAfter（正式服）
```

**★ 本次顺手修掉一处越界**：`04_站点/web/tools/parse_file_hash_pack.py` 原先无条件读
`E:\LifeAfter\Documents\file_hash_pack.bin`。已改为**默认只读测试服**，
要碰正式服必须显式 `--allow-live`（会打警告）。读它的文件同样越界，不只是「不拆」。

---

## 三、用法

```bash
PY="E:/la拆包项目/.venv/Scripts/python.exe"
CLI="01_工具/run_all.py"

# 拉清单到缓存（默认全部入口；可 --entry 指定）
"$PY" "$CLI" delta fetch
"$PY" "$CLI" delta fetch --entry playertest

# diff（默认 release 正式服 vs playertest 测试服）
"$PY" "$CLI" delta diff
"$PY" "$CLI" delta diff --pair release futuretest --limit 50 --out 报告.json

# 只看家族聚合（哪个族有新东西）
"$PY" "$CLI" delta families
```

参数：
```
--pair A B     对比哪两份清单（默认 release playertest）
--keys ext     ext=filesNN_2（以 .npk 包为主，默认）· main=filesNN（引擎+包）
--limit N      明细最多列几条（默认 30）
--cache DIR    缓存目录（默认 03_执行/10_索引/patch_manifests）
--out FILE     完整报告落盘
--json         报告 JSON：裸用打 stdout，给路径则落盘
```

---

## 四、★★ 核心修正：键名会漂移（第一版是个静默错）

```
实测 5 个入口的 file 表键名：
   release            files50 · files57 · files57_2
   playertest         files50 · files57 · files57_2
   playertest_bisai   files50 · files56 · files56_2     ← 56
   futuretest         files50 · files55 · files55_2     ← 55
   playertest_kol_zy  files50 · files55 · files55_2     ← 55

第一版 diff 硬编码 files57_2。release vs playertest 恰好都是 57 ⇒ 侥幸正确。
但 release vs futuretest 就会变成「一边 1745 条、一边 0 条」
⇒ 静默产出「全部新增」这种错结论。
```

**修法**：`_pick_file_keys()` 动态识别 —— 取 `files<NN>` 里 NN 最大的那个作 main，
配对的 `files<NN>_2` 作 ext。**取不到就明确抛错，绝不静默返回空 diff。**

**实测（跨键名，这才是验证点）：**
```
release(files57_2, 1745) vs futuretest(files55_2, 1694)         ✓
release(files57_2, 1745) vs playertest_bisai(files56_2, 1745)   ✓
```

**契约测试**：`00_共享核心/测试/test_patch_delta.py`（15 条）
```
1. 键名漂移下能挑对两组（55/56/57 参数化）
2. 跨不同键名 diff 能对上（核心用例）
3. 取不到文件表 → 明确抛错，不是静默空 diff
4. 家族归并正确
★ 写测试当场抓到我自己一个 bug：错误分支里 `for k, _ in (None, None)` 抛
  TypeError，把「输入不对」变成看不懂的崩溃 —— 已修。
```

---

## 五、实测结果（release 20260915 → playertest 20260923）

```
新增 19 个包（全是 .npk）：
   res/model_high_2024/pve05.layers.{1,256}.257.npk
   res/model_high_2024/pve_jiayuan01b.layers.{1,256}.257.npk
   res/scene_bw.layers.256.257.npk
   res/scene_bw/bigworld/bg{03,04,06,09,11,14,15,21,37}_content.layers.256.257.npk …
变更 722 个包（705 个 .npk + 17 个 bin/其它），按家族前几：
   bin/x64-3                    35
   res/character/players2021    28
   res/model/bigworld           18
   res/model/pve_city01         18
   res/ui                       8   ← ★ 含 huodong_icon / ziliaopian
```

**★ 命名规律（本工具的输出副产品，很有用）：`<家族>.layers.<层起>.<层止>.npk`**

**★ 拿到的 30 个 `res/ui/` 家族名**（一份现成词表）：
```
all_pc · all_txt_meishuzi_icon · bigmap · building_icon · chenghao · haiyang ·
huodong_icon · item_icon · main_zhujiemian_v3 · map_icon · mingpiankuang_icon ·
nielian_icon_v4 · quyuxingdong_v4 · quyuxingdong_v4_icon · renwu_icon · shangcheng ·
shengcunfu · shizhuang_icon ★ · spine · spine_new ★ · touxiang_cemian_icon ·
ugc · vx · xueguolieche · zhengbasai_xin · zhutihuodong_v4 · zhutihuodong_v5 ★ ·
zhutihuodong_v5_icon · ziliaopian
```

---

## 六、它到不了哪（诚实说）

```
两张更新表（服务端 manifest 的 filesNN_2 · 客户端 file_hash_pack.bin 的 FHPK TOC）
都是【包级】—— 告诉你「哪个包变了」，不告诉你「包里哪张图变了」。

要到资产级仍需【包内的名字】，而 GPK/NPK 索引表只存 murmur3 哈希、不可逆。
```

**所以本工具的正确定位**：不是「找出新图」，而是
① 缩小范围（哪个容器/哪一族有新东西）
② 给「位置-内容索引」提供家族词表
③ 变化监控（哪些包反复变更 ⇒ 那些就是总有新内容的包）

---

## 七、相关

- 实证分析：`00_治理/规范/热更增量溯源_实证结论_20260928.md`
- 路径还原边界：`00_治理/规范/路径还原充分性_实证分析_20260928.md`
- CLI 总图：`00_治理/规范/CLI与EXE统一方案.md` §七
