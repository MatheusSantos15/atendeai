import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq, RateLimitError, APIError

#Carregar veriáveis de ambiente
load_dotenv()

MODELO = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
Você é o AtendeAI, assistente de atendimento de delivery.
Responda em português brasileiro, com clareza e educação.
Seja breve e objetivo.

Não invente preços, cardápios, horários ou status de pedidos.
Se não possuir dados suficientes, explique sua limitação.
"""

#Configuração da Interface
st.set_page_config(
    page_title="AtendeAI",
    page_icon=":robot_face:"
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
        "content": pergunta
    })

    with st.chat_message("user"):
        st.markdown(pergunta)

#Enviar apenas as ultimas 6 mensagens
historico_recente = st.session_state.mensagens[-6:]

with st.chat_message("assistant"):
    try:
        inicio = __import__("time").perf_counter()

        resposta_api = client.chat.completions.create(
            model=MODELO,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                *historico_recente
            ],
            temperature=0.3,
            reasoning_effort="low",
            max_completion_tokens=512
        )

        tempo = __import__("time").perf_counter() - inicio

        resposta = resposta_api.choices[0].message.content

        if not resposta:
            raise ValueError("Resposta vazia do modelo")

        st.markdown(resposta)

        st.session_state.mensagens.append({
            "role": "assistant",
            "content": resposta
        })

        #Medição de utilização
        uso = resposta_api.usage

        if uso:
            st.caption(
                f"Tokens: {uso.total_tokens} | "
                f"Tempo: {tempo:.2f}s"
            )

    except RateLimitError:
        st.warning(
            "Limite de utilização da Groq atingido."
            "Tente novamente mais tarde."
        )

    except (APIError, ValueError):
        st.error(
            "Não foi possível obter uma resposta."
            "Verifique a configuração ou tente novamente"
        )