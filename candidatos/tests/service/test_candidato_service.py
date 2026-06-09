"""Módulo tests/service/test_candidato_service."""

from __future__ import annotations

import pytest

from candidatos.models import Candidato, ConcursoCandidato
from candidatos.service.candidato_service import (
    remover_mascara_cpf,
    upsert_candidato_e_concurso,
)

pytestmark = pytest.mark.django_db


def test_remover_mascara_cpf_vazio_retorna_vazio() -> None:
    """Verifica remover mascara cpf vazio retorna vazio."""
    assert remover_mascara_cpf("") == ""
    assert remover_mascara_cpf(None) == ""  # type: ignore[arg-type]


def test_remover_mascara_cpf_remove_pontos_e_traco() -> None:
    """Verifica remover mascara cpf remove pontos e traco."""
    assert remover_mascara_cpf("123.456.789-00") == "12345678900"
    assert remover_mascara_cpf("12345678900") == "12345678900"


def test_remover_mascara_cpf_aceita_nao_string() -> None:
    """Verifica remover mascara cpf aceita nao string."""
    assert remover_mascara_cpf(12345678900) == "12345678900"  # type: ignore[arg-type]


def test_upsert_cria_candidato_e_concurso_quando_novo() -> None:
    """Verifica upsert cria candidato e concurso quando novo."""
    data = {
        "nome": "Fulano",
        "cpf": "000.000.000-00",
        "email": "f@example.com",
        "data_nascimento": "01/01/1990",
        "sexo": "1",
        "codigo_inscricao": "123",
        "pontos": 0,
    }
    candidato, concurso = upsert_candidato_e_concurso(data)
    assert Candidato.objects.count() == 1
    assert ConcursoCandidato.objects.count() == 1
    assert candidato.nome == "Fulano"
    assert concurso.codigo_inscricao == "123"


def test_upsert_cria_novos_candidatos_para_mesmo_cpf() -> None:
    """Verifica upsert cria novos candidatos para mesmo cpf."""
    primeiro, _ = upsert_candidato_e_concurso(
        {
            "nome": "A",
            "cpf": "111.111.111-11",
            "email": "a@example.com",
            "data_nascimento": "01/01/1990",
            "sexo": "1",
            "codigo_inscricao": "x",
            "pontos": 0,
        }
    )
    candidato2, _c2 = upsert_candidato_e_concurso(
        {
            "nome": "B",
            "cpf": "111.111.111-11",
            "email": "a2@example.com",
            "telefone": "9999",
            "sexo": "2",
            "codigo_inscricao": "y",
            "pontos": 0,
        }
    )
    candidato2.refresh_from_db()
    assert candidato2.id != primeiro.id
    assert candidato2.nome == "B"
    assert candidato2.telefone == "9999"
    assert Candidato.objects.filter(cpf="11111111111").count() == 2
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_data_nascimento_formato_invalido_nao_quebra() -> None:
    """Verifica upsert data nascimento formato invalido nao quebra."""
    candidato, concurso = upsert_candidato_e_concurso(
        {
            "cpf": "222.222.222-22",
            "email": "b@example.com",
            "data_nascimento": "1990-31-12",
            "codigo_inscricao": "789",
            "pontos": 0,
        }
    )
    assert Candidato.objects.filter(cpf="22222222222").exists()


def test_upsert_cria_novos_candidatos_para_mesmo_email_sem_cpf() -> None:
    """Verifica upsert cria novos candidatos para mesmo email sem cpf."""
    candidato1, _c1 = upsert_candidato_e_concurso(
        {
            "nome": "X",
            "email": "unico@example.com",
            "data_nascimento": "01/01/1990",
            "sexo": "1",
            "codigo_inscricao": "a",
            "pontos": 0,
        }
    )
    candidato2, _c2 = upsert_candidato_e_concurso(
        {
            "nome": "Y",
            "email": "unico@example.com",
            "codigo_inscricao": "b",
            "pontos": 0,
        }
    )
    assert candidato1.id != candidato2.id
    candidato2.refresh_from_db()
    assert candidato2.nome == "Y"
    assert Candidato.objects.filter(email="unico@example.com").count() == 2
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_cria_novos_candidatos_com_diferentes_datas_de_nascimento() -> (
    None
):
    """Verifica upsert cria novos candidatos com diferentes datas de."""
    primeiro, _ = upsert_candidato_e_concurso(
        {
            "nome": "A",
            "cpf": "333.333.333-33",
            "email": "c@example.com",
            "data_nascimento": "01/01/1985",
            "sexo": "1",
            "codigo_inscricao": "x",
            "pontos": 0,
        }
    )
    candidato2, _ = upsert_candidato_e_concurso(
        {
            "nome": "A",
            "cpf": "333.333.333-33",
            "email": "c@example.com",
            "data_nascimento": "15/06/1990",
            "sexo": "1",
            "codigo_inscricao": "y",
            "pontos": 0,
        }
    )
    assert primeiro.data_nascimento.year == 1985
    candidato2.refresh_from_db()
    assert candidato2.id != primeiro.id
    assert candidato2.data_nascimento.year == 1990
    assert candidato2.data_nascimento.month == 6
    assert candidato2.data_nascimento.day == 15
    assert Candidato.objects.filter(cpf="33333333333").count() == 2
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_categoria_efetiva_pcd() -> None:
    """classificacao_deficiente preenchido define categoria_efetiva PCD."""
    _, concurso = upsert_candidato_e_concurso(
        {
            "cpf": "444.444.444-44",
            "email": "pcd@example.com",
            "codigo_inscricao": "p1",
            "classificacao_deficiente": 1,
            "pontos": 0,
        }
    )
    assert concurso.categoria_efetiva == "PCD"
    assert concurso.classificacao_pcd == 1


def test_upsert_categoria_efetiva_nna() -> None:
    """classificacao_nna preenchido define categoria_efetiva NNA (linhas."""
    _, concurso = upsert_candidato_e_concurso(
        {
            "cpf": "555.555.555-55",
            "email": "nna@example.com",
            "codigo_inscricao": "n1",
            "classificacao_nna": 2,
            "pontos": 0,
        }
    )
    assert concurso.categoria_efetiva == "NNA"
    assert concurso.classificacao_nna == 2


def test_upsert_none_if_empty_string_retorna_none() -> None:
    """classificacao_nna/classificacao_deficiente vazios resultam em None."""
    _, concurso = upsert_candidato_e_concurso(
        {
            "cpf": "666.666.666-66",
            "email": "vazio@example.com",
            "codigo_inscricao": "v1",
            "classificacao_nna": "",
            "classificacao_deficiente": "",
            "pontos": 0,
        }
    )
    assert concurso.categoria_efetiva == "GERAL"
    assert concurso.classificacao_nna is None
    assert concurso.classificacao_pcd is None
