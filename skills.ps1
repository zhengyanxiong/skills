$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
  $Python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $Python) {
  Write-Error "Python is required. Install Python 3 and make sure python or python3 is on PATH."
  exit 1
}

& $Python.Source (Join-Path $ScriptDir "skills.py") @args
exit $LASTEXITCODE
