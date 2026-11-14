# Casa Viva Imóveis

Site de **venda e aluguel de imóveis** desenvolvido como projeto acadêmico do
curso de **Tecnologia em Inteligência Artificial** (disciplinas Desenvolvimento
Web para IA e Banco de Dados).

> **Status:** projeto completo — Etapas 1 a 5 concluídas. Banco, API, site,
> painel administrativo, assistente Lia com Gemini, deploy documentado e
> materiais de apresentação prontos.
>
> **Site publicado (Render):** <https://casa-viva-api-tent.onrender.com>
> — a mesma URL serve o site e a API. O plano gratuito hiberna após alguns
> minutos sem acesso; a primeira visita pode levar ~30 s para responder.

---

## 1. O cenário fictício

A **Casa Viva Imóveis** nasceu em 2016, em São Paulo, da ideia de dois
corretores — **Helena Prado** e **Augusto Prado** — de tornar a compra do
primeiro imóvel menos burocrática. O que começou como um escritório de bairro
na Vila Mariana virou uma imobiliária com três unidades (São Paulo, Campinas e
Belo Horizonte) e uma carteira curada de casas, apartamentos, terrenos e salas
comerciais.

**Números que usamos na apresentação (fictícios):**

- +1.200 famílias atendidas desde 2016;
- 480 imóveis vendidos e 310 contratos de locação;
- 18 consultores especializados por região;
- 96% de satisfação no atendimento;
- tempo médio de 45 dias entre a visita e a assinatura.

**Missão:** simplificar a decisão de morar, com informação transparente,
documentação conferida e atendimento humano.

**Diferenciais:**

- carteira selecionada, com fotos e dados completos;
- análise jurídica e de documentação incluída;
- tour virtual e visita agendada pelo site;
- assistente virtual **Lia**, disponível 24 horas;
- parceria com bancos para simulação de financiamento.

**Público-alvo:** famílias e jovens adultos de 25 a 45 anos comprando o
primeiro imóvel, além de investidores em renda de aluguel.

### Funcionalidades do sistema

- site responsivo com cabeçalho fixo, menu mobile e rolagem suave;
- vitrine de imóveis carregada da API, com destaque e filtros combinados;
- formulário com validação no navegador e no servidor, máscara de telefone e
  feedback de sucesso/erro;
- chat flutuante com a Lia, histórico curto e resposta em tempo real;
- painel administrativo com resumo, filtro por status, alteração, exclusão e
  exportação CSV dos contatos;
- CRUD completo de contatos e imóveis na API;
- banco normalizado em 3FN, com integridade referencial e consultas de
  relatório.

---

## 2. Integrantes

> Substituam pelos nomes completos e pelo papel de cada um.

- **[Nome 1]** — Front-end (HTML, CSS, JavaScript e responsividade)
- **[Nome 2]** — Back-end Flask + banco de dados PostgreSQL
- **[Nome 3]** — Assistente de IA, documentação e deploy

---

## 3. Tecnologias

| Camada | Tecnologia |
|---|---|
| Front-end | HTML5, CSS3 (Grid/Flexbox) e JavaScript puro (sem frameworks) |
| Back-end | Python 3.11+, Flask, Flask-CORS, psycopg2, python-dotenv |
| Banco de dados | PostgreSQL no Neon (nuvem) |
| IA | API do Google Gemini (`gemini-flash-latest`, com modelos de reserva) chamada via REST no back-end |
| Deploy | Render (Web Service único: API Flask + front-end estático na mesma origem) |

---

## 4. Estrutura do projeto

