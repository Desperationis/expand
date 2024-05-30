-- Install packer automatically if it is not installed
local install_path = vim.fn.stdpath 'data' .. '/site/pack/packer/start/packer.nvim'
local is_bootstrap = false
if vim.fn.empty(vim.fn.glob(install_path)) > 0 then
  is_bootstrap = true
  vim.fn.system { 'git', 'clone', '--depth', '1', 'https://github.com/wbthomason/packer.nvim', install_path }
  vim.cmd [[packadd packer.nvim]]
end



require('packer').startup(function()
	use 'wbthomason/packer.nvim'

	use { -- LSP Configuration & Plugins
		'neovim/nvim-lspconfig',
		requires = {
		  -- Automatically install LSPs to stdpath for neovim
		  'williamboman/mason.nvim',
		  'williamboman/mason-lspconfig.nvim',

		  -- Useful status updates for LSP
		  { 'j-hui/fidget.nvim', branch = "legacy" },

		  -- Additional lua configuration, makes nvim stuff amazing
		  'folke/neodev.nvim',
		},
	  }

	use { -- Autocompletion
		'hrsh7th/nvim-cmp',
		requires = { 'hrsh7th/cmp-nvim-lsp', 'L3MON4D3/LuaSnip', 'saadparwaiz1/cmp_luasnip' },
	  }

	use 'HiPhish/rainbow-delimiters.nvim'

	use { -- Highlight, edit, and navigate code
		'nvim-treesitter/nvim-treesitter',
	run = function()
		pcall(require('nvim-treesitter.install').update { with_sync = true })
	end,
	}

	use { -- Additional text objects via treesitter
		'nvim-treesitter/nvim-treesitter-textobjects',
		after = 'nvim-treesitter',
	}

	use { "lukas-reineke/indent-blankline.nvim", main = "ibl", opts = {} }

	use 'nvim-lualine/lualine.nvim'
	use 'numToStr/Comment.nvim'

	use 'preservim/nerdtree'

	use 'tpope/vim-fugitive' -- git
	use 'lewis6991/gitsigns.nvim' -- Visualize git changes on the side

	use { "catppuccin/nvim", as = "catppuccin" } -- Colorscheme

	-- Fuzzy Finder (files, lsp, etc)
	use { 'nvim-telescope/telescope.nvim', branch = '0.1.x', requires = { 'nvim-lua/plenary.nvim' } }

	-- Fuzzy Finder Algorithm which requires local dependencies to be built. Only load if `make` is available
	use { 'nvim-telescope/telescope-fzf-native.nvim', run = 'make', cond = vim.fn.executable 'make' == 1 }

	if is_bootstrap then
		require('packer').sync()
	end
end)



if is_bootstrap then
  print '=================================='
  print '    Plugins are being installed'
  print '    Wait until Packer completes,'
  print '       then restart nvim'
  print '=================================='
  return
end


-- Set Preferences
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.linebreak = true
vim.opt.backspace = "indent,eol,start"
vim.opt.guicursor="n-v-c-sm:block,i-ci-ve:ver25,r-cr-o:hor20"

vim.o.mouse = ""
vim.wo.number = true

-- vim.o.updatetime = 250 -- This is how many ms it takes of inactivity to write to swap file
vim.wo.signcolumn = "yes"

-- Set completeopt to have a better completion experience
vim.o.completeopt = 'menuone,noselect'

-- For some custom keymaps
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

-- Terminal mode remap                                                        
vim.cmd [[ :tnoremap <Esc> <C-\><C-n> ]]


-- [[ Highlight on yank ]]
-- See `:help vim.highlight.on_yank()`
local highlight_group = vim.api.nvim_create_augroup('YankHighlight', { clear = true })
vim.api.nvim_create_autocmd('TextYankPost', {
  callback = function()
    vim.highlight.on_yank()
  end,
  group = highlight_group,
  pattern = '*',
})


-- Automatically source and re-compile packer whenever you save this init.lua
local packer_group = vim.api.nvim_create_augroup('Packer', { clear = true })
vim.api.nvim_create_autocmd('BufWritePost', {
  command = 'source <afile> | silent! LspStop | silent! LspStart | PackerCompile',
  group = packer_group,
  pattern = vim.fn.expand '$MYVIMRC',
})
 



-- ANYTHING BELOW IS SETUP FOR ALL PACKAGES

require("catppuccin").setup({
	dim_inactive = {
        enabled = true,
        shade = "dark",
        --percentage = 0.15,
        percentage = 0.5,
    },
	term_colors=true,
	integrations = {
		cmp = true,
		gitsigns = true,
		--nvimtree = true,
		--telescrope = true,
		fidget = true,
		mason = true,
	}
})
vim.cmd [[ colorscheme catppuccin ]]

