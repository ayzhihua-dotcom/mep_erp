# 《S2 开发任务书：装运与装运明细（TP-LOGIMP-001）》草案（V0.1）

- 编制依据：V0.2 字段字典（LOG-001~004 / LOG-006）、《ERPNext 标准能力核验与开发任务拆解》（V0.1）、《数据库关联与权限设计》（§3.4 Shipment 多对多）、TP-PUR-006/007（PO 下游衔接）。
- 编制日期：2026-10-28
- 状态：草稿

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 覆盖功能 | LOG-001 备货跟踪、LOG-002 装运批次、LOG-003 分批发运、LOG-004 包装明细、LOG-006 单证关联（批次级） |
| 实现形态 | ERPNext 无成熟国际物流模块，Shipment 族为**定制 DocType 三件套**：Shipment / Shipment Item / Shipment Document |
| 前置依赖 | TP-PUR-007-01（PO 行追溯字段）、TP-MDM-01 |

## 二、DocType 设计

### 2.1 主表 Shipment

| 字段 | 规则 |
| --- | --- |
| shipment_no | 自动编码（SH-YYYY-流水）；唯一 |
| supplier / carrier / from_port / to_port | 供应商、承运商、起运/目的港 |
| shipment_mode | 海运 / 空运 / 陆运 / 多式联运 |
| batch_type | `custom_is_consolidated`：多订单合并批次 或 订单行分批（LOG-002 两种形态均支持） |
| expected_ship_date / actual_ship_date / eta_revised | 计划发运/实际发运/修订 ETA（修订留痕） |
| status | 状态机见 §三 |
| packing_total_gross / packing_total_net / packing_total_volume | 汇总自明细 |

### 2.2 行 Shipment Item（LOG-003/004 承载）

| 字段 | 规则 |
| --- | --- |
| link_purchase_order / link_purchase_order_item | 必填；PO 行可分多次发运、一批次可合并多 PO 行 |
| item_code / shipped_qty（发运数量） | shipped_qty ≤ PO 行未发数量（服务端校验） |
| packing_no（箱号/包装号） / net_weight / gross_weight / volume | 包装明细（LOG-004） |
| batch_no / serial_no | 批次/序列号（INV-010 追溯上游源） |
| project | 由 Project Allocation（PO 分配记录）带出，可分配到项目级 |

### 2.3 子表式关联 Shipment Document（LOG-006 批次级单证）

| 字段 | 规则 |
| --- | --- |
| doc_type（单证类型） | 装箱单/发票/提单/原产地证/出口报关单…枚举字典待业务确认 |
| attachment / doc_version / issue_date | 文件、版本、出具日期 |
| review_status / submitted_by / reviewed_by | 审核状态、提交/审核人 |
| missing_flag / expired_flag | 缺失/过期标记（ALR-004 预警取数源） |

### 2.4 备货跟踪（LOG-001）

- `custom_supplier_production_status`（订单确认/生产中/备货完成）+ `custom_expected_completion_date`（预计完工日期）挂在 PO 行（或 Shipment 预期装载数据）；变更留痕，供 ALR-002 取数。

## 三、状态机

| 状态 | 转换条件 |
| --- | --- |
| 草稿（创建） | 可编辑 |
| 备货中 | 供应商确认（LOG-001 状态联动） |
| 已发运 | 记录 actual_ship_date + 单证齐备（出口组）校验可配置 |
| 在途 | 承接 S4 物流节点维护（LOG-005） |
| 部分到港/全部到港 | 按 Import/物流事件更新 |
| 完成 / 异常 | 异常态触发 LOG-007（S4 详设），恢复后回原态 |

## 四、任务分解

| 任务号 | 任务 |
| --- | --- |
| TP-LOGIMP-001-01 | 三件套 DocType 创建 + PO 行未发数量校验 |
| TP-LOGIMP-001-02 | 装运状态机 Workflow + 修订 ETA 留痕 |
| TP-LOGIMP-001-03 | Shipment Document 子表 + 单证类型字典 + 缺失/过期标记 |
| TP-LOGIMP-001-04 | 备货跟踪字段挂 PO 行 + 变更留痕 |
| TP-LOGIMP-001-05 | 装运汇总/明细标准报表（按 PO、按项目、按供应商） |
| TP-LOGIMP-001-06 | 示例数据：1 个合并批次（2 PO）+ 1 个分批发运（1 PO 行拆 2） |

## 五、验收用例

| 用例 | 通过标准 |
| --- | --- |
| UC-S01 | 装运数量超 PO 行未发数量被拒 |
| UC-S02 | 一 PO 行拆两个批次，累计发运正确 |
| UC-S03 | 合并批次含两家供应商/多 PO 行，明细各自追溯完整 |
| UC-S04 | ETA 修订后历史记录可查 |
| UC-S05 | 单证缺失标记可被预警取数（占位验证） |

## 六、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| S2-S1 | 单证类型完整枚举清单 | 业务方提供 |
| S2-S2 | 装运编号规则确认（SH-YYYY-流水是否采用） | 业务方确认 |
| 接口 | Import Case 与 Shipment 的关联字段（TP-LOGIMP-002 内承接） |
