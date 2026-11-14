/* =====================================================================
   banco.js — página "Banco de dados" (banco.html)
   ---------------------------------------------------------------------
   Único comportamento dinâmico da página: o botão "Copiar" de cada
   consulta. Isso ajuda na apresentação — dá para colar direto no SQL
   Editor do Neon sem selecionar o texto à mão.

   Tudo o mais na página é estático (HTML + CSS).
   ===================================================================== */
(function () {
  "use strict";

  var botoes = document.querySelectorAll("[data-copiar]");

  /* Cópia pelo método clássico (<textarea> + execCommand).
     Serve de reserva quando a Clipboard API não existe (file://, http)
     ou quando ela recusa a operação (aba sem foco, por exemplo). */
  function copiarComTextarea(texto) {
    return new Promise(function (resolver, rejeitar) {
      var area = document.createElement("textarea");
      area.value = texto;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();

      try {
        var copiou = document.execCommand("copy");
        if (copiou) {
          resolver();
        } else {
          rejeitar(new Error("execCommand não copiou"));
        }
      } catch (erro) {
        rejeitar(erro);
      } finally {
        document.body.removeChild(area);
      }
    });
  }

  /* Copia um texto para a área de transferência, tentando primeiro a
     Clipboard API (mais moderna) e caindo no método clássico se falhar. */
  function copiar(texto) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(texto).catch(function () {
        return copiarComTextarea(texto);
      });
    }

    return copiarComTextarea(texto);
  }

  botoes.forEach(function (botao) {
    botao.addEventListener("click", function () {
      /* O código fica no <code> do mesmo cartão .consulta. */
      var cartao = botao.closest(".consulta");
      var codigo = cartao ? cartao.querySelector("code") : null;

      if (!codigo) {
        return;
      }

      var rotuloOriginal = botao.textContent;

      copiar(codigo.textContent).then(
        function () {
          botao.textContent = "Copiado!";
          setTimeout(function () {
            botao.textContent = rotuloOriginal;
          }, 1600);
        },
        function () {
          botao.textContent = "Não foi possível";
          setTimeout(function () {
            botao.textContent = rotuloOriginal;
          }, 1600);
        }
      );
    });
  });
})();
