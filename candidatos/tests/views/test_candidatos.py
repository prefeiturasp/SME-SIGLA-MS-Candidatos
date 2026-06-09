"""Módulo tests/views/test_candidatos."""
from __future__ import annotations
from typing import Any
from uuid import uuid4
import pytest
from django.urls import reverse
from rest_framework import status
from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote
pytestmark = pytest.mark.django_db

@pytest.fixture
def candidato_url() -> Any:
    """Executa candidato url."""
    return reverse('candidato-list')

@pytest.fixture
def buscar_url() -> Any:
    """Executa buscar url."""
    return reverse('candidato-buscar')

def test_list_candidatos(api_client: Any, candidatos_criados: Any, candidato_url: Any) -> None:
    """Verifica list candidatos."""
    response = api_client.get(candidato_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

def test_create_candidatos_em_lote(api_client: Any, candidato_url: Any) -> None:
    """Verifica create candidatos em lote."""
    payload = {'concurso_uuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'concurso_nome': 'Concurso X', 'candidatos': [{'nome': 'Ana Costa', 'cpf': '555.666.777-88', 'email': 'ana.costa@email.com', 'telefone': '(11) 66666-6666', 'data_nascimento': '25/08/1988', 'genero': 'F', 'endereco': 'Rua Augusta, 321', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01305-000', 'status': 'ativo', 'observacao': 'Nova candidata', 'codigo_inscricao': '12345', 'classificacao': '10', 'pontos': '95'}]}
    response = api_client.post(candidato_url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['total_itens'] == 1
    assert ConcursoCandidatosLote.objects.count() == 1
    lote = ConcursoCandidatosLote.objects.first()
    assert ConcursoCandidato.objects.filter(lote=lote).count() == 1
    assert Candidato.objects.filter(cpf='55566677788').exists()

def test_retrieve_candidato(api_client: Any, candidatos_criados: Any) -> None:
    """Verifica retrieve candidato."""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'João Silva'

def test_update_candidato(api_client: Any, candidatos_criados: Any) -> None:
    """Verifica update candidato."""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    dados_atualizados = {'nome': 'João Silva Santos', 'cpf': '123.456.789-00', 'email': 'joao.silva.santos@email.com', 'telefone': '(11) 99999-9999', 'data_nascimento': '1990-01-15', 'genero': 'M', 'endereco': 'Rua das Flores, 123', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01234-567', 'status': 'ativo', 'observacoes': 'Candidato atualizado'}
    response = api_client.put(url, dados_atualizados, format='json')
    assert response.status_code == status.HTTP_200_OK

def test_partial_update_candidato(api_client: Any, candidatos_criados: Any) -> None:
    """Verifica partial update candidato."""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.patch(url, {'telefone': '(11) 11111-1111', 'status': 'suspenso'}, format='json')
    assert response.status_code == status.HTTP_200_OK

def test_delete_candidato(api_client: Any, candidatos_criados: Any) -> None:
    """Verifica delete candidato."""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'uuid': candidato1.uuid})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_buscar_sem_parametros_retorna_400(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar sem parametros retorna 400."""
    response = api_client.get(buscar_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'nome' in response.data['detail'] or 'parâmetro' in response.data['detail'].lower()

def test_buscar_por_nome_retorna_candidatos(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar por nome retorna candidatos."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    candidato = Candidato.objects.create(nome='Fulano da Silva', cpf='11122233344', email='fulano@email.com', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote, codigo_inscricao='001')
    response = api_client.get(buscar_url, {'nome': 'Fulano'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == 'Fulano da Silva'
    assert 'concursos' in response.data[0]
    assert len(response.data[0]['concursos']) == 1

def test_buscar_por_cpf_retorna_candidatos(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar por cpf retorna candidatos."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    candidato = Candidato.objects.create(nome='Beltrano', cpf='55566677788', email='beltrano@email.com', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote, codigo_inscricao='002')
    response = api_client.get(buscar_url, {'cpf': '55566677788'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['cpf'] == '55566677788'

def test_buscar_por_rg_retorna_candidatos(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar por rg retorna candidatos."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    candidato = Candidato.objects.create(nome='Cicrano', cpf='99988877766', email='cicrano@email.com', rg='12.345.678-9', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote, codigo_inscricao='003')
    response = api_client.get(buscar_url, {'rg': '12.345.678-9'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == 'Cicrano'

def test_buscar_por_registro_funcional_retorna_candidatos(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar por registro funcional retorna candidatos."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    candidato = Candidato.objects.create(nome='Registro', cpf='12312312312', email='registro@email.com', registro_funcional='RF12345', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote, codigo_inscricao='004')
    response = api_client.get(buscar_url, {'registro_funcional': 'RF12345'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == 'Registro'

def test_buscar_agrupa_concursos_por_candidato(api_client: Any, buscar_url: Any) -> None:
    """Candidato com mais de um ConcursoCandidato deve retornar um único item.

    com lista de concursos.
    """
    concurso_uuid = uuid4()
    lote1 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Lote 1')
    lote2 = ConcursoCandidatosLote.objects.create(concurso_uuid=concurso_uuid, concurso_nome='Lote 2')
    candidato = Candidato.objects.create(nome='Multi Concurso', cpf='77777777777', email='multi@email.com', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote1, codigo_inscricao='A1')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote2, codigo_inscricao='A2')
    response = api_client.get(buscar_url, {'nome': 'Multi'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert len(response.data[0]['concursos']) == 2

def test_buscar_retorna_lista_vazia_quando_nao_encontra(api_client: Any, buscar_url: Any) -> None:
    """Verifica buscar retorna lista vazia quando nao encontra."""
    response = api_client.get(buscar_url, {'nome': 'NomeQueNaoExisteEmNenhumCandidato'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

def test_buscar_nome_icontains(api_client: Any, buscar_url: Any) -> None:
    """Busca por nome usa icontains (parte do nome)."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    candidato = Candidato.objects.create(nome='Maria Fernanda Santos', cpf='44455566677', email='maria.f@email.com', telefone='', data_nascimento='1990-01-01', genero='F', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=candidato, lote=lote, codigo_inscricao='005')
    response = api_client.get(buscar_url, {'nome': 'Fernanda'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert 'Fernanda' in response.data[0]['nome']

def test_buscar_com_multiplos_parametros(api_client: Any, buscar_url: Any) -> None:
    """Vários parâmetros são combinados com AND (todos devem bater)."""
    lote = ConcursoCandidatosLote.objects.create(concurso_uuid=uuid4(), concurso_nome='Concurso X')
    c1 = Candidato.objects.create(nome='Alfa', cpf='22222222222', email='alfa@email.com', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    c2 = Candidato.objects.create(nome='Beta', cpf='11111111111', email='beta@email.com', telefone='', data_nascimento='1990-01-01', genero='M', endereco='', cidade='', estado='', cep='', status='ativo', observacoes='')
    ConcursoCandidato.objects.create(candidato=c1, lote=lote, codigo_inscricao='1')
    ConcursoCandidato.objects.create(candidato=c2, lote=lote, codigo_inscricao='2')
    response = api_client.get(buscar_url, {'nome': 'Alfa', 'cpf': '22222222222'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == 'Alfa'
