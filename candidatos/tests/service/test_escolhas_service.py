import pytest
import requests as _requests
from unittest.mock import patch, Mock, MagicMock
from candidatos.service.escolhas_service import EscolhasService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(status_code=200, json_data=None):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data if json_data is not None else []
    resp.text = str(json_data)
    resp.raise_for_status = Mock()
    return resp


# ---------------------------------------------------------------------------
# _get_base_url
# ---------------------------------------------------------------------------

def test_get_base_url_retorna_url_sem_barra_final(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas-service/'
    assert EscolhasService._get_base_url() == 'http://escolhas-service'


def test_get_base_url_sem_configuracao_levanta_erro(settings):
    settings.ESCOLHAS_API_URL = None
    with pytest.raises(ValueError, match='ESCOLHAS_API_URL'):
        EscolhasService._get_base_url()


def test_get_base_url_string_vazia_levanta_erro(settings):
    settings.ESCOLHAS_API_URL = ''
    with pytest.raises(ValueError, match='ESCOLHAS_API_URL'):
        EscolhasService._get_base_url()


# ---------------------------------------------------------------------------
# buscar_reconvocacoes – resposta lista
# ---------------------------------------------------------------------------

def test_buscar_reconvocacoes_retorna_lista(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    payload = [{'uuid': 'u1', 'candidato_uuid': 'c1'}, {'uuid': 'u2', 'candidato_uuid': 'c2'}]

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_reconvocacoes()

    assert result == payload


def test_buscar_reconvocacoes_resposta_dict_com_results(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    items = [{'uuid': 'u1'}]
    payload = {'count': 1, 'results': items}

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_reconvocacoes()

    assert result == items


def test_buscar_reconvocacoes_resposta_dict_sem_results(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    payload = {'uuid': 'u1', 'candidato_uuid': 'c1'}

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_reconvocacoes()

    assert result == [payload]


def test_buscar_reconvocacoes_resposta_vazia(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])):
        result = EscolhasService.buscar_reconvocacoes()

    assert result == []


# ---------------------------------------------------------------------------
# buscar_reconvocacoes – erros HTTP
# ---------------------------------------------------------------------------

def test_buscar_reconvocacoes_erro_http_levanta_excecao(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    mock_resp = _mock_response(500)
    mock_resp.raise_for_status.side_effect = _requests.HTTPError('500 Server Error')

    with patch('candidatos.service.escolhas_service.requests.get', return_value=mock_resp):
        with pytest.raises(_requests.RequestException):
            EscolhasService.buscar_reconvocacoes()


def test_buscar_reconvocacoes_connection_error_levanta_request_exception(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', side_effect=_requests.ConnectionError('timeout')):
        with pytest.raises(_requests.RequestException, match='Erro ao conectar'):
            EscolhasService.buscar_reconvocacoes()


def test_buscar_reconvocacoes_timeout_levanta_request_exception(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', side_effect=_requests.Timeout('timed out')):
        with pytest.raises(_requests.RequestException):
            EscolhasService.buscar_reconvocacoes()


# ---------------------------------------------------------------------------
# buscar_reconvocacoes – path customizado
# ---------------------------------------------------------------------------

def test_buscar_reconvocacoes_usa_path_customizado(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_reconvocacoes(path='/api/v2/reconvocacao/')

    called_url = mock_get.call_args[0][0]
    assert '/api/v2/reconvocacao/' in called_url


# ---------------------------------------------------------------------------
# buscar_escolhas – resposta lista
# ---------------------------------------------------------------------------

def test_buscar_escolhas_retorna_lista(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    payload = [{'uuid': 'e1', 'candidato_uuid': 'c1', 'situacao': 'escolha'}]

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_escolhas(concurso_uuid='conc-uuid-1')

    assert result == payload


def test_buscar_escolhas_resposta_dict_com_results(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    items = [{'uuid': 'e1'}]
    payload = {'count': 1, 'results': items}

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_escolhas(concurso_uuid='conc-uuid-1')

    assert result == items


def test_buscar_escolhas_resposta_dict_sem_results(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    payload = {'uuid': 'e1', 'situacao': 'escolha'}

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, payload)):
        result = EscolhasService.buscar_escolhas(concurso_uuid='conc-uuid-1')

    assert result == [payload]


def test_buscar_escolhas_resposta_vazia(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])):
        result = EscolhasService.buscar_escolhas(concurso_uuid='conc-uuid-1')

    assert result == []


# ---------------------------------------------------------------------------
# buscar_escolhas – URL inclui concurso_uuid
# ---------------------------------------------------------------------------

def test_buscar_escolhas_url_inclui_concurso_uuid(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid='meu-uuid-123')

    called_url = mock_get.call_args[0][0]
    assert 'meu-uuid-123' in called_url


def test_buscar_escolhas_url_inclui_page_size(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid='uuid-x')

    called_url = mock_get.call_args[0][0]
    assert 'page_size=10000' in called_url


# ---------------------------------------------------------------------------
# buscar_escolhas – erros HTTP
# ---------------------------------------------------------------------------

def test_buscar_escolhas_erro_http_levanta_excecao(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'
    mock_resp = _mock_response(404)
    mock_resp.raise_for_status.side_effect = _requests.HTTPError('404 Not Found')

    with patch('candidatos.service.escolhas_service.requests.get', return_value=mock_resp):
        with pytest.raises(_requests.RequestException):
            EscolhasService.buscar_escolhas(concurso_uuid='uuid-x')


def test_buscar_escolhas_connection_error_levanta_request_exception(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', side_effect=_requests.ConnectionError('refused')):
        with pytest.raises(_requests.RequestException, match='Erro ao buscar escolhas'):
            EscolhasService.buscar_escolhas(concurso_uuid='uuid-x')


def test_buscar_escolhas_timeout_levanta_request_exception(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', side_effect=_requests.Timeout('timed out')):
        with pytest.raises(_requests.RequestException):
            EscolhasService.buscar_escolhas(concurso_uuid='uuid-x')


# ---------------------------------------------------------------------------
# buscar_escolhas – path customizado
# ---------------------------------------------------------------------------

def test_buscar_escolhas_usa_path_customizado(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid='uuid-x', path='/api/v2/escolhas/?situacao=escolha')

    called_url = mock_get.call_args[0][0]
    assert '/api/v2/escolhas/' in called_url


# ---------------------------------------------------------------------------
# Timeout padrão é utilizado
# ---------------------------------------------------------------------------

def test_buscar_reconvocacoes_usa_timeout_padrao(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_reconvocacoes()

    _, kwargs = mock_get.call_args
    assert kwargs.get('timeout') == EscolhasService.DEFAULT_TIMEOUT


def test_buscar_escolhas_usa_timeout_padrao(settings):
    settings.ESCOLHAS_API_URL = 'http://escolhas'

    with patch('candidatos.service.escolhas_service.requests.get', return_value=_mock_response(200, [])) as mock_get:
        EscolhasService.buscar_escolhas(concurso_uuid='uuid-x')

    _, kwargs = mock_get.call_args
    assert kwargs.get('timeout') == EscolhasService.DEFAULT_TIMEOUT