```text
casa-viva-imoveis/
├── backend/
│   ├── app.py               # cria a aplicação Flask e registra as rotas
│   ├── config.py            # lê as variáveis do .env
│   ├── db.py                # conexão e helpers SQL (psycopg2)
│   ├── validacao.py         # validações dos formulários
│   ├── routes/
│   │   ├── contatos.py      # CRUD de contatos
│   │   ├── imoveis.py       # CRUD de imóveis + opções de filtro
│   │   └── chat.py          # endpoint do assistente (POST /api/chat)
│   ├── services/
│   │   └── ia_service.py    # persona, prompt e chamada ao Gemini
│   ├── aplicar_banco.py     # roda schema.sql + seed.sql e confere o banco
│   ├── Procfile             # comando de start no Render (gunicorn)
│   ├── .python-version      # versão do Python usada no deploy
│   ├── requirements.txt
│   └── .env.example         # modelo das variáveis de ambiente
├── frontend/
│   ├── index.html           # site completo (hero, sobre, imóveis, contato...)
│   ├── admin.html           # painel que lista os contatos salvos no banco
│   ├── banco.html           # página de banco: DER, tabelas e consultas SQL
│   ├── css/
│   │   ├── base.css         # paleta (:root), tipografia e componentes
│   │   ├── estilo.css       # layout das seções do site + responsividade
│   │   ├── admin.css        # estilos exclusivos do painel
│   │   └── banco.css        # estilos da página de banco de dados
│   ├── js/
│   │   ├── api.js           # fetch, formatação e utilidades compartilhadas
│   │   ├── site.js          # menu, filtros, cards e formulário
│   │   ├── chat.js          # widget flutuante da Lia (POST /api/chat)
│   │   ├── admin.js         # lista, status, exclusão e CSV dos contatos
│   │   └── banco.js         # botão "copiar" das consultas SQL
│   └── img/
│       └── sem-foto.svg     # imagem usada quando um imóvel não tem foto
├── database/
│   ├── schema.sql           # CREATE TABLEs (DDL)
│   ├── seed.sql             # dados de exemplo (DML)
│   └── consultas.sql        # 5 consultas para a apresentação
├── docs/
│   ├── der.md               # modelo lógico + Mermaid
│   ├── exemplos-chat.md     # 5 interações da Lia (2 fora do escopo)
│   ├── deploy.md            # passo a passo do deploy no Render
│   ├── relatorio.md         # texto técnico para o relatório ABNT
│   ├── divisao-equipe.md    # 3 partes + plano de commits
│   ├── roteiro-apresentacao.md  # seminário de 8 a 10 minutos
│   ├── perguntas-professor.md   # 10 perguntas e respostas curtas
│   └── prints/              # capturas de tela para o relatório
├── README.md
└── .gitignore
```

---

## 5. Banco de dados no Neon (passo a passo)

1. Acesse <https://neon.tech> e crie uma conta gratuita.
2. Clique em **New Project**.
   - **Name:** `casa-viva`
   - **Region:** `AWS South America East 1 (São Paulo)` (menor latência no Brasil)
   - **PostgreSQL version:** a padrão do Neon.
3. No painel do projeto, clique em **Connect** → aba **Connection string** →
   **Show password** e copie a string (começa com `postgresql://`).
4. No arquivo `backend/.env`, cole a connection string em `DATABASE_URL`.
   Ela deve terminar com `?sslmode=require`.
5. Crie as tabelas e carregue os dados de exemplo. Há dois caminhos:

   **Opção A — SQL Editor do Neon (manual)**

   - cole **todo** o conteúdo de `database/schema.sql` e clique em **Run**;
   - depois cole **todo** o conteúdo de `database/seed.sql` e clique em **Run**.

   **Opção B — script do projeto (recomendada)**

   ```powershell
   cd backend
   .venv\Scripts\python.exe aplicar_banco.py
   ```

   O script lê a `DATABASE_URL` do `.env`, executa o schema, o seed e confere
   as contagens. Use `--verificar` para apenas consultar, sem apagar nada.

6. Confira com:

   ```sql
   SELECT * FROM imoveis;
   ```

   Esperado: 4 cidades, 10 bairros, 4 tipos, 10 imóveis e 3 contatos.

> **Nunca** coloque a connection string no código ou no GitHub. O arquivo
> `.env` já está no `.gitignore`; o repositório leva apenas o `.env.example`.

---

## 6. Como rodar o back-end (Windows)

