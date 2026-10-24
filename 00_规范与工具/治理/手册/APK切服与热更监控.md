# 安卓客户端切服与热更监控（2026-10-18 实测）

> **★ 2026-10-18 起：拆包大本营 = PE 测试服（安卓）**
> 理由：内容与 PC 测试服同源（表数量 31,336 vs 33,269，差 6%），但 **npk 保留路径、可按名寻址**，
> 而 PC/PE 的 `*.gpk` 条目键都不是路径哈希（PC 59% 无名、PE 0/60 命中），只能靠内容匹配。
> PC 测试服降级为**差异对照**（新内容有时先在 PC 的 `0006.gpk` 出现）。


## 一、切服开关

开关是 `Documents/` 下的 **1 字节文件**，内容 `1`（无换行、无 BOM）：

| 开关文件 | 作用 |
|---|---|
| `download_playertest_patch` | **测试服**（playertest） |
| `download_playertest_yk_patch` | 测试服 · yk 服型 |
| `download_futuretest_patch` | 未来测试服 |
| `download_yh_patch` | 预发布/灰度 |
| `download_gray_patch` | 灰度 |
| `patch_abtest_2026` | AB 测试 |

来源：`script.py314.lc.npk/patch/PatchConfig.py` 里的常量表（实测文件名逐个对上）。

★ **开关只在启动时读取**。切服后客户端自己向服务器取版本信息，重写：
- `Documents/update.ini` → `version = 0.2<YYMMDD><HH><分钟首位>.<sub>`
- `Documents/cloud.json` → `combo_patch_dir = "cloudfile_<同上数字>/"`

**不要手改这两个值**：sub 位无法从外部推断，改错就是 E116（版本信息检查失败）。

## 二、完整路径

```
/sdcard/Android/data/com.netease.mrzh/files/netease/g66/
  Documents/
    update.ini  cloud.json  client.ini  fo_version
    local_state_314_lc  local_finfo_314_lc  cfs_version
    downloaded_packages  plcoht_ag(.1~.10 补丁日志，XOR 0xAA)
    gres/          172~175 个 gpk（43 GB）
    _backup_before_switch/   切服前的原始 update.ini/cloud.json
```

## 三、工具

`01_索引与产物/10_索引/热更检测/android_watch/切服.py`

```bash
python 切服.py status          # 渠道/版本/开关一览
python 切服.py record release  # 记录快照到 baseline_<标签>_<日期>/
python 切服.py to-playertest   # 只建开关，不启动
python 切服.py to-release      # 删除全部开关
python 切服.py launch / stop   # 启动 / 停止游戏
```

配套监控：`android_watch.py`（每 4 s 扫 503 个文件，变化即落快照 + 拉 CDN 清单）

- `python android_watch.py baseline` 记录基线
- `python android_watch.py watch 4` 持续监控
- `python android_watch.py status` 与基线比对一次

## 四、踩过的坑

1. **文件权限 600**：`gres/*.gpk` 属主 u0_a108、`-rw-------`，shell 拉不动。
   ⇒ 雷电需开 root：`ldconsole.exe modify --index 0 --root 1`，**必须重启模拟器**才生效；
   之后用 `su -c 'cp 源 /sdcard/Download/ && chmod 644 ...'` 再 `adb pull`。
2. **不要用 `adb exec-out su -c "cat 大文件"`**：su 会往 stdout 混入约 1 MB 内容，文件会偏大。
3. **su 的参数引号**：必须 `adb shell "su -c '命令'"`（整条命令单引号包住），否则 su 把参数当 uid，报 `Unknown id`。
4. **中途重启会留下半成品包**（本次 0339/0340/0341），随后一直 E116；
   处理办法：把半成品 `mv 成 .bak_halfdownload`，启动游戏让它重下（本次实测可行）。
5. 客户端「修复」会**删除** `download_playertest_patch`，等于自动回正式服。
