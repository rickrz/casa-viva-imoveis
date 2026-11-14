"""
Validações dos dados recebidos pela API.

Concentrar as regras aqui deixa as rotas mais curtas e fáceis de explicar.
Cada função devolve uma dupla `(dados_limpos, erros)`:
- se `erros` estiver vazio, os dados podem ir para o banco;
- se houver erros, a rota responde 400 com o dicionário de mensagens.
"""

import re
from decimal import Decimal, InvalidOperation

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CODIGO = re.compile(r"^[A-Z0-9-]+$")

TIPOS_INTERESSE = {"comprar", "alugar", "vender"}
STATUS_CONTATO = {"novo", "em_atendimento", "atendido"}

FINALIDADES = {"venda", "aluguel"}
STATUS_IMOVEL = {"disponivel", "reservado", "vendido", "alugado"}


def _texto(valor):
    """Devolve uma string sem espaços nas pontas (ou vazio se não for texto)."""
    return valor.strip() if isinstance(valor, str) else ""


def _inteiro(valor):
    """Converte para inteiro; devolve None se não for possível."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _decimal(valor):
    """Converte para Decimal com 2 casas; devolve None se inválido."""
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite():
            return None
        return numero.quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _booleano(valor):
    """Aceita true/false vindos de JSON, formulário ou strings."""
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in {"1", "true", "sim", "on"}


def validar_contato(dados):
    """Valida o corpo de POST/PUT de /api/contatos."""
    dados = dados if isinstance(dados, dict) else {}
    limpo, erros = {}, {}

    nome = _texto(dados.get("nome"))
    if len(nome) < 3:
        erros["nome"] = "Informe seu nome completo (mínimo de 3 caracteres)."
    elif len(nome) > 120:
        erros["nome"] = "O nome deve ter no máximo 120 caracteres."
    limpo["nome"] = nome

    email = _texto(dados.get("email")).lower()
    if not EMAIL.match(email):
        erros["email"] = "Informe um e-mail válido."
    elif len(email) > 160:
        erros["email"] = "O e-mail deve ter no máximo 160 caracteres."
    limpo["email"] = email

    telefone = _texto(dados.get("telefone"))
    digitos = re.sub(r"\D", "", telefone)
    if not 10 <= len(digitos) <= 13:
        erros["telefone"] = "Informe um telefone com DDD (10 a 13 dígitos)."
    limpo["telefone"] = telefone

    tipo = _texto(dados.get("tipo_interesse")).lower()
    if tipo not in TIPOS_INTERESSE:
        erros["tipo_interesse"] = "Escolha uma opção: comprar, alugar ou vender."
    limpo["tipo_interesse"] = tipo

    imovel_id = dados.get("imovel_id")
    if imovel_id in (None, "", 0, "0"):
        limpo["imovel_id"] = None
    else:
        convertido = _inteiro(imovel_id)
        if convertido is None or convertido <= 0:
            erros["imovel_id"] = "O imóvel selecionado é inválido."
        else:
            limpo["imovel_id"] = convertido

    mensagem = _texto(dados.get("mensagem"))
    if len(mensagem) > 2000:
        erros["mensagem"] = "A mensagem deve ter no máximo 2000 caracteres."
    limpo["mensagem"] = mensagem or None

    status = _texto(dados.get("status")).lower() or "novo"
    if status not in STATUS_CONTATO:
        erros["status"] = "Status inválido."
    limpo["status"] = status

    return limpo, erros


def validar_imovel(dados):
    """Valida o corpo de POST/PUT de /api/imoveis."""
    dados = dados if isinstance(dados, dict) else {}
    limpo, erros = {}, {}

    codigo = _texto(dados.get("codigo")).upper()
    if not 3 <= len(codigo) <= 12 or not CODIGO.match(codigo):
        erros["codigo"] = (
            "O código deve ter de 3 a 12 caracteres (letras, números ou hífen)."
        )
    limpo["codigo"] = codigo

    titulo = _texto(dados.get("titulo"))
    if len(titulo) < 5:
        erros["titulo"] = "O título deve ter pelo menos 5 caracteres."
    elif len(titulo) > 140:
        erros["titulo"] = "O título deve ter no máximo 140 caracteres."
    limpo["titulo"] = titulo

    descricao = _texto(dados.get("descricao"))
    if len(descricao) < 20:
        erros["descricao"] = "Descreva o imóvel com pelo menos 20 caracteres."
    limpo["descricao"] = descricao

    tipo_id = _inteiro(dados.get("tipo_id"))
    if not tipo_id or tipo_id <= 0:
        erros["tipo_id"] = "Selecione o tipo do imóvel."
    limpo["tipo_id"] = tipo_id

    bairro_id = _inteiro(dados.get("bairro_id"))
    if not bairro_id or bairro_id <= 0:
        erros["bairro_id"] = "Selecione o bairro do imóvel."
    limpo["bairro_id"] = bairro_id

    finalidade = _texto(dados.get("finalidade")).lower()
    if finalidade not in FINALIDADES:
        erros["finalidade"] = "A finalidade deve ser 'venda' ou 'aluguel'."
    limpo["finalidade"] = finalidade

    status = _texto(dados.get("status")).lower() or "disponivel"
    if status not in STATUS_IMOVEL:
        erros["status"] = "Status do imóvel inválido."
    limpo["status"] = status

    preco = _decimal(dados.get("preco"))
    if preco is None or preco <= 0:
        erros["preco"] = "Informe um preço maior que zero."
    limpo["preco"] = preco

    for campo in ("quartos", "banheiros", "vagas"):
        valor = _inteiro(dados.get(campo, 0))
        if valor is None or valor < 0 or valor > 50:
            erros[campo] = "Informe um número entre 0 e 50."
        limpo[campo] = valor if valor is not None else 0

    area = _decimal(dados.get("area_m2"))
    if area is None or area <= 0 or area > 100000:
        erros["area_m2"] = "Informe a área em m² (maior que zero)."
    limpo["area_m2"] = area

    imagem_url = _texto(dados.get("imagem_url"))
    if imagem_url and not imagem_url.startswith(("http://", "https://")):
        erros["imagem_url"] = "A imagem deve ser uma URL http(s)."
    if len(imagem_url) > 500:
        erros["imagem_url"] = "A URL da imagem deve ter no máximo 500 caracteres."
    limpo["imagem_url"] = imagem_url or None

    limpo["destaque"] = _booleano(dados.get("destaque", False))

    return limpo, erros
