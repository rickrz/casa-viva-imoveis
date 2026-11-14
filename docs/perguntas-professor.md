# 10 perguntas prováveis do professor (com respostas curtas)

Respostas de 20 a 40 segundos. Ajustem os nomes e treinem em voz alta.

---

### 1. Por que Flask e não Django?

Porque o projeto é pequeno e a disciplina pede para enxergar o que acontece.
O Flask é minimalista: eu escolho as peças (CORS, conexão, rotas) e consigo
explicar cada linha. O Django traria ORM, admin e várias convenções que
esconderiam o SQL, que é justamente o que queremos demonstrar.

---

### 2. Por que não usaram ORM?

Para manter o SQL explícito. Usamos `psycopg2` com consultas parametrizadas,
então joins, filtros e agregações ficam visíveis no código e podem ser
mostrados no relatório. O custo é escrever mais SQL; o ganho é didática e
controle total das consultas.

---

### 3. Como vocês garantem que o banco está em 3FN?

Cada tabela tem um assunto: cidade, bairro, tipo, imóvel e contato. Cidade e
bairro não se repetem em `imoveis`; o tipo é referenciado por chave. Não há
atributo não chave dependendo de outro atributo não chave — por exemplo, o UF
fica só em `cidades`, não em `imoveis`. As chaves estrangeiras preservam a
integridade.

---

### 4. Como a Lia evita inventar imóveis ou preços?

O back-end consulta os imóveis disponíveis no banco e injeta essa lista no
*system prompt* a cada requisição. O prompt proíbe inventar e manda dizer “não
temos no momento” quando o pedido não está na carteira. A temperatura baixa
(0,45) reduz respostas criativas. Ainda assim, é uma IA generativa: por isso
limitamos o escopo e orientamos o contato humano.

---

### 5. Onde fica a chave do Gemini? O navegador tem acesso?

Não. A chave fica em `backend/.env`, que está no `.gitignore`. O navegador só
chama `POST /api/chat`; quem fala com o Google é o Flask. No deploy, a chave é
uma variável de ambiente secreta no Render. O repositório leva apenas o
`.env.example` vazio.

---

### 6. O que acontece se o Gemini cair ou a cota acabar?

A API continua no ar. O serviço captura timeout, erro HTTP, cota (429) e
resposta inválida, registra no log e devolve `503` com uma mensagem amigável
que indica o formulário e o telefone. O site não quebra: o chat mostra o aviso
e o resto das funções continua normal.

---

### 7. Como o formulário é validado?

Em duas camadas. No navegador, o JavaScript confere nome, e-mail, telefone,
interesse e tamanho da mensagem para dar resposta imediata. No servidor,
`validacao.py` repete as regras e devolve `400` com o campo culpado. O banco
ainda tem `CHECK`s como última barreira. Nunca confiamos só no cliente.

---

### 8. Por que PostgreSQL no Neon e não um banco local?

O Neon é PostgreSQL gerenciado na nuvem, com plano gratuito e connection string
pronta para o Render. Isso permite que o site publicado e o ambiente local
usem o mesmo banco, sem instalar servidor. O código é SQL padrão, então dá para
migrar para outro PostgreSQL mudando apenas a `DATABASE_URL`.

---

### 9. O painel administrativo tem login?

Não, e essa é uma limitação assumida do projeto acadêmico. O foco era CRUD,
banco e IA. Em produção, o próximo passo seria autenticação com sessão ou JWT,
permissões por papel e proteção das rotas de escrita. Deixamos isso registrado
como trabalho futuro no relatório.

---

### 10. O que vocês fariam diferente com mais tempo?

Três coisas: autenticação no painel, upload de imagens em vez de URL externa e
testes end-to-end automatizados. Também evoluiríamos a Lia com métricas de
atendimento e integração com WhatsApp, mantendo o mesmo princípio: IA só no
back-end, com contexto vindo do banco e regras explícitas.

---

## Perguntas de reserva

| Pergunta | Resposta curta |
|---|---|
| O site funciona no celular? | Sim: menu gaveta abaixo de 980 px, grid de uma coluna e chat em largura total; testado com redimensionamento. |
| Como evitam SQL injection? | Todas as consultas usam `%s` com parâmetros; nunca concatenamos entrada do usuário. |
| Quantos imóveis o seed tem? | Dez imóveis em quatro cidades, quatro tipos e três contatos de exemplo. |
| O que é o `/api/health`? | Diagnóstico que confirma API, banco e se a chave da IA está configurada, sem expor segredo. |
| Como o histórico do chat é limitado? | O front guarda 12 mensagens, envia as 8 últimas; a rota recusa mais de 50 itens e o serviço trunca cada texto em 1.000 caracteres. |
| Por que JavaScript puro? | Requisito da disciplina e demonstração de DOM, `fetch`, validação e responsividade sem dependência de framework. |
| O CSV é gerado onde? | No navegador, a partir dos contatos já carregados, com BOM e ponto e vírgula para abrir certo no Excel em português. |
| Como fizeram o DER? | Modelo lógico em `docs/der.md`, com cardinalidades e código Mermaid pronto para renderizar. |
