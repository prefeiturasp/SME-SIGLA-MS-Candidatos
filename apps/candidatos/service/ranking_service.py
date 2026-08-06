"""Módulo service/ranking_service."""

from __future__ import annotations

from typing import Any

from candidatos.repository import ConcursoCandidatoRepository


class RankingService:
    """Service para atualização de ranking de candidatos."""

    @staticmethod
    def atualizar_ranking(itens: Any) -> None:
        """Atualiza ranking.

        Args:
            itens: Lista de ConcursoCandidato na ordem desejada.

        Returns:
            Nenhum valor; persiste alterações no banco.
        """
        try:
            for idx, it in enumerate(itens, start=1):
                it.ranking = idx
            if itens:
                ConcursoCandidatoRepository.bulk_atualizar_ranking(itens)
        except Exception:
            pass

    @staticmethod
    def atualizar_ranking_escolha(itens: Any) -> None:
        """Atualiza ranking escolha.

        Args:
            itens: Lista de ConcursoCandidato a reordenar.

        Returns:
            Nenhum valor; persiste alterações no banco.
        """
        try:
            "classificacao"
            itens_pcd = [
                it
                for it in itens
                if getattr(it, "classificacao_pcd", None) is not None
            ]
            itens_pcd.sort(
                key=lambda it: (
                    getattr(it, "classificacao", None) is None,
                    getattr(it, "classificacao", 0),
                )
            )
            itens_restantes = [
                it
                for it in itens
                if getattr(it, "classificacao_pcd", None) is None
            ]
            itens_restantes.sort(
                key=lambda it: (
                    getattr(it, "classificacao", None) is None,
                    getattr(it, "classificacao", float("inf")),
                )
            )
            nova_ordem = itens_pcd + itens_restantes
            for idx, it in enumerate(nova_ordem, start=1):
                it.ranking_escolha = idx
            if nova_ordem:
                ConcursoCandidatoRepository.bulk_atualizar_ranking_escolha(
                    nova_ordem
                )
        except Exception:
            pass
