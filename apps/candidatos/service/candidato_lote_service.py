"""Módulo service/candidato_lote_service."""

from typing import Any

from candidatos.repository import (
    ConcursoCandidatoRepository,
    ConcursoCandidatosLoteRepository,
)
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

    lote = ConcursoCandidatosLoteRepository.criar(
        concurso_uuid=concurso_uuid,
        concurso_nome=data.get("concurso_nome", ""),
    )
    itens: list[dict[str, Any]] = []
    for item in data.get("candidatos", []):
        _cand, concurso = upsert_candidato_e_concurso(item)
        concurso.lote = lote
        ConcursoCandidatoRepository.salvar(
            concurso, campos_atualizacao=["lote"]
        )
        itens.append(
            {
                "candidato_uuid": concurso.candidato_id,
                "concurso_id": concurso.id,
            }
        )

    return {
        "lote_uuid": str(lote.id),
        "total_itens": len(itens),
    }, status.HTTP_201_CREATED
