# Platform-Specific Deployment Notes

## Windows

### Package Manager: Scoop

Scoop is the recommended package manager for Windows. It installs tools to `~/scoop/` without requiring admin rights.

**Bootstrap (if Scoop not installed):**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
irm get.scoop.sh | iex
```

**Verify:**
```powershell
scoop --version
```

**Common packages:**
```powershell
scoop install neovim git ripgrep fd fzf
```

### Path Conventions

- Vim config: `%USERPROFILE%\.vim\` (typically `C:\Users\<name>\.vim\`)
- Vim config file: `%USERPROFILE%\_vimrc` or `%USERPROFILE%\.vimrc`
- Neovim config: `%LOCALAPPDATA%\nvim\` (typically `C:\Users\<name>\AppData\Local\nvim\`)
- Neovim data: `%LOCALAPPDATA%\nvim-data\`

### Symlink on Windows

Windows supports directory symlinks with `mklink /D` or `New-Item -Type SymbolicLink`. Requires either:
- Administrator privileges, OR
- Developer Mode enabled (Settings > Update & Security > For developers)

**PowerShell symlink creation:**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:LOCALAPPDATA\nvim" -Target "$env:USERPROFILE\.vim"
```

If symlink creation fails without admin, prompt user to enable Developer Mode or run as Administrator.

### PowerShell Profile

Add Neovim `bin/` to PATH if not already present (Scoop handles this automatically via shims).

## Linux

### Package Managers

**Debian/Ubuntu (apt):**
```bash
sudo apt update
sudo apt install neovim ripgrep fd-find git curl
# fd is named fd-find on Debian-based systems
# Create symlink for fd command if needed:
mkdir -p ~/.local/bin && ln -s $(which fdfind) ~/.local/bin/fd
```

**RHEL/Fedora (dnf):**
```bash
sudo dnf install neovim ripgrep fd-find git curl
```

**Arch (pacman):**
```bash
sudo pacman -S neovim ripgrep fd git curl
```

### Path Conventions

- Vim config: `~/.vim/`
- Vim config file: `~/.vimrc`
- Neovim config: `~/.config/nvim/`
- Neovim data: `~/.local/share/nvim/`

### Symlink

```bash
# Create Neovim config symlink pointing to shared ~/.vim
mkdir -p ~/.config
ln -sf ~/.vim ~/.config/nvim
```

### No Sudo Access

If the user lacks sudo, try user-mode installation:
1. Build from source to `~/.local/`
2. Use `linuxbrew` (Homebrew for Linux)
3. Use `nix` package manager (user mode)

If none are feasible, report the blockers and suggest the user contact their system administrator.

## macOS

### Package Manager: Homebrew

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install packages
brew install neovim ripgrep fd git curl
```

### Path Conventions

Same as Linux:
- Vim config: `~/.vim/`
- Vim config file: `~/.vimrc`
- Neovim config: `~/.config/nvim/`

### macOS Specifics

- **System Vim**: macOS ships with Vim (usually outdated). Recommend installing via Homebrew.
- **SIP (System Integrity Protection)**: `/usr/bin/vim` is protected. Homebrew installs to `/usr/local/bin/vim` or `/opt/homebrew/bin/vim`.
- **PATH order**: Ensure `/usr/local/bin` (Intel) or `/opt/homebrew/bin` (Apple Silicon) comes before `/usr/bin`.
- **Shell**: macOS 10.15+ uses zsh as default shell. Ensure shell config (`.zshrc`) sets PATH correctly.

## WSL (Windows Subsystem for Linux)

### Detection

Check for WSL by looking at `/proc/version`:
```bash
grep -qi microsoft /proc/version && echo "WSL detected"
```

### WSL-Specific Considerations

- **Treat as Linux** for package management (apt, dnf, etc.)
- **Clipboard integration**: Prompt user whether to configure Windows clipboard sharing.
  - Requires `win32yank` installed on the Windows side
  - Add to `init.vim`: `set clipboard=unnamedplus` with WSL-specific clipboard tool
- **Filesystem performance**: `~/.vim/` should be inside WSL filesystem (not `/mnt/c/`) for performance.
  - WSL1: cross-filesystem access is slow
  - WSL2: ext4 is fast, `/mnt/c` 9pfs is slower
- **Windows Terminal**: Recommend Windows Terminal as the default terminal for best Neovim experience (true color, font support)
