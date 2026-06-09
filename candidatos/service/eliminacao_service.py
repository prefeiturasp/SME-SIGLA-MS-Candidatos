"""Módulo service/eliminacao_service."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone
from sigla_sdk.context import get_correlation_id

from candidatos.models import ConcursoCandidato, ConcursoCandidatoEliminacao

logger = logging.getLogger(__name__)


@transaction.atomic
def aplicar_eliminacao(
    *, candidato_uuid: Any, motivo: str = "", executado_por: str = ""
) -> tuple[ConcursoCandidato, ConcursoCandidatoEliminacao]:
    """Executa aplicar eliminacao.

    Args:
        candidato_uuid: Parâmetro candidato uuid.
        motivo: Parâmetro motivo.
        executado_por: Parâmetro executado por.

    Returns:
        Resultado da operação.

    Raises:
        ValueError: Se ocorrer erro nesta operação.
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
    cc = ConcursoCandidato.objects.select_for_update().get(uuid=candidato_uuid)
    if cc.eliminado:
        raise ValueError("Registro já está eliminado.")
    cc.eliminado = True
    cc.eliminado_em = timezone.now()
    cc.eliminado_motivo = motivo or ""
    cc.eliminado_por = executado_por or ""
    cc.save(
        update_fields=[
            "eliminado",
            "eliminado_em",
            "eliminado_motivo",
            "eliminado_por",
            "atualizado_em",
        ]
    )
    hist = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc,
        motivo=motivo or "",
        executado_por=executado_por or "",
    )
    return (cc, hist)
