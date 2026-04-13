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


def test_habilitados_list_quando_concurso_uuid_filtra_apenas_ultimo_lote(api_client):
    """
    `HabilitadosViewSet.get_queryset()` deve restringir ao último lote do concurso
    sempre que `concurso_uuid` (ou `lote__concurso_uuid`) for informado.
    """
    concurso_uuid = uuid4()
    lote_antigo = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Antigo')
    lote_recente = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Recente')

    cold = criar_candidato('OLD', '999.999.999-99')
    cnew = criar_candidato('NEW', '888.888.888-88')
    ConcursoCandidato.objects.create(candidato=cold, lote=lote_antigo, codigo_inscricao='old', classificacao=1)
    ConcursoCandidato.objects.create(candidato=cnew, lote=lote_recente, codigo_inscricao='new', classificacao=1)

    url = reverse('habilitados-list')
    resp = api_client.get(url, {'concurso_uuid': str(concurso_uuid)})
    assert resp.status_code == 200
    # Sem paginação: deve ser lista
    assert isinstance(resp.data, list)
    assert len(resp.data) == 1
    assert resp.data[0]['candidato']['cpf'] == '888.888.888-88'


def test_habilitados_list_quando_concurso_uuid_sem_lote_retorna_vazio(api_client):
    url = reverse('habilitados-list')
    resp = api_client.get(url, {'concurso_uuid': str(uuid4())})
    assert resp.status_code == 200
    assert resp.data == []


def test_habilitados_list_quando_lote_uuid_informado_nao_restringe_ao_ultimo_lote(api_client):
    """
    Se o filtro for por `lote__uuid` diretamente (sem `concurso_uuid`),
    o `get_queryset()` não restringe ao último lote (conforme docstring).
    """
    concurso_uuid = uuid4()
    lote1 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='L1')
    lote2 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='L2')

    c1 = criar_candidato('C1', '777.777.777-77')
    c2 = criar_candidato('C2', '666.666.666-66')
    ConcursoCandidato.objects.create(candidato=c1, lote=lote1, codigo_inscricao='1', classificacao=1)
    ConcursoCandidato.objects.create(candidato=c2, lote=lote2, codigo_inscricao='2', classificacao=1)

    url = reverse('habilitados-list')
    resp = api_client.get(url, {'lote__uuid': str(lote1.uuid)})
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['candidato']['cpf'] == '777.777.777-77'


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


def test_habilitados_desconvocar_sem_codigo_cargo_desconvoca_todos(api_client, lote):
    """Quando codigo_cargo não é enviado, desconvoca todos os cargos do processo."""
    processo_uuid = uuid4()
    c1 = criar_candidato("C1", "111.111.111-11")
    c2 = criar_candidato("C2", "222.222.222-22")
    cc1 = ConcursoCandidato.objects.create(
        candidato=c1, lote=lote, codigo_inscricao="1", foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo="1008"
    )
    cc2 = ConcursoCandidato.objects.create(
        candidato=c2, lote=lote, codigo_inscricao="2", foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo="2001"
    )

    url = reverse("habilitados-desconvocar")
    resp = api_client.patch(url, {"processo_uuid": str(processo_uuid)}, format="json")

    assert resp.status_code == 200
    assert resp.data["total"] == 2
    assert set(resp.data["desconvocados"]) == {str(cc1.uuid), str(cc2.uuid)}
    assert resp.data["codigo_cargo"] is None

    cc1.refresh_from_db()
    cc2.refresh_from_db()
    assert cc1.foi_convocado is False
    assert cc1.processo_uuid is None
    assert cc2.foi_convocado is False
    assert cc2.processo_uuid is None


def test_habilitados_desconvocar_com_codigo_cargo_desconvoca_so_um(api_client, lote):
    """Quando codigo_cargo é enviado, desconvoca apenas os registros daquele cargo."""
    processo_uuid = uuid4()
    c1 = criar_candidato("C1", "333.333.333-33")
    c2 = criar_candidato("C2", "444.444.444-44")
    cc1 = ConcursoCandidato.objects.create(
        candidato=c1, lote=lote, codigo_inscricao="1", foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo="1008"
    )
    cc2 = ConcursoCandidato.objects.create(
        candidato=c2, lote=lote, codigo_inscricao="2", foi_convocado=True, processo_uuid=processo_uuid, codigo_cargo="2001"
    )

    url = reverse("habilitados-desconvocar")
    resp = api_client.patch(
        url, {"processo_uuid": str(processo_uuid), "codigo_cargo": "1008"}, format="json"
    )

    assert resp.status_code == 200
    assert resp.data["total"] == 1
    assert resp.data["desconvocados"] == [str(cc1.uuid)]
    assert resp.data["codigo_cargo"] == "1008"

    cc1.refresh_from_db()
    cc2.refresh_from_db()
    assert cc1.foi_convocado is False
    assert cc1.processo_uuid is None
    assert cc2.foi_convocado is True
    assert str(cc2.processo_uuid) == str(processo_uuid)


