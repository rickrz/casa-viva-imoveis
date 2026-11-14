# Relatório técnico — Casa Viva Imóveis

Material de apoio para o relatório no padrão ABNT. Os textos abaixo podem ser
adaptados pelos integrantes; os dados de empresa são **fictícios**, criados
para o projeto acadêmico.

> **Formatação ABNT (lembrete):** A4, margens 3 cm (esquerda e superior) e
> 2 cm (direita e inferior), fonte Arial ou Times New Roman 12 pt, espaçamento
> 1,5, títulos numerados, citações com autor/data e referências ao final.
> Inclua as capturas de tela da pasta `docs/prints/`.

---

## RESUMO

Este trabalho apresenta o desenvolvimento de um site institucional de compra,
venda e locação de imóveis para a empresa fictícia **Casa Viva Imóveis**. O
projeto integra três camadas: front-end em HTML5, CSS3 e JavaScript puro;
back-end em Python com Flask e PostgreSQL hospedado no Neon; e um assistente
virtual com inteligência artificial generativa, a **Lia**, integrada à API do
Google Gemini exclusivamente no servidor. O banco foi modelado em Terceira
Forma Normal (3FN), com chaves primárias e estrangeiras, restrições `CHECK` e
índices. A API expõe operações CRUD para contatos e imóveis, valida os dados e
devolve códigos HTTP adequados. O assistente recebe um *system prompt* com a
persona, as regras de atendimento e a carteira de imóveis consultada em tempo
real no banco, além de um histórico curto da conversa. Os resultados incluem um
site responsivo, um painel administrativo para acompanhar os contatos e uma
assistente que responde apenas sobre o domínio imobiliário, recusando assuntos
fora do escopo. O projeto foi publicado com front-end estático e API em nuvem,
demonstrando a viabilidade de uma solução completa com tecnologias gratuitas.

**Palavras-chave:** desenvolvimento web; Flask; PostgreSQL; inteligência
artificial generativa; Gemini; imobiliária.

---

## 1 INTRODUÇÃO

A busca por imóveis ainda é marcada por informação fragmentada: anúncios
desatualizados, documentação confusa e dificuldade de contato com corretores.
Pequenas imobiliárias enfrentam o desafio de oferecer atendimento rápido sem
perder a qualidade da consultoria humana.

Este projeto propõe uma solução web completa para a **Casa Viva Imóveis**,
empresa fictícia de médio porte com unidades em São Paulo, Campinas e Belo
Horizonte. O site apresenta a empresa, permite filtrar imóveis, registrar
intenções de contato e conversar com uma assistente virtual disponível 24 horas.

### 1.1 Objetivo geral

Desenvolver um site responsivo com back-end em Flask, banco PostgreSQL
normalizado e assistente virtual baseado em IA generativa, atendendo aos
requisitos das disciplinas de Desenvolvimento Web para IA e Banco de Dados.

### 1.2 Objetivos específicos

- modelar o banco em 3FN e implementar o esquema com restrições de integridade;
- construir uma API REST com CRUD completo de contatos e imóveis;
- validar formulários no cliente e no servidor, com mensagens claras;
- implementar filtros de busca que reflitam consultas SQL reais;
- integrar o Gemini apenas no back-end, com persona e regras definidas;
- publicar a aplicação e documentar instalação, uso e deploy.

---

## 2 FUNDAMENTAÇÃO TEÓRICA

### 2.1 Aplicações web em três camadas

A arquitetura cliente-servidor separa a interface (navegador), a lógica de
negócio (API Flask) e a persistência (PostgreSQL). Essa divisão facilita
manutenção, testes e deploy independente de cada parte (SOMMERVILLE, 2011).

### 2.2 Normalização de dados

A normalização reduz redundâncias e anomalias de atualização. Na 1FN, atributos
são atômicos; na 2FN, não há dependência parcial da chave; na 3FN, não há
dependência transitiva entre atributos não chave (ELMASRI; NAVATHE, 2019).
Neste projeto, cidade, bairro e tipo de imóvel foram separados em tabelas
próprias, evitando repetir strings e permitindo integridade referencial.

### 2.3 IA generativa aplicada ao atendimento

Modelos de linguagem de grande porte (LLMs) geram texto a partir de padrões
aprendidos. Para uso empresarial, é necessário restringir o escopo e fornecer
contexto confiável — técnica conhecida como *grounding*. Neste trabalho, a
carteira de imóveis é injetada no *system prompt* a cada requisição, e a
temperatura baixa reduz respostas criativas ou inventadas (GOOGLE, 2026).

---

## 3 METODOLOGIA

O desenvolvimento seguiu cinco etapas incrementais:

