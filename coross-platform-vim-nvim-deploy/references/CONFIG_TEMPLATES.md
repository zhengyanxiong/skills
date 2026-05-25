# Configuration Templates

## init.vim -- Smart Shared Entry Point

```vim
" init.vim -- Shared configuration for Vim 8.2+ and Neovim 0.9+
" Vim loads this directly; Neovim loads it via ~/.config/nvim -> ~/.vim symlink

" ── Neovim Bootstrap (Vim skips this block) ──────────────────────
if has('nvim')
  " Install lazy.nvim if not present
  let lazypath = stdpath('data') . '/lazy/lazy.nvim'
  if !isdirectory(lazypath)
    silent! execute '!git clone --filter=blob:none https://github.com/folke/lazy.nvim.git ' . lazypath
  endif
  execute 'set runtimepath+=' . lazypath

  " Load Lua configuration
  lua require('shared.plugins')
  lua require('shared.keymaps')
endif

" ── Vim Bootstrap (Neovim skips this block) ──────────────────────
if !has('nvim')
  set nocompatible
  filetype plugin indent on

  " Optional: vim-plug (install if needed)
  " if empty(glob('~/.vim/autoload/plug.vim'))
  "   silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
  "     \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  " endif
  " call plug#begin('~/.vim/plugged')
  " Plug 'preservim/nerdtree'
  " Plug 'tpope/vim-fugitive'
  " call plug#end()
endif

" ── Shared Settings (Works in Both) ──────────────────────────────
set number
set relativenumber
set tabstop=4
set shiftwidth=4
set expandtab
set smartindent
set mouse=a
set clipboard=unnamedplus
set ignorecase
set smartcase
set hlsearch
set incsearch
set termguicolors
set updatetime=300
set signcolumn=yes
set cursorline
set splitright
set splitbelow

" Leader key
let mapleader = ' '
let maplocalleader = ' '

" ── Shared Keybindings ───────────────────────────────────────────
" Window navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Clear search highlight
nnoremap <leader>h :nohlsearch<CR>

" ── Platform Detection ───────────────────────────────────────────
if has('wsl')
  " WSL clipboard integration (requires win32yank on Windows side)
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

if has('win32') || has('win64')
  " Windows-specific: use PowerShell as default shell
  set shell=powershell
  set shellcmdflag=-command
endif
```

## Lua: plugins.lua -- lazy.nvim Configuration

```lua
-- lua/shared/plugins.lua
-- Only loaded by Neovim (via if has('nvim') guard in init.vim)

require('lazy').setup({
  -- Color scheme
  { 'catppuccin/nvim', name = 'catppuccin', priority = 1000 },

  -- LSP
  { 'neovim/nvim-lspconfig' },
  { 'williamboman/mason.nvim' },
  { 'williamboman/mason-lspconfig.nvim' },
  { 'hrsh7th/nvim-cmp',
    dependencies = {
      'hrsh7th/cmp-nvim-lsp',
      'hrsh7th/cmp-buffer',
      'hrsh7th/cmp-path',
      'L3MON4D3/LuaSnip',
    },
  },

  -- Tree-sitter
  { 'nvim-treesitter/nvim-treesitter', build = ':TSUpdate' },

  -- Fuzzy finder
  { 'nvim-telescope/telescope.nvim', dependencies = { 'nvim-lua/plenary.nvim' } },

  -- Git
  { 'lewis6991/gitsigns.nvim' },

  -- Which-key
  { 'folke/which-key.nvim' },

  -- File explorer
  { 'nvim-neo-tree/neo-tree.nvim', dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-tree/nvim-web-devicons',
    'MunifTanjim/nui.nvim',
  }},
})

-- Color scheme
vim.cmd.colorscheme 'catppuccin-mocha'
```

## Lua: keymaps.lua

```lua
-- lua/shared/keymaps.lua
-- Only loaded by Neovim (via if has('nvim') guard in init.vim)

local map = vim.keymap.set

-- Telescope
map('n', '<leader>ff', '<cmd>Telescope find_files<CR>')
map('n', '<leader>fg', '<cmd>Telescope live_grep<CR>')
map('n', '<leader>fb', '<cmd>Telescope buffers<CR>')

-- LSP
map('n', 'gd', vim.lsp.buf.definition)
map('n', 'gr', vim.lsp.buf.references)
map('n', 'K', vim.lsp.buf.hover)
map('n', '<leader>rn', vim.lsp.buf.rename)
map('n', '<leader>ca', vim.lsp.buf.code_action)

-- Neo-tree
map('n', '<leader>e', '<cmd>Neotree toggle<CR>')
```

## Lua: compatibility.lua

```lua
-- lua/shared/compatibility.lua
-- Safe wrapper for Neovim API calls -- prevents crashes if called in unexpected contexts

local M = {}

function M.is_available()
  return vim.api ~= nil and vim.fn.has('nvim') == 1
end

function M.safe_keymap(mode, lhs, rhs, opts)
  if M.is_available() then
    vim.keymap.set(mode, lhs, rhs, opts or {})
  end
end

function M.safe_autocmd(event, opts)
  if M.is_available() then
    vim.api.nvim_create_autocmd(event, opts)
  end
end

return M
```
