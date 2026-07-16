"""Testes unitários dos serializers de candidato."""

from uuid import uuid4

import pytest

from candidatos.serializer.candidato import (
    CandidatoConcursoCreateSerializer,
    CandidatoSerializer,
    CandidatosLoteCreateSerializer,
)

pytestmark = pytest.mark.django_db


def test_candidato_serializer_serializacao(candidato, concurso_candidato):
    """Testa serialização do CandidatoSerializer com concursos."""
    data = CandidatoSerializer(candidato).data
    assert data["nome"] == candidato.nome
    assert data["cpf"] == candidato.cpf
    assert data["email"] == candidato.email
    assert "uuid" in data
    assert "criado_em" in data
    assert "atualizado_em" in data
    assert "esta_ativo" in data
    assert len(data["concursos"]) == 1
    assert data["concursos"][0]["codigo_inscricao"] == "001"
    assert concurso_candidato.candidato_id == candidato.id


def test_candidato_serializer_cria(candidato_data):
    """Testa criação via CandidatoSerializer."""
    serializer = CandidatoSerializer(data=candidato_data)
    assert serializer.is_valid(), serializer.errors
    instancia = serializer.save()
    assert instancia.nome == candidato_data["nome"]
    assert instancia.cpf == candidato_data["cpf"]


def test_candidato_serializer_campos_somente_leitura(candidato):
    """Testa que campos somente leitura não são sobrescritos."""
    original_criado_em = candidato.criado_em
    serializer = CandidatoSerializer(
        candidato,
        data={
            "nome": "Novo Nome",
            "esta_ativo": False,
            "criado_em": "2020-01-01T00:00:00Z",
        },
        partial=True,
    )
    assert serializer.is_valid(), serializer.errors
    atualizado = serializer.save()
    assert atualizado.nome == "Novo Nome"
    assert atualizado.esta_ativo is True
    assert atualizado.criado_em == original_criado_em


def test_candidato_concurso_create_serializer_valido():
    """Testa validação válida do CandidatoConcursoCreateSerializer."""
    serializer = CandidatoConcursoCreateSerializer(
        data={
            "nome": "Maria",
            "cpf": "123.456.789-00",
            "email": "maria@example.com",
            "codigo_inscricao": "001",
            "classificacao": "10",
            "pontos": "100.5",
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["codigo_inscricao"] == "001"


def test_candidato_concurso_create_serializer_requer_codigo_inscricao():
    """Testa que codigo_inscricao é obrigatório."""
    serializer = CandidatoConcursoCreateSerializer(data={"nome": "Maria"})
    assert serializer.is_valid() is False
    assert "codigo_inscricao" in serializer.errors


def test_candidatos_lote_create_serializer_valido():
    """Testa validação válida do CandidatosLoteCreateSerializer."""
    concurso_uuid = uuid4()
    serializer = CandidatosLoteCreateSerializer(
        data={
            "concurso_uuid": str(concurso_uuid),
            "concurso_nome": "PME 2024",
            "candidatos": [
                {
                    "nome": "João",
                    "codigo_inscricao": "001",
                    "cpf": "111.111.111-11",
                }
            ],
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["concurso_uuid"] == concurso_uuid
    assert len(serializer.validated_data["candidatos"]) == 1


def test_candidatos_lote_create_serializer_invalido():
    """Testa validação inválida do CandidatosLoteCreateSerializer."""
    serializer = CandidatosLoteCreateSerializer(
        data={"concurso_nome": "Sem UUID", "candidatos": []}
    )
    assert serializer.is_valid() is False
    assert "concurso_uuid" in serializer.errors
