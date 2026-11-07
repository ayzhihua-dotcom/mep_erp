# CB-ERP master data seed (D-1 ~ D-9) via Frappe REST API - ASCII only
# Target dev.localhost by default. All names are PLACEHOLDERS until O-02/O-03 freeze.
param(
    [string]$SitePort = '8090',
    [string]$AdminPwd = 'CBrp_dev_Admin_2026'
)

$ErrorActionPreference = 'Continue'
$BaseUri = ('http://localhost:' + $SitePort)

$login = Invoke-WebRequest -Uri ($BaseUri + '/api/method/login') -Method POST -ContentType 'application/x-www-form-urlencoded' -Body ('usr=Administrator&pwd=' + $AdminPwd) -SessionVariable sess -UseBasicParsing -TimeoutSec 30
Write-Output ("LOGIN:" + $login.StatusCode)
$ws = $sess

function ApiPost($path, $bodyObj) {
    $body = $bodyObj | ConvertTo-Json -Depth 10 -Compress
    try {
        $r = Invoke-WebRequest -Uri ($BaseUri + $path) -Method POST -ContentType 'application/json; charset=utf-8' -Body $body -WebSession $ws -UseBasicParsing -TimeoutSec 60
        return $true
    } catch {
        $msg = $_.ErrorDetails.Message
        if (-not $msg) { $msg = $_.Exception.Message }
        $label = $bodyObj.label
        if (-not $label) { $label = $path }
        Write-Output ("ERR " + $label + " -> " + $msg.Substring(0, [Math]::Min(200, $msg.Length)))
        return $false
    }
}

function NewDoc($doctype, $fields, $label) {
    $docObj = @{ doctype = $doctype }
    foreach ($k in $fields.Keys) { $docObj[$k] = $fields[$k] }
    if (-not $label) {
        $keyHit = $docObj.Keys | Where-Object { $_ -like '*_name' -or $_ -like '*_code' -or $_ -eq 'email' } | Select-Object -First 1
        if ($keyHit) { $label = $docObj[$keyHit] } else { $label = $doctype }
    }
    $docJson = $docObj | ConvertTo-Json -Depth 10 -Compress
    $payload = @{ label = $doctype + ':' + $label; doc = $docJson }
    $ok = ApiPost '/api/method/frappe.client.insert' $payload
    if ($ok) { Write-Output ("OK " + $doctype + " " + $label) }
    return $ok
}

function SetValue($doctype, $name, $fields) {
    foreach ($k in $fields.Keys) {
        $bodyObj = @{ doctype = $doctype; name = $name; fieldname = $k; val = $fields[$k]; label = ($name + '.' + $k) }
        ApiPost '/api/method/frappe.client.set_value' $bodyObj | Out-Null
    }
    Write-Output ("DONE SET " + $doctype + " " + $name)
}

# ---- D-9 system params: language zh (D-11), timezone, default country ----
SetValue 'System Settings' 'System Settings' @{ language = 'zh'; time_zone = 'Asia/Shanghai'; country = 'China' }
SetValue 'Currency' 'CNY' @{ enabled = '1' }
SetValue 'Currency' 'BRL' @{ enabled = '1' }
SetValue 'Currency' 'USD' @{ enabled = '1' }

# ---- D-1 companies: C1 China (CNY), C2 Brazil (BRL); names = placeholder ----
NewDoc 'Company' @{ company_name = 'CB-ERP China Purchasing Co (Placeholder)'; abbr = 'CBC'; default_currency = 'CNY'; country = 'China'; company_logo = $null; domain = $null }
NewDoc 'Company' @{ company_name = 'CB-ERP Brazil Project Co (Placeholder)'; abbr = 'CBP'; default_currency = 'BRL'; country = 'Brazil' }

# ---- D-4 item groups ----
NewDoc 'Item Group' @{ item_group_name = 'MEC Engineering Materials (Placeholder)'; parent_item_group = 'All Item Groups'; is_group = '1' }
NewDoc 'Item Group' @{ item_group_name = 'MEC-Pipe Valves'; parent_item_group = 'MEC Engineering Materials (Placeholder)' }
NewDoc 'Item Group' @{ item_group_name = 'MEC-Electrical'; parent_item_group = 'MEC Engineering Materials (Placeholder)' }
NewDoc 'Item Group' @{ item_group_name = 'MEC-Instruments'; parent_item_group = 'MEC Engineering Materials (Placeholder)' }

