<#
.SYNOPSIS
  Python availability check + delegate to skills.py (Windows/PowerShell).

.DESCRIPTION
  Ensures Python is available before delegating to skills.py.
  If Python is missing, prompts to install manually or auto via Scoop.

.EXAMPLE
  .\skills.ps1 list
  .\skills.ps1 install
  .\skills.ps1 status
  .\skills.ps1 install -DryRun
  .\skills.ps1 install -Agents claude-code,kimi
  .\skills.ps1 install -Skills skill-authoring-guide
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── Python check ────────────────────────────────────────────────────────────

function Test-IsPythonInstalled {
    try {
        $null = python --version 2>&1
        return $true
    } catch {
        try {
            $null = py --version 2>&1
            return $true
        } catch {
            return $false
        }
    }
}

if (-not (Test-IsPythonInstalled)) {
    Write-Host ''
    Write-Host '⚠  Python is not installed on this system.' -ForegroundColor Yellow
    Write-Host ''
    Write-Host '  [m] Manual - show install instructions and exit'
    Write-Host '  [a] Auto   - install Python via Scoop'
    Write-Host '  [q] Quit'
    Write-Host ''
    $choice = (Read-Host 'Choose (m/a/q, default: q)').Trim().ToLower()

    switch ($choice) {
        'm' {
            Write-Host ''
            Write-Host 'Install Python 3.11+ from https://www.python.org/downloads/' -ForegroundColor Cyan
            Write-Host 'Make sure to check "Add Python to PATH" during installation.' -ForegroundColor Cyan
            Write-Host ''
            Write-Host 'After installing, disable App Execution Aliases to avoid Store redirect:' -ForegroundColor Cyan
            Write-Host '  Settings > Apps > Advanced app settings > App execution aliases' -ForegroundColor Cyan
            Write-Host '  → Turn OFF "python.exe" and "python3.exe"' -ForegroundColor Cyan
            exit 1
        }
        'a' {
            Write-Host 'Installing Python via Scoop...' -ForegroundColor Green

            if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
                Write-Host 'Scoop not found. Installing Scoop first...' -ForegroundColor Yellow
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
                if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
                    Write-Host '  [XX] Scoop installation failed. Please install Python manually.' -ForegroundColor Red
                    exit 1
                }
                Write-Host '  [OK] Scoop installed' -ForegroundColor Green
            }

            scoop install python
            if ($LASTEXITCODE -eq 0) {
                Write-Host '  [OK] Python installed via Scoop' -ForegroundColor Green
                $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + `
                            [Environment]::GetEnvironmentVariable('Path', 'Machine')
                if (-not (Test-IsPythonInstalled)) {
                    Write-Host '  [XX] Python not found after install. Please restart terminal.' -ForegroundColor Red
                    exit 1
                }
            } else {
                Write-Host '  [XX] Python installation via Scoop failed. Install manually.' -ForegroundColor Red
                exit 1
            }
        }
        default {
            Write-Host 'Exiting.' -ForegroundColor Red
            exit 1
        }
    }
}

# ── Delegate to skills.py ──────────────────────────────────────────────────

$PythonCmd = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
& $PythonCmd (Join-Path $ScriptDir 'skills.py') @args
exit $LASTEXITCODE
