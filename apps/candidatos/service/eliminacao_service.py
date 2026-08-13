"""Módulo service/eliminacao_service."""

from __future__ import annotations

import logging
from typing import Any

from candidatos.models import ConcursoCandidato, ConcursoCandidatoEliminacao
from candidatos.repository import (
    ConcursoCandidatoEliminacaoRepository,
    ConcursoCandidatoRepository,
)
from django.db import transaction
from django.utils import timezone
from sigla_sdk.context import get_correlation_id

logger = logging.getLogger(__name__)


class EliminacaoService:
    """Service para aplicação de eliminação de candidatos."""

    @staticmethod
    @transaction.atomic
    def aplicar_eliminacao(
        *, candidato_uuid: Any, motivo: str = "", executado_por: str = ""
    ) -> tuple[ConcursoCandidato, ConcursoCandidatoEliminacao]:
        """Aplica eliminacao.

        Args:
            candidato_uuid: UUID do ConcursoCandidato a eliminar.
            motivo: Motivo.
            executado_por: Executado por.

        Returns:
            Tupla com os objetos criados ou atualizados.

        Raises:
            ValueError: Se o candidato já estiver eliminado.
        """
        logger.info(
            "Aplicando eliminação",
            extra={
                "correlation_id": get_correlation_id(),
                "candidato_uuid": candidato_uuid,
                "motivo": motivo,
                "executado_por": executado_por,
            },
        )
        cc = ConcursoCandidatoRepository.obter_por_uuid_for_update(
            candidato_uuid
        )
        if cc.eliminado:
            raise ValueError("Registro já está eliminado.")
        cc.eliminado = True
        cc.eliminado_em = timezone.now()
        cc.eliminado_motivo = motivo or ""
        cc.eliminado_por = executado_por or ""
        ConcursoCandidatoRepository.salvar(
            cc,
            campos_atualizacao=[
                "eliminado",
                "eliminado_em",
                "eliminado_motivo",
                "eliminado_por",
                "atualizado_em",
            ],
        )
        hist = ConcursoCandidatoEliminacaoRepository.criar(
            concurso_candidato=cc,
            motivo=motivo or "",
            executado_por=executado_por or "",
        )
        return (cc, hist)
