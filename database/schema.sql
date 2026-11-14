-- =====================================================================
-- Casa Viva Imóveis — Esquema do banco de dados (PostgreSQL / Neon)
-- Disciplina: Banco de Dados
-- Modelo normalizado até a 3ª Forma Normal (3FN).
--
-- COMO USAR:
--   1. Abra o SQL Editor do Neon (ou o psql).
--   2. Cole e execute TODO este arquivo primeiro.
--   3. Depois execute database/seed.sql para carregar os dados de exemplo.
-- =====================================================================

-- Remove as tabelas na ordem inversa das dependências.
-- Isso permite rodar o script novamente durante o desenvolvimento.
DROP TABLE IF EXISTS contatos CASCADE;
DROP TABLE IF EXISTS imoveis CASCADE;
DROP TABLE IF EXISTS tipos_imoveis CASCADE;
DROP TABLE IF EXISTS bairros CASCADE;
DROP TABLE IF EXISTS cidades CASCADE;

-- ---------------------------------------------------------------------
-- 1) CIDADES
-- Guardar a cidade em uma tabela própria evita repetir "São Paulo/SP"
-- em dezenas de imóveis — redundância que violaria a 3FN.
-- ---------------------------------------------------------------------
CREATE TABLE cidades (
    id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(80) NOT NULL,
    uf   CHAR(2)     NOT NULL CHECK (uf ~ '^[A-Z]{2}$'),

    CONSTRAINT uq_cidades_nome_uf UNIQUE (nome, uf)
);

-- ---------------------------------------------------------------------
-- 2) BAIRROS
-- Cada bairro pertence a UMA cidade (1:N). O par (nome, cidade) é único,
-- pois pode existir "Centro" em várias cidades.
-- ---------------------------------------------------------------------
CREATE TABLE bairros (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome      VARCHAR(80) NOT NULL,
    cidade_id INTEGER     NOT NULL,

    CONSTRAINT fk_bairros_cidade
        FOREIGN KEY (cidade_id) REFERENCES cidades (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_bairros_nome_cidade UNIQUE (nome, cidade_id)
);

-- ---------------------------------------------------------------------
-- 3) TIPOS DE IMÓVEIS
-- Casa, Apartamento, Terreno, Sala Comercial...
-- ---------------------------------------------------------------------
CREATE TABLE tipos_imoveis (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome      VARCHAR(40) NOT NULL,
    descricao TEXT,

    CONSTRAINT uq_tipos_imoveis_nome UNIQUE (nome)
);

-- ---------------------------------------------------------------------
-- 4) IMÓVEIS
-- Entidade central. Aponta para tipo e bairro por chave estrangeira.
-- CHECKs garantem dados coerentes (preço positivo, finalidade válida...).
-- ---------------------------------------------------------------------
CREATE TABLE imoveis (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo     VARCHAR(12)   NOT NULL,
    titulo     VARCHAR(140)  NOT NULL,
    descricao  TEXT          NOT NULL,
    tipo_id    INTEGER       NOT NULL,
    bairro_id  INTEGER       NOT NULL,
    finalidade VARCHAR(10)   NOT NULL,
    status     VARCHAR(12)   NOT NULL DEFAULT 'disponivel',
    preco      NUMERIC(12,2) NOT NULL,
    quartos    SMALLINT      NOT NULL DEFAULT 0,
    banheiros  SMALLINT      NOT NULL DEFAULT 0,
    vagas      SMALLINT      NOT NULL DEFAULT 0,
    area_m2    NUMERIC(8,2)  NOT NULL,
    imagem_url TEXT,
    destaque   BOOLEAN       NOT NULL DEFAULT FALSE,
    criado_em  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_imoveis_tipo
        FOREIGN KEY (tipo_id) REFERENCES tipos_imoveis (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_imoveis_bairro
        FOREIGN KEY (bairro_id) REFERENCES bairros (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_imoveis_codigo UNIQUE (codigo),

    CONSTRAINT ck_imoveis_finalidade
        CHECK (finalidade IN ('venda', 'aluguel')),

    CONSTRAINT ck_imoveis_status
        CHECK (status IN ('disponivel', 'reservado', 'vendido', 'alugado')),

    CONSTRAINT ck_imoveis_preco CHECK (preco > 0),
    CONSTRAINT ck_imoveis_area CHECK (area_m2 > 0),
    CONSTRAINT ck_imoveis_quartos CHECK (quartos >= 0),
    CONSTRAINT ck_imoveis_banheiros CHECK (banheiros >= 0),
    CONSTRAINT ck_imoveis_vagas CHECK (vagas >= 0),
    CONSTRAINT ck_imoveis_titulo CHECK (char_length(trim(titulo)) >= 5),
    CONSTRAINT ck_imoveis_descricao CHECK (char_length(trim(descricao)) >= 20)
);

-- ---------------------------------------------------------------------
-- 5) CONTATOS
-- Registros enviados pelo formulário do site.
-- imovel_id é OPCIONAL: a pessoa pode querer apenas falar com a equipe.
-- ON DELETE SET NULL mantém o histórico do contato se o imóvel for excluído.
-- ---------------------------------------------------------------------
CREATE TABLE contatos (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome           VARCHAR(120) NOT NULL,
    email          VARCHAR(160) NOT NULL,
    telefone       VARCHAR(20)  NOT NULL,
    tipo_interesse VARCHAR(10)  NOT NULL,
    imovel_id      INTEGER,
    mensagem       TEXT,
    status         VARCHAR(16)  NOT NULL DEFAULT 'novo',
    criado_em      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_contatos_imovel
        FOREIGN KEY (imovel_id) REFERENCES imoveis (id)
        ON DELETE SET NULL ON UPDATE CASCADE,

    CONSTRAINT ck_contatos_nome
        CHECK (char_length(trim(nome)) >= 3),

    CONSTRAINT ck_contatos_email
        CHECK (email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),

    CONSTRAINT ck_contatos_telefone
        CHECK (char_length(regexp_replace(telefone, '[^0-9]', '', 'g')) BETWEEN 10 AND 13),

    CONSTRAINT ck_contatos_interesse
        CHECK (tipo_interesse IN ('comprar', 'alugar', 'vender')),

    CONSTRAINT ck_contatos_status
        CHECK (status IN ('novo', 'em_atendimento', 'atendido')),

    CONSTRAINT ck_contatos_mensagem
        CHECK (mensagem IS NULL OR char_length(mensagem) <= 2000)
);

-- ---------------------------------------------------------------------
-- ÍNDICES
-- Chaves estrangeiras não são indexadas automaticamente no PostgreSQL.
-- Estes índices aceleram os JOINs e os filtros do site.
-- ---------------------------------------------------------------------
CREATE INDEX idx_bairros_cidade        ON bairros (cidade_id);
CREATE INDEX idx_imoveis_tipo          ON imoveis (tipo_id);
CREATE INDEX idx_imoveis_bairro        ON imoveis (bairro_id);
CREATE INDEX idx_imoveis_finalidade    ON imoveis (finalidade, status);
CREATE INDEX idx_imoveis_preco         ON imoveis (preco);
CREATE INDEX idx_contatos_status       ON contatos (status);
CREATE INDEX idx_contatos_imovel       ON contatos (imovel_id);
CREATE INDEX idx_contatos_criado_em    ON contatos (criado_em DESC);
