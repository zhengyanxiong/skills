---
name: coross-platform-vim-nvim-deploy
description: >
  Cross-platform Vim/Neovim unified configuration deployment.
  Deploy shared Vim 8.2+ and Neovim 0.9+ config across Windows, Linux, and macOS.
  Make sure to use this skill whenever the user mentions: setting up vim, installing neovim,
  configuring nvim, vim config, nvim setup, editor environment, dev environment setup,
  vimrc deployment, dotfiles for vim, sharing vim and neovim config, migrating from vim
  to neovim, cross-platform editor config, vim on new machine, vim dependencies (ripgrep/fd),
  vim plugin setup, LSP setup for vim, treesitter config, lazy.nvim setup, 安装vim,
  配置nvim, vim环境搭建, 编辑器配置同步, or any task involving deploying a Vim or Neovim
  development environment across machines — even if the user doesn't explicitly say "deploy."
license: MIT
compatibility: >
  Requires bash (Linux/macOS) or PowerShell 5.1+ (Windows).
  Supports Vim 8.2+ and Neovim 0.9+.
metadata:
  author: developer
  version: "2.0"
  category: dev-environment
  tags: [vim, neovim, cross-platform, deployment, configuration, pipeline, inversion]
---

# Vim/Neovim Cross-Platform Configuration Deployment

## Design Pattern: Pipeline + Inversion

This skill combines two patterns:

**Pipeline** (primary): The deployment follows a strict 4-stage workflow. Each stage has defined inputs, outputs, and verification checkpoints. No stage begins before the previous stage passes its checkpoint.

**Inversion** (Stage 1): Before executing, interview the user to gather environment details. Provide sensible defaults so the user can accept with a single confirmation.

## Pipeline Overview

```
Stage 1: Detect & Interview  →  Stage 2: Install Dependencies  →  Stage 3: Deploy Config  →  Stage 4: Verify
       ↓                              ↓                              ↓                          ↓
  Input: user prompt           Input: confirmed plan         Input: installed tools      Input: deployed config
  Output: deployment plan      Output: ready toolchain       Output: ~/.vim/ + symlink   Output: verification report
  Checkpoint: user confirms    Checkpoint: all pkgs present   Checkpoint: init.vim valid  Checkpoint: both editors OK
```

---

## Stage 1: Environment Detection & User Interview

### Input
The user's request -- may be specific ("install neovim on my mac with lazy.nvim") or vague ("help me set up vim").

### Process

Interview the user to collect these four data points. Explain why each matters so the user understands the tradeoffs:

1. **Target OS** -- Auto-detect from the environment. Why: package managers, paths, and symlink syntax differ per platform. Getting this wrong breaks the entire pipeline.
2. **Current editor state** -- Is Vim installed? Neovim? Neither? Both? Detect versions automatically. Why: determines whether to install fresh or migrate. If Vim < 8.2 or Neovim < 0.9, an upgrade is required for the shared config to work reliably.
3. **Existing config to preserve** -- Path to vimrc/init.vim if any. Why: losing a user's years of customization is unacceptable. Back up everything before touching it.
4. **Plugin manager preference** -- Default to lazy.nvim (Neovim) + vim-plug (Vim fallback). Why: lazy.nvim is the modern standard with lazy-loading; vim-plug provides a lightweight fallback for plain Vim.

**Defaults (use when user provides no input):**
- OS: auto-detect
- Editors: install Neovim if missing; keep existing Vim if present
- Backup: always, with timestamp suffix
- Plugin managers: lazy.nvim + vim-plug fallback

### Output
A deployment plan summarizing detected state and proposed actions. Present to user for confirmation before proceeding.

### Checkpoint
User explicitly confirms the plan. Do NOT proceed to Stage 2 without confirmation.

---

## Stage 2: Dependency Installation

### Input
Confirmed deployment plan from Stage 1.

### Process

Select package manager by detected OS. Why each mapping:

