"""Testes unitários dos models de parametrização."""

from __future__ import annotations

import pytest

from parametrizacao.models import Parametrizacao

pytestmark = pytest.mark.django_db


def test_parametrizacao_cria_com_valores_padrao() -> None:
    """Verifica criação da parametrização com valores padrão."""
    parametrizacao = Parametrizacao.objects.create()
    assert parametrizacao.porcentagem_pcd == 0.05
    assert parametrizacao.porcentagem_nna == 0.2
    assert parametrizacao.uuid is not None
    assert parametrizacao.esta_ativo is True
    assert parametrizacao.criado_em is not None
    assert parametrizacao.atualizado_em is not None


def test_parametrizacao_cria_com_valores_customizados() -> None:
    """Verifica criação da parametrização com valores customizados."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.1, porcentagem_nna=0.25
    )
    assert parametrizacao.porcentagem_pcd == 0.1
    assert parametrizacao.porcentagem_nna == 0.25


def test_parametrizacao_representacao_str() -> None:
    """Verifica a representação textual da parametrização."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.15, porcentagem_nna=0.3
    )
    expected_str = f"Parametrização - PCD: {parametrizacao.porcentagem_pcd}, NNA: {parametrizacao.porcentagem_nna}"  # noqa: E501
    assert str(parametrizacao) == expected_str


def test_parametrizacao_ordenacao() -> None:
    """Verifica a ordenação das parametrizações."""
    parametrizacao1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    import time

    time.sleep(0.01)
    parametrizacao2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.1, porcentagem_nna=0.25
    )
    all_parametrizacoes = list(Parametrizacao.objects.all())
    assert all_parametrizacoes[0] == parametrizacao2
    assert all_parametrizacoes[1] == parametrizacao1


def test_parametrizacao_update() -> None:
    """Verifica o update da parametrização."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    original_updated = parametrizacao.atualizado_em
    parametrizacao.porcentagem_pcd = 0.15
    parametrizacao.porcentagem_nna = 0.3
    parametrizacao.save()
    parametrizacao.refresh_from_db()
    assert parametrizacao.porcentagem_pcd == 0.15
    assert parametrizacao.porcentagem_nna == 0.3
    assert parametrizacao.atualizado_em > original_updated


def test_parametrizacao_soft_delete() -> None:
    """Verifica o soft delete da parametrização."""
    parametrizacao = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    assert parametrizacao.esta_ativo is True
    parametrizacao.esta_ativo = False
    parametrizacao.save()
    parametrizacao.refresh_from_db()
    assert parametrizacao.esta_ativo is False


def test_parametrizacao_multiplas_instancias() -> None:
    """Verifica criação de múltiplas instâncias de parametrização."""
    Parametrizacao.objects.all().delete()
    parametrizacao1 = Parametrizacao.objects.create(
        porcentagem_pcd=0.05, porcentagem_nna=0.2
    )
    parametrizacao2 = Parametrizacao.objects.create(
        porcentagem_pcd=0.1, porcentagem_nna=0.25
    )
    assert Parametrizacao.objects.count() == 2
    assert parametrizacao1.uuid != parametrizacao2.uuid
