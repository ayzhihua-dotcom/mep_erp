# 《S2 开发任务书：设计材料清单（Design BOM / TP-PRJ-001）》草案（V0.1）

- 编制依据：《ERPNext 标准能力核验与开发任务拆解》（V0.1，TP-PRJ-001）、《ERP 模块功能清单与字段字典 V0.2》（PRJ-003 / PRJ-005 / PRJ-004 / PRJ-006 衔接）、《核心业务流程与状态转换规范》（V0.1 §2.1）、《S2 开发任务书：材料主数据库（TP-MDM）》（V0.1，材料与编码规则依赖）。
- 编制日期：2026-10-28
- 状态：草稿（待开发启动评审确认）

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 任务编号 | TP-PRJ-001（对应 S2 任务包，承载 PRJ-003 + PRJ-005） |
| 覆盖功能 | PRJ-003 设计材料清单（主表与状态机）+ PRJ-005 需求日期/数量（清单行字段） |
| 明确排除 | 需求汇总/净缺口计算（PRJ-006 / PUR-002，属 TP-PRJ-004，下游）；设计变更单（PRJ-004，属 TP-PRJ-002，本任务仅定义接口） |
| 实现形态 | **自定义 DocType（非 ERPNext 制造 BOM）**：设计 BOM 与制造 BOM 语义不同，独立建模，保留 item_code 关联 |
| 前置依赖 | TP-MDM-01（材料字段就绪）；项目/WBS 骨架（S1 ④ D-3） |

## 二、DocType 设计

### 2.1 主表 Design BOM

| 字段 | 规则 |
| --- | --- |
| project | 必填；关联 Project |
| bom_list_no（清单编号） | 项目内唯一组成部分；与 version 组成唯一键 |
| version | 起始 V1.0；变更时递增（TP-PRJ-002 接口）；同 project + bom_list_no + version 唯一（PRJ-003） |
| discipline（专业） | 必填；来源于专业字典（与 Item Group 专业口径一致） |
| source_file / drawing_version | 来源设计文件、图纸版本（可空文本/附件） |
| prepared_by / reviewed_by / approved_date | 编制人、审核人、日期 |
| status | 状态机见第三节（草稿 → 已提交 → 已审核 → **锁定**） |
| 联合唯一约束 | (project, bom_list_no, version)；由服务端校验（fixture + server script） |

### 2.2 子表 Design BOM Item（承载 PRJ-005）

| 字段 | 规则 |
| --- | --- |
| item_code | 必填；Link → Item（TP-MDM 就绪材料） |
| design_qty（需求数量） | > 0 |
| uom | 默认取 Item 的 stock_uom，可改但须校验 UOM 转换关系 |
| required_date（需求日期） | 必填；单据级默认 + 行级可覆盖 |
| priority | 中/高/低（高风险关键项标高） |
| remarks / engineering_system / wbs_link | 用途说明；关联 WBS（PRJ-002 楼栋/区域/专业包） |
| lost_allowance（批准损耗率） | 行级可空；需求汇总时使用（口径冻结点见 TP-PRJ-004） |

## 三、状态机与版本规则

| 状态 | 转换条件 |
| --- | --- |
| 草稿 | 可编辑；可删除 |
| 已提交 | 提交动作；系统校验：所有行 item_code 有效、数量 > 0、需求日期必填 |
| 已审核 | 工程审核（ENG 角色，审/批如需两级由 Workflow 配置） |
| 锁定 | 已审核版本进入锁定；**锁定后不可编辑**（PRJ-003 验收要点） |
| 新版本 | 变更不覆盖旧版本：由 TP-PRJ-002 设计变更单生成 version+1 的新 Draft（差异可对照） |

规则承接《流程规范》§2.1：已审核/锁定版本不可覆盖，更正走变更流程。

## 四、与 PRJ-004（设计变更）的接口约定

| 接口点 | 约定 |
| --- | --- |
| 变更来源 | Design Change Request（TP-PRJ-002）引用 原版本 Design BOM |
| 生效方式 | 变更批准 → 生成新 version 草稿 + 差异行（原数量/新数量/差额）→ 走本任务状态机提交/审核/锁定 |
| 下游影响 | 减量且已下单/发运的行生成影响清单，转采购/项目负责人处理（TP-PRJ-002 承接） |
| 本任务预留 | Design BOM 主表提供 `change_request_link` 字段冗余存变更单引用，便于追溯 |

## 五、实施任务分解

| 任务号 | 任务 | 类型 | 依赖 |
| --- | --- | --- | --- |
| TP-PRJ-001-01 | Design BOM / Design BOM Item DocType 创建 + 联合唯一校验 | 代码 | S1 环境；M-01 冻结不阻塞（手工编码） |
| TP-PRJ-001-02 | 状态机 Workflow（草稿→提交→审核→锁定）+ 锁定字段保护 | 配置 | -01 |
| TP-PRJ-001-03 | 行级校验（通用校验：item 有效、qty>0、required_date） | 代码 | -01 |
| TP-PRJ-001-04 | 专业字典与 Item Group 对齐逻辑（专业下拉与材料分组一致） | 配置+代码 | M-01-c 提供后 |
| TP-PRJ-001-05 | change_request_link 预留 + 新版本草稿生成接口（供 TP-PRJ-002 调用） | 代码 | -01；接口先行 |
| TP-PRJ-001-06 | 示例数据：Dev 环境 1 个试点项目示例 BOM（3 份清单 × 2 版本） | 数据 | TP-MDM-07 材料就绪 |

> TP-PRJ-006（需求汇总/净缺口计算）不属本任务；但其明细来源字段（本任务保证：行数据含 item/qty/date/priority/wbs/损耗率）即其输入，需在 -01 中保持口径稳定。

## 六、验收用例

| 用例 | 步骤 | 通过标准 |
| --- | --- | --- |
| UC-P01 | 同 project+清单编号+version 重复保存 | 被拒 |
| UC-P02 | 锁定版本尝试修改行数量 | 不可编辑（要点：仅版本变更通道可变更） |
| UC-P03 | 行含无效 item 或 qty=0 提交 | 提交被拦并指出行号 |
| UC-P04 | 多版本并存查看 | V1.0 锁定只读 + V1.1 草稿可编辑，历史可回查 |
| UC-P05 | 需求日期行级覆盖 | 默认日期来自主表，行级覆盖生效 |
| UC-P06 | 与 TP-MDM 联动：material 停用后新增行 | 依据 TP-MDM-05 配置被阻断或强提示 |

## 七、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| D-y1 | 审核是否需要两级（编制→校核→审核），映射 SRS 工程管理角色 | 业务方确认 |
| D-y2 | lost_allowance 损耗率预设值与批准规则 | 与 PRJ-006/PUR-002 口径统一后确认（归 TP-PRJ-004 / D 决策） |
| M-04（引用） | 材料样本 | 影响 TP-PRJ-001-06 验收数据 |
