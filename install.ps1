$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = if ($env:PYTHON_BIN) { $env:PYTHON_BIN } else { "py" }

if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
  Write-Error "Python 3.10 or later is required. Install Python, then run this script again."
}

$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
  & $Python -m venv (Join-Path $RootDir ".venv")
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $RootDir "requirements.txt")

Write-Host ""
Write-Host "SiteSentry is installed. Start it with:"
Write-Host "  & `"$VenvPython`" `"$RootDir\backend\app.py`""
Write-Host "Then open http://127.0.0.1:5123 in your browser."
