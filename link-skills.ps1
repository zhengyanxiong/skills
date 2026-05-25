<#
.SYNOPSIS
  Symlink skills from a central repository to agent skill directories (Windows/PowerShell)

.DESCRIPTION
  Detects installed agents by checking for their config directories, then creates
  symlinks from the central skills repo into each agent's skills/ directory.
  Only the central repo holds the real files; agent directories hold symlinks.

.PARAMETER Command
  install, uninstall, or status

.PARAMETER DryRun
  Preview changes without executing

.PARAMETER Agents
  Comma-separated list of agent IDs to operate on (e.g. "claude-code,kimi")

.PARAMETER Skills
  Comma-separated list of skill names to operate on (e.g. "skill-authoring-guide")

.EXAMPLE
  .\link-skills.ps1 install
  .\link-skills.ps1 install -DryRun
  .\link-skills.ps1 install -Agents claude-code,kimi
  .\link-skills.ps1 status
  .\link-skills.ps1 uninstall -DryRun
#>

param(
  [Parameter(Position = 0, Mandatory = $false)]
  [ValidateSet('install', 'uninstall', 'status')]
  [string]$Command,

  [switch]$DryRun,

  [string]$Agents = '',

  [string]$Skills = ''
)

# ── Globals ────────────────────────────────────────────────────────────────

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir  = (Resolve-Path $ScriptDir).Path

# Known agent definitions: @{ Id = @{ Name, ConfigDir, SkillDirName } }
$AgentDefs = [ordered]@{
  'claude-code' = @{ Name = 'Claude Code'; ConfigDir = "$env:USERPROFILE\.claude"; SkillDirName = 'skills' }
  'codex-cli'   = @{ Name = 'Codex CLI';   ConfigDir = "$env:USERPROFILE\.codex"; SkillDirName = 'skills' }
  'openclaw'    = @{ Name = 'OpenClaw';    ConfigDir = "$env:USERPROFILE\.openclaw"; SkillDirName = 'skills' }
  'kimi'        = @{ Name = 'Kimi';        ConfigDir = "$env:USERPROFILE\.kimi"; SkillDirName = 'skills' }
  'cowork'      = @{ Name = 'CoWork';      ConfigDir = "$env:USERPROFILE\.cowork"; SkillDirName = 'skills' }
  'cursor'      = @{ Name = 'Cursor';      ConfigDir = "$env:USERPROFILE\.cursor"; SkillDirName = 'skills' }
}

# ── Helpers ────────────────────────────────────────────────────────────────

