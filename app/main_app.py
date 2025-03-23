# app/main_app.py

from PyQt5.QtWidgets import QApplication
from app.utils.settings import load_hotkey
from app.listeners.hotkey_listener import HotkeyListener
from app.main_window import MainWindow

#MainApp é a classe principal da aplicação, responsável por inicializar a janela principal e o listener de hotkey.
class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        saved_hotkey = load_hotkey()
        self.hotkey_listener = HotkeyListener(hotkey=saved_hotkey)
        self.main_window = MainWindow()
        self.hotkey_listener.hotkey_pressed.connect(self.main_window.start_screenshot)
        self.main_window.show()


    def update_hotkey(self, new_hotkey):
        self.hotkey_listener.update_hotkey(new_hotkey)
        print(f"Hotkey atualizada para: {new_hotkey}")

    def quit(self):
        self.hotkey_listener.stop()
        super().quit()