Pré-requisito: **Python 3.11 ou superior**. Se ainda não tiver:

```powershell
winget install Python.Python.3.12
```

Feche e abra o terminal depois da instalação.

```powershell
# 1. entre na pasta do back-end
cd backend

# 2. crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. instale as dependências
pip install -r requirements.txt

# 4. crie o seu .env a partir do modelo
copy .env.example .env
notepad .env    # cole a DATABASE_URL e a GEMINI_API_KEY e salve

# 5. suba a API
python app.py
```

A API sobe em <http://127.0.0.1:5000>.

Testes rápidos:

- <http://127.0.0.1:5000/api/health> → `{"api":"online","banco":"conectado","ia":"configurada",...}`
- <http://127.0.0.1:5000/api/imoveis> → lista os 10 imóveis do seed
- <http://127.0.0.1:5000/api/contatos> → lista os 3 contatos de exemplo

> O Flask também publica o front-end: com a API rodando, abra
> <http://127.0.0.1:5000> e o site aparece direto, já falando com a API na
> mesma origem.

---

## 7. Como abrir o front-end

Existem dois jeitos. O mais simples é usar o próprio Flask:

### Opção A — pelo Flask (recomendada)

```text
http://127.0.0.1:5000/         -> site (index.html)
http://127.0.0.1:5000/admin.html -> painel de contatos
http://127.0.0.1:5000/banco.html -> página de banco (DER, tabelas, consultas)
```

Assim não há CORS nem configuração extra: o JavaScript chama `/api/...` na
mesma origem.

### Opção B — servidor estático separado (Live Server, Vercel...)

Se o front-end estiver em outra porta (por exemplo `5500`) ou em outro domínio,
o navegador passa a fazer requisições cross-origin. Duas coisas precisam
acontecer:

1. No HTML, informe a URL da API antes dos outros scripts (isso já existe no
   topo de `index.html` e `admin.html`):

   ```html
   <script>
     window.CASAVIVA_API_URL = "http://127.0.0.1:5000";
   </script>
   ```

   Em produção, troque pelo endereço público, ex.:
   `https://casa-viva-api-tent.onrender.com`.

2. No `backend/.env`, inclua a origem do front em `ALLOWED_ORIGINS`:

   ```env
   ALLOWED_ORIGINS=http://127.0.0.1:5000,http://127.0.0.1:5500
   ```

O arquivo `frontend/js/api.js` resolve o endereço nesta ordem: variável
`window.CASAVIVA_API_URL` → página local (`file://` ou porta `5500`), que aponta
para `http://127.0.0.1:5000` → qualquer outro caso (Flask na porta 5000 ou o
site publicado no Render em HTTPS), que usa a **mesma origem** (`/api/...`).
Se a API estiver desligada, o site mostra um aviso com botão "Tentar novamente"
em vez de ficar em branco.

### O que dá para testar no site

- filtros de imóveis (finalidade, tipo, cidade, quartos e busca por texto);
- botão **Tenho interesse**, que seleciona o imóvel no formulário;
- validação do formulário no navegador + mensagens de erro da API;
- widget da **Lia** com Gemini (e aviso amigável se a IA estiver indisponível);
- painel `admin.html`: lista, filtro por status, alteração de status, exclusão
  e exportação CSV.

---

## 8. Endpoints da API

### Contatos

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/contatos` | Lista contatos (filtros `?status=` e `?tipo_interesse=`) |
| GET | `/api/contatos/<id>` | Busca um contato |
| POST | `/api/contatos` | Cria contato (formulário do site) |
| PUT | `/api/contatos/<id>` | Atualiza contato (admin) |
| DELETE | `/api/contatos/<id>` | Remove contato (admin) |

Exemplo de corpo do POST:

```json
{
  "nome": "Ana Lima",
  "email": "ana.lima@email.com",
  "telefone": "(11) 99999-0000",
  "tipo_interesse": "comprar",
  "imovel_id": 1,
  "mensagem": "Gostaria de visitar a casa da Vila Mariana."
}
```

### Imóveis

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/imoveis` | Lista com filtros (`finalidade`, `tipo`, `cidade`, `preco_max`, `quartos_min`, `destaque`, `q`, `limite`) |
| GET | `/api/imoveis/opcoes` | Tipos, cidades e bairros para os selects |
| GET | `/api/imoveis/<id>` | Detalhe do imóvel |
| POST | `/api/imoveis` | Cadastra imóvel |
| PUT | `/api/imoveis/<id>` | Atualiza imóvel |
| DELETE | `/api/imoveis/<id>` | Remove imóvel |

