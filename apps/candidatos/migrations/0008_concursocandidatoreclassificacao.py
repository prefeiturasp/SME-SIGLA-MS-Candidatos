from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candidatos', '0007_concursocandidato_ranking_escolha'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConcursoCandidatoReclassificacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False, unique=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('esta_ativo', models.BooleanField(default=True, verbose_name='Está Ativo?')),
                ('desclassificado_de', models.CharField(choices=[('NNA', 'NNA'), ('PCD', 'PCD')], max_length=3, verbose_name='Desclassificado de')),
                ('motivo', models.TextField(blank=True, default='', verbose_name='Motivo/Observação')),
                ('executado_por', models.CharField(blank=True, default='', max_length=150, verbose_name='Executado por')),
                ('concurso_candidato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historicos_reclassificacao', to='candidatos.concursocandidato', verbose_name='ConcursoCandidato')),
            ],
            options={
                'verbose_name': 'Reclassificação de ConcursoCandidato',
                'verbose_name_plural': 'Reclassificações de ConcursoCandidato',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='concursocandidatoreclassificacao',
            unique_together={('concurso_candidato', 'desclassificado_de')},
        ),
    ]

