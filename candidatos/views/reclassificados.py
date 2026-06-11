"""Módulo views/reclassificados."""

from __future__ import annotations

import logging
from typing import Any

from rest_framework import status, viewsets
from rest_framework.response import Response

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializers import ConcursoCandidatoReclassificadoSerializer

logger = logging.getLogger(__name__)


class ReclassificadosViewSet(viewsets.ViewSet):
    """Endpoint para listar candidatos reclassificados (de NNA/PCD ->."""

    def list(self, request: Any) -> Any:
        """Lista candidatos reclassificados de NNA/PCD para ampla concorrência.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resposta HTTP com os dados serializados.
        """
        concurso_uuid = request.query_params.get("concurso_uuid")
        processo_uuid = request.query_params.get("processo_uuid")
        if not concurso_uuid or not processo_uuid:
            return Response(
                {"detail": "concurso_uuid e processo_uuid são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lote = (
            ConcursoCandidatosLote.objects.filter(concurso_uuid=concurso_uuid)
            .order_by("-criado_em")
            .first()
        )
        if not lote:
            return Response({"nna": [], "pcd": []})
        base = ConcursoCandidato.objects.select_related(
            "candidato", "lote"
        ).filter(lote=lote, eliminado=False, categoria_efetiva="GERAL")
        base = base.filter(
            historicos_reclassificacao__processo_uuid=processo_uuid
        )
        qs_nna = base.filter(
            historicos_reclassificacao__desclassificado_de="NNA"
        ).distinct()
        qs_pcd = base.filter(
            historicos_reclassificacao__desclassificado_de="PCD"
        ).distinct()
        data = {
            "nna": ConcursoCandidatoReclassificadoSerializer(
                qs_nna, many=True
            ).data,
            "pcd": ConcursoCandidatoReclassificadoSerializer(
                qs_pcd, many=True
            ).data,
        }
        return Response(data)