| Platform | Package Manager | Rationale |
|----------|----------------|-----------|
| Windows | Scoop | Installs without admin rights to `~/scoop/`; avoids PATH pollution |
| Ubuntu/Debian | apt | System native; most Ubuntu servers have no other PM |
| macOS | Homebrew | De facto standard on macOS; ships updated formulae |

Install these packages (minimum set for a working environment):
- `neovim` -- the editor itself
- `git` -- plugin installation and config versioning
- `ripgrep` -- telescope.nvim / fzf.vim search backend
- `fd` -- alternative to `find`, used by telescope

Edge cases handled at this stage:
- **Windows without Scoop**: Bootstrap Scoop first, then proceed
- **Linux without sudo**: Attempt user-mode install (build from source to `~/.local/`, or use linuxbrew/nix). Report if impossible.
- **WSL detected**: Treat as Linux. Flag Windows clipboard integration for later.

### Output
All required packages installed and verified on PATH.

### Checkpoint
Run `nvim --version` (and `vim --version` if Vim kept). Both must return without error. Do NOT proceed to Stage 3 with missing tools.

---

## Stage 3: Configuration Deployment

### Input
Verified toolchain from Stage 2.

### Process

Execute in strict order. Each step builds on the previous; skipping creates an inconsistent state:

**Step 3.1: Backup**
Rename `~/.vimrc` and `~/.config/nvim/` to `*.backup.{ISO-date}`.
Why: the deployment must be reversible. A timestamped backup lets the user undo everything with a single command.

**Step 3.2: Create unified root**
Create `~/.vim/` directory structure (init.vim, lua/shared/, plugin/, after/ftplugin/).
Why: this is the single source of truth for both editors. Vim loads `~/.vim/init.vim` directly. Neovim reaches it through the symlink created next.

**Step 3.3: Create Neovim symlink**
- Linux/macOS: `ln -sf ~/.vim ~/.config/nvim`
- Windows: `New-Item -Type SymbolicLink "$env:LOCALAPPDATA\nvim" -Target "$env:USERPROFILE\.vim"`
Why: Neovim looks for config at `~/.config/nvim/`. Symlinking to `~/.vim/` means one set of files serves both editors. No duplication, no drift.

**Step 3.4: Deploy init.vim**
Write the shared entry point. The key design constraint: it must use `if has('nvim')` guards so Neovim loads Lua modules while Vim skips them gracefully. The file must:
- Bootstrap lazy.nvim automatically (Neovim only)
- Configure shared settings (both editors)
- Handle platform-specific quirks (WSL clipboard, Windows shell)
For the full template, load `references/CONFIG_TEMPLATES.md`.

**Step 3.5: Deploy Lua modules**
Write `lua/shared/plugins.lua`, `lua/shared/keymaps.lua`, `lua/shared/compatibility.lua`.
Why: these are Neovim-only; Vim never reads the `lua/` directory. The `compatibility.lua` module wraps API calls in `pcall` for safety.

**Step 3.6: Generate deployment report**
Write `~/.vim/deploy-report.txt` with a summary of every action taken, every file created/modified, and every backup made.
Why: when something goes wrong weeks later, the user can check this report to understand what the deployment did.

### Output
Complete `~/.vim/` directory tree, Neovim symlink, and deployment report.

### Checkpoint
- `~/.vim/init.vim` exists and is readable
- `~/.config/nvim` (or `%LOCALAPPDATA%\nvim`) resolves to `~/.vim/`
- `~/.vim/deploy-report.txt` exists

Do NOT proceed to Stage 4 until all three conditions pass.

---

## Stage 4: Verification & First Run

### Input
Deployed configuration from Stage 3.

### Process

1. **First-run initialization**: Neovim's first launch triggers `:Lazy sync` to install plugins. If vim-plug is configured for Vim fallback, remind the user to run `:PlugInstall` inside Vim.
2. **Headless verification**: Run the following to confirm runtime detection works:
   ```bash
   nvim --headless -c "echo has('nvim')" -c "qa" 2>&1   # Must output: 1
   vim --headless -c "echo has('nvim')" -c "qa" 2>&1     # Must output: 0
   ```
   Why: verifies that `init.vim`'s `if has('nvim')` branching correctly identifies the running editor. If these fail, the shared config is broken.

