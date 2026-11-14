"""
Rotas de contatos — CRUD completo.

POST   /api/contatos          -> cria um contato (formulário do site)
GET    /api/contatos          -> lista contatos (filtros: status, tipo_interesse)
GET    /api/contatos/<id>     -> busca um contato
PUT    /api/contatos/<id>     -> atualiza um contato (admin)
DELETE /api/contatos/<id>     -> remove um contato (admin)
"""

from flask import Blueprint, jsonify, request
from psycopg2 import errors

from db import buscar_todos, buscar_um, executar
from validacao import STATUS_CONTATO, TIPOS_INTERESSE, validar_contato

contatos_bp = Blueprint("contatos", __name__, url_prefix="/api/contatos")

# Consulta base reaproveitada pelo GET e pelo retorno do POST/PUT.
SQL_LISTAR = """
    SELECT c.id,
           c.nome,
           c.email,
           c.telefone,
           c.tipo_interesse,
           c.imovel_id,
           i.codigo AS imovel_codigo,
           i.titulo AS imovel_titulo,
           c.mensagem,
           c.status,
           c.criado_em
      FROM contatos c
      LEFT JOIN imoveis i ON i.id = c.imovel_id
"""


def _buscar_por_id(contato_id):
    """Busca um contato já com o título do imóvel (JOIN)."""
    return buscar_um(SQL_LISTAR + " WHERE c.id = %s", (contato_id,))


@contatos_bp.get("")
def listar_contatos():
    """Lista os contatos, do mais recente para o mais antigo."""
    filtros, parametros = [], []

    status = request.args.get("status", "").strip().lower()
    if status:
        if status not in STATUS_CONTATO:
            return jsonify({"ok": False, "erro": "Status inválido."}), 400
        filtros.append("c.status = %s")
        parametros.append(status)

    tipo = request.args.get("tipo_interesse", "").strip().lower()
    if tipo:
        if tipo not in TIPOS_INTERESSE:
            return jsonify({"ok": False, "erro": "Tipo de interesse inválido."}), 400
        filtros.append("c.tipo_interesse = %s")
        parametros.append(tipo)

    sql = SQL_LISTAR
    if filtros:
        sql += " WHERE " + " AND ".join(filtros)
    sql += " ORDER BY c.criado_em DESC"

    return jsonify(buscar_todos(sql, tuple(parametros)))


@contatos_bp.get("/<int:contato_id>")
def obter_contato(contato_id):
    contato = _buscar_por_id(contato_id)
    if not contato:
        return jsonify({"ok": False, "erro": "Contato não encontrado."}), 404
    return jsonify(contato)


@contatos_bp.post("")
def criar_contato():
    """
    Recebe o formulário do site.
    Todo contato novo entra com status "novo" (o admin muda depois).
    """
    dados, erros = validar_contato(request.get_json(silent=True))
    if erros:
        return jsonify({"ok": False, "erros": erros}), 400

    # Confere se o imóvel existe antes de gravar (mensagem mais amigável).
    if dados["imovel_id"] is not None:
        existe = buscar_um("SELECT id FROM imoveis WHERE id = %s", (dados["imovel_id"],))
        if not existe:
            return jsonify({"ok": False, "erros": {"imovel_id": "Imóvel inexistente."}}), 400

    try:
        criado = executar(
            """
            INSERT INTO contatos
                (nome, email, telefone, tipo_interesse, imovel_id, mensagem, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'novo')
            RETURNING id
            """,
            (
                dados["nome"],
                dados["email"],
                dados["telefone"],
                dados["tipo_interesse"],
                dados["imovel_id"],
                dados["mensagem"],
            ),
        )
    except errors.ForeignKeyViolation:
        return jsonify({"ok": False, "erro": "O imóvel informado não existe."}), 400

    contato = _buscar_por_id(criado["id"])
    return (
        jsonify(
            {
                "ok": True,
                "mensagem": "Contato registrado com sucesso! Em breve falaremos com você.",
                "contato": contato,
            }
        ),
        201,
        {"Location": f"/api/contatos/{criado['id']}"},
    )


@contatos_bp.put("/<int:contato_id>")
def atualizar_contato(contato_id):
    """Atualiza o contato inteiro (usado pelo painel administrativo)."""
    if not buscar_um("SELECT id FROM contatos WHERE id = %s", (contato_id,)):
        return jsonify({"ok": False, "erro": "Contato não encontrado."}), 404

    dados, erros = validar_contato(request.get_json(silent=True))
    if erros:
        return jsonify({"ok": False, "erros": erros}), 400

    if dados["imovel_id"] is not None:
        existe = buscar_um("SELECT id FROM imoveis WHERE id = %s", (dados["imovel_id"],))
        if not existe:
            return jsonify({"ok": False, "erros": {"imovel_id": "Imóvel inexistente."}}), 400

    try:
        executar(
            """
            UPDATE contatos
               SET nome = %s,
                   email = %s,
                   telefone = %s,
                   tipo_interesse = %s,
                   imovel_id = %s,
                   mensagem = %s,
                   status = %s
             WHERE id = %s
            """,
            (
                dados["nome"],
                dados["email"],
                dados["telefone"],
                dados["tipo_interesse"],
                dados["imovel_id"],
                dados["mensagem"],
                dados["status"],
                contato_id,
            ),
        )
    except errors.ForeignKeyViolation:
        return jsonify({"ok": False, "erro": "O imóvel informado não existe."}), 400

    return jsonify(
        {
            "ok": True,
            "mensagem": "Contato atualizado com sucesso.",
            "contato": _buscar_por_id(contato_id),
        }
    )


@contatos_bp.delete("/<int:contato_id>")
def excluir_contato(contato_id):
    removido = executar(
        "DELETE FROM contatos WHERE id = %s RETURNING id", (contato_id,)
    )
    if not removido:
        return jsonify({"ok": False, "erro": "Contato não encontrado."}), 404
    return "", 204
