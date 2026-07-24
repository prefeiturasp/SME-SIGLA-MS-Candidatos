"""Testes unitários do serializer de parametrização."""

from __future__ import annotations

import pytest
from parametrizacao.models import Parametrizacao
from parametrizacao.serializer import ParametrizacaoSerializer

pytestmark = pytest.mark.django_db


def test_parametrizacao_serializer_serializacao() -> None:
    """Verifica a serialização da parametrização."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.1, porcentagem_nna=0.25
    )
    serializer = ParametrizacaoSerializer(parametrizacao)
    data = serializer.data
    assert data["porcentagem_pcd"] == 0.1
    assert data["porcentagem_nna"] == 0.25
    assert "uuid" in data
    assert "criado_em" in data
    assert "atualizado_em" in data
    assert "esta_ativo" in data


def test_parametrizacao_serializer_desserializacao() -> None:
    """Verifica a desserialização da parametrização."""
    data = {"porcentagem_pcd": 0.15, "porcentagem_nna": 0.3}
    serializer = ParametrizacaoSerializer(data=data)
    assert serializer.is_valid()
    parametrizacao = serializer.save()
    assert parametrizacao.porcentagem_pcd == 0.15
    assert parametrizacao.porcentagem_nna == 0.3
    assert parametrizacao.uuid is not None


def test_parametrizacao_serializer_partial_update() -> None:
    """Verifica o partial update do serializer de parametrização."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    data = {"porcentagem_pcd": 0.12}
    serializer = ParametrizacaoSerializer(
        parametrizacao, data=data, partial=True
    )
    assert serializer.is_valid()
    updated_parametrizacao = serializer.save()
    assert updated_parametrizacao.porcentagem_pcd == 0.12
    assert updated_parametrizacao.porcentagem_nna == 0.2


def test_parametrizacao_serializer_campos_somente_leitura() -> None:
    """Verifica os campos somente leitura do serializer."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    original_uuid = parametrizacao.uuid
    original_criado_em = parametrizacao.criado_em
    data = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "criado_em": "2020-01-01T00:00:00Z",
        "porcentagem_pcd": 0.15,
    }
    serializer = ParametrizacaoSerializer(
        parametrizacao, data=data, partial=True
    )
    assert serializer.is_valid()
    updated_parametrizacao = serializer.save()
    assert updated_parametrizacao.uuid == original_uuid
    assert updated_parametrizacao.criado_em == original_criado_em
    assert updated_parametrizacao.porcentagem_pcd == 0.15


def test_parametrizacao_serializer_validacao() -> None:
    """Verifica a validação do serializer de parametrização."""
    data = {"porcentagem_pcd": 0.1, "porcentagem_nna": 0.25}
    serializer = ParametrizacaoSerializer(data=data)
    assert serializer.is_valid()
    data_invalid = {"porcentagem_pcd": -0.1, "porcentagem_nna": 0.25}
    ParametrizacaoSerializer(data=data_invalid)
