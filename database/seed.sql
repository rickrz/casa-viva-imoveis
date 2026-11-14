-- =====================================================================
-- Casa Viva Imóveis — Dados de exemplo (seed)
-- Execute DEPOIS de database/schema.sql.
--
-- Repare que usamos subconsultas (SELECT id FROM ...) em vez de números
-- fixos. Assim o seed funciona mesmo que os IDs gerados mudem.
-- =====================================================================

-- ---------------------------------------------------------------------
-- CIDADES ATENDIDAS
-- ---------------------------------------------------------------------
INSERT INTO cidades (nome, uf) VALUES
    ('São Paulo',      'SP'),
    ('Campinas',       'SP'),
    ('Santos',         'SP'),
    ('Belo Horizonte', 'MG');

-- ---------------------------------------------------------------------
-- BAIRROS
-- ---------------------------------------------------------------------
INSERT INTO bairros (nome, cidade_id) VALUES
    ('Vila Mariana',   (SELECT id FROM cidades WHERE nome = 'São Paulo')),
    ('Moema',          (SELECT id FROM cidades WHERE nome = 'São Paulo')),
    ('Pinheiros',      (SELECT id FROM cidades WHERE nome = 'São Paulo')),
    ('Vila Olímpia',   (SELECT id FROM cidades WHERE nome = 'São Paulo')),
    ('Cambuí',         (SELECT id FROM cidades WHERE nome = 'Campinas')),
    ('Barão Geraldo',  (SELECT id FROM cidades WHERE nome = 'Campinas')),
    ('Ponta da Praia', (SELECT id FROM cidades WHERE nome = 'Santos')),
    ('Boqueirão',      (SELECT id FROM cidades WHERE nome = 'Santos')),
    ('Savassi',        (SELECT id FROM cidades WHERE nome = 'Belo Horizonte')),
    ('Pampulha',       (SELECT id FROM cidades WHERE nome = 'Belo Horizonte'));

-- ---------------------------------------------------------------------
-- TIPOS DE IMÓVEIS
-- ---------------------------------------------------------------------
INSERT INTO tipos_imoveis (nome, descricao) VALUES
    ('Casa',          'Casas e sobrados prontos para morar.'),
    ('Apartamento',   'Apartamentos em prédios com lazer e segurança.'),
    ('Terreno',       'Terrenos e lotes para construção.'),
    ('Sala Comercial','Salas e conjuntos para escritórios e lojas.');

-- ---------------------------------------------------------------------
-- IMÓVEIS
-- Fotos reais do Unsplash (troque as URLs em src/js/catalogo.js ou no banco).
-- ---------------------------------------------------------------------
INSERT INTO imoveis
    (codigo, titulo, descricao, tipo_id, bairro_id, finalidade, status,
     preco, quartos, banheiros, vagas, area_m2, imagem_url, destaque)
