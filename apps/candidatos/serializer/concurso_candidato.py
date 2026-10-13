"""Módulo serializer/concurso_candidato."""

from __future__ import annotations

from typing import Any

from candidatos.constants import COTA_CHOICES
from candidatos.models import Candidato, ConcursoCandidato
from candidatos.models.concurso_candidato import CATEGORIA_CHOICES
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .descricoes import DESCRICOES_CANDIDATO, DESCRICOES_HABILITADO
from .historico_classificacao import (
    ConcursoCandidatoHistoricoClassificacaoSerializer,
)


class DynamicFieldsSerializer(serializers.ModelSerializer):
    """Serializer do modelo DynamicFields."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Inicializa a instância com os parâmetros informados."""
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class CandidatoResumoSerializer(serializers.Serializer):
    """Identificação do candidato de um habilitado."""

    id = serializers.IntegerField(**DESCRICOES_CANDIDATO["id"])
    nome = serializers.CharField(**DESCRICOES_CANDIDATO["nome"])
    cpf = serializers.CharField(**DESCRICOES_CANDIDATO["cpf"])
    email = serializers.EmailField(**DESCRICOES_CANDIDATO["email"])
    rg = serializers.CharField(allow_blank=True, **DESCRICOES_CANDIDATO["rg"])
    registro_funcional = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["registro_funcional"]
    )


class CandidatoHabilitadoSerializer(serializers.Serializer):
    """Dados pessoais do candidato de um habilitado."""

    id = serializers.IntegerField(**DESCRICOES_CANDIDATO["id"])
    uuid = serializers.UUIDField(**DESCRICOES_CANDIDATO["uuid"])
    nome = serializers.CharField(**DESCRICOES_CANDIDATO["nome"])
    cpf = serializers.CharField(**DESCRICOES_CANDIDATO["cpf"])
    email = serializers.EmailField(**DESCRICOES_CANDIDATO["email"])
    telefone = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["telefone"]
    )
    celular = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["celular"]
    )
    rg = serializers.CharField(allow_blank=True, **DESCRICOES_CANDIDATO["rg"])
    registro_funcional = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["registro_funcional"]
    )
    vinculo = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["vinculo"]
    )
    data_nascimento = serializers.DateField(
        **DESCRICOES_CANDIDATO["data_nascimento"]
    )
    genero = serializers.ChoiceField(
        choices=Candidato.GENERO_CHOICES,
        allow_blank=True,
        **DESCRICOES_CANDIDATO["genero"],
    )
    endereco = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["endereco"]
    )
    numero = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["numero"]
    )
    complemento = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["complemento"]
    )
    bairro = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["bairro"]
    )
    cidade = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["cidade"]
    )
    estado = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["estado"]
    )
    cep = serializers.CharField(
        allow_blank=True, **DESCRICOES_CANDIDATO["cep"]
    )


class ReclassificacaoHistoricoSerializer(serializers.Serializer):
    """Reclassificação registrada para um habilitado."""

    uuid = serializers.UUIDField(
        help_text="Identificador único da reclassificação."
    )
    desclassificado_de = serializers.ChoiceField(
        choices=COTA_CHOICES,
        help_text="Lista reservada da qual o habilitado foi desclassificado.",
    )
    nova_classificacao = serializers.ChoiceField(
        choices=CATEGORIA_CHOICES,
        allow_null=True,
        help_text=(
            "Categoria efetiva que o habilitado assumiu com a "
            "desclassificação."
        ),
    )
    motivo = serializers.CharField(
        allow_blank=True, help_text="Motivo informado na operação."
    )
    executado_por = serializers.CharField(
        allow_blank=True,
        help_text=(
            "Usuário que executou a operação. Vazio quando a chamada não "
            "foi autenticada."
        ),
    )
    mandado_judicial = serializers.BooleanField(
        help_text=(
            "Indica que a desclassificação foi revertida por mandado "
            "judicial e não vale mais."
        )
    )
    criado_em = serializers.DateTimeField(
        help_text="Data e hora em que a reclassificação foi registrada."
    )


