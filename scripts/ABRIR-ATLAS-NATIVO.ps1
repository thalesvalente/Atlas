[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CodeRoot,
    [Parameter(Mandatory=$true)][string]$NotebookRoot,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [switch]$NoOpen,
    [switch]$ProbeOnly
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$python = Get-Command python -CommandType Application -ErrorAction Stop | Select-Object -First 1
$root = Split-Path -Parent $PSScriptRoot
$exporter = Join-Path $root 'tools\export_native_notebook.py'
$launcher = Join-Path $PSScriptRoot 'atlas_launch.py'
if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) { throw 'ATLAS_NOVO_LAUNCHER_MISSING' }
if (-not (Test-Path -LiteralPath (Join-Path $CodeRoot 'src\r4\campaigns\atlas.py') -PathType Leaf)) {
    throw 'ATLAS_PRODUCER_CODE_MISSING: selecione o checkout R4 já funcional.'
}
if (-not (Test-Path -LiteralPath $NotebookRoot -PathType Container)) { throw 'ATLAS_NOTEBOOK_MISSING' }
if (Test-Path -LiteralPath $Output) { throw 'ATLAS_OUTPUT_MUST_BE_NEW' }
& $python.Source -I -c 'import atlas_viewer, caderno_protocol'
if ($LASTEXITCODE -ne 0) { throw 'Instale os pacotes públicos protocol/viewer desta PR antes de abrir; o launcher não instala nada automaticamente.' }
& $python.Source -I -B $exporter --r4-code $CodeRoot --notebook-root $NotebookRoot --output $Output
if ($LASTEXITCODE -ne 0) { throw 'ATLAS_NATIVE_EXPORT_BLOCKED: consulte a mensagem; fontes preservadas.' }
$source = (Resolve-Path -LiteralPath $Output).Path
# Share the main launcher's static readiness probe and process/exit handling.
# Pass argv only: embedded Python source is unsafe under PowerShell 5.1 quoting.
$arguments = @('--source', $source, '--port', [string]$Port, '--view', 'Notebook')
if ($NoOpen) { $arguments += '--no-open' }
if ($ProbeOnly) { $arguments += '--probe-only' }
& $python.Source -I -B $launcher @arguments
if ($LASTEXITCODE -ne 0) { throw 'ATLAS_NATIVE_SESSION_FAILED' }
