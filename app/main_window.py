# app/main_window.py

import io
import base64
import threading

from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, pyqtSlot, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize
from PyQt5.QtWidgets import (
    QMenu, QAction, QLabel, QPushButton, QLineEdit, QSizePolicy, QShortcut,
    QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QFrame, QApplication,QSystemTrayIcon 
)

from PyQt5.QtGui import QIcon, QPixmap, QKeySequence, QGuiApplication
from PIL import ImageGrab

from app.widgets.taskbar import Taskbar
from app.widgets.floating_widget import FloatingWidget
from app.widgets.side_menu import SideMenuWindow
from app.widgets.chat_bubble import ChatBubble
from app.widgets.screenshot_widget import ScreenshotWidget
from app.dialogs.settings_window import SettingsWindow
from app.utils.settings import load_theme, save_theme, resource_path, load_api_key
from app.utils.api_calls import process_question, sidemenu_action
from app.utils.helpers import set_button_icon_with_hover, show_custom_message

#Resolver problema de icone
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('company.app.echo')

# Classe principal da janela
class MainWindow(QFrame):
    response_received = pyqtSignal(str)
    is_to_copy = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Echo')
        self.setObjectName("main_window")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint) #retira a barra de título

        # Obter a geometria da tela
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_height = screen_geometry.height()

        #Altura maxima
        maximum_height = 800
        # Define o tamanho mínimo da janela
        self.setMinimumSize(450, maximum_height)

        # Define a altura máxima como 80% da altura da tela
        max_height = int(screen_height * 0.8)
        if max_height < maximum_height:
            self.setFixedSize(450, max_height)  # Redefinir o tamanho da janela para caber na altura máxima

        # Definir o tamanho inicial da janela
        self.resize(450, min(maximum_height, max_height))

        #Setar icone
        self.setWindowIcon(QIcon(resource_path('resources/icons/app_icon.ico')))

        #Tray Icon -----------------------------------
        # Certifique-se de criar o tray_icon antes de setar o ícone
        self.tray_icon = QSystemTrayIcon(self)

        # Criar o ícone da bandeja do sistema
        tray_icon_path = resource_path('resources/icons/app_icon.ico')
        tray_icon = QIcon(tray_icon_path)
        # Setar o ícone da bandeja
        self.tray_icon.setIcon(tray_icon)


        # Criar o menu da bandeja
        self.tray_menu = QMenu()
        restore_action = QAction("Restaurar", self)
        restore_action.triggered.connect(self.restore_from_tray)
        exit_action = QAction("Fechar Aplicativo", self)
        exit_action.triggered.connect(self.close_application)
        self.tray_menu.addAction(restore_action)
        self.tray_menu.addAction(exit_action)
        self.tray_icon.setContextMenu(self.tray_menu)

        # Conectar o sinal de ativação do ícone da bandeja
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        #Fim Tray Icon -----------------------------------


        # Inicia o histórico de conversas
        self.conversation_history = []
        self.conversation_lock = threading.Lock()

        self.settings_window = None
        # Layout principal horizontal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Container do menu lateral
        self.side_menu_container = QWidget()
        self.side_menu_layout = QVBoxLayout(self.side_menu_container)
        self.side_menu_layout.setContentsMargins(0, 0, 0, 0)
        self.side_menu_layout.setSpacing(0)

        # Menu lateral
        self.side_menu_window = SideMenuWindow(main_window=self)
        self.side_menu_width = 100  # Ajuste a largura conforme necessário
        self.side_menu_window.setFixedWidth(self.side_menu_width)
        self.side_menu_layout.addWidget(self.side_menu_window)

        # Inicialmente, o menu lateral está oculto definindo sua largura máxima como 0
        self.side_menu_container.setMaximumWidth(0)
        self.side_menu_container.setMinimumWidth(0)
        self.side_menu_container.setVisible(False)

        # Container de conteúdo principal
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Barra de tarefas superior arrastável
        self.taskbar = Taskbar(self)
        self.taskbar.toggle_side_menu.connect(self.toggle_side_menu)
        self.content_layout.addWidget(self.taskbar)

        # Cria e exibe o widget flutuante
        self.floating_widget = FloatingWidget(main_window=self)

        # Área de exibição de chat
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #bfbfbf;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a6a6a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.addStretch()
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)
        self.content_layout.addWidget(self.chat_scroll)

        # Linha horizontal
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.content_layout.addWidget(line)

        # Área para inserir a pergunta e botões
        self.input_layout = QHBoxLayout()
        self.input_layout.setContentsMargins(10, 10, 10, 10)
        self.input_layout.setSpacing(10)

        # Botão de captura de imagem
        self.capture_button = QPushButton()

        # Gerar ícone FontAwesome (Exemplo: ícone de câmera)
        set_button_icon_with_hover(self.capture_button, 'fa.camera', '#b4b4b4', '#171717')
        self.capture_button.setIconSize(QSize(24, 24))
        self.capture_button.setFixedSize(36, 36)
        self.capture_button.setObjectName("capture_button")
        self.capture_button.clicked.connect(self.start_screenshot)
        self.input_layout.addWidget(self.capture_button)

        # Caixa de texto para a pergunta
        self.text_edit = QLineEdit(self)
        self.text_edit.setPlaceholderText('Digite sua mensagem...')
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setFixedHeight(36)
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.input_layout.addWidget(self.text_edit)

        # Botão de enviar mdi.send
        self.send_button = QPushButton()
        set_button_icon_with_hover(self.send_button, 'mdi.send', '#b4b4b4', '#171717')
        self.send_button.setIconSize(QSize(24, 24))
        self.send_button.setFixedSize(36, 36)
        self.send_button.setObjectName("send_button")

        self.send_button.clicked.connect(self.send_question)
        self.input_layout.addWidget(self.send_button)

        self.content_layout.addLayout(self.input_layout)

        # Adicionar os containers ao layout principal
        self.main_layout.addWidget(self.side_menu_container)
        self.main_layout.addWidget(self.content_container)



        # Conectar o sinal ao slot
        self.response_received.connect(self.update_response)

        # Conectar o sinal do SideMenuWindow para acoes
        self.side_menu_window.sidemenu_action_triggered.connect(lambda prompt: sidemenu_action(self, prompt))
        # Atalho para Ctrl+Enter acionar o botão "Enviar"
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self.text_edit)
        shortcut.activated.connect(self.send_question)
        #Procura o tema atual e aplica
        self.current_theme = load_theme()
        self.apply_theme(self.current_theme)

        # Mostrar a janela
        self.show()

        # Verificar se a chave da API está configurada
        self.check_api_key_on_startup()


    def apply_theme(self, theme):
        if theme == "dark":
            #Botao de camera
            set_button_icon_with_hover(self.capture_button, 'fa.camera', '#b4b4b4', '#171717')
            #Botao de enviar
            set_button_icon_with_hover(self.send_button, 'mdi.send','#b4b4b4', '#171717')
            self.setStyleSheet("""                        
                QPushButton#send_button, QPushButton#capture_button{
                    border: none;
                    background-color: transparent;
                }
                QPushButton#send_button:hover, QPushButton#capture_button:hover {
                    background-color: #e0e0e0;
                    border-radius: 18px;
                }
                QWidget {
                    background-color: #212121;
                    color: #FFFFFF;
                    font-family: 'SF Pro Text';
                    font-weight: 600;
                }
                QWidget#main_window {
                    border: 1px solid #666666;
                }                 
                QWidget QLineEdit#text_edit, QTextEdit, QComboBox {
                    background-color: #3E3E3E;
                    color: white;
                    border: 1px solid #555555;
                    border-radius: 10px;
                }                     
                QLabel {
                    color: white;
                }
                QScrollBar::handle:vertical {
                    background: #555555;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #777777;
                }
                QLabel#image_label {
                    border: 2px solid #555555;              
                }
            """)

        else:
            #Botao de camera
            set_button_icon_with_hover(self.capture_button, 'fa.camera', '#171717', '#171717')
            #Botao de enviar
            set_button_icon_with_hover(self.send_button, 'mdi.send', '#171717', '#171717')
            self.setStyleSheet("""
                QPushButton#send_button, QPushButton#capture_button{
                    border: none;
                    background-color: transparent;
                }
                QPushButton#send_button:hover, QPushButton#capture_button:hover {
                    background-color: #b4b4b4;
                    border-radius: 18px;
                }
                QWidget{
                    background-color: #ECECEC;
                    color: #000000;
                    font-family: 'SF Pro Text';
                }
                QWidget#main_window {
                    border: 1px solid #cccccc;
                }              
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #FFFFFF;
                    color: black;
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                }
                QLabel {
                    color: black;
                }
                QScrollBar::handle:vertical {
                    background: #bfbfbf;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #a6a6a6;
                }
                QLabel#image_label {
                    border: 2px solid #555555;              
                }
            """)

    def open_settings(self):
        self.settings_window = SettingsWindow()
        # Conectar os sinais para atualizar a API key, o tema e o hotkey
        self.settings_window.api_key_updated.connect(self.update_api_key)
        self.settings_window.theme_updated.connect(self.change_theme)
        self.settings_window.hotkey_updated.connect(self.update_hotkey)

        self.settings_window.exec_()

    #Quando tiver mudança no sinal theme_updated, ativa a funcao de aplicar o tema escolhido
    def change_theme(self, theme):
        self.current_theme = theme
        save_theme(theme)  # Salvar o tema escolhido
        self.apply_theme(theme)  # Aplicar o tema imediatamente
        self.taskbar.apply_theme(theme)  # Atualizar o estilo da Taskbar
        self.side_menu_window.apply_theme(theme)  # Atualizar o estilo do SideMenuWindow
        self.floating_widget.apply_theme(theme)  # Atualizar o estilo do FloatingWidget
        # Atualizar todas as ChatBubble com o novo tema
        for i in range(self.chat_layout.count()):
            item = self.chat_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, ChatBubble):
                widget.apply_theme(theme)

    def update_api_key(self, new_api_key):
        # Atualizar a chave da API com a nova chave
        self.api_key = new_api_key
        print(f"Chave da API atualizada para: {self.api_key}")

    def update_hotkey(self, new_hotkey):
        # Emitir um sinal ou chamar uma função para atualizar o hotkey no HotkeyListener
        app = QApplication.instance()
        if hasattr(app, 'update_hotkey'):
            app.update_hotkey(new_hotkey)
        else:
            print("Erro: A instância do aplicativo não possui o método 'update_hotkey'.")

    def start_screenshot(self):
        self.screenshot_widget = ScreenshotWidget()
        self.screenshot_widget.selection_made.connect(self.update_image)
        self.screenshot_widget.show()

    @pyqtSlot(QRect)
    def update_image(self, rect):
        # Verificar se o retângulo tem uma área mínima maior que 1x1 pixel
        if rect.width() <= 1 or rect.height() <= 1:
            show_custom_message('Alerta', 'A seleção de captura de tela é muito pequena. Por favor, selecione uma área maior')
            return

        # Capturar a imagem da área selecionada
        img = ImageGrab.grab(bbox=(rect.left(), rect.top(), rect.right(), rect.bottom()))

        # Armazenar a imagem capturada
        self.captured_image = img

        # Converter a imagem para bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        image_data = buffer.getvalue()

        # Armazenar os dados da imagem codificados em base64
        self.image_data_base64 = base64.b64encode(image_data).decode('utf-8')

        # Exibir a imagem na área de chat
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setObjectName("image_label")
        image_label.setPixmap(pixmap)
        image_label.setFixedWidth(200)


        bubble_widget = QWidget()
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(10, 5, 10, 5)
        bubble_layout.addStretch()
        bubble_layout.addWidget(image_label)
        bubble_widget.setLayout(bubble_layout)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_widget)

        # Autoscroll para a última mensagem
        self.autoscroll_chat()

        # Trazer a janela principal para o primeiro plano
        self.raise_()
        self.activateWindow()

    def send_question(self):
        question = self.text_edit.text().strip()
        if not question and not hasattr(self, 'image_data_base64'):
            show_custom_message('Alerta', 'Por favor, digite uma mensagem ou capture uma imagem')
            return

        # Armazenar a pergunta atual
        self.current_question = question

        # Exibir a mensagem do usuário na área de chat
        if question:
            user_bubble = ChatBubble(question, sender='user')
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble)
            # Autoscroll para a última mensagem
            self.autoscroll_chat()

        # Limpar a caixa de texto
        self.text_edit.clear()

        # Desabilitar o botão enquanto processa
        self.send_button.setEnabled(False)

        # Iniciar thread para não bloquear a interface
        threading.Thread(target=process_question, args=(self, question)).start()


    @pyqtSlot(str)
    def update_response(self, answer):
        # Habilitar o botão "Enviar" novamente
        self.send_button.setEnabled(True)

        if answer.startswith("Erro:"):
            show_custom_message('Alerta', answer)
            #Reativar botoes do sidemenu
            self.side_menu_window.reactivate_buttons()
            return

        # Exibir a resposta na área de chat
        assistant_bubble = ChatBubble(answer, sender='assistant')
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, assistant_bubble)
        # Copiar para o clipboard se setado para tal
        if self.is_to_copy:
            clipboard = QApplication.clipboard()
            clipboard.setText(answer)
            self.is_to_copy = False  # Resetar a flag

        #Reativar botoes do sidemenu
        self.side_menu_window.reactivate_buttons()
        # Autoscroll para a última mensagem
        self.autoscroll_chat()



    #limpa o chat das bubbles e também a lista de conversas
    def clear_chat(self):
        """
        Limpa a área de chat e o histórico de conversas.
        """
        with self.conversation_lock:
            # Limpar o histórico de conversas
            self.conversation_history.clear()
        
        # Remover todas as mensagens da área de chat (exceto o widget de espaçamento)
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Opcional: Adicionar uma mensagem informando que o chat foi limpo
        info_bubble = ChatBubble("O chat foi limpo", sender='system')
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, info_bubble)
        self.autoscroll_chat()

    def autoscroll_chat(self):
        """
        Força o chat a rolar para o final quando uma nova mensagem é adicionada.
        Usando QTimer para garantir que o layout foi atualizado antes de rolar.
        """
        QTimer.singleShot(100, self._scroll_to_bottom)
    def _scroll_to_bottom(self):
        """
        Função auxiliar para rolar o chat até o final.
        """
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


    def toggle_side_menu(self):
        self.taskbar.toggle_button.setEnabled(False)
        if self.side_menu_container.maximumWidth() == 0:
            # Abrir o menu
            self.side_menu_container.setVisible(True)
            self.animate_side_menu(self.side_menu_width)
        else:
            # Fechar o menu
            self.animate_side_menu(0)

    def animate_side_menu(self, target_width):
        animation_duration = 200

        # Animação da largura do menu lateral
        side_menu_animation = QPropertyAnimation(self.side_menu_container, b"maximumWidth")
        side_menu_animation.setDuration(animation_duration)
        side_menu_animation.setStartValue(self.side_menu_container.maximumWidth())
        side_menu_animation.setEndValue(target_width)
        side_menu_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Animação da geometria do conteúdo
        content_animation = QPropertyAnimation(self.content_container, b"geometry")
        content_animation.setDuration(animation_duration)
        current_geometry = self.content_container.geometry()
        if target_width > 0:
            # Menu está abrindo
            end_geometry = QRect(self.side_menu_width, 0, self.width() - self.side_menu_width, self.height())
        else:
            # Menu está fechando
            end_geometry = QRect(0, 0, self.width(), self.height())
        content_animation.setStartValue(current_geometry)
        content_animation.setEndValue(end_geometry)
        content_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Agrupar animações
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(side_menu_animation)
        self.animation_group.addAnimation(content_animation)
        self.animation_group.finished.connect(self.on_animation_finished)
        self.animation_group.start()

    def on_animation_finished(self):
        # Alternar visibilidade se necessário
        if self.side_menu_container.maximumWidth() == 0:
            self.side_menu_container.setVisible(False)
        self.taskbar.toggle_button.setEnabled(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ajustar a geometria do conteúdo se o menu lateral estiver aberto
        if self.side_menu_container.maximumWidth() > 0:
            self.content_container.setGeometry(self.side_menu_container.width(), 0, self.width() - self.side_menu_container.width(), self.height())
        else:
            self.content_container.setGeometry(0, 0, self.width(), self.height())

    def close_application(self):
        QApplication.instance().quit()

    def minimize_to_tray(self):
        self.hide()
        self.tray_icon.show()

    def restore_from_tray(self):
        self.show()
        self.tray_icon.hide()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.restore_from_tray()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.text_edit.hasFocus():
            self.send_question()

    def check_api_key_on_startup(self):
        api_key = load_api_key()
        if not api_key:
            # Se a chave da API não estiver configurada, abrir a janela de configurações
            show_custom_message('Alerta', 'Por favor, insira a chave da API para continuar')
            self.open_settings()
        else:
            self.api_key = api_key  # Armazenar a chave da API para uso posterior