class ConcursoCandidatoSerializer(DynamicFieldsSerializer):
    """Habilitado: inscrição de um candidato em um cargo de um concurso."""

    candidato = serializers.SerializerMethodField(
        read_only=True, help_text="Dados pessoais do candidato."
    )
    reclassificacoes = serializers.SerializerMethodField(
        read_only=True,
        help_text=(
            "Reclassificações do habilitado, da mais recente para a mais "
            "antiga."
        ),
    )
    historico_classificacao = serializers.SerializerMethodField(
        read_only=True,
        help_text=(
            "Pioras de classificação causadas por novas cargas da lista, "
            "da mais recente para a mais antiga."
        ),
    )
    concurso_candidato_uuid = serializers.SerializerMethodField(
        read_only=True,
        help_text="Mesmo valor de `uuid`, mantido por compatibilidade.",
    )

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]
        extra_kwargs = DESCRICOES_HABILITADO

    @extend_schema_field(OpenApiTypes.UUID)
    def get_concurso_candidato_uuid(self, obj: Any) -> Any:
        """Retorna concurso candidato uuid."""
        return str(obj.uuid) if getattr(obj, "uuid", None) else None

    @extend_schema_field(CandidatoHabilitadoSerializer)
    def get_candidato(self, obj: Any) -> Any:
        """Retorna candidato."""
        c = obj.candidato
        if not c:
            return None
        return {
            "id": c.id,
            "uuid": str(c.uuid),
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "telefone": c.telefone,
            "celular": getattr(c, "celular", ""),
            "rg": getattr(c, "rg", ""),
            "registro_funcional": getattr(c, "registro_funcional", ""),
            "vinculo": getattr(c, "vinculo", ""),
            "data_nascimento": c.data_nascimento,
            "genero": c.genero,
            "endereco": c.endereco,
            "numero": getattr(c, "numero", ""),
            "complemento": getattr(c, "complemento", ""),
            "bairro": getattr(c, "bairro", ""),
            "cidade": c.cidade,
            "estado": c.estado,
            "cep": c.cep,
        }

    @extend_schema_field(ReclassificacaoHistoricoSerializer(many=True))
    def get_reclassificacoes(self, obj: Any) -> Any:
        """Retorna reclassificacoes."""
        from candidatos.repository import (
            ConcursoCandidatoReclassificacaoRepository,
        )

        return ConcursoCandidatoReclassificacaoRepository.listar_serializado_por_concurso_candidato(  # noqa: E501
            obj
        )

    @extend_schema_field(
        ConcursoCandidatoHistoricoClassificacaoSerializer(many=True)
    )
    def get_historico_classificacao(self, obj: Any) -> Any:
        """Retorna histórico de deslocamento de classificação."""
        from candidatos.repository import (
            ConcursoCandidatoHistoricoClassificacaoRepository,
        )

        return ConcursoCandidatoHistoricoClassificacaoRepository.listar_serializado_por_concurso_candidato(  # noqa: E501
            obj
        )


class BuscarPorUuidsSerializer(serializers.Serializer):
    """Habilitados a buscar, identificados pelo UUID."""

    uuids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        error_messages={
            "required": 'O campo "uuids" é obrigatório',
            "empty": "A lista de UUIDs não pode estar vazia",
            "min_length": "A lista de UUIDs deve conter pelo menos 1 item",
            "invalid": 'O campo "uuids" deve ser uma lista de UUIDs válidos',
        },
        help_text="UUIDs dos habilitados. Ao menos um.",
    )


class BuscarPorCpfsSerializer(serializers.Serializer):
    """CPFs a localizar entre os convocados de um processo."""

    cpfs = serializers.ListField(
        child=serializers.CharField(max_length=14),
        min_length=1,
        error_messages={
            "required": 'O campo "cpfs" é obrigatório',
            "empty": "A lista de CPFs não pode estar vazia",
            "min_length": "A lista de CPFs deve conter pelo menos 1 item",
            "invalid": 'O campo "cpfs" deve ser uma lista de CPFs válidos',
        },
        help_text=(
            "CPFs dos candidatos, no mesmo formato em que estão gravados "
            "(a carga em lote grava apenas os dígitos). Ao menos um."
        ),
    )
    processo_uuid = serializers.UUIDField(
        required=True,
        error_messages={
            "required": 'O campo "processo_uuid" é obrigatório',
            "invalid": 'O campo "processo_uuid" deve ser um UUID válido',
        },
        help_text="UUID do processo de convocação em que buscar.",
    )


class ConcursoCandidatoCpfUuidSerializer(serializers.ModelSerializer):
    """Par que relaciona o CPF do candidato ao UUID do habilitado."""

    cpf = serializers.SerializerMethodField(help_text="CPF do candidato.")

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = ["uuid", "cpf"]
        extra_kwargs = {"uuid": DESCRICOES_HABILITADO["uuid"]}

    @extend_schema_field(OpenApiTypes.STR)
    def get_cpf(self, obj: Any) -> Any:
        """Retorna cpf."""
        if obj.candidato:
            return obj.candidato.cpf
        return None


class HabilitadosCalculadosParamsSerializer(serializers.Serializer):
    """Valida parâmetros de consulta contendo 'quantidade' e."""

    quantidade = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            "required": 'O parâmetro "quantidade" é obrigatório',
            "invalid": 'O parâmetro "quantidade" deve ser um número inteiro',
            "min_value": 'O parâmetro "quantidade" deve ser maior que zero',
        },
    )
    concurso_uuid = serializers.UUIDField(
        required=True,
        error_messages={
            "required": 'O parâmetro "concurso_uuid" é obrigatório',
            "invalid": 'O parâmetro "concurso_uuid" deve ser um UUID válido',
        },
    )
    processo_uuid = serializers.UUIDField(
        required=True,
        error_messages={
            "required": 'O parâmetro "processo_uuid" é obrigatório',
            "invalid": 'O parâmetro "processo_uuid" deve ser um UUID válido',
        },
    )
    codigo_cargo = serializers.CharField(
        required=False,
        error_messages={
            "required": 'O parâmetro "codigo_cargo" é obrigatório',
            "invalid": 'O parâmetro "codigo_cargo" deve ser uma string válida',
        },
    )


