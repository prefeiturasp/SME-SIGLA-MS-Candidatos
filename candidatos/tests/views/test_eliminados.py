import pytest
from uuid import uuid4
from django.urls import reverse
from rest_framework.test import APIClient

from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def criar_candidato(nome, cpf):
    return Candidato.objects.create(
        nome=nome, cpf=cpf,
        email=f"user-{uuid4().hex[:8]}@example.com",
        telefone='', data_nascimento='1990-01-01',
        genero='M', endereco='', cidade='', estado='', cep='',
        status='ativo', observacoes=''
    )


def criar_lote(concurso_uuid):
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=concurso_uuid, concurso_nome='Concurso Teste'
    )


# ---------------------------------------------------------------------------
# Testes de validação de parâmetros
# ---------------------------------------------------------------------------

class TestEliminadosParametros:
    def test_sem_parametros_retorna_400(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url)
        assert resp.status_code == 400
        assert 'detail' in resp.data

    def test_sem_concurso_uuid_retorna_400(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url, {'classificacao_max': '10', 'classificacao_min': '1'})
        assert resp.status_code == 400

    def test_sem_classificacao_max_retorna_400(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url, {'concurso_uuid': str(uuid4()), 'classificacao_min': '1'})
        assert resp.status_code == 400

    def test_sem_classificacao_min_retorna_400(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url, {'concurso_uuid': str(uuid4()), 'classificacao_max': '10'})
        assert resp.status_code == 400

    def test_mensagem_erro_contem_campos_obrigatorios(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url)
        assert 'concurso_uuid' in resp.data['detail']
        assert 'classificacao_max' in resp.data['detail']
        assert 'classificacao_min' in resp.data['detail']


# ---------------------------------------------------------------------------
# Testes quando não existe lote
# ---------------------------------------------------------------------------

class TestEliminadosSemLote:
    def test_sem_lote_retorna_listas_vazias(self, api_client):
        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(uuid4()),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })
        assert resp.status_code == 200
        assert resp.data == {'geral': [], 'nna': [], 'pcd': []}


# ---------------------------------------------------------------------------
# Testes de filtragem e separação por categoria
# ---------------------------------------------------------------------------

class TestEliminadosFiltros:
    def test_retorna_eliminado_geral(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Geral Eliminado', '111.111.111-11')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='g1',
            eliminado=True, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 1
        assert len(resp.data['nna']) == 0
        assert len(resp.data['pcd']) == 0

    def test_retorna_eliminado_nna(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('NNA Eliminado', '222.222.222-22')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='nna1',
            eliminado=True, classificacao=3,
            classificacao_nna=2, classificacao_pcd=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 1
        assert len(resp.data['geral']) == 0

    def test_retorna_eliminado_pcd(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('PCD Eliminado', '333.333.333-33')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='pcd1',
            eliminado=True, classificacao=4,
            classificacao_pcd=1, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['pcd']) == 1
        assert len(resp.data['geral']) == 0

    def test_retorna_todos_os_tipos_separados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        c_geral = criar_candidato('Geral', '444.444.444-44')
        ConcursoCandidato.objects.create(
            candidato=c_geral, lote=lote, codigo_inscricao='g2',
            eliminado=True, classificacao=2,
            classificacao_pcd=None, classificacao_nna=None,
        )

        c_nna = criar_candidato('NNA', '555.555.555-55')
        ConcursoCandidato.objects.create(
            candidato=c_nna, lote=lote, codigo_inscricao='nna2',
            eliminado=True, classificacao=3,
            classificacao_nna=1, classificacao_pcd=None,
        )

        c_pcd = criar_candidato('PCD', '666.666.666-66')
        ConcursoCandidato.objects.create(
            candidato=c_pcd, lote=lote, codigo_inscricao='pcd2',
            eliminado=True, classificacao=4,
            classificacao_pcd=1, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 1
        assert len(resp.data['nna']) == 1
        assert len(resp.data['pcd']) == 1

    def test_nao_retorna_nao_eliminados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Ativo', '777.777.777-77')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='at1',
            eliminado=False, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 0

    def test_filtra_por_classificacao_max(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        c_dentro = criar_candidato('Dentro', '888.888.888-88')
        ConcursoCandidato.objects.create(
            candidato=c_dentro, lote=lote, codigo_inscricao='d1',
            eliminado=True, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        c_fora = criar_candidato('Fora', '999.999.999-99')
        ConcursoCandidato.objects.create(
            candidato=c_fora, lote=lote, codigo_inscricao='f1',
            eliminado=True, classificacao=15,
            classificacao_pcd=None, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 1

    def test_filtra_por_classificacao_min(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        c_dentro = criar_candidato('Dentro Min', '010.010.010-10')
        ConcursoCandidato.objects.create(
            candidato=c_dentro, lote=lote, codigo_inscricao='dm1',
            eliminado=True, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        c_fora = criar_candidato('Fora Min', '020.020.020-20')
        ConcursoCandidato.objects.create(
            candidato=c_fora, lote=lote, codigo_inscricao='fm1',
            eliminado=True, classificacao=1,
            classificacao_pcd=None, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '3',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 1

    def test_usa_ultimo_lote(self, api_client):
        concurso_uuid = uuid4()

        lote_antigo = criar_lote(concurso_uuid)
        lote_novo = criar_lote(concurso_uuid)

        c_antigo = criar_candidato('Antigo', '030.030.030-30')
        ConcursoCandidato.objects.create(
            candidato=c_antigo, lote=lote_antigo, codigo_inscricao='ant1',
            eliminado=True, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        c_novo = criar_candidato('Novo', '040.040.040-40')
        cc_novo = ConcursoCandidato.objects.create(
            candidato=c_novo, lote=lote_novo, codigo_inscricao='nov1',
            eliminado=True, classificacao=5,
            classificacao_pcd=None, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 1
        ids = [item['id'] for item in resp.data['geral']]
        assert cc_novo.id in ids

    def test_nna_e_pcd_nao_aparecem_em_geral(self, api_client):
        """Candidatos com classificacao_nna ou classificacao_pcd não devem aparecer em geral."""
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        c_nna = criar_candidato('NNA Excluido Geral', '050.050.050-50')
        ConcursoCandidato.objects.create(
            candidato=c_nna, lote=lote, codigo_inscricao='neg1',
            eliminado=True, classificacao=3,
            classificacao_nna=1, classificacao_pcd=None,
        )

        c_pcd = criar_candidato('PCD Excluido Geral', '060.060.060-60')
        ConcursoCandidato.objects.create(
            candidato=c_pcd, lote=lote, codigo_inscricao='neg2',
            eliminado=True, classificacao=4,
            classificacao_pcd=1, classificacao_nna=None,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert len(resp.data['geral']) == 0
        assert len(resp.data['nna']) == 1
        assert len(resp.data['pcd']) == 1

    def test_estrutura_resposta(self, api_client):
        """Resposta deve conter exatamente as chaves 'geral', 'nna' e 'pcd'."""
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert set(resp.data.keys()) == {'geral', 'nna', 'pcd'}

    def test_sem_eliminados_retorna_listas_vazias(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Nao Eliminado', '070.070.070-70')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='ne1',
            eliminado=False, classificacao=5,
        )

        url = reverse('eliminados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'classificacao_max': '10',
            'classificacao_min': '1',
        })

        assert resp.status_code == 200
        assert resp.data['geral'] == []
        assert resp.data['nna'] == []
        assert resp.data['pcd'] == []
