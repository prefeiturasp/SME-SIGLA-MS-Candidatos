"""Testes unitários para candidatos/service/escolhas_service.py.

Cobre _get_base_url, buscar_reconvocacoes, buscar_escolhas (com mock de
requests).
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from candidatos.service.escolhas_service import EscolhasService


def test_get_base_url_levanta_quando_nao_configurado() -> None:
    """Verifica get base url levanta quando nao configurado."""
    with patch(
        "candidatos.service.escolhas_service.settings"
    ) as mock_settings:
        mock_settings.ESCOLHAS_API_URL = None
        with pytest.raises(ValueError, match="ESCOLHAS_API_URL"):
            EscolhasService._get_base_url()


def test_get_base_url_retorna_url_sem_barra_final() -> None:
    """Verifica get base url retorna url sem barra final."""
    with patch(
        "candidatos.service.escolhas_service.settings"
    ) as mock_settings:
        mock_settings.ESCOLHAS_API_URL = "https://escolhas.example.com/"
        assert (
            EscolhasService._get_base_url() == "https://escolhas.example.com"
        )


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_200_retorna_lista_direta(mock_get: Any) -> None:
    """Verifica buscar reconvocacoes 200 retorna lista direta."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"uuid": "a", "candidato_uuid": "b"}
    ]
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"uuid": "a", "candidato_uuid": "b"}]


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_200_dict_com_results(mock_get: Any) -> None:
    """Verifica buscar reconvocacoes 200 dict com results."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": [{"candidato_uuid": "x"}]
    }
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"candidato_uuid": "x"}]


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_200_dict_sem_results_retorna_lista_unitária(
    mock_get: Any,
) -> None:
    """Verifica buscar reconvocacoes 200 dict sem results retorna lista."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "uuid": "um",
        "candidato_uuid": "c1",
    }
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [{"uuid": "um", "candidato_uuid": "c1"}]


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_200_outro_formato_retorna_lista_vazia(
    mock_get: Any,
) -> None:
    """Verifica buscar reconvocacoes 200 outro formato retorna lista vazia."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = "não é list nem dict"
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == []


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_nao_200_levanta_request_exception(
    mock_get: Any,
) -> None:
    """Verifica buscar reconvocacoes nao 200 levanta request exception."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"
    mock_resp.json.side_effect = Exception("not json")
    mock_resp.raise_for_status.side_effect = Exception("404")
    mock_get.return_value = mock_resp
    with (
        patch.object(
            EscolhasService, "_get_base_url", return_value="https://api"
        ),
        pytest.raises(Exception, match="404"),
    ):
        EscolhasService.buscar_reconvocacoes()


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_reconvocacoes_request_exception_propaga(mock_get: Any) -> None:
    """Verifica buscar reconvocacoes request exception propaga."""
    mock_get.side_effect = ConnectionError("rede")
    with (
        patch.object(
            EscolhasService, "_get_base_url", return_value="https://api"
        ),
        pytest.raises(ConnectionError, match="rede"),
    ):
        EscolhasService.buscar_reconvocacoes()


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_escolhas_200_retorna_lista_direta(mock_get: Any) -> None:
    """Verifica buscar escolhas 200 retorna lista direta."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"candidato_uuid": "e1"}]
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="concurso-123")
    assert result == [{"candidato_uuid": "e1"}]
    call_url = mock_get.call_args[0][0]
    assert "concurso_uuid=concurso-123" in call_url


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_escolhas_200_dict_com_results(mock_get: Any) -> None:
    """Verifica buscar escolhas 200 dict com results."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": [{"candidato_uuid": "e2"}]
    }
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="uu")
    assert result == [{"candidato_uuid": "e2"}]


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_escolhas_200_dict_sem_results_retorna_lista_unitária(
    mock_get: Any,
) -> None:
    """Verifica buscar escolhas 200 dict sem results retorna lista unitária."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"candidato_uuid": "e3"}
    with patch.object(
        EscolhasService, "_get_base_url", return_value="https://api"
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="uu")
    assert result == [{"candidato_uuid": "e3"}]


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_escolhas_nao_200_levanta(mock_get: Any) -> None:
    """Verifica buscar escolhas nao 200 levanta."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Error"
    mock_resp.raise_for_status.side_effect = Exception("500")
    mock_get.return_value = mock_resp
    with (
        patch.object(
            EscolhasService, "_get_base_url", return_value="https://api"
        ),
        pytest.raises(Exception),
    ):
        EscolhasService.buscar_escolhas(concurso_uuid="uu")


