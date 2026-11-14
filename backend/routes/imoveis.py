"""
Rotas de imóveis — CRUD completo + opções para os filtros do site.

GET    /api/imoveis              -> lista com filtros
GET    /api/imoveis/opcoes       -> tipos, cidades e bairros (para os selects)
GET    /api/imoveis/<id>         -> detalhe
POST   /api/imoveis              -> cadastra (admin)
PUT    /api/imoveis/<id>         -> atualiza (admin)
DELETE /api/imoveis/<id>         -> remove (admin)
"""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from psycopg2 import errors

from db import buscar_todos, buscar_um, executar
from validacao import FINALIDADES, STATUS_IMOVEL, validar_imovel

imoveis_bp = Blueprint("imoveis", __name__, url_prefix="/api/imoveis")

# JOIN para trazer tipo, bairro e cidade juntos (o front não precisa de
# várias requisições para montar o card).
SQL_LISTAR = """
    SELECT i.id,
           i.codigo,
           i.titulo,
           i.descricao,
           i.tipo_id,
           t.nome AS tipo,
           i.bairro_id,
           b.nome AS bairro,
           c.id   AS cidade_id,
           c.nome AS cidade,
           c.uf,
           i.finalidade,
           i.status,
           i.preco,
           i.quartos,
           i.banheiros,
           i.vagas,
           i.area_m2,
           i.imagem_url,
           i.destaque,
           i.criado_em
      FROM imoveis i
      JOIN tipos_imoveis t ON t.id = i.tipo_id
      JOIN bairros b       ON b.id = i.bairro_id
      JOIN cidades c       ON c.id = b.cidade_id
"""


def _buscar_por_id(imovel_id):
    return buscar_um(SQL_LISTAR + " WHERE i.id = %s", (imovel_id,))


@imoveis_bp.get("/opcoes")
def listar_opcoes():
    """
    Alimenta os selects de filtro do site e do painel admin.
    Uma única chamada evita três requisições no front.
    """
    return jsonify(
        {
            "tipos": buscar_todos(
                "SELECT id, nome FROM tipos_imoveis ORDER BY nome"
            ),
            "cidades": buscar_todos(
                "SELECT id, nome, uf FROM cidades ORDER BY nome"
            ),
            "bairros": buscar_todos(
                """
                SELECT b.id, b.nome, b.cidade_id, c.nome AS cidade, c.uf
                  FROM bairros b
                  JOIN cidades c ON c.id = b.cidade_id
                 ORDER BY c.nome, b.nome
                """
            ),
        }
    )


@imoveis_bp.get("")
def listar_imoveis():
    """
    Lista imóveis com filtros opcionais:
    ?finalidade=venda&tipo=Casa&cidade=Campinas&preco_max=800000
    &quartos_min=2&destaque=1&q=piscina&limite=50
    """
    filtros, parametros = [], []

    finalidade = request.args.get("finalidade", "").strip().lower()
    if finalidade:
        if finalidade not in FINALIDADES:
            return jsonify({"ok": False, "erro": "Finalidade inválida."}), 400
        filtros.append("i.finalidade = %s")
        parametros.append(finalidade)

    status = request.args.get("status", "").strip().lower()
    if status:
        if status not in STATUS_IMOVEL:
            return jsonify({"ok": False, "erro": "Status inválido."}), 400
        filtros.append("i.status = %s")
        parametros.append(status)

    tipo = request.args.get("tipo", "").strip()
    if tipo:
        filtros.append("t.nome ILIKE %s")
        parametros.append(tipo)

    cidade = request.args.get("cidade", "").strip()
    if cidade:
        filtros.append("c.nome ILIKE %s")
        parametros.append(cidade)

    bairro = request.args.get("bairro", "").strip()
    if bairro:
        filtros.append("b.nome ILIKE %s")
        parametros.append(bairro)

    preco_max = request.args.get("preco_max", "").strip()
    if preco_max:
        try:
            valor = Decimal(preco_max)
        except InvalidOperation:
            return jsonify({"ok": False, "erro": "preco_max deve ser um número."}), 400
        if not valor.is_finite() or valor <= 0:
            return jsonify({"ok": False, "erro": "preco_max deve ser maior que zero."}), 400
        filtros.append("i.preco <= %s")
        parametros.append(valor)

    quartos_min = request.args.get("quartos_min", "").strip()
    if quartos_min:
        try:
            valor = int(quartos_min)
        except ValueError:
            return jsonify({"ok": False, "erro": "quartos_min deve ser inteiro."}), 400
        if valor < 0:
            return jsonify({"ok": False, "erro": "quartos_min não pode ser negativo."}), 400
        filtros.append("i.quartos >= %s")
        parametros.append(valor)

    if request.args.get("destaque", "").lower() in {"1", "true", "sim"}:
        filtros.append("i.destaque = TRUE")

    busca = request.args.get("q", "").strip()
    if busca:
        filtros.append(
            "(i.titulo ILIKE %s OR i.descricao ILIKE %s "
            "OR b.nome ILIKE %s OR c.nome ILIKE %s)"
        )
        parametros.extend([f"%{busca}%"] * 4)

    limite = request.args.get("limite", "100")
    try:
        limite = int(limite)
    except ValueError:
        return jsonify({"ok": False, "erro": "limite deve ser inteiro."}), 400
    limite = max(1, min(limite, 200))

    sql = SQL_LISTAR
    if filtros:
        sql += " WHERE " + " AND ".join(filtros)
    sql += " ORDER BY i.destaque DESC, i.criado_em DESC LIMIT %s"
    parametros.append(limite)

    return jsonify(buscar_todos(sql, tuple(parametros)))


