"""Testes unitários para o modelo ConcursoCandidatoReclassificacao."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

from candidatos.models import (
    Candidato,
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
    ConcursoCandidatosLote,
)

pytestmark = pytest.mark.django_db


def _criar_candidato(nome: Any, cpf: Any) -> Any:
    """Executa  criar candidato."""
    return Candidato.objects.create(
        nome=nome,
        cpf=cpf,
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
def lote() -> Any:
    """Executa lote."""
    return ConcursoCandidatosLote.objects.create(
        concurso_uuid=uuid4(), concurso_nome="Concurso Teste"
    )


@pytest.fixture
def concurso_candidato(lote: Any) -> Any:
    """Executa concurso candidato."""
    c = _criar_candidato("Teste", "111.111.111-11")
    return ConcursoCandidato.objects.create(
        candidato=c,
        lote=lote,
        codigo_inscricao="001",
        classificacao=1,
        classificacao_nna=1,
        classificacao_pcd=None,
    )


class TestConcursoCandidatoReclassificacao:
    """Testes do modelo ConcursoCandidatoReclassificacao."""

    def test_cria_reclassificacao_nna(self, concurso_candidato: Any) -> None:
        """Verifica cria reclassificacao nna."""
        rec = ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato,
            desclassificado_de="NNA",
            motivo="Motivo teste",
            executado_por="user",
        )
        assert rec.desclassificado_de == "NNA"
        assert rec.motivo == "Motivo teste"
        assert rec.executado_por == "user"
        assert rec.uuid is not None
        assert rec.criado_em is not None

    def test_cria_reclassificacao_pcd(self, concurso_candidato: Any) -> None:
        """Verifica cria reclassificacao pcd."""
        rec = ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato,
            desclassificado_de="PCD",
            processo_uuid=uuid4(),
        )
        assert rec.desclassificado_de == "PCD"
        assert rec.processo_uuid is not None

    def test_str_retorna_concurso_candidato_id_e_cota(
        self, concurso_candidato: Any
    ) -> None:
        """Verifica str retorna concurso candidato id e cota."""
        rec = ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato, desclassificado_de="NNA"
        )
        expected = f"{concurso_candidato.id} - NNA"
        assert str(rec) == expected

    def test_meta_ordering_por_criado_em_decrescente(
        self, concurso_candidato: Any
    ) -> None:
        """Verifica meta ordering por criado em decrescente."""
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato, desclassificado_de="NNA"
        )
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato, desclassificado_de="PCD"
        )
        qs = ConcursoCandidatoReclassificacao.objects.filter(
            concurso_candidato=concurso_candidato
        )
        assert list(qs)[0].desclassificado_de == "PCD"

    def test_related_name_historicos_reclassificacao(
        self, concurso_candidato: Any
    ) -> None:
        """Verifica related name historicos reclassificacao."""
        ConcursoCandidatoReclassificacao.objects.create(
            concurso_candidato=concurso_candidato, desclassificado_de="NNA"
        )
        assert concurso_candidato.historicos_reclassificacao.count() == 1
        assert (
            concurso_candidato.historicos_reclassificacao.first().desclassificado_de
            == "NNA"
        )

    def test_classificacao_choices(self) -> None:
        """Verifica classificacao choices."""
        assert ConcursoCandidatoReclassificacao.CLASSIFICACAO_CHOICES == (
            ("GERAL", "GERAL"),
            ("NNA", "NNA"),
            ("PCD", "PCD"),
        )
