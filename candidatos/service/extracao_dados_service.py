"""Agregações para a extração de dados de habilitados / convocados."""

from typing import Any
from uuid import UUID

from django.db.models import Count

from candidatos.models import ConcursoCandidato

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
            convocados = _contar_convocados(
                concurso_uuid, processo_uuids
            )
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


def _contar_habilitados(
    concurso_uuid: UUID | str | None = None,
) -> dict[str, int]:
    """Conta habilitados por categoria efetiva.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.

    Returns:
        Dicionário com o ``total`` e a quebra por ``geral`` / ``pcd`` /
        ``nna``.
    """
    qs = ConcursoCandidato.objects.all()
    if concurso_uuid:
        qs = qs.filter(lote__concurso_uuid=concurso_uuid)
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


def _contar_habilitados_por_processos(
    concurso_uuid: UUID | str | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> dict[str, int]:
    """Conta habilitados por categoria no escopo dos processos informados."""
    if not processo_uuids:
        return {"total": 0, "geral": 0, "pcd": 0, "nna": 0}

    qs = ConcursoCandidato.objects.filter(processo_uuid__in=processo_uuids)
    if concurso_uuid:
        qs = qs.filter(lote__concurso_uuid=concurso_uuid)

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


def _contar_convocados(
    concurso_uuid: UUID | str | None = None,
    processo_uuids: list[UUID | str] | None = None,
) -> int:
    """Conta ``foi_convocado=True``.

    Args:
        concurso_uuid: Concurso a restringir; ausente → todos os concursos.
        processo_uuids: Processos a filtrar. ``None`` → modo "ALL" (todos os
            convocados do escopo); lista → filtra também pelos processos do
            ano.

    Returns:
        Quantidade de convocados no escopo informado.
    """
    qs = ConcursoCandidato.objects.filter(foi_convocado=True)
    if concurso_uuid:
        qs = qs.filter(lote__concurso_uuid=concurso_uuid)
    if processo_uuids is not None:
        qs = qs.filter(processo_uuid__in=processo_uuids)
    return qs.count()
