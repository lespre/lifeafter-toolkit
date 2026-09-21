"""Workbench API（Phase 1）：唯一正式查询入口。

只通过 services/ 访问 registry/ · artifacts/active/ · residuals/ · evidence/。
禁止直接读 legacy board / historical artifact / 日志 / raw package / LOCATOR DB（services.store 强制）。
"""
