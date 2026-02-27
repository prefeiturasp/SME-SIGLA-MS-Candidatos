import pytest
from candidatos.models import Parametrizacao


pytestmark = pytest.mark.django_db


def test_parametrizacao_create_with_defaults():
    """Testa criação de Parametrizacao com valores padrão"""
    parametrizacao = Parametrizacao.objects.create()
    
    assert parametrizacao.porcentagem_pcd == 0.05
    assert parametrizacao.porcentagem_nna == 0.20
    assert parametrizacao.uuid is not None
    assert parametrizacao.esta_ativo is True
    assert parametrizacao.criado_em is not None
    assert parametrizacao.atualizado_em is not None


def test_parametrizacao_create_with_custom_values():
    """Testa criação de Parametrizacao com valores customizados"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.10,
        porcentagem_nna=0.25
    )
    
    assert parametrizacao.porcentagem_pcd == 0.10
    assert parametrizacao.porcentagem_nna == 0.25


def test_parametrizacao_str_representation():
    """Testa a representação string do model"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.15,
        porcentagem_nna=0.30
    )
    
    expected_str = f"Parametrização - PCD: {parametrizacao.porcentagem_pcd}, NNA: {parametrizacao.porcentagem_nna}"
    assert str(parametrizacao) == expected_str


def test_parametrizacao_ordering():
    """Testa que a ordenação é por criado_em decrescente"""
    parametrizacao1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    # Simula um pequeno delay para garantir ordem diferente
    import time
    time.sleep(0.01)
    
    parametrizacao2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.10,
        porcentagem_nna=0.25
    )
    
    # O mais recente deve vir primeiro
    all_parametrizacoes = list(Parametrizacao.objects.all())
    assert all_parametrizacoes[0] == parametrizacao2
    assert all_parametrizacoes[1] == parametrizacao1


def test_parametrizacao_update():
    """Testa atualização de Parametrizacao"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    original_updated = parametrizacao.atualizado_em
    
    parametrizacao.porcentagem_pcd = 0.15
    parametrizacao.porcentagem_nna = 0.30
    parametrizacao.save()
    
    parametrizacao.refresh_from_db()
    assert parametrizacao.porcentagem_pcd == 0.15
    assert parametrizacao.porcentagem_nna == 0.30
    assert parametrizacao.atualizado_em > original_updated


def test_parametrizacao_soft_delete():
    """Testa soft delete (esta_ativo)"""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    assert parametrizacao.esta_ativo is True
    
    parametrizacao.esta_ativo = False
    parametrizacao.save()
    
    parametrizacao.refresh_from_db()
    assert parametrizacao.esta_ativo is False


def test_parametrizacao_multiple_instances():
    """Testa criação de múltiplas instâncias"""
    Parametrizacao.objects.all().delete()
    parametrizacao1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    parametrizacao2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.10,
        porcentagem_nna=0.25
    )
    assert Parametrizacao.objects.count() == 2
    assert parametrizacao1.uuid != parametrizacao2.uuid
