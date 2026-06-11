"""Módulo views/parametrizacao."""

from __future__ import annotations

from typing import Any

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
    """ViewSet para gerenciar parametrização de relatórios."""

    queryset = Parametrizacao.objects.all().order_by("-criado_em")
    serializer_class = ParametrizacaoSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_object(self) -> Any:
        """Retorna object.

        Returns:
            Resposta HTTP com os dados solicitados.

        Raises:
            NotFound: Quando não existir nenhum registro de parametrização.
        """
        from rest_framework.exceptions import NotFound

        obj = self.queryset.first()
        if obj is None:
            raise NotFound()
        return obj

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Rejeita criação via POST; parametrização é gerenciada por update.

        Args:
            request: Requisição HTTP recebida.
            *args: Argumentos posicionais repassados ao ViewSet.
            **kwargs: Argumentos nomeados repassados ao ViewSet.

        Returns:
            Resposta HTTP com os dados serializados.
        """
        return Response(
            {"detail": 'Method "POST" not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
