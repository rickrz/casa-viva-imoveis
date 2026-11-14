# Roteiro da apresentação — 8 a 10 minutos

Seminário de 3 integrantes. Tempo-alvo: **9 minutos**, deixando 1 minuto de
folga para imprevistos. Cada pessoa fala cerca de 3 minutos.

> Ensaie com cronômetro. A demonstração ao vivo é o trecho que mais atrasa:
> deixe abas abertas e o banco já populado antes de começar.

---

## Antes de começar (checklist de 2 minutos)

- [ ] API rodando e `/api/health` com `banco: conectado` e `ia: configurada`.
- [ ] Site aberto na aba 1, em tela cheia.
- [ ] `admin.html` aberto na aba 2.
- [ ] `banco.html` aberto na aba 3 (DER, tabelas e consultas SQL).
- [ ] Neon com uma consulta pronta na aba 4 (opcional).
- [ ] Chat limpo (recarregar a página) para a saudação aparecer.
- [ ] Volume do projetor e fonte do navegador em 110%.

---

## 0:00 – 3:00 | [Nome 2] — Problema, arquitetura e banco

**Fala de abertura (30 s):**

> Boa noite. Somos [nomes] e apresentamos a Casa Viva Imóveis, uma imobiliária
> fictícia que atende São Paulo, Campinas e Belo Horizonte. O problema que
> escolhemos resolver é simples: encontrar imóvel ainda envolve anúncio
> desatualizado, documentação confusa e demora no atendimento.

**Arquitetura (45 s):** mostre o diagrama do README.

> A solução tem três camadas. O navegador roda HTML, CSS e JavaScript puro. A
> API em Flask concentra as regras e conversa com o PostgreSQL no Neon. A IA
> fica atrás da API: a chave do Gemini nunca chega ao navegador.

**Banco (60 s):** abra `docs/der.md` ou o diagrama renderizado.

> Modelamos cinco tabelas em Terceira Forma Normal. Cidade e bairro ficam
> separados para não repetir texto; o tipo de imóvel também. `imoveis` é a
> entidade central, e `contatos` guarda o formulário com chave estrangeira
> opcional para o imóvel. Temos chaves primárias, estrangeiras com `ON DELETE`
> definido, `UNIQUE`, dez `CHECK`s e índices para busca por finalidade, preço e
> status.

**Consultas (30 s):** mostre uma consulta de `database/consultas.sql`.

> Esta consulta junta imóveis, bairros e cidades e calcula a média por bairro
> com `GROUP BY`. As outras quatro cobrem `LEFT JOIN`, `CASE` e `Top 5`.

**Transição:**

> Agora o [Nome 1] mostra como isso aparece para o cliente.

---

## 3:00 – 6:00 | [Nome 1] — Site e painel

**Página inicial (40 s):** role devagar a página.

> O site começa com o hero e um imóvel em destaque, que vem da API. O cabeçalho
> é fixo, muda de cor ao rolar e, no celular, vira uma gaveta com o botão
> hambúrguer. Toda a paleta está documentada em variáveis no `:root`.

**Filtros (50 s):** selecione “Alugar” e depois uma cidade.

> Os cards não estão escritos no HTML: o JavaScript chama `GET /api/imoveis` e
> monta a lista. Cada filtro vira parâmetro de consulta no banco. Vou filtrar
> por aluguel — repare que o contador e os cards mudam juntos.

**Formulário (60 s):** clique em “Tenho interesse” em um card e envie vazio.

> O botão seleciona o imóvel no formulário. Se eu tentar enviar vazio, a
> validação do navegador marca nome, e-mail, telefone e interesse. Agora vou
> preencher e enviar. O `fetch` faz o `POST`, a API valida de novo no servidor e
> o contato é gravado no PostgreSQL.

**Painel (50 s):** abra `admin.html` e altere um status.

> Este é o painel administrativo. Ele lista os contatos reais do banco, resume
> por status e permite alterar, excluir e exportar CSV. A alteração usa `PUT`;
> o registro sai do painel na hora e continua no banco.

**Transição:**

> Com o contato salvo, entra a parte de inteligência artificial, com a [Nome 3].

---

## 6:00 – 9:00 | [Nome 3] — Lia, segurança e conclusão

**Como funciona (50 s):**

> A Lia é a assistente virtual. O navegador manda a mensagem para
> `POST /api/chat`. O Flask busca os imóveis disponíveis no banco, monta um
> *system prompt* com a persona, as regras e a carteira, e só então chama o
> Gemini. A chave fica no `.env` do servidor. O histórico é curto: no máximo as
> oito mensagens mais recentes, e cada mensagem tem limite de mil caracteres.

**Demonstração dentro do escopo (50 s):**

Digite: `Quero alugar um apartamento em Belo Horizonte. Quanto custa?`

> Espero que ela cite o CV-008, na Savassi, por R$ 3.500 por mês, e faça uma
> pergunta de qualificação. Ela só pode usar os dados que vieram do banco.

**Demonstração fora do escopo (40 s):**

Digite: `Me passa uma receita de bolo de cenoura.`

> Ela recusa em uma frase e volta para imóveis. Isso está no prompt: não opina
> sobre política, não dá receita, não inventa imóvel e não pede CPF ou dados
> bancários.

**Segurança e deploy (30 s):**

> As credenciais ficam só no `.env`; o CORS é restrito; todas as consultas são
> parametrizadas; e o front escapa o texto vindo do banco. O site e a API estão
> publicados juntos no Render, na mesma origem, com o banco no Neon.

**Conclusão (30 s):**

> O projeto integrou interface, API, banco normalizado e IA com escopo
> controlado. O principal aprendizado foi que a qualidade do assistente depende
> menos do modelo e mais do contexto e das regras ao redor dele. Obrigado!
> Estamos à disposição para perguntas.

---

## Plano B (se algo falhar)

| Problema | O que fazer |
|---|---|
| Internet caiu | use as capturas em `docs/prints/` e o vídeo gravado de backup |
| API hibernou | abra `/api/health` antes; aguarde o cold start |
| Gemini sem cota | mostre `docs/exemplos-chat.md` e explique o fallback `503` |
| Formulário não envia | mostre o erro de validação e a aba Network |
| Tempo estourou | pule a segunda demo do chat e vá direto à conclusão |

## Divisão de perguntas

- **Banco/back-end:** [Nome 2]
- **Front-end/UX:** [Nome 1]
- **IA/deploy:** [Nome 3]
- Se a pergunta for geral, quem estiver com o microfone responde e passa a
  palavra: “Complementando o que o [nome] falou...”.
