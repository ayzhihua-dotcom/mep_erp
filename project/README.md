# MEP 完整项目快照

本目录是 MEP ERP 项目在 **2026-11-08 当前验证通过版本** 的完整快照，包含代码、部署、文档、历史备份和全量数据。

> 仓库为 **Private**。本目录包含真实数据库、站点配置、密码/密钥、业务数据，请勿公开或外传。

## 目录结构

```
project/
├─ README.md                  # 本文件
├─ data/
│  └─ MEP_CURRENT_20261108_021515/   # 当前版本全量数据（推荐恢复点）
│     ├─ dev_localhost-database.sql.gz      # 数据库完整 dump
│     ├─ dev_localhost-files.tar            # 公共文件
│     ├─ dev_localhost-private-files.tar    # 私有文件
│     ├─ dev_localhost-site_config_backup.json
│     ├─ site_config.json                   # 当前站点配置（含密钥）
│     ├─ common_site_config.json            # 公共配置（DB/Redis）
│     ├─ apps.txt                           # 已挂载应用
│     ├─ cb_erp_code_MEP_CURRENT_*.zip      # 应用代码快照（HEAD）
│     ├─ ENVIRONMENT.md                     # 版本/容器/环境信息
│     ├─ README_RESTORE.md                  # 恢复步骤
│     └─ MANIFEST.txt                       # SHA256 校验
├─ backups/                   # 历史备份节点
│  ├─ 2026-11-07/             # 20261107_100408
│  └─ MEP_20261108_003357/    # 整库回滚使用的节点
├─ deployment/
│  ├─ dev/                    # cb_dev 开发栈 compose + 历史工作脚本/日志
│  ├─ test/                   # cb_test 测试栈 compose
│  └─ scripts/                # 启动、初始化、恢复脚本
├─ workspace-root/            # 工作区根目录全部文档、台账、脚本
└─ legacy/                    # 早期原型（inventory_desktop / inventory_management）
```

## 与运行环境的关系

- 应用代码就是本仓库根目录（`hooks.py`、`cb_erp/`、`public/` 等），运行中的容器挂载为：
  ```
  环境搭建/stacks/dev/apps/cb_erp  →  /home/frappe/frappe-bench/apps/cb_erp
  ```
- 当前验证版本：`4603ab0 Initial MEP ERP application`
- 当前数据版本：`MEP_CURRENT_20261108_021515`
- 技术 app id 仍为 `cb_erp`；产品/界面名为 MEP。

## 恢复

优先使用 `data/MEP_CURRENT_20261108_021515/README_RESTORE.md` 中的步骤。

简要流程：

```bash
# 1) 数据库 + 文件
bench --site dev.localhost --force restore \
  dev_localhost-database.sql.gz \
  --with-public-files dev_localhost-files.tar \
  --with-private-files dev_localhost-private-files.tar \
  --db-root-username root --db-root-password=<root 密码>

# 2) 清缓存 + 构建资源
bench --site dev.localhost clear-cache
bench build --app cb_erp

# 3) 确认静态资源软链
readlink -f sites/assets/cb_erp
# 必须是 .../apps/cb_erp/public
```

## 说明

- 未纳入版本库的内容：`.git` 内部对象、`__pycache__`、`*.pyc`、Docker 命名卷的原始二进制（数据已通过 SQL dump + files tar 完整归档）。
- Docker 卷：`cb_dev_sites`、`cb_dev_assets`、`cb_dev_db-data`、`cb_dev_logs`、`cb_dev_redis-queue-data`。
- 本站点数据量很小（数据库 dump 约 1.6 MB，附件 10 KB），所有业务单据均在 dump 中。
