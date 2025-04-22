-- Hint: use `:h <option>` to figure out the meaning if needed
-- vim.opt.clipboard = 'unnamedplus'   -- use system clipboard for yank
vim.opt.completeopt = {'menu', 'menuone', 'noselect'}
vim.opt.mouse = ''                  -- Does NOT allow the mouse to be used in Nvim

-- Tab
vim.opt.tabstop = 4                 -- number of visual spaces per TAB
vim.opt.softtabstop = 4             -- number of spacesin tab when editing
vim.opt.shiftwidth = 4              -- insert 4 spaces on a tab
vim.opt.expandtab = true            -- tabs are spaces, mainly because of python
vim.opt.linebreak = true            -- If line is too long, break by word instead of char

-- UI config
vim.opt.number = true               -- show absolute number
vim.opt.relativenumber = true       -- add numbers to each line on the left side
vim.opt.cursorline = true           -- highlight cursor line underneath the cursor horizontally
vim.opt.splitbelow = true           -- open new vertical split bottom
vim.opt.splitright = true           -- open new horizontal splits right
vim.opt.termguicolors = true        -- enabl 24-bit RGB color in the TUI
vim.opt.showmode = false            -- we are experienced, wo don't need the "-- INSERT --" mode hint

-- Searching
vim.opt.incsearch = true            -- search as characters are entered
vim.opt.hlsearch = false            -- do not highlight matches
vim.opt.ignorecase = true           -- ignore case in searches by default
vim.opt.smartcase = true            -- but make it case sensitive if an uppercase is entered


-- My own
vim.wo.signcolumn = "yes"
vim.opt.backspace = "indent,eol,start" -- Delete things in a more intuitive way
vim.opt.guicursor="n-v-c-sm:block,i-ci-ve:ver25,r-cr-o:hor20"
vim.wo.number = true                -- Show line number
vim.o.listchars = "tab:| ,trail:·,extends:>,precedes:<,space:·" -- See spaces
vim.o.list = true -- Show spaces
vim.opt.clipboard = "unnamedplus"  -- Uses clipboard for yank/delete
