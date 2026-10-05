# CDN 与版本体系

> 全部结论都有实测证据（HTTP 响应 / logcat / 文件字节）。
> 权威原件：`00_治理/规范/服务器切换与CDN体系_20261002.md` ·
> `00_治理/规范/官方CDN清单_fid级diff_20260928.md`

---

## 一、CDN 全图

| host | 用途 | 证据 |
|---|---|---|
| `g66.update.netease.com` | **版本清单**（`/pl/<name>`） | HTTP 200 + logcat |
| `g66.gph.netease.com` | **补丁数据**（引擎 `PATCH_DATA_HOST`） | 引擎 `<ppg3d>` 配置 |
| `drpf-g66.proxima.nie.netease.com` | **API**（根路径返 `ok`，需参数） | 实测 200 `ok` |
| `dns.update.netease.com/hdserver` · `dns.update.easebar.com/hdserver` | HTTP DNS | `PatchConfig.py` |
| 分片缓存 | **HTTP 206 Range** + `Documents/orbit_cache/` + `plcoht_ag*` 索引 | logcat |

```bash
# 取版本清单（纯只读 ✓）
curl -s "https://g66.update.netease.com/pl/npk_version_newpc4_playertest" -o x.json
```

---

## 二、清单命名体系

```text
PC   ：npk_version_newpc4[_后缀]
手机 ：npk_version_android4[_后缀]

后缀 = 服型 / 构建线：
  （无）                       正式服 release
  _playertest                 玩家测试服     ★ 常用
  _futuretest                 未来测试服
  _playertest_kol_zy          KOL / 知乎测试
  _playertest_bisai           比赛测试
  _gray                       灰度
  _playertest_yk              已失效（2018 占位）
```

### 已实测可取（HTTP 200 ✓）

| 清单名 | version |
|---|---|
| `npk_version_newpc4` | `20260923_230458_release_newpc` |
| `npk_version_newpc4_playertest` | `20260923_164313_playertest_newpc` |
| `npk_version_newpc4_futuretest` | `20260807_101927_futuretest_newpc` |
| `npk_version_android4` | `20260923_230452_release_android` |
| `npk_version_android4_playertest` | `20260923_121822_playertest_android` |
| `npk_version_pc3*` | 2026-03 老货，**已停更** |

> ★ **清单条目全是「包级」**（`.npk` / `.dll` / `.exe` / `.pak`），
> **不含资源级路径**（无 `.dds`/`.mesh`/`.gim`）——
> **别再从清单求资源路径**。

---

## 三、版本号 ↔ 清单对应（关键规律）

```text
Documents/update.ini
   [Setting]
   version = 0.<YYMMDD><HHMM截3位>.<sub>
   subversion = 0

实测对照：
   0.260923 164 .1  ←→  npk_version_*_playertest = 20260923_164313_playertest_*   ✓
   0.260923 230 .9  ←→  npk_version_*            = 20260923_230458_release_*      ✓

Documents/cloud.json
   combo_patch_dir = "cloudfile_<YYMMDD><HHMM截3位>/"
   实测：cloudfile_260923164/（PC 测试服）· cloudfile_260923230/（手机正式服）
```

### 判据：这个客户端在哪条线

```text
① update.ini 的 version 时间戳
② cloud.json 的 combo_patch_dir
③ 标记文件 download_playertest_patch 是否存在
④ （手机）logcat 里请求的 npk_version_android4* 清单名
```

### 监控测试服更新（推荐 ✓ 纯只读）

```bash
# 定期拉，比对 version 字段；变了就是测试服更新了
curl -s https://g66.update.netease.com/pl/npk_version_newpc4_playertest
```

---

## 四、版本级 diff（不读本地客户端）

```bash
toolkit_cli.py delta
```

```text
清单 URL：https://g66.update.netease.com/pl/npk_version_newpc4[_<后缀>]
  release    = npk_version_newpc4              正式服
  playertest = npk_version_newpc4_playertest   测试服
★ 只拉 CDN 清单 + 只读项目内缓存（不读任何本地客户端文件）
```

