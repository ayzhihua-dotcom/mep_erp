# 《S2 开发任务书：进口案件族（TP-LOGIMP-002）》草案（V0.1）

- 编制依据：V0.2 字段字典（IMP-001 ~ IMP-006 / IMP-009 接口）、《流程规范》（§2.2 Import Case 状态机 / IMP-008 三事件）、《数据库关联与权限设计》（§2 定制对象）、TP-LOGIMP-001。
- 编制日期：2026-10-28
- 状态：草稿

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 覆盖功能 | IMP-001 进口业务档案、IMP-002 单证清单、IMP-004 申报状态（里程碑）、IMP-003 接口（NCM 来源 MDM）、IMP-005 税费记录、IMP-006 代理费用 |
| 实现形态 | 定制 DocType 五件套：Import Case / Import Document Checklist / Import Milestone / Import Cost（+ Allocation 属 S5） |
| 前置依赖 | TP-LOGIMP-001（Shipment 就绪）；TP-MDM NCM 字段 |

## 二、DocType 设计

### 2.1 主表 Import Case（IMP-001）

| 字段 | 规则 |
| --- | --- |
| import_case_no | 自动编码（IC-YYYY-流水）；唯一 |
| importing_company / customs_broker（代理） | 进口公司、清关代理（供应商档承载） |
| link_shipment | Link → Shipment（可多个：允许 Link 子表，V0.1 先一对一预留多对） |
| destination_port / commercial_invoice_no / invoice_date | 目的港、商业发票号/日期 |
| declared_value / declared_currency / exchange_rate | 货值、币种、汇率 |
| country_of_origin / ncm_summary | 原产国、NCM 汇总（取装运行→Item；异常时人工处理留痕） |
| internal_status | 状态机见 §三 |

### 2.2 Import Document Checklist（IMP-002）

| 字段 | 规则 |
| --- | --- |
| doc_type / is_mandatory | 单证类型（与 Shipment Document 字典同源）、是否必需 |
| required_at_stage | 要求具备的阶段（申报前/放行前/归档前） |
| attachment / doc_version / due_date | 文件、版本、截止日 |
| status / issue_text | 齐备/缺失/问题、问题描述 |
| submitted_by / reviewed_by | 提交/审核人 |

校验：推进到"申报"前，`is_mandatory` 且 `required_at_stage=申报前` 的单证必须齐备，否则拦截（留痕豁免走高权限，IC 对应内控）。

### 2.3 Import Milestone（IMP-004 申报状态）

| 字段 | 规则 |
| --- | --- |
| milestone_type | 申报提交 / 海关受理 / 查验 / 补资料 / 缴税 / 放行 / 提货 …（字典待确认） |
| planned_date / actual_date | 计划/实际日期（差异自动标色） |
| responsible_party / evidence_attachment / remarks | 责任方（代理/公司）、来源证明文件、说明 |
| is_abnormal | 异常标记（IMP-007 / ALR-004 取数源） |

### 2.4 Import Cost（IMP-005 / IMP-006）

| 字段 | 规则 |
| --- | --- |
| cost_type | 关税（II/HI/IPI/PIS/COFINS/ICMS 枚举待确认）/ 报关代理 / 港口 / 仓储 / 其他 |
| estimated_amount / actual_amount / currency / exchange_rate / base_amount | 预计/实际、原币、汇率、基准币 |
| voucher_attachment / cost_supplier | 凭证、收款方 |
| payment_status | 未付/部分/已付；付款审批联动财务（IC-04 变更留痕：原金额/新金额/原因字段） |
| capitalized_flag（资本化/期间） | 决策 D-y13（暂默认资本化，随分摊细化定稿） |
| approval_status | 费用录入/变更走审批（财务 FIN） |

## 三、状态机（承接流程规范 §2.3）

创建 → 单证齐备（校验）→ 申报 → 查验（可分支补资料）→ 缴税确认 → 放行 **事件①** →提货 **事件②** → 仓库验收 **事件③**（三事件为 IMP-008 独立记录，在 Import Milestone 中分别落节点）→ 归档（IMP-010）。

## 四、任务分解

| 任务号 | 任务 |
| --- | --- |
| TP-LOGIMP-002-01 | 五件套 DocType + Import Case 状态机 Workflow（含单证齐备校验拦截） |
| TP-LOGIMP-002-02 | Import Milestone 三事件节点 + evidence 上传 |
| TP-LOGIMP-002-03 | Import Cost 审批流 + IC-04 变更留痕字段 |
| TP-LOGIMP-002-04 | 案件汇总视图（单证齐备率、费用对比预计/实际、里程碑进度） |
| TP-LOGIMP-002-05 | 国别公司隔离：BRA/CUS 角色数据范围验证 |
| TP-LOGIMP-002-06 | 示例数据：1 案件全周期（申报→查验→补资料→放行→提货→验收→归档） |

## 五、验收用例

| 用例 | 通过标准 |
| --- | --- |
| UC-I01 | 必需单证未齐时推进"申报"被拦截 |
| UC-I02 | 三事件（放行/提货/验收）分别独立记录且时间可差 |
| UC-I03 | 费用修改（实际≠预计）留原/新金额+原因+审批 |
| UC-I04 | 案件 ETA/里程碑异常标记可被预警取数（占位） |
| UC-I05 | CUS/BRA 角色仅见 C2 范围案件 |

## 六、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| S2-I1 | 税费域 II/IPI/PIS/COFINS/ICMS 枚举与归类规则 | 清关业务方确认 |
| S2-I2 | 案件-装运是否始终一对一 | 业务确认（默认一对一，预留多对） |
| S2-I3 | 里程碑类型完整字典 | 业务方提供 |
| S2-I4 | NCM 与 Import Case 的取数异常处理（Item 未归类时的阻断/占位规则） | 业务决策 |
| D-y13 | 进口费用资本化/期间划分规则 | S5 分摊细化定稿 |
