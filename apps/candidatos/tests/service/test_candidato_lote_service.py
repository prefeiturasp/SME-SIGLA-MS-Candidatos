"""Módulo tests/service/test_candidato_lote_service."""

import pytest
from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoHistoricoClassificacao,
)
from candidatos.service.candidato_lote_service import (
    processar_criacao_candidatos_lote,
)

pytestmark = pytest.mark.django_db


def payload_exemplo():
    """Payload de exemplo para importação."""
    return {
        "concurso_uuid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "concurso_nome": "Concurso X",
        "candidatos": [
            {
                "nome": "Fulano",
                "cpf": "111.111.111-11",
                "email": "f1@example.com",
                "data_nascimento": "01/01/1990",
                "codigo_inscricao": "123",
                "pontos": 0,
                "classificacao": 20,
                "classificacao_nna": 1,
            },
            {
                "nome": "Beltrano",
                "cpf": "222.222.222-22",
                "email": "f2@example.com",
                "data_nascimento": "02/02/1991",
                "codigo_inscricao": "456",
                "pontos": 0,
                "classificacao": 21,
                "classificacao_nna": 2,
            },
        ],
    }


def test_processar_criacao_candidatos_lote_cria_candidatos_e_relacionamentos():
    """Verifica criacao de candidatos e relacionamentos."""
    body, status_code = processar_criacao_candidatos_lote(payload_exemplo())
    assert status_code == 201
    assert body["concurso_uuid"] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert body["total_itens"] == 2
    assert ConcursoCandidato.objects.count() == 2
    assert Candidato.objects.count() == 2


def test_processar_criacao_candidatos_lote_sem_concurso_uuid_retorna_400():
    """Verifica processar criacao candidatos lote sem concurso uuid retorna."""
    p = payload_exemplo()
    del p["concurso_uuid"]
    body, status_code = processar_criacao_candidatos_lote(p)
    assert status_code == 400
    assert "concurso_uuid" in body["detail"]


def test_segundo_post_com_deslocamento_cria_historico():
    """Segundo POST com alguém à frente registra histórico."""
    processar_criacao_candidatos_lote(payload_exemplo())
    cc = ConcursoCandidato.objects.get(codigo_inscricao="123")
    cc.foi_convocado = True
    cc.save(update_fields=["foi_convocado"])

    payload2 = payload_exemplo()
    payload2["mandado_judicial"] = True
    payload2["candidatos"] = [
        {
            "nome": "Novo Mandado",
            "cpf": "333.333.333-33",
            "email": "novo@example.com",
            "data_nascimento": "01/01/1992",
            "codigo_inscricao": "999",
            "pontos": 0,
            "classificacao": 20,
            "classificacao_nna": 1,
        },
        {
            "nome": "Fulano",
            "cpf": "111.111.111-11",
            "email": "f1@example.com",
            "data_nascimento": "01/01/1990",
            "codigo_inscricao": "123",
            "pontos": 0,
            "classificacao": 21,
            "classificacao_nna": 2,
        },
        {
            "nome": "Beltrano",
            "cpf": "222.222.222-22",
            "email": "f2@example.com",
            "data_nascimento": "02/02/1991",
            "codigo_inscricao": "456",
            "pontos": 0,
            "classificacao": 22,
            "classificacao_nna": 3,
        },
    ]
    body, status_code = processar_criacao_candidatos_lote(payload2)
    assert status_code == 201
    assert body["total_itens"] == 3
    assert ConcursoCandidato.objects.count() == 3

    hist_fulano = ConcursoCandidatoHistoricoClassificacao.objects.filter(
        concurso_candidato__codigo_inscricao="123"
    ).get()
    assert hist_fulano.classificacao_nna_anterior == 1
    assert hist_fulano.classificacao_nna_nova == 2
    assert hist_fulano.foi_convocado is True
    assert hist_fulano.mandado_judicial is True

    hist_beltrano = ConcursoCandidatoHistoricoClassificacao.objects.filter(
        concurso_candidato__codigo_inscricao="456"
    ).get()
    assert hist_beltrano.classificacao_nna_anterior == 2
    assert hist_beltrano.classificacao_nna_nova == 3
    assert hist_beltrano.foi_convocado is False

    assert not ConcursoCandidatoHistoricoClassificacao.objects.filter(
        concurso_candidato__codigo_inscricao="999"
    ).exists()

    cc_fulano = ConcursoCandidato.objects.get(codigo_inscricao="123")
    assert cc_fulano.classificacao_nna == 2
    assert cc_fulano.classificacao == 21
