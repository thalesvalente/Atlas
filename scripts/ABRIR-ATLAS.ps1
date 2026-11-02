[CmdletBinding()]
param(
    [string[]]$Source = @(),
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [ValidateSet('Notebook','Protocol')][string]$View = 'Notebook',
    [string]$LegacyCodeRoot,
    [string]$LegacyNotebookRoot,
    [switch]$NoOpen,
    [switch]$ProbeOnly
)
# This is the Atlas NEW product launcher, not the historical R4 renderer.
# The optional legacy reader is invoked out-of-process by atlas_launch.py.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$python = Get-Command -Name python -CommandType Application -ErrorAction Stop | Select-Object -First 1
# PowerShell 5.1 may resolve both the installed executable and the WindowsApps shim.
# Keep ONE command object; enumerating .Source produced a corrupt multi-path executable.
$launcher = Join-Path $PSScriptRoot 'atlas_launch.py'
if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) {
    throw 'ATLAS_NOVO_LAUNCHER_MISSING'
}
& $python.Source -I -c 'import atlas_viewer, caderno_protocol'
if ($LASTEXITCODE -ne 0) {
    throw 'ATLAS_NOVO_NOT_INSTALLED: instale packages/protocol e packages/atlas antes de abrir.'
}
$arguments = @('--port', [string]$Port, '--view', $View)
foreach ($item in $Source) {
    $arguments += @('--source', [string]$item)
}
if (-not [string]::IsNullOrWhiteSpace($LegacyCodeRoot)) {
    $arguments += @('--legacy-code-root', $LegacyCodeRoot)
}
if (-not [string]::IsNullOrWhiteSpace($LegacyNotebookRoot)) {
    $arguments += @('--legacy-notebook-root', $LegacyNotebookRoot)
}
if ($NoOpen) { $arguments += '--no-open' }
if ($ProbeOnly) { $arguments += '--probe-only' }
# Pass only ordinary arguments, not an embedded Python program. This works
# in Windows PowerShell 5.1's legacy native argument mode and in pwsh 7.
& $python.Source -I -B $launcher @arguments
if ($LASTEXITCODE -ne 0) {
    throw ('ATLAS_NOVO_SESSION_FAILED: exit ' + $LASTEXITCODE)
}
