# app/widgets/taskbar.py

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QToolButton, QMenu, QAction, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame  
)
from .draggable_widget import DraggableWidget
from app.utils.settings import load_theme
from app.utils.helpers import set_button_icon_with_hover

# Classe para a barra de tarefas arrastável
class Taskbar(DraggableWidget):
    # Definir o sinal toggle_side_menu
    toggle_side_menu = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Referência para MainWindow
        self.init_ui()
        self.setObjectName("Taskbar")

    def init_ui(self):
        # Usar QVBoxLayout para empilhar botões e separador verticalmente
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens para borda completa
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        self.setFixedHeight(50)  # Definir altura fixa para consistência

        # Horizontal layout para os botões
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 5, 10, 5)  # Margens internas
        button_layout.setSpacing(20)  # Espaçamento entre botões
        main_layout.addLayout(button_layout)

        # Botão de Toggle da Side Menu
        self.toggle_button = QPushButton()  # Ícone de menu
        set_button_icon_with_hover(self.toggle_button, 'mdi.menu', '#b4b4b4', 'green', (30,30))
        self.toggle_button.setObjectName("toggle_button")
        self.toggle_button.setFixedWidth(40)

        # Conectar o botão ao sinal toggle_side_menu
        self.toggle_button.clicked.connect(self.toggle_side_menu.emit)
        button_layout.addWidget(self.toggle_button)

        # Botão "Limpar Chat" (mais discreto)
        self.clear_chat_button = QPushButton()  # Ícone de lixeira
        set_button_icon_with_hover(self.clear_chat_button, 'fa.trash', '#171717' ,'#b4b4b4') 
        self.clear_chat_button.setObjectName("clearChatButton")
        self.clear_chat_button.setFixedSize(30, 30)
        self.clear_chat_button.clicked.connect(self.parent().clear_chat)
        button_layout.addWidget(self.clear_chat_button)

        # Spacer para empurrar os próximos botões para a direita
        button_layout.addStretch()

        # Botão de Minimizar
        self.minimize_button = QPushButton()
        set_button_icon_with_hover(self.minimize_button, 'mdi.window-minimize', '#171717', '#b4b4b4')
        self.minimize_button.setObjectName("minimizeButton")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.clicked.connect(self.parent().showMinimized)
        button_layout.addWidget(self.minimize_button)

        # Botão de Engrenagem com Menu Dropdown
        self.settings_menu_button = QToolButton()
        self.settings_menu_button.setObjectName("settingsMenuButton")
        set_button_icon_with_hover(self.settings_menu_button, 'ri.settings-5-fill', '#171717' ,'#171717') 


        # Criar o menu
        self.settings_menu = QMenu(self)

        # Adicionar ações ao menu
        config_action = QAction("⚙️ Configurações", self)  # Usando emoji
        config_action.triggered.connect(self.parent().open_settings)
        self.settings_menu.addAction(config_action)

        close_action = QAction("✖️ Fechar Aplicativo", self)  # Usando emoji
        close_action.triggered.connect(self.parent().close_application)
        self.settings_menu.addAction(close_action)

        # Adicionar ação para minimizar para a bandeja do sistema
        minimize_to_tray_action = QAction("🗕 Minimizar para a bandeja", self)
        minimize_to_tray_action.triggered.connect(self.parent().minimize_to_tray)
        self.settings_menu.addAction(minimize_to_tray_action)

        # Associar o menu ao botão
        self.settings_menu_button.setMenu(self.settings_menu)
        self.settings_menu_button.setPopupMode(QToolButton.InstantPopup)

        button_layout.addWidget(self.settings_menu_button)

        # Adicionar um QFrame como separador inferior de 1px
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setFixedHeight(1)  # Altura de 1px para a borda
        main_layout.addWidget(self.separator)

        # Aplicar o estilo do tema atual
        current_theme = load_theme()
        self.apply_theme(current_theme)

    def apply_theme(self, theme):
        """
        Aplica o estilo à Taskbar e ao seu menu com base no tema selecionado.
        """
        if theme == "dark":

            # Estilo da Taskbar
            self.setStyleSheet("""
                background-color: #34495E;
                border-radius: 0px;
            """)
            
            # Estilo do toggle_button
            set_button_icon_with_hover(self.toggle_button, 'mdi.menu', '#b4b4b4', 'green', (30,30))
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
            """)
            #Botão de Limpar Chat
            set_button_icon_with_hover(self.clear_chat_button, 'fa.trash', '#b4b4b4', '#171717')                                    
            self.clear_chat_button.setStyleSheet("""
                QPushButton#clearChatButton {
                    background-color: transparent;
                    color: white;
                    font-size: 18px;
                    border: none;
                }
                QPushButton#clearChatButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 15px;
                }
            """)
            #Botão de Configurações
            set_button_icon_with_hover(self.settings_menu_button, 'ri.settings-5-fill', '#b4b4b4', '#171717')
            self.settings_menu_button.setStyleSheet("""
                QToolButton#settingsMenuButton {
                    background-color: transparent;                              
                    border: none;
                }
                QToolButton#settingsMenuButton::menu-indicator {
                    image: none;  /* Remove o indicador de menu */
                }
                QToolButton#settingsMenuButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 12px;
                }
            """)                             
            # Estilo do separador
            if self.separator:
                self.separator.setStyleSheet("background-color: #666666;")  # Cinza para tema escuro
            # Estilo do Menu
            self.settings_menu.setStyleSheet("""
                QMenu {
                    background-color: #2E2E2E;
                    color: white;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
            """)
            # Botão de Minimizar
            set_button_icon_with_hover(self.minimize_button, 'mdi.window-minimize', '#b4b4b4', '#171717')
            self.minimize_button.setStyleSheet("""
                QPushButton#minimizeButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton#minimizeButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 15px;
                }
            """)
        else:
            #Botão de Limpar Chat
            set_button_icon_with_hover(self.clear_chat_button, 'fa.trash', '#171717', '#171717')
            # Estilo da Taskbar
            self.setStyleSheet("""
                background-color: #FFFFFF;  /* Cor de fundo clara */
                border-radius: 0px;         /* Bordas retas */
            """)
            # Estilo do toggle_button
            set_button_icon_with_hover(self.toggle_button, 'mdi.menu', '#171717', 'green', (30,30))
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
            """)
            # Estilo do botão de limpar chat
            self.clear_chat_button.setStyleSheet("""
                QPushButton#clearChatButton {
                    background-color: transparent;
                    color: white;
                    font-size: 18px;
                    border: none;
                }
                QPushButton#clearChatButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 15px;
                }
            """)
            #Botão de Configurações
            set_button_icon_with_hover(self.settings_menu_button, 'ri.settings-5-fill', '#171717', '#171717ß')
            self.settings_menu_button.setStyleSheet("""
                QToolButton#settingsMenuButton {
                    background-color: transparent;                              
                    border: none;
                }
                QToolButton#settingsMenuButton::menu-indicator {
                    image: none;  /* Remove o indicador de menu */
                }
                QToolButton#settingsMenuButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 12px;
                }
            """)   
            # Estilo do separador
            if self.separator:
                self.separator.setStyleSheet("background-color: #000000;")  # Preto para tema claro
            # Estilo do Menu
            self.settings_menu.setStyleSheet("""
                QMenu {
                    background-color: #FFFFFF;
                    color: black;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #ECECEC;
                }
            """)
            # Botão de Minimizar
            set_button_icon_with_hover(self.minimize_button, 'mdi.window-minimize', '#171717', '#171717')
            self.minimize_button.setStyleSheet("""
                QPushButton#minimizeButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton#minimizeButton:hover {
                    background-color: #b4b4b4;
                    border-radius: 15px;
                }
            """)
