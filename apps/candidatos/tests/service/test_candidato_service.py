"""Módulo tests/service/test_candidato_service."""

import pytest
from candidatos.models import Candidato, ConcursoCandidato
from candidatos.service.candidato_service import (
    remover_mascara_cpf,
    upsert_candidato_e_concurso,
)

pytestmark = pytest.mark.django_db


def test_remover_mascara_cpf_vazio_retorna_vazio():
    """Verifica remover mascara cpf vazio retorna vazio."""
    assert remover_mascara_cpf("") == ""
    assert remover_mascara_cpf(None) == ""


def test_remover_mascara_cpf_remove_pontos_e_traco():
    """Verifica remover mascara cpf remove pontos e traco."""
    assert remover_mascara_cpf("123.456.789-00") == "12345678900"
    assert remover_mascara_cpf("12345678900") == "12345678900"


def test_remover_mascara_cpf_aceita_nao_string():
    """Verifica remover mascara cpf aceita nao string."""
    assert remover_mascara_cpf(12345678900) == "12345678900"


def test_upsert_cria_candidato_e_concurso_quando_novo():
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


def test_upsert_reusa_candidato_mesmo_cpf_e_cria_novo_concurso():
    """Mesmo CPF sem concurso_uuid reutiliza Candidato e cria novo vínculo."""
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
    assert candidato2.id == primeiro.id
    assert candidato2.nome == "B"
    assert candidato2.telefone == "9999"
    assert Candidato.objects.filter(cpf="11111111111").count() == 1
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_mesmo_cpf_cargos_diferentes_cria_dois_concurso_candidato():
    """Mesmo CPF no mesmo concurso com cargos distintos gera 2 registros."""
    concurso_uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    payload_base = {
        "nome": "Fulano",
        "cpf": "111.111.111-11",
        "email": "f@example.com",
        "data_nascimento": "01/01/1990",
        "sexo": "1",
        "codigo_inscricao": "123",
        "pontos": 0,
    }
    _, cc1 = upsert_candidato_e_concurso(
        {**payload_base, "codigo_cargo": "1008"},
        concurso_uuid=concurso_uuid,
    )
    _, cc2 = upsert_candidato_e_concurso(
        {**payload_base, "codigo_cargo": "2001", "codigo_inscricao": "456"},
        concurso_uuid=concurso_uuid,
    )
    assert cc1.id != cc2.id
    assert cc1.candidato_id == cc2.candidato_id
    assert cc1.codigo_cargo == "1008"
    assert cc2.codigo_cargo == "2001"
    assert Candidato.objects.filter(cpf="11111111111").count() == 1
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_mesmo_cpf_mesmo_cargo_atualiza_registro():
    """Mesmo CPF + cargo + concurso atualiza o ConcursoCandidato existente."""
    concurso_uuid = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    payload = {
        "nome": "Fulano",
        "cpf": "222.222.222-22",
        "email": "f@example.com",
        "data_nascimento": "01/01/1990",
        "codigo_inscricao": "123",
        "codigo_cargo": "1008",
        "pontos": 0,
        "classificacao": 10,
    }
    _, cc1 = upsert_candidato_e_concurso(
        payload, concurso_uuid=concurso_uuid, concurso_nome="C1"
    )
    _, cc2 = upsert_candidato_e_concurso(
        {**payload, "classificacao": 15, "nome": "Fulano Atualizado"},
        concurso_uuid=concurso_uuid,
        concurso_nome="C1",
    )
    assert cc1.id == cc2.id
    assert cc2.classificacao == 15
    assert cc2.candidato.nome == "Fulano Atualizado"
    assert ConcursoCandidato.objects.count() == 1
    assert Candidato.objects.count() == 1


def test_upsert_data_nascimento_formato_invalido_nao_quebra():
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


def test_upsert_cria_novos_candidatos_para_mesmo_email_sem_cpf():
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


def test_upsert_atualiza_data_nascimento_do_mesmo_candidato():
    """Mesmo CPF reutiliza candidato e atualiza a data de nascimento."""
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
    assert primeiro.id == candidato2.id
    candidato2.refresh_from_db()
    assert candidato2.data_nascimento.year == 1990
    assert candidato2.data_nascimento.month == 6
    assert candidato2.data_nascimento.day == 15
    assert Candidato.objects.filter(cpf="33333333333").count() == 1
    assert ConcursoCandidato.objects.count() == 2


def test_upsert_categoria_efetiva_pcd():
    """Verifica upsert categoria efetiva pcd."""
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


def test_upsert_categoria_efetiva_nna():
    """Verifica upsert categoria efetiva nna."""
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


def test_upsert_none_if_empty_string_retorna_none():
    """Verifica upsert none if empty string retorna none."""
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
