import traceback
import time
import logging
from .curses_cli import *

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
    error_str = ""
    cli = curses_cli()

    try:
        cli.setup()
        cli.loop()


    except Exception as e:
        error_str = traceback.format_exc()

    finally:
        cli.end()
        if len(error_str) > 0:
            logging.error(error_str)

