return { 
    "lukas-reineke/indent-blankline.nvim", 
    main = "ibl", 
    dependencies = {
        "nvim-treesitter/nvim-treesitter"
    },
    config = function()
        require("ibl").setup({
            indent = { 
                char = "┊", 
                tab_char = "║", 
                smart_indent_cap = false
            },
            whitespace = { highlight = { "Whitespace", "NonText" } },
            scope = {
                char = "▍"
            }




        })

    end
}
