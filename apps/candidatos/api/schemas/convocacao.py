"""Documentação OpenAPI das operações de convocação de habilitados."""

from __future__ import annotations

from candidatos.serializers import (
    ConcursoCandidatoSerializer,
    ConvocarRequisicaoSerializer,
    ConvocarRespostaSerializer,
    DesconvocarRequisicaoSerializer,
    DesconvocarRespostaSerializer,
    HabilitadosCalculadosRespostaSerializer,
)
from core.openapi import exemplos_requisicao, resposta, respostas
from core.serializers import ErrosValidacaoSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .comuns import (
    AVISO_UUID_INVALIDO,
    CODIGO_CARGO_EXEMPLO,
    EXEMPLO_HABILITADO_CONVOCADO,
    EXEMPLO_HABILITADO_NA_SEQUENCIA,
    PARAMETRO_CODIGO_CARGO,
    PARAMETRO_CONCURSO_OBRIGATORIO,
    PARAMETRO_FIELDS,
    RESPOSTA_CONCURSO_OBRIGATORIO,
    RESPOSTA_SEQUENCIA_HABILITADOS,
    TAG_CONVOCACAO,
    UUID_CONCURSO_EXEMPLO,
    UUID_HABILITADO_2_EXEMPLO,
    UUID_HABILITADO_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_detalhe,
)

AVISO_GRAVA_RANKING = (
    "**Embora seja GET, a operação grava dados**: atualiza `ranking` e "
    "`ranking_escolha` dos habilitados retornados."
)

PARAMETROS_CALCULO = [
    OpenApiParameter(
        name="quantidade",
        type=OpenApiTypes.INT,
        required=True,
        description="Quantidade de habilitados a convocar. Mínimo: 1.",
    ),
    OpenApiParameter(
        name="concurso_uuid",
        type=OpenApiTypes.UUID,
        required=True,
        description="UUID do concurso.",
    ),
    OpenApiParameter(
        name="processo_uuid",
        type=OpenApiTypes.UUID,
        required=True,
        description=(
            "UUID do processo de convocação em preparação. É a ele que as "
            "reclassificações e eliminações ficam associadas."
        ),
    ),
    OpenApiParameter(
        name="codigo_cargo",
        type=OpenApiTypes.STR,
        required=True,
        description=(
            "Código do cargo. A validação não o exige, mas sem ele a "
            "operação falha com erro 500."
        ),
    ),
    PARAMETRO_FIELDS,
]

PARAMETROS_REPOSICAO = [
    PARAMETRO_CONCURSO_OBRIGATORIO,
    PARAMETRO_CODIGO_CARGO,
    OpenApiParameter(
        name="geral",
        type=OpenApiTypes.INT,
        description=(
            "Quantidade de habilitados a tomar da lista geral. Valor não "
            "numérico é tratado como 0."
        ),
    ),
    OpenApiParameter(
        name="pcd",
        type=OpenApiTypes.INT,
        description=(
            "Quantidade de habilitados a tomar da lista PCD. Valor não "
            "numérico é tratado como 0."
        ),
    ),
    OpenApiParameter(
        name="nna",
        type=OpenApiTypes.INT,
        description=(
            "Quantidade de habilitados a tomar da lista NNA. Valor não "
            "numérico é tratado como 0."
        ),
    ),
    PARAMETRO_FIELDS,
]

PARAMETROS_RECONVOCACAO = [
    OpenApiParameter(
        name="concurso_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "UUID do concurso. Sem ele, a resposta é uma lista vazia. "
            f"{AVISO_UUID_INVALIDO}"
        ),
    ),
    OpenApiParameter(
        name="quantidade",
        type=OpenApiTypes.INT,
        description=(
            "Quantidade máxima de habilitados a retornar, maior que zero. "
            "Obrigatória quando `concurso_uuid` é informado e há "
            "reconvocações registradas."
        ),
    ),
    PARAMETRO_CODIGO_CARGO,
    PARAMETRO_FIELDS,
]

