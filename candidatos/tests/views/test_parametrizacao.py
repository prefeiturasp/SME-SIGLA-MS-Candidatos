import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from candidatos.models import Parametrizacao


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def parametrizacao_url():
    return reverse('parametrizacao-atual')


@pytest.fixture
def parametrizacao_existente():
    """Cria uma parametrização existente"""
    return Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )


@pytest.fixture
def parametrizacao_multiplas():
    """Cria múltiplas parametrizações para testar ordenação"""
    import time
    
    param1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05,
        porcentagem_nna=0.20
    )
    
    time.sleep(0.01)  # Garante ordem diferente
    
    param2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.10,
        porcentagem_nna=0.25
    )
    
    return {'param1': param1, 'param2': param2}


def test_get_parametrizacao_when_exists(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa GET quando existe parametrização"""
    response = api_client.get(parametrizacao_url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data is not None
    assert response.data['porcentagem_pcd'] == 0.05
    assert response.data['porcentagem_nna'] == 0.20
    assert response.data['uuid'] == str(parametrizacao_existente.uuid)


def test_get_parametrizacao_when_not_exists(api_client, parametrizacao_url):
    """Testa GET quando não existe parametrização"""
    response = api_client.get(parametrizacao_url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data is None


def test_get_parametrizacao_returns_most_recent(api_client, parametrizacao_url, parametrizacao_multiplas):
    """Testa que GET retorna sempre o registro mais recente"""
    response = api_client.get(parametrizacao_url)
    
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar o mais recente (param2)
    assert response.data['porcentagem_pcd'] == 0.10
    assert response.data['porcentagem_nna'] == 0.25
    assert response.data['uuid'] == str(parametrizacao_multiplas['param2'].uuid)


def test_patch_parametrizacao_when_exists(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa PATCH quando existe parametrização"""
    payload = {
        'porcentagem_pcd': 0.15,
        'porcentagem_nna': 0.30
    }
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.15
    assert response.data['porcentagem_nna'] == 0.30
    
    # Verifica que foi atualizado no banco
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.15
    assert parametrizacao_existente.porcentagem_nna == 0.30


def test_patch_parametrizacao_partial_update(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa PATCH com atualização parcial (apenas um campo)"""
    payload = {
        'porcentagem_pcd': 0.12
    }
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.12
    assert response.data['porcentagem_nna'] == 0.20  # Não alterado
    
    # Verifica no banco
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.12
    assert parametrizacao_existente.porcentagem_nna == 0.20


def test_patch_parametrizacao_when_not_exists(api_client, parametrizacao_url):
    """Testa PATCH quando não existe parametrização (deve criar)"""
    payload = {
        'porcentagem_pcd': 0.10,
        'porcentagem_nna': 0.25
    }
    
    assert Parametrizacao.objects.count() == 0
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['porcentagem_pcd'] == 0.10
    assert response.data['porcentagem_nna'] == 0.25
    
    # Verifica que foi criado no banco
    assert Parametrizacao.objects.count() == 1
    parametrizacao = Parametrizacao.objects.first()
    assert parametrizacao.porcentagem_pcd == 0.10
    assert parametrizacao.porcentagem_nna == 0.25


def test_patch_parametrizacao_updates_most_recent(api_client, parametrizacao_url, parametrizacao_multiplas):
    """Testa que PATCH atualiza sempre o registro mais recente"""
    payload = {
        'porcentagem_pcd': 0.20,
        'porcentagem_nna': 0.35
    }
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verifica que apenas o mais recente foi atualizado
    parametrizacao_multiplas['param2'].refresh_from_db()
    parametrizacao_multiplas['param1'].refresh_from_db()
    
    assert parametrizacao_multiplas['param2'].porcentagem_pcd == 0.20
    assert parametrizacao_multiplas['param2'].porcentagem_nna == 0.35
    
    # O mais antigo não foi alterado
    assert parametrizacao_multiplas['param1'].porcentagem_pcd == 0.05
    assert parametrizacao_multiplas['param1'].porcentagem_nna == 0.20


def test_patch_parametrizacao_invalid_data(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa PATCH com dados inválidos"""
    # Testa com tipo errado (string ao invés de float)
    payload = {
        'porcentagem_pcd': 'invalid',
        'porcentagem_nna': 0.25
    }
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    # Deve retornar erro de validação
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_patch_parametrizacao_empty_payload(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa PATCH com payload vazio (deve manter valores atuais)"""
    payload = {}
    
    original_pcd = parametrizacao_existente.porcentagem_pcd
    original_nna = parametrizacao_existente.porcentagem_nna
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    
    # Valores devem permanecer os mesmos
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == original_pcd
    assert parametrizacao_existente.porcentagem_nna == original_nna


def test_get_parametrizacao_response_structure(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa estrutura da resposta GET"""
    response = api_client.get(parametrizacao_url)
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    
    # Verifica campos obrigatórios
    required_fields = ['uuid', 'porcentagem_pcd', 'porcentagem_nna', 'criado_em', 'atualizado_em', 'esta_ativo']
    for field in required_fields:
        assert field in response.data


def test_patch_parametrizacao_response_structure(api_client, parametrizacao_url, parametrizacao_existente):
    """Testa estrutura da resposta PATCH"""
    payload = {
        'porcentagem_pcd': 0.15,
        'porcentagem_nna': 0.30
    }
    
    response = api_client.patch(parametrizacao_url, payload, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    
    # Verifica campos obrigatórios
    required_fields = ['uuid', 'porcentagem_pcd', 'porcentagem_nna', 'criado_em', 'atualizado_em', 'esta_ativo']
    for field in required_fields:
        assert field in response.data
    
    # Verifica valores atualizados
    assert response.data['porcentagem_pcd'] == 0.15
    assert response.data['porcentagem_nna'] == 0.30

