# MEP ERP（Frappe / ERPNext 自定义应用）

面向机电安装/EPC 项目的材料与项目管控应用：以设计 BOM 为源头，串联请购、采购、到货、领用、安装，并提供项目、质量、文档与台账报表。

## 功能概览

- **工程与预算**：设计 BOM、设计变更、材料预算、材料承诺
- **采购与库存**：采购申请、采购订单、采购入库、库存移动（领用/退料）、库存盘点
- **项目执行**：项目专业/系统、任务、安装记录、试运行/移交
- **质量**：质检单、质检模板、NCR（不合格报告）
- **报表**：物资四量台账、采购与领用台账、单据总台账、项目库存余额、物料流水、项目文档台账、项目专业系统矩阵
- **批量能力**：Excel/CSV 导入、粘贴、从 BOM 生成、按缺口生成
- **受控分级**：项目三态（不管控 / 只管控受控物料 / 全管控），物料受控标记
- **界面**：MEP 工作台、分组侧栏、高级功能页、深页专注模式

## 仓库结构

```
cb_erp/
├─ cb_erp/                 # 应用主体（Python / DocType / 报表 / 页面）
│  ├─ page/                # 自定义页面（mep-advanced、ops-console）
│  ├─ cb_erp/              # 业务模块（linkage/quota/bulk_ops 等）
│  ├─ hooks.py
│  └─ patches.txt
├─ public/                 # 前端 JS / CSS / 图片
├─ deploy/                 # 部署示例（不含真实密码）
├─ README.md
└─ .gitignore
```

## 环境要求

- Frappe Framework v16.x
- ERPNext v16.x
- MariaDB 11.x / Redis 6.x
- Docker（可选，见 `deploy/compose.example.yaml`）

## 安装（已有 bench 环境）

```bash
# 1) 将本仓库放入 bench 的 apps 目录
cd /home/frappe/frappe-bench/apps
git clone <repo-url> cb_erp

# 2) 安装应用
cd /home/frappe/frappe-bench
bench --site your.site install-app cb_erp
bench --site your.site migrate
bench build --app cb_erp
bench --site your.site clear-cache
```

## Docker 部署

复制示例并填写环境变量（不要把真实密码提交到仓库）：

```bash
cp deploy/.env.example deploy/.env
# 编辑 deploy/.env
docker compose -f deploy/compose.example.yaml --env-file deploy/.env up -d
```

> `compose.example.yaml` 中的数据库/管理员密码使用环境变量占位，仓库中不包含任何真实凭据。

## 数据与安全

- 本仓库**不包含**数据库、附件、站点配置、备份文件或任何密码。
- 请勿把 `site_config.json`、`.env`、`*.sql.gz`、`*.tar` 提交到 Git。
- 生产环境请使用独立的数据库账号、强密码、备份与恢复演练。

## 许可证

内部项目代码；如需开源请先补充 LICENSE 并确认业务代码授权。
