"""
Testes unitários para HabilitadosViewSet (candidatos/views/habilitados.py).
Cobre: get_queryset, reposicao, reconvocacao, reclassificar, eliminar,
       convocar, desconvocar, buscar_por_uuids, buscar_por_cpfs, calculados.
"""
import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote


pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


def criar_candidato(nome=None, cpf=None):
    nome = nome or f"Candidato {uuid4().hex[:4]}"
    cpf = cpf or f"{uuid4().int % 99999999999:011d}"
    return Candidato.objects.create(
        nome=nome, cpf=cpf,
        email=f"user-{uuid4().hex[:8]}@example.com",
        telefone='', data_nascimento='1990-01-01',
        genero='M', endereco='', cidade='', estado='', cep='',
        status='ativo', observacoes=''
    )


def criar_lote(concurso_uuid=None):
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=concurso_uuid or uuid4(),
        concurso_nome='Concurso Teste'
    )


def criar_cc(candidato=None, lote=None, **kwargs):
    candidato = candidato or criar_candidato()
    lote = lote or criar_lote()
    defaults = dict(codigo_inscricao=uuid4().hex[:8])
    defaults.update(kwargs)
    return ConcursoCandidato.objects.create(candidato=candidato, lote=lote, **defaults)


# ---------------------------------------------------------------------------
# get_queryset
# ---------------------------------------------------------------------------

class TestGetQueryset:
    def test_sem_concurso_uuid_retorna_todos(self, api_client):
        lote = criar_lote()
        criar_cc(lote=lote)
        resp = api_client.get(reverse('habilitados-list'))
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_com_concurso_uuid_filtra_ultimo_lote(self, api_client):
        concurso_uuid = uuid4()
        lote_antigo = criar_lote(concurso_uuid)
        lote_novo = criar_lote(concurso_uuid)
        c_antigo = criar_candidato()
        c_novo = criar_candidato()
        criar_cc(candidato=c_antigo, lote=lote_antigo)
        cc_novo = criar_cc(candidato=c_novo, lote=lote_novo)

        resp = api_client.get(reverse('habilitados-list'), {'concurso_uuid': str(concurso_uuid)})
        assert resp.status_code == 200
        ids = [item['id'] for item in resp.data]
        assert cc_novo.id in ids

    def test_com_concurso_uuid_sem_lote_retorna_vazio(self, api_client):
        resp = api_client.get(reverse('habilitados-list'), {'concurso_uuid': str(uuid4())})
        assert resp.status_code == 200
        assert resp.data == []

    def test_com_lote__concurso_uuid_filtra_ultimo_lote(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        cc = criar_cc(lote=lote)

        resp = api_client.get(
            reverse('habilitados-list'),
            {'lote__concurso_uuid': str(concurso_uuid)}
        )
        assert resp.status_code == 200
        ids = [item['id'] for item in resp.data]
        assert cc.id in ids


# ---------------------------------------------------------------------------
# reposicao
# ---------------------------------------------------------------------------

class TestReposicao:
    URL = 'habilitados-reposicao'

    def test_sem_concurso_uuid_retorna_400(self, api_client):
        resp = api_client.get(reverse(self.URL))
        assert resp.status_code == 400
        assert 'concurso_uuid' in resp.data['detail']

    def test_sem_lote_retorna_lista_vazia(self, api_client):
        resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4())})
        assert resp.status_code == 200
        assert resp.data == []

    def test_sem_limites_retorna_todos_nao_convocados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        criar_cc(lote=lote, foi_convocado=False)
        criar_cc(lote=lote, foi_convocado=False)
        criar_cc(lote=lote, foi_convocado=True)

        resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(concurso_uuid)})
        assert resp.status_code == 200
        assert len(resp.data) == 2

    def test_filtra_por_codigo_cargo(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        criar_cc(lote=lote, foi_convocado=False, codigo_cargo='CARGO_A', classificacao=1)
        criar_cc(lote=lote, foi_convocado=False, codigo_cargo='CARGO_B', classificacao=2)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'codigo_cargo': 'CARGO_A'}
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_limites_geral_pcd_nna(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        for i in range(1, 4):
            criar_cc(lote=lote, foi_convocado=False, classificacao=i)
        criar_cc(lote=lote, foi_convocado=False, classificacao_pcd=1)
        criar_cc(lote=lote, foi_convocado=False, classificacao_nna=1)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'geral': 2, 'pcd': 1, 'nna': 1}
        )
        assert resp.status_code == 200
        assert len(resp.data) == 4

    def test_limite_geral_zero_nao_inclui_geral(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        criar_cc(lote=lote, foi_convocado=False, classificacao=1)
        criar_cc(lote=lote, foi_convocado=False, classificacao_pcd=1)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'geral': 0, 'pcd': 1}
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_usa_ultimo_lote(self, api_client):
        concurso_uuid = uuid4()
        lote_antigo = criar_lote(concurso_uuid)
        lote_novo = criar_lote(concurso_uuid)
        criar_cc(lote=lote_antigo, foi_convocado=False, classificacao=1)
        cc_novo = criar_cc(lote=lote_novo, foi_convocado=False, classificacao=1)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'geral': 5}
        )
        assert resp.status_code == 200
        ids = [item['id'] for item in resp.data]
        assert cc_novo.id in ids
        assert len(ids) == 1

    def test_nao_inclui_convocados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        criar_cc(lote=lote, foi_convocado=True, classificacao=1)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'geral': 5}
        )
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_sem_candidatos_retorna_vazio(self, api_client):
        concurso_uuid = uuid4()
        criar_lote(concurso_uuid)

        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'geral': 5}
        )
        assert resp.status_code == 200
        assert resp.data == []


