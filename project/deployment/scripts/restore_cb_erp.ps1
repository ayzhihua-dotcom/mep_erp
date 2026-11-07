param(
    [string]$proj = "cb_dev",
    [string]$site = "dev.localhost"
)
Write-Output "== PARAM == " # proj=$proj site=$site
# cb_erp 应用恢复脚本（栈 down/up 或容器重建后执行一次）
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File .\restore_cb_erp.ps1 [-proj cb_dev] [-site dev.localhost]
# 前提: compose.yaml 已挂 ./apps → backend 的 apps/cb_erp；后端容器 Up
# 原理: apps 内代码随绑卷自恢复，但 env 的 editable 注册与 sites/apps.txt 属容器/卷旧态，需本脚本补
Write-Output "== 0) 补日志目录（v16 运行时路径，重建后缺失即报错） =="
docker compose -p $proj exec -T backend bash -c "mkdir -p /home/frappe/logs /home/frappe/frappe-bench/$site/logs 2>/dev/null; echo logs-dirs-ok"
Write-Output "== 1) 补 sites/apps.txt 卷内登记（缺 cb_erp 会 ModuleNotFoundError） =="
docker compose -p $proj exec -T backend bash -c "cd /home/frappe/frappe-bench && grep -qx cb_erp sites/apps.txt || printf 'cb_erp\n' >> sites/apps.txt; cat sites/apps.txt"
Write-Output "== 2) env 级 pip -e 注册 cb_erp（必须用 env/bin/pip，系统 pip 不进站点环境） =="
docker compose -p $proj exec -T backend bash -c "cd /home/frappe/frappe-bench && env/bin/pip install -e apps/cb_erp 2>&1 | tail -1"
Write-Output "== 3) 前端资源构建 + 物化（frappe/erpnext assets 原为 symlink 指各自镜像层，须解为共享卷实体） =="
docker compose -p $proj exec -T backend bash -c "cd /home/frappe/frappe-bench/assets && for app in frappe erpnext; do if [ -L `$app ] || [ -d `$app ]; then cp -aL `$app `/tmp/real_`$app && rm -rf `$app && mv `/tmp/real_`$app `$app; fi; done; echo materialized; bench build --app cb_erp 2>&1 | tail -2"
Write-Output "== 4) 清缓存 + 重启 backend（让已启动的 gunicorn 重新加载 cb_erp） =="
docker compose -p $proj exec -T backend bash -c "cd /home/frappe/frappe-bench && bench --site $site clear-cache 2>&1 | tail -1"
docker compose -p $proj restart backend | Out-Null
Start-Sleep -Seconds 25
Write-Output "== 5) 导入自检 =="
docker compose -p $proj exec -T backend bash -c "cd /home/frappe/frappe-bench && env/bin/python -c 'import cb_erp' && echo IMPORT-OK"
Write-Output "== 6) 站点探测 =="
docker compose -p $proj exec -T $site bash -c "curl -s -o /dev/null -w 'login-http=%{http_code}\n' http://$($site):8080/login"
Write-Output "== DONE =="
