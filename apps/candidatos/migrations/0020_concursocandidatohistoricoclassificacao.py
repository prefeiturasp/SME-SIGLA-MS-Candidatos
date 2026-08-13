# Generated manually for ConcursoCandidatoHistoricoClassificacao

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "candidatos",
            "0019_concursocandidatoreclassificacao_mandado_judicial",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ConcursoCandidatoHistoricoClassificacao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(editable=False, unique=True),
                ),
                (
                    "criado_em",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de Criação"
                    ),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data de Atualização"
                    ),
                ),
                (
                    "esta_ativo",
                    models.BooleanField(
                        default=True, verbose_name="Está Ativo?"
                    ),
                ),
                (
                    "classificacao_anterior",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação anterior",
                    ),
                ),
                (
                    "classificacao_nova",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação nova",
                    ),
                ),
                (
                    "classificacao_nna_anterior",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação NNA anterior",
                    ),
                ),
                (
                    "classificacao_nna_nova",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação NNA nova",
                    ),
                ),
                (
                    "classificacao_pcd_anterior",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação PCD anterior",
                    ),
                ),
                (
                    "classificacao_pcd_nova",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Classificação PCD nova",
                    ),
                ),
                (
                    "mandado_judicial",
                    models.BooleanField(
                        blank=True,
                        default=None,
                        null=True,
                        verbose_name="Mandado judicial",
                    ),
                ),
                (
                    "foi_convocado",
                    models.BooleanField(
                        default=False, verbose_name="Foi convocado?"
                    ),
                ),
                (
                    "motivo",
                    models.TextField(
                        blank=True,
                        default="",
                        verbose_name="Motivo/Observação",
                    ),
                ),
                (
                    "concurso_candidato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="historicos_classificacao",
                        to="candidatos.concursocandidato",
                        verbose_name="ConcursoCandidato",
                    ),
                ),
            ],
            options={
                "verbose_name": (
                    "Histórico de Classificação de ConcursoCandidato"
                ),
                "verbose_name_plural": (
                    "Históricos de Classificação de ConcursoCandidato"
                ),
                "ordering": ["-criado_em"],
            },
        ),
    ]
