import csv
from pathlib import Path

# Localizar a pasta onde este script está salvo
PASTA_TESTES = Path(__file__).parent

# Caminho do arquivo contendo os casos
ARQUIVO_CASOS = PASTA_TESTES / "casos_teste.csv"


def carregar_casos():
    """Lê os casos de teste cadastrados no CSV."""

    with open(
        ARQUIVO_CASOS,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        leitor = csv.DictReader(arquivo, delimiter=";")
        casos = list(leitor)

    return casos


def main():
    casos = carregar_casos()

    print(f"Total de casos encontrados: {len(casos)}")
    print("-" * 50)

    for caso in casos:
        print(f"Teste {caso['id']}")
        print(f"Pergunta: {caso['pergunta']}")
        print(f"Ferramenta esperada: {caso['ferramenta_esperada']}")
        print("-" * 50)


if __name__ == "__main__":
    main()
