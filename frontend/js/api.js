/* =====================================================================
   api.js — ponte entre o front-end e a API Flask
   ---------------------------------------------------------------------
   Este arquivo é carregado antes de site.js, chat.js e admin.js.
   Ele expõe um objeto global `window.CV` com:

     CV.requisitar(caminho, { metodo, dados })  -> fetch + tratamento de erro
     CV.preco(valor)                           -> R$ 1.250.000
     CV.data(valor)                            -> 13/11/2026 14:30
     CV.escapar(texto)                         -> protege o HTML
     CV.digitos(texto)                         -> só números
     CV.mascararTelefone(texto)                -> (11) 98888-1111
     CV.avisar(mensagem)                       -> aviso rápido na tela

   Por que não usamos módulos ES (import/export)? Porque assim o site
   funciona mesmo aberto por file:// durante os testes.
   ===================================================================== */
(function () {
  "use strict";

  /* -------------------------------------------------------------------
     ONDE A API ESTÁ?
     1. Se a página definiu window.CASAVIVA_API_URL, usamos ela (deploy
        com front separado da API).
     2. Se o site foi aberto por um arquivo local (file://) ou pelo Live
        Server (porta 5500), apontamos para o Flask local em
        http://127.0.0.1:5000.
     3. Em qualquer outro caso (o próprio Flask servindo o site, tanto na
        porta 5000 quanto no Render em HTTPS), usamos a MESMA ORIGEM e
        basta "/api/...".
     ------------------------------------------------------------------- */
  var API_BASE = (function () {
    var configurada = String(window.CASAVIVA_API_URL || "").trim();
    if (configurada) {
      return configurada.replace(/\/+$/, ""); // remove barra final
    }
    var paginaLocal =
      window.location.protocol === "file:" ||
      window.location.port === "5500";
    if (paginaLocal) {
      return "http://127.0.0.1:5000";
    }
    return ""; // mesma origem: /api/...
  })();

  /* -------------------------------------------------------------------
     REQUISIÇÃO
     Devolve o JSON já convertido. Se a resposta vier com erro HTTP,
     lança um Error com .status e .dados (útil para mostrar os campos
     inválidos que a API devolve em `erros`).
     ------------------------------------------------------------------- */
  async function requisitar(caminho, opcoes) {
    var config = opcoes || {};
    var metodo = config.metodo || "GET";
    var init = {
      method: metodo,
      headers: { Accept: "application/json" },
    };

    if (config.dados !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(config.dados);
    }

    var resposta;
    try {
      resposta = await fetch(API_BASE + caminho, init);
    } catch (falha) {
      throw new Error(
        "Não foi possível falar com a API. Verifique se o Flask está rodando em " +
          (API_BASE || window.location.origin) +
          "."
      );
    }

    // 204 (No Content) não tem corpo: nada para converter.
    var corpo = null;
    if (resposta.status !== 204) {
      var texto = await resposta.text();
      try {
        corpo = texto ? JSON.parse(texto) : null;
      } catch (falha) {
        corpo = null;
      }
    }

    if (!resposta.ok) {
      var mensagem =
        (corpo && (corpo.erro || corpo.mensagem)) ||
        "A API respondeu com o código " + resposta.status + ".";
      var erro = new Error(mensagem);
      erro.status = resposta.status;
      erro.dados = corpo;
      throw erro;
    }

    return corpo;
  }

  /* -------------------------------------------------------------------
     FORMATAÇÃO
     ------------------------------------------------------------------- */
  var formatoMoeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  });

  var formatoData = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  });

  function preco(valor) {
    var numero = Number(valor);
    return Number.isFinite(numero) ? formatoMoeda.format(numero) : "—";
  }

  function data(valor) {
    if (!valor) return "—";
    var d = new Date(valor);
    return isNaN(d.getTime()) ? "—" : formatoData.format(d);
  }

  /* Evita que um título vindo do banco quebre o HTML. */
  var TROCAS = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

  function escapar(texto) {
    return String(texto === null || texto === undefined ? "" : texto).replace(
      /[&<>"']/g,
      function (caractere) {
        return TROCAS[caractere];
      }
    );
  }

  function digitos(texto) {
    return String(texto || "").replace(/\D/g, "");
  }

  /* Máscara simples de telefone brasileiro: (11) 98888-1111 */
  function mascararTelefone(texto) {
    var n = digitos(texto).slice(0, 11);
    if (!n) return "";
    if (n.length <= 2) return "(" + n;
    if (n.length <= 6) return "(" + n.slice(0, 2) + ") " + n.slice(2);
    if (n.length <= 10) {
      return "(" + n.slice(0, 2) + ") " + n.slice(2, 6) + "-" + n.slice(6);
    }
    return "(" + n.slice(0, 2) + ") " + n.slice(2, 7) + "-" + n.slice(7);
  }

  /* -------------------------------------------------------------------
     AVISO RÁPIDO (usa o <div id="toast"> presente nas páginas)
     ------------------------------------------------------------------- */
  var relogioAviso = null;

  function avisar(mensagem, tipo) {
    var caixa = document.getElementById("toast");
    if (!caixa) return;
    caixa.textContent = mensagem;
    caixa.className = "toast visivel" + (tipo === "erro" ? " toast--erro" : "");
    clearTimeout(relogioAviso);
    relogioAviso = setTimeout(function () {
      caixa.className = "toast";
    }, 4000);
  }

  /* Tudo o que os outros scripts precisam fica aqui. */
  window.CV = {
    API_BASE: API_BASE,
    requisitar: requisitar,
    preco: preco,
    data: data,
    escapar: escapar,
    digitos: digitos,
    mascararTelefone: mascararTelefone,
    avisar: avisar,
  };
})();
