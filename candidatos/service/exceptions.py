"""Módulo service/exceptions."""
from __future__ import annotations
from typing import Any

class SalvarLotesException(Exception):
    """Define SalvarLotesException."""

    def __init__(self, mensagem: str, detalhes: str | None=None) -> None:
        """Executa   init  .
        
        Args:
            self: Instância do objeto.
            mensagem: Parâmetro mensagem da operação.
            detalhes: Parâmetro detalhes da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or ''

    def __str__(self) -> str:
        """Executa   str  .
        
        Args:
            self: Instância do objeto.
        
        Returns:
            Texto resultante da operação.
        
        Raises:
            Nenhuma exceção específica documentada.
        """
        return self.mensagem
