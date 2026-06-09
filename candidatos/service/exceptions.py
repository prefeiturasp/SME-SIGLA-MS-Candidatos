"""Módulo service/exceptions."""
from __future__ import annotations
from typing import Any

class SalvarLotesException(Exception):
    """Define SalvarLotesException."""

    def __init__(self, mensagem: str, detalhes: str | None=None) -> None:
        """Executa   init  ."""
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or ''

    def __str__(self) -> str:
        """Executa   str  ."""
        return self.mensagem
