"""Testes unitários para candidatos/service/agendas_api_service.py."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from candidatos.service.agendas_api_service import AgendasApiService


def test_get_base_url_levanta_quando_nao_configurado():
    """Verifica get base url levanta quando nao configurado."""
    with patch(
        "candidatos.service.agendas_api_service.settings"
    ) as mock_settings:
        mock_settings.AGENDAS_API_URL = None
        with pytest.raises(ValueError, match="AGENDAS_API_URL"):
            AgendasApiService._get_base_url()


def test_get_base_url_retorna_url_sem_barra_final():
    """Verifica get base url retorna url sem barra final."""
    with patch(
        "candidatos.service.agendas_api_service.settings"
    ) as mock_settings:
        mock_settings.AGENDAS_API_URL = "https://agendas.example.com/"
        assert (
            AgendasApiService._get_base_url() == "https://agendas.example.com"
        )


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_200_retorna_json(mock_delete):
    """Verifica remoção com status 200 retorna o JSON da resposta."""
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b'{"excluidas": 2}'
    mock_delete.return_value.json.return_value = {"excluidas": 2}
    with patch.object(
        AgendasApiService, "_get_base_url", return_value="https://agendas"
    ):
        resultado = (
            AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
                processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
            )
        )
    assert resultado == {"excluidas": 2}


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_200_sem_body_retorna_dict_vazio(mock_delete):
    """Verifica remoção com status 200 e body vazio retorna dict vazio."""
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b""
    with patch.object(
        AgendasApiService, "_get_base_url", return_value="https://agendas"
    ):
        resultado = (
            AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
                processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
            )
        )
    assert resultado == {}


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_envia_delete_com_url_e_params_corretos(mock_delete):
    """Verifica remoção envia DELETE com URL e parâmetros corretos."""
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.content = b'{"excluidas": 1}'
    mock_delete.return_value.json.return_value = {"excluidas": 1}
    with patch.object(
        AgendasApiService, "_get_base_url", return_value="https://agendas"
    ):
        AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
            processo_uuid="proc-uuid",
            codigo_cargo="cargo-uuid",
            path="/api/v1/agendas/por-processo-e-cargo/",
        )
    mock_delete.assert_called_once_with(
        "https://agendas/api/v1/agendas/por-processo-e-cargo/",
        params={"processo_uuid": "proc-uuid", "cargo": "cargo-uuid"},
        timeout=AgendasApiService.DEFAULT_TIMEOUT,
    )


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_nao_200_levanta_erro(mock_delete):
    """Verifica remoção com status diferente de 200 propaga erro HTTP."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"
    mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
    mock_delete.return_value = mock_resp
    with (
        patch.object(
            AgendasApiService, "_get_base_url", return_value="https://agendas"
        ),
        pytest.raises(requests.HTTPError, match="500"),
    ):
        AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
            processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
        )


@patch("candidatos.service.agendas_api_service.http_client.delete")
def test_remover_agendas_request_exception_propaga(mock_delete):
    """Verifica falha de conexão propaga RequestException."""
    mock_delete.side_effect = requests.ConnectionError("rede")
    with (
        patch.object(
            AgendasApiService, "_get_base_url", return_value="https://agendas"
        ),
        pytest.raises(
            requests.RequestException,
            match="Erro ao conectar com o microserviço de Agendas",
        ),
    ):
        AgendasApiService.remover_agendas_por_processo_uuid_e_cargo(
            processo_uuid="proc-uuid", codigo_cargo="cargo-uuid"
        )
