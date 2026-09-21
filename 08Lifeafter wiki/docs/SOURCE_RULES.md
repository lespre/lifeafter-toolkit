# SOURCE_RULES（P3 可靠数据源规则 v2）

1. **verified**：关键槽（名称正源=name；业务源=name+icon）全 verified。
2. **usable_with_limits**：关键槽 likely（样本不足），行级复核后可用。
3. **unsafe**：关键槽 unsafe——该槽值禁止作为业务真值。
4. **unresolved**：池缺/无样本/无标准语义槽名。
5. 类别仅表名模式归类；不做业务 join。
6. oversea 变体为分支版本；server_branch 一律 unresolved。
