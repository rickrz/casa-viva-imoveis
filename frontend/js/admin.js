/* =====================================================================
   admin.js — painel administrativo (admin.html)
   ---------------------------------------------------------------------
   Áreas separadas:
     - visão geral: resumo + últimos contatos;
     - contatos: filtro, status, exclusão e exportação CSV;
     - minha conta: sessão e troca de senha.

   Rotas usadas:
     GET    /api/auth/sessao        -> quem está logado
     POST   /api/auth/logout        -> encerrar sessão
     POST   /api/auth/senha         -> trocar senha
     GET    /api/contatos           -> lista (protegida)
     PUT    /api/contatos/<id>      -> altera status (protegida)
     DELETE /api/contatos/<id>      -> exclui (protegida)
   ===================================================================== */
(function () {
  "use strict";

  var CV = window.CV;
  var requisitar = CV.requisitar;

  var corpoTabela = document.getElementById("corpoTabela");
  var estadoTabela = document.getElementById("estadoTabela");
  var filtro = document.getElementById("filtroStatus");
  var botaoAtualizar = document.getElementById("atualizar");
  var botaoAtualizarContatos = document.getElementById("atualizarContatos");
  var botaoExportar = document.getElementById("exportar");
  var horaAtualizacao = document.getElementById("ultimaAtualizacao");
  var listaUltimos = document.getElementById("ultimosContatos");

  var adminUsuario = document.getElementById("adminUsuario");
  var contaUsuario = document.getElementById("contaUsuario");
  var avisoTroca = document.getElementById("avisoTroca");
  var formSenha = document.getElementById("formSenha");
  var erroSenha = document.getElementById("erroSenha");
  var senhaAtual = document.getElementById("senhaAtual");
  var senhaNova = document.getElementById("senhaNova");
  var senhaConfirmacao = document.getElementById("senhaConfirmacao");
  var botaoSalvarSenha = formSenha.querySelector('[type="submit"]');
  var botoesMenu = document.querySelectorAll(".admin__menu-item");
  var botoesSair = document.querySelectorAll(".js-sair");

  var secoes = {
    visao: document.getElementById("secao-visao"),
    contatos: document.getElementById("secao-contatos"),
    conta: document.getElementById("secao-conta"),
  };

  var ROTULOS_STATUS = {
    novo: "Novo",
    em_atendimento: "Em atendimento",
    atendido: "Atendido",
  };

  var ROTULOS_INTERESSE = {
    comprar: "Comprar",
    alugar: "Alugar",
    vender: "Vender",
  };

  var contatos = [];

  /* -------------------------------------------------------------------
     Sessão e navegação entre as áreas
     ------------------------------------------------------------------- */
  function enderecoAtual() {
    return window.location.pathname + window.location.search;
  }

  function irParaLogin() {
    window.location.assign(
      "login.html?proxima=" + encodeURIComponent(enderecoAtual())
    );
  }

  /* Toda chamada protegida passa por aqui: sessão expirada volta ao login
     e senha temporária pendente abre a área de conta. */
  function requisitarAdmin(caminho, opcoes) {
    return requisitar(caminho, opcoes).catch(function (erro) {
      if (erro.status === 401) {
        irParaLogin();
      } else if (erro.status === 403 && erro.dados && erro.dados.trocar_senha) {
        mostrarSecao("conta");
        avisoTroca.hidden = false;
      }
      throw erro;
    });
  }

  function mostrarSecao(nome) {
    if (!secoes[nome]) nome = "visao";

    Object.keys(secoes).forEach(function (chave) {
      secoes[chave].hidden = chave !== nome;
    });

    Array.prototype.forEach.call(botoesMenu, function (botao) {
      var ativo = botao.getAttribute("data-secao") === nome;
      botao.classList.toggle("is-ativo", ativo);
      if (ativo) {
        botao.setAttribute("aria-current", "page");
      } else {
        botao.removeAttribute("aria-current");
      }
    });

    // No celular, focar o campo rola a página e esconde a navegação.
    if (nome === "conta" && !avisoTroca.hidden && window.innerWidth > 640) {
      senhaAtual.focus();
    }
  }

  async function verificarSessao() {
    try {
      var dados = await requisitar("/api/auth/sessao");
      if (!dados.autenticado) {
        irParaLogin();
        return false;
      }

      adminUsuario.textContent = dados.usuario || "administrador";
      contaUsuario.textContent = dados.usuario || "—";
      avisoTroca.hidden = !dados.trocar_senha;

      var parametros = new URLSearchParams(window.location.search);
      var secao = dados.trocar_senha ? "conta" : parametros.get("secao") || "visao";
      mostrarSecao(secao);
      return true;
    } catch (erro) {
      mostrarSecao("visao");
      return true;
    }
  }

  async function sair() {
    try {
      await requisitar("/api/auth/logout", { metodo: "POST" });
    } catch (erro) {
      /* Mesmo com erro de rede, limpamos a tela e voltamos ao login. */
    }
    window.location.assign("login.html");
  }

  async function alterarSenha(evento) {
    evento.preventDefault();
    erroSenha.textContent = "";

    if (senhaNova.value !== senhaConfirmacao.value) {
      erroSenha.textContent = "As senhas não coincidem.";
      return;
    }

    botaoSalvarSenha.disabled = true;
    try {
      await requisitarAdmin("/api/auth/senha", {
        metodo: "POST",
        dados: {
          senha_atual: senhaAtual.value,
          senha_nova: senhaNova.value,
        },
      });

      formSenha.reset();
      avisoTroca.hidden = true;
      CV.avisar("Senha alterada. Acesso liberado.");
      mostrarSecao("visao");
      carregar();
    } catch (erro) {
      if (!erro.dados || !erro.dados.trocar_senha) {
        erroSenha.textContent = erro.message;
      }
    } finally {
      botaoSalvarSenha.disabled = false;
    }
  }

  /* -------------------------------------------------------------------
     Carregar a lista
     ------------------------------------------------------------------- */
  async function carregar() {
    estadoTabela.hidden = false;
    estadoTabela.textContent = "Carregando contatos...";
    corpoTabela.innerHTML = "";

    try {
      var dados = await requisitarAdmin("/api/contatos");
      contatos = Array.isArray(dados) ? dados : [];
      renderizar();
      atualizarResumo();
      horaAtualizacao.textContent =
        "Atualizado às " +
        new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    } catch (erro) {
      if (erro.status === 401 || (erro.dados && erro.dados.trocar_senha)) return;
      estadoTabela.hidden = false;
      estadoTabela.innerHTML =
        "<strong>Não foi possível carregar os contatos.</strong><br />" +
        CV.escapar(erro.message);
    }
  }

  /* -------------------------------------------------------------------
     Visão geral: últimos 3 contatos
     ------------------------------------------------------------------- */
  function renderizarUltimos() {
    if (!contatos.length) {
      listaUltimos.innerHTML =
        '<p class="tabela__estado">Nenhum contato recebido ainda.</p>';
      return;
    }

    listaUltimos.innerHTML = contatos
      .slice(0, 3)
      .map(function (contato) {
        var status = ROTULOS_STATUS[contato.status] || contato.status;
        return (
          '<div class="lista-ultimos__item">' +
          "<div>" +
          '<div class="lista-ultimos__nome">' +
          CV.escapar(contato.nome) +
          "</div>" +
          '<div class="lista-ultimos__msg">' +
          CV.escapar(contato.mensagem || "—") +
          "</div>" +
          '<span class="lista-ultimos__hora">' +
          CV.data(contato.criado_em) +
          "</span>" +
          "</div>" +
          '<span class="estado estado--' +
          CV.escapar(contato.status) +
          '">' +
          CV.escapar(status) +
          "</span>" +
          "</div>"
        );
      })
      .join("");
  }

  /* -------------------------------------------------------------------
     Renderizar a tabela (com o filtro aplicado no navegador)
     ------------------------------------------------------------------- */
  function renderizar() {
    renderizarUltimos();

    var visiveis = filtro.value
      ? contatos.filter(function (contato) {
          return contato.status === filtro.value;
        })
      : contatos;

    if (!visiveis.length) {
      corpoTabela.innerHTML = "";
      estadoTabela.hidden = false;
      estadoTabela.textContent = contatos.length
        ? "Nenhum contato com esse status."
        : "Nenhum contato recebido ainda. Envie uma mensagem pelo site para testar.";
      return;
    }

    estadoTabela.hidden = true;

    corpoTabela.innerHTML = visiveis
      .map(function (contato) {
        return (
          "<tr>" +
          '<td data-rotulo="Contato">' +
          '<div class="tabela__pessoa">' +
          "<strong>" +
          CV.escapar(contato.nome) +
          "</strong>" +
          '<span class="tabela__secundario">' +
          CV.escapar(contato.email) +
          "</span>" +
          "</div></td>" +
          '<td data-rotulo="Telefone">' +
          CV.escapar(contato.telefone) +
          "</td>" +
          '<td data-rotulo="Interesse">' +
          '<span class="pilula pilula--' +
          CV.escapar(contato.tipo_interesse) +
          '">' +
          CV.escapar(ROTULOS_INTERESSE[contato.tipo_interesse] || contato.tipo_interesse) +
          "</span></td>" +
          '<td data-rotulo="Imóvel">' +
          (contato.imovel_codigo
            ? CV.escapar(contato.imovel_codigo) +
              '<br /><span class="tabela__secundario">' +
              CV.escapar(contato.imovel_titulo) +
              "</span>"
            : '<span class="tabela__secundario">Não informado</span>') +
          "</td>" +
          '<td data-rotulo="Mensagem">' +
          '<p class="tabela__mensagem">' +
          CV.escapar(contato.mensagem || "—") +
          "</p></td>" +
          '<td data-rotulo="Recebido em">' +
          CV.data(contato.criado_em) +
          "</td>" +
          '<td data-rotulo="Status">' +
          '<select class="tabela__status tabela__status--' +
          CV.escapar(contato.status) +
          '" data-id="' +
          contato.id +
          '" data-status-anterior="' +
          CV.escapar(contato.status) +
          '" aria-label="Alterar status do contato de ' +
          CV.escapar(contato.nome) +
          '">' +
          Object.keys(ROTULOS_STATUS)
            .map(function (valor) {
              return (
                '<option value="' +
                valor +
                '"' +
                (valor === contato.status ? " selected" : "") +
                ">" +
                ROTULOS_STATUS[valor] +
                "</option>"
              );
            })
            .join("") +
          "</select></td>" +
          '<td data-rotulo="Ações">' +
          '<button class="btn btn--perigo btn--pequeno" type="button" data-excluir="' +
          contato.id +
          '">Excluir</button>' +
          "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  /* -------------------------------------------------------------------
     Números do resumo
     ------------------------------------------------------------------- */
  function atualizarResumo() {
    document.getElementById("totalContatos").textContent = contatos.length;
    document.getElementById("totalNovos").textContent = contarPorStatus("novo");
    document.getElementById("totalAtendimento").textContent = contarPorStatus("em_atendimento");
    document.getElementById("totalAtendidos").textContent = contarPorStatus("atendido");
  }

  function contarPorStatus(status) {
    return contatos.filter(function (contato) {
      return contato.status === status;
    }).length;
  }

  /* -------------------------------------------------------------------
     Mudar o status (PUT com o contato completo)
     ------------------------------------------------------------------- */
  corpoTabela.addEventListener("change", async function (evento) {
    var select = evento.target.closest("select[data-id]");
    if (!select) return;

    var contato = contatos.find(function (item) {
      return String(item.id) === select.getAttribute("data-id");
    });
    if (!contato) return;

    var statusAnterior = contato.status;
    select.disabled = true;

    try {
      await requisitarAdmin("/api/contatos/" + contato.id, {
        metodo: "PUT",
        dados: {
          nome: contato.nome,
          email: contato.email,
          telefone: contato.telefone,
          tipo_interesse: contato.tipo_interesse,
          imovel_id: contato.imovel_id,
          mensagem: contato.mensagem,
          status: select.value,
        },
      });

      select.classList.remove("tabela__status--" + statusAnterior);
      select.classList.add("tabela__status--" + select.value);
      contato.status = select.value;
      atualizarResumo();
      renderizarUltimos();
      CV.avisar('Status alterado para "' + ROTULOS_STATUS[contato.status] + '".');

      // Se a lista está filtrada, a linha pode precisar sair da tela.
      if (filtro.value) renderizar();
    } catch (erro) {
      select.value = statusAnterior;
      CV.avisar(erro.message, "erro");
    } finally {
      select.disabled = false;
    }
  });

  /* -------------------------------------------------------------------
     Excluir
     ------------------------------------------------------------------- */
  corpoTabela.addEventListener("click", async function (evento) {
    var botao = evento.target.closest("[data-excluir]");
    if (!botao) return;

    var confirmou = window.confirm(
      "Excluir este contato definitivamente? Esta ação não pode ser desfeita."
    );
    if (!confirmou) return;

    var id = botao.getAttribute("data-excluir");
    botao.disabled = true;

    try {
      await requisitarAdmin("/api/contatos/" + id, { metodo: "DELETE" });

      contatos = contatos.filter(function (contato) {
        return String(contato.id) !== id;
      });

      renderizar();
      atualizarResumo();
      CV.avisar("Contato excluído.");
    } catch (erro) {
      botao.disabled = false;
      CV.avisar(erro.message, "erro");
    }
  });

  /* -------------------------------------------------------------------
     Exportar CSV (gerado no navegador, sem rota extra na API)
     Usamos ponto e vírgula e BOM para o Excel em português abrir certo.
     ------------------------------------------------------------------- */
  function exportarCsv() {
    if (!contatos.length) {
      CV.avisar("Não há contatos para exportar.", "erro");
      return;
    }

    var colunas = [
      "id",
      "nome",
      "email",
      "telefone",
      "tipo_interesse",
      "imovel_codigo",
      "mensagem",
      "status",
      "criado_em",
    ];

    function celula(valor) {
      var texto = valor === null || valor === undefined ? "" : String(valor);
      return '"' + texto.replace(/"/g, '""') + '"';
    }

    var linhas = [colunas.join(";")];

    contatos.forEach(function (contato) {
      linhas.push(
        colunas
          .map(function (coluna) {
            return celula(contato[coluna]);
          })
          .join(";")
      );
    });

    var csv = "\ufeff" + linhas.join("\r\n");
    var arquivo = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    var endereco = URL.createObjectURL(arquivo);

    var link = document.createElement("a");
    link.href = endereco;
    link.download = "casa-viva-contatos.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(endereco);

    CV.avisar("CSV gerado com " + contatos.length + " contatos.");
  }

  /* -------------------------------------------------------------------
     Ligações e carga inicial
     ------------------------------------------------------------------- */
  Array.prototype.forEach.call(botoesMenu, function (botao) {
    botao.addEventListener("click", function () {
      mostrarSecao(botao.getAttribute("data-secao"));
    });
  });

  Array.prototype.forEach.call(botoesSair, function (botao) {
    botao.addEventListener("click", sair);
  });

  document.getElementById("irContatos").addEventListener("click", function () {
    mostrarSecao("contatos");
  });
  document.getElementById("irConta").addEventListener("click", function () {
    mostrarSecao("conta");
  });

  filtro.addEventListener("change", renderizar);
  botaoAtualizar.addEventListener("click", carregar);
  botaoAtualizarContatos.addEventListener("click", carregar);
  botaoExportar.addEventListener("click", exportarCsv);
  formSenha.addEventListener("submit", alterarSenha);

  (async function iniciar() {
    var ok = await verificarSessao();
    if (ok) carregar();
  })();
})();