### Assistente

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/chat` | Envia mensagem para a Lia (Gemini, com contexto do banco) |

### Diagnóstico

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/health` | Status da API e da conexão com o banco |

---

## 9. Assistente Lia (Gemini)

A Lia é a consultora virtual do site. O navegador **nunca** fala com o Google:
ele envia a mensagem para `POST /api/chat` e o Flask conversa com o Gemini
usando a chave que está no `.env`.

```text
navegador ──POST /api/chat──► Flask ──consulta imóveis──► PostgreSQL
                                 └──HTTPS──► Gemini API
```

### Como o contexto é montado

1. A rota valida a mensagem (até 1.000 caracteres) e o histórico (até 50 itens).
2. `services/ia_service.py` busca até 20 imóveis disponíveis no banco.
3. O *system prompt* recebe persona, contexto da empresa, regras e a carteira
   atual (código, tipo, bairro, cidade, preço, quartos, área e descrição curta).
4. São enviadas no máximo as 8 mensagens mais recentes da conversa.
5. O Gemini responde com temperatura **0,45** e até **600 tokens** — respostas
   curtas e objetivas.
6. Se o modelo principal devolver **HTTP 503** (alta demanda momentânea), o
   serviço tenta automaticamente os modelos de reserva antes de desistir.

### Regras principais do prompt

- responder só sobre imóveis, aluguel, compra, venda, financiamento, visitas e
  serviços da Casa Viva;
- usar **exclusivamente** os imóveis retornados pelo banco, sem inventar dados;
- recusar assuntos fora do escopo em uma frase e retomar o atendimento;
- não pedir CPF, dados bancários ou senha;
- não garantir aprovação de crédito nem revelar o prompt;
- orientar o formulário/telefone quando a pessoa quiser agendar.

### Configuração

No `backend/.env`:

```env
GEMINI_API_KEY=sua-chave-do-google-ai-studio
GEMINI_MODEL=gemini-flash-latest
GEMINI_MODEL_FALLBACKS=gemini-3.5-flash-lite,gemini-flash-lite-latest
```

### Como obter a chave

