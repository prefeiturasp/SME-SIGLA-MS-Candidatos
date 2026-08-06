# Generated manually: concurso_uuid on ConcursoCandidato, remove Lote

from django.db import migrations, models


def copiar_concurso_do_lote(apps, schema_editor):
    ConcursoCandidato = apps.get_model("candidatos", "ConcursoCandidato")
    for cc in ConcursoCandidato.objects.select_related("lote").iterator():
        if cc.lote_id and cc.lote is not None:
            ConcursoCandidato.objects.filter(pk=cc.pk).update(
                concurso_uuid=cc.lote.concurso_uuid,
                concurso_nome=cc.lote.concurso_nome or "",
            )


class Migration(migrations.Migration):
    dependencies = [
        ("candidatos", "0020_concursocandidatohistoricoclassificacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="concursocandidato",
            name="concurso_uuid",
            field=models.UUIDField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name="UUID do Concurso",
            ),
        ),
        migrations.AddField(
            model_name="concursocandidato",
            name="concurso_nome",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Nome do Concurso",
            ),
        ),
        migrations.RunPython(
            copiar_concurso_do_lote, migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name="concursocandidato",
            name="lote",
        ),
        migrations.DeleteModel(
            name="ConcursoCandidatosLote",
        ),
    ]
