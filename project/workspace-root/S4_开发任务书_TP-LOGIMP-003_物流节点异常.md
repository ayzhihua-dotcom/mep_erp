# 《S4 开发任务书：物流节点、异常与到货预测（TP-LOGIMP-003）》草案（V0.1）

- 编制依据：V0.2 字段字典（LOG-005 / 007 / 008 / IMP-007 / 008~010），S2 TP-LOGIMP-001/002（基础对象已建）。
- 编制日期：2026-10-28
- 状态：草稿

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 覆盖功能 | LOG-005 运输节点、LOG-007 运输异常、LOG-008 到货预测、IMP-007 清关异常、IMP-008 三事件补全、IMP-009 成本关联接口确认、IMP-010 进口归档 |
| 实现形态 | Shipment Transport Milestone / Exception 子对象 + Import Case 收尾逻辑 |

## 二、功能设计

### 2.1 运输节点（LOG-005）

| 字段 | 规则 |
| --- | --- |
| node_type | 订舱 / 发运 / 到港 / 提取 / 境内运输节点 |
| planned_time / actual_time / updated_time / source / responsible | 计划/实际/更新时间、信息来源（代理/承运商/人工）、责任人 |
| is_abnormal | 异常标记 |

### 2.2 异常管理（LOG-007 / IMP-007 统一对象 Supply Chain Exception）

| 字段 | 规则 |
| --- | --- |
| exception_type | 延误 / 短装 / 货损 / 改单 / 额外费用 / 查验 / 单证差异 / 补税 / 滞港 |
| affected_object / severity | 关联单据（Shipment/Import Case/PO）+ 严重度 |
| description / evidence附件 | 描述与证据 |
| assignee / due_date / status（待处理→处理中→已关闭） | 分派与闭环，处理结论留痕 |

### 2.3 到货预测（LOG-008）

| 规则 |
| --- |
| 预计到货 = 计划 ETA → 随最新物流事件（节点 actual_time 承诺）刷新 |
| 变更覆盖规则：每次刷新为新版本记录（旧值保留），偏差显示；台账另给"历次 ETA 时间线" |
| 联动：ETA 推迟落库通知（S5 正式 ALR-002 激活时统一处理） |

### 2.4 进口收尾（IMP-008 / 010）

- 三事件（放行/提货/验收）已在 S2 Milestone 承载，本任务补：事件证据链完整性校验放规则（放行前各 milestone 必须闭环）；
- 归档（IMP-010）：案件关闭检查（单证齐备+费用结清+异常结清）→ 归档态 → 附件锁定只读。

## 三、任务分解

| 任务号 | 任务 |
| --- | --- |
| TP-LOGIMP-003-01 | Transport Milestone + Exception 通用对象（LOG/IMP 共用子类） |
| TP-LOGIMP-003-02 | ETA 计算与留痕版本线 |
| TP-LOGIMP-003-03 | 异常分派/闭环 Workflow + 证据附件 |
| TP-LOGIMP-004/IMP 归档 | 案件关闭检查清单 + 归档态锁定 |
| TP-LOGIMP-003-05 | 物流总览看板（在途批次 × 节点状态 × ETA × 异常计数） |
| TP-LOGIMP-003-06 | 示例：延误异常 → 改派（分派）→ ETA 更新 → 预警占位链路 |

## 四、验收用例

| 用例 | 通过标准 |
| --- | --- |
| UC-L01 | 异常创建关联对象并分派，处理收益闭环时间可查 |
| UC-L02 | ETA 多次更新形成时间线，最新 ETA 可供关联计算 |
| UC-L03 | 证据缺失时异常不可关闭（配置级） |
| UC-L04 | 归档检查未结清事项被拦 |
| UC-L05 | 三事件证据链不全时归档被拦 |

## 五、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| S4-L1 | exception_type 权威字典与严重度分级 | 业务确认 |
| S4-L2 | ETA 刷新来源（人工 vs 代理对接接口） | 与 O-01 / 接口规范衔接 |
