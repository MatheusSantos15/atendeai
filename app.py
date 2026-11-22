import json
import os
import time

import streamlit as st
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError

from tools.pedidos import consultar_pedido
from tools.cardapio import consultar_cardapio

#Carregar variáveis de ambiente
load_dotenv()

MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
Você é o AtendeAI, assistente de atendimento da Pizzaria Pirituba.
Responda em português brasileiro, com clareza e educação.
Seja breve e objetivo.

Não invente preços, cardápios, horários ou status de pedidos.
Se não possuir dados suficientes, explique sua limitação.

Sempre que o cliente mencionar um número de pedido (ex.: 1001, 1002, 1003), chame a ferramenta consultar_pedido imediatamente.
Só peça o número do pedido se nenhum número tiver sido informado na conversa.

Quando o cliente perguntar sobre produtos, preços, disponibilidade ou quiser ver o cardápio, utilize a ferramenta consultar_cardapio.
Se o cliente solicitar o cardápio completo, consulte a ferramente com produto vazio.
Utilize os dados retornados pelas ferramentas para responder, sem inventar informações.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_pedido",
            "description": "Consulta status, itens, valor total e previsão de entrega de um pedido pelo número.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pedido_id": {
                        "type": "string",
                        "description": "Número do pedido, apenas dígitos. Exemplo: 1001.",
                    }
                },
                "required": ["pedido_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_cardapio",
            "description": (
                "Consulta produtos, preços e disponibilidade"
                "no cardápio da pizzaria."
                "Pode pesquisar um produto pelo nome ou"
                "retornar o cardápio completo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "produto": {
                        "type": "string",
                        "description": (
                            "Nome ou parte do nome do produto. "
                            "Use uma string vazia para consultar "
                            "todo o cardápio."
                        ),
                    }
                },
                "required": ["produto"],
            },
        },
    },
]

FUNCOES = {
    "consultar_pedido": consultar_pedido,
    "consultar_cardapio": consultar_cardapio,
}

#Configuração da Interface
st.set_page_config(
    page_title="AtendeAI",
    page_icon="🤖",
)

st.title("AtendeAI 🤖")
st.caption("Assistente inteligente para atendimento de delivery")

#Carregar a chave
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Configure a GROQ_API_KEY no arquivo .env")
    st.stop()

client = Groq(api_key=api_key, max_retries=0)

#Inicializar histórico
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

#Botão para limpar conversa
if st.button("Limpar Conversa"):
    st.session_state.mensagens = []
    st.rerun()

#Exibir histórico completo na interface
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

#Campo de entrada
pergunta = st.chat_input("Como posso ajudar?")

if pergunta:
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta,
    })

    with st.chat_message("user"):
        st.markdown(pergunta)

    #Enviar apenas as ultimas 6 mensagens
    historico_recente = st.session_state.mensagens[-6:]

    with st.chat_message("assistant"):
        try:
            inicio = time.perf_counter()

            mensagens_api = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *historico_recente,
            ]

            uso_total = 0
            resposta = None

            # Repete enquanto o modelo pedir ferramentas (máximo 4 rodadas)
            for rodada in range(4):
                resposta_api = client.chat.completions.create(
                    model=MODELO,
                    messages=mensagens_api,
                    tools=TOOLS,
                    temperature=0.3,
                    reasoning_effort="low",
                    max_completion_tokens=1024,
                )

                if resposta_api.usage:
                    uso_total += resposta_api.usage.total_tokens

                mensagem = resposta_api.choices[0].message

                if not mensagem.tool_calls:
                    resposta = mensagem.content
                    break

                mensagens_api.append({
                    "role": "assistant",
                    "content": mensagem.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in mensagem.tool_calls
                    ],
                })

                for tc in mensagem.tool_calls:
                    try:
                        argumentos = json.loads(tc.function.arguments or "{}")
                        resultado = FUNCOES[tc.function.name](**argumentos)
                        print(
                            f"[TOOL] {tc.function.name} | "
                            f"Argumentos: {argumentos}"
                            )
                    except Exception as e:
                        resultado = json.dumps(
                            {"erro": f"Falha ao executar a ferramenta: {e}"},
                            ensure_ascii=False,
                        )

                    mensagens_api.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": resultado,
                    })

            tempo = time.perf_counter() - inicio

            if not resposta:
                raise ValueError("Resposta vazia do modelo após o loop de ferramentas")

            st.markdown(resposta)

            st.session_state.mensagens.append({
                "role": "assistant",
                "content": resposta,
            })

            # Medição de utilização
            if uso_total:
                st.caption(
                    f"Tokens: {uso_total} | "
                    f"Tempo: {tempo:.2f}s"
                )

        except RateLimitError as e:
            st.warning(f"Limite de utilização da Groq atingido: {e}")

        except APIError as e:
            st.error(f"Erro na API da Groq: {e}")

        except ValueError as e:
            st.error(f"Resposta inválida: {e}")