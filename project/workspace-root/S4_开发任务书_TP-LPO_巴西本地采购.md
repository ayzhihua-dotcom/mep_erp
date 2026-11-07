# 《S4 开发任务书：巴西本地采购（TP-LPO）》草案（V0.1）

- 编制依据：V0.2 字段字典（LPO-001 ~ 007）、《数据库关联与权限设计》（BRA 角色范围）、TP-MDM（CNPJ 字段）、SRS §本地采购。
- 编制日期：2026-10-28
- 状态：草稿

## 一、任务定位

| 项 | 内容 |
| --- | --- |
| 覆盖功能 | LPO-002 本地询价、LPO-003 本地订单、LPO-004 到货衔接、LPO-005 发票关联、LPO-006 本地费用、LPO-007 中巴对比 |
| 实现原则 | 复用 PUR 域全套流程（RFQ/SQ/PO/PR/PI），加"本地标识 + 巴西税务口径 + 中巴对比"三层定制 |

## 二、功能设计

### 2.1 本地标识（LPO-003）

| 字段 | 规则 |
| --- | --- |
| sourcing_region | Purchase Order / RFQ / Supplier 主档增加 sourcing_region（China / Brazil Local） |
| 规则联动 | BRA 角色仅允许出现在 sourcing_region=Brazil Local 的单据范围；PRC 同理 China |

### 2.2 本地询价与税务口径（LPO-002）

| 字段 | 规则 |
| --- | --- |
| tax_scenario（税务口径） | SQ/PO 端 `custom_tax_scenario`：PTS 含税 / NT 未税 + 全套 BRL 上下文（ICMS/IPI/PIS/COFINS 汇报行，行级税额按ibeix 文案配置 tax template 承载——具体税率模板经财务确认） |
| delivery_terms 本地交货条件 | 适用 RAD/现场提货；Incoterm 为空约束 |
| 有效期 | 承接 TP-PUR 通用过期/选用机制 |

### 2.3 到货与发票（LPO-004 / 005）

- 到货：走 TP-INV-001 统一收货入口（sourcing_region 一致性校验）；
- 发票关联：本地 PI（Purchase Invoice）必关联 PO + 附件（巴西 Nota Fiscal 电子发票号 custom_nf_e 字段预留对接）。

### 2.4 本地费用（LPO-006）

- 运输/等服务费：费用类型字典 + 归集（Landed Cost 或项目杂费口径，对接 S5 分摊通道）。

### 2.5 中巴对比（LPO-007）

| 维度 | 数据来源 |
| --- | --- |
| 同 Item 成本 | 最近中调采购 SQ/PO 单价（CNY→BRL 折算） vs 本地报价（BRL） |
| 交期 | 中国线（承诺+装运+清关+入仓） vs 本地承诺 |
| 技术 | 同规格可达率（规格字段相似度人工可判，作辅助列） |
| 输出 | 对比报表（手动触发或选品时调用） |

## 三、任务分解

| 任务号 | 任务 |
| --- | --- |
| TP-LPO-01 | sourcing_region 标识贯通 + 角色范围联动校验 |
| TP-LPO-02 | 税务口径字段 + 税模板位（财务确认后配置） |
| TP-LPO-03 | 交货条件与 Incoterm 约束校验 |
| TP-LPO-04 | Nota Fiscal 字段预留 + 发票-收货-订单三方关联 |
| TP-LPO-05 | 本地费用类型与归集通道 |
| TP-LPO-06 | 中巴对比报表 |
| TP-LPO-07 | 示例：本地 RFQ → 含税 SQ → PO → 收货 → NF 关联全链 |

## 四、验收用例

| 用例 | 通过标准 |
| --- | --- |
| UC-BR01 | BRA 角色只可见/操作 Brazil Local 单据范围 |
| UC-BR02 | 本地订单缺税务口径或带 Incoterm 被拦 |
| UC-BR03 | 发票与订单/收货三方金额一致性校验 |
| UC-BR04 | 中巴对比报表单包装导出 |
| UC-BR05 | 本地费用归集通道可入项目成本（联调 S5） |

## 五、遗留待办

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| S4-BR1 | 巴西税模板时间（II/IPI/PIS/COFINS/ICMS 组合税率） | 财务/清关方确认 |
| S4-BR2 | Nota Fiscal 电子发票系统对接范围（本期仅登记 vs 对接 SEFAZ） | 依赖 O-01 + 业务决策 |
| S4-BR3 | 中巴对比的币种折算汇率口径 | 业务确认（与 M-02 汇率策略统一） |