@patch("candidatos.service.escolhas_service.http_client.get")
def test_buscar_escolhas_request_exception_propaga(mock_get: Any) -> None:
    """Verifica buscar escolhas request exception propaga."""
    mock_get.side_effect = TimeoutError("timeout")
    with (
        patch.object(
            EscolhasService, "_get_base_url", return_value="https://api"
        ),
        pytest.raises(TimeoutError),
    ):
        EscolhasService.buscar_escolhas(concurso_uuid="uu")


from unittest.mock import Mock, patch

import requests as _requests


def _mock_response(status_code: Any = 200, json_data: Any = None) -> Any:
    """Resposta simulada da API externa."""
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else []
    resp.text = str(json_data)
    resp.raise_for_status = Mock()
    return resp


def test_get_base_url_retorna_url_sem_barra_final(settings: Any) -> None:  # type: ignore[no-redef]
    """Verifica get base url retorna url sem barra final."""
    settings.ESCOLHAS_API_URL = "http://escolhas-service/"
    assert EscolhasService._get_base_url() == "http://escolhas-service"


def test_get_base_url_sem_configuracao_levanta_erro(settings: Any) -> None:
    """Verifica get base url sem configuracao levanta erro."""
    settings.ESCOLHAS_API_URL = None
    with pytest.raises(ValueError, match="ESCOLHAS_API_URL"):
        EscolhasService._get_base_url()


def test_get_base_url_string_vazia_levanta_erro(settings: Any) -> None:
    """Verifica get base url string vazia levanta erro."""
    settings.ESCOLHAS_API_URL = ""
    with pytest.raises(ValueError, match="ESCOLHAS_API_URL"):
        EscolhasService._get_base_url()


def test_buscar_reconvocacoes_retorna_lista(settings: Any) -> None:
    """Verifica buscar reconvocacoes retorna lista."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    payload = [
        {"uuid": "u1", "candidato_uuid": "c1"},
        {"uuid": "u2", "candidato_uuid": "c2"},
    ]
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == payload


def test_buscar_reconvocacoes_resposta_dict_com_results(settings: Any) -> None:
    """Verifica buscar reconvocacoes resposta dict com results."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    items = [{"uuid": "u1"}]
    payload = {"count": 1, "results": items}
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == items


def test_buscar_reconvocacoes_resposta_dict_sem_results(settings: Any) -> None:
    """Verifica buscar reconvocacoes resposta dict sem results."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    payload = {"uuid": "u1", "candidato_uuid": "c1"}
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == [payload]


def test_buscar_reconvocacoes_resposta_vazia(settings: Any) -> None:
    """Verifica buscar reconvocacoes resposta vazia."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ):
        result = EscolhasService.buscar_reconvocacoes()
    assert result == []


def test_buscar_reconvocacoes_erro_http_levanta_excecao(settings: Any) -> None:
    """Verifica buscar reconvocacoes erro http levanta excecao."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    mock_resp = _mock_response(500)
    mock_resp.raise_for_status.side_effect = _requests.HTTPError(
        "500 Server Error"
    )
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            return_value=mock_resp,
        ),
        pytest.raises(_requests.RequestException),
    ):
        EscolhasService.buscar_reconvocacoes()


def test_buscar_reconvocacoes_connection_error_levanta_request_exception(
    settings: Any,
) -> None:
    """Verifica buscar reconvocacoes connection error levanta request."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            side_effect=_requests.ConnectionError("timeout"),
        ),
        pytest.raises(_requests.RequestException, match="Erro ao conectar"),
    ):
        EscolhasService.buscar_reconvocacoes()


def test_buscar_reconvocacoes_timeout_levanta_request_exception(
    settings: Any,
) -> None:
    """Verifica buscar reconvocacoes timeout levanta request exception."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            side_effect=_requests.Timeout("timed out"),
        ),
        pytest.raises(_requests.RequestException),
    ):
        EscolhasService.buscar_reconvocacoes()


def test_buscar_reconvocacoes_usa_path_customizado(settings: Any) -> None:
    """Verifica buscar reconvocacoes usa path customizado."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_reconvocacoes(path="/api/v2/reconvocacao/")
    called_url = mock_get.call_args[0][0]
    assert "/api/v2/reconvocacao/" in called_url