@imoveis_bp.get("/<int:imovel_id>")
def obter_imovel(imovel_id):
    imovel = _buscar_por_id(imovel_id)
    if not imovel:
        return jsonify({"ok": False, "erro": "Imóvel não encontrado."}), 404
    return jsonify(imovel)


@imoveis_bp.post("")
def criar_imovel():
    dados, erros = validar_imovel(request.get_json(silent=True))
    if erros:
        return jsonify({"ok": False, "erros": erros}), 400

    try:
        criado = executar(
            """
            INSERT INTO imoveis
                (codigo, titulo, descricao, tipo_id, bairro_id, finalidade,
                 status, preco, quartos, banheiros, vagas, area_m2,
                 imagem_url, destaque)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                dados["codigo"],
                dados["titulo"],
                dados["descricao"],
                dados["tipo_id"],
                dados["bairro_id"],
                dados["finalidade"],
                dados["status"],
                dados["preco"],
                dados["quartos"],
                dados["banheiros"],
                dados["vagas"],
                dados["area_m2"],
                dados["imagem_url"],
                dados["destaque"],
            ),
        )
    except errors.UniqueViolation:
        return (
            jsonify(
                {"ok": False, "erros": {"codigo": "Já existe um imóvel com este código."}}
            ),
            409,
        )
    except errors.ForeignKeyViolation:
        return (
            jsonify(
                {"ok": False, "erros": {"tipo_id": "Tipo ou bairro inexistente."}}
            ),
            400,
        )

    return (
        jsonify(
            {
                "ok": True,
                "mensagem": "Imóvel cadastrado com sucesso.",
                "imovel": _buscar_por_id(criado["id"]),
            }
        ),
        201,
        {"Location": f"/api/imoveis/{criado['id']}"},
    )


@imoveis_bp.put("/<int:imovel_id>")
def atualizar_imovel(imovel_id):
    if not buscar_um("SELECT id FROM imoveis WHERE id = %s", (imovel_id,)):
        return jsonify({"ok": False, "erro": "Imóvel não encontrado."}), 404

    dados, erros = validar_imovel(request.get_json(silent=True))
    if erros:
        return jsonify({"ok": False, "erros": erros}), 400

    try:
        executar(
            """
            UPDATE imoveis
               SET codigo = %s,
                   titulo = %s,
                   descricao = %s,
                   tipo_id = %s,
                   bairro_id = %s,
                   finalidade = %s,
                   status = %s,
                   preco = %s,
                   quartos = %s,
                   banheiros = %s,
                   vagas = %s,
                   area_m2 = %s,
                   imagem_url = %s,
                   destaque = %s
             WHERE id = %s
            """,
            (
                dados["codigo"],
                dados["titulo"],
                dados["descricao"],
                dados["tipo_id"],
                dados["bairro_id"],
                dados["finalidade"],
                dados["status"],
                dados["preco"],
                dados["quartos"],
                dados["banheiros"],
                dados["vagas"],
                dados["area_m2"],
                dados["imagem_url"],
                dados["destaque"],
                imovel_id,
            ),
        )
    except errors.UniqueViolation:
        return (
            jsonify(
                {"ok": False, "erros": {"codigo": "Já existe um imóvel com este código."}}
            ),
            409,
        )
    except errors.ForeignKeyViolation:
        return (
            jsonify(
                {"ok": False, "erros": {"tipo_id": "Tipo ou bairro inexistente."}}
            ),
            400,
        )

    return jsonify(
        {
            "ok": True,
            "mensagem": "Imóvel atualizado com sucesso.",
            "imovel": _buscar_por_id(imovel_id),
        }
    )


@imoveis_bp.delete("/<int:imovel_id>")
def excluir_imovel(imovel_id):
    """
    Remove o imóvel. Os contatos ligados a ele NÃO são apagados:
    a FK usa ON DELETE SET NULL, então `imovel_id` vira NULL.
    """
    removido = executar(
        "DELETE FROM imoveis WHERE id = %s RETURNING id", (imovel_id,)
    )
    if not removido:
        return jsonify({"ok": False, "erro": "Imóvel não encontrado."}), 404
    return "", 204
