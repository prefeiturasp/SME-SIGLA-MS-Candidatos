"""Modelos de requisição e resposta usados só na documentação da API.

As views montam essas respostas diretamente. As classes daqui descrevem o
formato publicado no Swagger.
"""

from __future__ import annotations

from typing import Any

from candidatos.models.concurso_candidato import CATEGORIA_CHOICES
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from .candidato import CandidatoSerializer
from .concurso_candidato import (
    ConcursoCandidatoEliminadoSerializer,
    ConcursoCandidatoReclassificadoSerializer,
    ConcursoCandidatoSerializer,
)

AJUDA_HABILITADO_ATUALIZADO = "Habilitado após a operação."
AJUDA_HISTORICO_UUID = "UUID do registro de histórico gravado pela operação."


@extend_schema_serializer(many=False)
class CandidatoPaginadoSerializer(serializers.Serializer):
    """Página da listagem de candidatos."""

    count = serializers.IntegerField(
        help_text="Total de candidatos que atendem aos filtros."
    )
    next = serializers.URLField(
        allow_null=True,
        help_text="URL da próxima página. Nulo na última página.",
    )
    previous = serializers.URLField(
        allow_null=True,
        help_text="URL da página anterior. Nulo na primeira página.",
    )
    results = CandidatoSerializer(many=True, help_text="Candidatos da página.")


class CandidatosLoteRespostaSerializer(serializers.Serializer):
    """Resultado da carga em lote de habilitados."""

    concurso_uuid = serializers.UUIDField(
        help_text="UUID do concurso que recebeu a carga."
    )
    total_itens = serializers.IntegerField(
        help_text="Quantidade de linhas processadas, criadas ou atualizadas."
    )


class TotaisPorCategoriaSerializer(serializers.Serializer):
    """Quantidade de habilitados, no total e por categoria efetiva."""

    total = serializers.IntegerField(help_text="Soma das três categorias.")
    geral = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `GERAL`."
    )
    pcd = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `PCD`."
    )
    nna = serializers.IntegerField(
        help_text="Quantidade com categoria efetiva `NNA`."
    )


class _TotaisDeConvocacaoSerializer(serializers.Serializer):
    def get_fields(self) -> dict[str, Any]:
        """Publica ``nao_convocados`` com a chave real da resposta."""
        return {
            "nao-convocados" if nome == "nao_convocados" else nome: campo
            for nome, campo in super().get_fields().items()
        }


class ExtracaoDadosAnoSerializer(_TotaisDeConvocacaoSerializer):
    """Totais dos processos de convocação de um ano."""

    habilitados = TotaisPorCategoriaSerializer(
        help_text="Habilitados vinculados aos processos do ano."
    )
    convocados = TotaisPorCategoriaSerializer(
        help_text="Convocados nos processos do ano."
    )
    nao_convocados = TotaisPorCategoriaSerializer(
        help_text=(
            "Habilitados do escopo inteiro menos os convocados do ano, sem "
            "valores negativos."
        )
    )


class ExtracaoDadosRespostaSerializer(_TotaisDeConvocacaoSerializer):
    """Totais de habilitados e convocados do escopo consultado.

    Sem `filtros`, traz `convocados` e `nao-convocados` na raiz. Com
    `filtros`, esses dois campos saem e entra uma chave por ano informado.
    """

    habilitados = TotaisPorCategoriaSerializer(
        help_text="Habilitados do concurso ou, sem concurso, de todos."
    )
    convocados = TotaisPorCategoriaSerializer(
        required=False,
        help_text="Convocados do escopo. Presente apenas sem `filtros`.",
    )
    nao_convocados = TotaisPorCategoriaSerializer(
        required=False,
        help_text=(
            "Habilitados menos convocados. Presente apenas sem `filtros`."
        ),
    )


class ProcessosUuidsRequisicaoSerializer(serializers.Serializer):
    """Processos de convocação cujos convocados serão agregados."""

    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="UUIDs dos processos de convocação. Ao menos um.",
    )


