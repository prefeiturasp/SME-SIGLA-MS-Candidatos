"""Remove Parametrizacao do estado do app candidatos."""

from django.db import migrations


class Migration(migrations.Migration):
    """Transfere o model Parametrizacao para o app parametrizacao."""

    dependencies = [
        ("candidatos", "0017_concursocandidato_chave_inscrito_and_more"),
        ("parametrizacao", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name="Parametrizacao"),
            ],
            database_operations=[],
        ),
    ]
