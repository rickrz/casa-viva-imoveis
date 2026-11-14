# Deploy — Casa Viva Imóveis

Guia para publicar a **API no Render** e o **front-end na Vercel** (ou no
Render Static Site). O banco continua no **Neon**.

```text
Neon (PostgreSQL)
      ▲
      │ DATABASE_URL
Render (Flask + gunicorn)  ◄── fetch ──  Vercel (HTML/CSS/JS)
      │                                   window.CASAVIVA_API_URL
      └────────────── Gemini (HTTPS) ─────┘   (só o back-end tem a chave)
```

> Todos os serviços têm plano gratuito. O Render hiberna após alguns minutos
> sem acesso; a primeira requisição depois disso pode demorar ~30 s.

---

## 1. Banco no Neon (uma vez)

1. Crie o projeto e rode `database/schema.sql` e `database/seed.sql`
   (passo a passo na seção 5 do `README.md`). Atalho: com o `backend/.env`
   já configurado, `python aplicar_banco.py` executa os dois arquivos.
2. Copie a connection string com `?sslmode=require`.

---

## 2. API no Render

1. Suba o projeto para o GitHub (o `.env` **não** vai junto).
2. No Render: **New +** → **Web Service** → conecte o repositório.
3. Preencha:

   | Campo | Valor |
   |---|---|
   | Name | `casa-viva-api` |
   | Language | `Python 3` |
   | Root Directory | `backend` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
   | Instance Type | Free |

   O arquivo `backend/Procfile` já contém o comando de start; o
   `backend/.python-version` fixa o Python 3.12.10.

4. Em **Environment Variables**, adicione:

   | Variável | Exemplo / observação |
   |---|---|
   | `DATABASE_URL` | connection string do Neon com `sslmode=require` |
   | `GEMINI_API_KEY` | chave do Google AI Studio (**secret**) |
   | `GEMINI_MODEL` | `gemini-flash-latest` |
   | `GEMINI_MODEL_FALLBACKS` | `gemini-3.5-flash-lite,gemini-flash-lite-latest` |
   | `ALLOWED_ORIGINS` | `https://casa-viva.vercel.app,http://127.0.0.1:5000` |
   | `FLASK_DEBUG` | `0` |

5. Clique em **Create Web Service** e aguarde o build.
6. Teste:

   - `https://casa-viva-api.onrender.com/api/health`
   - esperado: `{"api":"online","banco":"conectado","ia":"configurada",...}`

> A API também serve o front-end. Se quiser simplificar, use só o Render e
> acesse `https://casa-viva-api.onrender.com/` — não precisa de Vercel.

---

## 3. Front-end na Vercel (opcional)

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
     window.CASAVIVA_API_URL = "https://casa-viva-api.onrender.com";
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

- [ ] `database/schema.sql` e `seed.sql` executados no Neon.
- [ ] `/api/health` responde `banco: conectado`.
- [ ] `ia: configurada` no health (chave presente).
- [ ] `ALLOWED_ORIGINS` contém a URL exata do front (sem barra no final).
- [ ] `window.CASAVIVA_API_URL` aponta para a API (sem barra no final).
- [ ] Formulário grava e aparece no `admin.html`.
- [ ] Chat responde algo coerente e recusa assunto fora do escopo.
- [ ] Nenhuma chave aparece no console, no HTML ou no GitHub.
- [ ] `.env` continua no `.gitignore`.

---

## 5. Problemas comuns

| Sintoma | Causa provável | Correção |
|---|---|---|
| `A API respondeu 500` | `DATABASE_URL` errada ou schema não rodado | confira o health e os logs do Render |
| Erro de CORS no console | origem não listada | inclua a URL do front em `ALLOWED_ORIGINS` |
| Chat com “chave não configurada” | `GEMINI_API_KEY` ausente | adicione a variável e reinicie |
| Primeira requisição lenta | Render Free hibernou | aguarde o cold start |
| Imagens não aparecem | URL do Unsplash bloqueada | troque por imagem local em `frontend/img/` |