def test_buscar_escolhas_retorna_lista(settings: Any) -> None:
    """Verifica buscar escolhas retorna lista."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    payload = [{"uuid": "e1", "candidato_uuid": "c1", "situacao": "escolha"}]
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="conc-uuid-1")
    assert result == payload


def test_buscar_escolhas_resposta_dict_com_results(settings: Any) -> None:
    """Verifica buscar escolhas resposta dict com results."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    items = [{"uuid": "e1"}]
    payload = {"count": 1, "results": items}
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="conc-uuid-1")
    assert result == items


def test_buscar_escolhas_resposta_dict_sem_results(settings: Any) -> None:
    """Verifica buscar escolhas resposta dict sem results."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    payload = {"uuid": "e1", "situacao": "escolha"}
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, payload),
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="conc-uuid-1")
    assert result == [payload]


def test_buscar_escolhas_resposta_vazia(settings: Any) -> None:
    """Verifica buscar escolhas resposta vazia."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ):
        result = EscolhasService.buscar_escolhas(concurso_uuid="conc-uuid-1")
    assert result == []


def test_buscar_escolhas_url_inclui_concurso_uuid(settings: Any) -> None:
    """Verifica buscar escolhas url inclui concurso uuid."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid="meu-uuid-123")
    called_url = mock_get.call_args[0][0]
    assert "meu-uuid-123" in called_url


def test_buscar_escolhas_url_inclui_page_size(settings: Any) -> None:
    """Verifica buscar escolhas url inclui page size."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid="uuid-x")
    called_url = mock_get.call_args[0][0]
    assert "page_size=10000" in called_url


def test_buscar_escolhas_erro_http_levanta_excecao(settings: Any) -> None:
    """Verifica buscar escolhas erro http levanta excecao."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    mock_resp = _mock_response(404)
    mock_resp.raise_for_status.side_effect = _requests.HTTPError(
        "404 Not Found"
    )
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            return_value=mock_resp,
        ),
        pytest.raises(_requests.RequestException),
    ):
        EscolhasService.buscar_escolhas(concurso_uuid="uuid-x")


def test_buscar_escolhas_connection_error_levanta_request_exception(
    settings: Any,
) -> None:
    """Verifica buscar escolhas connection error levanta request exception."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            side_effect=_requests.ConnectionError("refused"),
        ),
        pytest.raises(
            _requests.RequestException, match="Erro ao buscar escolhas"
        ),
    ):
        EscolhasService.buscar_escolhas(concurso_uuid="uuid-x")


def test_buscar_escolhas_timeout_levanta_request_exception(
    settings: Any,
) -> None:
    """Verifica buscar escolhas timeout levanta request exception."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with (
        patch(
            "candidatos.service.escolhas_service.http_client.get",
            side_effect=_requests.Timeout("timed out"),
        ),
        pytest.raises(_requests.RequestException),
    ):
        EscolhasService.buscar_escolhas(concurso_uuid="uuid-x")


def test_buscar_escolhas_usa_path_customizado(settings: Any) -> None:
    """Verifica buscar escolhas usa path customizado."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_escolhas(
            concurso_uuid="uuid-x", path="/api/v2/escolhas/?situacao=escolha"
        )
    called_url = mock_get.call_args[0][0]
    assert "/api/v2/escolhas/" in called_url


def test_buscar_reconvocacoes_usa_timeout_padrao(settings: Any) -> None:
    """Verifica buscar reconvocacoes usa timeout padrao."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_reconvocacoes()
    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") == EscolhasService.DEFAULT_TIMEOUT


def test_buscar_escolhas_usa_timeout_padrao(settings: Any) -> None:
    """Verifica buscar escolhas usa timeout padrao."""
    settings.ESCOLHAS_API_URL = "http://escolhas"
    with patch(
        "candidatos.service.escolhas_service.http_client.get",
        return_value=_mock_response(200, []),
    ) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid="uuid-x")
    _, kwargs = mock_get.call_args
    assert kwargs.get("timeout") == EscolhasService.DEFAULT_TIMEOUT
