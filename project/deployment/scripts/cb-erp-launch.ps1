# Rebuild-safe runbook for CB-ERP Dev/Test stacks (ASCII-only script)
# Usage: powershell -File .\cb-erp-launch.ps1 -EnvName dev    -> project cb_dev, site dev.localhost, port 8090
#        powershell -File .\cb-erp-launch.ps1 -EnvName test  -> project cb_test, site test.localhost, port 8091
# Note: ports 8090/8091 chosen because 8080 is occupied by a pre-existing host service (WeKnora).
# Requires: $PwdYml path to frappe_docker pwd.yml (adjust if moved).
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'test')]
    [string]$EnvName
)

$ErrorActionPreference = 'Stop'
$Base = $PSScriptRoot
$PwdYml = 'C:\Users\Administrator\AppData\Local\Temp\opencode\frappe_docker\pwd.yml'

if ($EnvName -eq 'dev') {
    $SiteName  = 'dev.localhost'
    $HostPort  = '8090'
    $DbRootPwd = 'CBrp_dev_DBroot_2026'
    $AdminPwd  = 'CBrp_dev_Admin_2026'
} else {
    $SiteName  = 'test.localhost'
    $HostPort  = '8091'
    $DbRootPwd = 'CBrp_test_DBroot_2026'
    $AdminPwd  = 'CBrp_test_Admin_2026'
}

$StackDir = Join-Path $Base (Join-Path 'stacks' $EnvName)
New-Item -ItemType Directory -Force -Path $StackDir | Out-Null

$compose = Get-Content $PwdYml -Raw
# pin parameterization: site name, passwords, host port
$compose = $compose -replace 'frontend', $SiteName
$compose = $compose -replace 'admin-password=admin', ('admin-password=' + $AdminPwd)
$compose = $compose -replace 'db-root-password=admin', ('db-root-password=' + $DbRootPwd)
$compose = $compose -replace 'MYSQL_ROOT_PASSWORD: admin', ('MYSQL_ROOT_PASSWORD: ' + $DbRootPwd)
$compose = $compose -replace 'MARIADB_ROOT_PASSWORD: admin', ('MARIADB_ROOT_PASSWORD: ' + $DbRootPwd)
$compose = $compose -replace '8080:8080', ($HostPort + ':8080')

$ComposePath = Join-Path $StackDir 'compose.yaml'
Set-Content -Path $ComposePath -Value $compose -Encoding UTF8
Write-Output ("compose written: " + $ComposePath)

docker compose -p ('cb_' + $EnvName) --project-directory $StackDir -f $ComposePath up -d
if ($LASTEXITCODE -ne 0) { throw 'docker compose up failed' }

Write-Output 'stack started.'
Write-Output ("access url: http://localhost:" + $HostPort + "   site: " + $SiteName + "   admin user: Administrator / " + $AdminPwd)
