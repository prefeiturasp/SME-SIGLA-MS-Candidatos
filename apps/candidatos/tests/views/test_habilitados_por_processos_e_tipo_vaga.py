"""Testes da action por-processos-e-tipo-vaga."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from candidatos.api.views.habilitados import HabilitadosViewSet
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

SERVICE = (
    "candidatos.api.views.habilitados."
    "HabilitadosPorProcessoService.montar_por_processos_e_tipo_vaga"
)


def _post(payload: dict):
    factory = APIRequestFactory()
    request = factory.post(
        reverse("habilitados-por-processos-e-tipo-vaga"),
        payload,
        format="json",
    )
    view = HabilitadosViewSet.as_view({"post": "por_processos_e_tipo_vaga"})
    return view(request)


def test_por_processos_e_tipo_vaga_sem_lista_retorna_400():
    """Body sem processo_uuids retorna 400."""
    resposta = _post({})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST
    assert "processo_uuids" in resposta.data["detail"]

    resposta = _post({"processo_uuids": "nao-lista"})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST


def test_por_processos_e_tipo_vaga_lista_vazia_retorna_400():
    """Lista vazia de processo_uuids retorna 400."""
    resposta = _post({"processo_uuids": []})
    assert resposta.status_code == status.HTTP_400_BAD_REQUEST


@patch(SERVICE)
def test_por_processos_e_tipo_vaga_sucesso(mock_montar):
    """Retorna o resultado montado pelo service."""
    pid = str(uuid.uuid4())
    esperado = {
        pid: {
            "GERAL": {"total": 1, "candidatos_uuids": ["a"]},
            "NNA": {"total": 0, "candidatos_uuids": []},
            "PCD": {"total": 0, "candidatos_uuids": []},
        }
    }
    mock_montar.return_value = esperado

    resposta = _post({"processo_uuids": [pid]})

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.data == esperado
    mock_montar.assert_called_once_with([pid])
