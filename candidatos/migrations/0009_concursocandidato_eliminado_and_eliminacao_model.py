from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candidatos', '0008_concursocandidatoreclassificacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='concursocandidato',
            name='eliminado',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Eliminado?'),
        ),
        migrations.AddField(
            model_name='concursocandidato',
            name='eliminado_em',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Eliminado em'),
        ),
        migrations.AddField(
            model_name='concursocandidato',
            name='eliminado_motivo',
            field=models.TextField(blank=True, default='', verbose_name='Motivo da eliminação'),
        ),
        migrations.AddField(
            model_name='concursocandidato',
            name='eliminado_por',
            field=models.CharField(blank=True, default='', max_length=150, verbose_name='Eliminado por'),
        ),
        migrations.CreateModel(
            name='ConcursoCandidatoEliminacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False, unique=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('esta_ativo', models.BooleanField(default=True, verbose_name='Está Ativo?')),
                ('acao', models.CharField(choices=[('ELIMINAR', 'ELIMINAR'), ('RESTAURAR', 'RESTAURAR')], max_length=10, verbose_name='Ação')),
                ('motivo', models.TextField(blank=True, default='', verbose_name='Motivo/Observação')),
                ('executado_por', models.CharField(blank=True, default='', max_length=150, verbose_name='Executado por')),
                ('concurso_candidato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historicos_eliminacao', to='candidatos.concursocandidato', verbose_name='ConcursoCandidato')),
            ],
            options={
                'verbose_name': 'Eliminação de ConcursoCandidato',
                'verbose_name_plural': 'Eliminações de ConcursoCandidato',
                'ordering': ['-criado_em'],
            },
        ),
    ]

