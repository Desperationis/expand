"""
This file is in charge of drawing the UI to the screen.
"""


import curses
import subprocess
import os
import pwd
import shutil
from expand import util
from expand.failure_cache import FailureCache
from expand.gui_elements import ChoicePreview, Choice
from expand.colors import init_colors
from expand.priviledge import AnyUserNoEscalation, OnlyRoot
from expand.expansion_card import ExpansionCard

class package_select:
    def __init__(self, category: int, selection: int):
        self.category = category
        self.selection = selection

    def __hash__(self):
        return hash(self.category * 100 + self.selection)

    def __eq__(self, other):
        return isinstance(other, package_select) and self.category == other.category and self.selection == other.selection

class curses_cli:
    def __init__(self) -> None:
        self.stdscr = curses.initscr()
        self.show_hidden = False

    def should_hide(self, choice: 'Choice') -> bool:
        """Check if a choice should be hidden based on privilege, probes, and install status."""
        # Hide OnlyRoot items if user is not root
        privilege = choice.expansion_card.get_priviledge_level()
        if isinstance(privilege, OnlyRoot) and os.getuid() != 0:
            return True

        # Hide items with failing probes
        if len(choice.failing_probes()) > 0:
            return True

        # Hide installed packages
        if choice.installed_status() == "Installed":
            return True

        return False

    def get_visible_choices(self, choices: list) -> list[tuple[int, 'Choice']]:
        """Return list of (original_index, choice) for visible items."""
        if self.show_hidden:
            return list(enumerate(choices))
        return [(i, c) for i, c in enumerate(choices) if not self.should_hide(c)]

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

        # Add every folder in ansible/ dynamically
        base_dir = "ansible/"
        categories = []
        for entry in os.scandir(base_dir):
            if entry.is_dir() and not entry.name.startswith('.'):
                dir_path = os.path.join(base_dir, entry.name)
                categories.append((entry.name, get_choices_from_folder(dir_path)))

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
            visible_choices = self.get_visible_choices(current_display)
            rows, cols = self.stdscr.getmaxyx()

            self.stdscr.erase()

            user_info = pwd.getpwnam(os.environ["USER"])
            self.stdscr.addstr(0, 0, f"ENV: {os.environ['USER']}  UID: {user_info.pw_uid} EUID: {os.geteuid()}", 0)

            # Draw Categories
            running_length = 0
            for i, elem in enumerate(categories):
                attrs = 0
                if i == current_category:
                    attrs |= curses.A_REVERSE


                self.stdscr.addstr(2, 3 + running_length, elem[0], attrs)
                running_length += len(elem[0]) + 2

            self.stdscr.addstr(4, 0, "Please Select:", 0)

            for display_idx, (orig_idx, elem) in enumerate(visible_choices):
                chosen = False
                for s in selections:
                    if orig_idx == s.selection and s.category == current_category:
                        chosen = True
                        break

                elem.set_chosen(chosen or display_idx == hover)
                elem.set_hover(display_idx == hover)

                y = display_idx + 6
                x = 5
                elem.draw(self.stdscr, y, x, cols - x - 5)

            # Draw legend at bottom
            hidden_count = len(current_display) - len(visible_choices)
            legend = "TAB: select  h: show all" if hidden_count > 0 or self.show_hidden else "TAB: select"
            if self.show_hidden and hidden_count > 0:
                legend = "TAB: select  h: hide installed/incompatible"
            try:
                self.stdscr.addstr(rows - 1, 0, legend, curses.A_DIM)
            except curses.error:
                pass

            # 5 from offset of `Choice`, 3 for offset
            x = round(cols - (cols / 3))
            if x + 3 > Choice.get_min_width() + 5 and len(visible_choices) > 0:
                hovered_choice = visible_choices[hover][1]
                preview = ChoicePreview(hovered_choice.name, hovered_choice.file_path)
                preview.draw(self.stdscr, 0, x, cols - x, rows)

            c = self.stdscr.getch()
            if c == curses.KEY_UP or c == ord("k"):
                hover -= 1
            elif c == curses.KEY_DOWN or c == ord("j"):
                hover += 1
            elif c == curses.KEY_RIGHT or c == ord("l"):
                current_category += 1
                hover = 0
                #selections.clear()
            elif c == curses.KEY_LEFT:
                current_category -= 1
                hover = 0
                #selections.clear()
            elif c == ord("h"):
                self.show_hidden = not self.show_hidden
                hover = 0
            elif c == 9:  # Tab
                if len(visible_choices) > 0:
                    orig_idx = visible_choices[hover][0]
                    obj = package_select(current_category, orig_idx)

                    existing = False
                    for s in selections:
                        if s.category == current_category and s.selection == orig_idx:
                            existing = True
                            break

                    if existing:
                        selections.remove(obj)
                    else:
                        selections.add(obj)

            elif c == curses.KEY_ENTER or c == 10:
                self.end()

                # Run Playbooks
                for i in selections:
                    current_display = categories[i.category][1]
                    file_path = os.path.abspath(current_display[i.selection].file_path)

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
                    tmp = "root"
                    if isinstance(priviledge, AnyUserNoEscalation):
                        tmp = pwd.getpwuid(os.getuid()).pw_name

                    p = subprocess.Popen(["ansible-playbook", file_path], user=tmp)
                    p.wait()

                    # For some reason the Ansible tmp files are owned by root
                    # when run with EUID 0. Just clear out cache to avoid
                    # permission errors on rewriting temporary files.
                    ansible_tmp_dir = os.path.expanduser("~/.ansible/tmp")
                    if os.path.exists(ansible_tmp_dir):
                        shutil.rmtree(ansible_tmp_dir)

                    package_name = current_display[i.selection].name
                    if p.returncode == 0:
                        # Success - clear any failure entry
                        FailureCache.clear_failed(package_name)
                    else:
                        # Failure - record it
                        FailureCache.set_failed(package_name)

                    # Clear cached status so it gets re-evaluated
                    current_display[i.selection].clear_installed_status()

                    # AnyUserEscalation does weird things with permissions that
                    # I will not get into here that interferes with most
                    # programs installed on HOME. So, make everything in HOME
                    # belong to the user, because that is how it is supposed to
                    # be in the first place.
                    own_user = pwd.getpwuid(os.getuid()).pw_name
                    p = subprocess.Popen(f"chown -R {own_user}:{own_user} {os.path.expanduser('~')}".split(" "), user="root")
                    p.wait()

                # Everything ran successfully, reset requirements
                categories = self.create_ansible_data_structure()
                selections.clear()

                self.setup()

            current_category %= len(categories)

            if len(visible_choices) > 0:
                hover %= len(visible_choices)
            else:
                hover = 0

            self.stdscr.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
