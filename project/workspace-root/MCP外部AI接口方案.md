# 《MCP 外部 AI 接口方案（V0.1）》

- 编制依据：《外部接口规范》（本方案作为 IF-10 承载）、《数据库关联与权限设计》（RBAC/审计）、《S1 交付物：环境搭建与定制应用骨架方案》（cb_erp 应用扩展位）、S4 部署终案（托管形态依赖）。
- 编制日期：2026-10-28
- 状态：草稿（待业务/技术评审；实现排期建议 S5~S6，可与部署形态一并冻结）

## 一、定位与目标

| 项 | 内容 |
| --- | --- |
| 目标 | 为 ERP 系统提供一个 **MCP（Model Context Protocol）标准接口**，让外部软件（AI 助手、智能体办公软件、上下游系统、数据分析 Copilot 等）以统一协议读取（首期）/受控写入（二期）ERP 业务数据 |
| 实现载体 | 定制应用 `cb_erp` 内新增模块 `mcpsrv`（Frappe 内嵌 MCP Server），或独立旁挂 MCP 服务进程连 MariaDB/Frappe API——二选一见 §四 |
| 协议 | MCP 标准传输：stdio（本机/同进程）+ Streamable HTTP（远程客户端），SSE 兼容旧客户端 |
| 典型消费方 | 桌面 AI 助手（如 Claude Desktop、OpenCode 等 MCP 客户端）、企业内部智能体、其他业务系统的 MCP 网关 |

## 二、对外能力设计（首期：只读）

### 2.1 MCP Tools（业务查询工具，首批 12 个）

| 工具名 | 功能 | 数据来源 |
| --- | --- | --- |
| get_project_status | 项目状态/合同/预算概览 | Project + custom 字段 |
| list_material_stock | 库存查询（仓库/可用/冻结/待检） | Bin / Stock Ledger |
| get_demand_gap | 项目净采购缺口与明细钻取 | Demand Summary Snapshot（最新快照） |
| list_purchase_orders | 采购订单清单/状态/交期 | Purchase Order |
| get_shipment_status | 装运批次进度/ETA | Shipment / Milestone |
| get_import_case | 进口案件状态/单证齐备率 | Import Case / Checklist / Milestone |
| import_costs_summary | 进口费用预计 vs 实际 | Import Cost |
| get_cost_deviation | 预算-承诺-实际-偏差 | CST-007 报表口径 |
| list_alerts | 未结预警清单 | Alert Event |
| search_materials | 材料检索（三语名称/规格/NCM） | Item |
| getSupplierPerformance | 供应商绩效快照 | PUR-010 报表 |
| whoami | 当前授权身份与数据范围自检 | MCP 鉴权层 |

### 2.2 MCP Resources（资源数据）

- 报表快照资源：需求快照/偏差报表/库存报表的最新快照（URI 形式，供 AI 自行分析）；
- 单证元数据（附件名/版本/状态；**首期不开放文件内容流**——保密附件走 ERP 界面）。

### 2.3 二期（受控写入，默认关闭）

- write_alert_resolution（预警处理回写）、create_data_import_task（ALR-005 口径）、update_milestone（IF-01 代理回传）——均须走审批镜像 + 审计，开关默认 OFF。

## 三、安全与权限（硬性规则）

| 规则 | 实现 |
| --- | --- |
| 身份绑定 | 每 MCP 客户端配发独立服务账号（Role = mcp_client + Agent User），**禁止共用超级账号** |
| 数据范围 | 服务账号绑定 User Permission（公司/项目/仓库范围），与 S1 ② 矩阵同源；不同外部软件按授权范围最小化配置 |
| 只读优先 | 首期全部工具只读；写入工具默认禁用（§2.3） |
| 字段保密 | MCP 输出按《字段级保密清单》过滤（价格/成本类字段对非授权范围不返回，而非仅界面隐藏） |
| 审计 | 每次 MCP 调用写 MCP Audit Log：调用方/identity/工具/参数摘要/耗时/返回行数；接入 Cost Audit Log 同级报表 |
| 限流与配额 | 每调用方每分钟请求上限 + 每日配额，超限返回标准错误 |
| 密钥管理 | 令牌定期轮换；泄露即吊销；存运维密柜 |
| 输出一致性 | 驾驶舱同源禁令同样适用：MCP 返回值必须来自同一计算服务/报表口径 |

## 四、架构（两种承载，O-01 联动）

| 方案 | 描述 | 优点 | 风险 |
| --- | --- | --- | --- |
| A. 应用内嵌（建议默认） | `cb_erp/mcpsrv` 模块随站点启动 Streamable HTTP 端点（Nginx 反代 + 独立路径 + TLS） | 权限/审计原生复用、部署零旁路 | MCP 依赖版本需适配 Frappe v16 |
| B. 旁挂服务 | 独立 Python MCP 服务（mcp 官方 SDK）经 Frappe REST API 取数 | 解耦、随升独立迭代 | 双层鉴权易漏、审计重实现 |

决策登记：MCP-01（承载方式，S4 部署终案时一并冻结；默认 A）。

## 五、数据互通边界（与其他接口的关系）

- MCP ≈ **AI 软件专用语义层**：给 AI 的"会话式读数+分析"能力；
- 非智能体软件的数据互通仍走 `外部接口规范` 既有通道（IF-01~09 + Frappe REST API）；MCP 不放大权限、不绕过 Workflow；
- 三语输出：工具返回带 language 参数（D-11：默认中文）。

## 六、验收用例

| 用例 | 通过标准 |
| --- | --- |
| UC-MCP01 | 外部 AI 客户端发现 12 工具并用 whoami 获取自身范围 |
| UC-MCP02 | 范围外项目数据查询被拒（403 语义）且留审计 |
| UC-MCP03 | 金额类字段对未授权范围不返回（非空字段隐藏） |
| UC-MCP04 | get_demand_gap 结果与驾驶舱数值一致（同源校验） |
| UC-MCP05 | 令牌吊销后客户端立即失效 |
| UC-MCP06 | 限流触发返回标准错误且不扰动 ERP 主服务 |

## 七、任务分解与排期建议

| 任务号 | 任务 | 依赖 |
| --- | --- | --- |
| TP-MCP-01 | 承载方式决策（MCP-01）+ 服务账号规范 | O-01 |
| TP-MCP-02 | 首批 12 个只读工具实现 + 字段过滤层（SEC 联动） | S2~S5 DocType/报表就绪 |
| TP-MCP-03 | MCP Audit Log + 审计报表 | TP-CST-B-04 |
| TP-MCP-04 | 限流/配额/密钥轮换运维件 | 部署 runbook |
| TP-MCP-05 | 外部软件接入手册（连接参数/工具清单/示例对话） | TP-MCP-02 |

## 八、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| MCP-01 | 承载方案 A/B 冻结 | S4 部署终案 |
| MCP-02 | 首个消费方（哪个外部软件/团队）与范围 | 业务方决策 |
| MCP-03 | 二期写入工具清单 | 二期评审 |
