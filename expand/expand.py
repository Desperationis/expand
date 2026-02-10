"""expand - Interactive TUI for installing software via Ansible playbooks.

Usage:
  expand [options]

Options:
  -h --help          Show this screen.
  -v --verbose       Write debug output to `expand.log`
  --user=<name>      Install packages for specified user [default: root]
  --workers=<n>      Number of parallel workers for status checks [default: 4]
"""

import os
import sys
import traceback
import logging
import pwd
import grp


def main():
    """
    This function is what is called when the module is run.
    """

    if "ACTIVATED_EXPAND" not in os.environ:
        print("Please run activate.sh as the root user first.")
        sys.exit(1)

    from docopt import docopt
    from expand import curses_cli
    from expand.util import change_user

    args = docopt(__doc__)

    if args["--verbose"]:
        logging.basicConfig(
            filename="expand.log",
            filemode="a",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.DEBUG,
        )

    # Parse workers option
    workers = int(args["--workers"])

    # Curses is initialized first because it doesn't like changing user in this
    # context. If it is initialized after changing user, the program won't work
    # on some computers.
    cli = curses_cli.curses_cli(workers=workers)

    if args["--user"]:
        try:
            change_user(args["--user"])
        except:
            print(f"\"{args['--user']}\" is not a valid user.")
            sys.exit(1)

        # If the user has never used ansible before, ~/.ansible will belong to
        # root, and any AnyUserNoEscalation operations will fail due to
        # priviledge because it can't write to ~/.ansible/tmp
        def fix_user_group(folder):
            folder = os.path.expanduser(folder)
            os.makedirs(folder, exist_ok=True)

            uid = pwd.getpwnam(args["--user"]).pw_uid
            gid = grp.getgrnam(args["--user"]).gr_gid

            os.chown(folder, uid, gid)

        fix_user_group("~/.ansible")
        fix_user_group("~/.ansible/tmp/")

    try:
        cli.setup()
        cli.loop()

    except:
        logging.error(traceback.format_exc())

    finally:
        cli.end()
