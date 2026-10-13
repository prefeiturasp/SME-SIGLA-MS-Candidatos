"""Documentação OpenAPI da consulta de habilitados e do CRUD legado."""

from __future__ import annotations

from candidatos.serializers import (
    BuscarPorCpfsSerializer,
    BuscarPorUuidsSerializer,
    ConcursoCandidatoCpfUuidSerializer,
    ConcursoCandidatoSerializer,
    ExtracaoDadosRespostaSerializer,
    ExtracaoDadosSerializer,
    HabilitadosPorProcessoRespostaSerializer,
    HabilitadosPorUuidsRespostaSerializer,
    ProcessosUuidsRequisicaoSerializer,
)
from core.openapi import (
    ERRO_REQUISICAO,
    exemplos_requisicao,
    resposta,
    respostas,
)
from core.serializers import ErrosValidacaoSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .comuns import (
    AVISO_LEGADO,
    AVISO_UUID_INVALIDO,
    CPF_EXEMPLO,
    EXEMPLO_DADOS_HABILITADO,
    EXEMPLO_HABILITADO,
    EXEMPLO_HABILITADO_CONVOCADO,
    PARAMETRO_CODIGO_CARGO,
    PARAMETRO_CONCURSO_OBRIGATORIO,
    PARAMETRO_FIELDS,
    PARAMETRO_ORDER_BY,
    RESPOSTA_CONCURSO_OBRIGATORIO,
    RESPOSTA_HABILITADO_INEXISTENTE,
    RESPOSTA_HABILITADOS,
    TAG_HABILITADOS,
    UUID_CONCURSO_EXEMPLO,
    UUID_HABILITADO_2_EXEMPLO,
    UUID_HABILITADO_EXEMPLO,
    UUID_PROCESSO_2_EXEMPLO,
    UUID_PROCESSO_EXEMPLO,
    erro_detalhe,
)

FILTROS_COM_LISTA = {
    "processo_uuid": (
        OpenApiTypes.UUID,
        "Retorna apenas os habilitados convocados no processo informado.",
    ),
    "codigo_cargo": (
        OpenApiTypes.STR,
        "Retorna apenas os habilitados do cargo informado.",
    ),
    "candidato__cpf": (
        OpenApiTypes.STR,
        (
            "Retorna apenas os habilitados do candidato com o CPF "
            "informado, como está gravado."
        ),
    ),
    "candidato__registro_funcional": (
        OpenApiTypes.STR,
        (
            "Retorna apenas os habilitados do candidato com o registro "
            "funcional informado."
        ),
    ),
    "candidato__nome": (
        OpenApiTypes.STR,
        (
            "Retorna apenas os habilitados do candidato com o nome "
            "informado. A comparação é pelo texto exato."
        ),
    ),
    "candidato__rg": (
        OpenApiTypes.STR,
        "Retorna apenas os habilitados do candidato com o RG informado.",
    ),
    "classificacao": (
        OpenApiTypes.INT,
        "Retorna apenas os habilitados com a classificação geral informada.",
    ),
    "classificacao_pcd": (
        OpenApiTypes.INT,
        "Retorna apenas os habilitados com a classificação PCD informada.",
    ),
    "classificacao_nna": (
        OpenApiTypes.INT,
        "Retorna apenas os habilitados com a classificação NNA informada.",
    ),
}


def _filtros_com_lista() -> list[OpenApiParameter]:
    """Monta cada filtro na forma exata e na forma de lista (``__in``)."""
    parametros = []
    for nome, (tipo, descricao) in FILTROS_COM_LISTA.items():
        parametros.append(
            OpenApiParameter(name=nome, type=tipo, description=descricao)
        )
        parametros.append(
            OpenApiParameter(
                name=f"{nome}__in",
                type=tipo,
                many=True,
                explode=False,
                description=(
                    f"Como `{nome}`, aceitando vários valores separados "
                    "por vírgula."
                ),
            )
        )
    return parametros


PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="concurso_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Retorna apenas os habilitados do concurso informado. "
            f"{AVISO_UUID_INVALIDO}"
        ),
    ),
    OpenApiParameter(
        name="concurso_uuid__in",
        type=OpenApiTypes.UUID,
        many=True,
        explode=False,
        description=(
            "Como `concurso_uuid`, aceitando vários valores separados por "
            "vírgula. Aqui um valor que não seja UUID resulta em 400."
        ),
    ),
    OpenApiParameter(
        name="lote__concurso_uuid",
        type=OpenApiTypes.UUID,
        description=(
            "Nome alternativo de `concurso_uuid`, mantido por "
            "compatibilidade."
        ),
    ),
    *_filtros_com_lista(),
    OpenApiParameter(
        name="numero_lote",
        type=OpenApiTypes.INT,
        description=(
            "Retorna apenas os habilitados do lote do SIGPEC informado."
        ),
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            "Campo do habilitado usado na ordenação, por exemplo "
            "`classificacao`. Prefixe com `-` para ordem decrescente e "
            "separe vários campos por vírgula. Um campo desconhecido é "
            "ignorado. Padrão: `-criado_em`."
        ),
    ),
    PARAMETRO_FIELDS,
]

PARAMETRO_ID = OpenApiParameter(
    name="id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description=(
        "Identificador numérico interno do habilitado (campo `id`). Não é "
        "o `uuid`."
    ),
)

TOTAIS_HABILITADOS = {"total": 188, "geral": 150, "pcd": 8, "nna": 30}
TOTAIS_CONVOCADOS = {"total": 120, "geral": 96, "pcd": 6, "nna": 18}

EXEMPLO_EXTRACAO_GERAL = {
    "habilitados": TOTAIS_HABILITADOS,
    "convocados": TOTAIS_CONVOCADOS,
    "nao-convocados": {"total": 68, "geral": 54, "pcd": 2, "nna": 12},
}

EXEMPLO_EXTRACAO_POR_ANO = {
    "habilitados": TOTAIS_HABILITADOS,
    "2025": {
        "habilitados": {"total": 80, "geral": 64, "pcd": 4, "nna": 12},
        "convocados": {"total": 80, "geral": 64, "pcd": 4, "nna": 12},
        "nao-convocados": {"total": 108, "geral": 86, "pcd": 4, "nna": 18},
    },
    "2026": {
        "habilitados": {"total": 40, "geral": 32, "pcd": 2, "nna": 6},
        "convocados": {"total": 40, "geral": 32, "pcd": 2, "nna": 6},
        "nao-convocados": {"total": 148, "geral": 118, "pcd": 6, "nna": 24},
    },
}

EXEMPLO_POR_PROCESSO = {
    UUID_PROCESSO_EXEMPLO: {
        "GERAL": {"total": 1, "candidatos_uuids": [UUID_HABILITADO_2_EXEMPLO]},
        "NNA": {"total": 1, "candidatos_uuids": [UUID_HABILITADO_EXEMPLO]},
        "PCD": {"total": 0, "candidatos_uuids": []},
    }
}

RESPOSTA_HABILITADO = resposta(
    ConcursoCandidatoSerializer,
    "Habilitado.",
    {"Habilitado": EXEMPLO_HABILITADO},
)

RESPOSTA_HABILITADO_INVALIDO = resposta(
    ErrosValidacaoSerializer,
    "Dados do habilitado inválidos.",
    {
        "Classificação inválida": {
            "classificacao": ["Um número inteiro válido é exigido."]
        }
    },
)

ERRO_ORDENACAO_INVALIDA = "Parâmetro order_by inválido"

