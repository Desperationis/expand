return {
    "hrsh7th/nvim-cmp",
    dependencies = {
            "neovim/nvim-lspconfig",
            "L3MON4D3/LuaSnip",
			"hrsh7th/cmp-nvim-lsp", -- lsp auto-completion
			"hrsh7th/cmp-buffer", -- buffer auto-completion
			"hrsh7th/cmp-path", -- path auto-completion
			"hrsh7th/cmp-cmdline", -- cmdline auto-completion
		},
        config = function()
            local luasnip = require("luasnip")
            local cmp = require("cmp")

            cmp.setup({
        snippet = {
            -- REQUIRED - you must specify a snippet engine
            expand = function(args)
                require('luasnip').lsp_expand(args.body) 
            end,
        },


        -- I like to go through all the autocomplete options with tab and
        -- shift+tab
        mapping = cmp.mapping.preset.insert({
            --- Tab
            ["<Tab>"] = cmp.mapping(function(fallback)
              if cmp.visible() then
                cmp.select_next_item()
              elseif luasnip.expand_or_jumpable() then
                luasnip.expand_or_jump()
              else
                fallback()
              end
            end, { "i", "s" }), -- i - insert mode; s - select mode

            --- Shift + Tab
            ["<S-Tab>"] = cmp.mapping(function(fallback)
                if cmp.visible() then
                    cmp.select_prev_item()
                elseif luasnip.jumpable( -1) then
                    luasnip.jump( -1)
                else
                    fallback()
                end
            end, { "i", "s" }),
        }),

      formatting = {
          fields = { 'abbr', 'menu' },

          -- When an option is selected, show what engine it came from
          format = function(entry, vim_item)
              vim_item.menu = ({
                  nvim_lsp = '[Lsp]',
                  luasnip = '[Luasnip]',
                  buffer = '[nvim]',
                  path = '[Path]',
              })[entry.source.name]
              return vim_item
          end,
      },

      -- Set source precedence
      sources = cmp.config.sources({
          { name = 'nvim_lsp' },    -- For nvim-lsp
          { name = 'luasnip' },     -- For luasnip user
          { name = 'buffer' },      -- For buffer word completion
          { name = 'path' },        -- For path completion
      })
    })


    end,

}
