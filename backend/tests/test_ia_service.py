"""
Testes automatizados do assistente Lia (services/ia_service.py).

Os testes NÃO acessam o banco nem o Gemini: verificam as funções puras
(formatação de preço, montagem do prompt, sanitização do histórico) e os
caminhos de erro da função `responder`.

Como rodar (dentro da pasta backend):

    python -m unittest discover -s tests -v
"""

import unittest
from unittest import mock

from config import Config
from services import ia_service


class TesteFormatarPreco(unittest.TestCase):
    """`_formatar_preco` deve virar texto em reais, sem depender de locale."""

    def test_formata_numero(self):
        self.assertEqual(ia_service._formatar_preco(1250000), "R$ 1.250.000,00")

    def test_valor_invalido_vira_sob_consulta(self):
        self.assertEqual(ia_service._formatar_preco(None), "sob consulta")
        self.assertEqual(ia_service._formatar_preco("abc"), "sob consulta")


class TesteNormalizarHistorico(unittest.TestCase):
    """O histórico vindo do navegador é dado não confiável: precisa ser limpo."""

    def test_descarta_invalidos_e_junta_papeis_repetidos(self):
        historico = [
            "texto solto",                                   # não é dict
            {"papel": "model", "texto": "model no começo"},  # começaria por model
            {"papel": "user", "texto": "oi"},                # ok
            {"papel": "user", "texto": ""},                  # vazio
            {"papel": "user", "texto": "de novo"},           # junta com o anterior
            {"papel": "model", "texto": "olá"},              # ok
        ]
        limpo = ia_service._normalizar_historico(historico)

        self.assertEqual([mensagem["role"] for mensagem in limpo], ["user", "model"])
        self.assertIn("de novo", limpo[0]["parts"][0]["text"])

    def test_nao_lista_vira_lista_vazia(self):
        self.assertEqual(ia_service._normalizar_historico("nada"), [])

    def test_limita_tamanho_de_cada_mensagem(self):
        enorme = "x" * 5000
        limpo = ia_service._normalizar_historico([{"papel": "user", "texto": enorme}])
        self.assertEqual(len(limpo[0]["parts"][0]["text"]), ia_service.LIMITE_TEXTO_HISTORICO)


class TestePrompt(unittest.TestCase):
    """O prompt precisa conter a persona e a carteira real do banco."""

    def test_prompt_inclui_persona_e_imovel(self):
        imovel = {
            "codigo": "CV-999",
            "titulo": "Casa de teste",
            "descricao": "casa de teste para o unittest",
            "tipo": "Casa",
            "bairro": "Centro",
            "cidade": "Testópolis",
            "uf": "SP",
            "finalidade": "venda",
            "preco": 100000,
            "quartos": 2,
            "banheiros": 1,
            "vagas": 1,
            "area_m2": 80,
        }
        prompt = ia_service._montar_prompt([imovel])

        self.assertIn("Lia", prompt)
        self.assertIn("Casa Viva", prompt)
        self.assertIn("CV-999", prompt)
        self.assertIn("Testópolis", prompt)

    def test_prompt_sem_imoveis_avisa_que_nao_ha_carteira(self):
        prompt = ia_service._montar_prompt([])
        self.assertIn("Nenhum imóvel disponível", prompt)


class TesteListaModelos(unittest.TestCase):
    """Principal + reservas, sem repetir o mesmo modelo."""

    def test_nao_repete_modelos(self):
        with mock.patch.object(
            Config, "GEMINI_MODEL_FALLBACKS",
            [Config.GEMINI_MODEL, "gemini-3.5-flash-lite"],
        ):
            modelos = ia_service._lista_modelos()

        self.assertEqual(len(modelos), len(set(modelos)))
        self.assertGreaterEqual(len(modelos), 1)


class TesteResponder(unittest.TestCase):
    """Caminhos de erro da função de entrada, sem tocar na rede."""

    def test_mensagem_vazia_devolve_400(self):
        payload, codigo = ia_service.responder("   ")
        self.assertEqual(codigo, 400)
        self.assertFalse(payload["ok"])

    def test_sem_chave_devolve_503_com_mensagem_amigavel(self):
        with mock.patch.object(ia_service, "_buscar_imoveis", return_value=[]):
            with mock.patch.object(Config, "GEMINI_API_KEY", ""):
                payload, codigo = ia_service.responder("Olá")

        self.assertEqual(codigo, 503)
        self.assertFalse(payload["ok"])
        self.assertIn("formulário", payload["resposta"])


if __name__ == "__main__":
    unittest.main()
