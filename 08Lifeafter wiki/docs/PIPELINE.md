# 08Lifeafter Wiki 生成流水线（PIPELINE v0.1）

> 作者：Hermes ｜ 模型：gpt-5.6-terra（openai-codex）｜ 日期：2026-08-31

## 一、流水线总览

```text
拆包工具库（01拆包器本体\工具库）
   │  export_*.py 导出（带 provenance）
   ▼
data/boards/*.json（板块数据）
   │  build_wiki.py 扫描+校验
   ▼
data/manifest.js（window.WIKI_MANIFEST）
   │  <script src> 引入
   ▼
wiki.html / 各板块页（纯静态渲染，file:// 直接可用）
```

**设计原则**：数据与页面分离。页面只负责渲染，数据全部来自带 provenance 的 JSON；`file://` 协议下不能用 `fetch`，所以 builder 一律输出 `window.XXX = ...` 形式的 .js（沿用豆包模式）。

## 二、各环节校验点

| 环节 | 校验点 | 失败处理 |
|---|---|---|
| 导出 | provenance 字段齐全；证据等级合法；命名走正源 | 拒绝导出 |
| builder | meta 必填；items 必填；证据等级枚举；无时间字段 | 不生成 manifest（fail fast） |
| 页面 | manifest 加载后统计板块条目 | 页面显示"未生成"提示 |
| 发布 | git diff 审阅；源 SHA 变化检查 | 未审阅不发布 |

## 三、常用命令

```bash
# 生成/更新板块清单
python tools/build_wiki.py

# 查看数据状态（git）
git status
git diff --stat
```

## 四、Phase 1 起每板块接入步骤

1. 拆包工具库中确认/新增 `export_<board>.py`（复用严格 BinDict 解码器）
2. 导出到 `data/boards/<board>.json`，补齐 provenance
3. 名称/说明字段另保留 `field_chs_slot → value_chs_slot → text`；不能只保留解码后的中文
4. 跑 `build_wiki.py` 校验通过
5. 新增板块页（沿用豆包渲染风格），wiki.html 登记入口
6. git commit，日志写入 06

## 五、与 06 日志联动

- 拆包新结论：先写 06 日志（作者/模型/证据等级/来源），再入数据
- 数据修正：06 日志追加更正条目，数据文件同步更新
- 旧包数据：源 SHA 变化即降级 candidate，不得静默沿用
