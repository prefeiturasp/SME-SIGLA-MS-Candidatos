import pytest
from uuid import uuid4
from django.urls import reverse
from rest_framework.test import APIClient
from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
    ConcursoCandidatoReclassificacao,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def lote():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome="Concurso Teste",
    )


def criar_candidato(nome, cpf, email=None):
    if email is None:
        email = f"user-{uuid4().hex[:8]}@example.com"
    return Candidato.objects.create(
        nome=nome, cpf=cpf, email=email, telefone='', data_nascimento='1990-01-01',
        genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes=''
    )


def test_habilitados_filtra_por_ultimo_lote_e_limites(api_client):
    url = reverse('habilitados-reposicao')
    concurso_uuid = uuid4()
    lote1 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='X')
    lote2 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='X2')  # mais recente

    # cria 5 candidatos com várias classificações
    for i in range(1, 6):
        c = criar_candidato(f'C{i}', f'000.000.000-0{i}')
        ConcursoCandidato.objects.create(candidato=c, lote=lote2, codigo_inscricao=str(i), classificacao=i)
    # pcd
    cpcd = criar_candidato('PCD1', '111.111.111-11')
    ConcursoCandidato.objects.create(candidato=cpcd, lote=lote2, codigo_inscricao='pcd1', classificacao_pcd=1)
    # nnatest_habilitados_filtra_por_ultimo_lote_e_limites
    cnna = criar_candidato('NNA1', '222.222.222-22')
    ConcursoCandidato.objects.create(candidato=cnna, lote=lote2, codigo_inscricao='nna1', classificacao_nna=1)

    # lote antigo não deve entrar
    cold = criar_candidato('OLD', '333.333.333-33')
    ConcursoCandidato.objects.create(candidato=cold, lote=lote1, codigo_inscricao='old', classificacao=1)

    resp = api_client.get(
        url,
        {
            'concurso_uuid': str(concurso_uuid),
            'geral': 2,
            'pcd': 1,
            'nna': 1,
        },
    )
    assert resp.status_code == 200
    results = resp.data
    # Deve ter 1 PCD, 1 NNA e 2 gerais (total 4), sem duplicação
    assert len(results) == 4

    # Ordem: primeiro PCD, depois NNA, depois gerais por classificacao
    # Verifica prioridade
    assert results[0]['classificacao_pcd'] is not None
    assert results[1]['classificacao_nna'] is not None
    # restantes gerais
    assert results[2]['classificacao'] is not None
    assert results[3]['classificacao'] is not None

    # candidato aninhado presente
    assert 'candidato' in results[0]
    assert 'nome' in results[0]['candidato']


# --- Testes de Reclassificação de Candidatos habilitados ---


class TestReclassificacaoHabilitados:
    """Testes unitários para o endpoint POST /habilitados/reclassificar/."""

    def test_reclassificar_de_nna_retorna_200_e_atualiza_categoria(self, api_client, lote):
        c = criar_candidato("Candidato NNA", "111.111.111-11")
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="001",
            classificacao=10,
            classificacao_nna=1,
            classificacao_pcd=None,
            categoria_efetiva="NNA",
        )
        url = reverse("habilitados-reclassificar")
        payload = {
            "candidato_uuid": str(cc.uuid),
            "desclassificar_de": "NNA",
            "motivo": "Reclassificação solicitada",
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 200
        assert resp.data["nova_categoria_efetiva"] == "GERAL"
        assert "historico_uuid" in resp.data
        assert "concurso_candidato" in resp.data
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"
        assert ConcursoCandidatoReclassificacao.objects.filter(
            concurso_candidato=cc, desclassificado_de="NNA"
        ).exists()

    def test_reclassificar_de_pcd_retorna_200_e_atualiza_categoria(self, api_client, lote):
        c = criar_candidato("Candidato PCD", "222.222.222-22")
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="002",
            classificacao=20,
            classificacao_nna=None,
            classificacao_pcd=1,
            categoria_efetiva="PCD",
        )
        url = reverse("habilitados-reclassificar")
        payload = {
            "candidato_uuid": str(cc.uuid),
            "desclassificar_de": "PCD",
            "motivo": "",
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 200
        assert resp.data["nova_categoria_efetiva"] == "GERAL"
        cc.refresh_from_db()
        assert cc.categoria_efetiva == "GERAL"

    def test_reclassificar_payload_invalido_retorna_400(self, api_client):
        url = reverse("habilitados-reclassificar")
        resp = api_client.post(url, {}, format="json")
        assert resp.status_code == 400

    def test_reclassificar_candidato_uuid_inexistente_retorna_500(self, api_client):
        url = reverse("habilitados-reclassificar")
        payload = {
            "candidato_uuid": str(uuid4()),
            "desclassificar_de": "NNA",
            "motivo": "",
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 500
        assert "detail" in resp.data

    def test_reclassificar_sem_classificacao_nna_retorna_400(self, api_client, lote):
        c = criar_candidato("Só PCD", "333.333.333-33")
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="003",
            classificacao=30,
            classificacao_nna=None,
            classificacao_pcd=1,
            categoria_efetiva="PCD",
        )
        url = reverse("habilitados-reclassificar")
        payload = {
            "candidato_uuid": str(cc.uuid),
            "desclassificar_de": "NNA",
            "motivo": "",
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 400
        assert "NNA" in (resp.data.get("detail") or "")

    def test_reclassificar_duplicado_para_mesma_cota_retorna_400(self, api_client, lote):
        c = criar_candidato("NNA Duplicado", "444.444.444-44")
        cc = ConcursoCandidato.objects.create(
            candidato=c,
            lote=lote,
            codigo_inscricao="004",
            classificacao=40,
            classificacao_nna=1,
            classificacao_pcd=None,
            categoria_efetiva="NNA",
        )
        url = reverse("habilitados-reclassificar")
        payload = {
            "candidato_uuid": str(cc.uuid),
            "desclassificar_de": "NNA",
            "motivo": "",
        }
        resp1 = api_client.post(url, payload, format="json")
        assert resp1.status_code == 200
        resp2 = api_client.post(url, payload, format="json")
        assert resp2.status_code == 400
        detail = (resp2.data.get("detail") or "").lower()
        assert "nna" in detail or "desclassificação" in detail or "já há" in detail

