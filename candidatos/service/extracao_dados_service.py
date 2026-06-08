"""Agregações para a extração de dados de habilitados / convocados."""

from django.db.models import Count

from candidatos.models import ConcursoCandidato

CATEGORIAS = ("GERAL", "PCD", "NNA")


def montar_extracao_dados(concurso_uuid, filtros) -> dict:
    """
    Monta o dicionário de indicadores de habilitados e convocações.

    - ``habilitados``: total de candidatos importados no concurso (todos os
      lotes) e a distribuição por ``categoria_efetiva`` (geral/pcd/nna).
    - uma chave por ``ano`` (vinda de ``filtros``) com:
      - ``convocados``: ``foi_convocado=True`` nos ``processo_uuids`` do ano.
      - ``nao-convocados``: habilitados importados que ainda não foram
        convocados naquele ano = total de habilitados − convocados do ano.
    """
    habilitados = _contar_habilitados(concurso_uuid)
    resultado = {"habilitados": habilitados}

    for filtro in filtros:
        ano = str(filtro["ano"])
        convocados = _contar_convocados(filtro["processo_uuids"])
        resultado[ano] = {
            "convocados": convocados,
            "nao-convocados": habilitados["total"] - convocados,
        }

    return resultado


def _contar_habilitados(concurso_uuid) -> dict:
    contagens = (
        ConcursoCandidato.objects.filter(lote__concurso_uuid=concurso_uuid)
        .values("categoria_efetiva")
        .annotate(total=Count("uuid"))
    )
    por_categoria = {
        item["categoria_efetiva"]: item["total"] for item in contagens
    }
    return {
        "total": sum(por_categoria.values()),
        "geral": por_categoria.get("GERAL", 0),
        "pcd": por_categoria.get("PCD", 0),
        "nna": por_categoria.get("NNA", 0),
    }


def _contar_convocados(processo_uuids) -> int:
    return ConcursoCandidato.objects.filter(
        processo_uuid__in=processo_uuids, foi_convocado=True
    ).count()
