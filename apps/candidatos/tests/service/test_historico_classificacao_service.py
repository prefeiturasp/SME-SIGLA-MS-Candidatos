"""Testes do serviço de histórico de classificação."""

import pytest
from candidatos.models import ConcursoCandidatoHistoricoClassificacao
from candidatos.service.historico_classificacao_service import (
    HistoricoClassificacaoService,
)

pytestmark = pytest.mark.django_db


def test_classificacao_deslocada_quando_nna_piora():
    """Detecta deslocamento quando NNA aumenta."""
    assert HistoricoClassificacaoService.classificacao_deslocada(
        classificacao_anterior=20,
        classificacao_nova=21,
        classificacao_nna_anterior=1,
        classificacao_nna_nova=2,
        classificacao_pcd_anterior=None,
        classificacao_pcd_nova=None,
    )


def test_classificacao_deslocada_false_quando_igual():
    """Não detecta deslocamento quando valores iguais."""
    assert not HistoricoClassificacaoService.classificacao_deslocada(
        classificacao_anterior=1,
        classificacao_nova=1,
        classificacao_nna_anterior=None,
        classificacao_nna_nova=None,
        classificacao_pcd_anterior=None,
        classificacao_pcd_nova=None,
    )


def test_registrar_deslocamento_cria_historico(concurso_candidato):
    """Registra histórico quando classificação piora."""
    concurso_candidato.classificacao_nna = 1
    concurso_candidato.classificacao = 20
    concurso_candidato.foi_convocado = True
    concurso_candidato.save(
        update_fields=["classificacao_nna", "classificacao", "foi_convocado"]
    )
    hist = HistoricoClassificacaoService.registrar_deslocamento_classificacao(
        concurso_candidato,
        classificacao_nova=21,
        classificacao_nna_nova=2,
        classificacao_pcd_nova=None,
    )
    assert hist is not None
    assert hist.foi_convocado is True
    assert hist.classificacao_nna_anterior == 1
    assert hist.classificacao_nna_nova == 2
    assert ConcursoCandidatoHistoricoClassificacao.objects.count() == 1


def test_registrar_deslocamento_sem_piora_retorna_none(concurso_candidato):
    """Não cria histórico quando classificação não piora."""
    hist = HistoricoClassificacaoService.registrar_deslocamento_classificacao(
        concurso_candidato,
        classificacao_nova=concurso_candidato.classificacao,
        classificacao_nna_nova=concurso_candidato.classificacao_nna,
        classificacao_pcd_nova=concurso_candidato.classificacao_pcd,
    )
    assert hist is None
    assert ConcursoCandidatoHistoricoClassificacao.objects.count() == 0
