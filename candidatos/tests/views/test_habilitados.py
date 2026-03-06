import pytest
from unittest.mock import patch, MagicMock
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


# --- Reconvocação (GET /habilitados/reconvocacao/) ---


class TestReconvocacao:
    def test_erro_servico_retorna_503(self, api_client):
        with patch("candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes", side_effect=Exception("falha")):
            resp = api_client.get(
                reverse("habilitados-reconvocacao"),
                {"concurso_uuid": str(uuid4()), "quantidade": "1"},
            )
        assert resp.status_code == 503
        assert "reconvocações" in resp.data.get("detail", "")

    def test_sem_reconvocacoes_retorna_lista_vazia(self, api_client):
        with patch("candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes", return_value=[]):
            resp = api_client.get(
                reverse("habilitados-reconvocacao"),
                {"concurso_uuid": str(uuid4()), "quantidade": "1"},
            )
        assert resp.status_code == 200
        assert resp.data == []

    def test_sem_concurso_uuid_retorna_lista_vazia(self, api_client):
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(uuid4())}],
        ):
            resp = api_client.get(reverse("habilitados-reconvocacao"), {"quantidade": "1"})
        assert resp.status_code == 200
        assert resp.data == []

    def test_sem_quantidade_retorna_400(self, api_client):
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(uuid4())}],
        ):
            resp = api_client.get(reverse("habilitados-reconvocacao"), {"concurso_uuid": str(uuid4())})
        assert resp.status_code == 400
        assert "quantidade" in resp.data.get("detail", "").lower()

    def test_quantidade_invalida_retorna_400(self, api_client):
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(uuid4())}],
        ):
            resp = api_client.get(
                reverse("habilitados-reconvocacao"),
                {"concurso_uuid": str(uuid4()), "quantidade": "abc"},
            )
        assert resp.status_code == 400

    def test_quantidade_zero_retorna_400(self, api_client):
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(uuid4())}],
        ):
            resp = api_client.get(
                reverse("habilitados-reconvocacao"),
                {"concurso_uuid": str(uuid4()), "quantidade": "0"},
            )
        assert resp.status_code == 400

    def test_sem_lote_retorna_lista_vazia(self, api_client):
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(uuid4())}],
        ):
            resp = api_client.get(
                reverse("habilitados-reconvocacao"),
                {"concurso_uuid": str(uuid4()), "quantidade": "1"},
            )
        assert resp.status_code == 200
        assert resp.data == []

    def test_retorna_convocados_na_lista_reconvocacoes(self, api_client, lote):
        c = criar_candidato("Reconv", "555.555.555-55")
        cc = ConcursoCandidato.objects.create(
            candidato=c, lote=lote, codigo_inscricao="rc1", foi_convocado=True
        )
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(cc.uuid)}],
        ):
            with patch("candidatos.views.habilitados.atualizar_ranking"):
                with patch("candidatos.views.habilitados.atualizar_ranking_escolha"):
                    resp = api_client.get(
                        reverse("habilitados-reconvocacao"),
                        {"concurso_uuid": str(lote.concurso_uuid), "quantidade": "5"},
                    )
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["codigo_inscricao"] == "rc1"

    def test_filtra_por_codigo_cargo(self, api_client, lote):
        c1 = criar_candidato("C1", "666.666.666-66")
        c2 = criar_candidato("C2", "777.777.777-77")
        cc1 = ConcursoCandidato.objects.create(
            candidato=c1, lote=lote, codigo_inscricao="a", foi_convocado=True, codigo_cargo="CARGO_A"
        )
        cc2 = ConcursoCandidato.objects.create(
            candidato=c2, lote=lote, codigo_inscricao="b", foi_convocado=True, codigo_cargo="CARGO_B"
        )
        with patch(
            "candidatos.views.habilitados.EscolhasService.buscar_reconvocacoes",
            return_value=[{"candidato_uuid": str(cc1.uuid)}, {"candidato_uuid": str(cc2.uuid)}],
        ):
            with patch("candidatos.views.habilitados.atualizar_ranking"):
                with patch("candidatos.views.habilitados.atualizar_ranking_escolha"):
                    resp = api_client.get(
                        reverse("habilitados-reconvocacao"),
                        {"concurso_uuid": str(lote.concurso_uuid), "quantidade": "5", "codigo_cargo": "CARGO_A"},
                    )
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["codigo_cargo"] == "CARGO_A"