function Write-OK   { Write-Host '  [' -NoNewline; Write-Host 'OK' -ForegroundColor Green -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Warn { Write-Host '  [' -NoNewline; Write-Host '!!' -ForegroundColor Yellow -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Err  { Write-Host '  [' -NoNewline; Write-Host 'XX' -ForegroundColor Red -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Info { Write-Host '  [' -NoNewline; Write-Host '..' -ForegroundColor Cyan -NoNewline; Write-Host '] ' -NoNewline; Write-Host $args }
function Write-Dim  { Write-Host $args -ForegroundColor DarkGray }

# ── Resolve functions ──────────────────────────────────────────────────────

function Get-ResolvedAgents {
  $selected = if ($Agents) { $Agents -split ',' | ForEach-Object { $_.Trim() } } else { @() }
  $result = @()

  foreach ($id in $AgentDefs.Keys) {
    $def = $AgentDefs[$id]
    if ($selected.Count -gt 0 -and $id -notin $selected) { continue }
    if (Test-Path $def.ConfigDir) {
      $skillDir = Join-Path $def.ConfigDir $def.SkillDirName
      $result += @{ Id = $id; Name = $def.Name; SkillDir = $skillDir }
    }
  }
  return $result
}

function Get-ResolvedSkills {
  $selected = if ($Skills) { $Skills -split ',' | ForEach-Object { $_.Trim() } } else { @() }
  $result = @()

  Get-ChildItem -Path $RepoDir -Directory | ForEach-Object {
    $skillDir = $_.FullName
    $skillName = $_.Name
    $skillMd = Join-Path $skillDir 'SKILL.md'

    if (-not (Test-Path $skillMd)) { return }
    if ($selected.Count -gt 0 -and $skillName -notin $selected) { return }

    $result += @{ Name = $skillName; Path = $skillDir }
  }
  return $result
}

# ── Symlink helpers ────────────────────────────────────────────────────────

function Test-IsSymlink {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return $false }
  $item = Get-Item $Path -Force -ErrorAction SilentlyContinue
  return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq [System.IO.FileAttributes]::ReparsePoint
}

function Get-SymlinkTarget {
  param([string]$Path)
  if (-not (Test-IsSymlink $Path)) { return $null }
  $item = Get-Item $Path -Force
  return $item.Target
}

function New-SkillSymlink {
  param([string]$LinkPath, [string]$TargetPath)

  if ($DryRun) { return $true }

  try {
    New-Item -ItemType SymbolicLink -Path $LinkPath -Target $TargetPath -Force | Out-Null
    return $true
  } catch {
    if ($_.Exception.Message -match 'privilege|elevation|Developer Mode|administrator') {
      Write-Err "Symlink requires Administrator privileges or Developer Mode"
      Write-Info "Enable Developer Mode: Settings > Update & Security > For developers > Developer Mode"
      Write-Info "Or run PowerShell as Administrator"
    } else {
      Write-Err "Failed: $($_.Exception.Message)"
    }
    return $false
  }
}

function Remove-SkillSymlink {
  param([string]$LinkPath)

  if ($DryRun) { return $true }

  try {
    Remove-Item $LinkPath -Force
    return $true
  } catch {
    Write-Err "Failed to remove: $($_.Exception.Message)"
    return $false
  }
}

# ── Check symlink capability ───────────────────────────────────────────────

function Test-SymlinkCapability {
  $devMode = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock' -Name 'AllowDevelopmentWithoutDevLicense' -ErrorAction SilentlyContinue
  $isDevMode = ($devMode -and $devMode.AllowDevelopmentWithoutDevLicense -eq 1)

  $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

  if (-not $isAdmin -and -not $isDevMode) {
    Write-Warn "Symlink creation may fail without Administrator privileges or Developer Mode."
    Write-Info "Enable Developer Mode: Settings > Update & Security > For developers > Developer Mode"
    Write-Info "Or right-click PowerShell > Run as Administrator"
    Write-Host ''
    Write-Host 'Continue anyway? [Y/n]' -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'n' -or $response -eq 'N') {
      exit 0
    }
  }
}

# ── Commands ───────────────────────────────────────────────────────────────

function Invoke-Install {
  if (-not $DryRun) {
    Test-SymlinkCapability
  }

  $agents = Get-ResolvedAgents
  $skills = Get-ResolvedSkills

  if ($agents.Count -eq 0) {
    Write-Warn "No installed agents detected (or none matched -Agents filter)"
    Write-Host ''
    Write-Host '  Currently monitored agent config directories:'
    foreach ($id in $AgentDefs.Keys) {
      $def = $AgentDefs[$id]
      if (Test-Path $def.ConfigDir) {
        Write-Host "    + $($def.Name) ($($def.ConfigDir))" -ForegroundColor Green
      } else {
        Write-Host "    - $($def.Name) ($($def.ConfigDir)) -- not installed" -ForegroundColor DarkGray
      }
    }
    return
  }

  if ($skills.Count -eq 0) {
    Write-Warn "No skills found in $RepoDir"
    return
  }

  $totalCreated = 0
  $totalSkipped = 0
  $totalErrors  = 0

  foreach ($agent in $agents) {
    Write-Host ''
    Write-Host $agent.Name -NoNewline
    Write-Dim " ($($agent.SkillDir))"

    # Create agent skill directory if needed
    if (-not (Test-Path $agent.SkillDir)) {
      if ($DryRun) {
        Write-Info "mkdir $($agent.SkillDir)"
      } else {
        New-Item -ItemType Directory -Path $agent.SkillDir -Force | Out-Null
        Write-OK "created $($agent.SkillDir)"
      }
    }

    foreach ($skill in $skills) {
      $linkPath = Join-Path $agent.SkillDir $skill.Name

      if (Test-IsSymlink $linkPath) {
        $currentTarget = Get-SymlinkTarget $linkPath
        if ($currentTarget -eq $skill.Path) {
          Write-Info "$($skill.Name)" -NoNewline; Write-Dim ' already linked'
          $totalSkipped++
        } else {
          Write-Warn "$($skill.Name) points to $currentTarget, expected $($skill.Path)"
          if ($DryRun) {
            Write-Info 'would update symlink'
          } else {
            $ok = New-SkillSymlink -LinkPath $linkPath -TargetPath $skill.Path
            if ($ok) { Write-OK "$($skill.Name) updated" }
          }
          $totalCreated++
        }
      } elseif ((Test-Path $linkPath) -and -not (Test-IsSymlink $linkPath)) {
        Write-Err "$($skill.Name) real file exists at target, skipping"
        $totalErrors++
      } else {
        if ($DryRun) {
          Write-Info "$($skill.Name) would symlink"
        } else {
          $ok = New-SkillSymlink -LinkPath $linkPath -TargetPath $skill.Path
          if ($ok) { Write-OK "$($skill.Name) linked" }
          else { $totalErrors++; continue }
        }
        $totalCreated++
      }
    }
  }

  Write-Host ''
  Write-Host 'Summary: ' -NoNewline
  Write-Host "$totalCreated created/updated" -ForegroundColor Green -NoNewline
  Write-Host ', ' -NoNewline
  Write-Host "$totalSkipped skipped" -ForegroundColor DarkGray -NoNewline
  Write-Host ', ' -NoNewline
  Write-Host "$totalErrors errors" -ForegroundColor Red
}

function Invoke-Uninstall {
  $agents = Get-ResolvedAgents
  $skills = Get-ResolvedSkills

  $totalRemoved = 0
  $totalSkipped = 0

  foreach ($agent in $agents) {
    if (-not (Test-Path $agent.SkillDir)) {
      Write-Host $agent.Name -NoNewline
      Write-Dim ' skill dir not found, skipping'
      continue
    }

    Write-Host ''
    Write-Host $agent.Name -NoNewline
    Write-Dim " ($($agent.SkillDir))"

    foreach ($skill in $skills) {
      $linkPath = Join-Path $agent.SkillDir $skill.Name

      if (Test-IsSymlink $linkPath) {
        $currentTarget = Get-SymlinkTarget $linkPath
        if ($currentTarget -eq $skill.Path) {
          if ($DryRun) {
            Write-Info "$($skill.Name) would remove"
          } else {
            $ok = Remove-SkillSymlink $linkPath
            if ($ok) { Write-OK "$($skill.Name) removed" }
          }
          $totalRemoved++
        } else {
          Write-Warn "$($skill.Name) points elsewhere ($currentTarget), not ours to remove"
          $totalSkipped++
        }
      } elseif (Test-Path $linkPath) {
        Write-Warn "$($skill.Name) real file, not a symlink -- not touched"
        $totalSkipped++
      } else {
        Write-Info "$($skill.Name)" -NoNewline; Write-Dim ' not linked'
        $totalSkipped++
      }
    }
  }

  Write-Host ''
  Write-Host 'Summary: ' -NoNewline
  Write-Host "$totalRemoved removed" -ForegroundColor Green -NoNewline
  Write-Host ', ' -NoNewline
  Write-Host "$totalSkipped skipped" -ForegroundColor DarkGray
}

function Invoke-Status {
  $agents = Get-ResolvedAgents
  $skills = Get-ResolvedSkills

  Write-Host 'Central repo: ' -NoNewline
  Write-Host $RepoDir -ForegroundColor Cyan
  Write-Host ''

  Write-Host 'Skills in repo:'
  foreach ($skill in $skills) {
    Write-Host "  $($skill.Name)" -ForegroundColor Cyan
  }

  Write-Host ''
  Write-Host 'Agent links:'
  Write-Host ''

  foreach ($agent in $agents) {
    Write-Host $agent.Name -NoNewline
    Write-Dim " ($($agent.SkillDir))"

    if (-not (Test-Path $agent.SkillDir)) {
      Write-Dim '  skill directory does not exist'
      continue
    }

    foreach ($skill in $skills) {
      $linkPath = Join-Path $agent.SkillDir $skill.Name

      if (Test-IsSymlink $linkPath) {
        $target = Get-SymlinkTarget $linkPath
        if ($target -eq $skill.Path) {
          Write-Host "  $($skill.Name)" -ForegroundColor Green -NoNewline
          Write-Dim " -> $target"
        } else {
          Write-Host "  $($skill.Name)" -ForegroundColor Yellow -NoNewline
          Write-Dim " -> $target (stale)"
        }
      } elseif (Test-Path $linkPath) {
        Write-Host "  $($skill.Name)" -ForegroundColor Red -NoNewline
        Write-Dim ' (real file, not symlink)'
      } else {
        Write-Dim "  $($skill.Name) (not linked)"
      }
    }
    Write-Host ''
  }

  # Show agents that are not installed
  foreach ($id in $AgentDefs.Keys) {
    $def = $AgentDefs[$id]
    if (-not (Test-Path $def.ConfigDir)) {
      Write-Dim "  $($def.Name) -- not installed ($($def.ConfigDir))"
    }
  }
  Write-Host ''
}

# ── Entry point ────────────────────────────────────────────────────────────

if (-not $Command) {
  Write-Err "Missing command. Use: install, uninstall, or status"
  Write-Host 'Usage: .\link-skills.ps1 [install|uninstall|status] [-DryRun] [-Agents a,b] [-Skills x,y]'
  exit 1
}

if ($DryRun) {
  Write-Host '== DRY RUN (no changes will be made) ==' -ForegroundColor Yellow
  Write-Host ''
}

switch ($Command) {
  'install'   { Invoke-Install }
  'uninstall' { Invoke-Uninstall }
  'status'    { Invoke-Status }
}
