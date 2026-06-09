"""Testes unitários para o ViewSet de candidatos reclassificados (GET.

/reclassificados/).
"""
from __future__ import annotations
from typing import Any
from uuid import uuid4
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatoReclassificacao, ConcursoCandidatosLote
from candidatos.service.reclassificacao_service import aplicar_reclassificacao
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

def _criar_candidato(nome: Any, cpf: Any, email: Any=None) -> Any:
    """Executa  criar candidato.
    
    Args:
        nome: Parâmetro nome da operação.
        cpf: Parâmetro cpf da operação.
        email: Parâmetro email da operação.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    if email is None:
        email = f'user-{uuid4().hex[:8]}@example.com'
    return Candidato.objects.create(nome=nome, cpf=cpf, email=email, telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')

@pytest.fixture
def lote() -> Any:
    """Executa lote.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    return ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso Teste')

class TestReclassificadosViewSetList:
    """Testes para GET /reclassificados/ (list)."""

    def test_list_sem_concurso_uuid_retorna_400(self, api_client: Any) -> None:
        """Verifica list sem concurso uuid retorna 400.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'processo_uuid': str(uuid4())})
        assert resp.status_code == 400
        assert 'concurso_uuid' in (resp.data.get('detail') or '').lower()

    def test_list_sem_processo_uuid_retorna_400(self, api_client: Any) -> None:
        """Verifica list sem processo uuid retorna 400.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'concurso_uuid': str(uuid4())})
        assert resp.status_code == 400
        assert 'processo_uuid' in (resp.data.get('detail') or '').lower()

    def test_list_sem_params_retorna_400(self, api_client: Any) -> None:
        """Verifica list sem params retorna 400.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        url = reverse('reclassificados-list')
        resp = api_client.get(url)
        assert resp.status_code == 400

    def test_list_concurso_sem_lote_retorna_listas_vazias(self, api_client: Any) -> None:
        """Verifica list concurso sem lote retorna listas vazias.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'concurso_uuid': str(uuid4()), 'processo_uuid': str(uuid4())})
        assert resp.status_code == 200
        assert resp.data['nna'] == []
        assert resp.data['pcd'] == []

    def test_list_com_reclassificados_nna_e_pcd_retorna_agrupados(self, api_client: Any, lote: Any) -> None:
        """Verifica list com reclassificados nna e pcd retorna agrupados.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
            lote: Parâmetro lote da operação.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        processo_uuid = uuid4()
        c_nna = _criar_candidato('NNA Reclass', '111.111.111-11')
        cc_nna = ConcursoCandidato.objects.create(candidato=c_nna, lote=lote, codigo_inscricao='001', classificacao=5, classificacao_nna=1, classificacao_pcd=None, categoria_efetiva='GERAL', eliminado=False)
        aplicar_reclassificacao(candidato_uuid=str(cc_nna.uuid), desclassificar_de='NNA', motivo='', executado_por='')
        ConcursoCandidatoReclassificacao.objects.filter(concurso_candidato=cc_nna).update(processo_uuid=processo_uuid)
        c_pcd = _criar_candidato('PCD Reclass', '222.222.222-22')
        cc_pcd = ConcursoCandidato.objects.create(candidato=c_pcd, lote=lote, codigo_inscricao='002', classificacao=10, classificacao_nna=None, classificacao_pcd=1, categoria_efetiva='GERAL', eliminado=False)
        aplicar_reclassificacao(candidato_uuid=str(cc_pcd.uuid), desclassificar_de='PCD', motivo='', executado_por='')
        ConcursoCandidatoReclassificacao.objects.filter(concurso_candidato=cc_pcd).update(processo_uuid=processo_uuid)
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'concurso_uuid': str(lote.concurso_uuid), 'processo_uuid': str(processo_uuid)})
        assert resp.status_code == 200
        assert 'nna' in resp.data
        assert 'pcd' in resp.data
        assert len(resp.data['nna']) == 1
        assert len(resp.data['pcd']) == 1
        assert resp.data['nna'][0]['candidato']['nome'] == 'NNA Reclass'
        assert resp.data['pcd'][0]['candidato']['nome'] == 'PCD Reclass'

    def test_list_nao_retorna_eliminados(self, api_client: Any, lote: Any) -> None:
        """Verifica list nao retorna eliminados.
        
        Args:
            self: Instância do objeto.
            api_client: Cliente de API para requisições de teste.
            lote: Parâmetro lote da operação.
        
        Returns:
            Não retorna valor.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        processo_uuid = uuid4()
        c = _criar_candidato('Eliminado', '333.333.333-33')
        cc = ConcursoCandidato.objects.create(candidato=c, lote=lote, codigo_inscricao='003', classificacao=1, classificacao_nna=1, classificacao_pcd=None, categoria_efetiva='GERAL', eliminado=True)
        ConcursoCandidatoReclassificacao.objects.create(concurso_candidato=cc, desclassificado_de='NNA', processo_uuid=processo_uuid)
        url = reverse('reclassificados-list')
        resp = api_client.get(url, {'concurso_uuid': str(lote.concurso_uuid), 'processo_uuid': str(processo_uuid)})
        assert resp.status_code == 200
        assert len(resp.data['nna']) == 0
        assert len(resp.data['pcd']) == 0
