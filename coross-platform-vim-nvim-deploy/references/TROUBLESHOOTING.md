# Troubleshooting Guide

## Symlink Creation Failures

### Windows: "Access Denied" on mklink

**Cause**: User lacks Administrator privileges or Developer Mode is not enabled.

**Solutions (try in order):**
1. Enable Developer Mode: Settings > Update & Security > For developers > Developer Mode (preferred, no elevation needed after)
2. Run PowerShell as Administrator: right-click PowerShell > Run as Administrator
3. Fall back to copying: copy `~/.vim` contents to `%LOCALAPPDATA%\nvim\` instead of symlinking (requires user to manually sync changes)

### Linux/macOS: "Permission denied" on ln -s

**Cause**: Parent directory (`~/.config/`) owned by another user or has restrictive permissions.

**Solutions:**
```bash
# Check ownership
ls -la ~/.config/

# Fix if owned incorrectly
sudo chown -R $USER:$USER ~/.config/
```

## Plugin Installation Failures

### lazy.nvim: "module 'lazy' not found"

**Cause**: `lazy.nvim` not bootstrapped in init.vim.

**Solution**: Ensure the bootstrap code is present at the top of `init.vim`:
```vim
if has('nvim')
  let lazypath = stdpath('data') . '/lazy/lazy.nvim'
  if !isdirectory(lazypath)
    execute '!git clone --filter=blob:none https://github.com/folke/lazy.nvim.git ' . lazypath
  endif
  execute 'set runtimepath+=' . lazypath
endif
```

### vim-plug: "E117: Unknown function: plug#begin"

**Cause**: vim-plug not installed.

**Solution** (Vim):
```bash
curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
  https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
```
Then run `:PlugInstall` in Vim.

### ripgrep/fd not found

**Cause**: Package not installed or not in PATH.

**Solutions:**
- Re-run the dependency installation stage
- Check if the package manager installed the binary under a different name (e.g., `fd-find` vs `fd` on Debian)
- Verify PATH includes the install location

## First-Run Issues

### Neovim: Colors broken or missing

**Cause**: Terminal does not support true color (24-bit).

**Solution**: Add to `init.vim`:
```vim
set termguicolors  " Neovim only, safe via has('nvim') guard
```
If the terminal does not support true color, leave `termguicolors` off and use a 256-color theme.

### Vim: "E319: Sorry, the command is not available in this version"

**Cause**: Using a Neovim-only feature in Vim without the `has('nvim')` guard.

**Solution**: Wrap all Neovim-only commands and Lua calls in `if has('nvim') ... endif` blocks. Check `references/COMPATIBILITY.md` for the full feature comparison.

### "command not found: nvim" after installation

**Cause**: Neovim binary not in PATH.

**Solutions:**
- Windows: restart terminal to pick up Scoop shims
- Linux/macOS: restart shell or run `hash -r` (bash/zsh)
- Verify: `which nvim`

## Rollback Procedure

### Restore from backup

```bash
# List available backups
ls -la ~/.vimrc.backup.*
ls -la ~/.config/nvim.backup.*

# Restore a specific backup
cp ~/.vimrc.backup.20260127 ~/.vimrc
cp -r ~/.config/nvim.backup.20260127 ~/.config/nvim

# Or use the provided script
bash assets/backup-restore.sh --restore 20260127
```

### Manual rollback steps

1. Remove the symlink: `rm ~/.config/nvim` (or delete `%LOCALAPPDATA%\nvim` on Windows)
2. Restore backed-up config: `mv ~/.vimrc.backup.* ~/.vimrc`
3. Remove the unified config: `rm -rf ~/.vim`

## WSL-Specific Issues

### Clipboard not working

**Cause**: WSL does not have native access to the Windows clipboard.

**Solution**: Install `win32yank` on the Windows side and configure clipboard tool in `init.vim`:
```vim
if has('wsl')
  let g:clipboard = {
    \ 'name': 'win32yank-wsl',
    \ 'copy': {
    \    '+': 'win32yank.exe -i --crlf',
    \    '*': 'win32yank.exe -i --crlf',
    \  },
    \ 'paste': {
    \    '+': 'win32yank.exe -o --lf',
    \    '*': 'win32yank.exe -o --lf',
    \  },
    \ 'cache_enabled': 0,
    \}
endif
```

### Slow file operations

**Cause**: Config directory located on `/mnt/c/` (Windows filesystem, 9pfs protocol).

**Solution**: Move `~/.vim/` to the WSL ext4 filesystem (e.g., `/home/username/.vim/`). WSL2 ext4 performance is significantly better than cross-filesystem 9pfs access.
