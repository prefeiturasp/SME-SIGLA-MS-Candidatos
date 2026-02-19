# Generated manually

from django.db import migrations


def remover_mascara_cpf(cpf):
    """
    Remove máscara do CPF, retornando apenas os dígitos.
    
    Args:
        cpf: CPF com ou sem máscara (ex: "123.456.789-00" ou "12345678900")
        
    Returns:
        CPF sem máscara (apenas dígitos)
    """
    if not cpf:
        return ''
    return ''.join(filter(str.isdigit, str(cpf)))


def atualizar_cpfs_sem_mascara(apps, schema_editor):
    """
    Remove máscara dos CPFs de todos os candidatos no banco de dados.
    """
    Candidato = apps.get_model('candidatos', 'Candidato')
    
    candidatos = Candidato.objects.all()
    candidatos_para_atualizar = []
    atualizados = 0
    
    for candidato in candidatos:
        if candidato.cpf:
            cpf_sem_mascara = remover_mascara_cpf(candidato.cpf)
            # Só atualiza se o CPF realmente tinha máscara (tem caracteres não numéricos)
            if cpf_sem_mascara != candidato.cpf:
                candidato.cpf = cpf_sem_mascara
                candidatos_para_atualizar.append(candidato)
                atualizados += 1
    
    # Atualiza em lote para melhor performance
    if candidatos_para_atualizar:
        Candidato.objects.bulk_update(candidatos_para_atualizar, ['cpf'], batch_size=1000)
    
    print(f'Atualizados {atualizados} CPFs removendo máscara.')


def reverter_atualizacao_cpf(apps, schema_editor):
    """
    Função reversa - não é possível reverter a remoção de máscara,
    então esta função não faz nada.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('candidatos', '0008_parametrizacao'),
    ]

    operations = [
        migrations.RunPython(
            atualizar_cpfs_sem_mascara,
            reverter_atualizacao_cpf
        ),
    ]

