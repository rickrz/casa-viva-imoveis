"""
Configurações centrais do back-end.

REGRA DE OURO: senhas e chaves ficam somente no arquivo `.env`.
Este arquivo apenas LÊ as variáveis — nada de valor secreto no código.

Copie `backend/.env.example` para `backend/.env` e preencha os valores.
"""

import os

from dotenv import load_dotenv

# Carrega o .env que fica na mesma pasta deste arquivo (backend/).
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class Config:
    """Valores de configuração acessados pelo restante da aplicação."""

    # Connection string do Neon (obrigatória).
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

    # Chave do Gemini — usada apenas no back-end, pela assistente Lia.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

    # Modelo do Gemini (pode ser trocado sem mexer no código).
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()

    # Modelos de reserva: se o principal responder 503/429, tentamos o próximo.
    # Ex.: "gemini-3.5-flash-lite,gemini-flash-lite-latest".
    GEMINI_MODEL_FALLBACKS = [
        modelo.strip()
        for modelo in os.getenv(
            "GEMINI_MODEL_FALLBACKS",
            "gemini-3.5-flash-lite,gemini-flash-lite-latest",
        ).split(",")
        if modelo.strip()
    ]

    # Debug ligado/desligado (1 = recarrega automaticamente ao salvar).
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # Origens autorizadas a chamar a API (front local e deploy).
    ALLOWED_ORIGINS = [
        origem.strip()
        for origem in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5000,http://127.0.0.1:5000,"
            "http://localhost:5500,http://127.0.0.1:5500",
        ).split(",")
        if origem.strip()
    ]

    @classmethod
    def validar(cls):
        """
        Falha cedo (com mensagem clara) se faltar configuração essencial.
        É melhor errar ao iniciar do que descobrir no meio da apresentação.
        """
        if not cls.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL não configurada.\n"
                "Copie backend/.env.example para backend/.env e cole a "
                "connection string do Neon."
            )
