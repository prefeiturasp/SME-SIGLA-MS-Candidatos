import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from candidatos.models import Candidato


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def candidato_url():
    return reverse('candidato-list')


@pytest.fixture
def candidato_data():
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
    candidato1 = Candidato.objects.create(**candidato_data)
    candidato2 = Candidato.objects.create(**candidato_data_2)
    candidato3 = Candidato.objects.create(**candidato_data_3)
    return {
        'candidato1': candidato1,
        'candidato2': candidato2,
        'candidato3': candidato3
    }


