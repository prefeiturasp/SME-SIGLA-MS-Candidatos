"""Testes mínimos para EliminadosViewSet.list (GET /eliminados/)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatoEliminacao, ConcursoCandidatosLote
pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client() -> Any:
    """Executa api client.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return APIClient()

def _candidato(**kwargs: Any) -> Any:
    """Executa  candidato.
    
    Args:
        **kwargs: Argumentos nomeados variáveis.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return Candidato.objects.create(nome=kwargs.get('nome', 'Teste'), cpf=kwargs.get('cpf', f'{uuid4().int % 10 ** 11:011d}'), email=kwargs.get('email', f'{uuid4().hex[:8]}@example.com'), telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')

def _cc(lote: Any, candidato: Any=None, **kwargs: Any) -> Any:
    """Executa  cc.
    
    Args:
        lote: Parâmetro lote da operação.
        candidato: Parâmetro candidato da operação.
        **kwargs: Argumentos nomeados variáveis.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return ConcursoCandidato.objects.create(candidato=candidato or _candidato(), lote=lote, codigo_inscricao=kwargs.get('codigo_inscricao', uuid4().hex[:8]), eliminado=kwargs.get('eliminado', True), classificacao=kwargs.get('classificacao'), classificacao_nna=kwargs.get('classificacao_nna'), classificacao_pcd=kwargs.get('classificacao_pcd'))

def test_parametros_obrigatorios(api_client: Any) -> None:
    """Verifica parametros obrigatorios.
    
    Args:
        api_client: Cliente de API para requisições de teste.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse('eliminados-list')
    assert api_client.get(url).status_code == 400
    assert api_client.get(url, {'concurso_uuid': str(uuid4())}).status_code == 400
    assert api_client.get(url, {'concurso_uuid': str(uuid4()), 'processo_uuid': str(uuid4()), 'classificacao_max': '10'}).status_code == 400

def test_sem_lote_retorna_listas_vazias(api_client: Any) -> None:
    """Verifica sem lote retorna listas vazias.
    
    Args:
        api_client: Cliente de API para requisições de teste.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    url = reverse('eliminados-list')
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    resp = api_client.get(url, {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'classificacao_max': '10', 'classificacao_min': '0'})
    assert resp.status_code == 200
    assert resp.data == {'geral': [], 'nna': [], 'pcd': []}

def test_retorna_eliminados_separados_e_filtra_classificacao(api_client: Any) -> None:
    """Verifica retorna eliminados separados e filtra classificacao.
    
    Args:
        api_client: Cliente de API para requisições de teste.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='X')
    cc_geral = _cc(lote, eliminado=True, classificacao=5, classificacao_nna=None, classificacao_pcd=None)
    cc_nna = _cc(lote, eliminado=True, classificacao=3, classificacao_nna=1, classificacao_pcd=None)
    cc_pcd = _cc(lote, eliminado=True, classificacao=2, classificacao_nna=None, classificacao_pcd=1)
    cc_max_out = _cc(lote, eliminado=True, classificacao=15, classificacao_nna=None, classificacao_pcd=None)
    _cc(lote, eliminado=False, classificacao=1, classificacao_nna=None, classificacao_pcd=None)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_geral, processo_uuid=processo_uuid)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_nna, processo_uuid=processo_uuid)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_pcd, processo_uuid=processo_uuid)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_max_out, processo_uuid=processo_uuid)
    url = reverse('eliminados-list')
    resp = api_client.get(url, {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'classificacao_max': '10', 'classificacao_min': '0'})
    assert resp.status_code == 200
    assert len(resp.data['geral']) == 1
    assert len(resp.data['nna']) == 1
    assert len(resp.data['pcd']) == 1
    resp2 = api_client.get(url, {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'classificacao_max': '4', 'classificacao_min': '0'})
    assert resp2.status_code == 200
    assert len(resp2.data['geral']) == 0
    assert len(resp2.data['nna']) == 1
    assert len(resp2.data['pcd']) == 1

def test_usa_ultimo_lote(api_client: Any) -> None:
    """Verifica usa ultimo lote.
    
    Args:
        api_client: Cliente de API para requisições de teste.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concurso_uuid = uuid4()
    processo_uuid = uuid4()
    lote_antigo = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='A')
    lote_novo = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='B')
    cc_antigo = _cc(lote_antigo, eliminado=True, classificacao=1)
    cc_novo = _cc(lote_novo, eliminado=True, classificacao=1)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_antigo, processo_uuid=processo_uuid)
    ConcursoCandidatoEliminacao.objects.create(concurso_candidato=cc_novo, processo_uuid=processo_uuid)
    url = reverse('eliminados-list')
    resp = api_client.get(url, {'concurso_uuid': str(concurso_uuid), 'processo_uuid': str(processo_uuid), 'classificacao_max': '10', 'classificacao_min': '0'})
    assert resp.status_code == 200
    assert len(resp.data['geral']) == 1
    assert resp.data['geral'][0]['id'] == cc_novo.id