OPERACOES_CONVOCACAO = {
    "calculados": extend_schema(
        operation_id="calcular_habilitados_convocacao",
        summary="Calcular a sequência de habilitados a convocar",
        tags=[TAG_CONVOCACAO],
        description=(
            "Monta a sequência dos próximos habilitados a convocar para um "
            "cargo, intercalando as listas geral, NNA e PCD conforme os "
            "percentuais da parametrização e descontando quem já foi "
            "convocado no concurso.\n\n"
            "Só entram habilitados não convocados e não eliminados do "
            "cargo. Quando uma lista reservada não tem habilitados "
            "suficientes, as posições dela são preenchidas pelas outras "
            "listas. Se a lista se esgotar, a sequência vem com menos "
            "itens do que o pedido.\n\n"
            "**Embora seja GET, a operação grava dados.** Nos habilitados "
            "retornados, atualiza `categoria_efetiva`, os campos de "
            "promoção para a lista geral, `ranking` e `ranking_escolha`. "
            "Também associa ao processo as reclassificações e eliminações "
            "dos habilitados que ficaram à frente na classificação: é isso "
            "que alimenta as consultas de reclassificados e eliminados do "
            "processo.\n\n"
            "A quantidade já convocada considera os convocados com escolha "
            "registrada no MS-Escolhas. Se não houver escolhas ou se a "
            "consulta ao MS-Escolhas falhar, considera todos os convocados "
            "do cargo. A operação exige uma parametrização cadastrada."
        ),
        parameters=PARAMETROS_CALCULO,
        responses=respostas(
            {
                200: resposta(
                    HabilitadosCalculadosRespostaSerializer,
                    "Sequência calculada e percentuais aplicados.",
                    {
                        "Sequência com um habilitado": {
                            "quantidade": 1,
                            "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                            "results": [EXEMPLO_HABILITADO_NA_SEQUENCIA],
                            "porcentagem_nna": 0.2,
                            "porcentagem_pcd": 0.05,
                        }
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Parâmetro obrigatório ausente ou com valor inválido.",
                    {
                        "Parâmetros ausentes": {
                            "quantidade": [
                                'O parâmetro "quantidade" é obrigatório'
                            ],
                            "concurso_uuid": [
                                'O parâmetro "concurso_uuid" é obrigatório'
                            ],
                            "processo_uuid": [
                                'O parâmetro "processo_uuid" é obrigatório'
                            ],
                        }
                    },
                ),
            }
        ),
    ),
    "reposicao": extend_schema(
        operation_id="listar_habilitados_reposicao",
        summary="Listar habilitados para reposição",
        tags=[TAG_CONVOCACAO],
        description=(
            "Lista os habilitados do concurso ainda não convocados, para "
            "repor vagas.\n\n"
            "- **Sem `geral`, `pcd` e `nna`**: retorna todos os não "
            "convocados do concurso, ou do cargo, se informado, sem "
            "alterar dados.\n"
            "- **Com ao menos uma quantidade**: toma os primeiros de cada "
            "lista, pela respectiva classificação e sem repetir "
            "habilitado, e devolve o conjunto ordenado pela classificação "
            f"geral. {AVISO_GRAVA_RANKING}\n\n"
            "A consulta não descarta habilitados eliminados."
        ),
        parameters=PARAMETROS_REPOSICAO,
        responses=respostas(
            {
                200: RESPOSTA_SEQUENCIA_HABILITADOS,
                400: RESPOSTA_CONCURSO_OBRIGATORIO,
            }
        ),
    ),
    "reconvocacao": extend_schema(
        operation_id="listar_habilitados_reconvocacao",
        summary="Listar habilitados para reconvocação",
        tags=[TAG_CONVOCACAO],
        description=(
            "Lista os habilitados do concurso que já foram convocados e "
            "têm reconvocação registrada no MS-Escolhas, até a quantidade "
            "pedida. A ordem prioriza quem concorre na lista PCD, depois "
            "na NNA e por fim os demais, pela classificação de cada "
            f"lista. {AVISO_GRAVA_RANKING}\n\n"
            "A resposta é uma lista vazia quando não há reconvocações "
            "registradas ou quando `concurso_uuid` não é informado.\n\n"
            "A consulta ao MS-Escolhas acontece antes de qualquer "
            "validação: se ele não responder, o resultado é 503, mesmo com "
            "parâmetros inválidos."
        ),
        parameters=PARAMETROS_RECONVOCACAO,
        responses=respostas(
            {
                200: resposta(
                    ConcursoCandidatoSerializer(many=True),
                    (
                        "Habilitados a reconvocar. Lista vazia se não há "
                        "reconvocações ou concurso informado."
                    ),
                    {"Habilitado a reconvocar": EXEMPLO_HABILITADO_CONVOCADO},
                ),
                400: erro_detalhe(
                    "Parâmetro `quantidade` ausente ou inválido.",
                    {
                        "Quantidade ausente": "quantidade é obrigatória",
                        "Quantidade não numérica": (
                            "quantidade deve ser um número válido"
                        ),
                        "Quantidade zero ou negativa": (
                            "quantidade deve ser um número positivo"
                        ),
                    },
                ),
                503: erro_detalhe(
                    "O MS-Escolhas não respondeu à consulta de reconvocações.",
                    {
                        "MS-Escolhas indisponível": (
                            "Erro ao buscar reconvocações no microserviço "
                            "de Escolhas"
                        )
                    },
                ),
            }
        ),
    ),
    "convocar": extend_schema(
        operation_id="convocar_habilitados",
        summary="Convocar habilitados",
        tags=[TAG_CONVOCACAO],
        description=(
            "Marca como convocados os habilitados informados que pertencem "
            "ao concurso: grava `foi_convocado`, o `processo_uuid` e a "
            "data e hora atuais em `data_convocacao`. UUIDs que não "
            "pertencem ao concurso são ignorados, e a resposta lista os "
            "que foram de fato marcados.\n\n"
            "A operação não confere se o habilitado já estava convocado "
            "nem se está eliminado: quem já estava convocado tem o "
            "processo e a data sobrescritos.\n\n"
            "`concurso_uuid` e os itens de `candidatos` não têm o formato "
            "validado: um valor que não seja UUID resulta em erro 500."
        ),
        request=ConvocarRequisicaoSerializer,
        examples=exemplos_requisicao(
            {
                "Dois habilitados": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "processo_uuid": UUID_PROCESSO_EXEMPLO,
                    "candidatos": [
                        UUID_HABILITADO_EXEMPLO,
                        UUID_HABILITADO_2_EXEMPLO,
                    ],
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ConvocarRespostaSerializer,
                    "Habilitados marcados como convocados.",
                    {
                        "Dois convocados": {
                            "atualizados": [
                                UUID_HABILITADO_EXEMPLO,
                                UUID_HABILITADO_2_EXEMPLO,
                            ],
                            "total": 2,
                        }
                    },
                ),
                400: erro_detalhe(
                    "Concurso ausente ou `candidatos` fora do formato.",
                    {
                        "Concurso não informado": (
                            "concurso_uuid é obrigatório"
                        ),
                        "Candidatos não é uma lista": "Payload inválido",
                    },
                ),
            }
        ),
    ),
    "desconvocar": extend_schema(
        operation_id="desconvocar_habilitados",
        summary="Desconvocar habilitados de um processo",
        tags=[TAG_CONVOCACAO],
        description=(
            "Desfaz a convocação de todos os habilitados convocados no "
            "processo ou, com `codigo_cargo`, apenas dos convocados "
            "daquele cargo: `foi_convocado` volta a falso, e "
            "`processo_uuid` e `data_convocacao` são apagados.\n\n"
            "Com `codigo_cargo`, o serviço também pede ao MS-Agenda a "
            "remoção das agendas do processo para o cargo. Uma falha nessa "
            "chamada é registrada em log e não altera a resposta.\n\n"
            "`processo_uuid` não tem o formato validado: um valor que não "
            "seja UUID resulta em erro 500."
        ),
        request=DesconvocarRequisicaoSerializer,
        examples=exemplos_requisicao(
            {
                "Processo inteiro": {"processo_uuid": UUID_PROCESSO_EXEMPLO},
                "Apenas um cargo": {
                    "processo_uuid": UUID_PROCESSO_EXEMPLO,
                    "codigo_cargo": CODIGO_CARGO_EXEMPLO,
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    DesconvocarRespostaSerializer,
                    "Habilitados desconvocados.",
                    {
                        "Processo inteiro": {
                            "desconvocados": [
                                UUID_HABILITADO_EXEMPLO,
                                UUID_HABILITADO_2_EXEMPLO,
                            ],
                            "total": 2,
                            "processo_uuid": UUID_PROCESSO_EXEMPLO,
                            "codigo_cargo": None,
                        },
                        "Apenas um cargo": {
                            "desconvocados": [UUID_HABILITADO_EXEMPLO],
                            "total": 1,
                            "processo_uuid": UUID_PROCESSO_EXEMPLO,
                            "codigo_cargo": CODIGO_CARGO_EXEMPLO,
                        },
                    },
                ),
                400: erro_detalhe(
                    "Processo não informado.",
                    {
                        "Processo não informado": (
                            "processo_uuid (ou concurso_uuid) é obrigatório"
                        )
                    },
                ),
            }
        ),
    ),
}
