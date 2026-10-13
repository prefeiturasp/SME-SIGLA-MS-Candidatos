"""Documentação OpenAPI das operações de lotes do SIGPEC."""

from __future__ import annotations

from candidatos.serializers import (
    CargoLoteSerializer,
    ErroSalvarLotesSerializer,
    NumeroLoteSerializer,
    SalvarLotesRespostaSerializer,
    SalvarLotesSerializer,
)
from core.openapi import exemplos_requisicao, resposta, respostas
from core.serializers import ErrosValidacaoSerializer
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema

from .comuns import (
    CODIGO_CARGO_EXEMPLO,
    NOME_CARGO_EXEMPLO,
    PARAMETRO_CODIGO_CARGO,
    PARAMETRO_CONCURSO_OBRIGATORIO,
    RESPOSTA_CONCURSO_OBRIGATORIO,
    TAG_LOTES,
    UUID_CONCURSO_EXEMPLO,
)

ERRO_SALVAR_LOTES = PolymorphicProxySerializer(
    component_name="ErroSalvarLotesRequisicao",
    serializers=[ErroSalvarLotesSerializer, ErrosValidacaoSerializer],
    resource_type_field_name=None,
)

OPERACOES_LOTES = {
    "numeros_lote": extend_schema(
        operation_id="listar_numeros_lote",
        summary="Listar números de lote do concurso",
        tags=[TAG_LOTES],
        description=(
            "Retorna os números de lote do SIGPEC já gravados nos "
            "habilitados do concurso, em ordem crescente e sem repetição. "
            "Com `codigo_cargo`, considera só os habilitados do cargo."
        ),
        parameters=[PARAMETRO_CONCURSO_OBRIGATORIO, PARAMETRO_CODIGO_CARGO],
        responses=respostas(
            {
                200: resposta(
                    NumeroLoteSerializer(many=True),
                    "Números de lote. Lista vazia se nenhum lote foi salvo.",
                    {"Lote 1": {"numero_lote": 1}},
                ),
                400: RESPOSTA_CONCURSO_OBRIGATORIO,
            }
        ),
    ),
    "cargos": extend_schema(
        operation_id="listar_cargos_lote",
        summary="Listar cargos com lote no concurso",
        tags=[TAG_LOTES],
        description=(
            "Retorna os cargos do concurso que têm habilitados com lote do "
            "SIGPEC gravado, em ordem de código e sem repetição. Serve "
            "para escolher o cargo na exportação para o SIGPEC."
        ),
        parameters=[PARAMETRO_CONCURSO_OBRIGATORIO],
        responses=respostas(
            {
                200: resposta(
                    CargoLoteSerializer(many=True),
                    "Cargos com lote. Lista vazia se nenhum lote foi salvo.",
                    {
                        "Cargo com lote": {
                            "codigo_cargo": CODIGO_CARGO_EXEMPLO,
                            "descricao_cargo": NOME_CARGO_EXEMPLO,
                        }
                    },
                ),
                400: RESPOSTA_CONCURSO_OBRIGATORIO,
            }
        ),
    ),
    "salvar_lotes": extend_schema(
        operation_id="salvar_lotes",
        summary="Salvar lote do SIGPEC",
        tags=[TAG_LOTES],
        description=(
            "Grava nos habilitados do concurso os dados de um lote "
            "devolvido pelo SIGPEC: número do lote, empresa, vaga e chave "
            "do inscrito. No candidato, grava o registro funcional e o "
            "vínculo; se `numfunc` e `numvinc` não vierem, esses dois "
            "campos ficam em branco.\n\n"
            "O lote é substituído por inteiro:\n\n"
            "1. Os habilitados do concurso que estavam com o número de "
            "lote da **primeira linha** têm lote, empresa e vaga "
            "apagados.\n"
            "2. Cada linha localiza o habilitado pelo código de inscrição "
            "(`identificacao`) no concurso e grava os dados nele.\n\n"
            "A operação é atômica: se alguma linha não localizar o "
            "habilitado, nada é gravado, e a resposta é 400 com a relação "
            "das linhas não localizadas."
        ),
        request=SalvarLotesSerializer,
        examples=exemplos_requisicao(
            {
                "Lote com duas linhas": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "lotes": [
                        {
                            "lote": 1,
                            "empresa": 16,
                            "vaga": 1001,
                            "identificacao": "0012345",
                            "chave_inscrito": "A1B2C3",
                            "numfunc": "1234567",
                            "numvinc": "1",
                        },
                        {
                            "lote": 1,
                            "empresa": 16,
                            "vaga": 1002,
                            "identificacao": "0012346",
                            "chave_inscrito": "D4E5F6",
                            "numfunc": "7654321",
                            "numvinc": "1",
                        },
                    ],
                }
            }
        ),
        responses=respostas(
            {
                201: resposta(
                    SalvarLotesRespostaSerializer,
                    "Lote gravado.",
                    {"Duas linhas gravadas": {"total_atualizados": 2}},
                ),
                400: resposta(
                    ERRO_SALVAR_LOTES,
                    (
                        "Corpo inválido ou falha ao gravar o lote. Nada é "
                        "persistido."
                    ),
                    {
                        "Inscrição não localizada": {
                            "mensagem": (
                                "Falha ao salvar lotes. Nenhuma alteracao "
                                "foi persistida."
                            ),
                            "detail": (
                                "Linha: 2 - Candidato com codigo_inscricao: "
                                "0012346 não encontrado"
                            ),
                        },
                        "Lista de linhas vazia": {
                            "lotes": [
                                "Ensure this field has at least 1 elements."
                            ]
                        },
                    },
                ),
            }
        ),
    ),
}
