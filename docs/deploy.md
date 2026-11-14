# Deploy — Casa Viva Imóveis

Guia de publicação do projeto. A escolha feita foi **um único Web Service no
Render**, que serve o site e a API na mesma origem — assim não há CORS nem uma
segunda hospedagem. O banco continua no **Neon**.

```text
Neon (PostgreSQL)
      ▲
      │ DATABASE_URL
Render (Flask + gunicorn)  ── serve "/" (HTML/CSS/JS)  e  "/api/*"
      │
      └────────────── Gemini (HTTPS) ──  (só o back-end tem a chave)
```

> **Site publicado:** <https://casa-viva-api-tent.onrender.com>
> Todos os serviços têm plano gratuito. O Render hiberna após alguns minutos
> sem acesso; a primeira requisição depois disso pode demorar ~30 s.

---

## 1. Banco no Neon (uma vez)

1. Crie o projeto e rode `database/schema.sql` e `database/seed.sql`
   (passo a passo na seção 5 do `README.md`). Atalho: com o `backend/.env`
   já configurado, `python aplicar_banco.py` executa os dois arquivos.
2. Copie a connection string com `?sslmode=require`.

---

## 2. Publicação no Render (Blueprint)

O repositório traz o arquivo `render.yaml`, que descreve o serviço. Com ele o
deploy vira um clique:

1. Suba o projeto para o GitHub (o `.env` **não** vai junto).
2. No Render: **New +** → **Blueprint** → conecte o repositório.
3. O Render lê o `render.yaml` e mostra o serviço **casa-viva-api**:

   | Campo | Valor |
   |---|---|
   | Runtime | `Python 3` |
   | Root Directory | `backend` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
   | Health Check Path | `/api/health` |
   | Instance Type | Free |

   O `backend/Procfile` já contém o comando de start e o
   `backend/.python-version` fixa o Python 3.12.10.

4. Preencha as variáveis marcadas como secretas (`sync: false` no
   `render.yaml`). As demais já vêm do arquivo:

   | Variável | Origem | Exemplo / observação |
   |---|---|---|
   | `DATABASE_URL` | painel (secret) | connection string do Neon com `sslmode=require` |
   | `GEMINI_API_KEY` | painel (secret) | chave do Gemini (**secret**) |
   | `ALLOWED_ORIGINS` | painel (secret) | a própria URL do Render |
   | `GEMINI_MODEL` | `render.yaml` | `gemini-flash-latest` |
   | `GEMINI_MODEL_FALLBACKS` | `render.yaml` | `gemini-3.5-flash-lite,gemini-flash-lite-latest` |
   | `FLASK_DEBUG` | `render.yaml` | `0` |

5. Clique em **Deploy Blueprint** e aguarde o build.
6. Teste:

   - <https://casa-viva-api-tent.onrender.com/api/health>
   - esperado: `{"api":"online","banco":"conectado","ia":"configurada",...}`
   - e o site: <https://casa-viva-api-tent.onrender.com/>

> **Nota:** o nome `casa-viva-api` já estava em uso, então o Render criou o
> endereço `casa-viva-api-tent.onrender.com`. O nome do serviço continua
> `casa-viva-api` no painel.

### Deploy manual (sem Blueprint)

Se preferir criar à mão, use **New +** → **Web Service** com os mesmos campos da
tabela acima e cadastre as variáveis em **Environment**.

---

## 3. Front-end em outro domínio (opcional)

O front já é servido pelo próprio Flask, então este passo **não é necessário**.
Use-o apenas se quiser publicar o front separado da API (Vercel ou Render
Static Site).

1. **Add New** → **Project** → importe o mesmo repositório.
2. Configurações:

   | Campo | Valor |
   |---|---|
   | Framework Preset | `Other` |
   | Root Directory | `frontend` |
   | Build Command | *(vazio)* |
   | Output Directory | `.` |

3. Antes do deploy, edite `frontend/index.html` e `frontend/admin.html`:

   ```html
   <script>
     window.CASAVIVA_API_URL = "https://casa-viva-api-tent.onrender.com";
   </script>
   ```

4. Deploy. Copie a URL final (ex.: `https://casa-viva.vercel.app`).
5. Volte ao Render → **Environment** → atualize `ALLOWED_ORIGINS` com essa URL
   e salve (o serviço reinicia).
6. Abra o site publicado e teste formulário, filtros e chat.

### Alternativa: Render Static Site

**New +** → **Static Site** → Root Directory `frontend`, Build Command vazio,
Publish Directory `.`. O restante é igual (URL da API + CORS).

---

## 4. Checklist de publicação

- [x] `database/schema.sql` e `seed.sql` executados no Neon.
- [x] `/api/health` responde `banco: conectado`.
- [x] `ia: configurada` no health (chave presente).
- [x] Site e API na mesma origem (sem CORS no fluxo normal).
- [x] `ALLOWED_ORIGINS` contém a URL do Render (usado só se o front for separado).
- [x] Formulário grava e aparece no `admin.html`.
- [x] Chat responde algo coerente e recusa assunto fora do escopo.
- [x] Nenhuma chave aparece no console, no HTML ou no GitHub.
- [x] `.env` continua no `.gitignore`.

---

## 5. Problemas comuns

| Sintoma | Causa provável | Correção |
|---|---|---|
| `A API respondeu 500` | `DATABASE_URL` errada ou schema não rodado | confira o health e os logs do Render |
| Erro de CORS no console | origem não listada (só ocorre com o front separado) | inclua a URL do front em `ALLOWED_ORIGINS` |
| Chat com “chave não configurada” | `GEMINI_API_KEY` ausente | adicione a variável e reinicie |
| Chat demora ~12 s | modelo principal retornou 503 e entrou a reserva | comportamento esperado (ver `docs/relatorio.md`) |
| Primeira requisição lenta | Render Free hibernou | aguarde o cold start (~30 s) |
| Imagens não aparecem | URL do Unsplash bloqueada | troque por imagem local em `frontend/img/` |
