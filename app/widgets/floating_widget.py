# app/widgets/floating_widgets.py

import sys
import ctypes
import time
from ctypes import wintypes
from app.utils.settings import load_theme, load_name
from app.utils.helpers import set_button_icon_with_hover, CustomTextEdit, show_custom_message
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup, QEasingCurve, pyqtSlot, QTimer, QRect, QEventLoop, QObject, QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QToolButton, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QDialog, QApplication , QTextEdit,
    QGraphicsOpacityEffect
)
from app.utils.api_calls import floating_widget_action
from app.widgets.chat_bubble import ChatBubble
from app.utils.qt_waiting_spinner import QtWaitingSpinner



class FloatingWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # Armazena a referência para a MainWindow
        self.is_dragging = False  # Controle para saber se está arrastando a janela
        self.drag_position = None  # Posição inicial do clique para arrastar
        self.expanded = False  # Controle para saber se está expandido ou não
        self.current_action = None  # Ação atual selecionada - mostral modal ou não
        self.original_text = None  # Inicializa copied_text como None
        self.waiting_for_response = False  # Controle para saber se está esperando uma resposta da API
        self.original_hwnd = None  # Handle da janela original
        self.init_ui()

        # Aplica o tema ao widget flutuante
        self.apply_theme(load_theme())

        # Conectar o sinal de resposta uma vez no __init__
        if main_window:
            main_window.response_received.connect(self.handle_api_response)

    def init_ui(self):
        # Seta a janela para ficar sempre no topo e com fundo transparente
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool  # Previne que a janela apareça na barra de tarefas
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # Habilita a transparência do fundo

        # Função para aplicar efeitos de opacidade
        def apply_opacity(button, initial_opacity=1.0):
            opacity_effect = QGraphicsOpacityEffect()
            button.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(initial_opacity)
            return opacity_effect
        
        # Pega a geometria da tela
        screen_geometry = QApplication.desktop().availableGeometry()

        # Tamanho inicial da janela
        self.widget_width = 50
        self.widget_height = 50

        # Calcula a posição inicial da janela (lado direito da tela)
        x = screen_geometry.width() - self.widget_width - 10  # Ajuste de 10 pixels para afastar da borda
        y = (screen_geometry.height() - self.widget_height) // 2  # Centralizada verticalmente

        # Seta a geometria inicial da janela e posição
        self.setGeometry(x, y, self.widget_width, self.widget_height)

        # Cria um layout para o widget principal
        self.layout = QVBoxLayout()
        #self.layout.setSpacing(10)  # Espaçamento entre os botões
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Widget de fundo com transparência
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("background_widget")
        self.background_widget.setGeometry(0, 0, self.widget_width, self.widget_height)  # Define o tamanho do fundo


        # Spinner de carregamento
        self.spinner = QtWaitingSpinner(self.background_widget, centerOnParent=True, disableParentWhenSpinning=False)
        self.spinner.setNumberOfLines(12)
        self.spinner.setLineLength(10)
        self.spinner.setLineWidth(5)
        self.spinner.setInnerRadius(10)
        self.spinner.setColor(QColor('#007BFF'))  # Ajuste conforme o tema


        # Layout interno do background_widget
        self.inner_layout = QVBoxLayout()
        self.inner_layout.setSpacing(2) # Espaçamento entre os botões
        self.inner_layout.setContentsMargins(5, 5, 5, 5)
        self.background_widget.setLayout(self.inner_layout)

        # Botão Principal
        self.main_button = QPushButton(self)
        self.main_button.setFixedSize(40, 40)
        self.main_button.setObjectName("main_button")
        self.main_button.setFlat(True)  # Remove borda e sombra
        set_button_icon_with_hover(self.main_button, 'mdi.assistant', '#171717', '#171717', (30, 30))
        self.main_button.clicked.connect(self.toggle_expand)
        self.inner_layout.addWidget(self.main_button, alignment=Qt.AlignCenter)
        self.main_opacity = apply_opacity(self.main_button, initial_opacity=1.0)
        # Eventos de mouse para permitir movimentar a janela
        self.main_button.mousePressEvent = self.main_button_mouse_press_event
        self.main_button.mouseMoveEvent = self.main_button_mouse_move_event
        self.main_button.mouseReleaseEvent = self.main_button_mouse_release_event
        # Adicionar o temporizador para diferenciar clique rápido de arraste
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.toggle_expand)  # Conectar ao método de expandir/contrair

        # Botão Topo 1
        self.top_button1 = QToolButton(self)
        self.top_button1.setFixedSize(90, 50)
        self.top_button1.setObjectName("top_button1")
        set_button_icon_with_hover(self.top_button1, 'mdi.magnify-scan', '#171717', '#171717', (20, 20))
        self.top_button1.setText("Revisar")
        self.top_button1.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # Texto abaixo do ícone
        self.top_button1.clicked.connect(self.handle_review_format)
        self.top_button1.hide()  # Oculta inicialmente

        # Botão Topo 2
        self.top_button2 = QToolButton(self)
        self.top_button2.setFixedSize(90, 50)
        self.top_button2.setObjectName("top_button2")
        set_button_icon_with_hover(self.top_button2, 'ph.pencil-simple', '#171717', '#b4b4b4', (20, 20))
        self.top_button2.setText("Reescrever")
        self.top_button2.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # Texto abaixo do ícone
        self.top_button2.clicked.connect(self.handle_rewrite_format)
        self.top_button2.hide()  # Oculta inicialmente
        # Layout horizontal para os botões de topo
        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.top_button1, alignment=Qt.AlignLeft)
        self.top_layout.addWidget(self.top_button2, alignment=Qt.AlignRight)

        # Adicionar o layout de topo ao layout interno
        self.inner_layout.addLayout(self.top_layout)

        # Botão 1
        self.button1 = QPushButton(self)
        self.button1.setFixedSize(190, 25)  # Aumentar a largura para 80
        self.button1.setObjectName("button1")
        self.button1.setFlat(True)
        set_button_icon_with_hover(self.button1, 'fa.smile-o', '#171717', '#171717', (20, 20))
        self.button1.setText("Casual")
        self.button1.clicked.connect(self.handle_casual_format)
        self.button1.hide()  # Oculta inicialmente
        self.inner_layout.addWidget(self.button1, alignment=Qt.AlignCenter)

        # Botão 2
        self.button2 = QPushButton(self)
        self.button2.setFixedSize(190, 25)  # Aumentar a largura para 80
        self.button2.setObjectName("button2")
        self.button2.setFlat(True)
        set_button_icon_with_hover(self.button2, 'ri.briefcase-line', '#171717', '#171717', (20, 20))
        self.button2.setText("Profissional")
        self.button2.clicked.connect(self.handle_professional_format)
        self.button2.hide()  # Oculta inicialmente
        self.inner_layout.addWidget(self.button2, alignment=Qt.AlignCenter)

        # Botão conciso
        self.conciso = QPushButton(self)
        self.conciso.setFixedSize(190, 25)  # Aumentar a largura para 80
        self.conciso.setObjectName("conciso")
        self.conciso.setFlat(True)
        set_button_icon_with_hover(self.conciso, 'ph.arrows-in-line-vertical-fill', '#171717', '#171717', (20, 20))
        self.conciso.setText("Conciso")
        self.conciso.clicked.connect(self.handle_concise_format)
        self.conciso.hide()  # Oculta inicialmente
        self.inner_layout.addWidget(self.conciso, alignment=Qt.AlignCenter)

        # Linha de divisão
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.divider.setFixedHeight(1)  # Define a altura desejada
        self.divider.setStyleSheet("background-color: black; border: none;")
        self.divider.hide()  # Oculta inicialmente
        # Adicionar Linha de Divisão
        self.inner_layout.addWidget(self.divider)

        # Botão 3
        self.button3 = QPushButton(self)
        self.button3.setFixedSize(190, 25)  # Aumentar a largura para 80
        self.button3.setObjectName("button3")
        self.button3.setFlat(True)
        set_button_icon_with_hover(self.button3, 'fa5.file-alt', '#171717', '#171717', (20, 20))
        self.button3.setText("Resumir")
        self.button3.clicked.connect(self.handle_summarize_format)
        self.button3.hide()  # Oculta inicialmente
        self.inner_layout.addWidget(self.button3, alignment=Qt.AlignCenter)

        # Botão 4
        self.button4 = QPushButton(self)
        self.button4.setFixedSize(190, 25)  # Aumentar a largura para 80
        self.button4.setObjectName("button4")
        self.button4.setFlat(True)
        set_button_icon_with_hover(self.button4, 'mdi6.format-list-bulleted', '#171717', '#171717', (20, 20))
        self.button4.setText("Pontos-Chave")
        self.button4.clicked.connect(self.handle_keypoints_format)
        self.button4.hide()  # Oculta inicialmente
        self.inner_layout.addWidget(self.button4, alignment=Qt.AlignCenter)

        # Botão Final 1
        self.bottom_button1 = QPushButton(self)
        self.bottom_button1.setFixedSize(50, 25)
        self.bottom_button1.setObjectName("bottom_button1")
        set_button_icon_with_hover(self.bottom_button1, 'ph.arrow-square-left-light', '#171717', '#171717', (20, 20))
        self.bottom_button1.clicked.connect(self.bring_main_window)
        self.bottom_button1.hide()  # Oculta inicialmente
        # Botão Final 3
        self.bottom_button3 = QPushButton(self)
        self.bottom_button3.setFixedSize(50, 25)
        self.bottom_button3.setObjectName("bottom_button1")
        set_button_icon_with_hover(self.bottom_button3, 'mdi.refresh', '#171717', '#171717', (20, 20))
        self.bottom_button3.clicked.connect(self.return_copied_text)
        self.bottom_button3.hide()  # Oculta inicialmente
        # Botão Final 2
        self.bottom_button2 = QPushButton(self)
        self.bottom_button2.setFixedSize(50, 25)
        self.bottom_button2.setObjectName("bottom_button2")
        set_button_icon_with_hover(self.bottom_button2, 'mdi.window-minimize', '#171717', '#171717', (20, 20))
        self.bottom_button2.clicked.connect(self.toggle_expand)
        self.bottom_button2.hide()  # Oculta inicialmente

        # Layout horizontal para os botões de final
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.bottom_button1, alignment=Qt.AlignLeft)
        self.bottom_layout.addWidget(self.bottom_button3, alignment=Qt.AlignCenter)
        #Seta o botão 3 desabilitado por default
        self.bottom_button3.setEnabled(False)
        self.bottom_layout.addWidget(self.bottom_button2, alignment=Qt.AlignRight)


        # Adicionar o layout de final ao layout interno
        self.inner_layout.addLayout(self.bottom_layout)

        # Lista de botões que participarão das animações de fade
        self.fade_buttons = [
            self.top_button1, self.top_button2,
            self.button1, self.button2, self.conciso,
            self.divider,
            self.button3, self.button4,
            self.bottom_button1, self.bottom_button3, self.bottom_button2
        ]

        # Aplicar efeitos de opacidade aos botões
        self.button_opacities = {}
        for btn in self.fade_buttons:
            btn_opacity = apply_opacity(btn, initial_opacity=0.0)
            self.button_opacities[btn] = btn_opacity


        # Setar o layout ao widget principal
        self.setLayout(self.layout)

        # Mostrar o widget
        self.show()

        # Criar um timer para periodicamente levantar o widget
        self.raise_timer = QTimer()
        self.raise_timer.timeout.connect(self.raise_widget)
        self.raise_timer.start(1000)  # Levantar a janela a cada 1 segundo

        # Impedir que a janela receba foco
        self.set_window_no_activate()



    def raise_widget(self):
        self.raise_()

    def toggle_expand(self):
        if self.expanded:
            target_width = 50
            target_height = 50
        else:
            target_width = 200  # Ajuste conforme necessário
            target_height = 260  # Ajuste conforme necessário

        self.animate_widget(target_width, target_height)

        self.expanded = not self.expanded

    def animate_widget(self, target_width, target_height):
        animation_duration = 300  # Duração da animação em milissegundos
        fade_animation_duration = 300  # Duração da animação de fade em milissegundos

        # Geometria atual da janela
        current_geometry = self.geometry()
        delta_width = target_width - current_geometry.width()
        delta_height = target_height - current_geometry.height()
        new_x = int(round(current_geometry.x() - delta_width))
        new_y = int(round(current_geometry.y() - delta_height / 2.0))  # Centraliza verticalmente ao expandir
        new_geometry = QRect(new_x, new_y, target_width, target_height)

        # Animação da geometria da janela
        geometry_animation = QPropertyAnimation(self, b"geometry")
        geometry_animation.setDuration(animation_duration)
        geometry_animation.setStartValue(current_geometry)
        geometry_animation.setEndValue(new_geometry)
        geometry_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Animação da geometria do background_widget
        background_animation = QPropertyAnimation(self.background_widget, b"geometry")
        background_animation.setDuration(animation_duration)
        background_animation.setStartValue(self.background_widget.geometry())
        background_animation.setEndValue(QRect(0, 0, target_width, target_height))
        background_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Grupo de animações de redimensionamento
        resize_group = QParallelAnimationGroup()
        resize_group.addAnimation(background_animation)
        resize_group.addAnimation(geometry_animation)


        if not self.expanded:
            # **Expandir**

            # 1. Fade out do botão principal
            fade_out_main = QPropertyAnimation(self.main_opacity, b"opacity")
            fade_out_main.setDuration(fade_animation_duration // 2)
            fade_out_main.setStartValue(1.0)
            fade_out_main.setEndValue(0.0)
            fade_out_main.setEasingCurve(QEasingCurve.InOutQuad)

            # 2. Redimensionamento da janela
            # 3. Fade in dos outros botões
            fade_in_buttons = QParallelAnimationGroup()
            for btn in self.fade_buttons:
                fade_in = QPropertyAnimation(self.button_opacities[btn], b"opacity")
                fade_in.setDuration(fade_animation_duration // 2)
                fade_in.setStartValue(0.0)
                fade_in.setEndValue(1.0)
                fade_in.setEasingCurve(QEasingCurve.InOutQuad)
                fade_in_buttons.addAnimation(fade_in)

            # Cria um grupo sequencial para expandir
            self.expand_group = QSequentialAnimationGroup()
            self.expand_group.addAnimation(fade_out_main)
            self.expand_group.addAnimation(resize_group)
            self.expand_group.addAnimation(fade_in_buttons)

            # Conectar o sinal de finalização da animação para atualizar os botões
            self.expand_group.finished.connect(self.update_buttons_visibility)

            # Inicia a animação de expansão
            self.expand_group.start(QSequentialAnimationGroup.DeleteWhenStopped)

        else:
            # **Contrair**

            # 1. Fade out dos outros botões
            fade_out_buttons = QParallelAnimationGroup()
            for btn in self.fade_buttons:
                fade_out = QPropertyAnimation(self.button_opacities[btn], b"opacity")
                fade_out.setDuration(fade_animation_duration // 2)
                fade_out.setStartValue(1.0)
                fade_out.setEndValue(0.0)
                fade_out.setEasingCurve(QEasingCurve.InOutQuad)
                fade_out_buttons.addAnimation(fade_out)

            # 2. Redimensionamento da janela
            # 3. Fade in do botão principal
            fade_in_main = QPropertyAnimation(self.main_opacity, b"opacity")
            fade_in_main.setDuration(fade_animation_duration // 2)
            fade_in_main.setStartValue(0.0)
            fade_in_main.setEndValue(1.0)
            fade_in_main.setEasingCurve(QEasingCurve.InOutQuad)

            # Cria um grupo sequencial para contrair
            self.contract_group = QSequentialAnimationGroup()
            self.contract_group.addAnimation(fade_out_buttons)
            self.contract_group.addAnimation(resize_group)
            self.contract_group.addAnimation(fade_in_main)

            # Conectar o sinal de finalização da animação para atualizar os botões
            self.contract_group.finished.connect(self.update_buttons_visibility)

            # Inicia a animação de contração
            self.contract_group.start(QSequentialAnimationGroup.DeleteWhenStopped)


    def update_buttons_visibility(self):
        if self.expanded:
            # Expansão: Garantir que os botões estejam visíveis
            for btn in self.fade_buttons:
                btn.show()
            self.main_button.hide()
        else:
            # Contração: Garantir que os botões estejam ocultos
            for btn in self.fade_buttons:
                btn.hide()
            self.main_button.show()



    def set_window_no_activate(self):
        if sys.platform == 'win32':
            hwnd = self.winId().__int__()  # Obter o HWND da janela
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000

            # Obter o estilo estendido atual
            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            # Adicionar WS_EX_NOACTIVATE ao estilo estendido
            new_style = current_style | WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

    # Eventos de mouse para permitir movimentar a janela
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def apply_theme(self, theme):
        """Aplica o tema especificado à barra flutuante."""
        if theme == 'light':
            self.setStyleSheet("""
                QPushButton, QToolButton {
                    background-color: transparent;
                    color: black;
                    border: none;  /* Remove sombra e borda - border: 1px solid black; */
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 50);
                }
            """)
            self.background_widget.setStyleSheet("""
                #background_widget {
                    background-color: rgba(236, 236, 236, 75%);
                    border-radius: 15px;
                    border: 1px solid #cccccc;
                }
            """)
            #spinner
            self.spinner.setColor(QColor('#007BFF'))
            #Botoes funcoes
            set_button_icon_with_hover(self.button1, 'fa.smile-o', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.button2, 'ri.briefcase-line', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.conciso, 'ph.arrows-in-line-vertical-fill', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.button3, 'fa5.file-alt', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.button4, 'mdi6.format-list-bulleted', '#171717', '#171717', (20, 20))

            for btn in [self.button1, self.button2, self.conciso, self.button3, self.button4]:
                btn.setStyleSheet("""
                    font-size: 12px;
                    color: black;
                    text-align: left;
                    border-radius: 5px;
                    font-weight: 500;
                    padding-left: 10px;
                """)
            #Botão principal
            set_button_icon_with_hover(self.main_button, 'mdi.assistant', '#171717', '#171717', (30, 30))
            self.main_button.setStyleSheet("""
                QPushButton{
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover{
                    background-color: rgba(0, 0, 0, 25%);
                    border-radius: 20%;
                }  
            """)
            #Botões superiores
            set_button_icon_with_hover(self.top_button1, 'mdi.magnify-scan', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.top_button2, 'ph.pencil-simple', '#171717', '#171717', (20, 20))
            for btn in [self.top_button1, self.top_button2]:
                btn.setStyleSheet("""
                    QToolButton{
                        font-size: 12px;
                        border-radius: 8px;
                        background-color: rgba(0, 0, 0, 15%);
                        border: none;
                    }
                    QToolButton:hover { 
                        background-color: rgba(0, 0, 0, 25%);
                    }
                """)
            #Divisor
            self.divider.setStyleSheet("background-color: rgba(0, 0, 0, 25%); border: none;")
            #Botões inferiores
            set_button_icon_with_hover(self.bottom_button1, 'ph.arrow-square-left-light', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.bottom_button3, 'mdi.refresh', '#171717', '#171717', (20, 20))
            set_button_icon_with_hover(self.bottom_button2, 'mdi.window-minimize', '#171717', '#171717', (20, 20))

            for btn in [self.bottom_button1, self.bottom_button3, self.bottom_button2]:
                btn.setStyleSheet("""
                    QPushButton{
                        font-size: 12px;
                        border-radius: 8px;
                        background-color: rgba(0, 0, 0, 15%);
                        border: none;
                    }
                    QPushButton:hover { 
                        background-color: rgba(0, 0, 0, 25%);
                    }
                """)
        elif theme == 'dark':
            self.setStyleSheet("""
                QPushButton, QToolButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(224, 224, 224, 75%);
                    color: black;
                }
            """)
            self.background_widget.setStyleSheet("""
                #background_widget {
                    background-color: rgba(23, 23, 23, 85%);
                    border-radius: 15px;
                    border: 1px solid #666666;
                }
            """)
            #spinner
            self.spinner.setColor(QColor('#FFFFFF'))
            #Botoes funcoes
            set_button_icon_with_hover(self.button1, 'fa.smile-o', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.button2, 'ri.briefcase-line', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.conciso, 'ph.arrows-in-line-vertical-fill', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.button3, 'fa5.file-alt', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.button4, 'mdi6.format-list-bulleted', '#b4b4b4', '#171717', (20, 20))

            for btn in [self.button1, self.button2, self.conciso, self.button3, self.button4]:
                btn.setStyleSheet("""
                    QPushButton{
                        font-size: 12px;
                        color: white;
                        text-align: left;
                        border-radius: 5px;
                        font-weight: 500;
                        padding-left: 10px;
                    }
                    QPushButton:hover {
                        color: black;
                    }
                """)
            #Botão principal
            set_button_icon_with_hover(self.main_button, 'mdi.assistant', '#b4b4b4', '#171717', (30, 30))
            self.main_button.setStyleSheet("""
                QPushButton{
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover{
                    background-color: rgba(224, 224, 224, 75%);
                    border-radius: 20%;
                }  
            """)
            #Botões superiores
            set_button_icon_with_hover(self.top_button1, 'mdi.magnify-scan', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.top_button2, 'ph.pencil-simple', '#b4b4b4', '#171717', (20, 20))
            for btn in [self.top_button1, self.top_button2]:
                btn.setStyleSheet("""
                    QToolButton{
                        font-size: 12px;
                        border-radius: 8px;
                        background-color: rgba(224, 224, 224, 15%);
                        border: none;
                    }
                    QToolButton:hover { 
                        background-color: rgba(224, 224, 224, 75%);
                        color: black;
                    }
                """)
            #Divisor
            self.divider.setStyleSheet("background-color: rgba(224, 224, 224, 25%); border: none;")
            #Botões inferiores
            set_button_icon_with_hover(self.bottom_button1, 'ph.arrow-square-left-light', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.bottom_button3, 'mdi.refresh', '#b4b4b4', '#171717', (20, 20))
            set_button_icon_with_hover(self.bottom_button2, 'mdi.window-minimize', '#b4b4b4', '#171717', (20, 20))

            for btn in [self.bottom_button1, self.bottom_button3, self.bottom_button2]:
                btn.setStyleSheet("""
                    QPushButton{
                        font-size: 12px;
                        border-radius: 8px;
                        background-color: rgba(224, 224, 224, 15%);
                        border: none;
                    }
                    QPushButton:hover { 
                        background-color: rgba(224, 224, 224, 75%);
                    }
                """)

    def handle_casual_format(self):
        # 1. Copiar o texto
        copied_text = self.copy_text()
        # Esconder os botões
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            # Reabilita os botões
            self.reactivate_buttons()
            return

        # Captura a janela ativa antes de enviar a solicitação
        self.original_hwnd = ctypes.windll.user32.GetForegroundWindow()

        # Atualiza original_text e habilita o botão
        self.original_text = copied_text
        self.bottom_button3.setEnabled(True)

        # Define a ação atual
        self.current_action = 'casual'

        # Cria o system_content e user_content
        system_content = """Você é uma assistente de escrita. Você transforma textos para um tom casual.
        Por favor, formate o seguinte texto para ser mais casual. Não inclua nenhum outro comentário, apenas o texto formatado."""

        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Formatando para casual:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Enviar o system_content e user_content para a API
        floating_widget_action(self.main_window, ("casual", {"system_content": system_content, "user_content": user_content}, copied_text))

        # Preparar para receber a resposta
        self.waiting_for_response = True


    def handle_professional_format(self):
        copied_text = self.copy_text()
        # Esconder os botões
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            self.reactivate_buttons()
            return

        self.original_hwnd = ctypes.windll.user32.GetForegroundWindow()

        self.original_text = copied_text
        self.bottom_button3.setEnabled(True)

        self.current_action = 'professional'

        name = load_name()

        # Conteúdo do sistema e do usuário
        system_content = f"""Você é uma assistente de escrita profissional. Por favor, transforme o texto a seguir em um texto com tom profissional, sem adicionar informações extras ou mencionar que está formatando o texto. Apenas faça a transformação e devolva o texto."""
        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Tornando profissional:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Enviar o prompt para a API
        floating_widget_action(self.main_window, ("professional", prompt_data, copied_text))

        self.waiting_for_response = True

    def handle_concise_format(self):
        # Mesmo processo que handle_casual_format
        copied_text = self.copy_text()
        # Esconder os botões
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            self.reactivate_buttons()
            return

        self.original_hwnd = ctypes.windll.user32.GetForegroundWindow()

        self.original_text = copied_text
        self.bottom_button3.setEnabled(True)

        self.current_action = 'concise'

        # Conteúdo do sistema e do usuário
        system_content = """Você é uma assistente de escrita especializada em tornar textos mais concisos.
        Sua tarefa é reformular o texto a seguir, tornando-o mais claro, coeso e direto ao ponto, sem omitir informações importantes. Não mencione esse prompt ou a tarefa em si."""
        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Tornando texto mais conciso:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Enviar o prompt para a API
        floating_widget_action(self.main_window, ("concise", prompt_data, copied_text))

        self.waiting_for_response = True

    def handle_review_format(self):
        # Mesmo processo que handle_casual_format
        copied_text = self.copy_text()
        # Esconder os botões
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            self.reactivate_buttons()
            return

        self.original_hwnd = ctypes.windll.user32.GetForegroundWindow()

        self.original_text = copied_text
        self.bottom_button3.setEnabled(True)

        self.current_action = 'review'

        # Conteúdo do sistema e do usuário
        system_content = """Você é uma assistente de escrita focada em revisar textos. Sua tarefa é corrigir todos os erros gramaticais, ortográficos e de estilo, tornando o texto mais claro e coeso. Não mencione esse prompt ou a tarefa em si."""
        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Revisando texto:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Enviar o prompt para a API
        floating_widget_action(self.main_window, ("review", prompt_data, copied_text))

        self.waiting_for_response = True


    def handle_rewrite_format(self):
        # 1. Copiar o texto (já implementado)
        copied_text = self.copy_text()
        # Esconder os botões
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            # Reabilita os botões
            self.reactivate_buttons()
            return

        # Captura a janela ativa antes de abrir a modal
        self.original_hwnd = ctypes.windll.user32.GetForegroundWindow()
        # Debug
        # print(f"Janela ativa capturada: HWND={self.original_hwnd}")

        # Atualiza copied_text e habilita o botão
        self.original_text = copied_text
        self.bottom_button3.setEnabled(True)

        # 2. Definir a ação atual como 'rewrite'
        self.current_action = 'rewrite'
        #Debug
        # print(f"Current action set to: {self.current_action}")

        # 3. Abrir a modal para obter as instruções do usuário
        instructions, ok = self.get_user_instructions()
        if not ok or not instructions.strip():
            # O usuário cancelou ou não inseriu instruções
            # Resetar a ação atual
            self.current_action = None
            print("Ação resetada para: None")
            # Reabilita os botões
            self.reactivate_buttons()
            return

        # 4. Criar o prompt separado por system_content e user_content
        system_content = f"""Você é uma assistente de escrita focada em reescrever textos. Utilize as instruções fornecidas para reescrever o texto da melhor forma possível.
        Instruções: {instructions}"""
        user_content = copied_text

        # 5. Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Reescrevendo texto com as instruções:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # 6. Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # 7. Enviar o prompt para a API através de api_calls.py
        floating_widget_action(self.main_window, ("rewrite", prompt_data, copied_text))

        # 8. Preparar para receber a resposta
        self.waiting_for_response = True



    #Modal para obter instruções do usuário
    def get_user_instructions(self):
        """
        Abre uma modal personalizada com bordas arredondadas para o usuário inserir instruções.
        Retorna o texto inserido e se o usuário clicou em OK.
        """
        theme = load_theme()  # Obtém o tema atual

        dialog = QDialog(self.main_window, flags=Qt.FramelessWindowHint | Qt.Dialog | Qt.Tool | Qt.WindowStaysOnTopHint)
        dialog.setWindowModality(Qt.NonModal)  # Alterado para NonModal
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setAttribute(Qt.WA_ShowWithoutActivating)  # Impede ativação ao mostrar
        dialog.setFixedSize(400, 250)


        # Centralizar na tela
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        dialog.move(
            (screen_geometry.width() - dialog.width()) // 2,
            (screen_geometry.height() - dialog.height()) // 2
        )

        # Widget de fundo com bordas arredondadas
        background_widget = QWidget(dialog)
        background_widget.setGeometry(0, 0, dialog.width(), dialog.height())

        # Layout interno do background_widget
        layout = QVBoxLayout(background_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Textarea com placeholder
        text_edit = CustomTextEdit(300)
        text_edit.setPlaceholderText("Como você deseja reescrever o texto?")
        layout.addWidget(text_edit)

        # Botões OK e Cancelar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancelar")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Conectar os botões
        ok_button.clicked.connect(dialog.accept)
        # Estilização

        if theme == 'light':
            background_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: #ECECEC;
                    border-radius: 15px;
                    color: black;
                    border: 1px solid #cccccc;
                }}
                QTextEdit {{
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                QPushButton {{
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: #0056b3;
                }}
            """)
        else:
            background_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: #2E2E2E;
                    border-radius: 15px;
                    color: white;
                    border: 1px solid #cccccc;
                }}
                QTextEdit {{
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                QPushButton {{
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }}
                QPushButton:hover {{
                    background-color: #0056b3;
                }}
            """) 


        # Animação de fade-out para o cancelamento
        def fade_out_and_close():
            fade_out = QPropertyAnimation(dialog, b"windowOpacity")
            fade_out.setDuration(300)
            fade_out.setStartValue(dialog.windowOpacity())
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(close_after_animation) 
            # Manter uma referência para evitar coleta de lixo
            dialog.fade_out = fade_out
            fade_out.start()

        def close_after_animation():
            dialog.close()
            # **Reativar a janela original após fechar a modal**
            if self.main_window:
                ctypes.windll.user32.SetForegroundWindow(self.main_window.winId().__int__())
                self.main_window.activateWindow()
                self.main_window.raise_()

        cancel_button.clicked.connect(fade_out_and_close)

        # Animação de fade-in
        dialog.setWindowOpacity(0.0)
        fade_in = QPropertyAnimation(dialog, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.start()

        result = dialog.exec_()

        if result == QDialog.Accepted:
            return text_edit.toPlainText(), True
        else:
            return "", False



    def handle_summarize_format(self):
        copied_text = self.copy_text()
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()

        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            self.reactivate_buttons()
            return
        
        # Definir a ação atual
        self.current_action = 'summarize'

        # Criar o conteúdo do sistema e do usuário
        system_content = """Você é uma assistente de escrita focada em resumir textos de forma clara e objetiva.
        Você deve resumir o texto a seguir em poucas palavras, mantendo as informações mais importantes.
        Você não conversará com o usuário, apenas resumirá o texto."""
        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Resumindo texto:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Enviar o prompt para a API através de api_calls.py
        floating_widget_action(self.main_window, ("summarize", prompt_data, copied_text))

        self.waiting_for_response = True


    def handle_keypoints_format(self):
        copied_text = self.copy_text()
        self.deactivate_buttons()
        # Mostrar o spinner
        self.spinner.start()
        if not copied_text:
            show_custom_message('Alerta', 'Nenhum texto selecionado')
            self.reactivate_buttons()
            return
        
        # Definir a ação atual
        self.current_action = 'keypoints'

        # Criar o conteúdo do sistema e do usuário
        system_content = """Você é uma assistente de escrita focada em extrair os pontos-chave de textos. Extraia apenas os pontos mais importantes."""
        user_content = copied_text

        # Exibir a pergunta na MainWindow
        user_bubble = ChatBubble(f"Extraindo pontos-chave:\n\n{copied_text}", sender='user')
        self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)
        self.main_window.autoscroll_chat()

        # Preparar os dados para enviar
        prompt_data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Enviar o prompt para a API através de api_calls.py
        floating_widget_action(self.main_window, ("keypoints", prompt_data, copied_text))

        self.waiting_for_response = True


    def show_response_modal(self, response_text):
        dialog = QDialog(self, flags=Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        # Obter dimensões da tela
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_height = int(screen_geometry.height() * 0.7)

        # Estimar a altura com base no número de quebras de linha
        num_lines = response_text.count('\n') + 1
        line_height = 20  # Aproximação da altura por linha (em pixels)
        
        # Estimar a altura com base no número de caracteres
        num_chars = len(response_text)
        char_height_factor = 0.2  # Aproximação de altura por caractere (ajustável conforme necessário)
        estimated_height_by_chars = int(150 + num_chars * char_height_factor)

        # Calcular o required_height pegando o maior entre altura por linhas ou caracteres
        required_height = min(max(150 + num_lines * line_height, estimated_height_by_chars), max_height)
        #debug
        # print("Caracteres:", num_chars, "Altura estimada:", estimated_height_by_chars, "Altura por linhas:", 150 + num_lines * line_height, "Altura final:", required_height)

        #definir tamanho
        #dialog.setFixedSize(400, required_height)
        dialog.setFixedWidth(400)
        dialog.setMinimumHeight(required_height)
        dialog.setMaximumHeight(max_height)

        # Centralizar na tela
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        dialog.move(
            (screen_geometry.width() - dialog.width()) // 2,
            (screen_geometry.height() - dialog.height()) // 2
        )

        # Widget de fundo com bordas arredondadas
        background_widget = QWidget(dialog)
        theme = load_theme()
            
        if theme == 'light':
            background_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 15px;
                    color: black;
                    border: 1px solid #ccc;
                }
                QTextEdit {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-weight: 600;
                }
                QTextEdit QScrollBar:vertical {
                    background: transparent;
                    width: 8px;
                    margin: 0px 0px 0px 0px;
                }
                QTextEdit QScrollBar::handle:vertical {
                    background: #bfbfbf;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QTextEdit QScrollBar::handle:vertical:hover {
                    background: #a6a6a6;
                }
                QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {
                    background: none;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
        else:
            background_widget.setStyleSheet("""
                QWidget {
                    background-color: #2E2E2E;
                    border-radius: 15px;
                    color: black;
                    border: 1px solid #ccc;
                }
                QTextEdit {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-weight: 600;
                }
                QTextEdit QScrollBar:vertical {
                    background: transparent;
                    width: 8px;
                    margin: 0px 0px 0px 0px;
                }
                QTextEdit QScrollBar::handle:vertical {
                    background: #bfbfbf;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QTextEdit QScrollBar::handle:vertical:hover {
                    background: #a6a6a6;
                }
                QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {
                    background: none;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
        
        background_widget.setGeometry(0, 0, dialog.width(), dialog.height())

        # Layout interno do background_widget
        layout = QVBoxLayout(background_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Textarea não editável
        text_edit = QTextEdit()
        text_edit.setPlainText(response_text)
        text_edit.setReadOnly(True)


        layout.addWidget(text_edit)

        # Botão OK
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)

        # Animação de fade-in
        dialog.setWindowOpacity(0.0)
        fade_in = QPropertyAnimation(dialog, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.start()

        # Animação de fade-out
        def fade_out_and_close():
            fade_out = QPropertyAnimation(dialog, b"windowOpacity")
            fade_out.setDuration(300)
            fade_out.setStartValue(dialog.windowOpacity())
            fade_out.setEndValue(0.0)
            fade_out.finished.connect(dialog.close)
            dialog.fade_out = fade_out
            fade_out.start()

        ok_button.clicked.connect(fade_out_and_close)

        dialog.exec_()

    @pyqtSlot(str)
    def handle_api_response(self, answer):
        if self.waiting_for_response:
            # Define a resposta no clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(answer)
            #debug - print mensagem copiada
            # print(f"Texto copiado para o clipboard: {answer}")
            # Verifica se a ação atual requer exibir a modal
            if self.current_action in ['keypoints', 'summarize']:
                self.show_response_modal(answer)
            else:
                # Ativar a janela original
                if self.original_hwnd:
                    # #debug
                    # window_title, process_name = get_window_info(self.original_hwnd)
                    # print(f"Tentando ativar a janela: HWND={self.original_hwnd}, Título='{window_title}', Processo='{process_name}'")

                    # Permitir que a janela original seja trazida para frente
                    self.activate_window(self.original_hwnd)
                    # ctypes.windll.user32.AllowSetForegroundWindow(-1)

                    #debug
                    # result = ctypes.windll.user32.SetForegroundWindow(self.original_hwnd)
                    # print(f"SetForegroundWindow retornou: {result}")

                    # Simular Ctrl+V após um pequeno atraso
                    QTimer.singleShot(500, self.paste_text)
                else:
                    # Se não tiver HWND, apenas colar
                    QTimer.singleShot(500, self.paste_text)

            # Resetar flags
            self.waiting_for_response = False
            self.current_action = None
            self.original_hwnd = None

            # Reativar os botões
            self.reactivate_buttons()


    def copy_text(self):
        """
        Copia o texto selecionado simulando Ctrl+C e retorna o texto copiado.
        Exibe uma mensagem de aviso se nenhum texto estiver selecionado.
        """
        # Limpa o clipboard antes de copiar
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Clipboard)

        # Simula Ctrl+C
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Pressiona Ctrl
        ctypes.windll.user32.keybd_event(0x43, 0, 0, 0)  # Pressiona C
        ctypes.windll.user32.keybd_event(0x43, 0, 2, 0)  # Solta C
        ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)  # Solta Ctrl

        # Processa eventos para permitir a cópia
        QApplication.processEvents()

        # Cria um loop de eventos para aguardar a atualização do clipboard
        loop = QEventLoop()
        QTimer.singleShot(300, loop.quit)  # Aguarda 300ms
        loop.exec_()

        # Obtém o texto do clipboard após a cópia
        copied_text = clipboard.text().strip()

        # Debug
        # print("Texto copiado:", copied_text)

        # Verifica se o texto está vazio
        if not copied_text:
            print("Nenhum texto selecionado para copiar.")
            return None

        return copied_text

    def paste_text(self):
        try:
            # Debug
            # print("Iniciando a função paste_text...")
            # Verificar qual janela está ativa antes
            # active_hwnd = ctypes.windll.user32.GetForegroundWindow()
            # print(f"Janela ativa antes de colar: HWND={active_hwnd}")

            # Definir constantes
            VK_CONTROL = 0x11
            VK_V = 0x56
            KEYEVENTF_KEYUP = 0x0002
            KEYEVENTF_EXTENDEDKEY = 0x0001
            VK_BACKSPACE = 0x08  # Tecla de apagar (Backspace)

            #debug
            # # Verificar o estado inicial das teclas Ctrl e V
            # ctrl_state_before = ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL)  # VK_CONTROL
            # v_state_before = ctypes.windll.user32.GetAsyncKeyState(VK_V)           # VK_V
            # print(f"Estado da tecla Ctrl antes: {ctrl_state_before}")
            # print(f"Estado da tecla V antes: {v_state_before}")

            # Simular a tecla Backspace para limpar antes de colar
            ctypes.windll.user32.keybd_event(VK_BACKSPACE, 0, 0, 0)  # Pressionar Backspace
            ctypes.windll.user32.keybd_event(VK_BACKSPACE, 0, KEYEVENTF_KEYUP, 0)  # Soltar Backspace

            # Pressionar Ctrl (com flag extended key)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.05)

            # Pressionar V
            ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
            time.sleep(0.05)

            # Soltar V
            ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)

            # Soltar Ctrl (com flag extended key)
            ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP | KEYEVENTF_EXTENDEDKEY, 0)
            time.sleep(0.05)

            #debug
            # Verificar qual janela está ativa depois
            # active_hwnd_after = ctypes.windll.user32.GetForegroundWindow()
            # print(f"Janela ativa após colar: HWND={active_hwnd_after}")
            
            # if active_hwnd != active_hwnd_after:
            #     print("Aviso: A janela ativa mudou durante a colagem.")

        except Exception as e:
            print(f"Erro ao tentar colar o texto: {e}")


    def bring_main_window(self):
        if self.main_window:
            if self.main_window.isMinimized() or not self.main_window.isVisible():
                # Se a janela estiver minimizada ou não visível, restaura e traz para frente
                self.main_window.showNormal()
                self.main_window.raise_()
                self.main_window.activateWindow()
            else:
                # Se a janela já estiver visível, minimiza
                self.main_window.showMinimized()

    def return_copied_text(self):
        if self.original_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.original_text)
            show_custom_message('Alerta', 'Texto copiado para o clipboard')

    #Esconde botoes
    def deactivate_buttons(self):
        # Esconde os botões enquanto a solicitação está em andamento
        for btn in self.fade_buttons:
            btn.hide()
    #Mostra os botoes        
    def reactivate_buttons(self):
        # Parar e esconder o spinner
        self.spinner.stop()
        # Mostrar os botões novamente se o widget estiver expandido
        if self.expanded:
            for btn in self.fade_buttons:
                btn.show()

    #Ativa a janela            
    def activate_window(self, hwnd):
        try:
            #debug
            # print(f"Ativando a janela com HWND={hwnd}")
            # Obter a janela atualmente em primeiro plano
            foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()

            #Debug
            # print(f"Janela atualmente em primeiro plano: HWND={foreground_hwnd}")

            if foreground_hwnd != hwnd:
                # Obter IDs de thread
                current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
                foreground_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, 0)
                target_thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, 0)

                # Anexar threads
                ctypes.windll.user32.AttachThreadInput(target_thread_id, foreground_thread_id, True)

                # Ativar janela
                result = ctypes.windll.user32.SetForegroundWindow(hwnd)
                #Debug
                # print(f"SetForegroundWindow retornou: {result}")

                # Desanexar threads
                ctypes.windll.user32.AttachThreadInput(target_thread_id, foreground_thread_id, False)
            else:
                pass
                #Debug
                # print("A janela de destino já está em primeiro plano.")

        except Exception as e:
            print(f"Erro ao ativar a janela: {e}")

    #Funcoes para mover a janela
    def main_button_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.click_timer.start(200)  # Define 200ms como tempo limite para diferenciar clique de arraste
            event.accept()

    def main_button_mouse_move_event(self, event):
        if self.is_dragging:
            # Se o mouse for movido, isso significa que é um arraste
            if self.click_timer.isActive():
                self.click_timer.stop()  # Cancela o clique se o usuário mover o mouse (arraste)
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def main_button_mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            # Se o timer ainda estiver ativo, significa que foi um clique rápido (não arraste)
            if self.click_timer.isActive():
                self.click_timer.stop()  # Cancela o temporizador de clique após o clique ser processado
                self.toggle_expand()  # Expande/Contrai se for um clique rápido
            event.accept()




#Debug - Função para obter o título da janela e o nome do processo a partir do HWND   
def get_window_info(hwnd):
    """
    Obtém o título da janela e o nome do processo a partir do HWND.
    
    Parâmetros:
        hwnd (int): Handle da janela.
    
    Retorna:
        tuple: (título_da_janela, nome_do_processo)
    """
    # Funções do user32 e kernel32
    GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
    GetWindowTextW = ctypes.windll.user32.GetWindowTextW
    GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
    OpenProcess = ctypes.windll.kernel32.OpenProcess
    GetModuleFileNameExW = ctypes.windll.psapi.GetModuleFileNameExW
    CloseHandle = ctypes.windll.kernel32.CloseHandle

    # Obter o comprimento do título da janela
    length = GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buff, length + 1)
    window_title = buff.value

    # Obter o ID do processo
    pid = wintypes.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_id = pid.value

    # Definir as permissões para abrir o processo
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    process_handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id)

    if process_handle:
        # Obter o nome do módulo base (executável)
        filename_buff = ctypes.create_unicode_buffer(260)
        GetModuleFileNameExW(process_handle, 0, filename_buff, 260)
        process_name = filename_buff.value
        CloseHandle(process_handle)
    else:
        process_name = "Desconhecido"

    return window_title, process_name
