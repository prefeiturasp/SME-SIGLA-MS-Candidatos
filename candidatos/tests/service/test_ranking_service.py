"""
Testes unitários para candidatos/service/ranking_service.py.
Cobre atualizar_ranking (linhas 4-12) e atualizar_ranking_escolha (linhas 15-41).
"""
import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from candidatos.models import Candidato, ConcursoCandidato, ConcursoCandidatosLote
from candidatos.service.ranking_service import atualizar_ranking, atualizar_ranking_escolha


pytestmark = pytest.mark.django_db


def _candidato():
    return Candidato.objects.create(
        nome="Teste",
        cpf=f"{uuid4().int % 10**11:011d}",
        email=f"{uuid4().hex[:8]}@example.com",
        telefone="",
        data_nascimento="1990-01-01",
        genero="M",
        endereco="",
        cidade="",
        estado="",
        cep="",
        status="ativo",
        observacoes="",
    )


@pytest.fixture
def lote():
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(),
        concurso_nome="Concurso Teste",
    )


@pytest.fixture
def dois_cc(lote):
    c1 = ConcursoCandidato.objects.create(
        candidato=_candidato(), lote=lote, codigo_inscricao="1", ranking=0
    )
    c2 = ConcursoCandidato.objects.create(
        candidato=_candidato(), lote=lote, codigo_inscricao="2", ranking=0
    )
    return [c1, c2]


# --- atualizar_ranking (linhas 4-12) ---


def test_atualizar_ranking_lista_vazia_nao_quebra():
    atualizar_ranking([])


def test_atualizar_ranking_atribui_ranking_e_persiste(dois_cc):
    atualizar_ranking(dois_cc)
    dois_cc[0].refresh_from_db()
    dois_cc[1].refresh_from_db()
    assert dois_cc[0].ranking == 1
    assert dois_cc[1].ranking == 2


def test_atualizar_ranking_excecao_nao_propaga():
    """Em caso de erro no bulk_update, o except faz pass (linhas 10-12)."""
    itens = [MagicMock(spec=ConcursoCandidato)]
    with patch("candidatos.service.ranking_service.ConcursoCandidato.objects.bulk_update", side_effect=Exception("db")):
        atualizar_ranking(itens)
    assert itens[0].ranking == 1


# --- atualizar_ranking_escolha (linhas 15-41) ---


def test_atualizar_ranking_escolha_lista_vazia_nao_quebra():
    atualizar_ranking_escolha([])


def test_atualizar_ranking_escolha_ordena_pcd_primeiro_e_persiste(lote):
    """PCD primeiro por classificacao, depois demais; atribui ranking_escolha (linhas 24-37)."""
    c_geral = ConcursoCandidato.objects.create(
        candidato=_candidato(), lote=lote, codigo_inscricao="g",
        classificacao=1, classificacao_pcd=None, ranking_escolha=0
    )
    c_pcd = ConcursoCandidato.objects.create(
        candidato=_candidato(), lote=lote, codigo_inscricao="p",
        classificacao=5, classificacao_pcd=1, ranking_escolha=0
    )
    itens = [c_geral, c_pcd]
    atualizar_ranking_escolha(itens)
    c_pcd.refresh_from_db()
    c_geral.refresh_from_db()
    assert c_pcd.ranking_escolha == 1
    assert c_geral.ranking_escolha == 2


def test_atualizar_ranking_escolha_excecao_nao_propaga():
    """Em caso de erro, o except faz pass (linhas 39-41)."""
    itens = [MagicMock(spec=ConcursoCandidato)]
    itens[0].classificacao_pcd = None
    itens[0].classificacao = 1
    with patch("candidatos.service.ranking_service.ConcursoCandidato.objects.bulk_update", side_effect=Exception("db")):
        atualizar_ranking_escolha(itens)
    assert itens[0].ranking_escolha == 1
