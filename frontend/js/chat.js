/* =====================================================================
   chat.js — widget flutuante da assistente Lia
   ---------------------------------------------------------------------
   O navegador NUNCA fala com o Gemini: ele manda a mensagem para
   POST /api/chat e o Flask (com a chave no .env) conversa com a IA.

   Histórico curto: guardamos no máximo as últimas 6 trocas (12 mensagens)
   e enviamos apenas as 8 mensagens anteriores mais recentes. Isso mantém
   o contexto da conversa sem estourar o limite de tokens do modelo.
   ===================================================================== */
(function () {
  "use strict";

  var CV = window.CV;
  var requisitar = CV.requisitar;

  var raiz = document.getElementById("chat");
  if (!raiz) return;

  var painel = document.getElementById("chatPainel");
  var botaoChat = document.getElementById("chatBotao");
  var botaoFechar = document.getElementById("chatFechar");
  var listaMensagens = document.getElementById("chatMensagens");
  var sugestoes = document.getElementById("chatSugestoes");
  var formulario = document.getElementById("chatForm");
  var entrada = document.getElementById("chatInput");
  var botaoEnviar = formulario.querySelector('button[type="submit"]');

  var historico = []; // [{ papel: "user" | "model", texto: "..." }]
  var enviando = false;
  var jaSaudou = false;

  var SAUDACAO =
    "Oi! Eu sou a Lia, consultora virtual da Casa Viva Imóveis. " +
    "Posso ajudar você a encontrar um imóvel, entender como funciona o " +
    "financiamento ou agendar uma visita. O que você procura?";

  /* -------------------------------------------------------------------
     Abrir / fechar
     ------------------------------------------------------------------- */
  function abrir() {
    raiz.classList.add("chat--aberto");
    botaoChat.setAttribute("aria-expanded", "true");
    painel.setAttribute("aria-hidden", "false");

    if (!jaSaudou) {
      adicionarMensagem("model", SAUDACAO);
      jaSaudou = true;
    }

    setTimeout(function () {
      entrada.focus();
    }, 220);
  }

  function fechar() {
    raiz.classList.remove("chat--aberto");
    botaoChat.setAttribute("aria-expanded", "false");
    painel.setAttribute("aria-hidden", "true");
    botaoChat.focus();
  }

  botaoChat.addEventListener("click", function () {
    if (raiz.classList.contains("chat--aberto")) {
      fechar();
    } else {
      abrir();
    }
  });

  botaoFechar.addEventListener("click", fechar);

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape" && raiz.classList.contains("chat--aberto")) {
      fechar();
    }
  });

  /* Qualquer botão com [data-abrir-chat] no site abre a janela. */
  document.querySelectorAll("[data-abrir-chat]").forEach(function (botao) {
    botao.addEventListener("click", abrir);
  });

  /* -------------------------------------------------------------------
     Mensagens na tela
     ------------------------------------------------------------------- */
  function adicionarMensagem(papel, texto) {
    var bolha = document.createElement("div");
    bolha.className = "chat__msg chat__msg--" + (papel === "user" ? "usuario" : "lia");
    bolha.textContent = texto; // textContent evita HTML injetado na conversa
    listaMensagens.appendChild(bolha);
    listaMensagens.scrollTop = listaMensagens.scrollHeight;
    return bolha;
  }

  function mostrarDigitando() {
    var bolha = document.createElement("div");
    bolha.className = "chat__msg chat__msg--lia chat__digitando";
    bolha.setAttribute("aria-label", "Lia está digitando");
    bolha.innerHTML = "<span></span><span></span><span></span>";
    listaMensagens.appendChild(bolha);
    listaMensagens.scrollTop = listaMensagens.scrollHeight;
    return bolha;
  }

  /* -------------------------------------------------------------------
     Envio
     ------------------------------------------------------------------- */
  async function enviar(texto) {
    var mensagem = String(texto || "").trim();
    if (!mensagem || enviando) return;

    if (mensagem.length > 1000) {
      CV.avisar("A mensagem pode ter no máximo 1000 caracteres.", "erro");
      return;
    }

    enviando = true;
    botaoEnviar.disabled = true;
    sugestoes.hidden = true;

    // O histórico enviado é o das trocas ANTERIORES: a mensagem atual vai
    // separada no campo "mensagem".
    var historicoAnterior = historico.slice(-8);

    adicionarMensagem("user", mensagem);
    historico.push({ papel: "user", texto: mensagem });
    entrada.value = "";

    var bolhaDigitando = mostrarDigitando();

    try {
      var resposta = await requisitar("/api/chat", {
        metodo: "POST",
        dados: {
          mensagem: mensagem,
          historico: historicoAnterior,
        },
      });

      bolhaDigitando.remove();

      var textoLia =
        (resposta && resposta.resposta) ||
        "Desculpe, não consegui responder agora. Pode tentar de novo?";

      adicionarMensagem("model", textoLia);
      historico.push({ papel: "model", texto: textoLia });

      // Mantém o histórico curto (6 trocas = 12 mensagens).
      if (historico.length > 12) {
        historico.splice(0, historico.length - 12);
      }
    } catch (erro) {
      bolhaDigitando.remove();

      // O que o visitante vê é sempre a mensagem amigável da API
      // (campo "resposta"). O detalhe técnico fica no console, para
      // não expor configuração interna do servidor no site.
      var amigavel =
        (erro.dados && erro.dados.resposta) ||
        "Não consegui falar com a assistente agora. " +
          "Tente novamente ou envie sua mensagem pelo formulário de contato.";

      if (erro.message) {
        console.warn("Chat indisponível:", erro.message);
      }

      adicionarMensagem("model", amigavel);
    } finally {
      enviando = false;
      botaoEnviar.disabled = false;
      entrada.focus();
    }
  }

  formulario.addEventListener("submit", function (evento) {
    evento.preventDefault();
    enviar(entrada.value);
  });

  /* Botões de sugestão (ex.: "Como funciona o financiamento?") */
  sugestoes.querySelectorAll("[data-sugestao]").forEach(function (botao) {
    botao.addEventListener("click", function () {
      enviar(botao.getAttribute("data-sugestao"));
    });
  });

  /* Deixa o abrir() disponível para outros scripts, se precisarem. */
  CV.abrirChat = abrir;
})();
