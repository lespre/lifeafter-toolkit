# 站点数据目录

**框架入库，数据不入库。**

## 入库的（框架）

| 文件 | 作用 |
|---|---|
| `wiki_taxonomy.json` / `.js` | 板块目录树（分类 → 板块），导航与路由的唯一来源 |
| `publication_policy.json` / `.js` | 发布策略：哪些板块可公开、证据等级要求 |
| `manifest.js` | 板块清单（板块 id / 条目数 / 构建时间） |
| `table_index.json` | 表名索引（provenance 校验用） |

## 不入库的（数据）

```
data/boards/*.json / *.js     板块条目（数百 MB，可由还原树重建）
data/*.jsonl                  审计中间产物
```

重建方式：

```bash
# 需要还原树 03_执行/41_还原树/pe_<日期>/
python 04_站点/web/tools/build_wiki.py
```

`build_wiki.py` 会重新生成 `manifest.js` 与全部板块文件，并做完整性校验
（meta 必填字段、证据等级、provenance 表名可达）。

## 新设备上跑起来

1. 克隆仓库（含框架）
2. 按 `docs/AGENT.md` 重建还原树与索引
3. `python 04_站点/web/tools/build_wiki.py` 生成板块
4. `python 04_站点/web/tools/wiki_server.py` 起服务

没有第 2、3 步时，站点能启动、导航能显示，但板块页会是空的 —— 这是预期行为。