# ---- D-2 warehouses (under auto-created company parent) ----
NewDoc 'Warehouse' @{ warehouse_name = 'China Shipping Warehouse'; company = 'CB-ERP China Purchasing Co (Placeholder) - CBC'; warehouse_type = 'Transit' }
NewDoc 'Warehouse' @{ warehouse_name = 'Quarantine Warehouse C1'; company = 'CB-ERP China Purchasing Co (Placeholder) - CBC'; is_rejecting_warehouse = '1' }
NewDoc 'Warehouse' @{ warehouse_name = 'Inspection Pending Warehouse C1'; company = 'CB-ERP China Purchasing Co (Placeholder) - CBC' }
NewDoc 'Warehouse' @{ warehouse_name = 'Brazil Site Main Warehouse'; company = 'CB-ERP Brazil Project Co (Placeholder) - CBP' }
NewDoc 'Warehouse' @{ warehouse_name = 'Quarantine Warehouse C2'; company = 'CB-ERP Brazil Project Co (Placeholder) - CBP'; is_rejecting_warehouse = '1' }
NewDoc 'Warehouse' @{ warehouse_name = 'Inspection Pending Warehouse C2'; company = 'CB-ERP Brazil Project Co (Placeholder) - CBP' }

# ---- D-3 pilot project ----
NewDoc 'Project' @{ project_name = 'CB-D01 Pilot Project (Placeholder)'; company = 'CB-ERP Brazil Project Co (Placeholder) - CBP'; project_type = 'External'; expected_start_date = '2026-10-28' }

# ---- D-6 sample items (3; hand placeholder codes, M-01 auto coding pending) ----
NewDoc 'Item' @{ item_code = 'CB-M-0001'; item_name = 'Gate Valve DN100 PN16'; item_group = 'MEC-Pipe Valves'; stock_uom = 'Unit'; is_stock_item = '1'; description = 'Sample material seeded for dev' }
NewDoc 'Item' @{ item_code = 'CB-M-0002'; item_name = 'Power Cable 4x16mm2'; item_group = 'MEC-Electrical'; stock_uom = 'Meter'; is_stock_item = '1'; description = 'Sample material seeded for dev' }
NewDoc 'Item' @{ item_code = 'CB-M-0003'; item_name = 'Pressure Transmitter 0-10bar'; item_group = 'MEC-Instruments'; stock_uom = 'Unit'; is_stock_item = '1'; description = 'Sample material seeded for dev' }

# ---- D-7 suppliers (3 placeholders; CNPJ pending) ----
NewDoc 'Supplier' @{ supplier_name = 'CB CN Supplier A (Placeholder)'; supplier_group = 'All Supplier Groups'; country = 'China' }
NewDoc 'Supplier' @{ supplier_name = 'CB CN Supplier B (Placeholder)'; supplier_group = 'All Supplier Groups'; country = 'China' }
NewDoc 'Supplier' @{ supplier_name = 'CB BR Supplier C (Placeholder)'; supplier_group = 'All Supplier Groups'; country = 'Brazil'; tax_id = '000.000.000/0001-00' }

# ---- D-8 roles + 1 example user each (placeholder emails; passwords logged at record doc) ----
$roles = @('SYS','ENG','PRC','BRA','LOG','CUS','WHS','PM','FIN','MGT')
foreach ($r in $roles) { NewDoc 'Role' @{ role_name = $r; description = 'CB-ERP role placeholder (matrix S1 #2)' } }

$i = 0
foreach ($r in $roles) {
    $i++
    $uid = ('dev' + ('{0:D2}' -f $i) + '.' + $r.ToLower() + '@cb.local')
    NewDoc 'User' @{ email = $uid; first_name = ('CB-' + $r); username = $uid; send_welcome_email = '0'; language = 'zh'; time_zone = 'Asia/Shanghai'; new_password = ('CBrp_dev' + '{0:D2}' -f $i + '_2026'); roles = @(@{'role' = $r }) }
}

# ---- user permissions (company data-scope skeleton, S1 #2 matrix sec.5) ----
NewDoc 'User Permission' @{ user = 'dev03.prc@cb.local'; allow = 'Company'; for_value = 'CB-ERP China Purchasing Co (Placeholder) - CBC' }
NewDoc 'User Permission' @{ user = 'dev04.bra@cb.local'; allow = 'Company'; for_value = 'CB-ERP Brazil Project Co (Placeholder) - CBP' }
NewDoc 'User Permission' @{ user = 'dev06.cus@cb.local'; allow = 'Company'; for_value = 'CB-ERP China Purchasing Co (Placeholder) - CBC' }

Write-Output 'SEED-DONE'
