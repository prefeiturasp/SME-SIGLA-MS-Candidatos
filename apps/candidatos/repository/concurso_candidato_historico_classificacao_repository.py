"""Repositório de histórico de classificação de concurso candidato."""

from __future__ import annotations

from typing import Any

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoHistoricoClassificacao,
)
from django.db.models import QuerySet


class ConcursoCandidatoHistoricoClassificacaoRepository:
    """Consultas e persistência de históricos de classificação."""

    @classmethod
    def criar(
        cls,
        *,
        concurso_candidato: ConcursoCandidato,
        mandado_judicial: bool | None = None,
        motivo: str = "",
        **dados: Any,
    ) -> ConcursoCandidatoHistoricoClassificacao:
        """Cria histórico copiando ``foi_convocado`` do concurso candidato.

        Se ``concurso_candidato.foi_convocado`` for ``True``, o histórico
        também é gravado com ``foi_convocado=True``.

        Args:
            concurso_candidato: Registro cuja classificação mudou.
            mandado_judicial: Flag opcional de mandado judicial.
            motivo: Motivo/observação.
            **dados: Demais campos do histórico (classificações etc.).

        Returns:
            Histórico persistido.
        """
        return ConcursoCandidatoHistoricoClassificacao.objects.create(
            concurso_candidato=concurso_candidato,
            mandado_judicial=mandado_judicial,
            foi_convocado=bool(concurso_candidato.foi_convocado),
            motivo=motivo or "",
            **dados,
        )

    @classmethod
    def listar_por_concurso_candidato(
        cls, concurso_candidato: ConcursoCandidato
    ) -> QuerySet[ConcursoCandidatoHistoricoClassificacao]:
        """Lista históricos do concurso candidato por criado_em desc."""
        return concurso_candidato.historicos_classificacao.all().order_by(
            "-criado_em"
        )
