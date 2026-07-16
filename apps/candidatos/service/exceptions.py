"""Módulo service/exceptions."""

from __future__ import annotations


class SalvarLotesException(Exception):
    """Erro de negócio ao persistir dados de lote de classificação."""

    def __init__(self, mensagem: str, detalhes: str | None = None) -> None:
        """Inicializa a instância com os parâmetros informados.

        Args:
            mensagem: Mensagem principal do erro.
            detalhes: Detalhes complementares do erro.
        """
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or ""

    def __str__(self) -> str:
        """Retorna representação textual do registro.

        Returns:
            Conteúdo textual gerado.
        """
        return self.mensagem
