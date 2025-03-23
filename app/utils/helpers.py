# app/utils/helpers.py

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QTextCursor, QFontMetrics, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QByteArray, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5 import QtWidgets, QtCore
from app.utils.settings import load_theme
import qtawesome as qta


#Funcoes para gerenciar icones SVG
def set_button_icon_with_hover_svg(button, icon_path, default_color, hover_color, icon_size=(24, 24)):
    """
    Define ícones SVG com comportamento de hover, permitindo trocar a cor dinamicamente.

    Args:
        button (QPushButton): O botão ao qual o comportamento será adicionado.
        icon_path (str): Caminho do arquivo SVG.
        default_color (str): Cor padrão do ícone.
        hover_color (str): Cor do ícone quando o mouse está sobre o botão.
        icon_size (tuple): O tamanho do ícone (largura, altura).
    """
    # Função para renderizar o SVG com a cor especificada
    def render_svg_with_color(svg_path, color, size):
        svg_renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(size[0], size[1])
        pixmap.fill(QtCore.Qt.transparent)
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()
        return QIcon(pixmap)

    # Ícones para os diferentes estados
    default_icon = render_svg_with_color(icon_path, default_color, icon_size)
    hover_icon = render_svg_with_color(icon_path, hover_color, icon_size)

    # Definir ícone padrão
    button.setIcon(default_icon)
    button.setIconSize(QtCore.QSize(*icon_size))

    # Substituir enterEvent e leaveEvent para controlar o hover
    def on_hover_enter(event):
        button.setIcon(hover_icon)
        super(button.__class__, button).enterEvent(event)

    def on_hover_leave(event):
        button.setIcon(default_icon)
        super(button.__class__, button).leaveEvent(event)

    # Associar eventos ao botão
    button.enterEvent = on_hover_enter
    button.leaveEvent = on_hover_leave

#Tratativa hover para icones qta5
def set_button_icon_with_hover(button, icon_name, default_color, hover_color, icon_size=(24, 24)):
    """
    Função genérica para definir um botão com ícone e comportamento de hover.
    
    Args:
        button (QPushButton): O botão ao qual o comportamento será adicionado.
        icon_name (str): O nome do ícone no FontAwesome.
        default_color (str): A cor do ícone no estado normal.
        hover_color (str): A cor do ícone no estado de hover.
        icon_size (tuple): O tamanho do ícone (largura, altura).
    """
    # Ícones para os diferentes estados
    default_icon = qta.icon(icon_name, color=default_color)
    hover_icon = qta.icon(icon_name, color=hover_color)

    # Definir ícone padrão
    button.setIcon(default_icon)
    button.setIconSize(QtCore.QSize(*icon_size))

    # Substituir enterEvent e leaveEvent para controlar o hover
    def on_hover_enter(event):
        button.setIcon(hover_icon)
        super(button.__class__, button).enterEvent(event)

    def on_hover_leave(event):
        button.setIcon(default_icon)
        super(button.__class__, button).leaveEvent(event)

    # Associar eventos ao botão
    button.enterEvent = on_hover_enter
    button.leaveEvent = on_hover_leave


#Mensagem customizada de erro
def show_custom_message(message_type, message):
    """
    Exibe uma modal personalizada com base no tipo de mensagem.
    
    Parâmetros:
        message_type (str): Tipo da mensagem ('Alerta', 'Confirmação', 'Erro').
        message (str): Texto da mensagem a ser exibida.
    """
    theme = load_theme()  # Carregar o tema atual



    # Criar o diálogo
    dialog = QDialog()
    # Obter a janela ativa para definir como parent
    parent = QtWidgets.QApplication.activeWindow()

    # Criar o diálogo com flags ajustadas para ficar sempre no topo e não aparecer na barra de tarefas
    dialog = QDialog(parent, flags=QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
    
    dialog.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    dialog.setModal(True)

    # Layout principal
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)
    dialog.setLayout(layout)

    # Widget de fundo com bordas arredondadas
    background_widget = QtWidgets.QWidget()
    if theme == 'light':
        background_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(236, 236, 236, 0.7);
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """)
    else:
        background_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(23, 23, 23, 0.7);
                border-radius: 10px;
                border: 1px solid #cccccc;
            }
        """) 
    bg_layout = QVBoxLayout()
    bg_layout.setContentsMargins(15, 15, 15, 15)
    background_widget.setLayout(bg_layout)


    # Texto da mensagem
    message_label = QLabel(message)
    message_label.setWordWrap(True)
    message_label.setAlignment(QtCore.Qt.AlignCenter)
    bg_layout.addWidget(message_label)
    if theme == 'light':
        message_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
    else:
        message_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                color: white;
            }
        """)
    # Adicionar o widget de fundo ao layout principal
    layout.addWidget(background_widget)

    # Cálculo do tamanho baseado no conteúdo
    font_metrics = QFontMetrics(message_label.font())
    max_width = 300  # Largura máxima da modal
    text_width = font_metrics.boundingRect(0, 0, max_width, 0, QtCore.Qt.TextWordWrap, message).width()
    text_height = font_metrics.boundingRect(0, 0, max_width, 0, QtCore.Qt.TextWordWrap, message).height()

    # Definir tamanho dinâmico
    padding = 60  # Padding adicional para ícone e margens
    calculated_width = min(text_width + 80, max_width)  # 40 para padding horizontal
    calculated_height = text_height + padding + 50
    # Definir tamanho mínimo e máximo
    dialog.setFixedSize(calculated_width, calculated_height)

    # Centralizar na tela
    screen = QtWidgets.QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    dialog.move(
        (screen_geometry.width() - dialog.width()) // 2,
        (screen_geometry.height() - dialog.height()) // 2
    )

    # Animação de fade-in
    dialog.setWindowOpacity(0.0)
    fade_in = QPropertyAnimation(dialog, b"windowOpacity")
    fade_in.setDuration(300)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.InOutQuad)
    fade_in.start()
    # Animação de fade-out para o cancelamento
    def fade_out_and_close():
        fade_out = QPropertyAnimation(dialog, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(dialog.windowOpacity())
        fade_out.setEndValue(0.0)

        # Conectar ao fechamento após a animação com um pequeno atraso para garantir que o fechamento seja processado
        fade_out.finished.connect(close_after_animation) 

        # Manter uma referência para a animação para evitar coleta de lixo
        dialog.fade_out = fade_out
        fade_out.start()
    def close_after_animation():
        # Fechar a janela após o fade
        dialog.close()

    # Timer para iniciar o fade-out após 1 segundo
    QTimer.singleShot(1000, fade_out_and_close)

    # Exibir a modal
    dialog.exec_()


class CustomTextEdit(QtWidgets.QTextEdit):
    def __init__(self, max_characters, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_characters = max_characters
        self.textChanged.connect(self.check_character_limit)

    def check_character_limit(self):
        # Pega o texto atual
        current_text = self.toPlainText()

        # Verifica se o texto ultrapassa o limite
        if len(current_text) > self.max_characters:
            # Limita o texto ao máximo de caracteres
            self.setPlainText(current_text[:self.max_characters])

            # Move o cursor para o final
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)