# ---------------------------------------------------------------------------
# reconvocacao
# ---------------------------------------------------------------------------

class TestReconvocacao:
    URL = 'habilitados-reconvocacao'

    def test_erro_no_servico_retorna_503(self, api_client):
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes', side_effect=Exception('falha')):
            resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4()), 'quantidade': '1'})
        assert resp.status_code == 503

    def test_sem_reconvocacoes_retorna_lista_vazia(self, api_client):
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes', return_value=[]):
            resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4()), 'quantidade': '1'})
        assert resp.status_code == 200
        assert resp.data == []

    def test_sem_concurso_uuid_retorna_lista_vazia(self, api_client):
        candidato_uuid = str(uuid4())
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': candidato_uuid}]):
            resp = api_client.get(reverse(self.URL), {'quantidade': '2'})
        assert resp.status_code == 200
        assert resp.data == []

    def test_sem_quantidade_retorna_400(self, api_client):
        candidato_uuid = str(uuid4())
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': candidato_uuid}]):
            resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4())})
        assert resp.status_code == 400

    def test_quantidade_invalida_retorna_400(self, api_client):
        candidato_uuid = str(uuid4())
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': candidato_uuid}]):
            resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4()), 'quantidade': 'abc'})
        assert resp.status_code == 400

    def test_quantidade_zero_retorna_400(self, api_client):
        candidato_uuid = str(uuid4())
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': candidato_uuid}]):
            resp = api_client.get(reverse(self.URL), {'concurso_uuid': str(uuid4()), 'quantidade': '0'})
        assert resp.status_code == 400

    def test_sem_lote_retorna_lista_vazia(self, api_client):
        candidato_uuid = str(uuid4())
        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': candidato_uuid}]):
            resp = api_client.get(
                reverse(self.URL),
                {'concurso_uuid': str(uuid4()), 'quantidade': '1'}
            )
        assert resp.status_code == 200
        assert resp.data == []

    def test_retorna_candidatos_convocados_na_lista(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        candidato = criar_candidato()
        cc = criar_cc(candidato=candidato, lote=lote, foi_convocado=True)

        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': str(cc.uuid)}]):
            with patch('candidatos.views.habilitados.atualizar_ranking'):
                with patch('candidatos.views.habilitados.atualizar_ranking_escolha'):
                    resp = api_client.get(
                        reverse(self.URL),
                        {'concurso_uuid': str(concurso_uuid), 'quantidade': '5'}
                    )
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_nao_retorna_nao_convocados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        candidato = criar_candidato()
        cc = criar_cc(candidato=candidato, lote=lote, foi_convocado=False)

        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[{'candidato_uuid': str(cc.uuid)}]):
            resp = api_client.get(
                reverse(self.URL),
                {'concurso_uuid': str(concurso_uuid), 'quantidade': '5'}
            )
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_filtra_por_codigo_cargo(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        cc_a = criar_cc(lote=lote, foi_convocado=True, codigo_cargo='CARGO_A')
        cc_b = criar_cc(lote=lote, foi_convocado=True, codigo_cargo='CARGO_B')

        with patch('candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes',
                   return_value=[
                       {'candidato_uuid': str(cc_a.uuid)},
                       {'candidato_uuid': str(cc_b.uuid)},
                   ]):
            with patch('candidatos.views.habilitados.atualizar_ranking'):
                with patch('candidatos.views.habilitados.atualizar_ranking_escolha'):
                    resp = api_client.get(
                        reverse(self.URL),
                        {'concurso_uuid': str(concurso_uuid), 'quantidade': '5', 'codigo_cargo': 'CARGO_A'}
                    )
        assert resp.status_code == 200
        assert len(resp.data) == 1


# ---------------------------------------------------------------------------
# reclassificar
# ---------------------------------------------------------------------------

class TestReclassificar:
    URL = 'habilitados-reclassificar'

    def _payload(self, candidato_uuid=None, desclassificar_de='NNA', motivo=''):
        return {
            'candidato_uuid': str(candidato_uuid or uuid4()),
            'desclassificar_de': desclassificar_de,
            'motivo': motivo,
        }

    def test_payload_invalido_retorna_400(self, api_client):
        resp = api_client.post(reverse(self.URL), {}, format='json')
        assert resp.status_code == 400

    def test_desclassificar_de_invalido_retorna_400(self, api_client):
        resp = api_client.post(
            reverse(self.URL),
            {'candidato_uuid': str(uuid4()), 'desclassificar_de': 'INVALIDO'},
            format='json'
        )
        assert resp.status_code == 400

    def test_sucesso_retorna_200_com_dados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        cc = criar_cc(lote=lote, categoria_efetiva='GERAL')
        hist_mock = MagicMock()
        hist_mock.uuid = uuid4()

        with patch('candidatos.views.habilitados.aplicar_reclassificacao', return_value=(cc, hist_mock)):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(candidato_uuid=cc.uuid),
                format='json'
            )
        assert resp.status_code == 200
        assert 'concurso_candidato' in resp.data
        assert 'historico_uuid' in resp.data
        assert 'nova_categoria_efetiva' in resp.data

    def test_value_error_retorna_400(self, api_client):
        with patch('candidatos.views.habilitados.aplicar_reclassificacao', side_effect=ValueError('não encontrado')):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(),
                format='json'
            )
        assert resp.status_code == 400
        assert 'não encontrado' in resp.data['detail']

    def test_excecao_generica_retorna_500(self, api_client):
        with patch('candidatos.views.habilitados.aplicar_reclassificacao', side_effect=Exception('erro inesperado')):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(),
                format='json'
            )
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# eliminar
# ---------------------------------------------------------------------------

