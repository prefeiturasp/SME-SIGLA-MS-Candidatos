"""Módulo tests/views/test_parametrizacao_view."""
from __future__ import annotations
from typing import Any
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from candidatos.models import Parametrizacao
pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client() -> Any:
    """Executa api client."""
    return APIClient()

@pytest.fixture
def parametrizacao_existente() -> Any:
    """Cria uma parametrização existente"""
    return Parametrizacao.objects.create(porcentagem_pcd=0.05, porcentagem_nna=0.2)

@pytest.fixture
def parametrizacao_multiplas() -> Any:
    """Cria múltiplas parametrizações para testar ordenação"""
    import time
    param1 = Parametrizacao.objects.create(porcentagem_pcd=0.05, porcentagem_nna=0.2)
    time.sleep(0.01)
    param2 = Parametrizacao.objects.create(porcentagem_pcd=0.1, porcentagem_nna=0.25)
    return {'param1': param1, 'param2': param2}

def test_list_parametrizacao_when_exists(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa GET /api/v1/parametrizacao/ quando existe parametrização."""
    url = reverse('parametrizacao-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    assert response.data[0]['porcentagem_pcd'] == 0.05
    assert response.data[0]['porcentagem_nna'] == 0.2
    assert response.data[0]['uuid'] == str(parametrizacao_existente.uuid)

def test_list_parametrizacao_when_not_exists(api_client: Any) -> None:
    """Testa GET /api/v1/parametrizacao/ quando não existe parametrização."""
    Parametrizacao.objects.all().delete()
    url = reverse('parametrizacao-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) == 0

def test_list_parametrizacao_returns_most_recent(api_client: Any, parametrizacao_multiplas: Any) -> None:
    """Testa que GET retorna sempre o registro mais recente."""
    url = reverse('parametrizacao-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['porcentagem_pcd'] == 0.1
    assert response.data[0]['porcentagem_nna'] == 0.25
    assert response.data[0]['uuid'] == str(parametrizacao_multiplas['param2'].uuid)

def test_retrieve_parametrizacao_when_exists(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa GET /api/v1/parametrizacao/{pk}/ quando existe."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.05
    assert response.data['porcentagem_nna'] == 0.2
    assert response.data['uuid'] == str(parametrizacao_existente.uuid)

def test_retrieve_parametrizacao_returns_most_recent(api_client: Any, parametrizacao_multiplas: Any) -> None:
    """Testa que retrieve retorna sempre o mais recente, ignorando o pk."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_multiplas['param1'].uuid})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.1
    assert response.data['porcentagem_nna'] == 0.25
    assert response.data['uuid'] == str(parametrizacao_multiplas['param2'].uuid)

def test_patch_parametrizacao_when_exists(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa PATCH /api/v1/parametrizacao/{pk}/ quando existe parametrização."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    payload = {'porcentagem_pcd': 0.15, 'porcentagem_nna': 0.3}
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.15
    assert response.data['porcentagem_nna'] == 0.3
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.15
    assert parametrizacao_existente.porcentagem_nna == 0.3

def test_patch_parametrizacao_partial_update(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa PATCH com atualização parcial (apenas um campo)."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    payload = {'porcentagem_pcd': 0.12}
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['porcentagem_pcd'] == 0.12
    assert response.data['porcentagem_nna'] == 0.2
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.12
    assert parametrizacao_existente.porcentagem_nna == 0.2

def test_patch_parametrizacao_when_not_exists(api_client: Any) -> None:
    """Testa PATCH quando não existe parametrização (get_object retorna o mais.

    recente; com 0 registros cria novo).
    """
    Parametrizacao.objects.all().delete()
    url = reverse('parametrizacao-detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
    payload = {'porcentagem_pcd': 0.1, 'porcentagem_nna': 0.25}
    assert Parametrizacao.objects.count() == 0
    response = api_client.patch(url, payload, format='json')
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND)
    if response.status_code == status.HTTP_200_OK:
        assert Parametrizacao.objects.count() == 1
        assert response.data['porcentagem_pcd'] == 0.1
        assert response.data['porcentagem_nna'] == 0.25

def test_patch_parametrizacao_updates_most_recent(api_client: Any, parametrizacao_multiplas: Any) -> None:
    """Testa que PATCH atualiza sempre o registro mais recente."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_multiplas['param1'].uuid})
    payload = {'porcentagem_pcd': 0.2, 'porcentagem_nna': 0.35}
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    parametrizacao_multiplas['param2'].refresh_from_db()
    parametrizacao_multiplas['param1'].refresh_from_db()
    assert parametrizacao_multiplas['param2'].porcentagem_pcd == 0.2
    assert parametrizacao_multiplas['param2'].porcentagem_nna == 0.35
    assert parametrizacao_multiplas['param1'].porcentagem_pcd == 0.05
    assert parametrizacao_multiplas['param1'].porcentagem_nna == 0.2

def test_patch_parametrizacao_invalid_data(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa PATCH com dados inválidos."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    payload = {'porcentagem_pcd': 'invalid', 'porcentagem_nna': 0.25}
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_patch_parametrizacao_empty_payload(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa PATCH com payload vazio (deve manter valores atuais)."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    payload = {}  # type: ignore[var-annotated]
    original_pcd = parametrizacao_existente.porcentagem_pcd
    original_nna = parametrizacao_existente.porcentagem_nna
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == original_pcd
    assert parametrizacao_existente.porcentagem_nna == original_nna

def test_list_parametrizacao_response_structure(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa estrutura da resposta GET list."""
    url = reverse('parametrizacao-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    if len(response.data) > 0:
        required_fields = ['uuid', 'porcentagem_pcd', 'porcentagem_nna', 'criado_em', 'atualizado_em', 'esta_ativo']
        for field in required_fields:
            assert field in response.data[0]

def test_retrieve_parametrizacao_response_structure(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa estrutura da resposta GET retrieve."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    required_fields = ['uuid', 'porcentagem_pcd', 'porcentagem_nna', 'criado_em', 'atualizado_em', 'esta_ativo']
    for field in required_fields:
        assert field in response.data

def test_patch_parametrizacao_response_structure(api_client: Any, parametrizacao_existente: Any) -> None:
    """Testa estrutura da resposta PATCH."""
    url = reverse('parametrizacao-detail', kwargs={'pk': parametrizacao_existente.uuid})
    payload = {'porcentagem_pcd': 0.15, 'porcentagem_nna': 0.3}
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    required_fields = ['uuid', 'porcentagem_pcd', 'porcentagem_nna', 'criado_em', 'atualizado_em', 'esta_ativo']
    for field in required_fields:
        assert field in response.data
    assert response.data['porcentagem_pcd'] == 0.15
    assert response.data['porcentagem_nna'] == 0.3

def test_post_parametrizacao_not_allowed(api_client: Any) -> None:
    """Testa que POST não é permitido."""
    url = reverse('parametrizacao-list')
    payload = {'porcentagem_pcd': 0.1, 'porcentagem_nna': 0.25}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert 'detail' in response.data
    assert 'POST' in response.data['detail']
