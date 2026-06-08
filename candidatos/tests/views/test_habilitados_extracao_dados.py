from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def criar_candidato(nome, cpf):
    return Candidato.objects.create(
        nome=nome,
        cpf=cpf,
        email=f"user-{uuid4().hex[:8]}@example.com",
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


def criar_concurso_candidato(lote, categoria, foi_convocado, processo_uuid):
    candidato = criar_candidato(f"C-{uuid4().hex[:6]}", uuid4().hex[:14])
    return ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote,
        codigo_inscricao=uuid4().hex[:8],
        categoria_efetiva=categoria,
        foi_convocado=foi_convocado,
        processo_uuid=processo_uuid,
    )


def test_extracao_dados_agrega_habilitados_e_convocados_por_ano(api_client):
    url = reverse("habilitados-extracao-dados")
    concurso_uuid = uuid4()
    processo_2026 = uuid4()
    processo_2025 = uuid4()

    # Dois lotes do mesmo concurso -> habilitados soma os dois
    lote1 = ConcursoCandidatosLote.objects.create(
        concurso_uuid=concurso_uuid, concurso_nome="Lote 1"
    )
    lote2 = ConcursoCandidatosLote.objects.create(
        concurso_uuid=concurso_uuid, concurso_nome="Lote 2"
    )

    # lote1: 2 GERAL (1 convocado 2026, 1 nao-convocado), 1 PCD nao-convocado
    criar_concurso_candidato(lote1, "GERAL", True, processo_2026)
    criar_concurso_candidato(lote1, "GERAL", False, None)
    criar_concurso_candidato(lote1, "PCD", False, None)

    # lote2: 1 GERAL convocado 2025, 1 NNA nao-convocado
    criar_concurso_candidato(lote2, "GERAL", True, processo_2025)
    criar_concurso_candidato(lote2, "NNA", False, None)

    # Candidato de outro concurso nao deve contar
    outro_lote = ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(), concurso_nome="Outro"
    )
    criar_concurso_candidato(outro_lote, "GERAL", True, uuid4())

    payload = {
        "concurso_uuid": str(concurso_uuid),
        "filtros": [
            {"ano": 2026, "processo_uuids": [str(processo_2026)]},
            {"ano": 2025, "processo_uuids": [str(processo_2025)]},
        ],
    }

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200, resp.content
    data = resp.json()

    # habilitados = todos os importados do concurso (5)
    assert data["habilitados"] == {
        "total": 5,
        "geral": 3,
        "pcd": 1,
        "nna": 1,
    }
    # por ano: convocados (foi_convocado=True nos processos do ano) e
    # nao-convocados = total de habilitados - convocados do ano
    assert data["2026"] == {"convocados": 1, "nao-convocados": 4}
    assert data["2025"] == {"convocados": 1, "nao-convocados": 4}


def test_extracao_dados_exige_concurso_uuid(api_client):
    url = reverse("habilitados-extracao-dados")
    resp = api_client.post(url, {"filtros": []}, format="json")
    assert resp.status_code == 400
