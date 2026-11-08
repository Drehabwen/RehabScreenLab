param(
    [Parameter(Mandatory=$true)][string]$RoutesJson,
    [string]$BaseUrl = "http://localhost:5174",
    [string]$OutDir  = "",
    [int]$Width = 480,
    [int]$Height = 1000,
    [int]$Scale = 2,
    [string]$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe",
    [string]$Profile = ""
)
# Batch-capture running UI screens per routes.json:
#   [{"file":"r01-tasks.png","route":"/tasks","label":"..."}]
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'

if (-not (Test-Path $Chrome)) { throw "chrome not found: $Chrome" }
if ([string]::IsNullOrWhiteSpace($OutDir)) { $OutDir = Join-Path (Split-Path $RoutesJson -Parent) 'real' }
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
if ([string]::IsNullOrWhiteSpace($Profile)) { $Profile = Join-Path $env:TEMP ('shot-profile-' + [guid]::NewGuid().ToString('N')) }

$routes = Get-Content $RoutesJson -Raw -Encoding UTF8 | ConvertFrom-Json
$ok = 0
foreach ($r in $routes) {
    $out = Join-Path $OutDir $r.file
    & $Chrome --headless=new --disable-gpu --hide-scrollbars --no-first-run --no-default-browser-check `
        --force-device-scale-factor=$Scale --window-size="$Width,$Height" --virtual-time-budget=9000 `
        --use-fake-ui-for-media-stream --use-fake-device-for-media-stream `
        --user-data-dir=$Profile --screenshot="$out" ($BaseUrl + $r.route) 2>&1 | Out-Null
    if ((Test-Path $out) -and ((Get-Item $out).Length -gt 1000)) {
        $ok++
        Write-Host ("OK   {0}  {1} KB" -f $r.file, [math]::Round((Get-Item $out).Length / 1KB))
    } else {
        Write-Host ("FAIL {0}" -f $r.file)
    }
}
Write-Host ("done: {0}/{1}" -f $ok, $routes.Count)
if ($ok -lt $routes.Count) { exit 1 }
