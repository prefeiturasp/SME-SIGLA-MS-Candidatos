from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from candidatos.models import Parametrizacao
from candidatos.serializer import ParametrizacaoSerializer


class ParametrizacaoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet para gerenciar parametrização de relatórios.
    Sempre trabalha com o registro mais recente.
    """

    queryset = Parametrizacao.objects.all().order_by("-criado_em")
    serializer_class = ParametrizacaoSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_object(self):
        """Sempre retorna o registro mais recente, ignorando o pk."""
        from rest_framework.exceptions import NotFound

        obj = self.queryset.first()
        if obj is None:
            raise NotFound()
        return obj

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": 'Method "POST" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