class TestEliminar:
    URL = 'habilitados-eliminar'

    def _payload(self, candidato_uuid=None, motivo=''):
        return {
            'candidato_uuid': str(candidato_uuid or uuid4()),
            'motivo': motivo,
        }

    def test_payload_invalido_retorna_400(self, api_client):
        resp = api_client.post(reverse(self.URL), {}, format='json')
        assert resp.status_code == 400

    def test_sucesso_retorna_200_com_dados(self, api_client):
        lote = criar_lote()
        cc = criar_cc(lote=lote)
        hist_mock = MagicMock()
        hist_mock.uuid = uuid4()

        with patch('candidatos.views.habilitados.aplicar_eliminacao', return_value=(cc, hist_mock)):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(candidato_uuid=cc.uuid),
                format='json'
            )
        assert resp.status_code == 200
        assert 'concurso_candidato' in resp.data
        assert 'historico_uuid' in resp.data
        assert resp.data['acao'] == 'ELIMINAR'

    def test_value_error_retorna_400(self, api_client):
        with patch('candidatos.views.habilitados.aplicar_eliminacao', side_effect=ValueError('candidato não encontrado')):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(),
                format='json'
            )
        assert resp.status_code == 400

    def test_excecao_generica_retorna_500(self, api_client):
        with patch('candidatos.views.habilitados.aplicar_eliminacao', side_effect=Exception('erro')):
            resp = api_client.post(
                reverse(self.URL),
                self._payload(),
                format='json'
            )
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# convocar
# ---------------------------------------------------------------------------

