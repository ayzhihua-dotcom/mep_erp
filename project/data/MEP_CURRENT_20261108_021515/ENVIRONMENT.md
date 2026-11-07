# 环境与版本信息

采集时间：2026-11-08 02:15（容器时间）

## 站点

| 项 | 值 |
|---|---|
| 访问地址 | `http://127.0.0.1:8090` |
| 站点名 | `dev.localhost` |
| Docker 项目名 | `cb_dev` |
| 默认工作区 | 巴西机电ERP系统测试（MEP 工作台） |
| 语言 | zh |

## 应用版本

| 应用 | 版本 | 仓库提交 |
|---|---|---|
| frappe | 16.54.0 | 镜像内置 |
| erpnext | 16.53.0 | 镜像内置 |
| cb_erp | 0.0.1 | `4603ab0 Initial MEP ERP application` |

## 容器镜像

| 服务 | 镜像 |
|---|---|
| backend / frontend / queue / scheduler / websocket / create-site / configurator | `frappe/erpnext:v16.53.0` |
| db | `mariadb:11.8` |
| redis-cache / redis-queue | `redis:6.2-alpine` |

## 容器与卷

运行容器（cb_dev）：

```
cb_dev-backend-1
cb_dev-dev.localhost-1        # 前端 nginx，映射 8090 -> 8080
cb_dev-websocket-1
cb_dev-queue-short-1
cb_dev-queue-long-1
cb_dev-scheduler-1
cb_dev-db-1
cb_dev-redis-cache-1
cb_dev-redis-queue-1
```

命名卷：

```
cb_dev_sites
cb_dev_assets
cb_dev_db-data
cb_dev_logs
cb_dev_redis-queue-data
```

## 挂载

```
宿主机: 环境搭建/stacks/dev/apps/cb_erp
容器:   /home/frappe/frappe-bench/apps/cb_erp
```

`sites/apps.txt` 内容：

```
cb_erp
erpnext
frappe
```

Python 路径：

```
PYTHONPATH=/home/frappe/frappe-bench/apps
```

## 数据库

| 项 | 值 |
|---|---|
| 类型 | MariaDB 11.8 |
| 库名 | 见 `site_config.json` 的 `db_name` |
| 字符集 | utf8mb4 / utf8mb4_unicode_ci |
| 备份大小 | 约 1.6 MB（gzip） |

## 当前数据概况

| 单据/配置 | 数量 |
|---|---|
| 采购申请 Material Request | 92 |
| 采购订单 Purchase Order | 82 |
| 设计 BOM Design BOM | 52 |
| 工作区链接 Workspace Link | 39 |
| 侧栏项 Sidebar Item（CB ERP） | 41 |
| 默认工作区用户 | 62 |

## 静态资源

```
sites/assets/cb_erp -> /home/frappe/frappe-bench/apps/cb_erp/public
```

`bench build --app cb_erp` 已执行；`nav_controls.js`、`sidebar_fix.js`、`batch_entry.js` 等均返回 200。

## 说明

- 前端实时服务（socket.io）在通过 `127.0.0.1:8090` 访问时会记录 `Invalid origin`，原因是容器 nginx 将 Origin 固定为 `http://dev.localhost`；不影响页面、列表和报表。
- 容器重建后请确认 `sites/apps.txt` 包含 `cb_erp`、`PYTHONPATH` 已设置、`sites/assets/cb_erp` 软链正确。
