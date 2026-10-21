# 已归档测试

这些测试只覆盖已删除的旧板块（retired），板块数据已移入 `_备份归档/deleted_boards_20261019/`，
测试一并归档保留，不再进入 CI。

如需复活某块板：把对应 json/js 从 `_备份归档/deleted_boards_20261019/` 拷回 `data/boards/`，
重新登记 publication_policy，再把这里的测试文件移回 `tests/`。
