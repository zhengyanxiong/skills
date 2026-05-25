# Vim vs Neovim Compatibility Reference

## Shared Features (Work in Both)

These features require no conditional branching:

- Vimscript 9.0 syntax (Vim 8.2+ / Neovim 0.9+)
- `autocmd`, `augroup`, `map` commands
- `set` options: `number`, `tabstop`, `shiftwidth`, `expandtab`, `mouse`, `clipboard`
- `filetype plugin indent on`
- `syntax on` / `syntax enable`
- `colorscheme` (most themes)
- Built-in packages (`packadd`, `packpath`)
- `terminal` (both have `:term` since Vim 8.1 / Neovim 0.1)

## Conditionally Loaded Features

Use `if has('nvim')` to guard these:

| Feature | Neovim | Vim | Notes |
|---------|--------|-----|-------|
| Lua config | Native `lua require()` | Not supported | Place Lua files in `lua/`, Vim ignores |
| LSP | Built-in `vim.lsp` | Requires plugin (coc.nvim, ALE) | Neovim 0.9+ has native LSP |
| Tree-sitter | Built-in `vim.treesitter` | Not available | Syntax highlighting engine |
| Floating windows | `nvim_open_win()` | `popup_create()` (Vim 8.2+) | API differs, use abstraction |
| Virtual text | `nvim_buf_set_virtual_text()` | `prop_type_add()` (Vim 9.0+) | Different APIs |
| `vim.ui` module | `vim.ui.input()`, `vim.ui.select()` | Not available | Used by plugins for UI |

## Neovim-Exclusive Features

These have no Vim equivalent:

- `vim.api.*` -- comprehensive Lua API
- `vim.diagnostic` -- built-in diagnostic framework
- `vim.lsp.buf.*` -- LSP actions (formatting, hover, definition)
- `vim.keymap.set()` -- modern key mapping Lua API
- `vim.opt` -- option access in Lua
- Remote plugins (`:CheckHealth`, `rplugin`)
- `:Lazy` plugin manager commands
- `vim.cmd()` -- execute Vimscript from Lua

## Vim-Exclusive Features

- `:smile` -- easter egg (not a practical concern)
- Some `+` features at compile time (`+clipboard`, `+python3`) -- Neovim has these as defaults

## Plugin Compatibility Table

| Plugin | Neovim | Vim | Notes |
|--------|--------|-----|-------|
| lazy.nvim | Native | Not supported | Primary Neovim plugin manager |
| vim-plug | Works | Native | Fallback for Vim |
| nvim-lspconfig | Native | Not supported | Requires `:LspInfo` setup |
| coc.nvim | Works | Works | Alternative LSP client |
| telescope.nvim | Native | Not supported | Neovim fuzzy finder |
| fzf.vim | Works | Works | Shared fuzzy finder |
| nvim-treesitter | Native | Not supported | |
| nerdtree | Works | Works | File explorer |
| vim-airline | Works | Works | Status line |
| which-key.nvim | Native | Not supported | |
| gitsigns.nvim | Native | Not supported | |
| vim-fugitive | Works | Works | Git integration |

## Lua API Safety Pattern

When writing Lua modules for shared config, always wrap Neovim API calls:

```lua
-- compatibility.lua
local M = {}

local function safe_call(fn, fallback)
  local ok, result = pcall(fn)
  if not ok then
    return fallback
  end
  return result
end

M.set_keymap = function(mode, lhs, rhs, opts)
  if vim.api then
    vim.keymap.set(mode, lhs, rhs, opts or {})
  end
end

return M
```

Neovim will execute the Lua code normally; Vim will never load Lua files, so no error occurs.
