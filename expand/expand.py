"""
This is the main script that is run on `python3 -m expand`
"""

import traceback
import logging
import os
import sys
from expand import curses_cli

"""
if "ACTIVATED_EXPAND" not in os.environ:
    print("[bold bright_red]Please run activate.sh as root first.[/bold bright_red]")
    sys.exit(1)
"""

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

    cli = curses_cli.curses_cli()

    try:
        cli.setup()
        cli.loop()

    except:
        logging.error(traceback.format_exc())

    finally:
        cli.end()