require('Comment').setup()


require('lualine').setup {
  options = {
    icons_enabled = false,
    theme = 'catppuccin',
    component_separators = '|',
    section_separators = '',
  },
}

require('gitsigns').setup{
  on_attach = function(bufnr)
	local gs = package.loaded.gitsigns

	local function map(mode, l, r, opts)
	  opts = opts or {}
	  opts.buffer = bufnr
	  vim.keymap.set(mode, l, r, opts)
	end

	-- Navigation
	map('n', ']c', function()
	  if vim.wo.diff then return ']c' end
	  vim.schedule(function() gs.next_hunk() end)
	  return '<Ignore>'
	end, {expr=true})

	map('n', '[c', function()
	  if vim.wo.diff then return '[c' end
	  vim.schedule(function() gs.prev_hunk() end)
	  return '<Ignore>'
	end, {expr=true})

	-- Actions
	map({'n', 'v'}, '<leader>hs', ':Gitsigns stage_hunk<CR>')
	map({'n', 'v'}, '<leader>hr', ':Gitsigns reset_hunk<CR>')
	map('n', '<leader>hS', gs.stage_buffer)
	map('n', '<leader>hu', gs.undo_stage_hunk)
	map('n', '<leader>hR', gs.reset_buffer)
	map('n', '<leader>hp', gs.preview_hunk)
	map('n', '<leader>hb', function() gs.blame_line{full=true} end)
	map('n', '<leader>tb', gs.toggle_current_line_blame)
	map('n', '<leader>hd', gs.diffthis)
	map('n', '<leader>hD', function() gs.diffthis('~') end)
	map('n', '<leader>td', gs.toggle_deleted)

	-- Text object
	map({'o', 'x'}, 'ih', ':<C-U>Gitsigns select_hunk<CR>')
  end
}

-- Configure lua_ls to have nvim lua stuff
require("neodev").setup()


-- nvim-cmp supports additional completion capabilities, so broadcast that to servers
local capabilities = vim.lsp.protocol.make_client_capabilities()
capabilities = require('cmp_nvim_lsp').default_capabilities(capabilities)

-- Enable the following language servers
--  Feel free to add/remove any LSPs that you want here. They will automatically be installed.
--
--  Add any additional override configuration in the following tables. They will be passed to
--  the `settings` field of the server config. You must look up that documentation yourself.
local servers = {
   clangd = {},
   pyright = {},
   lua_ls = {
		Lua = {
			workspace = { checkThirdParty = false}, -- Remove annoying prompt for neodev
			telemetry = { enable = false }
		}
   },
   bashls = {},
   arduino_language_server = {},
   cmake = {},
   cssls = {},
   html = {},
   dockerls = {},
   jdtls = {},
   jsonls = {},
   quick_lint_js = {},
   marksman = {},
   ansiblels= {}
}

require("mason").setup()


-- Ensure the servers above are installed
local mason_lspconfig = require 'mason-lspconfig'

mason_lspconfig.setup {
  ensure_installed = vim.tbl_keys(servers),
}

-- Auto setup all LSP's whenever Mason installs a package
mason_lspconfig.setup_handlers {
  function(server_name)
    require('lspconfig')[server_name].setup{
		settings = servers[server_name]
	}
  end,
}

-- Turn on lsp status information
require('fidget').setup({
	window = { -- This is for catppuccin
		blend = 0,
	}
})





-- [[ Configure Telescope ]]
-- See `:help telescope` and `:help telescope.setup()`
require('telescope').setup {
  defaults = {
    mappings = {
      i = {
        ['<C-u>'] = false,
        ['<C-d>'] = false,
      },
    },
  },
}

-- Enable telescope fzf native, if installed
pcall(require('telescope').load_extension, 'fzf')

-- See `:help telescope.builtin`
vim.keymap.set('n', '<leader>?', require('telescope.builtin').oldfiles, { desc = '[?] Find recently opened files' })
vim.keymap.set('n', '<leader><space>', require('telescope.builtin').buffers, { desc = '[ ] Find existing buffers' })
vim.keymap.set('n', '<leader>/', function()
  -- You can pass additional configuration to telescope to change theme, layout, etc.
  require('telescope.builtin').current_buffer_fuzzy_find(require('telescope.themes').get_dropdown {
    winblend = 10,
    previewer = false,
  })
end, { desc = '[/] Fuzzily search in current buffer]' })

vim.keymap.set('n', '<leader>sf', require('telescope.builtin').find_files, { desc = '[S]earch [F]iles' })
vim.keymap.set('n', '<leader>sh', require('telescope.builtin').help_tags, { desc = '[S]earch [H]elp' })
vim.keymap.set('n', '<leader>sw', require('telescope.builtin').grep_string, { desc = '[S]earch current [W]ord' })
vim.keymap.set('n', '<leader>sg', require('telescope.builtin').live_grep, { desc = '[S]earch by [G]rep' })
vim.keymap.set('n', '<leader>sd', require('telescope.builtin').diagnostics, { desc = '[S]earch [D]iagnostics' })



