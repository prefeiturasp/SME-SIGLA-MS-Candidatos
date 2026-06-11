"""Módulo tests/service/test_candidato_lote_service."""

from __future__ import annotations

from typing import Any

import pytest

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
)
from candidatos.service.candidato_lote_service import (
    processar_criacao_candidatos_lote,
)

pytestmark = pytest.mark.django_db


def payload_exemplo() -> Any:
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
            },
            {
                "nome": "Beltrano",
                "cpf": "222.222.222-22",
                "email": "f2@example.com",
                "data_nascimento": "02/02/1991",
                "codigo_inscricao": "456",
                "pontos": 0,
            },
        ],
    }


def test_processar_criacao_candidatos_lote_cria_lote_e_relacionamentos() -> (
    None
):
    """Verifica processar criacao candidatos lote cria lote e relacionamentos."""
    body, status_code = processar_criacao_candidatos_lote(payload_exemplo())
    assert status_code == 201
    assert "lote_uuid" in body
    assert body["total_itens"] == 2
    assert ConcursoCandidatosLote.objects.count() == 1
    lote = ConcursoCandidatosLote.objects.first()
    assert ConcursoCandidato.objects.filter(lote=lote).count() == 2
    assert Candidato.objects.count() == 2


def test_processar_criacao_candidatos_lote_sem_concurso_uuid_retorna_400() -> (
    None
):
    """Verifica processar criacao candidatos lote sem concurso uuid retorna."""
    p = payload_exemplo()
    del p["concurso_uuid"]
    body, status_code = processar_criacao_candidatos_lote(p)
    assert status_code == 400
    assert "concurso_uuid" in body["detail"]
