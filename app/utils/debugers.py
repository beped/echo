# app/utils/debuggers.py

#Funcao debug que imprime todas as mensagens da lista
def debug_chat(self):
    """
    Imprime o histórico da conversa formatado, incluindo o número de cada mensagem.
    """
    with self.conversation_lock:
        for index, message in enumerate(self.conversation_history, start=1):
            role = message.get('role', '')
            content = message.get('content', '')
            if role == 'user':
                # O conteúdo pode ser uma lista de itens (ex.: texto, imagem)
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif item.get('type') == 'image_url':
                            text_parts.append("[Imagem]")
                        # Adicione outros tipos aqui, se necessário
                    message_text = ' '.join(text_parts)
                else:
                    # Se o conteúdo for uma string, usamos diretamente
                    message_text = str(content)
                print(f"{index}. Usuário: {message_text}")
            elif role == 'assistant':
                # O conteúdo é uma string
                print(f"{index}. Assistente: {content}")
            else:
                # Caso haja outros roles
                print(f"{index}. {role.capitalize()}: {content}")

                
#Funcao que recebe as mensagens que voltam de get_messages_to_send e imprime na tela
def debug_conversation(messages):
    """
    Imprime a conversa formatada, incluindo o número de cada mensagem, a partir da lista de mensagens fornecida.
    """
    for index, message in enumerate(messages, start=1):
        role = message.get('role', '')
        content = message.get('content', '')
        if role == 'user':
            # O conteúdo pode ser uma lista de itens (ex.: texto, imagem)
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'image_url':
                        text_parts.append("[Imagem]")
                    # Adicione outros tipos aqui, se necessário
                message_text = ' '.join(text_parts)
            else:
                # Se o conteúdo for uma string, usamos diretamente
                message_text = str(content)
            print(f"{index}. Usuário: {message_text}")
        elif role == 'assistant':
            # O conteúdo é uma string
            print(f"{index}. Assistente: {content}")
        else:
            # Caso haja outros roles
            print(f"{index}. {role.capitalize()}: {content}")

def debug_print_payload_messages(payload):
    messages = payload.get('messages', [])
    message_number = 1
    for idx, message in enumerate(messages):
        role = message.get('role', '')
        content = message.get('content', '')
        if role == 'system':
            print(f"System: {content}")
        else:
            print(f"{message_number} - {role.capitalize()}: {content}")
            # Incrementar o número apenas após um par de mensagens usuário/assistente
            if role == 'assistant':
                message_number += 1

