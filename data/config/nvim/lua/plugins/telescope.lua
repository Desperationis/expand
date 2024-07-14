return {
    "nvim-telescope/telescope.nvim",
    tag = "0.1.8",
    dependencies = {
        "nvim-lua/plenary.nvim",
        "BurntSushi/ripgrep",
        "nvim-treesitter/nvim-treesitter",
        "nvim-tree/nvim-web-devicons",
        "nvim-telescope/telescope-fzf-native.nvim"
    },
    config = function()
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
        vim.keymap.set('n', '<leader><leader>', require('telescope.builtin').current_buffer_fuzzy_find, { desc = '[ ] Find in current file' })
        vim.keymap.set('n', '<leader>sf', require('telescope.builtin').find_files, { desc = '[S]earch [F]iles' })
        vim.keymap.set('n', '<leader>sg', require('telescope.builtin').live_grep, { desc = '[S]earch by [G]rep' })



    end

}
