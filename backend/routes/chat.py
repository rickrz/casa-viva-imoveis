"""
Rota do assistente virtual (Lia).

POST /api/chat
Corpo esperado:
{
  "mensagem": "Vocês têm casa para alugar em Campinas?",
  "historico": [
    {"papel": "user",  "texto": "Oi"},
    {"papel": "model", "texto": "Olá! Como posso ajudar?"}
  ]
}

A rota só valida e delega: persona, carteira do banco e chamada ao Gemini
ficam em services/ia_service.py. Assim o front-end não precisa mudar quando
a IA é trocada ou ajustada.
"""

from flask import Blueprint, jsonify, request

from services import ia_service

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

TAMANHO_MAXIMO_MENSAGEM = 1000
TAMANHO_MAXIMO_HISTORICO = 50  # itens; a IA usa apenas os 8 mais recentes


@chat_bp.post("")
def conversar():
    dados = request.get_json(silent=True) or {}
    mensagem = str(dados.get("mensagem", "")).strip()

    if not mensagem:
        return jsonify({"ok": False, "erro": "Envie o campo 'mensagem'."}), 400
    if len(mensagem) > TAMANHO_MAXIMO_MENSAGEM:
        return (
            jsonify(
                {
                    "ok": False,
                    "erro": f"Mensagem muito longa (máximo {TAMANHO_MAXIMO_MENSAGEM} caracteres).",
                }
            ),
            400,
        )

    historico = dados.get("historico") or []
    if not isinstance(historico, list):
        return jsonify({"ok": False, "erro": "O campo 'historico' deve ser uma lista."}), 400
    if len(historico) > TAMANHO_MAXIMO_HISTORICO:
        return (
            jsonify(
                {
                    "ok": False,
                    "erro": f"Histórico muito longo (máximo {TAMANHO_MAXIMO_HISTORICO} mensagens).",
                }
            ),
            400,
        )

    resposta, codigo = ia_service.responder(mensagem, historico)
    return jsonify(resposta), codigo
