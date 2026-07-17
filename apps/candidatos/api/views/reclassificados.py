"""Módulo views/reclassificados."""

from __future__ import annotations

import logging
from typing import Any

from candidatos.repository import (
    ConcursoCandidatoRepository,
    ConcursoCandidatosLoteRepository,
)
from rest_framework import status, viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class ReclassificadosViewSet(viewsets.ViewSet):
    """Endpoint para listar candidatos reclassificados (de NNA/PCD ->."""

    def list(self, request: Any) -> Any:
        """Lista reclassificados de NNA/PCD para ampla concorrência."""
        concurso_uuid = request.query_params.get("concurso_uuid")
        processo_uuid = request.query_params.get("processo_uuid")
        if not concurso_uuid or not processo_uuid:
            return Response(
                {"detail": "concurso_uuid e processo_uuid são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lote = ConcursoCandidatosLoteRepository.obter_ultimo_por_concurso(
            concurso_uuid
        )
        if not lote:
            return Response({"nna": [], "pcd": []})
        qs_nna = (
            ConcursoCandidatoRepository.filtrar_reclassificados_por_processo(
                lote=lote,
                processo_uuid=processo_uuid,
                desclassificado_de="NNA",
            )
        )
        qs_pcd = (
            ConcursoCandidatoRepository.filtrar_reclassificados_por_processo(
                lote=lote,
                processo_uuid=processo_uuid,
                desclassificado_de="PCD",
            )
        )
        data = {
            "nna": ConcursoCandidatoRepository.serializar_reclassificados(
                qs_nna
            ),
            "pcd": ConcursoCandidatoRepository.serializar_reclassificados(
                qs_pcd
            ),
        }
        return Response(data)
