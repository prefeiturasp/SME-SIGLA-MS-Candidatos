"""Testes unitários para o modelo ConcursoCandidatoEliminacao."""

from time import sleep
from uuid import uuid4

import pytest
from candidatos.models import ConcursoCandidatoEliminacao

pytestmark = pytest.mark.django_db


def test_eliminacao_cria_com_campos_obrigatorios(concurso_candidato):
    """Testa criação da eliminação com campos obrigatórios."""
    eliminacao = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato
    )
    assert eliminacao.concurso_candidato == concurso_candidato
    assert eliminacao.uuid is not None
    assert eliminacao.criado_em is not None
    assert eliminacao.esta_ativo is True


def test_eliminacao_cria_com_valores_completos(concurso_candidato):
    """Testa criação da eliminação com todos os campos."""
    processo_uuid = uuid4()
    eliminacao = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato,
        processo_uuid=processo_uuid,
        motivo="Falta de documentação",
        executado_por="admin",
    )
    assert eliminacao.processo_uuid == processo_uuid
    assert eliminacao.motivo == "Falta de documentação"
    assert eliminacao.executado_por == "admin"


def test_eliminacao_cria_com_valores_padrao(concurso_candidato):
    """Testa valores padrão da eliminação."""
    eliminacao = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato
    )
    assert eliminacao.processo_uuid is None
    assert eliminacao.motivo == ""
    assert eliminacao.executado_por == ""


def test_eliminacao_representacao_str(concurso_candidato):
    """Testa a representação textual da eliminação."""
    eliminacao = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato
    )
    assert str(eliminacao) == f"{concurso_candidato.id} - ELIMINACAO"


def test_eliminacao_meta_opcoes():
    """Testa as opções Meta do model ConcursoCandidatoEliminacao."""
    assert (
        ConcursoCandidatoEliminacao._meta.verbose_name
        == "Eliminação de ConcursoCandidato"
    )
    assert (
        ConcursoCandidatoEliminacao._meta.verbose_name_plural
        == "Eliminações de ConcursoCandidato"
    )
    assert ConcursoCandidatoEliminacao._meta.ordering == ["-criado_em"]


def test_eliminacao_ordenacao_por_criado_em_decrescente(concurso_candidato):
    """Testa ordenação das eliminações por criado_em decrescente."""
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato, motivo="Primeira"
    )
    sleep(0.01)
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato, motivo="Segunda"
    )
    qs = ConcursoCandidatoEliminacao.objects.filter(
        concurso_candidato=concurso_candidato
    )
    assert list(qs)[0].motivo == "Segunda"
    assert list(qs)[1].motivo == "Primeira"


def test_eliminacao_related_name_historicos(concurso_candidato):
    """Testa o related_name historicos_eliminacao."""
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato, motivo="Motivo 1"
    )
    assert concurso_candidato.historicos_eliminacao.count() == 1
    assert (
        concurso_candidato.historicos_eliminacao.first().motivo == "Motivo 1"
    )


def test_eliminacao_cascade_delete(concurso_candidato):
    """Testa cascade delete ao remover o concurso candidato."""
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato
    )
    assert ConcursoCandidatoEliminacao.objects.count() == 1
    concurso_candidato.delete()
    assert ConcursoCandidatoEliminacao.objects.count() == 0


def test_eliminacao_update(concurso_candidato):
    """Testa o update da eliminação."""
    eliminacao = ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=concurso_candidato, motivo="Original"
    )
    eliminacao.motivo = "Atualizado"
    eliminacao.executado_por = "supervisor"
    eliminacao.save()
    eliminacao.refresh_from_db()
    assert eliminacao.motivo == "Atualizado"
    assert eliminacao.executado_por == "supervisor"
