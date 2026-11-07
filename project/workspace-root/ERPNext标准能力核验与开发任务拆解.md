# 《ERPNext 标准能力核验与开发任务拆解》草稿（V0.1）

- 编制依据：V0.2 字段字典（本项目草案）、SRS V1.0、《SRS V1.0 ↔ 字段字典 V0.1 功能覆盖对照清单》、核心业务流程与状态转换规范、数据库关联与权限设计。
- 编制日期：2026-10-28
- 状态：草稿

## 一、核验结论总览

| V0.2 章节 / 功能 | ERPNext 标准能力复用情况 | 主要定制 / 配置 |
| --- | --- | --- |
| PRJ / PRJ-001~007 | Project + Material Request 复用；设计 BOM、变更、关闭检查多需定制 | Design BOM DocType；Change Request；Close Check 工作流 |
| PUR / PUR-001~010 | Buying 模块主体复用（Material Request/Rfq/Quotation/PO/Receipt/Invoice/Payment）；审批、比价、技术审核、交期、关闭、绩效部分需配置/开发 | Workflow；Supplier Quotation；计算/报表 |
| LOG / IMP / SHP | Shipment、Import Case 等多需定制；物流节点、清关单证、费用需定制 | Shipment DocType；Import Case/Docs/Cost DocType |
| CST | Landed Cost Voucher 部分复用；项目成本、分摊、预算偏差需扩展 | Landed Cost；分摊引擎；Project Cost |
| INV / WH | Warehouse、Quality Inspection、Stock Entry 复用；调拨、冻结、报表部分需开发 | Transfer；冻结；库存报表 |
| LPO | PO + Supplier 复用；本地采购标识、费用、比较需扩展 | Local Tag；费用归集 |
| ALR / BI | Notification/Report 部分复用；预警、驾驶舱需定制 | Alert Event；Dashboard |

## 二、开发任务包（按 V0.2 章节拆分）

### TP-PRJ（项目与工程材料管理）

- TP-PRJ-001：设计材料清单（Design BOM）DocType 开发。
- TP-PRJ-002：设计变更（Change Request / 版本差异行）开发。
- TP-PRJ-003：项目关闭检查流程开发。
- TP-PRJ-004：需求追溯计算服务开发（净采购缺口）。

### TP-PUR（采购管理）

- TP-PUR-001：采购审批 Workflow 配置。
- TP-PUR-002：供应商报价/比价能力扩展。
- TP-PUR-003：采购订单项目分配与订单关闭检查开发。
- TP-PUR-004：交期管理与订单关闭流程开发。

### TP-LOGIMP（国际物流与进口清关）

- TP-LOGIMP-001：Shipment DocType 与 Shipment Item 开发。
- TP-LOGIMP-002：Import Case / Import Document / Import Cost 开发。
- TP-LOGIMP-003：物流节点、异常、到货预测、归档流程开发。

### TP-CST（项目成本与预算）

- TP-CST-001：Landed Cost 项目归属与分摊扩展。
- TP-CST-002：项目材料成本 / 领料成本 / 预算偏差计算开发。

### TP-INV（仓库与库存）

- TP-INV-001：仓库调拨（Transfer）流程。
- TP-INV-002：项目间调拨与成本归属。
- TP-INV-003：盘点（Stock Reconciliation）、批次追溯、冻结、库存报表。

### TP-LPO（巴西本地采购）

- TP-LPO-001：本地采购标识（Local Tag）与费用归集。
- TP-LPO-002：本地供应商对比。

### TP-ALRBI（预警与驾驶舱）

- TP-ALRBI-001：预警事件（Alert Event）与定时计算。
- TP-ALRBI-002：管理驾驶舱 Dashboard。

## 三、任务优先级

1. **P0**：TP-PRJ-001/2/3；TP-PUR-001/3/4；TP-LOGIMP-001~3；TP-CST-001/2；TP-INV-001~3；TP-LPO-001/2；TP-ALRBI-001/2。
2. **P1**：剩余任务包（绩效、Excel 导入、操作审计等）。

## 四、阶段映射

- S2/S3：主数据、采购、仓储领料相关任务。
- S4：国际物流/进口任务。
- S5：成本/预警任务。
- S6：上线前任务收敛。

## 五、遗留待办

- D-01~D-10 业务决策冻结前，任务范围以业务确认为准。
- ERPNext 目标版本核验后，任务拆解细化（字段类型、状态类型、DocType 能力）。

## 六、验收要点

1. 每个任务可对应 SRS 功能编号与验收用例。
2. 标准能力复用优先，定制任务独立于 ERPNext 核心代码。

## 七、下一步

- 依据本任务拆解，进入 **S0：业务调研与蓝图设计** 阶段门准备，或细化单个任务（如 TP-PUR-001）到可开发粒度。
