# app/utils/settings.py

import os
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QFontDatabase
from app.utils.decorators import measure_time


def load_name():
    settings = QtCore.QSettings("Echo", "Echo")
    return settings.value("name", "")

def save_name(name):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("name", name)

def load_api_key():
    settings = QtCore.QSettings("Echo", "Echo")
    return settings.value("OPENAI_API_KEY", "")

def save_api_key(api_key):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("OPENAI_API_KEY", api_key)

# @measure_time
def load_theme():
    settings = QtCore.QSettings("Echo", "Echo")
    return settings.value("THEME", "light")

def save_theme(theme):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("THEME", theme)

def load_hotkey():
    settings = QtCore.QSettings("Echo", "Echo")
    return settings.value("HOTKEY", "Ctrl+Shift+S")

def save_hotkey(hotkey):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("HOTKEY", hotkey)

def load_context_setting():
    settings = QtCore.QSettings("Echo", "Echo")
    value = settings.value("MAINTAIN_CONTEXT", True)
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() == 'true'
    elif isinstance(value, int):
        return bool(value)
    else:
        return True  # Valor padrão

def save_context_setting(value):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("MAINTAIN_CONTEXT", value)

def save_max_context(value):
    settings = QtCore.QSettings("Echo", "Echo")
    settings.setValue("MAX_CONTEXT_MESSAGES", value)

def load_max_context():
    settings = QtCore.QSettings("Echo", "Echo")
    value = settings.value("MAX_CONTEXT_MESSAGES", 2)
    # Converter o valor para inteiro
    try:
        return int(value)
    except (TypeError, ValueError):
        return 2  # Valor padrão
    

def resource_path(relative_path):
    """Obtenha o caminho absoluto para os recursos, funciona tanto no dev quanto no executável compilado"""
    try:
        # Quando compilado com PyInstaller, os recursos são extraídos para uma pasta temporária
        base_path = sys._MEIPASS
    except Exception:
        # No ambiente de desenvolvimento, usa o caminho normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#funcao debug para apagar todas as configuracoes
def clear_all_settings():
    settings = QtCore.QSettings("Echo", "Echo")
    settings.clear()
    settings.sync()
    print("Todas as configurações foram apagadas.")

# @measure_time
def load_fonts():
    font_paths = [
        resource_path(os.path.join('resources', 'fonts', 'SF-Pro-Text-Regular.otf')),
        resource_path(os.path.join('resources', 'fonts', 'SF-Pro-Text-Semibold.otf')),
        resource_path(os.path.join('resources', 'fonts', 'SF-Pro-Text-Bold.otf')),
        resource_path(os.path.join('resources', 'fonts', 'SF-Pro-Text-Black.otf')),
        resource_path(os.path.join('resources', 'fonts', 'SF-Pro-Text-BlackItalic.otf')),
        resource_path(os.path.join('resources', 'fonts', 'Sebino-Regular.ttf'))
    ]
    for font_path in font_paths:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Falha ao carregar fonte: {font_path}")
        else:
            loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Fonte personalizada carregada: {loaded_fonts}")


#Seta fonte global para o aplicativo
def set_global_font(app):
    app.setStyleSheet("""
        * {
            font-family: 'SF Pro Text';
            font-weight: 500;
        }
        QPushButton {
            font-family: 'SF Pro Text';
            font-size: 12pt;
            font-weight: 600;
        }
                      
    """)

def get_messages_to_send(self):
    """
    Retorna a lista de mensagens a serem enviadas para a API, incluindo as últimas N conversas (pares de usuário e assistente)
    e a última mensagem do usuário que ainda não foi respondida.

    Se 'maintain_context' for True, inclui as últimas N conversas (2 * N mensagens) + 1 mensagem do usuário (se ainda não tiver sido respondida),
    totalizando 2 * N + 1 mensagens.

    Se 'maintain_context' for False, retorna apenas a última mensagem do usuário.
    """
    # Carregar as configurações
    maintain_context = load_context_setting()
    max_context_pairs = load_max_context()  # Número de pares usuário-assistente

    with self.conversation_lock:
        if not maintain_context:
            # Não manter contexto, enviar apenas a última mensagem do usuário
            if self.conversation_history:
                messages = [self.conversation_history[-1]]
            else:
                messages = []
            return messages

        # Manter contexto
        messages = []
        conversation = self.conversation_history.copy()
        total_messages = len(conversation)

        index = total_messages - 1
        pairs_collected = 0

        # Incluir a última mensagem do usuário que ainda não foi respondida
        if index >= 0 and conversation[index]['role'] == 'user':
            # Última mensagem do usuário não foi respondida ainda
            messages.append(conversation[index])
            index -= 1

        # Coletar os últimos N pares de usuário e assistente
        while index >= 0 and pairs_collected < max_context_pairs:
            # Coletar a mensagem do assistente
            if conversation[index]['role'] == 'assistant':
                assistant_message = conversation[index]
                index -= 1
            else:
                # Se não for uma mensagem do assistente, ignorar e continuar
                index -= 1
                continue

            # Coletar a mensagem do usuário
            if index >= 0 and conversation[index]['role'] == 'user':
                user_message = conversation[index]
                index -= 1
            else:
                # Se não houver mensagem do usuário correspondente, interromper
                break

            # Adicionar as mensagens à lista na ordem correta
            messages.extend([assistant_message, user_message])

            pairs_collected += 1

        # Reverter a lista para restaurar a ordem cronológica
        messages.reverse()

        return messages