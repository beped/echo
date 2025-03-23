# app/utils/api_calls.py

import requests
import threading
from app.widgets.chat_bubble import ChatBubble
from app.utils.settings import load_api_key, get_messages_to_send
from app.utils.debugers import debug_conversation, debug_print_payload_messages



def sidemenu_action(window, data):
    """
    Recebe os dados do botão clicado no menu lateral e emite um sinal para o processamento.
    """
    action, prompt, copied_text = data  # Separar o prompt completo e o texto copiado
    if action == 'casual':
        send_casual_prompt(window, (prompt, copied_text))
    if action == 'formal':
        send_formal_prompt(window, (prompt, copied_text))
    if action == 'correction':
        send_correction_prompt(window, (prompt, copied_text))
    if action == 'concise':
        send_concise_prompt(window, (prompt, copied_text))
    if action == 'rewrite':
        send_rewrite_prompt(window, (prompt, copied_text))
    if action == 'resume':
        send_resume_prompt(window, (prompt, copied_text))
    if action == 'synthesis':
        send_synthesis_prompt(window, (prompt, copied_text))
    if action == 'custom_reading':
        send_synthesis_prompt(window, (prompt, copied_text))


#Formata o texto casual para ser enviado para a API 
def send_casual_prompt(window, data):
    """
    Envia o prompt completo para formalização e imprime apenas o texto que será formalizado.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado
    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Formando texto casual:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API


#Formata o texto formal para ser enviado para a API
def send_formal_prompt(window, data):
    """
    Envia o prompt completo para formalização e imprime apenas o texto que será formalizado.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Formalizando Texto:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API

#Formata o texto casual para ser enviado para a API 
def send_correction_prompt(window, data):
    """
    Envia o prompt completo para correção e imprime apenas o texto que será corrigido.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Corrigindo texto:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API

#Formata o texto casual para ser enviado para a API 
def send_concise_prompt(window, data):
    """
    Envia o prompt completo para tornar mais conciso.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Tornando texto conciso:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API

#Formata o texto casual para ser enviado para a API 
def send_rewrite_prompt(window, data):
    """
    Envia o prompt completo para tornar mais conciso.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Formatando o texto com as instruções:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API


#Formata o texto de resumo para ser enviado para a API
def send_resume_prompt(window, data):
    """
    Envia o prompt completo para ser resumido e imprime apenas o texto que será formalizado.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Resumindo Texto:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API

