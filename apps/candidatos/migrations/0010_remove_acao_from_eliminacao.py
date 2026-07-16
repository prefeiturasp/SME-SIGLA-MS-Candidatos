from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candidatos', '0009_concursocandidato_eliminado_and_eliminacao_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concursocandidatoeliminacao',
            name='acao',
        ),
    ]

