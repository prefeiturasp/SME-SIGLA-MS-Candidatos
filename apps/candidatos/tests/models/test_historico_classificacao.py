"""Testes do modelo ConcursoCandidatoHistoricoClassificacao."""

import pytest
from candidatos.models import ConcursoCandidatoHistoricoClassificacao
from candidatos.repository import (
    ConcursoCandidatoHistoricoClassificacaoRepository,
)

pytestmark = pytest.mark.django_db


class TestConcursoCandidatoHistoricoClassificacao:
    """Testes do modelo de histórico de classificação."""

    def test_cria_historico_com_foi_convocado_false(self, concurso_candidato):
        """Cria histórico com foi_convocado False quando CC não foi."""
        concurso_candidato.foi_convocado = False
        concurso_candidato.save(update_fields=["foi_convocado"])
        hist = ConcursoCandidatoHistoricoClassificacaoRepository.criar(
            concurso_candidato=concurso_candidato,
            classificacao_anterior=1,
            classificacao_nova=2,
            classificacao_nna_anterior=1,
            classificacao_nna_nova=2,
            mandado_judicial=True,
        )
        assert hist.foi_convocado is False
        assert hist.mandado_judicial is True
        assert hist.classificacao_nna_anterior == 1
        assert hist.classificacao_nna_nova == 2

    def test_cria_historico_copia_foi_convocado_true(self, concurso_candidato):
        """Copia foi_convocado=True do concurso candidato."""
        concurso_candidato.foi_convocado = True
        concurso_candidato.save(update_fields=["foi_convocado"])
        hist = ConcursoCandidatoHistoricoClassificacaoRepository.criar(
            concurso_candidato=concurso_candidato,
            classificacao_anterior=20,
            classificacao_nova=21,
            classificacao_nna_anterior=1,
            classificacao_nna_nova=2,
            mandado_judicial=True,
        )
        assert hist.foi_convocado is True

    def test_mandado_judicial_opcional_null(self, concurso_candidato):
        """Permite mandado_judicial None."""
        hist = ConcursoCandidatoHistoricoClassificacaoRepository.criar(
            concurso_candidato=concurso_candidato,
            classificacao_anterior=1,
            classificacao_nova=2,
        )
        assert hist.mandado_judicial is None

    def test_related_name_historicos_classificacao(self, concurso_candidato):
        """Related name historicos_classificacao funciona."""
        ConcursoCandidatoHistoricoClassificacaoRepository.criar(
            concurso_candidato=concurso_candidato,
            classificacao_anterior=1,
            classificacao_nova=2,
        )
        assert concurso_candidato.historicos_classificacao.count() == 1

    def test_str_contem_valores(self, concurso_candidato):
        """Str contém id e valores de classificação."""
        hist = ConcursoCandidatoHistoricoClassificacao.objects.create(
            concurso_candidato=concurso_candidato,
            classificacao_anterior=1,
            classificacao_nova=2,
            classificacao_nna_anterior=1,
            classificacao_nna_nova=2,
            classificacao_pcd_anterior=None,
            classificacao_pcd_nova=None,
        )
        texto = str(hist)
        assert str(concurso_candidato.id) in texto
        assert "1->2" in texto
