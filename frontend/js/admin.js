/* =====================================================================
   admin.js — painel de contatos (admin.html)
   ---------------------------------------------------------------------
   Demonstra ao vivo, na apresentação, que o formulário do site grava no
   PostgreSQL:

     GET    /api/contatos        -> lista (usada ao abrir a página)
     PUT    /api/contatos/<id>   -> altera o status
     DELETE /api/contatos/<id>   -> exclui o registro

   Observação: a rota PUT valida o contato inteiro, por isso enviamos
   todos os campos (e não só o status).
   ===================================================================== */
(function () {
  "use strict";

  var CV = window.CV;
  var requisitar = CV.requisitar;

  var corpoTabela = document.getElementById("corpoTabela");
  var estadoTabela = document.getElementById("estadoTabela");
  var filtro = document.getElementById("filtroStatus");
  var botaoAtualizar = document.getElementById("atualizar");
  var botaoExportar = document.getElementById("exportar");
  var horaAtualizacao = document.getElementById("ultimaAtualizacao");

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
     Carregar a lista
     ------------------------------------------------------------------- */
  async function carregar() {
    estadoTabela.hidden = false;
    estadoTabela.textContent = "Carregando contatos...";
    corpoTabela.innerHTML = "";

    try {
      var dados = await requisitar("/api/contatos");
      contatos = Array.isArray(dados) ? dados : [];
      renderizar();
      atualizarResumo();
      horaAtualizacao.textContent =
        "Atualizado às " +
        new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    } catch (erro) {
      estadoTabela.hidden = false;
      estadoTabela.innerHTML =
        "<strong>Não foi possível carregar os contatos.</strong><br />" +
        CV.escapar(erro.message);
    }
  }

  /* -------------------------------------------------------------------
     Renderizar a tabela (com o filtro de status aplicado no navegador)
     ------------------------------------------------------------------- */
  function renderizar() {
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
     Números do topo
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
      await requisitar("/api/contatos/" + contato.id, {
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
      await requisitar("/api/contatos/" + id, { metodo: "DELETE" });

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
  filtro.addEventListener("change", renderizar);
  botaoAtualizar.addEventListener("click", carregar);
  botaoExportar.addEventListener("click", exportarCsv);

  carregar();
})();
