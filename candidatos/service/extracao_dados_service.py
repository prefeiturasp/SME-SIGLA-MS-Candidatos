"""Agregações para a extração de dados de habilitados / convocados.

Toda contagem parte sempre do **último lote importado** de cada concurso
(o lote mais recente por ``criado_em``). Tanto para um concurso específico
quanto para o agregado de todos os concursos, considera-se apenas o último
lote vigente, garantindo regra única entre habilitados e convocados.
"""

from typing import Any
from uuid import UUID

from django.db.models import Count
from django.db.models.query import QuerySet

from candidatos.models import ConcursoCandidato, ConcursoCandidatosLote

CATEGORIAS = ("GERAL", "PCD", "NNA")


def montar_extracao_dados(
    concurso_uuid: UUID | str | None = None,
    filtros: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Monta o dicionário de indicadores de habilitados e convocações.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        filtros: Lista de ``{ano, processo_uuids}``; ausente (ou vazia) →
            agregado direto na raiz, sem quebra por ano.

    Returns:
        Dicionário com ``habilitados`` e, por ano (ou na raiz), os
        ``convocados`` e ``nao-convocados`` do escopo.
    """
    habilitados = _contar_habilitados(concurso_uuid)
    resultado = {"habilitados": habilitados}

    if filtros:
        for filtro in filtros:
            ano = str(filtro["ano"])
            processo_uuids = filtro["processo_uuids"]
            habilitados_ano = _contar_habilitados_por_processos(
                concurso_uuid, processo_uuids
            )
            convocados = _contar_convocados(concurso_uuid, processo_uuids)
            resultado[ano] = {
                "habilitados": habilitados_ano,
                "convocados": convocados,
                "nao-convocados": habilitados["total"] - convocados,
            }
    else:
        convocados = _contar_convocados(concurso_uuid)
        resultado.update(
            {
                "convocados": convocados,
                "nao-convocados": habilitados["total"] - convocados,
            }
        )

    return resultado


def _uuids_ultimos_lotes(
    concurso_uuid: UUID | str | None = None,
) -> list[Any]:
    """Resolve os ``uuid`` dos últimos lotes importados.

    Args:
        concurso_uuid: Concurso a restringir; ausente → último lote de cada
            concurso distinto.

    Returns:
        Lista de ``uuid`` dos lotes vigentes (um por concurso). Vazia quando
        não há lote no escopo.
    """
    if concurso_uuid:
        lote = (
            ConcursoCandidatosLote.objects.filter(concurso_uuid=concurso_uuid)
            .order_by("-criado_em")
            .first()
        )
        return [lote.uuid] if lote else []

    # Sem concurso: o último lote (maior criado_em) de cada concurso. Itera do
    # mais recente para o mais antigo e fica com o primeiro de cada concurso.
    vistos: set[Any] = set()
    uuids: list[Any] = []
    lotes = ConcursoCandidatosLote.objects.order_by("-criado_em").values_list(
        "concurso_uuid", "uuid"
    )
    for concurso, uuid_lote in lotes:
        if concurso not in vistos:
            vistos.add(concurso)
            uuids.append(uuid_lote)
    return uuids


def _queryset_base(
    concurso_uuid: UUID | str | None = None,
) -> QuerySet[ConcursoCandidato]:
    """Queryset canônico de habilitados (apenas os últimos lotes).

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.

    Returns:
        ``ConcursoCandidato`` filtrado pelos lotes vigentes do escopo.
    """
    return ConcursoCandidato.objects.filter(
        lote__uuid__in=_uuids_ultimos_lotes(concurso_uuid)
    )


def _agregar_por_categoria(
    qs: QuerySet[ConcursoCandidato],
) -> dict[str, int]:
    """Agrega a contagem por ``categoria_efetiva``.

    Args:
        qs: Queryset de ``ConcursoCandidato`` a agregar.

    Returns:
        Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
        ``nna``.
    """
    contagens = qs.values("categoria_efetiva").annotate(total=Count("uuid"))
    por_categoria = {
        item["categoria_efetiva"]: item["total"] for item in contagens
    }
    return {
        "total": sum(por_categoria.values()),
        "geral": por_categoria.get("GERAL", 0),
        "pcd": por_categoria.get("PCD", 0),
        "nna": por_categoria.get("NNA", 0),
    }


def _contar_habilitados(
    concurso_uuid: UUID | str | None = None,
) -> dict[str, int]:
    """Conta habilitados por categoria efetiva no último lote.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.

    Returns:
        Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
        ``nna``.
    """
    return _agregar_por_categoria(_queryset_base(concurso_uuid))


def _contar_habilitados_por_processos(
    concurso_uuid: UUID | str | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, int]:
    """Conta habilitados por categoria no escopo dos processos informados.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        processo_uuids: Processos a filtrar; vazio → zeros.

    Returns:
        Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
        ``nna`` no último lote, restrito aos processos informados.
    """
    if not processo_uuids:
        return {"total": 0, "geral": 0, "pcd": 0, "nna": 0}

    qs = _queryset_base(concurso_uuid).filter(processo_uuid__in=processo_uuids)
    return _agregar_por_categoria(qs)


def _contar_convocados(
    concurso_uuid: UUID | str | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> int:
    """Conta ``foi_convocado=True`` no último lote.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        processo_uuids: Processos a filtrar. ``None`` → modo "ALL" (todos os
            convocados do escopo); lista → filtra também pelos processos do
            ano.

    Returns:
        Quantidade de convocados no escopo informado.
    """
    qs = _queryset_base(concurso_uuid).filter(foi_convocado=True)
    if processo_uuids is not None:
        qs = qs.filter(processo_uuid__in=processo_uuids)
    return qs.count()
