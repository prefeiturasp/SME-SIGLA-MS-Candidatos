from rest_framework import serializers
from .models import Candidato


class CandidatoSerializer(serializers.ModelSerializer):
    idade = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidato
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
