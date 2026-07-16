"""Módulo models/reclassificacao."""

from __future__ import annotations

from typing import Any

from django.db import models

from .base import BaseModel
from .concurso_candidato import ConcursoCandidato


class ConcursoCandidatoReclassificacao(BaseModel):
    """Histórico de reclassificações explícitas, registrando."""

    CLASSIFICACAO_CHOICES = (
        ("GERAL", "GERAL"),
        ("NNA", "NNA"),
        ("PCD", "PCD"),
    )
    concurso_candidato = models.ForeignKey(
        ConcursoCandidato,
        on_delete=models.CASCADE,
        related_name="historicos_reclassificacao",
        verbose_name="ConcursoCandidato",
    )
    desclassificado_de = models.CharField(
        max_length=5,
        choices=CLASSIFICACAO_CHOICES,
        verbose_name="Desclassificado de",
    )
    nova_classificacao = models.CharField(
        max_length=5,
        choices=CLASSIFICACAO_CHOICES,
        verbose_name="Nova Classificação",
        default="GERAL",
        blank=True,
        null=True,
    )
    processo_uuid = models.UUIDField(
        null=True, blank=True, verbose_name="Processo UUID"
    )
    motivo = models.TextField(
        blank=True, default="", verbose_name="Motivo/Observação"
    )
    executado_por = models.CharField(
        max_length=150, blank=True, default="", verbose_name="Executado por"
    )

    class Meta:
        """Representa Meta."""

        verbose_name = "Reclassificação de ConcursoCandidato"
        verbose_name_plural = "Reclassificações de ConcursoCandidato"
        ordering = ["-criado_em"]
        unique_together = (("concurso_candidato", "desclassificado_de"),)

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return f"{self.concurso_candidato_id} - {self.desclassificado_de}"
