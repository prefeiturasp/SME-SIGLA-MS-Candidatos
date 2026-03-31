from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("candidatos", "0015_concursocandidatoreclassificacao_nova_classificacao_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="candidato",
            name="cpf",
            field=models.CharField(max_length=14, verbose_name="CPF"),
        ),
        migrations.AlterField(
            model_name="candidato",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="Email"),
        ),
    ]

