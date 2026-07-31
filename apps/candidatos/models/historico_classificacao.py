"""Módulo models/historico_classificacao."""

from __future__ import annotations

from typing import Any

from django.db import models

from .base import BaseModel
from .concurso_candidato import ConcursoCandidato


class ConcursoCandidatoHistoricoClassificacao(BaseModel):
    """Histórico de deslocamento de classificação por inserção na lista.

    Registra candidatos cuja classificação (geral, NNA ou PCD) piorou
    porque outro candidato entrou à frente em um novo POST da lista.
    """

    concurso_candidato = models.ForeignKey(
        ConcursoCandidato,
        on_delete=models.CASCADE,
        related_name="historicos_classificacao",
        verbose_name="ConcursoCandidato",
    )
    classificacao_anterior = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação anterior"
    )
    classificacao_nova = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação nova"
    )
    classificacao_nna_anterior = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação NNA anterior"
    )
    classificacao_nna_nova = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação NNA nova"
    )
    classificacao_pcd_anterior = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação PCD anterior"
    )
    classificacao_pcd_nova = models.IntegerField(
        blank=True, null=True, verbose_name="Classificação PCD nova"
    )
    mandado_judicial = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Mandado judicial",
    )
    foi_convocado = models.BooleanField(
        default=False, verbose_name="Foi convocado?"
    )
    motivo = models.TextField(
        blank=True, default="", verbose_name="Motivo/Observação"
    )

    class Meta:
        """Representa Meta."""

        verbose_name = "Histórico de Classificação de ConcursoCandidato"
        verbose_name_plural = (
            "Históricos de Classificação de ConcursoCandidato"
        )
        ordering = ["-criado_em"]

    def __str__(self) -> Any:
        """Retorna representação textual do registro."""
        return (
            f"{self.concurso_candidato_id} - "
            f"G:{self.classificacao_anterior}->{self.classificacao_nova} "
            f"NNA:{self.classificacao_nna_anterior}->"
            f"{self.classificacao_nna_nova} "
            f"PCD:{self.classificacao_pcd_anterior}->"
            f"{self.classificacao_pcd_nova}"
        )
