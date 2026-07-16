"""Módulo views/eliminados."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import status, viewsets
from rest_framework.response import Response

from candidatos.repository import (
    ConcursoCandidatoRepository,
    ConcursoCandidatosLoteRepository,
)

logger = logging.getLogger(__name__)


class EliminadosViewSet(viewsets.ViewSet):
    """Endpoint para listar candidatos eliminados por concurso_uuid e."""

    def list(self, request: Any) -> Any:
        """Lista candidatos eliminados por concurso e classificação."""
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
        lote = ConcursoCandidatosLoteRepository.obter_ultimo_por_concurso(
            concurso_uuid
        )
        if not lote:
            return Response({"geral": [], "nna": [], "pcd": []})
        base = ConcursoCandidatoRepository.filtrar_eliminados_por_processo_e_classificacao(
            lote=lote,
            processo_uuid=processo_uuid,
            classificacao_min=classificacao_min,
            classificacao_max=classificacao_max,
        )
        qs_nna = base.filter(classificacao_nna__isnull=False).distinct()
        qs_pcd = base.filter(classificacao_pcd__isnull=False).distinct()
        ids_excluir = list(
            ConcursoCandidatoRepository.listar_ids(qs_nna)
        ) + list(ConcursoCandidatoRepository.listar_ids(qs_pcd))
        qs_geral = (
            base.exclude(id__in=ids_excluir)
            .filter(classificacao__isnull=False)
            .distinct()
        )
        data = {
            "geral": ConcursoCandidatoRepository.serializar_eliminados(
                qs_geral
            ),
            "nna": ConcursoCandidatoRepository.serializar_eliminados(qs_nna),
            "pcd": ConcursoCandidatoRepository.serializar_eliminados(qs_pcd),
        }
        return Response(data)
