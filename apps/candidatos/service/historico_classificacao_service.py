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


class HistoricoClassificacaoService:
    """Service para histórico de deslocamento de classificação."""

    @staticmethod
    def _classificacao_piorou(anterior: Any, nova: Any) -> bool:
        """Indica se a classificação numérica piorou (número maior)."""
        if anterior is None or nova is None:
            return False
        try:
            return int(nova) > int(anterior)
        except (TypeError, ValueError):
            return False

    @classmethod
    def classificacao_deslocada(
        cls,
        *,
        classificacao_anterior: Any,
        classificacao_nova: Any,
        classificacao_nna_anterior: Any,
        classificacao_nna_nova: Any,
        classificacao_pcd_anterior: Any,
        classificacao_pcd_nova: Any,
    ) -> bool:
        """Retorna True se alguma classificação piorou (alguém entrou à frente)."""  # noqa E501
        return any(
            (
                cls._classificacao_piorou(
                    classificacao_anterior, classificacao_nova
                ),
                cls._classificacao_piorou(
                    classificacao_nna_anterior, classificacao_nna_nova
                ),
                cls._classificacao_piorou(
                    classificacao_pcd_anterior, classificacao_pcd_nova
                ),
            )
        )

    @classmethod
    def registrar_deslocamento_classificacao(
        cls,
        concurso_candidato: ConcursoCandidato,
        *,
        classificacao_nova: Any,
        classificacao_nna_nova: Any,
        classificacao_pcd_nova: Any,
        motivo: str = "",
    ) -> ConcursoCandidatoHistoricoClassificacao | None:
        """Registra histórico se a classificação do candidato piorou.

        Args:
            concurso_candidato: Registro atual (ainda com valores anteriores).
            classificacao_nova: Nova classificação geral.
            classificacao_nna_nova: Nova classificação NNA.
            classificacao_pcd_nova: Nova classificação PCD.
            motivo: Motivo/observação.

        Returns:
            Histórico criado ou ``None`` se não houve deslocamento.
        """
        if not cls.classificacao_deslocada(
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
            motivo=motivo,
        )
