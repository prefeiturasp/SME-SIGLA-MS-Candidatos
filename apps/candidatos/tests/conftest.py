"""Módulo tests/conftest."""

from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatosLote,
)


@pytest.fixture
def api_client():
    """Cliente HTTP para requisições de teste."""
    return APIClient()


@pytest.fixture
def candidato_url():
    """URL do endpoint de candidatos."""
    return reverse("candidato-list")


@pytest.fixture
def candidato_data():
    """Dados de candidato para criação no teste."""
    return {
        "nome": "João Silva",
        "cpf": "123.456.789-00",
        "email": "joao.silva@email.com",
        "telefone": "(11) 99999-9999",
        "data_nascimento": "1990-01-15",
        "genero": "M",
        "endereco": "Rua das Flores, 123",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01234-567",
        "status": "ativo",
        "observacoes": "Candidato teste",
    }


@pytest.fixture
def candidato_data_2():
    """Segundo conjunto de dados de candidato."""
    return {
        "nome": "Maria Santos",
        "cpf": "987.654.321-00",
        "email": "maria.santos@email.com",
        "telefone": "(11) 88888-8888",
        "data_nascimento": "1985-05-20",
        "genero": "F",
        "endereco": "Av. Paulista, 456",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01310-100",
        "status": "ativo",
        "observacoes": "Candidata teste",
    }


@pytest.fixture
def candidato_data_3():
    """Terceiro conjunto de dados de candidato."""
    return {
        "nome": "Pedro Oliveira",
        "cpf": "111.222.333-44",
        "email": "pedro.oliveira@email.com",
        "telefone": "(21) 77777-7777",
        "data_nascimento": "1992-12-10",
        "genero": "M",
        "endereco": "Rua Copacabana, 789",
        "cidade": "Rio de Janeiro",
        "estado": "RJ",
        "cep": "22000-000",
        "status": "inativo",
        "observacoes": "Candidato inativo",
    }


@pytest.fixture
def candidatos_criados(candidato_data, candidato_data_2, candidato_data_3):
    """Candidatos persistidos no banco para o teste."""
    candidato1 = Candidato.objects.create(**candidato_data)
    candidato2 = Candidato.objects.create(**candidato_data_2)
    candidato3 = Candidato.objects.create(**candidato_data_3)
    return {
        "candidato1": candidato1,
        "candidato2": candidato2,
        "candidato3": candidato3,
    }


@pytest.fixture
def criar_candidato():
    """Factory para criar candidatos de exemplo no banco."""

    def _criar(**overrides):
        dados = {
            "nome": "João Silva",
            "cpf": "123.456.789-00",
            "email": f"{uuid4().hex[:8]}@example.com",
            "telefone": "",
            "data_nascimento": "1990-01-01",
            "genero": "M",
            "endereco": "",
            "cidade": "",
            "estado": "",
            "cep": "",
            "status": "ativo",
            "observacoes": "",
        }
        dados.update(overrides)
        return Candidato.objects.create(**dados)

    return _criar


@pytest.fixture
def candidato(criar_candidato):
    """Candidato padrão usado nos testes."""
    return criar_candidato()


@pytest.fixture
def criar_lote():
    """Factory para criar lotes de exemplo no banco."""

    def _criar(**overrides):
        dados = {
            "concurso_uuid": uuid4(),
            "concurso_nome": "Concurso Teste",
        }
        dados.update(overrides)
        return ConcursoCandidatosLote.objects.create(**dados)

    return _criar


@pytest.fixture
def lote(criar_lote):
    """Lote de concurso usado nos testes."""
    return criar_lote()


@pytest.fixture
def concurso_candidato(lote, candidato):
    """ConcursoCandidato de exemplo para os testes."""
    return ConcursoCandidato.objects.create(
        candidato=candidato,
        lote=lote,
        codigo_inscricao="001",
        classificacao=1,
        classificacao_nna=1,
        classificacao_pcd=None,
    )
