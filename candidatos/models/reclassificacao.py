from django.db import models
from .base import BaseModel
from .concurso_candidato import ConcursoCandidato


class ConcursoCandidatoReclassificacao(BaseModel):
    """
    Histórico de reclassificações explícitas, registrando desclassificação
    de cotas sem alterar os campos de classificação originais.
    """
    COTA_CHOICES = (
        ('NNA', 'NNA'),
        ('PCD', 'PCD'),
    )

    concurso_candidato = models.ForeignKey(
        ConcursoCandidato,
        on_delete=models.CASCADE,
        related_name='historicos_reclassificacao',
        verbose_name="ConcursoCandidato"
    )
    desclassificado_de = models.CharField(
        max_length=3,
        choices=COTA_CHOICES,
        verbose_name="Desclassificado de"
    )
    motivo = models.TextField(blank=True, default='', verbose_name="Motivo/Observação")
    executado_por = models.CharField(max_length=150, blank=True, default='', verbose_name="Executado por")

    class Meta:
        verbose_name = 'Reclassificação de ConcursoCandidato'
        verbose_name_plural = 'Reclassificações de ConcursoCandidato'
        ordering = ['-criado_em']
        unique_together = (('concurso_candidato', 'desclassificado_de'),)

    def __str__(self):
        return f"{self.concurso_candidato_id} - {self.desclassificado_de}"

