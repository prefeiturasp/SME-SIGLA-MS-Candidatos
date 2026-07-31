"""Repositório de acesso a dados de ConcursoCandidatoReclassificacao."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from candidatos.models import (
    ConcursoCandidato,
    ConcursoCandidatoReclassificacao,
)
from django.db.models import Q, QuerySet


class ConcursoCandidatoReclassificacaoRepository:
    """Consultas e persistência de reclassificações de concurso candidato."""

    @staticmethod
    def serializar(
        historico: ConcursoCandidatoReclassificacao,
    ) -> dict[str, Any]:
        """Converta um histórico de reclassificação em dicionário."""
        return {
            "uuid": (
                str(getattr(historico, "uuid", ""))
                if getattr(historico, "uuid", None)
                else None
            ),
            "desclassificado_de": getattr(
                historico, "desclassificado_de", None
            ),
            "nova_classificacao": getattr(
                historico, "nova_classificacao", None
            ),
            "motivo": getattr(historico, "motivo", ""),
            "executado_por": getattr(historico, "executado_por", ""),
            "mandado_judicial": getattr(historico, "mandado_judicial", False),
            "criado_em": getattr(historico, "criado_em", None),
        }

    @classmethod
    def serializar_lista(
        cls,
        historicos: (
            list[ConcursoCandidatoReclassificacao]
            | QuerySet[ConcursoCandidatoReclassificacao]
        ),
    ) -> list[dict[str, Any]]:
        """Converta lista/queryset de históricos em dicionários."""
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
        """Persista alterações em um histórico de reclassificação."""
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
        """Verifica se há desclassificação ativa para a categoria.

        Considera apenas o registro mais recente entre os que têm
        ``desclassificado_de`` igual à categoria informada. Se o mais
        recente tiver ``mandado_judicial=True``, a desclassificação foi
        revertida e não é considerada ativa.

        Args:
            concurso_candidato: ConcursoCandidato avaliado.
            desclassificado_de: Categoria de origem (``NNA`` ou ``PCD``).

        Returns:
            ``True`` se houver desclassificação ativa; senão ``False``.
        """
        return cls.obter_ativa_por_categoria(
            concurso_candidato, desclassificado_de
        ) is not None

    @classmethod
    def obter_ativa_por_categoria(
        cls,
        concurso_candidato: ConcursoCandidato,
        desclassificado_de: str,
    ) -> ConcursoCandidatoReclassificacao | None:
        """Retorna a desclassificação ativa da categoria, se existir.

        Considera o registro mais recente entre os que envolvem a
        categoria informada — seja como origem da desclassificação
        (``desclassificado_de``), seja como destino de uma reversão por
        mandado judicial (``nova_classificacao`` com
        ``mandado_judicial=True``, que inverte esses campos). Só há
        desclassificação ativa se esse registro mais recente for, ele
        próprio, uma desclassificação (``desclassificado_de`` igual à
        categoria) ainda não revertida (``mandado_judicial=False``).

        O desempate por ``-id`` é necessário porque ``criado_em`` tem
        resolução de datetime e duas operações podem ser persistidas no
        mesmo instante, tornando a ordenação por ``-criado_em`` sozinha
        indeterminada entre os registros empatados.

        Args:
            concurso_candidato: ConcursoCandidato avaliado.
            desclassificado_de: Categoria de origem (``NNA`` ou ``PCD``).

        Returns:
            O registro ativo ou ``None`` quando não houver.
        """
        mais_recente = (
            concurso_candidato.historicos_reclassificacao.filter(
                Q(desclassificado_de=desclassificado_de)
                | Q(
                    nova_classificacao=desclassificado_de,
                    mandado_judicial=True,
                )
            )
            .order_by("-criado_em", "-id")
            .first()
        )
        if (
            mais_recente is None
            or mais_recente.mandado_judicial
            or mais_recente.desclassificado_de != desclassificado_de
        ):
            return None
        return mais_recente

    @classmethod
    def listar_por_concurso_candidato_ordenado(
        cls, concurso_candidato: ConcursoCandidato
    ) -> QuerySet[ConcursoCandidatoReclassificacao]:
        """Lista históricos do concurso candidato por criado_em desc.

        O desempate por ``-id`` garante ordem determinística mesmo
        quando dois registros têm o mesmo ``criado_em``.
        """
        return concurso_candidato.historicos_reclassificacao.all().order_by(
            "-criado_em", "-id"
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
