param(
    [Parameter(Mandatory = $true)][string]$Dir,
    [string]$OutDir = "",
    [string[]]$Only = @(),
    [switch]$OnePass,
    [string]$Python = 'python'
)

# Compile every .tex in $Dir with xelatex (2 passes) and copy PDFs to $OutDir.
# Windows PowerShell 5.1: keep this file pure ASCII (no BOM -> GBK decoding).
# Usage:
#   & build_pdf.ps1 -Dir <abs dir> [-OutDir <abs dir>] [-Only manual.tex]

$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'

if (-not (Test-Path $Dir)) { throw "dir not found: $Dir" }
if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $OutDir = Join-Path (Split-Path $Dir -Parent) '..\out'
}
$OutDir = [System.IO.Path]::GetFullPath($OutDir)
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }

$texFiles = Get-ChildItem -Path $Dir -Filter *.tex -File | Sort-Object Name
if ($Only.Count -gt 0) {
    $texFiles = $texFiles | Where-Object { $Only -contains $_.Name }
}
if (-not $texFiles) { throw "no .tex in $Dir" }

$passes = 1
if (-not $OnePass) { $passes = 2 }
$results = @()
$py = $Python

foreach ($tex in $texFiles) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($tex.Name)
    $exit = 0
    for ($i = 1; $i -le $passes; $i++) {
        Push-Location $Dir
        try {
            & xelatex -interaction=nonstopmode -halt-on-error $tex.Name *> "$stem.pass$i.log"
            $exit = $LASTEXITCODE
        }
        finally { Pop-Location }
        if ($exit -ne 0) { break }
    }

    $pdf = Join-Path $Dir "$stem.pdf"
    $ok = ($exit -eq 0) -and (Test-Path $pdf) -and ((Get-Item $pdf).Length -gt 1000)
    $target = Join-Path $OutDir "$stem.pdf"
    $pages = 0
    $sizeKB = 0
    if ($ok) {
        Copy-Item $pdf $target -Force
        $sizeKB = [math]::Round((Get-Item $target).Length / 1KB, 1)
        $pages = (& $py -c "from pypdf import PdfReader;import sys;print(len(PdfReader(sys.argv[1]).pages))" $target)
    }
    $results += [pscustomobject]@{
        tex    = $tex.Name
        exit   = $exit
        ok     = $ok
        pages  = $pages
        sizeKB = $sizeKB
        log    = Join-Path $Dir "$stem.pass$passes.log"
    }
}

$results | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
$results | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $Dir 'build_result.json')
if (($results | Where-Object { -not $_.ok }).Count -gt 0) { exit 1 }
exit 0
