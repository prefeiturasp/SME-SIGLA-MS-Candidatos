"""Módulo service/candidato_lote_service."""

from typing import Any

from rest_framework import status

from .candidato_service import upsert_candidato_e_concurso


def processar_criacao_candidatos_lote(
    data: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Processa criacao candidatos lote.

    Args:
        data: Data.

    Returns:
        Tupla com os objetos criados ou atualizados.
    """
    concurso_uuid = data.get("concurso_uuid")
    if not concurso_uuid:
        return {
            "detail": "concurso_uuid é obrigatório"
        }, status.HTTP_400_BAD_REQUEST

    concurso_nome = data.get("concurso_nome", "")
    mandado_judicial = data.get("mandado_judicial")
    itens: list[dict[str, Any]] = []
    for item in data.get("candidatos", []):
        _cand, concurso = upsert_candidato_e_concurso(
            item,
            concurso_uuid=concurso_uuid,
            concurso_nome=concurso_nome,
            mandado_judicial=mandado_judicial,
        )
        itens.append(
            {
                "candidato_uuid": concurso.candidato_id,
                "concurso_id": concurso.id,
            }
        )

    return {
        "concurso_uuid": str(concurso_uuid),
        "total_itens": len(itens),
    }, status.HTTP_201_CREATED
