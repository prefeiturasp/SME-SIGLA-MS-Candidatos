from django.db import models
from .base import BaseModel
from .candidato import Candidato
from .lote import ConcursoCandidatosLote


class ConcursoCandidato(BaseModel):
    lote = models.ForeignKey(ConcursoCandidatosLote, on_delete=models.CASCADE, related_name='itens', null=True, blank=True)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='concursos')
    codigo_inscricao = models.CharField(max_length=30, verbose_name="Código de Inscrição")
    pontos = models.CharField(max_length=20, blank=True, verbose_name="Pontos")
    opcao_concurso = models.CharField(max_length=50, blank=True, verbose_name="Opção de Concurso")
    codigo_cargo = models.CharField(max_length=20, blank=True, verbose_name="Código do Cargo")
    processo_uuid = models.UUIDField(blank=True, null=True, verbose_name="UUID do Processo")
    cota = models.CharField(max_length=50, blank=True, verbose_name="Cota")
    descricao_cargo = models.CharField(max_length=200, blank=True, verbose_name="Descrição do Cargo")
    df = models.CharField(max_length=50, blank=True, verbose_name="DF")
    classificacao = models.IntegerField(blank=True, null=True, verbose_name="Classificação")
    classificacao_pcd = models.IntegerField(blank=True, null=True, verbose_name="Classificação PCD")
    classificacao_nna = models.IntegerField(blank=True, null=True, verbose_name="Classificação NNA")
    ano_concurso = models.CharField(max_length=10, blank=True, verbose_name="Ano do Concurso")
    observacao = models.TextField(blank=True, verbose_name="Observação")
    foi_convocado = models.BooleanField(default=False, verbose_name="Foi Convocado?")
    data_convocacao = models.DateTimeField(blank=True, null=True, verbose_name="Data de Convocação")

    class Meta:
        verbose_name = 'Concurso do Candidato'
        verbose_name_plural = 'Concursos dos Candidatos'
        ordering = ['-criado_em']