class TestConvocar:
    URL = 'habilitados-convocar'

    def test_payload_invalido_retorna_400(self, api_client):
        resp = api_client.patch(reverse(self.URL), {}, format='json')
        assert resp.status_code == 400

    def test_candidatos_nao_lista_retorna_400(self, api_client):
        resp = api_client.patch(
            reverse(self.URL),
            {'concurso_uuid': str(uuid4()), 'candidatos': 'nao-lista'},
            format='json'
        )
        assert resp.status_code == 400

    def test_lote_inexistente_retorna_404(self, api_client):
        resp = api_client.patch(
            reverse(self.URL),
            {'concurso_uuid': str(uuid4()), 'candidatos': []},
            format='json'
        )
        assert resp.status_code == 404

    def test_sucesso_marca_convocados(self, api_client):
        concurso_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        cc1 = criar_cc(lote=lote, foi_convocado=False)
        cc2 = criar_cc(lote=lote, foi_convocado=False)

        resp = api_client.patch(
            reverse(self.URL),
            {
                'concurso_uuid': str(concurso_uuid),
                'candidatos': [str(cc1.uuid), str(cc2.uuid)]
            },
            format='json'
        )
        assert resp.status_code == 200
        assert resp.data['total'] == 2
        cc1.refresh_from_db()
        cc2.refresh_from_db()
        assert cc1.foi_convocado is True
        assert cc2.foi_convocado is True

    def test_sucesso_com_processo_uuid(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)
        cc = criar_cc(lote=lote, foi_convocado=False)

        resp = api_client.patch(
            reverse(self.URL),
            {
                'concurso_uuid': str(concurso_uuid),
                'processo_uuid': str(processo_uuid),
                'candidatos': [str(cc.uuid)]
            },
            format='json'
        )
        assert resp.status_code == 200
        cc.refresh_from_db()
        assert cc.foi_convocado is True

    def test_lista_vazia_retorna_zero(self, api_client):
        concurso_uuid = uuid4()
        criar_lote(concurso_uuid)

        resp = api_client.patch(
            reverse(self.URL),
            {'concurso_uuid': str(concurso_uuid), 'candidatos': []},
            format='json'
        )
        assert resp.status_code == 200
        assert resp.data['total'] == 0


# ---------------------------------------------------------------------------
# desconvocar
# ---------------------------------------------------------------------------

class TestDesconvocar:
    URL = 'habilitados-desconvocar'

    def test_sem_processo_uuid_retorna_400(self, api_client):
        resp = api_client.patch(
            reverse(self.URL),
            {'codigo_cargo': '123'},
            format='json'
        )
        assert resp.status_code == 400

    def test_sem_codigo_cargo_retorna_400(self, api_client):
        resp = api_client.patch(
            reverse(self.URL),
            {'processo_uuid': str(uuid4())},
            format='json'
        )
        assert resp.status_code == 400

    def test_payload_vazio_retorna_400(self, api_client):
        resp = api_client.patch(reverse(self.URL), {}, format='json')
        assert resp.status_code == 400

    def test_sucesso_desmarca_convocados(self, api_client):
        processo_uuid = uuid4()
        lote = criar_lote()
        cc = criar_cc(
            lote=lote,
            foi_convocado=True,
            processo_uuid=processo_uuid,
            codigo_cargo='CARGO_X'
        )

        resp = api_client.patch(
            reverse(self.URL),
            {'processo_uuid': str(processo_uuid), 'codigo_cargo': 'CARGO_X'},
            format='json'
        )
        assert resp.status_code == 200
        assert resp.data['total'] == 1
        cc.refresh_from_db()
        assert cc.foi_convocado is False
        assert cc.data_convocacao is None

    def test_aceita_concurso_uuid_como_alias(self, api_client):
        processo_uuid = uuid4()
        lote = criar_lote()
        cc = criar_cc(
            lote=lote,
            foi_convocado=True,
            processo_uuid=processo_uuid,
            codigo_cargo='CARGO_Y'
        )

        resp = api_client.patch(
            reverse(self.URL),
            {'concurso_uuid': str(processo_uuid), 'codigo_cargo': 'CARGO_Y'},
            format='json'
        )
        assert resp.status_code == 200
        cc.refresh_from_db()
        assert cc.foi_convocado is False

    def test_nao_afeta_outros_cargos(self, api_client):
        processo_uuid = uuid4()
        lote = criar_lote()
        cc_a = criar_cc(lote=lote, foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo='CARGO_A')
        cc_b = criar_cc(lote=lote, foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo='CARGO_B')

        api_client.patch(
            reverse(self.URL),
            {'processo_uuid': str(processo_uuid), 'codigo_cargo': 'CARGO_A'},
            format='json'
        )
        cc_b.refresh_from_db()
        assert cc_b.foi_convocado is True

    def test_resposta_contem_campos_esperados(self, api_client):
        processo_uuid = uuid4()
        resp = api_client.patch(
            reverse(self.URL),
            {'processo_uuid': str(processo_uuid), 'codigo_cargo': 'CARGO_Z'},
            format='json'
        )
        assert resp.status_code == 200
        assert 'desconvocados' in resp.data
        assert 'total' in resp.data
        assert 'processo_uuid' in resp.data
        assert 'codigo_cargo' in resp.data


