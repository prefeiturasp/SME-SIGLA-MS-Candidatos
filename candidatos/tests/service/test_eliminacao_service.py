"""
Testes unitários para candidatos/service/eliminacao_service.py.
Cobre aplicar_eliminacao (linhas 12-25).
"""
import pytest
from uuid import uuid4

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
    ConcursoCandidatoEliminacao,
)
from candidatos.service.eliminacao_service import aplicar_eliminacao


pytestmark = pytest.mark.django_db


def _candidato(**kwargs):
    return Candidato.objects.create(
        nome=kwargs.get("nome", "Teste"),
        cpf=kwargs.get("cpf", f"{uuid4().int % 10**11:011d}"),
        email=kwargs.get("email", f"{uuid4().hex[:8]}@example.com"),
        telefone="",
        data_nascimento="1990-01-01",
        genero="M",
        endereco="",
        cidade="",
        estado="",
        cep="",
        status="ativo",
        observacoes="",
    )


@pytest.fixture
def lote():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome="Concurso Teste",
    )


@pytest.fixture
def cc_habilitado(lote):
    return ConcursoCandidato.objects.create(
        candidato=_candidato(),
        lote=lote,
        codigo_inscricao="001",
        eliminado=False,
    )


def test_aplicar_eliminacao_marca_eliminado_e_cria_historico(cc_habilitado):
    cc, hist = aplicar_eliminacao(
        candidato_uuid=cc_habilitado.uuid,
        motivo="Desistência",
        executado_por="sistema",
    )
    cc.refresh_from_db()
    assert cc.eliminado is True
    assert cc.eliminado_motivo == "Desistência"
    assert cc.eliminado_por == "sistema"
    assert cc.eliminado_em is not None
    assert hist.concurso_candidato_id == cc.id
    assert hist.motivo == "Desistência"
    assert hist.executado_por == "sistema"
    assert ConcursoCandidatoEliminacao.objects.filter(concurso_candidato=cc).count() == 1


def test_aplicar_eliminacao_motivo_e_executado_vazios(cc_habilitado):
    cc, hist = aplicar_eliminacao(candidato_uuid=cc_habilitado.uuid, motivo="", executado_por="")
    cc.refresh_from_db()
    assert cc.eliminado_motivo == ""
    assert cc.eliminado_por == ""
    assert hist.motivo == ""
    assert hist.executado_por == ""


def test_aplicar_eliminacao_ja_eliminado_levanta_value_error(lote):
    cc = ConcursoCandidato.objects.create(
        candidato=_candidato(),
        lote=lote,
        codigo_inscricao="002",
        eliminado=True,
    )
    with pytest.raises(ValueError, match="já está eliminado"):
        aplicar_eliminacao(candidato_uuid=cc.uuid, motivo="", executado_por="")


def test_aplicar_eliminacao_uuid_inexistente_levanta_does_not_exist():
    with pytest.raises(ConcursoCandidato.DoesNotExist):
        aplicar_eliminacao(candidato_uuid=uuid4(), motivo="", executado_por="")
