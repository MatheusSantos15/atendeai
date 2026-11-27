
import argparse
import csv
import os
import time

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from motor import executar_pergunta
from tests.executar_testes import carregar_casos


# Caminhos do projeto
RAIZ = Path(__file__).resolve().parent.parent
PASTA_RESULTADOS = RAIZ / "tests" / "resultados"

# Configuração da API
load_dotenv(dotenv_path=RAIZ / ".env")
API_KEY = os.environ["GROQ_API_KEY"]

# Colunas dos resultados
CAMPOS = [
    "id",
    "resposta_obtida",
    "ferramenta_executada",
    "resposta_correta",
    "ferramenta_correta",
    "tempo_segundos",
    "tokens",
    "status_execucao",
    "observacoes"
]


def executar_lote(limite=None, intervalo=2.0, ids=None):
    """Executa os casos e registra seus resultados."""

    casos = carregar_casos()

    if ids is not None:
        casos = [
            caso for caso in casos
            if int (caso["id"]) in ids
        ]

    if limite is not None:
        casos = casos[:limite]

    PASTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    # Nome único para cada rodada
    agora = datetime.now().astimezone()
    identificador = agora.strftime("%Y%m%d_%H%M%S_%f")

    arquivo_resultados = (
        PASTA_RESULTADOS / f"rodada_{identificador}.csv"
    )

    total = len(casos)

    print(f"\nIniciando avaliação com {total} testes.")
    print(f"Arquivo: {arquivo_resultados.name}\n")

    # O modo "x" impede sobrescrever um arquivo existente
    with open(
        arquivo_resultados,
        mode="x",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=CAMPOS,
            delimiter=";"
        )

        escritor.writeheader()
        arquivo.flush()

        for indice, caso in enumerate(casos, start=1):

            print(f"[{indice}/{total}] Teste {caso['id']}")

            inicio = time.perf_counter()

            resultado = {
                "id": caso["id"],
                "resposta_obtida": "",
                "ferramenta_executada": "",
                "resposta_correta": "",
                "ferramenta_correta": "",
                "tempo_segundos": "",
                "tokens": "",
                "status_execucao": "",
                "observacoes": ""
            }

            try:
                execucao = executar_pergunta(
                    caso["pergunta"],
                    API_KEY
                )

                ferramentas = execucao["ferramentas"]
                esperada = caso["ferramenta_esperada"]

                lista_esperada = (
                    [] if esperada == "nenhuma"
                    else [esperada]
                )

                ferramenta_correta = int(
                    ferramentas == lista_esperada
                )

                resultado.update({
                    "resposta_obtida": execucao["resposta"],
                    "ferramenta_executada": (
                        ",".join(ferramentas)
                        if ferramentas else "nenhuma"
                    ),
                    "ferramenta_correta": ferramenta_correta,
                    "tokens": execucao["tokens"],
                    "status_execucao": "sucesso"
                })

                print("  Resultado: sucesso")

            except Exception as erro:

                resultado.update({
                    "resposta_correta": 0,
                    "ferramenta_executada": "nao_verificada",
                    "status_execucao": "erro",
                    "observacoes": (
                        f"{type(erro).__name__}: {erro}"
                    )
                })

                print(f"  Resultado: erro - {erro}")

            # Registrar o tempo mesmo quando houve erro
            tempo = time.perf_counter() - inicio

            resultado["tempo_segundos"] = round(
                tempo, 2
            )

            # Salvar imediatamente cada resultado
            escritor.writerow(resultado)
            arquivo.flush()

            print(f"  Tempo: {tempo:.2f}s\n")

            # Intervalo entre testes, exceto após o último
            if indice < total:
                time.sleep(intervalo)

    print("Avaliação finalizada!")
    print(f"Resultados salvos em: {arquivo_resultados}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Quantidade de casos a executar"
    )

    parser.add_argument(
        "--intervalo",
        type=float,
        default=2.0,
        help="Intervalo em segundos entre os testes"
    )

    parser.add_argument(
        "--ids",
        type=int,
        nargs="+",
        default=None,
        help="IDs dos testes que deseja executar"
    )

    argumentos = parser.parse_args()

    if argumentos.limite is not None and argumentos.limite < 1:
        parser.error("--limite deve ser maior que zero")

    if argumentos.intervalo < 0:
        parser.error("--intervalo não pode ser negativo")

    executar_lote(
        limite=argumentos.limite,
        intervalo=argumentos.intervalo,
        ids=argumentos.ids
    )
