# Echo: Corretor de Textos com Inteligência Artificial

O **Echo** é um aplicativo desktop que combina um corretor de textos inteligente e um gerador de resumos. Ele foi desenvolvido em **Python** e utiliza **PyQt5** para a interface gráfica e a **API da OpenAI** para processamento e análise de texto.  

## Principais Funcionalidades

1. **Correção Ortográfica e Gramatical**  
   - Utilize a IA para revisar textos em qualquer aplicativo do seu computador, sem precisar copiar e colar em um editor online.

2. **Geração de Resumos Automáticos**  
   - Selecione qualquer texto e obtenha um resumo conciso em poucos segundos.

3. **Captura de Tela com Análise de Texto**  
   - Defina um atalho de teclado para capturar uma porção da tela; o Echo extrai o texto da imagem e realiza correções ou resumos conforme necessário.

4. **Chat Integrado**  
   - Converse diretamente com a IA na janela principal para tirar dúvidas ou reformular conteúdos.

## Pré-requisitos

- **Python 3.12+** instalado em seu sistema.
- **Pip** (ou outro gerenciador de pacotes compatível) para instalar dependências.

## Instalação

1. **Clone** este repositório (ou baixe o código-fonte em formato ZIP):

   ```bash
   git clone https://github.com/beped/echo.git
   cd echo
   ```
2. Crie e ative um ambiente virtual (opcional, mas recomendado):

    ```
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    ```
    ```
    python -m venv venv
    venv\Scripts\activate      # Windows
    ```
3. Instale as dependências:

    ```
    pip install -r requirements.txt
    ```
## Execução

Para iniciar o aplicativo, execute:

```bash
python main.py
```
   Em sua primeira execucao, o Echo abrira automaticamente a tela de configuração para ser configurada as variáveis necessários para o funcionamento do sistema: Seu nome e Chave API da OpenAI.