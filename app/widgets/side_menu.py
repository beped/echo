# app/widgets/side_menu.py
import ctypes
from PyQt5.QtWidgets import QFrame, QLabel, QWidget, QDialog, QApplication, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QPropertyAnimation
from app.utils.settings import load_theme, load_name, clear_all_settings, resource_path
from app.utils.helpers import show_custom_message, set_button_icon_with_hover_svg, set_button_icon_with_hover, CustomTextEdit
from app.widgets.chat_bubble import ChatBubble
from PyQt5.QtCore import Qt

class SideMenuWindow(QWidget):
    # Definindo um sinal que emitirá o texto copiado
    sidemenu_action_triggered = pyqtSignal(tuple)
    def __init__(self, main_window=None):
        super().__init__(parent=main_window)
        self.main_window = main_window  # Referência para MainWindow
        self.expanded = False  # Estado inicial do menu lateral (fechado)


        # Criar QFrame como contêiner com borda direita
        self.frame = QFrame(self)
        self.frame.setObjectName("sideMenuFrame")
        self.frame.setFrameShape(QFrame.NoFrame)  # Remove a moldura padrão

        # Layout interno do frame
        self.frame_layout = QVBoxLayout()
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.setSpacing(0)
        self.frame.setLayout(self.frame_layout)

        # Título da seção - Escrita
        self.section_label_format_text = QLabel("Escrita")
        self.frame_layout.addWidget(self.section_label_format_text)
        self.section_label_format_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Alinha texto à esquerda e verticalmente centralizado
        self.section_label_format_text.setFixedHeight(30)  # Define altura fixa

        # Botão "Casual"
        self.casual_button = QPushButton("Casual")
        self.casual_button.setFixedHeight(40)
        self.casual_button.setObjectName("casualButton")
        self.casual_button.clicked.connect(self.format_casual)
        self.frame_layout.addWidget(self.casual_button)
        # Botão "Formal"
        self.formal_button = QPushButton("Formal")
        self.formal_button.setFixedHeight(40)
        self.formal_button.setObjectName("formalButton")  # Nome de objeto para estilização
        self.formal_button.clicked.connect(self.format_formal)
        self.frame_layout.addWidget(self.formal_button)
        # Botão "Corrigir"
        self.correction_button = QPushButton("Corrigir")
        self.correction_button.setFixedHeight(40)
        self.correction_button.setObjectName("correctButton")
        self.correction_button.clicked.connect(self.format_correction)
        self.frame_layout.addWidget(self.correction_button) #correction button
        # Botão "Conciso"
        self.concise_button = QPushButton("Conciso")
        self.concise_button.setFixedHeight(40)
        self.concise_button.setObjectName("correctButton")
        self.concise_button.clicked.connect(self.format_concise)
        self.frame_layout.addWidget(self.concise_button) #concise button
        # Botão "Reescrever"
        self.rewrite_button = QPushButton("Reescrever")
        self.rewrite_button.setFixedHeight(40)
        self.rewrite_button.setObjectName("rewriteButton")
        self.rewrite_button.clicked.connect(self.format_rewrite)
        self.frame_layout.addWidget(self.rewrite_button)

        # Título da seção - Leitura
        self.section_label_read_text = QLabel("Leitura")
        self.frame_layout.addWidget(self.section_label_read_text)
        self.section_label_read_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Alinha texto à esquerda e verticalmente centralizado
        self.section_label_read_text.setFixedHeight(30)  # Define altura fixa
        # Botão "Resumir"
        self.resume_button = QPushButton("Resumir")
        self.resume_button.setFixedHeight(40)
        self.resume_button.setObjectName("resumeButton")  # Nome de objeto para estilização
        self.resume_button.clicked.connect(self.format_resume)
        self.frame_layout.addWidget(self.resume_button)

        # Botão "Síntese"
        self.synthesis_button = QPushButton("Síntese")
        self.synthesis_button.setFixedHeight(40)
        self.synthesis_button.setObjectName("synthesisButton")
        self.synthesis_button.clicked.connect(self.format_synthesis)
        self.frame_layout.addWidget(self.synthesis_button)
        # Botão "Leitura Personalizada"
        self.custom_reading_button = QPushButton("Infos")
        self.custom_reading_button.setFixedHeight(40)
        self.custom_reading_button.setObjectName("customReadingButton")
        self.custom_reading_button.clicked.connect(self.format_custom_reading)
        self.frame_layout.addWidget(self.custom_reading_button)

        # Exemplo de outro botão: "Ajuda"
        # self.help_button = QtWidgets.QPushButton("Teste2")
        # self.help_button.setFixedHeight(40)
        # self.help_button.setObjectName("synthesisButton2")
        # self.help_button.clicked.connect(self.open_help2)
        # self.frame_layout.addWidget(self.help_button)
        # # Exemplo de outro botão: "Ajuda"
        # self.help_button = QtWidgets.QPushButton("Teste1")
        # self.help_button.setFixedHeight(40)
        # self.help_button.setObjectName("synthesisButton")
        # self.help_button.clicked.connect(self.open_help)
        # self.frame_layout.addWidget(self.help_button)
        # Adicionar espaçamento flexível
        # Debug = Botão "Teste"
        # self.debug = QtWidgets.QPushButton("Teste")
        # self.debug.setFixedHeight(40)
        # self.debug.setObjectName("debug")  # Nome de objeto para estilização
        # self.debug.clicked.connect(clear_all_settings)
        # self.frame_layout.addWidget(self.debug)


        #Adiciona espaçamento
        self.frame_layout.addStretch()

        # Adicionar QFrame ao layout principal do SideMenuWindow
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

        # Aplicar o tema atual na inicialização
        current_theme = load_theme()
        self.apply_theme(current_theme)

    def apply_theme(self, theme):
        """
        Aplica o estilo ao SideMenuWindow com base no tema selecionado.
        """
        hover_background = "rgba(0, 0, 0, 0.5)"  # Preto com 50% de opacidade
        # set_button_icon_with_hover_svg(self.casual_button, resource_path('resources/icons/down_arrow.svg'), "#171717", "#5865F2", icon_size=(24, 24))


        if theme == "dark":
            set_button_icon_with_hover(self.casual_button, 'fa.smile-o', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.formal_button, 'ri.briefcase-line', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.correction_button, 'mdi.magnify-scan', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.concise_button, 'ph.arrows-in-line-vertical-fill', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.rewrite_button, 'ph.pencil-simple', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.resume_button, 'fa5.file-alt', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.synthesis_button, 'mdi6.format-list-bulleted', '#fff', '#fff', (18, 18))
            set_button_icon_with_hover(self.custom_reading_button, 'mdi.book-open-page-variant', '#fff', '#fff', (18, 18))
            # Label de seção - Escrita
            self.section_label_format_text.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    padding-left: 10px;
                    margin-right: 1px; /*  Margem pra não sobrescrever linha na direita */
                }
            """)
            #Label de seção - Leitura
            self.section_label_read_text.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    padding-left: 10px;
                    margin-right: 1px; /*  Margem pra não sobrescrever linha na direita */
                }
            """)
            self.frame.setStyleSheet(f"""
                QFrame#sideMenuFrame {{
                    background-color: #2E2E2E;
                    border-right: 1px solid #666666;
                }}
                QPushButton#formalButton, QPushButton#casualButton, QPushButton#correctButton, QPushButton#rewriteButton, QPushButton#resumeButton, QPushButton#synthesisButton, QPushButton#customReadingButton  {{
                    background-color: transparent;
                    color: white;
                    border-bottom: 1px solid {hover_background};
                    text-align: left;
                    padding-left: 10px;
                    font-family: 'SF Pro Text';
                    font-weight: 600;
                    font-size: 10px;
                    margin-right: 1px;
                    border-radius: 0px;  /* Remover border-radius */
                }}
                QPushButton#formalButton:hover, QPushButton#casualButton:hover, QPushButton#correctButton:hover, QPushButton#rewriteButton:hover, QPushButton#resumeButton:hover, QPushButton#synthesisButton:hover, QPushButton#customReadingButton:hover {{
                    background-color: {hover_background};
                }}
            """)
        else:
            set_button_icon_with_hover(self.casual_button, 'fa.smile-o', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.formal_button, 'ri.briefcase-line', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.correction_button, 'mdi.magnify-scan', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.concise_button, 'ph.arrows-in-line-vertical-fill', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.rewrite_button, 'ph.pencil-simple', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.resume_button, 'fa5.file-alt', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.synthesis_button, 'mdi6.format-list-bulleted', '#171717', '#171717', (18, 18))
            set_button_icon_with_hover(self.custom_reading_button, 'mdi.book-open-page-variant', '#171717', '#171717', (18, 18))
            # Label de seção - Escrita
            self.section_label_format_text.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #171717;
                    padding-left: 10px;
                    margin-right: 1px; /*  Margem pra não sobrescrever linha na direita */
                }
            """)
            #Label de seção - Leitura
            self.section_label_read_text.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #171717;
                    padding-left: 10px;
                    margin-right: 1px; /*  Margem pra não sobrescrever linha na direita */
                }
            """)
            self.frame.setStyleSheet(f"""
                QFrame#sideMenuFrame {{
                    background-color: #ECECEC;
                    border-right: 1px solid #000000;
                }}
                QPushButton#formalButton, QPushButton#casualButton, QPushButton#correctButton, QPushButton#rewriteButton, QPushButton#resumeButton, QPushButton#synthesisButton, QPushButton#customReadingButton{{
                    background-color: transparent;
                    color: black;
                    border-bottom: 1px solid {hover_background};
                    text-align: left;
                    padding-left: 10px;
                    font-family: 'SF Pro Text';
                    font-weight: 600;
                    font-size: 10px;
                    margin-right: 1px;
                    border-radius: 0px;  /* Remover border-radius */
                }}
                QPushButton#formalButton:hover, QPushButton#casualButton:hover, QPushButton#correctButton:hover, QPushButton#rewriteButton:hover, QPushButton#resumeButton:hover, QPushButton#synthesisButton:hover, QPushButton#customReadingButton:hover {{
                    background-color: {hover_background};
                }}
            """)
    #Função para lidar com o clique no botão 'Formal'.
    def format_formal(self):
        """
        Função para lidar com o clique no botão 'Formal'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()
        name = load_name()

        # Desativa os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para formalizar')
            # Ativar os botões novamente
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = f"""
        Você é uma assistente de escrita. Você transforma textos para um tom profissional.
        Por favor, formate o seguinte texto para ser mais formal. Não inclua nenhum outro comentário, apenas o texto formatado.
        """

        # Conteúdo do usuário, que é o texto do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("formal", data, copied_text))

    #Função para lidar com o clique no botão 'Casual'.
    def format_casual(self):
        """
        Função para lidar com o clique no botão 'Casual'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()
        name = load_name()

        # Desativa os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para formatar')
            # Ativar os botões novamente
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = f"""
        Você é uma assistente de escrita. Você transforma textos para um tom casual.
        Por favor, formate o seguinte texto para ser mais casual. Não inclua nenhum outro comentário, apenas o texto formatado.
        """

        # Conteúdo do usuário, que é o texto do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("casual", data, copied_text))

    #Função para lidar com o clique no botão 'Resumir'.   
    def format_resume(self):
        """
        Função para lidar com o clique no botão 'Resumir'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para resumir')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = """
        Você é uma assistente de escrita que resume textos longos. 
        Por favor, resuma o seguinte texto, e se o conteúdo for muito longo, você pode enumerar os itens principais do texto.
        Gere a resposta formatada já com as quebras de linha apropriadas.
        """

        # Conteúdo do usuário, que é o texto copiado do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("resume", data, copied_text))  # Emitir o prompt e o texto copiado separadamente


    #Função para lidar com o clique no botão 'Corrigir'.   
    def format_correction(self):
        """
        Função para lidar com o clique no botão 'Corrigir'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para corrigir')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = """
        Você é uma assistente de escrita que corrige textos. 
        Corrija o texto fornecido, colocando a pontuação correta, corrigindo erros gramaticais e ortográficos, e deixando o texto mais claro e coeso.
        Gere a correção formatada já com as quebras de linha apropriadas.
        """

        # Conteúdo do usuário, que é o texto copiado do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("correction", data, copied_text))  # Emitir o prompt e o texto copiado separadamente

    # Função para lidar com o clique no botão 'Reescrever'.
    def format_rewrite(self):
        """
        Função para lidar com o clique no botão 'Reescrever'.
        Ela solicita ao usuário as instruções e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para reescrever')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Abrir uma caixa de diálogo para obter as instruções do usuário
        custom_placeholder = "Por favor, forneça instruções para reescrever o texto.\nExemplo:\nTorne o texto mais formal e adicione mais detalhes."
        instructions, ok = self.get_user_instructions(custom_placeholder)

        if not ok or not instructions.strip():
            # O usuário cancelou ou não forneceu instruções
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = f"""
        Você é uma assistente de escrita focada em reescrever textos. 
        Use as instruções fornecidas abaixo para reescrever o texto original:
        Instruções: {instructions}
        """

        # Conteúdo do usuário, que é o texto do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("rewrite", data, copied_text))  # Emitir o prompt e o texto copiado separadamente

    #Função para lidar com o clique no botão 'Resumir'.   
    def format_concise(self):
        """
        Função para lidar com o clique no botão 'Conciso'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para tornar conciso')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = """
        Você é uma assistente de escrita que torna textos mais concisos. 
        Sua tarefa é encurtar o texto fornecido, corrigir erros gramaticais e ortográficos, 
        e deixá-lo mais claro e coeso, mantendo o significado original. 
        Gere a resposta formatada já com as quebras de linha apropriadas.
        """

        # Conteúdo do usuário, que é o texto copiado do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("concise", data, copied_text))  # Emitir o prompt e o texto copiado separadamente


    #Função para lidar com o clique no botão 'Resumir'.   
    def format_synthesis(self):
        """
        Função para lidar com o clique no botão 'Síntese'.
        Ela lê o texto do clipboard e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para sintetizar')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define o comportamento da assistente
        system_content = """
        Você é uma assistente de escrita especializada em síntese de textos. 
        Sua tarefa é resumir o texto fornecido em 1 ou 2 frases, mantendo os pontos principais. 
        Gere o resumo formatado já com as quebras de linha apropriadas.
        """

        # Conteúdo do usuário, que é o texto copiado do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("synthesis", data, copied_text))  # Emitir o prompt e o texto copiado separadamente

    # Função para lidar com o clique no botão 'Leitura Personalizada'.
    def format_custom_reading(self):
        """
        Função para lidar com o clique no botão 'Leitura Personalizada'.
        Ela solicita ao usuário instruções de leitura e emite um sinal para o MainWindow processar.
        """
        # Ler o texto do clipboard
        clipboard = QApplication.clipboard()
        copied_text = clipboard.text().strip()

        # Desativar os botões
        self.deactivate_buttons()

        if not copied_text:
            # Emitir um sinal para mostrar uma mensagem de erro
            show_custom_message('Alerta', 'Nenhum texto encontrado no clipboard para leitura personalizada')
            # Reativar os botões
            self.reactivate_buttons()
            return

        # Abrir uma caixa de diálogo para obter as instruções do usuário
        custom_placeholder = "Por favor, forneça instruções para a leitura personalizada do texto.\nExemplo:\nAnalise o texto e destaque os pontos principais."
        instructions, ok = self.get_user_instructions(custom_placeholder)

        if not ok or not instructions.strip():
            # O usuário cancelou ou não forneceu instruções
            self.reactivate_buttons()
            return

        # Conteúdo do sistema que define como o assistente deve se comportar
        system_content = f"""
        Você é uma assistente de leitura focada em interpretar textos com base nas instruções fornecidas.
        Use as instruções a seguir para interpretar o texto original.
        Instruções: {instructions}
        """

        # Conteúdo do usuário, que é o texto copiado do clipboard
        user_content = copied_text

        # Preparar os dados para enviar, usando o novo formato
        data = {
            "system_content": system_content,
            "user_content": user_content
        }

        # Emitir o sinal com o prompt no novo formato
        self.sidemenu_action_triggered.emit(("custom_reading", data, copied_text))  # Emitir o prompt e o texto copiado separadamente

   
    #Reativa os botoes
    def reactivate_buttons(self):
        self.formal_button.setEnabled(True)
        self.casual_button.setEnabled(True)
        self.concise_button.setEnabled(True)
        self.correction_button.setEnabled(True)
        self.rewrite_button.setEnabled(True)
        self.resume_button.setEnabled(True)
        self.synthesis_button.setEnabled(True)
        self.custom_reading_button.setEnabled(True)
    #Desativa os botoes
    def deactivate_buttons(self):
        self.formal_button.setEnabled(False)
        self.casual_button.setEnabled(False)
        self.concise_button.setEnabled(False)
        self.correction_button.setEnabled(False)
        self.rewrite_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.synthesis_button.setEnabled(False)
        self.custom_reading_button.setEnabled(False)

    #Modal para obter instruções do usuário
    def get_user_instructions(self,custom_msg=None):
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
        text_edit.setPlaceholderText(custom_msg)
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

    #Debug - deletar posteriormente
    def open_help(self):
        # Exibir uma mensagem de ajuda no chat da janela principal
        if hasattr(self.main_window, 'chat_layout'):
            user_bubble = ChatBubble("Esta é a seção de ajuda.", sender='assistant')
            self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)

            # Chamar a função de autoscroll da janela principal para debug
            self.main_window.autoscroll_chat()
        else:
            print("Erro: 'MainWindow' não possui o layout de chat.")
    #Debug - deletar posteriormente
    def open_help2(self):
        # Exibir uma mensagem de ajuda no chat da janela principal
        if hasattr(self.main_window, 'chat_layout'):
            user_bubble = ChatBubble("Esta é a seção de ajuda com mensagem de usuario.", sender='user')
            self.main_window.chat_layout.insertWidget(self.main_window.chat_layout.count() - 1, user_bubble)

            # Chamar a função de autoscroll da janela principal para debug
            self.main_window.autoscroll_chat()
        else:
            print("Erro: 'MainWindow' não possui o layout de chat.")

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()  # Garantir que a janela fique acima

