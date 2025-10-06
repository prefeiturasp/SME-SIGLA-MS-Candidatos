from django.db import models
from .base import BaseModel
from .candidato import Candidato
from .lote import ConcursoCandidatosLote


class ConcursoCandidato(BaseModel):
    lote = models.ForeignKey(ConcursoCandidatosLote, on_delete=models.CASCADE, related_name='itens', null=True, blank=True)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='concursos')
    codigo_inscricao = models.CharField(max_length=30)
    pontos = models.CharField(max_length=20, blank=True)
    opcao_concurso = models.CharField(max_length=50, blank=True)
    codigo_cargo = models.CharField(max_length=20, blank=True)
    cota = models.CharField(max_length=50, blank=True)
    descricao_cargo = models.CharField(max_length=200, blank=True)
    df = models.CharField(max_length=50, blank=True)
    classificacao = models.IntegerField(blank=True, null=True)
    classificacao_pcd = models.IntegerField(blank=True, null=True)
    classificacao_nna = models.IntegerField(blank=True, null=True)
    ano_concurso = models.CharField(max_length=10, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Concurso do Candidato'
        verbose_name_plural = 'Concursos dos Candidatos'
        ordering = ['-criado_em']
