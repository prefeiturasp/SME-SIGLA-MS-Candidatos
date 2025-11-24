from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from candidatos.models import Candidato, ConcursoCandidato
from candidatos.serializers import (
    CandidatoSerializer,
    CandidatosLoteCreateSerializer,
)
from candidatos.service.candidato_lote_service import processar_criacao_candidatos_lote


class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'genero', 'cidade', 'estado']
    search_fields = ['nome', 'cpf', 'email', 'cidade']
    ordering_fields = ['nome', 'data_nascimento', 'created_at']
    ordering = ['nome']

    def create(self, request, *args, **kwargs):
        input_serializer = CandidatosLoteCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        resp_data, status_code = processar_criacao_candidatos_lote(input_serializer.validated_data)
        return Response(resp_data, status=status_code)
