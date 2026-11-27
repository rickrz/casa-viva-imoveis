"""
Prepara o login administrativo no banco Neon.

O que este script faz:
  1. cria as tabelas `administradores` e `config_seguranca`;
  2. gera e guarda a chave de assinatura da sessão (não aparece no terminal);
  3. cria o usuário inicial `admin` com uma SENHA TEMPORÁRIA hasheada;
     a senha em texto puro aparece uma única vez aqui no terminal.

Uso (dentro de backend/):
    python aplicar_seguranca.py
    python aplicar_seguranca.py --reset-senha admin

Nunca commite a senha exibida nem o arquivo .env.
"""

import argparse
import os
import secrets
import sys
from pathlib import Path

# Permite executar de qualquer pasta: `python backend/aplicar_seguranca.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash  # noqa: E402

from config import Config  # noqa: E402
from db import conexao  # noqa: E402
from seguranca import CHAVE_SESSAO  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SQL_SEGURANCA = RAIZ / "database" / "seguranca.sql"

# Sem letras ambiguas (I, O, l, 1, 0) para facilitar digitar a senha temporária.
ALFABETO_SENHA = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
TAMANHO_SENHA = 16
METODO_HASH = "pbkdf2:sha256:600000"


def gerar_senha_temporaria():
    return "".join(secrets.choice(ALFABETO_SENHA) for _ in range(TAMANHO_SENHA))


def main():
    parser = argparse.ArgumentParser(description="Configura o login do painel administrativo.")
    parser.add_argument(
        "--reset-senha",
        nargs="?",
        const="admin",
        metavar="USUARIO",
        help="gera uma nova senha temporária para o usuário (padrão: admin)",
    )
    args = parser.parse_args()

    Config.validar()

    with conexao() as conn:
        # 1. Estrutura (segura para rodar várias vezes).
        with conn.cursor() as cur:
            cur.execute(SQL_SEGURANCA.read_text(encoding="utf-8"))
        print("Tabelas de segurança verificadas.")

        # 2. Chave da sessão: nunca é sobrescrita, para não deslogar ninguém.
        with conn.cursor() as cur:
            cur.execute("SELECT valor FROM config_seguranca WHERE chave = %s", (CHAVE_SESSAO,))
            registrado = cur.fetchone()
            if not registrado:
                cur.execute(
                    "INSERT INTO config_seguranca (chave, valor) VALUES (%s, %s)",
                    (CHAVE_SESSAO, secrets.token_hex(32)),
                )
                print("Chave de sessão gerada e salva no banco.")
            else:
                print("Chave de sessão já existia (mantida).")

        usuario = (args.reset_senha or "admin").strip().lower()
        if not usuario:
            parser.error("usuário inválido")

        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM administradores WHERE lower(usuario) = %s", (usuario,)
            )
            existente = cur.fetchone()

        if existente and not args.reset_senha:
            print(
                "Usuário '%s' já existe; a senha atual foi mantida. "
                "Use --reset-senha se precisar de uma nova senha temporária." % usuario
            )
            return

        senha = gerar_senha_temporaria()
        senha_hash = generate_password_hash(senha, method=METODO_HASH)

        with conn.cursor() as cur:
            if existente:
                cur.execute(
                    """
                    UPDATE administradores
                       SET senha_hash = %s,
                           trocar_senha = TRUE,
                           ativo = TRUE,
                           tentativas_falhas = 0,
                           bloqueado_ate = NULL
                     WHERE id = %s
                    """,
                    (senha_hash, existente["id"]),
                )
                acao = "Senha temporária renovada"
            else:
                cur.execute(
                    """
                    INSERT INTO administradores (usuario, nome, senha_hash, trocar_senha)
                    VALUES (%s, %s, %s, TRUE)
                    """,
                    (usuario, "Administrador Casa Viva", senha_hash),
                )
                acao = "Usuário criado"

        print("\n" + "=" * 56)
        print(acao + " com sucesso")
        print("Usuário: " + usuario)
        print("Senha temporária: " + senha)
        print("=" * 56)
        print("A troca é obrigatória no primeiro login.")
        print("Esta senha NÃO aparecerá de novo. Não a coloque no Git.\n")


if __name__ == "__main__":
    main()
