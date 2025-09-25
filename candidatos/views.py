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
    template_name_js = 'drf_spectacular/swagger_ui_inline.js'

    def _get_schema_url(self, request):
        return None

    @cached_property
    def _schema_dict(self):
        schema_path = Path(settings.BASE_DIR) / 'schema.yaml'
        with open(schema_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get_schema(self, request):
        return self._schema_dict

    def get(self, request, *args, **kwargs):
        resp = super().get(request, *args, **kwargs)
        resp.data['schema'] = json.dumps(self._get_schema(request))
        resp.data['schema_url'] = ''
        return resp