OPERACOES_CONSULTA = {
    "list": extend_schema(
        operation_id="listar_habilitados",
        summary="Listar habilitados",
        tags=[TAG_HABILITADOS],
        description=(
            "Lista os habilitados que atendem aos filtros, cada um com os "
            "dados do candidato, as reclassificações e o histórico de "
            "classificação. Os filtros podem ser combinados.\n\n"
            "A resposta **não é paginada**: sem filtros, vêm todos os "
            "habilitados da base. Filtre sempre por concurso ou processo "
            "e use `fields` para reduzir o volume. Parâmetros "
            "desconhecidos são ignorados, sem erro."
        ),
        filters=False,
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: RESPOSTA_HABILITADOS,
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtro com valor de tipo inválido.",
                    {
                        "Classificação não numérica": {
                            "classificacao": ["Informe um número."]
                        },
                        "Processo que não é UUID": {
                            "processo_uuid": ["Insira um UUID válido."]
                        },
                    },
                ),
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_habilitado",
        summary="Criar habilitado",
        tags=[TAG_HABILITADOS],
        description=(
            f"{AVISO_LEGADO} Para incluir habilitados, use a carga em lote "
            "de candidatos.\n\n"
            "A rota não consegue criar o registro: o candidato do "
            "habilitado não pode ser informado no corpo, então uma "
            "requisição com dados válidos falha com erro 500. Dados "
            "inválidos resultam em 400."
        ),
        deprecated=True,
        request=ConcursoCandidatoSerializer,
        examples=exemplos_requisicao(
            {"Dados de inscrição": EXEMPLO_DADOS_HABILITADO}
        ),
        responses=respostas(
            {
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Dados do habilitado inválidos.",
                    {
                        "Inscrição ausente": {
                            "codigo_inscricao": ["Este campo é obrigatório."]
                        }
                    },
                ),
                500: resposta(
                    None,
                    (
                        "Resultado de toda requisição com dados válidos: o "
                        "habilitado não pode ser gravado sem candidato. O "
                        "corpo não segue um modelo JSON."
                    ),
                ),
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_habilitado",
        summary="Detalhar habilitado",
        tags=[TAG_HABILITADOS],
        description=(
            f"{AVISO_LEGADO} Para obter habilitados pelo UUID, use a busca "
            "por UUIDs.\n\n"
            "Retorna um habilitado pelo identificador numérico interno."
        ),
        deprecated=True,
        parameters=[PARAMETRO_ID, PARAMETRO_FIELDS],
        responses=respostas(
            {200: RESPOSTA_HABILITADO, 404: RESPOSTA_HABILITADO_INEXISTENTE}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_habilitado",
        summary="Atualizar habilitado",
        tags=[TAG_HABILITADOS],
        description=(
            f"{AVISO_LEGADO}\n\n"
            "Substitui os dados da inscrição do habilitado. "
            "`codigo_inscricao` é obrigatório. Os campos são gravados como "
            "recebidos, sem aplicar as regras de convocação, "
            "reclassificação e eliminação nem gerar histórico. O candidato "
            "não é alterado."
        ),
        deprecated=True,
        parameters=[PARAMETRO_ID],
        request=ConcursoCandidatoSerializer,
        examples=exemplos_requisicao(
            {"Atualização completa": EXEMPLO_DADOS_HABILITADO}
        ),
        responses=respostas(
            {
                200: RESPOSTA_HABILITADO,
                400: RESPOSTA_HABILITADO_INVALIDO,
                404: RESPOSTA_HABILITADO_INEXISTENTE,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_habilitado",
        summary="Atualizar parcialmente habilitado",
        tags=[TAG_HABILITADOS],
        description=(
            f"{AVISO_LEGADO}\n\n"
            "Atualiza apenas os campos enviados da inscrição. Os campos "
            "são gravados como recebidos, sem aplicar as regras de "
            "convocação, reclassificação e eliminação nem gerar histórico."
        ),
        deprecated=True,
        parameters=[PARAMETRO_ID],
        request=ConcursoCandidatoSerializer,
        examples=exemplos_requisicao(
            {"Registrar observação": {"observacao": "Documentação pendente"}}
        ),
        responses=respostas(
            {
                200: RESPOSTA_HABILITADO,
                400: RESPOSTA_HABILITADO_INVALIDO,
                404: RESPOSTA_HABILITADO_INEXISTENTE,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_habilitado",
        summary="Excluir habilitado",
        tags=[TAG_HABILITADOS],
        description=(
            f"{AVISO_LEGADO}\n\n"
            "Exclui o habilitado e os seus históricos de reclassificação, "
            "eliminação e classificação. O candidato continua cadastrado. "
            "A exclusão é definitiva."
        ),
        deprecated=True,
        parameters=[PARAMETRO_ID],
        responses=respostas(
            {
                204: resposta(None, "Habilitado excluído."),
                404: RESPOSTA_HABILITADO_INEXISTENTE,
            }
        ),
    ),
    "buscar_por_uuids": extend_schema(
        operation_id="buscar_habilitados_por_uuids",
        summary="Buscar habilitados por UUIDs",
        tags=[TAG_HABILITADOS],
        description=(
            "Retorna os habilitados cujos UUIDs foram informados, com os "
            "dados completos. UUIDs desconhecidos são ignorados. É a "
            "consulta que os demais microsserviços usam para resolver os "
            "`candidato_uuid` que guardam."
        ),
        parameters=[PARAMETRO_ORDER_BY, PARAMETRO_FIELDS],
        request=BuscarPorUuidsSerializer,
        examples=exemplos_requisicao(
            {
                "Dois habilitados": {
                    "uuids": [
                        UUID_HABILITADO_EXEMPLO,
                        UUID_HABILITADO_2_EXEMPLO,
                    ]
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    HabilitadosPorUuidsRespostaSerializer,
                    "Habilitados encontrados.",
                    {
                        "Um habilitado encontrado": {
                            "results": [EXEMPLO_HABILITADO_CONVOCADO]
                        }
                    },
                ),
                400: resposta(
                    ERRO_REQUISICAO,
                    "Lista de UUIDs ou campo de ordenação inválido.",
                    {
                        "Lista ausente": {
                            "uuids": ['O campo "uuids" é obrigatório']
                        },
                        "Item que não é UUID": {
                            "uuids": {"0": ["Must be a valid UUID."]}
                        },
                        "Ordenação inválida": {
                            "detail": ERRO_ORDENACAO_INVALIDA
                        },
                    },
                ),
            }
        ),
    ),
    "buscar_por_cpfs": extend_schema(
        operation_id="buscar_habilitados_por_cpfs",
        summary="Buscar habilitados de um processo por CPFs",
        tags=[TAG_HABILITADOS],
        description=(
            "Para cada CPF informado que tenha habilitado convocado no "
            "processo, retorna o par CPF e UUID do habilitado. CPFs sem "
            "habilitado no processo ficam fora da resposta."
        ),
        parameters=[PARAMETRO_ORDER_BY],
        request=BuscarPorCpfsSerializer,
        examples=exemplos_requisicao(
            {
                "Um CPF": {
                    "cpfs": [CPF_EXEMPLO],
                    "processo_uuid": UUID_PROCESSO_EXEMPLO,
                }
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ConcursoCandidatoCpfUuidSerializer(many=True),
                    "Pares de CPF e UUID encontrados.",
                    {
                        "CPF encontrado": {
                            "uuid": UUID_HABILITADO_EXEMPLO,
                            "cpf": CPF_EXEMPLO,
                        }
                    },
                ),
                400: resposta(
                    ERRO_REQUISICAO,
                    "Corpo da requisição ou campo de ordenação inválido.",
                    {
                        "Campos ausentes": {
                            "cpfs": ['O campo "cpfs" é obrigatório'],
                            "processo_uuid": [
                                'O campo "processo_uuid" é obrigatório'
                            ],
                        },
                        "Ordenação inválida": {
                            "detail": ERRO_ORDENACAO_INVALIDA
                        },
                    },
                ),
            }
        ),
    ),
    "mandado_judicial": extend_schema(
        operation_id="listar_habilitados_mandado_judicial",
        summary="Listar habilitados por mandado judicial",
        tags=[TAG_HABILITADOS],
        description=(
            "Lista os habilitados do concurso marcados com "
            "`mandado_judicial` que ainda não foram convocados, em ordem "
            "alfabética do nome do candidato. Retorna no máximo 300."
        ),
        parameters=[
            PARAMETRO_CONCURSO_OBRIGATORIO,
            PARAMETRO_CODIGO_CARGO,
            PARAMETRO_FIELDS,
        ],
        responses=respostas(
            {
                200: resposta(
                    ConcursoCandidatoSerializer(many=True),
                    "Habilitados por mandado judicial ainda não convocados.",
                    {
                        "Habilitado por mandado": {
                            **EXEMPLO_HABILITADO,
                            "mandado_judicial": True,
                        }
                    },
                ),
                400: RESPOSTA_CONCURSO_OBRIGATORIO,
            }
        ),
    ),
    "por_processos_e_tipo_vaga": extend_schema(
        operation_id="agregar_habilitados_por_processo",
        summary="Agregar convocados por processo e categoria",
        tags=[TAG_HABILITADOS],
        description=(
            "Para cada processo informado, retorna a quantidade e os UUIDs "
            "dos habilitados convocados nele, separados pela categoria "
            "efetiva. Processos sem convocados vêm com os totais zerados.\n\n"
            "Um item da lista que não seja UUID não é validado e resulta "
            "em erro 500."
        ),
        request=ProcessosUuidsRequisicaoSerializer,
        examples=exemplos_requisicao(
            {"Um processo": {"processo_uuids": [UUID_PROCESSO_EXEMPLO]}}
        ),
        responses=respostas(
            {
                200: resposta(
                    HabilitadosPorProcessoRespostaSerializer,
                    "Convocados de cada processo, por categoria efetiva.",
                    {"Um processo": EXEMPLO_POR_PROCESSO},
                ),
                400: erro_detalhe(
                    "Lista de processos ausente, vazia ou em outro formato.",
                    {
                        "Lista ausente ou vazia": (
                            "processo_uuids é obrigatório e deve ser uma "
                            "lista"
                        )
                    },
                ),
            }
        ),
    ),
    "extracao_dados": extend_schema(
        operation_id="extrair_dados_habilitados",
        summary="Extrair totais de habilitados e convocados",
        tags=[TAG_HABILITADOS],
        description=(
            "Retorna os totais de habilitados e de convocados, no total e "
            "por categoria efetiva, usados nos relatórios.\n\n"
            "- **Sem `filtros`**: `habilitados`, `convocados` e "
            "`nao-convocados` do concurso ou, sem `concurso_uuid`, de toda "
            "a base.\n"
            "- **Com `filtros`**: `habilitados` do escopo e, para cada ano "
            "informado, um bloco com os habilitados vinculados aos "
            "processos do ano, os convocados neles e o saldo de não "
            "convocados. Nesse caso `convocados` e `nao-convocados` não "
            "aparecem na raiz."
        ),
        request=ExtracaoDadosSerializer,
        examples=exemplos_requisicao(
            {
                "Totais do concurso": {"concurso_uuid": UUID_CONCURSO_EXEMPLO},
                "Totais por ano": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "filtros": [
                        {
                            "ano": 2025,
                            "processo_uuids": [UUID_PROCESSO_EXEMPLO],
                        },
                        {
                            "ano": 2026,
                            "processo_uuids": [UUID_PROCESSO_2_EXEMPLO],
                        },
                    ],
                },
            }
        ),
        responses=respostas(
            {
                200: resposta(
                    ExtracaoDadosRespostaSerializer,
                    "Totais do escopo consultado.",
                    {
                        "Totais do concurso": EXEMPLO_EXTRACAO_GERAL,
                        "Totais por ano": EXEMPLO_EXTRACAO_POR_ANO,
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Corpo da requisição inválido.",
                    {
                        "Filtro incompleto": {
                            "filtros": [
                                {
                                    "ano": [
                                        "Um número inteiro válido é exigido."
                                    ],
                                    "processo_uuids": [
                                        "Este campo é obrigatório."
                                    ],
                                }
                            ]
                        }
                    },
                ),
            }
        ),
    ),
}
