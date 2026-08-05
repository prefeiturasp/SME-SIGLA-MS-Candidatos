# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    """Move mandado_judicial do histórico para ConcursoCandidato."""

    dependencies = [
        ("candidatos", "0021_concursocandidato_concurso_uuid_remove_lote"),
    ]

    operations = [
        migrations.AddField(
            model_name="concursocandidato",
            name="mandado_judicial",
            field=models.BooleanField(
                default=False, verbose_name="Mandado judicial"
            ),
        ),
        migrations.RemoveField(
            model_name="concursocandidatohistoricoclassificacao",
            name="mandado_judicial",
        ),
    ]
