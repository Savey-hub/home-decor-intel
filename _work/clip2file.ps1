param([Parameter(Mandatory=$true)][string]$Out)
Add-Type -AssemblyName System.Windows.Forms | Out-Null
$t = [System.Windows.Forms.Clipboard]::GetText()
if ($null -eq $t) { $t = "" }
$dir = Split-Path -Parent $Out
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($Out, $t, $enc)
Write-Host ("LEN=" + $t.Length + " -> " + $Out)
