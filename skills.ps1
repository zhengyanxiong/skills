<#
.SYNOPSIS
  Skills management entry point for Windows/PowerShell.
  Delegates to link-skills.ps1 after ensuring Python is available.

.DESCRIPTION
  If Python is not installed, prompts user to install manually or
  auto-install via Scoop before delegating to link-skills.ps1.

.EXAMPLE
  .\skills.ps1 list
  .\skills.ps1 install
  .\skills.ps1 status
#>

param(
  [Parameter(Position = 0, Mandatory = $false)]
  [string]$Command,

  [switch]$DryRun,

  [string]$Agents = '',

  [string]$Skills = ''
)

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

function Install-PythonIfMissing {
    if (Test-IsPythonInstalled) {
        return
    }

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
                    Write-Host '[XX] Scoop installation failed. Please install Python manually.' -ForegroundColor Red
                    exit 1
                }
                Write-Host '  [OK] Scoop installed' -ForegroundColor Green
            }

            scoop install python
            if ($LASTEXITCODE -eq 0) {
                Write-Host '  [OK] Python installed via Scoop' -ForegroundColor Green
                $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + `
                            [Environment]::GetEnvironmentVariable('Path', 'Machine')
            } else {
                Write-Host '[XX] Python installation via Scoop failed. Install manually.' -ForegroundColor Red
                exit 1
            }
        }
        default {
            Write-Host 'Exiting.' -ForegroundColor Red
            exit 1
        }
    }
}

# ── Helpers ────────────────────────────────────────────────────────────────

function Write-OK   { Write-Host '  [' -NoNewline; Write-Host 'OK' -ForegroundColor Green -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Warn { Write-Host '  [' -NoNewline; Write-Host '!!' -ForegroundColor Yellow -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Err  { Write-Host '  [' -NoNewline; Write-Host 'XX' -ForegroundColor Red -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Info { Write-Host '  [' -NoNewline; Write-Host '..' -ForegroundColor Cyan -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Dim  { Write-Host $args -ForegroundColor DarkGray }

# ── Main ───────────────────────────────────────────────────────────────────

Install-PythonIfMissing

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir  = (Resolve-Path $ScriptDir).Path
$LinkScript = Join-Path $RepoDir 'link-skills.ps1'

if (-not (Test-Path $LinkScript)) {
    Write-Err "link-skills.ps1 not found at $LinkScript"
    exit 1
}

# Map commands: 'list' → 'status'
$mappedCommand = if ($Command -eq 'list') { 'status' } else { $Command }

$argsList = @($mappedCommand)
if ($DryRun) { $argsList += '-DryRun' }
if ($Agents) { $argsList += "-Agents $Agents" }
if ($Skills) { $argsList += "-Skills $Skills" }

Write-Dim "Delegating to link-skills.ps1 $($argsList -join ' ')..."
Write-Host ''

& $LinkScript @argsList
