return {
    "williamboman/mason-lspconfig.nvim",
    tag = "v1.29.0",
    dependencies = {
        "neovim/nvim-lspconfig",
        "williamboman/mason.nvim"
    },
    config = function()
        local mason_lspconfig = require 'mason-lspconfig'
        mason_lspconfig.setup()

        -- Auto setup all LSP's whenever Mason installs a package
        mason_lspconfig.setup_handlers {
          function(server_name)
            require('lspconfig')[server_name].setup{}
          end,
        }

    end
}