local highlight = {
    "RainbowRed",
    "RainbowYellow",
    "RainbowBlue",
    "RainbowOrange",
    "RainbowGreen",
    "RainbowViolet",
    "RainbowCyan",
}
local hooks = require "ibl.hooks"
-- create the highlight groups in the highlight setup hook, so they are reset
-- every time the colorscheme changes
hooks.register(hooks.type.HIGHLIGHT_SETUP, function()
    vim.api.nvim_set_hl(0, "RainbowRed", { fg = "#E06C75" })
    vim.api.nvim_set_hl(0, "RainbowYellow", { fg = "#E5C07B" })
    vim.api.nvim_set_hl(0, "RainbowBlue", { fg = "#61AFEF" })
    vim.api.nvim_set_hl(0, "RainbowOrange", { fg = "#D19A66" })
    vim.api.nvim_set_hl(0, "RainbowGreen", { fg = "#98C379" })
    vim.api.nvim_set_hl(0, "RainbowViolet", { fg = "#C678DD" })
    vim.api.nvim_set_hl(0, "RainbowCyan", { fg = "#56B6C2" })
end)

vim.g.rainbow_delimiters = { highlight = highlight }
require("ibl").setup { scope = { highlight = highlight } }

hooks.register(hooks.type.SCOPE_HIGHLIGHT, hooks.builtin.scope_highlight_from_extmark)











-- [[ Configure Treesitter ]]
-- See `:help nvim-treesitter`
require('nvim-treesitter.configs').setup {
  -- Add languages to be installed here that you want installed for treesitter
  ensure_installed = { 'c', 'cmake', 'cpp', 'lua', 'python', 'vim', 'arduino', 'bash', 'comment', 'css', 'gitcommit', 'git_rebase', 'html', 'json', 'latex', 'markdown', 'dockerfile', 'java', 'fish'},

  highlight = { enable = true },
  indent = { enable = true, disable = { 'python' } },
  incremental_selection = {
    enable = true,
    keymaps = {
      init_selection = '<c-space>',
      node_incremental = '<c-space>',
      scope_incremental = '<c-s>',
      node_decremental = '<c-backspace>',
    },
  },
  textobjects = {
    select = {
      enable = true,
      lookahead = true, -- Automatically jump forward to textobj, similar to targets.vim
      keymaps = {
        -- You can use the capture groups defined in textobjects.scm
        ['aa'] = '@parameter.outer',
        ['ia'] = '@parameter.inner',
        ['af'] = '@function.outer',
        ['if'] = '@function.inner',
        ['ac'] = '@class.outer',
        ['ic'] = '@class.inner',
      },
    },
    move = {
      enable = true,
      set_jumps = true, -- whether to set jumps in the jumplist
      goto_next_start = {
        [']m'] = '@function.outer',
        [']]'] = '@class.outer',
      },
      goto_next_end = {
        [']M'] = '@function.outer',
        [']['] = '@class.outer',
      },
      goto_previous_start = {
        ['[m'] = '@function.outer',
        ['[['] = '@class.outer',
      },
      goto_previous_end = {
        ['[M'] = '@function.outer',
        ['[]'] = '@class.outer',
      },
    },
    swap = {
      enable = true,
      swap_next = {
        ['<leader>a'] = '@parameter.inner',
      },
      swap_previous = {
        ['<leader>A'] = '@parameter.inner',
      },
    },
  },
}
















-- nvim-cmp setup
local cmp = require 'cmp'
local luasnip = require 'luasnip'

cmp.setup {
  snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  mapping = cmp.mapping.preset.insert {
    ['<C-d>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),
    ['<C-Space>'] = cmp.mapping.complete(),
    ['<CR>'] = cmp.mapping.confirm {
      behavior = cmp.ConfirmBehavior.Replace,
      select = true,
    },
    ['<Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_next_item()
      elseif luasnip.expand_or_jumpable() then
        luasnip.expand_or_jump()
      else
        fallback()
      end
    end, { 'i', 's' }),
    ['<S-Tab>'] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_prev_item()
      elseif luasnip.jumpable(-1) then
        luasnip.jump(-1)
      else
        fallback()
      end
    end, { 'i', 's' }),
  },
  sources = {
    { name = 'nvim_lsp' },
    { name = 'luasnip' },
  },
}

vim.api.nvim_set_keymap('n', '<C-a>', [[:!npx prettier -w %<CR>]], { noremap = true, silent = true })
vim.keymap.set( "i", "jk", "<esc>") 
