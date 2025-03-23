# main.py
import sys
from PyQt5.QtWidgets import QApplication
from app.main_app import MainApp
from app.utils.settings import load_fonts, set_global_font
from app import __version__


def main():
    app = MainApp(sys.argv)
    load_fonts()
    set_global_font(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

