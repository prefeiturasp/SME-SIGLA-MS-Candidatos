"""Agregações para a extração de dados de habilitados / convocados."""

from django.db.models import Count

from candidatos.models import ConcursoCandidato

CATEGORIAS = ("GERAL", "PCD", "NNA")


def montar_extracao_dados(concurso_uuid=None, filtros=None) -> dict:
    """
    Monta o dicionário de indicadores de habilitados e convocações.

    - ``habilitados``: total de candidatos importados no concurso (todos os
      lotes) e a distribuição por ``categoria_efetiva`` (geral/pcd/nna). Sem
      ``concurso_uuid``, agrega os habilitados de todos os concursos.
    - Com ``filtros``: uma chave por ``ano`` (vinda de ``filtros``) com:
      - ``convocados``: ``foi_convocado=True`` nos ``processo_uuids`` do ano.
      - ``nao-convocados``: habilitados importados que ainda não foram
        convocados naquele ano = total de habilitados − convocados do ano.
    - Sem ``filtros`` (None ou lista vazia): uma chave ``total`` agregada com:
      - ``convocados``: todos os ``foi_convocado=True`` do concurso.
      - ``nao-convocados``: total de habilitados − convocados do concurso.
    """
    habilitados = _contar_habilitados(concurso_uuid)
    resultado = {"habilitados": habilitados}

    if filtros:
        for filtro in filtros:
            ano = str(filtro["ano"])
            convocados = _contar_convocados(
                concurso_uuid, filtro["processo_uuids"]
            )
            resultado[ano] = {
                "convocados": convocados,
                "nao-convocados": habilitados["total"] - convocados,
            }
    else:
        convocados = _contar_convocados(concurso_uuid)
        resultado.update({
            "convocados": convocados,
            "nao-convocados": habilitados["total"] - convocados,
        })

    return resultado


def _contar_habilitados(concurso_uuid) -> dict:
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


def _contar_convocados(concurso_uuid, processo_uuids=None) -> int:
    """Conta ``foi_convocado=True``.

    - ``concurso_uuid`` informado → restringe ao concurso; ausente → todos.
    - ``processo_uuids is None`` → modo "ALL": todos os convocados do escopo.
    - ``processo_uuids`` informado → filtra também pelos processos do ano.
    """
    qs = ConcursoCandidato.objects.filter(foi_convocado=True)
    if concurso_uuid:
        qs = qs.filter(lote__concurso_uuid=concurso_uuid)
    if processo_uuids is not None:
        qs = qs.filter(processo_uuid__in=processo_uuids)
    return qs.count()
