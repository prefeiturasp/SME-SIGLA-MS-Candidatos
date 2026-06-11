"""Módulo serializer/concurso_candidato."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from candidatos.models import ConcursoCandidato


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
        """Retorna concurso candidato uuid.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
        return str(obj.uuid) if getattr(obj, "uuid", None) else None

    def get_concurso_uuid(self, obj: Any) -> Any:
        """Retorna concurso uuid.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
        if getattr(obj, "concurso_uuid", None):
            return str(obj.concurso_uuid)
        lote = getattr(obj, "lote", None)
        if lote and getattr(lote, "concurso_uuid", None):
            return str(lote.concurso_uuid)
        return None

    def get_concurso_nome(self, obj: Any) -> Any:
        """Retorna concurso nome.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
        lote = getattr(obj, "lote", None)
        if lote and getattr(lote, "concurso_nome", None):
            return lote.concurso_nome
        return None

    def get_candidato(self, obj: Any) -> Any:
        """Retorna candidato.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
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
        """Retorna reclassificacoes.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
        try:
            historicos = getattr(obj, "historicos_reclassificacao", None)
            if historicos is None:
                return []
            items = []
            for h in historicos.all().order_by("-criado_em"):
                items.append(
                    {
                        "uuid": str(getattr(h, "uuid", ""))
                        if getattr(h, "uuid", None)
                        else None,
                        "desclassificado_de": getattr(
                            h, "desclassificado_de", None
                        ),
                        "nova_classificacao": getattr(
                            h, "nova_classificacao", None
                        ),
                        "motivo": getattr(h, "motivo", ""),
                        "executado_por": getattr(h, "executado_por", ""),
                        "criado_em": getattr(h, "criado_em", None),
                    }
                )
            return items
        except Exception:
            return []


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
        """Retorna cpf.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
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
        """Retorna candidato.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
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
        """Retorna candidato.

        Args:
            obj: Instância de ConcursoCandidato sendo serializada.

        Returns:
            Valor do campo serializado.
        """
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