class HabilitadosCategoriaSerializer(serializers.Serializer):
    """Convocados de um processo em uma categoria efetiva."""

    total = serializers.IntegerField(help_text="Quantidade de convocados.")
    candidatos_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs dos habilitados convocados.",
    )


class HabilitadosPorCategoriaSerializer(serializers.Serializer):
    """Convocados de um processo, separados por categoria efetiva."""

    GERAL = HabilitadosCategoriaSerializer(
        help_text="Convocados pela lista geral."
    )
    NNA = HabilitadosCategoriaSerializer(
        help_text="Convocados pela lista NNA."
    )
    PCD = HabilitadosCategoriaSerializer(
        help_text="Convocados pela lista PCD."
    )


class HabilitadosPorProcessoRespostaSerializer(serializers.Serializer):
    """Convocados por processo: cada chave é o UUID de um processo."""


class ReclassificacaoRespostaSerializer(serializers.Serializer):
    """Resultado da reclassificação de um habilitado."""

    concurso_candidato = ConcursoCandidatoSerializer(
        help_text=AJUDA_HABILITADO_ATUALIZADO
    )
    historico_uuid = serializers.UUIDField(help_text=AJUDA_HISTORICO_UUID)
    nova_categoria_efetiva = serializers.ChoiceField(
        choices=CATEGORIA_CHOICES,
        help_text="Categoria efetiva do habilitado após a operação.",
    )


class EliminacaoRespostaSerializer(serializers.Serializer):
    """Resultado da eliminação de um habilitado."""

    concurso_candidato = ConcursoCandidatoSerializer(
        help_text=AJUDA_HABILITADO_ATUALIZADO
    )
    historico_uuid = serializers.UUIDField(help_text=AJUDA_HISTORICO_UUID)
    acao = serializers.CharField(help_text="Sempre `ELIMINAR`.")


class _CorpoCompletoSerializer(serializers.Serializer):
    """Mantém os campos obrigatórios de um corpo enviado por PATCH.

    Em PATCH, o drf-spectacular marca o modelo de entrada como parcial e
    publica todos os campos como opcionais. As ações que usam estes modelos
    não são atualizações parciais: exigem o corpo como descrito.
    """

    @property
    def partial(self) -> bool:
        """Indica que o corpo nunca é tratado como parcial."""
        return False

    @partial.setter
    def partial(self, valor: bool) -> None:
        """Ignora a marcação de parcial feita na geração do schema."""


class ConvocarRequisicaoSerializer(_CorpoCompletoSerializer):
    """Habilitados a marcar como convocados em um processo."""

    concurso_uuid = serializers.UUIDField(help_text="UUID do concurso.")
    processo_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=(
            "UUID do processo de convocação gravado nos habilitados. Se "
            "omitido, eles ficam convocados sem processo."
        ),
    )
    candidatos = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text=(
            "UUIDs dos habilitados a convocar. Os que não pertencem ao "
            "concurso são ignorados."
        ),
    )


class ConvocarRespostaSerializer(serializers.Serializer):
    """Habilitados marcados como convocados."""

    atualizados = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs dos habilitados marcados como convocados.",
    )
    total = serializers.IntegerField(
        help_text="Quantidade de habilitados marcados."
    )


class DesconvocarRequisicaoSerializer(_CorpoCompletoSerializer):
    """Processo, e opcionalmente cargo, cuja convocação será desfeita."""

    processo_uuid = serializers.UUIDField(
        required=False,
        help_text=(
            "UUID do processo de convocação. Obrigatório, salvo se "
            "`concurso_uuid` for enviado no lugar."
        ),
    )
    concurso_uuid = serializers.UUIDField(
        required=False,
        help_text=(
            "Aceito no lugar de `processo_uuid` por compatibilidade. O "
            "valor é tratado como UUID do processo, não do concurso."
        ),
    )
    codigo_cargo = serializers.CharField(
        required=False,
        help_text=(
            "Restringe a operação aos convocados do cargo. Quando "
            "informado, as agendas do cargo também são removidas."
        ),
    )


