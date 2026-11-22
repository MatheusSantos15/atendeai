import json

from database.delivery_data import CARDAPIO

def consultar_cardapio(produto: str = "") -> str:
    """Consulta produtos cadastrados no cardápio."""
    
    #Padronizar o texto recebido
    busca = produto.strip().lower()

    #Procurar produtos que contenham o texto informado
    resultados = [
        item for item in CARDAPIO
        if busca in item["nome"].lower()
    ]

    #Tratar produtos não encontrados
    if not resultados:
        return json.dumps(
            {
                "encontrado": False,
                "mensagem": "Nenhum produto encontrado."
            },
            ensure_ascii = False
        )

    #Retornar os produtos encontrados
    return json.dumps(
        {
            "encontrado": True,
            "quantidade": len(resultados),
            "produtos": resultados
        },
        ensure_ascii = False
    )