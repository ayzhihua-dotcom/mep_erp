$ErrorActionPreference = "Stop"
$path = "项目文档台账.md"
$lines = [System.IO.File]::ReadAllLines($path, [System.Text.Encoding]::UTF8)
$out = New-Object System.Collections.Generic.List[string]
[out]::Add(("TOTAL UTF8 LINES: " + $lines.Count))
for ($i = 1; $i -le $lines.Count; $i++) {
  $l = $lines[$i - 1]
  if ([string]::IsNullOrWhiteSpace($l)) {
    [out]::Add(("$i: <BLANK>"))
  } elseif ($l.StartsWith("|")) {
    $parts = $l.Split('|')
    $rownum = $parts[1].Trim()
    [out]::Add(("$i: row " + $rownum))
  } else {
    [out]::Add(("$i: other " + $l.Substring(0, [Math]::Min(25, $l.Length))))
  }
}
$writer = New-Object System.IO.StreamWriter("环境搭建/stacks/dev/ledger_structure.txt", $false, [System.Text.Encoding]::UTF8)
try { $writer.Write(($out -join "`n")) } finally { $writer.Close() }
