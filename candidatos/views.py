from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Candidato
from .serializers import (
    CandidatoSerializer, 
)
from rest_framework.views import APIView
from drf_spectacular.views import SpectacularSwaggerView
from django.utils.functional import cached_property
import yaml
import json


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


class SwaggerFromFileView(SpectacularSwaggerView):
    def _get_schema_url(self, request):
        url = super()._get_schema_url(request)
        url_com_prefixo = f'{settings.MS_PATH}{url}'
        return url_com_prefixo
