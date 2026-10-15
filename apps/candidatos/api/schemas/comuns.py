"""Blocos reutilizados na documentação OpenAPI do app candidatos."""

from __future__ import annotations

from typing import Any

from candidatos.serializers import (
    ConcursoCandidatoSerializer,
    ExtracaoDadosAnoSerializer,
    ExtracaoDadosRespostaSerializer,
    HabilitadosPorCategoriaSerializer,
    HabilitadosPorProcessoRespostaSerializer,
)
from core.openapi import resposta
from core.serializers import ErroDetalheSerializer
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    Direction,
    OpenApiParameter,
    OpenApiResponse,
)

TAG_CANDIDATOS = "Candidatos"
TAG_HABILITADOS = "Habilitados"
TAG_CONVOCACAO = "Convocação de habilitados"
TAG_RECLASSIFICACAO = "Reclassificação e eliminação"
TAG_LOTES = "Lotes SIGPEC"

AVISO_LEGADO = (
    "**Rota legada**, herdada do CRUD genérico e sem uso pelos serviços do "
    "SIGLA. Não adote em novos consumidores."
)
AVISO_UUID_INVALIDO = (
    "Um valor que não seja UUID não é validado e resulta em erro 500."
)

UUID_CONCURSO_EXEMPLO = "7e6d5c4b-3a2f-4e1d-9c8b-7a6f5e4d3c2b"
NOME_CONCURSO_EXEMPLO = "Concurso Professor de Educação Infantil 2025"
UUID_PROCESSO_EXEMPLO = "c1a7e0d2-4b3f-4a6e-8d9c-0f1e2d3c4b5a"
UUID_PROCESSO_2_EXEMPLO = "a9b8c7d6-e5f4-4a3b-8c2d-1e0f9a8b7c6d"
UUID_HABILITADO_EXEMPLO = "0d9e8f7a-6b5c-4d3e-a2f1-b0c9d8e7f6a5"
UUID_HABILITADO_2_EXEMPLO = "3b2a1c0d-9e8f-4a7b-b6c5-d4e3f2a1b0c9"
UUID_CANDIDATO_EXEMPLO = "5a4b3c2d-1e0f-4a9b-8c7d-6e5f4a3b2c1d"
UUID_HISTORICO_EXEMPLO = "6f5e4d3c-2b1a-4f0e-9d8c-7b6a5f4e3d2c"
CODIGO_CARGO_EXEMPLO = "3859"
NOME_CARGO_EXEMPLO = "Professor de Educação Infantil"
CPF_EXEMPLO = "12345678909"

EXEMPLO_CANDIDATO_RESUMO = {
    "id": 4821,
    "nome": "Maria Aparecida da Silva",
    "cpf": CPF_EXEMPLO,
    "email": "maria.silva@exemplo.test",
    "rg": "123456789",
    "registro_funcional": "1234567",
}

EXEMPLO_CANDIDATO_HABILITADO = {
    "id": 4821,
    "uuid": UUID_CANDIDATO_EXEMPLO,
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
}

EXEMPLO_DADOS_HABILITADO = {
    "concurso_uuid": UUID_CONCURSO_EXEMPLO,
    "concurso_nome": NOME_CONCURSO_EXEMPLO,
    "codigo_inscricao": "0012345",
    "pontos": 87.5,
    "opcao_concurso": "01",
    "codigo_cargo": CODIGO_CARGO_EXEMPLO,
    "processo_uuid": None,
    "cota": "",
    "descricao_cargo": NOME_CARGO_EXEMPLO,
    "df": "",
    "classificacao": 12,
    "classificacao_pcd": None,
    "classificacao_nna": 3,
    "ano_concurso": "2025",
    "observacao": "",
    "foi_convocado": False,
    "data_convocacao": None,
    "mandado_judicial": False,
    "ranking": 0,
    "ranking_escolha": 0,
    "categoria_efetiva": "NNA",
    "promovido_para_geral": False,
    "promovido_de": None,
    "promovido_em": None,
    "eliminado": False,
    "eliminado_em": None,
    "eliminado_motivo": "",
    "eliminado_por": "",
    "numero_lote": None,
    "codigo_sigpec": None,
    "numero_vaga": None,
    "chave_inscrito": None,
}

EXEMPLO_REGISTRO_HABILITADO = {
    "uuid": UUID_HABILITADO_EXEMPLO,
    "criado_em": "2026-08-20T09:00:00-03:00",
    "atualizado_em": "2026-09-15T09:00:00-03:00",
    "esta_ativo": True,
    **EXEMPLO_DADOS_HABILITADO,
}

EXEMPLO_HABILITADO = {
    "id": 15230,
    "candidato": EXEMPLO_CANDIDATO_HABILITADO,
    "reclassificacoes": [],
    "historico_classificacao": [],
    "concurso_candidato_uuid": UUID_HABILITADO_EXEMPLO,
    **EXEMPLO_REGISTRO_HABILITADO,
}

