"""Documentação OpenAPI das operações de parametrização."""

from __future__ import annotations

from core.openapi import exemplos_requisicao, resposta, respostas
from core.serializers import ErroDetalheSerializer, ErrosValidacaoSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from parametrizacao.serializers import ParametrizacaoSerializer

TAG_PARAMETRIZACAO = "Parametrização"

AVISO_ID_IGNORADO = (
    "O identificador da rota é ignorado: a operação sempre atua sobre a "
    "parametrização mais recente."
)

EXEMPLO_PARAMETRIZACAO = {
    "id": 1,
    "uuid": "2f1e0d9c-8b7a-4c6d-9e5f-4a3b2c1d0e9f",
    "criado_em": "2026-01-05T08:00:00-03:00",
    "atualizado_em": "2026-08-18T16:20:00-03:00",
    "esta_ativo": True,
    "porcentagem_pcd": 0.05,
    "porcentagem_nna": 0.2,
}

PARAMETRO_ID = OpenApiParameter(
    name="id",
    type=OpenApiTypes.STR,
    location=OpenApiParameter.PATH,
    description=(
        "Valor ignorado pela operação. Qualquer texto é aceito, e ele não "
        "seleciona o registro."
    ),
)

RESPOSTA_PARAMETRIZACAO = resposta(
    ParametrizacaoSerializer,
    "Parametrização vigente.",
    {"Percentuais padrão": EXEMPLO_PARAMETRIZACAO},
)

RESPOSTA_SEM_PARAMETRIZACAO = resposta(
    ErroDetalheSerializer,
    "Nenhuma parametrização cadastrada.",
    {"Sem parametrização": {"detail": "Não encontrado."}},
)

RESPOSTA_PERCENTUAL_INVALIDO = resposta(
    ErrosValidacaoSerializer,
    "Percentual com valor inválido.",
    {
        "Percentual não numérico": {
            "porcentagem_pcd": ["Um número válido é necessário."]
        }
    },
)

OPERACOES_PARAMETRIZACAO = {
    "list": extend_schema(
        operation_id="listar_parametrizacoes",
        summary="Listar parametrizações",
        description=(
            "Retorna as parametrizações cadastradas, da mais recente para "
            "a mais antiga. A primeira é a vigente: é ela que o cálculo da "
            "sequência de convocação usa e é sobre ela que as operações de "
            "detalhe e de atualização atuam. Em operação normal existe um "
            "único registro."
        ),
        filters=False,
        responses=respostas(
            {
                200: resposta(
                    ParametrizacaoSerializer(many=True),
                    "Parametrizações cadastradas.",
                    {"Percentuais padrão": EXEMPLO_PARAMETRIZACAO},
                )
            }
        ),
    ),
    "create": extend_schema(exclude=True),
    "retrieve": extend_schema(
        operation_id="detalhar_parametrizacao",
        summary="Detalhar a parametrização vigente",
        description=f"Retorna a parametrização vigente. {AVISO_ID_IGNORADO}",
        parameters=[PARAMETRO_ID],
        responses=respostas(
            {200: RESPOSTA_PARAMETRIZACAO, 404: RESPOSTA_SEM_PARAMETRIZACAO}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_parametrizacao",
        summary="Atualizar a parametrização vigente",
        description=(
            "Atualiza os percentuais de reserva de vagas. Os dois campos "
            "são opcionais: o que não for enviado permanece como está. "
            f"{AVISO_ID_IGNORADO}"
        ),
        parameters=[PARAMETRO_ID],
        request=ParametrizacaoSerializer,
        examples=exemplos_requisicao(
            {
                "Definir os dois percentuais": {
                    "porcentagem_pcd": 0.05,
                    "porcentagem_nna": 0.2,
                }
            }
        ),
        responses=respostas(
            {
                200: RESPOSTA_PARAMETRIZACAO,
                400: RESPOSTA_PERCENTUAL_INVALIDO,
                404: RESPOSTA_SEM_PARAMETRIZACAO,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_parametrizacao",
        summary="Atualizar parcialmente a parametrização vigente",
        description=(
            "Atualiza apenas os percentuais enviados. " f"{AVISO_ID_IGNORADO}"
        ),
        parameters=[PARAMETRO_ID],
        request=ParametrizacaoSerializer,
        examples=exemplos_requisicao(
            {"Alterar a reserva PCD": {"porcentagem_pcd": 0.07}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_PARAMETRIZACAO,
                400: RESPOSTA_PERCENTUAL_INVALIDO,
                404: RESPOSTA_SEM_PARAMETRIZACAO,
            }
        ),
    ),
}
