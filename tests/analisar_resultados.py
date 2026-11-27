import argparse
import csv
from pathlib import Path

def carregar_resultados(caminho):
    """Carrega os resultados de uma rodada experimental."""

    with open(
        caminho,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:
        leitor = csv.DictReader(
            arquivo,
            delimiter=";"
        )
        return list (leitor)

def calcular_metricas(resultados):
    """Calcula as métricas de avaliação do AtendeAI."""

    total = len(resultados)

    if total == 0:
        raise ValueError("O arquivo não possui resultados.")

    #Separar execuções concluídas
    sucessos = [
        r for r in resultados
        if r["status_execucao"] == "sucesso"
    ]

    erros = [
        r for r in resultados
        if r["status_execucao"] == "erro"
    ]

    #Avaliar respostas classificadas
    respostas_avaliadas = [
        r for r in resultados
        if r["resposta_correta"] in ("0", "1")
    ]

    respostas_corretas = sum(
        int(r["resposta_correta"])
        for r in respostas_avaliadas
    )

    #Avaliar ferramentas verificáveis
    
    ferramentas_avaliadas = [
        r for r in resultados
        if r["ferramenta_correta"] in ("0", "1")
    ]

    ferramentas_corretas = sum(
        int(r["ferramenta_correta"])
        for r in ferramentas_avaliadas
    )

    #Considerar tempo apoenas de respostas concluídas

    tempos = [
        float(r["tempo_segundos"])
        for r in sucessos
        if r["tempo_segundos"]
    ]

    tokens = [
        int(r["tokens"])
        for r in sucessos
        if r["tokens"]
    ]

    def percentual(parte, total):
        if total == 0:
            return None
        return round(parte / total *100, 2)

    def media(valores):
        if not valores:
            return None
        return round(sum(valores) / len(valores), 2)

    return {
        "total": total,
        "sucessos": len(sucessos),
        "erros": len(erros),

        "taxa_conclusao": percentual(
            len(sucessos), total
        ),

        "respostas_avaliadas": len(respostas_avaliadas),
        "respostas_corretas": respostas_corretas,
        "taxa_respostas_corretas": percentual(
            respostas_corretas, len(respostas_avaliadas)
        ),

        "ferramentas_avaliadas": len(ferramentas_avaliadas),
        "ferramentas_corretas": ferramentas_corretas,
        "taxa_ferramentas_corretas": percentual(
            ferramentas_corretas, len(ferramentas_avaliadas)
        ),

        "tempo_medio": media(tempos),
        "tokens_medios": media(tokens),
        "tokens_totais": sum(tokens)
    }


def exibir_relatorio(metricas):
    """Exibe os indicadores calculados no terminal."""

    def formatar(valor, sufixo=""):
        if valor is None:
            return "Não disponível"
        return f"{valor}{sufixo}"

    print("\n" + "=" * 50)
    print("RELATÓRIO DE AVALIAÇÃO - ATENDEAI")
    print("=" * 50)

    print(f"Total de testes: {metricas['total']}")
    print(f"Execuções concluídas: {metricas['sucessos']}")
    print(f"Erros: {metricas['erros']}")

    print(
        "Taxa de conclusão: "
        + formatar(metricas["taxa_conclusao"], "%")
    )

    print("\n--- QUALIDADE DAS RESPOSTAS ---")
    print(
        f"Respostas corretas: "
        f"{metricas['respostas_corretas']}/"
        f"{metricas['respostas_avaliadas']} avaliadas"
    )

    print(
        "Taxa de respostas corretas: "
        + formatar(metricas["taxa_respostas_corretas"], "%")
    )

    print("\n--- SELEÇÃO DE FERRAMENTAS ---")
    print(
        f"Seleções corretas: "
        f"{metricas['ferramentas_corretas']}/"
        f"{metricas['ferramentas_avaliadas']} avaliadas"
    )

    print(
        "Taxa de seleção correta: "
        + formatar(metricas["taxa_ferramentas_corretas"], "%")
    )

    print("\n--- DESEMPENHO ---")
    print(
        "Tempo médio (sucessos): "
        + formatar(metricas["tempo_medio"], " s")
    )

    print(
        "Tokens médios (sucessos): "
        + formatar(metricas["tokens_medios"])
    )

    print(
        f"Tokens totais registrados: "
        f"{metricas['tokens_totais']}"
    )

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "arquivo",
        type=Path,
        help="Caminho do CSV com os resultados da rodada"
    )

    args = parser.parse_args()

    resultados = carregar_resultados(args.arquivo)
    metricas = calcular_metricas(resultados)

    exibir_relatorio(metricas)


if __name__ == "__main__":
    main()


    