class DesconvocarRespostaSerializer(serializers.Serializer):
    """Habilitados que deixaram de estar convocados."""

    desconvocados = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="UUIDs dos habilitados desconvocados.",
    )
    total = serializers.IntegerField(
        help_text="Quantidade de habilitados desconvocados."
    )
    processo_uuid = serializers.UUIDField(
        help_text="UUID do processo informado."
    )
    codigo_cargo = serializers.CharField(
        allow_null=True,
        help_text="Cargo informado. Nulo se a operação valeu para todos.",
    )


class HabilitadosPorUuidsRespostaSerializer(serializers.Serializer):
    """Habilitados localizados pelos UUIDs informados."""

    results = ConcursoCandidatoSerializer(
        many=True,
        help_text=(
            "Habilitados encontrados. UUIDs desconhecidos são ignorados."
        ),
    )


class HabilitadosCalculadosRespostaSerializer(serializers.Serializer):
    """Sequência de habilitados a convocar e percentuais aplicados."""

    quantidade = serializers.IntegerField(
        help_text="Quantidade de habilitados pedida."
    )
    concurso_uuid = serializers.UUIDField(help_text="UUID do concurso.")
    results = ConcursoCandidatoSerializer(
        many=True,
        help_text=(
            "Habilitados na ordem de convocação. Pode vir com menos itens "
            "do que o pedido se a lista se esgotar."
        ),
    )
    porcentagem_nna = serializers.FloatField(
        help_text="Fração de vagas reservada à lista NNA usada no cálculo."
    )
    porcentagem_pcd = serializers.FloatField(
        help_text="Fração de vagas reservada à lista PCD usada no cálculo."
    )


class NumeroLoteSerializer(serializers.Serializer):
    """Número de lote do SIGPEC existente no concurso."""

    numero_lote = serializers.IntegerField(help_text="Número do lote.")


class CargoLoteSerializer(serializers.Serializer):
    """Cargo que tem habilitados com lote do SIGPEC."""

    codigo_cargo = serializers.CharField(
        allow_blank=True, help_text="Código do cargo."
    )
    descricao_cargo = serializers.CharField(
        allow_blank=True, help_text="Nome do cargo."
    )


class SalvarLotesRespostaSerializer(serializers.Serializer):
    """Resultado da gravação de um lote do SIGPEC."""

    total_atualizados = serializers.IntegerField(
        help_text="Quantidade de habilitados atualizados."
    )


class ErroSalvarLotesSerializer(serializers.Serializer):
    """Falha ao gravar um lote do SIGPEC. Nada é persistido."""

    mensagem = serializers.CharField(help_text="Resumo da falha.")
    detail = serializers.CharField(
        allow_blank=True,
        help_text=(
            "Uma linha de texto por inscrição não localizada ou, em erro "
            "inesperado, a mensagem do erro."
        ),
    )


@extend_schema_serializer(many=False)
class ReclassificadosRespostaSerializer(serializers.Serializer):
    """Habilitados reclassificados em um processo, por lista de origem."""

    nna = ConcursoCandidatoReclassificadoSerializer(
        many=True,
        help_text="Saíram da lista NNA e passaram a concorrer pela geral.",
    )
    pcd = ConcursoCandidatoReclassificadoSerializer(
        many=True,
        help_text="Saíram da lista PCD e passaram a concorrer pela geral.",
    )


@extend_schema_serializer(many=False)
class EliminadosRespostaSerializer(serializers.Serializer):
    """Habilitados eliminados em um processo, por lista em que concorriam."""

    geral = ConcursoCandidatoEliminadoSerializer(
        many=True,
        help_text="Eliminados que concorriam apenas na lista geral.",
    )
    nna = ConcursoCandidatoEliminadoSerializer(
        many=True, help_text="Eliminados que concorriam na lista NNA."
    )
    pcd = ConcursoCandidatoEliminadoSerializer(
        many=True, help_text="Eliminados que concorriam na lista PCD."
    )
