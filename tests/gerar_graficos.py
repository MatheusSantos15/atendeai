
import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from tests.analisar_resultados import (
    carregar_resultados,
    calcular_metricas,
)


def gerar_graficos(caminho_csv):
    # Carregar os resultados da rodada
    resultados = carregar_resultados(caminho_csv)
    metricas = calcular_metricas(resultados)

    # Pasta onde os gráficos serão salvos
    pasta_saida = (
        Path(__file__).resolve().parent
        / "resultados"
        / "graficos"
    )
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # GRÁFICO 1 - Resultados das execuções
    fig, ax = plt.subplots()

    ax.bar(
        ["Concluídas", "Erros"],
        [metricas["sucessos"], metricas["erros"]]
    )

    ax.set_title("Resultados das execuções")
    ax.set_ylabel("Quantidade de testes")

    fig.tight_layout()
    fig.savefig(
        pasta_saida / "execucoes.png",
        dpi=150
    )
    plt.close(fig)

    # GRÁFICO 2 - Correção das respostas
    corretas = metricas["respostas_corretas"]
    avaliadas = metricas["respostas_avaliadas"]

    fig, ax = plt.subplots()

    ax.bar(
        ["Corretas", "Incorretas"],
        [corretas, avaliadas - corretas]
    )

    ax.set_title("Correção das respostas")
    ax.set_ylabel("Quantidade de testes")

    fig.tight_layout()
    fig.savefig(
        pasta_saida / "correcao_respostas.png",
        dpi=150
    )
    plt.close(fig)

    # GRÁFICO 3 - Tempo por teste concluído
    ids = []
    tempos = []

    for resultado in resultados:
        if (
            resultado["status_execucao"] == "sucesso"
            and resultado["tempo_segundos"]
        ):
            ids.append(resultado["id"])
            tempos.append(
                float(resultado["tempo_segundos"])
            )

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(ids, tempos)
    ax.axhline(
        metricas["tempo_medio"],
        linestyle="--",
        label=f"Média: {metricas['tempo_medio']}s"
    )

    ax.set_title("Tempo de resposta por teste")
    ax.set_xlabel("ID do teste")
    ax.set_ylabel("Tempo (segundos)")
    ax.legend()

    fig.tight_layout()
    fig.savefig(
        pasta_saida / "tempo_resposta.png",
        dpi=150
    )
    plt.close(fig)

    print("Gráficos gerados com sucesso!")
    print(f"Arquivos salvos em: {pasta_saida}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "arquivo",
        type=Path,
        help="Caminho do CSV de resultados"
    )

    args = parser.parse_args()

    gerar_graficos(args.arquivo)
