"""
Segurança da sessão administrativa.

A chave usada para assinar os cookies de sessão fica no banco, na tabela
config_seguranca. Assim todos os processos do gunicorn usam a MESMA chave e
o login não cai quando o Render reinicia o serviço.

Se o banco estiver temporariamente indisponível na subida, usamos uma chave
aleatória só na memória para não derrubar o site. Nesse caso o login pode
ser invalidado na próxima reinicialização — por isso o script
`aplicar_seguranca.py` deve ser executado antes do deploy.
"""

import logging
import os
import secrets

from db import buscar_um

CHAVE_SESSAO = "chave_sessao"
logger = logging.getLogger(__name__)


def carregar_chave_sessao():
    """Retorna a chave da sessão: ambiente > banco > gerada na memória."""
    chave_ambiente = os.getenv("SECRET_KEY", "").strip()
    if chave_ambiente:
        return chave_ambiente

    try:
        registro = buscar_um(
            "SELECT valor FROM config_seguranca WHERE chave = %s", (CHAVE_SESSAO,)
        )
        if registro and registro.get("valor"):
            return registro["valor"]
    except Exception as erro:  # noqa: BLE001 — não queremos derrubar a API
        logger.warning(
            "Não foi possível ler a chave de sessão no banco (%s). "
            "Usando chave temporária em memória.",
            erro.__class__.__name__,
        )

    return secrets.token_hex(32)
