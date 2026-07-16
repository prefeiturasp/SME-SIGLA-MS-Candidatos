"""Repositório de acesso a dados de ConcursoCandidatoEliminacao."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import QuerySet

from candidatos.models import ConcursoCandidatoEliminacao


class ConcursoCandidatoEliminacaoRepository:
    """Consultas e persistência de eliminações de concurso candidato."""

    @staticmethod
    def serializar(
        historico: ConcursoCandidatoEliminacao,
    ) -> dict[str, Any]:
        """Converte um histórico de eliminação em dicionário."""
        return {
            "uuid": str(historico.uuid) if historico.uuid else None,
            "motivo": historico.motivo,
            "executado_por": historico.executado_por,
            "processo_uuid": (
                str(historico.processo_uuid)
                if historico.processo_uuid
                else None
            ),
            "criado_em": historico.criado_em,
        }

    @classmethod
    def serializar_lista(
        cls,
        historicos: list[ConcursoCandidatoEliminacao]
        | QuerySet[ConcursoCandidatoEliminacao],
    ) -> list[dict[str, Any]]:
        """Converte lista/queryset de históricos em dicionários."""
        return [cls.serializar(item) for item in historicos]

    @classmethod
    def criar(cls, **dados: Any) -> ConcursoCandidatoEliminacao:
        """Cria e persiste um histórico de eliminação."""
        return ConcursoCandidatoEliminacao.objects.create(**dados)

    @classmethod
    def atualizar_processo_uuid_em_lote(
        cls,
        concurso_candidato_ids: list[int] | QuerySet[Any],
        *,
        processo_uuid: UUID | str,
    ) -> int:
        """Atualiza processo_uuid dos históricos sem processo definidos."""
        return ConcursoCandidatoEliminacao.objects.filter(
            concurso_candidato__in=concurso_candidato_ids,
            processo_uuid=None,
        ).update(processo_uuid=processo_uuid)
