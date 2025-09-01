"""
Testes unitários para CandidatoViewSet usando pytest
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from candidatos.models import Candidato

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    """Fixture para cliente API"""
    return APIClient()


@pytest.fixture
def candidato_url():
    """Fixture para URL da lista de candidatos"""
    return reverse('candidato-list')


@pytest.fixture
def candidato_data():
    """Fixture com dados de teste para candidato"""
    return {
        'nome': 'João Silva',
        'cpf': '123.456.789-00',
        'email': 'joao.silva@email.com',
        'telefone': '(11) 99999-9999',
        'data_nascimento': '1990-01-15',
        'genero': 'M',
        'endereco': 'Rua das Flores, 123',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234-567',
        'status': 'ativo',
        'observacoes': 'Candidato teste'
    }


@pytest.fixture
def candidato_data_2():
    """Fixture com dados de teste para segundo candidato"""
    return {
        'nome': 'Maria Santos',
        'cpf': '987.654.321-00',
        'email': 'maria.santos@email.com',
        'telefone': '(11) 88888-8888',
        'data_nascimento': '1985-05-20',
        'genero': 'F',
        'endereco': 'Av. Paulista, 456',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01310-100',
        'status': 'ativo',
        'observacoes': 'Candidata teste'
    }


@pytest.fixture
def candidato_data_3():
    """Fixture com dados de teste para terceiro candidato"""
    return {
        'nome': 'Pedro Oliveira',
        'cpf': '111.222.333-44',
        'email': 'pedro.oliveira@email.com',
        'telefone': '(21) 77777-7777',
        'data_nascimento': '1992-12-10',
        'genero': 'M',
        'endereco': 'Rua Copacabana, 789',
        'cidade': 'Rio de Janeiro',
        'estado': 'RJ',
        'cep': '22000-000',
        'status': 'inativo',
        'observacoes': 'Candidato inativo'
    }


@pytest.fixture
def candidatos_criados(candidato_data, candidato_data_2, candidato_data_3):
    """Fixture que cria candidatos para os testes"""
    candidato1 = Candidato.objects.create(**candidato_data)
    candidato2 = Candidato.objects.create(**candidato_data_2)
    candidato3 = Candidato.objects.create(**candidato_data_3)
    return {
        'candidato1': candidato1,
        'candidato2': candidato2,
        'candidato3': candidato3
    }


# Testes CRUD
def test_list_candidatos(api_client, candidato_url, candidatos_criados):
    """Testa listagem de todos os candidatos"""
    response = api_client.get(candidato_url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    
    # Verificar se os dados estão corretos
    candidatos = response.data['results']
    nomes = [c['nome'] for c in candidatos]
    assert 'João Silva' in nomes
    assert 'Maria Santos' in nomes
    assert 'Pedro Oliveira' in nomes


def test_create_candidato(api_client, candidato_url):
    """Testa criação de novo candidato"""
    novo_candidato = {
        'nome': 'Ana Costa',
        'cpf': '555.666.777-88',
        'email': 'ana.costa@email.com',
        'telefone': '(11) 66666-6666',
        'data_nascimento': '1988-08-25',
        'genero': 'F',
        'endereco': 'Rua Augusta, 321',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01305-000',
        'status': 'ativo',
        'observacoes': 'Nova candidata'
    }
    
    response = api_client.post(candidato_url, novo_candidato, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Candidato.objects.count() == 1
    
    # Verificar se o candidato foi criado corretamente
    candidato = Candidato.objects.get(cpf='555.666.777-88')
    assert candidato.nome == 'Ana Costa'
    assert candidato.email == 'ana.costa@email.com'


def test_retrieve_candidato(api_client, candidatos_criados):
    """Testa busca de candidato específico"""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'pk': candidato1.pk})
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['nome'] == 'João Silva'
    assert response.data['cpf'] == '123.456.789-00'
    assert response.data['email'] == 'joao.silva@email.com'


def test_update_candidato(api_client, candidatos_criados):
    """Testa atualização de candidato"""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'pk': candidato1.pk})
    dados_atualizados = {
        'nome': 'João Silva Santos',
        'cpf': '123.456.789-00',
        'email': 'joao.silva.santos@email.com',
        'telefone': '(11) 99999-9999',
        'data_nascimento': '1990-01-15',
        'genero': 'M',
        'endereco': 'Rua das Flores, 123',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234-567',
        'status': 'ativo',
        'observacoes': 'Candidato atualizado'
    }
    
    response = api_client.put(url, dados_atualizados, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar se foi atualizado no banco
    candidato = Candidato.objects.get(pk=candidato1.pk)
    assert candidato.nome == 'João Silva Santos'
    assert candidato.email == 'joao.silva.santos@email.com'
    assert candidato.observacoes == 'Candidato atualizado'


def test_partial_update_candidato(api_client, candidatos_criados):
    """Testa atualização parcial de candidato"""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'pk': candidato1.pk})
    dados_parciais = {
        'telefone': '(11) 11111-1111',
        'status': 'suspenso'
    }
    
    response = api_client.patch(url, dados_parciais, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    
    # Verificar se foi atualizado no banco
    candidato = Candidato.objects.get(pk=candidato1.pk)
    assert candidato.telefone == '(11) 11111-1111'
    assert candidato.status == 'suspenso'
    # Verificar se outros campos não foram alterados
    assert candidato.nome == 'João Silva'


def test_delete_candidato(api_client, candidatos_criados):
    """Testa exclusão de candidato"""
    candidato1 = candidatos_criados['candidato1']
    url = reverse('candidato-detail', kwargs={'pk': candidato1.pk})
    response = api_client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Candidato.objects.count() == 2
    
    # Verificar se o candidato foi realmente excluído
    with pytest.raises(Candidato.DoesNotExist):
        Candidato.objects.get(pk=candidato1.pk)
