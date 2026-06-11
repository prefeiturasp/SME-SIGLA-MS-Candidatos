"""Módulo models/lote."""

from __future__ import annotations

from typing import Any

from django.db import models

from .base import BaseModel


class ConcursoCandidatosLote(BaseModel):
    """Representa ConcursoCandidatosLote."""

    concurso_uuid = models.UUIDField()
    concurso_nome = models.CharField(max_length=255, blank=True)

    class Meta:
        """Representa Meta."""

        verbose_name = "Lote de Candidatos do Concurso"
        verbose_name_plural = "Lotes de Candidatos dos Concursos"
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.concurso_nome} ({self.concurso_uuid})"
