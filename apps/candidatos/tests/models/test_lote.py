"""Testes unitários para o modelo ConcursoCandidatosLote."""

from time import sleep
from uuid import uuid4

import pytest

from candidatos.models import ConcursoCandidatosLote

pytestmark = pytest.mark.django_db


def test_lote_cria_com_campos_obrigatorios(criar_lote):
    """Testa criação do lote com campos obrigatórios."""
    concurso_uuid = uuid4()
    lote = criar_lote(concurso_uuid=concurso_uuid, concurso_nome="PME 2024")
    assert lote.concurso_uuid == concurso_uuid
    assert lote.concurso_nome == "PME 2024"
    assert lote.uuid is not None
    assert lote.criado_em is not None
    assert lote.esta_ativo is True


def test_lote_cria_com_nome_vazio():
    """Testa criação do lote com nome em branco."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4())
    assert lote.concurso_nome == ""


def test_lote_representacao_str(criar_lote):
    """Testa a representação textual do lote."""
    concurso_uuid = uuid4()
    lote = criar_lote(
        concurso_uuid=concurso_uuid, concurso_nome="Concurso XYZ"
    )
    assert str(lote) == f"Concurso XYZ ({concurso_uuid})"


def test_lote_meta_opcoes():
    """Testa as opções Meta do model ConcursoCandidatosLote."""
    assert (
        ConcursoCandidatosLote._meta.verbose_name
        == "Lote de Candidatos do Concurso"
    )
    assert (
        ConcursoCandidatosLote._meta.verbose_name_plural
        == "Lotes de Candidatos dos Concursos"
    )
    assert ConcursoCandidatosLote._meta.ordering == ["-criado_em"]


def test_lote_ordenacao_por_criado_em_decrescente(criar_lote):
    """Testa ordenação dos lotes por criado_em decrescente."""
    ConcursoCandidatosLote.objects.all().delete()
    lote1 = criar_lote(concurso_nome="Lote Antigo")
    sleep(0.01)
    lote2 = criar_lote(concurso_nome="Lote Novo")
    lotes = list(ConcursoCandidatosLote.objects.all())
    assert lotes[0] == lote2
    assert lotes[1] == lote1


def test_lote_update(criar_lote):
    """Testa o update do lote."""
    lote = criar_lote(concurso_nome="Original")
    lote.concurso_nome = "Atualizado"
    lote.save()
    lote.refresh_from_db()
    assert lote.concurso_nome == "Atualizado"


def test_lote_soft_delete(criar_lote):
    """Testa o soft delete do lote."""
    lote = criar_lote()
    assert lote.esta_ativo is True
    lote.esta_ativo = False
    lote.save()
    lote.refresh_from_db()
    assert lote.esta_ativo is False