# ---------------------------------------------------------------------------
# buscar_por_uuids
# ---------------------------------------------------------------------------

class TestBuscarPorUuids:
    URL = 'habilitados-buscar-por-uuids'

    def test_sem_uuids_retorna_400(self, api_client):
        resp = api_client.post(reverse(self.URL), {}, format='json')
        assert resp.status_code == 400

    def test_lista_vazia_retorna_400(self, api_client):
        resp = api_client.post(reverse(self.URL), {'uuids': []}, format='json')
        assert resp.status_code == 400

    def test_uuid_invalido_retorna_400(self, api_client):
        resp = api_client.post(reverse(self.URL), {'uuids': ['nao-e-uuid']}, format='json')
        assert resp.status_code == 400

    def test_retorna_candidatos_encontrados(self, api_client):
        lote = criar_lote()
        cc = criar_cc(lote=lote)

        resp = api_client.post(
            reverse(self.URL),
            {'uuids': [str(cc.uuid)]},
            format='json'
        )
        assert resp.status_code == 200
        assert 'results' in resp.data
        assert len(resp.data['results']) == 1

    def test_uuid_inexistente_retorna_vazio(self, api_client):
        resp = api_client.post(
            reverse(self.URL),
            {'uuids': [str(uuid4())]},
            format='json'
        )
        assert resp.status_code == 200
        assert resp.data['results'] == []

    def test_order_by_invalido_retorna_400(self, api_client):
        lote = criar_lote()
        cc = criar_cc(lote=lote)

        resp = api_client.post(
            f"{reverse(self.URL)}?order_by=campo_inexistente",
            {'uuids': [str(cc.uuid)]},
            format='json'
        )
        assert resp.status_code == 400

    def test_retorna_multiplos_candidatos(self, api_client):
        lote = criar_lote()
        cc1 = criar_cc(lote=lote)
        cc2 = criar_cc(lote=lote)

        resp = api_client.post(
            reverse(self.URL),
            {'uuids': [str(cc1.uuid), str(cc2.uuid)]},
            format='json'
        )
        assert resp.status_code == 200
        assert len(resp.data['results']) == 2


# ---------------------------------------------------------------------------
# buscar_por_cpfs
# ---------------------------------------------------------------------------

