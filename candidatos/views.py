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


class StaticSchemaView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        schema_path = Path(settings.BASE_DIR) / 'schema.yaml'
        if not schema_path.exists():
            raise Http404('schema.yaml não encontrado na raiz do projeto')
        return FileResponse(open(schema_path, 'rb'), content_type='application/yaml')