[CmdletBinding()]
param(
    [string]$CodeRoot = $(if ($env:ATLAS_R4_CODE_ROOT) { $env:ATLAS_R4_CODE_ROOT } else { 'H:\Atlas009-CA01' }),
    [string]$NotebookRoot = $(if ($env:ATLAS_NOTEBOOK_ROOT) { $env:ATLAS_NOTEBOOK_ROOT } else { 'H:\R4-Caderno-Cientifico' }),
    [switch]$OpenExisting,
    [switch]$NoOpen
)
# Reuse the ORIGINAL operational R4 renderer; do not embed R4 code into Atlas.
# All scientific inputs remain in the external central notebook.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$pointer = Join-Path (Join-Path $NotebookRoot '.r4\atlas') 'ATLAS-ATUAL.html'
if (-not $OpenExisting) {
    $entry = Join-Path $CodeRoot 'R4-CADERNO.py'
    if (-not (Test-Path -LiteralPath $entry -PathType Leaf)) {
        throw 'ATLAS_ORIGINAL_CODE_MISSING: informe -CodeRoot apontando para o checkout R4 com R4-CADERNO.py'
    }
    if (-not (Test-Path -LiteralPath $NotebookRoot -PathType Container)) {
        throw 'ATLAS_CENTRAL_NOTEBOOK_MISSING: informe -NotebookRoot do Caderno central'
    }
    $python = Get-Command -Name 'python' -CommandType Application -ErrorAction SilentlyContinue
    if (-not $python) { throw 'PYTHON_NOT_FOUND: Python 3.11+ deve estar disponível no PATH' }

    foreach ($phase in @('project', 'validate')) {
        & $python.Source -B $entry --root $NotebookRoot $phase
        if ($LASTEXITCODE -ne 0) { throw ('ATLAS_ORIGINAL_' + $phase.ToUpperInvariant() + '_FAILED') }
    }
    $output = Join-Path $NotebookRoot '.r4\atlas'
    & $python.Source -B $entry --root $NotebookRoot atlas --output $output
    if ($LASTEXITCODE -ne 0) { throw 'ATLAS_ORIGINAL_RENDER_FAILED' }
}
if (-not (Test-Path -LiteralPath $pointer -PathType Leaf)) {
    throw 'ATLAS_ORIGINAL_HTML_MISSING: execute novamente sem -OpenExisting para gerar a visualizacao original'
}
$file = Get-Item -LiteralPath $pointer
if (($file.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'ATLAS_ORIGINAL_POINTER_REPARSE_UNSAFE'
}
if (-not $NoOpen) {
    Start-Process -FilePath $pointer
    Write-Output 'ATLAS_ORIGINAL_OPENED'
} else {
    Write-Output 'ATLAS_ORIGINAL_READY_NO_OPEN'
}
