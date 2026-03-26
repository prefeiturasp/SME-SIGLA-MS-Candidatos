from rest_framework import serializers
from ..models import ConcursoCandidatosLote


class ConcursoCandidatosLoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcursoCandidatosLote
        fields = ['uuid', 'concurso_uuid', 'concurso_nome', 'criado_em']
