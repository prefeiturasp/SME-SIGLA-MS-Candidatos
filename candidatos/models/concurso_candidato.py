from django.db import models
from .base import BaseModel
from .candidato import Candidato
from .lote import ConcursoCandidatosLote


CATEGORIA_CHOICES = (
    ('GERAL', 'GERAL'),
    ('NNA', 'NNA'),
    ('PCD', 'PCD'),
)


class ConcursoCandidato(BaseModel):
    lote = models.ForeignKey(ConcursoCandidatosLote, on_delete=models.CASCADE, related_name='itens', null=True, blank=True)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='concursos')
    codigo_inscricao = models.CharField(max_length=30, verbose_name="Código de Inscrição")
    pontos = models.FloatField(blank=True, null=True, verbose_name="Pontos", default=0.0)
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
    ranking = models.IntegerField(default=0, verbose_name="Ranking")
    # Sinalização de categoria efetiva e promoções
    categoria_efetiva = models.CharField(
        max_length=10,
        choices=CATEGORIA_CHOICES,
        default='GERAL',
        db_index=True,
        verbose_name="Categoria Efetiva",
    )
    promovido_para_geral = models.BooleanField(default=False, verbose_name="Promovido para Geral")
    promovido_de = models.CharField(
        max_length=10,
        choices=(('NNA', 'NNA'), ('PCD', 'PCD')),
        blank=True,
        null=True,
        verbose_name="Promovido de",
    )
    promovido_em = models.DateTimeField(blank=True, null=True, verbose_name="Promovido em")

    class Meta:
        verbose_name = 'Concurso do Candidato'
        verbose_name_plural = 'Concursos dos Candidatos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.candidato.nome} - {self.uuid} - {self.classificacao} - {self.classificacao_pcd} - {self.classificacao_nna} - {self.ranking}"
