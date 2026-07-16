"""Repositório de acesso a dados de ConcursoCandidatoReclassificacao."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import QuerySet

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
)


class ConcursoCandidatoReclassificacaoRepository:
    """Consultas e persistência de reclassificações de concurso candidato."""

    @staticmethod
    def serializar(
        historico: ConcursoCandidatoReclassificacao,
    ) -> dict[str, Any]:
        """Converte um histórico de reclassificação em dicionário."""
        return {
            "uuid": str(getattr(historico, "uuid", ""))
            if getattr(historico, "uuid", None)
            else None,
            "desclassificado_de": getattr(
                historico, "desclassificado_de", None
            ),
            "nova_classificacao": getattr(
                historico, "nova_classificacao", None
            ),
            "motivo": getattr(historico, "motivo", ""),
            "executado_por": getattr(historico, "executado_por", ""),
            "criado_em": getattr(historico, "criado_em", None),
        }

    @classmethod
    def serializar_lista(
        cls,
        historicos: list[ConcursoCandidatoReclassificacao]
        | QuerySet[ConcursoCandidatoReclassificacao],
    ) -> list[dict[str, Any]]:
        """Converte lista/queryset de históricos em dicionários."""
        return [cls.serializar(item) for item in historicos]

    @classmethod
    def criar(cls, **dados: Any) -> ConcursoCandidatoReclassificacao:
        """Cria e persiste um histórico de reclassificação."""
        return ConcursoCandidatoReclassificacao.objects.create(**dados)

    @classmethod
    def salvar(
        cls,
        historico: ConcursoCandidatoReclassificacao,
        *,
        campos_atualizacao: list[str] | None = None,
    ) -> None:
        """Persiste alterações em um histórico de reclassificação."""
        if campos_atualizacao:
            historico.save(update_fields=campos_atualizacao)
        else:
            historico.save()

    @classmethod
    def existe_desclassificacao(
        cls,
        concurso_candidato: ConcursoCandidato,
        desclassificado_de: str,
    ) -> bool:
        """Verifica se já existe desclassificação para a categoria."""
        return concurso_candidato.historicos_reclassificacao.filter(
            desclassificado_de=desclassificado_de
        ).exists()

    @classmethod
    def listar_por_concurso_candidato_ordenado(
        cls, concurso_candidato: ConcursoCandidato
    ) -> QuerySet[ConcursoCandidatoReclassificacao]:
        """Lista históricos do concurso candidato por criado_em desc."""
        return concurso_candidato.historicos_reclassificacao.all().order_by(
            "-criado_em"
        )

    @classmethod
    def listar_serializado_por_concurso_candidato(
        cls, concurso_candidato: ConcursoCandidato
    ) -> list[dict[str, Any]]:
        """Retorna históricos serializados do concurso candidato."""
        historicos = getattr(
            concurso_candidato, "historicos_reclassificacao", None
        )
        if historicos is None:
            return []
        try:
            return cls.serializar_lista(
                cls.listar_por_concurso_candidato_ordenado(concurso_candidato)
            )
        except Exception:
            return []

    @classmethod
    def atualizar_processo_uuid_em_lote(
        cls,
        concurso_candidato_ids: list[int] | QuerySet[Any],
        *,
        processo_uuid: UUID | str,
        desclassificado_de: str,
    ) -> int:
        """Atualiza processo_uuid dos históricos sem processo definidos."""
        return ConcursoCandidatoReclassificacao.objects.filter(
            concurso_candidato__in=concurso_candidato_ids,
            processo_uuid=None,
            desclassificado_de=desclassificado_de,
        ).update(processo_uuid=processo_uuid)
