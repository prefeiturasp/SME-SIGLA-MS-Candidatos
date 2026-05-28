from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def lote():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(), concurso_nome="Concurso Teste"
    )


@pytest.fixture
def candidatos_no_lote(lote):
    cand1 = Candidato.objects.create(
        nome="Fulano", cpf="11111111111", email="john_wick@email.com"
    )
    cand2 = Candidato.objects.create(
        nome="Beltrano", cpf="22222222222", email="jardani@email.com"
    )
    cc1 = ConcursoCandidato.objects.create(
        lote=lote,
        candidato=cand1,
        codigo_inscricao="A1",
        descricao_cargo="Cargo X",
    )
    cc2 = ConcursoCandidato.objects.create(
        lote=lote,
        candidato=cand2,
        codigo_inscricao="A2",
        descricao_cargo="Cargo X",
    )
    return cc1, cc2


def test_convocar_sucesso(client, lote, candidatos_no_lote):
    url = reverse("habilitados-convocar")
    cc1, cc2 = candidatos_no_lote
    payload = {
        "concurso_uuid": str(lote.concurso_uuid),
        "candidatos": [str(cc1.uuid), str(cc2.uuid)],
    }
    resp = client.patch(url, payload, format="json")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data.get("total") == 2

    cc1.refresh_from_db()
    cc2.refresh_from_db()
    assert cc1.foi_convocado is True and cc2.foi_convocado is True
    assert cc1.data_convocacao is not None and cc2.data_convocacao is not None


def test_convocar_lote_inexistente(client):
    url = reverse("habilitados-convocar")
    payload = {"concurso_uuid": str(uuid4()), "candidatos": []}
    resp = client.patch(url, payload, format="json")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_convocar_payload_invalido(client):
    url = reverse("habilitados-convocar")
    resp = client.patch(url, {}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
