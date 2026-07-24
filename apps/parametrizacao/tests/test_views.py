"""Testes unitários das views de parametrização."""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from parametrizacao.models import Parametrizacao
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> Any:
    """Cliente HTTP para requisições de teste."""
    return APIClient()


@pytest.fixture
def parametrizacao_existente() -> Any:
    """Cria uma parametrização existente."""
    return Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )


@pytest.fixture
def parametrizacao_multiplas() -> Any:
    """Cria múltiplas parametrizações para testar ordenação."""
    import time

    param1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    time.sleep(0.01)
    param2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.1, porcentagem_nna=0.25
    )
    return {"param1": param1, "param2": param2}


def test_lista_parametrizacao_quando_existe(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica a listagem da parametrização quando existe registro."""
    url = reverse("parametrizacao-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) > 0
    assert response.data[0]["porcentagem_pcd"] == 0.05
    assert response.data[0]["porcentagem_nna"] == 0.2
    assert response.data[0]["uuid"] == str(parametrizacao_existente.uuid)


def test_lista_parametrizacao_quando_nao_existe(api_client: Any) -> None:
    """Verifica a listagem da parametrização quando não existe registro."""
    Parametrizacao.objects.all().delete()
    url = reverse("parametrizacao-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) == 0


def test_lista_parametrizacao_retorna_mais_recente(
    api_client: Any, parametrizacao_multiplas: Any
) -> None:
    """Verifica se a listagem retorna a parametrização mais recente."""
    url = reverse("parametrizacao-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["porcentagem_pcd"] == 0.1
    assert response.data[0]["porcentagem_nna"] == 0.25
    assert response.data[0]["uuid"] == str(
        parametrizacao_multiplas["param2"].uuid
    )


def test_detalhe_parametrizacao_quando_existe(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica o detalhe da parametrização quando existe registro."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["porcentagem_pcd"] == 0.05
    assert response.data["porcentagem_nna"] == 0.2
    assert response.data["uuid"] == str(parametrizacao_existente.uuid)


def test_detalhe_parametrizacao_retorna_mais_recente(
    api_client: Any, parametrizacao_multiplas: Any
) -> None:
    """Verifica se o detalhe retorna a parametrização mais recente."""
    url = reverse(
        "parametrizacao-detail",
        kwargs={"pk": parametrizacao_multiplas["param1"].uuid},
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["porcentagem_pcd"] == 0.1
    assert response.data["porcentagem_nna"] == 0.25
    assert response.data["uuid"] == str(
        parametrizacao_multiplas["param2"].uuid
    )


def test_patch_parametrizacao_quando_existe(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica o patch da parametrização quando existe registro."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    payload = {"porcentagem_pcd": 0.15, "porcentagem_nna": 0.3}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["porcentagem_pcd"] == 0.15
    assert response.data["porcentagem_nna"] == 0.3
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.15
    assert parametrizacao_existente.porcentagem_nna == 0.3


def test_patch_parametrizacao_partial_update(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica o patch com partial update da parametrização."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    payload = {"porcentagem_pcd": 0.12}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["porcentagem_pcd"] == 0.12
    assert response.data["porcentagem_nna"] == 0.2
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == 0.12
    assert parametrizacao_existente.porcentagem_nna == 0.2


def test_patch_parametrizacao_quando_nao_existe(api_client: Any) -> None:
    """Verifica o patch da parametrização quando não existe registro."""
    Parametrizacao.objects.all().delete()
    url = reverse(
        "parametrizacao-detail",
        kwargs={"pk": "00000000-0000-0000-0000-000000000000"},
    )
    payload = {"porcentagem_pcd": 0.1, "porcentagem_nna": 0.25}
    assert Parametrizacao.objects.count() == 0
    response = api_client.patch(url, payload, format="json")
    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_404_NOT_FOUND,
    )
    if response.status_code == status.HTTP_200_OK:
        assert Parametrizacao.objects.count() == 1
        assert response.data["porcentagem_pcd"] == 0.1
        assert response.data["porcentagem_nna"] == 0.25


def test_patch_parametrizacao_update_mais_recente(
    api_client: Any, parametrizacao_multiplas: Any
) -> None:
    """Verifica se o patch faz update da parametrização mais recente."""
    url = reverse(
        "parametrizacao-detail",
        kwargs={"pk": parametrizacao_multiplas["param1"].uuid},
    )
    payload = {"porcentagem_pcd": 0.2, "porcentagem_nna": 0.35}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    parametrizacao_multiplas["param2"].refresh_from_db()
    parametrizacao_multiplas["param1"].refresh_from_db()
    assert parametrizacao_multiplas["param2"].porcentagem_pcd == 0.2
    assert parametrizacao_multiplas["param2"].porcentagem_nna == 0.35
    assert parametrizacao_multiplas["param1"].porcentagem_pcd == 0.05
    assert parametrizacao_multiplas["param1"].porcentagem_nna == 0.2


def test_patch_parametrizacao_dados_invalidos(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica o patch da parametrização com dados inválidos."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    payload = {"porcentagem_pcd": "invalid", "porcentagem_nna": 0.25}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_patch_parametrizacao_payload_vazio(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica o patch da parametrização com payload vazio."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    payload = {}  # type: ignore[var-annotated]
    original_pcd = parametrizacao_existente.porcentagem_pcd
    original_nna = parametrizacao_existente.porcentagem_nna
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    parametrizacao_existente.refresh_from_db()
    assert parametrizacao_existente.porcentagem_pcd == original_pcd
    assert parametrizacao_existente.porcentagem_nna == original_nna


def test_lista_parametrizacao_estrutura_resposta(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica a estrutura da resposta na listagem da parametrização."""
    url = reverse("parametrizacao-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    if len(response.data) > 0:
        required_fields = [
            "uuid",
            "porcentagem_pcd",
            "porcentagem_nna",
            "criado_em",
            "atualizado_em",
            "esta_ativo",
        ]
        for field in required_fields:
            assert field in response.data[0]


def test_detalhe_parametrizacao_estrutura_resposta(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica a estrutura da resposta no detalhe da parametrização."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    required_fields = [
        "uuid",
        "porcentagem_pcd",
        "porcentagem_nna",
        "criado_em",
        "atualizado_em",
        "esta_ativo",
    ]
    for field in required_fields:
        assert field in response.data


def test_patch_parametrizacao_estrutura_resposta(
    api_client: Any, parametrizacao_existente: Any
) -> None:
    """Verifica a estrutura da resposta no patch da parametrização."""
    url = reverse(
        "parametrizacao-detail", kwargs={"pk": parametrizacao_existente.uuid}
    )
    payload = {"porcentagem_pcd": 0.15, "porcentagem_nna": 0.3}
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)
    required_fields = [
        "uuid",
        "porcentagem_pcd",
        "porcentagem_nna",
        "criado_em",
        "atualizado_em",
        "esta_ativo",
    ]
    for field in required_fields:
        assert field in response.data
    assert response.data["porcentagem_pcd"] == 0.15
    assert response.data["porcentagem_nna"] == 0.3


def test_post_parametrizacao_nao_permitido(api_client: Any) -> None:
    """Verifica que o post da parametrização não é permitido."""
    url = reverse("parametrizacao-list")
    payload = {"porcentagem_pcd": 0.1, "porcentagem_nna": 0.25}
    response = api_client.post(url, payload, format="json")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "detail" in response.data
    assert "POST" in response.data["detail"]
