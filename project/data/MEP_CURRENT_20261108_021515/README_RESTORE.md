# 当前版本数据备份节点

- 备份编号：**MEP_CURRENT_20261108_021515**
- 备份时间：2026-11-08 02:15（容器时间）
- 备份类型：站点数据库 + 公共文件 + 私有文件 + 站点配置 + 应用代码快照
- 适用站点：`dev.localhost`（cb_dev 环境）
- 状态：已完成界面与功能验证，作为当前阶段基准版本

## 文件说明

| 文件 | 说明 |
|---|---|
| `dev_localhost-database.sql.gz` | 数据库完整备份（MariaDB dump，gzip，约 1.6 MB） |
| `dev_localhost-files.tar` | 公共文件（附件、图片等） |
| `dev_localhost-private-files.tar` | 私有文件 |
| `dev_localhost-site_config_backup.json` | bench 生成的站点配置备份 |
| `site_config.json` | 当前站点配置（含 db_password、encryption_key） |
| `common_site_config.json` | 当前公共配置（DB/Redis/socketio） |
| `apps.txt` | 当前已安装应用列表 |
| `cb_erp_code_20261108_021515.zip` | 应用代码快照（仓库 HEAD `4603ab0`） |
| `ENVIRONMENT.md` | 版本、容器、访问地址 |
| `MANIFEST.txt` | 文件大小与 SHA256 |

> 本节点包含真实业务数据与敏感配置，仅用于私有仓库/内部恢复。

## 恢复步骤（数据库 + 文件）

```bash
# 0) 建议先停止写入：停止 queue / scheduler / websocket，保留 db 与 backend
docker stop cb_dev-queue-long-1 cb_dev-queue-short-1 cb_dev-scheduler-1 cb_dev-websocket-1 cb_dev-dev.localhost-1

# 1) 把备份文件复制进容器
docker cp dev_localhost-database.sql.gz   cb_dev-backend-1:/tmp/mep_restore/db.sql.gz
docker cp dev_localhost-files.tar         cb_dev-backend-1:/tmp/mep_restore/files.tar
docker cp dev_localhost-private-files.tar cb_dev-backend-1:/tmp/mep_restore/private-files.tar

# 2) 恢复（密码使用容器内 MYSQL_ROOT_PASSWORD）
docker exec cb_dev-backend-1 sh -c 'cd /home/frappe/frappe-bench && \
  bench --site dev.localhost --force restore /tmp/mep_restore/db.sql.gz \
    --with-public-files /tmp/mep_restore/files.tar \
    --with-private-files /tmp/mep_restore/private-files.tar \
    --db-root-username root --db-root-password="$MYSQL_ROOT_PASSWORD"'

# 3) 缓存与资源
docker exec cb_dev-backend-1 sh -c 'cd /home/frappe/frappe-bench && \
  bench --site dev.localhost clear-cache && bench build --app cb_erp'

# 4) 启动
docker start cb_dev-dev.localhost-1 cb_dev-websocket-1 cb_dev-queue-short-1 cb_dev-queue-long-1 cb_dev-scheduler-1
```

## 恢复步骤（代码）

1. 解压 `cb_erp_code_20261108_021515.zip`；
2. 覆盖到 `环境搭建/stacks/dev/apps/cb_erp`（保留 `.git` 时请先备份）；
3. `bench build --app cb_erp`、`bench --site dev.localhost clear-cache`；
4. 重启 backend / frontend。

## 关键检查

```bash
# 静态资源软链必须指向 apps/cb_erp/public
readlink -f /home/frappe/frappe-bench/sites/assets/cb_erp

# 应用导入
docker exec cb_dev-backend-1 sh -c 'cd /home/frappe/frappe-bench && ./env/bin/python -c "import cb_erp; print(cb_erp.__file__)"'
```

恢复后确认：

- `/desk` 进入 **MEP 工作台**；
- 顶部 `⌂ MEP / 返回 / 前进 / 高级 / 菜单` 正常；
- 高级功能页 36 个入口；
- 侧栏 9 个分组；
- 采购申请等列表正常；
- `/assets/cb_erp/*` 无 404。

## 站点配置

- 访问地址：`http://127.0.0.1:8090`
- 站点名：`dev.localhost`
- 数据库：MariaDB 11.8，库名/账号见 `site_config.json`
- 应用：frappe 16.54.0 / erpnext 16.53.0 / cb_erp 0.0.1
- Docker 项目名：`cb_dev`
