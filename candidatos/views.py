from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Candidato
from .serializers import (
    CandidatoSerializer, 
)


class CandidatoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing candidates
    """
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'genero', 'cidade', 'estado']
    search_fields = ['nome', 'cpf', 'email', 'cidade']
    ordering_fields = ['nome', 'data_nascimento', 'created_at']
    ordering = ['nome']
