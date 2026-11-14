# Divisão da equipe e plano de commits

Projeto **Casa Viva Imóveis** — 3 integrantes, 5 etapas. A divisão abaixo é
equilibrada por esforço e permite que cada pessoa consiga explicar a sua parte
na apresentação.

> Substituam **[Nome 1]**, **[Nome 2]** e **[Nome 3]** pelos nomes reais e
> usem exatamente esses nomes no README e no relatório.

| Integrante | Frente principal | Entregas |
|---|---|---|
| **[Nome 1]** | Front-end | `index.html`, `admin.html`, 3 arquivos CSS, 4 scripts JS, responsividade, acessibilidade, capturas de tela |
| **[Nome 2]** | Banco + back-end | `schema.sql`, `seed.sql`, `consultas.sql`, DER, rotas CRUD, validações, conexão Neon, testes da API |
| **[Nome 3]** | IA + deploy + documentação | `ia_service.py`, prompt da Lia, exemplos de chat, deploy Render/Vercel, README, relatório e roteiro |

### Regra de trabalho

- Nenhum integrante altera a frente do outro sem avisar.
- Todo `push` na `main` exige que a API continue subindo e o site abrindo.
- Segredos nunca entram no Git: apenas `backend/.env.example`.
- Cada etapa termina com uma revisão rápida dos outros dois.

---

## Plano de commits (18 commits convencionais)

Formato: `tipo(escopo): descrição no imperativo`.

Distribuí os commits em **10 dias** e nas três frentes. A ordem sugerida é a
da tabela; ajustem as datas conforme o calendário real da equipe.

| # | Dia | Autor | Commit |
|---:|---|---|---|
| 1 | 1 | [Nome 2] | `chore: cria estrutura de pastas e gitignore` |
| 2 | 1 | [Nome 3] | `docs: adiciona cenario da empresa e integrantes no README` |
| 3 | 2 | [Nome 2] | `feat(db): cria schema normalizado com checks e indices` |
| 4 | 2 | [Nome 2] | `feat(db): adiciona seed com imoveis, cidades e contatos` |
| 5 | 3 | [Nome 2] | `feat(api): implementa configuracao, conexao e health check` |
| 6 | 3 | [Nome 2] | `feat(api): adiciona crud e validacao de contatos` |
| 7 | 4 | [Nome 2] | `feat(api): adiciona crud de imoveis e filtros de busca` |
| 8 | 4 | [Nome 3] | `feat(chat): cria rota inicial do assistente com limite de mensagem` |
| 9 | 5 | [Nome 1] | `feat(ui): cria pagina inicial com hero, sobre e secoes` |
| 10 | 5 | [Nome 1] | `style: adiciona paleta no root e layout responsivo` |
| 11 | 6 | [Nome 1] | `feat(ui): integra cards de imoveis e filtros com a api` |
| 12 | 6 | [Nome 1] | `feat(chat): cria widget flutuante de conversa com a lia` |
| 13 | 7 | [Nome 1] | `feat(admin): cria painel de contatos com status e exportacao csv` |
| 14 | 7 | [Nome 3] | `feat(ia): integra gemini com persona, contexto do banco e historico` |
| 15 | 8 | [Nome 3] | `test(ia): valida prompt, sanitizacao e respostas de erro` |
| 16 | 8 | [Nome 3] | `docs: adiciona exemplos de conversa e guia de deploy` |
| 17 | 9 | [Nome 3] | `docs: escreve relatorio tecnico e roteiro da apresentacao` |
| 18 | 10 | [Nome 1] | `docs: adiciona capturas de tela e revisa textos do site` |

### Commits opcionais (se precisarem passar de 18)

| Autor | Commit |
|---|---|
| [Nome 2] | `docs(db): adiciona der em mermaid e consultas de relatorio` |
| [Nome 1] | `fix(ui): corrige menu mobile e foco do teclado` |
| [Nome 3] | `chore(deploy): adiciona procfile e python-version` |
| [Nome 2] | `test(api): cobre erros 400, 404 e 409 com curl` |

### Como executar (exemplo)

```powershell
git init
git add .
git commit -m "chore: cria estrutura de pastas e gitignore"

# nas próximas entregas
git add backend/database/schema.sql
git commit -m "feat(db): cria schema normalizado com checks e indices"

git remote add origin https://github.com/USUARIO/casa-viva-imoveis.git
git branch -M main
git push -u origin main
```

> **Importante:** façam commits reais ao longo do trabalho. Não criem 18
> commits de uma vez no último dia — o histórico deve refletir a evolução.

### Checklist do GitHub

- [ ] repositório público (ou com os professores convidados);
- [ ] `README.md` com nomes reais e link do deploy;
- [ ] `.env` fora do repositório (confira com `git status`);
- [ ] 15+ commits convencionais, de pelo menos dois integrantes diferentes;
- [ ] branch `main` funcionando do zero (clonar, instalar, rodar);
- [ ] issues ou pull requests, se o professor exigir.
