param(
  [string]$HostName = $(if ($env:WEBUI_HOST) { $env:WEBUI_HOST } else { '127.0.0.1' }),
  [int]$Port = $(if ($env:WEBUI_PORT) { [int]$env:WEBUI_PORT } else { 8000 }),
  [switch]$Schedule
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $ProjectRoot

# Keep Windows console logging stable for Korean/Chinese provider messages.
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONLEGACYWINDOWSSTDIO = '0'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)

$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (!(Test-Path $Python)) {
  $Python = 'python'
}

$Arguments = @('-X', 'utf8', 'main.py', '--serve-only', '--host', $HostName, '--port', [string]$Port)
if ($Schedule) {
  $Arguments = @('-X', 'utf8', 'main.py', '--serve', '--schedule', '--host', $HostName, '--port', [string]$Port)
}

Write-Host "Starting Daily Stock Analysis server at http://$HostName`:$Port"
Write-Host 'UTF-8 runtime enabled: PYTHONUTF8=1, PYTHONIOENCODING=utf-8'
& $Python @Arguments
