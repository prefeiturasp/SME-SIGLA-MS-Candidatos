"""Testes unitários para o modelo Candidato."""

from datetime import date
from uuid import uuid4

import pytest

from candidatos.models import Candidato

pytestmark = pytest.mark.django_db


def test_candidato_cria_com_campos_obrigatorios(candidato):
    """Testa criação do candidato com campos obrigatórios."""
    assert candidato.nome == "João Silva"
    assert candidato.cpf == "123.456.789-00"
    assert candidato.email is not None
    assert candidato.uuid is not None
    assert candidato.criado_em is not None
    assert candidato.atualizado_em is not None
    assert candidato.esta_ativo is True


def test_candidato_cria_com_valores_padrao():
    """Testa valores padrão do candidato."""
    candidato = Candidato.objects.create(
        nome="Maria",
        cpf="111.111.111-11",
        email=f"{uuid4().hex[:8]}@example.com",
    )
    assert candidato.status == "ativo"
    assert candidato.data_nascimento == date.today()
    assert candidato.telefone == ""
    assert candidato.observacoes == ""


def test_candidato_representacao_str(candidato):
    """Testa a representação textual do candidato."""
    assert str(candidato) == candidato.nome


def test_candidato_meta_opcoes():
    """Testa as opções Meta do model Candidato."""
    assert Candidato._meta.verbose_name == "Candidato"
    assert Candidato._meta.verbose_name_plural == "Candidatos"
    assert Candidato._meta.ordering == ["nome"]


def test_candidato_status_choices():
    """Testa as choices de status do candidato."""
    assert Candidato.STATUS_CHOICES == [
        ("ativo", "Ativo"),
        ("inativo", "Inativo"),
        ("suspenso", "Suspenso"),
    ]


def test_candidato_genero_choices():
    """Testa as choices de gênero do candidato."""
    assert Candidato.GENERO_CHOICES == [
        ("M", "Masculino"),
        ("F", "Feminino"),
        ("O", "Outro"),
        ("N", "Prefiro não informar"),
    ]


def test_candidato_ordenacao_por_nome(criar_candidato):
    """Testa ordenação dos candidatos por nome."""
    Candidato.objects.all().delete()
    c1 = criar_candidato(nome="Zoe", cpf="100.000.000-01")
    c2 = criar_candidato(nome="Ana", cpf="100.000.000-02")
    c3 = criar_candidato(nome="Maria", cpf="100.000.000-03")
    nomes = list(Candidato.objects.values_list("nome", flat=True))
    assert nomes == ["Ana", "Maria", "Zoe"]
    assert list(Candidato.objects.all()) == [c2, c3, c1]


def test_candidato_update(candidato):
    """Testa o update do candidato."""
    candidato.nome = "Atualizado"
    candidato.status = "inativo"
    candidato.save()
    candidato.refresh_from_db()
    assert candidato.nome == "Atualizado"
    assert candidato.status == "inativo"


def test_candidato_soft_delete(candidato):
    """Testa o soft delete do candidato."""
    assert candidato.esta_ativo is True
    candidato.esta_ativo = False
    candidato.save()
    candidato.refresh_from_db()
    assert candidato.esta_ativo is False
