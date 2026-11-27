"""
Autenticação do painel administrativo.

Rotas públicas
    POST /api/auth/login    -> valida usuário/senha e cria a sessão
    GET  /api/auth/sessao   -> consulta quem está logado (usado pelo front)

Rotas que exigem sessão
    POST /api/auth/logout   -> encerra a sessão
    POST /api/auth/senha    -> troca a senha (obrigatória no primeiro login)

As senhas nunca são gravadas em texto puro: o banco guarda apenas o hash
PBKDF2-SHA256 gerado por werkzeug.security.
"""

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import buscar_um, executar

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

TENTATIVAS_MAXIMAS = 5
MINUTOS_BLOQUEIO = 15
SENHA_MINIMA = 8
METODO_HASH = "pbkdf2:sha256:600000"


def _agora():
    """datetime com fuso, comparável ao TIMESTAMPTZ do PostgreSQL."""
    return datetime.now(timezone.utc)


def _buscar_usuario(usuario):
    return buscar_um(
        """
        SELECT id, usuario, nome, senha_hash, ativo, trocar_senha,
               tentativas_falhas, bloqueado_ate
          FROM administradores
         WHERE lower(usuario) = lower(%s)
        """,
        (usuario,),
    )


def _erro(mensagem, status):
    return jsonify({"ok": False, "erro": mensagem}), status


@auth_bp.post("/login")
def login():
    """Entra no painel e guarda o id do administrador na sessão."""
    dados = request.get_json(silent=True) or {}
    usuario = str(dados.get("usuario", "")).strip()
    senha = str(dados.get("senha", ""))

    if not usuario or not senha:
        return _erro("Informe usuário e senha.", 400)

    registro = _buscar_usuario(usuario)
    agora = _agora()

    if (
        registro
        and registro["bloqueado_ate"]
        and registro["bloqueado_ate"] > agora
    ):
        restante = int((registro["bloqueado_ate"] - agora).total_seconds() // 60) + 1
        return _erro(
            "Muitas tentativas incorretas. Tente novamente em %d minuto(s)." % restante,
            429,
        )

    senha_valida = bool(registro) and check_password_hash(
        registro["senha_hash"], senha
    )

    if not registro or not registro["ativo"] or not senha_valida:
        if registro and registro["ativo"]:
            tentativas = (registro["tentativas_falhas"] or 0) + 1
            bloqueado_ate = (
                agora + timedelta(minutes=MINUTOS_BLOQUEIO)
                if tentativas >= TENTATIVAS_MAXIMAS
                else None
            )
            executar(
                """
                UPDATE administradores
                   SET tentativas_falhas = %s,
                       bloqueado_ate = %s
                 WHERE id = %s
                """,
                # Depois do bloqueio zeramos a contagem para dar uma nova
                # chance quando o tempo expirar.
                (0 if bloqueado_ate else tentativas, bloqueado_ate, registro["id"]),
            )
            if bloqueado_ate:
                current_app.logger.warning(
                    "Login bloqueado por muitas tentativas para o usuário id=%s",
                    registro["id"],
                )
                return _erro(
                    "Muitas tentativas incorretas. Tente novamente em %d minutos."
                    % MINUTOS_BLOQUEIO,
                    429,
                )

        # Mensagem genérica: não informa se o usuário existe.
        return _erro("Usuário ou senha incorretos.", 401)

    executar(
        """
        UPDATE administradores
           SET tentativas_falhas = 0,
               bloqueado_ate = NULL,
               ultimo_login = %s
         WHERE id = %s
        """,
        (agora, registro["id"]),
    )

    session.clear()
    session.permanent = True
    session["admin_id"] = registro["id"]
    session["admin_usuario"] = registro["usuario"]
    session["trocar_senha"] = bool(registro["trocar_senha"])

    return jsonify(
        {
            "ok": True,
            "usuario": registro["usuario"],
            "nome": registro["nome"],
            "trocar_senha": bool(registro["trocar_senha"]),
        }
    )


@auth_bp.get("/sessao")
def sessao_atual():
    """Diz ao front se existe um administrador logado."""
    if not session.get("admin_id"):
        return jsonify({"autenticado": False, "usuario": None, "trocar_senha": False})

    registro = buscar_um(
        "SELECT usuario, nome, ativo, trocar_senha FROM administradores WHERE id = %s",
        (session.get("admin_id"),),
    )

    if not registro or not registro["ativo"]:
        session.clear()
        return jsonify({"autenticado": False, "usuario": None, "trocar_senha": False})

    # Mantém a sessão atualizada se a senha foi trocada em outra aba.
    session["admin_usuario"] = registro["usuario"]
    session["trocar_senha"] = bool(registro["trocar_senha"])

    return jsonify(
        {
            "autenticado": True,
            "usuario": registro["usuario"],
            "nome": registro["nome"],
            "trocar_senha": bool(registro["trocar_senha"]),
        }
    )


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True, "mensagem": "Sessão encerrada."})


@auth_bp.post("/senha")
def trocar_senha():
    """Troca a senha do administrador logado e libera o painel."""
    if not session.get("admin_id"):
        return _erro("Faça login para trocar a senha.", 401)

    dados = request.get_json(silent=True) or {}
    atual = str(dados.get("senha_atual", ""))
    nova = str(dados.get("senha_nova", ""))

    if not atual or not nova:
        return _erro("Informe a senha atual e a nova senha.", 400)
    if len(nova) < SENHA_MINIMA:
        return _erro("A nova senha deve ter pelo menos %d caracteres." % SENHA_MINIMA, 400)

    registro = buscar_um(
        "SELECT senha_hash FROM administradores WHERE id = %s",
        (session.get("admin_id"),),
    )
    if not registro or not check_password_hash(registro["senha_hash"], atual):
        return _erro("Senha atual incorreta.", 401)
    if check_password_hash(registro["senha_hash"], nova):
        return _erro("A nova senha deve ser diferente da atual.", 400)

    executar(
        """
        UPDATE administradores
           SET senha_hash = %s,
               trocar_senha = FALSE,
               tentativas_falhas = 0,
               bloqueado_ate = NULL
         WHERE id = %s
        """,
        (generate_password_hash(nova, method=METODO_HASH), session.get("admin_id")),
    )

    session["trocar_senha"] = False
    return jsonify({"ok": True, "mensagem": "Senha alterada com sucesso."})
