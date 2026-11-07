# 《S2 开发任务书：材料主数据库（TP-MDM）》草案（V0.1）

- 编制依据：《ERPNext 标准能力核验与开发任务拆解》（V0.1，TP-MDM 承接 MDM 域）、《ERP 模块功能清单与字段字典 V0.2》（MDM-001 ~ MDM-009）、《S1 交付物：主数据初始化规范》（V0.1，D-4~D-6、M-01）、《S1 交付物：三语基础配置方案》（V0.1，D-11）。
- 编制日期：2026-10-28
- 状态：草稿（M-01 编码规则待业务确认项置前，冻结前不开发编码自动生成逻辑）

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 任务编号 | TP-MDM（对应 S2 首批任务包） |
| 覆盖功能 | MDM-001 统一编码 / 002 三语名称 / 003 规格 / 004 单位 / 005 供应商映射 / 006 进口属性 / 007 批量导入 / 008 档案变更 / 009 材料停用 |
| 交付边界 | Item 及配套字段、Item Group、UOM、供应商映射、批量导入通道、变更审计、停用流程；不含采购/库存交易功能 |
| 阶段 | S2（主数据与采购核心开发） |

## 二、前置确认项（M-01，置前约束开发）

| 决策项 | 内容 | 未决期间的处理 |
| --- | --- | --- |
| M-01-a 编码结构 | "大类-专业-流水"（如 JX-JD-0001）是否采用 | **不开发自动编码逻辑**；编码采用手工录入 + 唯一性校验先行，规则冻结后补充自动生成器（不阻塞后续任务） |
| M-01-b 编码唯一范围 | 全.company 全局唯一 vs 公司内唯一 | 默认全局唯一（建议），与 MDM-001 一致 |
| M-01-c 材料大分类字典 | 大类/专业的枚举清单 | 业务方提供（可复用 Item Group 分组结构承载） |

## 三、字段设计清单

### 3.1 Item 标准字段复用

| 字段 | 承载 |
| --- | --- |
| item_code / item_name / item_group / stock_uom / disabled / is_stock_item | MDM-001 / 004 / 009 |
| description | 中文名称长描述（中文） |
| manufacturers / brand（或 custom brand） | MDM-003 品牌、型号 |

### 3.2 自定义字段（cb_erp 定制，fixtures 交付）

| 字段（建议 fieldname） | 功能编号 | 说明 |
| --- | --- | --- |
| custom_item_name_zh | MDM-002 | 中文名（可由 item_name 代表，二选一览 B-确认） |
| custom_item_name_pt / custom_item_name_en | MDM-002 | 葡/英名称，可后补 |
| custom_spec_material | MDM-003 | 材质 |
| custom_spec_dimension | MDM-003 | 尺寸（含长度/口径等说明文本） |
| custom_spec_model | MDM-003 | 型号 |
| custom_spec_pressure | MDM-003 | 压力等级（适用物料组） |
| custom_spec_standard | MDM-003 | 执行标准 |
| custom_ncm_code | MDM-006 / IMP-003 | 巴西 NCM 码（进口材料必填或"待归类审核"态） |
| custom_ncm_basis_text | IMP-003 | 归类依据 |
| custom_ncm_status | IMP-003 | 归类审核状态（待归类 / 人工已确认） |
| custom_ncm_history | IMP-003 | 归类变更历史：采用 track_changes/Versioning 承载，不另建新表 |
| custom_country_of_origin | MDM-006 | 原产国 |

> 供应商映射（MDM-005）使用 Item 标准子表 Item Supplier Details：`supplier + supplier_part_no` 唯一约束（脚本/fixture 校验）；自动匹配候选、人工确认合并的逻辑列 TP-MDM-02。

### 3.3 唯一性与其他校验

- item_code 全局唯一（标准已有）；
- Item Group 层级承载大类/专业字典（M-01-c）；
- 库存类材料 stock_uom 必填；
- 强制质检标志（quality inspection template 相关）默认继承至收货流程（INV-003 衔接）。

## 四、实施任务分解

| 任务号 | 任务 | 类型 | 依赖 |
| --- | --- | --- | --- |
| TP-MDM-01 | Item 12 个自定义字段 fixtures + DocType 整理 + 权限（按 S1 ② 矩阵） | 配置+代码 | S1 ①环境就绪 |
| TP-MDM-02 | Item Supplier Details 唯一性约束 + 自动匹配候选清单（脚本/报表） | 代码 | TP-MDM-01 |
| TP-MDM-03 | 批量导入通道（承接 ALR-005 口径）：模板、预览校验、失败行下载、幂等重跑 | 代码 | TP-MDM-01 |
| TP-MDM-04 | 档案变更审计：track_changes 开启 + 关键字段变更审批流（MDM-008，或简化为记录前后值+原因） | 配置+代码 | TP-MDM-01 |
| TP-MDM-05 | 材料停用流程（MDM-009）：disabled + 停用校验（有在途需求/订单时警示或阻断） | 配置 | TP-MDM-01 |
| TP-MDM-06 | 三语完整率报表（Item 中文100% / 葡英完整率） | 报表 | TP-MDM-01 |
| TP-MDM-07 | Dev 主数据初始化执行（D-4~D-6 规格）：20~50 条示例材料 + 分组 + UOM + 3~5 家供应商 | 数据 | TP-MDM-01 + M-04 样本到位 |

## 五、验收用例

| 用例 | 步骤 | 通过标准 |
| --- | --- | --- |
| UC-M01 | 重复编码录入 | 被拒，提示唯一性 |
| UC-M02 | 三语切换：同一条 Item 在 zh/pt/en 用户下查看名称 | pt/en 缺失时回退中文；完整时对应语言显示 |
| UC-M03 | 供应商重复料号约束：同 supplier+part_no 重复保存 | 被拒 |
| UC-M04 | 批量导入：含错误行的文件导入 | 预览→错误行报告→修正后重跑不重复写入（幂等） |
| UC-M05 | 停用材料再入采购申请 | 依据配置被阻断或强提示 |
| UC-M06 | 修改 NCM 后查看变更历史 | 前后值、修改人、时间可见 |
| UC-M07 | 三语完整率报表运行 | 中文 100%，葡/英比例正确 |

## 六、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| M-01-a/b/c | 编码规则系列 | 业务方确认；冻结前不开发自动编码 |
| M-04 | 材料样本清单 | 业务方提供后执行 TP-MDM-07 |
| B-确认 | custom_item_name_zh 是否独立字段（还是直接用 item_name） | 开发启动会确认（建议直接用 item_name，避免双写） |
