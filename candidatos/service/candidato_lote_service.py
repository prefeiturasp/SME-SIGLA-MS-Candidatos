"""Módulo service/candidato_lote_service."""
from typing import Any

from rest_framework import status

from candidatos.models import ConcursoCandidatosLote

from .candidato_service import upsert_candidato_e_concurso


def processar_criacao_candidatos_lote(
    data: dict[str, Any],
) -> tuple[dict[str, Any], int]:
    """Espera payload:.
    
    Args:
        data: Dados de entrada.
    
    Returns:
        Resultado da operação.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    concurso_uuid = data.get("concurso_uuid")
    if not concurso_uuid:
        return {
            "detail": "concurso_uuid é obrigatório"
        }, status.HTTP_400_BAD_REQUEST

    lote = ConcursoCandidatosLote.objects.create(
        concurso_uuid=concurso_uuid,
        concurso_nome=data.get("concurso_nome", ""),
    )
    itens: list[dict[str, Any]] = []
    for item in data.get("candidatos", []):
        _cand, concurso = upsert_candidato_e_concurso(item)
        concurso.lote = lote
        concurso.save(update_fields=["lote"])
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
