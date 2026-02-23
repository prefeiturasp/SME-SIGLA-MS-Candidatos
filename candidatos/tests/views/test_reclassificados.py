import pytest
from uuid import uuid4
from django.urls import reverse
from rest_framework.test import APIClient

from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote
from candidatos.models.reclassificacao import ConcursoCandidatoReclassificacao


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

class TestReclassificadosParametros:
    def test_sem_parametros_retorna_400(self, api_client):
        url = reverse('reclassificados-list')
        resp = api_client.get(url)
        assert resp.status_code == 400
        assert 'detail' in resp.data

    def test_sem_concurso_uuid_retorna_400(self, api_client):
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'processo_uuid': str(uuid4())})
        assert resp.status_code == 400

    def test_sem_processo_uuid_retorna_400(self, api_client):
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'concurso_uuid': str(uuid4())})
        assert resp.status_code == 400

    def test_mensagem_erro_contem_campos_obrigatorios(self, api_client):
        url = reverse('reclassificados-list')
        resp = api_client.get(url)
        assert 'concurso_uuid' in resp.data['detail']
        assert 'processo_uuid' in resp.data['detail']


# ---------------------------------------------------------------------------
# Testes quando não existe lote
# ---------------------------------------------------------------------------

class TestReclassificadosSemLote:
    def test_sem_lote_retorna_listas_vazias(self, api_client):
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(uuid4()),
            'processo_uuid': str(uuid4()),
        })
        assert resp.status_code == 200
        assert resp.data == {'nna': [], 'pcd': []}


# ---------------------------------------------------------------------------
# Testes de filtragem por processo_uuid e categoria
# ---------------------------------------------------------------------------

class TestReclassificadosFiltros:
    def test_retorna_nna_reclassificado(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Candidato NNA', '111.111.111-11')
        cc = ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote,
            codigo_inscricao='001',
            categoria_efetiva='GERAL',
            eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc,
            desclassificado_de='NNA',
            processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 1
        assert len(resp.data['pcd']) == 0

    def test_retorna_pcd_reclassificado(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Candidato PCD', '222.222.222-22')
        cc = ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote,
            codigo_inscricao='002',
            categoria_efetiva='GERAL',
            eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc,
            desclassificado_de='PCD',
            processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['pcd']) == 1
        assert len(resp.data['nna']) == 0

    def test_retorna_nna_e_pcd_separados(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        c_nna = criar_candidato('NNA Candidato', '333.333.333-33')
        cc_nna = ConcursoCandidato.objects.create(
            candidato=c_nna, lote=lote, codigo_inscricao='nna1',
            categoria_efetiva='GERAL', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc_nna, desclassificado_de='NNA', processo_uuid=processo_uuid,
        )

        c_pcd = criar_candidato('PCD Candidato', '444.444.444-44')
        cc_pcd = ConcursoCandidato.objects.create(
            candidato=c_pcd, lote=lote, codigo_inscricao='pcd1',
            categoria_efetiva='GERAL', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc_pcd, desclassificado_de='PCD', processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 1
        assert len(resp.data['pcd']) == 1

    def test_nao_retorna_eliminados(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Eliminado NNA', '555.555.555-55')
        cc = ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='elim1',
            categoria_efetiva='GERAL', eliminado=True,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc, desclassificado_de='NNA', processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 0

    def test_nao_retorna_categoria_nna_ou_pcd(self, api_client):
        """Candidatos que ainda estão em categoria NNA/PCD não devem aparecer."""
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Ainda NNA', '666.666.666-66')
        cc = ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='nna2',
            categoria_efetiva='NNA', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc, desclassificado_de='NNA', processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 0

    def test_usa_ultimo_lote(self, api_client):
        """Candidatos de lotes antigos não devem aparecer."""
        concurso_uuid = uuid4()
        processo_uuid = uuid4()

        lote_antigo = criar_lote(concurso_uuid)
        lote_novo = criar_lote(concurso_uuid)

        candidato_antigo = criar_candidato('Antigo', '777.777.777-77')
        cc_antigo = ConcursoCandidato.objects.create(
            candidato=candidato_antigo, lote=lote_antigo, codigo_inscricao='ant1',
            categoria_efetiva='GERAL', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc_antigo, desclassificado_de='NNA', processo_uuid=processo_uuid,
        )

        candidato_novo = criar_candidato('Novo', '888.888.888-88')
        cc_novo = ConcursoCandidato.objects.create(
            candidato=candidato_novo, lote=lote_novo, codigo_inscricao='nov1',
            categoria_efetiva='GERAL', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc_novo, desclassificado_de='NNA', processo_uuid=processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 1
        ids = [item['id'] for item in resp.data['nna']]
        assert cc_novo.id in ids
        assert cc_antigo.id not in ids

    def test_nao_retorna_outro_processo_uuid(self, api_client):
        """Reclassificações de outro processo não devem aparecer."""
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        outro_processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Outro Processo', '999.999.999-99')
        cc = ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='out1',
            categoria_efetiva='GERAL', eliminado=False,
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=cc, desclassificado_de='NNA', processo_uuid=outro_processo_uuid,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert len(resp.data['nna']) == 0

    def test_estrutura_resposta(self, api_client):
        """Resposta deve conter exatamente as chaves 'nna' e 'pcd'."""
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert set(resp.data.keys()) == {'nna', 'pcd'}

    def test_sem_reclassificados_retorna_listas_vazias(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        candidato = criar_candidato('Sem Reclassificacao', '010.010.010-10')
        ConcursoCandidato.objects.create(
            candidato=candidato, lote=lote, codigo_inscricao='sr1',
            categoria_efetiva='GERAL', eliminado=False,
        )

        url = reverse('reclassificados-list')
        resp = api_client.get(url, {
            'concurso_uuid': str(concurso_uuid),
            'processo_uuid': str(processo_uuid),
        })

        assert resp.status_code == 200
        assert resp.data['nna'] == []
        assert resp.data['pcd'] == []
