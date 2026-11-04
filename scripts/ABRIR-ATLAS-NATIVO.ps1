[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CodeRoot,
    [Parameter(Mandatory=$true)][string]$NotebookRoot,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [switch]$NoOpen,
    [switch]$ProbeOnly
)
# Compatibility entrypoint: export out of process, then reuse the Atlas NEW
# supervisor. No legacy module is imported into the installed viewer.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$python = Get-Command -Name python -CommandType Application -ErrorAction Stop | Select-Object -First 1
$root = Split-Path -Parent $PSScriptRoot
$exporter = Join-Path $root 'tools\export_native_notebook.py'
$launcher = Join-Path $PSScriptRoot 'atlas_launch.py'
if (-not (Test-Path -LiteralPath $exporter -PathType Leaf)) { throw 'ATLAS_EXTERNAL_ADAPTER_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'ATLAS_NOVO_LAUNCHER_MISSING' }
if (-not (Test-Path -LiteralPath (Join-Path $CodeRoot 'src\r4\campaigns\atlas.py') -PathType Leaf)) {
    throw 'ATLAS_PRODUCER_CODE_MISSING: selecione o checkout R4 ja funcional.'
}
if (-not (Test-Path -LiteralPath $NotebookRoot -PathType Container)) { throw 'ATLAS_NOTEBOOK_MISSING' }
if (Test-Path -LiteralPath $Output) { throw 'ATLAS_OUTPUT_MUST_BE_NEW' }
& $python.Source -I -c 'import atlas_viewer, caderno_protocol'
if ($LASTEXITCODE -ne 0) {
    throw 'ATLAS_NOVO_NOT_INSTALLED: instale os pacotes publicos protocol/viewer desta PR.'
}
& $python.Source -B $exporter --r4-code $CodeRoot --notebook-root $NotebookRoot --output $Output
if ($LASTEXITCODE -ne 0) { throw ('ATLAS_NATIVE_EXPORT_BLOCKED: exit ' + $LASTEXITCODE) }
$source = (Resolve-Path -LiteralPath $Output).Path
# One owner of lifecycle/readiness: static-page startup probe in normal mode.
# ProbeOnly performs one full-data request with a long deadline and exits.
$arguments = @('--source', $source, '--port', [string]$Port)
if ($NoOpen) { $arguments += '--no-open' }
if ($ProbeOnly) { $arguments += '--probe-only' }
& $python.Source -I -B $launcher @arguments
if ($LASTEXITCODE -ne 0) { throw ('ATLAS_NATIVE_SESSION_FAILED: exit ' + $LASTEXITCODE) }
