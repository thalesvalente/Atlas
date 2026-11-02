[CmdletBinding()]
param(
    [string[]]$Source = @(),
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [ValidateSet('Notebook','Protocol')][string]$View = 'Notebook',
    [switch]$NoOpen
)
# Atlas NOVO. Only a selected Caderno protocol package is read.
# R4/CA-01 is not loaded, imported, discovered, or executed.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$python = Get-Command -Name python -CommandType Application -ErrorAction Stop
& $python.Source -I -c 'import atlas_viewer, caderno_protocol'
if ($LASTEXITCODE -ne 0) {
    throw 'ATLAS_NOVO_NOT_INSTALLED: instale packages/protocol e packages/atlas desta PR no ambiente Python escolhido.'
}
if ($Source.Count -gt 16) { throw 'ATLAS_MAX_16_EXPLICIT_SOURCES' }
$selected = @()
foreach ($item in $Source) {
    if ([string]::IsNullOrWhiteSpace($item) -or -not (Test-Path -LiteralPath $item)) {
        throw ('ATLAS_SOURCE_NOT_FOUND: ' + $item)
    }
    $selected += (Resolve-Path -LiteralPath $item).Path
}
if ($selected.Count -eq 0) {
    Write-Warning 'Nenhuma fonte selecionada; o Atlas NOVO abrirá sem registros, sem dados inventados.'
}
$program = @'
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

port = int(sys.argv[1])
view = sys.argv[2]
no_open = sys.argv[3] == "1"
sources = sys.argv[4:]
command = [sys.executable, "-I", "-m", "atlas_viewer", "serve", "--port", str(port)]
for source in sources:
    command.extend(["--source", source])
with socket.socket() as probe:
    probe.bind(("127.0.0.1", port))
process = subprocess.Popen(command, stdin=subprocess.DEVNULL)
try:
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("ATLAS_NOVO_SERVER_TERMINATED")
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/notebook", timeout=2
            ) as response:
                catalog = json.load(response)
                if not isinstance(catalog.get("sources"), list):
                    raise RuntimeError("ATLAS_NOVO_RESPONSE_INVALID")
                ready = sum(s.get("status") == "READY" for s in catalog["sources"])
                if sources and not ready:
                    print("ATLAS_NOVO_NO_NATIVE_SOURCE_READY: " +
                          "a interface abre, mas esta fonte não contém uma apresentação nativa READY.",
                          flush=True)
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(.1)
    else:
        raise TimeoutError("ATLAS_NOVO_START_TIMEOUT")
    route = "/notebook" if view == "Notebook" else "/"
    url = f"http://127.0.0.1:{port}{route}"
    print("ATLAS_NOVO: " + url, flush=True)
    print("Ctrl+C encerra somente este servidor. A fonte permanece intacta.", flush=True)
    if not no_open:
        webbrowser.open(url)
    process.wait()
except KeyboardInterrupt:
    pass
finally:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
'@
& $python.Source -I -B -c $program $Port $View $(if ($NoOpen) { '1' } else { '0' }) @selected
if ($LASTEXITCODE -ne 0) { throw 'ATLAS_NOVO_SESSION_FAILED' }
