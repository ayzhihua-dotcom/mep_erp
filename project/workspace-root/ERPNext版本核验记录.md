# 《ERPNext 版本核验记录》正式版（V1.0）

- 核验日期：2026-10-28；核验方式：GitHub 官方 Releases API 在线核验 + 官方能力清单比对
- 关闭事项：L-02（SRS 阶段门带出的 ERPNext 目标版本核验）
- 状态：**已核验冻结**（版本基线；环境实例化后小版本按 CI 实测复核）

## 一、核验结论登记

| 项 | 结果 |
| --- | --- |
| 选定大版本 | **ERPNext v16 主线**（现行稳定主版本；v15 仍在维护作为回退线） |
| 冻结基线 | ERPNext **v16.53.0**（version-16 分支，2026-10-28 发布） |
| 框架配套 | Frappe Framework **v16.54.0**（version-16，2026-10-27 发布） |
| 部署镜像 | frappe-docker 按版本标签拉取（erpnext:v16 系列） |
| 回退线 | v15.124.2（version-15，同日仍在发布维护） |
| 核验证据 | GitHub Releases（frappe/erpnext、frappe/frappe），标签与日期均已留存 |
| 核验人 | 本轮代理核验（技术预审）；正式签字区见第五节 |

## 二、七项能力核验结果

| # | 核验项 | 结论 | 说明 |
| --- | --- | --- | --- |
| 1 | Workflow 多级审批流 | ✅ v16 具备 | 原生 Workflow/Workflow Action Master 支持多级与条件转换；金额阈值条件用 Workflow Condition 脚本条件实现 |
| 2 | Quality Inspection 强制检验前置 | ✅ v16 具备 | 检验模板 + 单据强制检验配置，未检不入库可用"待检仓流转"方案兜底 |
| 3 | Landed Cost Voucher 分摊 | ✅ v16 具备 | 分摊基础标准支持（数量/金额/重量/体积），满足 CST-004（TP-CST-C-02 定制项为通道与项目拆分） |
| 4 | Stock Reconciliation 盘点 + track_changes | ✅ v16 具备 | 盘点恢复/期初双用途；重大差异二级审批走定制 Workflow |
| 5 | 多语言 / 多币种 | ✅ v16 具备 | zh 官方翻译包随版本维护（完整度实测列 P-T4 复核项）；CNY/BRL/USD 多币种原生 |
| 6 | Project + Custom Fields + User Permission | ✅ v16 具备 | 数据范围（Company/Warehouse/Project reference）原生支持，承载 S1 ② 矩阵 |
| 7 | 备份恢复与升级路径 | ✅ v16 具备 | bench backup/restore 与 docker 流程随版本维护；半年度小版本升级窗口（S4 终案 §升级通道） |

## 三、与既有文档的联动更新

| 承接点 | 更新 |
| --- | --- |
| S1 ① 版本选型节 | 候选主线 → v16 冻结（本记录为准） |
| S2 任务书 | "版本核验后确认"类表述自动满足；DocType 能力按 v16 标准编写 |
| S4 交付物（部署终案） | 生产镜像基线 = erpnext v16.53.0 / frappe v16.54.0 |
| 容量与依赖 | MariaDB/Redis 版本以 frappe-docker v16 镜像组内默认为准（实例化时登记） |
| P-T4 | 官方中文翻译完整度 → Dev 实例化后实测（维持开放项） |

## 四、遗留开放项

| 编号 | 事项 | 处理 |
| --- | --- | --- |
| R-01 | 小版本升级策略（跟随 v16 补丁版节奏，建议每季度窗口） | S4 部署 runbook 细化 |
| R-02 | Dev 实例化后复核七项能力实测 + zh 翻译完整度 | ✅ **2026-10-29 实测闭环**（见下） |

**R-02 闭环实测记录（2026-10-29）**：
- 容器内 `bench version` 实测：**erpnext 16.53.0 / frappe 16.54.0**（与冻结基线逐字符一致，镜像摘要 sha256:74180ed8…）；
- MariaDB 11.8（healthy）/ Redis 6.2-alpine（镜像组默认，已登记第二节口径）；
- 官方翻译完整度实测（P-T4 同步闭环）：**zh 16802 条 / pt 16315 条 / en 43 条（基准语言，正常）**——D-11 三语策略的 zh/pt 官方包层面完整度充足；
- Dev/Test 双站点实测登录（Administrator + 10 示例账号 REST）全部 HTTP 200；
- Test 恢复演练后数据完整性验证通过（公司×2 / Item×3 / 仓库×14 / 用户×10 / 语言 zh）。

## 五、签字区

技术负责人（____）；项目经理（____）；日期（____）。