EXEMPLO_HABILITADO_RESUMIDO = {
    "id": 15230,
    "candidato": EXEMPLO_CANDIDATO_RESUMO,
    **EXEMPLO_REGISTRO_HABILITADO,
}

CONVOCACAO_EXEMPLO = {
    "processo_uuid": UUID_PROCESSO_EXEMPLO,
    "foi_convocado": True,
    "data_convocacao": "2026-09-15T09:00:00-03:00",
    "ranking": 1,
    "ranking_escolha": 1,
}

EXEMPLO_HABILITADO_CONVOCADO = {**EXEMPLO_HABILITADO, **CONVOCACAO_EXEMPLO}

EXEMPLO_HABILITADO_NA_SEQUENCIA = {
    **EXEMPLO_HABILITADO,
    "ranking": 1,
    "ranking_escolha": 1,
}

ERRO_HABILITADO_INEXISTENTE = {
    "detail": "No ConcursoCandidato matches the given query."
}
ERRO_CONCURSO_OBRIGATORIO = {"detail": "concurso_uuid é obrigatório"}

PARAMETRO_FIELDS = OpenApiParameter(
    name="fields",
    type=OpenApiTypes.STR,
    description=(
        "Campos do habilitado a devolver, separados por vírgula, por "
        "exemplo `uuid,classificacao,candidato`. Os demais são omitidos da "
        "resposta. Sem o parâmetro, vêm todos."
    ),
)

PARAMETRO_CONCURSO_OBRIGATORIO = OpenApiParameter(
    name="concurso_uuid",
    type=OpenApiTypes.UUID,
    required=True,
    description=f"UUID do concurso. {AVISO_UUID_INVALIDO}",
)

PARAMETRO_CODIGO_CARGO = OpenApiParameter(
    name="codigo_cargo",
    type=OpenApiTypes.STR,
    description="Restringe o resultado ao cargo informado.",
)

PARAMETRO_ORDER_BY = OpenApiParameter(
    name="order_by",
    type=OpenApiTypes.STR,
    description=(
        "Campo do habilitado usado na ordenação. Prefixe com `-` para "
        "ordem decrescente. Padrão: `classificacao`."
    ),
)

RESPOSTA_HABILITADOS = resposta(
    ConcursoCandidatoSerializer(many=True),
    "Habilitados encontrados. Lista vazia se nenhum atende à consulta.",
    {"Habilitado": EXEMPLO_HABILITADO},
)

RESPOSTA_SEQUENCIA_HABILITADOS = resposta(
    ConcursoCandidatoSerializer(many=True),
    "Habilitados na ordem calculada. Lista vazia se não há elegíveis.",
    {"Habilitado na sequência": EXEMPLO_HABILITADO_NA_SEQUENCIA},
)

RESPOSTA_HABILITADO_INEXISTENTE = resposta(
    ErroDetalheSerializer,
    "Habilitado não encontrado.",
    {"Não encontrado": ERRO_HABILITADO_INEXISTENTE},
)


def erro_detalhe(descricao: str, mensagens: dict[str, str]) -> OpenApiResponse:
    """Monta uma resposta de erro com mensagem única.

    Args:
        descricao: Texto exibido para o código de resposta.
        mensagens: Mensagens de erro, indexadas pelo nome do exemplo.

    Returns:
        Resposta pronta para o ``responses`` de ``extend_schema``.
    """
    return resposta(
        ErroDetalheSerializer,
        descricao,
        {nome: {"detail": mensagem} for nome, mensagem in mensagens.items()},
    )


RESPOSTA_CONCURSO_OBRIGATORIO = erro_detalhe(
    "Parâmetro `concurso_uuid` ausente.",
    {"Concurso não informado": ERRO_CONCURSO_OBRIGATORIO["detail"]},
)


class HabilitadosPorProcessoExtension(OpenApiSerializerExtension):
    """Descreve a resposta como mapa de processo para convocados."""

    target_class = HabilitadosPorProcessoRespostaSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema do mapa de processos."""
        return {
            "type": "object",
            "description": (
                "Convocados por processo. Cada chave é o UUID de um "
                "processo informado na requisição, e o valor traz os "
                "convocados dele por categoria efetiva."
            ),
            "additionalProperties": auto_schema.resolve_serializer(
                HabilitadosPorCategoriaSerializer, direction
            ).ref,
        }


class ExtracaoDadosRespostaExtension(OpenApiSerializerExtension):
    """Acrescenta as chaves de ano aos totais da extração de dados."""

    target_class = ExtracaoDadosRespostaSerializer

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        """Retorna o schema dos totais, com uma chave por ano."""
        esquema = auto_schema._map_serializer(
            self.target, direction, bypass_extensions=True
        )
        esquema["additionalProperties"] = auto_schema.resolve_serializer(
            ExtracaoDadosAnoSerializer, direction
        ).ref
        return esquema
