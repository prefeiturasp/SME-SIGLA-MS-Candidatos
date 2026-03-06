"""
Testes unitários para candidatos/service/escolhas_service.py.
Cobre _get_base_url, buscar_reconvocacoes, buscar_escolhas (com mock de requests).
"""
import pytest
from unittest.mock import patch, MagicMock

from candidatos.service.escolhas_service import EscolhasService


# --- _get_base_url (linhas 21-24) ---


def test_get_base_url_levanta_quando_nao_configurado():
    with patch("candidatos.service.escolhas_service.settings") as mock_settings:
        mock_settings.ESCOLHAS_API_URL = None
        with pytest.raises(ValueError, match="ESCOLHAS_API_URL"):
            EscolhasService._get_base_url()


def test_get_base_url_retorna_url_sem_barra_final():
    with patch("candidatos.service.escolhas_service.settings") as mock_settings:
        mock_settings.ESCOLHAS_API_URL = "https://escolhas.example.com/"
        assert EscolhasService._get_base_url() == "https://escolhas.example.com"


# --- buscar_reconvocacoes (linhas 38-62) ---


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_200_retorna_lista_direta(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"uuid": "a", "candidato_uuid": "b"}]
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"uuid": "a", "candidato_uuid": "b"}]


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_200_dict_com_results(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": [{"candidato_uuid": "x"}]}
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"candidato_uuid": "x"}]


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_200_dict_sem_results_retorna_lista_unitária(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"uuid": "um", "candidato_uuid": "c1"}
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"uuid": "um", "candidato_uuid": "c1"}]


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_200_outro_formato_retorna_lista_vazia(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = "não é list nem dict"
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == []


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_nao_200_levanta_request_exception(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"
    mock_resp.json.side_effect = Exception("not json")
    mock_resp.raise_for_status.side_effect = Exception("404")
    mock_get.return_value = mock_resp
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        with pytest.raises(Exception, match="404"):
            EscolhasService.buscar_reconvocacoes()


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_reconvocacoes_request_exception_propaga(mock_get):
    mock_get.side_effect = ConnectionError("rede")
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        with pytest.raises(ConnectionError, match="rede"):
            EscolhasService.buscar_reconvocacoes()


# --- buscar_escolhas (linhas 78-102) ---


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_escolhas_200_retorna_lista_direta(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"candidato_uuid": "e1"}]
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_escolhas(concurso_uuid="concurso-123")
    assert result == [{"candidato_uuid": "e1"}]
    call_url = mock_get.call_args[0][0]
    assert "concurso_uuid=concurso-123" in call_url


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_escolhas_200_dict_com_results(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": [{"candidato_uuid": "e2"}]}
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_escolhas(concurso_uuid="uu")
    assert result == [{"candidato_uuid": "e2"}]


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_escolhas_200_dict_sem_results_retorna_lista_unitária(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"candidato_uuid": "e3"}
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        result = EscolhasService.buscar_escolhas(concurso_uuid="uu")
    assert result == [{"candidato_uuid": "e3"}]


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_escolhas_nao_200_levanta(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Error"
    mock_resp.raise_for_status.side_effect = Exception("500")
    mock_get.return_value = mock_resp
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        with pytest.raises(Exception):
            EscolhasService.buscar_escolhas(concurso_uuid="uu")


@patch("candidatos.service.escolhas_service.requests.get")
def test_buscar_escolhas_request_exception_propaga(mock_get):
    mock_get.side_effect = TimeoutError("timeout")
    with patch.object(EscolhasService, "_get_base_url", return_value="https://api"):
        with pytest.raises(TimeoutError):
            EscolhasService.buscar_escolhas(concurso_uuid="uu")
