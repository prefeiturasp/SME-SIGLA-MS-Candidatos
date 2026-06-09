"""Módulo service/ranking_service."""
from __future__ import annotations
from typing import Any
from candidatos.models import ConcursoCandidato

def atualizar_ranking(itens: Any) -> None:
    """Executa atualizar ranking.
    
    Args:
        itens: Parâmetro itens da operação.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    try:
        for idx, it in enumerate(itens, start=1):
            it.ranking = idx
        if itens:
            ConcursoCandidato.objects.bulk_update(itens, ['ranking'])
    except Exception:
        pass

def atualizar_ranking_escolha(itens: Any) -> None:
    """Define ranking_escolha conforme regra:.
    
    Args:
        itens: Parâmetro itens da operação.
    
    Returns:
        Não retorna valor.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    try:
        'classificacao'
        itens_pcd = [it for it in itens if getattr(it, 'classificacao_pcd', None) is not None]
        itens_pcd.sort(key=lambda it: (getattr(it, 'classificacao', None) is None, getattr(it, 'classificacao', 0)))
        itens_restantes = [it for it in itens if getattr(it, 'classificacao_pcd', None) is None]
        itens_restantes.sort(key=lambda it: (getattr(it, 'classificacao', None) is None, getattr(it, 'classificacao', float('inf'))))
        nova_ordem = itens_pcd + itens_restantes
        for idx, it in enumerate(nova_ordem, start=1):
            it.ranking_escolha = idx
        if nova_ordem:
            ConcursoCandidato.objects.bulk_update(nova_ordem, ['ranking_escolha'])
    except Exception:
        pass
