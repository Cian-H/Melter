import flet as ft
from loguru import logger
import sys

from melter.gui import main


logger.remove()
logger.add(sys.stderr, level="ERROR")


if __name__ == "__main__":
    ft.app(main)
