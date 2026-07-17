"""Repositório de acesso a dados de ConcursoCandidatosLote."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from candidatos.models import ConcursoCandidatosLote
from django.db.models import QuerySet


class ConcursoCandidatosLoteRepository:
    """Consultas e persistência de lotes de candidatos do concurso."""

    @classmethod
    def criar(cls, **dados: Any) -> ConcursoCandidatosLote:
        """Cria e persiste um lote de candidatos."""
        return ConcursoCandidatosLote.objects.create(**dados)

    @classmethod
    def obter_ultimo_por_concurso(
        cls, concurso_uuid: UUID | str
    ) -> ConcursoCandidatosLote | None:
        """Retorna o lote mais recente do concurso informado."""
        return (
            ConcursoCandidatosLote.objects.filter(concurso_uuid=concurso_uuid)
            .order_by("-criado_em")
            .first()
        )

    @classmethod
    def listar_pares_concurso_uuid_ordenado(cls) -> QuerySet[Any]:
        """Lista pares (concurso_uuid, uuid) ordenados por criado_em desc."""
        return ConcursoCandidatosLote.objects.order_by(
            "-criado_em"
        ).values_list("concurso_uuid", "uuid")
