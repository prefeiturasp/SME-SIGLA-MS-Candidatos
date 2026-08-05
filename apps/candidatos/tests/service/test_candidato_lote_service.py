"""Testes unitários do CandidatoLoteService."""

from uuid import uuid4

import pytest
from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoHistoricoClassificacao,
)
from candidatos.service.candidato_lote_service import CandidatoLoteService
from candidatos.service.candidato_service import CandidatoService

pytestmark = pytest.mark.django_db


def _payload_exemplo(*, mandado_judicial: bool | None = None) -> dict:
    """Payload de exemplo para importação em lote."""
    payload = {
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
    if mandado_judicial is not None:
        payload["mandado_judicial"] = mandado_judicial
    return payload


class TestResolverMandadoJudicial:
    """Testes unitários de CandidatoLoteService._resolver_mandado_judicial."""

    def test_true_sem_candidatos_no_concurso_retorna_false(self):
        """True no payload sem candidatos existentes vira False."""
        resultado = CandidatoLoteService._resolver_mandado_judicial(
            True, str(uuid4())
        )
        assert resultado is False

    def test_true_com_candidatos_no_concurso_retorna_true(self):
        """True no payload com candidatos existentes permanece True."""
        concurso_uuid = str(uuid4())
        CandidatoService.upsert_candidato_e_concurso(
            {
                "nome": "Existente",
                "cpf": "111.111.111-11",
                "email": "e@example.com",
                "data_nascimento": "01/01/1990",
                "codigo_inscricao": "001",
                "pontos": 0,
            },
            concurso_uuid=concurso_uuid,
        )
        resultado = CandidatoLoteService._resolver_mandado_judicial(
            True, concurso_uuid
        )
        assert resultado is True

    def test_false_com_candidatos_no_concurso_retorna_true(self):
        """False no payload com candidatos existentes vira True."""
        concurso_uuid = str(uuid4())
        CandidatoService.upsert_candidato_e_concurso(
            {
                "nome": "Existente",
                "cpf": "222.222.222-22",
                "email": "e2@example.com",
                "data_nascimento": "01/01/1990",
                "codigo_inscricao": "002",
                "pontos": 0,
            },
            concurso_uuid=concurso_uuid,
        )
        resultado = CandidatoLoteService._resolver_mandado_judicial(
            False, concurso_uuid
        )
        assert resultado is True

    def test_false_sem_candidatos_no_concurso_retorna_false(self):
        """False no payload sem candidatos existentes permanece False."""
        resultado = CandidatoLoteService._resolver_mandado_judicial(
            False, str(uuid4())
        )
        assert resultado is False


class TestProcessarCriacaoCandidatosLote:
    """Testes de CandidatoLoteService.processar_criacao_candidatos_lote."""

    def test_cria_candidatos_e_relacionamentos(self):
        """Primeiro lote cria candidatos sem mandado_judicial."""
        body, status_code = (
            CandidatoLoteService.processar_criacao_candidatos_lote(
                _payload_exemplo()
            )
        )
        assert status_code == 201
        assert body["concurso_uuid"] == (
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        )
        assert body["total_itens"] == 2
        assert ConcursoCandidato.objects.count() == 2
        assert Candidato.objects.count() == 2
        assert all(
            not cc.mandado_judicial for cc in ConcursoCandidato.objects.all()
        )

    def test_sem_concurso_uuid_retorna_400(self):
        """Payload sem concurso_uuid retorna 400."""
        payload = _payload_exemplo()
        del payload["concurso_uuid"]
        body, status_code = (
            CandidatoLoteService.processar_criacao_candidatos_lote(payload)
        )
        assert status_code == 400
        assert "concurso_uuid" in body["detail"]

    def test_mandado_judicial_true_sem_candidatos_persiste_false(self):
        """True no payload sem candidatos existentes persiste False."""
        body, status_code = (
            CandidatoLoteService.processar_criacao_candidatos_lote(
                _payload_exemplo(mandado_judicial=True)
            )
        )
        assert status_code == 201
        assert all(
            not cc.mandado_judicial for cc in ConcursoCandidato.objects.all()
        )

    def test_mandado_judicial_false_com_candidatos_persiste_true_no_novo(self):
        """False no payload com concurso já populado marca o novo como True."""
        CandidatoLoteService.processar_criacao_candidatos_lote(
            _payload_exemplo()
        )
        payload = _payload_exemplo(mandado_judicial=False)
        payload["candidatos"] = [
            {
                "nome": "Novo Mandado",
                "cpf": "333.333.333-33",
                "email": "novo@example.com",
                "data_nascimento": "01/01/1992",
                "codigo_inscricao": "999",
                "pontos": 0,
                "classificacao": 20,
                "classificacao_nna": 1,
            }
        ]
        body, status_code = (
            CandidatoLoteService.processar_criacao_candidatos_lote(payload)
        )
        assert status_code == 201
        cc_novo = ConcursoCandidato.objects.get(codigo_inscricao="999")
        assert cc_novo.mandado_judicial is True

    def test_segundo_post_com_deslocamento_cria_historico(self):
        """Segundo POST desloca classificação e marca novo com mandado."""
        CandidatoLoteService.processar_criacao_candidatos_lote(
            _payload_exemplo()
        )
        cc = ConcursoCandidato.objects.get(codigo_inscricao="123")
        cc.foi_convocado = True
        cc.save(update_fields=["foi_convocado"])

        payload2 = _payload_exemplo(mandado_judicial=True)
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
        body, status_code = (
            CandidatoLoteService.processar_criacao_candidatos_lote(payload2)
        )
        assert status_code == 201
        assert body["total_itens"] == 3
        assert ConcursoCandidato.objects.count() == 3

        hist_fulano = ConcursoCandidatoHistoricoClassificacao.objects.filter(
            concurso_candidato__codigo_inscricao="123"
        ).get()
        assert hist_fulano.classificacao_nna_anterior == 1
        assert hist_fulano.classificacao_nna_nova == 2
        assert hist_fulano.foi_convocado is True

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
        assert cc_fulano.mandado_judicial is False

        cc_novo = ConcursoCandidato.objects.get(codigo_inscricao="999")
        assert cc_novo.mandado_judicial is True