VALUES
    ('CV-001',
     'Casa ampla na Vila Mariana',
     'Casa de rua com 4 quartos, quintal arborizado, churrasqueira e garagem para 2 carros. Fica a 600 metros do metrô Ana Rosa.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Casa'),
     (SELECT id FROM bairros WHERE nome = 'Vila Mariana'),
     'venda', 'disponivel', 1250000.00, 4, 3, 2, 210.00,
     'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1200&q=70',
     TRUE),

    ('CV-002',
     'Apartamento reformado em Moema',
     'Apartamento de 3 quartos com suíte, varanda gourmet e dois andares de lazer. Condomínio com portaria 24 horas.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Apartamento'),
     (SELECT id FROM bairros WHERE nome = 'Moema'),
     'venda', 'disponivel', 890000.00, 3, 2, 2, 96.00,
     'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=70',
     TRUE),

    ('CV-003',
     'Apartamento charmoso em Pinheiros',
     'Dois quartos, sala integrada, cozinha planejada e uma vaga. A poucos passos da Rua dos Pinheiros e do metrô Fradique Coutinho.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Apartamento'),
     (SELECT id FROM bairros WHERE nome = 'Pinheiros'),
     'aluguel', 'disponivel', 4200.00, 2, 1, 1, 68.00,
     'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-004',
     'Casa familiar no Cambuí',
     'Sobrado com 3 quartos, quintal, escritório e garagem coberta. Bairro arborizado, perto de escolas e comércio.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Casa'),
     (SELECT id FROM bairros WHERE nome = 'Cambuí'),
     'venda', 'disponivel', 780000.00, 3, 2, 2, 160.00,
     'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-005',
     'Terreno a 300 m da praia',
     'Lote plano de 360 m² em rua tranquila, com água, luz e esgoto disponíveis. Excelente para construir ou investir.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Terreno'),
     (SELECT id FROM bairros WHERE nome = 'Ponta da Praia'),
     'venda', 'disponivel', 650000.00, 0, 0, 0, 360.00,
     'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-006',
     'Sala comercial na Vila Olímpia',
     'Conjunto de 120 m² com recepção, copa e dois banheiros. Prédio com elevadores, segurança e estacionamento rotativo.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Sala Comercial'),
     (SELECT id FROM bairros WHERE nome = 'Vila Olímpia'),
     'aluguel', 'disponivel', 6800.00, 0, 2, 2, 120.00,
     'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-007',
     'Casa com piscina no Boqueirão',
     'Casa de 3 quartos com piscina, área gourmet coberta e jardim. Rua sem saída, a cinco minutos da orla.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Casa'),
     (SELECT id FROM bairros WHERE nome = 'Boqueirão'),
     'venda', 'disponivel', 980000.00, 3, 3, 2, 185.00,
     'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-008',
     'Apartamento prático na Savassi',
     'Apartamento de 2 quartos, mobiliado, com academia e salão de festas no prédio. Ideal para quem trabalha no centro de BH.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Apartamento'),
     (SELECT id FROM bairros WHERE nome = 'Savassi'),
     'aluguel', 'disponivel', 3500.00, 2, 2, 1, 74.00,
     'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=1200&q=70',
     FALSE),

    ('CV-009',
     'Casa contemporânea na Pampulha',
     'Projeto assinado, 4 suítes, pé-direito alto, piscina aquecida e vista para a lagoa. Acabamento de alto padrão.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Casa'),
     (SELECT id FROM bairros WHERE nome = 'Pampulha'),
     'venda', 'disponivel', 1450000.00, 4, 5, 3, 320.00,
     'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=70',
     TRUE),

    ('CV-010',
     'Terreno em condomínio fechado',
     'Lote de 450 m² em condomínio com portaria, clube e área verde. Pronto para construir, com projeto aprovado.',
     (SELECT id FROM tipos_imoveis WHERE nome = 'Terreno'),
     (SELECT id FROM bairros WHERE nome = 'Barão Geraldo'),
     'venda', 'disponivel', 520000.00, 0, 0, 0, 450.00,
     'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=70',
     FALSE);

-- ---------------------------------------------------------------------
-- CONTATOS DE EXEMPLO (para o admin.html já abrir com dados)
-- Datas diferentes para demonstrar a ordenação por data.
-- ---------------------------------------------------------------------
INSERT INTO contatos
    (nome, email, telefone, tipo_interesse, imovel_id, mensagem, status, criado_em)
VALUES
    ('Mariana Alves',
     'mariana.alves@email.com',
     '(11) 98888-1111',
     'comprar',
     (SELECT id FROM imoveis WHERE codigo = 'CV-001'),
     'Gostaria de agendar uma visita no sábado pela manhã.',
     'em_atendimento',
     NOW() - INTERVAL '2 days'),

    ('Rafael Souza',
     'rafael.souza@email.com',
     '(11) 97777-2222',
     'alugar',
     (SELECT id FROM imoveis WHERE codigo = 'CV-003'),
     'Qual é o valor do condomínio e do IPTU?',
     'novo',
     NOW() - INTERVAL '1 day'),

    ('Helena Martins',
     'helena.martins@email.com',
     '(31) 96666-3333',
     'vender',
     NULL,
     'Quero uma avaliação do meu apartamento na Savassi.',
     'atendido',
     NOW() - INTERVAL '5 days');
