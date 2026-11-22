INFO_EMPRESA = {
    "nome": "Pizzaria Pirituba",
    "horario_funcionamento": {
        "segunda_a_quinta": "18:00 às 23:00",
        "sexta_a_domingo": "18:00 às 00:00",
    },
    "formas_pagamento": ["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"],
    "tempo_medio_preparo": "30 a 45 minutos",
}

CARDAPIO = [
    {
        "id": "101",
        "nome": "Pizza Marguerita",
        "categoria": "Pizzas",
        "descricao": "Molho de tomate, muçarela, rodelas de tomate e manjericão",
        "preco": 44.90,
        "disponivel": True,
    },
    {
        "id": "102",
        "nome": "Pizza Calabresa",
        "categoria": "Pizzas",
        "descricao": "Molho de tomate, muçarela, calabresa fatiada, cebola e orégano",
        "preco": 46.90,
        "disponivel": True,
    },
    {
        "id": "103",
        "nome": "Pizza Portuguesa",
        "categoria": "Pizzas",
        "descricao": "Molho de tomate, muçarela, presunto, ovos, palmito, ervilha e cebola",
        "preco": 51.90,
        "disponivel": True,
    },
    {
        "id": "104",
        "nome": "Pizza Quatro Queijos",
        "categoria": "Pizzas",
        "descricao": "Molho de tomate, muçarela, catupiry, gorgonzola e parmesão ralado",
        "preco": 53.90,
        "disponivel": True,
    },
    {
        "id": "105",
        "nome": "Pizza Frango com Catupiry",
        "categoria": "Pizzas",
        "descricao": "Molho de tomate, muçarela, frango desfiado e catupiry",
        "preco": 49.90,
        "disponivel": True,
    },
    {
        "id": "106",
        "nome": "Coca-Cola Lata 350ml",
        "categoria": "Bebidas",
        "descricao": "Refrigerante de cola em lata de 350ml",
        "preco": 6.50,
        "disponivel": True,
    },
    {
        "id": "107",
        "nome": "Guaraná Antarctica Lata 350ml",
        "categoria": "Bebidas",
        "descricao": "Refrigerante de guaraná em lata de 350ml",
        "preco": 6.00,
        "disponivel": True,
    },
    {
        "id": "108",
        "nome": "Sprite Lata 350ml",
        "categoria": "Bebidas",
        "descricao": "Refrigerante de limão em lata de 350ml",
        "preco": 6.00,
        "disponivel": False,  # exemplo de item fora de estoque
    },
    {
        "id": "109",
        "nome": "Fanta Laranja 2L",
        "categoria": "Bebidas",
        "descricao": "Refrigerante de laranja garrafa de 2 litros",
        "preco": 14.00,
        "disponivel": True,
    },
    {
        "id": "110",
        "nome": "Coca-Cola Zero 2L",
        "categoria": "Bebidas",
        "descricao": "Refrigerante de cola zero açúcar garrafa de 2 litros",
        "preco": 15.00,
        "disponivel": True,
    },
]

PEDIDOS = {
    "1001": {
        "cliente": "Carlos Silva",
        "itens": ["Pizza Marguerita", "Coca-Cola Lata 350ml"],
        "total": 51.40,
        "status": "Em preparo",
        "previsao_entrega": "20:15",
    },
    "1002": {
        "cliente": "Mariana Souza",
        "itens": ["Pizza Calabresa", "Guaraná Antarctica Lata 350ml"],
        "total": 52.90,
        "status": "Saiu para entrega",
        "previsao_entrega": "19:50",
    },
    "1003": {
        "cliente": "João Oliveira",
        "itens": ["Pizza Quatro Queijos"],
        "total": 53.90,
        "status": "Entregue",
        "previsao_entrega": "Entregue às 19:10",
    },
}