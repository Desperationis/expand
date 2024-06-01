"""expand

Usage:
  expand [--user=<name>] [-v | --verbose]

Options:
  -h --help     Show this screen.
  -v --verbose  Write `expand.log`
  --user=<name> Change User [default: root]
"""

import os
import sys
if "ACTIVATED_EXPAND" not in os.environ:
    print("[bold bright_red]Please run activate.sh as the root user first.[/bold bright_red]")
    sys.exit(1)


import traceback
import logging
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


def main():
    """
    This function is what is called when the module is run.
    """

    if args["--user"]:
        change_user(args["--user"])

    cli = curses_cli.curses_cli()

    try:
        cli.setup()
        cli.loop()

    except:
        logging.error(traceback.format_exc())

    finally:
        cli.end()
