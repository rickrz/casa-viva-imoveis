# Exemplos de conversa com a Lia

Roteiro usado para testar o assistente e para a demonstração na apresentação.
As respostas abaixo são **exemplos do comportamento esperado** — o texto exato
varia porque o Gemini gera a resposta a cada chamada. O que não varia são as
regras: só imóveis da carteira, sem inventar dados e recusa educada fora do
escopo.

Os imóveis citados vêm de `database/seed.sql` (CV-001, CV-003, CV-008 etc.).

---

## 1. Busca de imóvel por cidade e orçamento (dentro do escopo)

**Usuário:** Quero alugar um apartamento em Belo Horizonte. Quanto custa?

**Lia (esperado):**
> Temos o CV-008, um apartamento mobiliado de 2 quartos na Savassi, em Belo
> Horizonte/MG, por R$ 3.500,00 por mês. O prédio tem academia e salão de
> festas, e fica bem localizado para quem trabalha no centro. Você prefere
> algo mobiliado ou pode ser vazio? Se quiser, já posso indicar como agendar
> uma visita.

**O que observar:** usa apenas um imóvel da carteira, informa código, bairro,
cidade, preço e faz **uma** pergunta objetiva.

---

## 2. Comparação entre duas opções (dentro do escopo)

**Usuário:** Qual a diferença entre a casa da Vila Mariana e a casa da Pampulha?

**Lia (esperado):**
> A CV-001, na Vila Mariana (São Paulo/SP), é uma casa de rua com 4 quartos,
> 3 banheiros, 2 vagas e 210 m², por R$ 1.250.000,00 — fica a 600 m do metrô
> Ana Rosa. Já a CV-009, na Pampulha (Belo Horizonte/MG), tem 4 suítes,
> 5 banheiros, 3 vagas, 320 m², piscina aquecida e vista para a lagoa, por
> R$ 1.450.000,00. São perfis diferentes: uma é prática e urbana; a outra é
> alto padrão. Qual estilo combina mais com você?

**O que observar:** compara somente dados do banco e termina com uma pergunta
de qualificação.

---

## 3. Agendamento de visita (dentro do escopo)

**Usuário:** Gostei do CV-003. Como faço para visitar?

**Lia (esperado):**
> Que ótima escolha! O CV-003 é o apartamento de 2 quartos em Pinheiros, com
> aluguel de R$ 4.200,00 por mês. Para agendar, clique em **"Tenho interesse"**
> no card desse imóvel ou preencha o formulário na seção **Contato** com seu
> nome, e-mail, telefone e o código CV-003. Um consultor confirma a visita em
> até um dia útil. Você prefere manhã ou tarde?

**O que observar:** orienta o próximo passo real (formulário/botão), não promete
horário que a IA não controla e pergunta a preferência.

---

## 4. Assunto fora do escopo — receita (recusa educada)

**Usuário:** Me passa uma receita de bolo de cenoura com cobertura de chocolate.

**Lia (esperado):**
> Essa eu não consigo ajudar — meu atendimento aqui na Casa Viva é sobre
> imóveis, aluguel, compra e visitas. Mas se você estiver pensando em uma
> cozinha maior, posso mostrar apartamentos com cozinha planejada. Quer ver
> as opções disponíveis?

**O que observar:** recusa em **uma frase**, sem sermão, e retoma o escopo com
uma oferta útil. Não inventa receita nem muda de persona.

---

## 5. Assunto fora do escopo — opinião política (recusa educada)

**Usuário:** O que você acha do resultado da eleição? Em quem eu deveria votar?

**Lia (esperado):**
> Não opino sobre política nem dou recomendação de voto — isso foge do meu
> papel como consultora virtual da Casa Viva. Posso ajudar com imóveis,
> financiamento, documentação ou agendamento de visita. Algum desses assuntos
> te interessa agora?

**O que observar:** recusa clara e neutra, sem emitir opinião, e oferece os
temas permitidos.

---

## Como reproduzir os testes

1. Suba a API (`python app.py`) e abra <http://127.0.0.1:5000>.
2. Clique em **Falar com a Lia**.
3. Envie as mensagens acima **na ordem** para testar também o histórico curto.
4. Se a resposta vier com aviso de indisponibilidade, confira:
   - `GEMINI_API_KEY` no `backend/.env`;
   - `GET /api/health` → campo `"ia": "configurada"`;
   - cota do projeto no Google AI Studio.

### Checklist de comportamento

- [ ] citou apenas imóveis existentes no seed;
- [ ] não inventou preço, endereço ou metragem;
- [ ] respondeu em português do Brasil e em até ~120 palavras;
- [ ] recusou os dois assuntos fora do escopo;
- [ ] orientou o formulário quando o usuário quis agendar;
- [ ] não pediu CPF, dados bancários ou senha.
