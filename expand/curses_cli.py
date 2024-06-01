"""
This file is in charge of drawing the UI to the screen.
"""


import curses
import subprocess
import os
import pwd
import shutil
from expand import util
from expand.cache import InstalledCache
from expand.gui_elements import ChoicePreview, Choice
from expand.colors import init_colors 
from expand.priviledge import AnyUserNoEscalation, OnlyRoot
from expand.expansion_card import ExpansionCard

class curses_cli:
    def __init__(self) -> None:
        self.stdscr = curses.initscr()

    def setup(self):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()  # Without this color pair has no transparent background
        curses.set_escdelay(25)  # Without this there is a lag when pressing escape
        self.stdscr.keypad(True)

        init_colors()

    def create_ansible_data_structure(self):
        # `categories` defines the possible pages available to `expand`:
        # [ ("packages", list[Choice]), ("config", list[Choice]), ... ]
        categories = []

        def get_choices_from_folder(folder) -> list[Choice]:
            files = util.get_files(folder)
            display = map(lambda name: Choice(name, files[name]), files)
            return list(display)

        categories.append(("packages", get_choices_from_folder("ansible/packages/")))
        categories.append(("config", get_choices_from_folder("ansible/config/")))

        return categories


    def loop(self):
        categories = self.create_ansible_data_structure()

        # Index of Current Category
        current_category = 0

        # For selection
        hover = 0
        selections = set()

        while True:
            current_display = categories[current_category][1]
            rows, cols = self.stdscr.getmaxyx()

            self.stdscr.erase()

            user_info = pwd.getpwnam(os.environ["USER"])
            self.stdscr.addstr(0, 0, f"ENV: {os.environ['USER']}  UID: {user_info.pw_uid} EUID: {os.geteuid()}", 0)
            
            for i, elem in enumerate(categories):
                attrs = 0
                if i == current_category:
                    attrs |= curses.A_REVERSE

                self.stdscr.addstr(2, i * 10 + 3, elem[0], attrs)

            self.stdscr.addstr(4, 0, "Please Select", 0)

            for i, elem in enumerate(current_display):
                elem.set_chosen(i in selections or i == hover)
                elem.set_hover(i == hover)

                y = i + 6
                x = 5
                elem.draw(self.stdscr, y, x, cols - x - 5)

            # 5 from offset of `Choice`, 3 for offset
            x = round(cols - (cols / 3))
            if x + 3 > Choice.get_min_width() + 5:
                preview = ChoicePreview(current_display[hover].name, current_display[hover].file_path)
                preview.draw(self.stdscr, 0, x, cols - x, rows)

            c = self.stdscr.getch()
            if c == curses.KEY_UP or c == ord("k"):
                hover -= 1
            elif c == curses.KEY_DOWN or c == ord("j"):
                hover += 1
            elif c == curses.KEY_RIGHT or c == ord("l"):
                current_category += 1
                hover = 0
                selections.clear()
            elif c == curses.KEY_LEFT or c == ord("h"):
                current_category += 1
                hover = 0
                selections.clear()
            elif c == 9:  # Tab
                if hover in selections:
                    selections.remove(hover)
                else:
                    selections.add(hover)
            elif c == curses.KEY_ENTER or c == 10:
                self.end()

                # Run Playbooks
                for i in selections:
                    file_path = os.path.abspath(current_display[i].file_path)

                    priviledge = ExpansionCard(file_path).get_priviledge_level()

                    # The choices I made here a bit confusing so I'll try to explain. 
                    #
                    # At this point in the code, EUID == 0 and UID is set to
                    # the user the user is trying to install things too. We
                    # have the power of root but not necessarily the identity.
                    #
                    # OnlyRoot runs as UID == 0 and EUID == 0
                    # AnyUserEscalation runs as UID == 0 and EUID == 0, but env variables are set
                    # AnyUserEscalation runs as (UID == EUID) != 0
                    #
                    # In all cases, UID == EUID. Popen can temporarily run any
                    # command with both of those variables set to the UID ==
                    # EUID of any `user`. So, in this code we just use UID to
                    # keep track of who to downgrade to in the case of
                    # AnyUserNoEscalation, and in every other case run as root.
                    user = "root"
                    local = True
                    if isinstance(priviledge, OnlyRoot):
                        local = False
                    if isinstance(priviledge, AnyUserNoEscalation):
                        user = pwd.getpwuid(os.getuid()).pw_name

                    p = subprocess.Popen(["ansible-playbook", file_path], user=user)
                    p.wait()

                    # For some reason the Ansible tmp files are owned by root
                    # when run with EUID 0. Just clear out cache to avoid
                    # permission errors on rewriting temporary files.
                    ansible_tmp_dir = os.path.expanduser("~/.ansible/tmp")
                    if os.path.exists(ansible_tmp_dir):
                        shutil.rmtree(ansible_tmp_dir)

                    status = p.returncode == 0

                    if local:
                        InstalledCache.set_local_status(current_display[i].name, user, status)
                    else:
                        InstalledCache.set_global_status(current_display[i].name, status)

                # Everything ran successfully, reset requirements
                categories = self.create_ansible_data_structure()
                selections.clear()

                self.setup()

            current_category %= len(categories)

            hover %= len(current_display)

            self.stdscr.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