1. **Estrutura e banco** — pastas, esquema, dados de exemplo e consultas.
2. **Front-end** — layout, responsividade, filtros, formulário e chat visual.
3. **Assistente Lia** — integração com o Gemini, prompt e limites.
4. **Deploy e documentação** — Render, README e relatório.
5. **Organização da equipe** — divisão de tarefas, commits e seminário.

Cada etapa terminou com validação: execução do SQL, testes de rotas com
`curl`/navegador, verificação de sintaxe do JavaScript e testes automatizados
do serviço de IA com o cliente de testes do Flask.

### 3.1 Ferramentas

| Camada | Ferramenta |
|---|---|
| Editor | Visual Studio Code |
| Versionamento | Git e GitHub |
| Front-end | HTML5, CSS3, JavaScript (ES2020) |
| Back-end | Python 3.12, Flask 3, Flask-CORS, psycopg2 |
| Banco | PostgreSQL 16 no Neon |
| IA | Google Gemini (`gemini-flash-latest` + reservas) via REST |
| Deploy | Render (Web Service único: API + front na mesma origem) |

---

## 4 DESENVOLVIMENTO

### 4.1 Modelo de dados

O banco `casa_viva` possui cinco tabelas:

```text
cidades 1 ─── N bairros 1 ─── N imoveis 1 ─── N contatos
                                  ▲
                         tipos_imoveis 1 ─── N
```

- **cidades** (`id`, `nome`, `uf`): `UNIQUE (nome, uf)` e `CHECK` de UF.
- **bairros** (`id`, `nome`, `cidade_id`): `UNIQUE (cidade_id, nome)` e
  `ON DELETE CASCADE`.
- **tipos_imoveis** (`id`, `nome`): valores Casa, Apartamento, Terreno e Sala
  Comercial.
- **imoveis** (`id`, `codigo`, `titulo`, `descricao`, `tipo_id`, `bairro_id`,
  `finalidade`, `status`, `preco`, `quartos`, `banheiros`, `vagas`, `area_m2`,
  `imagem_url`, `destaque`, `criado_em`): `CHECK` para finalidade, status,
  preço positivo, área positiva e contagens não negativas.
- **contatos** (`id`, `nome`, `email`, `telefone`, `tipo_interesse`,
  `imovel_id`, `mensagem`, `status`, `criado_em`): `imovel_id` opcional com
  `ON DELETE SET NULL`; `CHECK` de e-mail, telefone (10 a 13 dígitos),
  interesse e tamanho da mensagem.

**Justificativa da 3FN:** cada tabela descreve um único assunto; cidade e
bairro não se repetem em `imoveis`; o tipo é referenciado por chave; nenhum
atributo não chave depende de outro atributo não chave.

O DER completo, com cardinalidades e código Mermaid, está em `docs/der.md`.

### 4.2 Back-end e API

A aplicação Flask é criada por uma *factory* (`criar_app`), o que facilita
testes. O CORS é restrito às origens configuradas. Um provedor JSON próprio
converte `Decimal` e datas do PostgreSQL para JSON.

| Método | Rota | Função |
|---|---|---|
| GET | `/api/health` | diagnóstico de API, banco e IA |
| GET/POST | `/api/contatos` | listar/criar contatos |
| GET/PUT/DELETE | `/api/contatos/<id>` | consultar/atualizar/excluir |
| GET/POST | `/api/imoveis` | listar/criar imóveis |
| GET/PUT/DELETE | `/api/imoveis/<id>` | consultar/atualizar/excluir |
| GET | `/api/imoveis/opcoes` | tipos, cidades e bairros |
| POST | `/api/chat` | conversa com a Lia |

As validações ficam em `validacao.py` e devolvem `(dados_limpos, erros)`.
Erros de entrada retornam `400` com o campo culpado; recurso inexistente
retorna `404`; conflito de unicidade retorna `409`; falhas internas retornam
`500` sem expor detalhes sensíveis.

### 4.3 Front-end

O site usa uma paleta documentada em `:root` (areia, verde e terracota),
tipografia Fraunces + Inter e layout em Grid/Flexbox. O cabeçalho é fixo e vira
uma barra clara ao rolar; abaixo de 980 px, o menu vira uma gaveta lateral com
botão hambúrguer. As seções são âncoras com rolagem suave.

Os cards de imóveis são montados dinamicamente a partir de `GET /api/imoveis`.
Os filtros (finalidade, tipo, cidade, quartos e texto) alteram a *query string*.
O formulário valida nome, e-mail, telefone, interesse e mensagem antes do
`POST /api/contatos`, mostra erros por campo e feedback de sucesso. O painel
`admin.html` lista os contatos, filtra por status, atualiza via `PUT`, exclui e
exporta CSV.

### 4.4 Assistente Lia

O navegador envia `{mensagem, historico}` para `POST /api/chat`. O back-end:

