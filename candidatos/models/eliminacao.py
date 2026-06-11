"""Módulo models/eliminacao."""

from __future__ import annotations

from typing import Any

from django.db import models

from .base import BaseModel
from .concurso_candidato import ConcursoCandidato


class ConcursoCandidatoEliminacao(BaseModel):
    """Histórico de eliminações/restaurações de ConcursoCandidato."""

    concurso_candidato = models.ForeignKey(
        ConcursoCandidato,
        on_delete=models.CASCADE,
        related_name="historicos_eliminacao",
        verbose_name="ConcursoCandidato",
    )
    processo_uuid = models.UUIDField(
        blank=True, null=True, verbose_name="UUID do Processo"
    )
    motivo = models.TextField(
        blank=True, default="", verbose_name="Motivo/Observação"
    )
    executado_por = models.CharField(
        max_length=150, blank=True, default="", verbose_name="Executado por"
    )

    class Meta:
        """Representa Meta."""

        verbose_name = "Eliminação de ConcursoCandidato"
        verbose_name_plural = "Eliminações de ConcursoCandidato"
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.concurso_candidato_id} - ELIMINACAO"
