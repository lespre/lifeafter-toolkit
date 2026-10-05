# 本地只读 NPK 检查器（MVP）

> 建立：2026-09-02 02:39 +0800  
> 范围：当前体验服 Documents 脚本包的**索引与单条内存解码**；不是全量拆包器，也不是活动启用判定器。

## 1. 当前登记源

```text
source_id：documents-py314-current
文件：E:\mrzh\Documents\script.py314.lc.npk
服务器：体验服 Documents 当前快照
SHA-256：328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f
字节数：270,106,156
```

`data/live_sources.json` 是本地服务唯一允许读取的源登记表。启动时会重算 SHA-256，并且只在实际哈希和文件大小都与登记源锁一致时，开放条目读取。

## 2. 启动与访问

在 Wiki 根目录执行：

```bash
PYTHONDONTWRITEBYTECODE=1 python tools/wiki_server.py --host 127.0.0.1 --port 8765
```

浏览器打开：

```text
http://127.0.0.1:8765/
```

首页标题右侧的 **本地工具 · 现场读取 NPK** 会进入 `live_reader.html`。

服务强制只绑定 `127.0.0.1`；不监听局域网，也不向外上传任何资源包内容。

## 3. 实际读取方式

```text
浏览器检查页
→ localhost API
→ 读取 NPK 头 + 48B 索引表到内存
→ 按 entry_index / file_id seek 单个压缩段
→ AES / zlib / LZ4 / Zstd 内存解码
→ 返回摘要、哈希、直接路径候选和有限 UTF-8 预览
```

- 不创建 `entries/*.bin`；索引只在服务进程内存中存在。
- 不提供原始 payload / NPK 下载 API。
- 不提供全包文本扫描 API；中文全文检索以后如需实现，必须另建轻量文本摘要索引，不能把全量解包伪装成检索。
- 每条摘要都包含 `source_package_sha256`、`entry_index/file_id`、解码 SHA-256、证据等级和解释边界。

## 4. API（只读）

```text
GET /api/health
GET /api/sources
GET /api/sources/<source_id>/entries?offset=0&limit=50&q=<entry_index或file_id片段>
GET /api/sources/<source_id>/entries/<entry_index>/summary
```

没有 `/raw`、`/download`、`/extract-all` 或写源包的接口。

## 5. 证据边界

`evidence_level=package_entry_exists` 只表示：该条目在当前、已锁定的客户端包中物理存在，并已在内存里成功静态解码。

它**不表示**活动已开启、奖池已切换、奖励可领取、物品已上线或服务端 selector 已生效。业务结论继续要求当前同快照的活动表、selector / 时间字段和实机锚点闭环。

## 6. 热更后的正确处理

如果 `script.py314.lc.npk` 被热更，服务检测到文件大小或 mtime 变化会拒绝继续读取；若 SHA / bytes 与 `live_sources.json` 不再匹配，也会返回 `source_lock_mismatch`。

正确顺序：

1. 先重建当前包的源锁和差分审计；
2. 更新 `data/live_sources.json` 的 SHA / bytes；
3. 重启本地 Wiki 服务；
4. 重新验证 API 与业务证据链。

不能为了让页面恢复工作而直接把新哈希填进去。

## 7. 回归验证

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
```

当前回归覆盖：真实 Documents NPK 的索引/单条摘要、localhost API、首页工具入口、检查页静态访问链。
