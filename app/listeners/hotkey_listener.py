# app/listeners/hotkey_listener.py

import threading
from pynput import keyboard
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from pynput import keyboard


# Classe para ouvir hotkeys
class HotkeyListener(QtCore.QObject):
    hotkey_pressed = pyqtSignal()

    def __init__(self, hotkey="Ctrl+Shift+S"):
        super().__init__()
        self.current_hotkey = hotkey
        self.listener = None
        self.listener_thread = None
        self.start_listener(self.current_hotkey)

    def start_listener(self, hotkey):
        # Converter a string da hotkey para o formato esperado pelo pynput
        hotkey_pynput = self.convert_hotkey(hotkey)
        # Definir as ações para a hotkey
        self.listener = keyboard.GlobalHotKeys({
            hotkey_pynput: self.on_hotkey
        })
        # Iniciar o listener em um thread separado
        self.listener_thread = threading.Thread(target=self.listener.run)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def convert_hotkey(self, hotkey_str):
        """
        Converte uma string de hotkey no formato 'Ctrl+Shift+S' para o formato esperado pelo pynput,
        que é '<ctrl>+<shift>+s'.
        """
        parts = hotkey_str.lower().split('+')
        return '+'.join(f"<{part}>" if part in ["ctrl", "shift", "alt", "cmd"] else part for part in parts)

    def on_hotkey(self):
        # Emitir o sinal para notificar o thread principal
        self.hotkey_pressed.emit()

    def update_hotkey(self, new_hotkey):
        if self.listener:
            self.listener.stop()
            self.listener_thread.join()
        self.current_hotkey = new_hotkey
        self.start_listener(self.current_hotkey)

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener_thread.join()
