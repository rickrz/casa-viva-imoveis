"""
Acesso ao PostgreSQL (Neon).

Usamos psycopg2 com RealDictCursor: cada linha volta como dicionário
(ex.: {"id": 1, "nome": "Casa"}), pronto para virar JSON.

Não há ORM aqui de propósito: o objetivo da disciplina é enxergar o SQL.
"""

from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from config import Config


@contextmanager
def conexao():
    """
    Abre uma conexão e garante o fechamento.

    - Sucesso  -> commit (grava as alterações).
    - Exceção  -> rollback (desfaz tudo e repassa o erro para a rota).
    """
    conn = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def buscar_todos(sql, parametros=()):
    """Executa um SELECT e devolve uma lista de dicionários."""
    with conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            return cur.fetchall()


def buscar_um(sql, parametros=()):
    """Executa um SELECT que deve devolver no máximo uma linha."""
    with conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            return cur.fetchone()


def executar(sql, parametros=()):
    """
    Executa INSERT, UPDATE ou DELETE.

    Quando o SQL termina com `RETURNING id`, devolve a linha retornada;
    caso contrário, devolve None.
    """
    with conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, parametros)
            if cur.description:  # existe resultado (RETURNING)
                return cur.fetchone()
            return None
