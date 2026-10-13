"""Módulo serializer/historico_classificacao."""

from candidatos.models import ConcursoCandidatoHistoricoClassificacao
from rest_framework import serializers

from .descricoes import DESCRICOES_HISTORICO_CLASSIFICACAO


class ConcursoCandidatoHistoricoClassificacaoSerializer(
    serializers.ModelSerializer
):
    """Piora de classificação de um habilitado após nova carga da lista."""

    class Meta:
        """Representa Meta."""

        model = ConcursoCandidatoHistoricoClassificacao
        fields = [
            "uuid",
            "classificacao_anterior",
            "classificacao_nova",
            "classificacao_nna_anterior",
            "classificacao_nna_nova",
            "classificacao_pcd_anterior",
            "classificacao_pcd_nova",
            "foi_convocado",
            "motivo",
            "criado_em",
        ]
        read_only_fields = fields
        extra_kwargs = DESCRICOES_HISTORICO_CLASSIFICACAO