class ReclassificarSerializer(serializers.Serializer):
    """Reclassificação de um habilitado que concorre em lista reservada."""

    candidato_uuid = serializers.UUIDField(
        required=True, help_text="UUID do habilitado (campo `uuid`)."
    )
    desclassificar_de = serializers.ChoiceField(
        choices=COTA_CHOICES,
        required=True,
        help_text=(
            "Lista reservada da qual o habilitado sai ou, com "
            "`mandado_judicial`, à qual ele volta."
        ),
    )
    nova_classificacao = serializers.ChoiceField(
        choices=CATEGORIA_CHOICES,
        required=False,
        help_text=(
            "Aceito por compatibilidade e ignorado: a nova categoria "
            "efetiva é calculada pelo serviço."
        ),
    )
    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Motivo da reclassificação.",
    )
    mandado_judicial = serializers.BooleanField(
        required=False,
        default=False,
        help_text=(
            "Quando verdadeiro, em vez de desclassificar, reverte a "
            "desclassificação já registrada para a lista informada."
        ),
    )

    def validate(self, attrs: Any) -> Any:
        """Valida payload de reclassificação sem alterações adicionais."""
        return attrs


class EliminarSerializer(serializers.Serializer):
    """Eliminação de um habilitado."""

    candidato_uuid = serializers.UUIDField(
        required=True, help_text="UUID do habilitado (campo `uuid`)."
    )
    motivo = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Motivo da eliminação.",
    )


class ConcursoCandidatoReclassificadoSerializer(serializers.ModelSerializer):
    """Habilitado reclassificado, com a identificação do candidato."""

    candidato = serializers.SerializerMethodField(
        read_only=True, help_text="Identificação do candidato."
    )

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]
        extra_kwargs = DESCRICOES_HABILITADO

    @extend_schema_field(CandidatoResumoSerializer)
    def get_candidato(self, obj: Any) -> Any:
        """Retorna candidato."""
        c = obj.candidato
        if not c:
            return None
        return {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "rg": getattr(c, "rg", ""),
            "registro_funcional": getattr(c, "registro_funcional", ""),
        }


class LoteItemSerializer(serializers.Serializer):
    """Linha do arquivo de lote devolvido pelo SIGPEC."""

    lote = serializers.IntegerField(help_text="Número do lote.")
    empresa = serializers.IntegerField(
        help_text="Código da empresa no SIGPEC."
    )
    vaga = serializers.IntegerField(help_text="Número da vaga.")
    identificacao = serializers.CharField(
        help_text=(
            "Código de inscrição do candidato no concurso. É por ele que o "
            "habilitado é localizado."
        )
    )
    chave_inscrito = serializers.CharField(
        allow_blank=True,
        default="",
        help_text="Chave do inscrito no SIGPEC.",
    )
    numfunc = serializers.CharField(
        allow_blank=True,
        default="",
        help_text="Registro funcional (RF) gravado no candidato.",
    )
    numvinc = serializers.CharField(
        allow_blank=True,
        default="",
        help_text="Número do vínculo funcional gravado no candidato.",
    )


class SalvarLotesSerializer(serializers.Serializer):
    """Lote do SIGPEC a gravar nos habilitados de um concurso."""

    concurso_uuid = serializers.UUIDField(help_text="UUID do concurso.")
    lotes = serializers.ListField(
        child=LoteItemSerializer(),
        min_length=1,
        help_text=(
            "Linhas do arquivo de lote. O número de lote da primeira linha "
            "define o lote que é substituído."
        ),
    )


class ConcursoCandidatoEliminadoSerializer(serializers.ModelSerializer):
    """Habilitado eliminado, com a identificação do candidato."""

    candidato = serializers.SerializerMethodField(
        read_only=True, help_text="Identificação do candidato."
    )

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]
        extra_kwargs = DESCRICOES_HABILITADO

    @extend_schema_field(CandidatoResumoSerializer)
    def get_candidato(self, obj: Any) -> Any:
        """Retorna candidato."""
        c = obj.candidato
        if not c:
            return None
        return {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "email": c.email,
            "rg": getattr(c, "rg", ""),
            "registro_funcional": getattr(c, "registro_funcional", ""),
        }


class ExtracaoDadosFiltroSerializer(serializers.Serializer):
    """Processos de convocação de um ano, para quebrar os totais por ano."""

    ano = serializers.IntegerField(
        help_text="Ano. Vira a chave do bloco correspondente na resposta."
    )
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
        help_text=(
            "UUIDs dos processos de convocação do ano. Com a lista vazia, "
            "os totais do ano vêm zerados."
        ),
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Escopo da extração de totais de habilitados e convocados."""

    concurso_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=(
            "UUID do concurso. Se omitido ou nulo, os totais consideram "
            "todos os concursos."
        ),
    )
    filtros = ExtracaoDadosFiltroSerializer(
        many=True,
        required=False,
        default=list,
        help_text=(
            "Anos e respectivos processos. Se omitido ou vazio, a resposta "
            "traz os totais gerais, sem quebra por ano."
        ),
    )
