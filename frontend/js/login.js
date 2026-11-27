/* =====================================================================
   login.js — acesso ao painel administrativo
   ---------------------------------------------------------------------
   Usa apenas a API pública de autenticação:
     GET  /api/auth/sessao  -> se já estiver logado, segue direto
     POST /api/auth/login   -> cria a sessão com cookie HttpOnly
   ===================================================================== */
(function () {
  "use strict";

  var CV = window.CV;
  var form = document.getElementById("formLogin");
  var campoUsuario = document.getElementById("usuario");
  var campoSenha = document.getElementById("senha");
  var botaoMostrar = document.getElementById("mostrarSenha");
  var botaoEntrar = document.getElementById("entrar");
  var erro = document.getElementById("erroLogin");

  /* Evita redirecionamento para um site externo via ?proxima=. */
  function destinoSeguro(valor) {
    if (!valor) return "admin.html";
    if (valor === "admin.html" || valor === "banco.html") return valor;
    if (/^\/(?!\/)/.test(valor)) return valor;
    return "admin.html";
  }

  var proxima = destinoSeguro(
    new URLSearchParams(window.location.search).get("proxima")
  );

  function redirecionar(trocarSenha) {
    window.location.replace(
      trocarSenha ? "admin.html?secao=conta" : proxima
    );
  }

  async function verificarSessao() {
    try {
      var dados = await CV.requisitar("/api/auth/sessao");
      if (dados.autenticado) redirecionar(dados.trocar_senha);
    } catch (falha) {
      /* Sem sessão (ou API fora do ar) seguimos com o formulário. */
    }
  }

  botaoMostrar.addEventListener("click", function () {
    var visivel = campoSenha.type === "text";
    campoSenha.type = visivel ? "password" : "text";
    botaoMostrar.textContent = visivel ? "Mostrar" : "Ocultar";
    botaoMostrar.setAttribute("aria-label", visivel ? "Mostrar senha" : "Ocultar senha");
  });

  form.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    erro.textContent = "";

    var usuario = campoUsuario.value.trim();
    var senha = campoSenha.value;

    if (!usuario || !senha) {
      erro.textContent = "Informe usuário e senha.";
      return;
    }

    botaoEntrar.disabled = true;
    botaoEntrar.textContent = "Entrando...";

    try {
      var dados = await CV.requisitar("/api/auth/login", {
        metodo: "POST",
        dados: { usuario: usuario, senha: senha },
      });
      CV.avisar("Acesso liberado, " + (dados.nome || dados.usuario) + "!");
      redirecionar(dados.trocar_senha);
    } catch (falha) {
      erro.textContent = falha.message;
      botaoEntrar.disabled = false;
      botaoEntrar.textContent = "Entrar no painel";
      campoSenha.select();
    }
  });

  verificarSessao();
})();
