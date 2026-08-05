"""Repositório de histórico de classificação de concurso candidato."""

from __future__ import annotations

from typing import Any

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoHistoricoClassificacao,
)
from candidatos.serializer.historico_classificacao import (
    ConcursoCandidatoHistoricoClassificacaoSerializer,
)
from django.db.models import QuerySet


class ConcursoCandidatoHistoricoClassificacaoRepository:
    """Consultas e persistência de históricos de classificação."""

    @classmethod
    def criar(
        cls,
        *,
        concurso_candidato: ConcursoCandidato,
        motivo: str = "",
        **dados: Any,
    ) -> ConcursoCandidatoHistoricoClassificacao:
        """Cria histórico copiando ``foi_convocado`` do concurso candidato.

        Se ``concurso_candidato.foi_convocado`` for ``True``, o histórico
        também é gravado com ``foi_convocado=True``.

        Args:
            concurso_candidato: Registro cuja classificação mudou.
            motivo: Motivo/observação.
            **dados: Demais campos do histórico (classificações etc.).

        Returns:
            Histórico persistido.
        """
        return ConcursoCandidatoHistoricoClassificacao.objects.create(
            concurso_candidato=concurso_candidato,
            foi_convocado=bool(concurso_candidato.foi_convocado),
            motivo=motivo or "",
            **dados,
        )

    @classmethod
    def listar_por_concurso_candidato(
        cls, concurso_candidato: ConcursoCandidato
    ) -> QuerySet[ConcursoCandidatoHistoricoClassificacao]:
        """Lista históricos do concurso candidato por criado_em desc."""
        return concurso_candidato.historicos_classificacao.all()

    @staticmethod
    def serializar(
        historico: ConcursoCandidatoHistoricoClassificacao,
    ) -> dict[str, Any]:
        """Converta um histórico de classificação em dicionário."""
        return ConcursoCandidatoHistoricoClassificacaoSerializer(
            historico
        ).data

    @classmethod
    def serializar_lista(
        cls,
        historicos: (
            list[ConcursoCandidatoHistoricoClassificacao]
            | QuerySet[ConcursoCandidatoHistoricoClassificacao]
        ),
    ) -> list[dict[str, Any]]:
        """Converta lista/queryset de históricos em dicionários."""
        return ConcursoCandidatoHistoricoClassificacaoSerializer(
            historicos, many=True
        ).data

    @classmethod
    def listar_serializado_por_concurso_candidato(
        cls, concurso_candidato: ConcursoCandidato
    ) -> list[dict[str, Any]]:
        """Retorna históricos de classificação serializados."""
        try:
            return cls.serializar_lista(
                cls.listar_por_concurso_candidato(concurso_candidato)
            )
        except Exception:
            return []