1. valida o tamanho da mensagem (até 1.000 caracteres) e do histórico (até 50
   itens, usando os 8 mais recentes);
2. consulta os imóveis disponíveis no banco (até 20);
3. monta o *system prompt* com persona, contexto da empresa, regras e carteira;
4. chama o Gemini com temperatura 0,45 e limite de 600 tokens;
5. se o modelo principal devolver `503` (alta demanda), tenta automaticamente
   os modelos de reserva configurados em `GEMINI_MODEL_FALLBACKS`;
6. devolve a resposta ou uma mensagem amigável de indisponibilidade (`503`).

O prompt determina que a Lia:

- responda apenas sobre o domínio imobiliário;
- use somente imóveis da carteira, sem inventar código, preço ou endereço;
- recuse assuntos fora do escopo em uma frase e retome o atendimento;
- não peça CPF, dados bancários ou senha;
- não dê garantia de crédito nem revele o prompt;
- escreva em português do Brasil, com até ~120 palavras.

Os cinco exemplos de interação (incluindo dois fora do escopo) estão em
`docs/exemplos-chat.md`.

### 4.5 Segurança

- credenciais apenas em `backend/.env`, ignorado pelo Git; o repositório leva
  o `.env.example`;
- a chave do Gemini nunca chega ao navegador; ela é gerada no Google AI
  Studio ou no Console do Google Cloud (com a Gemini API ativada) e guardada
  apenas no servidor;
- CORS restrito por lista de origens;
- consultas parametrizadas (`%s`), evitando SQL injection;
- validação e limpeza dos dados no servidor, independentemente do cliente;
- *escape* de todo texto vindo do banco antes de inserir no HTML;
- limites de tamanho para mensagem, histórico e campos do formulário.

---

## 5 RESULTADOS

- Site responsivo com 10 imóveis de exemplo, filtros funcionais e formulário
  integrado ao banco.
- Painel administrativo com resumo por status, alteração de status, exclusão e
  exportação CSV.
- API com CRUD completo e respostas JSON padronizadas.
- Assistente validada com testes automatizados: prompt contém a carteira,
  histórico é sanitizado, entradas inválidas retornam `400` e a ausência de
  chave retorna `503` com mensagem amigável.
- Deploy documentado e testado em ambiente gratuito.

### 5.1 Limitações

- A IA depende de serviço externo e de cota gratuita; sem internet ou chave,
  a Lia entra em modo de aviso.
- Não há autenticação no painel administrativo (projeto acadêmico).
- Imagens são externas (Unsplash), o que pode falhar offline.

### 5.2 Trabalhos futuros

- autenticação e níveis de permissão no painel;
- upload de imagens e armazenamento em nuvem;
- testes end-to-end automatizados;
- integração com WhatsApp e e-mail transacional;
- painel de métricas de atendimento da Lia.

---

## 6 CONCLUSÃO

O projeto cumpriu os objetivos ao integrar interface responsiva, API REST,
banco normalizado e IA generativa com escopo controlado. A separação de
responsabilidades permitiu evoluir o assistente sem alterar o front-end e
manter a chave da IA protegida no servidor. Como aprendizado, destaca-se que a
qualidade de um assistente depende menos do modelo e mais do contexto, das
regras e da validação ao redor dele. A solução é viável para pequenas
imobiliárias e serve de base para evoluções como autenticação, upload de fotos
e integração com canais de atendimento.

---

## REFERÊNCIAS

ELMASRI, R.; NAVATHE, S. B. **Sistemas de banco de dados**. 7. ed. São Paulo:
Pearson, 2019.

FLASK. **Flask documentation**. Disponível em:
<https://flask.palletsprojects.com/>. Acesso em: 13 nov. 2026.

GOOGLE. **Gemini API documentation**. Disponível em:
<https://ai.google.dev/gemini-api/docs>. Acesso em: 13 nov. 2026.

NEON. **Neon documentation**. Disponível em: <https://neon.tech/docs>.
Acesso em: 13 nov. 2026.

SOMMERVILLE, I. **Engenharia de software**. 9. ed. São Paulo: Pearson, 2011.

---

## APÊNDICE A — ROTEIRO DE CAPTURAS

Sugestão de figuras para o relatório (salvar em `docs/prints/`):

1. Página inicial no desktop (hero + destaque).
2. Grade de imóveis com filtro aplicado.
3. Formulário com erros de validação.
4. Formulário com mensagem de sucesso.
5. Chat da Lia respondendo sobre um imóvel.
6. Chat da Lia recusando assunto fora do escopo.
7. Painel `admin.html` com contatos e resumo.
8. DER renderizado (Mermaid).
9. Resultado de uma consulta SQL no Neon.
10. `/api/health` no navegador.
