"""Testes unitários para candidatos/service/agendas_api_service.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from candidatos.service.agendas_api_service import AgendasApiService


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_200_retorna_json(mock_delete, settings):
    """Verifica remoção com status 200 retorna o JSON da resposta."""
    settings.AGENDAS_API_URL = "https://agendas"
    settings.AGENDAS_API_KEY = "api-key-agenda"
    settings.API_KEY_HEADER = "X-API-Key"
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b'{"excluidas": 2}'
    mock_delete.return_value.json.return_value = {"excluidas": 2}
    resultado = AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
        processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
    )
    assert resultado == {"excluidas": 2}


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_200_sem_body_retorna_dict_vazio(
    mock_delete, settings
):
    """Verifica remoção com status 200 e body vazio retorna dict vazio."""
    settings.AGENDAS_API_URL = "https://agendas"
    settings.AGENDAS_API_KEY = "api-key-agenda"
    settings.API_KEY_HEADER = "X-API-Key"
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b""
    resultado = AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
        processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
    )
    assert resultado == {}


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_envia_delete_com_url_e_params_corretos(
    mock_delete, settings
):
    """Verifica remoção envia DELETE com URL, headers e parâmetros corretos."""
    settings.AGENDAS_API_URL = "https://agendas"
    settings.AGENDAS_API_KEY = "api-key-agenda"
    settings.API_KEY_HEADER = "X-API-Key"
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b'{"excluidas": 1}'
    mock_delete.return_value.json.return_value = {"excluidas": 1}
    AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
        processo_uuid="proc-uuid",
        codigo_cargo="cargo-uuid",
        path="/api/v1/agendas/por-processo-e-cargo/",
    )
    mock_delete.assert_called_once_with(
        "https://agendas/api/v1/agendas/por-processo-e-cargo/",
        headers={"X-API-Key": "api-key-agenda"},
        params={"processo_uuid": "proc-uuid", "cargo": "cargo-uuid"},
        timeout=AgendasApiService.DEFAULT_TIMEOUT,
    )


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_nao_200_levanta_erro(mock_delete, settings):
    """Verifica remoção com status diferente de 200 propaga erro HTTP."""
    settings.AGENDAS_API_URL = "https://agendas"
    settings.AGENDAS_API_KEY = "api-key-agenda"
    settings.API_KEY_HEADER = "X-API-Key"
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
    mock_delete.return_value = mock_resp
    with pytest.raises(requests.HTTPError, match="500"):
        AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
            processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
        )


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_request_exception_propaga(mock_delete, settings):
    """Verifica falha de conexão propaga RequestException."""
    settings.AGENDAS_API_URL = "https://agendas"
    settings.AGENDAS_API_KEY = "api-key-agenda"
    settings.API_KEY_HEADER = "X-API-Key"
    mock_delete.side_effect = requests.ConnectionError("rede")
    with pytest.raises(
        requests.RequestException,
        match="Erro ao conectar com o microserviço de Agendas",
    ):
        AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
            processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
        )
