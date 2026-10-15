"""Módulo serializer/parametrizacao."""

from parametrizacao.models import Parametrizacao
from rest_framework import serializers

DESCRICOES_CAMPOS = {
    "id": {"help_text": "Identificador numérico interno da parametrização."},
    "uuid": {"help_text": "Identificador único da parametrização."},
    "criado_em": {"help_text": "Data e hora de criação do registro."},
    "atualizado_em": {
        "help_text": "Data e hora da última atualização do registro."
    },
    "esta_ativo": {"help_text": "Indica se o registro está ativo."},
    "porcentagem_pcd": {
        "help_text": (
            "Fração das vagas reservada à lista PCD no cálculo da "
            "convocação (0.05 = 5%)."
        )
    },
    "porcentagem_nna": {
        "help_text": (
            "Fração das vagas reservada à lista NNA no cálculo da "
            "convocação (0.2 = 20%)."
        )
    },
}


class ParametrizacaoSerializer(serializers.ModelSerializer):
    """Percentuais de reserva de vagas usados no cálculo da convocação."""

    class Meta:
        """Representa Meta."""

        model = Parametrizacao
        fields = "__all__"
        read_only_fields = ["uuid", "criado_em", "atualizado_em", "esta_ativo"]
        extra_kwargs = DESCRICOES_CAMPOS