# --- Eliminar (POST /habilitados/eliminar/) ---


class TestEliminar:
    def test_payload_invalido_retorna_400(self, api_client):
        resp = api_client.post(reverse("habilitados-eliminar"), {}, format="json")
        assert resp.status_code == 400

    def test_sucesso_retorna_200_com_dados(self, api_client, lote):
        cc = ConcursoCandidato.objects.create(
            candidato=criar_candidato("Elim", "888.888.888-88"),
            lote=lote,
            codigo_inscricao="el1",
        )
        hist_mock = MagicMock()
        hist_mock.uuid = uuid4()
        with patch("candidatos.views.habilitados.aplicar_eliminacao", return_value=(cc, hist_mock)):
            resp = api_client.post(
                reverse("habilitados-eliminar"),
                {"candidato_uuid": str(cc.uuid), "motivo": "Teste"},
                format="json",
            )
        assert resp.status_code == 200
        assert "concurso_candidato" in resp.data
        assert "historico_uuid" in resp.data
        assert resp.data["acao"] == "ELIMINAR"

    def test_value_error_retorna_400(self, api_client):
        with patch(
            "candidatos.views.habilitados.aplicar_eliminacao",
            side_effect=ValueError("candidato não encontrado"),
        ):
            resp = api_client.post(
                reverse("habilitados-eliminar"),
                {"candidato_uuid": str(uuid4()), "motivo": ""},
                format="json",
            )
        assert resp.status_code == 400
        assert "candidato não encontrado" in resp.data.get("detail", "")

    def test_excecao_generica_retorna_500(self, api_client):
        with patch("candidatos.views.habilitados.aplicar_eliminacao", side_effect=Exception("erro")):
            resp = api_client.post(
                reverse("habilitados-eliminar"),
                {"candidato_uuid": str(uuid4()), "motivo": ""},
                format="json",
            )
        assert resp.status_code == 500
        assert "detail" in resp.data


# --- Buscar por UUIDs (POST /habilitados/buscar-por-uuids/) ---


class TestBuscarPorUuids:
    def test_sem_uuids_retorna_400(self, api_client):
        resp = api_client.post(reverse("habilitados-buscar-por-uuids"), {}, format="json")
        assert resp.status_code == 400

    def test_lista_vazia_retorna_400(self, api_client):
        resp = api_client.post(reverse("habilitados-buscar-por-uuids"), {"uuids": []}, format="json")
        assert resp.status_code == 400

    def test_uuid_invalido_retorna_400(self, api_client):
        resp = api_client.post(
            reverse("habilitados-buscar-por-uuids"),
            {"uuids": ["nao-e-uuid"]},
            format="json",
        )
        assert resp.status_code == 400

    def test_retorna_candidatos_encontrados(self, api_client, lote):
        cc = ConcursoCandidato.objects.create(
            candidato=criar_candidato("Uuid", "999.999.999-99"),
            lote=lote,
            codigo_inscricao="uu1",
        )
        resp = api_client.post(
            reverse("habilitados-buscar-por-uuids"),
            {"uuids": [str(cc.uuid)]},
            format="json",
        )
        assert resp.status_code == 200
        assert "results" in resp.data
        assert len(resp.data["results"]) == 1
        assert resp.data["results"][0]["codigo_inscricao"] == "uu1"

    def test_uuid_inexistente_retorna_vazio(self, api_client):
        resp = api_client.post(
            reverse("habilitados-buscar-por-uuids"),
            {"uuids": [str(uuid4())]},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["results"] == []

    def test_order_by_invalido_retorna_400(self, api_client, lote):
        cc = ConcursoCandidato.objects.create(
            candidato=criar_candidato("O", "101.101.101-10"),
            lote=lote,
            codigo_inscricao="oo1",
        )
        resp = api_client.post(
            reverse("habilitados-buscar-por-uuids") + "?order_by=campo_inexistente",
            {"uuids": [str(cc.uuid)]},
            format="json",
        )
        assert resp.status_code == 400
        assert "order_by" in resp.data.get("detail", "").lower()

