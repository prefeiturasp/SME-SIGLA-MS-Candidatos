"""Documentação OpenAPI das operações de candidatos."""

from __future__ import annotations

from candidatos.models import Candidato
from candidatos.serializers import (
    CandidatoPaginadoSerializer,
    CandidatoSerializer,
    CandidatosLoteCreateSerializer,
    CandidatosLoteRespostaSerializer,
)
from core.openapi import exemplos_requisicao, resposta, respostas
from core.serializers import ErrosValidacaoSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from .comuns import (
    AVISO_LEGADO,
    CODIGO_CARGO_EXEMPLO,
    CPF_EXEMPLO,
    EXEMPLO_HABILITADO,
    NOME_CARGO_EXEMPLO,
    NOME_CONCURSO_EXEMPLO,
    UUID_CANDIDATO_EXEMPLO,
    UUID_CONCURSO_EXEMPLO,
    erro_detalhe,
)

EXEMPLO_DADOS_CANDIDATO = {
    "nome": "Maria Aparecida da Silva",
    "cpf": CPF_EXEMPLO,
    "email": "maria.silva@exemplo.test",
    "telefone": "1133334444",
    "celular": "11988887777",
    "rg": "123456789",
    "registro_funcional": "1234567",
    "vinculo": "1",
    "data_nascimento": "1988-04-12",
    "genero": "F",
    "endereco": "Rua das Flores",
    "numero": "123",
    "complemento": "Apto 45",
    "bairro": "Vila Mariana",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "04101000",
    "status": "ativo",
    "observacoes": "",
}

EXEMPLO_CANDIDATO = {
    "id": 4821,
    "concursos": [EXEMPLO_HABILITADO],
    "uuid": UUID_CANDIDATO_EXEMPLO,
    "criado_em": "2026-08-20T09:00:00-03:00",
    "atualizado_em": "2026-09-15T09:00:00-03:00",
    "esta_ativo": True,
    **EXEMPLO_DADOS_CANDIDATO,
}

EXEMPLO_PAGINA = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [EXEMPLO_CANDIDATO],
}

EXEMPLO_LINHA_LISTA = {
    "nome": "Maria Aparecida da Silva",
    "data_nascimento": "12/04/1988",
    "sexo": "2",
    "rg": "123456789",
    "cpf": "123.456.789-09",
    "endereco": "Rua das Flores",
    "numero": "123",
    "complemento": "Apto 45",
    "bairro": "Vila Mariana",
    "cep": "04101000",
    "cidade": "São Paulo",
    "uf": "SP",
    "telefone": "1133334444",
    "celular": "11988887777",
    "email": "maria.silva@exemplo.test",
    "codigo_inscricao": "0012345",
    "classificacao": "12",
    "pontos": "87.5",
    "classificacao_deficiente": "",
    "opcao_concurso": "01",
    "codigo_cargo": CODIGO_CARGO_EXEMPLO,
    "descricao_cargo": NOME_CARGO_EXEMPLO,
    "classificacao_nna": "3",
    "ano_concurso": "2025",
}

ERRO_CANDIDATO_INEXISTENTE = "No Candidato matches the given query."

PARAMETRO_UUID = OpenApiParameter(
    name="uuid",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description="UUID do candidato.",
)

PARAMETROS_LISTAGEM = [
    OpenApiParameter(
        name="status",
        type=OpenApiTypes.STR,
        enum=[codigo for codigo, _ in Candidato.STATUS_CHOICES],
        description="Retorna apenas os candidatos na situação informada.",
    ),
    OpenApiParameter(
        name="genero",
        type=OpenApiTypes.STR,
        enum=[codigo for codigo, _ in Candidato.GENERO_CHOICES],
        description=(
            "Retorna apenas os candidatos do gênero informado: `M` "
            "(masculino), `F` (feminino), `O` (outro) ou `N` (prefere não "
            "informar)."
        ),
    ),
    OpenApiParameter(
        name="cidade",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas os candidatos da cidade informada. A "
            "comparação é pelo texto exato."
        ),
    ),
    OpenApiParameter(
        name="estado",
        type=OpenApiTypes.STR,
        description=(
            "Retorna apenas os candidatos da unidade federativa informada, "
            "pela sigla exata."
        ),
    ),
    OpenApiParameter(
        name="search",
        type=OpenApiTypes.STR,
        description=(
            "Busca por trecho em nome, CPF, e-mail, cidade, RG ou registro "
            "funcional."
        ),
    ),
    OpenApiParameter(
        name="ordering",
        type=OpenApiTypes.STR,
        description=(
            "Campo de ordenação: `nome` ou `data_nascimento`. Prefixe com "
            "`-` para ordem decrescente. Padrão: `nome`."
        ),
    ),
    OpenApiParameter(
        name="page",
        type=OpenApiTypes.INT,
        description="Número da página, a partir de 1.",
    ),
]

