import json

from database.delivery_data import INFO_EMPRESA

def consultar_info_empresa() -> str:
    """Retorna informações gerais da pizzaria."""

    return json.dumps(
        INFO_EMPRESA,
        ensure_ascii = False
    )