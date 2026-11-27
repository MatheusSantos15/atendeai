import json
import time

from groq import Groq

from tools.pedidos import consultar_pedido
from tools.cardapio import consultar_cardapio
from tools.empresa import consultar_info_empresa

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

Quando o cliente perguntar sobre horários de funcionamento, formas de pagamento ou tempo médio de preparo, utilize a ferramenta consultar_info_empresa.
Responda utilizando as informações retornadas, sem inventar dados não cadastrados.
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
                "Consulta produtos, preços e disponibilidade no cardápio da pizzaria. Pode pesquisar um produto pelo nome ou retornar o cardápio completo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "produto": {
                        "type": "string",
                        "description": (
                            "Nome ou parte do nome do produto. Use uma string vazia para consultar todo o cardápio."
                        ),
                    }
                },
                "required": ["produto"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_info_empresa",
            "description": (
                "Consulta informações gerais da Pizzaria Pirituba, incluindo horários de funcionamento, formas de pagamento e tempo médio de preparo."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },

        },
    },
]

FUNCOES = {
    "consultar_pedido": consultar_pedido,
    "consultar_cardapio": consultar_cardapio,
    "consultar_info_empresa": consultar_info_empresa,
}


def executar_pergunta(pergunta, api_key):
    """Executa uma pergunta utilizando o LLM e as ferramentas."""

    client = Groq(api_key=api_key, max_retries=0)

    mensagens_api = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pergunta},
    ]

    ferramentas_executadas = []
    uso_total = 0
    resposta = None

    inicio = time.perf_counter()

    # Mesmo fluxo que já utilizamos no app.py
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
        print(
            f"[DEBUG] Rodada {rodada + 1} | "
            f"Finalização: {resposta_api.choices[0].finish_reason} | "
            f"Tools: {len(mensagem.tool_calls or [])}"
        )

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
                argumentos = json.loads(
                    tc.function.arguments or "{}"
                )

                resultado = FUNCOES[tc.function.name](**argumentos)

                ferramentas_executadas.append(tc.function.name)

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
        raise ValueError(
            "Resposta vazia do modelo após o loop de ferramentas"
        )

    return {
        "resposta": resposta,
        "ferramentas": ferramentas_executadas,
        "tempo_segundos": round(tempo, 2),
        "tokens": uso_total,
    }
