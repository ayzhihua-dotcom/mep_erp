$ledger = $args[0]
$rowfile = $args[1]
$anchor = $args[2]
$row = ([System.IO.File]::ReadAllText($rowfile, [System.Text.Encoding]::UTF8)).TrimEnd([char]13, [char]10)
$lines = [System.IO.File]::ReadAllLines($ledger, [System.Text.Encoding]::UTF8)
$idx = -1
for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i].TrimStart().StartsWith($anchor)) { $idx = $i; break } }
if ($idx -lt 0) { "ANCHOR_NOT_FOUND: " + $anchor; exit 1 }
$out = New-Object System.Collections.Generic.List[string]
for ($i = 0; $i -lt $lines.Count; $i++) {
  [void]$out.Add($lines[$i])
  if ($i -eq $idx) { [void]$out.Add($row) }
}
$text = ($out -join "`n")
$bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
[System.IO.File]::WriteAllBytes($ledger, $bytes)
"INSERTED_AFTER_IDX: " + $idx + " ; NEW_COUNT: " + $out.Count
