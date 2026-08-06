"""Testes mínimos para EliminadosViewSet.list (GET /eliminados/)."""

from uuid import uuid4

import pytest
from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoEliminacao,
)
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    """Cliente HTTP para requisições de teste."""
    return APIClient()


def _candidato(**kwargs):
    """Candidato de exemplo para os testes."""
    return Candidato.objects.create(
        nome=kwargs.get("nome", "Teste"),
        cpf=kwargs.get("cpf", f"{uuid4().int % 10 ** 11:011d}"),
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


def _cc(concurso_uuid, candidato=None, **kwargs):
    """ConcursoCandidato de exemplo para os testes."""
    return ConcursoCandidato.objects.create(
        candidato=candidato or _candidato(),
        concurso_uuid=concurso_uuid,
        concurso_nome="Concurso Teste",
        codigo_inscricao=kwargs.get("codigo_inscricao", uuid4().hex[:8]),
        eliminado=kwargs.get("eliminado", True),
        classificacao=kwargs.get("classificacao"),
        classificacao_nna=kwargs.get("classificacao_nna"),
        classificacao_pcd=kwargs.get("classificacao_pcd"),
    )


def test_parametros_obrigatorios(api_client):
    """Verifica parametros obrigatorios."""
    url = reverse("eliminados-list")
    assert api_client.get(url).status_code == 400
    assert (
        api_client.get(url, {"concurso_uuid": str(uuid4())}).status_code == 400
    )
    assert (
        api_client.get(
            url,
            {
                "concurso_uuid": str(uuid4()),
                "processo_uuid": str(uuid4()),
                "classificacao_max": "10",
            },
        ).status_code
        == 400
    )


def test_sem_candidatos_retorna_listas_vazias(api_client):
    """Verifica sem candidatos retorna listas vazias."""
    url = reverse("eliminados-list")
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    resp = api_client.get(
        url,
        {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "classificacao_max": "10",
            "classificacao_min": "0",
        },
    )
    assert resp.status_code == 200
    assert resp.data == {"geral": [], "nna": [], "pcd": []}


def test_retorna_eliminados_separados_e_filtra_classificacao(api_client):
    """Verifica retorna eliminados separados e filtra classificacao."""
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    cc_geral = _cc(
        concurso_uuid,
        eliminado=True,
        classificacao=5,
        classificacao_nna=None,
        classificacao_pcd=None,
    )
    cc_nna = _cc(
        concurso_uuid,
        eliminado=True,
        classificacao=3,
        classificacao_nna=1,
        classificacao_pcd=None,
    )
    cc_pcd = _cc(
        concurso_uuid,
        eliminado=True,
        classificacao=2,
        classificacao_nna=None,
        classificacao_pcd=1,
    )
    cc_max_out = _cc(
        concurso_uuid,
        eliminado=True,
        classificacao=15,
        classificacao_nna=None,
        classificacao_pcd=None,
    )
    _cc(
        concurso_uuid,
        eliminado=False,
        classificacao=1,
        classificacao_nna=None,
        classificacao_pcd=None,
    )
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_geral, processo_uuid=processo_uuid
    )
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_nna, processo_uuid=processo_uuid
    )
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_pcd, processo_uuid=processo_uuid
    )
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_max_out, processo_uuid=processo_uuid
    )
    url = reverse("eliminados-list")
    resp = api_client.get(
        url,
        {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "classificacao_max": "10",
            "classificacao_min": "0",
        },
    )
    assert resp.status_code == 200
    assert len(resp.data["geral"]) == 1
    assert len(resp.data["nna"]) == 1
    assert len(resp.data["pcd"]) == 1
    resp2 = api_client.get(
        url,
        {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "classificacao_max": "4",
            "classificacao_min": "0",
        },
    )
    assert resp2.status_code == 200
    assert len(resp2.data["geral"]) == 0
    assert len(resp2.data["nna"]) == 1
    assert len(resp2.data["pcd"]) == 1


def test_filtra_por_concurso_uuid(api_client):
    """Verifica filtro por concurso_uuid retorna apenas do concurso."""
    concurso_uuid = uuid4()
    outro_concurso_uuid = uuid4()
    processo_uuid = uuid4()
    cc_concurso = _cc(concurso_uuid, eliminado=True, classificacao=1)
    cc_outro = _cc(outro_concurso_uuid, eliminado=True, classificacao=1)
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_concurso, processo_uuid=processo_uuid
    )
    ConcursoCandidatoEliminacao.objects.create(
        concurso_candidato=cc_outro, processo_uuid=processo_uuid
    )
    url = reverse("eliminados-list")
    resp = api_client.get(
        url,
        {
            "concurso_uuid": str(concurso_uuid),
            "processo_uuid": str(processo_uuid),
            "classificacao_max": "10",
            "classificacao_min": "0",
        },
    )
    assert resp.status_code == 200
    assert len(resp.data["geral"]) == 1
    assert resp.data["geral"][0]["id"] == cc_concurso.id
