import curses


expand_color_palette = {}

def init_colors():
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    expand_color_palette["NORMAL"] = curses.color_pair(0)
    expand_color_palette["RED"] = curses.color_pair(1)
    expand_color_palette["GREEN"] = curses.color_pair(2)
    expand_color_palette["YELLOW"] = curses.color_pair(3)



