# 《TP-MCP-02：MCP 只读工具技术详设（V0.1）》

- 编制依据：《MCP外部AI接口方案》（TP-MCP-02 承接）、《数据字典_字段级完整版》（返回结构字段同源）、《字段级保密与审计配置清单》（服务端过滤）
- 编制日期：2026-10-28
- 状态：草稿（实现于 S5~S6；字段名以数据字典实建回填写准）

## 一、通用调用约定

| 项 | 规则 |
| --- | --- |
| 语言参数 | 每工具参数 `language`（zh / pt-BR / en，默认 zh=D-11；用于名称/状态显示文本） |
| 分页 | `page`（1 起始）+ `page_size`（默认 20，上限 100）；返回 `total / page / page_size / has_next` |
| 错误模型 | 统一 `{ error: { code, message, ref_id } }`；code：AUTH_REQUIRED / FORBIDDEN_SCOPE / FIELD_FILTERED / NOT_FOUND / RATE_LIMITED / INVALID_PARAMS / SERVER_ERROR |
| 时间格式 | UTC ISO-8601；金额带 currency 三位码 |
| 字段过滤 | 保密字段返回中直接不出现（非空值隐藏），并返回 `filtered_fields: [...]` 提示 |
| 审计 | 每条调用入 MCP Audit Log（调用方/工具/参数摘要/返回行数/耗时） |

## 二、12 工具参数与返回结构

### 2.1 whoami

- 入参：无。
- 出参：`{ identity, role_profile, scope: { companies[], warehouses[], projects[] }, read_only: true, tools_allowed_count }`。

### 2.2 get_project_status

- 入参：`project`（必填，Link 精确匹配）；`language`。
- 出参：`{ project_code, name(zh/pt/en), status, contract_no, contract_amount{value,currency}, budget_amount, wbs_outline_graph_count, last_activity_date }`。
- 过滤：预算类字段按《保密清单》角色告警范围过滤（PM/FIN/MGT 可见，其余 FIELD_FILTERED）。

### 2.3 list_material_stock

- 入参：`warehouse`（可选；不含则按授权范围汇总）、`item_group`（可选）、`include_frozen`（默认 true 分列）、`page/page_size`。
- 出参行：`{ item_code, item_name(display lang), group, warehouse_name, qty_available, qty_on_hold(待检), qty_frozen, valuation_flagged(金额仅 FIN/MGT) }`。

### 2.4 get_demand_gap

- 入参：`project`（必填）、`item`（可选）、`snapshot_no`（可选；缺省最新快照）。
- 出参：`{ snapshot_no, computed_at, rule_version, lines: [ { item, wbs, design_total, issued, allocated, available, confirmed_transit, net_gap, drill: { bom_doc, mr_docs[], po_docs[], shipment_docs[] } } ], totals }`。
- 同源校验：值直取 Demand Summary Snapshot（UC-MCP04）。

### 2.5 list_purchase_orders

- 入参：`project` / `supplier` / `status`（枚举）/ `sourcing_region`（仅授权 China/Brazil Local）/ `date_from/date_to` / 分页。
- 出参行：`{ po_no, supplier_name, status, currency, amount, amount_filtered?, schedule_date, latest_promised_date, actual_delivery_date, projects[通过 Allocation] }`。
- 保密：金额列对 WHS/LOG/CUS/ENG 不返回。

### 2.6 get_shipment_status

- 入参：`shipment_no`（精确）或 `po_no` 或 `project` 检索 + 分页。
- 出参：`{ shipment_no, status, supplier, mode, actual_ship_date, eta_current, eta_history[{recorded_at, eta}], nodes[{node_type, planned, actual}], docs_summary{required, ready, missing[]} }`。

### 2.7 get_import_case

- 入参：`import_case_no` 必填。
- 出参：`{ case_no, internal_status, broker, declared_value{value,currency}, checklist[{doc_type, status, is_mandatory, due_date}], milestones[{type, planned, actual, is_abnormal}], costs_summary{ estimated_total, actual_total, by_type[] } }`。
- costs_summary 仅 FIN/MGT/录入人可见（FIELD_FILTERED 处理同 2.2）。

### 2.8 import_costs_summary

- 入参：`import_case_no` 或 `project`；`cost_type` 可选。
- 出参：总计与分类型 `{ estimated, actual, variance, payment_status }`。

### 2.9 get_cost_deviation

- 入参：`project` 必填。
- 出参：`{ budget, commitment, actual, eac, deviation, trend_points[{date, values}] }`。
- 范围：FIN/PM/MGT 之外 FORBIDDEN_SCOPE 直接拒。

### 2.10 list_alerts

- 入参：`status`（默认: 未结）、`alert_type`、`project`、`assignee=me` 强制语义、分页。
- 出参行：`{ alert_id, alert_type, ref_object, metric_value+unit, severity, assignee, due_date, status }`。

### 2.11 search_materials

- 入参：`query`（搜三语名称/规格/型号/NCM）、`item_group`、分页。
- 出参行：`{ item_code, name_zh, name_pt, name_en(缺失回退提示), group, spec_summary, ncm_code?, ncm_status, disabled }`。

### 2.12 getSupplierPerformance

- 入参：`supplier`；`period`（YYYY-Q 或 YYYY-H）。
- 出参：`{ on_time_rate, completion_rate, price_change_index, quality_exception_count(占位口径), orders_count }`（PUR-010 报表口径）。

## 三、实现要点（V16 承接）

1. 参数结构以 JSON Schema 声明，供 MCP 客户端自动校验与自动发现；
2. 全部查询走 Frappe ORM/Report 层而非裸 SQL——保证权限钩子生效；
3. 字段过滤实现于输出序列化层（统一 Filter Layer），而非调用处散写（SEC-01 同组件）；
4. `ref_id` 错误追踪关联 MCP Audit Log 条目；
5. 返回数据一律标注 `computed_at` / `as_of`，防止 AI 陈旧取数误解。

## 四、验收补充（并 UC-MCP01~06 执行）

| 用例 | 通过标准 |
| --- | --- |
| UC-MCP07 | 12 工具 schema 手册发布并与实际返回字段 100% 一致 |
| UC-MCP08 | 分页边界（首页/末页/超页）无错 |
| UC-MCP09 | language=pt-BR 时名称字段返回葡语（缺失回退标 flag） |
| UC-MCP10 | filtered_fields 提示与保密矩阵逐条一致 |
