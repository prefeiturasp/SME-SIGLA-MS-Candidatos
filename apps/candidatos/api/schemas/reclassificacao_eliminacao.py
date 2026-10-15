"""Documentação OpenAPI de reclassificação e eliminação de habilitados."""

from __future__ import annotations

from candidatos.serializers import (
    EliminacaoRespostaSerializer,
    EliminadosRespostaSerializer,
    EliminarSerializer,
    ReclassificacaoRespostaSerializer,
    ReclassificadosRespostaSerializer,
    ReclassificarSerializer,
)
from core.openapi import (
    ERRO_REQUISICAO,
    exemplos_requisicao,
    resposta,
    respostas,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .comuns import (
    AVISO_UUID_INVALIDO,
    EXEMPLO_HABILITADO,
    EXEMPLO_HABILITADO_RESUMIDO,
    PARAMETRO_CONCURSO_OBRIGATORIO,
    TAG_RECLASSIFICACAO,
    UUID_HABILITADO_EXEMPLO,
    UUID_HISTORICO_EXEMPLO,
    erro_detalhe,
)

AVISO_ASSOCIACAO_AO_PROCESSO = (
    "A associação ao processo acontece no cálculo da sequência de "
    "convocação. Antes disso, o registro não aparece nesta consulta."
)

EXEMPLO_RECLASSIFICACAO = {
    "uuid": UUID_HISTORICO_EXEMPLO,
    "desclassificado_de": "NNA",
    "nova_classificacao": "GERAL",
    "motivo": "Não confirmado pela comissão de heteroidentificação",
    "executado_por": "maria.gestora",
    "mandado_judicial": False,
    "criado_em": "2026-09-10T14:30:00-03:00",
}

EXEMPLO_HABILITADO_RECLASSIFICADO = {
    **EXEMPLO_HABILITADO,
    "reclassificacoes": [EXEMPLO_RECLASSIFICACAO],
    "categoria_efetiva": "GERAL",
}

ELIMINACAO_EXEMPLO = {
    "eliminado": True,
    "eliminado_em": "2026-09-12T10:00:00-03:00",
    "eliminado_motivo": "Não apresentou a documentação no prazo",
    "eliminado_por": "maria.gestora",
}

PARAMETRO_PROCESSO_OBRIGATORIO = OpenApiParameter(
    name="processo_uuid",
    type=OpenApiTypes.UUID,
    required=True,
    description=f"UUID do processo de convocação. {AVISO_UUID_INVALIDO}",
)

PARAMETROS_ELIMINADOS = [
    PARAMETRO_CONCURSO_OBRIGATORIO,
    PARAMETRO_PROCESSO_OBRIGATORIO,
    OpenApiParameter(
        name="classificacao_min",
        type=OpenApiTypes.INT,
        required=True,
        description=(
            "Menor classificação geral do intervalo, inclusive. Um valor "
            "não numérico resulta em erro 500."
        ),
    ),
    OpenApiParameter(
        name="classificacao_max",
        type=OpenApiTypes.INT,
        required=True,
        description=(
            "Maior classificação geral do intervalo, inclusive. Um valor "
            "não numérico resulta em erro 500."
        ),
    ),
]

OPERACOES_RECLASSIFICACAO = {
    "reclassificar": extend_schema(
        operation_id="reclassificar_habilitado",
        summary="Reclassificar habilitado",
        tags=[TAG_RECLASSIFICACAO],
        description=(
            "Retira o habilitado de uma lista reservada, `NNA` ou `PCD`, "
            "ou, com `mandado_judicial`, devolve-o a ela.\n\n"
            "- **Desclassificar** (padrão): registra a reclassificação e "
            "recalcula a categoria efetiva, que passa à outra lista "
            "reservada em que o habilitado ainda concorra ou, na falta "
            "dela, a `GERAL`. Exige classificação na lista informada e "
            "que ainda não haja desclassificação registrada para ela.\n"
            "- **Reverter por mandado judicial** (`mandado_judicial` "
            "verdadeiro): marca a desclassificação existente como "
            "revertida, mantendo-a no histórico, e recalcula a categoria "
            "efetiva. Exige uma desclassificação ativa para a lista "
            "informada.\n\n"
            "O usuário autenticado fica registrado como autor da operação."
        ),
        request=ReclassificarSerializer,
        examples=exemplos_requisicao(
            {
                "Desclassificar da lista NNA": {
                    "candidato_uuid": UUID_HABILITADO_EXEMPLO,
                    "desclassificar_de": "NNA",
                    "motivo": EXEMPLO_RECLASSIFICACAO["motivo"],
                },
                "Reverter por mandado judicial": {
                    "candidato_uuid": UUID_HABILITADO_EXEMPLO,
                    "desclassificar_de": "NNA",
                    "motivo": "Decisão judicial de reintegração à lista",
                    "mandado_judicial": True,
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ReclassificacaoRespostaSerializer,
                    "Habilitado reclassificado.",
                    {
                        "Passou da lista NNA para a geral": {
                            "concurso_candidato": (
                                EXEMPLO_HABILITADO_RECLASSIFICADO
                            ),
                            "historico_uuid": UUID_HISTORICO_EXEMPLO,
                            "nova_categoria_efetiva": "GERAL",
                        }
                    },
                ),
                400: resposta(
                    ERRO_REQUISICAO,
                    "Corpo inválido ou reclassificação recusada.",
                    {
                        "Lista inválida": {
                            "desclassificar_de": [
                                '"X" não é um escolha válido.'
                            ]
                        },
                        "Sem classificação na lista": {
                            "detail": "Candidato não possui classificação NNA."
                        },
                        "Já desclassificado": {
                            "detail": (
                                "Já há desclassificação registrada para NNA."
                            )
                        },
                        "Nada a reverter": {
                            "detail": (
                                "Não há desclassificação a reverter para NNA."
                            )
                        },
                        "Habilitado inexistente": {
                            "detail": "Erro ao reclassificar"
                        },
                    },
                ),
            }
        ),
    ),
    "eliminar": extend_schema(
        operation_id="eliminar_habilitado",
        summary="Eliminar habilitado",
        tags=[TAG_RECLASSIFICACAO],
        description=(
            "Elimina o habilitado: grava `eliminado`, a data e hora, o "
            "motivo e o usuário autenticado, e registra a eliminação no "
            "histórico. O habilitado eliminado deixa de entrar no cálculo "
            "da sequência de convocação.\n\n"
            "Esta API não tem operação para desfazer a eliminação."
        ),
        request=EliminarSerializer,
        examples=exemplos_requisicao(
            {
                "Eliminar com motivo": {
                    "candidato_uuid": UUID_HABILITADO_EXEMPLO,
                    "motivo": ELIMINACAO_EXEMPLO["eliminado_motivo"],
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    EliminacaoRespostaSerializer,
                    "Habilitado eliminado.",
                    {
                        "Habilitado eliminado": {
                            "concurso_candidato": {
                                **EXEMPLO_HABILITADO,
                                **ELIMINACAO_EXEMPLO,
                            },
                            "historico_uuid": UUID_HISTORICO_EXEMPLO,
                            "acao": "ELIMINAR",
                        }
                    },
                ),
                400: resposta(
                    ERRO_REQUISICAO,
                    "Corpo inválido ou eliminação recusada.",
                    {
                        "Habilitado não informado": {
                            "candidato_uuid": ["Este campo é obrigatório."]
                        },
                        "Já eliminado": {
                            "detail": "Registro já está eliminado."
                        },
                        "Habilitado inexistente": {
                            "detail": "Erro ao eliminar"
                        },
                    },
                ),
            }
        ),
    ),
}

OPERACOES_RECLASSIFICADOS = {
    "list": extend_schema(
        operation_id="listar_reclassificados",
        summary="Listar reclassificados de um processo",
        description=(
            "Lista os habilitados do concurso que saíram de uma lista "
            "reservada e passaram a concorrer pela geral, com a "
            "reclassificação associada ao processo informado, separados "
            "pela lista de origem. Habilitados eliminados não entram.\n\n"
            f"{AVISO_ASSOCIACAO_AO_PROCESSO}"
        ),
        parameters=[
            PARAMETRO_CONCURSO_OBRIGATORIO,
            PARAMETRO_PROCESSO_OBRIGATORIO,
        ],
        responses=respostas(
            {
                200: resposta(
                    ReclassificadosRespostaSerializer,
                    "Reclassificados do processo, por lista de origem.",
                    {
                        "Um reclassificado da lista NNA": {
                            "nna": [
                                {
                                    **EXEMPLO_HABILITADO_RESUMIDO,
                                    "categoria_efetiva": "GERAL",
                                }
                            ],
                            "pcd": [],
                        }
                    },
                ),
                400: erro_detalhe(
                    "Concurso ou processo não informado.",
                    {
                        "Parâmetros ausentes": (
                            "concurso_uuid e processo_uuid são obrigatórios"
                        )
                    },
                ),
            }
        ),
    ),
}

OPERACOES_ELIMINADOS = {
    "list": extend_schema(
        operation_id="listar_eliminados",
        summary="Listar eliminados de um processo",
        description=(
            "Lista os habilitados eliminados do concurso cuja eliminação "
            "está associada ao processo informado e cuja classificação "
            "geral está no intervalo pedido, separados pela lista em que "
            "concorriam. Quem concorria nas listas NNA e PCD aparece nas "
            "duas, e `geral` traz só quem não concorria em lista "
            "reservada.\n\n"
            f"{AVISO_ASSOCIACAO_AO_PROCESSO}"
        ),
        parameters=PARAMETROS_ELIMINADOS,
        responses=respostas(
            {
                200: resposta(
                    EliminadosRespostaSerializer,
                    "Eliminados do processo, por lista em que concorriam.",
                    {
                        "Um eliminado da lista NNA": {
                            "geral": [],
                            "nna": [
                                {
                                    **EXEMPLO_HABILITADO_RESUMIDO,
                                    **ELIMINACAO_EXEMPLO,
                                }
                            ],
                            "pcd": [],
                        }
                    },
                ),
                400: erro_detalhe(
                    "Parâmetro obrigatório não informado.",
                    {
                        "Parâmetros ausentes": (
                            "concurso_uuid, processo_uuid, "
                            "classificacao_max e classificacao_min são "
                            "obrigatórios"
                        )
                    },
                ),
            }
        ),
    ),
}
