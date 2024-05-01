import os 
import sys
import curses
from rich import print

if "ACTIVATED_EXPAND" not in os.environ:
    print("[bold bright_red]Please run activate.sh as root first.[/bold bright_red]")
    sys.exit(1)



