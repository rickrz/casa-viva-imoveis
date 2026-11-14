-- =====================================================================
-- Casa Viva Imóveis — 5 consultas para demonstrar na apresentação
-- Execute no SQL Editor do Neon, uma por vez, explicando o resultado.
-- =====================================================================

-- ---------------------------------------------------------------------
-- CONSULTA 1 — Contatos recebidos + imóvel de interesse + localização
-- Demonstra JOIN com LEFT JOIN (contatos sem imóvel também aparecem).
-- ---------------------------------------------------------------------
SELECT c.id,
       c.nome,
       c.email,
       c.tipo_interesse,
       c.status,
       COALESCE(i.codigo, '—')                          AS codigo_imovel,
       COALESCE(i.titulo, 'Não informado')              AS imovel,
       COALESCE(b.nome || ' / ' || ci.uf, '—')          AS localizacao,
       c.criado_em
  FROM contatos c
  LEFT JOIN imoveis  i  ON i.id = c.imovel_id
  LEFT JOIN bairros  b  ON b.id = i.bairro_id
  LEFT JOIN cidades  ci ON ci.id = b.cidade_id
 ORDER BY c.criado_em DESC;

-- ---------------------------------------------------------------------
-- CONSULTA 2 — Quantidade de contatos por tipo de interesse
-- Usa GROUP BY e uma window function para calcular o percentual.
-- ---------------------------------------------------------------------
SELECT tipo_interesse,
       COUNT(*)                                              AS total,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)    AS percentual
  FROM contatos
 GROUP BY tipo_interesse
 ORDER BY total DESC;

-- ---------------------------------------------------------------------
-- CONSULTA 3 — Imóveis disponíveis para venda por faixa de preço
-- Demonstra CASE WHEN + GROUP BY por expressão.
-- ---------------------------------------------------------------------
SELECT CASE
         WHEN preco < 500000   THEN 'Até R$ 500 mil'
         WHEN preco < 1000000  THEN 'R$ 500 mil a R$ 1 milhão'
         ELSE                       'Acima de R$ 1 milhão'
       END              AS faixa,
       COUNT(*)         AS quantidade
  FROM imoveis
 WHERE status = 'disponivel'
   AND finalidade = 'venda'
 GROUP BY faixa
 ORDER BY MIN(preco);

-- ---------------------------------------------------------------------
-- CONSULTA 4 — Preço médio por tipo de imóvel e finalidade
-- Demonstra JOIN + AVG + MIN/MAX + GROUP BY com duas colunas.
-- ---------------------------------------------------------------------
SELECT t.nome          AS tipo,
       i.finalidade,
       COUNT(*)        AS quantidade,
       ROUND(AVG(i.preco), 2) AS preco_medio,
       MIN(i.preco)    AS menor_preco,
       MAX(i.preco)    AS maior_preco
  FROM imoveis i
  JOIN tipos_imoveis t ON t.id = i.tipo_id
 GROUP BY t.nome, i.finalidade
 ORDER BY t.nome, i.finalidade;

-- ---------------------------------------------------------------------
-- CONSULTA 5 — Top 5 bairros por quantidade de imóveis e ticket médio
-- LEFT JOIN para incluir bairros ainda sem imóvel cadastrado.
-- ---------------------------------------------------------------------
SELECT b.nome          AS bairro,
       c.nome          AS cidade,
       c.uf,
       COUNT(i.id)     AS imoveis,
       ROUND(AVG(i.preco), 2) AS ticket_medio
  FROM bairros b
  JOIN cidades c      ON c.id = b.cidade_id
  LEFT JOIN imoveis i ON i.bairro_id = b.id
 GROUP BY b.id, b.nome, c.nome, c.uf
 ORDER BY imoveis DESC, ticket_medio DESC
 LIMIT 5;
