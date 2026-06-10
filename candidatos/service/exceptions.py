"""Módulo service/exceptions."""

from __future__ import annotations


class SalvarLotesException(Exception):
    """Erro de negócio ao persistir dados de lote de classificação."""

    def __init__(self, mensagem: str, detalhes: str | None = None) -> None:
        """Inicializa exceção com mensagem principal e detalhes opcionais.

        Args:
            mensagem: Resumo do erro exibido ao usuário.
            detalhes: Descrição complementar, como erros por linha do arquivo.
        """
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or ""

    def __str__(self) -> str:
        """Retorna a mensagem principal do erro."""
        return self.mensagem
