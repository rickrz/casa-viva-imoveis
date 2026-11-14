/* =====================================================================
   site.js — comportamento da página inicial
   ---------------------------------------------------------------------
   Responsabilidades deste arquivo:
     1. Cabeçalho fixo que muda de cor ao rolar.
     2. Menu hambúrguer (abre/fecha a gaveta no celular).
     3. Marcar no menu a seção visível (IntersectionObserver).
     4. Buscar imóveis na API e montar os cards.
     5. Filtros (finalidade, tipo, cidade, quartos e busca por texto).
     6. Formulário de contato: validação + POST /api/contatos.
   ===================================================================== */
(function () {
  "use strict";

  var CV = window.CV;
  var requisitar = CV.requisitar;

  /* ===================================================================
     1. CABEÇALHO FIXO + MENU MOBILE
     =================================================================== */
  var header = document.querySelector(".header");
  var botaoMenu = document.getElementById("botaoMenu");
  var overlay = document.getElementById("overlay");
  var navegacao = document.getElementById("navegacao");
  var linksMenu = navegacao
    ? Array.prototype.slice.call(navegacao.querySelectorAll('a[href^="#"]'))
    : [];

  function atualizarHeader() {
    header.classList.toggle("rolado", window.scrollY > 24);
  }

  function abrirMenu() {
    document.body.classList.add("menu-aberto");
    header.classList.add("menu-aberto");
    botaoMenu.setAttribute("aria-expanded", "true");
    botaoMenu.setAttribute("aria-label", "Fechar menu");
  }

  function fecharMenu() {
    document.body.classList.remove("menu-aberto");
    header.classList.remove("menu-aberto");
    botaoMenu.setAttribute("aria-expanded", "false");
    botaoMenu.setAttribute("aria-label", "Abrir menu");
  }

  botaoMenu.addEventListener("click", function () {
    if (document.body.classList.contains("menu-aberto")) {
      fecharMenu();
    } else {
      abrirMenu();
    }
  });

  overlay.addEventListener("click", fecharMenu);

  linksMenu.forEach(function (link) {
    link.addEventListener("click", fecharMenu);
  });

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") fecharMenu();
  });

  window.addEventListener(
    "resize",
    function () {
      if (window.innerWidth > 980) fecharMenu();
    },
    { passive: true }
  );

  atualizarHeader();
  window.addEventListener("scroll", atualizarHeader, { passive: true });

  /* ===================================================================
     2. LINK ATIVO CONFORME A SEÇÃO VISÍVEL
     =================================================================== */
  if ("IntersectionObserver" in window) {
    var observador = new IntersectionObserver(
      function (entradas) {
        entradas.forEach(function (entrada) {
          if (!entrada.isIntersecting) return;
          var alvo = "#" + entrada.target.id;
          linksMenu.forEach(function (link) {
            link.classList.toggle("ativo", link.getAttribute("href") === alvo);
          });
        });
      },
      // A faixa central da tela define qual seção está "ativa".
      { rootMargin: "-45% 0px -50% 0px" }
    );

    // Só as seções do conteúdo principal (o widget de chat também é um
    // <section>, mas não tem link no menu).
    document.querySelectorAll("main section[id]").forEach(function (secao) {
      observador.observe(secao);
    });
  }

  /* ===================================================================
     3. ÍCONES USADOS NOS CARDS (SVG inline, sem biblioteca)
     =================================================================== */
  var CAMINHOS_ICONE = {
    cama:
      '<path d="M3 18v-6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6"/><path d="M3 18h18M7 10V7a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v3"/>',
    banheiro:
      '<path d="M4 12h16v3a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-3z"/><path d="M6 12V6a2 2 0 0 1 4 0"/>',
    carro:
      '<path d="m5 12 1.5-4.5A2 2 0 0 1 8.4 6h7.2a2 2 0 0 1 1.9 1.5L19 12"/><path d="M4 12h16v5H4z"/><circle cx="7.5" cy="17.5" r="1.5"/><circle cx="16.5" cy="17.5" r="1.5"/>',
    area:
      '<path d="M4 9V4h5M20 15v5h-5M15 4h5v5M9 20H4v-5"/>',
    local:
      '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
  };

  function icone(nome) {
    return (
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      CAMINHOS_ICONE[nome] +
      "</svg>"
    );
  }

  /* ===================================================================
     4. LISTA DE IMÓVEIS
     =================================================================== */
  var lista = document.getElementById("listaImoveis");
  var estado = document.getElementById("estado");
  var contador = document.getElementById("contadorImoveis");
  var formFiltros = document.getElementById("filtros");
  var campoBusca = document.getElementById("f-busca");
  var relogioBusca = null;

  /* Lê os campos e monta a query string: ?finalidade=venda&tipo=Casa... */
  function parametrosFiltro() {
    var parametros = new URLSearchParams();

    function valor(id) {
      var campo = document.getElementById(id);
      return campo ? campo.value.trim() : "";
    }

    if (valor("f-finalidade")) parametros.set("finalidade", valor("f-finalidade"));
    if (valor("f-tipo")) parametros.set("tipo", valor("f-tipo"));
    if (valor("f-cidade")) parametros.set("cidade", valor("f-cidade"));
    if (valor("f-quartos")) parametros.set("quartos_min", valor("f-quartos"));
    if (valor("f-busca")) parametros.set("q", valor("f-busca"));

    parametros.set("limite", "60");
    return parametros.toString();
  }

  function esqueletos() {
    var html = "";
    for (var i = 0; i < 6; i += 1) html += '<div class="esqueleto"></div>';
    lista.innerHTML = html;
    estado.hidden = true;
  }

  function mostrarEstado(titulo, texto, comBotao) {
    lista.innerHTML = "";
    estado.hidden = false;
    estado.innerHTML =
      "<h3>" +
      titulo +
      "</h3><p>" +
      texto +
      "</p>" +
      (comBotao
        ? '<button class="btn btn--contorno" type="button" id="tentarNovamente">Tentar novamente</button>'
        : "");

    var botao = document.getElementById("tentarNovamente");
    if (botao) botao.addEventListener("click", carregarImoveis);
  }

  async function carregarImoveis() {
    esqueletos();

    try {
      var dados = await requisitar("/api/imoveis?" + parametrosFiltro());

      if (!dados.length) {
        contador.textContent = "";
        mostrarEstado(
          "Nenhum imóvel com esses filtros",
          "Tente outra cidade, outro tipo ou limpe os filtros para ver a carteira inteira.",
          false
        );
        return;
      }

      contador.textContent =
        dados.length + (dados.length === 1 ? " imóvel encontrado" : " imóveis encontrados");
      lista.innerHTML = dados.map(montarCartao).join("");
      estado.hidden = true;
    } catch (erro) {
      contador.textContent = "";
      mostrarEstado(
        "Não conseguimos carregar os imóveis",
        CV.escapar(erro.message),
        true
      );
    }
  }

  /* Monta o HTML de um card. Os dados vêm do banco, por isso escapamos. */
  function montarCartao(imovel) {
    var aluguel = imovel.finalidade === "aluguel";
    var ficha = [];

    if (Number(imovel.quartos) > 0) {
      ficha.push("<li>" + icone("cama") + imovel.quartos + " quartos</li>");
    }
    if (Number(imovel.banheiros) > 0) {
      ficha.push("<li>" + icone("banheiro") + imovel.banheiros + " banh.</li>");
    }
    if (Number(imovel.vagas) > 0) {
      ficha.push("<li>" + icone("carro") + imovel.vagas + " vagas</li>");
    }
    ficha.push(
      "<li>" +
        icone("area") +
        Number(imovel.area_m2).toLocaleString("pt-BR") +
        " m²</li>"
    );

    return (
      '<article class="cartao">' +
      '<div class="cartao__foto">' +
      '<img src="' +
      CV.escapar(imovel.imagem_url || "img/sem-foto.svg") +
      '" alt="' +
      CV.escapar(imovel.titulo) +
      '" loading="lazy" />' +
      '<span class="etiqueta' +
      (aluguel ? " etiqueta--aluguel" : "") +
      '">' +
      (aluguel ? "Aluguel" : "Venda") +
      "</span>" +
      '<span class="etiqueta etiqueta--codigo">' +
      CV.escapar(imovel.codigo) +
      "</span>" +
      "</div>" +
      '<div class="cartao__corpo">' +
      '<p class="cartao__local">' +
      icone("local") +
      CV.escapar(imovel.tipo + " · " + imovel.bairro + ", " + imovel.cidade + "/" + imovel.uf) +
      "</p>" +
      '<h3 class="cartao__titulo">' +
      CV.escapar(imovel.titulo) +
      "</h3>" +
      '<ul class="cartao__ficha">' +
      ficha.join("") +
      "</ul>" +
      '<div class="cartao__rodape">' +
      '<p class="cartao__preco">' +
      CV.preco(imovel.preco) +
      "<small>" +
      (aluguel ? "por mês" : "à vista ou financiado") +
      "</small></p>" +
      '<button class="btn btn--contorno btn--pequeno" type="button" data-interesse="' +
      imovel.id +
      '" data-finalidade="' +
      imovel.finalidade +
      '">Tenho interesse</button>' +
      "</div>" +
      "</div>" +
      "</article>"
    );
  }

  /* ===================================================================
     5. DESTAQUE DO HERO
     =================================================================== */
  async function carregarDestaque() {
    var caixa = document.getElementById("destaque");
    if (!caixa) return;

    try {
      var dados = await requisitar("/api/imoveis?destaque=1&limite=1");
      var imovel = dados[0];
      if (!imovel) return;

      caixa.innerHTML =
        '<article class="destaque__cartao">' +
        '<div class="destaque__foto">' +
        '<img src="' +
        CV.escapar(imovel.imagem_url || "img/sem-foto.svg") +
        '" alt="' +
        CV.escapar(imovel.titulo) +
        '" loading="lazy" />' +
        '<span class="etiqueta">Destaque</span>' +
        "</div>" +
        '<div class="destaque__corpo">' +
        '<p class="destaque__rotulo">Seleção da semana</p>' +
        '<h2 class="destaque__titulo">' +
        CV.escapar(imovel.titulo) +
        "</h2>" +
        '<p class="destaque__local">' +
        CV.escapar(imovel.bairro + ", " + imovel.cidade + "/" + imovel.uf) +
        "</p>" +
        '<div class="destaque__rodape">' +
        '<p class="destaque__preco">' +
        CV.preco(imovel.preco) +
        "<small>" +
        (imovel.finalidade === "aluguel" ? "por mês" : "venda") +
        "</small></p>" +
        '<button class="btn btn--contorno btn--pequeno" type="button" data-interesse="' +
        imovel.id +
        '" data-finalidade="' +
        imovel.finalidade +
        '">Tenho interesse</button>' +
        "</div>" +
        "</div>" +
        "</article>";

      caixa.hidden = false;
    } catch (erro) {
      // Se o destaque falhar, o hero continua funcionando sem o cartão.
      caixa.hidden = true;
    }
  }

  /* ===================================================================
     6. SELECTS: TIPOS, CIDADES E IMÓVEIS
     =================================================================== */
  function preencherSelect(id, itens, rotuloTodos, formatar) {
    var select = document.getElementById(id);
    if (!select) return;

    var html = '<option value="">' + rotuloTodos + "</option>";
    itens.forEach(function (item) {
      var texto = formatar ? formatar(item) : item.nome;
      html += '<option value="' + CV.escapar(item.nome) + '">' + CV.escapar(texto) + "</option>";
    });
    select.innerHTML = html;
  }

  async function carregarOpcoes() {
    try {
      var dados = await requisitar("/api/imoveis/opcoes");
      preencherSelect("f-tipo", dados.tipos, "Todos os tipos");
      preencherSelect("f-cidade", dados.cidades, "Todas as cidades", function (cidade) {
        return cidade.nome + " (" + cidade.uf + ")";
      });
    } catch (erro) {
      // Os filtros ficam só com a opção "Todos"; os cards ainda carregam.
      console.warn("Não foi possível carregar as opções de filtro:", erro.message);
    }
  }

  /* O select do formulário usa o código do imóvel (CV-001) para o usuário
     identificar rápido qual imóvel despertou o interesse. */
  async function carregarImoveisDoFormulario() {
    var select = document.getElementById("imovel_id");
    if (!select) return;

    try {
      var dados = await requisitar("/api/imoveis?limite=200");
      var html = '<option value="">Ainda não sei / quero falar com a equipe</option>';

      dados.forEach(function (imovel) {
        html +=
          '<option value="' +
          imovel.id +
          '">' +
          CV.escapar(imovel.codigo + " · " + imovel.titulo) +
          "</option>";
      });

      select.innerHTML = html;
    } catch (erro) {
      console.warn("Não foi possível carregar os imóveis no formulário:", erro.message);
    }
  }

  /* ===================================================================
     7. "TENHO INTERESSE" -> seleciona o imóvel e rola até o formulário
     =================================================================== */
  document.addEventListener("click", function (evento) {
    var botao = evento.target.closest("[data-interesse]");
    if (!botao) return;

    var id = botao.getAttribute("data-interesse");
    var finalidade = botao.getAttribute("data-finalidade");
    var select = document.getElementById("imovel_id");

    if (select) {
      select.value = id;
      select.closest(".campo").classList.remove("campo--invalido");
      var erro = document.querySelector('[data-erro="imovel_id"]');
      if (erro) erro.textContent = "";
    }

    /* Pré-seleciona "comprar" ou "alugar" conforme o imóvel clicado.
       Não sobrescreve "vender", que é uma intenção independente do card. */
    var interesse = document.getElementById("tipo_interesse");
    if (interesse && finalidade && interesse.value !== "vender") {
      interesse.value = finalidade === "aluguel" ? "alugar" : "comprar";
      interesse.closest(".campo").classList.remove("campo--invalido");
      var erroInteresse = document.querySelector('[data-erro="tipo_interesse"]');
      if (erroInteresse) erroInteresse.textContent = "";
    }

    var local = document.getElementById("contato");
    if (local) local.scrollIntoView({ behavior: "smooth", block: "start" });

    CV.avisar("Imóvel selecionado no formulário. Agora é só preencher seus dados.");

    setTimeout(function () {
      var nome = document.getElementById("nome");
      if (nome) nome.focus({ preventScroll: true });
    }, 700);
  });

  /* ===================================================================
     8. EVENTOS DOS FILTROS
     =================================================================== */
  ["f-finalidade", "f-tipo", "f-cidade", "f-quartos"].forEach(function (id) {
    var campo = document.getElementById(id);
    if (campo) campo.addEventListener("change", carregarImoveis);
  });

  // Espera a pessoa parar de digitar por 350 ms antes de consultar a API.
  campoBusca.addEventListener("input", function () {
    clearTimeout(relogioBusca);
    relogioBusca = setTimeout(carregarImoveis, 350);
  });

  formFiltros.addEventListener("reset", function () {
    clearTimeout(relogioBusca);
    setTimeout(carregarImoveis, 0); // roda depois que os campos forem limpos
  });

  /* ===================================================================
     9. FORMULÁRIO DE CONTATO
     =================================================================== */
  var formulario = document.getElementById("formContato");
  var feedback = document.getElementById("feedback");
  var botaoEnviar = document.getElementById("botaoEnviar");
  var campoTelefone = document.getElementById("telefone");

  campoTelefone.addEventListener("input", function () {
    campoTelefone.value = CV.mascararTelefone(campoTelefone.value);
  });

  function limparErros() {
    formulario.querySelectorAll(".campo--invalido").forEach(function (campo) {
      campo.classList.remove("campo--invalido");
    });
    formulario.querySelectorAll("[data-erro]").forEach(function (alvo) {
      alvo.textContent = "";
    });
  }

  function marcarErro(nomeDoCampo, mensagem) {
    var campo = formulario.elements[nomeDoCampo];
    if (campo) {
      var caixa = campo.closest(".campo");
      if (caixa) caixa.classList.add("campo--invalido");
    }
    var alvo = formulario.querySelector('[data-erro="' + nomeDoCampo + '"]');
    if (alvo) alvo.textContent = mensagem;
  }

  function mostrarFeedback(tipo, mensagem) {
    feedback.hidden = false;
    feedback.className = "feedback feedback--" + tipo;
    feedback.textContent = mensagem;
  }

  /* Repetimos no navegador as regras principais do validacao.py para a
     pessoa receber o aviso na hora, sem esperar a resposta da API. */
  function validarNoNavegador(dados) {
    var erros = {};

    if (dados.nome.trim().length < 3) {
      erros.nome = "Informe seu nome completo (mínimo de 3 caracteres).";
    }

    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(dados.email.trim())) {
      erros.email = "Informe um e-mail válido.";
    }

    var telefone = CV.digitos(dados.telefone);
    if (telefone.length < 10 || telefone.length > 13) {
      erros.telefone = "Informe o telefone com DDD (10 a 13 dígitos).";
    }

    if (["comprar", "alugar", "vender"].indexOf(dados.tipo_interesse) === -1) {
      erros.tipo_interesse = "Escolha se você quer comprar, alugar ou vender.";
    }

    if (dados.mensagem.length > 2000) {
      erros.mensagem = "A mensagem deve ter no máximo 2000 caracteres.";
    }

    return erros;
  }

  formulario.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    limparErros();
    feedback.hidden = true;

    // Object.fromEntries transforma o FormData em um objeto simples.
    var dados = Object.fromEntries(new FormData(formulario).entries());
    var erros = validarNoNavegador(dados);

    if (Object.keys(erros).length > 0) {
      Object.keys(erros).forEach(function (campo) {
        marcarErro(campo, erros[campo]);
      });
      mostrarFeedback("erro", "Confira os campos destacados antes de enviar.");
      var primeiro = formulario.querySelector(".campo--invalido input, .campo--invalido select, .campo--invalido textarea");
      if (primeiro) primeiro.focus();
      return;
    }

    var corpo = {
      nome: dados.nome.trim(),
      email: dados.email.trim().toLowerCase(),
      telefone: dados.telefone.trim(),
      tipo_interesse: dados.tipo_interesse,
      imovel_id: dados.imovel_id ? Number(dados.imovel_id) : null,
      mensagem: dados.mensagem.trim() || null,
    };

    botaoEnviar.disabled = true;
    botaoEnviar.textContent = "Enviando...";

    try {
      var resposta = await requisitar("/api/contatos", { metodo: "POST", dados: corpo });

      mostrarFeedback(
        "sucesso",
        resposta.mensagem || "Contato registrado com sucesso! Em breve falaremos com você."
      );
      formulario.reset();
      CV.avisar("Mensagem enviada!");
    } catch (erro) {
      // A API devolve { erros: { campo: "mensagem" } } quando a validação falha.
      if (erro.dados && erro.dados.erros) {
        Object.keys(erro.dados.erros).forEach(function (campo) {
          marcarErro(campo, erro.dados.erros[campo]);
        });
      }
      mostrarFeedback("erro", erro.message);
    } finally {
      botaoEnviar.disabled = false;
      botaoEnviar.textContent = "Enviar mensagem";
    }
  });

  /* ===================================================================
     10. INICIALIZAÇÃO
     =================================================================== */
  document.getElementById("anoAtual").textContent = new Date().getFullYear();

  carregarOpcoes();
  carregarDestaque();
  carregarImoveis();
  carregarImoveisDoFormulario();
})();