对应模块：`toolkit_core/patch_delta.py` · `toolkit_core/patch_log.py` · `toolkit_core/patch_overlay.py`

> 官方 CDN 清单只到**包级**，客户端 `plcoht_ag` 是**落盘级** —— 两者**互补**。

---

## 五、补丁下载（只走官方 CDN）

```text
BASE_CDN = "https://g66.gph.netease.com"

流程（patch_overlay.py）：
  ① 读客户端状态（update.ini / cloud.json / pkg_N.pi）
  ② ★ CDN 目录名藏在 version_info 的 pkg_lst.name / pkg_N.pi.name 里
  ③ GET  <BASE_CDN>/<cdn_dir>/<name>
  ④ 解包 → 对本地行
```

```bash
toolkit_cli.py hotfix all      # 下载 + 解包定位 + 官方对比 + 报告
toolkit_cli.py ovl entries <包>  # 看 overlay 条目表
```

---

## 六、切服（★ 需谨慎，有封号风险）

### 手机端（机制：一个 1 字节标记）

```text
开关文件：Documents/download_playertest_patch   内容 = "1"（严格 1 字节）
★ 版本值必须取【本 tier】的，不能拿 PC 的值给手机
   手机 playertest: version = 20260923_121822_playertest_android
     ⇒ update.ini:  version = 0.260923121.1
     ⇒ cloud.json:  combo_patch_dir = cloudfile_260923121/
   ✗ 用 PC 的 260923164 ⇒ 客户端报 E116 版本信息检查失败
```

步骤：备份 8 个文件 → 写 `update.ini`/`cloud.json` → 建标记文件 → 重启 → 登录
（`am force-stop` + `am start -n <Activity>`；`monkey` 在雷电里不存在 ✗）

**验证（不用 root ✓）**：

```bash
adb -s emulator-5554 logcat -d | grep -iE "Orbit|npk_version|playertest|orbit_cache"
# 判据：出现 npk_version_android4_playertest 且 httpcode 200
#       或下载文件名含 playertest
#       或 orbit_cache 出现 pl_npk_version_android4_playertest
```

**回滚**：`_backup_before_switch/` 8 个文件覆盖回去 + 删标记文件 + 重启。
原文件清单：`update.ini · version · fo_version · cloud.json · last_region_code ·
prbsw · cfs_version · cfs_version_inited`

### PC 端（机制：换一套补丁文件）

```text
★ launcher_conf 不是开关 ✗（正式服与测试服的该文件完全一致 = diff 为空）
   它 = 单字节 XOR 0xFA 的 JSON，字段仅 version / cleanup / exe
⇒ PC 上"切服" = 把目标服的补丁集下载并覆盖到客户端
⇒ 手机"切服" = 那个 1 字节标记（机制不同，别混）
```

### 脚本

```bash
python 01_工具/工具库/04_热更定位/切服与CDN.py gen --tier android --line playertest --out <dir>
```

---

## 七、风险与合规（必须知道）

```text
· 改客户端文件（§6）属于【修改客户端】，违反用户协议 ⇒ 封号风险落在操作者自己账号上
· 性质说明：只是【版本/补丁选择】，不修改游戏逻辑、不是作弊工具
· 可回滚 ✓ · 不影响服务端 ✓
· 【纯只读】部分（取清单 / 监控版本 / 版本 diff）无此风险 ✓ —— 那是服务端公开内容
```

---

## 八、复现命令

```bash
# 取清单（只读）
curl -s "https://g66.update.netease.com/pl/npk_version_android4_playertest" -o x.json

# 抓运行时请求（不用 root）
adb -s emulator-5554 logcat -d | grep -iE "Orbit|npk_version"

# 备份 / 回滚（手机）
adb -s emulator-5554 shell "mkdir -p <DOC>/_backup_before_switch"
adb -s emulator-5554 shell "cp -f <DOC>/update.ini <DOC>/_backup_before_switch/"
```

**相关模块**：`toolkit_core/{patch_delta,patch_log,patch_overlay,npk_remote}.py` ·
**脚本**：`01_工具/工具库/04_热更定位/切服与CDN.py`
