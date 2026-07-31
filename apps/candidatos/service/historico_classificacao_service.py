"""Serviço de registro de histórico de deslocamento de classificação."""

from __future__ import annotations

from typing import Any

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoHistoricoClassificacao,
)
from candidatos.repository import (
    ConcursoCandidatoHistoricoClassificacaoRepository,
)


def _classificacao_piorou(anterior: Any, nova: Any) -> bool:
    """Indica se a classificação numérica piorou (número maior)."""
    if anterior is None or nova is None:
        return False
    try:
        return int(nova) > int(anterior)
    except (TypeError, ValueError):
        return False


def classificacao_deslocada(
    *,
    classificacao_anterior: Any,
    classificacao_nova: Any,
    classificacao_nna_anterior: Any,
    classificacao_nna_nova: Any,
    classificacao_pcd_anterior: Any,
    classificacao_pcd_nova: Any,
) -> bool:
    """Retorna True se alguma classificação piorou (alguém entrou à frente)."""
    return any(
        (
            _classificacao_piorou(classificacao_anterior, classificacao_nova),
            _classificacao_piorou(
                classificacao_nna_anterior, classificacao_nna_nova
            ),
            _classificacao_piorou(
                classificacao_pcd_anterior, classificacao_pcd_nova
            ),
        )
    )


def registrar_deslocamento_classificacao(
    concurso_candidato: ConcursoCandidato,
    *,
    classificacao_nova: Any,
    classificacao_nna_nova: Any,
    classificacao_pcd_nova: Any,
    mandado_judicial: bool | None = None,
    motivo: str = "",
) -> ConcursoCandidatoHistoricoClassificacao | None:
    """Registra histórico se a classificação do candidato piorou.

    Args:
        concurso_candidato: Registro atual (ainda com valores anteriores).
        classificacao_nova: Nova classificação geral.
        classificacao_nna_nova: Nova classificação NNA.
        classificacao_pcd_nova: Nova classificação PCD.
        mandado_judicial: Flag opcional de mandado judicial.
        motivo: Motivo/observação.

    Returns:
        Histórico criado ou ``None`` se não houve deslocamento.
    """
    breakpoint()
    if not classificacao_deslocada(
        classificacao_anterior=concurso_candidato.classificacao,
        classificacao_nova=classificacao_nova,
        classificacao_nna_anterior=concurso_candidato.classificacao_nna,
        classificacao_nna_nova=classificacao_nna_nova,
        classificacao_pcd_anterior=concurso_candidato.classificacao_pcd,
        classificacao_pcd_nova=classificacao_pcd_nova,
    ):
        return None

    return ConcursoCandidatoHistoricoClassificacaoRepository.criar(
        concurso_candidato=concurso_candidato,
        classificacao_anterior=concurso_candidato.classificacao,
        classificacao_nova=classificacao_nova,
        classificacao_nna_anterior=concurso_candidato.classificacao_nna,
        classificacao_nna_nova=classificacao_nna_nova,
        classificacao_pcd_anterior=concurso_candidato.classificacao_pcd,
        classificacao_pcd_nova=classificacao_pcd_nova,
        mandado_judicial=mandado_judicial,
        motivo=motivo,
    )
