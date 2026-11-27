-- =====================================================================
-- Casa Viva Imóveis — segurança do painel administrativo
-- ---------------------------------------------------------------------
-- Este arquivo NÃO contém senhas nem chaves. Ele só cria a estrutura.
-- A senha temporária e a chave da sessão são geradas localmente por
-- backend/aplicar_seguranca.py e gravadas já com hash/valor aleatório.
--
-- Aplicação:
--   cd backend
--   .venv\Scripts\python.exe aplicar_seguranca.py
-- =====================================================================

CREATE TABLE IF NOT EXISTS config_seguranca (
    chave          VARCHAR(60) PRIMARY KEY,
    valor          TEXT NOT NULL,
    atualizado_em  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS administradores (
    id                SERIAL PRIMARY KEY,
    usuario           VARCHAR(80) NOT NULL UNIQUE,
    nome              VARCHAR(120) NOT NULL DEFAULT 'Administrador',
    senha_hash        TEXT NOT NULL,
    trocar_senha      BOOLEAN NOT NULL DEFAULT TRUE,
    ativo             BOOLEAN NOT NULL DEFAULT TRUE,
    tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    bloqueado_ate     TIMESTAMPTZ,
    ultimo_login      TIMESTAMPTZ,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT administradores_usuario_tamanho CHECK (char_length(usuario) >= 3),
    CONSTRAINT administradores_tentativas_validas CHECK (tentativas_falhas >= 0)
);

-- Deixa o script seguro para rodar de novo em um banco que já tenha parte
-- da tabela (útil durante a apresentação).
ALTER TABLE administradores
    ADD COLUMN IF NOT EXISTS trocar_senha BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS ativo BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS bloqueado_ate TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS ultimo_login TIMESTAMPTZ;

COMMENT ON TABLE administradores IS
    'Usuários autorizados a acessar /admin.html. A senha fica hasheada (PBKDF2-SHA256).';

COMMENT ON COLUMN administradores.trocar_senha IS
    'TRUE obriga a troca da senha temporária no primeiro login.';

COMMENT ON TABLE config_seguranca IS
    'Configurações sensíveis persistidas no banco, como a chave de assinatura da sessão.';