PARAMETROS_BUSCA = [
    OpenApiParameter(
        name="nome",
        type=OpenApiTypes.STR,
        description="Trecho do nome do candidato.",
    ),
    OpenApiParameter(
        name="cpf",
        type=OpenApiTypes.STR,
        description=(
            "Trecho do CPF, como está gravado. A carga em lote grava "
            "apenas os dígitos."
        ),
    ),
    OpenApiParameter(
        name="rg",
        type=OpenApiTypes.STR,
        description="Trecho do RG.",
    ),
    OpenApiParameter(
        name="registro_funcional",
        type=OpenApiTypes.STR,
        description="Trecho do registro funcional.",
    ),
]

RESPOSTA_CANDIDATO = resposta(
    CandidatoSerializer,
    "Candidato com os seus habilitados.",
    {"Candidato": EXEMPLO_CANDIDATO},
)

RESPOSTA_CANDIDATO_INEXISTENTE = erro_detalhe(
    "Candidato não encontrado.",
    {"Não encontrado": ERRO_CANDIDATO_INEXISTENTE},
)

RESPOSTA_CANDIDATO_INVALIDO = resposta(
    ErrosValidacaoSerializer,
    "Dados do candidato inválidos.",
    {"E-mail inválido": {"email": ["Insira um endereço de email válido."]}},
)

