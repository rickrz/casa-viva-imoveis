"""
Casa Viva Imóveis — API Flask

Esta aplicação:
- serve o front-end estático da pasta ../frontend;
- expõe a API em /api/*;
- conversa com o PostgreSQL do Neon;
- aciona a assistente Lia (Gemini) via services/ia_service.py.

Para rodar localmente (Windows), veja o README.md.
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from urllib.parse import quote

from flask import Flask, jsonify, redirect, request, send_from_directory, session
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from auth import auth_bp
from config import Config
from db import buscar_um
from routes.chat import chat_bp
from routes.contatos import contatos_bp
from routes.imoveis import imoveis_bp
from seguranca import carregar_chave_sessao

# Caminho absoluto da pasta do front-end (independente de onde o Python roda).
# O Flask entrega o front-end da mesma origem da API (sem CORS em produção).
# Atenção para o deploy: o Blueprint do Render usa rootDir=backend, então o
# autoDeploy só dispara quando o commit toca algo dentro de backend/. Mudanças
# apenas em frontend/ exigem deploy manual ou um commit que também toque aqui.
PASTA_FRONTEND = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

# Páginas internas: só entram depois de login. O formulário público de
# contato (POST /api/contatos) continua livre — é assim que o site recebe
# mensagens de visitantes que não têm conta no painel.
PAGINAS_PROTEGIDAS = {"/admin.html", "/admin", "/banco.html", "/banco"}
METODOS_DE_GRAVACAO = {"POST", "PUT", "PATCH", "DELETE"}


class ProvedorJSON(DefaultJSONProvider):
    """
    Ensina o Flask a converter tipos que vêm do PostgreSQL:

    - Decimal (NUMERIC) -> número JSON;
    - date/datetime     -> texto ISO 8601 (ex.: "2026-11-13T18:00:00");
    - ensure_ascii=False mantém acentos legíveis nas respostas.
    """

    ensure_ascii = False

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def criar_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__, static_folder=PASTA_FRONTEND, static_url_path="")
    app.json = ProvedorJSON(app)

    # Valida a configuração antes de subir o servidor.
    Config.validar()

    # O Render termina o TLS no proxy; sem isto o Flask acha que é HTTP e
    # não marca o cookie da sessão como Secure.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Chave lida do banco (nunca do Git). Todos os workers usam a mesma.
    app.secret_key = carregar_chave_sessao()
    app.config.update(
        SESSION_COOKIE_NAME="cv_admin_sessao",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )

    @app.after_request
    def cabecalhos_de_seguranca(resposta):
        """CSS/JS sempre frescos; páginas e sessão nunca em cache."""
        caminho = request.path
        if caminho.endswith((".css", ".js")):
            resposta.headers["Cache-Control"] = "no-cache, must-revalidate"
        elif caminho in PAGINAS_PROTEGIDAS or caminho == "/login.html":
            resposta.headers["Cache-Control"] = "no-store"
        elif caminho.startswith("/api/auth/"):
            resposta.headers["Cache-Control"] = "no-store"
        return resposta

    @app.before_request
    def proteger_area_administrativa():
        """
        Porta única de entrada do painel.

        - POST /api/contatos continua público (formulário do site);
        - GET/PUT/DELETE de contatos e gravações de imóveis exigem login;
        - enquanto trocar_senha estiver ativo, só a troca de senha passa.
        """
        # Em HTTPS o cookie é Secure; em HTTP local ele continua funcionando.
        app.config["SESSION_COOKIE_SECURE"] = request.is_secure

        caminho = request.path
        raiz_contatos = caminho.rstrip("/")
        eh_pagina_interna = caminho in PAGINAS_PROTEGIDAS
        eh_api_contatos = (
            raiz_contatos == "/api/contatos" or caminho.startswith("/api/contatos/")
        )
        # O envio de mensagem pelo site é a única operação de contato livre.
        envio_publico = (
            request.method == "POST" and raiz_contatos == "/api/contatos"
        )
        eh_api_imoveis = (
            raiz_contatos == "/api/imoveis" or caminho.startswith("/api/imoveis/")
        )
        grava_imovel = eh_api_imoveis and request.method in METODOS_DE_GRAVACAO

        if not (
            eh_pagina_interna
            or (eh_api_contatos and not envio_publico)
            or grava_imovel
        ):
            return None

        if not session.get("admin_id"):
            if eh_pagina_interna:
                volta = quote(request.full_path.rstrip("?"), safe="")
                return redirect("/login.html?proxima=" + volta)
            return (
                jsonify(
                    {
                        "ok": False,
                        "erro": "Login necessário para acessar esta área.",
                        "login": True,
                    }
                ),
                401,
            )

        if session.get("trocar_senha"):
            if eh_pagina_interna and request.args.get("secao") == "conta":
                return None
            if eh_pagina_interna:
                return redirect("/admin.html?secao=conta")
            return (
                jsonify(
                    {
                        "ok": False,
                        "erro": "Troque a senha temporária antes de continuar.",
                        "trocar_senha": True,
                    }
                ),
                403,
            )
        return None

    # Libera apenas as origens configuradas no .env.
    CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

    # Registra os módulos de rotas (cada um em seu arquivo).
    app.register_blueprint(auth_bp)
    app.register_blueprint(contatos_bp)
    app.register_blueprint(imoveis_bp)
    app.register_blueprint(chat_bp)

    @app.get("/api/health")
    def health():
        """
        Rota de diagnóstico usada no deploy e na apresentação.
        Confirma que a API responde, se o banco está acessível e se a
        chave da Lia foi configurada (sem nunca exibir a chave).
        """
        try:
            buscar_um("SELECT 1 AS ok")
            banco = "conectado"
        except Exception as erro:  # noqa: BLE001 — queremos mostrar o tipo do erro
            app.logger.warning("Banco indisponível: %s", erro)
            banco = f"indisponivel ({erro.__class__.__name__})"

        return jsonify(
            {
                "ok": True,
                "api": "online",
                "banco": banco,
                "ia": "configurada" if Config.GEMINI_API_KEY else "sem chave",
                "modelo_ia": Config.GEMINI_MODEL,
                "modelos_reserva": Config.GEMINI_MODEL_FALLBACKS,
            }
        )

    @app.get("/")
    def inicio():
        """Entrega o index.html do front-end."""
        return send_from_directory(PASTA_FRONTEND, "index.html")

    # -----------------------------------------------------------------
    # Tratamento de erros: JSON para a API, texto simples para o site.
    # -----------------------------------------------------------------
    @app.errorhandler(404)
    def nao_encontrado(_erro):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "erro": "Recurso não encontrado."}), 404
        return "Página não encontrada.", 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_erro):
        return jsonify({"ok": False, "erro": "Método HTTP não permitido."}), 405

    @app.errorhandler(500)
    def erro_interno(erro):
        app.logger.error("Erro interno: %s", erro)
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "erro": "Erro interno do servidor."}), 500
        return "Erro interno do servidor.", 500

    return app


app = criar_app()


if __name__ == "__main__":
    porta = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=porta, debug=Config.FLASK_DEBUG)
