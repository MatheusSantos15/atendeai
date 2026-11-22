import json

from database.delivery_data import PEDIDOS


def consultar_pedido(pedido_id) -> str:
    """Consulta status, itens, total e previsão de um pedido pelo número (ex.: 1001)."""
    try:
        numero = int(pedido_id)
    except (TypeError, ValueError):
        return json.dumps({"erro": "Informe o número do pedido (apenas dígitos)."}, ensure_ascii=False)

    pedido = PEDIDOS.get(str(numero)) 

    if not pedido:
        return json.dumps(
            {"encontrado": False, "mensagem": f"Pedido {numero} não encontrado no sistema."},
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "encontrado": True,
            "pedido_id": numero,
            "itens": pedido["itens"],
            "total": pedido["total"],
            "status": pedido["status"],
            "previsao_entrega": pedido["previsao_entrega"],
        },
        ensure_ascii=False,
    )