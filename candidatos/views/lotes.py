from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from ..models import ConcursoCandidatosLote
from ..serializer import ConcursoCandidatosLoteSerializer


class ConcursoCandidatosLoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConcursoCandidatosLote.objects.all()
    serializer_class = ConcursoCandidatosLoteSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {'concurso_uuid': ['exact']}
    ordering_fields = ['criado_em']
    ordering = ['-criado_em']
    pagination_class = None
