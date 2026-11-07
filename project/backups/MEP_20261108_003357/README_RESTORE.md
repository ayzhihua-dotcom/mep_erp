# MEP 系统版本备份节点

- 备份编号：**20261108_003357**
- 备份时间：2026-11-08 00:33（容器时间）
- 备份类型：站点数据库 + 公共文件 + 私有文件 + 站点配置 + 自定义应用代码快照
- 适用站点：`dev.localhost`（cb_dev 环境）

## 目录内容

| 文件 | 说明 |
|---|---|
| `dev_localhost-database.sql.gz` | 数据库完整备份（MariaDB dump，gzip） |
| `dev_localhost-files.tar` | 公共文件（附件、图片等） |
| `dev_localhost-private-files.tar` | 私有文件（备份、私有附件等） |
| `dev_localhost-site_config_backup.json` | 站点配置（含数据库连接等敏感信息，注意保管） |
| `cb_erp_code_20261108_003357.zip` | 自定义应用代码 + compose.yaml + config + 项目文档台账 + 评估意见 |
| `MANIFEST.txt` | 文件大小与 SHA256 校验清单 |

## 恢复前注意

1. **先停业务/停容器写入**，避免恢复过程中产生新数据。
2. 建议先恢复到一个临时站点验证，再覆盖正式站点。
3. `site_config_backup.json` 含敏感信息，不要外传。
4. 本备份是 2026-11-08 的节点；恢复后该时间点之后的新数据会丢失。

## 恢复步骤（站点）

```bash
# 1) 把备份文件放回服务器（示例路径）
#    /home/frappe/frappe-bench/sites/dev.localhost/private/backups/

# 2) 恢复数据库 + 文件（先确认站点存在）
cd /home/frappe/frappe-bench
bench --site dev.localhost --force restore \
  /path/dev_localhost-database.sql.gz \
  --with-files /path/dev_localhost-files.tar

# 3) 如果私有文件未随 --with-files 恢复，手动解压
#    tar -xf dev_localhost-private-files.tar -C sites/dev.localhost/private/files/

# 4) 清理缓存
bench --site dev.localhost clear-cache
bench --site dev.localhost migrate

# 5) 重启
docker restart cb_dev-backend-1
```

> 若使用 Docker，请把备份文件先 `docker cp` 进容器，再执行 bench 命令。

## 恢复步骤（代码）

1. 备份当前 `环境搭建/stacks/dev/apps/cb_erp`（改名或复制）；
2. 解压 `cb_erp_code_20261108_003357.zip`，把 `cb_erp` 目录覆盖到 `环境搭建/stacks/dev/apps/cb_erp`；
3. 执行：
```bash
bench --site dev.localhost clear-cache
bench build --app cb_erp
docker restart cb_dev-backend-1
```

## 恢复后检查

- 登录 `/desk` 是否进入 MEP 工作台；
- 检查「单据总台账」「MEP 项目库存余额」「MEP 物料流水」能否打开；
- 检查侧栏、高级功能页、权限是否正常；
- 抽查 1 个项目、1 张采购订单、1 张领用单、1 张盘点单。

## 说明

- 这是**版本节点**，不是自动每日备份；建议后续配置每日自动备份 + 定期恢复演练。
- 历史备份节点另有 `环境搭建/backups/2026-11-07/`（20261107_100408）。
