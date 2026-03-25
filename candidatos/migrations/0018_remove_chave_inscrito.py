from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("candidatos", "0017_add_lote_classificacao_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="concursocandidato",
            name="chave_inscrito",
        ),
    ]