def test_habilitados_desconvocar_sem_processo_uuid_retorna_400(api_client):
    url = reverse("habilitados-desconvocar")
    resp = api_client.patch(url, {"codigo_cargo": "1008"}, format="json")
    assert resp.status_code == 400
    assert "processo_uuid" in resp.data["detail"]


def test_habilitados_buscar_por_cpfs_retorna_dados_do_processo(api_client, lote):
    processo_uuid = uuid4()
    # 2 candidatos no processo
    c1 = criar_candidato("C1", "12345678901")
    c2 = criar_candidato("C2", "98765432100")
    ConcursoCandidato.objects.create(
        candidato=c1,
        lote=lote,
        codigo_inscricao="1",
        processo_uuid=processo_uuid,
        classificacao=2,
    )
    ConcursoCandidato.objects.create(
        candidato=c2,
        lote=lote,
        codigo_inscricao="2",
        processo_uuid=processo_uuid,
        classificacao=1,
    )
    # Mesmo cpf, mas em outro processo: não pode retornar
    c3 = criar_candidato("C3", "11122233344")
    ConcursoCandidato.objects.create(
        candidato=c3,
        lote=lote,
        codigo_inscricao="3",
        processo_uuid=uuid4(),
        classificacao=1,
    )

    url = reverse("habilitados-buscar-por-cpfs")
    payload = {"cpfs": ["12345678901", "98765432100", "11122233344"], "processo_uuid": str(processo_uuid)}

    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 200
    assert isinstance(resp.data, list)
    # Deve retornar só os 2 do processo informado
    assert len(resp.data) == 2
    returned_cpfs = {item["cpf"] for item in resp.data}
    assert returned_cpfs == {"12345678901", "98765432100"}
    # Default order_by = classificacao (asc): cpf do c2 (classificacao=1) deve vir primeiro
    assert resp.data[0]["cpf"] == "98765432100"


def test_habilitados_buscar_por_cpfs_order_by_invalido_retorna_400(api_client):
    url = reverse("habilitados-buscar-por-cpfs")
    payload = {"cpfs": ["12345678901"], "processo_uuid": str(uuid4())}
    resp = api_client.post(url + "?order_by=campo_inexistente", payload, format="json")
    assert resp.status_code == 400
    assert resp.data["detail"] == "Parâmetro order_by inválido"


def test_habilitados_calculados_sem_lote_retorna_404(api_client):
    url = reverse("habilitados-calculados")
    resp = api_client.get(
        url,
        {
            "quantidade": 5,
            "concurso_uuid": str(uuid4()),
            "processo_uuid": str(uuid4()),
            "codigo_cargo": "1008",
        },
    )
    assert resp.status_code == 404
    assert resp.data["detail"] == "Lote não encontrado para o concurso_uuid informado"


@patch("candidatos.views.habilitados.EscolhasService.buscar_escolhas")
@patch("candidatos.views.habilitados.gerar_sequencia_convocados")
def test_habilitados_calculados_sucesso_mockando_externos(
    mock_gerar_sequencia,
    mock_buscar_escolhas,
    api_client,
):
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome="X")

    mock_buscar_escolhas.return_value = [
        {"candidato_uuid": "u1"},
        {"candidato_uuid": None},
        {},
        {"candidato_uuid": "u2"},
    ]
    mock_gerar_sequencia.return_value = []

    url = reverse("habilitados-calculados")
    resp = api_client.get(
        url,
        {
            "quantidade": 3,
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "codigo_cargo": "1008",
        },
    )

    assert resp.status_code == 200
    assert resp.data["quantidade"] == 3
    assert resp.data["concurso_uuid"] == str(concurso_uuid)
    assert resp.data["lote_uuid"] == str(lote.uuid)
    assert resp.data["results"] == []

    mock_buscar_escolhas.assert_called_once_with(concurso_uuid=str(concurso_uuid))
    mock_gerar_sequencia.assert_called_once()
    args = mock_gerar_sequencia.call_args.args
    assert args[0] == 3  # quantidade
    assert args[1] == lote
    assert args[2] == ["u1", "u2"]  # escolhas_candidato_uuids filtrado
    assert args[3] == "1008"  # codigo_cargo
    assert args[4] == str(processo_uuid)


@patch("candidatos.views.habilitados.EscolhasService.buscar_escolhas", side_effect=Exception("ms caiu"))
@patch("candidatos.views.habilitados.gerar_sequencia_convocados")
def test_habilitados_calculados_quando_escolhas_falha_continua_com_lista_vazia(
    mock_gerar_sequencia,
    mock_buscar_escolhas,
    api_client,
):
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome="X")

    mock_gerar_sequencia.return_value = []

    url = reverse("habilitados-calculados")
    resp = api_client.get(
        url,
        {
            "quantidade": 2,
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "codigo_cargo": "1008",
        },
    )

    assert resp.status_code == 200
    assert resp.data["lote_uuid"] == str(lote.uuid)
    assert resp.data["results"] == []
    mock_buscar_escolhas.assert_called_once_with(concurso_uuid=str(concurso_uuid))

    args = mock_gerar_sequencia.call_args.args
    assert args[2] == []  # escolhas_candidato_uuids vazio

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
        assert resp.status_code == 400
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

