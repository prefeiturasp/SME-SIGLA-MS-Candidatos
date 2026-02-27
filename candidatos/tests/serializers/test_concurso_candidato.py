"""
Testes unitários para ConcursoCandidatoSerializer (feature/143715-consulta-concursado).
Campos testados: concurso_candidato_uuid, concurso_uuid, concurso_nome.
"""
import pytest
from uuid import uuid4
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote
from candidatos.serializer import ConcursoCandidatoSerializer


pytestmark = pytest.mark.django_db


@pytest.fixture
def candidato():
    return Candidato.objects.create(
        nome='Candidato Teste',
        cpf='111.222.333-44',
        email='teste@email.com',
        telefone='',
        data_nascimento='1990-01-01',
        genero='M',
        endereco='',
        cidade='',
        estado='',
        cep='',
        status='ativo',
        observacoes='',
    )


@pytest.fixture
def lote_com_concurso():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome='Concurso Nome do Lote',
    )


def test_get_concurso_candidato_uuid(candidato, lote_com_concurso):
    """concurso_candidato_uuid deve ser o UUID do ConcursoCandidato."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote_com_concurso,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    assert serializer.data['concurso_candidato_uuid'] == str(cc.uuid)


def test_get_concurso_uuid_from_lote(candidato, lote_com_concurso):
    """concurso_uuid deve vir do lote quando o modelo não tem o campo."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote_com_concurso,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    assert serializer.data['concurso_uuid'] == str(lote_com_concurso.concurso_uuid)


def test_get_concurso_nome_from_lote(candidato, lote_com_concurso):
    """concurso_nome deve vir do lote."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote_com_concurso,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    assert serializer.data['concurso_nome'] == lote_com_concurso.concurso_nome


def test_get_concurso_nome_returns_none_sem_lote(candidato):
    """concurso_nome deve ser None quando não há lote."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=None,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    assert serializer.data['concurso_nome'] is None


def test_get_concurso_uuid_returns_none_sem_lote(candidato):
    """concurso_uuid deve ser None quando não há lote e modelo não tem o campo."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=None,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    assert serializer.data['concurso_uuid'] is None


def test_serializer_inclui_novos_campos_na_serializacao(candidato, lote_com_concurso):
    """A serialização deve incluir concurso_uuid, concurso_nome e concurso_candidato_uuid."""
    cc = ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote_com_concurso,
        codigo_inscricao='INS1',
        classificacao=1,
    )
    serializer = ConcursoCandidatoSerializer(cc)
    data = serializer.data
    assert 'concurso_candidato_uuid' in data
    assert 'concurso_uuid' in data
    assert 'concurso_nome' in data
    assert data['concurso_candidato_uuid'] == str(cc.uuid)
    assert data['concurso_uuid'] == str(lote_com_concurso.concurso_uuid)
    assert data['concurso_nome'] == lote_com_concurso.concurso_nome
