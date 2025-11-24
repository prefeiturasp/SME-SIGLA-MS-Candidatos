from django.db import models
from .base import BaseModel


class ConcursoCandidatosLote(BaseModel):
    concurso_uuid = models.UUIDField()
    concurso_nome = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Lote de Candidatos do Concurso'
        verbose_name_plural = 'Lotes de Candidatos dos Concursos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.concurso_nome} ({self.concurso_uuid})"