#Formata o texto de resumo para ser enviado para a API
def send_synthesis_prompt(window, data):
    """
    Envia o prompt completo para ser resumido e imprime apenas o texto que será formalizado.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Resumindo texto:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API

#Formata o texto de resumo com instrucoes para ser enviado para a API
def send_synthesis_prompt(window, data):
    """
    Envia o prompt completo para ser resumido e imprime apenas o texto que será formalizado.
    """
    prompt, copied_text = data  # Separar o prompt completo e o texto copiado

    # Criar a bolha de chat com a indicação do início da formalização
    user_bubble = ChatBubble(f"Resumindo texto com instruções:\n\n {copied_text}", sender='user')  # Exibir apenas o texto copiado
    window.chat_layout.insertWidget(window.chat_layout.count() - 1, user_bubble)
    window.autoscroll_chat()
    window.is_to_copy = True
    # Adicionar o prompt completo ao histórico como mensagem do usuário
    with window.conversation_lock:
        window.conversation_history.append({"role": "user", "content": prompt["user_content"]})
    threading.Thread(target=process_prompt, args=(window, prompt), daemon=True).start()  # Enviar o prompt completo para a API


def process_prompt(window, data):
    """
    Processa o envio do prompt para a API do ChatGPT, incluindo a mensagem do 'system'.
    """
    window.api_key = load_api_key()
    if not window.api_key:
        window.response_received.emit("Erro: Chave da API não está configurada.")
        return

    # Extrair os conteúdos do sistema e do usuário
    system_content = data.get("system_content")
    user_content = data.get("user_content")

    try:
        # Construir as mensagens para a API, incluindo a mensagem 'system'
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 300
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {window.api_key}"
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response_json = response.json()

        if response.status_code != 200:
            error_message = response_json.get('error', {}).get('message', 'Erro desconhecido')
            answer = f"Erro ao consultar a API: {error_message}"
        else:
            answer = response_json['choices'][0]['message']['content']
            # Adicionar a resposta do assistente ao histórico da conversa
            with window.conversation_lock:
                window.conversation_history.append({"role": "assistant", "content": answer})

    except Exception as e:
        answer = f"Erro ao consultar a API: {e}"

    window.response_received.emit(answer)

#Chamada da api para a sidebar e para o chat
def process_question(window, question):
    """
    Processa a pergunta enviada pelo usuário, incluindo o tratamento de imagens e o histórico da conversa.
    """
    window.api_key = load_api_key()
    if not window.api_key:
        # Emitir sinal para mostrar mensagem de erro na thread principal
        window.response_received.emit("Erro: Chave da API não está configurada.")
        window.send_button.setEnabled(True)
        return

    try:
        # Construir o conteúdo da mensagem do usuário
        content_list = []

        if question:
            content_list.append({
                "type": "text",
                "text": question
            })

        # Verificar se há uma imagem capturada
        if hasattr(window, 'image_data_base64'):
            base64_image = window.image_data_base64
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
            # Limpar a imagem após o envio
            del window.image_data_base64
            del window.captured_image

        if not content_list:
            answer = "Nenhuma mensagem ou imagem para enviar."
            # Emitir o sinal com a resposta
            window.response_received.emit(answer)
            return

        # Adicionar a mensagem do usuário ao histórico da conversa
        with window.conversation_lock:
            window.conversation_history.append({
                "role": "user",
                "content": content_list  # 'content' pode incluir texto e imagens
            })

        # Obter as mensagens a serem enviadas
        messages = get_messages_to_send(window)

        # Construir o payload para a API
        payload = {
            "model": "gpt-4o-mini",  # Certifique-se de que o modelo está correto
            "messages": messages,
            "max_tokens": 300
        }

        # Construir os headers da requisição
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {window.api_key}"
        }

        # Enviar a requisição para a API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        #debug
        # print("Payload: ", payload)
        response_json = response.json()

        if response.status_code != 200:
            # Obter a mensagem de erro da resposta
            error_message = response_json.get('error', {}).get('message', 'Erro desconhecido')
            answer = f"Erro ao consultar a API: {error_message}"
        else:
            # Obter a resposta do assistente
            answer = response_json['choices'][0]['message']['content']

            # Adicionar a resposta do assistente ao histórico da conversa
            with window.conversation_lock:
                window.conversation_history.append({
                    "role": "assistant",
                    "content": answer  # A resposta do assistente é uma string
                })


    except Exception as e:
        answer = f"Erro ao consultar a API: {e}"

    #Debug - print do historico de conversas
    # debug_conversation(window.conversation_history)
    # Emitir o sinal com a resposta para atualizar a interface
    window.response_received.emit(answer)


#definicoes da floating widget
def floating_widget_action(window, data):
    """
    Recebe os dados do botão clicado no floating widget e processa a requisição.
    """
    action, prompt, copied_text = data
    if action in ['casual', 'professional', 'concise', 'review', 'rewrite', 'keypoints', 'summarize']:
        threading.Thread(target=process_prompt_floating_widget, args=(window, prompt), daemon=True).start()
    else:
        print(f"Ação '{action}' não está implementada.")

def process_prompt_floating_widget(window, prompt_data):
    """
    Envia o prompt para a API do ChatGPT e emite a resposta através de sinais.
    """
    window.api_key = load_api_key()
    if not window.api_key:
        window.response_received.emit("Erro: Chave da API não está configurada.")
        return

    try:
        # Extrair os conteúdos do sistema e do usuário
        system_content = prompt_data.get("system_content")
        user_content = prompt_data.get("user_content")

        # Adicionar a mensagem do usuário ao histórico
        with window.conversation_lock:
            window.conversation_history.append({
                "role": "user",
                "content": user_content
            })

        # Configurar o payload para a API com mensagens 'system' e 'user'
        payload = {
            "model": "gpt-4o-mini",  # Certifique-se de que o modelo está correto
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 300
        }
        #debug
        # print("Payload: ", payload)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {window.api_key}"
        }

        # Enviar a requisição para a API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        #Debug
        # debug_print_payload_messages(payload)


        response_json = response.json()

        if response.status_code != 200:
            # Obter a mensagem de erro da resposta
            error_message = response_json.get('error', {}).get('message', 'Erro desconhecido')
            answer = f"Erro ao consultar a API: {error_message}"
        else:
            # Obter a resposta do assistente
            answer = response_json['choices'][0]['message']['content']

            # Adicionar a resposta do assistente ao histórico da conversa
            with window.conversation_lock:
                window.conversation_history.append({
                    "role": "assistant",
                    "content": answer
                })

    except Exception as e:
        answer = f"Erro ao consultar a API: {e}"

    # Emitir o sinal com a resposta para atualizar a interface
    window.response_received.emit(answer)

