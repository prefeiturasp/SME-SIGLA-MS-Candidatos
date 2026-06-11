"""Módulo serializer/parametrizacao."""

from rest_framework import serializers

from candidatos.models import Parametrizacao


class ParametrizacaoSerializer(serializers.ModelSerializer):
    """Serializer do modelo Parametrizacao."""

    class Meta:
        """Representa Meta."""

        model = Parametrizacao
        fields = "__all__"
        read_only_fields = ["uuid", "criado_em", "atualizado_em", "esta_ativo"]