class TestBuscarPorCpfs:
    URL = 'habilitados-buscar-por-cpfs'

    def test_sem_cpfs_retorna_400(self, api_client):
        resp = api_client.post(
            reverse(self.URL),
            {'processo_uuid': str(uuid4())},
            format='json'
        )
        assert resp.status_code == 400

    def test_sem_processo_uuid_retorna_400(self, api_client):
        resp = api_client.post(
            reverse(self.URL),
            {'cpfs': ['12345678901']},
            format='json'
        )
        assert resp.status_code == 400

    def test_lista_cpfs_vazia_retorna_400(self, api_client):
        resp = api_client.post(
            reverse(self.URL),
            {'cpfs': [], 'processo_uuid': str(uuid4())},
            format='json'
        )
        assert resp.status_code == 400

    def test_retorna_candidatos_do_processo(self, api_client):
        processo_uuid = uuid4()
        lote = criar_lote()
        candidato = criar_candidato(cpf='12345678901')
        criar_cc(candidato=candidato, lote=lote, processo_uuid=processo_uuid)

        resp = api_client.post(
            reverse(self.URL),
            {'cpfs': ['12345678901'], 'processo_uuid': str(processo_uuid)},
            format='json'
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_nao_retorna_candidatos_de_outro_processo(self, api_client):
        processo_uuid = uuid4()
        outro_processo = uuid4()
        lote = criar_lote()
        candidato = criar_candidato(cpf='98765432100')
        criar_cc(candidato=candidato, lote=lote, processo_uuid=outro_processo)

        resp = api_client.post(
            reverse(self.URL),
            {'cpfs': ['98765432100'], 'processo_uuid': str(processo_uuid)},
            format='json'
        )
        assert resp.status_code == 200
        assert len(resp.data) == 0

    def test_order_by_invalido_retorna_400(self, api_client):
        resp = api_client.post(
            f"{reverse(self.URL)}?order_by=campo_inexistente",
            {'cpfs': ['11111111111'], 'processo_uuid': str(uuid4())},
            format='json'
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# calculados
# ---------------------------------------------------------------------------

class TestCalculados:
    URL = 'habilitados-calculados'

    def test_sem_parametros_retorna_400(self, api_client):
        resp = api_client.get(reverse(self.URL))
        assert resp.status_code == 400

    def test_sem_quantidade_retorna_400(self, api_client):
        resp = api_client.get(
            reverse(self.URL),
            {'concurso_uuid': str(uuid4()), 'processo_uuid': str(uuid4())}
        )
        assert resp.status_code == 400

    def test_sem_concurso_uuid_retorna_400(self, api_client):
        resp = api_client.get(
            reverse(self.URL),
            {'quantidade': '5', 'processo_uuid': str(uuid4())}
        )
        assert resp.status_code == 400

    def test_sem_processo_uuid_retorna_400(self, api_client):
        resp = api_client.get(
            reverse(self.URL),
            {'quantidade': '5', 'concurso_uuid': str(uuid4())}
        )
        assert resp.status_code == 400

    def test_lote_inexistente_retorna_404(self, api_client):
        with patch('candidatos.views.habilitados.EscolhasService.buscar_escolhas', return_value=[]):
            resp = api_client.get(
                reverse(self.URL),
                {
                    'quantidade': '5',
                    'concurso_uuid': str(uuid4()),
                    'processo_uuid': str(uuid4()),
                    'codigo_cargo': 'CARGO_X',
                }
            )
        assert resp.status_code == 404

    def test_sucesso_retorna_estrutura_correta(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        with patch('candidatos.views.habilitados.EscolhasService.buscar_escolhas', return_value=[]):
            with patch('candidatos.views.habilitados.gerar_sequencia_convocados', return_value=[]):
                resp = api_client.get(
                    reverse(self.URL),
                    {
                        'quantidade': '5',
                        'concurso_uuid': str(concurso_uuid),
                        'processo_uuid': str(processo_uuid),
                        'codigo_cargo': 'CARGO_X',
                    }
                )
        assert resp.status_code == 200
        assert 'quantidade' in resp.data
        assert 'concurso_uuid' in resp.data
        assert 'lote_uuid' in resp.data
        assert 'results' in resp.data

    def test_erro_no_servico_escolhas_usa_lista_vazia(self, api_client):
        concurso_uuid = uuid4()
        processo_uuid = uuid4()
        lote = criar_lote(concurso_uuid)

        with patch('candidatos.views.habilitados.EscolhasService.buscar_escolhas', side_effect=Exception('falha')):
            with patch('candidatos.views.habilitados.gerar_sequencia_convocados', return_value=[]) as mock_gerar:
                resp = api_client.get(
                    reverse(self.URL),
                    {
                        'quantidade': '5',
                        'concurso_uuid': str(concurso_uuid),
                        'processo_uuid': str(processo_uuid),
                        'codigo_cargo': 'CARGO_X',
                    }
                )
        assert resp.status_code == 200
        mock_gerar.assert_called_once()
        _, call_args, _ = mock_gerar.mock_calls[0]
        assert call_args[2] == []
