"""
Aplica o banco da Casa Viva no Neon (ou em qualquer PostgreSQL).

O que este script faz:
1. lê a DATABASE_URL do arquivo backend/.env;
2. executa database/schema.sql (recria as tabelas);
3. executa database/seed.sql (carrega os dados de exemplo);
4. confere as contagens e mostra um imóvel de amostra.

Por que existe? Para não depender do SQL Editor do site do Neon: com um
comando só, o banco fica idêntico ao do repositório — útil para a equipe,
para o deploy e para a apresentação.

Uso (Windows, dentro da pasta backend):
    .venv\\Scripts\\python.exe aplicar_banco.py
    .venv\\Scripts\\python.exe aplicar_banco.py --sim       # sem confirmação
    .venv\\Scripts\\python.exe aplicar_banco.py --verificar # só consulta

ATENÇÃO: o schema.sql começa com DROP TABLE. Rodar o script APAGA os dados
atuais do banco configurado. Use --verificar quando quiser apenas checar.
"""

import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config

PASTA_PROJETO = Path(__file__).resolve().parent.parent
ARQUIVO_SCHEMA = PASTA_PROJETO / "database" / "schema.sql"
ARQUIVO_SEED = PASTA_PROJETO / "database" / "seed.sql"

TABELAS = ("cidades", "bairros", "tipos_imoveis", "imoveis", "contatos")


def mascarar(url):
    """Esconde a senha antes de imprimir a URL no terminal/log."""
    if not url:
        return "(vazia)"
    if "@" not in url:
        return url
    inicio, resto = url.split("@", 1)
    if ":" not in inicio:
        return url
    return inicio.split(":", 1)[0] + ":***@" + resto


def ler_sql(caminho):
    """Lê um arquivo .sql em UTF-8 (o Neon aceita acentos normalmente)."""
    if not caminho.exists():
        raise SystemExit(f"Arquivo não encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8")


def conectar():
    if not Config.DATABASE_URL:
        raise SystemExit(
            "DATABASE_URL não configurada.\n"
            "Crie backend/.env a partir de backend/.env.example e cole a "
            "connection string do Neon (com ?sslmode=require)."
        )

    print(f"Conectando em {mascarar(Config.DATABASE_URL)} ...")
    try:
        conn = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
    except psycopg2.OperationalError as erro:
        raise SystemExit(f"Não foi possível conectar: {erro}") from erro

    print("Conexão OK.")
    return conn


def aplicar(conn):
    schema = ler_sql(ARQUIVO_SCHEMA)
    seed = ler_sql(ARQUIVO_SEED)

    with conn.cursor() as cur:
        print("Executando database/schema.sql ...")
        cur.execute(schema)
        conn.commit()

        print("Executando database/seed.sql ...")
        cur.execute(seed)
        conn.commit()

    print("Banco criado e populado.")


def verificar(conn):
    print("\n== Conferência ==")
    with conn.cursor() as cur:
        for tabela in TABELAS:
            cur.execute(f"SELECT COUNT(*) AS total FROM {tabela}")
            total = cur.fetchone()["total"]
            print(f"  {tabela:<15} {total:>3} registro(s)")

        cur.execute(
            """
            SELECT i.codigo, i.titulo, i.finalidade, i.preco,
                   b.nome AS bairro, c.nome AS cidade
              FROM imoveis i
              JOIN bairros b ON b.id = i.bairro_id
              JOIN cidades c ON c.id = b.cidade_id
             ORDER BY i.codigo
             LIMIT 3
            """
        )
        print("\n== Amostra de imóveis ==")
        for linha in cur.fetchall():
            print(
                f"  {linha['codigo']} | {linha['titulo']} | "
                f"{linha['bairro']}, {linha['cidade']} | "
                f"{linha['finalidade']} | R$ {linha['preco']}"
            )

    print("\nTudo certo: o back-end pode subir com 'python app.py'.")


def main():
    argumentos = {arg.lower() for arg in sys.argv[1:]}
    somente_verificar = "--verificar" in argumentos
    sem_confirmacao = "--sim" in argumentos or "-y" in argumentos

    conn = conectar()
    try:
        if somente_verificar:
            verificar(conn)
            return

        if not sem_confirmacao:
            print(
                "\nATENÇÃO: isto APAGA as tabelas atuais do banco configurado "
                "e recria com os dados de exemplo."
            )
            resposta = input("Digite 'sim' para continuar: ").strip().lower()
            if resposta != "sim":
                print("Cancelado. Nada foi alterado.")
                return

        aplicar(conn)
        verificar(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
