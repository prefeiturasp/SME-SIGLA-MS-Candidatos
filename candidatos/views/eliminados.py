"""Módulo views/eliminados."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import status, viewsets
from rest_framework.response import Response

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializers import ConcursoCandidatoEliminadoSerializer

logger = logging.getLogger(__name__)


class EliminadosViewSet(viewsets.ViewSet):
    """Endpoint para listar candidatos eliminados por concurso_uuid e."""

    def list(self, request: Any) -> Any:
        """Lista candidatos eliminados por concurso e classificação.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resposta HTTP com os dados serializados.
        """
        concurso_uuid = request.query_params.get("concurso_uuid")
        processo_uuid = request.query_params.get("processo_uuid")
        classificacao_max = request.query_params.get("classificacao_max")
        classificacao_min = request.query_params.get("classificacao_min")
        if (
            not concurso_uuid
            or not processo_uuid
            or (not classificacao_max)
            or (not classificacao_min)
        ):
            return Response(
                {
                    "detail": "concurso_uuid, processo_uuid, classificacao_max e classificacao_min são obrigatórios"  # noqa: E501
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        lote = (
            ConcursoCandidatosLote.objects.filter(concurso_uuid=concurso_uuid)
            .order_by("-criado_em")
            .first()
        )
        if not lote:
            return Response({"geral": [], "nna": [], "pcd": []})
        base = (
            ConcursoCandidato.objects.select_related("candidato", "lote")
            .filter(lote=lote, eliminado=True)
            .filter(
                classificacao__lte=classificacao_max,
                classificacao__gte=classificacao_min,
            )
            .filter(historicos_eliminacao__processo_uuid=processo_uuid)
            .distinct()
        )
        qs_nna = base.filter(classificacao_nna__isnull=False).distinct()
        qs_pcd = base.filter(classificacao_pcd__isnull=False).distinct()
        ids_excluir = list(qs_nna.values_list("id", flat=True)) + list(
            qs_pcd.values_list("id", flat=True)
        )
        qs_geral = (
            base.exclude(id__in=ids_excluir)
            .filter(classificacao__isnull=False)
            .distinct()
        )
        data = {
            "geral": ConcursoCandidatoEliminadoSerializer(
                qs_geral, many=True
            ).data,
            "nna": ConcursoCandidatoEliminadoSerializer(
                qs_nna, many=True
            ).data,
            "pcd": ConcursoCandidatoEliminadoSerializer(
                qs_pcd, many=True
            ).data,
        }
        return Response(data)
