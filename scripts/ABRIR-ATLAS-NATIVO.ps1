[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CodeRoot,
    [Parameter(Mandatory=$true)][string]$NotebookRoot,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [switch]$NoOpen
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$python = Get-Command python -CommandType Application -ErrorAction Stop
$root = Split-Path -Parent $PSScriptRoot
$exporter = Join-Path $root 'tools\export_native_notebook.py'
if (-not (Test-Path -LiteralPath (Join-Path $CodeRoot 'src\r4\campaigns\atlas.py') -PathType Leaf)) {
    throw 'ATLAS_PRODUCER_CODE_MISSING: selecione o checkout R4 já funcional.'
}
if (-not (Test-Path -LiteralPath $NotebookRoot -PathType Container)) { throw 'ATLAS_NOTEBOOK_MISSING' }
if (Test-Path -LiteralPath $Output) { throw 'ATLAS_OUTPUT_MUST_BE_NEW' }
& $python.Source -I -c 'import atlas_viewer, caderno_protocol'
if ($LASTEXITCODE -ne 0) { throw 'Instale os pacotes públicos protocol/viewer desta PR antes de abrir; o launcher não instala nada automaticamente.' }
& $python.Source -B $exporter --r4-code $CodeRoot --notebook-root $NotebookRoot --output $Output
if ($LASTEXITCODE -ne 0) { throw 'ATLAS_NATIVE_EXPORT_BLOCKED: consulte a mensagem; fontes preservadas.' }
$source = (Resolve-Path -LiteralPath $Output).Path
# Popen argument list avoids shell quoting and opens only the new local package.
$launch = @'
import subprocess, sys, time, urllib.request, webbrowser
port, source, no_open = int(sys.argv[1]), sys.argv[2], sys.argv[3]
import socket
with socket.socket() as probe:
    probe.bind(('127.0.0.1', port))
process = subprocess.Popen([sys.executable, '-I', '-m', 'atlas_viewer', 'serve', '--source', source, '--port', str(port)])
try:
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError('ATLAS_NATIVE_SERVER_FAILED')
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/notebook', timeout=2) as r:
                import json
                model = json.load(r)
                if not any(s['status'] == 'READY' for s in model['sources']):
                    raise RuntimeError('ATLAS_NATIVE_PACKAGE_NOT_READY')
                break
        except OSError:
            time.sleep(.1)
    else:
        raise TimeoutError('ATLAS_NATIVE_START_TIMEOUT')
    url = f'http://127.0.0.1:{port}/notebook'
    if no_open != '1':
        webbrowser.open(url)
    print('Atlas nativo: ' + url + ' — Ctrl+C encerra somente este servidor.', flush=True)
    process.wait()
except KeyboardInterrupt:
    pass
finally:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=5)
'@
& $python.Source -B -c $launch $Port $source $(if ($NoOpen) { '1' } else { '0' })
if ($LASTEXITCODE -ne 0) { throw 'ATLAS_NATIVE_SESSION_FAILED' }
