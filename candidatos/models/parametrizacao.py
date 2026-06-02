from django.db import models

from .base import BaseModel


class Parametrizacao(BaseModel):
    """
    Model para gerenciar parâmetros de cálculo de habilitados.
    Armazena as porcentagens usadas no cálculo de candidatos habilitados.
    """

    porcentagem_pcd = models.FloatField(
        default=0.05,
        verbose_name="Porcentagem PCD",
        help_text="Porcentagem padrão para cálculo de habilitados PCD (padrão: 0.05 = 5%)",  # noqa: E501
    )
    porcentagem_nna = models.FloatField(
        default=0.20,
        verbose_name="Porcentagem NNA",
        help_text="Porcentagem padrão para cálculo de habilitados NNA (padrão: 0.20 = 20%)",  # noqa: E501
    )

    class Meta:
        verbose_name = "Parametrização"
        verbose_name_plural = "Parametrizações"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Parametrização - PCD: {self.porcentagem_pcd}, NNA: {self.porcentagem_nna}"  # noqa: E501