OPERACOES_CANDIDATOS = {
    "list": extend_schema(
        operation_id="listar_candidatos",
        summary="Listar candidatos",
        description=(
            "Lista os candidatos cadastrados em ordem alfabética de nome, "
            "cada um com os seus habilitados. Os filtros podem ser "
            "combinados. A resposta é paginada, com 20 candidatos por "
            "página."
        ),
        filters=False,
        parameters=PARAMETROS_LISTAGEM,
        responses=respostas(
            {
                200: resposta(
                    CandidatoPaginadoSerializer,
                    "Página de candidatos.",
                    {"Página única": EXEMPLO_PAGINA},
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Filtro `status` ou `genero` com valor inválido.",
                    {
                        "Situação inexistente": {
                            "status": [
                                "Faça uma escolha válida. xyz não é uma "
                                "das escolhas disponíveis."
                            ]
                        }
                    },
                ),
                404: erro_detalhe(
                    "Página além da última.",
                    {"Página inexistente": "Página inválida."},
                ),
            }
        ),
    ),
    "create": extend_schema(
        operation_id="criar_candidatos_em_lote",
        summary="Carregar a lista de habilitados de um concurso",
        description=(
            "Recebe a lista de classificação de um concurso e grava, linha "
            "a linha, o candidato e o seu habilitado. É a operação usada "
            "pela importação de arquivos.\n\n"
            "- O **candidato** é localizado pelo CPF, considerando só os "
            "dígitos. Se já existe, os dados pessoais são atualizados; "
            "senão, ele é criado.\n"
            "- O **habilitado** é localizado por CPF, cargo e concurso. Se "
            "já existe, os dados da inscrição são atualizados e, quando "
            "alguma classificação piora, a mudança entra no histórico de "
            "classificação; senão, ele é criado.\n"
            "- A **categoria efetiva** sai das classificações enviadas: "
            "`PCD` se há classificação PCD, `NNA` se há classificação NNA "
            "e `GERAL` nos demais casos.\n\n"
            "As linhas são gravadas uma a uma, sem transação única: se uma "
            "linha causar erro inesperado, as anteriores continuam "
            "gravadas."
        ),
        request=CandidatosLoteCreateSerializer,
        examples=exemplos_requisicao(
            {
                "Lista com um habilitado": {
                    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                    "concurso_nome": NOME_CONCURSO_EXEMPLO,
                    "candidatos": [EXEMPLO_LINHA_LISTA],
                }
            }
        ),
        responses=respostas(
            {
                201: resposta(
                    CandidatosLoteRespostaSerializer,
                    "Lista gravada.",
                    {
                        "Uma linha processada": {
                            "concurso_uuid": UUID_CONCURSO_EXEMPLO,
                            "total_itens": 1,
                        }
                    },
                ),
                400: resposta(
                    ErrosValidacaoSerializer,
                    "Corpo da requisição inválido. Nada é gravado.",
                    {
                        "Concurso e inscrição ausentes": {
                            "concurso_uuid": ["Este campo é obrigatório."],
                            "candidatos": [
                                {
                                    "codigo_inscricao": [
                                        "Este campo é obrigatório."
                                    ]
                                }
                            ],
                        }
                    },
                ),
            }
        ),
    ),
    "retrieve": extend_schema(
        operation_id="detalhar_candidato",
        summary="Detalhar candidato",
        description="Retorna um candidato com todos os seus habilitados.",
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {200: RESPOSTA_CANDIDATO, 404: RESPOSTA_CANDIDATO_INEXISTENTE}
        ),
    ),
    "update": extend_schema(
        operation_id="atualizar_candidato",
        summary="Atualizar candidato",
        description=(
            f"{AVISO_LEGADO} Para alterar dados pessoais, use a "
            "atualização parcial.\n\n"
            "Substitui os dados pessoais do candidato. `nome`, `cpf` e "
            "`email` são obrigatórios. Os habilitados não são alterados."
        ),
        deprecated=True,
        parameters=[PARAMETRO_UUID],
        request=CandidatoSerializer,
        examples=exemplos_requisicao(
            {"Atualização completa": EXEMPLO_DADOS_CANDIDATO}
        ),
        responses=respostas(
            {
                200: RESPOSTA_CANDIDATO,
                400: RESPOSTA_CANDIDATO_INVALIDO,
                404: RESPOSTA_CANDIDATO_INEXISTENTE,
            }
        ),
    ),
    "partial_update": extend_schema(
        operation_id="atualizar_parcial_candidato",
        summary="Atualizar parcialmente candidato",
        description=(
            "Atualiza apenas os dados pessoais enviados. Os habilitados "
            "não são alterados por esta operação."
        ),
        parameters=[PARAMETRO_UUID],
        request=CandidatoSerializer,
        examples=exemplos_requisicao(
            {
                "Corrigir contato": {
                    "email": "maria.aparecida@exemplo.test",
                    "celular": "11977776666",
                }
            }
        ),
        responses=respostas(
            {
                200: RESPOSTA_CANDIDATO,
                400: RESPOSTA_CANDIDATO_INVALIDO,
                404: RESPOSTA_CANDIDATO_INEXISTENTE,
            }
        ),
    ),
    "destroy": extend_schema(
        operation_id="excluir_candidato",
        summary="Excluir candidato",
        description=(
            f"{AVISO_LEGADO}\n\n"
            "Exclui o candidato **e todos os seus habilitados**, com os "
            "históricos de reclassificação, eliminação e classificação. A "
            "exclusão é definitiva."
        ),
        deprecated=True,
        parameters=[PARAMETRO_UUID],
        responses=respostas(
            {
                204: resposta(None, "Candidato excluído."),
                404: RESPOSTA_CANDIDATO_INEXISTENTE,
            }
        ),
    ),
    "buscar": extend_schema(
        operation_id="buscar_candidatos",
        summary="Buscar candidatos por nome, CPF, RG ou registro funcional",
        description=(
            "Busca candidatos por trecho de nome, CPF, RG ou registro "
            "funcional, sem diferenciar maiúsculas de minúsculas. Informe "
            "ao menos um parâmetro; os informados são combinados, e todos "
            "precisam casar.\n\n"
            "A busca percorre os habilitados e considera no máximo 300, "
            "ordenados pelo nome do candidato. Cada candidato vem uma vez, "
            "e `concursos` traz apenas os habilitados considerados na "
            "busca. Candidatos sem habilitado não aparecem. A resposta não "
            "é paginada."
        ),
        parameters=PARAMETROS_BUSCA,
        responses=respostas(
            {
                200: resposta(
                    CandidatoSerializer(many=True),
                    "Candidatos encontrados. Lista vazia se nenhum casa.",
                    {"Candidato": EXEMPLO_CANDIDATO},
                ),
                400: erro_detalhe(
                    "Nenhum parâmetro de busca informado.",
                    {
                        "Sem parâmetros": (
                            "Informe pelo menos um parâmetro: nome, cpf, rg "
                            "ou registro_funcional."
                        )
                    },
                ),
            }
        ),
    ),
}
