"""Módulo serializer/concurso_candidato."""

from __future__ import annotations

from typing import Any

from candidatos.models import ConcursoCandidato
from rest_framework import serializers


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


class ConcursoCandidatoSerializer(DynamicFieldsSerializer):
    """Serializer do modelo ConcursoCandidato."""

    candidato = serializers.SerializerMethodField(read_only=True)
    reclassificacoes = serializers.SerializerMethodField(read_only=True)
    concurso_uuid = serializers.SerializerMethodField(read_only=True)
    concurso_nome = serializers.SerializerMethodField(read_only=True)
    concurso_candidato_uuid = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]

    def get_concurso_candidato_uuid(self, obj: Any) -> Any:
        """Retorna concurso candidato uuid."""
        return str(obj.uuid) if getattr(obj, "uuid", None) else None

    def get_concurso_uuid(self, obj: Any) -> Any:
        """Retorna concurso uuid."""
        if getattr(obj, "concurso_uuid", None):
            return str(obj.concurso_uuid)
        lote = getattr(obj, "lote", None)
        if lote and getattr(lote, "concurso_uuid", None):
            return str(lote.concurso_uuid)
        return None

    def get_concurso_nome(self, obj: Any) -> Any:
        """Retorna concurso nome."""
        lote = getattr(obj, "lote", None)
        if lote and getattr(lote, "concurso_nome", None):
            return lote.concurso_nome
        return None

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

    def get_reclassificacoes(self, obj: Any) -> Any:
        """Retorna reclassificacoes."""
        from candidatos.repository import (
            ConcursoCandidatoReclassificacaoRepository,
        )

        return ConcursoCandidatoReclassificacaoRepository.listar_serializado_por_concurso_candidato(  # noqa: E501
            obj
        )


class BuscarPorUuidsSerializer(serializers.Serializer):
    """Serializer para validação do payload da action buscar_por_uuids."""

    uuids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        error_messages={
            "required": 'O campo "uuids" é obrigatório',
            "empty": "A lista de UUIDs não pode estar vazia",
            "min_length": "A lista de UUIDs deve conter pelo menos 1 item",
            "invalid": 'O campo "uuids" deve ser uma lista de UUIDs válidos',
        },
    )


class BuscarPorCpfsSerializer(serializers.Serializer):
    """Serializer para validação do payload da action buscar_por_cpfs."""

    cpfs = serializers.ListField(
        child=serializers.CharField(max_length=14),
        min_length=1,
        error_messages={
            "required": 'O campo "cpfs" é obrigatório',
            "empty": "A lista de CPFs não pode estar vazia",
            "min_length": "A lista de CPFs deve conter pelo menos 1 item",
            "invalid": 'O campo "cpfs" deve ser uma lista de CPFs válidos',
        },
    )
    processo_uuid = serializers.UUIDField(
        required=True,
        error_messages={
            "required": 'O campo "processo_uuid" é obrigatório',
            "invalid": 'O campo "processo_uuid" deve ser um UUID válido',
        },
    )


class ConcursoCandidatoCpfUuidSerializer(serializers.ModelSerializer):
    """Serializer simplificado que retorna apenas o CPF do candidato e o."""

    cpf = serializers.SerializerMethodField()

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = ["uuid", "cpf"]

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
    """Payload para reclassificação explícita:."""

    candidato_uuid = serializers.UUIDField(required=True)
    desclassificar_de = serializers.ChoiceField(
        choices=[("NNA", "NNA"), ("PCD", "PCD")], required=True
    )
    nova_classificacao = serializers.ChoiceField(
        choices=[("GERAL", "GERAL"), ("NNA", "NNA"), ("PCD", "PCD")],
        required=False,
    )
    motivo = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    mandado_judicial = serializers.BooleanField(
        required=False, default=False
    )

    def validate(self, attrs: Any) -> Any:
        """Valida payload de reclassificação sem alterações adicionais."""
        return attrs


class EliminarSerializer(serializers.Serializer):
    """Payload para eliminação explícita:."""

    candidato_uuid = serializers.UUIDField(required=True)
    motivo = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class ConcursoCandidatoReclassificadoSerializer(serializers.ModelSerializer):
    """Serializer compacto para saída de reclassificados."""

    candidato = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]

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


class ConcursoCandidatoMandadoJudicialSerializer(
    serializers.ModelSerializer
):
    """Serializer enxuto para candidatos com mandado judicial."""

    candidato = serializers.SerializerMethodField(read_only=True)
    reclassificacao_judicial = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = [
            "uuid",
            "candidato",
            "categoria_efetiva",
            "classificacao",
            "classificacao_pcd",
            "classificacao_nna",
            "codigo_cargo",
            "reclassificacao_judicial",
        ]

    def get_candidato(self, obj: Any) -> Any:
        """Retorna dados mínimos do candidato para exibição na tabela.

        Args:
            obj: ConcursoCandidato sendo serializado.

        Returns:
            Dicionário com uuid, nome e cpf, ou ``None`` sem candidato.
        """
        c = obj.candidato
        if not c:
            return None
        return {"uuid": str(c.uuid), "nome": c.nome, "cpf": c.cpf}

    def get_reclassificacao_judicial(self, obj: Any) -> Any:
        """Retorna a reclassificação judicial mais recente do candidato.

        Args:
            obj: ConcursoCandidato sendo serializado.

        Returns:
            Dicionário com dados do histórico judicial, ou ``None``.
        """
        # Usa o cache do prefetch quando disponível (evita N+1); só recorre
        # ao banco se o objeto vier de um queryset sem o prefetch aplicado.
        prefetchados = getattr(obj, "reclassificacoes_judiciais", None)
        if prefetchados is not None:
            historico = prefetchados[0] if prefetchados else None
        else:
            historico = (
                obj.historicos_reclassificacao.filter(mandado_judicial=True)
                .order_by("-criado_em")
                .first()
            )
        if not historico:
            return None
        return {
            "desclassificado_de": historico.desclassificado_de,
            "motivo": historico.motivo,
            "criado_em": historico.criado_em,
        }


class LoteItemSerializer(serializers.Serializer):
    """Serializer para um item de lote (linha do arquivo TXT)."""

    lote = serializers.IntegerField()
    empresa = serializers.IntegerField()
    vaga = serializers.IntegerField()
    identificacao = serializers.CharField()
    chave_inscrito = serializers.CharField(allow_blank=True, default="")
    numfunc = serializers.CharField(allow_blank=True, default="")
    numvinc = serializers.CharField(allow_blank=True, default="")


class SalvarLotesSerializer(serializers.Serializer):
    """Serializer para o payload do endpoint salvar-lotes."""

    concurso_uuid = serializers.UUIDField()
    lotes = serializers.ListField(child=LoteItemSerializer(), min_length=1)


class ConcursoCandidatoEliminadoSerializer(serializers.ModelSerializer):
    """Serializer compacto para saída de eliminados."""

    candidato = serializers.SerializerMethodField(read_only=True)

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em", "esta_ativo"]

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
    """Serializer de filtro por ano para extração de dados de habilitados."""

    ano = serializers.IntegerField()
    processo_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
    )


class ExtracaoDadosSerializer(serializers.Serializer):
    """Serializer de habilitados e convocações para extração de dados."""

    concurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    filtros = ExtracaoDadosFiltroSerializer(
        many=True, required=False, default=list
    )