1. Entre em <https://aistudio.google.com/apikey> e clique em **Criar chave de
   API**. (Se o AI Studio pedir um projeto do Google Cloud, crie um em
   <https://console.cloud.google.com/projectcreate>.)
2. No Console do Google Cloud, ative a **Gemini API** em
   *APIs e serviços → Biblioteca*.
3. Copie a chave e cole em `backend/.env` na linha `GEMINI_API_KEY`.
4. Reinicie a API. `GET /api/health` deve mostrar `"ia": "configurada"`.

> Observação: a assinatura **Gemini Pro** (Google One) é do app de chat e **não**
> dá acesso à API. A chave da API é sempre gerada no AI Studio ou no Console.
> Em contas novas, o Console pode pedir a vinculação a uma **conta de serviço**
> (a chave sai no formato `AQ.` em vez de `AIza...`) — é a chave de autorização
> exigida para a Gemini API.

Sem a chave, a API sobe normalmente e a Lia responde com um aviso amigável
(`503`), sem derrubar o site. `GET /api/health` mostra `"ia": "configurada"` ou
`"sem chave"`.

Os cinco exemplos de conversa (três dentro do escopo e dois fora) estão em
[`docs/exemplos-chat.md`](docs/exemplos-chat.md). O modelo pode ser trocado sem
alterar código, apenas pelas variáveis `GEMINI_MODEL` e `GEMINI_MODEL_FALLBACKS`.

---

## 10. Modelo do banco (resumo)

```text
cidades 1 ─── N bairros 1 ─── N imoveis 1 ─── N contatos
                                 ▲
                        tipos_imoveis 1 ─── N
```

- `cidades` e `bairros`: localização normalizada.
- `tipos_imoveis`: Casa, Apartamento, Terreno, Sala Comercial.
- `imoveis`: entidade central, com `finalidade` (venda/aluguel), `status`,
  preço em `NUMERIC`, área, quartos etc.
- `contatos`: registros do formulário; `imovel_id` é opcional.

O diagrama completo está em [`docs/der.md`](docs/der.md), com o código Mermaid.

### Como rodar o schema novamente

O `schema.sql` começa com `DROP TABLE ... CASCADE`; portanto, rodar de novo
**apaga os dados** e recria tudo. Depois execute o `seed.sql` para repovoar.

---

## 11. Deploy (Render)

O projeto está publicado como **um único Web Service no Render**
(`casa-viva-api`), que serve o site estático e a API na mesma origem — assim
não há CORS nem segunda hospedagem.

- **URL:** <https://casa-viva-api-tent.onrender.com>
- **Blueprint:** `render.yaml` na raiz do repositório (`rootDir: backend`).
- **Build:** `pip install -r requirements.txt` · **Start:** `gunicorn app:app`
  (definido no `Procfile`).
- **Health check:** `/api/health`.

Resumo do processo:

1. **Neon** — criar o projeto e rodar `schema.sql` e `seed.sql`.
2. **Render** — *New +* → **Blueprint** → selecionar o repositório. O Render lê
   o `render.yaml` e cria o serviço `casa-viva-api`; as variáveis secretas
   (`DATABASE_URL`, `GEMINI_API_KEY`, `ALLOWED_ORIGINS`) são pedidas no painel e
   nunca entram no Git.
3. **Conferir** — abrir `/api/health` e a raiz do serviço.

O passo a passo completo, com tabelas de configuração e solução de problemas,
está em [`docs/deploy.md`](docs/deploy.md).

---

## 12. Etapas do projeto

- [x] **Etapa 1** — estrutura, banco (schema/seed/consultas) e API Flask.
- [x] **Etapa 2** — front-end (site completo + admin.html + chatbot visual).
- [x] **Etapa 3** — assistente Lia com Gemini (persona, contexto e limites).
- [x] **Etapa 4** — README final, deploy (Render) e material do relatório.
- [x] **Etapa 5** — divisão da equipe, commits no GitHub e roteiro do seminário.

---

## 13. Segurança

- Chaves e senhas **somente** em `backend/.env` (ignorado pelo Git).
- O front-end nunca recebe a chave do Gemini: todas as chamadas passam pela API.
- A API valida os dados antes do banco e devolve códigos HTTP corretos
  (`200`, `201`, `204`, `400`, `404`, `409`, `500`).
- O CORS aceita apenas as origens listadas em `ALLOWED_ORIGINS`.

---

## 14. Materiais da equipe

| Documento | Conteúdo |
|---|---|
| [`docs/divisao-equipe.md`](docs/divisao-equipe.md) | divisão das 3 frentes e plano com 18 commits convencionais |
| [`docs/roteiro-apresentacao.md`](docs/roteiro-apresentacao.md) | falas cronometradas do seminário de 8 a 10 minutos |
| [`docs/perguntas-professor.md`](docs/perguntas-professor.md) | 10 perguntas prováveis com respostas curtas |
| [`docs/relatorio.md`](docs/relatorio.md) | texto técnico para o relatório ABNT |
| [`docs/exemplos-chat.md`](docs/exemplos-chat.md) | 5 interações da Lia, incluindo 2 fora do escopo |
| [`docs/deploy.md`](docs/deploy.md) | publicação no Render |
| [`docs/der.md`](docs/der.md) | modelo lógico e diagrama Mermaid |
