# app/dialogs/settings_window.py

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QFrame, QDialog, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QGuiApplication

from app.utils.settings import (
    load_name, save_name, load_api_key, save_api_key, load_theme, load_hotkey, save_hotkey,
    load_context_setting, save_context_setting, load_max_context, save_max_context,
    resource_path
)
from app.utils.helpers import show_custom_message
from app import __version__

# Classe para a janela de configurações
class SettingsWindow(QDialog):
    # Sinais emitidos quando a chave da API, o tema ou o hotkey for atualizado
    api_key_updated = pyqtSignal(str)
    theme_updated = pyqtSignal(str)
    hotkey_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Configurações')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  # Retira a barra de título
        self.init_ui()
        self.setModal(True)  # Impede interação com outras janelas enquanto a configuração está aberta
        self.apply_theme(load_theme())  # Aplicar o tema atual

    def init_ui(self):
        # Define um layout principal vertical com espaçamento
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Título da janela de configurações
        self.title = QLabel("Configurações do Aplicativo")
        self.title.setObjectName("settingsTitle")
        self.title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Grupo de configurações
        settings_group = QGroupBox()
        settings_layout = QFormLayout()
        settings_layout.setSpacing(15)

        # Checkbox para "Manter contexto"
        self.context_checkbox = QtWidgets.QCheckBox("Manter contexto")
        self.context_checkbox.setObjectName("context_checkbox")
        # Carrega a configuração atual do manter contexto
        current_context_setting = load_context_setting()
        self.context_checkbox.setChecked(current_context_setting)
        # Conectar o sinal stateChanged ao método toggle_max_context_combo
        self.context_checkbox.stateChanged.connect(self.toggle_max_context_combo)

        # Combobox do máximo de mensagens
        self.max_context_combo = QComboBox()
        self.max_context_combo.setObjectName("max_context_combo")

        # Adicionando as opções com texto e valores associados
        self.max_context_combo.addItem("2 mensagens", 2)
        self.max_context_combo.addItem("5 mensagens", 5)
        self.max_context_combo.addItem("10 mensagens", 10)
        self.max_context_combo.addItem("20 mensagens", 20)
        self.max_context_combo.addItem("30 mensagens", 30)
        # Carregar o valor atual da configuração
        current_max_context = load_max_context()
        # Encontrar o índice do valor atual e definir no combobox
        index = self.max_context_combo.findData(current_max_context)
        if index != -1:
            self.max_context_combo.setCurrentIndex(index)
        else:
            # Se o valor atual não estiver na lista, selecionar o primeiro
            self.max_context_combo.setCurrentIndex(0)
        # Definir o estado inicial do combobox
        self.max_context_combo.setEnabled(current_context_setting)

        settings_layout.addRow(self.context_checkbox, self.max_context_combo)

        # Campo para inserir o nome do usuário
        name_label = QLabel("Seu nome:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Fulano de Tal")
        self.name_input.setObjectName("name_input")
        # Carregar o nome existente
        current_name = load_name()
        self.name_input.setText(current_name)
        settings_layout.addRow(name_label, self.name_input)

        # Campo para inserir a chave da API
        api_label = QLabel("Chave da API:")
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Chave API da OpenAI")
        self.api_input.setObjectName("api_input")
        self.api_input.setEchoMode(QLineEdit.Password)  # Ocultar o texto como senha
        # Carregar a chave da API existente
        current_api_key = load_api_key()
        self.api_input.setText(current_api_key)
        settings_layout.addRow(api_label, self.api_input)

        # Adicionar campo para escolher o tema
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["Claro", "Escuro"])

        # Carregar o tema atual das configurações
        current_theme = load_theme()
        if current_theme == "dark":
            self.theme_combo.setCurrentText("Escuro")
        else:
            self.theme_combo.setCurrentText("Claro")

        settings_layout.addRow(theme_label, self.theme_combo)

        # Adicionar campo para definir a tecla de atalho para captura de tela
        hotkey_label = QLabel("Tecla de Atalho para Captura de Tela:")
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.setObjectName("hotkey_combo")

        # Lista de combinações de teclas predefinidas
        predefined_hotkeys = [
            "Ctrl+Shift+S",
            "Ctrl+Alt+S",
            "Ctrl+Shift+C",
            "Ctrl+Alt+C",
            "Ctrl+Alt+Shift+S"
        ]
        self.hotkey_combo.addItems(predefined_hotkeys)

        # Carregar a tecla de atalho atual e selecionar no combo
        current_hotkey = load_hotkey()
        if current_hotkey in predefined_hotkeys:
            self.hotkey_combo.setCurrentText(current_hotkey)
        else:
            self.hotkey_combo.setCurrentIndex(0)  # Seleciona a primeira opção se a atual não estiver na lista

        settings_layout.addRow(hotkey_label, self.hotkey_combo)

        # Adicionar campo de versão do aplicativo - versao
        version_label = QLabel("Versão:")
        version_text = QLabel(__version__)
        settings_layout.addRow(version_label, version_text)


        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        

        # Botões de ação (Salvar e Cancelar)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # Botão Salvar
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)

        # Botão Cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        # Define tamanho mínimo e ajusta o tamanho com base no conteúdo
        self.setMinimumWidth(400)
        self.center_window()



    def apply_theme(self, theme):
        # Caminho relativo para o ícone da seta para baixo
        icon_path = resource_path("resources/icons/down_arrow.svg").replace('\\', '/')
        combo_style = f"""
            QComboBox {{
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
                padding-right: 30px; /* Espaço para a seta */
                color: black;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url("{icon_path}");  /* Usando a variável icon_path */
                width: 10px;
                height: 10px;
            }}
            QComboBox:focus {{
                border: 1px solid #0084FF;
                background-color: #ffffff;
            }}
        """
        if theme == "dark":
            # Título
            self.title.setStyleSheet(
                "font-size: 16px;"
                "color: white;"
                "font-weight: bold;"
            )
            # Nome
            self.name_input.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                    color: black;
                }
                QLineEdit:focus {
                    border: 1px solid #0084FF;
                    background-color: #ffffff;
                }
            """)
            # API
            self.api_input.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                    color: black;
                }
                QLineEdit:focus {
                    border: 1px solid #0084FF;
                    background-color: #ffffff;
                }
            """)
            # Aplicar o estilo aos ComboBoxes
            self.theme_combo.setStyleSheet(combo_style)
            self.max_context_combo.setStyleSheet(combo_style)
            self.hotkey_combo.setStyleSheet(combo_style)
            # Estilo para o checkbox
            self.context_checkbox.setStyleSheet("""
                QCheckBox {
                    color: white;
                    margin-top: 10px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
                                
            # Botão Salvar
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #0084FF;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005BB5;
                }
                QPushButton:pressed {
                    background-color: #003F7F;
                }
            """)
            # Botão Cancelar
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #555555;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
                QPushButton:pressed {
                    background-color: #a0a0a0;
                }
            """)
            self.setStyleSheet("""
                QDialog {
                    background-color: #2E2E2E;
                    color: white;
                    font-family: Arial, sans-serif;
                    border: 2px solid #3e3e3e;
                }
                QLabel {
                    color: white;
                }
                QLineEdit, QComboBox, QGroupBox {
                    background-color: #3E3E3E;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 10px;
                }
                QGroupBox {
                    border: 1px solid #555555;
                }
            """)
        else:
            # Título
            self.title.setStyleSheet(
                "font-size: 16px;"
                "color: black;"
                "font-weight: bold;"
            )
            # Nome
            self.name_input.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                    color: black;
                }
                QLineEdit:focus {
                    border: 1px solid #0084FF;
                    background-color: #ffffff;
                }
            """)
            # API
            self.api_input.setStyleSheet("""
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                    color: black;
                }
                QLineEdit:focus {
                    border: 1px solid #0084FF;
                    background-color: #ffffff;
                }
            """)
            # Aplicar o estilo aos ComboBoxes
            self.theme_combo.setStyleSheet(combo_style)
            self.max_context_combo.setStyleSheet(combo_style)
            self.hotkey_combo.setStyleSheet(combo_style)
            # Estilo para o checkbox
            self.context_checkbox.setStyleSheet("""
                QCheckBox {
                    color: black;
                    margin-top: 10px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
   
            # Botão Salvar
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #0084FF;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #005BB5;
                }
                QPushButton:pressed {
                    background-color: #003F7F;
                }
            """)
            # Botão Cancelar
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #555555;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
                QPushButton:pressed {
                    background-color: #a0a0a0;
                }
            """)
            self.setStyleSheet("""
                QDialog {
                    background-color: #F0F0F0;
                    color: black;
                    font-family: Arial, sans-serif;
                    border: 2px solid #CCCCCC;
                }
                QLabel {
                    color: black;
                }
                QLineEdit, QComboBox, QGroupBox {
                    background-color: #ECECEC;
                    color: black;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                }
            """)

    def save_settings(self):
        name = self.name_input.text().strip()
        api_key = self.api_input.text().strip()
        theme_choice = self.theme_combo.currentText()
        selected_hotkey = self.hotkey_combo.currentText()

        # Validação básica
        if not api_key:
            show_custom_message('Alerta', 'A chave da API não pode estar vazia')
            return

        # Salvar nome
        save_name(name)

        # Salvar chave da API
        save_api_key(api_key)
        self.api_key_updated.emit(api_key)

        # Salvar tema escolhido
        if theme_choice == "Claro":
            self.theme_updated.emit("light")
        else:
            self.theme_updated.emit("dark")

        # Salvar tecla de atalho selecionada
        if selected_hotkey:
            save_hotkey(selected_hotkey)
            self.hotkey_updated.emit(selected_hotkey)
        else:
            # Se nenhuma tecla for definida, usar o padrão
            default_hotkey = "Ctrl+Shift+S"
            save_hotkey(default_hotkey)
            self.hotkey_updated.emit(default_hotkey)

        # Salvar a configuração do "Manter contexto"
        maintain_context = self.context_checkbox.isChecked()
        save_context_setting(maintain_context)
        # Salvar o número máximo de mensagens no contexto
        max_context_value = self.max_context_combo.currentData()
        save_max_context(max_context_value)

        self.accept()

    # Função para habilitar o combo de máximo de mensagens
    def toggle_max_context_combo(self, state):
        if state == Qt.Checked:
            self.max_context_combo.setEnabled(True)
        else:
            self.max_context_combo.setEnabled(False)
    # Função para centralizar a janela
    def center_window(self):
        # Defina o tamanho mínimo da janela, se necessário
        self.setMinimumWidth(400)
        
        # Ajuste o tamanho com base no conteúdo
        self.adjustSize()

        # Centraliza a janela na tela principal
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        dialog_geometry = self.frameGeometry()
        dialog_geometry.moveCenter(screen_geometry.center())
        self.move(dialog_geometry.topLeft())
