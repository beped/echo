# app/widgets/chat_bubble.py

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout  
)
from app.utils.helpers import set_button_icon_with_hover
from app.utils.settings import load_theme

# Classe para as bolhas de chat
class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text, sender='user'):
        super().__init__()
        self.text = text
        self.sender = sender
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Criação da bolha de texto usando QLabel
        self.bubble = QLabel()
        self.bubble.setWordWrap(True)
        self.bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Permitir seleção de texto

        # Usar setText com HTML para que as quebras de linha (\n) sejam respeitadas
        self.bubble.setText(self.text.replace('\n', '<br>'))  # Substituir \n por <br> para que as quebras sejam visíveis

        # Configurar cores e alinhamento com base no sender
        if self.sender == 'user':
            self.setup_user_bubble()
        elif self.sender == 'assistant':
            self.setup_assistant_bubble()
        elif self.sender == 'system':
            self.setup_system_bubble()
        
        # Ajustar tamanho do QLabel ao conteúdo
        self.bubble.adjustSize()

        # Inicializar QTimer para resetar o botão de copiar (não necessário para system)
        if self.sender != 'system':
            self.reset_timer = QTimer(self)
            self.reset_timer.setSingleShot(True)
            self.reset_timer.timeout.connect(self.reset_copy_button)
        
        # Carregar o tema atual
        self.current_theme = load_theme()
        self.apply_theme(self.current_theme)

    def setup_user_bubble(self):
        # Botão de copiar para o usuário
        self.copy_button = QPushButton()
        set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#171717', '#b4b4b4', (20, 20))
        self.copy_button.setFixedSize(25, 25)
        self.copy_button.setObjectName("copy_button")
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setToolTip("Copiar texto")

        # Estilo da bolha do usuário
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: #004690;  /* Azul para o usuário */
                color: #fefeff;
                border-radius: 10px;
                padding: 10px;
                font-family: 'SF Pro Text';
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        # Adicionar elementos ao layout
        # Adicionar espaço extra à esquerda
        self.layout.addStretch()
        self.layout.addWidget(self.bubble)
        self.layout.addWidget(self.copy_button)  # Copiar também do lado direito

    def setup_assistant_bubble(self):
        # Botão de copiar para o assistente
        self.copy_button = QPushButton()
        set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#171717', '#b4b4b4', (20, 20))
        self.copy_button.setFixedSize(25, 25)
        self.copy_button.setObjectName("copy_button")
        self.copy_button.clicked.connect(self.copy_text)
        self.copy_button.setToolTip("Copiar texto")

        # Estilo da bolha do assistente
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: #2E2E2E;  /* Cinza para assistente */
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-family: 'SF Pro Text';
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        # Adicionar elementos ao layout
        self.layout.addWidget(self.bubble)
        self.layout.addWidget(self.copy_button)
        # Adicionar espaço extra à direita
        self.layout.addStretch()

    def setup_system_bubble(self):
        # Não há botão de copiar para system
        # Estilo da bolha do sistema
        self.bubble.setStyleSheet("""
            QLabel {
                background-color: #FFA500;  /* Laranja para system */
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-family: 'SF Pro Text';
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        # Adicionar elementos ao layout centralizados
        self.layout.addStretch()
        self.layout.addWidget(self.bubble, alignment=Qt.AlignCenter)
        self.layout.addStretch()

    def copy_text(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.text)
        # Feedback visual: mudar o ícone do botão para "✔️" por 1 segundo
        set_button_icon_with_hover(self.copy_button, 'fa.check', 'green', 'green', (20, 20))
        # Iniciar o timer para resetar o botão após 1 segundo
        self.reset_timer.start(1000)  # Iniciar o timer para 1 segundo

    def reset_copy_button(self):
        current_theme = load_theme()
        if current_theme == "dark":
            set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#b4b4b4', '#171717', (20, 20))
        else:
            set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#171717', '#171717', (20, 20))

    def apply_theme(self, theme):
        #### Inicio tema escuro
        if theme == "dark":
            # Configurar cores diferentes para o usuário e assistente
            # Usuario - Tema escuro
            if self.sender == 'user':
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: #004690; /* #004690 */
                        color: #fefeff;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)
            elif self.sender == 'assistant':
                # Assistente - Tema escuro
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: #2E2E2E;
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)
            elif self.sender == 'system':
                # Sistema - Tema escuro
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: green;  /* Laranja para system */
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)

            # Botão de copiar    
            if self.sender != 'system':
                self.copy_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #b4b4b4;
                        border-radius: 12px;
                    }
                """)
                if self.sender != 'system':
                    set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#b4b4b4', '#171717', (20, 20))
        #### Final tema escuro
        else:
        #### Inicio tema claro
            # Configurar cores diferentes para o usuário e assistente
            # Usuario - Tema claro
            if self.sender == 'user':
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: #004690;
                        color: #fefeff;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)
            elif self.sender == 'assistant':
                # Assistente - Tema claro
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: #2E2E2E;
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)
            elif self.sender == 'system':
                # Sistema - Tema claro
                self.bubble.setStyleSheet("""
                    QLabel {
                        background-color: green;  /* Laranja para system */
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font-family: 'SF Pro Text';
                        font-weight: 600;
                        font-size: 14px;
                    }
                """)

            # Botão de copiar    
            if self.sender != 'system':
                self.copy_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #b4b4b4;
                        border-radius: 12px;
                    }
                """)
                if self.sender != 'system':
                    set_button_icon_with_hover(self.copy_button, 'fa5s.copy', '#171717', '#171717', (20, 20))
        #### Final tema claro
