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
from datetime import date, datetime
from decimal import Decimal

from flask import Flask, jsonify, request, send_from_directory
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from config import Config
from db import buscar_um
from routes.chat import chat_bp
from routes.contatos import contatos_bp
from routes.imoveis import imoveis_bp

# Caminho absoluto da pasta do front-end (independente de onde o Python roda).
# O Flask entrega o front-end da mesma origem da API (sem CORS em produção).
# Atenção para o deploy: o Blueprint do Render usa rootDir=backend, então o
# autoDeploy só dispara quando o commit toca algo dentro de backend/. Mudanças
# apenas em frontend/ exigem deploy manual ou um commit que também toque aqui.
PASTA_FRONTEND = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


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

    @app.after_request
    def sem_cache_de_estaticos(resposta):
        """CSS e JS sempre atualizados após um deploy, sem Ctrl+F5."""
        if request.path.endswith((".css", ".js")):
            resposta.headers["Cache-Control"] = "no-cache, must-revalidate"
        return resposta

    # Valida a configuração antes de subir o servidor.
    Config.validar()

    # Libera apenas as origens configuradas no .env.
    CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

    # Registra os módulos de rotas (cada um em seu arquivo).
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