### Output
Verification results. If both editors initialize without errors, deployment is complete.

### Checkpoint
Both headless checks pass. Report success or specific failures to the user.

---

## Configuration Architecture (Reference)

```
~/.vim/
├── init.vim                    # Shared entry point
├── lua/
│   └── shared/                 # Neovim-only Lua modules
│       ├── keymaps.lua
│       ├── plugins.lua
│       └── compatibility.lua
├── plugin/
│   └── plug.vim                # vim-plug fallback
├── after/
│   └── ftplugin/
└── deploy-report.txt
```

Design rationale: 90% of settings live in shared Vimscript. 10% that need editor-specific behavior use `if has('nvim')` guards. Vim users feel no penalty for not using Neovim.

## Boundary Cases

| Scenario | Handling Strategy |
|----------|------------------|
| No Vim or Neovim installed | Install Neovim (richer features). Offer Vim as optional extra. |
| Only Vim, no Neovim | Prompt: Neovim recommended for LSP/Tree-sitter/Lua. Install on user confirmation. |
| Config file conflicts | Auto-backup with timestamp. Offer `--force` to overwrite without backup. |
| Scoop not installed (Windows) | Bootstrap Scoop first, then proceed. |
| WSL environment | Treat as Linux. Ask about Windows clipboard integration (win32yank). |
| No sudo (Linux) | Attempt user-mode install (linuxbrew, nix, source build). Report if impossible. |
| Symlink creation fails | Check permissions/Developer Mode. Load `references/TROUBLESHOOTING.md`. |
| Config rollback needed | Run `assets/backup-restore.sh` to restore most recent backup. |

## L3 File References

Load these only when the deployment context requires their detail -- never preemptively:

- **`references/COMPATIBILITY.md`**: Vim vs Neovim feature matrix -- shared features, conditional APIs, plugin compatibility table
- **`references/PLATFORM_NOTES.md`**: OS-specific package manager syntax, path conventions, WSL quirks, macOS SIP considerations
- **`references/TROUBLESHOOTING.md`**: Symlink failures, plugin install errors, clipboard issues, rollback procedures
- **`references/CONFIG_TEMPLATES.md`**: Full init.vim and Lua module templates with bootstrap code

## Output Constraints

- **Idempotent**: Running deployment twice produces the same result without errors. Detect existing setup and skip or update. Why: users re-run scripts for confidence; a broken second run destroys trust.
- **Safe by default**: Always back up before modifying. Never overwrite user files without confirmation. Why: Vim config represents years of personal tuning; data loss here is a sharp betrayal of user trust.
- **Platform-aware**: Adapt commands, paths, and package managers to the detected OS. Why: a Linux command on Windows produces cryptic errors that erode confidence in the tool.
- **Informative**: Report every action. If something is skipped, explain why. Why: silent success leaves the user wondering what happened; silent failure is worse.
- **Rollback-ready**: Every deployment generates a timestamped backup. Restoration is one command. Why: the best time to prepare for rollback is before anything goes wrong.
- **Shared-first**: 90% shared Vimscript, 10% editor-specific via `has('nvim')` guard. Why: the shared config is the whole point -- two editors, one source of truth.
- **Lightweight**: Base config startup under 100ms, plugins load on demand. Why: a slow editor feels broken even when it's working correctly.

## Verification Commands

```bash
# Editor versions
vim --version | head -1
nvim --version | head -1

# Symlink check (Linux/macOS)
ls -la ~/.config/nvim

# Symlink check (Windows PowerShell)
ls "$env:LOCALAPPDATA\nvim"

# Runtime detection
nvim --headless -c "echo has('nvim')" -c "qa"   # Expected: 1
vim --headless -c "echo has('nvim')" -c "qa"     # Expected: 0
```
